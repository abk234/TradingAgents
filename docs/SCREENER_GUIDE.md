# 📊 TradingAgents Screener - Complete Guide

## 🎯 Understanding Your Results

When you run the screener with sector analysis, you'll see several metrics. Here's what they all mean and how to use them.

---

## 📖 Metric Definitions

### 1. **Sector Strength** (0-100%)

**What it is:** Composite score combining technical indicators across all stocks in that sector

**Interpretation:**
- 🟢 **>40%**: Strong sector - Good opportunities likely
- 🟡 **20-40%**: Neutral - Moderate opportunities
- 🔴 **<20%**: Weak sector - Few opportunities

**Example from your output:**
```
Healthcare: 28.5% ← This is neutral, some opportunities
Energy: 27.2%     ← Also neutral
Technology: 18.2% ← This is weak, fewer opportunities
```

**What to do:** Focus on sectors with >30% strength for best results

---

### 2. **Stocks** (e.g., 0/10)

**What it is:** Number of buy signals / Total stocks analyzed in sector

**Interpretation:**
- First number = Stocks currently showing buy signals
- Second number = Total stocks tracked in that sector

**Example:**
```
Healthcare: 0/10 ← 0 stocks with buy signals out of 10 tracked
Industrials: 0/9  ← 0 stocks with buy signals out of 9 tracked
```

**Why all zeros?** This means currently no stocks are meeting the strict technical buy criteria (MACD bullish cross + RSI oversold + Volume spike). This is normal in sideways markets.

---

### 3. **Buy Signals** (Count)

**What it is:** Total number of bullish technical signals detected across all stocks in sector

**Types of signals:**
- **MACD Bullish Cross**: Moving averages crossing upward (momentum building)
- **RSI Oversold**: Stock potentially undervalued (RSI < 30)
- **Volume Spike**: Unusual trading activity (potential breakout)
- **Bollinger Band Touch**: Price at support/resistance levels

**Example:**
```
All showing "0" ← Currently a neutral market, no strong technical triggers
```

**What to do:** When you see buy signals > 0, those stocks deserve deeper analysis

---

### 4. **Avg Priority** (0-100)

**What it is:** Average priority score of all stocks in that sector

**Interpretation:**
- 🟢 **>50**: High priority - Strong buy candidates
- 🟡 **40-50**: Good priority - Worth investigating
- 🟠 **30-40**: Medium priority - Some interest
- 🔴 **<30**: Low priority - Weak signals

**Example from your output:**
```
Healthcare: 34.2% ← Medium priority, worth a look
Industrials: 33.0% ← Medium priority
Finance: 33.5% ← Medium priority
Technology: 30.2% ← Lower end of medium
```

**What to do:** Stocks with priority >40 are your best candidates

---

### 5. **Momentum** (Strong/Neutral/Weak)

**What it is:** Recent price trend combined with volume analysis

**Interpretation:**
- 🔥 **Strong**: Clear uptrend with increasing volume → Bullish
- ⚪ **Neutral**: Sideways movement → Wait and see
- 📉 **Weak**: Downtrend or declining volume → Bearish

**Example from your output:**
```
Most sectors showing "Neutral" ← Market is sideways, not trending
Finance, Technology, Consumer Defensive showing "Weak" ← Avoid these
```

**What to do:** Prefer "Strong" or "Neutral" over "Weak" momentum

---

## 🎯 How to Read Your Specific Results

Looking at your sector analysis output:

| Rank | Sector | Strength | Signals | Avg Priority | Momentum | **Action** |
|------|--------|----------|---------|--------------|----------|------------|
| 1 | Healthcare | 28.5% | 0/10, 0 | 34.2% | Neutral | ✅ **Top pick** - Moderate strength, neutral momentum |
| 2 | Energy | 27.2% | 0/10, 0 | 33.6% | Neutral | ✅ **Good** - Similar to Healthcare |
| 3 | Industrial | 26.6% | 0/1, 0 | 33.0% | Neutral | ✅ **Worth checking** - Fewer stocks but decent |
| 6 | Finance | 21.3% | 0/2, 0 | 33.5% | Weak | ⚠️ **Caution** - Weak momentum |
| 11 | Technology | 18.2% | 0/10, 0 | 30.2% | Weak | ❌ **Skip** - Low strength + weak momentum |

---

## 💡 Recommended Workflow

Based on your results, here's what to do next:

### Step 1: View Top Stocks
```bash
venv/bin/python -m tradingagents.screener top 10
```

This shows you the individual stocks ranked by priority score.

### Step 2: Focus on Healthcare & Energy Sectors
These showed the highest strength (28.5% and 27.2%). Look for stocks in these sectors with:
- Priority score >40
- Positive price change %
- Not showing "Weak" momentum

### Step 3: Deep Dive with AI
```bash
# Analyze specific stocks you identified
venv/bin/python -m tradingagents.analyze TICKER --plain-english

# Or use quick command
./quick_run.sh analyze TICKER
```

### Step 4: Check Again Tomorrow
When markets are sideways (like now), wait for better setups. Run the screener daily:
```bash
./quick_run.sh screener
```

---

## 🚨 What "All Zeros" Means

Your output shows:
- Buy Signals: All 0
- Stocks column: All 0/XX

**This is completely normal!** It means:

1. **Market is in a holding pattern** - No strong technical breakouts right now
2. **Quality over quantity** - The screener only flags HIGH-QUALITY signals
3. **Wait for better setups** - Don't force trades when technicals are weak

**What to do:**
- ✅ Still look at top priority stocks (>40 score)
- ✅ Focus on Healthcare and Energy sectors
- ✅ Run screener daily until you see buy signals appear
- ✅ Use AI analysis on interesting stocks
- ❌ Don't force trades just because the screener ran

---

## 🔍 Filtering & Next Steps

### View Just The Top Stocks
```bash
# See top 10 across all sectors (ignores sector analysis)
venv/bin/python -m tradingagents.screener top 10

# Or use quick command
./quick_run.sh top
```

### Get Help Anytime
```bash
# Show legend and interpretation guide
venv/bin/python -m tradingagents.screener legend

# Or from interactive shell
./trading_interactive.sh
# Select: 1 → Run screener
```

### Analyze Promising Stocks
```bash
# AI-powered deep dive
venv/bin/python -m tradingagents.analyze DHR --plain-english

# This gives you:
# - BUY/HOLD/SELL recommendation
# - Confidence score (0-100)
# - Position size for your portfolio
# - Bull and bear arguments
```

---

## 📊 Interpreting "Priority Score" for Individual Stocks

When you run `top 10`, you'll see stocks ranked by priority. Here's what different scores mean:

- **60-100**: 🔥 Strong buy signal - Multiple technical indicators aligning
- **50-59**: ✅ Good buy signal - Several positive indicators
- **40-49**: ⚠️ Moderate signal - Worth investigating with AI analysis
- **30-39**: ⏸️ Weak signal - Wait for better setup
- **0-29**: ❌ No signal - Avoid or wait

**Your data shows most stocks at 30-41**, which means:
- Market is providing some opportunities
- Not slam-dunk setups, but worth researching
- Use AI analysis to separate good from great

---

## 🎯 Summary: Your Action Plan

Based on your specific results:

### ✅ DO:
1. Run `./quick_run.sh top` to see top 10 individual stocks
2. Focus on Healthcare and Energy sectors (highest strength)
3. Look for stocks with priority >40
4. Use AI to analyze promising candidates:
   ```bash
   ./quick_run.sh analyze TICKER
   ```
5. Run screener daily to catch improving setups

### ❌ DON'T:
1. Don't panic about "all zeros" - this is normal in sideways markets
2. Don't ignore Technology sector (weak + low priority)
3. Don't force trades just to trade - wait for >40% sector strength
4. Don't skip AI analysis - technicals alone aren't enough

---

## 🔔 Want Automated Alerts?

Set up daily screening with Slack notifications:

```bash
# Add to your crontab
crontab -e

# Run screener every morning at 7 AM
0 7 * * 1-5 cd /path/to/TradingAgents && ./quick_run.sh screener
```

You'll get Slack notifications with top opportunities automatically!

---

## 📖 Quick Reference Commands

```bash
# Show legend/help
venv/bin/python -m tradingagents.screener legend

# Run screener with sector analysis
./quick_run.sh screener

# View top 10 stocks
./quick_run.sh top

# Analyze a specific stock with AI
./quick_run.sh analyze TICKER

# Interactive menu (easiest)
./trading_interactive.sh
```

---

## 💡 Pro Tips

1. **Best Screening Times**:
   - Before market open (6-9 AM) - Plan your day
   - After market close (4-6 PM) - Review what happened

2. **Combining Metrics**:
   - Look for: High sector strength + High priority + Neutral/Strong momentum
   - Avoid: Weak sector + Low priority + Weak momentum

3. **AI Analysis is Key**:
   - Technical indicators alone aren't enough
   - Always run AI analysis on candidates before buying
   - AI provides fundamental analysis, news sentiment, and risk assessment

4. **Track Your Decisions**:
   - The system tracks all recommendations automatically
   - Check performance: `./quick_run.sh evaluate`

---

**Remember:** The screener finds opportunities. YOU make the final decision. Always do your own research! 📚

---

## ❓ Still Have Questions?

Check the complete documentation:
- **INTERACTIVE_SHELL_GUIDE.md** - All features explained
- **QUICK_START.md** - Get started in 3 steps
- **README_INTERACTIVE.md** - Interactive shell reference

Or run:
```bash
venv/bin/python -m tradingagents.screener legend
```

**Happy Trading! 📈**
