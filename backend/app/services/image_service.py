"""
图片服务类
负责图片搜索和处理功能
"""

import requests
import json
from typing import List, Dict, Any, Optional
from urllib.parse import quote
import time
import random
from pathlib import Path
from PIL import Image
import io

from ..core.config import settings


class ImageService:
    """图片服务类"""
    
    def __init__(self):
        self.unsplash_access_key = getattr(settings, 'UNSPLASH_ACCESS_KEY', None)
        self.static_dir = Path(settings.STATIC_DIR) / "images"
        self.static_dir.mkdir(parents=True, exist_ok=True)
        
        # 预定义的图片关键词库
        self.keyword_mapping = {
            "business": ["business", "office", "meeting", "corporate", "finance", "professional"],
            "technology": ["technology", "computer", "innovation", "digital", "data", "coding"],
            "nature": ["nature", "forest", "environment", "green", "earth", "sustainability"],
            "education": ["education", "learning", "books", "school", "knowledge", "study"],
            "health": ["health", "medical", "wellness", "healthcare", "fitness", "hospital"],
            "creative": ["creative", "art", "design", "colorful", "inspiration", "innovation"],
            "teamwork": ["teamwork", "collaboration", "team", "cooperation", "group", "partnership"],
            "growth": ["growth", "success", "development", "progress", "achievement", "improvement"],
            "communication": ["communication", "discussion", "presentation", "speaking", "networking"],
            "strategy": ["strategy", "planning", "goal", "target", "objective", "vision"],
            "default": ["abstract", "background", "minimal", "modern", "clean", "professional"]
        }
    
    async def search_images(self, keyword: str, category: str = None, count: int = 3, timeout: int = 5) -> List[Dict[str, Any]]:
        """搜索图片"""
        try:
            # 快速返回模式：直接返回空列表，跳过图片搜索
            # 避免外部API调用导致的卡死问题
            print(f"⚠️ 跳过图片搜索以避免卡死：{keyword} - {category}")
            return []
            
            # 原有的图片搜索逻辑暂时注释掉
            # # 根据类别和关键词生成搜索词
            # search_terms = self._generate_search_terms(keyword, category)
            # 
            # images = []
            # for search_term in search_terms[:count]:
            #     if self.unsplash_access_key:
            #         # 使用Unsplash API
            #         image_data = await self._search_unsplash(search_term)
            #         if image_data:
            #             images.append(image_data)
            #     else:
            #         # 使用预设图片或占位符
            #         image_data = self._get_placeholder_image(search_term, category)
            #         images.append(image_data)
            #     
            #     # 避免API限制
            #     time.sleep(0.1)
            # 
            # return images
            
        except Exception as e:
            print(f"图片搜索失败: {e}")
            return self._get_fallback_images(count)
    
    def _generate_search_terms(self, keyword: str, category: str = None) -> List[str]:
        """生成搜索词"""
        terms = []
        
        # 基于关键词直接搜索
        if keyword:
            terms.append(keyword)
        
        # 基于类别生成搜索词
        if category:
            category_lower = category.lower()
            if "商务" in category or "business" in category_lower:
                terms.extend(self.keyword_mapping["business"])
            elif "科技" in category or "tech" in category_lower:
                terms.extend(self.keyword_mapping["technology"])
            elif "自然" in category or "nature" in category_lower:
                terms.extend(self.keyword_mapping["nature"])
            elif "教育" in category or "education" in category_lower:
                terms.extend(self.keyword_mapping["education"])
            elif "创意" in category or "creative" in category_lower:
                terms.extend(self.keyword_mapping["creative"])
            else:
                terms.extend(self.keyword_mapping["default"])
        
        # 如果没有搜索词，使用默认词
        if not terms:
            terms = self.keyword_mapping["default"]
        
        # 随机选择并去重
        random.shuffle(terms)
        return list(dict.fromkeys(terms))  # 去重但保持顺序
    
    async def _search_unsplash(self, query: str) -> Optional[Dict[str, Any]]:
        """通过Unsplash API搜索图片"""
        try:
            url = f"https://api.unsplash.com/search/photos"
            headers = {
                "Authorization": f"Client-ID {self.unsplash_access_key}"
            }
            params = {
                "query": query,
                "per_page": 1,
                "orientation": "landscape"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data["results"]:
                    photo = data["results"][0]
                    return {
                        "url": photo["urls"]["regular"],
                        "thumbnail": photo["urls"]["thumb"],
                        "description": photo.get("alt_description", query),
                        "author": photo["user"]["name"],
                        "source": "unsplash"
                    }
            
        except Exception as e:
            print(f"Unsplash API搜索失败: {e}")
        
        return None
    
    def _get_placeholder_image(self, keyword: str, category: str = None) -> Dict[str, Any]:
        """获取占位符图片"""
        # 生成颜色基于类别
        colors = {
            "商务": "#2563eb",
            "科技": "#7c3aed", 
            "自然": "#16a34a",
            "创意": "#ea580c",
            "简约": "#6b7280"
        }
        
        color = colors.get(category, "#6b7280").replace("#", "")
        
        # 使用图片占位符服务
        placeholder_url = f"https://via.placeholder.com/800x450/{color}/ffffff?text={quote(keyword)}"
        
        return {
            "url": placeholder_url,
            "thumbnail": placeholder_url,
            "description": f"{keyword} - {category}",
            "author": "Placeholder",
            "source": "placeholder"
        }
    
    def _get_fallback_images(self, count: int) -> List[Dict[str, Any]]:
        """获取后备图片"""
        fallback_images = []
        colors = ["3b82f6", "8b5cf6", "10b981", "f59e0b", "ef4444"]
        
        for i in range(count):
            color = colors[i % len(colors)]
            fallback_images.append({
                "url": f"https://via.placeholder.com/800x450/{color}/ffffff?text=Image+{i+1}",
                "thumbnail": f"https://via.placeholder.com/400x225/{color}/ffffff?text=Image+{i+1}",
                "description": f"Fallback image {i+1}",
                "author": "System",
                "source": "fallback"
            })
        
        return fallback_images
    
    async def download_and_process_image(self, image_url: str, target_size: tuple = (800, 450)) -> Optional[str]:
        """下载并处理图片"""
        try:
            response = requests.get(image_url, timeout=30)
            if response.status_code == 200:
                # 打开图片
                image = Image.open(io.BytesIO(response.content))
                
                # 调整大小
                image = image.resize(target_size, Image.Resampling.LANCZOS)
                
                # 生成文件名
                timestamp = int(time.time())
                filename = f"image_{timestamp}_{random.randint(1000, 9999)}.jpg"
                file_path = self.static_dir / filename
                
                # 保存图片
                if image.mode in ("RGBA", "P"):
                    image = image.convert("RGB")
                image.save(file_path, "JPEG", quality=85)
                
                return str(file_path.relative_to(Path.cwd()))
            
        except Exception as e:
            print(f"下载图片失败: {e}")
        
        return None
    
    def get_image_keywords_from_content(self, content: str) -> List[str]:
        """从内容中提取图片关键词"""
        keywords = []
        
        # 基于内容关键词匹配
        content_lower = content.lower()
        
        # 预定义关键词检测
        keyword_patterns = {
            "数据": ["data", "chart", "graph"],
            "团队": ["team", "collaboration", "meeting"],
            "技术": ["technology", "computer", "innovation"],
            "市场": ["market", "business", "growth"],
            "产品": ["product", "design", "innovation"],
            "战略": ["strategy", "planning", "target"],
            "分析": ["analysis", "data", "research"],
            "发展": ["development", "growth", "progress"],
            "管理": ["management", "leadership", "organization"],
            "创新": ["innovation", "creative", "idea"]
        }
        
        for chinese_keyword, english_keywords in keyword_patterns.items():
            if chinese_keyword in content:
                keywords.extend(english_keywords)
        
        # 如果没有找到关键词，使用通用词
        if not keywords:
            keywords = ["business", "professional", "modern"]
        
        return keywords[:3]  # 限制关键词数量