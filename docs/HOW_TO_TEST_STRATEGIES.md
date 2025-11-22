# How to Test Strategies in TradingAgents

**Quick Guide:** Testing all available strategies in your application

---

## Available Strategies

You actually have **8 strategies** (not 3!):

1. **Value Investing** (`value`) - Buffett-style value investing
2. **Growth Investing** (`growth`) - Growth at reasonable price (GARP)
3. **Dividend Investing** (`dividend`) - Income-focused investing
4. **Momentum Trading** (`momentum`) - Technical momentum trading
5. **Contrarian Investing** (`contrarian`) - Buy when others fear
6. **Quantitative Investing** (`quantitative`) - Factor-based systematic
7. **Sector Rotation** (`sector_rotation`) - Economic cycle-based
8. **Market Structure and Cloud Trend** (`market_structure`) - Market Structure & Cloud Trend

---

## Method 1: Using Quick Run Script (Easiest) ✅

The `quick_run.sh` script has built-in strategy testing commands:

### List All Strategies
```bash
./quick_run.sh strategy-list
```

### Compare All Strategies on One Stock
```bash
./quick_run.sh strategies AAPL
# or
./quick_run.sh strategy-compare AAPL
```

### Run Single Strategy
```bash
./quick_run.sh strategy-run value AAPL      # Value investing
./quick_run.sh strategy-run growth AAPL     # Growth investing
./quick_run.sh strategy-run dividend AAPL   # Dividend investing
./quick_run.sh strategy-run momentum AAPL   # Momentum trading
./quick_run.sh strategy-run contrarian AAPL # Contrarian investing
./quick_run.sh strategy-run quantitative AAPL # Quantitative
./quick_run.sh strategy-run sector_rotation AAPL # Sector rotation
./quick_run.sh strategy-run market_structure AAPL    # Market Structure and Cloud Trend
```

### Compare Strategies Across Multiple Stocks
```bash
./quick_run.sh strategy-multi AAPL MSFT GOOGL
```

### Compare Strategies on Top Screener Stocks
```bash
./quick_run.sh strategy-screener 20        # Top 20 screener stocks
./quick_run.sh strategy-screener-full 20    # Run screener first, then compare
```

### Comprehensive Strategy Test
```bash
./quick_run.sh strategy-test AAPL
```

---

## Method 2: Using Python CLI Module

### List All Strategies
```bash
python -m tradingagents.strategies list
```

### Compare All Strategies
```bash
python -m tradingagents.strategies compare AAPL
```

### Compare Specific Strategies
```bash
python -m tradingagents.strategies compare AAPL --strategies value growth momentum
```

### Run Single Strategy
```bash
python -m tradingagents.strategies run value AAPL
python -m tradingagents.strategies run growth AAPL
python -m tradingagents.strategies run market_structure AAPL
```

### Output JSON Format
```bash
python -m tradingagents.strategies compare AAPL --json
```

---

## Method 3: Using Test Script

### Compare All Strategies
```bash
python test_and_compare_strategies.py compare AAPL
```

### Compare Specific Strategies
```bash
python test_and_compare_strategies.py compare AAPL --strategies value growth momentum
```

### Compare Multiple Stocks
```bash
python test_and_compare_strategies.py compare-multi AAPL MSFT GOOGL
```

### List Strategies
```bash
python test_and_compare_strategies.py list
```

---

## Method 4: Test Strategies One After Another

### Using a Simple Loop Script

Create a file `test_all_strategies.sh`:

```bash
#!/bin/bash

TICKER=${1:-AAPL}
STRATEGIES=("value" "growth" "dividend" "momentum" "contrarian" "quantitative" "sector_rotation" "market_structure")

echo "Testing all strategies for $TICKER..."
echo "========================================"

for strategy in "${STRATEGIES[@]}"; do
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Testing: $strategy"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    python -m tradingagents.strategies run "$strategy" "$TICKER"
    echo ""
done

echo "========================================"
echo "All strategies tested!"
```

Make it executable and run:
```bash
chmod +x test_all_strategies.sh
./test_all_strategies.sh AAPL
```

### Using Python Script

Create `test_strategies_sequential.py`:

```python
#!/usr/bin/env python3
"""Test all strategies sequentially."""

import sys
from tradingagents.strategies import (
    StrategyDataCollector,
    ValueStrategy,
    GrowthStrategy,
    DividendStrategy,
    MomentumStrategy,
    ContrarianStrategy,
    QuantitativeStrategy,
    SectorRotationStrategy,
)
from tradingagents.strategies.market_structure_cloud_trend import MarketStructureCloudTrendStrategy

def test_all_strategies(ticker="AAPL"):
    """Test all strategies one after another."""
    
    strategies = [
        ("Value Investing", ValueStrategy()),
        ("Growth Investing", GrowthStrategy()),
        ("Dividend Investing", DividendStrategy()),
        ("Momentum Trading", MomentumStrategy()),
        ("Contrarian Investing", ContrarianStrategy()),
        ("Quantitative Investing", QuantitativeStrategy()),
        ("Sector Rotation", SectorRotationStrategy()),
        ("Market Structure and Cloud Trend", MarketStructureCloudTrendStrategy()),
    ]
    
    # Collect data once
    print(f"Collecting data for {ticker}...")
    collector = StrategyDataCollector()
    data = collector.collect_all_data(ticker)
    
    print(f"\n{'='*70}")
    print(f"Testing All Strategies for {ticker}")
    print(f"{'='*70}\n")
    
    results = []
    
    for name, strategy in strategies:
        print(f"\n{'─'*70}")
        print(f"Strategy: {name}")
        print(f"{'─'*70}")
        
        try:
            result = strategy.evaluate(
                ticker=ticker,
                market_data=data["market_data"],
                fundamental_data=data["fundamental_data"],
                technical_data=data["technical_data"],
                additional_data={"ticker": ticker}  # For Market Structure and Cloud Trend
            )
            
            print(f"Recommendation: {result.recommendation.value}")
            print(f"Confidence: {result.confidence}%")
            print(f"Reasoning: {result.reasoning[:200]}...")
            
            if result.entry_price:
                print(f"Entry Price: ${result.entry_price:.2f}")
            if result.stop_loss:
                print(f"Stop Loss: ${result.stop_loss:.2f}")
            if result.target_price:
                print(f"Take Profit: ${result.target_price:.2f}")
            
            results.append((name, result))
            
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append((name, None))
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    
    buy_count = sum(1 for _, r in results if r and r.recommendation.value == "BUY")
    sell_count = sum(1 for _, r in results if r and r.recommendation.value == "SELL")
    wait_count = sum(1 for _, r in results if r and r.recommendation.value == "WAIT")
    hold_count = sum(1 for _, r in results if r and r.recommendation.value == "HOLD")
    
    print(f"\nRecommendations:")
    print(f"  BUY: {buy_count}")
    print(f"  SELL: {sell_count}")
    print(f"  WAIT: {wait_count}")
    print(f"  HOLD: {hold_count}")
    
    print(f"\nStrategy Details:")
    for name, result in results:
        if result:
            print(f"  {name}: {result.recommendation.value} ({result.confidence}%)")
        else:
            print(f"  {name}: ERROR")

if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    test_all_strategies(ticker)
```

Run it:
```bash
python test_strategies_sequential.py AAPL
```

---

## Method 5: Compare All Strategies at Once

### Using StrategyComparator

```python
from tradingagents.strategies import StrategyComparator, StrategyDataCollector
from tradingagents.strategies import (
    ValueStrategy, GrowthStrategy, DividendStrategy,
    MomentumStrategy, ContrarianStrategy, QuantitativeStrategy,
    SectorRotationStrategy
)
from tradingagents.strategies.market_structure_cloud_trend import MarketStructureCloudTrendStrategy

# Collect data
collector = StrategyDataCollector()
data = collector.collect_all_data("AAPL")

# Create comparator with all strategies
comparator = StrategyComparator([
    ValueStrategy(),
    GrowthStrategy(),
    DividendStrategy(),
    MomentumStrategy(),
    ContrarianStrategy(),
    QuantitativeStrategy(),
    SectorRotationStrategy(),
    AIPineScriptStrategy(),  # NEW!
])

# Compare
result = comparator.compare(
    ticker="AAPL",
    market_data=data["market_data"],
    fundamental_data=data["fundamental_data"],
    technical_data=data["technical_data"],
    additional_data={"ticker": "AAPL"}  # For AI Pine Script
)

# View results
print(f"Consensus: {result['consensus']['recommendation']}")
print(f"Agreement: {result['consensus']['agreement_level']:.1f}%")

for name, strategy_result in result['strategies'].items():
    print(f"{name}: {strategy_result['recommendation']} ({strategy_result['confidence']}%)")
```

---

## Quick Reference

### Commands Summary

| Action | Command |
|--------|---------|
| **List strategies** | `./quick_run.sh strategy-list` |
| **Compare all** | `./quick_run.sh strategies AAPL` |
| **Run single** | `./quick_run.sh strategy-run value AAPL` |
| **Compare multiple stocks** | `./quick_run.sh strategy-multi AAPL MSFT GOOGL` |
| **Test on screener stocks** | `./quick_run.sh strategy-screener 20` |

### Strategy Names

- `value` - Value Investing
- `growth` - Growth Investing
- `dividend` - Dividend Investing
- `momentum` - Momentum Trading
- `contrarian` - Contrarian Investing
- `quantitative` - Quantitative Investing
- `sector_rotation` - Sector Rotation
- `market_structure` - Market Structure and Cloud Trend

---

## Examples

### Example 1: Quick Test
```bash
# List all strategies
./quick_run.sh strategy-list

# Compare all on AAPL
./quick_run.sh strategies AAPL
```

### Example 2: Test Specific Strategies
```bash
# Compare value, growth, and Market Structure and Cloud Trend
python -m tradingagents.strategies compare AAPL --strategies value growth market_structure
```

### Example 3: Test One After Another
```bash
# Run each strategy sequentially
for strategy in value growth dividend momentum contrarian quantitative sector_rotation market_structure; do
    echo "Testing $strategy..."
    ./quick_run.sh strategy-run $strategy AAPL
    echo ""
done
```

### Example 4: Comprehensive Test
```bash
# Full strategy comparison with insights
./quick_run.sh strategy-test AAPL
```

---

## Tips

1. **Use Quick Run Script:** Easiest way to test strategies
2. **Compare All:** Use `strategies` command to see consensus
3. **Test Sequentially:** Use loop script to test one after another
4. **Include Market Structure and Cloud Trend:** Add `market_structure` to your strategy list
5. **Multiple Stocks:** Test on multiple stocks to see consistency

---

## Next Steps

1. **Backtesting:** Test strategies on historical data
2. **Performance Tracking:** Monitor which strategies perform best
3. **Strategy Evolution:** Improve strategies based on results
4. **Live Testing:** Paper trade with validated strategies

---

**Last Updated:** 2025-01-20  
**Total Strategies:** 8 (including Market Structure and Cloud Trend)

