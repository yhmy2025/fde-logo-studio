"""
FDE Logo Studio v3 — 设计组合引擎Web界面
Streamlit前端 + generate.py v3核心引擎
"""
import streamlit as st
import sys, os, subprocess, glob, base64, zipfile, io, time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from datetime import datetime
from pathlib import Path

st.set_page_config(
    page_title="FDE Logo Studio v3",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1a1a2e; margin-bottom: 0; }
    .sub-header { font-size: 1rem; color: #666; margin-bottom: 1.5rem; }
    .price-tag { 
        display: inline-block; background: #1a1a2e; color: white; 
        padding: 4px 12px; border-radius: 20px; font-size: 0.85rem;
    }
    .stButton > button {
        width: 100%; border-radius: 8px; font-weight: 600;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; border: none; padding: 12px;
    }
</style>
""", unsafe_allow_html=True)

ENGINE = r"D:\Tools\logo-generator\generate.py"
OUTPUT_BASE = r"D:\Tools\logo-generator\output"

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<p class="main-header">🎨 FDE Logo Studio v3</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">设计组合引擎 · 12种构图 · 30+几何元素 · 15种图案 · 14行业适配</p>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div style="text-align:right;padding-top:20px"><span class="price-tag">v3.0 组合引擎</span></div>', unsafe_allow_html=True)

st.divider()

with st.sidebar:
    st.markdown("### ⚙️ 品牌信息")
    brand_name = st.text_input("品牌名称", placeholder="例：谊璜贸易", value="")

    input_mode = st.radio("输入模式", ["🎯 快速配置", "📝 设计简报", "📦 按数量"], horizontal=False)

    if input_mode == "🎯 快速配置":
        industry = st.selectbox("行业", [
            "trade(贸易)", "tech(科技)", "food(食品)", "finance(金融)",
            "manufacturing(制造)", "healthcare(医疗)", "education(教育)",
            "realestate(房地产)", "design(设计)", "sports(运动)",
            "culture(文化)", "beauty(美妆)", "legal(法律)", "media(传媒)"
        ])
        industry_code = industry.split("(")[1].replace(")", "") if "(" in industry else "tech"

        mood = st.selectbox("调性", [
            "modern(现代简约)", "elegance(优雅高端)", "bold(大胆醒目)",
            "playful(活泼有趣)", "tech(科技感)", "vintage(复古经典)",
            "minimal(极致极简)", "nature(自然有机)"
        ])
        mood_code = mood.split("(")[1].replace(")", "") if "(" in mood else "modern"

        count = st.slider("生成数量", 4, 16, 8, help="每个都是独立组合的设计")
        tagline = st.text_input("口号/副标题（可选）", placeholder="例：品质至上 诚信为本")
        brief = ""

    elif input_mode == "📝 设计简报":
        brief = st.text_area("描述你的品牌风格",
            placeholder="例：高端土特产品牌，主打古朴雅致，不要太现代，偏中国传统风格。",
            height=120)
        industry_code = "trade"
        mood_code = ""
        count = 8
        tagline = st.text_input("口号/副标题（可选）")

    else:  # 按数量
        tier = st.radio("选择数量", [
            "💰 体验版 ¥69 — 6个设计",
            "💎 标准版 ¥129 — 9个设计",
            "👑 进阶版 ¥299 — 12个全构图"
        ])
        if "6个" in tier: count = 6
        elif "9个" in tier: count = 9
        else: count = 12
        industry_code = st.selectbox("行业", ["trade", "tech", "food", "finance", "manufacturing", "healthcare"],
            format_func=lambda x: {"trade":"贸易","tech":"科技","food":"食品","finance":"金融","manufacturing":"制造","healthcare":"医疗"}.get(x,x))
        mood_code = st.selectbox("调性", ["modern", "elegance", "bold", "tech", "minimal"])
        brief = ""
        tagline = st.text_input("口号/副标题（可选）")

    st.divider()
    generate_btn = st.button("🚀 开始生成", use_container_width=True, type="primary")

tab1, tab2, tab3 = st.tabs(["🎨 生成结果", "📊 方案对比", "📖 使用指南"])

with tab3:
    st.markdown("""
    ### 🎯 v3 设计组合引擎 vs 传统模板

    | | 传统模板工具 | FDE Logo Studio v3 |
    |---|---|---|
    | 设计方式 | 固定模板换色换字 | 12种构图 × 30+几何 × 15种图案 |
    | 同行业不同名 | 一样的设计 | **完全不同** |
    | 输出多样性 | 4-8种颜色变体 | **数千种组合可能性** |
    | 行业感知 | 无 | 形状/图案/符号自动匹配 |

    ### 🏗️ 12种构图框架

    | # | 构图 | 特点 |
    |---|------|------|
    | 1 | 中心图形 | 几何标识+品牌名 |
    | 2 | 左右分区 | 图形左·文字右 |
    | 3 | 圆形徽章 | 多层环状徽记 |
    | 4 | 对角分割 | 斜切分区·强对比 |
    | 5 | 边框框架 | 四角L形框·高级感 |
    | 6 | 几何图案 | 点阵/辐射/弧线背景 |
    | 7 | 环状徽章 | 商标级徽章·多层认证风 |
    | 8 | 文字焦点 | 文字本身就是Logo |
    | 9 | 图层重叠 | 多色叠层·现代感 |
    | 10 | 线艺抽象 | 波浪线·艺术感 |
    | 11 | 负空间 | 色彩分区·镂空效果 |
    | 12 | 模块网格 | n×n网格·极客感 |

    ### 💡 核心原理

    公司名→哈希值→决定：图形形状/颜色顺序/图案类型/布局参数。
    **同一名称永远生成相同序列，不同名称完全不同。**
    """)

if generate_btn:
    if not brand_name:
        st.error("请输入品牌名称")
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(OUTPUT_BASE, f"{brand_name}_{timestamp}")

        cmd_list = [
            sys.executable, ENGINE,
            "--name", brand_name,
            "--industry", industry_code,
            "--count", str(count),
            "--output", output_dir,
        ]
        if mood_code:
            cmd_list.extend(["--mood", mood_code])
        if tagline:
            cmd_list.extend(["--tagline", tagline])
        if brief:
            cmd_list.extend(["--brief", brief])

        progress_text = st.empty()
        progress_bar = st.progress(0)
        status = st.empty()

        try:
            progress_text.text(f"正在为 {brand_name} 组合设计...")
            progress_bar.progress(20)
            status.text("⏳ 引擎运行中...")

            result = subprocess.run(cmd_list, capture_output=True, text=True,
                                  encoding='utf-8', timeout=120)
            progress_bar.progress(80)
            status.text("✅ 生成完成！")

            if result.returncode == 0:
                progress_bar.progress(100)

                compositions = ["中心图形","左右分区","圆形徽章","对角分割",
                               "边框框架","几何图案","环状徽章","文字焦点",
                               "图层重叠","线艺抽象","负空间","模块网格"]

                progress_text.text(
                    f"✅ {brand_name} · {count}个独立设计 · {count*2}张文件"
                    f" · 覆盖 {min(count,12)} 种构图")

                with tab1:
                    st.success(f"生成成功！输出目录：`{output_dir}`")

                    png_files = glob.glob(os.path.join(output_dir, "*.png"))
                    main_files = sorted([f for f in png_files if "-avatar" not in f])

                    if main_files:
                        st.markdown(f"### 🖼️ {count}个独立设计")

                        cols_per_row = 3
                        for i in range(0, len(main_files), cols_per_row):
                            cols = st.columns(cols_per_row)
                            for j in range(cols_per_row):
                                idx = i + j
                                if idx < len(main_files):
                                    f = main_files[idx]
                                    fname = os.path.basename(f).replace(".png", "")
                                    comp = compositions[idx % 12] if idx < 12 else ""
                                    caption = f"{fname} · {comp}"
                                    try:
                                        cols[j].image(f, caption=caption,
                                                    use_container_width=True)
                                    except:
                                        cols[j].text(fname)

                        st.divider()
                        st.markdown("### 📦 一键下载")
                        zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                            for f in main_files:
                                zf.write(f, os.path.basename(f))
                        zip_buffer.seek(0)

                        st.download_button(
                            label=f"⬇️ 下载全部 {len(main_files)} 张方案 (ZIP)",
                            data=zip_buffer,
                            file_name=f"{brand_name}_Logo方案_{timestamp}.zip",
                            mime="application/zip",
                            use_container_width=True
                        )

                    with tab2:
                        if len(main_files) >= 2:
                            st.markdown("### 并排对比")
                            for i in range(0, len(main_files), 2):
                                c1, c2 = st.columns(2)
                                with c1:
                                    if i < len(main_files):
                                        comp1 = compositions[i%12] if i<12 else ""
                                        st.image(main_files[i],
                                               caption=f"设计{i+1} · {comp1}",
                                               use_container_width=True)
                                with c2:
                                    if i+1 < len(main_files):
                                        comp2 = compositions[(i+1)%12] if i+1<12 else ""
                                        st.image(main_files[i+1],
                                               caption=f"设计{i+2} · {comp2}",
                                               use_container_width=True)
            else:
                st.error(f"生成失败\n```\n{result.stderr}\n{result.stdout}\n```")

        except subprocess.TimeoutExpired:
            st.error("生成超时（120秒），请减少数量重试")
        except Exception as e:
            st.error(f"出错：{e}")

st.divider()
c1, c2, c3 = st.columns(3)
with c1: st.metric("构图系统", "12", "种框架")
with c2: st.metric("组合可能", "数千", "种/品牌")
with c3: st.metric("适配行业", "14", "个行业")
