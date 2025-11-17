"""
Task Tracker for TradingAgents
Track task execution and send notifications on completion
"""

import os
import logging
from typing import Optional, Dict, Any, Callable
from datetime import datetime
from functools import wraps
import traceback

from .email_notifier import EmailNotifier
from .slack_notifier import SlackNotifier

logger = logging.getLogger(__name__)


class TaskTracker:
    """Track tasks and send notifications on completion"""

    def __init__(self):
        """Initialize task tracker with notifiers"""
        self.email_notifier = EmailNotifier()
        self.slack_notifier = SlackNotifier()
        self.notify_on_success = os.getenv('NOTIFY_ON_SUCCESS', 'true').lower() == 'true'
        self.notify_on_error = os.getenv('NOTIFY_ON_ERROR', 'true').lower() == 'true'

    def track_task(self, task_name: str, notify_email: bool = True, notify_slack: bool = True):
        """
        Decorator to track task execution and send notifications

        Usage:
            @task_tracker.track_task("Morning Briefing")
            def run_morning_briefing():
                # Task code here
                pass

        Args:
            task_name: Name of the task to track
            notify_email: Send email notification on completion
            notify_slack: Send Slack notification on completion

        Returns:
            Decorated function that tracks execution
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = datetime.now()
                logger.info(f"Starting task: {task_name}")

                try:
                    # Execute the task
                    result = func(*args, **kwargs)

                    # Calculate duration
                    duration = (datetime.now() - start_time).total_seconds()
                    duration_str = f"{duration:.1f}s"

                    details = f"Task completed successfully in {duration_str}"

                    # Send success notifications
                    if self.notify_on_success:
                        if notify_email:
                            self.email_notifier.send_task_completion(task_name, "success", details)
                        if notify_slack:
                            self.slack_notifier.send_task_completion(task_name, "success", details)

                    logger.info(f"Task completed: {task_name} ({duration_str})")
                    return result

                except Exception as e:
                    # Calculate duration
                    duration = (datetime.now() - start_time).total_seconds()
                    duration_str = f"{duration:.1f}s"

                    # Format error details
                    error_msg = str(e)
                    error_trace = traceback.format_exc()
                    details = f"Task failed after {duration_str}\n\nError: {error_msg}\n\n{error_trace[:500]}"

                    # Send error notifications
                    if self.notify_on_error:
                        if notify_email:
                            self.email_notifier.send_task_completion(task_name, "error", details)
                        if notify_slack:
                            self.slack_notifier.send_task_completion(task_name, "error", error_msg)

                    logger.error(f"Task failed: {task_name} - {error_msg}")
                    raise

            return wrapper
        return decorator

    def notify_completion(self, task_name: str, status: str, details: Optional[str] = None,
                         email: bool = True, slack: bool = True) -> None:
        """
        Manually send completion notification

        Args:
            task_name: Name of the task
            status: Status (success, warning, error)
            details: Optional details
            email: Send email notification
            slack: Send Slack notification
        """
        if email:
            self.email_notifier.send_task_completion(task_name, status, details)
        if slack:
            self.slack_notifier.send_task_completion(task_name, status, details)

    def send_briefing(self, data: Dict[str, Any]) -> None:
        """
        Send morning briefing via email and Slack

        Args:
            data: Briefing data dictionary
        """
        self.email_notifier.send_morning_briefing(data)
        self.slack_notifier.send_morning_briefing(data)

    def send_alert(self, alert_type: str, symbol: str, message: str,
                  data: Optional[Dict[str, Any]] = None) -> None:
        """
        Send alert via email and Slack

        Args:
            alert_type: Type of alert
            symbol: Stock symbol
            message: Alert message
            data: Optional additional data
        """
        self.email_notifier.send_alert(alert_type, symbol, message, data)
        self.slack_notifier.send_alert(alert_type, symbol, message, data)

    def send_analysis_complete(self, symbol: str, recommendation: str, confidence: float) -> None:
        """
        Send analysis completion notification

        Args:
            symbol: Stock symbol
            recommendation: BUY/WAIT/SELL
            confidence: Confidence score
        """
        self.slack_notifier.send_analysis_complete(symbol, recommendation, confidence)

    def send_performance_report(self, metrics: Dict[str, Any], period: str = "30 days") -> None:
        """
        Send performance report

        Args:
            metrics: Performance metrics
            period: Reporting period
        """
        self.email_notifier.send_performance_report(metrics, period)
        self.slack_notifier.send_performance_report(metrics, period)


# Global instance for easy importing
task_tracker = TaskTracker()


# Convenience decorators
def notify_on_completion(task_name: str, email: bool = True, slack: bool = True):
    """Convenience decorator for task tracking"""
    return task_tracker.track_task(task_name, email, slack)


# Example usage:
if __name__ == "__main__":
    # Example 1: Using decorator
    @notify_on_completion("Test Task")
    def test_task():
        print("Running test task...")
        import time
        time.sleep(2)
        print("Task complete!")
        return "success"

    # Example 2: Manual notification
    tracker = TaskTracker()
    tracker.notify_completion("Manual Task", "success", "Task ran successfully")

    # Example 3: Send briefing
    briefing_data = {
        'sector_analysis': [
            {'sector': 'Technology', 'strength_score': 87},
            {'sector': 'Healthcare', 'strength_score': 78}
        ],
        'top_opportunities': [
            {'symbol': 'NVDA', 'priority_score': 95},
            {'symbol': 'MSFT', 'priority_score': 88}
        ],
        'performance': {
            'win_rate': 76.5,
            'alpha': 2.8
        }
    }
    tracker.send_briefing(briefing_data)
