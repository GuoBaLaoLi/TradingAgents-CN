"""
Token 使用统计仓库
提供 Token 数据的 CRUD 操作
"""
from typing import List
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.postgresql_models import TokenUsage
from app.repositories.base import BaseRepository


class UsageRepository(BaseRepository[TokenUsage]):
    """Token 使用统计仓库"""

    def __init__(self, session: AsyncSession):
        super().__init__(TokenUsage, session)

    async def get_by_session(self, session_id: str) -> List[TokenUsage]:
        """根据会话 ID 获取使用记录"""
        result = await self.session.execute(
            select(TokenUsage).where(TokenUsage.session_id == session_id)
        )
        return list(result.scalars().all())

    async def get_by_provider(self, provider: str, limit: int = 100) -> List[TokenUsage]:
        """根据供应商获取使用记录"""
        result = await self.session.execute(
            select(TokenUsage).where(TokenUsage.provider == provider).limit(limit)
        )
        return list(result.scalars().all())

    async def get_total_cost(self, days: int = 30) -> float:
        """获取指定天数内的总成本"""
        cutoff = datetime.now() - timedelta(days=days)
        result = await self.session.execute(
            select(func.sum(TokenUsage.cost)).where(TokenUsage.timestamp >= cutoff)
        )
        return result.scalar() or 0.0