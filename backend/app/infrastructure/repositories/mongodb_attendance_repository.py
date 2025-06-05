"""
MongoDB User Repository Implementation
Following SOLID principles and DDD patterns for user data access
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
from decimal import Decimal
from bson import ObjectId
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
from pymongo.collection import Collection

from app.domain.entities.attendance import Attendance
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.attendance_status import AttendanceStatus
from app.application.interfaces.repositories.attendance_repository import (
    AttendanceCommandRepository, AttendanceQueryRepository, AttendanceAnalyticsRepository,
    AttendanceReportsRepository, AttendanceBulkOperationsRepository, AttendanceRepository
)
from app.application.dto.attendance_dto import (
    AttendanceSearchFiltersDTO, AttendanceStatisticsDTO, AttendanceSummaryDTO,
    DepartmentAttendanceDTO, AttendanceTrendDTO
)
from app.infrastructure.database.database_connector import DatabaseConnector
from app.domain.events.attendance_events import AttendanceCreatedEvent, AttendanceUpdatedEvent, AttendanceDeletedEvent
# from app.config.mongodb_config import get_mongodb_connection_string, get_mongodb_client_options
from app.domain.value_objects.working_hours import WorkingHours

logger = logging.getLogger(__name__)


class MongoDBAttendanceRepository(AttendanceRepository):
    """
    MongoDB implementation of attendance repository following DDD patterns.
    
    Implements all attendance repository interfaces in a single class for simplicity
    while maintaining SOLID principles through interface segregation.
    """
    
    def __init__(self, database_connector: DatabaseConnector):
        """
        Initialize repository with database connector.
        
        Args:
            database_connector: Database connection abstraction
        """
        self.db_connector = database_connector
        self._collection_name = "attendance_info"
        
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
        Get attendance collection for specific organisation or global.
        
        Ensures database connection is established in the correct event loop.
        """
        db_name = organisation_id if organisation_id else "pms_global_database"
        
        # Ensure database is connected in the current event loop
        if not self.db_connector.is_connected:
            logger.debug("Database not connected, establishing connection...")
            
            try:
                # Use stored connection configuration
                if self._connection_string and self._client_options:
                    logger.debug("Using stored connection parameters from repository configuration")
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
            logger.debug(f"Successfully retrieved collection: {self._collection_name} from database: {'pms_'+db_name}")
            return collection
            
        except Exception as e:
            logger.error(f"Failed to get collection {self._collection_name}: {e}")
            # Reset connection state to force reconnection on next call
            if hasattr(self.db_connector, '_client'):
                self.db_connector._client = None
            raise RuntimeError(f"Collection access failed: {e}")
    
    def _attendance_to_document(self, attendance: Attendance) -> Dict[str, Any]:
        """Convert domain entity to database document."""
        
        # Safe value extraction for enums - handle both enum objects and strings
        def safe_enum_value(field_value):
            if hasattr(field_value, 'value'):
                return field_value.value
            return str(field_value) if field_value is not None else None
        
        # Safe extraction for complex nested objects
        def safe_get_attr(obj, attr_path, default=None):
            """Safely get nested attributes like 'permissions.role.value'"""
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
            elif hasattr(date_value, 'date') and callable(date_value.date):
                # It's a datetime, return as is
                return date_value
            elif hasattr(date_value, 'year') and hasattr(date_value, 'month') and hasattr(date_value, 'day'):
                # It's a date object, convert to datetime
                from datetime import datetime as dt
                return dt.combine(date_value, dt.min.time())
            else:
                return date_value
        
        # Safe boolean extraction - call method if it's callable
        def safe_boolean_value(obj, attr_name, default=True):
            """Safely get boolean value, calling method if needed"""
            try:
                value = getattr(obj, attr_name, default)
                if callable(value):
                    return value()
                return bool(value) if value is not None else default
            except (AttributeError, TypeError):
                return default
        
        return {
            "employee_id": str(attendance.employee_id)
        }
    
    def _document_to_attendance(self, document: Dict[str, Any]) -> Attendance:
        """Convert database document to domain entity."""
        # Identity
        attendance_id = document.get("attendance_id")
        employee_id = EmployeeId(document.get("employee_id"))
        attendance_date = document.get("attendance_date")
    
        # Core attributes
        status = AttendanceStatus(document.get("status"))
        working_hours = WorkingHours(document.get("working_hours"))
        
        # Metadata
        created_at = document.get("created_at")
        created_by = document.get("created_by")
        updated_at = document.get("updated_at")
        updated_by = document.get("updated_by")
        
        # Location tracking (optional)
        check_in_location = document.get("check_in_location")
        check_out_location = document.get("check_out_location")
        
        # Comments and notes
        comments = document.get("comments")
        admin_notes = document.get("admin_notes")
    
        return Attendance(
            attendance_id=attendance_id,
            employee_id=employee_id,
            attendance_date=attendance_date,
            status=status,
            working_hours=working_hours,
            created_at=created_at,
            created_by=created_by,
            updated_at=updated_at,
            updated_by=updated_by,
            check_in_location=check_in_location,
            check_out_location=check_out_location,
            comments=comments,
            admin_notes=admin_notes
    )
    
    async def _publish_events(self, events: List[Any]) -> None:
        """Publish domain events."""
        # Implementation would depend on event publisher
        for event in events:
            logger.info(f"Publishing event: {type(event).__name__}")
    
    # Command Repository Implementation
    async def save(self, attendance: Attendance) -> Attendance:
        """Save a attendance (create or update)."""
        try:
            collection = await self._get_collection()
            document = self._attendance_to_document(attendance)
            
            # Use upsert based on employee_id for simplicity
            filter_query = {"employee_id": str(attendance.employee_id)}
            
            result = await collection.replace_one(
                filter_query,
                document,
                upsert=True
            )
            
            # Publish events based on operation
            events = []
            if result.upserted_id:
                events.append(AttendanceCreatedEvent(
                    event_id=f"attendance_created_{attendance.employee_id}_{datetime.utcnow().isoformat()}",
                    occurred_at=datetime.utcnow(),
                    attendance_id=str(attendance.employee_id),  # Using employee_id as attendance_id for now
                    employee_id=str(attendance.employee_id),
                    attendance_date=str(attendance.attendance_date) if hasattr(attendance, 'attendance_date') else datetime.utcnow().date().isoformat(),
                    initial_status=str(attendance.status) if hasattr(attendance, 'status') else "present",
                    created_by="system"
                ))
                logger.info(f"Created attendance: {attendance.employee_id}")
            else:
                events.append(AttendanceUpdatedEvent(
                    event_id=f"attendance_updated_{attendance.employee_id}_{datetime.utcnow().isoformat()}",
                    occurred_at=datetime.utcnow(),
                    attendance_id=str(attendance.employee_id),  # Using employee_id as attendance_id for now
                    employee_id=str(attendance.employee_id),
                    previous_status="unknown",  # Would need to fetch from DB in real implementation
                    new_status=str(attendance.status) if hasattr(attendance, 'status') else "present",
                    updated_by="system"
                ))
                logger.info(f"Updated attendance: {attendance.employee_id}")
            
            await self._publish_events(events)
            return attendance
            
        except Exception as e:
            logger.error(f"Error saving attendance: {e}")
            raise
    
    async def save_batch(self, attendances: List[Attendance]) -> List[Attendance]:
        """Save multiple users in a batch operation."""
        try:
            # Group users by organisation
            attendances_by_org = {}
            for attendance in attendances:
                org_id = attendance.organisation_id or "pms_global_database"
                if org_id not in attendances_by_org:
                    attendances_by_org[org_id] = []
                attendances_by_org[org_id].append(attendance)
            
            saved_attendances = []
            for org_id, org_attendances in attendances_by_org.items():
                collection = await self._get_collection(org_id)
                
                # Prepare bulk operations
                operations = []
                for attendance in org_attendances:
                    document = self._attendance_to_document(attendance)
                    operations.append({
                        "replaceOne": {
                            "filter": {"attendance_id": str(attendance.attendance_id)},
                            "replacement": document,
                            "upsert": True
                        }
                    })
                
                # Execute bulk write
                if operations:
                    await collection.bulk_write(operations)
                    saved_attendances.extend(org_attendances)
                    
                    # Publish events for all attendances
                    for attendance in org_attendances:
                        await self._publish_events(attendance.get_domain_events())
                        attendance.clear_domain_events()
            
            logger.info(f"Batch saved {len(saved_attendances)} attendances")
            return saved_attendances
            
        except Exception as e:
            logger.error(f"Error in batch save: {e}")
            raise
    
    async def delete(self, attendance_id: str, soft_delete: bool = True, hostname: Optional[str] = None) -> bool:
        """Delete a attendance by ID."""
        try:
            # For soft delete, we need to find the user first to get organisation
            attendance = await self.get_by_id(attendance_id, hostname)
            if not attendance:
                return False
            
            collection = await self._get_collection(hostname)
            
            if soft_delete:
                # Soft delete - mark as deleted
                result = await collection.update_one(
                    {"attendance_id": str(attendance_id)},
                    {
                        "$set": {
                            "is_deleted": True,
                            "deleted_at": datetime.utcnow(),
                            "status": AttendanceStatus.INACTIVE.value
                        }
                    }
                )
            else:
                # Hard delete
                result = await collection.delete_one({"attendance_id": str(attendance_id)})
            
            if result.modified_count > 0 or result.deleted_count > 0:
                # Publish delete event
                delete_event = AttendanceDeletedEvent(
                    event_id=f"attendance_deleted_{attendance_id}_{datetime.utcnow().isoformat()}",
                    occurred_at=datetime.utcnow(),
                    attendance_id=attendance_id,
                    employee_id=attendance.employee_id if attendance else "unknown",
                    deleted_by="system",
                    deletion_reason="Soft delete" if soft_delete else "Hard delete"
                )
                await self._publish_events([delete_event])
                
                logger.info(f"Attendance deleted: {attendance_id} (soft: {soft_delete})")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting attendance {attendance_id}: {e}")
            raise
    
    # Query Repository Implementation
    async def get_by_id(self, attendance_id: str, organisation_id: Optional[str] = None) -> Optional[Attendance]:
        """Get attendance by ID."""
        try:
            collection = await self._get_collection(organisation_id)
            document = await collection.find_one({
                "attendance_id": str(attendance_id),
                "is_deleted": {"$ne": True}
            })
            
            if document:
                return self._document_to_attendance(document)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting attendance by ID {attendance_id}: {e}")
            raise
    
    async def get_by_employee_id(self, employee_id: EmployeeId, organisation_id: Optional[str] = None) -> Optional[Attendance]:
        """Get attendance by employee ID."""
        try:
            collection = await self._get_collection(organisation_id)
            document = await collection.find_one({
                "employee_id": str(employee_id),
                "is_deleted": {"$ne": True}
            })
            
            if document:
                return self._document_to_attendance(document)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting attendance by employee ID {employee_id}: {e}")
            raise
    
    async def get_by_attendance_date(self, attendance_date: date, organisation_id: Optional[str] = None) -> Optional[Attendance]:
        """Get attendance by attendance date."""
        try:
            collection = await self._get_collection(organisation_id)
            document = await collection.find_one({
                "attendance_date": attendance_date,
                "is_deleted": {"$ne": True}
            })
            
            if document:
                return self._document_to_attendance(document)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting attendance by attendance date {attendance_date}: {e}")
            raise
    
    async def get_by_status(self, status: AttendanceStatus, organisation_id: Optional[str] = None) -> Optional[Attendance]:
        """Get attendance by status."""
        try:
            collection = await self._get_collection(organisation_id)
            document = await collection.find_one({
                "status": status.value,
                "is_deleted": {"$ne": True}
            })
            
            if document:
                return self._document_to_attendance(document)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting attendance by status {status}: {e}")
            raise
    
    async def get_by_working_hours(self, working_hours: WorkingHours, organisation_id: Optional[str] = None) -> Optional[Attendance]:
        """Get attendance by working hours."""
        try:
            collection = await self._get_collection(organisation_id)
            document = await collection.find_one({
                "working_hours": working_hours.value,
                "is_deleted": {"$ne": True}
            })
            
            if document:
                return self._document_to_attendance(document)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting attendance by working hours {working_hours}: {e}")
            raise
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        include_inactive: bool = False,
        include_deleted: bool = False,
        organisation_id: Optional[str] = None
    ) -> List[Attendance]:
        """Get all attendances with pagination."""
        try:
            collection = await self._get_collection(organisation_id)
            
            # Build filter
            filter_query = {}
            if not include_deleted:
                filter_query["is_deleted"] = {"$ne": True}
            if not include_inactive:
                filter_query["is_active"] = True
            
            # Execute query
            cursor = collection.find(filter_query).skip(skip).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            attendances = [self._document_to_attendance(doc) for doc in documents]
            logger.info(f"Retrieved {len(attendances)} attendances")
            return attendances
            
        except Exception as e:
            logger.error(f"Error getting all attendances: {e}")
            raise
    
    async def search(self, filters: AttendanceSearchFiltersDTO, organisation_id: Optional[str] = None) -> List[Attendance]:
        """Search attendances with filters."""
        try:
            collection = await self._get_collection(organisation_id)
            
            # Build search query
            query = {}
            
            # Text search
            if filters.search_term:
                query["$or"] = [
                    {"employee_id": {"$regex": filters.search_term, "$options": "i"}},
                    {"attendance_date": {"$regex": filters.search_term, "$options": "i"}},
                    {"status": {"$regex": filters.search_term, "$options": "i"}}
                ]
            
            # Employee ID filter
            if filters.employee_id:
                query["employee_id"] = filters.employee_id
            
            # Attendance date filter
            if filters.attendance_date:
                query["attendance_date"] = filters.attendance_date
            
            # Working hours filter
            if filters.working_hours:
                query["working_hours"] = filters.working_hours
            
                # Status filter
            if filters.status:
                query["status"] = filters.status
            
            # Date range filters
            if filters.attendance_date_from or filters.attendance_date_to:
                date_filter = {}
                if filters.attendance_date_from:
                    date_filter["$gte"] = filters.attendance_date_from
                if filters.attendance_date_to:
                    date_filter["$lte"] = filters.attendance_date_to
                query["attendance_date"] = date_filter
            
            # Active/deleted filters
            if not filters.include_deleted:
                query["is_deleted"] = {"$ne": True}
            if not filters.include_inactive:
                query["is_active"] = True
            
            # Execute query with pagination
            cursor = collection.find(query)
            
            # Apply sorting
            if filters.sort_by:
                sort_direction = DESCENDING if filters.sort_desc else ASCENDING
                cursor = cursor.sort(filters.sort_by, sort_direction)
            
            # Apply pagination
            cursor = cursor.skip(filters.skip).limit(filters.limit)
            
            documents = await cursor.to_list(length=filters.limit)
            attendances = [self._document_to_attendance(doc) for doc in documents]
            
            logger.info(f"Search returned {len(attendances)} attendances")
            return attendances
            
        except Exception as e:
            logger.error(f"Error searching attendances: {e}")
            raise
    

    
    # Count methods
    async def count_total(self, include_deleted: bool = False, organisation_id: Optional[str] = None) -> int:
        """Count total attendances."""
        try:
            collection = await self._get_collection(organisation_id)
            filter_query = {}
            if not include_deleted:
                filter_query["is_deleted"] = {"$ne": True}
            
            return await collection.count_documents(filter_query)
            
        except Exception as e:
            logger.error(f"Error counting total users: {e}")
            raise
    
    async def count_by_status(self, status: AttendanceStatus, organisation_id: Optional[str] = None) -> int:
        """Count attendances by status."""
        try:
            collection = await self._get_collection(organisation_id)
            return await collection.count_documents({
                "status": status.value,
                "is_deleted": {"$ne": True}
            })
            
        except Exception as e:
            logger.error(f"Error counting attendances by status {status}: {e}")
            raise
    
    # ==================== FACTORY METHODS IMPLEMENTATION ====================
    # These methods are required by the repository interfaces but are not used
    # in the current dependency injection architecture. They return self since
    # this repository implements all user repository interfaces.
    
    def create_command_repository(self) -> AttendanceCommandRepository:
        """Create command repository instance."""
        return self
    
    def create_query_repository(self) -> AttendanceQueryRepository:
        """Create query repository instance."""
        return self
    
    def create_analytics_repository(self) -> AttendanceAnalyticsRepository:
        """Create analytics repository instance."""
        return self
    
    def create_reports_repository(self) -> AttendanceReportsRepository:
        """Create reports repository instance."""
        return self
    
    def create_bulk_operations_repository(self) -> AttendanceBulkOperationsRepository:
        """Create bulk operations repository instance."""
        return self

    # New required interface methods
    async def delete_by_employee_and_date(self, employee_id: str, attendance_date: date) -> bool:
        """Delete attendance record by employee and date"""
        try:
            collection = await self._get_collection()
            result = await collection.delete_one({
                "employee_id": employee_id,
                "attendance_date": attendance_date.isoformat()
            })
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting attendance by employee and date: {e}")
            raise

    async def get_by_employee_and_date(self, employee_id: str, attendance_date: date) -> Optional[Attendance]:
        """Get attendance record by employee ID and date"""
        try:
            collection = await self._get_collection()
            document = await collection.find_one({
                "employee_id": employee_id,
                "attendance_date": attendance_date.isoformat(),
                "is_deleted": {"$ne": True}
            })
            
            if document:
                return self._document_to_attendance(document)
            return None
        except Exception as e:
            logger.error(f"Error getting attendance by employee and date: {e}")
            raise

    async def get_by_employee(
        self,
        employee_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Attendance]:
        """Get attendance records by employee ID with optional date range"""
        try:
            collection = await self._get_collection()
            query = {"employee_id": employee_id, "is_deleted": {"$ne": True}}
            
            if start_date or end_date:
                date_query = {}
                if start_date:
                    date_query["$gte"] = start_date.isoformat()
                if end_date:
                    date_query["$lte"] = end_date.isoformat()
                query["attendance_date"] = date_query
            
            cursor = collection.find(query)
            if offset:
                cursor = cursor.skip(offset)
            if limit:
                cursor = cursor.limit(limit)
                
            documents = await cursor.to_list(length=limit)
            return [self._document_to_attendance(doc) for doc in documents]
        except Exception as e:
            logger.error(f"Error getting attendance by employee: {e}")
            raise

    async def get_by_date(
        self,
        attendance_date: date,
        employee_ids: Optional[List[str]] = None
    ) -> List[Attendance]:
        """Get attendance records by date with optional employee filter"""
        try:
            collection = await self._get_collection()
            query = {
                "attendance_date": attendance_date.isoformat(),
                "is_deleted": {"$ne": True}
            }
            
            if employee_ids:
                query["employee_id"] = {"$in": employee_ids}
                
            documents = await collection.find(query).to_list(length=None)
            return [self._document_to_attendance(doc) for doc in documents]
        except Exception as e:
            logger.error(f"Error getting attendance by date: {e}")
            raise

    async def get_by_date_range(
        self,
        start_date: date,
        end_date: date,
        employee_ids: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Attendance]:
        """Get attendance records by date range with optional employee filter"""
        try:
            collection = await self._get_collection()
            query = {
                "attendance_date": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                },
                "is_deleted": {"$ne": True}
            }
            
            if employee_ids:
                query["employee_id"] = {"$in": employee_ids}
                
            cursor = collection.find(query)
            if offset:
                cursor = cursor.skip(offset)
            if limit:
                cursor = cursor.limit(limit)
                
            documents = await cursor.to_list(length=limit)
            return [self._document_to_attendance(doc) for doc in documents]
        except Exception as e:
            logger.error(f"Error getting attendance by date range: {e}")
            raise

    async def count_by_filters(self, filters: AttendanceSearchFiltersDTO) -> int:
        """Count attendance records matching filters"""
        try:
            collection = await self._get_collection()
            
            # Build search query (reuse search logic)
            query = {}
            
            if filters.employee_id:
                query["employee_id"] = filters.employee_id
                
            if filters.start_date or filters.end_date:
                date_filter = {}
                if filters.start_date:
                    date_filter["$gte"] = filters.start_date.isoformat()
                if filters.end_date:
                    date_filter["$lte"] = filters.end_date.isoformat()
                query["attendance_date"] = date_filter
                
            if not filters.include_deleted:
                query["is_deleted"] = {"$ne": True}
                
            return await collection.count_documents(query)
        except Exception as e:
            logger.error(f"Error counting attendance by filters: {e}")
            raise

    async def get_pending_check_outs(self, date: Optional[date] = None) -> List[Attendance]:
        """Get attendance records with check-in but no check-out"""
        try:
            collection = await self._get_collection()
            query = {
                "check_in_time": {"$exists": True, "$ne": None},
                "check_out_time": {"$exists": False},
                "is_deleted": {"$ne": True}
            }
            
            if date:
                query["attendance_date"] = date.isoformat()
                
            documents = await collection.find(query).to_list(length=None)
            return [self._document_to_attendance(doc) for doc in documents]
        except Exception as e:
            logger.error(f"Error getting pending check outs: {e}")
            raise

    async def get_regularization_requests(
        self,
        employee_ids: Optional[List[str]] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Attendance]:
        """Get attendance records that need regularization"""
        try:
            collection = await self._get_collection()
            query = {
                "is_regularized": {"$ne": True},
                "needs_regularization": True,
                "is_deleted": {"$ne": True}
            }
            
            if employee_ids:
                query["employee_id"] = {"$in": employee_ids}
                
            if start_date or end_date:
                date_filter = {}
                if start_date:
                    date_filter["$gte"] = start_date.isoformat()
                if end_date:
                    date_filter["$lte"] = end_date.isoformat()
                query["attendance_date"] = date_filter
                
            documents = await collection.find(query).to_list(length=None)
            return [self._document_to_attendance(doc) for doc in documents]
        except Exception as e:
            logger.error(f"Error getting regularization requests: {e}")
            raise

    async def exists_by_employee_and_date(self, employee_id: str, attendance_date: date) -> bool:
        """Check if attendance record exists for employee and date"""
        try:
            collection = await self._get_collection()
            count = await collection.count_documents({
                "employee_id": employee_id,
                "attendance_date": attendance_date.isoformat(),
                "is_deleted": {"$ne": True}
            })
            return count > 0
        except Exception as e:
            logger.error(f"Error checking attendance existence: {e}")
            raise

    # Analytics Repository Implementation
    async def get_employee_summary(
        self,
        employee_id: str,
        start_date: date,
        end_date: date
    ) -> AttendanceSummaryDTO:
        """Get attendance summary for an employee"""
        try:
            collection = await self._get_collection()
            # This is a placeholder implementation
            # You would implement actual aggregation logic here
            return AttendanceSummaryDTO(
                employee_id=employee_id,
                total_days=0,
                present_days=0,
                absent_days=0,
                late_days=0,
                half_days=0,
                work_from_home_days=0,
                leave_days=0,
                holiday_days=0,
                total_working_hours=0.0,
                total_overtime_hours=0.0,
                average_working_hours=0.0,
                attendance_percentage=0.0
            )
        except Exception as e:
            logger.error(f"Error getting employee summary: {e}")
            raise

    async def get_multiple_employee_summaries(
        self,
        employee_ids: List[str],
        start_date: date,
        end_date: date
    ) -> List[AttendanceSummaryDTO]:
        """Get attendance summaries for multiple employees"""
        try:
            summaries = []
            for employee_id in employee_ids:
                summary = await self.get_employee_summary(employee_id, start_date, end_date)
                summaries.append(summary)
            return summaries
        except Exception as e:
            logger.error(f"Error getting multiple employee summaries: {e}")
            raise

    async def get_daily_statistics(self, date: date) -> AttendanceStatisticsDTO:
        """Get daily attendance statistics"""
        try:
            # Placeholder implementation
            return AttendanceStatisticsDTO(
                total_employees=0,
                present_today=0,
                absent_today=0,
                late_today=0,
                on_leave_today=0,
                work_from_home_today=0,
                checked_in=0,
                checked_out=0,
                pending_check_out=0,
                average_working_hours=0.0,
                total_overtime_hours=0.0,
                attendance_percentage=0.0
            )
        except Exception as e:
            logger.error(f"Error getting daily statistics: {e}")
            raise

    async def get_period_statistics(
        self,
        start_date: date,
        end_date: date,
        employee_ids: Optional[List[str]] = None
    ) -> AttendanceStatisticsDTO:
        """Get attendance statistics for a period"""
        try:
            # Placeholder implementation
            return AttendanceStatisticsDTO(
                total_employees=0,
                present_today=0,
                absent_today=0,
                late_today=0,
                on_leave_today=0,
                work_from_home_today=0,
                checked_in=0,
                checked_out=0,
                pending_check_out=0,
                average_working_hours=0.0,
                total_overtime_hours=0.0,
                attendance_percentage=0.0
            )
        except Exception as e:
            logger.error(f"Error getting period statistics: {e}")
            raise

    async def get_department_attendance(
        self,
        date: date,
        department_ids: Optional[List[str]] = None
    ) -> List[DepartmentAttendanceDTO]:
        """Get department-wise attendance for a date"""
        try:
            # Placeholder implementation
            return []
        except Exception as e:
            logger.error(f"Error getting department attendance: {e}")
            raise

    async def get_attendance_trends(
        self,
        start_date: date,
        end_date: date,
        employee_ids: Optional[List[str]] = None
    ) -> List[AttendanceTrendDTO]:
        """Get attendance trends over a period"""
        try:
            # Placeholder implementation
            return []
        except Exception as e:
            logger.error(f"Error getting attendance trends: {e}")
            raise

    async def get_late_arrivals(
        self,
        start_date: date,
        end_date: date,
        employee_ids: Optional[List[str]] = None
    ) -> List[Attendance]:
        """Get late arrival records"""
        try:
            collection = await self._get_collection()
            query = {
                "status": "late",
                "attendance_date": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                },
                "is_deleted": {"$ne": True}
            }
            
            if employee_ids:
                query["employee_id"] = {"$in": employee_ids}
                
            documents = await collection.find(query).to_list(length=None)
            return [self._document_to_attendance(doc) for doc in documents]
        except Exception as e:
            logger.error(f"Error getting late arrivals: {e}")
            raise

    async def get_overtime_records(
        self,
        start_date: date,
        end_date: date,
        employee_ids: Optional[List[str]] = None,
        min_overtime_hours: Optional[Decimal] = None
    ) -> List[Attendance]:
        """Get overtime records"""
        try:
            collection = await self._get_collection()
            query = {
                "overtime_hours": {"$gt": 0},
                "attendance_date": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                },
                "is_deleted": {"$ne": True}
            }
            
            if employee_ids:
                query["employee_id"] = {"$in": employee_ids}
                
            if min_overtime_hours:
                query["overtime_hours"]["$gte"] = float(min_overtime_hours)
                
            documents = await collection.find(query).to_list(length=None)
            return [self._document_to_attendance(doc) for doc in documents]
        except Exception as e:
            logger.error(f"Error getting overtime records: {e}")
            raise

    async def get_absent_employees(
        self,
        date: date,
        department_ids: Optional[List[str]] = None
    ) -> List[str]:
        """Get list of absent employee IDs for a date"""
        try:
            collection = await self._get_collection()
            query = {
                "status": "absent",
                "attendance_date": date.isoformat(),
                "is_deleted": {"$ne": True}
            }
            
            # Note: department filtering would require joining with employee data
            # This is a simplified implementation
            
            documents = await collection.find(query, {"employee_id": 1}).to_list(length=None)
            return [doc["employee_id"] for doc in documents]
        except Exception as e:
            logger.error(f"Error getting absent employees: {e}")
            raise

    async def get_working_hours_distribution(
        self,
        start_date: date,
        end_date: date,
        employee_ids: Optional[List[str]] = None
    ) -> Dict[str, int]:
        """Get working hours distribution"""
        try:
            # Placeholder implementation
            return {}
        except Exception as e:
            logger.error(f"Error getting working hours distribution: {e}")
            raise

    async def get_attendance_percentage_by_employee(
        self,
        start_date: date,
        end_date: date,
        employee_ids: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """Get attendance percentage by employee"""
        try:
            # Placeholder implementation
            return {}
        except Exception as e:
            logger.error(f"Error getting attendance percentage by employee: {e}")
            raise

    async def get_monthly_attendance_summary(
        self,
        year: int,
        month: int,
        employee_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get monthly attendance summary"""
        try:
            # Placeholder implementation
            return {}
        except Exception as e:
            logger.error(f"Error getting monthly attendance summary: {e}")
            raise

    # Reports Repository Implementation - placeholder methods
    async def generate_daily_report(
        self,
        date: date,
        employee_ids: Optional[List[str]] = None,
        department_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate daily attendance report"""
        return {}

    async def generate_weekly_report(
        self,
        start_date: date,
        employee_ids: Optional[List[str]] = None,
        department_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate weekly attendance report"""
        return {}

    async def generate_monthly_report(
        self,
        year: int,
        month: int,
        employee_ids: Optional[List[str]] = None,
        department_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate monthly attendance report"""
        return {}

    async def generate_custom_report(
        self,
        start_date: date,
        end_date: date,
        employee_ids: Optional[List[str]] = None,
        department_ids: Optional[List[str]] = None,
        include_summary: bool = True,
        include_details: bool = True
    ) -> Dict[str, Any]:
        """Generate custom attendance report"""
        return {}

    async def export_to_csv(
        self,
        attendances: List[Attendance],
        include_summary: bool = False
    ) -> str:
        """Export attendance records to CSV format"""
        return ""

    async def export_to_excel(
        self,
        attendances: List[Attendance],
        include_summary: bool = False,
        include_charts: bool = False
    ) -> bytes:
        """Export attendance records to Excel format"""
        return b""

    # Bulk Operations Repository Implementation - placeholder methods
    async def bulk_import(
        self,
        attendance_data: List[Dict[str, Any]],
        import_mode: str = "create"
    ) -> Dict[str, Any]:
        """Bulk import attendance records"""
        return {}

    async def bulk_update_status(
        self,
        attendance_ids: List[str],
        new_status: str,
        updated_by: str,
        reason: Optional[str] = None
    ) -> int:
        """Bulk update attendance status"""
        return 0

    async def bulk_regularize(
        self,
        attendance_ids: List[str],
        reason: str,
        regularized_by: str
    ) -> int:
        """Bulk regularize attendance records"""
        return 0

    async def bulk_delete(
        self,
        attendance_ids: List[str],
        deleted_by: str,
        reason: str
    ) -> int:
        """Bulk delete attendance records"""
        return 0

    async def auto_mark_absent(
        self,
        date: date,
        employee_ids: Optional[List[str]] = None,
        exclude_on_leave: bool = True,
        exclude_holidays: bool = True
    ) -> int:
        """Auto-mark employees as absent for a date"""
        return 0

    async def auto_mark_holidays(
        self,
        date: date,
        employee_ids: Optional[List[str]] = None
    ) -> int:
        """Auto-mark employees as on holiday for a date"""
        return 0 