# FDE Logo Studio 🎨

> **FDE（前沿部署工程师）典型案例** | AI驱动的品牌Logo生成器  
> 8种风格 · 14个行业 · 32版方案/品牌名

---

## 🎯 项目背景

**客户问题：** 中小企业/初创公司需要Logo，但请设计师贵（¥500-5000+），在线工具模板千篇一律，无法体现品牌独特性。

**FDE方案：** 不是把AI模型交给客户自己摸索，而是把AI能力"嵌入"成一个零门槛的Web工具——客户输入品牌名，3秒出8种风格方案。

**价值量化：**
- 设计成本：¥500-5000 → ¥69-299
- 交付速度：3-7天 → 3秒
- 方案多样性：1-3版 → 最多32版/品牌

---

## 🚀 快速开始

### 方式一：Web界面（推荐）

```bash
pip install -r requirements.txt
streamlit run fde_studio.py
```

打开 http://localhost:8501 即可使用。

### 方式二：命令行

```bash
python generate.py --name "你的品牌名" --industry tech --styles seal,badge,gradient --mood modern
```

### 方式三：一键设计简报

```bash
python generate.py --name "谊璜贸易" --brief "高端土特产品牌，主营陈皮、凉果，要有中国传统韵味但不老气"
```

---

## 🎨 8种调性系统

| 调性 | 适合行业 | 视觉特征 |
|------|----------|----------|
| modern | 科技/金融/设计 | 几何线条、冷色调、无衬线 |
| elegance | 珠宝/高端零售/法律 | 衬线体、金/黑色系、留白多 |
| bold | 运动/媒体/电商 | 大色块、高对比度、粗字重 |
| playful | 食品/母婴/教育 | 圆角、暖色调、活泼字体 |
| tech | AI/SaaS/硬件 | 蓝紫渐变、数据感、发光效果 |
| vintage | 餐饮/文化/手工艺 | 做旧纹理、印章风格、暖黄 |
| minimal | 设计工作室/咨询 | 极致留白、单色、细线条 |
| nature | 农业/环保/健康 | 大地色、有机形状、枝叶元素 |

---

## 🏭 14个行业适配

贸易 · 科技 · 食品 · 金融 · 制造 · 医疗 · 教育 · 房地产 · 设计 · 运动 · 文化 · 美妆 · 法律 · 传媒

---

## 📦 项目结构

```
logo-generator/
├── generate.py          # 核心生成引擎（35KB/550+行）
├── fde_studio.py        # Streamlit Web界面
├── make_collage_v3.py   # 朋友圈方案对比拼图
├── treehole_cover.py    # 小红书心理树洞号封面
├── xhs_cover.py         # 小红书号封面
├── requirements.txt     # Python依赖
├── Dockerfile           # Docker容器化
├── docker-compose.yml   # 一键部署
└── output/              # 生成结果目录（gitignore）
```

---

## 💰 三档定价

| 档位 | 价格 | 方向数 | 方案数 | 适合 |
|------|------|--------|--------|------|
| 体验版 | ¥69 | 2 | 8 | 试试看 |
| 标准版 | ¥129 | 4 | 16 | 认真选 |
| 进阶版 | ¥299 | 8 | 32 | 全方位对比 |

---

## 🔧 技术栈

- **核心引擎:** Python 3.11+ / Pillow
- **Web前端:** Streamlit 1.58
- **容器化:** Docker (准备中)
- **部署:** 单机/局域网/Streamlit Cloud

---

## 🧭 FDE能力展示

本项目是**前沿部署工程师（Forward Deployed Engineer）**能力的完整演示：

1. **需求发现：** 从闲鱼客户反馈中发现Logo设计需求
2. **快速原型：** 一周搭建CLI版本（v1）
3. **迭代优化：** 从4种风格扩展到8种调性系统（v2）
4. **客户界面：** Streamlit Web UI，零门槛使用
5. **产品化：** 三档定价、一键下载、方案对比
6. **行业深耕：** 14个行业自动化适配

---

*Built by yhmy2025 | FDE Portfolio Case #1*
