# 🚀 Quick Start Guide - How to Test Your App

## Step 1: System Check
Run this first to make sure everything is installed:
```bash
test-setup.bat
```

## Step 2: Environment Setup (One-time)
Set up your environment variables:
```bash
setup-environment.bat
```

## Step 3: Start All Services
Launch everything at once:
```bash
start-all-services.bat
```

## Alternative: Manual Step-by-Step

### Option A: Start Backend Only
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
**Test**: Visit http://localhost:8000/docs

### Option B: Start Frontend Only
```bash
cd desktop\01agent-app
npm install
npm start
```
**Test**: Visit http://localhost:3000

### Option C: Start AI Agent Only
```bash
cd desktop\aiagent
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
set 01AGENT_API_URL=http://localhost:8000
set 01AGENT_THREAD_ID=your-thread-id
set 01AGENT_USER_ACCESS_TOKEN=your-token

python main.py
```

## 🌐 Where to Test Your App

### 1. Backend API
- **URL**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 2. Frontend UI
- **URL**: http://localhost:3000
- **Main Dashboard**: http://localhost:3000
- **Agent Status**: http://localhost:3000/agent-status
- **Performance**: http://localhost:3000/performance
- **Settings**: http://localhost:3000/settings

### 3. Landing Page
- **URL**: Open `landing-page/index.html` in browser
- **Features**: Project overview and documentation

## 🔧 Troubleshooting

### Common Issues:

**Port Already in Use:**
```bash
# Kill processes on ports
netstat -ano | findstr :8000
netstat -ano | findstr :3000
taskkill /PID <PID_NUMBER> /F
```

**Python/Node Not Found:**
- Install Python 3.8+ from https://python.org
- Install Node.js 16+ from https://nodejs.org
- Restart command prompt after installation

**Environment Variables:**
```bash
# Check if set
echo %01AGENT_API_URL%
echo %01AGENT_THREAD_ID%
echo %01AGENT_USER_ACCESS_TOKEN%
```

**Dependencies Issues:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
npm install --force
```

## 📊 Testing Checklist

- [ ] Backend starts without errors
- [ ] Frontend loads in browser
- [ ] API documentation accessible
- [ ] AI Agent connects to backend
- [ ] UI automation works
- [ ] Performance monitoring active

## 🎯 Key Features to Test

1. **Backend API**: Test endpoints at http://localhost:8000/docs
2. **Frontend UI**: Navigate through all pages
3. **AI Agent**: Check logs for successful startup
4. **Integration**: Verify frontend connects to backend
5. **Performance**: Monitor system resources
6. **Automation**: Test UI detection and interaction

## 📝 Logs Location

- **Backend**: Console output or backend.log
- **Frontend**: Browser console (F12)
- **AI Agent**: enhanced_agent.log
- **System**: Check Windows Event Viewer for errors

Your app is ready to test! 🎉