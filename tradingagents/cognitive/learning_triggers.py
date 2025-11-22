# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Event-Driven Learning Triggers for Eddie v2.0
Phase 2.4: Advanced Autonomous Learning

Automatically triggers learning based on market events and patterns.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable, Any
from enum import Enum
import logging
import asyncio
from collections import defaultdict

logger = logging.getLogger(__name__)


class TriggerType(Enum):
    """Types of learning triggers"""
    PRICE_MOVEMENT = "price_movement"
    EARNINGS_EVENT = "earnings_event"
    NEWS_ALERT = "news_alert"
    SECTOR_ROTATION = "sector_rotation"
    PATTERN_DETECTED = "pattern_detected"
    SCHEDULED = "scheduled"
    MANUAL = "manual"


class TriggerPriority(Enum):
    """Priority levels for triggers"""
    CRITICAL = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1


class TriggerStatus(Enum):
    """Status of trigger execution"""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class TriggerCondition:
    """Condition for triggering learning"""
    condition_type: str
    parameters: Dict[str, Any]
    evaluator: Optional[Callable] = None
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """
        Evaluate if condition is met.
        
        Args:
            context: Context data for evaluation
        
        Returns:
            True if condition is met
        """
        if self.evaluator:
            return self.evaluator(context, self.parameters)
        return True


@dataclass
class LearningAction:
    """Action to take when trigger fires"""
    action_type: str
    parameters: Dict[str, Any]
    executor: Optional[Callable] = None
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the learning action.
        
        Args:
            context: Context data for execution
        
        Returns:
            Execution result
        """
        if self.executor:
            return await self.executor(context, self.parameters)
        return {"status": "no_executor"}


@dataclass
class Trigger:
    """A learning trigger definition"""
    id: str
    name: str
    trigger_type: TriggerType
    priority: TriggerPriority
    condition: TriggerCondition
    action: LearningAction
    enabled: bool = True
    cooldown_seconds: int = 3600  # 1 hour default cooldown
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    
    def can_trigger(self) -> bool:
        """Check if trigger can fire (cooldown check)"""
        if not self.enabled:
            return False
        
        if self.last_triggered is None:
            return True
        
        elapsed = (datetime.now() - self.last_triggered).total_seconds()
        return elapsed >= self.cooldown_seconds
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.trigger_type.value,
            "priority": self.priority.value,
            "enabled": self.enabled,
            "cooldown_seconds": self.cooldown_seconds,
            "last_triggered": self.last_triggered.isoformat() if self.last_triggered else None,
            "trigger_count": self.trigger_count
        }


@dataclass
class TriggerExecution:
    """Record of a trigger execution"""
    trigger_id: str
    trigger_name: str
    triggered_at: datetime
    status: TriggerStatus
    context: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_seconds: float = 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "trigger_id": self.trigger_id,
            "trigger_name": self.trigger_name,
            "triggered_at": self.triggered_at.isoformat(),
            "status": self.status.value,
            "context": self.context,
            "result": self.result,
            "error_message": self.error_message,
            "execution_time_seconds": self.execution_time_seconds
        }


class EventTriggerManager:
    """
    Manages event-driven learning triggers.
    
    Features:
    - Register custom triggers
    - Check market events
    - Execute triggered learning
    - Priority-based execution
    - Cooldown management
    """
    
    def __init__(self):
        """Initialize trigger manager"""
        self.triggers: Dict[str, Trigger] = {}
        self.execution_history: List[TriggerExecution] = []
        self.running = False
        self._check_interval = 300  # 5 minutes
        logger.info("EventTriggerManager initialized")
        
        # Register default triggers
        self._register_default_triggers()
    
    def register_trigger(
        self,
        trigger_id: str,
        name: str,
        trigger_type: TriggerType,
        priority: TriggerPriority,
        condition: TriggerCondition,
        action: LearningAction,
        cooldown_seconds: int = 3600
    ) -> Trigger:
        """
        Register a new learning trigger.
        
        Args:
            trigger_id: Unique trigger ID
            name: Human-readable name
            trigger_type: Type of trigger
            priority: Priority level
            condition: Condition to evaluate
            action: Action to execute
            cooldown_seconds: Cooldown between triggers
        
        Returns:
            Registered Trigger
        """
        trigger = Trigger(
            id=trigger_id,
            name=name,
            trigger_type=trigger_type,
            priority=priority,
            condition=condition,
            action=action,
            cooldown_seconds=cooldown_seconds
        )
        
        self.triggers[trigger_id] = trigger
        logger.info(f"Registered trigger: {name} ({trigger_id})")
        
        return trigger
    
    def unregister_trigger(self, trigger_id: str) -> bool:
        """
        Unregister a trigger.
        
        Args:
            trigger_id: Trigger ID to remove
        
        Returns:
            True if removed
        """
        if trigger_id in self.triggers:
            del self.triggers[trigger_id]
            logger.info(f"Unregistered trigger: {trigger_id}")
            return True
        return False
    
    def enable_trigger(self, trigger_id: str) -> bool:
        """Enable a trigger"""
        if trigger_id in self.triggers:
            self.triggers[trigger_id].enabled = True
            logger.info(f"Enabled trigger: {trigger_id}")
            return True
        return False
    
    def disable_trigger(self, trigger_id: str) -> bool:
        """Disable a trigger"""
        if trigger_id in self.triggers:
            self.triggers[trigger_id].enabled = False
            logger.info(f"Disabled trigger: {trigger_id}")
            return True
        return False
    
    async def check_triggers(self, context: Dict[str, Any]) -> List[Trigger]:
        """
        Check all triggers and return those that should fire.
        
        Args:
            context: Context data for evaluation
        
        Returns:
            List of triggers that should fire
        """
        triggered = []
        
        for trigger in self.triggers.values():
            if not trigger.can_trigger():
                continue
            
            try:
                if trigger.condition.evaluate(context):
                    triggered.append(trigger)
                    logger.info(f"Trigger fired: {trigger.name}")
            except Exception as e:
                logger.error(f"Error evaluating trigger {trigger.name}: {e}")
        
        # Sort by priority
        triggered.sort(key=lambda t: t.priority.value, reverse=True)
        
        return triggered
    
    async def execute_trigger(
        self,
        trigger: Trigger,
        context: Dict[str, Any]
    ) -> TriggerExecution:
        """
        Execute a single trigger.
        
        Args:
            trigger: Trigger to execute
            context: Context data
        
        Returns:
            TriggerExecution record
        """
        execution = TriggerExecution(
            trigger_id=trigger.id,
            trigger_name=trigger.name,
            triggered_at=datetime.now(),
            status=TriggerStatus.EXECUTING,
            context=context
        )
        
        start_time = datetime.now()
        
        try:
            logger.info(f"Executing trigger: {trigger.name}")
            
            # Execute action
            result = await trigger.action.execute(context)
            
            # Update execution
            execution.status = TriggerStatus.COMPLETED
            execution.result = result
            execution.execution_time_seconds = (datetime.now() - start_time).total_seconds()
            
            # Update trigger
            trigger.last_triggered = datetime.now()
            trigger.trigger_count += 1
            
            logger.info(f"Trigger completed: {trigger.name} (took {execution.execution_time_seconds:.2f}s)")
            
        except Exception as e:
            logger.error(f"Trigger execution failed: {trigger.name} - {e}")
            execution.status = TriggerStatus.FAILED
            execution.error_message = str(e)
            execution.execution_time_seconds = (datetime.now() - start_time).total_seconds()
        
        # Store execution history
        self.execution_history.append(execution)
        
        return execution
    
    async def execute_triggered_learning(
        self,
        context: Dict[str, Any],
        max_concurrent: int = 3
    ) -> List[TriggerExecution]:
        """
        Check and execute all triggered learning actions.
        
        Args:
            context: Context data for evaluation
            max_concurrent: Maximum concurrent executions
        
        Returns:
            List of TriggerExecution records
        """
        # Check triggers
        triggered = await self.check_triggers(context)
        
        if not triggered:
            logger.debug("No triggers fired")
            return []
        
        logger.info(f"{len(triggered)} trigger(s) fired")
        
        # Execute triggers (limit concurrent executions)
        executions = []
        for i in range(0, len(triggered), max_concurrent):
            batch = triggered[i:i+max_concurrent]
            tasks = [self.execute_trigger(t, context) for t in batch]
            batch_results = await asyncio.gather(*tasks)
            executions.extend(batch_results)
        
        return executions
    
    def check_price_movements(self, ticker_data: Dict[str, Dict]) -> List[Dict]:
        """
        Check for significant price movements.
        
        Args:
            ticker_data: Dict of ticker -> {price, prev_price, change_percent}
        
        Returns:
            List of price movement events
        """
        events = []
        
        for ticker, data in ticker_data.items():
            change_percent = abs(data.get('change_percent', 0))
            
            if change_percent >= 5.0:
                events.append({
                    "ticker": ticker,
                    "event_type": "price_spike",
                    "change_percent": change_percent,
                    "price": data.get('price'),
                    "prev_price": data.get('prev_price'),
                    "direction": "up" if data.get('change_percent', 0) > 0 else "down"
                })
                logger.info(f"Price movement detected: {ticker} {change_percent:+.2f}%")
        
        return events
    
    def check_earnings_calendar(
        self,
        ticker_earnings: Dict[str, datetime]
    ) -> List[Dict]:
        """
        Check for upcoming earnings.
        
        Args:
            ticker_earnings: Dict of ticker -> earnings_date
        
        Returns:
            List of earnings events
        """
        events = []
        now = datetime.now()
        
        for ticker, earnings_date in ticker_earnings.items():
            days_until = (earnings_date - now).days
            
            if 0 <= days_until <= 7:
                events.append({
                    "ticker": ticker,
                    "event_type": "earnings_upcoming",
                    "earnings_date": earnings_date,
                    "days_until": days_until
                })
                logger.info(f"Upcoming earnings: {ticker} in {days_until} days")
        
        return events
    
    def check_news_alerts(self, news_items: List[Dict]) -> List[Dict]:
        """
        Check for major news alerts.
        
        Args:
            news_items: List of news items with ticker, headline, sentiment
        
        Returns:
            List of news alert events
        """
        events = []
        
        # Keywords that indicate major news
        major_keywords = [
            'earnings', 'acquisition', 'merger', 'fda approval', 'bankruptcy',
            'lawsuit', 'ceo', 'guidance', 'recall', 'investigation'
        ]
        
        for item in news_items:
            headline = item.get('headline', '').lower()
            
            if any(keyword in headline for keyword in major_keywords):
                events.append({
                    "ticker": item.get('ticker'),
                    "event_type": "major_news",
                    "headline": item.get('headline'),
                    "sentiment": item.get('sentiment'),
                    "timestamp": item.get('timestamp')
                })
                logger.info(f"Major news detected: {item.get('ticker')} - {item.get('headline')[:50]}")
        
        return events
    
    def check_sector_rotation(
        self,
        sector_strengths: Dict[str, float],
        prev_sector_strengths: Dict[str, float]
    ) -> List[Dict]:
        """
        Check for sector rotation signals.
        
        Args:
            sector_strengths: Current sector strength scores
            prev_sector_strengths: Previous sector strength scores
        
        Returns:
            List of sector rotation events
        """
        events = []
        
        for sector, strength in sector_strengths.items():
            prev_strength = prev_sector_strengths.get(sector, strength)
            change = strength - prev_strength
            
            # Significant sector strength change (>10 points)
            if abs(change) >= 10.0:
                events.append({
                    "sector": sector,
                    "event_type": "sector_rotation",
                    "strength": strength,
                    "prev_strength": prev_strength,
                    "change": change,
                    "direction": "strengthening" if change > 0 else "weakening"
                })
                logger.info(f"Sector rotation detected: {sector} {change:+.1f} points")
        
        return events
    
    def get_execution_history(
        self,
        limit: Optional[int] = None,
        trigger_type: Optional[TriggerType] = None,
        status: Optional[TriggerStatus] = None
    ) -> List[TriggerExecution]:
        """
        Get execution history with optional filters.
        
        Args:
            limit: Maximum number of records
            trigger_type: Filter by trigger type
            status: Filter by execution status
        
        Returns:
            List of TriggerExecution records
        """
        history = self.execution_history.copy()
        
        # Apply filters
        if trigger_type:
            history = [
                e for e in history
                if self.triggers.get(e.trigger_id, {}).trigger_type == trigger_type
            ]
        
        if status:
            history = [e for e in history if e.status == status]
        
        # Sort by time (most recent first)
        history.sort(key=lambda e: e.triggered_at, reverse=True)
        
        # Apply limit
        if limit:
            history = history[:limit]
        
        return history
    
    def get_trigger_stats(self) -> Dict:
        """
        Get trigger statistics.
        
        Returns:
            Statistics dictionary
        """
        total_triggers = len(self.triggers)
        enabled_triggers = sum(1 for t in self.triggers.values() if t.enabled)
        total_executions = len(self.execution_history)
        
        # Count by status
        status_counts = defaultdict(int)
        for execution in self.execution_history:
            status_counts[execution.status.value] += 1
        
        # Count by type
        type_counts = defaultdict(int)
        for trigger in self.triggers.values():
            type_counts[trigger.trigger_type.value] += 1
        
        return {
            "total_triggers": total_triggers,
            "enabled_triggers": enabled_triggers,
            "total_executions": total_executions,
            "executions_by_status": dict(status_counts),
            "triggers_by_type": dict(type_counts),
            "last_execution": self.execution_history[-1].triggered_at.isoformat() if self.execution_history else None
        }
    
    # Private methods
    
    def _register_default_triggers(self):
        """Register default triggers"""
        # These are template triggers - actual implementations would be added by the system
        logger.info("Default triggers registered (templates only)")


# Global instance
_trigger_manager = None


def get_trigger_manager() -> EventTriggerManager:
    """Get global EventTriggerManager instance"""
    global _trigger_manager
    if _trigger_manager is None:
        _trigger_manager = EventTriggerManager()
    return _trigger_manager


# Helper functions for creating common triggers

def create_price_spike_trigger(
    threshold_percent: float = 5.0,
    action_executor: Optional[Callable] = None
) -> Dict:
    """
    Create a price spike trigger definition.
    
    Args:
        threshold_percent: Minimum price change to trigger
        action_executor: Async function to execute
    
    Returns:
        Trigger definition dict
    """
    def condition_evaluator(context: Dict, params: Dict) -> bool:
        price_change = abs(context.get('price_change_percent', 0))
        return price_change >= params['threshold']
    
    return {
        "id": f"price_spike_{threshold_percent}",
        "name": f"Price Spike ≥{threshold_percent}%",
        "trigger_type": TriggerType.PRICE_MOVEMENT,
        "priority": TriggerPriority.HIGH,
        "condition": TriggerCondition(
            condition_type="price_change",
            parameters={"threshold": threshold_percent},
            evaluator=condition_evaluator
        ),
        "action": LearningAction(
            action_type="research_cause",
            parameters={"topic": "price_spike_cause"},
            executor=action_executor
        ),
        "cooldown_seconds": 3600
    }


def create_earnings_trigger(
    days_before: int = 1,
    action_executor: Optional[Callable] = None
) -> Dict:
    """
    Create an earnings event trigger definition.
    
    Args:
        days_before: Days before earnings to trigger
        action_executor: Async function to execute
    
    Returns:
        Trigger definition dict
    """
    def condition_evaluator(context: Dict, params: Dict) -> bool:
        days_until = context.get('days_until_earnings')
        return days_until == params['days_before']
    
    return {
        "id": f"earnings_{days_before}d",
        "name": f"Earnings in {days_before} Day(s)",
        "trigger_type": TriggerType.EARNINGS_EVENT,
        "priority": TriggerPriority.MEDIUM,
        "condition": TriggerCondition(
            condition_type="earnings_proximity",
            parameters={"days_before": days_before},
            evaluator=condition_evaluator
        ),
        "action": LearningAction(
            action_type="research_earnings",
            parameters={"topic": "earnings_expectations"},
            executor=action_executor
        ),
        "cooldown_seconds": 86400  # Once per day
    }

