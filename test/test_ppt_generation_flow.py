#!/usr/bin/env python3
"""
PPT生成流程完整测试
测试从大纲生成到PPT完成的整个流程
"""

import asyncio
import httpx
import json
import time
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class PPTGenerationTester:
    """PPT生成流程测试器"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
        self.test_data = {}
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def log(self, message, level="INFO"):
        """打印测试日志"""
        timestamp = time.strftime("%H:%M:%S")
        symbols = {
            "INFO": "ℹ️",
            "SUCCESS": "✅", 
            "ERROR": "❌",
            "WARNING": "⚠️",
            "TEST": "🧪"
        }
        print(f"[{timestamp}] {symbols.get(level, 'ℹ️')} {message}")
    
    async def test_step_1_generate_outline(self):
        """测试步骤1：生成大纲"""
        self.log("开始测试步骤1：生成大纲", "TEST")
        
        # 测试数据
        outline_request = {
            "topic": "人工智能在医药的应用",
            "language": "中文",
            "outline_length": "中等"
        }
        
        try:
            self.log(f"发送大纲生成请求: {outline_request}")
            response = await self.client.post(
                f"{self.base_url}/api/v1/ai/generate-outline",
                json=outline_request,
                timeout=30.0
            )
            
            self.log(f"响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                self.test_data["outline"] = result.get("outline_markdown", "")
                self.log(f"大纲生成成功，长度: {len(self.test_data['outline'])} 字符", "SUCCESS")
                self.log(f"大纲内容预览: {self.test_data['outline'][:200]}...")
                return True
            else:
                self.log(f"大纲生成失败: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"大纲生成异常: {str(e)}", "ERROR")
            return False
    
    async def test_step_2_get_templates(self):
        """测试步骤2：获取模板列表"""
        self.log("开始测试步骤2：获取模板列表", "TEST")
        
        try:
            self.log("发送模板列表请求")
            response = await self.client.get(
                f"{self.base_url}/api/v1/templates/",
                timeout=10.0
            )
            
            self.log(f"响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                templates = response.json()
                self.log(f"模板列表获取成功，共 {len(templates)} 个模板", "SUCCESS")
                
                if templates:
                    # 选择第一个模板进行测试
                    self.test_data["template_id"] = templates[0]["id"]
                    self.test_data["template_info"] = templates[0]
                    self.log(f"选择测试模板: {templates[0]['name']} (ID: {templates[0]['id']})")
                    
                    # 显示所有可用模板
                    for template in templates:
                        self.log(f"  - 模板: {template['name']} (ID: {template['id']})")
                    
                    return True
                else:
                    self.log("模板列表为空", "WARNING")
                    return False
            else:
                self.log(f"模板列表获取失败: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"模板列表获取异常: {str(e)}", "ERROR")
            return False
    
    async def test_step_3_generate_content(self):
        """测试步骤3：生成详细内容（可选）"""
        self.log("开始测试步骤3：生成详细内容", "TEST")
        
        content_request = {
            "outline": self.test_data["outline"],
            "template_id": self.test_data["template_id"]
        }
        
        try:
            self.log(f"发送内容生成请求，模板ID: {content_request['template_id']}")
            response = await self.client.post(
                f"{self.base_url}/api/v1/ai/generate-content",
                json=content_request,
                timeout=60.0
            )
            
            self.log(f"响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                self.test_data["content_data"] = result.get("data", {})
                self.log("详细内容生成成功", "SUCCESS")
                self.log(f"内容数据: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}...")
                return True
            else:
                self.log(f"详细内容生成失败: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"详细内容生成异常: {str(e)}", "ERROR")
            return False
    
    async def test_step_4_generate_ppt(self):
        """测试步骤4：生成PPT文件"""
        self.log("开始测试步骤4：生成PPT文件", "TEST")
        
        # 准备PPT生成请求
        ppt_request = {
            "outline": self.test_data["outline"],
            "template_id": self.test_data["template_id"]
        }
        
        try:
            self.log(f"发送PPT生成请求:")
            self.log(f"  - 大纲长度: {len(ppt_request['outline'])} 字符")
            self.log(f"  - 模板ID: {ppt_request['template_id']}")
            self.log(f"  - 模板名称: {self.test_data['template_info']['name']}")
            
            # 发送请求
            response = await self.client.post(
                f"{self.base_url}/api/v1/ai/generate-ppt",
                json=ppt_request,
                timeout=120.0  # PPT生成可能需要更长时间
            )
            
            self.log(f"响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                self.test_data["ppt_result"] = result.get("data", {})
                self.log("PPT生成成功!", "SUCCESS")
                self.log(f"生成结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
                return True
            else:
                self.log(f"PPT生成失败: {response.text}", "ERROR")
                self.log(f"响应内容: {response.content.decode('utf-8', errors='ignore')}")
                return False
                
        except httpx.TimeoutException:
            self.log("PPT生成超时（可能是正常现象，PPT生成需要时间）", "WARNING")
            return False
        except Exception as e:
            self.log(f"PPT生成异常: {str(e)}", "ERROR")
            return False
    
    async def test_direct_pptx_service(self):
        """测试步骤5：直接测试PPTX服务"""
        self.log("开始测试步骤5：直接测试PPTX服务", "TEST")
        
        try:
            # 直接导入和测试PPTX服务
            from backend.app.services.pptx_service import PPTXService
            self.log("PPTX服务导入成功", "SUCCESS")
            
            # 创建服务实例
            pptx_service = PPTXService()
            self.log("PPTX服务实例创建成功", "SUCCESS")
            
            # 测试生成演示文稿
            template_info = self.test_data.get("template_info", {
                "name": "测试模板",
                "description": "测试描述",
                "category": "商务"
            })
            
            content_data = self.test_data.get("content_data", {"slides": []})
            
            self.log("开始直接调用PPTX服务生成演示文稿")
            result = await pptx_service.create_presentation(
                outline=self.test_data["outline"],
                content_data=content_data,
                template_info=template_info
            )
            
            self.log("直接PPTX服务调用成功!", "SUCCESS")
            self.log(f"生成结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return True
            
        except ImportError as e:
            self.log(f"PPTX服务导入失败: {str(e)}", "ERROR")
            return False
        except Exception as e:
            self.log(f"直接PPTX服务调用失败: {str(e)}", "ERROR")
            return False
    
    async def test_server_health(self):
        """测试服务器健康状态"""
        self.log("开始测试服务器健康状态", "TEST")
        
        try:
            response = await self.client.get(f"{self.base_url}/docs")
            if response.status_code == 200:
                self.log("服务器运行正常", "SUCCESS")
                return True
            else:
                self.log(f"服务器响应异常: {response.status_code}", "WARNING")
                return False
        except Exception as e:
            self.log(f"服务器连接失败: {str(e)}", "ERROR")
            return False
    
    async def run_complete_test(self):
        """运行完整测试流程"""
        self.log("🚀 开始PPT生成流程完整测试", "TEST")
        print("=" * 80)
        
        # 测试步骤
        tests = [
            ("服务器健康检查", self.test_server_health),
            ("步骤1: 生成大纲", self.test_step_1_generate_outline),
            ("步骤2: 获取模板列表", self.test_step_2_get_templates),
            ("步骤3: 生成详细内容", self.test_step_3_generate_content),
            ("步骤4: 生成PPT文件", self.test_step_4_generate_ppt),
            ("步骤5: 直接测试PPTX服务", self.test_direct_pptx_service),
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            print("\n" + "-" * 60)
            self.log(f"执行测试: {test_name}")
            
            try:
                result = await test_func()
                results[test_name] = result
                
                if result:
                    self.log(f"✅ {test_name} - 通过")
                else:
                    self.log(f"❌ {test_name} - 失败")
                    
            except Exception as e:
                self.log(f"❌ {test_name} - 异常: {str(e)}", "ERROR")
                results[test_name] = False
        
        # 输出测试总结
        print("\n" + "=" * 80)
        self.log("测试总结:", "TEST")
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{status} - {test_name}")
        
        print("\n" + "-" * 60)
        self.log(f"总计: {passed}/{total} 测试通过", "SUCCESS" if passed == total else "WARNING")
        
        if passed < total:
            self.log("建议检查失败的测试步骤，可能的问题：", "WARNING")
            self.log("1. 服务器未正常启动")
            self.log("2. API路由配置问题") 
            self.log("3. 数据库连接问题")
            self.log("4. 依赖库导入问题")
            self.log("5. 权限或路径问题")


async def main():
    """主函数"""
    print("🧪 PPT生成流程测试工具")
    print("=" * 80)
    
    async with PPTGenerationTester() as tester:
        await tester.run_complete_test()
    
    print("\n🎉 测试完成!")


if __name__ == "__main__":
    asyncio.run(main())
