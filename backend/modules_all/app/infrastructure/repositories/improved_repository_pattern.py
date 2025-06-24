"""
Improved Repository Pattern
Combines best practices from user and organisation repositories
"""

import logging
from typing import List, Optional, Dict, Any, TypeVar, Generic
from datetime import datetime
from abc import ABC, abstractmethod

from app.infrastructure.database.database_connector import DatabaseConnector
from app.domain.entities.base_entity import BaseEntity

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseEntity)


class ImprovedBaseRepository(ABC, Generic[T]):
    """
    Improved base repository pattern combining best practices.
    
    Key improvements:
    1. Uses DatabaseConnector abstraction (from user repo)
    2. Supports multi-tenancy (from user repo)
    3. Proper entity conversion (from organisation repo)
    4. Connection resilience (from user repo)
    5. Index management (from organisation repo)
    """
    
    def __init__(self, database_connector: DatabaseConnector, collection_name: str):
        """
        Initialize repository with database connector.
        
        Args:
            database_connector: Database connection abstraction
            collection_name: Name of the collection
        """
        self.db_connector = database_connector
        self._collection_name = collection_name
        
        # Connection configuration (set by dependency container)
        self._connection_string = None
        self._client_options = None
        
        # Initialize indexes
        self._ensure_indexes()
    
    def set_connection_config(self, connection_string: str, client_options: Dict[str, Any]):
        """Set MongoDB connection configuration."""
        self._connection_string = connection_string
        self._client_options = client_options
    
    async def _get_collection(self, organisation_id: Optional[str] = None):
        """
        Get collection with proper connection management.
        
        Combines user repo's connection resilience with organisation-based routing.
        """
        # Ensure database connection
        if not self.db_connector.is_connected:
            logger.info("Database not connected, establishing connection...")
            
            try:
                if self._connection_string and self._client_options:
                    connection_string = self._connection_string
                    options = self._client_options
                else:
                    # Fallback to config functions
                    from app.config.mongodb_config import get_mongodb_connection_string, get_mongodb_client_options
                    connection_string = get_mongodb_connection_string()
                    options = get_mongodb_client_options()
                
                await self.db_connector.connect(connection_string, **options)
                logger.info("MongoDB connection established successfully")
                
            except Exception as e:
                logger.error(f"Failed to establish database connection: {e}")
                raise RuntimeError(f"Database connection failed: {e}")
        
        # Get organisation-specific database
        db_name = f"pms_{organisation_id}" if organisation_id else "pms_global_database"
        
        try:
            db = self.db_connector.get_database(db_name)
            collection = db[self._collection_name]
            logger.info(f"Retrieved collection: {self._collection_name} from database: {db_name}")
            return collection
            
        except Exception as e:
            logger.error(f"Failed to get collection {self._collection_name}: {e}")
            # Reset connection for retry
            if hasattr(self.db_connector, '_client'):
                self.db_connector._client = None
            raise RuntimeError(f"Collection access failed: {e}")
    
    @abstractmethod
    def _entity_to_document(self, entity: T) -> Dict[str, Any]:
        """Convert domain entity to database document."""
        pass
    
    @abstractmethod
    def _document_to_entity(self, document: Dict[str, Any]) -> Optional[T]:
        """Convert database document to domain entity."""
        pass
    
    @abstractmethod
    def _define_indexes(self) -> List[Dict[str, Any]]:
        """Define indexes for the collection."""
        pass
    
    def _ensure_indexes(self):
        """
        Ensure indexes are created (non-blocking).
        
        This should be called during repository initialization.
        """
        try:
            indexes = self._define_indexes()
            if indexes:
                logger.info(f"Index definitions prepared for {self._collection_name}: {len(indexes)} indexes")
        except Exception as e:
            logger.warning(f"Failed to prepare index definitions for {self._collection_name}: {e}")
    
    async def _publish_events(self, events: List[Any]) -> None:
        """Publish domain events."""
        for event in events:
            logger.info(f"Publishing event: {type(event).__name__}")
            # Implement event publishing logic here
    
    # Common repository operations
    async def save(self, entity: T, organisation_id: Optional[str] = None) -> T:
        """Save entity (create or update)."""
        try:
            collection = await self._get_collection(organisation_id)
            document = self._entity_to_document(entity)
            
            # Use entity ID for upsert
            entity_id = getattr(entity, 'id', None) or getattr(entity, 'entity_id', None)
            if entity_id:
                result = await collection.replace_one(
                    {"_id": entity_id} if isinstance(entity_id, str) else {"id": str(entity_id)},
                    document,
                    upsert=True
                )
            else:
                result = await collection.insert_one(document)
            
            # Publish domain events
            if hasattr(entity, 'get_domain_events'):
                await self._publish_events(entity.get_domain_events())
                entity.clear_domain_events()
            
            logger.info(f"Saved entity: {type(entity).__name__}")
            return entity
            
        except Exception as e:
            logger.error(f"Error saving entity {type(entity).__name__}: {e}")
            raise
    
    async def get_by_id(self, entity_id: str, organisation_id: Optional[str] = None) -> Optional[T]:
        """Get entity by ID."""
        try:
            collection = await self._get_collection(organisation_id)
            
            # Try different ID field patterns
            for id_field in ["_id", "id", f"{self._collection_name.rstrip('s')}_id"]:
                document = await collection.find_one({
                    id_field: entity_id,
                    "is_deleted": {"$ne": True}
                })
                if document:
                    return self._document_to_entity(document)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting entity by ID {entity_id}: {e}")
            raise
    
    async def delete(self, entity_id: str, soft_delete: bool = True, organisation_id: Optional[str] = None) -> bool:
        """Delete entity (soft or hard)."""
        try:
            collection = await self._get_collection(organisation_id)
            
            if soft_delete:
                result = await collection.update_one(
                    {"_id": entity_id},
                    {
                        "$set": {
                            "is_deleted": True,
                            "deleted_at": datetime.utcnow()
                        }
                    }
                )
                return result.modified_count > 0
            else:
                result = await collection.delete_one({"_id": entity_id})
                return result.deleted_count > 0
                
        except Exception as e:
            logger.error(f"Error deleting entity {entity_id}: {e}")
            raise
    
    async def count_total(self, organisation_id: Optional[str] = None, include_deleted: bool = False) -> int:
        """Count total entities."""
        try:
            collection = await self._get_collection(organisation_id)
            
            filter_query = {}
            if not include_deleted:
                filter_query["is_deleted"] = {"$ne": True}
            
            return await collection.count_documents(filter_query)
            
        except Exception as e:
            logger.error(f"Error counting entities: {e}")
            raise


# Example implementation
class ImprovedOrganisationRepository(ImprovedBaseRepository):
    """
    Improved organisation repository using the new pattern.
    """
    
    def __init__(self, database_connector: DatabaseConnector):
        super().__init__(database_connector, "organisations")
    
    def _define_indexes(self) -> List[Dict[str, Any]]:
        """Define indexes for organisation collection."""
        return [
            {"fields": [("organisation_id", 1)], "unique": True},
            {"fields": [("name", 1)], "unique": True},
            {"fields": [("hostname", 1)], "unique": True},
            {"fields": [("status", 1)]},
            {"fields": [("organisation_type", 1)]},
            {"fields": [("created_at", -1)]},
        ]
    
    def _entity_to_document(self, organisation) -> Dict[str, Any]:
        """Convert organisation entity to document."""
        return {
            "organisation_id": organisation.organisation_id.value,
            "name": organisation.name,
            "organisation_type": organisation.organisation_type.value,
            "status": organisation.status.value,
            "hostname": organisation.hostname,
            "contact_information": {
                "email": organisation.contact_info.email,
                "phone": organisation.contact_info.phone,
                # ... other fields
            },
            "created_at": organisation.created_at,
            "updated_at": organisation.updated_at,
            "is_deleted": getattr(organisation, 'is_deleted', False)
        }
    
    def _document_to_entity(self, document: Dict[str, Any]):
        """Convert document to organisation entity."""
        # Proper entity reconstruction like organisation repo
        from app.domain.entities.organisation import Organisation
        from app.domain.value_objects.organisation_id import OrganisationId
        # ... other imports
        
        try:
            return Organisation.from_existing_data(
                organisation_id=OrganisationId.from_string(document["organisation_id"]),
                name=document["name"],
                # ... other fields
            )
        except Exception as e:
            logger.error(f"Error converting document to organisation: {e}")
            return None 