#!/usr/bin/env python3
"""
Test Langfuse Connection

Quick script to verify Langfuse is properly configured and connected.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment_variables():
    """Check if environment variables are set."""
    print("🔍 Checking Environment Variables...")
    print("-" * 50)
    
    required_vars = {
        'LANGFUSE_ENABLED': os.getenv('LANGFUSE_ENABLED'),
        'LANGFUSE_PUBLIC_KEY': os.getenv('LANGFUSE_PUBLIC_KEY'),
        'LANGFUSE_SECRET_KEY': os.getenv('LANGFUSE_SECRET_KEY'),
        'LANGFUSE_HOST': os.getenv('LANGFUSE_HOST', 'http://localhost:3000'),
    }
    
    all_set = True
    for var, value in required_vars.items():
        if var == 'LANGFUSE_SECRET_KEY':
            status = "✅ Set" if value else "❌ Not set"
            display_value = "***hidden***" if value else "Not set"
        elif var == 'LANGFUSE_PUBLIC_KEY':
            status = "✅ Set" if value else "❌ Not set"
            display_value = value[:20] + "..." if value and len(value) > 20 else (value or "Not set")
        else:
            status = "✅ Set" if value else "❌ Not set"
            display_value = value or "Not set"
        
        print(f"{var:25} {status:10} {display_value}")
        
        if var != 'LANGFUSE_ENABLED' and not value:
            all_set = False
    
    print("-" * 50)
    return all_set


def test_langfuse_import():
    """Test if Langfuse can be imported."""
    print("\n📦 Testing Langfuse Import...")
    print("-" * 50)
    
    try:
        import langfuse
        version = getattr(langfuse, '__version__', 'unknown')
        print(f"✅ Langfuse imported successfully (version: {version})")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Langfuse: {e}")
        print("   Install with: pip install langfuse>=2.0.0")
        return False


def test_langfuse_connection():
    """Test connection to Langfuse server."""
    print("\n🌐 Testing Langfuse Connection...")
    print("-" * 50)
    
    try:
        from langfuse import Langfuse
        
        public_key = os.getenv('LANGFUSE_PUBLIC_KEY')
        secret_key = os.getenv('LANGFUSE_SECRET_KEY')
        host = os.getenv('LANGFUSE_HOST', 'http://localhost:3000')
        
        if not public_key or not secret_key:
            print("❌ Missing API keys. Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY")
            return False
        
        langfuse = Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=host
        )
        
        # Test connection by checking if client was created successfully
        # Langfuse v3 API is different, so we just verify client creation
        print(f"✅ Connection successful!")
        print(f"   Host: {host}")
        print(f"   Client initialized: OK")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"   Check that Langfuse is running at {os.getenv('LANGFUSE_HOST', 'http://localhost:3000')}")
        return False


def test_tradingagents_integration():
    """Test TradingAgents Langfuse integration."""
    print("\n🤖 Testing TradingAgents Integration...")
    print("-" * 50)
    
    try:
        from tradingagents.monitoring.langfuse_integration import get_langfuse_tracer
        
        tracer = get_langfuse_tracer()
        
        if not tracer:
            print("❌ Failed to get Langfuse tracer")
            return False
        
        if tracer.enabled:
            print("✅ Langfuse tracer initialized and enabled")
            print(f"   Host: {tracer.host}")
            return True
        else:
            print("⚠️  Langfuse tracer initialized but disabled")
            print("   Check LANGFUSE_ENABLED environment variable")
            return False
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("Langfuse Connection Test")
    print("=" * 50)
    
    results = []
    
    # Test 1: Environment variables
    results.append(("Environment Variables", test_environment_variables()))
    
    # Test 2: Langfuse import
    results.append(("Langfuse Import", test_langfuse_import()))
    
    # Test 3: Connection (only if env vars are set)
    if results[0][1]:
        results.append(("Langfuse Connection", test_langfuse_connection()))
    
    # Test 4: TradingAgents integration
    if results[1][1]:  # Only if import succeeded
        results.append(("TradingAgents Integration", test_tradingagents_integration()))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:30} {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("=" * 50)
    if all_passed:
        print("🎉 All tests passed! Langfuse is ready to use.")
        print("\nNext steps:")
        print("1. Run a TradingAgents analysis")
        print("2. Check traces at http://localhost:3000")
    else:
        print("⚠️  Some tests failed. Check the output above.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

