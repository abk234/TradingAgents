# Quick Start: Langfuse Monitoring

## ✅ Setup Complete!

Your Langfuse integration is **ready to use**. All tests passed!

---

## 🚀 Run Your First Traced Analysis

### Option 1: Use the Test Script

```bash
cd /Users/lxupkzwjs/Developer/eval/TradingAgents
python3 test_langfuse_tracing.py
```

This will:
- ✅ Run a quick AAPL analysis
- ✅ Trace all agent executions
- ✅ Show you where to find traces in Langfuse

### Option 2: Use in Your Code

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from datetime import date

# Create graph (Langfuse enabled by default)
graph = TradingAgentsGraph(enable_langfuse=True)

# Run analysis - automatically traced!
result, signal = graph.propagate("AAPL", date.today())

# Check traces at: http://localhost:3000
```

---

## 📊 View Traces in Langfuse

1. **Open:** `http://localhost:3000`
2. **Login** (if needed)
3. **Go to:** Traces (sidebar)
4. **Look for:** `"Stock Analysis: AAPL"` (or your ticker)
5. **Click** to see:
   - ✅ All agent executions
   - ✅ Execution times
   - ✅ LLM calls
   - ✅ Full trace details

---

## 🔍 What Gets Traced

Every analysis automatically traces:
- ✅ **All 13 agents** - Each execution
- ✅ **Graph flow** - How agents connect
- ✅ **LLM calls** - Tokens, costs, responses
- ✅ **Tool usage** - Which tools were called
- ✅ **Timing** - How long each step took
- ✅ **Metadata** - Ticker, date, RAG status

---

## 🎯 Example: Monitor Multiple Stocks

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from datetime import date

graph = TradingAgentsGraph(enable_langfuse=True)

# Analyze multiple stocks
for ticker in ["AAPL", "MSFT", "GOOGL"]:
    result, signal = graph.propagate(ticker, date.today())
    print(f"{ticker}: {result.get('final_decision')}")

# Then check Langfuse dashboard to compare:
# - Which agents ran for each stock
# - Execution times
# - Costs per analysis
```

---

## 📈 Monitor Agent Performance

In Langfuse dashboard, you can:

1. **Compare agents** - See which agents are fastest
2. **Track costs** - Monitor LLM spending per analysis
3. **Debug issues** - Inspect failed executions
4. **Optimize** - Identify bottlenecks

---

## 🛠️ Troubleshooting

### No Traces Appearing?

1. **Check Langfuse is running:**
   ```bash
   cd /Users/lxupkzwjs/Developer/langfuse
   docker compose ps
   ```

2. **Verify environment variables:**
   ```bash
   python3 test_langfuse_connection.py
   ```

3. **Check logs:**
   ```bash
   docker compose logs langfuse-web --tail 50
   ```

### Traces Appear But Empty?

- Langfuse v3 may need additional configuration
- Check that callback handler is working
- Verify API keys are correct

---

## ✅ Success Checklist

- [x] Langfuse server running
- [x] Environment variables set
- [x] Python package installed
- [x] Tracer enabled
- [ ] Run first analysis ← **You are here!**
- [ ] Verify traces appear
- [ ] Explore dashboard

---

## 🎉 Next Steps

1. **Run a test analysis** - See traces appear
2. **Explore the dashboard** - Check out trace details
3. **Monitor regularly** - Track agent performance
4. **Plan Prometheus/Grafana** - Add later for advanced metrics

---

**Ready to start monitoring!** 🚀

Run: `python3 test_langfuse_tracing.py`

