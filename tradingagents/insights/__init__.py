"""
Automated Insights & Alerts Module - Phase 7

Provides daily market digests, price alerts, and proactive notifications.
"""

from .digest import MarketDigest
from .alerts import PriceAlertSystem
from .notifications import NotificationDelivery

__all__ = ['MarketDigest', 'PriceAlertSystem', 'NotificationDelivery']
