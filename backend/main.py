"""
AI-PPTX 后端主入口文件
基于 FastAPI 构建的 API 服务
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import os
from pathlib import Path

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.database import create_tables

# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-PPTX API 服务",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该配置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
if os.path.exists("../static"):
    app.mount("/static", StaticFiles(directory="../static"), name="static")

if os.path.exists("../uploads"):
    app.mount("/uploads", StaticFiles(directory="../uploads"), name="uploads")

if os.path.exists("../templates"):
    app.mount("/templates", StaticFiles(directory="../templates"), name="templates")

# 包含 API 路由
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    # 创建数据库表
    create_tables()
    
    # 创建必要的目录
    os.makedirs("../uploads", exist_ok=True)
    os.makedirs("../templates", exist_ok=True)
    os.makedirs("../static", exist_ok=True)
    
    print(f"🚀 {settings.APP_NAME} 后端服务启动成功！")
    print(f"📚 API 文档地址: http://localhost:8000/docs")

@app.get("/", response_class=HTMLResponse)
async def root():
    """根路径返回服务状态"""
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
    return {"status": "ok", "message": "服务运行正常"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"]
    ) 