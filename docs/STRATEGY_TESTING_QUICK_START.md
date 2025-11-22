# Strategy Testing - Quick Start Guide

**How to test all strategies in your TradingAgents application**

---

## ✅ Available Strategies (8 Total)

1. **Value Investing** (`value`) - Buffett-style value investing
2. **Growth Investing** (`growth`) - Growth at reasonable price (GARP)
3. **Dividend Investing** (`dividend`) - Income-focused investing
4. **Momentum Trading** (`momentum`) - Technical momentum trading
5. **Contrarian Investing** (`contrarian`) - Buy when others fear
6. **Quantitative Investing** (`quantitative`) - Factor-based systematic
7. **Sector Rotation** (`sector_rotation`) - Economic cycle-based
8. **Market Structure and Cloud Trend** (`market_structure`) - Market Structure & Cloud Trend

---

## 🚀 Quick Commands

### Method 1: Using Quick Run Script (Recommended)

```bash
# List all strategies
./quick_run.sh strategy-list

# Compare all strategies on one stock
./quick_run.sh strategies AAPL

# Run single strategy
./quick_run.sh strategy-run value AAPL
./quick_run.sh strategy-run market_structure AAPL

# Compare strategies across multiple stocks
./quick_run.sh strategy-multi AAPL MSFT GOOGL

# Test on top screener stocks
./quick_run.sh strategy-screener 20
```

### Method 2: Using Python CLI

```bash
# List all strategies
python -m tradingagents.strategies list

# Compare all strategies
python -m tradingagents.strategies compare AAPL

# Compare specific strategies
python -m tradingagents.strategies compare AAPL --strategies value growth market_structure

# Run single strategy
python -m tradingagents.strategies run value AAPL
python -m tradingagents.strategies run market_structure AAPL
```

### Method 3: Test All Strategies One After Another

```bash
# Using the test script
python test_strategies_quick.py AAPL

# Or using the shell script
./test_all_strategies.sh AAPL
```

---

## 📋 Example: Testing All Strategies

### Quick Test (All at Once)
```bash
./quick_run.sh strategies AAPL
```

This will:
- Collect data once
- Run all 8 strategies
- Show consensus recommendation
- Display individual strategy results

### Sequential Test (One After Another)
```bash
python test_strategies_quick.py AAPL
```

This will:
- Test each strategy one by one
- Show detailed results for each
- Provide a summary at the end

---

## 🎯 What You'll See

### Comparison Output
```
Strategy Comparison Results: AAPL
======================================================================

📊 Consensus:
   Recommendation: BUY
   Agreement Level: 62.5%
   Votes: BUY=5, SELL=0, HOLD=1, WAIT=2

📈 Strategy Results:

   Value Investing:
      Recommendation: BUY
      Confidence: 75%
      Reasoning: Stock is undervalued...

   Growth Investing:
      Recommendation: BUY
      Confidence: 80%
      Reasoning: Strong growth prospects...

   Market Structure and Cloud Trend:
      Recommendation: WAIT
      Confidence: 45%
      Reasoning: No clear structure break...
```

---

## 💡 Tips

1. **Start with Comparison:** Use `./quick_run.sh strategies AAPL` to see all strategies at once
2. **Test Sequentially:** Use `python test_strategies_quick.py AAPL` to see each strategy in detail
3. **Include Market Structure and Cloud Trend:** The strategy is automatically included in comparisons
4. **Multiple Stocks:** Test on different stocks to see strategy consistency
5. **Screener Integration:** Test on top screener stocks for best opportunities

---

## 📚 More Information

- **Full Guide:** `docs/HOW_TO_TEST_STRATEGIES.md`
- **Strategy Details:** `docs/AI_PINE_SCRIPT_STRATEGY.md` (historical reference)
- **Quick Reference:** `docs/STRATEGY_TESTING_QUICK_REFERENCE.md`

---

**Quick Start:** Just run `./quick_run.sh strategies AAPL` to test all strategies!

