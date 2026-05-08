"""
PostgreSQL 数据库连接管理模块
使用 SQLAlchemy 2.0 + asyncpg 实现异步数据库操作
"""
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text

logger = logging.getLogger(__name__)

Base = declarative_base()


class DatabaseManager:
    """PostgreSQL 数据库连接管理器"""

    def __init__(self):
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[sessionmaker] = None
        self._connected = False

    async def init_postgresql(self):
        """初始化 PostgreSQL 连接"""
        try:
            from app.core.config import settings

            logger.info("🔄 正在初始化 PostgreSQL 连接...")

            self.engine = create_async_engine(
                settings.POSTGRES_URL,
                max_overflow=settings.POSTGRES_MAX_CONNECTIONS - settings.POSTGRES_MIN_CONNECTIONS,
                pool_size=settings.POSTGRES_MIN_CONNECTIONS,
                pool_pre_ping=True,
                echo=False,
            )

            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))

            self.session_factory = sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )

            self._connected = True
            logger.info("✅ PostgreSQL 连接成功建立")
            logger.info(f"📊 数据库: {settings.POSTGRES_DB}")
            logger.info(f"🔗 连接池: {settings.POSTGRES_MIN_CONNECTIONS}-{settings.POSTGRES_MAX_CONNECTIONS}")

        except Exception as e:
            logger.error(f"❌ PostgreSQL 连接失败: {e}")
            self._connected = False
            raise

    async def close(self):
        """关闭数据库连接"""
        if self.engine:
            await self.engine.dispose()
            self._connected = False
            logger.info("✅ PostgreSQL 连接已关闭")

    async def health_check(self) -> bool:
        """健康检查"""
        try:
            if self.engine:
                async with self.engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                return True
            return False
        except Exception as e:
            logger.error(f"PostgreSQL 健康检查失败: {e}")
            return False


db_manager = DatabaseManager()


async def init_database():
    """初始化数据库连接"""
    await db_manager.init_postgresql()


async def close_database():
    """关闭数据库连接"""
    await db_manager.close()


async def get_session() -> AsyncSession:
    """获取数据库会话"""
    if not db_manager.session_factory:
        raise RuntimeError("数据库未初始化")
    return db_manager.session_factory()


get_db = get_session