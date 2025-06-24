"""
MongoDB Configuration
Configuration settings for MongoDB connections
"""

import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def get_mongodb_connection_string() -> str:
    """
    Get MongoDB connection string from environment or use default.
    
    Returns:
        MongoDB connection string
    """
    # First try to get from environment variables
    connection_string = os.getenv("MONGODB_URL")
    
    if not connection_string:
        # Use the provided connection string as default
        connection_string = "mongodb+srv://admin:test123@mongodbtest.jhfj7s3.mongodb.net/?appName=mongodbTest"
    
    logger.info(f"Using MongoDB connection: {connection_string.replace('test123', '***')}")  # Hide password in logs
    return connection_string


def get_mongodb_client_options() -> Dict[str, Any]:
    """
    Get MongoDB client options.
    
    Returns:
        Dictionary of MongoDB client options
    """
    return {
        "maxPoolSize": 50,
        "minPoolSize": 5,
        "maxIdleTimeMS": 30000,
        "waitQueueTimeoutMS": 5000,
        "serverSelectionTimeoutMS": 5000,
        "connectTimeoutMS": 10000,
        "socketTimeoutMS": 30000,
        "retryWrites": True,
        "retryReads": True
    }


def get_global_database_name() -> str:
    """
    Get the name of the global database.
    
    Returns:
        Global database name
    """
    return "pms_global_database"


def get_organization_database_name(hostname: str) -> str:
    """
    Get the database name for an organization.
    
    Args:
        hostname: Organization hostname
        
    Returns:
        Organization database name
    """
    # Sanitize hostname for MongoDB database name (replace dots and other invalid chars)
    sanitized_hostname = hostname.replace(".", "_").replace("-", "_").lower()
    return f"pms_{sanitized_hostname}"


def get_collection_names() -> Dict[str, str]:
    """
    Get collection names used in the application.
    
    Returns:
        Dictionary mapping collection types to names
    """
    return {
        "salary_components": "salary_components",
        "salary_component_assignments": "salary_component_assignments",
        "global_salary_components": "global_salary_components",
        "employee_salaries": "employee_salaries",
        "tax_computations": "tax_computations",
        "organizations": "organizations",
        "users": "users"
    } 