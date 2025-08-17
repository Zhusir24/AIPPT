"""
模板服务类
负责 PPT 模板的管理
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from ..core.logger import get_logger
from ..models.pptx import PPTTemplate


class TemplateService:
    """模板服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(__name__)
        self.logger.debug("🎨 初始化模板服务实例")
    
    def get_template(self, template_id: int) -> Optional[PPTTemplate]:
        """获取单个模板"""
        self.logger.debug(f"🔍 查找模板 ID: {template_id}")
        
        template = self.db.query(PPTTemplate).filter(
            PPTTemplate.id == template_id,
            PPTTemplate.is_active == True
        ).first()
        
        if template:
            self.logger.debug(f"✅ 模板找到: {template.name}")
        else:
            self.logger.debug(f"❌ 模板未找到: ID {template_id}")
        
        return template
    
    def get_templates(
        self,
        category: Optional[str] = None,
        is_active: bool = True,
        skip: int = 0,
        limit: int = 50
    ) -> List[PPTTemplate]:
        """获取模板列表"""
        self.logger.debug(f"📄 查询模板列表: category={category}, is_active={is_active}, skip={skip}, limit={limit}")
        
        query = self.db.query(PPTTemplate).filter(PPTTemplate.is_active == is_active)
        
        if category:
            self.logger.debug(f"📂 按分类筛选: {category}")
            query = query.filter(PPTTemplate.category == category)
        
        templates = query.order_by(PPTTemplate.sort_order).offset(skip).limit(limit).all()
        self.logger.debug(f"📊 查询结果: {len(templates)} 个模板")
        
        return templates
    
    def get_random_templates(self, count: int = 12, category: Optional[str] = None) -> List[PPTTemplate]:
        """获取随机模板"""
        self.logger.debug(f"🎲 查询随机模板: count={count}, category={category}")
        
        query = self.db.query(PPTTemplate).filter(PPTTemplate.is_active == True)
        
        if category:
            self.logger.debug(f"📂 按分类筛选: {category}")
            query = query.filter(PPTTemplate.category == category)
        
        templates = query.order_by(func.random()).limit(count).all()
        self.logger.debug(f"🎲 随机获取 {len(templates)} 个模板")
        
        return templates
    
    def get_categories(self) -> List[str]:
        """获取模板分类列表"""
        self.logger.debug("📂 查询所有模板分类")
        
        categories = self.db.query(PPTTemplate.category).filter(
            PPTTemplate.is_active == True,
            PPTTemplate.category.isnot(None)
        ).distinct().all()
        
        category_list = [category[0] for category in categories if category[0]]
        self.logger.debug(f"📊 找到 {len(category_list)} 个分类: {category_list}")
        
        return category_list 