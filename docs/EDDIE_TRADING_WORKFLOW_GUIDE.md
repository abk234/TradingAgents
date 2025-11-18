# 🚀 Eddie Trading Workflow Guide
## Complete Guide to Using Eddie for Trading Decisions

**Last Updated:** November 17, 2025

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Daily Trading Workflows](#daily-trading-workflows)
3. [Understanding Eddie's Recommendations](#understanding-eddies-recommendations)
4. [Workflow Examples by Trading Style](#workflow-examples-by-trading-style)
5. [Best Practices](#best-practices)
6. [Advanced Features](#advanced-features)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Step 1: Launch Eddie

```bash
# Option 1: Use the launcher script
./trading_bot.sh

# Option 2: Direct Python command
venv/bin/python -m tradingagents.bot

# Option 3: Using Chainlit directly
venv/bin/chainlit run tradingagents/bot/chainlit_app.py
```

**Eddie will open in your browser at:** `http://localhost:8000`

### Step 2: Prerequisites Check

Before starting, ensure:
- ✅ **Ollama** is running (`ollama serve`)
- ✅ **llama3.3** model is downloaded (`ollama pull llama3.3`)
- ✅ **Database** has recent stock data (run `./scripts/run_daily_analysis.sh` if needed)
- ✅ **Portfolio value** is configured in `tradingagents/default_config.py`

### Step 3: Your First Conversation

**Try this:**
```
You: "What are the best stocks right now?"

Eddie: [Runs market screener, analyzes sectors, shows top opportunities]
```

---

## 📅 Daily Trading Workflows

### Morning Routine (Before Market Open)

**Goal:** Identify opportunities for the day

#### Workflow 1: Market Overview
```
1. Ask Eddie: "What data do you have?"
   → Eddie shows database status and strategic recommendations

2. Ask Eddie: "What are the best stocks right now?"
   → Eddie runs screener, shows top opportunities with scores

3. Review sector strength:
   → Look for sectors >30% strength
   → Avoid sectors <20% strength
```

#### Workflow 2: Quick Opportunity Scan
```
1. Ask Eddie: "Run screener and show top 10"
   → Fast scan (10-30 seconds)

2. Filter by your criteria:
   → "Show me tech stocks with score above 40"
   → "What healthcare stocks look good?"

3. Get quick checks on top picks:
   → "What's the news on AAPL?" (10 seconds)
   → "Show me TSLA's technicals" (10 seconds)
```

### Pre-Trade Analysis (Before Making Decision)

**Goal:** Get comprehensive analysis before buying/selling

#### Workflow 3: Deep Stock Analysis
```
1. Ask Eddie: "Should I buy AAPL? My portfolio is $100k"
   → Eddie runs full analysis (30-90 seconds)
   → Coordinates all 8 agents
   → Provides BUY/SELL/HOLD recommendation

2. Review Eddie's analysis:
   ✅ Decision: BUY/SELL/HOLD
   ✅ Confidence score (0-100%)
   ✅ Bull case (why it could go up)
   ✅ Bear case (risks and downsides)
   ✅ Entry price recommendation
   ✅ Stop loss level
   ✅ Position sizing (e.g., 3-5% of portfolio)
   ✅ Expected return and holding period

3. Validate the recommendation:
   → "Check earnings risk for AAPL"
   → "Validate price sources for AAPL"
   → "Check data quality for AAPL"
```

#### Workflow 4: Learning from Past
```
1. Before analyzing, check Eddie's track record:
   → "What did you learn about AAPL?"
   → "Have you seen this pattern before?"
   → "What did you say about TSLA last time?"

2. Use pattern recognition:
   → Eddie finds similar situations
   → Shows what happened in past cases
   → Helps avoid repeating mistakes
```

### Trade Execution (Manual)

**Goal:** Execute trades based on Eddie's recommendations

#### Workflow 5: Execute Buy Order
```
1. Get Eddie's recommendation:
   → "Should I buy NVDA? Portfolio: $100k"
   → Eddie provides: BUY, 75% confidence, entry $520, stop $495

2. Review validation:
   ✅ Earnings risk: LOW (earnings in 30 days)
   ✅ Price validation: 9.2/10 (multi-source agreement)
   ✅ Data quality: 8.5/10 (fresh data)

3. Calculate position size:
   → Eddie recommends: 5% of portfolio = $5,000
   → Entry price: $520
   → Shares: ~9 shares ($5,000 / $520)

4. Execute in your broker:
   → Place limit order at $520 (or market if urgent)
   → Set stop loss at $495
   → Set target price (if provided by Eddie)

5. Track the trade:
   → "Show my portfolio status"
   → Monitor performance over time
```

#### Workflow 6: Portfolio Management
```
1. Weekly review:
   → "Show my portfolio status"
   → "What should I rebalance?"

2. Check underperformers:
   → "What did you say about [LOSING_STOCK]?"
   → "Should I sell [LOSING_STOCK]?"

3. Add to winners:
   → "Should I add more to [WINNING_STOCK]?"
   → Eddie checks if thesis still valid
```

---

## 🎯 Understanding Eddie's Recommendations

### Decision Types

**BUY** - Eddie recommends buying
- **Confidence 60-100%**: Strong buy signal
- **Confidence 50-59%**: Good buy signal
- **Confidence 40-49%**: Moderate - investigate further
- **When to act**: High confidence + good validation = execute
- **When to wait**: Low confidence or weak validation = wait

**HOLD** - Eddie recommends holding existing positions
- **Meaning**: Stock is fine, but not time to add more
- **Action**: Keep position, monitor

**SELL** - Eddie recommends selling
- **Meaning**: Exit position, thesis invalidated
- **Action**: Close position, take profit/loss

**WAIT** - Eddie recommends waiting
- **Meaning**: Not a good time to enter
- **Reasons**: Earnings coming, weak signals, poor timing
- **Action**: Wait for better entry point

### Confidence Scores

| Score Range | Meaning | Action |
|------------|---------|--------|
| **80-100%** | Very High Confidence | Strong buy/sell signal - act decisively |
| **60-79%** | High Confidence | Good signal - proceed with normal position size |
| **40-59%** | Moderate Confidence | Investigate further - smaller position size |
| **20-39%** | Low Confidence | Weak signal - avoid or very small position |
| **0-19%** | Very Low Confidence | No signal - avoid |

### Priority Scores (0-100)

From the screener:
- **60-100**: 🔥 Strong buy candidate
- **50-59**: ✅ Good buy signal
- **40-49**: ⚠️ Moderate - worth investigating
- **30-39**: ⏸️ Weak signal
- **0-29**: ❌ No signal - avoid

### Sector Strength

- **>40%**: 💪 Strong sector - good opportunities
- **20-40%**: ➖ Neutral sector - moderate opportunities
- **<20%**: 📉 Weak sector - few opportunities

**Rule:** Focus on sectors >30% strength. Avoid sectors <20% unless you have strong conviction.

---

## 💼 Workflow Examples by Trading Style

### Style 1: Conservative Value Investor

**Goal:** Buy undervalued stocks, hold long-term

#### Daily Workflow:
```
1. Morning: "What are the best value opportunities?"
   → Eddie filters for low P/E, strong fundamentals

2. Analysis: "Analyze [TICKER] for value investing"
   → Focus on fundamentals gate
   → Check dividend yield
   → Verify financial health

3. Entry: Wait for technical confirmation
   → "What's the technical setup for [TICKER]?"
   → Look for RSI < 40 (not overbought)
   → Price near support levels

4. Position: 3-5% per stock, 10-15 stocks total
   → Diversify across sectors
   → Hold for 6-12 months minimum
```

#### Example Conversation:
```
You: "Find me undervalued dividend stocks"

Eddie: [Shows stocks with high dividend yield, low P/E]

You: "Analyze JNJ for value investing, portfolio $100k"

Eddie: [Full analysis with BUY recommendation, 65% confidence]
       - Entry: $165
       - Stop: $155
       - Position: 4% = $4,000
       - Dividend yield: 3.2%
       - Expected return: 15% over 12 months

You: [Review validation, execute trade in broker]
```

### Style 2: Growth Trader

**Goal:** Buy momentum stocks, hold 1-6 months

#### Daily Workflow:
```
1. Morning: "What stocks have strong momentum?"
   → Eddie shows stocks with high momentum scores
   → Focus on sectors with >40% strength

2. Quick checks: "What's the news on [TICKER]?"
   → Check for catalysts
   → Verify momentum is sustainable

3. Analysis: "Should I buy [TICKER]? Portfolio $100k"
   → Full analysis with all agents
   → Focus on technical and timing gates

4. Entry: Enter on breakouts or pullbacks
   → Use Eddie's entry price recommendation
   → Set stop loss as recommended

5. Exit: Use trailing stops
   → "What's my exit strategy for [TICKER]?"
   → Take partial profits at 5%, 10%, 15% gains
```

#### Example Conversation:
```
You: "What are the best momentum stocks?"

Eddie: [Shows top momentum picks with scores]

You: "Should I buy NVDA? Portfolio $100k"

Eddie: [Full analysis]
       - BUY, 78% confidence
       - Strong momentum + positive news
       - Entry: $520
       - Stop: $495 (trailing)
       - Position: 6% = $6,000
       - Target: $600 (15% gain)

You: [Execute trade, set trailing stop]
```

### Style 3: Swing Trader

**Goal:** 3-10 day trades, technical setups

#### Daily Workflow:
```
1. Morning: "Run screener, show top 20"
   → Quick scan for opportunities

2. Technical focus: "Show me TSLA's technicals"
   → Quick technical check (10 seconds)
   → Look for setups: RSI oversold, MACD cross, support bounce

3. Analysis: "Analyze [TICKER] for swing trading"
   → Focus on technical and timing gates
   → Check for catalysts (news, earnings)

4. Entry: Enter on technical signals
   → Use Eddie's entry price
   → Tight stop loss (2-3%)

5. Exit: Quick profits
   → Take profits at 3-5% gains
   → Use trailing stops
   → Exit if thesis invalidated
```

#### Example Conversation:
```
You: "What stocks have good swing setups?"

Eddie: [Shows stocks with technical signals]

You: "Show me AAPL's technicals"

Eddie: [Quick technical check]
       - RSI: 35 (oversold)
       - MACD: Bullish cross forming
       - Support: $175
       - Entry: $176-177

You: "Should I buy AAPL for swing trade?"

Eddie: [Full analysis]
       - BUY, 62% confidence
       - Good technical setup
       - Entry: $176
       - Stop: $171 (3%)
       - Target: $182 (3.4% gain)
       - Hold: 3-7 days

You: [Execute swing trade]
```

### Style 4: Dividend Investor

**Goal:** Build passive income, focus on dividends

#### Daily Workflow:
```
1. Screening: "Find me dividend stocks with yield > 4%"
   → Eddie filters for high dividend yield

2. Safety check: "Analyze [TICKER] for dividend safety"
   → Check payout ratio < 80%
   → Verify 5+ years of payments
   → Confirm dividend growth

3. Entry timing: "Should I buy [TICKER] now?"
   → Look for good entry price
   → Avoid overbought conditions

4. Position: Larger positions (5-10% per stock)
   → Focus on 10-15 dividend stocks
   → Hold long-term for income
```

#### Example Conversation:
```
You: "Find high dividend stocks"

Eddie: [Shows stocks with >4% yield]

You: "Analyze T for dividend investing, portfolio $100k"

Eddie: [Full analysis]
       - BUY, 70% confidence
       - Dividend yield: 6.8%
       - Payout ratio: 58% (safe)
       - 20+ years of payments
       - Entry: $18.50
       - Position: 8% = $8,000
       - Annual income: $544

You: [Execute trade, set up dividend reinvestment]
```

---

## ✅ Best Practices

### 1. Always Validate Before Trading

**Before executing any trade:**
```
✅ Check earnings risk: "Check earnings risk for [TICKER]"
✅ Validate prices: "Validate price sources for [TICKER]"
✅ Check data quality: "Check data quality for [TICKER]"
✅ Review Eddie's track record: "What did you learn about [TICKER]?"
```

### 2. Use Position Sizing

**Eddie's recommendations:**
- **High confidence (70%+)**: 5-7% of portfolio
- **Medium confidence (50-69%)**: 3-5% of portfolio
- **Low confidence (40-49%)**: 1-3% of portfolio
- **Very low (<40%)**: Avoid or <1%

**Never risk more than 10% per position!**

### 3. Set Stop Losses

**Always use Eddie's stop loss recommendations:**
- High confidence: Tighter stops (2-3%)
- Lower confidence: Wider stops (3-5%)
- Volatile stocks: Wider stops (5-7%)

### 4. Diversify

**Portfolio guidelines:**
- **Sectors**: 3-5 different sectors
- **Positions**: 10-20 stocks (depending on portfolio size)
- **Correlation**: Avoid highly correlated stocks
- **Max sector exposure**: 30-35% per sector

### 5. Monitor and Review

**Weekly:**
- "Show my portfolio status"
- Review underperformers
- Check if thesis still valid

**Monthly:**
- "What should I rebalance?"
- Review Eddie's track record
- Adjust strategy based on performance

### 6. Learn from Mistakes

**After a losing trade:**
```
→ "What did you say about [LOSING_STOCK]?"
→ "What did you learn from this?"
→ "Have you seen this pattern before?"
```

**Eddie learns from outcomes - use this to improve!**

---

## 🎓 Advanced Features

### 1. Pattern Recognition

**Find similar situations:**
```
You: "Have you seen this pattern before for AAPL?"

Eddie: [Searches past analyses using RAG]
       - Found 3 similar setups
       - 2 went up 12% average
       - 1 went down 5%
       - Pattern: Strong momentum + positive news
```

### 2. Track Record Review

**Check Eddie's accuracy:**
```
You: "What did you learn about TSLA?"

Eddie: [Shows learning summary]
       - Analyzed 7 times
       - Average confidence: 78%
       - Win rate: 71% (5 wins, 2 losses)
       - Average return: +8.5%
       - Best call: +22% gain
       - Worst call: -6% loss
```

### 3. Data Intelligence Dashboard

**Strategic planning:**
```
You: "What data do you have?"

Eddie: [Shows comprehensive dashboard]
       - Watchlist: 110 stocks
       - Latest scan: FRESH (3 hours old)
       - Top 5 opportunities
       - Strategic recommendations
       - Data quality status
```

### 4. Multi-Source Validation

**Verify data reliability:**
```
You: "Validate price sources for AAPL"

Eddie: [Cross-validates prices]
       - yfinance: $175.25
       - Alpha Vantage: $175.28
       - Discrepancy: 0.02% (excellent)
       - Validation score: 9.5/10
```

### 5. Earnings Risk Detection

**Avoid volatility traps:**
```
You: "Check earnings risk for AAPL"

Eddie: [Checks earnings proximity]
       - ⚠️ HIGH RISK: Earnings in 2 days
       - Recommendation: AVOID new positions
       - Wait until after earnings (3+ days)
```

---

## 🔧 Troubleshooting

### Problem: Eddie is slow

**Solutions:**
- Use quick checks for specific questions (5-15 seconds)
- Full analysis takes 30-90 seconds (normal)
- Check if database is responsive
- Ensure Ollama is running properly

### Problem: No recommendations

**Possible causes:**
- Market is weak (all sectors <30%)
- Data is stale (run `./scripts/run_daily_analysis.sh`)
- No stocks meet criteria
- Database needs update

**Solutions:**
- "What data do you have?" (check freshness)
- Run screener: "Run screener"
- Check sector strength: "How are sectors doing?"

### Problem: Recommendations seem wrong

**Validation steps:**
1. Check data quality: "Check data quality for [TICKER]"
2. Validate prices: "Validate price sources for [TICKER]"
3. Check earnings risk: "Check earnings risk for [TICKER]"
4. Review track record: "What did you learn about [TICKER]?"

### Problem: Can't connect to Eddie

**Check:**
- Ollama is running: `ollama serve`
- Model is downloaded: `ollama pull llama3.3`
- Port 8000 is available
- Database is accessible

---

## 📊 Example Complete Workflow

### Scenario: Finding and Trading a Stock

**Step 1: Morning Scan**
```
You: "What are the best stocks right now?"

Eddie: [Runs screener]
       📊 Market Overview:
       - Healthcare sector: 28.5% (strongest)
       - All sectors <30% (sideways market)
       
       Top 3 Opportunities:
       1. DHR - Score 41/100, Healthcare
       2. MRK - Score 41/100, Healthcare
       3. DE - Score 40/100, Industrials
       
       ⚠️ Market is sideways - proceed cautiously
```

**Step 2: Quick Check**
```
You: "What's the news on DHR?"

Eddie: [Quick news check - 10 seconds]
       📰 Recent News:
       - Positive earnings beat
       - New product launch
       - Analyst upgrades
       - Sentiment: Bullish
```

**Step 3: Deep Analysis**
```
You: "Should I buy DHR? My portfolio is $100k"

Eddie: [Full analysis - 60 seconds]
       🔍 Comprehensive Analysis:
       
       Decision: BUY
       Confidence: 65%
       
       Bull Case:
       - Strong fundamentals
       - Positive momentum
       - Good entry point
       
       Bear Case:
       - Market is sideways
       - Moderate score (41/100)
       
       Entry: $242
       Stop Loss: $230
       Target: $265
       Position Size: 4% = $4,000
       Shares: ~16 shares
       Expected Return: 9.5% over 60 days
```

**Step 4: Validation**
```
You: "Check earnings risk for DHR"

Eddie: ✅ Earnings Risk: LOW
       - Next earnings in 28 days (safe window)

You: "Validate price sources for DHR"

Eddie: ✅ Price Validation: 9.2/10
       - yfinance: $242.15
       - Alpha Vantage: $242.18
       - Discrepancy: 0.01% (excellent)

You: "Check data quality for DHR"

Eddie: ✅ Data Quality: 8.5/10
       - Fresh data (2 hours old)
       - Multi-source validation
       - All checks passed
```

**Step 5: Learning Check**
```
You: "What did you learn about DHR?"

Eddie: 📚 Learning Summary:
       - Analyzed 3 times previously
       - Average confidence: 68%
       - Win rate: 67% (2 wins, 1 loss)
       - Average return: +7.2%
       
       Similar patterns found:
       - 2 similar setups went up 8-12%
       - 1 similar setup went down 3%
```

**Step 6: Execute Trade**
```
[In your broker]
- Place limit order: Buy 16 shares DHR @ $242
- Set stop loss: $230
- Set target: $265
- Position size: $4,000 (4% of portfolio)
```

**Step 7: Monitor**
```
[Weekly check]
You: "Show my portfolio status"

Eddie: [Shows portfolio]
       DHR: +5.2% ($4,208 value)
       - Still bullish thesis
       - Consider trailing stop at $250
```

---

## 🎯 Key Takeaways

1. **Eddie is a research assistant** - Provides analysis and recommendations
2. **You execute trades** - Manual execution through your broker
3. **Always validate** - Check earnings risk, validate prices, review data quality
4. **Use position sizing** - Follow Eddie's recommendations (3-5% typical)
5. **Set stop losses** - Always use Eddie's stop loss recommendations
6. **Learn from outcomes** - Review Eddie's track record and learn from mistakes
7. **Diversify** - Don't put all eggs in one basket
8. **Monitor regularly** - Weekly portfolio reviews, monthly rebalancing

---

## 📚 Additional Resources

- **Quick Start Guide**: `QUICK_START_GUIDE.md`
- **Bot Guide**: `docs/BOT_GUIDE.md`
- **Profit Guide**: `docs/PROFIT_MAKING_GUIDE.md`
- **Validation Guide**: `docs/VALIDATION_GUIDE.md`

---

## 💡 Pro Tips

1. **Start with quick checks** - Use 5-15 second checks before full analysis
2. **Check data freshness** - Always verify data is current before trading
3. **Use pattern recognition** - Learn from similar past situations
4. **Track performance** - Review Eddie's track record regularly
5. **Combine with your research** - Eddie augments, doesn't replace your judgment
6. **Be patient** - Wait for high-confidence setups (>60%)
7. **Cut losses quickly** - Use stop losses religiously
8. **Let winners run** - Use trailing stops for profits

---

**Happy Trading! 🚀**

Remember: Eddie provides intelligent analysis, but you make the final decisions. Always do your own research and never risk more than you can afford to lose.

