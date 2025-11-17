# Evaluation CLI - Performance Tracking

## Overview

Track recommendation outcomes, calculate performance metrics, and compare against benchmarks.

## Commands

### Performance Report
```bash
python -m tradingagents.evaluate report --period 30
```

**Output includes:**
- Total recommendations
- Win rate
- Average return
- Alpha vs S&P 500
- Performance by confidence level

### Statistics
```bash
python -m tradingagents.evaluate stats
```

Shows detailed statistics:
- Recommendation distribution
- Confidence level breakdown
- Outcome summary
- Benchmark comparison

### Update Outcomes
```bash
python -m tradingagents.evaluate update --days 30
```

Updates existing outcomes with latest price data:
- Fetches current prices
- Calculates returns
- Updates S&P 500 benchmark
- Calculates alpha

### Backfill Historical
```bash
python -m tradingagents.evaluate backfill --days 30
```

Backfills historical recommendations:
1. Creates outcome records from past analyses
2. Updates with price data
3. Updates S&P 500 benchmark
4. Calculates alpha

## Metrics

### Win Rate
Percentage of recommendations that resulted in positive returns.

### Alpha
Excess return vs S&P 500 benchmark. Positive alpha indicates outperformance.

### Confidence-Based Performance
Performance broken down by confidence levels:
- High confidence (80-100)
- Medium confidence (60-79)
- Low confidence (<60)

## Database

Results stored in:
- `recommendation_outcomes` table
- `sp500_benchmark` table
- `performance_analytics` table

---

**Next**: [[Insights|Insights CLI]] | [[Dividends|Dividends CLI]]

