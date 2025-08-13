from PIL import Image, ImageDraw
import numpy as np
from copy import deepcopy

# === 이미지 불러오기 ===
background = Image.open("map2.png").convert("RGB")
thickness = 10
blockSize = 98  # 측정값: 블록 세로 간격

# === 도형 그리기 함수 ===
def draw_line(img_draw, pt1, pt2, color=(255, 38, 0)):
    # Pillow는 fill 색상은 RGB 튜플로 넣으면 됨
    if pt1[0] == pt2[0]:  # 세로 (x 동일)
        Pt1 = (pt1[0] - thickness, pt1[1])
        Pt2 = (pt1[0] + thickness, pt1[1])
        Pt3 = (pt2[0] + thickness, pt2[1])
        Pt4 = (pt2[0] - thickness, pt2[1])
    else:  # 가로 (y 동일)
        Pt1 = (pt1[0], pt1[1] - thickness)
        Pt2 = (pt1[0], pt1[1] + thickness)
        Pt3 = (pt2[0], pt2[1] + thickness)
        Pt4 = (pt2[0], pt2[1] - thickness)

    img_draw.polygon([Pt1, Pt2, Pt3, Pt4], fill=color)

def draw_triangle(img_draw, point, d):
    if d == "left":
        pt = [(point[0], point[1] - 22),
              (point[0] - 36, point[1]),
              (point[0], point[1] + 22)]
    else:
        pt = [(point[0], point[1] - 22),
              (point[0] + 36, point[1]),
              (point[0], point[1] + 22)]
    img_draw.polygon(pt, fill=(255, 38, 0))

# === 핀 이미지 불러오기 ===
pin = Image.open("pin.png").convert("RGBA")
ratio = 0.6
pin_w, pin_h = pin.size
pin = pin.resize((int(pin_w * ratio), int(pin_h * ratio)))
pin_w, pin_h = pin.size
pin_center_offset = (pin_h // 2, pin_w // 2)  # (cy, cx)

def makepin(img, pt):
    """
    img : Pillow Image (RGB or RGBA)
    pt  : (x, y) - 핀 중앙 기준
    """
    cx, cy = pt
    px, py = pin_center_offset[1], pin_center_offset[0]

    # 위치 계산
    paste_x = int(cx - px)
    paste_y = int(cy - py)

    img.paste(pin, (paste_x, paste_y), mask=pin)

# === 측정된 라인 좌표 (map2.png 기준) ===
line_x = {
    1: 20,   
    2: 630,   
    3: 1270,  
    4: 1900
}
line_y_start = {
    1: 250,
    2: 250,
    3: 250,
    4: 250
}

# === 부스 매핑 ===
booth = {}
for i, code in enumerate(["D22","D21","D20","D19","D18","D17","D16","D15","D14","D13","D12","D11","D10","D09"]):
    booth[code] = (1, i, "left")
codes_line2 = ["D08","D07","D06","D05","D04","D03","D02","D01",
               "C09","C08","C07","C06","C05","C04","C03","C02","C01",
               "B43","B42","B41","B40","B39"]
for i, code in enumerate(codes_line2):
    booth[code] = (2, i, "left")
codes_line3 = ["B38","B37","B36","B35","B34","B33","B32","B31","B30","B29","B28","B27","B26","B25","B24","B23","B22","B21","B20",
               "B19","B18","B17","B16","B15","B14","B13","B12","B11","B10","B09","B08","B07","B06"]
for i, code in enumerate(codes_line3):
    booth[code] = (3, i, "right")
codes_line4 = ["B05","B04","B03","B02","B01","A10","A09","A08","A07","A06","A05","A04","A03","A02","A01"]
for i, code in enumerate(codes_line4):
    booth[code] = (4, i, "right")

aisles = {
    1: 320,
    2: 950,
    3: 1580
}

hx, hy = 732, 1700

def get_aisle_for_booth(line, idx):
    if line == 1:
        return 1
    elif line == 2:
        if idx <= 13:
            return 1
        else:
            return 2
    elif line == 3:
        if idx <= 15:
            return 2
        else:
            return 3
    elif line == 4:
        return 3

def get_location_image(team_code):
    edited = deepcopy(background)
    draw = ImageDraw.Draw(edited)

    line, idx, _ = booth[team_code]
    aisle_idx = get_aisle_for_booth(line, idx)
    tx = line_x[line]
    ty = line_y_start[line] + (idx+1) * blockSize -1860

    cx, cy = hx, hy + 50
    box_half = 42
    pin_offset = 26

    if aisle_idx < line:
        tx = tx - box_half - 185
        pin_x = tx - pin_offset + 140
        direction = "right"
    else:
        tx = tx + box_half + 185
        pin_x = tx + pin_offset - 140
        direction = "left"

    aisle_x = aisles[aisle_idx]
    draw.line([(cx, cy), (aisle_x, cy)], fill=(255, 0, 0), width=15)
    draw.line([(aisle_x, cy), (aisle_x, ty)], fill=(255, 0, 0), width=15)
    draw.line([(aisle_x, ty), (tx, ty)], fill=(255, 0, 0), width=15)

    draw_triangle(draw, (tx, ty), direction)
    makepin(edited, (pin_x, ty - 70))

    return edited

# === 실행 예시 ===
#if __name__ == "__main__":
#    img = get_location_image("B09")
#    img.show()  # 화면에서 바로 보기

