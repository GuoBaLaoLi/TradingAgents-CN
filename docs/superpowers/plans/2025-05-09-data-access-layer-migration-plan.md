# PostgreSQL 数据访问层迁移实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修改现有服务的数据访问层，从 MongoDB 切换到 PostgreSQL。

**Architecture:** 在现有服务中注入 Repository 依赖，替换 MongoDB 查询为 PostgreSQL 查询。

**Tech Stack:** SQLAlchemy 2.0, Repository 模式, 依赖注入

---

## 任务 1: 创建统一的数据访问服务

**Files:**
- Create: `app/services/data_access_service.py`

- [ ] **Step 1: 创建数据访问服务**

```python
"""
统一数据访问服务
提供所有数据仓库的集中访问
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.postgresql import get_session
from app.repositories.stock_repository import StockRepository
from app.repositories.market_repository import MarketRepository
from app.repositories.user_repository import UserRepository
from app.repositories.usage_repository import UsageRepository


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
```

- [ ] **Step 2: 验证导入**

Run: `python3 -c "from app.services.data_access_service import DataAccessService; print('DataAccessService 导入成功')"`

- [ ] **Step 3: 提交**

```bash
git add app/services/data_access_service.py
git commit -m "feat: add DataAccessService for unified data access"
```

---

## 任务 2: 创建股票数据查询服务

**Files:**
- Modify: `app/services/unified_stock_service.py`

- [ ] **Step 1: 添加 PostgreSQL 数据源支持**

在 `UnifiedStockService` 类中添加 PostgreSQL 数据源查询方法：

```python
async def get_stock_from_postgres(self, symbol: str) -> Optional[dict]:
    """从 PostgreSQL 获取股票数据"""
    from app.services.data_access_service import get_data_access
    
    try:
        da = await get_data_access()
        stock = await da.stock.get_by_symbol(symbol)
        if stock:
            return {
                "symbol": stock.symbol,
                "name": stock.name,
                "industry": stock.industry,
                "market": stock.market,
                "source": stock.source
            }
        await da.close()
    except Exception as e:
        logger.warning(f"PostgreSQL 查询失败: {e}")
    return None
```

- [ ] **Step 2: 验证语法**

Run: `python3 -c "from app.services.unified_stock_service import UnifiedStockService; print('UnifiedStockService 导入成功')"`

- [ ] **Step 3: 提交**

```bash
git add app/services/unified_stock_service.py
git commit -m "feat: add PostgreSQL query support to UnifiedStockService"
```

---

## 任务 3: 修改行情数据服务

**Files:**
- Modify: `app/services/quotes_ingestion_service.py`

- [ ] **Step 1: 添加 PostgreSQL 写入方法**

在 `QuotesIngestionService` 类中添加 PostgreSQL 数据保存方法：

```python
async def save_to_postgres(self, quote_data: dict) -> bool:
    """保存行情数据到 PostgreSQL"""
    from app.services.data_access_service import get_data_access
    
    try:
        da = await get_data_access()
        
        # 创建 MarketQuotes 对象
        from app.models.postgresql_models import MarketQuotes
        quote = MarketQuotes(
            symbol=quote_data.get("code"),
            full_symbol=quote_data.get("full_symbol"),
            close=quote_data.get("close"),
            open=quote_data.get("open"),
            high=quote_data.get("high"),
            low=quote_data.get("low"),
            pct_chg=quote_data.get("pct_chg"),
            amount=quote_data.get("amount"),
            volume=quote_data.get("volume"),
            data_source=quote_data.get("source", "akshare")
        )
        
        await da.market.session.merge(quote)
        await da.session.commit()
        await da.close()
        return True
    except Exception as e:
        logger.error(f"保存到 PostgreSQL 失败: {e}")
        return False
```

- [ ] **Step 2: 验证语法**

Run: `python3 -c "from app.services.quotes_ingestion_service import QuotesIngestionService; print('QuotesIngestionService 导入成功')"`

- [ ] **Step 3: 提交**

```bash
git add app/services/quotes_ingestion_service.py
git commit -m "feat: add PostgreSQL write support to QuotesIngestionService"
```

---

## 任务 4: 修改用户服务

**Files:**
- Modify: `app/services/user_service.py`

- [ ] **Step 1: 添加 PostgreSQL 用户查询**

在 `UserService` 类中添加 PostgreSQL 用户查询方法：

```python
async def get_user_from_postgres(self, username: str) -> Optional[dict]:
    """从 PostgreSQL 获取用户"""
    from app.services.data_access_service import get_data_access
    
    try:
        da = await get_data_access()
        user = await da.user.get_by_username(username)
        if user:
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
                "is_admin": user.is_admin
            }
        await da.close()
    except Exception as e:
        logger.warning(f"PostgreSQL 用户查询失败: {e}")
    return None
```

- [ ] **Step 2: 验证语法**

Run: `python3 -c "from app.services.user_service import UserService; print('UserService 导入成功')"`

- [ ] **Step 3: 提交**

```bash
git add app/services/user_service.py
git commit -m "feat: add PostgreSQL query support to UserService"
```

---

## 总结

此计划完成以下任务：

1. **DataAccessService** - 统一数据访问服务
2. **UnifiedStockService** - 添加 PostgreSQL 股票查询
3. **QuotesIngestionService** - 添加 PostgreSQL 行情写入
4. **UserService** - 添加 PostgreSQL 用户查询

每个任务都是增量修改，保持与现有 MongoDB 代码的兼容性。

**Plan complete and saved to `docs/superpowers/plans/2025-05-09-data-access-layer-migration-plan.md`. Two execution options:**

1. **Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

2. **Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?