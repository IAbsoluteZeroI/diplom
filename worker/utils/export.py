from ultralytics import YOLO

# Load the YOLOv8 model
model = YOLO("worker/utils/models/new/640/yolov8m_640_80ep_16b.pt")

# Export the model to TensorRT format
model.export(format="engine")  # creates 'yolov8n.engine'
