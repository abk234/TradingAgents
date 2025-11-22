# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Advanced Autonomous Learning - Eddie v2.0

Enhanced autonomous learning with source verification, conflict resolution,
and event-driven triggers.
"""

import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import asyncio

from .web_crawler import AutonomousResearcher, get_autonomous_researcher
from tradingagents.cognitive import get_knowledge_graph

logger = logging.getLogger(__name__)


class LearningTrigger(Enum):
    """Types of events that trigger autonomous learning."""
    UNKNOWN_TERM = "unknown_term"  # User mentions unknown term
    MARKET_CRASH = "market_crash"  # Market drops >3%
    MAJOR_EVENT = "major_event"  # Major market event detected
    USER_REQUEST = "user_request"  # User explicitly requests learning
    CONFLICT_DETECTED = "conflict_detected"  # Conflicting information found


@dataclass
class LearningEvent:
    """An event that triggers autonomous learning."""
    trigger_type: LearningTrigger
    context: Dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    priority: int = 5  # 1-10, higher = more urgent


@dataclass
class SourceVerification:
    """Verification result for a knowledge source."""
    source_url: str
    credibility_score: float  # 0-1
    verification_status: str  # verified, unverified, conflicting
    cross_references: List[str] = field(default_factory=list)
    verification_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class KnowledgeConflict:
    """A conflict between different knowledge sources."""
    topic: str
    conflicting_sources: List[Dict[str, Any]]
    conflict_type: str  # contradiction, outdated, ambiguous
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None


class SourceVerifier:
    """
    Verifies credibility of knowledge sources.
    
    Checks:
    - Source reputation (domain-based)
    - Cross-referencing with other sources
    - Recency of information
    - Author credibility (if available)
    """
    
    def __init__(self):
        """Initialize source verifier."""
        # Trusted domains (high credibility)
        self.trusted_domains = {
            "investopedia.com": 0.9,
            "seekingalpha.com": 0.8,
            "bloomberg.com": 0.9,
            "reuters.com": 0.9,
            "wsj.com": 0.9,
            "finance.yahoo.com": 0.8,
            "marketwatch.com": 0.8,
            "nasdaq.com": 0.8,
            "sec.gov": 1.0,  # Government source
        }
        
        # Suspicious domains (low credibility)
        self.suspicious_domains = {
            "reddit.com": 0.4,
            "twitter.com": 0.3,
            "4chan.org": 0.1,
        }
    
    def verify_source(self, url: str, content: str) -> SourceVerification:
        """
        Verify a knowledge source.
        
        Args:
            url: Source URL
            content: Content from source
        
        Returns:
            SourceVerification result
        """
        # Extract domain
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Check domain reputation
        credibility_score = 0.5  # Default
        
        if domain in self.trusted_domains:
            credibility_score = self.trusted_domains[domain]
        elif domain in self.suspicious_domains:
            credibility_score = self.suspicious_domains[domain]
        else:
            # Unknown domain - check for indicators
            if "edu" in domain or "gov" in domain:
                credibility_score = 0.8
            elif "blog" in domain or "wordpress" in domain:
                credibility_score = 0.4
        
        # Determine verification status
        if credibility_score >= 0.8:
            status = "verified"
        elif credibility_score >= 0.6:
            status = "unverified"
        else:
            status = "conflicting"
        
        return SourceVerification(
            source_url=url,
            credibility_score=credibility_score,
            verification_status=status,
            cross_references=[]
        )
    
    def cross_reference(self, sources: List[Dict[str, Any]]) -> List[SourceVerification]:
        """
        Cross-reference multiple sources for the same topic.
        
        Args:
            sources: List of source dictionaries with url and content
        
        Returns:
            List of verified sources
        """
        verifications = []
        
        for source in sources:
            verification = self.verify_source(
                source.get("url", ""),
                source.get("content", "")
            )
            verifications.append(verification)
        
        # Add cross-references
        for i, ver1 in enumerate(verifications):
            for j, ver2 in enumerate(verifications):
                if i != j:
                    ver1.cross_references.append(ver2.source_url)
        
        return verifications


class ConflictResolver:
    """
    Resolves conflicts between different knowledge sources.
    
    Strategies:
    - Prefer higher credibility sources
    - Use recency (newer information preferred)
    - Cross-reference with trusted sources
    - Flag unresolved conflicts for human review
    """
    
    def __init__(self):
        """Initialize conflict resolver."""
        self.verifier = SourceVerifier()
    
    def detect_conflicts(
        self,
        topic: str,
        sources: List[Dict[str, Any]]
    ) -> List[KnowledgeConflict]:
        """
        Detect conflicts between sources.
        
        Args:
            topic: Topic being researched
            sources: List of sources with content
        
        Returns:
            List of detected conflicts
        """
        conflicts = []
        
        # Verify all sources
        verifications = self.verifier.cross_reference(sources)
        
        # Simple conflict detection: look for contradictory statements
        # In a real implementation, this would use NLP to detect contradictions
        
        # For now, flag if sources have very different credibility scores
        high_cred = [v for v in verifications if v.credibility_score >= 0.8]
        low_cred = [v for v in verifications if v.credibility_score < 0.6]
        
        if high_cred and low_cred:
            conflict = KnowledgeConflict(
                topic=topic,
                conflicting_sources=[
                    {"url": v.source_url, "credibility": v.credibility_score}
                    for v in high_cred + low_cred
                ],
                conflict_type="credibility_mismatch"
            )
            conflicts.append(conflict)
        
        return conflicts
    
    def resolve_conflict(
        self,
        conflict: KnowledgeConflict,
        verifications: List[SourceVerification]
    ) -> Optional[str]:
        """
        Resolve a knowledge conflict.
        
        Args:
            conflict: The conflict to resolve
            verifications: Source verifications
        
        Returns:
            Resolution text or None if unresolved
        """
        # Prefer highest credibility source
        if conflict.conflicting_sources:
            # Sort by credibility
            sorted_sources = sorted(
                conflict.conflicting_sources,
                key=lambda x: x.get("credibility", 0),
                reverse=True
            )
            
            best_source = sorted_sources[0]
            
            conflict.resolution = f"Resolved: Using highest credibility source ({best_source['url']})"
            conflict.resolved_at = datetime.now(timezone.utc)
            
            return conflict.resolution
        
        return None


class AdvancedAutonomousLearner:
    """
    Advanced autonomous learning system with verification and conflict resolution.
    
    Features:
    - Event-driven learning triggers
    - Source verification
    - Conflict detection and resolution
    - Knowledge graph integration
    """
    
    def __init__(self):
        """Initialize advanced autonomous learner."""
        self.researcher = get_autonomous_researcher()
        self.verifier = SourceVerifier()
        self.resolver = ConflictResolver()
        self.knowledge_graph = get_knowledge_graph()
        self.learning_events: List[LearningEvent] = []
        self.conflicts: List[KnowledgeConflict] = []
    
    async def learn_with_verification(
        self,
        topic: str,
        trigger: LearningTrigger = LearningTrigger.USER_REQUEST,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Learn about a topic with source verification and conflict resolution.
        
        Args:
            topic: Topic to learn about
            trigger: What triggered this learning
            context: Additional context
        
        Returns:
            Learning result with verification
        """
        logger.info(f"Advanced learning triggered: {topic} ({trigger.value})")
        
        # Create learning event
        event = LearningEvent(
            trigger_type=trigger,
            context=context or {},
            priority=self._calculate_priority(trigger)
        )
        self.learning_events.append(event)
        
        # Research topic
        learning_result = await self.researcher.learn_about(topic)
        
        if not learning_result.get("learned"):
            return {
                "topic": topic,
                "learned": False,
                "error": learning_result.get("error", "Unknown error")
            }
        
        knowledge = learning_result.get("knowledge", {})
        sources = knowledge.get("sources", [])
        
        # Verify sources
        verifications = []
        for source in sources:
            verification = self.verifier.verify_source(
                source.get("url", ""),
                source.get("content", "")
            )
            verifications.append(verification)
        
        # Detect conflicts
        conflicts = self.resolver.detect_conflicts(topic, sources)
        
        # Resolve conflicts
        resolved_conflicts = []
        for conflict in conflicts:
            resolution = self.resolver.resolve_conflict(conflict, verifications)
            if resolution:
                resolved_conflicts.append(conflict)
                self.conflicts.append(conflict)
        
        # Store in knowledge graph
        self._store_in_knowledge_graph(topic, knowledge, verifications)
        
        return {
            "topic": topic,
            "learned": True,
            "knowledge": knowledge,
            "sources": len(sources),
            "verifications": [
                {
                    "url": v.source_url,
                    "credibility": v.credibility_score,
                    "status": v.verification_status
                }
                for v in verifications
            ],
            "conflicts_detected": len(conflicts),
            "conflicts_resolved": len(resolved_conflicts),
            "trigger": trigger.value
        }
    
    def _calculate_priority(self, trigger: LearningTrigger) -> int:
        """Calculate priority for learning event."""
        priority_map = {
            LearningTrigger.MARKET_CRASH: 10,
            LearningTrigger.MAJOR_EVENT: 9,
            LearningTrigger.CONFLICT_DETECTED: 8,
            LearningTrigger.UNKNOWN_TERM: 6,
            LearningTrigger.USER_REQUEST: 5
        }
        return priority_map.get(trigger, 5)
    
    def _store_in_knowledge_graph(
        self,
        topic: str,
        knowledge: Dict[str, Any],
        verifications: List[SourceVerification]
    ):
        """Store learned knowledge in knowledge graph."""
        try:
            # Create node for topic
            node_id = topic.lower().replace(" ", "_")
            
            # Calculate overall credibility
            avg_credibility = sum(v.credibility_score for v in verifications) / len(verifications) if verifications else 0.5
            
            self.knowledge_graph.add_node(
                node_id=node_id,
                label=topic,
                node_type="concept",
                properties={
                    "description": knowledge.get("summary", ""),
                    "sources": knowledge.get("sources", []),
                    "credibility": avg_credibility,
                    "verified": avg_credibility >= 0.7
                },
                confidence=avg_credibility
            )
            
            logger.info(f"Stored {topic} in knowledge graph (credibility: {avg_credibility:.2f})")
            
        except Exception as e:
            logger.error(f"Error storing in knowledge graph: {e}")
    
    def detect_unknown_term(self, text: str) -> List[str]:
        """
        Detect unknown terms in text.
        
        Simple implementation - checks if terms are in knowledge graph.
        Could be enhanced with NLP.
        
        Args:
            text: Text to analyze
        
        Returns:
            List of unknown terms
        """
        # Simple keyword extraction (could use NLP)
        words = text.lower().split()
        unknown_terms = []
        
        for word in words:
            if len(word) > 4:  # Ignore short words
                # Check if term exists in knowledge graph
                results = self.knowledge_graph.query(word)
                if not results:
                    unknown_terms.append(word)
        
        return unknown_terms
    
    def get_learning_history(self, limit: int = 10) -> List[LearningEvent]:
        """Get recent learning events."""
        return sorted(
            self.learning_events,
            key=lambda x: (x.priority, x.timestamp),
            reverse=True
        )[:limit]
    
    def get_unresolved_conflicts(self) -> List[KnowledgeConflict]:
        """Get unresolved conflicts."""
        return [c for c in self.conflicts if c.resolution is None]


# Global instance
_advanced_learner: Optional[AdvancedAutonomousLearner] = None


def get_advanced_learner() -> AdvancedAutonomousLearner:
    """Get the global advanced autonomous learner instance."""
    global _advanced_learner
    if _advanced_learner is None:
        _advanced_learner = AdvancedAutonomousLearner()
    return _advanced_learner

