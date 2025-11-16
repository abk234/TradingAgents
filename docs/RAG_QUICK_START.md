# RAG System Quick Start Guide

Get started with RAG-enhanced investment analysis in 5 minutes.

## Prerequisites

✅ Phase 1 complete (PostgreSQL + pgvector setup)
✅ Phase 2 complete (Daily screener running)
✅ Ollama running locally with nomic-embed-text model

## Verify Ollama Setup

```bash
# Check Ollama is running
ollama list

# If nomic-embed-text is not installed:
ollama pull nomic-embed-text
```

## Quick Test

Run the comprehensive test suite to verify RAG system:

```bash
PYTHONPATH=/Users/lxupkzwjs/Developer/eval/TradingAgents \
  .venv/bin/python tradingagents/analyze/test_rag.py
```

Expected output:
```
🎉 All tests passed! RAG system is ready.
Results: 5/5 tests passed
```

## Basic Usage

### 1. Analyze a Single Ticker

```bash
python -m tradingagents.analyze AAPL
```

### 2. Analyze Multiple Tickers

```bash
python -m tradingagents.analyze AAPL GOOGL MSFT
```

### 3. Verbose Output (Full Reports)

```bash
python -m tradingagents.analyze AAPL --verbose
```

### 4. Without RAG (Faster, No Historical Context)

```bash
python -m tradingagents.analyze AAPL --no-rag
```

## Python API

### Simple Analysis

```python
from tradingagents.analyze import DeepAnalyzer
from datetime import date

# Initialize
analyzer = DeepAnalyzer(enable_rag=True)

# Analyze
results = analyzer.analyze(
    ticker="AAPL",
    analysis_date=date.today(),
    store_results=True
)

# Print formatted results
analyzer.print_results(results, verbose=True)

# Access decision
print(f"Decision: {results['decision']}")
print(f"Confidence: {results['confidence']}/100")
```

### Batch Analysis

```python
from tradingagents.analyze import DeepAnalyzer

analyzer = DeepAnalyzer(enable_rag=True)

for ticker in ["AAPL", "GOOGL", "MSFT"]:
    results = analyzer.analyze(ticker, store_results=True)
    print(f"{ticker}: {results['decision']} ({results['confidence']}/100)")

analyzer.close()
```

### Using with Existing TradingAgentsGraph

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from datetime import date

# Initialize with RAG enabled
graph = TradingAgentsGraph(
    selected_analysts=["market", "fundamentals", "news"],
    enable_rag=True  # This enables RAG!
)

# Run analysis - historical context automatically included
final_state, signal = graph.propagate(
    company_name="AAPL",
    trade_date=date.today(),
    store_analysis=True  # Store results for future RAG
)
```

## How RAG Works

### 1. Embedding Generation
When you analyze a ticker, the system:
- Creates a 768-dimensional vector embedding of the current situation
- Uses Ollama's nomic-embed-text model

### 2. Context Retrieval
The system searches for:
- **Similar past analyses** for the same ticker
- **Cross-ticker patterns** from other stocks
- **Sector trends** in the same industry

### 3. Prompt Enhancement
Historical intelligence is injected into agent prompts:
- Bull agents see successful past buy signals
- Bear agents see cautionary past decisions
- Risk agents see historical risk patterns

### 4. Storage
After analysis, results are stored with embeddings:
- Each analysis enriches the knowledge base
- Future analyses benefit from more historical data

## CLI Options

| Option | Description |
|--------|-------------|
| `--date YYYY-MM-DD` | Specify analysis date (default: today) |
| `--verbose` | Show full analyst reports and debates |
| `--no-rag` | Disable RAG (faster, no historical context) |
| `--no-store` | Don't save results to database |
| `--debug` | Enable debug mode with detailed tracing |
| `--config PATH` | Use custom configuration file |

## Examples

### Example 1: Historical Analysis

```bash
# Analyze AAPL as of December 1, 2024
python -m tradingagents.analyze AAPL --date 2024-12-01
```

### Example 2: Top 5 from Screener

```bash
# Get top 5 from daily screener
python -m tradingagents.screener top 5

# Then analyze each with RAG
python -m tradingagents.analyze XOM V AAPL TSLA CAT --verbose
```

### Example 3: Without Storing Results

```bash
# Quick analysis, don't add to database
python -m tradingagents.analyze AAPL --no-store
```

## Understanding Results

### Decision Types

| Decision | Meaning |
|----------|---------|
| **BUY** | Strong buy signal, all conditions favorable |
| **WAIT** | Good opportunity but timing not optimal |
| **HOLD** | Maintain current position |
| **SELL** | Sell signal or avoid entry |

### Confidence Scores

| Score | Interpretation |
|-------|----------------|
| 80-100 | High confidence, strong consensus |
| 65-79 | Moderate confidence, some uncertainty |
| 50-64 | Low confidence, conflicting signals |
| <50 | Very low confidence, avoid action |

### RAG Context Indicator

```
🤖 RAG Context: ✓ Used        # Historical intelligence included
🤖 RAG Context: ✗ Not available  # No historical data or RAG disabled
```

## Building Historical Intelligence

The system gets smarter over time:

### Week 1: Bootstrap
- Run daily screener: `python -m tradingagents.screener run`
- Analyze top 3-5 tickers with `store_results=True`
- Build initial knowledge base

### Week 2-4: Accumulation
- Continue daily screening
- Analyze opportunities with RAG enabled
- Historical context becomes more valuable

### Month 2+: Full Power
- Rich historical database
- Similar situations identified
- Pattern recognition improving
- Sector trends visible

## Troubleshooting

### "No module named 'tradingagents'"

```bash
# Use PYTHONPATH
PYTHONPATH=/path/to/TradingAgents python -m tradingagents.analyze AAPL

# Or run from project directory
cd /path/to/TradingAgents
python -m tradingagents.analyze AAPL
```

### "Failed to generate embedding"

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Pull nomic-embed-text model
ollama pull nomic-embed-text
```

### "Database connection failed"

```bash
# Check PostgreSQL is running
brew services list | grep postgresql

# Start PostgreSQL if needed
brew services start postgresql@14

# Verify connection
psql investment_intelligence -c "SELECT version();"
```

### "RAG initialization failed"

The system will continue without RAG:
```
⚠ RAG initialization failed: [error]. Running without RAG.
```

This is expected if:
- Database is unavailable
- Ollama is not running
- No embeddings model available

Analysis will still run, just without historical context.

## Performance Tips

### 1. Batch Processing
Analyze multiple tickers in one run:
```bash
python -m tradingagents.analyze AAPL GOOGL MSFT NVDA AMD
```

### 2. Disable RAG for Speed
When you don't need historical context:
```bash
python -m tradingagents.analyze AAPL --no-rag
```

### 3. Use Smaller LLM for Faster Analysis
Edit your config to use llama3.1 instead of llama3.3:
```json
{
  "deep_think_llm": "llama3.1",
  "quick_think_llm": "llama3.1"
}
```

## Next Steps

1. **Run Daily Screener**: `python -m tradingagents.screener run`
2. **Analyze Top Picks**: `python -m tradingagents.analyze [TICKERS]`
3. **Review Results**: Check the detailed analysis output
4. **Build History**: Store results to improve future analyses
5. **Monitor Performance**: Track decisions over time

## Resources

- **Full Documentation**: `docs/PHASE_3_COMPLETION_REPORT.md`
- **Test Suite**: `tradingagents/analyze/test_rag.py`
- **Phase 1 Guide**: `docs/PRD_Investment_Intelligence_System.md`
- **Screener Guide**: `python -m tradingagents.screener --help`

## Questions?

Run the test suite to diagnose issues:
```bash
python tradingagents/analyze/test_rag.py
```

All tests should pass for a working system.

---

**Happy analyzing! 🚀**
