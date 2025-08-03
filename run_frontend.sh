#!/bin/bash
# AI-PPTX 前端启动脚本

echo "🎨 启动 AI-PPTX 前端界面..."

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

# 切换到前端目录
cd frontend

# 启动 Streamlit 服务
echo "🌟 启动 Streamlit 应用..."
echo "🌐 前端地址: http://localhost:8501"
echo "⚙️ 请确保后端服务已启动 (http://localhost:8000)"
echo ""

streamlit run main.py --server.port 8501 