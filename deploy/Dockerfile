FROM python:3.10-slim

WORKDIR /app

# 安装最小系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 升级 pip
RUN pip install --no-cache-dir --upgrade pip

# 复制依赖文件
COPY requirements.txt .

# 分步安装（确保核心包先安装）
RUN pip install --no-cache-dir numpy==1.24.3 && \
    pip install --no-cache-dir pandas==1.5.3 && \
    pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8050

# 环境变量
ENV PYTHONUNBUFFERED=1
ENV PORT=8050

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:8050", "--workers", "2", "app:server"]
