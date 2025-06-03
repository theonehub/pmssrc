"""
SOLID-Compliant Employee Leave Repository Implementation
Replaces the procedural employee_leave_database.py with proper SOLID architecture
"""

import logging
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date, timedelta
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

# Import domain entities
try:
    from app.domain.entities.employee_leave import EmployeeLeave
    from app.domain.value_objects.employee_id import EmployeeId
    from app.domain.value_objects.leave_type import LeaveType
    from app.domain.value_objects.date_range import DateRange
    from models.leave_model import LeaveStatus
except ImportError:
    # Fallback classes for migration compatibility
    class EmployeeLeave:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        def dict(self):
            return {k: v for k, v in self.__dict__.items()}
        def model_dump(self):
            return {k: v for k, v in self.__dict__.items()}
    
    class EmployeeId:
        def __init__(self, value: str):
            self.value = value
        def __str__(self):
            return self.value
    
    class LeaveType:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class DateRange:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class LeaveStatus:
        PENDING = "pending"
        APPROVED = "approved"
        REJECTED = "rejected"
        CANCELLED = "cancelled"

# Import application interfaces
try:
    from app.application.interfaces.repositories.employee_leave_repository import (
        EmployeeLeaveCommandRepository, EmployeeLeaveQueryRepository,
        EmployeeLeaveAnalyticsRepository, EmployeeLeaveRepository
    )
except ImportError:
    # Fallback interfaces
    from abc import ABC, abstractmethod
    
    class EmployeeLeaveCommandRepository(ABC):
        pass
    
    class EmployeeLeaveQueryRepository(ABC):
        pass
    
    class EmployeeLeaveAnalyticsRepository(ABC):
        pass
    
    class EmployeeLeaveRepository(ABC):
        pass

# Import DTOs
try:
    from app.application.dto.employee_leave_dto import (
        EmployeeLeaveSearchFiltersDTO, EmployeeLeaveSummaryDTO,
        EmployeeLeaveStatisticsDTO
    )
except ImportError:
    # Fallback DTOs
    class EmployeeLeaveSearchFiltersDTO:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class EmployeeLeaveSummaryDTO:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class EmployeeLeaveStatisticsDTO:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

from .base_repository import BaseRepository
from ..database.database_connector import DatabaseConnector

logger = logging.getLogger(__name__)


class SolidEmployeeLeaveRepository(
    BaseRepository[EmployeeLeave],
    EmployeeLeaveCommandRepository,
    EmployeeLeaveQueryRepository,
    EmployeeLeaveAnalyticsRepository,
    EmployeeLeaveRepository
):
    """
    SOLID-compliant employee leave repository implementation.
    
    Replaces the procedural employee_leave_database.py with proper SOLID architecture:
    - Single Responsibility: Only handles employee leave data persistence
    - Open/Closed: Can be extended without modification
    - Liskov Substitution: Implements all employee leave repository interfaces
    - Interface Segregation: Implements focused employee leave repository interfaces
    - Dependency Inversion: Depends on DatabaseConnector abstraction
    """
    
    def __init__(self, database_connector: DatabaseConnector):
        """
        Initialize employee leave repository.
        
        Args:
            database_connector: Database connection abstraction
        """
        super().__init__(database_connector, "employee_leave")
        
    def _entity_to_document(self, leave: EmployeeLeave) -> Dict[str, Any]:
        """
        Convert EmployeeLeave entity to database document.
        
        Args:
            leave: EmployeeLeave entity to convert
            
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
        if 'leave_id' not in document and hasattr(leave, 'leave_id'):
            document['leave_id'] = getattr(leave, 'leave_id')
        
        if 'employee_id' not in document and hasattr(leave, 'employee_id'):
            employee_id = getattr(leave, 'employee_id')
            if hasattr(employee_id, 'value'):
                document['employee_id'] = employee_id.value
            else:
                document['employee_id'] = str(employee_id)
        
        # Handle date range
        date_range = getattr(leave, 'date_range', None)
        if date_range:
            if hasattr(date_range, 'start_date'):
                document['start_date'] = getattr(date_range, 'start_date')
            if hasattr(date_range, 'end_date'):
                document['end_date'] = getattr(date_range, 'end_date')
        
        # Handle leave type
        leave_type = getattr(leave, 'leave_type', None)
        if leave_type:
            if hasattr(leave_type, 'code'):
                document['leave_name'] = getattr(leave_type, 'code')
            elif hasattr(leave_type, 'name'):
                document['leave_name'] = getattr(leave_type, 'name')
        
        # Convert dates to strings for MongoDB compatibility
        date_fields = ['start_date', 'end_date', 'applied_date', 'approved_date']
        for field in date_fields:
            if field in document and isinstance(document[field], date):
                document[field] = document[field].strftime("%Y-%m-%d")
        
        return document
    
    def _document_to_entity(self, document: Dict[str, Any]) -> EmployeeLeave:
        """
        Convert database document to EmployeeLeave entity.
        
        Args:
            document: Database document to convert
            
        Returns:
            EmployeeLeave entity instance
        """
        # Convert MongoDB _id to id
        if '_id' in document:
            document['id'] = str(document['_id'])
            del document['_id']
        
        # Map legacy fields to new structure
        if 'employee_id' in document and 'employee_id' not in document:
            document['employee_id'] = document['employee_id']
        
        if 'leave_name' in document and 'leave_type' not in document:
            document['leave_type'] = document['leave_name']
        
        # Handle date conversions
        date_fields = ['start_date', 'end_date', 'applied_date', 'approved_date']
        for field in date_fields:
            if field in document and isinstance(document[field], str):
                try:
                    document[field] = datetime.strptime(document[field], "%Y-%m-%d").date()
                except (ValueError, TypeError):
                    pass
        
        return EmployeeLeave(**document)
    
    async def _ensure_indexes(self, organisation_id: str) -> None:
        """Ensure necessary indexes for optimal query performance."""
        try:
            collection = self._get_collection(organisation_id)
            
            # Index for employee queries
            await collection.create_index([
                ("employee_id", 1),
                ("start_date", -1)
            ])
            
            # Index for date range queries
            await collection.create_index([
                ("start_date", 1),
                ("end_date", 1)
            ])
            
            # Index for status queries
            await collection.create_index([
                ("status", 1),
                ("applied_date", -1)
            ])
            
            # Index for manager queries
            await collection.create_index([
                ("manager_id", 1),
                ("status", 1)
            ])
            
            # Unique index for leave_id
            await collection.create_index([
                ("leave_id", 1)
            ], unique=True)
            
            logger.info(f"Employee leave indexes ensured for organisation: {organisation_id}")
            
        except Exception as e:
            logger.error(f"Error ensuring employee leave indexes: {e}")
    
    # Command Repository Implementation
    async def save(self, leave: EmployeeLeave) -> EmployeeLeave:
        """
        Save employee leave record.
        
        Replaces: create_employee_leave() function
        """
        try:
            # Get organisation from leave or use default
            organisation_id = getattr(leave, 'organisation_id', 'default')
            
            # Ensure indexes
            await self._ensure_indexes(organisation_id)
            
            # Prepare document
            document = self._entity_to_document(leave)
            
            # Set timestamps
            if not document.get('created_at'):
                document['created_at'] = datetime.now()
            document['updated_at'] = datetime.now()
            
            # Set created_by if not present
            if not document.get('created_by'):
                document['created_by'] = document.get('employee_id')
            
            # Check for existing record by leave_id
            existing = await self.get_by_id(document.get('leave_id'), organisation_id)
            
            if existing:
                # Update existing record
                filters = {"leave_id": document['leave_id']}
                success = await self._update_document(
                    filters=filters,
                    update_data=document,
                    organisation_id=organisation_id
                )
                if success:
                    return await self.get_by_id(document['leave_id'], organisation_id)
                else:
                    raise ValueError("Failed to update employee leave record")
            else:
                # Insert new record
                document_id = await self._insert_document(document, organisation_id)
                return await self.get_by_id(document.get('leave_id'), organisation_id)
            
        except Exception as e:
            logger.error(f"Error saving employee leave: {e}")
            raise
    
    async def update(self, leave_id: str, update_data: Dict[str, Any], 
                    organisation_id: str) -> bool:
        """
        Update employee leave record.
        
        Replaces: update_employee_leave() function
        """
        try:
            # Add updated timestamp
            update_data['updated_at'] = datetime.now()
            
            # Convert date objects to strings if needed
            date_fields = ['start_date', 'end_date', 'applied_date', 'approved_date']
            for field in date_fields:
                if field in update_data and isinstance(update_data[field], date):
                    update_data[field] = update_data[field].strftime("%Y-%m-%d")
            
            filters = {"leave_id": leave_id}
            success = await self._update_document(
                filters=filters,
                update_data=update_data,
                organisation_id=organisation_id
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating employee leave {leave_id}: {e}")
            return False
    
    async def delete(self, leave_id: str, organisation_id: str) -> bool:
        """
        Delete employee leave record.
        
        Replaces: delete_employee_leave() function
        """
        try:
            filters = {"leave_id": leave_id}
            return await self._delete_document(
                filters=filters,
                organisation_id=organisation_id,
                soft_delete=True
            )
            
        except Exception as e:
            logger.error(f"Error deleting employee leave {leave_id}: {e}")
            return False
    
    # Query Repository Implementation
    async def get_by_id(self, leave_id: str, organisation_id: str = "default") -> Optional[EmployeeLeave]:
        """
        Get employee leave by ID.
        
        Replaces: get_employee_leave_by_id() function
        """
        try:
            filters = {"leave_id": leave_id}
            documents = await self._execute_query(
                filters=filters,
                limit=1,
                organisation_id=organisation_id
            )
            
            if documents:
                return self._document_to_entity(documents[0])
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving employee leave {leave_id}: {e}")
            return None
    
    async def get_by_employee_id(self, employee_id: str, organisation_id: str = "default") -> List[EmployeeLeave]:
        """
        Get all employee leaves for a specific employee.
        
        Replaces: get_employee_leaves_by_employee_id() function
        """
        try:
            filters = {"employee_id": employee_id}
            
            documents = await self._execute_query(
                filters=filters,
                sort_by="start_date",
                sort_order=-1,
                limit=100,
                organisation_id=organisation_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error retrieving employee leaves for {employee_id}: {e}")
            return []
    
    async def get_all(self, organisation_id: str = "default", 
                     employee_ids: Optional[List[str]] = None) -> List[EmployeeLeave]:
        """
        Get all employee leaves.
        
        Replaces: get_all_employee_leaves() function
        """
        try:
            filters = {}
            
            if employee_ids:
                filters["employee_id"] = {"$in": employee_ids}
            
            documents = await self._execute_query(
                filters=filters,
                sort_by="start_date",
                sort_order=-1,
                limit=1000,
                organisation_id=organisation_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error retrieving all employee leaves: {e}")
            return []
    
    async def get_by_manager_id(self, manager_id: str, 
                               organisation_id: str = "default") -> List[EmployeeLeave]:
        """
        Get all employee leaves for a specific manager.
        
        Replaces: get_employee_leaves_by_manager_id() function
        """
        try:
            filters = {"manager_id": manager_id}
            
            documents = await self._execute_query(
                filters=filters,
                sort_by="applied_date",
                sort_order=-1,
                limit=100,
                organisation_id=organisation_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error retrieving employee leaves for manager {manager_id}: {e}")
            return []
    
    async def get_by_employee_and_month(self, employee_id: str, year: int, month: int,
                                       organisation_id: str = "default") -> List[EmployeeLeave]:
        """
        Get employee leaves for a specific month.
        
        Replaces: get_employee_leaves_by_month_for_employee_id() function
        """
        try:
            # Calculate month boundaries
            month_start = date(year, month, 1)
            if month == 12:
                month_end = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                month_end = date(year, month + 1, 1) - timedelta(days=1)
            
            month_start_str = month_start.strftime("%Y-%m-%d")
            month_end_str = month_end.strftime("%Y-%m-%d")
            
            # Build query for leaves that overlap with the month
            filters = {
                "employee_id": employee_id,
                "$or": [
                    # Leave starts in this month
                    {"start_date": {"$gte": month_start_str, "$lte": month_end_str}},
                    # Leave ends in this month
                    {"end_date": {"$gte": month_start_str, "$lte": month_end_str}},
                    # Leave spans over this month
                    {"$and": [
                        {"start_date": {"$lt": month_start_str}},
                        {"end_date": {"$gt": month_end_str}}
                    ]}
                ]
            }
            
            documents = await self._execute_query(
                filters=filters,
                sort_by="start_date",
                sort_order=1,
                limit=50,
                organisation_id=organisation_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error retrieving employee leaves for {employee_id} in {year}-{month}: {e}")
            return []
    
    async def get_by_date_range(self, start_date: date, end_date: date,
                               organisation_id: str = "default",
                               employee_ids: Optional[List[str]] = None) -> List[EmployeeLeave]:
        """Get employee leaves within a date range."""
        try:
            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")
            
            filters = {
                "$or": [
                    # Leave starts in this range
                    {"start_date": {"$gte": start_str, "$lte": end_str}},
                    # Leave ends in this range
                    {"end_date": {"$gte": start_str, "$lte": end_str}},
                    # Leave spans over this range
                    {"$and": [
                        {"start_date": {"$lt": start_str}},
                        {"end_date": {"$gt": end_str}}
                    ]}
                ]
            }
            
            if employee_ids:
                filters["employee_id"] = {"$in": employee_ids}
            
            documents = await self._execute_query(
                filters=filters,
                sort_by="start_date",
                sort_order=1,
                limit=500,
                organisation_id=organisation_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error retrieving leaves by date range: {e}")
            return []
    
    async def get_by_status(self, status: str, organisation_id: str = "default",
                           limit: Optional[int] = None) -> List[EmployeeLeave]:
        """Get employee leaves by status."""
        try:
            filters = {"status": status}
            
            documents = await self._execute_query(
                filters=filters,
                sort_by="applied_date",
                sort_order=-1,
                limit=limit or 100,
                organisation_id=organisation_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error retrieving leaves by status {status}: {e}")
            return []
    
    async def search(self, filters: EmployeeLeaveSearchFiltersDTO,
                    organisation_id: str = "default") -> List[EmployeeLeave]:
        """Search employee leaves with filters."""
        try:
            query_filters = {}
            
            if hasattr(filters, 'employee_id') and filters.employee_id:
                query_filters["employee_id"] = filters.employee_id
            
            if hasattr(filters, 'employee_ids') and filters.employee_ids:
                query_filters["employee_id"] = {"$in": filters.employee_ids}
            
            if hasattr(filters, 'status') and filters.status:
                query_filters["status"] = filters.status
            
            if hasattr(filters, 'leave_type') and filters.leave_type:
                query_filters["leave_name"] = filters.leave_type
            
            if hasattr(filters, 'start_date') and filters.start_date:
                start_str = filters.start_date.strftime("%Y-%m-%d")
                query_filters["start_date"] = {"$gte": start_str}
            
            if hasattr(filters, 'end_date') and filters.end_date:
                end_str = filters.end_date.strftime("%Y-%m-%d")
                if "start_date" in query_filters:
                    query_filters["start_date"]["$lte"] = end_str
                else:
                    query_filters["start_date"] = {"$lte": end_str}
            
            # Get pagination parameters
            page = getattr(filters, 'page', 1)
            page_size = getattr(filters, 'page_size', 50)
            skip = (page - 1) * page_size
            
            documents = await self._execute_query(
                filters=query_filters,
                skip=skip,
                limit=page_size,
                sort_by="applied_date",
                sort_order=-1,
                organisation_id=organisation_id
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error searching employee leaves: {e}")
            return []
    
    async def count_by_filters(self, filters: EmployeeLeaveSearchFiltersDTO,
                              organisation_id: str = "default") -> int:
        """Count employee leaves matching filters."""
        try:
            query_filters = {}
            
            if hasattr(filters, 'employee_id') and filters.employee_id:
                query_filters["employee_id"] = filters.employee_id
            
            if hasattr(filters, 'status') and filters.status:
                query_filters["status"] = filters.status
            
            return await self._count_documents(query_filters, organisation_id)
            
        except Exception as e:
            logger.error(f"Error counting employee leaves: {e}")
            return 0
    
    # Analytics Repository Implementation
    async def get_leave_statistics(self, organisation_id: str = "default",
                                  year: Optional[int] = None) -> Dict[str, Any]:
        """Get leave statistics."""
        try:
            filters = {}
            
            if year:
                start_date = f"{year}-01-01"
                end_date = f"{year}-12-31"
                filters = {
                    "$or": [
                        {"start_date": {"$gte": start_date, "$lte": end_date}},
                        {"end_date": {"$gte": start_date, "$lte": end_date}},
                        {"$and": [
                            {"start_date": {"$lt": start_date}},
                            {"end_date": {"$gt": end_date}}
                        ]}
                    ]
                }
            
            # Use aggregation pipeline for statistics
            pipeline = [
                {"$match": filters},
                {
                    "$group": {
                        "_id": None,
                        "total_leaves": {"$sum": 1},
                        "pending_leaves": {
                            "$sum": {"$cond": [{"$eq": ["$status", "pending"]}, 1, 0]}
                        },
                        "approved_leaves": {
                            "$sum": {"$cond": [{"$eq": ["$status", "approved"]}, 1, 0]}
                        },
                        "rejected_leaves": {
                            "$sum": {"$cond": [{"$eq": ["$status", "rejected"]}, 1, 0]}
                        },
                        "total_leave_days": {"$sum": "$leave_count"}
                    }
                }
            ]
            
            results = await self._aggregate(pipeline, organisation_id)
            
            if results:
                stats = results[0]
                return {
                    "total_leaves": stats.get("total_leaves", 0),
                    "pending_leaves": stats.get("pending_leaves", 0),
                    "approved_leaves": stats.get("approved_leaves", 0),
                    "rejected_leaves": stats.get("rejected_leaves", 0),
                    "total_leave_days": stats.get("total_leave_days", 0)
                }
            else:
                return {
                    "total_leaves": 0,
                    "pending_leaves": 0,
                    "approved_leaves": 0,
                    "rejected_leaves": 0,
                    "total_leave_days": 0
                }
                
        except Exception as e:
            logger.error(f"Error getting leave statistics: {e}")
            return {}
    
    async def get_employee_leave_summary(self, employee_id: str, year: int,
                                        organisation_id: str = "default") -> Dict[str, Any]:
        """Get leave summary for an employee."""
        try:
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31"
            
            filters = {
                "employee_id": employee_id,
                "$or": [
                    {"start_date": {"$gte": start_date, "$lte": end_date}},
                    {"end_date": {"$gte": start_date, "$lte": end_date}},
                    {"$and": [
                        {"start_date": {"$lt": start_date}},
                        {"end_date": {"$gt": end_date}}
                    ]}
                ]
            }
            
            leaves = await self._execute_query(
                filters=filters,
                sort_by="start_date",
                sort_order=1,
                organisation_id=organisation_id
            )
            
            total_leaves = len(leaves)
            approved_leaves = sum(1 for leave in leaves if leave.get('status') == 'approved')
            total_days = sum(leave.get('leave_count', 0) for leave in leaves)
            
            # Group by leave type
            leave_types = {}
            for leave in leaves:
                leave_type = leave.get('leave_name', 'Unknown')
                if leave_type not in leave_types:
                    leave_types[leave_type] = {"count": 0, "days": 0}
                leave_types[leave_type]["count"] += 1
                leave_types[leave_type]["days"] += leave.get('leave_count', 0)
            
            return {
                "employee_id": employee_id,
                "year": year,
                "total_leaves": total_leaves,
                "approved_leaves": approved_leaves,
                "total_days": total_days,
                "leave_types": leave_types
            }
            
        except Exception as e:
            logger.error(f"Error getting employee leave summary: {e}")
            return {}
    
    # Legacy compatibility methods
    async def create_employee_leave_legacy(self, leave: EmployeeLeave, hostname: str) -> str:
        """
        Legacy compatibility for create_employee_leave() function.
        
        Args:
            leave: EmployeeLeave entity
            hostname: Organisation hostname
            
        Returns:
            Inserted document ID as string
        """
        try:
            saved_leave = await self.save(leave)
            return getattr(saved_leave, 'leave_id', str(saved_leave.id) if hasattr(saved_leave, 'id') else '')
            
        except Exception as e:
            logger.error(f"Error creating employee leave (legacy): {e}")
            raise
    
    async def get_employee_leave_by_id_legacy(self, leave_id: str, hostname: str) -> Optional[EmployeeLeave]:
        """
        Legacy compatibility for get_employee_leave_by_id() function.
        """
        return await self.get_by_id(leave_id, hostname)
    
    async def get_employee_leaves_by_employee_id_legacy(self, employee_id: str, hostname: str) -> List[EmployeeLeave]:
        """
        Legacy compatibility for get_employee_leaves_by_employee_id() function.
        """
        return await self.get_by_employee_id(employee_id, hostname)
    
    async def update_employee_leave_legacy(self, leave_id: str, update_data: dict, hostname: str):
        """
        Legacy compatibility for update_employee_leave() function.
        """
        return await self.update(leave_id, update_data, hostname)
    
    async def delete_employee_leave_legacy(self, leave_id: str, hostname: str):
        """
        Legacy compatibility for delete_employee_leave() function.
        """
        return await self.delete(leave_id, hostname)
    
    async def get_all_employee_leaves_legacy(self, hostname: str, employee_ids: list = None) -> List[EmployeeLeave]:
        """
        Legacy compatibility for get_all_employee_leaves() function.
        """
        return await self.get_all(hostname, employee_ids)
    
    async def get_employee_leaves_by_manager_id_legacy(self, manager_id: str, hostname: str) -> List[EmployeeLeave]:
        """
        Legacy compatibility for get_employee_leaves_by_manager_id() function.
        """
        return await self.get_by_manager_id(manager_id, hostname)
    
    async def get_employee_leaves_by_month_for_employee_id_legacy(
        self, employee_id: str, year: int, month: int, 
        month_start: datetime, month_end: datetime, hostname: str
    ) -> List[EmployeeLeave]:
        """Legacy method for getting employee leaves by month"""
        return await self.get_by_employee_and_month(employee_id, year, month, hostname)

    # ==================== MISSING ABSTRACT METHODS IMPLEMENTATION ====================
    
    # EmployeeLeaveQueryRepository Missing Methods
    
    async def get_by_month(
        self, 
        employee_id: EmployeeId,
        month: int,
        year: int
    ) -> List[EmployeeLeave]:
        """Get employee leaves for a specific month."""
        try:
            # Convert EmployeeId to string
            employee_id = employee_id.value if hasattr(employee_id, 'value') else str(employee_id)
            
            # Use existing method
            return await self.get_by_employee_and_month(employee_id, year, month)
            
        except Exception as e:
            logger.error(f"Error getting leaves by month for employee {employee_id}: {e}")
            return []
    
    async def get_overlapping_leaves(
        self, 
        employee_id: EmployeeId,
        date_range: DateRange,
        exclude_leave_id: Optional[str] = None
    ) -> List[EmployeeLeave]:
        """Get leaves that overlap with the given date range."""
        try:
            employee_id = employee_id.value if hasattr(employee_id, 'value') else str(employee_id)
            organisation_id = "default"  # Using default organisation
            
            collection = await self._get_collection(organisation_id)
            
            # Build query for overlapping dates
            query = {
                "employee_id": employee_id,
                "$or": [
                    {
                        "start_date": {
                            "$lte": date_range.end_date.strftime("%Y-%m-%d")
                        },
                        "end_date": {
                            "$gte": date_range.start_date.strftime("%Y-%m-%d")
                        }
                    }
                ]
            }
            
            # Exclude specific leave if provided
            if exclude_leave_id:
                query["leave_id"] = {"$ne": exclude_leave_id}
            
            documents = await collection.find(query).to_list(length=None)
            
            leaves = []
            for doc in documents:
                leave = self._document_to_entity(doc)
                if leave:
                    leaves.append(leave)
            
            return leaves
            
        except Exception as e:
            logger.error(f"Error getting overlapping leaves: {e}")
            return []
    
    async def get_pending_approvals(
        self, 
        manager_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[EmployeeLeave]:
        """Get leaves pending approval."""
        try:
            organisation_id = "default"
            
            if manager_id:
                # Get leaves for team members under this manager
                return await self.get_by_manager_id(manager_id, organisation_id)
            else:
                # Get all pending leaves
                return await self.get_by_status("pending", organisation_id, limit)
                
        except Exception as e:
            logger.error(f"Error getting pending approvals: {e}")
            return []
    
    async def update_status(
        self, 
        leave_id: str, 
        status: LeaveStatus, 
        approved_by: str,
        comments: Optional[str] = None
    ) -> bool:
        """Update leave application status."""
        try:
            organisation_id = "default"
            
            update_data = {
                "status": status.value if hasattr(status, 'value') else str(status),
                "approved_by": approved_by,
                "approved_date": datetime.now().strftime("%Y-%m-%d")
            }
            
            if comments:
                update_data["comments"] = comments
            
            return await self.update(leave_id, update_data, organisation_id)
            
        except Exception as e:
            logger.error(f"Error updating leave status: {e}")
            return False
    
    # EmployeeLeaveAnalyticsRepository Missing Methods
    
    async def get_leave_type_breakdown(
        self,
        employee_id: Optional[EmployeeId] = None,
        manager_id: Optional[str] = None,
        year: Optional[int] = None
    ) -> Dict[str, int]:
        """Get leave type breakdown."""
        try:
            organisation_id = "default"
            collection = await self._get_collection(organisation_id)
            
            # Build query
            query = {}
            
            if employee_id:
                employee_id = employee_id.value if hasattr(employee_id, 'value') else str(employee_id)
                query["employee_id"] = employee_id
            
            if manager_id:
                # Get team members under manager (simplified)
                query["manager_id"] = manager_id
            
            if year:
                query["$or"] = [
                    {"start_date": {"$regex": f"^{year}"}},
                    {"end_date": {"$regex": f"^{year}"}}
                ]
            
            # Aggregate by leave type
            pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": "$leave_name",
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            result = await collection.aggregate(pipeline).to_list(length=None)
            
            breakdown = {}
            for item in result:
                leave_type = item["_id"] or "Unknown"
                breakdown[leave_type] = item["count"]
            
            return breakdown
            
        except Exception as e:
            logger.error(f"Error getting leave type breakdown: {e}")
            return {}
    
    async def get_monthly_leave_trends(
        self,
        employee_id: Optional[EmployeeId] = None,
        manager_id: Optional[str] = None,
        year: Optional[int] = None
    ) -> Dict[str, int]:
        """Get monthly leave trends."""
        try:
            organisation_id = "default"
            collection = await self._get_collection(organisation_id)
            
            # Build query
            query = {}
            
            if employee_id:
                employee_id = employee_id.value if hasattr(employee_id, 'value') else str(employee_id)
                query["employee_id"] = employee_id
            
            if manager_id:
                query["manager_id"] = manager_id
            
            if year:
                query["$or"] = [
                    {"start_date": {"$regex": f"^{year}"}},
                    {"end_date": {"$regex": f"^{year}"}}
                ]
            
            documents = await collection.find(query).to_list(length=None)
            
            monthly_trends = {}
            
            for doc in documents:
                start_date_str = doc.get("start_date", "")
                if start_date_str and len(start_date_str) >= 7:
                    month_key = start_date_str[:7]  # YYYY-MM format
                    monthly_trends[month_key] = monthly_trends.get(month_key, 0) + 1
            
            return monthly_trends
            
        except Exception as e:
            logger.error(f"Error getting monthly leave trends: {e}")
            return {}
    
    async def get_team_leave_summary(
        self,
        manager_id: str,
        month: Optional[int] = None,
        year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get team leave summary for a manager."""
        try:
            organisation_id = "default"
            
            # Get all leaves for team members
            team_leaves = await self.get_by_manager_id(manager_id, organisation_id)
            
            # Filter by month/year if provided
            if month or year:
                filtered_leaves = []
                for leave in team_leaves:
                    start_date_str = getattr(leave, 'start_date', '')
                    if start_date_str:
                        try:
                            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                            if year and start_date.year != year:
                                continue
                            if month and start_date.month != month:
                                continue
                            filtered_leaves.append(leave)
                        except ValueError:
                            continue
                team_leaves = filtered_leaves
            
            # Group by employee
            summary = {}
            for leave in team_leaves:
                employee_id = getattr(leave, 'employee_id', 'Unknown')
                if employee_id not in summary:
                    summary[employee_id] = {
                        "employee_id": employee_id,
                        "total_leaves": 0,
                        "approved_leaves": 0,
                        "pending_leaves": 0,
                        "rejected_leaves": 0
                    }
                
                summary[employee_id]["total_leaves"] += 1
                status = getattr(leave, 'status', '').lower()
                if status == 'approved':
                    summary[employee_id]["approved_leaves"] += 1
                elif status == 'pending':
                    summary[employee_id]["pending_leaves"] += 1
                elif status == 'rejected':
                    summary[employee_id]["rejected_leaves"] += 1
            
            return list(summary.values())
            
        except Exception as e:
            logger.error(f"Error getting team leave summary: {e}")
            return []
    
    async def calculate_lwp_for_employee(
        self,
        employee_id: EmployeeId,
        month: int,
        year: int
    ) -> int:
        """Calculate Leave Without Pay (LWP) for an employee."""
        try:
            employee_id = employee_id.value if hasattr(employee_id, 'value') else str(employee_id)
            
            # Get all leaves for the employee in the specified month
            leaves = await self.get_by_employee_and_month(employee_id, year, month)
            
            lwp_days = 0
            
            for leave in leaves:
                # Check if this is an LWP leave
                leave_name = getattr(leave, 'leave_name', '').lower()
                status = getattr(leave, 'status', '').lower()
                
                if 'lwp' in leave_name or 'without pay' in leave_name:
                    if status == 'approved':
                        # Calculate days between start and end date
                        start_date_str = getattr(leave, 'start_date', '')
                        end_date_str = getattr(leave, 'end_date', '')
                        
                        if start_date_str and end_date_str:
                            try:
                                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                                days = (end_date - start_date).days + 1
                                lwp_days += days
                            except ValueError:
                                logger.warning(f"Invalid date format in leave record")
            
            return lwp_days
            
        except Exception as e:
            logger.error(f"Error calculating LWP: {e}")
            return 0
    
    # EmployeeLeaveBalanceRepository Missing Methods
    
    async def get_leave_balance(self, employee_id: EmployeeId) -> Dict[str, int]:
        """Get leave balance for an employee."""
        try:
            employee_id = employee_id.value if hasattr(employee_id, 'value') else str(employee_id)
            organisation_id = "default"
            
            # Check if we have a separate balances collection
            balances_collection = self.db_connector.get_database().get_collection(f"{organisation_id}_employee_leave_balances")
            
            balance_doc = await balances_collection.find_one({"employee_id": employee_id})
            
            if balance_doc:
                # Remove MongoDB _id field
                balance_doc.pop("_id", None)
                balance_doc.pop("employee_id", None)
                return balance_doc
            else:
                # Return default balances if not found
                return {
                    "annual_leave": 21,
                    "sick_leave": 12,
                    "casual_leave": 7,
                    "maternity_leave": 84,
                    "paternity_leave": 15,
                    "lwp": 0
                }
                
        except Exception as e:
            logger.error(f"Error getting leave balance: {e}")
            return {}
    
    async def update_leave_balance(
        self, 
        employee_id: EmployeeId, 
        leave_type: str, 
        balance_change: int
    ) -> bool:
        """Update leave balance for an employee."""
        try:
            employee_id = employee_id.value if hasattr(employee_id, 'value') else str(employee_id)
            organisation_id = "default"
            
            balances_collection = self.db_connector.get_database().get_collection(f"{organisation_id}_employee_leave_balances")
            
            # Update the specific leave type balance
            result = await balances_collection.update_one(
                {"employee_id": employee_id},
                {
                    "$inc": {leave_type: balance_change},
                    "$set": {"updated_at": datetime.utcnow()}
                },
                upsert=True
            )
            
            return result.acknowledged
            
        except Exception as e:
            logger.error(f"Error updating leave balance: {e}")
            return False
    
    async def set_leave_balance(
        self, 
        employee_id: EmployeeId, 
        leave_balances: Dict[str, int]
    ) -> bool:
        """Set leave balances for an employee."""
        try:
            employee_id = employee_id.value if hasattr(employee_id, 'value') else str(employee_id)
            organisation_id = "default"
            
            balances_collection = self.db_connector.get_database().get_collection(f"{organisation_id}_employee_leave_balances")
            
            # Set all leave balances
            balance_doc = {
                "employee_id": employee_id,
                "updated_at": datetime.utcnow(),
                **leave_balances
            }
            
            result = await balances_collection.replace_one(
                {"employee_id": employee_id},
                balance_doc,
                upsert=True
            )
            
            return result.acknowledged
            
        except Exception as e:
            logger.error(f"Error setting leave balance: {e}")
            return False
    
    async def get_team_leave_balances(self, manager_id: str) -> List[Dict[str, Any]]:
        """Get leave balances for all team members under a manager."""
        try:
            organisation_id = "default"
            
            # First, get all team members under this manager
            # This is simplified - in a real system, you'd have an employee-manager relationship
            collection = await self._get_collection(organisation_id)
            
            # Get unique employee IDs who have had leaves under this manager
            pipeline = [
                {"$match": {"manager_id": manager_id}},
                {"$group": {"_id": "$employee_id"}},
                {"$limit": 100}  # Reasonable limit
            ]
            
            result = await collection.aggregate(pipeline).to_list(length=None)
            employee_ids = [item["_id"] for item in result]
            
            # Get balances for each employee
            team_balances = []
            for employee_id in employee_ids:
                try:
                    employee_id = EmployeeId(employee_id)
                    balances = await self.get_leave_balance(employee_id)
                    
                    team_balances.append({
                        "employee_id": employee_id,
                        "balances": balances
                    })
                except Exception as emp_error:
                    logger.warning(f"Error getting balance for employee {employee_id}: {emp_error}")
                    continue
            
            return team_balances
            
        except Exception as e:
            logger.error(f"Error getting team leave balances: {e}")
            return [] 