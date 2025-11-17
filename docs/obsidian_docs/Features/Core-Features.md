# Core Features

## 1. Multi-Agent Analysis System

### Analyst Team
Four specialized analysts gather and analyze different types of data:

- **Market Analyst**: Technical analysis using MACD, RSI, moving averages, Bollinger Bands
- **Social Analyst**: Sentiment analysis from Reddit and social media
- **News Analyst**: News articles, earnings reports, macroeconomic events
- **Fundamentals Analyst**: Company financials, balance sheets, income statements

### Research Team
- **Bull Researcher**: Argues FOR buying the stock
- **Bear Researcher**: Argues AGAINST buying the stock
- **Research Manager**: Makes final research decision after debate

### Trading Team
- **Trader Agent**: Creates detailed trading plan with entry, size, stop-loss, take-profit

### Risk Management Team
- **Aggressive Analyst**: Argues for higher risk tolerance
- **Conservative Analyst**: Argues for lower risk tolerance
- **Neutral Analyst**: Balanced perspective
- **Portfolio Manager**: Final approval/rejection decision

## 2. Daily Stock Screener

### Features
- Scans 16+ pre-configured tickers
- Technical indicator analysis (RSI, MACD, Bollinger Bands)
- Priority scoring algorithm (0-100)
- Alert system with multiple signal types
- Sector analysis and ranking
- Incremental price data updates

### Commands
```bash
python -m tradingagents.screener run              # Run full scan
python -m tradingagents.screener top 5             # Show top 5
python -m tradingagents.screener report           # Latest report
python -m tradingagents.screener update           # Update prices only
```

## 3. RAG-Enhanced Analysis

### Capabilities
- Historical context retrieval from past analyses
- Similar analysis matching using embeddings
- Pattern recognition across time periods
- Four-Gate decision framework
- Context-aware recommendations

### Benefits
- More informed decisions based on historical patterns
- Faster analysis with context reuse
- Better accuracy through pattern matching

## 4. Portfolio Management

### Features
- Position tracking and monitoring
- Performance calculation
- Dividend tracking and calendar
- Risk-adjusted position sizing
- Portfolio-aware recommendations
- Daily snapshots

### Commands
```bash
python -m tradingagents.portfolio view            # View portfolio
python -m tradingagents.portfolio buy AAPL 10 150  # Buy shares
python -m tradingagents.portfolio performance      # Performance history
python -m tradingagents.portfolio dividends       # Upcoming dividends
```

## 5. Performance Tracking

### Metrics
- Recommendation outcome tracking
- Win rate calculation
- S&P 500 benchmark comparison
- Alpha (excess returns) calculation
- Performance by confidence level

### Commands
```bash
python -m tradingagents.evaluate report           # Performance report
python -m tradingagents.evaluate stats             # Statistics
python -m tradingagents.evaluate update             # Update outcomes
```

## 6. Alerts & Notifications

### Alert Types
- Price alerts (entry/exit/stop-loss)
- RSI-based alerts (oversold/overbought)
- Daily market digest
- Dividend alerts

### Notification Channels
- Terminal output
- Log files
- Email (SMTP)
- Webhook (HTTP POST)

### Commands
```bash
python -m tradingagents.insights morning          # Morning briefing
python -m tradingagents.insights digest           # Daily digest
python -m tradingagents.insights alerts            # Check alerts
```

## 7. Batch Processing

### Features
- Analyze multiple tickers automatically
- Top N screener analysis
- Scheduled daily analysis
- Parallel processing support

### Commands
```bash
python -m tradingagents.analyze.batch_analyze --top 5
```

## 8. Memory System

### ChromaDB Integration
- Financial situation memory storage
- Persistent embeddings
- Historical context retrieval
- Similarity-based search

### Browser
```bash
./browse_chromadb.sh  # Interactive ChromaDB browser
```

## 9. LLM Provider Flexibility

### Supported Providers
- **OpenAI**: GPT-4o, GPT-4o-mini, o1-preview
- **Google Gemini**: gemini-2.0-flash, gemini-2.5-flash
- **Anthropic**: claude-3-5-sonnet, claude-3-5-haiku
- **Ollama**: Local models (llama3.3, llama3.1, etc.)
- **OpenRouter**: Multiple providers

### Configuration
Edit `tradingagents/default_config.py` or use environment variables.

## 10. Data Vendor Options

### Stock Data
- **yfinance**: Free, no API key needed
- **Alpha Vantage**: Requires API key, higher rate limits
- **local**: Tauric TradingDB (in development)

### News Data
- **yfinance**: Basic news
- **Alpha Vantage**: Comprehensive news API
- **google**: Google News
- **local**: Cached news data

---

**Next**: [[Advanced-Features|Advanced Features]] | [[CLI-Commands/Main-CLI|CLI Commands]]

