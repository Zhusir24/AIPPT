#!/usr/bin/env python3
"""
更新模板数据库记录
添加模板文件路径和预览图片路径
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.pptx import PPTTemplate


def update_template_paths():
    """更新模板的文件路径和预览图片路径"""
    print("📝 更新模板文件路径...")
    
    db = SessionLocal()
    try:
        # 更新模板路径映射
        template_mappings = [
            {
                "name": "商务蓝",
                "template_file": "templates/business_blue/business_blue.json",
                "preview_image": "templates/business_blue/business_blue.svg"
            },
            {
                "name": "简约白", 
                "template_file": "templates/simple_white/simple_white.json",
                "preview_image": "templates/simple_white/simple_white.svg"
            },
            {
                "name": "活力橙",
                "template_file": "templates/vibrant_orange/vibrant_orange.json", 
                "preview_image": "templates/vibrant_orange/vibrant_orange.svg"
            },
            {
                "name": "自然绿",
                "template_file": "templates/nature_green/nature_green.json", 
                "preview_image": "templates/nature_green/nature_green.svg"
            },
            {
                "name": "科技紫",
                "template_file": "templates/tech_purple/tech_purple.json", 
                "preview_image": "templates/tech_purple/tech_purple.svg"
            }
        ]
        
        updated_count = 0
        for mapping in template_mappings:
            template = db.query(PPTTemplate).filter(
                PPTTemplate.name == mapping["name"]
            ).first()
            
            if template:
                template.template_file = mapping["template_file"]
                template.preview_image = mapping["preview_image"]
                updated_count += 1
                print(f"✅ 更新模板: {mapping['name']}")
            else:
                print(f"⚠️ 未找到模板: {mapping['name']}")
        
        db.commit()
        print(f"🎉 成功更新 {updated_count} 个模板的文件路径")
        
    except Exception as e:
        print(f"❌ 更新模板路径失败: {e}")
        db.rollback()
    finally:
        db.close()


def add_new_templates():
    """添加新的模板记录"""
    print("➕ 添加额外的模板...")
    
    db = SessionLocal()
    try:
        # 检查是否需要添加新模板
        new_templates = [
            {
                "name": "科技紫",
                "description": "现代科技感设计，适合技术演示和创新项目。紫色渐变，体现科技感。",
                "category": "科技",
                "template_file": "templates/json/tech_purple.json",
                "preview_image": "templates/images/tech_purple.svg",
                "is_active": True,
                "sort_order": 13
            },
            {
                "name": "自然绿",
                "description": "清新自然的绿色主题，适合环保、健康相关主题演示。",
                "category": "自然", 
                "template_file": "templates/json/nature_green.json",
                "preview_image": "templates/images/nature_green.svg",
                "is_active": True,
                "sort_order": 14
            }
        ]
        
        added_count = 0
        for template_data in new_templates:
            # 检查是否已存在
            existing = db.query(PPTTemplate).filter(
                PPTTemplate.name == template_data["name"]
            ).first()
            
            if not existing:
                template = PPTTemplate(**template_data)
                db.add(template)
                added_count += 1
                print(f"✅ 添加新模板: {template_data['name']}")
            else:
                print(f"⚠️ 模板已存在: {template_data['name']}")
        
        db.commit()
        print(f"🎉 成功添加 {added_count} 个新模板")
        
    except Exception as e:
        print(f"❌ 添加新模板失败: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """主函数"""
    print("🚀 开始更新模板数据...")
    
    # 更新现有模板的路径
    update_template_paths()
    
    # 添加新模板
    add_new_templates()
    
    print("✨ 模板数据更新完成！")
    print("📊 您可以通过以下方式查看数据:")
    print("  - 启动后端服务: cd backend && python main.py")
    print("  - 访问API文档: http://localhost:8000/docs")
    print("  - 查看模板列表: http://localhost:8000/api/v1/templates/")


if __name__ == "__main__":
    main()