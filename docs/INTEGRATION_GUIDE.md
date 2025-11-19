# Profitability Features Integration Guide

Complete guide for integrating profitability improvements into your trading workflow.

---

## Quick Start: Enable Profitability Features

### Option 1: Enable in Default Config

Edit `tradingagents/default_config.py`:

```python
DEFAULT_CONFIG = {
    # ... existing config ...
    
    # Profitability Features
    "enable_profitability_features": True,
    "portfolio_value": 100000,  # Your portfolio value
    "enable_regime_detection": True,
    "enable_sector_rotation": True,
    "enable_correlation_check": True,
}
```

### Option 2: Enable When Creating Trading Graph

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from decimal import Decimal

config = DEFAULT_CONFIG.copy()
config["enable_profitability_features"] = True
config["portfolio_value"] = 100000
config["enable_regime_detection"] = True
config["enable_sector_rotation"] = True
config["enable_correlation_check"] = True

ta = TradingAgentsGraph(debug=True, config=config)

# Run analysis - profitability enhancements will be automatically applied
final_state, decision = ta.propagate("NVDA", "2024-05-10", store_analysis=True)

# Access profitability enhancements
if "profitability_enhancements" in final_state:
    enhancements = final_state["profitability_enhancements"]
    print(f"Market regime: {enhancements['market_regime']}")
    print(f"Sector action: {enhancements['sector_action']}")
    print(f"Position sizing: {enhancements['position_sizing']}")
```

---

## Feature-by-Feature Integration

### 1. Market Regime Detection

**Automatic:** Enabled when `enable_regime_detection=True`

**Manual Usage:**
```python
from tradingagents.decision.market_regime import MarketRegimeDetector

detector = MarketRegimeDetector()
market_regime = detector.detect_market_regime()  # 'bull', 'bear', 'neutral'
volatility_regime = detector.detect_volatility_regime()  # 'high', 'low', 'normal'

# Get dynamic thresholds
thresholds = detector.get_dynamic_thresholds(market_regime, volatility_regime)
```

**Integration with Four-Gate Framework:**
```python
from tradingagents.decision.four_gate import FourGateFramework
from tradingagents.decision.market_regime import MarketRegimeDetector

framework = FourGateFramework()
regime_detector = MarketRegimeDetector()

market_regime = regime_detector.detect_market_regime()
volatility_regime = regime_detector.detect_volatility_regime()

result = framework.evaluate_all_gates(
    fundamentals=fundamentals,
    signals=signals,
    price_data=price_data,
    risk_analysis=risk_analysis,
    position_size_pct=5.0,
    historical_context=context,
    confidence_score=85,
    # Thresholds automatically adjust based on regime
)
```

---

### 2. Sector Rotation Detection

**Automatic:** Enabled when `enable_sector_rotation=True`

**Manual Usage:**
```python
from tradingagents.decision.sector_rotation import SectorRotationDetector

detector = SectorRotationDetector()

# Detect rotation for all sectors
actions = detector.detect_sector_rotation()
# Returns: {'Technology': 'OVERWEIGHT', 'Energy': 'UNDERWEIGHT', ...}

# Get top sectors
top_sectors = detector.get_top_sectors(limit=3)

# Check specific sector
should_overweight = detector.should_overweight_sector('Technology')
```

**Integration with Portfolio Allocation:**
```python
# Before adding a position, check sector rotation
sector_actions = detector.detect_sector_rotation()
ticker_sector = 'Technology'  # Get from ticker info

if sector_actions.get(ticker_sector) == 'OVERWEIGHT':
    # Consider larger position
    position_multiplier = 1.2
elif sector_actions.get(ticker_sector) == 'UNDERWEIGHT':
    # Consider smaller position or skip
    position_multiplier = 0.8
else:
    position_multiplier = 1.0
```

---

### 3. Correlation Risk Management

**Automatic:** Enabled when `enable_correlation_check=True`

**Manual Usage:**
```python
from tradingagents.portfolio.correlation_manager import CorrelationManager

mgr = CorrelationManager()

# Check before adding position
existing_holdings = ['AAPL', 'MSFT', 'GOOGL']
new_ticker = 'NVDA'

is_safe, max_corr, correlations = mgr.check_correlation_risk(
    new_ticker, existing_holdings
)

if not is_safe:
    print(f"⚠️ High correlation ({max_corr:.2f}) - consider reducing position or skipping")
    # Option 1: Reduce position size
    recommendation = mgr.recommend_position_adjustment(
        new_ticker, 
        [{'ticker': h, 'position_pct': 5.0} for h in existing_holdings],
        proposed_position_pct=5.0
    )
    adjusted_size = recommendation['adjusted_position_pct']
    # Option 2: Skip the trade
else:
    print(f"✓ Low correlation ({max_corr:.2f}) - safe to add")
```

**Integration with Risk Gate:**
```python
from tradingagents.decision.four_gate import FourGateFramework

framework = FourGateFramework()

# Check correlation first
is_safe, max_corr, correlations = correlation_mgr.check_correlation_risk(
    ticker, existing_holdings
)

# Pass to risk gate
result = framework.evaluate_all_gates(
    fundamentals=fundamentals,
    signals=signals,
    price_data=price_data,
    risk_analysis=risk_analysis,
    position_size_pct=5.0,
    historical_context=context,
    correlation_risk={'max_correlation': max_corr}  # Risk gate will penalize high correlation
)
```

---

### 4. Enhanced Position Sizing

**Automatic:** Enabled when `portfolio_value` is set in config

**Manual Usage:**
```python
from tradingagents.portfolio.position_sizer import PositionSizer
from decimal import Decimal

sizer = PositionSizer(
    portfolio_value=Decimal('100000'),
    max_position_pct=Decimal('10.0'),
    risk_tolerance='moderate'
)

# Basic sizing
sizing = sizer.calculate_position_size(
    confidence=85,
    current_price=Decimal('175.00')
)

# With gate scores (recommended)
gate_scores = {
    'fundamental': 88,
    'technical': 85,
    'risk': 82,
    'timing': 80
}

sizing = sizer.calculate_position_size(
    confidence=85,
    current_price=Decimal('175.00'),
    gate_scores=gate_scores,
    timing_passed=True
)

print(f"Position: {sizing['position_size_pct']}%")
print(f"Amount: ${sizing['recommended_amount']}")
```

**Integration with Trading Graph:**
```python
# After getting gate evaluation results
gate_scores = {
    'fundamental': result['gates']['fundamental']['score'],
    'technical': result['gates']['technical']['score'],
    'risk': result['gates']['risk']['score'],
    'timing': result['gates']['timing']['score']
}

sizing = sizer.calculate_position_size(
    confidence=result['confidence_score'],
    current_price=Decimal(str(price_data['current_price'])),
    gate_scores=gate_scores,
    timing_passed=result['gates']['timing']['passed']
)
```

---

### 5. Exit Strategy Optimization

**Manual Usage:**
```python
from tradingagents.portfolio.position_sizer import PositionSizer
from decimal import Decimal

sizer = PositionSizer(portfolio_value=Decimal('100000'))

# Trailing stop
entry_price = Decimal('175.00')
current_price = Decimal('190.00')
highest_price = Decimal('195.00')

stop_info = sizer.calculate_trailing_stop(
    entry_price=entry_price,
    current_price=current_price,
    highest_price=highest_price
)

if stop_info['should_exit']:
    print("Exit position - stop loss hit")

# Partial profit taking
profit_info = sizer.should_take_partial_profit(
    entry_price=entry_price,
    current_price=current_price
)

if profit_info['should_take_profit']:
    print(f"Sell {profit_info['profit_pct']*100}% of position")
```

**Integration with Portfolio Tracking:**
```python
# Daily monitoring script
for position in portfolio_positions:
    current_price = get_current_price(position['ticker'])
    
    # Update trailing stop
    stop_info = sizer.calculate_trailing_stop(
        entry_price=position['entry_price'],
        current_price=current_price,
        highest_price=position['highest_price']
    )
    
    # Check partial profits
    profit_info = sizer.should_take_partial_profit(
        entry_price=position['entry_price'],
        current_price=current_price
    )
    
    # Execute exits if needed
    if stop_info['should_exit']:
        execute_sell(position['ticker'], 'STOP_LOSS')
    elif profit_info['should_take_profit']:
        execute_partial_sell(position['ticker'], profit_info['profit_pct'])
```

---

## Complete Integration Example

```python
"""
Complete example showing all profitability features integrated.
"""

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.decision.four_gate import FourGateFramework
from tradingagents.decision.market_regime import MarketRegimeDetector
from tradingagents.decision.sector_rotation import SectorRotationDetector
from tradingagents.portfolio.correlation_manager import CorrelationManager
from tradingagents.portfolio.position_sizer import PositionSizer
from decimal import Decimal

# 1. Configure and initialize
config = DEFAULT_CONFIG.copy()
config["enable_profitability_features"] = True
config["portfolio_value"] = 100000
config["enable_regime_detection"] = True
config["enable_sector_rotation"] = True
config["enable_correlation_check"] = True

ta = TradingAgentsGraph(debug=True, config=config)

# 2. Run analysis (profitability features automatically applied)
final_state, decision = ta.propagate("NVDA", "2024-05-10", store_analysis=True)

# 3. Access enhancements
if "profitability_enhancements" in final_state:
    enhancements = final_state["profitability_enhancements"]
    
    print(f"Market Regime: {enhancements['market_regime']}")
    print(f"Volatility Regime: {enhancements['volatility_regime']}")
    print(f"Sector Action: {enhancements['sector_action']}")
    
    if enhancements['correlation_risk']:
        print(f"Correlation Risk: {enhancements['correlation_risk']['max_correlation']:.2f}")
    
    if enhancements['position_sizing']:
        sizing = enhancements['position_sizing']
        print(f"Recommended Position: {sizing['position_size_pct']}%")
        print(f"Recommended Amount: ${sizing['recommended_amount']:,.2f}")
        print(f"Shares: {sizing['recommended_shares']}")
    
    if enhancements['exit_strategy']:
        exit_strat = enhancements['exit_strategy']
        print(f"Trailing Stop: ${exit_strat['trailing_stop']:.2f}")

# 4. Manual checks (if needed)
regime_detector = MarketRegimeDetector()
sector_detector = SectorRotationDetector()
correlation_mgr = CorrelationManager()

# Check sector rotation
sector_actions = sector_detector.detect_sector_rotation()
print(f"\nSector Recommendations:")
for sector, action in sector_actions.items():
    if action != 'NEUTRAL':
        print(f"  {sector}: {action}")

# Check correlation
existing_holdings = ['AAPL', 'MSFT']  # Your current holdings
is_safe, max_corr, _ = correlation_mgr.check_correlation_risk("NVDA", existing_holdings)
print(f"\nCorrelation Check: {'✓ Safe' if is_safe else '⚠ High correlation'} ({max_corr:.2f})")
```

---

## Testing

Run the test suite:

```bash
python test_profitability_features.py
```

This will validate:
- Dynamic thresholds
- Position sizing
- Sector rotation
- Correlation management
- Earnings checks
- Integration

---

## Performance Monitoring

Monitor performance:

```bash
python monitor_profitability_performance.py
```

This generates a report with:
- Win rate by confidence level
- Sector rotation accuracy
- Recommendations for improvement

---

## Best Practices

1. **Always enable correlation checks** - Prevents over-concentration
2. **Monitor sector rotation weekly** - Adjust allocations accordingly
3. **Use gate scores in position sizing** - More accurate than confidence alone
4. **Set up trailing stops** - Protect profits automatically
5. **Take partial profits** - Lock in gains at 5%, 10%, 15%
6. **Review performance monthly** - Adjust parameters based on results

---

## Troubleshooting

### Profitability features not working?

1. Check config: `enable_profitability_features=True`
2. Check portfolio_value is set (for position sizing)
3. Check database connection (for correlation checks)
4. Review logs for initialization errors

### Correlation checks failing?

- Ensure existing holdings are in database
- Check ticker symbols are correct
- Verify yfinance can fetch data

### Sector rotation not detecting?

- Check sector ETFs are accessible
- Verify ticker has sector information in database
- Check network connectivity for ETF data

---

**Last Updated:** November 17, 2025

