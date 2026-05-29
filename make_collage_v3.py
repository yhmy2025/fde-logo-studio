"""朋友圈Logo拼图 v3 — 横条展示，高质量"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

logo_dir = r"C:\Users\YH2\Desktop\CC文档\logo_compare_v3"
out_path = r"C:\Users\YH2\Desktop\CC文档\Logo进化_朋友圈配图_v3.png"

# 每个风格选最佳1张
picks = [
    ("badge_圆徽主色.png", "徽章"),
    ("geometric_圆形徽记.png", "几何"),
    ("gradient_对角渐变.png", "渐变"),
    ("abstract_重叠圆.png", "抽象"),
]

images = []
labels = []
for fname, label in picks:
    fp = os.path.join(logo_dir, fname)
    if os.path.exists(fp):
        images.append(Image.open(fp).convert("RGBA"))
        labels.append(label)
    else:
        print(f"Missing: {fname}")

if len(images) < 4:
    exit(1)

# 画布：横条布局，每个logo 400x400，间距18
cell = 420
gap = 16
pad_x = 40
pad_top = 50
label_h = 36
bottom_h = 70

W = pad_x * 2 + cell * 4 + gap * 3
H = pad_top + cell + label_h + 16 + bottom_h

bg = Image.new("RGBA", (W, H), (18, 22, 34, 255))
draw = ImageDraw.Draw(bg)

# 字体
font_paths = ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf"]
f_title = f_label = None
for fp in font_paths:
    if os.path.exists(fp):
        try:
            f_title = ImageFont.truetype(fp, 32)
            f_label = ImageFont.truetype(fp, 24)
            break
        except:
            continue

# 标题
title = "谊璜贸易 · 同一品牌四种风格"
if f_title:
    bbox = draw.textbbox((0, 0), title, font=f_title)
    tw = bbox[2] - bbox[0]
    draw.text(((W-tw)//2, 18), title, font=f_title, fill=(220, 225, 240))

# 放置logo
for i, (img, label) in enumerate(zip(images, labels)):
    x = pad_x + i * (cell + gap)
    y = pad_top
    
    # 卡片背景圆角
    card = Image.new("RGBA", (cell, cell+label_h), (0,0,0,0))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle([1, 1, cell-1, cell+label_h-1], radius=14,
                          fill=(28, 33, 48, 255), outline=(55, 62, 82, 255), width=1)
    bg.paste(card, (x, y), card)
    
    # Logo居中缩放
    logo_size = cell - 40
    scaled = img.copy()
    scaled.thumbnail((logo_size, logo_size), Image.LANCZOS)
    lx = x + (cell - scaled.width) // 2
    ly = y + (cell - label_h - scaled.height) // 2
    bg.paste(scaled, (lx, ly), scaled)
    
    # 标签
    if f_label:
        bbox_l = draw.textbbox((0, 0), label, font=f_label)
        lw = bbox_l[2] - bbox_l[0]
        draw.text((x + (cell - lw) // 2, y + cell + 4), label, font=f_label, fill=(170, 178, 200))

# 底部
if f_label:
    footer = "从手画到8种风格系统，Logo生成器迭代记"
    bbox_f = draw.textbbox((0, 0), footer, font=f_label)
    fw = bbox_f[2] - bbox_f[0]
    draw.text(((W-fw)//2, H - 50), footer, font=f_label, fill=(120, 128, 150))

bg.save(out_path, quality=95)
print(f"Saved: {out_path} ({W}x{H})")
