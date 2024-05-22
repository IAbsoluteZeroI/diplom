import sys
import time
from typing import List

import cv2
import numpy as np
from onemetric.cv.utils.iou import box_iou_batch
from supervision.draw.color import ColorPalette
from supervision.tools.detections import BoxAnnotator, Detections
from supervision.video.dataclasses import VideoInfo
from supervision.video.sink import VideoSink
from supervision.video.source import get_video_frames_generator
from tqdm import tqdm
from utils.anotator import CustomLineCounterAnnotator
from utils.ByteTrack.yolox.tracker.byte_tracker import BYTETracker, STrack
from utils.counter import CustomLineCounter
from utils.settings import CLASS_ID, CLASS_NAMES_DICT, BYTETrackerArgs, model


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


async def track_video(video_path, start, end, camera_id) -> None:
    byte_tracker = BYTETracker(BYTETrackerArgs())
    video_info = VideoInfo.from_video_path(video_path)
    generator = get_video_frames_generator(video_path)
    line_counter = CustomLineCounter(
        start=start,
        end=end,
        classes=CLASS_ID,
        camera_id=camera_id,
        class_name_dict=CLASS_NAMES_DICT,
    )
    box_annotator = BoxAnnotator(
        color=ColorPalette(), thickness=2, text_thickness=2, text_scale=1
    )
    line_annotator = CustomLineCounterAnnotator(
        thickness=2,
        text_thickness=1,
        text_scale=0.5,
        class_name_dict=CLASS_NAMES_DICT,
        video_info=video_info,
    )
    
    
    
    for frame in tqdm(generator, total=video_info.total_frames):
        # model prediction on single frame and conversion to supervision Detections
        results = model(frame, verbose=False)
        detections = Detections(
            xyxy=results[0].boxes.xyxy.cpu().numpy(),
            confidence=results[0].boxes.conf.cpu().numpy(),
            class_id=results[0].boxes.cls.cpu().numpy().astype(int),
        )

        mask = np.array(
            [class_id in CLASS_ID for class_id in detections.class_id], dtype=bool
        )
        detections.filter(mask=mask, inplace=True)

        tracks = byte_tracker.update(
            output_results=detections2boxes(detections=detections),
            img_info=frame.shape,
            img_size=frame.shape,
        )

        tracker_id = match_detections_with_tracks(
            detections=detections, tracks=tracks
        )

        detections.tracker_id = np.array(tracker_id)

        mask = np.array(
            [tracker_id is not None for tracker_id in detections.tracker_id],
            dtype=bool,
        )
        detections.filter(mask=mask, inplace=True)
        
        await line_counter.update(detections=detections)
    
    
    
    
    # with VideoSink("result.mp4", video_info) as sink:
    #     # loop over video frames
    #     for frame in tqdm(generator, total=video_info.total_frames):
    #         # model prediction on single frame and conversion to supervision Detections
    #         results = model(frame)
    #         detections = Detections(
    #             xyxy=results[0].boxes.xyxy.cpu().numpy(),
    #             confidence=results[0].boxes.conf.cpu().numpy(),
    #             class_id=results[0].boxes.cls.cpu().numpy().astype(int),
    #         )

    #         # filtering out detections with unwanted classes
    #         mask = np.array(
    #             [class_id in CLASS_ID for class_id in detections.class_id], dtype=bool
    #         )
    #         detections.filter(mask=mask, inplace=True)

    #         # tracking detections
    #         tracks = byte_tracker.update(
    #             output_results=detections2boxes(detections=detections),
    #             img_info=frame.shape,
    #             img_size=frame.shape,
    #         )

    #         tracker_id = match_detections_with_tracks(
    #             detections=detections, tracks=tracks
    #         )

    #         detections.tracker_id = np.array(tracker_id)

    #         # filtering out detections without trackers
    #         mask = np.array(
    #             [tracker_id is not None for tracker_id in detections.tracker_id],
    #             dtype=bool,
    #         )
    #         detections.filter(mask=mask, inplace=True)
    #         # format custom labels
    #         labels = [
    #             f"id{tracker_id} {CLASS_NAMES_DICT[class_id]} {confidence:0.2f}"
    #             for _, confidence, class_id, tracker_id in detections
    #         ]

    #         frame = box_annotator.annotate(
    #             frame=frame, detections=detections, labels=labels
    #         )

    #         await line_counter.update(detections=detections)
    #         line_annotator.annotate(frame=frame, line_counter=line_counter)

    #         sink.write_frame(frame)
