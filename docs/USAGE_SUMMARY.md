# TradingAgents Usage Summary

## 🚀 Quick Start

### **Run the Application**
```bash
python run.py
```

This script will:
1. ✅ Check Python version
2. ✅ Create virtual environment (if needed)
3. ✅ Install all dependencies from `requirements.txt`
4. ✅ Check API keys
5. ✅ Fix configuration issues
6. ✅ Start the interactive CLI

---

## 📋 What This Application Does

**TradingAgents** is a multi-agent AI system that analyzes stocks and provides trading recommendations. It simulates a professional trading firm with specialized teams:

### **The 5-Stage Process**:

1. **Analyst Team** → Collects and analyzes data (technical, sentiment, news, fundamentals)
2. **Research Team** → Bull and bear researchers debate the investment
3. **Trader Agent** → Creates a detailed trading plan
4. **Risk Management Team** → Evaluates and adjusts the trading strategy
5. **Portfolio Manager** → Makes final decision (APPROVE or REJECT)

### **Output**:
- **4 detailed analyst reports** (Market, Social, News, Fundamentals)
- **Research team debate** (Bull vs Bear arguments)
- **Trading plan** (entry, size, stop-loss, take-profit)
- **Risk assessment** (aggressive, conservative, neutral views)
- **Final decision** (BUY, SELL, or HOLD with reasoning)

---

## 💡 What You Can Achieve

### **1. Stock Analysis**
- Analyze any US stock ticker (AAPL, NVDA, TSLA, etc.)
- Get comprehensive analysis from 4 different perspectives
- Understand why a stock might be a good/bad investment

### **2. Trading Recommendations**
- Get **Buy, Sell, or Hold** recommendations
- See the reasoning behind each recommendation
- Understand the debate between bullish and bearish perspectives

### **3. Learning Tool**
- **For Students**: Learn how professional trading firms analyze stocks
- **For Developers**: Understand multi-agent AI systems
- **For Traders**: See how AI can augment trading decisions

### **4. Research & Backtesting**
- Analyze historical dates to see what the system would have recommended
- Compare different analysis approaches
- Test different configurations

### **5. Customizable Analysis**
- Choose which analysts to use (you don't need all 4)
- Adjust research depth (shallow, medium, deep)
- Select different AI models (OpenAI, Gemini, Claude)

---

## 🎯 How to Fully Utilize

### **Quick Analysis** (5-10 min, ~$0.10-0.30)
- **Analysts**: All 4
- **Research Depth**: Shallow (1 round)
- **Models**: `gemini-2.0-flash-lite`
- **Use Case**: Quick opinion on a stock

### **Deep Analysis** (20-30 min, ~$0.80-2.00)
- **Analysts**: All 4
- **Research Depth**: Deep (5 rounds)
- **Models**: `gemini-2.5-pro`
- **Use Case**: Important investment decisions

### **Technical Only** (3-5 min, ~$0.05-0.15)
- **Analysts**: Market Analyst only
- **Research Depth**: Medium
- **Use Case**: Focus on charts and technical indicators

### **Sentiment & News** (5-8 min, ~$0.15-0.40)
- **Analysts**: Social + News Analysts
- **Research Depth**: Medium
- **Use Case**: Understand market mood and news impact

---

## 📊 Understanding the Output

You'll get:
1. **4 Analyst Reports** (Market, Social, News, Fundamentals)
2. **Research Team Decision** (Bull vs Bear debate)
3. **Trading Plan** (entry strategy, position sizing)
4. **Risk Assessment** (aggressive, conservative, neutral views)
5. **Final Decision** (APPROVED or REJECTED with reasoning)

---

## ⚙️ Configuration Options

- **Analyst Selection**: All 4, or specific ones
- **Research Depth**: Shallow (1), Medium (3), Deep (5) rounds
- **AI Models**: Gemini, OpenAI, or Claude
- **Data Sources**: Yahoo Finance, Alpha Vantage, Google News

---

## 💰 Cost Estimates

**With Gemini** (Recommended):
- Shallow: ~$0.10-0.30
- Medium: ~$0.30-0.80
- Deep: ~$0.80-2.00

**With OpenAI**:
- Shallow: ~$0.50-1.50
- Medium: ~$1.50-4.00
- Deep: ~$4.00-10.00

---

## 📚 Documentation

- **What Can It Do?**: See `WHAT_CAN_IT_DO.md` for detailed capabilities
- **Application Guide**: See `APPLICATION_GUIDE.md` for comprehensive guide
- **Quick Reference**: See `QUICK_REFERENCE.md` for quick commands
- **Setup Guide**: See `SETUP_GUIDE.md` for installation help

---

## ⚠️ Important Notes

1. **Not Financial Advice**: This is a research tool, not investment advice
2. **AI Limitations**: AI models can make mistakes
3. **Always Do Your Own Research**: Use this as one tool among many
4. **Risk Management**: Never invest more than you can afford to lose

---

Happy Trading! 🚀📊

