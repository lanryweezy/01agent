import asyncio
import psutil
import time
import logging
import os
import platform
import subprocess
from typing import Dict, List, Optional, Any
import threading
import gc
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    cpu_percent: float
    memory_percent: float
    disk_io_read: float
    disk_io_write: float
    network_io_sent: float
    network_io_recv: float
    process_count: int
    thread_count: int
    timestamp: float

class PerformanceOptimizer:
    """System performance optimizer for maximum speed."""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.is_optimized = False
        self.original_settings = {}
        self.monitoring = False
        self.metrics_history: List[PerformanceMetrics] = []
        self.max_history = 100
        
        # Performance thresholds
        self.thresholds = {
            'cpu_high': 80.0,
            'memory_high': 85.0,
            'disk_io_high': 100 * 1024 * 1024,  # 100 MB/s
            'network_io_high': 50 * 1024 * 1024,  # 50 MB/s
        }
        
        # Optimization strategies
        self.optimizations = {
            'process_priority': self._optimize_process_priority,
            'memory_cleanup': self._optimize_memory,
            'disk_cache': self._optimize_disk_cache,
            'network_settings': self._optimize_network,
            'visual_effects': self._optimize_visual_effects,
            'background_apps': self._optimize_background_apps,
            'power_settings': self._optimize_power_settings
        }
    
    async def start_monitoring(self):
        """Start performance monitoring."""
        if not self.monitoring:
            self.monitoring = True
            asyncio.create_task(self._monitoring_loop())
            logger.info("Performance monitoring started")
    
    async def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring = False
        logger.info("Performance monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring:
            try:
                metrics = await self._collect_metrics()
                self.metrics_history.append(metrics)
                
                # Keep only recent history
                if len(self.metrics_history) > self.max_history:
                    self.metrics_history.pop(0)
                
                # Check if optimization is needed
                if await self._should_optimize(metrics):
                    await self._auto_optimize()
                
                await asyncio.sleep(1.0)  # Check every second
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5.0)
    
    async def _collect_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics."""
        try:
            # CPU and memory
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            disk_read = disk_io.read_bytes if disk_io else 0
            disk_write = disk_io.write_bytes if disk_io else 0
            
            # Network I/O
            network_io = psutil.net_io_counters()
            network_sent = network_io.bytes_sent if network_io else 0
            network_recv = network_io.bytes_recv if network_io else 0
            
            # Process info
            process_count = len(psutil.pids())
            thread_count = sum(p.num_threads() for p in psutil.process_iter(['num_threads']) 
                             if p.info['num_threads'])
            
            return PerformanceMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_io_read=disk_read,
                disk_io_write=disk_write,
                network_io_sent=network_sent,
                network_io_recv=network_recv,
                process_count=process_count,
                thread_count=thread_count,
                timestamp=time.time()
            )
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return PerformanceMetrics(0, 0, 0, 0, 0, 0, 0, 0, time.time())
    
    async def _should_optimize(self, metrics: PerformanceMetrics) -> bool:
        """Check if optimization is needed based on current metrics."""
        return (
            metrics.cpu_percent > self.thresholds['cpu_high'] or
            metrics.memory_percent > self.thresholds['memory_high']
        )
    
    async def _auto_optimize(self):
        """Automatically optimize system performance."""
        if not self.is_optimized:
            logger.info("Auto-optimizing system performance...")
            await self.optimize_for_speed()
    
    async def optimize_for_speed(self):
        """Optimize system for maximum speed."""
        try:
            logger.info("Starting performance optimization...")
            
            # Run optimizations
            for name, optimization_func in self.optimizations.items():
                try:
                    await optimization_func()
                    logger.info(f"Applied optimization: {name}")
                except Exception as e:
                    logger.error(f"Failed to apply {name}: {e}")
            
            self.is_optimized = True
            logger.info("Performance optimization completed")
            
        except Exception as e:
            logger.error(f"Error during optimization: {e}")
    
    async def _optimize_process_priority(self):
        """Optimize process priority for current process."""
        try:
            current_process = psutil.Process()
            
            if self.system == "windows":
                # Set high priority on Windows
                import win32api
                import win32process
                import win32con
                
                handle = win32api.GetCurrentProcess()
                win32process.SetPriorityClass(handle, win32process.HIGH_PRIORITY_CLASS)
                
            else:
                # Set nice value on Unix-like systems
                os.nice(-10)  # Higher priority (lower nice value)
            
            logger.info("Process priority optimized")
            
        except Exception as e:
            logger.error(f"Failed to optimize process priority: {e}")
    
    async def _optimize_memory(self):
        """Optimize memory usage."""
        try:
            # Force garbage collection
            gc.collect()
            
            # Clear Python caches
            import sys
            if hasattr(sys, '_clear_type_cache'):
                sys._clear_type_cache()
            
            # On Windows, try to optimize working set
            if self.system == "windows":
                try:
                    import ctypes
                    from ctypes import wintypes
                    
                    # Trim working set
                    kernel32 = ctypes.windll.kernel32
                    handle = kernel32.GetCurrentProcess()
                    kernel32.SetProcessWorkingSetSize(handle, -1, -1)
                    
                except Exception:
                    pass
            
            logger.info("Memory optimization completed")
            
        except Exception as e:
            logger.error(f"Failed to optimize memory: {e}")
    
    async def _optimize_disk_cache(self):
        """Optimize disk cache settings."""
        try:
            if self.system == "windows":
                # Windows-specific disk optimizations
                commands = [
                    # Disable write cache buffer flushing (for speed, but less safe)
                    'fsutil behavior set DisableDeleteNotify 0',  # Enable TRIM
                ]
                
                for cmd in commands:
                    try:
                        subprocess.run(cmd, shell=True, check=False, 
                                     creationflags=subprocess.CREATE_NO_WINDOW)
                    except Exception:
                        pass
            
            logger.info("Disk cache optimization completed")
            
        except Exception as e:
            logger.error(f"Failed to optimize disk cache: {e}")
    
    async def _optimize_network(self):
        """Optimize network settings."""
        try:
            if self.system == "windows":
                # Windows network optimizations
                commands = [
                    'netsh int tcp set global autotuninglevel=normal',
                    'netsh int tcp set global chimney=enabled',
                    'netsh int tcp set global rss=enabled',
                ]
                
                for cmd in commands:
                    try:
                        subprocess.run(cmd, shell=True, check=False,
                                     creationflags=subprocess.CREATE_NO_WINDOW)
                    except Exception:
                        pass
            
            logger.info("Network optimization completed")
            
        except Exception as e:
            logger.error(f"Failed to optimize network: {e}")
    
    async def _optimize_visual_effects(self):
        """Optimize visual effects for performance."""
        try:
            if self.system == "windows":
                # Disable visual effects for performance
                import winreg
                
                try:
                    # Set visual effects to "Adjust for best performance"
                    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects"
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                        winreg.SetValueEx(key, "VisualFXSetting", 0, winreg.REG_DWORD, 2)
                        
                except Exception:
                    pass
            
            logger.info("Visual effects optimization completed")
            
        except Exception as e:
            logger.error(f"Failed to optimize visual effects: {e}")
    
    async def _optimize_background_apps(self):
        """Optimize background applications."""
        try:
            # Get list of processes that consume high resources
            high_resource_processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if (proc.info['cpu_percent'] > 5.0 or 
                        proc.info['memory_percent'] > 2.0):
                        
                        # Skip critical system processes
                        if proc.info['name'].lower() not in [
                            'system', 'kernel', 'csrss.exe', 'winlogon.exe',
                            'services.exe', 'lsass.exe', 'svchost.exe'
                        ]:
                            high_resource_processes.append(proc.info)
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Log high resource processes (don't automatically kill them)
            if high_resource_processes:
                logger.info(f"Found {len(high_resource_processes)} high-resource processes")
                for proc in high_resource_processes[:5]:  # Log top 5
                    logger.info(f"  {proc['name']}: CPU {proc['cpu_percent']:.1f}%, "
                              f"Memory {proc['memory_percent']:.1f}%")
            
        except Exception as e:
            logger.error(f"Failed to optimize background apps: {e}")
    
    async def _optimize_power_settings(self):
        """Optimize power settings for performance."""
        try:
            if self.system == "windows":
                # Set power plan to High Performance
                commands = [
                    'powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c',  # High Performance GUID
                    'powercfg /change monitor-timeout-ac 0',  # Never turn off monitor
                    'powercfg /change disk-timeout-ac 0',     # Never turn off disk
                ]
                
                for cmd in commands:
                    try:
                        subprocess.run(cmd, shell=True, check=False,
                                     creationflags=subprocess.CREATE_NO_WINDOW)
                    except Exception:
                        pass
            
            logger.info("Power settings optimization completed")
            
        except Exception as e:
            logger.error(f"Failed to optimize power settings: {e}")
    
    async def restore_original_settings(self):
        """Restore original system settings."""
        try:
            if self.is_optimized:
                logger.info("Restoring original system settings...")
                
                # Restore process priority
                try:
                    current_process = psutil.Process()
                    if self.system == "windows":
                        import win32api
                        import win32process
                        handle = win32api.GetCurrentProcess()
                        win32process.SetPriorityClass(handle, win32process.NORMAL_PRIORITY_CLASS)
                    else:
                        os.nice(10)  # Reset to normal priority
                except Exception:
                    pass
                
                self.is_optimized = False
                logger.info("Original settings restored")
                
        except Exception as e:
            logger.error(f"Error restoring settings: {e}")
    
    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """Get the most recent performance metrics."""
        return self.metrics_history[-1] if self.metrics_history else None
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a summary of performance metrics."""
        if not self.metrics_history:
            return {}
        
        recent_metrics = self.metrics_history[-10:]  # Last 10 measurements
        
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
        
        return {
            'average_cpu_percent': avg_cpu,
            'average_memory_percent': avg_memory,
            'current_process_count': recent_metrics[-1].process_count,
            'current_thread_count': recent_metrics[-1].thread_count,
            'is_optimized': self.is_optimized,
            'monitoring': self.monitoring,
            'metrics_count': len(self.metrics_history),
            'performance_status': self._get_performance_status(avg_cpu, avg_memory)
        }
    
    def _get_performance_status(self, cpu_percent: float, memory_percent: float) -> str:
        """Get performance status based on metrics."""
        if cpu_percent > 80 or memory_percent > 85:
            return "high_load"
        elif cpu_percent > 60 or memory_percent > 70:
            return "medium_load"
        else:
            return "low_load"
    
    async def quick_cleanup(self):
        """Perform quick system cleanup for immediate performance boost."""
        try:
            logger.info("Performing quick system cleanup...")
            
            # Memory cleanup
            gc.collect()
            
            # Clear temporary files (basic cleanup)
            if self.system == "windows":
                temp_dirs = [
                    os.environ.get('TEMP', ''),
                    os.environ.get('TMP', ''),
                    os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Temp')
                ]
                
                for temp_dir in temp_dirs:
                    if temp_dir and os.path.exists(temp_dir):
                        try:
                            # Only remove files older than 1 hour for safety
                            current_time = time.time()
                            for filename in os.listdir(temp_dir):
                                filepath = os.path.join(temp_dir, filename)
                                try:
                                    if (os.path.isfile(filepath) and 
                                        current_time - os.path.getmtime(filepath) > 3600):
                                        os.remove(filepath)
                                except Exception:
                                    pass
                        except Exception:
                            pass
            
            logger.info("Quick cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during quick cleanup: {e}")
    
    def set_thresholds(self, **kwargs):
        """Set performance thresholds."""
        for key, value in kwargs.items():
            if key in self.thresholds:
                self.thresholds[key] = value
                logger.info(f"Threshold {key} set to {value}")

# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()