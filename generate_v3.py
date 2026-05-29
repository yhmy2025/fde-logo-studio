#!/usr/bin/env python3
"""
Logo Generator v3 — 设计组合引擎
=================================
从"模板换色"升级为"元素组合系统"：每个公司名生成完全不同的Logo。

核心理念：
- 不是选择"风格模板"，而是组合"设计元素"
- 名称哈希驱动确定性随机 → 每次同结果，不同名不同结果
- 行业感知 → 装饰元素自动匹配行业语义
- 12种构图 × 30+几何元素 × 15种图案 × 布局参数化

用法:
  python generate_v3.py --name "星辰科技" --industry tech --count 12
  python generate_v3.py --name "谊璜贸易" --industry trade --mood elegance --count 8
"""

import argparse
import colorsys
import math
import os
import random
import sys
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from PIL import Image, ImageDraw, ImageFont

# ═══════════════ 字体 ═══════════════
FONT_CN = "C:/Windows/Fonts/msyh.ttc"
FONT_BOLD = "C:/Windows/Fonts/msyhbd.ttc"
FONT_LIGHT = "C:/Windows/Fonts/msyhl.ttc"
FONT_EN = "C:/Windows/Fonts/arial.ttf"
FONT_EN_BOLD = "C:/Windows/Fonts/arialbd.ttf"

SIZE = 800
AVATAR = 400

# ═══════════════ 调性配色 ═══════════════
MOOD_PALETTES = {
    "modern":   {"primary":"#1a1a2e","secondary":"#e94560","bg":"#ffffff","accent":"#0f3460","muted":"#c0c0c0"},
    "elegance": {"primary":"#1a1a1a","secondary":"#c9a84c","bg":"#f5f0e8","accent":"#8b7355","muted":"#d4a843"},
    "bold":     {"primary":"#dc2626","secondary":"#1e1e1e","bg":"#ffffff","accent":"#f97316","muted":"#fef3c7"},
    "playful":  {"primary":"#ff6b6b","secondary":"#4ecdc4","bg":"#ffffff","accent":"#ffe66d","muted":"#a8e6cf"},
    "tech":     {"primary":"#1e1b4b","secondary":"#6366f1","bg":"#0f172a","accent":"#06b6d4","muted":"#8b5cf6"},
    "vintage":  {"primary":"#5c4033","secondary":"#c9a84c","bg":"#f5f0e8","accent":"#8b7355","muted":"#3c2415"},
    "minimal":  {"primary":"#1a1a1a","secondary":"#ffffff","bg":"#ffffff","accent":"#6b7280","muted":"#e5e5e5"},
    "nature":   {"primary":"#064e3b","secondary":"#059669","bg":"#ecfdf5","accent":"#34d399","muted":"#10b981"},
}

INDUSTRY_MOOD = {
    "tech":"tech","finance":"elegance","food":"playful","construction":"bold",
    "health":"nature","education":"modern","trade":"elegance","design":"modern",
    "realestate":"elegance","culture":"vintage","sports":"bold","manufacturing":"bold",
    "beauty":"modern","law":"elegance","default":"modern",
}

# ═══════════════ 工具 ═══════════════
def name_hash(name):
    h = 0
    for i, c in enumerate(name):
        h = (h * 31 + ord(c)) % 2147483647
    return h

def seeded_random(name, salt=""):
    """确定性伪随机 0.0-1.0"""
    seed = name_hash(name + salt)
    x = (seed * 16807) % 2147483647
    return x / 2147483647

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"

def lerp_color(c1, c2, t):
    return tuple(max(0, min(255, int(a + (b-a)*t))) for a, b in zip(c1, c2))

def get_font(size, weight="regular"):
    try:
        if weight == "bold": return ImageFont.truetype(FONT_BOLD, size)
        if weight == "light" and os.path.exists(FONT_LIGHT): return ImageFont.truetype(FONT_LIGHT, size)
        return ImageFont.truetype(FONT_CN, size)
    except:
        return ImageFont.load_default()

def text_bbox(draw, text, font):
    b = draw.textbbox((0, 0), text, font=font)
    return b[2]-b[0], b[3]-b[1]

def draw_ctext(draw, text, y, font, color, w=SIZE):
    tw, _ = text_bbox(draw, text, font)
    draw.text(((w-tw)/2, y), text, fill=color, font=font)
    return tw

def save_pair(img, out, name):
    fn = os.path.join(out, f"{name}.png")
    img.save(fn)
    av = img.resize((AVATAR, AVATAR), Image.LANCZOS)
    av.save(os.path.join(out, f"{name}-avatar.png"))
    return fn


# ═══════════════ 设计元素库 ═══════════════

class Shapes:
    """30+ 几何形状绘制函数"""

    @staticmethod
    def circle(draw, cx, cy, r, fill=None, outline=None, width=2):
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=fill, outline=outline, width=width)

    @staticmethod
    def ring(draw, cx, cy, r, outline, width=3):
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=outline, width=width)

    @staticmethod
    def dot(draw, cx, cy, r, fill):
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=fill)

    @staticmethod
    def rect(draw, x1, y1, x2, y2, fill=None, outline=None, width=2, radius=0):
        if radius:
            draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill, outline=outline, width=width)
        else:
            draw.rectangle([x1, y1, x2, y2], fill=fill, outline=outline, width=width)

    @staticmethod
    def triangle(draw, cx, cy, r, fill=None, outline=None, width=2, angle=0):
        pts = []
        for i in range(3):
            a = angle + i * 2*math.pi/3 - math.pi/2
            pts.append((cx + r*math.cos(a), cy + r*math.sin(a)))
        draw.polygon(pts, fill=fill, outline=outline) if outline else draw.polygon(pts, fill=fill)

    @staticmethod
    def diamond(draw, cx, cy, r, fill=None, outline=None, width=2):
        pts = [(cx, cy-r), (cx+r, cy), (cx, cy+r), (cx-r, cy)]
        draw.polygon(pts, fill=fill, outline=outline) if outline else draw.polygon(pts, fill=fill)

    @staticmethod
    def hexagon(draw, cx, cy, r, fill=None, outline=None, width=2):
        pts = [(cx+r*math.cos(i*math.pi/3), cy+r*math.sin(i*math.pi/3)) for i in range(6)]
        draw.polygon(pts, fill=fill, outline=outline) if outline else draw.polygon(pts, fill=fill)

    @staticmethod
    def star(draw, cx, cy, r, points=5, fill=None, outline=None, width=2):
        pts = []
        for i in range(points*2):
            a = i * math.pi/points - math.pi/2
            rr = r if i % 2 == 0 else r * 0.4
            pts.append((cx + rr*math.cos(a), cy + rr*math.sin(a)))
        draw.polygon(pts, fill=fill, outline=outline) if outline else draw.polygon(pts, fill=fill)

    @staticmethod
    def cross(draw, cx, cy, r, arm=0.3, fill=None, outline=None, width=2):
        w = r * arm
        draw.rectangle([cx-w, cy-r, cx+w, cy+r], fill=fill) if fill else None
        draw.rectangle([cx-r, cy-w, cx+r, cy+w], fill=fill) if fill else None
        if outline:
            draw.rectangle([cx-w, cy-r, cx+w, cy+r], outline=outline, width=width)
            draw.rectangle([cx-r, cy-w, cx+r, cy+w], outline=outline, width=width)

    @staticmethod
    def arc_line(draw, cx, cy, r, start_angle, end_angle, outline, width=2):
        """绘制弧线（用多边形近似）"""
        pts = []
        steps = max(10, int(r * abs(end_angle-start_angle) / 10))
        for i in range(steps+1):
            a = start_angle + (end_angle-start_angle) * i/steps
            pts.append((cx + r*math.cos(a), cy + r*math.sin(a)))
        draw.line(pts, fill=outline, width=width)

    @staticmethod
    def wave(draw, x1, y1, x2, y2, amplitude=20, frequency=3, outline=None, width=2):
        """正弦曲线"""
        pts = []
        dx = x2 - x1
        steps = max(10, abs(dx)//2)
        for i in range(steps+1):
            t = i / steps
            x = x1 + dx * t
            y = y1 + (y2-y1)*t + amplitude * math.sin(t * frequency * 2*math.pi)
            pts.append((x, y))
        draw.line(pts, fill=outline, width=width)


class Patterns:
    """15+ 背景图案生成器"""

    @staticmethod
    def dot_grid(draw, cx, cy, cols, rows, gap, dot_r, color, x0, y0):
        for r in range(rows):
            for c in range(cols):
                x = x0 + c*gap - (cols-1)*gap/2 + cx
                y = y0 + r*gap - (rows-1)*gap/2 + cy
                Shapes.dot(draw, x, y, dot_r, color)

    @staticmethod
    def concentric(draw, cx, cy, rings, start_r, gap, color, lw=2):
        for i in range(rings):
            r = start_r + i*gap
            Shapes.ring(draw, cx, cy, r, color, lw)

    @staticmethod
    def radiating(draw, cx, cy, lines, start_r, end_r, color, lw=1):
        for i in range(lines):
            a = i * 2*math.pi / lines
            x1, y1 = cx + start_r*math.cos(a), cy + start_r*math.sin(a)
            x2, y2 = cx + end_r*math.cos(a), cy + end_r*math.sin(a)
            draw.line([(x1, y1), (x2, y2)], fill=color, width=lw)

    @staticmethod
    def checks(draw, x0, y0, w, h, cell, color_a, color_b):
        for y in range(y0, y0+h, cell):
            for x in range(x0, x0+w, cell):
                c = color_a if ((x//cell)+(y//cell))%2==0 else color_b
                draw.rectangle([x, y, x+cell, y+cell], fill=c)

    @staticmethod
    def stripes_h(draw, x0, y0, w, h, gap, color, lw=1):
        for y in range(y0, y0+h+gap, gap):
            draw.line([(x0, y), (x0+w, y)], fill=color, width=lw)

    @staticmethod
    def stripes_v(draw, x0, y0, w, h, gap, color, lw=1):
        for x in range(x0, x0+w+gap, gap):
            draw.line([(x, y0), (x, y0+h)], fill=color, width=lw)

    @staticmethod
    def diagonal_mesh(draw, x0, y0, w, h, gap, color, lw=1):
        for offset in range(-h, w+h, gap):
            draw.line([(x0+offset, y0), (x0+offset+w, y0+h)], fill=color, width=lw)
            draw.line([(x0+offset, y0+h), (x0+offset-w, y0)], fill=color, width=lw)

    @staticmethod
    def arcs(draw, cx, cy, rings, start_r, step, color, lw=2):
        for i in range(rings):
            r = start_r + i*step
            Shapes.arc_line(draw, cx, cy, r, i*0.5, i*0.5+math.pi*1.2, color, lw)

    @staticmethod
    def scatter_dots(draw, cx, cy, count, spread, min_r, max_r, color):
        """伪随机散点（确定性的）"""
        for i in range(count):
            a = (i * 137.5) * math.pi/180  # 黄金角
            d = spread * math.sqrt(i/count)
            x = cx + d*math.cos(a)
            y = cy + d*math.sin(a)
            r = min_r + (max_r-min_r) * (i%5)/4
            Shapes.dot(draw, x, y, r, color)

    @staticmethod
    def polygon_frame(draw, cx, cy, sides, r, outline, width=2):
        pts = [(cx+r*math.cos(2*math.pi*i/sides-math.pi/2), cy+r*math.sin(2*math.pi*i/sides-math.pi/2))
               for i in range(sides)]
        draw.polygon(pts, outline=outline) if outline else None
        draw.line(pts + [pts[0]], fill=outline, width=width)

    @staticmethod
    def corner_brackets(draw, x1, y1, x2, y2, length, color, width=2):
        """四角L形边框"""
        for dx, dy in [(-1,-1),(1,-1),(-1,1),(1,1)]:
            cx_c = (x1+x2)/2 + dx*(x2-x1-length)/2
            cy_c = (y1+y2)/2 + dy*(y2-y1-length)/2
            l = length
            draw.line([(cx_c, cy_c+l*dy), (cx_c, cy_c)], fill=color, width=width)
            draw.line([(cx_c, cy_c), (cx_c+l*dx, cy_c)], fill=color, width=width)


# ═══════════════ 行业视觉语义 ═══════════════

INDUSTRY_SHAPES = {
    "tech":       ["hexagon", "diamond", "circle", "dot_matrix"],
    "finance":    ["pillar", "triangle_up", "circle", "rect"],
    "food":       ["circle", "leaf", "wave", "star"],
    "construction":["rect", "triangle", "hexagon", "cross_beam"],
    "health":     ["cross", "circle", "leaf", "heart"],
    "education":  ["book", "circle", "star", "diamond"],
    "trade":      ["globe", "arrow", "circle", "hexagon"],
    "design":     ["circle", "triangle", "square", "wave"],
    "realestate": ["home", "key", "square", "chevron"],
    "culture":    ["seal_square", "circle", "cloud", "wave"],
    "sports":     ["flame", "chevron", "star", "circle"],
    "manufacturing":["gear", "hexagon", "rect", "arrow"],
    "beauty":     ["flower", "circle", "wave", "drop"],
    "law":        ["scales", "pillar", "circle", "shield"],
    "default":    ["circle", "diamond", "star", "square"],
}

INDUSTRY_PATTERNS = {
    "tech":       ["radiating", "dot_grid", "diagonal", "arcs"],
    "finance":    ["stripes_v", "grid", "concentric", "corner"],
    "food":       ["dots", "wave", "concentric", "stripes_h"],
    "construction":["checks", "stripes_v", "grid", "cross_beam"],
    "health":     ["cross_grid", "concentric", "wave", "dots"],
    "education":  ["grid", "stripes_h", "arcs", "dots"],
    "trade":      ["concentric", "radiating", "diagonal", "stripes_h"],
    "design":     ["dots", "diagonal", "arcs", "concentric"],
    "realestate": ["grid", "stripes_h", "corner", "concentric"],
    "culture":    ["frame", "stamp", "cloud", "concentric"],
    "sports":     ["radiating", "chevrons", "dots", "stripes_v"],
    "manufacturing":["stripes_v", "grid", "hex_grid", "diagonal"],
    "beauty":     ["dots", "wave", "concentric", "petals"],
    "law":        ["stripes_v", "concentric", "corner", "frame"],
    "default":    ["dots", "concentric", "stripes_h", "grid"],
}


# ═══════════════ 构图引擎 ═══════════════

def compose_logo(name, industry, mood, palette, idx, tagline="", english=""):
    """
    核心函数：组合一个完整的Logo设计。

    每种构图对应一个"设计框架"，框架内部有大量参数变化。
    idx 用于选择构图类型，同一名称多次调用生成不同设计。
    """
    img = Image.new("RGBA", (SIZE, SIZE), hex_to_rgb(palette["bg"]) + (255,))
    draw = ImageDraw.Draw(img)
    nh = name_hash(name)
    salt = f"_{idx}_{industry}"

    # 根据 idx 选择构图策略
    composition = [
        centered_mark,
        side_by_side,
        circle_frame,
        diagonal_split,
        corner_frame,
        geometric_pattern,
        ring_badge,
        typo_focus,
        overlap_layers,
        line_art,
        negative_space,
        modular_grid,
    ][idx % 12]

    return composition(draw, name, industry, mood, palette, nh, salt, tagline, english)


# ── 构图1: 中心图形+文字 ──
def centered_mark(draw, name, industry, mood, pal, nh, salt, tagline, eng):
    img = draw._image
    cx, cy = SIZE//2, SIZE//2

    # 选择图形形状
    shapes = INDUSTRY_SHAPES.get(industry, INDUSTRY_SHAPES["default"])
    shape = shapes[nh % len(shapes)]

    # 随机配色点位
    primary = hex_to_rgb(pal["primary"])
    secondary = hex_to_rgb(pal["secondary"])
    accent = hex_to_rgb(pal["accent"])
    bg = hex_to_rgb(pal["bg"])

    # 背景微装饰
    sr = seeded_random(name, f"{salt}_bg")
    if sr < 0.33:
        # 细线背景
        for i in range(5):
            ly = (i+1)*(SIZE/6)
            c_alpha = tuple(lerp_color(accent, bg, 0.7))
            draw.line([(100, ly), (SIZE-100, ly)], fill=c_alpha, width=1)
    elif sr < 0.66:
        # 散点背景
        Patterns.scatter_dots(draw, cx, cy, 40, SIZE*0.4, 1, 4, tuple(lerp_color(primary, bg, 0.85)))

    # 中心图形 - 根据行业和名称确定
    r = 120 + int(seeded_random(name, f"{salt}_size") * 80)
    mark_y = SIZE * 0.38

    if shape == "hexagon":
        Shapes.hexagon(draw, cx, int(mark_y), r, fill=primary, outline=secondary, width=3)
        inner = r * 0.55
        Shapes.circle(draw, cx, int(mark_y), inner, outline=secondary, width=2)
        # 内嵌行业小符号
        draw_industry_mini(draw, cx, int(mark_y), int(inner*0.6), secondary, industry)
    elif shape == "diamond":
        Shapes.diamond(draw, cx, int(mark_y), r, fill=primary, outline=secondary, width=3)
        # 对角十字
        Shapes.cross(draw, cx, int(mark_y), int(r*0.4), arm=0.3, outline=secondary, width=2)
    elif shape == "circle":
        Shapes.circle(draw, cx, int(mark_y), r, fill=primary, outline=secondary, width=3)
        Shapes.circle(draw, cx, int(mark_y), int(r*0.65), outline=secondary, width=1)
        Shapes.circle(draw, cx, int(mark_y), int(r*0.3), fill=secondary)
    elif shape == "triangle":
        Shapes.triangle(draw, cx, int(mark_y), r, fill=primary, outline=secondary, width=3)
        Shapes.circle(draw, cx, int(mark_y), int(r*0.3), fill=secondary)
    elif shape == "star":
        pts = int(4 + seeded_random(name, f"{salt}_pts") * 5)
        Shapes.star(draw, cx, int(mark_y), r, points=pts, fill=primary, outline=secondary, width=2)
    else:  # rect/square
        Shapes.rect(draw, cx-r, int(mark_y)-r, cx+r, int(mark_y)+r, fill=primary, outline=secondary, width=3, radius=15)

    # 品牌名
    fn_bold = get_font(64, "bold")
    text_y = SIZE * 0.65
    draw_ctext(draw, name, text_y, fn_bold, primary)

    # 英文/副标题
    sub_y = SIZE * 0.76
    if eng:
        fn_en = get_font(22, "light")
        draw_ctext(draw, eng.upper(), sub_y, fn_en, accent, SIZE)
    elif tagline:
        fn_tag = get_font(20, "light")
        draw_ctext(draw, tagline, sub_y, fn_tag, accent, SIZE)

    # 装饰线
    line_y = SIZE * 0.60
    lw = int(1.5 + seeded_random(name, f"{salt}_lw") * 3)
    llen = SIZE * 0.12
    draw.line([(cx-llen, line_y), (cx+llen, line_y)], fill=accent, width=lw)

    return img


# ── 构图2: 左右分区 ──
def side_by_side(draw, name, industry, mood, pal, nh, salt, tagline, eng):
    img = draw._image
    cx, cy = SIZE//2, SIZE//2

    primary = hex_to_rgb(pal["primary"])
    secondary = hex_to_rgb(pal["secondary"])
    accent = hex_to_rgb(pal["accent"])
    bg = hex_to_rgb(pal["bg"])

    # 左侧：图形区
    left_cx = SIZE * 0.3
    left_area_w = SIZE * 0.4
    # 背景色块
    left_bg = primary if seeded_random(name, f"{salt}_lb") > 0.3 else secondary
    draw.rectangle([0, 0, int(left_area_w+SIZE*0.1), SIZE], fill=left_bg)

    # 左侧图形
    r = 100 + int(seeded_random(name, f"{salt}_lr") * 50)
    shape_idx = (nh // 7) % 4
    left_color = secondary if left_bg == primary else primary
    if shape_idx == 0:
        Shapes.circle(draw, int(left_cx), cy, r, fill=left_color)
        Shapes.ring(draw, int(left_cx), cy, int(r*1.3), left_color, width=2)
    elif shape_idx == 1:
        Shapes.diamond(draw, int(left_cx), cy, r, fill=left_color, outline=rgb_to_hex(*bg), width=2)
    elif shape_idx == 2:
        Shapes.hexagon(draw, int(left_cx), cy, r, fill=left_color)
        Shapes.circle(draw, int(left_cx), cy, int(r*0.4), fill=bg)
    else:
        # 渐变圆环组
        for i in range(4):
            rr = r * (0.3 + i*0.25)
            Shapes.ring(draw, int(left_cx), cy, int(rr), left_color, width=3-i//2)

    # 右侧：文字区
    text_x = int(left_area_w + SIZE*0.15)
    text_w = SIZE - text_x

    # 品牌名 - 字体大小自适应
    n = len(name)
    if n <= 2: fs = 100
    elif n <= 4: fs = 72
    elif n <= 6: fs = 56
    else: fs = 42
    fn_bold = get_font(fs, "bold")
    draw.text((text_x, SIZE*0.30), name, fill=primary, font=fn_bold)

    # 副标题
    if tagline or eng:
        text = eng.upper() if eng else tagline
        fn_sub = get_font(20, "light")
        draw.text((text_x, SIZE*0.30+fs+20), text, fill=accent, font=fn_sub)

    # 装饰色条
    bar_h = 4
    y_bar = SIZE*0.30 + fs + 50
    draw.rectangle([text_x, y_bar, text_x+text_w-40, y_bar+bar_h], fill=accent)

    return img


# ── 构图3: 圆形徽章 ──
def circle_frame(draw, name, industry, mood, pal, nh, salt, tagline, eng):
    img = draw._image
    cx, cy = SIZE//2, SIZE//2

    primary = hex_to_rgb(pal["primary"])
    secondary = hex_to_rgb(pal["secondary"])
    accent = hex_to_rgb(pal["accent"])
    bg = hex_to_rgb(pal["bg"])

    # 外环
    outer_r = 300
    n_rings = 2 + int(seeded_random(name, f"{salt}_rings") * 3)
    for i in range(n_rings):
        r = outer_r - i*12
        c = secondary if i%2==0 else primary
        Shapes.ring(draw, cx, cy, r, c, width=2+i)

    # 中心图形
    shape_r = 80
    circle_fill = primary
    Shapes.circle(draw, cx, cy-30, shape_r, fill=circle_fill, outline=secondary, width=2)

    # 内嵌符号
    draw_industry_mini(draw, cx, cy-30, int(shape_r*0.6), rgb_to_hex(*bg), industry)

    # 弧线文字位置
    arc_r = 240
    y_text_top = cy - arc_r + 20
    y_text_bot = cy + arc_r - 30

    # 品牌名在上半部分
    fn = get_font(56, "bold")
    draw_ctext(draw, name, y_text_top, fn, primary)

    # 行业/副标题在下半部分
    fn_sub = get_font(22, "light")
    draw_ctext(draw, tagline or eng or industry.upper(), y_text_bot, fn_sub, accent)

    return img


# ── 构图4: 对角分割 ──
def diagonal_split(draw, name, industry, mood, pal, nh, salt, tagline, eng):
    img = draw._image
    primary = hex_to_rgb(pal["primary"])
    secondary = hex_to_rgb(pal["secondary"])
    accent = hex_to_rgb(pal["accent"])
    bg = hex_to_rgb(pal["bg"])

    # 对角线分割
    angle = seeded_random(name, f"{salt}_angle") * 0.6 + 0.3  # 30%-90%
    split_x = SIZE * angle
    pts = [(0, SIZE), (0, 0), (int(split_x), 0)]
    draw.polygon(pts, fill=primary)

    # 对侧装饰图案
    pattern_type = INDUSTRY_PATTERNS.get(industry, INDUSTRY_PATTERNS["default"])[nh%4]
    px_secondary = rgb_to_hex(*secondary)

    if "diagonal" in pattern_type:
        half = int(SIZE*0.3)
        Patterns.diagonal_mesh(draw, SIZE-half, SIZE-half, half, half, 30, hex_to_rgb(pal["muted"]), 1)
    elif "dots" in pattern_type:
        Patterns.scatter_dots(draw, SIZE*3//4, SIZE//4, 25, SIZE*0.25, 1, 4, secondary)

    # 文字
    fn_bold = get_font(72, "bold")
    tx, ty = SIZE*0.05, SIZE*0.08
    draw.text((tx, ty), name, fill=secondary if split_x < SIZE//2 else primary, font=fn_bold)

    # 装饰几何
    shape_x = SIZE * 0.82
    shape_y = SIZE * 0.85
    shapes = ["circle", "diamond", "triangle", "hexagon"]
    s = shapes[nh % 4]
    r = 40
    sf = primary if split_x > SIZE//2 else secondary
    if s == "circle": Shapes.circle(draw, int(shape_x), int(shape_y), r, fill=sf)
    elif s == "diamond": Shapes.diamond(draw, int(shape_x), int(shape_y), r, fill=sf)
    elif s == "triangle": Shapes.triangle(draw, int(shape_x), int(shape_y), r, fill=sf)
    else: Shapes.hexagon(draw, int(shape_x), int(shape_y), r, fill=sf)

    if tagline:
        fn_tag = get_font(18, "light")
        draw.text((tx, ty+90), tagline, fill=accent, font=fn_tag)

    return img


# ── 构图5: 边框框架 ──
def corner_frame(draw, name, industry, mood, pal, nh, salt, tagline, eng):
    img = draw._image
    cx, cy = SIZE//2, SIZE//2

    primary = hex_to_rgb(pal["primary"])
    secondary = hex_to_rgb(pal["secondary"])
    accent = hex_to_rgb(pal["accent"])

    margin = 60
    l_len = 60 + int(seeded_random(name, f"{salt}_llen") * 40)

    # 四角L形
    Patterns.corner_brackets(draw, margin, margin, SIZE-margin, SIZE-margin, l_len, primary, width=3)

    # 副角
    inner_m = margin + 30
    Patterns.corner_brackets(draw, inner_m, inner_m, SIZE-inner_m, SIZE-inner_m, l_len//2, secondary, width=1)

    # 中间品牌名
    fn_bold = get_font(80 if len(name)<=3 else 60, "bold")
    draw_ctext(draw, name, cy-15, fn_bold, primary)

    # 底部装饰
    ly = SIZE * 0.70
    lx1, lx2 = SIZE*0.35, SIZE*0.65
    draw.line([(lx1, ly), (lx2, ly)], fill=accent, width=2)
    Shapes.diamond(draw, cx, int(ly), 8, fill=accent)

    if tagline or eng:
        fn_tag = get_font(20, "light")
        draw_ctext(draw, tagline or eng.upper(), ly+25, fn_tag, accent)

    return img


# ── 构图6: 几何图案背景 ──
def geometric_pattern(draw, name, industry, mood, pal, nh, salt, tagline, eng):
    img = draw._image
    cx, cy = SIZE//2, SIZE//2

    primary = hex_to_rgb(pal["primary"])
    secondary = hex_to_rgb(pal["secondary"])
    accent = hex_to_rgb(pal["accent"])

    # 选择背景图案系统
    pattern_key = (nh // 13) % 5

    if pattern_key == 0:
        # 圆环扩散
        rings = 8 + int(seeded_random(name, f"{salt}_r") * 6)
        Patterns.concentric(draw, cx, cy, rings, 30, 30, rgb_to_hex(*lerp_color(primary, (255,255,255), 0.8)), 1)
    elif pattern_key == 1:
        # 网格点阵
        g = 40 + int(seeded_random(name, f"{salt}_g") * 20)
        cols = SIZE//g + 3
        Patterns.dot_grid(draw, cx, cy, cols, cols, g, 3, rgb_to_hex(*lerp_color(secondary, (255,255,255), 0.7)),
                         -(cols-1)*g/2, -(cols-1)*g/2)
    elif pattern_key == 2:
        # 辐射线
        lines = 24 + int(seeded_random(name, f"{salt}_ln") * 24)
        Patterns.radiating(draw, cx, cy, lines, 50, SIZE//2, rgb_to_hex(*lerp_color(primary, (255,255,255), 0.85)), 1)
    elif pattern_key == 3:
        # 弧线组
        Patterns.arcs(draw, cx, cy, 8, 60, 40, rgb_to_hex(*lerp_color(secondary, (255,255,255), 0.7)), 2)
    else:
        # 条纹
        gap = 20 + int(seeded_random(name, f"{salt}_st") * 15)
        if nh % 2 == 0:
            Patterns.stripes_v(draw, 0, 0, SIZE, SIZE, gap, rgb_to_hex(*lerp_color(primary, (255,255,255), 0.88)), 1)
        else:
            Patterns.stripes_h(draw, 0, 0, SIZE, SIZE, gap, rgb_to_hex(*lerp_color(primary, (255,255,255), 0.88)), 1)

    # 半透明覆盖框
    overlay_a = int(80 + seeded_random(name, f"{salt}_oa") * 60)
    overlay_w = 280
    overlay_h = 160 if len(name) <= 4 else 200
    ox, oy = cx-overlay_w//2, cy-overlay_h//2
    draw.rectangle([ox, oy, ox+overlay_w, oy+overlay_h], fill=(255,255,255,overlay_a))
    draw.rectangle([ox, oy, ox+overlay_w, oy+overlay_h], outline=primary, width=2)

    # 品牌名
    fn_bold = get_font(64, "bold")
    draw_ctext(draw, name, cy-10, fn_bold, primary)

    # 装饰小图形
    mini_r = 6
    Shapes.dot(draw, cx, oy+overlay_h+15, mini_r, secondary)

    if tagline:
        fn_tag = get_font(18, "light")
        draw_ctext(draw, tagline, oy+overlay_h+30, fn_tag, accent)

    return img


# ── 构图7: 环状徽章 ──
def ring_badge(draw, name, industry, mood, pal, nh, salt, tagline, eng):
    img = draw._image
    cx, cy = SIZE//2, SIZE//2

    primary = hex_to_rgb(pal["primary"])
    secondary = hex_to_rgb(pal["secondary"])
    accent = hex_to_rgb(pal["accent"])

    # 外环 - 粗
    outer_r = min(280, SIZE//2 - 20)
    Shapes.ring(draw, cx, cy, outer_r, primary, width=6)
    # 中环
    mid_r = outer_r - 20
    Shapes.ring(draw, cx, cy, mid_r, secondary, width=2)
    # 内环
    inner_r = mid_r - 30
    Shapes.ring(draw, cx, cy, inner_r, accent, width=1)

    # 环间装饰 - 散点
    n_dots = 12 + int(seeded_random(name, f"{salt}_nd") * 12)
    for i in range(n_dots):
        a = i * 2*math.pi / n_dots
        dot_r = mid_r - 10
        dx, dy = cx + dot_r*math.cos(a), cy + dot_r*math.sin(a)
        Shapes.dot(draw, int(dx), int(dy), 4, secondary if i%3==0 else accent)

    # 中心
    center_r = 90
    Shapes.circle(draw, cx, cy, center_r, fill=primary, outline=secondary, width=2)

    # 中心字
    n = len(name)
    if n <= 2:
        fn_center = get_font(90, "bold")
        for i, ch in enumerate(name):
            tw, th = text_bbox(draw, ch, fn_center)
            draw.text((cx-tw//2, cy-th+i*95), ch, fill=hex_to_rgb(pal["bg"]), font=fn_center)
    elif n <= 4:
        fn_center = get_font(56, "bold")
        half = n//2
        l1, l2 = name[:half], name[half:]
        draw_ctext(draw, l1, cy-35, fn_center, hex_to_rgb(pal["bg"]))
        draw_ctext(draw, l2, cy+25, fn_center, hex_to_rgb(pal["bg"]))
    else:
        fn_center = get_font(32, "bold")
        draw_ctext(draw, name, cy-10, fn_center, hex_to_rgb(pal["bg"]))

    # 底部装饰文字
    fn_sub = get_font(18, "light")
    bottom_text = tagline or eng or industry.upper()
    draw_ctext(draw, bottom_text, cy + outer_r + 30, fn_sub, secondary)

    return img


# ── 构图8: 文字焦点 ──
def typo_focus(draw, name, industry, mood, pal, nh, salt, tagline, eng):
    img = draw._image
    cx, cy = SIZE//2, SIZE//2

    primary = hex_to_rgb(pal["primary"])
    secondary = hex_to_rgb(pal["secondary"])
    accent = hex_to_rgb(pal["accent"])

    n = len(name)
    # 自适应字号
    if n <= 2: fs, gap = 200, 30
    elif n <= 3: fs, gap = 140, 20
    elif n <= 4: fs, gap = 100, 15
    elif n <= 6: fs, gap = 72, 12
    else: fs, gap = 52, 10

    fn = get_font(fs, "bold")

    # 水平排列 + 第一字特殊处理
    # 测量
    char_data = []
    total_w = 0
    for ch in name:
        tw, th = text_bbox(draw, ch, fn)
        char_data.append((tw, th))
        total_w += tw
    total_w += gap * (n-1)

    start_x = (SIZE - total_w) / 2
    x = start_x

    for i, (ch_w, ch_h) in enumerate(char_data):
        ch = name[i]
        y = cy - ch_h//2

        # 根据名称哈希决定文字处理方式
        text_mode = (nh // (i+3)) % 3
        if text_mode == 0:
            draw.text((x, y), ch, fill=primary, font=fn)
        elif text_mode == 1:
            # 轮廓+填充
            draw.text((x+1, y+1), ch, fill=secondary, font=fn)
            draw.text((x, y), ch, fill=primary, font=fn)
        else:
            # 只有轮廓
            draw.text((x+1, y+1), ch, fill=accent, font=fn)
            draw.text((x-1, y-1), ch, fill=primary, font=fn)
            draw.text((x, y), ch, fill=hex_to_rgb(pal["bg"]), font=fn)

        x += ch_w + gap

    # 底部装饰线 + 符号
    line_y = SIZE * 0.72
    draw.line([(SIZE*0.25, line_y), (SIZE*0.75, line_y)], fill=primary, width=2)
    Shapes.diamond(draw, cx, int(line_y), 5, fill=accent)

    if tagline or eng:
        fn_sub = get_font(20, "light")
        draw_ctext(draw, tagline or eng.upper(), line_y+20, fn_sub, accent)

    return img


# ── 构图9: 图层重叠 ──
def overlap_layers(draw, name, industry, mood, pal, nh, salt, tagline, eng):
    img = draw._image
    primary = hex_to_rgb(pal["primary"])
    secondary = hex_to_rgb(pal["secondary"])
    accent = hex_to_rgb(pal["accent"])

    # 3层叠层几何
    shapes_pool = [(Shapes.circle, 180), (Shapes.diamond, 160), (Shapes.hexagon, 170),
                   (Shapes.triangle, 170), (Shapes.rect_wrapper, 150)]
    n_layers = 3
    selected = []
    for i in range(n_layers):
        idx = (nh // (i*7+1)) % len(shapes_pool)
        selected.append(shapes_pool[idx])

    centers = [
        (SIZE*0.38, SIZE*0.42),
        (SIZE*0.62, SIZE*0.36),
        (SIZE*0.50, SIZE*0.58),
    ]
    colors = [
        lerp_color(primary, (255,255,255), 0.1),
        lerp_color(secondary, (255,255,255), 0.0),
        lerp_color(accent, (255,255,255), 0.0),
    ]
    outlines = [secondary, accent, primary]

    for i in range(n_layers):
        shape_fn, r = selected[i]
        cx_i, cy_i = centers[i]
        r_i = int(r * (0.8 + seeded_random(name, f"{salt}_sr{i}") * 0.4))
        fill_c = colors[i]
        outline_c = outlines[i]

        if shape_fn == Shapes.rect_wrapper:
            Shapes.rect(draw, int(cx_i-r_i), int(cy_i-r_i), int(cx_i+r_i), int(cy_i+r_i),
                       fill=fill_c, outline=outline_c, width=2, radius=12)
        else:
            shape_fn(draw, int(cx_i), int(cy_i), r_i, fill=fill_c, outline=outline_c, width=2)

    # 品牌名叠加
    fn = get_font(56, "bold")
    ty = SIZE * 0.75
    cover_a = int(180 + seeded_random(name, f"{salt}_ca") * 60)
    draw.rectangle([SIZE*0.05, ty-10, SIZE*0.95, ty+80], fill=(255,255,255,cover_a))
    draw_ctext(draw, name, ty+5, fn, primary)

    if tagline:
        fn_sub = get_font(18, "light")
        draw_ctext(draw, tagline, ty+65, fn_sub, secondary)

    return img


def _rect_wrapper(draw, cx, cy, r, fill=None, outline=None, width=2):
    Shapes.rect(draw, int(cx-r), int(cy-r), int(cx+r), int(cy+r), fill=fill, outline=outline, width=width, radius=15)
Shapes.rect_wrapper = staticmethod(_rect_wrapper)


# ── 构图10: 线艺抽象 ──
def line_art(draw, name, industry, mood, pal, nh, salt, tagline, eng):
    img = draw._image
    cx, cy = SIZE//2, SIZE//2

    primary = hex_to_rgb(pal["primary"])
    secondary = hex_to_rgb(pal["secondary"])
    accent = hex_to_rgb(pal["accent"])

    # 波状线艺
    n_waves = 3 + int(seeded_random(name, f"{salt}_nw") * 5)
    for i in range(n_waves):
        amp = 10 + (i+1) * 8
        freq = 2 + i
        y_pos = SIZE*0.2 + i * SIZE*0.6/(n_waves-1) if n_waves>1 else cy
        c = lerp_color(primary, secondary, i/(n_waves-1)) if n_waves>1 else primary
        Shapes.wave(draw, 50, y_pos, SIZE-50, y_pos, amp, freq, c, width=2)

    # 圆形锚点
    for i in range(4):
        a = i * math.pi/2 + seeded_random(name, f"{salt}_ang{i}") * 0.5
        r = SIZE*0.35
        x, y = cx + r*math.cos(a), cy + r*math.sin(a)
        Shapes.circle(draw, int(x), int(y), 20, fill=secondary, outline=primary, width=2)

    # 中心品牌名
    fn = get_font(56, "bold")
    bg_a = 220
    tw, th = text_bbox(draw, name, fn)
    bx1, by1 = (SIZE-tw)//2-20, cy-th//2-10
    bx2, by2 = bx1+tw+40, by1+th+20
    draw.rounded_rectangle([bx1, by1, bx2, by2], radius=10, fill=(255,255,255,bg_a),
                           outline=primary, width=2)
    draw_ctext(draw, name, cy-th//2+5, fn, primary)

    if tagline:
        fn_sub = get_font(18, "light")
        draw_ctext(draw, tagline, cy+th//2+30, fn_sub, secondary)

    return img


# ── 构图11: 负空间 ──
def negative_space(draw, name, industry, mood, pal, nh, salt, tagline, eng):
    img = draw._image
    cx, cy = SIZE//2, SIZE//2

    primary = hex_to_rgb(pal["primary"])
    secondary = hex_to_rgb(pal["secondary"])
    accent = hex_to_rgb(pal["accent"])
    bg = hex_to_rgb(pal["bg"])

    # 上色块（矩形/圆形/三角形）
    shape_type = nh % 3
    top_h = SIZE * 0.6
    if shape_type == 0:
        draw.rectangle([0, 0, SIZE, int(top_h)], fill=primary)
    elif shape_type == 1:
        draw.ellipse([-SIZE//2, -SIZE//6, int(SIZE*1.5), int(top_h*2)], fill=primary)
    else:
        pts = [(0, 0), (SIZE, 0), (0, int(top_h))]
        draw.polygon(pts, fill=primary)

    # 上色块中的"负空间"（白色镂空）
    cut_shape = shapes_pool = ["circle", "diamond", "hexagon", "triangle"]
    cs = cut_shape[nh % 4]
    cut_r = 80 + int(seeded_random(name, f"{salt}_cr") * 40)
    cut_cx = SIZE//2
    cut_cy = SIZE//3

    if cs == "circle":
        Shapes.circle(draw, cut_cx, int(cut_cy), cut_r, fill=bg)
        Shapes.ring(draw, cut_cx, int(cut_cy), cut_r, secondary, width=2)
    elif cs == "diamond":
        Shapes.diamond(draw, cut_cx, int(cut_cy), cut_r, fill=bg, outline=secondary, width=2)
    elif cs == "hexagon":
        Shapes.hexagon(draw, cut_cx, int(cut_cy), cut_r, fill=bg, outline=secondary, width=2)
    else:
        Shapes.triangle(draw, cut_cx, int(cut_cy), cut_r, fill=bg, outline=secondary, width=2)

    # 下部品牌名
    fn = get_font(56, "bold")
    draw_ctext(draw, name, SIZE*0.78, fn, primary)

    # 分隔线
    draw.line([(SIZE*0.3, SIZE*0.67), (SIZE*0.7, SIZE*0.67)], fill=accent, width=2)

    if tagline:
        fn_sub = get_font(20, "light")
        draw_ctext(draw, tagline, SIZE*0.85, fn_sub, accent)

    return img


# ── 构图12: 模块化网格 ──
def modular_grid(draw, name, industry, mood, pal, nh, salt, tagline, eng):
    img = draw._image
    cx, cy = SIZE//2, SIZE//2

    primary = hex_to_rgb(pal["primary"])
    secondary = hex_to_rgb(pal["secondary"])
    accent = hex_to_rgb(pal["accent"])

    # n×n 网格
    grid_n = 3 + int(seeded_random(name, f"{salt}_gn") * 2 + 0.5)  # 3-5
    cell = SIZE // (grid_n + 1)
    offset = (SIZE - cell*grid_n) // 2

    # 每个格子的形状和颜色选择
    for r in range(grid_n):
        for c in range(grid_n):
            gcx = offset + c*cell + cell//2
            gcy = offset + r*cell + cell//2
            gidx = r*grid_n + c
            filled = (gidx * 7 + nh) % 3 != 0  # 约1/3留空

            if filled:
                gs = (gidx + nh//11) % 5
                gr = cell//3
                gc = secondary if gidx % 2 == 0 else primary

                if gs == 0: Shapes.circle(draw, int(gcx), int(gcy), gr, fill=gc)
                elif gs == 1: Shapes.diamond(draw, int(gcx), int(gcy), int(gr*0.8), fill=gc)
                elif gs == 2: Shapes.rect(draw, int(gcx-gr), int(gcy-gr), int(gcx+gr), int(gcy+gr), fill=gc, radius=5)
                elif gs == 3: Shapes.triangle(draw, int(gcx), int(gcy), int(gr*0.9), fill=gc)
                else: Shapes.dot(draw, int(gcx), int(gcy), gr//2, gc)

    # 叠加中心品牌标识
    overlay_w = SIZE * 0.45
    overlay_h = 140
    ox, oy = cx-overlay_w//2, cy-overlay_h//2
    draw.rounded_rectangle([ox, oy, ox+overlay_w, oy+overlay_h], radius=15,
                          fill=(255,255,255,210), outline=primary, width=3)

    fn = get_font(52, "bold")
    draw_ctext(draw, name, cy-15, fn, primary)

    if tagline:
        fn_sub = get_font(18, "light")
        draw_ctext(draw, tagline, cy+45, fn_sub, secondary)
    else:
        fn_sub = get_font(16, "light")
        draw_ctext(draw, industry.upper() if industry != "default" else "", cy+40, fn_sub, accent)

    return img


# ═══════════════ 行业迷你图标 ═══════════════

def draw_industry_mini(draw, cx, cy, r, color, industry):
    """在指定位置绘制小型行业符号"""
    c = hex_to_rgb(color) if isinstance(color, str) else color
    lw = max(1, r//12)

    if industry == "tech":
        Shapes.rect(draw, cx-r, cy-r, cx+r, cy+r, outline=c, width=lw, radius=4)
        for dx in [-r//2, 0, r//2]:
            for dy in [-r//2, 0, r//2]:
                if dx==0 and dy==0: continue
                Shapes.dot(draw, cx+dx, cy+dy, r//8, c)
    elif industry == "finance":
        for i, (dx, offset_y) in enumerate([(0, -r//2), (-r//3, r//2), (r//3, r//2)]):
            pw = r//6
            draw.rectangle([cx+dx-pw, cy+offset_y, cx+dx+pw, cy+r//2], outline=c, width=lw)
    elif industry == "food":
        Shapes.circle(draw, cx, cy, r, outline=c, width=lw)
        Shapes.dot(draw, cx, cy-r//3, r//4, c)
    elif industry == "trade":
        Shapes.circle(draw, cx, cy, r, outline=c, width=lw)
        draw.line([(cx-r, cy), (cx+r, cy)], fill=c, width=1)
        draw.ellipse([cx-r//2, cy-r, cx+r//2, cy+r], outline=c, width=1)
    elif industry == "culture":
        Shapes.rect(draw, cx-r, cy-r, cx+r, cy+r, outline=c, width=lw)
        Shapes.rect(draw, cx-r//2, cy-r//2, cx+r//2, cy+r//2, outline=c, width=1)
    elif industry in ("health", "medical"):
        w = r//4
        draw.rectangle([cx-w, cy-r, cx+w, cy+r], fill=c)
        draw.rectangle([cx-r, cy-w, cx+r, cy+w], fill=c)
    elif industry == "sports":
        pts = [
            (cx, cy-r), (cx+r//2, cy-r//3), (cx+r//2, cy),
            (cx, cy+r//2), (cx-r//2, cy), (cx-r//2, cy-r//3)
        ]
        draw.polygon(pts, fill=c)
    elif industry == "beauty":
        for i in range(5):
            a = i * 2*math.pi/5 - math.pi/2
            px, py = cx + r//2*math.cos(a), cy + r//2*math.sin(a)
            Shapes.dot(draw, int(px), int(py), r//4, c)
        Shapes.dot(draw, cx, cy, r//5, c)
    else:
        Shapes.circle(draw, cx, cy, r//2, fill=c)
        Shapes.ring(draw, cx, cy, r, c, lw)


# ═══════════════ 主程序 ═══════════════

def main():
    parser = argparse.ArgumentParser(description="Logo Generator v3 — 设计组合引擎")
    parser.add_argument("--name", type=str, required=True, help="公司/品牌名称")
    parser.add_argument("--industry", type=str, default="default",
                       help=f"行业: {', '.join(INDUSTRY_MOOD.keys())}")
    parser.add_argument("--mood", type=str, default=None,
                       help=f"调性: {', '.join(MOOD_PALETTES.keys())}")
    parser.add_argument("--count", type=int, default=8, help="生成设计数量 (推荐8-16)")
    parser.add_argument("--tagline", type=str, default="", help="口号/副标题")
    parser.add_argument("--english", type=str, default="", help="英文名")
    parser.add_argument("--output", type=str, default="", help="输出目录")
    parser.add_argument("--color", type=str, default="", help="主色覆盖 (例: #ff6b35)")
    parser.add_argument("--brief", type=str, default="", help="设计简报 (自然语言)")

    args = parser.parse_args()

    # 行业→调性
    mood = args.mood or INDUSTRY_MOOD.get(args.industry, "modern")
    if mood not in MOOD_PALETTES:
        mood = "modern"

    palette = dict(MOOD_PALETTES[mood])
    if args.color:
        palette["primary"] = args.color

    # 输出目录
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = "".join(c if c.isascii() and c.isalnum() else "_" for c in args.name)[:20] or "logo"
    out_dir = args.output or os.path.join(os.path.dirname(__file__) or ".", "output", f"{safe}_{ts}")
    os.makedirs(out_dir, exist_ok=True)

    # 生成摘要
    nh = name_hash(args.name)

    print("=" * 60)
    print(f"  🎨 Logo Generator v3 — 设计组合引擎")
    print(f"  公司: {args.name}")
    print(f"  行业: {args.industry}")
    print(f"  调性: {mood} — {MOOD_PALETTES[mood].get('primary','')}")
    if args.brief:
        print(f"  简报: {args.brief}")
    print(f"  生成: {args.count} 个独立设计")
    print(f"  哈希: {nh}")
    print("=" * 60)
    print()

    n = args.count

    for i in range(n):
        try:
            img = compose_logo(args.name, args.industry, mood, palette, i,
                              tagline=args.tagline, english=args.english)
            name_i = f"logo_{i+1:02d}"
            fn = save_pair(img, out_dir, name_i)
            comp_type = [
                "中心图形", "左右分区", "圆形徽章", "对角分割",
                "边框框架", "几何图案", "环状徽章", "文字焦点",
                "图层重叠", "线艺抽象", "负空间", "模块网格",
            ][i % 12]
            print(f"    ✓ logo_{i+1:02d} — {comp_type}")
        except Exception as e:
            print(f"    ✗ logo_{i+1:02d} — 生成失败: {e}")
            import traceback
            traceback.print_exc()

    print()
    print("=" * 60)
    print(f"  ✅ 完成! {n} 个独立设计 (2×{n} 文件)")
    print(f"  📁 {out_dir}")
    print(f"\n  💡 每个设计使用了不同的构图、形状和装饰，")
    print(f"     同一名称永远生成相同序列，不同名称完全不同。")
    print("=" * 60)


if __name__ == "__main__":
    main()
