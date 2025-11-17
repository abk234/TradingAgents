# TradingAgents Feature Overview

## 🎯 What is TradingAgents?

TradingAgents is a sophisticated multi-agent AI system that simulates a real-world trading firm. It uses multiple specialized AI agents that work together to analyze stocks and make trading decisions, just like a professional trading desk.

## 🏗️ Architecture

The framework decomposes complex trading tasks into specialized roles, ensuring a robust, scalable approach to market analysis and decision-making.

### Five-Stage Analysis Process

1. **Analyst Team** → Data Collection & Analysis
2. **Research Team** → Bull/Bear Debate
3. **Trader Agent** → Trading Strategy Creation
4. **Risk Management Team** → Risk Assessment
5. **Portfolio Manager** → Final Decision

## ✨ Key Features

### 1. Multi-Agent Analysis System
- **4 Specialized Analysts**: Market, Social, News, Fundamentals
- **Research Team**: Bull and Bear researchers with debate system
- **Trader Agent**: Creates detailed trading plans
- **Risk Management**: 3 risk analysts (Aggressive, Conservative, Neutral)
- **Portfolio Manager**: Final approval/rejection authority

### 2. LLM Provider Support
- **OpenAI**: GPT-4o, GPT-4o-mini, o1-preview, o3-mini
- **Google Gemini**: gemini-2.0-flash, gemini-2.5-flash
- **Anthropic Claude**: claude-3-5-sonnet, claude-3-5-haiku
- **Ollama**: Local models (llama3.3, llama3.1, mistral, etc.)
- **OpenRouter**: Access to multiple providers

### 3. Data Sources
- **Stock Data**: yfinance, Alpha Vantage
- **Technical Indicators**: RSI, MACD, Bollinger Bands, ATR, VWMA
- **Fundamentals**: Balance sheets, income statements, cash flow
- **News**: Alpha Vantage News, Google News
- **Social Media**: Reddit sentiment analysis

### 4. Daily Stock Screener
- Scans 16+ pre-configured tickers
- Technical indicator analysis
- Priority scoring (0-100)
- Alert system (RSI_OVERSOLD, BB_UPPER_TOUCH, etc.)
- Sector analysis

### 5. RAG-Enhanced Analysis
- Historical context retrieval
- Similar analysis matching
- Pattern recognition
- Four-Gate decision framework
- Embedding-based similarity search

### 6. Portfolio Management
- Position tracking
- Performance monitoring
- Dividend tracking
- Risk-adjusted allocations
- Portfolio-aware recommendations

### 7. Performance Tracking
- Recommendation outcome tracking
- Win rate calculation
- S&P 500 benchmark comparison
- Alpha (excess returns) calculation
- Performance analytics by confidence level

### 8. Alerts & Notifications
- Daily market digest
- Price alerts (entry/exit/stop-loss)
- RSI-based alerts (oversold/overbought)
- Multi-channel notifications (terminal, log, email, webhook)

### 9. Batch Processing
- Analyze multiple tickers automatically
- Top N screener analysis
- Scheduled daily analysis
- Automated evaluation

### 10. Memory System
- ChromaDB for financial situation memory
- Persistent embeddings
- Historical context storage
- Similarity-based retrieval

## 📊 Output Capabilities

### Analysis Reports
- **Market Analysis**: Technical indicators, trends, support/resistance
- **Social Sentiment**: Public opinion, market mood, sentiment scores
- **News Analysis**: Important events, earnings, macroeconomic indicators
- **Fundamentals**: Financial metrics, P/E ratios, growth indicators

### Trading Recommendations
- **Buy/Sell/Hold** decisions with reasoning
- **Entry/Exit** price recommendations
- **Position sizing** based on confidence
- **Stop-loss** and **take-profit** levels
- **Risk assessment** and portfolio impact

### Performance Metrics
- Win rate statistics
- Alpha vs S&P 500
- Confidence-based performance
- Historical recommendation tracking

## 🔧 Technical Features

### Configuration
- Flexible LLM provider switching
- Customizable debate rounds
- Configurable data vendors
- Environment-based settings

### CLI Interface
- Interactive analysis interface
- Rich terminal output
- Real-time progress tracking
- Comprehensive reporting

### Database Integration
- PostgreSQL with pgvector
- Analysis storage
- Portfolio tracking
- Performance metrics

### Extensibility
- Modular agent architecture
- Custom tool integration
- Plugin system
- API for programmatic use

## 🎓 Use Cases

1. **Stock Analysis**: Comprehensive multi-perspective analysis
2. **Trading Decisions**: AI-powered buy/sell/hold recommendations
3. **Portfolio Management**: Track and optimize investments
4. **Research**: Learn trading firm workflows
5. **Backtesting**: Historical analysis and evaluation
6. **Education**: Understand multi-agent AI systems

## 📈 Performance

- **Screener**: 16 tickers in ~7-10 seconds
- **Deep Analysis**: 2-5 minutes per ticker
- **Batch Analysis**: 10-25 minutes for 5 tickers
- **RAG Enhancement**: 60-80% speedup with fast mode

---

**Next**: [[Core-Features|Core Features]] | [[Agents/Analyst-Team|Analyst Team]]

