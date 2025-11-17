# Analyst Team

## Overview

Four specialized analysts gather and analyze different types of data to provide comprehensive market insights.

## Market Analyst

### Purpose
Analyzes price charts and technical indicators to identify trading patterns and forecast price movements.

### Tools Used
- **MACD** (Moving Average Convergence Divergence): Trend indicator
- **RSI** (Relative Strength Index): Momentum indicator
- **Moving Averages**: Trend identification
- **Bollinger Bands**: Volatility indicator
- **ATR** (Average True Range): Volatility measure
- **VWMA** (Volume Weighted Moving Average): Volume-weighted trend

### Data Sources
- Yahoo Finance
- Alpha Vantage

### Output
Technical analysis report identifying:
- Trend direction (bullish/bearish)
- Support and resistance levels
- Momentum indicators
- Volatility patterns
- Entry/exit signals

## Social Media Analyst

### Purpose
Analyzes social media sentiment (Reddit, Twitter, etc.) to gauge short-term market mood.

### Tools Used
- Sentiment scoring algorithms
- Social media APIs (PRAW for Reddit)
- Text analysis

### Data Sources
- Reddit (via PRAW)
- Social media feeds

### Output
Sentiment report showing:
- Public opinion about the stock
- Market mood (bullish/bearish)
- Social media buzz and discussions
- Sentiment scores

## News Analyst

### Purpose
Monitors news, earnings reports, and macroeconomic events to interpret their impact on market conditions.

### Tools Used
- News aggregation
- Event detection
- Impact assessment

### Data Sources
- Alpha Vantage News
- Google News
- Financial news feeds

### Output
News analysis report highlighting:
- Important events (earnings, product launches, etc.)
- Macroeconomic indicators
- Market-moving news
- Impact assessment

## Fundamentals Analyst

### Purpose
Evaluates company financials and performance metrics, identifying intrinsic values and potential red flags.

### Tools Used
- Balance sheets
- Income statements
- Cash flow statements
- Financial ratios (P/E, P/B, etc.)
- Growth metrics

### Data Sources
- Alpha Vantage
- Yahoo Finance

### Output
Fundamental analysis report evaluating:
- Company financial health
- Valuation metrics
- Growth prospects
- Risk factors
- Competitive position

## Workflow

1. **Parallel Analysis**: All four analysts work in parallel
2. **Data Collection**: Each analyst gathers relevant data
3. **Analysis**: Each analyst performs specialized analysis
4. **Report Generation**: Each analyst generates detailed report
5. **Integration**: Reports passed to Research Team

## Configuration

Analysts can be selectively enabled:
```python
selected_analysts = ["market", "social", "news", "fundamentals"]
```

---

**Next**: [[Research-Team|Research Team]] | [[Trading-Team|Trading Team]]

