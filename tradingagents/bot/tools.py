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
    """
    try:
        # Use fast config for bot (no news to save time)
        analyzer = DeepAnalyzer(
            config=FAST_CONFIG,
            enable_rag=True,
            debug=False
        )

        results = analyzer.analyze(
            ticker=ticker.upper(),
            analysis_date=date.today(),
            store_results=True
        )

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

        # Help & Education
        explain_metric,
        show_legend,

        # Portfolio (placeholder)
        get_portfolio_status,
    ]
