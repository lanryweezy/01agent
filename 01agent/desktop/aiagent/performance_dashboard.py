import asyncio
import time
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import threading

logger = logging.getLogger(__name__)

# Import TaskMetrics from task_manager to avoid duplication
from task_manager import TaskMetrics as BaseTaskMetrics

@dataclass
class TaskMetrics(BaseTaskMetrics):
    """Extended metrics for dashboard with additional fields."""
    task_id: str = ""
    task_description: str = ""
    execution_method: str = ""
    success: bool = True
    timestamp: float = 0.0
    error_message: Optional[str] = None
    system_load_cpu: Optional[float] = None
    system_load_memory: Optional[float] = None

@dataclass
class SystemSnapshot:
    """System performance snapshot."""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    disk_io_read: float
    disk_io_write: float
    network_io_sent: float
    network_io_recv: float
    active_tasks: int
    queue_size: int

@dataclass
class PerformanceReport:
    """Comprehensive performance report."""
    report_time: str
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    success_rate: float
    average_execution_time: float
    fastest_execution: float
    slowest_execution: float
    most_used_method: str
    system_performance: Dict[str, float]
    recommendations: List[str]

class PerformanceDashboard:
    """Real-time performance monitoring and analytics dashboard."""
    
    def __init__(self, max_history_size: int = 1000):
        self.max_history_size = max_history_size
        self.task_metrics: List[TaskMetrics] = []
        self.system_snapshots: List[SystemSnapshot] = []
        self.is_monitoring = False
        self.lock = threading.Lock()
        
        # Performance thresholds
        self.thresholds = {
            'execution_time_warning': 5.0,
            'execution_time_critical': 10.0,
            'success_rate_warning': 0.8,
            'success_rate_critical': 0.6,
            'cpu_warning': 80.0,
            'cpu_critical': 90.0,
            'memory_warning': 85.0,
            'memory_critical': 95.0
        }
        
        # Analytics cache
        self._analytics_cache = {}
        self._cache_timestamp = 0
        self._cache_ttl = 5.0  # 5 seconds
    
    def record_task_execution(self, task_metrics: TaskMetrics):
        """Record a task execution for analytics."""
        with self.lock:
            self.task_metrics.append(task_metrics)
            
            # Keep only recent history
            if len(self.task_metrics) > self.max_history_size:
                self.task_metrics.pop(0)
            
            # Clear analytics cache
            self._analytics_cache.clear()
            
            logger.debug(f"Recorded task execution: {task_metrics.task_id}")
    
    def record_system_snapshot(self, snapshot: SystemSnapshot):
        """Record a system performance snapshot."""
        with self.lock:
            self.system_snapshots.append(snapshot)
            
            # Keep only recent history
            if len(self.system_snapshots) > self.max_history_size:
                self.system_snapshots.pop(0)
            
            logger.debug(f"Recorded system snapshot at {snapshot.timestamp}")
    
    def get_real_time_stats(self) -> Dict[str, Any]:
        """Get real-time performance statistics."""
        current_time = time.time()
        
        # Check cache
        if (current_time - self._cache_timestamp < self._cache_ttl and 
            'real_time_stats' in self._analytics_cache):
            return self._analytics_cache['real_time_stats']
        
        with self.lock:
            if not self.task_metrics:
                return {}
            
            # Recent tasks (last 5 minutes)
            recent_cutoff = current_time - 300
            recent_tasks = [t for t in self.task_metrics if t.timestamp > recent_cutoff]
            
            if not recent_tasks:
                return {}
            
            # Calculate statistics
            total_tasks = len(recent_tasks)
            successful_tasks = sum(1 for t in recent_tasks if t.success)
            success_rate = successful_tasks / total_tasks if total_tasks > 0 else 0
            
            execution_times = [t.execution_time for t in recent_tasks]
            avg_execution_time = sum(execution_times) / len(execution_times)
            
            # Method distribution
            method_counts = {}
            for task in recent_tasks:
                method_counts[task.execution_method] = method_counts.get(task.execution_method, 0) + 1
            
            most_used_method = max(method_counts.items(), key=lambda x: x[1])[0] if method_counts else "none"
            
            # System performance
            recent_snapshots = [s for s in self.system_snapshots if s.timestamp > recent_cutoff]
            avg_cpu = sum(s.cpu_percent for s in recent_snapshots) / len(recent_snapshots) if recent_snapshots else 0
            avg_memory = sum(s.memory_percent for s in recent_snapshots) / len(recent_snapshots) if recent_snapshots else 0
            
            stats = {
                'timestamp': current_time,
                'recent_tasks': total_tasks,
                'success_rate': success_rate,
                'average_execution_time': avg_execution_time,
                'fastest_execution': min(execution_times) if execution_times else 0,
                'slowest_execution': max(execution_times) if execution_times else 0,
                'most_used_method': most_used_method,
                'method_distribution': method_counts,
                'system_cpu_avg': avg_cpu,
                'system_memory_avg': avg_memory,
                'performance_status': self._get_performance_status(success_rate, avg_execution_time, avg_cpu, avg_memory)
            }
            
            # Cache the result
            self._analytics_cache['real_time_stats'] = stats
            self._cache_timestamp = current_time
            
            return stats
    
    def get_performance_report(self, hours: int = 24) -> PerformanceReport:
        """Generate a comprehensive performance report."""
        current_time = time.time()
        cutoff_time = current_time - (hours * 3600)
        
        with self.lock:
            # Filter tasks within time range
            filtered_tasks = [t for t in self.task_metrics if t.timestamp > cutoff_time]
            
            if not filtered_tasks:
                return PerformanceReport(
                    report_time=datetime.now().isoformat(),
                    total_tasks=0,
                    successful_tasks=0,
                    failed_tasks=0,
                    success_rate=0.0,
                    average_execution_time=0.0,
                    fastest_execution=0.0,
                    slowest_execution=0.0,
                    most_used_method="none",
                    system_performance={},
                    recommendations=[]
                )
            
            # Calculate metrics
            total_tasks = len(filtered_tasks)
            successful_tasks = sum(1 for t in filtered_tasks if t.success)
            failed_tasks = total_tasks - successful_tasks
            success_rate = successful_tasks / total_tasks
            
            execution_times = [t.execution_time for t in filtered_tasks]
            avg_execution_time = sum(execution_times) / len(execution_times)
            fastest_execution = min(execution_times)
            slowest_execution = max(execution_times)
            
            # Method analysis
            method_counts = {}
            for task in filtered_tasks:
                method_counts[task.execution_method] = method_counts.get(task.execution_method, 0) + 1
            
            most_used_method = max(method_counts.items(), key=lambda x: x[1])[0] if method_counts else "none"
            
            # System performance
            filtered_snapshots = [s for s in self.system_snapshots if s.timestamp > cutoff_time]
            system_performance = {}
            if filtered_snapshots:
                system_performance = {
                    'avg_cpu': sum(s.cpu_percent for s in filtered_snapshots) / len(filtered_snapshots),
                    'avg_memory': sum(s.memory_percent for s in filtered_snapshots) / len(filtered_snapshots),
                    'max_cpu': max(s.cpu_percent for s in filtered_snapshots),
                    'max_memory': max(s.memory_percent for s in filtered_snapshots)
                }
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                success_rate, avg_execution_time, system_performance, method_counts
            )
            
            return PerformanceReport(
                report_time=datetime.now().isoformat(),
                total_tasks=total_tasks,
                successful_tasks=successful_tasks,
                failed_tasks=failed_tasks,
                success_rate=success_rate,
                average_execution_time=avg_execution_time,
                fastest_execution=fastest_execution,
                slowest_execution=slowest_execution,
                most_used_method=most_used_method,
                system_performance=system_performance,
                recommendations=recommendations
            )
    
    def _get_performance_status(self, success_rate: float, avg_execution_time: float, 
                              avg_cpu: float, avg_memory: float) -> str:
        """Determine overall performance status."""
        if (success_rate < self.thresholds['success_rate_critical'] or
            avg_execution_time > self.thresholds['execution_time_critical'] or
            avg_cpu > self.thresholds['cpu_critical'] or
            avg_memory > self.thresholds['memory_critical']):
            return "critical"
        
        elif (success_rate < self.thresholds['success_rate_warning'] or
              avg_execution_time > self.thresholds['execution_time_warning'] or
              avg_cpu > self.thresholds['cpu_warning'] or
              avg_memory > self.thresholds['memory_warning']):
            return "warning"
        
        else:
            return "good"
    
    def _generate_recommendations(self, success_rate: float, avg_execution_time: float,
                                system_performance: Dict[str, float], 
                                method_counts: Dict[str, int]) -> List[str]:
        """Generate performance improvement recommendations."""
        recommendations = []
        
        # Success rate recommendations
        if success_rate < self.thresholds['success_rate_critical']:
            recommendations.append("Critical: Success rate is very low. Consider switching to reliability_priority strategy.")
        elif success_rate < self.thresholds['success_rate_warning']:
            recommendations.append("Warning: Success rate is below optimal. Review failed tasks and consider strategy adjustment.")
        
        # Execution time recommendations
        if avg_execution_time > self.thresholds['execution_time_critical']:
            recommendations.append("Critical: Average execution time is very high. Consider optimizing task complexity or system resources.")
        elif avg_execution_time > self.thresholds['execution_time_warning']:
            recommendations.append("Warning: Execution time is above optimal. Consider speed_priority strategy or system optimization.")
        
        # System performance recommendations
        if system_performance:
            avg_cpu = system_performance.get('avg_cpu', 0)
            avg_memory = system_performance.get('avg_memory', 0)
            
            if avg_cpu > self.thresholds['cpu_critical']:
                recommendations.append("Critical: CPU usage is very high. Consider reducing concurrent tasks or background_priority strategy.")
            elif avg_cpu > self.thresholds['cpu_warning']:
                recommendations.append("Warning: CPU usage is high. Monitor system load and consider optimization.")
            
            if avg_memory > self.thresholds['memory_critical']:
                recommendations.append("Critical: Memory usage is very high. Consider memory cleanup or reducing cache sizes.")
            elif avg_memory > self.thresholds['memory_warning']:
                recommendations.append("Warning: Memory usage is high. Monitor memory consumption and consider optimization.")
        
        # Method-specific recommendations
        if method_counts:
            total_methods = sum(method_counts.values())
            gui_percentage = method_counts.get('gui_fallback', 0) / total_methods
            
            if gui_percentage > 0.5:
                recommendations.append("Consider optimizing tasks to use faster methods (terminal, scripts) instead of GUI automation.")
            
            if 'background_script_error' in method_counts or 'terminal_error' in method_counts:
                recommendations.append("Review error logs for failed terminal/script executions and improve error handling.")
        
        # General recommendations
        if not recommendations:
            recommendations.append("Performance is optimal. Continue monitoring for any changes.")
        
        return recommendations
    
    def get_method_performance_comparison(self) -> Dict[str, Dict[str, float]]:
        """Compare performance across different execution methods."""
        with self.lock:
            if not self.task_metrics:
                return {}
            
            method_stats = {}
            
            for task in self.task_metrics:
                method = task.execution_method
                if method not in method_stats:
                    method_stats[method] = {
                        'total_tasks': 0,
                        'successful_tasks': 0,
                        'total_time': 0.0,
                        'min_time': float('inf'),
                        'max_time': 0.0
                    }
                
                stats = method_stats[method]
                stats['total_tasks'] += 1
                if task.success:
                    stats['successful_tasks'] += 1
                
                stats['total_time'] += task.execution_time
                stats['min_time'] = min(stats['min_time'], task.execution_time)
                stats['max_time'] = max(stats['max_time'], task.execution_time)
            
            # Calculate derived metrics
            for method, stats in method_stats.items():
                if stats['total_tasks'] > 0:
                    stats['success_rate'] = stats['successful_tasks'] / stats['total_tasks']
                    stats['average_time'] = stats['total_time'] / stats['total_tasks']
                else:
                    stats['success_rate'] = 0.0
                    stats['average_time'] = 0.0
                
                if stats['min_time'] == float('inf'):
                    stats['min_time'] = 0.0
            
            return method_stats
    
    def export_metrics(self, filename: str = None) -> str:
        """Export performance metrics to JSON file."""
        if filename is None:
            filename = f"performance_metrics_{int(time.time())}.json"
        
        with self.lock:
            export_data = {
                'export_timestamp': time.time(),
                'export_date': datetime.now().isoformat(),
                'task_metrics': [asdict(task) for task in self.task_metrics],
                'system_snapshots': [asdict(snapshot) for snapshot in self.system_snapshots],
                'performance_report': asdict(self.get_performance_report()),
                'method_comparison': self.get_method_performance_comparison(),
                'real_time_stats': self.get_real_time_stats()
            }
            
            try:
                with open(filename, 'w') as f:
                    json.dump(export_data, f, indent=2)
                
                logger.info(f"Performance metrics exported to {filename}")
                return filename
                
            except Exception as e:
                logger.error(f"Failed to export metrics: {e}")
                return ""
    
    def clear_history(self):
        """Clear all performance history."""
        with self.lock:
            self.task_metrics.clear()
            self.system_snapshots.clear()
            self._analytics_cache.clear()
            logger.info("Performance history cleared")
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get a summary for dashboard display."""
        real_time_stats = self.get_real_time_stats()
        method_comparison = self.get_method_performance_comparison()
        
        return {
            'current_status': real_time_stats.get('performance_status', 'unknown'),
            'recent_tasks': real_time_stats.get('recent_tasks', 0),
            'success_rate': real_time_stats.get('success_rate', 0.0),
            'avg_execution_time': real_time_stats.get('average_execution_time', 0.0),
            'system_cpu': real_time_stats.get('system_cpu_avg', 0.0),
            'system_memory': real_time_stats.get('system_memory_avg', 0.0),
            'top_methods': sorted(method_comparison.items(), 
                                key=lambda x: x[1].get('total_tasks', 0), 
                                reverse=True)[:3],
            'total_history_size': len(self.task_metrics)
        }

# Global performance dashboard instance
performance_dashboard = PerformanceDashboard()