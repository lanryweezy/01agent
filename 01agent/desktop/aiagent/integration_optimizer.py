import asyncio
import logging
import time
import os
import platform
from typing import Dict, Any, List
import json

logger = logging.getLogger(__name__)

class IntegrationOptimizer:
    """Optimizes integration between all agent components for maximum performance."""
    
    def __init__(self):
        self.system_type = platform.system().lower()
        self.optimization_applied = False
        self.integration_checks = {}
        
    async def optimize_all_integrations(self) -> Dict[str, Any]:
        """Optimize all component integrations for maximum performance."""
        logger.info("Starting comprehensive integration optimization...")
        
        optimization_results = {
            'timestamp': time.time(),
            'system_type': self.system_type,
            'optimizations_applied': [],
            'warnings': [],
            'errors': []
        }
        
        try:
            # 1. Optimize component communication
            await self._optimize_component_communication(optimization_results)
            
            # 2. Optimize memory usage across components
            await self._optimize_memory_integration(optimization_results)
            
            # 3. Optimize execution pipeline
            await self._optimize_execution_pipeline(optimization_results)
            
            # 4. Optimize system resources
            await self._optimize_system_resources(optimization_results)
            
            # 5. Optimize caching strategies
            await self._optimize_caching_strategies(optimization_results)
            
            # 6. Validate all integrations
            await self._validate_integrations(optimization_results)
            
            self.optimization_applied = True
            logger.info("Integration optimization completed successfully")
            
        except Exception as e:
            logger.error(f"Integration optimization failed: {e}")
            optimization_results['errors'].append(str(e))
        
        return optimization_results
    
    async def _optimize_component_communication(self, results: Dict[str, Any]):
        """Optimize communication between components."""
        try:
            from config_manager import config_manager
            from performance_optimizer import performance_optimizer
            from background_executor import background_executor
            from fast_ui_detector import fast_ui_detector
            
            # Synchronize timeouts across components
            config = config_manager.get_config()
            
            # Set consistent timeouts
            terminal_timeout = config.execution.terminal_timeout
            background_timeout = config.execution.background_script_timeout
            
            # Optimize background executor settings
            if hasattr(background_executor, 'max_concurrent_tasks'):
                background_executor.max_concurrent_tasks = config.performance.max_concurrent_tasks
            
            # Optimize UI detector settings
            fast_ui_detector.set_screenshot_scale(config.performance.screenshot_scale)
            fast_ui_detector.set_cache_timeout(config.performance.cache_timeout)
            
            # Set performance thresholds consistently
            if hasattr(performance_optimizer, 'set_thresholds'):
                performance_optimizer.set_thresholds(
                    cpu_high=config.performance.cpu_optimization_threshold,
                    memory_high=config.performance.memory_cleanup_threshold
                )
            
            results['optimizations_applied'].append('component_communication')
            logger.info("Component communication optimized")
            
        except Exception as e:
            logger.error(f"Component communication optimization failed: {e}")
            results['errors'].append(f"Component communication: {e}")
    
    async def _optimize_memory_integration(self, results: Dict[str, Any]):
        """Optimize memory usage across all components."""
        try:
            import gc
            from config_manager import config_manager
            
            config = config_manager.get_config()
            
            # Force garbage collection
            gc.collect()
            
            # Set memory limits for components
            memory_limit_mb = config.system.memory_limit_mb
            
            # Optimize cache sizes based on available memory
            cache_multiplier = min(memory_limit_mb / 1024, 2.0)  # Max 2x for high memory systems
            
            # Adjust UI detector cache
            from fast_ui_detector import fast_ui_detector
            if hasattr(fast_ui_detector, 'element_cache'):
                max_cache_size = int(100 * cache_multiplier)
                fast_ui_detector.element_cache = {}  # Clear cache
            
            # Optimize performance dashboard history
            from performance_dashboard import performance_dashboard
            if hasattr(performance_dashboard, 'max_history_size'):
                performance_dashboard.max_history_size = int(1000 * cache_multiplier)
            
            # Set Python memory optimizations
            if memory_limit_mb < 2048:  # Less than 2GB allocated
                gc.set_threshold(500, 5, 5)  # More aggressive GC
            else:
                gc.set_threshold(700, 10, 10)  # Standard GC
            
            results['optimizations_applied'].append('memory_integration')
            logger.info("Memory integration optimized")
            
        except Exception as e:
            logger.error(f"Memory integration optimization failed: {e}")
            results['errors'].append(f"Memory integration: {e}")
    
    async def _optimize_execution_pipeline(self, results: Dict[str, Any]):
        """Optimize the task execution pipeline."""
        try:
            from config_manager import config_manager
            from smart_executor import smart_executor
            from terminal_controller import terminal_controller
            
            config = config_manager.get_config()
            
            # Optimize smart executor performance cache
            if hasattr(smart_executor, 'performance_cache'):
                # Clear old cache entries
                smart_executor.performance_cache.clear()
            
            # Optimize terminal controller sessions
            if hasattr(terminal_controller, 'cleanup_inactive_sessions'):
                await terminal_controller.cleanup_inactive_sessions(max_idle_time=300.0)
            
            # Pre-warm execution strategies
            if hasattr(smart_executor, 'strategies'):
                # Initialize strategy performance metrics
                for strategy_name in smart_executor.strategies.keys():
                    if strategy_name not in smart_executor.execution_history:
                        smart_executor.execution_history[strategy_name] = []
            
            results['optimizations_applied'].append('execution_pipeline')
            logger.info("Execution pipeline optimized")
            
        except Exception as e:
            logger.error(f"Execution pipeline optimization failed: {e}")
            results['errors'].append(f"Execution pipeline: {e}")
    
    async def _optimize_system_resources(self, results: Dict[str, Any]):
        """Optimize system resource usage."""
        try:
            import psutil
            from performance_optimizer import performance_optimizer
            
            # Get current system state
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            
            # Apply system-specific optimizations
            if self.system_type == 'windows':
                await self._optimize_windows_resources(results)
            elif self.system_type == 'darwin':
                await self._optimize_macos_resources(results)
            else:
                await self._optimize_linux_resources(results)
            
            # Apply performance optimizations based on current load
            if cpu_percent > 80 or memory_percent > 85:
                await performance_optimizer.quick_cleanup()
                results['optimizations_applied'].append('high_load_cleanup')
            
            results['optimizations_applied'].append('system_resources')
            logger.info(f"System resources optimized for {self.system_type}")
            
        except Exception as e:
            logger.error(f"System resource optimization failed: {e}")
            results['errors'].append(f"System resources: {e}")
    
    async def _optimize_windows_resources(self, results: Dict[str, Any]):
        """Windows-specific optimizations."""
        try:
            import subprocess
            
            # Set process priority
            try:
                import psutil
                current_process = psutil.Process()
                current_process.nice(psutil.HIGH_PRIORITY_CLASS)
                results['optimizations_applied'].append('windows_process_priority')
            except:
                results['warnings'].append('Could not set high process priority')
            
            # Optimize Windows-specific settings
            commands = [
                'powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c',  # High Performance
            ]
            
            for cmd in commands:
                try:
                    subprocess.run(cmd, shell=True, check=False, 
                                 creationflags=subprocess.CREATE_NO_WINDOW, timeout=5)
                except:
                    pass
            
        except Exception as e:
            results['warnings'].append(f"Windows optimization warning: {e}")
    
    async def _optimize_macos_resources(self, results: Dict[str, Any]):
        """macOS-specific optimizations."""
        try:
            import os
            
            # Set process priority
            try:
                os.nice(-10)
                results['optimizations_applied'].append('macos_process_priority')
            except:
                results['warnings'].append('Could not set higher process priority')
            
            # macOS-specific environment variables
            os.environ['NSAppSleepDisabled'] = '1'  # Prevent app nap
            
        except Exception as e:
            results['warnings'].append(f"macOS optimization warning: {e}")
    
    async def _optimize_linux_resources(self, results: Dict[str, Any]):
        """Linux-specific optimizations."""
        try:
            import os
            
            # Set process priority
            try:
                os.nice(-10)
                results['optimizations_applied'].append('linux_process_priority')
            except:
                results['warnings'].append('Could not set higher process priority')
            
        except Exception as e:
            results['warnings'].append(f"Linux optimization warning: {e}")
    
    async def _optimize_caching_strategies(self, results: Dict[str, Any]):
        """Optimize caching strategies across components."""
        try:
            from config_manager import config_manager
            from fast_ui_detector import fast_ui_detector
            
            config = config_manager.get_config()
            
            # Coordinate cache timeouts
            base_cache_timeout = config.performance.cache_timeout
            
            # Set UI detector cache
            fast_ui_detector.set_cache_timeout(base_cache_timeout)
            
            # Optimize screenshot caching based on system performance
            import psutil
            memory_percent = psutil.virtual_memory().percent
            
            if memory_percent > 80:
                # Reduce cache timeout under memory pressure
                fast_ui_detector.set_cache_timeout(base_cache_timeout * 0.5)
                results['optimizations_applied'].append('memory_pressure_cache_reduction')
            
            results['optimizations_applied'].append('caching_strategies')
            logger.info("Caching strategies optimized")
            
        except Exception as e:
            logger.error(f"Caching optimization failed: {e}")
            results['errors'].append(f"Caching strategies: {e}")
    
    async def _validate_integrations(self, results: Dict[str, Any]):
        """Validate that all component integrations are working correctly."""
        try:
            validation_results = {}
            
            # Test component imports
            try:
                from smart_executor import smart_executor
                from terminal_controller import terminal_controller
                from background_executor import background_executor
                from fast_ui_detector import fast_ui_detector
                from performance_optimizer import performance_optimizer
                from config_manager import config_manager
                from performance_dashboard import performance_dashboard
                
                validation_results['imports'] = 'success'
            except Exception as e:
                validation_results['imports'] = f'failed: {e}'
                results['errors'].append(f"Import validation failed: {e}")
            
            # Test configuration access
            try:
                config = config_manager.get_config()
                validation_results['configuration'] = 'success'
            except Exception as e:
                validation_results['configuration'] = f'failed: {e}'
                results['errors'].append(f"Configuration validation failed: {e}")
            
            # Test performance monitoring
            try:
                perf_stats = performance_optimizer.get_performance_summary()
                validation_results['performance_monitoring'] = 'success'
            except Exception as e:
                validation_results['performance_monitoring'] = f'failed: {e}'
                results['warnings'].append(f"Performance monitoring validation failed: {e}")
            
            # Test dashboard
            try:
                dashboard_summary = performance_dashboard.get_dashboard_summary()
                validation_results['dashboard'] = 'success'
            except Exception as e:
                validation_results['dashboard'] = f'failed: {e}'
                results['warnings'].append(f"Dashboard validation failed: {e}")
            
            self.integration_checks = validation_results
            results['validation_results'] = validation_results
            
            # Count successful validations
            successful_validations = sum(1 for result in validation_results.values() 
                                       if result == 'success')
            total_validations = len(validation_results)
            
            logger.info(f"Integration validation: {successful_validations}/{total_validations} passed")
            
        except Exception as e:
            logger.error(f"Integration validation failed: {e}")
            results['errors'].append(f"Integration validation: {e}")
    
    def get_optimization_status(self) -> Dict[str, Any]:
        """Get current optimization status."""
        return {
            'optimization_applied': self.optimization_applied,
            'system_type': self.system_type,
            'integration_checks': self.integration_checks,
            'last_check_time': time.time()
        }
    
    async def run_performance_test(self) -> Dict[str, Any]:
        """Run a comprehensive performance test of all integrations."""
        logger.info("Running integration performance test...")
        
        test_results = {
            'start_time': time.time(),
            'tests': {},
            'overall_score': 0.0
        }
        
        try:
            # Test 1: Configuration loading speed
            start_time = time.time()
            from config_manager import config_manager
            config = config_manager.get_config()
            config_time = time.time() - start_time
            test_results['tests']['config_loading'] = {
                'time': config_time,
                'score': max(0, 100 - (config_time * 1000))  # Score based on milliseconds
            }
            
            # Test 2: Screenshot capture speed
            start_time = time.time()
            from fast_ui_detector import fast_ui_detector
            screenshot = await fast_ui_detector.take_fast_screenshot()
            screenshot_time = time.time() - start_time
            test_results['tests']['screenshot_capture'] = {
                'time': screenshot_time,
                'score': max(0, 100 - (screenshot_time * 50)),  # Score based on speed
                'screenshot_size': screenshot.size if hasattr(screenshot, 'size') else 0
            }
            
            # Test 3: Performance monitoring speed
            start_time = time.time()
            from performance_optimizer import performance_optimizer
            metrics = await performance_optimizer.get_current_metrics()
            monitoring_time = time.time() - start_time
            test_results['tests']['performance_monitoring'] = {
                'time': monitoring_time,
                'score': max(0, 100 - (monitoring_time * 100))
            }
            
            # Test 4: Dashboard response speed
            start_time = time.time()
            from performance_dashboard import performance_dashboard
            dashboard_summary = performance_dashboard.get_dashboard_summary()
            dashboard_time = time.time() - start_time
            test_results['tests']['dashboard_response'] = {
                'time': dashboard_time,
                'score': max(0, 100 - (dashboard_time * 200))
            }
            
            # Calculate overall score
            scores = [test['score'] for test in test_results['tests'].values()]
            test_results['overall_score'] = sum(scores) / len(scores) if scores else 0
            
            test_results['end_time'] = time.time()
            test_results['total_time'] = test_results['end_time'] - test_results['start_time']
            
            logger.info(f"Performance test completed. Overall score: {test_results['overall_score']:.1f}/100")
            
        except Exception as e:
            logger.error(f"Performance test failed: {e}")
            test_results['error'] = str(e)
        
        return test_results

# Global integration optimizer instance
integration_optimizer = IntegrationOptimizer()