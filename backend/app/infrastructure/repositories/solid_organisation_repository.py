"""
SOLID-Compliant Organisation Repository Implementation
Replaces the procedural organisation_database.py with proper SOLID architecture
"""

import logging
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

# Import domain entities
try:
    from app.domain.entities.organisation import Organisation
    from app.domain.value_objects.organisation_id import OrganisationId
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
    from app.application.interfaces.repositories.organisation_repository import (
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
    from app.application.dto.organisation_dto import (
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

    # Missing Abstract Methods Implementation
    
    # Command Repository Methods
    async def save_batch(self, organisations: List[Organisation]) -> List[Organisation]:
        """Save multiple organisations in a batch operation."""
        try:
            saved_organisations = []
            for organisation in organisations:
                saved_org = await self.save(organisation)
                saved_organisations.append(saved_org)
            
            logger.info(f"Batch saved {len(saved_organisations)} organisations")
            return saved_organisations
            
        except Exception as e:
            logger.error(f"Error in batch save: {e}")
            raise

    # Query Repository Methods
    async def get_by_pan_number(self, pan_number: str) -> Optional[Organisation]:
        """Get organisation by PAN number."""
        try:
            collection = self._get_collection()
            document = await collection.find_one({
                "pan_number": pan_number,
                "is_active": True
            })
            
            if document:
                return self._document_to_entity(document)
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving organisation by PAN {pan_number}: {e}")
            return None

    async def get_by_status(self, status: str) -> List[Organisation]:
        """Get organisations by status."""
        try:
            collection = self._get_collection()
            cursor = collection.find({"status": status})
            documents = await cursor.to_list(length=None)
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting organisations by status {status}: {e}")
            return []

    async def get_by_type(self, organisation_type: str) -> List[Organisation]:
        """Get organisations by type."""
        try:
            collection = self._get_collection()
            cursor = collection.find({"type": organisation_type, "is_active": True})
            documents = await cursor.to_list(length=None)
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting organisations by type {organisation_type}: {e}")
            return []

    async def get_by_location(self, city: str = None, state: str = None, country: str = None) -> List[Organisation]:
        """Get organisations by location."""
        try:
            collection = self._get_collection()
            query = {"is_active": True}
            
            if city:
                query["city"] = city
            if state:
                query["state"] = state
            if country:
                query["country"] = country
            
            cursor = collection.find(query)
            documents = await cursor.to_list(length=None)
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting organisations by location: {e}")
            return []

    async def count_total(self) -> int:
        """Get total count of organisations."""
        try:
            collection = self._get_collection()
            return await collection.count_documents({})
        except Exception as e:
            logger.error(f"Error counting total organisations: {e}")
            return 0

    async def count_by_status(self, status: str) -> int:
        """Get count of organisations by status."""
        try:
            collection = self._get_collection()
            return await collection.count_documents({"status": status})
        except Exception as e:
            logger.error(f"Error counting organisations by status {status}: {e}")
            return 0

    async def exists_by_name(self, name: str, exclude_id: Optional[str] = None) -> bool:
        """Check if organisation exists by name."""
        try:
            collection = self._get_collection()
            query = {"name": name, "is_active": True}
            
            if exclude_id:
                query["organisation_id"] = {"$ne": exclude_id}
            
            count = await collection.count_documents(query)
            return count > 0
            
        except Exception as e:
            logger.error(f"Error checking name existence {name}: {e}")
            return False

    async def exists_by_hostname(self, hostname: str, exclude_id: Optional[str] = None) -> bool:
        """Check if organisation exists by hostname."""
        try:
            collection = self._get_collection()
            query = {"hostname": hostname, "is_active": True}
            
            if exclude_id:
                query["organisation_id"] = {"$ne": exclude_id}
            
            count = await collection.count_documents(query)
            return count > 0
            
        except Exception as e:
            logger.error(f"Error checking hostname existence {hostname}: {e}")
            return False

    async def exists_by_pan_number(self, pan_number: str, exclude_id: Optional[str] = None) -> bool:
        """Check if organisation exists by PAN number."""
        try:
            collection = self._get_collection()
            query = {"pan_number": pan_number, "is_active": True}
            
            if exclude_id:
                query["organisation_id"] = {"$ne": exclude_id}
            
            count = await collection.count_documents(query)
            return count > 0
            
        except Exception as e:
            logger.error(f"Error checking PAN existence {pan_number}: {e}")
            return False

    # Analytics Repository Methods
    async def get_statistics(self) -> Dict[str, Any]:
        """Get organisation statistics."""
        try:
            collection = self._get_collection()
            
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
                }
            ]
            
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=1)
            
            if results:
                return results[0]
            return {"total_organisations": 0, "active_organisations": 0, "inactive_organisations": 0}
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}

    async def get_analytics(self) -> Dict[str, Any]:
        """Get organisation analytics."""
        try:
            stats = await self.get_statistics()
            by_type = await self.get_organizations_by_type_count()
            by_location = await self.get_organizations_by_location_count()
            
            return {
                "statistics": stats,
                "type_distribution": by_type,
                "location_distribution": by_location,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {}

    async def get_organizations_by_type_count(self) -> Dict[str, int]:
        """Get count of organizations by type."""
        try:
            collection = self._get_collection()
            pipeline = [
                {"$match": {"is_active": True}},
                {"$group": {"_id": "$type", "count": {"$sum": 1}}}
            ]
            
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            return {doc["_id"] or "unknown": doc["count"] for doc in results}
            
        except Exception as e:
            logger.error(f"Error getting type count: {e}")
            return {}

    async def get_organizations_by_status_count(self) -> Dict[str, int]:
        """Get count of organizations by status."""
        try:
            collection = self._get_collection()
            pipeline = [
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]
            
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            return {doc["_id"] or "unknown": doc["count"] for doc in results}
            
        except Exception as e:
            logger.error(f"Error getting status count: {e}")
            return {}

    async def get_organizations_by_location_count(self) -> Dict[str, Dict[str, int]]:
        """Get count of organizations by location."""
        try:
            collection = self._get_collection()
            pipeline = [
                {"$match": {"is_active": True}},
                {
                    "$group": {
                        "_id": {
                            "country": "$country",
                            "state": "$state",
                            "city": "$city"
                        },
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            location_stats = {"by_country": {}, "by_state": {}, "by_city": {}}
            
            for doc in results:
                location = doc["_id"]
                count = doc["count"]
                
                country = location.get("country", "unknown")
                state = location.get("state", "unknown")
                city = location.get("city", "unknown")
                
                location_stats["by_country"][country] = location_stats["by_country"].get(country, 0) + count
                location_stats["by_state"][state] = location_stats["by_state"].get(state, 0) + count
                location_stats["by_city"][city] = location_stats["by_city"].get(city, 0) + count
            
            return location_stats
            
        except Exception as e:
            logger.error(f"Error getting location count: {e}")
            return {"by_country": {}, "by_state": {}, "by_city": {}}

    async def get_capacity_utilization_stats(self) -> Dict[str, Any]:
        """Get employee capacity utilization statistics."""
        try:
            collection = self._get_collection()
            pipeline = [
                {"$match": {"is_active": True}},
                {
                    "$group": {
                        "_id": None,
                        "total_capacity": {"$sum": "$employee_capacity"},
                        "total_current": {"$sum": "$current_employee_count"},
                        "avg_utilization": {
                            "$avg": {
                                "$cond": [
                                    {"$gt": ["$employee_capacity", 0]},
                                    {"$multiply": [{"$divide": ["$current_employee_count", "$employee_capacity"]}, 100]},
                                    0
                                ]
                            }
                        }
                    }
                }
            ]
            
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=1)
            
            if results:
                stats = results[0]
                return {
                    "total_capacity": stats.get("total_capacity", 0),
                    "total_current": stats.get("total_current", 0),
                    "average_utilization_percentage": round(stats.get("avg_utilization", 0), 2),
                    "capacity_remaining": max(0, stats.get("total_capacity", 0) - stats.get("total_current", 0))
                }
            
            return {"total_capacity": 0, "total_current": 0, "average_utilization_percentage": 0, "capacity_remaining": 0}
            
        except Exception as e:
            logger.error(f"Error getting capacity utilization stats: {e}")
            return {}

    async def get_growth_trends(self, months: int = 12) -> Dict[str, Any]:
        """Get organization growth trends."""
        try:
            collection = self._get_collection()
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)
            
            pipeline = [
                {
                    "$match": {
                        "created_at": {"$gte": start_date, "$lte": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "year": {"$year": "$created_at"},
                            "month": {"$month": "$created_at"}
                        },
                        "count": {"$sum": 1}
                    }
                },
                {"$sort": {"_id.year": 1, "_id.month": 1}}
            ]
            
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            monthly_growth = {}
            for doc in results:
                month_key = f"{doc['_id']['year']}-{doc['_id']['month']:02d}"
                monthly_growth[month_key] = doc["count"]
            
            return {
                "period_months": months,
                "monthly_growth": monthly_growth,
                "total_new_organizations": sum(monthly_growth.values()),
                "average_monthly_growth": sum(monthly_growth.values()) / months if months > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting growth trends: {e}")
            return {}

    async def get_top_organizations_by_capacity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top organizations by employee capacity."""
        try:
            collection = self._get_collection()
            cursor = collection.find(
                {"is_active": True, "employee_capacity": {"$gt": 0}},
                {"organisation_id": 1, "name": 1, "employee_capacity": 1, "current_employee_count": 1}
            ).sort("employee_capacity", -1).limit(limit)
            
            documents = await cursor.to_list(length=limit)
            
            result = []
            for doc in documents:
                capacity = doc.get("employee_capacity", 0)
                current = doc.get("current_employee_count", 0)
                utilization = (current / capacity * 100) if capacity > 0 else 0
                
                result.append({
                    "organisation_id": doc.get("organisation_id"),
                    "name": doc.get("name"),
                    "employee_capacity": capacity,
                    "current_employee_count": current,
                    "utilization_percentage": round(utilization, 2)
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting top organizations by capacity: {e}")
            return []

    async def get_organizations_created_in_period(self, start_date: datetime, end_date: datetime) -> List[Organisation]:
        """Get organizations created in a specific period."""
        try:
            collection = self._get_collection()
            cursor = collection.find({
                "created_at": {"$gte": start_date, "$lte": end_date},
                "is_active": True
            }).sort("created_at", -1)
            
            documents = await cursor.to_list(length=None)
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting organizations created in period: {e}")
            return []

    # Health Repository Methods
    async def perform_health_check(self, organization_id: str) -> Dict[str, Any]:
        """Perform health check for an organization."""
        try:
            org = await self.get_by_id(organization_id)
            if not org:
                return {"status": "not_found", "organization_id": organization_id}
            
            health_status = "healthy"
            issues = []
            
            # Check basic requirements
            if not getattr(org, 'name', None):
                issues.append("Missing organization name")
                health_status = "unhealthy"
            
            if not getattr(org, 'hostname', None):
                issues.append("Missing hostname")
                health_status = "unhealthy"
            
            # Check capacity utilization
            capacity = getattr(org, 'employee_capacity', 0)
            current = getattr(org, 'current_employee_count', 0)
            
            if capacity > 0:
                utilization = (current / capacity) * 100
                if utilization > 95:
                    issues.append("Over capacity (>95%)")
                    health_status = "warning" if health_status == "healthy" else health_status
                elif utilization < 10:
                    issues.append("Underutilized (<10%)")
                    health_status = "warning" if health_status == "healthy" else health_status
            
            return {
                "status": health_status,
                "organization_id": organization_id,
                "organization_name": getattr(org, 'name', ''),
                "issues": issues,
                "capacity_utilization": round((current / capacity * 100) if capacity > 0 else 0, 2),
                "checked_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error performing health check for {organization_id}: {e}")
            return {"status": "error", "organization_id": organization_id, "error": str(e)}

    async def get_unhealthy_organizations(self) -> List[Dict[str, Any]]:
        """Get list of unhealthy organizations."""
        try:
            all_orgs = await self.get_all_active()
            unhealthy_orgs = []
            
            for org in all_orgs:
                health_check = await self.perform_health_check(getattr(org, 'organisation_id', ''))
                if health_check.get("status") in ["unhealthy", "error"]:
                    unhealthy_orgs.append(health_check)
            
            return unhealthy_orgs
            
        except Exception as e:
            logger.error(f"Error getting unhealthy organizations: {e}")
            return []

    async def get_organizations_needing_attention(self) -> List[Dict[str, Any]]:
        """Get organizations that need attention."""
        try:
            all_orgs = await self.get_all_active()
            needs_attention = []
            
            for org in all_orgs:
                health_check = await self.perform_health_check(getattr(org, 'organisation_id', ''))
                if health_check.get("status") in ["unhealthy", "warning", "error"]:
                    needs_attention.append(health_check)
            
            return needs_attention
            
        except Exception as e:
            logger.error(f"Error getting organizations needing attention: {e}")
            return []

    # Bulk Operations Repository Methods
    async def bulk_update_status(self, organization_ids: List[str], status: str, updated_by: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """Bulk update organization status."""
        try:
            collection = self._get_collection()
            update_data = {
                "status": status,
                "updated_at": datetime.now(),
                "updated_by": updated_by
            }
            
            if reason:
                update_data["status_change_reason"] = reason
            
            result = await collection.update_many(
                {"organisation_id": {"$in": organization_ids}},
                {"$set": update_data}
            )
            
            return {
                "modified_count": result.modified_count,
                "matched_count": result.matched_count,
                "status": "success" if result.modified_count > 0 else "no_changes"
            }
            
        except Exception as e:
            logger.error(f"Error in bulk status update: {e}")
            return {"error": str(e), "status": "failed"}

    async def bulk_update_employee_strength(self, updates: Dict[str, int], updated_by: str) -> Dict[str, Any]:
        """Bulk update employee strength."""
        try:
            collection = self._get_collection()
            successful_updates = 0
            failed_updates = 0
            
            for org_id, employee_count in updates.items():
                try:
                    result = await collection.update_one(
                        {"organisation_id": org_id},
                        {
                            "$set": {
                                "current_employee_count": employee_count,
                                "updated_at": datetime.now(),
                                "updated_by": updated_by
                            }
                        }
                    )
                    
                    if result.modified_count > 0:
                        successful_updates += 1
                    else:
                        failed_updates += 1
                        
                except Exception:
                    failed_updates += 1
            
            return {
                "successful_updates": successful_updates,
                "failed_updates": failed_updates,
                "total_requested": len(updates),
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error in bulk employee strength update: {e}")
            return {"error": str(e), "status": "failed"}

    async def bulk_export(self, organization_ids: Optional[List[str]] = None, format: str = "csv") -> bytes:
        """Bulk export organization data."""
        try:
            import csv
            import io
            
            if organization_ids:
                query = {"organisation_id": {"$in": organization_ids}}
            else:
                query = {"is_active": True}
            
            collection = self._get_collection()
            cursor = collection.find(query, {
                "organisation_id": 1, "name": 1, "hostname": 1, "status": 1,
                "type": 1, "city": 1, "state": 1, "country": 1,
                "employee_capacity": 1, "current_employee_count": 1,
                "created_at": 1, "is_active": 1
            })
            
            documents = await cursor.to_list(length=None)
            
            # Convert to CSV
            output = io.StringIO()
            if documents:
                fieldnames = ["organisation_id", "name", "hostname", "status", "type", 
                             "city", "state", "country", "employee_capacity", 
                             "current_employee_count", "created_at", "is_active"]
                
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                
                for doc in documents:
                    doc.pop('_id', None)  # Remove MongoDB _id
                    writer.writerow({k: doc.get(k, '') for k in fieldnames})
            
            return output.getvalue().encode('utf-8')
            
        except Exception as e:
            logger.error(f"Error in bulk export: {e}")
            return b""

    async def bulk_import(self, data: bytes, format: str = "csv", created_by: str = "system") -> Dict[str, Any]:
        """Bulk import organization data."""
        try:
            import csv
            import io
            
            # Parse CSV data
            content = data.decode('utf-8')
            reader = csv.DictReader(io.StringIO(content))
            
            orgs_data = list(reader)
            valid_orgs = []
            errors = []
            
            for i, org_data in enumerate(orgs_data):
                try:
                    # Basic validation
                    if not org_data.get('organisation_id'):
                        errors.append(f"Row {i+1}: Missing organisation_id")
                        continue
                    
                    if not org_data.get('name'):
                        errors.append(f"Row {i+1}: Missing name")
                        continue
                    
                    if not org_data.get('hostname'):
                        errors.append(f"Row {i+1}: Missing hostname")
                        continue
                    
                    valid_orgs.append(org_data)
                    
                except Exception as e:
                    errors.append(f"Row {i+1}: {str(e)}")
            
            # Import valid organizations
            imported_count = 0
            if valid_orgs:
                collection = self._get_collection()
                
                for org_data in valid_orgs:
                    try:
                        # Set defaults
                        org_data['created_by'] = created_by
                        org_data['created_at'] = datetime.now()
                        org_data['updated_at'] = datetime.now()
                        org_data['is_active'] = org_data.get('is_active', 'true').lower() == 'true'
                        
                        # Convert string numbers
                        if 'employee_capacity' in org_data:
                            org_data['employee_capacity'] = int(org_data['employee_capacity'] or 0)
                        if 'current_employee_count' in org_data:
                            org_data['current_employee_count'] = int(org_data['current_employee_count'] or 0)
                        
                        # Upsert operation
                        await collection.replace_one(
                            {"organisation_id": org_data['organisation_id']},
                            org_data,
                            upsert=True
                        )
                        imported_count += 1
                        
                    except Exception as e:
                        errors.append(f"Import error for {org_data.get('organisation_id', 'unknown')}: {str(e)}")
            
            return {
                "total_rows": len(orgs_data),
                "valid_rows": len(valid_orgs),
                "imported_count": imported_count,
                "errors": errors,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error in bulk import: {e}")
            return {"error": str(e), "status": "failed"}

    # Factory Methods (placeholder implementations)
    def create_command_repository(self):
        """Create command repository instance"""
        return self

    def create_query_repository(self):
        """Create query repository instance"""
        return self

    def create_analytics_repository(self):
        """Create analytics repository instance"""
        return self

    def create_health_repository(self):
        """Create health repository instance"""
        return self

    def create_bulk_operations_repository(self):
        """Create bulk operations repository instance"""
        return self 