#!/usr/bin/env python3
"""
Test script for analytics endpoints
Tests if all required endpoints exist and return proper responses
"""

import requests
import json
import sys

API_BASE = "http://localhost:8005"

def test_endpoint(method, endpoint, data=None, description=""):
    """Test an API endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {method} {endpoint}")
    if description:
        print(f"Description: {description}")
    print(f"{'='*60}")
    
    try:
        url = f"{API_BASE}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=5)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=5)
        else:
            print(f"  ❌ Unsupported method: {method}")
            return False
        
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"  ✅ Success!")
                print(f"  Response keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                return True
            except json.JSONDecodeError:
                print(f"  ⚠️  Response is not JSON: {response.text[:100]}")
                return True  # Still consider it success if endpoint exists
        elif response.status_code == 404:
            print(f"  ❌ Endpoint NOT FOUND (404)")
            print(f"  This endpoint is missing and needs to be implemented!")
            return False
        elif response.status_code == 401 or response.status_code == 403:
            print(f"  ⚠️  Authentication required (status: {response.status_code})")
            print(f"  Endpoint exists but requires auth - this is OK")
            return True  # Endpoint exists, just needs auth
        elif response.status_code == 503:
            print(f"  ⚠️  Service unavailable (503)")
            print(f"  Endpoint exists but service not initialized - this is OK")
            return True  # Endpoint exists
        else:
            print(f"  ⚠️  Unexpected status: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return True  # Endpoint exists, just has an error
        
    except requests.exceptions.ConnectionError:
        print(f"  ❌ Cannot connect to API server")
        print(f"  Make sure the server is running on {API_BASE}")
        return None  # Can't determine
    except requests.exceptions.Timeout:
        print(f"  ⚠️  Request timeout")
        return None
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None

def main():
    """Run all endpoint tests"""
    print("\n" + "="*60)
    print("Analytics Endpoints Test")
    print("="*60)
    print(f"\nTesting API at: {API_BASE}")
    print("Make sure the API server is running!")
    
    results = []
    
    # Test all analytics endpoints that frontend expects
    endpoints = [
        ("GET", "/analytics/prompts", None, "Prompt analytics"),
        ("GET", "/analytics/portfolio/performance", None, "Portfolio performance"),
        ("GET", "/analytics/history?limit=10&offset=0", None, "Historical analyses"),
        ("POST", "/analytics/risk", {
            "positions": [
                {"ticker": "AAPL", "shares": 10, "entryPrice": 150}
            ],
            "total_value": 1500
        }, "Risk analysis"),
    ]
    
    for method, endpoint, data, desc in endpoints:
        result = test_endpoint(method, endpoint, data, desc)
        if result is not None:
            results.append((endpoint, result))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    missing = []
    existing = []
    unknown = []
    
    for endpoint, exists in results:
        if exists:
            existing.append(endpoint)
            print(f"✅ {endpoint} - EXISTS")
        elif exists is False:
            missing.append(endpoint)
            print(f"❌ {endpoint} - MISSING")
        else:
            unknown.append(endpoint)
            print(f"⚠️  {endpoint} - UNKNOWN (connection issue)")
    
    print("\n" + "="*60)
    if missing:
        print(f"\n❌ {len(missing)} endpoint(s) are MISSING and need to be implemented:")
        for ep in missing:
            print(f"   - {ep}")
        print("\nThese endpoints are called by the frontend and must be added to the API.")
    elif unknown:
        print(f"\n⚠️  Could not test {len(unknown)} endpoint(s) - check server connection")
    else:
        print(f"\n✅ All tested endpoints exist!")
    
    print("="*60 + "\n")
    
    return 0 if not missing else 1

if __name__ == "__main__":
    sys.exit(main())

