import asyncio
import subprocess
import os
import json
import time
import tempfile
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import threading
import queue
import platform
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import psutil

logger = logging.getLogger(__name__)

class ScriptType(Enum):
    """Types of background scripts."""
    POWERSHELL = "ps1"
    BATCH = "bat"
    PYTHON = "py"
    JAVASCRIPT = "js"
    VBS = "vbs"
    BASH = "sh"

@dataclass
class BackgroundTask:
    """Represents a background task."""
    task_id: str
    script_type: ScriptType
    script_content: str
    parameters: Dict[str, Any]
    priority: int = 5
    timeout: float = 60.0
    created_at: float = 0.0
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    status: str = "pending"  # pending, running, completed, failed, timeout
    result: Optional[Dict[str, Any]] = None
    process: Optional[subprocess.Popen] = None

class BackgroundScriptExecutor:
    """High-performance background script execution system."""
    
    def __init__(self, max_concurrent_tasks: int = 8):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.task_queue = asyncio.PriorityQueue()
        self.running_tasks: Dict[str, BackgroundTask] = {}
        self.completed_tasks: Dict[str, BackgroundTask] = {}
        self.task_counter = 0
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_tasks)
        self.process_executor = ProcessPoolExecutor(max_workers=max_concurrent_tasks // 2)
        
        # System detection
        self.system = platform.system().lower()
        self.temp_dir = tempfile.gettempdir()
        
        # Pre-built script templates
        self.script_templates = self._initialize_script_templates()
        
        # Start background worker
        self.worker_task = None
        self.is_running = False
        
    def _initialize_script_templates(self) -> Dict[str, Dict[str, str]]:
        """Initialize pre-built script templates for common tasks."""
        templates = {
            "file_operations": {
                "create_multiple_files": {
                    ScriptType.POWERSHELL.value: '''
param($files, $content)
foreach ($file in $files) {
    New-Item -Path $file -ItemType File -Force | Out-Null
    if ($content) { Set-Content -Path $file -Value $content }
}
Write-Output "Created $($files.Count) files"
''',
                    ScriptType.PYTHON.value: '''
import os
import sys
import json

files = json.loads(sys.argv[1])
content = sys.argv[2] if len(sys.argv) > 2 else ""

for file_path in files:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        f.write(content)

print(f"Created {len(files)} files")
''',
                    ScriptType.BATCH.value: '''
@echo off
setlocal enabledelayedexpansion
set count=0
for %%f in (%*) do (
    echo. > "%%f"
    set /a count+=1
)
echo Created !count! files
'''
                },
                "bulk_rename": {
                    ScriptType.POWERSHELL.value: '''
param($directory, $pattern, $replacement)
Get-ChildItem -Path $directory -Filter $pattern | ForEach-Object {
    $newName = $_.Name -replace $pattern, $replacement
    Rename-Item -Path $_.FullName -NewName $newName
}
Write-Output "Renamed files in $directory"
''',
                    ScriptType.PYTHON.value: '''
import os
import re
import sys

directory = sys.argv[1]
pattern = sys.argv[2]
replacement = sys.argv[3]

count = 0
for filename in os.listdir(directory):
    if re.search(pattern, filename):
        new_name = re.sub(pattern, replacement, filename)
        old_path = os.path.join(directory, filename)
        new_path = os.path.join(directory, new_name)
        os.rename(old_path, new_path)
        count += 1

print(f"Renamed {count} files")
'''
                },
                "organize_downloads": {
                    ScriptType.POWERSHELL.value: '''
param($downloadsPath)
if (-not $downloadsPath) { $downloadsPath = "$env:USERPROFILE\\Downloads" }

$extensions = @{
    "Images" = @(".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp")
    "Documents" = @(".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt")
    "Videos" = @(".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm")
    "Audio" = @(".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma")
    "Archives" = @(".zip", ".rar", ".7z", ".tar", ".gz", ".bz2")
    "Executables" = @(".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm")
}

$moved = 0
foreach ($category in $extensions.Keys) {
    $categoryPath = Join-Path $downloadsPath $category
    if (-not (Test-Path $categoryPath)) { New-Item -Path $categoryPath -ItemType Directory | Out-Null }
    
    foreach ($ext in $extensions[$category]) {
        Get-ChildItem -Path $downloadsPath -Filter "*$ext" | ForEach-Object {
            Move-Item -Path $_.FullName -Destination $categoryPath -Force
            $moved++
        }
    }
}

Write-Output "Organized $moved files into categories"
'''
                }
            },
            "system_maintenance": {
                "cleanup_temp": {
                    ScriptType.POWERSHELL.value: '''
$tempPaths = @(
    $env:TEMP,
    "$env:USERPROFILE\\AppData\\Local\\Temp",
    "$env:WINDIR\\Temp",
    "$env:USERPROFILE\\AppData\\Local\\Microsoft\\Windows\\INetCache"
)

$totalSize = 0
$deletedFiles = 0

foreach ($path in $tempPaths) {
    if (Test-Path $path) {
        Get-ChildItem -Path $path -Recurse -Force -ErrorAction SilentlyContinue | ForEach-Object {
            try {
                $totalSize += $_.Length
                Remove-Item -Path $_.FullName -Force -Recurse -ErrorAction SilentlyContinue
                $deletedFiles++
            } catch {}
        }
    }
}

Write-Output "Cleaned $deletedFiles files, freed $([math]::Round($totalSize/1MB, 2)) MB"
''',
                    ScriptType.PYTHON.value: '''
import os
import shutil
import tempfile

def get_size(path):
    total = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total += os.path.getsize(filepath)
                except:
                    pass
    except:
        pass
    return total

temp_dirs = [
    tempfile.gettempdir(),
    os.path.expanduser("~/AppData/Local/Temp") if os.name == 'nt' else "/tmp"
]

total_size = 0
deleted_files = 0

for temp_dir in temp_dirs:
    if os.path.exists(temp_dir):
        for item in os.listdir(temp_dir):
            item_path = os.path.join(temp_dir, item)
            try:
                if os.path.isfile(item_path):
                    total_size += os.path.getsize(item_path)
                    os.remove(item_path)
                    deleted_files += 1
                elif os.path.isdir(item_path):
                    total_size += get_size(item_path)
                    shutil.rmtree(item_path)
                    deleted_files += 1
            except:
                pass

print(f"Cleaned {deleted_files} items, freed {total_size/1024/1024:.2f} MB")
'''
                },
                "system_info_report": {
                    ScriptType.POWERSHELL.value: '''
$info = @{
    "System" = Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, TotalPhysicalMemory
    "CPU" = Get-WmiObject -Class Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors
    "Disk" = Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, Size, FreeSpace
    "Network" = Get-NetAdapter | Where-Object Status -eq 'Up' | Select-Object Name, LinkSpeed
    "Processes" = Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Name, CPU, WorkingSet
}

$info | ConvertTo-Json -Depth 3
'''
                }
            },
            "automation_helpers": {
                "batch_screenshot": {
                    ScriptType.PYTHON.value: '''
import time
import os
from PIL import ImageGrab
import sys

count = int(sys.argv[1]) if len(sys.argv) > 1 else 5
interval = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0
output_dir = sys.argv[3] if len(sys.argv) > 3 else os.path.expanduser("~/Desktop/Screenshots")

os.makedirs(output_dir, exist_ok=True)

for i in range(count):
    screenshot = ImageGrab.grab()
    filename = f"screenshot_{int(time.time())}_{i+1}.png"
    filepath = os.path.join(output_dir, filename)
    screenshot.save(filepath)
    
    if i < count - 1:
        time.sleep(interval)

print(f"Captured {count} screenshots in {output_dir}")
'''
                },
                "monitor_process": {
                    ScriptType.PYTHON.value: '''
import psutil
import time
import json
import sys

process_name = sys.argv[1]
duration = int(sys.argv[2]) if len(sys.argv) > 2 else 60
interval = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0

data = []
start_time = time.time()

while time.time() - start_time < duration:
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
        try:
            if process_name.lower() in proc.info['name'].lower():
                data.append({
                    'timestamp': time.time(),
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu_percent': proc.info['cpu_percent'],
                    'memory_mb': proc.info['memory_info'].rss / 1024 / 1024
                })
        except:
            pass
    
    time.sleep(interval)

print(json.dumps(data))
'''
                }
            }
        }
        return templates
    
    async def start(self):
        """Start the background executor."""
        if not self.is_running:
            self.is_running = True
            self.worker_task = asyncio.create_task(self._worker_loop())
            logger.info("Background script executor started")
    
    async def stop(self):
        """Stop the background executor."""
        self.is_running = False
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
        
        # Clean up running tasks
        for task in self.running_tasks.values():
            if task.process and task.process.poll() is None:
                task.process.terminate()
        
        self.executor.shutdown(wait=False)
        self.process_executor.shutdown(wait=False)
        logger.info("Background script executor stopped")
    
    async def _worker_loop(self):
        """Main worker loop for processing background tasks."""
        while self.is_running:
            try:
                # Check if we can start more tasks
                if len(self.running_tasks) < self.max_concurrent_tasks:
                    try:
                        # Get next task from queue (with timeout to allow periodic cleanup)
                        priority, task = await asyncio.wait_for(
                            self.task_queue.get(), 
                            timeout=1.0
                        )
                        
                        # Start the task
                        await self._start_task(task)
                        
                    except asyncio.TimeoutError:
                        pass  # No tasks available, continue to cleanup
                
                # Clean up completed tasks
                await self._cleanup_completed_tasks()
                
                # Small delay to prevent busy waiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in worker loop: {e}")
                await asyncio.sleep(1.0)
    
    async def _start_task(self, task: BackgroundTask):
        """Start executing a background task."""
        try:
            task.status = "running"
            task.started_at = time.time()
            self.running_tasks[task.task_id] = task
            
            # Execute the task in a separate thread
            future = self.executor.submit(self._execute_task_sync, task)
            
            # Monitor the task completion
            asyncio.create_task(self._monitor_task(task, future))
            
        except Exception as e:
            task.status = "failed"
            task.result = {"success": False, "error": str(e)}
            logger.error(f"Failed to start task {task.task_id}: {e}")
    
    async def _monitor_task(self, task: BackgroundTask, future):
        """Monitor a task's execution."""
        try:
            # Wait for the task to complete
            result = await asyncio.get_event_loop().run_in_executor(None, future.result)
            
            task.status = "completed"
            task.completed_at = time.time()
            task.result = result
            
        except Exception as e:
            task.status = "failed"
            task.completed_at = time.time()
            task.result = {"success": False, "error": str(e)}
            
        finally:
            # Move task from running to completed
            if task.task_id in self.running_tasks:
                del self.running_tasks[task.task_id]
                self.completed_tasks[task.task_id] = task
    
    def _execute_task_sync(self, task: BackgroundTask) -> Dict[str, Any]:
        """Execute a task synchronously (runs in thread)."""
        try:
            start_time = time.time()
            
            # Create temporary script file
            script_file = self._create_script_file(task)
            
            try:
                # Execute the script
                result = self._run_script(script_file, task)
                
                execution_time = time.time() - start_time
                
                return {
                    "success": True,
                    "output": result.get("output", ""),
                    "error": result.get("error", ""),
                    "execution_time": execution_time,
                    "return_code": result.get("return_code", 0)
                }
                
            finally:
                # Clean up script file
                try:
                    os.remove(script_file)
                except:
                    pass
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_time": time.time() - start_time
            }
    
    def _create_script_file(self, task: BackgroundTask) -> str:
        """Create a temporary script file."""
        script_extension = task.script_type.value
        script_file = os.path.join(
            self.temp_dir, 
            f"bg_script_{task.task_id}.{script_extension}"
        )
        
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(task.script_content)
        
        return script_file
    
    def _run_script(self, script_file: str, task: BackgroundTask) -> Dict[str, Any]:
        """Run a script file."""
        try:
            # Determine command based on script type
            if task.script_type == ScriptType.POWERSHELL:
                cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_file]
            elif task.script_type == ScriptType.BATCH:
                cmd = ["cmd", "/c", script_file]
            elif task.script_type == ScriptType.PYTHON:
                cmd = ["python", script_file]
            elif task.script_type == ScriptType.JAVASCRIPT:
                cmd = ["node", script_file]
            elif task.script_type == ScriptType.VBS:
                cmd = ["cscript", "//NoLogo", script_file]
            elif task.script_type == ScriptType.BASH:
                cmd = ["bash", script_file]
            else:
                raise ValueError(f"Unsupported script type: {task.script_type}")
            
            # Add parameters if any
            if task.parameters:
                for key, value in task.parameters.items():
                    if isinstance(value, (list, dict)):
                        cmd.append(json.dumps(value))
                    else:
                        cmd.append(str(value))
            
            # Execute with timeout
            creation_flags = subprocess.CREATE_NO_WINDOW if self.system == "windows" else 0
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=creation_flags
            )
            
            task.process = process
            
            try:
                stdout, stderr = process.communicate(timeout=task.timeout)
                return_code = process.returncode
                
                return {
                    "output": stdout,
                    "error": stderr,
                    "return_code": return_code
                }
                
            except subprocess.TimeoutExpired:
                process.kill()
                task.status = "timeout"
                return {
                    "output": "",
                    "error": f"Script timed out after {task.timeout} seconds",
                    "return_code": -1
                }
                
        except Exception as e:
            return {
                "output": "",
                "error": str(e),
                "return_code": -1
            }
    
    async def _cleanup_completed_tasks(self):
        """Clean up old completed tasks."""
        current_time = time.time()
        max_age = 300  # 5 minutes
        
        expired_tasks = [
            task_id for task_id, task in self.completed_tasks.items()
            if task.completed_at and (current_time - task.completed_at) > max_age
        ]
        
        for task_id in expired_tasks:
            del self.completed_tasks[task_id]
    
    async def execute_script(self, script_content: str, script_type: ScriptType, 
                           parameters: Dict[str, Any] = None, priority: int = 5, 
                           timeout: float = 60.0) -> str:
        """Execute a custom script in the background."""
        task_id = f"task_{self.task_counter}"
        self.task_counter += 1
        
        task = BackgroundTask(
            task_id=task_id,
            script_type=script_type,
            script_content=script_content,
            parameters=parameters or {},
            priority=priority,
            timeout=timeout,
            created_at=time.time()
        )
        
        # Add to queue (lower priority number = higher priority)
        await self.task_queue.put((10 - priority, task))
        
        return task_id
    
    async def execute_template(self, category: str, template_name: str, 
                             parameters: Dict[str, Any] = None, 
                             preferred_script_type: Optional[ScriptType] = None,
                             priority: int = 5, timeout: float = 60.0) -> str:
        """Execute a pre-built template script."""
        if category not in self.script_templates:
            raise ValueError(f"Unknown template category: {category}")
        
        if template_name not in self.script_templates[category]:
            raise ValueError(f"Unknown template: {template_name}")
        
        templates = self.script_templates[category][template_name]
        
        # Choose script type
        if preferred_script_type and preferred_script_type.value in templates:
            script_type = preferred_script_type
        else:
            # Choose best available script type for current system
            if self.system == "windows":
                if ScriptType.POWERSHELL.value in templates:
                    script_type = ScriptType.POWERSHELL
                elif ScriptType.PYTHON.value in templates:
                    script_type = ScriptType.PYTHON
                elif ScriptType.BATCH.value in templates:
                    script_type = ScriptType.BATCH
                else:
                    script_type = ScriptType(list(templates.keys())[0])
            else:
                if ScriptType.PYTHON.value in templates:
                    script_type = ScriptType.PYTHON
                elif ScriptType.BASH.value in templates:
                    script_type = ScriptType.BASH
                else:
                    script_type = ScriptType(list(templates.keys())[0])
        
        script_content = templates[script_type.value]
        
        return await self.execute_script(
            script_content=script_content,
            script_type=script_type,
            parameters=parameters,
            priority=priority,
            timeout=timeout
        )
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a task."""
        # Check running tasks
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            return {
                "task_id": task_id,
                "status": task.status,
                "created_at": task.created_at,
                "started_at": task.started_at,
                "progress": "running"
            }
        
        # Check completed tasks
        if task_id in self.completed_tasks:
            task = self.completed_tasks[task_id]
            return {
                "task_id": task_id,
                "status": task.status,
                "created_at": task.created_at,
                "started_at": task.started_at,
                "completed_at": task.completed_at,
                "result": task.result
            }
        
        return None
    
    async def wait_for_task(self, task_id: str, timeout: float = 60.0) -> Optional[Dict[str, Any]]:
        """Wait for a task to complete."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_task_status(task_id)
            if status and status["status"] in ["completed", "failed", "timeout"]:
                return status
            
            await asyncio.sleep(0.1)
        
        return None
    
    def list_running_tasks(self) -> List[Dict[str, Any]]:
        """List all running tasks."""
        return [
            {
                "task_id": task.task_id,
                "status": task.status,
                "created_at": task.created_at,
                "started_at": task.started_at,
                "script_type": task.script_type.value,
                "priority": task.priority
            }
            for task in self.running_tasks.values()
        ]
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        total_completed = len(self.completed_tasks)
        successful_tasks = sum(1 for task in self.completed_tasks.values() 
                             if task.result and task.result.get("success", False))
        
        avg_execution_time = 0
        if self.completed_tasks:
            total_time = sum(
                task.result.get("execution_time", 0) 
                for task in self.completed_tasks.values() 
                if task.result
            )
            avg_execution_time = total_time / len(self.completed_tasks)
        
        return {
            "total_completed": total_completed,
            "successful_tasks": successful_tasks,
            "success_rate": successful_tasks / max(total_completed, 1),
            "average_execution_time": avg_execution_time,
            "running_tasks": len(self.running_tasks),
            "queue_size": self.task_queue.qsize()
        }

    async def create_file_fast(self, file_path: str) -> Dict[str, Any]:
        """Create a file quickly."""
        try:
            start_time = time.time()
            
            # Ensure directory exists
            directory = os.path.dirname(file_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            
            # Create file
            with open(file_path, 'w') as f:
                f.write("")  # Create empty file
            
            execution_time = time.time() - start_time
            
            return {
                'success': True,
                'output': f"File created: {file_path}",
                'execution_time': execution_time,
                'method': 'create_file_script',
                'file_path': file_path
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'create_file_script'
            }

# Global background executor instance
background_executor = BackgroundScriptExecutor()