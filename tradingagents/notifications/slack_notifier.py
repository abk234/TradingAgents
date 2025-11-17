"""
Slack/Discord Notification System
Send formatted messages to Slack or Discord via webhooks
"""

import os
import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SlackNotifier:
    """Send notifications to Slack or Discord via webhooks"""

    def __init__(self):
        """Initialize Slack notifier with config from environment"""
        self.enabled = os.getenv('SLACK_ENABLED', 'false').lower() == 'true'
        self.webhook_url = os.getenv('SLACK_WEBHOOK_URL', '')
        self.channel = os.getenv('SLACK_CHANNEL', '')
        self.username = os.getenv('SLACK_USERNAME', 'TradingAgents Bot')
        self.icon_emoji = os.getenv('SLACK_ICON_EMOJI', ':robot_face:')

        if self.enabled and not self.webhook_url:
            logger.warning("Slack enabled but webhook URL not configured. Disabling Slack notifications.")
            self.enabled = False

    def send_message(self, text: str, attachments: Optional[List[Dict[str, Any]]] = None) -> bool:
        """
        Send a message to Slack/Discord

        Args:
            text: Main message text
            attachments: Optional list of attachments (Slack format)

        Returns:
            bool: True if sent successfully
        """
        if not self.enabled:
            logger.debug("Slack notifications disabled, skipping message")
            return False

        payload = {
            "text": text,
            "username": self.username,
            "icon_emoji": self.icon_emoji
        }

        if self.channel:
            payload["channel"] = self.channel

        if attachments:
            payload["attachments"] = attachments

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"Slack message sent successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to send Slack message: {e}")
            return False

    def send_morning_briefing(self, data: Dict[str, Any]) -> bool:
        """
        Send morning briefing notification

        Args:
            data: Dictionary containing briefing data

        Returns:
            bool: True if sent successfully
        """
        # Extract top sectors
        top_sectors = data.get('sector_analysis', [])[:3]
        sector_text = "\n".join([
            f"  {i+1}. {s.get('sector', 'Unknown')}: {s.get('strength_score', 0):.0f}/100"
            for i, s in enumerate(top_sectors)
        ])

        # Extract top opportunities
        top_stocks = data.get('top_opportunities', [])[:3]
        stocks_text = "\n".join([
            f"  • {s.get('symbol', 'N/A')}: {s.get('priority_score', 0):.0f}/100"
            for s in top_stocks
        ])

        text = f"🌅 *Morning Briefing - {datetime.now().strftime('%B %d, %Y')}*"

        attachments = [
            {
                "color": "#36a64f",
                "fields": [
                    {
                        "title": "🎯 Top Sectors",
                        "value": sector_text or "No data available",
                        "short": False
                    },
                    {
                        "title": "📈 Top Opportunities",
                        "value": stocks_text or "No recommendations",
                        "short": False
                    }
                ],
                "footer": "TradingAgents",
                "ts": int(datetime.now().timestamp())
            }
        ]

        # Add performance if available
        performance = data.get('performance')
        if performance:
            perf_text = f"Win Rate: {performance.get('win_rate', 0):.1f}% | Alpha: {performance.get('alpha', 0):+.2f}%"
            attachments[0]["fields"].append({
                "title": "📊 Performance (30d)",
                "value": perf_text,
                "short": False
            })

        return self.send_message(text, attachments)

    def send_task_completion(self, task_name: str, status: str, details: Optional[str] = None) -> bool:
        """
        Send task completion notification

        Args:
            task_name: Name of the completed task
            status: Status (success, warning, error)
            details: Optional details

        Returns:
            bool: True if sent successfully
        """
        emoji_map = {
            'success': '✅',
            'warning': '⚠️',
            'error': '❌'
        }
        color_map = {
            'success': 'good',
            'warning': 'warning',
            'error': 'danger'
        }

        emoji = emoji_map.get(status, 'ℹ️')
        color = color_map.get(status, '#808080')

        text = f"{emoji} *{task_name}*"

        attachments = [{
            "color": color,
            "fields": [
                {
                    "title": "Status",
                    "value": status.upper(),
                    "short": True
                },
                {
                    "title": "Time",
                    "value": datetime.now().strftime('%H:%M:%S'),
                    "short": True
                }
            ],
            "footer": "TradingAgents",
            "ts": int(datetime.now().timestamp())
        }]

        if details:
            attachments[0]["text"] = details

        return self.send_message(text, attachments)

    def send_alert(self, alert_type: str, symbol: str, message: str, data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send price alert notification

        Args:
            alert_type: Type of alert
            symbol: Stock symbol
            message: Alert message
            data: Optional additional data

        Returns:
            bool: True if sent successfully
        """
        text = f"🔔 *{alert_type.upper()} Alert: {symbol}*"

        attachments = [{
            "color": "#fbbf24",
            "text": message,
            "footer": "TradingAgents",
            "ts": int(datetime.now().timestamp())
        }]

        if data:
            fields = [
                {
                    "title": key.replace('_', ' ').title(),
                    "value": str(value),
                    "short": True
                }
                for key, value in list(data.items())[:6]  # Limit to 6 fields
            ]
            attachments[0]["fields"] = fields

        return self.send_message(text, attachments)

    def send_analysis_complete(self, symbol: str, recommendation: str, confidence: float) -> bool:
        """
        Send analysis completion notification

        Args:
            symbol: Stock symbol
            recommendation: BUY/WAIT/SELL
            confidence: Confidence score 0-100

        Returns:
            bool: True if sent successfully
        """
        emoji_map = {
            'BUY': '🟢',
            'STRONG_BUY': '🟢🟢',
            'WAIT': '🟡',
            'HOLD': '🟡',
            'SELL': '🔴',
            'STRONG_SELL': '🔴🔴'
        }

        color_map = {
            'BUY': 'good',
            'STRONG_BUY': 'good',
            'WAIT': 'warning',
            'HOLD': 'warning',
            'SELL': 'danger',
            'STRONG_SELL': 'danger'
        }

        emoji = emoji_map.get(recommendation.upper(), '⚪')
        color = color_map.get(recommendation.upper(), '#808080')

        text = f"📊 *Analysis Complete: {symbol}*"

        attachments = [{
            "color": color,
            "fields": [
                {
                    "title": "Recommendation",
                    "value": f"{emoji} {recommendation}",
                    "short": True
                },
                {
                    "title": "Confidence",
                    "value": f"{confidence:.1f}%",
                    "short": True
                }
            ],
            "footer": "TradingAgents",
            "ts": int(datetime.now().timestamp())
        }]

        return self.send_message(text, attachments)

    def send_performance_report(self, metrics: Dict[str, Any], period: str = "30 days") -> bool:
        """
        Send performance report

        Args:
            metrics: Performance metrics
            period: Reporting period

        Returns:
            bool: True if sent successfully
        """
        text = f"📊 *Performance Report - {period}*"

        win_rate = metrics.get('win_rate', 0)
        alpha = metrics.get('alpha', 0)
        total_recs = metrics.get('total_recs', 0)
        avg_return = metrics.get('avg_return', 0)

        # Color based on performance
        color = "good" if win_rate >= 75 and alpha > 0 else "warning" if win_rate >= 60 else "danger"

        attachments = [{
            "color": color,
            "fields": [
                {
                    "title": "Win Rate",
                    "value": f"{win_rate:.1f}%",
                    "short": True
                },
                {
                    "title": "Alpha",
                    "value": f"{alpha:+.2f}%",
                    "short": True
                },
                {
                    "title": "Total Recommendations",
                    "value": str(total_recs),
                    "short": True
                },
                {
                    "title": "Avg Return",
                    "value": f"{avg_return:+.2f}%",
                    "short": True
                }
            ],
            "footer": "TradingAgents",
            "ts": int(datetime.now().timestamp())
        }]

        return self.send_message(text, attachments)
