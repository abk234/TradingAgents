# Screener Langfuse Integration

## ✅ Status: Integrated!

The screener (`./run_screener.sh`) **will capture traces in Langfuse** when using `--with-analysis`.

---

## 🔍 How It Works

### When You Run:

```bash
./run_screener.sh run --with-analysis --analysis-limit 5
```

**What happens:**

1. **Screener runs** - Scans stocks, calculates indicators, scores them
2. **DeepAnalyzer initialized** - Creates `TradingAgentsGraph` internally
3. **Langfuse enabled** - If `LANGFUSE_ENABLED=true` in your `.env`
4. **Each analysis traced** - All 5 stock analyses are traced to Langfuse

### Code Flow:

```
run_screener.sh
  └─> tradingagents.screener.__main__.cmd_run()
      └─> DeepAnalyzer.analyze() [for each stock]
          └─> TradingAgentsGraph.propagate()
              └─> Langfuse tracing (if enabled)
```

---

## ✅ What Gets Traced

When you run the screener with `--with-analysis`:

- ✅ **Each stock analysis** - Separate trace per stock
- ✅ **All 13 agents** - Every agent execution
- ✅ **LLM calls** - Tokens, costs, latency
- ✅ **Execution times** - How long each analysis took
- ✅ **Metadata** - Ticker, date, priority score

---

## 📊 View Traces in Langfuse

After running:

```bash
./run_screener.sh run --with-analysis --analysis-limit 5
```

1. **Open:** `http://localhost:3000`
2. **Go to:** Traces
3. **Look for:** 
   - `"Stock Analysis: AAPL"` (or whatever stocks were analyzed)
   - Multiple traces (one per stock)
   - All agent executions within each trace

---

## ⚙️ Configuration

### Enable Langfuse for Screener

Make sure your `.env` has:

```bash
LANGFUSE_ENABLED=true
LANGFUSE_PUBLIC_KEY=pk_your_key
LANGFUSE_SECRET_KEY=sk_your_key
LANGFUSE_HOST=http://localhost:3000
```

### Without `--with-analysis`

If you run:

```bash
./run_screener.sh run
```

**No traces** - This only runs the screener (scoring), not the AI analysis. No `TradingAgentsGraph` is used, so no traces.

### With `--with-analysis`

```bash
./run_screener.sh run --with-analysis --analysis-limit 5
```

**Traces captured** - Each of the 5 stock analyses will be traced!

---

## 🎯 Example

```bash
# Run screener with analysis (will trace to Langfuse)
./run_screener.sh run --with-analysis --analysis-limit 5

# Then check Langfuse dashboard
# You should see 5 traces, one for each stock analyzed
```

---

## ✅ Summary

| Command | Langfuse Traces? |
|---------|------------------|
| `./run_screener.sh run` | ❌ No (screener only, no AI analysis) |
| `./run_screener.sh run --with-analysis` | ✅ Yes (if `LANGFUSE_ENABLED=true`) |
| `./run_screener.sh run --with-analysis --analysis-limit 5` | ✅ Yes (5 traces, one per stock) |

---

**Status:** ✅ Screener is integrated with Langfuse! Just make sure `LANGFUSE_ENABLED=true` in your `.env` file.

