from ..base.ICommand import ICommand
from ..base.ITerminal import ITerminal
from ..model.camera import Camera
from ..model.custom_line_counter import CustomLineCounter
from supervision.geometry.dataclasses import Point
from ..utils.yolov8_model import CLASS_ID


class ExitCommand(ICommand):
    def __init__(self, executor: ITerminal):
        self.__executor = executor

    def execute(self) -> None:
        self.__executor.close()


class TrackSampleVideoCommand(ICommand):
    def __init__(self, video_path: str, line_coords: list):
        self.__video_path = video_path
        self.__line_coords = line_coords

    def execute(self) -> dict:
        return Camera(
            id=1,
            aud=21,
            line_counter=CustomLineCounter(
                Point(self.__line_coords[1][0],self.__line_coords[1][1]),
                Point(self.__line_coords[0][0],self.__line_coords[0][1]),
                classes=CLASS_ID
                ),
            video_path = self.__video_path
            ).track_video('result.mp4')