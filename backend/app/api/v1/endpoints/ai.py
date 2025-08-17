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
    OutlineGenerateRequest, OutlineGenerateResponse, BaseResponse, ContentGenerateRequest,
    APIConfigTestRequest, APIConfigTestResponse, APIConfigRequest
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
        if request.target_audience:
            logger.info(f"👥 目标受众: {request.target_audience}")
        if request.presentation_duration:
            logger.info(f"⏱️ 演示时长: {request.presentation_duration}")
        if request.additional_requirements:
            logger.info(f"📋 额外要求: {request.additional_requirements}")
        
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
    logger.info("🚀🚀🚀 PPT生成请求已到达后端! 🚀🚀🚀")
    logger.info("📊 开始生成完整 PPT 文件")
    logger.info(f"📋 请求参数: outline长度={len(request.outline)}, template_id={request.template_id}")
    logger.debug(f"📋 详细请求参数: {request.dict()}")
    
    print("🚀🚀🚀 PPT生成请求已到达后端!")
    print(f"📊 模板ID: {request.template_id}")
    print(f"📄 大纲长度: {len(request.outline)} 字符")
    
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
        try:
            from ...services.pptx_service import PPTXService
            logger.debug("✅ PPTX 服务导入成功")
            pptx_service = PPTXService()
            logger.debug("✅ PPTX 服务实例创建成功")
        except ImportError as e:
            logger.error(f"❌ PPTX 服务导入失败: {str(e)}")
            # 尝试另一种导入方式
            try:
                import sys
                import os
                sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
                from app.services.pptx_service import PPTXService
                logger.debug("✅ PPTX 服务导入成功（备用方式）")
                pptx_service = PPTXService()
                logger.debug("✅ PPTX 服务实例创建成功")
            except Exception as e2:
                logger.error(f"❌ PPTX 服务导入彻底失败: {str(e2)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"无法导入PPT生成服务: {str(e2)}"
                )
        
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


@router.get("/models")
async def get_available_models(db: Session = Depends(get_db)):
    """获取所有可用的AI模型"""
    logger.info("📋 获取可用AI模型列表")
    
    try:
        logger.debug("🤖 创建 AI 服务实例")
        service = AIService(db)
        
        logger.info("🔍 查询可用模型配置")
        models_info = service.get_available_models()
        
        logger.success(f"✅ 获取模型列表成功，共 {len(models_info['providers'])} 个提供商")
        logger.info(f"🔗 当前使用: {models_info['current_provider']} - {models_info['current_model']}")
        
        return BaseResponse(
            success=True,
            message="获取可用模型成功",
            data=models_info
        )
        
    except Exception as e:
        logger.error(f"❌ 获取可用模型失败: {str(e)}")
        logger.exception("详细错误信息:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取可用模型失败: {str(e)}"
        )


@router.post("/switch-model")
async def switch_model(
    provider: str,
    model: str,
    db: Session = Depends(get_db)
):
    """切换AI模型"""
    logger.info(f"🔄 开始切换AI模型: {provider} -> {model}")
    
    try:
        logger.debug("🤖 创建 AI 服务实例")
        service = AIService(db)
        
        logger.info(f"⚡ 执行模型切换: {provider} / {model}")
        result = await service.switch_model(provider, model)
        
        if result["success"]:
            logger.success(f"🎉 模型切换成功: {result['old_provider']}/{result['old_model']} -> {result['new_provider']}/{result['new_model']}")
            logger.info(f"🧪 连接测试结果: {result['test_result']['message']}")
            
            return BaseResponse(
                success=True,
                message="模型切换成功",
                data=result
            )
        else:
            logger.error(f"❌ 模型切换失败: {result['message']}")
            return BaseResponse(
                success=False,
                message=result["message"],
                data=result
            )
        
    except Exception as e:
        logger.error(f"❌ 模型切换异常: {str(e)}")
        logger.exception("详细错误信息:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"模型切换失败: {str(e)}"
        )


@router.post("/test-model")
async def test_current_model(db: Session = Depends(get_db)):
    """测试当前模型连接"""
    logger.info("🧪 开始测试当前模型连接")
    
    try:
        logger.debug("🤖 创建 AI 服务实例")
        service = AIService(db)
        
        logger.info(f"🔗 当前模型: {service.get_current_provider()} - {service._get_model_name()}")
        logger.info("⚡ 执行连接测试")
        
        test_result = await service._test_model_connection()
        
        if test_result["success"]:
            logger.success(f"✅ 模型连接测试成功: {test_result['message']}")
            logger.debug(f"📝 测试响应: {test_result.get('test_response', '无响应')}")
        else:
            logger.error(f"❌ 模型连接测试失败: {test_result['message']}")
        
        return BaseResponse(
            success=test_result["success"],
            message=test_result["message"],
            data={
                "current_provider": service.get_current_provider(),
                "current_model": service._get_model_name(),
                "test_result": test_result
            }
        )
        
    except Exception as e:
        logger.error(f"❌ 模型测试异常: {str(e)}")
        logger.exception("详细错误信息:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"模型测试失败: {str(e)}"
        )


@router.post("/test-api-config", response_model=APIConfigTestResponse)
async def test_api_config(
    config: APIConfigTestRequest,
    db: Session = Depends(get_db)
):
    """测试指定的API配置连接"""
    logger.info(f"🧪 开始测试API配置连接 - 提供商: {config.provider}")
    
    # 记录详细的配置信息（敏感信息已脱敏）
    config_info = {
        "provider": config.provider,
        "api_key": f"{config.api_key[:8]}***{config.api_key[-4:]}" if config.api_key else "未设置",
        "custom_api_url": config.custom_api_url,
        "custom_model_name": config.custom_model_name
    }
    logger.info(f"📋 API配置信息: {config_info}")
    
    try:
        import time
        import openai
        from openai import OpenAI
        
        start_time = time.time()
        
        # 根据提供商配置客户端
        if config.provider == "openai":
            logger.info("🔗 配置OpenAI客户端")
            client = OpenAI(
                api_key=config.api_key,
                base_url="https://api.openai.com/v1"
            )
            model_name = "gpt-3.5-turbo"
            
        elif config.provider == "deepseek":
            logger.info("🔗 配置DeepSeek客户端")
            client = OpenAI(
                api_key=config.api_key,
                base_url="https://api.deepseek.com/v1"
            )
            model_name = "deepseek-chat"
            
        elif config.provider == "anthropic":
            logger.error("❌ Anthropic 测试暂未实现")
            return APIConfigTestResponse(
                success=False,
                message="Anthropic API测试功能暂未实现",
                provider=config.provider,
                model_name=None
            )
            
        elif config.provider == "custom":
            logger.info(f"🔗 配置自定义API客户端: {config.custom_api_url}")
            if not config.custom_api_url or not config.custom_model_name:
                logger.error("❌ 自定义API配置不完整")
                return APIConfigTestResponse(
                    success=False,
                    message="自定义API配置需要提供API地址和模型名称",
                    provider=config.provider,
                    model_name=config.custom_model_name
                )
            
            # 验证API URL格式
            import urllib.parse
            parsed_url = urllib.parse.urlparse(config.custom_api_url)
            if not parsed_url.scheme or not parsed_url.netloc:
                logger.error(f"❌ 无效的API URL格式: {config.custom_api_url}")
                return APIConfigTestResponse(
                    success=False,
                    message=f"API地址格式不正确: {config.custom_api_url}。请确保包含完整的URL（如: https://api.example.com/v1）",
                    provider=config.provider,
                    model_name=config.custom_model_name
                )
            
            # 基本连通性测试
            try:
                import requests
                test_url = config.custom_api_url.rstrip('/') + '/models'
                logger.info(f"🧪 测试API端点连通性: {test_url}")
                
                response = requests.get(
                    test_url,
                    headers={"Authorization": f"Bearer {config.api_key}"},
                    timeout=5
                )
                logger.info(f"📡 端点响应状态: {response.status_code}")
            except requests.exceptions.ConnectionError:
                logger.warning("⚠️ 无法连接到API端点，但将继续尝试聊天接口测试")
            except requests.exceptions.Timeout:
                logger.warning("⚠️ API端点连接超时，但将继续尝试聊天接口测试")
            except Exception as e:
                logger.warning(f"⚠️ 端点测试异常: {str(e)}，但将继续尝试聊天接口测试")
            
            client = OpenAI(
                api_key=config.api_key,
                base_url=config.custom_api_url
            )
            model_name = config.custom_model_name
        
        else:
            logger.error(f"❌ 不支持的提供商: {config.provider}")
            return APIConfigTestResponse(
                success=False,
                message=f"不支持的API提供商: {config.provider}",
                provider=config.provider,
                model_name=None
            )
        
        # 执行测试请求
        logger.info(f"⚡ 发送测试请求到模型: {model_name}")
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "user", "content": config.test_message}
                ],
                max_tokens=50,
                timeout=10
            )
        except openai.NotFoundError as e:
            logger.error(f"❌ 模型未找到 (404错误): {model_name}")
            logger.error(f"💡 可能的原因:")
            logger.error(f"   1. 模型名称不正确，请检查拼写")
            logger.error(f"   2. API服务不支持该模型")
            logger.error(f"   3. API端点URL配置错误")
            
            # 提供常见模型名称建议
            model_suggestions = []
            if "qwen" in model_name.lower():
                model_suggestions = ["qwen2.5-coder-plus", "qwen-plus", "qwen2.5-plus", "qwen-max"]
            elif "gpt" in model_name.lower():
                model_suggestions = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
            elif "claude" in model_name.lower():
                model_suggestions = ["claude-3-haiku", "claude-3-sonnet", "claude-3-opus"]
            
            suggestion_text = ""
            if model_suggestions:
                suggestion_text = f"\n💡 建议尝试的模型名称: {', '.join(model_suggestions)}"
            
            return APIConfigTestResponse(
                success=False,
                message=f"模型 '{model_name}' 未找到 (404错误)。请检查模型名称是否正确，或确认API服务支持该模型。{suggestion_text}",
                provider=config.provider,
                model_name=model_name
            )
        except openai.AuthenticationError as e:
            logger.error(f"❌ API认证失败: {str(e)}")
            return APIConfigTestResponse(
                success=False,
                message="API密钥认证失败，请检查API密钥是否正确",
                provider=config.provider,
                model_name=model_name
            )
        except openai.PermissionDeniedError as e:
            logger.error(f"❌ API权限被拒绝: {str(e)}")
            return APIConfigTestResponse(
                success=False,
                message="API访问权限被拒绝，请检查API密钥权限设置",
                provider=config.provider,
                model_name=model_name
            )
        except openai.APIConnectionError as e:
            logger.error(f"❌ API连接失败: {str(e)}")
            return APIConfigTestResponse(
                success=False,
                message=f"无法连接到API服务器，请检查网络连接和API地址配置: {config.custom_api_url}",
                provider=config.provider,
                model_name=model_name
            )
        
        end_time = time.time()
        latency = round((end_time - start_time) * 1000, 2)  # 毫秒
        
        response_text = response.choices[0].message.content
        logger.success(f"✅ API配置测试成功 - 延迟: {latency}ms")
        logger.debug(f"📝 测试响应: {response_text[:100]}...")
        
        return APIConfigTestResponse(
            success=True,
            message=f"连接成功！模型响应正常，延迟 {latency}ms",
            provider=config.provider,
            model_name=model_name,
            response_preview=response_text[:100] + "..." if len(response_text) > 100 else response_text,
            latency=latency
        )
        
    except openai.AuthenticationError as e:
        logger.error(f"❌ API认证失败: {str(e)}")
        return APIConfigTestResponse(
            success=False,
            message=f"API密钥认证失败: {str(e)}",
            provider=config.provider,
            model_name=model_name if 'model_name' in locals() else None
        )
        
    except openai.APIConnectionError as e:
        logger.error(f"❌ API连接失败: {str(e)}")
        return APIConfigTestResponse(
            success=False,
            message=f"无法连接到API服务器: {str(e)}",
            provider=config.provider,
            model_name=model_name if 'model_name' in locals() else None
        )
        
    except openai.RateLimitError as e:
        logger.error(f"❌ API请求限制: {str(e)}")
        return APIConfigTestResponse(
            success=False,
            message=f"API请求频率限制: {str(e)}",
            provider=config.provider,
            model_name=model_name if 'model_name' in locals() else None
        )
        
    except Exception as e:
        logger.error(f"❌ API配置测试异常: {str(e)}")
        logger.exception("详细错误信息:")
        return APIConfigTestResponse(
            success=False,
            message=f"测试失败: {str(e)}",
            provider=config.provider,
            model_name=model_name if 'model_name' in locals() else None
        )


@router.post("/save-api-config")
async def save_api_config(
    config: APIConfigRequest,
    db: Session = Depends(get_db)
):
    """保存API配置设置"""
    logger.info(f"💾 开始保存API配置 - 提供商: {config.provider}")
    
    # 记录详细的配置信息（敏感信息已脱敏）
    config_info = {
        "provider": config.provider,
        "api_key": f"{config.api_key[:8]}***{config.api_key[-4:]}" if config.api_key else "未设置",
        "custom_api_url": config.custom_api_url,
        "custom_model_name": config.custom_model_name
    }
    logger.info(f"📋 保存的API配置: {config_info}")
    
    try:
        import time
        
        # 保存配置并立即应用
        logger.info("🔄 保存配置并立即切换到新的API配置")
        
        # 创建AI服务实例来应用配置
        service = AIService(db)
        
        # 根据提供商类型确定切换参数
        if config.provider == "custom":
            if not config.custom_api_url or not config.custom_model_name:
                raise ValueError("自定义API配置需要提供API地址和模型名称")
            
            # 为自定义配置设置特殊的provider名称和模型名称
            provider_name = f"custom-{config.custom_api_url}"
            model_name = config.custom_model_name
            
            # 临时设置自定义配置到服务中
            logger.info(f"🛠️ 应用自定义API配置: {config.custom_api_url} / {model_name}")
            service._apply_custom_config(config.api_key, config.custom_api_url, model_name)
            
        elif config.provider == "openai":
            provider_name = "OpenAI"
            model_name = "gpt-3.5-turbo"
            service._apply_openai_config(config.api_key)
            
        elif config.provider == "deepseek":
            provider_name = "DeepSeek"
            model_name = "deepseek-chat"
            service._apply_deepseek_config(config.api_key)
            
        else:
            raise ValueError(f"不支持的API提供商: {config.provider}")
        
        logger.success(f"✅ API配置保存并应用成功 - 提供商: {config.provider}")
        logger.info(f"🎯 当前使用: {provider_name} / {model_name}")
        
        return BaseResponse(
            success=True,
            message=f"API配置保存成功，已切换到 {provider_name} ({model_name})",
            data={
                "provider": provider_name,
                "model": model_name,
                "timestamp": time.time(),
                "config_saved": True,
                "applied": True
            }
        )
        
    except Exception as e:
        logger.error(f"❌ 保存API配置失败: {str(e)}")
        logger.exception("详细错误信息:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"保存API配置失败: {str(e)}"
        ) 