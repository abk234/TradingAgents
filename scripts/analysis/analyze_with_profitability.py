#!/usr/bin/env python3
"""
Analyze Stock with Profitability Features

Simple script to analyze a stock with all profitability improvements enabled.
"""

import sys
from datetime import date
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

def analyze_stock(ticker: str, portfolio_value: float = 100000):
    """
    Analyze a stock with all profitability features enabled.
    
    Args:
        ticker: Stock ticker symbol (e.g., "AAPL", "NVDA")
        portfolio_value: Your portfolio value in USD
    """
    print("="*70)
    print("TRADINGAGENTS ANALYSIS WITH PROFITABILITY FEATURES")
    print("="*70)
    print(f"\nAnalyzing: {ticker}")
    print(f"Portfolio Value: ${portfolio_value:,.2f}")
    print(f"Analysis Date: {date.today()}")
    print("\n" + "-"*70)
    
    # Load config (profitability features already enabled by default)
    config = DEFAULT_CONFIG.copy()
    config["portfolio_value"] = portfolio_value
    
    # Confirm features are enabled
    print("\n✅ Profitability Features Status:")
    print(f"   Market Regime Detection: {config.get('enable_regime_detection', False)}")
    print(f"   Sector Rotation: {config.get('enable_sector_rotation', False)}")
    print(f"   Correlation Checks: {config.get('enable_correlation_check', False)}")
    print(f"   All Features Enabled: {config.get('enable_profitability_features', False)}")
    
    if not config.get('enable_profitability_features'):
        print("\n⚠️  WARNING: Profitability features are disabled!")
        print("   Edit tradingagents/default_config.py to enable them.")
        return
    
    print("\n" + "-"*70)
    print("Running Analysis...")
    print("-"*70 + "\n")
    
    try:
        # Initialize trading graph
        ta = TradingAgentsGraph(debug=False, config=config)
        
        # Run analysis
        analysis_date = date.today().strftime("%Y-%m-%d")
        final_state, decision = ta.propagate(
            ticker, 
            analysis_date, 
            store_analysis=True
        )
        
        # Display results
        print("\n" + "="*70)
        print("ANALYSIS RESULTS")
        print("="*70)
        print(f"\nDecision: {decision}")
        
        # Show profitability enhancements
        if "profitability_enhancements" in final_state:
            enhancements = final_state["profitability_enhancements"]
            
            print("\n" + "-"*70)
            print("PROFITABILITY ENHANCEMENTS")
            print("-"*70)
            
            # Market Regime
            if enhancements.get('market_regime'):
                print(f"\n📊 Market Context:")
                print(f"   Regime: {enhancements['market_regime'].upper()}")
                print(f"   Volatility: {enhancements.get('volatility_regime', 'N/A').upper()}")
            
            # Sector Action
            if enhancements.get('sector_action'):
                action = enhancements['sector_action']
                icon = "📈" if action == "OVERWEIGHT" else "📉" if action == "UNDERWEIGHT" else "➡️"
                print(f"\n{icon} Sector Recommendation: {action}")
            
            # Correlation Risk
            if enhancements.get('correlation_risk'):
                corr = enhancements['correlation_risk']
                status = "✓ Safe" if corr['is_safe'] else "⚠ High Risk"
                print(f"\n🔗 Correlation Risk: {status}")
                print(f"   Max Correlation: {corr['max_correlation']:.2f}")
                if corr['correlations']:
                    print(f"   Correlations: {corr['correlations']}")
            
            # Position Sizing
            if enhancements.get('position_sizing'):
                sizing = enhancements['position_sizing']
                print(f"\n💰 Position Sizing:")
                print(f"   Recommended: {sizing['position_size_pct']:.1f}% of portfolio")
                print(f"   Amount: ${sizing['recommended_amount']:,.2f}")
                print(f"   Shares: {sizing['recommended_shares']}")
                print(f"   Reasoning: {sizing['sizing_reasoning']}")
            
            # Exit Strategy
            if enhancements.get('exit_strategy'):
                exit_strat = enhancements['exit_strategy']
                print(f"\n🚪 Exit Strategy:")
                print(f"   Trailing Stop: ${exit_strat['trailing_stop']:.2f}")
                print(f"   Partial Profit Levels:")
                for level, info in exit_strat['partial_profit_levels'].items():
                    print(f"     • {level}: Sell {info['sell_pct']*100:.0f}% - {info['reasoning']}")
        
        print("\n" + "="*70)
        print("Analysis Complete!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # Get ticker from command line or use default
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    
    # Get portfolio value from command line or use default
    portfolio_value = float(sys.argv[2]) if len(sys.argv) > 2 else 100000
    
    analyze_stock(ticker, portfolio_value)

