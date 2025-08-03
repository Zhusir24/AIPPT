"""
PPT 项目管理 API 端点
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ....core.database import get_db
from ....models.schemas import (
    PPTProject, PPTProjectCreate, PPTProjectUpdate, BaseResponse
)
from ....services.project_service import ProjectService

router = APIRouter()


@router.post("/", response_model=PPTProject)
async def create_project(
    project: PPTProjectCreate,
    db: Session = Depends(get_db)
):
    """创建新的 PPT 项目"""
    try:
        service = ProjectService(db)
        return service.create_project(project)
    except Exception as e:
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
    try:
        service = ProjectService(db)
        return service.get_projects(skip=skip, limit=limit)
    except Exception as e:
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
    try:
        service = ProjectService(db)
        project = service.get_project(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        return project
    except HTTPException:
        raise
    except Exception as e:
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
    try:
        service = ProjectService(db)
        project = service.update_project(project_id, project_update)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        return project
    except HTTPException:
        raise
    except Exception as e:
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
    try:
        service = ProjectService(db)
        success = service.delete_project(project_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        return BaseResponse(success=True, message="项目删除成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 