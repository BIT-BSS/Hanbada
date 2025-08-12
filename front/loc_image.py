from PIL import Image, ImageDraw
import numpy as np
from copy import deepcopy

# 이미지 불러오기
background = Image.open('map.png').convert("RGB")

thickness = 10
blockSize = 84
n = 10

# 핀 이미지 불러오기 및 리사이즈
pin = Image.open('pin.png').convert("RGBA")
ratio = 0.6
new_size = (int(pin.width * ratio), int(pin.height * ratio))
pin = pin.resize(new_size)
pinpin = np.round(np.array([309, 105]) * ratio).astype(np.uint8)

def draw_line(draw, pt1, pt2, color=(255, 38, 0)):
    if pt1[0] == pt2[0]:
        # 세로선
        Pt1 = [pt1[0] - thickness, pt1[1]]
        Pt2 = [pt1[0] + thickness, pt1[1]]
        Pt3 = [pt2[0] + thickness, pt2[1]]
        Pt4 = [pt2[0] - thickness, pt2[1]]
        Pts = [Pt1, Pt2, Pt3, Pt4]
        draw.polygon(Pts, fill=color)
    elif pt1[1] == pt2[1]:
        # 가로선
        Pt1 = [pt1[0], pt1[1] - thickness]
        Pt2 = [pt1[0], pt1[1] + thickness]
        Pt3 = [pt2[0], pt2[1] + thickness]
        Pt4 = [pt2[0], pt2[1] - thickness]
        Pts = [Pt1, Pt2, Pt3, Pt4]
        draw.polygon(Pts, fill=color)

def draw_triangle(draw, point, d, color=(255, 38, 0)):
    if d == "left":
        pt = [[point[0], point[1] - 30],
              [point[0] - 40, point[1]],
              [point[0], point[1] + 30]]
    elif d == "right":
        pt = [[point[0], point[1] - 30],
              [point[0] + 40, point[1]],
              [point[0], point[1] + 30]]
    draw.polygon(pt, fill=color)

def makepin(img, pt):
    # pin 이미지 붙이기
    x_offset = pt[0] - pinpin[1]
    y_offset = pt[1] - pinpin[0]
    img.paste(pin, (x_offset, y_offset), pin)

def arrow(line, n, d):
    edited = background.copy()
    draw = ImageDraw.Draw(edited)

    if line == 1:
        draw_line(draw, (1670, 1890), (1670, 1770))
        draw_line(draw, (1670 + thickness, 1770), (400, 1770))
        draw_line(draw, (400, 1770 + thickness), (400, 1770 - blockSize * n))

        if d == 'right':
            draw_line(draw, (400 - thickness, 1770 - blockSize * n), (450, 1770 - blockSize * n))
            draw_triangle(draw, (450, 1770 - blockSize * n), 'right')
            makepin(edited, (450 + 250, 1770 - blockSize * n - 20))

        elif d == 'left':
            draw_line(draw, (400 + thickness, 1770 - blockSize * n), (350, 1770 - blockSize * n))
            draw_triangle(draw, (350, 1770 - blockSize * n), 'left')
            makepin(edited, (350 - 250, 1770 - blockSize * n - 20))

    elif line == 2:
        draw_line(draw, (1670, 1890), (1670, 1770))
        draw_line(draw, (1670 + thickness, 1770), (1035, 1770))
        draw_line(draw, (1035, 1770 + thickness), (1035, 1770 - blockSize * n))

        if d == 'right':
            draw_line(draw, (1035 - thickness, 1770 - blockSize * n), (1035 + 50, 1770 - blockSize * n))
            draw_triangle(draw, (1035 + 50, 1770 - blockSize * n), 'right')
            makepin(edited, (1035 + 50 + 250, 1770 - blockSize * n - 20))

        elif d == 'left':
            draw_line(draw, (1035 + thickness, 1770 - blockSize * n), (1035 - 50, 1770 - blockSize * n))
            draw_triangle(draw, (1035 - 50, 1770 - blockSize * n), 'left')
            makepin(edited, (1035 - 50 - 250, 1770 - blockSize * n - 20))

    elif line == 3:
        draw_line(draw, (1670, 1890), (1670, 1770))
        draw_line(draw, (1670, 1770 + thickness), (1670, 1770 - blockSize * n))

        if d == 'right':
            draw_line(draw, (1670 - thickness, 1770 - blockSize * n), (1670 + 50, 1770 - blockSize * n))
            draw_triangle(draw, (1670 + 50, 1770 - blockSize * n), 'right')
            makepin(edited, (1670 + 50 + 250, 1770 - blockSize * n - 20))

        elif d == 'left':
            draw_line(draw, (1670 + thickness, 1770 - blockSize * n), (1670 - 50, 1770 - blockSize * n))
            draw_triangle(draw, (1670 - 50, 1770 - blockSize * n), 'left')
            makepin(edited, (1670 - 50 - 250, 1770 - blockSize * n - 20))

    return edited

# 부스 매핑 정보는 그대로 사용
booth = {}

for i in range(17):
    if i >= 0 and i <= 2:
        booth[f'C{13 + i}'] = (1, i, 'left')
    if i >= 3:
        booth['D' + f'{i - 2}'.zfill(2)] = (1, i, 'left')
    if i >= 0 and i <= 10:
        booth['A' + f'{i + 1}'.zfill(2)] = (3, i, 'right')
    if i >= 11:
        booth['B' + f'{i - 10}'.zfill(2)] = (3, i, 'right')

for i in range(15):
    booth[f'B{39 + i}'] = (2, i + 1, 'left')
    if i >= 3:
        booth['C' + f'{i - 2}'.zfill(2)] = (1, i + 1, 'right')
    if i <= 2:
        booth['B' + f'{i + 54}'.zfill(2)] = (1, i + 1, 'right')

for i in range(16):
    booth[f'B{23 + i}'] = (2, i + 1, 'right')
    booth['B' + f'{7 + i}'.zfill(2)] = (3, i + 1, 'left')


# 최종 함수
def get_location_image(team_code):
    team_cord = booth[team_code]
    img = arrow(team_cord[0], team_cord[1], team_cord[2])
    return img
