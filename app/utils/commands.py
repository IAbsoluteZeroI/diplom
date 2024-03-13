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
from ..model.models import Camera, CustomLineCounter, EventHistory, Session
from supervision.geometry.dataclasses import Point
from ..model.yolov8_model import CLASS_ID
from datetime import datetime
import uuid
from PyQt5.QtWidgets import QMainWindow
from ..model.data.json_db_manager import json_db_manager
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from ..model.tracker import track_video


class TerminalExitCommand(ICommand):
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


class GetCamera1Command(ICommand):
    def execute(self) -> Camera:
        session = Session()
        camera = session.query(Camera).first()
        session.close()
        return camera


class GetCamera2Command(ICommand):
    def execute(self) -> Camera:
        session = Session()
        camera = session.query(Camera).offset(1).first()
        session.close()
        return camera


class GetTwoCameras(ICommand):
    def __init__(self):
        self.camera1 = GetCamera1Command().execute()
        self.camera2 = GetCamera2Command().execute()

    def execute(self) -> List[ICamera]:
        return [self.camera1, self.camera2]


class TrackVideoCommand(ICommand):
    def __init__(self, camera: Camera, target_video_path: str, annotate: bool = False):
        self.camera = camera
        self.target_video_path = target_video_path
        self.annotate = annotate

    def execute(self) -> list[EventHistory]:
        session = Session()
        session.add(self.camera)
        session.flush()
        track_video(
            self.target_video_path,
            camera=self.camera,
            session=session,
            annotate=self.annotate,
        )
        session.commit()
        events = session.query(EventHistory).all()
        session.close()
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
