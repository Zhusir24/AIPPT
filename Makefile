.PHONY: help init install start stop clean backend frontend dev test

# 默认目标
help:
	@echo "AI-PPTX 项目管理工具"
	@echo ""
	@echo "可用命令："
	@echo "  make help      - 显示此帮助信息"
	@echo "  make init      - 初始化项目环境"
	@echo "  make install   - 安装项目依赖"
	@echo "  make start     - 启动前后端服务"
	@echo "  make backend   - 仅启动后端服务"
	@echo "  make frontend  - 仅启动前端服务"
	@echo "  make dev       - 开发模式启动（自动重载）"
	@echo "  make stop      - 停止所有服务"
	@echo "  make clean     - 清理项目文件"
	@echo "  make test      - 运行测试"

# 项目初始化
init:
	@echo "🔧 初始化项目环境..."
	@if [ ! -d ".venv" ]; then \
		echo "📦 创建虚拟环境..."; \
		python3 -m venv .venv; \
	fi
	@echo "✅ 环境初始化完成"
	@echo "💡 请运行 'make install' 安装依赖"

# 安装依赖
install:
	@echo "📥 安装项目依赖..."
	@. .venv/bin/activate && pip install --upgrade pip
	@. .venv/bin/activate && pip install -r requirements.txt
	@if [ ! -f ".env" ] && [ -f "env.example" ]; then \
		echo "⚙️  创建环境变量文件..."; \
		cp env.example .env; \
		echo "💡 请编辑 .env 文件配置您的 AI API 密钥"; \
	fi
	@echo "✅ 依赖安装完成"

# 启动所有服务
start:
	@echo "🚀 启动前后端服务..."
	@make backend &
	@sleep 5
	@make frontend &
	@echo "🎉 服务启动完成！"
	@echo "🌐 前端地址: http://localhost:8501"
	@echo "📚 后端API: http://localhost:8000/docs"
	@echo "💡 使用 'make stop' 停止服务"

# 启动后端服务
backend:
	@echo "🔧 启动后端服务..."
	@. .venv/bin/activate && cd backend && python main.py

# 启动前端服务
frontend:
	@echo "🎨 启动前端服务..."
	@. .venv/bin/activate && cd frontend && streamlit run main.py --server.port 8501

# 开发模式
dev:
	@echo "🛠️  开发模式启动..."
	@make backend &
	@sleep 3
	@make frontend &
	@echo "🎯 开发模式启动完成！"

# 停止服务
stop:
	@echo "🛑 停止所有服务..."
	@pkill -f "python.*main.py" 2>/dev/null || echo "后端服务已停止"
	@pkill -f "streamlit.*main.py" 2>/dev/null || echo "前端服务已停止"
	@echo "✅ 服务已停止"

# 清理项目
clean:
	@echo "🧹 清理项目文件..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name "*.pyo" -delete 2>/dev/null || true
	@find . -name ".DS_Store" -delete 2>/dev/null || true
	@echo "✅ 清理完成"

# 运行测试
test:
	@echo "🧪 运行项目测试..."
	@. .venv/bin/activate && python -m pytest test/ -v
	@echo "✅ 测试完成"

# 健康检查
health:
	@echo "🏥 服务健康检查..."
	@curl -s http://localhost:8000/health > /dev/null && echo "✅ 后端服务正常" || echo "❌ 后端服务异常"
	@curl -s http://localhost:8501 > /dev/null && echo "✅ 前端服务正常" || echo "❌ 前端服务异常"

# 查看日志
logs:
	@echo "📋 查看服务进程..."
	@ps aux | grep -E "(python.*main.py|streamlit)" | grep -v grep || echo "无运行中的服务"

# 重启服务
restart: stop start

# 更新依赖
update:
	@echo "🔄 更新项目依赖..."
	@. .venv/bin/activate && pip install --upgrade -r requirements.txt
	@echo "✅ 依赖更新完成"