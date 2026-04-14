import asyncio
import json
import time
import logging
import os
import sys
from typing import Dict, List, Optional, Any, Tuple
import requests
import aiohttp
import mss
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO
import numpy as np

# Import our custom modules
try:
    from executor import executor
    from background_executor import background_executor
    from browser_automation import browser_automation
    from resource_monitor import ResourceMonitor, SystemMetrics
    from ocr_engine import ocr_engine
except ImportError as e:
    logging.error(f"Failed to import custom modules: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedAIAgent:
    """An AI agent that acts as a fast executor for the backend's brain."""
    
    def __init__(self):
        self.api_url = os.getenv('01AGENT_API_URL')
        self.thread_id = os.getenv('01AGENT_THREAD_ID')
        self.access_token = os.getenv('01AGENT_USER_ACCESS_TOKEN')
        
        if not all([self.api_url, self.thread_id, self.access_token]):
            logger.error("Missing required environment variables")
            sys.exit(1)
        
        # Initialize components
        self.resource_monitor = ResourceMonitor()
        self.session = None
        self.is_running = False
        self.task_history = []
        self.performance_metrics = {
            'total_tasks': 0,
            'successful_tasks': 0,
            'average_execution_time': 0.0,
            'fastest_execution': float('inf'),
            'slowest_execution': 0.0
        }
    
    async def start(self):
        """Start the AI agent."""
        logger.info("Starting Enhanced AI Agent...")
        try:
            await background_executor.start()
            await browser_automation.launch_browser()
            
            max_connections = 15
            connector = aiohttp.TCPConnector(limit=max_connections, limit_per_host=max_connections // 2, keepalive_timeout=30, enable_cleanup_closed=True)
            self.session = aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=300, connect=10), headers={'Authorization': f'Bearer {self.access_token}'})
            
            self.is_running = True
            logger.info("Enhanced AI Agent started successfully")
            await self._main_loop()
        except Exception as e:
            logger.error(f"Failed to start agent: {e}")
            await self.stop()
    
    async def stop(self):
        """Stop the AI agent."""
        logger.info("Stopping Enhanced AI Agent...")
        self.is_running = False
        await background_executor.stop()
        await browser_automation.close_browser()
        if self.session: await self.session.close()
        logger.info("Enhanced AI Agent stopped")
    
    async def _main_loop(self):
        """Main execution loop."""
        monitoring_task = asyncio.create_task(self._system_monitoring_loop())
        try:
            while self.is_running:
                try:
                    subtask_info = await self._get_current_subtask()
                    if not subtask_info:
                        await asyncio.sleep(1.0)
                        continue
                    if subtask_info.get('action') == 'task_completed':
                        logger.info("All tasks completed")
                        break
                    await self._execute_subtask(subtask_info)
                    await asyncio.sleep(0.1)
                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                    await asyncio.sleep(2.0)
        finally:
            monitoring_task.cancel()
            try: await monitoring_task
            except asyncio.CancelledError: pass
    
    async def _system_monitoring_loop(self):
        """Continuous system monitoring loop."""
        while self.is_running:
            try:
                metrics = await self.resource_monitor.get_current_metrics()
                os_state = executor.get_system_state()
                status_update = {
                    "event": "status",
                    "data": {
                        "cpu": metrics.cpu_percent,
                        "memory": metrics.memory_percent,
                        "active_window": os_state.get('active_window'),
                        "timestamp": time.time()
                    }
                }
                print(json.dumps(status_update), flush=True)
                await asyncio.sleep(2.0)
            except Exception as e:
                logger.error(f"Error in system monitoring: {e}")
                await asyncio.sleep(5.0)
    
    async def _get_current_subtask(self) -> Optional[Dict[str, Any]]:
        """Get the current subtask from the backend."""
        try:
            system_info = await self._get_system_info()
            url = f"{self.api_url}/aiagent/{self.thread_id}/current_subtask"
            async with self.session.post(url, json=system_info) as response:
                if response.status == 200: return await response.json()
                else: return None
        except Exception as e:
            logger.error(f"Error getting current subtask: {e}")
            return None
    
    async def _execute_subtask(self, subtask_info: Dict[str, Any]):
        """Execute a subtask by communicating with the backend's brain."""
        subtask_id = subtask_info.get('id')
        subtask_text = subtask_info.get('subtask_text', '')
        logger.info(f"Starting subtask {subtask_id}: {subtask_text}")

        last_results = None
        while self.is_running:
            start_time = time.time()
            screenshot_img, screenshot_b64 = await self._take_screenshot_with_image()
            if not screenshot_img: break

            # Local OCR grounding for perfect text awareness
            ocr_grounding = ocr_engine.get_text_coordinates(screenshot_img)
            
            response_data = await self._get_next_step_from_backend(screenshot_b64, last_results, ocr_grounding)
            if not response_data: break

            actions = response_data.get('actions', [])
            is_completed = any(a.get('action') == 'subtask_completed' for a in actions)
            is_failed = any(a.get('action') == 'subtask_failed' for a in actions)
            
            for action in actions:
                print(json.dumps({"event": "action", "data": action}), flush=True)
            
            last_results = executor.execute_actions(actions)
            execution_time = time.time() - start_time
            self._update_performance_metrics(execution_time, not is_failed)
            
            if is_completed or is_failed: break
            await asyncio.sleep(0.5)

    async def _get_next_step_from_backend(self, screenshot_b64: str, last_results: List[Dict] = None, ocr_grounding: List[Dict] = None) -> Optional[Dict[str, Any]]:
        """Get the next actions from the backend."""
        try:
            url = f"{self.api_url}/aiagent/{self.thread_id}/next_step"
            system_info = await self._get_system_info()
            payload = {
                **system_info,
                'screenshot_b64': screenshot_b64,
                'last_action_results': last_results,
                'ocr_grounding': ocr_grounding[:50] if ocr_grounding else []
            }
            async with self.session.post(url, json=payload) as response:
                if response.status == 200: return await response.json()
                else: return None
        except Exception as e:
            logger.error(f"Error calling backend: {e}")
            return None
    
    async def _get_system_info(self) -> Dict[str, Any]:
        """Get current system information."""
        try:
            running_apps = []
            import psutil
            for proc in psutil.process_iter(['pid', 'name']):
                try: running_apps.append({'name': proc.info['name'], 'pid': proc.info['pid']})
                except: pass
            
            os_state = executor.get_system_state()
            return {
                'current_os': os.name,
                'current_interactive_elements': [],
                'current_running_apps': running_apps[:20],
                'active_window': os_state.get('active_window'),
                'open_windows': os_state.get('open_windows', [])[:15],
                'clipboard': os_state.get('clipboard_content')
            }
        except Exception:
            return {'current_os': os.name}

    async def _take_screenshot_with_image(self) -> Tuple[Optional[Image.Image], str]:
        """Takes screenshot, returns (PIL Image, Base64 String)."""
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)
                original_img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                
                # Add visual grid for better AI grounding
                grounded_img = self._add_visual_grid(original_img.copy())
                grounded_img = grounded_img.resize((1280, 720), Image.Resampling.LANCZOS)
                
                buffer = BytesIO()
                grounded_img.save(buffer, format="JPEG", quality=75, optimize=True)
                screenshot_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                return original_img, screenshot_b64
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return None, ""

    def _add_visual_grid(self, img: Image) -> Image:
        """Adds a subtle numbered grid to the image."""
        draw = ImageDraw.Draw(img)
        width, height = img.size
        grid_size = 100
        line_color = (0, 255, 136, 60)
        for x in range(0, width, grid_size):
            draw.line([(x, 0), (x, height)], fill=line_color, width=1)
            if x % 200 == 0: draw.text((x + 5, 5), str(x), fill=line_color)
        for y in range(0, height, grid_size):
            draw.line([(0, y), (width, y)], fill=line_color, width=1)
            if y % 200 == 0: draw.text((5, y + 5), str(y), fill=line_color)
        return img

    def _update_performance_metrics(self, execution_time: float, success: bool):
        self.performance_metrics['total_tasks'] += 1
        if success: self.performance_metrics['successful_tasks'] += 1
        total_time = (self.performance_metrics['average_execution_time'] * (self.performance_metrics['total_tasks'] - 1) + execution_time)
        self.performance_metrics['average_execution_time'] = total_time / self.performance_metrics['total_tasks']
        if execution_time < self.performance_metrics['fastest_execution']: self.performance_metrics['fastest_execution'] = execution_time
        if execution_time > self.performance_metrics['slowest_execution']: self.performance_metrics['slowest_execution'] = execution_time

    def get_performance_stats(self) -> Dict[str, Any]:
        success_rate = (self.performance_metrics['successful_tasks'] / max(self.performance_metrics['total_tasks'], 1))
        return {**self.performance_metrics, 'success_rate': success_rate, 'recent_tasks': len(self.task_history)}

async def main():
    agent = EnhancedAIAgent()
    try: await agent.start()
    except KeyboardInterrupt: logger.info("Interrupt")
    except Exception as e: logger.error(f"Error: {e}")
    finally: await agent.stop()

if __name__ == "__main__":
    asyncio.run(main())
