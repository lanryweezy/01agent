"""
Task management, prioritization, and performance caching for the AI Agent.
"""
import time
import asyncio
from typing import Dict, List
from dataclasses import dataclass
from resource_monitor import ResourceMonitor, SystemMetrics


class PerformanceCache:
    def __init__(self, max_size=1000):
        self.cache = {}
        self.max_size = max_size
        self.access_times = {}
        self.lock = asyncio.Lock()

    async def get(self, key):
        async with self.lock:
            if key in self.cache:
                self.access_times[key] = time.time()
                return self.cache[key]
            return None

    async def set(self, key, value):
        async with self.lock:
            if len(self.cache) >= self.max_size:
                # Remove least recently used item
                oldest_key = min(self.access_times.items(), key=lambda x: x[1])[0]
                del self.cache[oldest_key]
                del self.access_times[oldest_key]
            self.cache[key] = value
            self.access_times[key] = time.time()


@dataclass
class TaskMetrics:
    execution_time: float
    cpu_usage: float
    memory_usage: float
    io_activity: float
    success_rate: float
    priority_score: float = 0.0
    last_execution_time: float = 0.0
    failure_count: int = 0
    retry_delay: float = 1.0


class TaskPrioritizer:
    def __init__(self):
        self.task_history: Dict[str, List[TaskMetrics]] = {}
        self.resource_monitor = ResourceMonitor()
        self.lock = asyncio.Lock()
        self.task_dependencies: Dict[str, List[str]] = {}
        self.task_cooldowns: Dict[str, float] = {}
        self.max_retries = 3
        self.base_retry_delay = 1.0

    async def record_task_metrics(self, task_type: str, metrics: TaskMetrics, success: bool = True):
        async with self.lock:
            current_time = time.time()
            if task_type not in self.task_history:
                self.task_history[task_type] = []

            metrics.last_execution_time = current_time
            if not success:
                metrics.failure_count += 1
                metrics.retry_delay = min(metrics.retry_delay * 2, 60.0)  # Exponential backoff up to 60s
            else:
                metrics.failure_count = 0
                metrics.retry_delay = self.base_retry_delay

            self.task_history[task_type].append(metrics)
            if len(self.task_history[task_type]) > 100:
                self.task_history[task_type].pop(0)

            # Update cooldown period based on success/failure
            self.task_cooldowns[task_type] = current_time + metrics.retry_delay

    async def get_task_priority(self, task_type: str, current_system_load: SystemMetrics) -> float:
        if task_type not in self.task_history:
            return 5.0  # Default medium priority

        metrics = self.task_history[task_type]
        if not metrics:
            return 5.0

        # Calculate average metrics
        avg_metrics = TaskMetrics(
            execution_time=sum(m.execution_time for m in metrics) / len(metrics),
            cpu_usage=sum(m.cpu_usage for m in metrics) / len(metrics),
            memory_usage=sum(m.memory_usage for m in metrics) / len(metrics),
            io_activity=sum(m.io_activity for m in metrics) / len(metrics),
            success_rate=sum(m.success_rate for m in metrics) / len(metrics),
            failure_count=max(m.failure_count for m in metrics),
            retry_delay=max(m.retry_delay for m in metrics)
        )

        # Check cooldown period
        current_time = time.time()
        if task_type in self.task_cooldowns and current_time < self.task_cooldowns[task_type]:
            return 0.0  # Task is in cooldown

        # Calculate priority score components
        resource_availability = (
            (100 - current_system_load.cpu_percent) / 100 +
            (100 - current_system_load.memory_percent) / 100
        ) / 2

        success_factor = avg_metrics.success_rate
        failure_penalty = max(0, 1 - (avg_metrics.failure_count / self.max_retries))
        time_factor = min(1.0, (current_time - avg_metrics.last_execution_time) / 300)  # Scale up to 5 minutes

        # Calculate final priority score
        priority_score = (
            resource_availability * 0.4 +
            success_factor * 0.3 +
            failure_penalty * 0.2 +
            time_factor * 0.1
        ) * 10  # Scale to 0-10 range

        return max(0.1, min(10.0, priority_score))  # Clamp between 0.1 and 10

    async def can_execute_task(self, task_type: str) -> bool:
        current_metrics = await self.resource_monitor.get_current_metrics()

        # Check if system resources are too constrained
        if current_metrics.cpu_percent > 90 or current_metrics.memory_percent > 90:
            return False

        # Check task history for resource requirements
        if task_type in self.task_history and self.task_history[task_type]:
            avg_metrics = self.task_history[task_type][-1]  # Use most recent metrics
            if (current_metrics.cpu_percent + avg_metrics.cpu_usage > 95 or
                current_metrics.memory_percent + avg_metrics.memory_usage > 95):
                return False

        return True