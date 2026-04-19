# 01Agent v2.0

## High-Performance AI Desktop Assistant

### Features
- **Thin Executor Architecture**: Sub-50ms screen capture and low-latency execution.
- **Superior Cloud Models**: Defaulting to Claude 3.7 Sonnet (Reasoning) and GPT-4o.
- **Proactive Intelligence**: Suggestor agent for real-time task recommendations.
- **Skill Marketplace**: Discover and install community-built automations.
- **Self-Healing**: Automated subtask retries for resilient execution.
- **Visual Feedback**: Real-time thinking and action markers on desktop overlay.
- **Multi-Monitor Support**: Enumerates and reports all connected displays.

### Setup
1. Backend: `cd backend && pip install -r requirements.txt && alembic upgrade head && uvicorn main:app`
2. Desktop App: `cd desktop && npm install && cd 01agent-app && npm install && npm run build`
3. Start Electron: `cd desktop && npm start`

MIT License.
