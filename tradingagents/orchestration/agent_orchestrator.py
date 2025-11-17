"""
Agent Orchestrator for Quick Single-Agent Queries

Provides fast access to individual specialized agents without running full analysis.
Enables Eddie to answer specific questions quickly (5-10 seconds) instead of
always running the full 30-90 second deep analysis.
"""

from typing import Dict, Any, Optional
from datetime import date
import logging

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.fast_config import FAST_CONFIG

logger = logging.getLogger(__name__)


class AgentOrchestrationResult:
    """Result from a quick agent query."""

    def __init__(
        self,
        agent_type: str,
        ticker: str,
        summary: str,
        raw_report: str,
        confidence: int = 0
    ):
        self.agent_type = agent_type
        self.ticker = ticker
        self.summary = summary
        self.raw_report = raw_report
        self.confidence = confidence

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            'agent_type': self.agent_type,
            'ticker': self.ticker,
            'summary': self.summary,
            'raw_report': self.raw_report,
            'confidence': self.confidence
        }


class AgentOrchestrator:
    """
    Orchestrator for quick single-agent queries.

    Allows Eddie to delegate to specific specialized agents for fast answers:
    - Market Analyst: Technical analysis (charts, indicators)
    - News Analyst: Recent news and events
    - Social Media Analyst: Community sentiment (Reddit, Twitter)
    - Fundamentals Analyst: Company financials

    Each query takes 5-15 seconds instead of full 30-90 second deep analysis.
    """

    def __init__(self, config: Dict[str, Any] = None, debug: bool = False):
        """
        Initialize agent orchestrator.

        Args:
            config: Configuration dictionary (uses FAST_CONFIG if None for speed)
            debug: Whether to enable debug logging
        """
        self.config = config or FAST_CONFIG
        self.debug = debug

        # We'll initialize agents on-demand to save startup time
        self._market_graph = None
        self._social_graph = None
        self._news_graph = None
        self._fundamentals_graph = None

        logger.info("✓ AgentOrchestrator initialized (agents will load on-demand)")

    def _get_market_analyst(self) -> TradingAgentsGraph:
        """Get or create Market Analyst graph."""
        if self._market_graph is None:
            self._market_graph = TradingAgentsGraph(
                selected_analysts=["market"],
                debug=self.debug,
                config=self.config,
                enable_rag=False  # Disable RAG for quick queries
            )
        return self._market_graph

    def _get_social_analyst(self) -> TradingAgentsGraph:
        """Get or create Social Media Analyst graph."""
        if self._social_graph is None:
            self._social_graph = TradingAgentsGraph(
                selected_analysts=["social"],
                debug=self.debug,
                config=self.config,
                enable_rag=False
            )
        return self._social_graph

    def _get_news_analyst(self) -> TradingAgentsGraph:
        """Get or create News Analyst graph."""
        if self._news_graph is None:
            self._news_graph = TradingAgentsGraph(
                selected_analysts=["news"],
                debug=self.debug,
                config=self.config,
                enable_rag=False
            )
        return self._news_graph

    def _get_fundamentals_analyst(self) -> TradingAgentsGraph:
        """Get or create Fundamentals Analyst graph."""
        if self._fundamentals_graph is None:
            self._fundamentals_graph = TradingAgentsGraph(
                selected_analysts=["fundamentals"],
                debug=self.debug,
                config=self.config,
                enable_rag=False
            )
        return self._fundamentals_graph

    def quick_technical_check(self, ticker: str) -> AgentOrchestrationResult:
        """
        Quick technical analysis using Market Analyst only.

        Args:
            ticker: Stock ticker symbol

        Returns:
            AgentOrchestrationResult with technical analysis summary

        Speed: 5-10 seconds
        """
        logger.info(f"📊 Running quick technical check for {ticker}")

        graph = self._get_market_analyst()
        final_state, _ = graph.propagate(
            company_name=ticker,
            trade_date=date.today(),
            store_analysis=False
        )

        # Extract market report
        market_report = final_state.get('market_report', '')

        # Create summary
        summary = self._summarize_technical_report(market_report, ticker)

        return AgentOrchestrationResult(
            agent_type="Market Analyst",
            ticker=ticker,
            summary=summary,
            raw_report=market_report,
            confidence=70
        )

    def quick_news_check(self, ticker: str) -> AgentOrchestrationResult:
        """
        Quick news analysis using News Analyst only.

        Args:
            ticker: Stock ticker symbol

        Returns:
            AgentOrchestrationResult with news summary

        Speed: 5-15 seconds
        """
        logger.info(f"📰 Running quick news check for {ticker}")

        graph = self._get_news_analyst()
        final_state, _ = graph.propagate(
            company_name=ticker,
            trade_date=date.today(),
            store_analysis=False
        )

        # Extract news report
        news_report = final_state.get('news_report', '')

        # Create summary
        summary = self._summarize_news_report(news_report, ticker)

        return AgentOrchestrationResult(
            agent_type="News Analyst",
            ticker=ticker,
            summary=summary,
            raw_report=news_report,
            confidence=75
        )

    def quick_sentiment_check(self, ticker: str) -> AgentOrchestrationResult:
        """
        Quick social media sentiment check using Social Media Analyst only.

        Args:
            ticker: Stock ticker symbol

        Returns:
            AgentOrchestrationResult with social sentiment summary

        Speed: 5-10 seconds
        """
        logger.info(f"📱 Running quick sentiment check for {ticker}")

        graph = self._get_social_analyst()
        final_state, _ = graph.propagate(
            company_name=ticker,
            trade_date=date.today(),
            store_analysis=False
        )

        # Extract sentiment report
        sentiment_report = final_state.get('sentiment_report', '')

        # Create summary
        summary = self._summarize_sentiment_report(sentiment_report, ticker)

        return AgentOrchestrationResult(
            agent_type="Social Media Analyst",
            ticker=ticker,
            summary=summary,
            raw_report=sentiment_report,
            confidence=65
        )

    def quick_fundamentals_check(self, ticker: str) -> AgentOrchestrationResult:
        """
        Quick fundamentals analysis using Fundamentals Analyst only.

        Args:
            ticker: Stock ticker symbol

        Returns:
            AgentOrchestrationResult with fundamentals summary

        Speed: 5-10 seconds
        """
        logger.info(f"💼 Running quick fundamentals check for {ticker}")

        graph = self._get_fundamentals_analyst()
        final_state, _ = graph.propagate(
            company_name=ticker,
            trade_date=date.today(),
            store_analysis=False
        )

        # Extract fundamentals report
        fundamentals_report = final_state.get('fundamentals_report', '')

        # Create summary
        summary = self._summarize_fundamentals_report(fundamentals_report, ticker)

        return AgentOrchestrationResult(
            agent_type="Fundamentals Analyst",
            ticker=ticker,
            summary=summary,
            raw_report=fundamentals_report,
            confidence=80
        )

    # Summary helper methods

    def _summarize_technical_report(self, report: str, ticker: str) -> str:
        """Create concise summary from technical report."""
        if not report:
            return f"No technical data available for {ticker}"

        # Extract key insights from report
        lines = report.split('\n')
        key_lines = [line for line in lines if any(keyword in line.lower()
                     for keyword in ['trend', 'rsi', 'support', 'resistance', 'moving average', 'signal'])]

        if key_lines:
            return '\n'.join(key_lines[:5])  # Top 5 insights
        return report[:500]  # First 500 chars if no keywords found

    def _summarize_news_report(self, report: str, ticker: str) -> str:
        """Create concise summary from news report."""
        if not report:
            return f"No recent news available for {ticker}"

        # Extract headlines and sentiment
        lines = report.split('\n')
        key_lines = [line for line in lines if any(keyword in line.lower()
                     for keyword in ['headline', 'sentiment', 'positive', 'negative', 'breaking', 'announced'])]

        if key_lines:
            return '\n'.join(key_lines[:7])  # Top 7 news items
        return report[:600]

    def _summarize_sentiment_report(self, report: str, ticker: str) -> str:
        """Create concise summary from sentiment report."""
        if not report:
            return f"No social sentiment data available for {ticker}"

        # Extract sentiment indicators
        lines = report.split('\n')
        key_lines = [line for line in lines if any(keyword in line.lower()
                     for keyword in ['bullish', 'bearish', 'sentiment', 'reddit', 'twitter', 'social', 'community'])]

        if key_lines:
            return '\n'.join(key_lines[:5])
        return report[:400]

    def _summarize_fundamentals_report(self, report: str, ticker: str) -> str:
        """Create concise summary from fundamentals report."""
        if not report:
            return f"No fundamental data available for {ticker}"

        # Extract financial metrics
        lines = report.split('\n')
        key_lines = [line for line in lines if any(keyword in line.lower()
                     for keyword in ['revenue', 'earnings', 'p/e', 'debt', 'growth', 'margin', 'cash', 'ratio'])]

        if key_lines:
            return '\n'.join(key_lines[:7])
        return report[:600]
