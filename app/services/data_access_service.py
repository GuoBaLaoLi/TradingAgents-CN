"""
统一数据访问服务
提供所有数据仓库的集中访问
"""
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.postgresql import get_session
from app.repositories.stock_repository import StockRepository
from app.repositories.market_repository import MarketRepository
from app.repositories.user_repository import UserRepository
from app.repositories.usage_repository import UsageRepository

logger = logging.getLogger(__name__)


class DataAccessService:
    """统一数据访问服务"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.stock = StockRepository(session)
        self.market = MarketRepository(session)
        self.user = UserRepository(session)
        self.usage = UsageRepository(session)

    @staticmethod
    async def create() -> "DataAccessService":
        """创建数据访问服务实例"""
        session = await get_session()
        return DataAccessService(session)

    async def close(self):
        """关闭会话"""
        await self.session.close()


async def get_data_access() -> DataAccessService:
    """获取数据访问服务"""
    return await DataAccessService.create()