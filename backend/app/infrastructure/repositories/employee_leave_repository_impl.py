"""
Employee Leave Repository Implementation
MongoDB implementation of employee leave data access following DDD patterns
"""

import logging
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from bson import ObjectId
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
from pymongo.collection import Collection

from app.domain.value_objects.employee_id import EmployeeId

from app.domain.entities.employee_leave import EmployeeLeave
from app.application.interfaces.repositories.employee_leave_repository import (
    EmployeeLeaveCommandRepository, EmployeeLeaveQueryRepository, 
    EmployeeLeaveAnalyticsRepository, EmployeeLeaveRepository
)
from app.application.dto.employee_leave_dto import EmployeeLeaveSearchFiltersDTO
from app.infrastructure.database.database_connector import DatabaseConnector
from app.domain.events.leave_events import EmployeeLeaveCreatedEvent, EmployeeLeaveUpdatedEvent, EmployeeLeaveDeletedEvent

logger = logging.getLogger(__name__)


class EmployeeLeaveRepositoryImpl(EmployeeLeaveRepository):
    """
    MongoDB implementation of employee leave repository following DDD patterns.
    
    Implements all employee leave repository interfaces in a single class for simplicity
    while maintaining SOLID principles through interface segregation.
    """
    
    def __init__(self, database_connector: DatabaseConnector):
        """
        Initialize repository with database connector.
        
        Args:
            database_connector: Database connection abstraction
        """
        self.db_connector = database_connector
        self._collection_name = "employee_leaves"
        
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
        Get employee leave collection for specific organisation or global.
        
        Ensures database connection is established in the correct event loop.
        """
        db_name = organisation_id if organisation_id else "pms_global_database"
        
        # Ensure database is connected in the current event loop
        if not self.db_connector.is_connected:
            logger.info("Database not connected, establishing connection...")
            
            try:
                # Use stored connection configuration
                if self._connection_string and self._client_options:
                    logger.info("Using stored connection parameters from repository configuration")
                    connection_string = self._connection_string
                    options = self._client_options
                else:
                    # Connection config must be set by dependency container
                    raise RuntimeError("Database connection configuration not set. Call set_connection_config() first.")
                
                await self.db_connector.connect(connection_string, **options)
                logger.info("MongoDB connection established successfully in current event loop")
                
            except Exception as e:
                logger.error(f"Failed to establish database connection: {e}")
                raise RuntimeError(f"Database connection failed: {e}")
        
        # Verify connection and get collection
        try:
            db = self.db_connector.get_database('pms_'+db_name)
            collection = db[self._collection_name]
            logger.info(f"Successfully retrieved collection: {self._collection_name} from database: {'pms_'+db_name}")
            return collection
            
        except Exception as e:
            logger.error(f"Failed to get collection {self._collection_name}: {e}")
            # Reset connection state to force reconnection on next call
            if hasattr(self.db_connector, '_client'):
                self.db_connector._client = None
            raise RuntimeError(f"Collection access failed: {e}")
    
    def _leave_to_document(self, employee_leave: EmployeeLeave) -> Dict[str, Any]:
        """Convert domain entity to database document."""
        
        # Safe value extraction for enums - handle both enum objects and strings
        def safe_enum_value(field_value):
            if hasattr(field_value, 'value'):
                return field_value.value
            return str(field_value) if field_value is not None else None
        
        # Safe extraction for complex nested objects
        def safe_get_attr(obj, attr_path, default=None):
            """Safely get nested attributes"""
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
        
        # Convert date objects to ISO string for MongoDB compatibility
        def safe_date_conversion(date_value):
            """Convert date objects to ISO string for MongoDB"""
            if date_value is None:
                return None
            if isinstance(date_value, datetime):
                return date_value.isoformat()
            elif hasattr(date_value, 'isoformat'):
                return date_value.isoformat()
            else:
                return str(date_value)
        
        return {
            "leave_id": employee_leave.leave_id,
            "employee_id": employee_leave.employee_id,
            "employee_name": employee_leave.employee_name,
            "employee_email": employee_leave.employee_email,
            "organisation_id": employee_leave.organisation_id,
            "leave_name": employee_leave.leave_name,
            "start_date": safe_date_conversion(employee_leave.start_date),
            "end_date": safe_date_conversion(employee_leave.end_date),
            "reason": employee_leave.reason,
            "status": employee_leave.status,
            "applied_days": employee_leave.applied_days,
            "approved_days": employee_leave.approved_days,
            "applied_at": safe_date_conversion(employee_leave.applied_at),
            "approved_at": safe_date_conversion(employee_leave.approved_at) if employee_leave.approved_at else None,
            "approved_by": employee_leave.approved_by,
            "rejected_at": safe_date_conversion(employee_leave.rejected_at) if employee_leave.rejected_at else None,
            "rejected_by": employee_leave.rejected_by,
            "rejection_reason": employee_leave.rejection_reason,
            "is_half_day": employee_leave.is_half_day,
            "is_compensatory": employee_leave.is_compensatory,
            "compensatory_work_date": safe_date_conversion(employee_leave.compensatory_work_date) if employee_leave.compensatory_work_date else None,
            "created_at": safe_date_conversion(employee_leave.created_at),
            "updated_at": safe_date_conversion(employee_leave.updated_at),
            "created_by": employee_leave.created_by,
            "updated_by": employee_leave.updated_by,
            "is_deleted": False
        }
    
    def _document_to_leave(self, document: Dict[str, Any]) -> EmployeeLeave:
        """Convert database document to domain entity."""
        
        # Helper function to parse dates
        def parse_date(date_str):
            if not date_str:
                return None
            if isinstance(date_str, str):
                try:
                    # Try parsing as ISO format first
                    if 'T' in date_str:
                        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    else:
                        return datetime.fromisoformat(date_str).date()
                except ValueError:
                    try:
                        # Try parsing as date only
                        return datetime.strptime(date_str, '%Y-%m-%d').date()
                    except ValueError:
                        return None
            return date_str
        
        # Parse dates
        start_date = parse_date(document.get("start_date"))
        end_date = parse_date(document.get("end_date"))
        applied_at = parse_date(document.get("applied_at"))
        approved_at = parse_date(document.get("approved_at"))
        rejected_at = parse_date(document.get("rejected_at"))
        compensatory_work_date = parse_date(document.get("compensatory_work_date"))
        created_at = parse_date(document.get("created_at"))
        updated_at = parse_date(document.get("updated_at"))
        
        # Ensure datetime objects where needed
        if isinstance(applied_at, date) and not isinstance(applied_at, datetime):
            applied_at = datetime.combine(applied_at, datetime.min.time())
        if isinstance(created_at, date) and not isinstance(created_at, datetime):
            created_at = datetime.combine(created_at, datetime.min.time())
        if isinstance(updated_at, date) and not isinstance(updated_at, datetime):
            updated_at = datetime.combine(updated_at, datetime.min.time())
    
        return EmployeeLeave(
            leave_id=document.get("leave_id"),
            employee_id=document.get("employee_id"),
            employee_name=document.get("employee_name", ""),
            employee_email=document.get("employee_email", ""),
            organisation_id=document.get("organisation_id"),
            leave_name=document.get("leave_name"),
            start_date=start_date,
            end_date=end_date,
            reason=document.get("reason"),
            status=document.get("status", "pending"),
            applied_days=document.get("applied_days"),
            approved_days=document.get("approved_days"),
            applied_at=applied_at or datetime.utcnow(),
            approved_at=approved_at,
            approved_by=document.get("approved_by"),
            rejected_at=rejected_at,
            rejected_by=document.get("rejected_by"),
            rejection_reason=document.get("rejection_reason"),
            is_half_day=document.get("is_half_day", False),
            is_compensatory=document.get("is_compensatory", False),
            compensatory_work_date=compensatory_work_date,
            created_at=created_at or datetime.utcnow(),
            updated_at=updated_at or datetime.utcnow(),
            created_by=document.get("created_by"),
            updated_by=document.get("updated_by")
        )
    
    async def _publish_events(self, events: List[Any]) -> None:
        """Publish domain events."""
        # Implementation would depend on event publisher
        for event in events:
            logger.info(f"Publishing event: {type(event).__name__}")
    
    # Command Repository Implementation
    async def save(self, employee_leave: EmployeeLeave, organisation_id: Optional[str] = None) -> EmployeeLeave:
        """Save an employee leave (create or update)."""
        try:
            collection = await self._get_collection(organisation_id)
            document = self._leave_to_document(employee_leave)
            
            # Use upsert based on leave_id
            filter_query = {"leave_id": employee_leave.leave_id}
            
            result = await collection.replace_one(
                filter_query,
                document,
                upsert=True
            )
            
            # Publish events based on operation
            events = []
            if result.upserted_id:
                event = EmployeeLeaveCreatedEvent(
                    employee_id=employee_leave.employee_id,
                    leave_id=employee_leave.leave_id,
                    leave_name=employee_leave.leave_name,
                    start_date=employee_leave.start_date,
                    end_date=employee_leave.end_date,
                    applied_days=employee_leave.applied_days or 0,
                    created_by=employee_leave.created_by or "system"
                )
                events.append(event)
                logger.info(f"Created employee leave: {employee_leave.leave_id}")
            else:
                event = EmployeeLeaveUpdatedEvent(
                    employee_id=employee_leave.employee_id,
                    leave_id=employee_leave.leave_id,
                    leave_name=employee_leave.leave_name,
                    updated_by=employee_leave.updated_by or "system"
                )
                events.append(event)
                logger.info(f"Updated employee leave: {employee_leave.leave_id}")
            
            await self._publish_events(events)
            return employee_leave
            
        except Exception as e:
            logger.error(f"Error saving employee leave: {e}")
            raise
    
    async def save_batch(self, employee_leaves: List[EmployeeLeave], organisation_id: Optional[str] = None) -> List[EmployeeLeave]:
        """Save multiple employee leaves in a batch operation."""
        try:
            collection = await self._get_collection(organisation_id)
            
            # Prepare bulk operations
            operations = []
            for employee_leave in employee_leaves:
                document = self._leave_to_document(employee_leave)
                operations.append({
                    "replaceOne": {
                        "filter": {"leave_id": employee_leave.leave_id},
                        "replacement": document,
                        "upsert": True
                    }
                })
            
            # Execute bulk write
            if operations:
                await collection.bulk_write(operations)
                
                # Publish events for all leaves
                for employee_leave in employee_leaves:
                    await self._publish_events(employee_leave.get_domain_events())
                    employee_leave.clear_domain_events()
            
            logger.info(f"Batch saved {len(employee_leaves)} employee leaves")
            return employee_leaves
            
        except Exception as e:
            logger.error(f"Error in batch save: {e}")
            raise
    
    async def delete(self, leave_id: str, soft_delete: bool = True, organisation_id: Optional[str] = None) -> bool:
        """Delete an employee leave by ID."""
        try:
            # For soft delete, we need to find the leave first
            employee_leave = await self.get_by_id(leave_id, organisation_id)
            if not employee_leave:
                return False
            
            collection = await self._get_collection(organisation_id)
            
            if soft_delete:
                # Soft delete - mark as deleted
                result = await collection.update_one(
                    {"leave_id": leave_id},
                    {
                        "$set": {
                            "is_deleted": True,
                            "deleted_at": datetime.utcnow(),
                            "status": "cancelled"
                        }
                    }
                )
            else:
                # Hard delete
                result = await collection.delete_one({"leave_id": leave_id})
            
            if result.modified_count > 0 or result.deleted_count > 0:
                # Publish delete event
                delete_event = EmployeeLeaveDeletedEvent(
                    employee_id=employee_leave.employee_id,
                    leave_id=leave_id,
                    leave_name=employee_leave.leave_name,
                    deleted_by="system",
                    deletion_reason="Soft delete" if soft_delete else "Hard delete"
                )
                await self._publish_events([delete_event])
                
                logger.info(f"Employee leave deleted: {leave_id} (soft: {soft_delete})")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting employee leave {leave_id}: {e}")
            raise
    
    # Query Repository Implementation
    async def get_by_id(self, leave_id: str, organisation_id: Optional[str] = None) -> Optional[EmployeeLeave]:
        """Get employee leave by ID."""
        try:
            collection = await self._get_collection(organisation_id)
            document = await collection.find_one({
                "leave_id": leave_id,
                "is_deleted": {"$ne": True}
            })
            
            if document:
                return self._document_to_leave(document)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting employee leave by ID {leave_id}: {e}")
            raise
    
    async def get_by_employee_id(self, employee_id: Union[str, EmployeeId], organisation_id: Optional[str] = None) -> List[EmployeeLeave]:
        """Get employee leaves by employee ID."""
        try:
            collection = await self._get_collection(organisation_id)
            
            # Convert EmployeeId to string if needed
            employee_id_str = str(employee_id) if hasattr(employee_id, 'value') else str(employee_id)
            
            cursor = collection.find({
                "employee_id": employee_id_str,
                "is_deleted": {"$ne": True}
            }).sort("created_at", DESCENDING)
            
            documents = await cursor.to_list(length=None)
            return [self._document_to_leave(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting employee leaves by employee ID {employee_id}: {e}")
            raise
    
    async def get_by_status(self, status: str, organisation_id: Optional[str] = None) -> List[EmployeeLeave]:
        """Get employee leaves by status."""
        try:
            collection = await self._get_collection(organisation_id)
            cursor = collection.find({
                "status": status,
                "is_deleted": {"$ne": True}
            }).sort("created_at", DESCENDING)
            
            documents = await cursor.to_list(length=None)
            return [self._document_to_leave(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting employee leaves by status {status}: {e}")
            raise
    
    async def get_by_leave_name(self, leave_name: str, organisation_id: Optional[str] = None) -> List[EmployeeLeave]:
        """Get employee leaves by leave name."""
        try:
            collection = await self._get_collection(organisation_id)
            cursor = collection.find({
                "leave_name": leave_name,
                "is_deleted": {"$ne": True}
            }).sort("created_at", DESCENDING)
            
            documents = await cursor.to_list(length=None)
            return [self._document_to_leave(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting employee leaves by leave name {leave_name}: {e}")
            raise
    
    async def get_by_date_range(
        self, 
        start_date: date, 
        end_date: date, 
        organisation_id: Optional[str] = None,
        employee_id: Optional[str] = None
    ) -> List[EmployeeLeave]:
        """Get employee leaves by date range."""
        try:
            collection = await self._get_collection(organisation_id)
            # Build query
            query = {
                "$and": [
                    {
                        "$or": [
                            {
                                "start_date": {
                                    "$gte": start_date.isoformat(),
                                    "$lte": end_date.isoformat()
                                }
                            },
                            {
                                "end_date": {
                                    "$gte": start_date.isoformat(),
                                    "$lte": end_date.isoformat()
                                }
                            },
                            {
                                "$and": [
                                    {"start_date": {"$lte": start_date.isoformat()}},
                                    {"end_date": {"$gte": end_date.isoformat()}}
                                ]
                            }
                        ]
                    },
                    {
                        "status": {"$in": ["pending", "approved"]},
                        "is_deleted": {"$ne": True}
                    }
                ]
            }
            
            # Add employee_id filter if provided
            if employee_id:
                query["$and"].append({"employee_id": employee_id})
            
            cursor = collection.find(query).sort("start_date", ASCENDING)
            
            documents = await cursor.to_list(length=None)
            return [self._document_to_leave(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting employee leaves by date range: {e}")
            raise

    async def get_by_month(
        self, 
        employee_id: str, 
        month: int, 
        year: int, 
        organisation_id: Optional[str] = None
    ) -> List[EmployeeLeave]:
        """Get employee leaves for a specific month."""
        try:
            collection = await self._get_collection(organisation_id)
            
            # Create month start and end dates
            from datetime import datetime, timedelta
            month_start = datetime(year, month, 1)
            if month == 12:
                month_end = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                month_end = datetime(year, month + 1, 1) - timedelta(days=1)
            
            # Query for leaves that overlap with the month
            cursor = collection.find({
                "employee_id": employee_id,
                "$or": [
                    {
                        "start_date": {
                            "$gte": month_start.strftime("%Y-%m-%d"),
                            "$lte": month_end.strftime("%Y-%m-%d")
                        }
                    },
                    {
                        "end_date": {
                            "$gte": month_start.strftime("%Y-%m-%d"),
                            "$lte": month_end.strftime("%Y-%m-%d")
                        }
                    },
                    {
                        "$and": [
                            {"start_date": {"$lte": month_start.strftime("%Y-%m-%d")}},
                            {"end_date": {"$gte": month_end.strftime("%Y-%m-%d")}}
                        ]
                    }
                ],
                "is_deleted": {"$ne": True}
            }).sort("start_date", ASCENDING)
            
            documents = await cursor.to_list(length=None)
            return [self._document_to_leave(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error getting employee leaves by month {month}/{year}: {e}")
            raise
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        include_deleted: bool = False,
        organisation_id: Optional[str] = None
    ) -> List[EmployeeLeave]:
        """Get all employee leaves with pagination."""
        try:
            collection = await self._get_collection(organisation_id)
            
            # Build filter
            filter_query = {}
            if not include_deleted:
                filter_query["is_deleted"] = {"$ne": True}
            
            # Execute query
            cursor = collection.find(filter_query).skip(skip).limit(limit).sort("created_at", DESCENDING)
            documents = await cursor.to_list(length=limit)
            
            employee_leaves = [self._document_to_leave(doc) for doc in documents]
            logger.info(f"Retrieved {len(employee_leaves)} employee leaves")
            return employee_leaves
            
        except Exception as e:
            logger.error(f"Error getting all employee leaves: {e}")
            raise
    
    async def search(self, filters: EmployeeLeaveSearchFiltersDTO, organisation_id: Optional[str] = None) -> List[EmployeeLeave]:
        """Search employee leaves with filters."""
        try:
            collection = await self._get_collection(organisation_id)
            
            # Build search query
            query = {}
            
            # Text search
            if filters.search_term:
                query["$or"] = [
                    {"manager_id": {"$regex": filters.search_term, "$options": "i"}},
                    {"leave_name": {"$regex": filters.search_term, "$options": "i"}},
                    {"reason": {"$regex": filters.search_term, "$options": "i"}}
                ]
            
            # Employee ID filter
            if filters.employee_id:
                query["employee_id"] = filters.employee_id
            
            # Leave type filter
            if filters.leave_type:
                query["leave_name"] = {"$regex": filters.leave_type, "$options": "i"}
            
            # Status filter
            if filters.status:
                query["status"] = filters.status
            
            # Date range filters
            if filters.start_date or filters.end_date:
                date_filter = {}
                if filters.start_date:
                    date_filter["$gte"] = filters.start_date.isoformat()
                if filters.end_date:
                    date_filter["$lte"] = filters.end_date.isoformat()
                query["start_date"] = date_filter
            
            # Deleted filter
            if not filters.include_deleted:
                query["is_deleted"] = {"$ne": True}
            
            # Execute query with pagination
            cursor = collection.find(query)
            
            # Apply sorting
            if filters.sort_by:
                sort_direction = DESCENDING if filters.sort_desc else ASCENDING
                cursor = cursor.sort(filters.sort_by, sort_direction)
            
            # Apply pagination
            cursor = cursor.skip(filters.skip).limit(filters.limit)
            
            documents = await cursor.to_list(length=filters.limit)
            employee_leaves = [self._document_to_leave(doc) for doc in documents]
            
            logger.info(f"Search returned {len(employee_leaves)} employee leaves")
            return employee_leaves
            
        except Exception as e:
            logger.error(f"Error searching employee leaves: {e}")
            raise
    
    # Count methods
    async def count_total(self, include_deleted: bool = False, organisation_id: Optional[str] = None) -> int:
        """Count total employee leaves."""
        try:
            collection = await self._get_collection(organisation_id)
            filter_query = {}
            if not include_deleted:
                filter_query["is_deleted"] = {"$ne": True}
            
            return await collection.count_documents(filter_query)
            
        except Exception as e:
            logger.error(f"Error counting total employee leaves: {e}")
            raise
    
    async def count_by_status(self, status: str, organisation_id: Optional[str] = None) -> int:
        """Count employee leaves by status."""
        try:
            collection = await self._get_collection(organisation_id)
            return await collection.count_documents({
                "status": status,
                "is_deleted": {"$ne": True}
            })
            
        except Exception as e:
            logger.error(f"Error counting employee leaves by status {status}: {e}")
            raise
    
    # ==================== FACTORY METHODS IMPLEMENTATION ====================
    # These methods are required by the repository interfaces but are not used
    # in the current dependency injection architecture. They return self since
    # this repository implements all employee leave repository interfaces.
    
    def create_command_repository(self) -> EmployeeLeaveCommandRepository:
        """Create command repository instance."""
        return self
    
    def create_query_repository(self) -> EmployeeLeaveQueryRepository:
        """Create query repository instance."""
        return self
    
    def create_analytics_repository(self) -> EmployeeLeaveAnalyticsRepository:
        """Create analytics repository instance."""
        return self
    
    # Analytics Repository Implementation
    async def get_leave_statistics(
        self,
        employee_id: Optional[str] = None,
        manager_id: Optional[str] = None,
        year: Optional[int] = None,
        organisation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get leave statistics."""
        try:
            collection = await self._get_collection(organisation_id)
            
            # Build base query
            query = {   }
            if employee_id:
                query["employee_id"] = employee_id
            if manager_id:
                query["manager_id"] = manager_id
            if year:
                query["$expr"] = {
                    "$eq": [{"$year": {"$toDate": "$start_date"}}, year]
                }
            
            # Get total applications
            total_applications = await collection.count_documents(query)
            
            # Get status breakdowns
            status_queries = {
                "approved": {**query, "status": "approved"},
                "rejected": {**query, "status": "rejected"},
                "pending": {**query, "status": "pending"}
            }
            
            status_counts = {}
            for status, status_query in status_queries.items():
                status_counts[f"{status}_applications"] = await collection.count_documents(status_query)
            
            # Calculate total days taken
            pipeline = [
                {"$match": {**query, "status": "approved"}},
                {"$group": {
                    "_id": None,
                    "total_days": {"$sum": "$applied_days"}
                }}
            ]
            
            days_result = await collection.aggregate(pipeline).to_list(length=1)
            total_days = days_result[0]["total_days"] if days_result else 0
            
            return {
                "total_applications": total_applications,
                **status_counts,
                "total_days_taken": total_days
            }
            
        except Exception as e:
            logger.error(f"Error getting leave statistics: {e}")
            raise
    
    async def get_leave_type_breakdown(
        self,
        employee_id: Optional[str] = None,
        manager_id: Optional[str] = None,
        year: Optional[int] = None,
        organisation_id: Optional[str] = None
    ) -> Dict[str, int]:
        """Get leave type breakdown."""
        try:
            collection = await self._get_collection(organisation_id)
            
            # Build base query
            query = {"is_deleted": {"$ne": True}}
            if employee_id:
                query["employee_id"] = employee_id
            if manager_id:
                query["manager_id"] = manager_id
            if year:
                query["$expr"] = {
                    "$eq": [{"$year": {"$toDate": "$start_date"}}, year]
                }
            
            # Aggregate by leave type
            pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": "$leave_name",
                    "count": {"$sum": 1}
                }}
            ]
            
            results = await collection.aggregate(pipeline).to_list(length=None)
            return {doc["_id"]: doc["count"] for doc in results}
            
        except Exception as e:
            logger.error(f"Error getting leave type breakdown: {e}")
            raise
    
    async def get_monthly_leave_trends(
        self,
        employee_id: Optional[str] = None,
        manager_id: Optional[str] = None,
        year: Optional[int] = None,
        organisation_id: Optional[str] = None
    ) -> Dict[str, int]:
        """Get monthly leave trends."""
        try:
            collection = await self._get_collection(organisation_id)
            
            # Build base query
            query = {"is_deleted": {"$ne": True}}
            if employee_id:
                query["employee_id"] = employee_id
            if manager_id:
                query["manager_id"] = manager_id
            if year:
                query["$expr"] = {
                    "$eq": [{"$year": {"$toDate": "$start_date"}}, year]
                }
            
            # Aggregate by month
            pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": {"$month": {"$toDate": "$start_date"}},
                    "count": {"$sum": 1}
                }},
                {"$sort": {"_id": 1}}
            ]
            
            results = await collection.aggregate(pipeline).to_list(length=None)
            return {str(doc["_id"]): doc["count"] for doc in results}
            
        except Exception as e:
            logger.error(f"Error getting monthly leave trends: {e}")
            raise
    
    async def get_team_leave_summary(
        self,
        manager_id: str,
        month: Optional[int] = None,
        year: Optional[int] = None,
        organisation_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get team leave summary for a manager."""
        try:
            collection = await self._get_collection(organisation_id)
            
            # Build base query
            query = {
                "manager_id": manager_id,
                "is_deleted": {"$ne": True}
            }
            
            if month and year:
                query["$expr"] = {
                    "$and": [
                        {"$eq": [{"$month": {"$toDate": "$start_date"}}, month]},
                        {"$eq": [{"$year": {"$toDate": "$start_date"}}, year]}
                    ]
                }
            
            # Get all leaves for the team
            cursor = collection.find(query)
            leaves = await cursor.to_list(length=None)
            
            # Group by employee
            employee_summary = {}
            for leave in leaves:
                employee_id = leave["employee_id"]
                if employee_id not in employee_summary:
                    employee_summary[employee_id] = {
                        "employee_id": employee_id,
                        "total_leaves": 0,
                        "approved_leaves": 0,
                        "pending_leaves": 0,
                        "rejected_leaves": 0,
                        "total_days": 0
                    }
                
                summary = employee_summary[employee_id]
                summary["total_leaves"] += 1
                summary["total_days"] += leave.get("number_of_days", 0)
                
                if leave["status"] == "approved":
                    summary["approved_leaves"] += 1
                elif leave["status"] == "pending":
                    summary["pending_leaves"] += 1
                elif leave["status"] == "rejected":
                    summary["rejected_leaves"] += 1
            
            return list(employee_summary.values())
            
        except Exception as e:
            logger.error(f"Error getting team leave summary: {e}")
            raise
    
    async def calculate_lwp_for_employee(
        self,
        employee_id: str,
        month: int,
        year: int,
        organisation_id: Optional[str] = None
    ) -> int:
        """Calculate Leave Without Pay (LWP) for an employee."""
        try:
            # Use the standardized LWP calculation service from dependency container
            from app.config.dependency_container import get_dependency_container
            container = get_dependency_container()
            lwp_service = container.get_lwp_calculation_service()
            
            # Calculate LWP using standardized method
            lwp_result = await lwp_service.calculate_lwp_for_month(
                employee_id, month, year, organisation_id or "default"
            )
            
            return lwp_result.lwp_days
            
        except Exception as e:
            logger.error(f"Error calculating LWP for employee: {e}")
            # Fallback to simple calculation if standardized method fails
            return await self._calculate_lwp_fallback(employee_id, month, year, organisation_id)
    
    async def _calculate_lwp_fallback(
        self,
        employee_id: str,
        month: int,
        year: int,
        organisation_id: Optional[str] = None
    ) -> int:
        """Fallback LWP calculation method."""
        try:
            collection = await self._get_collection(organisation_id)
            
            # Get all leaves for the employee in the specified month
            query = {
                "employee_id": employee_id,
                "is_deleted": {"$ne": True},
                "$expr": {
                    "$and": [
                        {"$eq": [{"$month": {"$toDate": "$start_date"}}, month]},
                        {"$eq": [{"$year": {"$toDate": "$start_date"}}, year]}
                    ]
                }
            }
            
            cursor = collection.find(query)
            leaves = await cursor.to_list(length=None)
            
            # Calculate total LWP days
            lwp_days = 0
            for leave in leaves:
                if leave["leave_name"] == "lwp":  # Assuming LWP is a specific leave type
                    lwp_days += leave.get("number_of_days", 0)
            
            return lwp_days
            
        except Exception as e:
            logger.error(f"Error in fallback LWP calculation: {e}")
            return 0 
        