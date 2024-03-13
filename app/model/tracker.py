import cv2
from typing import List
import numpy as np
from ..utils.ByteTrack.yolox.tracker.byte_tracker import STrack
from onemetric.cv.utils.iou import box_iou_batch
from dataclasses import dataclass
import cv2
import numpy as np
from supervision.tools.detections import Detections
from .models import Camera
from ..utils.ByteTrack.yolox.tracker.byte_tracker import BYTETracker
from supervision.tools.detections import Detections, BoxAnnotator
from supervision.video.dataclasses import VideoInfo
from supervision.video.source import get_video_frames_generator
from supervision.video.sink import VideoSink
from supervision.draw.color import Color, ColorPalette
from supervision.geometry.dataclasses import Rect
from .yolov8_model import CLASS_ID, CLASS_ID_BY_NAME, CLASS_NAMES_DICT, model
from .models import CustomLineCounter
from datetime import datetime
from .models import EventHistory, objs
from supervision.geometry.dataclasses import Rect, Point
from .event_type import EventType
import time


# [eq]


class VideoProcessor:
    def __init__(
        self,
        video_path,
    ):
        self.video_path = video_path
        self.video = cv2.VideoCapture(video_path)
        self.width = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def get_frame_by_order(self, frame_number):
        self.video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = self.video.read()
        if ret:
            return frame
        else:
            return None

    def get_width_height(self):
        return self.width, self.height


@dataclass(frozen=True)
class BYTETrackerArgs:
    track_thresh: float = 0.25
    track_buffer: int = 30
    match_thresh: float = 0.8
    aspect_ratio_thresh: float = 3.0
    min_box_area: float = 1.0
    mot20: bool = False


# converts Detections into format that can be consumed by match_detections_with_tracks function
def detections2boxes(detections: Detections) -> np.ndarray:
    return np.hstack((detections.xyxy, detections.confidence[:, np.newaxis]))


# converts List[STrack] into format that can be consumed by match_detections_with_tracks function
def tracks2boxes(tracks: List[STrack]) -> np.ndarray:
    return np.array([track.tlbr for track in tracks], dtype=float)


# matches our bounding boxes with predictions
def match_detections_with_tracks(
    detections: Detections, tracks: List[STrack]
) -> Detections:
    if not np.any(detections.xyxy) or len(tracks) == 0:
        return np.empty((0,))

    tracks_boxes = tracks2boxes(tracks=tracks)
    iou = box_iou_batch(tracks_boxes, detections.xyxy)
    track2detection = np.argmax(iou, axis=1)

    tracker_ids = [None] * len(detections)

    for tracker_index, detection_index in enumerate(track2detection):
        if iou[tracker_index, detection_index] != 0:
            tracker_ids[detection_index] = tracks[tracker_index].track_id

    return tracker_ids


class LineCounter:
    def __init__(self, events=None):
        self.events = events or []

    def add_events(self, events):
        self.events.extend(events)


def track_video(
    target_video_path, camera: Camera, session, annotate: bool = False
) -> None:
    byte_tracker = BYTETracker(BYTETrackerArgs())
    box_annotator = BoxAnnotator(
        color=ColorPalette(), thickness=2, text_thickness=2, text_scale=1
    )
    generator = get_video_frames_generator(camera.video_path)
    video_info = VideoInfo.from_video_path(camera.video_path)
    line_counter: CustomLineCounter = camera.line_counters[0]
    frame_annotator = FrameAnnotator(
        class_name_dict=CLASS_NAMES_DICT,
        video_info=video_info,
        line_counter=line_counter,
    )
    # open target video file
    with VideoSink(target_video_path, video_info) as sink:
        # loop over video frames
        # for index, frame in enumerate(generator):
        num_of_current_frame = 0
        for frame in generator:
            # current_frame = index
            # current_time = datetime.fromtimestamp(current_frame / video_info.fps)
            current_time = datetime.fromtimestamp(num_of_current_frame / video_info.fps)
            # current_time = datetime.now()

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

            line_counter.update(
                detections=detections, current_time=current_time, session=session
            )
            if annotate:
                frame_annotator.annotate(frame=frame)

            sink.write_frame(frame)
            num_of_current_frame += 1


class FrameAnnotator:
    def __init__(
        self,
        line_counter: CustomLineCounter,
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
        self.line_counter = line_counter

    def annotate(self, frame: np.ndarray) -> np.ndarray:
        vector = self.line_counter.get_vector()
        cv2.line(
            frame,
            vector.start.as_xy_int_tuple(),
            vector.end.as_xy_int_tuple(),
            self.color.as_bgr(),
            self.thickness,
            lineType=cv2.LINE_AA,
            shift=0,
        )
        cv2.circle(
            frame,
            vector.start.as_xy_int_tuple(),
            radius=5,
            color=self.text_color.as_bgr(),
            thickness=-1,
            lineType=cv2.LINE_AA,
        )
        cv2.circle(
            frame,
            vector.end.as_xy_int_tuple(),
            radius=5,
            color=self.text_color.as_bgr(),
            thickness=-1,
            lineType=cv2.LINE_AA,
        )

        report = ""
        for event in self.line_counter.events:
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
