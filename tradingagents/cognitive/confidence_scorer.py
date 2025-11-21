"""
Learning Confidence Scoring System for Eddie v2.0
Phase 2.4: Advanced Autonomous Learning

Tracks and calculates confidence scores for learned information over time.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum
import logging
import math

logger = logging.getLogger(__name__)


class FactType(Enum):
    """Types of facts with different decay rates"""
    FACTUAL = "factual"           # Hard facts (earnings, revenue) - 10% decay/week
    SENTIMENT = "sentiment"       # Sentiment data - 30% decay/week
    PATTERN = "pattern"           # Technical patterns - 5% decay/week
    PREDICTION = "prediction"     # Future predictions - 40% decay/week
    NEWS = "news"                 # News-based facts - 20% decay/week


# Decay rates per week for each fact type
DECAY_RATES = {
    FactType.FACTUAL: 0.10,
    FactType.SENTIMENT: 0.30,
    FactType.PATTERN: 0.05,
    FactType.PREDICTION: 0.40,
    FactType.NEWS: 0.20
}


@dataclass
class ConfidenceFactor:
    """Individual factor contributing to confidence score"""
    name: str
    value: float  # 0-1
    weight: float  # Weight in final calculation
    description: str


@dataclass
class ConfidenceScore:
    """Complete confidence score breakdown"""
    fact_id: str
    total_confidence: float  # 0-1
    factors: List[ConfidenceFactor]
    fact_type: FactType
    age_days: int
    time_decay_applied: float
    calculated_at: datetime
    notes: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "fact_id": self.fact_id,
            "total_confidence": self.total_confidence,
            "confidence_level": self._get_confidence_level(),
            "factors": [
                {
                    "name": f.name,
                    "value": f.value,
                    "weight": f.weight,
                    "description": f.description,
                    "contribution": f.value * f.weight
                }
                for f in self.factors
            ],
            "fact_type": self.fact_type.value,
            "age_days": self.age_days,
            "time_decay_applied": self.time_decay_applied,
            "calculated_at": self.calculated_at.isoformat(),
            "notes": self.notes
        }
    
    def _get_confidence_level(self) -> str:
        """Get human-readable confidence level"""
        if self.total_confidence >= 0.8:
            return "Very High"
        elif self.total_confidence >= 0.6:
            return "High"
        elif self.total_confidence >= 0.4:
            return "Moderate"
        elif self.total_confidence >= 0.2:
            return "Low"
        else:
            return "Very Low"


@dataclass
class ConfidenceReport:
    """Confidence report for a ticker or topic"""
    subject: str  # Ticker or topic
    total_facts: int
    avg_confidence: float
    high_confidence_facts: int
    low_confidence_facts: int
    facts_by_type: Dict[str, int]
    oldest_fact_age_days: int
    newest_fact_age_days: int
    confidence_scores: List[ConfidenceScore]
    generated_at: datetime
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "subject": self.subject,
            "total_facts": self.total_facts,
            "avg_confidence": self.avg_confidence,
            "confidence_level": self._get_avg_confidence_level(),
            "high_confidence_facts": self.high_confidence_facts,
            "low_confidence_facts": self.low_confidence_facts,
            "facts_by_type": self.facts_by_type,
            "oldest_fact_age_days": self.oldest_fact_age_days,
            "newest_fact_age_days": self.newest_fact_age_days,
            "generated_at": self.generated_at.isoformat()
        }
    
    def _get_avg_confidence_level(self) -> str:
        """Get human-readable confidence level"""
        if self.avg_confidence >= 0.8:
            return "Very High"
        elif self.avg_confidence >= 0.6:
            return "High"
        elif self.avg_confidence >= 0.4:
            return "Moderate"
        elif self.avg_confidence >= 0.2:
            return "Low"
        else:
            return "Very Low"


class ConfidenceScorer:
    """
    Calculates and tracks confidence scores for learned information.
    
    Confidence Factors (weights):
    - Source Credibility (30%): Quality of information source
    - Cross-Validation (25%): Agreement across multiple sources
    - Recency (20%): How recent the information is
    - Historical Accuracy (15%): Past accuracy of similar learnings
    - Context Relevance (10%): Relevance to current market conditions
    """
    
    # Factor weights (must sum to 1.0)
    WEIGHTS = {
        "source_credibility": 0.30,
        "cross_validation": 0.25,
        "recency": 0.20,
        "historical_accuracy": 0.15,
        "context_relevance": 0.10
    }
    
    def __init__(self):
        """Initialize confidence scorer"""
        self.accuracy_history: Dict[str, List[float]] = {}  # fact_type -> [accuracies]
        logger.info("ConfidenceScorer initialized")
    
    def calculate_confidence(
        self,
        fact_id: str,
        fact_type: FactType,
        source_credibility: float,
        cross_validation_score: float,
        age_days: int,
        historical_accuracy: Optional[float] = None,
        context_relevance: Optional[float] = None
    ) -> ConfidenceScore:
        """
        Calculate comprehensive confidence score for a fact.
        
        Args:
            fact_id: Unique fact identifier
            fact_type: Type of fact
            source_credibility: Source credibility score (0-1)
            cross_validation_score: Cross-validation score (0-1)
            age_days: Age of fact in days
            historical_accuracy: Optional historical accuracy (0-1)
            context_relevance: Optional context relevance (0-1)
        
        Returns:
            ConfidenceScore with breakdown
        """
        logger.debug(f"Calculating confidence for fact: {fact_id}")
        
        factors = []
        
        # Factor 1: Source Credibility (30%)
        factors.append(ConfidenceFactor(
            name="source_credibility",
            value=source_credibility,
            weight=self.WEIGHTS["source_credibility"],
            description=f"Quality of information source: {self._format_score(source_credibility)}"
        ))
        
        # Factor 2: Cross-Validation (25%)
        factors.append(ConfidenceFactor(
            name="cross_validation",
            value=cross_validation_score,
            weight=self.WEIGHTS["cross_validation"],
            description=f"Agreement across sources: {self._format_score(cross_validation_score)}"
        ))
        
        # Factor 3: Recency (20%)
        recency_score = self._calculate_recency_score(age_days)
        factors.append(ConfidenceFactor(
            name="recency",
            value=recency_score,
            weight=self.WEIGHTS["recency"],
            description=f"Information freshness: {self._format_score(recency_score)} ({age_days} days old)"
        ))
        
        # Factor 4: Historical Accuracy (15%)
        if historical_accuracy is None:
            historical_accuracy = self._get_default_accuracy(fact_type)
        factors.append(ConfidenceFactor(
            name="historical_accuracy",
            value=historical_accuracy,
            weight=self.WEIGHTS["historical_accuracy"],
            description=f"Past accuracy: {self._format_score(historical_accuracy)}"
        ))
        
        # Factor 5: Context Relevance (10%)
        if context_relevance is None:
            context_relevance = 0.7  # Default moderate relevance
        factors.append(ConfidenceFactor(
            name="context_relevance",
            value=context_relevance,
            weight=self.WEIGHTS["context_relevance"],
            description=f"Market relevance: {self._format_score(context_relevance)}"
        ))
        
        # Calculate weighted confidence
        base_confidence = sum(f.value * f.weight for f in factors)
        
        # Apply time decay
        time_decay = self.apply_time_decay(base_confidence, age_days, fact_type)
        final_confidence = base_confidence * time_decay
        
        # Clamp to [0, 1]
        final_confidence = max(0.0, min(1.0, final_confidence))
        
        # Generate notes
        notes = self._generate_notes(final_confidence, age_days, fact_type, time_decay)
        
        score = ConfidenceScore(
            fact_id=fact_id,
            total_confidence=final_confidence,
            factors=factors,
            fact_type=fact_type,
            age_days=age_days,
            time_decay_applied=time_decay,
            calculated_at=datetime.now(),
            notes=notes
        )
        
        logger.info(f"Confidence calculated: {fact_id} = {final_confidence:.2f}")
        
        return score
    
    def apply_time_decay(
        self,
        confidence: float,
        age_days: int,
        fact_type: FactType
    ) -> float:
        """
        Apply time-based decay to confidence score.
        
        Args:
            confidence: Current confidence (0-1)
            age_days: Age in days
            fact_type: Type of fact
        
        Returns:
            Decay multiplier (0-1)
        """
        if age_days <= 0:
            return 1.0
        
        decay_rate = DECAY_RATES.get(fact_type, 0.15)  # Default 15% per week
        weeks = age_days / 7.0
        
        # Exponential decay: decay_multiplier = (1 - decay_rate) ^ weeks
        decay_multiplier = math.pow(1.0 - decay_rate, weeks)
        
        # Ensure minimum decay (don't go below 10% of original)
        decay_multiplier = max(0.10, decay_multiplier)
        
        return decay_multiplier
    
    def update_based_on_accuracy(
        self,
        fact_id: str,
        fact_type: FactType,
        actual_outcome: bool
    ) -> float:
        """
        Update confidence based on actual outcome.
        
        Args:
            fact_id: Fact identifier
            fact_type: Type of fact
            actual_outcome: True if fact was accurate
        
        Returns:
            Updated accuracy score
        """
        accuracy_value = 1.0 if actual_outcome else 0.0
        
        # Store in history
        type_key = fact_type.value
        if type_key not in self.accuracy_history:
            self.accuracy_history[type_key] = []
        
        self.accuracy_history[type_key].append(accuracy_value)
        
        # Calculate running average (last 100 facts)
        recent_accuracies = self.accuracy_history[type_key][-100:]
        avg_accuracy = sum(recent_accuracies) / len(recent_accuracies)
        
        logger.info(
            f"Accuracy updated for {fact_type.value}: "
            f"{'✓' if actual_outcome else '✗'} "
            f"(avg: {avg_accuracy:.2f})"
        )
        
        return avg_accuracy
    
    def get_confidence_report(
        self,
        subject: str,
        fact_scores: List[ConfidenceScore]
    ) -> ConfidenceReport:
        """
        Generate confidence report for a subject.
        
        Args:
            subject: Subject (ticker or topic)
            fact_scores: List of confidence scores
        
        Returns:
            ConfidenceReport
        """
        if not fact_scores:
            return ConfidenceReport(
                subject=subject,
                total_facts=0,
                avg_confidence=0.0,
                high_confidence_facts=0,
                low_confidence_facts=0,
                facts_by_type={},
                oldest_fact_age_days=0,
                newest_fact_age_days=0,
                confidence_scores=[],
                generated_at=datetime.now()
            )
        
        # Calculate statistics
        total_facts = len(fact_scores)
        avg_confidence = sum(s.total_confidence for s in fact_scores) / total_facts
        high_confidence_facts = sum(1 for s in fact_scores if s.total_confidence >= 0.7)
        low_confidence_facts = sum(1 for s in fact_scores if s.total_confidence < 0.4)
        
        # Count by type
        facts_by_type = {}
        for score in fact_scores:
            type_name = score.fact_type.value
            facts_by_type[type_name] = facts_by_type.get(type_name, 0) + 1
        
        # Age statistics
        oldest_age = max(s.age_days for s in fact_scores)
        newest_age = min(s.age_days for s in fact_scores)
        
        report = ConfidenceReport(
            subject=subject,
            total_facts=total_facts,
            avg_confidence=avg_confidence,
            high_confidence_facts=high_confidence_facts,
            low_confidence_facts=low_confidence_facts,
            facts_by_type=facts_by_type,
            oldest_fact_age_days=oldest_age,
            newest_fact_age_days=newest_age,
            confidence_scores=fact_scores,
            generated_at=datetime.now()
        )
        
        logger.info(f"Confidence report generated for {subject}: avg={avg_confidence:.2f}")
        
        return report
    
    def get_historical_accuracy(self, fact_type: FactType) -> float:
        """
        Get historical accuracy for a fact type.
        
        Args:
            fact_type: Type of fact
        
        Returns:
            Average historical accuracy (0-1)
        """
        type_key = fact_type.value
        if type_key not in self.accuracy_history or not self.accuracy_history[type_key]:
            return self._get_default_accuracy(fact_type)
        
        recent_accuracies = self.accuracy_history[type_key][-100:]
        return sum(recent_accuracies) / len(recent_accuracies)
    
    # Private methods
    
    def _calculate_recency_score(self, age_days: int) -> float:
        """Calculate recency score based on age"""
        if age_days <= 0:
            return 1.0
        elif age_days <= 1:
            return 0.95
        elif age_days <= 7:
            return 0.85
        elif age_days <= 30:
            return 0.70
        elif age_days <= 90:
            return 0.50
        elif age_days <= 180:
            return 0.30
        else:
            return 0.10
    
    def _get_default_accuracy(self, fact_type: FactType) -> float:
        """Get default accuracy for a fact type"""
        defaults = {
            FactType.FACTUAL: 0.85,
            FactType.SENTIMENT: 0.65,
            FactType.PATTERN: 0.70,
            FactType.PREDICTION: 0.50,
            FactType.NEWS: 0.75
        }
        return defaults.get(fact_type, 0.70)
    
    def _format_score(self, score: float) -> str:
        """Format score as percentage"""
        return f"{score*100:.0f}%"
    
    def _generate_notes(
        self,
        confidence: float,
        age_days: int,
        fact_type: FactType,
        time_decay: float
    ) -> List[str]:
        """Generate notes about confidence score"""
        notes = []
        
        # Overall confidence
        if confidence >= 0.8:
            notes.append("✅ Very high confidence - reliable information")
        elif confidence >= 0.6:
            notes.append("✅ High confidence - generally reliable")
        elif confidence >= 0.4:
            notes.append("⚠️ Moderate confidence - use with caution")
        else:
            notes.append("❌ Low confidence - verify before using")
        
        # Age warnings
        if age_days > 180:
            notes.append("⚠️ Information is quite old (>6 months)")
        elif age_days > 90:
            notes.append("ℹ️ Information is somewhat dated (>3 months)")
        elif age_days > 30:
            notes.append("ℹ️ Information is over a month old")
        
        # Time decay impact
        if time_decay < 0.5:
            notes.append(f"⚠️ Significant time decay applied ({time_decay*100:.0f}% of original confidence)")
        elif time_decay < 0.8:
            notes.append(f"ℹ️ Moderate time decay applied ({time_decay*100:.0f}% of original confidence)")
        
        # Fact type specific notes
        if fact_type == FactType.PREDICTION:
            notes.append("ℹ️ Prediction-type fact - inherently uncertain")
        elif fact_type == FactType.SENTIMENT:
            notes.append("ℹ️ Sentiment data - can change rapidly")
        
        return notes


# Global instance
_scorer = None


def get_confidence_scorer() -> ConfidenceScorer:
    """Get global ConfidenceScorer instance"""
    global _scorer
    if _scorer is None:
        _scorer = ConfidenceScorer()
    return _scorer

