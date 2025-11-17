# Database Access Guide for TradingAgents

## Overview

TradingAgents uses **two databases**:
1. **PostgreSQL** - Main database for analyses, tickers, prices, portfolio
2. **ChromaDB** - Vector database for embeddings and memory

---

## 🐘 PostgreSQL Database

### Database Information

- **Database Name**: `investment_intelligence`
- **Default Host**: `localhost`
- **Default Port**: `5432`
- **Default User**: Your OS username
- **Connection Pool**: 1-10 connections

### Access Methods

#### 1. **Command Line (psql)**

```bash
# Connect to database
psql -U $USER -d investment_intelligence

# Or with explicit connection
psql -h localhost -U your_username -d investment_intelligence
```

**Common Commands:**
```sql
-- List all tables
\dt

-- Describe a table
\d tickers
\d analyses
\d daily_prices

-- View table contents
SELECT * FROM tickers LIMIT 10;
SELECT * FROM analyses ORDER BY analysis_date DESC LIMIT 10;

-- Count records
SELECT COUNT(*) FROM tickers;
SELECT COUNT(*) FROM analyses;
SELECT COUNT(*) FROM daily_prices;

-- View recent analyses
SELECT 
    t.symbol,
    a.analysis_date,
    a.final_decision,
    a.confidence_score
FROM analyses a
JOIN tickers t ON a.ticker_id = t.ticker_id
ORDER BY a.analysis_date DESC
LIMIT 20;
```

#### 2. **Python Script**

```python
from tradingagents.database import get_db_connection

# Get connection
db = get_db_connection()

# Execute query
results = db.execute_dict_query(
    "SELECT * FROM tickers WHERE active = true"
)

for row in results:
    print(row)
```

#### 3. **Database GUI Tools**

**pgAdmin**:
- Download: https://www.pgadmin.org/
- Connect to: `localhost:5432`
- Database: `investment_intelligence`

**DBeaver**:
- Download: https://dbeaver.io/
- Create PostgreSQL connection
- Host: `localhost`, Port: `5432`, Database: `investment_intelligence`

**TablePlus** (macOS):
- Download: https://tableplus.com/
- Create PostgreSQL connection
- Connect to `investment_intelligence` database

#### 4. **Using Python REPL**

```python
# Activate virtual environment
source venv/bin/activate

# Start Python
python

# In Python:
from tradingagents.database import get_db_connection

db = get_db_connection()

# Query tickers
tickers = db.execute_dict_query("SELECT * FROM tickers")
print(tickers)

# Query analyses
analyses = db.execute_dict_query("""
    SELECT t.symbol, a.analysis_date, a.final_decision, a.confidence_score
    FROM analyses a
    JOIN tickers t ON a.ticker_id = t.ticker_id
    ORDER BY a.analysis_date DESC
    LIMIT 10
""")
for a in analyses:
    print(f"{a['symbol']} - {a['analysis_date']}: {a['final_decision']} ({a['confidence_score']})")
```

---

## 📊 Main Tables

### 1. **tickers**
Watchlist management
```sql
SELECT * FROM tickers;
```

**Columns:**
- `ticker_id` - Primary key
- `symbol` - Stock ticker (e.g., AAPL)
- `company_name` - Company name
- `sector` - Sector (e.g., Technology)
- `industry` - Industry
- `active` - Whether ticker is active
- `priority_tier` - Priority level (1=high, 2=medium, 3=low)

### 2. **daily_prices**
Historical price data
```sql
SELECT * FROM daily_prices 
WHERE ticker_id = (SELECT ticker_id FROM tickers WHERE symbol = 'AAPL')
ORDER BY price_date DESC
LIMIT 10;
```

**Columns:**
- `price_id` - Primary key
- `ticker_id` - Foreign key to tickers
- `price_date` - Date
- `open`, `high`, `low`, `close` - OHLC prices
- `volume` - Trading volume
- `ma_20`, `ma_50`, `ma_200` - Moving averages
- `rsi_14` - RSI indicator

### 3. **analyses**
Deep analysis results
```sql
SELECT 
    t.symbol,
    a.analysis_date,
    a.final_decision,
    a.confidence_score,
    a.executive_summary
FROM analyses a
JOIN tickers t ON a.ticker_id = t.ticker_id
ORDER BY a.analysis_date DESC;
```

**Columns:**
- `analysis_id` - Primary key
- `ticker_id` - Foreign key
- `analysis_date` - Date of analysis
- `final_decision` - BUY/SELL/HOLD/WAIT
- `confidence_score` - 0-100
- `executive_summary` - Summary text
- `bull_case`, `bear_case` - Debate results
- `key_catalysts` - Array of catalysts
- `risk_factors` - Array of risks
- `embedding` - Vector embedding (pgvector)

### 4. **daily_scans**
Screener results
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
ORDER BY ds.priority_rank;
```

### 5. **recommendation_outcomes**
Performance tracking
```sql
SELECT 
    t.symbol,
    ro.recommendation_date,
    ro.recommendation,
    ro.entry_price,
    ro.current_price,
    ro.return_pct,
    ro.alpha_vs_sp500
FROM recommendation_outcomes ro
JOIN tickers t ON ro.ticker_id = t.ticker_id
ORDER BY ro.recommendation_date DESC;
```

### 6. **portfolio_holdings**
Portfolio positions
```sql
SELECT 
    t.symbol,
    ph.shares,
    ph.cost_basis,
    ph.current_value,
    ph.unrealized_pnl
FROM portfolio_holdings ph
JOIN tickers t ON ph.ticker_id = t.ticker_id
WHERE ph.portfolio_id = 1;
```

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

### Top Performing Recommendations
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

### Latest Screener Results
```sql
SELECT 
    t.symbol,
    t.sector,
    ds.priority_score,
    ds.priority_rank,
    ds.triggered_alerts,
    ds.scan_date
FROM daily_scans ds
JOIN tickers t ON ds.ticker_id = t.ticker_id
WHERE ds.scan_date = (
    SELECT MAX(scan_date) FROM daily_scans
)
ORDER BY ds.priority_rank
LIMIT 10;
```

---

## 🗄️ ChromaDB (Vector Database)

### Access Methods

#### 1. **Python Script**

```python
import chromadb
from chromadb.config import Settings

# Connect to ChromaDB
client = chromadb.Client(Settings(anonymized_telemetry=False))

# List collections
collections = client.list_collections()
for col in collections:
    print(f"Collection: {col.name}, Count: {col.count()}")

# Access a collection
collection = client.get_collection("bull_memory")

# Query
results = collection.query(
    query_texts=["High inflation with rising interest rates"],
    n_results=5
)

for i, doc in enumerate(results['documents'][0]):
    print(f"{i+1}. {doc}")
```

#### 2. **Using browse_chromadb.py**

```bash
./browse_chromadb.sh
# Or
python browse_chromadb.py
```

This provides an interactive browser for ChromaDB collections.

#### 3. **Direct Python Access**

```python
from tradingagents.agents.utils.memory import FinancialSituationMemory
from tradingagents.default_config import DEFAULT_CONFIG

# Access memory
memory = FinancialSituationMemory("bull_memory", DEFAULT_CONFIG)

# Get memories
situation = "High inflation rate with rising interest rates"
memories = memory.get_memories(situation, n_matches=5)

for mem in memories:
    print(f"Similarity: {mem['similarity_score']:.2f}")
    print(f"Recommendation: {mem['recommendation']}")
    print()
```

---

## 📁 Database Files Location

### PostgreSQL
- **Data Directory**: Usually `/usr/local/var/postgres` (macOS Homebrew)
- **Config**: `/usr/local/var/postgres/postgresql.conf`
- **Logs**: Check PostgreSQL logs for location

### ChromaDB
- **Storage**: In-memory by default (transient)
- **Persistent**: Can be configured to use persistent storage
- **Location**: Check ChromaDB settings

---

## 🔧 Database Management

### Backup PostgreSQL

```bash
# Backup database
pg_dump -U $USER investment_intelligence > backup_$(date +%Y%m%d).sql

# Restore database
psql -U $USER investment_intelligence < backup_20250116.sql
```

### Initialize Database

```bash
# Run schema
psql -U $USER -d investment_intelligence -f database/schema.sql

# Or use Python script
python scripts/init_database.py
```

### Check Database Size

```sql
SELECT 
    pg_size_pretty(pg_database_size('investment_intelligence')) as db_size;

SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## 🚀 Quick Access Scripts

### View Recent Analyses
```bash
python -c "
from tradingagents.database import get_db_connection
db = get_db_connection()
results = db.execute_dict_query('''
    SELECT t.symbol, a.analysis_date, a.final_decision, a.confidence_score
    FROM analyses a
    JOIN tickers t ON a.ticker_id = t.ticker_id
    ORDER BY a.analysis_date DESC LIMIT 10
''')
for r in results:
    print(f\"{r['symbol']} | {r['analysis_date']} | {r['final_decision']} | {r['confidence_score']}\")
"
```

### Count Records
```bash
python -c "
from tradingagents.database import get_db_connection
db = get_db_connection()
print(f\"Tickers: {db.get_table_count('tickers')}\")
print(f\"Analyses: {db.get_table_count('analyses')}\")
print(f\"Prices: {db.get_table_count('daily_prices')}\")
print(f\"Scans: {db.get_table_count('daily_scans')}\")
"
```

---

## 📝 Environment Variables

For custom database connection:

```bash
export PGHOST=localhost
export PGPORT=5432
export PGUSER=your_username
export PGPASSWORD=your_password
export PGDATABASE=investment_intelligence
```

---

*Last Updated: 2025-01-16*

