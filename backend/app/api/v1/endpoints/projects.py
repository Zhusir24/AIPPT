"""
PPT 项目管理 API 端点
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ....core.database import get_db
from ....core.logger import get_logger, log_async_function_call
from ....models.schemas import (
    PPTProject, PPTProjectCreate, PPTProjectUpdate, BaseResponse
)
from ....services.project_service import ProjectService

router = APIRouter()
logger = get_logger(__name__)


@router.post("/", response_model=PPTProject)
async def create_project(
    project: PPTProjectCreate,
    db: Session = Depends(get_db)
):
    """创建新的 PPT 项目"""
    logger.info("🎆 开始创建新 PPT 项目")
    logger.debug(f"📋 项目信息: {project.dict()}")
    
    try:
        logger.debug("📋 创建项目服务实例")
        service = ProjectService(db)
        
        logger.info(f"⚡ 创建项目: {project.title}")
        result = service.create_project(project)
        
        logger.success(f"✅ 项目创建成功，ID: {result.id}")
        return result
        
    except Exception as e:
        logger.error(f"❌ 创建项目失败: {str(e)}")
        logger.exception("详细错误信息:")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[PPTProject])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取项目列表"""
    logger.info("📄 获取项目列表")
    logger.debug(f"🔢 分页参数: skip={skip}, limit={limit}")
    
    try:
        logger.debug("📋 创建项目服务实例")
        service = ProjectService(db)
        
        logger.info("⚡ 获取项目列表")
        projects = service.get_projects(skip=skip, limit=limit)
        
        logger.success(f"✅ 获取项目列表成功，共 {len(projects)} 个项目")
        return projects
        
    except Exception as e:
        logger.error(f"❌ 获取项目列表失败: {str(e)}")
        logger.exception("详细错误信息:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{project_id}", response_model=PPTProject)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """获取特定项目详情"""
    logger.info(f"🔍 获取项目详情，ID: {project_id}")
    
    try:
        logger.debug("📋 创建项目服务实例")
        service = ProjectService(db)
        
        logger.info(f"⚡ 查找项目 ID: {project_id}")
        project = service.get_project(project_id)
        
        if not project:
            logger.warning(f"❌ 项目不存在: {project_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        logger.success(f"✅ 项目获取成功: {project.title}")
        return project
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取项目详情失败: {str(e)}")
        logger.exception("详细错误信息:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{project_id}", response_model=PPTProject)
async def update_project(
    project_id: int,
    project_update: PPTProjectUpdate,
    db: Session = Depends(get_db)
):
    """更新项目信息"""
    logger.info(f"✏️ 开始更新项目，ID: {project_id}")
    logger.debug(f"📋 更新信息: {project_update.dict()}")
    
    try:
        logger.debug("📋 创建项目服务实例")
        service = ProjectService(db)
        
        logger.info(f"⚡ 更新项目 ID: {project_id}")
        project = service.update_project(project_id, project_update)
        
        if not project:
            logger.warning(f"❌ 项目不存在: {project_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        logger.success(f"✅ 项目更新成功: {project.title}")
        return project
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 更新项目失败: {str(e)}")
        logger.exception("详细错误信息:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{project_id}", response_model=BaseResponse)
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """删除项目"""
    logger.info(f"🗑️ 开始删除项目，ID: {project_id}")
    
    try:
        logger.debug("📋 创建项目服务实例")
        service = ProjectService(db)
        
        logger.info(f"⚡ 删除项目 ID: {project_id}")
        success = service.delete_project(project_id)
        
        if not success:
            logger.warning(f"❌ 项目不存在或删除失败: {project_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        logger.success(f"✅ 项目删除成功: {project_id}")
        return BaseResponse(success=True, message="项目删除成功")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 删除项目失败: {str(e)}")
        logger.exception("详细错误信息:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 