"""
Pydantic 模式定义
用于 API 请求和响应的数据验证
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class InputType(str, Enum):
    """输入类型枚举"""
    TOPIC = "topic"
    FILE = "file"
    URL = "url"
    TEXT = "text"


class ProjectStatus(str, Enum):
    """项目状态枚举"""
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class GenerationStep(str, Enum):
    """生成步骤枚举"""
    INPUT = "input"
    OUTLINE = "outline"
    TEMPLATE = "template"
    GENERATE = "generate"
    COMPLETE = "complete"


# PPT 项目相关模式
class PPTProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    input_type: InputType
    input_content: str
    settings: Optional[Dict[str, Any]] = None


class PPTProjectCreate(PPTProjectBase):
    pass


class PPTProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    outline_content: Optional[str] = None
    template_id: Optional[int] = None
    status: Optional[ProjectStatus] = None
    settings: Optional[Dict[str, Any]] = None


class PPTProject(PPTProjectBase):
    id: int
    outline_content: Optional[str] = None
    template_id: Optional[int] = None
    status: ProjectStatus
    file_path: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# AI 生成相关模式
class OutlineGenerateRequest(BaseModel):
    topic: str
    language: str = "中文"
    outline_length: str = "中等"  # 简短/中等/详细
    target_audience: Optional[str] = None
    presentation_duration: Optional[str] = None
    additional_requirements: Optional[str] = None


class OutlineGenerateResponse(BaseModel):
    outline_markdown: str
    outline_tree: List[Dict[str, Any]]
    status: str
    error_message: Optional[str] = None


class ContentGenerateRequest(BaseModel):
    outline: str
    template_id: int


class ContentGenerateResponse(BaseModel):
    slides: List[Dict[str, Any]]
    status: str
    error_message: Optional[str] = None


# 模板相关模式
class PPTTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None


class PPTTemplate(PPTTemplateBase):
    id: int
    preview_image: Optional[str] = None
    template_file: Optional[str] = None
    is_active: bool
    sort_order: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# PPT 生成相关模式
class PPTGenerateRequest(BaseModel):
    project_id: int
    template_id: int
    outline_content: str


class PPTGenerateResponse(BaseModel):
    success: bool
    message: str
    file_path: Optional[str] = None
    preview_images: Optional[List[str]] = None


# 文件上传模式
class FileUploadResponse(BaseModel):
    success: bool
    message: str
    file_path: Optional[str] = None
    extracted_content: Optional[str] = None


# 通用响应模式
class BaseResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None


# 错误响应模式
class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None 