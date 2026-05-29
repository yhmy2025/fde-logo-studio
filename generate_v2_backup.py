#!/usr/bin/env python3
"""
Logo Generator v2 — 多调性·多布局·行业适配
=============================================
设计思路驱动的Logo批量生成器

用法:
  # 基础：公司名 + 行业
  python generate.py --name "星辰科技" --industry tech

  # 加调性：控制整体视觉风格
  python generate.py --name "绿野餐饮" --industry food --mood elegance

  # 加口号/副标题
  python generate.py --name "谊璜贸易" --industry trade --tagline "全球供应链服务商"

  # 自然语言设计简报（AI辅助选参）
  python generate.py --name "山里人" --brief "做高端土特产的，想要古朴雅致的感觉，不要太现代化"

  # 自定义主色
  python generate.py --name "品牌名" --industry tech --color "#ff6b35"

  # 按方向数量控制（对接收费档位）
  python generate.py --name "品牌名" --industry tech --directions 3  # 出3个风格方向

调性 (--mood):
  modern    现代简约 — 大留白、细字体、冷色
  elegance  优雅高端 — 衬线感、金/深色、对称
  bold      大胆醒目 — 强对比、粗字体、高饱和
  playful   活泼年轻 — 圆润、暖色、有趣
  tech      科技感   — 蓝紫渐变、几何、发光
  vintage   复古经典 — 暖灰、做旧色、传统排版
  minimal   极致简约 — 黑白、极细、去掉一切装饰
  nature    自然健康 — 绿色系、柔和曲线

行业 (--industry): tech, finance, food, construction, health, education,
  trade, design, realestate, culture, sports, manufacturing, beauty, law

风格方向 (--styles 或 --directions):
  seal, minimal, geometric, gradient, lettermark, badge, abstract, typographic
"""

import argparse
import colorsys
import json
import math
import os
import sys
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from PIL import Image, ImageDraw, ImageFont

# ═══════════════════════════════════════════════════════
#  字体
# ═══════════════════════════════════════════════════════
FONT_CN = "C:/Windows/Fonts/msyh.ttc"
FONT_BOLD = "C:/Windows/Fonts/msyhbd.ttc"
FONT_LIGHT = "C:/Windows/Fonts/msyhl.ttc"
FONT_EN = "C:/Windows/Fonts/arial.ttf"
FONT_EN_BOLD = "C:/Windows/Fonts/arialbd.ttf"
FONT_SERIF = "C:/Windows/Fonts/times.ttf"

for fp in [FONT_BOLD, FONT_LIGHT, FONT_SERIF]:
    if not os.path.exists(fp) and fp != FONT_SERIF:
        pass  # fallback below

SIZE = 800
AVATAR = 400

# ═══════════════════════════════════════════════════════
#  调性 → 配色+排版参数
# ═══════════════════════════════════════════════════════
MOOD_PALETTES = {
    "modern": {
        "colors": ["#1a1a2e", "#e94560", "#0f3460", "#16213e", "#ffffff"],
        "accent_colors": ["#e94560", "#f5f5f5", "#c0c0c0"],
        "description": "现代简约：大留白、细字体、冷色调",
        "font_weight": "light",
        "spacing": "loose",
        "contrast": "high",
    },
    "elegance": {
        "colors": ["#1a1a1a", "#c9a84c", "#2c2c2c", "#f5f0e8", "#8b7355"],
        "accent_colors": ["#c9a84c", "#d4a843", "#b8860b"],
        "description": "优雅高端：深色底、金色点缀、对称构图",
        "font_weight": "bold",
        "spacing": "normal",
        "contrast": "medium",
    },
    "bold": {
        "colors": ["#dc2626", "#1e1e1e", "#f97316", "#ffffff", "#fef3c7"],
        "accent_colors": ["#f97316", "#fbbf24", "#ffffff"],
        "description": "大胆醒目：强对比、粗体、高饱和",
        "font_weight": "bold",
        "spacing": "tight",
        "contrast": "high",
    },
    "playful": {
        "colors": ["#ff6b6b", "#4ecdc4", "#ffe66d", "#a8e6cf", "#ffffff"],
        "accent_colors": ["#ff6b6b", "#4ecdc4", "#ffe66d"],
        "description": "活泼年轻：圆润、暖色、有趣",
        "font_weight": "regular",
        "spacing": "loose",
        "contrast": "medium",
    },
    "tech": {
        "colors": ["#1e1b4b", "#6366f1", "#06b6d4", "#8b5cf6", "#0f172a"],
        "accent_colors": ["#6366f1", "#06b6d4", "#22d3ee"],
        "description": "科技感：蓝紫渐变、几何图形、发光感",
        "font_weight": "light",
        "spacing": "loose",
        "contrast": "high",
    },
    "vintage": {
        "colors": ["#5c4033", "#c9a84c", "#8b7355", "#f5f0e8", "#3c2415"],
        "accent_colors": ["#c9a84c", "#8b7355", "#d4a843"],
        "description": "复古经典：暖灰棕、做旧质感、传统排版",
        "font_weight": "bold",
        "spacing": "normal",
        "contrast": "low",
    },
    "minimal": {
        "colors": ["#1a1a1a", "#ffffff", "#f5f5f5", "#6b7280", "#e5e5e5"],
        "accent_colors": ["#1a1a1a", "#374151", "#9ca3af"],
        "description": "极致简约：黑白灰、极细线条、去装饰",
        "font_weight": "light",
        "spacing": "loose",
        "contrast": "high",
    },
    "nature": {
        "colors": ["#064e3b", "#059669", "#34d399", "#ecfdf5", "#f0fdf4"],
        "accent_colors": ["#059669", "#10b981", "#6ee7b7"],
        "description": "自然健康：绿色系、柔和曲线、有机感",
        "font_weight": "regular",
        "spacing": "normal",
        "contrast": "medium",
    },
}

# 行业默认调性映射
INDUSTRY_MOOD = {
    "tech": "tech", "finance": "elegance", "food": "playful",
    "construction": "bold", "health": "nature", "education": "modern",
    "trade": "elegance", "design": "modern", "realestate": "elegance",
    "culture": "vintage", "sports": "bold", "manufacturing": "bold",
    "beauty": "modern", "law": "elegance", "default": "modern",
}

# ═══════════════════════════════════════════════════════
#  行业图标抽象 (纯几何线条)
# ═══════════════════════════════════════════════════════
def draw_industry_icon(draw, cx, cy, size, color, industry):
    """在(cx,cy)绘制行业几何图标，size为半径"""
    r = size
    color_rgb = hex_to_rgb(color)
    lw = max(2, r // 20)

    icons = {
        "tech": lambda: _icon_circuit(draw, cx, cy, r, color_rgb, lw),
        "finance": lambda: _icon_pillar(draw, cx, cy, r, color_rgb, lw),
        "food": lambda: _icon_leaf(draw, cx, cy, r, color_rgb, lw),
        "construction": lambda: _icon_building(draw, cx, cy, r, color_rgb, lw),
        "health": lambda: _icon_cross(draw, cx, cy, r, color_rgb, lw),
        "education": lambda: _icon_book(draw, cx, cy, r, color_rgb, lw),
        "trade": lambda: _icon_globe(draw, cx, cy, r, color_rgb, lw),
        "design": lambda: _icon_pen(draw, cx, cy, r, color_rgb, lw),
        "realestate": lambda: _icon_home(draw, cx, cy, r, color_rgb, lw),
        "culture": lambda: _icon_chinese(draw, cx, cy, r, color_rgb, lw),
        "sports": lambda: _icon_flame(draw, cx, cy, r, color_rgb, lw),
        "manufacturing": lambda: _icon_gear(draw, cx, cy, r, color_rgb, lw),
        "beauty": lambda: _icon_flower(draw, cx, cy, r, color_rgb, lw),
        "law": lambda: _icon_scales(draw, cx, cy, r, color_rgb, lw),
    }
    icons.get(industry, lambda: _icon_circle(draw, cx, cy, r, color_rgb, lw))()


def _icon_circle(draw, cx, cy, r, c, lw):
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=c, width=lw)
    draw.ellipse([cx-r//3, cy-r//3, cx+r//3, cy+r//3], fill=c)

def _icon_gear(draw, cx, cy, r, c, lw):
    draw.ellipse([cx-r+5, cy-r+5, cx+r-5, cy+r-5], outline=c, width=lw)
    draw.ellipse([cx-r//4, cy-r//4, cx+r//4, cy+r//4], fill=c)
    for i in range(8):
        a = i * math.pi/4
        dx, dy = r*0.8*math.cos(a), r*0.8*math.sin(a)
        sr = r//6
        draw.ellipse([cx+dx-sr, cy+dy-sr, cx+dx+sr, cy+dy+sr], fill=c)

def _icon_leaf(draw, cx, cy, r, c, lw):
    pts = [(cx, cy-r), (cx+r*0.7, cy-r*0.2), (cx+r*0.5, cy+r*0.5),
           (cx, cy+r*0.8), (cx-r*0.5, cy+r*0.5), (cx-r*0.7, cy-r*0.2)]
    draw.polygon(pts, outline=c, width=lw)
    draw.line([(cx, cy+r*0.8), (cx, cy+r)], fill=c, width=lw)

def _icon_building(draw, cx, cy, r, c, lw):
    w, h = r*1.2, r*1.4
    draw.rectangle([cx-w//2, cy-h//2, cx+w//2, cy+h//2], outline=c, width=lw)
    for row in range(2):
        for col in range(2):
            sx = cx - w//4 + col*w//2.5
            sy = cy - h//3 + row*h//2.5
            sr = r//10
            draw.rectangle([sx-sr, sy-sr, sx+sr, sy+sr], outline=c, width=1)

def _icon_cross(draw, cx, cy, r, c, lw):
    a = r // 5
    draw.rectangle([cx-a, cy-r, cx+a, cy+r], fill=c)
    draw.rectangle([cx-r, cy-a, cx+r, cy+a], fill=c)

def _icon_book(draw, cx, cy, r, c, lw):
    w, h = r*1.0, r*1.3
    draw.rectangle([cx-w//2, cy-h//2, cx+w//2, cy+h//2], outline=c, width=lw)
    draw.line([(cx, cy-h//2), (cx, cy+h//2)], fill=c, width=1)

def _icon_globe(draw, cx, cy, r, c, lw):
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=c, width=lw)
    draw.ellipse([cx-r//2, cy-r, cx+r//2, cy+r], outline=c, width=1)
    draw.line([(cx-r, cy), (cx+r, cy)], fill=c, width=1)

def _icon_home(draw, cx, cy, r, c, lw):
    pts = [(cx, cy-r), (cx+r, cy-r*0.2), (cx+r, cy+r),
           (cx-r, cy+r), (cx-r, cy-r*0.2)]
    draw.polygon(pts, outline=c, width=lw)
    hw = r // 3
    draw.rectangle([cx-hw, cy+r-hw*2, cx+hw, cy+r], outline=c, width=lw//2)

def _icon_pillar(draw, cx, cy, r, c, lw):
    for i, (dx, dy) in enumerate([(0, -r*0.5), (-r*0.4, r*0.2), (r*0.4, r*0.2)]):
        w = r//3
        draw.rectangle([cx+dx-w, cy+dy, cx+dx+w, cy+r*0.6], outline=c, width=lw)
        draw.rectangle([cx+dx-w*1.5, cy+dy-w//2, cx+dx+w*1.5, cy+dy], fill=c)
    draw.line([(cx-r*0.8, cy+r*0.6), (cx+r*0.8, cy+r*0.6)], fill=c, width=lw)

def _icon_pen(draw, cx, cy, r, c, lw):
    pts = [(cx-r*0.3, cy+r*0.6), (cx+r*0.3, cy-r*0.6)]
    draw.line(pts, fill=c, width=lw*2)
    pts2 = [(cx-r*0.1, cy-r*0.5), (cx+r*0.2, cy-r*0.8), (cx+r*0.4, cy-r*0.6)]
    draw.polygon(pts2, fill=c)

def _icon_flame(draw, cx, cy, r, c, lw):
    pts = [(cx, cy-r), (cx+r*0.5, cy-r*0.3), (cx+r*0.6, cy+r*0.2),
           (cx+r*0.2, cy+r*0.5), (cx, cy+r*0.3),
           (cx-r*0.2, cy+r*0.5), (cx-r*0.6, cy+r*0.2), (cx-r*0.5, cy-r*0.3)]
    draw.polygon(pts, fill=c)

def _icon_chinese(draw, cx, cy, r, c, lw):
    """中式回纹/方框"""
    s = r * 0.7
    draw.rectangle([cx-s, cy-s, cx+s, cy+s], outline=c, width=lw)
    s2 = r * 0.4
    draw.rectangle([cx-s2, cy-s2, cx+s2, cy+s2], outline=c, width=lw//2)
    # 四角装饰
    cl = r // 5
    for dx, dy in [(-1,-1), (1,-1), (-1,1), (1,1)]:
        draw.line([(cx+dx*cl, cy+dy*s2), (cx+dx*cl, cy+dy*s)], fill=c, width=2)

def _icon_circuit(draw, cx, cy, r, c, lw):
    """电路板/芯片"""
    s = r * 0.7
    draw.rectangle([cx-s, cy-s, cx+s, cy+s], outline=c, width=lw)
    for dx in [-s*0.5, 0, s*0.5]:
        for dy in [-s*0.5, 0, s*0.5]:
            sr = r // 8
            draw.ellipse([cx+dx-sr, cy+dy-sr, cx+dx+sr, cy+dy+sr], fill=c)

def _icon_flower(draw, cx, cy, r, c, lw):
    for i in range(5):
        a = i * 2*math.pi/5 - math.pi/2
        px = cx + r*0.5*math.cos(a)
        py = cy + r*0.5*math.sin(a)
        sr = r // 3
        draw.ellipse([px-sr, py-sr, px+sr, py+sr], outline=c, width=lw)
    draw.ellipse([cx-r//5, cy-r//5, cx+r//5, cy+r//5], fill=c)

def _icon_scales(draw, cx, cy, r, c, lw):
    draw.line([(cx-r*0.6, cy+r*0.5), (cx+r*0.6, cy+r*0.5)], fill=c, width=lw)
    draw.line([(cx, cy-r*0.4), (cx, cy+r*0.5)], fill=c, width=lw)
    for dx in [-1, 1]:
        pts = [(cx+dx*r*0.45, cy-r*0.15), (cx+dx*r*0.15, cy+r*0.3),
               (cx+dx*r*0.55, cy+r*0.3), (cx+dx*r*0.55, cy-r*0.15)]
        draw.polygon(pts, outline=c, width=lw//2)

# ═══════════════════════════════════════════════════════
#  工具函数
# ═══════════════════════════════════════════════════════
def name_hash(name):
    """名称哈希 → 0-99，用于决定配色顺序等变化"""
    h = 0
    for i, c in enumerate(name):
        h = (h * 31 + ord(c)) % 100
    return h

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"

def lerp_color(c1, c2, t):
    return tuple(max(0, min(255, int(a + (b-a)*t))) for a, b in zip(c1, c2))

def get_font(size, weight="regular"):
    try:
        if weight == "bold":
            return ImageFont.truetype(FONT_BOLD, size)
        elif weight == "light" and os.path.exists(FONT_LIGHT):
            return ImageFont.truetype(FONT_LIGHT, size)
        return ImageFont.truetype(FONT_CN, size)
    except Exception:
        return ImageFont.truetype(FONT_CN, size)

def get_font_en(size, bold=False):
    try:
        fp = FONT_EN_BOLD if bold else FONT_EN
        return ImageFont.truetype(fp, size)
    except Exception:
        return ImageFont.truetype(FONT_EN, size)

def text_bbox(draw, text, font):
    b = draw.textbbox((0, 0), text, font=font)
    return b[2]-b[0], b[3]-b[1]

def draw_centered_text(draw, text, y, font, color, w):
    tw, _ = text_bbox(draw, text, font)
    draw.text(((w-tw)/2, y), text, fill=color, font=font)
    return tw

def save_both(img, path, name):
    fn = os.path.join(path, f"{name}.png")
    img.save(fn)
    av = img.resize((AVATAR, AVATAR), Image.LANCZOS)
    av.save(os.path.join(path, f"{name}-avatar.png"))
    return fn


# ═══════════════════════════════════════════════════════
#  风格1: 印章/徽章 SEAL
# ═══════════════════════════════════════════════════════
def gen_seal(name, mood, palette, output_dir, tagline="", industry="default"):
    results = []
    colors = palette["colors"]
    accents = palette["accent_colors"]
    fw = palette["font_weight"]

    combos = [
        ("朱砂印", colors[0], accents[0]),
        ("蓝金印", accents[1] if len(accents) > 1 else colors[0], accents[0]),
        ("墨金印", "#1a1a1a", accents[0]),
        ("雅白印", "#f5f0e8", colors[0]),
    ]

    for vname, bg, accent in combos:
        img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        cx, cy = SIZE//2, SIZE//2
        outer_r = 320

        # 双层圆环
        draw.ellipse([cx-outer_r, cy-outer_r, cx+outer_r, cy+outer_r],
                     outline=hex_to_rgb(bg), width=10)
        draw.ellipse([cx-outer_r+16, cy-outer_r+16, cx+outer_r-16, cy+outer_r-16],
                     outline=hex_to_rgb(accent), width=2)

        # 主文字
        cn_len = len(name)
        if cn_len <= 2:
            font_cn = get_font(150, fw)
            for i, ch in enumerate(name):
                tw, th = text_bbox(draw, ch, font_cn)
                draw.text((cx-tw//2, cy-th + i*140), ch, fill=hex_to_rgb(bg), font=font_cn)
        elif cn_len <= 4:
            half = cn_len // 2
            line1, line2 = name[:half], name[half:]
            font_cn = get_font(110, fw)
            th = text_bbox(draw, "测", font_cn)[1]
            draw_centered_text(draw, line1, cy-80, font_cn, hex_to_rgb(bg), SIZE)
            draw_centered_text(draw, line2, cy+30, font_cn, hex_to_rgb(bg), SIZE)
        else:
            font_cn = get_font(72, fw)
            draw_centered_text(draw, name, cy-25, font_cn, hex_to_rgb(bg), SIZE)

        # 副标题（放在底部）
        if tagline:
            f_tag = get_font(22, "light")
            draw_centered_text(draw, tagline, cy+outer_r-50, f_tag,
                              hex_to_rgb(accent), SIZE)

        results.append(save_both(img, output_dir, f"seal_{vname}"))
    return results


# ═══════════════════════════════════════════════════════
#  风格2: 极简字标 MINIMAL
# ═══════════════════════════════════════════════════════
def gen_minimal(name, mood, palette, output_dir, tagline="", industry="default"):
    results = []
    colors = palette["colors"]
    fw = palette["font_weight"]
    spacing = palette["spacing"]

    combos = [
        ("白底主色", "#ffffff", colors[0], colors[2] if len(colors) > 2 else colors[1]),
        ("主色底白字", colors[0], "#ffffff", colors[3] if len(colors) > 3 else colors[0]),
        ("浅灰底黑字", colors[3] if len(colors) > 3 else "#f5f5f5", "#1a1a1a",
         colors[1] if len(colors) > 1 else colors[0]),
        ("白底双色", "#ffffff", colors[0], colors[1]),
    ]

    for vname, bg, fg, *rest in combos:
        accent = rest[0] if rest else None
        img = Image.new("RGBA", (SIZE, SIZE), hex_to_rgb(bg) + (255,))
        draw = ImageDraw.Draw(img)

        cn_len = len(name)
        if cn_len <= 3:
            fn, gap = get_font(130, fw), 150
        elif cn_len <= 5:
            fn, gap = get_font(90, fw), 110
        else:
            fn, gap = get_font(64, fw), 80

        # 计算水平排列
        char_data = []
        total_w = 0
        for ch in name:
            tw, th = text_bbox(draw, ch, fn)
            char_data.append((tw, th))
            total_w += tw
        total_w += gap * (cn_len - 1)

        start_x = (SIZE - total_w) / 2
        x = start_x
        for i, (cw, ch_h) in enumerate(char_data):
            y = (SIZE - ch_h) / 2 - 15
            draw.text((x, y), name[i], fill=hex_to_rgb(fg), font=fn)
            x += cw
            if accent and i < cn_len - 1:
                dr = 5
                dx = x + gap/2
                draw.ellipse([dx-dr, SIZE/2-dr, dx+dr, SIZE/2+dr],
                             fill=hex_to_rgb(accent))
            x += gap

        # 装饰线
        ly = SIZE * 0.68
        draw.line([(SIZE*0.3, ly), (SIZE*0.7, ly)], fill=hex_to_rgb(fg), width=2)

        if tagline:
            ft = get_font(24, "light")
            draw_centered_text(draw, tagline, ly + 25, ft, hex_to_rgb(accent or fg), SIZE)

        results.append(save_both(img, output_dir, f"minimal_{vname}"))
    return results


# ═══════════════════════════════════════════════════════
#  风格3: 几何图形 GEOMETRIC
# ═══════════════════════════════════════════════════════
def gen_geometric(name, mood, palette, output_dir, tagline="", industry="default"):
    results = []
    colors = palette["colors"]
    fw = palette["font_weight"]
    cx, cy = SIZE//2, SIZE//2

    combos = [
        ("六边形", colors[0], colors[2] if len(colors) > 2 else colors[1], True),
        ("菱形", colors[0], colors[1], True),
        ("圆形徽记", colors[0], colors[2] if len(colors) > 2 else colors[1], True),
        ("方形构成", colors[0], colors[1], False),
    ]

    for vname, c1, c2, use_icon in combos:
        img = Image.new("RGBA", (SIZE, SIZE), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)
        r = 180

        if "六边形" in vname:
            pts = [(cx+r*math.cos(math.pi/6+i*math.pi/3),
                    cy+r*math.sin(math.pi/6+i*math.pi/3)) for i in range(6)]
            draw.polygon(pts, fill=hex_to_rgb(c1), outline=hex_to_rgb(c2), width=3)
            if use_icon:
                draw_industry_icon(draw, cx, cy, r//2, c2, industry)
        elif "菱形" in vname:
            pts = [(cx, cy-r-20), (cx+r, cy), (cx, cy+r+20), (cx-r, cy)]
            draw.polygon(pts, fill=hex_to_rgb(c1), outline=hex_to_rgb(c2), width=3)
            if use_icon:
                draw_industry_icon(draw, cx, cy, r//2, c2, industry)
        elif "圆形" in vname:
            draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=hex_to_rgb(c1),
                         outline=hex_to_rgb(c2), width=3)
            if use_icon:
                draw_industry_icon(draw, cx, cy, r//2, c2, industry)
        elif "方形" in vname:
            s = r * 1.3
            draw.rounded_rectangle([cx-s, cy-s, cx+s, cy+s], radius=20,
                                   fill=hex_to_rgb(c1), outline=hex_to_rgb(c2), width=3)
            if use_icon:
                draw_industry_icon(draw, cx, cy, r//2, c2, industry)

        fn = get_font(56, fw)
        draw_centered_text(draw, name, cy+r+55, fn, hex_to_rgb("#1a1a1a"), SIZE)
        if tagline:
            ft = get_font(22, "light")
            draw_centered_text(draw, tagline, cy+r+105, ft, hex_to_rgb("#6b7280"), SIZE)

        results.append(save_both(img, output_dir, f"geometric_{vname}"))
    return results


# ═══════════════════════════════════════════════════════
#  风格4: 渐变现代 GRADIENT
# ═══════════════════════════════════════════════════════
def gen_gradient(name, mood, palette, output_dir, tagline="", industry="default"):
    results = []
    colors = palette["colors"]
    fw = palette["font_weight"]

    combos = [
        ("对角渐变", colors[0], colors[2] if len(colors) > 2 else colors[1]),
        ("垂直渐变", colors[0], colors[1]),
        ("深色渐变", "#0f172a", colors[2] if len(colors) > 2 else colors[0]),
        ("暖色渐变", colors[1], "#ffffff" if mood in ["modern"] else colors[3] if len(colors) > 3 else colors[0]),
    ]

    for vname, c1, c2 in combos:
        img = Image.new("RGBA", (SIZE, SIZE))
        px = img.load()
        c1r, c2r = hex_to_rgb(c1), hex_to_rgb(c2)
        for y in range(SIZE):
            t = y / SIZE
            col = lerp_color(c1r, c2r, t)
            for x in range(SIZE):
                px[x, y] = col + (255,)

        draw = ImageDraw.Draw(img)
        font_cn = get_font(96, fw)
        tw, th = text_bbox(draw, name, font_cn)
        x, y = (SIZE-tw)/2, (SIZE-th)/2 - 30

        # 文字阴影
        draw.text((x+2, y+2), name, fill=(0,0,0,60), font=font_cn)
        draw.text((x, y), name, fill=(255,255,255,245), font=font_cn)

        # 装饰线
        ly = y + th + 25
        draw.line([(SIZE*0.35, ly), (SIZE*0.65, ly)], fill=(255,255,255,180), width=2)

        if tagline:
            ft = get_font(24, "light")
            draw_centered_text(draw, tagline, ly+20, ft, (255,255,255,200), SIZE)

        results.append(save_both(img, output_dir, f"gradient_{vname}"))
    return results


# ═══════════════════════════════════════════════════════
#  风格5: 字母标 LETTERMARK
# ═══════════════════════════════════════════════════════
def gen_lettermark(name, mood, palette, output_dir, tagline="", industry="default",
                   english_name=""):
    results = []
    colors = palette["colors"]
    fw = palette["font_weight"]

    initials = english_name[:2].upper() if english_name else name[:2]

    combos = [
        ("深底浅字", colors[0], "#ffffff"),
        ("浅底深字", "#ffffff", colors[0]),
        ("双色组合", "#ffffff", colors[0], colors[1]),
        ("暗底衬线", colors[0] if colors[0].startswith("#") else "#1a1a2e", "#ffffff"),
    ]

    for vname, bg, fg, *rest in combos:
        accent = rest[0] if rest else None
        img = Image.new("RGBA", (SIZE, SIZE), hex_to_rgb(bg) + (255,))
        draw = ImageDraw.Draw(img)

        if accent:
            # 加装饰色块
            block_h = SIZE // 6
            draw.rectangle([0, SIZE-block_h, SIZE, SIZE], fill=hex_to_rgb(accent))

        # 主字母
        try:
            font_main = get_font_en(200, True)
        except Exception:
            font_main = get_font(180, fw)

        tw, th = text_bbox(draw, initials, font_main)
        draw.text(((SIZE-tw)/2, (SIZE-th)/2-40), initials, fill=hex_to_rgb(fg), font=font_main)

        # 装饰短线
        ly = (SIZE+th)/2 + 5
        draw.line([(SIZE*0.38, ly), (SIZE*0.62, ly)], fill=hex_to_rgb(fg), width=2)

        fn = get_font(28, "light")
        draw_centered_text(draw, name, ly+20, fn, hex_to_rgb(fg), SIZE)
        if tagline:
            ft = get_font(20, "light")
            draw_centered_text(draw, tagline, ly+55, ft,
                              hex_to_rgb(accent or fg), SIZE)

        results.append(save_both(img, output_dir, f"lettermark_{vname}"))
    return results


# ═══════════════════════════════════════════════════════
#  风格6: 徽章/盾牌 BADGE
# ═══════════════════════════════════════════════════════
def gen_badge(name, mood, palette, output_dir, tagline="", industry="default"):
    results = []
    colors = palette["colors"]
    fw = palette["font_weight"]
    cx, cy = SIZE//2, SIZE//2

    combos = [
        ("盾牌深色", colors[0], "#ffffff"),
        ("盾牌金色", "#1a1a1a", "#c9a84c"),
        ("圆徽主色", colors[0], "#ffffff"),
        ("圆徽反色", "#ffffff", colors[0]),
    ]

    for vname, bg, fg in combos:
        img = Image.new("RGBA", (SIZE, SIZE), (0,0,0,0))
        draw = ImageDraw.Draw(img)

        if "盾牌" in vname:
            pts = [(cx, cy-260), (cx+190, cy-190), (cx+210, cy-90),
                   (cx+170, cy+60), (cx, cy+190),
                   (cx-170, cy+60), (cx-210, cy-90), (cx-190, cy-190)]
            draw.polygon(pts, fill=hex_to_rgb(bg), outline=hex_to_rgb(fg), width=4)
        else:
            draw.ellipse([cx-250, cy-250, cx+250, cy+250], fill=hex_to_rgb(bg))
            draw.ellipse([cx-230, cy-230, cx+230, cy+230], outline=hex_to_rgb(fg), width=3)
            draw_industry_icon(draw, cx, cy-90, 50, fg, industry)
            f_est = get_font(22, "light")
            draw_centered_text(draw, "EST. 2026", cy-170, f_est, hex_to_rgb(fg), SIZE)

        fn = get_font(64 if len(name) <= 4 else 48, fw)
        draw_centered_text(draw, name, cy-15 if tagline else cy, fn, hex_to_rgb(fg), SIZE)
        if tagline:
            ft = get_font(20, "light")
            draw_centered_text(draw, tagline, cy+60, ft, hex_to_rgb(fg), SIZE)

        results.append(save_both(img, output_dir, f"badge_{vname}"))
    return results


# ═══════════════════════════════════════════════════════
#  风格7: 抽象艺术 ABSTRACT
# ═══════════════════════════════════════════════════════
def gen_abstract(name, mood, palette, output_dir, tagline="", industry="default"):
    """抽象风格：随机几何构成+品牌名"""
    results = []
    colors = palette["colors"]
    fw = palette["font_weight"]
    cx, cy = SIZE//2, SIZE//2

    combos = [
        ("重叠圆", colors[0], colors[1], colors[2] if len(colors) > 2 else colors[1]),
        ("流动线条", colors[0], colors[1], colors[3] if len(colors) > 3 else colors[0]),
        ("色块拼接", colors[0], colors[1], colors[0]),
        ("负空间", colors[0], "#ffffff", colors[2] if len(colors) > 2 else colors[1]),
    ]

    for vname, c1, c2, c3 in combos:
        img = Image.new("RGBA", (SIZE, SIZE), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)

        if "重叠圆" in vname:
            for i, (dx, dy, col) in enumerate([
                (-60, -40, c1), (60, -60, c2), (0, 60, c3)
            ]):
                r = 130
                draw.ellipse([cx+dx-r, cy+dy-r, cx+dx+r, cy+dy+r],
                             fill=hex_to_rgb(col), outline=None)
        elif "流动线条" in vname:
            for i in range(5):
                y0 = cy - 180 + i*80
                pts = [(cx-200, y0)]
                for j in range(8):
                    x = cx-200 + j*50
                    yy = y0 + 30*math.sin(j*0.8 + i)
                    pts.append((x, yy))
                draw.line(pts, fill=hex_to_rgb(c2), width=3+i*2)
        elif "色块" in vname:
            w, h = 160, 180
            for dx, dy, col in [(-80, -90, c1), (80, -60, c2), (0, 70, c3)]:
                draw.rounded_rectangle([cx+dx-w//2, cy+dy-h//2, cx+dx+w//2, cy+dy+h//2],
                                       radius=15, fill=hex_to_rgb(col))
        elif "负空间" in vname:
            draw.rectangle([0, 0, SIZE, SIZE], fill=hex_to_rgb(c1))
            r = 200
            draw.ellipse([cx-r, cy-30-r, cx+r, cy-30+r], fill=(255,255,255,255))
            draw_industry_icon(draw, cx, cy-30, r//2, c3, industry)

        # 文字放在下方
        fn = get_font(64, fw)
        draw_centered_text(draw, name, SIZE*0.78, fn, hex_to_rgb("#1a1a1a"), SIZE)
        if tagline:
            ft = get_font(22, "light")
            draw_centered_text(draw, tagline, SIZE*0.85, ft, hex_to_rgb("#6b7280"), SIZE)

        results.append(save_both(img, output_dir, f"abstract_{vname}"))
    return results


# ═══════════════════════════════════════════════════════
#  风格8: 文字排版 TYPOGRAPHIC
# ═══════════════════════════════════════════════════════
def gen_typographic(name, mood, palette, output_dir, tagline="", industry="default"):
    """纯文字排版：横排/竖排/错位/框线，自适应名称长度"""
    results = []
    colors = palette["colors"]
    fw = palette["font_weight"]
    cx, cy = SIZE//2, SIZE//2

    # 根据名称长度自适应字号
    n = len(name)
    if n <= 2:
        fn_big, fn_mid, char_gap = 160, 100, 180
    elif n <= 3:
        fn_big, fn_mid, char_gap = 120, 90, 140
    elif n <= 4:
        fn_big, fn_mid, char_gap = 96, 80, 110
    elif n <= 6:
        fn_big, fn_mid, char_gap = 72, 64, 90
    else:
        fn_big, fn_mid, char_gap = 56, 48, 70

    combos = [
        ("竖排古典", colors[0], colors[3] if len(colors) > 3 else "#f5f0e8"),
        ("横排左齐", colors[0], "#ffffff"),
        ("框线排版", colors[0], "#ffffff"),
        ("错位排版", colors[0], colors[3] if len(colors) > 3 else "#f5f5f5"),
    ]

    for vname, fg, bg in combos:
        img = Image.new("RGBA", (SIZE, SIZE), hex_to_rgb(bg) + (255,))
        draw = ImageDraw.Draw(img)

        if "竖排" in vname:
            fn = get_font(fn_big, fw)
            y_gap = min(char_gap, (SIZE - 160) // max(n, 1))
            total_h = n * y_gap
            start_y = (SIZE - total_h) / 2
            for i, ch in enumerate(name):
                tw, th = text_bbox(draw, ch, fn)
                draw.text((cx-tw//2, start_y + i*y_gap), ch, fill=hex_to_rgb(fg), font=fn)
            line_x = cx + fn_big//2 + 30
            draw.line([(line_x, start_y), (line_x, start_y+total_h-y_gap//2)],
                      fill=hex_to_rgb(fg), width=2)
            ft = get_font(18, "light")
            draw_centered_text(draw, "— " + mood.upper() + " —", SIZE - 60, ft, hex_to_rgb(fg), SIZE)

        elif "左齐" in vname:
            fn = get_font(fn_mid, fw)
            left = 80
            line_h = text_bbox(draw, "测", fn)[1]
            total_h = n * line_h + (n-1) * 10
            start_y = (SIZE - total_h) / 2
            for i, ch in enumerate(name):
                draw.text((left, start_y + i*(line_h+10)), ch, fill=hex_to_rgb(fg), font=fn)
            draw.line([(left-15, start_y), (left-15, start_y + total_h - line_h)],
                      fill=hex_to_rgb(fg), width=2)

        elif "框线" in vname:
            fn = get_font(fn_mid, fw)
            margin = 100
            draw.rectangle([margin, margin, SIZE-margin, SIZE-margin],
                           outline=hex_to_rgb(fg), width=3)
            cl = 30
            for dx, dy in [(-1,-1), (1,-1), (-1,1), (1,1)]:
                cx_c = cx + dx*(SIZE//2 - margin - cl//2)
                cy_c = cy + dy*(SIZE//2 - margin - cl//2)
                draw.line([(cx_c, cy_c+cl*dy), (cx_c, cy_c)], fill=hex_to_rgb(fg), width=2)
                draw.line([(cx_c, cy_c), (cx_c+cl*dx, cy_c)], fill=hex_to_rgb(fg), width=2)
            draw_centered_text(draw, name, cy-20, fn, hex_to_rgb(fg), SIZE)
            if tagline:
                ft = get_font(24, "light")
                draw_centered_text(draw, tagline, cy+80, ft, hex_to_rgb(fg), SIZE)

        elif "错位" in vname:
            fn = get_font(fn_mid, fw)
            gap = char_gap // 2
            total_w = 0
            cw_list, th_list = [], []
            for ch in name:
                tw, th = text_bbox(draw, ch, fn)
                cw_list.append(tw); th_list.append(th)
                total_w += tw
            total_w += gap * (n - 1)
            if total_w > SIZE - 80:
                scale = (SIZE - 80) / total_w
                fn = get_font(int(fn_mid * scale), fw)
                cw_list = [text_bbox(draw, ch, fn)[0] for ch in name]
                th_list = [text_bbox(draw, ch, fn)[1] for ch in name]
                total_w = sum(cw_list) + gap * (n - 1)
            start_x = (SIZE - total_w) / 2
            for i, ch in enumerate(name):
                y_off = -35 if i % 2 == 0 else 35
                tw, th = cw_list[i], th_list[i]
                draw.text((start_x, cy-th//2+y_off), ch, fill=hex_to_rgb(fg), font=fn)
                start_x += tw + gap

        results.append(save_both(img, output_dir, f"typographic_{vname}"))
    return results


# ═══════════════════════════════════════════════════════
#  主流程
# ═══════════════════════════════════════════════════════
STYLE_MAP = {
    "seal": gen_seal,
    "minimal": gen_minimal,
    "geometric": gen_geometric,
    "gradient": gen_gradient,
    "lettermark": gen_lettermark,
    "badge": gen_badge,
    "abstract": gen_abstract,
    "typographic": gen_typographic,
}

STYLE_DESCRIPTIONS = {
    "seal": "印章徽章 — 传统感、权威感、文化底蕴",
    "minimal": "极简字标 — 现代、干净、专业",
    "geometric": "几何图形 — 结构感、稳定、工业",
    "gradient": "渐变现代 — 科技、时尚、年轻",
    "lettermark": "字母标识 — 国际化、简洁、好记",
    "badge": "徽章盾牌 — 品质保证、经典、信任",
    "abstract": "抽象艺术 — 创意、独特、艺术感",
    "typographic": "文字排版 — 文化感、书卷气、东方美学",
}


def main():
    parser = argparse.ArgumentParser(
        description="Logo Generator v2 — 多调性·多布局·行业适配",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python generate.py --name "星辰科技" --industry tech
  python generate.py --name "绿野餐饮" --industry food --mood nature --tagline "从田间到餐桌"
  python generate.py --name "谊璜贸易" --industry trade --directions 3
  python generate.py --name "山里人" --brief "高端土特产，古朴雅致，不要太现代"
        """
    )
    parser.add_argument("--name", required=True, help="公司/品牌名称")
    parser.add_argument("--en", dest="english", default="", help="英文名")
    parser.add_argument("--tagline", default="", help="口号/副标题")
    parser.add_argument("--industry", default="default", help="行业")
    parser.add_argument("--mood", default=None, help="调性: modern/elegance/bold/playful/tech/vintage/minimal/nature")
    parser.add_argument("--color", default=None, help="自定义主色(#hex)")
    parser.add_argument("--styles", default="all-mood",
                        help="风格,逗号分隔。可选: seal,minimal,geometric,gradient,lettermark,badge,abstract,typographic,all-mood,all")
    parser.add_argument("--directions", type=int, default=None,
                        help="控制风格方向数(对应收费档位: 2=69元, 4=129元, 6=299元)")
    parser.add_argument("--output", default=None, help="输出目录")
    parser.add_argument("--brief", default=None, help="自然语言设计简报")
    parser.add_argument("--list-moods", action="store_true", help="列出所有调性")
    parser.add_argument("--list-styles", action="store_true", help="列出所有风格")
    args = parser.parse_args()

    # 列出信息
    if args.list_moods:
        for k, v in MOOD_PALETTES.items():
            print(f"  {k:12s} — {v['description']}")
        return
    if args.list_styles:
        for k, v in STYLE_DESCRIPTIONS.items():
            print(f"  {k:14s} — {v}")
        return

    # 设计简报模式
    if args.brief:
        mood = _parse_brief(args.brief)
        print(f"\n  📝 简报分析: \"{args.brief}\"")
        print(f"  → 推荐调性: {mood} ({MOOD_PALETTES[mood]['description']})")
        args.mood = mood

    # 调性
    if args.mood is None:
        args.mood = INDUSTRY_MOOD.get(args.industry, "modern")
    base_palette = MOOD_PALETTES.get(args.mood, MOOD_PALETTES["modern"])

    # 自定义色
    if args.color:
        mood_palette = dict(base_palette)
        mood_palette["colors"] = [args.color] + base_palette["colors"][1:]
    else:
        # 根据公司名称哈希轮转调色板 → 不同名称不同配色顺序
        nh = name_hash(args.name)
        mood_palette = dict(base_palette)
        colors = list(base_palette["colors"])
        accs = list(base_palette["accent_colors"])
        shift = nh % len(colors)
        mood_palette["colors"] = colors[shift:] + colors[:shift]
        if accs:
            acc_shift = nh % len(accs)
            mood_palette["accent_colors"] = accs[acc_shift:] + accs[:acc_shift]

    # 风格
    if args.styles == "all-mood":
        # 根据调性选最合适的4个风格
        mood_style_map = {
            "modern": ["minimal", "gradient", "lettermark", "abstract"],
            "elegance": ["seal", "badge", "lettermark", "minimal"],
            "bold": ["badge", "gradient", "abstract", "geometric"],
            "playful": ["gradient", "abstract", "minimal", "geometric"],
            "tech": ["gradient", "abstract", "lettermark", "geometric"],
            "vintage": ["seal", "typographic", "badge", "minimal"],
            "minimal": ["minimal", "lettermark", "geometric", "typographic"],
            "nature": ["geometric", "abstract", "minimal", "badge"],
        }
        styles = mood_style_map.get(args.mood, ["minimal", "gradient", "lettermark", "seal"])
    elif args.styles == "all":
        styles = list(STYLE_MAP.keys())
    else:
        styles = [s.strip() for s in args.styles.split(",")]

    # 按方向数控制 + 名称哈希确定性打乱风格顺序（不同公司名不同排列）
    if args.directions:
        nh = name_hash(args.name)
        # 混合公司哈希+风格名 → 每个名称有独特的风格顺序
        seeded = sorted(styles, key=lambda s: ((nh * 13 + sum(ord(c) for c in s)) % 97))
        styles = seeded[:args.directions]

    # 输出目录
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = "".join(c if c.isascii() and c.isalnum() else "_" for c in args.name)[:20] or "logo"
    out_dir = args.output or os.path.join(
        os.path.dirname(__file__), "output", f"{safe}_{ts}"
    )
    os.makedirs(out_dir, exist_ok=True)

    # 打印头部
    print(f"\n{'='*60}")
    print(f"  🎨 Logo Generator v2")
    print(f"  公司: {args.name}" + (f" ({args.english})" if args.english else ""))
    if args.tagline:
        print(f"  口号: {args.tagline}")
    print(f"  行业: {args.industry}")
    print(f"  调性: {args.mood} — {mood_palette['description']}")
    print(f"  风格: {', '.join(styles)} ({len(styles)*4}版配色)")
    print(f"  输出: {out_dir}")
    print(f"{'='*60}\n")

    # 生成
    generated = 0
    for style in styles:
        if style not in STYLE_MAP:
            print(f"  ⚠ 未知风格: {style}")
            continue
        print(f"  🎨 {style} ({STYLE_DESCRIPTIONS.get(style, '')})")
        func = STYLE_MAP[style]
        files = func(args.name, args.mood, mood_palette, out_dir,
                     args.tagline, args.industry)
        if style == "lettermark":
            args.english  # already used above
        for f in files:
            print(f"     ✓ {os.path.basename(f)}")
        generated += len(files)

    # 汇总
    print(f"\n{'='*60}")
    print(f"  ✅ 完成! {len(styles)}个方向 × 4版 = {generated//2}个方案 ({generated}文件)")
    print(f"  📁 {out_dir}")
    print(f"\n  💡 查看全部: 打开文件夹或运行预览命令")
    print(f"{'='*60}\n")


def _parse_brief(text: str) -> str:
    """简单关键词匹配推荐调性"""
    text = text.lower()
    rules = [
        (["高端", "奢华", "金", "尊贵", "品质", "经典", "传统", "古朴", "雅致", "大气"], "elegance"),
        (["科技", "智能", "数字", "未来", "AI", "数据", "云"], "tech"),
        (["年轻", "活力", "有趣", "好玩", "活泼", "可爱", "清新", "甜"], "playful"),
        (["简约", "干净", "简洁", "现代", "极简", "白", "少"], "minimal"),
        (["大胆", "醒目", "冲击", "力量", "强", "运动", "燃", "爆"], "bold"),
        (["自然", "绿色", "健康", "有机", "环保", "生态", "纯净"], "nature"),
        (["复古", "老", "怀旧", "民国", "年代", "岁月", "沉淀"], "vintage"),
    ]
    for keywords, mood in rules:
        if any(kw in text for kw in keywords):
            return mood
    return "modern"


if __name__ == "__main__":
    main()
