"""
Base Repository Implementation
SOLID-compliant base class for all repositories
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic
from datetime import datetime
from bson import ObjectId

from ..database.database_connector import DatabaseConnector

logger = logging.getLogger(__name__)

T = TypeVar('T')  # Generic type for domain entities


class BaseRepository(ABC, Generic[T]):
    """
    Abstract base repository class following SOLID principles.
    
    Provides common functionality for all repositories while maintaining
    separation of concerns and dependency inversion.
    
    Follows SOLID principles:
    - SRP: Only handles common repository concerns
    - OCP: Can be extended by specific repository implementations
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for repository operations
    - DIP: Depends on DatabaseConnector abstraction
    """
    
    def __init__(self, database_connector: DatabaseConnector, collection_name: str):
        """
        Initialize base repository.
        
        Args:
            database_connector: Database connection abstraction
            collection_name: Name of the collection/table
        """
        self._db_connector = database_connector
        self._collection_name = collection_name
        
    async def _get_collection(self, organisation_id: Optional[str] = None):
        """
        Get collection for specific organisation or global.
        
        Ensures database connection is established in the correct event loop.
        
        Args:
            organisation_id: Organisation ID for multi-tenant support
            
        Returns:
            Collection instance
        """
        # Ensure database is connected in the current event loop
        if not self._db_connector.is_connected:
            logger.info("Database not connected, establishing connection...")
            
            try:
                # Check if connection parameters are available from DI container
                if hasattr(self._db_connector, '_connection_string') and self._db_connector._connection_string:
                    logger.info("Using stored connection parameters from dependency injection")
                    await self._db_connector.connect(
                        self._db_connector._connection_string,
                        **getattr(self._db_connector, '_connection_params', {})
                    )
                else:
                    # Fallback: load from mongodb_config
                    logger.info("Loading connection parameters from mongodb_config")
                    from app.config.mongodb_config import get_mongodb_connection_string, get_mongodb_client_options
                    connection_string = get_mongodb_connection_string()
                    client_options = get_mongodb_client_options()
                    await self._db_connector.connect(connection_string, **client_options)
                
                logger.info("MongoDB connection established successfully in current event loop")
                
            except Exception as e:
                logger.error(f"Failed to establish database connection: {e}")
                raise RuntimeError(f"Database connection failed: {e}")
        
        # Verify connection is still active
        try:
            # This will raise an exception if connection is invalid
            db_name = f"pms_{organisation_id}" if organisation_id else "pms_global_database"
            collection = self._db_connector.get_collection(db_name, self._collection_name)
            logger.info(f"Successfully retrieved collection: {self._collection_name} from database: {db_name}")
            return collection
            
        except Exception as e:
            logger.error(f"Failed to get collection {self._collection_name}: {e}")
            # Reset connection state to force reconnection on next call
            if hasattr(self._db_connector, '_client'):
                self._db_connector._client = None
            raise RuntimeError(f"Collection access failed: {e}")
    
    @abstractmethod
    def _entity_to_document(self, entity: T) -> Dict[str, Any]:
        """
        Convert domain entity to database document.
        
        Args:
            entity: Domain entity to convert
            
        Returns:
            Database document representation
        """
        pass
    
    @abstractmethod
    def _document_to_entity(self, document: Dict[str, Any]) -> T:
        """
        Convert database document to domain entity.
        
        Args:
            document: Database document to convert
            
        Returns:
            Domain entity instance
        """
        pass
    
    def _prepare_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare database filters from input parameters.
        
        Args:
            filters: Input filter parameters
            
        Returns:
            Database-specific filter dictionary
        """
        db_filter = {}
        
        for key, value in filters.items():
            if value is not None:
                if key == "id" and isinstance(value, str):
                    # Convert string ID to ObjectId if needed
                    try:
                        db_filter["_id"] = ObjectId(value)
                    except:
                        db_filter["_id"] = value
                else:
                    db_filter[key] = value
        
        return db_filter
    
    def _prepare_sort(self, sort_by: Optional[str] = None, sort_order: int = 1) -> List[tuple]:
        """
        Prepare sort parameters for database query.
        
        Args:
            sort_by: Field to sort by
            sort_order: Sort order (1 for ascending, -1 for descending)
            
        Returns:
            List of sort tuples
        """
        if sort_by:
            return [(sort_by, sort_order)]
        return [("created_at", -1)]  # Default sort by creation date
    
    async def _execute_query(
        self,
        filters: Dict[str, Any],
        skip: int = 0,
        limit: int = 100,
        sort_by: Optional[str] = None,
        sort_order: int = 1,
        organisation_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a database query with common parameters.
        
        Args:
            filters: Query filters
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            sort_by: Field to sort by
            sort_order: Sort order
            organisation_id: Organisation ID for multi-tenant support
            
        Returns:
            List of database documents
        """
        try:
            collection = await self._get_collection(organisation_id)
            db_filter = self._prepare_filter(filters)
            sort_params = self._prepare_sort(sort_by, sort_order)
            
            cursor = collection.find(db_filter).sort(sort_params).skip(skip).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            logger.info(f"Query executed: {len(documents)} documents found")
            return documents
            
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise
    
    async def _count_documents(
        self,
        filters: Dict[str, Any],
        organisation_id: Optional[str] = None
    ) -> int:
        """
        Count documents matching filters.
        
        Args:
            filters: Query filters
            organisation_id: Organisation ID for multi-tenant support
            
        Returns:
            Number of matching documents
        """
        try:
            collection = await self._get_collection(organisation_id)
            db_filter = self._prepare_filter(filters)
            
            count = await collection.count_documents(db_filter)
            logger.info(f"Document count: {count}")
            return count
            
        except Exception as e:
            logger.error(f"Error counting documents: {e}")
            raise
    
    async def _insert_document(
        self,
        document: Dict[str, Any],
        organisation_id: Optional[str] = None
    ) -> str:
        """
        Insert a single document.
        
        Args:
            document: Document to insert
            organisation_id: Organisation ID for multi-tenant support
            
        Returns:
            Inserted document ID
        """
        try:
            collection = await self._get_collection(organisation_id)
            
            # Add timestamps
            now = datetime.utcnow()
            document.setdefault("created_at", now)
            document.setdefault("updated_at", now)
            
            result = await collection.insert_one(document)
            logger.info(f"Document inserted with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error inserting document: {e}")
            raise
    
    async def _update_document(
        self,
        filters: Dict[str, Any],
        update_data: Dict[str, Any],
        organisation_id: Optional[str] = None,
        upsert: bool = False
    ) -> bool:
        """
        Update documents matching filters.
        
        Args:
            filters: Query filters to match documents
            update_data: Data to update
            organisation_id: Organisation ID for multi-tenant support
            upsert: Whether to insert if document doesn't exist
            
        Returns:
            True if documents were modified, False otherwise
        """
        try:
            collection = await self._get_collection(organisation_id)
            db_filter = self._prepare_filter(filters)
            
            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            result = await collection.update_many(
                db_filter,
                {"$set": update_data},
                upsert=upsert
            )
            
            logger.info(f"Documents updated: {result.modified_count}")
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating documents: {e}")
            raise
    
    async def _delete_document(
        self,
        filters: Dict[str, Any],
        organisation_id: Optional[str] = None,
        soft_delete: bool = True
    ) -> bool:
        """
        Delete documents matching filters.
        
        Args:
            filters: Query filters to match documents
            organisation_id: Organisation ID for multi-tenant support
            soft_delete: Whether to perform soft delete (mark as deleted)
            
        Returns:
            True if documents were deleted, False otherwise
        """
        try:
            collection = await self._get_collection(organisation_id)
            db_filter = self._prepare_filter(filters)
            
            if soft_delete:
                # Soft delete: mark as deleted
                update_data = {
                    "is_deleted": True,
                    "deleted_at": datetime.utcnow()
                }
                result = await collection.update_many(
                    db_filter,
                    {"$set": update_data}
                )
                deleted_count = result.modified_count
            else:
                # Hard delete: remove from database
                result = await collection.delete_many(db_filter)
                deleted_count = result.deleted_count
            
            logger.info(f"Documents deleted: {deleted_count}")
            return deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            raise
    
    async def _aggregate(
        self,
        pipeline: List[Dict[str, Any]],
        organisation_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute aggregation pipeline.
        
        Args:
            pipeline: Aggregation pipeline stages
            organisation_id: Organisation ID for multi-tenant support
            
        Returns:
            Aggregation results
        """
        try:
            collection = await self._get_collection(organisation_id)
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            logger.info(f"Aggregation executed: {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error executing aggregation: {e}")
            raise
    
    async def health_check(self, organisation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Check repository health status.
        
        Args:
            organisation_id: Organisation ID for multi-tenant support
            
        Returns:
            Health status information
        """
        try:
            collection = await self._get_collection(organisation_id)
            
            # Simple ping to check collection accessibility
            count = await collection.count_documents({})
            
            return {
                "status": "healthy",
                "collection": self._collection_name,
                "organisation_id": organisation_id,
                "document_count": count,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed for {self._collection_name}: {e}")
            return {
                "status": "unhealthy",
                "collection": self._collection_name,
                "organisation_id": organisation_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            } 