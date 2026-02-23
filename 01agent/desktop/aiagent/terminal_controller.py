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
import threading
import queue
import psutil

logger = logging.getLogger(__name__)

class TerminalType(Enum):
    """Different terminal types available."""
    POWERSHELL = "powershell"
    CMD = "cmd"
    BASH = "bash"
    ZSH = "zsh"
    FISH = "fish"
    WSL = "wsl"

@dataclass
class TerminalSession:
    """Represents an active terminal session."""
    session_id: str
    terminal_type: TerminalType
    process: subprocess.Popen
    working_directory: str
    environment: Dict[str, str]
    created_at: float
    last_used: float
    is_active: bool = True

class AdvancedTerminalController:
    """Advanced terminal controller with persistent sessions and smart command execution."""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.sessions: Dict[str, TerminalSession] = {}
        self.command_history: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, float] = {}
        self.session_counter = 0
        
        # Initialize available terminals
        self.available_terminals = self._detect_available_terminals()
        self.preferred_terminal = self._get_preferred_terminal()
        
        # Command templates for different operations
        self.command_templates = self._initialize_command_templates()
        
    def _detect_available_terminals(self) -> List[TerminalType]:
        """Detect available terminal types on the system."""
        available = []
        
        if self.system == "windows":
            # Check for PowerShell
            try:
                subprocess.run(["powershell", "-Command", "Get-Host"], 
                             capture_output=True, timeout=5, creationflags=subprocess.CREATE_NO_WINDOW)
                available.append(TerminalType.POWERSHELL)
            except:
                pass
            
            # CMD is always available on Windows
            available.append(TerminalType.CMD)
            
            # Check for WSL
            try:
                subprocess.run(["wsl", "--list"], 
                             capture_output=True, timeout=5, creationflags=subprocess.CREATE_NO_WINDOW)
                available.append(TerminalType.WSL)
            except:
                pass
                
        else:  # Unix-like systems
            # Check for bash
            if os.path.exists("/bin/bash"):
                available.append(TerminalType.BASH)
            
            # Check for zsh
            if os.path.exists("/bin/zsh"):
                available.append(TerminalType.ZSH)
            
            # Check for fish
            if os.path.exists("/usr/bin/fish") or os.path.exists("/usr/local/bin/fish"):
                available.append(TerminalType.FISH)
        
        return available
    
    def _get_preferred_terminal(self) -> TerminalType:
        """Get the preferred terminal for the current system."""
        if self.system == "windows":
            if TerminalType.POWERSHELL in self.available_terminals:
                return TerminalType.POWERSHELL
            else:
                return TerminalType.CMD
        else:
            if TerminalType.ZSH in self.available_terminals:
                return TerminalType.ZSH
            elif TerminalType.BASH in self.available_terminals:
                return TerminalType.BASH
            else:
                return self.available_terminals[0] if self.available_terminals else TerminalType.BASH
    
    def _initialize_command_templates(self) -> Dict[str, Dict[str, str]]:
        """Initialize command templates for different operations."""
        templates = {
            "file_operations": {
                "create_file": {
                    TerminalType.POWERSHELL.value: "New-Item -Path '{path}' -ItemType File -Force",
                    TerminalType.CMD.value: "type nul > \"{path}\"",
                    TerminalType.BASH.value: "touch '{path}'",
                    TerminalType.ZSH.value: "touch '{path}'",
                },
                "create_directory": {
                    TerminalType.POWERSHELL.value: "New-Item -Path '{path}' -ItemType Directory -Force",
                    TerminalType.CMD.value: "mkdir \"{path}\"",
                    TerminalType.BASH.value: "mkdir -p '{path}'",
                    TerminalType.ZSH.value: "mkdir -p '{path}'",
                },
                "copy_file": {
                    TerminalType.POWERSHELL.value: "Copy-Item '{source}' '{destination}' -Force",
                    TerminalType.CMD.value: "copy \"{source}\" \"{destination}\" /Y",
                    TerminalType.BASH.value: "cp '{source}' '{destination}'",
                    TerminalType.ZSH.value: "cp '{source}' '{destination}'",
                },
                "move_file": {
                    TerminalType.POWERSHELL.value: "Move-Item '{source}' '{destination}' -Force",
                    TerminalType.CMD.value: "move \"{source}\" \"{destination}\"",
                    TerminalType.BASH.value: "mv '{source}' '{destination}'",
                    TerminalType.ZSH.value: "mv '{source}' '{destination}'",
                },
                "delete_file": {
                    TerminalType.POWERSHELL.value: "Remove-Item '{path}' -Force",
                    TerminalType.CMD.value: "del \"{path}\" /F",
                    TerminalType.BASH.value: "rm -f '{path}'",
                    TerminalType.ZSH.value: "rm -f '{path}'",
                },
                "list_files": {
                    TerminalType.POWERSHELL.value: "Get-ChildItem '{path}' | Format-Table Name, Length, LastWriteTime",
                    TerminalType.CMD.value: "dir \"{path}\"",
                    TerminalType.BASH.value: "ls -la '{path}'",
                    TerminalType.ZSH.value: "ls -la '{path}'",
                },
                "find_files": {
                    TerminalType.POWERSHELL.value: "Get-ChildItem -Path '{path}' -Recurse -Filter '*{pattern}*' | Select-Object FullName",
                    TerminalType.CMD.value: "dir \"{path}\\*{pattern}*\" /S /B",
                    TerminalType.BASH.value: "find '{path}' -name '*{pattern}*'",
                    TerminalType.ZSH.value: "find '{path}' -name '*{pattern}*'",
                }
            },
            "system_operations": {
                "get_processes": {
                    TerminalType.POWERSHELL.value: "Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Name, CPU, WorkingSet",
                    TerminalType.CMD.value: "tasklist /FO TABLE",
                    TerminalType.BASH.value: "ps aux --sort=-%cpu | head -10",
                    TerminalType.ZSH.value: "ps aux --sort=-%cpu | head -10",
                },
                "kill_process": {
                    TerminalType.POWERSHELL.value: "Stop-Process -Name '{name}' -Force",
                    TerminalType.CMD.value: "taskkill /F /IM \"{name}\"",
                    TerminalType.BASH.value: "pkill '{name}'",
                    TerminalType.ZSH.value: "pkill '{name}'",
                },
                "system_info": {
                    TerminalType.POWERSHELL.value: "Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, TotalPhysicalMemory",
                    TerminalType.CMD.value: "systeminfo | findstr /C:\"OS Name\" /C:\"OS Version\" /C:\"Total Physical Memory\"",
                    TerminalType.BASH.value: "uname -a && free -h && df -h",
                    TerminalType.ZSH.value: "uname -a && free -h && df -h",
                },
                "network_info": {
                    TerminalType.POWERSHELL.value: "Get-NetAdapter | Where-Object Status -eq 'Up' | Select-Object Name, InterfaceDescription, LinkSpeed",
                    TerminalType.CMD.value: "ipconfig /all",
                    TerminalType.BASH.value: "ip addr show && netstat -i",
                    TerminalType.ZSH.value: "ip addr show && netstat -i",
                },
                "disk_usage": {
                    TerminalType.POWERSHELL.value: "Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, @{Name='Size(GB)';Expression={[math]::Round($_.Size/1GB,2)}}, @{Name='FreeSpace(GB)';Expression={[math]::Round($_.FreeSpace/1GB,2)}}",
                    TerminalType.CMD.value: "wmic logicaldisk get size,freespace,caption",
                    TerminalType.BASH.value: "df -h",
                    TerminalType.ZSH.value: "df -h",
                }
            },
            "application_operations": {
                "start_application": {
                    TerminalType.POWERSHELL.value: "Start-Process '{app}' -WindowStyle Normal",
                    TerminalType.CMD.value: "start \"\" \"{app}\"",
                    TerminalType.BASH.value: "nohup '{app}' > /dev/null 2>&1 &",
                    TerminalType.ZSH.value: "nohup '{app}' > /dev/null 2>&1 &",
                },
                "stop_application": {
                    TerminalType.POWERSHELL.value: "Get-Process '{app}' | Stop-Process -Force",
                    TerminalType.CMD.value: "taskkill /F /IM \"{app}\"",
                    TerminalType.BASH.value: "pkill -f '{app}'",
                    TerminalType.ZSH.value: "pkill -f '{app}'",
                }
            },
            "text_operations": {
                "write_to_file": {
                    TerminalType.POWERSHELL.value: "Set-Content -Path '{path}' -Value '{content}'",
                    TerminalType.CMD.value: "echo {content} > \"{path}\"",
                    TerminalType.BASH.value: "echo '{content}' > '{path}'",
                    TerminalType.ZSH.value: "echo '{content}' > '{path}'",
                },
                "append_to_file": {
                    TerminalType.POWERSHELL.value: "Add-Content -Path '{path}' -Value '{content}'",
                    TerminalType.CMD.value: "echo {content} >> \"{path}\"",
                    TerminalType.BASH.value: "echo '{content}' >> '{path}'",
                    TerminalType.ZSH.value: "echo '{content}' >> '{path}'",
                },
                "read_file": {
                    TerminalType.POWERSHELL.value: "Get-Content '{path}'",
                    TerminalType.CMD.value: "type \"{path}\"",
                    TerminalType.BASH.value: "cat '{path}'",
                    TerminalType.ZSH.value: "cat '{path}'",
                },
                "search_in_file": {
                    TerminalType.POWERSHELL.value: "Select-String -Path '{path}' -Pattern '{pattern}'",
                    TerminalType.CMD.value: "findstr \"{pattern}\" \"{path}\"",
                    TerminalType.BASH.value: "grep '{pattern}' '{path}'",
                    TerminalType.ZSH.value: "grep '{pattern}' '{path}'",
                }
            }
        }
        return templates
    
    async def create_session(self, terminal_type: Optional[TerminalType] = None, working_directory: Optional[str] = None) -> str:
        """Create a new persistent terminal session."""
        if terminal_type is None:
            terminal_type = self.preferred_terminal
        
        if working_directory is None:
            working_directory = os.getcwd()
        
        session_id = f"session_{self.session_counter}"
        self.session_counter += 1
        
        try:
            # Create terminal process
            if terminal_type == TerminalType.POWERSHELL:
                cmd = ["powershell", "-NoExit", "-Command", f"Set-Location '{working_directory}'"]
                creation_flags = subprocess.CREATE_NO_WINDOW if self.system == "windows" else 0
            elif terminal_type == TerminalType.CMD:
                cmd = ["cmd", "/K", f"cd /D \"{working_directory}\""]
                creation_flags = subprocess.CREATE_NO_WINDOW if self.system == "windows" else 0
            elif terminal_type == TerminalType.WSL:
                cmd = ["wsl", "-d", "Ubuntu", "--cd", working_directory]
                creation_flags = subprocess.CREATE_NO_WINDOW if self.system == "windows" else 0
            else:  # Unix shells
                cmd = [terminal_type.value, "-c", f"cd '{working_directory}' && exec {terminal_type.value}"]
                creation_flags = 0
            
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0,
                creationflags=creation_flags
            )
            
            # Create session object
            session = TerminalSession(
                session_id=session_id,
                terminal_type=terminal_type,
                process=process,
                working_directory=working_directory,
                environment=os.environ.copy(),
                created_at=time.time(),
                last_used=time.time()
            )
            
            self.sessions[session_id] = session
            logger.info(f"Created terminal session {session_id} with {terminal_type.value}")
            
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create terminal session: {e}")
            raise
    
    async def execute_command(self, command: str, session_id: Optional[str] = None, timeout: float = 30.0) -> Dict[str, Any]:
        """Execute a command in a terminal session."""
        start_time = time.time()
        
        try:
            # Use existing session or create new one
            if session_id and session_id in self.sessions:
                session = self.sessions[session_id]
            else:
                session_id = await self.create_session()
                session = self.sessions[session_id]
            
            # Update last used time
            session.last_used = time.time()
            
            # Execute command
            result = await self._execute_in_session(session, command, timeout)
            
            # Record performance
            execution_time = time.time() - start_time
            self._record_command_performance(command, execution_time, result.get('success', False))
            
            return {
                **result,
                'session_id': session_id,
                'execution_time': execution_time
            }
            
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'session_id': session_id,
                'execution_time': time.time() - start_time
            }
    
    async def _execute_in_session(self, session: TerminalSession, command: str, timeout: float) -> Dict[str, Any]:
        """Execute a command in a specific session."""
        try:
            # Send command to process
            session.process.stdin.write(command + "\n")
            session.process.stdin.flush()
            
            # Read output with timeout
            output_lines = []
            error_lines = []
            
            # Use asyncio to handle timeout
            try:
                stdout_task = asyncio.create_task(self._read_output(session.process.stdout))
                stderr_task = asyncio.create_task(self._read_output(session.process.stderr))
                
                stdout_result, stderr_result = await asyncio.wait_for(
                    asyncio.gather(stdout_task, stderr_task),
                    timeout=timeout
                )
                
                output_lines = stdout_result
                error_lines = stderr_result
                
            except asyncio.TimeoutError:
                logger.warning(f"Command timed out after {timeout} seconds")
                return {
                    'success': False,
                    'output': '\n'.join(output_lines),
                    'error': f'Command timed out after {timeout} seconds',
                    'timeout': True
                }
            
            # Determine success based on output
            success = len(error_lines) == 0 or not any('error' in line.lower() for line in error_lines)
            
            return {
                'success': success,
                'output': '\n'.join(output_lines),
                'error': '\n'.join(error_lines),
                'command': command,
                'terminal_type': session.terminal_type.value
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'command': command,
                'terminal_type': session.terminal_type.value
            }
    
    async def _read_output(self, stream) -> List[str]:
        """Read output from a stream."""
        lines = []
        try:
            while True:
                line = await asyncio.get_event_loop().run_in_executor(None, stream.readline)
                if not line:
                    break
                lines.append(line.strip())
                if len(lines) > 1000:  # Prevent memory issues
                    break
        except Exception as e:
            logger.error(f"Error reading stream: {e}")
        
        return lines
    
    async def execute_template_command(self, operation_category: str, operation_name: str, parameters: Dict[str, Any], session_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute a command using predefined templates."""
        try:
            # Get command template
            if operation_category not in self.command_templates:
                return {
                    'success': False,
                    'error': f'Unknown operation category: {operation_category}'
                }
            
            if operation_name not in self.command_templates[operation_category]:
                return {
                    'success': False,
                    'error': f'Unknown operation: {operation_name}'
                }
            
            # Get session or create new one
            if session_id and session_id in self.sessions:
                session = self.sessions[session_id]
            else:
                session_id = await self.create_session()
                session = self.sessions[session_id]
            
            # Get command template for current terminal type
            templates = self.command_templates[operation_category][operation_name]
            terminal_key = session.terminal_type.value
            
            if terminal_key not in templates:
                # Fallback to preferred terminal
                terminal_key = self.preferred_terminal.value
                if terminal_key not in templates:
                    return {
                        'success': False,
                        'error': f'No template available for {session.terminal_type.value}'
                    }
            
            # Format command with parameters
            command_template = templates[terminal_key]
            try:
                command = command_template.format(**parameters)
            except KeyError as e:
                return {
                    'success': False,
                    'error': f'Missing parameter: {e}'
                }
            
            # Execute command
            result = await self.execute_command(command, session_id)
            
            return {
                **result,
                'operation': f'{operation_category}.{operation_name}',
                'template_used': command_template
            }
            
        except Exception as e:
            logger.error(f"Template command execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'operation': f'{operation_category}.{operation_name}'
            }
    
    async def execute_smart_command(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a command using smart analysis of the task description."""
        context = context or {}
        
        try:
            # Analyze task to determine best command approach
            operation_info = await self._analyze_task_for_terminal(task_description, context)
            
            if operation_info:
                category, operation, parameters = operation_info
                return await self.execute_template_command(category, operation, parameters)
            else:
                # Fallback to direct command execution
                return await self.execute_command(task_description)
                
        except Exception as e:
            logger.error(f"Smart command execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'task': task_description
            }
    
    async def _analyze_task_for_terminal(self, task_description: str, context: Dict[str, Any]) -> Optional[Tuple[str, str, Dict[str, Any]]]:
        """Analyze task description to determine terminal operation."""
        task_lower = task_description.lower()
        
        # File operations
        if any(word in task_lower for word in ['create', 'make', 'new']) and 'file' in task_lower:
            path = self._extract_path_from_description(task_description, context, 'file')
            return ('file_operations', 'create_file', {'path': path})
        
        elif any(word in task_lower for word in ['create', 'make', 'new']) and any(word in task_lower for word in ['folder', 'directory']):
            path = self._extract_path_from_description(task_description, context, 'folder')
            return ('file_operations', 'create_directory', {'path': path})
        
        elif 'copy' in task_lower:
            source, destination = self._extract_copy_paths_from_description(task_description, context)
            return ('file_operations', 'copy_file', {'source': source, 'destination': destination})
        
        elif 'move' in task_lower:
            source, destination = self._extract_copy_paths_from_description(task_description, context)
            return ('file_operations', 'move_file', {'source': source, 'destination': destination})
        
        elif 'delete' in task_lower or 'remove' in task_lower:
            path = self._extract_path_from_description(task_description, context, 'file')
            return ('file_operations', 'delete_file', {'path': path})
        
        elif 'list' in task_lower and 'file' in task_lower:
            path = self._extract_path_from_description(task_description, context, 'folder', default='.')
            return ('file_operations', 'list_files', {'path': path})
        
        elif any(word in task_lower for word in ['find', 'search']) and 'file' in task_lower:
            path = self._extract_path_from_description(task_description, context, 'folder', default='.')
            pattern = self._extract_search_pattern(task_description)
            return ('file_operations', 'find_files', {'path': path, 'pattern': pattern})
        
        # System operations
        elif 'process' in task_lower and any(word in task_lower for word in ['list', 'show', 'get']):
            return ('system_operations', 'get_processes', {})
        
        elif 'kill' in task_lower or 'stop' in task_lower:
            if 'process' in task_lower:
                name = self._extract_process_name(task_description)
                return ('system_operations', 'kill_process', {'name': name})
            else:
                app = self._extract_app_name(task_description)
                return ('application_operations', 'stop_application', {'app': app})
        
        elif 'system' in task_lower and 'info' in task_lower:
            return ('system_operations', 'system_info', {})
        
        elif 'network' in task_lower and 'info' in task_lower:
            return ('system_operations', 'network_info', {})
        
        elif 'disk' in task_lower and any(word in task_lower for word in ['usage', 'space']):
            return ('system_operations', 'disk_usage', {})
        
        # Application operations
        elif any(word in task_lower for word in ['start', 'open', 'launch', 'run']):
            app = self._extract_app_name(task_description)
            return ('application_operations', 'start_application', {'app': app})
        
        # Text operations
        elif 'write' in task_lower and 'file' in task_lower:
            path = self._extract_path_from_description(task_description, context, 'file')
            content = self._extract_content_from_description(task_description)
            return ('text_operations', 'write_to_file', {'path': path, 'content': content})
        
        elif 'read' in task_lower and 'file' in task_lower:
            path = self._extract_path_from_description(task_description, context, 'file')
            return ('text_operations', 'read_file', {'path': path})
        
        return None
    
    def _extract_path_from_description(self, description: str, context: Dict[str, Any], path_type: str, default: str = None) -> str:
        """Extract file/folder path from description."""
        import re
        
        # Look for quoted paths
        quoted_match = re.search(r'"([^"]+)"', description)
        if quoted_match:
            return quoted_match.group(1)
        
        # Look for file extensions for files
        if path_type == 'file':
            ext_match = re.search(r'(\w+\.\w+)', description)
            if ext_match:
                filename = ext_match.group(1)
                return os.path.join(context.get('working_directory', os.getcwd()), filename)
        
        # Use default or generate one
        if default:
            return default
        
        if path_type == 'file':
            return os.path.join(context.get('working_directory', os.getcwd()), 'new_file.txt')
        else:
            return os.path.join(context.get('working_directory', os.getcwd()), 'new_folder')
    
    def _extract_copy_paths_from_description(self, description: str, context: Dict[str, Any]) -> Tuple[str, str]:
        """Extract source and destination paths."""
        import re
        
        # Look for "from X to Y" pattern
        from_to_match = re.search(r'from\s+"([^"]+)"\s+to\s+"([^"]+)"', description, re.IGNORECASE)
        if from_to_match:
            return from_to_match.group(1), from_to_match.group(2)
        
        # Look for quoted paths
        quoted_paths = re.findall(r'"([^"]+)"', description)
        if len(quoted_paths) >= 2:
            return quoted_paths[0], quoted_paths[1]
        
        # Default fallback
        return "source_file.txt", "destination_file.txt"
    
    def _extract_search_pattern(self, description: str) -> str:
        """Extract search pattern from description."""
        import re
        
        # Look for quoted pattern
        quoted_match = re.search(r'"([^"]+)"', description)
        if quoted_match:
            return quoted_match.group(1)
        
        # Look for "for X" pattern
        for_match = re.search(r'for\s+(\w+)', description, re.IGNORECASE)
        if for_match:
            return for_match.group(1)
        
        return "*"
    
    def _extract_process_name(self, description: str) -> str:
        """Extract process name from description."""
        import re
        
        # Look for quoted name
        quoted_match = re.search(r'"([^"]+)"', description)
        if quoted_match:
            return quoted_match.group(1)
        
        # Look for common process names
        words = description.split()
        for word in words:
            if word.lower() in ['notepad', 'chrome', 'firefox', 'calculator', 'explorer']:
                return word.lower()
        
        return "notepad"
    
    def _extract_app_name(self, description: str) -> str:
        """Extract application name from description."""
        import re
        
        # Look for quoted name
        quoted_match = re.search(r'"([^"]+)"', description)
        if quoted_match:
            return quoted_match.group(1)
        
        # Common application mappings
        app_mappings = {
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'browser': 'chrome.exe',
            'chrome': 'chrome.exe',
            'firefox': 'firefox.exe',
            'explorer': 'explorer.exe'
        }
        
        description_lower = description.lower()
        for app_key, app_exe in app_mappings.items():
            if app_key in description_lower:
                return app_exe
        
        return 'notepad.exe'
    
    def _extract_content_from_description(self, description: str) -> str:
        """Extract content to write from description."""
        import re
        
        # Look for quoted content
        quoted_match = re.search(r'"([^"]+)"', description)
        if quoted_match:
            return quoted_match.group(1)
        
        # Look for "write X" pattern
        write_match = re.search(r'write\s+(.+)', description, re.IGNORECASE)
        if write_match:
            return write_match.group(1)
        
        return "Hello, World!"
    
    def _record_command_performance(self, command: str, execution_time: float, success: bool):
        """Record command performance for optimization."""
        command_key = command[:50]  # Truncate for key
        
        if success:
            performance_score = min(1.0, 1.0 / max(execution_time, 0.1))
        else:
            performance_score = 0.1
        
        # Update performance metrics with exponential moving average
        if command_key in self.performance_metrics:
            self.performance_metrics[command_key] = (
                0.7 * self.performance_metrics[command_key] + 
                0.3 * performance_score
            )
        else:
            self.performance_metrics[command_key] = performance_score
        
        # Add to command history
        self.command_history.append({
            'command': command,
            'execution_time': execution_time,
            'success': success,
            'timestamp': time.time()
        })
        
        # Keep only recent history
        if len(self.command_history) > 100:
            self.command_history.pop(0)
    
    async def close_session(self, session_id: str):
        """Close a terminal session."""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            try:
                session.process.terminate()
                await asyncio.sleep(1)
                if session.process.poll() is None:
                    session.process.kill()
            except:
                pass
            
            del self.sessions[session_id]
            logger.info(f"Closed terminal session {session_id}")
    
    async def cleanup_inactive_sessions(self, max_idle_time: float = 300.0):
        """Clean up inactive sessions."""
        current_time = time.time()
        inactive_sessions = []
        
        for session_id, session in self.sessions.items():
            if current_time - session.last_used > max_idle_time:
                inactive_sessions.append(session_id)
        
        for session_id in inactive_sessions:
            await self.close_session(session_id)
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a session."""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        return {
            'session_id': session_id,
            'terminal_type': session.terminal_type.value,
            'working_directory': session.working_directory,
            'created_at': session.created_at,
            'last_used': session.last_used,
            'is_active': session.is_active,
            'process_id': session.process.pid if session.process else None
        }
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions."""
        return [self.get_session_info(session_id) for session_id in self.sessions.keys()]

# Global terminal controller instance
terminal_controller = AdvancedTerminalController()