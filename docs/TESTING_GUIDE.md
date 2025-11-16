# Investment Intelligence System - Testing Guide

Comprehensive manual testing scenarios for end-to-end validation.

---

## Test Environment Setup

### 1. Verify Prerequisites

```bash
# Check PostgreSQL is running
brew services list | grep postgresql
# Expected: postgresql@14  started

# Check Ollama is running
ollama list
# Expected: nomic-embed-text and llama models listed

# Check database has data
psql investment_intelligence -c "SELECT COUNT(*) FROM tickers;"
# Expected: 16 (or your watchlist count)

# Check screener has run
psql investment_intelligence -c "SELECT COUNT(*) FROM daily_scans;"
# Expected: Number of past scans
```

### 2. Activate Virtual Environment

```bash
cd /Users/lxupkzwjs/Developer/eval/TradingAgents
source .venv/bin/activate
```

---

## Test Scenario 1: Daily Screening Workflow

### Objective
Verify the daily screener identifies opportunities correctly.

### Steps

```bash
# 1. Run the daily screener
python -m tradingagents.screener run

# Expected output:
# ==================== DAILY MARKET SCAN ====================
# Date: 2025-11-15
# Scanning 16 tickers...
#
# Completed in X.X seconds
# Top 5 Opportunities: [list of tickers]
```

### 2. View Today's Top Opportunities

```bash
python -m tradingagents.screener top 5

# Expected output:
# ==================== TOP 5 OPPORTUNITIES ====================
# Scan Date: 2025-11-15
#
# Rank 1: XOM (Energy) - Score: 78.5
#   Signals: MACD_BULLISH_CROSS, VOLUME_SPIKE
#   RSI: 45.2 | MACD: 1.25 | Volume: 2.1x
#
# Rank 2: V (Financial Services) - Score: 76.2
#   ...
```

### 3. View Full Report

```bash
python -m tradingagents.screener report

# Expected output:
# Full screening report with all tickers, statistics, alerts
```

### Expected Results

✅ **PASS Criteria:**
- Screener completes in <30 seconds for 16 tickers
- All tickers analyzed (check "Analyzed: 16/16")
- Priority scores between 0-100
- Triggered alerts listed for each ticker
- Top opportunities ranked correctly

❌ **FAIL Indicators:**
- Errors during price fetching
- Missing technical indicators
- No alerts triggered (unlikely with 16 tickers)
- Scores all zeros

---

## Test Scenario 2: Single Ticker Deep Analysis

### Objective
Verify deep analysis works for a single ticker with RAG.

### Steps

```bash
# Analyze AAPL with verbose output
python -m tradingagents.analyze AAPL --verbose
```

### Expected Output

```
======================================================================
INVESTMENT INTELLIGENCE SYSTEM - DEEP ANALYSIS
======================================================================
Date: 2025-11-15
Tickers: AAPL
RAG: Enabled
Store Results: Yes
======================================================================

[Ollama model loading messages...]

======================================================================
ANALYSIS RESULTS: AAPL
======================================================================

📅 Date: 2025-11-15
🎯 Decision: BUY | WAIT | HOLD | SELL
📊 Confidence: XX/100
🤖 RAG Context: ✓ Used | ✗ Not available

📝 Summary:
----------------------------------------------------------------------
Analysis of AAPL on 2025-11-15
Recommendation: [decision]
Confidence: XX/100
Investment Consensus: [consensus summary]

📈 ANALYST REPORTS:
======================================================================

MARKET ANALYST:
----------------------------------------------------------------------
[Market analysis with technical indicators, price action, trends]

FUNDAMENTALS ANALYST:
----------------------------------------------------------------------
[Financial analysis with P/E, growth rates, balance sheet]

NEWS ANALYST:
----------------------------------------------------------------------
[Recent news, insider activity, market sentiment]

SOCIAL ANALYST:
----------------------------------------------------------------------
[Social media sentiment, trending topics]

💬 INVESTMENT DEBATES:
======================================================================

BULL CASE:
----------------------------------------------------------------------
[Bullish arguments, growth catalysts, opportunities]

BEAR CASE:
----------------------------------------------------------------------
[Risks, headwinds, concerns]

INVESTMENT CONSENSUS:
----------------------------------------------------------------------
[Judge's decision on investment merit]

RISK ASSESSMENT:
----------------------------------------------------------------------
[Risk manager's evaluation]

📋 TRADER EXECUTION PLAN:
======================================================================
[Specific trading plan with entry/exit points]

🎬 FINAL TRADE DECISION:
======================================================================
[Detailed final decision with reasoning]
```

### Expected Results

✅ **PASS Criteria:**
- Analysis completes in 2-5 minutes (depending on Ollama model)
- All 4 analyst reports generated
- Investment debate shows bull/bear perspectives
- Final decision is clear (BUY/WAIT/HOLD/SELL)
- Confidence score between 50-100
- RAG context indicator shows "✓ Used" (may be "✗" if no historical data)
- No Python errors or tracebacks

⏱️ **Performance Benchmarks:**
- With RAG: 2-5 minutes total
- Without RAG (`--no-rag`): 1-3 minutes
- RAG overhead: ~500-1000ms

❌ **FAIL Indicators:**
- Analysis crashes or hangs
- Missing analyst reports
- No final decision provided
- Confidence score is 0 or >100
- Python exceptions in output

---

## Test Scenario 3: Multiple Ticker Analysis

### Objective
Verify batch analysis of multiple tickers.

### Steps

```bash
# Analyze top 3 from screener
python -m tradingagents.analyze AAPL GOOGL MSFT
```

### Expected Output

```
======================================================================
INVESTMENT INTELLIGENCE SYSTEM - DEEP ANALYSIS
======================================================================
Date: 2025-11-15
Tickers: AAPL, GOOGL, MSFT
RAG: Enabled
Store Results: Yes
======================================================================

[Analysis of AAPL]
======================================================================
ANALYSIS RESULTS: AAPL
======================================================================
[Full analysis...]

[Analysis of GOOGL]
======================================================================
ANALYSIS RESULTS: GOOGL
======================================================================
[Full analysis...]

[Analysis of MSFT]
======================================================================
ANALYSIS RESULTS: MSFT
======================================================================
[Full analysis...]

======================================================================
SUMMARY OF ALL ANALYSES
======================================================================
🟢 AAPL   - BUY  (Confidence: 85/100)
🟡 GOOGL  - WAIT (Confidence: 72/100)
🟢 MSFT   - BUY  (Confidence: 78/100)
```

### Expected Results

✅ **PASS Criteria:**
- All tickers analyzed sequentially
- Each gets full analysis
- Summary table at end
- Emoji indicators for decisions (🟢=BUY, 🔴=SELL, 🟡=HOLD/WAIT)

⏱️ **Performance:**
- 3 tickers: 6-15 minutes total
- Roughly 2-5 minutes per ticker

---

## Test Scenario 4: RAG System Validation

### Objective
Verify RAG historical intelligence is working.

### Steps

```bash
# 1. Run test suite
PYTHONPATH=/Users/lxupkzwjs/Developer/eval/TradingAgents \
  .venv/bin/python tradingagents/analyze/test_rag.py

# Expected: All 5 tests pass
```

```bash
# 2. First analysis (no history yet)
python -m tradingagents.analyze AAPL

# Expected: "🤖 RAG Context: ✗ Not available" (no historical analyses yet)
```

```bash
# 3. Second analysis of same ticker
python -m tradingagents.analyze AAPL

# Expected: "🤖 RAG Context: ✓ Used" (now has history from first analysis)
```

### Expected Results

✅ **PASS Criteria:**
- Test suite: 5/5 tests pass
- First analysis: RAG context not available (normal)
- Second analysis: RAG context available
- Historical intelligence appears in verbose output

📊 **RAG Context Components:**
When verbose, you should see historical context like:
```
======================================================================
HISTORICAL INTELLIGENCE FOR AAPL
======================================================================

## TICKER ANALYSIS HISTORY

**Most Recent Analysis**: 2025-11-15
  - Decision: **BUY**
  - Confidence: 85/100
  - Price: $XXX.XX

## SIMILAR PAST SITUATIONS

1. 2025-11-14 (Similarity: 87.5%)
   - Decision: **BUY** (Confidence: 82/100)
   - Summary: Strong momentum with...
```

---

## Test Scenario 5: Performance Comparison (With/Without RAG)

### Objective
Measure RAG performance impact.

### Steps

```bash
# 1. Analyze with RAG
time python -m tradingagents.analyze AAPL

# 2. Analyze without RAG
time python -m tradingagents.analyze AAPL --no-rag
```

### Expected Results

| Configuration | Time Range | Notes |
|--------------|------------|-------|
| With RAG | 2-5 min | Includes embedding + context retrieval |
| Without RAG | 1-3 min | Faster but no historical intelligence |
| RAG Overhead | ~500ms - 1s | Amortized over full analysis |

✅ **PASS Criteria:**
- Both complete successfully
- RAG version shows context
- Non-RAG version faster but no context
- Time difference reasonable (<1 minute extra for RAG)

---

## Test Scenario 6: Database Storage Verification

### Objective
Verify analyses are stored to database correctly.

### Steps

```bash
# 1. Check analyses before
psql investment_intelligence -c "SELECT COUNT(*) FROM analyses;"
# Note the count

# 2. Run analysis with storage
python -m tradingagents.analyze AAPL

# 3. Check analyses after
psql investment_intelligence -c "SELECT COUNT(*) FROM analyses;"
# Should be +1

# 4. View the stored analysis
psql investment_intelligence -c "
SELECT
  analysis_id,
  analysis_date,
  final_decision,
  confidence_score,
  LENGTH(executive_summary) as summary_length
FROM analyses
ORDER BY analysis_date DESC
LIMIT 1;
"
```

### Expected Output

```
 analysis_id | analysis_date | final_decision | confidence_score | summary_length
-------------+---------------+----------------+------------------+----------------
          1  | 2025-11-15    | BUY            |               85 |            450
```

✅ **PASS Criteria:**
- Analysis count increases by 1
- Analysis has valid decision (BUY/WAIT/SELL/HOLD)
- Confidence score between 0-100
- Executive summary has content (>100 chars)
- Analysis date matches today

---

## Test Scenario 7: Historical Context Growth

### Objective
Verify system learns from multiple analyses.

### Steps

```bash
# Day 1: Analyze 3 tickers
python -m tradingagents.analyze AAPL GOOGL MSFT

# Day 2: Analyze same tickers again
python -m tradingagents.analyze AAPL GOOGL MSFT --verbose

# Look for historical context in verbose output
```

### Expected Results

✅ **PASS Criteria:**
- Day 1: Little to no historical context
- Day 2: Rich historical context appears
- Similar situations identified
- Sector trends visible
- Context influences analysis quality

📊 **What to Look For in Day 2 Output:**
```
## TICKER ANALYSIS HISTORY

**Most Recent Analysis**: [Day 1 date]
  - Decision: **BUY**
  - Confidence: 85/100
  - Price: $XXX.XX

**Past 4 Analyses**:
  - [dates with decisions and confidence scores]

## SIMILAR PAST SITUATIONS

We've seen similar market conditions before:
[List of similar analyses with similarity percentages]

## SECTOR ANALYSIS: Technology

Recent sector activity (last 30 days):
  - Total analyses: 6
  - Buy signals: 4 (66.7% of analyses)
  - Average confidence: 78.5/100
```

---

## Test Scenario 8: Error Handling

### Objective
Verify graceful degradation when components fail.

### Test 8.1: Ollama Not Running

```bash
# Stop Ollama
pkill ollama

# Try to analyze
python -m tradingagents.analyze AAPL
```

**Expected:**
```
⚠ RAG initialization failed: [connection error]. Running without RAG.
[Analysis continues without historical context]
```

✅ **PASS:** System continues, shows warning, completes without RAG

### Test 8.2: Database Not Running

```bash
# Stop PostgreSQL
brew services stop postgresql@14

# Try to analyze
python -m tradingagents.analyze AAPL
```

**Expected:**
```
⚠ RAG initialization failed: [database error]. Running without RAG.
[Analysis continues]
```

✅ **PASS:** System continues without database features

### Test 8.3: Invalid Ticker

```bash
python -m tradingagents.analyze INVALID_TICKER
```

**Expected:**
- Error message about ticker not found
- Or analysis attempts but may fail during data fetching

---

## Test Scenario 9: CLI Options

### Objective
Test all CLI options work correctly.

### Test 9.1: Custom Date

```bash
python -m tradingagents.analyze AAPL --date 2024-11-01
```

✅ **PASS:** Analysis uses specified date

### Test 9.2: No Storage

```bash
# Count before
psql investment_intelligence -c "SELECT COUNT(*) FROM analyses;"

python -m tradingagents.analyze AAPL --no-store

# Count after (should be same)
psql investment_intelligence -c "SELECT COUNT(*) FROM analyses;"
```

✅ **PASS:** Analysis runs but database count unchanged

### Test 9.3: Debug Mode

```bash
python -m tradingagents.analyze AAPL --debug
```

✅ **PASS:** Extra debugging output, message tracing visible

---

## Test Scenario 10: Integration Flow

### Objective
Complete end-to-end workflow from screening to analysis.

### Complete Workflow

```bash
# 1. Morning: Run daily screener
python -m tradingagents.screener run

# 2. Review top opportunities
python -m tradingagents.screener top 5

# Output example:
# Rank 1: XOM - Score: 78.5
# Rank 2: V - Score: 76.2
# Rank 3: AAPL - Score: 74.8
# Rank 4: TSLA - Score: 72.1
# Rank 5: CAT - Score: 70.5

# 3. Deep analysis on top 3
python -m tradingagents.analyze XOM V AAPL

# 4. Review results and make decisions
# [Read the analysis output for each ticker]

# 5. Optional: Check what's stored
psql investment_intelligence -c "
SELECT
  t.symbol,
  a.analysis_date,
  a.final_decision,
  a.confidence_score
FROM analyses a
JOIN tickers t ON a.ticker_id = t.ticker_id
WHERE a.analysis_date = CURRENT_DATE
ORDER BY a.confidence_score DESC;
"
```

### Expected Complete Workflow

```
Morning (9:30 AM):
├─ Run screener → Get top 5 opportunities
└─ Total time: ~30 seconds

Morning (10:00 AM):
├─ Deep analysis on top 3 tickers
├─ RAG provides historical context
├─ Multi-agent analysis runs
└─ Total time: ~6-15 minutes

Review:
├─ Read analysis summaries
├─ Review confidence scores
├─ Check historical patterns
└─ Make investment decisions
```

✅ **PASS Criteria:**
- Complete workflow runs without errors
- Screener → Analyzer pipeline works
- Results are actionable
- Historical context enriches decisions

---

## Performance Benchmarks

### Expected Timing (16-ticker watchlist)

| Operation | Time | Notes |
|-----------|------|-------|
| Daily screener run | 20-40s | Depends on market hours |
| Price data update (incremental) | 5-10s | Per ticker |
| Single deep analysis (with RAG) | 2-5 min | Depends on LLM |
| Single deep analysis (no RAG) | 1-3 min | Faster without embeddings |
| Embedding generation | ~500ms | Per analysis |
| Vector similarity search | <50ms | With proper indexing |
| 3-ticker batch analysis | 6-15 min | Sequential processing |

### Resource Usage

| Component | RAM | CPU | Notes |
|-----------|-----|-----|-------|
| PostgreSQL | ~100MB | Low | Minimal with 16 tickers |
| Ollama (llama3.1) | ~8GB | High | During inference |
| Ollama (llama3.3) | ~40GB | High | Requires more RAM |
| Python process | ~200MB | Low | Steady state |

---

## Troubleshooting Common Issues

### Issue 1: "No module named 'tradingagents'"

**Solution:**
```bash
# Run from project root
cd /Users/lxupkzwjs/Developer/eval/TradingAgents

# Or use PYTHONPATH
PYTHONPATH=/Users/lxupkzwjs/Developer/eval/TradingAgents \
  python -m tradingagents.analyze AAPL
```

### Issue 2: Analysis hangs/takes very long

**Possible Causes:**
- Ollama model loading (first run slower)
- Large LLM model (llama3.3 vs llama3.1)
- Network issues fetching market data

**Solutions:**
```bash
# Use smaller model in config
"deep_think_llm": "llama3.1"  # Instead of llama3.3

# Check Ollama logs
ollama ps

# Use --no-rag for faster analysis
python -m tradingagents.analyze AAPL --no-rag
```

### Issue 3: "RAG Context: ✗ Not available" always

**Possible Causes:**
- No historical analyses stored yet
- Database empty
- Ollama embedding model not running

**Solutions:**
```bash
# Check if analyses are stored
psql investment_intelligence -c "SELECT COUNT(*) FROM analyses;"

# Run analysis with storage
python -m tradingagents.analyze AAPL  # (storage enabled by default)

# Verify Ollama embedding model
ollama list | grep nomic-embed-text
```

---

## Success Criteria Summary

### Minimum Viable System
✅ Daily screener runs successfully
✅ Single ticker analysis completes
✅ Results are stored to database
✅ No critical errors or crashes

### Fully Functional System
✅ All test scenarios pass
✅ RAG context appears after 2nd analysis
✅ Multi-ticker batch analysis works
✅ Performance within expected ranges
✅ Integration flow smooth

### Production Ready
✅ All test scenarios pass consistently
✅ RAG improving analysis quality
✅ Historical context rich and relevant
✅ Error handling graceful
✅ Performance optimized

---

## Next Steps After Testing

Once all tests pass, you're ready for:

1. **Daily Operations**
   - Morning: Run screener
   - Analyze top 3-5 opportunities
   - Track decisions over time

2. **Build Intelligence**
   - Store all analyses
   - Accumulate historical patterns
   - Improve RAG effectiveness

3. **Phase 4 Planning**
   - Automated batch analysis
   - Position sizing recommendations
   - Portfolio tracking
   - Performance monitoring

---

**Ready to test? Start with Test Scenario 1 (Daily Screening Workflow)!**
