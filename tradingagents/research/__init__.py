"""
Autonomous Research Module - Eddie v2.0

Web crawling and autonomous learning capabilities.
"""

from .web_crawler import (
    WebCrawler,
    CrawlResult,
    SearchResult,
    AutonomousResearcher,
    get_autonomous_researcher
)

from .autonomous_learner import (
    AdvancedAutonomousLearner,
    SourceVerifier,
    ConflictResolver,
    LearningTrigger,
    LearningEvent,
    SourceVerification,
    KnowledgeConflict,
    get_advanced_learner
)

__all__ = [
    # Basic Research
    'WebCrawler',
    'CrawlResult',
    'SearchResult',
    'AutonomousResearcher',
    'get_autonomous_researcher',
    
    # Advanced Learning
    'AdvancedAutonomousLearner',
    'SourceVerifier',
    'ConflictResolver',
    'LearningTrigger',
    'LearningEvent',
    'SourceVerification',
    'KnowledgeConflict',
    'get_advanced_learner',
]

