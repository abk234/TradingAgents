# Basic Usage Examples

## Quick Start

### 1. Run Interactive Analysis
```bash
./trading_agents.sh
# Select option 1: Interactive Analysis
```

### 2. Run Daily Screener
```bash
python -m tradingagents.screener run
```

### 3. Analyze Top Opportunity
```bash
python -m tradingagents.screener top 1
# Then analyze the top ticker
python -m tradingagents.analyze XOM
```

## Common Workflows

### Daily Routine

```bash
# 1. Run screener
python -m tradingagents.screener run

# 2. View top opportunities
python -m tradingagents.screener top 5

# 3. Analyze top pick
python -m tradingagents.analyze XOM --plain-english --portfolio-value 100000

# 4. Check morning briefing
python -m tradingagents.insights morning
```

### Portfolio Management

```bash
# View portfolio
python -m tradingagents.portfolio view

# Buy stock
python -m tradingagents.portfolio buy AAPL 10 150.50

# View performance
python -m tradingagents.portfolio performance --days 30

# View dividends
python -m tradingagents.portfolio dividends --days 90
```

### Performance Tracking

```bash
# Generate performance report
python -m tradingagents.evaluate report --period 30

# Update outcomes
python -m tradingagents.evaluate update --days 30

# View statistics
python -m tradingagents.evaluate stats
```

## Programmatic Usage

### Basic Analysis
```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Initialize
ta = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG.copy())

# Run analysis
_, decision = ta.propagate("NVDA", "2024-05-10")
print(decision)
```

### Custom Configuration
```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Create custom config
config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "gpt-4o"
config["quick_think_llm"] = "gpt-4o-mini"
config["max_debate_rounds"] = 2

# Initialize
ta = TradingAgentsGraph(debug=True, config=config)

# Run analysis
_, decision = ta.propagate("AAPL", "2024-01-15")
print(decision)
```

### With Gemini
```python
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "google"
config["deep_think_llm"] = "gemini-2.0-flash"
config["quick_think_llm"] = "gemini-2.0-flash-lite"

ta = TradingAgentsGraph(debug=True, config=config)
_, decision = ta.propagate("TSLA", "2024-01-15")
```

### With Ollama
```python
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "ollama"
config["backend_url"] = "http://localhost:11434/v1"
config["deep_think_llm"] = "llama3.3"
config["quick_think_llm"] = "llama3.1"

ta = TradingAgentsGraph(debug=True, config=config)
_, decision = ta.propagate("MSFT", "2024-01-15")
```

---

**Next**: [[Advanced-Usage|Advanced Usage]] | [[Programmatic-Usage|Programmatic Usage]]

