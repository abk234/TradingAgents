# Strategy System Quick Start Guide

**Date:** November 17, 2025  
**Purpose:** Quick reference for using the new multi-strategy system

---

## 🚀 Quick Start

### Basic Usage: Single Strategy

```python
from tradingagents.strategies import ValueStrategy, StrategyDataCollector

# Step 1: Collect data
collector = StrategyDataCollector()
data = collector.collect_all_data("AAPL", "2024-11-17")

# Step 2: Run strategy
strategy = ValueStrategy()
result = strategy.evaluate(
    ticker="AAPL",
    market_data=data["market_data"],
    fundamental_data=data["fundamental_data"],
    technical_data=data["technical_data"],
)

# Step 3: View results
print(f"Recommendation: {result.recommendation.value}")
print(f"Confidence: {result.confidence}%")
print(f"Reasoning: {result.reasoning}")
print(f"Target Price: ${result.target_price:.2f}" if result.target_price else "N/A")
```

---

## 🔄 Strategy Comparison

### Compare Multiple Strategies

```python
from tradingagents.strategies import (
    StrategyComparator,
    ValueStrategy,
    GrowthStrategy,
    DividendStrategy,
    MomentumStrategy,
    StrategyDataCollector
)

# Collect data once
collector = StrategyDataCollector()
data = collector.collect_all_data("AAPL", "2024-11-17")

# Create comparator with multiple strategies
comparator = StrategyComparator([
    ValueStrategy(),
    GrowthStrategy(),
    DividendStrategy(),
    MomentumStrategy(),
])

# Compare all strategies
comparison = comparator.compare(
    ticker="AAPL",
    market_data=data["market_data"],
    fundamental_data=data["fundamental_data"],
    technical_data=data["technical_data"],
    additional_data={
        "dividend_data": data["dividend_data"],
        "news_data": data["news_data"],
    }
)

# View consensus
print(f"Consensus Recommendation: {comparison['consensus']['recommendation']}")
print(f"Agreement Level: {comparison['consensus']['agreement_level']}%")
print(f"BUY votes: {comparison['consensus']['buy_count']}")
print(f"SELL votes: {comparison['consensus']['sell_count']}")

# View individual strategy results
for strategy_name, result in comparison['strategies'].items():
    print(f"\n{strategy_name}:")
    print(f"  Recommendation: {result['recommendation']}")
    print(f"  Confidence: {result['confidence']}%")
    print(f"  Reasoning: {result['reasoning']}")

# View insights
print("\nInsights:")
for insight in comparison['insights']:
    print(f"  - {insight}")
```

---

## 📊 Available Strategies

### 1. Value Strategy
```python
from tradingagents.strategies import ValueStrategy

strategy = ValueStrategy()
# Focus: Intrinsic value, margin of safety, economic moat
# Timeframe: 5-10 years
```

### 2. Growth Strategy
```python
from tradingagents.strategies import GrowthStrategy

strategy = GrowthStrategy()
# Focus: Revenue/earnings growth, PEG ratio
# Timeframe: 1-5 years
```

### 3. Dividend Strategy
```python
from tradingagents.strategies import DividendStrategy

strategy = DividendStrategy()
# Focus: Dividend yield, safety, growth
# Timeframe: 5+ years
```

### 4. Momentum Strategy
```python
from tradingagents.strategies import MomentumStrategy

strategy = MomentumStrategy()
# Focus: Price trends, technical indicators
# Timeframe: 30-90 days
```

### 5. Contrarian Strategy
```python
from tradingagents.strategies import ContrarianStrategy

strategy = ContrarianStrategy()
# Focus: Oversold conditions, negative sentiment
# Timeframe: Months to years
```

### 6. Quantitative Strategy
```python
from tradingagents.strategies import QuantitativeStrategy

strategy = QuantitativeStrategy()
# Focus: Factor-based scoring (value, momentum, quality, size)
# Timeframe: Weeks to months
```

### 7. Sector Rotation Strategy
```python
from tradingagents.strategies import SectorRotationStrategy

strategy = SectorRotationStrategy()
# Focus: Sector strength, economic cycle alignment
# Timeframe: Months to years
```

---

## 🔌 Integration with Existing System

### Option 1: Use New Strategies Only
```python
# Use new strategy system independently
from tradingagents.strategies import ValueStrategy, StrategyDataCollector

collector = StrategyDataCollector()
data = collector.collect_all_data("AAPL")
strategy = ValueStrategy()
result = strategy.evaluate(...)
```

### Option 2: Use Existing System Only (Unchanged)
```python
# Existing system works exactly as before
from tradingagents.graph.trading_graph import TradingAgentsGraph

ta = TradingAgentsGraph()
_, decision = ta.propagate("AAPL", "2024-11-17")
# No changes to existing code
```

### Option 3: Use Both Systems (Future)
```python
# Integration layer (to be implemented in Phase 5)
from tradingagents.integration import ComparisonRunner

runner = ComparisonRunner()
comparison = runner.compare_both_systems("AAPL", "2024-11-17")
```

---

## 📋 Strategy Result Format

All strategies return `StrategyResult` with:

```python
result = {
    "recommendation": Recommendation.BUY,  # BUY/SELL/HOLD/WAIT
    "confidence": 75,  # 0-100
    "reasoning": "Strong margin of safety, good fundamentals...",
    "entry_price": 175.50,
    "target_price": 220.00,
    "stop_loss": 165.00,  # Optional
    "holding_period": "5-10 years",
    "key_metrics": {
        "pe_ratio": 28.5,
        "margin_of_safety": 20.5,
        # ... strategy-specific metrics
    },
    "risks": [
        "High P/E ratio suggests overvaluation",
        # ... identified risks
    ],
    "strategy_name": "Value Investing"
}
```

---

## 🎯 Common Use Cases

### Use Case 1: Validate Recommendation
```python
# Run multiple strategies to validate a recommendation
comparator = StrategyComparator([
    ValueStrategy(),
    GrowthStrategy(),
    MomentumStrategy(),
])

comparison = comparator.compare(...)

if comparison['consensus']['agreement_level'] >= 80:
    print("Strong consensus - high confidence")
elif comparison['consensus']['agreement_level'] >= 60:
    print("Moderate consensus - medium confidence")
else:
    print("Mixed signals - investigate further")
```

### Use Case 2: Find Best Strategy for Stock
```python
# Run all strategies and see which recommends BUY
comparator = StrategyComparator([
    ValueStrategy(),
    GrowthStrategy(),
    DividendStrategy(),
    MomentumStrategy(),
    ContrarianStrategy(),
    QuantitativeStrategy(),
    SectorRotationStrategy(),
])

comparison = comparator.compare(...)

# Find strategies that recommend BUY
buy_strategies = [
    name for name, result in comparison['strategies'].items()
    if result['recommendation'] == 'BUY'
]

print(f"Strategies recommending BUY: {', '.join(buy_strategies)}")
```

### Use Case 3: Compare Strategy Perspectives
```python
# See how different strategies view the same stock
comparison = comparator.compare(...)

for strategy_name, result in comparison['strategies'].items():
    print(f"\n{strategy_name}:")
    print(f"  View: {result['recommendation']}")
    print(f"  Key Metrics: {result['key_metrics']}")
    print(f"  Risks: {result['risks']}")
```

---

## ⚠️ Important Notes

### Data Requirements
- Strategies require market, fundamental, and technical data
- Some strategies need additional data (dividend, news, sector)
- Missing data is handled gracefully (returns WAIT recommendation)

### Backward Compatibility
- ✅ Existing system unchanged
- ✅ New system is separate module
- ✅ Both can coexist
- ✅ No breaking changes

### Performance
- Data collection may take a few seconds (reuses existing APIs)
- Strategy evaluation is fast (<1 second per strategy)
- Comparison of 7 strategies takes ~5-10 seconds total

---

## 🐛 Troubleshooting

### Import Errors
```python
# If strategy import fails, check dependencies
from tradingagents.strategies import ValueStrategy
# Should work if base module is installed
```

### Data Collection Errors
```python
# If data collection fails, check:
# 1. API keys configured (if needed)
# 2. Network connection
# 3. Ticker symbol valid

try:
    data = collector.collect_all_data("AAPL")
except Exception as e:
    print(f"Error: {e}")
```

### Strategy Evaluation Errors
```python
# Strategies handle missing data gracefully
# Returns WAIT recommendation with low confidence
result = strategy.evaluate(...)
if result.confidence == 0:
    print("Insufficient data for analysis")
```

---

## 📚 Next Steps

1. **Test Strategies:** Run each strategy on different stocks
2. **Compare Results:** Use comparator to see strategy differences
3. **Integrate:** Add to your workflow (when ready)
4. **Customize:** Modify strategy logic for your needs

---

**For detailed documentation, see:**
- `STRATEGY_IMPLEMENTATION_PLAN.md` - Full implementation plan
- `STRATEGY_IMPLEMENTATION_STATUS.md` - Current status
- `MULTI_STRATEGY_ANALYSIS.md` - Strategy analysis

