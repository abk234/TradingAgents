"""
Summarization middleware for TradingAgents.

Automatically summarizes context when it exceeds token limits to reduce costs.
"""

from typing import Dict, Any, List, Optional
from langchain_core.tools import BaseTool
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from .base import TradingMiddleware
from .token_tracker import TokenTracker
import logging

logger = logging.getLogger(__name__)


class SummarizationMiddleware(TradingMiddleware):
    """
    Middleware for automatic context summarization.
    
    Summarizes agent outputs when they exceed token thresholds to reduce
    costs while preserving key information.
    """
    
    def __init__(
        self,
        token_threshold: int = 50000,
        summarization_model: str = "gpt-4o-mini",
        llm_provider: str = "openai",
        preserve_key_info: bool = True,
        summarize_analyst_reports: bool = True,
        summarize_debates: bool = True
    ):
        """
        Initialize summarization middleware.
        
        Args:
            token_threshold: Summarize if state exceeds this many tokens
            summarization_model: Model to use for summarization (should be fast/cheap)
            llm_provider: LLM provider ("openai", "anthropic", "google", "ollama")
            preserve_key_info: Whether to preserve key data points in summaries
            summarize_analyst_reports: Whether to summarize analyst team outputs
            summarize_debates: Whether to summarize debate histories
        """
        self.token_threshold = token_threshold
        self.summarization_model = summarization_model
        self.llm_provider = llm_provider.lower()
        self.preserve_key_info = preserve_key_info
        self.summarize_analyst_reports = summarize_analyst_reports
        self.summarize_debates = summarize_debates
        
        # Initialize LLM for summarization
        self.llm = self._create_llm()
        self.tracker = TokenTracker(model="gpt-4o")  # For counting tokens
        
        logger.info(
            f"Initialized SummarizationMiddleware "
            f"(threshold: {token_threshold}, model: {summarization_model})"
        )
    
    def _create_llm(self):
        """Create LLM instance for summarization."""
        if self.llm_provider == "openai":
            return ChatOpenAI(model=self.summarization_model, temperature=0)
        elif self.llm_provider == "anthropic":
            return ChatAnthropic(model=self.summarization_model, temperature=0)
        elif self.llm_provider == "google":
            return ChatGoogleGenerativeAI(model=self.summarization_model, temperature=0)
        elif self.llm_provider == "ollama":
            return ChatOpenAI(
                model=self.summarization_model,
                base_url="http://localhost:11434/v1",
                api_key="ollama",
                temperature=0
            )
        else:
            logger.warning(f"Unknown LLM provider: {self.llm_provider}. Using OpenAI.")
            return ChatOpenAI(model=self.summarization_model, temperature=0)
    
    @property
    def tools(self) -> List[BaseTool]:
        """No tools provided by this middleware."""
        return []
    
    def modify_prompt(self, prompt: str, agent_type: str) -> str:
        """No prompt modification needed."""
        return prompt
    
    def pre_process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """No pre-processing needed."""
        return state
    
    def summarize_analyst_reports(self, state: Dict[str, Any]) -> str:
        """
        Summarize all analyst reports into concise format.
        
        Args:
            state: Current agent state
        
        Returns:
            Summarized analyst reports
        """
        reports = []
        
        if state.get("market_report"):
            market = state["market_report"]
            reports.append(f"**Market Analysis:**\n{market[:800]}...")
        
        if state.get("sentiment_report"):
            sentiment = state["sentiment_report"]
            reports.append(f"**Sentiment Analysis:**\n{sentiment[:800]}...")
        
        if state.get("news_report"):
            news = state["news_report"]
            reports.append(f"**News Analysis:**\n{news[:800]}...")
        
        if state.get("fundamentals_report"):
            fundamentals = state["fundamentals_report"]
            reports.append(f"**Fundamentals Analysis:**\n{fundamentals[:800]}...")
        
        if not reports:
            return ""
        
        summary_prompt = f"""Summarize the following analyst reports into a concise format, preserving:
1. Key findings and signals (buy/sell/hold indicators)
2. Critical data points (numbers, percentages, price levels)
3. Risk factors and concerns
4. Recommendations and action items

Preserve all numerical data and specific recommendations. Be concise but comprehensive.

Analyst Reports:
{chr(10).join(reports)}

Provide a structured summary (max 1000 tokens) with clear sections for each analyst type."""

        try:
            messages = [
                SystemMessage(content="You are a financial analysis summarizer. Preserve all key data points and recommendations."),
                HumanMessage(content=summary_prompt)
            ]
            
            response = self.llm.invoke(messages)
            summary = response.content if hasattr(response, 'content') else str(response)
            
            logger.info(f"Summarized analyst reports: {len(summary)} chars")
            return summary
        except Exception as e:
            logger.error(f"Error summarizing analyst reports: {e}")
            # Return concatenated reports if summarization fails
            return "\n\n".join(reports)
    
    def summarize_debate(self, debate_state: Dict[str, Any]) -> str:
        """
        Summarize debate history.
        
        Args:
            debate_state: Debate state dictionary
        
        Returns:
            Summarized debate
        """
        if isinstance(debate_state, dict):
            history = debate_state.get("history", "")
            bull_history = debate_state.get("bull_history", "")
            bear_history = debate_state.get("bear_history", "")
        else:
            history = str(debate_state)
            bull_history = ""
            bear_history = ""
        
        if not history and not bull_history and not bear_history:
            return ""
        
        # Combine all debate history
        full_history = ""
        if bull_history:
            full_history += f"**Bullish Arguments:**\n{bull_history[:2000]}\n\n"
        if bear_history:
            full_history += f"**Bearish Arguments:**\n{bear_history[:2000]}\n\n"
        if history:
            full_history += f"**Debate History:**\n{history[:2000]}"
        
        if len(full_history) < 500:
            return full_history  # Already short enough
        
        summary_prompt = f"""Summarize this investment debate, preserving:
1. Key arguments from both sides (bullish and bearish)
2. Critical concerns raised
3. Consensus points
4. Final recommendation and reasoning

Debate History:
{full_history[:5000]}  # Limit input to avoid token limits

Provide concise summary (max 800 tokens) with clear structure."""

        try:
            messages = [
                SystemMessage(content="You are a debate summarizer. Preserve key arguments and final recommendations."),
                HumanMessage(content=summary_prompt)
            ]
            
            response = self.llm.invoke(messages)
            summary = response.content if hasattr(response, 'content') else str(response)
            
            logger.info(f"Summarized debate: {len(summary)} chars")
            return summary
        except Exception as e:
            logger.error(f"Error summarizing debate: {e}")
            return full_history[:2000]  # Return truncated version
    
    def post_process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Summarize state if it exceeds token threshold.
        
        Args:
            state: Current agent state
        
        Returns:
            State with summaries added (and optionally original reports cleared)
        """
        # Check total token count
        total_tokens = self.tracker.count_state_tokens(
            state,
            exclude_keys=["_token_count", "_total_tokens", "_token_summary", "_summarized"]
        )
        
        modified_state = state.copy()
        
        # Summarize analyst reports if needed
        if self.summarize_analyst_reports and not state.get("_analyst_summarized"):
            if all([
                state.get("market_report"),
                state.get("sentiment_report"),
                state.get("news_report"),
                state.get("fundamentals_report")
            ]):
                # Check if analyst reports are large
                analyst_tokens = sum([
                    self.tracker.count_tokens(state.get("market_report", "")),
                    self.tracker.count_tokens(state.get("sentiment_report", "")),
                    self.tracker.count_tokens(state.get("news_report", "")),
                    self.tracker.count_tokens(state.get("fundamentals_report", ""))
                ])
                
                if analyst_tokens > 10000:  # Summarize if > 10k tokens
                    logger.info(f"Summarizing analyst reports ({analyst_tokens} tokens)")
                    summary = self.summarize_analyst_reports(state)
                    modified_state["analyst_summary"] = summary
                    modified_state["_analyst_summarized"] = True
                    # Keep original reports but mark as summarized
                    modified_state["_original_reports_summarized"] = True
        
        # Summarize research debate if needed
        if self.summarize_debates and not state.get("_research_summarized"):
            debate_state = state.get("investment_debate_state", {})
            if debate_state:
                debate_tokens = self.tracker.count_state_tokens(debate_state)
                if debate_tokens > 5000:  # Summarize if > 5k tokens
                    logger.info(f"Summarizing research debate ({debate_tokens} tokens)")
                    summary = self.summarize_debate(debate_state)
                    modified_state["debate_summary"] = summary
                    modified_state["_research_summarized"] = True
        
        # Summarize risk debate if needed
        if self.summarize_debates and not state.get("_risk_summarized"):
            risk_state = state.get("risk_debate_state", {})
            if risk_state:
                risk_tokens = self.tracker.count_state_tokens(risk_state)
                if risk_tokens > 5000:  # Summarize if > 5k tokens
                    logger.info(f"Summarizing risk debate ({risk_tokens} tokens)")
                    summary = self.summarize_debate(risk_state)
                    modified_state["risk_summary"] = summary
                    modified_state["_risk_summarized"] = True
        
        # Mark as processed
        modified_state["_summarized"] = True
        
        return modified_state

