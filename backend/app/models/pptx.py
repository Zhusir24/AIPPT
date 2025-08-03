"""
PPT 相关的数据模型
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from ..core.database import Base


class PPTProject(Base):
    """PPT 项目模型"""
    __tablename__ = "ppt_projects"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, comment="项目标题")
    description = Column(Text, comment="项目描述")
    input_type = Column(String(50), nullable=False, comment="输入类型：topic/file/url")
    input_content = Column(Text, comment="输入内容")
    outline_content = Column(Text, comment="大纲内容（Markdown格式）")
    template_id = Column(Integer, comment="模板ID")
    status = Column(String(20), default="draft", comment="状态：draft/generating/completed/failed")
    file_path = Column(String(500), comment="生成的PPT文件路径")
    settings = Column(JSON, comment="生成设置")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PPTTemplate(Base):
    """PPT 模板模型"""
    __tablename__ = "ppt_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="模板名称")
    description = Column(Text, comment="模板描述")
    preview_image = Column(String(500), comment="预览图路径")
    template_file = Column(String(500), comment="模板文件路径")
    category = Column(String(50), comment="模板分类")
    is_active = Column(Boolean, default=True, comment="是否激活")
    sort_order = Column(Integer, default=0, comment="排序")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class GenerationLog(Base):
    """生成日志模型"""
    __tablename__ = "generation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, comment="项目ID")
    step = Column(String(50), comment="生成步骤")
    status = Column(String(20), comment="状态")
    message = Column(Text, comment="消息内容")
    details = Column(JSON, comment="详细信息")
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 