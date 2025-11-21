# Software & Tools Inventory: TradingAgents Application

**Last Updated:** November 2025  
**Version:** 1.0

This document provides a comprehensive inventory of all software, libraries, frameworks, and tools used in the TradingAgents application.

---

## Table of Contents

1. [Programming Languages](#1-programming-languages)
2. [Core Frameworks & Libraries](#2-core-frameworks--libraries)
3. [AI & Machine Learning](#3-ai--machine-learning)
4. [Database & Data Storage](#4-database--data-storage)
5. [Financial Data APIs](#5-financial-data-apis)
6. [Web Frameworks & UI](#6-web-frameworks--ui)
7. [Monitoring & Observability](#7-monitoring--observability)
8. [Development Tools](#8-development-tools)
9. [Infrastructure & Deployment](#9-infrastructure--deployment)
10. [External Services & APIs](#10-external-services--apis)
11. [Build & Package Management](#11-build--package-management)

---

## 1. Programming Languages

### Primary Language
- **Python 3.10+** (Primary backend language)
  - Used for: Core application logic, agent orchestration, data processing
  - Minimum version: Python 3.10
  - Recommended: Python 3.13

### Secondary Languages
- **TypeScript** (Frontend web app)
- **JavaScript/Node.js** (Frontend build tools)
- **SQL** (Database queries and schema)

---

## 2. Core Frameworks & Libraries

### AI & Agent Orchestration
- **LangChain** (`langchain-openai>=0.1.0`)
  - Purpose: LLM integration and agent framework
  - Providers: OpenAI, Anthropic, Google, OpenRouter
  
- **LangGraph** (`langgraph>=0.0.40`)
  - Purpose: Multi-agent orchestration and workflow management
  - Used for: Agent coordination, decision graphs, state management

- **LangChain Experimental** (`langchain-experimental>=0.0.40`)
  - Purpose: Experimental LangChain features

- **LangChain Anthropic** (`langchain_anthropic>=0.1.0`)
  - Purpose: Claude AI integration

- **LangChain Google GenAI** (`langchain-google-genai>=1.0.0`)
  - Purpose: Google Gemini integration

### Vector Store & Embeddings
- **ChromaDB** (`chromadb>=0.4.0`)
  - Purpose: Vector database for RAG (Retrieval-Augmented Generation)
  - Used for: Pattern recognition, similarity search, memory storage

- **Ollama** (`ollama>=0.1.0`)
  - Purpose: Local LLM inference server
  - Models: llama3.3 (70B), llama3.1, mistral, qwen2.5
  - Endpoint: http://localhost:11434/v1

### Data Processing
- **Pandas** (`pandas>=2.0.0`)
  - Purpose: Data manipulation and analysis
  - Used for: Stock data processing, time series analysis

- **NumPy** (Implicit dependency)
  - Purpose: Numerical computing

### Utilities
- **Python-dotenv** (`python-dotenv>=1.0.0`)
  - Purpose: Environment variable management

- **Typing Extensions** (`typing-extensions>=4.0.0`)
  - Purpose: Enhanced type hints

- **Keyring** (`keyring>=24.0.0`)
  - Purpose: Secure credential storage

- **Requests** (`requests>=2.31.0`)
  - Purpose: HTTP client library

- **TQDM** (`tqdm>=4.66.0`)
  - Purpose: Progress bars for long-running operations

- **Pytz** (`pytz>=2023.3`)
  - Purpose: Timezone handling

- **Typer** (`typer>=0.9.0`)
  - Purpose: CLI framework

- **Rich** (`rich>=13.0.0`)
  - Purpose: Terminal formatting and UI
  - Used for: CLI output, tables, progress bars, syntax highlighting

- **Questionary** (`questionary>=2.0.0`)
  - Purpose: Interactive CLI prompts

---

## 3. AI & Machine Learning

### LLM Providers (Configurable)
- **OpenAI** (via LangChain)
  - Models: gpt-4o-mini, gpt-4o, o4-mini, o3-mini
  - Used for: Deep thinking, quick thinking agents

- **Anthropic Claude** (via LangChain)
  - Models: claude-3-5-haiku-latest, claude-3-5-sonnet-latest
  - Used for: Advanced reasoning

- **Google Gemini** (via LangChain)
  - Models: gemini-2.0-flash-lite, gemini-2.0-flash, gemini-2.5-flash
  - Used for: Multi-modal analysis

- **Ollama** (Local)
  - Models: llama3.3 (70B), llama3.1, mistral, qwen2.5
  - Used for: Local inference, cost-effective analysis

- **OpenRouter** (via LangChain)
  - Purpose: Unified API for multiple LLM providers

### Observability & Tracking
- **Langfuse** (`langfuse>=2.0.0`)
  - Purpose: LLM observability and tracing
  - Used for: Tracking agent calls, performance monitoring, debugging
  - UI: http://localhost:3001

---

## 4. Database & Data Storage

### Primary Database
- **PostgreSQL** (Version 16+)
  - Purpose: Primary relational database
  - Used for: Stock data, scan results, analysis history, portfolio data
  - Extensions: pgvector (for vector embeddings)
  - Connection: psycopg2-binary (`psycopg2-binary>=2.9.0`)

### Caching Layer
- **Redis** (`redis>=5.0.0`)
  - Purpose: Caching and session management
  - Version: Redis 6.2-alpine (Docker)
  - Port: 6379
  - Used for: API response caching, rate limiting

### Vector Database
- **ChromaDB** (`chromadb>=0.4.0`)
  - Purpose: Vector embeddings storage
  - Used for: RAG system, pattern recognition, similarity search

---

## 5. Financial Data APIs

### Stock Data Providers
- **yfinance** (`yfinance>=0.2.0`)
  - Purpose: Yahoo Finance API wrapper
  - Used for: Stock prices, historical data, technical indicators, fundamentals
  - Default provider for: Core stock APIs, technical indicators

- **Alpha Vantage** (API Key Required)
  - Purpose: Financial data API
  - Used for: Fundamental data, news data, alternative price sources
  - Rate limits: 60 requests/minute (with TradingAgents partnership)

- **EODHD** (`eodhd>=1.0.0`)
  - Purpose: End of Day Historical Data API
  - Used for: Historical stock data

- **Finnhub** (`finnhub-python>=2.4.0`)
  - Purpose: Financial data API
  - Used for: Market data, company information

- **AKShare** (`akshare>=1.12.0`)
  - Purpose: Chinese financial data API
  - Used for: Asian market data

- **Tushare** (`tushare>=1.2.0`)
  - Purpose: Chinese financial data API
  - Used for: Chinese market data

### Technical Analysis
- **StockStats** (`stockstats>=0.6.0`)
  - Purpose: Technical indicator calculations
  - Used for: MACD, RSI, Bollinger Bands, moving averages

- **Backtrader** (`backtrader>=1.9.0`)
  - Purpose: Backtesting framework
  - Used for: Strategy testing and validation

### News & Social Media
- **PRAW** (`praw>=7.7.0`)
  - Purpose: Python Reddit API Wrapper
  - Used for: Reddit sentiment analysis (r/wallstreetbets, r/stocks)

- **Feedparser** (`feedparser>=6.0.0`)
  - Purpose: RSS/Atom feed parser
  - Used for: News feed parsing

- **Parsel** (`parsel>=1.8.0`)
  - Purpose: HTML/XML parsing
  - Used for: Web scraping and data extraction

---

## 6. Web Frameworks & UI

### Backend API
- **FastAPI** (`fastapi>=0.100.0`)
  - Purpose: Modern Python web framework
  - Used for: REST API endpoints, agent orchestration API
  - Port: 8005
  - Features: Async support, automatic OpenAPI docs, type validation

- **Uvicorn** (`uvicorn>=0.20.0`)
  - Purpose: ASGI server
  - Used for: Running FastAPI application
  - Features: Hot reload, async support

### Conversational UI
- **Chainlit** (`chainlit>=2.5.5`)
  - Purpose: Conversational AI interface
  - Used for: Eddie's web chat interface
  - Port: 8000
  - Features: Real-time chat, streaming responses, file uploads

### Frontend Web App
- **Next.js** (`next@16.0.3`)
  - Purpose: React framework for web application
  - Used for: Modern web UI for TradingAgents
  - Port: 3000

- **React** (`react@19.2.0`)
  - Purpose: UI library
  - Used with: React DOM (`react-dom@19.2.0`)

- **TypeScript** (`typescript@^5`)
  - Purpose: Type-safe JavaScript

- **Tailwind CSS** (`tailwindcss@^4`)
  - Purpose: Utility-first CSS framework
  - Used for: Styling web application

- **Framer Motion** (`framer-motion@^12.23.24`)
  - Purpose: Animation library
  - Used for: UI animations

- **Lucide React** (`lucide-react@^0.554.0`)
  - Purpose: Icon library

- **React Markdown** (`react-markdown@^10.1.0`)
  - Purpose: Markdown rendering
  - Used with: Remark GFM (`remark-gfm@^4.0.1`)

- **CLSX** (`clsx@^2.1.1`)
  - Purpose: Conditional class names

- **Tailwind Merge** (`tailwind-merge@^3.4.0`)
  - Purpose: Merge Tailwind classes

### Visualization
- **Plotly** (`plotly>=5.18.0`)
  - Purpose: Interactive charts and visualizations
  - Used for: Stock charts, technical indicators visualization

---

## 7. Monitoring & Observability

### Metrics Collection
- **Prometheus** (`prom/prometheus:latest`)
  - Purpose: Metrics collection and storage
  - Port: 9095 (mapped to 9090)
  - Used for: Application metrics, system metrics, custom metrics

- **Prometheus Client** (`prometheus-client>=0.21.0`)
  - Purpose: Python client for Prometheus metrics
  - Used for: Exposing metrics from FastAPI application

- **Prometheus FastAPI Instrumentator** (`prometheus-fastapi-instrumentator>=7.0.0`)
  - Purpose: Automatic FastAPI metrics instrumentation
  - Used for: HTTP metrics, request/response tracking

- **PSUtil** (`psutil>=6.1.0`)
  - Purpose: System and process utilities
  - Used for: System resource monitoring

### Visualization & Dashboards
- **Grafana** (`grafana/grafana:latest`)
  - Purpose: Metrics visualization and dashboards
  - Port: 3001 (mapped to 3000)
  - Used for: Creating monitoring dashboards, alerting

### Log Aggregation
- **Loki** (`grafana/loki:latest`)
  - Purpose: Log aggregation system
  - Port: 3100
  - Used for: Centralized log storage

- **Promtail** (`grafana/promtail:latest`)
  - Purpose: Log shipper for Loki
  - Used for: Collecting and shipping logs to Loki

### Alerting
- **AlertManager** (`prom/alertmanager:latest`)
  - Purpose: Alert routing and management
  - Port: 9093
  - Used for: Managing alerts from Prometheus

### Database Monitoring
- **PostgreSQL Exporter** (`prometheuscommunity/postgres-exporter:latest`)
  - Purpose: PostgreSQL metrics exporter
  - Port: 9187
  - Used for: Database performance metrics

- **Redis Exporter** (`oliver006/redis_exporter:latest`)
  - Purpose: Redis metrics exporter
  - Port: 9121
  - Used for: Cache performance metrics

### System Monitoring
- **Node Exporter** (`prom/node-exporter:latest`)
  - Purpose: System metrics exporter
  - Port: 9100
  - Used for: CPU, memory, disk, network metrics

---

## 8. Development Tools

### Code Quality
- **ESLint** (`eslint@^9`)
  - Purpose: JavaScript/TypeScript linting
  - Config: `eslint-config-next@16.0.3`

- **Babel Plugin React Compiler** (`babel-plugin-react-compiler@1.0.0`)
  - Purpose: React compiler optimization

### Build Tools
- **Setuptools** (`setuptools>=68.0.0`)
  - Purpose: Python package building and distribution

### Template Engine
- **Jinja2** (`jinja2>=3.0.0`)
  - Purpose: Template engine
  - Used for: Email templates, notification formatting

---

## 9. Infrastructure & Deployment

### Containerization
- **Docker** (Docker Engine)
  - Purpose: Containerization platform
  - Used for: Application containerization, service orchestration

- **Docker Compose** (Version 3.8)
  - Purpose: Multi-container Docker application orchestration
  - Files:
    - `docker-compose.yml` (Main application)
    - `docker-compose.monitoring.yml` (Monitoring stack)
    - `docker-compose.langfuse-v2.yml` (Langfuse observability)

### Base Images
- **Python 3.10-slim** (Dockerfile)
  - Purpose: Base image for application container
  - Includes: build-essential, git

- **Redis 6.2-alpine** (Docker Compose)
  - Purpose: Redis cache container

- **PostgreSQL 16** (Docker Compose - Langfuse)
  - Purpose: Database container for Langfuse

### Version Control
- **Git**
  - Purpose: Version control system
  - Used for: Source code management

---

## 10. External Services & APIs

### Notification Services
- **Yagmail** (`yagmail>=0.15.0`)
  - Purpose: Gmail SMTP client
  - Used for: Email notifications

- **Slack SDK** (`slack-sdk>=3.0.0`)
  - Purpose: Slack API integration
  - Used for: Slack notifications and alerts

### API Keys Required
- **OpenAI API Key** (Optional)
  - Purpose: OpenAI LLM access
  - Environment variable: `OPENAI_API_KEY`

- **Alpha Vantage API Key** (Recommended)
  - Purpose: Financial data access
  - Environment variable: `ALPHA_VANTAGE_API_KEY`
  - Note: Free tier available, increased rate limits for TradingAgents

- **Anthropic API Key** (Optional)
  - Purpose: Claude AI access
  - Environment variable: `ANTHROPIC_API_KEY`

- **Google API Key** (Optional)
  - Purpose: Gemini AI access
  - Environment variable: `GOOGLE_API_KEY`

- **Reddit API Credentials** (Optional)
  - Purpose: Reddit API access for sentiment analysis
  - Required for: Social media analyst agent

---

## 11. Build & Package Management

### Python Package Management
- **pip** (Python package installer)
  - Purpose: Installing Python dependencies
  - Requirements file: `requirements.txt`

- **uv** (Lock file present: `uv.lock`)
  - Purpose: Fast Python package installer and resolver
  - Used for: Dependency management (alternative to pip)

- **pyproject.toml**
  - Purpose: Python project configuration
  - Standard: PEP 518, PEP 621

### Node.js Package Management
- **npm** (Node Package Manager)
  - Purpose: Installing Node.js dependencies
  - Package file: `web-app/package.json`

---

## 12. System Requirements

### Operating System
- **Linux** (Recommended for production)
- **macOS** (Supported for development)
- **Windows** (Supported via WSL/Docker)

### Runtime Requirements
- **Python 3.10+** (Required)
- **Node.js 18+** (For web app)
- **PostgreSQL 16+** (Required)
- **Redis 6.2+** (Required for caching)
- **Docker & Docker Compose** (Optional, for containerized deployment)

### Hardware Recommendations
- **CPU**: 4+ cores recommended
- **RAM**: 8GB+ recommended (16GB+ for local LLM with Ollama)
- **Storage**: 20GB+ free space
- **GPU**: Optional, for local LLM acceleration (CUDA/ROCm)

---

## 13. Configuration Files

### Application Configuration
- `.env` - Environment variables (API keys, database credentials)
- `tradingagents/default_config.py` - Default application configuration
- `config/config_ollama.json` - Ollama-specific configuration
- `config/config_gemini.json` - Gemini-specific configuration

### Docker Configuration
- `Dockerfile` - Application container definition
- `docker-compose.yml` - Main application services
- `docker-compose.monitoring.yml` - Monitoring stack
- `docker-compose.langfuse-v2.yml` - Langfuse observability

### Monitoring Configuration
- `monitoring/prometheus/prometheus.yml` - Prometheus configuration
- `monitoring/prometheus/alerts.yml` - Alert rules
- `monitoring/grafana/provisioning/` - Grafana dashboards and datasources
- `monitoring/loki/loki-config.yml` - Loki configuration
- `monitoring/promtail/promtail-config.yml` - Promtail configuration
- `monitoring/alertmanager/alertmanager.yml` - AlertManager configuration

### Chainlit Configuration
- `.chainlit/config.toml` - Chainlit UI configuration

---

## 14. Port Assignments

| Service | Port | Purpose |
|---------|------|---------|
| Chainlit (Eddie UI) | 8000 | Conversational interface |
| FastAPI API | 8005 | REST API endpoints |
| Next.js Web App | 3000 | Modern web UI |
| PostgreSQL | 5432 | Database (default) |
| PostgreSQL (Langfuse) | 5435 | Langfuse database |
| Redis | 6379 | Cache |
| Prometheus | 9095 | Metrics collection |
| Grafana | 3001 | Monitoring dashboards |
| Loki | 3100 | Log aggregation |
| AlertManager | 9093 | Alert management |
| PostgreSQL Exporter | 9187 | Database metrics |
| Redis Exporter | 9121 | Cache metrics |
| Node Exporter | 9100 | System metrics |
| Langfuse UI | 3001 | LLM observability |
| Ollama | 11434 | Local LLM server |

---

## 15. Summary Statistics

### Total Dependencies
- **Python Packages**: 30+ core dependencies
- **Node.js Packages**: 15+ dependencies
- **Docker Images**: 10+ container images
- **External APIs**: 6+ financial data providers
- **LLM Providers**: 5+ configurable providers

### Technology Stack Summary
- **Backend**: Python 3.10+, FastAPI, LangGraph, LangChain
- **Frontend**: Next.js, React, TypeScript, Tailwind CSS
- **Database**: PostgreSQL, Redis, ChromaDB
- **AI/ML**: Multiple LLM providers, RAG system, vector embeddings
- **Monitoring**: Prometheus, Grafana, Loki, Langfuse
- **Infrastructure**: Docker, Docker Compose

---

## 16. License & Attribution

Most dependencies are open-source and follow their respective licenses. Key frameworks:
- **LangChain**: MIT License
- **FastAPI**: MIT License
- **Next.js**: MIT License
- **PostgreSQL**: PostgreSQL License
- **Redis**: BSD License

---

**Document Maintained By:** TradingAgents Development Team  
**Last Updated:** November 2025  
**Version:** 1.0

