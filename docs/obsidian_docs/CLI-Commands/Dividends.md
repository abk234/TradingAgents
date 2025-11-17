# Dividends CLI - Dividend Tracking

## Overview

Track upcoming dividends, view dividend calendar, and monitor dividend metrics.

## Commands

### View Dividend Calendar
```bash
python -m tradingagents.dividends calendar --days 90
```

Shows upcoming dividends for next N days.

**Output:**
- Ex-dividend dates
- Payment dates
- Dividend amounts
- Yield percentages

### Update Dividend Calendar
```bash
python -m tradingagents.dividends update-calendar
```

Fetches and updates dividend calendar from data sources.

### View Dividend Metrics
```bash
python -m tradingagents.dividends metrics AAPL
```

Shows dividend metrics for specific ticker:
- Annual dividend
- Dividend yield
- Payout ratio
- Dividend growth rate
- Ex-dividend dates

### Track Dividends
```bash
python -m tradingagents.dividends track
```

Tracks dividends for all portfolio holdings.

## Features

### Dividend Calendar
- Upcoming ex-dividend dates
- Payment dates
- Dividend amounts
- Yield calculations

### Metrics
- Annual dividend rate
- Dividend yield
- Payout ratio
- Growth trends

### Alerts
- Upcoming dividend notifications
- Ex-dividend date reminders
- Payment date alerts

---

**Next**: [[Main-CLI|Main CLI]] | [[Configuration/LLM-Providers|Configuration]]

