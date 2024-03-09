from typing import List
from ..base.i_command import ICommand
from ..base.i_terminal import ITerminal
from ..base.models_interfaces import ICustomLineCounter, IObj, EventType, ICamera, IEventHistory
from ..model.camera import Camera
from ..model.custom_line_counter import CustomLineCounter
from ..model.event_history import EventHistory
from ..model.obj import objs
from supervision.geometry.dataclasses import Point
from ..utils.yolov8_model import CLASS_ID
from datetime import datetime
import uuid


class ExitCommand(ICommand):
    def __init__(self, executor: ITerminal):
        self._executor = executor

    def execute(self) -> None:
        self._executor.close()


class TrackSampleVideoCommand(ICommand):
    def __init__(self, video_path: str, line_coords: list):
        self._video_path = video_path
        self._line_coords = line_coords

    def execute(self) -> List[IEventHistory]:
        return Camera(
            aud=21,
            line_counter=CustomLineCounter(
                Point(self._line_coords[1][0], self._line_coords[1][1]),
                Point(self._line_coords[0][0], self._line_coords[0][1]),
                classes=CLASS_ID,
            ),
            video_path=self._video_path,
        ).track_video("result.mp4")

