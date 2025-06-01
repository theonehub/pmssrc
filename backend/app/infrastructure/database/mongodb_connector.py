"""
MongoDB Database Connector Implementation
SOLID-compliant MongoDB connection management
"""

import logging
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection

from .database_connector import DatabaseConnector

logger = logging.getLogger(__name__)


class MongoDBConnector(DatabaseConnector):
    """
    MongoDB implementation of database connector.
    
    Provides MongoDB-specific connection management while maintaining
    SOLID principles through interface abstraction.
    
    Follows SOLID principles:
    - SRP: Only handles MongoDB connection concerns
    - OCP: Can be extended with additional MongoDB features
    - LSP: Substitutable with other DatabaseConnector implementations
    - ISP: Implements focused database connector interface
    - DIP: Depends on abstractions (DatabaseConnector interface)
    """
    
    def __init__(self):
        """Initialize MongoDB connector."""
        self._client: Optional[AsyncIOMotorClient] = None
        self._sync_client: Optional[MongoClient] = None
        self._databases: Dict[str, AsyncIOMotorDatabase] = {}
        self._connection_string: Optional[str] = None
        self._connection_params: Dict[str, Any] = {}
        
    async def connect(self, connection_string: str, **kwargs) -> None:
        """
        Establish MongoDB connection.
        
        Args:
            connection_string: MongoDB connection string
            **kwargs: Additional connection parameters
        """
        try:
            self._connection_string = connection_string
            self._connection_params = kwargs
            
            # Create async client
            self._client = AsyncIOMotorClient(
                connection_string,
                **kwargs
            )
            
            # Create sync client for operations that require it
            self._sync_client = MongoClient(
                connection_string,
                **kwargs
            )
            
            # Test connection
            await self._client.admin.command('ping')
            logger.info("MongoDB connection established successfully")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close MongoDB connection."""
        try:
            if self._client:
                self._client.close()
                self._client = None
                
            if self._sync_client:
                self._sync_client.close()
                self._sync_client = None
                
            self._databases.clear()
            logger.info("MongoDB connections closed")
            
        except Exception as e:
            logger.error(f"Error closing MongoDB connections: {e}")
    
    def get_database(self, database_name: str) -> AsyncIOMotorDatabase:
        """
        Get database instance.
        
        Args:
            database_name: Name of the database
            
        Returns:
            AsyncIOMotorDatabase instance
            
        Raises:
            RuntimeError: If not connected to MongoDB
        """
        if not self._client:
            raise RuntimeError(f"Not connected to MongoDB. Call connect() first. Connection string: {self._connection_string} and database_name: {database_name}")
            
        if database_name not in self._databases:
            self._databases[database_name] = self._client[database_name]
            logger.debug(f"Database '{database_name}' cached")
        
        return self._databases[database_name]
    
    def get_collection(self, database_name: str, collection_name: str) -> AsyncIOMotorCollection:
        """
        Get collection instance.
        
        Args:
            database_name: Name of the database
            collection_name: Name of the collection
            
        Returns:
            AsyncIOMotorCollection instance
        """
        database = self.get_database(database_name)
        return database[collection_name]
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check MongoDB health status.
        
        Returns:
            Health status information
        """
        try:
            if not self._client:
                return {
                    "status": "disconnected",
                    "connected": False,
                    "error": "No active connection"
                }
            
            # Ping the database
            await self._client.admin.command('ping')
            
            # Get server info
            server_info = await self._client.admin.command('buildInfo')
            
            return {
                "status": "healthy",
                "connected": True,
                "server_version": server_info.get("version"),
                "connection_string": self._connection_string,
                "cached_databases": list(self._databases.keys()),
                "uptime": server_info.get("uptime")
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e),
                "connection_string": self._connection_string
            }
    
    async def create_indexes(self, database_name: str, collection_name: str, indexes: List[Dict[str, Any]]) -> None:
        """
        Create indexes for a collection.
        
        Args:
            database_name: Name of the database
            collection_name: Name of the collection
            indexes: List of index specifications
        """
        try:
            collection = self.get_collection(database_name, collection_name)
            
            for index_spec in indexes:
                await collection.create_index(
                    index_spec.get("keys"),
                    **{k: v for k, v in index_spec.items() if k != "keys"}
                )
                
            logger.info(f"Created {len(indexes)} indexes for {database_name}.{collection_name}")
            
        except Exception as e:
            logger.error(f"Error creating indexes for {database_name}.{collection_name}: {e}")
            raise
    
    @asynccontextmanager
    async def transaction(self):
        """
        Create a MongoDB transaction context.
        
        Yields:
            Transaction session
        """
        if not self._client:
            raise RuntimeError("Not connected to MongoDB. Call connect() first.")
            
        async with await self._client.start_session() as session:
            async with session.start_transaction():
                try:
                    yield session
                except Exception:
                    await session.abort_transaction()
                    raise
    
    @property
    def is_connected(self) -> bool:
        """Check if MongoDB is connected."""
        try:
            if self._client:
                # This is a simple check - for a more thorough check use health_check()
                return True
            return False
        except Exception:
            return False
    
    def get_sync_database(self, database_name: str) -> Database:
        """
        Get synchronous database instance for operations that require it.
        
        Args:
            database_name: Name of the database
            
        Returns:
            Synchronous Database instance
            
        Raises:
            RuntimeError: If not connected to MongoDB
        """
        if not self._sync_client:
            raise RuntimeError("Not connected to MongoDB. Call connect() first.")
            
        return self._sync_client[database_name]
    
    def get_sync_collection(self, database_name: str, collection_name: str) -> Collection:
        """
        Get synchronous collection instance.
        
        Args:
            database_name: Name of the database
            collection_name: Name of the collection
            
        Returns:
            Synchronous Collection instance
        """
        database = self.get_sync_database(database_name)
        return database[collection_name]


class MongoDBConnectionPool:
    """
    MongoDB connection pool implementation.
    
    Manages multiple MongoDB connections efficiently for different databases.
    """
    
    def __init__(self, connection_string: str, max_pool_size: int = 10):
        """
        Initialize connection pool.
        
        Args:
            connection_string: MongoDB connection string
            max_pool_size: Maximum number of connections in pool
        """
        self.connection_string = connection_string
        self.max_pool_size = max_pool_size
        self._connections: Dict[str, MongoDBConnector] = {}
        
    async def get_connection(self, database_name: str) -> MongoDBConnector:
        """
        Get a connection for a specific database.
        
        Args:
            database_name: Name of the database
            
        Returns:
            MongoDB connector instance
        """
        if database_name not in self._connections:
            if len(self._connections) >= self.max_pool_size:
                raise RuntimeError(f"Connection pool limit reached ({self.max_pool_size})")
                
            connector = MongoDBConnector()
            await connector.connect(self.connection_string)
            self._connections[database_name] = connector
            
        return self._connections[database_name]
    
    async def return_connection(self, connection: MongoDBConnector) -> None:
        """
        Return a connection to the pool (no-op for this implementation).
        
        Args:
            connection: Database connector to return
        """
        # In this implementation, connections are kept alive
        # Could be extended to implement actual pooling logic
        pass
    
    async def close_all(self) -> None:
        """Close all connections in the pool."""
        for connector in self._connections.values():
            await connector.disconnect()
        self._connections.clear()
    
    @property
    def pool_size(self) -> int:
        """Get current pool size."""
        return len(self._connections) 