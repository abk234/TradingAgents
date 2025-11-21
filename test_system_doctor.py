#!/usr/bin/env python3
"""
Test System Doctor with Real Data

Tests Eddie v2.0's System Doctor functionality with actual stock data.
"""

import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_system_doctor():
    """Test System Doctor with real stock data."""
    
    print("=" * 80)
    print("🏥 Testing Eddie v2.0 System Doctor")
    print("=" * 80)
    print()
    
    try:
        from tradingagents.validation import SystemDoctor
        from tradingagents.database import get_db_connection, TickerOperations, ScanOperations
        import pandas as pd
        import yfinance as yf
        
        # Initialize System Doctor
        doctor = SystemDoctor()
        print("✅ System Doctor initialized")
        print()
        
        # Get database connection
        db = get_db_connection()
        ticker_ops = TickerOperations(db)
        scan_ops = ScanOperations(db)
        print("✅ Database connection established")
        print()
        
        # Get a test ticker (try common ones)
        test_tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]
        ticker = None
        ticker_id = None
        
        for test_ticker in test_tickers:
            ticker_id = ticker_ops.get_ticker_id(test_ticker)
            if ticker_id:
                ticker = test_ticker
                break
        
        if not ticker:
            print("❌ No test ticker found in database")
            print("   Please run screener first to populate database")
            return False
        
        print(f"📊 Testing with ticker: {ticker}")
        print()
        
        # Get latest scan date
        latest_scan_date = scan_ops.get_latest_scan_date()
        if not latest_scan_date:
            print(f"❌ No scan data found in database")
            print("   Please run screener first")
            return False
        
        print(f"✅ Latest scan date: {latest_scan_date}")
        
        # Get latest scan data for this ticker
        latest_scan = scan_ops.get_latest_scan(ticker_id=ticker_id, scan_date=latest_scan_date)
        if not latest_scan:
            print(f"❌ No scan data found for {ticker} on {latest_scan_date}")
            print("   Please run screener first")
            return False
        
        local_price = float(latest_scan.get('price', 0))
        if local_price == 0:
            print(f"❌ Invalid price data for {ticker}")
            print(f"   Available fields: {list(latest_scan.keys())}")
            return False
        
        print(f"✅ Found scan data:")
        print(f"   Local Price: ${local_price:.2f}")
        print(f"   Scan Date: {latest_scan.get('scan_date')}")
        print()
        
        # Get indicator values
        technical_signals = latest_scan.get('technical_signals', {})
        application_indicators = {}
        if isinstance(technical_signals, dict):
            if 'rsi' in technical_signals:
                application_indicators['RSI'] = float(technical_signals['rsi'])
                print(f"✅ Found RSI: {application_indicators['RSI']:.2f}")
            if 'macd' in technical_signals:
                application_indicators['MACD'] = float(technical_signals['macd'])
                print(f"✅ Found MACD: {application_indicators['MACD']:.4f}")
        
        if not application_indicators:
            print("⚠️  No indicator data found in scan (will test data sanity only)")
        print()
        
        # Fetch price history for indicator audit
        print("📈 Fetching price history for indicator audit...")
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="3mo")
            if not hist.empty:
                price_history = hist['Close']
                print(f"✅ Fetched {len(price_history)} days of price data")
                print(f"   Date range: {hist.index[0].date()} to {hist.index[-1].date()}")
            else:
                print("⚠️  No price history available")
                price_history = None
        except Exception as e:
            print(f"⚠️  Could not fetch price history: {e}")
            price_history = None
        print()
        
        # Perform health check
        print("🔬 Running System Doctor health check...")
        print("-" * 80)
        
        report = doctor.perform_health_check(
            ticker=ticker,
            local_price=local_price,
            application_indicators=application_indicators if application_indicators else None,
            price_history=price_history,
            external_price=None  # Will fetch automatically
        )
        
        # Display report
        print(report.format_for_display())
        print()
        print("-" * 80)
        
        # Test individual components
        print("\n🧪 Testing Individual Components:")
        print()
        
        # Test 1: Data Sanity Check
        print("1️⃣  Testing Data Sanity Check...")
        sanity_check = doctor.check_data_sanity(ticker, local_price)
        if sanity_check.passed:
            print(f"   ✅ PASSED: Prices aligned ({sanity_check.price_discrepancy_percent:.3f}% discrepancy)")
        else:
            print(f"   ⚠️  WARNING: {sanity_check.warning}")
        print()
        
        # Test 2: Indicator Audit (if we have data)
        if application_indicators and price_history is not None:
            print("2️⃣  Testing Indicator Audit...")
            
            if 'RSI' in application_indicators:
                print(f"   Testing RSI audit...")
                rsi_audit = doctor.audit_indicator(
                    "RSI",
                    application_indicators['RSI'],
                    price_history,
                    period=14
                )
                if rsi_audit.passed:
                    print(f"   ✅ RSI PASSED: {rsi_audit.discrepancy_percent:.2f}% discrepancy")
                else:
                    print(f"   ⚠️  RSI WARNING: {rsi_audit.warning}")
            
            if 'MACD' in application_indicators:
                print(f"   Testing MACD audit...")
                macd_audit = doctor.audit_indicator(
                    "MACD",
                    application_indicators['MACD'],
                    price_history
                )
                if macd_audit.passed:
                    print(f"   ✅ MACD PASSED: {macd_audit.discrepancy_percent:.2f}% discrepancy")
                else:
                    print(f"   ⚠️  MACD WARNING: {macd_audit.warning}")
        else:
            print("   ⏭️  Skipped (no indicator data or price history)")
        print()
        
        # Test 3: Independent Calculations
        if price_history is not None:
            print("3️⃣  Testing Independent Calculations...")
            try:
                independent_rsi = doctor.calculate_rsi_independent(price_history, period=14)
                print(f"   ✅ Independent RSI: {independent_rsi:.2f}")
                
                independent_macd = doctor.calculate_macd_independent(price_history)
                print(f"   ✅ Independent MACD: {independent_macd['macd']:.4f}")
                print(f"   ✅ Independent Signal: {independent_macd['signal']:.4f}")
                print(f"   ✅ Independent Histogram: {independent_macd['histogram']:.4f}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        print()
        
        # Summary
        print("=" * 80)
        print("📋 Test Summary:")
        print(f"   Ticker: {ticker}")
        print(f"   Overall Health: {report.overall_health}")
        print(f"   Data Sanity: {'✅ PASSED' if report.data_sanity_check.passed else '⚠️  FAILED'}")
        print(f"   Indicator Audits: {len([a for a in report.indicator_audits if a.passed])}/{len(report.indicator_audits)} passed")
        print("=" * 80)
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("   Make sure you're in the correct environment")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_system_doctor()
    sys.exit(0 if success else 1)

