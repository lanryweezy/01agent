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
                subtask = await self._get_current_subtask()
                if not subtask: await asyncio.sleep(1.0); continue
                if subtask.get('action') == 'task_completed': break
                await self._execute_subtask(subtask); await asyncio.sleep(0.1)
            except Exception as e: logger.error(f"Loop error: {e}"); await asyncio.sleep(2.0)

    async def _system_monitoring_loop(self):
        while self.is_running:
            try:
                m = await self.resource_monitor.get_current_metrics()
                s = executor.get_system_state()
                print(json.dumps({"event": "status", "data": {"cpu": m.cpu_percent, "memory": m.memory_percent, "active_window": s.get('active_window'), "timestamp": time.time()}}), flush=True)
                await asyncio.sleep(2.0)
            except Exception: await asyncio.sleep(5.0)

    async def _get_current_subtask(self):
        try:
            async with self.session.post(f"{self.api_url}/aiagent/{self.thread_id}/current_subtask", json=await self._get_system_info()) as r:
                return await r.json() if r.status == 200 else None
        except Exception: return None

    async def _execute_subtask(self, info):
        tid = info.get('id'); last_results = None
        while self.is_running:
            start = time.time()
            m = await self.resource_monitor.get_current_metrics()
            q = 50 if m.cpu_percent > 85 else 85 if m.cpu_percent < 30 else 75
            img_np, b64 = fast_capture.capture_fast(quality=q)
            ocr = ocr_engine.get_text_coordinates(Image.fromarray(cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)))
            resp = await self._get_next_step(b64, last_results, ocr)
            if not resp: break
            actions = resp.get('actions', [])
            for a in actions: print(json.dumps({"event": "action", "data": a}), flush=True)
            last_results = executor.execute_actions(actions)
            self._update_metrics(time.time() - start, not any(a.get('action') == 'subtask_failed' for a in actions))
            if any(a.get('action') in ['subtask_completed', 'subtask_failed'] for a in actions): break
            await asyncio.sleep(0.5)

    async def _get_next_step(self, b64, results, ocr):
        try:
            p = {**await self._get_system_info(), 'screenshot_b64': b64, 'last_action_results': results, 'ocr_grounding': ocr[:50]}
            async with self.session.post(f"{self.api_url}/aiagent/{self.thread_id}/next_step", json=p) as r:
                return await r.json() if r.status == 200 else None
        except Exception: return None

    async def _get_system_info(self):
        s = executor.get_system_state()
        return {'current_os': os.name, 'current_running_apps': [], 'active_window': s.get('active_window'), 'open_windows': s.get('open_windows', [])[:15], 'clipboard': s.get('clipboard_content')}

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
