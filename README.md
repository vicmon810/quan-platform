# Quant Platform

[![CI](https://github.com/vicmon810/quan-platform/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/vicmon810/quan-platform/actions/workflows/ci.yml)

An asynchronous algorithmic-trading backtest platform with a React dashboard, Spring Boot API, Python/Backtrader worker, and PostgreSQL persistence.

一个异步量化回测平台，由 React 控制台、Spring Boot API、Python/Backtrader Worker 和 PostgreSQL 持久化层组成。

## Architecture / 架构

```mermaid
flowchart LR
    UI["React + Vite"] -->|HTTP /api/backtests| API["Spring Boot API"]
    API -->|create and query runs| DB[(PostgreSQL)]
    DB -->|claim PENDING job| Worker["Python Worker"]
    Worker -->|execute| Engine["Backtrader Engine"]
    Strategies["Strategy Modules"] --> Engine
    Data["OHLCV CSV Data"] --> Engine
    Worker -->|metrics and portfolio values| DB
```

The API accepts a backtest and returns immediately. PostgreSQL acts as both the job handoff and durable result store; the worker claims pending jobs and runs them outside the HTTP request lifecycle.

API 接收回测请求后立即返回。PostgreSQL 同时承担任务交接和结果存储；Worker 在 HTTP 请求生命周期之外领取并执行任务。

## Features / 功能

- **React dashboard / React 控制台** — submit backtests, track status, and inspect metrics and equity curves.
- **Asynchronous execution / 异步执行** — API requests and backtest execution are decoupled through PostgreSQL.
- **Walk-forward optimisation / 滚动前向优化** — train on historical windows and evaluate unseen periods.
- **Strategy analytics / 策略分析** — return, CAGR, drawdown, Sharpe, Calmar, exposure, and duration metrics.
- **Durable results / 持久化结果** — run state, summary metrics, and daily portfolio values are stored transactionally.
- **Multi-layer tests / 多层测试** — Python, Java integration, and React component/API tests.

## Technology / 技术栈

| Layer / 层 | Technology / 技术 |
|---|---|
| Web UI / 前端 | React 19, TypeScript, Vite 8, Recharts |
| HTTP API | Java 21, Spring Boot 4, Spring JDBC |
| Worker and engine / Worker 与引擎 | Python 3.12, Backtrader, pandas |
| Database / 数据库 | PostgreSQL 17, Flyway 13 |
| CI | GitHub Actions |

## Quick Start / 快速开始

### 1. Database / 数据库

```bash
export POSTGRES_DB=quant_platform
export POSTGRES_USER=quant_app
export POSTGRES_PASSWORD=change-me
export POSTGRES_PORT=5432

docker compose up -d --wait postgres
docker compose --profile tools run --rm flyway migrate
```

### 2. API

```bash
cd api
SPRING_DATASOURCE_URL="jdbc:postgresql://localhost:5432/quant_platform" \
SPRING_DATASOURCE_USERNAME="quant_app" \
SPRING_DATASOURCE_PASSWORD="change-me" \
./mvnw spring-boot:run
```

The API runs on `http://localhost:8080` by default.

API 默认运行在 `http://localhost:8080`。

### 3. Frontend / 前端

```bash
cd frontend
npm ci
npm run dev
```

Vite proxies `/api` requests to the Spring Boot API on port `8080`.

Vite 会把 `/api` 请求代理到 `8080` 端口的 Spring Boot API。

### 4. Worker

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt

DATABASE_URL="postgresql://quant_app:change-me@localhost:5432/quant_platform" \
PYTHONPATH=. \
python -m src.worker
```

The worker loads matching files from `data/raw/`, such as `data/raw/AAPL.csv`.

Worker 从 `data/raw/` 读取对应的行情文件，例如 `data/raw/AAPL.csv`。

## API

| Method | Endpoint | Description / 说明 |
|---|---|---|
| `POST` | `/api/backtests` | Create a pending run / 创建待执行任务 |
| `GET` | `/api/backtests/{publicId}` | Read status and summary metrics / 查询状态和汇总指标 |
| `GET` | `/api/backtests/{publicId}/portfolio-values` | Read the equity series / 查询组合净值序列 |

## Tests / 测试

```bash
# Python
PYTHONPATH=. python -m pytest

# Java
cd api && ./mvnw test

# React
cd frontend
npm run lint
npm run test:run
npm run build
```

Database-backed Python and Java tests require PostgreSQL and Flyway migrations.

依赖数据库的 Python 和 Java 测试需要先启动 PostgreSQL 并执行 Flyway migrations。

## Project Structure / 项目结构

```text
quant-platform/
├── frontend/            # React dashboard / React 控制台
├── api/                 # Spring Boot API
├── src/
│   ├── domain/          # Backtest job model / 回测任务模型
│   ├── engine/          # Backtrader engine / 回测引擎
│   ├── helper/          # Metrics and reporting / 指标与报告
│   ├── persistence/     # PostgreSQL transactions / 数据库事务
│   └── worker/          # Async worker / 异步 Worker
├── strategies/          # Trading strategies / 交易策略
├── backtests/           # Standalone research scripts / 研究脚本
├── database/migrations/ # Flyway migrations / 数据库迁移
├── data/raw/            # Local OHLCV files / 本地行情文件
├── tests/               # Python tests
└── docs/                # Design documentation / 设计文档
```

## Documentation / 文档

- [Strategy evaluation and walk-forward design / 策略评估与滚动前向设计](docs/design.md)
- [Backtest lifecycle / 回测生命周期](docs/backtest_lifecycle.md)
- [Persistence workflow / 持久化流程](docs/persistence_workflow.md)
- [Transaction boundary / 事务边界](docs/transaction_boundary.md)
- [Data model ERD / 数据模型](docs/data_erd.md)

## Current Scope / 当前范围

- The asynchronous worker currently registers `BuyAndHold`; other strategies are used by standalone research scripts.
- Market data is repository-local CSV input rather than a live ingestion service.
- Authentication and production deployment configuration are not included yet.

- 异步 Worker 当前注册 `BuyAndHold`；其他策略由独立研究脚本使用。
- 行情数据来自仓库内 CSV，而不是实时采集服务。
- 当前尚未包含身份认证和生产部署配置。

