"""
Strategy Adapter

Adapts the existing TradingAgents system to the InvestmentStrategy interface.
This allows the existing system to participate in strategy comparisons.
"""

from typing import Dict, Any, Optional
import logging

from tradingagents.strategies.base import InvestmentStrategy, StrategyResult, Recommendation
from tradingagents.graph.trading_graph import TradingAgentsGraph

logger = logging.getLogger(__name__)


class HybridStrategyAdapter(InvestmentStrategy):
    """
    Adapts existing TradingAgents system to InvestmentStrategy interface.
    
    This wraps the existing Four-Gate Framework + Multi-Agent system
    as a strategy that can be compared with other strategies.
    """
    
    def __init__(
        self,
        graph: Optional[TradingAgentsGraph] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize adapter with TradingAgents graph.
        
        Args:
            graph: TradingAgentsGraph instance (creates new if None)
            config: Configuration dictionary (optional)
        """
        if graph is None:
            from tradingagents.default_config import DEFAULT_CONFIG
            from tradingagents.graph.trading_graph import TradingAgentsGraph
            
            final_config = config or DEFAULT_CONFIG
            self.graph = TradingAgentsGraph(
                selected_analysts=["market", "social", "news", "fundamentals"],
                debug=False,
                config=final_config,
                enable_rag=True,
            )
        else:
            self.graph = graph
        
        logger.info("Initialized HybridStrategyAdapter with existing TradingAgents system")
    
    def get_strategy_name(self) -> str:
        return "Hybrid (Four-Gate + Multi-Agent)"
    
    def get_timeframe(self) -> str:
        return "30-90 days"
    
    def evaluate(
        self,
        ticker: str,
        market_data: Dict[str, Any],
        fundamental_data: Dict[str, Any],
        technical_data: Dict[str, Any],
        additional_data: Optional[Dict[str, Any]] = None
    ) -> StrategyResult:
        """
        Evaluate stock using existing TradingAgents system.
        
        Note: This runs the full multi-agent analysis, which may take time.
        For faster comparisons, consider using individual strategies instead.
        """
        # Extract analysis date from additional_data or use today
        analysis_date = additional_data.get("analysis_date") if additional_data else None
        if analysis_date is None:
            from datetime import date
            analysis_date = date.today().strftime("%Y-%m-%d")
        
        try:
            # Run existing system
            logger.info(f"Running existing TradingAgents system for {ticker}")
            final_state, processed_signal = self.graph.propagate(
                company_name=ticker,
                trade_date=analysis_date,
                store_analysis=False  # Don't store during comparison
            )
            
            # Extract decision
            decision_str = processed_signal.strip().upper()
            
            # Map to Recommendation enum
            if "BUY" in decision_str:
                recommendation = Recommendation.BUY
            elif "SELL" in decision_str:
                recommendation = Recommendation.SELL
            elif "HOLD" in decision_str:
                recommendation = Recommendation.HOLD
            else:
                recommendation = Recommendation.WAIT
            
            # Extract confidence score
            confidence = final_state.get("confidence_score", 50)
            if not isinstance(confidence, int):
                try:
                    confidence = int(float(confidence))
                except (ValueError, TypeError):
                    confidence = 50
            
            # Extract reasoning from final decision
            final_decision_text = final_state.get("final_trade_decision", "")
            reasoning = self._extract_reasoning(final_state, final_decision_text)
            
            # Extract key metrics
            key_metrics = self._extract_key_metrics(final_state, market_data, fundamental_data, technical_data)
            
            # Extract risks
            risks = self._extract_risks(final_state)
            
            # Extract price targets
            entry_price, target_price, stop_loss = self._extract_price_targets(
                final_state, market_data
            )
            
            return StrategyResult(
                recommendation=recommendation,
                confidence=confidence,
                reasoning=reasoning,
                entry_price=entry_price,
                target_price=target_price,
                stop_loss=stop_loss,
                holding_period="30-90 days",
                key_metrics=key_metrics,
                risks=risks,
                strategy_name=self.get_strategy_name()
            )
        
        except Exception as e:
            logger.error(f"Error running existing system for {ticker}: {e}")
            return StrategyResult(
                recommendation=Recommendation.WAIT,
                confidence=0,
                reasoning=f"Error running analysis: {str(e)}",
                strategy_name=self.get_strategy_name()
            )
    
    def _extract_reasoning(
        self,
        final_state: Dict[str, Any],
        final_decision_text: str
    ) -> str:
        """Extract reasoning from final state."""
        reasons = []
        
        # Add final decision text
        if final_decision_text:
            reasons.append(final_decision_text[:500])  # Limit length
        
        # Add gate results if available
        profitability_enhancements = final_state.get("profitability_enhancements", {})
        if profitability_enhancements:
            gates = profitability_enhancements.get("gate_results", {})
            if gates:
                gate_summary = []
                for gate_name, gate_result in gates.items():
                    if isinstance(gate_result, dict):
                        passed = gate_result.get("passed", False)
                        score = gate_result.get("score", 0)
                        gate_summary.append(f"{gate_name}: {'✓' if passed else '✗'} ({score}/100)")
                
                if gate_summary:
                    reasons.append("Gate results: " + " | ".join(gate_summary))
        
        return " | ".join(reasons) if reasons else "Multi-agent analysis completed"
    
    def _extract_key_metrics(
        self,
        final_state: Dict[str, Any],
        market_data: Dict[str, Any],
        fundamental_data: Dict[str, Any],
        technical_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract key metrics from final state and data."""
        metrics = {}
        
        # Extract from profitability enhancements
        profitability_enhancements = final_state.get("profitability_enhancements", {})
        if profitability_enhancements:
            # Gate scores
            gates = profitability_enhancements.get("gate_results", {})
            if gates:
                metrics["gate_scores"] = {
                    name: result.get("score", 0) if isinstance(result, dict) else 0
                    for name, result in gates.items()
                }
            
            # Position sizing
            position_info = profitability_enhancements.get("position_sizing", {})
            if position_info:
                metrics["position_size_pct"] = position_info.get("position_size_pct")
                metrics["position_value"] = position_info.get("position_value")
        
        # Extract from data
        from tradingagents.strategies.utils import extract_metric
        
        metrics["current_price"] = extract_metric(market_data, "current_price")
        metrics["pe_ratio"] = extract_metric(fundamental_data, "pe_ratio") or extract_metric(fundamental_data, "Trailing P/E")
        metrics["rsi"] = extract_metric(technical_data, "rsi") or extract_metric(technical_data, "RSI")
        
        return metrics
    
    def _extract_risks(self, final_state: Dict[str, Any]) -> list:
        """Extract risks from final state."""
        risks = []
        
        # Check gate results for failures
        profitability_enhancements = final_state.get("profitability_enhancements", {})
        if profitability_enhancements:
            gates = profitability_enhancements.get("gate_results", {})
            if gates:
                for gate_name, gate_result in gates.items():
                    if isinstance(gate_result, dict):
                        passed = gate_result.get("passed", False)
                        if not passed:
                            risks.append(f"{gate_name} gate failed")
        
        return risks
    
    def _extract_price_targets(
        self,
        final_state: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> tuple:
        """Extract entry price, target price, and stop loss."""
        from tradingagents.strategies.utils import extract_metric
        
        entry_price = extract_metric(market_data, "current_price")
        
        # Try to extract from profitability enhancements
        profitability_enhancements = final_state.get("profitability_enhancements", {})
        target_price = None
        stop_loss = None
        
        if profitability_enhancements:
            exit_strategy = profitability_enhancements.get("exit_strategy", {})
            if exit_strategy:
                stop_loss = exit_strategy.get("trailing_stop")
            
            # Try to find target price in investment plan
            investment_plan = final_state.get("investment_plan", "")
            if investment_plan and entry_price:
                # Simple extraction - look for price mentions
                # In full implementation, would parse more carefully
                pass
        
        return entry_price, target_price, stop_loss

