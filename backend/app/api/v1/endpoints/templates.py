"""
PPT 模板管理 API 端点
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ....core.database import get_db
from ....core.logger import get_logger, log_async_function_call
from ....models.schemas import PPTTemplate, BaseResponse
from ....services.template_service import TemplateService

router = APIRouter()
logger = get_logger(__name__)


@router.get("/", response_model=List[PPTTemplate])
async def list_templates(
    category: Optional[str] = None,
    is_active: bool = True,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """获取模板列表"""
    logger.info("🎨 获取模板列表")
    logger.debug(f"🔍 查询参数: category={category}, is_active={is_active}, skip={skip}, limit={limit}")
    
    try:
        logger.debug("📋 创建模板服务实例")
        service = TemplateService(db)
        
        logger.info("⚡ 开始查询模板")
        templates = service.get_templates(
            category=category,
            is_active=is_active,
            skip=skip,
            limit=limit
        )
        
        logger.success(f"✅ 模板列表获取成功，共 {len(templates)} 个模板")
        return templates
        
    except Exception as e:
        logger.error(f"❌ 获取模板列表失败: {str(e)}")
        logger.exception("详细错误信息:")
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
    logger.info(f"🔍 获取模板详情，ID: {template_id}")
    
    try:
        logger.debug("📋 创建模板服务实例")
        service = TemplateService(db)
        
        logger.info(f"⚡ 查找模板 ID: {template_id}")
        template = service.get_template(template_id)
        
        if not template:
            logger.warning(f"❌ 模板不存在: {template_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="模板不存在"
            )
        
        logger.success(f"✅ 模板获取成功: {template.name}")
        return template
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取模板详情失败: {str(e)}")
        logger.exception("详细错误信息:")
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
    logger.info(f"🎲 获取随机模板，数量: {count}")
    logger.debug(f"🔍 分类筛选: {category}")
    
    try:
        logger.debug("📋 创建模板服务实例")
        service = TemplateService(db)
        
        logger.info(f"⚡ 获取 {count} 个随机模板")
        templates = service.get_random_templates(count, category)
        
        logger.success(f"✅ 随机模板获取成功，实际返回 {len(templates)} 个模板")
        
        return BaseResponse(
            success=True,
            message="获取模板成功",
            data=templates
        )
        
    except Exception as e:
        logger.error(f"❌ 获取随机模板失败: {str(e)}")
        logger.exception("详细错误信息:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/categories/")
async def get_template_categories(db: Session = Depends(get_db)):
    """获取模板分类列表"""
    logger.info("📂 获取模板分类列表")
    
    try:
        logger.debug("📋 创建模板服务实例")
        service = TemplateService(db)
        
        logger.info("⚡ 查询所有模板分类")
        categories = service.get_categories()
        
        logger.success(f"✅ 模板分类获取成功，共 {len(categories)} 个分类")
        logger.debug(f"📊 分类列表: {categories}")
        
        return BaseResponse(
            success=True,
            message="获取分类成功",
            data=categories
        )
        
    except Exception as e:
        logger.error(f"❌ 获取模板分类失败: {str(e)}")
        logger.exception("详细错误信息:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 