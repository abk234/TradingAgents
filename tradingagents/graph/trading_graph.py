# TradingAgents/graph/trading_graph.py

import os
from pathlib import Path
import json
from datetime import date
from typing import Dict, Any, Tuple, List, Optional
import logging

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.prebuilt import ToolNode

from tradingagents.agents import *
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.agents.utils.memory import FinancialSituationMemory
from tradingagents.agents.utils.agent_states import (
    AgentState,
    InvestDebateState,
    RiskDebateState,
)
from tradingagents.dataflows.config import set_config

# Import the new abstract tool methods from agent_utils
from tradingagents.agents.utils.agent_utils import (
    get_stock_data,
    get_indicators,
    get_fundamentals,
    get_balance_sheet,
    get_cashflow,
    get_income_statement,
    get_news,
    get_insider_sentiment,
    get_insider_transactions,
    get_global_news
)

from .conditional_logic import ConditionalLogic
from .setup import GraphSetup
from .propagation import Propagator
from .reflection import Reflector
from .signal_processing import SignalProcessor

# RAG and database imports
from tradingagents.database import get_db_connection, DatabaseConnection, TickerOperations
from tradingagents.rag import EmbeddingGenerator, ContextRetriever, PromptFormatter
from tradingagents.decision import FourGateFramework, GateResult

logger = logging.getLogger(__name__)


class TradingAgentsGraph:
    """Main class that orchestrates the trading agents framework."""

    def __init__(
        self,
        selected_analysts=["market", "social", "news", "fundamentals"],
        debug=False,
        config: Dict[str, Any] = None,
        enable_rag: bool = True,
        db: Optional[DatabaseConnection] = None,
    ):
        """Initialize the trading agents graph and components.

        Args:
            selected_analysts: List of analyst types to include
            debug: Whether to run in debug mode
            config: Configuration dictionary. If None, uses default config
            enable_rag: Whether to enable RAG-based historical context
            db: DatabaseConnection instance (optional, creates new if None)
        """
        self.debug = debug
        self.config = config or DEFAULT_CONFIG
        self.enable_rag = enable_rag

        # Update the interface's config
        set_config(self.config)

        # Create necessary directories
        os.makedirs(
            os.path.join(self.config["project_dir"], "dataflows/data_cache"),
            exist_ok=True,
        )

        # Initialize RAG components if enabled
        if self.enable_rag:
            try:
                self.db = db or get_db_connection()
                self.ticker_ops = TickerOperations(self.db)
                self.embedding_generator = EmbeddingGenerator()
                self.context_retriever = ContextRetriever(self.db)
                self.prompt_formatter = PromptFormatter()
                self.four_gate_framework = FourGateFramework()
                logger.info("✓ RAG system initialized")
            except Exception as e:
                logger.warning(f"⚠ RAG initialization failed: {e}. Running without RAG.")
                self.enable_rag = False
        else:
            logger.info("RAG system disabled")

        # Initialize LLMs
        if self.config["llm_provider"].lower() == "openai" or self.config["llm_provider"] == "ollama" or self.config["llm_provider"] == "openrouter":
            # For Ollama, we need to set a dummy API key since it doesn't require authentication
            api_key = "ollama" if self.config["llm_provider"] == "ollama" else None
            # Set generous timeout for local Ollama or API calls
            timeout = 120  # 2 minutes timeout for LLM responses
            self.deep_thinking_llm = ChatOpenAI(
                model=self.config["deep_think_llm"],
                base_url=self.config["backend_url"],
                api_key=api_key,
                temperature=0.7,
                timeout=timeout
            )
            self.quick_thinking_llm = ChatOpenAI(
                model=self.config["quick_think_llm"],
                base_url=self.config["backend_url"],
                api_key=api_key,
                temperature=0.7,
                timeout=timeout
            )
        elif self.config["llm_provider"].lower() == "anthropic":
            self.deep_thinking_llm = ChatAnthropic(model=self.config["deep_think_llm"], base_url=self.config["backend_url"])
            self.quick_thinking_llm = ChatAnthropic(model=self.config["quick_think_llm"], base_url=self.config["backend_url"])
        elif self.config["llm_provider"].lower() == "google":
            self.deep_thinking_llm = ChatGoogleGenerativeAI(model=self.config["deep_think_llm"])
            self.quick_thinking_llm = ChatGoogleGenerativeAI(model=self.config["quick_think_llm"])
        else:
            raise ValueError(f"Unsupported LLM provider: {self.config['llm_provider']}")
        
        # Initialize memories
        self.bull_memory = FinancialSituationMemory("bull_memory", self.config)
        self.bear_memory = FinancialSituationMemory("bear_memory", self.config)
        self.trader_memory = FinancialSituationMemory("trader_memory", self.config)
        self.invest_judge_memory = FinancialSituationMemory("invest_judge_memory", self.config)
        self.risk_manager_memory = FinancialSituationMemory("risk_manager_memory", self.config)

        # Create tool nodes
        self.tool_nodes = self._create_tool_nodes()

        # Initialize components
        self.conditional_logic = ConditionalLogic()
        self.graph_setup = GraphSetup(
            self.quick_thinking_llm,
            self.deep_thinking_llm,
            self.tool_nodes,
            self.bull_memory,
            self.bear_memory,
            self.trader_memory,
            self.invest_judge_memory,
            self.risk_manager_memory,
            self.conditional_logic,
        )

        self.propagator = Propagator()
        self.reflector = Reflector(self.quick_thinking_llm)
        self.signal_processor = SignalProcessor(self.quick_thinking_llm)

        # State tracking
        self.curr_state = None
        self.ticker = None
        self.log_states_dict = {}  # date to full state dict

        # Set up the graph
        self.graph = self.graph_setup.setup_graph(selected_analysts)

    def _create_tool_nodes(self) -> Dict[str, ToolNode]:
        """Create tool nodes for different data sources using abstract methods."""
        return {
            "market": ToolNode(
                [
                    # Core stock data tools
                    get_stock_data,
                    # Technical indicators
                    get_indicators,
                ]
            ),
            "social": ToolNode(
                [
                    # News tools for social media analysis
                    get_news,
                ]
            ),
            "news": ToolNode(
                [
                    # News and insider information
                    get_news,
                    get_global_news,
                    get_insider_sentiment,
                    get_insider_transactions,
                ]
            ),
            "fundamentals": ToolNode(
                [
                    # Fundamental analysis tools
                    get_fundamentals,
                    get_balance_sheet,
                    get_cashflow,
                    get_income_statement,
                ]
            ),
        }

    def propagate(self, company_name, trade_date, store_analysis: bool = False):
        """Run the trading agents graph for a company on a specific date.

        Args:
            company_name: Ticker symbol to analyze
            trade_date: Date of analysis
            store_analysis: Whether to store analysis results to database

        Returns:
            Tuple of (final_state, processed_signal)
        """
        self.ticker = company_name

        # Generate historical context if RAG is enabled
        historical_context = None
        if self.enable_rag:
            historical_context = self._generate_historical_context(company_name)

        # Initialize state with historical context
        init_agent_state = self.propagator.create_initial_state(
            company_name, trade_date, historical_context
        )
        args = self.propagator.get_graph_args()

        if self.debug:
            # Debug mode with tracing
            trace = []
            for chunk in self.graph.stream(init_agent_state, **args):
                if len(chunk["messages"]) == 0:
                    pass
                else:
                    chunk["messages"][-1].pretty_print()
                    trace.append(chunk)

            final_state = trace[-1]
        else:
            # Standard mode without tracing
            final_state = self.graph.invoke(init_agent_state, **args)

        # Store current state for reflection
        self.curr_state = final_state

        # Log state
        self._log_state(trade_date, final_state)

        # Optionally store analysis to database
        if store_analysis and self.enable_rag:
            self._store_analysis(company_name, trade_date, final_state)

        # Return decision and processed signal
        return final_state, self.process_signal(final_state["final_trade_decision"])

    def _log_state(self, trade_date, final_state):
        """Log the final state to a JSON file."""
        self.log_states_dict[str(trade_date)] = {
            "company_of_interest": final_state["company_of_interest"],
            "trade_date": final_state["trade_date"],
            "market_report": final_state["market_report"],
            "sentiment_report": final_state["sentiment_report"],
            "news_report": final_state["news_report"],
            "fundamentals_report": final_state["fundamentals_report"],
            "investment_debate_state": {
                "bull_history": final_state["investment_debate_state"]["bull_history"],
                "bear_history": final_state["investment_debate_state"]["bear_history"],
                "history": final_state["investment_debate_state"]["history"],
                "current_response": final_state["investment_debate_state"][
                    "current_response"
                ],
                "judge_decision": final_state["investment_debate_state"][
                    "judge_decision"
                ],
            },
            "trader_investment_decision": final_state["trader_investment_plan"],
            "risk_debate_state": {
                "risky_history": final_state["risk_debate_state"]["risky_history"],
                "safe_history": final_state["risk_debate_state"]["safe_history"],
                "neutral_history": final_state["risk_debate_state"]["neutral_history"],
                "history": final_state["risk_debate_state"]["history"],
                "judge_decision": final_state["risk_debate_state"]["judge_decision"],
            },
            "investment_plan": final_state["investment_plan"],
            "final_trade_decision": final_state["final_trade_decision"],
        }

        # Save to file
        directory = Path(f"eval_results/{self.ticker}/TradingAgentsStrategy_logs/")
        directory.mkdir(parents=True, exist_ok=True)

        with open(
            f"eval_results/{self.ticker}/TradingAgentsStrategy_logs/full_states_log_{trade_date}.json",
            "w",
        ) as f:
            json.dump(self.log_states_dict, f, indent=4)

    def reflect_and_remember(self, returns_losses):
        """Reflect on decisions and update memory based on returns."""
        self.reflector.reflect_bull_researcher(
            self.curr_state, returns_losses, self.bull_memory
        )
        self.reflector.reflect_bear_researcher(
            self.curr_state, returns_losses, self.bear_memory
        )
        self.reflector.reflect_trader(
            self.curr_state, returns_losses, self.trader_memory
        )
        self.reflector.reflect_invest_judge(
            self.curr_state, returns_losses, self.invest_judge_memory
        )
        self.reflector.reflect_risk_manager(
            self.curr_state, returns_losses, self.risk_manager_memory
        )

    def process_signal(self, full_signal):
        """Process a signal to extract the core decision."""
        return self.signal_processor.process_signal(full_signal)

    def _generate_historical_context(self, ticker_symbol: str) -> Optional[str]:
        """
        Generate historical context using RAG for the given ticker.

        Args:
            ticker_symbol: Stock ticker symbol

        Returns:
            Formatted historical context string or None
        """
        try:
            # Get ticker info from database
            ticker_info = self.ticker_ops.get_ticker(symbol=ticker_symbol)
            if not ticker_info:
                logger.warning(f"Ticker {ticker_symbol} not found in database")
                return None

            ticker_id = ticker_info['ticker_id']

            # Create embedding for current market situation
            # Note: In a full implementation, we would gather current market data here
            # For now, we'll create a simple context string
            current_situation_text = f"Analyzing {ticker_symbol} for potential investment opportunity"

            embedding = self.embedding_generator.generate(current_situation_text)
            if not embedding:
                logger.warning("Failed to generate embedding for current situation")
                return None

            # Build comprehensive historical context
            context = self.context_retriever.build_historical_context(
                ticker_id=ticker_id,
                current_situation_embedding=embedding,
                symbol=ticker_symbol
            )

            # Format context for LLM prompt
            formatted_context = self.prompt_formatter.format_analysis_context(
                context, include_section="all"
            )

            return formatted_context

        except Exception as e:
            logger.error(f"Error generating historical context: {e}")
            return None

    def _store_analysis(self, ticker_symbol: str, analysis_date: date, final_state: Dict[str, Any]):
        """
        Store analysis results to database with embeddings.

        Args:
            ticker_symbol: Stock ticker symbol
            analysis_date: Date of analysis
            final_state: Final state from graph execution
        """
        try:
            from tradingagents.database import AnalysisOperations

            # Get ticker info
            ticker_info = self.ticker_ops.get_ticker(symbol=ticker_symbol)
            if not ticker_info:
                logger.warning(f"Cannot store analysis: ticker {ticker_symbol} not found")
                return

            ticker_id = ticker_info['ticker_id']

            # Extract key information from final state
            analysis_data = {
                'ticker_id': ticker_id,
                'analysis_date': analysis_date,
                'executive_summary': self._extract_summary(final_state),
                'bull_case': final_state.get('investment_debate_state', {}).get('bull_history', ''),
                'bear_case': final_state.get('investment_debate_state', {}).get('bear_history', ''),
                'final_decision': self._extract_decision(final_state.get('final_trade_decision', '')),
                'confidence_score': self._extract_confidence(final_state),
                'key_catalysts': self._extract_catalysts(final_state),
                'risk_factors': self._extract_risks(final_state),
            }

            # Generate embedding for this analysis
            embedding = self.embedding_generator.embed_analysis(analysis_data)

            # Store to database
            analysis_ops = AnalysisOperations(self.db)
            analysis_id = analysis_ops.create_analysis(
                ticker_id=ticker_id,
                analysis_date=analysis_date,
                embedding=embedding,
                **{k: v for k, v in analysis_data.items() if k not in ['ticker_id', 'analysis_date']}
            )

            logger.info(f"✓ Stored analysis {analysis_id} for {ticker_symbol} to database")

        except Exception as e:
            logger.error(f"Error storing analysis to database: {e}")

    def _extract_summary(self, final_state: Dict[str, Any]) -> str:
        """Extract executive summary from final state."""
        # Combine key reports into a summary
        parts = []

        if final_state.get('market_report'):
            parts.append(f"Market: {final_state['market_report'][:200]}")

        if final_state.get('fundamentals_report'):
            parts.append(f"Fundamentals: {final_state['fundamentals_report'][:200]}")

        return " | ".join(parts) if parts else "Analysis completed"

    def _extract_decision(self, final_trade_decision: str) -> str:
        """Extract decision from final trade decision text."""
        # Parse the decision from the final output
        decision_upper = final_trade_decision.upper()

        if 'BUY' in decision_upper or 'LONG' in decision_upper:
            return 'BUY'
        elif 'SELL' in decision_upper or 'SHORT' in decision_upper:
            return 'SELL'
        elif 'HOLD' in decision_upper:
            return 'HOLD'
        else:
            return 'WAIT'

    def _extract_confidence(self, final_state: Dict[str, Any]) -> int:
        """Extract confidence score from final state."""
        # Default confidence based on consensus
        # In a full implementation, we would parse this from agent outputs
        return 75

    def _extract_catalysts(self, final_state: Dict[str, Any]) -> List[str]:
        """Extract key catalysts from analysis."""
        catalysts = []

        # Parse from reports
        if final_state.get('news_report'):
            # Simple extraction - in production, would use LLM to extract
            catalysts.append("News events analyzed")

        if final_state.get('fundamentals_report'):
            catalysts.append("Fundamental factors")

        return catalysts or ["General market analysis"]

    def _extract_risks(self, final_state: Dict[str, Any]) -> List[str]:
        """Extract risk factors from analysis."""
        risks = []

        # Extract from risk debate
        risk_state = final_state.get('risk_debate_state', {})
        if risk_state.get('risky_history'):
            risks.append("Risk factors identified in analysis")

        return risks or ["Standard market risks"]
