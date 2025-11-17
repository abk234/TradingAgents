#!/bin/bash
# Wrapper script to run browse_chromadb.py with the virtual environment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found."
    echo "Please run: python run.py (this will create the venv and install dependencies)"
    exit 1
fi

# Activate virtual environment and run the script
source venv/bin/activate
python browse_chromadb.py "$@"

