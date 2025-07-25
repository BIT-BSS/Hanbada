from pdf2image import convert_from_path
import os

pdf_folder = './poster'         # PDF 파일들이 들어있는 폴더 경로
output_folder = './images'    # 이미지를 저장할 폴더 경로
poppler_path = r'./poppler-24.08.0/Library/bin'  # 본인 PC에 맞게 수정

os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(pdf_folder):
    if filename.lower().endswith('.pdf'):
        pdf_path = os.path.join(pdf_folder, filename)
        base_name = os.path.splitext(filename)[0]
        images = convert_from_path(pdf_path, poppler_path=poppler_path)
        for i, image in enumerate(images):
            if len(images) == 1:
                image.save(f"{output_folder}/{base_name}.png", "PNG")
            else:
                image.save(f"{output_folder}/{base_name}_{i+1}.png", "PNG")
        print(f"{filename} 변환 완료")
