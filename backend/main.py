"""
AI-PPTX 后端主入口文件
基于 FastAPI 构建的 API 服务
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import os
import time
from pathlib import Path

from app.core.config import settings
from app.core.logger import setup_logger, get_logger
from app.api.v1.api import api_router
from app.core.database import create_tables

# 初始化日志系统
setup_logger()
logger = get_logger(__name__)

# 创建 FastAPI 应用实例
logger.info("🚀 开始初始化 FastAPI 应用")
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-PPTX API 服务",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)
logger.info("✅ FastAPI 应用实例创建成功")

# 添加请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录所有HTTP请求的日志"""
    start_time = time.time()
    
    # 记录请求开始
    logger.info(f"📨 收到请求: {request.method} {request.url}")
    logger.debug(f"📋 请求头: {dict(request.headers)}")
    
    # 记录客户端信息
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    logger.debug(f"🌐 客户端 IP: {client_ip}")
    logger.debug(f"🖥️ User-Agent: {user_agent}")
    
    try:
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 记录响应
        logger.info(f"📤 响应完成: {request.method} {request.url} - 状态码: {response.status_code} - 耗时: {process_time:.3f}s")
        
        if response.status_code >= 400:
            logger.warning(f"⚠️ 请求异常: {request.method} {request.url} - 状态码: {response.status_code}")
        
        # 添加处理时间到响应头
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"❌ 请求处理异常: {request.method} {request.url} - 错误: {str(e)} - 耗时: {process_time:.3f}s")
        raise

# 配置 CORS
logger.info("🔧 配置 CORS 中间件")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该配置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("✅ CORS 中间件配置完成")

# 挂载静态文件目录
logger.info("📂 开始挂载静态文件目录")
if os.path.exists("../static"):
    app.mount("/static", StaticFiles(directory="../static"), name="static")
    logger.info("✅ 挂载 static 目录成功: /static")
else:
    logger.warning("⚠️ static 目录不存在，跳过挂载")

if os.path.exists("../uploads"):
    app.mount("/uploads", StaticFiles(directory="../uploads"), name="uploads")
    logger.info("✅ 挂载 uploads 目录成功: /uploads")
else:
    logger.warning("⚠️ uploads 目录不存在，跳过挂载")

if os.path.exists("../templates"):
    app.mount("/templates", StaticFiles(directory="../templates"), name="templates")
    logger.info("✅ 挂载 templates 目录成功: /templates")
else:
    logger.warning("⚠️ templates 目录不存在，跳过挂载")

# 包含 API 路由
logger.info("🛣️ 开始注册 API 路由")
app.include_router(api_router, prefix=settings.API_V1_STR)
logger.info(f"✅ API 路由注册成功: {settings.API_V1_STR}")

@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    logger.info("🔧 开始应用启动初始化")
    
    # 创建数据库表
    logger.info("💾 开始初始化数据库")
    try:
        create_tables()
        logger.info("✅ 数据库表创建/检查完成")
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {str(e)}")
        raise
    
    # 创建必要的目录
    logger.info("📁 开始创建必要的目录")
    directories = ["../uploads", "../templates", "../static"]
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"✅ 目录创建/检查完成: {directory}")
        except Exception as e:
            logger.error(f"❌ 创建目录失败 {directory}: {str(e)}")
    
    # 记录配置信息
    logger.info("⚙️ 当前配置信息:")
    logger.info(f"  📛 应用名称: {settings.APP_NAME}")
    logger.info(f"  🐛 调试模式: {settings.DEBUG}")
    logger.info(f"  💾 数据库URL: {settings.DATABASE_URL}")
    logger.info(f"  📊 日志级别: {settings.LOG_LEVEL}")
    
    logger.success(f"🚀 {settings.APP_NAME} 后端服务启动成功！")
    logger.info(f"📚 API 文档地址: http://localhost:8000/docs")
    logger.info(f"📖 ReDoc 文档地址: http://localhost:8000/redoc")

@app.get("/", response_class=HTMLResponse)
async def root():
    """根路径返回服务状态"""
    logger.info("🏠 访问根路径")
    return """
    <html>
        <head>
            <title>AI-PPTX API 服务</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 600px; margin: 0 auto; text-align: center; }
                .status { color: #28a745; font-size: 24px; margin: 20px 0; }
                .links { margin: 30px 0; }
                .link { display: inline-block; margin: 10px; padding: 10px 20px; 
                       background: #007bff; color: white; text-decoration: none; 
                       border-radius: 5px; }
                .link:hover { background: #0056b3; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 AI-PPTX API 服务</h1>
                <div class="status">✅ 服务运行正常</div>
                <p>基于 FastAPI 构建的 AI 自动生成 PPT 服务</p>
                <div class="links">
                    <a href="/docs" class="link">📚 API 文档</a>
                    <a href="/redoc" class="link">📖 ReDoc 文档</a>
                </div>
                <p><em>前端界面请访问: http://localhost:8501</em></p>
            </div>
        </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """健康检查接口"""
    logger.info("💗 执行健康检查")
    
    # 检查数据库连接
    try:
        from app.core.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "ok"
        logger.debug("✅ 数据库连接正常")
    except Exception as e:
        db_status = "error"
        logger.error(f"❌ 数据库连接异常: {str(e)}")
    
    health_data = {
        "status": "ok" if db_status == "ok" else "error",
        "message": "服务运行正常" if db_status == "ok" else "服务异常",
        "database": db_status,
        "timestamp": time.time()
    }
    
    logger.info(f"💗 健康检查完成: {health_data['status']}")
    return health_data

if __name__ == "__main__":
    logger.info("🌐 启动开发服务器")
    logger.info("🔧 配置:")
    logger.info("  📡 主机: 0.0.0.0")
    logger.info("  🔌 端口: 8000")
    logger.info("  🔄 热重载: 开启")
    logger.info("  📁 监控目录: app")
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            reload_dirs=["app"]
        )
    except KeyboardInterrupt:
        logger.info("⏹️ 收到停止信号，正在关闭服务器")
    except Exception as e:
        logger.error(f"❌ 服务器启动失败: {str(e)}")
        raise 