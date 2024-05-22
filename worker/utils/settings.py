from dataclasses import dataclass

from ultralytics import YOLO

# MODEL = "utils/640.engine"
MODEL = "utils/640.engine"
model = YOLO(MODEL, verbose=False)

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

CLASS_ID = list(range(8))

CLASS_ID_BY_NAME = {v: k for k, v in CLASS_NAMES_DICT.items()}

@dataclass(frozen=True)
class BYTETrackerArgs:
    track_thresh: float = 0.25
    track_buffer: int = 30
    match_thresh: float = 0.8
    aspect_ratio_thresh: float = 3.0
    min_box_area: float = 1.0
    mot20: bool = False