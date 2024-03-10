from PyQt5 import uic
from PyQt5.QtWidgets import (
    QDesktopWidget,
    QWidget,
    QMainWindow,
    QAction,
)

from .views import *
from .UI import main_window_ui
from ...view_model.main_view_model import view_model


class MainWindow(QMainWindow):
    __current_view: QWidget

    def __init__(self) -> None:
        super().__init__()

        view_model.on_change("state", lambda state: self.__check_state())
        view_model.on_change("command", lambda command: self.__check_command())

        self.__load_ui()

        self.__setup_menu_actions()

        self.__current_view = MenuView(self)
        self.setCentralWidget(self.__current_view)

        self.show()

    def __load_ui(self):
        uic.loadUi(main_window_ui, self)
        self.menuExitAction: QAction
        self.menuAboutProgramAction: QAction

    def __setup_menu_actions(self):
        self.menuExitAction.triggered.connect(lambda: view_model.set_command("exit"))
        self.menuAboutProgramAction.triggered.connect(
            lambda: view_model.set_command("about_programm")
        )

    def __check_state(self):
        if view_model.state == "menu":
            self.__current_view = MenuView(self)
            self.statusBar().showMessage("")

        elif view_model.state == "track_two_videos":
            self.__current_view = TrackingView(self)

    def __check_command(self):
        if view_model.command == "exit":
            PyQtExitCommand(self).execute()

        elif view_model.command == "about_programm":
            MessageView(
                "Выполнили студенты САФУ, 4 курс, 351018, \nАрхаров Никита Михайлович\nГолышев Алексей Витальевич."
            )
