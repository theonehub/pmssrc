"""
Database Connector Module
Handles MongoDB connection management and collection access
"""

from pymongo import MongoClient, ASCENDING
from app.config import MONGO_URI

# Import centralized logger
from app.utils.logger import get_logger

logger = get_logger(__name__)

database_clients = {}

def get_database_client(organisation_id: str = None) -> MongoClient:
    """
    Get MongoDB client for an organisation.
    
    Args:
        organisation_id: Organisation ID for multi-tenant support
        
    Returns:
        MongoClient: MongoDB client instance
    """
    try:
        global database_clients
        
        # Use default client for no organisation
        client_key = organisation_id or 'default'
        
        # Return existing client if available
        if client_key in database_clients:
            logger.debug(f"Using existing database client for: {client_key}")
            return database_clients[client_key]
        
        # Create new client
        logger.info(f"Creating new database client for: {client_key}")
        client = MongoClient(MONGO_URI)
        database_clients[client_key] = client
        
        return client
        
    except Exception as e:
        logger.error(f"Failed to get database client: {str(e)}", exc_info=True)
        raise

def get_database(organisation_id: str = None) -> str:
    """
    Get database name for an organisation.
    
    Args:
        organisation_id: Organisation ID for multi-tenant support
        
    Returns:
        str: Database name
    """
    try:
        # Use organisation-specific database if provided
        if organisation_id:
            db_name = f"pms_{organisation_id}"
            logger.debug(f"Using organisation database: {db_name}")
            return db_name
        
        # Use global database as fallback
        logger.debug("Using global database")
        return "pms_global_database"
        
    except Exception as e:
        logger.error(f"Failed to get database name: {str(e)}", exc_info=True)
        raise

def get_collection(database_name: str, collection_name: str):
    """
    Get MongoDB collection.
    
    Args:
        database_name: Database name
        collection_name: Collection name
        
    Returns:
        Collection: MongoDB collection instance
    """
    try:
        # Get client and database
        client = get_database_client()
        db = client[database_name]
        
        logger.debug(f"Accessing collection: {collection_name} in database: {database_name}")
        return db[collection_name]
        
    except Exception as e:
        logger.error(f"Failed to get collection {collection_name}: {str(e)}", exc_info=True)
        raise

def close_connections():
    """Close all database connections."""
    try:
        global database_clients
        
        for client_key, client in database_clients.items():
            logger.info(f"Closing database connection for: {client_key}")
            client.close()
        
        database_clients = {}
        logger.info("All database connections closed")
        
    except Exception as e:
        logger.error(f"Failed to close database connections: {str(e)}", exc_info=True)
        raise

