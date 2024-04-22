from ultralytics import YOLO
from dataclasses import dataclass

MODEL = "worker/utils/best1280.pt"
model = YOLO(MODEL)
model.fuse()

CLASS_NAMES_DICT = model.names
CLASS_ID = [0, 1, 2, 3, 4, 5, 6, 7]

CLASS_ID_BY_NAME = {
    "chair": 0,
    "person": 1,
    "interactive whiteboard": 2,
    "keyboard": 3,
    "laptop": 4,
    "monitor": 5,
    "pc": 6,
    "table": 7,
}


@dataclass(frozen=True)
class BYTETrackerArgs:
    track_thresh: float = 0.25
    track_buffer: int = 30
    match_thresh: float = 0.8
    aspect_ratio_thresh: float = 3.0
    min_box_area: float = 1.0
    mot20: bool = False