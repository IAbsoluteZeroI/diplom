from typing import List
from ..base.models_interfaces import IObjectsInPlace, ICamera
from dataclasses import dataclass
import uuid


@dataclass
class Place:
    id: int
    objects: IObjectsInPlace
    cameras: List["ICamera"]

    def __init__(self):
        id = uuid.uuid4
