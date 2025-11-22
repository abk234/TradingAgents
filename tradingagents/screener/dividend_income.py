# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Dividend Income Screener

Specialized screener for finding stocks suitable for living off dividend income.

DIVIDEND INCOME CRITERIA
========================

This screener focuses on sustainable dividend income for retirement or passive income.

Key Requirements:
-----------------
1. Dividend Yield: 3%+ (4%+ preferred)
2. Dividend Safety: Payout ratio < 80%
3. Dividend Consistency: 5+ consecutive years (10+ preferred)
4. Dividend Growth: Positive growth over 3-5 years
5. Financial Stability: Profitable with manageable debt
6. Price Stability: Lower volatility preferred

Scoring System:
--------------
- Yield Score (30%): Based on dividend yield
- Safety Score (25%): Based on payout ratio and financial health
- Consistency Score (20%): Based on payment history
- Growth Score (15%): Based on dividend growth rate
- Stability Score (10%): Based on price volatility

Income Ranking:
--------------
Results are ranked by "Income Score" which prioritizes:
1. High sustainable yield
2. Dividend safety and consistency
3. Dividend growth potential
"""

from typing import List, Dict, Any, Optional
from datetime import date
import logging

from .data_fetcher import DataFetcher
from .indicators import TechnicalIndicators
from tradingagents.database import get_db_connection, TickerOperations

logger = logging.getLogger(__name__)


class DividendIncomeScreener:
    """Screen for dividend income stocks suitable for living off dividends."""

    def __init__(self, db=None):
        """
        Initialize dividend income screener.

        Args:
            db: DatabaseConnection instance (optional)
        """
        self.db = db or get_db_connection()
        self.data_fetcher = DataFetcher(self.db)
        self.indicators = TechnicalIndicators()
        self.ticker_ops = TickerOperations(self.db)

    def calculate_income_score(
        self,
        dividend_yield: float,
        payout_ratio: Optional[float],
        consecutive_years: int,
        dividend_growth_1yr: Optional[float],
        dividend_growth_3yr: Optional[float],
        current_price: float,
        volatility: Optional[float],
        pe_ratio: Optional[float],
        debt_to_equity: Optional[float]
    ) -> Dict[str, Any]:
        """
        Calculate income score based on dividend income criteria.

        Args:
            dividend_yield: Annual dividend yield (as decimal, e.g., 0.04 for 4%)
            payout_ratio: Dividend payout ratio (as decimal)
            consecutive_years: Number of consecutive years paying dividends
            dividend_growth_1yr: 1-year dividend growth rate
            dividend_growth_3yr: 3-year dividend growth rate
            current_price: Current stock price
            volatility: Price volatility (standard deviation)
            pe_ratio: Price-to-earnings ratio
            debt_to_equity: Debt-to-equity ratio

        Returns:
            Dictionary with score breakdown and reasoning
        """
        score = 0
        max_score = 100
        reasons = []
        warnings = []

        # === 1. YIELD SCORE (30 points) ===
        yield_score = 0
        if dividend_yield >= 0.06:  # 6%+
            yield_score = 30
            reasons.append(f"Excellent yield: {dividend_yield:.2%}")
        elif dividend_yield >= 0.05:  # 5-6%
            yield_score = 27
            reasons.append(f"Very good yield: {dividend_yield:.2%}")
        elif dividend_yield >= 0.04:  # 4-5%
            yield_score = 24
            reasons.append(f"Good yield: {dividend_yield:.2%}")
        elif dividend_yield >= 0.03:  # 3-4%
            yield_score = 18
            reasons.append(f"Moderate yield: {dividend_yield:.2%}")
        elif dividend_yield >= 0.02:  # 2-3%
            yield_score = 10
            warnings.append(f"Low yield: {dividend_yield:.2%} - may not meet income needs")
        else:  # <2%
            yield_score = 0
            warnings.append(f"Very low yield: {dividend_yield:.2%} - unsuitable for income")

        score += yield_score

        # === 2. SAFETY SCORE (25 points) ===
        safety_score = 0

        # Payout ratio (15 points)
        if payout_ratio is not None:
            if payout_ratio <= 0.50:  # ≤50%
                safety_score += 15
                reasons.append(f"Very safe payout ratio: {payout_ratio:.1%}")
            elif payout_ratio <= 0.60:  # 50-60%
                safety_score += 13
                reasons.append(f"Safe payout ratio: {payout_ratio:.1%}")
            elif payout_ratio <= 0.70:  # 60-70%
                safety_score += 10
                reasons.append(f"Reasonable payout ratio: {payout_ratio:.1%}")
            elif payout_ratio <= 0.80:  # 70-80%
                safety_score += 6
                warnings.append(f"Elevated payout ratio: {payout_ratio:.1%}")
            else:  # >80%
                safety_score += 0
                warnings.append(f"High payout ratio: {payout_ratio:.1%} - dividend at risk")
        else:
            safety_score += 7  # Neutral if no data

        # Financial health (10 points)
        if pe_ratio is not None and pe_ratio > 0:
            if pe_ratio <= 15:
                safety_score += 5
                reasons.append(f"Attractive valuation: P/E {pe_ratio:.1f}")
            elif pe_ratio <= 25:
                safety_score += 3
            elif pe_ratio > 40:
                warnings.append(f"High valuation: P/E {pe_ratio:.1f}")

        if debt_to_equity is not None:
            if debt_to_equity <= 0.5:
                safety_score += 5
                reasons.append(f"Low debt: D/E {debt_to_equity:.2f}")
            elif debt_to_equity <= 1.0:
                safety_score += 3
            else:
                warnings.append(f"High debt: D/E {debt_to_equity:.2f}")

        score += safety_score

        # === 3. CONSISTENCY SCORE (20 points) ===
        consistency_score = 0
        if consecutive_years >= 25:
            consistency_score = 20
            reasons.append(f"Dividend Aristocrat: {consecutive_years} consecutive years")
        elif consecutive_years >= 10:
            consistency_score = 17
            reasons.append(f"Strong dividend history: {consecutive_years} years")
        elif consecutive_years >= 5:
            consistency_score = 12
            reasons.append(f"Good dividend history: {consecutive_years} years")
        elif consecutive_years >= 3:
            consistency_score = 6
            warnings.append(f"Short dividend history: {consecutive_years} years")
        else:
            consistency_score = 0
            warnings.append(f"Very short dividend history: {consecutive_years} years")

        score += consistency_score

        # === 4. GROWTH SCORE (15 points) ===
        growth_score = 0

        # Prioritize 3-year growth (more stable indicator)
        growth_rate = dividend_growth_3yr if dividend_growth_3yr is not None else dividend_growth_1yr

        if growth_rate is not None:
            if growth_rate >= 0.10:  # 10%+
                growth_score = 15
                reasons.append(f"Strong dividend growth: {growth_rate:.1%}")
            elif growth_rate >= 0.07:  # 7-10%
                growth_score = 12
                reasons.append(f"Good dividend growth: {growth_rate:.1%}")
            elif growth_rate >= 0.05:  # 5-7%
                growth_score = 9
                reasons.append(f"Moderate dividend growth: {growth_rate:.1%}")
            elif growth_rate >= 0.03:  # 3-5%
                growth_score = 6
                reasons.append(f"Modest dividend growth: {growth_rate:.1%}")
            elif growth_rate >= 0:  # 0-3%
                growth_score = 3
                warnings.append(f"Low dividend growth: {growth_rate:.1%}")
            else:  # Negative growth
                growth_score = 0
                warnings.append(f"Declining dividends: {growth_rate:.1%}")
        else:
            growth_score = 5  # Neutral if no data

        score += growth_score

        # === 5. STABILITY SCORE (10 points) ===
        stability_score = 0

        if volatility is not None:
            if volatility <= 0.20:  # Low volatility
                stability_score = 10
                reasons.append("Low price volatility")
            elif volatility <= 0.30:  # Moderate volatility
                stability_score = 7
            elif volatility <= 0.40:  # Above average volatility
                stability_score = 4
                warnings.append("Moderate price volatility")
            else:  # High volatility
                stability_score = 0
                warnings.append("High price volatility - capital at risk")
        else:
            stability_score = 5  # Neutral if no data

        score += stability_score

        # Normalize score to 0-100
        normalized_score = int((score / max_score) * 100)

        # Determine income category
        if normalized_score >= 80:
            category = "EXCELLENT"
        elif normalized_score >= 70:
            category = "VERY GOOD"
        elif normalized_score >= 60:
            category = "GOOD"
        elif normalized_score >= 50:
            category = "FAIR"
        else:
            category = "POOR"

        return {
            'income_score': normalized_score,
            'yield_score': yield_score,
            'safety_score': safety_score,
            'consistency_score': consistency_score,
            'growth_score': growth_score,
            'stability_score': stability_score,
            'category': category,
            'reasons': reasons,
            'warnings': warnings
        }

    def scan_ticker_for_income(
        self,
        ticker_id: int,
        symbol: str
    ) -> Optional[Dict[str, Any]]:
        """
        Scan a single ticker for dividend income suitability.

        Args:
            ticker_id: Ticker ID
            symbol: Ticker symbol

        Returns:
            Dictionary with scan results or None if unsuitable
        """
        try:
            # Get dividend data from cache
            dividend_query = """
                SELECT
                    dividend_yield_pct,
                    annual_dividend,
                    current_price,
                    payout_ratio_pct,
                    consecutive_years_paid,
                    dividend_growth_1yr_pct,
                    dividend_growth_3yr_pct,
                    payout_frequency,
                    last_ex_date,
                    calculated_at
                FROM dividend_yield_cache
                WHERE ticker_id = %s
                    AND valid_until > CURRENT_TIMESTAMP
            """
            dividend_data = self.db.execute_dict_query(dividend_query, (ticker_id,))

            if not dividend_data or len(dividend_data) == 0:
                logger.debug(f"  ⊙ {symbol:6s} - Skipped: No dividend data")
                return None

            div = dividend_data[0]

            # Quick filters - skip if doesn't meet minimum criteria
            dividend_yield = float(div['dividend_yield_pct']) / 100 if div['dividend_yield_pct'] else 0

            if dividend_yield < 0.025:  # Less than 2.5% - not suitable for income
                logger.debug(f"  ⊙ {symbol:6s} - Skipped: Yield too low ({dividend_yield:.2%})")
                return None

            consecutive_years = int(div['consecutive_years_paid']) if div['consecutive_years_paid'] else 0
            if consecutive_years < 3:  # Less than 3 years - too risky
                logger.debug(f"  ⊙ {symbol:6s} - Skipped: Dividend history too short ({consecutive_years} years)")
                return None

            # Get fundamental data from tickers table
            fundamental_query = """
                SELECT market_cap
                FROM tickers
                WHERE ticker_id = %s
            """
            fundamental_data = self.db.execute_dict_query(fundamental_query, (ticker_id,))

            pe_ratio = None
            debt_to_equity = None
            market_cap = None

            if fundamental_data and len(fundamental_data) > 0:
                fund = fundamental_data[0]
                # PE ratio and debt_to_equity not in tickers table - will be None for now
                pe_ratio = None
                debt_to_equity = None
                market_cap = float(fund['market_cap']) if fund['market_cap'] else None

            # Get price data for volatility calculation
            price_data = self.data_fetcher.get_price_history(ticker_id, days=90)
            volatility = None

            if price_data is not None and len(price_data) > 20:
                returns = price_data['close'].pct_change().dropna()
                volatility = returns.std() * (252 ** 0.5)  # Annualized volatility

            # Calculate income score
            current_price = float(div['current_price']) if div['current_price'] else 0
            payout_ratio = float(div['payout_ratio_pct']) / 100 if div['payout_ratio_pct'] else None
            dividend_growth_1yr = float(div['dividend_growth_1yr_pct']) / 100 if div['dividend_growth_1yr_pct'] else None
            dividend_growth_3yr = float(div['dividend_growth_3yr_pct']) / 100 if div['dividend_growth_3yr_pct'] else None

            score_result = self.calculate_income_score(
                dividend_yield=dividend_yield,
                payout_ratio=payout_ratio,
                consecutive_years=consecutive_years,
                dividend_growth_1yr=dividend_growth_1yr,
                dividend_growth_3yr=dividend_growth_3yr,
                current_price=current_price,
                volatility=volatility,
                pe_ratio=pe_ratio,
                debt_to_equity=debt_to_equity
            )

            # Calculate annual income per $10,000 invested
            annual_income_per_10k = dividend_yield * 10000 if dividend_yield else 0

            # Get trading metrics from latest daily_scans entry (if available)
            trading_metrics_query = """
                SELECT
                    entry_price_min,
                    entry_price_max,
                    target,
                    stop_loss,
                    gain_percent,
                    risk_reward_ratio,
                    technical_signals,
                    recommendation
                FROM daily_scans
                WHERE ticker_id = %s
                ORDER BY scan_date DESC
                LIMIT 1
            """
            trading_metrics_data = self.db.execute_dict_query(trading_metrics_query, (ticker_id,))

            # Extract trading metrics
            entry_price_min = None
            entry_price_max = None
            target_price = None
            stop_loss = None
            gain_percent = None
            risk_reward_ratio = None
            technical_signals = None
            recommendation = None

            if trading_metrics_data and len(trading_metrics_data) > 0:
                metrics = trading_metrics_data[0]
                entry_price_min = float(metrics['entry_price_min']) if metrics['entry_price_min'] else None
                entry_price_max = float(metrics['entry_price_max']) if metrics['entry_price_max'] else None
                target_price = float(metrics['target']) if metrics['target'] else None
                stop_loss = float(metrics['stop_loss']) if metrics['stop_loss'] else None
                gain_percent = float(metrics['gain_percent']) if metrics['gain_percent'] else None
                risk_reward_ratio = float(metrics['risk_reward_ratio']) if metrics['risk_reward_ratio'] else None
                technical_signals = metrics['technical_signals']
                recommendation = metrics['recommendation']

            result = {
                'ticker_id': ticker_id,
                'symbol': symbol,
                'current_price': current_price,
                'dividend_yield': dividend_yield,
                'annual_dividend': float(div['annual_dividend']) if div['annual_dividend'] else 0,
                'payout_ratio': payout_ratio,
                'consecutive_years': consecutive_years,
                'dividend_growth_1yr': dividend_growth_1yr,
                'dividend_growth_3yr': dividend_growth_3yr,
                'payout_frequency': div['payout_frequency'],
                'last_ex_date': div['last_ex_date'],
                'pe_ratio': pe_ratio,
                'debt_to_equity': debt_to_equity,
                'market_cap': market_cap,
                'volatility': volatility,
                'annual_income_per_10k': annual_income_per_10k,
                # Trading metrics from daily_scans
                'entry_price_min': entry_price_min,
                'entry_price_max': entry_price_max,
                'target': target_price,
                'stop_loss': stop_loss,
                'gain_percent': gain_percent,
                'risk_reward_ratio': risk_reward_ratio,
                'technical_signals': technical_signals,
                '_recommendation': recommendation,
                **score_result
            }

            logger.info(
                f"  ✓ {symbol:6s} - Income Score: {score_result['income_score']:3d} "
                f"| Yield: {dividend_yield:.2%} "
                f"| {score_result['category']}"
            )

            return result

        except Exception as e:
            logger.error(f"  ✗ {symbol} - Error: {e}")
            return None

    def scan_all_for_income(
        self,
        min_yield: float = 0.025,
        min_consecutive_years: int = 3,
        top_n: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Scan all tickers for dividend income opportunities.

        Args:
            min_yield: Minimum dividend yield (default 2.5%)
            min_consecutive_years: Minimum consecutive years (default 3)
            top_n: Number of top results to return (default 20)

        Returns:
            List of top dividend income opportunities, sorted by income score
        """
        logger.info("=" * 70)
        logger.info("Dividend Income Screener - Finding Best Income Stocks")
        logger.info("=" * 70)

        # Get all tickers with dividend data
        query = """
            SELECT DISTINCT t.ticker_id, t.symbol, t.company_name
            FROM tickers t
            JOIN dividend_yield_cache dyc ON t.ticker_id = dyc.ticker_id
            WHERE t.active = TRUE
                AND dyc.dividend_yield_pct >= %s
                AND dyc.consecutive_years_paid >= %s
                AND dyc.valid_until > CURRENT_TIMESTAMP
            ORDER BY t.symbol
        """

        tickers = self.db.execute_dict_query(
            query,
            (min_yield * 100, min_consecutive_years)
        )

        if not tickers:
            tickers = []

        logger.info(f"Found {len(tickers)} tickers with dividend data meeting minimum criteria")
        logger.info(f"Minimum yield: {min_yield:.2%}, Minimum history: {min_consecutive_years} years")
        logger.info("")
        logger.info("Scanning tickers...")

        results = []
        for ticker in tickers:
            result = self.scan_ticker_for_income(ticker['ticker_id'], ticker['symbol'])
            if result:
                result['company_name'] = ticker['company_name']
                results.append(result)

        # Sort by income score
        results.sort(key=lambda x: x['income_score'], reverse=True)

        # Take top N
        top_results = results[:top_n]

        logger.info("")
        logger.info("=" * 70)
        logger.info("Scan Complete")
        logger.info("=" * 70)
        logger.info(f"Total tickers scanned: {len(results)}")
        logger.info(f"Returning top {len(top_results)} income opportunities")

        if top_results:
            avg_score = sum(r['income_score'] for r in top_results) / len(top_results)
            avg_yield = sum(r['dividend_yield'] for r in top_results) / len(top_results)
            logger.info(f"Average income score: {avg_score:.1f}")
            logger.info(f"Average yield: {avg_yield:.2%}")
            logger.info(f"Top stock: {top_results[0]['symbol']} (Score: {top_results[0]['income_score']}, Yield: {top_results[0]['dividend_yield']:.2%})")

        return top_results
