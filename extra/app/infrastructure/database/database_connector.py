"""
MongoDB Database Connector
Multi-tenant database connection management with Motor async driver
"""

import logging
from typing import Dict, Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure

from app.config.settings import settings

logger = logging.getLogger(__name__)


class DatabaseConnector:
    """
    MongoDB database connector with multi-tenant support.
    
    Manages connections to organization-specific databases using the pattern:
    {database_prefix}_{hostname}
    
    Example: pms_org1, pms_org2, etc.
    """
    
    def __init__(self):
        """Initialize database connector."""
        self._client: Optional[AsyncIOMotorClient] = None
        self._databases: Dict[str, AsyncIOMotorDatabase] = {}
        self._connection_url = settings.mongodb_url
        self._database_prefix = settings.database_prefix
    
    async def connect(self) -> None:
        """Establish connection to MongoDB."""
        try:
            self._client = AsyncIOMotorClient(
                self._connection_url,
                maxPoolSize=100,
                minPoolSize=10,
                maxIdleTimeMS=30000,
                waitQueueTimeoutMS=5000,
                serverSelectionTimeoutMS=5000
            )
            
            # Test the connection
            await self._client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self._client:
            self._client.close()
            self._databases.clear()
            logger.info("Disconnected from MongoDB")
    
    async def get_database(self, hostname: str) -> AsyncIOMotorDatabase:
        """
        Get organization-specific database.
        
        Args:
            hostname: Organization hostname identifier
            
        Returns:
            AsyncIOMotorDatabase: Organization-specific database instance
        """
        if not self._client:
            raise ConnectionError("Database client not connected. Call connect() first.")
        
        database_name = f"{self._database_prefix}_{hostname}"
        
        if database_name not in self._databases:
            self._databases[database_name] = self._client[database_name]
            logger.info(f"Created database connection for: {database_name}")
        
        return self._databases[database_name]
    
    async def get_client(self) -> AsyncIOMotorClient:
        """Get the raw MongoDB client."""
        if not self._client:
            raise ConnectionError("Database client not connected. Call connect() first.")
        return self._client
    
    async def health_check(self) -> bool:
        """Check database connection health."""
        try:
            if not self._client:
                return False
            
            await self._client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    async def create_indexes(self, hostname: str) -> None:
        """Create database indexes for organization."""
        try:
            db = await self.get_database(hostname)
            
            # Create indexes for common collections
            # User collection indexes
            await db.users.create_index("email", unique=True)
            await db.users.create_index("employee_id", unique=True)
            await db.users.create_index("is_active")
            
            # General indexes for audit fields
            await db.users.create_index("created_at")
            await db.users.create_index("updated_at")
            
            logger.info(f"Created indexes for database: {hostname}")
            
        except Exception as e:
            logger.error(f"Error creating indexes for {hostname}: {e}")
            raise


# Global database connector instance
database_connector = DatabaseConnector() 