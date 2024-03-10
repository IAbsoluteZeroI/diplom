from typing import List
from ..base.i_command import ICommand
from ..base.i_terminal import ITerminal
from ..base.models_interfaces import (
    ICustomLineCounter,
    IObj,
    EventType,
    ICamera,
    IEventHistory,
)
from ..model.models import Camera, CustomLineCounter, EventHistory, objs
from supervision.geometry.dataclasses import Point
from ..utils.yolov8_model import CLASS_ID
from datetime import datetime
import uuid
from PyQt5.QtWidgets import QMainWindow
from ..model.data.json_db_manager import json_db_manager


class TerminalExitCommand(ICommand):
    def __init__(self, executor: ITerminal):
        self._executor = executor

    def execute(self) -> None:
        self._executor.close()


class PyQtExitCommand(ICommand):
    def __init__(self, executor: QMainWindow):
        self.__executor = executor

    def execute(self) -> None:
        self.__executor.close()


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


class GetCamera1Command(ICommand):
    def execute(self) -> ICamera:
        return json_db_manager.get_cameras()[0]


class GetCamera2Command(ICommand):
    def execute(self) -> ICamera:
        return json_db_manager.get_cameras()[1]


class GetTwoCameras(ICommand):
    def __init__(self):
        self.camera1 = GetCamera1Command().execute()
        self.camera2 = GetCamera2Command().execute()

    def execute(self) -> List[ICamera]:
        return [self.camera1, self.camera2]


class TrackVideoCommand(ICommand):
    def __init__(self, camera: ICamera, target_video_path: str):
        self.camera = camera
        self.target_video_path = target_video_path

    def execute(self) -> list[IEventHistory]:
        events = self.camera.track_video(self.target_video_path)
        return events


# class TrackTwoVideosCommand(ICommand):
#     def __init__(self, camera1: ICamera, camera2: ICamera):
#         self.camera1 = camera1
#         self.camera2 = camera2

#     def execute(self) -> dict:
#         self.camera1.track_video("camera1_result.mp4")
#         self.camera2.track_video("camera2_result.mp4")

#         return {'camera1': self.camera1.line_counters[0].events, 'camera2': self.camera1.line_counters[0].events}


class GetEventHistoryFromJson(ICommand):
    pass
