# Strategy Testing Quick Reference

**Quick reference for testing and comparing strategies**

---

## Quick Commands

### Using the CLI (Built-in)

```bash
# Compare all strategies on a stock
python -m tradingagents.strategies compare AAPL

# Compare specific strategies
python -m tradingagents.strategies compare AAPL --strategies value growth momentum

# Run single strategy
python -m tradingagents.strategies run value AAPL

# List all strategies
python -m tradingagents.strategies list
```

### Using the Test Script

```bash
# Compare all strategies on a stock
python test_and_compare_strategies.py compare AAPL

# Compare specific strategies
python test_and_compare_strategies.py compare AAPL --strategies value growth momentum

# Compare multiple stocks
python test_and_compare_strategies.py compare-multi AAPL MSFT GOOGL

# Output JSON
python test_and_compare_strategies.py compare AAPL --json

# List strategies
python test_and_compare_strategies.py list
```

---

## Python API Examples

### Basic Comparison

```python
from tradingagents.strategies import StrategyComparator, StrategyDataCollector
from tradingagents.strategies import ValueStrategy, GrowthStrategy, MomentumStrategy

# Collect data
collector = StrategyDataCollector()
data = collector.collect_all_data("AAPL")

# Compare strategies
comparator = StrategyComparator([
    ValueStrategy(),
    GrowthStrategy(),
    MomentumStrategy(),
])

results = comparator.compare(
    ticker="AAPL",
    market_data=data["market_data"],
    fundamental_data=data["fundamental_data"],
    technical_data=data["technical_data"],
)

# View consensus
print(f"Consensus: {results['consensus']['recommendation']}")
print(f"Agreement: {results['consensus']['agreement_level']:.1f}%")
```

### Single Strategy

```python
from tradingagents.strategies import ValueStrategy, StrategyDataCollector

collector = StrategyDataCollector()
data = collector.collect_all_data("AAPL")

strategy = ValueStrategy()
result = strategy.evaluate(
    ticker="AAPL",
    market_data=data["market_data"],
    fundamental_data=data["fundamental_data"],
    technical_data=data["technical_data"],
)

print(f"Recommendation: {result.recommendation.value}")
print(f"Confidence: {result.confidence}%")
print(f"Target Price: ${result.target_price:.2f}" if result.target_price else "N/A")
```

---

## Available Strategies

| Strategy | Name | Timeframe | Focus |
|----------|------|-----------|-------|
| Value Investing | `value` | 5-10 years | Intrinsic value, margin of safety |
| Growth Investing | `growth` | 1-5 years | Revenue/earnings growth, PEG |
| Dividend Investing | `dividend` | 5+ years | Dividend yield, safety, growth |
| Momentum Trading | `momentum` | 30-90 days | Price trends, technical indicators |
| Contrarian Investing | `contrarian` | Months to years | Oversold conditions, negative sentiment |
| Quantitative Investing | `quantitative` | Weeks to months | Factor-based scoring |
| Sector Rotation | `sector_rotation` | Months to years | Sector strength, economic cycle |

---

## Understanding Results

### Consensus Levels

- **≥80% agreement**: Strong consensus - high confidence
- **60-79% agreement**: Moderate consensus - medium confidence  
- **40-59% agreement**: Mixed signals - investigate further
- **<40% agreement**: Strong divergence - strategies disagree

### Recommendations

- **BUY**: Strategy recommends buying
- **SELL**: Strategy recommends selling
- **HOLD**: Strategy recommends holding existing position
- **WAIT**: Strategy recommends waiting (insufficient data or unclear signal)

### Confidence Scores

- **90-100**: Very high confidence
- **70-89**: High confidence
- **50-69**: Moderate confidence
- **<50**: Low confidence

---

## Common Workflows

### 1. Validate a Recommendation

```python
# Run multiple strategies to validate
comparison = comparator.compare(...)

if comparison['consensus']['agreement_level'] >= 80:
    print("Strong consensus - proceed with confidence")
elif comparison['consensus']['agreement_level'] >= 60:
    print("Moderate consensus - proceed with caution")
else:
    print("Mixed signals - investigate further")
```

### 2. Find Best Strategy for Stock

```python
# Find which strategies recommend BUY
comparison = comparator.compare(...)

buy_strategies = [
    name for name, result in comparison['strategies'].items()
    if result['recommendation'] == 'BUY'
]

print(f"Strategies recommending BUY: {', '.join(buy_strategies)}")
```

### 3. Compare Across Multiple Stocks

```python
tickers = ["AAPL", "MSFT", "GOOGL"]
results = {}

for ticker in tickers:
    data = collector.collect_all_data(ticker)
    results[ticker] = comparator.compare(...)

# Find stocks with strong BUY consensus
for ticker, comparison in results.items():
    if (comparison['consensus']['recommendation'] == 'BUY' and
        comparison['consensus']['agreement_level'] >= 70):
        print(f"{ticker}: Strong BUY consensus")
```

---

## Troubleshooting

### Data Collection Errors

- **Check ticker symbol**: Ensure it's valid (e.g., "AAPL" not "apple")
- **Check date**: Use valid dates in YYYY-MM-DD format
- **Network issues**: Ensure internet connection is working

### Strategy Errors

- Strategies return WAIT if data is insufficient
- Check logs for specific error messages
- Verify all required data fields are present

### Performance Issues

- Data collection takes a few seconds per stock
- Strategy evaluation is fast (<1 second per strategy)
- Comparison of 7 strategies takes ~5-10 seconds total

---

## Next Steps

1. **Read Full Guide**: See `STRATEGY_TESTING_AND_COMPARISON.md` for detailed documentation
2. **Run Tests**: Use `python test_and_compare_strategies.py compare AAPL` to get started
3. **Explore Strategies**: Try different combinations of strategies
4. **Backtest**: Use backtesting engine for historical validation
5. **Track Performance**: Set up outcome tracking for real-world validation

---

## Additional Resources

- **Full Guide**: `docs/STRATEGY_TESTING_AND_COMPARISON.md`
- **Quick Start**: `docs/STRATEGY_QUICK_START.md`
- **Implementation**: `docs/STRATEGY_IMPLEMENTATION_SUMMARY.md`
- **Tests**: `tests/strategies/`
- **Source Code**: `tradingagents/strategies/`

