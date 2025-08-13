import cv2
import numpy as np
from copy import deepcopy

# === 이미지 불러오기 ==
background = cv2.imread("map2.png")
background = cv2.cvtColor(background, cv2.COLOR_BGR2RGB)

thickness = 10
blockSize = 98  # 측정값: 블록 세로 간격

# === 도형 그리기 함수 ===
def draw_line(img, pt1, pt2, color=(255, 38, 0)):
    # pt : (x, y)
    if pt1[0] == pt2[0]:  # 세로 (x 동일)
        Pt1 = [pt1[0] - thickness, pt1[1]]
        Pt2 = [pt1[0] + thickness, pt1[1]]
        Pt3 = [pt2[0] + thickness, pt2[1]]
        Pt4 = [pt2[0] - thickness, pt2[1]]
    else:  # 가로 (y 동일)
        Pt1 = [pt1[0], pt1[1] - thickness]
        Pt2 = [pt1[0], pt1[1] + thickness]
        Pt3 = [pt2[0], pt2[1] + thickness]
        Pt4 = [pt2[0], pt2[1] - thickness]

    Pts = np.array([Pt1, Pt2, Pt3, Pt4])
    cv2.fillPoly(img, np.int32([Pts]), color)

def draw_triangle(img, point, d):
    # point: (x, y) - 삼각형 중심 기준
    if d == "left":
        pt = np.array([[point[0], point[1] - 22],
                       [point[0] - 36, point[1]],
                       [point[0], point[1] + 22]])
    else:
        pt = np.array([[point[0], point[1] - 22],
                       [point[0] + 36, point[1]],
                       [point[0], point[1] + 22]])
    cv2.fillPoly(img, [pt], (255, 38, 0))

# === 핀 이미지 불러오기 ===
pin = cv2.imread('pin.png')                      # BGR
pin = cv2.cvtColor(pin, cv2.COLOR_BGR2RGB)       # RGB
ratio = 0.6
pin = cv2.resize(pin, dsize=(0,0), fx=ratio, fy=ratio)
pin_h, pin_w = pin.shape[:2]
pin_center_offset = (pin_h // 2, pin_w // 2)  # (cy, cx)

def makepin(img, pt):
    """
    img : 배경 이미지 (H, W, 3)
    pt  : (x, y) - 핀을 놓고 싶은 중앙 기준점 (이미지 좌표계)
    """
    h, w = img.shape[:2]
    ph, pw = pin_h, pin_w
    cy, cx = pin_center_offset

    y1 = int(pt[1] - cy)
    y2 = y1 + ph
    x1 = int(pt[0] - cx)
    x2 = x1 + pw

    oy1 = max(0, y1)
    oy2 = min(h, y2)
    ox1 = max(0, x1)
    ox2 = min(w, x2)

    if oy1 >= oy2 or ox1 >= ox2:
        return

    sy1 = oy1 - y1
    sy2 = sy1 + (oy2 - oy1)
    sx1 = ox1 - x1
    sx2 = sx1 + (ox2 - ox1)

    subpin = pin[sy1:sy2, sx1:sx2]
    mask = (subpin != [0,0,0]).any(axis=2)

    img_region = img[oy1:oy2, ox1:ox2]
    img_region[mask] = subpin[mask]
    img[oy1:oy2, ox1:ox2] = img_region

# === 측정된 라인 좌표 (map2.png 기준) ===
line_x = {
    1: 20,   # D22~D09 중심 X
    2: 630,   # D08~B39 중심 X
    3: 1270,  # B38~B06 중심 X
    4: 1900   # B05~A01 중심 X
}
line_y_start = {
    1: 250,
    2: 250,
    3: 250,
    4: 250
}

# === 부스 매핑 ===
booth = {}
# 라인 1
for i, code in enumerate(["D22","D21","D20","D19","D18","D17","D16","D15","D14","D13","D12","D11","D10","D09"]):
    booth[code] = (1, i, "left")
# 라인 2
codes_line2 = ["D08","D07","D06","D05","D04","D03","D02","D01",
               "C09","C08","C07","C06","C05","C04","C03","C02","C01",
               "B43","B42","B41","B40","B39"]
for i, code in enumerate(codes_line2):
    booth[code] = (2, i, "left")
# 라인 3
codes_line3 = ["B38","B37","B36","B35","B34","B33","B32","B31","B30","B29","B28","B27","B26","B25","B24","B23","B22","B21","B20",
               "B19","B18","B17","B16","B15","B14","B13","B12","B11","B10","B09","B08","B07","B06"]
for i, code in enumerate(codes_line3):
    booth[code] = (3, i, "right")
# 라인 4
codes_line4 = ["B05","B04","B03","B02","B01","A10","A09","A08","A07","A06","A05","A04","A03","A02","A01"]
for i, code in enumerate(codes_line4):
    booth[code] = (4, i, "right")

# === 통로(aisle) 자동 계산 (인접 라인 중심의 중간값) ===
aisles = {
    1: 320,  # between line1 & line2
    2: 950,  # between line2 & line3
    3: 1580   # between line3 & line4
}

# 현재 위치 (현 위치 좌표) - 필요 시 수정하세요
hx, hy = 732, 1700

def get_aisle_for_booth(line, idx):
    if line == 1:
        return 1
    elif line == 2:
        if idx <= 13:  # C04까지
            return 1
        else:          # B43~B39
            return 2
    elif line == 3:
        if idx <= 15:  # B38~B24
            return 2
        else:          # B23~B06
            return 3
    elif line == 4:
        return 3
    
# === 화살표 함수: 통로를 통해 이동하도록 경로 생성 ===
def arrow(team_code):
    edited = deepcopy(background)
    print(booth[team_code])
    # 1. 팀 좌표 구하기
    line, idx, _ = booth[team_code]  # booth dict: {팀코드: (열번호, 인덱스)}
    aisle_idx= get_aisle_for_booth(line,idx)
    tx = line_x[line]
    ty = line_y_start[line] + (idx+1) * blockSize

    # 2. 현재 위치(hx, hy)는 미리 정의했다고 가정
    #    hx, hy = 출입문 혹은 시작 위치 좌표
    cx, cy = hx, hy+50
    box_half = 42
    pin_offset = 26

    if aisle_idx < line:  # 통로가 왼쪽
        tx = tx - box_half - 185
        pin_x = tx - pin_offset +140
        direction = "right"
    else:  # 통로가 오른쪽
        tx = tx + box_half + 185
        pin_x = tx + pin_offset -140
        direction = "left"
    # 3. 통로를 통해 이동 경로 그리기
    # 3-1. 세로로 통로 y좌표까지 이동
    aisle_x = aisles[aisle_idx]  # 통로의 x좌표
    cv2.line(edited, (cx, cy), (aisle_x, cy), (255, 0, 0), 15)

    # 3-2. 통로 방향으로 x좌표 이동
    
    cv2.line(edited, (aisle_x, cy), (aisle_x, ty), (255, 0, 0), 15)

    # 3-3. 통로에서 목표 부스 옆으로 이동
    cv2.line(edited, (aisle_x, ty), (tx, ty), (255, 0, 0), 15)

    # 4. 화살표/핀을 통로 쪽 옆에 배치


    draw_triangle(edited, (tx, ty), direction)
    makepin(edited, (pin_x, ty - 60))

    return edited

# === 테스트 및 저장 예시 ===
# if __name__ == "__main__":
#     img = arrow("A09")
#     # 결과 저장 (RGB -> BGR 변환)
#     cv2.imwrite("result_aisle_route.png", cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
#     print("saved: result_aisle_route.png")
