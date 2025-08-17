"""
Loguru 日志配置模块
"""
import os
import sys
from pathlib import Path
from loguru import logger
from app.core.config import settings


def setup_logger():
    """配置 loguru 日志系统"""
    
    # 移除默认的 handler
    logger.remove()
    
    # 创建日志目录
    log_file_path = Path(settings.LOG_FILE)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 控制台输出配置
    logger.add(
        sys.stdout,
        format=settings.LOG_FORMAT,
        level=settings.LOG_LEVEL,
        colorize=True,
        backtrace=True,
        diagnose=True,
        catch=True
    )
    
    # 文件输出配置
    logger.add(
        settings.LOG_FILE,
        format=settings.LOG_FORMAT,
        level=settings.LOG_LEVEL,
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        encoding="utf-8",
        backtrace=True,
        diagnose=True,
        catch=True
    )
    
    # 错误日志单独记录
    error_log_file = log_file_path.parent / "error.log"
    logger.add(
        str(error_log_file),
        format=settings.LOG_FORMAT,
        level="ERROR",
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        encoding="utf-8",
        backtrace=True,
        diagnose=True,
        catch=True
    )
    
    logger.info("📝 日志系统初始化完成")
    logger.info(f"📁 日志文件路径: {settings.LOG_FILE}")
    logger.info(f"📊 日志级别: {settings.LOG_LEVEL}")
    
    return logger


def get_logger(name: str = None):
    """获取 logger 实例
    
    Args:
        name: 模块名称，如果为空则使用调用者的模块名
        
    Returns:
        logger 实例
    """
    if name:
        return logger.bind(name=name)
    else:
        # 自动获取调用者的模块名
        import inspect
        frame = inspect.currentframe().f_back
        module_name = frame.f_globals.get('__name__', 'unknown')
        return logger.bind(name=module_name)


# 创建一个装饰器用于函数调用日志
def log_function_call(func):
    """装饰器：记录函数调用日志"""
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_logger = get_logger(func.__module__)
        func_logger.debug(f"🔄 调用函数: {func.__name__}")
        func_logger.debug(f"📥 参数: args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            func_logger.debug(f"✅ 函数 {func.__name__} 执行成功")
            return result
        except Exception as e:
            func_logger.error(f"❌ 函数 {func.__name__} 执行失败: {str(e)}")
            raise
    
    return wrapper


def log_async_function_call(func):
    """装饰器：记录异步函数调用日志"""
    import functools
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        func_logger = get_logger(func.__module__)
        func_logger.debug(f"🔄 调用异步函数: {func.__name__}")
        func_logger.debug(f"📥 参数: args={args}, kwargs={kwargs}")
        
        try:
            result = await func(*args, **kwargs)
            func_logger.debug(f"✅ 异步函数 {func.__name__} 执行成功")
            return result
        except Exception as e:
            func_logger.error(f"❌ 异步函数 {func.__name__} 执行失败: {str(e)}")
            raise
    
    return wrapper
