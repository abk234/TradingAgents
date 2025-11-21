# Ollama Setup Guide

## ✅ Status: Ollama is Ready!

Your system is already configured with:
- ✅ Ollama installed at `/usr/local/bin/ollama`
- ✅ Ollama server running on port 11434
- ✅ llama3.3:latest (70B) downloaded
- ✅ llama3.1:latest (8B) downloaded

## Current Configuration

The application is configured to use:

| Component | Model | Size | Purpose |
|-----------|-------|------|---------|
| Deep Thinking | `llama3.3` | 70B | Complex analysis, stock research |
| Quick Thinking | `llama3.1` | 8B | Fast conversation, simple queries |

**Location:** `tradingagents/default_config.py`

## Restart the Application

Now that configuration is reverted to Ollama:

```bash
# Stop current instance (Ctrl+C)

# Restart
./start.sh
```

## Test Ollama

### Quick Test
```bash
# Test Ollama directly
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.3",
  "prompt": "What is a stock?",
  "stream": false
}'
```

### Test via App
```bash
# Test the trading app endpoint
curl -X POST http://localhost:8005/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Analyze AAPL stock", "conversation_history": []}'
```

## Available Models

You have these models downloaded:

```
llama3.3:latest          70B (Q4_K_M) - Best quality for analysis
llama3.1:latest           8B (Q4_K_M) - Fast for conversation
deepseek-coder:33b       33B (Q4_0)   - Code-focused
qwen2.5:7b-instruct       7B (Q4_K_M) - Fast alternative
mistral:latest            7B (Q4_K_M) - Fast alternative
```

## Switch Models (Optional)

To use different models, edit `tradingagents/default_config.py`:

```python
# Example: Use faster models
"deep_think_llm": "qwen2.5:7b-instruct",  # Faster than llama3.3
"quick_think_llm": "llama3.1",             # Keep as is
```

## Troubleshooting

### If Ollama is not responding:

```bash
# Restart Ollama
# macOS GUI: Quit and restart Ollama app
# OR via command:
ollama serve
```

### If models are missing:

```bash
# Pull required models
ollama pull llama3.3
ollama pull llama3.1
```

### Check Ollama is working:

```bash
# List models
ollama list

# Test generation
ollama run llama3.3 "What is a stock?"
```

### Performance Tips

1. **RAM**: llama3.3 (70B) needs ~40GB RAM
   - If you have <40GB, use smaller model:
     ```python
     "deep_think_llm": "qwen2.5:7b-instruct",
     ```

2. **Speed**: For faster responses, use smaller models:
   ```python
   "deep_think_llm": "llama3.1",      # 8B instead of 70B
   "quick_think_llm": "llama3.1",     # Same model
   ```

3. **Quality vs Speed**:
   - llama3.3 (70B): Best quality, slower (~30-60s)
   - qwen2.5 (7B): Good quality, fast (~5-10s)
   - llama3.1 (8B): Balanced (~10-20s)

## Why Ollama?

✅ **Free**: No API costs
✅ **Private**: Data stays on your machine
✅ **Fast**: No network latency
✅ **Offline**: Works without internet

❌ **Needs RAM**: Large models need significant RAM
❌ **Slower**: Not as fast as cloud APIs for large models

## Next Steps

1. **Restart the app:**
   ```bash
   ./start.sh
   ```

2. **Test it works:**
   - Open http://localhost:3005
   - Ask: "Analyze AAPL stock"
   - Wait for Ollama to generate response (may take 30-60 seconds for complex queries)

3. **Monitor performance:**
   - Check RAM usage: `top` or Activity Monitor
   - If slow, consider switching to smaller model

---

**All set!** Your app is now configured to use Ollama for free, local AI. 🚀
