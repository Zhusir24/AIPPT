"""
应用配置设置
"""
import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用设置"""
    
    # 应用基本信息
    APP_NAME: str = Field(default="AI-PPTX", env="APP_NAME")
    DEBUG: bool = Field(default=False, env="DEBUG")
    API_V1_STR: str = "/api/v1"
    
    # 数据库配置
    DATABASE_URL: str = Field(default="sqlite:///./aipptx.db", env="DATABASE_URL")
    
    # AI 配置
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    OPENAI_BASE_URL: str = Field(default="https://api.openai.com/v1", env="OPENAI_BASE_URL")
    OPENAI_MODEL: str = Field(default="gpt-3.5-turbo", env="OPENAI_MODEL")
    
    DEEPSEEK_API_KEY: Optional[str] = Field(default=None, env="DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL: str = Field(default="https://api.deepseek.com/v1", env="DEEPSEEK_BASE_URL")
    DEEPSEEK_MODEL: str = Field(default="deepseek-chat", env="DEEPSEEK_MODEL")
    
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL: str = Field(default="claude-3-sonnet-20240229", env="ANTHROPIC_MODEL")
    
    # 文件配置
    UPLOAD_DIR: str = Field(default="./uploads", env="UPLOAD_DIR")
    MAX_FILE_SIZE: int = Field(default=50 * 1024 * 1024, env="MAX_FILE_SIZE")  # 50MB
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=["pdf", "docx", "txt", "md"], 
        env="ALLOWED_EXTENSIONS"
    )
    
    # 模板配置
    TEMPLATE_DIR: str = Field(default="./templates", env="TEMPLATE_DIR")
    STATIC_DIR: str = Field(default="./static", env="STATIC_DIR")
    
    # PPT 生成配置
    DEFAULT_LANGUAGE: str = Field(default="中文", env="DEFAULT_LANGUAGE")
    DEFAULT_OUTLINE_LENGTH: str = Field(default="中等", env="DEFAULT_OUTLINE_LENGTH")
    MAX_CONTENT_LENGTH: int = Field(default=10000, env="MAX_CONTENT_LENGTH")
    
    # 安全配置
    SECRET_KEY: str = Field(default="ai-pptx-secret-key-change-in-production", env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(
        default="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        env="LOG_FORMAT"
    )
    LOG_FILE: str = Field(default="./logs/aippt.log", env="LOG_FILE")
    LOG_ROTATION: str = Field(default="10 MB", env="LOG_ROTATION")
    LOG_RETENTION: str = Field(default="10 days", env="LOG_RETENTION")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建设置实例
settings = Settings() 