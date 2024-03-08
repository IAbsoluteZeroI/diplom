from supervision.tools.detections import Detections
from supervision.geometry.dataclasses import Point, Vector
from typing import List, Dict
import numpy as np
from ..base.ICamera import ICamera


class CustomLineCounter:
    def __init__(self, start: Point, end: Point, classes: List):
        self.vector = Vector(start=start, end=end)
        self.tracker_state: Dict[str, bool] = {}
        self.start = start
        self.end = end
        self.result_dict = {
            # int(class_id): {"in_count": int(0), "out_count": int(0)}
            int(class_id): {"in": [], "out": []}
            for class_id in classes
        }
        self.parent: ICamera = None

    def update(self, detections: Detections):
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
                triggers = [self.vector.is_in(point=anchor) for anchor in anchors]

                # detection is partially in and partially out
                if len(set(triggers)) == 2:
                    continue

                tracker_state = triggers[0]
                # handle new detection
                if tracker_id not in self.tracker_state:
                    self.tracker_state[tracker_id] = tracker_state
                    continue

                # handle detection on the same side of the line
                if self.tracker_state.get(tracker_id) == tracker_state:
                    continue

                self.tracker_state[tracker_id] = tracker_state
                if tracker_state:
                    # self.result_dict[int(id)]["in_count"] += 1
                    self.result_dict[int(id)]["in"].append(self.parent.get_current_time())
                else:
                    # self.result_dict[int(id)]["out_count"] += 1
                    self.result_dict[int(id)]["out"].append(self.parent.get_current_time())

    def get_result_dict(self) -> dict:
        return self.result_dict
