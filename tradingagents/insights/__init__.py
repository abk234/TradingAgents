# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Automated Insights & Alerts Module - Phase 7

Provides daily market digests, price alerts, and proactive notifications.
"""

from .digest import MarketDigest
from .alerts import PriceAlertSystem
from .notifications import NotificationDelivery

__all__ = ['MarketDigest', 'PriceAlertSystem', 'NotificationDelivery']
