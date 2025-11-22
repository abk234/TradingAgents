# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
System Doctor - Self-Diagnostics and Health Monitoring

Eddie v2.0's "System Doctor" agent that audits the application's health,
validates data integrity, and verifies indicator calculations before recommendations.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class IndicatorAuditResult:
    """Result of independent indicator calculation audit."""
    
    indicator_name: str
    application_value: Optional[float] = None
    independent_value: Optional[float] = None
    discrepancy: Optional[float] = None
    discrepancy_percent: Optional[float] = None
    passed: bool = True
    warning: Optional[str] = None
    
    def calculate_discrepancy(self):
        """Calculate discrepancy between application and independent values."""
        if self.application_value is None or self.independent_value is None:
            self.passed = False
            self.warning = "Missing values for comparison"
            return
        
        self.discrepancy = abs(self.application_value - self.independent_value)
        
        # Calculate percentage discrepancy
        if self.application_value != 0:
            self.discrepancy_percent = (self.discrepancy / abs(self.application_value)) * 100
        else:
            self.discrepancy_percent = 100.0 if self.independent_value != 0 else 0.0
        
        # Tolerance thresholds
        if self.indicator_name == "RSI":
            # RSI is 0-100, allow 1% discrepancy
            threshold = 1.0
        elif self.indicator_name == "MACD":
            # MACD can vary more, allow 5% discrepancy
            threshold = 5.0
        else:
            threshold = 2.0
        
        if self.discrepancy_percent > threshold:
            self.passed = False
            self.warning = f"Discrepancy {self.discrepancy_percent:.2f}% exceeds threshold {threshold}%"


@dataclass
class DataSanityCheckResult:
    """Result of data sanity check (local DB vs external API)."""
    
    ticker: str
    local_price: Optional[float] = None
    external_price: Optional[float] = None
    price_discrepancy: Optional[float] = None
    price_discrepancy_percent: Optional[float] = None
    passed: bool = True
    warning: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def calculate_discrepancy(self):
        """Calculate price discrepancy between local and external sources."""
        if self.local_price is None or self.external_price is None:
            self.passed = False
            self.warning = "Missing price data for comparison"
            return
        
        self.price_discrepancy = abs(self.local_price - self.external_price)
        
        if self.local_price != 0:
            self.price_discrepancy_percent = (self.price_discrepancy / self.local_price) * 100
        else:
            self.price_discrepancy_percent = 100.0 if self.external_price != 0 else 0.0
        
        # Alert if discrepancy > 0.5% (as per PRD requirement)
        if self.price_discrepancy_percent > 0.5:
            self.passed = False
            self.warning = f"Data desync detected: {self.price_discrepancy_percent:.2f}% discrepancy"


@dataclass
class SystemHealthReport:
    """Comprehensive system health report."""
    
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ticker: Optional[str] = None
    
    # Data sanity checks
    data_sanity_check: Optional[DataSanityCheckResult] = None
    
    # Indicator audits
    indicator_audits: List[IndicatorAuditResult] = field(default_factory=list)
    
    # Overall health
    overall_health: str = "HEALTHY"  # HEALTHY, WARNING, CRITICAL
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def assess_overall_health(self):
        """Assess overall system health based on all checks."""
        issues = []
        
        # Check data sanity
        if self.data_sanity_check and not self.data_sanity_check.passed:
            issues.append(f"Data desync: {self.data_sanity_check.warning}")
        
        # Check indicator audits
        failed_audits = [audit for audit in self.indicator_audits if not audit.passed]
        if failed_audits:
            issues.append(f"{len(failed_audits)} indicator calculation(s) failed verification")
        
        if not issues:
            self.overall_health = "HEALTHY"
        elif len(issues) == 1:
            self.overall_health = "WARNING"
            self.warnings.extend(issues)
        else:
            self.overall_health = "CRITICAL"
            self.warnings.extend(issues)
        
        # Generate recommendations
        if self.overall_health != "HEALTHY":
            if self.data_sanity_check and not self.data_sanity_check.passed:
                self.recommendations.append("Refresh data from external sources")
            if failed_audits:
                self.recommendations.append("Switch to manual indicator calculations for this session")
                self.recommendations.append("Review indicator calculation libraries for potential bugs")
    
    def format_for_display(self) -> str:
        """Format health report for user display."""
        lines = [
            f"\n🏥 **System Doctor Health Report**",
            f"Timestamp: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}",
        ]
        
        if self.ticker:
            lines.append(f"Ticker: {self.ticker}")
        
        # Overall health status
        health_emoji = {
            "HEALTHY": "✅",
            "WARNING": "⚠️",
            "CRITICAL": "🔴"
        }
        lines.append(f"\nOverall Health: {health_emoji.get(self.overall_health, '❓')} **{self.overall_health}**")
        
        # Data sanity check
        if self.data_sanity_check:
            lines.append("\n📊 **Data Sanity Check:**")
            if self.data_sanity_check.passed:
                lines.append("✅ Data sources aligned")
                lines.append(f"   Local: ${self.data_sanity_check.local_price:.2f}")
                lines.append(f"   External: ${self.data_sanity_check.external_price:.2f}")
                lines.append(f"   Discrepancy: {self.data_sanity_check.price_discrepancy_percent:.3f}%")
            else:
                lines.append(f"❌ {self.data_sanity_check.warning}")
                lines.append(f"   Local: ${self.data_sanity_check.local_price:.2f}")
                lines.append(f"   External: ${self.data_sanity_check.external_price:.2f}")
                lines.append(f"   Discrepancy: {self.data_sanity_check.price_discrepancy_percent:.2f}%")
        
        # Indicator audits
        if self.indicator_audits:
            lines.append("\n🔬 **Indicator Math Audit:**")
            for audit in self.indicator_audits:
                if audit.passed:
                    lines.append(f"✅ {audit.indicator_name}: Verified")
                    lines.append(f"   App: {audit.application_value:.4f} | Independent: {audit.independent_value:.4f}")
                    lines.append(f"   Discrepancy: {audit.discrepancy_percent:.2f}%")
                else:
                    lines.append(f"❌ {audit.indicator_name}: {audit.warning}")
                    lines.append(f"   App: {audit.application_value:.4f} | Independent: {audit.independent_value:.4f}")
                    lines.append(f"   Discrepancy: {audit.discrepancy_percent:.2f}%")
        
        # Warnings
        if self.warnings:
            lines.append("\n⚠️ **Warnings:**")
            for warning in self.warnings:
                lines.append(f"  - {warning}")
        
        # Recommendations
        if self.recommendations:
            lines.append("\n💡 **Recommendations:**")
            for rec in self.recommendations:
                lines.append(f"  - {rec}")
        
        return "\n".join(lines)


class SystemDoctor:
    """
    System Doctor - Audits application health and data integrity.
    
    Performs:
    1. Data sanity checks (local DB vs external API)
    2. Indicator math audits (independent calculation verification)
    3. System health assessment
    """
    
    @staticmethod
    def calculate_rsi_independent(prices: pd.Series, period: int = 14) -> float:
        """
        Independently calculate RSI using NumPy/pandas.
        
        This is Eddie's "independent calculation" to verify application values.
        """
        if len(prices) < period + 1:
            raise ValueError(f"Need at least {period + 1} data points for RSI calculation")
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        # Avoid division by zero
        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi.iloc[-1])
    
    @staticmethod
    def calculate_macd_independent(
        prices: pd.Series,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Dict[str, float]:
        """
        Independently calculate MACD using NumPy/pandas.
        
        Returns MACD line, signal line, and histogram.
        """
        if len(prices) < slow + signal:
            raise ValueError(f"Need at least {slow + signal} data points for MACD calculation")
        
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return {
            "macd": float(macd_line.iloc[-1]),
            "signal": float(signal_line.iloc[-1]),
            "histogram": float(histogram.iloc[-1])
        }
    
    def audit_indicator(
        self,
        indicator_name: str,
        application_value: float,
        price_data: pd.Series,
        **kwargs
    ) -> IndicatorAuditResult:
        """
        Audit an indicator calculation by comparing application value with independent calculation.
        
        Args:
            indicator_name: Name of indicator (RSI, MACD, etc.)
            application_value: Value from application/library
            price_data: Historical price data (close prices)
            **kwargs: Additional parameters for indicator calculation
        
        Returns:
            IndicatorAuditResult with comparison
        """
        audit = IndicatorAuditResult(
            indicator_name=indicator_name,
            application_value=application_value
        )
        
        try:
            if indicator_name.upper() == "RSI":
                period = kwargs.get("period", 14)
                independent_value = self.calculate_rsi_independent(price_data, period)
                audit.independent_value = independent_value
            
            elif indicator_name.upper() == "MACD":
                macd_result = self.calculate_macd_independent(
                    price_data,
                    fast=kwargs.get("fast", 12),
                    slow=kwargs.get("slow", 26),
                    signal=kwargs.get("signal", 9)
                )
                # Compare MACD line (main value)
                audit.independent_value = macd_result["macd"]
            
            else:
                audit.passed = False
                audit.warning = f"Indicator {indicator_name} not supported for audit"
                return audit
            
            audit.calculate_discrepancy()
            
        except Exception as e:
            logger.error(f"Error auditing {indicator_name}: {e}")
            audit.passed = False
            audit.warning = f"Audit failed: {str(e)}"
        
        return audit
    
    def check_data_sanity(
        self,
        ticker: str,
        local_price: float,
        external_price: Optional[float] = None
    ) -> DataSanityCheckResult:
        """
        Check data sanity by comparing local database price with external API.
        
        Args:
            ticker: Stock ticker symbol
            local_price: Price from local database
            external_price: Price from external API (yfinance). If None, will fetch.
        
        Returns:
            DataSanityCheckResult with comparison
        """
        check = DataSanityCheckResult(
            ticker=ticker,
            local_price=local_price
        )
        
        try:
            # Fetch external price if not provided
            if external_price is None:
                import yfinance as yf
                stock = yf.Ticker(ticker)
                hist = stock.history(period="1d")
                if not hist.empty:
                    external_price = float(hist['Close'].iloc[-1])
                else:
                    check.passed = False
                    check.warning = "Could not fetch external price"
                    return check
            
            check.external_price = external_price
            check.calculate_discrepancy()
            
        except Exception as e:
            logger.error(f"Error checking data sanity for {ticker}: {e}")
            check.passed = False
            check.warning = f"Data sanity check failed: {str(e)}"
        
        return check
    
    def perform_health_check(
        self,
        ticker: str,
        local_price: float,
        application_indicators: Optional[Dict[str, float]] = None,
        price_history: Optional[pd.DataFrame] = None,
        external_price: Optional[float] = None
    ) -> SystemHealthReport:
        """
        Perform comprehensive system health check.
        
        Args:
            ticker: Stock ticker symbol
            local_price: Price from local database
            application_indicators: Dict of indicator values from application (e.g., {"RSI": 45.2, "MACD": 0.5})
            price_history: Historical price data (DataFrame with 'close' column or Series)
            external_price: External API price (optional, will fetch if None)
        
        Returns:
            SystemHealthReport with all checks
        """
        report = SystemHealthReport(ticker=ticker)
        
        # Data sanity check
        logger.info(f"Performing data sanity check for {ticker}...")
        report.data_sanity_check = self.check_data_sanity(ticker, local_price, external_price)
        
        # Indicator audits (if data provided)
        if application_indicators and price_history is not None:
            logger.info(f"Auditing indicators for {ticker}...")
            
            # Convert price_history to Series if DataFrame
            if isinstance(price_history, pd.DataFrame):
                if 'close' in price_history.columns:
                    prices = price_history['close']
                elif 'Close' in price_history.columns:
                    prices = price_history['Close']
                else:
                    prices = price_history.iloc[:, -1]  # Use last column
            else:
                prices = price_history
            
            # Audit RSI if available
            if "RSI" in application_indicators or "rsi" in application_indicators:
                rsi_value = application_indicators.get("RSI") or application_indicators.get("rsi")
                audit = self.audit_indicator("RSI", rsi_value, prices, period=14)
                report.indicator_audits.append(audit)
            
            # Audit MACD if available
            if "MACD" in application_indicators or "macd" in application_indicators:
                macd_value = application_indicators.get("MACD") or application_indicators.get("macd")
                audit = self.audit_indicator("MACD", macd_value, prices)
                report.indicator_audits.append(audit)
        
        # Assess overall health
        report.assess_overall_health()
        
        logger.info(
            f"Health check complete for {ticker}: {report.overall_health} "
            f"(Data: {report.data_sanity_check.passed if report.data_sanity_check else 'N/A'}, "
            f"Indicators: {len([a for a in report.indicator_audits if a.passed])}/{len(report.indicator_audits)} passed)"
        )
        
        return report

