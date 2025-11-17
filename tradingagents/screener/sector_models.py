"""
Sector Data Models
Data classes and constants for sector analysis
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import date
from enum import Enum


class Momentum(str, Enum):
    """Sector momentum levels"""
    STRONG = "Strong"
    MODERATE = "Moderate"
    NEUTRAL = "Neutral"
    WEAK = "Weak"


class TrendDirection(str, Enum):
    """Sector trend directions"""
    UP = "Up"
    DOWN = "Down"
    SIDEWAYS = "Sideways"


class SectorTier(str, Enum):
    """Sector performance tiers"""
    TOP = "Top"
    MIDDLE = "Middle"
    BOTTOM = "Bottom"


@dataclass
class SectorScore:
    """Sector strength score data"""
    sector: str
    strength_score: float
    total_stocks: int
    buy_signals: int
    wait_signals: int
    sell_signals: int
    avg_priority: float
    avg_rsi: float
    avg_volume_ratio: float
    momentum: Momentum
    trend_direction: TrendDirection
    analysis_date: date
    rank: Optional[int] = None
    tier: Optional[SectorTier] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'sector': self.sector,
            'strength_score': self.strength_score,
            'total_stocks': self.total_stocks,
            'buy_signals': self.buy_signals,
            'wait_signals': self.wait_signals,
            'sell_signals': self.sell_signals,
            'avg_priority': self.avg_priority,
            'avg_rsi': self.avg_rsi,
            'avg_volume_ratio': self.avg_volume_ratio,
            'momentum': self.momentum.value if isinstance(self.momentum, Momentum) else self.momentum,
            'trend_direction': self.trend_direction.value if isinstance(self.trend_direction, TrendDirection) else self.trend_direction,
            'analysis_date': self.analysis_date.isoformat() if isinstance(self.analysis_date, date) else str(self.analysis_date),
            'rank': self.rank,
            'tier': self.tier.value if isinstance(self.tier, SectorTier) else self.tier
        }


@dataclass
class SectorRotation:
    """Sector rotation event data"""
    rotation_date: date
    from_sector: str
    to_sector: str
    rotation_type: str
    confidence_level: str
    strength_change: float
    notes: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'rotation_date': self.rotation_date.isoformat() if isinstance(self.rotation_date, date) else str(self.rotation_date),
            'from_sector': self.from_sector,
            'to_sector': self.to_sector,
            'rotation_type': self.rotation_type,
            'confidence_level': self.confidence_level,
            'strength_change': self.strength_change,
            'notes': self.notes
        }


# Market sector constants
SECTORS = {
    'Technology': {
        'description': 'Software, hardware, semiconductors, IT services',
        'typical_stocks': ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META', 'AVGO', 'ADBE', 'CRM', 'ORCL', 'AMD'],
        'emoji': '💻',
        'cyclical': True
    },
    'Healthcare': {
        'description': 'Pharmaceuticals, biotechnology, medical devices, healthcare services',
        'typical_stocks': ['UNH', 'JNJ', 'LLY', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR', 'PFE', 'BMY'],
        'emoji': '🏥',
        'cyclical': False
    },
    'Financial Services': {
        'description': 'Banks, insurance, investment services, payment processors',
        'typical_stocks': ['BRK.B', 'JPM', 'V', 'MA', 'BAC', 'WFC', 'GS', 'MS', 'SPGI', 'AXP'],
        'emoji': '🏦',
        'cyclical': True
    },
    'Consumer Cyclical': {
        'description': 'Retail, automotive, luxury goods, entertainment',
        'typical_stocks': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'SBUX', 'LOW', 'TGT', 'TJX', 'BKNG'],
        'emoji': '🛒',
        'cyclical': True
    },
    'Communication': {
        'description': 'Telecom, media, internet services',
        'typical_stocks': ['META', 'GOOGL', 'NFLX', 'DIS', 'CMCSA', 'VZ', 'T', 'TMUS', 'EA', 'CHTR'],
        'emoji': '📡',
        'cyclical': True
    },
    'Industrials': {
        'description': 'Manufacturing, aerospace, construction, transportation',
        'typical_stocks': ['CAT', 'UPS', 'HON', 'BA', 'RTX', 'UNP', 'GE', 'MMM', 'LMT', 'DE'],
        'emoji': '🏭',
        'cyclical': True
    },
    'Consumer Defensive': {
        'description': 'Food, beverages, household products, tobacco',
        'typical_stocks': ['PG', 'KO', 'PEP', 'WMT', 'COST', 'PM', 'MO', 'CL', 'MDLZ', 'KMB'],
        'emoji': '🍔',
        'cyclical': False
    },
    'Energy': {
        'description': 'Oil, gas, renewable energy',
        'typical_stocks': ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'PSX', 'VLO', 'OXY', 'HAL'],
        'emoji': '⚡',
        'cyclical': True
    },
    'Utilities': {
        'description': 'Electric, gas, water utilities',
        'typical_stocks': ['NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC', 'SRE', 'PEG', 'XEL', 'ED'],
        'emoji': '💡',
        'cyclical': False
    },
    'Real Estate': {
        'description': 'REITs, real estate services',
        'typical_stocks': ['AMT', 'PLD', 'CCI', 'EQIX', 'PSA', 'WELL', 'SPG', 'O', 'DLR', 'SBAC'],
        'emoji': '🏠',
        'cyclical': True
    },
    'Basic Materials': {
        'description': 'Mining, chemicals, metals, paper',
        'typical_stocks': ['LIN', 'APD', 'ECL', 'SHW', 'FCX', 'NEM', 'DOW', 'DD', 'NUE', 'VMC'],
        'emoji': '⛏️',
        'cyclical': True
    }
}


def get_sector_emoji(sector: str) -> str:
    """Get emoji for a sector"""
    return SECTORS.get(sector, {}).get('emoji', '📊')


def get_sector_description(sector: str) -> str:
    """Get description for a sector"""
    return SECTORS.get(sector, {}).get('description', 'Unknown sector')


def is_cyclical_sector(sector: str) -> bool:
    """Check if sector is cyclical"""
    return SECTORS.get(sector, {}).get('cyclical', True)


def get_all_sector_names() -> List[str]:
    """Get list of all sector names"""
    return list(SECTORS.keys())


def get_sector_stocks(sector: str) -> List[str]:
    """Get typical stocks for a sector"""
    return SECTORS.get(sector, {}).get('typical_stocks', [])


# Sector performance thresholds
STRENGTH_THRESHOLDS = {
    'excellent': 80,
    'strong': 70,
    'moderate': 60,
    'weak': 50,
    'poor': 0
}


def get_strength_label(strength_score: float) -> str:
    """Get label for strength score"""
    if strength_score >= STRENGTH_THRESHOLDS['excellent']:
        return 'Excellent'
    elif strength_score >= STRENGTH_THRESHOLDS['strong']:
        return 'Strong'
    elif strength_score >= STRENGTH_THRESHOLDS['moderate']:
        return 'Moderate'
    elif strength_score >= STRENGTH_THRESHOLDS['weak']:
        return 'Weak'
    else:
        return 'Poor'


# Sector rotation types
ROTATION_TYPES = {
    'LEADERSHIP': 'Leadership rotation - new sector taking #1 position',
    'MONEY_FLOW': 'Money flow rotation - capital moving between sectors',
    'MOMENTUM': 'Momentum rotation - momentum shift between sectors',
    'DEFENSIVE': 'Defensive rotation - flight to safety sectors',
    'CYCLICAL': 'Cyclical rotation - rotation into cyclical sectors'
}


def get_rotation_description(rotation_type: str) -> str:
    """Get description for rotation type"""
    return ROTATION_TYPES.get(rotation_type, 'Sector rotation')
