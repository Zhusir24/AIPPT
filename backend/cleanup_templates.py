#!/usr/bin/env python3
"""
清理模板数据库记录
只保留有实际配置文件的模板
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.pptx import PPTTemplate


def cleanup_templates():
    """清理模板数据库，只保留有实际文件的模板"""
    print("🧹 开始清理模板数据库...")
    
    db = SessionLocal()
    try:
        # 定义有实际文件的模板
        valid_templates = [
            {
                "name": "商务蓝",
                "description": "专业的商务风格，适合企业演示和工作汇报。采用蓝色系配色，简洁大方。",
                "category": "商务",
                "template_file": "templates/business_blue/business_blue.json",
                "preview_image": "templates/business_blue/business_blue.svg",
                "is_active": True,
                "sort_order": 1
            },
            {
                "name": "简约白",
                "description": "简洁清爽的设计，适合学术演示和技术分享。白色背景，突出内容重点。",
                "category": "简约",
                "template_file": "templates/simple_white/simple_white.json",
                "preview_image": "templates/simple_white/simple_white.svg",
                "is_active": True,
                "sort_order": 2
            },
            {
                "name": "活力橙",
                "description": "充满活力的色彩搭配，适合创意展示和产品发布。橙色系设计，富有感染力。",
                "category": "创意",
                "template_file": "templates/vibrant_orange/vibrant_orange.json",
                "preview_image": "templates/vibrant_orange/vibrant_orange.svg",
                "is_active": True,
                "sort_order": 3
            },
            {
                "name": "科技紫",
                "description": "现代科技感设计，适合技术演示和创新项目。紫色渐变，体现科技感。",
                "category": "科技",
                "template_file": "templates/tech_purple/tech_purple.json",
                "preview_image": "templates/tech_purple/tech_purple.svg",
                "is_active": True,
                "sort_order": 4
            },
            {
                "name": "自然绿",
                "description": "清新自然的绿色主题，适合环保、健康相关主题演示。",
                "category": "自然",
                "template_file": "templates/nature_green/nature_green.json",
                "preview_image": "templates/nature_green/nature_green.svg",
                "is_active": True,
                "sort_order": 5
            }
        ]
        
        # 验证模板文件是否存在
        valid_templates_verified = []
        for template in valid_templates:
            template_path = project_root / template["template_file"]
            preview_path = project_root / template["preview_image"]
            
            if template_path.exists() and preview_path.exists():
                valid_templates_verified.append(template)
                print(f"✅ 验证模板文件存在: {template['name']}")
            else:
                print(f"❌ 模板文件不存在: {template['name']}")
                if not template_path.exists():
                    print(f"   缺少配置文件: {template_path}")
                if not preview_path.exists():
                    print(f"   缺少预览图: {preview_path}")
        
        # 清空现有模板数据
        deleted_count = db.query(PPTTemplate).delete()
        print(f"🗑️ 删除了 {deleted_count} 个旧模板记录")
        
        # 插入有效的模板数据
        added_count = 0
        for template_data in valid_templates_verified:
            template = PPTTemplate(**template_data)
            db.add(template)
            added_count += 1
            print(f"➕ 添加模板: {template_data['name']}")
        
        db.commit()
        print(f"✅ 成功添加 {added_count} 个有效模板")
        
        # 验证结果
        final_count = db.query(PPTTemplate).count()
        print(f"📊 当前数据库中共有 {final_count} 个模板")
        
    except Exception as e:
        print(f"❌ 清理模板数据失败: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """主函数"""
    print("🚀 开始清理模板数据...")
    cleanup_templates()
    print("✨ 模板数据清理完成！")
    print("📊 您可以通过以下方式验证结果:")
    print("  - 启动后端服务: cd backend && python main.py")
    print("  - 访问API文档: http://localhost:8000/docs")
    print("  - 查看模板列表: http://localhost:8000/api/v1/templates/")


if __name__ == "__main__":
    main()