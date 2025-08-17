#!/bin/bash

# AI-PPTX HTML前端启动脚本
# 启动纯HTML版本的前端界面

echo "🚀 启动 AI-PPTX HTML 前端..."

# 检查是否在项目根目录
if [ ! -f "run_frontend_html.py" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 检查前端HTML目录是否存在
if [ ! -d "frontend_html" ]; then
    echo "❌ 错误：frontend_html 目录不存在"
    echo "请确保已经创建了HTML前端文件"
    exit 1
fi

# 检查Python是否可用
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 python3"
    echo "请安装 Python 3"
    exit 1
fi

echo "📂 检查前端文件..."
echo "✅ HTML前端文件存在"

echo "🌐 前端将在 http://localhost:8080 启动"
echo "🔗 请确保后端服务运行在 http://localhost:8000"
echo ""

# 启动HTML前端服务器
python3 run_frontend_html.py

echo "✅ HTML前端已关闭"
