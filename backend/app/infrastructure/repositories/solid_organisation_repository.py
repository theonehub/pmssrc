"""
SOLID-Compliant Organisation Repository Implementation
Replaces the procedural organisation_database.py with proper SOLID architecture
"""

import logging
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

# Import domain entities
try:
    from domain.entities.organisation import Organisation
    from domain.value_objects.organisation_id import OrganisationId
    from models.organisation import Organisation as OrganisationModel, OrganisationCreate, OrganisationUpdate
except ImportError:
    # Fallback classes for migration compatibility
    class Organisation:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        def dict(self):
            return {k: v for k, v in self.__dict__.items()}
        def model_dump(self):
            return {k: v for k, v in self.__dict__.items()}
    
    class OrganisationId:
        def __init__(self, value: str):
            self.value = value
        def __str__(self):
            return self.value
    
    class OrganisationModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        def dict(self):
            return {k: v for k, v in self.__dict__.items()}
        def model_dump(self):
            return {k: v for k, v in self.__dict__.items()}
    
    class OrganisationCreate:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        def model_dump(self):
            return {k: v for k, v in self.__dict__.items()}
    
    class OrganisationUpdate:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        def model_dump(self):
            return {k: v for k, v in self.__dict__.items()}

# Import application interfaces
try:
    from application.interfaces.repositories.organisation_repository import (
        OrganisationCommandRepository, OrganisationQueryRepository,
        OrganisationAnalyticsRepository, OrganisationRepository
    )
except ImportError:
    # Fallback interfaces
    from abc import ABC, abstractmethod
    
    class OrganisationCommandRepository(ABC):
        pass
    
    class OrganisationQueryRepository(ABC):
        pass
    
    class OrganisationAnalyticsRepository(ABC):
        pass
    
    class OrganisationRepository(ABC):
        pass

# Import DTOs
try:
    from application.dto.organisation_dto import (
        OrganisationSearchFiltersDTO, OrganisationStatisticsDTO
    )
except ImportError:
    # Fallback DTOs
    class OrganisationSearchFiltersDTO:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class OrganisationStatisticsDTO:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

from .base_repository import BaseRepository
from ..database.database_connector import DatabaseConnector

logger = logging.getLogger(__name__)


class SolidOrganisationRepository(
    BaseRepository[Organisation],
    OrganisationCommandRepository,
    OrganisationQueryRepository,
    OrganisationAnalyticsRepository,
    OrganisationRepository
):
    """
    SOLID-compliant organisation repository implementation.
    
    Replaces the procedural organisation_database.py with proper SOLID architecture:
    - Single Responsibility: Only handles organisation data persistence
    - Open/Closed: Can be extended without modification
    - Liskov Substitution: Implements all organisation repository interfaces
    - Interface Segregation: Implements focused organisation repository interfaces
    - Dependency Inversion: Depends on DatabaseConnector abstraction
    """
    
    def __init__(self, database_connector: DatabaseConnector):
        """
        Initialize organisation repository.
        
        Args:
            database_connector: Database connection abstraction
        """
        # Organisation data is stored in global database
        super().__init__(database_connector, "organisation")
        self._global_db = "global_database"
        
    def _entity_to_document(self, organisation: Organisation) -> Dict[str, Any]:
        """
        Convert Organisation entity to database document.
        
        Args:
            organisation: Organisation entity to convert
            
        Returns:
            Database document representation
        """
        if hasattr(organisation, 'model_dump'):
            document = organisation.model_dump()
        elif hasattr(organisation, 'dict'):
            document = organisation.dict()
        else:
            document = {k: v for k, v in organisation.__dict__.items()}
        
        # Remove the 'id' field if present (MongoDB uses '_id')
        if 'id' in document:
            del document['id']
        
        # Ensure proper field mapping for legacy compatibility
        if 'organisation_id' not in document and hasattr(organisation, 'organisation_id'):
            document['organisation_id'] = getattr(organisation, 'organisation_id')
        
        # Set default values
        if 'is_active' not in document:
            document['is_active'] = True
        
        return document
    
    def _document_to_entity(self, document: Dict[str, Any]) -> Organisation:
        """
        Convert database document to Organisation entity.
        
        Args:
            document: Database document to convert
            
        Returns:
            Organisation entity instance
        """
        # Convert MongoDB _id to id
        if '_id' in document:
            document['id'] = str(document['_id'])
            del document['_id']
        
        return Organisation(**document)
    
    def _get_collection(self, organization_id: str = None):
        """Override to always use global database for organisations."""
        return self._db_connector.get_collection(self._global_db, self._collection_name)
    
    async def _ensure_indexes(self) -> None:
        """Ensure necessary indexes for optimal query performance."""
        try:
            collection = self._get_collection()
            
            # Index for organisation_id queries
            await collection.create_index([
                ("organisation_id", 1)
            ], unique=True)
            
            # Index for hostname queries
            await collection.create_index([
                ("hostname", 1)
            ], unique=True)
            
            # Index for name queries
            await collection.create_index([
                ("name", 1)
            ])
            
            # Index for active organisations
            await collection.create_index([
                ("is_active", 1),
                ("name", 1)
            ])
            
            # Index for created_at queries
            await collection.create_index([
                ("created_at", -1)
            ])
            
            logger.info("Organisation indexes ensured")
            
        except Exception as e:
            logger.error(f"Error ensuring organisation indexes: {e}")
    
    # Command Repository Implementation
    async def save(self, organisation: Organisation) -> Organisation:
        """
        Save organisation record.
        
        Replaces: create_organisation() function
        """
        try:
            # Ensure indexes
            await self._ensure_indexes()
            
            # Prepare document
            document = self._entity_to_document(organisation)
            
            # Set timestamps
            if not document.get('created_at'):
                document['created_at'] = datetime.now()
            document['updated_at'] = datetime.now()
            
            # Check for existing record by organisation_id
            existing = None
            if document.get('organisation_id'):
                existing = await self.get_by_id(document['organisation_id'])
            
            if existing:
                # Update existing record
                filters = {"organisation_id": document['organisation_id']}
                success = await self._update_document(
                    filters=filters,
                    update_data=document,
                    organization_id=self._global_db
                )
                if success:
                    return await self.get_by_id(document['organisation_id'])
                else:
                    raise ValueError("Failed to update organisation record")
            else:
                # Insert new record
                collection = self._get_collection()
                result = await collection.insert_one(document)
                # Return the saved document
                saved_doc = await collection.find_one({"_id": result.inserted_id})
                return self._document_to_entity(saved_doc)
            
        except Exception as e:
            logger.error(f"Error saving organisation: {e}")
            raise
    
    async def update(self, organisation_id: str, update_data: Dict[str, Any]) -> Optional[Organisation]:
        """
        Update organisation record.
        
        Replaces: update_organisation() function
        """
        try:
            # Add updated timestamp
            update_data['updated_at'] = datetime.now()
            
            collection = self._get_collection()
            
            # Update the document
            result = await collection.update_one(
                {"organisation_id": organisation_id},
                {"$set": update_data}
            )
            
            if result.matched_count > 0:
                # Get the updated document
                updated_doc = await collection.find_one({"organisation_id": organisation_id})
                if updated_doc:
                    return self._document_to_entity(updated_doc)
            
            return None
            
        except Exception as e:
            logger.error(f"Error updating organisation {organisation_id}: {e}")
            return None
    
    async def delete(self, organisation_id: str) -> bool:
        """
        Delete organisation record (soft delete).
        """
        try:
            # Soft delete by setting is_active to False
            update_data = {
                "is_active": False,
                "updated_at": datetime.now()
            }
            
            updated_org = await self.update(organisation_id, update_data)
            return updated_org is not None
            
        except Exception as e:
            logger.error(f"Error deleting organisation {organisation_id}: {e}")
            return False
    
    # Query Repository Implementation
    async def get_by_id(self, organisation_id: str) -> Optional[Organisation]:
        """
        Get organisation record by ID.
        
        Replaces: get_organisation_by_id() function
        """
        try:
            collection = self._get_collection()
            document = await collection.find_one({"organisation_id": organisation_id})
            
            if document:
                return self._document_to_entity(document)
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving organisation {organisation_id}: {e}")
            return None
    
    async def get_by_hostname(self, hostname: str) -> Optional[Organisation]:
        """
        Get organisation record by hostname.
        
        Replaces: get_organisation_by_hostname() function
        """
        try:
            collection = self._get_collection()
            document = await collection.find_one({"hostname": hostname})
            
            if document:
                return self._document_to_entity(document)
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving organisation by hostname {hostname}: {e}")
            return None
    
    async def get_all_active(self) -> List[Organisation]:
        """
        Get all active organisations.
        
        Replaces: get_all_organisations() function
        """
        try:
            collection = self._get_collection()
            cursor = collection.find({"is_active": True})
            documents = await cursor.to_list(length=None)
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error retrieving all active organisations: {e}")
            return []
    
    async def get_all(self) -> List[Organisation]:
        """Get all organisations (active and inactive)."""
        try:
            collection = self._get_collection()
            cursor = collection.find({})
            documents = await cursor.to_list(length=None)
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error retrieving all organisations: {e}")
            return []
    
    async def get_by_name(self, name: str) -> Optional[Organisation]:
        """Get organisation by name."""
        try:
            collection = self._get_collection()
            document = await collection.find_one({"name": name, "is_active": True})
            
            if document:
                return self._document_to_entity(document)
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving organisation by name {name}: {e}")
            return None
    
    async def search(self, filters: OrganisationSearchFiltersDTO) -> List[Organisation]:
        """Search organisations with filters."""
        try:
            query_filters = {}
            
            if hasattr(filters, 'name') and filters.name:
                query_filters["name"] = {"$regex": filters.name, "$options": "i"}
            
            if hasattr(filters, 'hostname') and filters.hostname:
                query_filters["hostname"] = {"$regex": filters.hostname, "$options": "i"}
            
            if hasattr(filters, 'is_active') and filters.is_active is not None:
                query_filters["is_active"] = filters.is_active
            
            # Get pagination parameters
            page = getattr(filters, 'page', 1)
            page_size = getattr(filters, 'page_size', 50)
            skip = (page - 1) * page_size
            
            collection = self._get_collection()
            cursor = collection.find(query_filters).skip(skip).limit(page_size).sort("name", 1)
            documents = await cursor.to_list(length=None)
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error searching organisations: {e}")
            return []
    
    async def count_all(self) -> int:
        """
        Count all organisations.
        
        Replaces: get_organisations_count() function
        """
        try:
            collection = self._get_collection()
            return await collection.count_documents({})
            
        except Exception as e:
            logger.error(f"Error counting organisations: {e}")
            return 0
    
    async def count_active(self) -> int:
        """Count active organisations."""
        try:
            collection = self._get_collection()
            return await collection.count_documents({"is_active": True})
            
        except Exception as e:
            logger.error(f"Error counting active organisations: {e}")
            return 0
    
    async def count_by_filters(self, filters: OrganisationSearchFiltersDTO) -> int:
        """Count organisations matching filters."""
        try:
            query_filters = {}
            
            if hasattr(filters, 'name') and filters.name:
                query_filters["name"] = {"$regex": filters.name, "$options": "i"}
            
            if hasattr(filters, 'is_active') and filters.is_active is not None:
                query_filters["is_active"] = filters.is_active
            
            collection = self._get_collection()
            return await collection.count_documents(query_filters)
            
        except Exception as e:
            logger.error(f"Error counting organisations: {e}")
            return 0
    
    # Analytics Repository Implementation
    async def get_organisation_statistics(self) -> Dict[str, Any]:
        """Get organisation statistics."""
        try:
            collection = self._get_collection()
            
            # Use aggregation pipeline for statistics
            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "total_organisations": {"$sum": 1},
                        "active_organisations": {
                            "$sum": {"$cond": [{"$eq": ["$is_active", True]}, 1, 0]}
                        },
                        "inactive_organisations": {
                            "$sum": {"$cond": [{"$eq": ["$is_active", False]}, 1, 0]}
                        }
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "total_organisations": 1,
                        "active_organisations": 1,
                        "inactive_organisations": 1
                    }
                }
            ]
            
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            if results:
                stats = results[0]
                return {
                    "total_organisations": stats.get("total_organisations", 0),
                    "active_organisations": stats.get("active_organisations", 0),
                    "inactive_organisations": stats.get("inactive_organisations", 0)
                }
            else:
                return {
                    "total_organisations": 0,
                    "active_organisations": 0,
                    "inactive_organisations": 0
                }
                
        except Exception as e:
            logger.error(f"Error getting organisation statistics: {e}")
            return {}
    
    async def get_recent_organisations(self, limit: int = 10) -> List[Organisation]:
        """Get recently created organisations."""
        try:
            collection = self._get_collection()
            cursor = collection.find({"is_active": True}).sort("created_at", -1).limit(limit)
            documents = await cursor.to_list(length=None)
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting recent organisations: {e}")
            return []
    
    # Legacy compatibility methods
    async def get_all_organisations_legacy(self) -> List[Dict[str, Any]]:
        """
        Legacy compatibility for get_all_organisations() function.
        
        Returns:
            List of organisation documents without _id field
        """
        try:
            organisations = await self.get_all_active()
            
            # Convert to legacy document format (without _id)
            legacy_organisations = []
            for org in organisations:
                legacy_data = {
                    "organisation_id": getattr(org, 'organisation_id', ''),
                    "name": getattr(org, 'name', ''),
                    "hostname": getattr(org, 'hostname', ''),
                    "is_active": getattr(org, 'is_active', True),
                    "created_at": getattr(org, 'created_at', None),
                    "updated_at": getattr(org, 'updated_at', None)
                }
                # Add any other fields that might exist
                for key, value in org.__dict__.items():
                    if key not in legacy_data:
                        legacy_data[key] = value
                
                legacy_organisations.append(legacy_data)
            
            return legacy_organisations
            
        except Exception as e:
            logger.error(f"Error getting all organisations (legacy): {e}")
            return []
    
    async def get_organisations_count_legacy(self) -> int:
        """
        Legacy compatibility for get_organisations_count() function.
        """
        return await self.count_all()
    
    async def get_organisation_by_id_legacy(self, organisation_id: str) -> Optional[Dict[str, Any]]:
        """
        Legacy compatibility for get_organisation_by_id() function.
        """
        try:
            organisation = await self.get_by_id(organisation_id)
            
            if organisation:
                # Convert to legacy document format
                legacy_data = {
                    "organisation_id": getattr(organisation, 'organisation_id', ''),
                    "name": getattr(organisation, 'name', ''),
                    "hostname": getattr(organisation, 'hostname', ''),
                    "is_active": getattr(organisation, 'is_active', True),
                    "created_at": getattr(organisation, 'created_at', None),
                    "updated_at": getattr(organisation, 'updated_at', None)
                }
                # Add any other fields that might exist
                for key, value in organisation.__dict__.items():
                    if key not in legacy_data:
                        legacy_data[key] = value
                
                return legacy_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting organisation by ID (legacy): {e}")
            return None
    
    async def get_organisation_by_hostname_legacy(self, hostname: str) -> Optional[Dict[str, Any]]:
        """
        Legacy compatibility for get_organisation_by_hostname() function.
        """
        try:
            organisation = await self.get_by_hostname(hostname)
            
            if organisation:
                # Convert to legacy document format
                legacy_data = {
                    "organisation_id": getattr(organisation, 'organisation_id', ''),
                    "name": getattr(organisation, 'name', ''),
                    "hostname": getattr(organisation, 'hostname', ''),
                    "is_active": getattr(organisation, 'is_active', True),
                    "created_at": getattr(organisation, 'created_at', None),
                    "updated_at": getattr(organisation, 'updated_at', None)
                }
                # Add any other fields that might exist
                for key, value in organisation.__dict__.items():
                    if key not in legacy_data:
                        legacy_data[key] = value
                
                return legacy_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting organisation by hostname (legacy): {e}")
            return None
    
    async def create_organisation_legacy(self, organisation: OrganisationCreate):
        """
        Legacy compatibility for create_organisation() function.
        """
        try:
            # Convert OrganisationCreate to Organisation entity
            org_data = organisation.model_dump()
            org_entity = Organisation(**org_data)
            
            # Save using new method
            saved_org = await self.save(org_entity)
            
            # Return legacy-style result (insert result)
            return type('InsertResult', (), {
                'inserted_id': getattr(saved_org, 'id', None)
            })()
            
        except Exception as e:
            logger.error(f"Error creating organisation (legacy): {e}")
            raise
    
    async def update_organisation_legacy(self, organisation_id: str, 
                                        organisation: Union[OrganisationUpdate, dict]) -> Optional[Dict[str, Any]]:
        """
        Legacy compatibility for update_organisation() function.
        """
        try:
            # Convert to dict if it's a Pydantic model
            update_data = organisation.model_dump() if hasattr(organisation, 'model_dump') else organisation
            
            # Update using new method
            updated_org = await self.update(organisation_id, update_data)
            
            if updated_org:
                # Convert to legacy document format (without _id)
                legacy_data = {
                    "organisation_id": getattr(updated_org, 'organisation_id', ''),
                    "name": getattr(updated_org, 'name', ''),
                    "hostname": getattr(updated_org, 'hostname', ''),
                    "is_active": getattr(updated_org, 'is_active', True),
                    "created_at": getattr(updated_org, 'created_at', None),
                    "updated_at": getattr(updated_org, 'updated_at', None)
                }
                # Add any other fields that might exist
                for key, value in updated_org.__dict__.items():
                    if key not in legacy_data:
                        legacy_data[key] = value
                
                return legacy_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error updating organisation (legacy): {e}")
            return None 