# Screener CLI - Daily Stock Screening

## Overview

The screener automatically scans pre-configured tickers, analyzes technical indicators, and identifies top trading opportunities.

## Commands

### Run Daily Screener
```bash
python -m tradingagents.screener run
```

**What it does:**
- Scans all configured tickers (~16 stocks)
- Calculates technical indicators (RSI, MACD, Bollinger Bands)
- Generates priority scores (0-100)
- Identifies trading signals
- Stores results to database

**Time:** ~7-10 seconds for 16 tickers

### Show Top Opportunities
```bash
python -m tradingagents.screener top 5
```

**Output:**
```
==================== TOP 5 OPPORTUNITIES ====================
Scan Date: 2025-01-15

Rank 1: XOM (Energy) - Score: 78.5
  Signals: MACD_BULLISH_CROSS, VOLUME_SPIKE
  RSI: 45.2 | MACD: 1.25 | Volume: 2.1x

Rank 2: V (Financial Services) - Score: 76.2
  Signals: RSI_OVERSOLD
  RSI: 28.5 | MACD: -0.15 | Volume: 1.3x
```

### Show Latest Report
```bash
python -m tradingagents.screener report
```

### Update Price Data Only
```bash
python -m tradingagents.screener update
```

## Options

### Sector Analysis
```bash
python -m tradingagents.screener run --sector-analysis
```

Analyzes sectors and ranks them by strength.

### With Deep Analysis
```bash
python -m tradingagents.screener run --with-analysis --top 3
```

Runs screener, then automatically runs deep analysis on top 3 opportunities.

### Sector-First Analysis
```bash
python -m tradingagents.screener run --sector-first --top-sectors 2 --stocks-per-sector 3
```

Focuses on top sectors first, then analyzes stocks within those sectors.

## Technical Indicators

### Calculated Indicators
- **RSI** (Relative Strength Index): Momentum indicator
- **MACD** (Moving Average Convergence Divergence): Trend indicator
- **Bollinger Bands**: Volatility indicator
- **Volume**: Volume analysis vs average

### Alert Signals
- `RSI_OVERSOLD`: RSI < 30 (potential buy)
- `RSI_OVERBOUGHT`: RSI > 70 (potential sell)
- `MACD_BULLISH_CROSS`: MACD crosses above signal
- `MACD_BEARISH_CROSS`: MACD crosses below signal
- `BB_UPPER_TOUCH`: Price touches upper Bollinger Band
- `BB_LOWER_TOUCH`: Price touches lower Bollinger Band
- `VOLUME_SPIKE`: Volume > 2x average

## Priority Scoring

Scores range from 0-100 based on:
- Technical indicator strength
- Signal presence
- Volume patterns
- Historical performance

## Database Storage

Results are stored in:
- `scan_results` table: Individual scan results
- `tickers` table: Ticker metadata
- `prices` table: Historical price data

---

**Next**: [[Analyzer|Analyzer CLI]] | [[Portfolio|Portfolio CLI]]

