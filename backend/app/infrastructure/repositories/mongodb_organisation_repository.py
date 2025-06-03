"""
MongoDB Organisation Repository Implementation
Unified repository following SOLID principles and DDD patterns for organisation data access
Merges functionality from both mongodb_organisation_repository.py and solid_organisation_repository.py
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
from pymongo.collection import Collection

from app.domain.entities.organisation import Organisation
from app.domain.value_objects.organisation_id import OrganisationId
from app.domain.value_objects.organisation_details import (
    OrganisationType, ContactInformation, 
    Address, TaxInformation, OrganisationStatus
)
from app.application.interfaces.repositories.organisation_repository import (
    OrganisationCommandRepository, OrganisationQueryRepository, OrganisationAnalyticsRepository,
    OrganisationHealthRepository, OrganisationBulkOperationsRepository, OrganisationRepository
)
from app.application.dto.organisation_dto import (
    OrganisationSearchFiltersDTO, OrganisationStatisticsDTO, OrganisationAnalyticsDTO,
    OrganisationHealthCheckDTO, BulkOrganisationUpdateDTO, BulkOrganisationUpdateResultDTO
)
from app.infrastructure.database.database_connector import DatabaseConnector
from app.config.mongodb_config import get_mongodb_connection_string, get_mongodb_client_options

logger = logging.getLogger(__name__)


class MongoDBOrganisationRepository(OrganisationRepository):
    """
    MongoDB implementation of organisation repository following DDD patterns.
    
    Implements all organisation repository interfaces in a single class for simplicity
    while maintaining SOLID principles through interface segregation.
    
    Unified implementation that merges features from:
    - mongodb_organisation_repository.py (comprehensive DDD implementation)
    - solid_organisation_repository.py (legacy compatibility methods)
    """
    
    def __init__(self, database_connector: DatabaseConnector):
        """
        Initialize repository with database connector.
        
        Args:
            database_connector: Database connection abstraction
        """
        self.db_connector = database_connector
        self._collection_name = "organisation"
        
        # Connection configuration (will be set by dependency container)
        self._connection_string = None
        self._client_options = None
        
    def set_connection_config(self, connection_string: str, client_options: Dict[str, Any]):
        """
        Set MongoDB connection configuration.
        
        Args:
            connection_string: MongoDB connection string
            client_options: MongoDB client options
        """
        self._connection_string = connection_string
        self._client_options = client_options
        
    async def _get_collection(self, organisation_id: Optional[str] = None):
        """
        Get organisations collection for specific organisation or global.
        
        Ensures database connection is established in the correct event loop.
        Uses global database for organisation data.
        """
        db_name = "pms_global_database"
        
        # Ensure database is connected in the current event loop
        if not self.db_connector.is_connected:
            logger.debug("Database not connected, establishing connection...")
            
            try:
                # Use stored connection configuration or fallback to config functions
                if self._connection_string and self._client_options:
                    logger.debug("Using stored connection parameters from repository configuration")
                    connection_string = self._connection_string
                    options = self._client_options
                else:
                    # Fallback to config functions if connection config not set
                    logger.debug("Loading connection parameters from mongodb_config")
                    connection_string = get_mongodb_connection_string()
                    options = get_mongodb_client_options()
                
                await self.db_connector.connect(connection_string, **options)
                logger.info("MongoDB connection established successfully in current event loop")
                
            except Exception as e:
                logger.error(f"Failed to establish database connection: {e}")
                raise RuntimeError(f"Database connection failed: {e}")
        
        # Verify connection and get collection
        try:
            db = self.db_connector.get_database(db_name)
            collection = db[self._collection_name]
            logger.debug(f"Successfully retrieved collection: {self._collection_name} from database: {db_name}")
            return collection
            
        except Exception as e:
            logger.error(f"Failed to get collection {self._collection_name}: {e}")
            # Reset connection state to force reconnection on next call
            if hasattr(self.db_connector, '_client'):
                self.db_connector._client = None
            raise RuntimeError(f"Collection access failed: {e}")
    
    async def _ensure_indexes(self) -> None:
        """Ensure necessary indexes for optimal query performance."""
        try:
            collection = await self._get_collection()
            
            # Unique indexes
            await collection.create_index([("organisation_id", ASCENDING)], unique=True)
            await collection.create_index([("name", ASCENDING)], unique=True)
            await collection.create_index([("hostname", ASCENDING)], unique=True, sparse=True)
            await collection.create_index([("tax_information.pan_number", ASCENDING)], unique=True, sparse=True)
            
            # Query optimization indexes
            await collection.create_index([("status", ASCENDING)])
            await collection.create_index([("organisation_type", ASCENDING)])
            await collection.create_index([("created_at", DESCENDING)])
            await collection.create_index([("updated_at", DESCENDING)])
            await collection.create_index([("is_deleted", ASCENDING)])
            
            # Compound indexes for common queries
            await collection.create_index([
                ("status", ASCENDING),
                ("organisation_type", ASCENDING),
                ("created_at", DESCENDING)
            ])
            await collection.create_index([
                ("is_deleted", ASCENDING),
                ("status", ASCENDING)
            ])
            
            logger.info("Organisation indexes ensured")
            
        except Exception as e:
            logger.error(f"Error ensuring organisation indexes: {e}")
    
    def _organisation_to_document(self, organisation: Organisation) -> Dict[str, Any]:
        """Convert domain entity to database document."""
        
        # Safe value extraction for enums - handle both enum objects and strings
        def safe_enum_value(field_value):
            if hasattr(field_value, 'value'):
                return field_value.value
            return str(field_value) if field_value is not None else None
        
        # Safe extraction for complex nested objects
        def safe_get_attr(obj, attr_path, default=None):
            """Safely get nested attributes like 'contact_info.email'"""
            try:
                attrs = attr_path.split('.')
                value = obj
                for attr in attrs:
                    value = getattr(value, attr, None)
                    if value is None:
                        return default
                return value
            except (AttributeError, TypeError):
                return default
        
        # Convert date objects to datetime for MongoDB compatibility
        def safe_date_conversion(date_value):
            """Convert date objects to datetime objects for MongoDB"""
            if date_value is None:
                return None
            if isinstance(date_value, datetime):
                return date_value
            elif hasattr(date_value, 'year') and hasattr(date_value, 'month') and hasattr(date_value, 'day'):
                # It's a date object, convert to datetime
                from datetime import datetime as dt
                return dt.combine(date_value, dt.min.time())
            else:
                return date_value
        
        # Handle value object conversion to dict
        def value_object_to_dict(value_obj):
            """Convert value object to dictionary"""
            if value_obj is None:
                return {}
            if hasattr(value_obj, 'to_dict'):
                return value_obj.to_dict()
            elif hasattr(value_obj, 'model_dump'):
                return value_obj.model_dump()
            elif hasattr(value_obj, 'dict'):
                return value_obj.dict()
            else:
                # Fallback: convert object attributes to dict
                return {k: v for k, v in value_obj.__dict__.items() if not k.startswith('_')}
        
        return {
            "organisation_id": str(organisation.organisation_id),
            "name": getattr(organisation, 'name', ''),
            "description": getattr(organisation, 'description', ''),
            "organisation_type": safe_enum_value(getattr(organisation, 'organisation_type')),
            "status": safe_enum_value(getattr(organisation, 'status')),
            "hostname": getattr(organisation, 'hostname', ''),
            "contact_information": value_object_to_dict(getattr(organisation, 'contact_info', None)),
            "address": value_object_to_dict(getattr(organisation, 'address', None)),
            "tax_information": value_object_to_dict(getattr(organisation, 'tax_info', None)),
            "employee_strength": getattr(organisation, 'employee_strength', 0),
            "used_employee_strength": getattr(organisation, 'used_employee_strength', 0),
            "is_active": organisation.is_active(),
            "is_deleted": getattr(organisation, 'is_deleted', False),
            "created_at": safe_date_conversion(getattr(organisation, 'created_at', None)),
            "updated_at": safe_date_conversion(getattr(organisation, 'updated_at', None)),
            "deleted_at": safe_date_conversion(getattr(organisation, 'deleted_at', None)),
            "created_by": getattr(organisation, 'created_by', None),
            "updated_by": getattr(organisation, 'updated_by', None),
            "version": getattr(organisation, 'version', 1)
        }
    
    def _document_to_organisation(self, document: Dict[str, Any]) -> Organisation:
        """Convert database document to domain entity."""
        
        try:
            # Use the actual Organisation entity instead of SimpleOrganisation
            return Organisation.from_existing_data(
                organisation_id=document["organisation_id"],
                name=document.get("name", ""),
                description=document.get("description", ""),
                hostname=document.get("hostname", ""),
                organisation_type=document.get("organisation_type", "private_limited"),
                status=document.get("status", "active"),
                contact_info=document.get("contact_information", {}),
                address=document.get("address", {}),
                tax_info=document.get("tax_information", {}),
                employee_strength=document.get("employee_strength", 0),
                used_employee_strength=document.get("used_employee_strength", 0),
                logo_path=document.get("logo_path"),
                created_at=document.get("created_at"),
                updated_at=document.get("updated_at"),
                created_by=document.get("created_by"),
                updated_by=document.get("updated_by")
            )
            
        except Exception as e:
            logger.error(f"Error creating Organisation entity from document: {e}")
            raise ValueError(f"Failed to reconstruct Organisation entity: {e}")
    
    async def _publish_events(self, events: List[Any]) -> None:
        """Publish domain events."""
        # Implementation would depend on event publisher
        for event in events:
            logger.info(f"Publishing event: {type(event).__name__}")

    # ==================== COMMAND REPOSITORY IMPLEMENTATION ====================
    
    async def save(self, organisation: Organisation) -> Organisation:
        """Save an organisation (create or update)."""
        try:
            await self._ensure_indexes()
            collection = await self._get_collection()
            document = self._organisation_to_document(organisation)
            
            # Set timestamps
            if not document.get('created_at'):
                document['created_at'] = datetime.utcnow()
            document['updated_at'] = datetime.utcnow()
            
            # Use upsert to handle both create and update
            result = await collection.replace_one(
                {"organisation_id": str(organisation.organisation_id)},
                document,
                upsert=True
            )
            
            # Publish domain events
            if hasattr(organisation, 'get_domain_events'):
                await self._publish_events(organisation.get_domain_events())
                organisation.clear_domain_events()
            
            logger.info(f"Organisation saved: {organisation.organisation_id}")
            return organisation
            
        except DuplicateKeyError as e:
            logger.error(f"Duplicate key error saving organisation {organisation.organisation_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error saving organisation {organisation.organisation_id}: {e}")
            raise
    
    async def save_batch(self, organisations: List[Organisation]) -> List[Organisation]:
        """Save multiple organisations in a batch operation."""
        try:
            await self._ensure_indexes()
            collection = await self._get_collection()
            
            # Prepare bulk operations
            operations = []
            for organisation in organisations:
                document = self._organisation_to_document(organisation)
                if not document.get('created_at'):
                    document['created_at'] = datetime.utcnow()
                document['updated_at'] = datetime.utcnow()
                
                operations.append({
                    "replaceOne": {
                        "filter": {"organisation_id": str(organisation.organisation_id)},
                        "replacement": document,
                        "upsert": True
                    }
                })
            
            # Execute bulk write
            if operations:
                await collection.bulk_write(operations)
                
                # Publish events for all organisations
                for organisation in organisations:
                    if hasattr(organisation, 'get_domain_events'):
                        await self._publish_events(organisation.get_domain_events())
                        organisation.clear_domain_events()
            
            logger.info(f"Batch saved {len(organisations)} organisations")
            return organisations
            
        except Exception as e:
            logger.error(f"Error in batch save: {e}")
            raise
    
    async def update(self, organisation: Organisation) -> Organisation:
        """Update an existing organisation."""
        try:
            collection = await self._get_collection()
            document = self._organisation_to_document(organisation)
            document["updated_at"] = datetime.utcnow()
            
            result = await collection.replace_one(
                {"organisation_id": str(organisation.organisation_id)},
                document
            )
            
            if result.modified_count > 0 or result.matched_count > 0:
                # Publish domain events
                if hasattr(organisation, 'get_domain_events'):
                    await self._publish_events(organisation.get_domain_events())
                    organisation.clear_domain_events()
                
                logger.debug(f"Updated organisation: {organisation.organisation_id}")
                return organisation
            else:
                raise Exception(f"Organisation {organisation.organisation_id} not found for update")
                
        except Exception as e:
            logger.error(f"Error updating organisation {organisation.organisation_id}: {e}")
            raise
    
    # ==================== QUERY REPOSITORY IMPLEMENTATION ====================

    async def get_by_id(self, organisation_id: OrganisationId) -> Optional[Organisation]:
        """Get organisation by ID."""
        try:
            collection = await self._get_collection()
            document = await collection.find_one({
                "organisation_id": str(organisation_id),
                "is_deleted": {"$ne": True}
            })
            
            if document:
                return self._document_to_organisation(document)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting organisation by ID {organisation_id}: {e}")
            raise
    
    async def get_by_name(self, name: str) -> Optional[Organisation]:
        """Get organisation by name."""
        try:
            collection = await self._get_collection()
            document = await collection.find_one({
                "name": name,
                "is_deleted": {"$ne": True}
            })
            
            if document:
                return self._document_to_organisation(document)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting organisation by name {name}: {e}")
            raise
    
    async def get_by_hostname(self, hostname: str) -> Optional[Organisation]:
        """Get organisation by hostname."""
        try:
            collection = await self._get_collection()
            document = await collection.find_one({
                "hostname": hostname,
                "is_deleted": {"$ne": True}
            })
            
            if document:
                return self._document_to_organisation(document)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting organisation by hostname {hostname}: {e}")
            raise
    
    async def get_by_pan_number(self, pan_number: str) -> Optional[Organisation]:
        """Get organisation by PAN number."""
        try:
            collection = await self._get_collection()
            document = await collection.find_one({
                "tax_information.pan_number": pan_number,
                "is_deleted": {"$ne": True}
            })
            
            if document:
                return self._document_to_organisation(document)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting organisation by PAN {pan_number}: {e}")
            raise
    
    async def search(self, filters: OrganisationSearchFiltersDTO) -> List[Organisation]:
        """Search organisations with filters."""
        try:
            collection = await self._get_collection()
            query = {"is_deleted": {"$ne": True}}
            
            # Apply filters
            if filters.name:
                query["name"] = {"$regex": filters.name, "$options": "i"}
            
            if filters.organisation_type:
                query["organisation_type"] = filters.organisation_type
            
            if filters.status:
                query["status"] = filters.status
            
            if hasattr(filters, 'city') and filters.city:
                query["address.city"] = {"$regex": filters.city, "$options": "i"}
            
            if hasattr(filters, 'state') and filters.state:
                query["address.state"] = {"$regex": filters.state, "$options": "i"}
            
            if hasattr(filters, 'country') and filters.country:
                query["address.country"] = {"$regex": filters.country, "$options": "i"}
            
            if hasattr(filters, 'created_after') and filters.created_after:
                query["created_at"] = {"$gte": filters.created_after}
            
            if hasattr(filters, 'created_before') and filters.created_before:
                if "created_at" in query:
                    query["created_at"]["$lte"] = filters.created_before
                else:
                    query["created_at"] = {"$lte": filters.created_before}
            
            # Build sort criteria
            sort_criteria = []
            if hasattr(filters, 'sort_by') and filters.sort_by:
                direction = DESCENDING if getattr(filters, 'sort_order', 'asc') == "desc" else ASCENDING
                sort_criteria.append((filters.sort_by, direction))
            else:
                sort_criteria.append(("created_at", DESCENDING))
            
            # Handle pagination
            page = getattr(filters, 'page', 1)
            page_size = getattr(filters, 'page_size', 20)
            skip = (page - 1) * page_size
            
            # Execute query with pagination
            cursor = collection.find(query).sort(sort_criteria)
            
            if skip > 0:
                cursor = cursor.skip(skip)
            
            if page_size > 0:
                cursor = cursor.limit(page_size)
            
            documents = await cursor.to_list(length=None)
            
            organisations = []
            for doc in documents:
                org = self._document_to_organisation(doc)
                if org:
                    organisations.append(org)
            
            return organisations
            
        except Exception as e:
            logger.error(f"Error searching organisations: {e}")
            raise
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        include_inactive: bool = False,
        include_deleted: bool = False
    ) -> List[Organisation]:
        """Get all organisations with pagination."""
        try:
            collection = await self._get_collection()
            
            # Build filter
            filter_query = {}
            if not include_deleted:
                filter_query["is_deleted"] = {"$ne": True}
            if not include_inactive:
                filter_query["status"] = "active"
            
            # Execute query
            cursor = collection.find(filter_query).skip(skip).limit(limit).sort("created_at", DESCENDING)
            documents = await cursor.to_list(length=limit)
            
            organisations = [self._document_to_organisation(doc) for doc in documents]
            logger.info(f"Retrieved {len(organisations)} organisations")
            return organisations
            
        except Exception as e:
            logger.error(f"Error getting all organisations: {e}")
            raise
    
    async def get_by_type(self, organisation_type: OrganisationType) -> List[Organisation]:
        """Get organisations by type."""
        try:
            collection = await self._get_collection()
            cursor = collection.find({
                "organisation_type": organisation_type.value,
                "is_deleted": {"$ne": True}
            }).sort("created_at", DESCENDING)
            
            documents = await cursor.to_list(length=None)
            return [self._document_to_organisation(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting organisations by type {organisation_type}: {e}")
            raise
    
    async def get_by_location(self, city: str = None, state: str = None, country: str = None) -> List[Organisation]:
        """Get organisations by location."""
        try:
            collection = await self._get_collection()
            query = {"is_deleted": {"$ne": True}}
            
            if city:
                query["address.city"] = {"$regex": city, "$options": "i"}
            if state:
                query["address.state"] = {"$regex": state, "$options": "i"}
            if country:
                query["address.country"] = {"$regex": country, "$options": "i"}
            
            cursor = collection.find(query).sort("created_at", DESCENDING)
            documents = await cursor.to_list(length=None)
            
            return [self._document_to_organisation(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting organisations by location: {e}")
            raise
    
    # Count methods
    async def count_total(self, include_deleted: bool = False) -> int:
        """Count total organisations."""
        try:
            collection = await self._get_collection()
            filter_query = {}
            if not include_deleted:
                filter_query["is_deleted"] = {"$ne": True}
            
            return await collection.count_documents(filter_query)
            
        except Exception as e:
            logger.error(f"Error counting total organisations: {e}")
            raise
    

    async def count_by_type(self, organisation_type: OrganisationType) -> int:
        """Count organisations by type."""
        try:
            collection = await self._get_collection()
            return await collection.count_documents({
                "organisation_type": organisation_type.value,
                "is_deleted": {"$ne": True}
            })
        except Exception as e:
            logger.error(f"Error counting organisations by type {organisation_type}: {e}")
            raise
    
    # Existence checks
    async def exists_by_name(self, name: str, exclude_id: Optional[OrganisationId] = None) -> bool:
        """Check if organisation exists by name."""
        try:
            collection = await self._get_collection()
            query = {
                "name": name,
                "is_deleted": {"$ne": True}
            }
            if exclude_id:
                query["organisation_id"] = {"$ne": str(exclude_id)}
            
            count = await collection.count_documents(query)
            return count > 0
        except Exception as e:
            logger.error(f"Error checking organisation existence by name {name}: {e}")
            raise
    
    async def exists_by_hostname(self, hostname: str, exclude_id: Optional[OrganisationId] = None) -> bool:
        """Check if organisation exists by hostname."""
        try:
            collection = await self._get_collection()
            query = {
                "hostname": hostname,
                "is_deleted": {"$ne": True}
            }
            if exclude_id:
                query["organisation_id"] = {"$ne": str(exclude_id)}
            
            count = await collection.count_documents(query)
            return count > 0
        except Exception as e:
            logger.error(f"Error checking organisation existence by hostname {hostname}: {e}")
            raise
    
    async def exists_by_pan_number(self, pan_number: str, exclude_id: Optional[OrganisationId] = None) -> bool:
        """Check if organisation exists by PAN number."""
        try:
            collection = await self._get_collection()
            query = {
                "tax_information.pan_number": pan_number,
                "is_deleted": {"$ne": True}
            }
            if exclude_id:
                query["organisation_id"] = {"$ne": str(exclude_id)}
            
            count = await collection.count_documents(query)
            return count > 0
        except Exception as e:
            logger.error(f"Error checking organisation existence by PAN {pan_number}: {e}")
            raise

    # ==================== ANALYTICS REPOSITORY IMPLEMENTATION ====================
    
    async def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> OrganisationStatisticsDTO:
        """Get comprehensive organisation statistics."""
        try:
            collection = await self._get_collection()
            
            # Build date filter
            date_filter = {}
            if start_date or end_date:
                date_query = {}
                if start_date:
                    date_query["$gte"] = start_date
                if end_date:
                    date_query["$lte"] = end_date
                date_filter["created_at"] = date_query
            
            base_query = {"is_deleted": {"$ne": True}}
            if date_filter:
                base_query.update(date_filter)
            
            # Aggregate statistics
            pipeline = [
                {"$match": base_query},
                {
                    "$group": {
                        "_id": None,
                        "total_organisations": {"$sum": 1},
                        "active_organisations": {
                            "$sum": {"$cond": [{"$eq": ["$status", "active"]}, 1, 0]}
                        },
                        "inactive_organisations": {
                            "$sum": {"$cond": [{"$eq": ["$status", "inactive"]}, 1, 0]}
                        },
                        "suspended_organisations": {
                            "$sum": {"$cond": [{"$eq": ["$status", "suspended"]}, 1, 0]}
                        },
                        "total_employee_capacity": {"$sum": "$employee_strength"},
                        "total_employees_used": {"$sum": "$used_employee_strength"},
                        "avg_employee_strength": {"$avg": "$employee_strength"}
                    }
                }
            ]
            
            result = await collection.aggregate(pipeline).to_list(length=1)
            stats = result[0] if result else {}
            
            # Get type distribution
            type_pipeline = [
                {"$match": base_query},
                {"$group": {"_id": "$organisation_type", "count": {"$sum": 1}}}
            ]
            type_results = await collection.aggregate(type_pipeline).to_list(length=None)
            type_distribution = {item["_id"]: item["count"] for item in type_results}
            
            return OrganisationStatisticsDTO(
                total_organisations=stats.get("total_organisations", 0),
                active_organisations=stats.get("active_organisations", 0),
                inactive_organisations=stats.get("inactive_organisations", 0),
                suspended_organisations=stats.get("suspended_organisations", 0),
                organisations_by_type=type_distribution,
                total_employee_capacity=stats.get("total_employee_capacity", 0),
                total_employees_used=stats.get("total_employees_used", 0),
                average_employee_strength=stats.get("avg_employee_strength", 0.0),
                capacity_utilization_percentage=round(
                    (stats.get("total_employees_used", 0) / max(stats.get("total_employee_capacity", 1), 1)) * 100, 2
                )
            )
            
        except Exception as e:
            logger.error(f"Error getting organisation statistics: {e}")
            raise
    
    async def get_analytics(self) -> OrganisationAnalyticsDTO:
        """Get comprehensive organisation analytics."""
        try:
            # Get basic statistics
            stats = await self.get_statistics()
            
            # Get additional analytics data
            growth_trends = await self.get_growth_trends()
            capacity_stats = await self.get_capacity_utilization_stats()
            location_distribution = await self.get_organisations_by_location_count()
            
            return OrganisationAnalyticsDTO(
                total_organisations=stats.total_organisations,
                active_organisations=stats.active_organisations,
                inactive_organisations=stats.inactive_organisations,
                organisations_by_type=stats.organisations_by_type,
                organisations_by_location=location_distribution,
                capacity_utilization=capacity_stats,
                growth_trends=growth_trends,
                average_employee_strength=stats.average_employee_strength,
                capacity_utilization_percentage=stats.capacity_utilization_percentage
            )
            
        except Exception as e:
            logger.error(f"Error getting organisation analytics: {e}")
            raise
    
    async def get_organisations_by_type_count(self) -> Dict[str, int]:
        """Get count of organisations by type."""
        try:
            collection = await self._get_collection()
            pipeline = [
                {"$match": {"is_deleted": {"$ne": True}}},
                {"$group": {"_id": "$organisation_type", "count": {"$sum": 1}}}
            ]
            
            results = await collection.aggregate(pipeline).to_list(length=None)
            return {item["_id"]: item["count"] for item in results}
            
        except Exception as e:
            logger.error(f"Error getting organisations by type count: {e}")
            return {}
    
    async def get_organisations_by_status_count(self) -> Dict[str, int]:
        """Get count of organisations by status."""
        try:
            collection = await self._get_collection()
            pipeline = [
                {"$match": {"is_deleted": {"$ne": True}}},
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]
            
            results = await collection.aggregate(pipeline).to_list(length=None)
            return {item["_id"]: item["count"] for item in results}
            
        except Exception as e:
            logger.error(f"Error getting organisations by status count: {e}")
            return {}
    
    async def get_organisations_by_location_count(self) -> Dict[str, Dict[str, int]]:
        """Get count of organisations by location (country, state, city)."""
        try:
            collection = await self._get_collection()
            
            # Count by country
            country_pipeline = [
                {"$match": {"is_deleted": {"$ne": True}}},
                {"$group": {"_id": "$address.country", "count": {"$sum": 1}}}
            ]
            country_results = await collection.aggregate(country_pipeline).to_list(length=None)
            
            # Count by state
            state_pipeline = [
                {"$match": {"is_deleted": {"$ne": True}}},
                {"$group": {"_id": "$address.state", "count": {"$sum": 1}}}
            ]
            state_results = await collection.aggregate(state_pipeline).to_list(length=None)
            
            # Count by city
            city_pipeline = [
                {"$match": {"is_deleted": {"$ne": True}}},
                {"$group": {"_id": "$address.city", "count": {"$sum": 1}}}
            ]
            city_results = await collection.aggregate(city_pipeline).to_list(length=None)
            
            return {
                "by_country": {item["_id"]: item["count"] for item in country_results if item["_id"]},
                "by_state": {item["_id"]: item["count"] for item in state_results if item["_id"]},
                "by_city": {item["_id"]: item["count"] for item in city_results if item["_id"]}
            }
            
        except Exception as e:
            logger.error(f"Error getting organisations by location count: {e}")
            return {"by_country": {}, "by_state": {}, "by_city": {}}

    async def get_capacity_utilization_stats(self) -> Dict[str, Any]:
        """Get capacity utilization statistics."""
        try:
            collection = await self._get_collection()
            pipeline = [
                {"$match": {"is_deleted": {"$ne": True}}},
                {
                    "$group": {
                        "_id": None,
                        "total_capacity": {"$sum": "$employee_strength"},
                        "total_used": {"$sum": "$used_employee_strength"},
                        "avg_capacity": {"$avg": "$employee_strength"},
                        "avg_used": {"$avg": "$used_employee_strength"},
                        "max_capacity": {"$max": "$employee_strength"},
                        "min_capacity": {"$min": "$employee_strength"},
                        "organisations_count": {"$sum": 1}
                    }
                }
            ]
            
            result = await collection.aggregate(pipeline).to_list(length=1)
            
            if result:
                stats = result[0]
                total_capacity = stats.get("total_capacity", 0)
                total_used = stats.get("total_used", 0)
                
                return {
                    "total_capacity": total_capacity,
                    "total_used": total_used,
                    "total_available": total_capacity - total_used,
                    "utilization_percentage": round((total_used / max(total_capacity, 1)) * 100, 2),
                    "average_capacity_per_org": round(stats.get("avg_capacity", 0), 2),
                    "average_used_per_org": round(stats.get("avg_used", 0), 2),
                    "max_capacity_org": stats.get("max_capacity", 0),
                    "min_capacity_org": stats.get("min_capacity", 0),
                    "total_organisations": stats.get("organisations_count", 0)
                }
            
            return {
                "total_capacity": 0,
                "total_used": 0,
                "total_available": 0,
                "utilization_percentage": 0.0,
                "average_capacity_per_org": 0.0,
                "average_used_per_org": 0.0,
                "max_capacity_org": 0,
                "min_capacity_org": 0,
                "total_organisations": 0
            }
            
        except Exception as e:
            logger.error(f"Error getting capacity utilization stats: {e}")
            return {}

    async def get_growth_trends(self, months: int = 12) -> Dict[str, Any]:
        """Get organisation growth trends over specified months."""
        try:
            collection = await self._get_collection()
            
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=months * 30)  # Approximation
            
            pipeline = [
                {
                    "$match": {
                        "is_deleted": {"$ne": True},
                        "created_at": {"$gte": start_date, "$lte": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "year": {"$year": "$created_at"},
                            "month": {"$month": "$created_at"}
                        },
                        "count": {"$sum": 1},
                        "total_capacity": {"$sum": "$employee_strength"}
                    }
                },
                {"$sort": {"_id.year": 1, "_id.month": 1}}
            ]
            
            results = await collection.aggregate(pipeline).to_list(length=None)
            
            monthly_data = []
            total_growth = 0
            
            for result in results:
                month_key = f"{result['_id']['year']}-{result['_id']['month']:02d}"
                count = result["count"]
                capacity = result["total_capacity"]
                
                monthly_data.append({
                    "period": month_key,
                    "new_organisations": count,
                    "total_capacity_added": capacity
                })
                
                total_growth += count
            
            # Calculate growth rate
            if len(monthly_data) > 1:
                first_month = monthly_data[0]["new_organisations"]
                last_month = monthly_data[-1]["new_organisations"]
                growth_rate = ((last_month - first_month) / max(first_month, 1)) * 100
            else:
                growth_rate = 0.0
            
            return {
                "period_months": months,
                "monthly_data": monthly_data,
                "total_new_organisations": total_growth,
                "average_monthly_growth": round(total_growth / max(months, 1), 2),
                "growth_rate_percentage": round(growth_rate, 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting growth trends: {e}")
            return {}

    async def get_top_organisations_by_capacity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top organisations by employee capacity."""
        try:
            collection = await self._get_collection()
            pipeline = [
                {"$match": {"is_deleted": {"$ne": True}}},
                {
                    "$project": {
                        "name": 1,
                        "organisation_type": 1,
                        "employee_strength": 1,
                        "used_employee_strength": 1,
                        "utilization_rate": {
                            "$cond": [
                                {"$gt": ["$employee_strength", 0]},
                                {"$multiply": [
                                    {"$divide": ["$used_employee_strength", "$employee_strength"]},
                                    100
                                ]},
                                0
                            ]
                        }
                    }
                },
                {"$sort": {"employee_strength": -1}},
                {"$limit": limit}
            ]
            
            results = await collection.aggregate(pipeline).to_list(length=limit)
            
            top_organisations = []
            for i, result in enumerate(results, 1):
                top_organisations.append({
                    "rank": i,
                    "name": result.get("name", "Unknown"),
                    "organisation_type": result.get("organisation_type", "Unknown"),
                    "employee_capacity": result.get("employee_strength", 0),
                    "employees_used": result.get("used_employee_strength", 0),
                    "available_capacity": result.get("employee_strength", 0) - result.get("used_employee_strength", 0),
                    "utilization_rate": round(result.get("utilization_rate", 0), 2)
                })
            
            return top_organisations
            
        except Exception as e:
            logger.error(f"Error getting top organisations by capacity: {e}")
            return []

    async def get_organisations_created_in_period(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Organisation]:
        """Get organisations created within specified period."""
        try:
            collection = await self._get_collection()
            query = {
                "is_deleted": {"$ne": True},
                "created_at": {"$gte": start_date, "$lte": end_date}
            }
            
            cursor = collection.find(query).sort("created_at", DESCENDING)
            documents = await cursor.to_list(length=None)
            
            organisations = []
            for doc in documents:
                org = self._document_to_organisation(doc)
                if org:
                    organisations.append(org)
            
            return organisations
            
        except Exception as e:
            logger.error(f"Error getting organisations created in period: {e}")
            return []

    # ==================== HEALTH REPOSITORY IMPLEMENTATION ====================
    
    async def perform_health_check(self, organisation_id: OrganisationId) -> OrganisationHealthCheckDTO:
        """Perform health check for specific organisation."""
        try:
            organisation = await self.get_by_id(organisation_id)
            
            if not organisation:
                return OrganisationHealthCheckDTO(
                    organisation_id=str(organisation_id),
                    is_healthy=False,
                    health_score=0,
                    issues=["Organisation not found"],
                    recommendations=["Verify organisation exists"]
                )
            
            # Perform various health checks
            issues = []
            recommendations = []
            health_score = 100
            
            # Check basic data completeness
            if not organisation.name:
                issues.append("Missing organisation name")
                recommendations.append("Set organisation name")
                health_score -= 20
            
            if not organisation.description:
                issues.append("Missing organisation description")
                recommendations.append("Add organisation description")
                health_score -= 5
            
            # Check contact information
            if not organisation.contact_info.email:
                issues.append("Missing contact email")
                recommendations.append("Add contact email address")
                health_score -= 15
            
            if not organisation.contact_info.phone:
                issues.append("Missing contact phone")
                recommendations.append("Add contact phone number")
                health_score -= 10
            
            # Check address completeness
            if not organisation.address.city or not organisation.address.state:
                issues.append("Incomplete address information")
                recommendations.append("Complete address details")
                health_score -= 10
            
            # Check tax information
            if not organisation.tax_info.pan_number:
                issues.append("Missing PAN number")
                recommendations.append("Add PAN number for tax compliance")
                health_score -= 15
            
            # Check capacity utilization
            if organisation.employee_strength > 0:
                utilization = (organisation.used_employee_strength / organisation.employee_strength) * 100
                if utilization > 95:
                    issues.append("Organisation near capacity limit")
                    recommendations.append("Consider increasing employee capacity")
                    health_score -= 5
                elif utilization < 20:
                    issues.append("Low capacity utilization")
                    recommendations.append("Review capacity planning")
                    health_score -= 3
            
            # Check status
            if organisation.status.value == "inactive":
                issues.append("Organisation is inactive")
                recommendations.append("Review organisation status")
                health_score -= 25
            elif organisation.status.value == "suspended":
                issues.append("Organisation is suspended")
                recommendations.append("Resolve suspension issues")
                health_score -= 40
            
            is_healthy = health_score >= 80 and len(issues) == 0
            
            return OrganisationHealthCheckDTO(
                organisation_id=str(organisation_id),
                organisation_name=organisation.name,
                is_healthy=is_healthy,
                health_score=max(0, health_score),
                issues=issues,
                recommendations=recommendations,
                last_checked=datetime.utcnow(),
                capacity_utilization=round(
                    (organisation.used_employee_strength / max(organisation.employee_strength, 1)) * 100, 2
                )
            )
            
        except Exception as e:
            logger.error(f"Error performing health check for {organisation_id}: {e}")
            return OrganisationHealthCheckDTO(
                organisation_id=str(organisation_id),
                is_healthy=False,
                health_score=0,
                issues=["Health check failed"],
                recommendations=["Contact system administrator"]
            )
    
    async def get_unhealthy_organisations(self) -> List[OrganisationHealthCheckDTO]:
        """Get all organisations with health issues."""
        try:
            # Get all active organisations
            query = {"is_deleted": {"$ne": True}, "status": {"$ne": "suspended"}}
            collection = await self._get_collection()
            cursor = collection.find(query)
            documents = await cursor.to_list(length=None)
            
            unhealthy_orgs = []
            
            for doc in documents:
                org_id = OrganisationId.from_string(doc["organisation_id"])
                health_check = await self.perform_health_check(org_id)
                
                if not health_check.is_healthy or health_check.health_score < 80:
                    unhealthy_orgs.append(health_check)
            
            # Sort by health score (worst first)
            unhealthy_orgs.sort(key=lambda x: x.health_score)
            
            return unhealthy_orgs
            
        except Exception as e:
            logger.error(f"Error getting unhealthy organisations: {e}")
            return []
    
    async def get_organisations_needing_attention(self) -> List[OrganisationHealthCheckDTO]:
        """Get organisations that need immediate attention."""
        try:
            # Get organisations with severe issues
            collection = await self._get_collection()
            query = {
                "is_deleted": {"$ne": True},
                "$or": [
                    {"status": "suspended"},
                    {"status": "inactive"},
                    {"contact_information.email": {"$exists": False}},
                    {"contact_information.email": ""},
                    {"tax_information.pan_number": {"$exists": False}},
                    {"tax_information.pan_number": ""},
                    {"$expr": {"$gte": ["$used_employee_strength", "$employee_strength"]}}
                ]
            }
            
            cursor = collection.find(query)
            documents = await cursor.to_list(length=None)
            
            attention_needed = []
            
            for doc in documents:
                org_id = OrganisationId.from_string(doc["organisation_id"])
                health_check = await self.perform_health_check(org_id)
                attention_needed.append(health_check)
            
            # Sort by severity (lowest health score first)
            attention_needed.sort(key=lambda x: x.health_score)
            
            return attention_needed
            
        except Exception as e:
            logger.error(f"Error getting organisations needing attention: {e}")
            return []

    # ==================== BULK OPERATIONS REPOSITORY IMPLEMENTATION ====================
    
    async def bulk_update_employee_strength(
        self, 
        updates: Dict[OrganisationId, int],
        updated_by: str
    ) -> Dict[str, Any]:
        """Bulk update employee strength for multiple organisations."""
        try:
            collection = await self._get_collection()
            updated_count = 0
            failed_updates = []
            
            for org_id, new_strength in updates.items():
                try:
                    result = await collection.update_one(
                        {"organisation_id": str(org_id), "is_deleted": {"$ne": True}},
                        {
                            "$set": {
                                "employee_strength": new_strength,
                                "updated_at": datetime.utcnow(),
                                "updated_by": updated_by
                            }
                        }
                    )
                    
                    if result.modified_count > 0:
                        updated_count += 1
                    else:
                        failed_updates.append(str(org_id))
                        
                except Exception as update_error:
                    logger.error(f"Error updating {org_id}: {update_error}")
                    failed_updates.append(str(org_id))
            
            return {
                "total_requested": len(updates),
                "updated_count": updated_count,
                "failed_count": len(failed_updates),
                "failed_organisation_ids": failed_updates,
                "success": updated_count > 0,
                "updated_by": updated_by,
                "updated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in bulk employee strength update: {e}")
            return {
                "total_requested": len(updates),
                "updated_count": 0,
                "success": False,
                "error": str(e)
            }
    
    async def bulk_export(
        self, 
        organisation_ids: Optional[List[OrganisationId]] = None,
        format: str = "csv"
    ) -> bytes:
        """Export organisations data in specified format."""
        try:
            import io
            import csv
            import json
            
            collection = await self._get_collection()
            
            # Build query
            query = {"is_deleted": {"$ne": True}}
            if organisation_ids:
                ids = [str(org_id) for org_id in organisation_ids]
                query["organisation_id"] = {"$in": ids}
            
            # Get organisations
            cursor = collection.find(query)
            documents = await cursor.to_list(length=None)
            
            if format.lower() == "csv":
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Write header
                writer.writerow([
                    'Organisation ID', 'Name', 'Type', 'Status', 'Hostname',
                    'Email', 'Phone', 'City', 'State', 'Country', 'PAN Number',
                    'Employee Strength', 'Used Strength', 'Created At'
                ])
                
                # Write data
                for doc in documents:
                    writer.writerow([
                        doc.get('organisation_id', ''),
                        doc.get('name', ''),
                        doc.get('organisation_type', ''),
                        doc.get('status', ''),
                        doc.get('hostname', ''),
                        doc.get('contact_information', {}).get('email', ''),
                        doc.get('contact_information', {}).get('phone', ''),
                        doc.get('address', {}).get('city', ''),
                        doc.get('address', {}).get('state', ''),
                        doc.get('address', {}).get('country', ''),
                        doc.get('tax_information', {}).get('pan_number', ''),
                        doc.get('employee_strength', 0),
                        doc.get('used_employee_strength', 0),
                        doc.get('created_at', '').isoformat() if doc.get('created_at') else ''
                    ])
                
                return output.getvalue().encode('utf-8')
            
            elif format.lower() == "json":
                # Convert documents to JSON-serializable format
                export_data = []
                for doc in documents:
                    # Remove MongoDB-specific fields and convert dates
                    clean_doc = {k: v for k, v in doc.items() if k != '_id'}
                    if 'created_at' in clean_doc and clean_doc['created_at']:
                        clean_doc['created_at'] = clean_doc['created_at'].isoformat()
                    if 'updated_at' in clean_doc and clean_doc['updated_at']:
                        clean_doc['updated_at'] = clean_doc['updated_at'].isoformat()
                    export_data.append(clean_doc)
                
                return json.dumps(export_data, indent=2).encode('utf-8')
            
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Error in bulk export: {e}")
            return f"Export failed: {str(e)}".encode('utf-8')
    
    async def bulk_import(
        self, 
        data: bytes, 
        format: str = "csv",
        created_by: str = "system"
    ) -> Dict[str, Any]:
        """Import organisations from data."""
        try:
            import io
            import csv
            import json
            
            collection = await self._get_collection()
            imported_count = 0
            failed_imports = []
            
            if format.lower() == "csv":
                data_str = data.decode('utf-8')
                reader = csv.DictReader(io.StringIO(data_str))
                
                for row in reader:
                    try:
                        # Create organisation from CSV row
                        org_data = {
                            "organisation_id": row.get('Organisation ID') or str(ObjectId()),
                            "name": row.get('Name', ''),
                            "organisation_type": row.get('Type', 'company'),
                            "status": row.get('Status', 'active'),
                            "hostname": row.get('Hostname', ''),
                            "contact_information": {
                                "email": row.get('Email', ''),
                                "phone": row.get('Phone', ''),
                                "website": row.get('Website', ''),
                                "fax": row.get('Fax', '')
                            },
                            "address": {
                                "street_address": row.get('Street Address', ''),
                                "city": row.get('City', ''),
                                "state": row.get('State', ''),
                                "country": row.get('Country', ''),
                                "pin_code": row.get('Pin Code', ''),
                                "landmark": row.get('Landmark', '')
                            },
                            "tax_information": {
                                "pan_number": row.get('PAN Number', ''),
                                "gst_number": row.get('GST Number', ''),
                                "tan_number": row.get('TAN Number', ''),
                                "cin_number": row.get('CIN Number', '')
                            },
                            "employee_strength": int(row.get('Employee Strength', 0) or 0),
                            "used_employee_strength": int(row.get('Used Strength', 0) or 0),
                            "created_at": datetime.utcnow(),
                            "updated_at": datetime.utcnow(),
                            "created_by": created_by,
                            "is_deleted": False
                        }
                        
                        # Insert organisation
                        await collection.insert_one(org_data)
                        imported_count += 1
                        
                    except Exception as row_error:
                        logger.error(f"Error importing row: {row_error}")
                        failed_imports.append(f"Row {reader.line_num}: {str(row_error)}")
            
            elif format.lower() == "json":
                data_str = data.decode('utf-8')
                organisations_data = json.loads(data_str)
                
                for org_data in organisations_data:
                    try:
                        # Ensure required fields
                        if 'organisation_id' not in org_data:
                            org_data['organisation_id'] = str(ObjectId())
                        
                        org_data.update({
                            "created_at": datetime.utcnow(),
                            "updated_at": datetime.utcnow(),
                            "created_by": created_by,
                            "is_deleted": False
                        })
                        
                        await collection.insert_one(org_data)
                        imported_count += 1
                        
                    except Exception as org_error:
                        logger.error(f"Error importing organisation: {org_error}")
                        failed_imports.append(str(org_error))
            
            else:
                raise ValueError(f"Unsupported import format: {format}")
            
            return {
                "imported_count": imported_count,
                "failed_count": len(failed_imports),
                "failed_imports": failed_imports,
                "success": imported_count > 0,
                "format": format,
                "imported_by": created_by,
                "imported_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in bulk import: {e}")
            return {
                "imported_count": 0,
                "failed_count": 1,
                "failed_imports": [str(e)],
                "success": False,
                "error": str(e)
            }

    # ==================== LEGACY COMPATIBILITY METHODS ====================
    
    async def get_all_organisations_legacy(self) -> List[Dict[str, Any]]:
        """Legacy compatibility for get_all_organisations() function."""
        try:
            organisations = await self.get_all(include_inactive=False, include_deleted=False)
            
            # Convert to legacy document format (without _id)
            legacy_organisations = []
            for org in organisations:
                legacy_data = {
                    "organisation_id": str(getattr(org, 'organisation_id', '')),
                    "name": getattr(org, 'name', ''),
                    "hostname": getattr(org, 'hostname', ''),
                    "is_active": org.is_active() if hasattr(org, 'is_active') else True,
                    "created_at": getattr(org, 'created_at', None),
                    "updated_at": getattr(org, 'updated_at', None)
                }
                legacy_organisations.append(legacy_data)
            
            return legacy_organisations
            
        except Exception as e:
            logger.error(f"Error getting all organisations (legacy): {e}")
            return []
    
    async def get_organisations_count_legacy(self) -> int:
        """Legacy compatibility for get_organisations_count() function."""
        return await self.count_total(include_deleted=False)
    
    async def get_organisation_by_id_legacy(self, organisation_id: str) -> Optional[Dict[str, Any]]:
        """Legacy compatibility for get_organisation_by_id() function."""
        try:
            org_id = OrganisationId.from_string(organisation_id)
            organisation = await self.get_by_id(org_id)
            
            if organisation:
                # Convert to legacy document format
                legacy_data = {
                    "organisation_id": str(getattr(organisation, 'organisation_id', '')),
                    "name": getattr(organisation, 'name', ''),
                    "hostname": getattr(organisation, 'hostname', ''),
                    "is_active": organisation.is_active() if hasattr(organisation, 'is_active') else True,
                    "created_at": getattr(organisation, 'created_at', None),
                    "updated_at": getattr(organisation, 'updated_at', None)
                }
                return legacy_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting organisation by ID (legacy): {e}")
            return None
    
    async def get_organisation_by_hostname_legacy(self, hostname: str) -> Optional[Dict[str, Any]]:
        """Legacy compatibility for get_organisation_by_hostname() function."""
        try:
            organisation = await self.get_by_hostname(hostname)
            
            if organisation:
                # Convert to legacy document format
                legacy_data = {
                    "organisation_id": str(getattr(organisation, 'organisation_id', '')),
                    "name": getattr(organisation, 'name', ''),
                    "hostname": getattr(organisation, 'hostname', ''),
                    "is_active": organisation.is_active() if hasattr(organisation, 'is_active') else True,
                    "created_at": getattr(organisation, 'created_at', None),
                    "updated_at": getattr(organisation, 'updated_at', None)
                }
                return legacy_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting organisation by hostname (legacy): {e}")
            return None

    # ==================== FACTORY METHODS IMPLEMENTATION ====================
    # These methods are required by the repository interfaces but are not used
    # in the current dependency injection architecture. They return self since
    # this repository implements all organisation repository interfaces.
    
    def create_command_repository(self) -> OrganisationCommandRepository:
        """Create command repository instance."""
        return self
    
    def create_query_repository(self) -> OrganisationQueryRepository:
        """Create query repository instance."""
        return self
    
    def create_analytics_repository(self) -> OrganisationAnalyticsRepository:
        """Create analytics repository instance."""
        return self
    
    def create_health_repository(self) -> OrganisationHealthRepository:
        """Create health repository instance."""
        return self
    
    def create_bulk_operations_repository(self) -> OrganisationBulkOperationsRepository:
        """Create bulk operations repository instance."""
        return self 