#!/bin/bash
# AI-PPTX 后端启动脚本

echo "🚀 启动 AI-PPTX 后端服务..."

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 未安装，请先安装 Python 3.8+"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖包..."
pip install -r requirements.txt

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "⚙️ 创建环境变量文件..."
    cp env.example .env
    echo "请编辑 .env 文件配置 API 密钥"
fi

# 切换到后端目录
cd backend

# 启动服务
echo "🌟 启动 FastAPI 服务..."
echo "📚 API 文档地址: http://localhost:8000/docs"
echo "🔄 服务健康检查: http://localhost:8000/health"
echo ""

python main.py 