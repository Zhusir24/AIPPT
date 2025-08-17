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
from ..core.logger import get_logger, log_async_function_call
from ..models.schemas import FileUploadResponse


class FileService:
    """文件服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(__name__)
        self.logger.debug("📁 初始化文件服务实例")
        
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.logger.debug(f"📂 上传目录路径: {self.upload_dir}")
        
        # 确保上传目录存在
        self.upload_dir.mkdir(exist_ok=True)
        self.logger.debug("✅ 上传目录检查/创建完成")
    
    async def upload_and_extract(self, file: UploadFile) -> FileUploadResponse:
        """上传文件并提取内容"""
        self.logger.info("📤 开始文件上传和内容提取")
        self.logger.info(f"📄 原始文件名: {file.filename}")
        self.logger.info(f"🏷️ 文件类型: {file.content_type}")
        
        try:
            # 生成唯一文件名
            self.logger.debug("🔄 生成唯一文件名")
            file_extension = Path(file.filename).suffix
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = self.upload_dir / unique_filename
            self.logger.info(f"📁 目标文件路径: {file_path}")
            
            # 读取文件内容
            self.logger.debug("📖 读取上传文件内容")
            content = await file.read()
            file_size = len(content)
            self.logger.info(f"📊 文件大小: {file_size} bytes ({file_size/1024:.2f} KB)")
            
            # 保存文件
            self.logger.debug("💾 开始保存文件到磁盘")
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
            self.logger.success("✅ 文件保存成功")
            
            # 提取文件内容
            self.logger.info("🔍 开始提取文件内容")
            extracted_content = self._extract_file_content(file_path, file.content_type)
            content_length = len(extracted_content) if extracted_content else 0
            self.logger.info(f"📄 提取内容长度: {content_length} 字符")
            
            if content_length > 0:
                self.logger.debug(f"📄 提取内容预览: {extracted_content[:200]}...")
            
            self.logger.success("🎉 文件上传和内容提取完成")
            return FileUploadResponse(
                success=True,
                message="文件上传成功",
                file_path=str(file_path),
                extracted_content=extracted_content
            )
            
        except Exception as e:
            self.logger.error(f"❌ 文件上传和提取失败: {str(e)}")
            self.logger.exception("详细错误信息:")
            return FileUploadResponse(
                success=False,
                message=f"文件上传失败: {str(e)}"
            )
    
    async def extract_from_url(self, url: str) -> str:
        """从网页 URL 提取内容"""
        self.logger.info("🌐 开始从URL提取内容")
        self.logger.info(f"🔗 目标URL: {url}")
        
        try:
            # 准备请求头
            self.logger.debug("🔧 设置请求头")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            self.logger.debug(f"📋 User-Agent: {headers['User-Agent']}")
            
            # 发送HTTP请求
            self.logger.info("📡 发送HTTP请求")
            response = requests.get(url, headers=headers, timeout=10)
            self.logger.info(f"📈 响应状态码: {response.status_code}")
            
            response.raise_for_status()
            self.logger.success("✅ HTTP请求成功")
            
            # 记录响应信息
            content_length = len(response.content)
            self.logger.info(f"📊 响应内容大小: {content_length} bytes ({content_length/1024:.2f} KB)")
            self.logger.debug(f"🏷️ 内容类型: {response.headers.get('content-type', '未知')}")
            
            # 使用 BeautifulSoup 解析 HTML
            self.logger.debug("🔍 开始解析HTML内容")
            soup = BeautifulSoup(response.content, 'html.parser')
            self.logger.debug("✅ HTML解析完成")
            
            # 移除脚本和样式元素
            self.logger.debug("🧹 清理脚本和样式元素")
            script_count = 0
            for script in soup(["script", "style"]):
                script_count += 1
                script.extract()
            self.logger.debug(f"🗑️ 移除了 {script_count} 个脚本/样式元素")
            
            # 提取文本内容
            self.logger.debug("📄 提取纯文本内容")
            text = soup.get_text()
            original_length = len(text)
            self.logger.debug(f"📊 原始文本长度: {original_length} 字符")
            
            # 清理文本
            self.logger.debug("🧽 清理和格式化文本")
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # 限制长度
            final_text = text[:5000]
            final_length = len(final_text)
            self.logger.info(f"📄 最终文本长度: {final_length} 字符 (限制5000字符)")
            
            if final_length > 0:
                self.logger.debug(f"📄 提取内容预览: {final_text[:300]}...")
            
            self.logger.success("🎉 网页内容提取完成")
            return final_text
            
        except requests.RequestException as e:
            self.logger.error(f"❌ HTTP请求失败: {str(e)}")
            raise Exception(f"提取网页内容失败: {str(e)}")
        except Exception as e:
            self.logger.error(f"❌ 网页内容提取失败: {str(e)}")
            self.logger.exception("详细错误信息:")
            raise Exception(f"提取网页内容失败: {str(e)}")
    
    def get_file_preview(self, file_path: str) -> dict:
        """获取文件预览信息"""
        self.logger.info("🔍 获取文件预览信息")
        self.logger.debug(f"📁 文件路径: {file_path}")
        
        try:
            path = Path(file_path)
            
            # 检查文件是否存在
            self.logger.debug("🔎 检查文件是否存在")
            if not path.exists():
                self.logger.warning(f"❌ 文件不存在: {file_path}")
                raise FileNotFoundError("文件不存在")
            
            # 获取文件信息
            self.logger.debug("📊 获取文件统计信息")
            file_stat = path.stat()
            
            preview_info = {
                "filename": path.name,
                "size": file_stat.st_size,
                "extension": path.suffix,
                "created_at": file_stat.st_ctime
            }
            
            self.logger.info(f"📄 文件名: {preview_info['filename']}")
            self.logger.info(f"📊 文件大小: {preview_info['size']} bytes ({preview_info['size']/1024:.2f} KB)")
            self.logger.info(f"🏷️ 文件扩展名: {preview_info['extension']}")
            self.logger.debug(f"📅 创建时间: {preview_info['created_at']}")
            
            self.logger.success("✅ 文件预览信息获取成功")
            return preview_info
            
        except FileNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"❌ 获取文件预览失败: {str(e)}")
            self.logger.exception("详细错误信息:")
            raise Exception(f"获取文件预览失败: {str(e)}")
    
    def delete_file(self, file_path: str) -> bool:
        """删除文件"""
        self.logger.info("🗑️ 开始删除文件")
        self.logger.debug(f"📁 目标文件路径: {file_path}")
        
        try:
            path = Path(file_path)
            
            # 检查文件是否存在
            self.logger.debug("🔎 检查文件是否存在")
            if path.exists():
                # 记录文件信息
                file_size = path.stat().st_size
                self.logger.info(f"📊 待删除文件大小: {file_size} bytes ({file_size/1024:.2f} KB)")
                
                # 删除文件
                self.logger.debug("🗑️ 执行文件删除")
                path.unlink()
                
                self.logger.success("✅ 文件删除成功")
                return True
            else:
                self.logger.warning(f"⚠️ 文件不存在，无需删除: {file_path}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ 文件删除失败: {str(e)}")
            self.logger.exception("详细错误信息:")
            return False
    
    def _extract_file_content(self, file_path: Path, content_type: str) -> str:
        """根据文件类型提取内容"""
        self.logger.debug("🔍 开始根据文件类型提取内容")
        self.logger.debug(f"🏷️ 文件类型: {content_type}")
        
        try:
            if content_type == "application/pdf":
                self.logger.debug("📄 检测到PDF文件，调用PDF提取器")
                return self._extract_pdf_content(file_path)
            elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                self.logger.debug("📝 检测到Word文档，调用DOCX提取器")
                return self._extract_docx_content(file_path)
            elif content_type in ["text/plain", "text/markdown"]:
                self.logger.debug("📝 检测到纯文本文件，调用文本提取器")
                return self._extract_text_content(file_path)
            else:
                self.logger.warning(f"⚠️ 不支持的文件类型: {content_type}")
                return "不支持的文件类型"
                
        except Exception as e:
            self.logger.error(f"❌ 内容提取过程失败: {str(e)}")
            self.logger.exception("详细错误信息:")
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