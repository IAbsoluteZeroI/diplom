from .view.pyqt_view.main_window import MainWindow
from .model.data.json_db_manager import *
from .model.models import Camera, Place, CustomLineCounter
from supervision.geometry.dataclasses import Point
from PyQt5.QtWidgets import QApplication
import sys


# app = QApplication(sys.argv)
# sys.path.append(".")
# sys.path.append("./app")
# main_window = MainWindow()

# app.exec()
# sys.exit()

# json_db_manager.add_camera(Camera(
#     line_counter=CustomLineCounter(coord_left=Point(x=927,y=1063), coord_right=Point(x=739,y=227)),
#     video_path='lift.avi',
#     place=Place()
#     ))
# print(json_db_manager.get_cameras())


# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from .model.base import Base

# engine = create_engine("postgresql+psycopg2://admin:root@127.0.0.1:5432/db")
# engine.connect()


# Session = sessionmaker(bind=engine)
# session = Session()
# # [[1100, 230], [1200, 750]]

# place = Place()
# session.add(place)
# session.commit()

# camera = Camera(
#     video_path='test.avi',
#     line_counter=CustomLineCounter(coord_left_x=1100, coord_left_y=230, coord_right_x=1200, coord_right_y=750),
#     place_id=place.id
#     )
# session.add(camera)

# session.add(camera)
# session.commit()
# session.close()
