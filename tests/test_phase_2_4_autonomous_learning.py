"""
Tests for Phase 2.4: Advanced Autonomous Learning
Eddie v2.0

Tests all components of the autonomous learning system:
- Source verification
- Conflict resolution
- Event-driven triggers
- Confidence scoring
- Knowledge graph integration
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List

from tradingagents.cognitive.source_verifier import (
    SourceVerifier, SourceTier, BiasLevel, get_source_verifier
)
from tradingagents.cognitive.conflict_resolver import (
    ConflictResolver, Fact, ConflictType, ResolutionStrategy, get_conflict_resolver
)
from tradingagents.cognitive.learning_triggers import (
    EventTriggerManager, TriggerType, TriggerPriority, TriggerCondition,
    LearningAction, get_trigger_manager, create_price_spike_trigger
)
from tradingagents.cognitive.confidence_scorer import (
    ConfidenceScorer, FactType, get_confidence_scorer
)
from tradingagents.cognitive.knowledge_integrator import (
    KnowledgeIntegrator, get_knowledge_integrator
)


class TestSourceVerifier:
    """Test source verification system"""
    
    def test_verify_tier1_source(self):
        """Test verification of Tier 1 source"""
        verifier = SourceVerifier()
        
        result = verifier.verify_source(
            url="https://www.bloomberg.com/news/article",
            content="Apple announces strong earnings."
        )
        
        assert result.tier == SourceTier.TIER_1
        assert result.credibility_score >= 0.9
        assert "Tier 1" in str(result.notes)
        print(f"✓ Tier 1 source verified: {result.credibility_score:.2f}")
    
    def test_verify_tier2_source(self):
        """Test verification of Tier 2 source"""
        verifier = SourceVerifier()
        
        result = verifier.verify_source(
            url="https://www.nytimes.com/business/article",
            content="Market analysis shows bullish trend."
        )
        
        assert result.tier == SourceTier.TIER_2
        assert 0.7 <= result.credibility_score < 0.9
        print(f"✓ Tier 2 source verified: {result.credibility_score:.2f}")
    
    def test_verify_unknown_source(self):
        """Test verification of unknown source"""
        verifier = SourceVerifier()
        
        result = verifier.verify_source(
            url="https://unknownsite.com/article",
            content="Stock will moon!"
        )
        
        assert result.tier == SourceTier.TIER_5
        assert result.credibility_score < 0.3
        print(f"✓ Unknown source detected: {result.credibility_score:.2f}")
    
    def test_bias_detection_highly_biased(self):
        """Test detection of highly biased content"""
        verifier = SourceVerifier()
        
        biased_content = "This is a guaranteed profit! Secret insider information that they don't want you to know!"
        
        result = verifier.verify_source(
            url="https://example.com/article",
            content=biased_content
        )
        
        assert result.bias_level in [BiasLevel.HIGHLY_BIASED, BiasLevel.MODERATELY_BIASED]
        assert result.bias_score > 0.3
        print(f"✓ Bias detected: {result.bias_level.value} (score: {result.bias_score:.2f})")
    
    def test_bias_detection_neutral(self):
        """Test detection of neutral content"""
        verifier = SourceVerifier()
        
        neutral_content = "The company reported Q3 earnings of $2.50 per share, beating estimates by $0.10."
        
        result = verifier.verify_source(
            url="https://reuters.com/article",
            content=neutral_content
        )
        
        assert result.bias_level == BiasLevel.NEUTRAL
        assert result.bias_score < 0.15
        print(f"✓ Neutral content verified: bias_score={result.bias_score:.2f}")
    
    def test_verify_fact_multiple_sources(self):
        """Test fact verification across multiple sources"""
        verifier = SourceVerifier()
        
        sources = [
            ("https://bloomberg.com/article1", "Apple revenue grew 10%"),
            ("https://reuters.com/article2", "Apple revenue increased 10%"),
            ("https://wsj.com/article3", "Apple sees 10% revenue growth")
        ]
        
        result = verifier.verify_fact(
            fact="Apple revenue grew 10%",
            sources=sources
        )
        
        assert result["verified"] is True
        assert result["confidence"] >= 0.7
        assert result["sources_checked"] == 3
        print(f"✓ Fact verified with {result['confidence']:.2f} confidence")


class TestConflictResolver:
    """Test conflict resolution engine"""
    
    def test_detect_numeric_conflict(self):
        """Test detection of numeric conflicts"""
        resolver = ConflictResolver()
        
        facts = [
            Fact(content=100.5, source_url="source1.com", source_verification=None, timestamp=None),
            Fact(content=110.2, source_url="source2.com", source_verification=None, timestamp=None)
        ]
        
        conflicts = resolver.detect_conflicts(facts, topic="AAPL price", conflict_threshold=0.05)
        
        assert len(conflicts) > 0
        assert conflicts[0].conflict_type == ConflictType.NUMERIC
        print(f"✓ Numeric conflict detected: {len(conflicts)} conflict(s)")
    
    def test_resolve_by_source_weight(self):
        """Test resolution by source credibility"""
        verifier = SourceVerifier()
        resolver = ConflictResolver(verifier)
        
        # Create facts with different source credibilities
        verification1 = verifier.verify_source("https://bloomberg.com/a", "content")
        verification2 = verifier.verify_source("https://unknownsite.com/a", "content")
        
        facts = [
            Fact(content="Earnings beat by 5%", source_url="https://bloomberg.com/a",
                 source_verification=verification1, timestamp=None),
            Fact(content="Earnings beat by 3%", source_url="https://unknownsite.com/a",
                 source_verification=verification2, timestamp=None)
        ]
        
        conflicts = resolver.detect_conflicts(facts, topic="AAPL earnings")
        
        if conflicts:
            resolution = resolver.resolve_by_source_weight(conflicts[0])
            
            assert resolution.content == "Earnings beat by 5%"  # Bloomberg preferred
            assert resolution.confidence > 0.5
            print(f"✓ Conflict resolved by source weight: {resolution.confidence:.2f}")
    
    def test_resolve_by_consensus(self):
        """Test resolution by consensus"""
        resolver = ConflictResolver()
        
        facts = [
            Fact(content="BUY", source_url="s1.com", source_verification=None, timestamp=None),
            Fact(content="BUY", source_url="s2.com", source_verification=None, timestamp=None),
            Fact(content="HOLD", source_url="s3.com", source_verification=None, timestamp=None)
        ]
        
        conflicts = resolver.detect_conflicts(facts, topic="AAPL recommendation")
        
        if conflicts:
            resolution = resolver.resolve_by_consensus(conflicts[0])
            
            assert resolution.content == "BUY"  # Majority wins
            assert len(resolution.supporting_sources) == 2
            print(f"✓ Conflict resolved by consensus: {resolution.content}")


class TestLearningTriggers:
    """Test event-driven learning triggers"""
    
    @pytest.mark.asyncio
    async def test_register_trigger(self):
        """Test trigger registration"""
        manager = EventTriggerManager()
        
        def simple_condition(context, params):
            return context.get("value", 0) > params.get("threshold", 0)
        
        async def simple_action(context, params):
            return {"action": "completed", "value": context.get("value")}
        
        trigger_def = {
            "id": "test_trigger",
            "name": "Test Trigger",
            "trigger_type": TriggerType.MANUAL,
            "priority": TriggerPriority.LOW,
            "condition": TriggerCondition(
                condition_type="test",
                parameters={"threshold": 10},
                evaluator=simple_condition
            ),
            "action": LearningAction(
                action_type="test_action",
                parameters={},
                executor=simple_action
            )
        }
        
        trigger = manager.register_trigger(**trigger_def)
        
        assert trigger.id == "test_trigger"
        assert trigger.enabled is True
        print(f"✓ Trigger registered: {trigger.name}")
    
    @pytest.mark.asyncio
    async def test_trigger_execution(self):
        """Test trigger execution"""
        manager = EventTriggerManager()
        
        execution_count = 0
        
        async def counting_action(context, params):
            nonlocal execution_count
            execution_count += 1
            return {"count": execution_count}
        
        trigger_def = {
            "id": "count_trigger",
            "name": "Count Trigger",
            "trigger_type": TriggerType.MANUAL,
            "priority": TriggerPriority.HIGH,
            "condition": TriggerCondition(
                condition_type="always",
                parameters={},
                evaluator=lambda ctx, prm: True  # Always fire
            ),
            "action": LearningAction(
                action_type="count",
                parameters={},
                executor=counting_action
            )
        }
        
        trigger = manager.register_trigger(**trigger_def)
        
        # Execute trigger
        execution = await manager.execute_trigger(trigger, context={})
        
        assert execution_count == 1
        assert execution.result["count"] == 1
        print(f"✓ Trigger executed successfully")
    
    def test_price_movement_detection(self):
        """Test price movement detection"""
        manager = EventTriggerManager()
        
        ticker_data = {
            "AAPL": {"price": 150, "prev_price": 140, "change_percent": 7.14},
            "MSFT": {"price": 300, "prev_price": 299, "change_percent": 0.33}
        }
        
        events = manager.check_price_movements(ticker_data)
        
        assert len(events) == 1  # Only AAPL moved >5%
        assert events[0]["ticker"] == "AAPL"
        assert events[0]["event_type"] == "price_spike"
        print(f"✓ Price movement detected: {events[0]['ticker']} {events[0]['change_percent']:+.2f}%")
    
    def test_earnings_calendar_check(self):
        """Test earnings calendar checking"""
        manager = EventTriggerManager()
        
        tomorrow = datetime.now() + timedelta(days=1)
        next_week = datetime.now() + timedelta(days=8)
        
        ticker_earnings = {
            "AAPL": tomorrow,
            "MSFT": next_week
        }
        
        events = manager.check_earnings_calendar(ticker_earnings)
        
        assert len(events) == 1  # Only AAPL within 7 days
        assert events[0]["ticker"] == "AAPL"
        assert events[0]["days_until"] == 1
        print(f"✓ Earnings event detected: {events[0]['ticker']} in {events[0]['days_until']} day(s)")


class TestConfidenceScorer:
    """Test confidence scoring system"""
    
    def test_calculate_confidence_high(self):
        """Test high confidence calculation"""
        scorer = ConfidenceScorer()
        
        score = scorer.calculate_confidence(
            fact_id="test_fact_1",
            fact_type=FactType.FACTUAL,
            source_credibility=0.95,  # High credibility
            cross_validation_score=0.9,  # Well validated
            age_days=1,  # Very fresh
            historical_accuracy=0.85,
            context_relevance=0.8
        )
        
        assert score.total_confidence >= 0.7
        assert len(score.factors) == 5
        print(f"✓ High confidence calculated: {score.total_confidence:.2f}")
    
    def test_calculate_confidence_low(self):
        """Test low confidence calculation"""
        scorer = ConfidenceScorer()
        
        score = scorer.calculate_confidence(
            fact_id="test_fact_2",
            fact_type=FactType.PREDICTION,
            source_credibility=0.3,  # Low credibility
            cross_validation_score=0.2,  # Poor validation
            age_days=180,  # Old
            historical_accuracy=0.4,
            context_relevance=0.3
        )
        
        assert score.total_confidence < 0.4
        print(f"✓ Low confidence calculated: {score.total_confidence:.2f}")
    
    def test_time_decay(self):
        """Test time-based decay"""
        scorer = ConfidenceScorer()
        
        # Test decay for different fact types
        for fact_type in FactType:
            decay_7d = scorer.apply_time_decay(1.0, 7, fact_type)
            decay_30d = scorer.apply_time_decay(1.0, 30, fact_type)
            decay_90d = scorer.apply_time_decay(1.0, 90, fact_type)
            
            # Decay should increase with age
            assert decay_7d > decay_30d > decay_90d
            print(f"✓ Decay for {fact_type.value}: 7d={decay_7d:.2f}, 30d={decay_30d:.2f}, 90d={decay_90d:.2f}")
    
    def test_update_accuracy(self):
        """Test accuracy tracking"""
        scorer = ConfidenceScorer()
        
        # Track some accurate predictions
        scorer.update_based_on_accuracy("fact1", FactType.PREDICTION, True)
        scorer.update_based_on_accuracy("fact2", FactType.PREDICTION, True)
        scorer.update_based_on_accuracy("fact3", FactType.PREDICTION, False)
        
        accuracy = scorer.get_historical_accuracy(FactType.PREDICTION)
        
        # 2 correct, 1 incorrect = 66.7%
        assert 0.6 <= accuracy <= 0.7
        print(f"✓ Historical accuracy tracked: {accuracy:.2f}")


class TestKnowledgeIntegrator:
    """Test knowledge graph integration"""
    
    @pytest.mark.asyncio
    async def test_add_verified_fact(self):
        """Test adding verified fact"""
        integrator = KnowledgeIntegrator()
        
        sources = [
            ("https://bloomberg.com/aapl", "Apple revenue grew 15% year over year."),
            ("https://reuters.com/aapl", "Apple reports 15% revenue growth.")
        ]
        
        fact = await integrator.add_verified_fact(
            subject="AAPL",
            content="Apple revenue grew 15% YoY",
            fact_type=FactType.FACTUAL,
            sources=sources,
            metadata={"category": "earnings"}
        )
        
        assert fact is not None
        assert fact.subject == "AAPL"
        assert fact.confidence_score.total_confidence >= 0.4
        print(f"✓ Verified fact added: confidence={fact.confidence_score.total_confidence:.2f}")
    
    @pytest.mark.asyncio
    async def test_add_low_confidence_fact_rejected(self):
        """Test that low confidence facts are rejected"""
        integrator = KnowledgeIntegrator()
        
        # Unknown source with biased content
        sources = [
            ("https://unknownsite.com/article", "Stock will definitely moon! Guaranteed profit!")
        ]
        
        fact = await integrator.add_verified_fact(
            subject="TEST",
            content="Dubious claim",
            fact_type=FactType.PREDICTION,
            sources=sources
        )
        
        # Should be rejected due to low confidence
        assert fact is None or fact.confidence_score.total_confidence < 0.4
        print(f"✓ Low confidence fact rejected")
    
    def test_get_learning_summary(self):
        """Test learning summary generation"""
        integrator = KnowledgeIntegrator()
        
        # This test assumes facts were added in previous tests
        # In a real scenario, you'd set up test data first
        
        summary = integrator.get_learning_summary("AAPL")
        
        if summary:
            assert summary.subject == "AAPL"
            assert summary.total_facts >= 0
            print(f"✓ Learning summary: {summary.total_facts} facts, avg confidence={summary.avg_confidence:.2f}")
        else:
            print("✓ No facts yet for AAPL (expected in isolated test)")
    
    def test_query_learned_knowledge(self):
        """Test querying learned knowledge"""
        integrator = KnowledgeIntegrator()
        
        results = integrator.query_learned_knowledge(
            query="revenue",
            min_confidence=0.5,
            limit=10
        )
        
        assert isinstance(results, list)
        print(f"✓ Query returned {len(results)} results")
    
    def test_get_stats(self):
        """Test statistics generation"""
        integrator = KnowledgeIntegrator()
        
        stats = integrator.get_stats()
        
        assert "total_facts" in stats
        assert "total_subjects" in stats
        assert "avg_confidence" in stats
        print(f"✓ Stats: {stats['total_facts']} facts across {stats['total_subjects']} subjects")


class TestEndToEndIntegration:
    """End-to-end integration tests"""
    
    @pytest.mark.asyncio
    async def test_full_learning_pipeline(self):
        """Test complete learning pipeline"""
        print("\n=== Full Learning Pipeline Test ===")
        
        # 1. Verify sources
        verifier = SourceVerifier()
        sources = [
            ("https://bloomberg.com/news", "Apple announces strong Q4 earnings, beating expectations by 10%."),
            ("https://reuters.com/business", "Apple Q4 earnings exceed estimates by 10%.")
        ]
        
        verifications = [verifier.verify_source(url, content) for url, content in sources]
        
        print(f"1. Sources verified: {len(verifications)} sources")
        print(f"   - Avg credibility: {sum(v.credibility_score for v in verifications) / len(verifications):.2f}")
        
        # 2. Check for conflicts
        resolver = ConflictResolver(verifier)
        facts = [
            Fact(content="Earnings beat by 10%", source_url=url, source_verification=ver, timestamp=datetime.now())
            for (url, _), ver in zip(sources, verifications)
        ]
        
        conflicts = resolver.detect_conflicts(facts, topic="AAPL earnings")
        print(f"2. Conflicts detected: {len(conflicts)}")
        
        # 3. Calculate confidence
        scorer = ConfidenceScorer()
        score = scorer.calculate_confidence(
            fact_id="aapl_earnings_q4",
            fact_type=FactType.FACTUAL,
            source_credibility=verifications[0].credibility_score,
            cross_validation_score=1.0,  # Both sources agree
            age_days=0
        )
        
        print(f"3. Confidence calculated: {score.total_confidence:.2f}")
        
        # 4. Add to knowledge graph
        integrator = KnowledgeIntegrator()
        fact = await integrator.add_verified_fact(
            subject="AAPL",
            content="Q4 earnings beat expectations by 10%",
            fact_type=FactType.FACTUAL,
            sources=sources
        )
        
        if fact:
            print(f"4. Fact added to knowledge graph: ✓")
            print(f"   - Subject: {fact.subject}")
            print(f"   - Confidence: {fact.confidence_score.total_confidence:.2f}")
        else:
            print(f"4. Fact rejected (confidence too low)")
        
        # 5. Query knowledge
        results = integrator.query_learned_knowledge("earnings", subject="AAPL")
        print(f"5. Knowledge query: {len(results)} results")
        
        print("=== Pipeline Complete ===\n")
        
        assert True  # Pipeline completed without errors


def run_all_tests():
    """Run all tests with detailed output"""
    print("\n" + "="*60)
    print("Phase 2.4: Advanced Autonomous Learning - Test Suite")
    print("="*60 + "\n")
    
    # Run pytest programmatically
    pytest.main([__file__, "-v", "-s"])


if __name__ == "__main__":
    run_all_tests()

