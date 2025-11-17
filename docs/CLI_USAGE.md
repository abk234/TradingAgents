# CLI Usage Guide

## Running the Application

### Option 1: Direct Script (Recommended)
```bash
source venv/bin/activate
python run_analysis.py
```

### Option 2: Using run.py (Setup + Run)
```bash
python run.py
```
This will:
1. Set up virtual environment
2. Install dependencies
3. Fix ChromaDB config
4. Launch interactive CLI

### Option 3: Direct Function Call
```bash
source venv/bin/activate
python -c "from cli.main import run_analysis; run_analysis()"
```

## Known Issue with `python -m cli.main analyze`

**Problem**: When running `python -m cli.main analyze`, you may get:
```
Got unexpected extra argument (analyze)
```

**Cause**: Typer command registration issue when running as a module.

**Solution**: Use `run_analysis.py` instead (Option 1 above).

## Interactive Prompts

When you run the analysis, you'll be prompted for:

1. **Ticker Symbol** (e.g., AAPL, NVDA, SPY)
2. **Analysis Date** (YYYY-MM-DD format)
3. **Analysts Team** (Market, Social, News, Fundamentals)
4. **Research Depth** (Shallow/Medium/Deep)
5. **LLM Provider** (Google/OpenAI/Anthropic/Ollama)
6. **Thinking Agents** (Quick and Deep thinking models)

## Quick Start

```bash
# Activate virtual environment
source venv/bin/activate

# Run analysis
python run_analysis.py
```

---

*Last Updated: 2025-01-16*

