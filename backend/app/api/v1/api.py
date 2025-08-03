"""
API v1 主路由
"""

from fastapi import APIRouter
from .endpoints import projects, templates, ai, files

api_router = APIRouter()

# 包含各个模块的路由
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(files.router, prefix="/files", tags=["files"]) 