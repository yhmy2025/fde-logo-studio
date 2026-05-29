"""朋友圈Logo拼图 — KH投资公司版"""
from PIL import Image, ImageDraw, ImageFont
import os

logo_dir = r"C:\Users\YH2\Desktop\CC文档\logo_compare_kh"
out_path = r"C:\Users\YH2\Desktop\CC文档\Logo进化_朋友圈配图_KH.png"

picks = [
    ("badge_圆徽主色.png", "徽章"),
    ("geometric_菱形.png", "几何"),
    ("gradient_对角渐变.png", "渐变"),
    ("abstract_重叠圆.png", "抽象"),
]

images, labels = [], []
for fname, label in picks:
    fp = os.path.join(logo_dir, fname)
    if os.path.exists(fp):
        images.append(Image.open(fp).convert("RGBA"))
        labels.append(label)

if len(images) < 4:
    print(f"Only found {len(images)} images")
    exit(1)

cell, gap, pad_x, pad_top, label_h, bottom_h = 420, 18, 40, 56, 36, 70
W = pad_x * 2 + cell * 4 + gap * 3
H = pad_top + cell + label_h + 18 + bottom_h

bg = Image.new("RGBA", (W, H), (15, 19, 30, 255))
draw = ImageDraw.Draw(bg)

font_paths = ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf"]
f_title = f_label = None
for fp in font_paths:
    if os.path.exists(fp):
        try:
            f_title = ImageFont.truetype(fp, 30)
            f_label = ImageFont.truetype(fp, 22)
            break
        except:
            continue

title = "KH投资 · 同一品牌四种方案"
if f_title:
    bbox = draw.textbbox((0, 0), title, font=f_title)
    draw.text(((W - bbox[2] + bbox[0]) // 2, 18), title, font=f_title, fill=(225, 230, 245))

for i, (img, label) in enumerate(zip(images, labels)):
    x = pad_x + i * (cell + gap)
    y = pad_top

    card = Image.new("RGBA", (cell, cell + label_h), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle([1, 1, cell-1, cell+label_h-1], radius=14,
                          fill=(25, 30, 45, 255), outline=(50, 58, 78, 255), width=1)
    bg.paste(card, (x, y), card)

    scaled = img.copy()
    scaled.thumbnail((cell - 50, cell - 50), Image.LANCZOS)
    lx = x + (cell - scaled.width) // 2
    ly = y + (cell - label_h - scaled.height) // 2
    bg.paste(scaled, (lx, ly), scaled)

    if f_label:
        bbox_l = draw.textbbox((0, 0), label, font=f_label)
        lw = bbox_l[2] - bbox_l[0]
        draw.text((x + (cell - lw) // 2, y + cell + 4), label, font=f_label, fill=(165, 173, 195))

if f_label:
    footer = "8种风格系统，同品牌名可达32版方案"
    bbox_f = draw.textbbox((0, 0), footer, font=f_label)
    fw = bbox_f[2] - bbox_f[0]
    draw.text(((W - fw) // 2, H - 46), footer, font=f_label, fill=(115, 123, 145))

bg.save(out_path, quality=95)
print(f"Saved: {out_path} ({W}x{H})")
