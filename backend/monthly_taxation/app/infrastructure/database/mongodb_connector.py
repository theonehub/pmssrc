"""
MongoDB Database Connector
Handles MongoDB connections with organization-based multi-tenancy
"""

import logging
from typing import Optional, Dict
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
import os

logger = logging.getLogger(__name__)


class MongoDBConnector:
    """
    MongoDB connector with multi-tenancy support.
    
    Manages connections to organization-specific databases.
    Each organization gets its own database: pms_{hostname}
    """
    
    def __init__(self):
        """Initialize MongoDB connector"""
        self.client: Optional[AsyncIOMotorClient] = None
        self.databases: Dict[str, AsyncIOMotorDatabase] = {}
        self.connection_string = self._get_connection_string()
        self.is_connected = False
    
    async def initialize(self):
        """Initialize MongoDB connection"""
        try:
            logger.info("Initializing MongoDB connection...")
            
            self.client = AsyncIOMotorClient(
                self.connection_string,
                maxPoolSize=50,
                minPoolSize=5,
                maxIdleTimeMS=30000,
                waitQueueTimeoutMS=5000,
                serverSelectionTimeoutMS=5000
            )
            
            # Test connection
            await self.client.admin.command('ping')
            self.is_connected = True
            
            logger.info("MongoDB connection established successfully")
            
        except (ServerSelectionTimeoutError, ConnectionFailure) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise ConnectionError(f"Could not connect to MongoDB: {e}")
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            raise
    
    async def cleanup(self):
        """Close MongoDB connection"""
        if self.client:
            logger.info("Closing MongoDB connection...")
            self.client.close()
            self.databases.clear()
            self.is_connected = False
            logger.info("MongoDB connection closed")
    
    async def get_database(self, hostname: str) -> AsyncIOMotorDatabase:
        """
        Get database for organization.
        
        Args:
            hostname: Organization hostname
            
        Returns:
            AsyncIOMotorDatabase instance for the organization
        """
        if not self.is_connected:
            raise ConnectionError("Database not connected")
        
        # Sanitize hostname for MongoDB database name (replace dots and other invalid chars)
        sanitized_hostname = hostname.replace(".", "_").replace("-", "_").lower()
        database_name = f"pms_{sanitized_hostname}"
        
        if database_name not in self.databases:
            logger.info(f"Creating database connection for organization: {hostname}")
            self.databases[database_name] = self.client[database_name]
            
            # Ensure indexes for better performance
            await self._ensure_indexes(self.databases[database_name])
        
        return self.databases[database_name]
    
    async def _ensure_indexes(self, database: AsyncIOMotorDatabase):
        """Ensure proper indexes exist for performance"""
        try:
            # Salary components indexes
            components_collection = database["salary_components"]
            await components_collection.create_index("code", unique=True)
            await components_collection.create_index("component_type")
            await components_collection.create_index("is_active")
            await components_collection.create_index("created_at")
            
            # Employee salary indexes
            employee_salary_collection = database["employee_salaries"]
            await employee_salary_collection.create_index("employee_id")
            await employee_salary_collection.create_index("employee_code", unique=True)
            await employee_salary_collection.create_index("is_active")
            await employee_salary_collection.create_index("created_at")
            
            # Tax computation indexes
            tax_computation_collection = database["tax_computations"]
            await tax_computation_collection.create_index([("employee_id", 1), ("financial_year", 1)])
            await tax_computation_collection.create_index("computation_date")
            await tax_computation_collection.create_index("is_finalized")
            
            logger.info(f"Database indexes ensured for {database.name}")
            
        except Exception as e:
            logger.warning(f"Failed to create indexes: {e}")
    
    def _get_connection_string(self) -> str:
        """Get MongoDB connection string from environment or use provided default"""
        # First try to get from environment variables
        connection_string = os.getenv("MONGODB_URL")
        
        if not connection_string:
            # Use the provided connection string as default
            connection_string = "mongodb+srv://admin:test123@mongodbtest.jhfj7s3.mongodb.net/?appName=mongodbTest"
        
        logger.info(f"Using MongoDB connection: {connection_string.replace('test123', '***')}")  # Hide password in logs
        return connection_string
    
    async def get_health_status(self) -> dict:
        """Get database health status"""
        total_collections = 0
        if self.is_connected and self.databases:
            try:
                for db in self.databases.values():
                    collections = await db.list_collection_names()
                    total_collections += len(collections)
            except Exception as e:
                logger.warning(f"Error getting collection count: {e}")
        
        return {
            "connected": self.is_connected,
            "active_databases": len(self.databases),
            "connection_type": "Real MongoDB Atlas",
            "total_collections": total_collections
        } 