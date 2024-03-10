from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List
from enum import Enum
from supervision.geometry.dataclasses import Point


@dataclass
class IObjectsInPlace:
    id: int
    chair: int
    person: int
    interactive_whiteboard: int
    keyboard: int
    monitor: int
    pc: int
    table: int


@dataclass
class IPlace:
    id: int
    objects: IObjectsInPlace
    cameras: List["ICamera"]  # Один ко многим с Camera


@dataclass
class ICustomLineCounter:
    id: int
    coord_left: Point
    coord_right: Point
    events: List["IEventHistory"]  # Один ко многим с EventHistory


class EventType(Enum):
    IN = "IN"
    OUT = "OUT"


@dataclass
class IEventHistory:
    id: int
    line_counter: ICustomLineCounter
    obj: "IObj"
    date: datetime
    type: EventType


@dataclass
class ICamera(ABC):
    id: int
    place: "IPlace"  # Один к одному с Place
    line_counters: List[ICustomLineCounter]  # Один ко многим с LineCounter
    video_path: str

    @abstractmethod
    def get_current_time(self) -> datetime: ...

    @abstractmethod
    def track_video(self) -> dict: ...


@dataclass
class IObj:
    id: int
    name: str
    events: List[IEventHistory]  # Один ко многим с EventHistory
