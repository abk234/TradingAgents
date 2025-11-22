#!/usr/bin/env python3
"""
System Health Monitor for TradingAgents
Monitors backend, frontend, middleware, and system health
"""

import os
import sys
import time
import json
import requests
import psutil
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8005")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3005")
API_KEY = os.getenv("API_KEY", "")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "10"))  # seconds

# Colors
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
NC = '\033[0m'

@dataclass
class HealthStatus:
    component: str
    status: str  # "healthy", "degraded", "down"
    message: str
    timestamp: str
    metrics: Dict = None
    
    def __post_init__(self):
        if self.metrics is None:
            self.metrics = {}

class SystemMonitor:
    def __init__(self):
        self.health_history: List[HealthStatus] = []
        
    def check_backend_health(self) -> HealthStatus:
        """Check backend health"""
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                agent_initialized = data.get("agent_initialized", False)
                
                if agent_initialized:
                    return HealthStatus(
                        component="Backend",
                        status="healthy",
                        message="Backend is running and agent is initialized",
                        timestamp=datetime.now().isoformat(),
                        metrics={"agent_initialized": True}
                    )
                else:
                    return HealthStatus(
                        component="Backend",
                        status="degraded",
                        message="Backend is running but agent is not initialized",
                        timestamp=datetime.now().isoformat(),
                        metrics={"agent_initialized": False}
                    )
            else:
                return HealthStatus(
                    component="Backend",
                    status="down",
                    message=f"Backend returned status {response.status_code}",
                    timestamp=datetime.now().isoformat()
                )
        except requests.exceptions.ConnectionError:
            return HealthStatus(
                component="Backend",
                status="down",
                message="Cannot connect to backend",
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            return HealthStatus(
                component="Backend",
                status="down",
                message=f"Error: {str(e)}",
                timestamp=datetime.now().isoformat()
            )
            
    def check_frontend_health(self) -> HealthStatus:
        """Check frontend health"""
        try:
            response = requests.get(f"{FRONTEND_URL}", timeout=5)
            if response.status_code == 200:
                return HealthStatus(
                    component="Frontend",
                    status="healthy",
                    message="Frontend is accessible",
                    timestamp=datetime.now().isoformat()
                )
            else:
                return HealthStatus(
                    component="Frontend",
                    status="degraded",
                    message=f"Frontend returned status {response.status_code}",
                    timestamp=datetime.now().isoformat()
                )
        except requests.exceptions.ConnectionError:
            return HealthStatus(
                component="Frontend",
                status="down",
                message="Cannot connect to frontend",
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            return HealthStatus(
                component="Frontend",
                status="down",
                message=f"Error: {str(e)}",
                timestamp=datetime.now().isoformat()
            )
            
    def check_backend_metrics(self) -> HealthStatus:
        """Check backend metrics endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/metrics", timeout=5)
            if response.status_code == 200:
                metrics_text = response.text
                # Parse some basic metrics
                metrics = {}
                for line in metrics_text.split('\n'):
                    if line.startswith('#') or not line.strip():
                        continue
                    if 'http_requests_total' in line:
                        try:
                            parts = line.split()
                            if len(parts) >= 2:
                                metrics['http_requests'] = float(parts[-1])
                        except:
                            pass
                            
                return HealthStatus(
                    component="Backend Metrics",
                    status="healthy",
                    message="Metrics endpoint is accessible",
                    timestamp=datetime.now().isoformat(),
                    metrics=metrics
                )
            else:
                return HealthStatus(
                    component="Backend Metrics",
                    status="degraded",
                    message=f"Metrics endpoint returned status {response.status_code}",
                    timestamp=datetime.now().isoformat()
                )
        except Exception as e:
            return HealthStatus(
                component="Backend Metrics",
                status="down",
                message=f"Error: {str(e)}",
                timestamp=datetime.now().isoformat()
            )
            
    def check_backend_api(self) -> HealthStatus:
        """Check backend API endpoint"""
        headers = {}
        if API_KEY:
            headers["X-API-Key"] = API_KEY
            
        try:
            response = requests.get(f"{BACKEND_URL}/state", headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return HealthStatus(
                    component="Backend API",
                    status="healthy",
                    message="API endpoint is accessible",
                    timestamp=datetime.now().isoformat(),
                    metrics={"state": data.get("state", "unknown")}
                )
            elif response.status_code == 401:
                return HealthStatus(
                    component="Backend API",
                    status="degraded",
                    message="API authentication required but not provided",
                    timestamp=datetime.now().isoformat()
                )
            elif response.status_code == 503:
                return HealthStatus(
                    component="Backend API",
                    status="degraded",
                    message="API endpoint available but agent not initialized",
                    timestamp=datetime.now().isoformat()
                )
            else:
                return HealthStatus(
                    component="Backend API",
                    status="degraded",
                    message=f"API returned status {response.status_code}",
                    timestamp=datetime.now().isoformat()
                )
        except Exception as e:
            return HealthStatus(
                component="Backend API",
                status="down",
                message=f"Error: {str(e)}",
                timestamp=datetime.now().isoformat()
            )
            
    def check_system_resources(self) -> HealthStatus:
        """Check system resources"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            status = "healthy"
            issues = []
            
            if cpu_percent > 90:
                status = "degraded"
                issues.append(f"High CPU: {cpu_percent:.1f}%")
            if memory.percent > 90:
                status = "degraded"
                issues.append(f"High Memory: {memory.percent:.1f}%")
            if disk.percent > 90:
                status = "degraded"
                issues.append(f"High Disk: {disk.percent:.1f}%")
                
            message = "System resources normal" if not issues else "; ".join(issues)
            
            return HealthStatus(
                component="System Resources",
                status=status,
                message=message,
                timestamp=datetime.now().isoformat(),
                metrics={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent,
                    "memory_available_gb": memory.available / (1024**3),
                    "disk_free_gb": disk.free / (1024**3)
                }
            )
        except Exception as e:
            return HealthStatus(
                component="System Resources",
                status="down",
                message=f"Error: {str(e)}",
                timestamp=datetime.now().isoformat()
            )
            
    def check_all(self) -> List[HealthStatus]:
        """Run all health checks"""
        checks = [
            self.check_backend_health(),
            self.check_frontend_health(),
            self.check_backend_metrics(),
            self.check_backend_api(),
            self.check_system_resources()
        ]
        
        self.health_history.extend(checks)
        # Keep only last 100 checks
        if len(self.health_history) > 100:
            self.health_history = self.health_history[-100:]
            
        return checks
        
    def print_status(self, statuses: List[HealthStatus]):
        """Print health status"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print(f"\n{CYAN}{'='*70}{NC}")
        print(f"{CYAN}TradingAgents System Health Monitor{NC:^70}")
        print(f"{CYAN}{'='*70}{NC}\n")
        print(f"{BLUE}Last Check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{NC}\n")
        
        for status in statuses:
            if status.status == "healthy":
                icon = f"{GREEN}✓{NC}"
            elif status.status == "degraded":
                icon = f"{YELLOW}⚠{NC}"
            else:
                icon = f"{RED}✗{NC}"
                
            print(f"{icon} {status.component:25} {status.status.upper():10} {status.message}")
            
            if status.metrics:
                for key, value in status.metrics.items():
                    if isinstance(value, float):
                        print(f"   {key}: {value:.2f}")
                    else:
                        print(f"   {key}: {value}")
                        
        print(f"\n{CYAN}{'='*70}{NC}")
        print(f"{BLUE}Press Ctrl+C to stop monitoring{NC}\n")
        
    def export_status(self, filename: str = None):
        """Export health status to JSON"""
        if filename is None:
            filename = f"health_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        data = {
            "timestamp": datetime.now().isoformat(),
            "checks": [asdict(status) for status in self.health_history[-10:]]  # Last 10 checks
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
            
        print(f"{GREEN}Health status exported to {filename}{NC}")
        
    def monitor_loop(self, continuous: bool = False):
        """Run monitoring loop"""
        try:
            while True:
                statuses = self.check_all()
                self.print_status(statuses)
                
                if not continuous:
                    break
                    
                time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print(f"\n{YELLOW}Monitoring stopped by user{NC}")
            self.export_status()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="TradingAgents System Health Monitor")
    parser.add_argument("--continuous", "-c", action="store_true", 
                       help="Run continuous monitoring")
    parser.add_argument("--interval", "-i", type=int, default=10,
                       help="Check interval in seconds (default: 10)")
    parser.add_argument("--export", "-e", type=str,
                       help="Export status to JSON file")
    
    args = parser.parse_args()
    
    global CHECK_INTERVAL
    CHECK_INTERVAL = args.interval
    
    monitor = SystemMonitor()
    
    if args.export:
        statuses = monitor.check_all()
        monitor.export_status(args.export)
    else:
        monitor.monitor_loop(continuous=args.continuous)

if __name__ == "__main__":
    main()

