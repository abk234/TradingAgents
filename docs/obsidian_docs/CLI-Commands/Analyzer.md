# Analyzer CLI - Deep Analysis

## Overview

The analyzer runs comprehensive multi-agent analysis on individual tickers with RAG-enhanced historical context.

## Basic Usage

### Analyze Single Ticker
```bash
python -m tradingagents.analyze AAPL
```

### Analyze with Date
```bash
python -m tradingagents.analyze AAPL --date 2024-01-15
```

### Analyze Multiple Tickers
```bash
python -m tradingagents.analyze AAPL GOOGL MSFT
```

## Options

### Plain English Mode
```bash
python -m tradingagents.analyze AAPL --plain-english --portfolio-value 100000
```

**Features:**
- Simple, easy-to-understand recommendations
- Dollar amount position sizing
- Plain language risk assessment
- Step-by-step instructions

**Perfect for:** Non-technical users

### Without RAG
```bash
python -m tradingagents.analyze AAPL --no-rag
```

Faster but no historical context.

### Verbose Output
```bash
python -m tradingagents.analyze AAPL --verbose
```

Shows full analyst reports and debates.

### Don't Store Results
```bash
python -m tradingagents.analyze AAPL --no-store
```

Runs analysis but doesn't save to database.

### Debug Mode
```bash
python -m tradingagents.analyze AAPL --debug
```

Detailed tracing and logging.

## Batch Analysis

### Analyze Top N from Screener
```bash
python -m tradingagents.analyze.batch_analyze --top 5
```

**What it does:**
1. Gets top 5 from today's screener
2. Runs deep analysis on each
3. Stores results to database
4. Shows summary of all recommendations

**Time:** ~10-25 minutes (5 tickers × 2-5 min each)

**Output:**
```
BUY Signals (2):
  XOM    | Confidence: 85/100 | Screener: #1 (78.5)
  AAPL   | Confidence: 78/100 | Screener: #3 (74.8)

WAIT Signals (2):
  V      | Confidence: 72/100 | Screener: #2 (76.2)
  ...
```

## Analysis Output

### Reports Generated
1. **Market Analysis**: Technical indicators, trends
2. **Social Sentiment**: Reddit/social media sentiment
3. **News Analysis**: Events and market impact
4. **Fundamentals**: Financial metrics and ratios
5. **Research Decision**: Bull vs Bear debate
6. **Trading Plan**: Entry, size, stop-loss, take-profit
7. **Risk Assessment**: Aggressive, Conservative, Neutral views
8. **Final Decision**: Portfolio Manager approval/rejection

### Database Storage
- Analysis results stored in `analyses` table
- Embeddings generated and stored
- Historical context available for future analyses

## RAG Enhancement

When RAG is enabled (default):
- Retrieves similar past analyses
- Matches historical patterns
- Provides context-aware recommendations
- Uses Four-Gate decision framework

## Performance

- **Single Analysis**: 2-5 minutes
- **Batch (5 tickers)**: 10-25 minutes
- **With RAG**: Slightly slower but more accurate
- **Fast Mode**: 60-80% speedup available

---

**Next**: [[Portfolio|Portfolio CLI]] | [[Evaluation|Evaluation CLI]]

