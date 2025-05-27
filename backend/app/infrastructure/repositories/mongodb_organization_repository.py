"""
MongoDB Repository Implementation for Organization System
Implements all organization repository interfaces using MongoDB
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING
from bson import ObjectId

from domain.entities.organization import Organization
from domain.value_objects.organization_id import OrganizationId
from domain.value_objects.organization_details import (
    OrganizationType, OrganizationStatus, ContactInformation, 
    Address, TaxInformation
)
from application.interfaces.repositories.organization_repository import (
    OrganizationCommandRepository,
    OrganizationQueryRepository,
    OrganizationAnalyticsRepository,
    OrganizationHealthRepository,
    OrganizationBulkOperationsRepository,
    OrganizationRepository
)
from application.dto.organization_dto import (
    OrganizationSearchFiltersDTO,
    OrganizationStatisticsDTO,
    OrganizationAnalyticsDTO,
    OrganizationHealthCheckDTO,
    BulkOrganizationUpdateDTO,
    BulkOrganizationUpdateResultDTO
)


logger = logging.getLogger(__name__)


class MongoDBOrganizationRepository(OrganizationRepository):
    """
    MongoDB implementation of the complete organization repository.
    
    Follows SOLID principles:
    - SRP: Each method has a single responsibility
    - OCP: Extensible through inheritance
    - LSP: Can be substituted with other implementations
    - ISP: Implements focused interfaces
    - DIP: Depends on abstractions (database interface)
    """
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.organizations_collection = database.organizations
        
        # Create indexes for better performance
        self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes for optimal query performance"""
        try:
            # Organizations collection indexes
            self.organizations_collection.create_index([("organization_id", ASCENDING)], unique=True)
            self.organizations_collection.create_index([("name", ASCENDING)], unique=True)
            self.organizations_collection.create_index([("hostname", ASCENDING)], unique=True)
            self.organizations_collection.create_index([("tax_information.pan_number", ASCENDING)], unique=True)
            self.organizations_collection.create_index([("status", ASCENDING)])
            self.organizations_collection.create_index([("organization_type", ASCENDING)])
            self.organizations_collection.create_index([("created_at", DESCENDING)])
            self.organizations_collection.create_index([("updated_at", DESCENDING)])
            self.organizations_collection.create_index([("is_deleted", ASCENDING)])
            self.organizations_collection.create_index([
                ("status", ASCENDING),
                ("organization_type", ASCENDING),
                ("created_at", DESCENDING)
            ])
            
            logger.info("Organization database indexes created successfully")
        except Exception as e:
            logger.error(f"Failed to create organization indexes: {e}")
    
    # ==================== COMMAND OPERATIONS ====================
    
    async def save(self, organization: Organization) -> Organization:
        """Save a new organization"""
        try:
            document = self._organization_to_document(organization)
            result = await self.organizations_collection.insert_one(document)
            
            if result.inserted_id:
                logger.debug(f"Saved organization: {organization.organization_id}")
                return organization
            else:
                raise Exception("Failed to insert organization document")
                
        except Exception as e:
            logger.error(f"Error saving organization {organization.organization_id}: {e}")
            raise
    
    async def save_batch(self, organizations: List[Organization]) -> List[Organization]:
        """Save multiple organizations in batch"""
        try:
            documents = [self._organization_to_document(org) for org in organizations]
            result = await self.organizations_collection.insert_many(documents)
            
            if len(result.inserted_ids) == len(organizations):
                logger.info(f"Saved {len(organizations)} organizations in batch")
                return organizations
            else:
                raise Exception("Failed to insert all organization documents")
                
        except Exception as e:
            logger.error(f"Error saving organization batch: {e}")
            raise
    
    async def update(self, organization: Organization) -> Organization:
        """Update an existing organization"""
        try:
            document = self._organization_to_document(organization)
            document["updated_at"] = datetime.utcnow()
            
            result = await self.organizations_collection.replace_one(
                {"organization_id": organization.organization_id.value},
                document
            )
            
            if result.modified_count > 0 or result.matched_count > 0:
                logger.debug(f"Updated organization: {organization.organization_id}")
                return organization
            else:
                raise Exception(f"Organization {organization.organization_id} not found for update")
                
        except Exception as e:
            logger.error(f"Error updating organization {organization.organization_id}: {e}")
            raise
    
    async def delete(self, organization_id: OrganizationId) -> bool:
        """Soft delete an organization"""
        try:
            result = await self.organizations_collection.update_one(
                {"organization_id": organization_id.value},
                {
                    "$set": {
                        "is_deleted": True,
                        "deleted_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            success = result.modified_count > 0
            if success:
                logger.debug(f"Soft deleted organization: {organization_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting organization {organization_id}: {e}")
            raise
    
    # ==================== QUERY OPERATIONS ====================
    
    async def get_by_id(self, organization_id: OrganizationId) -> Optional[Organization]:
        """Get organization by ID"""
        try:
            document = await self.organizations_collection.find_one({
                "organization_id": organization_id.value,
                "is_deleted": {"$ne": True}
            })
            
            if document:
                return self._document_to_organization(document)
            return None
            
        except Exception as e:
            logger.error(f"Error getting organization by ID {organization_id}: {e}")
            raise
    
    async def get_by_name(self, name: str) -> Optional[Organization]:
        """Get organization by name"""
        try:
            document = await self.organizations_collection.find_one({
                "name": name,
                "is_deleted": {"$ne": True}
            })
            
            if document:
                return self._document_to_organization(document)
            return None
            
        except Exception as e:
            logger.error(f"Error getting organization by name {name}: {e}")
            raise
    
    async def get_by_hostname(self, hostname: str) -> Optional[Organization]:
        """Get organization by hostname"""
        try:
            document = await self.organizations_collection.find_one({
                "hostname": hostname,
                "is_deleted": {"$ne": True}
            })
            
            if document:
                return self._document_to_organization(document)
            return None
            
        except Exception as e:
            logger.error(f"Error getting organization by hostname {hostname}: {e}")
            raise
    
    async def get_by_pan_number(self, pan_number: str) -> Optional[Organization]:
        """Get organization by PAN number"""
        try:
            document = await self.organizations_collection.find_one({
                "tax_information.pan_number": pan_number,
                "is_deleted": {"$ne": True}
            })
            
            if document:
                return self._document_to_organization(document)
            return None
            
        except Exception as e:
            logger.error(f"Error getting organization by PAN {pan_number}: {e}")
            raise
    
    async def search(self, filters: OrganizationSearchFiltersDTO) -> List[Organization]:
        """Search organizations with filters"""
        try:
            query = {"is_deleted": {"$ne": True}}
            
            # Apply filters
            if filters.name:
                query["name"] = {"$regex": filters.name, "$options": "i"}
            
            if filters.organization_type:
                query["organization_type"] = filters.organization_type
            
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
            cursor = self.organizations_collection.find(query).sort(sort_criteria)
            
            if filters.skip:
                cursor = cursor.skip(filters.skip)
            
            if filters.limit:
                cursor = cursor.limit(filters.limit)
            
            documents = await cursor.to_list(length=None)
            
            organizations = []
            for doc in documents:
                org = self._document_to_organization(doc)
                if org:
                    organizations.append(org)
            
            return organizations
            
        except Exception as e:
            logger.error(f"Error searching organizations: {e}")
            raise
    
    async def get_all(self, skip: int = 0, limit: int = 100, include_inactive: bool = False) -> List[Organization]:
        """Get all organizations with pagination"""
        try:
            query = {"is_deleted": {"$ne": True}}
            if not include_inactive:
                query["status"] = "active"
            
            cursor = self.organizations_collection.find(query).sort("created_at", DESCENDING).skip(skip).limit(limit)
            
            documents = await cursor.to_list(length=None)
            
            organizations = []
            for doc in documents:
                org = self._document_to_organization(doc)
                if org:
                    organizations.append(org)
            
            return organizations
            
        except Exception as e:
            logger.error(f"Error getting all organizations: {e}")
            raise
    
    async def count_total(self) -> int:
        """Count all organizations"""
        try:
            return await self.organizations_collection.count_documents({
                "is_deleted": {"$ne": True}
            })
        except Exception as e:
            logger.error(f"Error counting organizations: {e}")
            raise
    
    async def count_by_status(self, status: OrganizationStatus) -> int:
        """Count organizations by status"""
        try:
            return await self.organizations_collection.count_documents({
                "status": status.value,
                "is_deleted": {"$ne": True}
            })
        except Exception as e:
            logger.error(f"Error counting organizations by status {status}: {e}")
            raise
    
    async def count_by_type(self, organization_type: OrganizationType) -> int:
        """Count organizations by type"""
        try:
            return await self.organizations_collection.count_documents({
                "organization_type": organization_type.value,
                "is_deleted": {"$ne": True}
            })
        except Exception as e:
            logger.error(f"Error counting organizations by type {organization_type}: {e}")
            raise
    
    async def exists_by_name(self, name: str) -> bool:
        """Check if organization exists by name"""
        try:
            count = await self.organizations_collection.count_documents({
                "name": name,
                "is_deleted": {"$ne": True}
            })
            return count > 0
        except Exception as e:
            logger.error(f"Error checking organization existence by name {name}: {e}")
            raise
    
    async def exists_by_hostname(self, hostname: str) -> bool:
        """Check if organization exists by hostname"""
        try:
            count = await self.organizations_collection.count_documents({
                "hostname": hostname,
                "is_deleted": {"$ne": True}
            })
            return count > 0
        except Exception as e:
            logger.error(f"Error checking organization existence by hostname {hostname}: {e}")
            raise
    
    async def exists_by_pan_number(self, pan_number: str, exclude_id: Optional[OrganizationId] = None) -> bool:
        """Check if organization exists by PAN number"""
        try:
            query = {
                "tax_information.pan_number": pan_number,
                "is_deleted": {"$ne": True}
            }
            if exclude_id:
                query["organization_id"] = {"$ne": exclude_id.value}
            
            count = await self.organizations_collection.count_documents(query)
            return count > 0
        except Exception as e:
            logger.error(f"Error checking organization existence by PAN {pan_number}: {e}")
            raise
    
    async def exists_by_name(self, name: str, exclude_id: Optional[OrganizationId] = None) -> bool:
        """Check if organization exists by name"""
        try:
            query = {
                "name": name,
                "is_deleted": {"$ne": True}
            }
            if exclude_id:
                query["organization_id"] = {"$ne": exclude_id.value}
            
            count = await self.organizations_collection.count_documents(query)
            return count > 0
        except Exception as e:
            logger.error(f"Error checking organization existence by name {name}: {e}")
            raise
    
    async def exists_by_hostname(self, hostname: str, exclude_id: Optional[OrganizationId] = None) -> bool:
        """Check if organization exists by hostname"""
        try:
            query = {
                "hostname": hostname,
                "is_deleted": {"$ne": True}
            }
            if exclude_id:
                query["organization_id"] = {"$ne": exclude_id.value}
            
            count = await self.organizations_collection.count_documents(query)
            return count > 0
        except Exception as e:
            logger.error(f"Error checking organization existence by hostname {hostname}: {e}")
            raise
    
    async def get_by_status(self, status: OrganizationStatus) -> List[Organization]:
        """Get organizations by status"""
        try:
            cursor = self.organizations_collection.find({
                "status": status.value,
                "is_deleted": {"$ne": True}
            }).sort("created_at", DESCENDING)
            
            documents = await cursor.to_list(length=None)
            
            organizations = []
            for doc in documents:
                org = self._document_to_organization(doc)
                if org:
                    organizations.append(org)
            
            return organizations
            
        except Exception as e:
            logger.error(f"Error getting organizations by status {status}: {e}")
            raise
    
    async def get_by_type(self, organization_type: OrganizationType) -> List[Organization]:
        """Get organizations by type"""
        try:
            cursor = self.organizations_collection.find({
                "organization_type": organization_type.value,
                "is_deleted": {"$ne": True}
            }).sort("created_at", DESCENDING)
            
            documents = await cursor.to_list(length=None)
            
            organizations = []
            for doc in documents:
                org = self._document_to_organization(doc)
                if org:
                    organizations.append(org)
            
            return organizations
            
        except Exception as e:
            logger.error(f"Error getting organizations by type {organization_type}: {e}")
            raise
    
    async def get_by_location(self, city: str = None, state: str = None, country: str = None) -> List[Organization]:
        """Get organizations by location"""
        try:
            query = {"is_deleted": {"$ne": True}}
            
            if city:
                query["address.city"] = {"$regex": city, "$options": "i"}
            if state:
                query["address.state"] = {"$regex": state, "$options": "i"}
            if country:
                query["address.country"] = {"$regex": country, "$options": "i"}
            
            cursor = self.organizations_collection.find(query).sort("created_at", DESCENDING)
            
            documents = await cursor.to_list(length=None)
            
            organizations = []
            for doc in documents:
                org = self._document_to_organization(doc)
                if org:
                    organizations.append(org)
            
            return organizations
            
        except Exception as e:
            logger.error(f"Error getting organizations by location: {e}")
            raise
    
    # ==================== ANALYTICS OPERATIONS ====================
    
    async def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> OrganizationStatisticsDTO:
        """Get organization statistics"""
        try:
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
                        "total_organizations": {"$sum": 1},
                        "active_organizations": {
                            "$sum": {"$cond": [{"$eq": ["$status", "active"]}, 1, 0]}
                        },
                        "inactive_organizations": {
                            "$sum": {"$cond": [{"$eq": ["$status", "inactive"]}, 1, 0]}
                        },
                        "suspended_organizations": {
                            "$sum": {"$cond": [{"$eq": ["$status", "suspended"]}, 1, 0]}
                        },
                        "total_employee_capacity": {"$sum": "$employee_strength"},
                        "total_employees_used": {"$sum": "$used_employee_strength"},
                        "avg_employee_strength": {"$avg": "$employee_strength"}
                    }
                }
            ]
            
            result = await self.organizations_collection.aggregate(pipeline).to_list(length=1)
            stats = result[0] if result else {}
            
            # Get type distribution
            type_pipeline = [
                {"$match": base_query},
                {"$group": {"_id": "$organization_type", "count": {"$sum": 1}}}
            ]
            type_results = await self.organizations_collection.aggregate(type_pipeline).to_list(length=None)
            type_distribution = {item["_id"]: item["count"] for item in type_results}
            
            return OrganizationStatisticsDTO(
                total_organizations=stats.get("total_organizations", 0),
                active_organizations=stats.get("active_organizations", 0),
                inactive_organizations=stats.get("inactive_organizations", 0),
                suspended_organizations=stats.get("suspended_organizations", 0),
                organizations_by_type=type_distribution,
                total_employee_capacity=stats.get("total_employee_capacity", 0),
                total_employees_used=stats.get("total_employees_used", 0),
                average_employee_strength=stats.get("avg_employee_strength", 0.0),
                capacity_utilization_percentage=round(
                    (stats.get("total_employees_used", 0) / max(stats.get("total_employee_capacity", 1), 1)) * 100, 2
                )
            )
            
        except Exception as e:
            logger.error(f"Error getting organization statistics: {e}")
            raise
    
    # ==================== HELPER METHODS ====================
    
    def _organization_to_document(self, organization: Organization) -> Dict[str, Any]:
        """Convert organization entity to MongoDB document"""
        return {
            "organization_id": organization.organization_id.value,
            "name": organization.name,
            "description": organization.description,
            "organization_type": organization.organization_type.value,
            "status": organization.status.value,
            "hostname": organization.hostname,
            "contact_information": {
                "email": organization.contact_info.email,
                "phone": organization.contact_info.phone,
                "website": organization.contact_info.website,
                "fax": organization.contact_info.fax
            },
            "address": {
                "street_address": organization.address.street_address,
                "city": organization.address.city,
                "state": organization.address.state,
                "country": organization.address.country,
                "pin_code": organization.address.pin_code,
                "landmark": organization.address.landmark
            },
            "tax_information": {
                "pan_number": organization.tax_info.pan_number,
                "gst_number": organization.tax_info.gst_number,
                "tan_number": organization.tax_info.tan_number,
                "cin_number": organization.tax_info.cin_number
            },
            "employee_strength": organization.employee_strength,
            "used_employee_strength": organization.used_employee_strength,
            "created_at": organization.created_at,
            "updated_at": organization.updated_at,
            "is_deleted": getattr(organization, 'is_deleted', False),
            "deleted_at": getattr(organization, 'deleted_at', None)
        }
    
    def _document_to_organization(self, document: Dict[str, Any]) -> Optional[Organization]:
        """Convert MongoDB document to organization entity"""
        try:
            # Create value objects
            organization_id = OrganizationId.from_string(document["organization_id"])
            organization_type = OrganizationType(document["organization_type"])
            status = OrganizationStatus(document["status"])
            
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
            
            # Create organization using factory method
            return Organization.from_existing_data(
                organization_id=organization_id,
                name=document["name"],
                description=document.get("description"),
                organization_type=organization_type,
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
            logger.error(f"Error converting document to organization: {e}")
            return None 