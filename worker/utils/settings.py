from dataclasses import dataclass

from ultralytics import YOLO

# MODEL = "utils/640.engine"
MODEL = "utils/640.onnx"
model = YOLO(MODEL)

CLASS_NAMES_DICT = {
    0: "chair",
    1: "person",
    2: "interactive whiteboard",
    3: "keyboard",
    4: "laptop",
    5: "monitor",
    6: "pc",
    7: "table",
}

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
