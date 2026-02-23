"""
Ollama health monitoring and performance optimization.
"""
import time
import asyncio
from typing import Dict, List
from dataclasses import dataclass
from resource_monitor import ResourceMonitor, SystemMetrics
from task_manager import TaskPrioritizer, TaskMetrics, PerformanceCache


class OllamaHealthMonitor:
    def __init__(self):
        self.last_health_check = 0
        self.health_check_interval = 60  # seconds
        self.status_history = []
        self.max_history = 10
        self.current_model = None
        self.model_stats = {}
        self.performance_cache = PerformanceCache()
        self.batch_size = 5
        self.batch_queue = asyncio.Queue()
        self.batch_lock = asyncio.Lock()
        self.processing = False
        self.task_prioritizer = TaskPrioritizer()
        self.resource_monitor = ResourceMonitor()
        self.performance_thresholds = {
            'latency_ms': 1000,  # 1 second
            'error_rate': 0.1,   # 10%
            'throughput': 10,     # requests/second
            'batch_size_max': 20,
            'batch_size_min': 2
        }
        self.adaptive_intervals = {
            'health_check': {'min': 30, 'max': 300},  # 30s to 5m
            'batch_timeout': {'min': 0.05, 'max': 1.0}  # 50ms to 1s
        }
    
    async def process_batches(self):
        self.processing = True
        try:
            while True:
                # Get current system metrics
                current_metrics = await self.resource_monitor.get_current_metrics()
                
                # Adjust batch size based on system load
                adjusted_batch_size = self._calculate_adaptive_batch_size(current_metrics)
                
                # Calculate adaptive timeout
                timeout = self._calculate_adaptive_timeout(current_metrics)
                
                batch = []
                try:
                    # Get first item with adaptive timeout
                    first_item = await asyncio.wait_for(self.batch_queue.get(), timeout=timeout)
                    batch.append(first_item)
                    
                    # Try to get more items without blocking
                    batch_start_time = time.time()
                    while len(batch) < adjusted_batch_size:
                        try:
                            # Check if we've spent too long building the batch
                            if time.time() - batch_start_time > timeout:
                                break
                            batch.append(self.batch_queue.get_nowait())
                        except asyncio.QueueEmpty:
                            break
                except asyncio.TimeoutError:
                    if not batch:
                        continue

                if batch:
                    # Process batch with current system metrics
                    await self._process_batch(batch, current_metrics)
                    
                    # Adjust health check interval based on error rate
                    self._adjust_health_check_interval()
                    
                    # Brief pause based on system load
                    await asyncio.sleep(self.resource_monitor.get_adaptive_delay())
        finally:
            self.processing = False

    def _calculate_adaptive_batch_size(self, metrics: SystemMetrics) -> int:
        # Calculate load factor (0-1)
        load_factor = max(
            metrics.cpu_percent / 100,
            metrics.memory_percent / 100,
            sum(metrics.disk_io.values()) / (100 * 1024 * 1024),  # Normalize to 100MB/s
            sum(metrics.network_io.values()) / (50 * 1024 * 1024)  # Normalize to 50MB/s
        )
        
        # Adjust batch size inversely to load
        base_range = self.performance_thresholds['batch_size_max'] - self.performance_thresholds['batch_size_min']
        adjusted_size = self.performance_thresholds['batch_size_max'] - (base_range * load_factor)
        
        return max(self.performance_thresholds['batch_size_min'],
                   min(self.performance_thresholds['batch_size_max'],
                       int(adjusted_size)))

    def _calculate_adaptive_timeout(self, metrics: SystemMetrics) -> float:
        # Calculate timeout based on system load
        load_factor = max(
            metrics.cpu_percent / 100,
            metrics.memory_percent / 100
        )
        
        base_range = self.adaptive_intervals['batch_timeout']['max'] - self.adaptive_intervals['batch_timeout']['min']
        timeout = self.adaptive_intervals['batch_timeout']['min'] + (base_range * (1 - load_factor))
        
        return max(self.adaptive_intervals['batch_timeout']['min'],
                   min(self.adaptive_intervals['batch_timeout']['max'],
                       timeout))

    def _adjust_health_check_interval(self):
        # Calculate error rates across all models
        total_error_rate = 0
        total_models = 0
        
        for stats in self.model_stats.values():
            if stats['total_generations'] > 0:
                total_error_rate += stats['performance_metrics']['error_rate']
                total_models += 1
        
        if total_models > 0:
            avg_error_rate = total_error_rate / total_models
            base_range = self.adaptive_intervals['health_check']['max'] - self.adaptive_intervals['health_check']['min']
            
            # Higher error rates = more frequent health checks
            self.health_check_interval = self.adaptive_intervals['health_check']['max'] - (base_range * avg_error_rate)
            self.health_check_interval = max(self.adaptive_intervals['health_check']['min'],
                                           min(self.adaptive_intervals['health_check']['max'],
                                               self.health_check_interval))

    async def _process_batch(self, items, current_metrics: SystemMetrics):
        batch_start_time = time.time()
        
        for model_name, generation_time, error in items:
            if model_name not in self.model_stats:
                self.model_stats[model_name] = {
                    'total_generations': 0,
                    'successful_generations': 0,
                    'failed_generations': 0,
                    'avg_generation_time': 0,
                    'last_error': None,
                    'performance_metrics': {
                        'latency_ms': [],
                        'throughput': 0,
                        'error_rate': 0,
                        'system_metrics': []
                    }
                }
            
            stats = self.model_stats[model_name]
            stats['total_generations'] += 1
            
            # Record system metrics snapshot
            metrics_snapshot = {
                'timestamp': time.time(),
                'cpu_percent': current_metrics.cpu_percent,
                'memory_percent': current_metrics.memory_percent,
                'disk_io': current_metrics.disk_io.copy(),
                'network_io': current_metrics.network_io.copy(),
                'gpu_utilization': current_metrics.gpu_utilization
            }
            stats['performance_metrics']['system_metrics'].append(metrics_snapshot)
            
            # Keep only recent system metrics
            if len(stats['performance_metrics']['system_metrics']) > 50:
                stats['performance_metrics']['system_metrics'].pop(0)
            
            if error:
                stats['failed_generations'] += 1
                stats['last_error'] = str(error)
                stats['performance_metrics']['error_rate'] = (
                    stats['failed_generations'] / stats['total_generations']
                )
                
                # Record task metrics for failed generation
                await self.task_prioritizer.record_task_metrics(
                    f'model_generation_{model_name}',
                    TaskMetrics(
                        execution_time=time.time() - batch_start_time,
                        cpu_usage=current_metrics.cpu_percent,
                        memory_usage=current_metrics.memory_percent,
                        io_activity=sum(current_metrics.disk_io.values()),
                        success_rate=0.0
                    ),
                    success=False
                )
            else:
                stats['successful_generations'] += 1
                if generation_time:
                    latency = generation_time * 1000  # Convert to milliseconds
                    stats['performance_metrics']['latency_ms'].append(latency)
                    if len(stats['performance_metrics']['latency_ms']) > 100:
                        stats['performance_metrics']['latency_ms'].pop(0)
                    
                    # Calculate moving average for generation time
                    stats['avg_generation_time'] = (
                        (stats['avg_generation_time'] * (stats['successful_generations'] - 1) + generation_time)
                        / stats['successful_generations']
                    )
                    
                    # Calculate throughput (requests/second) using recent history
                    recent_latencies = stats['performance_metrics']['latency_ms'][-20:]  # Last 20 requests
                    if recent_latencies:
                        avg_latency = sum(recent_latencies) / len(recent_latencies)
                        stats['performance_metrics']['throughput'] = 1000 / avg_latency  # Convert ms to seconds
                    
                    # Record task metrics for successful generation
                    await self.task_prioritizer.record_task_metrics(
                        f'model_generation_{model_name}',
                        TaskMetrics(
                            execution_time=generation_time,
                            cpu_usage=current_metrics.cpu_percent,
                            memory_usage=current_metrics.memory_percent,
                            io_activity=sum(current_metrics.disk_io.values()),
                            success_rate=1.0
                        ),
                        success=True
                    )
                    
                    # Adjust batch size based on latency threshold
                    if latency > self.performance_thresholds['latency_ms']:
                        self.batch_size = max(self.performance_thresholds['batch_size_min'],
                                             self.batch_size - 1)
                    elif latency < self.performance_thresholds['latency_ms'] / 2:
                        self.batch_size = min(self.performance_thresholds['batch_size_max'],
                                             self.batch_size + 1)
    
    async def update_model_stats(self, model_name, generation_time=None, error=None):
        await self.batch_queue.put((model_name, generation_time, error))
        if not self.processing:
            asyncio.create_task(self.process_batches())