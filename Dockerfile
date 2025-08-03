# AI-PPTX Docker 文件
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建必要的目录
RUN mkdir -p uploads templates static

# 初始化数据库
RUN cd backend && python init_db.py

# 暴露端口
EXPOSE 8000 8501

# 创建启动脚本
RUN echo '#!/bin/bash\n\
cd /app/backend && python main.py &\n\
cd /app/frontend && streamlit run main.py --server.port 8501 --server.address 0.0.0.0\n\
' > /app/start.sh && chmod +x /app/start.sh

# 启动命令
CMD ["/app/start.sh"] 