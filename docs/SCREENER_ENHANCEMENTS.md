# Screener Enhancements Summary

**Date:** 2025-11-17

**Status:** ✅ IMPLEMENTED

---

## New Features Added

### 1. ✅ Dividend Yield Column

**What it shows:**
- Annual dividend yield percentage
- Calculated from dividend history or cache
- Green color when yield > 0%

**How it works:**
- First checks `dividend_yield_cache` table
- Falls back to calculating from `dividend_payments` table (last 4 dividends)
- Shows "N/A" if no dividend data available

**Example:**
```
Div Yield: 2.45%  (green)
Div Yield: N/A    (dim, no dividends)
```

---

### 2. ✅ Recommended Entry Price

**What it shows:**
- Optimal entry price range based on:
  - Historical support levels (Bollinger Bands lower)
  - Moving averages (50-day, 200-day)
  - RSI levels (oversold/overbought)
  - Technical analysis

**How it's calculated:**
- Uses `PositionSizer.calculate_entry_timing()`
- Considers:
  - Support levels (BB lower, moving averages)
  - RSI (oversold = buy now, overbought = wait for pullback)
  - Price vs moving averages
  - Trend direction

**Example outputs:**
- `$145.50-$148.20` (green) - Entry range
- `$145.50` (green) - Single target price
- `$135.20` (yellow) - Wait for pullback (overbought)

---

### 3. ✅ BUY-Only Filter

**New flag:** `--buy-only`

**What it does:**
- Filters screener results to show only BUY and STRONG BUY recommendations
- Hides NEUTRAL, WAIT, SELL recommendations
- Shows more actionable opportunities

**Usage:**
```bash
# Show only BUY recommendations
python -m tradingagents.screener run --top 20 --buy-only

# Result: Only stocks with BUY/STRONG BUY recommendations
```

---

## Updated Table Columns

The screener table now shows:

| Column | Description | Example |
|--------|-------------|---------|
| Rank | Ranking (🥇🥈🥉) | 🥇 |
| Symbol | Stock ticker | AAPL |
| Name | Company name | Apple Inc. |
| Sector | Market sector | 💻 Technology |
| Priority | Priority score | 66.0% |
| RSI | RSI indicator | 44.1 (color-coded) |
| Signals | Technical alerts | MACD_BULLISH_CROSS |
| **Recommendation** | **BUY/SELL/NEUTRAL** | **BUY** |
| **Div Yield** | **Dividend yield %** | **2.45%** |
| **Entry Price** | **Recommended entry** | **$145.50-$148.20** |
| Price | Current price | $150.25 |
| Change | Price change % | +0.60% |

---

## Entry Price Logic

### When RSI < 30 (Oversold):
- **Entry:** Current price or slightly below (98% of current)
- **Reasoning:** Stock is oversold, good entry opportunity
- **Color:** Green

### When RSI > 70 (Overbought):
- **Entry:** Wait for pullback (92% of current = 8% below)
- **Reasoning:** Stock is overbought, wait for better entry
- **Color:** Yellow

### When RSI 30-70 (Neutral):
- **Entry:** Within 2% of current price (98%-102%)
- **Reasoning:** Normal trading range
- **Color:** Dim

### With Support Level:
- **Entry:** Near support level (BB lower or MA)
- **Reasoning:** Support provides good risk/reward
- **Color:** Green

### With Moving Averages:
- **Entry:** Above MA50/MA200 = buy now
- **Entry:** Below MA50/MA200 = wait for breakout
- **Reasoning:** Trend confirmation

---

## Usage Examples

### Show All Results (Default)
```bash
python -m tradingagents.screener run --top 20
```
Shows top 20 stocks with all recommendations.

### Show Only BUY Recommendations
```bash
python -m tradingagents.screener run --top 20 --buy-only
```
Shows only stocks with BUY or STRONG BUY recommendations.

### Show More BUY Opportunities
```bash
python -m tradingagents.screener run --top 50 --buy-only
```
Shows up to 50 BUY recommendations (filters from larger set).

---

## Dividend Yield Calculation

### Method 1: From Cache (Fast)
- Uses `dividend_yield_cache` table
- Pre-calculated yields
- Fastest method

### Method 2: From History (Fallback)
- Queries `dividend_payments` table
- Gets last 4 dividends
- Calculates annual dividend
- Divides by current price

### Populating Dividend Data

To populate dividend data for better yield display:

```bash
# Update dividend calendar
python -m tradingagents.dividends update-calendar

# Backfill dividend history
python -m tradingagents.dividends backfill --years 5
```

---

## Entry Price Examples

### Example 1: Oversold Stock
```
Stock: AAPL
Current Price: $150.00
RSI: 28.5 (oversold)
Support: $145.00 (BB lower)

Entry Price: $145.00-$147.00 (green)
Reasoning: Near support, oversold = good entry
```

### Example 2: Overbought Stock
```
Stock: NVDA
Current Price: $500.00
RSI: 75.2 (overbought)
No support nearby

Entry Price: $460.00 (yellow)
Reasoning: Wait for 8% pullback from overbought level
```

### Example 3: Neutral Stock
```
Stock: MSFT
Current Price: $350.00
RSI: 45.0 (neutral)
MA50: $345.00

Entry Price: $343.00-$357.00 (dim)
Reasoning: Within 2% of current, neutral conditions
```

---

## Benefits

### 1. More Actionable Results
- **Before:** See all stocks, manually filter for BUY
- **After:** See only BUY recommendations with `--buy-only`

### 2. Dividend Income Planning
- **Before:** No dividend information in screener
- **After:** See dividend yield for income planning

### 3. Better Entry Timing
- **Before:** No guidance on when to buy
- **After:** Recommended entry price based on technical analysis

### 4. Faster Decision Making
- **Before:** Analyze each stock individually
- **After:** See entry price, yield, and recommendation at a glance

---

## Next Steps

### To Get Better Dividend Data:
```bash
# Populate dividend cache
python -m tradingagents.dividends update-calendar
python -m tradingagents.dividends backfill --years 5
```

### To Use Enhanced Screener:
```bash
# Daily workflow - find BUY opportunities
python -m tradingagents.screener run --top 20 --buy-only

# Review entry prices and dividend yields
# Execute trades at recommended entry prices
```

---

## Summary

✅ **Dividend Yield:** Now shown in screener results
✅ **Entry Price:** Calculated from historical analysis
✅ **BUY Filter:** Show only actionable recommendations
✅ **Better Decisions:** All key info in one table

**Result:** Faster, more informed trading decisions with clear entry prices and dividend information!

