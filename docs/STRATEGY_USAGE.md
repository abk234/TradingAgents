# Strategy System Usage Guide

**Date:** November 17, 2025  
**Purpose:** Complete usage guide for the multi-strategy system

---

## 🚀 Quick Start

### Command Line Usage

```bash
# Compare all strategies on a stock
python -m tradingagents.strategies compare AAPL

# Compare specific strategies
python -m tradingagents.strategies compare AAPL --strategies value growth dividend

# Run a single strategy
python -m tradingagents.strategies run value AAPL

# List available strategies
python -m tradingagents.strategies list

# Compare with existing TradingAgents system
python -m tradingagents.strategies compare-with-existing AAPL

# Output JSON format
python -m tradingagents.strategies compare AAPL --json
```

---

## 📚 Python API Usage

### Example 1: Single Strategy

```python
from tradingagents.strategies import ValueStrategy, StrategyDataCollector

# Collect data
collector = StrategyDataCollector()
data = collector.collect_all_data("AAPL", "2024-11-17")

# Run strategy
strategy = ValueStrategy()
result = strategy.evaluate(
    ticker="AAPL",
    market_data=data["market_data"],
    fundamental_data=data["fundamental_data"],
    technical_data=data["technical_data"],
)

print(f"Recommendation: {result.recommendation.value}")
print(f"Confidence: {result.confidence}%")
print(f"Reasoning: {result.reasoning}")
```

### Example 2: Strategy Comparison

```python
from tradingagents.strategies import (
    StrategyComparator,
    ValueStrategy,
    GrowthStrategy,
    DividendStrategy,
    MomentumStrategy,
    StrategyDataCollector
)

# Collect data
collector = StrategyDataCollector()
data = collector.collect_all_data("AAPL", "2024-11-17")

# Create comparator
comparator = StrategyComparator([
    ValueStrategy(),
    GrowthStrategy(),
    DividendStrategy(),
    MomentumStrategy(),
])

# Compare
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

# View results
print(f"Consensus: {comparison['consensus']['recommendation']}")
print(f"Agreement: {comparison['consensus']['agreement_level']}%")
```

### Example 3: Compare with Existing System

```python
from tradingagents.integration import ComparisonRunner

# Create runner (includes existing system)
runner = ComparisonRunner(include_existing=True)

# Compare both systems
comparison = runner.compare_both_systems("AAPL", "2024-11-17")

# View results
for strategy_name, result in comparison['strategies'].items():
    print(f"{strategy_name}: {result['recommendation']} ({result['confidence']}%)")
```

---

## 📊 Available Strategies

### 1. Value Strategy
```python
from tradingagents.strategies import ValueStrategy

strategy = ValueStrategy()
# Focus: Intrinsic value, margin of safety, economic moat
# Timeframe: 5-10 years
# Best for: Long-term value investors
```

### 2. Growth Strategy
```python
from tradingagents.strategies import GrowthStrategy

strategy = GrowthStrategy()
# Focus: Revenue/earnings growth, PEG ratio
# Timeframe: 1-5 years
# Best for: Growth-oriented investors
```

### 3. Dividend Strategy
```python
from tradingagents.strategies import DividendStrategy

strategy = DividendStrategy()
# Focus: Dividend yield, safety, growth
# Timeframe: 5+ years
# Best for: Income-focused investors
```

### 4. Momentum Strategy
```python
from tradingagents.strategies import MomentumStrategy

strategy = MomentumStrategy()
# Focus: Price trends, technical indicators
# Timeframe: 30-90 days
# Best for: Active traders
```

### 5. Contrarian Strategy
```python
from tradingagents.strategies import ContrarianStrategy

strategy = ContrarianStrategy()
# Focus: Oversold conditions, negative sentiment
# Timeframe: Months to years
# Best for: Contrarian investors
```

### 6. Quantitative Strategy
```python
from tradingagents.strategies import QuantitativeStrategy

strategy = QuantitativeStrategy()
# Focus: Factor-based scoring
# Timeframe: Weeks to months
# Best for: Systematic investors
```

### 7. Sector Rotation Strategy
```python
from tradingagents.strategies import SectorRotationStrategy

strategy = SectorRotationStrategy()
# Focus: Sector strength, economic cycle
# Timeframe: Months to years
# Best for: Macro-oriented investors
```

---

## 🔌 Integration Options

### Option 1: Use New Strategies Only

```python
# Independent usage - doesn't require existing system
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
# No changes needed
```

### Option 3: Use Both Systems

```python
# Compare both systems
from tradingagents.integration import ComparisonRunner

runner = ComparisonRunner(include_existing=True)
comparison = runner.compare_both_systems("AAPL", "2024-11-17")
```

---

## 📋 Output Formats

### StrategyResult Format

```python
result = StrategyResult(
    recommendation=Recommendation.BUY,  # BUY/SELL/HOLD/WAIT
    confidence=75,  # 0-100
    reasoning="Strong margin of safety, good fundamentals...",
    entry_price=175.50,
    target_price=220.00,
    stop_loss=165.00,  # Optional
    holding_period="5-10 years",
    key_metrics={
        "pe_ratio": 28.5,
        "margin_of_safety": 20.5,
        # ... strategy-specific metrics
    },
    risks=[
        "High P/E ratio suggests overvaluation",
        # ... identified risks
    ],
    strategy_name="Value Investing"
)
```

### Comparison Result Format

```python
comparison = {
    "ticker": "AAPL",
    "strategies": {
        "Value Investing": {
            "recommendation": "BUY",
            "confidence": 78,
            "reasoning": "...",
            # ... full StrategyResult as dict
        },
        # ... other strategies
    },
    "consensus": {
        "recommendation": "BUY",
        "agreement_level": 80.0,
        "buy_count": 4,
        "sell_count": 0,
        "hold_count": 1,
        "wait_count": 0,
        "total_strategies": 5,
    },
    "divergences": [
        {
            "recommendation": "HOLD",
            "strategies": ["Dividend Investing"],
            "count": 1,
        }
    ],
    "insights": [
        "Strong consensus: 4 of 5 strategies recommend BUY",
        "Value strategy sees 20.5% margin of safety",
        # ... more insights
    ],
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
    print("✅ Strong consensus - high confidence")
elif comparison['consensus']['agreement_level'] >= 60:
    print("⚠️ Moderate consensus - medium confidence")
else:
    print("❌ Mixed signals - investigate further")
```

### Use Case 2: Find Best Strategy for Stock

```python
# Run all strategies and see which recommends BUY
comparison = comparator.compare(...)

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

### Use Case 4: Compare with Existing System

```python
# See how new strategies compare to existing system
runner = ComparisonRunner(include_existing=True)
comparison = runner.compare_both_systems("AAPL", "2024-11-17")

# Find if existing system agrees with new strategies
existing_result = comparison['strategies'].get('Hybrid (Four-Gate + Multi-Agent)')
new_strategies_results = {
    k: v for k, v in comparison['strategies'].items()
    if k != 'Hybrid (Four-Gate + Multi-Agent)'
}

# Check agreement
if existing_result:
    existing_rec = existing_result['recommendation']
    new_consensus = comparison['consensus']['recommendation']
    
    if existing_rec == new_consensus:
        print(f"✅ Existing system agrees with new strategies: {existing_rec}")
    else:
        print(f"⚠️ Existing system ({existing_rec}) differs from new strategies ({new_consensus})")
```

---

## ⚙️ Configuration

### Custom Strategy Selection

```python
# Use only specific strategies
comparator = StrategyComparator([
    ValueStrategy(),
    GrowthStrategy(),
    # Skip others
])
```

### Custom Data Collection

```python
# Use custom config for data collection
from tradingagents.default_config import DEFAULT_CONFIG

config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "ollama"

collector = StrategyDataCollector(config=config)
```

### Integration Configuration

```python
# Configure integration runner
from tradingagents.integration import ComparisonRunner
from tradingagents.default_config import DEFAULT_CONFIG

config = DEFAULT_CONFIG.copy()
runner = ComparisonRunner(
    include_existing=True,
    strategies=None,  # Use all strategies
    config=config
)
```

---

## 🐛 Troubleshooting

### Import Errors

```python
# If strategy import fails, check dependencies
try:
    from tradingagents.strategies import ValueStrategy
except ImportError as e:
    print(f"Import error: {e}")
    # Check that base module is installed
```

### Data Collection Errors

```python
# If data collection fails
try:
    data = collector.collect_all_data("AAPL")
except Exception as e:
    print(f"Error: {e}")
    # Check:
    # 1. API keys configured (if needed)
    # 2. Network connection
    # 3. Ticker symbol valid
```

### Strategy Evaluation Errors

```python
# Strategies handle missing data gracefully
result = strategy.evaluate(...)
if result.confidence == 0:
    print("Insufficient data for analysis")
    print(f"Reasoning: {result.reasoning}")
```

---

## 📝 Notes

### Performance
- Data collection: 3-10 seconds (depends on APIs)
- Strategy evaluation: <1 second per strategy
- Comparison of 7 strategies: ~5-10 seconds total
- Existing system comparison: 30-90 seconds (full multi-agent analysis)

### Data Requirements
- Market data: Required for all strategies
- Fundamental data: Required for value, growth, dividend strategies
- Technical data: Required for momentum, contrarian strategies
- Additional data: Dividend data for dividend strategy, news for contrarian

### Backward Compatibility
- ✅ Existing system unchanged
- ✅ New system is separate module
- ✅ Both can coexist
- ✅ No breaking changes

---

## 📚 Additional Resources

- `STRATEGY_QUICK_START.md` - Quick reference
- `STRATEGY_IMPLEMENTATION_PLAN.md` - Implementation details
- `STRATEGY_IMPLEMENTATION_STATUS.md` - Current status
- `MULTI_STRATEGY_ANALYSIS.md` - Strategy analysis

---

**Last Updated:** November 17, 2025

