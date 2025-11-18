# Quick Start Guide - Analyzing Stocks with Profitability Features

**Status:** ✅ **All Profitability Features Are Now ENABLED by Default!**

---

## ✅ Feature Status Confirmation

**All features are ENABLED and ready to use!**

- ✅ Dynamic gate thresholds (confidence + market regime)
- ✅ Enhanced position sizing (up to 12% for high confidence)
- ✅ Trailing stop losses
- ✅ Partial profit taking
- ✅ Earnings proximity checks
- ✅ Market regime detection
- ✅ Sector rotation detection
- ✅ Correlation risk management

**Default Configuration:**
- `enable_profitability_features`: **True** ✅
- `portfolio_value`: **100000** (adjust to your portfolio)
- All sub-features: **Enabled**

---

## 🚀 How to Start Analyzing Stocks

### Method 1: Using main.py (Simplest)

```bash
# Edit portfolio value in main.py if needed, then:
python main.py
```

This will analyze NVDA with all profitability features enabled.

**To analyze a different stock:**
Edit `main.py` and change:
```python
_, decision = ta.propagate("AAPL", "2024-05-10", store_analysis=True)  # Change "NVDA" to any ticker
```

---

### Method 2: Using the CLI (Interactive)

```bash
python -m cli.main analyze
```

Or:
```bash
python run.py
```

**Features are automatically enabled** - you'll see profitability enhancements in the output.

---

### Method 3: Using the Screener (Recommended Daily Workflow)

```bash
# Step 1: Run daily screener (finds opportunities)
python -m tradingagents.screener run

# Step 2: View top opportunities
python -m tradingagents.screener top 5

# Step 3: Analyze top pick (profitability features automatically applied)
python -m tradingagents.analyze AAPL --portfolio-value 100000
```

**Note:** Earnings proximity check is automatic - stocks near earnings are skipped.

---

### Method 4: Programmatic Usage (Python Script)

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from datetime import date

# Config already has profitability features enabled!
config = DEFAULT_CONFIG.copy()
config["portfolio_value"] = 100000  # Adjust to your portfolio

# Initialize
ta = TradingAgentsGraph(debug=True, config=config)

# Analyze a stock
ticker = "AAPL"
analysis_date = date.today().strftime("%Y-%m-%d")

final_state, decision = ta.propagate(ticker, analysis_date, store_analysis=True)

# Print decision
print(f"\nDecision for {ticker}: {decision}")

# Access profitability enhancements
if "profitability_enhancements" in final_state:
    enhancements = final_state["profitability_enhancements"]
    
    print("\n" + "="*70)
    print("PROFITABILITY ENHANCEMENTS")
    print("="*70)
    
    if enhancements.get('market_regime'):
        print(f"Market Regime: {enhancements['market_regime']}")
        print(f"Volatility Regime: {enhancements['volatility_regime']}")
    
    if enhancements.get('sector_action'):
        print(f"Sector Action: {enhancements['sector_action']}")
    
    if enhancements.get('correlation_risk'):
        corr = enhancements['correlation_risk']
        print(f"Correlation Risk: {corr['max_correlation']:.2f} ({'✓ Safe' if corr['is_safe'] else '⚠ High'})")
    
    if enhancements.get('position_sizing'):
        sizing = enhancements['position_sizing']
        print(f"\nPosition Sizing:")
        print(f"  Recommended: {sizing['position_size_pct']:.1f}% of portfolio")
        print(f"  Amount: ${sizing['recommended_amount']:,.2f}")
        print(f"  Shares: {sizing['recommended_shares']}")
        print(f"  Reasoning: {sizing['sizing_reasoning']}")
    
    if enhancements.get('exit_strategy'):
        exit_strat = enhancements['exit_strategy']
        print(f"\nExit Strategy:")
        print(f"  Trailing Stop: ${exit_strat['trailing_stop']:.2f}")
        print(f"  Partial Profit Levels:")
        for level, info in exit_strat['partial_profit_levels'].items():
            print(f"    {level}: Sell {info['sell_pct']*100}% - {info['reasoning']}")
```

---

## 📊 Example: Complete Analysis Workflow

### Daily Routine

```bash
# Morning: Run screener
python -m tradingagents.screener run

# Review top opportunities
python -m tradingagents.screener top 5

# Analyze top pick with profitability features
python -m tradingagents.analyze AAPL --portfolio-value 100000 --plain-english

# Check profitability enhancements in output
```

### Analyzing Multiple Stocks

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from datetime import date

config = DEFAULT_CONFIG.copy()
config["portfolio_value"] = 100000

ta = TradingAgentsGraph(debug=False, config=config)

tickers = ["AAPL", "MSFT", "GOOGL", "NVDA", "AMZN"]

for ticker in tickers:
    print(f"\n{'='*70}")
    print(f"Analyzing {ticker}")
    print('='*70)
    
    final_state, decision = ta.propagate(ticker, date.today().strftime("%Y-%m-%d"))
    
    print(f"Decision: {decision}")
    
    # Show profitability enhancements
    if "profitability_enhancements" in final_state:
        enhancements = final_state["profitability_enhancements"]
        if enhancements.get('position_sizing'):
            print(f"Position: {enhancements['position_sizing']['position_size_pct']:.1f}%")
```

---

## 🎯 What You'll See

When analyzing stocks, you'll now get:

1. **Market Regime Context:**
   - Bull/Bear/Neutral market detection
   - High/Low/Normal volatility detection
   - Adjusted gate thresholds automatically

2. **Sector Recommendations:**
   - OVERWEIGHT/UNDERWEIGHT/NEUTRAL for each sector
   - Top sectors by momentum

3. **Position Sizing:**
   - Confidence-based sizing (up to 12% for very high confidence)
   - Gate score adjustments
   - Timing gate impact

4. **Risk Management:**
   - Correlation checks with existing holdings
   - Diversification scoring
   - Position size adjustments for correlation

5. **Exit Strategy:**
   - Trailing stop recommendations
   - Partial profit levels (5%, 10%, 15%)

6. **Earnings Avoidance:**
   - Automatic skip of stocks near earnings (7 days before to 3 days after)

---

## ⚙️ Adjusting Settings

### Change Portfolio Value

Edit `tradingagents/default_config.py`:
```python
"portfolio_value": 50000,  # Change to your portfolio value
```

Or override in your script:
```python
config["portfolio_value"] = 50000
```

### Disable Specific Features

```python
config["enable_regime_detection"] = False  # Disable market regime
config["enable_sector_rotation"] = False   # Disable sector rotation
config["enable_correlation_check"] = False  # Disable correlation checks
```

### Disable All Profitability Features

```python
config["enable_profitability_features"] = False
```

---

## 🧪 Testing the Features

Run the test suite to verify everything works:

```bash
python test_profitability_features.py
```

Expected output:
```
✅ Dynamic thresholds test PASSED
✅ Position sizing test PASSED
✅ Sector rotation test PASSED
✅ Correlation management test PASSED
✅ Earnings check test PASSED
✅ Integration test PASSED
```

---

## 📈 Monitoring Performance

Generate performance reports:

```bash
python monitor_profitability_performance.py
```

This shows:
- Win rate by confidence level
- Sector rotation accuracy
- Recommendations for improvement

---

## 🎓 Quick Examples

### Example 1: Analyze Single Stock

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

config = DEFAULT_CONFIG.copy()
ta = TradingAgentsGraph(config=config)

final_state, decision = ta.propagate("AAPL", "2024-11-17", store_analysis=True)
print(decision)
```

### Example 2: Get Position Sizing

```python
# After analysis, access enhancements
enhancements = final_state.get("profitability_enhancements", {})
if enhancements.get('position_sizing'):
    sizing = enhancements['position_sizing']
    print(f"Invest ${sizing['recommended_amount']:,.2f}")
    print(f"Buy {sizing['recommended_shares']} shares")
```

### Example 3: Check Sector Rotation

```python
from tradingagents.decision.sector_rotation import SectorRotationDetector

detector = SectorRotationDetector()
actions = detector.detect_sector_rotation()

for sector, action in actions.items():
    if action != 'NEUTRAL':
        print(f"{sector}: {action}")
```

---

## ✅ Summary

**All features are ENABLED and ready!**

1. **Features Status:** ✅ All enabled by default
2. **Portfolio Value:** Set to $100,000 (adjust in config)
3. **How to Analyze:** Use any method above - features are automatic
4. **What You Get:** Enhanced decisions with profitability improvements

**Start analyzing now:**
```bash
python main.py  # Quick test
# OR
python -m cli.main analyze  # Interactive
# OR
python -m tradingagents.screener run  # Find opportunities first
```

---

**Last Updated:** November 17, 2025

