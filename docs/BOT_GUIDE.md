# 🤖 Eddie - AI Trading Expert

## Meet Eddie

Eddie is your evolving AI trading assistant powered by the TradingAgents platform. Eddie uses advanced language models (llama3.3) combined with specialized trading tools to provide intelligent market analysis and trading recommendations. Eddie learns and grows smarter with each interaction, using specialized agents to deliver the best possible trading insights.

## 🚀 Quick Start

### Launch the Bot

```bash
# Simple - just run the launcher
./trading_bot.sh

# Or use Python directly
venv/bin/python -m tradingagents.bot

# Or use Chainlit
venv/bin/chainlit run tradingagents/bot/chainlit_app.py
```

The bot will open in your browser at **http://localhost:8000**

### Prerequisites

✅ **Ollama** running on http://localhost:11434
✅ **llama3.3** model downloaded (`ollama pull llama3.3`)
✅ **Database** with stock data
✅ **Chainlit** installed (`pip install chainlit`)

## 💬 Example Conversations

### Finding Opportunities

**You:** "What are the best stocks right now?"

**Bot:**
- Runs market screener
- Analyzes all sectors
- Shows top opportunities with scores
- Warns if market is weak
- Suggests next actions

**You:** "Show me tech stocks above 40"

**Bot:**
- Filters for Technology sector
- Shows stocks with priority score ≥40
- Lists with details

### Deep Analysis

**You:** "Analyze AAPL for me, my portfolio is $100k"

**Bot:**
- Performs comprehensive AI analysis (takes 30-90 seconds)
- Shows BUY/HOLD/SELL recommendation
- Provides confidence score
- Explains bull and bear cases
- Suggests position sizing

### Understanding Results

**You:** "What does priority score mean?"

**Bot:**
- Explains the metric in detail
- Shows interpretation ranges
- Gives examples
- Suggests how to use it

**You:** "Show me the legend"

**Bot:**
- Displays complete metrics guide
- Explains all indicators
- Provides strategy recommendations

### Sector Analysis

**You:** "How is healthcare doing?"

**Bot:**
- Analyzes Healthcare sector
- Shows strength score and momentum
- Lists top stocks in that sector
- Provides sector-specific recommendation

## 🛠️ Available Commands (Natural Language)

### Screening & Discovery
- "What stocks should I look at?"
- "Run a market scan"
- "Show me top 10 opportunities"
- "Find opportunities in energy sector"
- "What's hot right now?"

### Stock Analysis
- "Analyze TSLA"
- "Should I buy Microsoft?"
- "Give me details on DHR"
- "Compare AAPL and MSFT"
- "Quick summary of NVDA"

### Sector Analysis
- "How is tech doing?"
- "Show me healthcare stocks"
- "What's the strongest sector?"
- "Analyze the energy sector"

### Education & Help
- "What does momentum mean?"
- "Explain T/V/M/F scores"
- "Show the legend"
- "How do I read these results?"
- "What's a good priority score?"

### Portfolio (Coming Soon)
- "Show my portfolio"
- "What's my performance?"
- "How am I doing?"

## 📊 Understanding the Bot's Intelligence

### The Bot Knows About:

**Technical Analysis**
- MACD, RSI, Bollinger Bands
- Volume analysis and momentum
- Support/resistance levels

**Fundamental Analysis**
- P/E ratios and market cap
- Earnings and growth metrics
- Company financials

**Sector Trends**
- Industry rotation
- Sector strength scores
- Cross-sector comparisons

**Risk Management**
- Position sizing (5% default)
- Diversification strategies
- Stop-loss recommendations

### The Bot's Personality

✅ **Honest** - Warns when markets are weak
✅ **Educational** - Explains concepts as it works
✅ **Conservative** - Better to miss opportunity than lose money
✅ **Actionable** - Always provides specific next steps
✅ **Data-Driven** - Uses real database, not made-up numbers

## 🎯 Features

### 1. **Natural Language Understanding**

No commands to memorize:
- "What's good in tech?" → Runs sector analysis
- "Compare Apple and Google" → Deep comparison
- "Why is this rated 41?" → Explains scoring

### 2. **Intelligent Recommendations**

Context-aware advice:
- Suggests waiting when markets are weak
- Recommends deeper analysis when needed
- Provides portfolio allocation guidance

### 3. **Rich Responses**

Formatted output:
- Tables for screener results
- Structured analysis reports
- Color-coded recommendations
- Clear action items

### 4. **Conversation Memory**

Remembers context:
- References previous queries
- Builds on discussion
- Maintains session history

## 🧠 How It Works

### Architecture

```
User Query
    ↓
LangGraph ReAct Agent (llama3.3)
    ↓
Selects Appropriate Tools
    ↓
Executes: run_screener, analyze_stock, etc.
    ↓
Synthesizes Results
    ↓
Natural Language Response
```

### Available Tools (10+)

1. `run_screener` - Daily market scan
2. `get_top_stocks` - Top opportunities
3. `analyze_sector` - Sector strength
4. `search_stocks` - Filter by criteria
5. `analyze_stock` - Deep AI analysis
6. `get_stock_summary` - Quick overview
7. `get_stock_info` - Company details
8. `explain_metric` - Metric explanations
9. `show_legend` - Complete guide
10. `get_portfolio_status` - Portfolio view

## ⚙️ Configuration

### Custom Settings

Edit `tradingagents/bot/agent.py`:

```python
agent = TradingAgent(
    model_name="llama3.3",  # Change model
    temperature=0.7,         # Adjust creativity
    debug=True              # Enable detailed logging
)
```

### Chat Profiles

The bot has 3 modes:
- **Standard**: Full capabilities
- **Quick Screener**: Fast market scans
- **Deep Analysis**: Detailed AI insights

## 📈 Best Practices

### For Best Results:

1. **Be Specific**
   - ❌ "stocks"
   - ✅ "show me tech stocks above 40"

2. **Ask Follow-ups**
   - Initial: "What's good?"
   - Follow-up: "Analyze the top one for me"

3. **Use Context**
   - "Tell me more about that"
   - "What about the second one?"

4. **Specify Your Portfolio**
   - "Analyze AAPL, I have $50k to invest"
   - Helps with position sizing

### When Market is Weak:

The bot will warn you:
- "All sectors showing <30% strength"
- "Consider waiting for better opportunities"
- "Market is sideways"

**Don't force trades!** Listen to the bot's warnings.

## 🐛 Troubleshooting

### Bot Won't Start

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Check llama3.3 is available
ollama list

# Restart Ollama
ollama serve
```

### Slow Responses

- Deep analysis takes 30-90 seconds (normal)
- Initial model load takes ~10 seconds
- Complex queries may take longer

### "Tool Error" Messages

- Check database has recent data
- Run screener first: `venv/bin/python -m tradingagents.screener run`
- Ensure tickers are in database

## 🔐 Security

### Authentication (Optional)

Edit `chainlit_app.py` to add password protection:

```python
@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # Add your authentication logic
    if username == "trader" and password == "secret":
        return cl.User(identifier=username)
    return None
```

## 🎨 Customization

### Modify System Prompt

Edit `tradingagents/bot/prompts.py`:
- Add your trading strategies
- Customize personality
- Add specific knowledge

### Add New Tools

Edit `tradingagents/bot/tools.py`:

```python
@tool
def my_custom_tool(param: str) -> str:
    """Your tool description."""
    # Implementation
    return "Result"
```

Add to `get_all_tools()` list.

## 📞 Support

### Issues?

1. Check logs in terminal
2. Verify prerequisites
3. Test individual tools
4. Review error messages

### Example Error Handling

```
User: "Analyze XYZ"
Bot: "Ticker XYZ not found in database."
```

This is good! Bot knows when data isn't available.

## 🚀 Advanced Usage

### Batch Analysis

**You:** "Analyze the top 5 stocks for me"

**Bot:** Runs deep analysis on each sequentially.

### Complex Queries

**You:** "Find healthcare stocks above 45 with strong momentum, analyze the top 2"

**Bot:**
1. Filters stocks
2. Identifies top 2
3. Runs deep analysis
4. Provides comparison

### Strategy Development

**You:** "I want a defensive portfolio strategy"

**Bot:**
- Recommends Consumer Defensive and Utilities sectors
- Suggests stocks with low volatility
- Explains defensive investing principles

## 💡 Tips & Tricks

1. **Morning Routine**: "What should I focus on today?"
2. **Sector Rotation**: "Which sector is strongest?"
3. **Risk Check**: "Are there any warnings I should know about?"
4. **Education**: "Teach me about RSI"
5. **Comparison**: "Compare healthcare vs technology"

## 📝 Changelog

### v1.0 (Current)
- Natural language interface
- 10+ tools for screening and analysis
- Sector strength analysis
- Deep AI-powered stock analysis
- Metric explanations and education
- Context-aware recommendations
- Chainlit web UI

### Coming Soon
- Portfolio tracking integration
- Real-time price updates
- News sentiment analysis
- Technical chart display
- Multi-stock comparisons
- Custom watchlists
- Email/Slack alerts via bot

---

**Happy Trading!** 🎉

Remember: The bot is a tool to help you make informed decisions. Always do your own research and never invest more than you can afford to lose.
