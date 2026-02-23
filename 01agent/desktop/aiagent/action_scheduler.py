"""
Action scheduling and execution management for the AI Agent.
"""
import time
import asyncio
from typing import Dict, List, Any
from dataclasses import dataclass
from resource_monitor import ResourceMonitor, SystemMetrics


@dataclass
class ActionMetrics:
    action_type: str
    execution_time: float
    success_rate: float
    resource_usage: Dict[str, float]
    dependencies: List[str]
    priority: float = 5.0
    cooldown: float = 0.0


class ActionScheduler:
    def __init__(self):
        self.resource_monitor = ResourceMonitor()
        self.action_history: Dict[str, List[ActionMetrics]] = {}
        self.action_queue = asyncio.PriorityQueue()
        self.executing_actions: Dict[str, int] = {}
        self.max_concurrent_actions = 5
        self.lock = asyncio.Lock()
        
        # Performance thresholds
        self.thresholds = {
            'cpu_percent': 80,
            'memory_percent': 85,
            'io_rate': 50 * 1024 * 1024,  # 50MB/s
            'max_execution_time': 30.0,    # 30 seconds
            'min_success_rate': 0.7        # 70%
        }
    
    async def schedule_action(self, action_type: str, action_func, *args, **kwargs) -> Any:
        async with self.lock:
            # Get current system metrics
            metrics = await self.resource_monitor.get_current_metrics()
            
            # Calculate action priority
            priority = await self._calculate_action_priority(action_type, metrics)
            
            # Check if action can be executed
            if not await self._can_execute_action(action_type, metrics):
                raise RuntimeError(f"Cannot execute {action_type} due to resource constraints")
            
            # Create action task
            task = asyncio.create_task(self._execute_action(action_type, action_func, *args, **kwargs))
            await self.action_queue.put((priority, task))
            
            return await task
    
    async def _execute_action(self, action_type: str, action_func, *args, **kwargs) -> Any:
        start_time = time.time()
        start_metrics = await self.resource_monitor.get_current_metrics()
        success = False
        result = None
        
        try:
            # Increment executing actions counter
            self.executing_actions[action_type] = self.executing_actions.get(action_type, 0) + 1
            
            # Execute the action
            result = await action_func(*args, **kwargs)
            success = True
            return result
        except Exception as e:
            success = False
            raise e
        finally:
            # Record metrics
            end_time = time.time()
            end_metrics = await self.resource_monitor.get_current_metrics()
            
            # Calculate resource usage
            resource_usage = {
                'cpu_delta': end_metrics.cpu_percent - start_metrics.cpu_percent,
                'memory_delta': end_metrics.memory_percent - start_metrics.memory_percent,
                'io_delta': sum(end_metrics.disk_io.values()) - sum(start_metrics.disk_io.values()),
                'execution_time': end_time - start_time
            }
            
            # Update action history
            await self._update_action_history(action_type, success, resource_usage)
            
            # Decrement executing actions counter
            self.executing_actions[action_type] = max(0, self.executing_actions.get(action_type, 1) - 1)
    
    async def _calculate_action_priority(self, action_type: str, current_metrics: SystemMetrics) -> float:
        if action_type not in self.action_history:
            return 5.0
        
        recent_actions = self.action_history[action_type][-10:]  # Last 10 executions
        if not recent_actions:
            return 5.0
        
        # Calculate priority components
        avg_execution_time = sum(a.execution_time for a in recent_actions) / len(recent_actions)
        success_rate = sum(1 for a in recent_actions if a.success_rate > 0.5) / len(recent_actions)
        resource_impact = sum(sum(a.resource_usage.values()) for a in recent_actions) / len(recent_actions)
        
        # Normalize and weight components
        time_score = 1.0 - min(1.0, avg_execution_time / self.thresholds['max_execution_time'])
        success_score = success_rate
        resource_score = 1.0 - min(1.0, resource_impact / (sum(self.thresholds.values()) / len(self.thresholds)))
        
        # Calculate final priority (0-10)
        priority = (time_score * 0.3 + success_score * 0.4 + resource_score * 0.3) * 10
        return max(0.1, min(10.0, priority))
    
    async def _can_execute_action(self, action_type: str, metrics: SystemMetrics) -> bool:
        # Check system resource thresholds
        if (metrics.cpu_percent > self.thresholds['cpu_percent'] or
            metrics.memory_percent > self.thresholds['memory_percent'] or
            sum(metrics.disk_io.values()) > self.thresholds['io_rate']):
            return False
        
        # Check concurrent action limits
        if sum(self.executing_actions.values()) >= self.max_concurrent_actions:
            return False
        
        # Check action type specific metrics
        if action_type in self.action_history:
            recent_actions = self.action_history[action_type][-5:]  # Last 5 executions
            if recent_actions:
                recent_success_rate = sum(1 for a in recent_actions if a.success_rate > 0.5) / len(recent_actions)
                if recent_success_rate < self.thresholds['min_success_rate']:
                    return False
        
        return True
    
    async def _update_action_history(self, action_type: str, success: bool, resource_usage: Dict[str, float]):
        async with self.lock:
            if action_type not in self.action_history:
                self.action_history[action_type] = []
            
            metrics = ActionMetrics(
                action_type=action_type,
                execution_time=resource_usage['execution_time'],
                success_rate=1.0 if success else 0.0,
                resource_usage=resource_usage,
                dependencies=[],  # Can be updated based on action dependencies
                priority=await self._calculate_action_priority(action_type, await self.resource_monitor.get_current_metrics())
            )
            
            self.action_history[action_type].append(metrics)
            if len(self.action_history[action_type]) > 100:
                self.action_history[action_type].pop(0)