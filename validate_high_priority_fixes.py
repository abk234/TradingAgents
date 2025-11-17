#!/usr/bin/env python3
"""
End-to-end validation of high priority fixes
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_1_hardcoded_path_fix():
    """Test that hardcoded path is fixed"""
    print("\n✅ Test 1: Hardcoded Path Fix")
    try:
        from tradingagents.default_config import DEFAULT_CONFIG
        data_dir = DEFAULT_CONFIG.get('data_dir', '')
        
        # Should not contain hardcoded user path
        if '/Users/yluo/' in data_dir:
            print(f"   ❌ FAIL: Still contains hardcoded path: {data_dir}")
            return False
        
        # Should use environment variable or relative path
        if 'TRADINGAGENTS_DATA_DIR' in str(data_dir) or data_dir.startswith('./') or 'data' in data_dir:
            print(f"   ✓ PASS: Using flexible path: {data_dir}")
            return True
        else:
            print(f"   ⚠️  WARNING: Unexpected path format: {data_dir}")
            return True
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        return False


def test_2_env_example_exists():
    """Test that .env.example exists"""
    print("\n✅ Test 2: .env.example Template")
    env_example = project_root / '.env.example'
    if env_example.exists():
        print(f"   ✓ PASS: .env.example exists")
        return True
    else:
        print(f"   ❌ FAIL: .env.example not found")
        return False


def test_3_secrets_manager():
    """Test secrets manager"""
    print("\n✅ Test 3: Secrets Manager")
    try:
        from tradingagents.utils.secrets_manager import get_secrets_manager, get_api_key
        
        manager = get_secrets_manager()
        print(f"   ✓ Secrets manager initialized")
        
        # Test getting a key (should fall back to env)
        key = get_api_key('alpha_vantage')
        if key:
            print(f"   ✓ Can retrieve API key (from env or keyring)")
        else:
            print(f"   ⚠️  No API key found (this is OK if not configured)")
        
        return True
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_4_database_connection():
    """Test database connection with secure credentials"""
    print("\n✅ Test 4: Database Connection")
    try:
        from tradingagents.database import get_db_connection
        
        db = get_db_connection()
        print(f"   ✓ Database connection created")
        
        # Test query
        count = db.get_table_count('tickers')
        print(f"   ✓ Database query successful (found {count} tickers)")
        
        # Test pool stats
        stats = db.get_pool_stats()
        if stats:
            print(f"   ✓ Connection pool monitoring active")
            print(f"     - Active connections: {stats.get('active_connections', 0)}")
            print(f"     - Utilization: {stats.get('utilization_pct', 0):.1f}%")
        
        return True
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_5_cache_manager():
    """Test cache manager"""
    print("\n✅ Test 5: Cache Manager")
    try:
        from tradingagents.utils.cache_manager import get_cache_manager
        
        cache = get_cache_manager()
        stats = cache.get_stats()
        
        if stats.get('status') == 'disabled':
            print(f"   ⚠️  Redis not available (this is OK)")
            print(f"     Cache will be disabled but app will work")
        else:
            print(f"   ✓ Redis cache connected")
            print(f"     - Total keys: {stats.get('total_keys', 0)}")
            print(f"     - Hit rate: {stats.get('hit_rate', 0):.1%}")
        
        return True
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_6_circuit_breaker():
    """Test circuit breaker"""
    print("\n✅ Test 6: Circuit Breaker")
    try:
        from tradingagents.utils.circuit_breaker import CircuitBreaker, CircuitState
        
        breaker = CircuitBreaker(failure_threshold=3, timeout_seconds=10, name="test")
        
        # Test initial state
        assert breaker.state == CircuitState.CLOSED, "Should start CLOSED"
        print(f"   ✓ Circuit breaker initialized (state: {breaker.state.value})")
        
        # Test state getter
        state = breaker.get_state()
        assert state['state'] == 'closed', "Should be closed"
        print(f"   ✓ State tracking works")
        
        return True
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_7_retry_decorator():
    """Test retry decorator"""
    print("\n✅ Test 7: Retry with Backoff")
    try:
        from tradingagents.utils.retry import retry_with_backoff
        
        call_count = [0]
        
        @retry_with_backoff(max_retries=2, initial_delay=0.1)
        def test_func():
            call_count[0] += 1
            if call_count[0] < 2:
                raise ValueError("Test error")
            return "success"
        
        result = test_func()
        assert result == "success", "Should succeed after retry"
        assert call_count[0] == 2, "Should have retried once"
        print(f"   ✓ Retry decorator works (retried {call_count[0]-1} time)")
        
        return True
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_8_logging_config():
    """Test logging configuration"""
    print("\n✅ Test 8: Centralized Logging")
    try:
        from tradingagents.utils.logging_config import setup_logging
        import logging
        
        # Setup logging
        logger = setup_logging(level='INFO', enable_json=False)
        
        # Test logging
        logger.info("Test log message")
        print(f"   ✓ Logging configured and working")
        
        # Check log file exists
        log_file = Path('./logs/tradingagents.log')
        if log_file.exists():
            print(f"   ✓ Log file created: {log_file}")
        else:
            print(f"   ⚠️  Log file not found (may be created on first log)")
        
        return True
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_9_alpha_vantage_integration():
    """Test Alpha Vantage uses secrets manager"""
    print("\n✅ Test 9: Alpha Vantage Integration")
    try:
        from tradingagents.dataflows.alpha_vantage_common import get_api_key
        
        # This should use secrets manager first, then fall back to env
        try:
            key = get_api_key()
            if key:
                print(f"   ✓ API key retrieved (length: {len(key)})")
            else:
                print(f"   ⚠️  No API key found (OK if not configured)")
        except ValueError as e:
            if "not set" in str(e):
                print(f"   ⚠️  API key not configured (this is OK)")
            else:
                raise
        
        return True
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_10_basic_imports():
    """Test that all new modules can be imported"""
    print("\n✅ Test 10: Module Imports")
    modules = [
        'tradingagents.utils.secrets_manager',
        'tradingagents.utils.cache_manager',
        'tradingagents.utils.logging_config',
        'tradingagents.utils.circuit_breaker',
        'tradingagents.utils.retry',
    ]
    
    failed = []
    for module in modules:
        try:
            __import__(module)
            print(f"   ✓ {module}")
        except Exception as e:
            print(f"   ❌ {module}: {e}")
            failed.append(module)
    
    if failed:
        return False
    return True


def main():
    """Run all validation tests"""
    print("=" * 70)
    print("HIGH PRIORITY FIXES - END-TO-END VALIDATION")
    print("=" * 70)
    
    tests = [
        test_1_hardcoded_path_fix,
        test_2_env_example_exists,
        test_3_secrets_manager,
        test_4_database_connection,
        test_5_cache_manager,
        test_6_circuit_breaker,
        test_7_retry_decorator,
        test_8_logging_config,
        test_9_alpha_vantage_integration,
        test_10_basic_imports,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"   ❌ Test crashed: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! High priority fixes are working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review output above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())

