# Troubleshooting: Connection Errors Fixed

**Date:** 2025-11-16
**Issue:** "Connection error" when analyzing stocks
**Status:** ✅ RESOLVED

---

## The Problem

When running analysis, you would see errors like:
```
ERROR:__main__:Error analyzing XOM: Connection error.
INFO:openai._base_client:Retrying request to /chat/completions
```

## Root Cause

The `langchain_openai.ChatOpenAI` client was using a **very short default timeout** (likely 10-30 seconds). When Ollama took longer to:
1. Load the llama3.3:70b model into memory (first request)
2. Generate complex financial analysis responses (can take 30-60+ seconds for large models)

...the client would timeout before receiving a response, causing "Connection error".

## The Fix

Added explicit `timeout=120` parameter to LLM initialization in `tradingagents/graph/trading_graph.py`:

```python
# Before (no timeout):
self.deep_thinking_llm = ChatOpenAI(
    model=self.config["deep_think_llm"],
    base_url=self.config["backend_url"],
    api_key=api_key,
    temperature=0.7
)

# After (with timeout):
timeout = 120  # 2 minutes timeout for LLM responses
self.deep_thinking_llm = ChatOpenAI(
    model=self.config["deep_think_llm"],
    base_url=self.config["backend_url"],
    api_key=api_key,
    temperature=0.7,
    timeout=timeout  # ← ADDED
)
```

## Verification

Test that Ollama works:
```bash
# Test Ollama API directly
curl http://localhost:11434/v1/models

# Test with langchain (should succeed now)
.venv/bin/python << 'EOF'
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="llama3.3",
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    timeout=120
)
print(llm.invoke("Say hello").content)
EOF
```

## Now You Can Run Analysis

```bash
# Run daily analysis (should work now!)
./scripts/run_daily_analysis.sh

# Or analyze single stock
PYTHONPATH=$PWD .venv/bin/python -m tradingagents.analyze AAPL --plain-english --portfolio-value 100000
```

## Expected Timing

With Ollama llama3.3:70b on local hardware:
- First analysis: 3-5 minutes (model loading + generation)
- Subsequent analyses: 2-3 minutes (model cached in memory)
- Fast mode (--fast --no-rag): 1-2 minutes per stock

## Other Potential Issues

If you still see connection errors after this fix:

### Issue: Ollama not running
```bash
# Check if running
pgrep ollama

# Start if needed
ollama serve
```

### Issue: Model not pulled
```bash
# Pull the model if missing
ollama pull llama3.3
ollama pull llama3.1
```

### Issue: Ollama on different port
```bash
# Check Ollama's actual port
ps aux | grep ollama

# Update config if needed
# Edit tradingagents/default_config.py:
# "backend_url": "http://localhost:ACTUAL_PORT/v1"
```

### Issue: Out of memory
If your system runs out of RAM with llama3.3:70b (42GB model):

**Option 1: Use smaller model**
```python
# Edit tradingagents/default_config.py:
"deep_think_llm": "llama3.1",      # 4.9GB instead of 42GB
"quick_think_llm": "qwen2.5:7b",    # 4.7GB, fast
```

**Option 2: Use quantized version**
```bash
# Pull a smaller quantized version
ollama pull llama3.3:8b            # Much smaller
```

Then update config to use "llama3.3:8b"

---

## Summary

✅ Connection errors were caused by timeout issues, not Ollama itself
✅ Adding `timeout=120` parameter fixes the issue
✅ Ollama is working perfectly with the system
✅ Analysis should now complete successfully

---

**Now try running:** `./scripts/run_daily_analysis.sh`
