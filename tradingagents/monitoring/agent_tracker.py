"""
Agent Execution Tracker

Tracks individual agent executions in real-time during analysis runs.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from contextlib import contextmanager
import logging
import time

from tradingagents.database import get_db_connection

logger = logging.getLogger(__name__)


class AgentExecutionTracker:
    """
    Tracks individual agent executions for capability monitoring.
    
    Usage:
        tracker = AgentExecutionTracker(analysis_id=123)
        with tracker.track_agent('market_analyst', 'analyst'):
            # Agent execution code here
            pass
    """

    def __init__(self, analysis_id: Optional[int] = None):
        """
        Initialize agent execution tracker.
        
        Args:
            analysis_id: Optional analysis ID this execution belongs to
        """
        self.analysis_id = analysis_id
        self.db = get_db_connection()
        self._current_execution_id = None

    @contextmanager
    def track_agent(
        self,
        agent_name: str,
        agent_team: str,
        llm_model: Optional[str] = None,
        llm_temperature: Optional[float] = None,
        agent_metrics: Optional[Dict[str, Any]] = None
    ):
        """
        Context manager to track an agent execution.
        
        Args:
            agent_name: Name of the agent (e.g., 'market_analyst')
            agent_team: Team the agent belongs to ('analyst', 'research', etc.)
            llm_model: LLM model used (if applicable)
            llm_temperature: LLM temperature setting (if applicable)
            agent_metrics: Additional agent-specific metrics (dict)
        
        Yields:
            execution_id: ID of the tracked execution
        """
        execution_start = datetime.now()
        execution_id = None
        error_occurred = False
        error_message = None
        
        try:
            # Insert execution record
            execution_id = self._create_execution_record(
                agent_name=agent_name,
                agent_team=agent_team,
                execution_start=execution_start,
                llm_model=llm_model,
                llm_temperature=llm_temperature,
                agent_metrics=agent_metrics
            )
            
            self._current_execution_id = execution_id
            logger.debug(f"Started tracking agent: {agent_name} (execution_id={execution_id})")
            
            # Yield control to agent execution
            yield execution_id
            
        except Exception as e:
            error_occurred = True
            error_message = str(e)
            logger.error(f"Error during agent execution tracking: {e}", exc_info=True)
            raise
        
        finally:
            # Update execution record with completion data
            if execution_id:
                execution_end = datetime.now()
                duration = (execution_end - execution_start).total_seconds()
                
                self._update_execution_record(
                    execution_id=execution_id,
                    execution_end=execution_end,
                    duration=duration,
                    has_errors=error_occurred,
                    error_message=error_message
                )
                
                logger.debug(
                    f"Completed tracking agent: {agent_name} "
                    f"(duration={duration:.2f}s, errors={error_occurred})"
                )

    def _create_execution_record(
        self,
        agent_name: str,
        agent_team: str,
        execution_start: datetime,
        llm_model: Optional[str] = None,
        llm_temperature: Optional[float] = None,
        agent_metrics: Optional[Dict[str, Any]] = None
    ) -> int:
        """Create a new execution record."""
        import json
        
        data = {
            'analysis_id': self.analysis_id,
            'agent_name': agent_name,
            'agent_team': agent_team,
            'execution_start_time': execution_start,
            'llm_model': llm_model,
            'llm_temperature': llm_model and llm_temperature,  # Only if LLM used
            'agent_metrics': json.dumps(agent_metrics) if agent_metrics else None
        }
        
        execution_id = self.db.insert('agent_executions', data, returning='execution_id')
        return execution_id

    def _update_execution_record(
        self,
        execution_id: int,
        execution_end: datetime,
        duration: float,
        has_errors: bool,
        error_message: Optional[str] = None,
        output_length: Optional[int] = None,
        output_quality_score: Optional[int] = None,
        llm_tokens_used: Optional[int] = None,
        llm_cost_usd: Optional[float] = None,
        contribution_score: Optional[int] = None,
        was_cited_in_final_report: Optional[bool] = None
    ):
        """Update execution record with completion data."""
        update_data = {
            'execution_end_time': execution_end,
            'duration_seconds': duration,
            'has_errors': has_errors,
            'error_message': error_message,
            'output_length': output_length,
            'output_quality_score': output_quality_score,
            'llm_tokens_used': llm_tokens_used,
            'llm_cost_usd': llm_cost_usd,
            'contribution_score': contribution_score,
            'was_cited_in_final_report': was_cited_in_final_report
        }
        
        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        if update_data:
            self.db.update(
                'agent_executions',
                update_data,
                where={'execution_id': execution_id}
            )

    def update_output_metrics(
        self,
        execution_id: int,
        output_text: str,
        quality_score: Optional[int] = None
    ):
        """
        Update execution record with output metrics.
        
        Args:
            execution_id: Execution ID to update
            output_text: Agent output text
            quality_score: Optional quality score (0-100)
        """
        output_length = len(output_text) if output_text else 0
        
        # Calculate quality score if not provided
        if quality_score is None:
            quality_score = self._calculate_quality_score(output_text)
        
        self._update_execution_record(
            execution_id=execution_id,
            output_length=output_length,
            output_quality_score=quality_score
        )

    def update_llm_metrics(
        self,
        execution_id: int,
        tokens_used: int,
        cost_usd: float
    ):
        """
        Update execution record with LLM usage metrics.
        
        Args:
            execution_id: Execution ID to update
            tokens_used: Number of tokens used
            cost_usd: Cost in USD
        """
        self._update_execution_record(
            execution_id=execution_id,
            llm_tokens_used=tokens_used,
            llm_cost_usd=cost_usd
        )

    def update_contribution(
        self,
        execution_id: int,
        contribution_score: int,
        was_cited: bool = False
    ):
        """
        Update execution record with contribution metrics.
        
        Args:
            execution_id: Execution ID to update
            contribution_score: Contribution score (0-100)
            was_cited: Whether agent output was cited in final report
        """
        self._update_execution_record(
            execution_id=execution_id,
            contribution_score=contribution_score,
            was_cited_in_final_report=was_cited
        )

    def _calculate_quality_score(self, output_text: str) -> int:
        """
        Calculate quality score based on output characteristics.
        
        Args:
            output_text: Agent output text
        
        Returns:
            Quality score (0-100)
        """
        if not output_text or len(output_text.strip()) == 0:
            return 0
        
        score = 50  # Base score
        
        # Length bonus (up to 20 points)
        length_score = min(len(output_text) / 100, 1.0) * 20
        score += length_score
        
        # Structure bonus (up to 15 points)
        has_structure = any(keyword in output_text.lower() for keyword in [
            'summary', 'analysis', 'conclusion', 'recommendation', 'risk', 'opportunity'
        ])
        if has_structure:
            score += 15
        
        # Data presence bonus (up to 15 points)
        has_data = any(keyword in output_text.lower() for keyword in [
            'price', 'volume', 'ratio', 'percent', '%', '$', 'earnings', 'revenue'
        ])
        if has_data:
            score += 15
        
        return min(int(score), 100)

