from typing import List
from ..base.i_command import ICommand
from ..base.i_terminal import ITerminal
from ..base.models_interfaces import (
    ICamera,
)
from ..model.models import Camera, EventHistory, Session
from ..model.tracker import track_video


class TerminalExitCommand(ICommand):
    def __init__(self, executor: ITerminal):
        self._executor = executor

    def execute(self) -> None:
        self._executor.close()


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
