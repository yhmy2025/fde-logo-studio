#!/usr/bin/env python3
"""
Logo Generator v4 — 多品类设计引擎
=====================================
从"一套模具12种排列"升级为"7个独立视觉品类"。

核心理念：
- 不是改变参数，而是改变整个视觉范式
- 名称哈希 → 选择品类 + 品类内参数 → 天差地别
- 7种品类：字标·字母标·图形标·抽象标·徽章标·组合标·负空间

用法:
  python generate.py --name "星辰科技" --industry tech --count 7
"""

import argparse, colorsys, math, os, random, sys, json, hashlib
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from PIL import Image, ImageDraw, ImageFont, ImageFilter

SIZE = 800
PAD = 60

# ═══════════════ 字体 ═══════════════

def _font_paths():
    """Retorna caminhos possíveis de fontes no sistema."""
    paths = {}
    if sys.platform == "win32":
        base = os.environ.get("WINDIR", "C:\\Windows")
        fd = os.path.join(base, "Fonts")
        paths["bold"] = os.path.join(fd, "simhei.ttf")
        paths["regular"] = os.path.join(fd, "simhei.ttf")
        paths["light"] = os.path.join(fd, "simhei.ttf")
        paths["serif"] = os.path.join(fd, "simsun.ttc")
        paths["mono"] = os.path.join(fd, "simsun.ttc")
    else:
        paths["bold"] = "/System/Library/Fonts/PingFang.ttc"
        paths["regular"] = "/System/Library/Fonts/PingFang.ttc"
        paths["light"] = "/System/Library/Fonts/PingFang.ttc"
        paths["serif"] = "/System/Library/Fonts/STSong.ttf"
        paths["mono"] = "/System/Library/Fonts/Menlo.ttc"
    # 后备
    for k, v in list(paths.items()):
        if not os.path.exists(v):
            try:
                paths[k] = ImageFont.load_default()
            except:
                pass
    return paths

FONT_PATHS = _font_paths()
FONT_CACHE = {}

def get_font(size, weight="bold"):
    key = (size, weight)
    if key in FONT_CACHE:
        return FONT_CACHE[key]
    path = FONT_PATHS.get(weight, FONT_PATHS["bold"])
    try:
        fn = ImageFont.truetype(path, size)
    except:
        fn = ImageFont.load_default()
    FONT_CACHE[key] = fn
    return fn

def text_bbox(draw, text, font):
    try:
        return draw.textbbox((0, 0), text, font=font)
    except:
        tw, th = draw.textsize(text, font=font)
        return (0, 0, tw, th)

def draw_ctext(draw, text, cy, font, color):
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
    except:
        tw, _ = draw.textsize(text, font=font)
    draw.text(((SIZE - tw) / 2, cy), text, fill=color, font=font)

# ═══════════════ 哈希 ═══════════════

def name_hash(name):
    d = hashlib.sha256(name.encode("utf-8")).digest()
    return int.from_bytes(d[:8], "big")

def seeded_choice(name, salt, items):
    h = name_hash(name + str(salt))
    return items[h % len(items)]

def seeded_shuffle(name, salt, items):
    lst = list(items)
    h = name_hash(name + str(salt))
    rng = random.Random(h)
    rng.shuffle(lst)
    return lst

# ═══════════════ 色彩 ═══════════════

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r, g, b):
    return f"#{max(0,min(255,int(r))):02x}{max(0,min(255,int(g))):02x}{max(0,min(255,int(b))):02x}"

def rgb_tuple(c):
    if isinstance(c, (tuple, list)):
        return tuple(int(x) for x in c[:3])
    return hex_to_rgb(c)

PALETTES = {
    "modern":   {"primary": "#2563eb", "secondary": "#3b82f6", "accent": "#f59e0b", "bg": "#f8fafc", "dark": "#1e293b"},
    "elegance": {"primary": "#1a1a2e", "secondary": "#16213e", "accent": "#c9a96e", "bg": "#f5f0eb", "dark": "#0f0f23"},
    "bold":     {"primary": "#dc2626", "secondary": "#ea580c", "accent": "#fbbf24", "bg": "#ffffff", "dark": "#1f1f1f"},
    "playful":  {"primary": "#ff6b6b", "secondary": "#ffa94d", "accent": "#ffd43b", "bg": "#fff4e6", "dark": "#2d3436"},
    "tech":     {"primary": "#0ea5e9", "secondary": "#06b6d4", "accent": "#22d3ee", "bg": "#0f172a", "dark": "#020617"},
    "vintage":  {"primary": "#5c4033", "secondary": "#8b6914", "accent": "#d4a853", "bg": "#faf3e0", "dark": "#3e2723"},
    "minimal":  {"primary": "#000000", "secondary": "#333333", "accent": "#999999", "bg": "#ffffff", "dark": "#000000"},
    "nature":   {"primary": "#15803d", "secondary": "#22c55e", "accent": "#a3e635", "bg": "#f0fdf4", "dark": "#064e3b"},
}

INDUSTRY_MOOD = {
    "tech": "tech", "finance": "modern", "food": "playful", "trade": "elegance",
    "construction": "bold", "health": "nature", "education": "modern",
    "design": "bold", "realestate": "elegance", "culture": "vintage",
    "sports": "bold", "manufacturing": "bold", "beauty": "playful", "law": "minimal",
}

# ═══════════════ 绘图工具箱 ═══════════════

class D:
    """Drawing utilities"""
    @staticmethod
    def circle(draw, cx, cy, r, fill=None, outline=None, width=1):
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=fill, outline=outline, width=width)

    @staticmethod
    def rect(draw, x1, y1, x2, y2, fill=None, outline=None, width=1, radius=0):
        if radius:
            draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill, outline=outline, width=width)
        else:
            draw.rectangle([x1, y1, x2, y2], fill=fill, outline=outline, width=width)

    @staticmethod
    def diamond(draw, cx, cy, r, fill=None, outline=None, width=1):
        pts = [(cx, cy-r), (cx+r, cy), (cx, cy+r), (cx-r, cy)]
        draw.polygon(pts, fill=fill, outline=outline)
        if outline:
            draw.line(pts + [pts[0]], fill=outline, width=width)

    @staticmethod
    def hexagon(draw, cx, cy, r, fill=None, outline=None, width=1):
        pts = [(cx+r*math.cos(2*math.pi*i/6-math.pi/6), cy+r*math.sin(2*math.pi*i/6-math.pi/6)) for i in range(6)]
        draw.polygon(pts, fill=fill, outline=outline)
        if outline:
            draw.line(pts + [pts[0]], fill=outline, width=width)

    @staticmethod
    def triangle(draw, cx, cy, r, fill=None, outline=None, width=1, angle=0):
        pts = [(cx+r*math.cos(2*math.pi*i/3-math.pi/2+angle), cy+r*math.sin(2*math.pi*i/3-math.pi/2+angle)) for i in range(3)]
        draw.polygon(pts, fill=fill, outline=outline)
        if outline:
            draw.line(pts + [pts[0]], fill=outline, width=width)

    @staticmethod
    def star(draw, cx, cy, r, points=5, fill=None, outline=None, width=1, inner_ratio=0.4):
        pts = []
        for i in range(points*2):
            a = 2*math.pi*i/(points*2) - math.pi/2
            rad = r if i%2==0 else r*inner_ratio
            pts.append((cx+rad*math.cos(a), cy+rad*math.sin(a)))
        draw.polygon(pts, fill=fill, outline=outline)
        if outline:
            draw.line(pts + [pts[0]], fill=outline, width=width)

    @staticmethod
    def ring(draw, cx, cy, r, color, width=2):
        D.circle(draw, cx, cy, r, outline=color, width=width)

    @staticmethod
    def dot(draw, x, y, r, color):
        D.circle(draw, int(x), int(y), r, fill=color)

    @staticmethod
    def cross(draw, cx, cy, size, color, width=2):
        draw.line([(cx-size, cy), (cx+size, cy)], fill=color, width=width)
        draw.line([(cx, cy-size), (cx, cy+size)], fill=color, width=width)

    @staticmethod
    def arc_line(draw, cx, cy, r, start_angle, end_angle, color, width=2):
        pts = []
        steps = max(20, int(r))
        for i in range(steps+1):
            a = start_angle + (end_angle-start_angle)*i/steps
            pts.append((cx+r*math.cos(a), cy+r*math.sin(a)))
        if len(pts) >= 2:
            draw.line(pts, fill=color, width=width)

    @staticmethod
    def polygon(draw, cx, cy, sides, r, fill=None, outline=None, width=1, rot=0):
        pts = [(cx+r*math.cos(2*math.pi*i/sides+rot), cy+r*math.sin(2*math.pi*i/sides+rot)) for i in range(sides)]
        draw.polygon(pts, fill=fill, outline=outline)
        if outline:
            draw.line(pts + [pts[0]], fill=outline, width=width)

    @staticmethod
    def wave(draw, cx, cy, w, amplitude, frequency, color, width=2):
        pts = []
        for i in range(101):
            x = cx - w/2 + w * i / 100
            y = cy + amplitude * math.sin(frequency * i / 100 * 2 * math.pi)
            pts.append((x, y))
        draw.line(pts, fill=color, width=width)


# ═══════════════ 行业专属图标 ═══════════════

def draw_industry_icon(draw, cx, cy, size, industry, palette, name=""):
    """绘制行业专属图标 - 7品类各不同"""
    c1 = hex_to_rgb(palette["primary"])
    c2 = hex_to_rgb(palette["secondary"])
    c3 = hex_to_rgb(palette["accent"])
    nh = name_hash(name) if name else 0

    icons = {
        "tech": lambda: _icon_tech(draw, cx, cy, size, c1, c2, c3, nh),
        "finance": lambda: _icon_finance(draw, cx, cy, size, c1, c2, c3, nh),
        "food": lambda: _icon_food(draw, cx, cy, size, c1, c2, c3, nh),
        "trade": lambda: _icon_trade(draw, cx, cy, size, c1, c2, c3, nh),
        "construction": lambda: _icon_build(draw, cx, cy, size, c1, c2, c3, nh),
        "health": lambda: _icon_health(draw, cx, cy, size, c1, c2, c3, nh),
        "education": lambda: _icon_edu(draw, cx, cy, size, c1, c2, c3, nh),
        "design": lambda: _icon_design(draw, cx, cy, size, c1, c2, c3, nh),
        "culture": lambda: _icon_culture(draw, cx, cy, size, c1, c2, c3, nh),
        "sports": lambda: _icon_sports(draw, cx, cy, size, c1, c2, c3, nh),
        "manufacturing": lambda: _icon_mfg(draw, cx, cy, size, c1, c2, c3, nh),
        "beauty": lambda: _icon_beauty(draw, cx, cy, size, c1, c2, c3, nh),
        "law": lambda: _icon_law(draw, cx, cy, size, c1, c2, c3, nh),
        "realestate": lambda: _icon_realestate(draw, cx, cy, size, c1, c2, c3, nh),
        "media": lambda: _icon_media(draw, cx, cy, size, c1, c2, c3, nh),
    }
    icons.get(industry, lambda: D.circle(draw, cx, cy, size, fill=c1))()


# ── 图标实现 ──

def _icon_tech(draw, cx, cy, s, c1, c2, c3, nh):
    mode = nh % 3
    if mode == 0:
        # 芯片
        D.rect(draw, cx-s, cy-s, cx+s, cy+s, outline=c1, width=2, radius=6)
        D.rect(draw, cx-s//2, cy-s//2, cx+s//2, cy+s//2, fill=c1, radius=3)
        for x in [cx-s//3, cx+s//3]:
            for y in [cy-s//3, cy+s//3]:
                D.dot(draw, x, y, max(2, s//10), c2)
    elif mode == 1:
        # 数据网络
        for i in range(6):
            a = 2*math.pi*i/6 - math.pi/2
            D.dot(draw, int(cx+s*math.cos(a)), int(cy+s*math.sin(a)), max(3, s//6), c1)
        for i in range(6):
            for j in range(i+1, 6):
                a1, a2 = 2*math.pi*i/6-math.pi/2, 2*math.pi*j/6-math.pi/2
                draw.line([(cx+s*math.cos(a1), cy+s*math.sin(a1)),
                           (cx+s*math.cos(a2), cy+s*math.sin(a2))], fill=c2, width=1)
    else:
        # 电路节点
        D.rect(draw, cx-s, cy-s, cx+s, cy+s, outline=c1, width=2, radius=4)
        for dx in [-s//2, 0, s//2]:
            for dy in [-s//2, 0, s//2]:
                if dx==0 and dy==0: D.dot(draw, cx, cy, s//3, c1)
                else: D.dot(draw, cx+dx, cy+dy, s//8, c2)

def _icon_finance(draw, cx, cy, s, c1, c2, c3, nh):
    mode = nh % 3
    if mode == 0:
        # 柱状图
        bw = s//5
        for i, h in enumerate([0.4, 0.7, 1.0]):
            x = cx + (i-1)*s//2
            bh = int(s*h)
            D.rect(draw, x-bw, cy, x+bw, cy-bh, fill=c1, radius=2)
        draw.line([(cx-s, cy), (cx+s, cy)], fill=c2, width=2)
    elif mode == 1:
        # 上升箭头
        pts = [(cx, cy-s), (cx+s//2, cy), (cx+s//3, cy+s//2),
               (cx-s//3, cy+s//2), (cx-s//2, cy)]
        draw.polygon(pts, fill=c1)
    else:
        # 圆形币章
        D.circle(draw, cx, cy, s, outline=c1, width=3)
        D.circle(draw, cx, cy, s//2, fill=c1)
        D.star(draw, cx, cy, s//2, points=4, fill=c2, inner_ratio=0.05)

def _icon_food(draw, cx, cy, s, c1, c2, c3, nh):
    mode = nh % 3
    if mode == 0:
        # 叶子
        pts = [(cx, cy-s), (cx+s//2, cy-s//3), (cx+s//3, cy+s//3),
               (cx-s//3, cy+s//3), (cx-s//2, cy-s//3)]
        draw.polygon(pts, fill=c1)
        draw.line([(cx, cy+s//3), (cx, cy+s)], fill=c2, width=3)
    elif mode == 1:
        # 麦穗
        draw.line([(cx, cy-s), (cx, cy+s)], fill=c2, width=2)
        for side in [-1, 1]:
            for i in range(4):
                y = cy-s + i*s//2
                draw.line([(cx, y), (cx+side*s//2, y-s//4)], fill=c1, width=2)
    else:
        # 碗
        D.arc_line(draw, cx, cy+s//5, s, 0.2, 2.94, c1, width=max(3, s//6))
        draw.arc([cx-s, cy-s//2, cx+s, cy+s*2], 0, 180, fill=c1, width=0)
        D.dot(draw, cx, cy-s//3, s//4, c2)

def _icon_trade(draw, cx, cy, s, c1, c2, c3, nh):
    mode = nh % 3
    if mode == 0:
        # 地球
        D.circle(draw, cx, cy, s, outline=c1, width=2)
        draw.ellipse([cx-s//2, cy-s, cx+s//2, cy+s], outline=c2, width=1)
        draw.line([(cx-s, cy), (cx+s, cy)], fill=c2, width=1)
    elif mode == 1:
        # 循环箭头
        for a in [0, math.pi*2/3, math.pi*4/3]:
            x, y = cx+s*0.6*math.cos(a), cy+s*0.6*math.sin(a)
            D.triangle(draw, int(x), int(y), s//3, fill=c1, angle=a+math.pi/2)
        D.circle(draw, cx, cy, s//3, outline=c1, width=2)
    else:
        # 握手/交易
        D.rect(draw, cx-s, cy-s//3, cx+s, cy+s//3, outline=c1, width=2, radius=s//4)
        D.triangle(draw, cx-s//2, cy, s//3, fill=c1, angle=0)
        D.triangle(draw, cx+s//2, cy, s//3, fill=c1, angle=math.pi)

def _icon_build(draw, cx, cy, s, c1, c2, c3, nh):
    mode = nh % 3
    if mode == 0:
        # 建筑
        w, h = s, int(s*1.2)
        D.rect(draw, cx-w//2, cy-h//2, cx+w//2, cy+h//2, outline=c1, width=2)
        D.rect(draw, cx-w//3, cy-h//4, cx+w//3, cy+h//4, fill=c1, radius=3)
    elif mode == 1:
        # 蓝图格
        for dx in [-s//2, s//2]:
            for dy in [-s//2, s//2]:
                D.rect(draw, cx+dx-s//8, cy+dy-s//8, cx+dx+s//8, cy+dy+s//8, fill=c1, radius=2)
        D.rect(draw, cx-s//2, cy-s//2, cx+s//2, cy+s//2, fill=c2, outline=c1, width=1, radius=3)
    else:
        D.triangle(draw, cx, cy-s//3, s, fill=c1)
        D.rect(draw, cx-s//2, cy-s//3, cx+s//2, cy+s//2, outline=c1, width=2)

def _icon_health(draw, cx, cy, s, c1, c2, c3, nh):
    mode = nh % 3
    if mode == 0:
        w = s//4
        D.rect(draw, cx-w, cy-s, cx+w, cy+s, fill=c1, radius=3)
        D.rect(draw, cx-s, cy-w, cx+s, cy+w, fill=c1, radius=3)
    elif mode == 1:
        pts = [(cx,cy+s//2), (cx-s,cy), (cx-s//2,cy-s//2),
               (cx,cy-s//4), (cx+s//2,cy-s//2), (cx+s,cy)]
        draw.polygon(pts, fill=c1)
    else:
        draw.line([(cx-s,cy),(cx-s//3,cy),(cx,cy-s//2),(cx+s//3,cy),(cx+s,cy)], fill=c1, width=3)
        D.dot(draw, cx, cy-s//2, s//5, c2)

def _icon_edu(draw, cx, cy, s, c1, c2, c3, nh):
    mode = nh % 3
    if mode == 0:
        D.rect(draw, cx-s//2, cy-s//2, cx+s//2, cy+s//2, outline=c1, width=2, radius=4)
        draw.line([(cx, cy-s//2+4), (cx, cy+s//2-4)], fill=c2, width=1)
    elif mode == 1:
        D.circle(draw, cx, cy-s//4, s//3, fill=c2)
        pts = [(cx-s//2,cy-s//4),(cx+s//2,cy-s//4),(cx,cy+s//2)]
        draw.polygon(pts, fill=c1)
    else:
        D.circle(draw, cx, cy, s, outline=c1, width=2)
        for i in range(4):
            a = i*math.pi/2
            draw.line([(cx,cy),(cx+s*0.7*math.cos(a),cy+s*0.7*math.sin(a))], fill=c1, width=1)

def _icon_design(draw, cx, cy, s, c1, c2, c3, nh):
    mode = nh % 3
    if mode == 0:
        draw.line([(cx-s//3,cy+s//2),(cx+s//3,cy-s//2)], fill=c1, width=4)
        D.triangle(draw, cx+s//3, cy-s//2, s//3, fill=c1, angle=-math.pi/4)
    elif mode == 1:
        for i in range(3):
            for j in range(3):
                D.dot(draw, cx+(i-1)*s//2, cy+(j-1)*s//2, s//8, c1)
    else:
        draw.ellipse([cx-s, cy-s//2, cx+s, cy+s//2], outline=c1, width=2)
        D.circle(draw, cx, cy, s//3, fill=c1)

def _icon_culture(draw, cx, cy, s, c1, c2, c3, nh):
    mode = nh % 3
    if mode == 0:
        D.rect(draw, cx-s, cy-s, cx+s, cy+s, outline=c1, width=2)
        D.rect(draw, cx-s//2, cy-s//2, cx+s//2, cy+s//2, outline=c2, width=1)
    elif mode == 1:
        D.rect(draw, cx-s, cy-s, cx+s, cy+s, outline=c1, width=2, radius=s//4)
        draw.line([(cx, cy-s+4), (cx, cy+s-4)], fill=c2, width=1)
        draw.line([(cx-s+4, cy), (cx+s-4, cy)], fill=c2, width=1)
    else:
        for dx in [-s//2, 0, s//2]:
            D.circle(draw, cx+dx, cy, s//2, fill=c1, outline=c2, width=1)

def _icon_sports(draw, cx, cy, s, c1, c2, c3, nh):
    mode = nh % 3
    if mode == 0:
        pts = [(cx,cy-s),(cx+s//2,cy-s//3),(cx+s//2,cy+s//3),(cx,cy+s//2),
               (cx-s//2,cy+s//3),(cx-s//2,cy-s//3)]
        draw.polygon(pts, fill=c1)
    elif mode == 1:
        for i in range(3):
            y = cy-s//2 + i*s//2
            pts = [(cx-s//2,y-s//4),(cx,y),(cx-s//2,y+s//4)]
            draw.polygon(pts, fill=c1)
    else:
        D.star(draw, cx, cy, s, points=4, fill=c1)

def _icon_mfg(draw, cx, cy, s, c1, c2, c3, nh):
    mode = nh % 3
    if mode == 0:
        D.circle(draw, cx, cy, s, outline=c1, width=3)
        D.circle(draw, cx, cy, s//3, fill=c1)
        for i in range(8):
            a = i*math.pi/4
            D.rect(draw, cx+s*math.cos(a)-s//8, cy+s*math.sin(a)-s//8,
                   cx+s*math.cos(a)+s//8, cy+s*math.sin(a)+s//8, fill=c2, radius=2)
    elif mode == 1:
        pts = [(cx-s//3,cy-s),(cx+s//3,cy-s//3),(cx-s//3,cy),(cx+s//3,cy+s//3),(cx-s//3,cy+s)]
        draw.polygon(pts, fill=c1)
    else:
        D.circle(draw, cx-s//2, cy-s//2, s//3, outline=c1, width=3)
        D.rect(draw, cx, cy-s//8, cx+s//2, cy+s//8, fill=c1)

def _icon_beauty(draw, cx, cy, s, c1, c2, c3, nh):
    mode = nh % 3
    if mode == 0:
        for i in range(5):
            a = i*2*math.pi/5 - math.pi/2
            D.dot(draw, int(cx+s*0.45*math.cos(a)), int(cy+s*0.45*math.sin(a)), s//4, c1)
        D.dot(draw, cx, cy, s//5, c2)
    elif mode == 1:
        D.circle(draw, cx, cy-s//3, s//2, fill=c1)
        pts = [(cx-s//2,cy-s//3),(cx+s//2,cy-s//3),(cx,cy+s//2)]
        draw.polygon(pts, fill=c2)
    else:
        pts = [(cx-s,cy+s//3),(cx-s,cy-s//3),(cx-s//3,cy-s//3),
               (cx,cy-s),(cx+s//3,cy-s//3),(cx+s,cy-s//3),(cx+s,cy+s//3)]
        draw.polygon(pts, outline=c1, width=2)
        D.dot(draw, cx-s, cy-s//3, s//8, c2)
        D.dot(draw, cx, cy-s//3, s//8, c2)
        D.dot(draw, cx+s, cy-s//3, s//8, c2)

def _icon_law(draw, cx, cy, s, c1, c2, c3, nh):
    mode = nh % 3
    if mode == 0:
        draw.line([(cx,cy-s//2),(cx,cy+s//2)], fill=c1, width=2)
        draw.line([(cx-s,cy-s//2+2),(cx+s,cy-s//2+2)], fill=c1, width=2)
        for dx in [-1, 1]:
            pts = [(cx+dx*s//2,cy-s//2),(cx+dx*s//3,cy-s//4),(cx+dx*s*2//3,cy-s//4)]
            draw.polygon(pts, fill=c1)
    elif mode == 1:
        for i, (dx, h) in enumerate([(0,s), (-s//3,int(s*0.7)), (s//3,int(s*0.7))]):
            w = s//4
            D.rect(draw, cx+dx-w, cy-h//2, cx+dx+w, cy+h//2, outline=c1, width=2)
            D.rect(draw, cx+dx-w*2, cy-s//2, cx+dx+w*2, cy-h//2, fill=c1)
    else:
        pts = [(cx,cy-s),(cx+s,cy-s//2),(cx+s,cy+s//3),(cx,cy+s),
               (cx-s,cy+s//3),(cx-s,cy-s//2)]
        draw.polygon(pts, outline=c1, width=2)
        D.star(draw, cx, cy, s//3, points=5, fill=c1)

def _icon_realestate(draw, cx, cy, s, c1, c2, c3, nh):
    mode = nh % 3
    if mode == 0:
        pts = [(cx,cy-s),(cx+s,cy-s//3),(cx+s,cy+s//2),(cx-s,cy+s//2),(cx-s,cy-s//3)]
        draw.polygon(pts, outline=c1, width=2)
        D.rect(draw, cx-s//3, cy, cx+s//3, cy+s//2, outline=c2, width=1)
    elif mode == 1:
        D.circle(draw, cx-s//2, cy-s//3, s//3, outline=c1, width=2)
        draw.line([(cx-s//2,cy),(cx+s,cy)], fill=c1, width=3)
        draw.line([(cx+s//2,cy),(cx+s//2,cy+s//2)], fill=c1, width=3)
    else:
        w, h = s//2, s
        D.rect(draw, cx-w, cy-h//2, cx+w, cy+h//2, outline=c1, width=2)
        pts = [(cx-w,cy-h//2),(cx,cy-h),(cx+w,cy-h//2)]
        draw.polygon(pts, outline=c1, width=2)

def _icon_media(draw, cx, cy, s, c1, c2, c3, nh):
    mode = nh % 3
    if mode == 0:
        D.triangle(draw, cx+s//6, cy, s//2, fill=c1, angle=0)
        D.circle(draw, cx, cy, s, outline=c1, width=2)
    elif mode == 1:
        for i in range(3):
            y = cy-s//2 + i*s//2
            D.rect(draw, cx-s, y-s//6, cx+s, y+s//6, fill=c1 if i==1 else c2, radius=3)
    else:
        D.rect(draw, cx-s, cy-s//2, cx+s, cy+s//2, outline=c1, width=2, radius=s//4)
        D.triangle(draw, cx, cy, s//3, fill=c1, angle=0)


# ═══════════════ 7品类引擎 ═══════════════

def make_canvas(bg_color):
    img = Image.new("RGB", (SIZE, SIZE), bg_color)
    draw = ImageDraw.Draw(img)
    draw._image = img
    return img, draw


# ── 品类1: 纯文字标 (WORDMARK) ──
# 字体即Logo - 无图标，创意排版
def logo_wordmark(draw, name, industry, pal, nh, tagline):
    img = draw._image
    c1 = hex_to_rgb(pal["primary"])
    c2 = hex_to_rgb(pal["secondary"])
    c3 = hex_to_rgb(pal["accent"])
    n = len(name)

    # 文字表现方式 (4种)
    mode = (nh // 7) % 4

    if mode == 0:
        # 大字居中 + 装饰线
        if n <= 3: fs = 140
        elif n <= 5: fs = 100
        else: fs = 72
        fn = get_font(fs, "bold")
        tw, th = text_bbox(draw, name, fn)[2] - text_bbox(draw, name, fn)[0], text_bbox(draw, name, fn)[3] - text_bbox(draw, name, fn)[1]
        draw.text(((SIZE-tw)/2, SIZE/2-th), name, fill=c1, font=fn)
        # 双装饰线
        ly = SIZE/2 + 20
        draw.line([(SIZE*0.3, ly), (SIZE*0.7, ly)], fill=c2, width=2)
        draw.line([(SIZE*0.35, ly+10), (SIZE*0.65, ly+10)], fill=c3, width=1)
        sub_y = ly + 30
    elif mode == 1:
        # 竖排大字
        if n <= 3: fs = 120
        elif n <= 5: fs = 80
        else: fs = 56
        fn = get_font(fs, "bold")
        total_h = 0
        heights = []
        for ch in name:
            _, _, _, th = text_bbox(draw, ch, fn)
            heights.append(th)
            total_h += th + 8
        total_h -= 8
        y = (SIZE - total_h) / 2
        for i, ch in enumerate(name):
            bbox = text_bbox(draw, ch, fn)
            tw = bbox[2] - bbox[0]
            draw.text(((SIZE-tw)/2, y), ch, fill=c1, font=fn)
            y += heights[i] + 8
        sub_y = SIZE * 0.88
    elif mode == 2:
        # 首字超大
        if n <= 2:
            fs_big, fs_sm = 160, 80
        elif n <= 4:
            fs_big, fs_sm = 120, 60
        else:
            fs_big, fs_sm = 90, 48
        fn_big = get_font(fs_big, "bold")
        fn_sm = get_font(fs_sm, "bold")

        bb = text_bbox(draw, name[0], fn_big)
        tw_big = bb[2]-bb[0]
        th_big = bb[3]-bb[1]
        rest_w = 0
        for ch in name[1:]:
            rest_w += text_bbox(draw, ch, fn_sm)[2] - text_bbox(draw, ch, fn_sm)[0]
        rest_w += 10*(n-2)
        total_w = tw_big + 20 + rest_w
        x = (SIZE-total_w)/2
        mid_y = SIZE/2

        draw.text((x, mid_y-th_big/2), name[0], fill=c1, font=fn_big)
        x += tw_big + 20
        for ch in name[1:]:
            bb2 = text_bbox(draw, ch, fn_sm)
            tw_s, th_s = bb2[2]-bb2[0], bb2[3]-bb2[1]
            draw.text((x, mid_y+th_big/2-th_s-5), ch, fill=c2, font=fn_sm)
            x += tw_s + 10
        sub_y = SIZE * 0.72
    else:
        # 错位排版
        if n <= 3: fs = 100
        elif n <= 5: fs = 68
        else: fs = 44
        fn = get_font(fs, "bold")
        widths = []
        for ch in name:
            bb = text_bbox(draw, ch, fn)
            widths.append(bb[2]-bb[0])
        gap = fs//4
        total_w = sum(widths) + gap*(n-1)
        x = (SIZE-total_w)/2
        for i, (ch, tw) in enumerate(zip(name, widths)):
            bb = text_bbox(draw, ch, fn)
            th = bb[3]-bb[1]
            y_off = -fs//4 if i%2==0 else fs//4
            draw.text((x, SIZE/2-th//2+y_off), ch, fill=c1 if i%2==0 else c2, font=fn)
            x += tw + gap
        sub_y = SIZE * 0.78

    if tagline:
        fn_sub = get_font(20, "light")
        draw_ctext(draw, tagline.upper(), sub_y, fn_sub, c3)

    return img


# ── 品类2: 字母标 (LETTERMARK/MONOGRAM) ──
# 大字母+几何框，IBM/HBO风格
def logo_monogram(draw, name, industry, pal, nh, tagline):
    img = draw._image
    c1 = hex_to_rgb(pal["primary"])
    c2 = hex_to_rgb(pal["secondary"])
    c3 = hex_to_rgb(pal["accent"])

    # 取名字首字母（中文取第一字）
    initials = name[0]
    if len(name) >= 2:
        # 中文全部都是字母标，取前1-2字
        initials = name[:min(2, len(name))]

    mode = (nh // 11) % 3

    if mode == 0:
        # 圆形背景+字母
        r = 140
        D.circle(draw, SIZE/2, SIZE*0.42, r, fill=c1)
        fs = 120 if len(initials)==1 else 90
        fn = get_font(fs, "bold")
        bb = text_bbox(draw, initials, fn)
        tw = bb[2]-bb[0]
        th = bb[3]-bb[1]
        draw.text(((SIZE-tw)/2, SIZE*0.42-th/2), initials, fill=hex_to_rgb(pal["bg"]), font=fn)
        # 小副标题
        fn_sm = get_font(24, "regular")
        draw_ctext(draw, name, SIZE*0.42+r+40, fn_sm, c1)
        sub_y = SIZE*0.42+r+70
    elif mode == 1:
        # 方形重叠字母
        s = 130
        for i, ch in enumerate(initials):
            ox = SIZE/2 + (i-0.5)*s*0.6
            oy = SIZE*0.4
            D.rect(draw, ox-s/2, oy-s/2, ox+s/2, oy+s/2, fill=c1 if i==0 else c2, outline=c3, width=2, radius=10)
            fs = 90
            fn = get_font(fs, "bold")
            bb = text_bbox(draw, ch, fn)
            tw = bb[2]-bb[0]; th = bb[3]-bb[1]
            draw.text((ox-tw/2, oy-th/2), ch, fill=hex_to_rgb(pal["bg"]), font=fn)
        fn_sm = get_font(20, "regular")
        draw_ctext(draw, name, SIZE*0.75, fn_sm, c1)
        sub_y = SIZE*0.82
    else:
        # 六边形徽章
        r = 130
        D.hexagon(draw, SIZE/2, SIZE*0.42, r, fill=c1, outline=c2, width=3)
        fs = 100
        fn = get_font(fs, "bold")
        bb = text_bbox(draw, initials, fn)
        tw = bb[2]-bb[0]; th = bb[3]-bb[1]
        draw.text(((SIZE-tw)/2, SIZE*0.42-th/2), initials, fill=hex_to_rgb(pal["bg"]), font=fn)
        fn_sm = get_font(22, "regular")
        draw_ctext(draw, name, SIZE*0.42+r+40, fn_sm, c1)
        sub_y = SIZE*0.42+r+70

    if tagline:
        fn_sub = get_font(18, "light")
        draw_ctext(draw, tagline.upper(), sub_y, fn_sub, c3)

    return img


# ── 品类3: 图形标 (PICTORIAL MARK) ──
# 具象图标为主，品牌字为辅
def logo_pictorial(draw, name, industry, pal, nh, tagline):
    img = draw._image
    c1 = hex_to_rgb(pal["primary"])
    c2 = hex_to_rgb(pal["secondary"])
    c3 = hex_to_rgb(pal["accent"])

    mode = (nh // 13) % 3

    if mode == 0:
        # 大图标左上 + 文字右下
        icon_size = 160
        cxi, cyi = SIZE*0.35, SIZE*0.35
        draw_industry_icon(draw, cxi, cyi, icon_size, industry, pal, name)
        fn = get_font(52, "bold")
        draw.text((SIZE*0.2, SIZE*0.55), name, fill=c1, font=fn)
        sub_y = SIZE*0.65
    elif mode == 1:
        # 居中大图标 + 下方文字
        icon_size = 180
        draw_industry_icon(draw, SIZE/2, SIZE*0.35, icon_size, industry, pal, name)
        fn = get_font(44, "bold")
        draw_ctext(draw, name, SIZE*0.6, fn, c1)
        sub_y = SIZE*0.7
    else:
        # 图标 + 文字环绕排列
        icon_size = 140
        cxi, cyi = SIZE*0.3, SIZE/2
        draw_industry_icon(draw, cxi, cyi, icon_size, industry, pal, name)
        fn = get_font(48, "bold")
        draw.text((cxi+icon_size+30, cyi-30), name, fill=c1, font=fn)
        # 竖线分隔
        draw.line([(cxi+icon_size+20, cyi-40), (cxi+icon_size+20, cyi+60)], fill=c3, width=2)
        sub_y = cyi + 50

    if tagline:
        fn_sub = get_font(18, "light")
        draw_ctext(draw, tagline.upper(), sub_y, fn_sub, c3)

    return img


# ── 品类4: 抽象标 (ABSTRACT MARK) ──
# 纯抽象几何构成 + 文字
def logo_abstract(draw, name, industry, pal, nh, tagline):
    img = draw._image
    c1 = hex_to_rgb(pal["primary"])
    c2 = hex_to_rgb(pal["secondary"])
    c3 = hex_to_rgb(pal["accent"])
    cx, cy = SIZE/2, SIZE*0.38

    mode = (nh // 17) % 4

    if mode == 0:
        # 动态碎片 - 多个旋转矩形
        for i in range(5):
            a = i * 2*math.pi/5
            dx = 60*math.cos(a)
            dy = 60*math.sin(a)
            s = 30 + i*10
            # 使用旋转后的坐标画矩形
            r = 45
            ox = cx + r*math.cos(a)
            oy = cy + r*math.sin(a)
            D.rect(draw, ox-s/2, oy-s/2, ox+s/2, oy+s/2, fill=c1 if i<3 else c2, radius=4)
    elif mode == 1:
        # 同心辐射
        for i in range(4, 0, -1):
            r = 30 + i*35
            color = [c1, c2, c1, c3][i-1]
            if i%2==0:
                D.circle(draw, cx, cy, r, fill=color)
            else:
                D.ring(draw, cx, cy, r, color, 3)
    elif mode == 2:
        # 交叉动态线
        for i in range(6):
            a = i*math.pi/6
            dx, dy = 80*math.cos(a), 80*math.sin(a)
            color = c1 if i%3==0 else (c2 if i%3==1 else c3)
            draw.line([(cx-dx, cy-dy), (cx+dx, cy+dy)], fill=color, width=3)
        D.circle(draw, cx, cy, 25, fill=hex_to_rgb(pal["bg"]))
    else:
        # 不对称色块
        for i, (x, y, w, h) in enumerate([
            (cx-90, cy-70, 60, 40),
            (cx+30, cy-50, 50, 70),
            (cx-50, cy+20, 80, 30),
        ]):
            color = [c1, c2, c3][i]
            D.rect(draw, x, y, x+w, y+h, fill=color, radius=6)

    fn = get_font(44, "bold")
    draw_ctext(draw, name, SIZE*0.62, fn, c1)
    sub_y = SIZE*0.72

    if tagline:
        fn_sub = get_font(18, "light")
        draw_ctext(draw, tagline.upper(), sub_y, fn_sub, c3)

    return img


# ── 品类5: 徽章标 (EMBLEM) ──
# 图文被形状包裹 - Starbucks/哈雷风格
def logo_emblem(draw, name, industry, pal, nh, tagline):
    img = draw._image
    c1 = hex_to_rgb(pal["primary"])
    c2 = hex_to_rgb(pal["secondary"])
    c3 = hex_to_rgb(pal["accent"])
    bg_c = hex_to_rgb(pal["bg"])
    dark = hex_to_rgb(pal["dark"])
    cx, cy = SIZE/2, SIZE/2

    mode = (nh // 19) % 3

    if mode == 0:
        # 圆形徽章
        outer_r = 260
        D.circle(draw, cx, cy, outer_r, fill=c1)
        D.ring(draw, cx, cy, outer_r-10, c2, 4)
        D.ring(draw, cx, cy, outer_r-25, c3, 2)

        # 中心图标
        icon_r = 80
        draw_industry_icon(draw, cx, cy-25, icon_r, industry, {"primary": pal["bg"], "secondary": pal["accent"], "accent": pal["secondary"]}, name)

        # 环内文字
        fn_small = get_font(22, "bold")
        tname = name.upper() if any('\u4e00' <= c <= '\u9fff' for c in name) else name
        draw_ctext(draw, name, cy+70, fn_small, hex_to_rgb(pal["bg"]))
        sub_y = cy + outer_r + 30
    elif mode == 1:
        # 盾形徽章
        shield_h = 280
        shield_w = 220
        shield_top = cy - shield_h/2
        # 盾形轮廓
        pts = [
            (cx, shield_top),
            (cx+shield_w/2, shield_top+shield_h*0.3),
            (cx+shield_w/2, shield_top+shield_h*0.65),
            (cx, shield_top+shield_h),
            (cx-shield_w/2, shield_top+shield_h*0.65),
            (cx-shield_w/2, shield_top+shield_h*0.3),
        ]
        draw.polygon(pts, fill=c1, outline=c2)
        draw.line(pts + [pts[0]], fill=c2, width=3)

        draw_industry_icon(draw, cx, cy-30, 60, industry,
                          {"primary": pal["bg"], "secondary": pal["accent"], "accent": pal["bg"]}, name)

        fn = get_font(22, "bold")
        if len(name) > 3:
            l1, l2 = name[:len(name)//2], name[len(name)//2:]
            draw_ctext(draw, l1, cy+50, fn, hex_to_rgb(pal["bg"]))
            draw_ctext(draw, l2, cy+80, fn, hex_to_rgb(pal["bg"]))
        else:
            draw_ctext(draw, name, cy+60, fn, hex_to_rgb(pal["bg"]))
        sub_y = cy + shield_h/2 + 30
    else:
        # 六边形徽章
        r = 250
        D.hexagon(draw, cx, cy, r, fill=c1, outline=c2, width=4)
        D.hexagon(draw, cx, cy, r-15, fill=None, outline=c3, width=1)

        draw_industry_icon(draw, cx, cy-20, 80, industry,
                          {"primary": pal["bg"], "secondary": pal["accent"], "accent": pal["bg"]}, name)

        fn = get_font(24, "bold")
        draw_ctext(draw, name, cy+70, fn, hex_to_rgb(pal["bg"]))
        sub_y = cy + r + 20

    if tagline:
        fn_sub = get_font(18, "light")
        draw_ctext(draw, tagline.upper(), sub_y, fn_sub, c3)

    return img


# ── 品类6: 组合标 (COMBINATION MARK) ──
# 图标+文字经典组合 - 左侧图标+右侧文字
def logo_combination(draw, name, industry, pal, nh, tagline):
    img = draw._image
    c1 = hex_to_rgb(pal["primary"])
    c2 = hex_to_rgb(pal["secondary"])
    c3 = hex_to_rgb(pal["accent"])
    cx, cy = SIZE/2, SIZE/2

    mode = (nh // 23) % 3

    if mode == 0:
        # 左图标右文字
        icon_cx = SIZE*0.3
        draw_industry_icon(draw, icon_cx, cy, 130, industry, pal, name)
        tx = SIZE*0.48
        fn = get_font(52, "bold")
        draw.text((tx, cy-35), name, fill=c1, font=fn)
        sub = tagline or ""
        if sub:
            fn_sub = get_font(18, "light")
            draw.text((tx, cy+30), sub.upper(), fill=c3, font=fn_sub)
        sub_y = SIZE*0.78
    elif mode == 1:
        # 上图标下文字
        draw_industry_icon(draw, cx, SIZE*0.32, 140, industry, pal, name)
        fn = get_font(44, "bold")
        draw_ctext(draw, name, SIZE*0.58, fn, c1)
        sub_y = SIZE*0.68
    else:
        # 图标嵌入文字中
        icon_size = 80
        fn = get_font(64, "bold")
        bb = text_bbox(draw, name, fn)
        tw = bb[2]-bb[0]
        th = bb[3]-bb[1]
        text_x = (SIZE-tw)/2
        draw.text((text_x, cy-th/2), name, fill=c1, font=fn)
        icon_cx = text_x - icon_size - 20
        icon_cy = cy
        if icon_cx < 80:
            icon_cx = SIZE/2
            icon_cy = cy - th/2 - icon_size - 10
        draw_industry_icon(draw, icon_cx, icon_cy, icon_size, industry, pal, name)
        sub_y = cy + th/2 + 30

    if tagline:
        fn_sub = get_font(18, "light")
        draw_ctext(draw, tagline.upper(), sub_y, fn_sub, c3)

    return img


# ── 品类7: 负空间/巧思标 (NEGATIVE SPACE) ──
# 图形和文字之间创造负空间效果
def logo_negative(draw, name, industry, pal, nh, tagline):
    img = draw._image
    c1 = hex_to_rgb(pal["primary"])
    c2 = hex_to_rgb(pal["secondary"])
    c3 = hex_to_rgb(pal["accent"])
    bg_c = hex_to_rgb(pal["bg"])
    cx, cy = SIZE/2, SIZE/2

    mode = (nh // 29) % 3

    if mode == 0:
        # 上下分区 - 上半部纯色，下半部留白，文字在交界处
        D.rect(draw, 0, 0, SIZE, SIZE/2+PAD, fill=c1)
        fn = get_font(56, "bold")
        draw_ctext(draw, name, SIZE/2-8, fn, hex_to_rgb(pal["bg"]))
        fn2 = get_font(28, "bold")
        draw_ctext(draw, name, SIZE/2+30, fn2, c1)
        sub_y = SIZE*0.72
    elif mode == 1:
        # 色块切分 - 文字跨两个色块
        split_x = SIZE/2 + 40 * ((nh//31)%7-3)
        D.rect(draw, 0, 0, split_x, SIZE, fill=c1)
        D.rect(draw, split_x, 0, SIZE, SIZE, fill=c2)
        fn = get_font(60, "bold")
        bb = text_bbox(draw, name, fn)
        tw = bb[2]-bb[0]; th = bb[3]-bb[1]
        tx = (SIZE-tw)/2
        cl, cr = hex_to_rgb(pal["bg"]), hex_to_rgb(pal["bg"])
        # 画文字跨两色区
        for i, ch in enumerate(name):
            bb2 = text_bbox(draw, ch, fn)
            ctw = bb2[2]-bb2[0]
            cx_ch = tx + ctw/2
            for prev_w in [text_bbox(draw, name[:i], fn)[2]-text_bbox(draw, name[:i], fn)[0] if i>0 else 0]:
                pass
            if cx_ch < split_x:
                draw.text((tx, cy-th/2), ch, fill=hex_to_rgb(pal["bg"]), font=fn)
            else:
                draw.text((tx, cy-th/2), ch, fill=hex_to_rgb(pal["bg"]), font=fn)
            tx += ctw + 5
        sub_y = SIZE*0.72
    else:
        # 镂空图形 - 大形状挖出文字
        D.rect(draw, SIZE*0.15, SIZE*0.25, SIZE*0.85, SIZE*0.65, fill=c1, radius=40)
        fn = get_font(80, "bold")
        draw_ctext(draw, name, cy-5, fn, hex_to_rgb(pal["bg"]))
        sub_y = SIZE*0.78

    if tagline:
        fn_sub = get_font(18, "light")
        draw_ctext(draw, tagline.upper(), sub_y, fn_sub, c3)

    return img


# ═══════════════ 调度 ═══════════════

LOGO_TYPES = [
    ("wordmark",    logo_wordmark),
    ("monogram",    logo_monogram),
    ("pictorial",   logo_pictorial),
    ("abstract",    logo_abstract),
    ("emblem",      logo_emblem),
    ("combination", logo_combination),
    ("negative",    logo_negative),
]

LOGO_NAMES = {
    "wordmark":    "纯文字标",
    "monogram":    "字母标",
    "pictorial":   "图形标",
    "abstract":    "抽象标",
    "emblem":      "徽章标",
    "combination": "组合标",
    "negative":    "负空间标",
}


def compose_logo(name, industry, mood, palette, index, **kwargs):
    """根据index确定品类，同一名称永远相同品类"""
    nh = name_hash(name)

    # 用名称哈希决定品类：不同名称分配到不同品类
    type_idx = nh % len(LOGO_TYPES)
    # 然后用index在品类间轮转
    effective_idx = (type_idx + index) % len(LOGO_TYPES)

    type_name, logo_fn = LOGO_TYPES[effective_idx]
    ing = palette.get("bg", "#ffffff")
    img, draw = make_canvas(ing)

    try:
        result = logo_fn(draw, name, industry, palette, nh,
                        tagline=kwargs.get("tagline", ""))
        result._type = type_name
        return result
    except Exception as e:
        # 出错时回退到wordmark
        img2, draw2 = make_canvas(ing)
        result = logo_wordmark(draw2, name, industry, palette, nh,
                              tagline=kwargs.get("tagline", ""))
        result._type = "wordmark"
        return result


# ═══════════════ 保存 ═══════════════

def save_pair(img, out_dir, name):
    base = os.path.join(out_dir, name)
    img.save(f"{base}.png", "PNG")
    avatar = img.copy()
    avatar.thumbnail((256, 256), Image.LANCZOS)
    avatar.save(f"{base}-avatar.png", "PNG")
    return f"{base}.png"


# ═══════════════ 主程序 ═══════════════

def main():
    parser = argparse.ArgumentParser(description="Logo Generator v4 — 多品类引擎")
    parser.add_argument("--name", required=True)
    parser.add_argument("--industry", default="tech")
    parser.add_argument("--mood", default=None)
    parser.add_argument("--count", type=int, default=7)
    parser.add_argument("--tagline", default="")
    parser.add_argument("--english", default="")
    parser.add_argument("--output", default="")
    parser.add_argument("--color", default="")
    parser.add_argument("--brief", default="")

    args = parser.parse_args()

    mood = args.mood or INDUSTRY_MOOD.get(args.industry, "modern")
    if mood not in PALETTES:
        mood = "modern"
    palette = dict(PALETTES[mood])
    if args.color:
        palette["primary"] = args.color

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = "".join(c if c.isascii() and c.isalnum() else "_" for c in args.name)[:20]
    out_dir = args.output or os.path.join(os.path.dirname(__file__) or ".", "output", f"{safe}_{ts}")
    os.makedirs(out_dir, exist_ok=True)

    nh = name_hash(args.name)
    type_idx = nh % 7
    first_type = LOGO_TYPES[type_idx][0]

    print("=" * 60)
    print(f"  🎨 Logo Generator v4 — 多品类引擎")
    print(f"  公司: {args.name}")
    print(f"  行业: {args.industry}  调性: {mood}")
    print(f"  哈希: {nh}  主品类: {LOGO_NAMES[first_type]}")
    print(f"  生成: {args.count} 个设计（7品类轮转）")
    if args.brief:
        print(f"  简报: {args.brief}")
    print("=" * 60)
    print()

    ok = 0
    for i in range(args.count):
        try:
            img = compose_logo(args.name, args.industry, mood, palette, i,
                              tagline=args.tagline, english=args.english)
            name_i = f"logo_{i+1:02d}"
            save_pair(img, out_dir, name_i)
            tname = LOGO_NAMES.get(getattr(img, '_type', '?'), '?')
            print(f"    ✓ logo_{i+1:02d} — {tname}")
            ok += 1
        except Exception as e:
            print(f"    ✗ logo_{i+1:02d} — 失败: {e}")

    print()
    print("=" * 60)
    print(f"  ✅ {ok}/{args.count} 个独立设计")
    print(f"  📁 {out_dir}")
    print(f"  💡 7大品类 × 轮转 → 每个设计来自完全不同的视觉范式")
    print("=" * 60)


if __name__ == "__main__":
    main()
