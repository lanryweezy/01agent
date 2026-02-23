import os
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import platform

logger = logging.getLogger(__name__)

@dataclass
class PerformanceConfig:
    """Performance optimization configuration."""
    screenshot_scale: float = 0.7
    cache_timeout: float = 1.5
    max_concurrent_tasks: int = 8
    execution_timeout: float = 30.0
    memory_cleanup_threshold: float = 85.0
    cpu_optimization_threshold: float = 80.0
    adaptive_delays: bool = True
    fast_mode: bool = True


@dataclass
class UIConfig:
    """UI detection and automation configuration."""
    detection_confidence: float = 0.8
    click_delay: float = 0.01
    type_interval: float = 0.005
    element_cache_size: int = 100
    screenshot_quality: int = 85
    use_fast_detection: bool = True

@dataclass
class ExecutionConfig:
    """Task execution configuration."""
    default_strategy: str = "speed_priority"
    terminal_timeout: float = 15.0
    background_script_timeout: float = 45.0
    gui_operation_timeout: float = 10.0
    retry_attempts: int = 3
    adaptive_strategy: bool = True

@dataclass
class SystemConfig:
    """System-specific configuration."""
    system_type: str = platform.system().lower()
    cpu_cores: int = os.cpu_count()
    optimize_for_system: bool = True
    use_hardware_acceleration: bool = True
    memory_limit_mb: int = 1024
    temp_cleanup_enabled: bool = True

@dataclass
class BrowserConfig:
    """Browser automation configuration."""
    headless: bool = True
    browser_type: str = "chromium" # "chromium", "firefox", "webkit"
    default_timeout: float = 30.0 # Default timeout for browser operations

@dataclass
class AgentConfig:
    """Complete agent configuration."""
    performance: PerformanceConfig
    ui: UIConfig
    execution: ExecutionConfig
    system: SystemConfig
    browser: BrowserConfig
    debug_mode: bool = False
    log_level: str = "INFO"
    config_version: str = "2.0"

class ConfigManager:
    """Manages agent configuration with automatic optimization."""
    
    def __init__(self, config_file: str = "agent_config.json"):
        self.config_file = Path(config_file)
        self.config: Optional[AgentConfig] = None
        self._load_or_create_config()
    
    def _load_or_create_config(self):
        """Load existing config or create optimized default."""
        if self.config_file.exists():
            try:
                self.config = self._load_config()
                logger.info(f"Loaded configuration from {self.config_file}")
            except Exception as e:
                logger.warning(f"Failed to load config: {e}, creating default")
                self.config = self._create_optimized_config()
        else:
            self.config = self._create_optimized_config()
            self.save_config()
            logger.info(f"Created optimized configuration at {self.config_file}")
    
    def _load_config(self) -> AgentConfig:
        """Load configuration from file."""
        with open(self.config_file, 'r') as f:
            data = json.load(f)
        
        return AgentConfig(
            performance=PerformanceConfig(**data.get('performance', {})),
            ui=UIConfig(**data.get('ui', {})),
            execution=ExecutionConfig(**data.get('execution', {})),
            system=SystemConfig(**data.get('system', {})),
            browser=BrowserConfig(**data.get('browser', {})),
            debug_mode=data.get('debug_mode', False),
            log_level=data.get('log_level', 'INFO'),
            config_version=data.get('config_version', '2.0')
        )
    
    def _create_optimized_config(self) -> AgentConfig:
        """Create optimized configuration based on system capabilities."""
        system_type = platform.system().lower()
        cpu_cores = os.cpu_count()
        
        # Get system memory
        try:
            import psutil
            total_memory_gb = psutil.virtual_memory().total / (1024**3)
        except:
            total_memory_gb = 8  # Default assumption
        
        # Optimize performance settings based on system
        performance_config = PerformanceConfig()
        
        if cpu_cores >= 8:
            performance_config.max_concurrent_tasks = 12
            performance_config.screenshot_scale = 0.8  # Higher quality
        elif cpu_cores >= 4:
            performance_config.max_concurrent_tasks = 8
            performance_config.screenshot_scale = 0.7
        else:
            performance_config.max_concurrent_tasks = 4
            performance_config.screenshot_scale = 0.6  # Lower quality for performance
        
        if total_memory_gb >= 16:
            performance_config.cache_timeout = 2.0  # Longer cache
            performance_config.memory_cleanup_threshold = 90.0
        elif total_memory_gb >= 8:
            performance_config.cache_timeout = 1.5
            performance_config.memory_cleanup_threshold = 85.0
        else:
            performance_config.cache_timeout = 1.0
            performance_config.memory_cleanup_threshold = 75.0
        
        # Optimize UI settings
        ui_config = UIConfig()
        if system_type == 'windows':
            ui_config.detection_confidence = 0.8
            ui_config.click_delay = 0.01
        elif system_type == 'darwin':  # macOS
            ui_config.detection_confidence = 0.85
            ui_config.click_delay = 0.02
        else:  # Linux
            ui_config.detection_confidence = 0.75
            ui_config.click_delay = 0.015
        
        # Optimize execution settings
        execution_config = ExecutionConfig()
        if cpu_cores >= 8:
            execution_config.terminal_timeout = 20.0
            execution_config.background_script_timeout = 60.0
        else:
            execution_config.terminal_timeout = 15.0
            execution_config.background_script_timeout = 45.0
        
        # System-specific settings
        system_config = SystemConfig(
            system_type=system_type,
            cpu_cores=cpu_cores,
            memory_limit_mb=min(int(total_memory_gb * 1024 * 0.3), 2048),  # 30% of RAM, max 2GB
            use_hardware_acceleration=total_memory_gb >= 8
        )
        
        # Browser-specific settings
        browser_config = BrowserConfig(
            headless=True if total_memory_gb < 4 else False, # Use headless on low memory systems
            browser_type="chromium" # Default to chromium
        )
        
        return AgentConfig(
            performance=performance_config,
            ui=ui_config,
            execution=execution_config,
            system=system_config,
            browser=browser_config
        )
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            config_dict = {
                'performance': asdict(self.config.performance),
                'ui': asdict(self.config.ui),
                'execution': asdict(self.config.execution),
                'system': asdict(self.config.system),
                'browser': asdict(self.config.browser),
                'debug_mode': self.config.debug_mode,
                'log_level': self.config.log_level,
                'config_version': self.config.config_version
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            logger.info(f"Configuration saved to {self.config_file}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def get_config(self) -> AgentConfig:
        """Get current configuration."""
        return self.config
    
    def update_performance_config(self, **kwargs):
        """Update performance configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config.performance, key):
                setattr(self.config.performance, key, value)
                logger.info(f"Updated performance.{key} = {value}")
        self.save_config()
    
    def update_ui_config(self, **kwargs):
        """Update UI configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config.ui, key):
                setattr(self.config.ui, key, value)
                logger.info(f"Updated ui.{key} = {value}")
        self.save_config()
    
    def update_execution_config(self, **kwargs):
        """Update execution configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config.execution, key):
                setattr(self.config.execution, key, value)
                logger.info(f"Updated execution.{key} = {value}")
        self.save_config()
    
    def optimize_for_speed(self):
        """Optimize configuration for maximum speed."""
        logger.info("Optimizing configuration for maximum speed")
        
        # Performance optimizations
        self.config.performance.screenshot_scale = 0.6  # Lower quality for speed
        self.config.performance.cache_timeout = 1.0     # Shorter cache
        self.config.performance.fast_mode = True
        self.config.performance.adaptive_delays = True
        
        # UI optimizations
        self.config.ui.detection_confidence = 0.75      # Lower confidence for speed
        self.config.ui.click_delay = 0.005              # Faster clicks
        self.config.ui.type_interval = 0.003            # Faster typing
        self.config.ui.screenshot_quality = 75          # Lower quality
        
        # Execution optimizations
        self.config.execution.default_strategy = "speed_priority"
        self.config.execution.terminal_timeout = 10.0   # Shorter timeouts
        self.config.execution.gui_operation_timeout = 8.0
        self.config.execution.retry_attempts = 2        # Fewer retries
        
        self.save_config()
    
    def optimize_for_reliability(self):
        """Optimize configuration for maximum reliability."""
        logger.info("Optimizing configuration for maximum reliability")
        
        # Performance settings for reliability
        self.config.performance.screenshot_scale = 0.8  # Higher quality
        self.config.performance.cache_timeout = 2.0     # Longer cache
        self.config.performance.fast_mode = False
        
        # UI settings for reliability
        self.config.ui.detection_confidence = 0.9       # Higher confidence
        self.config.ui.click_delay = 0.02               # Slower but more reliable
        self.config.ui.type_interval = 0.01             # Slower typing
        self.config.ui.screenshot_quality = 95          # Higher quality
        
        # Execution settings for reliability
        self.config.execution.default_strategy = "reliability_priority"
        self.config.execution.terminal_timeout = 30.0   # Longer timeouts
        self.config.execution.gui_operation_timeout = 20.0
        self.config.execution.retry_attempts = 5        # More retries
        
        self.save_config()
    
    def auto_optimize_for_system(self):
        """Automatically optimize based on current system performance."""
        try:
            import psutil
            
            # Get current system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            
            logger.info(f"Auto-optimizing for system load: CPU {cpu_percent}%, Memory {memory_percent}%")
            
            if cpu_percent > 80 or memory_percent > 85:
                # High load - optimize for efficiency
                self.config.performance.screenshot_scale = 0.5
                self.config.performance.max_concurrent_tasks = max(2, self.config.system.cpu_cores // 2)
                self.config.performance.cache_timeout = 0.5
                self.config.ui.screenshot_quality = 60
                logger.info("Applied high-load optimizations")
                
            elif cpu_percent < 30 and memory_percent < 50:
                # Low load - optimize for quality
                self.config.performance.screenshot_scale = 0.9
                self.config.performance.max_concurrent_tasks = self.config.system.cpu_cores * 2
                self.config.performance.cache_timeout = 3.0
                self.config.ui.screenshot_quality = 95
                logger.info("Applied low-load optimizations")
            
            else:
                # Medium load - balanced settings
                self.config.performance.screenshot_scale = 0.7
                self.config.performance.max_concurrent_tasks = self.config.system.cpu_cores
                self.config.performance.cache_timeout = 1.5
                self.config.ui.screenshot_quality = 85
                logger.info("Applied balanced optimizations")
            
            self.save_config()
            
        except Exception as e:
            logger.error(f"Auto-optimization failed: {e}")
    
    def get_optimized_settings_dict(self) -> Dict[str, Any]:
        """Get all settings as a dictionary for easy access."""
        return {
            'performance': asdict(self.config.performance),
            'ui': asdict(self.config.ui),
            'execution': asdict(self.config.execution),
            'system': asdict(self.config.system),
            'browser': asdict(self.config.browser),
            'debug_mode': self.config.debug_mode,
            'log_level': self.config.log_level
        }
    
    self.save_config()

    def update_browser_config(self, **kwargs):
        """Update browser configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config.browser, key):
                setattr(self.config.browser, key, value)
                logger.info(f"Updated browser.{key} = {value}")
        self.save_config()

    def reset_to_defaults(self):
        """Reset configuration to optimized defaults."""
        logger.info("Resetting configuration to optimized defaults")
        self.config = self._create_optimized_config()
        self.save_config()

# Global configuration manager instance
config_manager = ConfigManager()