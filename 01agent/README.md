# 01Agent Elite v2.2

## Performance Architecture
- **Thin Executor:** Decoupled `VisionProducer` (20 FPS) and `NativeExecutor` (Direct OS Bindings).
- **Streaming Action Pipeline:** Greedily executes JSON actions from LLM chunks to eliminate inference-wait latency.
- **Speculative Interaction:** Predicts mouse movement and prepares visual context using perceptual hashing (dHash).
- **Fast-Track Router:** Intelligent routing between Claude 3.7 Sonnet (Reasoning) and GPT-4o-mini for sub-second responses.

## Technical Stack
- **Backend:** FastAPI (Python) with high-concurrency streaming.
- **Frontend:** React (Enterprise UI) + Electron (Overlay Mode).
- **Execution:** Native OS injection (Win32/macOS Quartz/X11) bypassing standard library delays.

## Installation
```bash
cd 01agent/desktop/aiagent
pip install -r requirements.txt
playwright install
python main.py
```
