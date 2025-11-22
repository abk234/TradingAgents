#!/usr/bin/env python3
"""
Integration Test Suite for TradingAgents
Tests frontend-backend-middleware integration
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional
import requests
import websocket
from urllib.parse import urljoin

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8005")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3005")
API_KEY = os.getenv("API_KEY", "")

# Colors for output
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
NC = '\033[0m'  # No Color

class IntegrationTester:
    def __init__(self):
        self.results = {
            "passed": [],
            "failed": [],
            "warnings": []
        }
        self.start_time = time.time()
        
    def print_header(self, text: str):
        print(f"\n{CYAN}{'='*60}{NC}")
        print(f"{CYAN}{text:^60}{NC}")
        print(f"{CYAN}{'='*60}{NC}\n")
        
    def print_test(self, name: str, status: str = "RUNNING"):
        if status == "PASS":
            print(f"{GREEN}✓{NC} {name}")
        elif status == "FAIL":
            print(f"{RED}✗{NC} {name}")
        elif status == "WARN":
            print(f"{YELLOW}⚠{NC} {name}")
        else:
            print(f"{BLUE}→{NC} {name}")
            
    def test_backend_health(self) -> bool:
        """Test backend health endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.print_test("Backend Health Check", "PASS")
                self.results["passed"].append("Backend Health Check")
                print(f"   Status: {data.get('status')}")
                print(f"   Agent Initialized: {data.get('agent_initialized')}")
                return True
            else:
                self.print_test("Backend Health Check", "FAIL")
                self.results["failed"].append(f"Backend Health Check: Status {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Backend Health Check", "FAIL")
            self.results["failed"].append(f"Backend Health Check: {str(e)}")
            return False
            
    def test_backend_root(self) -> bool:
        """Test backend root endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/", timeout=5)
            if response.status_code == 200:
                self.print_test("Backend Root Endpoint", "PASS")
                self.results["passed"].append("Backend Root Endpoint")
                return True
            else:
                self.print_test("Backend Root Endpoint", "FAIL")
                self.results["failed"].append(f"Backend Root: Status {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Backend Root Endpoint", "FAIL")
            self.results["failed"].append(f"Backend Root: {str(e)}")
            return False
            
    def test_backend_metrics(self) -> bool:
        """Test backend metrics endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/metrics", timeout=5)
            if response.status_code == 200:
                self.print_test("Backend Metrics Endpoint", "PASS")
                self.results["passed"].append("Backend Metrics Endpoint")
                return True
            else:
                self.print_test("Backend Metrics Endpoint", "WARN")
                self.results["warnings"].append(f"Backend Metrics: Status {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Backend Metrics Endpoint", "WARN")
            self.results["warnings"].append(f"Backend Metrics: {str(e)}")
            return False
            
    def test_backend_api_auth(self) -> bool:
        """Test API authentication"""
        headers = {}
        if API_KEY:
            headers["X-API-Key"] = API_KEY
            
        try:
            # Test without auth (should work if no API_KEY set, or fail if set)
            response = requests.get(f"{BACKEND_URL}/state", timeout=5)
            
            if API_KEY:
                # With API_KEY set, should require auth
                if response.status_code == 401:
                    # Now test with auth
                    response = requests.get(f"{BACKEND_URL}/state", headers=headers, timeout=5)
                    if response.status_code == 200:
                        self.print_test("Backend API Authentication", "PASS")
                        self.results["passed"].append("Backend API Authentication")
                        return True
                    else:
                        self.print_test("Backend API Authentication", "FAIL")
                        self.results["failed"].append(f"API Auth: Status {response.status_code}")
                        return False
                else:
                    self.print_test("Backend API Authentication", "WARN")
                    self.results["warnings"].append("API Auth: No auth required (dev mode)")
                    return True
            else:
                # No API_KEY set, should work without auth
                if response.status_code in [200, 503]:  # 503 if agent not initialized
                    self.print_test("Backend API Authentication", "PASS")
                    self.results["passed"].append("Backend API Authentication (dev mode)")
                    return True
                else:
                    self.print_test("Backend API Authentication", "WARN")
                    self.results["warnings"].append(f"API Auth: Unexpected status {response.status_code}")
                    return False
        except Exception as e:
            self.print_test("Backend API Authentication", "FAIL")
            self.results["failed"].append(f"API Auth: {str(e)}")
            return False
            
    def test_backend_chat_endpoint(self) -> bool:
        """Test chat endpoint"""
        headers = {"Content-Type": "application/json"}
        if API_KEY:
            headers["X-API-Key"] = API_KEY
            
        try:
            payload = {
                "message": "Hello, this is a test",
                "conversation_history": []
            }
            response = requests.post(
                f"{BACKEND_URL}/chat",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_test("Backend Chat Endpoint", "PASS")
                self.results["passed"].append("Backend Chat Endpoint")
                print(f"   Response received: {len(data.get('response', ''))} chars")
                return True
            elif response.status_code == 503:
                self.print_test("Backend Chat Endpoint", "WARN")
                self.results["warnings"].append("Backend Chat: Agent not initialized")
                return False
            else:
                self.print_test("Backend Chat Endpoint", "FAIL")
                self.results["failed"].append(f"Backend Chat: Status {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Backend Chat Endpoint", "FAIL")
            self.results["failed"].append(f"Backend Chat: {str(e)}")
            return False
            
    def test_backend_analyze_endpoint(self) -> bool:
        """Test analysis endpoint"""
        headers = {"Content-Type": "application/json"}
        if API_KEY:
            headers["X-API-Key"] = API_KEY
            
        try:
            payload = {
                "ticker": "AAPL",
                "risk_level": "moderate"
            }
            response = requests.post(
                f"{BACKEND_URL}/analyze",
                json=payload,
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_test("Backend Analyze Endpoint", "PASS")
                self.results["passed"].append("Backend Analyze Endpoint")
                print(f"   Ticker: {data.get('ticker')}")
                print(f"   Confidence: {data.get('confidence', 0)}")
                return True
            elif response.status_code == 503:
                self.print_test("Backend Analyze Endpoint", "WARN")
                self.results["warnings"].append("Backend Analyze: Agent not initialized")
                return False
            else:
                self.print_test("Backend Analyze Endpoint", "FAIL")
                self.results["failed"].append(f"Backend Analyze: Status {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Backend Analyze Endpoint", "FAIL")
            self.results["failed"].append(f"Backend Analyze: {str(e)}")
            return False
            
    def test_backend_state_endpoint(self) -> bool:
        """Test state endpoint"""
        headers = {}
        if API_KEY:
            headers["X-API-Key"] = API_KEY
            
        try:
            response = requests.get(f"{BACKEND_URL}/state", headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.print_test("Backend State Endpoint", "PASS")
                self.results["passed"].append("Backend State Endpoint")
                print(f"   State: {data.get('state', 'unknown')}")
                return True
            elif response.status_code == 503:
                self.print_test("Backend State Endpoint", "WARN")
                self.results["warnings"].append("Backend State: Agent not initialized")
                return False
            else:
                self.print_test("Backend State Endpoint", "FAIL")
                self.results["failed"].append(f"Backend State: Status {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Backend State Endpoint", "FAIL")
            self.results["failed"].append(f"Backend State: {str(e)}")
            return False
            
    def test_frontend_connectivity(self) -> bool:
        """Test frontend connectivity"""
        try:
            response = requests.get(f"{FRONTEND_URL}", timeout=10)
            if response.status_code == 200:
                self.print_test("Frontend Connectivity", "PASS")
                self.results["passed"].append("Frontend Connectivity")
                return True
            else:
                self.print_test("Frontend Connectivity", "FAIL")
                self.results["failed"].append(f"Frontend: Status {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Frontend Connectivity", "FAIL")
            self.results["failed"].append(f"Frontend: {str(e)}")
            return False
            
    def test_websocket_connection(self) -> bool:
        """Test WebSocket connection for voice"""
        try:
            ws_url = BACKEND_URL.replace("http://", "ws://").replace("https://", "wss://")
            ws_url = f"{ws_url}/voice/ws"
            
            connected = False
            error_msg = None
            
            def on_message(ws, message):
                nonlocal connected
                connected = True
                ws.close()
                
            def on_error(ws, error):
                nonlocal error_msg
                error_msg = str(error)
                
            def on_close(ws, close_status_code, close_msg):
                pass
                
            ws = websocket.WebSocketApp(
                ws_url,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            
            # Run for 3 seconds
            ws.run_forever(timeout=3)
            
            if connected:
                self.print_test("WebSocket Connection", "PASS")
                self.results["passed"].append("WebSocket Connection")
                return True
            elif error_msg:
                self.print_test("WebSocket Connection", "WARN")
                self.results["warnings"].append(f"WebSocket: {error_msg}")
                return False
            else:
                self.print_test("WebSocket Connection", "WARN")
                self.results["warnings"].append("WebSocket: Connection timeout (may be normal)")
                return False
        except Exception as e:
            self.print_test("WebSocket Connection", "WARN")
            self.results["warnings"].append(f"WebSocket: {str(e)}")
            return False
            
    def test_middleware_integration(self) -> bool:
        """Test middleware integration by checking metrics"""
        try:
            response = requests.get(f"{BACKEND_URL}/metrics", timeout=5)
            if response.status_code == 200:
                metrics_text = response.text
                # Check for middleware-related metrics
                if "http_request" in metrics_text or "tradingagents" in metrics_text.lower():
                    self.print_test("Middleware Integration (Metrics)", "PASS")
                    self.results["passed"].append("Middleware Integration")
                    return True
                else:
                    self.print_test("Middleware Integration (Metrics)", "WARN")
                    self.results["warnings"].append("Middleware: No custom metrics found")
                    return False
            else:
                self.print_test("Middleware Integration (Metrics)", "WARN")
                self.results["warnings"].append("Middleware: Metrics endpoint unavailable")
                return False
        except Exception as e:
            self.print_test("Middleware Integration (Metrics)", "WARN")
            self.results["warnings"].append(f"Middleware: {str(e)}")
            return False
            
    def test_cors_configuration(self) -> bool:
        """Test CORS configuration"""
        try:
            headers = {
                "Origin": FRONTEND_URL,
                "Access-Control-Request-Method": "POST"
            }
            response = requests.options(
                f"{BACKEND_URL}/chat",
                headers=headers,
                timeout=5
            )
            
            cors_headers = response.headers.get("Access-Control-Allow-Origin", "")
            if cors_headers in ["*", FRONTEND_URL]:
                self.print_test("CORS Configuration", "PASS")
                self.results["passed"].append("CORS Configuration")
                return True
            else:
                self.print_test("CORS Configuration", "WARN")
                self.results["warnings"].append(f"CORS: Allow-Origin = {cors_headers}")
                return False
        except Exception as e:
            self.print_test("CORS Configuration", "WARN")
            self.results["warnings"].append(f"CORS: {str(e)}")
            return False
            
    def run_all_tests(self):
        """Run all integration tests"""
        self.print_header("TradingAgents Integration Test Suite")
        
        print(f"{BLUE}Configuration:{NC}")
        print(f"   Backend URL: {BACKEND_URL}")
        print(f"   Frontend URL: {FRONTEND_URL}")
        print(f"   API Key: {'Set' if API_KEY else 'Not set (dev mode)'}\n")
        
        # Backend Tests
        self.print_header("Backend Tests")
        self.test_backend_health()
        self.test_backend_root()
        self.test_backend_metrics()
        self.test_backend_api_auth()
        self.test_backend_state_endpoint()
        self.test_backend_chat_endpoint()
        self.test_backend_analyze_endpoint()
        
        # Frontend Tests
        self.print_header("Frontend Tests")
        self.test_frontend_connectivity()
        
        # Integration Tests
        self.print_header("Integration Tests")
        self.test_websocket_connection()
        self.test_middleware_integration()
        self.test_cors_configuration()
        
        # Summary
        self.print_summary()
        
    def print_summary(self):
        """Print test summary"""
        elapsed = time.time() - self.start_time
        
        self.print_header("Test Summary")
        
        print(f"{GREEN}Passed: {len(self.results['passed'])}{NC}")
        print(f"{YELLOW}Warnings: {len(self.results['warnings'])}{NC}")
        print(f"{RED}Failed: {len(self.results['failed'])}{NC}")
        print(f"\n{BLUE}Total Time: {elapsed:.2f}s{NC}\n")
        
        if self.results["failed"]:
            print(f"{RED}Failed Tests:{NC}")
            for test in self.results["failed"]:
                print(f"   - {test}")
            print()
            
        if self.results["warnings"]:
            print(f"{YELLOW}Warnings:{NC}")
            for warning in self.results["warnings"]:
                print(f"   - {warning}")
            print()
            
        # Overall status
        if len(self.results["failed"]) == 0:
            print(f"{GREEN}✓ All critical tests passed!{NC}")
            return 0
        else:
            print(f"{RED}✗ Some tests failed. Please review the errors above.{NC}")
            return 1

def main():
    tester = IntegrationTester()
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

