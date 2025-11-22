# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Knowledge Graph Integrator for Eddie v2.0
Phase 2.4: Advanced Autonomous Learning

Deep integration between autonomous learning and knowledge graph.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import logging

from .knowledge_graph import KnowledgeGraph, get_knowledge_graph
from .source_verifier import SourceVerifier, VerificationResult, get_source_verifier
from .conflict_resolver import ConflictResolver, Fact, get_conflict_resolver
from .confidence_scorer import ConfidenceScorer, FactType, ConfidenceScore, get_confidence_scorer

logger = logging.getLogger(__name__)


@dataclass
class VerifiedFact:
    """A verified fact ready for knowledge graph"""
    content: str
    subject: str  # Ticker or topic
    fact_type: FactType
    source_url: str
    source_verification: VerificationResult
    confidence_score: ConfidenceScore
    learned_at: datetime
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "content": self.content,
            "subject": self.subject,
            "fact_type": self.fact_type.value,
            "source_url": self.source_url,
            "source_credibility": self.source_verification.credibility_score,
            "confidence": self.confidence_score.total_confidence,
            "learned_at": self.learned_at.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class LearningSummary:
    """Summary of learning for a subject"""
    subject: str
    total_facts: int
    avg_confidence: float
    last_updated: datetime
    fact_types: Dict[str, int]
    high_confidence_facts: int
    sources_used: List[str]
    key_insights: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "subject": self.subject,
            "total_facts": self.total_facts,
            "avg_confidence": self.avg_confidence,
            "confidence_level": self._get_confidence_level(),
            "last_updated": self.last_updated.isoformat(),
            "fact_types": self.fact_types,
            "high_confidence_facts": self.high_confidence_facts,
            "sources_used": self.sources_used,
            "key_insights": self.key_insights
        }
    
    def _get_confidence_level(self) -> str:
        """Get human-readable confidence level"""
        if self.avg_confidence >= 0.8:
            return "Very High"
        elif self.avg_confidence >= 0.6:
            return "High"
        elif self.avg_confidence >= 0.4:
            return "Moderate"
        else:
            return "Low"


class KnowledgeIntegrator:
    """
    Integrates autonomous learning with knowledge graph.
    
    Features:
    - Automatic node creation from verified facts
    - Relationship inference
    - Confidence propagation
    - Query optimization
    """
    
    def __init__(
        self,
        knowledge_graph: Optional[KnowledgeGraph] = None,
        source_verifier: Optional[SourceVerifier] = None,
        conflict_resolver: Optional[ConflictResolver] = None,
        confidence_scorer: Optional[ConfidenceScorer] = None
    ):
        """
        Initialize knowledge integrator.
        
        Args:
            knowledge_graph: Optional KnowledgeGraph instance
            source_verifier: Optional SourceVerifier instance
            conflict_resolver: Optional ConflictResolver instance
            confidence_scorer: Optional ConfidenceScorer instance
        """
        self.kg = knowledge_graph or get_knowledge_graph()
        self.verifier = source_verifier or get_source_verifier()
        self.resolver = conflict_resolver or get_conflict_resolver()
        self.scorer = confidence_scorer or get_confidence_scorer()
        
        # Storage for verified facts
        self.verified_facts: Dict[str, List[VerifiedFact]] = {}  # subject -> facts
        
        logger.info("KnowledgeIntegrator initialized")
    
    async def add_verified_fact(
        self,
        subject: str,
        content: str,
        fact_type: FactType,
        sources: List[Tuple[str, str]],  # List of (url, content) tuples
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[VerifiedFact]:
        """
        Add a verified fact to knowledge graph.
        
        Args:
            subject: Subject (ticker or topic)
            content: Fact content
            fact_type: Type of fact
            sources: List of (url, content) tuples
            metadata: Optional metadata
        
        Returns:
            VerifiedFact if added, None if verification failed
        """
        logger.info(f"Adding verified fact for {subject}: {content[:50]}...")
        
        if not sources:
            logger.warning("No sources provided for fact")
            return None
        
        # Verify sources
        verifications = []
        for url, source_content in sources:
            verification = self.verifier.verify_source(url, source_content)
            verifications.append(verification)
        
        # Calculate cross-validation score
        avg_credibility = sum(v.credibility_score for v in verifications) / len(verifications)
        cross_val_score = min(1.0, len(sources) / 3.0)  # Normalize by expected source count
        
        # Check for conflicts if multiple sources
        if len(sources) > 1:
            facts_to_check = [
                Fact(
                    content=content,
                    source_url=url,
                    source_verification=verification,
                    timestamp=datetime.now(),
                    confidence=0.0
                )
                for (url, _), verification in zip(sources, verifications)
            ]
            
            conflicts = self.resolver.detect_conflicts(facts_to_check, subject)
            
            if conflicts:
                # Resolve conflict
                logger.info(f"Conflict detected for {subject}, resolving...")
                resolution = self.resolver.resolve_conflict(conflicts[0])
                content = str(resolution.content)
                avg_credibility = resolution.confidence
        
        # Calculate confidence score
        age_days = 0  # New fact
        confidence_score = self.scorer.calculate_confidence(
            fact_id=f"{subject}_{hash(content)}",
            fact_type=fact_type,
            source_credibility=avg_credibility,
            cross_validation_score=cross_val_score,
            age_days=age_days
        )
        
        # Only add if confidence is above threshold
        if confidence_score.total_confidence < 0.4:
            logger.warning(f"Confidence too low ({confidence_score.total_confidence:.2f}), not adding fact")
            return None
        
        # Create verified fact
        verified_fact = VerifiedFact(
            content=content,
            subject=subject,
            fact_type=fact_type,
            source_url=sources[0][0],  # Primary source
            source_verification=verifications[0],
            confidence_score=confidence_score,
            learned_at=datetime.now(),
            metadata=metadata or {}
        )
        
        # Store in memory
        if subject not in self.verified_facts:
            self.verified_facts[subject] = []
        self.verified_facts[subject].append(verified_fact)
        
        # Add to knowledge graph
        self.kg.add_memory(
            content=content,
            memory_type="learned_fact",
            metadata={
                "subject": subject,
                "fact_type": fact_type.value,
                "confidence": confidence_score.total_confidence,
                "source": sources[0][0],
                "learned_at": datetime.now().isoformat(),
                **(metadata or {})
            }
        )
        
        logger.info(f"✓ Fact added with confidence {confidence_score.total_confidence:.2f}")
        
        return verified_fact
    
    def infer_relationships(self, subject: str) -> List[Dict[str, Any]]:
        """
        Infer relationships between facts for a subject.
        
        Args:
            subject: Subject to analyze
        
        Returns:
            List of inferred relationships
        """
        if subject not in self.verified_facts:
            return []
        
        facts = self.verified_facts[subject]
        relationships = []
        
        # Infer temporal relationships
        for i, fact1 in enumerate(facts):
            for fact2 in facts[i+1:]:
                # Check if facts are related (simple heuristic)
                if self._facts_related(fact1, fact2):
                    relationships.append({
                        "type": "related_to",
                        "fact1": fact1.content[:50],
                        "fact2": fact2.content[:50],
                        "reason": "temporal_proximity",
                        "confidence": min(fact1.confidence_score.total_confidence,
                                        fact2.confidence_score.total_confidence)
                    })
        
        logger.info(f"Inferred {len(relationships)} relationships for {subject}")
        
        return relationships
    
    def propagate_confidence(self, subject: str) -> None:
        """
        Propagate confidence scores through related facts.
        
        Args:
            subject: Subject to process
        """
        if subject not in self.verified_facts:
            return
        
        facts = self.verified_facts[subject]
        
        # Find high-confidence facts
        high_conf_facts = [f for f in facts if f.confidence_score.total_confidence >= 0.8]
        
        # Boost confidence of related low-confidence facts
        for low_conf_fact in [f for f in facts if f.confidence_score.total_confidence < 0.6]:
            for high_conf_fact in high_conf_facts:
                if self._facts_related(low_conf_fact, high_conf_fact):
                    # Boost by 10% if related to high-confidence fact
                    old_confidence = low_conf_fact.confidence_score.total_confidence
                    new_confidence = min(0.8, old_confidence * 1.1)
                    low_conf_fact.confidence_score.total_confidence = new_confidence
                    
                    logger.info(
                        f"Confidence boosted for related fact: "
                        f"{old_confidence:.2f} -> {new_confidence:.2f}"
                    )
        
        logger.info(f"Confidence propagation complete for {subject}")
    
    def query_learned_knowledge(
        self,
        query: str,
        subject: Optional[str] = None,
        min_confidence: float = 0.4,
        limit: int = 10
    ) -> List[VerifiedFact]:
        """
        Query learned knowledge.
        
        Args:
            query: Search query
            subject: Optional subject filter
            min_confidence: Minimum confidence threshold
            limit: Maximum results
        
        Returns:
            List of matching VerifiedFacts
        """
        results = []
        
        # Filter by subject if specified
        subjects_to_search = [subject] if subject else self.verified_facts.keys()
        
        for subj in subjects_to_search:
            if subj not in self.verified_facts:
                continue
            
            for fact in self.verified_facts[subj]:
                # Check confidence threshold
                if fact.confidence_score.total_confidence < min_confidence:
                    continue
                
                # Simple keyword matching (could be enhanced with embeddings)
                if query.lower() in fact.content.lower():
                    results.append(fact)
        
        # Sort by confidence
        results.sort(key=lambda f: f.confidence_score.total_confidence, reverse=True)
        
        # Apply limit
        results = results[:limit]
        
        logger.info(f"Query '{query}' returned {len(results)} results")
        
        return results
    
    def get_learning_summary(self, subject: str) -> Optional[LearningSummary]:
        """
        Get learning summary for a subject.
        
        Args:
            subject: Subject (ticker or topic)
        
        Returns:
            LearningSummary or None
        """
        if subject not in self.verified_facts or not self.verified_facts[subject]:
            return None
        
        facts = self.verified_facts[subject]
        
        # Calculate statistics
        total_facts = len(facts)
        avg_confidence = sum(f.confidence_score.total_confidence for f in facts) / total_facts
        last_updated = max(f.learned_at for f in facts)
        
        # Count by fact type
        fact_types = {}
        for fact in facts:
            type_name = fact.fact_type.value
            fact_types[type_name] = fact_types.get(type_name, 0) + 1
        
        # Count high confidence facts
        high_confidence_facts = sum(1 for f in facts if f.confidence_score.total_confidence >= 0.7)
        
        # Get unique sources
        sources_used = list(set(f.source_url for f in facts))
        
        # Extract key insights (high confidence facts)
        key_insights = [
            f.content
            for f in sorted(facts, key=lambda x: x.confidence_score.total_confidence, reverse=True)[:5]
        ]
        
        summary = LearningSummary(
            subject=subject,
            total_facts=total_facts,
            avg_confidence=avg_confidence,
            last_updated=last_updated,
            fact_types=fact_types,
            high_confidence_facts=high_confidence_facts,
            sources_used=sources_used,
            key_insights=key_insights
        )
        
        logger.info(f"Learning summary generated for {subject}: {total_facts} facts, avg confidence {avg_confidence:.2f}")
        
        return summary
    
    def update_fact_accuracy(
        self,
        subject: str,
        fact_content: str,
        was_accurate: bool
    ) -> bool:
        """
        Update fact accuracy based on validation.
        
        Args:
            subject: Subject
            fact_content: Fact content to update
            was_accurate: Whether fact was accurate
        
        Returns:
            True if updated
        """
        if subject not in self.verified_facts:
            return False
        
        for fact in self.verified_facts[subject]:
            if fact.content == fact_content:
                # Update accuracy in scorer
                self.scorer.update_based_on_accuracy(
                    fact_id=f"{subject}_{hash(fact_content)}",
                    fact_type=fact.fact_type,
                    actual_outcome=was_accurate
                )
                
                # Recalculate confidence
                age_days = (datetime.now() - fact.learned_at).days
                new_confidence = self.scorer.calculate_confidence(
                    fact_id=f"{subject}_{hash(fact_content)}",
                    fact_type=fact.fact_type,
                    source_credibility=fact.source_verification.credibility_score,
                    cross_validation_score=0.7,  # Assume moderate validation
                    age_days=age_days
                )
                
                fact.confidence_score = new_confidence
                
                logger.info(
                    f"Fact accuracy updated: {subject} - "
                    f"{'✓ correct' if was_accurate else '✗ incorrect'}"
                )
                
                return True
        
        return False
    
    def get_all_subjects(self) -> List[str]:
        """Get all subjects with learned facts"""
        return list(self.verified_facts.keys())
    
    def get_fact_count(self, subject: Optional[str] = None) -> int:
        """Get total fact count"""
        if subject:
            return len(self.verified_facts.get(subject, []))
        return sum(len(facts) for facts in self.verified_facts.values())
    
    def get_stats(self) -> Dict:
        """Get integrator statistics"""
        total_facts = self.get_fact_count()
        total_subjects = len(self.verified_facts)
        
        if total_facts == 0:
            return {
                "total_facts": 0,
                "total_subjects": 0,
                "avg_confidence": 0.0,
                "avg_facts_per_subject": 0.0
            }
        
        all_confidences = [
            fact.confidence_score.total_confidence
            for facts in self.verified_facts.values()
            for fact in facts
        ]
        
        return {
            "total_facts": total_facts,
            "total_subjects": total_subjects,
            "avg_confidence": sum(all_confidences) / len(all_confidences),
            "avg_facts_per_subject": total_facts / total_subjects
        }
    
    # Private methods
    
    def _facts_related(self, fact1: VerifiedFact, fact2: VerifiedFact) -> bool:
        """Check if two facts are related"""
        # Simple heuristic: same subject and close in time
        if fact1.subject != fact2.subject:
            return False
        
        time_diff = abs((fact1.learned_at - fact2.learned_at).total_seconds())
        
        # Within 1 day considered related
        return time_diff < 86400


# Global instance
_integrator = None


def get_knowledge_integrator() -> KnowledgeIntegrator:
    """Get global KnowledgeIntegrator instance"""
    global _integrator
    if _integrator is None:
        _integrator = KnowledgeIntegrator()
    return _integrator

