# Product Requirements Document (PRD): Eddie AI Trading Assistant

**Version:** 1.0  
**Date:** November 2025  
**Status:** Production Ready

---

## Executive Summary

**Eddie** is an intelligent, conversational AI trading assistant that orchestrates a team of specialized agents to provide comprehensive stock market analysis, investment recommendations, and trading insights. Eddie combines multi-agent orchestration, memory and learning capabilities, multi-source data validation, and strategic intelligence to help users make informed trading decisions.

**Key Value Proposition:**
- **Advisory Intelligence**: Provides BUY/SELL/HOLD recommendations with confidence scores
- **Multi-Agent Orchestration**: Coordinates 8 specialized AI agents for comprehensive analysis
- **Learning & Memory**: Remembers past analyses and improves over time
- **Data Validation**: Multi-source validation ensures credibility and trustworthiness
- **Speed Flexibility**: Quick checks (5-15 seconds) or full analysis (30-90 seconds)

**Important Disclaimer:** Eddie provides investment analysis and recommendations only. It does NOT execute trades or connect to brokers. Users execute trades manually through their own brokerage accounts.

---

## 1. Product Overview

### 1.1 Product Name
**Eddie** - AI Trading Expert

### 1.2 Product Type
Conversational AI Assistant for Stock Market Analysis and Trading Advisory

### 1.3 Target Users
- Individual retail traders
- Investment enthusiasts
- Portfolio managers seeking AI-assisted analysis
- Traders looking for comprehensive market insights

### 1.4 Core Architecture
- **LLM Backend**: llama3.3 (70B parameters) via Ollama (configurable)
- **Framework**: LangGraph with ReAct agent pattern
- **Database**: PostgreSQL with 110+ actively tracked stocks
- **UI**: Chainlit web interface (http://localhost:8000)
- **Memory System**: RAG (Retrieval-Augmented Generation) with vector embeddings

---

## 2. Core Features & Capabilities

### 2.1 Multi-Agent Orchestration System

Eddie orchestrates **8 specialized AI agents** to provide comprehensive analysis:

#### 2.1.1 Analyst Agents
1. **Market Analyst** (Technical Analysis)
   - Analyzes charts, technical indicators (MACD, RSI, Bollinger Bands, Moving Averages)
   - Identifies trends, support/resistance levels, momentum
   - Speed: ~15-20 seconds for full analysis

2. **News Analyst** (News & Sentiment)
   - Monitors recent news, market-moving events
   - Analyzes news sentiment and impact
   - Speed: ~10-15 seconds for full analysis

3. **Social Media Analyst** (Community Sentiment)
   - Analyzes Reddit (r/wallstreetbets, r/stocks), Twitter trends
   - Gauges retail investor sentiment
   - Speed: ~10-15 seconds for full analysis

4. **Fundamentals Analyst** (Company Financials)
   - Evaluates P/E ratios, earnings, revenue, balance sheets
   - Assesses company financial health and valuation
   - Speed: ~15-20 seconds for full analysis

#### 2.1.2 Research Agents
5. **Bull Researcher** (Bullish Case)
   - Builds comprehensive bullish arguments
   - Identifies reasons why stock could go UP
   - Speed: ~10-15 seconds

6. **Bear Researcher** (Bearish Case)
   - Builds comprehensive bearish arguments
   - Identifies risks and reasons to avoid
   - Speed: ~10-15 seconds

#### 2.1.3 Management Agents
7. **Research Manager** (Synthesis)
   - Coordinates all analyst findings
   - Synthesizes comprehensive view from all agents
   - Speed: ~5-10 seconds

8. **Risk Manager** (Position Sizing & Risk)
   - Assesses portfolio risk
   - Calculates position sizing recommendations
   - Determines stop-loss levels
   - Speed: ~5-10 seconds

**Orchestration Flow:**
```
User Request → Eddie → Parallel Agent Activation → 
Bull/Bear Debate → Research Manager Synthesis → 
Risk Manager Assessment → Comprehensive Recommendation
```

**Total Analysis Time:** 30-90 seconds for full orchestration

---

### 2.2 Market Screening & Discovery

#### 2.2.1 Daily Market Screener
- **Function**: Scans all 110+ stocks in database in real-time
- **Output**: Top opportunities ranked by priority score (0-100)
- **Speed**: 10-30 seconds
- **Features**:
  - Sector strength analysis
  - Buy signal detection (MACD, RSI, Volume, Bollinger Bands)
  - Momentum assessment
  - Priority score calculation (T+V+M+F components)

#### 2.2.2 Top Stock Finder
- **Function**: Retrieves top opportunities from latest scan
- **Features**:
  - Customizable limit (default: 10)
  - Minimum score filtering
  - Sector-based filtering
  - Alert detection

#### 2.2.3 Sector Analyzer
- **Function**: Analyzes sector-level trends and strength
- **Output**: Sector strength scores (0-100%), momentum, buy signals
- **Use Cases**: Sector rotation strategies, sector-focused investing

#### 2.2.4 Stock Search
- **Function**: Search stocks by symbol, name, or sector
- **Features**: Fuzzy matching, partial search support

---

### 2.3 Deep Stock Analysis

#### 2.3.1 Comprehensive Stock Analysis (`analyze_stock`)
- **Function**: Full multi-agent orchestration for comprehensive analysis
- **Output**:
  - BUY/SELL/HOLD recommendation
  - Confidence score (0-100%)
  - Entry price recommendation
  - Stop-loss level
  - Position sizing suggestion (% of portfolio)
  - Expected return timeframe
  - Bull case summary
  - Bear case summary
  - Risk assessment
- **Speed**: 30-90 seconds
- **Use Cases**: Investment decisions, position entry/exit planning

#### 2.3.2 Stock Summary
- **Function**: Quick overview of stock metrics and status
- **Speed**: 5-10 seconds
- **Output**: Current price, priority score, key metrics, recent alerts

---

### 2.4 Quick Single-Agent Checks (Phase 3 Part 2)

Fast access to individual agents for specific questions (5-15 seconds each):

#### 2.4.1 Quick Technical Check (`quick_technical_check`)
- **Agent**: Market Analyst only
- **Use When**: "What's the chart looking like?" "Is it in an uptrend?"
- **Output**: Charts, indicators, trends, support/resistance
- **Speed**: 5-10 seconds

#### 2.4.2 Quick News Check (`quick_news_check`)
- **Agent**: News Analyst only
- **Use When**: "What's the news?" "Any recent headlines?"
- **Output**: Recent news, events, sentiment
- **Speed**: 5-15 seconds

#### 2.4.3 Quick Sentiment Check (`quick_sentiment_check`)
- **Agent**: Social Media Analyst only
- **Use When**: "What's Reddit saying?" "Community sentiment?"
- **Output**: Reddit/Twitter sentiment, social buzz
- **Speed**: 5-10 seconds

#### 2.4.4 Quick Fundamentals Check (`quick_fundamentals_check`)
- **Agent**: Fundamentals Analyst only
- **Use When**: "Show me the financials" "Is it profitable?"
- **Output**: P/E, earnings, revenue, margins
- **Speed**: 5-10 seconds

**Decision Tree:**
- Specific question → Use quick check (5-15 sec)
- Comprehensive recommendation → Use full analysis (30-90 sec)

---

### 2.5 Learning & Memory System (Phase 3 Part 3)

Eddie has **MEMORY** and can **LEARN** from past analyses:

#### 2.5.1 Past Performance Tracking (`check_past_performance`)
- **Function**: Reviews Eddie's own past recommendations
- **Output**:
  - Historical recommendations for ticker
  - Confidence levels from past analyses
  - Track record (win rate, returns)
  - Accuracy metrics
- **Use Cases**: "What did you say about AAPL before?" "Show me your track record"

#### 2.5.2 Pattern Recognition (`find_similar_situations`)
- **Function**: RAG-powered pattern recognition using vector embeddings
- **Output**: Similar stocks with comparable setups from past analyses
- **Technology**: Vector similarity search on past analysis embeddings
- **Use Cases**: "Have I seen this pattern before?" "Find similar situations"

#### 2.5.3 Learning Summary (`what_did_i_learn`)
- **Function**: Shows what Eddie learned from past analyses
- **Output**:
  - Analysis count for ticker
  - Average confidence level
  - Insights gained
  - Prediction accuracy
- **Use Cases**: "What do you know about this stock?" "What did you learn?"

**Learning Workflow:**
```
Before Analysis → Check Past Learning → 
Find Similar Patterns → Run Analysis → 
Store Insights → Improve Future Recommendations
```

---

### 2.6 Data Intelligence & Strategic Dashboard (Phase 3 Part 4)

#### 2.6.1 Data Dashboard (`show_data_dashboard`)
- **Function**: Comprehensive database intelligence and strategic planning
- **Output**:
  1. **Watchlist Overview**: Stock count, sectors, market coverage
  2. **Scan Status**: Latest scan date, coverage %, data freshness level
  3. **Analysis History**: Analysis count, RAG context availability
  4. **Top 5 Opportunities**: Best stocks based on latest data
  5. **Data Quality Issues**: Gaps, staleness, missing coverage
  6. **Strategic Recommendations**: AI-generated next steps based on data state

**Freshness Levels:**
- 🟢 **FRESH** (< 4 hours): Data is current, ready for analysis
- 🟡 **MODERATE** (4-12 hours): Data is recent, acceptable for analysis
- 🟠 **STALE** (12-24 hours): Data is aging, recommend refresh
- 🔴 **VERY STALE** (> 24 hours): Data is outdated, strongly recommend refresh

**Use Cases**: "What data do you have?" "What should I analyze next?" "Is the data fresh?"

---

### 2.7 Data Validation & Credibility System

Eddie provides **comprehensive multi-source validation** for maximum trustworthiness:

#### 2.7.1 Data Quality Check (`check_data_quality`)
- **Function**: Shows data freshness, sources used, validation score (0-10)
- **Output**:
  - Data age (hours since last update)
  - Sources used (yfinance, Alpha Vantage, etc.)
  - Validation score (0-10)
  - Data completeness metrics

#### 2.7.2 Price Source Validation (`validate_price_sources`)
- **Function**: Cross-validates prices between yfinance + Alpha Vantage
- **Output**:
  - Price from yfinance
  - Price from Alpha Vantage
  - Discrepancy percentage
  - Validation confidence score (0-10)
- **Use Cases**: Before trading, verify price accuracy

#### 2.7.3 Earnings Risk Detection (`check_earnings_risk`)
- **Function**: Warns about earnings proximity and volatility risk
- **Output**:
  - Days until next earnings
  - Risk level (LOW/MEDIUM/HIGH)
  - Recommendation (AVOID if <7 days)
- **Use Cases**: Avoid entering positions before earnings announcements

#### 2.7.4 News Multi-Source Validation (`validate_news_multi_source`)
- **Function**: Cross-validates news sentiment across multiple sources
- **Output**: Sentiment consistency score, source agreement level
- **Use Cases**: Verify news reliability before making decisions

**Validation Workflow (CRITICAL):**
```
1. Run analysis (analyze_stock or run_screener)
2. Check earnings risk (ALWAYS before recommendations)
3. Validate price sources (for key stocks)
4. Check data quality (for additional context)
5. Present recommendation WITH full validation context
```

---

### 2.8 Portfolio Management

#### 2.8.1 Portfolio Status (`get_portfolio_status`)
- **Function**: Shows current portfolio holdings and status
- **Output**: Holdings, positions, performance, allocation
- **Status**: Placeholder/In Development

#### 2.8.2 Position Sizing Recommendations
- **Function**: Risk Manager provides position sizing advice
- **Guidelines**:
  - 70-100% confidence: 5-7% of portfolio
  - 50-69% confidence: 3-5% of portfolio
  - 40-49% confidence: 1-3% of portfolio
  - <40% confidence: <1% of portfolio
- **Rule**: Never risk more than 10% per position

---

### 2.9 Educational & Explanatory Features

#### 2.9.1 Metric Explainer (`explain_metric`)
- **Function**: Explains trading concepts and metrics
- **Examples**: Priority score, sector strength, momentum, MACD, RSI, etc.
- **Output**: Clear, educational explanations with examples

#### 2.9.2 Screener Legend (`show_legend`)
- **Function**: Complete guide to screener metrics
- **Output**: Explanation of all scoring systems, signals, and interpretations

#### 2.9.3 Agent Explanation (`explain_agents`)
- **Function**: Describes Eddie's specialized agent team
- **Output**: Role and capabilities of each agent

---

### 2.10 Market Data & Information

#### 2.10.1 Stock Information (`get_stock_info`)
- **Function**: Retrieves basic stock information
- **Output**: Company name, sector, current price, key metrics

#### 2.10.2 Real-Time Database
- **Coverage**: 110+ actively tracked stocks
- **Update Frequency**: Daily scans stored in database
- **Sectors**: 13+ sectors tracked
- **Data Types**: Prices, technical indicators, fundamentals, news

---

## 3. User Interface & Experience

### 3.1 Web Interface
- **Technology**: Chainlit
- **URL**: http://localhost:8000
- **Features**:
  - Natural language chat interface
  - Conversation history
  - Real-time responses
  - Tool execution visibility

### 3.2 Conversation Style
- **Natural Language**: Users can ask questions conversationally
- **Examples**:
  - "What stocks should I look at today?"
  - "Analyze AAPL for me"
  - "Should I buy NVDA? My portfolio is $100k"
  - "What's the news on TSLA?"
  - "Show me TSLA's technicals"

### 3.3 Response Characteristics
- **Clear and Concise**: No unnecessary jargon
- **Actionable**: Always provides next steps
- **Honest**: Admits when conditions aren't ideal
- **Educational**: Explains WHY, not just WHAT
- **Professional**: Maintains analyst credibility

---

## 4. Priority Score System

### 4.1 Score Components (T+V+M+F)
- **T (Technical)**: MACD, RSI, chart patterns, indicators
- **V (Volume)**: Trading activity signals, volume spikes
- **M (Momentum)**: Trend strength and direction
- **F (Fundamental)**: P/E ratios, earnings, growth metrics

### 4.2 Score Interpretation

| Score Range | Interpretation        | Action                          |
|-------------|------------------------|---------------------------------|
| 60-100      | Strong buy candidate   | Act with confidence             |
| 50-59       | Good buy signal        | Proceed after due diligence     |
| 40-49       | Moderate opportunity   | Investigate further             |
| 30-39       | Weak signal            | Be cautious                     |
| 0-29        | No signal              | Avoid                           |

### 4.3 Sector Strength (0-100%)
- **>40%**: Strong sector with good opportunities
- **20-40%**: Neutral sector with moderate opportunities
- **<20%**: Weak sector - few opportunities

### 4.4 Momentum Levels
- **Strong**: Clear uptrend + increasing volume (Bullish)
- **Neutral**: Sideways movement (Wait and see)
- **Weak**: Downtrend or declining volume (Bearish)

---

## 5. Performance & Speed

### 5.1 Response Times

| Operation Type          | Speed        | Use Case                    |
|-------------------------|--------------|-----------------------------|
| Quick Checks            | 5-15 seconds | Specific questions          |
| Market Screener         | 10-30 seconds| Market overview             |
| Full Stock Analysis      | 30-90 seconds| Investment decisions        |
| Data Dashboard          | 5-10 seconds | Strategic planning          |
| Validation Checks        | 5-10 seconds | Pre-trade verification      |

### 5.2 Optimization Strategies
- **Quick Checks**: Use single agents for fast answers
- **Full Analysis**: Use multi-agent orchestration for comprehensive recommendations
- **Database Caching**: Pre-scanned data stored in PostgreSQL
- **Parallel Processing**: Agents run in parallel when possible

---

## 6. Data Sources & Validation

### 6.1 Primary Data Sources
- **yfinance**: Stock prices, technical indicators
- **Alpha Vantage**: Fundamental data, news data
- **PostgreSQL Database**: Pre-scanned data, historical analyses

### 6.2 Multi-Source Validation
- **Price Validation**: Cross-check yfinance vs Alpha Vantage
- **News Validation**: Multi-source sentiment consistency
- **Data Freshness**: Real-time freshness tracking
- **Quality Scoring**: 0-10 validation scores

### 6.3 Data Quality Standards
- **Fresh Data**: < 4 hours old (FRESH)
- **Acceptable Data**: 4-12 hours old (MODERATE)
- **Stale Data**: 12-24 hours old (STALE) - refresh recommended
- **Very Stale**: > 24 hours old (VERY STALE) - refresh required

---

## 7. Risk Management & Safety

### 7.1 Risk Warnings
Eddie proactively warns about:
- ⚠️ Earnings proximity (<7 days)
- ⚠️ Weak market conditions (all sectors <30%)
- ⚠️ Low data quality (<6/10)
- ⚠️ Price discrepancies (>1%)
- ⚠️ Low confidence recommendations (<40%)

### 7.2 Conservative Approach
- **Philosophy**: Better to miss opportunity than lose money
- **Recommendations**: Always includes risk assessment
- **Position Sizing**: Conservative sizing guidelines
- **Stop Losses**: Always recommends stop-loss levels

### 7.3 Red Flags - Don't Trade If:
- Earnings in <7 days
- Data quality <6/10
- Price validation <7/10
- Confidence <40%
- Sector strength <20%
- All sectors <30% (sideways market)

---

## 8. Technical Specifications

### 8.1 System Requirements
- **Python**: 3.13+
- **Database**: PostgreSQL
- **LLM**: Ollama with llama3.3 (70B) or configurable
- **Dependencies**: See `requirements.txt`

### 8.2 Architecture Components
```
User Browser (Chainlit UI)
    ↓
Eddie (LangGraph Agent)
    ↓
Tool Orchestration Layer
    ↓
Specialized Agents (8 agents)
    ↓
Data Layer (PostgreSQL + APIs)
```

### 8.3 Key Files
- `tradingagents/bot/agent.py`: Main agent implementation
- `tradingagents/bot/tools.py`: All available tools (25+ tools)
- `tradingagents/bot/prompts.py`: Eddie's personality and knowledge
- `tradingagents/bot/chainlit_app.py`: Web UI interface

---

## 9. Feature Roadmap & Evolution

### 9.1 Completed Features (Phase 1-3)
- ✅ Multi-agent orchestration (8 agents)
- ✅ Market screening and discovery
- ✅ Deep stock analysis with recommendations
- ✅ Quick single-agent checks
- ✅ Learning & memory system (RAG)
- ✅ Data validation (multi-source)
- ✅ Data intelligence dashboard
- ✅ Portfolio management (basic)

### 9.2 Future Enhancements (Planned)
- [ ] Voice interaction (speech-to-text)
- [ ] Mobile app companion
- [ ] Portfolio optimization algorithms
- [ ] Automated trading signal alerts
- [ ] Multi-user support with authentication
- [ ] Historical backtesting integration
- [ ] Additional specialized agents (options, crypto, forex)
- [ ] Fine-tuning on historical trading outcomes
- [ ] Reinforcement learning from user feedback
- [ ] Advanced charting and visualization

---

## 10. Usage Examples & Workflows

### 10.1 Morning Routine
```
1. "What data do you have?" → Check freshness
2. "What are the best stocks right now?" → Run screener
3. Quick checks on top picks → News, technicals (10 sec each)
```

### 10.2 Pre-Trade Workflow
```
1. "Should I buy NVDA? Portfolio $100k" → Full analysis (60 sec)
2. "Check earnings risk for NVDA" → Validate (5 sec)
3. "Validate price sources for NVDA" → Verify (5 sec)
4. Execute trade → In user's broker
```

### 10.3 Learning & Pattern Recognition
```
1. "What did you learn about AAPL?" → Check memory
2. "Have you seen this pattern before?" → Find similar situations
3. "What did you say about TSLA last time?" → Track record
```

### 10.4 Strategic Planning
```
1. "What data do you have?" → Data dashboard
2. "What should I analyze next?" → Strategic recommendations
3. Analyze top opportunities → Full analysis
```

---

## 11. Success Metrics

### 11.1 User Engagement
- Response time satisfaction (quick checks <15 sec, full analysis <90 sec)
- Conversation depth (average messages per session)
- Tool usage diversity (variety of tools used)

### 11.2 Analysis Quality
- Recommendation accuracy (tracked via `check_past_performance`)
- Confidence calibration (confidence vs actual outcomes)
- Win rate tracking (30/60/90 day returns)

### 11.3 Data Quality
- Data freshness (target: >80% FRESH)
- Validation scores (target: >8/10 average)
- Multi-source agreement (target: >95% price agreement)

---

## 12. Limitations & Disclaimers

### 12.1 Trading Limitations
- **Does NOT execute trades**: Eddie provides recommendations only
- **Does NOT connect to brokers**: Users execute manually
- **Advisory only**: Not financial advice, users make final decisions

### 12.2 Data Limitations
- **110+ stocks**: Limited watchlist (not all stocks)
- **Daily updates**: Not real-time (updates daily)
- **API dependencies**: Relies on yfinance and Alpha Vantage availability

### 12.3 Model Limitations
- **LLM-based**: Recommendations are probabilistic, not guaranteed
- **Historical learning**: Learns from past but cannot predict future perfectly
- **Market conditions**: Performance varies with market conditions

### 12.4 Legal Disclaimer
> TradingAgents framework is designed for research purposes. Trading performance may vary based on many factors, including the chosen backbone language models, model temperature, trading periods, the quality of data, and other non-deterministic factors. **It is not intended as financial, investment, or trading advice.**

---

## 13. Support & Documentation

### 13.1 Documentation Files
- `docs/EDDIE_SUMMARY.md`: Quick overview
- `docs/EDDIE_USAGE_SUMMARY.md`: Usage guide
- `docs/EDDIE_TRADING_WORKFLOW_GUIDE.md`: Complete workflow guide
- `docs/EDDIE_QUICK_REFERENCE.md`: Quick reference card
- `docs/EDDIE_EXAMPLES_AND_USE_CASES.md`: Real-world examples
- `docs/BOT_GUIDE.md`: Comprehensive bot guide

### 13.2 Getting Started
```bash
# Launch Eddie
./trading_bot.sh

# Access web interface
http://localhost:8000

# Example first question
"What are the best stocks right now?"
```

---

## 14. Conclusion

Eddie represents a comprehensive AI trading assistant that combines:
- **Multi-agent intelligence** for thorough analysis
- **Learning and memory** for continuous improvement
- **Data validation** for trustworthiness
- **Strategic intelligence** for actionable insights
- **Speed flexibility** for different use cases

Eddie empowers users to make informed trading decisions through intelligent analysis, comprehensive validation, and continuous learning, while maintaining transparency and risk awareness.

---

**Document Version:** 1.0  
**Last Updated:** November 2025  
**Maintained By:** TradingAgents Development Team

