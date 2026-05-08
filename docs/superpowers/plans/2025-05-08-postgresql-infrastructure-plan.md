# PostgreSQL 数据库基础设施实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 创建 PostgreSQL 数据库表结构、连接配置和基础数据访问层，为 MongoDB 到 PostgreSQL 迁移奠定基础设施。

**Architecture:** 使用 SQLAlchemy 2.0 + asyncpg 实现异步数据库操作，创建表结构 SQL 脚本和 Python 数据模型。

**Tech Stack:** PostgreSQL, SQLAlchemy 2.0, asyncpg, psycopg2-binary

---

## 任务 1: 创建 PostgreSQL 表结构 SQL 脚本

**Files:**
- Create: `scripts/migrations/create_postgresql_tables.sql`

- [ ] **Step 1: 创建 SQL 脚本文件**

```sql
-- PostgreSQL 表结构创建脚本
-- 数据库: tradingagents
-- 版本: v1.0

-- 1. 股票基础信息表
CREATE TABLE IF NOT EXISTS stock_basic_info (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    full_symbol VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10),
    area VARCHAR(50),
    industry VARCHAR(100),
    market VARCHAR(100),
    list_date DATE,
    source VARCHAR(20) DEFAULT 'akshare',
    total_mv DECIMAL(18, 4),
    circ_mv DECIMAL(18, 4),
    pe DECIMAL(10, 4),
    pb DECIMAL(10, 4),
    pe_ttm DECIMAL(10, 4),
    pb_mrq DECIMAL(10, 4),
    roe DECIMAL(10, 4),
    turnover_rate DECIMAL(10, 4),
    volume_ratio DECIMAL(10, 4),
    name_en VARCHAR(200),
    board VARCHAR(50),
    industry_code VARCHAR(20),
    sector VARCHAR(100),
    delist_date DATE,
    status VARCHAR(10) DEFAULT 'L',
    is_hs BOOLEAN DEFAULT FALSE,
    total_shares DECIMAL(20, 4),
    float_shares DECIMAL(20, 4),
    lot_size INTEGER,
    currency VARCHAR(10) DEFAULT 'CNY',
    data_version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT uk_stock_basic_info UNIQUE (symbol, source)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_stock_basic_info_symbol ON stock_basic_info(symbol);
CREATE INDEX IF NOT EXISTS idx_stock_basic_info_source ON stock_basic_info(source);
CREATE INDEX IF NOT EXISTS idx_stock_basic_info_industry ON stock_basic_info(industry);
```

- [ ] **Step 2: 添加更多表结构**

在同一个 SQL 文件中添加以下表（简化版，实际生产需要完整字段）：

```sql
-- 2. 历史K线数据表
CREATE TABLE IF NOT EXISTS stock_daily_quotes (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    full_symbol VARCHAR(20),
    market VARCHAR(10),
    trade_date DATE NOT NULL,
    period VARCHAR(20) DEFAULT 'daily',
    data_source VARCHAR(20) DEFAULT 'akshare',
    open DECIMAL(18, 4), high DECIMAL(18, 4), low DECIMAL(18, 4),
    close DECIMAL(18, 4), pre_close DECIMAL(18, 4),
    volume DECIMAL(20, 4), amount DECIMAL(20, 4),
    change DECIMAL(18, 4), pct_chg DECIMAL(10, 4),
    turnover_rate DECIMAL(10, 4), volume_ratio DECIMAL(10, 4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER DEFAULT 1,
    CONSTRAINT uk_stock_daily_quotes UNIQUE (symbol, trade_date, data_source, period)
);

-- 3. 实时行情表
CREATE TABLE IF NOT EXISTS market_quotes (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL UNIQUE,
    full_symbol VARCHAR(20), market VARCHAR(10),
    close DECIMAL(18, 4), open DECIMAL(18, 4), high DECIMAL(18, 4), low DECIMAL(18, 4),
    pre_close DECIMAL(18, 4), pct_chg DECIMAL(10, 4), amount DECIMAL(20, 4),
    volume DECIMAL(20, 4), trade_date DATE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    data_source VARCHAR(20), data_version INTEGER DEFAULT 1
);

-- 4. 财务数据表
CREATE TABLE IF NOT EXISTS stock_financial_data (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL, full_symbol VARCHAR(20), market VARCHAR(10),
    report_period VARCHAR(10) NOT NULL, report_type VARCHAR(20), ann_date DATE,
    revenue DECIMAL(20, 4), net_income DECIMAL(20, 4), total_assets DECIMAL(20, 4),
    total_equity DECIMAL(20, 4), total_liab DECIMAL(20, 4), cash_and_equivalents DECIMAL(20, 4),
    roe DECIMAL(10, 4), roa DECIMAL(10, 4), gross_margin DECIMAL(10, 4),
    net_margin DECIMAL(10, 4), debt_to_assets DECIMAL(10, 4),
    data_source VARCHAR(20) DEFAULT 'akshare',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER DEFAULT 1,
    CONSTRAINT uk_stock_financial_data UNIQUE (symbol, report_period, data_source)
);

-- 5. 用户表
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE, is_verified BOOLEAN DEFAULT FALSE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    daily_quota INTEGER DEFAULT 1000, concurrent_limit INTEGER DEFAULT 3,
    total_analyses INTEGER DEFAULT 0, successful_analyses INTEGER DEFAULT 0,
    failed_analyses INTEGER DEFAULT 0,
    preferences JSONB DEFAULT '{}'
);

-- 6. Token 使用统计表
CREATE TABLE IF NOT EXISTS token_usage (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    provider VARCHAR(50) NOT NULL, model_name VARCHAR(100) NOT NULL,
    input_tokens INTEGER DEFAULT 0, output_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER GENERATED ALWAYS AS (input_tokens + output_tokens) STORED,
    cost DECIMAL(10, 4) DEFAULT 0.0, session_id VARCHAR(100), analysis_type VARCHAR(50),
    _created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 7. 系统配置表
CREATE TABLE IF NOT EXISTS system_config (
    id BIGSERIAL PRIMARY KEY,
    key VARCHAR(100) NOT NULL UNIQUE,
    value JSONB NOT NULL, description TEXT, category VARCHAR(50),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 8. 模型配置表
CREATE TABLE IF NOT EXISTS model_config (
    id BIGSERIAL PRIMARY KEY,
    provider VARCHAR(50) NOT NULL, model_name VARCHAR(100) NOT NULL,
    display_name VARCHAR(200), description TEXT,
    enabled BOOLEAN DEFAULT TRUE, priority INTEGER DEFAULT 0,
    capabilities VARCHAR(500), pricing JSONB, limits JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT uk_model_config UNIQUE (provider, model_name)
);
```

- [ ] **Step 3: 运行 SQL 脚本验证**

Run: `psql -U postgres -d tradingagents -f scripts/migrations/create_postgresql_tables.sql`
Expected: 输出显示所有表和索引创建成功

- [ ] **Step 4: 提交**

```bash
git add scripts/migrations/create_postgresql_tables.sql
git commit -m "feat: add PostgreSQL table structure SQL script"
```

---

## 任务 2: 添加 PostgreSQL 连接配置

**Files:**
- Modify: `.env.example:20-30`
- Modify: `app/core/config.py:50-80`

- [ ] **Step 1: 更新 .env.example 添加 PostgreSQL 配置**

在 MongoDB 配置后面添加：

```bash
# [REQUIRED] PostgreSQL 数据库连接
# 用于替代 MongoDB 存储股票数据、分析结果等
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=tradingagents
POSTGRES_USER=tradinguser
POSTGRES_PASSWORD=your_postgres_password

# PostgreSQL 连接池配置
POSTGRES_MAX_CONNECTIONS=20
POSTGRES_MIN_CONNECTIONS=5
POSTGRES_CONNECT_TIMEOUT_MS=30000
```

- [ ] **Step 2: 更新 app/core/config.py 添加配置类**

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # ... 现有配置 ...

    # PostgreSQL 配置
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "tradingagents"
    POSTGRES_USER: str = "tradinguser"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_MAX_CONNECTIONS: int = 20
    POSTGRES_MIN_CONNECTIONS: int = 5
    POSTGRES_CONNECT_TIMEOUT_MS: int = 30000

    @property
    def POSTGRES_URL(self) -> str:
        """构建 PostgreSQL 连接 URL"""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def POSTGRES_URL_SYNC(self) -> str:
        """构建同步 PostgreSQL 连接 URL"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
```

- [ ] **Step 3: 测试配置加载**

Run: `python -c "from app.core.config import settings; print(settings.POSTGRES_URL)"`
Expected: 输出类似 `postgresql+asyncpg://tradinguser:***@localhost:5432/tradingagents`

- [ ] **Step 4: 提交**

```bash
git add .env.example app/core/config.py
git commit -m "feat: add PostgreSQL configuration"
```

---

## 任务 3: 创建 PostgreSQL 数据库连接模块

**Files:**
- Create: `app/core/postgresql.py`

- [ ] **Step 1: 创建 PostgreSQL 连接管理模块**

```python
"""
PostgreSQL 数据库连接管理模块
使用 SQLAlchemy 2.0 + asyncpg 实现异步数据库操作
"""
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from sqlalchemy import text

from app.core.config import settings

logger = logging.getLogger(__name__)

# 创建异步引擎
_engine: Optional[AsyncEngine] = None
_async_session_factory: Optional[sessionmaker] = None

# SQLAlchemy 声明式基类
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
            logger.info("🔄 正在初始化 PostgreSQL 连接...")

            # 创建异步引擎
            self.engine = create_async_engine(
                settings.POSTGRES_URL,
                max_overflow=settings.POSTGRES_MAX_CONNECTIONS - settings.POSTGRES_MIN_CONNECTIONS,
                pool_size=settings.POSTGRES_MIN_CONNECTIONS,
                pool_pre_ping=True,
                echo=False,  # 生产环境设为 False
            )

            # 测试连接
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))

            # 创建会话工厂
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


# 全局数据库管理器实例
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


# 兼容性别名
get_db = get_session
```

- [ ] **Step 2: 运行模块测试验证语法**

Run: `python -c "import app.core.postgresql; print('模块导入成功')"`
Expected: 输出 "模块导入成功"

- [ ] **Step 3: 提交**

```bash
git add app/core/postgresql.py
git commit -m "feat: add PostgreSQL connection module"
```

---

## 任务 4: 创建基础 SQLAlchemy 模型

**Files:**
- Create: `app/models/postgresql_models.py`

- [ ] **Step 1: 创建基础数据模型**

```python
"""
PostgreSQL 数据模型
使用 SQLAlchemy 2.0 定义数据表结构
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, JSON, ARRAY
from sqlalchemy.sql import func
from app.core.postgresql import Base


class StockBasicInfo(Base):
    """股票基础信息模型"""
    __tablename__ = "stock_basic_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), nullable=False)
    full_symbol = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    code = Column(String(10))
    area = Column(String(50))
    industry = Column(String(100))
    market = Column(String(100))
    list_date = Column(DateTime)
    source = Column(String(20), default="akshare")
    total_mv = Column(Numeric(18, 4))
    circ_mv = Column(Numeric(18, 4))
    pe = Column(Numeric(10, 4))
    pb = Column(Numeric(10, 4))
    pe_ttm = Column(Numeric(10, 4))
    pb_mrq = Column(Numeric(10, 4))
    roe = Column(Numeric(10, 4))
    turnover_rate = Column(Numeric(10, 4))
    volume_ratio = Column(Numeric(10, 4))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        {"schema": "public"},
    )


class MarketQuotes(Base):
    """实时行情模型"""
    __tablename__ = "market_quotes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), nullable=False, unique=True)
    full_symbol = Column(String(20))
    market = Column(String(10))
    close = Column(Numeric(18, 4))
    open = Column(Numeric(18, 4))
    high = Column(Numeric(18, 4))
    low = Column(Numeric(18, 4))
    pre_close = Column(Numeric(18, 4))
    pct_chg = Column(Numeric(10, 4))
    amount = Column(Numeric(20, 4))
    volume = Column(Numeric(20, 4))
    trade_date = Column(DateTime)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    data_source = Column(String(20))
    data_version = Column(Integer, default=1)


class Users(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    daily_quota = Column(Integer, default=1000)
    concurrent_limit = Column(Integer, default=3)
    total_analyses = Column(Integer, default=0)
    successful_analyses = Column(Integer, default=0)
    failed_analyses = Column(Integer, default=0)
    preferences = Column(JSON, default={})


class TokenUsage(Base):
    """Token 使用统计模型"""
    __tablename__ = "token_usage"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    provider = Column(String(50), nullable=False)
    model_name = Column(String(100), nullable=False)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    cost = Column(Numeric(10, 4), default=0.0)
    session_id = Column(String(100))
    analysis_type = Column(String(50))
    _created_at = Column(DateTime(timezone=True), server_default=func.now())
```

- [ ] **Step 2: 验证模型定义**

Run: `python -c "from app.models.postgresql_models import StockBasicInfo, MarketQuotes, Users; print('模型导入成功')"`
Expected: 输出 "模型导入成功"

- [ ] **Step 3: 提交**

```bash
git add app/models/postgresql_models.py
git commit -m "feat: add SQLAlchemy data models for PostgreSQL"
```

---

## 任务 5: 创建数据访问基类

**Files:**
- Create: `app/repositories/base.py`

- [ ] **Step 1: 创建通用数据访问基类**

```python
"""
数据访问基类
提供通用的 CRUD 操作
"""
from typing import TypeVar, Generic, List, Optional, Any, Dict
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.postgresql import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """数据访问基类"""

    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """根据 ID 获取单条记录"""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """获取所有记录"""
        result = await self.session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_field(self, field_name: str, value: Any) -> Optional[ModelType]:
        """根据字段获取单条记录"""
        field = getattr(self.model, field_name)
        result = await self.session.execute(
            select(self.model).where(field == value)
        )
        return result.scalar_one_or_none()

    async def create(self, obj: ModelType) -> ModelType:
        """创建记录"""
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, id: int, data: Dict[str, Any]) -> Optional[ModelType]:
        """更新记录"""
        result = await self.session.execute(
            update(self.model).where(self.model.id == id).values(**data)
        )
        await self.session.flush()
        if result.rowcount > 0:
            return await self.get_by_id(id)
        return None

    async def delete(self, id: int) -> bool:
        """删除记录"""
        result = await self.session.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.session.flush()
        return result.rowcount > 0

    async def count(self) -> int:
        """统计记录数"""
        result = await self.session.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar() or 0
```

- [ ] **Step 2: 验证基类定义**

Run: `python -c "from app.repositories.base import BaseRepository; print('基类导入成功')"`
Expected: 输出 "基类导入成功"

- [ ] **Step 3: 提交**

```bash
git add app/repositories/base.py
git commit -m "feat: add base repository class"
```

---

## 总结

此计划完成以下任务：

1. **创建 SQL 脚本** - `scripts/migrations/create_postgresql_tables.sql`
2. **添加配置** - `.env.example` 和 `app/core/config.py`
3. **创建连接模块** - `app/core/postgresql.py`
4. **创建数据模型** - `app/models/postgresql_models.py`
5. **创建数据访问基类** - `app/repositories/base.py`

**Plan complete and saved to `docs/superpowers/plans/2025-05-08-postgresql-infrastructure-plan.md`. Two execution options:**

1. **Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

2. **Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?