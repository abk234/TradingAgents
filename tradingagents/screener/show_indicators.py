"""
Show Indicators - Display current indicator values with interpretations

Displays all technical indicators with their current values, ranges, and interpretations.
Helps traders understand what each indicator means and how to use them.
"""

import sys
from typing import Optional
from tradingagents.database import get_db_connection
from tradingagents.utils.cli_formatter import CLIFormatter
from tradingagents.utils import display_next_steps
from tradingagents.screener.indicators import TechnicalIndicators
from tradingagents.screener.pattern_recognition import PatternRecognition
import pandas as pd
from datetime import datetime, timedelta


class IndicatorDisplay:
    """Display indicator values with interpretations."""

    def __init__(self):
        self.formatter = CLIFormatter()
        self.db = get_db_connection()

    def show_all_indicators(self, ticker: Optional[str] = None):
        """Show all indicators with interpretations."""

        if ticker:
            self._show_ticker_indicators(ticker)
        else:
            self._show_indicator_guide()

    def _show_ticker_indicators(self, ticker: str):
        """Show indicator values for a specific ticker."""

        print(f"\n{self.formatter.CYAN}{self.formatter.BOLD}Technical Indicators for {ticker}{self.formatter.NC}\n")

        # Get latest scan data
        query = """
            SELECT
                t.symbol,
                t.sector,
                ds.price as current_price,
                ds.priority_score,
                ds.technical_signals,
                ds.scan_date
            FROM daily_scans ds
            JOIN tickers t ON ds.ticker_id = t.ticker_id
            WHERE t.symbol = %s
            ORDER BY ds.scan_date DESC
            LIMIT 1
        """

        result = self.db.execute_dict_query(query, (ticker,))

        if not result:
            print(f"{self.formatter.RED}No data found for {ticker}{self.formatter.NC}")
            print(f"{self.formatter.YELLOW}Run: ./quick_run.sh screener{self.formatter.NC} to scan stocks first")
            return

        data = result[0]
        signals = data.get('technical_signals', {})
        current_price_raw = data.get('current_price', 0)
        # Convert to float to avoid Decimal/float type errors
        current_price = float(current_price_raw) if current_price_raw else 0.0

        print(f"{self.formatter.GREEN}Last Scan:{self.formatter.NC} {data.get('scan_date', 'N/A')}")
        print(f"{self.formatter.GREEN}Sector:{self.formatter.NC} {data.get('sector', 'N/A')}")
        print(f"{self.formatter.GREEN}Current Price:{self.formatter.NC} ${current_price:.2f}")
        print(f"{self.formatter.GREEN}Priority Score:{self.formatter.NC} {data.get('priority_score', 0):.1f}/100\n")

        # === MOMENTUM INDICATORS ===
        print(f"{self.formatter.BOLD}{self.formatter.BLUE}═══ MOMENTUM INDICATORS ═══{self.formatter.NC}\n")

        # RSI
        rsi = signals.get('rsi')
        if rsi:
            rsi_interp = self._interpret_rsi(rsi)
            print(f"{self.formatter.WHITE}RSI (14):{self.formatter.NC}")
            print(f"  Value: {rsi_interp['color']}{rsi:.2f}{self.formatter.NC}")
            print(f"  Condition: {rsi_interp['condition']}")
            print(f"  Signal: {rsi_interp['signal']}")
            print(f"  Interpretation: {rsi_interp['interpretation']}\n")

        # RSI Divergence
        if signals.get('rsi_bullish_divergence'):
            strength = signals.get('rsi_divergence_strength', 0)
            print(f"{self.formatter.GREEN}🔔 BULLISH RSI DIVERGENCE DETECTED{self.formatter.NC}")
            print(f"  Strength: {strength:.1%}")
            print(f"  Meaning: Price making lower lows but RSI making higher lows")
            print(f"  Signal: Potential reversal to upside\n")

        if signals.get('rsi_bearish_divergence'):
            strength = signals.get('rsi_divergence_strength', 0)
            print(f"{self.formatter.RED}⚠️ BEARISH RSI DIVERGENCE DETECTED{self.formatter.NC}")
            print(f"  Strength: {strength:.1%}")
            print(f"  Meaning: Price making higher highs but RSI making lower highs")
            print(f"  Signal: Potential reversal to downside\n")

        # MACD
        macd = signals.get('macd')
        macd_signal = signals.get('macd_signal')
        macd_hist = signals.get('macd_histogram')
        if macd and macd_signal:
            macd_interp = self._interpret_macd(macd, macd_signal, macd_hist)
            print(f"{self.formatter.WHITE}MACD:{self.formatter.NC}")
            print(f"  MACD Line: {macd:.4f}")
            print(f"  Signal Line: {macd_signal:.4f}")
            print(f"  Histogram: {macd_interp['hist_color']}{macd_hist:.4f}{self.formatter.NC}")
            print(f"  Trend: {macd_interp['trend']}")
            print(f"  Signal: {macd_interp['signal']}\n")

        # === TREND INDICATORS ===
        print(f"{self.formatter.BOLD}{self.formatter.BLUE}═══ TREND INDICATORS ═══{self.formatter.NC}\n")

        # Moving Averages
        ma_20 = signals.get('ma_20')
        ma_50 = signals.get('ma_50')
        ma_200 = signals.get('ma_200')

        if ma_20 or ma_50 or ma_200:
            print(f"{self.formatter.WHITE}Moving Averages:{self.formatter.NC}")
            if ma_20:
                pct_from_ma20 = ((current_price - ma_20) / ma_20) * 100
                color = self.formatter.GREEN if pct_from_ma20 > 0 else self.formatter.RED
                print(f"  MA 20: ${ma_20:.2f} ({color}{pct_from_ma20:+.2f}%{self.formatter.NC} from price)")
            if ma_50:
                pct_from_ma50 = ((current_price - ma_50) / ma_50) * 100
                color = self.formatter.GREEN if pct_from_ma50 > 0 else self.formatter.RED
                print(f"  MA 50: ${ma_50:.2f} ({color}{pct_from_ma50:+.2f}%{self.formatter.NC} from price)")
            if ma_200:
                pct_from_ma200 = ((current_price - ma_200) / ma_200) * 100
                color = self.formatter.GREEN if pct_from_ma200 > 0 else self.formatter.RED
                print(f"  MA 200: ${ma_200:.2f} ({color}{pct_from_ma200:+.2f}%{self.formatter.NC} from price)")

            # Trend alignment
            if ma_20 and ma_50 and ma_200:
                if ma_20 > ma_50 > ma_200:
                    print(f"  {self.formatter.GREEN}✓ STRONG UPTREND{self.formatter.NC} (MA 20 > MA 50 > MA 200)")
                elif ma_20 < ma_50 < ma_200:
                    print(f"  {self.formatter.RED}✗ STRONG DOWNTREND{self.formatter.NC} (MA 20 < MA 50 < MA 200)")
                else:
                    print(f"  {self.formatter.YELLOW}○ MIXED TREND{self.formatter.NC} (MAs not aligned)")
            print()

        # VWAP
        vwap = signals.get('vwap')
        if vwap:
            vwap_float = float(vwap) if vwap else 0.0
            vwap_dist = ((current_price - vwap_float) / vwap_float) * 100 if vwap_float > 0 else 0.0
            vwap_interp = self._interpret_vwap(vwap_dist)
            print(f"{self.formatter.WHITE}VWAP (Volume Weighted Avg Price):{self.formatter.NC}")
            print(f"  VWAP: ${vwap:.2f}")
            print(f"  Distance: {vwap_interp['color']}{vwap_dist:+.2f}%{self.formatter.NC}")
            print(f"  Signal: {vwap_interp['signal']}")
            print(f"  Interpretation: {vwap_interp['interpretation']}\n")

        # === VOLATILITY INDICATORS ===
        print(f"{self.formatter.BOLD}{self.formatter.BLUE}═══ VOLATILITY INDICATORS ═══{self.formatter.NC}\n")

        # Bollinger Bands
        bb_upper = signals.get('bb_upper')
        bb_middle = signals.get('bb_middle')
        bb_lower = signals.get('bb_lower')

        if bb_upper and bb_middle and bb_lower:
            bb_width = ((bb_upper - bb_lower) / bb_middle) * 100
            bb_position = ((current_price - bb_lower) / (bb_upper - bb_lower)) * 100
            bb_interp = self._interpret_bb(bb_position)

            print(f"{self.formatter.WHITE}Bollinger Bands (20, 2):{self.formatter.NC}")
            print(f"  Upper: ${bb_upper:.2f}")
            print(f"  Middle: ${bb_middle:.2f}")
            print(f"  Lower: ${bb_lower:.2f}")
            print(f"  Width: {bb_width:.2f}%")
            print(f"  Position: {bb_interp['color']}{bb_position:.1f}%{self.formatter.NC} {bb_interp['zone']}")
            print(f"  Signal: {bb_interp['signal']}\n")

        # Bollinger Band Squeeze
        if signals.get('bb_squeeze_detected'):
            squeeze_strength = signals.get('bb_squeeze_strength', 0)
            squeeze_percentile = signals.get('bb_width_percentile', 0)
            print(f"{self.formatter.YELLOW}🔥 BOLLINGER BAND SQUEEZE DETECTED{self.formatter.NC}")
            print(f"  Strength: {squeeze_strength:.1%}")
            print(f"  Width Percentile: {squeeze_percentile:.1%} (bottom {squeeze_percentile*100:.0f}%)")
            print(f"  Meaning: Volatility compression - breakout imminent")
            print(f"  Signal: Prepare for major move (direction TBD)\n")

        # ATR
        atr = signals.get('atr')
        atr_pct = signals.get('atr_pct')
        if atr and atr_pct:
            atr_interp = self._interpret_atr(atr_pct)
            print(f"{self.formatter.WHITE}ATR (Average True Range):{self.formatter.NC}")
            print(f"  ATR: ${atr:.2f}")
            print(f"  ATR %: {atr_interp['color']}{atr_pct:.2f}%{self.formatter.NC}")
            print(f"  Volatility: {atr_interp['level']}")
            print(f"  Trading Impact: {atr_interp['impact']}\n")

        # === SUPPORT/RESISTANCE ===
        print(f"{self.formatter.BOLD}{self.formatter.BLUE}═══ SUPPORT & RESISTANCE ═══{self.formatter.NC}\n")

        # Pivot Points
        pivot = signals.get('pivot_point')
        if pivot:
            print(f"{self.formatter.WHITE}Pivot Points (Floor Trader):{self.formatter.NC}")
            print(f"  R3: ${signals.get('pivot_r3', 0):.2f}")
            print(f"  R2: ${signals.get('pivot_r2', 0):.2f}")
            print(f"  R1: ${signals.get('pivot_r1', 0):.2f}")
            print(f"  {self.formatter.BOLD}PP: ${pivot:.2f}{self.formatter.NC}")
            print(f"  S1: ${signals.get('pivot_s1', 0):.2f}")
            print(f"  S2: ${signals.get('pivot_s2', 0):.2f}")
            print(f"  S3: ${signals.get('pivot_s3', 0):.2f}")

            pivot_zone = self._identify_pivot_zone(current_price, signals)
            print(f"  {self.formatter.YELLOW}Current Zone:{self.formatter.NC} {pivot_zone}\n")

        # Fibonacci Levels
        fib_618 = signals.get('fib_618')
        if fib_618:
            print(f"{self.formatter.WHITE}Fibonacci Retracement Levels:{self.formatter.NC}")
            print(f"  Swing High: ${signals.get('fib_swing_high', 0):.2f}")
            print(f"  23.6%: ${signals.get('fib_236', 0):.2f}")
            print(f"  38.2%: ${signals.get('fib_382', 0):.2f}")
            print(f"  50.0%: ${signals.get('fib_500', 0):.2f}")
            print(f"  {self.formatter.YELLOW}61.8% (Golden):{self.formatter.NC} ${fib_618:.2f}")
            print(f"  78.6%: ${signals.get('fib_786', 0):.2f}")
            print(f"  Swing Low: ${signals.get('fib_swing_low', 0):.2f}")

            nearest_fib = self._find_nearest_fib(current_price, signals)
            if nearest_fib:
                print(f"  {self.formatter.GREEN}Nearest Level:{self.formatter.NC} {nearest_fib}\n")

        # === VOLUME ===
        print(f"{self.formatter.BOLD}{self.formatter.BLUE}═══ VOLUME ANALYSIS ═══{self.formatter.NC}\n")

        volume_ratio = signals.get('volume_ratio')
        if volume_ratio:
            vol_interp = self._interpret_volume(volume_ratio)
            print(f"{self.formatter.WHITE}Volume Ratio (vs 20-day avg):{self.formatter.NC}")
            print(f"  Ratio: {vol_interp['color']}{volume_ratio:.2f}x{self.formatter.NC}")
            print(f"  Level: {vol_interp['level']}")
            print(f"  Signal: {vol_interp['signal']}\n")

        # === VOLUME PROFILE (Phase 3) ===
        poc = signals.get('vp_poc')
        if poc:
            print(f"{self.formatter.BOLD}{self.formatter.BLUE}═══ VOLUME PROFILE (PHASE 3) ═══{self.formatter.NC}\n")

            vah = signals.get('vp_vah')
            val = signals.get('vp_val')
            profile_position = signals.get('vp_profile_position', 'UNKNOWN')
            position_signal = signals.get('vp_position_signal', '')
            distance_to_poc = signals.get('vp_distance_to_poc_pct', 0)

            print(f"{self.formatter.WHITE}Volume Profile Levels:{self.formatter.NC}")
            print(f"  VAH (Value Area High): ${vah:.2f} - Top of 70% volume")
            print(f"  {self.formatter.YELLOW}POC (Point of Control):{self.formatter.NC} ${poc:.2f} - Highest volume (strongest S/R)")
            print(f"  VAL (Value Area Low):  ${val:.2f} - Bottom of 70% volume\n")

            # Position interpretation
            pos_color = self.formatter.GREEN if 'BELOW' in profile_position else (
                self.formatter.RED if 'ABOVE' in profile_position else self.formatter.YELLOW
            )

            print(f"{self.formatter.WHITE}Current Position:{self.formatter.NC}")
            print(f"  Zone: {pos_color}{profile_position}{self.formatter.NC}")
            print(f"  Distance to POC: {distance_to_poc:+.2f}%")
            print(f"  Signal: {position_signal}\n")

            print(f"{self.formatter.WHITE}Professional Interpretation:{self.formatter.NC}")
            if 'BELOW_VALUE_AREA' in profile_position:
                print(f"  {self.formatter.GREEN}✓ BULLISH{self.formatter.NC} - Price below fair value")
                print(f"  Institutions likely to buy at these levels")
                print(f"  High probability bounce to VAL (${val:.2f})")
            elif 'ABOVE_VALUE_AREA' in profile_position:
                print(f"  {self.formatter.RED}✗ BEARISH{self.formatter.NC} - Price above fair value")
                print(f"  Institutions likely to sell at these levels")
                print(f"  High probability pullback to VAH (${vah:.2f})")
            elif 'AT_POC' in profile_position:
                print(f"  {self.formatter.YELLOW}○ NEUTRAL{self.formatter.NC} - Price at highest volume")
                print(f"  Expect consolidation or tight range")
            else:
                print(f"  {self.formatter.YELLOW}○ FAIR VALUE{self.formatter.NC} - Price within normal range")
                print(f"  Watch for breakout from value area")
            print()

        # === ORDER FLOW (Phase 3) ===
        of_signal = signals.get('of_signal')
        if of_signal:
            print(f"{self.formatter.BOLD}{self.formatter.BLUE}═══ ORDER FLOW & INSTITUTIONAL ACTIVITY (PHASE 3) ═══{self.formatter.NC}\n")

            institutional_activity = signals.get('of_institutional_activity', 'UNKNOWN')
            signal_strength = signals.get('of_signal_strength', 0)
            buying_pct = signals.get('of_buying_pct', 0)
            selling_pct = signals.get('of_selling_pct', 0)
            volume_spike = signals.get('of_volume_spike', False)

            # Color code based on signal
            if 'BULLISH' in of_signal or 'ACCUMULATION' in of_signal:
                signal_color = self.formatter.GREEN
                signal_icon = "📈"
            elif 'BEARISH' in of_signal or 'DISTRIBUTION' in of_signal:
                signal_color = self.formatter.RED
                signal_icon = "📉"
            else:
                signal_color = self.formatter.YELLOW
                signal_icon = "➡️"

            print(f"{self.formatter.WHITE}Order Flow Signal:{self.formatter.NC}")
            print(f"  {signal_color}{signal_icon} {of_signal}{self.formatter.NC}")
            print(f"  Institutional Activity: {institutional_activity}")
            print(f"  Signal Strength: {signal_strength:.0%}\n")

            print(f"{self.formatter.WHITE}Buying vs Selling Pressure:{self.formatter.NC}")
            buying_color = self.formatter.GREEN if buying_pct > 50 else self.formatter.RED
            selling_color = self.formatter.RED if selling_pct > 50 else self.formatter.GREEN

            print(f"  Buying:  {buying_color}{buying_pct:.1f}%{self.formatter.NC}")
            print(f"  Selling: {selling_color}{selling_pct:.1f}%{self.formatter.NC}\n")

            if volume_spike:
                print(f"{self.formatter.YELLOW}🔥 VOLUME SPIKE DETECTED{self.formatter.NC} - Unusual institutional activity\n")

            # Interpretation
            print(f"{self.formatter.WHITE}Professional Interpretation:{self.formatter.NC}")
            if institutional_activity == 'ACCUMULATION':
                print(f"  {self.formatter.GREEN}✓ ACCUMULATION{self.formatter.NC} - Smart money buying")
                print(f"  Price stable/down but volume increasing = institutions loading")
                print(f"  Signal: STRONG BUY - follow the smart money")
            elif institutional_activity == 'DISTRIBUTION':
                print(f"  {self.formatter.RED}✗ DISTRIBUTION{self.formatter.NC} - Smart money selling")
                print(f"  Price stable/up but volume increasing = institutions unloading")
                print(f"  Signal: STRONG SELL - exit before retail realizes")
            elif buying_pct > 65:
                print(f"  {self.formatter.GREEN}Strong buying pressure{self.formatter.NC} - bullish momentum")
            elif selling_pct > 65:
                print(f"  {self.formatter.RED}Strong selling pressure{self.formatter.NC} - bearish momentum")
            else:
                print(f"  Balanced order flow - no clear institutional direction")
            print()

        # === MULTI-TIMEFRAME ANALYSIS (Phase 3) ===
        mtf_alignment = signals.get('mtf_alignment')
        if mtf_alignment:
            print(f"{self.formatter.BOLD}{self.formatter.BLUE}═══ MULTI-TIMEFRAME ANALYSIS (PHASE 3) ═══{self.formatter.NC}\n")

            mtf_signal = signals.get('mtf_signal', 'NEUTRAL')
            mtf_confidence = signals.get('mtf_confidence', 0)
            daily_trend = signals.get('mtf_daily_trend', 'NEUTRAL')
            weekly_trend = signals.get('mtf_weekly_trend', 'NEUTRAL')
            monthly_trend = signals.get('mtf_monthly_trend', 'NEUTRAL')
            mtf_recommendation = signals.get('mtf_recommendation', '')

            # Alignment interpretation
            if 'PERFECT_BULLISH' in mtf_alignment:
                align_color = self.formatter.GREEN
                align_icon = "🚀"
            elif 'PERFECT_BEARISH' in mtf_alignment:
                align_color = self.formatter.RED
                align_icon = "🔻"
            elif 'PULLBACK_IN_UPTREND' in mtf_alignment:
                align_color = self.formatter.GREEN
                align_icon = "✅"
            elif 'BOUNCE_IN_DOWNTREND' in mtf_alignment:
                align_color = self.formatter.RED
                align_icon = "❌"
            else:
                align_color = self.formatter.YELLOW
                align_icon = "➡️"

            print(f"{self.formatter.WHITE}Timeframe Alignment:{self.formatter.NC}")
            print(f"  {align_color}{align_icon} {mtf_alignment}{self.formatter.NC}")
            print(f"  Signal: {mtf_signal}")
            print(f"  Confidence: {mtf_confidence:.0%}\n")

            print(f"{self.formatter.WHITE}Trend by Timeframe:{self.formatter.NC}")

            # Monthly (most important)
            monthly_icon = "📈" if monthly_trend == "UPTREND" else ("📉" if monthly_trend == "DOWNTREND" else "➡️")
            monthly_color = self.formatter.GREEN if monthly_trend == "UPTREND" else (
                self.formatter.RED if monthly_trend == "DOWNTREND" else self.formatter.YELLOW
            )
            print(f"  {self.formatter.BOLD}Monthly:{self.formatter.NC} {monthly_color}{monthly_icon} {monthly_trend}{self.formatter.NC} (Primary Direction)")

            # Weekly
            weekly_icon = "📈" if weekly_trend == "UPTREND" else ("📉" if weekly_trend == "DOWNTREND" else "➡️")
            weekly_color = self.formatter.GREEN if weekly_trend == "UPTREND" else (
                self.formatter.RED if weekly_trend == "DOWNTREND" else self.formatter.YELLOW
            )
            print(f"  Weekly:  {weekly_color}{weekly_icon} {weekly_trend}{self.formatter.NC} (Intermediate)")

            # Daily
            daily_icon = "📈" if daily_trend == "UPTREND" else ("📉" if daily_trend == "DOWNTREND" else "➡️")
            daily_color = self.formatter.GREEN if daily_trend == "UPTREND" else (
                self.formatter.RED if daily_trend == "DOWNTREND" else self.formatter.YELLOW
            )
            print(f"  Daily:   {daily_color}{daily_icon} {daily_trend}{self.formatter.NC} (Entry Timing)\n")

            print(f"{self.formatter.WHITE}Professional Recommendation:{self.formatter.NC}")
            print(f"  {mtf_recommendation}\n")

        # === PATTERN RECOGNITION ===
        print(f"{self.formatter.BOLD}{self.formatter.BLUE}═══ PATTERN RECOGNITION ═══{self.formatter.NC}\n")

        # Run pattern detection
        pattern_analysis = PatternRecognition.analyze_patterns(signals)
        detected_patterns = pattern_analysis.get('all_patterns', [])

        if detected_patterns:
            for pattern_signal in detected_patterns:
                # Convert PatternSignal dataclass to dictionary format expected by _display_pattern
                pattern_dict = {
                    'pattern': pattern_signal.pattern_name,
                    'probability': pattern_signal.probability,
                    'signal_score': pattern_signal.score,
                    'description': pattern_signal.reasoning,
                    'conditions': pattern_signal.conditions_met
                }
                self._display_pattern(pattern_dict)
        else:
            print(f"{self.formatter.YELLOW}No high-probability patterns detected{self.formatter.NC}\n")

        # === SUMMARY ===
        print(f"{self.formatter.BOLD}{self.formatter.BLUE}═══ TRADING SUMMARY ═══{self.formatter.NC}\n")

        # Overall signal score
        signal_score = pattern_analysis.get('overall_score', PatternRecognition._calculate_signal_score(signals))
        summary = self._get_trading_summary(signal_score, signals)

        print(f"{self.formatter.WHITE}Signal Score:{self.formatter.NC} {summary['score_color']}{signal_score}/10{self.formatter.NC}")
        print(f"{self.formatter.WHITE}Overall Signal:{self.formatter.NC} {summary['signal']}")
        print(f"{self.formatter.WHITE}Confidence:{self.formatter.NC} {summary['confidence']}")
        print(f"{self.formatter.WHITE}Recommendation:{self.formatter.NC} {summary['recommendation']}\n")

        # Key takeaways
        print(f"{self.formatter.BOLD}Key Takeaways:{self.formatter.NC}")
        for takeaway in summary['takeaways']:
            print(f"  • {takeaway}")
        print()
        
        # Display next steps and recommendations
        display_next_steps('indicators', context={'ticker': ticker})

    def _show_indicator_guide(self):
        """Show comprehensive indicator guide."""

        print(f"\n{self.formatter.CYAN}{self.formatter.BOLD}Technical Indicators Reference Guide{self.formatter.NC}\n")
        print(f"For detailed indicator guide, see: {self.formatter.YELLOW}docs/INDICATOR_GUIDE.md{self.formatter.NC}\n")
        print(f"{self.formatter.GREEN}Quick Reference:{self.formatter.NC}\n")

        # RSI Guide
        print(f"{self.formatter.BOLD}RSI (Relative Strength Index):{self.formatter.NC}")
        print("  < 30:  OVERSOLD - Consider buying")
        print("  30-40: Approaching oversold")
        print("  40-60: Neutral zone")
        print("  60-70: Approaching overbought")
        print("  > 70:  OVERBOUGHT - Consider selling\n")

        # MACD Guide
        print(f"{self.formatter.BOLD}MACD (Moving Average Convergence Divergence):{self.formatter.NC}")
        print("  MACD > Signal: Bullish (upward momentum)")
        print("  MACD < Signal: Bearish (downward momentum)")
        print("  Histogram > 0: Strengthening bullish")
        print("  Histogram < 0: Strengthening bearish\n")

        # VWAP Guide
        print(f"{self.formatter.BOLD}VWAP (Volume Weighted Average Price):{self.formatter.NC}")
        print("  Price < VWAP - 2%: Strong buy zone")
        print("  Price < VWAP - 1%: Buy zone")
        print("  Price within ±1%:  Fair value")
        print("  Price > VWAP + 1%: Sell zone")
        print("  Price > VWAP + 2%: Strong sell zone\n")

        # Bollinger Bands Guide
        print(f"{self.formatter.BOLD}Bollinger Bands:{self.formatter.NC}")
        print("  Position 0-20%:   Near lower band - oversold")
        print("  Position 20-40%:  Below middle - bearish")
        print("  Position 40-60%:  Neutral zone")
        print("  Position 60-80%:  Above middle - bullish")
        print("  Position 80-100%: Near upper band - overbought\n")

        # ATR Guide
        print(f"{self.formatter.BOLD}ATR (Average True Range):{self.formatter.NC}")
        print("  < 1%:  Low volatility - tight stops")
        print("  1-3%:  Normal volatility")
        print("  3-5%:  Elevated volatility - wider stops")
        print("  > 5%:  High volatility - use caution\n")

        # Volume Guide
        print(f"{self.formatter.BOLD}Volume Ratio:{self.formatter.NC}")
        print("  < 0.5x:  Very low - weak signal")
        print("  0.5-1x:  Below average")
        print("  1-1.5x:  Normal")
        print("  1.5-2x:  Above average - confirmation")
        print("  > 2x:    Unusually high - strong signal\n")

        # Pattern Guide
        print(f"{self.formatter.BOLD}Patterns:{self.formatter.NC}")
        print("  STRONG_BUY:         Multiple bullish confirmations (85%+ probability)")
        print("  BUY:                Several bullish signals (70%+ probability)")
        print("  WAIT_FOR_PULLBACK:  Bullish but overextended - wait for dip")
        print("  BREAKOUT_IMMINENT:  BB squeeze - prepare for move")
        print("  DIVERGENCE_REVERSAL: RSI divergence - trend change likely")
        print("  STRONG_SELL:        Multiple bearish confirmations\n")

        print(f"{self.formatter.CYAN}Usage:{self.formatter.NC}")
        print(f"  ./quick_run.sh indicators AAPL   - Show indicators for specific ticker")
        print(f"  ./quick_run.sh indicators         - Show this guide\n")
        
        # Display next steps and recommendations
        display_next_steps('indicators')

    # === INTERPRETATION HELPERS ===

    def _interpret_rsi(self, rsi):
        """Interpret RSI value."""
        if rsi < 30:
            return {
                'condition': 'OVERSOLD',
                'signal': 'Strong Buy Signal',
                'interpretation': 'Stock is oversold, potential reversal to upside',
                'color': self.formatter.GREEN
            }
        elif rsi < 40:
            return {
                'condition': 'Approaching Oversold',
                'signal': 'Buy Signal',
                'interpretation': 'Building support, good entry zone',
                'color': self.formatter.GREEN
            }
        elif rsi < 50:
            return {
                'condition': 'Neutral-Bearish',
                'signal': 'Hold',
                'interpretation': 'Slight bearish momentum',
                'color': self.formatter.YELLOW
            }
        elif rsi < 60:
            return {
                'condition': 'Neutral-Bullish',
                'signal': 'Hold',
                'interpretation': 'Slight bullish momentum',
                'color': self.formatter.YELLOW
            }
        elif rsi < 70:
            return {
                'condition': 'Approaching Overbought',
                'signal': 'Consider Profit Taking',
                'interpretation': 'Strong momentum but nearing overextension',
                'color': self.formatter.YELLOW
            }
        else:
            return {
                'condition': 'OVERBOUGHT',
                'signal': 'Strong Sell Signal',
                'interpretation': 'Stock is overbought, potential pullback',
                'color': self.formatter.RED
            }

    def _interpret_macd(self, macd, signal, histogram):
        """Interpret MACD values."""
        trend = "Bullish" if macd > signal else "Bearish"
        hist_color = self.formatter.GREEN if histogram > 0 else self.formatter.RED

        if macd > signal and histogram > 0:
            signal_txt = "Strong Buy - Bullish crossover with strengthening"
        elif macd > signal:
            signal_txt = "Buy - Bullish but weakening"
        elif macd < signal and histogram < 0:
            signal_txt = "Strong Sell - Bearish crossover with strengthening"
        else:
            signal_txt = "Sell - Bearish but weakening"

        return {
            'trend': trend,
            'signal': signal_txt,
            'hist_color': hist_color
        }

    def _interpret_vwap(self, distance_pct):
        """Interpret VWAP distance."""
        if distance_pct < -2:
            return {
                'signal': 'STRONG BUY',
                'interpretation': 'Well below institutional benchmark - excellent entry',
                'color': self.formatter.GREEN
            }
        elif distance_pct < -1:
            return {
                'signal': 'BUY',
                'interpretation': 'Below VWAP - good entry zone',
                'color': self.formatter.GREEN
            }
        elif distance_pct < 1:
            return {
                'signal': 'FAIR VALUE',
                'interpretation': 'Trading near institutional benchmark',
                'color': self.formatter.YELLOW
            }
        elif distance_pct < 2:
            return {
                'signal': 'SELL',
                'interpretation': 'Above VWAP - consider profit taking',
                'color': self.formatter.RED
            }
        else:
            return {
                'signal': 'STRONG SELL',
                'interpretation': 'Well above institutional benchmark - overextended',
                'color': self.formatter.RED
            }

    def _interpret_bb(self, position):
        """Interpret Bollinger Band position."""
        if position < 20:
            return {
                'zone': '(Near Lower Band)',
                'signal': 'OVERSOLD - Reversal likely',
                'color': self.formatter.GREEN
            }
        elif position < 40:
            return {
                'zone': '(Below Middle)',
                'signal': 'Bearish zone',
                'color': self.formatter.YELLOW
            }
        elif position < 60:
            return {
                'zone': '(Middle)',
                'signal': 'Neutral zone',
                'color': self.formatter.YELLOW
            }
        elif position < 80:
            return {
                'zone': '(Above Middle)',
                'signal': 'Bullish zone',
                'color': self.formatter.YELLOW
            }
        else:
            return {
                'zone': '(Near Upper Band)',
                'signal': 'OVERBOUGHT - Pullback likely',
                'color': self.formatter.RED
            }

    def _interpret_atr(self, atr_pct):
        """Interpret ATR percentage."""
        if atr_pct < 1:
            return {
                'level': 'LOW VOLATILITY',
                'impact': 'Use tight stops, normal position size',
                'color': self.formatter.GREEN
            }
        elif atr_pct < 3:
            return {
                'level': 'NORMAL VOLATILITY',
                'impact': 'Standard trading conditions',
                'color': self.formatter.YELLOW
            }
        elif atr_pct < 5:
            return {
                'level': 'ELEVATED VOLATILITY',
                'impact': 'Use wider stops, consider smaller positions',
                'color': self.formatter.YELLOW
            }
        else:
            return {
                'level': 'HIGH VOLATILITY',
                'impact': 'Use wide stops, reduce position size significantly',
                'color': self.formatter.RED
            }

    def _interpret_volume(self, ratio):
        """Interpret volume ratio."""
        if ratio < 0.5:
            return {
                'level': 'VERY LOW',
                'signal': 'Weak confirmation - signals unreliable',
                'color': self.formatter.RED
            }
        elif ratio < 1:
            return {
                'level': 'BELOW AVERAGE',
                'signal': 'Below normal - weak confirmation',
                'color': self.formatter.YELLOW
            }
        elif ratio < 1.5:
            return {
                'level': 'NORMAL',
                'signal': 'Average volume - normal confirmation',
                'color': self.formatter.YELLOW
            }
        elif ratio < 2:
            return {
                'level': 'ABOVE AVERAGE',
                'signal': 'Strong confirmation - signals reliable',
                'color': self.formatter.GREEN
            }
        else:
            return {
                'level': 'UNUSUALLY HIGH',
                'signal': 'Very strong confirmation - major interest',
                'color': self.formatter.GREEN
            }

    def _identify_pivot_zone(self, price, signals):
        """Identify which pivot zone price is in."""
        r3 = signals.get('pivot_r3', float('inf'))
        r2 = signals.get('pivot_r2', float('inf'))
        r1 = signals.get('pivot_r1', float('inf'))
        pp = signals.get('pivot_point', 0)
        s1 = signals.get('pivot_s1', 0)
        s2 = signals.get('pivot_s2', 0)
        s3 = signals.get('pivot_s3', 0)

        if price > r2:
            return f"{self.formatter.RED}Above R2 - Strong Resistance{self.formatter.NC}"
        elif price > r1:
            return f"{self.formatter.YELLOW}R1-R2 Zone - Resistance Area{self.formatter.NC}"
        elif price > pp:
            return f"{self.formatter.YELLOW}PP-R1 Zone - Bullish Territory{self.formatter.NC}"
        elif price > s1:
            return f"{self.formatter.YELLOW}S1-PP Zone - Neutral/Support{self.formatter.NC}"
        elif price > s2:
            return f"{self.formatter.GREEN}S1-S2 Zone - Support Area (Buy Zone){self.formatter.NC}"
        else:
            return f"{self.formatter.GREEN}Below S2 - Strong Support (Strong Buy){self.formatter.NC}"

    def _find_nearest_fib(self, price, signals):
        """Find nearest Fibonacci level."""
        fib_levels = {
            '23.6%': signals.get('fib_236'),
            '38.2%': signals.get('fib_382'),
            '50.0%': signals.get('fib_500'),
            '61.8% (Golden)': signals.get('fib_618'),
            '78.6%': signals.get('fib_786'),
        }

        nearest = None
        min_dist = float('inf')

        for name, level in fib_levels.items():
            if level:
                dist = abs(price - level)
                if dist < min_dist:
                    min_dist = dist
                    nearest = (name, level, dist)

        if nearest:
            pct_dist = (min_dist / price) * 100
            if pct_dist < 2:  # Within 2%
                return f"{nearest[0]} at ${nearest[1]:.2f} ({pct_dist:.2f}% away)"

        return None

    def _display_pattern(self, pattern):
        """Display a detected pattern."""
        if pattern['pattern'] == 'STRONG_BUY':
            icon = "🚀"
            color = self.formatter.GREEN
        elif pattern['pattern'] == 'BUY':
            icon = "✅"
            color = self.formatter.GREEN
        elif pattern['pattern'] == 'WAIT_FOR_PULLBACK':
            icon = "⏸️"
            color = self.formatter.YELLOW
        elif pattern['pattern'] == 'BREAKOUT_IMMINENT':
            icon = "💥"
            color = self.formatter.CYAN
        elif pattern['pattern'] == 'DIVERGENCE_REVERSAL':
            icon = "🔄"
            color = self.formatter.CYAN
        elif pattern['pattern'] == 'STRONG_SELL':
            icon = "🔻"
            color = self.formatter.RED
        else:
            icon = "ℹ️"
            color = self.formatter.YELLOW

        print(f"{color}{icon} {pattern['pattern']}{self.formatter.NC}")
        print(f"  Probability: {pattern['probability']:.0%}")
        print(f"  Signal Score: {pattern['signal_score']}/10")
        print(f"  Description: {pattern['description']}")

        if pattern['conditions']:
            print(f"  Key Conditions:")
            for cond in pattern['conditions'][:3]:  # Show top 3
                print(f"    • {cond}")
        print()

    def _get_trading_summary(self, score, signals):
        """Generate trading summary."""
        if score >= 7:
            signal = f"{self.formatter.GREEN}STRONG BUY{self.formatter.NC}"
            confidence = f"{self.formatter.GREEN}HIGH{self.formatter.NC}"
            recommendation = "Consider entering position with tight stops"
            score_color = self.formatter.GREEN
        elif score >= 4:
            signal = f"{self.formatter.GREEN}BUY{self.formatter.NC}"
            confidence = f"{self.formatter.YELLOW}MEDIUM{self.formatter.NC}"
            recommendation = "Good entry zone, confirm with volume"
            score_color = self.formatter.GREEN
        elif score >= 1:
            signal = f"{self.formatter.YELLOW}HOLD/WAIT{self.formatter.NC}"
            confidence = f"{self.formatter.YELLOW}MEDIUM{self.formatter.NC}"
            recommendation = "Wait for clearer signals or pullback"
            score_color = self.formatter.YELLOW
        elif score >= -3:
            signal = f"{self.formatter.YELLOW}NEUTRAL{self.formatter.NC}"
            confidence = f"{self.formatter.YELLOW}LOW{self.formatter.NC}"
            recommendation = "No clear direction, stay on sidelines"
            score_color = self.formatter.YELLOW
        elif score >= -6:
            signal = f"{self.formatter.RED}SELL{self.formatter.NC}"
            confidence = f"{self.formatter.YELLOW}MEDIUM{self.formatter.NC}"
            recommendation = "Consider reducing exposure"
            score_color = self.formatter.RED
        else:
            signal = f"{self.formatter.RED}STRONG SELL{self.formatter.NC}"
            confidence = f"{self.formatter.RED}HIGH{self.formatter.NC}"
            recommendation = "Exit or avoid position"
            score_color = self.formatter.RED

        # Generate takeaways
        takeaways = []

        rsi = signals.get('rsi')
        if rsi and rsi < 30:
            takeaways.append("RSI oversold - potential bounce")
        elif rsi and rsi > 70:
            takeaways.append("RSI overbought - pullback likely")

        vwap = signals.get('vwap')
        if vwap:
            vwap_dist = ((signals.get('current_price', vwap) - vwap) / vwap) * 100
            if vwap_dist < -1:
                takeaways.append("Trading below VWAP - institutional buy zone")
            elif vwap_dist > 1:
                takeaways.append("Trading above VWAP - consider profit taking")

        if signals.get('bb_squeeze_detected'):
            takeaways.append("BB squeeze - major move coming soon")

        if signals.get('rsi_bullish_divergence'):
            takeaways.append("Bullish RSI divergence - reversal signal")

        if not takeaways:
            takeaways.append("Monitor for clearer signals before acting")

        return {
            'signal': signal,
            'confidence': confidence,
            'recommendation': recommendation,
            'takeaways': takeaways,
            'score_color': score_color
        }


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Show technical indicators')
    parser.add_argument('ticker', nargs='?', help='Ticker symbol (optional)')

    args = parser.parse_args()

    display = IndicatorDisplay()
    display.show_all_indicators(args.ticker)


if __name__ == '__main__':
    main()
