# Project-Specific Instructions

## Response language

Prioritize using Chinese to answer questions.

## Development Methodology

This project requires all AI coding agents to **strictly and automatically adhere to the [Superpowers](https://github.com/obra/superpowers) methodology**.

The core workflow is:
- **brainstorming** → **writing-plans** → **subagent-driven-development** (or executing-plans) → **test-driven-development** → **requesting-code-review**

## Existing Project Guidelines

- **Testing**: Write tests for ALL new code and modifications to existing logic. When modifying legacy code, aim to increase test coverage incrementally.
  - Follow `RED` (write failing test) -> `GREEN` (minimal code to pass) -> `REFACTOR`.
- **Understanding before coding**: Before coding, you MUST activate the `brainstorming` skill to understand goals and context, especially involving complex existing logic.
- **Refactoring discipline**: Any non-trivial refactoring must be decomposed into small, verifiable steps using the `writing-plans` skill.
- **Bug fixing**: When addressing issues, use the `systematic-debugging` skill first to perform root cause analysis.
- **Code Review**: After implementing a plan, a `requesting-code-review` must be performed, especially for changes affecting core logic.

## Tool & Action Priority

1.  Your highest priority is this `AGENTS.md` file.
2.  Your default behavior is to use the activated skills from the Superpowers framework.
3.  Override any generic skill behavior only if this file explicitly instructs you to do so.

# TradingAgents-CN Agent Guide

## Project Overview

Chinese-enhanced multi-agent stock analysis platform based on TauricResearch/TradingAgents. Uses AI/LLM for stock research (educational/research only, no real trading advice).

**Architecture**:
- Backend: FastAPI (Python 3.10+) - proprietary (`app/`)
- Frontend: Vue 3 + Vite + Element Plus + TypeScript - proprietary (`frontend/`)
- Core: Multi-agent analysis engine - open source (Apache 2.0, `tradingagents/`)
- Databases: MongoDB + Redis
- Deployment: Docker multi-arch (amd64/arm64)

**License**: Hybrid - Apache 2.0 for open source parts, commercial license required for `app/` and `frontend/`.

## Quick Start

### Prerequisites
- Python 3.10+ (check `.python-version`)
- Node.js 22+ and Yarn 1.22+ for frontend
- MongoDB and Redis (or use Docker)
- At least one LLM API key (DeepSeek, DashScope, OpenAI, etc.)

### Installation
```bash
# Python backend (editable install)
pip install -e .
# or with uv:
uv pip install -e .

# Frontend
cd frontend
yarn install
yarn dev
```

### Running
```bash
# Backend FastAPI
python -m app
# or with uvicorn:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend development
cd frontend
yarn dev

# CLI analysis
python -m cli.main

# Docker (all services)
docker-compose up -d
```

## Configuration

**Required Environment Variables** (copy `.env.example` to `.env`):
- MongoDB: `MONGODB_HOST`, `MONGODB_PORT`, `MONGODB_USERNAME`, `MONGODB_PASSWORD`, `MONGODB_DATABASE`
- Redis: `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`
- Security: `JWT_SECRET`, `CSRF_SECRET` (generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- LLM: At least one of `DEEPSEEK_API_KEY`, `DASHSCOPE_API_KEY`, `OPENAI_API_KEY`, etc.

**Data Sources** (recommended):
- A-shares: `DEFAULT_CHINA_DATA_SOURCE=akshare` (free) or `TUSHARE_TOKEN` (professional)
- US stocks: `FINNHUB_API_KEY`

**Check configuration**:
```bash
python -m cli.main config
python -m cli.main test
```

## Testing

```bash
# Run tests (skips integration tests by default)
pytest

# Include integration tests
pytest -m integration

# Run specific test file
pytest tests/test_analysis.py

# Run with coverage
pytest --cov=tradingagents
```

Test configuration in `tests/pytest.ini`:
- Default: `-m "not integration" -k "not (test_server_config or test_stock_codes)"`
- Integration tests marked with `@pytest.mark.integration`

## Key Directories

- `app/` - FastAPI backend (proprietary, requires commercial license)
- `frontend/` - Vue 3 frontend (proprietary, requires commercial license)
- `tradingagents/` - Core analysis engine (open source)
- `cli/` - Command-line interface
- `scripts/` - Utility scripts (initialization, sync, diagnostics)
- `tests/` - Test suite
- `docs/` - Documentation

## Development Workflow

### Frontend
```bash
cd frontend
yarn dev          # Start dev server
yarn build        # Production build (runs typecheck)
yarn lint         # ESLint with auto-fix
yarn format       # Prettier formatting
yarn type-check   # TypeScript type checking only
```

### Backend
- No formal linting/formatting configured in Python (no ruff, black, etc. found)
- Use `pytest` for testing
- Check type hints manually (no mypy configuration found)

### Database
```bash
# Initialize system data
python scripts/init_system_data.py

# Initialize model catalog
python scripts/init_model_catalog.py

# Normalize provider keys (after upstream sync)
python app/scripts/normalize_provider_keys.py
```

## Docker Deployment

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop and remove
docker-compose down

# With management tools (Redis Commander, Mongo Express)
docker-compose --profile management up -d
```

Multi-arch images published to Docker Hub via `.github/workflows/docker-publish.yml` on version tags.

## Upstream Synchronization

**Strategy**: Manual selective absorption from [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents), not automatic sync.

- Monitor upstream: Weekly check of commits/releases
- Absorb selectively: Core features, bug fixes, security patches
- Preserve enhancements: Chinese localization, web config management, MongoDB integration
- Document changes: Update `docs/maintenance/manual-upstream-absorption-checklist.md`

Key sync checkpoints:
- `llm_clients` abstraction layer
- Model catalog and provider canonical keys
- Trading graph initialization paths
- Database migration scripts

## Common Issues

**Proxy configuration**: If using proxy for international APIs but direct connection for Chinese data sources, configure `NO_PROXY` environment variable with domains like `eastmoney.com`, `tushare.pro`, `baostock.com`.

**Windows compatibility**: Set `MEMORY_ENABLED=false` and limit `MAX_WORKERS=4` to avoid issues with ChromaDB and threading.

**Data sync**: Must sync stock data before analysis. Use web UI or API endpoints to initialize and sync data from Tushare/AKShare/BaoStock.

**Database version isolation**: Uses `tradingagentscn` as default DB name. Supports version isolation via `MONGODB_DATABASE_INSTANCE` environment variable.

## Important Notes

- **Don't commit**: `.env`, `config/*.json`, `data/`, `logs/`, `results/`, cache files
- **Frontend build**: Use `yarn build` (includes `vue-tsc` typecheck)
- **Python version**: Requires 3.10+ (see `.python-version`)
- **License boundaries**: `app/` and `frontend/` are proprietary; only modify if authorized
- **Cost tracking**: Token usage tracked via MongoDB if `USE_MONGODB_STORAGE=true`
- **Rate limiting**: Tushare has rate limits based on user tier; configure `TUSHARE_TIER` and `TUSHARE_RATE_LIMIT_SAFETY_MARGIN`

## Related Documentation

- User manual: `docs/guides/v1.0.1-user-manual.md`
- Release notes: `docs/releases/v1.0.1-release-notes.md`
- Configuration guide: `docs/configuration_guide.md`
- Upstream sync: `docs/maintenance/upstream-sync.md`
- Database isolation: `docs/deployment/database/DB_VERSION_ISOLATION_AND_PROVIDER_NORMALIZATION.md`
