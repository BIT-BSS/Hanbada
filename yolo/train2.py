from ultralytics import YOLO

model = YOLO("yolov8n.pt")

if __name__ == '__main__':
    model.train(data="data.yaml", epochs=50, imgsz=1280, batch =4)
    model.val(save=True) 
