# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Show Indicators - Display current indicator values with interpretations

Displays all technical indicators with their current values, ranges, and interpretations.
Helps traders understand what each indicator means and how to use them.
"""

import sys
from typing import Optional
from tradingagents.database import get_db_connection, TickerOperations, ScanOperations
from tradingagents.utils.cli_formatter import CLIFormatter
from tradingagents.utils import display_next_steps
from tradingagents.screener.indicators import TechnicalIndicators
from tradingagents.screener.pattern_recognition import PatternRecognition
from tradingagents.screener.data_fetcher import DataFetcher
from tradingagents.screener.screener import DailyScreener
from tradingagents.screener.scorer import PriorityScorer
import pandas as pd
from datetime import datetime, timedelta, date
import logging

logger = logging.getLogger(__name__)


class IndicatorDisplay:
    """Display indicator values with interpretations."""

    def __init__(self):
        self.formatter = CLIFormatter()
        self.db = get_db_connection()
        self.ticker_ops = TickerOperations(self.db)
        self.scan_ops = ScanOperations(self.db)
        self.data_fetcher = DataFetcher(self.db)
        self.indicators = TechnicalIndicators()
        self.scorer = PriorityScorer()

    def show_all_indicators(self, ticker: Optional[str] = None, refresh: bool = False, refresh_data: bool = False):
        """Show all indicators with interpretations.

        Args:
            ticker: Ticker symbol (optional)
            refresh: If True, recalculate indicators from existing price data
            refresh_data: If True, fetch fresh price data first, then recalculate indicators
        """
        if ticker:
            # Handle refresh flags
            if refresh_data:
                print(f"{self.formatter.YELLOW}Refreshing price data for {ticker}...{self.formatter.NC}\n")
                self._refresh_price_data(ticker)
                print(f"{self.formatter.GREEN}✓ Price data refreshed{self.formatter.NC}\n")
            
            if refresh or refresh_data:
                print(f"{self.formatter.YELLOW}Recalculating indicators for {ticker}...{self.formatter.NC}\n")
                self._recalculate_indicators(ticker)
                print(f"{self.formatter.GREEN}✓ Indicators recalculated{self.formatter.NC}\n")
            
            self._show_ticker_indicators(ticker)
        else:
            self._show_indicator_guide()

    def _show_comparison_table(self, tickers: list, refresh: bool = False, refresh_data: bool = False):
        """Show comparison table for multiple tickers."""
        from tradingagents.screener.pattern_recognition import PatternRecognition
        
        # Collect data for all tickers
        ticker_data = []
        
        # Show refresh progress if refreshing
        if refresh_data or refresh:
            print(f"{self.formatter.YELLOW}Processing {len(tickers)} tickers...{self.formatter.NC}")
        
        for i, ticker in enumerate(tickers, 1):
            # Handle refresh flags
            if refresh_data:
                print(f"  [{i}/{len(tickers)}] Refreshing {ticker}...", end=' ', flush=True)
                if self._refresh_price_data(ticker):
                    print(f"{self.formatter.GREEN}✓{self.formatter.NC}")
                else:
                    print(f"{self.formatter.RED}✗{self.formatter.NC}")
            
            if refresh or refresh_data:
                print(f"  [{i}/{len(tickers)}] Calculating indicators for {ticker}...", end=' ', flush=True)
                if self._recalculate_indicators(ticker):
                    print(f"{self.formatter.GREEN}✓{self.formatter.NC}")
                else:
                    print(f"{self.formatter.RED}✗{self.formatter.NC}")
            
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
            
            result = self.db.execute_dict_query(query, (ticker.upper(),))
            
            if not result:
                ticker_data.append({
                    'ticker': ticker,
                    'error': 'No data found'
                })
                continue
            
            data = result[0]
            signals = data.get('technical_signals', {})
            current_price = float(data.get('current_price', 0)) if data.get('current_price') else 0.0
            
            # Calculate signal score
            pattern_analysis = PatternRecognition.analyze_patterns(signals)
            signal_score = pattern_analysis.get('overall_score', PatternRecognition._calculate_signal_score(signals))
            
            # Extract key metrics
            ticker_data.append({
                'ticker': ticker.upper(),
                'sector': data.get('sector', 'N/A'),
                'price': current_price,
                'priority_score': data.get('priority_score', 0),
                'signal_score': signal_score,
                'rsi': signals.get('rsi'),
                'macd_hist': signals.get('macd_histogram'),
                'ma_trend': self._get_ma_trend(signals),
                'vwap_dist': signals.get('vwap_distance_pct', 0),
                'bb_position': self._get_bb_position(signals, current_price),
                'volume_ratio': signals.get('volume_ratio'),
                'atr_pct': signals.get('atr_pct'),
                'mtf_signal': signals.get('mtf_signal', 'NEUTRAL'),
                'signals': signals,
                'scan_date': data.get('scan_date')
            })
        
        # Print comparison table header
        print(f"\n{self.formatter.CYAN}{self.formatter.BOLD}{'='*120}{self.formatter.NC}")
        print(f"{self.formatter.CYAN}{self.formatter.BOLD}  TECHNICAL INDICATORS COMPARISON - {len(tickers)} TICKERS{self.formatter.NC}")
        print(f"{self.formatter.CYAN}{self.formatter.BOLD}{'='*120}{self.formatter.NC}\n")
        
        # Print table header
        header = f"{'Ticker':<8} {'Sector':<15} {'Price':<10} {'Score':<7} {'RSI':<7} {'MACD':<8} {'MA Trend':<12} {'VWAP':<8} {'BB':<10} {'Vol':<6} {'ATR%':<7} {'MTF':<12}"
        print(f"{self.formatter.BOLD}{header}{self.formatter.NC}")
        print(f"{'-'*120}")
        
        # Print each ticker's row
        for data in ticker_data:
            if 'error' in data:
                print(f"{data['ticker']:<8} {self.formatter.RED}{data['error']:<112}{self.formatter.NC}")
                continue
            
            # Format values
            price_str = f"${data['price']:.2f}" if data['price'] > 0 else "N/A"
            
            # Signal score with color
            score = data['signal_score']
            if score >= 7:
                score_color = self.formatter.GREEN
                score_str = f"{score:.1f}"
            elif score >= 4:
                score_color = self.formatter.GREEN
                score_str = f"{score:.1f}"
            elif score >= 1:
                score_color = self.formatter.YELLOW
                score_str = f"{score:.1f}"
            else:
                score_color = self.formatter.RED
                score_str = f"{score:.1f}"
            
            # RSI with color
            rsi = data['rsi']
            if rsi:
                if rsi < 30:
                    rsi_color = self.formatter.GREEN
                elif rsi < 50:
                    rsi_color = self.formatter.YELLOW
                elif rsi < 70:
                    rsi_color = self.formatter.YELLOW
                else:
                    rsi_color = self.formatter.RED
                rsi_str = f"{rsi:.1f}"
            else:
                rsi_color = ""
                rsi_str = "N/A"
            
            # MACD histogram
            macd_hist = data['macd_hist']
            if macd_hist is not None:
                macd_color = self.formatter.GREEN if macd_hist > 0 else self.formatter.RED
                macd_str = f"{macd_hist:+.3f}"
            else:
                macd_color = ""
                macd_str = "N/A"
            
            # MA Trend
            ma_trend = data['ma_trend']
            if 'UPTREND' in ma_trend:
                ma_color = self.formatter.GREEN
            elif 'DOWNTREND' in ma_trend:
                ma_color = self.formatter.RED
            else:
                ma_color = self.formatter.YELLOW
            
            # VWAP distance
            vwap_dist = data['vwap_dist']
            if vwap_dist:
                if vwap_dist < -1:
                    vwap_color = self.formatter.GREEN
                elif vwap_dist < 1:
                    vwap_color = self.formatter.YELLOW
                else:
                    vwap_color = self.formatter.GREEN
                vwap_str = f"{vwap_dist:+.1f}%"
            else:
                vwap_color = ""
                vwap_str = "N/A"
            
            # BB Position
            bb_pos = data['bb_position']
            if 'Lower' in bb_pos:
                bb_color = self.formatter.GREEN
            elif 'Upper' in bb_pos:
                bb_color = self.formatter.RED
            else:
                bb_color = self.formatter.YELLOW
            
            # Volume ratio
            vol_ratio = data['volume_ratio']
            if vol_ratio:
                if vol_ratio > 1.5:
                    vol_color = self.formatter.GREEN
                elif vol_ratio < 0.8:
                    vol_color = self.formatter.RED
                else:
                    vol_color = self.formatter.YELLOW
                vol_str = f"{vol_ratio:.2f}x"
            else:
                vol_color = ""
                vol_str = "N/A"
            
            # ATR %
            atr_pct = data['atr_pct']
            if atr_pct:
                if atr_pct < 1:
                    atr_color = self.formatter.GREEN
                elif atr_pct < 3:
                    atr_color = self.formatter.YELLOW
                else:
                    atr_color = self.formatter.RED
                atr_str = f"{atr_pct:.2f}%"
            else:
                atr_color = ""
                atr_str = "N/A"
            
            # MTF Signal
            mtf = data['mtf_signal']
            if 'BULLISH' in mtf or 'BUY' in mtf:
                mtf_color = self.formatter.GREEN
            elif 'BEARISH' in mtf or 'SELL' in mtf:
                mtf_color = self.formatter.RED
            else:
                mtf_color = self.formatter.YELLOW
            
            # Print row
            row = (f"{data['ticker']:<8} "
                   f"{data['sector']:<15} "
                   f"{price_str:<10} "
                   f"{score_color}{score_str:<7}{self.formatter.NC} "
                   f"{rsi_color}{rsi_str:<7}{self.formatter.NC} "
                   f"{macd_color}{macd_str:<8}{self.formatter.NC} "
                   f"{ma_color}{ma_trend:<12}{self.formatter.NC} "
                   f"{vwap_color}{vwap_str:<8}{self.formatter.NC} "
                   f"{bb_color}{bb_pos:<10}{self.formatter.NC} "
                   f"{vol_color}{vol_str:<6}{self.formatter.NC} "
                   f"{atr_color}{atr_str:<7}{self.formatter.NC} "
                   f"{mtf_color}{mtf:<12}{self.formatter.NC}")
            print(row)
        
        print(f"{'-'*120}\n")
        
        # Print summary with top picks
        print(f"{self.formatter.BOLD}{self.formatter.BLUE}Summary:{self.formatter.NC}\n")
        
        # Sort by signal score
        valid_data = [d for d in ticker_data if 'error' not in d]
        if valid_data:
            sorted_data = sorted(valid_data, key=lambda x: x['signal_score'], reverse=True)
            
            print(f"{self.formatter.GREEN}Top Picks (by Signal Score):{self.formatter.NC}")
            for i, data in enumerate(sorted_data[:3], 1):
                score = data['signal_score']
                if score >= 7:
                    icon = "🚀"
                elif score >= 4:
                    icon = "✅"
                else:
                    icon = "⚠️"
                print(f"  {i}. {icon} {data['ticker']:<8} Score: {score:.1f}/10  Price: ${data['price']:.2f}  {data['mtf_signal']}")
            
            print()
        
        # Store ticker_data for potential detailed view
        return ticker_data
    
    def _get_ma_trend(self, signals):
        """Get MA trend description."""
        ma_20 = signals.get('ma_20')
        ma_50 = signals.get('ma_50')
        ma_200 = signals.get('ma_200')
        
        if ma_20 and ma_50 and ma_200:
            if ma_20 > ma_50 > ma_200:
                return "UPTREND"
            elif ma_20 < ma_50 < ma_200:
                return "DOWNTREND"
            else:
                return "MIXED"
        return "N/A"
    
    def _get_bb_position(self, signals, current_price):
        """Get Bollinger Band position description."""
        bb_upper = signals.get('bb_upper')
        bb_middle = signals.get('bb_middle')
        bb_lower = signals.get('bb_lower')
        
        if bb_upper and bb_middle and bb_lower and current_price > 0:
            bb_position = ((current_price - bb_lower) / (bb_upper - bb_lower)) * 100
            if bb_position < 20:
                return "Lower"
            elif bb_position < 40:
                return "Below Mid"
            elif bb_position < 60:
                return "Middle"
            elif bb_position < 80:
                return "Above Mid"
            else:
                return "Upper"
        return "N/A"

    def _show_ticker_indicators(self, ticker: str):
        """Show indicator values for a specific ticker."""

        print(f"\n{self.formatter.CYAN}{self.formatter.BOLD}{'='*80}{self.formatter.NC}")
        print(f"{self.formatter.CYAN}{self.formatter.BOLD}Technical Indicators for {ticker}{self.formatter.NC}")
        print(f"{self.formatter.CYAN}{self.formatter.BOLD}{'='*80}{self.formatter.NC}\n")

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

        # Calculate signal score and summary early for executive summary
        from tradingagents.screener.pattern_recognition import PatternRecognition
        # Store pattern_analysis for later use
        pattern_analysis = PatternRecognition.analyze_patterns(signals)
        signal_score = pattern_analysis.get('overall_score', PatternRecognition._calculate_signal_score(signals))
        summary = self._get_trading_summary(signal_score, signals, current_price)
        # Store in instance for later access
        self._pattern_analysis = pattern_analysis

        # === EXECUTIVE SUMMARY ===
        print(f"{self.formatter.BOLD}{self.formatter.CYAN}{'═'*80}{self.formatter.NC}")
        print(f"{self.formatter.BOLD}{self.formatter.CYAN}📊 EXECUTIVE SUMMARY{self.formatter.NC}")
        print(f"{self.formatter.BOLD}{self.formatter.CYAN}{'═'*80}{self.formatter.NC}\n")
        
        # Overall Signal
        print(f"{self.formatter.BOLD}Overall Signal:{self.formatter.NC} {summary['signal']}")
        print(f"{self.formatter.BOLD}Signal Score:{self.formatter.NC} {summary['score_color']}{signal_score:.1f}/10{self.formatter.NC}")
        print(f"{self.formatter.BOLD}Confidence:{self.formatter.NC} {summary['confidence']}")
        print(f"{self.formatter.BOLD}Recommendation:{self.formatter.NC} {summary['recommendation']}\n")
        
        # Key Highlights
        print(f"{self.formatter.BOLD}{self.formatter.YELLOW}🔑 KEY HIGHLIGHTS:{self.formatter.NC}\n")
        highlights = []
        
        # RSI highlight
        rsi = signals.get('rsi')
        if rsi:
            if rsi < 30:
                highlights.append(f"{self.formatter.GREEN}✓ RSI {rsi:.1f} - OVERSOLD (Strong Buy Signal){self.formatter.NC}")
            elif rsi > 70:
                highlights.append(f"{self.formatter.RED}⚠ RSI {rsi:.1f} - OVERBOUGHT (Sell Signal){self.formatter.NC}")
            elif rsi < 40:
                highlights.append(f"{self.formatter.GREEN}✓ RSI {rsi:.1f} - Approaching Oversold (Buy Zone){self.formatter.NC}")
        
        # MACD highlight
        macd_hist = signals.get('macd_histogram')
        macd = signals.get('macd')
        macd_signal = signals.get('macd_signal')
        if macd and macd_signal:
            if macd > macd_signal and macd_hist and macd_hist > 0:
                highlights.append(f"{self.formatter.GREEN}✓ MACD Bullish Crossover (Momentum Building){self.formatter.NC}")
            elif macd < macd_signal and macd_hist and macd_hist < 0:
                highlights.append(f"{self.formatter.RED}⚠ MACD Bearish Crossover (Momentum Declining){self.formatter.NC}")
        
        # VWAP highlight
        vwap_dist = signals.get('vwap_distance_pct', 0)
        if vwap_dist:
            if vwap_dist < -3:
                highlights.append(f"{self.formatter.GREEN}✓ Price {abs(vwap_dist):.1f}% Below VWAP (Strong Buy Opportunity){self.formatter.NC}")
            elif vwap_dist > 8:
                highlights.append(f"{self.formatter.YELLOW}⚠ Price {vwap_dist:.1f}% Above VWAP (Overextended - Watch for Pullback){self.formatter.NC}")
        
        # Bollinger Band Squeeze
        if signals.get('bb_squeeze_detected'):
            squeeze_strength = signals.get('bb_squeeze_strength', 0)
            highlights.append(f"{self.formatter.CYAN}💥 Bollinger Band Squeeze Detected ({squeeze_strength:.0%} strength) - Breakout Imminent{self.formatter.NC}")
        
        # Volume Profile position
        vp_position = signals.get('vp_profile_position', '')
        if 'BELOW_VALUE_AREA' in vp_position:
            highlights.append(f"{self.formatter.GREEN}✓ Price Below Value Area (Institutional Buy Zone){self.formatter.NC}")
        elif 'ABOVE_VALUE_AREA' in vp_position:
            highlights.append(f"{self.formatter.RED}⚠ Price Above Value Area (Institutional Sell Zone){self.formatter.NC}")
        
        # Multi-timeframe alignment
        mtf_alignment = signals.get('mtf_alignment', '')
        if 'PERFECT_BULLISH' in mtf_alignment or 'STRONG_BULLISH' in mtf_alignment:
            highlights.append(f"{self.formatter.GREEN}✓ Perfect Multi-Timeframe Bullish Alignment{self.formatter.NC}")
        elif 'PERFECT_BEARISH' in mtf_alignment or 'STRONG_BEARISH' in mtf_alignment:
            highlights.append(f"{self.formatter.RED}⚠ Perfect Multi-Timeframe Bearish Alignment{self.formatter.NC}")
        elif 'RANGE_BOUND' in mtf_alignment:
            highlights.append(f"{self.formatter.YELLOW}○ Range-Bound Market (Trade Range, Not Trend){self.formatter.NC}")
        
        # Order Flow
        of_buying = signals.get('of_buying_pct', 0)
        if of_buying > 65:
            highlights.append(f"{self.formatter.GREEN}✓ Strong Buying Pressure ({of_buying:.0f}% buying){self.formatter.NC}")
        elif of_buying < 35:
            highlights.append(f"{self.formatter.RED}⚠ Strong Selling Pressure ({100-of_buying:.0f}% selling){self.formatter.NC}")
        
        # Volume confirmation
        vol_ratio = signals.get('volume_ratio')
        if vol_ratio and vol_ratio > 2.0:
            highlights.append(f"{self.formatter.GREEN}✓ Unusually High Volume ({vol_ratio:.1f}x avg) - Strong Confirmation{self.formatter.NC}")
        elif vol_ratio and vol_ratio < 0.8:
            highlights.append(f"{self.formatter.YELLOW}⚠ Low Volume ({vol_ratio:.1f}x avg) - Weak Confirmation{self.formatter.NC}")
        
        # Display top 5 highlights
        for i, highlight in enumerate(highlights[:5], 1):
            print(f"  {i}. {highlight}")
        
        if len(highlights) > 5:
            print(f"  ... and {len(highlights) - 5} more signals (see details below)\n")
        else:
            print()
        
        # Next Steps
        print(f"{self.formatter.BOLD}{self.formatter.BLUE}📋 NEXT STEPS:{self.formatter.NC}\n")
        
        # Entry/Exit guidance
        entry_min = None
        entry_max = None
        from tradingagents.screener.entry_price_calculator import EntryPriceCalculator
        try:
            entry_calc = EntryPriceCalculator()
            entry_data = entry_calc.calculate_entry_price(
                current_price=current_price,
                technical_signals=signals,
                quote={'price': current_price}
            )
            entry_min = entry_data.get('entry_price_min')
            entry_max = entry_data.get('entry_price_max')
        except:
            pass
        
        if signal_score >= 7:
            print(f"  {self.formatter.GREEN}1. ENTRY STRATEGY:{self.formatter.NC}")
            if entry_min and entry_max:
                if entry_min <= current_price <= entry_max:
                    print(f"     • Current price ${current_price:.2f} is IN optimal entry zone (${entry_min:.2f}-${entry_max:.2f})")
                    print(f"     • Consider entering position now")
                elif current_price < entry_min:
                    pct_below = ((entry_min - current_price) / entry_min) * 100
                    print(f"     • Current price ${current_price:.2f} is {pct_below:.1f}% below optimal entry zone")
                    print(f"     • Wait for pullback to ${entry_min:.2f}-${entry_max:.2f} for better entry")
                else:
                    pct_above = ((current_price - entry_max) / entry_max) * 100
                    print(f"     • Current price ${current_price:.2f} is {pct_above:.1f}% above optimal entry zone")
                    print(f"     • Consider waiting for pullback to ${entry_min:.2f}-${entry_max:.2f}")
            else:
                print(f"     • Consider entering position at current price ${current_price:.2f}")
            
            if summary.get('risk_reward') and summary['risk_reward'].get('stop_loss'):
                stop = summary['risk_reward']['stop_loss']
                stop_pct = summary['risk_reward'].get('stop_pct', 0)
                print(f"  {self.formatter.RED}2. RISK MANAGEMENT:{self.formatter.NC}")
                print(f"     • Set stop loss at ${stop:.2f} ({abs(stop_pct):.1f}% risk)")
                print(f"     • Position size based on risk tolerance")
            
            if summary.get('risk_reward') and summary['risk_reward'].get('targets'):
                print(f"  {self.formatter.YELLOW}3. PROFIT TARGETS:{self.formatter.NC}")
                for i, target in enumerate(summary['risk_reward']['targets'][:3], 1):
                    gain_pct = target.get('gain_pct', 0)
                    print(f"     • Target {i}: ${target['price']:.2f} ({target.get('level', 'N/A')}) - {gain_pct:+.1f}% gain")
            
            if summary.get('time_horizon'):
                print(f"  {self.formatter.CYAN}4. TIMELINE:{self.formatter.NC}")
                print(f"     • Expected move: {summary['time_horizon']}")
        
        elif signal_score >= 4:
            print(f"  {self.formatter.YELLOW}1. WAIT FOR CONFIRMATION:{self.formatter.NC}")
            print(f"     • Signal is moderately bullish but needs confirmation")
            if vol_ratio and vol_ratio < 1.0:
                print(f"     • Wait for volume to increase above 1.0x average")
            if entry_min and current_price > entry_max:
                print(f"     • Consider waiting for pullback to ${entry_min:.2f}-${entry_max:.2f}")
            print(f"  {self.formatter.CYAN}2. MONITOR KEY LEVELS:{self.formatter.NC}")
            pivot_s1 = signals.get('pivot_s1')
            if pivot_s1:
                print(f"     • Watch support at ${pivot_s1:.2f} (S1)")
            vp_val = signals.get('vp_val')
            if vp_val:
                print(f"     • Watch support at ${vp_val:.2f} (VAL)")
        
        elif signal_score >= 1:
            if 'RANGE_BOUND' in mtf_alignment:
                print(f"  {self.formatter.YELLOW}1. RANGE TRADING STRATEGY:{self.formatter.NC}")
                vp_vah = signals.get('vp_vah')
                vp_val = signals.get('vp_val')
                if vp_vah and vp_val:
                    print(f"     • Sell near ${vp_vah:.2f} (VAH resistance)")
                    print(f"     • Buy near ${vp_val:.2f} (VAL support)")
                    print(f"     • Stop loss: 2-3% outside range boundaries")
            else:
                print(f"  {self.formatter.YELLOW}1. WAIT FOR CLEARER SIGNALS:{self.formatter.NC}")
                print(f"     • Mixed signals - no clear directional bias")
                print(f"     • Monitor for breakout or clearer trend confirmation")
        
        else:
            print(f"  {self.formatter.RED}1. AVOID OR EXIT:{self.formatter.NC}")
            print(f"     • Bearish signals dominate - not a good entry")
            if signal_score < -3:
                print(f"     • Consider exiting existing positions")
        
        # Key Takeaways
        if summary.get('takeaways'):
            print(f"\n  {self.formatter.BOLD}💡 KEY TAKEAWAYS:{self.formatter.NC}")
            for takeaway in summary['takeaways'][:3]:
                print(f"     • {takeaway}")
        
        print(f"\n{self.formatter.CYAN}{'─'*80}{self.formatter.NC}\n")
        print(f"{self.formatter.YELLOW}📖 Detailed indicator breakdown below...{self.formatter.NC}\n")

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
                # Within value area - distinguish between upper/middle/lower
                if distance_to_poc > 1.5:
                    print(f"  {self.formatter.YELLOW}○ UPPER VALUE AREA{self.formatter.NC} - Price in upper fair value range")
                    print(f"  Near VAH (${vah:.2f}) - approaching resistance")
                    print(f"  Cautiously bullish - watch for rejection at VAH")
                elif distance_to_poc < -1.5:
                    print(f"  {self.formatter.YELLOW}○ LOWER VALUE AREA{self.formatter.NC} - Price in lower fair value range")
                    print(f"  Near VAL (${val:.2f}) - approaching support")
                    print(f"  Cautiously bullish - good support nearby")
                else:
                    print(f"  {self.formatter.YELLOW}○ FAIR VALUE{self.formatter.NC} - Price within normal range")
                    print(f"  Near POC (${poc:.2f}) - balanced market")
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
            elif 'SHORT_TERM_BULLISH' in mtf_alignment:
                align_color = self.formatter.GREEN
                align_icon = "📈"
            elif 'SHORT_TERM_BEARISH' in mtf_alignment:
                align_color = self.formatter.RED
                align_icon = "📉"
            elif 'MIXED_DAILY_BULLISH' in mtf_alignment or 'BULLISH' in mtf_alignment:
                align_color = self.formatter.GREEN
                align_icon = "📊"
            elif 'MIXED_DAILY_BEARISH' in mtf_alignment or 'BEARISH' in mtf_alignment:
                align_color = self.formatter.RED
                align_icon = "📊"
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

        # Run pattern detection (reuse pattern_analysis if already calculated)
        if hasattr(self, '_pattern_analysis'):
            pattern_analysis = self._pattern_analysis
        else:
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

        # === FINAL SUMMARY & ACTION PLAN ===
        print(f"\n{self.formatter.BOLD}{self.formatter.CYAN}{'═'*80}{self.formatter.NC}")
        print(f"{self.formatter.BOLD}{self.formatter.CYAN}📋 FINAL SUMMARY & ACTION PLAN{self.formatter.NC}")
        print(f"{self.formatter.BOLD}{self.formatter.CYAN}{'═'*80}{self.formatter.NC}\n")

        # Overall signal score (already calculated above)
        print(f"{self.formatter.BOLD}Overall Assessment:{self.formatter.NC}")
        print(f"  Signal Score: {summary['score_color']}{signal_score:.1f}/10{self.formatter.NC}")
        print(f"  Signal: {summary['signal']}")
        print(f"  Confidence: {summary['confidence']}\n")
        
        # === PRICE TARGETS & RISK/REWARD ===
        print(f"{self.formatter.BOLD}{self.formatter.BLUE}═══ PRICE TARGETS & RISK/REWARD ═══{self.formatter.NC}\n")
        
        # Get entry price range from entry calculator
        from tradingagents.screener.entry_price_calculator import EntryPriceCalculator
        entry_calc = EntryPriceCalculator()
        entry_data = entry_calc.calculate_entry_price(
            current_price=current_price,
            technical_signals=signals,
            quote={'price': current_price}
        )
        
        entry_min = entry_data.get('entry_price_min')
        entry_max = entry_data.get('entry_price_max')
        
        if entry_min and entry_max:
            entry_min_float = float(entry_min)
            entry_max_float = float(entry_max)
            entry_mid = (entry_min_float + entry_max_float) / 2
            
            print(f"{self.formatter.WHITE}Entry Zone:{self.formatter.NC} ${entry_min_float:.2f}-${entry_max_float:.2f}")
            print(f"{self.formatter.WHITE}Current Price:{self.formatter.NC} ${current_price:.2f}", end="")
            
            # Show if price is in entry range
            if entry_min_float <= current_price <= entry_max_float:
                print(f" {self.formatter.GREEN}(IN RANGE ✓){self.formatter.NC}")
            elif current_price < entry_min_float:
                pct_below = ((entry_min_float - current_price) / entry_min_float) * 100
                print(f" {self.formatter.YELLOW}({pct_below:.1f}% below entry){self.formatter.NC}")
            else:
                pct_above = ((current_price - entry_max_float) / entry_max_float) * 100
                print(f" {self.formatter.YELLOW}({pct_above:.1f}% above entry){self.formatter.NC}")
            print()
            
            # Show risk/reward from summary if available
            if summary.get('risk_reward'):
                rr_info = summary['risk_reward']
                if rr_info.get('stop_loss'):
                    print(f"{self.formatter.WHITE}Stop Loss:{self.formatter.NC} ${rr_info['stop_loss']:.2f} ({rr_info.get('stop_pct', 0):.1f}% risk)")
                if rr_info.get('targets'):
                    print(f"{self.formatter.WHITE}Targets:{self.formatter.NC}")
                    for i, target in enumerate(rr_info['targets'], 1):
                        gain_from_entry = ((target['price'] - entry_mid) / entry_mid) * 100
                        gain_from_current = ((target['price'] - current_price) / current_price) * 100
                        rr_ratio = target.get('rr_ratio', 'N/A')
                        print(f"  Target {i}: ${target['price']:.2f} ({target.get('level', 'N/A')}) - {gain_from_current:.1f}% from current, {gain_from_entry:.1f}% from entry - R/R {rr_ratio}")
                if rr_info.get('note'):
                    print(f"  {self.formatter.YELLOW}{rr_info['note']}{self.formatter.NC}")
                print()
            else:
                # Calculate basic targets if not in summary
                vp_vah = signals.get('vp_vah')
                pivot_r1 = signals.get('pivot_r1')
                pivot_r2 = signals.get('pivot_r2')
                
                if vp_vah or pivot_r1 or pivot_r2:
                    print(f"{self.formatter.WHITE}Potential Targets:{self.formatter.NC}")
                    if vp_vah and vp_vah > current_price:
                        gain = ((vp_vah - current_price) / current_price) * 100
                        print(f"  Target 1: ${vp_vah:.2f} (VAH) - {gain:.1f}% gain")
                    if pivot_r1 and pivot_r1 > current_price:
                        gain = ((pivot_r1 - current_price) / current_price) * 100
                        print(f"  Target 2: ${pivot_r1:.2f} (R1) - {gain:.1f}% gain")
                    if pivot_r2 and pivot_r2 > current_price:
                        gain = ((pivot_r2 - current_price) / current_price) * 100
                        print(f"  Target 3: ${pivot_r2:.2f} (R2) - {gain:.1f}% gain")
                    print()

        # Action Plan
        print(f"{self.formatter.BOLD}{self.formatter.GREEN}✅ ACTION PLAN:{self.formatter.NC}\n")
        
        if signal_score >= 7:
            print(f"  {self.formatter.GREEN}STRONG BUY SETUP{self.formatter.NC}")
            if summary.get('risk_reward'):
                rr_info = summary['risk_reward']
                if rr_info.get('stop_loss'):
                    print(f"     • Entry: ${current_price:.2f} (or wait for pullback to entry zone)")
                    print(f"     • Stop Loss: ${rr_info['stop_loss']:.2f} ({abs(rr_info.get('stop_pct', 0)):.1f}% risk)")
                if rr_info.get('targets'):
                    print(f"     • Profit Targets:")
                    for i, target in enumerate(rr_info['targets'][:3], 1):
                        print(f"       Target {i}: ${target['price']:.2f} ({target.get('level', 'N/A')}) - {target.get('gain_pct', 0):+.1f}% gain")
            if summary.get('time_horizon'):
                print(f"     • Timeline: {summary['time_horizon']}")
            if summary.get('exit_strategy'):
                print(f"     • Exit Strategy:")
                for exit_rule in summary['exit_strategy'][:3]:
                    print(f"       {exit_rule}")
        elif signal_score >= 4:
            print(f"  {self.formatter.YELLOW}MODERATE BUY SETUP{self.formatter.NC}")
            print(f"     • Wait for confirmation before entering")
            if summary.get('risk_reward'):
                rr_info = summary['risk_reward']
                if rr_info.get('stop_loss'):
                    print(f"     • If entering, use stop loss: ${rr_info['stop_loss']:.2f}")
        elif signal_score >= 1:
            if 'RANGE_BOUND' in mtf_alignment:
                print(f"  {self.formatter.YELLOW}RANGE TRADING OPPORTUNITY{self.formatter.NC}")
                vp_vah = signals.get('vp_vah')
                vp_val = signals.get('vp_val')
                if vp_vah and vp_val:
                    print(f"     • Sell near ${vp_vah:.2f} (VAH)")
                    print(f"     • Buy near ${vp_val:.2f} (VAL)")
            else:
                print(f"  {self.formatter.YELLOW}WAIT FOR CLEARER SIGNALS{self.formatter.NC}")
                print(f"     • Monitor for breakout or trend confirmation")
        else:
            print(f"  {self.formatter.RED}AVOID OR EXIT{self.formatter.NC}")
            print(f"     • Bearish signals dominate - not a good entry point")
        
        print()
        
        # Key Takeaways (if not already shown in executive summary)
        if summary.get('takeaways') and len(summary['takeaways']) > 3:
            print(f"{self.formatter.BOLD}💡 Additional Insights:{self.formatter.NC}")
            for takeaway in summary['takeaways'][3:]:
                print(f"  • {takeaway}")
            print()
        
        # Display next steps and recommendations
        display_next_steps('indicators', context={'ticker': ticker, 'tickers': [ticker]})
        
        # Add footer separator
        print(f"\n{self.formatter.CYAN}{'─'*80}{self.formatter.NC}\n")

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
        print("  Price < VWAP - 3%: Strong buy - far below benchmark")
        print("  Price < VWAP - 1%: Buy - sellers in control")
        print("  Price within ±1%:  Fair value - balanced")
        print("  Price > VWAP + 1%: Bullish - buyers in control")
        print("  Price > VWAP + 3%: Strong bullish - strong uptrend")
        print("  Price > VWAP + 8%: Overextended bullish - watch for pullback\n")

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
        """Interpret VWAP distance.

        VWAP is institutional traders' benchmark. Price above VWAP = bullish (buyers in control).
        Price below VWAP = bearish (sellers in control). Large deviations can indicate overextension.
        """
        if distance_pct < -3:
            return {
                'signal': 'STRONG BUY',
                'interpretation': 'Far below institutional benchmark - excellent entry opportunity',
                'color': self.formatter.GREEN
            }
        elif distance_pct < -1:
            return {
                'signal': 'BUY',
                'interpretation': 'Below VWAP - sellers in control, good entry zone',
                'color': self.formatter.GREEN
            }
        elif distance_pct < 1:
            return {
                'signal': 'FAIR VALUE',
                'interpretation': 'Trading at institutional benchmark - balanced',
                'color': self.formatter.YELLOW
            }
        elif distance_pct < 3:
            return {
                'signal': 'BULLISH',
                'interpretation': 'Above VWAP - buyers in control, positive momentum',
                'color': self.formatter.GREEN
            }
        elif distance_pct < 8:
            return {
                'signal': 'STRONG BULLISH',
                'interpretation': 'Well above VWAP - strong uptrend, buyers dominating',
                'color': self.formatter.GREEN
            }
        else:
            return {
                'signal': 'OVEREXTENDED BULLISH',
                'interpretation': 'Very far above VWAP - bullish but watch for profit-taking pullback',
                'color': self.formatter.YELLOW
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

    def _get_trading_summary(self, score, signals, current_price=0):
        """Generate trading summary with context-aware recommendations."""
        if score >= 7:
            signal = f"{self.formatter.GREEN}STRONG BUY{self.formatter.NC}"
            confidence = f"{self.formatter.GREEN}HIGH{self.formatter.NC}"

            # Enhanced recommendation with context
            pivot_s1 = signals.get('pivot_s1')
            bb_middle = signals.get('bb_middle')
            vp_vah = signals.get('vp_vah')

            # Check if above optimal entry
            if pivot_s1 and current_price > pivot_s1 * 1.02:
                recommendation = f"Consider small position now OR wait for pullback to ${pivot_s1:.2f} for optimal entry"
            else:
                recommendation = "Consider entering position with tight stops"

            # Add resistance context if near VAH
            if vp_vah and current_price > vp_vah * 0.98:
                recommendation += f" | Watch resistance at ${vp_vah:.2f}"

            score_color = self.formatter.GREEN
        elif score >= 4:
            signal = f"{self.formatter.GREEN}BUY{self.formatter.NC}"
            confidence = f"{self.formatter.YELLOW}MEDIUM{self.formatter.NC}"
            recommendation = "Good entry zone, confirm with volume"
            score_color = self.formatter.GREEN
        elif score >= 1:
            # Check if this is a range-bound opportunity
            mtf_alignment = signals.get('mtf_alignment', '')
            vp_position = signals.get('vp_profile_position', '')

            if mtf_alignment == 'RANGE_BOUND' and vp_position == 'AT_POC':
                signal = f"{self.formatter.YELLOW}RANGE TRADING{self.formatter.NC}"
                confidence = f"{self.formatter.YELLOW}MEDIUM{self.formatter.NC}"

                # Calculate range levels
                vp_vah = signals.get('vp_vah')
                vp_val = signals.get('vp_val')
                pivot_r1 = signals.get('pivot_r1')
                pivot_s1 = signals.get('pivot_s1')

                # Use VAH/VAL or R1/S1 for range
                resistance = vp_vah or pivot_r1
                support = vp_val or pivot_s1

                if resistance and support and current_price > 0:
                    range_pct = ((resistance - support) / support) * 100
                    recommendation = f"Range trading opportunity: Sell ${resistance:.2f}, Buy ${support:.2f} (~{range_pct:.1f}% range)"
                else:
                    recommendation = "Range trading opportunity: Sell resistance, buy support"

                score_color = self.formatter.YELLOW
            else:
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

        # Generate takeaways based on score and signals
        takeaways = []

        # For bullish setups (score >= 4)
        if score >= 7:
            # Strong buy - focus on execution details
            vp_dist_to_vah = signals.get('vp_distance_to_vah_pct', -999)
            if 0 < vp_dist_to_vah < 2:
                takeaways.append(f"Watch for resistance at VAH (${signals.get('vp_vah', 0):.2f})")

            vwap_dist = signals.get('vwap_distance_pct', 0)
            if vwap_dist > 8:
                takeaways.append("VWAP extended - watch for pullback opportunity")

            rsi = signals.get('rsi', 50)
            if rsi > 65:
                takeaways.append(f"RSI {rsi:.1f} approaching overbought - use tight stops")

            mtf_signal = signals.get('mtf_signal', '')
            if 'SHORT_TERM' in signals.get('mtf_alignment', ''):
                takeaways.append("Keep trades short-term - no long-term trend confirmation")

            # Add entry context if available
            pivot_s1 = signals.get('pivot_s1')
            bb_middle = signals.get('bb_middle')
            if pivot_s1 or bb_middle:
                optimal_entry = min(x for x in [pivot_s1, bb_middle] if x is not None)
                if current_price and current_price > optimal_entry * 1.02:
                    takeaways.append(f"Consider waiting for pullback to ${optimal_entry:.2f} for better entry")

        elif score >= 4:
            # Moderate buy - emphasize confirmations
            if signals.get('of_buying_pct', 50) > 65:
                takeaways.append("Strong buying pressure - follow institutional flow")
            if signals.get('volume_ratio', 1.0) > 1.3:
                takeaways.append("Above-average volume confirms move")
            if signals.get('rsi_bullish_divergence'):
                takeaways.append("Bullish divergence - potential reversal setup")
            if signals.get('bb_squeeze_detected'):
                takeaways.append("BB squeeze - breakout imminent, watch direction")

        elif score >= 1:
            # Weak buy/hold OR range trading opportunity
            mtf_alignment = signals.get('mtf_alignment', '')
            vp_position = signals.get('vp_profile_position', '')

            if mtf_alignment == 'RANGE_BOUND' and vp_position == 'AT_POC':
                # Range trading specific takeaways
                vp_vah = signals.get('vp_vah')
                vp_val = signals.get('vp_val')

                if vp_vah and vp_val:
                    range_size = ((vp_vah - vp_val) / vp_val) * 100
                    takeaways.append(f"Range-bound: Trade between ${vp_val:.2f}-${vp_vah:.2f} ({range_size:.1f}% range)")

                takeaways.append("Sell near VAH resistance, buy near VAL support")
                takeaways.append("Use 2-3% stops outside range boundaries")

                atr_pct = signals.get('atr_pct', 0)
                if atr_pct > 3.0:
                    takeaways.append(f"Higher volatility ({atr_pct:.1f}%) - use wider stops or smaller positions")
            else:
                # Regular weak signals
                takeaways.append("Mixed signals - wait for clearer confirmation")
                if signals.get('volume_ratio', 1.0) < 1.0:
                    takeaways.append("Below-average volume - weak conviction")
                if signals.get('mtf_signal') in ['NEUTRAL', 'RANGE_TRADE']:
                    takeaways.append("No clear trend - consider range trading only")

        elif score >= -3:
            # Neutral/weak sell
            takeaways.append("No clear directional bias - stay on sidelines")

        else:
            # Strong sell
            if signals.get('rsi', 50) > 70:
                takeaways.append("RSI overbought - take profits or exit")
            if signals.get('of_selling_pct', 50) > 65:
                takeaways.append("Strong selling pressure - avoid new longs")

        # Always include at least one takeaway
        if not takeaways:
            takeaways.append("Monitor price action for clearer signals")

        # === RISK/REWARD ANALYSIS (for scores >= 4) ===
        risk_reward = None
        time_horizon = None
        exit_strategy = None

        if score >= 4 and current_price > 0:
            # Calculate stop loss
            pivot_s1 = signals.get('pivot_s1')
            bb_middle = signals.get('bb_middle')
            fib_382 = signals.get('fib_382')

            # Use most conservative stop (lowest support level)
            stop_candidates = [x for x in [pivot_s1, bb_middle, fib_382] if x is not None]
            if stop_candidates:
                stop_loss = min(stop_candidates)
                # Place stop slightly below support
                stop_loss = stop_loss * 0.995  # 0.5% below support
                stop_pct = ((stop_loss - current_price) / current_price) * 100

                # Calculate targets
                targets = []
                vp_vah = signals.get('vp_vah')
                bb_upper = signals.get('bb_upper')
                pivot_r1 = signals.get('pivot_r1')
                pivot_r2 = signals.get('pivot_r2')

                risk = abs(current_price - stop_loss)

                # Target 1: VAH or R1 (whichever is closer)
                if vp_vah and vp_vah > current_price:
                    reward1 = vp_vah - current_price
                    rr_ratio1 = f"1:{reward1/risk:.1f}" if risk > 0 else "N/A"
                    targets.append({
                        'price': vp_vah,
                        'gain_pct': ((vp_vah - current_price) / current_price) * 100,
                        'rr_ratio': rr_ratio1,
                        'level': 'VAH'
                    })

                # Target 2: BB Upper or R1
                if bb_upper and bb_upper > current_price:
                    reward2 = bb_upper - current_price
                    rr_ratio2 = f"1:{reward2/risk:.1f}" if risk > 0 else "N/A"
                    targets.append({
                        'price': bb_upper,
                        'gain_pct': ((bb_upper - current_price) / current_price) * 100,
                        'rr_ratio': rr_ratio2,
                        'level': 'BB Upper'
                    })
                elif pivot_r1 and pivot_r1 > current_price:
                    reward2 = pivot_r1 - current_price
                    rr_ratio2 = f"1:{reward2/risk:.1f}" if risk > 0 else "N/A"
                    targets.append({
                        'price': pivot_r1,
                        'gain_pct': ((pivot_r1 - current_price) / current_price) * 100,
                        'rr_ratio': rr_ratio2,
                        'level': 'R1'
                    })

                # Target 3: R2 or extended target
                if pivot_r2 and pivot_r2 > current_price:
                    reward3 = pivot_r2 - current_price
                    rr_ratio3 = f"1:{reward3/risk:.1f}" if risk > 0 else "N/A"
                    targets.append({
                        'price': pivot_r2,
                        'gain_pct': ((pivot_r2 - current_price) / current_price) * 100,
                        'rr_ratio': rr_ratio3,
                        'level': 'R2'
                    })

                # Sort targets by price
                targets = sorted(targets, key=lambda x: x['price'])[:3]  # Max 3 targets

                # Add note if R/R is poor
                note = None
                if targets and risk > 0:
                    first_rr = targets[0].get('rr_ratio', '1:0')
                    if '1:' in first_rr:
                        ratio_val = float(first_rr.split(':')[1])
                        if ratio_val < 1.5:
                            optimal_entry = min(stop_candidates) if stop_candidates else current_price
                            note = f"⚠️ R/R is modest - consider waiting for ${optimal_entry:.2f} entry for better ratio"

                risk_reward = {
                    'stop_loss': stop_loss,
                    'stop_pct': stop_pct,
                    'targets': targets,
                    'note': note
                }

            # === TIME HORIZON ===
            mtf_alignment = signals.get('mtf_alignment', '')
            if 'PERFECT' in mtf_alignment or 'STRONG' in mtf_alignment:
                time_horizon = "2-4 weeks (strong trend alignment)"
            elif 'SHORT_TERM' in mtf_alignment:
                time_horizon = "5-15 trading days (short-term momentum only)"
            elif mtf_alignment == 'RANGE_BOUND':
                time_horizon = "Continuous (range trading until breakout)"
            elif score >= 7:
                time_horizon = "1-3 weeks (swing trade opportunity)"
            else:
                time_horizon = "5-10 trading days (moderate setup)"

            # === EXIT STRATEGY ===
            # Check if range trading
            vp_position = signals.get('vp_profile_position', '')

            if mtf_alignment == 'RANGE_BOUND' and vp_position == 'AT_POC':
                # Range trading specific exit strategy
                vp_vah = signals.get('vp_vah')
                vp_val = signals.get('vp_val')

                if vp_vah and vp_val:
                    exit_strategy = []
                    exit_strategy.append(f"Sell 100% near ${vp_vah:.2f} (VAH resistance)")
                    exit_strategy.append(f"Buy back near ${vp_val:.2f} (VAL support)")
                    exit_strategy.append("Stop loss: 2-3% outside range (breakout invalidates range)")
                    exit_strategy.append("Repeat until range breakout confirmed")
                    exit_strategy.append("Exit strategy if breakout: Follow new trend with appropriate stops")

            elif targets and len(targets) >= 2:
                exit_strategy = []
                if len(targets) >= 3:
                    exit_strategy.append(f"Take 50% profit at ${targets[0]['price']:.2f} ({targets[0]['level']})")
                    exit_strategy.append(f"Take 30% profit at ${targets[1]['price']:.2f} ({targets[1]['level']})")
                    exit_strategy.append(f"Take 20% profit at ${targets[2]['price']:.2f} ({targets[2]['level']}) or trail stop")
                elif len(targets) == 2:
                    exit_strategy.append(f"Take 60% profit at ${targets[0]['price']:.2f} ({targets[0]['level']})")
                    exit_strategy.append(f"Take 40% profit at ${targets[1]['price']:.2f} ({targets[1]['level']}) or trail stop")
                else:
                    exit_strategy.append(f"Take 70% profit at target, trail stop on remaining 30%")

                # Add stop management
                if 'SHORT_TERM' in mtf_alignment:
                    exit_strategy.append("Move stop to breakeven after 1% gain (short-term trade)")
                else:
                    exit_strategy.append("Move stop to breakeven after first target hit")

                # Add time-based exit
                if 'SHORT_TERM' in mtf_alignment:
                    exit_strategy.append("Exit completely if no progress within 10 trading days")

        return {
            'signal': signal,
            'confidence': confidence,
            'recommendation': recommendation,
            'takeaways': takeaways,
            'score_color': score_color,
            'risk_reward': risk_reward,
            'time_horizon': time_horizon,
            'exit_strategy': exit_strategy
        }

    def _refresh_price_data(self, ticker: str):
        """Fetch fresh price data for a ticker."""
        try:
            # Get ticker ID
            ticker_info = self.ticker_ops.get_ticker_by_symbol(ticker.upper())
            if not ticker_info:
                print(f"{self.formatter.RED}Error: Ticker {ticker} not found{self.formatter.NC}")
                return False
            
            ticker_id = ticker_info['ticker_id']
            
            # Use screener's data fetcher to update prices
            screener = DailyScreener()
            screener.data_fetcher.update_ticker_prices(ticker_id, ticker.upper())
            
            return True
        except Exception as e:
            logger.error(f"Error refreshing price data for {ticker}: {e}")
            print(f"{self.formatter.RED}Error refreshing price data: {e}{self.formatter.NC}")
            return False

    def _recalculate_indicators(self, ticker: str):
        """Recalculate indicators for a ticker and update daily_scans table."""
        try:
            # Get ticker ID
            ticker_info = self.ticker_ops.get_ticker_by_symbol(ticker.upper())
            if not ticker_info:
                print(f"{self.formatter.RED}Error: Ticker {ticker} not found{self.formatter.NC}")
                return False
            
            ticker_id = ticker_info['ticker_id']
            
            # Get price history from database
            price_data = self.data_fetcher.get_price_history(ticker_id, days=250)
            
            if price_data is None or len(price_data) < 50:
                print(f"{self.formatter.RED}Error: Insufficient price data for {ticker}{self.formatter.NC}")
                return False
            
            # Calculate indicators
            price_data = self.indicators.calculate_all_indicators(price_data)
            
            # Generate signals
            signals = self.indicators.generate_signals(price_data)
            
            # Get latest quote
            quote = self.data_fetcher.get_latest_quote(ticker.upper(), use_database=True)
            if quote is None:
                print(f"{self.formatter.RED}Error: Could not get quote for {ticker}{self.formatter.NC}")
                return False
            
            # Calculate priority score and alerts
            score_result = self.scorer.calculate_priority_score(signals, quote)
            
            # Get latest price from price data
            latest_price = float(price_data.iloc[-1]['close'])
            
            # Store/update in daily_scans table
            scan_date = date.today()
            scan_data = {
                'price': latest_price,
                'volume': float(price_data.iloc[-1]['volume']) if 'volume' in price_data.columns else 0,
                'priority_score': score_result.get('priority_score', 0),
                'priority_rank': 0,  # Will be set by update_rankings if needed
                'technical_signals': signals,
                'triggered_alerts': score_result.get('triggered_alerts', []),
                'pe_ratio': quote.get('pe_ratio'),
                'forward_pe': quote.get('forward_pe'),
                'news_sentiment_score': None,
                'scan_duration_seconds': 0,
            }
            
            # Store scan result
            self.scan_ops.store_scan_result(ticker_id, scan_date, scan_data)
            
            return True
        except Exception as e:
            logger.error(f"Error recalculating indicators for {ticker}: {e}")
            print(f"{self.formatter.RED}Error recalculating indicators: {e}{self.formatter.NC}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Show technical indicators')
    parser.add_argument('tickers', nargs='*', help='Ticker symbol(s) (optional, can specify multiple)')
    parser.add_argument(
        '--refresh',
        action='store_true',
        help='Recalculate indicators from existing price data and update database'
    )
    parser.add_argument(
        '--refresh-data',
        action='store_true',
        help='Fetch fresh price data first, then recalculate indicators (includes --refresh)'
    )
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed indicator breakdown for each ticker (default: comparison table for multiple tickers)'
    )

    args = parser.parse_args()

    display = IndicatorDisplay()
    
    # If no tickers provided, show guide
    if not args.tickers:
        display.show_all_indicators(
            None,
            refresh=args.refresh or args.refresh_data,
            refresh_data=args.refresh_data
        )
    elif len(args.tickers) == 1:
        # Single ticker - always show detailed view
        display.show_all_indicators(
            args.tickers[0],
            refresh=args.refresh or args.refresh_data,
            refresh_data=args.refresh_data
        )
    else:
        # Multiple tickers - show comparison table first
        ticker_data = display._show_comparison_table(
            args.tickers,
            refresh=args.refresh or args.refresh_data,
            refresh_data=args.refresh_data
        )
        
        # Display next steps with all tickers
        display_next_steps('indicators', context={'tickers': args.tickers, 'ticker': args.tickers[0] if args.tickers else None})
        
        # If --detailed flag is set, also show detailed views
        if args.detailed:
            print(f"\n{display.formatter.CYAN}{display.formatter.BOLD}{'='*120}{display.formatter.NC}")
            print(f"{display.formatter.CYAN}{display.formatter.BOLD}  DETAILED INDICATOR BREAKDOWN{display.formatter.NC}")
            print(f"{display.formatter.CYAN}{display.formatter.BOLD}{'='*120}{display.formatter.NC}\n")
            
            for i, ticker in enumerate(args.tickers):
                if i > 0:
                    # Add clear separator between tickers
                    print(f"\n{display.formatter.YELLOW}{'─'*120}{display.formatter.NC}\n")
                
                display.show_all_indicators(
                    ticker,
                    refresh=False,  # Already refreshed above
                    refresh_data=False
                )
        else:
            # Show hint about detailed view
            print(f"{display.formatter.YELLOW}Tip: Add --detailed flag to see full indicator breakdown for each ticker{display.formatter.NC}\n")
            print(f"{display.formatter.CYAN}Example: ./quick_run.sh indicators {' '.join(args.tickers)} --detailed{display.formatter.NC}\n")


if __name__ == '__main__':
    main()
