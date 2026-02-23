"""
Resource monitoring and system metrics for the AI Agent.
"""
import time
import asyncio
import psutil
import torch
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class SystemMetrics:
    cpu_percent: float
    memory_percent: float
    disk_io: Dict[str, float]
    network_io: Dict[str, float]
    gpu_utilization: Optional[float] = None
    process_count: int = 0
    thread_count: int = 0
    handle_count: int = 0
    context_switches: int = 0


class ResourceMonitor:
    def __init__(self, sampling_interval: float = 1.0):
        self.sampling_interval = sampling_interval
        self.metrics_history: List[Tuple[float, SystemMetrics]] = []
        self.max_history_size = 100
        self._last_disk_io = psutil.disk_io_counters()
        self._last_net_io = psutil.net_io_counters()
        self._last_check_time = time.time()
        self._last_ctx_switches = psutil.cpu_stats().ctx_switches
        self.lock = asyncio.Lock()
        self.performance_threshold = {
            'cpu': 80.0,  # CPU usage threshold (%)
            'memory': 85.0,  # Memory usage threshold (%)
            'disk_io': 50 * 1024 * 1024,  # 50 MB/s
            'network_io': 20 * 1024 * 1024,  # 20 MB/s
            'gpu': 90.0 if torch.cuda.is_available() else None  # GPU usage threshold (%)
        }

    async def get_current_metrics(self) -> SystemMetrics:
        async with self.lock:
            current_time = time.time()
            time_delta = current_time - self._last_check_time

            # Get current IO counters and system stats
            current_disk_io = psutil.disk_io_counters()
            current_net_io = psutil.net_io_counters()
            current_ctx_switches = psutil.cpu_stats().ctx_switches

            # Calculate IO rates and context switch rate
            disk_read_rate = (current_disk_io.read_bytes - self._last_disk_io.read_bytes) / time_delta
            disk_write_rate = (current_disk_io.write_bytes - self._last_disk_io.write_bytes) / time_delta
            net_send_rate = (current_net_io.bytes_sent - self._last_net_io.bytes_sent) / time_delta
            net_recv_rate = (current_net_io.bytes_recv - self._last_net_io.bytes_recv) / time_delta
            ctx_switch_rate = (current_ctx_switches - self._last_ctx_switches) / time_delta

            # Update last values
            self._last_disk_io = current_disk_io
            self._last_net_io = current_net_io
            self._last_ctx_switches = current_ctx_switches
            self._last_check_time = current_time

            # Get detailed system metrics
            process_info = psutil.Process().as_dict(attrs=['num_threads', 'num_handles'])
            system_stats = psutil.cpu_stats()

            # Get GPU utilization if available
            gpu_util = None
            if torch.cuda.is_available():
                try:
                    gpu_util = torch.cuda.utilization()
                except Exception:
                    pass

            metrics = SystemMetrics(
                cpu_percent=psutil.cpu_percent(),
                memory_percent=psutil.virtual_memory().percent,
                disk_io={"read_rate": disk_read_rate, "write_rate": disk_write_rate},
                network_io={"send_rate": net_send_rate, "recv_rate": net_recv_rate},
                gpu_utilization=gpu_util
            )

            self.metrics_history.append((current_time, metrics))
            if len(self.metrics_history) > self.max_history_size:
                self.metrics_history.pop(0)

            return metrics

    def get_adaptive_delay(self) -> float:
        """Calculate adaptive delay based on system load."""
        if not self.metrics_history:
            return 0.02

        latest_metrics = self.metrics_history[-1][1]
        
        # Base delay calculation using CPU and memory load
        base_delay = 0.02  # Default 20ms
        load_factor = max(latest_metrics.cpu_percent, latest_metrics.memory_percent) / 100.0
        
        # Adjust delay based on IO activity
        io_factor = max(
            sum(latest_metrics.disk_io.values()),
            sum(latest_metrics.network_io.values())
        ) / (10 * 1024 * 1024)  # Normalize to 10MB/s
        
        # Consider GPU utilization if available
        if latest_metrics.gpu_utilization is not None:
            load_factor = max(load_factor, latest_metrics.gpu_utilization / 100.0)
        
        # Calculate final delay
        adaptive_delay = base_delay * (1 + max(load_factor, io_factor))
        return min(0.1, max(0.01, adaptive_delay))  # Clamp between 10ms and 100ms

    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        return psutil.cpu_percent()

    def get_memory_usage(self) -> float:
        """Get current memory usage percentage."""
        return psutil.virtual_memory().percent


def check_gpu_availability():
    if torch.cuda.is_available():
        return {
            'available': True,
            'device': 'cuda',
            'name': torch.cuda.get_device_name(0),
            'compute_capability': torch.cuda.get_device_capability(0)
        }
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        return {
            'available': True,
            'device': 'mps',
            'name': 'Apple Silicon GPU'
        }
    return {
        'available': False,
        'device': 'cpu'
    }