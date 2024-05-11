from ultralytics import YOLO

# Load the YOLOv8 model
model = YOLO("./worker/utils/640.pt")

# Export the model to TensorRT format
model.export(format="engine")  # creates 'yolov8n.engine'
