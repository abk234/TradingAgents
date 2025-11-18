# Validation Walkthrough: Running Individual Scripts

**Purpose:** Step-by-step guide to validate the TradingAgents application using individual validation scripts

**Last Updated:** 2025-11-17

---

## Prerequisites

Before running validations, ensure:

1. **Virtual environment is activated:**
   ```bash
   source venv/bin/activate
   ```

2. **Database is running:**
   ```bash
   # Check PostgreSQL status
   brew services list | grep postgresql
   # Or on Linux:
   sudo systemctl status postgresql
   ```

3. **Dependencies installed:**
   ```bash
   pip install -r requirements.txt
   ```

---

## Validation Scripts Overview

### Core Validation Scripts

| Script | Purpose | Duration | Priority |
|--------|---------|----------|----------|
| `validate_eddie_prerequisites.py` | Database prerequisites | 5-10 sec | 🔴 Critical |
| `validate_system_data_flow.py` | End-to-end data flow | 30-60 sec | 🔴 Critical |
| `validate_data_accuracy.py` | Data quality checks | 20-40 sec | 🟡 Important |
| `validate_screener.py` | Screener functionality | 15-30 sec | 🟡 Important |
| `validate_agents.py` | Agent decision quality | 60-120 sec | 🟡 Important |
| `validate_high_priority_fixes.py` | Bug fixes validation | 30-60 sec | 🟢 Optional |

### Test Scripts

| Script | Purpose | Duration | Priority |
|--------|---------|----------|----------|
| `test_caching_implementation.py` | Price caching & LLM tracking | 10-20 sec | 🟡 Important |
| `test_application.py` | Basic application test | 30-60 sec | 🟢 Optional |
| `test_improvements.py` | Feature improvements | 40-80 sec | 🟢 Optional |

---

## Step-by-Step Validation Process

### Step 1: Validate Database Prerequisites

**Script:** `validate_eddie_prerequisites.py`

**What it checks:**
- Tickers table has sufficient data
- Price cache is populated
- Daily scans are recent
- Analyses exist with embeddings
- System configuration is set
- Vector extension enabled
- LLM tracking columns exist

**How to run:**
```bash
cd /Users/lxupkzwjs/Developer/eval/TradingAgents
source venv/bin/activate
python validate_eddie_prerequisites.py
```

**Expected output:**
```
✅ PASS Tickers: 111 active tickers across 13 sectors
✅ PASS Price Cache: 10+ tickers, newest: 2025-11-17
✅ PASS Daily Scans: Latest scan 2025-11-17
⚠️  WARN Analyses: 5 total, 0 with embeddings
✅ PASS System Config: 3/3 required configs present
✅ PASS Vector Extension: Enabled
✅ PASS LLM Tracking: 3/3 columns present

Overall Status: READY (or PARTIAL or NOT_READY)
```

**If it fails:**
- **Missing tickers:** Run `python -m tradingagents.screener`
- **Missing price cache:** Run `python scripts/precache_prices.py`
- **Missing scans:** Run `python -m tradingagents.screener`
- **Missing config:** Database schema may need initialization

**Success criteria:** Overall status should be "READY" or "PARTIAL"

---

### Step 2: Validate System Data Flow

**Script:** `validate_system_data_flow.py`

**What it checks:**
- Data layer (stock data retrieval)
- Database operations (CRUD)
- RAG system (embeddings)
- Four-gate framework
- Agent pipeline (full analysis)

**How to run:**
```bash
python validate_system_data_flow.py
```

**Expected output:**
```
Validating Data Layer...
✅ Stock data retrieval: PASS
✅ Technical indicators: PASS
✅ Fundamental data: PASS
✅ News data: PASS (or SKIP if no API keys)

Validating Database Operations...
✅ Ticker operations: PASS
✅ Analysis storage: PASS

Validating RAG System...
✅ Embedding generation: PASS
✅ Similarity search: PASS

Validating Four-Gate Framework...
✅ Fundamental gate: PASS
✅ Technical gate: PASS
✅ Risk gate: PASS
✅ Timing gate: PASS

Validating Agent Pipeline...
[This takes 30-90 seconds - runs full analysis]
✅ Agent pipeline: PASS

OVERALL: PASS (or PARTIAL or FAIL)
```

**If it fails:**
- **Data layer issues:** Check API keys (ALPHA_VANTAGE_API_KEY, etc.)
- **Database issues:** Check PostgreSQL connection
- **RAG issues:** Check pgvector extension
- **Agent pipeline:** Check Ollama/LLM is running

**Success criteria:** All critical components should PASS

---

### Step 3: Validate Data Accuracy

**Script:** `validate_data_accuracy.py`

**What it checks:**
- Price data consistency across sources
- Fundamental data accuracy
- News data quality
- Cross-source validation

**How to run:**
```bash
python validate_data_accuracy.py
```

**Expected output:**
```
Validating Price Data Accuracy...
✅ yfinance prices: PASS
✅ Alpha Vantage prices: PASS (if API key set)
✅ Price consistency: PASS (discrepancy < 2%)

Validating Fundamental Data...
✅ P/E ratios: PASS
✅ Market cap: PASS
✅ Revenue data: PASS

Validating News Data...
✅ News retrieval: PASS (or SKIP if no API keys)

OVERALL: PASS
```

**If it fails:**
- **Price discrepancies:** Check data sources, may be normal (< 2% is OK)
- **Missing fundamentals:** API key may be needed
- **News issues:** Optional, can skip if no API keys

**Success criteria:** Price consistency should be < 2% discrepancy

---

### Step 4: Validate Screener

**Script:** `validate_screener.py`

**What it checks:**
- Screener runs successfully
- Priority scores calculated
- Technical signals detected
- Sector analysis works

**How to run:**
```bash
python validate_screener.py
```

**Expected output:**
```
Validating Screener...
✅ Screener execution: PASS
✅ Priority scores: PASS (scores 0-100)
✅ Technical signals: PASS (RSI, MACD detected)
✅ Sector analysis: PASS
✅ Results storage: PASS

OVERALL: PASS
```

**If it fails:**
- **Execution timeout:** Database may be slow, increase timeout
- **No scores:** Check tickers table has data
- **Missing signals:** Check technical indicators are calculated

**Success criteria:** Screener should complete and produce scores

---

### Step 5: Validate Agents

**Script:** `validate_agents.py`

**What it checks:**
- Agent decision quality
- Four-gate framework integration
- Recommendation accuracy
- Confidence scores

**How to run:**
```bash
python validate_agents.py
```

**Expected output:**
```
Validating Agents...
✅ Fundamentals Analyst: PASS
✅ Technical Analyst: PASS
✅ News Analyst: PASS
✅ Trader Decision: PASS
✅ Risk Manager: PASS

Decision Quality:
✅ BUY signals have confidence > 70%
✅ Recommendations include reasoning
✅ Position sizing calculated

OVERALL: PASS
```

**If it fails:**
- **Agent errors:** Check LLM is running (Ollama/OpenAI)
- **Low confidence:** May be normal for test stocks
- **Missing reasoning:** Check agent outputs

**Success criteria:** Agents should produce valid decisions with reasoning

---

### Step 6: Validate Caching Implementation

**Script:** `test_caching_implementation.py`

**What it checks:**
- Price cache operations
- Cache hit/miss detection
- LLM tracking storage
- Cache cleanup

**How to run:**
```bash
python test_caching_implementation.py
```

**Expected output:**
```
TEST 1: Price Cache Operations
✅ Store prices: PASS
✅ Retrieve from cache: PASS
✅ Cache statistics: PASS

TEST 2: Cache Integration
✅ route_to_vendor_with_cache: PASS
✅ Cache hit detection: PASS
✅ Performance improvement: 2.1x faster

TEST 3: LLM Tracking
✅ Store analysis with LLM data: PASS
✅ Retrieve and verify: PASS

TEST 4: Cache Cleanup
✅ Cleanup execution: PASS

FINAL RESULT: 4 passed, 0 failed
```

**If it fails:**
- **Cache operations:** Check price_cache table exists
- **LLM tracking:** Check migrations 012 and 013 applied
- **Performance:** Should see speedup on cache hits

**Success criteria:** All 4 tests should PASS

---

### Step 7: Validate High Priority Fixes

**Script:** `validate_high_priority_fixes.py`

**What it checks:**
- Bug fixes are working
- API compatibility
- Error handling

**How to run:**
```bash
python validate_high_priority_fixes.py
```

**Expected output:**
```
Validating High Priority Fixes...
✅ API compatibility: PASS
✅ Error handling: PASS
✅ Data validation: PASS

OVERALL: PASS
```

**If it fails:**
- Review specific failing tests
- Check recent code changes
- May need to update validation script

**Success criteria:** All fixes should be validated

---

## Running All Validations Sequentially

### Option 1: Manual Sequential Run

```bash
# Activate environment
source venv/bin/activate

# Run each validation
echo "=== Step 1: Prerequisites ==="
python validate_eddie_prerequisites.py

echo "=== Step 2: Data Flow ==="
python validate_system_data_flow.py

echo "=== Step 3: Data Accuracy ==="
python validate_data_accuracy.py

echo "=== Step 4: Screener ==="
python validate_screener.py

echo "=== Step 5: Agents ==="
python validate_agents.py

echo "=== Step 6: Caching ==="
python test_caching_implementation.py
```

### Option 2: Use Master Validation Script

```bash
# Run all validations at once
python run_full_validation.py
```

This runs all validations and generates a comprehensive report.

---

## Interpreting Results

### Status Levels

- **✅ PASS:** Component is working correctly
- **⚠️  WARN:** Component works but has warnings (may need attention)
- **❌ FAIL:** Component has issues that need fixing
- **⏭️  SKIP:** Test skipped (e.g., no API keys)

### Overall Status

- **READY:** All critical components pass, ready for use
- **PARTIAL:** Most components pass, some warnings
- **NOT_READY:** Critical components failing, needs fixes

---

## Troubleshooting Common Issues

### Issue: "ModuleNotFoundError: No module named 'psycopg2'"

**Solution:**
```bash
source venv/bin/activate
pip install psycopg2-binary
```

### Issue: "Database connection failed"

**Solution:**
```bash
# Check PostgreSQL is running
brew services list | grep postgresql

# Start if needed
brew services start postgresql@14

# Verify connection
psql -d investment_intelligence -c "SELECT 1;"
```

### Issue: "Ollama not running"

**Solution:**
```bash
# Check Ollama
ollama list

# Start if needed (varies by system)
# On macOS: Check Ollama app is running
# On Linux: systemctl start ollama
```

### Issue: "No tickers in database"

**Solution:**
```bash
# Run screener to populate
python -m tradingagents.screener
```

### Issue: "Price cache empty"

**Solution:**
```bash
# Populate price cache
python scripts/precache_prices.py
```

### Issue: "API key missing"

**Solution:**
```bash
# Check .env file
cat .env | grep API_KEY

# Add missing keys to .env
# Note: Some validations can skip if API keys missing
```

---

## Validation Checklist

Use this checklist to track your validation progress:

- [ ] **Step 1:** Database prerequisites validated
- [ ] **Step 2:** System data flow validated
- [ ] **Step 3:** Data accuracy validated
- [ ] **Step 4:** Screener validated
- [ ] **Step 5:** Agents validated
- [ ] **Step 6:** Caching validated
- [ ] **Step 7:** High priority fixes validated

**All critical validations passing:** ✅ Ready for use

---

## Quick Validation Script

Create a simple script to run all validations:

```bash
#!/bin/bash
# quick_validate.sh

cd /Users/lxupkzwjs/Developer/eval/TradingAgents
source venv/bin/activate

echo "🔍 Running TradingAgents Validation Suite..."
echo ""

scripts=(
    "validate_eddie_prerequisites.py:Database Prerequisites"
    "validate_system_data_flow.py:System Data Flow"
    "validate_data_accuracy.py:Data Accuracy"
    "validate_screener.py:Screener"
    "validate_agents.py:Agents"
    "test_caching_implementation.py:Caching"
)

for script_info in "${scripts[@]}"; do
    IFS=':' read -r script name <<< "$script_info"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Running: $name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    python "$script"
    echo ""
done

echo "✅ Validation complete!"
```

Save as `quick_validate.sh`, make executable:
```bash
chmod +x quick_validate.sh
./quick_validate.sh
```

---

## Next Steps After Validation

1. **If all pass:** Application is ready for use!
2. **If partial:** Review warnings and fix non-critical issues
3. **If failures:** Fix critical issues before using application
4. **Document issues:** Note any failures for future reference

---

## Summary

**Recommended validation order:**
1. Prerequisites (fastest, checks foundation)
2. Data Flow (validates core functionality)
3. Data Accuracy (validates data quality)
4. Screener (validates screening feature)
5. Agents (validates decision-making)
6. Caching (validates performance features)

**Total time:** ~5-10 minutes for all validations

**Success criteria:** All critical validations should PASS

---

**Need help?** Check individual script files for detailed error messages and troubleshooting tips.

