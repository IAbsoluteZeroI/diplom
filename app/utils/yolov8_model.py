from ultralytics import YOLO


MODEL = "app/utils/best1280.pt"
model = YOLO(MODEL)
model.fuse()


CLASS_NAMES_DICT = model.names
CLASS_ID = [0, 1, 2, 3, 4, 5, 6, 7]

CLASS_ID_BY_NAME = {
    "chair": 0,
    "person": 1,
    "interactive whiteboard": 2,
    "keyboard": 3,
    "laptop": 4,
    "monitor": 5,
    "pc": 6,
    "table": 7,
}
