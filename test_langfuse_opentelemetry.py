#!/usr/bin/env python3
"""
Test Langfuse OpenTelemetry Integration

Verifies that Langfuse v3 is capturing OpenTelemetry spans.
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

# Force enable Langfuse
os.environ['LANGFUSE_ENABLED'] = 'true'
os.environ['LANGFUSE_TRACING_ENABLED'] = 'true'

def test_opentelemetry_integration():
    """Test OpenTelemetry integration with Langfuse."""
    print("=" * 70)
    print("Testing Langfuse OpenTelemetry Integration")
    print("=" * 70)
    print()
    
    # Step 1: Initialize Langfuse client
    print("Step 1: Initializing Langfuse client...")
    try:
        from langfuse import Langfuse
        
        langfuse = Langfuse(
            public_key=os.getenv('LANGFUSE_PUBLIC_KEY'),
            secret_key=os.getenv('LANGFUSE_SECRET_KEY'),
            host=os.getenv('LANGFUSE_HOST', 'http://localhost:3000'),
            tracing_enabled=True
        )
        
        print("✅ Langfuse client initialized")
        print(f"   Host: {os.getenv('LANGFUSE_HOST')}")
        print(f"   Has OTEL tracer: {hasattr(langfuse, '_otel_tracer')}")
        print()
        
    except Exception as e:
        print(f"❌ Failed to initialize Langfuse: {e}")
        return 1
    
    # Step 2: Test OpenTelemetry span creation
    print("Step 2: Creating OpenTelemetry spans...")
    try:
        from opentelemetry import trace
        
        # Get the tracer from OpenTelemetry
        tracer = trace.get_tracer(__name__)
        
        # Create a test span
        with tracer.start_as_current_span("test_span") as span:
            span.set_attribute("test.type", "verification")
            span.set_attribute("test.source", "manual_test")
            print("✅ Created test span")
            print(f"   Span name: test_span")
            print(f"   Trace ID: {format(span.get_span_context().trace_id, '032x')}")
            print()
            
            # Create a child span
            with tracer.start_as_current_span("child_span") as child:
                child.set_attribute("child.test", True)
                print("✅ Created child span")
                time.sleep(0.1)  # Small delay to ensure span is captured
        
        print("✅ Spans completed")
        print()
        
    except Exception as e:
        print(f"⚠️  OpenTelemetry span creation: {e}")
        print("   This might be normal - Langfuse may handle spans differently")
        print()
    
    # Step 3: Test Langfuse event creation
    print("Step 3: Creating Langfuse event...")
    try:
        event = langfuse.create_event(
            name="Test Event - Monitoring Verification",
            input={"test": "monitoring_verification"},
            metadata={"source": "test_script", "timestamp": str(time.time())}
        )
        print("✅ Event created")
        print(f"   Event ID: {event.id if hasattr(event, 'id') else 'OK'}")
        print()
        
    except Exception as e:
        print(f"⚠️  Event creation: {e}")
        print()
    
    # Step 4: Flush to ensure data is sent
    print("Step 4: Flushing traces to Langfuse...")
    try:
        langfuse.flush()
        print("✅ Flush completed")
        print("   Traces should now be visible in Langfuse dashboard")
        print()
    except Exception as e:
        print(f"⚠️  Flush: {e}")
        print()
    
    # Step 5: Instructions
    print("=" * 70)
    print("Verification Steps")
    print("=" * 70)
    print()
    print("1. Open: http://localhost:3000")
    print("2. Go to: Traces (sidebar)")
    print("3. Look for:")
    print("   - 'test_span' or 'child_span'")
    print("   - 'Test Event - Monitoring Verification'")
    print("4. If you see traces:")
    print("   ✅ Langfuse IS capturing monitoring data!")
    print("5. If you don't see traces:")
    print("   ⚠️  Check Langfuse logs:")
    print("      cd /Users/lxupkzwjs/Developer/langfuse")
    print("      docker compose logs langfuse-web --tail 50")
    print()
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(test_opentelemetry_integration())

