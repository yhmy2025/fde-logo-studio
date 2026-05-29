#!/usr/bin/env python3
"""号2配图生成 - 深夜职场情绪风"""

from PIL import Image, ImageDraw, ImageFilter, ImageFont
import os, random, math

W, H = 1080, 1440
out_dir = r"C:\Users\YH2\Desktop\CC文档"
img = Image.new("RGB", (W, H), (0, 0, 0))
draw = ImageDraw.Draw(img)

# ── 1. 深夜城市底板 ──
# 深蓝黑渐变
for y in range(H):
    t = y / H
    r = int(8 + 12 * t)
    g = int(10 + 18 * t)
    b = int(30 + 40 * t)
    for x in range(0, W, 2):
        draw.rectangle([x, y, x+1, y], fill=(r, g, b))

# ── 2. 远处城市建筑剪影 ──
buildings = []
for _ in range(14):
    bx = random.randint(0, W)
    bw = random.randint(60, 180)
    bh = random.randint(80, 350)
    by = H - bh
    brightness = random.randint(12, 35)
    buildings.append((bx, by, bx+bw, by+bh, brightness))

for bx, by, bx2, by2, bright in buildings:
    # 建筑体
    draw.rectangle([bx, by, bx2, by2], fill=(bright, bright+5, bright+15))
    # 零星窗户暖光
    for wy in range(by+15, by2-15, random.randint(18, 35)):
        for wx in range(bx+8, bx2-8, random.randint(15, 30)):
            if random.random() < 0.4:
                ww, wh = 3, 2
                wc = random.choice([
                    (255, 200, 100), (255, 180, 80), (200, 150, 60),
                    (255, 220, 140), (180, 140, 50), (240, 190, 90)
                ])
                draw.rectangle([wx, wy, wx+ww, wy+wh], fill=wc)

# 建筑底部光晕
for bx, by, bx2, by2, bright in buildings:
    glow = img.crop((bx-5, by-5, bx2+5, by2+5))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=3))
    img.paste(glow, (bx-5, by-5))

# ── 3. 底部地面反光 ──
for y in range(H-260, H, 1):
    alpha = (y - (H-260)) / 260
    r = int(15 + 15 * alpha)
    g = int(20 + 20 * alpha)
    b = int(35 + 30 * alpha)
    for x in range(0, W, 2):
        draw.rectangle([x, y, x+1, y], fill=(r, g, b))

# 地面几盏路灯/光点
for lx in [200, 540, 880]:
    for r_outer in [60, 40, 25]:
        for angle in range(0, 360, 3):
            rad = math.radians(angle)
            rx = int(lx + r_outer * math.cos(rad) * 2.5)
            ry = int(H-160 + r_outer * math.sin(rad) * 0.3)
            if 0 <= rx < W and 0 <= ry < H:
                dist = math.sqrt((rx-lx)**2 + ((ry-(H-160))*3)**2)
                a = max(0, 1 - dist/200)
                c = int(40 + 25 * a)
                draw.point((rx, ry), fill=(c+20, c+10, c))

# ── 4. 空办公桌剪影（左下角） ──
# 桌面
for dy in range(40):
    y = H-120+dy
    r = int(25 + dy*0.5)
    draw.rectangle([80, y, 420, y+1], fill=(r, r+3, r+10))

# 显示器剪影
for dx in range(100):
    x = 160 + dx
    h = 180 + int(20*math.sin(dx/60))
    for dy in range(h):
        y2 = H-120-h+dy
        r = int(18 + dx*0.03)
        draw.point((x, y2), fill=(r, r+2, r+8))

# 屏幕微光
screen_x, screen_y, screen_w, screen_h = 170, H-290, 80, 140
for sx in range(screen_x, screen_x+screen_w):
    for sy in range(screen_y, screen_y+screen_h):
        dist_edge = min(sx-screen_x, screen_x+screen_w-sx, sy-screen_y, screen_y+screen_h-sy)
        a = min(1.0, dist_edge/15)
        c = int(30 + 180*a)
        draw.point((sx, sy), fill=(c, c+20, c+40))

# ── 5. 窗外雨痕/雾感 ──
for _ in range(200):
    rx = random.randint(0, W)
    ry = random.randint(0, H-400)
    length = random.randint(15, 60)
    alpha_val = random.randint(3, 12)
    for offset in range(length):
        if ry+offset < H:
            draw.point((rx, ry+offset), fill=(alpha_val+3, alpha_val+5, alpha_val+12))

# ── 6. 大气光晕 ──
for _ in range(80):
    cx = random.randint(0, W)
    cy = random.randint(80, H-500)
    radius = random.randint(20, 80)
    for angle in range(0, 360, 8):
        rad = math.radians(angle)
        for r_ in range(radius):
            rx = int(cx + r_ * math.cos(rad))
            ry = int(cy + r_ * math.sin(rad) * 0.4)
            if 0 <= rx < W and 0 <= ry < H:
                a = max(0, 1 - r_/radius) * 0.08
                r, g, b = img.getpixel((rx, ry))
                nr = min(255, int(r + 8*a*255))
                ng = min(255, int(g + 6*a*255))
                nb = min(255, int(b + 15*a*255))
                draw.point((rx, ry), fill=(nr, ng, nb))

# ── 7. 文字 ──
font_paths = [
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    "C:/Windows/Fonts/simsun.ttc",
]
font_title = None
font_sub = None
for fp in font_paths:
    if os.path.exists(fp):
        try:
            font_title = ImageFont.truetype(fp, 72)
            font_sub = ImageFont.truetype(fp, 36)
            break
        except:
            continue

if font_title is None:
    font_title = ImageFont.load_default()
    font_sub = font_title

def draw_text_centered(draw, text, y, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2
    draw.text((x, y), text, font=font, fill=fill)
    return x, y, tw

# 主标题
title = "最怕的不是996"
draw_text_centered(draw, title, 520, font_title, (255, 255, 255))

# 副标题
sub = "是996了，还不知道为什么"
draw_text_centered(draw, sub, 620, font_sub, (180, 190, 210))

# 底部小字
tiny_font = None
for fp in font_paths:
    if os.path.exists(fp):
        try:
            tiny_font = ImageFont.truetype(fp, 24)
            break
        except:
            continue
if tiny_font is None:
    tiny_font = ImageFont.load_default()

credit = "深夜树洞 · 周五晚安"
bbox = draw.textbbox((0, 0), credit, font=tiny_font)
tw2 = bbox[2] - bbox[0]
draw.text(((W-tw2)//2, H-100), credit, font=tiny_font, fill=(100, 105, 120))

# ── 8. 整体氛围：暗角 ──
for y in range(H):
    for x in range(0, W, 3):
        dx = min(x, W-x) / (W/2)
        dy = min(y, H-y) / (H/2)
        dist = 1 - min(dx, dy) * 0.7
        if dist > 0:
            r, g, b = img.getpixel((x, y))
            factor = max(0.3, 1 - dist*0.65)
            draw.point((x, y), fill=(int(r*factor), int(g*factor), int(b*factor)))

# 保存
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "心理树洞_0529_配图.png")
img.save(out_path, quality=95)
print(f"✅ {out_path}")
