from datetime import datetime
from dataclasses import dataclass
from ..base.models_interfaces import IObj, ICustomLineCounter, EventType
import uuid


@dataclass
class EventHistory:
    id: int
    line_counter: ICustomLineCounter
    obj: "IObj"
    date: datetime
    type: EventType

