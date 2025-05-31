# Centralized Logging System

This document describes the centralized logging system implemented for the Payroll Management System.

## Overview

The centralized logging system provides a unified way to configure and manage logging across the entire application. It ensures consistent log formatting, levels, and output destinations.

## Key Features

- **Single Configuration Point**: All logging configuration is managed in one place
- **Dynamic Log Level Changes**: Change log levels at runtime without restart
- **Multiple Output Destinations**: Console and file logging with rotation
- **Custom Loggers**: Create specialized loggers for different components
- **Environment-based Configuration**: Configure via environment variables
- **Automatic Logger Management**: Handles third-party library logging levels

## Basic Usage

### Import and Use

```python
from utils.logger import get_logger

# Get logger for current module
logger = get_logger(__name__)

# Use the logger
logger.info("Application started")
logger.debug("Debug information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical issue")
```

### In Classes

```python
from utils.logger import get_logger

class UserService:
    def __init__(self):
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
    
    def create_user(self, username):
        self.logger.info(f"Creating user: {username}")
        # ... implementation
        self.logger.debug("User creation completed")
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `LOG_FORMAT` | `detailed` | Log format (standard, detailed, simple, json) |
| `LOG_TO_FILE` | `true` | Enable file logging |
| `LOG_FILE_PATH` | `logs/app.log` | Path to log file |
| `LOG_MAX_BYTES` | `10485760` | Max log file size (10MB) |
| `LOG_BACKUP_COUNT` | `5` | Number of backup log files |

### Example .env Configuration

```bash
# Logging Configuration
LOG_LEVEL=DEBUG
LOG_FORMAT=detailed
LOG_TO_FILE=true
LOG_FILE_PATH=logs/pms_app.log
LOG_MAX_BYTES=20971520
LOG_BACKUP_COUNT=10
```

## Advanced Features

### Dynamic Log Level Changes

```python
from utils.logger import set_log_level

# Change log level for all loggers
set_log_level('DEBUG')  # Enable debug logging
set_log_level('WARNING')  # Only warnings and above
```

### Custom Loggers

```python
from utils.logger import add_custom_logger, get_logger

# Create custom logger with separate file
add_custom_logger('database', 'DEBUG', 'logs/database.log')
db_logger = get_logger('database')

# Create custom logger with different level
add_custom_logger('api_requests', 'INFO')
api_logger = get_logger('api_requests')
```

### Structured Logging

```python
logger.info("User operation completed", extra={
    'user_id': '12345',
    'operation': 'login',
    'duration_ms': 150,
    'success': True
})
```

### Exception Logging

```python
try:
    # Some operation
    result = risky_operation()
except Exception as e:
    logger.error("Operation failed", exc_info=True)
```

## Log Formats

### Standard Format
```
2024-01-15 10:30:25 [INFO] app.services.user_service: User created successfully
```

### Detailed Format
```
2024-01-15 10:30:25 [INFO] app.services.user_service:45 - create_user(): User created successfully
```

### JSON Format
```json
{"timestamp": "2024-01-15 10:30:25", "level": "INFO", "logger": "app.services.user_service", "line": 45, "function": "create_user", "message": "User created successfully"}
```

## Migration from Old Logging

### Before (Old Pattern)
```python
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s:%(lineno)d]: %(message)s",
)
```

### After (New Centralized Pattern)
```python
from utils.logger import get_logger

logger = get_logger(__name__)
```

## File Structure

```
backend/app/
├── utils/
│   └── logger.py              # Centralized logger configuration
├── logs/                      # Log files directory
│   ├── app.log               # Main application log
│   ├── database.log          # Database operations log (if configured)
│   └── app.log.1             # Rotated log files
├── examples/
│   └── logger_usage_example.py  # Usage examples
└── docs/
    └── LOGGING.md            # This documentation
```

## Best Practices

1. **Use Module-Level Loggers**: Always pass `__name__` to get_logger()
2. **Appropriate Log Levels**: 
   - DEBUG: Detailed diagnostic information
   - INFO: General application flow
   - WARNING: Something unexpected but not an error
   - ERROR: Error occurred but application continues
   - CRITICAL: Serious error, application may not continue

3. **Structured Data**: Use the `extra` parameter for structured logging
4. **Exception Information**: Use `exc_info=True` when logging exceptions
5. **Performance**: Avoid expensive operations in log messages for production

## Troubleshooting

### Logs Not Appearing
- Check LOG_LEVEL environment variable
- Verify log file permissions
- Check if logs directory exists

### Log File Rotation Issues
- Verify LOG_MAX_BYTES and LOG_BACKUP_COUNT settings
- Check file system permissions
- Ensure sufficient disk space

### Performance Issues
- Lower log level in production (INFO or WARNING)
- Reduce file logging if needed
- Monitor log file sizes

## Example Implementation

See `examples/logger_usage_example.py` for comprehensive usage examples including:
- Basic logging operations
- Dynamic log level changes
- Custom logger creation
- Service class implementations
- Exception handling

## Integration Points

The centralized logger integrates with:
- FastAPI application startup
- Database connections (MongoDB)
- Authentication services
- API controllers
- Background tasks
- Third-party libraries (controlled logging levels) 