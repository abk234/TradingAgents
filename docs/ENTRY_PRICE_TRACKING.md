# Entry Price Tracking System

## Overview

The Entry Price Tracking system monitors recommended entry prices for stocks over time, allowing you to:
- **Track entry price trends**: See how recommended prices change as market conditions evolve
- **Measure recommendation accuracy**: Determine if recommended prices were actually achieved
- **Identify optimal entry windows**: Understand when the best time to enter was
- **Improve entry algorithms**: Use historical data to refine entry price calculations

## Architecture

### Database Schema

#### Tables

**`daily_scans`** (Enhanced):
- `entry_price_min` - Minimum recommended entry price
- `entry_price_max` - Maximum recommended entry price
- `entry_price_reasoning` - Explanation of the recommendation
- `entry_timing` - Timing recommendation (`BUY_NOW`, `ACCUMULATE`, `WAIT_FOR_PULLBACK`)
- `bb_upper`, `bb_lower`, `bb_middle` - Bollinger Band values at scan time
- `support_level`, `resistance_level` - Calculated support/resistance levels
- `enterprise_value`, `enterprise_to_ebitda`, `market_cap` - Fundamental snapshots

**`entry_price_outcomes`** (New):
Tracks whether entry prices were actually achieved:
- `scan_id` - Links to the original scan recommendation
- `entry_price_min/max` - Recommended entry prices
- `outcome_status` - `HIT_TARGET`, `MISSED_OPPORTUNITY`, `STILL_WAITING`, `STOPPED_OUT`
- `actual_entry_price` - Price actually achieved (if entered)
- `days_to_entry` - Days between recommendation and entry
- `opportunity_score` - Retrospective quality score (0-100)

**`daily_prices`** (Enhanced):
Now includes technical indicators for historical analysis:
- `bb_upper`, `bb_lower`, `bb_middle` - Bollinger Bands
- `macd`, `macd_signal`, `macd_histogram` - MACD indicators
- `volume_ratio` - Volume compared to 20-day average
- `day_return`, `week_return`, `month_return` - Price returns

#### Views

**`entry_price_history`**:
Combines scan data with outcomes for easy trend analysis:
```sql
SELECT * FROM entry_price_history
WHERE symbol = 'AAPL'
ORDER BY scan_date DESC
LIMIT 30;
```

## Entry Price Calculation

Entry prices are calculated using a sophisticated algorithm in `tradingagents/screener/entry_price_calculator.py`:

### Factors Considered

1. **RSI (Relative Strength Index)**:
   - RSI < 30: Oversold → Aggressive entry (BUY_NOW)
   - RSI < 40: Approaching oversold → Good entry (ACCUMULATE)
   - RSI > 70: Overbought → Wait for pullback
   - RSI 40-60: Neutral → Enter near support

2. **Bollinger Bands**:
   - Price below lower band → Good entry opportunity
   - Price near lower band → Entry at or slightly above lower band
   - Price above upper band → Wait for pullback to mid-band

3. **Moving Averages**:
   - MA 50 and MA 200 used as support/resistance levels
   - Entry targets adjusted based on distance from MAs

4. **Enterprise Value Metrics**:
   - EV/Market Cap < 0.9 → 2% discount (undervalued)
   - EV/Market Cap > 1.2 → 3% premium (high debt, wait)
   - EV/EBITDA < 5 → Excellent value, lower entry target
   - EV/EBITDA > 20 → Expensive, wait for better entry

5. **Support/Resistance Levels**:
   - Highest support below current price
   - Lowest resistance above current price
   - Entry range bounded by these levels

### Example Calculation

```
Current Price: $267.46
RSI: 47.1 (neutral)
BB Lower: $252.30
BB Upper: $282.60
Support: $262.11 (MA 50)

Calculation:
- RSI neutral → Target range: current * 0.98 to current * 1.02
- Use support as floor: $262.11 - $272.81
- Timing: ACCUMULATE (not oversold, but near support)
```

## Usage

### Running the Screener with Entry Price Tracking

The screener automatically calculates and stores entry prices:

```bash
# Run full screener
./quick_run.sh screener

# Run for specific tickers
python -m tradingagents.screener.screener
```

Entry prices are automatically:
1. Calculated during each scan
2. Stored in `daily_scans` table
3. Tracked in `entry_price_outcomes` table

### Viewing Entry Price Trends

```bash
# View trends for specific stocks
python scripts/show_entry_price_trends.py AAPL NVDA TSLA

# View trends over custom time period
python scripts/show_entry_price_trends.py AAPL --days 14

# View all recent recommendations
python scripts/show_entry_price_trends.py --all --days 7
```

### Updating Entry Price Outcomes

Entry price outcomes are automatically updated to track if recommended prices were hit:

```python
from tradingagents.database.scan_ops import ScanOperations

scan_ops = ScanOperations()
scan_ops.update_entry_outcomes()
```

This function:
1. Checks all `STILL_WAITING` outcomes
2. Queries daily price data to see if entry price was reached
3. Updates status to `HIT_TARGET` if price went below `entry_price_max`
4. Records actual entry price and days to entry

### Querying Entry Price Data

**Get entry price trends for a ticker:**
```python
from tradingagents.database.scan_ops import ScanOperations

scan_ops = ScanOperations()
trends = scan_ops.get_entry_price_trends(ticker_id=3, days=30)

for trend in trends:
    print(f"{trend['scan_date']}: ${trend['entry_price_min']}-${trend['entry_price_max']}")
```

**Get successful entries:**
```sql
SELECT
    symbol,
    scan_date,
    entry_price_min,
    entry_price_max,
    actual_entry_price,
    days_to_entry,
    entry_discount_pct
FROM entry_price_history
WHERE outcome_status = 'HIT_TARGET'
ORDER BY entry_discount_pct DESC;
```

**Calculate entry accuracy:**
```sql
SELECT
    symbol,
    COUNT(*) as total_recommendations,
    SUM(CASE WHEN outcome_status = 'HIT_TARGET' THEN 1 ELSE 0 END) as hits,
    AVG(days_to_entry) as avg_days_to_entry,
    AVG(entry_discount_pct) as avg_discount
FROM entry_price_history
WHERE scan_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY symbol
HAVING COUNT(*) >= 3
ORDER BY hits DESC;
```

## Understanding Outcomes

### Outcome Statuses

- **`STILL_WAITING`**: Initial status, waiting to see if entry price is hit
- **`HIT_TARGET`**: Price reached the recommended entry range
- **`MISSED_OPPORTUNITY`**: Price never reached entry range (would need manual classification)
- **`STOPPED_OUT`**: Position exited before entry (manual status)

### Entry Discount Percentage

Measures how much better the recommended entry was compared to current price:

```
entry_discount_pct = ((current_price - actual_entry) / current_price) * 100
```

- Positive % = Entry saved money vs. buying at scan time
- Negative % = Entry cost more (missed opportunity)

Example:
- Scan price: $267.46
- Recommended entry: $262.11 - $272.81
- Actual entry: $265.00
- Discount: ((267.46 - 265.00) / 267.46) * 100 = **0.92%** savings

## Integration with Existing Systems

### Screener Integration

Entry price calculation is automatically integrated into `DailyScreener`:

```python
# In tradingagents/screener/screener.py:115-123
entry_data = self.entry_calculator.calculate_entry_price(
    current_price=quote['price'],
    technical_signals=signals,
    quote=quote
)

result = {
    ...
    **entry_data  # Adds all entry price fields
}
```

### Database Integration

Entry prices are stored via `ScanOperations.store_scan_result()`:

```python
scan_id = scan_ops.store_scan_result(
    ticker_id=ticker_id,
    scan_date=date.today(),
    result  # Contains entry_price_min, entry_price_max, etc.
)

# Automatically creates outcome tracker
if entry_price_min:
    scan_ops.create_entry_price_outcome(
        scan_id=scan_id,
        ...
    )
```

## Improvement Opportunities

### 1. Machine Learning Entry Prediction

Use historical entry price outcomes to train ML models:

```python
# Feature engineering from entry_price_history
features = [
    'rsi', 'bb_position', 'ma_alignment',
    'ev_to_ebitda', 'priority_score'
]

target = 'entry_discount_pct'  # How good was the entry?

# Train model to predict optimal entry prices
```

### 2. Alert System

Create alerts when recommended entry prices are hit:

```python
def check_entry_alerts():
    """Alert when stocks hit recommended entry prices."""
    pending = get_pending_entries()

    for entry in pending:
        current_price = get_current_price(entry['symbol'])
        if current_price <= entry['entry_price_max']:
            send_alert(f"{entry['symbol']} hit entry price!")
```

### 3. Backtesting Framework

Test entry price algorithms against historical data:

```python
def backtest_entry_algorithm(algorithm, start_date, end_date):
    """Test entry price algorithm on historical data."""
    results = []

    for scan in historical_scans(start_date, end_date):
        recommended_entry = algorithm(scan)
        actual_low = get_actual_low_after(scan)

        hit = actual_low <= recommended_entry['max']
        results.append({
            'hit': hit,
            'savings': current_price - actual_low if hit else 0
        })

    return calculate_metrics(results)
```

## Best Practices

1. **Run screener daily**: More data points = better trend analysis
2. **Update outcomes regularly**: Run `update_entry_outcomes()` daily to track hits
3. **Review reasoning**: Use `entry_price_reasoning` to understand recommendations
4. **Combine with analysis**: Entry price is one factor - still run full agent analysis
5. **Monitor accuracy**: Track `entry_discount_pct` to measure recommendation quality

## Migration

The system was added via migration `014_add_entry_price_tracking.sql`.

To revert (if needed):
```sql
-- Drop new tables
DROP TABLE IF EXISTS entry_price_outcomes CASCADE;
DROP VIEW IF EXISTS entry_price_history CASCADE;

-- Remove columns from daily_scans
ALTER TABLE daily_scans
DROP COLUMN entry_price_min,
DROP COLUMN entry_price_max,
DROP COLUMN entry_price_reasoning,
DROP COLUMN bb_upper,
DROP COLUMN bb_lower,
DROP COLUMN bb_middle,
DROP COLUMN support_level,
DROP COLUMN resistance_level,
DROP COLUMN enterprise_value,
DROP COLUMN enterprise_to_ebitda,
DROP COLUMN market_cap,
DROP COLUMN entry_timing;
```

## Files Modified/Created

### Created:
- `scripts/migrations/014_add_entry_price_tracking.sql` - Database schema changes
- `tradingagents/screener/entry_price_calculator.py` - Entry price calculation logic
- `scripts/show_entry_price_trends.py` - Trend visualization tool
- `test_entry_price_tracking.py` - Integration test
- `docs/ENTRY_PRICE_TRACKING.md` - This documentation

### Modified:
- `tradingagents/database/scan_ops.py` - Added entry price storage methods
- `tradingagents/screener/screener.py` - Integrated entry price calculation
- Database view `entry_price_history` - Added `entry_price_reasoning` column

## Troubleshooting

**Entry prices not showing up?**
- Check that indicators (RSI, BB) are being calculated
- Verify `technical_signals` dict has required fields
- Check logs for entry calculator errors

**Outcomes always showing STILL_WAITING?**
- Run `scan_ops.update_entry_outcomes()` to update statuses
- Ensure `daily_prices` has data after scan date
- Check that entry prices are realistic (not too far from market)

**Entry prices seem inaccurate?**
- Review `entry_price_reasoning` to understand the logic
- Check if fundamental data (EV/EBITDA) is available
- Verify Bollinger Bands and support levels are correct

## Future Enhancements

1. **Real-time monitoring**: WebSocket alerts when entry prices are hit
2. **Portfolio integration**: Auto-execute trades at entry prices
3. **ML-based prediction**: Train models on outcome data
4. **Risk-adjusted entries**: Factor in portfolio correlation and risk
5. **Multi-timeframe analysis**: Different entry prices for day/swing/position trading
