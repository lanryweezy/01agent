import asyncio
import json
import time
import logging
import os
import sys
from typing import Dict, List, Optional, Any
import requests
import aiohttp
import mss
from PIL import Image
import base64
from io import BytesIO


# Import our custom modules
try:
    from executor import executor
    from background_executor import background_executor
    from browser_automation import browser_automation
    from resource_monitor import ResourceMonitor, SystemMetrics
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
            # Start background systems
            await background_executor.start()
            logger.info("Background executor started")
            
            # Launch browser automation
            await browser_automation.launch_browser()
            logger.info("Browser automation launched")
            
            # Create HTTP session with optimized settings
            max_connections = 15
            connector = aiohttp.TCPConnector(
                limit=max_connections,
                limit_per_host=max_connections // 2,
                keepalive_timeout=30,
                enable_cleanup_closed=True
            )
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=300, connect=10),
                headers={'Authorization': f'Bearer {self.access_token}'}
            )
            
            self.is_running = True
            logger.info("Enhanced AI Agent started successfully")
            
            # Start main execution loop
            await self._main_loop()
            
        except Exception as e:
            logger.error(f"Failed to start agent: {e}")
            await self.stop()
    
    async def stop(self):
        """Stop the AI agent."""
        logger.info("Stopping Enhanced AI Agent...")
        
        self.is_running = False
        
        # Stop all systems
        await background_executor.stop()
        await browser_automation.close_browser()
        
        # Close HTTP session
        if self.session:
            await self.session.close()
        
        logger.info("Enhanced AI Agent stopped")
    
    async def _main_loop(self):
        """Main execution loop."""
        # Start system monitoring task
        monitoring_task = asyncio.create_task(self._system_monitoring_loop())
        
        try:
            while self.is_running:
                try:
                    # Get current subtask
                    subtask_info = await self._get_current_subtask()
                    
                    if not subtask_info:
                        await asyncio.sleep(1.0)
                        continue
                    
                    if subtask_info.get('action') == 'task_completed':
                        logger.info("All tasks completed")
                        break
                    
                    # Execute the subtask
                    await self._execute_subtask(subtask_info)
                    
                    # Minimal delay to prevent CPU spinning
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                    await asyncio.sleep(2.0)
        finally:
            # Stop monitoring
            monitoring_task.cancel()
            try:
                await monitoring_task
            except asyncio.CancelledError:
                pass
    
    async def _system_monitoring_loop(self):
        """Continuous system monitoring loop."""
        while self.is_running:
            try:
                # Get current system metrics
                await self.resource_monitor.get_current_metrics()
                # Monitor every 5 seconds
                await asyncio.sleep(5.0)
            except Exception as e:
                logger.error(f"Error in system monitoring: {e}")
                await asyncio.sleep(5.0)
    
    async def _get_current_subtask(self) -> Optional[Dict[str, Any]]:
        """Get the current subtask from the backend."""
        try:
            # Get system information
            system_info = await self._get_system_info()
            
            # Make request to backend
            url = f"{self.api_url}/aiagent/{self.thread_id}/current_subtask"
            
            async with self.session.post(url, json=system_info) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to get subtask: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting current subtask: {e}")
            return None
    
    async def _execute_subtask(self, subtask_info: Dict[str, Any]):
        """Execute a subtask by communicating with the backend's brain."""
        subtask_id = subtask_info.get('id')
        subtask_text = subtask_info.get('subtask_text', '')
        
        logger.info(f"Starting subtask {subtask_id}: {subtask_text}")

        while self.is_running:
            start_time = time.time()
            
            # Take screenshot for the AI model
            screenshot_b64 = await self._take_screenshot_optimized()
            
            # Get next steps from backend
            response_data = await self._get_next_step_from_backend(screenshot_b64)
            
            if not response_data:
                logger.error("Failed to get response from backend")
                break

            actions = response_data.get('actions', [])
            
            # Check for terminal actions
            is_completed = any(a.get('action') == 'subtask_completed' for a in actions)
            is_failed = any(a.get('action') == 'subtask_failed' for a in actions)
            
            # Execute actions
            executor.execute_actions(actions)
            
            # Update performance metrics
            execution_time = time.time() - start_time
            self._update_performance_metrics(execution_time, not is_failed)
            
            if is_completed:
                logger.info(f"Subtask {subtask_id} completed successfully")
                break
            
            if is_failed:
                logger.warning(f"Subtask {subtask_id} failed")
                break

            # Small delay between steps to allow UI to settle
            await asyncio.sleep(0.5)

    async def _get_next_step_from_backend(self, screenshot_b64: str) -> Optional[Dict[str, Any]]:
        """Get the next actions from the backend."""
        try:
            url = f"{self.api_url}/aiagent/{self.thread_id}/next_step"
            
            system_info = await self._get_system_info()
            payload = {
                **system_info,
                'screenshot_b64': screenshot_b64
            }
            
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Backend error: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error calling backend: {e}")
            return None
    
    async def _get_system_info(self) -> Dict[str, Any]:
        """Get current system information."""
        try:
            # Get running applications (simplified)
            running_apps = []
            try:
                import psutil
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        running_apps.append({
                            'name': proc.info['name'],
                            'pid': proc.info['pid']
                        })
                    except:
                        pass
            except:
                pass
            
            # Get window management info
            os_state = executor.get_system_state()

            return {
                'current_os': os.name,
                'current_interactive_elements': [],  # Simplified for speed
                'current_running_apps': running_apps[:20],
                'active_window': os_state.get('active_window'),
                'open_windows': os_state.get('open_windows', [])[:15]
            }
            
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {
                'current_os': os.name,
                'current_interactive_elements': [],
                'current_running_apps': []
            }
    
    async def _take_screenshot_optimized(self) -> str:
        """Take an optimized screenshot and return as base64."""
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)
                
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

                # Optimize size
                img = img.resize((1280, 720), Image.Resampling.LANCZOS)
                
                # Convert to base64 with optimization
                buffer = BytesIO()
                img.save(buffer, format="JPEG", quality=75, optimize=True) # JPEG 75% for balance of speed/quality
                screenshot_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                return screenshot_b64
                
        except Exception as e:
            logger.error(f"Error taking optimized screenshot: {e}")
            return ""
    
    async def _save_screenshot_fast(self) -> str:
        """Save a screenshot quickly to desktop and return path."""
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

                # Save to desktop
                desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
                os.makedirs(desktop, exist_ok=True)

                filename = f"screenshot_{int(time.time())}.png"
                filepath = os.path.join(desktop, filename)

                img.save(filepath, format="PNG", optimize=True)
                return filepath
                
        except Exception as e:
            logger.error(f"Error saving fast screenshot: {e}")
            return ""
    
    def _update_performance_metrics(self, execution_time: float, success: bool):
        """Update performance metrics."""
        self.performance_metrics['total_tasks'] += 1
        
        if success:
            self.performance_metrics['successful_tasks'] += 1
        
        # Update execution time metrics
        total_time = (self.performance_metrics['average_execution_time'] * 
                     (self.performance_metrics['total_tasks'] - 1) + execution_time)
        self.performance_metrics['average_execution_time'] = total_time / self.performance_metrics['total_tasks']
        
        if execution_time < self.performance_metrics['fastest_execution']:
            self.performance_metrics['fastest_execution'] = execution_time
        
        if execution_time > self.performance_metrics['slowest_execution']:
            self.performance_metrics['slowest_execution'] = execution_time
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get basic performance statistics."""
        success_rate = (self.performance_metrics['successful_tasks'] / 
                       max(self.performance_metrics['total_tasks'], 1))
        
        return {
            **self.performance_metrics,
            'success_rate': success_rate,
            'recent_tasks': len(self.task_history),
        }


async def main():
    """Main entry point."""
    agent = EnhancedAIAgent()
    
    try:
        await agent.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        await agent.stop()

if __name__ == "__main__":
    asyncio.run(main())
