"""
Email Notification System
Send beautiful HTML emails for trading alerts and reports
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from jinja2 import Template
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

logger = logging.getLogger(__name__)


class EmailNotifier:
    """Send email notifications for trading events"""

    def __init__(self):
        """Initialize email notifier with config from environment"""
        self.enabled = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'
        self.from_email = os.getenv('EMAIL_FROM', '')
        self.to_email = os.getenv('EMAIL_TO', '')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_password = os.getenv('EMAIL_PASSWORD', '')

        if self.enabled and not all([self.from_email, self.to_email, self.smtp_password]):
            logger.warning("Email enabled but missing configuration. Disabling email notifications.")
            self.enabled = False

    def send_email(self, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
        """
        Send an email notification

        Args:
            subject: Email subject line
            html_content: HTML content of email
            text_content: Plain text fallback (optional)

        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.debug("Email notifications disabled, skipping email")
            return False

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = self.to_email
            msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')

            # Add text version if provided
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)

            # Add HTML version
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.from_email, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def send_morning_briefing(self, data: Dict[str, Any]) -> bool:
        """
        Send morning briefing email

        Args:
            data: Dictionary containing briefing data
                  - sector_analysis: List of sector rankings
                  - top_opportunities: List of top stocks
                  - alerts: List of active alerts
                  - performance: Performance metrics
                  - dividends: Upcoming dividends

        Returns:
            bool: True if sent successfully
        """
        subject = f"🎯 Trading Briefing - {datetime.now().strftime('%B %d, %Y')}"

        # Load template
        template_path = os.path.join(
            os.path.dirname(__file__),
            'templates',
            'briefing_email.html'
        )

        try:
            with open(template_path, 'r') as f:
                template = Template(f.read())

            html_content = template.render(
                date=datetime.now().strftime('%B %d, %Y'),
                **data
            )

            return self.send_email(subject, html_content)

        except Exception as e:
            logger.error(f"Failed to render email template: {e}")
            return False

    def send_task_completion(self, task_name: str, status: str, details: Optional[str] = None) -> bool:
        """
        Send task completion notification

        Args:
            task_name: Name of the completed task
            status: Status (success, warning, error)
            details: Optional details about the task

        Returns:
            bool: True if sent successfully
        """
        emoji_map = {
            'success': '✅',
            'warning': '⚠️',
            'error': '❌'
        }
        emoji = emoji_map.get(status, 'ℹ️')

        subject = f"{emoji} TradingAgents: {task_name} - {status.upper()}"

        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #1e3a8a; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f3f4f6; padding: 20px; }}
                .status {{ font-size: 18px; font-weight: bold; margin: 20px 0; }}
                .success {{ color: #059669; }}
                .warning {{ color: #d97706; }}
                .error {{ color: #dc2626; }}
                .details {{ background-color: white; padding: 15px; border-left: 4px solid #3b82f6; }}
                .footer {{ text-align: center; color: #6b7280; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 TradingAgents Notification</h1>
                </div>
                <div class="content">
                    <div class="status {status}">
                        {emoji} {task_name}
                    </div>
                    <p><strong>Status:</strong> {status.upper()}</p>
                    <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    {f'<div class="details"><strong>Details:</strong><br>{details}</div>' if details else ''}
                </div>
                <div class="footer">
                    <p>Automated notification from TradingAgents</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(subject, html_content)

    def send_alert(self, alert_type: str, symbol: str, message: str, data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send price alert notification

        Args:
            alert_type: Type of alert (buy, sell, price_target, etc.)
            symbol: Stock symbol
            message: Alert message
            data: Optional additional data

        Returns:
            bool: True if sent successfully
        """
        subject = f"🔔 Alert: {alert_type.upper()} - {symbol}"

        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .alert-header {{ background-color: #fbbf24; color: #78350f; padding: 20px; border-radius: 8px; }}
                .alert-body {{ background-color: #fffbeb; padding: 20px; margin-top: 20px; border-radius: 8px; }}
                .data-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                .data-table th, .data-table td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="alert-header">
                    <h2>🔔 {alert_type.upper()} Alert</h2>
                    <h3>{symbol}</h3>
                </div>
                <div class="alert-body">
                    <p><strong>{message}</strong></p>
                    <p><small>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small></p>
                    {self._render_data_table(data) if data else ''}
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(subject, html_content)

    def send_performance_report(self, metrics: Dict[str, Any], period: str = "30 days") -> bool:
        """
        Send performance report

        Args:
            metrics: Performance metrics dictionary
            period: Reporting period

        Returns:
            bool: True if sent successfully
        """
        subject = f"📊 Performance Report - {period}"

        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #1e3a8a; color: white; padding: 20px; text-align: center; }}
                .metrics {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin: 20px 0; }}
                .metric-card {{ background-color: #f3f4f6; padding: 20px; border-radius: 8px; text-align: center; }}
                .metric-value {{ font-size: 32px; font-weight: bold; margin: 10px 0; }}
                .positive {{ color: #059669; }}
                .negative {{ color: #dc2626; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Performance Report</h1>
                    <p>{period}</p>
                </div>
                <div class="metrics">
                    {self._render_metric_card("Win Rate", f"{metrics.get('win_rate', 0):.1f}%", metrics.get('win_rate', 0) >= 75)}
                    {self._render_metric_card("Alpha", f"{metrics.get('alpha', 0):+.2f}%", metrics.get('alpha', 0) > 0)}
                    {self._render_metric_card("Total Recommendations", str(metrics.get('total_recs', 0)), True)}
                    {self._render_metric_card("Avg Return", f"{metrics.get('avg_return', 0):+.2f}%", metrics.get('avg_return', 0) > 0)}
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(subject, html_content)

    def _render_data_table(self, data: Dict[str, Any]) -> str:
        """Render data as HTML table"""
        rows = "".join([
            f"<tr><th>{key}</th><td>{value}</td></tr>"
            for key, value in data.items()
        ])
        return f'<table class="data-table">{rows}</table>'

    def _render_metric_card(self, label: str, value: str, is_positive: bool = True) -> str:
        """Render a metric card"""
        color_class = "positive" if is_positive else "negative"
        return f"""
        <div class="metric-card">
            <div>{label}</div>
            <div class="metric-value {color_class}">{value}</div>
        </div>
        """
