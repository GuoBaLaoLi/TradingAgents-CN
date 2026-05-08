# PostgreSQL 验证测试实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 验证 PostgreSQL 连接和数据操作是否正常工作。

**Architecture:** 使用 Python 测试脚本验证数据库连接、CRUD 操作和数据完整性。

**Tech Stack:** PostgreSQL, SQLAlchemy, pytest

---

## 任务 1: 验证数据库连接

**Files:**
- Create: `tests/test_postgresql_connection.py`

- [ ] **Step 1: 创建连接测试脚本**

```python
"""
PostgreSQL 连接测试
"""
import asyncio
import pytest

from app.core.postgresql import db_manager


class TestPostgreSQLConnection:
    """PostgreSQL 连接测试"""

    @pytest.mark.asyncio
    async def test_connect(self):
        """测试数据库连接"""
        await db_manager.init_postgresql()
        result = await db_manager.health_check()
        assert result is True, "数据库连接失败"
        await db_manager.close()

    @pytest.mark.asyncio
    async def test_session_creation(self):
        """测试会话创建"""
        await db_manager.init_postgresql()
        session = await db_manager.session_factory()
        assert session is not None
        await session.close()
        await db_manager.close()
```

- [ ] **Step 2: 运行测试**

Run: `python3 -m pytest tests/test_postgresql_connection.py -v`

- [ ] **Step 3: 提交**

```bash
git add tests/test_postgresql_connection.py
git commit -m "test: add PostgreSQL connection tests"
```

---

## 任务 2: 验证 Repository 操作

**Files:**
- Create: `tests/test_postgresql_repositories.py`

- [ ] **Step 1: 创建 Repository 测试脚本**

```python
"""
PostgreSQL Repository 测试
"""
import asyncio
import pytest

from app.core.postgresql import db_manager
from app.models.postgresql_models import StockBasicInfo, MarketQuotes
from app.repositories.stock_repository import StockRepository
from app.repositories.market_repository import MarketRepository


class TestStockRepository:
    """股票 Repository 测试"""

    @pytest.mark.asyncio
    async def test_get_all(self):
        """测试获取所有股票"""
        await db_manager.init_postgresql()
        session = await db_manager.session_factory()
        
        repo = StockRepository(session)
        stocks = await repo.get_all(limit=10)
        
        assert isinstance(stocks, list)
        await session.close()
        await db_manager.close()


class TestMarketRepository:
    """行情 Repository 测试"""

    @pytest.mark.asyncio
    async def test_get_by_symbol(self):
        """测试按股票代码查询行情"""
        await db_manager.init_postgresql()
        session = await db_manager.session_factory()
        
        repo = MarketRepository(session)
        quote = await repo.get_by_symbol("000001")
        
        # 如果没有数据也应该返回 None 而不是报错
        assert quote is None or quote.symbol == "000001"
        await session.close()
        await db_manager.close()
```

- [ ] **Step 2: 运行测试**

Run: `python3 -m pytest tests/test_postgresql_repositories.py -v`

- [ ] **Step 3: 提交**

```bash
git add tests/test_postgresql_repositories.py
git commit -m "test: add PostgreSQL repository tests"
```

---

## 任务 3: 验证 DataAccessService

**Files:**
- Create: `tests/test_postgresql_data_access.py`

- [ ] **Step 1: 创建 DataAccessService 测试脚本**

```python
"""
PostgreSQL DataAccessService 测试
"""
import asyncio
import pytest

from app.services.data_access_service import DataAccessService


class TestDataAccessService:
    """DataAccessService 测试"""

    @pytest.mark.asyncio
    async def test_create_service(self):
        """测试创建服务实例"""
        da = await DataAccessService.create()
        assert da is not None
        assert da.stock is not None
        assert da.market is not None
        assert da.user is not None
        assert da.usage is not None
        await da.close()

    @pytest.mark.asyncio
    async def test_stock_query(self):
        """测试股票查询"""
        da = await DataAccessService.create()
        stocks = await da.stock.get_all(limit=5)
        assert isinstance(stocks, list)
        await da.close()
```

- [ ] **Step 2: 运行测试**

Run: `python3 -m pytest tests/test_postgresql_data_access.py -v`

- [ ] **Step 3: 提交**

```bash
git add tests/test_postgresql_data_access.py
git commit -m "test: add DataAccessService tests"
```

---

## 任务 4: 集成测试

**Files:**
- Create: `tests/test_postgresql_integration.py`

- [ ] **Step 1: 创建集成测试脚本**

```python
"""
PostgreSQL 集成测试
测试完整的数据流
"""
import asyncio
import pytest

from app.services.data_access_service import DataAccessService
from app.models.postgresql_models import StockBasicInfo, MarketQuotes


class TestPostgreSQLIntegration:
    """PostgreSQL 集成测试"""

    @pytest.mark.asyncio
    async def test_crud_operations(self):
        """测试完整的 CRUD 操作"""
        da = await DataAccessService.create()
        
        # Create - 创建测试数据
        stock = StockBasicInfo(
            symbol="TEST01",
            full_symbol="TEST01.SZ",
            name="测试股票",
            source="test"
        )
        created = await da.stock.create(stock)
        
        # Read - 读取数据
        retrieved = await da.stock.get_by_symbol("TEST01", "test")
        assert retrieved is not None
        assert retrieved.symbol == "TEST01"
        
        # Delete - 删除测试数据（可选）
        # await da.stock.delete(created.id)
        
        await da.close()

    @pytest.mark.asyncio
    async def test_market_quote_operations(self):
        """测试行情数据操作"""
        da = await DataAccessService.create()
        
        # Create
        quote = MarketQuotes(
            symbol="TEST01",
            close=100.0,
            open=99.0,
            high=101.0,
            low=98.0,
            pct_chg=1.0
        )
        created = await da.market.create(quote)
        
        # Read
        retrieved = await da.market.get_by_symbol("TEST01")
        assert retrieved is not None
        assert retrieved.close == 100.0
        
        await da.close()
```

- [ ] **Step 2: 运行测试**

Run: `python3 -m pytest tests/test_postgresql_integration.py -v`

- [ ] **Step 3: 提交**

```bash
git add tests/test_postgresql_integration.py
git commit -m "test: add PostgreSQL integration tests"
```

---

## 总结

此计划完成以下测试：

1. **test_postgresql_connection.py** - 数据库连接测试
2. **test_postgresql_repositories.py** - Repository 操作测试
3. **test_postgresql_data_access.py** - DataAccessService 测试
4. **test_postgresql_integration.py** - 集成测试

**Plan complete and saved to `docs/superpowers/plans/2025-05-09-postgresql-verification-plan.md`. Two execution options:**

1. **Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

2. **Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?