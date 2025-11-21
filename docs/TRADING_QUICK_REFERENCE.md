# Trading Metrics Quick Reference Guide

**For Traders:** Fast reference for understanding screener output

---

## Column Definitions

### Symbol
The stock ticker symbol (e.g., AAPL, MSFT, NVDA)

### Action
Trading recommendation based on technical analysis

| Icon | Action | Meaning |
|------|--------|---------|
| 🟢🟢 | STRONG BUY | Exceptional opportunity - Multiple bullish signals |
| ✅ | BUY DIP | Excellent entry on pullback - Below VWAP |
| 🟢 | BUY | Good entry point - Oversold conditions |
| 🔵 | ACCUMULATION | Build position gradually |
| ⚪ | HOLD/NEUTRAL | No clear direction - Stay in cash |
| 🟡 | WAIT | Price too high - Wait for pullback |
| 🔴 | SELL | Exit position - Overbought |
| 🔴🔴 | STRONG SELL | Exit immediately - Multiple bearish signals |

### Entry
**Recommended buy price** (most conservative entry point)
- This is the floor of your buy zone
- Best price to enter the trade
- Based on support levels and technical indicators

**Example:** Entry $266.63
- Try to buy at or near $266.63
- Acceptable up to the max entry range
- Below this = better deal!

### Target
**Price target for profit-taking**
- Based on resistance levels
- Calculated from technical indicators
- Conservative estimate (most likely achievable)

**Example:** Target $272.01
- Set limit order to sell at $272.01
- Or monitor for manual exit
- Partial exits okay (sell 50% at target, let rest run)

### Stop
**Stop loss price - Your maximum loss point**
- **ALWAYS USE THIS!** Never trade without a stop loss
- Exit immediately if price hits this level
- Protects your capital from large losses

**How it's calculated:**
- Primary: 2% below support level
- Fallback: 5% below entry (when no support exists)

**Example:** Stop $260.00
- Set stop loss order at $260.00
- If price drops to $260.00, exit automatically
- This is your risk management safety net

### Gain%
**Expected profit percentage** from entry to target

| Range | Assessment |
|-------|-----------|
| 20%+ | Excellent opportunity |
| 10-20% | Good opportunity |
| 5-10% | Moderate opportunity |
| 0-5% | Marginal - consider alternatives |
| Negative | Target below entry - unusual situation |

**Example:** Gain% +2.0%
- Expected profit: 2.0% from entry to target
- $1000 position = $20 profit potential
- $10,000 position = $200 profit potential

### R/R (Risk/Reward Ratio)
**Most important metric for professional traders!**

**Formula:** R/R = Potential Gain ÷ Potential Loss

**How to read it:**
- **R/R 3.0** = Risk $1 to make $3 (3:1 ratio)
- **R/R 2.0** = Risk $1 to make $2 (2:1 ratio)
- **R/R 0.5** = Risk $1 to make $0.50 (1:2 ratio - AVOID!)

**Professional Standards:**

| R/R Ratio | Color | Assessment | Action |
|-----------|-------|-----------|---------|
| 3.0+ | 🟢 Bold | Excellent | Professional grade - Take the trade! |
| 2.0-3.0 | 🟢 | Good | Acceptable for most strategies |
| 1.5-2.0 | 🔵 | Fair | Consider carefully |
| 1.0-1.5 | 🟡 | Marginal | High risk, small reward |
| Below 1.0 | 🔴 | Poor | AVOID - Risk exceeds reward |

**Why It Matters:**
- Professional traders require 2:1 minimum
- Accounts for the fact that not all trades win
- If you win 50% of trades with 2:1 R/R, you're profitable
- Key metric for long-term success

**Example:** R/R 0.8
- Risk $6.63 to make $5.38
- Poor ratio - reward doesn't justify risk
- Look for better opportunities with R/R > 2.0

### RSI
**Relative Strength Index** - Momentum indicator

| Range | Color | Meaning |
|-------|-------|---------|
| 0-30 | 🟢 | Oversold - Potential buy signal |
| 30-40 | 🟢 | Getting oversold |
| 40-60 | ⚪ | Neutral - No clear signal |
| 60-70 | 🔴 | Getting overbought |
| 70-100 | 🔴 | Overbought - Potential sell signal |

---

## Reading the Table

### Example Row Breakdown

```
#  Symbol  Action     Entry      Target     Stop       Gain%   R/R   RSI
8  CAT     🟢BUY      $535.21   $560.13   $529.80    +4.7%   4.6   36
```

**Translation:**
- **Stock:** CAT (Caterpillar)
- **Action:** BUY - Good entry opportunity
- **Entry:** Buy at $535.21 (or better)
- **Target:** Sell at $560.13 for profit
- **Stop:** Exit at $529.80 to limit loss
- **Gain:** 4.7% potential profit
- **R/R:** 4.6 - Excellent! Risk $5.41 to make $24.92
- **RSI:** 36 - Slightly oversold, supports buy signal

**Trade Plan:**
1. Enter at $535.21 or better
2. Set stop loss at $529.80 (risk: $5.41 per share)
3. Set target at $560.13 (reward: $24.92 per share)
4. Risk/Reward: 4.6:1 - Professional grade trade!
5. Position size: Risk 1% of account on this trade

---

## Position Sizing Calculator

**Never risk more than 1-2% of your account on a single trade!**

**Formula:**
```
Position Size = (Account Risk %) ÷ (Entry - Stop Loss)
```

**Example with $10,000 account:**
- Account: $10,000
- Risk per trade: 1% = $100
- Entry: $535.21
- Stop: $529.80
- Risk per share: $5.41

**Calculation:**
```
Position Size = $100 ÷ $5.41 = 18 shares
Total Investment: 18 × $535.21 = $9,633.78
Max Loss: 18 × $5.41 = $97.38 (≈1% of account)
Max Gain: 18 × $24.92 = $448.56 (4.6% of account)
```

---

## Trade Workflow

### Step 1: Filter for Quality
1. Look at top 20 results (BUYs are sorted first)
2. Filter for R/R > 2.0 (minimum professional standard)
3. Prefer Gain% > 5% for meaningful profits

### Step 2: Select Best Opportunities
- **Conservative:** R/R > 3.0, RSI < 40
- **Moderate:** R/R > 2.0, Gain% > 5%
- **Aggressive:** R/R > 1.5, any RSI

### Step 3: Calculate Position Size
1. Determine risk per trade (1-2% of account)
2. Calculate risk per share (Entry - Stop)
3. Divide risk amount by risk per share
4. Result = number of shares to buy

### Step 4: Place Orders
1. **Entry Order:** Limit buy at Entry price
2. **Stop Loss:** Stop market at Stop price
3. **Target:** Limit sell at Target price

### Step 5: Monitor
- Let the trade work
- Don't move stop loss down (only up as profit increases)
- Consider taking partial profits at target
- Trail stop loss in profitable trades

---

## Common Patterns

### Pattern 1: High Quality Setup
```
Symbol: CAT
Action: 🟢BUY
Entry: $535.21, Target: $560.13, Stop: $529.80
Gain%: +4.7%, R/R: 4.6, RSI: 36
```
**Why it's good:**
- ✅ BUY signal
- ✅ R/R > 3.0 (professional grade)
- ✅ Gain% > 4%
- ✅ RSI oversold
- **Action:** Strong candidate - Add to watchlist

### Pattern 2: Marginal Setup
```
Symbol: WFC
Action: 🟢BUY
Entry: $83.90, Target: $83.62, Stop: $79.71
Gain%: -0.3%, R/R: -0.1, RSI: 25
```
**Why it's questionable:**
- ✅ BUY signal
- ❌ R/R negative (target below entry!)
- ❌ Negative gain%
- ✅ RSI very oversold
- **Action:** Skip - Poor risk/reward despite buy signal

### Pattern 3: Wait Signal
```
Symbol: MRK
Action: 🟡WAIT
Entry: $92.78, Target: $95.00, Stop: $90.00
Gain%: +2.4%, R/R: 0.9, RSI: 74
```
**Why wait:**
- ❌ WAIT signal
- ❌ R/R < 1.0
- ❌ RSI overbought
- **Action:** Wait for pullback before entering

---

## Risk Management Rules

### The Golden Rules

1. **Never trade without a stop loss**
   - Use the Stop price provided
   - Set it and forget it
   - Don't move it down (only up)

2. **Risk 1-2% per trade maximum**
   - $10,000 account = $100-200 risk per trade
   - Use position sizing calculator
   - Smaller positions = longer survival

3. **Minimum 2:1 R/R ratio**
   - Professional standard
   - Ensures profitability over time
   - Skip trades below 2:1

4. **Diversify across 5-10 positions**
   - Don't put all capital in one stock
   - Spread risk across multiple trades
   - Different sectors preferred

5. **Cut losses quickly, let winners run**
   - Exit immediately at stop loss
   - Don't hope for recovery
   - Trail stops in profitable trades

---

## Frequently Asked Questions

### Q: Why are some Stop Loss values at 5% below entry?
**A:** When a stock has no clear support level (trading below all technical indicators), the system uses a conservative 5% fallback to ensure you always have a stop loss. This is safer than having no stop loss at all.

### Q: What if Target is below Entry price?
**A:** This is unusual and indicates the stock is in a downtrend. The system is warning you that even the resistance level is below your entry point. Consider waiting for better setups.

### Q: Should I always take trades with BUY signals?
**A:** No! Filter by R/R ratio first. A BUY signal with R/R < 1.0 is a poor trade. Focus on BUY signals with R/R > 2.0 for professional-grade opportunities.

### Q: How do I use the Entry price range?
**A:** The table shows Entry (minimum). There's also an Entry Max (not shown in compact table). Try to buy between Entry Min and Entry Max. The lower, the better!

### Q: What if price gaps through my stop loss?
**A:** Use stop-market orders which will execute at the next available price. This is why proper position sizing is critical - you might lose slightly more than planned in a gap situation.

### Q: How long should I hold these trades?
**A:** These are swing trades typically held 1-4 weeks. Exit at target or stop loss, whichever comes first. Don't hold indefinitely hoping for recovery.

### Q: Can I adjust the stop loss?
**A:** YES - but only move it UP (tighter) as the trade becomes profitable. Never move it down (wider) which increases your risk.

### Q: What does the number rank mean?
**A:** Results are ranked by recommendation strength first (BUYs at top), then by priority score. #1 is the highest quality BUY signal.

---

## Daily Workflow Example

**Morning Routine (Before Market Open):**

1. **Run screener:** `python -m tradingagents.screener run`
2. **Review top 20 results** (all BUYs due to sorting)
3. **Filter quality:**
   - Highlight R/R > 2.0
   - Check RSI for confirmation
   - Verify Gain% > 5%

4. **Select 3-5 best opportunities:**
   ```
   Selected:
   - CAT: R/R 4.6, Gain% +4.7% ✅
   - UPS: R/R 1.5, Gain% +4.5% ✅
   - AAPL: R/R 0.8, Gain% +2.0% ❌ (Skip - low R/R)
   ```

5. **Calculate position sizes** (1% risk per trade)
6. **Place orders** before market open

**During Market Hours:**

7. **Monitor fills** - Orders executed?
8. **Set stop losses** immediately after entry
9. **Set target orders** (good-till-cancelled)
10. **Update trade log** with entries

**End of Day:**

11. **Review open positions**
12. **Trail stops** on profitable trades
13. **Check for new opportunities** (evening scan)

---

## Performance Tracking

**Track these metrics:**
- Win rate (% of profitable trades)
- Average R/R of taken trades
- Average gain on winners
- Average loss on losers
- Total P&L
- Best/worst trades

**Goal:** 50% win rate with 2:1 R/R = Profitable!

---

## Support

For questions:
- Review full documentation: `TRADING_METRICS_CALCULATION.md`
- Check examples in this guide
- Understand the metrics before trading real money
- Paper trade first to build confidence

**Remember:** This is a tool to assist your trading decisions. Always do your own analysis and never risk more than you can afford to lose.

---

**Last Updated:** 2025-11-21
