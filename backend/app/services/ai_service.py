"""
AI 服务类
负责调用大语言模型 API 生成内容
"""

from openai import AsyncOpenAI
import asyncio
import json
import re
from typing import AsyncGenerator, Dict, Any, Optional
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.logger import get_logger, log_async_function_call
from ..models.schemas import OutlineGenerateRequest, OutlineGenerateResponse


class AIService:
    """AI 服务类"""
    
    # 类级别的配置存储，用于保持配置状态
    _global_config = {
        "provider": None,
        "model": None,
        "api_key": None,
        "api_url": None,
        "client": None
    }
    
    def __init__(self, db: Session):
        self.db = db
        self.settings = settings  # 添加settings引用
        self.logger = get_logger(__name__)
        self.logger.debug("🤖 初始化 AI 服务实例")
        
        # 动态模型管理
        self.current_provider = None
        self.current_model = None
        self.client = None
        
        # 检查是否有全局配置，如果有则使用，否则初始化默认客户端
        if self._global_config["client"] is not None:
            self.logger.info("🔄 使用已保存的API配置")
            self.current_provider = self._global_config["provider"]
            self.current_model = self._global_config["model"]
            self.client = self._global_config["client"]
            self.logger.success(f"✅ 配置加载成功: {self.current_provider} / {self.current_model}")
        else:
            # 初始化客户端
            self._initialize_default_client()
    
    def _initialize_default_client(self):
        """初始化默认客户端（同步版本）"""
        self.logger.info("🔧 开始初始化默认 AI 客户端")
        
        # 同步方式配置默认客户端
        if self.settings.DEEPSEEK_API_KEY:
            self.logger.info("🤖 使用 DeepSeek API")
            self.current_provider = "DeepSeek"
            self.current_model = self.settings.DEEPSEEK_MODEL
            self.client = AsyncOpenAI(
                api_key=self.settings.DEEPSEEK_API_KEY,
                base_url=self.settings.DEEPSEEK_BASE_URL
            )
            self.logger.success(f"✅ DeepSeek 客户端配置成功: {self.current_model}")
            
        elif self.settings.OPENAI_API_KEY:
            self.logger.info("🤖 使用 OpenAI API")
            self.current_provider = "OpenAI"
            self.current_model = self.settings.OPENAI_MODEL
            self.client = AsyncOpenAI(
                api_key=self.settings.OPENAI_API_KEY,
                base_url=self.settings.OPENAI_BASE_URL
            )
            self.logger.success(f"✅ OpenAI 客户端配置成功: {self.current_model}")
            
        elif self.settings.ANTHROPIC_API_KEY:
            self.logger.info("🤖 使用 Anthropic API")
            self.current_provider = "Anthropic"
            self.current_model = self.settings.ANTHROPIC_MODEL
            self.client = AsyncOpenAI(
                api_key=self.settings.ANTHROPIC_API_KEY,
                base_url="https://api.anthropic.com"
            )
            self.logger.success(f"✅ Anthropic 客户端配置成功: {self.current_model}")
            
        else:
            self.logger.error("❌ 未配置任何 AI API 密钥")
            raise ValueError("请配置 AI API 密钥")
    
    def get_available_models(self) -> Dict[str, Any]:
        """获取所有可用的模型配置"""
        self.logger.debug("📋 获取可用模型列表")
        
        available_models = {
            "providers": [],
            "current_provider": self.current_provider,
            "current_model": self.current_model
        }
        
        # DeepSeek 模型
        if self.settings.DEEPSEEK_API_KEY:
            deepseek_models = {
                "provider": "DeepSeek",
                "base_url": self.settings.DEEPSEEK_BASE_URL,
                "models": [
                    {"name": "deepseek-chat", "display_name": "DeepSeek Chat"},
                    {"name": "deepseek-coder", "display_name": "DeepSeek Coder"}
                ],
                "is_configured": True
            }
            available_models["providers"].append(deepseek_models)
            self.logger.debug(f"✅ DeepSeek 可用，模型数: {len(deepseek_models['models'])}")
        
        # OpenAI 模型
        if self.settings.OPENAI_API_KEY:
            openai_models = {
                "provider": "OpenAI",
                "base_url": self.settings.OPENAI_BASE_URL,
                "models": [
                    {"name": "gpt-4o", "display_name": "GPT-4o"},
                    {"name": "gpt-4o-mini", "display_name": "GPT-4o Mini"},
                    {"name": "gpt-4-turbo", "display_name": "GPT-4 Turbo"},
                    {"name": "gpt-3.5-turbo", "display_name": "GPT-3.5 Turbo"}
                ],
                "is_configured": True
            }
            available_models["providers"].append(openai_models)
            self.logger.debug(f"✅ OpenAI 可用，模型数: {len(openai_models['models'])}")
        
        # Anthropic 模型
        if self.settings.ANTHROPIC_API_KEY:
            anthropic_models = {
                "provider": "Anthropic",
                "base_url": "https://api.anthropic.com",
                "models": [
                    {"name": "claude-3-5-sonnet-20241022", "display_name": "Claude 3.5 Sonnet"},
                    {"name": "claude-3-sonnet-20240229", "display_name": "Claude 3 Sonnet"},
                    {"name": "claude-3-haiku-20240307", "display_name": "Claude 3 Haiku"}
                ],
                "is_configured": True
            }
            available_models["providers"].append(anthropic_models)
            self.logger.debug(f"✅ Anthropic 可用，模型数: {len(anthropic_models['models'])}")
        
        self.logger.info(f"📊 总共找到 {len(available_models['providers'])} 个可用提供商")
        return available_models
    
    async def switch_model(self, provider: str, model: str) -> Dict[str, Any]:
        """切换AI模型"""
        self.logger.info(f"🔄 开始切换模型: {provider} -> {model}")
        
        try:
            # 验证提供商和模型是否可用
            available_models = self.get_available_models()
            provider_found = False
            model_found = False
            
            for p in available_models["providers"]:
                if p["provider"] == provider:
                    provider_found = True
                    for m in p["models"]:
                        if m["name"] == model:
                            model_found = True
                            break
                    break
            
            if not provider_found:
                error_msg = f"提供商 {provider} 未配置或不可用"
                self.logger.error(f"❌ {error_msg}")
                return {"success": False, "message": error_msg}
            
            if not model_found:
                error_msg = f"模型 {model} 在提供商 {provider} 中不可用"
                self.logger.error(f"❌ {error_msg}")
                return {"success": False, "message": error_msg}
            
            # 创建新的客户端
            old_provider = self.current_provider
            old_model = self.current_model
            
            if provider == "DeepSeek":
                self.logger.debug(f"🔧 配置 DeepSeek 客户端，模型: {model}")
                self.client = AsyncOpenAI(
                    api_key=self.settings.DEEPSEEK_API_KEY,
                    base_url=self.settings.DEEPSEEK_BASE_URL
                )
                
            elif provider == "OpenAI":
                self.logger.debug(f"🔧 配置 OpenAI 客户端，模型: {model}")
                self.client = AsyncOpenAI(
                    api_key=self.settings.OPENAI_API_KEY,
                    base_url=self.settings.OPENAI_BASE_URL
                )
                
            elif provider == "Anthropic":
                self.logger.debug(f"🔧 配置 Anthropic 客户端，模型: {model}")
                # 注意：这里需要使用Anthropic的客户端，暂时用OpenAI兼容接口
                self.client = AsyncOpenAI(
                    api_key=self.settings.ANTHROPIC_API_KEY,
                    base_url="https://api.anthropic.com"
                )
            
            # 更新当前配置
            self.current_provider = provider
            self.current_model = model
            
            # 测试新配置
            test_result = await self._test_model_connection()
            
            if test_result["success"]:
                self.logger.success(f"🎉 模型切换成功: {old_provider}/{old_model} -> {provider}/{model}")
                self.logger.info(f"🔗 当前使用: {provider} - {model}")
                
                return {
                    "success": True,
                    "message": f"模型切换成功",
                    "old_provider": old_provider,
                    "old_model": old_model,
                    "new_provider": provider,
                    "new_model": model,
                    "test_result": test_result
                }
            else:
                # 切换失败，回滚到原配置
                self.logger.error(f"❌ 模型连接测试失败，回滚到原配置")
                if old_provider and old_model:
                    self.current_provider = old_provider
                    self.current_model = old_model
                    # 重新配置原来的客户端
                    if old_provider == "DeepSeek":
                        self.client = AsyncOpenAI(
                            api_key=self.settings.DEEPSEEK_API_KEY,
                            base_url=self.settings.DEEPSEEK_BASE_URL
                        )
                    elif old_provider == "OpenAI":
                        self.client = AsyncOpenAI(
                            api_key=self.settings.OPENAI_API_KEY,
                            base_url=self.settings.OPENAI_BASE_URL
                        )
                    elif old_provider == "Anthropic":
                        self.client = AsyncOpenAI(
                            api_key=self.settings.ANTHROPIC_API_KEY,
                            base_url="https://api.anthropic.com"
                        )
                
                return {
                    "success": False,
                    "message": f"模型切换失败: {test_result['message']}",
                    "test_result": test_result
                }
                
        except Exception as e:
            self.logger.error(f"❌ 模型切换异常: {str(e)}")
            self.logger.exception("详细错误信息:")
            return {
                "success": False,
                "message": f"模型切换异常: {str(e)}"
            }
    
    async def _test_model_connection(self) -> Dict[str, Any]:
        """测试当前模型连接"""
        self.logger.debug("🧪 开始测试模型连接")
        
        try:
            # 发送简单的测试请求
            response = await self.client.chat.completions.create(
                model=self.current_model,
                messages=[
                    {"role": "user", "content": "Hello, please respond with 'OK' to confirm the connection."}
                ],
                max_tokens=10,
                temperature=0
            )
            
            content = response.choices[0].message.content.strip()
            self.logger.debug(f"🔍 测试响应: {content}")
            
            if content:
                self.logger.success("✅ 模型连接测试成功")
                return {
                    "success": True,
                    "message": "模型连接正常",
                    "test_response": content
                }
            else:
                self.logger.warning("⚠️ 模型响应为空")
                return {
                    "success": False,
                    "message": "模型响应为空"
                }
                
        except Exception as e:
            self.logger.error(f"❌ 模型连接测试失败: {str(e)}")
            return {
                "success": False,
                "message": f"连接测试失败: {str(e)}"
            }
    
    async def generate_outline(self, request: OutlineGenerateRequest) -> OutlineGenerateResponse:
        """生成内容大纲"""
        self.logger.info("📝 开始生成内容大纲")
        self.logger.debug(f"📋 请求参数: topic={request.topic}, language={request.language}, length={request.outline_length}")
        
        try:
            # 构建提示词
            self.logger.debug("🔨 构建大纲生成提示词")
            prompt = self._build_outline_prompt(request)
            self.logger.debug(f"📝 提示词长度: {len(prompt)} 字符")
            
            # 获取模型名称
            model_name = self._get_model_name()
            self.logger.info(f"🤖 使用模型: {model_name}")
            
            # 调用 AI API
            self.logger.info("⚡ 开始调用 AI API 生成大纲")
            response = await self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "你是一个专业的 PPT 内容策划师，擅长创建结构清晰、内容丰富的演示文稿大纲。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            self.logger.success("✅ AI API 调用成功")
            
            # 处理响应
            content = response.choices[0].message.content
            self.logger.info(f"📊 生成内容长度: {len(content)} 字符")
            self.logger.debug(f"📄 生成内容预览: {content[:200]}...")
            
            # 解析大纲树结构
            self.logger.debug("🌲 解析大纲树结构")
            outline_tree = self._parse_outline_to_tree(content)
            self.logger.info(f"🔢 解析出 {len(outline_tree)} 个主要章节")
            
            self.logger.success("🎉 大纲生成完成")
            return OutlineGenerateResponse(
                outline_markdown=content,
                outline_tree=outline_tree,
                status="success"
            )
            
        except Exception as e:
            self.logger.error(f"❌ 生成大纲失败: {str(e)}")
            self.logger.exception("详细错误信息:")
            return OutlineGenerateResponse(
                outline_markdown="",
                outline_tree=[],
                status="error",
                error_message=str(e)
            )
    
    async def generate_outline_stream(self, request: OutlineGenerateRequest) -> AsyncGenerator[str, None]:
        """流式生成内容大纲"""
        self.logger.info("🌊 开始流式生成内容大纲")
        self.logger.debug(f"📋 请求参数: topic={request.topic}, language={request.language}, length={request.outline_length}")
        
        try:
            # 构建提示词
            self.logger.debug("🔨 构建流式大纲生成提示词")
            prompt = self._build_outline_prompt(request)
            self.logger.debug(f"📝 提示词长度: {len(prompt)} 字符")
            
            # 获取模型名称
            model_name = self._get_model_name()
            self.logger.info(f"🤖 使用模型: {model_name}")
            
            # 调用流式 AI API
            self.logger.info("⚡ 开始调用流式 AI API")
            stream = await self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "你是一个专业的 PPT 内容策划师，擅长创建结构清晰、内容丰富的演示文稿大纲。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                stream=True
            )
            
            self.logger.success("✅ 流式 API 调用成功，开始接收数据流")
            
            chunk_count = 0
            total_content = ""
            
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    chunk_count += 1
                    content_chunk = chunk.choices[0].delta.content
                    total_content += content_chunk
                    
                    if chunk_count % 10 == 0:  # 每10个chunk记录一次
                        self.logger.debug(f"📦 已接收 {chunk_count} 个数据块，当前内容长度: {len(total_content)}")
                    
                    yield content_chunk
            
            self.logger.success(f"🎉 流式生成完成，共接收 {chunk_count} 个数据块，总长度: {len(total_content)} 字符")
                    
        except Exception as e:
            self.logger.error(f"❌ 流式生成大纲失败: {str(e)}")
            self.logger.exception("详细错误信息:")
            yield f"错误: {str(e)}"
    
    async def generate_content(self, outline: str, template_info: Dict[str, Any]) -> Dict[str, Any]:
        """根据大纲生成详细内容"""
        self.logger.info("📄 开始生成详细内容")
        self.logger.debug(f"📝 大纲长度: {len(outline)} 字符")
        self.logger.debug(f"🎨 模板信息: {template_info}")
        
        try:
            # 构建内容生成提示词
            self.logger.debug("🔨 构建内容生成提示词")
            prompt = self._build_content_prompt(outline, template_info)
            self.logger.debug(f"📝 提示词长度: {len(prompt)} 字符")
            
            # 获取模型名称
            model_name = self._get_model_name()
            self.logger.info(f"🤖 使用模型: {model_name}")
            
            # 调用 AI API 生成内容
            self.logger.info("⚡ 开始调用 AI API 生成详细内容")
            response = await self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "你是一个专业的内容创作师，能够根据大纲创建详细的演示文稿内容。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            self.logger.success("✅ 内容生成 API 调用成功")
            
            # 处理生成的内容
            content = response.choices[0].message.content
            self.logger.info(f"📊 生成内容长度: {len(content)} 字符")
            self.logger.debug(f"📄 生成内容预览: {content[:300]}...")
            
            # 解析内容为幻灯片结构
            self.logger.debug("🎯 解析内容为幻灯片结构")
            parsed_slides = self._parse_content_to_slides(content)
            self.logger.info(f"🔢 解析出 {len(parsed_slides.get('slides', []))} 张幻灯片")
            
            self.logger.success("🎉 详细内容生成完成")
            return parsed_slides
            
        except Exception as e:
            self.logger.error(f"❌ 生成详细内容失败: {str(e)}")
            self.logger.exception("详细错误信息:")
            return {"error": str(e), "slides": []}
    
    async def expand_content(self, section_title: str, current_content: str) -> str:
        """扩展指定章节的内容"""
        self.logger.info("🔍 开始扩展章节内容")
        self.logger.info(f"📝 章节标题: {section_title}")
        self.logger.debug(f"📄 当前内容长度: {len(current_content)} 字符")
        self.logger.debug(f"📄 当前内容预览: {current_content[:200]}...")
        
        try:
            # 构建扩展提示词
            self.logger.debug("🔨 构建内容扩展提示词")
            prompt = f"""
请扩展以下章节的内容，使其更加详细和丰富：

章节标题：{section_title}
当前内容：{current_content}

要求：
1. 保持原有内容的核心观点
2. 增加更多细节和例子
3. 确保内容逻辑清晰
4. 字数增加50-100%
"""
            self.logger.debug(f"📝 提示词长度: {len(prompt)} 字符")
            
            # 获取模型名称
            model_name = self._get_model_name()
            self.logger.info(f"🤖 使用模型: {model_name}")
            
            # 调用 AI API 扩展内容
            self.logger.info("⚡ 开始调用 AI API 扩展内容")
            response = await self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "你是一个专业的内容扩展师，擅长丰富和完善现有内容。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=1500
            )
            
            self.logger.success("✅ 内容扩展 API 调用成功")
            
            # 处理扩展后的内容
            expanded_content = response.choices[0].message.content
            self.logger.info(f"📊 扩展后内容长度: {len(expanded_content)} 字符")
            self.logger.info(f"📈 内容增长: {len(expanded_content) - len(current_content)} 字符")
            self.logger.debug(f"📄 扩展后内容预览: {expanded_content[:300]}...")
            
            self.logger.success("🎉 内容扩展完成")
            return expanded_content
            
        except Exception as e:
            self.logger.error(f"❌ 扩展内容失败: {str(e)}")
            self.logger.exception("详细错误信息:")
            return f"扩展失败: {str(e)}"
    
    def _get_model_name(self) -> str:
        """获取当前使用的模型名称"""
        return self.current_model if self.current_model else "deepseek-chat"
    
    def get_current_provider(self) -> str:
        """获取当前AI提供商"""
        return self.current_provider if self.current_provider else "未配置"
    
    def _build_outline_prompt(self, request: OutlineGenerateRequest) -> str:
        """构建大纲生成提示词"""
        length_map = {
            "简短": "3-5个主要章节",
            "中等": "5-8个主要章节", 
            "详细": "8-12个主要章节"
        }
        
        sections_requirement = length_map.get(request.outline_length, "5-8个主要章节")
        
        prompt = f"""
请为以下主题创建一个详细的PPT演示大纲：

主题：{request.topic}
目标受众：{request.target_audience or '一般受众'}
演示时长：{request.presentation_duration or '15-20分钟'}
大纲详细程度：{request.outline_length}（{sections_requirement}）
演示语言：{request.language}

额外要求：
{request.additional_requirements or '无特殊要求'}

请按照以下格式输出大纲：

# 演示主题

## 1. 开场引入
- 问候和自我介绍
- 主题概述
- 演示大纲预览

## 2. [主要章节标题]
- [主要观点1]
  - [支撑细节]
  - [例子或数据]
- [主要观点2]
  - [支撑细节]

## 3. [主要章节标题]
...

## 结束语
- 总结要点
- 行动呼吁
- 感谢和问答

要求：
1. 大纲结构清晰，逻辑性强
2. 每个章节都有具体的内容要点
3. 适合{request.presentation_duration or '15-20分钟'}的演示时长
4. 内容实用且有价值
5. 使用{request.language}语言"""

        return prompt
    
    def _build_content_prompt(self, outline: str, template_info: Dict[str, Any]) -> str:
        """构建内容生成提示词"""
        template_name = template_info.get('name', '默认模板')
        template_style = template_info.get('description', '简洁专业风格')
        
        prompt = f"""
基于以下大纲，为每个章节生成详细的演示内容：

大纲：
{outline}

模板信息：
- 模板名称：{template_name}
- 风格特点：{template_style}

请为每个章节生成：
1. 标题页内容
2. 详细内容页
3. 关键要点总结

输出格式（JSON）：
{{
  "slides": [
    {{
      "type": "title",
      "title": "章节标题",
      "subtitle": "副标题或概述",
      "section": 1
    }},
    {{
      "type": "content", 
      "title": "内容标题",
      "content": [
        "要点1：详细说明",
        "要点2：详细说明"
      ],
      "section": 1
    }}
  ]
}}

要求：
1. 内容详实具体，避免空泛表述
2. 适合演示文稿的表达方式
3. 每页内容量适中，便于阅读
4. 保持风格一致性"""

        return prompt
    
    def _parse_outline_to_tree(self, markdown_content: str) -> list:
        """将 Markdown 大纲解析为树形结构"""
        lines = markdown_content.strip().split('\n')
        tree = []
        current_section = None
        current_subsection = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 主标题 (# 或 ##)
            if line.startswith('# ') or line.startswith('## '):
                if line.startswith('# '):
                    title = line[2:].strip()
                else:
                    title = line[3:].strip()
                    
                current_section = {
                    "title": title,
                    "level": 1,
                    "children": []
                }
                tree.append(current_section)
                current_subsection = None
                
            # 子标题 (### 或更多)
            elif line.startswith('###'):
                if current_section:
                    subtitle = line[3:].strip()
                    current_subsection = {
                        "title": subtitle,
                        "level": 2,
                        "children": []
                    }
                    current_section["children"].append(current_subsection)
                    
            # 列表项
            elif line.startswith('- '):
                content = line[2:].strip()
                item = {
                    "title": content,
                    "level": 3,
                    "children": []
                }
                
                if current_subsection:
                    current_subsection["children"].append(item)
                elif current_section:
                    current_section["children"].append(item)
        
        return tree
    
    def _parse_content_to_slides(self, content: str) -> Dict[str, Any]:
        """解析生成的内容为幻灯片格式"""
        self.logger.debug(f"🔍 开始解析内容，长度: {len(content)} 字符")
        self.logger.debug(f"📄 内容前500字符: {content[:500]}...")
        
        try:
            # 尝试解析 JSON 格式的内容
            parsed_json = json.loads(content)
            self.logger.debug("✅ 内容为JSON格式，直接返回")
            return parsed_json
        except json.JSONDecodeError:
            self.logger.debug("⚠️ 内容非JSON格式，进行文本解析")
            # 如果不是 JSON 格式，则进行简单的文本解析
            lines = content.strip().split('\n')
            slides = []
            current_slide = None
            
            self.logger.debug(f"📝 总行数: {len(lines)}")
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('#'):
                    if current_slide:
                        slides.append(current_slide)
                        self.logger.debug(f"📄 完成幻灯片: {current_slide['title']}")
                    
                    title = line.lstrip('#').strip()
                    current_slide = {
                        "type": "content",
                        "title": title,
                        "content": [],
                        "section": len(slides) + 1
                    }
                    self.logger.debug(f"🆕 新幻灯片: {title}")
                elif line.startswith('-') and current_slide:
                    current_slide["content"].append(line[1:].strip())
                    self.logger.debug(f"➕ 添加内容: {line[1:].strip()}")
            
            if current_slide:
                slides.append(current_slide)
                self.logger.debug(f"📄 完成最后幻灯片: {current_slide['title']}")
            
            self.logger.debug(f"🎯 解析完成，共 {len(slides)} 张幻灯片")
            return {"slides": slides}
    
    def _apply_custom_config(self, api_key: str, api_url: str, model_name: str):
        """应用自定义API配置"""
        from openai import AsyncOpenAI
        
        self.logger.info(f"🔧 应用自定义配置: {api_url} / {model_name}")
        
        self.current_provider = "Custom"
        self.current_model = model_name
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=api_url
        )
        
        # 更新全局配置
        self._global_config.update({
            "provider": "Custom",
            "model": model_name,
            "api_key": api_key,
            "api_url": api_url,
            "client": self.client
        })
        
        self.logger.success(f"✅ 自定义客户端配置成功: {model_name}")
        
    def _apply_openai_config(self, api_key: str):
        """应用OpenAI配置"""
        from openai import AsyncOpenAI
        
        self.logger.info("🔧 应用OpenAI配置")
        
        self.current_provider = "OpenAI"
        self.current_model = "gpt-3.5-turbo"
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.openai.com/v1"
        )
        
        # 更新全局配置
        self._global_config.update({
            "provider": "OpenAI",
            "model": "gpt-3.5-turbo",
            "api_key": api_key,
            "api_url": "https://api.openai.com/v1",
            "client": self.client
        })
        
        self.logger.success(f"✅ OpenAI客户端配置成功: {self.current_model}")
        
    def _apply_deepseek_config(self, api_key: str):
        """应用DeepSeek配置"""
        from openai import AsyncOpenAI
        
        self.logger.info("🔧 应用DeepSeek配置")
        
        self.current_provider = "DeepSeek"
        self.current_model = "deepseek-chat"
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"
        )
        
        # 更新全局配置
        self._global_config.update({
            "provider": "DeepSeek",
            "model": "deepseek-chat",
            "api_key": api_key,
            "api_url": "https://api.deepseek.com/v1",
            "client": self.client
        })
        
        self.logger.success(f"✅ DeepSeek客户端配置成功: {self.current_model}") 