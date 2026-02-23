import logging
import logging.config
import os
from typing import Dict, Any
from config.settings import settings

def get_logging_config() -> Dict[str, Any]:
    """Get logging configuration based on environment."""
    
    log_level = "DEBUG" if settings.is_development else "INFO"
    
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'detailed': {
                'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'json': {
                '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
            }
        },
        'handlers': {
            'console': {
                'level': log_level,
                'class': 'logging.StreamHandler',
                'formatter': 'standard' if settings.is_development else 'json',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'detailed',
                'filename': 'logs/app.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            },
            'error_file': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'detailed',
                'filename': 'logs/error.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            }
        },
        'loggers': {
            # Root logger
            '': {
                'handlers': ['console', 'file'],
                'level': log_level,
                'propagate': False
            },
            # Application loggers
            'app': {
                'handlers': ['console', 'file'],
                'level': log_level,
                'propagate': False
            },
            'services': {
                'handlers': ['console', 'file'],
                'level': log_level,
                'propagate': False
            },
            'db': {
                'handlers': ['console', 'file'],
                'level': log_level,
                'propagate': False
            },
            # Third-party loggers
            'uvicorn': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': False
            },
            'uvicorn.access': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': False
            },
            'sqlalchemy.engine': {
                'handlers': ['file'],
                'level': 'INFO' if settings.is_development else 'WARNING',
                'propagate': False
            },
            'httpx': {
                'handlers': ['file'],
                'level': 'WARNING',
                'propagate': False
            },
            'aiohttp': {
                'handlers': ['file'],
                'level': 'WARNING',
                'propagate': False
            }
        }
    }
    
    # Add error file handler for production
    if settings.is_production:
        config['loggers']['']['handlers'].append('error_file')
        config['loggers']['app']['handlers'].append('error_file')
        config['loggers']['services']['handlers'].append('error_file')
        config['loggers']['db']['handlers'].append('error_file')
    
    return config

def setup_logging():
    """Setup logging configuration."""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging
    logging_config = get_logging_config()
    logging.config.dictConfig(logging_config)
    
    # Get logger and log startup message
    logger = logging.getLogger('app')
    logger.info(f"Logging configured for {settings.environment} environment")
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)