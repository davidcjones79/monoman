#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

# Check if venv exists, create if not
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate venv
source "$VENV_DIR/bin/activate"

# Check if monoman-web is installed, install if not
if ! command -v monoman-web &> /dev/null; then
    echo "Installing monoman with web support..."
    pip install -e "$SCRIPT_DIR[web]"
fi

# Run monoman-web
monoman-web
