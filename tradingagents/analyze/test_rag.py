"""
RAG System Test Script

Tests the complete RAG integration including:
- Embedding generation
- Database connectivity
- Context retrieval
- Analysis initialization
"""

import logging
from datetime import date

from tradingagents.database import get_db_connection, TickerOperations
from tradingagents.rag import EmbeddingGenerator, ContextRetriever, PromptFormatter
from tradingagents.decision import FourGateFramework

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_embedding_generation():
    """Test embedding generation with Ollama."""
    print("\n" + "="*70)
    print("TEST 1: Embedding Generation")
    print("="*70)

    try:
        generator = EmbeddingGenerator()

        # Test simple embedding
        text = "Apple Inc. is showing strong technical indicators with RSI at 45 and MACD bullish crossover"
        embedding = generator.generate(text)

        if embedding and len(embedding) == 768:
            print(f"✓ Generated {len(embedding)}-dimensional embedding")
            print(f"  Sample values: {embedding[:5]}")
            return True
        else:
            print(f"✗ Invalid embedding: {len(embedding) if embedding else 0} dimensions")
            return False

    except Exception as e:
        print(f"✗ Embedding generation failed: {e}")
        return False


def test_database_connectivity():
    """Test database connection and ticker operations."""
    print("\n" + "="*70)
    print("TEST 2: Database Connectivity")
    print("="*70)

    try:
        db = get_db_connection()
        ticker_ops = TickerOperations(db)

        # Get all tickers
        tickers = ticker_ops.get_all_tickers()

        if tickers:
            print(f"✓ Connected to database")
            print(f"  Found {len(tickers)} tickers in watchlist:")
            for ticker in tickers[:5]:  # Show first 5
                print(f"    - {ticker['symbol']:6s} ({ticker['sector']})")
            if len(tickers) > 5:
                print(f"    ... and {len(tickers) - 5} more")

            return True
        else:
            print("✗ No tickers found in database")
            return False

    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False


def test_context_retrieval():
    """Test historical context retrieval."""
    print("\n" + "="*70)
    print("TEST 3: Context Retrieval")
    print("="*70)

    try:
        db = get_db_connection()
        ticker_ops = TickerOperations(db)
        context_retriever = ContextRetriever(db)
        embedding_gen = EmbeddingGenerator()

        # Get a ticker
        tickers = ticker_ops.get_all_tickers()
        if not tickers:
            print("✗ No tickers available for testing")
            return False

        test_ticker = tickers[0]
        ticker_id = test_ticker['ticker_id']
        symbol = test_ticker['symbol']

        print(f"Testing with ticker: {symbol}")

        # Generate embedding for test query
        query_text = f"Analyzing {symbol} for investment opportunity"
        query_embedding = embedding_gen.generate(query_text)

        if not query_embedding:
            print("✗ Failed to generate query embedding")
            return False

        # Retrieve ticker history
        history = context_retriever.get_ticker_history(ticker_id, limit=5)
        print(f"✓ Retrieved {len(history)} historical analyses")

        # Get sector context
        sector = test_ticker.get('sector')
        if sector:
            sector_ctx = context_retriever.get_sector_context(sector, days_back=30)
            print(f"✓ Sector context: {sector_ctx['total_analyses']} analyses in {sector}")

        # Build full context
        context = context_retriever.build_historical_context(
            ticker_id=ticker_id,
            current_situation_embedding=query_embedding,
            symbol=symbol
        )

        print(f"✓ Built historical context with {len(context)} components")

        return True

    except Exception as e:
        print(f"✗ Context retrieval failed: {e}")
        return False


def test_prompt_formatting():
    """Test prompt formatting."""
    print("\n" + "="*70)
    print("TEST 4: Prompt Formatting")
    print("="*70)

    try:
        formatter = PromptFormatter()

        # Create mock context
        mock_context = {
            'symbol': 'AAPL',
            'ticker_history': [
                {
                    'analysis_date': date.today(),
                    'final_decision': 'BUY',
                    'confidence_score': 85,
                    'price_at_analysis': 175.50
                }
            ],
            'last_analysis': {
                'date': date.today(),
                'decision': 'BUY',
                'confidence': 85,
                'price': 175.50
            },
            'similar_situations': [],
            'sector_context': {
                'sector': 'Technology',
                'total_analyses': 10,
                'buy_signals': 6,
                'buy_signal_rate': 0.6,
                'average_confidence': 78.5,
                'recent_analyses': []
            }
        }

        # Format context
        formatted = formatter.format_analysis_context(mock_context)

        if formatted and len(formatted) > 100:
            print(f"✓ Formatted context ({len(formatted)} chars)")
            print("\nSample output:")
            print("-" * 70)
            print(formatted[:500] + "...")
            return True
        else:
            print("✗ Formatting produced insufficient output")
            return False

    except Exception as e:
        print(f"✗ Prompt formatting failed: {e}")
        return False


def test_four_gate_framework():
    """Test four-gate decision framework."""
    print("\n" + "="*70)
    print("TEST 5: Four-Gate Framework")
    print("="*70)

    try:
        framework = FourGateFramework()

        # Mock data for testing
        mock_fundamentals = {
            'pe_ratio': 25.5,
            'forward_pe': 22.0,
            'peg_ratio': 1.8,
            'debt_to_equity': 1.2
        }

        mock_signals = {
            'rsi': 45,
            'macd_bullish_crossover': True,
            'price_above_ma20': True,
            'volume_ratio': 1.5
        }

        mock_risk = {
            'volatility': 25.0,
            'max_drawdown': -15.0,
            'sharpe_ratio': 1.2
        }

        # Mock price data for technical gate
        mock_price_data = {
            'current_price': 175.50,
            'ma20': 170.00,
            'ma50': 165.00,
            'support_level': 160.00,
            'resistance_level': 180.00
        }

        # Evaluate gates
        gate1 = framework.evaluate_fundamental_gate(mock_fundamentals)
        gate2 = framework.evaluate_technical_gate(mock_signals, mock_price_data)
        gate3 = framework.evaluate_risk_gate(mock_risk, position_size_pct=5.0)

        print(f"✓ Gate 1 (Fundamental): {'PASS' if gate1.passed else 'FAIL'} (Score: {gate1.score}/100)")
        print(f"✓ Gate 2 (Technical): {'PASS' if gate2.passed else 'FAIL'} (Score: {gate2.score}/100)")
        print(f"✓ Gate 3 (Risk): {'PASS' if gate3.passed else 'FAIL'} (Score: {gate3.score}/100)")

        return True

    except Exception as e:
        print(f"✗ Four-gate framework failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("RAG SYSTEM COMPREHENSIVE TEST")
    print("="*70)

    results = {
        'Embedding Generation': test_embedding_generation(),
        'Database Connectivity': test_database_connectivity(),
        'Context Retrieval': test_context_retrieval(),
        'Prompt Formatting': test_prompt_formatting(),
        'Four-Gate Framework': test_four_gate_framework()
    }

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8s} {test_name}")

    print()
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! RAG system is ready.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review errors above.")
        return 1


if __name__ == '__main__':
    exit(main())
