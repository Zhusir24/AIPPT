"""
文件服务类
负责文件上传、内容提取等操作
"""

import os
import uuid
import aiofiles
from pathlib import Path
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import UploadFile
import requests
from bs4 import BeautifulSoup
import docx
import PyPDF2
from io import BytesIO

from ..core.config import settings
from ..models.schemas import FileUploadResponse


class FileService:
    """文件服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(exist_ok=True)
    
    async def upload_and_extract(self, file: UploadFile) -> FileUploadResponse:
        """上传文件并提取内容"""
        try:
            # 生成唯一文件名
            file_extension = Path(file.filename).suffix
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = self.upload_dir / unique_filename
            
            # 保存文件
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # 提取文件内容
            extracted_content = self._extract_file_content(file_path, file.content_type)
            
            return FileUploadResponse(
                success=True,
                message="文件上传成功",
                file_path=str(file_path),
                extracted_content=extracted_content
            )
            
        except Exception as e:
            return FileUploadResponse(
                success=False,
                message=f"文件上传失败: {str(e)}"
            )
    
    async def extract_from_url(self, url: str) -> str:
        """从网页 URL 提取内容"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # 使用 BeautifulSoup 解析 HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 移除脚本和样式元素
            for script in soup(["script", "style"]):
                script.extract()
            
            # 提取文本内容
            text = soup.get_text()
            
            # 清理文本
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:5000]  # 限制长度
            
        except Exception as e:
            raise Exception(f"提取网页内容失败: {str(e)}")
    
    def get_file_preview(self, file_path: str) -> dict:
        """获取文件预览信息"""
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError("文件不存在")
            
            return {
                "filename": path.name,
                "size": path.stat().st_size,
                "extension": path.suffix,
                "created_at": path.stat().st_ctime
            }
            
        except Exception as e:
            raise Exception(f"获取文件预览失败: {str(e)}")
    
    def delete_file(self, file_path: str) -> bool:
        """删除文件"""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception:
            return False
    
    def _extract_file_content(self, file_path: Path, content_type: str) -> str:
        """根据文件类型提取内容"""
        try:
            if content_type == "application/pdf":
                return self._extract_pdf_content(file_path)
            elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                return self._extract_docx_content(file_path)
            elif content_type in ["text/plain", "text/markdown"]:
                return self._extract_text_content(file_path)
            else:
                return "不支持的文件类型"
                
        except Exception as e:
            return f"内容提取失败: {str(e)}"
    
    def _extract_pdf_content(self, file_path: Path) -> str:
        """提取 PDF 内容"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text[:5000]  # 限制长度
        except Exception as e:
            return f"PDF 解析失败: {str(e)}"
    
    def _extract_docx_content(self, file_path: Path) -> str:
        """提取 DOCX 内容"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text[:5000]  # 限制长度
        except Exception as e:
            return f"DOCX 解析失败: {str(e)}"
    
    def _extract_text_content(self, file_path: Path) -> str:
        """提取文本内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                return content[:5000]  # 限制长度
        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                with open(file_path, 'r', encoding='gbk') as file:
                    content = file.read()
                    return content[:5000]
            except Exception:
                return "文件编码不支持"
        except Exception as e:
            return f"文本解析失败: {str(e)}" 