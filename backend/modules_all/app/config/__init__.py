"""
Configuration Module for PMS System

STREAMLINED CONFIGURATION APPROACH:
=====================================

1. SINGLE SOURCE OF TRUTH: mongodb_config.py
   - All MongoDB and database configuration
   - Connection strings, client options, database names
   - Collection names, indexes, validation schemas
   - Tax calculation configuration

2. Application Settings: settings.py
   - JWT configuration
   - Application-level settings
   - References mongodb_config.py for database settings

3. Dependency Container: dependency_container.py
   - Uses mongodb_config.py for all database configuration
   - No duplicate configuration
   - Consistent across all modules

USAGE:
======

For database configuration:
```python
from app.config.mongodb_config import (
    get_database_config,
    get_mongodb_connection_string,
    get_mongodb_client_options,
    mongodb_settings
)

# Get complete database config
db_config = get_database_config()

# Get specific components
connection_string = get_mongodb_connection_string()
client_options = get_mongodb_client_options()
database_name = mongodb_settings.database_name
```

For application settings:
```python
from app.config.settings import (
    SECRET_KEY,
    ALGORITHM,
    DATABASE_URL,
    DATABASE_NAME
)
```

For dependency injection:
```python
from app.config.dependency_container import (
    get_dependency_container,
    get_user_service,
    get_organisation_controller,
    # ... all other dependency functions
)
```

ENVIRONMENT VARIABLES:
=====================

MongoDB Configuration:
- MONGODB_URL: MongoDB connection URL
- MONGODB_DATABASE: Database name
- MONGODB_MAX_POOL_SIZE: Maximum connection pool size
- MONGODB_MIN_POOL_SIZE: Minimum connection pool size
- ... (see mongodb_config.py for complete list)

Application Configuration:
- JWT_SECRET: JWT secret key
- JWT_ALGORITHM: JWT algorithm
- JWT_EXPIRATION_MINUTES: JWT expiration time
- DEBUG: Debug mode
- LOG_LEVEL: Logging level
- FILE_STORAGE_TYPE: File storage type
- EMAIL_NOTIFICATIONS_ENABLED: Enable email notifications
"""

# Convenient imports for common configuration needs
from .mongodb_config import (
    get_database_config,
    get_mongodb_connection_string,
    get_mongodb_client_options,
    mongodb_settings,
    validate_mongodb_config
)

from .settings import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    DATABASE_URL,
    DATABASE_NAME,
    DEBUG,
    LOG_LEVEL
)

from .dependency_container import (
    get_dependency_container,
    reset_dependency_container
)

__all__ = [
    # MongoDB configuration
    "get_database_config",
    "get_mongodb_connection_string", 
    "get_mongodb_client_options",
    "mongodb_settings",
    "validate_mongodb_config",
    
    # Application settings
    "SECRET_KEY",
    "ALGORITHM", 
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    "DATABASE_URL",
    "DATABASE_NAME",
    "DEBUG",
    "LOG_LEVEL",
    
    # Dependency container
    "get_dependency_container",
    "reset_dependency_container"
] 