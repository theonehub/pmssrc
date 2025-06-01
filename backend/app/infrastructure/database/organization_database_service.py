"""
Organization Database Service
Provides database connections and collections based on organization context
"""

import logging
from typing import Optional, Any
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

from app.config.mongodb_config import get_mongodb_connection_string, get_mongodb_client_options
from app.infrastructure.database.mongodb_connector import MongoDBConnector
from app.auth.auth_dependencies import CurrentUser
from app.utils.logger import get_logger

logger = get_logger(__name__)


class OrganizationDatabaseService:
    """
    Service for handling organization-specific database operations.
    
    Responsibilities:
    - Provide database connections based on organization context
    - Handle collection access with proper naming conventions
    - Manage database lifecycle for different organizations
    """
    
    def __init__(self):
        """Initialize the organization database service."""
        self._connector = MongoDBConnector()
        self._connection_established = False
    
    async def _ensure_connection(self):
        """Ensure database connection is established."""
        if not self._connection_established:
            connection_string = get_mongodb_connection_string()
            options = get_mongodb_client_options()
            await self._connector.connect(connection_string, **options)
            self._connection_established = True
    
    async def get_organization_database(self, current_user: CurrentUser) -> AsyncIOMotorDatabase:
        """
        Get database instance for the user's organization.
        
        Args:
            current_user: Current authenticated user with organization context
            
        Returns:
            AsyncIOMotorDatabase: Database instance for the organization
        """
        await self._ensure_connection()
        
        database_name = current_user.database_name
        logger.debug(f"Accessing database: {database_name} for organization: {current_user.hostname}")
        
        return self._connector.get_database(database_name)
    
    async def get_organization_collection(
        self, 
        current_user: CurrentUser, 
        collection_name: str
    ) -> AsyncIOMotorCollection:
        """
        Get collection instance for the user's organization.
        
        Args:
            current_user: Current authenticated user with organization context
            collection_name: Name of the collection to access
            
        Returns:
            AsyncIOMotorCollection: Collection instance for the organization
        """
        await self._ensure_connection()
        
        database_name = current_user.database_name
        logger.debug(f"Accessing collection: {collection_name} from database: {database_name}")
        
        return self._connector.get_collection(database_name, collection_name)
    
    async def get_global_collection(self, collection_name: str) -> AsyncIOMotorCollection:
        """
        Get collection from global database (for cross-organization data).
        
        Args:
            collection_name: Name of the collection to access
            
        Returns:
            AsyncIOMotorCollection: Collection instance from global database
        """
        await self._ensure_connection()
        
        logger.debug(f"Accessing global collection: {collection_name}")
        return self._connector.get_collection("pms_global_database", collection_name)
    
    async def get_collection_with_fallback(
        self,
        current_user: CurrentUser,
        collection_name: str,
        try_global: bool = True
    ) -> AsyncIOMotorCollection:
        """
        Get collection with fallback to global database.
        
        Args:
            current_user: Current authenticated user with organization context
            collection_name: Name of the collection to access
            try_global: Whether to try global database if organization collection fails
            
        Returns:
            AsyncIOMotorCollection: Collection instance (organization or global)
        """
        try:
            # Try organization-specific database first
            org_collection = await self.get_organization_collection(current_user, collection_name)
            
            # Check if collection has data (optional validation)
            # For now, we'll return the collection and let the calling code handle empty collections
            return org_collection
            
        except Exception as e:
            if try_global:
                logger.warning(f"Failed to access organization collection {collection_name}: {e}")
                logger.info(f"Falling back to global collection: {collection_name}")
                return await self.get_global_collection(collection_name)
            else:
                raise
    
    async def list_organization_collections(self, current_user: CurrentUser) -> list:
        """
        List all collections in the user's organization database.
        
        Args:
            current_user: Current authenticated user with organization context
            
        Returns:
            list: List of collection names
        """
        database = await self.get_organization_database(current_user)
        return await database.list_collection_names()
    
    async def create_organization_indexes(self, current_user: CurrentUser):
        """
        Create necessary indexes for organization collections.
        
        Args:
            current_user: Current authenticated user with organization context
        """
        try:
            # Common collections and their indexes
            collections_indexes = {
                "users_info": [
                    ("employee_id", 1),
                    ("email", 1),
                    ("username", 1),
                    ("mobile", 1),
                    ("pan_number", 1)
                ],
                "attendance": [
                    ("employee_id", 1),
                    ("date", 1),
                    [("employee_id", 1), ("date", 1)]  # Compound index
                ],
                "leaves": [
                    ("employee_id", 1),
                    ("leave_id", 1),
                    ("start_date", 1),
                    ("status", 1)
                ],
                "payroll": [
                    ("employee_id", 1),
                    ("month", 1),
                    ("year", 1),
                    [("employee_id", 1), ("month", 1), ("year", 1)]  # Compound index
                ],
                "reimbursements": [
                    ("employee_id", 1),
                    ("status", 1),
                    ("submitted_date", 1)
                ]
            }
            
            database = await self.get_organization_database(current_user)
            
            for collection_name, indexes in collections_indexes.items():
                collection = database[collection_name]
                
                for index in indexes:
                    if isinstance(index, tuple):
                        # Single field index
                        await collection.create_index(index)
                    elif isinstance(index, list):
                        # Compound index
                        await collection.create_index(index)
            
            logger.info(f"Created indexes for organization: {current_user.hostname}")
            
        except Exception as e:
            logger.error(f"Failed to create indexes for organization {current_user.hostname}: {e}")
            # Don't raise the exception as indexes are not critical for basic operations
    
    async def close_connection(self):
        """Close database connection."""
        if self._connection_established:
            await self._connector.disconnect()
            self._connection_established = False


# Global instance
organization_db_service = OrganizationDatabaseService()


async def get_organization_database_service() -> OrganizationDatabaseService:
    """
    Dependency for getting organization database service.
    
    Returns:
        OrganizationDatabaseService: Database service instance
    """
    return organization_db_service 