#!/usr/bin/env python3
"""
Log Analysis Tool for TradingAgents
Analyzes logs from backend, frontend, and middleware
"""

import os
import re
import sys
import json
import gzip
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional
from pathlib import Path

# Colors
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
NC = '\033[0m'

class LogAnalyzer:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.errors = []
        self.warnings = []
        self.info_messages = []
        self.api_calls = []
        self.middleware_events = []
        
    def find_log_files(self) -> List[Path]:
        """Find all log files"""
        log_files = []
        
        # Check logs directory
        if self.log_dir.exists():
            log_files.extend(self.log_dir.glob("*.log"))
            log_files.extend(self.log_dir.glob("*.log.gz"))
            
        # Check root directory
        root_logs = [
            Path("backend.log"),
            Path("frontend.log"),
            Path("services.log"),
            Path("backend_new.log")
        ]
        log_files.extend([f for f in root_logs if f.exists()])
        
        # Check web-app directory
        webapp_logs = Path("web-app")
        if webapp_logs.exists():
            log_files.extend(webapp_logs.glob("*.log"))
            
        return log_files
        
    def read_log_file(self, filepath: Path) -> List[str]:
        """Read log file (supports .gz)"""
        lines = []
        try:
            if filepath.suffix == '.gz':
                with gzip.open(filepath, 'rt', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
            else:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
        except Exception as e:
            print(f"{YELLOW}Warning: Could not read {filepath}: {e}{NC}")
        return lines
        
    def parse_log_line(self, line: str) -> Optional[Dict]:
        """Parse a log line"""
        # Common log patterns
        patterns = [
            # Python logging format
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (\w+) - (.*)',
            # ISO format
            r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[.\d]*Z?) - (\w+) - (.*)',
            # Simple format
            r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] (\w+) (.*)',
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line.strip())
            if match:
                timestamp = match.group(1)
                level = match.group(2).upper()
                message = match.group(3)
                return {
                    "timestamp": timestamp,
                    "level": level,
                    "message": message,
                    "raw": line.strip()
                }
                
        # If no pattern matches, return raw line
        if line.strip():
            return {
                "timestamp": None,
                "level": "UNKNOWN",
                "message": line.strip(),
                "raw": line.strip()
            }
        return None
        
    def analyze_errors(self, log_entries: List[Dict]) -> Dict:
        """Analyze error patterns"""
        errors = [e for e in log_entries if e["level"] in ["ERROR", "CRITICAL", "FATAL"]]
        
        error_patterns = Counter()
        error_messages = []
        
        for error in errors:
            message = error["message"]
            error_messages.append(message)
            
            # Extract error patterns
            if "Traceback" in message or "Exception" in message:
                # Try to extract exception type
                match = re.search(r'(\w+Error|\w+Exception)', message)
                if match:
                    error_patterns[match.group(1)] += 1
            else:
                # Use first 50 chars as pattern
                pattern = message[:50].strip()
                error_patterns[pattern] += 1
                
        return {
            "total_errors": len(errors),
            "error_patterns": dict(error_patterns.most_common(10)),
            "recent_errors": error_messages[-10:]
        }
        
    def analyze_api_calls(self, log_entries: List[Dict]) -> Dict:
        """Analyze API calls"""
        api_patterns = [
            r'POST /(\w+)',
            r'GET /(\w+)',
            r'PUT /(\w+)',
            r'DELETE /(\w+)',
        ]
        
        api_calls = Counter()
        response_times = []
        
        for entry in log_entries:
            message = entry["message"]
            
            # Check for API endpoints
            for pattern in api_patterns:
                match = re.search(pattern, message)
                if match:
                    endpoint = match.group(1)
                    api_calls[endpoint] += 1
                    
            # Check for response times
            time_match = re.search(r'(\d+\.?\d*)\s*ms|(\d+\.?\d*)\s*seconds?', message, re.IGNORECASE)
            if time_match:
                time_val = float(time_match.group(1) or time_match.group(2))
                response_times.append(time_val)
                
        return {
            "total_calls": sum(api_calls.values()),
            "endpoints": dict(api_calls.most_common(10)),
            "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0
        }
        
    def analyze_middleware(self, log_entries: List[Dict]) -> Dict:
        """Analyze middleware events"""
        middleware_keywords = [
            "middleware", "token", "summarization", "tracking",
            "pre_process", "post_process"
        ]
        
        middleware_events = []
        token_usage = []
        
        for entry in log_entries:
            message = entry["message"].lower()
            if any(keyword in message for keyword in middleware_keywords):
                middleware_events.append(entry)
                
                # Extract token counts
                token_match = re.search(r'(\d+)\s*tokens?', message, re.IGNORECASE)
                if token_match:
                    token_usage.append(int(token_match.group(1)))
                    
        return {
            "total_events": len(middleware_events),
            "token_usage": {
                "total": sum(token_usage),
                "avg": sum(token_usage) / len(token_usage) if token_usage else 0,
                "max": max(token_usage) if token_usage else 0
            }
        }
        
    def analyze_log_file(self, filepath: Path) -> Dict:
        """Analyze a single log file"""
        print(f"{BLUE}Analyzing {filepath}...{NC}")
        
        lines = self.read_log_file(filepath)
        log_entries = [self.parse_log_line(line) for line in lines]
        log_entries = [e for e in log_entries if e is not None]
        
        if not log_entries:
            return {}
            
        errors = self.analyze_errors(log_entries)
        api_calls = self.analyze_api_calls(log_entries)
        middleware = self.analyze_middleware(log_entries)
        
        # Count by level
        level_counts = Counter(e["level"] for e in log_entries)
        
        return {
            "file": str(filepath),
            "total_lines": len(log_entries),
            "level_counts": dict(level_counts),
            "errors": errors,
            "api_calls": api_calls,
            "middleware": middleware
        }
        
    def analyze_all(self) -> Dict:
        """Analyze all log files"""
        log_files = self.find_log_files()
        
        if not log_files:
            print(f"{YELLOW}No log files found{NC}")
            return {}
            
        print(f"{CYAN}Found {len(log_files)} log file(s){NC}\n")
        
        results = {}
        for log_file in log_files:
            results[log_file.name] = self.analyze_log_file(log_file)
            
        return results
        
    def print_summary(self, results: Dict):
        """Print analysis summary"""
        print(f"\n{CYAN}{'='*70}{NC}")
        print(f"{CYAN}Log Analysis Summary{NC:^70}")
        print(f"{CYAN}{'='*70}{NC}\n")
        
        total_errors = 0
        total_api_calls = 0
        total_middleware_events = 0
        
        for filename, analysis in results.items():
            if not analysis:
                continue
                
            print(f"{BLUE}{filename}{NC}")
            print(f"   Total Lines: {analysis.get('total_lines', 0)}")
            
            level_counts = analysis.get('level_counts', {})
            if level_counts:
                print(f"   Levels: {', '.join(f'{k}: {v}' for k, v in level_counts.items())}")
                
            errors = analysis.get('errors', {})
            if errors.get('total_errors', 0) > 0:
                total_errors += errors['total_errors']
                print(f"   {RED}Errors: {errors['total_errors']}{NC}")
                if errors.get('error_patterns'):
                    print(f"   Top Error Patterns:")
                    for pattern, count in list(errors['error_patterns'].items())[:3]:
                        print(f"      - {pattern}: {count}")
                        
            api_calls = analysis.get('api_calls', {})
            if api_calls.get('total_calls', 0) > 0:
                total_api_calls += api_calls['total_calls']
                print(f"   API Calls: {api_calls['total_calls']}")
                if api_calls.get('endpoints'):
                    print(f"   Top Endpoints:")
                    for endpoint, count in list(api_calls['endpoints'].items())[:5]:
                        print(f"      - /{endpoint}: {count}")
                        
            middleware = analysis.get('middleware', {})
            if middleware.get('total_events', 0) > 0:
                total_middleware_events += middleware['total_events']
                print(f"   Middleware Events: {middleware['total_events']}")
                if middleware.get('token_usage', {}).get('total', 0) > 0:
                    token_info = middleware['token_usage']
                    print(f"   Token Usage: {token_info['total']} total, {token_info['avg']:.0f} avg")
                    
            print()
            
        print(f"{CYAN}{'='*70}{NC}")
        print(f"{BLUE}Overall Statistics:{NC}")
        print(f"   Total Errors: {total_errors}")
        print(f"   Total API Calls: {total_api_calls}")
        print(f"   Total Middleware Events: {total_middleware_events}")
        print()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="TradingAgents Log Analyzer")
    parser.add_argument("--dir", "-d", type=str, default="logs",
                       help="Log directory (default: logs)")
    parser.add_argument("--output", "-o", type=str,
                       help="Output results to JSON file")
    
    args = parser.parse_args()
    
    analyzer = LogAnalyzer(log_dir=args.dir)
    results = analyzer.analyze_all()
    
    if results:
        analyzer.print_summary(results)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"{GREEN}Results exported to {args.output}{NC}")

if __name__ == "__main__":
    main()

