# PostgreSQL 数据模型适配实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 创建数据访问仓库类，实现从 MongoDB 到 PostgreSQL 的数据操作转换。

**Architecture:** 使用 SQLAlchemy 2.0 异步查询，创建专用的 Repository 类封装数据访问逻辑。

**Tech Stack:** SQLAlchemy 2.0, asyncpg, Repository 模式

---

## 任务 1: 创建股票基础信息仓库

**Files:**
- Create: `app/repositories/stock_repository.py`

- [ ] **Step 1: 创建股票基础信息仓库类**

```python
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
```

- [ ] **Step 2: 测试仓库类**

Run: `python3 -c "from app.repositories.stock_repository import StockRepository; print('StockRepository 导入成功')"`
Expected: 输出 "StockRepository 导入成功"

- [ ] **Step 3: 提交**

```bash
git add app/repositories/stock_repository.py
git commit -m "feat: add StockRepository for stock basic info"
```

---

## 任务 2: 创建实时行情仓库

**Files:**
- Create: `app/repositories/market_repository.py`

- [ ] **Step 1: 创建实时行情仓库类**

```python
"""
实时行情仓库
提供行情数据的 CRUD 操作
"""
from typing import Optional, List
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

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
```

- [ ] **Step 2: 测试仓库类**

Run: `python3 -c "from app.repositories.market_repository import MarketRepository; print('MarketRepository 导入成功')"`
Expected: 输出 "MarketRepository 导入成功"

- [ ] **Step 3: 提交**

```bash
git add app/repositories/market_repository.py
git commit -m "feat: add MarketRepository for market quotes"
```

---

## 任务 3: 创建用户仓库

**Files:**
- Create: `app/repositories/user_repository.py`

- [ ] **Step 1: 创建用户仓库类**

```python
"""
用户仓库
提供用户数据的 CRUD 操作
"""
from typing import Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.postgresql_models import Users
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[Users]):
    """用户仓库"""

    def __init__(self, session: AsyncSession):
        super().__init__(Users, session)

    async def get_by_username(self, username: str) -> Optional[Users]:
        """根据用户名获取用户"""
        result = await self.session.execute(
            select(Users).where(Users.username == username)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[Users]:
        """根据邮箱获取用户"""
        result = await self.session.execute(
            select(Users).where(Users.email == email)
        )
        return result.scalar_one_or_none()

    async def authenticate(self, username: str, password: str) -> Optional[Users]:
        """验证用户登录"""
        from app.utils.security import verify_password
        
        user = await self.get_by_username(username)
        if user and verify_password(password, user.hashed_password):
            return user
        return None
```

- [ ] **Step 2: 测试仓库类**

Run: `python3 -c "from app.repositories.user_repository import UserRepository; print('UserRepository 导入成功')"`
Expected: 输出 "UserRepository 导入成功"

- [ ] **Step 3: 提交**

```bash
git add app/repositories/user_repository.py
git commit -m "feat: add UserRepository for user management"
```

---

## 任务 4: 创建 Token 使用统计仓库

**Files:**
- Create: `app/repositories/usage_repository.py`

- [ ] **Step 1: 创建 Token 统计仓库类**

```python
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

    async def get_provider_stats(self, days: int = 30) -> dict:
        """获取供应商使用统计"""
        cutoff = datetime.now() - timedelta(days=days)
        result = await self.session.execute(
            select(
                TokenUsage.provider,
                func.count(TokenUsage.id).label('count'),
                func.sum(TokenUsage.input_tokens).label('input_tokens'),
                func.sum(TokenUsage.output_tokens).label('output_tokens'),
                func.sum(TokenUsage.cost).label('total_cost')
            ).where(TokenUsage.timestamp >= cutoff).group_by(TokenUsage.provider)
        )
        return {row[0]: {'count': row[1], 'input': row[2], 'output': row[3], 'cost': row[4]} for row in result.fetchall()}
```

- [ ] **Step 2: 测试仓库类**

Run: `python3 -c "from app.repositories.usage_repository import UsageRepository; print('UsageRepository 导入成功')"`
Expected: 输出 "UsageRepository 导入成功"

- [ ] **Step 3: 提交**

```bash
git add app/repositories/usage_repository.py
git commit -m "feat: add UsageRepository for token usage tracking"
```

---

## 总结

此计划完成以下任务：

1. **StockRepository** - `app/repositories/stock_repository.py`
2. **MarketRepository** - `app/repositories/market_repository.py`
3. **UserRepository** - `app/repositories/user_repository.py`
4. **UsageRepository** - `app/repositories/usage_repository.py`

每个仓库类提供：
- 基本 CRUD 操作（继承自 BaseRepository）
- 专用查询方法（如按行业搜索、涨幅榜等）

**Plan complete and saved to `docs/superpowers/plans/2025-05-09-postgresql-repositories-plan.md`. Two execution options:**

1. **Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

2. **Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?