from supervision.tools.detections import Detections
from supervision.geometry.dataclasses import Point, Vector
from typing import List, Dict
import numpy as np
from ..base.models_interfaces import ICamera, IEventHistory, EventType
from dataclasses import dataclass
from .event_history import EventHistory
from .obj import get_obj_from_id
import uuid


@dataclass
class CustomLineCounter:
    id: int
    coord_left: List[int]
    coord_right: List[int]
    events: List["IEventHistory"]

    def __init__(self, coord_left: Point, coord_right: Point, classes: List):
        self.id = uuid.uuid4
        self.vector = Vector(start=coord_left, end=coord_right)
        self.tracker_state: Dict[str, bool] = {}
        self.coord_left = coord_right
        self.coord_right = coord_right
        # self.result_dict = {
        #     # int(class_id): {"in_count": int(0), "out_count": int(0)}
        #     int(class_id): {"in": [], "out": []}
        #     for class_id in classes
        # }
        self.events = []
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

                    # self.result_dict[int(id)]["in"].append(
                    #     self.parent.get_current_time()
                    # )

                    # self.events.append(NewEventCommand(
                    #     camera=self.parent, 
                    #     line_counter=self, 
                    #     obj=GetObjCommand(int(id)).execute(), 
                    #     type=EventType.IN
                    # ))

                    self.events.append(self.__new_event(
                        int(id),
                        EventType.IN
                    ))


                else:
                    # self.result_dict[int(id)]["out_count"] += 1

                    # self.result_dict[int(id)]["out"].append(
                    #     self.parent.get_current_time()
                    # )

                    # self.events.append(NewEventCommand(
                    #     camera=self.parent, 
                    #     line_counter=self, 
                    #     obj=GetObjCommand(int(id)).execute(), 
                    #     type=EventType.OUT
                    # ))
                    self.events.append(self.__new_event(
                        int(id),
                        EventType.OUT
                    ))
    
    def __new_event(self, obj_id: int, type: EventType):
        return EventHistory(
            id=uuid.uuid4,
            line_counter=self,
            obj=get_obj_from_id(obj_id),
            date=self.parent.get_current_time(),
            type=type
            )

    def get_result_dict(self) -> dict:
        return self.result_dict
