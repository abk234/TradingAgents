# Dividend Income Strategy 💰

## Overview

The **Dividend Income Strategy** is designed for investors who want to live off dividend income. This strategy identifies stocks with high, sustainable dividend yields suitable for generating passive income - perfect for retirees or anyone seeking regular income from their portfolio.

## Strategy Philosophy

This isn't just about finding the highest yields. Living off dividends requires:

1. **Sustainable Income** - High yields that won't get cut
2. **Growth** - Dividends that grow to beat inflation
3. **Safety** - Strong companies with healthy balance sheets
4. **Consistency** - Long track record of paying dividends
5. **Stability** - Lower volatility to preserve capital

## How It Works

### Scoring System (0-100)

The strategy uses a comprehensive scoring system with 5 components:

1. **Yield Score (30%)** - Based on dividend yield
   - 6%+ yield: 30 points (Excellent)
   - 5-6% yield: 27 points (Very Good)
   - 4-5% yield: 24 points (Good)
   - 3-4% yield: 18 points (Moderate)
   - 2-3% yield: 10 points (Low)
   - <2% yield: 0 points (Too Low)

2. **Safety Score (25%)** - Based on payout ratio and financials
   - Payout Ratio <50%: Maximum safety points
   - Payout Ratio 50-60%: Good safety
   - Payout Ratio 60-70%: Reasonable
   - Payout Ratio 70-80%: Elevated risk
   - Payout Ratio >80%: High risk - dividend may be cut
   - Also considers P/E ratio and debt levels

3. **Consistency Score (20%)** - Based on dividend payment history
   - 25+ years: Dividend Aristocrat (20 points)
   - 10-24 years: Strong history (17 points)
   - 5-9 years: Good history (12 points)
   - 3-4 years: Short history (6 points)
   - <3 years: Too risky (0 points)

4. **Growth Score (15%)** - Based on dividend growth rate
   - 10%+ growth: Strong (15 points)
   - 7-10% growth: Good (12 points)
   - 5-7% growth: Moderate (9 points)
   - 3-5% growth: Modest (6 points)
   - 0-3% growth: Low (3 points)
   - Negative growth: Declining (0 points)

5. **Stability Score (10%)** - Based on price volatility
   - Low volatility: Preserves capital (10 points)
   - High volatility: Capital at risk (0 points)

### Income Categories

- **EXCELLENT** (80-100): Top-tier income stocks
- **VERY GOOD** (70-79): High-quality income stocks
- **GOOD** (60-69): Solid income stocks
- **FAIR** (50-59): Acceptable with caution
- **POOR** (<50): Not recommended for income

## Usage

### Basic Usage

```bash
# Find top 20 dividend income stocks
./quick_run.sh dividend-income

# Find top 10 stocks
./quick_run.sh dividend-income --top 10

# Show detailed analysis of top 5 stocks
./quick_run.sh dividend-income --details
```

### Advanced Options

```bash
# Via Python module
venv/bin/python -m tradingagents.screener.dividend_income_main --top 20 --details

# With custom parameters
venv/bin/python -m tradingagents.screener.dividend_income_main \
    --top 20 \
    --min-yield 0.03 \
    --min-years 5 \
    --details
```

## Output

The screener provides:

1. **Main Table** - Top stocks ranked by income score
   - Symbol & Company Name
   - Income Score & Category
   - Dividend Yield
   - Current Price
   - Annual Dividend
   - Years of Consecutive Payments
   - Annual Income per $10,000 invested

2. **Summary Statistics**
   - Average yield
   - Average income score
   - Average income per $10K for top 10 stocks
   - Total opportunities found

3. **Detailed Breakdown** (with --details)
   - Score breakdown for each component
   - Key metrics (payout ratio, P/E, volatility)
   - Income potential at various investment levels
   - Positive factors and warnings

4. **Investment Scenarios**
   - Shows how much income you'd generate at different investment levels
   - Monthly and annual income projections

## Examples

### Example Output (with data)

```
💰 Dividend Income Opportunities - Top Stocks for Living Off Dividends

 #  Symbol  Company             Score  Yield   Price     Annual Div  Years  Income/10K
 1  XYZ     Big Telecom Co      85     5.20%   $45.00    $2.34       15     $520.00
 2  ABC     Utility Power Inc   82     4.80%   $32.50    $1.56       25     $480.00
 3  DEF     REIT Holdings       78     6.10%   $28.00    $1.71       8      $610.00
```

### Investment Scenario Example

If you invest $100,000 in the top stock (5.20% yield):
- Annual Income: $5,200
- Monthly Income: $433.33
- Shares Owned: 2,222

## Strategy in Database

The strategy has been saved to the `trading_strategies` table with:

- **Strategy Name**: Dividend Income
- **Version**: 1
- **Min Dividend Yield**: 2.5%
- **Preferred Dividend Yield**: 4.0%
- **Min Consecutive Years**: 3
- **Min Income Score**: 60
- **Holding Period**: 5+ years
- **Status**: Active (needs backtesting)

## Data Requirements

⚠️ **Important**: This strategy requires dividend data to be populated in the database.

The screener uses the following tables:
- `dividend_yield_cache` - Current dividend yields and metrics
- `dividend_history` - Historical dividend payments
- `tickers` - Stock information

### Populating Dividend Data

You'll need to:

1. **Fetch dividend data** from yfinance or another data source
2. **Calculate dividend metrics** (yield, payout ratio, growth rates)
3. **Update the dividend_yield_cache** table
4. **Set valid_until** timestamp for cache expiration

Example data population script structure:
```python
# Fetch dividend data for each ticker
# Calculate:
#   - Annual dividend
#   - Dividend yield
#   - Payout ratio
#   - Consecutive years paid
#   - Growth rates (1yr, 3yr, 5yr)
# Insert/update dividend_yield_cache
```

## Use Cases

### 1. Retirement Planning
"I need $50,000/year in dividend income. Which stocks should I consider?"

With an average 4% yield from top stocks:
- Required investment: $1,250,000
- Diversified across 10-15 stocks
- Focus on high consistency scores

### 2. Passive Income Generation
"I want to supplement my income with $1,000/month."

Target: $12,000/year
- At 4% yield: $300,000 investment
- At 5% yield: $240,000 investment
- Spread across 8-10 stocks

### 3. FIRE (Financial Independence, Retire Early)
"Building a dividend portfolio to cover living expenses."

- Focus on dividend growth stocks (7%+ growth score)
- High consistency (10+ years)
- Moderate yields (3-5%) with strong growth
- Reinvest dividends during accumulation phase

## Risk Considerations

The strategy accounts for:

1. **Dividend Cut Risk** - Via payout ratio analysis
2. **Financial Stability Risk** - Via debt and earnings analysis
3. **Valuation Risk** - Via P/E ratio
4. **Price Volatility Risk** - Via volatility metrics
5. **Dividend Growth Risk** - Via growth rate analysis

## Best Practices

1. **Diversification** - Spread across 10-20 stocks
2. **Sector Balance** - Avoid concentrating in one sector
3. **Regular Review** - Check quarterly earnings and dividend announcements
4. **Watch Payout Ratios** - Be cautious if ratio exceeds 80%
5. **Reinvest Initially** - Compound growth before taking income
6. **Tax Efficiency** - Consider qualified dividends vs ordinary income

## Next Steps

1. **Populate Dividend Data**
   - Create data fetcher script
   - Schedule regular updates (weekly/monthly)

2. **Run Initial Scan**
   - `./quick_run.sh dividend-income --details`
   - Review top 20 opportunities

3. **Backtest Strategy**
   - Test historical performance
   - Validate scoring system
   - Update strategy as needed

4. **Build Portfolio**
   - Select 10-15 stocks from top results
   - Calculate required investment
   - Implement with dollar-cost averaging

## Related Commands

```bash
# View dividend information for specific ticker
./quick_run.sh dividends

# View portfolio performance
./quick_run.sh portfolio

# View upcoming dividend payments
./quick_run.sh dividends --refresh-data
```

## Technical Details

### Files Created

- `tradingagents/screener/dividend_income.py` - Core screener logic
- `tradingagents/screener/dividend_income_cli.py` - CLI interface
- `tradingagents/screener/dividend_income_main.py` - Module entry point
- `scripts/add_dividend_income_strategy.py` - Database strategy insertion

### Database Integration

The strategy is stored in `trading_strategies` table (ID: 2) and can be:
- Tracked for performance
- Evolved based on results
- Backtested against historical data
- Compared with other strategies

## Support

For issues or questions:
1. Check dividend data is populated: `SELECT COUNT(*) FROM dividend_yield_cache;`
2. Verify table structure: `\d dividend_yield_cache`
3. Review logs for errors
4. Check that migrations 008 and 011 are applied

## Future Enhancements

Potential improvements:
- [ ] Automatic dividend data fetching
- [ ] Tax-aware income calculations
- [ ] Dividend calendar integration
- [ ] Portfolio builder (auto-select diversified portfolio)
- [ ] Backtesting module
- [ ] Risk-adjusted income scoring
- [ ] Sector diversification constraints
