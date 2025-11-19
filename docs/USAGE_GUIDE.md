# Profitability Improvements - Complete Usage Guide

This guide shows how to use all the newly implemented profitability improvements.

---

## Quick Start: Using All Features Together

```python
from tradingagents.decision.four_gate import FourGateFramework
from tradingagents.decision.market_regime import MarketRegimeDetector
from tradingagents.decision.sector_rotation import SectorRotationDetector
from tradingagents.portfolio.position_sizer import PositionSizer
from tradingagents.portfolio.correlation_manager import CorrelationManager
from decimal import Decimal

# Initialize all components
framework = FourGateFramework()
regime_detector = MarketRegimeDetector()
sector_detector = SectorRotationDetector()
sizer = PositionSizer(portfolio_value=Decimal('100000'))
correlation_mgr = CorrelationManager()

# 1. Detect market regime
market_regime = regime_detector.detect_market_regime()
volatility_regime = regime_detector.detect_volatility_regime()
print(f"Market: {market_regime}, Volatility: {volatility_regime}")

# 2. Check sector rotation
sector_actions = sector_detector.detect_sector_rotation()
print(f"Sectors to overweight: {[s for s, a in sector_actions.items() if a == 'OVERWEIGHT']}")

# 3. Check correlation risk (before adding new position)
existing_holdings = ['AAPL', 'MSFT', 'GOOGL']
new_ticker = 'NVDA'

is_safe, max_corr, correlations = correlation_mgr.check_correlation_risk(
    new_ticker, existing_holdings
)

if not is_safe:
    print(f"⚠️ High correlation risk: {max_corr:.2f}")
    # Consider reducing position size or skipping

# 4. Evaluate gates with all enhancements
result = framework.evaluate_all_gates(
    fundamentals=fundamentals_data,
    signals=technical_signals,
    price_data=price_data,
    risk_analysis=risk_data,
    position_size_pct=5.0,
    historical_context=context,
    confidence_score=85,
    correlation_risk={'max_correlation': max_corr}
)

# 5. Calculate position size with gate scores
gate_scores = {
    'fundamental': result['gates']['fundamental']['score'],
    'technical': result['gates']['technical']['score'],
    'risk': result['gates']['risk']['score'],
    'timing': result['gates']['timing']['score']
}

sizing = sizer.calculate_position_size(
    confidence=result['confidence_score'],
    current_price=Decimal('175.00'),
    volatility=Decimal('20.0'),
    gate_scores=gate_scores,
    timing_passed=result['gates']['timing']['passed']
)

print(f"Recommended position: {sizing['position_size_pct']}%")
print(f"Amount: ${sizing['recommended_amount']}")

# 6. Set up trailing stop
stop_info = sizer.calculate_trailing_stop(
    entry_price=Decimal('175.00'),
    current_price=Decimal('190.00'),
    highest_price=Decimal('195.00')
)

print(f"Trailing stop: ${stop_info['trailing_stop']}")

# 7. Check partial profit taking
profit_info = sizer.should_take_partial_profit(
    entry_price=Decimal('175.00'),
    current_price=Decimal('192.50')
)

if profit_info['should_take_profit']:
    print(f"Take {profit_info['profit_pct']*100}% profit: {profit_info['reasoning']}")
```

---

## Feature-by-Feature Usage

### 1. Dynamic Gate Thresholds

#### Based on Confidence
```python
from tradingagents.decision.four_gate import FourGateFramework

framework = FourGateFramework()

# Get dynamic thresholds for high confidence
thresholds = framework.get_dynamic_thresholds(confidence_score=90)
# Result: Lower thresholds (more permissive)

# Get dynamic thresholds for low confidence
thresholds = framework.get_dynamic_thresholds(confidence_score=55)
# Result: Higher thresholds (more strict)
```

#### Based on Market Regime
```python
from tradingagents.decision.market_regime import MarketRegimeDetector

detector = MarketRegimeDetector()

# Detect current regime
market_regime = detector.detect_market_regime()  # 'bull', 'bear', or 'neutral'
volatility_regime = detector.detect_volatility_regime()  # 'high', 'low', or 'normal'

# Get dynamic thresholds
thresholds = detector.get_dynamic_thresholds(market_regime, volatility_regime)
```

---

### 2. Enhanced Position Sizing

#### Basic Usage
```python
from tradingagents.portfolio.position_sizer import PositionSizer
from decimal import Decimal

sizer = PositionSizer(
    portfolio_value=Decimal('100000'),
    max_position_pct=Decimal('10.0'),
    risk_tolerance='moderate'
)

# High confidence gets larger position (up to 12%)
sizing = sizer.calculate_position_size(
    confidence=92,
    current_price=Decimal('175.00')
)
# Result: Up to 12% position (vs 10% before)

# Low confidence gets smaller position
sizing = sizer.calculate_position_size(
    confidence=55,
    current_price=Decimal('175.00')
)
# Result: Smaller position based on confidence multiplier
```

#### With Gate Scores (High Impact 2)
```python
# Exceptional gate scores boost position
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
# Result: Position boosted by 20% due to high gate scores

# Weak gate scores reduce position
gate_scores = {
    'fundamental': 65,
    'technical': 60,
    'risk': 58,
    'timing': 55
}

sizing = sizer.calculate_position_size(
    confidence=70,
    current_price=Decimal('175.00'),
    gate_scores=gate_scores,
    timing_passed=False  # Timing gate failed
)
# Result: Position reduced by 20% (weak scores) + 30% (timing failed) = 50% reduction
```

---

### 3. Trailing Stop Loss

```python
# Calculate trailing stop
stop_info = sizer.calculate_trailing_stop(
    entry_price=Decimal('175.00'),
    current_price=Decimal('190.00'),
    highest_price=Decimal('195.00')  # Highest price reached
)

print(f"Trailing stop: ${stop_info['trailing_stop']}")
print(f"Should exit: {stop_info['should_exit']}")
print(f"Profit protected: {stop_info['profit_protected_pct']}%")

# Update as price moves
# If price goes to $200:
stop_info = sizer.calculate_trailing_stop(
    entry_price=Decimal('175.00'),
    current_price=Decimal('200.00'),
    highest_price=Decimal('200.00')  # Update highest
)
# Trailing stop moves up to $184 (8% below $200)
```

---

### 4. Partial Profit Taking

```python
# Check if partial profit should be taken
profit_info = sizer.should_take_partial_profit(
    entry_price=Decimal('175.00'),
    current_price=Decimal('183.75')  # 5% gain
)

if profit_info['should_take_profit']:
    print(f"Sell {profit_info['profit_pct']*100}% of position")
    # Result: Sell 25% at 5% gain

# At 10% gain
profit_info = sizer.should_take_partial_profit(
    entry_price=Decimal('175.00'),
    current_price=Decimal('192.50')  # 10% gain
)
# Result: Sell another 25% (total 50% sold)

# At 15% gain
profit_info = sizer.should_take_partial_profit(
    entry_price=Decimal('175.00'),
    current_price=Decimal('201.25')  # 15% gain
)
# Result: Sell remaining 50% (total 100% sold)
```

---

### 5. Sector Rotation Detection

```python
from tradingagents.decision.sector_rotation import SectorRotationDetector

detector = SectorRotationDetector()

# Detect sector rotation
actions = detector.detect_sector_rotation()
# Returns: {'Technology': 'OVERWEIGHT', 'Energy': 'UNDERWEIGHT', ...}

# Get top sectors
top_sectors = detector.get_top_sectors(limit=3)
for sector_data in top_sectors:
    print(f"{sector_data['sector']}: Momentum {sector_data['momentum_score']:.2f}")

# Quick check for single sector
should_overweight = detector.should_overweight_sector('Technology')
if should_overweight:
    print("Technology sector showing strong momentum - consider overweighting")
```

---

### 6. Correlation-Based Risk Management

```python
from tradingagents.portfolio.correlation_manager import CorrelationManager

mgr = CorrelationManager()

# Check correlation before adding position
existing_holdings = ['AAPL', 'MSFT', 'GOOGL']
new_ticker = 'NVDA'

is_safe, max_corr, correlations = mgr.check_correlation_risk(
    new_ticker, existing_holdings
)

if not is_safe:
    print(f"⚠️ High correlation ({max_corr:.2f}) - consider reducing position or skipping")
else:
    print(f"✓ Low correlation ({max_corr:.2f}) - safe to add")

# Get portfolio diversification score
diversification = mgr.get_diversification_score(
    tickers=['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'AMZN']
)

print(f"Diversification score: {diversification['score']:.2f}")
print(f"Average correlation: {diversification['avg_correlation']:.2f}")
print(f"Highly correlated pairs: {diversification['highly_correlated_pairs']}")

# Get position adjustment recommendation
existing_positions = [
    {'ticker': 'AAPL', 'position_pct': 5.0},
    {'ticker': 'MSFT', 'position_pct': 4.0}
]

recommendation = mgr.recommend_position_adjustment(
    new_ticker='NVDA',
    existing_holdings=existing_positions,
    proposed_position_pct=5.0
)

if recommendation['adjusted_position_pct'] < 5.0:
    print(f"Position reduced to {recommendation['adjusted_position_pct']}%")
    print(f"Reason: {recommendation['reduction_reason']}")
```

---

### 7. Earnings Proximity Check (Automatic in Screener)

```python
from tradingagents.screener.screener import DailyScreener

screener = DailyScreener()

# Earnings check is automatic
# Tickers near earnings (7 days before to 3 days after) are skipped
results = screener.scan_all(update_prices=True)

# Manual check
should_skip, reason = screener.should_skip_ticker('AAPL')
if should_skip:
    print(f"Skipping: {reason}")
```

---

## Integration Example: Complete Analysis Flow

```python
"""
Complete analysis flow using all profitability improvements.
"""

from tradingagents.decision.four_gate import FourGateFramework
from tradingagents.decision.market_regime import MarketRegimeDetector
from tradingagents.decision.sector_rotation import SectorRotationDetector
from tradingagents.portfolio.position_sizer import PositionSizer
from tradingagents.portfolio.correlation_manager import CorrelationManager
from decimal import Decimal

def analyze_opportunity(
    ticker: str,
    fundamentals: dict,
    technical_signals: dict,
    price_data: dict,
    risk_analysis: dict,
    existing_holdings: list,
    portfolio_value: Decimal
):
    """Complete analysis with all profitability improvements."""
    
    # Initialize components
    framework = FourGateFramework()
    regime_detector = MarketRegimeDetector()
    sector_detector = SectorRotationDetector()
    sizer = PositionSizer(portfolio_value=portfolio_value)
    correlation_mgr = CorrelationManager()
    
    # 1. Detect market regime
    market_regime = regime_detector.detect_market_regime()
    volatility_regime = regime_detector.detect_volatility_regime()
    
    # 2. Check sector rotation
    sector = fundamentals.get('sector', 'Unknown')
    sector_action = sector_detector.detect_sector_rotation([sector]).get(sector, 'NEUTRAL')
    
    # 3. Check correlation risk
    is_safe, max_corr, correlations = correlation_mgr.check_correlation_risk(
        ticker, existing_holdings
    )
    
    if not is_safe:
        return {
            'decision': 'PASS',
            'reason': f'High correlation risk ({max_corr:.2f})'
        }
    
    # 4. Evaluate gates with all enhancements
    result = framework.evaluate_all_gates(
        fundamentals=fundamentals,
        signals=technical_signals,
        price_data=price_data,
        risk_analysis=risk_analysis,
        position_size_pct=5.0,  # Initial estimate
        historical_context={},
        confidence_score=None,  # Will be calculated
        correlation_risk={'max_correlation': max_corr}
    )
    
    # 5. Calculate position size with gate scores
    gate_scores = {
        'fundamental': result['gates']['fundamental']['score'],
        'technical': result['gates']['technical']['score'],
        'risk': result['gates']['risk']['score'],
        'timing': result['gates']['timing']['score']
    }
    
    sizing = sizer.calculate_position_size(
        confidence=result['confidence_score'],
        current_price=Decimal(str(price_data['current_price'])),
        volatility=Decimal(str(risk_analysis.get('volatility', 20.0))),
        gate_scores=gate_scores,
        timing_passed=result['gates']['timing']['passed']
    )
    
    # 6. Adjust for correlation if needed
    if max_corr > 0.6:
        recommendation = correlation_mgr.recommend_position_adjustment(
            ticker,
            [{'ticker': h, 'position_pct': 0} for h in existing_holdings],
            float(sizing['position_size_pct'])
        )
        sizing['position_size_pct'] = Decimal(str(recommendation['adjusted_position_pct']))
    
    # 7. Final recommendation
    return {
        'decision': result['final_decision'],
        'confidence': result['confidence_score'],
        'position_size_pct': float(sizing['position_size_pct']),
        'recommended_amount': float(sizing['recommended_amount']),
        'gate_scores': gate_scores,
        'sector_action': sector_action,
        'correlation_risk': max_corr,
        'market_regime': market_regime,
        'volatility_regime': volatility_regime
    }

# Usage
result = analyze_opportunity(
    ticker='NVDA',
    fundamentals={'pe_ratio': 45, 'revenue_growth_yoy': 0.25},
    technical_signals={'rsi': 35, 'macd_bullish_crossover': True},
    price_data={'current_price': 500.0, 'week_52_high': 550.0},
    risk_analysis={'max_expected_drawdown_pct': 15, 'risk_reward_ratio': 2.5},
    existing_holdings=['AAPL', 'MSFT'],
    portfolio_value=Decimal('100000')
)

print(f"Decision: {result['decision']}")
print(f"Position: {result['position_size_pct']}% (${result['recommended_amount']})")
print(f"Sector action: {result['sector_action']}")
print(f"Correlation risk: {result['correlation_risk']:.2f}")
```

---

## Best Practices

1. **Always check correlation** before adding new positions
2. **Monitor sector rotation** weekly to adjust allocations
3. **Use trailing stops** for all positions to protect profits
4. **Take partial profits** at 5%, 10%, and 15% gains
5. **Adjust thresholds** based on market regime
6. **Skip analysis** near earnings to avoid volatility
7. **Scale position sizes** based on gate scores, not just confidence

---

**Last Updated:** November 17, 2025

