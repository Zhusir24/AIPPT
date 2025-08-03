"""
AI 生成相关 API 端点
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import json
import asyncio

from ....core.database import get_db
from ....models.schemas import (
    OutlineGenerateRequest, OutlineGenerateResponse, BaseResponse, ContentGenerateRequest
)
from ....services.ai_service import AIService
from ....services.template_service import TemplateService

router = APIRouter()


@router.post("/generate-outline", response_model=OutlineGenerateResponse)
async def generate_outline(
    request: OutlineGenerateRequest,
    db: Session = Depends(get_db)
):
    """生成内容大纲"""
    try:
        service = AIService(db)
        result = await service.generate_outline(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成大纲失败: {str(e)}"
        )


@router.post("/generate-outline-stream")
async def generate_outline_stream(
    request: OutlineGenerateRequest,
    db: Session = Depends(get_db)
):
    """流式生成内容大纲（SSE）"""
    try:
        service = AIService(db)
        
        async def event_generator():
            try:
                async for chunk in service.generate_outline_stream(request):
                    # 构造 SSE 格式的数据
                    yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
                
                # 发送完成事件
                yield f"data: {json.dumps({'status': 'complete'}, ensure_ascii=False)}\n\n"
            except Exception as e:
                # 发送错误事件
                error_data = {
                    'status': 'error',
                    'message': str(e)
                }
                yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成大纲失败: {str(e)}"
        )


@router.post("/generate-content")
async def generate_content(
    request: ContentGenerateRequest,
    db: Session = Depends(get_db)
):
    """根据大纲生成 PPT 内容"""
    try:
        ai_service = AIService(db)
        template_service = TemplateService(db)
        
        # 获取模板信息
        template = template_service.get_template(request.template_id)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="模板不存在"
            )
        
        template_info = {
            "name": template.name,
            "description": template.description,
            "category": template.category
        }
        
        result = await ai_service.generate_content(request.outline, template_info)
        return BaseResponse(
            success=True,
            message="内容生成成功",
            data=result
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成内容失败: {str(e)}"
        )


@router.post("/generate-ppt")
async def generate_ppt(
    request: ContentGenerateRequest,
    db: Session = Depends(get_db)
):
    """生成PPT文件"""
    try:
        ai_service = AIService(db)
        template_service = TemplateService(db)
        
        # 获取模板信息
        template = template_service.get_template(request.template_id)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="模板不存在"
            )
        
        template_info = {
            "name": template.name,
            "description": template.description,
            "category": template.category
        }
        
        # 生成详细内容
        content_result = await ai_service.generate_content(request.outline, template_info)
        if content_result.get('error'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"内容生成失败: {content_result['error']}"
            )
        
        # 导入PPT生成服务
        from ....services.pptx_service import PPTXService
        pptx_service = PPTXService()
        
        # 生成PPT文件
        ppt_result = await pptx_service.create_presentation(
            outline=request.outline,
            content_data=content_result,
            template_info=template_info
        )
        
        return BaseResponse(
            success=True,
            message="PPT生成成功",
            data=ppt_result
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()  # 打印完整的错误堆栈
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PPT生成失败: {str(e)}"
        )


@router.get("/provider")
async def get_ai_provider(db: Session = Depends(get_db)):
    """获取当前AI提供商信息"""
    try:
        ai_service = AIService(db)
        provider = ai_service.get_current_provider()
        model = ai_service._get_model_name()
        
        return BaseResponse(
            success=True,
            message="获取AI提供商信息成功",
            data={
                "provider": provider,
                "model": model
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取AI提供商信息失败: {str(e)}"
        )


@router.post("/expand-content")
async def expand_content(
    section_title: str,
    current_content: str,
    db: Session = Depends(get_db)
):
    """扩展和丰富内容"""
    try:
        service = AIService(db)
        result = await service.expand_content(section_title, current_content)
        return BaseResponse(
            success=True,
            message="内容扩展成功",
            data={"expanded_content": result}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"扩展内容失败: {str(e)}"
        ) 