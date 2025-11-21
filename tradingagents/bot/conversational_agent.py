import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from tradingagents.bot.agent import TradingAgent
from tradingagents.bot.state_tracker import get_state_tracker
from tradingagents.cognitive import get_cognitive_controller, CognitiveMode
from tradingagents.default_config import DEFAULT_CONFIG
# We will import the RAG retriever here later when we implement it
# from tradingagents.rag.context_retriever import ContextRetriever 

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are Eddie, a world-class AI Trading Assistant. 
You are professional, insightful, and "human-like". You don't just spit out data; you explain it.
You have access to a team of specialized analysts (via the Trading Graph) and a vast knowledge base of trading concepts.

Your goal is to help the user make better investment decisions.
- If the user asks for a stock analysis, use your tools to analyze it.
- If the user asks a general question (e.g., "What is RSI?"), explain it clearly using your knowledge base.
- If the user chats casually, respond warmly but professionally.

Always be transparent about risks. You are an assistant, not a financial advisor.
"""

class ConversationalAgent:
    """
    Orchestrator agent that manages the conversation flow,
    routes requests to specific sub-agents (TradingGraph),
    and handles general knowledge queries.
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or DEFAULT_CONFIG
        self.debug = self.config.get("debug", False)
        
        # Initialize the core LLM for conversation
        self.llm = ChatOpenAI(
            model=self.config.get("quick_think_llm", "llama3.3"), # Use quick model for chat
            base_url=self.config.get("backend_url", "http://localhost:11434/v1"),
            api_key="ollama",
            temperature=0.7
        )

        # Initialize the heavy-lifting Trading Agent (ReAct)
        self.trading_agent = TradingAgent(
            model_name=self.config.get("deep_think_llm", "llama3.3"),
            base_url=self.config.get("backend_url", "http://localhost:11434/v1"),
            debug=self.debug
        )
        
        # TODO: Initialize General Knowledge RAG
        self.knowledge_retriever = None
        
        # Initialize cognitive controller (v2.0)
        self.cognitive_controller = get_cognitive_controller()
        self.state_tracker = get_state_tracker() 

    async def chat(
        self, 
        message: str, 
        history: List[Dict[str, str]], 
        user_preferences: Optional[Dict] = None,
        prompt_metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Process a user message and determine the best course of action.
        
        Args:
            message: User's message
            history: Conversation history
            user_preferences: Optional user preferences
            prompt_metadata: Optional prompt metadata (prompt_type, prompt_id) for optimizations
        """
        try:
            # Apply prompt-specific optimizations
            if prompt_metadata:
                prompt_type = prompt_metadata.get("prompt_type")
                prompt_id = prompt_metadata.get("prompt_id")
                
                # Optimize based on prompt type
                if prompt_type == "quick_wins":
                    # For quick wins, prioritize speed - use screener first, then quick analysis
                    logger.info(f"Quick wins prompt detected - optimizing for speed")
                    # Message likely already asks for top stocks, so intent will be ANALYSIS
                    # But we can add a hint to prioritize screener
                    if "top" in message.lower() or "best" in message.lower() or "buy" in message.lower():
                        message = f"[QUICK_WINS_MODE] {message}"
                
                elif prompt_type == "analysis":
                    # For analysis prompts, ensure full analysis is triggered
                    logger.info(f"Analysis prompt detected - ensuring comprehensive analysis")
                    # Ensure intent classification recognizes this as analysis
                    if "analyze" not in message.lower():
                        message = f"Analyze {message}"
                
                elif prompt_type == "risk":
                    # For risk prompts, prioritize risk management tools
                    logger.info(f"Risk management prompt detected - prioritizing risk assessment")
                    # Add risk-focused context
                    message = f"[RISK_FOCUS] {message}"
                
                elif prompt_type == "market":
                    # For market intelligence, prioritize news and sector analysis
                    logger.info(f"Market intelligence prompt detected - prioritizing market context")
                    message = f"[MARKET_INTELLIGENCE] {message}"
            
            # 0. Cognitive Mode Decision (v2.0)
            # Decide which mode Eddie should use based on context
            system_health = self.state_tracker.get_state().system_health
            mode_decision = self.cognitive_controller.decide_mode(
                user_message=message,
                market_conditions=None,  # Could fetch from database if needed
                system_health=system_health,
                user_emotional_state=None  # Could detect from voice/text analysis
            )
            
            logger.info(f"Cognitive mode: {mode_decision.mode.value} - {mode_decision.reasoning}")
            
            # 1. Intent Classification (Simple heuristic or LLM call)
            # For now, we'll use a simple heuristic, but in production, use an LLM router.
            intent = self._classify_intent(message)
            
            logger.info(f"Detected intent: {intent} for message: {message[:50]}...")

            if intent == "ANALYSIS":
                # Delegate to Trading Agent
                # We pass the user's message directly to the ReAct agent
                # The ReAct agent has tools to fetch data and analyze
                response = await self._run_trading_agent(message, history)
                return response
            
            elif intent == "KNOWLEDGE":
                # TODO: Query RAG
                # context = self.knowledge_retriever.query(message)
                context = "RSI (Relative Strength Index) is a momentum oscillator that measures the speed and change of price movements."
                return await self._generate_conversational_response(message, history, context)
            
            else: # CHAT / GENERAL
                return await self._generate_conversational_response(message, history)

        except Exception as e:
            logger.error(f"Error in ConversationalAgent: {e}", exc_info=True)
            return "I apologize, but I encountered an error processing your request. Please try again."

    def _classify_intent(self, message: str) -> str:
        """
        Classify the user's intent.
        """
        msg_lower = message.lower()
        
        # Analysis triggers
        analysis_keywords = ["analyze", "stock", "price", "buy", "sell", "forecast", "prediction", "chart", "ticker"]
        if any(keyword in msg_lower for keyword in analysis_keywords):
            # Check if it's a definition question though
            if "what is" in msg_lower and "price" not in msg_lower:
                 return "KNOWLEDGE"
            return "ANALYSIS"
            
        # Knowledge triggers
        knowledge_keywords = ["what is", "explain", "define", "how does", "mean"]
        if any(keyword in msg_lower for keyword in knowledge_keywords):
            return "KNOWLEDGE"
            
        return "CHAT"

    async def _run_trading_agent(self, message: str, history: List[Dict[str, str]]) -> str:
        """
        Run the TradingAgent (ReAct) and wrap the response.
        """
        # Convert history to LangChain format if needed, but TradingAgent.chat takes list
        # We'll just call the synchronous chat method for now, or wrap it if we want async
        # The TradingAgent.chat is synchronous but we are in an async method.
        # Ideally TradingAgent should have an async chat.
        
        # For now, we run it in a thread executor if it's blocking, 
        # but let's assume we can just call it.
        # Wait, TradingAgent has astream which is async.
        
        full_response = ""
        async for chunk in self.trading_agent.astream(message, conversation_history=self._format_history(history)):
             full_response += chunk
             
        return full_response

    async def _generate_conversational_response(self, message: str, history: List[Dict[str, str]], context: str = None) -> str:
        """
        Generate a conversational response using the LLM.
        """
        # Add cognitive mode prompt addition (v2.0)
        mode_prompt = self.cognitive_controller.get_mode_prompt_addition()
        system_prompt_with_mode = SYSTEM_PROMPT + "\n" + mode_prompt
        
        messages = [SystemMessage(content=system_prompt_with_mode)]
        
        # Add history
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        
        # Add context if available
        if context:
            messages.append(SystemMessage(content=f"Relevant Knowledge Context: {context}"))
            
        messages.append(HumanMessage(content=message))
        
        response = await self.llm.ainvoke(messages)
        return response.content

    def _format_history(self, history: List[Dict[str, str]]) -> List:
        """Convert dict history to LangChain messages."""
        formatted = []
        for msg in history:
             if msg["role"] == "user":
                formatted.append(HumanMessage(content=msg["content"]))
             elif msg["role"] == "assistant":
                formatted.append(AIMessage(content=msg["content"]))
        return formatted
