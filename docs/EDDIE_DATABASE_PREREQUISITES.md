# Eddie Database Prerequisites Guide

**Purpose:** Ensure Eddie can perform valid trading strategies and make prompt decisions

**Last Updated:** 2025-11-17

---

## Overview

For Eddie to provide valid trading recommendations and forecast the market promptly, the backend database must be properly populated with:

1. **Stock Watchlist** (`tickers` table)
2. **Recent Price Data** (`price_cache` table - NEW)
3. **Screening Results** (`daily_scans` table)
4. **Historical Analyses** (`analyses` table with embeddings)
5. **System Configuration** (`system_config` table)

---

## Required Database Tables & Data

### 1. Tickers Table (Watchlist) ✅ REQUIRED

**Purpose:** Eddie needs a watchlist of stocks to analyze

**Minimum Requirements:**
- At least 10-20 active tickers across multiple sectors
- Sector and industry classifications populated
- Active flag set to `true` for stocks to monitor

**How to Populate:**
```bash
# Option 1: Run screener (automatically adds tickers)
python -m tradingagents.screener

# Option 2: Add manually via Eddie
# Ask Eddie: "Add AAPL to watchlist"

# Option 3: Use database script
python scripts/init_database.py
```

**Validation Query:**
```sql
SELECT COUNT(*) as ticker_count, 
       COUNT(DISTINCT sector) as sector_count
FROM tickers 
WHERE active = true;
-- Should have: ticker_count >= 10, sector_count >= 3
```

---

### 2. Price Cache Table ✅ REQUIRED (NEW)

**Purpose:** Fast price lookups for prompt decision-making (10x faster than API calls)

**Minimum Requirements:**
- Recent price data (within 24 hours) for active tickers
- Historical data (last 30-90 days) for technical analysis
- Realtime data (< 5 minutes old) for intraday decisions

**How to Populate:**
```bash
# Automatic: Price caching happens automatically when:
# 1. Running screener
# 2. Analyzing stocks
# 3. Using route_to_vendor_with_cache()

# Manual refresh:
python -c "
from tradingagents.dataflows.interface import route_to_vendor_with_cache
from datetime import date, timedelta
route_to_vendor_with_cache('get_stock_data', 'AAPL', 
    (date.today() - timedelta(days=90)).strftime('%Y-%m-%d'),
    date.today().strftime('%Y-%m-%d'))
"
```

**Validation Query:**
```sql
SELECT 
    COUNT(DISTINCT ticker_id) as tickers_with_data,
    MIN(price_date) as oldest_data,
    MAX(price_date) as newest_data,
    COUNT(*) as total_records
FROM price_cache
WHERE price_date >= CURRENT_DATE - INTERVAL '7 days';
-- Should have: tickers_with_data >= 10, newest_data = TODAY
```

---

### 3. Daily Scans Table ✅ REQUIRED

**Purpose:** Eddie uses screening results to identify opportunities and understand market state

**Minimum Requirements:**
- Scan from today or yesterday
- Priority scores calculated for ranking
- Technical signals populated (RSI, MACD, etc.)

**How to Populate:**
```bash
# Run daily screener
python -m tradingagents.screener
# or
./run_screener.sh

# Via Eddie:
# Ask: "Run screener" or "What stocks should I look at?"
```

**Validation Query:**
```sql
SELECT 
    scan_date,
    COUNT(*) as stocks_scanned,
    AVG(priority_score) as avg_score,
    MAX(priority_score) as max_score
FROM daily_scans
WHERE scan_date >= CURRENT_DATE - INTERVAL '1 day'
GROUP BY scan_date
ORDER BY scan_date DESC
LIMIT 1;
-- Should have: scan_date >= YESTERDAY, stocks_scanned >= 10
```

---

### 4. Analyses Table ✅ RECOMMENDED

**Purpose:** Historical context for RAG, pattern recognition, and learning

**Minimum Requirements:**
- At least 5-10 recent analyses for Eddie to learn from
- Embeddings populated for RAG similarity search
- LLM tracking data for debugging

**How to Populate:**
```bash
# Via Eddie (recommended):
# Ask: "Analyze AAPL" or "Should I buy NVDA?"

# Programmatic:
python -c "
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
ta = TradingAgentsGraph(config=DEFAULT_CONFIG)
result = ta.propagate('AAPL', '2025-11-17')
"
```

**Validation Query:**
```sql
SELECT 
    COUNT(*) as total_analyses,
    COUNT(DISTINCT ticker_id) as unique_tickers,
    COUNT(*) FILTER (WHERE embedding IS NOT NULL) as with_embeddings,
    MAX(analysis_date) as latest_analysis
FROM analyses;
-- Should have: total_analyses >= 5, with_embeddings >= 5
```

---

### 5. System Configuration ✅ REQUIRED

**Purpose:** Thresholds and parameters for decision-making

**Minimum Requirements:**
- Screening thresholds configured
- Buy decision gate thresholds set
- Position sizing rules defined

**How to Populate:**
```sql
-- Usually auto-populated by schema.sql
-- Verify with:
SELECT config_key, config_value 
FROM system_config;
-- Should have: screening_thresholds, buy_decision_gates, position_sizing_rules
```

---

## Data Freshness Requirements

### For Prompt Decision-Making:

| Data Type | Maximum Age | Priority |
|-----------|------------|----------|
| Price Cache (realtime) | 5 minutes | 🔴 CRITICAL |
| Price Cache (EOD) | 24 hours | 🔴 CRITICAL |
| Daily Scans | 24 hours | 🔴 CRITICAL |
| Analyses | 7 days | 🟡 RECOMMENDED |
| Historical Prices | 90 days | 🟡 RECOMMENDED |

### Freshness Levels:

- 🟢 **FRESH** (< 4 hours): Ready for immediate decisions
- 🟡 **MODERATE** (4-12 hours): Acceptable for analysis
- 🟠 **STALE** (12-24 hours): Refresh recommended
- 🔴 **VERY STALE** (> 24 hours): **Cannot make reliable decisions**

---

## Prerequisites Checklist

Run this validation script to check prerequisites:

```bash
python validate_eddie_prerequisites.py
```

### Manual Checklist:

- [ ] **Database Connection**: PostgreSQL running and accessible
- [ ] **Tickers**: At least 10 active tickers in watchlist
- [ ] **Price Cache**: Recent data (< 24 hours) for active tickers
- [ ] **Daily Scans**: Scan from today or yesterday
- [ ] **Analyses**: At least 5 historical analyses (for learning)
- [ ] **System Config**: Thresholds configured
- [ ] **Vector Extension**: pgvector enabled for RAG
- [ ] **LLM Tracking**: Columns exist in analyses table

---

## Quick Setup Script

Run this to ensure all prerequisites are met:

```bash
#!/bin/bash
# ensure_eddie_prerequisites.sh

echo "🔧 Setting up Eddie prerequisites..."

# 1. Check database connection
python -c "from tradingagents.database import get_db_connection; get_db_connection()" || exit 1

# 2. Run screener to populate tickers, scans, and price cache
echo "📊 Running screener..."
python -m tradingagents.screener || ./run_screener.sh

# 3. Verify data freshness
echo "✅ Verifying data..."
python validate_eddie_prerequisites.py

echo "🎉 Setup complete! Eddie is ready."
```

---

## Optimizing for Prompt Decisions

### 1. Pre-populate Price Cache

**Before market opens:**
```bash
# Cache prices for all watchlist stocks
python scripts/precache_prices.py
```

### 2. Run Daily Screener

**Schedule cron job:**
```bash
# Add to crontab (runs at 9:30 AM daily)
30 9 * * 1-5 cd /path/to/TradingAgents && ./run_screener.sh
```

### 3. Keep Analyses Fresh

**Eddie learns from recent analyses:**
- Run at least 1-2 analyses per day
- Focus on high-priority opportunities from screener
- Store with embeddings for RAG

### 4. Monitor Data Freshness

**Use Eddie's dashboard:**
```
Ask Eddie: "What data do you have?"
Eddie will show freshness levels and recommendations
```

---

## Troubleshooting

### Issue: "No screening results available"

**Solution:**
```bash
# Run screener
python -m tradingagents.screener
```

### Issue: "Data is stale"

**Solution:**
```bash
# Refresh price cache
python scripts/precache_prices.py

# Re-run screener
python -m tradingagents.screener
```

### Issue: "No tickers in watchlist"

**Solution:**
```bash
# Add tickers via Eddie or script
python scripts/add_tickers.py AAPL MSFT NVDA GOOGL
```

### Issue: "Slow responses"

**Causes:**
- Missing price cache (using API calls)
- No recent scans (running full scan)
- Missing embeddings (can't use RAG)

**Solution:**
- Ensure price cache is populated
- Run daily screener
- Generate analyses with embeddings

---

## Performance Targets

For prompt decision-making, Eddie should achieve:

| Operation | Target Time | With Prerequisites |
|-----------|-------------|-------------------|
| Quick check (news/technicals) | 5-15 seconds | ✅ Achievable |
| Full stock analysis | 30-90 seconds | ✅ Achievable |
| Market screening | 10-30 seconds | ✅ With cached data |
| Pattern recognition | < 5 seconds | ✅ With embeddings |
| Data dashboard | < 2 seconds | ✅ With indexes |

**Without prerequisites:**
- All operations take 2-10x longer
- API rate limits may be hit
- No historical context available
- Decisions less reliable

---

## Next Steps

1. **Run validation script**: `python validate_eddie_prerequisites.py`
2. **Fix any missing prerequisites** using scripts above
3. **Set up daily automation** (cron jobs)
4. **Test Eddie**: Ask "What data do you have?" to verify
5. **Monitor freshness**: Use dashboard regularly

---

## Summary

**Critical Prerequisites:**
1. ✅ Active ticker watchlist (10+ stocks)
2. ✅ Recent price cache (< 24 hours)
3. ✅ Daily scans (< 24 hours)
4. ✅ System configuration

**Recommended Prerequisites:**
5. ✅ Historical analyses (5+ with embeddings)
6. ✅ RAG embeddings for pattern recognition
7. ✅ LLM tracking data

**Result:**
- ✅ Prompt decision-making (< 15 seconds for quick checks)
- ✅ Reliable trading recommendations
- ✅ Market forecasting capability
- ✅ Pattern recognition and learning

