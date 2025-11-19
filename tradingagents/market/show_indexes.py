"""
Show Market Indexes - Display market indexes and analysis

Shows all tracked market indexes with current values, trends, sector rotation,
and market regime analysis. Provides context for trading decisions.
"""

from tradingagents.market.index_tracker import MarketIndexTracker
from tradingagents.utils.cli_formatter import CLIFormatter
from datetime import datetime


class IndexDisplay:
    """Display market index information."""

    def __init__(self):
        self.tracker = MarketIndexTracker()
        self.formatter = CLIFormatter()

    def show_all_indexes(self, refresh: bool = False):
        """Show all market indexes with analysis.

        Args:
            refresh: If True, force refresh of index data (default: False, uses cache if available)
        """
        print(f"\n{self.formatter.CYAN}{self.formatter.BOLD}Market Indexes & Analysis{self.formatter.NC}\n")
        
        if refresh:
            print(f"{self.formatter.YELLOW}Refreshing index data from yfinance...{self.formatter.NC}\n")
        else:
            print(f"{self.formatter.YELLOW}Fetching data from yfinance...{self.formatter.NC}\n")

        # Get all index data (tracker always fetches fresh, but we can add cache later)
        data = self.tracker.get_all_indexes()

        # Display market summary first
        self._display_market_summary(data['market_summary'])

        # Display market regime
        self._display_market_regime(data['market_regime'])

        # Display sector rotation
        self._display_sector_rotation(data['sector_rotation'])

        # Display indexes by category
        self._display_indexes_by_category(data['categories'])

        # Display next steps
        self._display_next_steps(data['market_regime'])

    def _display_market_summary(self, summary):
        """Display overall market summary."""

        print(f"{self.formatter.BOLD}{self.formatter.BLUE}═══ MARKET SUMMARY ═══{self.formatter.NC}\n")

        breadth = summary.get('breadth_pct', 0)
        indexes_up = summary.get('indexes_up', 0)
        indexes_down = summary.get('indexes_down', 0)

        breadth_color = self.formatter.GREEN if breadth >= 67 else (
            self.formatter.RED if breadth <= 33 else self.formatter.YELLOW
        )

        print(f"{self.formatter.WHITE}Market Breadth:{self.formatter.NC}")
        print(f"  {breadth_color}{breadth:.0f}%{self.formatter.NC} of major indexes are up")
        print(f"  {self.formatter.GREEN}↑ {indexes_up}{self.formatter.NC} indexes up  |  "
              f"{self.formatter.RED}↓ {indexes_down}{self.formatter.NC} indexes down\n")

        # Performance
        day_change = summary.get('avg_day_change_pct', 0)
        week_change = summary.get('avg_week_change_pct', 0)
        month_change = summary.get('avg_month_change_pct', 0)

        day_color = self.formatter.GREEN if day_change > 0 else self.formatter.RED
        week_color = self.formatter.GREEN if week_change > 0 else self.formatter.RED
        month_color = self.formatter.GREEN if month_change > 0 else self.formatter.RED

        print(f"{self.formatter.WHITE}Average Performance:{self.formatter.NC}")
        print(f"  Today:  {day_color}{day_change:+.2f}%{self.formatter.NC}")
        print(f"  Week:   {week_color}{week_change:+.2f}%{self.formatter.NC}")
        print(f"  Month:  {month_color}{month_change:+.2f}%{self.formatter.NC}\n")

        # VIX / Sentiment
        vix = summary.get('vix_level', 15)
        sentiment = summary.get('sentiment', 'CALM')
        strength = summary.get('market_strength', 'MIXED')

        vix_color = self.formatter.GREEN if vix < 20 else (
            self.formatter.YELLOW if vix < 30 else self.formatter.RED
        )

        sentiment_emoji = {
            'COMPLACENT': '😌',
            'CALM': '😊',
            'NERVOUS': '😬',
            'FEARFUL': '😱'
        }.get(sentiment, '😐')

        strength_color = self.formatter.GREEN if 'BULLISH' in strength else (
            self.formatter.RED if 'BEARISH' in strength else self.formatter.YELLOW
        )

        print(f"{self.formatter.WHITE}Market Sentiment:{self.formatter.NC}")
        print(f"  VIX Level: {vix_color}{vix:.2f}{self.formatter.NC} - {sentiment_emoji} {sentiment}")
        print(f"  Market Strength: {strength_color}{strength}{self.formatter.NC}\n")

    def _display_market_regime(self, regime):
        """Display market regime analysis."""

        print(f"{self.formatter.BOLD}{self.formatter.BLUE}═══ MARKET REGIME ═══{self.formatter.NC}\n")

        regime_type = regime.get('regime', 'NEUTRAL_CHOPPY')
        trend = regime.get('trend', 'NEUTRAL')
        volatility = regime.get('volatility_regime', 'NORMAL_VOLATILITY')
        recommendation = regime.get('recommendation', '')

        # Regime emoji and color
        regime_info = {
            'BULL_MARKET': ('🐂', self.formatter.GREEN, 'Bull Market'),
            'BEAR_MARKET': ('🐻', self.formatter.RED, 'Bear Market'),
            'HIGH_VOLATILITY_ENVIRONMENT': ('⚡', self.formatter.YELLOW, 'High Volatility'),
            'NEUTRAL_CHOPPY': ('〰️', self.formatter.YELLOW, 'Neutral/Choppy'),
        }

        emoji, color, display_name = regime_info.get(regime_type, ('ℹ️', self.formatter.YELLOW, regime_type))

        print(f"{self.formatter.WHITE}Current Regime:{self.formatter.NC}")
        print(f"  {color}{emoji} {display_name}{self.formatter.NC}\n")

        print(f"{self.formatter.WHITE}Details:{self.formatter.NC}")
        print(f"  Trend: {trend}")
        print(f"  Volatility: {volatility}")
        print(f"  VIX: {regime.get('vix_level', 0):.2f}\n")

        print(f"{self.formatter.WHITE}Trading Recommendation:{self.formatter.NC}")
        print(f"  {color}{recommendation}{self.formatter.NC}\n")

    def _display_sector_rotation(self, rotation):
        """Display sector rotation analysis."""

        print(f"{self.formatter.BOLD}{self.formatter.BLUE}═══ SECTOR ROTATION ═══{self.formatter.NC}\n")

        signal = rotation.get('rotation_signal', 'UNKNOWN')

        # Rotation signal interpretation
        signal_info = {
            'DEFENSIVE_ROTATION': ('🛡️', self.formatter.YELLOW, 'Defensive Rotation (Risk-Off)',
                                   'Investors rotating to defensive sectors - market caution'),
            'CYCLICAL_ROTATION': ('🚀', self.formatter.GREEN, 'Cyclical Rotation (Risk-On)',
                                  'Investors rotating to cyclical sectors - market confidence'),
            'MIXED': ('🔀', self.formatter.YELLOW, 'Mixed Rotation',
                     'No clear rotation pattern - mixed signals'),
            'UNKNOWN': ('❓', self.formatter.YELLOW, 'Unknown',
                       'Insufficient data for rotation analysis'),
        }

        emoji, color, display_name, interpretation = signal_info.get(
            signal, ('ℹ️', self.formatter.YELLOW, signal, 'Analyzing sector trends'))

        print(f"{self.formatter.WHITE}Rotation Signal:{self.formatter.NC}")
        print(f"  {color}{emoji} {display_name}{self.formatter.NC}")
        print(f"  {interpretation}\n")

        # Leaders
        leaders = rotation.get('leaders', [])
        if leaders:
            print(f"{self.formatter.GREEN}Leading Sectors (Top 3):{self.formatter.NC}")
            for i, sector in enumerate(leaders, 1):
                month_change = sector.get('month_change', 0)
                week_change = sector.get('week_change', 0)
                trend = sector.get('trend', 'NEUTRAL')

                trend_emoji = '📈' if trend == 'UPTREND' else ('📉' if trend == 'DOWNTREND' else '➡️')

                print(f"  {i}. {sector.get('name', 'Unknown')} ({sector.get('symbol', '')})")
                print(f"     Month: {self.formatter.GREEN}{month_change:+.2f}%{self.formatter.NC}  |  "
                      f"Week: {week_change:+.2f}%  |  {trend_emoji} {trend}")
            print()

        # Laggards
        laggards = rotation.get('laggards', [])
        if laggards:
            print(f"{self.formatter.RED}Lagging Sectors (Bottom 3):{self.formatter.NC}")
            for i, sector in enumerate(reversed(laggards), 1):
                month_change = sector.get('month_change', 0)
                week_change = sector.get('week_change', 0)
                trend = sector.get('trend', 'NEUTRAL')

                trend_emoji = '📈' if trend == 'UPTREND' else ('📉' if trend == 'DOWNTREND' else '➡️')

                print(f"  {i}. {sector.get('name', 'Unknown')} ({sector.get('symbol', '')})")
                print(f"     Month: {self.formatter.RED}{month_change:+.2f}%{self.formatter.NC}  |  "
                      f"Week: {week_change:+.2f}%  |  {trend_emoji} {trend}")
            print()

    def _display_indexes_by_category(self, categories):
        """Display indexes organized by category."""

        print(f"{self.formatter.BOLD}{self.formatter.BLUE}═══ INDEX DETAILS ═══{self.formatter.NC}\n")

        # Define category order
        category_order = [
            'Broad Market',
            'Volatility',
            'Sector',
            'International',
            'Fixed Income',
            'Commodities'
        ]

        for category in category_order:
            indexes = categories.get(category, [])
            if not indexes:
                continue

            print(f"{self.formatter.BOLD}{self.formatter.CYAN}{category}:{self.formatter.NC}")

            for index in indexes:
                symbol = index.get('symbol', '')
                name = index.get('name', '')
                price = index.get('price', 0)
                day_change = index.get('day_change_pct', 0)
                week_change = index.get('week_change_pct', 0)
                month_change = index.get('month_change_pct', 0)
                trend = index.get('trend', 'NEUTRAL')

                day_color = self.formatter.GREEN if day_change > 0 else self.formatter.RED
                week_color = self.formatter.GREEN if week_change > 0 else self.formatter.RED
                month_color = self.formatter.GREEN if month_change > 0 else self.formatter.RED

                trend_emoji = '📈' if trend == 'UPTREND' else ('📉' if trend == 'DOWNTREND' else '➡️')

                print(f"  {symbol:8} {name:25} ${price:10.2f}")
                print(f"           Day: {day_color}{day_change:+6.2f}%{self.formatter.NC}  |  "
                      f"Week: {week_color}{week_change:+6.2f}%{self.formatter.NC}  |  "
                      f"Month: {month_color}{month_change:+6.2f}%{self.formatter.NC}  |  "
                      f"{trend_emoji} {trend}")

            print()

    def _display_next_steps(self, regime):
        """Display actionable next steps based on regime."""

        print(f"{self.formatter.BOLD}{self.formatter.BLUE}═══ NEXT STEPS & RECOMMENDATIONS ═══{self.formatter.NC}\n")

        regime_type = regime.get('regime', 'NEUTRAL_CHOPPY')

        if regime_type == 'BULL_MARKET':
            print(f"{self.formatter.GREEN}Bull Market Strategy:{self.formatter.NC}")
            print("  1. Focus on cyclical sectors (Technology, Financials, Consumer Discretionary)")
            print("  2. Look for stocks breaking to new highs with strong volume")
            print("  3. Use pullbacks to VWAP or MA 20 as entry opportunities")
            print("  4. Consider momentum strategies and trend following")
            print("  5. Increase position sizes (but maintain risk management)\n")

            print(f"{self.formatter.WHITE}Screening Criteria:{self.formatter.NC}")
            print("  • RSI 40-60 (healthy momentum)")
            print("  • Price > MA 20 > MA 50 > MA 200 (aligned trend)")
            print("  • MACD bullish crossover")
            print("  • Volume > 1.3x average")
            print("  • Near VWAP for entry timing\n")

        elif regime_type == 'BEAR_MARKET':
            print(f"{self.formatter.RED}Bear Market Strategy:{self.formatter.NC}")
            print("  1. Focus on defensive sectors (Utilities, Consumer Staples, Healthcare)")
            print("  2. Prioritize quality stocks with strong fundamentals")
            print("  3. Reduce position sizes significantly")
            print("  4. Use tight stops and quick profit-taking")
            print("  5. Consider raising cash levels\n")

            print(f"{self.formatter.WHITE}Screening Criteria:{self.formatter.NC}")
            print("  • Look for RSI < 30 (deeply oversold)")
            print("  • Strong fundamentals (low debt, consistent earnings)")
            print("  • Dividend-paying stocks for income")
            print("  • Price near pivot S2/S3 for value entries")
            print("  • Avoid catching falling knives - wait for reversal confirmation\n")

        elif regime_type == 'HIGH_VOLATILITY_ENVIRONMENT':
            print(f"{self.formatter.YELLOW}High Volatility Strategy:{self.formatter.NC}")
            print("  1. Reduce position sizes by 50%")
            print("  2. Use wider stops (2-3x normal ATR)")
            print("  3. Avoid new positions unless conviction is very high")
            print("  4. Focus on larger-cap, more liquid stocks")
            print("  5. Consider waiting on the sidelines\n")

            print(f"{self.formatter.WHITE}Screening Criteria:{self.formatter.NC}")
            print("  • Focus on large-cap only (> $10B market cap)")
            print("  • Look for BB squeeze patterns (calm before storm)")
            print("  • Wait for VIX to drop below 25 before aggressive entries")
            print("  • Use options for defined-risk positions")
            print("  • Prioritize cash preservation\n")

        else:  # NEUTRAL_CHOPPY
            print(f"{self.formatter.YELLOW}Neutral/Choppy Market Strategy:{self.formatter.NC}")
            print("  1. Focus on stock-specific opportunities (stock picking)")
            print("  2. Use range-trading strategies")
            print("  3. Look for sector rotation opportunities")
            print("  4. Quick profit-taking (don't be greedy)")
            print("  5. Maintain balanced portfolio exposure\n")

            print(f"{self.formatter.WHITE}Screening Criteria:{self.formatter.NC}")
            print("  • Look for stocks with clear support/resistance (pivot points)")
            print("  • RSI divergence patterns for reversal trades")
            print("  • Fibonacci retracements for entry timing")
            print("  • Focus on leading sectors from rotation analysis")
            print("  • Use pattern recognition for high-probability setups\n")

        # Universal recommendations
        print(f"{self.formatter.BOLD}Universal Best Practices:{self.formatter.NC}")
        print("  • Always check indicator combinations (don't rely on single indicator)")
        print("  • Confirm signals with volume (> 1.3x average minimum)")
        print("  • Use VWAP for institutional context")
        print("  • Set stops at pivot levels or Fibonacci retracements")
        print("  • Monitor market regime daily - adjust strategy accordingly\n")

        # Commands to use - mapped to recommendations
        print(f"{self.formatter.CYAN}Commands to Check These Recommendations:{self.formatter.NC}\n")
        
        if regime_type == 'NEUTRAL_CHOPPY':
            print(f"{self.formatter.YELLOW}For Stock Picking & Range Trading:{self.formatter.NC}")
            print(f"  {self.formatter.WHITE}./quick_run.sh screener{self.formatter.NC}              - Find stock-specific opportunities")
            print(f"  {self.formatter.WHITE}./quick_run.sh indicators TICKER{self.formatter.NC}        - View pivot points & support/resistance")
            print(f"  {self.formatter.WHITE}./quick_run.sh top{self.formatter.NC}                     - Top 5 opportunities\n")
            
            print(f"{self.formatter.YELLOW}For RSI Divergence & Fibonacci:{self.formatter.NC}")
            print(f"  {self.formatter.WHITE}./quick_run.sh indicators TICKER{self.formatter.NC}        - Shows RSI divergence & Fibonacci levels")
            print(f"  {self.formatter.WHITE}./quick_run.sh analyze TICKER{self.formatter.NC}           - Entry timing with Fibonacci retracements\n")
            
            print(f"{self.formatter.YELLOW}For Sector Rotation:{self.formatter.NC}")
            print(f"  {self.formatter.WHITE}./quick_run.sh indexes{self.formatter.NC}                 - View leading sectors (already shown above)")
            print(f"  {self.formatter.WHITE}./quick_run.sh screener{self.formatter.NC}                - Stocks from leading sectors\n")
            
            print(f"{self.formatter.YELLOW}For Indicator Combinations & Volume:{self.formatter.NC}")
            print(f"  {self.formatter.WHITE}./quick_run.sh indicators TICKER{self.formatter.NC}        - All indicators + volume confirmation")
            print(f"  {self.formatter.WHITE}./quick_run.sh analyze TICKER{self.formatter.NC}           - VWAP analysis & stop loss levels\n")
            
            print(f"{self.formatter.YELLOW}For Pattern Recognition:{self.formatter.NC}")
            print(f"  {self.formatter.WHITE}./quick_run.sh indicators TICKER{self.formatter.NC}        - Pattern recognition signals")
            print(f"  {self.formatter.WHITE}./quick_run.sh analyze TICKER{self.formatter.NC}           - High-probability setup detection\n")
        else:
            print(f"{self.formatter.YELLOW}Find Stocks Matching Current Regime:{self.formatter.NC}")
            print(f"  {self.formatter.WHITE}./quick_run.sh screener{self.formatter.NC}              - Screener with sector analysis")
            print(f"  {self.formatter.WHITE}./quick_run.sh top{self.formatter.NC}                     - Top 5 opportunities\n")
            
            print(f"{self.formatter.YELLOW}Check Indicators & Entry Levels:{self.formatter.NC}")
            print(f"  {self.formatter.WHITE}./quick_run.sh indicators TICKER{self.formatter.NC}        - All technical indicators")
            print(f"  {self.formatter.WHITE}./quick_run.sh analyze TICKER{self.formatter.NC}           - Entry/exit recommendations\n")
            
            print(f"{self.formatter.YELLOW}Daily Monitoring:{self.formatter.NC}")
            print(f"  {self.formatter.WHITE}./quick_run.sh morning{self.formatter.NC}                 - Full morning briefing")
            print(f"  {self.formatter.WHITE}./quick_run.sh digest{self.formatter.NC}                  - Quick market digest\n")
        
        print(f"{self.formatter.CYAN}📖 Full Guide:{self.formatter.NC} See docs/STRATEGY_RECOMMENDATIONS_COMMANDS.md for complete command reference")
        print()


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description='Show market indexes and analysis')
    parser.add_argument(
        '--refresh',
        action='store_true',
        help='Force refresh of index data (default: uses cache if available)'
    )
    args = parser.parse_args()
    
    display = IndexDisplay()
    display.show_all_indexes(refresh=args.refresh)


if __name__ == '__main__':
    main()
