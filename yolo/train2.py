import os
from ultralytics import YOLO
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

model = YOLO("yolo11m.pt")

if __name__ == '__main__':
    model.train(data="data.yaml", epochs=100, imgsz=1600, batch=8, workers=6)
    model.val(save=True) 
