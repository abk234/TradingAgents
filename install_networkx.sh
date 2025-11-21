#!/bin/bash
# Install networkx in venv
cd "$(dirname "$0")/../.."
if [ -d "venv" ]; then
    echo "Installing networkx in venv..."
    venv/bin/pip install networkx
elif [ -d ".venv" ]; then
    echo "Installing networkx in .venv..."
    .venv/bin/pip install networkx
else
    echo "No virtual environment found"
    exit 1
fi
