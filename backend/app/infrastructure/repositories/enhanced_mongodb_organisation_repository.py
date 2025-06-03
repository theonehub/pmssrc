"""
Enhanced MongoDB Repository Implementation for Organisation System
Combines user repository's DatabaseConnector pattern with organisation repository's robust functionality
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING
from bson import ObjectId

from app.infrastructure.database.database_connector import DatabaseConnector
from app.domain.entities.organisation import Organisation
from app.domain.value_objects.organisation_id import OrganisationId
from app.domain.value_objects.organisation_details import (
    OrganisationType, OrganisationStatus, ContactInformation, 
    Address, TaxInformation
)
from app.application.interfaces.repositories.organisation_repository import (
    OrganisationCommandRepository,
    OrganisationQueryRepository,
    OrganisationAnalyticsRepository,
    OrganisationHealthRepository,
    OrganisationBulkOperationsRepository,
    OrganisationRepository
)
from app.application.dto.organisation_dto import (
    OrganisationSearchFiltersDTO,
    OrganisationStatisticsDTO,
    OrganisationAnalyticsDTO,
    OrganisationHealthCheckDTO,
    BulkOrganisationUpdateDTO,
    BulkOrganisationUpdateResultDTO
)


logger = logging.getLogger(__name__)


class EnhancedMongoDBOrganisationRepository(OrganisationRepository):
    """
    Enhanced MongoDB implementation of the complete organisation repository.
    
    Key improvements over original:
    1. Uses DatabaseConnector abstraction (from user repo)
    2. Supports multi-tenancy 
    3. Connection resilience and retry logic
    4. Better error handling and logging
    5. Maintains all sophisticated functionality from original
    
    Follows SOLID principles:
    - SRP: Each method has a single responsibility
    - OCP: Extensible through inheritance
    - LSP: Can be substituted with other implementations
    - ISP: Implements focused interfaces
    - DIP: Depends on abstractions (DatabaseConnector interface)
    """
    
    def __init__(self, database_connector: DatabaseConnector):
        """
        Initialize repository with database connector.
        
        Args:
            database_connector: Database connection abstraction
        """
        self.db_connector = database_connector
        self._collection_name = "organisations"
        
        # Connection configuration (will be set by dependency container)
        self._connection_string = None
        self._client_options = None
        
        # Initialize indexes (non-blocking)
        self._prepare_indexes()
    
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
        Get organisations collection with proper connection management.
        
        Ensures database connection is established in the correct event loop.
        """
        # Ensure database connection
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
                    from app.config.mongodb_config import get_mongodb_connection_string, get_mongodb_client_options
                    connection_string = get_mongodb_connection_string()
                    options = get_mongodb_client_options()
                
                await self.db_connector.connect(connection_string, **options)
                logger.info("MongoDB connection established successfully in current event loop")
                
            except Exception as e:
                logger.error(f"Failed to establish database connection: {e}")
                raise RuntimeError(f"Database connection failed: {e}")
        
        # Get organisation-specific database or global
        # For organisations, we typically use global database but support tenant isolation
        db_name = f"pms_{organisation_id}" if organisation_id else "pms_global_database"
        
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
    
    def _prepare_indexes(self):
        """Prepare index definitions for later creation"""
        try:
            self._index_definitions = [
                {"fields": [("organisation_id", ASCENDING)], "unique": True},
                {"fields": [("name", ASCENDING)], "unique": True},
                {"fields": [("hostname", ASCENDING)], "unique": True},
                {"fields": [("tax_information.pan_number", ASCENDING)], "unique": True},
                {"fields": [("status", ASCENDING)]},
                {"fields": [("organisation_type", ASCENDING)]},
                {"fields": [("created_at", DESCENDING)]},
                {"fields": [("updated_at", DESCENDING)]},
                {"fields": [("is_deleted", ASCENDING)]},
                {"fields": [("status", ASCENDING), ("organisation_type", ASCENDING), ("created_at", DESCENDING)]}
            ]
            logger.info(f"Prepared {len(self._index_definitions)} index definitions for organisations collection")
        except Exception as e:
            logger.error(f"Failed to prepare index definitions: {e}")
    
    async def _ensure_indexes(self, organisation_id: Optional[str] = None):
        """Create database indexes for optimal query performance"""
        try:
            collection = await self._get_collection(organisation_id)
            
            for index_def in getattr(self, '_index_definitions', []):
                try:
                    if index_def.get('unique'):
                        await collection.create_index(
                            index_def['fields'], 
                            unique=True,
                            background=True
                        )
                    else:
                        await collection.create_index(
                            index_def['fields'],
                            background=True
                        )
                except Exception as idx_error:
                    # Log but don't fail - indexes might already exist
                    logger.warning(f"Could not create index {index_def['fields']}: {idx_error}")
            
            logger.info("Organisation database indexes ensured successfully")
        except Exception as e:
            logger.error(f"Failed to ensure organisation indexes: {e}")
    
    async def _publish_events(self, events: List[Any]) -> None:
        """Publish domain events."""
        for event in events:
            logger.info(f"Publishing organisation event: {type(event).__name__}")
            # Implementation would depend on event publisher
    
    # ==================== COMMAND OPERATIONS ====================
    
    async def save(self, organisation: Organisation, organisation_id: Optional[str] = None) -> Organisation:
        """Save a new organisation"""
        try:
            collection = await self._get_collection(organisation_id)
            document = self._organisation_to_document(organisation)
            result = await collection.insert_one(document)
            
            if result.inserted_id:
                # Publish domain events
                if hasattr(organisation, 'get_domain_events'):
                    await self._publish_events(organisation.get_domain_events())
                    organisation.clear_domain_events()
                
                logger.debug(f"Saved organisation: {organisation.organisation_id}")
                return organisation
            else:
                raise Exception("Failed to insert organisation document")
                
        except Exception as e:
            logger.error(f"Error saving organisation {organisation.organisation_id}: {e}")
            raise
    
    async def save_batch(self, organisations: List[Organisation], organisation_id: Optional[str] = None) -> List[Organisation]:
        """Save multiple organisations in batch"""
        try:
            collection = await self._get_collection(organisation_id)
            documents = [self._organisation_to_document(org) for org in organisations]
            result = await collection.insert_many(documents)
            
            if len(result.inserted_ids) == len(organisations):
                # Publish events for all organisations
                for organisation in organisations:
                    if hasattr(organisation, 'get_domain_events'):
                        await self._publish_events(organisation.get_domain_events())
                        organisation.clear_domain_events()
                
                logger.info(f"Saved {len(organisations)} organisations in batch")
                return organisations
            else:
                raise Exception("Failed to insert all organisation documents")
                
        except Exception as e:
            logger.error(f"Error saving organisation batch: {e}")
            raise
    
    async def update(self, organisation: Organisation, organisation_id: Optional[str] = None) -> Organisation:
        """Update an existing organisation"""
        try:
            collection = await self._get_collection(organisation_id)
            document = self._organisation_to_document(organisation)
            document["updated_at"] = datetime.utcnow()
            
            result = await collection.replace_one(
                {"organisation_id": organisation.organisation_id.value},
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
    
    async def delete(self, organisation_id: OrganisationId, soft_delete: bool = True, tenant_id: Optional[str] = None) -> bool:
        """Delete an organisation (soft delete by default)"""
        try:
            collection = await self._get_collection(tenant_id)
            
            if soft_delete:
                result = await collection.update_one(
                    {"organisation_id": organisation_id.value},
                    {
                        "$set": {
                            "is_deleted": True,
                            "deleted_at": datetime.utcnow(),
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
            else:
                result = await collection.delete_one({"organisation_id": organisation_id.value})
            
            success = result.modified_count > 0 or result.deleted_count > 0
            if success:
                logger.debug(f"{'Soft ' if soft_delete else ''}deleted organisation: {organisation_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting organisation {organisation_id}: {e}")
            raise
    
    # ==================== QUERY OPERATIONS ====================
    
    async def get_by_id(self, organisation_id: OrganisationId, tenant_id: Optional[str] = None) -> Optional[Organisation]:
        """Get organisation by ID"""
        try:
            collection = await self._get_collection(tenant_id)
            document = await collection.find_one({
                "organisation_id": organisation_id.value,
                "is_deleted": {"$ne": True}
            })
            
            if document:
                return self._document_to_organisation(document)
            return None
            
        except Exception as e:
            logger.error(f"Error getting organisation by ID {organisation_id}: {e}")
            raise
    
    async def get_by_name(self, name: str, tenant_id: Optional[str] = None) -> Optional[Organisation]:
        """Get organisation by name"""
        try:
            collection = await self._get_collection(tenant_id)
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
    
    async def get_by_hostname(self, hostname: str, tenant_id: Optional[str] = None) -> Optional[Organisation]:
        """Get organisation by hostname"""
        try:
            collection = await self._get_collection(tenant_id)
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
    
    async def get_by_pan_number(self, pan_number: str, tenant_id: Optional[str] = None) -> Optional[Organisation]:
        """Get organisation by PAN number"""
        try:
            collection = await self._get_collection(tenant_id)
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
    
    async def search(self, filters: OrganisationSearchFiltersDTO, tenant_id: Optional[str] = None) -> List[Organisation]:
        """Search organisations with filters"""
        try:
            collection = await self._get_collection(tenant_id)
            query = {"is_deleted": {"$ne": True}}
            
            # Apply filters
            if filters.name:
                query["name"] = {"$regex": filters.name, "$options": "i"}
            
            if filters.organisation_type:
                query["organisation_type"] = filters.organisation_type
            
            if filters.status:
                query["status"] = filters.status
            
            if filters.city:
                query["address.city"] = {"$regex": filters.city, "$options": "i"}
            
            if filters.state:
                query["address.state"] = {"$regex": filters.state, "$options": "i"}
            
            if filters.country:
                query["address.country"] = {"$regex": filters.country, "$options": "i"}
            
            if filters.created_after:
                query["created_at"] = {"$gte": filters.created_after}
            
            if filters.created_before:
                if "created_at" in query:
                    query["created_at"]["$lte"] = filters.created_before
                else:
                    query["created_at"] = {"$lte": filters.created_before}
            
            # Build sort criteria
            sort_criteria = []
            if filters.sort_by:
                direction = DESCENDING if filters.sort_order == "desc" else ASCENDING
                sort_criteria.append((filters.sort_by, direction))
            else:
                sort_criteria.append(("created_at", DESCENDING))
            
            # Execute query with pagination
            cursor = collection.find(query).sort(sort_criteria)
            
            if filters.skip:
                cursor = cursor.skip(filters.skip)
            
            if filters.limit:
                cursor = cursor.limit(filters.limit)
            
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
    
    async def get_all(self, skip: int = 0, limit: int = 100, include_inactive: bool = False, tenant_id: Optional[str] = None) -> List[Organisation]:
        """Get all organisations with pagination"""
        try:
            collection = await self._get_collection(tenant_id)
            query = {"is_deleted": {"$ne": True}}
            if not include_inactive:
                query["status"] = "active"
            
            cursor = collection.find(query).sort("created_at", DESCENDING).skip(skip).limit(limit)
            documents = await cursor.to_list(length=None)
            
            organisations = []
            for doc in documents:
                org = self._document_to_organisation(doc)
                if org:
                    organisations.append(org)
            
            return organisations
            
        except Exception as e:
            logger.error(f"Error getting all organisations: {e}")
            raise
    
    # ==================== ANALYTICS OPERATIONS ====================
    
    async def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        tenant_id: Optional[str] = None
    ) -> OrganisationStatisticsDTO:
        """Get organisation statistics"""
        try:
            collection = await self._get_collection(tenant_id)
            
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
    
    # ==================== COUNT & EXISTENCE OPERATIONS ====================
    
    async def count_total(self, tenant_id: Optional[str] = None) -> int:
        """Count all organisations"""
        try:
            collection = await self._get_collection(tenant_id)
            return await collection.count_documents({
                "is_deleted": {"$ne": True}
            })
        except Exception as e:
            logger.error(f"Error counting organisations: {e}")
            raise
    
    async def count_by_status(self, status: OrganisationStatus, tenant_id: Optional[str] = None) -> int:
        """Count organisations by status"""
        try:
            collection = await self._get_collection(tenant_id)
            return await collection.count_documents({
                "status": status.value,
                "is_deleted": {"$ne": True}
            })
        except Exception as e:
            logger.error(f"Error counting organisations by status {status}: {e}")
            raise
    
    async def exists_by_name(self, name: str, exclude_id: Optional[OrganisationId] = None, tenant_id: Optional[str] = None) -> bool:
        """Check if organisation exists by name"""
        try:
            collection = await self._get_collection(tenant_id)
            query = {
                "name": name,
                "is_deleted": {"$ne": True}
            }
            if exclude_id:
                query["organisation_id"] = {"$ne": exclude_id.value}
            
            count = await collection.count_documents(query)
            return count > 0
        except Exception as e:
            logger.error(f"Error checking organisation existence by name {name}: {e}")
            raise
    
    async def exists_by_hostname(self, hostname: str, exclude_id: Optional[OrganisationId] = None, tenant_id: Optional[str] = None) -> bool:
        """Check if organisation exists by hostname"""
        try:
            collection = await self._get_collection(tenant_id)
            query = {
                "hostname": hostname,
                "is_deleted": {"$ne": True}
            }
            if exclude_id:
                query["organisation_id"] = {"$ne": exclude_id.value}
            
            count = await collection.count_documents(query)
            return count > 0
        except Exception as e:
            logger.error(f"Error checking organisation existence by hostname {hostname}: {e}")
            raise
    
    async def exists_by_pan_number(self, pan_number: str, exclude_id: Optional[OrganisationId] = None, tenant_id: Optional[str] = None) -> bool:
        """Check if organisation exists by PAN number"""
        try:
            collection = await self._get_collection(tenant_id)
            query = {
                "tax_information.pan_number": pan_number,
                "is_deleted": {"$ne": True}
            }
            if exclude_id:
                query["organisation_id"] = {"$ne": exclude_id.value}
            
            count = await collection.count_documents(query)
            return count > 0
        except Exception as e:
            logger.error(f"Error checking organisation existence by PAN {pan_number}: {e}")
            raise
    
    # ==================== HELPER METHODS ====================
    
    def _organisation_to_document(self, organisation: Organisation) -> Dict[str, Any]:
        """Convert organisation entity to MongoDB document"""
        return {
            "organisation_id": organisation.organisation_id.value,
            "name": organisation.name,
            "description": organisation.description,
            "organisation_type": organisation.organisation_type.value,
            "status": organisation.status.value,
            "hostname": organisation.hostname,
            "contact_information": {
                "email": organisation.contact_info.email,
                "phone": organisation.contact_info.phone,
                "website": organisation.contact_info.website,
                "fax": organisation.contact_info.fax
            },
            "address": {
                "street_address": organisation.address.street_address,
                "city": organisation.address.city,
                "state": organisation.address.state,
                "country": organisation.address.country,
                "pin_code": organisation.address.pin_code,
                "landmark": organisation.address.landmark
            },
            "tax_information": {
                "pan_number": organisation.tax_info.pan_number,
                "gst_number": organisation.tax_info.gst_number,
                "tan_number": organisation.tax_info.tan_number,
                "cin_number": organisation.tax_info.cin_number
            },
            "employee_strength": organisation.employee_strength,
            "used_employee_strength": organisation.used_employee_strength,
            "created_at": organisation.created_at,
            "updated_at": organisation.updated_at,
            "is_deleted": getattr(organisation, 'is_deleted', False),
            "deleted_at": getattr(organisation, 'deleted_at', None)
        }
    
    def _document_to_organisation(self, document: Dict[str, Any]) -> Optional[Organisation]:
        """Convert MongoDB document to organisation entity"""
        try:
            # Create value objects
            organisation_id = OrganisationId.from_string(document["organisation_id"])
            organisation_type = OrganisationType(document["organisation_type"])
            status = OrganisationStatus(document["status"])
            
            contact_info = ContactInformation(
                email=document["contact_information"]["email"],
                phone=document["contact_information"]["phone"],
                website=document["contact_information"].get("website"),
                fax=document["contact_information"].get("fax")
            )
            
            address = Address(
                street_address=document["address"]["street_address"],
                city=document["address"]["city"],
                state=document["address"]["state"],
                country=document["address"]["country"],
                pin_code=document["address"]["pin_code"],
                landmark=document["address"].get("landmark")
            )
            
            tax_info = TaxInformation(
                pan_number=document["tax_information"]["pan_number"],
                gst_number=document["tax_information"].get("gst_number"),
                tan_number=document["tax_information"].get("tan_number"),
                cin_number=document["tax_information"].get("cin_number")
            )
            
            # Create organisation using factory method
            return Organisation.from_existing_data(
                organisation_id=organisation_id,
                name=document["name"],
                description=document.get("description"),
                organisation_type=organisation_type,
                status=status,
                hostname=document.get("hostname"),
                contact_info=contact_info,
                address=address,
                tax_info=tax_info,
                employee_strength=document["employee_strength"],
                used_employee_strength=document.get("used_employee_strength", 0),
                created_at=document["created_at"],
                updated_at=document.get("updated_at"),
                is_deleted=document.get("is_deleted", False),
                deleted_at=document.get("deleted_at")
            )
            
        except Exception as e:
            logger.error(f"Error converting document to organisation: {e}")
            return None
    
    # ==================== REMAINING INTERFACE IMPLEMENTATIONS ====================
    # Note: I've implemented the core methods. The remaining methods from the original
    # repository (analytics, health checks, bulk operations) can be added using the 
    # same pattern with the enhanced _get_collection method.
    
    # ==================== ANALYTICS OPERATIONS (EXTENDED) ====================
    
    async def get_analytics(self, tenant_id: Optional[str] = None) -> OrganisationAnalyticsDTO:
        """Get comprehensive organisation analytics"""
        try:
            # Get basic statistics
            stats = await self.get_statistics(tenant_id=tenant_id)
            
            # Get additional analytics data
            growth_trends = await self.get_growth_trends(tenant_id=tenant_id)
            capacity_stats = await self.get_capacity_utilization_stats(tenant_id=tenant_id)
            location_distribution = await self.get_organisations_by_location_count(tenant_id=tenant_id)
            
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
    
    async def get_organisations_by_type_count(self, tenant_id: Optional[str] = None) -> Dict[str, int]:
        """Get count of organisations by type"""
        try:
            collection = await self._get_collection(tenant_id)
            pipeline = [
                {"$match": {"is_deleted": {"$ne": True}}},
                {"$group": {"_id": "$organisation_type", "count": {"$sum": 1}}}
            ]
            
            results = await collection.aggregate(pipeline).to_list(length=None)
            return {item["_id"]: item["count"] for item in results}
            
        except Exception as e:
            logger.error(f"Error getting organisations by type count: {e}")
            return {}
    
    async def get_organisations_by_status_count(self, tenant_id: Optional[str] = None) -> Dict[str, int]:
        """Get count of organisations by status"""
        try:
            collection = await self._get_collection(tenant_id)
            pipeline = [
                {"$match": {"is_deleted": {"$ne": True}}},
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]
            
            results = await collection.aggregate(pipeline).to_list(length=None)
            return {item["_id"]: item["count"] for item in results}
            
        except Exception as e:
            logger.error(f"Error getting organisations by status count: {e}")
            return {}
    
    async def get_organisations_by_location_count(self, tenant_id: Optional[str] = None) -> Dict[str, Dict[str, int]]:
        """Get count of organisations by location (country, state, city)"""
        try:
            collection = await self._get_collection(tenant_id)
            
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
    
    async def get_capacity_utilization_stats(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """Get capacity utilization statistics"""
        try:
            collection = await self._get_collection(tenant_id)
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
    
    async def get_growth_trends(self, months: int = 12, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """Get organisation growth trends over specified months"""
        try:
            collection = await self._get_collection(tenant_id)
            
            # Calculate date range
            end_date = datetime.utcnow()
            from dateutil.relativedelta import relativedelta
            start_date = end_date - relativedelta(months=months)
            
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
    
    # ==================== HEALTH CHECK OPERATIONS ====================
    
    async def perform_health_check(self, organisation_id: OrganisationId, tenant_id: Optional[str] = None) -> OrganisationHealthCheckDTO:
        """Perform health check for specific organisation"""
        try:
            organisation = await self.get_by_id(organisation_id, tenant_id)
            
            if not organisation:
                return OrganisationHealthCheckDTO(
                    organisation_id=organisation_id.value,
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
                organisation_id=organisation_id.value,
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
                organisation_id=organisation_id.value,
                is_healthy=False,
                health_score=0,
                issues=["Health check failed"],
                recommendations=["Contact system administrator"]
            )
    
    async def get_unhealthy_organisations(self, tenant_id: Optional[str] = None) -> List[OrganisationHealthCheckDTO]:
        """Get all organisations with health issues"""
        try:
            collection = await self._get_collection(tenant_id)
            
            # Get all active organisations
            query = {"is_deleted": {"$ne": True}, "status": {"$ne": "suspended"}}
            cursor = collection.find(query)
            documents = await cursor.to_list(length=None)
            
            unhealthy_orgs = []
            
            for doc in documents:
                org_id = OrganisationId.from_string(doc["organisation_id"])
                health_check = await self.perform_health_check(org_id, tenant_id)
                
                if not health_check.is_healthy or health_check.health_score < 80:
                    unhealthy_orgs.append(health_check)
            
            # Sort by health score (worst first)
            unhealthy_orgs.sort(key=lambda x: x.health_score)
            
            return unhealthy_orgs
            
        except Exception as e:
            logger.error(f"Error getting unhealthy organisations: {e}")
            return []
    
    async def get_organisations_needing_attention(self, tenant_id: Optional[str] = None) -> List[OrganisationHealthCheckDTO]:
        """Get organisations that need immediate attention"""
        try:
            collection = await self._get_collection(tenant_id)
            
            # Get organisations with severe issues
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
                health_check = await self.perform_health_check(org_id, tenant_id)
                attention_needed.append(health_check)
            
            # Sort by severity (lowest health score first)
            attention_needed.sort(key=lambda x: x.health_score)
            
            return attention_needed
            
        except Exception as e:
            logger.error(f"Error getting organisations needing attention: {e}")
            return []
    
    # ==================== BULK OPERATIONS ====================
    
    async def bulk_update_status(
        self, 
        organisation_ids: List[OrganisationId], 
        status: OrganisationStatus,
        updated_by: str,
        reason: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Bulk update organisation status"""
        try:
            collection = await self._get_collection(tenant_id)
            ids = [org_id.value for org_id in organisation_ids]
            
            update_data = {
                "status": status.value,
                "updated_at": datetime.utcnow(),
                "updated_by": updated_by
            }
            
            if reason:
                update_data["status_change_reason"] = reason
            
            result = await collection.update_many(
                {"organisation_id": {"$in": ids}, "is_deleted": {"$ne": True}},
                {"$set": update_data}
            )
            
            return {
                "total_requested": len(organisation_ids),
                "updated_count": result.modified_count,
                "matched_count": result.matched_count,
                "success": result.modified_count > 0,
                "new_status": status.value,
                "updated_by": updated_by,
                "updated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in bulk status update: {e}")
            return {
                "total_requested": len(organisation_ids),
                "updated_count": 0,
                "success": False,
                "error": str(e)
            }
    
    async def bulk_update_employee_strength(
        self, 
        updates: Dict[OrganisationId, int],
        updated_by: str,
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Bulk update employee strength for multiple organisations"""
        try:
            collection = await self._get_collection(tenant_id)
            updated_count = 0
            failed_updates = []
            
            for org_id, new_strength in updates.items():
                try:
                    result = await collection.update_one(
                        {"organisation_id": org_id.value, "is_deleted": {"$ne": True}},
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
                        failed_updates.append(org_id.value)
                        
                except Exception as update_error:
                    logger.error(f"Error updating {org_id}: {update_error}")
                    failed_updates.append(org_id.value)
            
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
        format: str = "csv",
        tenant_id: Optional[str] = None
    ) -> bytes:
        """Export organisations data in specified format"""
        try:
            collection = await self._get_collection(tenant_id)
            
            # Build query
            query = {"is_deleted": {"$ne": True}}
            if organisation_ids:
                ids = [org_id.value for org_id in organisation_ids]
                query["organisation_id"] = {"$in": ids}
            
            # Get organisations
            cursor = collection.find(query)
            documents = await cursor.to_list(length=None)
            
            if format.lower() == "csv":
                import io
                import csv
                
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
                import json
                
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
        created_by: str = "system",
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Import organisations from data"""
        try:
            collection = await self._get_collection(tenant_id)
            imported_count = 0
            failed_imports = []
            
            if format.lower() == "csv":
                import io
                import csv
                
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
                import json
                
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
    
    # ==================== ADDITIONAL QUERY METHODS ====================
    
    async def get_by_status(self, status: OrganisationStatus, tenant_id: Optional[str] = None) -> List[Organisation]:
        """Get organisations by status"""
        try:
            collection = await self._get_collection(tenant_id)
            cursor = collection.find({
                "status": status.value,
                "is_deleted": {"$ne": True}
            }).sort("created_at", DESCENDING)
            
            documents = await cursor.to_list(length=None)
            
            organisations = []
            for doc in documents:
                org = self._document_to_organisation(doc)
                if org:
                    organisations.append(org)
            
            return organisations
            
        except Exception as e:
            logger.error(f"Error getting organisations by status {status}: {e}")
            raise
    
    async def get_by_type(self, organisation_type: OrganisationType, tenant_id: Optional[str] = None) -> List[Organisation]:
        """Get organisations by type"""
        try:
            collection = await self._get_collection(tenant_id)
            cursor = collection.find({
                "organisation_type": organisation_type.value,
                "is_deleted": {"$ne": True}
            }).sort("created_at", DESCENDING)
            
            documents = await cursor.to_list(length=None)
            
            organisations = []
            for doc in documents:
                org = self._document_to_organisation(doc)
                if org:
                    organisations.append(org)
            
            return organisations
            
        except Exception as e:
            logger.error(f"Error getting organisations by type {organisation_type}: {e}")
            raise
    
    async def get_by_location(self, city: str = None, state: str = None, country: str = None, tenant_id: Optional[str] = None) -> List[Organisation]:
        """Get organisations by location"""
        try:
            collection = await self._get_collection(tenant_id)
            query = {"is_deleted": {"$ne": True}}
            
            if city:
                query["address.city"] = {"$regex": city, "$options": "i"}
            if state:
                query["address.state"] = {"$regex": state, "$options": "i"}
            if country:
                query["address.country"] = {"$regex": country, "$options": "i"}
            
            cursor = collection.find(query).sort("created_at", DESCENDING)
            documents = await cursor.to_list(length=None)
            
            organisations = []
            for doc in documents:
                org = self._document_to_organisation(doc)
                if org:
                    organisations.append(org)
            
            return organisations
            
        except Exception as e:
            logger.error(f"Error getting organisations by location: {e}")
            raise
    
    async def count_by_type(self, organisation_type: OrganisationType, tenant_id: Optional[str] = None) -> int:
        """Count organisations by type"""
        try:
            collection = await self._get_collection(tenant_id)
            return await collection.count_documents({
                "organisation_type": organisation_type.value,
                "is_deleted": {"$ne": True}
            })
        except Exception as e:
            logger.error(f"Error counting organisations by type {organisation_type}: {e}")
            raise
    
    async def get_organisations_created_in_period(
        self, 
        start_date: datetime, 
        end_date: datetime,
        tenant_id: Optional[str] = None
    ) -> List[Organisation]:
        """Get organisations created within specified period"""
        try:
            collection = await self._get_collection(tenant_id)
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
    
    async def get_top_organisations_by_capacity(self, limit: int = 10, tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get top organisations by employee capacity"""
        try:
            collection = await self._get_collection(tenant_id)
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
    
    # Factory Methods (required by interfaces)
    def create_command_repository(self) -> OrganisationCommandRepository:
        """Create command repository instance"""
        return self
    
    def create_query_repository(self) -> OrganisationQueryRepository:
        """Create query repository instance"""
        return self
    
    def create_analytics_repository(self) -> OrganisationAnalyticsRepository:
        """Create analytics repository instance"""
        return self
    
    def create_health_repository(self) -> OrganisationHealthRepository:
        """Create health repository instance"""
        return self
    
    def create_bulk_operations_repository(self) -> OrganisationBulkOperationsRepository:
        """Create bulk operations repository instance"""
        return self 