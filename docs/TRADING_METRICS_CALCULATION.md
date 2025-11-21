# Trading Metrics Calculation Documentation

**Version:** 1.0
**Last Updated:** 2025-11-21
**Status:** Production

## Table of Contents
1. [Overview](#overview)
2. [Core Trading Metrics](#core-trading-metrics)
3. [Entry Price Calculation](#entry-price-calculation)
4. [Target Price Calculation](#target-price-calculation)
5. [Stop Loss Calculation](#stop-loss-calculation)
6. [Gain Percentage Calculation](#gain-percentage-calculation)
7. [Risk/Reward Ratio Calculation](#riskreward-ratio-calculation)
8. [Sorting Logic](#sorting-logic)
9. [Fallback Mechanisms](#fallback-mechanisms)
10. [Examples](#examples)

---

## Overview

The trading system calculates essential metrics to help traders make informed decisions. All calculations are performed during the daily scan and stored permanently in the database.

**Key Principles:**
- Conservative approach to risk management
- Multiple fallback mechanisms to ensure complete data
- Clear, repeatable calculation methodology
- Support for both technical and fundamental analysis

**Location in Codebase:**
- Primary Logic: `tradingagents/screener/entry_price_calculator.py`
- Database Storage: `tradingagents/database/scan_ops.py`
- Display Formatting: `tradingagents/utils/screener_table_formatter.py`

---

## Core Trading Metrics

The system calculates five essential trading metrics for each stock:

| Metric | Purpose | Storage Column | Type |
|--------|---------|----------------|------|
| Entry Price | Optimal buy point | `entry_price_min` | NUMERIC(10,2) |
| Target Price | Profit-taking level | `target` | NUMERIC(10,2) |
| Stop Loss | Risk management exit | `stop_loss` | NUMERIC(10,2) |
| Gain % | Expected profit percentage | `gain_percent` | NUMERIC(6,2) |
| R/R Ratio | Risk/Reward assessment | `risk_reward_ratio` | NUMERIC(6,2) |

All metrics are calculated in `EntryPriceCalculator.calculate_entry_price()` method.

---

## Entry Price Calculation

### Methodology

Entry prices are calculated using institutional-grade indicators:

**Priority 1: VWAP Analysis (Institutional Benchmark)**
```python
if current_price < vwap * 0.995:  # More than 0.5% below VWAP
    entry_min = current_price * 0.99
    entry_max = vwap * 0.998
    timing = 'BUY_NOW'
```

**Priority 2: Volatility Adjustment (ATR)**
```python
if atr_pct > 3.0:
    range_multiplier = 1.5  # High volatility - wider range
elif atr_pct < 1.0:
    range_multiplier = 0.6  # Low volatility - tighter range
```

**Priority 3: Pivot Point Analysis**
```python
if current_price < pivot_s1:
    timing = 'BUY_NOW'  # Below support - oversold
```

**Fallback: RSI Logic**
```python
if rsi < 30:
    entry_min = current_price * 0.97
    entry_max = current_price * 1.00
    timing = 'BUY_NOW'
```

### Output Fields
- `entry_price_min`: Most conservative entry point (floor of buy zone)
- `entry_price_max`: Upper bound of buy zone
- `entry_timing`: One of: BUY_NOW, ACCUMULATE, WAIT_FOR_PULLBACK

### Data Sources
- VWAP (Volume Weighted Average Price)
- ATR (Average True Range)
- Pivot Points (S1, S2, R1, R2)
- RSI (Relative Strength Index)
- Bollinger Bands (Upper, Lower, Middle)
- Moving Averages (MA20, MA50, MA200)

---

## Target Price Calculation

### Formula

```python
if resistance_level and bb_upper:
    target = min(resistance_level, bb_upper)  # More conservative
elif resistance_level:
    target = resistance_level
elif bb_upper:
    target = bb_upper
```

### Logic

The target price uses the **most conservative** (lowest) of:
1. **Resistance Level**: Lowest resistance above current price from:
   - Bollinger Band Upper
   - MA50 (if above price)
   - MA200 (if above price)
   - Pivot R1
   - Pivot R2

2. **Bollinger Band Upper**: Statistical upper bound

**Why Conservative?**
- Increases probability of hitting target
- Reduces false expectations
- Aligns with risk management principles

### Code Location
`entry_price_calculator.py:126-133`

---

## Stop Loss Calculation

### Primary Method (When Support Exists)

```python
if support_level:
    stop_loss = support_level * 0.98  # 2% below support
```

**Support Level Calculation:**
```python
support_candidates = []
if bb_lower and bb_lower < current_price:
    support_candidates.append(bb_lower)
if ma_50 and ma_50 < current_price:
    support_candidates.append(ma_50)
if ma_200 and ma_200 < current_price:
    support_candidates.append(ma_200)
if pivot_s1 and pivot_s1 < current_price:
    support_candidates.append(pivot_s1)

support_level = max(support_candidates)  # Highest support below price
```

### Fallback Method (No Support Level)

```python
elif entry_min:
    stop_loss = entry_min * 0.95  # 5% below entry
```

**When This Happens:**
- Stock price is below all technical indicators
- No clear support level identified
- Common in trending down or oversold stocks

**Why 5%?**
- Conservative risk management
- Allows for normal price volatility
- Prevents premature stop-outs

### Risk Management Principles

1. **Always provide a stop loss** - Never leave traders without risk management
2. **2% below support** - Standard technical analysis practice
3. **5% fallback** - Conservative but realistic for no-support scenarios
4. **Below entry price** - Stop loss is always below entry to protect capital

### Code Location
`entry_price_calculator.py:135-142`

---

## Gain Percentage Calculation

### Formula

```python
if target and entry_min and entry_min > 0:
    gain_percent = ((target - entry_min) / entry_min) * 100
```

### Calculation Details

**Components:**
- `target`: Price target (resistance or BB upper)
- `entry_min`: Most conservative entry point (floor of buy zone)

**Why entry_min?**
- Represents best-case entry scenario
- Maximum potential gain calculation
- Conservative approach to profit expectations

### Interpretation

| Gain % | Assessment |
|--------|-----------|
| > 20% | Excellent opportunity |
| 10-20% | Good opportunity |
| 5-10% | Moderate opportunity |
| 0-5% | Marginal opportunity |
| < 0% | Target below entry (unusual) |

### Display Formatting

```python
if gain_pct >= 20:
    color = "bold green"
elif gain_pct >= 10:
    color = "green"
elif gain_pct >= 5:
    color = "cyan"
elif gain_pct > 0:
    color = "yellow"
else:
    color = "red"
```

### Code Location
`entry_price_calculator.py:144-147`

---

## Risk/Reward Ratio Calculation

### Formula

```python
if stop_loss and entry_min > stop_loss:
    risk = entry_min - stop_loss
    reward = target - entry_min
    if risk > 0:
        risk_reward_ratio = reward / risk
```

### Calculation Details

**Risk (Downside):**
```
Risk = Entry Price (min) - Stop Loss
```
- Amount you could lose per share
- Distance from entry to stop

**Reward (Upside):**
```
Reward = Target Price - Entry Price (min)
```
- Amount you could gain per share
- Distance from entry to target

**Ratio:**
```
R/R Ratio = Reward / Risk
```

### Interpretation

| R/R Ratio | Assessment | Trade Quality |
|-----------|-----------|---------------|
| > 3.0 | Excellent | Professional-grade |
| 2.0-3.0 | Good | Acceptable |
| 1.5-2.0 | Fair | Consider carefully |
| 1.0-1.5 | Marginal | High risk |
| < 1.0 | Poor | Avoid (risk > reward) |

### Professional Standards

**Minimum Standards:**
- Day Trading: 2:1 ratio
- Swing Trading: 3:1 ratio
- Position Trading: 4:1 ratio

**Why This Matters:**
- Professional traders typically require 2:1 minimum
- Accounts for win rate (not all trades win)
- Ensures long-term profitability
- Key risk management metric

### Display Formatting

```python
if rr_val >= 3.0:
    color = "bold green"  # Excellent
elif rr_val >= 2.0:
    color = "green"        # Good
elif rr_val >= 1.5:
    color = "cyan"         # Fair
elif rr_val >= 1.0:
    color = "yellow"       # Marginal
else:
    color = "red"          # Poor
```

### Code Location
`entry_price_calculator.py:148-154`

---

## Sorting Logic

### Display Priority Order

Results are sorted to prioritize actionable opportunities:

```python
def get_recommendation_rank(recommendation: str) -> int:
    """Lower number = higher priority"""
    if "STRONG BUY" in recommendation:
        return 1  # Highest priority
    elif "BUY DIP" in recommendation:
        return 2
    elif "BUY" in recommendation:
        return 3
    elif "ACCUMULATION" in recommendation:
        return 4
    elif "NEUTRAL" or "HOLD" in recommendation:
        return 5
    elif "WAIT" in recommendation:
        return 6
    elif "SELL" in recommendation:
        return 7
    elif "STRONG SELL" in recommendation:
        return 8
    else:
        return 9  # Unknown
```

### Two-Tier Sorting

```python
results.sort(
    key=lambda x: (
        get_recommendation_rank(x['recommendation']),  # Primary: Action
        -x['priority_score']                           # Secondary: Score (desc)
    )
)
```

**Example Output:**
```
1. SLB    - STRONG BUY - Score: 100
2. XEL    - STRONG BUY - Score: 95
3. HAL    - BUY        - Score: 95
4. UPS    - BUY        - Score: 94
...
42. GOOGL - HOLD       - Score: 85
43. XOM   - HOLD       - Score: 83
```

### Benefits

1. **Actionable First**: All BUY recommendations at top
2. **Quality Within Category**: Best BUYs listed first
3. **Clear Separation**: Easy to identify trading opportunities
4. **Consistent**: Same sorting in scans and database queries

### Code Locations
- Scanner: `screener.py:295-328`
- Display: `screener_table_formatter.py:136-161`

---

## Fallback Mechanisms

### 1. Stop Loss Fallback

**Scenario**: No support level identified (price below all indicators)

**Primary Calculation:**
```python
if support_level:
    stop_loss = support_level * 0.98
```

**Fallback Calculation:**
```python
elif entry_min:
    stop_loss = entry_min * 0.95
    logger.debug(f"No support level, using 5% below entry as stop loss")
```

**Why 5%?**
- Conservative risk management
- Typical volatility allowance
- Professional trading standards
- Prevents premature exits

**Real Examples:**
- **BAC**: Entry $51.74 → Stop $49.15 (5% below, no support)
- **WFC**: Entry $83.90 → Stop $79.71 (5% below, no support)
- **MS**: Entry $160.23 → Stop $155.47 (2% below support $158.64)

### 2. Target Price Fallback

**Priority Order:**
```python
if resistance_level and bb_upper:
    target = min(resistance_level, bb_upper)  # Most conservative
elif resistance_level:
    target = resistance_level
elif bb_upper:
    target = bb_upper
elif current_price:
    target = current_price * 1.05  # Fallback: 5% above current
```

### 3. Entry Price Fallback

**Priority Order:**
1. VWAP-based (if available)
2. Pivot Points (if available)
3. RSI-based (if available)
4. Bollinger Bands (if available)
5. Conservative range around current price

**Default Fallback:**
```python
entry_min = current_price * 0.98
entry_max = current_price * 1.02
timing = 'ACCUMULATE'
```

### Design Philosophy

**Multiple Layers of Safety:**
- Primary calculations use optimal technical indicators
- Fallbacks ensure 100% data completeness
- Conservative defaults protect trader capital
- Transparent logging for audit trail

---

## Examples

### Example 1: Standard BUY Signal (With Support)

**Stock: AAPL**

**Input Data:**
- Current Price: $268.00
- Support Level: $265.31 (MA50)
- Resistance Level: $272.01 (BB Upper)
- Entry Min: $266.63
- Entry Max: $268.91

**Calculations:**
```python
# Target: Use resistance level
target = 272.01

# Stop Loss: 2% below support
stop_loss = 265.31 * 0.98 = 260.00

# Gain %
gain_percent = ((272.01 - 266.63) / 266.63) * 100 = 2.02%

# R/R Ratio
risk = 266.63 - 260.00 = 6.63
reward = 272.01 - 266.63 = 5.38
risk_reward_ratio = 5.38 / 6.63 = 0.81
```

**Assessment:**
- Gain: +2.02% (Moderate)
- R/R: 0.81 (Below 1:1, marginal)
- Action: BUY (but lower quality)

---

### Example 2: Excellent Opportunity (High R/R)

**Stock: CAT**

**Input Data:**
- Current Price: $540.00
- Support Level: $540.61
- Resistance Level: $560.13
- Entry Min: $535.21
- Entry Max: $538.00

**Calculations:**
```python
# Target: Use resistance level
target = 560.13

# Stop Loss: 2% below support
stop_loss = 540.61 * 0.98 = 529.80

# Gain %
gain_percent = ((560.13 - 535.21) / 535.21) * 100 = 4.66%

# R/R Ratio
risk = 535.21 - 529.80 = 5.41
reward = 560.13 - 535.21 = 24.92
risk_reward_ratio = 24.92 / 5.41 = 4.61
```

**Assessment:**
- Gain: +4.66% (Good)
- R/R: 4.61 (Excellent - Professional grade!)
- Action: STRONG BUY

---

### Example 3: Fallback Stop Loss (No Support)

**Stock: BAC**

**Input Data:**
- Current Price: $51.50
- Support Level: None (price below all indicators)
- Resistance Level: $51.75
- Entry Min: $51.74
- Entry Max: $51.51

**Calculations:**
```python
# Target: Use resistance level
target = 51.75

# Stop Loss: Fallback (5% below entry, no support available)
stop_loss = 51.74 * 0.95 = 49.15

# Gain %
gain_percent = ((51.75 - 51.74) / 51.74) * 100 = 0.02%

# R/R Ratio
risk = 51.74 - 49.15 = 2.59
reward = 51.75 - 51.74 = 0.01
risk_reward_ratio = 0.01 / 2.59 = 0.00
```

**Assessment:**
- Gain: +0.02% (Very low)
- R/R: 0.00 (Poor - avoid)
- Action: BUY (but very low quality)
- Note: Fallback stop loss used successfully

---

### Example 4: High Volatility Stock

**Stock: NVDA**

**Input Data:**
- Current Price: $181.00
- ATR: 8.5 (High volatility)
- Support Level: $177.25
- Resistance Level: $186.44
- Entry Min: $179.02
- Entry Max: $182.45

**Calculations:**
```python
# Target: Use resistance level
target = 186.44

# Stop Loss: 2% below support
stop_loss = 177.25 * 0.98 = 173.70

# Gain %
gain_percent = ((186.44 - 179.02) / 179.02) * 100 = 4.14%

# R/R Ratio
risk = 179.02 - 173.70 = 5.32
reward = 186.44 - 179.02 = 7.42
risk_reward_ratio = 7.42 / 5.32 = 1.39
```

**Assessment:**
- Gain: +4.14% (Good)
- R/R: 1.39 (Fair, acceptable for volatile stock)
- Action: BUY
- Note: Wider entry range due to high ATR

---

## Validation & Quality Checks

### Data Quality Checks

**Before Calculation:**
```python
if current_price is None or current_price <= 0:
    return empty_result()
```

**After Calculation:**
```python
# Validate stop loss is below entry
if stop_loss and entry_min and stop_loss >= entry_min:
    logger.warning(f"Invalid stop loss {stop_loss} >= entry {entry_min}")

# Validate target is above entry
if target and entry_min and target <= entry_min:
    logger.warning(f"Invalid target {target} <= entry {entry_min}")
```

### Database Constraints

```sql
-- Ensure stop loss is positive
ALTER TABLE daily_scans ADD CONSTRAINT check_stop_loss_positive
    CHECK (stop_loss IS NULL OR stop_loss > 0);

-- Ensure gain_percent is reasonable (-100% to +1000%)
ALTER TABLE daily_scans ADD CONSTRAINT check_gain_percent_range
    CHECK (gain_percent IS NULL OR (gain_percent >= -100 AND gain_percent <= 1000));
```

---

## Monitoring & Logging

### Debug Logging

```python
logger.debug(f"Calculated metrics for {symbol}:")
logger.debug(f"  Entry: ${entry_min:.2f} - ${entry_max:.2f}")
logger.debug(f"  Target: ${target:.2f}")
logger.debug(f"  Stop: ${stop_loss:.2f}")
logger.debug(f"  Gain: {gain_percent:.2f}%")
logger.debug(f"  R/R: {risk_reward_ratio:.2f}")
```

### Performance Tracking

Track accuracy of calculations:
- Target hit rate
- Stop loss hit rate
- Average time to target
- Win/loss ratio by R/R tier

**Future Enhancement:**
Create `entry_price_outcomes` table to track prediction accuracy.

---

## References

### Technical Analysis Sources
- **VWAP**: Standard institutional benchmark
- **ATR**: J. Welles Wilder, "New Concepts in Technical Trading Systems"
- **Pivot Points**: Floor trader method
- **Bollinger Bands**: John Bollinger
- **RSI**: J. Welles Wilder

### Risk Management Standards
- **2:1 R/R Minimum**: Professional trading standard
- **2% Stop Below Support**: Technical analysis best practice
- **Position Sizing**: Based on stop loss distance

### Code References
- `tradingagents/screener/entry_price_calculator.py`: Core calculation logic
- `tradingagents/database/scan_ops.py`: Database storage
- `tradingagents/utils/screener_table_formatter.py`: Display formatting
- `database/migrations/001_add_trading_metrics.sql`: Schema definition

---

## Version History

### Version 1.0 (2025-11-21)
- Initial documentation
- Core metric calculations defined
- Fallback mechanisms implemented
- Sorting logic documented
- Examples added

### Future Enhancements
- Machine learning for dynamic stop loss adjustment
- Multi-timeframe analysis integration
- Sentiment-based adjustment factors
- Backtesting framework for validation
- Real-time adjustment based on market conditions

---

## Support & Questions

For questions about trading metric calculations:
1. Review this documentation
2. Check code comments in `entry_price_calculator.py`
3. Review unit tests in `tests/test_entry_price_calculator.py`
4. Contact development team

**Last Updated:** 2025-11-21
**Maintained By:** Trading System Development Team
