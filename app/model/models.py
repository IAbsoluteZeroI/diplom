from datetime import datetime

import cv2
import numpy as np
from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base


from supervision.tools.detections import Detections

from supervision.geometry.dataclasses import Rect, Point, Vector
from .event_type import EventType
from sqlalchemy.orm import sessionmaker


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

        # return datetime.now()


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

    def update(self, detections: Detections, current_time: datetime, session):
        vector = self.get_vector()
        tracker_state = {}
        is_in = None
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

                # detection is completely in or completely out
                if len(set(triggers)) == 1:
                    is_in = all(triggers)

                    # update tracker_state based on the current detection
                    tracker_state[tracker_id] = is_in

                # detection is partially in and partially out
                elif len(set(triggers)) == 2:
                    # check if tracker_id is already in tracker_state
                    if tracker_id in tracker_state:
                        # check if the previous state was different
                        if tracker_state[tracker_id] != is_in:
                            # create a new event and add it to the session
                            self.events.append(
                                EventHistory(
                                    line_counter=self,
                                    obj=objs[id],
                                    type=EventType.IN if is_in else EventType.OUT,
                                    date=current_time,
                                )
                            )
                            session.add(self.events[-1])
                            tracker_state[tracker_id] = is_in
                    else:
                        # add the tracker_id to tracker_state with its current state
                        tracker_state[tracker_id] = is_in

    # def update(self, detections: Detections, current_time: datetime, session):
    #     vector = self.get_vector()
    #     tracker_state = {}
    #     for id in detections.class_id:
    #         mask = np.array(
    #             [class_id in [int(id)] for class_id in detections.class_id], dtype=bool
    #         )
    #         filtereddet = detections.filter(mask=mask, inplace=False)

    #         for xyxy, confidence, class_id, tracker_id in filtereddet:
    #             # handle detections with no tracker_id
    #             if tracker_id is None:
    #                 continue

    #             # we check if all four anchors of bbox are on the same side of vector
    #             x1, y1, x2, y2 = xyxy
    #             anchors = [
    #                 Point(x=x1, y=y1),
    #                 Point(x=x1, y=y2),
    #                 Point(x=x2, y=y1),
    #                 Point(x=x2, y=y2),
    #             ]
    #             triggers = [vector.is_in(point=anchor) for anchor in anchors]

    #             # detection is completely in or completely out
    #             if len(set(triggers)) == 1:
    #                 is_in = all(triggers)

    #                 # update tracker_state based on the current detection
    #                 tracker_state[tracker_id] = is_in

    #                 # handle new detection
    #                 if tracker_id not in self.events:
    #                     self.events.append(EventHistory(
    #                         line_counter=self,
    #                         obj=objs[id],
    #                         type=EventType.IN if is_in else EventType.OUT,
    #                         date=current_time,
    #                     ))
    #                     session.add(self.events[-1])

    #                 # handle detection crossing the line
    #                 elif (is_in and self.events[-1].type == EventType.OUT) or \
    #                     (not is_in and self.events[-1].type == EventType.IN):
    #                     self.events.append(EventHistory(
    #                         line_counter=self,
    #                         obj=objs[id],
    #                         type=EventType.IN if is_in else EventType.OUT,
    #                         date=current_time,
    #                     ))

    def get_result_dict(self) -> dict:
        return self.result_dict

    def get_vector(self):
        return Vector(
            start=Point(self.coord_left_x, self.coord_left_y),
            end=Point(self.coord_right_x, self.coord_right_y),
        )


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
