# Portfolio CLI - Portfolio Management

## Overview

Manage your investment portfolio, track positions, monitor performance, and view dividends.

## Commands

### View Portfolio
```bash
python -m tradingagents.portfolio view
```

Shows:
- Current positions
- Total portfolio value
- Individual position values
- Unrealized gains/losses
- Portfolio allocation

### Buy Stock
```bash
python -m tradingagents.portfolio buy AAPL 10 150.50
```

**Arguments:**
- `symbol`: Stock ticker (e.g., AAPL)
- `shares`: Number of shares
- `price`: Price per share
- `--date`: Optional transaction date (YYYY-MM-DD)

### Sell Stock
```bash
python -m tradingagents.portfolio sell AAPL 5 155.00
```

**Arguments:**
- `symbol`: Stock ticker
- `shares`: Number of shares to sell
- `price`: Price per share
- `--date`: Optional transaction date

### View Performance
```bash
python -m tradingagents.portfolio performance --days 30
```

Shows performance history over specified days.

### View Dividends
```bash
python -m tradingagents.portfolio dividends --days 90
```

Shows upcoming dividends for next N days.

### Create Snapshot
```bash
python -m tradingagents.portfolio snapshot
```

Creates a daily snapshot of portfolio state.

## Portfolio ID

Default portfolio ID is 1. To use a different portfolio:
```bash
python -m tradingagents.portfolio view --portfolio-id 2
```

## Features

### Position Tracking
- Automatic position calculation
- Cost basis tracking
- Current value calculation
- Unrealized P&L

### Performance Metrics
- Total portfolio value
- Daily/weekly/monthly returns
- Position-level performance
- Allocation percentages

### Dividend Tracking
- Upcoming dividend dates
- Dividend amounts
- Ex-dividend dates
- Payment dates

---

**Next**: [[Evaluation|Evaluation CLI]] | [[Insights|Insights CLI]]

