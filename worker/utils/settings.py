from dataclasses import dataclass

from ultralytics import YOLO

MODEL = "utils/models/new/640/yolov8s_640_50ep_16b.onnx"
model = YOLO(MODEL,
            #  verbose=False
             )

# CLASS_NAMES_DICT = {
#     0: 'chair', 
#     1: 'person', 
#     2: 'interactive whiteboard', 
#     3: 'keyboard', 
#     4: 'laptop', 
#     5: 'monitor', 
#     6: 'pc', 
#     7: 'table'
# }

CLASS_NAMES_DICT = {
    0: 'chair', 
    1: 'interactive whiteboard', 
    2: 'keyboard', 
    3: 'laptop', 
    4: 'monitor', 
    5: 'pc', 
    6: 'person', 
    7: 'table'
}

CLASS_ID = list(range(8))

CLASS_ID_BY_NAME = {v: k for k, v in CLASS_NAMES_DICT.items()}

@dataclass(frozen=True)
class BYTETrackerArgs:
    track_thresh: float = 0.60
    track_buffer: int = 40
    match_thresh: float = 0.9
    aspect_ratio_thresh: float = 3.0
    min_box_area: float = 1.0
    mot20: bool = False