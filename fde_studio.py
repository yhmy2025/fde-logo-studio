"""
FDE Logo Studio v4 — 多品类设计引擎Web界面
Streamlit前端 + generate.py v4核心
"""
import streamlit as st
import sys, os, subprocess, glob, base64, zipfile, io

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from datetime import datetime

st.set_page_config(page_title="FDE Logo Studio v4", page_icon="🎨", layout="wide")

st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1a1a2e; margin-bottom: 0; }
    .sub-header { font-size: 1rem; color: #666; margin-bottom: 1.5rem; }
    .price-tag { display: inline-block; background: #1a1a2e; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; }
    .stButton > button { width: 100%; border-radius: 8px; font-weight: 600; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 12px; }
</style>
""", unsafe_allow_html=True)

ENGINE = r"D:\Tools\logo-generator\generate.py"
OUTPUT_BASE = r"D:\Tools\logo-generator\output"

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<p class="main-header">🎨 FDE Logo Studio v4</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">多品类设计引擎 · 7大品类 · 15行业 · 45种图标</p>', unsafe_allow_html=True)
with col2:
    st.markdown('<div style="text-align:right;padding-top:20px"><span class="price-tag">v4.0 多品类</span></div>', unsafe_allow_html=True)

st.divider()

with st.sidebar:
    st.markdown("### ⚙️ 品牌信息")
    brand_name = st.text_input("品牌名称", placeholder="例：谊璜贸易")

    input_mode = st.radio("输入模式", ["🎯 快速配置", "📝 设计简报", "📦 按数量"], horizontal=False)

    INDUSTRIES = { "trade":"贸易", "tech":"科技", "food":"食品", "finance":"金融",
        "manufacturing":"制造", "health":"医疗", "education":"教育",
        "realestate":"房地产", "design":"设计", "sports":"运动",
        "culture":"文化", "beauty":"美妆", "law":"法律", "media":"传媒", "construction":"建筑" }
    MOODS = { "modern":"现代简约", "elegance":"优雅高端", "bold":"大胆醒目",
        "playful":"活泼有趣", "tech":"科技感", "vintage":"复古经典",
        "minimal":"极致极简", "nature":"自然有机" }

    if input_mode == "🎯 快速配置":
        industry_code = st.selectbox("行业", list(INDUSTRIES.keys()),
            format_func=lambda x: f"{x}({INDUSTRIES[x]})")
        mood_code = st.selectbox("调性", list(MOODS.keys()),
            format_func=lambda x: f"{x}({MOODS[x]})")
        count = st.slider("生成数量", 4, 14, 7)
        tagline = st.text_input("口号/副标题（可选）")
        brief = ""
    elif input_mode == "📝 设计简报":
        brief = st.text_area("描述品牌风格", placeholder="例：高端土特产品牌，主打古朴雅致...", height=120)
        industry_code = st.selectbox("行业", list(INDUSTRIES.keys()),
            format_func=lambda x: INDUSTRIES[x])
        mood_code = st.selectbox("调性", list(MOODS.keys()),
            format_func=lambda x: MOODS[x])
        count = st.slider("生成数量", 4, 14, 7)
        tagline = st.text_input("口号/副标题（可选）")
    else:
        tier = st.radio("选择数量", [
            "💰 体验版 ¥69 — 4个品类", "💎 标准版 ¥129 — 7个全品类", "👑 进阶版 ¥299 — 14个深度"
        ])
        if "4个" in tier: count = 4
        elif "7个" in tier: count = 7
        else: count = 14
        industry_code = st.selectbox("行业", list(INDUSTRIES.keys()),
            format_func=lambda x: INDUSTRIES[x])
        mood_code = st.selectbox("调性", list(MOODS.keys()),
            format_func=lambda x: MOODS[x])
        brief = ""; tagline = st.text_input("口号/副标题（可选）")

    st.divider()
    generate_btn = st.button("🚀 生成Logo", use_container_width=True, type="primary")

tab1, tab2 = st.tabs(["🎨 生成结果", "📖 引擎说明"])

with tab2:
    st.markdown("""
    ### 🎯 v4 多品类引擎

    | | v3 | v4 |
    |---|---|---|
    | 设计方式 | 1套模具×12排列 | **7个独立视觉引擎** |
    | 异名同位置 | 可能类似 | **完全不同品类** |
    | 品类终点 | 全走几何范 | 字标/字母/图形/抽象/徽章/组合/负空间 |

    ### 🏗️ 7大品类

    | # | 品类 | 视觉 | 参考 |
    |---|------|------|------|
    | 1 | 纯文字标 | 字体即Logo | Google, Coca-Cola |
    | 2 | 字母标 | 字母艺术化 | IBM, HBO |
    | 3 | 图形标 | 具象图标为主 | Apple, Twitter |
    | 4 | 抽象标 | 纯几何构成 | Nike, Pepsi |
    | 5 | 徽章标 | 图文被包裹 | Starbucks |
    | 6 | 组合标 | 图标+文字 | Adidas |
    | 7 | 负空间标 | 镂空/分区 | FedEx |

    ### 💡 核心机制
    名称→SHA256→决定主品类(7选1)→每个设计在所有品类间轮转。
    **同一名称永远相同序列，不同名称完全不同起点。**
    """)

if generate_btn:
    if not brand_name:
        st.error("请输入品牌名称")
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(OUTPUT_BASE, f"{brand_name}_{timestamp}")
        cmd_list = [
            sys.executable, ENGINE, "--name", brand_name,
            "--industry", industry_code, "--count", str(count),
            "--output", output_dir,
        ]
        if mood_code: cmd_list.extend(["--mood", mood_code])
        if tagline: cmd_list.extend(["--tagline", tagline])
        if brief: cmd_list.extend(["--brief", brief])

        pb = st.progress(0)
        st.text(f"⏳ 正在为 {brand_name} 生成 {count} 个品类设计...")
        pb.progress(20)

        try:
            result = subprocess.run(cmd_list, capture_output=True, text=True,
                                  encoding='utf-8', timeout=120)
            pb.progress(80)

            if result.returncode == 0:
                pb.progress(100)
                type_names = ["纯文字标","字母标","图形标","抽象标","徽章标","组合标","负空间标"]
                png_files = glob.glob(os.path.join(output_dir, "*.png"))
                main_files = sorted([f for f in png_files if "-avatar" not in f])

                with tab1:
                    st.success(f"✅ {brand_name} · {len(main_files)}个品类设计 · {os.path.basename(output_dir)}")
                    if main_files:
                        cols = st.columns(min(3, len(main_files)))
                        for i, f in enumerate(main_files[:9]):
                            fname = os.path.basename(f).replace(".png","")
                            comp = type_names[i%7]
                            cols[i%3].image(f, caption=f"{fname} · {comp}", use_container_width=True)

                        if len(main_files) > 0:
                            st.divider()
                            zip_buffer = io.BytesIO()
                            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                                for f in main_files:
                                    zf.write(f, os.path.basename(f))
                            zip_buffer.seek(0)
                            st.download_button(
                                label=f"⬇️ 下载 {len(main_files)} 个方案 (ZIP)",
                                data=zip_buffer,
                                file_name=f"{brand_name}_Logo_{timestamp}.zip",
                                mime="application/zip", use_container_width=True)
            else:
                st.error(f"生成失败\n```\n{result.stderr}\n```")
        except subprocess.TimeoutExpired:
            st.error("操作超时")
        except Exception as e:
            st.error(f"出错：{e}")

st.divider()
c1, c2, c3 = st.columns(3)
with c1: st.metric("视觉品类", "7", "独立引擎")
with c2: st.metric("行业图标", "45", "种变体")
with c3: st.metric("适配行业", "15", "个")
