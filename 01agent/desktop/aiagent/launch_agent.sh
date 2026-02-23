#!/bin/bash

echo "========================================"
echo "   Enhanced AI Agent - Quick Launch"
echo "========================================"
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "ERROR: Python $required_version or higher is required (found $python_version)"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update requirements
echo "Installing/updating requirements..."
pip install -r requirements.txt --quiet --disable-pip-version-check

# Check environment variables
if [ -z "$01AGENT_API_URL" ]; then
    echo "WARNING: 01AGENT_API_URL not set"
    read -p "Enter API URL (e.g., http://localhost:8000): " 01AGENT_API_URL
    export 01AGENT_API_URL
fi

if [ -z "$01AGENT_THREAD_ID" ]; then
    echo "WARNING: 01AGENT_THREAD_ID not set"
    read -p "Enter Thread ID: " 01AGENT_THREAD_ID
    export 01AGENT_THREAD_ID
fi

if [ -z "$01AGENT_USER_ACCESS_TOKEN" ]; then
    echo "WARNING: 01AGENT_USER_ACCESS_TOKEN not set"
    read -p "Enter Access Token: " 01AGENT_USER_ACCESS_TOKEN
    export 01AGENT_USER_ACCESS_TOKEN
fi

# Launch the enhanced agent
echo
echo "Starting Enhanced AI Agent..."
echo "========================================"
python main.py

# Check exit code
exit_code=$?
if [ $exit_code -ne 0 ]; then
    echo
    echo "Agent exited with error code $exit_code"
    read -p "Press Enter to continue..."
fi

deactivate