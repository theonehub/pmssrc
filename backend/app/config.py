"""
Configuration settings for the PMS application
"""

import os
from typing import Optional

# Database Configuration
MONGO_URI: str = os.getenv(
    'MONGO_URI', 
    'mongodb://localhost:27017'
)

# Database Names
GLOBAL_DATABASE: str = os.getenv('GLOBAL_DATABASE', 'pms_global_database')

# Connection Settings
DB_CONNECTION_TIMEOUT: int = int(os.getenv('DB_CONNECTION_TIMEOUT', '5000'))
DB_MAX_POOL_SIZE: int = int(os.getenv('DB_MAX_POOL_SIZE', '10'))
DB_MIN_POOL_SIZE: int = int(os.getenv('DB_MIN_POOL_SIZE', '1'))

# Application Settings
DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')

# Security Settings
SECRET_KEY: str = os.getenv('SECRET_KEY', 'your-secret-key-here')
JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key-here')
JWT_ALGORITHM: str = os.getenv('JWT_ALGORITHM', 'HS256')
JWT_EXPIRATION_HOURS: int = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))

# File Upload Settings
UPLOAD_FOLDER: str = os.getenv('UPLOAD_FOLDER', 'uploads')
MAX_FILE_SIZE: int = int(os.getenv('MAX_FILE_SIZE', '16777216'))  # 16MB

# Email Settings (if needed)
SMTP_SERVER: Optional[str] = os.getenv('SMTP_SERVER')
SMTP_PORT: int = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME: Optional[str] = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD: Optional[str] = os.getenv('SMTP_PASSWORD')

# Redis Settings (if needed for caching)
REDIS_URL: Optional[str] = os.getenv('REDIS_URL')

# Environment
ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'development')

# Database Migration Settings
ENABLE_SOLID_MIGRATION: bool = os.getenv('ENABLE_SOLID_MIGRATION', 'True').lower() == 'true'
MIGRATION_BATCH_SIZE: int = int(os.getenv('MIGRATION_BATCH_SIZE', '100'))

# Logging Configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
        }
    },
    'handlers': {
        'default': {
            'level': LOG_LEVEL,
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': LOG_LEVEL,
            'formatter': 'detailed',
            'class': 'logging.FileHandler',
            'filename': 'app.log',
            'mode': 'a',
        }
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': LOG_LEVEL,
            'propagate': False
        }
    }
}

# Validation
def validate_config():
    """Validate configuration settings."""
    errors = []
    
    if not MONGO_URI:
        errors.append("MONGO_URI is required")
    
    if not SECRET_KEY or SECRET_KEY == 'your-secret-key-here':
        errors.append("SECRET_KEY must be set to a secure value")
    
    if not JWT_SECRET_KEY or JWT_SECRET_KEY == 'your-jwt-secret-key-here':
        errors.append("JWT_SECRET_KEY must be set to a secure value")
    
    if ENVIRONMENT == 'production' and DEBUG:
        errors.append("DEBUG should be False in production")
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")

# Auto-validate in non-test environments
if ENVIRONMENT != 'test':
    try:
        validate_config()
    except ValueError as e:
        print(f"Warning: {e}")
