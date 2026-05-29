"""
FDE Logo Studio — Web界面版Logo生成器
Streamlit前端 + generate.py核心引擎
"""
import streamlit as st
import sys, os, subprocess, glob, base64, zipfile, io, time
from datetime import datetime
from pathlib import Path

# ── 页面配置 ──
st.set_page_config(
    page_title="FDE Logo Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ──
st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1a1a2e; margin-bottom: 0; }
    .sub-header { font-size: 1rem; color: #666; margin-bottom: 1.5rem; }
    .card { 
        background: #f8f9fa; border-radius: 12px; padding: 20px; 
        margin: 10px 0; border: 1px solid #e9ecef;
    }
    .card h3 { margin-top: 0; color: #1a1a2e; }
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

# ── 引擎路径 ──
ENGINE = r"D:\Tools\logo-generator\generate.py"
OUTPUT_BASE = r"D:\Tools\logo-generator\output"

# ── 标题 ──
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<p class="main-header">🎨 FDE Logo Studio</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI驱动的品牌Logo生成器 · 8种风格 · 14个行业 · 32版方案</p>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div style="text-align:right;padding-top:20px"><span class="price-tag">v2.0 FDE Edition</span></div>', unsafe_allow_html=True)

st.divider()

# ── 侧边栏：输入区 ──
with st.sidebar:
    st.markdown("### ⚙️ 品牌信息")
    brand_name = st.text_input("品牌名称", placeholder="例：谊璜贸易", value="")
    
    # 输入模式
    input_mode = st.radio("输入模式", ["🎯 快速配置", "📝 设计简报", "📦 按档位"], horizontal=False)
    
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
        
        style_options = st.multiselect("风格方向", 
            ["seal(印章)", "badge(徽章)", "minimal(极简)", "geometric(几何)", 
             "gradient(渐变)", "lettermark(字母标)", "abstract(抽象)", "typographic(排版)"],
            default=["seal(印章)", "badge(徽章)", "gradient(渐变)", "abstract(抽象)"]
        )
        styles_code = ",".join([s.split("(")[1].replace(")", "") for s in style_options]) if style_options else "seal,badge,gradient"
        
        tagline = st.text_input("口号/副标题（可选）", placeholder="例：品质至上 诚信为本")
        
        num_directions = len(style_options) if style_options else 4
        
    elif input_mode == "📝 设计简报":
        brief = st.text_area("描述你的品牌风格", 
            placeholder="例：高端土特产品牌，主打古朴雅致，不要太现代，偏中国传统风格。目标客户30-50岁。",
            height=120)
        industry_code = "trade"
        mood_code = ""
        styles_code = "seal,badge,gradient,abstract"
        tagline = st.text_input("口号/副标题（可选）")
        num_directions = 4
        
    else:  # 按档位
        tier = st.radio("选择档位", [
            "💰 体验版 ¥69 — 2种方向", 
            "💎 标准版 ¥129 — 4种方向",
            "👑 进阶版 ¥299 — 8种全方向"
        ])
        if "2种" in tier:
            num_directions = 2
        elif "4种" in tier:
            num_directions = 4
        else:
            num_directions = 8
        industry_code = st.selectbox("行业", ["trade", "tech", "food", "finance", "manufacturing", "healthcare"]) 
        mood_code = st.selectbox("调性", ["modern", "elegance", "bold", "tech", "minimal"])
        styles_code = "seal,badge,gradient,abstract,minimal,geometric,lettermark,typographic"
        tagline = st.text_input("口号/副标题（可选）")
    
    st.divider()
    generate_btn = st.button("🚀 开始生成", use_container_width=True, type="primary")

# ── 主区域 ──
tab1, tab2, tab3 = st.tabs(["🎨 生成结果", "📊 方案对比", "📖 使用指南"])

with tab3:
    st.markdown("""
    ### 🎯 三种输入模式
    
    | 模式 | 适用场景 | 说明 |
    |------|----------|------|
    | 快速配置 | 知道品牌风格 | 手动选择行业、调性、风格 |
    | 设计简报 | 客户给了需求描述 | 用自然语言描述，AI自动匹配 |
    | 按档位 | 确定预算 | 2/4/8方向对应69/129/299三档 |
    
    ### 🎨 8种风格调性
    
    modern(现代) · elegance(优雅) · bold(大胆) · playful(活泼) · tech(科技) · vintage(复古) · minimal(极简) · nature(自然)
    
    ### 🏭 14个行业适配
    
    贸易/科技/食品/金融/制造/医疗/教育/房地产/设计/运动/文化/美妆/法律/传媒
    
    ### 💡 FDE核心价值
    
    本工具是FDE（前沿部署工程师）能力的典型案例：
    - 从零设计基础到32版/品牌 → AI赋能非设计人员
    - CLI+Web双界面 → 适应不同交付场景
    - 三档定价 → 产品化思维
    """)

# ── 生成逻辑 ──
if generate_btn:
    if not brand_name:
        st.error("请输入品牌名称")
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(OUTPUT_BASE, f"{brand_name}_{timestamp}")
        
        # 构建命令
        cmd_parts = [
            "python", ENGINE,
            "--name", f'"{brand_name}"',
            "--industry", industry_code,
            "--styles", styles_code,
            "--directions", str(num_directions),
            "--output", output_dir,
        ]
        if mood_code:
            cmd_parts.extend(["--mood", mood_code])
        if tagline:
            cmd_parts.extend(["--tagline", f'"{tagline}"'])
        if input_mode == "📝 设计简报" and brief:
            cmd_parts.extend(["--brief", f'"{brief}"'])
        
        cmd = " ".join(cmd_parts)
        
        progress_text = st.empty()
        progress_bar = st.progress(0)
        status = st.empty()
        
        try:
            progress_text.text(f"正在生成 {brand_name} 的Logo方案...")
            progress_bar.progress(20)
            status.text("⏳ 引擎启动中...")
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
            progress_bar.progress(80)
            status.text("✅ 生成完成！")
            
            if result.returncode == 0:
                progress_bar.progress(100)
                progress_text.text(f"✅ {brand_name} · {num_directions}种方向 · {num_directions*4}张成品")
                
                # 扫描输出文件
                with tab1:
                    st.success(f"生成成功！输出目录：`{output_dir}`")
                    
                    png_files = glob.glob(os.path.join(output_dir, "*.png"))
                    # 过滤掉avatar
                    main_files = [f for f in png_files if "-avatar" not in f]
                    
                    if main_files:
                        st.markdown(f"### 🖼️ 查看方案（共{len(main_files)}张）")
                        
                        cols_per_row = 4
                        for i in range(0, len(main_files), cols_per_row):
                            cols = st.columns(cols_per_row)
                            for j in range(cols_per_row):
                                idx = i + j
                                if idx < len(main_files):
                                    f = main_files[idx]
                                    fname = os.path.basename(f).replace(".png", "")
                                    try:
                                        cols[j].image(f, caption=fname, use_container_width=True)
                                    except:
                                        cols[j].text(fname)
                        
                        # 打包下载
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
                    
                    # 方案对比视图
                    with tab2:
                        if len(main_files) >= 2:
                            st.markdown("### 并排对比")
                            for i in range(0, len(main_files), 2):
                                c1, c2 = st.columns(2)
                                with c1:
                                    if i < len(main_files):
                                        fname = os.path.basename(main_files[i])
                                        st.image(main_files[i], caption=fname, use_container_width=True)
                                with c2:
                                    if i+1 < len(main_files):
                                        fname = os.path.basename(main_files[i+1])
                                        st.image(main_files[i+1], caption=fname, use_container_width=True)
            else:
                st.error(f"生成失败\n```\n{result.stderr}\n{result.stdout}\n```")
                
        except subprocess.TimeoutExpired:
            st.error("生成超时（120秒），请减少方向数重试")
        except Exception as e:
            st.error(f"出错：{e}")

# ── 底部 ──
st.divider()
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("可用风格", "8", "种调性系统")
with c2:
    st.metric("适配行业", "14", "个行业")
with c3:
    st.metric("最大方案", "32", "版/品牌")
