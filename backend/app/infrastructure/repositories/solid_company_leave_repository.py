"""
SOLID-Compliant Company Leave Repository Implementation
Replaces the procedural company_leave_database.py with proper SOLID architecture
"""

import logging
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import uuid
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

# Import domain entities
try:
    from app.domain.entities.company_leave import CompanyLeave
    from app.domain.value_objects.company_leave_id import CompanyLeaveId
    from models.company_leave import CompanyLeaveCreate, CompanyLeaveUpdate
except ImportError:
    # Fallback classes for migration compatibility
    class CompanyLeave:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        def dict(self):
            return {k: v for k, v in self.__dict__.items()}
        def model_dump(self):
            return {k: v for k, v in self.__dict__.items()}
    
    class CompanyLeaveId:
        def __init__(self, value: str):
            self.value = value
        def __str__(self):
            return self.value
    
    class CompanyLeaveCreate:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        def dict(self):
            return {k: v for k, v in self.__dict__.items()}
    
    class CompanyLeaveUpdate:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        def dict(self):
            return {k: v for k, v in self.__dict__.items()}

# Import application interfaces
try:
    from app.application.interfaces.repositories.company_leave_repository import (
        CompanyLeaveCommandRepository, CompanyLeaveQueryRepository,
        CompanyLeaveAnalyticsRepository, CompanyLeaveRepository
    )
except ImportError:
    # Fallback interfaces
    from abc import ABC, abstractmethod
    
    class CompanyLeaveCommandRepository(ABC):
        pass
    
    class CompanyLeaveQueryRepository(ABC):
        pass
    
    class CompanyLeaveAnalyticsRepository(ABC):
        pass
    
    class CompanyLeaveRepository(ABC):
        pass

# Import DTOs
try:
    from app.application.dto.company_leave_dto import (
        CompanyLeaveSearchFiltersDTO, CompanyLeaveStatisticsDTO
    )
except ImportError:
    # Fallback DTOs
    class CompanyLeaveSearchFiltersDTO:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class CompanyLeaveStatisticsDTO:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

from .base_repository import BaseRepository
from ..database.database_connector import DatabaseConnector

logger = logging.getLogger(__name__)


class SolidCompanyLeaveRepository(
    BaseRepository[CompanyLeave],
    CompanyLeaveCommandRepository,
    CompanyLeaveQueryRepository,
    CompanyLeaveAnalyticsRepository,
    CompanyLeaveRepository
):
    """
    SOLID-compliant company leave repository implementation.
    
    Replaces the procedural company_leave_database.py with proper SOLID architecture:
    - Single Responsibility: Only handles company leave data persistence
    - Open/Closed: Can be extended without modification
    - Liskov Substitution: Implements all company leave repository interfaces
    - Interface Segregation: Implements focused company leave repository interfaces
    - Dependency Inversion: Depends on DatabaseConnector abstraction
    """
    
    def __init__(self, database_connector: DatabaseConnector):
        """
        Initialize company leave repository.
        
        Args:
            database_connector: Database connection abstraction
        """
        super().__init__(database_connector, "company_leaves")
        
    def _entity_to_document(self, leave: CompanyLeave) -> Dict[str, Any]:
        """
        Convert CompanyLeave entity to database document.
        
        Args:
            leave: CompanyLeave entity to convert
            
        Returns:
            Database document representation
        """
        if hasattr(leave, 'model_dump'):
            document = leave.model_dump()
        elif hasattr(leave, 'dict'):
            document = leave.dict()
        else:
            document = {k: v for k, v in leave.__dict__.items()}
        
        # Remove the 'id' field if present (MongoDB uses '_id')
        if 'id' in document:
            del document['id']
        
        # Ensure proper field mapping for legacy compatibility
        if 'company_leave_id' not in document and hasattr(leave, 'company_leave_id'):
            document['company_leave_id'] = getattr(leave, 'company_leave_id')
        
        # Set default values
        if 'is_active' not in document:
            document['is_active'] = True
        
        return document
    
    def _document_to_entity(self, document: Dict[str, Any]) -> CompanyLeave:
        """
        Convert database document to CompanyLeave entity.
        
        Args:
            document: Database document to convert
            
        Returns:
            CompanyLeave entity instance
        """
        # Convert MongoDB _id to id
        if '_id' in document:
            document['id'] = str(document['_id'])
            del document['_id']
        
        return CompanyLeave(**document)
    
    async def _ensure_indexes(self, organization_id: str) -> None:
        """Ensure necessary indexes for optimal query performance."""
        try:
            collection = self._get_collection(organization_id)
            
            # Index for company_leave_id queries
            await collection.create_index([
                ("company_leave_id", 1)
            ], unique=True)
            
            # Index for name queries
            await collection.create_index([
                ("name", 1)
            ])
            
            # Index for active leaves
            await collection.create_index([
                ("is_active", 1),
                ("name", 1)
            ])
            
            # Index for count queries
            await collection.create_index([
                ("count", 1)
            ])
            
            # Index for created_at queries
            await collection.create_index([
                ("created_at", -1)
            ])
            
            logger.info(f"Company leave indexes ensured for organization: {organization_id}")
            
        except Exception as e:
            logger.error(f"Error ensuring company leave indexes: {e}")
    
    # Command Repository Implementation
    async def save(self, leave: CompanyLeave) -> CompanyLeave:
        """
        Save company leave record.
        
        Replaces: create_leave() function
        """
        try:
            # Get organization from leave or use default
            organization_id = getattr(leave, 'organization_id', 'default')
            
            # Ensure indexes
            await self._ensure_indexes(organization_id)
            
            # Prepare document
            document = self._entity_to_document(leave)
            
            # Set timestamps
            if not document.get('created_at'):
                document['created_at'] = datetime.now()
            document['updated_at'] = datetime.now()
            
            # Generate company_leave_id if not present
            if not document.get('company_leave_id'):
                document['company_leave_id'] = str(uuid.uuid4())
            
            # Check for existing record by company_leave_id
            existing = None
            if document.get('company_leave_id'):
                existing = await self.get_by_id(document['company_leave_id'], organization_id)
            
            if existing:
                # Update existing record
                filters = {"company_leave_id": document['company_leave_id']}
                success = await self._update_document(
                    filters=filters,
                    update_data=document,
                    organization_id=organization_id
                )
                if success:
                    return await self.get_by_id(document['company_leave_id'], organization_id)
                else:
                    raise ValueError("Failed to update company leave record")
            else:
                # Insert new record
                document_id = await self._insert_document(document, organization_id)
                # Return the saved document
                saved_doc = await self._get_collection(organization_id).find_one({"_id": document_id})
                return self._document_to_entity(saved_doc)
            
        except Exception as e:
            logger.error(f"Error saving company leave: {e}")
            raise
    
    async def update(self, leave_id: str, update_data: Dict[str, Any], 
                    organization_id: str) -> bool:
        """
        Update company leave record.
        
        Replaces: update_leave() function
        """
        try:
            # Filter out empty fields
            filtered_update_data = {}
            for key, value in update_data.items():
                if value is not None and value != "":
                    filtered_update_data[key] = value
            
            if not filtered_update_data:
                return False
            
            # Add updated timestamp
            filtered_update_data['updated_at'] = datetime.now()
            
            filters = {"company_leave_id": leave_id}
            
            success = await self._update_document(
                filters=filters,
                update_data=filtered_update_data,
                organization_id=organization_id
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating company leave {leave_id}: {e}")
            return False
    
    async def delete(self, leave_id: str, organization_id: str) -> bool:
        """
        Delete company leave record (soft delete).
        
        Replaces: delete_leave() function
        """
        try:
            # Soft delete by setting is_active to False
            update_data = {
                "is_active": False,
                "updated_at": datetime.now()
            }
            
            return await self.update(leave_id, update_data, organization_id)
            
        except Exception as e:
            logger.error(f"Error deleting company leave {leave_id}: {e}")
            return False
    
    # Query Repository Implementation
    async def get_by_id(self, leave_id: str, organization_id: str = "default") -> Optional[CompanyLeave]:
        """Get company leave record by ID."""
        try:
            filters = {"company_leave_id": leave_id, "is_active": True}
            
            documents = await self._execute_query(
                filters=filters,
                limit=1,
                organization_id=organization_id
            )
            
            if documents:
                return self._document_to_entity(documents[0])
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving company leave {leave_id}: {e}")
            return None
    
    async def get_all_active(self, organization_id: str = "default") -> List[CompanyLeave]:
        """
        Get all active company leaves.
        
        Replaces: get_all_leaves() function
        """
        try:
            filters = {"is_active": True}
            
            documents = await self._execute_query(
                filters=filters,
                sort_by="name",
                sort_order=1,
                limit=100,
                organization_id=organization_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error retrieving all active company leaves: {e}")
            return []
    
    async def get_by_name(self, name: str, organization_id: str = "default") -> Optional[CompanyLeave]:
        """Get company leave by name."""
        try:
            filters = {"name": name, "is_active": True}
            
            documents = await self._execute_query(
                filters=filters,
                limit=1,
                organization_id=organization_id
            )
            
            if documents:
                return self._document_to_entity(documents[0])
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving company leave by name {name}: {e}")
            return None
    
    async def get_by_count_range(self, min_count: int, max_count: int,
                                organization_id: str = "default") -> List[CompanyLeave]:
        """Get company leaves within a count range."""
        try:
            filters = {
                "count": {"$gte": min_count, "$lte": max_count},
                "is_active": True
            }
            
            documents = await self._execute_query(
                filters=filters,
                sort_by="count",
                sort_order=1,
                limit=50,
                organization_id=organization_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error retrieving company leaves by count range: {e}")
            return []
    
    async def search(self, filters: CompanyLeaveSearchFiltersDTO,
                    organization_id: str = "default") -> List[CompanyLeave]:
        """Search company leaves with filters."""
        try:
            query_filters = {"is_active": True}
            
            if hasattr(filters, 'name') and filters.name:
                query_filters["name"] = {"$regex": filters.name, "$options": "i"}
            
            if hasattr(filters, 'min_count') and filters.min_count is not None:
                query_filters["count"] = {"$gte": filters.min_count}
            
            if hasattr(filters, 'max_count') and filters.max_count is not None:
                if "count" in query_filters:
                    query_filters["count"]["$lte"] = filters.max_count
                else:
                    query_filters["count"] = {"$lte": filters.max_count}
            
            if hasattr(filters, 'is_active') and filters.is_active is not None:
                query_filters["is_active"] = filters.is_active
            
            # Get pagination parameters
            page = getattr(filters, 'page', 1)
            page_size = getattr(filters, 'page_size', 50)
            skip = (page - 1) * page_size
            
            documents = await self._execute_query(
                filters=query_filters,
                skip=skip,
                limit=page_size,
                sort_by="name",
                sort_order=1,
                organization_id=organization_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error searching company leaves: {e}")
            return []
    
    async def count_by_filters(self, filters: CompanyLeaveSearchFiltersDTO,
                              organization_id: str = "default") -> int:
        """Count company leaves matching filters."""
        try:
            query_filters = {"is_active": True}
            
            if hasattr(filters, 'name') and filters.name:
                query_filters["name"] = {"$regex": filters.name, "$options": "i"}
            
            if hasattr(filters, 'is_active') and filters.is_active is not None:
                query_filters["is_active"] = filters.is_active
            
            return await self._count_documents(query_filters, organization_id)
            
        except Exception as e:
            logger.error(f"Error counting company leaves: {e}")
            return 0
    
    # Analytics Repository Implementation
    async def get_leave_statistics(self, organization_id: str = "default") -> Dict[str, Any]:
        """Get company leave statistics."""
        try:
            # Use aggregation pipeline for statistics
            pipeline = [
                {"$match": {"is_active": True}},
                {
                    "$group": {
                        "_id": None,
                        "total_leaves": {"$sum": 1},
                        "total_count": {"$sum": "$count"},
                        "average_count": {"$avg": "$count"},
                        "min_count": {"$min": "$count"},
                        "max_count": {"$max": "$count"},
                        "leave_types": {
                            "$push": {
                                "name": "$name",
                                "count": "$count"
                            }
                        }
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "total_leaves": 1,
                        "total_count": 1,
                        "average_count": 1,
                        "min_count": 1,
                        "max_count": 1,
                        "leave_types": 1
                    }
                }
            ]
            
            results = await self._aggregate(pipeline, organization_id)
            
            if results:
                stats = results[0]
                return {
                    "total_leave_types": stats.get("total_leaves", 0),
                    "total_leave_count": stats.get("total_count", 0),
                    "average_leave_count": stats.get("average_count", 0),
                    "min_leave_count": stats.get("min_count", 0),
                    "max_leave_count": stats.get("max_count", 0),
                    "leave_types": stats.get("leave_types", [])
                }
            else:
                return {
                    "total_leave_types": 0,
                    "total_leave_count": 0,
                    "average_leave_count": 0,
                    "min_leave_count": 0,
                    "max_leave_count": 0,
                    "leave_types": []
                }
                
        except Exception as e:
            logger.error(f"Error getting company leave statistics: {e}")
            return {}
    
    async def get_leave_distribution(self, organization_id: str = "default") -> Dict[str, Any]:
        """Get leave count distribution."""
        try:
            pipeline = [
                {"$match": {"is_active": True}},
                {
                    "$group": {
                        "_id": "$count",
                        "leave_types": {"$sum": 1},
                        "names": {"$push": "$name"}
                    }
                },
                {
                    "$sort": {"_id": 1}
                },
                {
                    "$project": {
                        "count": "$_id",
                        "leave_types": 1,
                        "names": 1,
                        "_id": 0
                    }
                }
            ]
            
            results = await self._aggregate(pipeline, organization_id)
            
            distribution = {}
            for result in results:
                count = result["count"]
                distribution[count] = {
                    "leave_types": result["leave_types"],
                    "names": result["names"]
                }
            
            return distribution
            
        except Exception as e:
            logger.error(f"Error getting leave distribution: {e}")
            return {}
    
    # Legacy compatibility methods
    async def create_leave_legacy(self, leave_data: dict, hostname: str) -> str:
        """
        Legacy compatibility for create_leave() function.
        
        Args:
            leave_data: Company leave data dictionary
            hostname: Organization hostname
            
        Returns:
            Company leave ID
        """
        try:
            # Convert dict to CompanyLeave entity
            leave = CompanyLeave(**leave_data)
            
            # Save using new method
            saved_leave = await self.save(leave)
            
            return getattr(saved_leave, 'company_leave_id', '')
            
        except Exception as e:
            logger.error(f"Error creating company leave (legacy): {e}")
            raise
    
    async def get_all_leaves_legacy(self, hostname: str) -> List[Dict[str, Any]]:
        """
        Legacy compatibility for get_all_leaves() function.
        
        Args:
            hostname: Organization hostname
            
        Returns:
            List of company leave documents
        """
        try:
            leaves = await self.get_all_active(hostname)
            
            # Convert to legacy document format
            legacy_leaves = []
            for leave in leaves:
                legacy_data = {
                    "company_leave_id": getattr(leave, 'company_leave_id', ''),
                    "name": getattr(leave, 'name', ''),
                    "count": getattr(leave, 'count', 0),
                    "is_active": getattr(leave, 'is_active', True),
                    "created_at": getattr(leave, 'created_at', None),
                    "updated_at": getattr(leave, 'updated_at', None)
                }
                legacy_leaves.append(legacy_data)
            
            return legacy_leaves
            
        except Exception as e:
            logger.error(f"Error getting all leaves (legacy): {e}")
            return []
    
    async def get_leave_by_id_legacy(self, leave_id: str, hostname: str) -> Optional[Dict[str, Any]]:
        """
        Legacy compatibility for get_leave_by_id() function.
        
        Args:
            leave_id: Company leave ID
            hostname: Organization hostname
            
        Returns:
            Company leave document or None
        """
        try:
            leave = await self.get_by_id(leave_id, hostname)
            
            if leave:
                return {
                    "company_leave_id": getattr(leave, 'company_leave_id', ''),
                    "name": getattr(leave, 'name', ''),
                    "count": getattr(leave, 'count', 0),
                    "is_active": getattr(leave, 'is_active', True),
                    "created_at": getattr(leave, 'created_at', None),
                    "updated_at": getattr(leave, 'updated_at', None)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting leave by ID (legacy): {e}")
            return None
    
    async def update_leave_legacy(self, leave_id: str, leave_data: dict, hostname: str) -> bool:
        """
        Legacy compatibility for update_leave() function.
        
        Args:
            leave_id: Company leave ID
            leave_data: Update data dictionary
            hostname: Organization hostname
            
        Returns:
            True if updated, False otherwise
        """
        try:
            return await self.update(leave_id, leave_data, hostname)
            
        except Exception as e:
            logger.error(f"Error updating leave (legacy): {e}")
            return False
    
    async def delete_leave_legacy(self, leave_id: str, hostname: str) -> bool:
        """
        Legacy compatibility for delete_leave() function.
        
        Args:
            leave_id: Company leave identifier
            hostname: Organization hostname
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            return await self.delete(leave_id, hostname)
            
        except Exception as e:
            logger.error(f"Error deleting company leave (legacy): {e}")
            return False

    # ==================== MISSING ABSTRACT METHODS IMPLEMENTATION ====================
    
    # CompanyLeaveQueryRepository Missing Methods
    
    async def count_active(self, organization_id: str = "default") -> int:
        """Count active company leaves."""
        try:
            filters = {"is_active": True}
            return await self._count_documents(filters, organization_id)
            
        except Exception as e:
            logger.error(f"Error counting active company leaves: {e}")
            return 0
    
    async def exists_by_leave_type_code(self, leave_type_code: str, organization_id: str = "default") -> bool:
        """Check if company leave exists for leave type code."""
        try:
            filters = {"leave_type_code": leave_type_code}
            count = await self._count_documents(filters, organization_id)
            return count > 0
            
        except Exception as e:
            logger.error(f"Error checking leave type code existence: {e}")
            return False
    
    async def get_all(self, include_inactive: bool = False, organization_id: str = "default") -> List[CompanyLeave]:
        """Get all company leaves."""
        try:
            filters = {}
            
            if not include_inactive:
                filters["is_active"] = True
            
            documents = await self._execute_query(
                filters=filters,
                sort_by="name",
                sort_order=1,
                limit=100,
                organization_id=organization_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting all company leaves: {e}")
            return []
    
    async def get_applicable_for_employee(
        self,
        employee_gender: Optional[str] = None,
        employee_category: Optional[str] = None,
        is_on_probation: bool = False,
        organization_id: str = "default"
    ) -> List[CompanyLeave]:
        """Get company leaves applicable for employee."""
        try:
            filters = {"is_active": True}
            
            # Build query based on employee characteristics
            if employee_gender:
                filters["$or"] = [
                    {"applicable_gender": {"$in": [employee_gender, "all", None]}},
                    {"applicable_gender": {"$exists": False}}
                ]
            
            if employee_category:
                if "$and" not in filters:
                    filters["$and"] = []
                filters["$and"].append({
                    "$or": [
                        {"applicable_category": {"$in": [employee_category, "all", None]}},
                        {"applicable_category": {"$exists": False}}
                    ]
                })
            
            if is_on_probation:
                # Exclude leaves that don't allow probation employees
                if "$and" not in filters:
                    filters["$and"] = []
                filters["$and"].append({
                    "$or": [
                        {"allow_probation": True},
                        {"allow_probation": {"$exists": False}}
                    ]
                })
            
            documents = await self._execute_query(
                filters=filters,
                sort_by="name",
                sort_order=1,
                limit=50,
                organization_id=organization_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting applicable company leaves: {e}")
            return []
    
    async def get_by_leave_type_code(self, leave_type_code: str, organization_id: str = "default") -> Optional[CompanyLeave]:
        """Get company leave by leave type code."""
        try:
            filters = {"leave_type_code": leave_type_code}
            documents = await self._execute_query(
                filters=filters,
                limit=1,
                organization_id=organization_id
            )
            
            if documents:
                return self._document_to_entity(documents[0])
            return None
            
        except Exception as e:
            logger.error(f"Error getting company leave by leave type code {leave_type_code}: {e}")
            return None
    
    # CompanyLeaveAnalyticsRepository Missing Methods
    
    async def get_leave_trends(
        self,
        period: str = "monthly",
        organization_id: str = "default"
    ) -> List[Dict[str, Any]]:
        """Get leave application trends."""
        try:
            # This would typically analyze actual leave applications, but since this is a company leave
            # repository (which defines leave types), we'll provide trend data based on creation/updates
            
            # Build aggregation pipeline based on period
            date_format_map = {
                "daily": "%Y-%m-%d",
                "weekly": "%Y-W%U",
                "monthly": "%Y-%m",
                "quarterly": "%Y-Q"
            }
            
            date_format = date_format_map.get(period, "%Y-%m")
            
            pipeline = [
                {"$match": {"is_active": True}},
                {
                    "$group": {
                        "_id": {
                            "$dateToString": {
                                "format": date_format,
                                "date": {"$toDate": "$created_at"}
                            }
                        },
                        "count": {"$sum": 1},
                        "leave_types": {"$push": "$name"}
                    }
                },
                {"$sort": {"_id": 1}},
                {"$limit": 50}
            ]
            
            results = await self._aggregate(pipeline, organization_id)
            
            trends = []
            for result in results:
                trends.append({
                    "period": result["_id"],
                    "count": result["count"],
                    "leave_types": result["leave_types"]
                })
            
            return trends
            
        except Exception as e:
            logger.error(f"Error getting leave trends: {e}")
            return []
    
    async def get_leave_type_usage_stats(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        organization_id: str = "default"
    ) -> List[Dict[str, Any]]:
        """Get leave type usage statistics."""
        try:
            # Build date filter
            date_filter = {}
            if from_date or to_date:
                date_range = {}
                if from_date:
                    date_range["$gte"] = from_date
                if to_date:
                    date_range["$lte"] = to_date
                date_filter["created_at"] = date_range
            
            # Get all active company leaves
            filters = {"is_active": True, **date_filter}
            documents = await self._execute_query(
                filters=filters,
                sort_by="name",
                sort_order=1,
                organization_id=organization_id
            )
            
            # Calculate usage statistics
            usage_stats = []
            for doc in documents:
                # For each leave type, we'll calculate basic stats
                # In a real system, this would query actual leave applications
                stats = {
                    "leave_type_code": doc.get("leave_type_code", ""),
                    "leave_type_name": doc.get("name", ""),
                    "max_days_allowed": doc.get("count", 0),
                    "is_active": doc.get("is_active", False),
                    "created_at": doc.get("created_at"),
                    # These would be calculated from actual leave applications
                    "total_applications": 0,  # Placeholder
                    "total_days_used": 0,     # Placeholder  
                    "average_days_per_application": 0,  # Placeholder
                    "utilization_rate": 0.0   # Placeholder
                }
                usage_stats.append(stats)
            
            return usage_stats
            
        except Exception as e:
            logger.error(f"Error getting leave type usage stats: {e}")
            return []
    
    async def get_policy_compliance_report(self, organization_id: str = "default") -> List[Dict[str, Any]]:
        """Get policy compliance report."""
        try:
            # Get all company leaves
            documents = await self._execute_query(
                filters={},
                sort_by="name",
                sort_order=1,
                organization_id=organization_id
            )
            
            compliance_report = []
            
            for doc in documents:
                # Check various compliance aspects
                compliance_issues = []
                compliance_score = 100
                
                # Check if leave type has proper configuration
                if not doc.get("name"):
                    compliance_issues.append("Missing leave type name")
                    compliance_score -= 20
                
                if not doc.get("leave_type_code"):
                    compliance_issues.append("Missing leave type code")
                    compliance_score -= 15
                
                if not doc.get("count") or doc.get("count", 0) <= 0:
                    compliance_issues.append("Invalid or missing maximum days count")
                    compliance_score -= 15
                
                # Check if proper approval workflow is defined
                if not doc.get("requires_approval", True):
                    compliance_issues.append("No approval workflow defined")
                    compliance_score -= 10
                
                # Check if carry forward policy is defined
                if not doc.get("carry_forward_policy"):
                    compliance_issues.append("Carry forward policy not defined")
                    compliance_score -= 10
                
                # Check if proper documentation exists
                if not doc.get("description"):
                    compliance_issues.append("Missing leave type description")
                    compliance_score -= 5
                
                compliance_level = "High"
                if compliance_score < 80:
                    compliance_level = "Medium"
                if compliance_score < 60:
                    compliance_level = "Low"
                
                compliance_report.append({
                    "leave_type_code": doc.get("leave_type_code", ""),
                    "leave_type_name": doc.get("name", ""),
                    "is_active": doc.get("is_active", False),
                    "compliance_score": max(0, compliance_score),
                    "compliance_level": compliance_level,
                    "compliance_issues": compliance_issues,
                    "recommendations": self._generate_compliance_recommendations(compliance_issues),
                    "last_updated": doc.get("updated_at", doc.get("created_at"))
                })
            
            return compliance_report
            
        except Exception as e:
            logger.error(f"Error getting policy compliance report: {e}")
            return []
    
    def _generate_compliance_recommendations(self, issues: List[str]) -> List[str]:
        """Generate compliance recommendations based on issues."""
        recommendations = []
        
        if "Missing leave type name" in issues:
            recommendations.append("Add a clear and descriptive name for the leave type")
        
        if "Missing leave type code" in issues:
            recommendations.append("Define a unique code for the leave type (e.g., CL, SL, PL)")
        
        if "Invalid or missing maximum days count" in issues:
            recommendations.append("Set appropriate maximum days allowed for this leave type")
        
        if "No approval workflow defined" in issues:
            recommendations.append("Configure approval workflow and authorization levels")
        
        if "Carry forward policy not defined" in issues:
            recommendations.append("Define policy for carrying forward unused leave days")
        
        if "Missing leave type description" in issues:
            recommendations.append("Add detailed description of leave type eligibility and usage")
        
        return recommendations 