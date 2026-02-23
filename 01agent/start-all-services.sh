#!/bin/bash

echo "========================================"
echo "   01Agent - Complete System Startup"
echo "========================================"
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed or not in PATH"
    echo "Please install Node.js 16 or higher"
    exit 1
fi

echo "========================================"
echo "Step 1: Setting up Backend"
echo "========================================"

cd backend

# Create virtual environment for backend if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating backend virtual environment..."
    python3 -m venv venv
fi

# Activate backend virtual environment
source venv/bin/activate

# Install backend dependencies
echo "Installing backend dependencies..."
pip install -r requirements.txt --quiet

# Start backend in background
echo "Starting backend server..."
nohup uvicorn main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# Wait a moment for backend to start
sleep 5

cd ..

echo "========================================"
echo "Step 2: Setting up Frontend"
echo "========================================"

cd desktop/01agent-app

# Install frontend dependencies
echo "Installing frontend dependencies..."
npm install --silent

# Start frontend in background
echo "Starting frontend application..."
nohup npm start > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"

# Wait a moment for frontend to start
sleep 5

cd ../..

echo "========================================"
echo "Step 3: Setting up AI Agent"
echo "========================================"

cd desktop/aiagent

# Create virtual environment for agent if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating agent virtual environment..."
    python3 -m venv venv
fi

# Activate agent virtual environment
source venv/bin/activate

# Install agent dependencies
echo "Installing agent dependencies..."
pip install -r requirements.txt --quiet

# Check environment variables
if [ -z "$01AGENT_API_URL" ]; then
    echo "Setting default API URL..."
    export 01AGENT_API_URL="http://localhost:8000"
fi

if [ -z "$01AGENT_THREAD_ID" ]; then
    echo "WARNING: 01AGENT_THREAD_ID not set"
    read -p "Enter Thread ID (or press Enter to skip): " 01AGENT_THREAD_ID
    export 01AGENT_THREAD_ID
fi

if [ -z "$01AGENT_USER_ACCESS_TOKEN" ]; then
    echo "WARNING: 01AGENT_USER_ACCESS_TOKEN not set"
    read -p "Enter Access Token (or press Enter to skip): " 01AGENT_USER_ACCESS_TOKEN
    export 01AGENT_USER_ACCESS_TOKEN
fi

echo "========================================"
echo "All Services Status"
echo "========================================"
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo
echo "Press Enter to start the AI Agent..."
read

# Start AI Agent
echo "Starting AI Agent..."
python3 main.py

echo
echo "========================================"
echo "Startup Complete!"
echo "========================================"
echo
echo "Services running:"
echo "- Backend API: http://localhost:8000"
echo "- Frontend UI: http://localhost:3000"
echo "- AI Agent: Active"
echo
echo "To stop all services:"
echo "kill $BACKEND_PID $FRONTEND_PID"