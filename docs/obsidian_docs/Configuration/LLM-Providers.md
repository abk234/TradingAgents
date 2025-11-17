# LLM Providers Configuration

## Supported Providers

### OpenAI
**Models:**
- `gpt-4o`: Most capable, balanced
- `gpt-4o-mini`: Faster, cost-effective
- `o1-preview`: Deep reasoning
- `o3-mini`: Fast reasoning

**Setup:**
```bash
export OPENAI_API_KEY=your-key-here
```

**Configuration:**
```python
config["llm_provider"] = "openai"
config["deep_think_llm"] = "gpt-4o"
config["quick_think_llm"] = "gpt-4o-mini"
```

### Google Gemini
**Models:**
- `gemini-2.0-flash-lite`: Fast, efficient
- `gemini-2.0-flash`: Balanced
- `gemini-2.5-flash`: Enhanced capabilities

**Setup:**
```bash
export GOOGLE_API_KEY=your-key-here
```

**Configuration:**
```python
config["llm_provider"] = "google"
config["deep_think_llm"] = "gemini-2.0-flash"
config["quick_think_llm"] = "gemini-2.0-flash-lite"
```

### Anthropic Claude
**Models:**
- `claude-3-5-sonnet-latest`: Most capable
- `claude-3-5-haiku-latest`: Fast, efficient

**Setup:**
```bash
export ANTHROPIC_API_KEY=your-key-here
```

**Configuration:**
```python
config["llm_provider"] = "anthropic"
config["deep_think_llm"] = "claude-3-5-sonnet-latest"
config["quick_think_llm"] = "claude-3-5-haiku-latest"
```

### Ollama (Local)
**Models:**
- `llama3.3`: 70.6B, most capable
- `llama3.1`: 8B, balanced
- `mistral`: 7B, efficient
- `qwen2.5`: Various sizes
- `0xroyce/plutus`: 8B, financial-focused

**Setup:**
1. Install Ollama: https://ollama.ai
2. Pull models: `ollama pull llama3.3`
3. Start Ollama server: `ollama serve`

**Configuration:**
```python
config["llm_provider"] = "ollama"
config["backend_url"] = "http://localhost:11434/v1"
config["deep_think_llm"] = "llama3.3"
config["quick_think_llm"] = "llama3.1"
```

### OpenRouter
**Access to multiple providers through single API.**

**Setup:**
```bash
export OPENROUTER_API_KEY=your-key-here
```

**Configuration:**
```python
config["llm_provider"] = "openrouter"
config["deep_think_llm"] = "openai/gpt-4o"
config["quick_think_llm"] = "openai/gpt-4o-mini"
```

## Configuration File

Edit `tradingagents/default_config.py`:

```python
DEFAULT_CONFIG = {
    "llm_provider": "ollama",  # or "openai", "google", "anthropic", "openrouter"
    "deep_think_llm": "llama3.3",
    "quick_think_llm": "llama3.1",
    "backend_url": "http://localhost:11434/v1",  # For Ollama
}
```

## Environment Variables

Create `.env` file:
```
OPENAI_API_KEY=your-key
GOOGLE_API_KEY=your-key
ANTHROPIC_API_KEY=your-key
ALPHA_VANTAGE_API_KEY=your-key
```

## Cost Considerations

- **OpenAI**: Pay per token, can be expensive for many calls
- **Gemini**: Generally more cost-effective
- **Anthropic**: Mid-range pricing
- **Ollama**: Free (local), requires GPU
- **OpenRouter**: Varies by model

## Model Selection Guide

### For Deep Thinking (Research, Analysis)
- **Best**: `gpt-4o`, `claude-3-5-sonnet`, `llama3.3`
- **Cost-effective**: `gemini-2.0-flash`, `llama3.1`

### For Quick Thinking (Fast responses)
- **Best**: `gpt-4o-mini`, `gemini-2.0-flash-lite`, `claude-3-5-haiku`
- **Local**: `llama3.1`, `mistral`

---

**Next**: [[Data-Vendors|Data Vendors]] | [[Environment|Environment Setup]]

