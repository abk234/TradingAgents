# Phase 5: Portfolio Tracking - User Guide

## Overview

Phase 5 adds sophisticated portfolio tracking and position sizing to TradingAgents.

**Key Features:**
- ✅ Intelligent position sizing based on confidence, volatility, and risk tolerance
- ✅ Entry timing recommendations (BUY_NOW, WAIT_FOR_DIP, WAIT_FOR_BREAKOUT, WAIT)
- ✅ Portfolio configuration with risk parameters
- ✅ Holdings tracking with cost basis
- ✅ Trade execution history
- ✅ Performance snapshots with benchmarking

## Quick Start

### Analyze with Position Sizing

```bash
# Get position sizing recommendation for AAPL
python -m tradingagents.analyze AAPL --plain-english --portfolio-value 100000
```

**Output includes:**
```
💰 HOW MUCH TO INVEST
Recommended investment: $4,200 (4.2% of portfolio)
Number of shares: 24 shares
Price per share: $175.00

Why this amount?
Very high analyst confidence (85%) supports a full position.
High volatility (32%) reduces position size for risk management.
```

### Position Sizing Algorithm

The system considers:

1. **Confidence Level** (0-100)
   - 90-100%: Full position
   - 75-89%: 75% of max
   - 60-74%: 50% of max
   - 50-59%: 35% of max
   - <50%: 25% of max

2. **Risk Tolerance**
   - Conservative: 50% reduction
   - Moderate: Normal
   - Aggressive: 50% increase

3. **Volatility Adjustment**
   - Low (<15%): 20% increase
   - Normal (15-25%): No change
   - High (25-40%): 20% reduction
   - Very high (>40%): 40% reduction

## Entry Timing Recommendations

### Timing Types

**🟢 BUY_NOW**
- Price at favorable entry point
- Technical indicators supportive
- Action: Buy within 1-5 days

**🟡 WAIT_FOR_DIP**
- Stock overbought (RSI > 70)
- Price near resistance
- Action: Wait for 5-10% pullback

**🟡 WAIT_FOR_BREAKOUT**
- Stock consolidating
- Below key moving averages
- Action: Wait for confirmed breakout

**🔴 WAIT**
- Stock in downtrend
- Unfavorable setup
- Action: Re-evaluate in 2-4 weeks

## Database Schema

Five new tables added:

### 1. portfolio_config
Portfolio settings and risk parameters

### 2. position_recommendations  
Position sizing recommendations from analysis

### 3. portfolio_holdings
Actual stock positions with cost basis

### 4. trade_executions
Record of all buy/sell trades

### 5. performance_snapshots
Daily portfolio performance tracking

## API Usage

### PositionSizer

```python
from tradingagents.portfolio import PositionSizer
from decimal import Decimal

sizer = PositionSizer(
    portfolio_value=Decimal('100000'),
    max_position_pct=Decimal('10.0'),
    risk_tolerance='moderate'
)

sizing = sizer.calculate_position_size(
    confidence=85,
    current_price=Decimal('175.00'),
    volatility=Decimal('25.0')
)

print(f"Invest: ${sizing['recommended_amount']}")
print(f"Buy: {sizing['recommended_shares']} shares")
```

### PortfolioOperations

```python
from tradingagents.database import get_db_connection, PortfolioOperations
from decimal import Decimal

db = get_db_connection()
ops = PortfolioOperations(db)

# Create config
config_id = ops.create_config(
    portfolio_value=Decimal('100000'),
    risk_tolerance='moderate'
)

# Log trade
ops.log_trade(
    ticker_id=1,
    trade_type='BUY',
    shares=Decimal('42'),
    price=Decimal('175.00')
)

# View holdings
holdings = ops.get_open_holdings()
```

## Risk Management Best Practices

### Diversification
- Never exceed 10% in single position
- Aim for 15-20 positions
- Limit sector exposure to 30%

### Cash Management
- Keep 15-20% cash reserve
- Don't go all-in on high conviction
- Rebalance quarterly

### Position Sizing Rules
1. Start small with new strategies (50% of calculated)
2. Scale up gradually
3. Reduce in volatile markets (-30-50%)
4. Respect stop losses (exit at -10-15%)

---

**Last Updated:** November 16, 2025
