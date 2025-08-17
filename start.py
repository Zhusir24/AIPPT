#!/usr/bin/env python3
"""
AI-PPTX 一键启动脚本
同时启动HTML前端和后端服务
"""

import os
import sys
import subprocess
import time
import threading
import webbrowser
from pathlib import Path


def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 需要 Python 3.8 或更高版本")
        sys.exit(1)
    print(f"✅ Python 版本: {sys.version}")


def install_dependencies():
    """安装依赖包"""
    print("📥 检查并安装依赖包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖包安装完成")
    except subprocess.CalledProcessError:
        print("❌ 依赖包安装失败")
        sys.exit(1)


def create_env_file():
    """创建环境变量文件"""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists() and env_example.exists():
        print("⚙️ 创建环境变量文件...")
        import shutil
        shutil.copy(env_example, env_file)
        print("💡 请编辑 .env 文件配置您的 AI API 密钥")


def start_backend():
    """启动后端服务"""
    print("🚀 启动后端服务...")
    backend_dir = Path("backend")
    
    if not backend_dir.exists():
        print("❌ backend 目录不存在")
        return None
    
    try:
        # 切换到后端目录并启动服务
        env = os.environ.copy()
        env['PYTHONPATH'] = str(Path.cwd())
        
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=backend_dir,
            env=env
        )
        
        # 等待服务启动
        time.sleep(3)
        
        # 检查服务是否启动成功
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ 后端服务启动成功: http://localhost:8000")
                return process
            else:
                print("❌ 后端服务启动失败")
                return None
        except Exception as e:
            print(f"⚠️ 后端服务可能仍在启动中: {e}")
            return process
            
    except Exception as e:
        print(f"❌ 启动后端服务失败: {e}")
        return None


def start_frontend():
    """启动HTML前端服务"""
    print("🎨 启动HTML前端界面...")
    frontend_dir = Path("frontend_html")
    
    if not frontend_dir.exists():
        print("❌ frontend_html 目录不存在")
        return None
    
    try:
        import http.server
        import socketserver
        import threading
        
        # 切换到前端目录
        original_cwd = os.getcwd()
        
        # 创建HTTP服务器，指定目录
        class QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=frontend_dir, **kwargs)
                
            def do_GET(self):
                # 如果访问根路径，重定向到index.html
                if self.path == '/' or self.path == '':
                    self.path = '/index.html'
                super().do_GET()
                
            def log_message(self, format, *args):
                # 减少日志输出
                pass
        
        httpd = socketserver.TCPServer(("localhost", 8080), QuietHTTPRequestHandler)
        
        # 在新线程中运行服务器
        def run_server():
            httpd.serve_forever()
        
        server_thread = threading.Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()
        
        # 等待前端启动
        time.sleep(2)
        print("✅ HTML前端界面启动成功: http://localhost:8080")
        
        # 返回服务器对象而不是进程
        return httpd
        
    except Exception as e:
        print(f"❌ 启动HTML前端界面失败: {e}")
        # 确保恢复工作目录
        try:
            os.chdir(original_cwd)
        except:
            pass
        return None


def open_browser():
    """打开浏览器"""
    time.sleep(5)  # 等待服务完全启动
    try:
        webbrowser.open("http://localhost:8080")
        print("🌐 已自动打开浏览器")
    except:
        print("⚠️ 无法自动打开浏览器，请手动访问: http://localhost:8080")


def main():
    """主函数"""
    print("=" * 50)
    print("🤖 AI-PPTX 启动器")
    print("=" * 50)
    
    # 检查Python版本
    check_python_version()
    
    # 安装依赖
    install_dependencies()
    
    # 创建环境变量文件
    create_env_file()
    
    # 启动后端服务
    backend_process = start_backend()
    if not backend_process:
        print("❌ 后端服务启动失败，退出")
        sys.exit(1)
    
    # 启动前端服务
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ 前端服务启动失败，退出")
        backend_process.terminate()
        sys.exit(1)
    
    # 在新线程中打开浏览器
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    print("\n" + "=" * 50)
    print("🎉 AI-PPTX 启动完成！")
    print("🌐 HTML前端: http://localhost:8080")
    print("📚 后端API: http://localhost:8000/docs")
    print("💡 按 Ctrl+C 停止服务")
    print("=" * 50)
    
    try:
        # 等待用户中断
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 正在停止服务...")
        
        # 终止服务
        if frontend_process:
            try:
                frontend_process.shutdown()
            except:
                pass
        if backend_process:
            backend_process.terminate()
        
        print("✅ 服务已停止")


if __name__ == "__main__":
    main() 