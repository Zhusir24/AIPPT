#!/usr/bin/env python3
"""
AI-PPTX HTML前端启动服务器
使用Python内置HTTP服务器提供静态文件服务
"""

import os
import sys
import http.server
import socketserver
import webbrowser
from pathlib import Path

# 配置
HOST = 'localhost'
PORT = 8080
FRONTEND_DIR = 'frontend_html'

def main():
    """启动HTML前端服务器"""
    
    # 检查前端目录是否存在
    frontend_path = Path(__file__).parent / FRONTEND_DIR
    if not frontend_path.exists():
        print(f"❌ 错误：前端目录 {FRONTEND_DIR} 不存在")
        print("请确保已经创建了HTML前端文件")
        return 1
    
    # 切换到前端目录
    os.chdir(frontend_path)
    
    print("🚀 启动 AI-PPTX HTML 前端服务器...")
    print(f"📂 前端目录：{frontend_path.absolute()}")
    print(f"🌐 服务地址：http://{HOST}:{PORT}")
    print("🔗 后端服务：http://localhost:8000 (请确保后端服务已启动)")
    print()
    
    # 创建HTTP服务器
    class QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        """安静的HTTP请求处理器，减少日志输出"""
        
        def log_message(self, format, *args):
            # 只记录重要信息
            if "GET / " in format % args or "404" in format % args:
                super().log_message(format, *args)
    
    try:
        with socketserver.TCPServer((HOST, PORT), QuietHTTPRequestHandler) as httpd:
            print(f"✅ HTTP 服务器启动成功，监听 {HOST}:{PORT}")
            print("📱 正在自动打开浏览器...")
            
            # 自动打开浏览器
            try:
                webbrowser.open(f"http://{HOST}:{PORT}")
            except:
                print("⚠️  无法自动打开浏览器，请手动访问上述地址")
            
            print()
            print("💡 使用提示：")
            print("   - 确保后端服务运行在 http://localhost:8000")
            print("   - 如需停止服务，请按 Ctrl+C")
            print("   - 修改前端文件后，刷新浏览器即可看到更新")
            print()
            print("🎯 开始使用 AI-PPTX 生成您的演示文稿吧！")
            print("-" * 50)
            
            # 启动服务器
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
        return 0
    
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ 端口 {PORT} 已被占用")
            print(f"请尝试其他端口或停止占用 {PORT} 端口的程序")
        else:
            print(f"❌ 启动服务器失败：{e}")
        return 1
    
    except Exception as e:
        print(f"❌ 未知错误：{e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
