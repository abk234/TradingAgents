import requests
import json
import time

BASE_URL = "http://localhost:8005"

def test_system_status():
    print("\n--- Testing System Status ---")
    try:
        response = requests.get(f"{BASE_URL}/system/status")
        if response.status_code == 200:
            data = response.json()
            print("✅ System Status OK")
            print(f"   Status: {data.get('status')}")
            print(f"   Database: {data.get('services', {}).get('database')}")
            print(f"   Tickers: {data.get('stats', {}).get('tickers', {}).get('total')}")
        else:
            print(f"❌ Failed to get system status: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error: {e}")

def test_ticker_operations():
    print("\n--- Testing Ticker Operations ---")
    test_symbol = "TEST"
    
    # 1. Add Ticker
    print(f"Adding ticker {test_symbol}...")
    try:
        payload = {
            "symbol": test_symbol,
            "company_name": "Test Company Inc.",
            "sector": "Technology",
            "priority_tier": 3,
            "tags": ["test", "verification"]
        }
        response = requests.post(f"{BASE_URL}/data/tickers", json=payload)
        if response.status_code == 200:
            print("✅ Ticker added successfully")
        else:
            print(f"❌ Failed to add ticker: {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"❌ Error adding ticker: {e}")
        return

    # 2. Get Tickers
    print("Fetching tickers...")
    try:
        response = requests.get(f"{BASE_URL}/data/tickers?active_only=false")
        if response.status_code == 200:
            tickers = response.json()
            found = any(t['symbol'] == test_symbol for t in tickers)
            if found:
                print(f"✅ Ticker {test_symbol} found in list")
            else:
                print(f"❌ Ticker {test_symbol} NOT found in list")
        else:
            print(f"❌ Failed to fetch tickers: {response.status_code}")
    except Exception as e:
        print(f"❌ Error fetching tickers: {e}")

    # 3. Update Ticker
    print(f"Updating ticker {test_symbol}...")
    try:
        payload = {
            "company_name": "Updated Test Company",
            "notes": "Updated via verification script"
        }
        response = requests.put(f"{BASE_URL}/data/tickers/{test_symbol}", json=payload)
        if response.status_code == 200:
            print("✅ Ticker updated successfully")
        else:
            print(f"❌ Failed to update ticker: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error updating ticker: {e}")

    # 4. Delete Ticker
    print(f"Removing ticker {test_symbol}...")
    try:
        response = requests.delete(f"{BASE_URL}/data/tickers/{test_symbol}?soft_delete=false")
        if response.status_code == 200:
            print("✅ Ticker removed successfully")
        else:
            print(f"❌ Failed to remove ticker: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error removing ticker: {e}")

def test_refresh_endpoint():
    print("\n--- Testing Refresh Endpoint ---")
    try:
        response = requests.post(f"{BASE_URL}/data/refresh/scan")
        if response.status_code == 200:
            print("✅ Scan refresh triggered successfully")
        else:
            print(f"❌ Failed to trigger refresh: {response.status_code}")
    except Exception as e:
        print(f"❌ Error triggering refresh: {e}")

if __name__ == "__main__":
    print("Starting Verification...")
    # Wait a bit to ensure server might be up if we just restarted it (though we didn't)
    test_system_status()
    test_ticker_operations()
    test_refresh_endpoint()
    print("\nVerification Complete.")
