# ✅ Screener Improvements Applied

## 🎯 Changes Made

### 1. **Default Results Increased: 5 → 20**
- Changed default `--top` from 5 to **20**
- Now shows 20 results by default instead of 5
- You can still override with `--top N` if needed

### 2. **Signals Display Fixed**
- Fixed signals column to show `triggered_alerts` (was looking for wrong field)
- Now shows **first 3 signals** instead of 2 (better visibility)
- Shows "+X more" if there are additional signals

---

## 🚀 Usage

### Default (Shows 20 results):
```bash
./run_screener.sh run
```

### Custom number:
```bash
./run_screener.sh run --top 30  # Show top 30
./run_screener.sh run --top 50  # Show top 50
```

### With sector analysis:
```bash
./run_screener.sh run --sector-analysis --top 20
```

---

## 📊 What You'll See Now

### Signals Column:
- **Before**: "None" or empty
- **After**: Shows actual signals like:
  - "RSI_OVERSOLD, MACD_BULLISH_CROSS, VOLUME_SPIKE"
  - "RSI_OVERSOLD, MACD_BULLISH_CROSS +2 more" (if 5 total)

### Results Count:
- **Before**: 5 results
- **After**: 20 results (default)

---

## ✅ Test It

Run:
```bash
./run_screener.sh run
```

You should now see:
- ✅ 20 results instead of 5
- ✅ Signals displayed in the "Signals" column
- ✅ All triggered alerts visible

---

**The screener now shows 20 results with signals displayed!** 🎉

