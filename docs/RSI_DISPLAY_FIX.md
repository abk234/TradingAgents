# RSI Display Fix

**Issue:** RSI indicator was calculated and stored but not displayed in screener results table

**Status:** ✅ FIXED

**Date:** 2025-11-17

---

## The Problem

RSI (Relative Strength Index) was being:
- ✅ Calculated correctly in `indicators.py`
- ✅ Stored in `technical_signals` JSONB field in `daily_scans` table
- ❌ **NOT displayed** in the screener results table

The table showed:
- Rank, Symbol, Name, Sector, Priority, Signals, Price, Change
- But **RSI was missing**

---

## The Fix

**File:** `tradingagents/utils/cli_formatter.py`

**Changes:**
1. Added RSI column to the table (between Priority and Signals)
2. Extract RSI from `technical_signals` JSONB field
3. Color-code RSI values:
   - **Green** (< 30): Oversold - potential buy signal
   - **Yellow** (30-70): Neutral range
   - **Red** (> 70): Overbought - potential sell signal

---

## How RSI Works

**RSI (Relative Strength Index)** is a momentum oscillator that measures the speed and magnitude of price changes.

- **RSI < 30:** Oversold - stock may be undervalued, potential buy opportunity
- **RSI 30-70:** Neutral range - normal trading conditions
- **RSI > 70:** Overbought - stock may be overvalued, potential sell signal

---

## Updated Table Display

The screener results table now shows:

```
┌──────┬────────┬──────────┬──────────┬──────────┬──────┬──────────┬─────────┬────────┐
│ Rank │ Symbol │ Name     │ Sector   │ Priority │ RSI  │ Signals  │ Price   │ Change │
├──────┼────────┼──────────┼──────────┼──────────┼──────┼──────────┼─────────┼────────┤
│  🥇  │ NUE    │ Nucor    │ Basic    │ 66.0%    │ 44.1 │ MACD_BU… │ $148.67 │ +0.60% │
│  🥈  │ PEP    │ PepsiCo  │ Consumer │ 62.0%    │ 44.2 │ MACD_BU… │ $147.83 │ +1.36% │
│  🥉  │ PFE    │ Pfizer   │ Healthc… │ 58.0%    │ 63.1 │ None     │ $25.08  │ +0.08% │
└──────┴────────┴──────────┴──────────┴──────────┴──────┴──────────┴─────────┴────────┘
```

**RSI Color Coding:**
- 🟢 Green: RSI < 30 (oversold - buy opportunity)
- 🟡 Yellow: RSI 30-70 (neutral)
- 🔴 Red: RSI > 70 (overbought - sell signal)

---

## How to Use RSI

### For Buying:
- **RSI < 30:** Stock is oversold - good entry point
- **RSI 30-50:** Healthy range - can buy if other signals confirm
- **RSI > 70:** Avoid buying - wait for pullback

### For Selling:
- **RSI > 70:** Stock is overbought - consider taking profits
- **RSI 50-70:** Normal range - hold if other signals are positive
- **RSI < 30:** Don't sell - stock may be oversold

### Combined with Other Signals:
- **RSI < 30 + MACD_BULLISH_CROSS:** Strong buy signal
- **RSI > 70 + MACD_BEARISH_CROSS:** Strong sell signal
- **RSI 30-50 + Volume Spike:** Good momentum, consider buying

---

## Testing

To verify RSI is now displayed:

```bash
# Run screener
python -m tradingagents.screener run --top 10

# Check top opportunities
python -m tradingagents.screener top 10
```

RSI should now appear in the table with color coding!

---

## Summary

✅ **RSI is now displayed** in screener results
✅ **Color-coded** for easy interpretation
✅ **Extracted from JSONB** technical_signals field
✅ **Shows oversold/overbought** conditions at a glance

**Next Steps:**
- Use RSI along with other signals to make better trading decisions
- Look for oversold stocks (RSI < 30) as potential buy opportunities
- Avoid overbought stocks (RSI > 70) unless other signals are very strong

