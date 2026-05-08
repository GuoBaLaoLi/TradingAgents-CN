"""
实时行情仓库
提供行情数据的 CRUD 操作
"""
from typing import Optional, List
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.postgresql_models import MarketQuotes
from app.repositories.base import BaseRepository


class MarketRepository(BaseRepository[MarketQuotes]):
    """实时行情仓库"""

    def __init__(self, session: AsyncSession):
        super().__init__(MarketQuotes, session)

    async def get_by_symbol(self, symbol: str) -> Optional[MarketQuotes]:
        """根据股票代码获取行情"""
        result = await self.session.execute(
            select(MarketQuotes).where(MarketQuotes.symbol == symbol)
        )
        return result.scalar_one_or_none()

    async def get_top_gainers(self, limit: int = 10) -> List[MarketQuotes]:
        """获取涨幅榜"""
        result = await self.session.execute(
            select(MarketQuotes)
            .order_by(desc(MarketQuotes.pct_chg))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_top_losers(self, limit: int = 10) -> List[MarketQuotes]:
        """获取跌幅榜"""
        result = await self.session.execute(
            select(MarketQuotes)
            .order_by(MarketQuotes.pct_chg)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_symbols(self, symbols: List[str]) -> List[MarketQuotes]:
        """根据多个股票代码批量获取行情"""
        result = await self.session.execute(
            select(MarketQuotes).where(MarketQuotes.symbol.in_(symbols))
        )
        return list(result.scalars().all())