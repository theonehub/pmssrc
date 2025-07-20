"""
Centralized Logger Configuration
Provides a single logger instance that can be used across the entire project
"""

import logging
import logging.config
import logging.handlers
import os
from typing import Optional

# Get configuration from environment or default values
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
LOG_FORMAT = os.getenv('LOG_FORMAT', 'detailed')
LOG_TO_FILE = os.getenv('LOG_TO_FILE', 'true').lower() == 'true'
LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', 'logs/app.log')
LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', '10485760'))  # 10MB
LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '5'))

class LoggerConfig:
    """Centralized logger configuration class."""
    
    _instance = None
    _configured = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggerConfig, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._configured:
            self.configure_logging()
            self._configured = True
    
    def configure_logging(self):
        """Configure logging for the entire application."""
        
        # Ensure logs directory exists if logging to file
        if LOG_TO_FILE:
            log_dir = os.path.dirname(LOG_FILE_PATH)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
        
        # Define formatters
        formatters = {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'detailed': {
                'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(funcName)s(): %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'simple': {
                'format': '%(levelname)s - %(name)s - %(message)s'
            },
            'json': {
                'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "line": %(lineno)d, "function": "%(funcName)s", "message": "%(message)s"}',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'message_only': {
                'format': '%(message)s'
            }
        }
        
        # Define handlers
        handlers = {
            'console': {
                'class': 'logging.StreamHandler',
                'level': LOG_LEVEL,
                'formatter': LOG_FORMAT,
                'stream': 'ext://sys.stdout'
            }
        }
        
        # Add file handler if logging to file is enabled
        if LOG_TO_FILE:
            handlers['file'] = {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': LOG_LEVEL,
                'formatter': 'detailed',
                'filename': LOG_FILE_PATH,
                'maxBytes': LOG_MAX_BYTES,
                'backupCount': LOG_BACKUP_COUNT,
                'mode': 'a',
                'encoding': 'utf-8'
            }
        
        # Determine which handlers to use
        handler_list = ['console']
        if LOG_TO_FILE:
            handler_list.append('file')
        
        # Logging configuration
        config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': formatters,
            'handlers': handlers,
            'root': {
                'level': LOG_LEVEL,
                'handlers': handler_list
            },
            'loggers': {
                # Application specific loggers
                'app': {
                    'level': LOG_LEVEL,
                    'handlers': handler_list,
                    'propagate': False
                },
                # Detailed logger with all information
                'detailed': {
                    'level': LOG_LEVEL,
                    'handlers': handler_list,
                    'propagate': False
                },
                # Simple logger with just the message
                'simple': {
                    'level': LOG_LEVEL,
                    'handlers': handler_list,
                    'propagate': False
                },
                'uvicorn': {
                    'level': 'INFO',
                    'handlers': handler_list,
                    'propagate': False
                },
                'uvicorn.access': {
                    'level': 'INFO',
                    'handlers': handler_list,
                    'propagate': False
                },
                'uvicorn.error': {
                    'level': 'INFO',
                    'handlers': handler_list,
                    'propagate': False
                },
                'fastapi': {
                    'level': 'INFO',
                    'handlers': handler_list,
                    'propagate': False
                },
                # Third-party loggers with controlled levels
                'pymongo': {
                    'level': 'WARNING',
                    'handlers': handler_list,
                    'propagate': False
                },
                'motor': {
                    'level': 'WARNING',
                    'handlers': handler_list,
                    'propagate': False
                },
                'bson': {
                    'level': 'WARNING',
                    'handlers': handler_list,
                    'propagate': False
                }
            }
        }
        
        # Apply the configuration
        logging.config.dictConfig(config)
        
        # Configure the detailed and simple loggers with specific formatters
        detailed_logger = logging.getLogger('detailed')
        simple_logger = logging.getLogger('simple')
        
        # Clear existing handlers and add new ones with specific formatters
        detailed_logger.handlers.clear()
        simple_logger.handlers.clear()
        
        # Add console handlers with specific formatters
        detailed_console_handler = logging.StreamHandler()
        detailed_console_handler.setLevel(LOG_LEVEL)
        detailed_console_handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(funcName)s(): %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        detailed_logger.addHandler(detailed_console_handler)
        
        simple_console_handler = logging.StreamHandler()
        simple_console_handler.setLevel(LOG_LEVEL)
        simple_console_handler.setFormatter(logging.Formatter('%(message)s'))
        simple_logger.addHandler(simple_console_handler)
        
        # Add file handlers if logging to file is enabled
        if LOG_TO_FILE:
            detailed_file_handler = logging.handlers.RotatingFileHandler(
                LOG_FILE_PATH, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT
            )
            detailed_file_handler.setLevel(LOG_LEVEL)
            detailed_file_handler.setFormatter(logging.Formatter(
                '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(funcName)s(): %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ))
            detailed_logger.addHandler(detailed_file_handler)
            
            simple_file_handler = logging.handlers.RotatingFileHandler(
                LOG_FILE_PATH, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT
            )
            simple_file_handler.setLevel(LOG_LEVEL)
            simple_file_handler.setFormatter(logging.Formatter('%(message)s'))
            simple_logger.addHandler(simple_file_handler)
        
        # Log the configuration
        logger = logging.getLogger('app.logger_config')
        logger.info(f"Logging configured - Level: {LOG_LEVEL}, Format: {LOG_FORMAT}, File: {LOG_TO_FILE}")
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger instance with the given name.
        
        Args:
            name: Logger name, typically __name__ of the calling module
            
        Returns:
            logging.Logger: Configured logger instance
        """
        return logging.getLogger(name)
    
    def get_detailed_logger(self) -> logging.Logger:
        """
        Get a detailed logger with timestamp, level, name, line number, function name, and message.
        
        Returns:
            logging.Logger: Detailed logger instance
            
        Example:
            logger = get_detailed_logger()
            logger.info("pushed data")  # Output: 2025-07-20 14:24:11 [INFO] detailed:153 - configure_logging(): pushed data
        """
        return logging.getLogger('detailed')
    
    def get_simple_logger(self) -> logging.Logger:
        """
        Get a simple logger with just the message content.
        
        Returns:
            logging.Logger: Simple logger instance
            
        Example:
            logger = get_simple_logger()
            logger.info("pushed data")  # Output: pushed data
        """
        return logging.getLogger('simple')
    
    def set_log_level(self, level: str):
        """
        Dynamically change the log level for all loggers.
        
        Args:
            level: New log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        level = level.upper()
        
        # Validate log level
        if level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            raise ValueError(f"Invalid log level: {level}")
        
        # Update root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        
        # Update all handlers
        for handler in root_logger.handlers:
            handler.setLevel(level)
        
        # Update specific application loggers
        app_logger = logging.getLogger('app')
        app_logger.setLevel(level)
        for handler in app_logger.handlers:
            handler.setLevel(level)
        
        # Update detailed and simple loggers
        detailed_logger = logging.getLogger('detailed')
        simple_logger = logging.getLogger('simple')
        
        detailed_logger.setLevel(level)
        simple_logger.setLevel(level)
        
        for handler in detailed_logger.handlers:
            handler.setLevel(level)
        for handler in simple_logger.handlers:
            handler.setLevel(level)
        
        logger = logging.getLogger('app.logger_config')
        logger.info(f"Log level changed to: {level}")
    
    def add_custom_logger(self, name: str, level: Optional[str] = None, 
                         file_path: Optional[str] = None):
        """
        Add a custom logger configuration.
        
        Args:
            name: Logger name
            level: Log level for this logger
            file_path: Optional separate file for this logger
        """
        level = level or LOG_LEVEL
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        if file_path:
            # Create file handler for this specific logger
            file_handler = logging.handlers.RotatingFileHandler(
                file_path, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT
            )
            file_handler.setLevel(level)
            
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(funcName)s(): %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        main_logger = logging.getLogger('app.logger_config')
        main_logger.info(f"Custom logger '{name}' configured with level: {level}")


# Global logger configuration instance
_logger_config = LoggerConfig()

def get_logger(name: str = None) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name, defaults to calling module name
        
    Returns:
        logging.Logger: Configured logger instance
        
    Example:
        from utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("This is a log message")
    """
    if name is None:
        # Try to get the calling module name
        import inspect
        frame = inspect.currentframe()
        try:
            caller_frame = frame.f_back
            name = caller_frame.f_globals.get('__name__', 'app')
        finally:
            del frame
    
    return _logger_config.get_logger(name)

def get_detailed_logger() -> logging.Logger:
    """
    Get a detailed logger with timestamp, level, name, line number, function name, and message.
    
    Returns:
        logging.Logger: Detailed logger instance
        
    Example:
        from utils.logger import get_detailed_logger
        logger = get_detailed_logger()
        logger.info("pushed data")  # Output: 2025-07-20 14:24:11 [INFO] detailed:153 - configure_logging(): pushed data
    """
    return _logger_config.get_detailed_logger()

def get_simple_logger() -> logging.Logger:
    """
    Get a simple logger with just the message content.
    
    Returns:
        logging.Logger: Simple logger instance
        
    Example:
        from utils.logger import get_simple_logger
        logger = get_simple_logger()
        logger.info("pushed data")  # Output: pushed data
    """
    return _logger_config.get_simple_logger()

def set_log_level(level: str):
    """
    Change the log level for all loggers.
    
    Args:
        level: New log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Example:
        from utils.logger import set_log_level
        set_log_level('DEBUG')  # Enable debug logging
    """
    _logger_config.set_log_level(level)

def add_custom_logger(name: str, level: str = None, file_path: str = None):
    """
    Add a custom logger configuration.
    
    Args:
        name: Logger name
        level: Log level for this logger
        file_path: Optional separate file for this logger
        
    Example:
        from utils.logger import add_custom_logger
        add_custom_logger('database', 'DEBUG', 'logs/database.log')
    """
    _logger_config.add_custom_logger(name, level, file_path)

# Convenience function for backward compatibility
def setup_logging():
    """Setup logging configuration (called automatically on import)."""
    #set_log_level('DEBUG') # TODO: Remove this after testing
    pass  # Configuration is done automatically when the module is imported

# Auto-setup logging when module is imported
setup_logging() 