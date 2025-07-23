#PDF로 변환
import os
import subprocess

pptx_dir = './data/2024_OceanICT/'
output_dir = './data/2024_OceanICT/'

os.makedirs(output_dir, exist_ok=True)

for file in os.listdir(pptx_dir):
    if file.endswith('.pptx'):
        input_path = os.path.join(pptx_dir, file)
        # LibreOffice를 이용해 PDF로 변환
        subprocess.run([
            'libreoffice',
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', output_dir,
            input_path
        ])
        os.remove(input_path)  # 변환 후 원본 PPTX 파일 삭제
        print(f"변환 완료: {file}")