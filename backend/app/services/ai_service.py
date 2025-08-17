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
    
    def __init__(self, db: Session):
        self.db = db
        self.settings = settings  # 添加settings引用
        self.logger = get_logger(__name__)
        self.logger.debug("🤖 初始化 AI 服务实例")
        self.client = self.setup_openai_client()
    
    def setup_openai_client(self) -> AsyncOpenAI:
        """配置 OpenAI 客户端"""
        self.logger.info("🔧 开始配置 AI 客户端")
        
        # 优先使用 DeepSeek API
        if self.settings.DEEPSEEK_API_KEY:
            self.logger.info("🤖 使用 DeepSeek API")
            self.logger.debug(f"🔗 DeepSeek Base URL: {self.settings.DEEPSEEK_BASE_URL}")
            client = AsyncOpenAI(
                api_key=self.settings.DEEPSEEK_API_KEY,
                base_url=self.settings.DEEPSEEK_BASE_URL
            )
            self.logger.success("✅ DeepSeek 客户端配置成功")
            return client
        elif self.settings.OPENAI_API_KEY:
            self.logger.info("🤖 使用 OpenAI API")
            self.logger.debug(f"🔗 OpenAI Base URL: {self.settings.OPENAI_BASE_URL}")
            client = AsyncOpenAI(
                api_key=self.settings.OPENAI_API_KEY,
                base_url=self.settings.OPENAI_BASE_URL
            )
            self.logger.success("✅ OpenAI 客户端配置成功")
            return client
        else:
            self.logger.error("❌ 未配置任何 AI API 密钥")
            raise ValueError("请配置 AI API 密钥")
    
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
        """获取模型名称，优先使用已配置的API"""
        if self.settings.DEEPSEEK_API_KEY:
            return self.settings.DEEPSEEK_MODEL
        elif self.settings.OPENAI_API_KEY:
            return self.settings.OPENAI_MODEL
        elif self.settings.ANTHROPIC_API_KEY:
            return self.settings.ANTHROPIC_MODEL
        else:
            return "deepseek-chat"  # 默认模型
    
    def get_current_provider(self) -> str:
        """获取当前AI提供商"""
        if self.settings.DEEPSEEK_API_KEY:
            return "DeepSeek"
        elif self.settings.OPENAI_API_KEY:
            return "OpenAI"
        elif self.settings.ANTHROPIC_API_KEY:
            return "Anthropic"
        else:
            return "未配置"
    
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
        try:
            # 尝试解析 JSON 格式的内容
            return json.loads(content)
        except json.JSONDecodeError:
            # 如果不是 JSON 格式，则进行简单的文本解析
            lines = content.strip().split('\n')
            slides = []
            current_slide = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('#'):
                    if current_slide:
                        slides.append(current_slide)
                    
                    title = line.lstrip('#').strip()
                    current_slide = {
                        "type": "content",
                        "title": title,
                        "content": [],
                        "section": len(slides) + 1
                    }
                elif line.startswith('-') and current_slide:
                    current_slide["content"].append(line[1:].strip())
            
            if current_slide:
                slides.append(current_slide)
            
            return {"slides": slides} 