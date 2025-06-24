"""
Database Connection Factory
SOLID-compliant factory for creating database connections
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum

from .database_connector import DatabaseConnector
from .mongodb_connector import MongoDBConnector, MongoDBConnectionPool

logger = logging.getLogger(__name__)


class DatabaseType(Enum):
    """Supported database types."""
    MONGODB = "mongodb"
    # Future database types can be added here
    # POSTGRESQL = "postgresql"
    # MYSQL = "mysql"


class ConnectionFactory:
    """
    Factory for creating database connector instances.
    
    Follows SOLID principles:
    - SRP: Only responsible for creating database connections
    - OCP: Can be extended with new database types without modification
    - LSP: All created connectors are substitutable
    - ISP: Focused interface for connection creation
    - DIP: Depends on abstractions (DatabaseConnector interface)
    """
    
    _connector_registry: Dict[DatabaseType, type] = {
        DatabaseType.MONGODB: MongoDBConnector,
    }
    
    @classmethod
    def create_connector(
        self,
        db_type: DatabaseType,
        connection_string: str,
        **kwargs
    ) -> DatabaseConnector:
        """
        Create database connector based on type.
        
        Args:
            db_type: Type of database
            connection_string: Database connection string
            **kwargs: Additional connection parameters
            
        Returns:
            Database connector instance
            
        Raises:
            ValueError: If database type is not supported
        """
        if db_type not in self._connector_registry:
            supported_types = [t.value for t in self._connector_registry.keys()]
            raise ValueError(
                f"Unsupported database type: {db_type.value}. "
                f"Supported types: {supported_types}"
            )
        
        connector_class = self._connector_registry[db_type]
        connector = connector_class()
        
        logger.info(f"Created {db_type.value} connector")
        return connector
    
    @classmethod
    def create_connection_pool(
        self,
        db_type: DatabaseType,
        connection_string: str,
        max_pool_size: int = 10,
        **kwargs
    ) -> Any:
        """
        Create database connection pool based on type.
        
        Args:
            db_type: Type of database
            connection_string: Database connection string
            max_pool_size: Maximum number of connections in pool
            **kwargs: Additional connection parameters
            
        Returns:
            Database connection pool instance
            
        Raises:
            ValueError: If database type is not supported
        """
        if db_type == DatabaseType.MONGODB:
            return MongoDBConnectionPool(connection_string, max_pool_size)
        else:
            supported_types = [t.value for t in DatabaseType]
            raise ValueError(
                f"Connection pool not supported for database type: {db_type.value}. "
                f"Supported types: {supported_types}"
            )
    
    @classmethod
    def register_connector(
        self,
        db_type: DatabaseType,
        connector_class: type
    ) -> None:
        """
        Register a new database connector type.
        
        Args:
            db_type: Database type to register
            connector_class: Connector class that implements DatabaseConnector
            
        Raises:
            TypeError: If connector_class doesn't implement DatabaseConnector
        """
        if not issubclass(connector_class, DatabaseConnector):
            raise TypeError(
                f"Connector class must implement DatabaseConnector interface. "
                f"Got: {connector_class}"
            )
        
        self._connector_registry[db_type] = connector_class
        logger.info(f"Registered connector for {db_type.value}: {connector_class.__name__}")
    
    @classmethod
    def get_supported_types(self) -> list[str]:
        """
        Get list of supported database types.
        
        Returns:
            List of supported database type names
        """
        return [db_type.value for db_type in self._connector_registry.keys()]


class DatabaseConnectionManager:
    """
    Manages database connections across the application.
    
    Provides a centralized way to manage database connections with
    proper lifecycle management and connection pooling.
    """
    
    def __init__(self):
        """Initialize connection manager."""
        self._connections: Dict[str, DatabaseConnector] = {}
        self._pools: Dict[str, Any] = {}
        
    async def create_connection(
        self,
        name: str,
        db_type: DatabaseType,
        connection_string: str,
        **kwargs
    ) -> DatabaseConnector:
        """
        Create and register a named database connection.
        
        Args:
            name: Name for the connection
            db_type: Type of database
            connection_string: Database connection string
            **kwargs: Additional connection parameters
            
        Returns:
            Database connector instance
        """
        if name in self._connections:
            logger.warning(f"Connection '{name}' already exists. Closing existing connection.")
            await self._connections[name].disconnect()
        
        connector = ConnectionFactory.create_connector(db_type, connection_string, **kwargs)
        await connector.connect(connection_string, **kwargs)
        
        self._connections[name] = connector
        logger.info(f"Created and registered connection '{name}'")
        
        return connector
    
    async def create_connection_pool(
        self,
        name: str,
        db_type: DatabaseType,
        connection_string: str,
        max_pool_size: int = 10,
        **kwargs
    ) -> Any:
        """
        Create and register a named connection pool.
        
        Args:
            name: Name for the connection pool
            db_type: Type of database
            connection_string: Database connection string
            max_pool_size: Maximum number of connections in pool
            **kwargs: Additional connection parameters
            
        Returns:
            Database connection pool instance
        """
        if name in self._pools:
            logger.warning(f"Connection pool '{name}' already exists. Closing existing pool.")
            await self._pools[name].close_all()
        
        pool = ConnectionFactory.create_connection_pool(
            db_type, connection_string, max_pool_size, **kwargs
        )
        
        self._pools[name] = pool
        logger.info(f"Created and registered connection pool '{name}'")
        
        return pool
    
    def get_connection(self, name: str) -> Optional[DatabaseConnector]:
        """
        Get a named database connection.
        
        Args:
            name: Name of the connection
            
        Returns:
            Database connector instance or None if not found
        """
        return self._connections.get(name)
    
    def get_connection_pool(self, name: str) -> Optional[Any]:
        """
        Get a named connection pool.
        
        Args:
            name: Name of the connection pool
            
        Returns:
            Connection pool instance or None if not found
        """
        return self._pools.get(name)
    
    async def close_connection(self, name: str) -> bool:
        """
        Close and remove a named connection.
        
        Args:
            name: Name of the connection to close
            
        Returns:
            True if connection was closed, False if not found
        """
        if name in self._connections:
            await self._connections[name].disconnect()
            del self._connections[name]
            logger.info(f"Closed connection '{name}'")
            return True
        return False
    
    async def close_connection_pool(self, name: str) -> bool:
        """
        Close and remove a named connection pool.
        
        Args:
            name: Name of the connection pool to close
            
        Returns:
            True if pool was closed, False if not found
        """
        if name in self._pools:
            await self._pools[name].close_all()
            del self._pools[name]
            logger.info(f"Closed connection pool '{name}'")
            return True
        return False
    
    async def close_all(self) -> None:
        """Close all connections and pools."""
        # Close all individual connections
        for name in list(self._connections.keys()):
            await self.close_connection(name)
        
        # Close all connection pools
        for name in list(self._pools.keys()):
            await self.close_connection_pool(name)
        
        logger.info("Closed all database connections and pools")
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get status of all connections and pools.
        
        Returns:
            Dictionary with connection status information
        """
        return {
            "connections": {
                name: conn.is_connected 
                for name, conn in self._connections.items()
            },
            "pools": {
                name: pool.pool_size 
                for name, pool in self._pools.items()
            }
        } 