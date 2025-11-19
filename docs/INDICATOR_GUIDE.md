# 📊 TradingAgents Indicator Guide
**Complete Reference for All Technical Indicators**

---

## Table of Contents
1. [Momentum Indicators](#momentum-indicators)
2. [Trend Indicators](#trend-indicators)
3. [Volatility Indicators](#volatility-indicators)
4. [Volume Indicators](#volume-indicators)
5. [Support/Resistance Indicators](#supportresistance-indicators)
6. [Pattern Recognition](#pattern-recognition)
7. [Indicator Combinations](#indicator-combinations)
8. [Interpretation Matrix](#interpretation-matrix)

---

## Momentum Indicators
**Purpose**: Measure the rate of price change to identify overbought/oversold conditions

### 1. RSI (Relative Strength Index)

**What It Measures**: Momentum and overbought/oversold conditions

**Range**: 0 to 100

**Interpretation**:
| Value | Condition | Action | Strength |
|-------|-----------|--------|----------|
| **< 30** | **OVERSOLD** ✅ | **BUY SIGNAL** | Reversal likely |
| 30-40 | Approaching Oversold | Prepare to buy | Building support |
| 40-50 | Neutral-Bearish | Wait | Weak momentum |
| 50-60 | Neutral-Bullish | Hold | Normal |
| 60-70 | Approaching Overbought | Take profits | Building resistance |
| **> 70** | **OVERBOUGHT** ⚠️ | **SELL SIGNAL** | Pullback likely |

**Examples**:
```
RSI = 28: "OVERSOLD - Excellent buying opportunity"
RSI = 45: "Neutral - No strong signal"
RSI = 75: "OVERBOUGHT - Consider taking profits"
```

**What's Good**: RSI < 35 (buy opportunity) or RSI declining from > 70 (reversal starting)
**What's Bad**: RSI > 70 without pullback (extended), RSI < 30 with continued selling (panic)
**What's Neutral**: RSI 40-60 (no extreme)

**Common Patterns**:
- **Bullish**: RSI crosses above 30 from below
- **Bearish**: RSI crosses below 70 from above
- **Divergence**: Price new low but RSI higher low = bullish reversal

---

### 2. RSI Divergence (Phase 2 Enhancement)

**What It Measures**: Disagreement between price movement and RSI momentum

**Types**:
1. **Bullish Divergence** ✅ **STRONG BUY SIGNAL**
   - Price makes lower low
   - RSI makes higher low
   - **Meaning**: Selling pressure weakening, reversal up likely
   - **Strength**: 0.0 to 0.95 (higher = stronger signal)

2. **Bearish Divergence** ⚠️ **STRONG SELL SIGNAL**
   - Price makes higher high
   - RSI makes lower high
   - **Meaning**: Buying pressure weakening, reversal down likely
   - **Strength**: 0.0 to 0.95 (higher = stronger signal)

**Interpretation**:
| Strength | Reliability | Action |
|----------|-------------|--------|
| **0.7-0.95** | **Very High** | **ACT NOW** |
| 0.5-0.7 | High | Strong signal |
| 0.3-0.5 | Medium | Watch closely |
| < 0.3 | Low | Weak signal |

**Example**:
```
Bullish Divergence Detected:
- Strength: 0.82 (Very High)
- Price: $95 → $90 (lower low)
- RSI: 28 → 32 (higher low)
→ ACTION: BUY - Strong reversal signal
```

**What's Good**: Bullish divergence with strength > 0.6 at oversold levels
**What's Bad**: Bearish divergence with strength > 0.6 at overbought levels
**What's Neutral**: No divergence or strength < 0.3

---

### 3. MACD (Moving Average Convergence Divergence)

**What It Measures**: Trend direction and momentum

**Components**:
- **MACD Line**: 12-day EMA - 26-day EMA
- **Signal Line**: 9-day EMA of MACD
- **Histogram**: MACD - Signal

**Interpretation**:
| Signal | Meaning | Action |
|--------|---------|--------|
| **MACD crosses above Signal** | **Bullish Crossover** ✅ | **BUY** |
| **MACD crosses below Signal** | **Bearish Crossover** ⚠️ | **SELL** |
| Histogram expanding (positive) | Strengthening uptrend | Hold/Add |
| Histogram contracting (positive) | Weakening uptrend | Prepare to sell |
| Histogram expanding (negative) | Strengthening downtrend | Avoid |
| Histogram contracting (negative) | Weakening downtrend | Prepare to buy |

**Examples**:
```
MACD Bullish Crossover:
- MACD: 2.5 (rising)
- Signal: 1.8 (slower rise)
- Histogram: +0.7 (expanding)
→ ACTION: BUY - Momentum building
```

**What's Good**: Bullish crossover with expanding positive histogram
**What's Bad**: Bearish crossover with expanding negative histogram
**What's Neutral**: MACD and Signal line flat/converging

---

## Trend Indicators
**Purpose**: Identify the direction and strength of price trends

### 4. Moving Averages (SMA)

**What They Measure**: Average price over time, smoothing out volatility

**Types**:
- **MA 20**: Short-term trend (20 days)
- **MA 50**: Medium-term trend (50 days)
- **MA 200**: Long-term trend (200 days)

**Interpretation**:
| Condition | Meaning | Action |
|-----------|---------|--------|
| **Price > MA 20 > MA 50 > MA 200** | **Strong Uptrend** ✅ | **BUY/HOLD** |
| Price > MA 20 > MA 50 | Uptrend | Buy |
| Price > MA 20 | Short-term bullish | Consider buy |
| MA 20 > MA 50 (Golden Cross) | Bullish trend change | BUY SIGNAL |
| **Price < MA 20 < MA 50 < MA 200** | **Strong Downtrend** ⚠️ | **AVOID** |
| Price < MA 20 < MA 50 | Downtrend | Sell |
| Price < MA 20 | Short-term bearish | Avoid |
| MA 20 < MA 50 (Death Cross) | Bearish trend change | SELL SIGNAL |

**Examples**:
```
Strong Bull Market:
- Price: $150
- MA 20: $145
- MA 50: $138
- MA 200: $125
→ All MAs aligned upward - Strong buy

Weak Market:
- Price: $100
- MA 20: $102 (below)
- MA 50: $105 (below)
→ Price under MAs - Avoid
```

**What's Good**: Price > all MAs, MAs sloping up
**What's Bad**: Price < all MAs, MAs sloping down
**What's Neutral**: Price oscillating around MAs

---

### 5. VWAP (Volume Weighted Average Price) ⭐ **INSTITUTIONAL BENCHMARK**

**What It Measures**: Average price weighted by volume - where big money is buying/selling

**Interpretation**:
| Condition | Meaning | Action | Institutional Behavior |
|-----------|---------|--------|----------------------|
| **Price < VWAP - 0.5%** | **Below institutional level** ✅ | **BUY NOW** | Institutions accumulating |
| Price ≈ VWAP (±0.5%) | At institutional benchmark | ACCUMULATE | Fair value |
| Price > VWAP + 0.5% to 2% | Slightly extended | CAUTIOUS BUY | Retail pushing up |
| **Price > VWAP + 2%** | **Above institutional level** ⚠️ | **WAIT FOR PULLBACK** | Overbought vs benchmark |

**Distance from VWAP**:
| Distance | Interpretation |
|----------|----------------|
| -5% to -2% | Significant discount - Excellent buy |
| -2% to -0.5% | Discount - Good buy |
| -0.5% to +0.5% | Fair value - Neutral |
| +0.5% to +2% | Premium - Cautious |
| +2% to +5% | Significant premium - Wait |
| > +5% | Extremely extended - Avoid |

**Examples**:
```
Below VWAP (Bullish):
- Price: $98.50
- VWAP: $100.20
- Distance: -1.7%
→ ACTION: BUY NOW - Institutional accumulation zone

Above VWAP (Bearish):
- Price: $105.00
- VWAP: $100.00
- Distance: +5.0%
→ ACTION: WAIT - Price too extended, wait for retest of VWAP
```

**What's Good**: Price 1-2% below VWAP (discount to institutions)
**What's Bad**: Price > 3% above VWAP (extended vs benchmark)
**What's Neutral**: Price within ±0.5% of VWAP

---

## Volatility Indicators
**Purpose**: Measure price volatility and identify squeeze/expansion periods

### 6. Bollinger Bands

**What They Measure**: Price volatility and overbought/oversold relative to volatility

**Components**:
- **Upper Band**: MA 20 + (2 × Standard Deviation)
- **Middle Band**: MA 20 (baseline)
- **Lower Band**: MA 20 - (2 × Standard Deviation)

**Interpretation**:
| Condition | Meaning | Action |
|-----------|---------|--------|
| **Price touches Lower Band** | **Oversold** ✅ | **BUY** |
| Price near Lower Band (< 2%) | Approaching support | Prepare to buy |
| Price at Middle Band | Neutral | No signal |
| Price near Upper Band (< 2%) | Approaching resistance | Prepare to sell |
| **Price touches Upper Band** | **Overbought** ⚠️ | **SELL** |
| Bands contracting (squeeze) | Low volatility | **BREAKOUT IMMINENT** |
| Bands expanding | High volatility | Trend in motion |

**Examples**:
```
Bollinger Band Bounce:
- Price: $95.20
- BB Lower: $95.00
- BB Middle: $100.00
- BB Upper: $105.00
→ Price at lower band - BUY SIGNAL

Bollinger Band Squeeze:
- BB Width: 0.08 (8% of middle band)
- BB Width Percentile: 5% (narrowest in 20 days)
→ Squeeze detected - Breakout coming soon
```

**What's Good**: Price at lower band in uptrend (buy dip)
**What's Bad**: Price at upper band in downtrend (sell rally)
**What's Neutral**: Price at middle band

---

### 7. Bollinger Band Squeeze (Phase 2 Enhancement)

**What It Measures**: Volatility compression that precedes large price moves

**Metrics**:
- **BB Width**: (Upper - Lower) / Middle
- **BB Width Percentile**: Current width vs 20-day range

**Interpretation**:
| Width Percentile | Condition | Meaning | Action |
|------------------|-----------|---------|--------|
| **< 15%** | **SQUEEZE DETECTED** 🎯 | **Breakout imminent** | **PREPARE TO TRADE** |
| 15-30% | Low volatility | Consolidation | Watch closely |
| 30-70% | Normal volatility | Typical trading | Normal |
| 70-85% | High volatility | Trend in motion | Trade with trend |
| **> 85%** | **Extreme volatility** | Large moves happening | Reduce position |

**Squeeze Strength**:
| Strength | Meaning | Expected Move |
|----------|---------|---------------|
| **0.8-1.0** | **Extreme squeeze** | **Large breakout expected** |
| 0.6-0.8 | Strong squeeze | Significant move likely |
| 0.4-0.6 | Moderate squeeze | Normal breakout |
| < 0.4 | Weak squeeze | Small move |

**Examples**:
```
Strong Squeeze:
- BB Width: 0.05 (5% of price)
- Width Percentile: 8% (bottom 8% of 20 days)
- Squeeze Strength: 0.87 (very strong)
→ ACTION: PREPARE - Major breakout imminent (direction unknown)
→ WAIT for: Price to break above/below middle band for direction
```

**What's Good**: Squeeze detected with uptrend context (breakout up likely)
**What's Bad**: Squeeze detected in downtrend (breakout down likely)
**What's Neutral**: Width percentile 30-70% (normal volatility)

---

### 8. ATR (Average True Range)

**What It Measures**: Average trading range (volatility) over 14 days

**Absolute Value**: Dollar amount (e.g., $5.20 means average daily range is $5.20)

**ATR Percentage**: (ATR / Current Price) × 100

**Interpretation**:
| ATR % | Volatility Level | Meaning | Position Sizing |
|-------|------------------|---------|-----------------|
| **< 1.0%** | **Very Low** | Stable stock | Larger position |
| 1.0-2.0% | Low | Blue chip | Standard position |
| 2.0-3.0% | Normal | Typical stock | Standard position |
| 3.0-5.0% | High | Growth stock | Smaller position |
| **> 5.0%** | **Very High** | Volatile/speculative | **Much smaller position** |

**Entry Range Adjustment**:
| ATR % | Range Multiplier | Example Entry Range |
|-------|------------------|---------------------|
| < 1.0% | 0.6× (tight) | ±0.6% from target |
| 1.0-3.0% | 1.0× (standard) | ±1.0% from target |
| > 3.0% | 1.5× (wide) | ±1.5% from target |

**Examples**:
```
Low Volatility Stock:
- Price: $100
- ATR: $0.80
- ATR %: 0.8%
→ Low volatility - Can use tight stop loss (2× ATR = $1.60)

High Volatility Stock:
- Price: $50
- ATR: $3.00
- ATR %: 6.0%
→ High volatility - Need wide stop loss (2× ATR = $6.00)
```

**What's Good**: ATR < 2% for conservative investors
**What's Bad**: ATR > 5% for conservative investors (too risky)
**What's Neutral**: ATR 2-3% (typical stocks)

---

## Support/Resistance Indicators
**Purpose**: Identify price levels where buying/selling pressure concentrates

### 9. Pivot Points ⭐ **FLOOR TRADER LEVELS**

**What They Measure**: Mathematical support/resistance levels from previous day's data

**Levels**:
- **R3, R2, R1**: Resistance levels (selling pressure)
- **PP**: Pivot Point (central level)
- **S1, S2, S3**: Support levels (buying pressure)

**Calculation**:
```
PP = (Previous High + Previous Low + Previous Close) / 3
R1 = (2 × PP) - Previous Low
S1 = (2 × PP) - Previous High
R2 = PP + (Previous High - Previous Low)
S2 = PP - (Previous High - Previous Low)
```

**Interpretation**:
| Price Position | Zone | Meaning | Action |
|----------------|------|---------|--------|
| **Below S2** | **Oversold Zone** ✅ | **Strong support broken** | **BUY - Bounce likely** |
| S2 to S1 | Support Zone | Accumulation area | BUY |
| **S1 to PP** | **Accumulation Zone** ✅ | **Good buy zone** | **BUY/ACCUMULATE** |
| PP to R1 | Neutral Zone | Fair value | HOLD |
| R1 to R2 | Resistance Zone | Distribution area | SELL |
| **Above R2** | **Overbought Zone** ⚠️ | **Strong resistance broken** | **SELL - Pullback likely** |

**Trading Strategy**:
1. **Buy**: When price bounces off S1 or S2
2. **Sell**: When price fails at R1 or R2
3. **Breakout Buy**: Price breaks above R1 with volume
4. **Breakdown Sell**: Price breaks below S1 with volume

**Examples**:
```
Bullish Setup:
- Price: $98.50
- Pivot S1: $98.00
- Pivot PP: $100.00
- Pivot R1: $102.00
→ Price in accumulation zone (S1 to PP) - BUY SIGNAL

Bearish Setup:
- Price: $103.50
- Pivot R1: $102.00
- Pivot R2: $105.00
→ Price above R1, approaching R2 - TAKE PROFITS
```

**What's Good**: Price at S1 or S2 (support bounce opportunity)
**What's Bad**: Price at R1 or R2 (resistance rejection likely)
**What's Neutral**: Price at PP (fair value)

---

### 10. Fibonacci Retracement Levels (Phase 2 Enhancement)

**What They Measure**: Natural retracement levels based on Fibonacci sequence

**Levels** (from swing high to swing low):
- **23.6%**: Minor retracement (strong trend)
- **38.2%**: Moderate retracement (healthy pullback)
- **50.0%**: Midpoint (key psychological level)
- **61.8%**: Golden ratio (strong support/resistance)
- **78.6%**: Deep retracement (trend reversal possible)

**Interpretation**:
| Fib Level | Meaning | Trading Strategy |
|-----------|---------|------------------|
| **23.6%** | Minor pullback | Weak support - ignore in downtrend |
| **38.2%** | Healthy retracement | Good buy in uptrend |
| **50.0%** | Midpoint | Psychological level - key support |
| **61.8%** | Golden ratio | **STRONGEST SUPPORT/RESISTANCE** |
| **78.6%** | Deep retracement | Last support before trend reversal |

**Usage in Uptrend**:
```
Recent Swing: $80 (low) to $120 (high)
Fib Levels:
- 23.6%: $110.56 (minor support)
- 38.2%: $104.72 (good buy level)
- 50.0%: $100.00 (key support)
- 61.8%: $95.28 (strong support)
- 78.6%: $89.44 (last support before trend break)

Strategy:
1. Wait for pullback to 38.2% ($104.72) - FIRST BUY
2. If breaks, wait for 50% ($100) - SECOND BUY
3. If breaks, wait for 61.8% ($95.28) - FINAL BUY
4. Below 61.8% = trend broken, EXIT
```

**Current Fib Level Signal**:
| At Level | Meaning | Action |
|----------|---------|--------|
| **Near 61.8%** | **At golden ratio** ✅ | **STRONG BUY (if uptrend)** |
| Near 50.0% | At midpoint | BUY (if uptrend) |
| Near 38.2% | Shallow pullback | Early buy (aggressive) |
| Near 23.6% | Very shallow | Too early (wait deeper) |
| Near 78.6% | Deep retracement | Last chance buy (risky) |

**Examples**:
```
Strong Support:
- Current Price: $95.50
- Fib 61.8%: $95.28
- Tolerance: ±2%
→ Price near golden ratio - STRONG BUY SIGNAL

Failed Retracement:
- Current Price: $88.00
- Fib 78.6%: $89.44 (broke below)
→ Deep retracement failed - TREND BROKEN, AVOID
```

**What's Good**: Price bouncing off 50% or 61.8% in uptrend
**What's Bad**: Price breaking below 78.6% (trend reversal)
**What's Neutral**: Price between Fib levels (no clear signal)

---

## Volume Indicators
**Purpose**: Confirm price moves with volume strength

### 11. Volume Ratio

**What It Measures**: Current volume vs 20-day average volume

**Formula**: Current Volume / 20-day Average Volume

**Interpretation**:
| Ratio | Meaning | Significance |
|-------|---------|--------------|
| **< 0.5** | **Very low volume** | Weak move, low conviction |
| 0.5-0.8 | Below average | Normal quiet day |
| 0.8-1.2 | Average volume | Normal |
| 1.2-1.5 | Above average | Increased interest |
| **1.5-2.0** | **High volume** ✅ | **Strong conviction** |
| **> 2.0** | **Volume spike** 🎯 | **Major event, institutional activity** |

**With Price Movement**:
| Condition | Meaning | Action |
|-----------|---------|--------|
| **Price UP + Volume Spike (> 1.5)** | **Strong buying** ✅ | **BUY - Confirmed uptrend** |
| Price UP + Low Volume (< 0.8) | Weak rally | Avoid - lack of conviction |
| **Price DOWN + Volume Spike (> 1.5)** | **Strong selling** ⚠️ | **SELL - Confirmed downtrend** |
| Price DOWN + Low Volume (< 0.8) | Weak selloff | Potential bounce |
| Price FLAT + Volume Spike | Accumulation/Distribution | Watch for breakout |

**Examples**:
```
Bullish Confirmation:
- Price: +3.5%
- Volume Ratio: 2.3 (230% of average)
→ Strong buying with volume - CONFIRMED BUY SIGNAL

Weak Rally (Bearish):
- Price: +2.0%
- Volume Ratio: 0.4 (40% of average)
→ Price up but no volume - FAKE RALLY, AVOID
```

**What's Good**: Volume ratio > 1.5 confirming price direction
**What's Bad**: Volume ratio < 0.6 on important moves (not confirmed)
**What's Neutral**: Volume ratio 0.8-1.2 (normal trading)

---

## Pattern Recognition
**Combining multiple indicators to identify high-probability setups**

### Pattern 1: STRONG BUY (Highest Probability)

**Required Conditions** (ALL must be true):
1. ✅ RSI < 35 (oversold)
2. ✅ Price < VWAP - 1% (below institutional benchmark)
3. ✅ Price near Pivot S1 or S2 (support level)
4. ✅ MACD bullish crossover (momentum turning)
5. ✅ Volume ratio > 1.3 (strong buying interest)
6. ✅ Price > MA 50 (still in uptrend)

**Optional Enhancers**:
- Bullish RSI divergence (strength > 0.6)
- Price near Fib 61.8% or 50%
- BB Squeeze detected (breakout setup)

**Example**:
```
STRONG BUY Setup:
- Symbol: AAPL
- Price: $175.50
- RSI: 32 (oversold ✅)
- VWAP: $178.20 (price -1.5% below ✅)
- Pivot S1: $175.00 (price near ✅)
- MACD: Bullish crossover yesterday ✅
- Volume Ratio: 1.8 ✅
- MA 50: $170.00 (price above ✅)
→ PROBABILITY: 85% - STRONG BUY SIGNAL
```

---

### Pattern 2: BUY (Good Probability)

**Required Conditions** (3+ must be true):
1. RSI 30-40 (approaching oversold)
2. Price < VWAP (below benchmark)
3. Price in pivot accumulation zone (S1 to PP)
4. Price near MA 20 or MA 50 (trend support)
5. Volume ratio > 1.0 (healthy volume)

**Example**:
```
BUY Setup:
- RSI: 38 ✅
- VWAP Distance: -0.8% ✅
- Pivot Zone: S1 to PP ✅
- Near MA 20: Yes ✅
→ PROBABILITY: 65% - BUY SIGNAL
```

---

### Pattern 3: WAIT FOR PULLBACK

**Conditions**:
1. RSI > 65 (approaching overbought)
2. Price > VWAP + 2% (above institutional benchmark)
3. Price above Pivot R1 (resistance)
4. No MACD divergence warning
5. BB Squeeze NOT detected

**Example**:
```
WAIT Setup:
- RSI: 68 (elevated)
- VWAP Distance: +3.2% (extended)
- Pivot: Above R1
→ ACTION: WAIT for pullback to VWAP or pivot PP
```

---

### Pattern 4: STRONG SELL (Highest Risk)

**Required Conditions** (ALL must be true):
1. ⚠️ RSI > 75 (overbought)
2. ⚠️ Price > VWAP + 3% (way above institutional benchmark)
3. ⚠️ Bearish MACD crossover (momentum turning down)
4. ⚠️ Price at/above Pivot R2 (strong resistance)
5. ⚠️ Volume spike on down day (distribution)

**Optional Enhancers**:
- Bearish RSI divergence (strength > 0.6)
- Price rejected at Fib 23.6% in downtrend
- BB Squeeze breakout to downside

**Example**:
```
STRONG SELL Setup:
- RSI: 78 ⚠️
- VWAP Distance: +4.5% ⚠️
- MACD: Bearish crossover ⚠️
- Pivot: Above R2 ⚠️
- Volume: 2.1× on -2% day ⚠️
→ PROBABILITY: 80% - STRONG SELL/AVOID
```

---

### Pattern 5: BREAKOUT IMMINENT (BB Squeeze)

**Required Conditions**:
1. BB Squeeze detected (width percentile < 15%)
2. Squeeze strength > 0.6 (strong compression)
3. Price near pivot PP or MA 20 (consolidation)
4. Volume ratio declining (< 0.8) - quiet before storm

**Trading Strategy**:
1. **WAIT** for direction signal
2. **BUY** if price breaks above BB middle + volume spike
3. **SELL/AVOID** if price breaks below BB middle + volume spike

**Example**:
```
Breakout Setup:
- BB Squeeze: YES (width percentile: 8%)
- Squeeze Strength: 0.82
- Price: At pivot PP (consolidating)
- Volume: 0.6× (quiet)
→ ACTION: PREPARE - Breakout imminent, wait for direction
→ BUY TRIGGER: Price > BB middle + volume > 1.5×
→ SELL TRIGGER: Price < BB middle + volume > 1.5×
```

---

### Pattern 6: BULLISH DIVERGENCE REVERSAL

**Required Conditions**:
1. Bullish RSI divergence (strength > 0.6)
2. Price near Pivot S1 or Fib 61.8% (support)
3. MACD histogram contracting (selling weakening)
4. Volume declining on down days (exhaustion)

**Example**:
```
Reversal Setup:
- RSI Divergence: BULLISH, strength 0.78
- Price: At Fib 61.8% ($95.28)
- MACD Histogram: Contracting
- Volume: Declining on selloff
→ PROBABILITY: 75% - REVERSAL UP LIKELY - BUY
```

---

## Indicator Combinations
**How indicators work together to increase probability**

### Combination 1: Momentum + Trend
**Best Use**: Confirming entry in established trends

| RSI | Trend (MA) | Combined Signal | Probability |
|-----|------------|-----------------|-------------|
| < 30 | Price > MA 50 | BUY the dip | 80% |
| < 30 | Price < MA 50 | Falling knife | 40% |
| > 70 | Price > MA 50 | Take profits | 70% |
| > 70 | Price < MA 50 | Dead cat bounce | 30% |

---

### Combination 2: VWAP + Pivot Points
**Best Use**: Institutional-aligned entries

| VWAP Position | Pivot Zone | Combined Signal | Probability |
|---------------|------------|-----------------|-------------|
| < VWAP -1% | S1 to PP | **STRONG BUY** | **85%** |
| < VWAP | S1 to PP | BUY | 70% |
| > VWAP +2% | R1 to R2 | SELL | 70% |
| > VWAP +3% | Above R2 | **STRONG SELL** | **80%** |

---

### Combination 3: Volume + Price Action
**Best Use**: Confirming breakouts

| Price Move | Volume Ratio | BB Squeeze | Combined Signal | Probability |
|------------|--------------|------------|-----------------|-------------|
| UP +2% | > 1.5× | YES | **BREAKOUT BUY** | **90%** |
| UP +2% | < 0.8× | NO | Weak rally | 30% |
| DOWN -2% | > 1.5× | NO | **BREAKDOWN SELL** | **85%** |
| DOWN -2% | < 0.8× | NO | Weak selloff | 35% |

---

### Combination 4: RSI Divergence + Fibonacci
**Best Use**: Reversal trading

| Divergence | Fib Level | Support/Resistance | Combined Signal | Probability |
|------------|-----------|-------------------|-----------------|-------------|
| Bullish (> 0.7) | At 61.8% | At Pivot S1 | **REVERSAL UP** | **90%** |
| Bullish (> 0.5) | At 50% | Near VWAP | Reversal up | 75% |
| Bearish (> 0.7) | At 23.6% | At Pivot R1 | **REVERSAL DOWN** | **85%** |
| Bearish (> 0.5) | At 38.2% | Above VWAP | Reversal down | 70% |

---

## Interpretation Matrix
**Quick reference for all indicators at a glance**

### Bullish Signals (BUY)
| Indicator | Bullish Condition | Strength |
|-----------|-------------------|----------|
| RSI | < 30 | ⭐⭐⭐⭐⭐ |
| RSI Divergence | Bullish, strength > 0.7 | ⭐⭐⭐⭐⭐ |
| MACD | Bullish crossover | ⭐⭐⭐⭐ |
| MA | Price > MA 20 > MA 50 > MA 200 | ⭐⭐⭐⭐⭐ |
| VWAP | Price < VWAP -1% | ⭐⭐⭐⭐⭐ |
| BB | Price at lower band | ⭐⭐⭐⭐ |
| BB Squeeze | Detected + upward break | ⭐⭐⭐⭐⭐ |
| Pivot | Price at S1 or S2 | ⭐⭐⭐⭐ |
| Fibonacci | Price at 61.8% or 50% | ⭐⭐⭐⭐ |
| Volume | Spike (> 1.5×) on up day | ⭐⭐⭐⭐ |
| ATR | Low (< 2%) | ⭐⭐⭐ (safer) |

### Bearish Signals (SELL/AVOID)
| Indicator | Bearish Condition | Strength |
|-----------|-------------------|----------|
| RSI | > 75 | ⭐⭐⭐⭐⭐ |
| RSI Divergence | Bearish, strength > 0.7 | ⭐⭐⭐⭐⭐ |
| MACD | Bearish crossover | ⭐⭐⭐⭐ |
| MA | Price < MA 20 < MA 50 < MA 200 | ⭐⭐⭐⭐⭐ |
| VWAP | Price > VWAP +3% | ⭐⭐⭐⭐⭐ |
| BB | Price at upper band | ⭐⭐⭐⭐ |
| BB Squeeze | Detected + downward break | ⭐⭐⭐⭐⭐ |
| Pivot | Price at R1 or R2 | ⭐⭐⭐⭐ |
| Fibonacci | Price rejected at 23.6% in downtrend | ⭐⭐⭐ |
| Volume | Spike (> 1.5×) on down day | ⭐⭐⭐⭐ |
| ATR | Very high (> 5%) | ⭐⭐⭐ (risky) |

---

## Using This Guide

### For Quick Analysis:
1. Check RSI (< 30 = buy, > 70 = sell)
2. Check VWAP (below = buy, above = sell)
3. Check Pivot zone (S1-PP = buy, R1-R2 = sell)
4. Confirm with volume (> 1.5× = strong signal)

### For Deep Analysis:
1. **Trend**: Check all MAs, VWAP, pivot position
2. **Momentum**: Check RSI, MACD, RSI divergence
3. **Volatility**: Check BB, ATR, BB squeeze
4. **Support/Resistance**: Check pivots, Fibonacci, BB bands
5. **Volume**: Check volume ratio for confirmation
6. **Pattern**: Match to one of the 6 patterns above

### Signal Strength Scoring:
```
Score each indicator:
- Bullish indicator = +1
- Neutral = 0
- Bearish indicator = -1

Total Score:
+7 to +10: STRONG BUY ✅
+4 to +6: BUY
+1 to +3: WEAK BUY
0: NEUTRAL
-1 to -3: WEAK SELL
-4 to -6: SELL
-7 to -10: STRONG SELL ⚠️
```

---

## Next Steps

**See Also**:
- `./quick_run.sh indicators` - Show all current indicator values
- `./quick_run.sh indexes` - Track market indexes
- `docs/PATTERN_RECOGNITION.md` - Advanced pattern guide
- `docs/PHASE2_ENHANCEMENTS.md` - Phase 2 features

---

**📚 This guide is comprehensive but remember**: No single indicator is perfect. Always use multiple indicators to confirm signals and manage risk with proper stop losses and position sizing.
