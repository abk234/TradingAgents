# What Can TradingAgents Do? - Complete Guide

## 🎯 Overview

**TradingAgents** is a sophisticated multi-agent AI system that simulates a professional trading firm. It uses multiple specialized AI agents that work together to analyze stocks and make trading decisions, just like a real trading desk.

---

## 🏢 How It Works: The 5-Stage Analysis Process

### **Stage 1: Analyst Team** (Data Collection & Analysis)

Four specialized analysts gather and analyze different types of data:

#### **1. Market Analyst (Technical Analysis)**
- **What it does**: Analyzes price charts and technical indicators
- **Tools**: MACD, RSI, moving averages, Bollinger Bands, ATR, VWMA
- **Data sources**: Yahoo Finance, Alpha Vantage
- **Output**: Technical analysis report identifying:
  - Trend direction (bullish/bearish)
  - Support and resistance levels
  - Momentum indicators
  - Volatility patterns
  - Entry/exit signals

#### **2. Social Media Analyst (Sentiment Analysis)**
- **What it does**: Analyzes social media sentiment (Reddit, Twitter, etc.)
- **Tools**: Sentiment scoring algorithms, social media APIs
- **Data sources**: Reddit (PRAW), social media feeds
- **Output**: Sentiment report showing:
  - Public opinion about the stock
  - Market mood (bullish/bearish)
  - Social media buzz and discussions
  - Sentiment scores

#### **3. News Analyst (Fundamental Events)**
- **What it does**: Monitors news, earnings reports, macroeconomic events
- **Tools**: News aggregation, event detection
- **Data sources**: Alpha Vantage News, Google News, financial news feeds
- **Output**: News analysis report highlighting:
  - Important events (earnings, product launches, etc.)
  - Macroeconomic indicators
  - Market-moving news
  - Impact assessment

#### **4. Fundamentals Analyst (Company Financials)**
- **What it does**: Analyzes company financial statements and metrics
- **Tools**: Balance sheets, income statements, cash flow, P/E ratios
- **Data sources**: Alpha Vantage, Yahoo Finance
- **Output**: Fundamental analysis report evaluating:
  - Company financial health
  - Valuation metrics (P/E, P/S, etc.)
  - Cash flow analysis
  - Growth potential
  - Red flags or concerns

### **Stage 2: Research Team** (Debate & Strategy)

After analysts provide their reports, two researchers debate the investment:

#### **Bull Researcher** (Optimistic View)
- **Role**: Argues FOR buying the stock
- **Approach**: Highlights positive factors, growth potential, opportunities
- **Uses**: Analyst reports, historical data, market trends
- **Output**: Bullish arguments and reasoning

#### **Bear Researcher** (Pessimistic View)
- **Role**: Argues AGAINST buying the stock
- **Approach**: Highlights risks, concerns, potential downsides
- **Uses**: Analyst reports, risk factors, market volatility
- **Output**: Bearish arguments and reasoning

#### **Research Manager** (Final Decision)
- **Role**: Synthesizes both arguments and makes a research decision
- **Output**: Investment recommendation based on the debate

**Debate Process**: The researchers engage in multiple rounds of debate (configurable: 1-5 rounds) to thoroughly explore all angles.

### **Stage 3: Trader Agent** (Trading Strategy)

- **What it does**: Creates a detailed trading plan based on research
- **Considers**: 
  - Entry price
  - Position size
  - Stop-loss levels
  - Take-profit targets
  - Risk management
- **Output**: Comprehensive trading plan with specific recommendations

### **Stage 4: Risk Management Team** (Risk Assessment)

Three risk analysts evaluate the trading plan:

#### **Aggressive (Risky) Analyst**
- **Role**: Argues for taking more risk for higher returns
- **Approach**: Emphasizes potential gains, accepts higher volatility

#### **Conservative (Safe) Analyst**
- **Role**: Argues for lower risk, more cautious approach
- **Approach**: Emphasizes capital preservation, risk mitigation

#### **Neutral Analyst**
- **Role**: Provides balanced perspective
- **Approach**: Weighs both sides objectively

**Risk Discussion**: Multiple rounds of discussion (configurable) to assess risk properly.

### **Stage 5: Portfolio Manager** (Final Approval)

- **Role**: Final decision maker
- **What it does**: 
  - Reviews all analysis, research, trading plan, and risk assessment
  - Makes final decision: **APPROVE** or **REJECT** the trade
  - If approved: Order is executed (simulated)
  - If rejected: Trade is cancelled
- **Output**: Final decision with detailed reasoning

---

## 🚀 What You Can Achieve

### **1. Comprehensive Stock Analysis**
- Analyze any publicly traded stock (US markets)
- Get analysis from 4 different perspectives (technical, sentiment, news, fundamentals)
- Understand why a stock might be a good or bad investment
- Get detailed reports explaining each perspective

### **2. Trading Recommendations**
- Get **Buy, Sell, or Hold** recommendations
- Understand the reasoning behind each recommendation
- See the debate between bullish and bearish perspectives
- Get risk assessment and portfolio management decisions

### **3. Learning Tool**
- **For Students**: Learn how professional trading firms analyze stocks
- **For Developers**: Understand multi-agent AI systems and LangGraph
- **For Traders**: See how AI can augment trading decisions
- **For Researchers**: Study multi-agent systems in financial applications

### **4. Research & Backtesting**
- Analyze historical dates to see what the system would have recommended
- Compare different analysis approaches
- Test different configurations (models, debate rounds, etc.)
- Build backtesting frameworks

### **5. Customizable Analysis**
- Choose which analysts to use (you don't need all 4)
- Adjust research depth (shallow, medium, deep)
- Select different AI models (OpenAI, Gemini, Claude)
- Configure debate rounds and risk discussion rounds

### **6. Detailed Reports**
- Get comprehensive reports for each analyst
- See the full debate between bull and bear researchers
- Review risk assessment discussions
- Understand the final decision reasoning

---

## 💡 How to Fully Utilize This Application

### **Use Case 1: Quick Stock Opinion**
**Goal**: Get a quick opinion on a stock

**Configuration**:
- **Analysts**: All 4 (Market, Social, News, Fundamentals)
- **Research Depth**: **Shallow** (1 debate round)
- **Models**: `gemini-2.0-flash-lite` (fast, cheap)
- **Time**: ~5-10 minutes
- **Cost**: ~$0.10-0.30

**Example**:
```bash
python run.py
# Then select: AAPL, 2024-11-01, All analysts, Shallow, Google, gemini-2.0-flash-lite
```

### **Use Case 2: Deep Research Analysis**
**Goal**: Thorough analysis for important investment decisions

**Configuration**:
- **Analysts**: All 4
- **Research Depth**: **Deep** (5 rounds)
- **Models**: `gemini-2.5-pro` (powerful)
- **Time**: ~20-30 minutes
- **Cost**: ~$0.80-2.00

**Example**:
```bash
python run.py
# Then select: NVDA, 2024-11-01, All analysts, Deep, Google, gemini-2.5-pro
```

### **Use Case 3: Technical Analysis Only**
**Goal**: Focus on charts and technical indicators

**Configuration**:
- **Analysts**: **Only Market Analyst**
- **Research Depth**: Medium
- **Models**: Fast models
- **Time**: ~3-5 minutes
- **Cost**: ~$0.05-0.15

**Use Case**: When you only care about technical indicators and chart patterns

### **Use Case 4: Sentiment & News Analysis**
**Goal**: Understand market mood and news impact

**Configuration**:
- **Analysts**: **Social Analyst + News Analyst**
- **Research Depth**: Medium
- **Models**: Balanced models
- **Time**: ~5-8 minutes
- **Cost**: ~$0.15-0.40

**Use Case**: When you want to understand market sentiment and news impact

### **Use Case 5: Fundamentals Analysis Only**
**Goal**: Deep financial analysis

**Configuration**:
- **Analysts**: **Only Fundamentals Analyst**
- **Research Depth**: Deep
- **Models**: Powerful models
- **Time**: ~5-10 minutes
- **Cost**: ~$0.20-0.50

**Use Case**: When you want to evaluate company financials and valuation

### **Use Case 6: Programmatic Integration**
**Goal**: Integrate into your own trading system or backtesting

**Python Code**:
```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from dotenv import load_dotenv

load_dotenv()

# Configure for Gemini
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "google"
config["deep_think_llm"] = "gemini-2.0-flash"
config["quick_think_llm"] = "gemini-2.0-flash-lite"
config["max_debate_rounds"] = 2

# Initialize
ta = TradingAgentsGraph(
    selected_analysts=["market", "social", "news", "fundamentals"],
    debug=True,
    config=config
)

# Analyze a stock
_, decision = ta.propagate("AAPL", "2024-11-01")
print(f"Final Decision: {decision}")
```

### **Use Case 7: Historical Analysis**
**Goal**: Analyze what the system would have recommended in the past

**Example**:
- Analyze NVDA on 2024-05-10 (before a major move)
- Analyze TSLA on a specific earnings date
- Compare recommendations across different dates

### **Use Case 8: Model Comparison**
**Goal**: Compare different AI models' recommendations

**Approach**:
1. Run analysis with Gemini models
2. Run same analysis with OpenAI models
3. Compare the recommendations and reasoning

---

## 📊 Understanding the Output

### **What You Get**:

1. **4 Analyst Reports** (separate reports):
   - **Market**: Technical indicators, chart patterns, momentum
   - **Social**: Public sentiment, Reddit discussions, market mood
   - **News**: Important events, earnings, macro news
   - **Fundamentals**: Financial metrics, company health, valuation

2. **Research Team Decision**:
   - Bull arguments (why buy)
   - Bear arguments (why not buy)
   - Final research recommendation

3. **Trading Plan**:
   - Entry strategy
   - Position sizing
   - Risk management levels
   - Stop-loss and take-profit targets

4. **Risk Assessment**:
   - Aggressive view (higher risk, higher reward)
   - Conservative view (lower risk, capital preservation)
   - Neutral view (balanced perspective)

5. **Final Decision**:
   - **APPROVED**: Trade recommended
   - **REJECTED**: Trade not recommended
   - Detailed reasoning for the decision

### **Decision Format**:

The final decision typically includes:
- **Action**: BUY, SELL, or HOLD
- **Confidence**: How confident the system is
- **Reasoning**: Why this decision was made
- **Risk Level**: Low, Medium, or High risk

---

## ⚙️ Configuration Options

### **Analyst Selection**
- **All 4**: Most comprehensive (recommended for important decisions)
- **Market only**: Fast technical analysis
- **Social + News**: Sentiment and event analysis
- **Fundamentals only**: Deep financial analysis
- **Any combination**: Mix and match as needed

### **Research Depth**
- **Shallow (1 round)**: Quick analysis, ~5-10 min, ~$0.10-0.30
- **Medium (3 rounds)**: Balanced, ~10-15 min, ~$0.30-0.80
- **Deep (5 rounds)**: Thorough, ~20-30 min, ~$0.80-2.00

### **AI Models** (for Gemini)
- **Quick Thinking**: `gemini-2.0-flash-lite` (fastest, cheapest)
- **Deep Thinking**: `gemini-2.0-flash` (balanced)
- **Advanced**: `gemini-2.5-pro` (most powerful, slower)

### **Data Sources**
- **Stock Data**: Yahoo Finance (free) or Alpha Vantage
- **News**: Alpha Vantage (default) or Google News
- **Fundamentals**: Alpha Vantage (default)

---

## 💰 Cost Estimates (Per Analysis)

### **With Gemini** (Recommended):
- **Shallow**: ~$0.10 - $0.30
- **Medium**: ~$0.30 - $0.80
- **Deep**: ~$0.80 - $2.00

### **With OpenAI**:
- **Shallow**: ~$0.50 - $1.50
- **Medium**: ~$1.50 - $4.00
- **Deep**: ~$4.00 - $10.00

**Alpha Vantage**: Free (60 requests/minute)

**Tips to Save Costs**:
- Use Gemini instead of OpenAI
- Use `gemini-2.0-flash-lite` for quick analysis
- Reduce debate rounds (use Shallow depth)
- Select fewer analysts when appropriate

---

## 🎓 Learning Path

### **Beginner Level**
1. Start with simple analysis: Use all analysts, shallow depth
2. Analyze well-known stocks (AAPL, MSFT, GOOGL)
3. Read the reports to understand each analyst's perspective
4. Focus on understanding the final decision

### **Intermediate Level**
1. Experiment with different analyst combinations
2. Compare shallow vs deep research depth
3. Analyze stocks on different dates (earnings, news events)
4. Try different AI models and compare results

### **Advanced Level**
1. Integrate into your own trading system
2. Build backtesting frameworks
3. Customize agents and add new analysis types
4. Modify the debate logic and risk assessment

---

## 📈 Real-World Applications

1. **Pre-Trade Analysis**: Analyze stocks before making trades
2. **Portfolio Review**: Analyze holdings in your portfolio
3. **Market Research**: Understand market sentiment and trends
4. **Educational Tool**: Learn professional trading analysis
5. **Backtesting**: Test strategies on historical data
6. **Risk Assessment**: Get second opinion on trading ideas
7. **Research**: Study multi-agent systems in finance

---

## ⚠️ Important Disclaimers

1. **Not Financial Advice**: This is a research tool, not investment advice
2. **Past Performance**: Historical analysis doesn't guarantee future results
3. **AI Limitations**: AI models can make mistakes or miss important factors
4. **Always Do Your Own Research**: Use this as one tool among many
5. **Risk Management**: Never invest more than you can afford to lose

---

## 🎯 Quick Start

```bash
# 1. Run the setup and start script
python run.py

# 2. Follow the prompts:
#    - Ticker: AAPL (or any stock ticker)
#    - Date: 2024-11-01 (YYYY-MM-DD format)
#    - Analysts: All (or select specific ones)
#    - Research Depth: Shallow (for quick test)
#    - LLM Provider: Google
#    - Quick Thinker: gemini-2.0-flash-lite
#    - Deep Thinker: gemini-2.0-flash

# 3. Watch the analysis unfold in real-time!
```

---

## 📚 Additional Resources

- **Full Application Guide**: See `APPLICATION_GUIDE.md`
- **Setup Guide**: See `SETUP_GUIDE.md`
- **Quick Reference**: See `QUICK_REFERENCE.md`
- **Quick Start**: See `QUICK_START.md`
- **README**: See `README.md`

---

Happy Trading! 🚀📊

