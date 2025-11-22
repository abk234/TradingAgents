# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

import logging
from datetime import date, timedelta
from tradingagents.backtest.backtest_engine import BacktestEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_automated_backtest():
    """Run automated backtest for a set of tickers."""
    engine = BacktestEngine()
    
    # Define parameters
    end_date = date.today()
    start_date = end_date - timedelta(days=90) # Last quarter
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]
    
    logger.info("Starting automated quarterly backtest...")
    
    result = engine.test_strategy(
        strategy_name="Standard_Four_Gate",
        start_date=start_date,
        end_date=end_date,
        tickers=tickers,
        holding_period_days=10,
        min_confidence=75
    )
    
    print("\n" + "="*50)
    print(result)
    print("="*50 + "\n")
    
    # In a real scenario, we would store this result in the DB
    # engine.store_result(result)

if __name__ == "__main__":
    run_automated_backtest()
