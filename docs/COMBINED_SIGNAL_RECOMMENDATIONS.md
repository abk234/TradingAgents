# Combined Signal Recommendations

**Feature:** Smart trading recommendations based on RSI + signal combinations

**Status:** ✅ IMPLEMENTED

**Date:** 2025-11-17

---

## Overview

The screener now includes a **Recommendation** column that combines RSI values with technical signals to provide clear trading recommendations:

- **STRONG BUY** (bright green) - Multiple bullish signals align
- **BUY** (green) - Good buying opportunity
- **NEUTRAL** (dim) - No clear signal, wait
- **WAIT** (yellow) - Conflicting signals, wait for clarity
- **SELL** (red) - Consider selling
- **STRONG SELL** (bright red) - Multiple bearish signals align

---

## Recommendation Logic

### STRONG BUY 🟢🟢

**Bright green, bold** - Best buying opportunities

1. **RSI < 30 + MACD_BULLISH_CROSS + VOLUME_SPIKE**
   - Oversold + bullish momentum + high volume = strongest signal

2. **RSI < 30 + MACD_BULLISH_CROSS**
   - Oversold + bullish momentum = very strong buy

3. **RSI < 30 + BB_LOWER_TOUCH**
   - Oversold + touching support = strong buy

### BUY 🟢

**Green** - Good buying opportunities

1. **RSI < 30** (oversold alone)
   - Stock is oversold, potential bounce

2. **MACD_BULLISH_CROSS + RSI < 50**
   - Bullish momentum + neutral/low RSI = buy

3. **MACD_BULLISH_CROSS + VOLUME_SPIKE**
   - Bullish momentum + high volume = buy

### NEUTRAL ⚪

**Dim** - No clear signal

1. **MACD_BULLISH_CROSS** (but RSI neutral)
   - Some bullish signals but not strong enough

2. **RSI 30-50** (neutral range)
   - Normal trading conditions

3. **No clear signals**
   - Default when no strong signals present

### WAIT 🟡

**Yellow** - Conflicting signals, wait for clarity

1. **MACD_BULLISH_CROSS + RSI > 70**
   - Bullish momentum but overbought - wait for pullback

2. **MACD_BEARISH_CROSS + RSI < 30**
   - Bearish momentum but oversold - might bounce, wait

### SELL 🔴

**Red** - Consider selling

1. **RSI > 70** (overbought alone)
   - Stock is overbought, potential pullback

2. **MACD_BEARISH_CROSS + RSI > 50**
   - Bearish momentum + high RSI = sell

### STRONG SELL 🔴🔴

**Bright red, bold** - Strongest sell signals

1. **RSI > 70 + MACD_BEARISH_CROSS**
   - Overbought + bearish momentum = strong sell

2. **RSI > 70 + BB_UPPER_TOUCH**
   - Overbought + touching resistance = strong sell

---

## Example Output

```
╭──────┬───────┬───────┬───────┬───────┬──────┬───────┬──────────────┬────────┬───────╮
│ Rank │ Symb… │ Name  │ Sect… │ Prio… │ RSI  │ Sign… │ Recommendation│  Price │ Chan… │
├──────┼───────┼───────┼───────┼───────┼──────┼───────┼──────────────┼────────┼───────┤
│  🥇  │ NUE   │ Nucor │ Basic │ 66.0% │ 44.1 │ MACD… │     BUY      │ $148.67│ +0.60%│
│  🥈  │ PEP   │ Pepsi │ Cons… │ 62.0% │ 44.2 │ MACD… │     BUY      │ $147.83│ +1.36%│
│  🥉  │ PFE   │ Pfiz… │ Heal… │ 58.0% │ 63.1 │ None  │   NEUTRAL    │ $25.08 │ +0.08%│
│  4   │ MRK   │ Merck │ Heal… │ 58.0% │ 69.4 │ BB_U… │   NEUTRAL    │ $92.86 │ -0.06%│
│  5   │ UPS   │ Unit… │ Indu… │ 57.0% │ 44.4 │ MACD… │   NEUTRAL    │ $94.19 │ -1.86%│
╰──────┴───────┴───────┴───────┴───────┴──────┴───────┴──────────────┴────────┴───────┘
```

---

## How to Use Recommendations

### For Quick Decisions:

1. **Look for STRONG BUY** - Best opportunities, multiple signals align
2. **Consider BUY** - Good opportunities, single strong signal
3. **Avoid STRONG SELL** - Don't buy these, consider selling if you own
4. **Wait on WAIT** - Conflicting signals, wait for clarity
5. **Ignore NEUTRAL** - No clear signal, use other analysis

### Combined with Priority Score:

- **STRONG BUY + Priority > 60** = Excellent opportunity
- **BUY + Priority > 50** = Good opportunity
- **NEUTRAL + Priority > 60** = Investigate further (might be undervalued)
- **SELL + Priority < 40** = Avoid

---

## Signal Combinations Explained

### Why NUE Shows "BUY":
- RSI: 44.1 (neutral, but < 50)
- MACD_BULLISH_CROSS: ✅
- **Result:** MACD bullish + RSI < 50 = BUY

### Why PEP Shows "BUY":
- RSI: 44.2 (neutral, but < 50)
- MACD_BULLISH_CROSS: ✅
- **Result:** MACD bullish + RSI < 50 = BUY

### Why PFE Shows "NEUTRAL":
- RSI: 63.1 (neutral-high)
- No MACD signals
- **Result:** No strong signals = NEUTRAL

### Why MRK Shows "NEUTRAL":
- RSI: 69.4 (near overbought, but not > 70)
- BB_UPPER_TOUCH: ✅
- **Result:** Near overbought but not strong enough = NEUTRAL

---

## Best Practices

### 1. Use Recommendations as Starting Point
- Don't blindly follow - always do your own research
- Recommendations are based on technical analysis only
- Consider fundamentals, news, and market conditions

### 2. Combine with Priority Score
- Higher priority + STRONG BUY = best opportunities
- Lower priority + BUY = still good, but less urgent

### 3. Consider Entry Timing
- STRONG BUY: Enter soon (within 1-3 days)
- BUY: Good entry, can wait a bit
- WAIT: Wait for better entry point
- SELL: Don't enter, consider exiting if you own

### 4. Risk Management
- Always set stop losses
- Don't invest more than recommended position size
- Diversify across multiple recommendations

---

## Technical Details

**Function:** `_generate_recommendation()` in `tradingagents/utils/cli_formatter.py`

**Inputs:**
- RSI value (0-100)
- Signal list (MACD_BULLISH_CROSS, RSI_OVERSOLD, etc.)
- Technical signals dict (from JSONB)

**Output:**
- Color-coded recommendation string
- Formatted for Rich terminal display

**Priority Order:**
1. STRONG BUY (highest priority)
2. BUY
3. NEUTRAL
4. WAIT
5. SELL
6. STRONG SELL (lowest priority)

---

## Summary

✅ **Recommendation column added** to screener results
✅ **Combines RSI + signals** for smart recommendations
✅ **Color-coded** for easy interpretation
✅ **7 recommendation levels** from STRONG BUY to STRONG SELL

**Result:** You can now quickly identify the best trading opportunities at a glance!

---

**Next Steps:**
1. Run screener: `python -m tradingagents.screener run --top 10`
2. Look for STRONG BUY and BUY recommendations
3. Combine with priority scores for best opportunities
4. Always do your own research before trading

