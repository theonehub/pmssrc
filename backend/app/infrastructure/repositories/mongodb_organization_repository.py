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

from app.domain.entities.organization import Organization
from app.domain.value_objects.organization_id import OrganizationId
from app.domain.value_objects.organization_details import (
    OrganizationType, OrganizationStatus, ContactInformation, 
    Address, TaxInformation
)
from app.application.interfaces.repositories.organization_repository import (
    OrganizationCommandRepository,
    OrganizationQueryRepository,
    OrganizationAnalyticsRepository,
    OrganizationHealthRepository,
    OrganizationBulkOperationsRepository,
    OrganizationRepository
)
from app.application.dto.organization_dto import (
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
    
    # ==================== MISSING ABSTRACT METHODS IMPLEMENTATION ====================
    
    # OrganizationAnalyticsRepository Missing Methods
    
    async def get_analytics(self) -> OrganizationAnalyticsDTO:
        """Get comprehensive organization analytics"""
        try:
            # Get basic statistics
            stats = await self.get_statistics()
            
            # Get additional analytics data
            growth_trends = await self.get_growth_trends()
            capacity_stats = await self.get_capacity_utilization_stats()
            location_distribution = await self.get_organizations_by_location_count()
            
            return OrganizationAnalyticsDTO(
                total_organizations=stats.total_organizations,
                active_organizations=stats.active_organizations,
                inactive_organizations=stats.inactive_organizations,
                organizations_by_type=stats.organizations_by_type,
                organizations_by_location=location_distribution,
                capacity_utilization=capacity_stats,
                growth_trends=growth_trends,
                average_employee_strength=stats.average_employee_strength,
                capacity_utilization_percentage=stats.capacity_utilization_percentage
            )
            
        except Exception as e:
            logger.error(f"Error getting organization analytics: {e}")
            raise
    
    async def get_organizations_by_type_count(self) -> Dict[str, int]:
        """Get count of organizations by type"""
        try:
            pipeline = [
                {"$match": {"is_deleted": {"$ne": True}}},
                {"$group": {"_id": "$organization_type", "count": {"$sum": 1}}}
            ]
            
            results = await self.organizations_collection.aggregate(pipeline).to_list(length=None)
            return {item["_id"]: item["count"] for item in results}
            
        except Exception as e:
            logger.error(f"Error getting organizations by type count: {e}")
            return {}
    
    async def get_organizations_by_status_count(self) -> Dict[str, int]:
        """Get count of organizations by status"""
        try:
            pipeline = [
                {"$match": {"is_deleted": {"$ne": True}}},
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]
            
            results = await self.organizations_collection.aggregate(pipeline).to_list(length=None)
            return {item["_id"]: item["count"] for item in results}
            
        except Exception as e:
            logger.error(f"Error getting organizations by status count: {e}")
            return {}
    
    async def get_organizations_by_location_count(self) -> Dict[str, Dict[str, int]]:
        """Get count of organizations by location (country, state, city)"""
        try:
            # Count by country
            country_pipeline = [
                {"$match": {"is_deleted": {"$ne": True}}},
                {"$group": {"_id": "$address.country", "count": {"$sum": 1}}}
            ]
            country_results = await self.organizations_collection.aggregate(country_pipeline).to_list(length=None)
            
            # Count by state
            state_pipeline = [
                {"$match": {"is_deleted": {"$ne": True}}},
                {"$group": {"_id": "$address.state", "count": {"$sum": 1}}}
            ]
            state_results = await self.organizations_collection.aggregate(state_pipeline).to_list(length=None)
            
            # Count by city
            city_pipeline = [
                {"$match": {"is_deleted": {"$ne": True}}},
                {"$group": {"_id": "$address.city", "count": {"$sum": 1}}}
            ]
            city_results = await self.organizations_collection.aggregate(city_pipeline).to_list(length=None)
            
            return {
                "by_country": {item["_id"]: item["count"] for item in country_results if item["_id"]},
                "by_state": {item["_id"]: item["count"] for item in state_results if item["_id"]},
                "by_city": {item["_id"]: item["count"] for item in city_results if item["_id"]}
            }
            
        except Exception as e:
            logger.error(f"Error getting organizations by location count: {e}")
            return {"by_country": {}, "by_state": {}, "by_city": {}}
    
    async def get_capacity_utilization_stats(self) -> Dict[str, Any]:
        """Get capacity utilization statistics"""
        try:
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
                        "organizations_count": {"$sum": 1}
                    }
                }
            ]
            
            result = await self.organizations_collection.aggregate(pipeline).to_list(length=1)
            
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
                    "total_organizations": stats.get("organizations_count", 0)
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
                "total_organizations": 0
            }
            
        except Exception as e:
            logger.error(f"Error getting capacity utilization stats: {e}")
            return {}
    
    async def get_growth_trends(self, months: int = 12) -> Dict[str, Any]:
        """Get organization growth trends over specified months"""
        try:
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
            
            results = await self.organizations_collection.aggregate(pipeline).to_list(length=None)
            
            monthly_data = []
            total_growth = 0
            
            for result in results:
                month_key = f"{result['_id']['year']}-{result['_id']['month']:02d}"
                count = result["count"]
                capacity = result["total_capacity"]
                
                monthly_data.append({
                    "period": month_key,
                    "new_organizations": count,
                    "total_capacity_added": capacity
                })
                
                total_growth += count
            
            # Calculate growth rate
            if len(monthly_data) > 1:
                first_month = monthly_data[0]["new_organizations"]
                last_month = monthly_data[-1]["new_organizations"]
                growth_rate = ((last_month - first_month) / max(first_month, 1)) * 100
            else:
                growth_rate = 0.0
            
            return {
                "period_months": months,
                "monthly_data": monthly_data,
                "total_new_organizations": total_growth,
                "average_monthly_growth": round(total_growth / max(months, 1), 2),
                "growth_rate_percentage": round(growth_rate, 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting growth trends: {e}")
            return {}
    
    async def get_top_organizations_by_capacity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top organizations by employee capacity"""
        try:
            pipeline = [
                {"$match": {"is_deleted": {"$ne": True}}},
                {
                    "$project": {
                        "name": 1,
                        "organization_type": 1,
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
            
            results = await self.organizations_collection.aggregate(pipeline).to_list(length=limit)
            
            top_organizations = []
            for i, result in enumerate(results, 1):
                top_organizations.append({
                    "rank": i,
                    "name": result.get("name", "Unknown"),
                    "organization_type": result.get("organization_type", "Unknown"),
                    "employee_capacity": result.get("employee_strength", 0),
                    "employees_used": result.get("used_employee_strength", 0),
                    "available_capacity": result.get("employee_strength", 0) - result.get("used_employee_strength", 0),
                    "utilization_rate": round(result.get("utilization_rate", 0), 2)
                })
            
            return top_organizations
            
        except Exception as e:
            logger.error(f"Error getting top organizations by capacity: {e}")
            return []
    
    async def get_organizations_created_in_period(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Organization]:
        """Get organizations created within specified period"""
        try:
            query = {
                "is_deleted": {"$ne": True},
                "created_at": {"$gte": start_date, "$lte": end_date}
            }
            
            cursor = self.organizations_collection.find(query).sort("created_at", DESCENDING)
            documents = await cursor.to_list(length=None)
            
            organizations = []
            for doc in documents:
                org = self._document_to_organization(doc)
                if org:
                    organizations.append(org)
            
            return organizations
            
        except Exception as e:
            logger.error(f"Error getting organizations created in period: {e}")
            return []
    
    # OrganizationHealthRepository Missing Methods
    
    async def perform_health_check(self, organization_id: OrganizationId) -> OrganizationHealthCheckDTO:
        """Perform health check for specific organization"""
        try:
            organization = await self.get_by_id(organization_id)
            
            if not organization:
                return OrganizationHealthCheckDTO(
                    organization_id=organization_id.value,
                    is_healthy=False,
                    health_score=0,
                    issues=["Organization not found"],
                    recommendations=["Verify organization exists"]
                )
            
            # Perform various health checks
            issues = []
            recommendations = []
            health_score = 100
            
            # Check basic data completeness
            if not organization.name:
                issues.append("Missing organization name")
                recommendations.append("Set organization name")
                health_score -= 20
            
            if not organization.description:
                issues.append("Missing organization description")
                recommendations.append("Add organization description")
                health_score -= 5
            
            # Check contact information
            if not organization.contact_info.email:
                issues.append("Missing contact email")
                recommendations.append("Add contact email address")
                health_score -= 15
            
            if not organization.contact_info.phone:
                issues.append("Missing contact phone")
                recommendations.append("Add contact phone number")
                health_score -= 10
            
            # Check address completeness
            if not organization.address.city or not organization.address.state:
                issues.append("Incomplete address information")
                recommendations.append("Complete address details")
                health_score -= 10
            
            # Check tax information
            if not organization.tax_info.pan_number:
                issues.append("Missing PAN number")
                recommendations.append("Add PAN number for tax compliance")
                health_score -= 15
            
            # Check capacity utilization
            if organization.employee_strength > 0:
                utilization = (organization.used_employee_strength / organization.employee_strength) * 100
                if utilization > 95:
                    issues.append("Organization near capacity limit")
                    recommendations.append("Consider increasing employee capacity")
                    health_score -= 5
                elif utilization < 20:
                    issues.append("Low capacity utilization")
                    recommendations.append("Review capacity planning")
                    health_score -= 3
            
            # Check status
            if organization.status.value == "inactive":
                issues.append("Organization is inactive")
                recommendations.append("Review organization status")
                health_score -= 25
            elif organization.status.value == "suspended":
                issues.append("Organization is suspended")
                recommendations.append("Resolve suspension issues")
                health_score -= 40
            
            is_healthy = health_score >= 80 and len(issues) == 0
            
            return OrganizationHealthCheckDTO(
                organization_id=organization_id.value,
                organization_name=organization.name,
                is_healthy=is_healthy,
                health_score=max(0, health_score),
                issues=issues,
                recommendations=recommendations,
                last_checked=datetime.utcnow(),
                capacity_utilization=round(
                    (organization.used_employee_strength / max(organization.employee_strength, 1)) * 100, 2
                )
            )
            
        except Exception as e:
            logger.error(f"Error performing health check for {organization_id}: {e}")
            return OrganizationHealthCheckDTO(
                organization_id=organization_id.value,
                is_healthy=False,
                health_score=0,
                issues=["Health check failed"],
                recommendations=["Contact system administrator"]
            )
    
    async def get_unhealthy_organizations(self) -> List[OrganizationHealthCheckDTO]:
        """Get all organizations with health issues"""
        try:
            # Get all active organizations
            query = {"is_deleted": {"$ne": True}, "status": {"$ne": "suspended"}}
            cursor = self.organizations_collection.find(query)
            documents = await cursor.to_list(length=None)
            
            unhealthy_orgs = []
            
            for doc in documents:
                org_id = OrganizationId.from_string(doc["organization_id"])
                health_check = await self.perform_health_check(org_id)
                
                if not health_check.is_healthy or health_check.health_score < 80:
                    unhealthy_orgs.append(health_check)
            
            # Sort by health score (worst first)
            unhealthy_orgs.sort(key=lambda x: x.health_score)
            
            return unhealthy_orgs
            
        except Exception as e:
            logger.error(f"Error getting unhealthy organizations: {e}")
            return []
    
    async def get_organizations_needing_attention(self) -> List[OrganizationHealthCheckDTO]:
        """Get organizations that need immediate attention"""
        try:
            # Get organizations with severe issues
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
            
            cursor = self.organizations_collection.find(query)
            documents = await cursor.to_list(length=None)
            
            attention_needed = []
            
            for doc in documents:
                org_id = OrganizationId.from_string(doc["organization_id"])
                health_check = await self.perform_health_check(org_id)
                attention_needed.append(health_check)
            
            # Sort by severity (lowest health score first)
            attention_needed.sort(key=lambda x: x.health_score)
            
            return attention_needed
            
        except Exception as e:
            logger.error(f"Error getting organizations needing attention: {e}")
            return []
    
    # OrganizationBulkOperationsRepository Missing Methods
    
    async def bulk_update_status(
        self, 
        organization_ids: List[OrganizationId], 
        status: OrganizationStatus,
        updated_by: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Bulk update organization status"""
        try:
            ids = [org_id.value for org_id in organization_ids]
            
            update_data = {
                "status": status.value,
                "updated_at": datetime.utcnow(),
                "updated_by": updated_by
            }
            
            if reason:
                update_data["status_change_reason"] = reason
            
            result = await self.organizations_collection.update_many(
                {"organization_id": {"$in": ids}, "is_deleted": {"$ne": True}},
                {"$set": update_data}
            )
            
            return {
                "total_requested": len(organization_ids),
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
                "total_requested": len(organization_ids),
                "updated_count": 0,
                "success": False,
                "error": str(e)
            }
    
    async def bulk_update_employee_strength(
        self, 
        updates: Dict[OrganizationId, int],
        updated_by: str
    ) -> Dict[str, Any]:
        """Bulk update employee strength for multiple organizations"""
        try:
            updated_count = 0
            failed_updates = []
            
            for org_id, new_strength in updates.items():
                try:
                    result = await self.organizations_collection.update_one(
                        {"organization_id": org_id.value, "is_deleted": {"$ne": True}},
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
                "failed_organization_ids": failed_updates,
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
        organization_ids: Optional[List[OrganizationId]] = None,
        format: str = "csv"
    ) -> bytes:
        """Export organizations data in specified format"""
        try:
            # Build query
            query = {"is_deleted": {"$ne": True}}
            if organization_ids:
                ids = [org_id.value for org_id in organization_ids]
                query["organization_id"] = {"$in": ids}
            
            # Get organizations
            cursor = self.organizations_collection.find(query)
            documents = await cursor.to_list(length=None)
            
            if format.lower() == "csv":
                import io
                import csv
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Write header
                writer.writerow([
                    'Organization ID', 'Name', 'Type', 'Status', 'Hostname',
                    'Email', 'Phone', 'City', 'State', 'Country', 'PAN Number',
                    'Employee Strength', 'Used Strength', 'Created At'
                ])
                
                # Write data
                for doc in documents:
                    writer.writerow([
                        doc.get('organization_id', ''),
                        doc.get('name', ''),
                        doc.get('organization_type', ''),
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
        created_by: str = "system"
    ) -> Dict[str, Any]:
        """Import organizations from data"""
        try:
            imported_count = 0
            failed_imports = []
            
            if format.lower() == "csv":
                import io
                import csv
                
                data_str = data.decode('utf-8')
                reader = csv.DictReader(io.StringIO(data_str))
                
                for row in reader:
                    try:
                        # Create organization from CSV row
                        org_data = {
                            "organization_id": row.get('Organization ID') or str(ObjectId()),
                            "name": row.get('Name', ''),
                            "organization_type": row.get('Type', 'company'),
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
                        
                        # Insert organization
                        await self.organizations_collection.insert_one(org_data)
                        imported_count += 1
                        
                    except Exception as row_error:
                        logger.error(f"Error importing row: {row_error}")
                        failed_imports.append(f"Row {reader.line_num}: {str(row_error)}")
            
            elif format.lower() == "json":
                import json
                
                data_str = data.decode('utf-8')
                organizations_data = json.loads(data_str)
                
                for org_data in organizations_data:
                    try:
                        # Ensure required fields
                        if 'organization_id' not in org_data:
                            org_data['organization_id'] = str(ObjectId())
                        
                        org_data.update({
                            "created_at": datetime.utcnow(),
                            "updated_at": datetime.utcnow(),
                            "created_by": created_by,
                            "is_deleted": False
                        })
                        
                        await self.organizations_collection.insert_one(org_data)
                        imported_count += 1
                        
                    except Exception as org_error:
                        logger.error(f"Error importing organization: {org_error}")
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
    
    # Factory Methods
    
    def create_command_repository(self) -> OrganizationCommandRepository:
        """Create command repository instance"""
        return self
    
    def create_query_repository(self) -> OrganizationQueryRepository:
        """Create query repository instance"""
        return self
    
    def create_analytics_repository(self) -> OrganizationAnalyticsRepository:
        """Create analytics repository instance"""
        return self
    
    def create_health_repository(self) -> OrganizationHealthRepository:
        """Create health repository instance"""
        return self
    
    def create_bulk_operations_repository(self) -> OrganizationBulkOperationsRepository:
        """Create bulk operations repository instance"""
        return self
    
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