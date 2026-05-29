"""Logo进化对比拼图 - 朋友圈宣发"""
from PIL import Image, ImageDraw, ImageFont
import os

out_dir = r"C:\Users\YH2\Desktop\CC文档"
logo_dir = os.path.join(out_dir, "logo_compare_v2")

# 选4张代表：印章2张+极简2张
files = [
    "seal_墨金印.png", "seal_蓝金印.png",
    "minimal_白底主色.png", "minimal_白底双色.png"
]

images = []
for f in files:
    path = os.path.join(logo_dir, f)
    if os.path.exists(path):
        images.append(Image.open(path).convert("RGBA"))
    else:
        print(f"Missing: {f}")

if len(images) < 4:
    print("Not enough images")
    exit(1)

# 拼图: 2x2, 每格600x600, 间距20, 标题栏100
cell = 600
gap = 20
title_h = 120
cols, rows = 2, 2
canvas_w = cols * cell + (cols + 1) * gap
canvas_h = rows * cell + (rows + 1) * gap + title_h

bg = Image.new("RGB", (canvas_w, canvas_h), (15, 18, 30))
draw = ImageDraw.Draw(bg)

# 标题
font_paths = ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf"]
font_title = None
font_label = None
for fp in font_paths:
    if os.path.exists(fp):
        try:
            font_title = ImageFont.truetype(fp, 36)
            font_label = ImageFont.truetype(fp, 22)
            break
        except:
            continue

title = "谊璜贸易 Logo 方案矩阵"
bbox = draw.textbbox((0, 0), title, font=font_title)
tw = bbox[2] - bbox[0]
draw.text(((canvas_w-tw)//2, 35), title, font=font_title, fill=(255, 255, 255))

labels = ["印章·墨金", "印章·蓝金", "极简·白底主色", "极简·白底双色"]
for i, (img, label) in enumerate(zip(images, labels)):
    row, col = i // cols, i % cols
    x = gap + col * (cell + gap)
    y = title_h + gap + row * (cell + gap)
    
    # 缩放居中
    scaled = img.copy()
    scaled.thumbnail((cell-30, cell-30), Image.LANCZOS)
    sx = x + (cell - scaled.width) // 2
    sy = y + (cell - scaled.height) // 2
    
    # 背景圆角卡片
    draw.rounded_rectangle([x, y, x+cell, y+cell], radius=16, fill=(28, 32, 48), outline=(50, 55, 75), width=1)
    bg.paste(scaled, (sx, sy), scaled if scaled.mode == 'RGBA' else None)
    
    # 标签
    bbox2 = draw.textbbox((0, 0), label, font=font_label)
    lw = bbox2[2] - bbox2[0]
    draw.text((x + (cell-lw)//2, y + cell - 30), label, font=font_label, fill=(160, 170, 190))

out_path = os.path.join(out_dir, "Logo进化_朋友圈配图.png")
bg.save(out_path, quality=95)
print(f"Saved: {out_path}")
