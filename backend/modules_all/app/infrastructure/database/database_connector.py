"""
Database Connector Interface
Following SOLID principles for database abstraction
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from contextlib import asynccontextmanager


class DatabaseConnector(ABC):
    """
    Abstract database connector interface.
    
    Follows SOLID principles:
    - SRP: Only handles database connection concerns
    - OCP: Can be extended with new database implementations
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for database operations
    - DIP: High-level modules depend on this abstraction
    """
    
    @abstractmethod
    async def connect(self, connection_string: str, **kwargs) -> None:
        """
        Establish database connection.
        
        Args:
            connection_string: Database connection string
            **kwargs: Additional connection parameters
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close database connection."""
        pass
    
    @abstractmethod
    def get_database(self, database_name: str) -> Any:
        """
        Get database instance.
        
        Args:
            database_name: Name of the database
            
        Returns:
            Database instance
        """
        pass
    
    @abstractmethod
    def get_collection(self, database_name: str, collection_name: str) -> Any:
        """
        Get collection instance.
        
        Args:
            database_name: Name of the database
            collection_name: Name of the collection
            
        Returns:
            Collection instance
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Check database health status.
        
        Returns:
            Health status information
        """
        pass
    
    @abstractmethod
    async def create_indexes(self, database_name: str, collection_name: str, indexes: List[Dict[str, Any]]) -> None:
        """
        Create indexes for a collection.
        
        Args:
            database_name: Name of the database
            collection_name: Name of the collection
            indexes: List of index specifications
        """
        pass
    
    @abstractmethod
    @asynccontextmanager
    async def transaction(self):
        """
        Create a database transaction context.
        
        Yields:
            Transaction session
        """
        pass
    
    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if database is connected."""
        pass


class DatabaseConnectionPool(ABC):
    """
    Abstract database connection pool interface.
    
    Manages multiple database connections efficiently.
    """
    
    @abstractmethod
    async def get_connection(self, database_name: str) -> DatabaseConnector:
        """
        Get a connection from the pool.
        
        Args:
            database_name: Name of the database
            
        Returns:
            Database connector instance
        """
        pass
    
    @abstractmethod
    async def return_connection(self, connection: DatabaseConnector) -> None:
        """
        Return a connection to the pool.
        
        Args:
            connection: Database connector to return
        """
        pass
    
    @abstractmethod
    async def close_all(self) -> None:
        """Close all connections in the pool."""
        pass
    
    @property
    @abstractmethod
    def pool_size(self) -> int:
        """Get current pool size."""
        pass 