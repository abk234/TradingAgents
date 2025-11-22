# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

import logging
from typing import Optional
from tradingagents.validation.price_validation import validate_price_multi_source

logger = logging.getLogger(__name__)

class CircuitBreakerException(Exception):
    """Exception raised when circuit breaker is triggered."""
    pass

def check_circuit_breaker(ticker: str, discrepancy_threshold: float = 2.0) -> None:
    """
    Check if trading should be halted for a ticker due to data anomalies.
    
    Args:
        ticker: Stock ticker symbol
        discrepancy_threshold: Maximum acceptable price discrepancy (%)
        
    Raises:
        CircuitBreakerException: If validation fails
    """
    logger.info(f"Running circuit breaker check for {ticker}...")
    
    report = validate_price_multi_source(ticker, discrepancy_threshold=discrepancy_threshold)
    
    if not report.validation_passed:
        error_msg = f"Circuit Breaker Triggered for {ticker}!\n"
        error_msg += f"Reason: Data validation failed. Confidence Score: {report.confidence_score}/10\n"
        if report.warnings:
            error_msg += "Warnings:\n" + "\n".join([f"- {w}" for w in report.warnings])
            
        logger.error(error_msg)
        raise CircuitBreakerException(error_msg)
        
    logger.info(f"Circuit breaker passed for {ticker}. Confidence: {report.confidence_score}/10")
