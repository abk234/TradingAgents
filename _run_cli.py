
import os
import sys

# Set chromadb environment variables before any imports
os.environ.setdefault("CHROMA_SERVER_HOST", "localhost")
os.environ.setdefault("CHROMA_SERVER_HTTP_PORT", "8000")
os.environ.setdefault("CHROMA_SERVER_GRPC_PORT", "50051")
os.environ.setdefault("CLICKHOUSE_HOST", "localhost")
os.environ.setdefault("CLICKHOUSE_PORT", "8123")

# Load .env file
from dotenv import load_dotenv
load_dotenv()

# Import and run the interactive analysis function
from cli.main import run_analysis
run_analysis()
