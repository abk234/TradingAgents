#!/usr/bin/env python3
"""
Quick verification script to test audio format from API.
"""

import requests
import base64
import sys
import os

API_BASE_URL = "http://localhost:8005"

# Get API key
api_key = ""
try:
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("API_KEY="):
                api_key = line.split("=", 1)[1].strip()
                break
except:
    pass

if not api_key:
    print("❌ API_KEY not found in .env")
    sys.exit(1)

url = f"{API_BASE_URL}/voice/synthesize"
params = {
    "text": "This is a test",
    "tone": "professional",
    "return_base64": True
}

headers = {
    "Content-Type": "application/json",
    "X-API-Key": api_key
}

try:
    print("Testing voice synthesis API...")
    response = requests.post(url, params=params, headers=headers, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        if "audio_base64" in data:
            audio_b64 = data["audio_base64"]
            audio_bytes = base64.b64decode(audio_b64)
            
            print(f"✅ Response received")
            print(f"   Audio size: {len(audio_bytes)} bytes")
            print(f"   First 20 bytes: {audio_bytes[:20]}")
            
            # Check RIFF header
            if len(audio_bytes) >= 4:
                header = audio_bytes[:4]
                header_str = header.decode('latin-1', errors='ignore')
                print(f"   Header (as string): {repr(header_str)}")
                print(f"   Header (as bytes): {header.hex()}")
                
                if header == b"RIFF":
                    print("✅ Valid RIFF header found!")
                    sys.exit(0)
                else:
                    print(f"❌ Invalid header! Expected 'RIFF', got: {header_str}")
                    sys.exit(1)
            else:
                print("❌ Audio file too short")
                sys.exit(1)
        else:
            print("❌ No audio_base64 in response")
            print(f"   Response: {data}")
            sys.exit(1)
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(f"   Response: {response.text}")
        sys.exit(1)
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to backend. Is it running?")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

