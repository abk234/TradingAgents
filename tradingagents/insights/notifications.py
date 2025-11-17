"""
Notification Delivery System - Phase 7

Delivers alerts and digests through various channels:
- Terminal output (default)
- Log files
- Email (optional, requires configuration)
- Webhook (optional, for Slack/Discord integration)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import json
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class NotificationDelivery:
    """Handle delivery of notifications through various channels."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize notification delivery.

        Args:
            config: Configuration dictionary with delivery settings
        """
        self.config = config or {}
        self.log_dir = Path(self.config.get('log_dir', './logs'))
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def send(
        self,
        message: str,
        title: Optional[str] = None,
        priority: str = 'MEDIUM',
        channels: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """
        Send notification through specified channels.

        Args:
            message: The notification message
            title: Optional title/subject
            priority: URGENT, HIGH, MEDIUM, LOW
            channels: List of channels ('terminal', 'log', 'email', 'webhook')

        Returns:
            Dictionary of channel: success status
        """
        if channels is None:
            channels = ['terminal', 'log']

        results = {}

        for channel in channels:
            try:
                if channel == 'terminal':
                    results['terminal'] = self._send_terminal(message, title, priority)
                elif channel == 'log':
                    results['log'] = self._send_log(message, title, priority)
                elif channel == 'email':
                    results['email'] = self._send_email(message, title, priority)
                elif channel == 'webhook':
                    results['webhook'] = self._send_webhook(message, title, priority)
                else:
                    logger.warning(f"Unknown notification channel: {channel}")
                    results[channel] = False
            except Exception as e:
                logger.error(f"Failed to send notification via {channel}: {e}")
                results[channel] = False

        return results

    def _send_terminal(
        self, message: str, title: Optional[str], priority: str
    ) -> bool:
        """Send notification to terminal output."""
        try:
            if title:
                print(f"\n{'='*80}")
                print(f"📢 {title}")
                print(f"{'='*80}\n")

            print(message)
            print()
            return True
        except Exception as e:
            logger.error(f"Terminal notification failed: {e}")
            return False

    def _send_log(
        self, message: str, title: Optional[str], priority: str
    ) -> bool:
        """Log notification to file."""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_file = self.log_dir / 'notifications.log'

            with open(log_file, 'a') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"[{timestamp}] Priority: {priority}\n")
                if title:
                    f.write(f"Title: {title}\n")
                f.write(f"{'-'*80}\n")
                f.write(f"{message}\n")
                f.write(f"{'='*80}\n")

            return True
        except Exception as e:
            logger.error(f"Log notification failed: {e}")
            return False

    def _send_email(
        self, message: str, title: Optional[str], priority: str
    ) -> bool:
        """Send notification via email (requires configuration)."""
        email_config = self.config.get('email', {})

        if not email_config.get('enabled'):
            logger.debug("Email notifications not configured")
            return False

        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            sender = email_config.get('from')
            recipients = email_config.get('to', [])
            smtp_server = email_config.get('smtp_server')
            smtp_port = email_config.get('smtp_port', 587)
            username = email_config.get('username')
            password = email_config.get('password')

            if not all([sender, recipients, smtp_server, username, password]):
                logger.warning("Email configuration incomplete")
                return False

            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = ', '.join(recipients) if isinstance(recipients, list) else recipients
            msg['Subject'] = title or f"Trading Alert - {priority}"

            msg.attach(MIMEText(message, 'plain'))

            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(username, password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {recipients}")
            return True

        except Exception as e:
            logger.error(f"Email notification failed: {e}")
            return False

    def _send_webhook(
        self, message: str, title: Optional[str], priority: str
    ) -> bool:
        """Send notification via webhook (Slack, Discord, etc.)."""
        # Try to use the dedicated SlackNotifier first
        try:
            from tradingagents.notifications.slack_notifier import SlackNotifier
            slack = SlackNotifier()

            if slack.enabled:
                # Use SlackNotifier for better formatting
                return slack.send_message(f"*{title or 'Trading Alert'}*\n{message}")
        except ImportError:
            logger.debug("SlackNotifier not available, using legacy webhook")
        except Exception as e:
            logger.debug(f"SlackNotifier failed, falling back to legacy: {e}")

        # Fallback to legacy webhook implementation
        webhook_config = self.config.get('webhook', {})

        # If no config provided, try environment variables
        if not webhook_config:
            enabled = os.getenv('SLACK_ENABLED', 'false').lower() == 'true'
            url = os.getenv('SLACK_WEBHOOK_URL', '')

            if not enabled or not url:
                logger.debug("Webhook notifications not configured")
                return False

            webhook_config = {'enabled': enabled, 'url': url}

        if not webhook_config.get('enabled'):
            logger.debug("Webhook notifications not configured")
            return False

        try:
            import requests

            url = webhook_config.get('url')
            if not url:
                logger.warning("Webhook URL not configured")
                return False

            # Format for Slack/Discord
            payload = {
                'text': title or 'Trading Alert',
                'content': message,
                'username': 'TradingAgents Bot',
            }

            # Slack-specific formatting
            if 'slack.com' in url:
                payload = {
                    'text': f"*{title or 'Trading Alert'}*\n```\n{message}\n```"
                }

            # Discord-specific formatting
            elif 'discord.com' in url:
                payload = {
                    'content': f"**{title or 'Trading Alert'}**\n```\n{message}\n```"
                }

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            logger.info("Webhook notification sent successfully")
            return True

        except Exception as e:
            logger.error(f"Webhook notification failed: {e}")
            return False

    def send_daily_digest(self, digest: str) -> Dict[str, bool]:
        """Send daily market digest."""
        return self.send(
            message=digest,
            title="Daily Market Digest",
            priority='MEDIUM',
            channels=self.config.get('digest_channels', ['terminal', 'log'])
        )

    def send_alert(self, alert: Dict[str, Any]) -> Dict[str, bool]:
        """Send a price alert."""
        priority = alert.get('priority', 'MEDIUM')

        # Format alert message
        message = f"{alert.get('symbol')}: {alert.get('message')}\n"
        message += f"Action: {alert.get('action')}\n"

        if alert.get('current_price'):
            message += f"Current Price: ${alert['current_price']:.2f}\n"

        return self.send(
            message=message,
            title=f"Price Alert - {alert.get('type')}",
            priority=priority,
            channels=self.config.get('alert_channels', ['terminal', 'log'])
        )

    def send_weekly_summary(self, summary: str) -> Dict[str, bool]:
        """Send weekly performance summary."""
        return self.send(
            message=summary,
            title="Weekly Performance Summary",
            priority='LOW',
            channels=self.config.get('summary_channels', ['terminal', 'log', 'email'])
        )
