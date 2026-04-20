import asyncio, json, time, logging, os, sys, base64, mss, cv2, re
from typing import Dict, List, Optional, Any, Tuple
import aiohttp

try:
    from executor import executor
    from background_executor import background_executor
    from browser_automation import browser_automation
    from resource_monitor import ResourceMonitor
    from ocr_engine import ocr_engine
    from fast_capture import fast_capture
    from app_discovery import app_discovery
    from vision_producer import vision_producer
except ImportError as e:
    logging.error(f"Import error: {e}"); sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StreamingActionParser:
    """Greedily extracts JSON actions from a live LLM stream."""
    def __init__(self):
        self.buffer = ""
        self.yielded_count = 0

    def parse_and_yield(self, chunk: str):
        self.buffer += chunk
        match = re.search(r'"actions"\s*:\s*\[', self.buffer)
        if not match: return

        content = self.buffer[match.end():]
        depth = 0; obj_start = -1; found_objects = []
        for i, char in enumerate(content):
            if char == '{':
                if depth == 0: obj_start = i
                depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0 and obj_start != -1:
                    try:
                        found_objects.append(json.loads(content[obj_start:i+1]))
                    except: pass
                    obj_start = -1

        for obj in found_objects[self.yielded_count:]:
            self.yielded_count += 1
            yield obj

class EliteAgentEngine:
    """High-concurrency, low-latency agent engine (v2.2)."""
    def __init__(self):
        self.api_url = os.getenv('01AGENT_API_URL')
        self.thread_id = os.getenv('01AGENT_THREAD_ID')
        self.access_token = os.getenv('01AGENT_USER_ACCESS_TOKEN')
        self.resource_monitor = ResourceMonitor()
        self.session = None
        self.is_running = False
        self.local_cache = {}
        self.perf = {'latency': 0.2, 'cpu': 0, 'mem': 0}

    async def start(self):
        logger.info("🔥 Elite Engine v2.2 ACTIVE")
        try:
            vision_producer.start()
            await background_executor.start()
            await browser_automation.launch_browser()

            connector = aiohttp.TCPConnector(limit=100)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=600),
                headers={'Authorization': f'Bearer {self.access_token}'}
            )
            self.is_running = True
            await self._main_loop()
        except Exception as e:
            logger.error(f"Engine failure: {e}")
            await self.stop()

    async def stop(self):
        self.is_running = False
        vision_producer.is_running = False
        await background_executor.stop()
        await browser_automation.close_browser()
        if self.session: await self.session.close()

    async def _main_loop(self):
        asyncio.create_task(self._telemetry_loop())
        while self.is_running:
            try:
                ctx = vision_producer.get_latest()
                if not ctx:
                    await asyncio.sleep(0.1)
                    continue

                # Fetch subtask with minimal context
                subtask = await self._post_json("/current_subtask", ctx["sys_info"])
                if not subtask or subtask.get('action') == 'task_completed':
                    await asyncio.sleep(1.0)
                    continue

                await self._run_inference_loop(subtask)
            except Exception as e:
                logger.error(f"Main loop error: {e}")
                await asyncio.sleep(2.0)

    async def _run_inference_loop(self, subtask_info):
        last_results = None
        while self.is_running:
            ctx = vision_producer.get_latest()
            if not ctx:
                await asyncio.sleep(0.05)
                continue

            # Semantic Visual Cache Check
            cache_key = f"{ctx['sys_info']['active_window']}_{ctx['v_hash']}"
            if cache_key in self.local_cache and not last_results:
                logger.info(f"⚡ Cache Hit: {cache_key}")
                last_results = await asyncio.to_thread(executor.execute_actions, self.local_cache[cache_key].get('actions', []))
                await asyncio.sleep(0.5)
                continue

            payload = {
                **ctx["sys_info"],
                'screenshot_b64': ctx["b64"],
                'last_action_results': last_results,
                'ocr_grounding': ctx["ocr"][:50],
                'stream': True
            }
            
            start_req = time.time()
            try:
                async with self.session.post(f"{self.api_url}/aiagent/{self.thread_id}/next_step", json=payload) as r:
                    if r.status != 200: break

                    parser = StreamingActionParser()
                    executed_actions = []

                    async for chunk in r.content.iter_any():
                        chunk_str = chunk.decode('utf-8', errors='ignore')

                        for action in parser.parse_and_yield(chunk_str):
                            if action.get('params', {}).get('x') is not None:
                                executor.warp_mouse(action['params']['x'], action['params']['y'])

                            logger.info(f"Executing: {action.get('action')}")
                            print(json.dumps({"event": "action", "data": action}), flush=True)

                            # Parallel execution
                            last_results = await asyncio.to_thread(executor.execute_actions, [action])
                            executed_actions.append(action)

                    self.perf['latency'] = (self.perf['latency'] * 0.8) + ((time.time() - start_req) * 0.2)

                    # Update cache on success
                    if not last_results and executed_actions:
                        self.local_cache[cache_key] = {"actions": executed_actions}

                    if any(a.get('action') in ['subtask_completed', 'subtask_failed'] for a in executed_actions):
                        break
            except Exception as e:
                logger.error(f"Inference error: {e}")
                break

            await asyncio.to_thread(vision_producer.wait_for_change, timeout=0.1)

    async def _post_json(self, path, data):
        try:
            async with self.session.post(f"{self.api_url}/aiagent/{self.thread_id}{path}", json=data) as r:
                return await r.json() if r.status == 200 else None
        except: return None

    async def _telemetry_loop(self):
        while self.is_running:
            try:
                m = await self.resource_monitor.get_current_metrics()
                s = executor.get_system_state()
                self.perf['cpu'], self.perf['mem'] = m.cpu_percent, m.memory_percent
                print(json.dumps({
                    "event": "status",
                    "data": {
                        "cpu": m.cpu_percent,
                        "mem": m.memory_percent,
                        "latency": self.perf['latency'],
                        "win": s['active_window']
                    }
                }), flush=True)
                await asyncio.sleep(2.0)
            except: await asyncio.sleep(5.0)

if __name__ == "__main__":
    engine = EliteAgentEngine()
    asyncio.run(engine.start())
