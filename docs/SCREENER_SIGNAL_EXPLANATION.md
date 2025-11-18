# Screener Signal Explanation

**Understanding why stocks with bearish signals may still appear in screener results**

**Last Updated:** 2025-11-17

---

## The Issue: UPS with MACD_BEARISH_CROSS

You're absolutely right to question why UPS (with MACD_BEARISH_CROSS and 43% priority) appears in screener results. This is a valid concern!

---

## How Priority Scoring Works

The priority score is calculated from **4 components**:

```
Priority Score = (Technical × 40%) + (Fundamental × 25%) + (Volume × 20%) + (Momentum × 15%)
```

### Why UPS Could Score 43% Despite Bearish Signal

**UPS Example:**
- **MACD_BEARISH_CROSS:** -15 points (technical penalty) ✅ **NOW FIXED**
- **But other factors:**
  - Strong fundamentals (good P/E, growth) = +25 points
  - High volume = +20 points  
  - Positive momentum = +15 points
  - Other technical positives = +10 points
- **Total:** Could still reach 43% even with bearish MACD

**However:** This is problematic because:
1. Bearish MACD suggests downward momentum
2. Should reduce priority significantly
3. May not be a good buy opportunity

---

## Signal Interpretation

### Bullish Signals (Add Points)
- ✅ **MACD_BULLISH_CROSS:** +15 points
- ✅ **RSI_OVERSOLD:** +15 points (buying opportunity)
- ✅ **BB_LOWER_TOUCH:** +10 points (support level)
- ✅ **VOLUME_SPIKE:** +10-20 points

### Bearish Signals (Penalize Points) - **NOW FIXED**
- ❌ **MACD_BEARISH_CROSS:** -15 points (was 0, now penalized)
- ❌ **RSI_OVERBOUGHT:** -10 points (was 0, now penalized)
- ❌ **BB_UPPER_TOUCH:** -5 points (was 0, now penalized)
- ❌ **Price below MA50:** -10 points (was 0, now penalized)

---

## What Changed (Fix Applied)

### Before (Bug):
```python
# Only added points for bullish signals
if signals.get('macd_bullish_crossover'):
    score += 15
# Bearish signals were ignored in scoring!
```

### After (Fixed):
```python
# Adds points for bullish
if signals.get('macd_bullish_crossover'):
    score += 15
# NOW PENALIZES bearish signals
elif signals.get('macd_bearish_crossover'):
    score -= 15  # Reduces priority score
```

---

## How to Use Screener Results

### ✅ Good Buy Candidates:
- **Priority Score:** 50-100
- **Signals:** MACD_BULLISH_CROSS, RSI_OVERSOLD, BB_LOWER_TOUCH
- **No bearish signals**

### ⚠️  Caution Required:
- **Priority Score:** 40-49
- **Mixed signals:** Some bullish, some bearish
- **Action:** Investigate further before buying

### ❌ Avoid (After Fix):
- **Priority Score:** < 40
- **Bearish signals:** MACD_BEARISH_CROSS, RSI_OVERBOUGHT
- **Action:** Wait for better entry or avoid

---

## Updated Recommendation Logic

### For UPS Specifically:

**Before Fix:**
- MACD_BEARISH_CROSS (ignored)
- Score: 43% (from other factors)
- **Problem:** Bearish signal not penalized

**After Fix:**
- MACD_BEARISH_CROSS: -15 points penalty
- Score: ~28-33% (reduced by bearish signal)
- **Result:** Lower priority, less likely to be recommended

---

## Best Practice: Always Check Signals

Even with the fix, **always review signals** before buying:

### ✅ Good Setup:
```
Priority: 65%
Signals: MACD_BULLISH_CROSS, RSI_OVERSOLD, BB_LOWER_TOUCH
→ Strong buy candidate
```

### ⚠️  Mixed Signals:
```
Priority: 45%
Signals: MACD_BEARISH_CROSS, VOLUME_SPIKE
→ Caution: Bearish MACD suggests wait
```

### ❌ Poor Setup:
```
Priority: 30%
Signals: MACD_BEARISH_CROSS, RSI_OVERBOUGHT, BB_UPPER_TOUCH
→ Avoid: Multiple bearish signals
```

---

## Using Eddie for Validation

After screener, **always validate with Eddie:**

```
Ask Eddie: "Should I buy UPS?"
```

Eddie will:
1. Run full analysis
2. Check all signals
3. Warn about bearish MACD
4. Provide proper recommendation (likely WAIT or PASS)

---

## Summary

**The Fix:**
- ✅ Bearish MACD now reduces priority score (-15 points)
- ✅ RSI overbought penalized (-10 points)
- ✅ Other bearish signals penalized
- ✅ Stocks with bearish signals will score lower

**Result:**
- Stocks like UPS with MACD_BEARISH_CROSS will score lower
- Less likely to appear in top recommendations
- Better filtering of poor opportunities

**Your Question Was Valid:** Bearish signals should reduce priority, and now they do!

---

**Next Steps:**
1. Re-run screener to see updated scores
2. Bearish stocks should score lower
3. Focus on stocks with bullish signals only

