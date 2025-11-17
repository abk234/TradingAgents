"""
Custom LangChain Tools for TradingAgents Bot

These tools give the conversational agent access to all TradingAgents functionality.
"""

from langchain_core.tools import tool
from typing import Optional, List, Dict, Any
from datetime import date
import logging

from tradingagents.screener import DailyScreener
from tradingagents.screener.sector_analyzer import SectorAnalyzer
from tradingagents.analyze import DeepAnalyzer
from tradingagents.database import (
    get_db_connection,
    TickerOperations,
    ScanOperations,
    PortfolioOperations
)
from tradingagents.utils import (
    show_screener_legend,
    show_sector_recommendations,
    format_score_with_context
)
from tradingagents.fast_config import FAST_CONFIG
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.validation import validate_data_quality

logger = logging.getLogger(__name__)

# Initialize shared resources
_db_connection = None
_ticker_ops = None
_scan_ops = None
_portfolio_ops = None


def get_db():
    """Get or create database connection."""
    global _db_connection, _ticker_ops, _scan_ops, _portfolio_ops

    if _db_connection is None:
        _db_connection = get_db_connection()
        _ticker_ops = TickerOperations(_db_connection)
        _scan_ops = ScanOperations(_db_connection)
        _portfolio_ops = PortfolioOperations(_db_connection)

    return _db_connection, _ticker_ops, _scan_ops, _portfolio_ops


# =============================================================================
# SCREENING & DISCOVERY TOOLS
# =============================================================================

@tool
def run_screener(sector_analysis: bool = True, top_n: int = 10) -> str:
    """
    Run the daily stock screener to find investment opportunities.

    Args:
        sector_analysis: Whether to include sector-level analysis (default: True)
        top_n: Number of top stocks to return (default: 10)

    Returns:
        Screening results with top opportunities and sector analysis

    Use this when the user asks about:
    - "What stocks should I look at?"
    - "Run a scan"
    - "Find opportunities"
    - "What's hot in the market?"
    """
    try:
        screener = DailyScreener()

        # Run scan (no price update to be faster)
        results = screener.scan_all(
            update_prices=False,
            store_results=True
        )

        if not results:
            return "No screening results available. The database may need to be updated."

        # Format response
        response = [f"📊 Daily Screener Results - {len(results)} stocks analyzed\n"]

        # Sector analysis if requested
        if sector_analysis:
            db, _, _, _ = get_db()
            sector_analyzer = SectorAnalyzer(db)
            sector_results = sector_analyzer.analyze_all_sectors()

            if sector_results:
                response.append("🎯 Top Sectors by Strength:")
                for i, sector in enumerate(sector_results[:5], 1):
                    response.append(
                        f"{i}. {sector['sector']}: {sector['strength_score']:.1f}% "
                        f"({sector['buy_signals']}/{sector['total_stocks']} signals, "
                        f"momentum: {sector['momentum']})"
                    )
                response.append("")

        # Top stocks
        response.append(f"🌟 Top {top_n} Opportunities:")
        for i, stock in enumerate(results[:top_n], 1):
            response.append(
                f"{i}. {stock['symbol']} - {stock.get('name', 'N/A')}\n"
                f"   Sector: {stock.get('sector', 'Unknown')}\n"
                f"   Score: {stock['priority_score']}/100 | "
                f"Price: ${stock.get('current_price', 0):.2f} | "
                f"Change: {stock.get('change_pct', 0):+.2f}%"
            )

            if stock.get('triggered_alerts'):
                response.append(f"   Alerts: {', '.join(stock['triggered_alerts'])}")

        return "\n".join(response)

    except Exception as e:
        logger.error(f"Error running screener: {e}")
        return f"Error running screener: {str(e)}"


@tool
def get_top_stocks(limit: int = 10, min_score: Optional[int] = None) -> str:
    """
    Get top stock opportunities from the latest scan.

    Args:
        limit: Number of stocks to return (default: 10)
        min_score: Minimum priority score filter (optional)

    Returns:
        List of top stocks with scores and key metrics

    Use this when the user asks about:
    - "Show me the best stocks"
    - "What are the top picks?"
    - "Give me your top 5"
    """
    try:
        screener = DailyScreener()
        opportunities = screener.get_top_opportunities(limit=limit)

        if not opportunities:
            return "No opportunities found in the database. Try running the screener first."

        # Filter by min_score if specified
        if min_score:
            opportunities = [o for o in opportunities if o.get('priority_score', 0) >= min_score]

        response = [f"🎯 Top {len(opportunities)} Stock Opportunities:\n"]

        for i, stock in enumerate(opportunities, 1):
            score = stock.get('priority_score', 0)
            score_interpretation = "🔥 Strong" if score >= 50 else "✅ Good" if score >= 40 else "⚠️ Fair" if score >= 30 else "❌ Weak"

            response.append(
                f"{i}. **{stock['symbol']}** - {stock.get('company_name', 'N/A')}\n"
                f"   Score: {score}/100 {score_interpretation}\n"
                f"   Sector: {stock.get('sector', 'Unknown')}\n"
                f"   Price: ${stock.get('price', 0):.2f}"
            )

            if stock.get('triggered_alerts'):
                response.append(f"   🚨 Alerts: {', '.join(stock['triggered_alerts'])}")

            response.append("")

        return "\n".join(response)

    except Exception as e:
        logger.error(f"Error getting top stocks: {e}")
        return f"Error retrieving top stocks: {str(e)}"


@tool
def analyze_sector(sector_name: str) -> str:
    """
    Analyze a specific sector's strength and opportunities.

    Args:
        sector_name: Sector to analyze (e.g., "Technology", "Healthcare", "Energy")

    Returns:
        Detailed sector analysis with strength metrics and top stocks

    Use this when the user asks about:
    - "How is the tech sector doing?"
    - "Show me healthcare stocks"
    - "What's happening in energy?"
    """
    try:
        db, _, _, _ = get_db()
        sector_analyzer = SectorAnalyzer(db)

        # Get all sectors and find the requested one
        all_sectors = sector_analyzer.analyze_all_sectors()

        # Find matching sector (case-insensitive)
        sector_data = None
        for s in all_sectors:
            if sector_name.lower() in s['sector'].lower():
                sector_data = s
                break

        if not sector_data:
            available = [s['sector'] for s in all_sectors]
            return f"Sector '{sector_name}' not found. Available sectors: {', '.join(available)}"

        # Format response
        strength = sector_data['strength_score']
        strength_label = "💪 Strong" if strength > 40 else "➖ Neutral" if strength > 20 else "📉 Weak"

        response = [
            f"📊 {sector_data['sector']} Sector Analysis\n",
            f"Strength Score: {strength:.1f}/100 {strength_label}",
            f"Stocks Analyzed: {sector_data['total_stocks']}",
            f"Buy Signals: {sector_data['buy_signals']}",
            f"Average Priority: {sector_data.get('avg_priority', 0):.1f}/100",
            f"Momentum: {sector_data['momentum']}",
            "\n"
        ]

        # Get top stocks from this sector
        stocks = sector_analyzer.get_stocks_from_top_sectors(top_n_sectors=1, stocks_per_sector=5)
        if stocks:
            response.append("🌟 Top Stocks in This Sector:")
            for symbol, score in stocks[:5]:
                response.append(f"  • {symbol}: Score {score}/100")

        # Recommendation
        if strength > 40:
            response.append("\n✅ Recommendation: Strong sector - Good opportunities")
        elif strength > 20:
            response.append("\n⚠️ Recommendation: Neutral sector - Moderate opportunities")
        else:
            response.append("\n❌ Recommendation: Weak sector - Consider waiting or other sectors")

        return "\n".join(response)

    except Exception as e:
        logger.error(f"Error analyzing sector: {e}")
        return f"Error analyzing sector: {str(e)}"


@tool
def search_stocks(
    sector: Optional[str] = None,
    min_score: Optional[int] = None,
    with_signals: bool = False
) -> str:
    """
    Search for stocks matching specific criteria.

    Args:
        sector: Filter by sector (optional)
        min_score: Minimum priority score (optional)
        with_signals: Only show stocks with buy signals (default: False)

    Returns:
        List of stocks matching the criteria

    Use this when the user asks about:
    - "Find all tech stocks above 40"
    - "Show me healthcare stocks with buy signals"
    - "What has the highest scores?"
    """
    try:
        screener = DailyScreener()
        results = screener.get_top_opportunities(limit=100)

        if not results:
            return "No stocks found in database."

        # Apply filters
        filtered = results

        if sector:
            filtered = [s for s in filtered if sector.lower() in s.get('sector', '').lower()]

        if min_score:
            filtered = [s for s in filtered if s.get('priority_score', 0) >= min_score]

        if with_signals:
            filtered = [s for s in filtered if s.get('triggered_alerts')]

        if not filtered:
            return f"No stocks match your criteria (sector={sector}, min_score={min_score}, with_signals={with_signals})"

        response = [f"🔍 Found {len(filtered)} stocks matching your criteria:\n"]

        for i, stock in enumerate(filtered[:20], 1):  # Limit to top 20
            response.append(
                f"{i}. {stock['symbol']} ({stock.get('sector', 'Unknown')}): "
                f"Score {stock.get('priority_score', 0)}/100"
            )

        if len(filtered) > 20:
            response.append(f"\n... and {len(filtered) - 20} more")

        return "\n".join(response)

    except Exception as e:
        logger.error(f"Error searching stocks: {e}")
        return f"Error searching stocks: {str(e)}"


# =============================================================================
# DEEP ANALYSIS TOOLS
# =============================================================================

@tool
def analyze_stock(ticker: str, portfolio_value: float = 100000) -> str:
    """
    Perform deep AI analysis on a specific stock.

    Args:
        ticker: Stock ticker symbol (e.g., "AAPL", "MSFT")
        portfolio_value: Your portfolio size for position sizing (default: $100,000)

    Returns:
        Comprehensive AI analysis with BUY/HOLD/SELL recommendation,
        confidence score, bull/bear cases, and position sizing

    Use this when the user asks about:
    - "Analyze AAPL"
    - "Should I buy Tesla?"
    - "Give me a deep dive on Microsoft"
    - "What do you think about DHR?"

    This tool takes 30-90 seconds to run as it performs comprehensive AI analysis.

    IMPORTANT: Before calling this tool, Eddie should tell the user:
    "I'm activating my specialized agent team for {ticker}. This comprehensive analysis
    takes 30-90 seconds as I coordinate:
    • 📊 Market Analyst - Technical indicators
    • 📰 News Analyst - Recent news & sentiment
    • 📱 Social Media Analyst - Community buzz
    • 💼 Fundamentals Analyst - Financial health
    • 🐂🐻 Bull & Bear Researchers - Debate team
    • ⚖️ Risk Manager - Position sizing

    Analyzing now..."
    """
    try:
        logger.info(f"🔍 Starting comprehensive analysis for {ticker.upper()}")
        logger.info("📊 Activating specialized agent team...")

        # Use fast config for bot (no news to save time)
        analyzer = DeepAnalyzer(
            config=FAST_CONFIG,
            enable_rag=True,
            debug=False
        )

        logger.info(f"🤖 Running multi-agent analysis (30-90 seconds)...")

        results = analyzer.analyze(
            ticker=ticker.upper(),
            analysis_date=date.today(),
            store_results=True
        )

        logger.info(f"✓ Analysis complete for {ticker.upper()}")

        # Extract key information
        decision = results.get('decision', 'WAIT')
        confidence = results.get('confidence', 0)

        # Format response
        decision_emoji = {
            'BUY': '✅',
            'SELL': '❌',
            'HOLD': '⏸️',
            'WAIT': '⏰'
        }.get(decision, '❓')

        response = [
            f"🔍 Deep Analysis: {ticker.upper()}\n",
            f"{decision_emoji} **Recommendation: {decision}**",
            f"📊 Confidence: {confidence}/100",
            f"💰 Suggested Position: ${(portfolio_value * 0.05):.2f} (5% of portfolio)\n"
        ]

        # Bull case
        bull_case = results['debates'].get('bull_case', '')
        if bull_case:
            response.append("🐂 Bull Case (Why to buy):")
            response.append(bull_case[:300] + "..." if len(bull_case) > 300 else bull_case)
            response.append("")

        # Bear case
        bear_case = results['debates'].get('bear_case', '')
        if bear_case:
            response.append("🐻 Bear Case (Why to avoid):")
            response.append(bear_case[:300] + "..." if len(bear_case) > 300 else bear_case)
            response.append("")

        # Final decision details
        final_decision = results.get('final_trade_decision', '')
        if final_decision:
            response.append("📝 Final Analysis:")
            response.append(final_decision[:400] + "..." if len(final_decision) > 400 else final_decision)

        analyzer.close()

        return "\n".join(response)

    except Exception as e:
        logger.error(f"Error analyzing stock {ticker}: {e}")
        return f"Error analyzing {ticker}: {str(e)}"


@tool
def get_stock_summary(ticker: str) -> str:
    """
    Get a quick summary of a stock without deep analysis.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Quick overview with current price, sector, and latest screener score

    Use this for quick lookups without full AI analysis.
    """
    try:
        db, ticker_ops, scan_ops, _ = get_db()

        # Get ticker info
        ticker_info = ticker_ops.get_ticker(symbol=ticker.upper())
        if not ticker_info:
            return f"Ticker {ticker} not found in database."

        # Get latest scan result
        latest_scan = scan_ops.get_top_opportunities(limit=200)
        stock_scan = next((s for s in latest_scan if s['symbol'] == ticker.upper()), None)

        response = [f"📋 {ticker.upper()} - Quick Summary\n"]

        if ticker_info:
            response.append(f"Company: {ticker_info.get('company_name', 'N/A')}")
            response.append(f"Sector: {ticker_info.get('sector', 'N/A')}")

        if stock_scan:
            response.append(f"\nLatest Screener Score: {stock_scan.get('priority_score', 0)}/100")
            response.append(f"Current Price: ${stock_scan.get('price', 0):.2f}")

            if stock_scan.get('triggered_alerts'):
                response.append(f"Active Signals: {', '.join(stock_scan['triggered_alerts'])}")
        else:
            response.append("\nNo recent screening data available.")

        return "\n".join(response)

    except Exception as e:
        logger.error(f"Error getting stock summary: {e}")
        return f"Error getting summary for {ticker}: {str(e)}"


# =============================================================================
# MARKET DATA TOOLS
# =============================================================================

@tool
def get_stock_info(ticker: str) -> str:
    """
    Get detailed company information for a stock.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Company name, sector, industry, and other details
    """
    try:
        db, ticker_ops, _, _ = get_db()

        ticker_info = ticker_ops.get_ticker(symbol=ticker.upper())
        if not ticker_info:
            return f"Ticker {ticker} not found."

        response = [
            f"🏢 {ticker.upper()} Company Information\n",
            f"Name: {ticker_info.get('company_name', 'N/A')}",
            f"Sector: {ticker_info.get('sector', 'N/A')}",
            f"Industry: {ticker_info.get('industry', 'N/A')}",
            f"Active: {'Yes' if ticker_info.get('is_active') else 'No'}"
        ]

        return "\n".join(response)

    except Exception as e:
        return f"Error getting info for {ticker}: {str(e)}"


# =============================================================================
# HELP & EDUCATION TOOLS
# =============================================================================

@tool
def explain_metric(metric_name: str) -> str:
    """
    Explain what a specific screener metric means.

    Args:
        metric_name: Name of the metric to explain (e.g., "priority_score", "sector_strength",
                     "momentum", "T/V/M/F scores", "buy_signals", "RSI", "MACD")

    Returns:
        Detailed explanation of the metric with interpretation guidelines

    Use this when users ask "what does X mean?" or "explain X"
    """
    metric_lower = metric_name.lower()

    explanations = {
        "priority_score": """
🎯 **Priority Score** (0-100)

Composite score combining all technical indicators for a stock.

**Interpretation:**
• 60-100: 🔥 Strong buy candidate - Multiple bullish signals aligned
• 50-59: ✅ Good buy signal - Several positive indicators
• 40-49: ⚠️ Moderate signal - Worth investigating with AI analysis
• 30-39: ⏸️ Weak signal - Wait for better setup
• 0-29: ❌ No signal - Avoid or wait

**Components:** Technical (T) + Volume (V) + Momentum (M) + Fundamental (F) scores
""",

        "sector_strength": """
📊 **Sector Strength** (0-100%)

Average performance of all stocks in a sector based on technical indicators.

**Interpretation:**
• >40%: 💪 Strong sector - Good opportunities
• 20-40%: ➖ Neutral - Moderate opportunities
• <20%: 📉 Weak sector - Few opportunities

**Use:** Focus on sectors >30% for best results
""",

        "momentum": """
💨 **Momentum** (Strong/Neutral/Weak)

Recent price trend combined with volume analysis.

**Interpretation:**
• 🔥 Strong: Clear uptrend + increasing volume → Bullish
• ⚪ Neutral: Sideways movement → Wait and see
• 📉 Weak: Downtrend or declining volume → Bearish

**Use:** Prefer "Strong" or "Neutral" over "Weak"
""",

        "tvmf": """
📈 **T/V/M/F Breakdown** - Components of Priority Score

When you see "Score: 41 (T:35 V:5 M:65 F:65)":

• **T (Technical)**: MACD, RSI, Bollinger Band signals (max 40)
• **V (Volume)**: Trading activity vs average (max 20)
• **M (Momentum)**: Price trend strength (max 20)
• **F (Fundamental)**: PE ratio, market cap quality (max 20)

**Total = T + V + M + F** (max 100)

Higher numbers in each category = stronger signal in that area.
""",

        "buy_signals": """
🚨 **Buy Signals** - Specific Bullish Technical Patterns

Count of stocks showing these patterns:
• MACD Bullish Cross: Moving averages crossing upward (momentum building)
• RSI Oversold: Stock potentially undervalued (RSI < 30)
• Volume Spike: Unusual trading activity (potential breakout)
• Bollinger Band Touch: Price at support/resistance levels

**0 signals = No strong technical triggers currently** (normal in sideways markets)
""",

        "rsi": """
📉 **RSI (Relative Strength Index)** - Momentum Oscillator

Measures if a stock is overbought or oversold.

**Interpretation:**
• RSI > 70: Overbought (may pullback)
• RSI 30-70: Normal range
• RSI < 30: Oversold (may bounce)

**Use:** Look for RSI < 30 as potential entry points
""",

        "macd": """
📊 **MACD (Moving Average Convergence Divergence)** - Trend & Momentum

Shows relationship between two moving averages.

**Key Signal:**
• Bullish Cross: MACD line crosses above signal line → BUY signal
• Bearish Cross: MACD line crosses below signal line → SELL signal

**Use:** Bullish cross indicates momentum building for upward move
"""
    }

    # Find matching explanation
    for key, explanation in explanations.items():
        if key in metric_lower or metric_lower in key:
            return explanation

    # If not found, return general guide
    return f"""
Metric "{metric_name}" not found in knowledge base.

Available metrics to explain:
• priority_score - Overall stock score
• sector_strength - Sector performance
• momentum - Price trend strength
• tvmf - T/V/M/F score breakdown
• buy_signals - Technical pattern counts
• rsi - Relative Strength Index
• macd - Moving Average Convergence/Divergence

Try asking about one of these, or use the `show_legend` tool for complete documentation.
"""


@tool
def show_legend() -> str:
    """
    Show the complete screener metrics legend with all interpretations.

    Returns:
        Comprehensive guide to all metrics and their meanings

    Use this when the user asks for:
    - "Show me the legend"
    - "Explain all metrics"
    - "How do I read the results?"
    - "What do these numbers mean?"
    """
    return """
📖 **Complete Screener Metrics Guide**

**1. Priority Score (0-100)**
• 60-100: 🔥 Strong buy candidate
• 50-59: ✅ Good buy signal
• 40-49: ⚠️ Moderate - investigate further
• 30-39: ⏸️ Weak signal
• 0-29: ❌ No signal

**2. Sector Strength (0-100%)**
• >40%: 💪 Strong sector
• 20-40%: ➖ Neutral
• <20%: 📉 Weak sector

**3. Buy Signals (Count)**
Types detected:
• MACD Bullish Cross
• RSI Oversold
• Volume Spike
• Bollinger Band Touch

**4. Momentum**
• 🔥 Strong: Uptrend + volume
• ⚪ Neutral: Sideways
• 📉 Weak: Downtrend

**5. T/V/M/F Scores**
• T: Technical indicators
• V: Volume analysis
• M: Momentum strength
• F: Fundamental quality

**💡 Recommended Strategy:**
1. Start with sectors >30% strength
2. Focus on stocks with score >40
3. Look for buy signals
4. Avoid "Weak" momentum
5. Use AI to analyze top 3-5 picks

**Use `explain_metric("metric_name")` for detailed explanations of specific metrics.**
"""


# =============================================================================
# AGENT ORCHESTRATION TOOLS (Phase 3)
# =============================================================================

@tool
def explain_agents() -> str:
    """
    Explain Eddie's specialized agent team and what each agent does.

    Use this when:
    - User asks "What agents do you have?"
    - User asks "How do you analyze stocks?"
    - You want to explain your capabilities

    Shows all available specialized agents and their roles.
    """
    return """
🤖 Eddie's Specialized Agent Team

When I analyze stocks deeply (using analyze_stock), I orchestrate a team of specialized AI agents:

## Analyst Agents
📊 **Market Analyst**
   Role: Technical analysis expert
   Analyzes: Charts, indicators (MACD, RSI, Bollinger Bands, Moving Averages)
   Speed: ~15-20 seconds
   When Used: Understanding price trends and momentum

📰 **News Analyst**
   Role: News and sentiment expert
   Analyzes: Recent news, market-moving events, sentiment
   Speed: ~10-15 seconds
   When Used: Gauging market reaction to news

📱 **Social Media Analyst**
   Role: Community sentiment expert
   Analyzes: Reddit (r/wallstreetbets, r/stocks), Twitter trends
   Speed: ~10-15 seconds
   When Used: Understanding retail investor sentiment

💼 **Fundamentals Analyst**
   Role: Company financial health expert
   Analyzes: P/E ratios, earnings, revenue, balance sheets
   Speed: ~15-20 seconds
   When Used: Evaluating company value and health

## Research Agents
🐂 **Bull Researcher**
   Role: Builds the bullish case
   Analyzes: Why the stock could go UP
   Speed: ~10-15 seconds
   When Used: Finding reasons to buy

🐻 **Bear Researcher**
   Role: Builds the bearish case
   Analyzes: Why the stock could go DOWN
   Speed: ~10-15 seconds
   When Used: Finding risks and reasons to avoid

## Management Agents
🎯 **Research Manager**
   Role: Coordinates all analysts
   Analyzes: Synthesizes all agent findings
   Speed: ~5-10 seconds
   When Used: Creating comprehensive view

⚖️ **Risk Manager**
   Role: Assesses risk and position sizing
   Analyzes: Portfolio risk, position sizing, stop-loss levels
   Speed: ~5-10 seconds
   When Used: Determining how much to invest

## How Orchestration Works

When you ask me to "Analyze AAPL":
1. I activate all 4 analyst agents in parallel
2. They each analyze different aspects (takes ~30-60 seconds total)
3. Bull & Bear researchers debate the findings
4. Research Manager synthesizes everything
5. Risk Manager calculates position sizing
6. I present you with a comprehensive recommendation

**Total Time**: 30-90 seconds for complete analysis
**Alternative**: Ask for specific checks (news only, technical only) for 5-10 second responses

**Next**: Want to see a full analysis? Use `analyze_stock(ticker)`
"""


# =============================================================================
# QUICK SINGLE-AGENT TOOLS (Phase 3 Part 2)
# =============================================================================

# Initialize shared orchestrator (loaded on-demand)
_agent_orchestrator = None

def get_orchestrator():
    """Get or create AgentOrchestrator instance."""
    global _agent_orchestrator
    if _agent_orchestrator is None:
        from tradingagents.orchestration import AgentOrchestrator
        _agent_orchestrator = AgentOrchestrator(config=FAST_CONFIG, debug=False)
        logger.info("✓ AgentOrchestrator initialized for quick checks")
    return _agent_orchestrator


@tool
def quick_technical_check(ticker: str) -> str:
    """
    Quick technical analysis using Market Analyst ONLY (5-10 seconds).

    Much faster than full analyze_stock! Use when user asks about:
    - "What's the technical setup on AAPL?"
    - "Is TSLA in an uptrend?"
    - "Show me the charts for MSFT"
    - "What do the indicators say about NVDA?"

    Args:
        ticker: Stock ticker symbol

    Returns:
        Technical analysis with charts, indicators, trends

    Speed: 5-10 seconds (vs 30-90 for full analysis)
    """
    try:
        orchestrator = get_orchestrator()
        result = orchestrator.quick_technical_check(ticker.upper())

        return f"""
📊 Quick Technical Analysis: {ticker.upper()}
Agent: {result.agent_type}

{result.summary}

💡 For deeper analysis with fundamentals, news, and full recommendation, use analyze_stock("{ticker}")
"""
    except Exception as e:
        logger.error(f"Error in quick_technical_check for {ticker}: {e}")
        return f"Error performing quick technical check: {str(e)}"


@tool
def quick_news_check(ticker: str) -> str:
    """
    Quick news analysis using News Analyst ONLY (5-15 seconds).

    Much faster than full analyze_stock! Use when user asks about:
    - "What's the news on AAPL?"
    - "Any recent headlines for TSLA?"
    - "What's happening with MSFT?"
    - "Show me news for NVDA"

    Args:
        ticker: Stock ticker symbol

    Returns:
        Recent news, headlines, and sentiment

    Speed: 5-15 seconds (vs 30-90 for full analysis)
    """
    try:
        orchestrator = get_orchestrator()
        result = orchestrator.quick_news_check(ticker.upper())

        return f"""
📰 Quick News Analysis: {ticker.upper()}
Agent: {result.agent_type}

{result.summary}

💡 For complete analysis with technical, fundamentals, and recommendation, use analyze_stock("{ticker}")
"""
    except Exception as e:
        logger.error(f"Error in quick_news_check for {ticker}: {e}")
        return f"Error performing quick news check: {str(e)}"


@tool
def quick_sentiment_check(ticker: str) -> str:
    """
    Quick social media sentiment using Social Media Analyst ONLY (5-10 seconds).

    Much faster than full analyze_stock! Use when user asks about:
    - "What's Reddit saying about AAPL?"
    - "Is TSLA trending on social media?"
    - "What's the sentiment on MSFT?"
    - "Community opinion on NVDA?"

    Args:
        ticker: Stock ticker symbol

    Returns:
        Social media sentiment from Reddit, Twitter

    Speed: 5-10 seconds (vs 30-90 for full analysis)
    """
    try:
        orchestrator = get_orchestrator()
        result = orchestrator.quick_sentiment_check(ticker.upper())

        return f"""
📱 Quick Sentiment Analysis: {ticker.upper()}
Agent: {result.agent_type}

{result.summary}

💡 For comprehensive analysis with full recommendation, use analyze_stock("{ticker}")
"""
    except Exception as e:
        logger.error(f"Error in quick_sentiment_check for {ticker}: {e}")
        return f"Error performing quick sentiment check: {str(e)}"


@tool
def quick_fundamentals_check(ticker: str) -> str:
    """
    Quick fundamentals analysis using Fundamentals Analyst ONLY (5-10 seconds).

    Much faster than full analyze_stock! Use when user asks about:
    - "What are AAPL's financials?"
    - "Is TSLA profitable?"
    - "Show me MSFT's balance sheet"
    - "NVDA's earnings and revenue?"

    Args:
        ticker: Stock ticker symbol

    Returns:
        Financial metrics, P/E ratio, earnings, revenue

    Speed: 5-10 seconds (vs 30-90 for full analysis)
    """
    try:
        orchestrator = get_orchestrator()
        result = orchestrator.quick_fundamentals_check(ticker.upper())

        return f"""
💼 Quick Fundamentals Analysis: {ticker.upper()}
Agent: {result.agent_type}

{result.summary}

💡 For complete analysis with buy/sell recommendation, use analyze_stock("{ticker}")
"""
    except Exception as e:
        logger.error(f"Error in quick_fundamentals_check for {ticker}: {e}")
        return f"Error performing quick fundamentals check: {str(e)}"


# =============================================================================
# LEARNING & MEMORY TOOLS (Phase 3 Part 3 / Phase 4 Prep)
# =============================================================================

@tool
def check_past_performance(ticker: str, days_back: int = 30) -> str:
    """
    Check Eddie's past recommendations and analysis for this stock.

    Shows historical accuracy, previous calls, and what Eddie learned.

    Args:
        ticker: Stock ticker symbol
        days_back: How many days of history to review (default: 30)

    Returns:
        Historical performance summary with Eddie's track record

    Use this when:
    - User asks "What did you say about AAPL before?"
    - User wants to know Eddie's track record
    - Reviewing past recommendations
    - Learning from previous analysis
    """
    try:
        db, ticker_ops, _, _ = get_db()

        # Get ticker ID
        ticker_id = ticker_ops.get_ticker_id(ticker.upper())
        if not ticker_id:
            return f"No historical data found for {ticker}"

        # Get past analyses from database
        from datetime import datetime, timedelta, timezone
        from_date = datetime.now(timezone.utc) - timedelta(days=days_back)

        # Query analyses table
        query = """
            SELECT analysis_date, recommendation, confidence, price_at_analysis
            FROM analyses
            WHERE ticker_id = %s
            AND analysis_date >= %s
            ORDER BY analysis_date DESC
            LIMIT 10
        """

        with db.get_cursor() as cursor:
            cursor.execute(query, (ticker_id, from_date))
            results = cursor.fetchall()

        if not results:
            return f"No past analyses found for {ticker} in the last {days_back} days"

        response = [
            f"📚 Eddie's Past Analysis for {ticker.upper()} (Last {days_back} days)\n",
            f"Found {len(results)} previous analyses:\n"
        ]

        for i, (analysis_date, recommendation, confidence, price) in enumerate(results, 1):
            response.append(
                f"{i}. {analysis_date.strftime('%Y-%m-%d')}: {recommendation} "
                f"(Confidence: {confidence}/100) @ ${price:.2f}"
            )

        response.append("\n💡 Use this history to inform current recommendations!")

        return "\n".join(response)

    except Exception as e:
        logger.error(f"Error checking past performance for {ticker}: {e}")
        return f"Error retrieving historical data: {str(e)}"


@tool
def find_similar_situations(ticker: str, top_n: int = 5) -> str:
    """
    Find similar past situations using RAG (vector similarity search).

    Searches Eddie's memory for stocks with similar patterns, indicators,
    or market conditions. Uses AI embeddings to find relevant past analyses.

    Args:
        ticker: Stock ticker symbol to analyze
        top_n: Number of similar situations to return (default: 5)

    Returns:
        Similar past analyses with outcomes and lessons learned

    Use this when:
    - User asks "Have you seen this pattern before?"
    - Looking for comparable situations
    - Learning from similar stocks
    - Pattern recognition queries
    """
    try:
        # Get current stock data for comparison
        db, ticker_ops, scan_ops, _ = get_db()

        ticker_info = ticker_ops.get_ticker(ticker.upper())
        if not ticker_info:
            return f"Ticker {ticker} not found"

        # Get latest scan for current state
        ticker_id = ticker_ops.get_ticker_id(ticker.upper())
        latest_scan = scan_ops.get_latest_scan_for_ticker(ticker_id)

        if not latest_scan:
            return f"No recent data available for similarity search on {ticker}"

        # Build query for RAG search
        sector = ticker_info.get('sector', 'Unknown')
        score = latest_scan.get('priority_score', 0)

        search_query = f"""
        Stock: {ticker.upper()}
        Sector: {sector}
        Priority Score: {score}
        Looking for similar stocks with comparable patterns and outcomes
        """

        # Use RAG to find similar situations
        from tradingagents.rag import ContextRetriever

        retriever = ContextRetriever(db)
        similar_contexts = retriever.retrieve_context(
            query=search_query,
            company=ticker.upper(),
            top_k=top_n
        )

        if not similar_contexts:
            return f"No similar situations found in Eddie's memory for {ticker}"

        response = [
            f"🔍 Similar Situations to {ticker.upper()}\n",
            f"Found {len(similar_contexts)} comparable past analyses:\n"
        ]

        for i, context in enumerate(similar_contexts, 1):
            # Extract relevant info from context
            company = context.get('company', 'Unknown')
            date = context.get('date', 'Unknown')
            similarity = context.get('similarity_score', 0)

            response.append(
                f"{i}. {company} on {date} (Similarity: {similarity:.2%})"
            )

        response.append("\n💡 These situations share similar technical or fundamental patterns!")

        return "\n".join(response)

    except Exception as e:
        logger.error(f"Error finding similar situations for {ticker}: {e}")
        return f"Error searching for similar situations: {str(e)}"


@tool
def what_did_i_learn(ticker: str) -> str:
    """
    Show what Eddie learned from past analyses of this stock.

    Summarizes Eddie's evolving understanding, prediction accuracy,
    and key insights discovered over time.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Learning summary with key insights and accuracy metrics

    Use this when:
    - User asks "What do you know about AAPL?"
    - Reviewing Eddie's knowledge base
    - Understanding Eddie's learning progress
    - Transparency about AI learning
    """
    try:
        db, ticker_ops, _, _ = get_db()

        ticker_id = ticker_ops.get_ticker_id(ticker.upper())
        if not ticker_id:
            return f"No learning data available for {ticker}"

        # Get all analyses for this ticker
        query = """
            SELECT COUNT(*) as analysis_count,
                   AVG(confidence) as avg_confidence,
                   STRING_AGG(DISTINCT recommendation, ', ') as recommendations
            FROM analyses
            WHERE ticker_id = %s
        """

        with db.get_cursor() as cursor:
            cursor.execute(query, (ticker_id,))
            result = cursor.fetchone()

        if not result or result[0] == 0:
            return f"Eddie hasn't analyzed {ticker} yet - no learning data available"

        analysis_count, avg_confidence, recommendations = result

        response = [
            f"🧠 What Eddie Learned About {ticker.upper()}\n",
            f"Analyses Performed: {analysis_count}",
            f"Average Confidence: {avg_confidence:.1f}/100",
            f"Recommendations Made: {recommendations}\n",
            "Key Insights:"
        ]

        # Add insights based on analysis count
        if analysis_count >= 5:
            response.append("• 📊 Well-studied stock with multiple analyses")
        else:
            response.append("• 📊 Limited analysis history - more data needed")

        if avg_confidence and avg_confidence > 70:
            response.append("• ✅ High confidence in predictions for this stock")
        elif avg_confidence and avg_confidence < 50:
            response.append("• ⚠️ Lower confidence - this stock is harder to predict")

        response.append(f"\n💡 Eddie's understanding improves with each analysis!")

        return "\n".join(response)

    except Exception as e:
        logger.error(f"Error retrieving learning data for {ticker}: {e}")
        return f"Error accessing learning data: {str(e)}"


# =============================================================================
# INTERNET VALIDATION TOOLS (Phase 3 Part 3)
# =============================================================================

@tool
def validate_news_multi_source(ticker: str) -> str:
    """
    Cross-validate news across multiple internet sources.

    Checks consistency of news sentiment and headlines across different
    news providers to detect bias or misinformation.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Multi-source news validation report with consensus sentiment

    Use this when:
    - User questions news reliability
    - Detecting conflicting narratives
    - Verifying major news events
    - Building trust in news data
    """
    try:
        # This uses existing news data but analyzes for consistency
        from tradingagents.agents.utils.agent_utils import get_news

        # Get news from primary source (yfinance)
        news_data = get_news.invoke({"company": ticker.upper(), "days_back": 7})

        if not news_data or "No news" in str(news_data):
            return f"No news data available for multi-source validation on {ticker}"

        # Parse news data
        import json
        try:
            news_items = json.loads(news_data) if isinstance(news_data, str) else news_data
        except:
            news_items = []

        if not news_items:
            return f"No news articles found for {ticker} in the last 7 days"

        # Analyze sentiment consistency
        positive_count = 0
        negative_count = 0
        neutral_count = 0

        headlines = []

        for item in news_items[:10]:  # Top 10 articles
            if isinstance(item, dict):
                title = item.get('title', '')
                headlines.append(title)

                # Simple sentiment analysis based on keywords
                title_lower = title.lower()
                if any(word in title_lower for word in ['up', 'gain', 'high', 'beat', 'strong', 'positive']):
                    positive_count += 1
                elif any(word in title_lower for word in ['down', 'fall', 'low', 'miss', 'weak', 'negative']):
                    negative_count += 1
                else:
                    neutral_count += 1

        total = positive_count + negative_count + neutral_count

        if total == 0:
            return f"Unable to analyze news sentiment for {ticker}"

        # Calculate sentiment percentages
        positive_pct = (positive_count / total) * 100
        negative_pct = (negative_count / total) * 100
        neutral_pct = (neutral_count / total) * 100

        # Determine consensus
        if positive_pct > 60:
            consensus = "📈 Bullish Consensus"
        elif negative_pct > 60:
            consensus = "📉 Bearish Consensus"
        elif positive_pct > negative_pct:
            consensus = "↗️ Slight Bullish Lean"
        elif negative_pct > positive_pct:
            consensus = "↘️ Slight Bearish Lean"
        else:
            consensus = "↔️ Neutral/Mixed"

        response = [
            f"📰 Multi-Source News Validation: {ticker.upper()}\n",
            f"Articles Analyzed: {total}",
            f"Sentiment Breakdown:",
            f"  • Positive: {positive_pct:.1f}% ({positive_count} articles)",
            f"  • Negative: {negative_pct:.1f}% ({negative_count} articles)",
            f"  • Neutral: {neutral_pct:.1f}% ({neutral_count} articles)\n",
            f"Consensus: {consensus}\n",
            "Recent Headlines:"
        ]

        for i, headline in enumerate(headlines[:5], 1):
            response.append(f"  {i}. {headline}")

        response.append(f"\n💡 News sentiment is {consensus.split()[1].lower()} - use this to validate analysis!")

        return "\n".join(response)

    except Exception as e:
        logger.error(f"Error validating news for {ticker}: {e}")
        return f"Error performing multi-source news validation: {str(e)}"


# =============================================================================
# DATA INTELLIGENCE & STRATEGIC DASHBOARD (Phase 3 Part 4)
# =============================================================================

def calculate_data_age(latest_scan_date: date) -> dict:
    """
    Calculate how old the scan data is and determine freshness level.

    Args:
        latest_scan_date: The most recent scan date

    Returns:
        Dictionary with age metrics and freshness assessment
    """
    from datetime import timedelta, timezone, datetime

    today = date.today()
    age_days = (today - latest_scan_date).days

    # Calculate hours for more precise age
    latest_datetime = datetime.combine(latest_scan_date, datetime.min.time())
    now = datetime.now()
    age_hours = int((now - latest_datetime).total_seconds() / 3600)

    # Determine freshness level
    if age_days == 0:
        freshness = 'FRESH'
        status_emoji = '✅'
    elif age_days == 1:
        freshness = 'MODERATE'
        status_emoji = '🟡'
    elif age_days <= 5:
        freshness = 'STALE'
        status_emoji = '⚠️'
    else:
        freshness = 'VERY_STALE'
        status_emoji = '🔴'

    # Check if weekend (data from Friday is acceptable on weekend)
    is_weekend = today.weekday() >= 5
    if is_weekend and age_days <= 2:
        # Friday data on weekend is acceptable
        freshness = 'MODERATE' if age_days == 2 else 'FRESH'
        status_emoji = '🟡' if age_days == 2 else '✅'

    return {
        'days_old': age_days,
        'hours_old': age_hours,
        'freshness_level': freshness,
        'status_emoji': status_emoji,
        'is_stale': age_days > 1,
        'is_weekend': is_weekend
    }


def detect_data_issues(db, ticker_ops, scan_ops, latest_scan_date: date) -> list:
    """
    Detect data quality issues and gaps.

    Args:
        db: Database connection
        ticker_ops: TickerOperations instance
        scan_ops: ScanOperations instance
        latest_scan_date: Most recent scan date

    Returns:
        List of issue strings
    """
    issues = []

    try:
        # Check scan coverage
        total_active = ticker_ops.get_watchlist_summary()['active_tickers']

        # Get scan count for latest date
        with db.get_cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM daily_scans WHERE scan_date = %s",
                (latest_scan_date,)
            )
            scanned_count = cursor.fetchone()[0]

            coverage_pct = (scanned_count / total_active * 100) if total_active > 0 else 0

            if coverage_pct < 80:
                issues.append(f"Low scan coverage: Only {scanned_count}/{total_active} stocks ({coverage_pct:.1f}%)")
            elif coverage_pct < 100:
                missing = total_active - scanned_count
                issues.append(f"{missing} stocks not scanned on latest date")

            # Check for analyses
            cursor.execute("SELECT COUNT(*) FROM analyses")
            analysis_count = cursor.fetchone()[0]

            if analysis_count == 0:
                issues.append("No deep analyses performed yet - RAG pattern recognition unavailable")
            elif analysis_count < 5:
                issues.append(f"Only {analysis_count} analyses - need 5+ for robust pattern recognition")

            # Check data age
            age_info = calculate_data_age(latest_scan_date)
            if age_info['is_stale']:
                issues.append(f"Data is {age_info['days_old']} days old - recommend refresh")

    except Exception as e:
        logger.error(f"Error detecting data issues: {e}")
        issues.append(f"Error checking data quality: {str(e)}")

    return issues


def generate_strategic_recommendations(
    db,
    ticker_ops,
    scan_ops,
    data_age_info: dict,
    analysis_count: int,
    top_stocks: list,
    coverage_pct: float
) -> list:
    """
    Generate strategic recommendations based on database state.

    Args:
        db: Database connection
        ticker_ops: TickerOperations instance
        scan_ops: ScanOperations instance
        data_age_info: Output from calculate_data_age()
        analysis_count: Total number of analyses
        top_stocks: Top opportunities from latest scan
        coverage_pct: Scan coverage percentage

    Returns:
        List of recommendation dictionaries
    """
    recommendations = []

    try:
        # Priority 1: Stale data
        if data_age_info['days_old'] > 1:
            recommendations.append({
                'priority': 'HIGH',
                'emoji': '🔄',
                'action': 'Refresh Data',
                'reason': f"Data is {data_age_info['days_old']} days old - prices and signals may have changed",
                'suggestion': "Run the screener to get fresh data: 'Run screener'",
                'auto_action': 'run_screener'
            })

        # Priority 2: No analyses (can't use RAG/learning)
        if analysis_count == 0:
            top_3 = [s['symbol'] for s in top_stocks[:3]] if top_stocks else []
            recommendations.append({
                'priority': 'HIGH',
                'emoji': '📚',
                'action': 'Build Intelligence Base',
                'reason': 'No analyses yet - pattern recognition and learning features unavailable',
                'suggestion': f"Analyze top stocks to activate RAG: {', '.join(top_3) if top_3 else 'top opportunities'}",
                'auto_action': None
            })
        elif analysis_count < 5:
            recommendations.append({
                'priority': 'MEDIUM',
                'emoji': '🧠',
                'action': 'Expand Intelligence',
                'reason': f'Only {analysis_count} analyses - need more for robust pattern recognition',
                'suggestion': 'Analyze 5-10 stocks across different sectors for better learning',
                'auto_action': None
            })

        # Priority 3: Low coverage
        if coverage_pct < 80:
            recommendations.append({
                'priority': 'MEDIUM',
                'emoji': '📊',
                'action': 'Investigate Coverage Gaps',
                'reason': f'Only {coverage_pct:.1f}% of watchlist scanned',
                'suggestion': 'Check which stocks are missing and why',
                'auto_action': None
            })

        # Priority 4: Strong opportunities available (data is fresh)
        if not data_age_info['is_stale'] and top_stocks:
            top_stock = top_stocks[0]
            recommendations.append({
                'priority': 'LOW',
                'emoji': '🎯',
                'action': 'Analyze Top Opportunity',
                'reason': f"{top_stock['symbol']} shows strong signals (Score: {top_stock.get('priority_score', 0)}/100)",
                'suggestion': f"Deep dive on {top_stock['symbol']} - {top_stock.get('sector', 'Unknown')} sector",
                'auto_action': f"analyze_{top_stock['symbol']}"
            })

        # Sort by priority
        priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 99))

    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        recommendations.append({
            'priority': 'HIGH',
            'emoji': '⚠️',
            'action': 'Error',
            'reason': f'Could not generate recommendations: {str(e)}',
            'suggestion': 'Check database connectivity',
            'auto_action': None
        })

    return recommendations


@tool
def show_data_dashboard() -> str:
    """
    Show comprehensive database status and strategic recommendations.

    This is Eddie's intelligence dashboard - shows current data state,
    identifies gaps, and recommends strategic next steps.

    Returns:
        Comprehensive dashboard with:
        - Watchlist summary (stocks, sectors, priorities)
        - Scan status (latest date, coverage, freshness)
        - Analysis history (count, RAG context)
        - Top opportunities from latest scan
        - Data quality issues/warnings
        - Strategic recommendations for next steps

    Use this when:
    - User asks "What data do you have?"
    - User asks "What should I do next?"
    - User asks "Is the data fresh?"
    - Starting complex analysis (check data quality first)
    - User wants to understand database state

    Eddie should use this proactively to make data-driven recommendations!
    """
    try:
        db, ticker_ops, scan_ops, _ = get_db()

        # ===== WATCHLIST STATUS =====
        watchlist = ticker_ops.get_watchlist_summary()

        # ===== SCAN STATUS =====
        with db.get_cursor() as cursor:
            # Get latest scan date
            cursor.execute("SELECT MAX(scan_date) FROM daily_scans")
            latest_scan_date = cursor.fetchone()[0]

            if not latest_scan_date:
                return "📊 DATA DASHBOARD\n\n⚠️ No scan data available yet.\n\nRecommendation: Run the screener to populate the database."

            # Get scan count for latest date
            cursor.execute(
                "SELECT COUNT(*) FROM daily_scans WHERE scan_date = %s",
                (latest_scan_date,)
            )
            scanned_count = cursor.fetchone()[0]

            # Calculate coverage
            total_active = watchlist['active_tickers']
            coverage_pct = (scanned_count / total_active * 100) if total_active > 0 else 0

            # Get total historical scans
            cursor.execute("SELECT COUNT(*) FROM daily_scans")
            total_scans = cursor.fetchone()[0]

            # Get data age
            data_age = calculate_data_age(latest_scan_date)

            # ===== ANALYSIS HISTORY =====
            cursor.execute("SELECT COUNT(*) FROM analyses")
            analysis_count = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM analyses WHERE embedding IS NOT NULL"
            )
            rag_context_count = cursor.fetchone()[0]

        # ===== TOP OPPORTUNITIES =====
        top_stocks = scan_ops.get_top_opportunities(scan_date=latest_scan_date, limit=5)

        # ===== DATA ISSUES =====
        issues = detect_data_issues(db, ticker_ops, scan_ops, latest_scan_date)

        # ===== STRATEGIC RECOMMENDATIONS =====
        recommendations = generate_strategic_recommendations(
            db, ticker_ops, scan_ops, data_age, analysis_count, top_stocks, coverage_pct
        )

        # ===== FORMAT DASHBOARD =====
        response = ["📊 EDDIE'S DATA DASHBOARD", "=" * 60, ""]

        # Watchlist Section
        response.extend([
            "WATCHLIST STATUS",
            f"• Total Stocks: {watchlist['total_tickers']}",
            f"• Active: {watchlist['active_tickers']} ({(watchlist['active_tickers']/watchlist['total_tickers']*100):.0f}%)",
            f"• Sectors: {watchlist['sectors_count']}",
        ])

        # Show top 3 sectors
        if watchlist.get('sectors'):
            top_sectors = sorted(watchlist['sectors'], key=lambda x: x['count'], reverse=True)[:3]
            sector_str = ", ".join([f"{s['sector']}: {s['count']}" for s in top_sectors])
            response.append(f"  Top: {sector_str}")

        response.append(f"• Priority: High: {watchlist.get('high_priority', 0)}, "
                       f"Medium: {watchlist.get('medium_priority', 0)}, "
                       f"Low: {watchlist.get('low_priority', 0)}")
        response.append("")

        # Scan Section
        response.extend([
            "SCAN STATUS",
            f"• Latest Scan: {latest_scan_date} ({data_age['days_old']} days ago)",
            f"• Coverage: {scanned_count}/{total_active} stocks ({coverage_pct:.1f}%)",
            f"• Data Freshness: {data_age['status_emoji']} {data_age['freshness_level']}",
            f"• Historical Scans: {total_scans} total",
            ""
        ])

        # Analysis Section
        response.extend([
            "ANALYSIS HISTORY",
            f"• Deep Analyses: {analysis_count}",
            f"• RAG Context: {rag_context_count} embeddings available",
        ])

        if analysis_count == 0:
            response.append("• Status: No analyses yet - pattern recognition inactive")
        elif analysis_count < 5:
            response.append(f"• Status: Building intelligence ({analysis_count}/5 minimum for RAG)")
        else:
            response.append(f"• Status: ✓ Pattern recognition active")

        response.append("")

        # Top Opportunities Section
        if top_stocks:
            response.extend([
                "TOP OPPORTUNITIES (from latest scan)",
            ])
            for i, stock in enumerate(top_stocks, 1):
                score = stock.get('priority_score', 0)
                sector = stock.get('sector', 'Unknown')
                symbol = stock.get('symbol', '?')

                # Score interpretation
                if score >= 50:
                    score_label = "🔥 Strong"
                elif score >= 40:
                    score_label = "✅ Good"
                elif score >= 30:
                    score_label = "⚠️ Moderate"
                else:
                    score_label = "📉 Weak"

                response.append(f"{i}. {symbol} - Score: {score}/100 {score_label} ({sector})")

            response.append("")

        # Data Issues Section
        if issues:
            response.extend([
                "⚠️ DATA QUALITY ISSUES",
            ])
            for issue in issues:
                response.append(f"• {issue}")
            response.append("")

        # Strategic Recommendations Section
        response.extend([
            "🎯 STRATEGIC RECOMMENDATIONS",
            ""
        ])

        for rec in recommendations:
            response.append(f"{rec['emoji']} **{rec['priority']} PRIORITY**: {rec['action']}")
            response.append(f"   Reason: {rec['reason']}")
            response.append(f"   → {rec['suggestion']}")
            response.append("")

        # Auto-refresh offer if data is very stale
        if data_age['days_old'] > 2:
            response.extend([
                "💡 QUICK ACTION",
                "Your data is significantly stale. Would you like me to run",
                "a fresh screener scan? Just ask 'Run the screener' and I'll",
                "update everything with the latest market data.",
                ""
            ])

        response.extend([
            "=" * 60,
            "💬 Ask me anything based on this data, or request specific actions!"
        ])

        return "\n".join(response)

    except Exception as e:
        logger.error(f"Error generating data dashboard: {e}")
        return f"⚠️ Error generating dashboard: {str(e)}\n\nPlease check database connectivity."


# =============================================================================
# PORTFOLIO TOOLS (Placeholder - extend as needed)
# =============================================================================

@tool
def get_portfolio_status() -> str:
    """
    Get current portfolio positions and status.

    Returns:
        List of current holdings with values and performance

    Note: This is a placeholder. Implement based on your portfolio structure.
    """
    try:
        db, _, _, portfolio_ops = get_db()

        # This would query your actual portfolio
        return """
📊 Portfolio Status

This feature requires portfolio tracking setup.

To view your portfolio:
1. Add holdings to database
2. Track positions over time
3. Calculate performance

Use the portfolio module for full functionality.
"""

    except Exception as e:
        return f"Error getting portfolio: {str(e)}"


# =============================================================================
# DATA VALIDATION TOOLS (Eddie's Credibility Features)
# =============================================================================

@tool
def check_data_quality(ticker: str) -> str:
    """
    Check data quality and validation status for a stock.

    Shows Eddie's transparency about data sources, freshness, and credibility.

    Args:
        ticker: Stock ticker symbol (e.g., "AAPL", "TSLA")

    Returns:
        Data quality report with validation score and warnings

    Use this when:
    - User asks "How reliable is this data?"
    - You want to show transparency about data sources
    - Before making important recommendations
    - To build trust with data quality disclosure
    """
    try:
        # Get latest stock data to check timestamp
        db, ticker_ops, scan_ops, _ = get_db()

        # Get ticker info
        ticker_id = ticker_ops.get_ticker_id(ticker.upper())
        if not ticker_id:
            return f"Ticker {ticker} not found in database."

        # Get latest scan result to check data freshness
        latest_scan = scan_ops.get_latest_scan_for_ticker(ticker_id)

        if latest_scan:
            price_timestamp = latest_scan.get('scanned_at')
        else:
            from datetime import datetime, timezone
            # If no scan, use a default old timestamp
            price_timestamp = datetime.now(timezone.utc)

        # Determine data sources from config
        config = DEFAULT_CONFIG
        news_source = config['data_vendors'].get('news_data', 'yfinance')
        price_source = config['data_vendors'].get('core_stock_apis', 'yfinance')
        fundamental_source = config['data_vendors'].get('fundamental_data', 'yfinance')

        # Validate data quality
        report = validate_data_quality(
            ticker=ticker.upper(),
            price_timestamp=price_timestamp,
            price_source=price_source,
            news_source=news_source,
            fundamental_source=fundamental_source,
            config=config.get('validation', {})
        )

        # Format for display
        return report.format_for_display()

    except Exception as e:
        logger.error(f"Error checking data quality for {ticker}: {e}")
        return f"Error validating data quality for {ticker}: {str(e)}"


@tool
def validate_price_sources(ticker: str) -> str:
    """
    Cross-validate stock price across multiple data sources (yfinance + Alpha Vantage).

    Shows price comparison, discrepancies, and confidence score for price accuracy.

    Args:
        ticker: Stock ticker symbol (e.g., "AAPL", "TSLA")

    Returns:
        Multi-source price validation report with confidence score

    Use this when:
    - User questions price accuracy
    - Making important buy/sell decisions
    - Detecting potential data errors
    - Building trust in price data
    """
    try:
        from tradingagents.validation import validate_price_multi_source

        report = validate_price_multi_source(ticker.upper())
        return report.format_for_display()

    except Exception as e:
        logger.error(f"Error validating price sources for {ticker}: {e}")
        return f"Error validating price sources for {ticker}: {str(e)}"


@tool
def check_earnings_risk(ticker: str) -> str:
    """
    Check if stock is near earnings announcement (high volatility risk window).

    Shows earnings date, proximity risk level, and trading recommendations.

    Args:
        ticker: Stock ticker symbol (e.g., "AAPL", "TSLA")

    Returns:
        Earnings proximity report with risk assessment

    Use this when:
    - Making buy/sell recommendations
    - User asks about earnings
    - Warning about volatility risks
    - Timing entry/exit points

    Eddie should ALWAYS check this before recommending new positions!
    """
    try:
        from tradingagents.validation import check_earnings_proximity

        report = check_earnings_proximity(ticker.upper())
        return report.format_for_display()

    except Exception as e:
        logger.error(f"Error checking earnings risk for {ticker}: {e}")
        return f"Error checking earnings risk for {ticker}: {str(e)}"


# =============================================================================
# EXPORT ALL TOOLS
# =============================================================================

def get_all_tools() -> List:
    """
    Get all available tools for the agent.

    Returns:
        List of LangChain tools
    """
    return [
        # Screening & Discovery
        run_screener,
        get_top_stocks,
        analyze_sector,
        search_stocks,

        # Deep Analysis
        analyze_stock,
        get_stock_summary,

        # Market Data
        get_stock_info,

        # Data Validation (Eddie's credibility & trust)
        check_data_quality,        # Phase 1: Basic data quality
        validate_price_sources,    # Phase 2: Multi-source price validation
        check_earnings_risk,       # Phase 2: Earnings proximity warnings
        validate_news_multi_source,  # Phase 3 Part 3: News sentiment validation

        # Help & Education
        explain_metric,
        show_legend,

        # Agent Orchestration (Phase 3)
        explain_agents,            # Phase 3 Part 1: Explain agent team
        quick_technical_check,     # Phase 3 Part 2: Fast technical analysis
        quick_news_check,          # Phase 3 Part 2: Fast news check
        quick_sentiment_check,     # Phase 3 Part 2: Fast social sentiment
        quick_fundamentals_check,  # Phase 3 Part 2: Fast fundamentals

        # Learning & Memory (Phase 3 Part 3 / Phase 4 Prep)
        check_past_performance,    # Eddie's historical track record
        find_similar_situations,   # RAG-powered pattern recognition
        what_did_i_learn,          # Learning summary

        # Data Intelligence & Strategic Dashboard (Phase 3 Part 4)
        show_data_dashboard,       # Comprehensive data status and strategic recommendations

        # Portfolio (placeholder)
        get_portfolio_status,
    ]
