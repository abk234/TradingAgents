#!/usr/bin/env python3
"""
Test Langfuse Tracing with TradingAgents

Runs a quick stock analysis and verifies traces appear in Langfuse.
"""

import sys
from pathlib import Path
from datetime import date
import logging

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_analysis_with_tracing():
    """Run a test analysis with Langfuse tracing enabled."""
    print("=" * 70)
    print("Testing Langfuse Tracing with TradingAgents")
    print("=" * 70)
    print()
    
    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.monitoring.langfuse_integration import get_langfuse_tracer
        
        # Check Langfuse tracer status
        tracer = get_langfuse_tracer()
        if tracer and tracer.enabled:
            print("✅ Langfuse tracer is ENABLED")
            print(f"   Host: {tracer.host}")
            print(f"   Has handler: {tracer.handler is not None}")
        else:
            print("⚠️  Langfuse tracer is DISABLED")
            print("   Check your environment variables")
            return 1
        
        print()
        print("📊 Creating TradingAgents graph...")
        
        # Create graph with Langfuse enabled
        graph = TradingAgentsGraph(
            selected_analysts=['market', 'news'],  # Use 2 analysts for faster test
            enable_langfuse=True,
            enable_rag=False,  # Disable RAG for faster test
            debug=False
        )
        
        print("✅ Graph created")
        print()
        print("🚀 Running analysis for AAPL...")
        print("   This will trace all agent executions to Langfuse")
        print()
        
        # Run analysis
        result, signal = graph.propagate(
            company_name="AAPL",
            trade_date=date.today(),
            store_analysis=False
        )
        
        print()
        print("=" * 70)
        print("✅ Analysis Complete!")
        print("=" * 70)
        print()
        print("📊 Results:")
        print(f"   Final Decision: {result.get('final_decision', 'N/A')}")
        print(f"   Confidence: {result.get('confidence_score', 'N/A')}")
        print()
        print("🔍 Check Langfuse Dashboard:")
        print("   1. Open: http://localhost:3000")
        print("   2. Go to: Traces (in sidebar)")
        print("   3. Look for: 'Stock Analysis: AAPL'")
        print("   4. Click on it to see:")
        print("      - All agent executions")
        print("      - Execution times")
        print("      - LLM calls (if captured)")
        print("      - Full trace details")
        print()
        print("=" * 70)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(test_analysis_with_tracing())

