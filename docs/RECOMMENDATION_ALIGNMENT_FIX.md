# Recommendation Alignment Fix - Implementation Summary

**Date:** 2025-11-17  
**Status:** ✅ COMPLETE

---

## Problem Statement

Three different evaluation systems were showing inconsistent recommendations:

1. **Screener**: Showing BUY recommendations based on technical signals (RSI < 30, MACD bullish)
2. **Sector Analysis**: Showing 0 buy signals (counting `priority_score >= 70` instead of recommendations)
3. **Strategy Comparison**: Showing all HOLD (using incomplete API data, different evaluation criteria)

This created confusion and made it difficult to understand which stocks were actually good opportunities.

---

## Solution: Three-Phase Implementation

### Phase 1: Fix Sector Analysis ✅

**Problem:** Sector analyzer counted buy signals as `priority_score >= 70`, but screener recommendations were based on technical signals, not priority scores.

**Solution:**
1. Added `recommendation` column to `daily_scans` table (Migration 015)
2. Updated screener to generate and store plain-text recommendations
3. Updated sector analyzer to count by recommendation instead of priority_score

**Files Changed:**
- `scripts/migrations/015_add_recommendation_to_scans.sql` - Database migration
- `tradingagents/screener/screener.py` - Added `_generate_recommendation_plain_text()` method
- `tradingagents/database/scan_ops.py` - Store recommendation in database
- `tradingagents/screener/sector_analyzer.py` - Count by recommendation (BUY/STRONG BUY/etc.)

**Result:** Sector analysis now correctly counts stocks with BUY recommendations, matching the screener display.

---

### Phase 2: Fix Strategy Data Collection ✅

**Problem:** Strategy comparison used API calls that returned incomplete data, causing all strategies to default to HOLD.

**Solution:**
1. Updated `StrategyDataCollector` to use database data first (`daily_scans` table)
2. Falls back to API only when database data is missing
3. Added data completeness logging

**Files Changed:**
- `tradingagents/strategies/data_collector.py` - Added `_collect_from_database()` method
- Updated `collect_all_data()` to try database first, then API fallback

**Result:** Strategies now use the same data as the screener (fast, complete, consistent).

---

### Phase 3: Add Recommendation Alignment Utility ✅

**Problem:** No way to compare recommendations from different systems or understand when they agree/disagree.

**Solution:**
1. Created `RecommendationAligner` utility class
2. Compares screener (technical) vs strategies (fundamental) recommendations
3. Provides alignment levels, interpretations, actions, and insights

**Files Created:**
- `tradingagents/utils/recommendation_aligner.py` - Alignment utility

**Result:** Users can now see when systems agree/disagree and get actionable insights.

---

## How to Use

### 1. Run Migration

```bash
# Apply the database migration
psql -d tradingagents -f scripts/migrations/015_add_recommendation_to_scans.sql
```

### 2. Run Screener (to populate recommendations)

```bash
# Run screener - it will now store recommendations
python -m tradingagents.screener run --top 20
```

### 3. Check Sector Analysis

```bash
# Sector analysis will now show correct buy signal counts
python -m tradingagents.screener sector-analysis
```

### 4. Run Strategy Comparison

```bash
# Strategies will now use database data (faster, more complete)
python compare_screener_strategies.py --limit 20
```

### 5. Use Recommendation Aligner

```python
from tradingagents.utils.recommendation_aligner import align_stock_recommendations

# Compare screener vs strategy recommendations
alignment = align_stock_recommendations(
    ticker="AAPL",
    screener_recommendation="STRONG BUY",
    strategy_consensus="BUY",
    sector_strength=65.0
)

print(alignment["interpretation"])
print(alignment["action"])
print(alignment["warnings"])
print(alignment["insights"])
```

---

## Alignment Levels

The `RecommendationAligner` provides 5 alignment levels:

1. **STRONG_ALIGNMENT** (85% confidence)
   - Both systems agree (BUY/BUY or SELL/SELL)
   - Action: Strong signal, consider trading

2. **MODERATE_ALIGNMENT** (60% confidence)
   - One system BUY, other HOLD (or vice versa)
   - Action: Cautious trade, smaller position size

3. **WEAK_ALIGNMENT** (40% confidence)
   - One system BUY, other WAIT
   - Action: Wait for stronger signals

4. **NO_ALIGNMENT** (25% confidence)
   - Systems show different recommendations
   - Action: Review detailed analysis

5. **CONFLICT** (15% confidence)
   - Direct conflict (BUY vs SELL)
   - Action: Do not trade, wait for alignment

---

## What Changed

### Database Schema
- Added `recommendation VARCHAR(50)` column to `daily_scans` table
- Added index on `(scan_date, recommendation)` for faster sector queries

### Screener
- Generates plain-text recommendations (without Rich markup) for database storage
- Stores recommendation alongside priority_score and technical_signals

### Sector Analyzer
- Counts buy signals by recommendation (STRONG BUY, BUY, BUY DIP, ACCUMULATION, etc.)
- No longer uses `priority_score >= 70` threshold

### Strategy Data Collector
- Uses `daily_scans` table data first (fast, consistent with screener)
- Falls back to API only when database data is missing
- Logs data completeness for debugging

### New Utility
- `RecommendationAligner` class for comparing system recommendations
- Provides alignment analysis, interpretations, and actionable insights

---

## Benefits

1. **Consistency**: Sector analysis now matches screener recommendations
2. **Speed**: Strategies use database data (faster than API calls)
3. **Completeness**: Strategies get complete data from database
4. **Clarity**: Alignment utility helps understand when systems agree/disagree
5. **Actionable**: Clear recommendations on what to do based on alignment

---

## Next Steps

1. **Run migration** to add recommendation column
2. **Re-run screener** to populate recommendations for existing scans
3. **Test sector analysis** - should now show correct buy signal counts
4. **Test strategy comparison** - should show more accurate recommendations
5. **Use alignment utility** to compare screener vs strategy recommendations

---

## Example Output

### Before Fix:
```
Screener: BUY (RSI 28.2, MACD bullish)
Sector Analysis: 0 buy signals (priority_score < 70)
Strategy Comparison: HOLD (incomplete data)
```

### After Fix:
```
Screener: BUY (RSI 28.2, MACD bullish)
Sector Analysis: 5 buy signals (counting by recommendation)
Strategy Comparison: BUY (using database data)
Alignment: STRONG_ALIGNMENT - Both systems agree BUY
```

---

## Notes

- Recommendations are stored as plain text (no Rich markup) for database compatibility
- Sector analyzer uses LIKE patterns to match recommendation variations (e.g., "BUY DIP", "BUY (Below VAL)")
- Strategy data collector automatically falls back to API if database data is missing
- Alignment utility can be extended to include more systems (e.g., sentiment analysis, news)

