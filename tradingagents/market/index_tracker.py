# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Market Index Tracker

Tracks major market indexes to provide market context for trading decisions.
Helps identify market regime (bull/bear/neutral) and sector rotation.
"""

from typing import Dict, Any, List
import yfinance as yf
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class MarketIndexTracker:
    """Track and analyze major market indexes."""

    # Major market indexes
    INDEXES = {
        # Broad Market
        '^GSPC': {'name': 'S&P 500', 'category': 'Broad Market', 'description': 'Large cap stocks'},
        '^DJI': {'name': 'Dow Jones', 'category': 'Broad Market', 'description': 'Blue chip industrials'},
        '^IXIC': {'name': 'NASDAQ', 'category': 'Broad Market', 'description': 'Technology heavy'},
        '^RUT': {'name': 'Russell 2000', 'category': 'Broad Market', 'description': 'Small cap stocks'},

        # Volatility
        '^VIX': {'name': 'VIX', 'category': 'Volatility', 'description': 'Fear index'},

        # Sector ETFs
        'XLK': {'name': 'Technology', 'category': 'Sector', 'description': 'Tech sector'},
        'XLF': {'name': 'Financials', 'category': 'Sector', 'description': 'Financial sector'},
        'XLV': {'name': 'Healthcare', 'category': 'Sector', 'description': 'Healthcare sector'},
        'XLE': {'name': 'Energy', 'category': 'Sector', 'description': 'Energy sector'},
        'XLY': {'name': 'Consumer Discretionary', 'category': 'Sector', 'description': 'Consumer cyclical'},
        'XLP': {'name': 'Consumer Staples', 'category': 'Sector', 'description': 'Consumer defensive'},
        'XLI': {'name': 'Industrials', 'category': 'Sector', 'description': 'Industrial sector'},
        'XLB': {'name': 'Materials', 'category': 'Sector', 'description': 'Basic materials'},
        'XLRE': {'name': 'Real Estate', 'category': 'Sector', 'description': 'Real estate sector'},
        'XLU': {'name': 'Utilities', 'category': 'Sector', 'description': 'Utilities sector'},
        'XLC': {'name': 'Communication', 'category': 'Sector', 'description': 'Communication services'},

        # International
        'EFA': {'name': 'EAFE', 'category': 'International', 'description': 'Developed markets (ex-US)'},
        'EEM': {'name': 'Emerging Markets', 'category': 'International', 'description': 'Emerging markets'},
        'FXI': {'name': 'China', 'category': 'International', 'description': 'China large cap'},

        # Fixed Income
        'TLT': {'name': '20+ Year Treasury', 'category': 'Fixed Income', 'description': 'Long-term bonds'},
        'IEF': {'name': '7-10 Year Treasury', 'category': 'Fixed Income', 'description': 'Mid-term bonds'},
        'SHY': {'name': '1-3 Year Treasury', 'category': 'Fixed Income', 'description': 'Short-term bonds'},

        # Commodities
        'GLD': {'name': 'Gold', 'category': 'Commodities', 'description': 'Gold ETF'},
        'USO': {'name': 'Oil', 'category': 'Commodities', 'description': 'Crude oil ETF'},
    }

    def __init__(self):
        """Initialize index tracker."""
        pass

    def get_all_indexes(self) -> Dict[str, Any]:
        """
        Get current data for all tracked indexes.

        Returns:
            Dictionary with index data organized by category
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'categories': {},
            'market_summary': {},
            'sector_rotation': {},
            'market_regime': {}
        }

        # Fetch data for all indexes
        index_data = {}
        for symbol, info in self.INDEXES.items():
            try:
                data = self._fetch_index_data(symbol)
                if data:
                    data['info'] = info
                    index_data[symbol] = data

                    # Organize by category
                    category = info['category']
                    if category not in results['categories']:
                        results['categories'][category] = []
                    results['categories'][category].append({
                        'symbol': symbol,
                        'name': info['name'],
                        **data
                    })
            except Exception as e:
                logger.error(f"Error fetching {symbol}: {e}")

        # Calculate market summary
        results['market_summary'] = self._calculate_market_summary(index_data)

        # Detect sector rotation
        results['sector_rotation'] = self._detect_sector_rotation(index_data)

        # Determine market regime
        results['market_regime'] = self._determine_market_regime(index_data)

        return results

    def _fetch_index_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch data for a single index."""
        try:
            ticker = yf.Ticker(symbol)

            # Get historical data (30 days)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            hist = ticker.history(start=start_date, end=end_date)

            if hist.empty:
                return None

            # Calculate metrics
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price

            # Returns
            day_change = ((current_price - prev_close) / prev_close) * 100
            week_change = ((current_price - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5]) * 100 if len(hist) >= 5 else 0
            month_change = ((current_price - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100

            # Volatility
            daily_returns = hist['Close'].pct_change()
            volatility = daily_returns.std() * (252 ** 0.5) * 100  # Annualized volatility

            # Trend
            sma_20 = hist['Close'].tail(20).mean()
            sma_50 = hist['Close'].mean()  # Use all 30 days as proxy for 50-day

            trend = 'UPTREND' if current_price > sma_20 > sma_50 else 'DOWNTREND' if current_price < sma_20 < sma_50 else 'NEUTRAL'

            return {
                'price': current_price,
                'day_change_pct': day_change,
                'week_change_pct': week_change,
                'month_change_pct': month_change,
                'volatility_pct': volatility,
                'sma_20': sma_20,
                'sma_50': sma_50,
                'trend': trend,
                'volume': hist['Volume'].iloc[-1] if 'Volume' in hist.columns else None
            }

        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None

    def _calculate_market_summary(self, index_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall market summary."""
        sp500 = index_data.get('^GSPC', {})
        nasdaq = index_data.get('^IXIC', {})
        dow = index_data.get('^DJI', {})
        vix = index_data.get('^VIX', {})

        # Market breadth (how many major indexes are up)
        major_indexes = [sp500, nasdaq, dow]
        indexes_up = sum(1 for idx in major_indexes if idx.get('day_change_pct', 0) > 0)
        breadth_pct = (indexes_up / len(major_indexes)) * 100 if major_indexes else 0

        # Average performance
        avg_day_change = sum(idx.get('day_change_pct', 0) for idx in major_indexes) / len(major_indexes) if major_indexes else 0
        avg_week_change = sum(idx.get('week_change_pct', 0) for idx in major_indexes) / len(major_indexes) if major_indexes else 0
        avg_month_change = sum(idx.get('month_change_pct', 0) for idx in major_indexes) / len(major_indexes) if major_indexes else 0

        # Market sentiment
        vix_level = vix.get('price', 15)
        if vix_level < 15:
            sentiment = 'COMPLACENT'
        elif vix_level < 20:
            sentiment = 'CALM'
        elif vix_level < 30:
            sentiment = 'NERVOUS'
        else:
            sentiment = 'FEARFUL'

        # Market strength
        if breadth_pct >= 67 and avg_day_change > 0.5:
            strength = 'STRONG_BULLISH'
        elif breadth_pct >= 67:
            strength = 'BULLISH'
        elif breadth_pct <= 33 and avg_day_change < -0.5:
            strength = 'STRONG_BEARISH'
        elif breadth_pct <= 33:
            strength = 'BEARISH'
        else:
            strength = 'MIXED'

        return {
            'breadth_pct': breadth_pct,
            'indexes_up': indexes_up,
            'indexes_down': len(major_indexes) - indexes_up,
            'avg_day_change_pct': avg_day_change,
            'avg_week_change_pct': avg_week_change,
            'avg_month_change_pct': avg_month_change,
            'vix_level': vix_level,
            'sentiment': sentiment,
            'market_strength': strength
        }

    def _detect_sector_rotation(self, index_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect which sectors are leading/lagging."""
        # Get sector ETFs
        sector_symbols = ['XLK', 'XLF', 'XLV', 'XLE', 'XLY', 'XLP', 'XLI', 'XLB', 'XLRE', 'XLU', 'XLC']

        sector_performance = []
        for symbol in sector_symbols:
            data = index_data.get(symbol)
            if data:
                sector_performance.append({
                    'symbol': symbol,
                    'name': self.INDEXES[symbol]['name'],
                    'month_change': data.get('month_change_pct', 0),
                    'week_change': data.get('week_change_pct', 0),
                    'trend': data.get('trend', 'NEUTRAL')
                })

        # Sort by monthly performance
        sector_performance.sort(key=lambda x: x['month_change'], reverse=True)

        # Identify leaders and laggards
        leaders = sector_performance[:3] if sector_performance else []
        laggards = sector_performance[-3:] if len(sector_performance) >= 3 else []

        # Rotation signal
        if leaders and laggards:
            # Check if defensive sectors (XLP, XLU, XLRE) are leading
            defensive_symbols = ['XLP', 'XLU', 'XLRE']
            leaders_symbols = [s['symbol'] for s in leaders]
            defensive_leading = sum(1 for sym in defensive_symbols if sym in leaders_symbols)

            if defensive_leading >= 2:
                rotation_signal = 'DEFENSIVE_ROTATION'  # Risk-off
            else:
                # Check if cyclical sectors (XLY, XLI, XLF) are leading
                cyclical_symbols = ['XLY', 'XLI', 'XLF']
                cyclical_leading = sum(1 for sym in cyclical_symbols if sym in leaders_symbols)

                if cyclical_leading >= 2:
                    rotation_signal = 'CYCLICAL_ROTATION'  # Risk-on
                else:
                    rotation_signal = 'MIXED'
        else:
            rotation_signal = 'UNKNOWN'

        return {
            'leaders': leaders,
            'laggards': laggards,
            'rotation_signal': rotation_signal
        }

    def _determine_market_regime(self, index_data: Dict[str, Any]) -> Dict[str, Any]:
        """Determine overall market regime."""
        sp500 = index_data.get('^GSPC', {})
        vix = index_data.get('^VIX', {})

        # Trend
        trend = sp500.get('trend', 'NEUTRAL')

        # Volatility regime
        vix_level = vix.get('price', 15)
        if vix_level < 15:
            volatility_regime = 'LOW_VOLATILITY'
        elif vix_level < 20:
            volatility_regime = 'NORMAL_VOLATILITY'
        elif vix_level < 30:
            volatility_regime = 'ELEVATED_VOLATILITY'
        else:
            volatility_regime = 'HIGH_VOLATILITY'

        # Overall regime
        if trend == 'UPTREND' and volatility_regime in ['LOW_VOLATILITY', 'NORMAL_VOLATILITY']:
            regime = 'BULL_MARKET'
        elif trend == 'DOWNTREND' and volatility_regime in ['ELEVATED_VOLATILITY', 'HIGH_VOLATILITY']:
            regime = 'BEAR_MARKET'
        elif volatility_regime == 'HIGH_VOLATILITY':
            regime = 'HIGH_VOLATILITY_ENVIRONMENT'
        else:
            regime = 'NEUTRAL_CHOPPY'

        # Trading recommendation
        if regime == 'BULL_MARKET':
            recommendation = 'AGGRESSIVE - Buy dips, trend following'
        elif regime == 'BEAR_MARKET':
            recommendation = 'DEFENSIVE - Reduce exposure, quality stocks only'
        elif regime == 'HIGH_VOLATILITY_ENVIRONMENT':
            recommendation = 'CAUTIOUS - Small positions, wide stops'
        else:
            recommendation = 'SELECTIVE - Range trading, stock picking'

        return {
            'regime': regime,
            'trend': trend,
            'volatility_regime': volatility_regime,
            'vix_level': vix_level,
            'recommendation': recommendation
        }

    def get_index_summary(self, symbol: str) -> Dict[str, Any]:
        """Get detailed summary for a single index."""
        if symbol not in self.INDEXES:
            return {'error': f'Index {symbol} not tracked'}

        data = self._fetch_index_data(symbol)
        if not data:
            return {'error': f'Could not fetch data for {symbol}'}

        data['info'] = self.INDEXES[symbol]
        return data
