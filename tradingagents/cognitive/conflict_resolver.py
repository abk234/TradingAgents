# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Conflict Resolution Engine for Eddie v2.0
Phase 2.4: Advanced Autonomous Learning

Intelligently resolves conflicting information from multiple sources.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum
import logging
from collections import Counter

from .source_verifier import SourceVerifier, VerificationResult, get_source_verifier

logger = logging.getLogger(__name__)


class ConflictType(Enum):
    """Types of conflicts"""
    NUMERIC = "numeric"           # Conflicting numbers (e.g., different prices)
    BOOLEAN = "boolean"           # Conflicting yes/no (e.g., profitable vs unprofitable)
    CATEGORICAL = "categorical"   # Different categories (e.g., BUY vs SELL)
    TEXT = "text"                # Different text descriptions


class ResolutionStrategy(Enum):
    """Strategies for resolving conflicts"""
    SOURCE_WEIGHT = "source_weight"     # Prefer higher credibility sources
    RECENCY = "recency"                 # Prefer more recent information
    CONSENSUS = "consensus"             # Prefer majority agreement
    EXPERT_PRIORITY = "expert_priority" # Prefer domain experts
    COMBINED = "combined"               # Use multiple strategies


@dataclass
class Fact:
    """A fact with source information"""
    content: Any
    source_url: str
    source_verification: Optional[VerificationResult]
    timestamp: Optional[datetime]
    confidence: float = 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "content": str(self.content),
            "source_url": self.source_url,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "confidence": self.confidence,
            "source_credibility": self.source_verification.credibility_score if self.source_verification else 0.0
        }


@dataclass
class Conflict:
    """A conflict between multiple facts"""
    topic: str
    conflict_type: ConflictType
    facts: List[Fact]
    detected_at: datetime
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "topic": self.topic,
            "conflict_type": self.conflict_type.value,
            "facts": [f.to_dict() for f in self.facts],
            "detected_at": self.detected_at.isoformat()
        }


@dataclass
class ResolvedFact:
    """A resolved fact with reasoning"""
    content: Any
    confidence: float
    resolution_strategy: ResolutionStrategy
    supporting_sources: List[str]
    conflicting_sources: List[str]
    reasoning: str
    resolved_at: datetime
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "content": str(self.content),
            "confidence": self.confidence,
            "resolution_strategy": self.resolution_strategy.value,
            "supporting_sources": self.supporting_sources,
            "conflicting_sources": self.conflicting_sources,
            "reasoning": self.reasoning,
            "resolved_at": self.resolved_at.isoformat()
        }


class ConflictResolver:
    """
    Intelligently resolves conflicting information from multiple sources.
    
    Features:
    - Detects conflicts between facts
    - Multiple resolution strategies
    - Source-weighted resolution
    - Temporal resolution (prefer recent)
    - Consensus-based resolution
    """
    
    def __init__(self, source_verifier: Optional[SourceVerifier] = None):
        """
        Initialize conflict resolver.
        
        Args:
            source_verifier: Optional SourceVerifier instance
        """
        self.source_verifier = source_verifier or get_source_verifier()
        self.resolution_history: List[ResolvedFact] = []
        logger.info("ConflictResolver initialized")
    
    def detect_conflicts(
        self,
        facts: List[Fact],
        topic: str,
        conflict_threshold: float = 0.1
    ) -> List[Conflict]:
        """
        Detect conflicts between facts.
        
        Args:
            facts: List of facts to check
            topic: Topic of the facts
            conflict_threshold: Threshold for detecting conflicts (for numeric values)
        
        Returns:
            List of detected conflicts
        """
        if len(facts) < 2:
            return []
        
        logger.info(f"Detecting conflicts for {topic} with {len(facts)} facts")
        
        # Determine conflict type
        conflict_type = self._determine_conflict_type(facts)
        
        # Check for conflicts based on type
        has_conflict = False
        
        if conflict_type == ConflictType.NUMERIC:
            has_conflict = self._has_numeric_conflict(facts, conflict_threshold)
        elif conflict_type == ConflictType.BOOLEAN:
            has_conflict = self._has_boolean_conflict(facts)
        elif conflict_type == ConflictType.CATEGORICAL:
            has_conflict = self._has_categorical_conflict(facts)
        elif conflict_type == ConflictType.TEXT:
            has_conflict = self._has_text_conflict(facts)
        
        if has_conflict:
            conflict = Conflict(
                topic=topic,
                conflict_type=conflict_type,
                facts=facts,
                detected_at=datetime.now()
            )
            logger.warning(f"Conflict detected for {topic}: {conflict_type.value}")
            return [conflict]
        
        return []
    
    def resolve_conflict(
        self,
        conflict: Conflict,
        strategy: ResolutionStrategy = ResolutionStrategy.COMBINED
    ) -> ResolvedFact:
        """
        Resolve a conflict using specified strategy.
        
        Args:
            conflict: Conflict to resolve
            strategy: Resolution strategy to use
        
        Returns:
            ResolvedFact with resolution
        """
        logger.info(f"Resolving conflict for {conflict.topic} using {strategy.value}")
        
        if strategy == ResolutionStrategy.SOURCE_WEIGHT:
            return self.resolve_by_source_weight(conflict)
        elif strategy == ResolutionStrategy.RECENCY:
            return self.resolve_by_recency(conflict)
        elif strategy == ResolutionStrategy.CONSENSUS:
            return self.resolve_by_consensus(conflict)
        elif strategy == ResolutionStrategy.EXPERT_PRIORITY:
            return self.resolve_by_expert_priority(conflict)
        else:  # COMBINED
            return self.resolve_by_combined(conflict)
    
    def resolve_by_source_weight(self, conflict: Conflict) -> ResolvedFact:
        """
        Resolve conflict by preferring higher credibility sources.
        
        Args:
            conflict: Conflict to resolve
        
        Returns:
            ResolvedFact
        """
        # Sort facts by source credibility
        sorted_facts = sorted(
            conflict.facts,
            key=lambda f: f.source_verification.credibility_score if f.source_verification else 0.0,
            reverse=True
        )
        
        best_fact = sorted_facts[0]
        best_credibility = best_fact.source_verification.credibility_score if best_fact.source_verification else 0.0
        
        # Find supporting sources (similar content with high credibility)
        supporting = [best_fact.source_url]
        conflicting = []
        
        for fact in sorted_facts[1:]:
            if self._facts_agree(best_fact, fact, conflict.conflict_type):
                supporting.append(fact.source_url)
            else:
                conflicting.append(fact.source_url)
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            credibility=best_credibility,
            support_count=len(supporting),
            total_count=len(conflict.facts)
        )
        
        reasoning = (
            f"Resolved by source credibility. "
            f"Best source has credibility score of {best_credibility:.2f}. "
            f"{len(supporting)} supporting, {len(conflicting)} conflicting sources."
        )
        
        resolved = ResolvedFact(
            content=best_fact.content,
            confidence=confidence,
            resolution_strategy=ResolutionStrategy.SOURCE_WEIGHT,
            supporting_sources=supporting,
            conflicting_sources=conflicting,
            reasoning=reasoning,
            resolved_at=datetime.now()
        )
        
        self.resolution_history.append(resolved)
        logger.info(f"Resolved by source weight: confidence={confidence:.2f}")
        
        return resolved
    
    def resolve_by_recency(self, conflict: Conflict) -> ResolvedFact:
        """
        Resolve conflict by preferring more recent information.
        
        Args:
            conflict: Conflict to resolve
        
        Returns:
            ResolvedFact
        """
        # Filter facts with timestamps
        facts_with_time = [f for f in conflict.facts if f.timestamp is not None]
        
        if not facts_with_time:
            # Fallback to source weight if no timestamps
            logger.warning("No timestamps available, falling back to source weight")
            return self.resolve_by_source_weight(conflict)
        
        # Sort by recency
        sorted_facts = sorted(
            facts_with_time,
            key=lambda f: f.timestamp,
            reverse=True
        )
        
        most_recent = sorted_facts[0]
        
        # Find supporting sources
        supporting = [most_recent.source_url]
        conflicting = []
        
        for fact in sorted_facts[1:]:
            if self._facts_agree(most_recent, fact, conflict.conflict_type):
                supporting.append(fact.source_url)
            else:
                conflicting.append(fact.source_url)
        
        # Calculate confidence based on recency and credibility
        credibility = most_recent.source_verification.credibility_score if most_recent.source_verification else 0.5
        age_hours = (datetime.now() - most_recent.timestamp).total_seconds() / 3600
        recency_factor = max(0.5, 1.0 - (age_hours / 168))  # Decay over a week
        
        confidence = self._calculate_confidence(
            credibility=credibility * recency_factor,
            support_count=len(supporting),
            total_count=len(conflict.facts)
        )
        
        reasoning = (
            f"Resolved by recency. Most recent source from {age_hours:.1f} hours ago. "
            f"{len(supporting)} supporting, {len(conflicting)} conflicting sources."
        )
        
        resolved = ResolvedFact(
            content=most_recent.content,
            confidence=confidence,
            resolution_strategy=ResolutionStrategy.RECENCY,
            supporting_sources=supporting,
            conflicting_sources=conflicting,
            reasoning=reasoning,
            resolved_at=datetime.now()
        )
        
        self.resolution_history.append(resolved)
        logger.info(f"Resolved by recency: confidence={confidence:.2f}")
        
        return resolved
    
    def resolve_by_consensus(self, conflict: Conflict) -> ResolvedFact:
        """
        Resolve conflict by majority agreement.
        
        Args:
            conflict: Conflict to resolve
        
        Returns:
            ResolvedFact
        """
        # Group facts by content
        content_groups = {}
        for fact in conflict.facts:
            content_str = str(fact.content)
            if content_str not in content_groups:
                content_groups[content_str] = []
            content_groups[content_str].append(fact)
        
        # Find majority
        majority_content = max(content_groups.keys(), key=lambda k: len(content_groups[k]))
        majority_facts = content_groups[majority_content]
        
        # Calculate average credibility of majority
        avg_credibility = sum(
            f.source_verification.credibility_score if f.source_verification else 0.0
            for f in majority_facts
        ) / len(majority_facts)
        
        # Find supporting and conflicting sources
        supporting = [f.source_url for f in majority_facts]
        conflicting = [f.source_url for f in conflict.facts if f not in majority_facts]
        
        # Calculate confidence
        consensus_ratio = len(majority_facts) / len(conflict.facts)
        confidence = self._calculate_confidence(
            credibility=avg_credibility,
            support_count=len(supporting),
            total_count=len(conflict.facts)
        )
        
        reasoning = (
            f"Resolved by consensus. {len(majority_facts)}/{len(conflict.facts)} sources agree "
            f"({consensus_ratio*100:.0f}% consensus). Average credibility: {avg_credibility:.2f}."
        )
        
        resolved = ResolvedFact(
            content=majority_facts[0].content,
            confidence=confidence,
            resolution_strategy=ResolutionStrategy.CONSENSUS,
            supporting_sources=supporting,
            conflicting_sources=conflicting,
            reasoning=reasoning,
            resolved_at=datetime.now()
        )
        
        self.resolution_history.append(resolved)
        logger.info(f"Resolved by consensus: confidence={confidence:.2f}")
        
        return resolved
    
    def resolve_by_expert_priority(self, conflict: Conflict) -> ResolvedFact:
        """
        Resolve conflict by prioritizing domain experts.
        
        For financial topics, prioritize financial news sources.
        
        Args:
            conflict: Conflict to resolve
        
        Returns:
            ResolvedFact
        """
        # This is essentially source weight with domain-specific adjustments
        # For now, use source weight as experts are already in Tier 1
        return self.resolve_by_source_weight(conflict)
    
    def resolve_by_combined(self, conflict: Conflict) -> ResolvedFact:
        """
        Resolve conflict using multiple strategies combined.
        
        Args:
            conflict: Conflict to resolve
        
        Returns:
            ResolvedFact
        """
        # Try multiple strategies and combine
        source_weight_result = self.resolve_by_source_weight(conflict)
        consensus_result = self.resolve_by_consensus(conflict)
        
        # If both agree, high confidence
        if source_weight_result.content == consensus_result.content:
            combined_confidence = min(0.95, (source_weight_result.confidence + consensus_result.confidence) / 2 * 1.2)
            
            reasoning = (
                f"Resolved by combined strategy. "
                f"Both source credibility and consensus agree. "
                f"Source weight confidence: {source_weight_result.confidence:.2f}, "
                f"Consensus confidence: {consensus_result.confidence:.2f}."
            )
            
            resolved = ResolvedFact(
                content=source_weight_result.content,
                confidence=combined_confidence,
                resolution_strategy=ResolutionStrategy.COMBINED,
                supporting_sources=list(set(source_weight_result.supporting_sources + consensus_result.supporting_sources)),
                conflicting_sources=list(set(source_weight_result.conflicting_sources + consensus_result.conflicting_sources)),
                reasoning=reasoning,
                resolved_at=datetime.now()
            )
        else:
            # Disagree - prefer source weight but lower confidence
            combined_confidence = source_weight_result.confidence * 0.8
            
            reasoning = (
                f"Resolved by combined strategy with disagreement. "
                f"Preferring high-credibility source over consensus. "
                f"Confidence reduced due to disagreement."
            )
            
            resolved = ResolvedFact(
                content=source_weight_result.content,
                confidence=combined_confidence,
                resolution_strategy=ResolutionStrategy.COMBINED,
                supporting_sources=source_weight_result.supporting_sources,
                conflicting_sources=source_weight_result.conflicting_sources,
                reasoning=reasoning,
                resolved_at=datetime.now()
            )
        
        self.resolution_history.append(resolved)
        logger.info(f"Resolved by combined strategy: confidence={resolved.confidence:.2f}")
        
        return resolved
    
    def get_confidence_score(self, resolution: ResolvedFact) -> float:
        """
        Get confidence score for a resolution.
        
        Args:
            resolution: ResolvedFact
        
        Returns:
            Confidence score (0-1)
        """
        return resolution.confidence
    
    # Private methods
    
    def _determine_conflict_type(self, facts: List[Fact]) -> ConflictType:
        """Determine the type of conflict"""
        # Check if all facts are numeric
        try:
            [float(f.content) for f in facts]
            return ConflictType.NUMERIC
        except (ValueError, TypeError):
            pass
        
        # Check if boolean
        bool_values = {'true', 'false', 'yes', 'no', '1', '0'}
        if all(str(f.content).lower() in bool_values for f in facts):
            return ConflictType.BOOLEAN
        
        # Check if categorical (limited set of values)
        unique_values = set(str(f.content).lower() for f in facts)
        if len(unique_values) <= 5:  # Arbitrary threshold
            return ConflictType.CATEGORICAL
        
        return ConflictType.TEXT
    
    def _has_numeric_conflict(self, facts: List[Fact], threshold: float) -> bool:
        """Check if numeric facts conflict"""
        try:
            values = [float(f.content) for f in facts]
            if not values:
                return False
            
            min_val = min(values)
            max_val = max(values)
            
            # Check if difference exceeds threshold (percentage)
            if min_val == 0:
                return max_val > threshold
            
            diff_percent = abs(max_val - min_val) / min_val
            return diff_percent > threshold
        except (ValueError, TypeError):
            return False
    
    def _has_boolean_conflict(self, facts: List[Fact]) -> bool:
        """Check if boolean facts conflict"""
        values = set(str(f.content).lower() for f in facts)
        
        # Map to boolean
        true_values = {'true', 'yes', '1'}
        false_values = {'false', 'no', '0'}
        
        has_true = any(v in true_values for v in values)
        has_false = any(v in false_values for v in values)
        
        return has_true and has_false
    
    def _has_categorical_conflict(self, facts: List[Fact]) -> bool:
        """Check if categorical facts conflict"""
        values = set(str(f.content).lower() for f in facts)
        return len(values) > 1
    
    def _has_text_conflict(self, facts: List[Fact]) -> bool:
        """Check if text facts conflict"""
        # Simple check: if texts are different, there's a conflict
        texts = [str(f.content).lower().strip() for f in facts]
        return len(set(texts)) > 1
    
    def _facts_agree(self, fact1: Fact, fact2: Fact, conflict_type: ConflictType) -> bool:
        """Check if two facts agree"""
        if conflict_type == ConflictType.NUMERIC:
            try:
                v1 = float(fact1.content)
                v2 = float(fact2.content)
                # Within 5% is considered agreement
                diff_percent = abs(v1 - v2) / max(v1, v2) if max(v1, v2) > 0 else 0
                return diff_percent < 0.05
            except (ValueError, TypeError):
                return False
        else:
            # For other types, simple equality
            return str(fact1.content).lower().strip() == str(fact2.content).lower().strip()
    
    def _calculate_confidence(
        self,
        credibility: float,
        support_count: int,
        total_count: int
    ) -> float:
        """Calculate confidence score"""
        # Base confidence from source credibility
        base_confidence = credibility
        
        # Adjust for support ratio
        support_ratio = support_count / total_count if total_count > 0 else 0
        support_factor = 0.5 + (support_ratio * 0.5)  # 0.5 to 1.0
        
        # Combined confidence
        confidence = base_confidence * support_factor
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, confidence))


# Global instance
_resolver = None


def get_conflict_resolver() -> ConflictResolver:
    """Get global ConflictResolver instance"""
    global _resolver
    if _resolver is None:
        _resolver = ConflictResolver()
    return _resolver

