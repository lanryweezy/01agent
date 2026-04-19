import asyncio, json, time, logging, os, sys, base64, mss, cv2
from typing import Dict, List, Optional, Any, Tuple
import aiohttp
from PIL import Image
from io import BytesIO
import numpy as np

try:
    from executor import executor
    from background_executor import background_executor
    from browser_automation import browser_automation
    from resource_monitor import ResourceMonitor
    from ocr_engine import ocr_engine
    from fast_capture import fast_capture
except ImportError as e:
    logging.error(f"Import error: {e}"); sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedAIAgent:
    def __init__(self):
        self.api_url = os.getenv('01AGENT_API_URL')
        self.thread_id = os.getenv('01AGENT_THREAD_ID')
        self.access_token = os.getenv('01AGENT_USER_ACCESS_TOKEN')
        if not all([self.api_url, self.thread_id, self.access_token]): sys.exit(1)
        self.resource_monitor = ResourceMonitor()
        self.session = None
        self.is_running = False
        self.performance_metrics = {'total_tasks': 0, 'successful_tasks': 0, 'average_execution_time': 0.0, 'fastest_execution': float('inf'), 'slowest_execution': 0.0}

    async def start(self):
        logger.info("Starting Agent...")
        try:
            await background_executor.start(); await browser_automation.launch_browser()
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=300), headers={'Authorization': f'Bearer {self.access_token}'})
            self.is_running = True; await self._main_loop()
        except Exception as e: logger.error(f"Start failed: {e}"); await self.stop()

    async def stop(self):
        self.is_running = False; await background_executor.stop(); await browser_automation.close_browser()
        if self.session: await self.session.close()

    async def _main_loop(self):
        asyncio.create_task(self._system_monitoring_loop())
        while self.is_running:
            try:
                sys_info = await self._get_system_info()
                subtask = await self._get_current_subtask(sys_info)
                if not subtask: await asyncio.sleep(1.0); continue
                if subtask.get('action') == 'task_completed': break
                await self._execute_subtask(subtask); await asyncio.sleep(0.1)
            except Exception as e: logger.error(f"Loop error: {e}"); await asyncio.sleep(2.0)

    async def _system_monitoring_loop(self):
        while self.is_running:
            try:
                m = await self.resource_monitor.get_current_metrics()
                s = await asyncio.to_thread(executor.get_system_state)
                print(json.dumps({"event": "status", "data": {"cpu": m.cpu_percent, "memory": m.memory_percent, "active_window": s.get('active_window'), "timestamp": time.time()}}), flush=True)
                await asyncio.sleep(2.0)
            except Exception: await asyncio.sleep(5.0)

    async def _get_current_subtask(self, sys_info):
        try:
            async with self.session.post(f"{self.api_url}/aiagent/{self.thread_id}/current_subtask", json=sys_info) as r:
                return await r.json() if r.status == 200 else None
        except Exception: return None

    async def _execute_subtask(self, info):
        tid = info.get('id'); last_results = None
        complexity_score = 0
        while self.is_running:
            start = time.time()
            m = await self.resource_monitor.get_current_metrics()
            
            # 1. Parallel Context Gathering
            q = 50 if m.cpu_percent > 85 else 85 if m.cpu_percent < 30 else 75
            target_res = (1920, 1080) if complexity_score > 5 else (1280, 720)
            
            # Run Capture, System State, and Resource Monitoring in parallel
            capture_task = asyncio.to_thread(fast_capture.capture_fast, quality=q, target_size=target_res)
            sys_info_task = self._get_system_info()
            
            (img_np, b64), sys_info = await asyncio.gather(capture_task, sys_info_task)
            
            # OCR is dependent on the image
            ocr = await asyncio.to_thread(ocr_engine.get_text_coordinates, Image.fromarray(cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)))
            
            # 2. Get Next Step
            resp = await self._get_next_step(sys_info, b64, last_results, ocr)
            if not resp: break
            
            if resp.get('_thinking'):
                print(json.dumps({"event": "thinking", "data": resp.get('_thinking')}), flush=True)

            actions = resp.get('actions', [])
            for a in actions: print(json.dumps({"event": "action", "data": a}), flush=True)
            
            # 3. Parallel Action Execution (if multiple independent actions returned)
            last_results = await asyncio.to_thread(executor.execute_actions, actions)
            
            # Adjust complexity score based on response
            if resp.get('_thinking') and len(resp.get('_thinking')) > 500:
                complexity_score += 1
            else:
                complexity_score = max(0, complexity_score - 1)

            self._update_metrics(time.time() - start, not any(a.get('action') == 'subtask_failed' for a in actions))
            if any(a.get('action') in ['subtask_completed', 'subtask_failed'] for a in actions): break
            await asyncio.sleep(0.5)

    async def _get_next_step(self, sys_info, b64, results, ocr):
        try:
            p = {**sys_info, 'screenshot_b64': b64, 'last_action_results': results, 'ocr_grounding': ocr[:50]}
            async with self.session.post(f"{self.api_url}/aiagent/{self.thread_id}/next_step", json=p) as r:
                return await r.json() if r.status == 200 else None
        except Exception: return None

    async def _get_system_info(self):
        s = await asyncio.to_thread(executor.get_system_state)
        monitors = fast_capture.get_monitors()
        
        # Deep Browser Context
        browser_tree = None
        if "chrome" in (s.get('active_window') or "").lower():
            browser_tree = await browser_automation.get_accessibility_tree()

        return {
            'current_os': os.name,
            'current_running_apps': [],
            'active_window': s.get('active_window'),
            'open_windows': s.get('open_windows', [])[:15],
            'clipboard': s.get('clipboard_content'),
            'monitors': monitors,
            'browser_accessibility_tree': browser_tree
        }

    def _update_metrics(self, t, s):
        self.performance_metrics['total_tasks'] += 1
        if s: self.performance_metrics['successful_tasks'] += 1
        self.performance_metrics['average_execution_time'] = (self.performance_metrics['average_execution_time'] * (self.performance_metrics['total_tasks'] - 1) + t) / self.performance_metrics['total_tasks']

async def main():
    agent = EnhancedAIAgent()
    try: await agent.start()
    except KeyboardInterrupt: pass
    finally: await agent.stop()

if __name__ == "__main__": asyncio.run(main())
