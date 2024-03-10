from .view.pyqt_view.main_window import MainWindow
from supervision.geometry.dataclasses import Point
from PyQt5.QtWidgets import QApplication
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .model.models import Camera, Place, CustomLineCounter
from .model.models import Base


def run_pyqt_app():
    app = QApplication(sys.argv)
    sys.path.append(".")
    sys.path.append("./app")
    main_window = MainWindow()

    app.exec()
    sys.exit()


def create_all():
    engine = create_engine("postgresql+psycopg2://admin:root@127.0.0.1:5432/db")
    engine.connect()
    Base.metadata.create_all(engine)


run_pyqt_app()
# create_all()

# json_db_manager.add_camera(Camera(
#     line_counter=CustomLineCounter(coord_left=Point(x=927,y=1063), coord_right=Point(x=739,y=227)),
#     video_path='lift.avi',
#     place=Place()
#     ))
# print(json_db_manager.get_cameras())







# engine = create_engine("postgresql+psycopg2://admin:root@127.0.0.1:5432/db")
# engine.connect()

# Session = sessionmaker(bind=engine)
# session = Session()


# test.avi [[1100, 230], [1200, 750]]
# place1 = Place()
# session.add(place1)
# session.commit()
# place2 = Place()
# session.add(place2)
# session.commit()
# camera1 = Camera(
#     video_path='kab24.avi',
#     line_counter=CustomLineCounter(coord_left_x=1200, coord_left_y=250, coord_right_x=1550, coord_right_y=350),
#     place_id=place1.id
#     )
# session.add(camera1)
# session.commit()
# session.close()
# camera2 = Camera(
#     video_path='lift.avi',
#     line_counter=CustomLineCounter(coord_left_x=740, coord_left_y=400, coord_right_x=1030, coord_right_y=950),
#     place_id=place2.id
#     )
# session.add(camera2)
# session.commit()
# place = session.query(Place).offset(1).first()
# camera = Camera(
#     video_path='lift.avi',
#     line_counter=CustomLineCounter(coord_left_x=740, coord_left_y=400, coord_right_x=1030, coord_right_y=950),
#     place_id=place.id
#     )
# session.add(camera)
# session.commit()
# session.close()
