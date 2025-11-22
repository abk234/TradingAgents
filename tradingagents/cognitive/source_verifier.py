# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Source Verification System for Eddie v2.0
Phase 2.4: Advanced Autonomous Learning

Validates and scores the credibility of information sources for autonomous learning.
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SourceTier(Enum):
    """Source credibility tiers"""
    TIER_1 = (0.9, 1.0, "Major Financial News")  # Bloomberg, Reuters, WSJ
    TIER_2 = (0.7, 0.9, "Reputable News")        # NYT, WaPo, FT
    TIER_3 = (0.5, 0.7, "Industry Sources")      # Smaller financial sites, blogs
    TIER_4 = (0.3, 0.5, "Social/Forums")         # Reddit, Twitter, forums
    TIER_5 = (0.0, 0.3, "Unknown/Suspicious")    # Unknown sources
    
    def __init__(self, min_score, max_score, description):
        self.min_score = min_score
        self.max_score = max_score
        self.description = description


class BiasLevel(Enum):
    """Content bias levels"""
    NEUTRAL = "neutral"
    SLIGHTLY_BIASED = "slightly_biased"
    MODERATELY_BIASED = "moderately_biased"
    HIGHLY_BIASED = "highly_biased"


@dataclass
class VerificationResult:
    """Result of source verification"""
    url: str
    domain: str
    credibility_score: float
    tier: SourceTier
    bias_level: BiasLevel
    bias_score: float
    recency_days: Optional[int]
    publish_date: Optional[datetime]
    verification_timestamp: datetime
    notes: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "url": self.url,
            "domain": self.domain,
            "credibility_score": self.credibility_score,
            "tier": self.tier.name,
            "tier_description": self.tier.description,
            "bias_level": self.bias_level.value,
            "bias_score": self.bias_score,
            "recency_days": self.recency_days,
            "publish_date": self.publish_date.isoformat() if self.publish_date else None,
            "verification_timestamp": self.verification_timestamp.isoformat(),
            "notes": self.notes
        }


class SourceVerifier:
    """
    Verifies and scores the credibility of information sources.
    
    Features:
    - Domain credibility scoring
    - Bias detection
    - Recency validation
    - Source tier classification
    """
    
    # Trusted domains by tier
    TIER_1_DOMAINS = {
        'bloomberg.com', 'reuters.com', 'wsj.com', 'marketwatch.com',
        'cnbc.com', 'ft.com', 'morningstar.com', 'barrons.com',
        'seekingalpha.com', 'investopedia.com', 'sec.gov', 'investor.gov'
    }
    
    TIER_2_DOMAINS = {
        'nytimes.com', 'washingtonpost.com', 'forbes.com', 'businessinsider.com',
        'fool.com', 'thestreet.com', 'finance.yahoo.com', 'zacks.com',
        'money.cnn.com', 'bbc.com', 'theguardian.com', 'economist.com'
    }
    
    TIER_3_DOMAINS = {
        'medium.com', 'substack.com', 'blog.', 'investing.com',
        'tradingview.com', 'stocktwits.com', 'finviz.com'
    }
    
    TIER_4_DOMAINS = {
        'reddit.com', 'twitter.com', 'x.com', 'facebook.com',
        'youtube.com', 'discord.com', 'telegram.org'
    }
    
    # Bias indicators (words that may indicate bias)
    BIAS_KEYWORDS = {
        'highly_biased': [
            'guaranteed', 'never fail', 'secret', 'shocking', 'exposed',
            'they don\'t want you to know', 'insiders', 'pump', 'moon',
            'to the moon', 'guaranteed profit', 'risk-free'
        ],
        'moderately_biased': [
            'amazing', 'incredible', 'unbelievable', 'revolutionary',
            'game-changer', 'must buy', 'hot stock', 'explosive'
        ],
        'slightly_biased': [
            'strongly recommend', 'highly likely', 'certain to',
            'definitely', 'obviously', 'clearly the best'
        ]
    }
    
    def __init__(self):
        """Initialize source verifier"""
        self.verification_cache: Dict[str, VerificationResult] = {}
        logger.info("SourceVerifier initialized")
    
    def verify_source(
        self, 
        url: str, 
        content: Optional[str] = None,
        publish_date: Optional[datetime] = None
    ) -> VerificationResult:
        """
        Verify a source and return comprehensive verification result.
        
        Args:
            url: URL of the source
            content: Optional content text for bias detection
            publish_date: Optional publish date (if known)
        
        Returns:
            VerificationResult with credibility score, bias, recency
        """
        # Check cache
        cache_key = f"{url}_{hash(content) if content else 'nocontent'}"
        if cache_key in self.verification_cache:
            logger.debug(f"Cache hit for {url}")
            return self.verification_cache[cache_key]
        
        logger.info(f"Verifying source: {url}")
        
        # Extract domain
        domain = self._extract_domain(url)
        
        # Calculate credibility score
        credibility_score, tier = self._calculate_credibility_score(domain, url)
        
        # Detect bias
        bias_level, bias_score = self._detect_bias(content) if content else (BiasLevel.NEUTRAL, 0.0)
        
        # Calculate recency
        recency_days = self._calculate_recency(publish_date) if publish_date else None
        
        # Generate notes
        notes = self._generate_notes(tier, bias_level, recency_days)
        
        # Create result
        result = VerificationResult(
            url=url,
            domain=domain,
            credibility_score=credibility_score,
            tier=tier,
            bias_level=bias_level,
            bias_score=bias_score,
            recency_days=recency_days,
            publish_date=publish_date,
            verification_timestamp=datetime.now(),
            notes=notes
        )
        
        # Cache result
        self.verification_cache[cache_key] = result
        
        logger.info(f"Verification complete: {domain} - Score: {credibility_score:.2f}, Tier: {tier.name}")
        
        return result
    
    def domain_credibility_score(self, url: str) -> float:
        """
        Get credibility score for a domain (0-1).
        
        Args:
            url: URL to check
        
        Returns:
            Credibility score (0-1)
        """
        domain = self._extract_domain(url)
        score, _ = self._calculate_credibility_score(domain, url)
        return score
    
    def extract_publish_date(self, content: str) -> Optional[datetime]:
        """
        Extract publish date from content.
        
        Args:
            content: Article content or HTML
        
        Returns:
            Extracted datetime or None
        """
        # Common date patterns
        patterns = [
            r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
            r'(\d{2}/\d{2}/\d{4})',  # MM/DD/YYYY
            r'(\w+ \d{1,2}, \d{4})', # Month DD, YYYY
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                date_str = match.group(1)
                try:
                    # Try different parsing methods
                    for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%B %d, %Y']:
                        try:
                            return datetime.strptime(date_str, fmt)
                        except ValueError:
                            continue
                except Exception as e:
                    logger.debug(f"Failed to parse date '{date_str}': {e}")
        
        return None
    
    def verify_fact(
        self,
        fact: str,
        sources: List[Tuple[str, str]]  # List of (url, content) tuples
    ) -> Dict:
        """
        Verify a fact across multiple sources.
        
        Args:
            fact: Fact to verify
            sources: List of (url, content) tuples
        
        Returns:
            Verification summary with confidence score
        """
        if not sources:
            return {
                "fact": fact,
                "verified": False,
                "confidence": 0.0,
                "sources_checked": 0,
                "notes": ["No sources provided"]
            }
        
        verifications = []
        for url, content in sources:
            result = self.verify_source(url, content)
            verifications.append(result)
        
        # Calculate overall confidence based on source credibility
        avg_credibility = sum(v.credibility_score for v in verifications) / len(verifications)
        
        # Adjust for number of sources (more sources = higher confidence)
        source_count_factor = min(1.0, len(sources) / 3.0)  # Max out at 3 sources
        
        # Adjust for bias (lower bias = higher confidence)
        avg_bias = sum(v.bias_score for v in verifications) / len(verifications)
        bias_factor = 1.0 - (avg_bias * 0.3)  # Bias can reduce confidence by up to 30%
        
        # Calculate final confidence
        confidence = avg_credibility * source_count_factor * bias_factor
        
        return {
            "fact": fact,
            "verified": confidence >= 0.6,
            "confidence": confidence,
            "sources_checked": len(sources),
            "avg_credibility": avg_credibility,
            "avg_bias": avg_bias,
            "source_details": [v.to_dict() for v in verifications],
            "notes": self._generate_verification_notes(verifications, confidence)
        }
    
    def detect_bias(self, content: str) -> Tuple[BiasLevel, float]:
        """
        Detect bias in content.
        
        Args:
            content: Content to analyze
        
        Returns:
            Tuple of (BiasLevel, bias_score)
        """
        return self._detect_bias(content)
    
    # Private methods
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except Exception as e:
            logger.warning(f"Failed to parse URL {url}: {e}")
            return "unknown"
    
    def _calculate_credibility_score(self, domain: str, url: str) -> Tuple[float, SourceTier]:
        """Calculate credibility score and tier for domain"""
        # Check exact domain matches
        if domain in self.TIER_1_DOMAINS:
            return 0.95, SourceTier.TIER_1
        
        if domain in self.TIER_2_DOMAINS:
            return 0.80, SourceTier.TIER_2
        
        # Check partial matches for tier 3 (e.g., blog.example.com)
        for tier3_domain in self.TIER_3_DOMAINS:
            if tier3_domain in domain or domain in tier3_domain:
                return 0.60, SourceTier.TIER_3
        
        if domain in self.TIER_4_DOMAINS:
            return 0.40, SourceTier.TIER_4
        
        # Unknown domain - use heuristics
        # .gov or .edu domains get higher scores
        if domain.endswith('.gov') or domain.endswith('.edu'):
            return 0.85, SourceTier.TIER_2
        
        # Default to tier 5
        return 0.20, SourceTier.TIER_5
    
    def _detect_bias(self, content: str) -> Tuple[BiasLevel, float]:
        """Detect bias in content"""
        if not content:
            return BiasLevel.NEUTRAL, 0.0
        
        content_lower = content.lower()
        
        # Count bias keywords
        highly_biased_count = sum(
            1 for keyword in self.BIAS_KEYWORDS['highly_biased']
            if keyword in content_lower
        )
        
        moderately_biased_count = sum(
            1 for keyword in self.BIAS_KEYWORDS['moderately_biased']
            if keyword in content_lower
        )
        
        slightly_biased_count = sum(
            1 for keyword in self.BIAS_KEYWORDS['slightly_biased']
            if keyword in content_lower
        )
        
        # Calculate bias score (0-1)
        total_keywords = len(content_lower.split())
        if total_keywords == 0:
            return BiasLevel.NEUTRAL, 0.0
        
        bias_score = (
            highly_biased_count * 0.5 +
            moderately_biased_count * 0.3 +
            slightly_biased_count * 0.1
        ) / max(1, total_keywords / 100)  # Normalize per 100 words
        
        # Determine bias level
        if bias_score >= 0.7:
            return BiasLevel.HIGHLY_BIASED, bias_score
        elif bias_score >= 0.4:
            return BiasLevel.MODERATELY_BIASED, bias_score
        elif bias_score >= 0.15:
            return BiasLevel.SLIGHTLY_BIASED, bias_score
        else:
            return BiasLevel.NEUTRAL, bias_score
    
    def _calculate_recency(self, publish_date: datetime) -> int:
        """Calculate recency in days"""
        if not publish_date:
            return None
        
        now = datetime.now()
        delta = now - publish_date
        return delta.days
    
    def _generate_notes(
        self,
        tier: SourceTier,
        bias_level: BiasLevel,
        recency_days: Optional[int]
    ) -> List[str]:
        """Generate verification notes"""
        notes = []
        
        # Tier notes
        if tier == SourceTier.TIER_1:
            notes.append("✅ Highly credible source (Tier 1)")
        elif tier == SourceTier.TIER_2:
            notes.append("✅ Credible source (Tier 2)")
        elif tier == SourceTier.TIER_3:
            notes.append("⚠️ Moderate credibility (Tier 3)")
        elif tier == SourceTier.TIER_4:
            notes.append("⚠️ Lower credibility - social/forum source (Tier 4)")
        else:
            notes.append("❌ Unknown source - use with caution (Tier 5)")
        
        # Bias notes
        if bias_level == BiasLevel.HIGHLY_BIASED:
            notes.append("⚠️ Highly biased content detected")
        elif bias_level == BiasLevel.MODERATELY_BIASED:
            notes.append("⚠️ Moderate bias detected")
        elif bias_level == BiasLevel.SLIGHTLY_BIASED:
            notes.append("ℹ️ Slight bias detected")
        
        # Recency notes
        if recency_days is not None:
            if recency_days == 0:
                notes.append("✅ Published today")
            elif recency_days <= 1:
                notes.append("✅ Very recent (within 24 hours)")
            elif recency_days <= 7:
                notes.append("✅ Recent (within a week)")
            elif recency_days <= 30:
                notes.append("ℹ️ Moderate age (within a month)")
            else:
                notes.append(f"⚠️ Older content ({recency_days} days old)")
        
        return notes
    
    def _generate_verification_notes(
        self,
        verifications: List[VerificationResult],
        confidence: float
    ) -> List[str]:
        """Generate notes for fact verification"""
        notes = []
        
        # Confidence assessment
        if confidence >= 0.8:
            notes.append("✅ High confidence verification")
        elif confidence >= 0.6:
            notes.append("✅ Moderate confidence verification")
        elif confidence >= 0.4:
            notes.append("⚠️ Low confidence verification")
        else:
            notes.append("❌ Very low confidence - verification failed")
        
        # Source quality
        tier_1_count = sum(1 for v in verifications if v.tier == SourceTier.TIER_1)
        tier_2_count = sum(1 for v in verifications if v.tier == SourceTier.TIER_2)
        
        if tier_1_count > 0:
            notes.append(f"✅ {tier_1_count} Tier 1 source(s) confirm")
        if tier_2_count > 0:
            notes.append(f"✅ {tier_2_count} Tier 2 source(s) confirm")
        
        # Bias warning
        biased_count = sum(
            1 for v in verifications
            if v.bias_level in [BiasLevel.MODERATELY_BIASED, BiasLevel.HIGHLY_BIASED]
        )
        if biased_count > 0:
            notes.append(f"⚠️ {biased_count} source(s) show bias")
        
        return notes


# Global instance
_verifier = None


def get_source_verifier() -> SourceVerifier:
    """Get global SourceVerifier instance"""
    global _verifier
    if _verifier is None:
        _verifier = SourceVerifier()
    return _verifier

