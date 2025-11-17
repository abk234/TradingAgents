#!/usr/bin/env python3
"""
Progress Tracker Utility

This script provides real-time progress tracking for TradingAgents operations.
It monitors log files and displays progress information.
"""

import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import json

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class ProgressTracker:
    """Track progress of TradingAgents operations"""

    def __init__(self, log_dir: Path = None):
        self.log_dir = log_dir or Path(__file__).parent.parent / "logs"
        self.log_dir.mkdir(exist_ok=True)
        self.progress_file = self.log_dir / "progress.json"
        self.tasks: Dict[str, dict] = {}

    def load_progress(self):
        """Load progress from file"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    self.tasks = json.load(f)
            except json.JSONDecodeError:
                self.tasks = {}

    def save_progress(self):
        """Save progress to file"""
        with open(self.progress_file, 'w') as f:
            json.dump(self.tasks, f, indent=2)

    def add_task(self, task_id: str, name: str, total_steps: int = 1):
        """Add a new task to track"""
        self.tasks[task_id] = {
            'name': name,
            'total_steps': total_steps,
            'completed_steps': 0,
            'status': 'pending',
            'started_at': None,
            'completed_at': None,
            'error': None
        }
        self.save_progress()

    def start_task(self, task_id: str):
        """Mark task as started"""
        if task_id in self.tasks:
            self.tasks[task_id]['status'] = 'running'
            self.tasks[task_id]['started_at'] = datetime.now().isoformat()
            self.save_progress()

    def update_task(self, task_id: str, completed_steps: int = None, message: str = None):
        """Update task progress"""
        if task_id in self.tasks:
            if completed_steps is not None:
                self.tasks[task_id]['completed_steps'] = completed_steps
            if message:
                self.tasks[task_id]['message'] = message
            self.save_progress()

    def complete_task(self, task_id: str, success: bool = True, error: str = None):
        """Mark task as completed"""
        if task_id in self.tasks:
            self.tasks[task_id]['status'] = 'completed' if success else 'failed'
            self.tasks[task_id]['completed_at'] = datetime.now().isoformat()
            if error:
                self.tasks[task_id]['error'] = error
            self.save_progress()

    def display_progress(self, clear_screen: bool = True):
        """Display current progress"""
        if clear_screen:
            print('\033[2J\033[H', end='')  # Clear screen

        print(f"{Colors.HEADER}{Colors.BOLD}╔════════════════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}║              TradingAgents Progress Tracker                        ║{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}╚════════════════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not self.tasks:
            print(f"{Colors.WARNING}No tasks currently tracked{Colors.ENDC}")
            return

        for task_id, task in self.tasks.items():
            status_color = {
                'pending': Colors.WARNING,
                'running': Colors.OKCYAN,
                'completed': Colors.OKGREEN,
                'failed': Colors.FAIL
            }.get(task['status'], Colors.ENDC)

            status_icon = {
                'pending': '⏳',
                'running': '🔄',
                'completed': '✅',
                'failed': '❌'
            }.get(task['status'], '?')

            # Calculate percentage
            if task['total_steps'] > 0:
                percentage = (task['completed_steps'] / task['total_steps']) * 100
            else:
                percentage = 0

            # Display task info
            print(f"{status_color}{status_icon} {task['name']}{Colors.ENDC}")
            print(f"   Status: {status_color}{task['status'].upper()}{Colors.ENDC}")

            # Progress bar
            bar_width = 40
            filled = int(bar_width * percentage / 100)
            bar = '█' * filled + '░' * (bar_width - filled)
            print(f"   Progress: [{Colors.OKGREEN}{bar}{Colors.ENDC}] {percentage:.1f}%")
            print(f"   Steps: {task['completed_steps']}/{task['total_steps']}")

            if task.get('message'):
                print(f"   {Colors.OKCYAN}💬 {task['message']}{Colors.ENDC}")

            if task.get('error'):
                print(f"   {Colors.FAIL}❌ Error: {task['error']}{Colors.ENDC}")

            # Timing info
            if task['started_at']:
                started = datetime.fromisoformat(task['started_at'])
                if task['completed_at']:
                    completed = datetime.fromisoformat(task['completed_at'])
                    duration = (completed - started).total_seconds()
                    print(f"   ⏱️  Duration: {duration:.1f}s")
                else:
                    duration = (datetime.now() - started).total_seconds()
                    print(f"   ⏱️  Running for: {duration:.1f}s")

            print()

    def watch(self, interval: float = 1.0):
        """Watch and display progress in real-time"""
        try:
            while True:
                self.load_progress()
                self.display_progress()

                # Check if all tasks are completed
                if all(t['status'] in ['completed', 'failed'] for t in self.tasks.values()):
                    print(f"\n{Colors.OKGREEN}{Colors.BOLD}All tasks completed!{Colors.ENDC}\n")
                    break

                time.sleep(interval)
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}Progress tracking stopped{Colors.ENDC}")

    def summary(self):
        """Display summary statistics"""
        self.load_progress()

        total = len(self.tasks)
        completed = sum(1 for t in self.tasks.values() if t['status'] == 'completed')
        failed = sum(1 for t in self.tasks.values() if t['status'] == 'failed')
        running = sum(1 for t in self.tasks.values() if t['status'] == 'running')
        pending = sum(1 for t in self.tasks.values() if t['status'] == 'pending')

        print(f"\n{Colors.HEADER}{Colors.BOLD}Task Summary{Colors.ENDC}")
        print(f"{'─' * 40}")
        print(f"Total Tasks:     {total}")
        print(f"{Colors.OKGREEN}✅ Completed:    {completed}{Colors.ENDC}")
        print(f"{Colors.FAIL}❌ Failed:       {failed}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}🔄 Running:      {running}{Colors.ENDC}")
        print(f"{Colors.WARNING}⏳ Pending:      {pending}{Colors.ENDC}")

        if total > 0:
            success_rate = (completed / total) * 100
            print(f"\nSuccess Rate:    {success_rate:.1f}%")

    def clear(self):
        """Clear all tracked tasks"""
        self.tasks = {}
        self.save_progress()
        print(f"{Colors.OKGREEN}Progress cleared{Colors.ENDC}")


def main():
    """Main CLI interface"""
    tracker = ProgressTracker()

    if len(sys.argv) < 2:
        print("Usage: progress_tracker.py [watch|summary|clear]")
        print("\nCommands:")
        print("  watch    - Watch progress in real-time")
        print("  summary  - Display task summary")
        print("  clear    - Clear all tracked tasks")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'watch':
        tracker.watch()
    elif command == 'summary':
        tracker.summary()
    elif command == 'clear':
        tracker.clear()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
