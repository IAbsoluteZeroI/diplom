from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QTextBrowser
from PyQt5.QtWidgets import QDialog, QPushButton, QLabel
from PyQt5 import uic, QtCore
import time

from .UI import *
from ...view_model.main_view_model import view_model
from ...utils.commands import GetTwoCameras, TrackVideoCommand
from PyQt5.QtCore import QTimer


class MenuView(QWidget):
    def __init__(self, main_window) -> None:
        super().__init__()
        self.main_window = main_window
        self.main_window.setCentralWidget(self)
        uic.loadUi(menu_view_ui, self)
        self.__setup_buttons()

        self.infoLabel: QLabel
        self.infoLabel.setText(f"какая то информация")

    def __setup_buttons(self):
        self.toTwoVideoTrackingViewButton: QPushButton
        self.toTwoVideoTrackingViewButton.clicked.connect(
            lambda: view_model.set_state("track_two_videos")
        )


class MessageView(QDialog):
    __confirm_button: QPushButton
    __message_label: QLabel

    def __init__(self, label_text=None):
        super().__init__()
        uic.loadUi(message_view_ui, self)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)

        self.messageLabel.setText(label_text)
        self.confirmButton.clicked.connect(lambda: self.close())



class TrackingView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.main_window.setCentralWidget(self)
        self.two_cameras = None

        uic.loadUi(tracking_info_ui, self)

        self.toMenuViewButton.clicked.connect(lambda:view_model.set_state('menu'))
        self.__show_two_cameras()


    def __show_two_cameras(self):
        two_cameras = GetTwoCameras().execute()
        if len(two_cameras) == 2 and (two_cameras[0] is not None or two_cameras[1] is not None):
            self.camera1 = two_cameras[0]
            self.camera2 = two_cameras[1]

            info_about_two_cameras = ""
            for camera in two_cameras:
                info_about_two_cameras += (
                    f"Camera: id {camera.id}, video_path {camera.video_path}"
                )
                info_about_two_cameras += "<br/>"
            self.trackingInfo.append(f"<span>{info_about_two_cameras}</span>")
            self.startTrackingButton.clicked.connect(self.__start_tracking)
        else:
            self.trackingInfo.append(f"<span>Камер нет</span>")

    def __start_tracking(self):
        self.trackingInfo.append(f"<span><br/>Трекинг двух видео...</span>")
        self.trackingInfo.append(f"<span><br/><br/>Трекинг первого видео...</span>")
        QTimer.singleShot(100, self.__track_camera1)
        

    def __track_camera1(self):
        # time.sleep(1)
        # camera1_events = ['результат трекинга 1']
        camera1_events = TrackVideoCommand(self.camera1, "camera1_result.mp4").execute()
        self.trackingInfo.append(f"<span>Результат трекинга первой камеры:</span>")
        for event in camera1_events:
            self.trackingInfo.append(
                # event
                f'<span>{event.obj} {event.type.name} {event.date.strftime("%S")}</br></span>'
            )
        
        self.trackingInfo.append(f"<span><br/><br/>Трекинг второго видео...</span>")
        QTimer.singleShot(100, self.__track_camera2)

    
    def __track_camera2(self):
        # time.sleep(1)
        # camera2_events = ['результат трекинга 2']
        camera2_events = TrackVideoCommand(self.camera2, "camera2_result.mp4").execute()
        self.trackingInfo.append(f"<span>Результат трекинга второй камеры:</span>")
        for event in camera2_events:
            self.trackingInfo.append(
                # event
                f'<span>{event.obj} {event.type.name} {event.date.strftime("%S")}</br></span>'
            )