# Main CLI - Interactive Analysis Interface

## Overview

The main CLI provides an interactive interface for running comprehensive stock analysis with real-time progress tracking.

## Usage

### Interactive Mode
```bash
python -m cli.main analyze
```

Or using the wrapper script:
```bash
python run.py
```

## Features

### Interactive Selection
1. **Ticker Symbol**: Enter stock ticker (e.g., AAPL, NVDA, TSLA)
2. **Analysis Date**: Select date for analysis (YYYY-MM-DD)
3. **Analyst Selection**: Choose which analysts to include
   - Market Analyst
   - Social Analyst
   - News Analyst
   - Fundamentals Analyst
4. **Research Depth**: Select debate rounds (1-3)
5. **LLM Provider**: Choose provider (OpenAI, Gemini, Anthropic, Ollama)
6. **Thinking Agents**: Select quick and deep thinking models

### Real-Time Display

The CLI provides a rich terminal interface with:

- **Progress Panel**: Shows status of all agents
- **Messages Panel**: Real-time messages and tool calls
- **Analysis Panel**: Current report sections
- **Statistics Footer**: Tool calls, LLM calls, reports generated

### Output

#### Analyst Reports
- Market Analysis (technical indicators)
- Social Sentiment (Reddit/social media)
- News Analysis (events and impact)
- Fundamentals Analysis (financial metrics)

#### Research Team Decision
- Bull Researcher arguments
- Bear Researcher arguments
- Research Manager final decision

#### Trading Plan
- Entry price recommendations
- Position sizing
- Stop-loss and take-profit levels

#### Risk Assessment
- Aggressive Analyst view
- Conservative Analyst view
- Neutral Analyst view
- Portfolio Manager final decision

### Results Storage

Results are saved to:
```
results/{TICKER}/{DATE}/
├── reports/
│   ├── market_report.md
│   ├── sentiment_report.md
│   ├── news_report.md
│   ├── fundamentals_report.md
│   ├── investment_plan.md
│   ├── trader_investment_plan.md
│   └── final_trade_decision.md
└── message_tool.log
```

## Configuration

### Environment Variables
```bash
export OPENAI_API_KEY=your-key
export GOOGLE_API_KEY=your-key
export ALPHA_VANTAGE_API_KEY=your-key
```

### Config File
Edit `tradingagents/default_config.py` for default settings.

## Examples

### Basic Analysis
```bash
python -m cli.main analyze
# Select: AAPL, 2024-01-15, All analysts, Depth 1, OpenAI
```

### With Custom Models
```bash
# Edit default_config.py or use environment variables
python -m cli.main analyze
```

## Non-Interactive Mode

For automated runs, use:
```bash
python run_with_defaults.py
```

This uses predefined defaults (Ollama, llama3.3, etc.)

---

**Next**: [[Screener|Screener CLI]] | [[Analyzer|Analyzer CLI]]

