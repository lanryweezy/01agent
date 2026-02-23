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
    from ai_executor import ai_executor
    from terminal_controller import terminal_controller
    from background_executor import background_executor, ScriptType
    from fast_ui_detector import fast_ui_detector
    from performance_optimizer import performance_optimizer
    from config_manager import config_manager
    from performance_dashboard import performance_dashboard, TaskMetrics, SystemSnapshot
    from integration_optimizer import integration_optimizer
    from browser_automation import browser_automation
    from resource_monitor import ResourceMonitor, SystemMetrics, check_gpu_availability
    from task_manager import TaskPrioritizer, PerformanceCache
    from ollama_monitor import OllamaHealthMonitor
    from action_scheduler import ActionScheduler
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
    """An AI agent that uses a multimodal model to interact with the OS."""
    
    def __init__(self):
        
        self.api_url = os.getenv('01AGENT_API_URL')
        self.thread_id = os.getenv('01AGENT_THREAD_ID')
        self.access_token = os.getenv('01AGENT_USER_ACCESS_TOKEN')
        
        if not all([self.api_url, self.thread_id, self.access_token]):
            logger.error("Missing required environment variables")
            sys.exit(1)
        
        # Initialize enhanced components
        self.resource_monitor = ResourceMonitor()
        self.task_prioritizer = TaskPrioritizer()
        self.performance_cache = PerformanceCache()
        self.ollama_monitor = OllamaHealthMonitor()
        self.action_scheduler = ActionScheduler()
        
        # Performance tracking
        self.execution_metrics = []
        self.last_performance_check = 0
        
        # Load optimized configuration
        self.config = config_manager.get_config()
        logger.info(f"Loaded configuration: {self.config.config_version}")
        
        # Auto-optimize configuration for current system
        config_manager.auto_optimize_for_system()
        self.config = config_manager.get_config()  # Reload after optimization
        
                
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
        """Start the enhanced AI agent."""
        logger.info("Starting Enhanced AI Agent...")
        
        try:
            # Apply comprehensive integration optimizations
            optimization_results = await integration_optimizer.optimize_all_integrations()
            logger.info(f"Integration optimization completed: {len(optimization_results['optimizations_applied'])} optimizations applied")
            
            if optimization_results['errors']:
                logger.warning(f"Integration optimization errors: {optimization_results['errors']}")
            if optimization_results['warnings']:
                logger.info(f"Integration optimization warnings: {optimization_results['warnings']}")
            
            # Start performance optimization
            await performance_optimizer.start_monitoring()
            await performance_optimizer.optimize_for_speed()
            logger.info("Performance optimizer started")
            
            # Start background systems
            await background_executor.start()
            logger.info("Background executor started")
            
            # Launch browser automation
            await browser_automation.launch_browser()
            logger.info("Browser automation launched")
            
            # Initialize terminal controller
            logger.info("Terminal controller initialized")
            
            # Initialize fast UI detector with optimized settings
            fast_ui_detector.set_screenshot_scale(self.config.performance.screenshot_scale)
            fast_ui_detector.set_cache_timeout(self.config.performance.cache_timeout)
            logger.info(f"Fast UI detector initialized with scale={self.config.performance.screenshot_scale}, cache={self.config.performance.cache_timeout}s")
            
            # Create HTTP session with configuration-optimized settings
            max_connections = min(self.config.performance.max_concurrent_tasks, 15)
            connector = aiohttp.TCPConnector(
                limit=max_connections,
                limit_per_host=max_connections // 2,
                keepalive_timeout=30,
                enable_cleanup_closed=True
            )
            
            timeout_total = self.config.execution.terminal_timeout
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=timeout_total, connect=5),
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
        """Stop the enhanced AI agent."""
        logger.info("Stopping Enhanced AI Agent...")
        
        self.is_running = False
        
        # Stop all systems
        await background_executor.stop()
        await performance_optimizer.stop_monitoring()
        await fast_ui_detector.cleanup()
        await browser_automation.close_browser()
        
        # Close HTTP session
        if self.session:
            await self.session.close()
        
        # Restore original system settings
        await performance_optimizer.restore_original_settings()
        
        logger.info("Enhanced AI Agent stopped")
    
    async def _main_loop(self):
        """Main execution loop with integrated monitoring."""
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
                    
                    # Adaptive delay based on system performance
                    delay = self._calculate_adaptive_delay()
                    await asyncio.sleep(delay)
                    
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
                current_metrics = await performance_optimizer.get_current_metrics()
                
                if current_metrics:
                    # Record system snapshot
                    snapshot = SystemSnapshot(
                        timestamp=time.time(),
                        cpu_percent=current_metrics.cpu_percent,
                        memory_percent=current_metrics.memory_percent,
                        disk_io_read=current_metrics.disk_io.get('read_rate', 0),
                        disk_io_write=current_metrics.disk_io.get('write_rate', 0),
                        network_io_sent=current_metrics.network_io.get('send_rate', 0),
                        network_io_recv=current_metrics.network_io.get('recv_rate', 0),
                        active_tasks=len(background_executor.running_tasks),
                        queue_size=background_executor.task_queue.qsize()
                    )
                    performance_dashboard.record_system_snapshot(snapshot)
                
                # Check for performance issues and auto-adjust
                # await self._auto_adjust_performance() # Removed as part of refactoring
                
                # Monitor every 2 seconds
                await asyncio.sleep(2.0)
                
            except Exception as e:
                logger.error(f"Error in system monitoring: {e}")
                await asyncio.sleep(5.0)
    
    def _calculate_adaptive_delay(self) -> float:
        """Calculate adaptive delay based on current system performance."""
        try:
            current_metrics = performance_optimizer.get_current_metrics()
            if not current_metrics:
                return 0.1
            
            # Base delay
            base_delay = 0.05
            
            # Adjust based on CPU load
            if current_metrics.cpu_percent > 90:
                base_delay *= 3.0
            elif current_metrics.cpu_percent > 80:
                base_delay *= 2.0
            elif current_metrics.cpu_percent > 70:
                base_delay *= 1.5
            
            # Adjust based on memory load
            if current_metrics.memory_percent > 95:
                base_delay *= 2.5
            elif current_metrics.memory_percent > 85:
                base_delay *= 1.8
            
            # Adjust based on recent task performance
            recent_stats = performance_dashboard.get_real_time_stats()
            if recent_stats:
                success_rate = recent_stats.get('success_rate', 1.0)
                if success_rate < 0.7:
                    base_delay *= 1.5  # Slow down if many failures
            
            return min(max(base_delay, 0.01), 2.0)  # Clamp between 10ms and 2s
            
        except Exception as e:
            logger.error(f"Error calculating adaptive delay: {e}")
            return 0.1
    

    
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
        """Execute a subtask using the new AI executor."""
        start_time = time.time()
        
        try:
            subtask_text = subtask_info.get('subtask_text', '')
            subtask_id = subtask_info.get('id')
            
            logger.info(f"Executing subtask {subtask_id} with AI executor: {subtask_text}")
            
            # Quick performance check and optimization
            current_metrics = performance_optimizer.get_current_metrics()
            if current_metrics and (current_metrics.cpu_percent > 90 or current_metrics.memory_percent > 90):
                await performance_optimizer.quick_cleanup()
                logger.info("Performed quick cleanup due to high resource usage")

            # Take screenshot for the AI model
            screenshot_b64 = await self._take_screenshot_optimized()
            
            # Analyze screen context for better execution (can still be useful)
            screen_analysis = await fast_ui_detector.analyze_screen_fast()
            
            # Create enhanced context for the AI executor
            context = {
                'screen_analysis': screen_analysis,
                'performance_metrics': current_metrics,
                'screenshot_b64': screenshot_b64
            }
            
            # Execute task with the new AI executor
            result = await ai_executor.execute_task(subtask_text, context)
            
            # Send result to backend
            await self._send_next_step(result, screenshot_b64)
            
            # Update performance metrics
            execution_time = time.time() - start_time
            success = result.get('success', False)
            method = result.get('method', 'unknown')
            
            self._update_performance_metrics(execution_time, success)
            
            # Record task metrics in performance dashboard
            task_metrics = TaskMetrics(
                task_id=str(subtask_id),
                task_description=subtask_text[:100],  # Truncate for storage
                execution_method=method,
                execution_time=execution_time,
                success=success,
                timestamp=time.time(),
                error_message=result.get('error') if not success else None,
                system_load_cpu=current_metrics.cpu_percent if current_metrics else None,
                system_load_memory=current_metrics.memory_percent if current_metrics else None
            )
            performance_dashboard.record_task_execution(task_metrics)
            
            # Add to task history with enhanced info
            self.task_history.append({
                'subtask_id': subtask_id,
                'subtask_text': subtask_text,
                'execution_time': execution_time,
                'success': success,
                'method': method,
                'context': context,
                'timestamp': time.time()
            })
            
            # Keep only recent history
            if len(self.task_history) > 50:
                self.task_history.pop(0)
            
        except Exception as e:
            logger.error(f"Error executing subtask: {e}")
            
            # Send error to backend
            await self._send_next_step({
                'success': False,
                'error': str(e),
                'method': 'error'
            }, await self._take_screenshot_optimized())
    

    

    
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
            
            # Get interactive elements (simplified)
            interactive_elements = []
            
            return {
                'current_os': os.name,
                'current_interactive_elements': interactive_elements[:10],  # Limit to prevent large payloads
                'current_running_apps': running_apps[:20]  # Limit to prevent large payloads
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
            # Use fast UI detector's optimized screenshot method
            screenshot_array = await fast_ui_detector.take_fast_screenshot()
            
            if screenshot_array.size == 0:
                return await self._take_screenshot_fallback()
            
            # Convert numpy array to PIL Image
            img = Image.fromarray(screenshot_array)
            
            # Optimize size based on system performance
            current_metrics = performance_optimizer.get_current_metrics()
            if current_metrics and current_metrics.memory_percent > 80:
                # Use smaller size under memory pressure
                img = img.resize((960, 540), Image.Resampling.LANCZOS)
            else:
                # Standard size
                img = img.resize((1280, 720), Image.Resampling.LANCZOS)
            
            # Convert to base64 with optimization
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=85, optimize=True)  # JPEG for smaller size
            screenshot_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return screenshot_b64
                
        except Exception as e:
            logger.error(f"Error taking optimized screenshot: {e}")
            return await self._take_screenshot_fallback()
    
    async def _take_screenshot_fallback(self) -> str:
        """Fallback screenshot method."""
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)
                
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                img = img.resize((1280, 720), Image.Resampling.LANCZOS)
                
                buffer = BytesIO()
                img.save(buffer, format="PNG", optimize=True)
                screenshot_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                return screenshot_b64
                
        except Exception as e:
            logger.error(f"Error in fallback screenshot: {e}")
            return ""
    
    async def _save_screenshot_fast(self) -> str:
        """Save a screenshot quickly to desktop and return path."""
        try:
            # Use fast UI detector for screenshot
            screenshot_array = await fast_ui_detector.take_fast_screenshot()
            
            if screenshot_array.size == 0:
                return ""
            
            # Convert to PIL Image
            img = Image.fromarray(screenshot_array)
            
            # Save to desktop
            desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
            os.makedirs(desktop, exist_ok=True)
            
            filename = f"screenshot_{int(time.time())}.png"
            filepath = os.path.join(desktop, filename)
            
            # Save with optimization
            img.save(filepath, format="PNG", optimize=True)
            
            return filepath
                
        except Exception as e:
            logger.error(f"Error saving fast screenshot: {e}")
            return ""
    

    
    async def _send_next_step(self, result: Dict[str, Any], screenshot_b64: str):
        """Send the next step result to the backend."""
        try:
            url = f"{self.api_url}/aiagent/{self.thread_id}/next_step"
            
            payload = {
                **await self._get_system_info(),
                'screenshot_b64': screenshot_b64,
                'result': result
            }
            
            async with self.session.post(url, json=payload) as response:
                if response.status != 200:
                    logger.error(f"Failed to send next step: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error sending next step: {e}")
    
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
        """Get comprehensive performance statistics."""
        success_rate = (self.performance_metrics['successful_tasks'] / 
                       max(self.performance_metrics['total_tasks'], 1))
        
        # Get dashboard summary
        dashboard_summary = performance_dashboard.get_dashboard_summary()
        
        # Get method performance comparison
        method_comparison = performance_dashboard.get_method_performance_comparison()
        
        # Get system performance
        system_performance = performance_optimizer.get_performance_summary()
        
        # Get configuration info
        config_info = {
            'screenshot_scale': self.config.performance.screenshot_scale,
            'cache_timeout': self.config.performance.cache_timeout,
            'max_concurrent_tasks': self.config.performance.max_concurrent_tasks,
            'fast_mode': self.config.performance.fast_mode,
            'default_strategy': self.config.execution.default_strategy
        }
        
        return {
            # Basic metrics
            **self.performance_metrics,
            'success_rate': success_rate,
            'current_strategy': self.current_strategy,
            'recent_tasks': len(self.task_history),
            
            # Dashboard metrics
            'dashboard_status': dashboard_summary.get('current_status', 'unknown'),
            'recent_success_rate': dashboard_summary.get('success_rate', 0.0),
            'recent_avg_execution_time': dashboard_summary.get('avg_execution_time', 0.0),
            
            # System metrics
            'system_performance': system_performance,
            'system_cpu': dashboard_summary.get('system_cpu', 0.0),
            'system_memory': dashboard_summary.get('system_memory', 0.0),
            
            # Method performance
            'method_comparison': method_comparison,
            'top_methods': dashboard_summary.get('top_methods', []),
            
            # Background executor stats
            'background_stats': background_executor.get_performance_stats(),
            
            # Configuration
            'configuration': config_info,
            
            # Additional metrics
            'total_history_size': dashboard_summary.get('total_history_size', 0),
            'adaptive_delay_current': self._calculate_adaptive_delay(),
            'performance_optimized': performance_optimizer.is_optimized,
            'monitoring_active': performance_optimizer.monitoring
        }
    
    async def export_performance_report(self, filename: str = None) -> str:
        """Export comprehensive performance report."""
        try:
            # Generate comprehensive report
            report_data = {
                'agent_stats': self.get_performance_stats(),
                'performance_report': performance_dashboard.get_performance_report(),
                'system_summary': performance_optimizer.get_performance_summary(),
                'configuration': config_manager.get_optimized_settings_dict(),
                'export_timestamp': time.time(),
                'export_date': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            if filename is None:
                filename = f"agent_performance_report_{int(time.time())}.json"
            
            import json
            with open(filename, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            logger.info(f"Performance report exported to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Failed to export performance report: {e}")
            return ""
    


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