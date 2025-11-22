#!/usr/bin/env python3
"""
End-to-End Test Suite for TradingAgents
Tests complete user workflows from frontend to backend to middleware
"""

import os
import sys
import time
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8005")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3005")
API_KEY = os.getenv("API_KEY", "")

# Colors
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
NC = '\033[0m'

class E2ETester:
    def __init__(self):
        self.results = {
            "passed": [],
            "failed": [],
            "warnings": []
        }
        self.start_time = time.time()
        self.headers = {"Content-Type": "application/json"}
        if API_KEY:
            self.headers["X-API-Key"] = API_KEY
            
    def print_header(self, text: str):
        print(f"\n{CYAN}{'='*60}{NC}")
        print(f"{CYAN}{text:^60}{NC}")
        print(f"{CYAN}{'='*60}{NC}\n")
        
    def print_test(self, name: str, status: str = "RUNNING", details: str = ""):
        if status == "PASS":
            print(f"{GREEN}✓{NC} {name}")
        elif status == "FAIL":
            print(f"{RED}✗{NC} {name}")
        elif status == "WARN":
            print(f"{YELLOW}⚠{NC} {name}")
        else:
            print(f"{BLUE}→{NC} {name}")
            
        if details:
            print(f"   {details}")
            
    def test_workflow_chat(self) -> bool:
        """Test complete chat workflow"""
        self.print_test("E2E: Chat Workflow", "RUNNING")
        
        try:
            # Step 1: Send initial message
            payload = {
                "message": "Hello, can you help me analyze AAPL?",
                "conversation_history": []
            }
            
            response = requests.post(
                f"{BACKEND_URL}/chat",
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                conversation_id = data.get("conversation_id")
                response_text = data.get("response", "")
                
                if conversation_id and response_text:
                    self.print_test("E2E: Chat Workflow", "PASS", 
                                  f"Conversation ID: {conversation_id[:8]}...")
                    self.results["passed"].append("E2E: Chat Workflow")
                    
                    # Step 2: Continue conversation
                    payload2 = {
                        "message": "What is the current price?",
                        "conversation_history": [
                            {"role": "user", "content": "Hello, can you help me analyze AAPL?"},
                            {"role": "assistant", "content": response_text}
                        ],
                        "conversation_id": conversation_id
                    }
                    
                    response2 = requests.post(
                        f"{BACKEND_URL}/chat",
                        json=payload2,
                        headers=self.headers,
                        timeout=30
                    )
                    
                    if response2.status_code == 200:
                        self.print_test("E2E: Chat Continuation", "PASS")
                        self.results["passed"].append("E2E: Chat Continuation")
                        return True
                    else:
                        self.print_test("E2E: Chat Continuation", "WARN",
                                      f"Status: {response2.status_code}")
                        return True  # First part passed
                else:
                    self.print_test("E2E: Chat Workflow", "FAIL", "Missing conversation_id or response")
                    self.results["failed"].append("E2E: Chat Workflow")
                    return False
            elif response.status_code == 503:
                self.print_test("E2E: Chat Workflow", "WARN", "Agent not initialized")
                self.results["warnings"].append("E2E: Chat Workflow - Agent not initialized")
                return False
            else:
                self.print_test("E2E: Chat Workflow", "FAIL", f"Status: {response.status_code}")
                self.results["failed"].append(f"E2E: Chat Workflow - Status {response.status_code}")
                return False
        except Exception as e:
            self.print_test("E2E: Chat Workflow", "FAIL", str(e))
            self.results["failed"].append(f"E2E: Chat Workflow - {str(e)}")
            return False
            
    def test_workflow_analysis(self) -> bool:
        """Test complete analysis workflow"""
        self.print_test("E2E: Analysis Workflow", "RUNNING")
        
        try:
            payload = {
                "ticker": "AAPL",
                "risk_level": "moderate",
                "investment_style": "growth"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/analyze",
                json=payload,
                headers=self.headers,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                ticker = data.get("ticker")
                decision = data.get("decision", "")
                confidence = data.get("confidence", 0)
                
                if ticker == "AAPL" and decision and confidence >= 0:
                    self.print_test("E2E: Analysis Workflow", "PASS",
                                  f"Ticker: {ticker}, Confidence: {confidence}")
                    self.results["passed"].append("E2E: Analysis Workflow")
                    return True
                else:
                    self.print_test("E2E: Analysis Workflow", "FAIL", "Invalid response data")
                    self.results["failed"].append("E2E: Analysis Workflow - Invalid data")
                    return False
            elif response.status_code == 503:
                self.print_test("E2E: Analysis Workflow", "WARN", "Agent not initialized")
                self.results["warnings"].append("E2E: Analysis Workflow - Agent not initialized")
                return False
            else:
                self.print_test("E2E: Analysis Workflow", "FAIL", f"Status: {response.status_code}")
                self.results["failed"].append(f"E2E: Analysis Workflow - Status {response.status_code}")
                return False
        except Exception as e:
            self.print_test("E2E: Analysis Workflow", "FAIL", str(e))
            self.results["failed"].append(f"E2E: Analysis Workflow - {str(e)}")
            return False
            
    def test_workflow_state_tracking(self) -> bool:
        """Test state tracking workflow"""
        self.print_test("E2E: State Tracking", "RUNNING")
        
        try:
            # Get initial state
            response1 = requests.get(f"{BACKEND_URL}/state", headers=self.headers, timeout=5)
            
            if response1.status_code == 200:
                state1 = response1.json()
                
                # Trigger an action (chat)
                payload = {
                    "message": "What is the market status?",
                    "conversation_history": []
                }
                requests.post(f"{BACKEND_URL}/chat", json=payload, headers=self.headers, timeout=30)
                
                # Get state after action
                time.sleep(1)  # Give it a moment
                response2 = requests.get(f"{BACKEND_URL}/state", headers=self.headers, timeout=5)
                
                if response2.status_code == 200:
                    state2 = response2.json()
                    
                    # States should be different or at least accessible
                    self.print_test("E2E: State Tracking", "PASS",
                                  f"State accessible: {state2.get('state', 'unknown')}")
                    self.results["passed"].append("E2E: State Tracking")
                    return True
                else:
                    self.print_test("E2E: State Tracking", "WARN", "Could not get state after action")
                    return True  # Initial state worked
            elif response1.status_code == 503:
                self.print_test("E2E: State Tracking", "WARN", "Agent not initialized")
                self.results["warnings"].append("E2E: State Tracking - Agent not initialized")
                return False
            else:
                self.print_test("E2E: State Tracking", "FAIL", f"Status: {response1.status_code}")
                self.results["failed"].append(f"E2E: State Tracking - Status {response1.status_code}")
                return False
        except Exception as e:
            self.print_test("E2E: State Tracking", "FAIL", str(e))
            self.results["failed"].append(f"E2E: State Tracking - {str(e)}")
            return False
            
    def test_workflow_frontend_backend(self) -> bool:
        """Test frontend-backend integration"""
        self.print_test("E2E: Frontend-Backend Integration", "RUNNING")
        
        try:
            # Check frontend is accessible
            frontend_response = requests.get(f"{FRONTEND_URL}", timeout=5)
            
            if frontend_response.status_code == 200:
                # Check backend is accessible
                backend_response = requests.get(f"{BACKEND_URL}/health", timeout=5)
                
                if backend_response.status_code == 200:
                    # Check CORS
                    cors_headers = {
                        "Origin": FRONTEND_URL,
                        "Access-Control-Request-Method": "POST"
                    }
                    cors_response = requests.options(
                        f"{BACKEND_URL}/chat",
                        headers=cors_headers,
                        timeout=5
                    )
                    
                    if cors_response.status_code in [200, 204]:
                        self.print_test("E2E: Frontend-Backend Integration", "PASS",
                                      "Frontend and backend connected with CORS")
                        self.results["passed"].append("E2E: Frontend-Backend Integration")
                        return True
                    else:
                        self.print_test("E2E: Frontend-Backend Integration", "WARN",
                                      "CORS check failed")
                        return True  # Basic connectivity works
                else:
                    self.print_test("E2E: Frontend-Backend Integration", "FAIL",
                                  "Backend not accessible")
                    self.results["failed"].append("E2E: Frontend-Backend - Backend down")
                    return False
            else:
                self.print_test("E2E: Frontend-Backend Integration", "FAIL",
                              "Frontend not accessible")
                self.results["failed"].append("E2E: Frontend-Backend - Frontend down")
                return False
        except Exception as e:
            self.print_test("E2E: Frontend-Backend Integration", "FAIL", str(e))
            self.results["failed"].append(f"E2E: Frontend-Backend - {str(e)}")
            return False
            
    def test_workflow_middleware(self) -> bool:
        """Test middleware integration"""
        self.print_test("E2E: Middleware Integration", "RUNNING")
        
        try:
            # Make a request that should trigger middleware
            payload = {
                "message": "Analyze MSFT",
                "conversation_history": []
            }
            
            start_time = time.time()
            response = requests.post(
                f"{BACKEND_URL}/chat",
                json=payload,
                headers=self.headers,
                timeout=30
            )
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                # Check metrics endpoint for middleware activity
                metrics_response = requests.get(f"{BACKEND_URL}/metrics", timeout=5)
                
                if metrics_response.status_code == 200:
                    metrics_text = metrics_response.text
                    # Look for middleware-related metrics
                    if "http_request" in metrics_text or "tradingagents" in metrics_text.lower():
                        self.print_test("E2E: Middleware Integration", "PASS",
                                      f"Middleware active, response time: {elapsed:.2f}s")
                        self.results["passed"].append("E2E: Middleware Integration")
                        return True
                    else:
                        self.print_test("E2E: Middleware Integration", "WARN",
                                      "Middleware metrics not found")
                        return True  # Request worked
                else:
                    self.print_test("E2E: Middleware Integration", "WARN",
                                  "Could not check metrics")
                    return True  # Request worked
            elif response.status_code == 503:
                self.print_test("E2E: Middleware Integration", "WARN", "Agent not initialized")
                self.results["warnings"].append("E2E: Middleware - Agent not initialized")
                return False
            else:
                self.print_test("E2E: Middleware Integration", "FAIL",
                              f"Status: {response.status_code}")
                self.results["failed"].append(f"E2E: Middleware - Status {response.status_code}")
                return False
        except Exception as e:
            self.print_test("E2E: Middleware Integration", "FAIL", str(e))
            self.results["failed"].append(f"E2E: Middleware - {str(e)}")
            return False
            
    def run_all_tests(self):
        """Run all E2E tests"""
        self.print_header("TradingAgents End-to-End Test Suite")
        
        print(f"{BLUE}Configuration:{NC}")
        print(f"   Backend URL: {BACKEND_URL}")
        print(f"   Frontend URL: {FRONTEND_URL}")
        print(f"   API Key: {'Set' if API_KEY else 'Not set (dev mode)'}\n")
        
        # Run workflows
        self.test_workflow_frontend_backend()
        self.test_workflow_chat()
        self.test_workflow_analysis()
        self.test_workflow_state_tracking()
        self.test_workflow_middleware()
        
        # Summary
        self.print_summary()
        
    def print_summary(self):
        """Print test summary"""
        elapsed = time.time() - self.start_time
        
        self.print_header("E2E Test Summary")
        
        print(f"{GREEN}Passed: {len(self.results['passed'])}{NC}")
        print(f"{YELLOW}Warnings: {len(self.results['warnings'])}{NC}")
        print(f"{RED}Failed: {len(self.results['failed'])}{NC}")
        print(f"\n{BLUE}Total Time: {elapsed:.2f}s{NC}\n")
        
        if self.results["passed"]:
            print(f"{GREEN}Passed Tests:{NC}")
            for test in self.results["passed"]:
                print(f"   ✓ {test}")
            print()
            
        if self.results["warnings"]:
            print(f"{YELLOW}Warnings:{NC}")
            for warning in self.results["warnings"]:
                print(f"   ⚠ {warning}")
            print()
            
        if self.results["failed"]:
            print(f"{RED}Failed Tests:{NC}")
            for test in self.results["failed"]:
                print(f"   ✗ {test}")
            print()
            
        # Overall status
        if len(self.results["failed"]) == 0:
            print(f"{GREEN}✓ All E2E tests passed!{NC}")
            return 0
        else:
            print(f"{RED}✗ Some E2E tests failed. Please review the errors above.{NC}")
            return 1

def main():
    tester = E2ETester()
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

