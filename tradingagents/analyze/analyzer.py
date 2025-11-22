# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Deep Analyzer Module

Provides a simplified interface to TradingAgentsGraph with RAG enhancement.
"""

from typing import Dict, Any, Optional
from datetime import date, datetime
import logging

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.database import get_db_connection, DatabaseConnection
from tradingagents.default_config import DEFAULT_CONFIG

logger = logging.getLogger(__name__)


class DeepAnalyzer:
    """
    High-level interface for deep investment analysis with RAG.

    Wraps TradingAgentsGraph to provide a simple analysis interface.
    """

    def __init__(
        self,
        config: Dict[str, Any] = None,
        enable_rag: bool = True,
        db: Optional[DatabaseConnection] = None,
        debug: bool = False
    ):
        """
        Initialize deep analyzer.

        Args:
            config: Configuration dictionary (uses DEFAULT_CONFIG if None)
            enable_rag: Whether to enable RAG-based historical context
            db: DatabaseConnection instance (creates new if None)
            debug: Whether to run in debug mode with detailed output
        """
        # Merge config with DEFAULT_CONFIG to ensure all required fields are present
        if config:
            import copy
            merged_config = copy.deepcopy(DEFAULT_CONFIG)
            # Deep merge nested dictionaries
            for key, value in config.items():
                if isinstance(value, dict) and key in merged_config and isinstance(merged_config[key], dict):
                    merged_config[key].update(value)
                else:
                    merged_config[key] = value
            self.config = merged_config
        else:
            self.config = DEFAULT_CONFIG
        self.enable_rag = enable_rag
        self.db = db or (get_db_connection() if enable_rag else None)
        self.debug = debug

        # Initialize TradingAgentsGraph with RAG
        # Enable Langfuse if environment variable is set
        import os
        enable_langfuse = os.getenv("LANGFUSE_ENABLED", "false").lower() == "true"
        
        self.graph = TradingAgentsGraph(
            selected_analysts=["market", "social", "news", "fundamentals"],
            debug=debug,
            config=self.config,
            enable_rag=enable_rag,
            db=self.db,
            enable_langfuse=enable_langfuse,
            enable_token_tracking=False,
            enable_summarization=False,
            enable_todo_lists=False,
            enable_subagents=False
        )

        logger.info("✓ DeepAnalyzer initialized")

    def analyze(
        self,
        ticker: str,
        analysis_date: date = None,
        store_results: bool = True
    ) -> Dict[str, Any]:
        """
        Perform deep analysis on a ticker.

        Args:
            ticker: Stock ticker symbol
            analysis_date: Date to analyze (defaults to today)
            store_results: Whether to store analysis to database

        Returns:
            Analysis results dictionary with:
                - final_state: Complete agent state
                - decision: Parsed trading decision (BUY/SELL/HOLD/WAIT)
                - summary: Human-readable summary
                - confidence: Confidence score
                - reports: Individual analyst reports
        """
        if analysis_date is None:
            analysis_date = date.today()

        logger.info(f"\n{'='*70}")
        logger.info(f"DEEP ANALYSIS: {ticker} on {analysis_date}")
        logger.info(f"{'='*70}\n")

        # Run the analysis graph
        final_state, processed_signal = self.graph.propagate(
            company_name=ticker,
            trade_date=analysis_date,
            store_analysis=store_results
        )

        # Extract and structure results
        results = self._extract_results(final_state, processed_signal)

        return results

    def _extract_results(self, final_state: Dict[str, Any], processed_signal: str) -> Dict[str, Any]:
        """
        Extract structured results from final state.

        Args:
            final_state: Final state from graph execution
            processed_signal: Processed trading signal

        Returns:
            Structured results dictionary
        """
        # Extract decision
        decision = self._parse_decision(final_state.get('final_trade_decision', ''))

        # Extract confidence
        confidence = self._estimate_confidence(final_state)

        # Create summary
        summary = self._create_summary(final_state, decision, confidence)

        # Structure reports
        reports = {
            'market': final_state.get('market_report', ''),
            'sentiment': final_state.get('sentiment_report', ''),
            'news': final_state.get('news_report', ''),
            'fundamentals': final_state.get('fundamentals_report', '')
        }

        # Extract debate insights
        invest_debate = final_state.get('investment_debate_state', {})
        risk_debate = final_state.get('risk_debate_state', {})

        debates = {
            'bull_case': invest_debate.get('bull_history', ''),
            'bear_case': invest_debate.get('bear_history', ''),
            'investment_consensus': invest_debate.get('judge_decision', ''),
            'risk_assessment': risk_debate.get('judge_decision', '')
        }

        return {
            'ticker': final_state.get('company_of_interest'),
            'analysis_date': final_state.get('trade_date'),
            'decision': decision,
            'processed_signal': processed_signal,
            'confidence': confidence,
            'summary': summary,
            'reports': reports,
            'debates': debates,
            'trader_plan': final_state.get('trader_investment_plan', ''),
            'final_trade_decision': final_state.get('final_trade_decision', ''),
            'historical_context_used': bool(final_state.get('historical_context')),
            'full_state': final_state
        }

    def _parse_decision(self, final_trade_decision: str) -> str:
        """Parse trading decision from final output."""
        decision_upper = final_trade_decision.upper()

        if 'BUY' in decision_upper or 'LONG' in decision_upper:
            return 'BUY'
        elif 'SELL' in decision_upper or 'SHORT' in decision_upper:
            return 'SELL'
        elif 'HOLD' in decision_upper:
            return 'HOLD'
        else:
            return 'WAIT'

    def _estimate_confidence(self, final_state: Dict[str, Any]) -> int:
        """
        Estimate confidence score from final state.

        Uses debate consensus and report completeness as proxies.
        """
        # Start with base confidence
        confidence = 50

        # Increase confidence if we have complete reports
        reports = ['market_report', 'fundamentals_report', 'news_report', 'sentiment_report']
        complete_reports = sum(1 for r in reports if final_state.get(r))
        confidence += (complete_reports / len(reports)) * 20

        # Increase if investment debate reached consensus
        invest_debate = final_state.get('investment_debate_state', {})
        if invest_debate.get('judge_decision'):
            confidence += 10

        # Increase if risk assessment was thorough
        risk_debate = final_state.get('risk_debate_state', {})
        if risk_debate.get('judge_decision'):
            confidence += 10

        # Increase if trader plan is detailed
        if len(final_state.get('trader_investment_plan', '')) > 200:
            confidence += 10

        return min(int(confidence), 100)

    def _create_summary(self, final_state: Dict[str, Any], decision: str, confidence: int) -> str:
        """Create a human-readable summary of the analysis."""
        ticker = final_state.get('company_of_interest', 'Unknown')
        date_str = final_state.get('trade_date', 'Unknown')

        summary_parts = [
            f"Analysis of {ticker} on {date_str}",
            f"Recommendation: {decision}",
            f"Confidence: {confidence}/100"
        ]

        # Add key insights from investment debate
        invest_debate = final_state.get('investment_debate_state', {})
        if invest_debate.get('judge_decision'):
            summary_parts.append(f"Investment Consensus: {invest_debate['judge_decision'][:150]}...")

        # Add risk assessment
        risk_debate = final_state.get('risk_debate_state', {})
        if risk_debate.get('judge_decision'):
            summary_parts.append(f"Risk Assessment: {risk_debate['judge_decision'][:150]}...")

        return "\n".join(summary_parts)

    def print_results(self, results: Dict[str, Any], verbose: bool = False, plain_english: bool = False, portfolio_value: float = None):
        """
        Print analysis results in a formatted way.

        Args:
            results: Results dictionary from analyze()
            verbose: Whether to print full reports
            plain_english: Whether to print in plain English (layman-friendly)
            portfolio_value: Portfolio value for position sizing (optional)
        """
        # Plain English report
        if plain_english:
            from tradingagents.analyze.plain_english import generate_plain_english_report
            report = generate_plain_english_report(results, portfolio_value)
            print(report)
            return

        # Standard technical report
        print(f"\n{'='*70}")
        print(f"ANALYSIS RESULTS: {results['ticker']}")
        print(f"{'='*70}\n")

        print(f"📅 Date: {results['analysis_date']}")
        print(f"🎯 Decision: {results['decision']}")
        print(f"📊 Confidence: {results['confidence']}/100")
        print(f"🤖 RAG Context: {'✓ Used' if results['historical_context_used'] else '✗ Not available'}")
        print()

        # Summary
        print("📝 Summary:")
        print("-" * 70)
        print(results['summary'])
        print()

        if verbose:
            # Reports
            print("\n📈 ANALYST REPORTS:")
            print("=" * 70)

            for analyst_type, report in results['reports'].items():
                if report:
                    print(f"\n{analyst_type.upper()} ANALYST:")
                    print("-" * 70)
                    print(report[:500] + "..." if len(report) > 500 else report)

            # Debates
            print("\n💬 INVESTMENT DEBATES:")
            print("=" * 70)

            for debate_type, content in results['debates'].items():
                if content:
                    print(f"\n{debate_type.upper().replace('_', ' ')}:")
                    print("-" * 70)
                    print(content[:500] + "..." if len(content) > 500 else content)

            # Trader Plan
            if results['trader_plan']:
                print("\n📋 TRADER EXECUTION PLAN:")
                print("=" * 70)
                print(results['trader_plan'])

        # Final decision
        print(f"\n🎬 FINAL TRADE DECISION:")
        print("=" * 70)
        print(results['final_trade_decision'][:1000] if len(results['final_trade_decision']) > 1000 else results['final_trade_decision'])
        print()

    def close(self):
        """Clean up resources."""
        # Note: Database connection is a singleton shared across the application,
        # so we don't close it here. The connection pool manages itself.
        # If you need to close the database connection, use close_db_connection() from
        # tradingagents.database.connection module.
        logger.debug("DeepAnalyzer cleanup complete (database connection pool remains active)")
