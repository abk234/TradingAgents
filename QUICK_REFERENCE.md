# TradingAgents Quick Reference Guide

## 🚀 Quick Start

### Run the CLI (Interactive Mode)
```bash
cd /Users/lxupkzwjs/Developer/eval/TradingAgents
source venv/bin/activate
python -m cli.main analyze
```

**If you get "No module named typer" error:**
1. Make sure you're in the correct directory: `/Users/lxupkzwjs/Developer/eval/TradingAgents`
2. Make sure the virtual environment is activated: `source venv/bin/activate`
3. Verify typer is installed: `pip show typer`

---

## 📋 What This Application Does

### **Core Functionality**
Analyzes any stock ticker (like AAPL, NVDA, TSLA) and provides:
- ✅ **Comprehensive market analysis** from 4 different perspectives
- ✅ **Trading recommendation** (Buy, Sell, or Hold)
- ✅ **Risk assessment** and portfolio management decision
- ✅ **Detailed reports** explaining the reasoning

### **The 5-Stage Analysis Process**

```
1. ANALYST TEAM (Data Collection)
   ├─ Market Analyst: Technical indicators (MACD, RSI, etc.)
   ├─ Social Analyst: Sentiment from Reddit/social media
   ├─ News Analyst: News articles and events
   └─ Fundamentals Analyst: Company financials

2. RESEARCH TEAM (Debate)
   ├─ Bull Researcher: Argues FOR buying
   ├─ Bear Researcher: Argues AGAINST buying
   └─ Research Manager: Makes final research decision

3. TRADER AGENT (Strategy)
   └─ Creates detailed trading plan (entry, size, stop-loss)

4. RISK MANAGEMENT TEAM (Risk Assessment)
   ├─ Aggressive Analyst: Argues for higher risk
   ├─ Conservative Analyst: Argues for lower risk
   ├─ Neutral Analyst: Balanced perspective
   └─ Portfolio Manager: Final approval/rejection

5. FINAL DECISION
   └─ APPROVED or REJECTED with detailed reasoning
```

---

## 🎯 What You Can Achieve

### **1. Stock Analysis**
- Analyze any US stock ticker
- Get multi-perspective analysis (technical, sentiment, news, fundamentals)
- Understand why a stock might be a good/bad investment

### **2. Learning Tool**
- **For Students**: Learn how professional trading firms analyze stocks
- **For Developers**: Understand multi-agent AI systems
- **For Traders**: See how AI can augment trading decisions

### **3. Research & Backtesting**
- Analyze historical dates to see what the system would have recommended
- Compare different analysis approaches
- Test different configurations

### **4. Customizable Analysis**
- Choose which analysts to use (you don't need all 4)
- Adjust research depth (shallow, medium, deep)
- Select different AI models (OpenAI, Gemini, Claude)
- Configure debate rounds

---

## 💡 How to Fully Utilize

### **Use Case 1: Quick Stock Opinion**
**Goal**: Get a quick opinion on a stock

**Settings**:
- Analysts: All 4
- Research Depth: **Shallow** (1 round)
- Models: `gemini-2.0-flash-lite` (fast, cheap)
- **Time**: ~5-10 minutes
- **Cost**: ~$0.10-0.30

**Example**:
```bash
python -m cli.main analyze
# Select: AAPL, 2024-11-01, All analysts, Shallow, Google, gemini-2.0-flash-lite
```

### **Use Case 2: Deep Research Analysis**
**Goal**: Thorough analysis for important decisions

**Settings**:
- Analysts: All 4
- Research Depth: **Deep** (5 rounds)
- Models: `gemini-2.5-pro` (powerful)
- **Time**: ~20-30 minutes
- **Cost**: ~$0.80-2.00

**Example**:
```bash
python -m cli.main analyze
# Select: NVDA, 2024-11-01, All analysts, Deep, Google, gemini-2.5-pro
```

### **Use Case 3: Technical Analysis Only**
**Goal**: Focus on charts and technical indicators

**Settings**:
- Analysts: **Only Market Analyst**
- Research Depth: Medium
- Models: Fast models
- **Time**: ~3-5 minutes
- **Cost**: ~$0.05-0.15

### **Use Case 4: Sentiment & News Analysis**
**Goal**: Understand market mood and news impact

**Settings**:
- Analysts: **Social Analyst + News Analyst**
- Research Depth: Medium
- Models: Balanced models
- **Time**: ~5-8 minutes
- **Cost**: ~$0.15-0.40

### **Use Case 5: Programmatic Integration**
**Goal**: Integrate into your own system

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

# Analyze
_, decision = ta.propagate("AAPL", "2024-11-01")
print(decision)
```

---

## 📊 Understanding the Output

### **What You Get**:

1. **4 Analyst Reports**:
   - **Market**: Technical indicators, chart patterns
   - **Social**: Public sentiment, Reddit discussions
   - **News**: Important events, earnings, macro news
   - **Fundamentals**: Financial metrics, company health

2. **Research Team Decision**:
   - Bull arguments (why buy)
   - Bear arguments (why not buy)
   - Final research recommendation

3. **Trading Plan**:
   - Entry strategy
   - Position sizing
   - Risk management

4. **Risk Assessment**:
   - Aggressive view
   - Conservative view
   - Neutral view

5. **Final Decision**:
   - **APPROVED**: Trade recommended
   - **REJECTED**: Trade not recommended
   - Detailed reasoning

---

## ⚙️ Configuration Guide

### **Analyst Selection**
- **All 4**: Most comprehensive (recommended)
- **Market only**: Fast technical analysis
- **Social + News**: Sentiment and events
- **Fundamentals only**: Deep financial analysis

### **Research Depth**
- **Shallow (1 round)**: Quick, ~5-10 min, ~$0.10-0.30
- **Medium (3 rounds)**: Balanced, ~10-15 min, ~$0.30-0.80
- **Deep (5 rounds)**: Thorough, ~20-30 min, ~$0.80-2.00

### **AI Models (Gemini)**
- **Quick Thinking**: `gemini-2.0-flash-lite` (fastest, cheapest)
- **Deep Thinking**: `gemini-2.0-flash` (balanced)
- **Advanced**: `gemini-2.5-pro` (most powerful, slower)

---

## 💰 Cost Estimates (Per Analysis)

### **With Gemini** (Recommended):
- Shallow: ~$0.10 - $0.30
- Medium: ~$0.30 - $0.80
- Deep: ~$0.80 - $2.00

### **With OpenAI**:
- Shallow: ~$0.50 - $1.50
- Medium: ~$1.50 - $4.00
- Deep: ~$4.00 - $10.00

**Alpha Vantage**: Free (60 requests/minute)

**Tips to Save**:
- Use Gemini instead of OpenAI
- Use `gemini-2.0-flash-lite` for quick analysis
- Reduce debate rounds
- Select fewer analysts when appropriate

---

## 🔧 Troubleshooting

### **Error: "No module named typer"**

**Solution**:
```bash
# 1. Make sure you're in the correct directory
cd /Users/lxupkzwjs/Developer/eval/TradingAgents

# 2. Activate virtual environment
source venv/bin/activate

# 3. Verify typer is installed
pip show typer

# 4. If not installed, install it
pip install typer

# 5. Run the CLI
python -m cli.main analyze
```

### **Error: API key not found**

**Solution**:
```bash
# Check your .env file
cat .env

# Should show:
# GOOGLE_API_KEY=your-key-here
# ALPHA_VANTAGE_API_KEY=your-key-here
```

### **Error: Slow performance**

**Solution**:
- Use faster models (`gemini-2.0-flash-lite`)
- Reduce debate rounds (use Shallow depth)
- Select fewer analysts

---

## 📈 Real-World Applications

1. **Pre-Trade Analysis**: Analyze stocks before making trades
2. **Portfolio Review**: Analyze holdings in your portfolio
3. **Market Research**: Understand market sentiment and trends
4. **Educational Tool**: Learn professional trading analysis
5. **Backtesting**: Test strategies on historical data
6. **Risk Assessment**: Get second opinion on trading ideas

---

## 🎓 Learning Path

### **Beginner**:
1. Start with simple analysis (all analysts, shallow depth)
2. Analyze well-known stocks (AAPL, MSFT, GOOGL)
3. Read the reports to understand each perspective
4. Focus on understanding the final decision

### **Intermediate**:
1. Experiment with different analyst combinations
2. Compare shallow vs deep research depth
3. Analyze stocks on different dates (earnings, news events)
4. Try different AI models and compare results

### **Advanced**:
1. Integrate into your own trading system
2. Build backtesting frameworks
3. Customize agents and add new analysis types
4. Modify the debate logic and risk assessment

---

## ⚠️ Important Notes

1. **Not Financial Advice**: This is a research tool, not investment advice
2. **Past Performance**: Historical analysis doesn't guarantee future results
3. **AI Limitations**: AI models can make mistakes
4. **Always Do Your Own Research**: Use this as one tool among many
5. **Risk Management**: Never invest more than you can afford to lose

---

## 🎯 Example Workflow

```bash
# 1. Navigate to project
cd /Users/lxupkzwjs/Developer/eval/TradingAgents

# 2. Activate virtual environment
source venv/bin/activate

# 3. Run CLI
python -m cli.main analyze

# 4. Follow prompts:
#    - Ticker: AAPL
#    - Date: 2024-11-01
#    - Analysts: All (or select specific ones)
#    - Research Depth: Shallow (for quick test)
#    - LLM Provider: Google
#    - Quick Thinker: gemini-2.0-flash-lite
#    - Deep Thinker: gemini-2.0-flash

# 5. Watch the analysis unfold in real-time!
```

---

## 📚 Additional Resources

- **Full Guide**: See `APPLICATION_GUIDE.md` for detailed information
- **Setup Guide**: See `SETUP_GUIDE.md` for installation help
- **Quick Start**: See `QUICK_START.md` for prerequisites
- **README**: See `README.md` for project overview

---

Happy Trading! 🚀📊

