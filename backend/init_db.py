#!/usr/bin/env python3
"""
数据库初始化脚本
创建数据库表并插入示例模板数据
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from sqlalchemy.orm import Session
from app.core.database import engine, SessionLocal
from app.models.pptx import PPTTemplate, Base


def create_tables():
    """创建数据库表"""
    print("📚 创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建完成")


def insert_sample_templates():
    """插入示例模板数据"""
    print("🎨 插入示例模板数据...")
    
    db = SessionLocal()
    try:
        # 检查是否已有模板数据
        existing_count = db.query(PPTTemplate).count()
        if existing_count > 0:
            print(f"⚠️ 已存在 {existing_count} 个模板，跳过插入")
            return
        
        # 示例模板数据
        sample_templates = [
            {
                "name": "商务蓝",
                "description": "专业的商务风格，适合企业演示和工作汇报。采用蓝色系配色，简洁大方。",
                "category": "商务",
                "is_active": True,
                "sort_order": 1
            },
            {
                "name": "简约白",
                "description": "简洁清爽的设计，适合学术演示和技术分享。白色背景，突出内容重点。",
                "category": "简约",
                "is_active": True,
                "sort_order": 2
            },
            {
                "name": "活力橙",
                "description": "充满活力的色彩搭配，适合创意展示和产品发布。橙色系设计，富有感染力。",
                "category": "创意",
                "is_active": True,
                "sort_order": 3
            },
            {
                "name": "科技紫",
                "description": "现代科技感设计，适合技术演示和创新项目。紫色渐变，体现科技感。",
                "category": "科技",
                "is_active": True,
                "sort_order": 4
            },
            {
                "name": "自然绿",
                "description": "清新自然的绿色主题，适合环保、健康相关主题演示。",
                "category": "自然",
                "is_active": True,
                "sort_order": 5
            },
            {
                "name": "优雅灰",
                "description": "优雅的灰色调设计，适合正式场合和高端商务演示。",
                "category": "商务",
                "is_active": True,
                "sort_order": 6
            },
            {
                "name": "温暖红",
                "description": "温暖的红色系设计，适合节日庆典和热情主题演示。",
                "category": "庆典",
                "is_active": True,
                "sort_order": 7
            },
            {
                "name": "深海蓝",
                "description": "深沉的蓝色调，适合金融、稳重类主题演示。",
                "category": "金融",
                "is_active": True,
                "sort_order": 8
            },
            {
                "name": "粉色浪漫",
                "description": "浪漫的粉色系设计，适合女性产品、美容相关主题。",
                "category": "时尚",
                "is_active": True,
                "sort_order": 9
            },
            {
                "name": "金色奢华",
                "description": "金色的奢华设计，适合高端品牌、豪华产品展示。",
                "category": "奢华",
                "is_active": True,
                "sort_order": 10
            },
            {
                "name": "极简黑白",
                "description": "极简的黑白配色，适合艺术展示和概念性演示。",
                "category": "艺术",
                "is_active": True,
                "sort_order": 11
            },
            {
                "name": "彩虹渐变",
                "description": "多彩的渐变设计，适合儿童教育、创意设计主题。",
                "category": "教育",
                "is_active": True,
                "sort_order": 12
            }
        ]
        
        # 插入模板数据
        for template_data in sample_templates:
            template = PPTTemplate(**template_data)
            db.add(template)
        
        db.commit()
        print(f"✅ 成功插入 {len(sample_templates)} 个示例模板")
        
    except Exception as e:
        print(f"❌ 插入模板数据失败: {e}")
        db.rollback()
    finally:
        db.close()


def init_database():
    """初始化数据库"""
    print("🚀 开始初始化数据库...")
    
    # 创建表
    create_tables()
    
    # 插入示例数据
    insert_sample_templates()
    
    print("🎉 数据库初始化完成！")
    print("📊 您可以通过以下方式查看数据:")
    print("  - 启动后端服务: python main.py")
    print("  - 访问API文档: http://localhost:8000/docs")
    print("  - 查看模板列表: http://localhost:8000/api/v1/templates/")


if __name__ == "__main__":
    init_database() 