"""
Example: How to use the centralized logger
Demonstrates various logging features and log level changes
"""

from app.utils.logger import get_logger, set_log_level, add_custom_logger

# Get logger for this module
logger = get_logger(__name__)

def demonstrate_basic_logging():
    """Demonstrate basic logging functionality."""
    logger.info("Starting basic logging demonstration")
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

def demonstrate_logging_with_data():
    """Demonstrate logging with structured data."""
    user_id = "12345"
    operation = "user_login"
    
    logger.info(f"User operation: {operation}", extra={
        'user_id': user_id,
        'operation': operation,
        'component': 'auth'
    })
    
    # Log with exception
    try:
        result = 10 / 0
    except ZeroDivisionError as e:
        logger.error(f"Division error in operation {operation}", exc_info=True)

def demonstrate_log_level_changes():
    """Demonstrate dynamic log level changes."""
    logger.info("Current log level demonstration")
    
    # Enable debug logging
    logger.info("Switching to DEBUG level")
    set_log_level('DEBUG')
    
    logger.debug("Debug message - now visible!")
    logger.info("Info message still visible")
    
    # Switch to WARNING level
    logger.info("Switching to WARNING level")
    set_log_level('WARNING')
    
    logger.debug("Debug message - should not be visible")
    logger.info("Info message - should not be visible")
    logger.warning("Warning message - should be visible")
    
    # Switch back to INFO
    logger.warning("Switching back to INFO level")
    set_log_level('INFO')
    logger.info("Back to INFO level logging")

def demonstrate_custom_logger():
    """Demonstrate custom logger creation."""
    # Add a custom logger for database operations
    add_custom_logger('database_operations', 'DEBUG', 'logs/database.log')
    
    db_logger = get_logger('database_operations')
    db_logger.info("Database connection established")
    db_logger.debug("Executing query: SELECT * FROM users")
    
    # Add a custom logger for API operations
    add_custom_logger('api_operations', 'INFO')
    
    api_logger = get_logger('api_operations')
    api_logger.info("API request received")
    api_logger.info("Processing request...")
    api_logger.info("Response sent")

class DatabaseService:
    """Example service class using centralized logger."""
    
    def __init__(self):
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
    
    def connect(self):
        self.logger.info("Connecting to database")
        # Simulate connection
        self.logger.debug("Connection parameters validated")
        self.logger.info("Database connection successful")
    
    def query(self, sql):
        self.logger.debug(f"Executing query: {sql}")
        # Simulate query execution
        self.logger.info("Query executed successfully")
        return []
    
    def close(self):
        self.logger.info("Closing database connection")

class AuthService:
    """Example auth service using centralized logger."""
    
    def __init__(self):
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
    
    def login(self, username):
        self.logger.info(f"Login attempt for user: {username}")
        
        try:
            # Simulate authentication
            if username == "admin":
                self.logger.info(f"Login successful for user: {username}")
                return True
            else:
                self.logger.warning(f"Login failed for user: {username}")
                return False
        except Exception as e:
            self.logger.error(f"Login error for user {username}: {str(e)}", exc_info=True)
            return False

def main():
    """Main demonstration function."""
    logger.info("=" * 50)
    logger.info("Centralized Logger Demonstration")
    logger.info("=" * 50)
    
    # Basic logging
    logger.info("1. Basic Logging:")
    demonstrate_basic_logging()
    
    # Logging with data
    logger.info("\n2. Logging with Data:")
    demonstrate_logging_with_data()
    
    # Log level changes
    logger.info("\n3. Dynamic Log Level Changes:")
    demonstrate_log_level_changes()
    
    # Custom loggers
    logger.info("\n4. Custom Loggers:")
    demonstrate_custom_logger()
    
    # Service classes
    logger.info("\n5. Service Classes:")
    db_service = DatabaseService()
    db_service.connect()
    db_service.query("SELECT * FROM users WHERE active = 1")
    db_service.close()
    
    auth_service = AuthService()
    auth_service.login("admin")
    auth_service.login("invalid_user")
    
    logger.info("\nDemonstration completed!")

if __name__ == "__main__":
    main() 