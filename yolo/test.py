from ultralytics import YOLO

# 학습한 내 모델 불러오기
model = YOLO('runs/detect/train/weights/best.pt')  # 실제 경로로 변경

# 이미지에 대해 예측
results = model.predict(source=r'C:\Users\user\Desktop\Hanbada\Hanbada\dataset\(C01) 1108_1109_1114_1117.png', imgsz=1600)

# 결과 확인 및 저장
for result in results:
    result.show()   # 화면에 박스 표시
    result.save()   # 결과 이미지 저장 (runs/detect 폴더)
