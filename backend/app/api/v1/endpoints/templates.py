"""
PPT 模板管理 API 端点
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ....core.database import get_db
from ....models.schemas import PPTTemplate, BaseResponse
from ....services.template_service import TemplateService

router = APIRouter()


@router.get("/", response_model=List[PPTTemplate])
async def list_templates(
    category: Optional[str] = None,
    is_active: bool = True,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """获取模板列表"""
    try:
        service = TemplateService(db)
        return service.get_templates(
            category=category,
            is_active=is_active,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{template_id}", response_model=PPTTemplate)
async def get_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """获取特定模板详情"""
    try:
        service = TemplateService(db)
        template = service.get_template(template_id)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="模板不存在"
            )
        return template
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/random/{count}")
async def get_random_templates(
    count: int = 12,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取随机模板（用于展示）"""
    try:
        service = TemplateService(db)
        templates = service.get_random_templates(count, category)
        return BaseResponse(
            success=True,
            message="获取模板成功",
            data=templates
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/categories/")
async def get_template_categories(db: Session = Depends(get_db)):
    """获取模板分类列表"""
    try:
        service = TemplateService(db)
        categories = service.get_categories()
        return BaseResponse(
            success=True,
            message="获取分类成功",
            data=categories
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 