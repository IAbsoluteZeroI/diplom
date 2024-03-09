from typing import List
from dataclasses import dataclass
from ..base.models_interfaces import IEventHistory
from ..utils.yolov8_model import CLASS_ID_BY_NAME


@dataclass
class Obj:
    id: int
    name: str
    events: List[IEventHistory]


objs = [
    Obj(id=id, name=name, events=[])
    for name, id in CLASS_ID_BY_NAME.items()
]

def get_obj_from_id(id):
    if 0 <= id < len(objs):
        return objs[id]
    else:
        return None
