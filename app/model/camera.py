from datetime import datetime
from supervision.video.sink import VideoSink
from ..utils.ByteTrack.yolox.tracker.byte_tracker import BYTETracker
from ..utils.tracker import (
    BYTETrackerArgs,
    detections2boxes,
    match_detections_with_tracks,
)
from supervision.tools.detections import Detections, BoxAnnotator
from tqdm.notebook import tqdm
from supervision.draw.color import ColorPalette
from ..utils.yolov8_model import model, CLASS_ID, CLASS_NAMES_DICT
import numpy as np
from supervision.video.dataclasses import VideoInfo
from supervision.video.source import get_video_frames_generator
from .custom_line_counter_annotator import CustomLineCounterAnnotator


class Camera:
    def __init__(
        self,
        id: int,
        aud: int,
        line_counter,
        video_path,
    ):
        self.id = id
        self.aud = aud
        self.video_path = video_path
        self.video_info = VideoInfo.from_video_path(self.video_path)
        self.line_counter = line_counter
        self.line_counter.parent = self
        self.line_counter_annotator = CustomLineCounterAnnotator(
            class_name_dict=CLASS_NAMES_DICT,
            thickness=4,
            text_thickness=1,
            text_scale=0.5,
            video_info=self.video_info
        ),

        self.generator = get_video_frames_generator(self.video_path)

    def get_time_now(self) -> datetime:
        return datetime.now()

    def track_video(self, target_video_path):
        byte_tracker = BYTETracker(BYTETrackerArgs())
        box_annotator = BoxAnnotator(
            color=ColorPalette(), thickness=2, text_thickness=2, text_scale=1
        )

        # open target video file
        with VideoSink(target_video_path, self.video_info) as sink:
            # loop over video frames
            for frame in tqdm(self.generator, total=self.video_info.total_frames):
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

                self.line_counter.update(detections=detections)
                self.line_counter_annotator.annotate(
                    frame=frame, line_counter=self.line_counter
                )

                sink.write_frame(frame)
        return self.line_counter.result_dict

    def get_tracker_info(
        self,
    ) -> dict:
        return self.line_counter.get_result_dict()
