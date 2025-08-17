#!/usr/bin/env python3
"""
Loguru 日志系统测试脚本
用于验证日志系统是否正常工作
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.logger import setup_logger, get_logger


def test_logger():
    """测试日志系统功能"""
    
    # 初始化日志系统
    print("🔧 初始化日志系统...")
    setup_logger()
    
    # 获取测试日志实例
    logger = get_logger("test_module")
    
    print("\n📝 开始测试不同级别的日志输出...")
    
    # 测试不同级别的日志
    logger.debug("🐛 这是一个 DEBUG 级别的日志消息")
    logger.info("ℹ️ 这是一个 INFO 级别的日志消息")
    logger.success("✅ 这是一个 SUCCESS 级别的日志消息")
    logger.warning("⚠️ 这是一个 WARNING 级别的日志消息")
    logger.error("❌ 这是一个 ERROR 级别的日志消息")
    
    # 测试异常日志
    try:
        1 / 0
    except Exception as e:
        logger.exception("🚨 捕获到异常并记录完整堆栈:")
    
    # 测试结构化日志
    logger.info("📊 用户操作记录", extra={
        "user_id": 12345,
        "action": "upload_file",
        "file_name": "test.pdf",
        "file_size": 1024000
    })
    
    # 测试带变量的日志
    user_name = "张三"
    file_count = 5
    logger.info(f"👤 用户 {user_name} 上传了 {file_count} 个文件")
    
    print("\n✅ 日志测试完成！")
    print("📁 请检查 backend/logs/ 目录下的日志文件:")
    print("   - aippt.log (所有日志)")
    print("   - error.log (错误日志)")


if __name__ == "__main__":
    test_logger()
