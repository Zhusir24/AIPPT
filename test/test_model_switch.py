#!/usr/bin/env python3
"""
模型切换功能测试脚本
测试后端动态模型切换和日志记录
"""

import sys
import os
import asyncio
import json
import requests
import time
from pathlib import Path

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# API基础URL
BASE_URL = "http://localhost:8000/api/v1/ai"

def test_api_connectivity():
    """测试API连接"""
    print("🔌 测试API连接...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ API连接正常: {health_data['message']}")
            return True
        else:
            print(f"❌ API连接异常: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API连接失败: {str(e)}")
        print("请确保后端服务正在运行 (python start.py)")
        return False

def get_available_models():
    """获取可用模型列表"""
    print("\n📋 获取可用模型列表...")
    try:
        response = requests.get(f"{BASE_URL}/models", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                models_data = result["data"]
                print(f"✅ 获取模型列表成功")
                print(f"🔗 当前模型: {models_data['current_provider']} - {models_data['current_model']}")
                print(f"📊 可用提供商数量: {len(models_data['providers'])}")
                
                for provider in models_data["providers"]:
                    print(f"\n🏢 {provider['provider']}:")
                    print(f"   🔗 Base URL: {provider['base_url']}")
                    print(f"   📋 可用模型:")
                    for model in provider["models"]:
                        print(f"      - {model['name']}: {model['display_name']}")
                
                return models_data
            else:
                print(f"❌ 获取模型列表失败: {result.get('message', '未知错误')}")
                return None
        else:
            print(f"❌ API请求失败: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 获取模型列表异常: {str(e)}")
        return None

def test_current_model():
    """测试当前模型连接"""
    print("\n🧪 测试当前模型连接...")
    try:
        response = requests.post(f"{BASE_URL}/test-model", timeout=15)
        if response.status_code == 200:
            result = response.json()
            test_data = result["data"]
            test_result = test_data["test_result"]
            
            print(f"🔗 当前模型: {test_data['current_provider']} - {test_data['current_model']}")
            
            if test_result["success"]:
                print(f"✅ 模型连接测试成功: {test_result['message']}")
                print(f"📝 测试响应: {test_result.get('test_response', '无响应')}")
                return True
            else:
                print(f"❌ 模型连接测试失败: {test_result['message']}")
                return False
        else:
            print(f"❌ API请求失败: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 模型测试异常: {str(e)}")
        return False

def switch_model(provider, model):
    """切换模型"""
    print(f"\n🔄 切换模型: {provider} -> {model}")
    try:
        payload = {
            "provider": provider,
            "model": model
        }
        
        response = requests.post(
            f"{BASE_URL}/switch-model", 
            params=payload,
            timeout=20
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                switch_data = result["data"]
                print(f"🎉 模型切换成功!")
                print(f"   📈 从: {switch_data.get('old_provider', '未知')}/{switch_data.get('old_model', '未知')}")
                print(f"   📉 到: {switch_data.get('new_provider', '未知')}/{switch_data.get('new_model', '未知')}")
                
                test_result = switch_data.get("test_result", {})
                if test_result.get("success"):
                    print(f"   ✅ 连接测试: {test_result.get('message', '成功')}")
                    print(f"   📝 测试响应: {test_result.get('test_response', '无响应')}")
                else:
                    print(f"   ⚠️ 连接测试: {test_result.get('message', '失败')}")
                
                return True
            else:
                print(f"❌ 模型切换失败: {result.get('message', '未知错误')}")
                switch_data = result.get("data", {})
                test_result = switch_data.get("test_result", {})
                if test_result:
                    print(f"   🔍 测试结果: {test_result.get('message', '无详情')}")
                return False
        else:
            print(f"❌ API请求失败: HTTP {response.status_code}")
            if response.text:
                print(f"   📝 响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 模型切换异常: {str(e)}")
        return False

def get_current_provider_info():
    """获取当前提供商信息"""
    print("\n🔍 获取当前AI提供商信息...")
    try:
        response = requests.get(f"{BASE_URL}/provider", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                provider_data = result["data"]
                print(f"✅ 当前提供商: {provider_data['provider']}")
                print(f"🤖 当前模型: {provider_data['model']}")
                return provider_data
            else:
                print(f"❌ 获取提供商信息失败: {result.get('message', '未知错误')}")
                return None
        else:
            print(f"❌ API请求失败: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 获取提供商信息异常: {str(e)}")
        return None

def main():
    """主测试函数"""
    print("=" * 60)
    print("🤖 AI模型切换功能测试")
    print("=" * 60)
    
    # 1. 测试API连接
    if not test_api_connectivity():
        print("\n❌ 无法连接到后端API，测试终止")
        return
    
    # 2. 获取可用模型
    models_data = get_available_models()
    if not models_data:
        print("\n❌ 无法获取模型列表，测试终止")
        return
    
    # 3. 测试当前模型
    test_current_model()
    
    # 4. 获取当前提供商信息
    get_current_provider_info()
    
    # 5. 模型切换测试
    if len(models_data["providers"]) > 0:
        print(f"\n🔄 开始模型切换测试...")
        
        for provider_info in models_data["providers"]:
            provider = provider_info["provider"]
            models = provider_info["models"]
            
            if len(models) > 0:
                # 尝试切换到第一个可用模型
                target_model = models[0]["name"]
                current_provider = models_data["current_provider"]
                current_model = models_data["current_model"]
                
                # 如果不是当前模型，则切换
                if provider != current_provider or target_model != current_model:
                    print(f"\n🎯 测试切换到: {provider} - {target_model}")
                    success = switch_model(provider, target_model)
                    
                    if success:
                        # 切换成功后测试连接
                        time.sleep(1)
                        test_current_model()
                        
                        # 更新当前状态
                        models_data["current_provider"] = provider
                        models_data["current_model"] = target_model
                    
                    time.sleep(2)  # 等待一下再进行下次测试
    
    print("\n" + "=" * 60)
    print("✅ 模型切换功能测试完成")
    print("📝 请查看后端日志文件获取详细的切换过程记录:")
    print("   - backend/logs/aippt.log")
    print("   - backend/logs/error.log")
    print("=" * 60)

if __name__ == "__main__":
    main()
