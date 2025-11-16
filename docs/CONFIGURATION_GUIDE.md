# Configuration Guide - LLM Providers

The system now supports **Ollama**, **Gemini**, and **OpenAI** without requiring API keys by default.

---

## Default Configuration ✅

**The system is now configured to use Ollama by default** - no API keys required!

### Current Setup (Default)

- **LLM Provider:** Ollama (local)
- **Deep Analysis Model:** llama3.3 (70B)
- **Quick Analysis Model:** llama3.1 (8B)
- **Data Sources:** yfinance (no API keys needed)
- **Embeddings:** nomic-embed-text (via Ollama)

### No API Keys Needed!

Everything works locally:
- ✅ Ollama for LLM inference
- ✅ yfinance for market data
- ✅ PostgreSQL for database
- ✅ No external API dependencies

---

## Verify Ollama Setup

Before running the system, make sure Ollama has the required models:

```bash
# Check Ollama is running
ollama list

# You should see:
# - llama3.1 (or llama3.1:latest)
# - llama3.3 (or llama3.3:latest)
# - nomic-embed-text
```

### Install Missing Models

```bash
# If llama3.1 is missing
ollama pull llama3.1

# If llama3.3 is missing
ollama pull llama3.3

# If nomic-embed-text is missing
ollama pull nomic-embed-text
```

### Verify Ollama API

```bash
# Test Ollama API is responding
curl http://localhost:11434/api/tags

# Should return JSON with list of models
```

---

## Alternative Configurations

### Option 1: Use Gemini (Google)

**Pros:**
- Cloud-based (no local GPU needed)
- Fast inference
- Good quality

**Cons:**
- Requires Google API key
- Internet connection required
- API costs

#### Setup for Gemini

1. **Get Google API Key**
   ```bash
   # Visit: https://makersuite.google.com/app/apikey
   # Create API key
   export GOOGLE_API_KEY="your-key-here"
   ```

2. **Use Gemini Config**
   ```bash
   # Copy the Gemini config
   cp config_gemini.json my_config.json

   # Run with Gemini
   python -m tradingagents.analyze AAPL --config my_config.json
   ```

3. **Or modify default_config.py**
   ```python
   "llm_provider": "google",
   "deep_think_llm": "gemini-2.0-flash",
   "quick_think_llm": "gemini-2.0-flash-lite",
   ```

### Option 2: Use OpenAI

**Pros:**
- High quality models
- Fast inference
- Well-documented

**Cons:**
- Requires OpenAI API key
- Higher costs
- Internet connection required

#### Setup for OpenAI

1. **Get OpenAI API Key**
   ```bash
   # Visit: https://platform.openai.com/api-keys
   # Create API key
   export OPENAI_API_KEY="sk-..."
   ```

2. **Modify default_config.py**
   ```python
   "llm_provider": "openai",
   "deep_think_llm": "gpt-4o",
   "quick_think_llm": "gpt-4o-mini",
   "backend_url": "https://api.openai.com/v1",
   ```

---

## Config File Options

### Using Custom Config Files

Create your own config JSON file:

```json
{
  "llm_provider": "ollama",
  "deep_think_llm": "llama3.3",
  "quick_think_llm": "llama3.1",
  "backend_url": "http://localhost:11434/v1",
  "max_debate_rounds": 1,
  "max_risk_discuss_rounds": 1,
  "data_vendors": {
    "core_stock_apis": "yfinance",
    "technical_indicators": "yfinance",
    "fundamental_data": "yfinance",
    "news_data": "yfinance"
  }
}
```

### Use Custom Config

```bash
# With analyzer
python -m tradingagents.analyze AAPL --config my_config.json

# Note: Screener doesn't support custom config yet (uses default)
```

---

## Model Recommendations

### For Ollama

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| llama3.1 | 8B | Fast | Good | Quick analysis, screening |
| llama3.3 | 70B | Slow | Excellent | Deep analysis, debates |
| mistral | 7B | Fast | Good | Alternative to llama3.1 |
| qwen2.5 | 7B-72B | Varies | Good-Excellent | Alternative options |

**Recommended Setup:**
- **Quick thinking:** llama3.1 (8B) - Fast for analyst reports
- **Deep thinking:** llama3.3 (70B) - Better for final decisions

**Budget Setup (Faster, Less Accurate):**
- **Both:** llama3.1 (8B) - Faster but lower quality

**High Quality Setup (Slower):**
- **Both:** llama3.3 (70B) - Best quality but much slower

### For Gemini

| Model | Speed | Quality | Best For |
|-------|-------|---------|----------|
| gemini-2.0-flash-lite | Very Fast | Good | Quick analysis |
| gemini-2.0-flash | Fast | Excellent | Most analyses |
| gemini-2.5-flash | Fast | Excellent | Premium quality |

### For OpenAI

| Model | Speed | Quality | Cost | Best For |
|-------|-------|---------|------|----------|
| gpt-4o-mini | Very Fast | Good | Low | Quick analysis |
| gpt-4o | Fast | Excellent | Medium | Most analyses |
| o1-mini | Medium | Very High | High | Complex reasoning |

---

## Performance Comparison

### Analysis Time (Single Ticker)

| Provider | Quick Model | Deep Model | Total Time | Cost |
|----------|-------------|------------|------------|------|
| Ollama (llama3.1 + llama3.3) | - | - | 3-5 min | Free |
| Ollama (llama3.1 only) | - | - | 1-3 min | Free |
| Gemini (flash-lite + flash) | - | - | 30-60 sec | ~$0.01-0.05 |
| OpenAI (gpt-4o-mini + gpt-4o) | - | - | 30-90 sec | ~$0.10-0.30 |

**Note:** Ollama times depend heavily on your hardware (GPU/CPU/RAM)

---

## Switching Providers

### Quick Switch Method

**Option A: Edit default_config.py directly**
```python
# For Ollama (default)
"llm_provider": "ollama",
"deep_think_llm": "llama3.3",
"quick_think_llm": "llama3.1",
"backend_url": "http://localhost:11434/v1",

# For Gemini
"llm_provider": "google",
"deep_think_llm": "gemini-2.0-flash",
"quick_think_llm": "gemini-2.0-flash-lite",
"backend_url": "",

# For OpenAI
"llm_provider": "openai",
"deep_think_llm": "gpt-4o",
"quick_think_llm": "gpt-4o-mini",
"backend_url": "https://api.openai.com/v1",
```

**Option B: Use pre-made config files**
```bash
# Copy one of the pre-made configs
cp config_ollama.json my_config.json
# OR
cp config_gemini.json my_config.json

# Use it
python -m tradingagents.analyze AAPL --config my_config.json
```

---

## Troubleshooting

### "Failed to connect to Ollama"

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start Ollama
ollama serve
```

### "Model not found"

```bash
# Pull the required models
ollama pull llama3.1
ollama pull llama3.3
ollama pull nomic-embed-text
```

### "Google API key not found"

```bash
# Set your API key
export GOOGLE_API_KEY="your-key-here"

# Or add to ~/.bashrc or ~/.zshrc
echo 'export GOOGLE_API_KEY="your-key-here"' >> ~/.zshrc
```

### "OpenAI API key not found"

```bash
# Set your API key
export OPENAI_API_KEY="sk-your-key"

# Or add to ~/.bashrc or ~/.zshrc
echo 'export OPENAI_API_KEY="sk-your-key"' >> ~/.zshrc
```

### Analysis is very slow

**Solutions:**
1. Use smaller models:
   ```python
   "deep_think_llm": "llama3.1",  # Instead of llama3.3
   "quick_think_llm": "llama3.1",
   ```

2. Switch to cloud provider (Gemini/OpenAI) for speed

3. Upgrade hardware (more RAM/better GPU for Ollama)

---

## Recommended Configurations

### For Testing/Development
```json
{
  "llm_provider": "ollama",
  "deep_think_llm": "llama3.1",
  "quick_think_llm": "llama3.1"
}
```
**Why:** Fast, free, good enough for testing

### For Production (Free)
```json
{
  "llm_provider": "ollama",
  "deep_think_llm": "llama3.3",
  "quick_think_llm": "llama3.1"
}
```
**Why:** Best quality while staying free

### For Production (Paid, Fast)
```json
{
  "llm_provider": "google",
  "deep_think_llm": "gemini-2.0-flash",
  "quick_think_llm": "gemini-2.0-flash-lite"
}
```
**Why:** Fast inference, good quality, reasonable cost

---

## Current Status ✅

**Your system is configured for:**
- ✅ **Provider:** Ollama (local, no API keys)
- ✅ **Models:** llama3.3 (deep) + llama3.1 (quick)
- ✅ **Data:** yfinance (no API keys)
- ✅ **Cost:** $0 (everything free)

**You're ready to test!** Just make sure Ollama is running with the required models.

```bash
# Quick test
python -m tradingagents.analyze AAPL
```

If you want to switch to Gemini or OpenAI, follow the configuration steps above.
