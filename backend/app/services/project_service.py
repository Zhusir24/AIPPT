"""
项目服务类
负责 PPT 项目的 CRUD 操作
"""

from sqlalchemy.orm import Session
from typing import List, Optional

from ..models.pptx import PPTProject
from ..models.schemas import PPTProjectCreate, PPTProjectUpdate


class ProjectService:
    """项目服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_project(self, project: PPTProjectCreate) -> PPTProject:
        """创建新项目"""
        db_project = PPTProject(
            title=project.title,
            description=project.description,
            input_type=project.input_type,
            input_content=project.input_content,
            settings=project.settings
        )
        self.db.add(db_project)
        self.db.commit()
        self.db.refresh(db_project)
        return db_project
    
    def get_project(self, project_id: int) -> Optional[PPTProject]:
        """获取单个项目"""
        return self.db.query(PPTProject).filter(PPTProject.id == project_id).first()
    
    def get_projects(self, skip: int = 0, limit: int = 100) -> List[PPTProject]:
        """获取项目列表"""
        return self.db.query(PPTProject).offset(skip).limit(limit).all()
    
    def update_project(self, project_id: int, project_update: PPTProjectUpdate) -> Optional[PPTProject]:
        """更新项目"""
        db_project = self.get_project(project_id)
        if not db_project:
            return None
        
        update_data = project_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_project, field, value)
        
        self.db.commit()
        self.db.refresh(db_project)
        return db_project
    
    def delete_project(self, project_id: int) -> bool:
        """删除项目"""
        db_project = self.get_project(project_id)
        if not db_project:
            return False
        
        self.db.delete(db_project)
        self.db.commit()
        return True 