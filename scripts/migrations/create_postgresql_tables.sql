-- PostgreSQL Table Structure for TradingAgents-CN
-- MongoDB to PostgreSQL Migration Project
-- Target: SQLAlchemy 2.0 + asyncpg

-- Table 1: stock_basic_info (股票基础信息表)
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT uk_stock_basic_info UNIQUE (symbol, source)
);

CREATE INDEX IF NOT EXISTS idx_stock_basic_info_symbol ON stock_basic_info(symbol);
CREATE INDEX IF NOT EXISTS idx_stock_basic_info_source ON stock_basic_info(source);
CREATE INDEX IF NOT EXISTS idx_stock_basic_info_industry ON stock_basic_info(industry);

-- Table 2: stock_daily_quotes (历史K线数据表)
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

CREATE INDEX IF NOT EXISTS idx_stock_daily_quotes_symbol_date ON stock_daily_quotes(symbol, trade_date DESC);
CREATE INDEX IF NOT EXISTS idx_stock_daily_quotes_period ON stock_daily_quotes(period);

-- Table 3: market_quotes (实时行情表)
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

-- Table 4: stock_financial_data (财务数据表)
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

CREATE INDEX IF NOT EXISTS idx_stock_financial_data_symbol ON stock_financial_data(symbol);
CREATE INDEX IF NOT EXISTS idx_stock_financial_data_report_period ON stock_financial_data(report_period);

-- Table 5: users (用户表)
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

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Table 6: token_usage (Token 使用统计表)
CREATE TABLE IF NOT EXISTS token_usage (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    provider VARCHAR(50) NOT NULL, model_name VARCHAR(100) NOT NULL,
    input_tokens INTEGER DEFAULT 0, output_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER GENERATED ALWAYS AS (input_tokens + output_tokens) STORED,
    cost DECIMAL(10, 4) DEFAULT 0.0, session_id VARCHAR(100), analysis_type VARCHAR(50),
    _created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_token_usage_timestamp ON token_usage(timestamp);
CREATE INDEX IF NOT EXISTS idx_token_usage_provider ON token_usage(provider);
CREATE INDEX IF NOT EXISTS idx_token_usage_session_id ON token_usage(session_id);

-- Table 7: system_config (系统配置表)
CREATE TABLE IF NOT EXISTS system_config (
    id BIGSERIAL PRIMARY KEY,
    key VARCHAR(100) NOT NULL UNIQUE,
    value JSONB NOT NULL, description TEXT, category VARCHAR(50),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_system_config_key ON system_config(key);
CREATE INDEX IF NOT EXISTS idx_system_config_category ON system_config(category);

-- Table 8: model_config (模型配置表)
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

CREATE INDEX IF NOT EXISTS idx_model_config_provider ON model_config(provider);
CREATE INDEX IF NOT EXISTS idx_model_config_enabled ON model_config(enabled);