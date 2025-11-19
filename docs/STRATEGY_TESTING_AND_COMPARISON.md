# Strategy Testing and Comparison Guide

**Date:** November 17, 2025  
**Purpose:** Comprehensive guide for testing and comparing trading strategies

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Testing Methods](#testing-methods)
4. [Comparison Methods](#comparison-methods)
5. [Backtesting Strategies](#backtesting-strategies)
6. [Performance Evaluation](#performance-evaluation)
7. [Best Practices](#best-practices)

---

## Overview

This guide explains how to test and compare the various investment strategies implemented in TradingAgents. The system includes 7 different strategies:

1. **Value Investing** - Buffett-style value investing
2. **Growth Investing** - Growth at reasonable price (GARP)
3. **Dividend Investing** - Income-focused investing
4. **Momentum Trading** - Technical momentum trading
5. **Contrarian Investing** - Buy when others fear
6. **Quantitative Investing** - Factor-based systematic
7. **Sector Rotation** - Economic cycle-based

---

## Quick Start

### Method 1: CLI Comparison (Easiest)

Compare all strategies on a single stock:

```bash
# Compare all strategies
python -m tradingagents.strategies compare AAPL

# Compare specific strategies
python -m tradingagents.strategies compare AAPL --strategies value growth momentum

# Output JSON format
python -m tradingagents.strategies compare AAPL --json

# Run single strategy
python -m tradingagents.strategies run value AAPL

# List all available strategies
python -m tradingagents.strategies list
```

### Method 2: Python API

```python
from tradingagents.strategies import (
    StrategyComparator,
    StrategyDataCollector,
    ValueStrategy,
    GrowthStrategy,
    DividendStrategy,
    MomentumStrategy,
    ContrarianStrategy,
    QuantitativeStrategy,
    SectorRotationStrategy,
)

# Collect data once
collector = StrategyDataCollector()
data = collector.collect_all_data("AAPL", "2024-11-17")

# Create comparator with all strategies
comparator = StrategyComparator([
    ValueStrategy(),
    GrowthStrategy(),
    DividendStrategy(),
    MomentumStrategy(),
    ContrarianStrategy(),
    QuantitativeStrategy(),
    SectorRotationStrategy(),
])

# Compare strategies
comparison = comparator.compare(
    ticker="AAPL",
    market_data=data["market_data"],
    fundamental_data=data["fundamental_data"],
    technical_data=data["technical_data"],
    additional_data={
        "dividend_data": data.get("dividend_data", {}),
        "news_data": data.get("news_data", {}),
    }
)

# View results
print(f"Consensus: {comparison['consensus']['recommendation']}")
print(f"Agreement: {comparison['consensus']['agreement_level']:.1f}%")
```

---

## Testing Methods

### 1. Single Stock Analysis

Test how different strategies evaluate a single stock:

```python
from tradingagents.strategies import StrategyComparator, StrategyDataCollector
from tradingagents.strategies import (
    ValueStrategy, GrowthStrategy, DividendStrategy, MomentumStrategy
)

# Setup
collector = StrategyDataCollector()
ticker = "AAPL"
analysis_date = "2024-11-17"

# Collect data
data = collector.collect_all_data(ticker, analysis_date)

# Create comparator
comparator = StrategyComparator([
    ValueStrategy(),
    GrowthStrategy(),
    DividendStrategy(),
    MomentumStrategy(),
])

# Run comparison
results = comparator.compare(
    ticker=ticker,
    market_data=data["market_data"],
    fundamental_data=data["fundamental_data"],
    technical_data=data["technical_data"],
)

# Analyze results
print(f"\n{'='*70}")
print(f"Strategy Comparison: {ticker}")
print(f"{'='*70}\n")

print(f"Consensus Recommendation: {results['consensus']['recommendation']}")
print(f"Agreement Level: {results['consensus']['agreement_level']:.1f}%")
print(f"\nVotes:")
print(f"  BUY:  {results['consensus']['buy_count']}")
print(f"  SELL: {results['consensus']['sell_count']}")
print(f"  HOLD: {results['consensus']['hold_count']}")
print(f"  WAIT: {results['consensus']['wait_count']}")

print(f"\n{'='*70}")
print("Individual Strategy Results:")
print(f"{'='*70}")

for strategy_name, result in results['strategies'].items():
    print(f"\n{strategy_name}:")
    print(f"  Recommendation: {result['recommendation']}")
    print(f"  Confidence: {result['confidence']}%")
    print(f"  Reasoning: {result['reasoning'][:200]}...")
    if result.get('target_price'):
        print(f"  Target Price: ${result['target_price']:.2f}")
    if result.get('entry_price'):
        print(f"  Entry Price: ${result['entry_price']:.2f}")

# Show insights
if results.get('insights'):
    print(f"\n{'='*70}")
    print("Insights:")
    print(f"{'='*70}")
    for insight in results['insights']:
        print(f"  • {insight}")
```

### 2. Multi-Stock Comparison

Compare strategies across multiple stocks:

```python
from tradingagents.strategies import StrategyComparator, StrategyDataCollector
from tradingagents.strategies import (
    ValueStrategy, GrowthStrategy, MomentumStrategy
)

tickers = ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA"]
strategies = [ValueStrategy(), GrowthStrategy(), MomentumStrategy()]

collector = StrategyDataCollector()
comparator = StrategyComparator(strategies)

results_by_ticker = {}

for ticker in tickers:
    print(f"\nAnalyzing {ticker}...")
    try:
        data = collector.collect_all_data(ticker)
        comparison = comparator.compare(
            ticker=ticker,
            market_data=data["market_data"],
            fundamental_data=data["fundamental_data"],
            technical_data=data["technical_data"],
        )
        results_by_ticker[ticker] = comparison
    except Exception as e:
        print(f"Error analyzing {ticker}: {e}")
        continue

# Summary table
print(f"\n{'='*80}")
print("Multi-Stock Strategy Comparison Summary")
print(f"{'='*80}\n")

print(f"{'Ticker':<10} {'Value':<15} {'Growth':<15} {'Momentum':<15} {'Consensus':<15}")
print("-" * 80)

for ticker, comparison in results_by_ticker.items():
    strategies_results = comparison['strategies']
    value_rec = strategies_results.get('Value Investing', {}).get('recommendation', 'N/A')
    growth_rec = strategies_results.get('Growth Investing', {}).get('recommendation', 'N/A')
    momentum_rec = strategies_results.get('Momentum Trading', {}).get('recommendation', 'N/A')
    consensus = comparison['consensus'].get('recommendation', 'N/A')
    
    print(f"{ticker:<10} {value_rec:<15} {growth_rec:<15} {momentum_rec:<15} {consensus:<15}")

# Count recommendations
print(f"\n{'='*80}")
print("Recommendation Counts:")
print(f"{'='*80}")

buy_counts = {}
for ticker, comparison in results_by_ticker.items():
    for strategy_name, result in comparison['strategies'].items():
        rec = result.get('recommendation', 'WAIT')
        if rec == 'BUY':
            buy_counts[strategy_name] = buy_counts.get(strategy_name, 0) + 1

for strategy_name, count in sorted(buy_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {strategy_name}: {count} BUY recommendations out of {len(tickers)} stocks")
```

### 3. Strategy Performance Over Time

Track how strategies perform over different time periods:

```python
from datetime import date, timedelta
from tradingagents.strategies import StrategyComparator, StrategyDataCollector
from tradingagents.strategies import ValueStrategy, GrowthStrategy, MomentumStrategy

ticker = "AAPL"
strategies = [ValueStrategy(), GrowthStrategy(), MomentumStrategy()]
collector = StrategyDataCollector()
comparator = StrategyComparator(strategies)

# Test over multiple dates
test_dates = [
    date.today() - timedelta(days=30),
    date.today() - timedelta(days=60),
    date.today() - timedelta(days=90),
    date.today(),
]

results_by_date = {}

for test_date in test_dates:
    date_str = test_date.strftime("%Y-%m-%d")
    print(f"\nTesting on {date_str}...")
    
    try:
        data = collector.collect_all_data(ticker, date_str)
        comparison = comparator.compare(
            ticker=ticker,
            market_data=data["market_data"],
            fundamental_data=data["fundamental_data"],
            technical_data=data["technical_data"],
        )
        results_by_date[date_str] = comparison
    except Exception as e:
        print(f"Error on {date_str}: {e}")
        continue

# Show how recommendations changed over time
print(f"\n{'='*80}")
print(f"Strategy Recommendations Over Time: {ticker}")
print(f"{'='*80}\n")

for strategy_name in ["Value Investing", "Growth Investing", "Momentum Trading"]:
    print(f"{strategy_name}:")
    for date_str in sorted(results_by_date.keys()):
        rec = results_by_date[date_str]['strategies'].get(strategy_name, {}).get('recommendation', 'N/A')
        conf = results_by_date[date_str]['strategies'].get(strategy_name, {}).get('confidence', 0)
        print(f"  {date_str}: {rec} ({conf}% confidence)")
    print()
```

---

## Comparison Methods

### 1. Consensus Analysis

The `StrategyComparator` automatically calculates consensus:

```python
comparison = comparator.compare(...)

consensus = comparison['consensus']
print(f"Consensus Recommendation: {consensus['recommendation']}")
print(f"Agreement Level: {consensus['agreement_level']:.1f}%")
print(f"Total Strategies: {consensus['total_strategies']}")
print(f"BUY votes: {consensus['buy_count']}")
print(f"SELL votes: {consensus['sell_count']}")
print(f"HOLD votes: {consensus['hold_count']}")
print(f"WAIT votes: {consensus['wait_count']}")

# Interpretation
if consensus['agreement_level'] >= 80:
    print("✅ Strong consensus - high confidence")
elif consensus['agreement_level'] >= 60:
    print("✓ Moderate consensus - medium confidence")
else:
    print("⚠ Mixed signals - investigate further")
```

### 2. Divergence Analysis

Identify where strategies disagree:

```python
comparison = comparator.compare(...)

divergences = comparison['divergences']

if divergences:
    print("Strategy Divergences:")
    for div in divergences:
        print(f"  {div['recommendation']}: {', '.join(div['strategies'])} ({div['count']} strategies)")
else:
    print("✅ All strategies agree!")
```

### 3. Confidence Comparison

Compare confidence levels across strategies:

```python
comparison = comparator.compare(...)

# Sort strategies by confidence
strategies_by_conf = sorted(
    comparison['strategies'].items(),
    key=lambda x: x[1]['confidence'],
    reverse=True
)

print("Strategies Ranked by Confidence:")
for i, (name, result) in enumerate(strategies_by_conf, 1):
    print(f"{i}. {name}: {result['confidence']}% ({result['recommendation']})")
```

### 4. Key Metrics Comparison

Compare key metrics that each strategy focuses on:

```python
comparison = comparator.compare(...)

print("Key Metrics by Strategy:")
for strategy_name, result in comparison['strategies'].items():
    print(f"\n{strategy_name}:")
    metrics = result.get('key_metrics', {})
    for metric_name, value in metrics.items():
        if value is not None:
            if isinstance(value, float):
                print(f"  {metric_name}: {value:.2f}")
            else:
                print(f"  {metric_name}: {value}")
```

---

## Backtesting Strategies

### Using the Backtest Engine

The system includes a backtesting engine for historical validation:

```python
from datetime import date, timedelta
from tradingagents.backtest import BacktestEngine

# Initialize engine
engine = BacktestEngine()

# Run backtest
result = engine.test_strategy(
    strategy_name="Value Strategy",
    start_date=date(2023, 1, 1),
    end_date=date(2024, 12, 31),
    tickers=["AAPL", "MSFT", "GOOGL"],
    holding_period_days=30,
    min_confidence=70
)

# View results
print(f"Strategy: {result.strategy_name}")
print(f"Period: {result.start_date} to {result.end_date}")
print(f"Total Trades: {result.total_trades}")
print(f"Winning Trades: {result.winning_trades}")
print(f"Losing Trades: {result.losing_trades}")
print(f"Win Rate: {result.win_rate:.1f}%")
print(f"Average Return: {result.avg_return:.2f}%")
print(f"Total Return: {result.total_return:.2f}%")
print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
print(f"Max Drawdown: {result.max_drawdown:.2f}%")
```

### Backtesting Multiple Strategies

Compare strategies using backtesting:

```python
from datetime import date
from tradingagents.backtest import BacktestEngine

engine = BacktestEngine()
tickers = ["AAPL", "MSFT", "GOOGL", "NVDA"]
start_date = date(2023, 1, 1)
end_date = date(2024, 12, 31)

# Note: The current BacktestEngine uses Four-Gate Framework
# To backtest individual strategies, you would need to adapt them
# or create strategy-specific backtest wrappers

results = []

# Example: Backtest with different confidence thresholds
for min_conf in [60, 70, 80]:
    result = engine.test_strategy(
        strategy_name=f"Four-Gate (conf >= {min_conf})",
        start_date=start_date,
        end_date=end_date,
        tickers=tickers,
        holding_period_days=30,
        min_confidence=min_conf
    )
    results.append(result)

# Compare results
print(f"\n{'='*80}")
print("Backtest Comparison")
print(f"{'='*80}\n")

print(f"{'Strategy':<30} {'Trades':<10} {'Win Rate':<12} {'Avg Return':<15} {'Sharpe':<10}")
print("-" * 80)

for result in results:
    print(f"{result.strategy_name:<30} {result.total_trades:<10} "
          f"{result.win_rate:.1f}%{'':<7} {result.avg_return:+.2f}%{'':<9} "
          f"{result.sharpe_ratio:.2f}")
```

---

## Performance Evaluation

### Using Performance Analyzer

Track real-world performance of recommendations:

```python
from tradingagents.evaluate import PerformanceAnalyzer

analyzer = PerformanceAnalyzer()

# Get overall stats
stats = analyzer.get_overall_stats(days_back=90)
print(f"Total Recommendations: {stats.get('total_recommendations', 0)}")
print(f"Win Rate: {stats.get('win_rate_pct', 0):.1f}%")
print(f"Average Return (30d): {stats.get('avg_return_30days', 0):+.2f}%")
print(f"Alpha vs S&P 500: {stats.get('avg_alpha_30days', 0):+.2f}%")

# Performance by confidence level
by_confidence = analyzer.get_performance_by_confidence(days_back=90)
print("\nPerformance by Confidence Level:")
for row in by_confidence:
    print(f"  {row['confidence_range']}: "
          f"{row['win_rate_pct']:.1f}% win rate, "
          f"{row['avg_return_30days']:+.2f}% avg return")

# Generate full report
report = analyzer.generate_report(days_back=90)
print(report)
```

### Comparing Strategy Performance

```python
from tradingagents.evaluate import PerformanceAnalyzer
from tradingagents.database import get_db_connection

analyzer = PerformanceAnalyzer()
db = get_db_connection()

# Query recommendations by strategy (if stored)
# Note: This requires strategy information to be stored in analyses
query = """
    SELECT 
        a.final_decision,
        a.confidence_score,
        ro.return_30days_pct,
        ro.was_correct
    FROM analyses a
    JOIN recommendation_outcomes ro ON a.analysis_id = ro.analysis_id
    WHERE ro.return_30days_pct IS NOT NULL
    AND a.analysis_date >= CURRENT_DATE - INTERVAL '90 days'
    ORDER BY a.analysis_date DESC
"""

results = db.execute_dict_query(query)

# Group by decision type and analyze
# (This is a simplified example - actual strategy tracking would need
#  strategy_name stored in the database)
```

---

## Best Practices

### 1. Data Collection

- **Collect data once**: Use `StrategyDataCollector` to gather all data, then pass it to multiple strategies
- **Handle errors gracefully**: Strategies return WAIT recommendations when data is insufficient
- **Use appropriate dates**: For historical testing, use dates in the past

### 2. Strategy Selection

- **Match strategy to timeframe**: 
  - Value/Growth: Long-term (years)
  - Momentum: Short-term (days/weeks)
  - Dividend: Income-focused (years)
- **Consider market conditions**: Some strategies work better in certain market environments

### 3. Comparison Analysis

- **Look for consensus**: High agreement (>80%) suggests stronger signal
- **Investigate divergences**: When strategies disagree, understand why
- **Consider confidence levels**: Higher confidence doesn't always mean better, but it indicates conviction

### 4. Backtesting

- **Use sufficient data**: Test over multiple market cycles
- **Avoid lookahead bias**: Ensure only historical data is used
- **Test multiple scenarios**: Different time periods, different tickers
- **Compare to benchmarks**: Always compare results to S&P 500 or relevant index

### 5. Performance Tracking

- **Track outcomes**: Use `OutcomeTracker` to monitor real-world results
- **Update regularly**: Update outcomes periodically to track performance
- **Calculate alpha**: Compare returns to benchmarks
- **Review periodically**: Analyze performance monthly or quarterly

---

## Example: Complete Testing Workflow

```python
"""
Complete strategy testing workflow example
"""

from datetime import date, timedelta
from tradingagents.strategies import (
    StrategyComparator,
    StrategyDataCollector,
    ValueStrategy,
    GrowthStrategy,
    DividendStrategy,
    MomentumStrategy,
    ContrarianStrategy,
    QuantitativeStrategy,
    SectorRotationStrategy,
)

def test_strategies_comprehensive(ticker: str, analysis_date: str = None):
    """Comprehensive strategy testing for a single stock."""
    
    if analysis_date is None:
        analysis_date = date.today().strftime("%Y-%m-%d")
    
    print(f"\n{'='*80}")
    print(f"Comprehensive Strategy Test: {ticker}")
    print(f"Analysis Date: {analysis_date}")
    print(f"{'='*80}\n")
    
    # Step 1: Collect data
    print("Step 1: Collecting data...")
    collector = StrategyDataCollector()
    try:
        data = collector.collect_all_data(ticker, analysis_date)
        print("✅ Data collected successfully")
    except Exception as e:
        print(f"❌ Data collection failed: {e}")
        return None
    
    # Step 2: Initialize all strategies
    print("\nStep 2: Initializing strategies...")
    strategies = [
        ValueStrategy(),
        GrowthStrategy(),
        DividendStrategy(),
        MomentumStrategy(),
        ContrarianStrategy(),
        QuantitativeStrategy(),
        SectorRotationStrategy(),
    ]
    print(f"✅ {len(strategies)} strategies initialized")
    
    # Step 3: Run comparison
    print("\nStep 3: Running strategy comparison...")
    comparator = StrategyComparator(strategies)
    comparison = comparator.compare(
        ticker=ticker,
        market_data=data["market_data"],
        fundamental_data=data["fundamental_data"],
        technical_data=data["technical_data"],
        additional_data={
            "analysis_date": analysis_date,
            "dividend_data": data.get("dividend_data", {}),
            "news_data": data.get("news_data", {}),
        }
    )
    print("✅ Comparison complete")
    
    # Step 4: Analyze results
    print("\nStep 4: Analyzing results...")
    
    # Consensus
    consensus = comparison['consensus']
    print(f"\n📊 Consensus:")
    print(f"   Recommendation: {consensus['recommendation']}")
    print(f"   Agreement: {consensus['agreement_level']:.1f}%")
    print(f"   Votes: BUY={consensus['buy_count']}, "
          f"SELL={consensus['sell_count']}, "
          f"HOLD={consensus['hold_count']}, "
          f"WAIT={consensus['wait_count']}")
    
    # Individual strategies
    print(f"\n📈 Individual Strategy Results:")
    for strategy_name, result in comparison['strategies'].items():
        print(f"\n   {strategy_name}:")
        print(f"      Recommendation: {result['recommendation']}")
        print(f"      Confidence: {result['confidence']}%")
        if result.get('target_price'):
            print(f"      Target Price: ${result['target_price']:.2f}")
        if result.get('entry_price'):
            print(f"      Entry Price: ${result['entry_price']:.2f}")
    
    # Insights
    if comparison.get('insights'):
        print(f"\n💡 Insights:")
        for insight in comparison['insights']:
            print(f"   • {insight}")
    
    # Divergences
    if comparison.get('divergences'):
        print(f"\n⚠️  Divergences:")
        for div in comparison['divergences']:
            print(f"   {div['recommendation']}: {', '.join(div['strategies'])}")
    
    return comparison

# Run test
if __name__ == "__main__":
    # Test on multiple stocks
    test_tickers = ["AAPL", "MSFT", "GOOGL"]
    
    for ticker in test_tickers:
        result = test_strategies_comprehensive(ticker)
        if result:
            print(f"\n✅ Test complete for {ticker}\n")
        else:
            print(f"\n❌ Test failed for {ticker}\n")
```

---

## Troubleshooting

### Common Issues

1. **Data Collection Errors**
   - Check network connection
   - Verify ticker symbol is valid
   - Ensure API keys are configured (if needed)

2. **Strategy Evaluation Errors**
   - Strategies handle missing data gracefully (return WAIT)
   - Check that required data fields are present
   - Review strategy logs for specific errors

3. **Comparison Issues**
   - Ensure all strategies are properly initialized
   - Check that data format matches expectations
   - Verify strategy names are unique

4. **Backtesting Issues**
   - Ensure sufficient historical data is available
   - Check date ranges are valid
   - Verify tickers have enough trading history

---

## Next Steps

1. **Run Quick Test**: Use CLI to compare strategies on a few stocks
2. **Deep Dive**: Use Python API for detailed analysis
3. **Backtest**: Run historical backtests to validate strategies
4. **Track Performance**: Set up outcome tracking for real-world validation
5. **Customize**: Modify strategies or create new ones based on your needs

---

## Additional Resources

- `STRATEGY_QUICK_START.md` - Quick reference guide
- `STRATEGY_IMPLEMENTATION_SUMMARY.md` - Implementation details
- `tests/strategies/` - Unit tests for strategies
- `tradingagents/strategies/` - Strategy source code

