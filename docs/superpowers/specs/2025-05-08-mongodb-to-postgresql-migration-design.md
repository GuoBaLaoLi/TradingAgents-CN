# MongoDB 到 PostgreSQL 迁移设计方案

## 1. 项目概述

### 1.1 背景

TradingAgents-CN 是一个多智能体股票分析平台，当前使用 MongoDB 作为主要数据存储。原项目使用 MongoDB 的原因主要是：

1. 文档型存储灵活性：股票数据、财务数据等结构可能因不同数据源而有所差异
2. 聚合管道：用于复杂查询和数据关联
3. 灵活的查询能力：支持动态字段查询

### 1.2 迁移原因

用户选择迁移的主要原因：

- **Ubuntu 系统兼容性问题**：MongoDB 在 Ubuntu 系统上的支持不够友好，存在安装、配置和资源占用等问题
- **简化运维**：统一技术栈，降低数据库维护复杂度

### 1.3 迁移目标

1. 将 MongoDB 数据完全迁移到 PostgreSQL
2. 保持现有功能和 API 的兼容性
3. 优化数据模型，利用 PostgreSQL 的关系型特性
4. 保留 Redis 作为缓存层

---

## 2. 技术方案

### 2.1 方案选择

**采用方案一：关系型表存储**

将 MongoDB 集合转换为 PostgreSQL 表，使用严格的数据类型定义和关系型设计。

### 2.2 技术选型

| 组件 | 选型 | 说明 |
|------|------|------|
| **ORM 框架** | SQLAlchemy 2.0 | 支持异步操作，类型安全 |
| **异步驱动** | asyncpg | 高性能 PostgreSQL 驱动 |
| **同步驱动** | psycopg2 | 兼容现有同步代码 |
| **迁移工具** | 自定义迁移脚本 | 批量导出导入 |
| **连接池** | SQLAlchemy 内置 | 连接池管理 |

### 2.3 架构变化

```
# 迁移前架构
┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│  FastAPI    │
└─────────────┘     └──────┬──────┘
                          │
         ┌────────────────┼────────────────┐
         │                │                │
         ▼                ▼                ▼
   ┌──────────┐    ┌──────────┐    ┌──────────┐
   │  MongoDB │    │  Redis   │    │   File   │
   └──────────┘    └──────────┘    └──────────┘

# 迁移后架构
┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│  FastAPI    │
└─────────────┘     └──────┬──────┘
                          │
         ┌────────────────┼────────────────┐
         │                │                │
         ▼                ▼                ▼
   ┌──────────┐    ┌──────────┐    ┌──────────┐
   │PostgreSQL│    │  Redis   │    │   File   │
   └──────────┘    └──────────┘    └──────────┘
```

---

## 3. PostgreSQL 表结构设计

### 3.1 数据类型映射

| MongoDB 类型 | PostgreSQL 类型 | 说明 |
|-------------|-----------------|------|
| `string` | `VARCHAR(n)` | 变长字符串 |
| `int` | `INTEGER` | 32位整数 |
| `long` | `BIGINT` | 64位整数 |
| `double` | `DECIMAL(p,s)` | 精确数值 |
| `bool` | `BOOLEAN` | 布尔值 |
| `date` | `TIMESTAMP WITH TIME ZONE` | 带时区时间戳 |
| `array` | `JSONB` 或专用类型 | JSON 数组或 PostgreSQL 数组 |
| `object` | `JSONB` | JSON 对象 |
| `null` | `NULL` | 空值 |

### 3.2 表结构详细设计

#### 3.2.1 股票基础信息表 (stock_basic_info)

```sql
CREATE TABLE stock_basic_info (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    full_symbol VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10),

    -- 基础信息
    area VARCHAR(50),
    industry VARCHAR(100),
    market VARCHAR(100),
    list_date DATE,
    source VARCHAR(20) DEFAULT 'akshare',

    -- 市值数据
    total_mv DECIMAL(18, 4),
    circ_mv DECIMAL(18, 4),

    -- 估值指标
    pe DECIMAL(10, 4),
    pb DECIMAL(10, 4),
    pe_ttm DECIMAL(10, 4),
    pb_mrq DECIMAL(10, 4),
    roe DECIMAL(10, 4),

    -- 交易指标
    turnover_rate DECIMAL(10, 4),
    volume_ratio DECIMAL(10, 4),

    -- 扩展字段
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

    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT uk_stock_basic_info UNIQUE (symbol, source)
);

CREATE INDEX idx_stock_basic_info_symbol ON stock_basic_info(symbol);
CREATE INDEX idx_stock_basic_info_source ON stock_basic_info(source);
CREATE INDEX idx_stock_basic_info_industry ON stock_basic_info(industry);
CREATE INDEX idx_stock_basic_info_total_mv ON stock_basic_info(total_mv DESC);
CREATE INDEX idx_stock_basic_info_pe ON stock_basic_info(pe);
CREATE INDEX idx_stock_basic_info_pb ON stock_basic_info(pb);
CREATE INDEX idx_stock_basic_info_roe ON stock_basic_info(roe DESC);
CREATE INDEX idx_stock_basic_info_updated_at ON stock_basic_info(updated_at DESC);
```

#### 3.2.2 历史K线数据表 (stock_daily_quotes)

```sql
CREATE TABLE stock_daily_quotes (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    full_symbol VARCHAR(20),
    market VARCHAR(10),
    trade_date DATE NOT NULL,
    period VARCHAR(20) DEFAULT 'daily',
    data_source VARCHAR(20) DEFAULT 'akshare',

    open DECIMAL(18, 4),
    high DECIMAL(18, 4),
    low DECIMAL(18, 4),
    close DECIMAL(18, 4),
    pre_close DECIMAL(18, 4),
    volume DECIMAL(20, 4),
    amount DECIMAL(20, 4),
    change DECIMAL(18, 4),
    pct_chg DECIMAL(10, 4),
    turnover_rate DECIMAL(10, 4),
    volume_ratio DECIMAL(10, 4),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER DEFAULT 1,

    CONSTRAINT uk_stock_daily_quotes UNIQUE (symbol, trade_date, data_source, period)
);

CREATE INDEX idx_stock_daily_quotes_symbol_date ON stock_daily_quotes(symbol, trade_date DESC);
CREATE INDEX idx_stock_daily_quotes_symbol_period_date ON stock_daily_quotes(symbol, period, trade_date DESC);
CREATE INDEX idx_stock_daily_quotes_period ON stock_daily_quotes(period);
CREATE INDEX idx_stock_daily_quotes_data_source ON stock_daily_quotes(data_source);
CREATE INDEX idx_stock_daily_quotes_updated_at ON stock_daily_quotes(updated_at DESC);
```

#### 3.2.3 实时行情表 (market_quotes)

```sql
CREATE TABLE market_quotes (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL UNIQUE,
    full_symbol VARCHAR(20),
    market VARCHAR(10),

    close DECIMAL(18, 4),
    open DECIMAL(18, 4),
    high DECIMAL(18, 4),
    low DECIMAL(18, 4),
    pre_close DECIMAL(18, 4),
    pct_chg DECIMAL(10, 4),
    amount DECIMAL(20, 4),
    volume DECIMAL(20, 4),
    trade_date DATE,

    current_price DECIMAL(18, 4),
    change DECIMAL(18, 4),
    turnover_rate DECIMAL(10, 4),
    volume_ratio DECIMAL(10, 4),

    bid_prices DECIMAL(18, 4)[],
    bid_volumes DECIMAL(20, 4)[],
    ask_prices DECIMAL(18, 4)[],
    ask_volumes DECIMAL(20, 4)[],

    timestamp TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    data_source VARCHAR(20),
    data_version INTEGER DEFAULT 1
);

CREATE INDEX idx_market_quotes_pct_chg ON market_quotes(pct_chg DESC);
CREATE INDEX idx_market_quotes_amount ON market_quotes(amount DESC);
CREATE INDEX idx_market_quotes_updated_at ON market_quotes(updated_at DESC);
```

#### 3.2.4 财务数据表 (stock_financial_data)

```sql
CREATE TABLE stock_financial_data (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    full_symbol VARCHAR(20),
    market VARCHAR(10),
    report_period VARCHAR(10) NOT NULL,
    report_type VARCHAR(20),
    ann_date DATE,

    revenue DECIMAL(20, 4),
    net_income DECIMAL(20, 4),
    total_assets DECIMAL(20, 4),
    total_equity DECIMAL(20, 4),
    total_liab DECIMAL(20, 4),
    cash_and_equivalents DECIMAL(20, 4),

    roe DECIMAL(10, 4),
    roa DECIMAL(10, 4),
    gross_margin DECIMAL(10, 4),
    net_margin DECIMAL(10, 4),
    debt_to_assets DECIMAL(10, 4),

    data_source VARCHAR(20) DEFAULT 'akshare',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER DEFAULT 1,

    CONSTRAINT uk_stock_financial_data UNIQUE (symbol, report_period, data_source)
);

CREATE INDEX idx_stock_financial_data_symbol_period ON stock_financial_data(symbol, report_period DESC);
CREATE INDEX idx_stock_financial_data_full_symbol_period ON stock_financial_data(full_symbol, report_period DESC);
CREATE INDEX idx_stock_financial_data_market_period ON stock_financial_data(market, report_period DESC);
CREATE INDEX idx_stock_financial_data_report_period ON stock_financial_data(report_period DESC);
CREATE INDEX idx_stock_financial_data_ann_date ON stock_financial_data(ann_date DESC);
CREATE INDEX idx_stock_financial_data_data_source ON stock_financial_data(data_source);
CREATE INDEX idx_stock_financial_data_report_type ON stock_financial_data(report_type);
CREATE INDEX idx_stock_financial_data_updated_at ON stock_financial_data(updated_at DESC);
```

#### 3.2.5 新闻数据表 (stock_news)

```sql
CREATE TABLE stock_news (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10),
    symbols VARCHAR(500),
    title VARCHAR(500) NOT NULL,
    content TEXT,
    summary TEXT,
    url VARCHAR(1000),
    source VARCHAR(100),
    author VARCHAR(100),
    publish_time TIMESTAMP WITH TIME ZONE NOT NULL,
    category VARCHAR(50),
    sentiment VARCHAR(20),
    sentiment_score DECIMAL(5, 4),
    keywords VARCHAR(1000),
    importance VARCHAR(20),
    language VARCHAR(10) DEFAULT 'zh-CN',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    data_source VARCHAR(20),
    version INTEGER DEFAULT 1,

    CONSTRAINT uk_stock_news UNIQUE (url, title, publish_time)
);

CREATE INDEX idx_stock_news_symbol ON stock_news(symbol);
CREATE INDEX idx_stock_news_publish_time ON stock_news(publish_time DESC);
CREATE INDEX idx_stock_news_symbol_time ON stock_news(symbol, publish_time DESC);
CREATE INDEX idx_stock_news_category ON stock_news(category);
CREATE INDEX idx_stock_news_sentiment ON stock_news(sentiment);
CREATE INDEX idx_stock_news_importance ON stock_news(importance);
CREATE INDEX idx_stock_news_data_source ON stock_news(data_source);
CREATE INDEX idx_stock_news_category_time ON stock_news(symbol, category, publish_time DESC);
CREATE INDEX idx_stock_news_sentiment_importance_time ON stock_news(sentiment, importance, publish_time DESC);
CREATE INDEX idx_stock_news_created_at ON stock_news(created_at DESC);
CREATE INDEX idx_stock_news_text_search ON stock_news USING gin(to_tsvector('chinese', title || ' ' || COALESCE(content, '') || ' ' || COALESCE(summary, '')));
```

#### 3.2.6 社交媒体消息表 (social_media_messages)

```sql
CREATE TABLE social_media_messages (
    id BIGSERIAL PRIMARY KEY,
    message_id VARCHAR(100) NOT NULL UNIQUE,
    platform VARCHAR(50) NOT NULL,
    symbol VARCHAR(10),
    symbols VARCHAR(500),
    author JSONB,
    content TEXT,
    created_time TIMESTAMP WITH TIME ZONE NOT NULL,
    effective_time TIMESTAMP WITH TIME ZONE,
    expiry_time TIMESTAMP WITH TIME ZONE,
    message_type VARCHAR(50),
    category VARCHAR(50),
    subcategory VARCHAR(50),
    source JSONB,
    sentiment VARCHAR(20),
    importance VARCHAR(20),
    impact_scope VARCHAR(50),
    engagement JSONB,
    hashtags VARCHAR(1000),
    keywords VARCHAR(1000),
    topics VARCHAR(1000),
    location JSONB,
    data_source VARCHAR(50),
    crawler_version VARCHAR(50),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_social_media_messages_message_id ON social_media_messages(message_id);
CREATE INDEX idx_social_media_messages_symbol ON social_media_messages(symbol);
CREATE INDEX idx_social_media_messages_created_time ON social_media_messages(created_time DESC);
CREATE INDEX idx_social_media_messages_effective_time ON social_media_messages(effective_time);
CREATE INDEX idx_social_media_messages_expiry_time ON social_media_messages(expiry_time);
CREATE INDEX idx_social_media_messages_message_type ON social_media_messages(message_type);
CREATE INDEX idx_social_media_messages_category ON social_media_messages(category);
CREATE INDEX idx_social_media_messages_sentiment ON social_media_messages(sentiment);
CREATE INDEX idx_social_media_messages_importance ON social_media_messages(importance);
CREATE INDEX idx_social_media_messages_platform ON social_media_messages(platform);
CREATE INDEX idx_social_media_messages_sentiment_importance ON social_media_messages(sentiment, importance);
```

#### 3.2.7 分析任务表 (analysis_tasks)

```sql
CREATE TABLE analysis_tasks (
    id BIGSERIAL PRIMARY KEY,
    task_id VARCHAR(50) NOT NULL UNIQUE,
    batch_id VARCHAR(50),
    user_id BIGINT NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    stock_name VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending',
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,

    worker_id VARCHAR(100),
    parameters JSONB,
    result JSONB,

    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    last_error TEXT
);

CREATE INDEX idx_analysis_tasks_task_id ON analysis_tasks(task_id);
CREATE INDEX idx_analysis_tasks_user_id ON analysis_tasks(user_id);
CREATE INDEX idx_analysis_tasks_symbol ON analysis_tasks(symbol);
CREATE INDEX idx_analysis_tasks_status ON analysis_tasks(status);
CREATE INDEX idx_analysis_tasks_batch_id ON analysis_tasks(batch_id);
CREATE INDEX idx_analysis_tasks_created_at ON analysis_tasks(created_at DESC);
```

#### 3.2.8 分析报告表 (analysis_reports)

```sql
CREATE TABLE analysis_reports (
    id BIGSERIAL PRIMARY KEY,
    analysis_id VARCHAR(50) NOT NULL UNIQUE,
    user_id BIGINT NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    stock_name VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending',

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    parameters JSONB,
    result JSONB,

    tokens_used INTEGER DEFAULT 0,
    execution_time DECIMAL(10, 4) DEFAULT 0.0,
    model_info VARCHAR(200)
);

CREATE INDEX idx_analysis_reports_analysis_id ON analysis_reports(analysis_id);
CREATE INDEX idx_analysis_reports_user_id ON analysis_reports(user_id);
CREATE INDEX idx_analysis_reports_symbol ON analysis_reports(symbol);
CREATE INDEX idx_analysis_reports_status ON analysis_reports(status);
CREATE INDEX idx_analysis_reports_created_at ON analysis_reports(created_at DESC);
```

#### 3.2.9 用户表 (users)

```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,

    daily_quota INTEGER DEFAULT 1000,
    concurrent_limit INTEGER DEFAULT 3,

    total_analyses INTEGER DEFAULT 0,
    successful_analyses INTEGER DEFAULT 0,
    failed_analyses INTEGER DEFAULT 0,

    preferences JSONB DEFAULT '{}'
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_is_active ON users(is_active);
CREATE INDEX idx_users_created_at ON users(created_at DESC);
```

#### 3.2.10 Token 使用统计表 (token_usage)

```sql
CREATE TABLE token_usage (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    provider VARCHAR(50) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER GENERATED ALWAYS AS (input_tokens + output_tokens) STORED,
    cost DECIMAL(10, 4) DEFAULT 0.0,
    session_id VARCHAR(100),
    analysis_type VARCHAR(50),

    _created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_token_usage_timestamp ON token_usage(timestamp DESC);
CREATE INDEX idx_token_usage_provider ON token_usage(provider);
CREATE INDEX idx_token_usage_model_name ON token_usage(model_name);
CREATE INDEX idx_token_usage_session_id ON token_usage(session_id);
CREATE INDEX idx_token_usage_analysis_type ON token_usage(analysis_type);
CREATE INDEX idx_token_usage_provider_model ON token_usage(provider, model_name);
CREATE INDEX idx_token_usage_timestamp_provider_model ON token_usage(timestamp DESC, provider, model_name);
```

#### 3.2.11 系统配置表 (system_config)

```sql
CREATE TABLE system_config (
    id BIGSERIAL PRIMARY KEY,
    key VARCHAR(100) NOT NULL UNIQUE,
    value JSONB NOT NULL,
    description TEXT,
    category VARCHAR(50),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_system_config_key ON system_config(key);
CREATE INDEX idx_system_config_category ON system_config(category);
CREATE INDEX idx_system_config_updated_at ON system_config(updated_at DESC);
```

#### 3.2.12 模型配置表 (model_config)

```sql
CREATE TABLE model_config (
    id BIGSERIAL PRIMARY KEY,
    provider VARCHAR(50) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    display_name VARCHAR(200),
    description TEXT,
    enabled BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 0,
    capabilities VARCHAR(500),
    pricing JSONB,
    limits JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT uk_model_config UNIQUE (provider, model_name)
);

CREATE INDEX idx_model_config_provider ON model_config(provider);
CREATE INDEX idx_model_config_model_name ON model_config(model_name);
CREATE INDEX idx_model_config_enabled ON model_config(enabled);
CREATE INDEX idx_model_config_priority ON model_config(priority DESC);
CREATE INDEX idx_model_config_provider_name ON model_config(provider, model_name);
```

---

## 4. 数据迁移策略

### 4.1 迁移流程

```
┌─────────────────────────────────────────────────────────────────┐
│                         迁移流程                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐     │
│  │  准备   │───▶│  停止   │───▶│  迁移   │───▶│  切换   │     │
│  │  阶段   │    │  服务   │    │  数据   │    │  代码   │     │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘     │
│       │              │              │              │           │
│       ▼              ▼              ▼              ▼           │
│  - 备份数据     - 停止 FastAPI   - 导出 MongoDB  - 更新配置  │
│  - 创建表结构   - 停止后台任务    - 转换格式       - 测试功能  │
│  - 安装依赖     - 通知用户       - 导入 PostgreSQL - 启动服务  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 详细步骤

#### 阶段 0：环境检查（先执行）

**1. 检查 PostgreSQL 是否已安装**

```bash
# 检查 PostgreSQL 是否已安装
which psql

# 如果已安装，检查版本
psql --version

# 检查 PostgreSQL 服务状态
sudo systemctl status postgresql
```

如果已安装：
- 记录版本号（建议 PostgreSQL 14+）
- 确保服务正在运行：`sudo systemctl start postgresql`

如果未安装：
```bash
# 安装 PostgreSQL（Ubuntu）
sudo apt update
sudo apt install postgresql postgresql-contrib

# 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql  # 设置开机自启
```

**2. 检查 Python 虚拟环境**

```bash
# 检查是否在虚拟环境中
python -c "import sys; print(sys.prefix)" | grep -q "venv" && echo "在虚拟环境中" || echo "不在虚拟环境中"

# 如果项目有虚拟环境，激活它
source venv/bin/activate  # 假设虚拟环境名为 venv

# 或者创建新的虚拟环境（如果不存在）
python -m venv venv
source venv/bin/activate
```

**3. 确认项目依赖管理方式**

```bash
# 检查是否有 requirements.txt 或 pyproject.toml
ls -la requirements.txt pyproject.toml 2>/dev/null
```

#### 阶段 1：准备阶段

1. **创建数据库和用户**
   ```sql
   -- 以 postgres 用户登录
   sudo -u postgres psql

   -- 在 PostgreSQL 命令行中执行
   CREATE DATABASE tradingagents;
   CREATE USER tradinguser WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE tradingagents TO tradinguser;
   GRANT ALL ON SCHEMA public TO tradinguser;
   \q
   ```

2. **运行表结构创建脚本**
   ```bash
   psql -U tradinguser -d tradingagents -f create_tables.sql
   ```

3. **安装 Python 依赖（在虚拟环境中）**
   ```bash
   # 确保在虚拟环境中
   source venv/bin/activate

   # 安装 PostgreSQL 相关依赖
   pip install sqlalchemy asyncpg psycopg2-binary

   # 如果项目使用 requirements.txt
   pip install -r requirements.txt
   ```

#### 阶段 2：数据迁移

1. **导出 MongoDB 数据**
   - 使用 mongoexport 或自定义脚本导出 JSON
   - 导出格式：每个集合一个 JSON 文件

2. **转换数据格式**
   - 转换 MongoDB ObjectId 为字符串
   - 转换日期格式为 PostgreSQL 兼容格式
   - 转换数组为 JSONB

3. **导入 PostgreSQL**
   - 使用 psql 导入或自定义脚本
   - 批量导入，每批 1000 条
   - 记录迁移日志

4. **验证数据完整性**
   - 记录数对比
   - 关键字段抽样检查

#### 阶段 3：代码切换

1. **修改环境变量**
   ```bash
   # 添加 PostgreSQL 配置
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_DB=tradingagents
   POSTGRES_USER=tradinguser
   POSTGRES_PASSWORD=your_password
   ```

2. **修改数据库配置**
   - 更新 `app/core/database.py`
   - 添加 PostgreSQL 连接

3. **修改数据访问层**
   - 替换 PyMongo 为 SQLAlchemy
   - 修改查询逻辑

#### 阶段 4：验证

1. **功能测试**
   - 登录功能
   - 股票查询
   - 分析任务
   - 数据同步

2. **性能测试**
   - 响应时间
   - 并发能力

---

## 5. 代码修改计划

### 5.1 文件修改清单

#### 5.1.1 配置文件

| 文件 | 修改内容 |
|------|---------|
| `.env.example` | 添加 PostgreSQL 配置 |
| `app/core/config.py` | 添加 PostgreSQL 连接配置 |

#### 5.1.2 数据库层

| 文件 | 修改内容 |
|------|---------|
| `app/core/database.py` | 替换为 SQLAlchemy + asyncpg |
| `tradingagents/config/database_manager.py` | 添加 PostgreSQL 管理 |
| `tradingagents/config/mongodb_storage.py` | 创建 PostgreSQL 存储适配器 |

#### 5.1.3 数据模型

| 文件 | 修改内容 |
|------|---------|
| `app/models/user.py` | 调整字段类型 |
| `app/models/analysis.py` | 调整字段类型 |
| `app/models/stock_models.py` | 调整字段类型 |

#### 5.1.4 数据访问层（核心）

| 文件 | 修改内容 |
|------|---------|
| `app/services/unified_stock_service.py` | 替换为 SQL 查询 |
| `app/services/quotes_ingestion_service.py` | 替换为 SQL 写入 |
| `app/services/financial_data_service.py` | 替换为 SQL 写入 |
| `app/services/user_service.py` | 替换为 SQL 操作 |
| `tradingagents/dataflows/cache/mongodb_cache_adapter.py` | 创建 PostgreSQL 缓存适配器 |
| `tradingagents/dataflows/cache/adaptive.py` | 添加 PostgreSQL 支持 |
| `tradingagents/dataflows/cache/db_cache.py` | 添加 PostgreSQL 缓存 |

#### 5.1.5 其他服务

| 文件 | 修改内容 |
|------|---------|
| `app/services/usage_statistics_service.py` | 替换为 SQL 查询 |
| `app/services/simple_analysis_service.py` | 替换为 SQL 操作 |
| `web/utils/mongodb_report_manager.py` | 创建 PostgreSQL 报告管理器 |

### 5.2 技术债务

迁移过程中需要处理的技术债务：

1. **字段命名不一致**：如 `code` vs `symbol`
2. **日期格式**：MongoDB 使用 ISODate，PostgreSQL 使用 TIMESTAMP
3. **JSON 字段**：MongoDB 文档型字段转为 PostgreSQL JSONB
4. **索引迁移**：验证所有索引正确创建

---

## 6. 实施时间表

### 6.1 预估时间

| 阶段 | 任务 | 预估时间 |
|------|------|---------|
| 准备 | 环境搭建、依赖安装 | 1-2 小时 |
| 准备 | 创建表结构 | 1 小时 |
| 迁移 | 数据导出、转换、导入 | 2-4 小时 |
| 切换 | 代码修改 | 8-16 小时 |
| 验证 | 功能测试 | 2-4 小时 |

**总预估时间**：14-27 小时（约 2-4 天）

### 6.2 实施建议

1. **选择低峰期进行**：建议在夜间或周末进行
2. **分批迁移**：先迁移核心数据，再迁移历史数据
3. **保留回滚方案**：保留 MongoDB 备份，随时可回滚

---

## 7. 风险和注意事项

### 7.1 风险

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 数据丢失 | 高 | 完整备份 MongoDB |
| 性能下降 | 中 | 创建适当索引，优化查询 |
| 代码兼容 | 高 | 逐步切换，充分测试 |
| 时间超期 | 中 | 预留缓冲时间 |

### 7.2 注意事项

1. **数据备份**：迁移前必须完整备份 MongoDB 数据
2. **增量迁移**：建议先迁移增量数据，再迁移历史数据
3. **测试环境**：建议先在测试环境验证，再在生产环境执行
4. **回滚方案**：准备 MongoDB 回滚方案
5. **用户通知**：提前通知用户可能的停机时间

---

## 8. 后续优化

迁移完成后，可以考虑以下优化：

1. **PostgreSQL 特性利用**：利用物化视图、CTE 等高级特性
2. **查询优化**：分析慢查询，创建适当索引
3. **连接池优化**：调整连接池参数
4. **监控告警**：设置数据库监控和性能告警

---

## 9. 附录

### 9.1 相关文档

- [数据库管理实现文档](../database/DATABASE_MANAGEMENT_IMPLEMENTATION.md)
- [MongoDB 集合对比文档](../database/MONGODB_COLLECTIONS_COMPARISON.md)

### 9.2 参考资源

- PostgreSQL 官方文档：https://www.postgresql.org/docs/
- SQLAlchemy 文档：https://docs.sqlalchemy.org/
- asyncpg 文档：https://magicstack.github.io/asyncpg/

---

**文档版本**：v1.0  
**创建日期**：2025-05-08  
**作者**：TradingAgents-CN Team  
**状态**：待用户审批