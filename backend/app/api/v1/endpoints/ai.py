"""
AI 生成相关 API 端点
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import json
import asyncio

from ....core.database import get_db
from ....core.logger import get_logger, log_async_function_call
from ....models.schemas import (
    OutlineGenerateRequest, OutlineGenerateResponse, BaseResponse, ContentGenerateRequest
)
from ....services.ai_service import AIService
from ....services.template_service import TemplateService

router = APIRouter()
logger = get_logger(__name__)


@router.post("/generate-outline", response_model=OutlineGenerateResponse)
async def generate_outline(
    request: OutlineGenerateRequest,
    db: Session = Depends(get_db)
):
    """生成内容大纲"""
    logger.info("🎯 开始生成内容大纲")
    logger.debug(f"📋 请求参数: {request.dict()}")
    
    try:
        # 创建AI服务实例
        logger.debug("🤖 创建 AI 服务实例")
        service = AIService(db)
        
        # 记录请求详情
        logger.info(f"📝 主题: {request.topic}")
        logger.info(f"🌍 语言: {request.language}")
        logger.info(f"📏 大纲长度: {request.outline_length}")
        if request.content:
            logger.info(f"📄 输入内容长度: {len(request.content)} 字符")
        if request.url:
            logger.info(f"🔗 输入URL: {request.url}")
        
        # 生成大纲
        logger.info("⚡ 调用AI服务生成大纲")
        result = await service.generate_outline(request)
        
        logger.success("✅ 大纲生成成功")
        logger.debug(f"📊 返回结果: {result.dict()}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ 生成大纲失败: {str(e)}")
        logger.exception("详细错误信息:")
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
    logger.info("🌊 开始流式生成内容大纲")
    logger.debug(f"📋 请求参数: {request.dict()}")
    
    try:
        # 创建AI服务实例
        logger.debug("🤖 创建 AI 服务实例")
        service = AIService(db)
        
        # 记录请求详情
        logger.info(f"📝 主题: {request.topic}")
        logger.info(f"🌍 语言: {request.language}")
        logger.info(f"📏 大纲长度: {request.outline_length}")
        
        chunk_count = 0
        
        async def event_generator():
            nonlocal chunk_count
            try:
                logger.info("⚡ 开始流式生成")
                async for chunk in service.generate_outline_stream(request):
                    chunk_count += 1
                    logger.debug(f"📦 发送第 {chunk_count} 个数据块: {chunk[:50]}...")
                    # 构造 SSE 格式的数据
                    yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
                
                # 发送完成事件
                logger.info(f"✅ 流式生成完成，共发送 {chunk_count} 个数据块")
                yield f"data: {json.dumps({'status': 'complete'}, ensure_ascii=False)}\n\n"
                
            except Exception as e:
                logger.error(f"❌ 流式生成失败: {str(e)}")
                logger.exception("详细错误信息:")
                # 发送错误事件
                error_data = {
                    'status': 'error',
                    'message': str(e)
                }
                yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
        
        logger.info("🚀 开始返回流式响应")
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        
    except Exception as e:
        logger.error(f"❌ 流式生成大纲失败: {str(e)}")
        logger.exception("详细错误信息:")
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
    logger.info("📄 开始生成 PPT 内容")
    logger.debug(f"📋 请求参数: {request.dict()}")
    
    try:
        # 创建服务实例
        logger.debug("🤖 创建 AI 服务实例")
        ai_service = AIService(db)
        logger.debug("📋 创建模板服务实例")
        template_service = TemplateService(db)
        
        # 获取模板信息
        logger.info(f"🎨 获取模板信息，模板ID: {request.template_id}")
        template = template_service.get_template(request.template_id)
        if not template:
            logger.warning(f"❌ 模板不存在: {request.template_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="模板不存在"
            )
        
        template_info = {
            "name": template.name,
            "description": template.description,
            "category": template.category
        }
        logger.info(f"✅ 模板信息获取成功: {template.name} ({template.category})")
        logger.debug(f"📋 模板详情: {template_info}")
        
        # 生成内容
        logger.info("⚡ 调用AI服务生成内容")
        result = await ai_service.generate_content(request.outline, template_info)
        
        logger.success("✅ PPT内容生成成功")
        logger.debug(f"📊 生成结果: {str(result)[:200]}...")
        
        return BaseResponse(
            success=True,
            message="内容生成成功",
            data=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 生成内容失败: {str(e)}")
        logger.exception("详细错误信息:")
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
    logger.info("📊 开始生成完整 PPT 文件")
    logger.debug(f"📋 请求参数: {request.dict()}")
    
    try:
        # 创建服务实例
        logger.debug("🤖 创建 AI 服务实例")
        ai_service = AIService(db)
        logger.debug("📋 创建模板服务实例")
        template_service = TemplateService(db)
        
        # 获取模板信息
        logger.info(f"🎨 获取模板信息，模板ID: {request.template_id}")
        template = template_service.get_template(request.template_id)
        if not template:
            logger.warning(f"❌ 模板不存在: {request.template_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="模板不存在"
            )
        
        template_info = {
            "name": template.name,
            "description": template.description,
            "category": template.category
        }
        logger.info(f"✅ 模板信息获取成功: {template.name} ({template.category})")
        
        # 生成详细内容
        logger.info("⚡ 第一步：生成PPT内容")
        content_result = await ai_service.generate_content(request.outline, template_info)
        if content_result.get('error'):
            logger.error(f"❌ 内容生成失败: {content_result['error']}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"内容生成失败: {content_result['error']}"
            )
        logger.success("✅ PPT内容生成完成")
        
        # 导入PPT生成服务
        logger.debug("📋 导入 PPTX 服务")
        from ....services.pptx_service import PPTXService
        pptx_service = PPTXService()
        logger.debug("✅ PPTX 服务实例创建成功")
        
        # 生成PPT文件
        logger.info("⚡ 第二步：生成PPT文件")
        ppt_result = await pptx_service.create_presentation(
            outline=request.outline,
            content_data=content_result,
            template_info=template_info
        )
        
        logger.success(f"🎉 PPT文件生成成功: {ppt_result.get('filename', '未知文件名')}")
        logger.info(f"📁 文件路径: {ppt_result.get('file_path', '未知路径')}")
        
        return BaseResponse(
            success=True,
            message="PPT生成成功",
            data=ppt_result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ PPT生成失败: {str(e)}")
        logger.exception("详细错误信息:")
        import traceback
        traceback.print_exc()  # 打印完整的错误堆栈
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PPT生成失败: {str(e)}"
        )


@router.get("/provider")
async def get_ai_provider(db: Session = Depends(get_db)):
    """获取当前AI提供商信息"""
    logger.info("🤖 获取AI提供商信息")
    
    try:
        logger.debug("🤖 创建 AI 服务实例")
        ai_service = AIService(db)
        
        logger.debug("🔍 获取当前提供商")
        provider = ai_service.get_current_provider()
        
        logger.debug("🔍 获取当前模型")
        model = ai_service._get_model_name()
        
        logger.info(f"✅ AI提供商: {provider}, 模型: {model}")
        
        return BaseResponse(
            success=True,
            message="获取AI提供商信息成功",
            data={
                "provider": provider,
                "model": model
            }
        )
        
    except Exception as e:
        logger.error(f"❌ 获取AI提供商信息失败: {str(e)}")
        logger.exception("详细错误信息:")
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
    logger.info("📝 开始扩展内容")
    logger.info(f"📝 章节标题: {section_title}")
    logger.debug(f"📋 当前内容长度: {len(current_content)} 字符")
    logger.debug(f"📋 当前内容: {current_content[:100]}...")
    
    try:
        logger.debug("🤖 创建 AI 服务实例")
        service = AIService(db)
        
        logger.info("⚡ 调用AI服务扩展内容")
        result = await service.expand_content(section_title, current_content)
        
        logger.success("✅ 内容扩展成功")
        logger.debug(f"📊 扩展后内容长度: {len(result)} 字符")
        logger.debug(f"📊 扩展结果: {result[:100]}...")
        
        return BaseResponse(
            success=True,
            message="内容扩展成功",
            data={"expanded_content": result}
        )
        
    except Exception as e:
        logger.error(f"❌ 扩展内容失败: {str(e)}")
        logger.exception("详细错误信息:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"扩展内容失败: {str(e)}"
        ) 