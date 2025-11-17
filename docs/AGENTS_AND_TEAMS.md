# TradingAgents: Complete Teams and Agents Reference

## Overview

TradingAgents uses a **5-team, 13-agent** architecture that simulates a professional trading firm. Each team has specialized roles that work together to analyze stocks and make trading decisions.

---

## 🏢 Team Structure

### **Team 1: Analyst Team** (4 Agents)
**Purpose**: Data Collection & Analysis  
**Workflow**: All 4 analysts work in parallel to gather different types of data

#### 1. **Market Analyst** (Technical Analysis)
- **File**: `tradingagents/agents/analysts/market_analyst.py`
- **Function**: `create_market_analyst()`
- **Specialization**: Technical analysis using price charts and indicators
- **Tools Used**:
  - `get_stock_data`: Retrieves historical price data
  - `get_indicators`: Calculates technical indicators
- **Indicators Analyzed**:
  - Moving Averages: 50 SMA, 200 SMA, 10 EMA
  - MACD: MACD line, Signal, Histogram
  - Momentum: RSI
  - Volatility: Bollinger Bands (upper, middle, lower), ATR
  - Volume: VWMA (Volume Weighted Moving Average)
- **Output**: Technical analysis report with trend direction, support/resistance levels, momentum indicators, volatility patterns, and entry/exit signals

#### 2. **Social Media Analyst** (Sentiment Analysis)
- **File**: `tradingagents/agents/analysts/social_media_analyst.py`
- **Function**: `create_social_media_analyst()`
- **Specialization**: Social media sentiment analysis
- **Tools Used**:
  - `get_news`: Retrieves social media/news data
- **Data Sources**: Reddit (via PRAW), social media feeds
- **Output**: Sentiment report showing public opinion, market mood (bullish/bearish), social media buzz, and sentiment scores

#### 3. **News Analyst** (Fundamental Events)
- **File**: `tradingagents/agents/analysts/news_analyst.py`
- **Function**: `create_news_analyst()`
- **Specialization**: News and macroeconomic event analysis
- **Tools Used**:
  - `get_news`: News articles
  - `get_global_news`: Global macroeconomic news
  - `get_insider_sentiment`: Insider trading sentiment
  - `get_insider_transactions`: Insider transaction data
- **Data Sources**: Alpha Vantage News, Google News, financial news feeds
- **Output**: News analysis report highlighting important events (earnings, product launches), macroeconomic indicators, market-moving news, and impact assessment

#### 4. **Fundamentals Analyst** (Company Financials)
- **File**: `tradingagents/agents/analysts/fundamentals_analyst.py`
- **Function**: `create_fundamentals_analyst()`
- **Specialization**: Company financial statement analysis
- **Tools Used**:
  - `get_fundamentals`: Company fundamentals
  - `get_balance_sheet`: Balance sheet data
  - `get_cashflow`: Cash flow statements
  - `get_income_statement`: Income statements
- **Data Sources**: Alpha Vantage, Yahoo Finance
- **Output**: Fundamental analysis report evaluating company financial health, valuation metrics (P/E, P/B), growth prospects, risk factors, and competitive position

---

### **Team 2: Research Team** (3 Agents)
**Purpose**: Bull/Bear Debate & Research Decision  
**Workflow**: Bull and Bear researchers debate, then Research Manager makes final decision

#### 5. **Bull Researcher**
- **File**: `tradingagents/agents/researchers/bull_researcher.py`
- **Function**: `create_bull_researcher()`
- **Specialization**: Advocates FOR buying the stock
- **Memory**: Uses `bull_memory` (FinancialSituationMemory)
- **Focus Areas**:
  - Growth potential and market opportunities
  - Competitive advantages
  - Positive indicators (financial health, industry trends)
  - Countering bearish arguments
- **Output**: Bullish arguments and evidence-based case for investment

#### 6. **Bear Researcher**
- **File**: `tradingagents/agents/researchers/bear_researcher.py`
- **Function**: `create_bear_researcher()`
- **Specialization**: Advocates AGAINST buying the stock
- **Memory**: Uses `bear_memory` (FinancialSituationMemory)
- **Focus Areas**:
  - Risk factors and potential downsides
  - Market challenges and competition
  - Negative indicators
  - Countering bullish arguments
- **Output**: Bearish arguments and risk assessment

#### 7. **Research Manager**
- **File**: `tradingagents/agents/managers/research_manager.py`
- **Function**: `create_research_manager()`
- **Specialization**: Final research decision after debate
- **Memory**: Uses `invest_judge_memory` (FinancialSituationMemory)
- **Role**: Evaluates the Bull vs Bear debate and makes final research decision
- **Output**: Research team's final investment recommendation (Buy/Sell/Hold) with reasoning

---

### **Team 3: Trading Team** (1 Agent)
**Purpose**: Trading Strategy Creation

#### 8. **Trader Agent**
- **File**: `tradingagents/agents/trader/trader.py`
- **Function**: `create_trader()`
- **Specialization**: Creates detailed trading plan
- **Memory**: Uses `trader_memory` (FinancialSituationMemory)
- **Input**: All analyst reports + research team decision
- **Output**: Detailed trading plan including:
  - Entry price recommendations
  - Position sizing
  - Stop-loss levels
  - Take-profit targets
  - Trading strategy rationale

---

### **Team 4: Risk Management Team** (4 Agents)
**Purpose**: Risk Assessment & Portfolio Decision  
**Workflow**: Three risk analysts debate, then Portfolio Manager makes final decision

#### 9. **Aggressive Analyst** (Risky Debator)
- **File**: `tradingagents/agents/risk_mgmt/aggresive_debator.py`
- **Function**: `create_risky_debator()`
- **Specialization**: Argues for higher risk tolerance
- **Focus**: Emphasizes potential returns and growth opportunities
- **Output**: Arguments for taking on more risk

#### 10. **Conservative Analyst** (Safe Debator)
- **File**: `tradingagents/agents/risk_mgmt/conservative_debator.py`
- **Function**: `create_safe_debator()`
- **Specialization**: Argues for lower risk tolerance
- **Focus**: Emphasizes capital preservation and risk mitigation
- **Output**: Arguments for conservative approach

#### 11. **Neutral Analyst**
- **File**: `tradingagents/agents/risk_mgmt/neutral_debator.py`
- **Function**: `create_neutral_debator()`
- **Specialization**: Balanced perspective on risk
- **Focus**: Balanced view considering both risk and return
- **Output**: Balanced risk assessment

#### 12. **Portfolio Manager** (Risk Manager)
- **File**: `tradingagents/agents/managers/risk_manager.py`
- **Function**: `create_risk_manager()`
- **Specialization**: Final approval/rejection decision
- **Memory**: Uses `risk_manager_memory` (FinancialSituationMemory)
- **Role**: Evaluates the risk debate and makes final portfolio decision
- **Output**: Final decision (APPROVE/REJECT) with:
  - Refined trading plan based on risk assessment
  - Risk-adjusted position sizing
  - Final recommendation (Buy/Sell/Hold)

---

## 📊 Complete Agent Summary

| Team | Agent | Specialization | Memory | Key Output |
|------|-------|---------------|--------|------------|
| **Analyst Team** | Market Analyst | Technical Analysis | None | Technical indicators report |
| | Social Analyst | Sentiment Analysis | None | Social sentiment report |
| | News Analyst | News & Events | None | News analysis report |
| | Fundamentals Analyst | Financial Statements | None | Fundamentals report |
| **Research Team** | Bull Researcher | Bullish Arguments | bull_memory | Bullish case |
| | Bear Researcher | Bearish Arguments | bear_memory | Bearish case |
| | Research Manager | Research Decision | invest_judge_memory | Investment plan |
| **Trading Team** | Trader Agent | Trading Strategy | trader_memory | Trading plan |
| **Risk Management** | Aggressive Analyst | High Risk | None | Risk arguments |
| | Conservative Analyst | Low Risk | None | Conservative arguments |
| | Neutral Analyst | Balanced Risk | None | Balanced arguments |
| | Portfolio Manager | Final Decision | risk_manager_memory | Final trade decision |

**Total: 5 Teams, 13 Specialized Agents**

---

## 🔄 Workflow Sequence

```
1. ANALYST TEAM (Parallel)
   ├─ Market Analyst → Technical Report
   ├─ Social Analyst → Sentiment Report
   ├─ News Analyst → News Report
   └─ Fundamentals Analyst → Fundamentals Report
        ↓
2. RESEARCH TEAM (Sequential Debate)
   ├─ Bull Researcher → Bullish Arguments
   ├─ Bear Researcher → Bearish Arguments
   └─ Research Manager → Investment Plan Decision
        ↓
3. TRADING TEAM
   └─ Trader Agent → Detailed Trading Plan
        ↓
4. RISK MANAGEMENT TEAM (Sequential Debate)
   ├─ Aggressive Analyst → High Risk Arguments
   ├─ Conservative Analyst → Low Risk Arguments
   ├─ Neutral Analyst → Balanced Arguments
   └─ Portfolio Manager → Final APPROVE/REJECT Decision
        ↓
5. FINAL OUTPUT
   └─ Trading Decision with Complete Reasoning
```

---

## 🧠 Memory System

Each agent with memory uses **ChromaDB** to store and retrieve:
- **Financial Situation Memory**: Past analyses and recommendations
- **Context Retrieval**: Similar past situations for informed decisions
- **Pattern Recognition**: Historical patterns and outcomes

**Agents with Memory:**
1. Bull Researcher → `bull_memory`
2. Bear Researcher → `bear_memory`
3. Trader Agent → `trader_memory`
4. Research Manager → `invest_judge_memory`
5. Portfolio Manager → `risk_manager_memory`

---

## 🛠️ Configuration

### Selecting Analysts
You can choose which analysts to include:
```python
selected_analysts = ["market", "social", "news", "fundamentals"]
```

### Debate Rounds
Control the depth of debates:
```python
config["max_debate_rounds"] = 1  # Research team debate rounds
config["max_risk_discuss_rounds"] = 1  # Risk team debate rounds
```

---

## 📁 File Structure

```
tradingagents/agents/
├── analysts/
│   ├── market_analyst.py
│   ├── social_media_analyst.py
│   ├── news_analyst.py
│   └── fundamentals_analyst.py
├── researchers/
│   ├── bull_researcher.py
│   └── bear_researcher.py
├── managers/
│   ├── research_manager.py
│   └── risk_manager.py
├── trader/
│   └── trader.py
└── risk_mgmt/
    ├── aggresive_debator.py
    ├── conservative_debator.py
    └── neutral_debator.py
```

---

*Last Updated: 2025-01-16*

