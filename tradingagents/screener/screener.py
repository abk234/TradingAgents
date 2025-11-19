"""
Daily Screener Module

Main screening logic that coordinates data fetching, analysis, and scoring.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import date, datetime
import time
import logging

from .data_fetcher import DataFetcher
from .indicators import TechnicalIndicators
from .scorer import PriorityScorer
from .entry_price_calculator import EntryPriceCalculator
from tradingagents.database import get_db_connection, TickerOperations
from tradingagents.database.scan_ops import ScanOperations
from tradingagents.validation.earnings_calendar import check_earnings_proximity

logger = logging.getLogger(__name__)


class DailyScreener:
    """Coordinate daily screening of watchlist tickers."""

    def __init__(self, db=None):
        """
        Initialize daily screener.

        Args:
            db: DatabaseConnection instance (optional)
        """
        self.db = db or get_db_connection()
        self.data_fetcher = DataFetcher(self.db)
        self.indicators = TechnicalIndicators()
        self.scorer = PriorityScorer()
        self.entry_calculator = EntryPriceCalculator()
        self.ticker_ops = TickerOperations(self.db)
        self.scan_ops = ScanOperations(self.db)

    def should_skip_ticker(self, symbol: str, analysis_date: date = None) -> Tuple[bool, str]:
        """
        Check if ticker should be skipped due to earnings proximity (Quick Win 4).
        
        Args:
            symbol: Ticker symbol
            analysis_date: Date of analysis (defaults to today)
            
        Returns:
            Tuple of (should_skip, reason)
        """
        if analysis_date is None:
            analysis_date = date.today()
        
        try:
            earnings_report = check_earnings_proximity(symbol, days_before=7, days_after=3)
            
            if earnings_report.is_in_proximity_window:
                days_until = earnings_report.days_until_next_earnings
                if days_until is not None and -3 <= days_until <= 7:
                    return True, f"Near earnings ({days_until} days) - skipping to avoid volatility"
            
            return False, ""
        except Exception as e:
            logger.debug(f"Could not check earnings for {symbol}: {e}")
            return False, ""  # Don't skip if we can't check

    def scan_ticker(
        self,
        ticker_id: int,
        symbol: str,
        skip_earnings_check: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Scan a single ticker.

        Args:
            ticker_id: Ticker ID
            symbol: Ticker symbol
            skip_earnings_check: If True, skip earnings proximity check (Quick Win 4)

        Returns:
            Dictionary with scan results
        """
        start_time = time.time()

        # Quick Win 4: Skip analysis near earnings
        if not skip_earnings_check:
            should_skip, reason = self.should_skip_ticker(symbol)
            if should_skip:
                logger.info(f"  ⊙ {symbol:6s} - Skipped: {reason}")
                return None

        try:
            # Get price history from database
            price_data = self.data_fetcher.get_price_history(ticker_id, days=250)

            if price_data is None or len(price_data) < 50:
                logger.warning(f"Insufficient data for {symbol}")
                return None

            # Calculate indicators
            price_data = self.indicators.calculate_all_indicators(price_data)

            # Generate signals
            signals = self.indicators.generate_signals(price_data)

            # Get latest quote from database (fast, no API calls)
            quote = self.data_fetcher.get_latest_quote(symbol, use_database=True)

            if quote is None:
                logger.warning(f"Could not get quote for {symbol}")
                return None

            # Calculate priority score
            score_result = self.scorer.calculate_priority_score(signals, quote)

            # Calculate entry price recommendation
            entry_data = self.entry_calculator.calculate_entry_price(
                current_price=quote['price'],
                technical_signals=signals,
                quote=quote
            )

            # Generate recommendation (plain text for database storage)
            recommendation = self._generate_recommendation_plain_text(
                rsi=signals.get('rsi'),
                signals=score_result['triggered_alerts'],
                technical_signals=signals
            )

            # Compile result
            result = {
                'ticker_id': ticker_id,
                'symbol': symbol,
                'price': quote['price'],
                'volume': quote['volume'],
                'priority_score': score_result['priority_score'],
                'technical_score': score_result['technical_score'],
                'volume_score': score_result['volume_score'],
                'momentum_score': score_result['momentum_score'],
                'fundamental_score': score_result['fundamental_score'],
                'triggered_alerts': score_result['triggered_alerts'],
                'technical_signals': signals,
                'pe_ratio': quote.get('pe_ratio'),
                'forward_pe': quote.get('forward_pe'),
                'market_cap': quote.get('market_cap'),
                'recommendation': recommendation,  # Store recommendation for sector analysis
                'scan_duration_seconds': int(time.time() - start_time),
                # Entry price tracking data
                **entry_data
            }

            logger.info(
                f"  ✓ {symbol:6s} - Score: {result['priority_score']:3d} "
                f"(T:{score_result['technical_score']} "
                f"V:{score_result['volume_score']} "
                f"M:{score_result['momentum_score']} "
                f"F:{score_result['fundamental_score']})"
            )

            return result

        except Exception as e:
            logger.error(f"  ✗ {symbol} - Error: {e}")
            return None

    def scan_all(
        self,
        update_prices: bool = True,
        store_results: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Scan all active tickers in watchlist.

        Args:
            update_prices: Whether to update price data first
            store_results: Whether to store results in database

        Returns:
            List of scan results, sorted by priority
        """
        logger.info("="*70)
        logger.info("Daily Screener - Starting Scan")
        logger.info("="*70)

        scan_date = date.today()
        start_time = time.time()

        # Get all active tickers
        tickers = self.ticker_ops.get_all_tickers(active_only=True)
        logger.info(f"Found {len(tickers)} active tickers")

        # Update price data if requested
        if update_prices:
            logger.info("\nUpdating price data...")
            stats = self.data_fetcher.update_all_tickers(
                ticker_list=tickers,
                incremental=True
            )
            logger.info(
                f"Price update complete: {stats['successful']}/{stats['total']} tickers, "
                f"{stats['records_added']} new records"
            )

        # Scan each ticker
        logger.info("\nScanning tickers...")
        results = []

        for ticker in tickers:
            result = self.scan_ticker(ticker['ticker_id'], ticker['symbol'])
            if result:
                results.append(result)

        # Sort by priority score
        results.sort(key=lambda x: x['priority_score'], reverse=True)

        # Assign rankings
        for i, result in enumerate(results):
            result['priority_rank'] = i + 1

        # Store results in database
        if store_results and results:
            logger.info("\nStoring scan results...")
            for result in results:
                scan_id = self.scan_ops.store_scan_result(
                    result['ticker_id'],
                    scan_date,
                    result
                )

                # Create entry price outcome tracking if entry price was calculated
                if (scan_id and result.get('entry_price_min') and
                    result.get('entry_price_max')):
                    from decimal import Decimal
                    self.scan_ops.create_entry_price_outcome(
                        scan_id=scan_id,
                        ticker_id=result['ticker_id'],
                        scan_date=scan_date,
                        entry_price_min=Decimal(str(result['entry_price_min'])),
                        entry_price_max=Decimal(str(result['entry_price_max'])),
                        recommended_timing=result.get('entry_timing')
                    )

            # Update rankings
            self.scan_ops.update_rankings(scan_date)
            logger.info(f"Stored {len(results)} scan results with entry price tracking")

        # Summary
        duration = time.time() - start_time
        logger.info("\n" + "="*70)
        logger.info("Scan Complete")
        logger.info("="*70)
        logger.info(f"Total tickers scanned: {len(results)}")
        logger.info(f"Duration: {duration:.1f} seconds")

        if results:
            avg_score = sum(r['priority_score'] for r in results) / len(results)
            logger.info(f"Average priority score: {avg_score:.1f}")
            logger.info(f"Highest score: {results[0]['priority_score']} ({results[0]['symbol']})")

        # If results were stored, fetch enriched data from database
        # This includes company_name, sector, and current prices
        if store_results and results:
            enriched_results = self.get_top_opportunities(
                limit=len(results),
                scan_date=scan_date
            )

            # Add current price and change_pct from latest price data
            for result in enriched_results:
                # Get latest price data for this ticker
                price_query = """
                    SELECT close, volume
                    FROM daily_prices
                    WHERE ticker_id = %s
                    ORDER BY price_date DESC
                    LIMIT 2
                """
                prices = self.scan_ops.db.execute_dict_query(
                    price_query,
                    (result['ticker_id'],)
                )

                if prices and len(prices) > 0:
                    result['current_price'] = float(prices[0]['close'])
                    result['name'] = result.get('company_name', 'N/A')

                    # Calculate change percentage
                    if len(prices) > 1:
                        prev_close = float(prices[1]['close'])
                        curr_close = float(prices[0]['close'])
                        result['change_pct'] = ((curr_close - prev_close) / prev_close) * 100
                    else:
                        result['change_pct'] = 0.0
                else:
                    result['current_price'] = 0.0
                    result['change_pct'] = 0.0
                    result['name'] = result.get('company_name', 'N/A')

            return enriched_results

        return results

    def get_top_opportunities(
        self,
        limit: int = 5,
        scan_date: date = None,
        filter_buy_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get top opportunities from latest scan.

        Args:
            limit: Number of results to return
            scan_date: Scan date (defaults to today)
            filter_buy_only: If True, prioritize BUY recommendations

        Returns:
            List of top opportunities with details, including dividend yield
        """
        results = self.scan_ops.get_top_opportunities(scan_date, limit * 3 if filter_buy_only else limit, filter_buy_only)
        
        # Enrich with current price and change
        for result in results:
            # Get latest price data
            price_query = """
                SELECT close, volume
                FROM daily_prices
                WHERE ticker_id = %s
                ORDER BY price_date DESC
                LIMIT 2
            """
            prices = self.scan_ops.db.execute_dict_query(
                price_query,
                (result['ticker_id'],)
            )
            
            if prices and len(prices) > 0:
                result['current_price'] = float(prices[0]['close'])
                result['name'] = result.get('company_name', 'N/A')
                
                # Calculate change percentage
                if len(prices) > 1:
                    prev_close = float(prices[1]['close'])
                    curr_close = float(prices[0]['close'])
                    result['change_pct'] = ((curr_close - prev_close) / prev_close) * 100
                else:
                    result['change_pct'] = 0.0
            else:
                result['current_price'] = result.get('price', 0.0)
                result['change_pct'] = 0.0
                result['name'] = result.get('company_name', 'N/A')
        
        return results

    def generate_report(
        self,
        results: List[Dict[str, Any]] = None,
        scan_date: date = None,
        top_n: int = 5
    ) -> str:
        """
        Generate a text report from scan results.

        Args:
            results: Scan results (if None, fetches from DB)
            scan_date: Scan date (defaults to today)
            top_n: Number of top opportunities to highlight

        Returns:
            Formatted report string
        """
        if results is None:
            results = self.get_top_opportunities(limit=20, scan_date=scan_date)

        if not results:
            return "No scan results available."

        scan_date = scan_date or date.today()

        # Build report
        lines = []
        lines.append("="*70)
        lines.append(f"DAILY SCREENING REPORT - {scan_date.strftime('%Y-%m-%d')}")
        lines.append("="*70)
        lines.append("")

        # Summary
        summary = self.scan_ops.get_scan_summary(scan_date)
        if summary:
            lines.append(f"Tickers Scanned: {summary.get('total_scanned', 0)}")
            lines.append(f"Average Score: {summary.get('avg_score', 0):.1f}")
            lines.append(f"Score Range: {summary.get('min_score', 0):.0f} - {summary.get('max_score', 0):.0f}")
            lines.append("")

        # Top opportunities
        lines.append(f"TOP {top_n} OPPORTUNITIES:")
        lines.append("-"*70)
        lines.append("")

        for i, result in enumerate(results[:top_n], 1):
            lines.append(f"{i}. {result.get('symbol', 'N/A')} - {result.get('company_name', 'N/A')}")
            lines.append(f"   Priority Score: {result.get('priority_score', 0)} (Rank #{result.get('priority_rank', 'N/A')})")
            lines.append(f"   Sector: {result.get('sector', 'N/A')}")
            lines.append(f"   Price: ${result.get('price', 0):.2f}")

            # Alerts
            alerts = result.get('triggered_alerts', [])
            if alerts:
                lines.append(f"   Alerts: {', '.join(alerts)}")

            # Key metrics
            signals_json = result.get('technical_signals')
            if isinstance(signals_json, str):
                import json
                try:
                    signals = json.loads(signals_json)
                except:
                    signals = {}
            else:
                signals = signals_json or {}

            rsi = signals.get('rsi')
            if rsi:
                lines.append(f"   RSI: {rsi:.1f}")

            lines.append("")

        # Alert summary
        if summary and summary.get('alert_breakdown'):
            lines.append("ALERT SUMMARY:")
            lines.append("-"*70)
            for alert_info in summary['alert_breakdown'][:10]:
                lines.append(f"  {alert_info['alert']}: {alert_info['count']} occurrences")
            lines.append("")

        lines.append("="*70)
        lines.append("End of Report")
        lines.append("="*70)

        return "\n".join(lines)

    def _generate_recommendation_plain_text(
        self,
        rsi: Optional[float],
        signals: List[str],
        technical_signals: Dict[str, Any]
    ) -> str:
        """
        Generate plain text recommendation (without Rich markup) for database storage.
        
        This mirrors the logic in cli_formatter._generate_recommendation but returns
        plain text suitable for database storage and sector analysis.
        
        Args:
            rsi: RSI value
            signals: List of triggered alert strings
            technical_signals: Dictionary of technical signals
            
        Returns:
            Plain text recommendation string (e.g., "STRONG BUY", "BUY", "HOLD", "SELL", "WAIT")
        """
        from typing import Optional as Opt
        
        if not technical_signals or not isinstance(technical_signals, dict):
            # Fallback to basic RSI if no signals
            if rsi is None:
                return "HOLD"
            if rsi < 30:
                return "BUY"
            elif rsi > 70:
                return "SELL"
            else:
                return "HOLD"

        # Check for Phase 3 Multi-Timeframe Analysis (highest priority)
        mtf_signal = technical_signals.get('mtf_signal')
        mtf_confidence = technical_signals.get('mtf_confidence', 0)

        if mtf_signal and mtf_confidence > 0.8:
            if rsi and rsi > 80:
                if mtf_signal == 'BUY_THE_DIP':
                    return "BUY DIP"
                else:
                    return "WAIT"
            elif rsi and rsi > 70:
                if mtf_signal == 'BUY_THE_DIP':
                    return "BUY DIP"
                else:
                    return "WAIT"
            
            # Normal multi-timeframe signals
            if mtf_signal == 'STRONG_BUY':
                return "STRONG BUY"
            elif mtf_signal == 'BUY_THE_DIP':
                return "BUY DIP"
            elif mtf_signal == 'BUY':
                return "BUY"
            elif mtf_signal == 'STRONG_SELL':
                return "STRONG SELL"
            elif mtf_signal == 'SELL_THE_RALLY':
                return "SELL RALLY"

        # Check for Phase 3 Institutional Activity
        of_signal = technical_signals.get('of_signal')
        if of_signal:
            if rsi and rsi > 80:
                if of_signal in ['BULLISH_ACCUMULATION', 'STRONG_BUYING']:
                    return "WAIT"
                elif of_signal == 'BEARISH_DISTRIBUTION':
                    return "DISTRIBUTION"
                elif of_signal == 'STRONG_SELLING':
                    return "STRONG SELL"
            elif rsi and rsi > 70:
                if of_signal in ['STRONG_BUYING', 'BULLISH_ACCUMULATION']:
                    return "WAIT"
            
            # Normal institutional signals
            if of_signal == 'BULLISH_ACCUMULATION':
                return "ACCUMULATION"
            elif of_signal == 'BEARISH_DISTRIBUTION':
                return "DISTRIBUTION"
            elif of_signal == 'STRONG_BUYING':
                return "STRONG BUY"
            elif of_signal == 'STRONG_SELLING':
                return "STRONG SELL"

        # Check for Phase 3 Volume Profile position
        vp_position = technical_signals.get('vp_profile_position')
        if vp_position:
            if vp_position == 'BELOW_VALUE_AREA':
                return "BUY (Below VAL)"
            elif vp_position == 'ABOVE_VALUE_AREA':
                return "SELL (Above VAH)"

        # Check for Phase 2 RSI Divergence
        bullish_div = technical_signals.get('rsi_bullish_divergence', False)
        bearish_div = technical_signals.get('rsi_bearish_divergence', False)
        div_strength = technical_signals.get('rsi_divergence_strength', 0)

        if bullish_div and div_strength > 0.7:
            return "REVERSAL (Bullish Div)"
        elif bearish_div and div_strength > 0.7:
            return "REVERSAL (Bearish Div)"

        # Check for Phase 2 BB Squeeze
        bb_squeeze = technical_signals.get('bb_squeeze_detected', False)
        if bb_squeeze:
            return "BREAKOUT IMMINENT"

        # Fall back to Phase 1-2 basic signals
        macd_bullish = technical_signals.get('macd_bullish_crossover', False)
        macd_bearish = technical_signals.get('macd_bearish_crossover', False)
        volume_ratio = technical_signals.get('volume_ratio', 1.0)

        # Check for MACD in signal list
        if 'MACD_BULLISH_CROSS' in signals:
            macd_bullish = True
        if 'MACD_BEARISH_CROSS' in signals:
            macd_bearish = True

        # Check for other signals
        rsi_oversold = 'RSI_OVERSOLD' in signals or (rsi and rsi < 30)
        rsi_overbought = 'RSI_OVERBOUGHT' in signals or (rsi and rsi > 70)
        volume_spike = 'VOLUME_SPIKE' in signals or volume_ratio > 1.5
        bb_lower = 'BB_LOWER_TOUCH' in signals or technical_signals.get('near_bb_lower', False)
        bb_upper = 'BB_UPPER_TOUCH' in signals or technical_signals.get('near_bb_upper', False)

        # STRONG BUY: RSI oversold + MACD bullish + volume spike
        if rsi_oversold and macd_bullish and volume_spike:
            return "STRONG BUY"

        # STRONG BUY: RSI oversold + MACD bullish
        if rsi_oversold and macd_bullish:
            return "STRONG BUY"

        # STRONG BUY: RSI oversold + BB lower touch
        if rsi_oversold and bb_lower:
            return "STRONG BUY"

        # BUY: RSI oversold alone (stronger signal if extremely oversold)
        if rsi_oversold:
            if rsi and rsi < 20:
                return "STRONG BUY"  # Extremely oversold
            return "BUY"

        # BUY: MACD bullish + RSI neutral/low
        if macd_bullish and rsi and rsi < 50:
            return "BUY"

        # BUY: MACD bullish + volume spike
        if macd_bullish and volume_spike:
            return "BUY"

        # STRONG SELL: RSI overbought + MACD bearish
        if rsi_overbought and macd_bearish:
            return "STRONG SELL"

        # STRONG SELL: RSI overbought + BB upper touch
        if rsi_overbought and bb_upper:
            return "STRONG SELL"

        # SELL: RSI overbought alone
        if rsi_overbought:
            return "SELL"

        # SELL: MACD bearish + RSI high
        if macd_bearish and rsi and rsi > 50:
            return "SELL"

        # WAIT: MACD bullish but RSI high (wait for pullback)
        if macd_bullish and rsi and rsi > 70:
            return "WAIT"

        # WAIT: MACD bearish but RSI low (might bounce)
        if macd_bearish and rsi and rsi < 30:
            return "WAIT"

        # NEUTRAL: MACD bullish or RSI in neutral range
        if macd_bullish or (rsi and rsi >= 30 and rsi <= 50):
            return "NEUTRAL"

        # Default neutral
        return "HOLD"
