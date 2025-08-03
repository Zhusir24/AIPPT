#!/usr/bin/env python3
"""
AI-PPTX 系统测试脚本
测试各个模块的基本功能
"""

import sys
import requests
import time
from pathlib import Path


def test_backend_health():
    """测试后端健康状态"""
    print("🔍 测试后端健康状态...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 后端服务正常: {result.get('message')}")
            return True
        else:
            print(f"❌ 后端服务异常: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 后端连接失败: {e}")
        return False


def test_api_endpoints():
    """测试API端点"""
    print("🔍 测试API端点...")
    
    base_url = "http://localhost:8000/api/v1"
    
    # 测试模板列表API
    try:
        response = requests.get(f"{base_url}/templates/", timeout=10)
        if response.status_code == 200:
            templates = response.json()
            print(f"✅ 模板API正常: 返回 {len(templates)} 个模板")
        else:
            print(f"❌ 模板API异常: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 模板API测试失败: {e}")
    
    # 测试AI生成API (需要配置API密钥)
    print("⚠️ AI生成API需要配置API密钥才能测试")


def test_frontend_access():
    """测试前端访问"""
    print("🔍 测试前端访问...")
    try:
        response = requests.get("http://localhost:8501", timeout=10)
        if response.status_code == 200:
            print("✅ 前端界面可访问")
            return True
        else:
            print(f"❌ 前端访问异常: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 前端连接失败: {e}")
        return False


def test_database():
    """测试数据库"""
    print("🔍 测试数据库...")
    try:
        # 检查数据库文件
        db_file = Path("ai_pptx.db")
        if db_file.exists():
            print("✅ 数据库文件存在")
        else:
            print("⚠️ 数据库文件不存在，可能需要初始化")
        
        # 通过API测试数据库连接
        response = requests.get("http://localhost:8000/api/v1/templates/", timeout=5)
        if response.status_code == 200:
            print("✅ 数据库连接正常")
            return True
        else:
            print("❌ 数据库连接异常")
            return False
            
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return False


def test_file_structure():
    """测试文件结构"""
    print("🔍 测试文件结构...")
    
    required_dirs = [
        "backend",
        "frontend", 
        "uploads",
        "templates",
        "static"
    ]
    
    required_files = [
        "requirements.txt",
        "README.md",
        "backend/main.py",
        "frontend/main.py",
        "start.py"
    ]
    
    all_good = True
    
    # 检查目录
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ 目录存在: {dir_path}")
        else:
            print(f"❌ 目录缺失: {dir_path}")
            all_good = False
    
    # 检查文件
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ 文件存在: {file_path}")
        else:
            print(f"❌ 文件缺失: {file_path}")
            all_good = False
    
    return all_good


def main():
    """主测试函数"""
    print("=" * 60)
    print("🤖 AI-PPTX 系统测试")
    print("=" * 60)
    
    print("\n📂 1. 测试文件结构")
    test_file_structure()
    
    print("\n💾 2. 测试数据库")
    test_database()
    
    print("\n🔧 3. 测试后端服务")
    backend_ok = test_backend_health()
    
    if backend_ok:
        print("\n📡 4. 测试API端点")
        test_api_endpoints()
    else:
        print("\n❌ 后端服务未启动，跳过API测试")
    
    print("\n🎨 5. 测试前端界面")
    test_frontend_access()
    
    print("\n" + "=" * 60)
    print("🏁 测试完成")
    print("=" * 60)
    
    # 测试建议
    print("\n💡 建议:")
    print("1. 如果后端服务未启动，请运行: python start.py")
    print("2. 如果数据库未初始化，请运行: cd backend && python init_db.py")
    print("3. 如果需要使用AI功能，请在.env文件中配置API密钥")
    print("4. 详细使用说明请查看 README.md")


if __name__ == "__main__":
    main() 