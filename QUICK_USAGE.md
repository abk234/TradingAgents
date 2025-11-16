# Quick Usage Guide

Your Investment Intelligence System is ready! Here's how to use it.

---

## ⚡ Quick Start (2 minutes)

### Step 1: Run the Daily Screener

```bash
cd /Users/lxupkzwjs/Developer/eval/TradingAgents
python -m tradingagents.screener run
```

**What it does:** Analyzes all 16 tickers, identifies top opportunities
**Time:** ~30 seconds

### Step 2: See Top Opportunities

```bash
python -m tradingagents.screener top 5
```

**Output:**
```
==================== TOP 5 OPPORTUNITIES ====================
Scan Date: 2025-11-15

Rank 1: XOM (Energy) - Score: 78.5
  Signals: MACD_BULLISH_CROSS, VOLUME_SPIKE
  RSI: 45.2 | MACD: 1.25 | Volume: 2.1x

Rank 2: V (Financial Services) - Score: 76.2
  ...
```

### Step 3: Deep Analysis on Top Pick

#### For Beginners (Plain English - Recommended!)

```bash
python -m tradingagents.analyze XOM --plain-english --portfolio-value 100000
```

**What it does:**
- Simple, easy-to-understand recommendations
- Tells you exactly how much to invest ($$ amounts)
- Explains expected returns and risks in plain language
- Step-by-step instructions on what to do

**Perfect for:** Anyone new to investing or stock analysis

#### For Technical Users

```bash
python -m tradingagents.analyze XOM
```

**What it does:**
- Multi-agent analysis (market, fundamentals, news, social)
- RAG-enhanced with historical intelligence
- Technical indicators and detailed reports

**Time:** 2-5 minutes
**Output:** Comprehensive analysis report

---

## 🚀 Automated Batch Analysis (NEW!)

### Analyze Top 5 Automatically

```bash
python -m tradingagents.analyze.batch_analyze --top 5
```

**What it does:**
1. Gets top 5 from today's screener
2. Runs deep analysis on each
3. Stores results to database
4. Shows summary of all recommendations

**Time:** ~10-25 minutes (5 tickers × 2-5 min each)

**Output Summary:**
```
BUY Signals (2):
  XOM    | Confidence: 85/100 | Screener: #1 (78.5)
  AAPL   | Confidence: 78/100 | Screener: #3 (74.8)

WAIT Signals (2):
  V      | Confidence: 72/100 | Screener: #2 (76.2)
  TSLA   | Confidence: 68/100 | Screener: #4 (72.1)

Statistics:
  Total Analyzed: 5
  BUY Signals: 2 (40.0%)
  Average Confidence: 75.8/100
  RAG Context Used: 3/5
```

### Advanced Options

```bash
# Top 10 with minimum score of 70
python -m tradingagents.analyze.batch_analyze --top 10 --min-score 70

# Only tickers with specific alerts
python -m tradingagents.analyze.batch_analyze \
  --alerts "MACD_BULLISH_CROSS,RSI_OVERSOLD"

# Verbose output (full reports)
python -m tradingagents.analyze AAPL --verbose

# Without RAG (faster)
python -m tradingagents.analyze AAPL --no-rag

# Don't store to database
python -m tradingagents.analyze AAPL --no-store
```

---

## 📊 Complete Daily Workflow

### Morning Routine (9:30 AM - 10:00 AM)

```bash
# 1. Update watchlist prices and run screener
python -m tradingagents.screener run

# 2. Review top opportunities
python -m tradingagents.screener report
```

### Deep Analysis (10:00 AM - 11:00 AM)

```bash
# Option A: Analyze specific tickers
python -m tradingagents.analyze AAPL GOOGL MSFT

# Option B: Auto-analyze top 5 from screener
python -m tradingagents.analyze.batch_analyze --top 5

# Option C: Top 3 with high minimum score
python -m tradingagents.analyze.batch_analyze --top 3 --min-score 75
```

### Review Results

Read the analysis output for each ticker:
- **Decision:** BUY, WAIT, HOLD, or SELL
- **Confidence:** How confident the system is (0-100)
- **RAG Context:** Whether historical intelligence was used
- **Analyst Reports:** Market, fundamentals, news, social
- **Debates:** Bull case vs. bear case
- **Final Decision:** Detailed recommendation

### Make Investment Decisions

Based on the analysis:
1. **BUY signals with 80+ confidence** → Strong candidates
2. **BUY signals with 70-79 confidence** → Good candidates
3. **WAIT signals** → Good setup but timing not optimal
4. **HOLD** → Maintain if you own, don't enter new
5. **SELL** → Avoid or exit

---

## 🧪 Testing Commands

### Test RAG System

```bash
PYTHONPATH=/Users/lxupkzwjs/Developer/eval/TradingAgents \
  .venv/bin/python tradingagents/analyze/test_rag.py
```

**Expected:** All 5 tests pass

### Test Single Analysis

```bash
# First run (no history yet)
python -m tradingagents.analyze AAPL

# Second run (should use RAG context)
python -m tradingagents.analyze AAPL

# Look for: 🤖 RAG Context: ✓ Used
```

### Check Database

```bash
# See all analyses stored
psql investment_intelligence -c "
SELECT
  t.symbol,
  a.analysis_date,
  a.final_decision,
  a.confidence_score
FROM analyses a
JOIN tickers t ON a.ticker_id = t.ticker_id
ORDER BY a.analysis_date DESC
LIMIT 10;
"

# See recent scans
psql investment_intelligence -c "
SELECT
  scan_date,
  COUNT(*) as tickers_scanned,
  AVG(priority_score) as avg_score
FROM daily_scans
GROUP BY scan_date
ORDER BY scan_date DESC
LIMIT 5;
"
```

---

## 📚 Documentation

- **Testing Guide:** `docs/TESTING_GUIDE.md` - Comprehensive test scenarios
- **RAG Quick Start:** `docs/RAG_QUICK_START.md` - RAG system guide
- **Phase 3 Report:** `docs/PHASE_3_COMPLETION_REPORT.md` - Technical details
- **Future Features:** `docs/FUTURE_FEATURES.md` - Portfolio management roadmap
- **PRD:** `docs/PRD_Investment_Intelligence_System.md` - Full system design

---

## 🎯 What Works Now vs. What's Coming

### ✅ Available Now (Phase 1-3 Complete)

- [x] Daily screening of watchlist (16 tickers)
- [x] Technical indicator analysis
- [x] Priority scoring and ranking
- [x] Deep multi-agent analysis
- [x] RAG historical intelligence
- [x] BUY/WAIT/HOLD/SELL decisions
- [x] Confidence scoring
- [x] Batch analysis (top N from screener)
- [x] Database storage
- [x] PostgreSQL + pgvector
- [x] Ollama local models

### 🚧 Coming Soon (Phase 4+)

- [ ] Position sizing ($$ recommendations)
- [ ] Entry timing (when to buy)
- [ ] Dividend tracking
- [ ] Portfolio performance monitoring
- [ ] Automated rebalancing
- [ ] Risk/reward calculations
- [ ] Stop loss / target price tracking

See `docs/FUTURE_FEATURES.md` for full roadmap.

---

## 💡 Pro Tips

### 1. Build Historical Intelligence

Run analyses with storage enabled (default):
```bash
python -m tradingagents.analyze AAPL  # Stores by default
```

The more analyses you store, the better RAG works!

### 2. Focus on Top Opportunities

Don't analyze everything - use the screener to filter:
```bash
# Top 5 is usually enough
python -m tradingagents.analyze.batch_analyze --top 5
```

### 3. Use Minimum Score Threshold

Skip low-priority tickers:
```bash
# Only analyze if screener score ≥ 70
python -m tradingagents.analyze.batch_analyze --top 10 --min-score 70
```

### 4. Filter by Alerts

Focus on specific setups:
```bash
# Only analyze bullish technical setups
python -m tradingagents.analyze.batch_analyze \
  --alerts "MACD_BULLISH_CROSS,RSI_OVERSOLD,BB_LOWER_TOUCH"
```

### 5. Faster Analysis Without RAG

When you need quick results:
```bash
python -m tradingagents.analyze AAPL --no-rag
```

Saves ~1 second but loses historical context.

### 6. Review Historical Context

Use verbose mode to see what RAG found:
```bash
python -m tradingagents.analyze AAPL --verbose
```

Look for the "HISTORICAL INTELLIGENCE" section.

---

## ⚠️ Troubleshooting

### Screener Issues

**Problem:** "No price data found"
```bash
# Update prices manually
python -m tradingagents.screener update
```

**Problem:** "No scans found for today"
```bash
# Run the screener
python -m tradingagents.screener run
```

### Analysis Issues

**Problem:** "No opportunities found"
```bash
# Check if screener ran today
python -m tradingagents.screener report

# If not, run it
python -m tradingagents.screener run
```

**Problem:** Analysis very slow
- Using llama3.3 (70B)? Try llama3.1 (8B) in config
- First run loads model (slower)
- Disable RAG with `--no-rag` for speed

**Problem:** "RAG Context: ✗ Not available"
- Normal on first analysis of each ticker
- Run analysis again to build history
- Check Ollama is running: `ollama list`

### Database Issues

**Problem:** "Database connection failed"
```bash
# Start PostgreSQL
brew services start postgresql@14

# Verify
psql investment_intelligence -c "SELECT version();"
```

---

## 📞 Getting Help

### Run Diagnostics

```bash
# Test RAG system
PYTHONPATH=/Users/lxupkzwjs/Developer/eval/TradingAgents \
  .venv/bin/python tradingagents/analyze/test_rag.py

# Check services
brew services list | grep postgresql
ollama list
```

### Check Logs

Analysis errors will show in terminal output. Look for:
- Python tracebacks
- Database connection errors
- Ollama API errors

---

## 🎉 You're Ready!

Start with this simple workflow:

```bash
# 1. Morning screening
python -m tradingagents.screener run

# 2. See what's hot
python -m tradingagents.screener top 5

# 3. Deep dive on top 3
python -m tradingagents.analyze.batch_analyze --top 3

# 4. Review recommendations and decide!
```

**Happy investing! 🚀**

---

## Quick Command Reference

| Command | Purpose |
|---------|---------|
| `python -m tradingagents.screener run` | Run daily screener |
| `python -m tradingagents.screener top 5` | Show top 5 opportunities |
| `python -m tradingagents.screener report` | Full screening report |
| `python -m tradingagents.analyze TICKER` | Deep analysis of one ticker |
| `python -m tradingagents.analyze T1 T2 T3` | Analyze multiple tickers |
| `python -m tradingagents.analyze.batch_analyze --top 5` | Auto-analyze top 5 |
| `PYTHONPATH=... python tradingagents/analyze/test_rag.py` | Test RAG system |

**For full testing scenarios, see:** `docs/TESTING_GUIDE.md`
