# Screener Output → Deep Analysis Input
## Quick Reference Guide

---

## 🎯 TL;DR - What You Need to Know

**Your screener is working perfectly!** It has:
1. ✅ Scanned 108 tickers
2. ✅ Stored all data in `daily_scans` table
3. ✅ Ready to feed into deep analysis

**Next step:** Run deep analysis on top candidates

```bash
./scripts/run_daily_analysis.sh --fast
```

---

## 📊 Screener Output (What You Have Now)

### Table: `daily_scans`

Every ticker gets a record with:

| Field | What It Is | Example | Used For |
|-------|------------|---------|----------|
| **priority_score** | 0-100 composite score | 41 | **Select which stocks to analyze** |
| **technical_signals** | All indicators (JSONB) | {rsi: 35, macd: true} | **Pre-filter technical setups** |
| **triggered_alerts** | Alert conditions | [RSI_OVERSOLD] | **Identify specific opportunities** |
| **pe_ratio** | Valuation metric | 22.5 | **Fundamental screening** |
| **price** | Current price | 245.67 | **Entry point reference** |
| **volume** | Trading volume | 2,456,789 | **Liquidity check** |

### Priority Score Breakdown

From your log: `Score: 41 (T:35 V:5 M:65 F:65)`

```
41  = Total priority score (0-100)
│
├─ T:35  = Technical score (RSI, MACD, Bollinger Bands, MAs)
├─ V:5   = Volume score (volume ratio vs average)
├─ M:65  = Momentum score (20-day price return)
└─ F:65  = Fundamental score (P/E ratio, growth metrics)

Weighted: (35×40%) + (5×20%) + (65×15%) + (65×25%) = 41
```

### Your Top Candidates (from log)

```
Rank  Symbol  Score  Component Scores
────────────────────────────────────────────────
  1   DHR      41   T:35 V:5  M:65 F:65  ⭐ Top pick
  2   MRK      41   T:20 V:10 M:65 F:85  ⭐ Top pick
  3   DE       40   T:30 V:5  M:60 F:75  ⭐ Top pick
  4   WFC      39   T:35 V:5  M:45 F:70
  5   XEL      39   T:35 V:0  M:45 F:75
  6   UPS      39   T:20 V:0  M:65 F:85
  7   PFE      39   T:20 V:5  M:60 F:85
  8   SLB      39   T:20 V:0  M:65 F:85
  9   HON      39   T:30 V:0  M:60 F:75
 10   MMM      38   T:30 V:0  M:65 F:65
```

---

## 🔄 Deep Analysis Input (What It Needs)

### 1. Ticker Selection

```sql
-- Automatically selects from screener output
SELECT symbol, priority_score
FROM daily_scans ds
JOIN tickers t ON ds.ticker_id = t.ticker_id
WHERE scan_date = CURRENT_DATE
  AND priority_score >= 70  -- BUY threshold
ORDER BY priority_score DESC
LIMIT 3;
```

**Note:** Your top scores are 41, so you may want to lower the threshold or analyze top N regardless of score.

### 2. Technical Context (from screener)

```json
{
  "rsi": 35.2,
  "macd_bullish_crossover": true,
  "volume_ratio": 1.33,
  "twenty_day_return": 0.035,
  "near_bb_lower": true
}
```

### 3. Historical Data (from database)

```sql
-- Already stored in daily_prices table
SELECT * FROM daily_prices
WHERE ticker_id = 26  -- DHR
  AND price_date >= CURRENT_DATE - 90
ORDER BY price_date DESC;
```

### 4. Previous Analyses (RAG)

```sql
-- Retrieve similar past analyses
SELECT * FROM analyses
WHERE ticker_id = 26
ORDER BY analysis_date DESC
LIMIT 5;
```

---

## 🚀 How to Run Deep Analysis

### Option 1: Automated (Recommended)

```bash
# Analyze top 3 stocks (2-3 min each)
./scripts/run_daily_analysis.sh --fast

# What it does:
# 1. Reads daily_scans table
# 2. Selects top 3 by priority_score
# 3. Runs DeepAnalyzer on each
# 4. Stores results in analyses table
```

### Option 2: Manual Selection

```bash
# Analyze specific ticker
python -m tradingagents.analyze DHR

# Or use interactive CLI
python cli/main.py
```

### Option 3: Custom Query

```python
from tradingagents.analyze import DeepAnalyzer
from tradingagents.database import get_db_connection

db = get_db_connection()
analyzer = DeepAnalyzer(db=db)

# Analyze top candidate
result = analyzer.analyze("DHR")

print(f"Decision: {result['decision']}")
print(f"Confidence: {result['confidence']}")
```

---

## 📋 Data Flow Diagram (Simplified)

```
SCREENER                    DEEP ANALYSIS
════════                    ═════════════

daily_scans                 DeepAnalyzer
┌──────────────┐           ┌──────────────┐
│ priority: 41 │──────────▶│ Select: DHR  │
│ rsi: 35      │           │              │
│ macd: true   │──────────▶│ Technical    │
│ pe: 22.5     │           │ Gate: ✓      │
└──────────────┘           │              │
                           │ Fundamental  │
daily_prices               │ Gate: ✓      │
┌──────────────┐           │              │
│ 90 days OHLC │──────────▶│ Risk Gate: ✓ │
└──────────────┘           │              │
                           │ Timing: 72   │
analyses (RAG)             │              │
┌──────────────┐           │ DECISION:    │
│ Past DHR     │──────────▶│ BUY          │
│ analyses     │           │ Confidence:  │
└──────────────┘           │ 78%          │
                           └──────────────┘
                                  │
                                  ▼
                           analyses table
                           ┌──────────────┐
                           │ Store result │
                           │ for tracking │
                           └──────────────┘
```

---

## 🎯 Key Fields Mapping

| Screener Output | → | Deep Analysis Input |
|-----------------|---|---------------------|
| `priority_score >= 70` | → | Ticker selection criteria |
| `technical_signals.rsi` | → | Technical gate input |
| `technical_signals.macd` | → | Momentum analysis |
| `triggered_alerts` | → | Signal validation |
| `pe_ratio` | → | Fundamental gate input |
| `price` | → | Entry point baseline |
| `volume` | → | Liquidity assessment |

---

## 📊 Example: DHR Data Flow

### Screener Output
```json
{
  "symbol": "DHR",
  "priority_score": 41,
  "technical_signals": {
    "rsi": 35.2,
    "macd_bullish_crossover": true,
    "volume_ratio": 1.33
  },
  "pe_ratio": 22.5
}
```

### Deep Analysis Receives
```python
{
  "ticker": "DHR",
  "screener_score": 41,
  "technical_context": {...},
  "historical_prices": [...],
  "previous_analyses": [...]
}
```

### Deep Analysis Produces
```json
{
  "decision": "BUY",
  "confidence": 78,
  "entry_price": 243.50,
  "stop_loss": 230.00,
  "position_size": 5.0
}
```

---

## ⚡ Quick Commands

```bash
# 1. Check screener results
python -m tradingagents.screener report --top 10

# 2. Run deep analysis on top 3
./scripts/run_daily_analysis.sh --fast

# 3. View analysis results
python -m tradingagents.evaluate report

# 4. Analyze specific ticker
python -m tradingagents.analyze DHR
```

---

## 🔍 Verify Your Data

```sql
-- Check screener results
SELECT 
    t.symbol,
    ds.priority_score,
    ds.technical_signals->>'rsi' as rsi,
    ds.triggered_alerts
FROM daily_scans ds
JOIN tickers t ON ds.ticker_id = t.ticker_id
WHERE ds.scan_date = '2025-11-16'
ORDER BY ds.priority_score DESC
LIMIT 10;

-- Check if analyses exist
SELECT COUNT(*) FROM analyses;

-- Check latest analysis
SELECT 
    t.symbol,
    a.final_decision,
    a.confidence_score,
    a.analysis_date
FROM analyses a
JOIN tickers t ON a.ticker_id = t.ticker_id
ORDER BY a.analysis_date DESC
LIMIT 5;
```

---

## ✅ Your Current Status

```
✅ Screener completed
✅ 108 tickers scanned
✅ Priority scores calculated
✅ Data stored in daily_scans
✅ Sector analysis complete

⏳ Deep analysis: NOT RUN YET
   → Run: ./scripts/run_daily_analysis.sh --fast
```

---

## 🎓 Summary

**What the screener does:**
- Scans all tickers
- Calculates priority scores (0-100)
- Stores technical signals, alerts, fundamentals
- **Purpose:** Filter 110 stocks → top 3-5 candidates

**What deep analysis does:**
- Takes top candidates from screener
- Runs multi-agent analysis (30-45 min each)
- Generates BUY/WAIT/PASS decisions
- **Purpose:** Deep dive on pre-filtered opportunities

**The connection:**
- Screener output (`priority_score`, `technical_signals`) → Deep analysis input
- Screener is the filter, Deep analysis is the decision maker
- Screener runs daily (fast), Deep analysis runs on-demand (slow)

---

**Ready to proceed?**

```bash
./scripts/run_daily_analysis.sh --fast
```

This will analyze your top 3 candidates (DHR, MRK, DE) and generate actionable BUY/WAIT/PASS decisions.

