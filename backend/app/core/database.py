"""
数据库配置和连接管理
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
from .logger import get_logger

# 初始化日志
logger = get_logger(__name__)

# 创建数据库引擎
logger.info("💾 开始创建数据库引擎")
logger.info(f"🔗 数据库URL: {settings.DATABASE_URL}")

try:
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
    )
    logger.success("✅ 数据库引擎创建成功")
except Exception as e:
    logger.error(f"❌ 数据库引擎创建失败: {str(e)}")
    raise

# 创建会话工厂
logger.debug("🏭 创建数据库会话工厂")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
logger.debug("✅ 会话工厂创建完成")

# 创建基础模型类
logger.debug("📋 创建基础模型类")
Base = declarative_base()
logger.debug("✅ 基础模型类创建完成")

# 元数据
logger.debug("📊 创建元数据对象")
metadata = MetaData()
logger.debug("✅ 元数据对象创建完成")


def get_db():
    """获取数据库会话"""
    logger.debug("🔌 创建数据库会话")
    db = SessionLocal()
    try:
        logger.debug("✅ 数据库会话创建成功")
        yield db
    except Exception as e:
        logger.error(f"❌ 数据库会话异常: {str(e)}")
        logger.exception("详细错误信息:")
        raise
    finally:
        logger.debug("🔐 关闭数据库会话")
        db.close()


def create_tables():
    """创建数据库表"""
    logger.info("🔨 开始创建/检查数据库表")
    
    try:
        # 获取当前所有表名
        from sqlalchemy import inspect
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        logger.debug(f"📋 现有表数量: {len(existing_tables)}")
        
        if existing_tables:
            logger.debug(f"📝 现有表: {existing_tables}")
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        
        # 检查创建后的表
        updated_tables = inspector.get_table_names()
        new_tables = set(updated_tables) - set(existing_tables)
        
        if new_tables:
            logger.info(f"✨ 新创建表: {list(new_tables)}")
        
        logger.success(f"✅ 数据库表创建/检查完成，当前共 {len(updated_tables)} 个表")
        
    except Exception as e:
        logger.error(f"❌ 数据库表创建失败: {str(e)}")
        logger.exception("详细错误信息:")
        raise 