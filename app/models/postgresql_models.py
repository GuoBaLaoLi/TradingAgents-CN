"""
PostgreSQL 数据模型
使用 SQLAlchemy 2.0 定义数据表结构
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, JSON
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