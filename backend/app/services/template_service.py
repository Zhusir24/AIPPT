"""
模板服务类
负责 PPT 模板的管理
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from ..models.pptx import PPTTemplate


class TemplateService:
    """模板服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_template(self, template_id: int) -> Optional[PPTTemplate]:
        """获取单个模板"""
        return self.db.query(PPTTemplate).filter(
            PPTTemplate.id == template_id,
            PPTTemplate.is_active == True
        ).first()
    
    def get_templates(
        self,
        category: Optional[str] = None,
        is_active: bool = True,
        skip: int = 0,
        limit: int = 50
    ) -> List[PPTTemplate]:
        """获取模板列表"""
        query = self.db.query(PPTTemplate).filter(PPTTemplate.is_active == is_active)
        
        if category:
            query = query.filter(PPTTemplate.category == category)
        
        return query.order_by(PPTTemplate.sort_order).offset(skip).limit(limit).all()
    
    def get_random_templates(self, count: int = 12, category: Optional[str] = None) -> List[PPTTemplate]:
        """获取随机模板"""
        query = self.db.query(PPTTemplate).filter(PPTTemplate.is_active == True)
        
        if category:
            query = query.filter(PPTTemplate.category == category)
        
        return query.order_by(func.random()).limit(count).all()
    
    def get_categories(self) -> List[str]:
        """获取模板分类列表"""
        categories = self.db.query(PPTTemplate.category).filter(
            PPTTemplate.is_active == True,
            PPTTemplate.category.isnot(None)
        ).distinct().all()
        
        return [category[0] for category in categories if category[0]] 