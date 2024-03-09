from dataclasses import dataclass
import uuid


@dataclass
class ObjectsInPlace:
    id: int
    chair: int
    person: int
    interactive_whiteboard: int
    keyboard: int
    monitor: int
    pc: int
    table: int

    def __init__(self):
        id = uuid.uuid4
