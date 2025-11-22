#!/usr/bin/env python3
# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Quick Strategy Testing Script

Test all strategies one after another on a stock.
"""

import sys
from datetime import date

from tradingagents.strategies import (
    StrategyDataCollector,
    ValueStrategy,
    GrowthStrategy,
    DividendStrategy,
    MomentumStrategy,
    ContrarianStrategy,
    QuantitativeStrategy,
    SectorRotationStrategy,
)

# Try to import Market Structure and Cloud Trend
try:
    from tradingagents.strategies.market_structure_cloud_trend import MarketStructureCloudTrendStrategy
    MARKET_STRUCTURE_AVAILABLE = True
except ImportError:
    MARKET_STRUCTURE_AVAILABLE = False
    print("⚠️  Market Structure and Cloud Trend strategy not available")

def test_all_strategies(ticker="AAPL"):
    """Test all strategies one after another."""
    
    strategies = [
        ("Value Investing", ValueStrategy()),
        ("Growth Investing", GrowthStrategy()),
        ("Dividend Investing", DividendStrategy()),
        ("Momentum Trading", MomentumStrategy()),
        ("Contrarian Investing", ContrarianStrategy()),
        ("Quantitative Investing", QuantitativeStrategy()),
        ("Sector Rotation", SectorRotationStrategy()),
    ]
    
    # Add Market Structure and Cloud Trend if available
    if MARKET_STRUCTURE_AVAILABLE:
        strategies.append(("Market Structure and Cloud Trend", MarketStructureCloudTrendStrategy()))
    
    print(f"\n{'='*70}")
    print(f"Testing All Strategies for {ticker}")
    print(f"{'='*70}\n")
    
    # Collect data once
    print("Collecting data...")
    collector = StrategyDataCollector()
    try:
        data = collector.collect_all_data(ticker, date.today().strftime("%Y-%m-%d"))
        print("✓ Data collected\n")
    except Exception as e:
        print(f"❌ Error collecting data: {e}")
        return
    
    results = []
    
    for i, (name, strategy) in enumerate(strategies, 1):
        print(f"\n{'─'*70}")
        print(f"[{i}/{len(strategies)}] {name}")
        print(f"{'─'*70}")
        
        try:
            # Prepare additional data
            additional_data = {
                "ticker": ticker,  # For AI Pine Script
                "analysis_date": date.today().strftime("%Y-%m-%d"),
            }
            
            result = strategy.evaluate(
                ticker=ticker,
                market_data=data["market_data"],
                fundamental_data=data["fundamental_data"],
                technical_data=data["technical_data"],
                additional_data=additional_data
            )
            
            print(f"✓ Recommendation: {result.recommendation.value}")
            print(f"✓ Confidence: {result.confidence}%")
            
            if result.entry_price:
                print(f"✓ Entry: ${result.entry_price:.2f}")
            if result.stop_loss:
                print(f"✓ Stop Loss: ${result.stop_loss:.2f}")
            if result.target_price:
                print(f"✓ Take Profit: ${result.target_price:.2f}")
            
            # Show reasoning (truncated)
            reasoning = result.reasoning[:150] + "..." if len(result.reasoning) > 150 else result.reasoning
            print(f"✓ Reasoning: {reasoning}")
            
            results.append((name, result))
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, None))
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}\n")
    
    buy_count = sum(1 for _, r in results if r and r.recommendation.value == "BUY")
    sell_count = sum(1 for _, r in results if r and r.recommendation.value == "SELL")
    wait_count = sum(1 for _, r in results if r and r.recommendation.value == "WAIT")
    hold_count = sum(1 for _, r in results if r and r.recommendation.value == "HOLD")
    
    print(f"Recommendations:")
    print(f"  ✅ BUY:   {buy_count}")
    print(f"  ❌ SELL:  {sell_count}")
    print(f"  ⏸️  WAIT:  {wait_count}")
    print(f"  📊 HOLD:  {hold_count}")
    
    print(f"\nStrategy Details:")
    for name, result in results:
        if result:
            rec = result.recommendation.value
            conf = result.confidence
            icon = "✅" if rec == "BUY" else "❌" if rec == "SELL" else "⏸️" if rec == "WAIT" else "📊"
            print(f"  {icon} {name:25s} {rec:6s} ({conf:3d}%)")
        else:
            print(f"  ❌ {name:25s} ERROR")
    
    print(f"\n{'='*70}")

if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    test_all_strategies(ticker)

