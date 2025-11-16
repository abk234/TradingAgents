# Phase 6: Performance Tracking - Quick Start Guide

**5-Minute Setup Guide**

---

## 📋 What Phase 6 Does

Phase 6 creates a **feedback loop** for your AI investment system:
1. Tracks what happens to stocks after you get recommendations
2. Calculates win rates and returns
3. Compares your performance to the S&P 500
4. Identifies which signals/patterns work best
5. Generates comprehensive performance reports

---

## 🚀 Quick Start

### Step 1: First-Time Setup (2 minutes)

**The database migration should already be applied. If not:**
```bash
psql -U $USER -d investment_intelligence -f scripts/migrations/006_add_recommendation_outcomes.sql
```

### Step 2: Backfill Historical Data (1 minute)

**Create outcome records for all past analyses:**

**Option A - Using the wrapper script (easier):**
```bash
./scripts/evaluate.sh backfill --days 90
```

**Option B - Direct command:**
```bash
PYTHONPATH=/Users/lxupkzwjs/Developer/eval/TradingAgents python -m tradingagents.evaluate backfill --days 90
```

This will:
- Find all analyses from the last 90 days
- Create outcome tracking records
- Fetch historical price data
- Calculate returns at multiple intervals
- Update S&P 500 benchmark data
- Calculate alpha (excess returns)

### Step 3: View Performance Report (30 seconds)

**See how your AI performed:**
```bash
./scripts/evaluate.sh report --period 90
```

**Or quick stats:**
```bash
./scripts/evaluate.sh stats
```

---

## 📊 Daily Usage

### Option 1: Automated (Recommended)

**Set up daily cron job to update outcomes automatically:**

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 6 PM)
0 18 * * * cd /path/to/TradingAgents && ./scripts/daily_evaluation.sh >> logs/evaluation.log 2>&1
```

This automatically:
- Updates outcomes with latest prices
- Fetches S&P 500 data
- Calculates alpha
- Runs every day

### Option 2: Manual

**Run daily update manually:**
```bash
./scripts/evaluate.sh update

# Or with PYTHONPATH:
# PYTHONPATH=$PWD python -m tradingagents.evaluate update
```

---

## 📈 Weekly Performance Review

### Option 1: Automated Email Reports

**Get weekly performance reports via email:**

```bash
# Edit crontab
crontab -e

# Add this line (runs every Sunday at 9 AM)
0 9 * * 0 cd /path/to/TradingAgents && ./scripts/weekly_report.sh | mail -s "AI Trading Performance" your@email.com
```

### Option 2: Manual Report

**Generate report on demand:**
```bash
./scripts/evaluate.sh report --period 90
```

---

## 🔍 Viewing Results

### Quick Stats
```bash
./scripts/evaluate.sh stats --period 90
```

Output:
```
Total Recommendations: 45
Evaluated (30+ days):  28

Win Rate:              75.0%
Average Return:        +6.8%

S&P 500 Return:        +4.2%
Alpha:                 +2.6%
✅ Beating the market by 2.6%!
```

### Comprehensive Report
```bash
./scripts/evaluate.sh report --period 90
```

Shows:
- Overall statistics (total recs, win rate, avg return)
- Benchmark comparison (S&P 500, alpha)
- Outcome quality distribution
- Performance by confidence level
- Top 5 performers
- Worst 5 performers

### Recent Outcomes
```bash
./scripts/evaluate.sh recent --limit 20
```

Shows last 20 recommendations with returns at 1d, 7d, 30d.

---

## 🎯 What the Reports Tell You

### Win Rate
**What it means:** Percentage of recommendations that were correct

**Good performance:**
- 70%+ overall win rate
- 85%+ for high confidence (90-100) recommendations
- 60%+ for medium confidence (70-89) recommendations

### Average Return
**What it means:** Average % gain/loss on your recommendations

**Good performance:**
- Beat S&P 500 average (alpha > 0)
- +5% or higher on 30-day recommendations
- +10% or higher on 90-day recommendations

### Alpha
**What it means:** How much you beat (or trail) the S&P 500

**Interpretation:**
- Alpha > +2%: Excellent! You're adding significant value
- Alpha 0% to +2%: Good, beating the market
- Alpha < 0%: Underperforming, need to adjust strategy

### Outcome Quality
**Distribution you want to see:**
- 30%+ EXCELLENT (returns ≥ 15%)
- 30%+ GOOD (returns ≥ 8%)
- 20% NEUTRAL (returns ≥ 0%)
- < 20% POOR/FAILED (negative returns)

---

## 🛠️ Advanced Usage

### Custom Time Periods

```bash
# Last 30 days
python -m tradingagents.evaluate report --period 30

# Last 180 days (6 months)
python -m tradingagents.evaluate report --period 180

# Last year
python -m tradingagents.evaluate report --period 365
```

### Backfill Specific Period

```bash
# Backfill last 30 days only
python -m tradingagents.evaluate backfill --days 30

# Backfill last 6 months
python -m tradingagents.evaluate backfill --days 180
```

### Update Specific Period

```bash
# Update outcomes from last 30 days
python -m tradingagents.evaluate update --days 30
```

---

## 🔬 Understanding the Data

### Outcome Record Lifecycle

1. **Created (PENDING)**
   - When you run backfill or when new analysis is created
   - Has recommendation date, decision, confidence, entry price
   - Status: PENDING

2. **Tracking (TRACKING)**
   - Daily updates fetch current prices
   - Calculates returns at 1d, 3d, 7d, 14d, 30d, 60d, 90d
   - Tracks peak and trough prices
   - Status: TRACKING

3. **Completed (COMPLETED)**
   - After 90 days, evaluation is complete
   - All return intervals calculated
   - Quality score finalized
   - Status: COMPLETED

### Quality Scoring

**For BUY recommendations:**
- **EXCELLENT**: 30-day return ≥ 15%
- **GOOD**: 30-day return ≥ 8%
- **NEUTRAL**: 30-day return ≥ 0%
- **POOR**: 30-day return ≥ -5%
- **FAILED**: 30-day return < -5%

**For WAIT/SELL recommendations** (opposite logic):
- **EXCELLENT**: Stock fell ≥ 10%
- **GOOD**: Stock fell to 0%
- **NEUTRAL**: Stock rose ≤ 5%
- **POOR**: Stock rose ≤ 10%
- **FAILED**: Stock rose > 10%

---

## 🎓 Learning from Results

### High Win Rate, Low Returns
**What it means:** You're right often, but gains are small
**Action:** Increase position size on high-confidence calls

### Low Win Rate, High Returns
**What it means:** You're wrong often, but winners are big
**Action:** Tighter stop losses, let winners run

### Confidence Not Matching Results
**What it means:** 85% confidence calls only winning 60%?
**Action:** Recalibrate confidence scoring algorithm

### Beating Market on Good Picks, Losing on Bad Ones
**What it means:** Selection is good, but bad picks hurt too much
**Action:** Better risk management, smaller positions on uncertain calls

---

## 📊 Sample Reports

### Example: Good Performance
```
Win Rate:              78.5%
Average Return:        +8.2%
S&P 500 Return:        +5.1%
Alpha:                 +3.1%
✅ Beating the market by 3.1%!

Outcome Quality:
  EXCELLENT: 12 (35.3%)
  GOOD:      10 (29.4%)
  NEUTRAL:   5 (14.7%)
  POOR:      4 (11.8%)
  FAILED:    3 (8.8%)
```

### Example: Needs Improvement
```
Win Rate:              58.3%
Average Return:        +2.1%
S&P 500 Return:        +5.1%
Alpha:                 -3.0%
⚠️  Underperforming by 3.0%

Outcome Quality:
  EXCELLENT: 3 (12.0%)
  GOOD:      5 (20.0%)
  NEUTRAL:   4 (16.0%)
  POOR:      7 (28.0%)
  FAILED:    6 (24.0%)
```

**Action needed:** Review losing recommendations, identify patterns

---

## 🐛 Troubleshooting

### "No recommendations found"
**Cause:** No analyses in database yet
**Solution:** Run some analyses first:
```bash
python -m tradingagents.analyze AAPL --plain-english --portfolio-value 100000
```

### "No outcomes to update"
**Cause:** No outcome records created yet
**Solution:** Run backfill first:
```bash
python -m tradingagents.evaluate backfill --days 90
```

### "Price data not available"
**Cause:** yfinance API issue or invalid ticker
**Solution:** Wait and retry, or check if ticker symbol is correct

### "All outcomes show PENDING"
**Cause:** Recommendations are too recent (< 1 day old)
**Solution:** Wait for at least 1 day, then run update

---

## 🎉 Success!

You're now tracking AI performance! Here's what to do:

1. ✅ **Run backfill** to create historical outcome records
2. ✅ **Set up daily cron job** for automated updates
3. ✅ **Check weekly reports** to monitor performance
4. ✅ **Analyze results** to improve your strategy
5. ✅ **Celebrate wins** and learn from losses!

---

## 📞 Commands Reference

```bash
# Setup
./scripts/evaluate.sh backfill --days 90

# Daily (automated via cron)
./scripts/evaluate.sh update

# Reports
./scripts/evaluate.sh report --period 90
./scripts/evaluate.sh stats
./scripts/evaluate.sh recent --limit 20

# Automated scripts
./scripts/daily_evaluation.sh
./scripts/weekly_report.sh

# Alternative: Use PYTHONPATH directly
# PYTHONPATH=$PWD python -m tradingagents.evaluate <command>
```

---

**Ready to validate your AI?** Start with the backfill! 🚀
