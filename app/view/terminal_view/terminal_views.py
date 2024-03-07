from ...view_model.main_view_model import view_model
import time
from ...base.ITerminal import ITerminal


class MenuView:
    def __init__(self, main_window: ITerminal):
        self.main_window = main_window
        self.__setup_ui()
        self.__setup_menu_actions()
        self.__wait_for_input()

    def __setup_ui(self):
        self.main_window.clear()

    def __setup_menu_actions(self):
        print("1. Трекнуть видос")
        print("0. Выход")

    def __wait_for_input(self):
        user_input = input("Введи: ")
        if user_input == "1":
            view_model.set_state("sample_video_tracking")
        elif user_input == "0":
            view_model.set_command("exit")
        else:
            print("Неверный ввод. Попробуйте снова.")
            time.sleep(2)
            view_model.set_state("menu")


class SampleVideoTracking:
    def __init__(self, main_window: ITerminal):
        self.main_window = main_window
        self.__setup_ui()
        self.__show_tracking_info()
        self.__wait_for_input()

    def __setup_ui(self):
        self.main_window.clear()

    def __show_tracking_info(self):
        view_model.set_command("sample_video_tracking")
        print(view_model.get_tracking_info())

    def __wait_for_input(self):
        input("Нажмите ENTER.")
        view_model.set_state("menu")
