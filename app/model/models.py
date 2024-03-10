from typing import List, Dict, Optional
from datetime import datetime

import cv2
import numpy as np
from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from ..utils.yolov8_model import (
    model,
    CLASS_ID,
    CLASS_NAMES_DICT,
    CLASS_ID_BY_NAME,
)
from ..utils.ByteTrack.yolox.tracker.byte_tracker import BYTETracker
from ..utils.tracker import (
    BYTETrackerArgs,
    detections2boxes,
    match_detections_with_tracks,
)
from supervision.tools.detections import Detections, BoxAnnotator
from supervision.video.dataclasses import VideoInfo
from supervision.video.source import get_video_frames_generator
from supervision.video.sink import VideoSink
from supervision.draw.color import Color, ColorPalette
from supervision.geometry.dataclasses import Rect, Point, Vector
from tqdm.notebook import tqdm
from .event_type import EventType
from sqlalchemy.orm import sessionmaker
from supervision.video.source import get_video_frames_generator


engine = create_engine("postgresql+psycopg2://admin:root@127.0.0.1:5432/db")
Base = declarative_base()
Session = sessionmaker(bind=engine)

objs = {
    0: "chair",
    1: "person",
    2: "interactive whiteboard",
    3: "keyboard",
    4: "laptop",
    5: "monitor",
    6: "pc",
    7: "table",
}


class ObjectsInPlace(Base):
    __tablename__ = "objects_in_places"

    id = Column(Integer, primary_key=True)
    chair = Column(Integer)
    person = Column(Integer)
    interactive_whiteboard = Column(Integer)
    keyboard = Column(Integer)
    monitor = Column(Integer)
    pc = Column(Integer)
    table = Column(Integer)
    place_id = Column(Integer, ForeignKey("places.id"))
    place = relationship("Place", back_populates="objects", foreign_keys=[place_id])


class Place(Base):
    __tablename__ = "places"

    id = Column(Integer, primary_key=True)
    objects = relationship(
        "ObjectsInPlace", back_populates="place", cascade="all, delete-orphan"
    )
    cameras = relationship("Camera", back_populates="place")

    def __init__(self, objects=None):
        self.objects = objects or []


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True)
    place_id = Column(Integer, ForeignKey("places.id"))
    place = relationship("Place", back_populates="cameras")
    line_counters = relationship("CustomLineCounter", back_populates="camera")
    video_path = Column(String)

    def __init__(self, line_counter, video_path, place_id=None, id=None):
        self.video_path = video_path
        self.line_counters = [line_counter]
        self.place_id = place_id


    def get_current_time(self, video_info) -> datetime:
        current_time = datetime.fromtimestamp(self._current_frame / video_info.fps)
        return current_time

    def track_video(self, target_video_path) -> list:
        byte_tracker = BYTETracker(BYTETrackerArgs())
        box_annotator = BoxAnnotator(
            color=ColorPalette(), thickness=2, text_thickness=2, text_scale=1
        )
        generator = get_video_frames_generator(self.video_path)
        video_info = VideoInfo.from_video_path(self.video_path)
        line_counter_annotator = CustomLineCounterAnnotator(class_name_dict=CLASS_NAMES_DICT, video_info=video_info)
        line_counter: CustomLineCounter = self.line_counters[0]
        # open target video file
        with VideoSink(target_video_path, video_info) as sink:
            # loop over video frames
            for index, frame in enumerate(generator):
                self._current_frame = index
                # model prediction on single frame and conversion to supervision Detections
                results = model(frame)
                detections = Detections(
                    xyxy=results[0].boxes.xyxy.cpu().numpy(),
                    confidence=results[0].boxes.conf.cpu().numpy(),
                    class_id=results[0].boxes.cls.cpu().numpy().astype(int),
                )

                # filtering out detections with unwanted classes
                mask = np.array(
                    [class_id in CLASS_ID for class_id in detections.class_id],
                    dtype=bool,
                )
                detections.filter(mask=mask, inplace=True)

                # tracking detections
                tracks = byte_tracker.update(
                    output_results=detections2boxes(detections=detections),
                    img_info=frame.shape,
                    img_size=frame.shape,
                )

                tracker_id = match_detections_with_tracks(
                    detections=detections, tracks=tracks
                )

                detections.tracker_id = np.array(tracker_id)

                # filtering out detections without trackers
                mask = np.array(
                    [tracker_id is not None for tracker_id in detections.tracker_id],
                    dtype=bool,
                )
                detections.filter(mask=mask, inplace=True)
                # format custom labels
                labels = [
                    f"id{tracker_id} {CLASS_NAMES_DICT[class_id]} {confidence:0.2f}"
                    for _, confidence, class_id, tracker_id in detections
                ]
                frame = box_annotator.annotate(
                    frame=frame, detections=detections, labels=labels
                )

                # self.line_counters[0].update(detections=detections)
                line_counter.update(detections=detections, current_time=self.get_current_time(video_info=video_info))
                line_counter_annotator.annotate(
                    frame=frame, line_counter=self.line_counters[0],
                )

                sink.write_frame(frame)
        return self.line_counters[0].events

    def get_tracker_info(
        self,
    ) -> dict:
        return self.line_counter.get_result_dict()


class CustomLineCounter(Base):
    __tablename__ = "custom_line_counters"

    id = Column(Integer, primary_key=True)
    coord_left_x = Column(Float)
    coord_left_y = Column(Float)
    coord_right_x = Column(Float)
    coord_right_y = Column(Float)
    camera_id = Column(Integer, ForeignKey("cameras.id"))
    camera = relationship("Camera", back_populates="line_counters")
    events = relationship("EventHistory", back_populates="line_counter")

    def __init__(
        self,
        coord_left_x: float,
        coord_left_y: float,
        coord_right_x: float,
        coord_right_y: float,
        id: int = None,
    ):
        self.coord_left_x = coord_left_x
        self.coord_left_y = coord_left_y
        self.coord_right_x = coord_right_x
        self.coord_right_y = coord_right_y

        self.events = []
        self.parent: Camera = None


    def update(self, detections: Detections, current_time: datetime):
        vector = self.get_vector()
        tracker_state = {}
        temp_events = []
        for id in detections.class_id:
            mask = np.array(
                [class_id in [int(id)] for class_id in detections.class_id], dtype=bool
            )
            filtereddet = detections.filter(mask=mask, inplace=False)

            for xyxy, confidence, class_id, tracker_id in filtereddet:
                # handle detections with no tracker_id
                if tracker_id is None:
                    continue

                # we check if all four anchors of bbox are on the same side of vector
                x1, y1, x2, y2 = xyxy
                anchors = [
                    Point(x=x1, y=y1),
                    Point(x=x1, y=y2),
                    Point(x=x2, y=y1),
                    Point(x=x2, y=y2),
                ]
                triggers = [vector.is_in(point=anchor) for anchor in anchors]

                # detection is partially in and partially out
                if len(set(triggers)) == 2:
                    continue

                # update tracker_state based on the current detection
                tracker_state[tracker_id] = triggers[0]

                # handle new detection
                if tracker_id not in temp_events:
                    temp_events.append(
                        self.__new_event(
                            int(id),
                            EventType.IN if tracker_state[tracker_id] else EventType.OUT,
                            current_time=current_time,
                        )
                    )

                # handle detection on the same side of the line
                elif tracker_state[tracker_id] != self.events[-1].type:
                    temp_events.append(
                        self.__new_event(
                            int(id),
                            EventType.IN if tracker_state[tracker_id] else EventType.OUT,
                            current_time=current_time,
                        )
                    )
        self.events += temp_events
                

    def __new_event(self, obj_id: int, type: EventType, current_time: datetime):
        return EventHistory(
            line_counter=self,
            obj=objs[obj_id],
            date=current_time,
            type=type,
        )

    def get_result_dict(self) -> dict:
        return self.result_dict
    
    def get_vector(self):
        return Vector(start=Point(self.coord_left_x, self.coord_left_y), end=Point(self.coord_right_x, self.coord_right_y))
    

class EventHistory(Base):
    __tablename__ = "event_history"

    id = Column(Integer, primary_key=True)
    line_counter_id = Column(Integer, ForeignKey("custom_line_counters.id"))
    line_counter = relationship("CustomLineCounter", back_populates="events")
    obj = Column(String)
    date = Column(DateTime)
    type = Column(Enum(EventType))


# class Obj(Base):
#     __tablename__ = "objects"

#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     events = relationship("EventHistory", back_populates="obj")

#     def __init__(self, id, name, events=None):
#         self.id = id
#         self.name = name
#         self.events = events or []

# session = Session()
# objs = {}
# for obj in session.query(Obj).all():
#     objs[obj.id] = obj.name
# session.close()


class CustomLineCounterAnnotator:
    def __init__(
        self,
        thickness: float = 2,
        color: Color = Color.white(),
        text_thickness: float = 2,
        text_color: Color = Color.black(),
        text_scale: float = 0.5,
        text_offset: float = 1.5,
        text_padding: int = 10,
        class_name_dict={},
        video_info=[],
    ):
        self.thickness: float = thickness
        self.color: Color = color
        self.text_thickness: float = text_thickness
        self.text_color: Color = text_color
        self.text_scale: float = text_scale
        self.text_offset: float = text_offset
        self.text_padding: int = text_padding
        self.class_name_dict = class_name_dict
        self.video_info = video_info

    def annotate(
        self, frame: np.ndarray, line_counter: CustomLineCounter
    ) -> np.ndarray:
        cv2.line(
            frame,
            line_counter.get_vector().start.as_xy_int_tuple(),
            line_counter.get_vector().end.as_xy_int_tuple(),
            self.color.as_bgr(),
            self.thickness,
            lineType=cv2.LINE_AA,
            shift=0,
        )
        cv2.circle(
            frame,
            line_counter.get_vector().start.as_xy_int_tuple(),
            radius=5,
            color=self.text_color.as_bgr(),
            thickness=-1,
            lineType=cv2.LINE_AA,
        )
        cv2.circle(
            frame,
            line_counter.get_vector().end.as_xy_int_tuple(),
            radius=5,
            color=self.text_color.as_bgr(),
            thickness=-1,
            lineType=cv2.LINE_AA,
        )

        report = ""
        for event in line_counter.events:
            # class_name = self.class_name_dict[key]
            # in_count = line_counter.result_dict[key]["in"]
            # out_count = line_counter.result_dict[key]["out"]
            # report += f" | {class_name}: in {in_count} out {out_count}"

            event: EventHistory
            class_name = event.obj
            in_or_out = event.type
            mins_secs = event.date.strftime("%M:%S")
            report += f" | {class_name}: {in_or_out.name} time: {mins_secs}"
        report += " |"

        (report_width, report_height), _ = cv2.getTextSize(
            report, cv2.FONT_HERSHEY_SIMPLEX, self.text_scale, self.text_thickness
        )

        report_x = int(((self.video_info.width) - report_width) / 2)
        report_y = int((150 + report_height) / 2 - self.text_offset * report_height)

        report_background_rect = Rect(
            x=report_x,
            y=report_y - report_height,
            width=report_width,
            height=report_height,
        ).pad(padding=self.text_padding)

        cv2.rectangle(
            frame,
            report_background_rect.top_left.as_xy_int_tuple(),
            report_background_rect.bottom_right.as_xy_int_tuple(),
            self.color.as_bgr(),
            -1,
        )

        cv2.putText(
            frame,
            report,
            (report_x, report_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            self.text_scale,
            self.text_color.as_bgr(),
            self.text_thickness,
            cv2.LINE_AA,
        )

