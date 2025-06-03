"""
MongoDB User Repository Implementation
Following SOLID principles and DDD patterns for user data access
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
from pymongo.collection import Collection

from app.domain.entities.attendance import Attendance
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.attendance_status import AttendanceStatus
from app.application.interfaces.repositories.user_repository import (
    AttendanceCommandRepository, AttendanceQueryRepository, AttendanceAnalyticsRepository,
    AttendanceProfileRepository, AttendanceBulkOperationsRepository, AttendanceRepository
)
from app.application.dto.attendance_dto import (
    AttendanceSearchFiltersDTO, AttendanceStatisticsDTO, AttendanceAnalyticsDTO,
    AttendanceProfileCompletionDTO
)
from app.infrastructure.database.database_connector import DatabaseConnector
from app.domain.events.attendance_events import AttendanceCreated, AttendanceUpdated, AttendanceDeleted
from app.config.mongodb_config import get_mongodb_connection_string, get_mongodb_client_options
from app.domain.value_objects.working_hours import WorkingHours

logger = logging.getLogger(__name__)


class MongoDBAttendanceRepository(AttendanceRepository):
    """
    MongoDB implementation of user repository following DDD patterns.
    
    Implements all user repository interfaces in a single class for simplicity
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
    async def save(self, attendance: Attendance, hostname: str) -> Attendance:
        """Save a user (create or update)."""
        try:
            collection = await self._get_collection(hostname)
            document = self._attendance_to_document(attendance)
            
            # Use upsert to handle both create and update
            result = await collection.replace_one(
                {"attendance_id": str(attendance.attendance_id)},
                document,
                upsert=True
            )
            
            # Publish domain events
            await self._publish_events(attendance.get_domain_events())
            attendance.clear_domain_events()
            
            logger.info(f"Attendance saved: {attendance.attendance_id}")
            return attendance
            
        except DuplicateKeyError as e:
            logger.error(f"Duplicate key error saving attendance {attendance.attendance_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error saving attendance {attendance.attendance_id}: {e}")
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
    
    async def delete(self, attendance_id: AttendanceId, soft_delete: bool = True, hostname: Optional[str] = None) -> bool:
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
                delete_event = AttendanceDeleted(
                    attendance_id=attendance_id,
                    organisation_id=hostname,
                    soft_delete=soft_delete,
                    deleted_at=datetime.utcnow()
                )
                await self._publish_events([delete_event])
                
                logger.info(f"Attendance deleted: {attendance_id} (soft: {soft_delete})")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting attendance {attendance_id}: {e}")
            raise
    
    # Query Repository Implementation
    async def get_by_id(self, attendance_id: AttendanceId, organisation_id: Optional[str] = None) -> Optional[Attendance]:
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
    
    def create_profile_repository(self) -> AttendanceProfileRepository:
        """Create profile repository instance."""
        return self
    
    def create_bulk_operations_repository(self) -> AttendanceBulkOperationsRepository:
        """Create bulk operations repository instance."""
        return self 