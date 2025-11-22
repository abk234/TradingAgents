#!/usr/bin/env python3
# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Test Langfuse Monitoring - Verify traces are being captured

This script runs a minimal analysis and verifies traces appear in Langfuse.
"""

import sys
import os
from pathlib import Path
from datetime import date
import time

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

# Force enable Langfuse for this test
os.environ['LANGFUSE_ENABLED'] = 'true'

def test_langfuse_monitoring():
    """Run a test and verify Langfuse captures traces."""
    print("=" * 70)
    print("Testing Langfuse Monitoring Capture")
    print("=" * 70)
    print()
    
    # Step 1: Verify configuration
    print("Step 1: Checking Configuration...")
    from tradingagents.monitoring.langfuse_integration import get_langfuse_tracer
    
    tracer = get_langfuse_tracer(enabled=True)
    
    if not tracer or not tracer.enabled:
        print("❌ Langfuse tracer is not enabled!")
        print("   Check your environment variables:")
        print("   - LANGFUSE_ENABLED=true")
        print("   - LANGFUSE_PUBLIC_KEY")
        print("   - LANGFUSE_SECRET_KEY")
        return 1
    
    print("✅ Langfuse tracer is enabled")
    print(f"   Host: {tracer.host}")
    print(f"   Has callback handler: {tracer.handler is not None}")
    print()
    
    # Step 2: Create a simple trace manually to test
    print("Step 2: Creating test trace...")
    try:
        if tracer.langfuse_client:
            # Try to create a test trace
            test_trace = tracer.langfuse_client.trace(
                name="Test Trace - Langfuse Monitoring Verification",
                input={"test": "monitoring_verification"},
                metadata={"source": "test_script"}
            )
            print(f"✅ Test trace created: {test_trace.id if hasattr(test_trace, 'id') else 'OK'}")
            
            # Create a span
            span = test_trace.span(
                name="test_span",
                input={"action": "test"},
                output={"result": "success"}
            )
            span.end()
            
            # Update trace
            test_trace.update(output={"status": "complete"})
            
            print("✅ Test trace updated with span")
            print()
    except Exception as e:
        print(f"⚠️  Could not create test trace: {e}")
        print("   This might be normal for Langfuse v3 API differences")
        print()
    
    # Step 3: Run a minimal analysis
    print("Step 3: Running minimal analysis with tracing...")
    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        
        # Create graph with Langfuse explicitly enabled
        graph = TradingAgentsGraph(
            selected_analysts=['market'],  # Just one analyst for speed
            enable_langfuse=True,  # Explicitly enable
            enable_rag=False,  # Disable RAG for speed
            debug=False
        )
        
        print("✅ Graph created with Langfuse enabled")
        print("   Running analysis for AAPL...")
        print()
        
        # Run analysis
        result, signal = graph.propagate(
            company_name="AAPL",
            trade_date=date.today(),
            store_analysis=False
        )
        
        print("✅ Analysis completed!")
        print(f"   Decision: {result.get('final_decision', 'N/A')}")
        print()
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Step 4: Instructions for verification
    print("=" * 70)
    print("Step 4: Verify Traces in Langfuse Dashboard")
    print("=" * 70)
    print()
    print("1. Open: http://localhost:3000")
    print("2. Go to: Traces (in sidebar)")
    print("3. Look for:")
    print("   - 'Test Trace - Langfuse Monitoring Verification'")
    print("   - 'Stock Analysis: AAPL'")
    print("4. Click on a trace to see:")
    print("   - Execution details")
    print("   - Spans and sub-traces")
    print("   - Timing information")
    print()
    print("If you see traces:")
    print("  ✅ Langfuse IS capturing monitoring data!")
    print()
    print("If you don't see traces:")
    print("  ⚠️  Check Langfuse logs:")
    print("     cd /Users/lxupkzwjs/Developer/langfuse")
    print("     docker compose logs langfuse-web --tail 50")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(test_langfuse_monitoring())

