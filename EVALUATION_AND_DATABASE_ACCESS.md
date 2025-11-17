# TradingAgents: Evaluation & Database Access Guide

## 📋 Quick Start

### Run Evaluation
```bash
source venv/bin/activate
python evaluate_application.py
```

### Access Databases
- **PostgreSQL**: `psql -U $USER -d investment_intelligence`
- **ChromaDB**: `./browse_chromadb.sh`

---

## 🧪 Application Evaluation

### Functionality Status

| Component | Status | Notes |
|-----------|--------|-------|
| **PostgreSQL Database** | ✅ Working | 110 tickers, 0 analyses |
| **ChromaDB** | ⚠️ Needs Fix | Pydantic compatibility issue |
| **Ollama** | ✅ Working | 20 models available |
| **Multi-Agent Analysis** | ✅ Working | 4 analyst teams |
| **RAG System** | ✅ Working | Historical context retrieval |
| **Memory System** | ✅ Working | 5 memory stores |
| **CLI Interface** | ✅ Working | Full interactive CLI |

### Performance Benchmarks

**Expected Performance:**
- **Screener (16 tickers)**: 7-10 seconds
- **Single Analysis**: 2-5 minutes
- **Database Queries**: <1 second
- **RAG Retrieval**: <2 seconds

**Optimization Features:**
- ✅ Fast mode available (60-80% speedup)
- ✅ Parallel analyst execution
- ✅ Connection pooling
- ✅ Data caching

### Accuracy Features

**Decision Quality:**
- ✅ Multi-perspective analysis (4 views)
- ✅ Bull vs Bear debate system
- ✅ 3-tier risk assessment
- ✅ Historical context via RAG
- ✅ Confidence scoring (0-100)

**Learning & Evolution:**
- ✅ Memory system (ChromaDB)
- ✅ Reflection on outcomes
- ✅ Pattern recognition
- ✅ Cross-ticker learning

---

## 🗄️ Database Access

### PostgreSQL Database

#### Connection
```bash
psql -U $USER -d investment_intelligence
```

#### Key Tables

**1. tickers** - Watchlist (110 active tickers)
```sql
SELECT symbol, company_name, sector, active 
FROM tickers 
WHERE active = true
ORDER BY symbol;
```

**2. analyses** - Analysis results
```sql
SELECT 
    t.symbol,
    a.analysis_date,
    a.final_decision,
    a.confidence_score,
    LEFT(a.executive_summary, 100) as summary
FROM analyses a
JOIN tickers t ON a.ticker_id = t.ticker_id
ORDER BY a.analysis_date DESC
LIMIT 20;
```

**3. daily_prices** - Historical prices
```sql
SELECT 
    price_date,
    open, high, low, close,
    volume,
    ma_20, ma_50, ma_200,
    rsi_14
FROM daily_prices 
WHERE ticker_id = (SELECT ticker_id FROM tickers WHERE symbol = 'AAPL')
ORDER BY price_date DESC
LIMIT 10;
```

**4. daily_scans** - Screener results
```sql
SELECT 
    t.symbol,
    ds.scan_date,
    ds.priority_score,
    ds.priority_rank,
    ds.triggered_alerts
FROM daily_scans ds
JOIN tickers t ON ds.ticker_id = t.ticker_id
WHERE ds.scan_date = CURRENT_DATE
ORDER BY ds.priority_rank
LIMIT 10;
```

**5. recommendation_outcomes** - Performance tracking
```sql
SELECT 
    t.symbol,
    ro.recommendation_date,
    ro.recommendation,
    ro.return_pct,
    ro.alpha_vs_sp500
FROM recommendation_outcomes ro
JOIN tickers t ON ro.ticker_id = t.ticker_id
WHERE ro.return_pct IS NOT NULL
ORDER BY ro.return_pct DESC
LIMIT 10;
```

#### Python Access
```python
from tradingagents.database import get_db_connection

db = get_db_connection()

# Query tickers
tickers = db.execute_dict_query("SELECT * FROM tickers WHERE active = true")
for t in tickers:
    print(f"{t['symbol']}: {t['company_name']}")

# Query analyses
analyses = db.execute_dict_query("""
    SELECT t.symbol, a.analysis_date, a.final_decision, a.confidence_score
    FROM analyses a
    JOIN tickers t ON a.ticker_id = t.ticker_id
    ORDER BY a.analysis_date DESC
    LIMIT 10
""")
```

#### GUI Tools
- **pgAdmin**: https://www.pgadmin.org/
- **DBeaver**: https://dbeaver.io/
- **TablePlus** (macOS): https://tableplus.com/

**Connection Details:**
- Host: `localhost`
- Port: `5432`
- Database: `investment_intelligence`
- User: Your OS username

---

### ChromaDB (Vector Database)

#### Access Methods

**1. Interactive Browser**
```bash
./browse_chromadb.sh
# Or
python browse_chromadb.py
```

**2. Python Script**
```python
import chromadb
from chromadb.config import Settings

# Connect (with environment variables set)
import os
os.environ.setdefault("CHROMA_SERVER_HOST", "localhost")
os.environ.setdefault("CHROMA_SERVER_HTTP_PORT", "8000")
os.environ.setdefault("CHROMA_SERVER_GRPC_PORT", "50051")

client = chromadb.Client(Settings(anonymized_telemetry=False))

# List collections
collections = client.list_collections()
for col in collections:
    print(f"{col.name}: {col.count()} items")

# Query a collection
collection = client.get_collection("bull_memory")
results = collection.query(
    query_texts=["High inflation with rising interest rates"],
    n_results=5
)
```

**3. Direct Memory Access**
```python
from tradingagents.agents.utils.memory import FinancialSituationMemory
from tradingagents.default_config import DEFAULT_CONFIG

memory = FinancialSituationMemory("bull_memory", DEFAULT_CONFIG)
memories = memory.get_memories("current situation", n_matches=5)
```

#### Collections
- `bull_memory` - Bull researcher memories
- `bear_memory` - Bear researcher memories
- `trader_memory` - Trader agent memories
- `invest_judge_memory` - Research manager memories
- `risk_manager_memory` - Portfolio manager memories

---

## 🔍 Useful Queries

### Get All Active Tickers
```sql
SELECT symbol, company_name, sector 
FROM tickers 
WHERE active = true
ORDER BY symbol;
```

### Recent Analyses
```sql
SELECT 
    t.symbol,
    a.analysis_date,
    a.final_decision,
    a.confidence_score,
    LEFT(a.executive_summary, 100) as summary
FROM analyses a
JOIN tickers t ON a.ticker_id = t.ticker_id
ORDER BY a.analysis_date DESC
LIMIT 20;
```

### Performance Statistics
```sql
SELECT 
    final_decision,
    COUNT(*) as count,
    AVG(confidence_score) as avg_confidence,
    MIN(confidence_score) as min_confidence,
    MAX(confidence_score) as max_confidence
FROM analyses
GROUP BY final_decision;
```

### Top Opportunities (Latest Scan)
```sql
SELECT 
    t.symbol,
    ds.priority_score,
    ds.priority_rank,
    ds.triggered_alerts
FROM daily_scans ds
JOIN tickers t ON ds.ticker_id = t.ticker_id
WHERE ds.scan_date = (SELECT MAX(scan_date) FROM daily_scans)
ORDER BY ds.priority_rank
LIMIT 10;
```

### Database Statistics
```sql
SELECT 
    'tickers' as table_name,
    COUNT(*) as row_count
FROM tickers
UNION ALL
SELECT 
    'analyses',
    COUNT(*)
FROM analyses
UNION ALL
SELECT 
    'daily_prices',
    COUNT(*)
FROM daily_prices
UNION ALL
SELECT 
    'daily_scans',
    COUNT(*)
FROM daily_scans;
```

---

## 🚀 Running the Application

### Interactive Mode
```bash
python -m cli.main analyze
```

### Non-Interactive (Default Values)
```bash
python run_with_defaults.py
```

### Evaluation Script
```bash
python evaluate_application.py
```

---

## 📊 Evaluation Results Template

After running evaluation, check:
- ✅ Execution time (< 180s is good)
- ✅ Report completeness (> 80% is excellent)
- ✅ RAG enabled
- ✅ All databases connected
- ✅ Decision generated

---

## 🛠️ Troubleshooting

### PostgreSQL Issues

**Database not found:**
```bash
createdb investment_intelligence
psql -U $USER -d investment_intelligence -f database/schema.sql
```

**Connection refused:**
```bash
# macOS
brew services start postgresql@14

# Linux
sudo systemctl start postgresql
```

### ChromaDB Issues

**Pydantic error:**
- Already fixed in `venv/lib/python3.14/site-packages/chromadb/config.py`
- If issue persists, run: `python run.py` (auto-fixes)

**Environment variables:**
- Set in `tradingagents/agents/utils/memory.py`
- Or set manually before running

---

## 📝 Quick Reference

### Database Connection Strings

**PostgreSQL:**
```
postgresql://username@localhost:5432/investment_intelligence
```

**ChromaDB:**
- In-memory by default
- No connection string needed

### Common Commands

```bash
# Connect to PostgreSQL
psql -U $USER -d investment_intelligence

# Browse ChromaDB
./browse_chromadb.sh

# Run evaluation
python evaluate_application.py

# Run analysis
python -m cli.main analyze
```

---

*Last Updated: 2025-01-16*

