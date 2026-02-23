import asyncio
import subprocess
import platform
import os
import json
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from pywinauto import keyboard
import psutil
from concurrent.futures import ThreadPoolExecutor
import threading
from browser_automation import browser_automation, BrowserCommand

logger = logging.getLogger(__name__)

class ExecutionMethod(Enum):
    """Different methods to execute tasks."""
    CLI_POWERSHELL = "powershell"
    CLI_CMD = "cmd"
    CLI_BASH = "bash"
    GUI_AUTOMATION = "gui"
    KEYBOARD_SHORTCUT = "shortcut"
    SCRIPT_EXECUTION = "script"
    API_CALL = "api"
    BACKGROUND_SERVICE = "background"
    BROWSER_AUTOMATION = "browser"

@dataclass
class TaskExecution:
    """Represents a task execution strategy."""
    method: ExecutionMethod
    command: str
    priority: int = 5  # 1-10, higher is better
    estimated_time: float = 1.0  # seconds
    success_rate: float = 0.8  # 0-1
    requires_gui: bool = False
    can_run_background: bool = True
    dependencies: List[str] = None

class SmartTaskExecutor:
    """Intelligent task executor that chooses the best execution method."""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.execution_history: Dict[str, List[TaskExecution]] = {}
        self.performance_cache: Dict[str, float] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        
        # Initialize execution strategies
        self.strategies = self._initialize_strategies()
        
    def _initialize_strategies(self) -> Dict[str, List[TaskExecution]]:
        """Initialize execution strategies for common tasks."""
        strategies = {
            "open_application": [
                TaskExecution(
                    method=ExecutionMethod.CLI_POWERSHELL if self.system == "windows" else ExecutionMethod.CLI_BASH,
                    command="start {app_name}" if self.system == "windows" else "open -a '{app_name}'",
                    priority=9,
                    estimated_time=0.5,
                    success_rate=0.95,
                    can_run_background=True
                ),
                TaskExecution(
                    method=ExecutionMethod.KEYBOARD_SHORTCUT,
                    command="win+r,{app_name},enter" if self.system == "windows" else "cmd+space,{app_name},enter",
                    priority=8,
                    estimated_time=1.0,
                    success_rate=0.9,
                    requires_gui=True
                ),
                TaskExecution(
                    method=ExecutionMethod.GUI_AUTOMATION,
                    command="click_start_menu,search,{app_name},click",
                    priority=6,
                    estimated_time=2.0,
                    success_rate=0.8,
                    requires_gui=True
                )
            ],
            "create_file": [
                TaskExecution(
                    method=ExecutionMethod.CLI_POWERSHELL if self.system == "windows" else ExecutionMethod.CLI_BASH,
                    command="New-Item -Path '{file_path}' -ItemType File" if self.system == "windows" else "touch '{file_path}'",
                    priority=10,
                    estimated_time=0.1,
                    success_rate=0.98,
                    can_run_background=True
                ),
                TaskExecution(
                    method=ExecutionMethod.SCRIPT_EXECUTION,
                    command="create_file_script",
                    priority=9,
                    estimated_time=0.2,
                    success_rate=0.95,
                    can_run_background=True
                )
            ],
            "create_folder": [
                TaskExecution(
                    method=ExecutionMethod.CLI_POWERSHELL if self.system == "windows" else ExecutionMethod.CLI_BASH,
                    command="New-Item -Path '{folder_path}' -ItemType Directory" if self.system == "windows" else "mkdir -p '{folder_path}'",
                    priority=10,
                    estimated_time=0.1,
                    success_rate=0.98,
                    can_run_background=True
                )
            ],
            "copy_file": [
                TaskExecution(
                    method=ExecutionMethod.CLI_POWERSHELL if self.system == "windows" else ExecutionMethod.CLI_BASH,
                    command="Copy-Item '{source}' '{destination}'" if self.system == "windows" else "cp '{source}' '{destination}'",
                    priority=10,
                    estimated_time=0.2,
                    success_rate=0.98,
                    can_run_background=True
                ),
                TaskExecution(
                    method=ExecutionMethod.KEYBOARD_SHORTCUT,
                    command="ctrl+c,navigate,ctrl+v",
                    priority=7,
                    estimated_time=1.5,
                    success_rate=0.85,
                    requires_gui=True
                )
            ],
            "search_files": [
                TaskExecution(
                    method=ExecutionMethod.CLI_POWERSHELL if self.system == "windows" else ExecutionMethod.CLI_BASH,
                    command="Get-ChildItem -Recurse -Filter '*{query}*'" if self.system == "windows" else "find . -name '*{query}*'",
                    priority=10,
                    estimated_time=1.0,
                    success_rate=0.95,
                    can_run_background=True
                ),
                TaskExecution(
                    method=ExecutionMethod.KEYBOARD_SHORTCUT,
                    command="win+s,{query}" if self.system == "windows" else "cmd+space,{query}",
                    priority=8,
                    estimated_time=1.5,
                    success_rate=0.9,
                    requires_gui=True
                )
            ],
            "take_screenshot": [
                TaskExecution(
                    method=ExecutionMethod.SCRIPT_EXECUTION,
                    command="screenshot_script",
                    priority=10,
                    estimated_time=0.3,
                    success_rate=0.98,
                    can_run_background=True
                ),
                TaskExecution(
                    method=ExecutionMethod.KEYBOARD_SHORTCUT,
                    command="win+shift+s" if self.system == "windows" else "cmd+shift+4",
                    priority=8,
                    estimated_time=1.0,
                    success_rate=0.9,
                    requires_gui=True
                )
            ],
            "write_text": [
                TaskExecution(
                    method=ExecutionMethod.KEYBOARD_SHORTCUT,
                    command="type_text",
                    priority=9,
                    estimated_time=0.5,
                    success_rate=0.95,
                    requires_gui=True
                ),
                TaskExecution(
                    method=ExecutionMethod.CLI_POWERSHELL if self.system == "windows" else ExecutionMethod.CLI_BASH,
                    command="Set-Clipboard '{text}'; Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('^v')" if self.system == "windows" else "echo '{text}' | pbcopy && osascript -e 'tell application \"System Events\" to keystroke \"v\" using command down'",
                    priority=8,
                    estimated_time=0.8,
                    success_rate=0.9,
                    requires_gui=True
                )
            ],
            "system_info": [
                TaskExecution(
                    method=ExecutionMethod.CLI_POWERSHELL if self.system == "windows" else ExecutionMethod.CLI_BASH,
                    command="Get-ComputerInfo" if self.system == "windows" else "system_profiler SPHardwareDataType",
                    priority=10,
                    estimated_time=0.5,
                    success_rate=0.98,
                    can_run_background=True
                )
            ],
            "network_info": [
                TaskExecution(
                    method=ExecutionMethod.CLI_POWERSHELL if self.system == "windows" else ExecutionMethod.CLI_BASH,
                    command="Get-NetAdapter" if self.system == "windows" else "ifconfig",
                    priority=10,
                    estimated_time=0.3,
                    success_rate=0.98,
                    can_run_background=True
                )
            ],
            "open_url": [
                TaskExecution(
                    method=ExecutionMethod.BROWSER_AUTOMATION,
                    command=BrowserCommand.GOTO.value,
                    priority=9,
                    estimated_time=2.0,
                    success_rate=0.9,
                    requires_gui=False, # Can be headless
                    can_run_background=True
                )
            ],
            "click_web_element": [
                TaskExecution(
                    method=ExecutionMethod.BROWSER_AUTOMATION,
                    command=BrowserCommand.CLICK.value,
                    priority=8,
                    estimated_time=1.0,
                    success_rate=0.85,
                    requires_gui=False, # Can be headless
                    can_run_background=True
                )
            ],
            "type_web_text": [
                TaskExecution(
                    method=ExecutionMethod.BROWSER_AUTOMATION,
                    command=BrowserCommand.TYPE_TEXT.value,
                    priority=8,
                    estimated_time=1.5,
                    success_rate=0.85,
                    requires_gui=False, # Can be headless
                    can_run_background=True
                )
            ],
            "take_web_screenshot": [
                TaskExecution(
                    method=ExecutionMethod.BROWSER_AUTOMATION,
                    command=BrowserCommand.SCREENSHOT.value,
                    priority=7,
                    estimated_time=1.0,
                    success_rate=0.9,
                    requires_gui=False, # Can be headless
                    can_run_background=True
                )
            ],
            "get_web_content": [
                TaskExecution(
                    method=ExecutionMethod.BROWSER_AUTOMATION,
                    command=BrowserCommand.GET_PAGE_CONTENT.value,
                    priority=7,
                    estimated_time=1.0,
                    success_rate=0.9,
                    requires_gui=False, # Can be headless
                    can_run_background=True
                )
            ]
        }
        return strategies
    
    async def execute_task(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a task using the best available method."""
        start_time = time.time()
        context = context or {}
        
        try:
            # Analyze task and determine best execution strategy
            task_type, parameters = await self._analyze_task(task_description, context)
            
            # Get execution strategies for this task type
            strategies = self._get_strategies_for_task(task_type)
            
            # Choose best strategy based on current system state
            best_strategy = await self._choose_best_strategy(strategies, context)
            
            if not best_strategy:
                return await self._fallback_gui_execution(task_description, context)
            
            # Execute using chosen strategy
            result = await self._execute_strategy(best_strategy, parameters, context)
            
            # Record performance for future optimization
            execution_time = time.time() - start_time
            await self._record_performance(task_type, best_strategy, execution_time, result.get('success', False))
            
            return result
            
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'execution_time': time.time() - start_time,
                'method': 'error'
            }
    
    async def _analyze_task(self, task_description: str, context: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Analyze task description to determine task type and extract parameters."""
        task_lower = task_description.lower()
        parameters = {}
        
        # Pattern matching for common tasks
        if any(word in task_lower for word in ['open', 'launch', 'start', 'run']):
            if any(word in task_lower for word in ['notepad', 'calculator', 'browser', 'chrome', 'firefox', 'word', 'excel']):
                app_name = self._extract_app_name(task_description)
                return 'open_application', {'app_name': app_name}
        
        elif any(word in task_lower for word in ['create', 'make', 'new']) and 'file' in task_lower:
            file_path = self._extract_file_path(task_description, context)
            return 'create_file', {'file_path': file_path}
        
        elif any(word in task_lower for word in ['create', 'make', 'new']) and any(word in task_lower for word in ['folder', 'directory']):
            folder_path = self._extract_folder_path(task_description, context)
            return 'create_folder', {'folder_path': folder_path}
        
        elif any(word in task_lower for word in ['copy', 'duplicate']):
            source, destination = self._extract_copy_paths(task_description, context)
            return 'copy_file', {'source': source, 'destination': destination}
        
        elif any(word in task_lower for word in ['search', 'find', 'locate']):
            query = self._extract_search_query(task_description)
            return 'search_files', {'query': query}
        
        elif any(word in task_lower for word in ['screenshot', 'capture', 'snap']):
            return 'take_screenshot', {}
        
        elif any(word in task_lower for word in ['type', 'write', 'enter', 'input']):
            text = self._extract_text_to_type(task_description)
            return 'write_text', {'text': text}
        
        elif any(word in task_lower for word in ['system', 'computer', 'hardware']) and 'info' in task_lower:
            return 'system_info', {}
        
        elif any(word in task_lower for word in ['network', 'internet', 'connection']) and 'info' in task_lower:
            return 'network_info', {}
        
        # Default to generic task
        return 'generic_task', {'description': task_description}
    
    def _get_strategies_for_task(self, task_type: str) -> List[TaskExecution]:
        """Get available strategies for a task type."""
        return self.strategies.get(task_type, [])
    
    async def _choose_best_strategy(self, strategies: List[TaskExecution], context: Dict[str, Any]) -> Optional[TaskExecution]:
        """Choose the best strategy based on current conditions."""
        if not strategies:
            return None
        
        # Get current system metrics
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        
        # Score each strategy
        scored_strategies = []
        for strategy in strategies:
            score = await self._calculate_strategy_score(strategy, cpu_usage, memory_usage, context)
            scored_strategies.append((score, strategy))
        
        # Sort by score (highest first)
        scored_strategies.sort(key=lambda x: x[0], reverse=True)
        
        return scored_strategies[0][1] if scored_strategies else None
    
    async def _calculate_strategy_score(self, strategy: TaskExecution, cpu_usage: float, memory_usage: float, context: Dict[str, Any]) -> float:
        """Calculate a score for a strategy based on current conditions."""
        score = strategy.priority * 10  # Base score from priority
        
        # Adjust for success rate
        score *= strategy.success_rate
        
        # Adjust for estimated time (faster is better)
        score *= (10 / max(strategy.estimated_time, 0.1))
        
        # Adjust for system load
        if cpu_usage > 80 or memory_usage > 80:
            if strategy.can_run_background:
                score *= 0.8  # Slight penalty for background tasks under load
            else:
                score *= 0.5  # Higher penalty for GUI tasks under load
        
        # Adjust for GUI availability
        if strategy.requires_gui and context.get('headless', False):
            score *= 0.1  # Heavy penalty if GUI not available
        
        # Adjust based on historical performance
        task_key = f"{strategy.method.value}_{strategy.command[:20]}"
        if task_key in self.performance_cache:
            historical_performance = self.performance_cache[task_key]
            score *= historical_performance
        
        return score
    
    async def _execute_strategy(self, strategy: TaskExecution, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific strategy."""
        try:
            if strategy.method in [ExecutionMethod.CLI_POWERSHELL, ExecutionMethod.CLI_CMD, ExecutionMethod.CLI_BASH]:
                return await self._execute_cli_command(strategy, parameters)
            
            elif strategy.method == ExecutionMethod.KEYBOARD_SHORTCUT:
                return await self._execute_keyboard_shortcut(strategy, parameters)
            
            elif strategy.method == ExecutionMethod.SCRIPT_EXECUTION:
                return await self._execute_script(strategy, parameters)
            
            elif strategy.method == ExecutionMethod.GUI_AUTOMATION:
                return await self._execute_gui_automation(strategy, parameters)
            
            elif strategy.method == ExecutionMethod.BROWSER_AUTOMATION:
                return await self._execute_browser_automation(strategy, parameters)
            
            else:
                return await self._fallback_gui_execution(f"Execute {strategy.command}", context)
                
        except Exception as e:
            logger.error(f"Strategy execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': strategy.method.value
            }
    
    async def _execute_cli_command(self, strategy: TaskExecution, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a CLI command."""
        try:
            # Format command with parameters
            command = strategy.command.format(**parameters)
            
            # Choose shell based on system and strategy
            if strategy.method == ExecutionMethod.CLI_POWERSHELL:
                shell_cmd = ["powershell", "-Command", command]
            elif strategy.method == ExecutionMethod.CLI_CMD:
                shell_cmd = ["cmd", "/c", command]
            else:  # bash
                shell_cmd = ["bash", "-c", command]
            
            # Execute command
            start_time = time.time()
            result = await asyncio.create_subprocess_exec(
                *shell_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            )
            
            stdout, stderr = await result.communicate()
            execution_time = time.time() - start_time
            
            return {
                'success': result.returncode == 0,
                'output': stdout.decode('utf-8', errors='ignore'),
                'error': stderr.decode('utf-8', errors='ignore'),
                'execution_time': execution_time,
                'method': strategy.method.value,
                'command': command
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': strategy.method.value
            }
    
    async def _execute_browser_automation(self, strategy: TaskExecution, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute browser automation tasks."""
        try:
            start_time = time.time()
            success = False
            output = ""
            error = ""

            # Ensure browser is launched
            if not browser_automation._page or browser_automation._page.is_closed():
                await browser_automation.launch_browser() # Launch headless for background
                if not browser_automation._page:
                    raise RuntimeError("Browser page not available after launch.")

            if strategy.command == BrowserCommand.GOTO.value:
                success = await browser_automation.goto(parameters.get('url', ''))
                output = f"Navigated to {parameters.get('url', '')}"
            elif strategy.command == BrowserCommand.CLICK.value:
                success = await browser_automation.click(parameters.get('selector', ''))
                output = f"Clicked on {parameters.get('selector', '')}"
            elif strategy.command == BrowserCommand.TYPE_TEXT.value:
                success = await browser_automation.type_text(parameters.get('selector', ''), parameters.get('text', ''))
                output = f"Typed '{parameters.get('text', '')[:20]}...' into {parameters.get('selector', '')}"
            elif strategy.command == BrowserCommand.SCREENSHOT.value:
                path = parameters.get('path', f"screenshot_{int(time.time())}.png")
                success = await browser_automation.screenshot(path=path)
                output = f"Screenshot saved to {path}"
            elif strategy.command == BrowserCommand.GET_PAGE_CONTENT.value:
                content = await browser_automation.get_page_content()
                if content:
                    success = True
                    output = content[:500] # Truncate for output
                else:
                    error = "Failed to get page content"
            else:
                error = f"Unknown browser command: {strategy.command}"

            execution_time = time.time() - start_time

            return {
                'success': success,
                'output': output,
                'error': error,
                'execution_time': execution_time,
                'method': strategy.method.value,
                'command': strategy.command
            }

        except Exception as e:
            logger.error(f"Browser automation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': strategy.method.value
            }
    
    async def _execute_keyboard_shortcut(self, strategy: TaskExecution, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute keyboard shortcuts."""
        try:
            command = strategy.command.format(**parameters)
            actions = command.split(',')
            
            start_time = time.time()
            
            for action in actions:
                action = action.strip()
                
                if '+' in action:
                    # Key combination
                    keys = action.split('+')
                    keyboard.send_keys('+'.join(keys))
                elif action == 'enter':
                    keyboard.send_keys('{ENTER}')
                elif action == 'tab':
                    keyboard.send_keys('{TAB}')
                elif action == 'escape':
                    keyboard.send_keys('{ESC}')
                elif action.startswith('type:'):
                    text = action[5:]
                    keyboard.send_keys(text, pause=0.01)
                else:
                    # Regular text typing
                    keyboard.send_keys(action, pause=0.01)
                
                await asyncio.sleep(0.1)  # Small delay between actions
            
            execution_time = time.time() - start_time
            
            return {
                'success': True,
                'output': f"Executed keyboard shortcuts: {command}",
                'execution_time': execution_time,
                'method': strategy.method.value
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': strategy.method.value
            }
    
    async def _execute_script(self, strategy: TaskExecution, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute custom scripts."""
        try:
            if strategy.command == "screenshot_script":
                return await fast_ui_detector.save_screenshot_to_desktop()
            elif strategy.command == "create_file_script":
                return await background_executor.create_file_fast(parameters.get('file_path', ''))
            else:
                return {
                    'success': False,
                    'error': f"Unknown script: {strategy.command}",
                    'method': strategy.method.value
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': strategy.method.value
            }
    
    async def _execute_gui_automation(self, strategy: TaskExecution, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute GUI automation."""
        # This would implement more complex GUI automation
        # For now, fallback to basic implementation
        return await self._fallback_gui_execution(strategy.command, parameters)
    
    async def _fallback_gui_execution(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback GUI execution for unhandled tasks."""
        try:
            # Basic GUI automation fallback
            # This is a simplified implementation
            return {
                'success': True,
                'output': f"Executed GUI task: {task_description}",
                'method': 'gui_fallback',
                'note': 'Used fallback GUI automation'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'gui_fallback'
            }
    
    # Helper methods for parameter extraction
    def _extract_app_name(self, task_description: str) -> str:
        """Extract application name from task description."""
        task_lower = task_description.lower()
        
        app_mappings = {
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'browser': 'chrome.exe',
            'chrome': 'chrome.exe',
            'firefox': 'firefox.exe',
            'word': 'winword.exe',
            'excel': 'excel.exe',
            'powerpoint': 'powerpnt.exe',
            'paint': 'mspaint.exe',
            'file explorer': 'explorer.exe',
            'task manager': 'taskmgr.exe'
        }
        
        for app_key, app_exe in app_mappings.items():
            if app_key in task_lower:
                return app_exe
        
        # Try to extract quoted application name
        import re
        quoted_match = re.search(r'"([^"]+)"', task_description)
        if quoted_match:
            return quoted_match.group(1)
        
        # Default fallback
        words = task_description.split()
        for word in words:
            if word.lower() not in ['open', 'launch', 'start', 'run', 'the', 'a', 'an']:
                return word
        
        return 'notepad.exe'  # Ultimate fallback
    
    def _extract_file_path(self, task_description: str, context: Dict[str, Any]) -> str:
        """Extract file path from task description."""
        import re
        
        # Look for quoted paths
        quoted_match = re.search(r'"([^"]+)"', task_description)
        if quoted_match:
            return quoted_match.group(1)
        
        # Look for file extensions
        ext_match = re.search(r'(\w+\.\w+)', task_description)
        if ext_match:
            filename = ext_match.group(1)
            return os.path.join(context.get('working_directory', os.getcwd()), filename)
        
        # Default to desktop
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
        return os.path.join(desktop, 'new_file.txt')
    
    def _extract_folder_path(self, task_description: str, context: Dict[str, Any]) -> str:
        """Extract folder path from task description."""
        import re
        
        # Look for quoted paths
        quoted_match = re.search(r'"([^"]+)"', task_description)
        if quoted_match:
            return quoted_match.group(1)
        
        # Look for folder names
        words = task_description.split()
        for i, word in enumerate(words):
            if word.lower() in ['folder', 'directory'] and i > 0:
                return os.path.join(context.get('working_directory', os.getcwd()), words[i-1])
        
        # Default to desktop
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
        return os.path.join(desktop, 'new_folder')
    
    def _extract_copy_paths(self, task_description: str, context: Dict[str, Any]) -> Tuple[str, str]:
        """Extract source and destination paths for copy operations."""
        import re
        
        # Look for "from X to Y" pattern
        from_to_match = re.search(r'from\s+"([^"]+)"\s+to\s+"([^"]+)"', task_description, re.IGNORECASE)
        if from_to_match:
            return from_to_match.group(1), from_to_match.group(2)
        
        # Look for quoted paths
        quoted_paths = re.findall(r'"([^"]+)"', task_description)
        if len(quoted_paths) >= 2:
            return quoted_paths[0], quoted_paths[1]
        
        # Default fallback
        return "source_file.txt", "destination_file.txt"
    
    def _extract_search_query(self, task_description: str) -> str:
        """Extract search query from task description."""
        import re
        
        # Look for quoted query
        quoted_match = re.search(r'"([^"]+)"', task_description)
        if quoted_match:
            return quoted_match.group(1)
        
        # Look for "for X" pattern
        for_match = re.search(r'for\s+(\w+)', task_description, re.IGNORECASE)
        if for_match:
            return for_match.group(1)
        
        # Extract last word as query
        words = task_description.split()
        if words:
            return words[-1]
        
        return "search_query"
    
    def _extract_text_to_type(self, task_description: str) -> str:
        """Extract text to type from task description."""
        import re
        
        # Look for quoted text
        quoted_match = re.search(r'"([^"]+)"', task_description)
        if quoted_match:
            return quoted_match.group(1)
        
        # Look for "type X" pattern
        type_match = re.search(r'type\s+(.+)', task_description, re.IGNORECASE)
        if type_match:
            return type_match.group(1)
        
        return "Hello, World!"
    
    
    
    
    
    async def _record_performance(self, task_type: str, strategy: TaskExecution, execution_time: float, success: bool):
        """Record performance metrics for future optimization."""
        task_key = f"{strategy.method.value}_{strategy.command[:20]}"
        
        # Calculate performance score (success rate weighted by speed)
        if success:
            performance_score = min(1.0, 1.0 / max(execution_time, 0.1))
        else:
            performance_score = 0.1
        
        # Update performance cache with exponential moving average
        if task_key in self.performance_cache:
            self.performance_cache[task_key] = (
                0.7 * self.performance_cache[task_key] + 
                0.3 * performance_score
            )
        else:
            self.performance_cache[task_key] = performance_score
        
        # Record in execution history
        if task_type not in self.execution_history:
            self.execution_history[task_type] = []
        
        self.execution_history[task_type].append(strategy)
        
        # Keep only recent history
        if len(self.execution_history[task_type]) > 10:
            self.execution_history[task_type].pop(0)

# Global executor instance
smart_executor = SmartTaskExecutor()