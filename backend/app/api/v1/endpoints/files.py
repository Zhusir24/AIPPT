"""
文件处理 API 端点
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os

from ....core.database import get_db
from ....models.schemas import FileUploadResponse, BaseResponse
from ....services.file_service import FileService
from ....core.config import settings

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """上传文件并提取内容"""
    try:
        # 检查文件大小
        if file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"文件大小超过限制 ({settings.MAX_FILE_SIZE} bytes)"
            )
        
        # 检查文件类型
        if file.content_type not in settings.ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件类型: {file.content_type}"
            )
        
        service = FileService(db)
        result = await service.upload_and_extract(file)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传失败: {str(e)}"
        )


@router.post("/extract-url", response_model=BaseResponse)
async def extract_from_url(
    url: str,
    db: Session = Depends(get_db)
):
    """从网页 URL 提取内容"""
    try:
        service = FileService(db)
        content = await service.extract_from_url(url)
        return BaseResponse(
            success=True,
            message="网页内容提取成功",
            data={"content": content, "url": url}
        )
    except Exception as e:
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
    try:
        service = FileService(db)
        preview = service.get_file_preview(file_path)
        return BaseResponse(
            success=True,
            message="获取预览成功",
            data=preview
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取预览失败: {str(e)}"
        )


@router.get("/download/{filename}")
async def download_file(filename: str):
    """下载生成的文件"""
    try:
        from pathlib import Path
        from fastapi.responses import FileResponse
        
        # 检查文件是否存在
        file_path = Path(settings.UPLOAD_DIR) / filename
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在"
            )
        
        # 返回文件下载响应
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.presentationml.presentation'
        )
        
    except HTTPException:
        raise
    except Exception as e:
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
    try:
        service = FileService(db)
        success = service.delete_file(file_path)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在"
            )
        return BaseResponse(success=True, message="文件删除成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除文件失败: {str(e)}"
        ) 