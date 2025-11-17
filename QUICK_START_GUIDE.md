# Quick Start Guide - Eddie Trading Bot

## 🚀 Starting the Application

### Option 1: Use the Quick Start Script (Recommended)
```bash
./start_eddie.sh
```

This script will:
- ✅ Kill any existing processes on port 8000
- ✅ Clean up old chainlit/tradingagents processes
- ✅ Start Eddie fresh

### Option 2: Manual Start
```bash
# 1. Kill existing processes (if any)
lsof -ti:8000 | xargs kill -9 2>/dev/null
pkill -f "chainlit run" 2>/dev/null

# 2. Start the application
./trading_bot.sh
```

### Option 3: Use a Different Port
If port 8000 is permanently in use, you can modify the port:

```bash
# Edit tradingagents/bot/__main__.py or chainlit_app.py
# Change port from 8000 to another port (e.g., 8001)
```

---

## 🌐 Accessing the Application

Once started, open your browser to:
**http://localhost:8000**

---

## 🧪 Testing Natural Language Queries

Try these queries in the web interface:

1. **"Analyze AAPL for me"**
   - Should show dividend yield
   - Enhanced expected return breakdown
   - Sector information

2. **"What stocks should I look at?"**
   - Market screener results
   - Top opportunities

3. **"Show me dividend information for MSFT"**
   - Comprehensive dividend analysis

4. **"How is the technology sector doing?"**
   - Sector strength analysis

---

## ✅ What to Expect

### Enhanced Features (Now Active):
- ✅ **Dividend Integration** - Automatically included in all analyses
- ✅ **Sector Balance** - Warnings when approaching limits
- ✅ **Enhanced Profit Calculations** - Price appreciation + Dividends
- ✅ **Comprehensive Recommendations** - Complete breakdowns

### Example Response:
```
🔍 Deep Analysis: AAPL

✅ **Recommendation: BUY**
📊 Confidence: 78/100
💰 Suggested Position: $5,000.00 (5.0% of portfolio)
📈 Expected Return: 13.50%
   • Price Appreciation: 10.00%
   • Dividend Yield: 3.50%
💵 Dividend Yield: 3.50%

📊 Sector: Technology
💡 Tip: Ensure sector exposure stays below 35% for diversification
```

---

## 🛠️ Troubleshooting

### Port 8000 Already in Use
```bash
# Find what's using the port
lsof -i:8000

# Kill the process
lsof -ti:8000 | xargs kill -9
```

### Ollama Not Running
```bash
# Start Ollama
ollama serve

# Or use the Ollama app
```

### Database Connection Issues
- Some features require PostgreSQL database
- Core functionality works without database
- Full features need database setup

---

## 📝 Next Steps

1. **Open http://localhost:8000** in your browser
2. **Try natural language queries**
3. **Verify improvements are working:**
   - Check for dividend yield in analyses
   - Verify sector balance warnings
   - Confirm enhanced profit calculations

---

**Enjoy using Eddie!** 🎉

