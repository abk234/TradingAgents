#!/usr/bin/env python3
"""
Test script for voice synthesis API endpoint.
Tests the /voice/synthesize endpoint to ensure it works correctly.
"""

import requests
import base64
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8005")

# Try to load API key from .env file
API_KEY = os.getenv("API_KEY", "")
if not API_KEY:
    try:
        env_file = os.path.join(os.path.dirname(__file__), ".env")
        if os.path.exists(env_file):
            with open(env_file, "r") as f:
                for line in f:
                    if line.startswith("API_KEY="):
                        API_KEY = line.split("=", 1)[1].strip()
                        break
    except Exception:
        pass

def test_voice_synthesize_base64():
    """Test voice synthesis with base64 return format."""
    print("Testing voice synthesis API (base64 format)...")
    
    url = f"{API_BASE_URL}/voice/synthesize"
    params = {
        "text": "Hello, this is a test of the voice synthesis API.",
        "tone": "professional",
        "return_base64": True
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    if API_KEY:
        headers["X-API-Key"] = API_KEY
    
    try:
        print(f"Making request to: {url}")
        print(f"Parameters: {params}")
        
        response = requests.post(url, params=params, headers=headers, timeout=30)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if "audio_base64" in data:
                audio_b64 = data["audio_base64"]
                print(f"✅ Success! Received base64 audio (length: {len(audio_b64)} chars)")
                
                # Verify it's valid base64
                try:
                    audio_bytes = base64.b64decode(audio_b64)
                    print(f"✅ Base64 decoded successfully (audio size: {len(audio_bytes)} bytes)")
                    
                    # Check for RIFF header (WAV file signature)
                    if audio_bytes[:4] == b"RIFF":
                        print("✅ Audio file has valid RIFF header (WAV format)")
                        
                        # Save to file for manual verification
                        output_file = "test_voice_output.wav"
                        with open(output_file, "wb") as f:
                            f.write(audio_bytes)
                        print(f"✅ Audio saved to: {output_file}")
                        print(f"   You can play it with: afplay {output_file} (macOS) or aplay {output_file} (Linux)")
                        
                        return True
                    else:
                        print(f"❌ ERROR: Audio file does not start with RIFF header!")
                        print(f"   First 20 bytes: {audio_bytes[:20]}")
                        return False
                except Exception as e:
                    print(f"❌ ERROR: Failed to decode base64: {e}")
                    return False
            else:
                print(f"❌ ERROR: Response missing 'audio_base64' field")
                print(f"   Response: {data}")
                return False
        else:
            print(f"❌ ERROR: Request failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ ERROR: Could not connect to {API_BASE_URL}")
        print("   Make sure the backend server is running!")
        return False
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_voice_synthesize_blob():
    """Test voice synthesis with blob return format."""
    print("\nTesting voice synthesis API (blob format)...")
    
    url = f"{API_BASE_URL}/voice/synthesize"
    params = {
        "text": "This is a blob format test.",
        "tone": "professional",
        "return_base64": False
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    if API_KEY:
        headers["X-API-Key"] = API_KEY
    
    try:
        response = requests.post(url, params=params, headers=headers, timeout=30)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            audio_bytes = response.content
            print(f"✅ Success! Received audio blob (size: {len(audio_bytes)} bytes)")
            
            # Check for RIFF header
            if audio_bytes[:4] == b"RIFF":
                print("✅ Audio file has valid RIFF header (WAV format)")
                return True
            else:
                print(f"❌ ERROR: Audio file does not start with RIFF header!")
                print(f"   First 20 bytes: {audio_bytes[:20]}")
                return False
        else:
            print(f"❌ ERROR: Request failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Voice Synthesis API Test")
    print("=" * 60)
    
    # Test base64 format (used by frontend)
    base64_success = test_voice_synthesize_base64()
    
    # Test blob format (alternative)
    blob_success = test_voice_synthesize_blob()
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Base64 format: {'✅ PASS' if base64_success else '❌ FAIL'}")
    print(f"Blob format:   {'✅ PASS' if blob_success else '❌ FAIL'}")
    
    if base64_success:
        print("\n✅ Voice API is working correctly!")
        sys.exit(0)
    else:
        print("\n❌ Voice API test failed!")
        sys.exit(1)

