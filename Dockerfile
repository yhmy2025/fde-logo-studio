FROM python:3.11-slim

WORKDIR /app

# 安装中文字体（Pillow需要）
RUN apt-get update && apt-get install -y \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 创建字体符号链接
RUN mkdir -p /usr/share/fonts/truetype/custom && \
    echo "Fonts available: $(ls /usr/share/fonts/)"

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "fde_studio.py", \
    "--server.port=8501", \
    "--server.address=0.0.0.0", \
    "--server.headless=true", \
    "--browser.gatherUsageStats=false"]
