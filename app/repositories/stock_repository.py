"""
股票基础信息仓库
提供股票数据的 CRUD 操作
"""
from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.postgresql_models import StockBasicInfo
from app.repositories.base import BaseRepository


class StockRepository(BaseRepository[StockBasicInfo]):
    """股票基础信息仓库"""

    def __init__(self, session: AsyncSession):
        super().__init__(StockBasicInfo, session)

    async def get_by_symbol(self, symbol: str, source: str = "akshare") -> Optional[StockBasicInfo]:
        """根据股票代码获取信息"""
        result = await self.session.execute(
            select(StockBasicInfo).where(
                and_(StockBasicInfo.symbol == symbol, StockBasicInfo.source == source)
            )
        )
        return result.scalar_one_or_none()

    async def get_by_industry(self, industry: str, limit: int = 100) -> List[StockBasicInfo]:
        """根据行业获取股票列表"""
        result = await self.session.execute(
            select(StockBasicInfo).where(
                StockBasicInfo.industry == industry
            ).limit(limit)
        )
        return list(result.scalars().all())

    async def search_by_name(self, name: str, limit: int = 20) -> List[StockBasicInfo]:
        """根据名称搜索股票"""
        result = await self.session.execute(
            select(StockBasicInfo).where(
                StockBasicInfo.name.like(f"%{name}%")
            ).limit(limit)
        )
        return list(result.scalars().all())

    async def get_all_stocks(self, skip: int = 0, limit: int = 100) -> List[StockBasicInfo]:
        """获取所有股票（分页）"""
        return await self.get_all(skip=skip, limit=limit)