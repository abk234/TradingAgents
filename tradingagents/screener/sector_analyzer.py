"""
Sector Analyzer for TradingAgents
Analyze and rank market sectors for intelligent screening
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date
from decimal import Decimal

from tradingagents.database import DatabaseConnection

logger = logging.getLogger(__name__)


class SectorAnalyzer:
    """Analyze market sectors and identify strongest opportunities"""

    def __init__(self, db_conn: DatabaseConnection):
        """
        Initialize sector analyzer

        Args:
            db_conn: Database connection instance
        """
        self.db_conn = db_conn

    def analyze_all_sectors(self, analysis_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """
        Analyze all sectors and rank them by strength

        Args:
            analysis_date: Date to analyze (default: today)

        Returns:
            List of sector analysis dictionaries, sorted by strength
        """
        if analysis_date is None:
            analysis_date = date.today()

        logger.info(f"Analyzing all sectors for {analysis_date}")

        # Get all unique sectors from tickers
        sectors = self._get_active_sectors()

        sector_analyses = []
        for sector in sectors:
            analysis = self.analyze_sector(sector, analysis_date)
            if analysis:
                sector_analyses.append(analysis)

        # Sort by strength score (descending)
        sector_analyses.sort(key=lambda x: x['strength_score'], reverse=True)

        # Save to database
        self._save_sector_scores(sector_analyses, analysis_date)

        return sector_analyses

    def analyze_sector(self, sector: str, analysis_date: Optional[date] = None) -> Optional[Dict[str, Any]]:
        """
        Analyze a single sector

        Args:
            sector: Sector name
            analysis_date: Date to analyze (default: today)

        Returns:
            Sector analysis dictionary or None if no data
        """
        if analysis_date is None:
            analysis_date = date.today()

        try:
            with self.db_conn.get_connection() as conn:
                with conn.cursor() as cur:
                    # Get scan results for this sector
                    # Count buy signals by recommendation (aligned with screener display)
                    # BUY signals: STRONG BUY, BUY, BUY DIP, ACCUMULATION, BUY (Below VAL), etc.
                    query = """
                    SELECT
                        COUNT(*) as total_stocks,
                        COUNT(*) FILTER (
                            WHERE sr.recommendation IS NOT NULL 
                            AND (
                                sr.recommendation LIKE 'STRONG BUY%%' 
                                OR sr.recommendation LIKE 'BUY%%'
                                OR sr.recommendation LIKE '%%ACCUMULATION%%'
                                OR sr.recommendation LIKE '%%BUY DIP%%'
                            )
                        ) as buy_signals,
                        COUNT(*) FILTER (
                            WHERE sr.recommendation IS NOT NULL 
                            AND (
                                sr.recommendation = 'WAIT'
                                OR sr.recommendation = 'NEUTRAL'
                                OR sr.recommendation LIKE '%%BREAKOUT IMMINENT%%'
                            )
                        ) as wait_signals,
                        COUNT(*) FILTER (
                            WHERE sr.recommendation IS NOT NULL 
                            AND (
                                sr.recommendation LIKE 'SELL%%'
                                OR sr.recommendation LIKE '%%DISTRIBUTION%%'
                                OR sr.recommendation LIKE '%%SELL RALLY%%'
                            )
                        ) as sell_signals,
                        AVG(sr.priority_score) as avg_priority,
                        AVG((sr.technical_signals->>'rsi')::float) as avg_rsi,
                        AVG((sr.technical_signals->>'volume_ratio')::float) as avg_volume_ratio,
                        STDDEV(sr.priority_score) as priority_stddev
                    FROM daily_scans sr
                    JOIN tickers t ON sr.ticker_id = t.ticker_id
                    WHERE t.sector = %s
                      AND t.active = TRUE
                      AND sr.scan_date = %s
                    """

                    cur.execute(query, (sector, analysis_date))
                    result = cur.fetchone()

                    if not result:
                        logger.debug(f"No scan results for sector: {sector}")
                        return None
                    
                    # Check if we have enough columns
                    if len(result) < 8:
                        logger.warning(f"Unexpected result length {len(result)} for sector {sector}, expected 8")
                        return None
                    
                    # Check if there are any stocks
                    if result[0] == 0:
                        logger.debug(f"No stocks scanned for sector: {sector}")
                        return None

                    total_stocks = result[0] or 0
                    buy_signals = result[1] or 0
                    wait_signals = result[2] or 0
                    sell_signals = result[3] or 0
                    avg_priority = float(result[4]) if result[4] is not None else 0
                    avg_rsi = float(result[5]) if result[5] is not None else 50
                    avg_volume_ratio = float(result[6]) if result[6] is not None else 1.0
                    priority_stddev = float(result[7]) if result[7] is not None else 0

                    # Calculate strength score (0-100)
                    strength_score = self._calculate_strength_score(
                        total_stocks=total_stocks,
                        buy_signals=buy_signals,
                        avg_priority=avg_priority,
                        avg_rsi=avg_rsi,
                        avg_volume_ratio=avg_volume_ratio
                    )

                    # Determine momentum
                    momentum = self._determine_momentum(
                        buy_signals=buy_signals,
                        total_stocks=total_stocks,
                        avg_rsi=avg_rsi,
                        avg_volume_ratio=avg_volume_ratio
                    )

                    # Determine trend direction
                    trend_direction = self._determine_trend(avg_rsi)

                    return {
                        'sector': sector,
                        'strength_score': round(strength_score, 2),
                        'total_stocks': total_stocks,
                        'buy_signals': buy_signals,
                        'wait_signals': wait_signals,
                        'sell_signals': sell_signals,
                        'avg_priority': round(avg_priority, 2),
                        'avg_rsi': round(avg_rsi, 2),
                        'avg_volume_ratio': round(avg_volume_ratio, 2),
                        'priority_stddev': round(priority_stddev, 2),
                        'momentum': momentum,
                        'trend_direction': trend_direction,
                        'analysis_date': analysis_date
                    }

        except Exception as e:
            import traceback
            logger.error(f"Error analyzing sector {sector}: {e}")
            logger.debug(f"Traceback: {traceback.format_exc()}")
            return None

    def get_top_sectors(self, n: int = 3, analysis_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """
        Get top N sectors by strength

        Args:
            n: Number of top sectors to return
            analysis_date: Date to analyze (default: today)

        Returns:
            List of top N sector analyses
        """
        all_sectors = self.analyze_all_sectors(analysis_date)
        return all_sectors[:n]

    def get_stocks_from_top_sectors(
        self,
        top_n_sectors: int = 2,
        stocks_per_sector: int = 3,
        analysis_date: Optional[date] = None
    ) -> List[Tuple[str, str, float]]:
        """
        Get top stocks from the strongest sectors

        Args:
            top_n_sectors: Number of top sectors to consider
            stocks_per_sector: Number of stocks to get from each sector
            analysis_date: Date to analyze (default: today)

        Returns:
            List of (symbol, sector, priority_score) tuples
        """
        if analysis_date is None:
            analysis_date = date.today()

        # Get top sectors
        top_sectors = self.get_top_sectors(top_n_sectors, analysis_date)

        if not top_sectors:
            logger.warning("No sector data available")
            return []

        stocks = []
        for sector_data in top_sectors:
            sector = sector_data['sector']

            # Get top stocks from this sector
            sector_stocks = self._get_top_stocks_from_sector(
                sector,
                stocks_per_sector,
                analysis_date
            )

            stocks.extend(sector_stocks)

        return stocks

    def detect_sector_rotation(self, lookback_days: int = 5) -> List[Dict[str, Any]]:
        """
        Detect sector rotation (leadership changes)

        Args:
            lookback_days: Number of days to look back

        Returns:
            List of rotation events
        """
        try:
            with self.db_conn.get_connection() as conn:
                with conn.cursor() as cur:
                    query = """
                    WITH ranked_sectors AS (
                        SELECT
                            sector,
                            score_date,
                            strength_score,
                            ROW_NUMBER() OVER (PARTITION BY score_date ORDER BY strength_score DESC) as rank
                        FROM sector_scores
                        WHERE score_date >= CURRENT_DATE - INTERVAL '%s days'
                    ),
                    leadership_changes AS (
                        SELECT
                            curr.score_date,
                            prev.sector as from_sector,
                            curr.sector as to_sector,
                            curr.strength_score - prev.strength_score as strength_change
                        FROM ranked_sectors curr
                        JOIN ranked_sectors prev ON
                            curr.score_date = prev.score_date + INTERVAL '1 day'
                            AND curr.rank = 1
                            AND prev.rank = 1
                            AND curr.sector != prev.sector
                    )
                    SELECT * FROM leadership_changes
                    ORDER BY score_date DESC
                    """

                    cur.execute(query, (lookback_days,))
                    results = cur.fetchall()

                    rotations = []
                    for row in results:
                        rotations.append({
                            'rotation_date': row[0],
                            'from_sector': row[1],
                            'to_sector': row[2],
                            'strength_change': float(row[3]) if row[3] else 0
                        })

                    return rotations

        except Exception as e:
            logger.error(f"Error detecting sector rotation: {e}")
            return []

    def _calculate_strength_score(
        self,
        total_stocks: int,
        buy_signals: int,
        avg_priority: float,
        avg_rsi: float,
        avg_volume_ratio: float
    ) -> float:
        """
        Calculate sector strength score (0-100)

        Weighted components:
        - Buy signal ratio: 30%
        - Average priority score: 40%
        - RSI momentum: 15%
        - Volume strength: 15%
        """
        if total_stocks == 0:
            return 0.0

        # Buy signal ratio (0-100)
        buy_ratio = (buy_signals / total_stocks) * 100

        # RSI component (normalize to 0-100, with 50 as neutral)
        rsi_component = min(100, max(0, (avg_rsi - 30) / 0.4))  # 30-70 RSI maps to 0-100

        # Volume component (normalize to 0-100)
        volume_component = min(100, max(0, (avg_volume_ratio - 0.5) / 0.025))  # 0.5-3.0 volume ratio

        # Weighted average
        strength = (
            buy_ratio * 0.30 +
            avg_priority * 0.40 +
            rsi_component * 0.15 +
            volume_component * 0.15
        )

        return min(100.0, max(0.0, strength))

    def _determine_momentum(
        self,
        buy_signals: int,
        total_stocks: int,
        avg_rsi: float,
        avg_volume_ratio: float
    ) -> str:
        """Determine sector momentum: Strong, Moderate, Neutral, or Weak"""
        if total_stocks == 0:
            return "Neutral"

        buy_ratio = buy_signals / total_stocks

        # Strong momentum: High buy signals, strong RSI, high volume
        if buy_ratio >= 0.6 and avg_rsi >= 60 and avg_volume_ratio >= 1.5:
            return "Strong"

        # Moderate momentum: Good buy signals or strong RSI
        if buy_ratio >= 0.4 or (avg_rsi >= 55 and avg_volume_ratio >= 1.2):
            return "Moderate"

        # Weak momentum: Low buy signals, oversold, low volume
        if buy_ratio <= 0.2 and avg_rsi <= 40:
            return "Weak"

        # Default to neutral
        return "Neutral"

    def _determine_trend(self, avg_rsi: float) -> str:
        """Determine trend direction based on RSI: Up, Down, or Sideways"""
        if avg_rsi >= 60:
            return "Up"
        elif avg_rsi <= 40:
            return "Down"
        else:
            return "Sideways"

    def _get_active_sectors(self) -> List[str]:
        """Get list of all active sectors from database"""
        try:
            with self.db_conn.get_connection() as conn:
                with conn.cursor() as cur:
                    query = """
                    SELECT DISTINCT sector
                    FROM tickers
                    WHERE active = TRUE AND sector IS NOT NULL
                    ORDER BY sector
                    """
                    cur.execute(query)
                    results = cur.fetchall()
                    return [row[0] for row in results]

        except Exception as e:
            logger.error(f"Error getting active sectors: {e}")
            return []

    def _get_top_stocks_from_sector(
        self,
        sector: str,
        limit: int,
        analysis_date: date
    ) -> List[Tuple[str, str, float]]:
        """Get top stocks from a specific sector"""
        try:
            with self.db_conn.get_connection() as conn:
                with conn.cursor() as cur:
                    query = """
                    SELECT t.symbol, t.sector, sr.priority_score
                    FROM daily_scans sr
                    JOIN tickers t ON sr.ticker_id = t.ticker_id
                    WHERE t.sector = %s
                      AND t.active = TRUE
                      AND sr.scan_date = %s
                    ORDER BY sr.priority_score DESC
                    LIMIT %s
                    """

                    cur.execute(query, (sector, analysis_date, limit))
                    results = cur.fetchall()

                    return [(row[0], row[1], float(row[2])) for row in results]

        except Exception as e:
            logger.error(f"Error getting top stocks from sector {sector}: {e}")
            return []

    def _save_sector_scores(self, sector_analyses: List[Dict[str, Any]], analysis_date: date) -> None:
        """Save sector scores to database"""
        try:
            with self.db_conn.get_connection() as conn:
                with conn.cursor() as cur:
                    for sector in sector_analyses:
                        query = """
                        INSERT INTO sector_scores (
                            sector, score_date, strength_score, total_stocks,
                            buy_signals, wait_signals, sell_signals,
                            avg_priority_score, avg_rsi, avg_volume_ratio,
                            momentum, trend_direction
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (sector, score_date)
                        DO UPDATE SET
                            strength_score = EXCLUDED.strength_score,
                            total_stocks = EXCLUDED.total_stocks,
                            buy_signals = EXCLUDED.buy_signals,
                            wait_signals = EXCLUDED.wait_signals,
                            sell_signals = EXCLUDED.sell_signals,
                            avg_priority_score = EXCLUDED.avg_priority_score,
                            avg_rsi = EXCLUDED.avg_rsi,
                            avg_volume_ratio = EXCLUDED.avg_volume_ratio,
                            momentum = EXCLUDED.momentum,
                            trend_direction = EXCLUDED.trend_direction,
                            updated_at = CURRENT_TIMESTAMP
                        """

                        cur.execute(query, (
                            sector['sector'],
                            analysis_date,
                            sector['strength_score'],
                            sector['total_stocks'],
                            sector['buy_signals'],
                            sector['wait_signals'],
                            sector['sell_signals'],
                            sector['avg_priority'],
                            sector['avg_rsi'],
                            sector['avg_volume_ratio'],
                            sector['momentum'],
                            sector['trend_direction']
                        ))

                    conn.commit()
                    logger.info(f"Saved {len(sector_analyses)} sector scores to database")

        except Exception as e:
            logger.error(f"Error saving sector scores: {e}")


# Convenience functions
def analyze_sectors(db_conn: DatabaseConnection, analysis_date: Optional[date] = None) -> List[Dict[str, Any]]:
    """Quick function to analyze all sectors"""
    analyzer = SectorAnalyzer(db_conn)
    return analyzer.analyze_all_sectors(analysis_date)


def get_top_sectors(
    db_conn: DatabaseConnection,
    n: int = 3,
    analysis_date: Optional[date] = None
) -> List[Dict[str, Any]]:
    """Quick function to get top N sectors"""
    analyzer = SectorAnalyzer(db_conn)
    return analyzer.get_top_sectors(n, analysis_date)
