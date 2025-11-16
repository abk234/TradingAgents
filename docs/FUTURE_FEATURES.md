# Future Features - Portfolio Management & Position Sizing

This document outlines features requested for automated portfolio management, position sizing, and dividend tracking.

---

## Current Capabilities ✅

### What Works Now

1. **Daily Screening**
   - Scans 16 tickers in watchlist
   - Identifies top opportunities
   - Ranks by priority score

2. **Deep Analysis**
   - Multi-agent investment analysis
   - Historical intelligence via RAG
   - BUY/WAIT/HOLD/SELL decisions
   - Confidence scoring

3. **Batch Processing**
   - Analyze top N from screener
   - Filter by alerts or score
   - Sequential analysis

### Example Current Workflow

```bash
# 1. Run screener
python -m tradingagents.screener run

# 2. Analyze top 5
python -m tradingagents.analyze.batch_analyze --top 5

# Output:
# AAPL - BUY (Confidence: 85/100)
# GOOGL - WAIT (Confidence: 72/100)
# MSFT - BUY (Confidence: 78/100)
# ...
```

**What's Missing:**
- ❌ How much $$ to invest in each
- ❌ When exactly to buy
- ❌ Portfolio allocation recommendations
- ❌ Dividend tracking
- ❌ Performance monitoring
- ❌ Automated execution

---

## Requested Features 🚧

### Feature 1: Position Sizing & Allocation

**Goal:** Automatically recommend how much to invest in each opportunity.

#### What This Means

Instead of just:
```
AAPL - BUY (Confidence: 85/100)
```

Get:
```
AAPL - BUY
  Recommended: $5,000 (5% of portfolio)
  Entry Price: $175.50
  Target Price: $195.00 (3-6 months)
  Stop Loss: $160.00
  Expected Return: +11.1%
  Risk/Reward: 1:1.26
```

#### Required Inputs

1. **Portfolio Parameters**
   - Total portfolio value (e.g., $100,000)
   - Maximum position size (e.g., 10%)
   - Risk tolerance (conservative/moderate/aggressive)
   - Cash allocation (e.g., keep 20% cash)

2. **Risk Parameters**
   - Max portfolio volatility
   - Max drawdown tolerance
   - Sector concentration limits
   - Correlation constraints

#### Implementation Approach

**Database Schema Additions:**
```sql
-- Portfolio configuration
CREATE TABLE portfolio_config (
    config_id SERIAL PRIMARY KEY,
    portfolio_value DECIMAL(15, 2),
    max_position_pct DECIMAL(5, 2),
    risk_tolerance VARCHAR(20),
    cash_reserve_pct DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Position sizing recommendations
CREATE TABLE position_recommendations (
    recommendation_id SERIAL PRIMARY KEY,
    analysis_id BIGINT REFERENCES analyses(analysis_id),
    recommended_shares INTEGER,
    recommended_amount DECIMAL(15, 2),
    position_size_pct DECIMAL(5, 2),
    entry_price DECIMAL(10, 2),
    target_price DECIMAL(10, 2),
    stop_loss DECIMAL(10, 2),
    expected_return_pct DECIMAL(7, 2),
    risk_reward_ratio DECIMAL(5, 2),
    reasoning TEXT
);
```

**Position Sizing Logic:**
```python
def calculate_position_size(
    portfolio_value: float,
    confidence_score: int,
    risk_tolerance: str,
    volatility: float,
    sector_exposure: Dict[str, float]
) -> Dict[str, Any]:
    """
    Calculate optimal position size.

    Logic:
    1. Base allocation from confidence (80+ → 5%, 70-79 → 3%, etc.)
    2. Adjust for risk tolerance
    3. Adjust for volatility
    4. Check sector concentration limits
    5. Calculate share count
    """

    # Base allocation from confidence
    if confidence_score >= 80:
        base_pct = 5.0
    elif confidence_score >= 70:
        base_pct = 3.0
    elif confidence_score >= 60:
        base_pct = 2.0
    else:
        base_pct = 1.0

    # Risk tolerance adjustment
    risk_multipliers = {
        'conservative': 0.5,
        'moderate': 1.0,
        'aggressive': 1.5
    }
    adjusted_pct = base_pct * risk_multipliers[risk_tolerance]

    # Volatility adjustment (reduce for high vol stocks)
    if volatility > 40:  # High volatility
        adjusted_pct *= 0.7
    elif volatility > 25:  # Moderate volatility
        adjusted_pct *= 0.85

    # Sector concentration check
    # (reduce if sector already heavily weighted)

    # Calculate dollar amount
    position_value = portfolio_value * (adjusted_pct / 100)

    return {
        'position_size_pct': adjusted_pct,
        'position_value': position_value,
        'reasoning': f"Based on {confidence_score}/100 confidence, "
                    f"{risk_tolerance} risk tolerance, "
                    f"{volatility:.1f}% volatility"
    }
```

#### Usage Example

```bash
# Initialize portfolio
python -m tradingagents.portfolio init \
  --value 100000 \
  --max-position 10 \
  --risk moderate

# Analyze with position sizing
python -m tradingagents.analyze.batch_analyze --top 5 --with-sizing

# Output:
# ==================== RECOMMENDED POSITIONS ====================
#
# 1. AAPL - BUY
#    Confidence: 85/100
#    Position: $5,000 (5.0% of portfolio)
#    Shares: 28 @ $175.50
#    Target: $195.00 (+11.1%)
#    Stop: $160.00 (-8.8%)
#    R/R: 1:1.26
#
# 2. MSFT - BUY
#    Confidence: 78/100
#    Position: $3,000 (3.0% of portfolio)
#    Shares: 8 @ $380.25
#    Target: $420.00 (+10.5%)
#    Stop: $350.00 (-8.0%)
#    R/R: 1:1.31
#
# Total Allocation: $8,000 (8.0% of portfolio)
# Remaining Cash: $92,000 (92.0%)
```

---

### Feature 2: Timing Recommendations

**Goal:** Recommend when to execute trades.

#### What This Means

```
AAPL - BUY
  Timing: ⚠️ WAIT for pullback
  Current: $175.50
  Ideal Entry: $170-172 (support zone)
  Timeline: 1-5 days

  OR

  Timing: ✅ BUY NOW
  Current: $175.50 (near support)
  Window: Today-Tomorrow
  Urgency: High (breakout forming)
```

#### Implementation

**Four-Gate Framework Integration:**
- Gate 4 (Timing Quality) already evaluates this
- Extend to give specific entry recommendations:
  - "Buy immediately" (at market)
  - "Buy on dip" (wait for pullback to $X)
  - "Buy on breakout" (wait for $X confirmation)
  - "Wait" (timing not optimal)

**Technical Entry Logic:**
```python
def determine_entry_timing(
    current_price: float,
    support_level: float,
    resistance_level: float,
    rsi: float,
    macd_signal: str,
    volume_trend: str
) -> Dict[str, Any]:
    """
    Determine optimal entry timing.

    Returns:
      - action: "BUY_NOW", "WAIT_FOR_DIP", "WAIT_FOR_BREAKOUT", "WAIT"
      - target_entry: Target entry price
      - reasoning: Why this timing
    """

    # Near support + oversold = buy now
    if (current_price <= support_level * 1.02 and rsi < 40):
        return {
            'action': 'BUY_NOW',
            'target_entry': current_price,
            'reasoning': 'At support with oversold RSI'
        }

    # Above resistance = wait for pullback
    if current_price > resistance_level:
        return {
            'action': 'WAIT_FOR_DIP',
            'target_entry': support_level,
            'reasoning': 'Overextended, wait for pullback'
        }

    # Consolidating near breakout = wait for confirmation
    if abs(current_price - resistance_level) < resistance_level * 0.02:
        return {
            'action': 'WAIT_FOR_BREAKOUT',
            'target_entry': resistance_level * 1.01,
            'reasoning': 'Near resistance, wait for breakout'
        }

    # Default
    return {
        'action': 'WAIT',
        'reasoning': 'No clear entry setup'
    }
```

---

### Feature 3: Dividend Tracking

**Goal:** Track dividend income and total returns.

#### What This Means

```
Portfolio Dividend Summary (2024):
  Total Dividends: $3,450
  Yield on Cost: 3.2%

By Ticker:
  AAPL: $450 (1.2% yield)
  MSFT: $380 (1.5% yield)
  V: $220 (0.9% yield)
  ...

Upcoming Dividends (Next 30 Days):
  Nov 20: AAPL - $150 expected
  Dec 5: MSFT - $95 expected
  Dec 12: V - $55 expected
```

#### Implementation

**Database Schema:**
```sql
-- Dividend tracking
CREATE TABLE dividends (
    dividend_id SERIAL PRIMARY KEY,
    ticker_id INTEGER REFERENCES tickers(ticker_id),
    ex_date DATE NOT NULL,
    payment_date DATE,
    amount_per_share DECIMAL(10, 4),
    dividend_type VARCHAR(20), -- 'regular', 'special'
    shares_owned INTEGER,
    total_amount DECIMAL(15, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dividend history (from yfinance)
CREATE TABLE dividend_history (
    history_id SERIAL PRIMARY KEY,
    ticker_id INTEGER REFERENCES tickers(ticker_id),
    ex_date DATE NOT NULL,
    amount DECIMAL(10, 4),
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker_id, ex_date)
);
```

**Fetching Dividend Data:**
```python
def fetch_dividend_history(ticker: str):
    """Fetch dividend history from yfinance."""
    import yfinance as yf

    stock = yf.Ticker(ticker)
    dividends = stock.dividends

    return [
        {
            'ex_date': date,
            'amount': amount
        }
        for date, amount in dividends.items()
    ]

def calculate_dividend_yield(
    ticker: str,
    current_price: float,
    shares_owned: int
) -> Dict[str, Any]:
    """Calculate dividend yield and income."""

    # Get last 12 months of dividends
    dividends = get_dividends_last_12m(ticker)
    annual_dividend = sum(d['amount'] for d in dividends)

    # Yield
    dividend_yield = (annual_dividend / current_price) * 100

    # Annual income projection
    annual_income = annual_dividend * shares_owned

    return {
        'annual_dividend_per_share': annual_dividend,
        'dividend_yield': dividend_yield,
        'projected_annual_income': annual_income
    }
```

**Usage:**
```bash
# Track dividends for portfolio
python -m tradingagents.portfolio dividends

# Output:
# Portfolio Dividend Analysis
# ============================
# Holdings:
#   AAPL: 100 shares @ $175.50
#   MSFT: 50 shares @ $380.00
#   ...
#
# Annual Dividend Income: $3,450
# Average Yield: 3.2%
#
# Upcoming Payments:
#   Nov 20: AAPL - $150
#   Dec 5: MSFT - $95
```

---

### Feature 4: Portfolio Performance Tracking

**Goal:** Track actual vs. expected performance.

#### What This Means

```
Portfolio Performance (Last 6 Months)
====================================

Total Return: +12.5%
  Market Value: $112,500 (was $100,000)
  Dividends: $1,750
  Capital Gains: $10,750

vs. S&P 500: +8.2% (outperformed by 4.3%)

Top Performers:
  1. NVDA: +35.2% (bought Nov 1)
  2. MSFT: +18.5% (bought Oct 15)
  3. AAPL: +15.3% (bought Nov 10)

Underperformers:
  1. XOM: -5.2% (bought Dec 1)

Realized Gains:
  Sold GOOGL: +$2,500 (+12.5%, held 45 days)
  Sold TSLA: -$800 (-4.0%, held 30 days)
```

#### Implementation

**Database Schema:**
```sql
-- Portfolio holdings
CREATE TABLE portfolio_holdings (
    holding_id SERIAL PRIMARY KEY,
    ticker_id INTEGER REFERENCES tickers(ticker_id),
    shares DECIMAL(15, 4),
    avg_cost_basis DECIMAL(10, 2),
    acquisition_date DATE,
    is_open BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trade executions
CREATE TABLE trade_executions (
    execution_id SERIAL PRIMARY KEY,
    ticker_id INTEGER REFERENCES tickers(ticker_id),
    trade_type VARCHAR(10), -- 'BUY', 'SELL'
    shares DECIMAL(15, 4),
    price DECIMAL(10, 2),
    total_value DECIMAL(15, 2),
    execution_date TIMESTAMP NOT NULL,
    related_analysis_id BIGINT REFERENCES analyses(analysis_id),
    notes TEXT
);

-- Performance tracking
CREATE TABLE performance_snapshots (
    snapshot_id SERIAL PRIMARY KEY,
    snapshot_date DATE NOT NULL,
    total_value DECIMAL(15, 2),
    cash_balance DECIMAL(15, 2),
    total_cost_basis DECIMAL(15, 2),
    unrealized_gains DECIMAL(15, 2),
    realized_gains_ytd DECIMAL(15, 2),
    dividend_income_ytd DECIMAL(15, 2),
    benchmark_return DECIMAL(7, 2), -- S&P 500
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Performance Calculation:**
```python
def calculate_portfolio_performance(
    start_date: date,
    end_date: date
) -> Dict[str, Any]:
    """Calculate portfolio performance metrics."""

    # Get holdings at start and end
    start_value = get_portfolio_value(start_date)
    end_value = get_portfolio_value(end_date)

    # Get cash flows (deposits/withdrawals)
    cash_flows = get_cash_flows(start_date, end_date)

    # Calculate time-weighted return
    total_return_pct = ((end_value - start_value) / start_value) * 100

    # Get benchmark (S&P 500)
    sp500_return = get_sp500_return(start_date, end_date)

    # Alpha (excess return vs. benchmark)
    alpha = total_return_pct - sp500_return

    # Get components
    dividends = get_dividend_income(start_date, end_date)
    realized_gains = get_realized_gains(start_date, end_date)
    unrealized_gains = get_unrealized_gains(end_date)

    return {
        'start_value': start_value,
        'end_value': end_value,
        'total_return_pct': total_return_pct,
        'total_return_dollars': end_value - start_value,
        'dividend_income': dividends,
        'realized_gains': realized_gains,
        'unrealized_gains': unrealized_gains,
        'benchmark_return': sp500_return,
        'alpha': alpha
    }
```

---

### Feature 5: Automated Portfolio Rebalancing

**Goal:** Suggest rebalancing actions to maintain target allocations.

#### What This Means

```
Portfolio Rebalancing Recommendation
====================================

Current Allocation:
  Technology: 45% (target: 30%) ⚠️ OVERWEIGHT
  Healthcare: 15% (target: 20%) ✓
  Financial: 10% (target: 15%) ⚠️ UNDERWEIGHT
  Energy: 20% (target: 20%) ✓
  Consumer: 10% (target: 15%) ⚠️ UNDERWEIGHT

Recommended Actions:
  1. TRIM: AAPL - Sell 15 shares ($2,632)
     Reason: Technology overweight, lock in +25% gains

  2. ADD: V - Buy 8 shares ($2,160)
     Reason: Financial underweight, strong fundamentals

  3. ADD: AMZN - Buy 5 shares ($950)
     Reason: Consumer underweight, recent pullback
```

#### Implementation

```python
def generate_rebalancing_plan(
    current_holdings: List[Dict],
    target_allocations: Dict[str, float],
    min_trade_size: float = 500
) -> List[Dict]:
    """
    Generate rebalancing recommendations.

    Args:
        current_holdings: Current portfolio positions
        target_allocations: Target sector allocations (%)
        min_trade_size: Minimum trade size to recommend

    Returns:
        List of rebalancing actions
    """

    actions = []

    # Calculate current sector allocations
    current_allocations = calculate_sector_allocations(current_holdings)

    # Find overweight sectors
    for sector, current_pct in current_allocations.items():
        target_pct = target_allocations.get(sector, 0)
        diff = current_pct - target_pct

        if abs(diff) > 5:  # Rebalance if >5% off target
            if diff > 0:  # Overweight
                # Find positions to trim
                sector_holdings = [h for h in current_holdings
                                  if h['sector'] == sector]
                # Sort by gain % (sell winners first)
                sector_holdings.sort(key=lambda x: x['unrealized_gain_pct'],
                                    reverse=True)

                for holding in sector_holdings:
                    # Calculate trim amount
                    # ... logic to determine how many shares to sell
                    actions.append({
                        'action': 'TRIM',
                        'ticker': holding['symbol'],
                        'shares': shares_to_sell,
                        'value': trim_amount,
                        'reason': f"{sector} overweight by {diff:.1f}%"
                    })

            else:  # Underweight
                # Find positions to add (from recent analysis)
                # ... logic to find good candidates
                pass

    return actions
```

---

## Implementation Roadmap

### Phase 4: Position Sizing & Portfolio Management
**Estimated: 2-3 weeks**

- [ ] Portfolio configuration database tables
- [ ] Position sizing calculator
- [ ] Entry timing recommendations
- [ ] Integration with batch analyzer
- [ ] CLI for portfolio initialization
- [ ] Documentation and testing

### Phase 5: Dividend Tracking
**Estimated: 1-2 weeks**

- [ ] Dividend database tables
- [ ] Dividend data fetcher (yfinance)
- [ ] Dividend income calculator
- [ ] Upcoming dividend calendar
- [ ] CLI for dividend reports
- [ ] Integration with portfolio tracker

### Phase 6: Performance Monitoring
**Estimated: 2-3 weeks**

- [ ] Holdings and trades database tables
- [ ] Performance snapshot system
- [ ] Return calculation (TWR, IRR)
- [ ] Benchmark comparison (S&P 500)
- [ ] Performance reports and charts
- [ ] Win/loss analysis

### Phase 7: Automated Rebalancing
**Estimated: 1-2 weeks**

- [ ] Rebalancing algorithm
- [ ] Sector allocation tracking
- [ ] Rebalancing recommendations
- [ ] Tax-aware selling (FIFO, LIFO)
- [ ] CLI for rebalancing

---

## Usage Examples (Future)

### Complete Workflow

```bash
# 1. Initialize portfolio (one-time)
python -m tradingagents.portfolio init \
  --value 100000 \
  --max-position 10 \
  --risk moderate \
  --sectors "Technology:30,Healthcare:20,Financial:15,Energy:20,Consumer:15"

# 2. Daily morning routine
python -m tradingagents.screener run
python -m tradingagents.analyze.batch_analyze --top 5 --with-sizing

# Output:
# RECOMMENDED POSITIONS:
# 1. AAPL - BUY NOW
#    Shares: 28 @ $175.50 = $4,914
#    Target: $195 (+11.1%, 3-6mo)
#    Stop: $160 (-8.8%)
#
# 2. MSFT - WAIT FOR DIP
#    Ideal Entry: $370-375
#    Current: $380 (wait for pullback)

# 3. Execute trades (manual or via broker API)
python -m tradingagents.portfolio buy AAPL --shares 28 --price 175.50

# 4. Track performance
python -m tradingagents.portfolio performance

# 5. Weekly: Check dividends
python -m tradingagents.portfolio dividends

# 6. Monthly: Rebalancing check
python -m tradingagents.portfolio rebalance
```

---

## Next Steps

**For Now** (Phase 3 Complete):
- Use batch analyzer for top N opportunities
- Manually determine position sizes
- Track trades in spreadsheet
- Monitor performance manually

**Phase 4** (Build Next):
- Position sizing automation
- Entry timing recommendations
- Portfolio configuration

**Let me know when you'd like to proceed with Phase 4!**

---

## Summary: What You Can Do Today

```bash
# 1. Run daily screener
python -m tradingagents.screener run

# 2. Analyze top 5 automatically
python -m tradingagents.analyze.batch_analyze --top 5

# 3. Review recommendations
# (Manual decision on position sizes and timing)

# 4. Execute trades
# (Via your broker)

# 5. Track in spreadsheet
# (Manual performance tracking)
```

**What requires Phase 4+:**
- Automated position sizing ($$ amounts)
- Entry timing recommendations
- Dividend tracking
- Performance monitoring
- Portfolio rebalancing
