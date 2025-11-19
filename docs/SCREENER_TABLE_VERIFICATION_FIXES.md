# Screener Table Verification & Fixes

**Date:** 2025-01-XX  
**Status:** ✅ COMPLETED

## Issues Identified

1. **Recommendation Logic Not Aligned with RSI**
   - Stocks with RSI >70 (overbought) were showing STRONG BUY recommendations
   - Stocks with RSI >80 (extremely overbought) were still recommending BUY
   - Example: MRK with RSI 77.1 showing STRONG BUY (should be WAIT)

2. **Entry Price Calculation Inconsistency**
   - Table was recalculating entry prices instead of using stored values from `EntryPriceCalculator`
   - Could lead to discrepancies between stored scan results and displayed values

3. **Profit Target Calculation**
   - Entry price for profit target calculation was extracted from formatted string
   - Should use stored `entry_price_min`/`entry_price_max` values directly

## Fixes Implemented

### 1. Enhanced Recommendation Logic (`cli_formatter.py`)

**Multi-Timeframe Signals with RSI Overbought:**
- RSI >80: STRONG_BUY → "⏳ WAIT (RSI >80)"
- RSI >70: STRONG_BUY → "⏳ WAIT (RSI >70)"
- BUY_THE_DIP still shows correctly (designed for pullbacks)

**Institutional Activity Signals:**
- RSI >80: BULLISH_ACCUMULATION/STRONG_BUYING → "⏳ WAIT (RSI >80)"
- RSI >70: BULLISH_ACCUMULATION/STRONG_BUYING → "⏳ WAIT (RSI >70)"

**Extremely Oversold Enhancement:**
- RSI <20: BUY → "STRONG BUY" (stronger signal)

### 2. Use Stored Entry Prices (`cli_formatter.py`)

**Before:**
```python
entry_price_str = _calculate_entry_price(...)  # Recalculated
```

**After:**
```python
# Use stored entry prices from scan results if available (more accurate)
entry_price_min = result.get('entry_price_min')
entry_price_max = result.get('entry_price_max')

if entry_price_min and entry_price_max:
    # Use stored values from EntryPriceCalculator
    entry_price_str = f"${entry_min:.2f}-${entry_max:.2f}"
else:
    # Fallback to calculating
    entry_price_str = _calculate_entry_price(...)
```

### 3. Profit Target Uses Stored Entry Prices

**Before:**
```python
# Extract from formatted string
prices = re.findall(r'\d+\.?\d*', entry_price_str)
entry_price_numeric = float(prices[0])
```

**After:**
```python
# Prefer stored entry prices (more accurate)
if entry_price_min and entry_price_max:
    entry_price_numeric = (float(entry_price_min) + float(entry_price_max)) / 2
elif entry_price_str:
    # Fallback: extract from string
    ...
```

## Verification Results

### Test Cases

1. **RSI 77.1 (Overbought) with MTF STRONG_BUY:**
   - ✅ Result: "⏳ WAIT (RSI >70)" ✓

2. **RSI 94.9 (Extremely Overbought) with MTF STRONG_BUY:**
   - ✅ Result: "⏳ WAIT (RSI >80)" ✓

3. **RSI 77.1 with MTF BUY_THE_DIP:**
   - ✅ Result: "✅ BUY DIP" ✓ (Correct - designed for pullbacks)

4. **RSI 18.5 (Extremely Oversold):**
   - ✅ Result: "STRONG BUY" ✓ (Enhanced signal)

5. **RSI 28.2 (Oversold):**
   - ✅ Result: "BUY" ✓

## Table Column Accuracy

All columns now use consistent data sources:

| Column | Data Source | Status |
|--------|-------------|--------|
| Rank | Calculated from sorted results | ✅ |
| Symbol | From scan results | ✅ |
| Name | From database | ✅ |
| Sector | From database | ✅ |
| Priority | From scan results | ✅ |
| RSI | From technical_signals | ✅ |
| Signals | From triggered_alerts | ✅ |
| **Recommendation** | **Generated with RSI alignment** | ✅ **FIXED** |
| Div Yield | From dividend_yield_cache or calculated | ✅ |
| **Entry Price** | **From stored entry_price_min/max** | ✅ **FIXED** |
| **Profit Target** | **Calculated using stored entry prices** | ✅ **FIXED** |
| Gain % | Calculated from entry/target | ✅ |
| Position | From PositionSizer | ✅ |
| Profit Timeline | Calculated from RSI/signals | ✅ |
| Price | From current_price | ✅ |
| Change | From change_pct | ✅ |

## Expected Behavior

### Recommendations by RSI Level

- **RSI <20 (Extremely Oversold):** STRONG BUY
- **RSI 20-30 (Oversold):** BUY
- **RSI 30-70 (Neutral):** BUY/NEUTRAL based on other signals
- **RSI 70-80 (Overbought):** WAIT (unless BUY_THE_DIP signal)
- **RSI >80 (Extremely Overbought):** WAIT or SELL

### Multi-Timeframe Signals

- **BUY_THE_DIP:** Always shows (designed for overbought pullbacks)
- **STRONG_BUY with RSI >70:** Shows "WAIT (RSI >70)"
- **STRONG_BUY with RSI >80:** Shows "WAIT (RSI >80)"

## Files Modified

1. `tradingagents/utils/cli_formatter.py`
   - Enhanced `_generate_recommendation()` with RSI overbought checks
   - Updated entry price display to use stored values
   - Updated profit target calculation to use stored entry prices

## Testing

Run screener to verify:
```bash
./quick_run.sh screener
```

Check that:
1. Stocks with RSI >70 show WAIT (unless BUY_THE_DIP)
2. Entry prices match stored values from database
3. Profit targets are calculated correctly from stored entry prices
4. Recommendations align with RSI values

