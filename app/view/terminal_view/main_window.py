from ...view_model.main_view_model import view_model
from .terminal_views import *
from ...utils.commands import ExitCommand, TrackSampleVideoCommand
from ...base.ITerminal import ITerminal
import sys
import os


class MainWindow(ITerminal):
    __current_view: ITerminal

    def __init__(self):
        super().__init__()

        view_model.on_change("state", lambda state: self.__check_state())
        view_model.on_change("command", lambda command: self.__check_command())

        self.__current_view = MenuView(self)

    def close(self):
        self.clear()
        sys.exit()

    def clear(self):
        # Проверка операционной системы
        if os.name == "nt":  # Windows
            os.system("cls")
        else:  # Linux/MacOS
            os.system("clear")

    def __check_state(self):
        if view_model.state == "menu":
            self.__current_view = MenuView(self)
        elif view_model.state == "sample_video_tracking":
            self.__current_view = SampleVideoTracking(self)

    def __check_command(self):
        if view_model.command == "exit":
            # self.close()
            return ExitCommand(self).execute()
        if view_model.command == "sample_video_tracking":
            view_model.tracking_info = TrackSampleVideoCommand(
                video_path="test.avi", 
                line_coords=[[1100, 230], [1200, 750]]
                ).execute()
