#!/usr/bin/env python3
"""
Direct script to run TradingAgents analysis
This bypasses the Typer CLI issues when running as a module
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set chromadb environment variables before any imports
os.environ.setdefault("CHROMA_SERVER_HOST", "localhost")
os.environ.setdefault("CHROMA_SERVER_HTTP_PORT", "8000")
os.environ.setdefault("CHROMA_SERVER_GRPC_PORT", "50051")
os.environ.setdefault("CLICKHOUSE_HOST", "localhost")
os.environ.setdefault("CLICKHOUSE_PORT", "8123")

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import and run the analysis function
from cli.main import run_analysis

if __name__ == "__main__":
    run_analysis()

