"""号2小红书封面 - 字体排版风 (不会翻车)"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, math

W, H = 1080, 1440
out_dir = r"C:\Users\YH2\Desktop\CC文档"
img = Image.new("RGB", (W, H), (18, 20, 28))
draw = ImageDraw.Draw(img)

# ── 字体 ──
font_paths = [
    "C:/Windows/Fonts/msyhbd.ttf",   # 微软雅黑粗体
    "C:/Windows/Fonts/msyh.ttc",     # 微软雅黑
    "C:/Windows/Fonts/simhei.ttf",   # 黑体
]
f_bold = f_body = f_small = f_num = None
for fp in font_paths[:1]:
    if os.path.exists(fp):
        try: f_bold = ImageFont.truetype(fp, 96); break
        except: pass
for fp in font_paths:
    if os.path.exists(fp):
        try:
            f_body = ImageFont.truetype(fp, 52)
            f_small = ImageFont.truetype(fp, 28)
            f_num = ImageFont.truetype(fp, 200)
            break
        except: continue

if f_bold is None: f_bold = f_body

# ── 背景微光 ──
for y in range(0, H, 3):
    for x in range(0, W, 6):
        r, g, b = img.getpixel((x, y))
        noise = (y / H) * 15 + (x / W) * 8
        draw.point((x, y), fill=(int(r+noise), int(g+noise-3), int(b+noise-5)))

# 中心柔光
center_glow = Image.new("RGBA", (W, H), (0,0,0,0))
gd = ImageDraw.Draw(center_glow)
for r in range(400, 0, -1):
    alpha = int(18 * (1 - r/400))
    gd.ellipse([W//2-r, H//2-100-r, W//2+r, H//2-100+r], fill=(80,100,160, alpha))
center_glow = center_glow.filter(ImageFilter.GaussianBlur(8))
img = Image.alpha_composite(img.convert("RGBA"), center_glow).convert("RGB")
draw = ImageDraw.Draw(img)

# ── 左侧竖线装饰 ──
for i in range(6):
    lx = 120 + i * 18
    color = (60 + i*15, 75 + i*12, 120 + i*10)
    draw.line([(lx, 300), (lx, 1050)], fill=color, width=1)

# ── 数字 "4" 水印 ──
bbox4 = draw.textbbox((0,0), "4", font=f_num)
w4 = bbox4[2] - bbox4[0]
draw.text((W - w4 - 80, 200), "4", font=f_num, fill=(35, 40, 60))

# ── 主标题（分行排版） ──
lines_main = [
    ("辞职", (0, 0)),
    ("年", (0, 0)),
    ("后才发现", (0, 0)),
]

# 手工精排
y_start = 380

# Line 1: "辞职4年"
line1 = "辞职4年后才发现"
bbox1 = draw.textbbox((0,0), line1, font=f_bold)
w1 = bbox1[2] - bbox1[0]
x1 = 240
draw.text((x1, y_start), line1, font=f_bold, fill=(255, 255, 255))

# Line 2: "上班最可怕的"
line2 = "上班最可怕的"
bbox2 = draw.textbbox((0,0), line2, font=f_bold)
w2 = bbox2[2] - bbox2[0]
draw.text((x1, y_start + 130), line2, font=f_bold, fill=(255, 255, 255))

# Line 3: "不是996" — 强调 "996" 用金色
line3a = "不是"
line3b = "996"
bbox3a = draw.textbbox((0,0), line3a, font=f_bold)
draw.text((x1, y_start + 260), line3a, font=f_bold, fill=(255, 255, 255))
draw.text((x1 + bbox3a[2] + 15, y_start + 260), line3b, font=f_bold, fill=(255, 200, 100))

# ── 分隔线 ──
draw.line([(x1 + 40, y_start + 420), (x1 + 340, y_start + 420)], fill=(80, 95, 130), width=2)

# ── 副标题 ──
sub_lines = [
    "是上了那么多年班",
    "离了平台，什么都没有",
]
for i, sl in enumerate(sub_lines):
    bbox_s = draw.textbbox((0,0), sl, font=f_body)
    sw = bbox_s[2] - bbox_s[0]
    if i == 1:
        # 最后半句用暖色
        draw.text((x1 + 30, y_start + 470 + i*70), "离了平台，", font=f_body, fill=(200, 210, 225))
        draw.text((x1 + 30 + draw.textbbox((0,0), "离了平台，", font=f_body)[2], y_start + 470 + i*70),
                  "什么都没有", font=f_body, fill=(255, 180, 100))
    else:
        draw.text((x1 + 30, y_start + 470 + i*70), sl, font=f_body, fill=(200, 210, 225))

# ── 底部信息 ──
bottom_y = 1250
# 底部细线
draw.line([(W//2 - 60, bottom_y), (W//2 + 60, bottom_y)], fill=(60, 70, 90), width=1)

footer = "深夜树洞 · 周五"
bbox_f = draw.textbbox((0,0), footer, font=f_small)
fw = bbox_f[2] - bbox_f[0]
draw.text(((W-fw)//2, bottom_y + 20), footer, font=f_small, fill=(100, 110, 130))

# ── 顶部细节点缀 ──
for i, x in enumerate([200, 400, 600, 800]):
    draw.ellipse([x, 60, x+4, 64], fill=(60 + i*10, 80 + i*8, 110 + i*6))

# ── 保存 ──
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "心理树洞_0529_封面.png")
img.save(out_path, quality=95)
print(f"OK: {out_path}")
print(f"Size: {W}x{H}")
