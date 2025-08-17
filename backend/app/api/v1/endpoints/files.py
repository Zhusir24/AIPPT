"""
文件处理 API 端点
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os

from ....core.database import get_db
from ....core.logger import get_logger, log_async_function_call
from ....models.schemas import FileUploadResponse, BaseResponse, UrlExtractRequest
from ....services.file_service import FileService
from ....core.config import settings

router = APIRouter()
logger = get_logger(__name__)


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """上传文件并提取内容"""
    logger.info("📁 开始文件上传")
    logger.info(f"📎 文件名: {file.filename}")
    logger.info(f"📎 文件类型: {file.content_type}")
    logger.info(f"📎 文件大小: {file.size} bytes")
    
    try:
        # 检查文件大小
        logger.debug(f"🔍 检查文件大小，限制: {settings.MAX_FILE_SIZE} bytes")
        if file.size > settings.MAX_FILE_SIZE:
            logger.warning(f"❌ 文件大小超限: {file.size} > {settings.MAX_FILE_SIZE}")
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"文件大小超过限制 ({settings.MAX_FILE_SIZE} bytes)"
            )
        logger.debug("✅ 文件大小检查通过")
        
        # 检查文件类型
        logger.debug(f"🔍 检查文件类型: {file.content_type}")
        # 注意：这里可能需要根据实际的ALLOWED_FILE_TYPES设置进行调整
        # if file.content_type not in settings.ALLOWED_FILE_TYPES:
        #     logger.warning(f"❌ 不支持的文件类型: {file.content_type}")
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail=f"不支持的文件类型: {file.content_type}"
        #     )
        logger.debug("✅ 文件类型检查通过")
        
        # 创建服务实例并处理文件
        logger.debug("📋 创建文件服务实例")
        service = FileService(db)
        
        logger.info("⚡ 开始上传并提取文件内容")
        result = await service.upload_and_extract(file)
        
        logger.success("✅ 文件上传和内容提取成功")
        logger.debug(f"📊 提取结果: {str(result)[:200]}...")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 文件上传失败: {str(e)}")
        logger.exception("详细错误信息:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传失败: {str(e)}"
        )


@router.post("/extract-url", response_model=BaseResponse)
async def extract_from_url(
    request: UrlExtractRequest,
    db: Session = Depends(get_db)
):
    """从网页 URL 提取内容"""
    logger.info("🌐 开始从 URL 提取内容")
    logger.info(f"🔗 目标 URL: {request.url}")
    
    try:
        # 创建服务实例
        logger.debug("📋 创建文件服务实例")
        service = FileService(db)
        
        # 提取网页内容
        logger.info("⚡ 开始提取网页内容")
        content = await service.extract_from_url(request.url)
        
        logger.success("✅ 网页内容提取成功")
        logger.info(f"📊 提取内容长度: {len(content)} 字符")
        logger.debug(f"📊 提取内容预览: {content[:200]}...")
        
        return BaseResponse(
            success=True,
            message="网页内容提取成功",
            data={"content": content, "url": request.url}
        )
        
    except Exception as e:
        logger.error(f"❌ 网页内容提取失败: {str(e)}")
        logger.exception("详细错误信息:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"网页内容提取失败: {str(e)}"
        )


@router.get("/preview/{file_path}")
async def get_file_preview(
    file_path: str,
    db: Session = Depends(get_db)
):
    """获取文件预览信息"""
    logger.info("🔍 获取文件预览")
    logger.info(f"📁 文件路径: {file_path}")
    
    try:
        # 创建服务实例
        logger.debug("📋 创建文件服务实例")
        service = FileService(db)
        
        # 获取文件预览
        logger.info("⚡ 开始获取文件预览")
        preview = service.get_file_preview(file_path)
        
        logger.success("✅ 文件预览获取成功")
        logger.debug(f"📊 预览信息: {str(preview)[:200]}...")
        
        return BaseResponse(
            success=True,
            message="获取预览成功",
            data=preview
        )
        
    except Exception as e:
        logger.error(f"❌ 获取文件预览失败: {str(e)}")
        logger.exception("详细错误信息:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取预览失败: {str(e)}"
        )


@router.get("/download/{filename}")
async def download_file(filename: str):
    """下载生成的文件"""
    logger.info("📥 开始文件下载")
    logger.info(f"📁 文件名: {filename}")
    
    try:
        from pathlib import Path
        from fastapi.responses import FileResponse
        
        # 检查文件是否存在
        file_path = Path(settings.UPLOAD_DIR) / filename
        logger.debug(f"🔍 检查文件路径: {file_path}")
        
        if not file_path.exists():
            logger.warning(f"❌ 文件不存在: {file_path}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在"
            )
        
        logger.info(f"✅ 文件存在，大小: {file_path.stat().st_size} bytes")
        
        # 返回文件下载响应
        logger.info("🚀 开始返回文件响应")
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.presentationml.presentation'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 下载文件失败: {str(e)}")
        logger.exception("详细错误信息:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"下载文件失败: {str(e)}"
        )


@router.delete("/{file_path}")
async def delete_file(
    file_path: str,
    db: Session = Depends(get_db)
):
    """删除上传的文件"""
    logger.info("🗑️ 开始删除文件")
    logger.info(f"📁 文件路径: {file_path}")
    
    try:
        # 创建服务实例
        logger.debug("📋 创建文件服务实例")
        service = FileService(db)
        
        # 删除文件
        logger.info("⚡ 开始删除文件")
        success = service.delete_file(file_path)
        
        if not success:
            logger.warning(f"❌ 文件不存在或删除失败: {file_path}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在"
            )
        
        logger.success("✅ 文件删除成功")
        return BaseResponse(success=True, message="文件删除成功")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 删除文件失败: {str(e)}")
        logger.exception("详细错误信息:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除文件失败: {str(e)}"
        ) 