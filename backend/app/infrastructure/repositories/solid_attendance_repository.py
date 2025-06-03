"""
SOLID-Compliant Attendance Repository Implementation
Replaces the procedural attendance_database.py with proper SOLID architecture
"""

import logging
import uuid
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date, timedelta
from decimal import Decimal
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

# Import domain entities
try:
    from app.domain.entities.attendance import Attendance
    from app.domain.value_objects.employee_id import EmployeeId
    from app.domain.value_objects.attendance_status import AttendanceStatus, AttendanceStatusType
    from app.domain.value_objects.working_hours import WorkingHours
except ImportError:
    # Fallback classes for migration compatibility
    class Attendance:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        def dict(self):
            return {k: v for k, v in self.__dict__.items()}
    
    class EmployeeId:
        def __init__(self, value: str):
            self.value = value
        def __str__(self):
            return self.value
    
    class AttendanceStatus:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class AttendanceStatusType:
        PRESENT = "present"
        ABSENT = "absent"
        LATE = "late"
        HALF_DAY = "half_day"
        ON_LEAVE = "on_leave"
        HOLIDAY = "holiday"
    
    class WorkingHours:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

# Import application interfaces
try:
    from app.application.interfaces.repositories.attendance_repository import (
        AttendanceCommandRepository, AttendanceQueryRepository, 
        AttendanceAnalyticsRepository, AttendanceReportsRepository,
        AttendanceBulkOperationsRepository, AttendanceRepository
    )
except ImportError:
    # Fallback interfaces
    from abc import ABC, abstractmethod
    
    class AttendanceCommandRepository(ABC):
        pass
    
    class AttendanceQueryRepository(ABC):
        pass
    
    class AttendanceAnalyticsRepository(ABC):
        pass
    
    class AttendanceReportsRepository(ABC):
        pass
    
    class AttendanceBulkOperationsRepository(ABC):
        pass
    
    class AttendanceRepository(ABC):
        pass

# Import DTOs
try:
    from app.application.dto.attendance_dto import (
        AttendanceSearchFiltersDTO, AttendanceSummaryDTO, 
        AttendanceStatisticsDTO, DepartmentAttendanceDTO, AttendanceTrendDTO
    )
except ImportError:
    # Fallback DTOs
    class AttendanceSearchFiltersDTO:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class AttendanceSummaryDTO:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class AttendanceStatisticsDTO:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class DepartmentAttendanceDTO:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class AttendanceTrendDTO:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

from .base_repository import BaseRepository
from ..database.database_connector import DatabaseConnector

logger = logging.getLogger(__name__)


class SolidAttendanceRepository(
    BaseRepository[Attendance],
    AttendanceRepository
):
    """
    SOLID-compliant attendance repository implementation.
    
    Replaces the procedural attendance_database.py with proper SOLID architecture:
    - Single Responsibility: Only handles attendance data persistence
    - Open/Closed: Can be extended without modification
    - Liskov Substitution: Implements all attendance repository interfaces
    - Interface Segregation: Implements focused attendance repository interfaces
    - Dependency Inversion: Depends on DatabaseConnector abstraction
    """
    
    def __init__(self, database_connector: DatabaseConnector):
        """
        Initialize attendance repository.
        
        Args:
            database_connector: Database connection abstraction
        """
        super().__init__(database_connector, "attendance")
        
    def _entity_to_document(self, attendance: Attendance) -> Dict[str, Any]:
        """
        Convert Attendance entity to database document.
        
        Args:
            attendance: Attendance entity to convert
            
        Returns:
            Database document representation
        """
        if hasattr(attendance, 'dict'):
            document = attendance.dict()
        elif hasattr(attendance, 'to_dict'):
            document = attendance.to_dict()
        else:
            document = {k: v for k, v in attendance.__dict__.items()}
        
        # Remove the 'id' field if present (MongoDB uses '_id')
        if 'id' in document:
            del document['id']
        
        # Ensure proper field mapping for legacy compatibility
        if 'attendance_id' not in document and hasattr(attendance, 'attendance_id'):
            document['attendance_id'] = getattr(attendance, 'attendance_id')
        
        if 'employee_id' not in document and hasattr(attendance, 'employee_id'):
            employee_id = getattr(attendance, 'employee_id')
            if hasattr(employee_id, 'value'):
                document['employee_id'] = employee_id.value
            else:
                document['employee_id'] = str(employee_id)
        
        if 'date' not in document and hasattr(attendance, 'attendance_date'):
            document['date'] = getattr(attendance, 'attendance_date')
        
        # Handle working hours
        working_hours = getattr(attendance, 'working_hours', None)
        if working_hours:
            if hasattr(working_hours, 'check_in_time'):
                document['checkin_time'] = getattr(working_hours, 'check_in_time')
            if hasattr(working_hours, 'check_out_time'):
                document['checkout_time'] = getattr(working_hours, 'check_out_time')
        
        return document
    
    def _document_to_entity(self, document: Dict[str, Any]) -> Attendance:
        """
        Convert database document to Attendance entity.
        
        Args:
            document: Database document to convert
            
        Returns:
            Attendance entity instance
        """
        # Convert MongoDB _id to id
        if '_id' in document:
            document['id'] = str(document['_id'])
            del document['_id']
        
        # Map legacy fields to new structure
        if 'employee_id' in document and 'employee_id' not in document:
            document['employee_id'] = document['employee_id']
        
        if 'date' in document and 'attendance_date' not in document:
            document['attendance_date'] = document['date']
        
        # Handle legacy time fields
        if 'checkin_time' in document:
            document['check_in_time'] = document['checkin_time']
        if 'checkout_time' in document:
            document['check_out_time'] = document['checkout_time']
        
        return Attendance(**document)
    
    async def _ensure_indexes(self, organisation_id: str) -> None:
        """Ensure necessary indexes for optimal query performance."""
        try:
            collection = await self._get_collection(organisation_id)
            
            # Index for employee and date queries
            await collection.create_index([
                ("employee_id", 1),
                ("date", -1)
            ])
            
            # Index for date range queries
            await collection.create_index([
                ("date", -1)
            ])
            
            # Index for status queries
            await collection.create_index([
                ("status", 1),
                ("date", -1)
            ])
            
            # Unique index for employee and date combination
            await collection.create_index([
                ("employee_id", 1),
                ("date", 1)
            ], unique=True)
            
            logger.info(f"Attendance indexes ensured for organisation: {organisation_id}")
            
        except Exception as e:
            logger.error(f"Error ensuring attendance indexes: {e}")
    
    # Command Repository Implementation
    async def save(self, attendance: Attendance) -> Attendance:
        """
        Save attendance record.
        
        Replaces: create_attendance() function
        """
        try:
            # Get organisation from attendance or use default
            organisation_id = getattr(attendance, 'organisation_id', 'default')
            
            # Ensure indexes
            await self._ensure_indexes(organisation_id)
            
            # Prepare document
            document = self._entity_to_document(attendance)
            
            # Set timestamps
            if not document.get('created_at'):
                document['created_at'] = datetime.utcnow()
            document['updated_at'] = datetime.utcnow()
            
            # Generate attendance_id if not present
            if not document.get('attendance_id'):
                document['attendance_id'] = str(uuid.uuid4())
            
            # Check for existing record
            existing = await self.get_by_employee_and_date(
                document['employee_id'], 
                document['date'].date() if isinstance(document['date'], datetime) else document['date']
            )
            
            if existing:
                # Update existing record
                filters = {"employee_id": document['employee_id'], "date": document['date']}
                success = await self._update_document(
                    filters=filters,
                    update_data=document,
                    organisation_id=organisation_id
                )
                if success:
                    return await self.get_by_employee_and_date(
                        document['employee_id'], 
                        document['date'].date() if isinstance(document['date'], datetime) else document['date']
                    )
                else:
                    raise ValueError("Failed to update attendance record")
            else:
                # Insert new record
                document_id = await self._insert_document(document, organisation_id)
                return await self.get_by_id(str(document_id))
            
        except Exception as e:
            logger.error(f"Error saving attendance: {e}")
            raise
    
    async def save_batch(self, attendances: List[Attendance]) -> List[Attendance]:
        """Save multiple attendance records in batch."""
        try:
            saved_attendances = []
            
            for attendance in attendances:
                try:
                    saved_attendance = await self.save(attendance)
                    saved_attendances.append(saved_attendance)
                except Exception as e:
                    logger.error(f"Error saving attendance in batch: {e}")
                    # Continue with other records
            
            logger.info(f"Batch saved {len(saved_attendances)} attendance records")
            return saved_attendances
            
        except Exception as e:
            logger.error(f"Error in batch save: {e}")
            raise
    
    async def delete(self, attendance_id: str) -> bool:
        """Delete attendance record by ID."""
        try:
            filters = {"attendance_id": attendance_id}
            return await self._delete_document(
                filters=filters,
                organisation_id="default",  # Will be improved with proper org handling
                soft_delete=True
            )
            
        except Exception as e:
            logger.error(f"Error deleting attendance {attendance_id}: {e}")
            return False
    
    async def delete_by_employee_and_date(self, employee_id: str, attendance_date: date) -> bool:
        """Delete attendance record by employee and date."""
        try:
            filters = {"employee_id": employee_id, "date": attendance_date}
            return await self._delete_document(
                filters=filters,
                organisation_id="default",
                soft_delete=True
            )
            
        except Exception as e:
            logger.error(f"Error deleting attendance for {employee_id} on {attendance_date}: {e}")
            return False
    
    # Query Repository Implementation
    async def get_by_id(self, attendance_id: str) -> Optional[Attendance]:
        """Get attendance record by ID."""
        try:
            filters = {"attendance_id": attendance_id}
            documents = await self._execute_query(
                filters=filters,
                limit=1,
                organisation_id="default"
            )
            
            if documents:
                return self._document_to_entity(documents[0])
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving attendance {attendance_id}: {e}")
            return None
    
    async def get_by_employee_and_date(self, employee_id: str, attendance_date: date) -> Optional[Attendance]:
        """Get attendance record by employee ID and date."""
        try:
            # Convert date to datetime for MongoDB query
            if isinstance(attendance_date, date) and not isinstance(attendance_date, datetime):
                start_date = datetime.combine(attendance_date, datetime.min.time())
                end_date = start_date + timedelta(days=1)
                filters = {
                    "employee_id": employee_id,
                    "date": {"$gte": start_date, "$lt": end_date}
                }
            else:
                filters = {"employee_id": employee_id, "date": attendance_date}
            
            documents = await self._execute_query(
                filters=filters,
                limit=1,
                organisation_id="default"
            )
            
            if documents:
                return self._document_to_entity(documents[0])
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving attendance for {employee_id} on {attendance_date}: {e}")
            return None
    
    async def get_by_employee(
        self,
        employee_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Attendance]:
        """
        Get attendance records by employee ID with optional date range.
        
        Replaces: get_employee_attendance_by_month(), get_employee_attendance_by_year()
        """
        try:
            filters = {"employee_id": employee_id}
            
            if start_date or end_date:
                date_filter = {}
                if start_date:
                    date_filter["$gte"] = datetime.combine(start_date, datetime.min.time())
                if end_date:
                    date_filter["$lt"] = datetime.combine(end_date + timedelta(days=1), datetime.min.time())
                filters["date"] = date_filter
            
            documents = await self._execute_query(
                filters=filters,
                skip=offset or 0,
                limit=limit or 100,
                sort_by="date",
                sort_order=-1,
                organisation_id="default"
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error retrieving employee attendance: {e}")
            return []
    
    async def get_by_date(
        self,
        attendance_date: date,
        employee_ids: Optional[List[str]] = None
    ) -> List[Attendance]:
        """Get attendance records by date with optional employee filter."""
        try:
            start_date = datetime.combine(attendance_date, datetime.min.time())
            end_date = start_date + timedelta(days=1)
            
            filters = {
                "date": {"$gte": start_date, "$lt": end_date}
            }
            
            if employee_ids:
                filters["employee_id"] = {"$in": employee_ids}
            
            documents = await self._execute_query(
                filters=filters,
                sort_by="employee_id",
                sort_order=1,
                limit=1000,
                organisation_id="default"
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error retrieving attendance by date: {e}")
            return []
    
    async def get_by_date_range(
        self,
        start_date: date,
        end_date: date,
        employee_ids: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Attendance]:
        """Get attendance records by date range with optional employee filter."""
        try:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date + timedelta(days=1), datetime.min.time())
            
            filters = {
                "date": {"$gte": start_datetime, "$lt": end_datetime}
            }
            
            if employee_ids:
                filters["employee_id"] = {"$in": employee_ids}
            
            documents = await self._execute_query(
                filters=filters,
                skip=offset or 0,
                limit=limit or 1000,
                sort_by="date",
                sort_order=-1,
                organisation_id="default"
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error retrieving attendance by date range: {e}")
            return []
    
    async def search(self, filters: AttendanceSearchFiltersDTO) -> List[Attendance]:
        """Search attendance records with filters."""
        try:
            query_filters = {}
            
            if hasattr(filters, 'employee_ids') and filters.employee_ids:
                query_filters["employee_id"] = {"$in": filters.employee_ids}
            
            if hasattr(filters, 'start_date') and filters.start_date:
                query_filters["date"] = {"$gte": datetime.combine(filters.start_date, datetime.min.time())}
            
            if hasattr(filters, 'end_date') and filters.end_date:
                if "date" in query_filters:
                    query_filters["date"]["$lt"] = datetime.combine(filters.end_date + timedelta(days=1), datetime.min.time())
                else:
                    query_filters["date"] = {"$lt": datetime.combine(filters.end_date + timedelta(days=1), datetime.min.time())}
            
            if hasattr(filters, 'status') and filters.status:
                query_filters["status"] = filters.status
            
            # Get pagination parameters
            page = getattr(filters, 'page', 1)
            page_size = getattr(filters, 'page_size', 50)
            skip = (page - 1) * page_size
            
            documents = await self._execute_query(
                filters=query_filters,
                skip=skip,
                limit=page_size,
                sort_by="date",
                sort_order=-1,
                organisation_id="default"
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error searching attendance: {e}")
            return []
    
    async def count_by_filters(self, filters: AttendanceSearchFiltersDTO) -> int:
        """Count attendance records matching filters."""
        try:
            query_filters = {}
            
            if hasattr(filters, 'employee_ids') and filters.employee_ids:
                query_filters["employee_id"] = {"$in": filters.employee_ids}
            
            if hasattr(filters, 'start_date') and filters.start_date:
                query_filters["date"] = {"$gte": datetime.combine(filters.start_date, datetime.min.time())}
            
            if hasattr(filters, 'end_date') and filters.end_date:
                if "date" in query_filters:
                    query_filters["date"]["$lt"] = datetime.combine(filters.end_date + timedelta(days=1), datetime.min.time())
                else:
                    query_filters["date"] = {"$lt": datetime.combine(filters.end_date + timedelta(days=1), datetime.min.time())}
            
            return await self._count_documents(query_filters, "default")
            
        except Exception as e:
            logger.error(f"Error counting attendance: {e}")
            return 0
    
    async def get_pending_check_outs(self, date: Optional[date] = None) -> List[Attendance]:
        """Get attendance records with check-in but no check-out."""
        try:
            if date is None:
                date = datetime.now().date()
            
            start_date = datetime.combine(date, datetime.min.time())
            end_date = start_date + timedelta(days=1)
            
            filters = {
                "date": {"$gte": start_date, "$lt": end_date},
                "checkin_time": {"$ne": None},
                "checkout_time": None
            }
            
            documents = await self._execute_query(
                filters=filters,
                sort_by="checkin_time",
                sort_order=1,
                limit=100,
                organisation_id="default"
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error retrieving pending check-outs: {e}")
            return []
    
    async def get_regularization_requests(
        self,
        employee_ids: Optional[List[str]] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Attendance]:
        """Get attendance records that need regularization."""
        try:
            filters = {"is_regularized": True}
            
            if employee_ids:
                filters["employee_id"] = {"$in": employee_ids}
            
            if start_date or end_date:
                date_filter = {}
                if start_date:
                    date_filter["$gte"] = datetime.combine(start_date, datetime.min.time())
                if end_date:
                    date_filter["$lt"] = datetime.combine(end_date + timedelta(days=1), datetime.min.time())
                filters["date"] = date_filter
            
            documents = await self._execute_query(
                filters=filters,
                sort_by="date",
                sort_order=-1,
                limit=100,
                organisation_id="default"
            )
            
            return [self._document_to_entity(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error retrieving regularization requests: {e}")
            return []
    
    async def exists_by_employee_and_date(self, employee_id: str, attendance_date: date) -> bool:
        """Check if attendance record exists for employee and date."""
        try:
            attendance = await self.get_by_employee_and_date(employee_id, attendance_date)
            return attendance is not None
            
        except Exception as e:
            logger.error(f"Error checking attendance existence: {e}")
            return False
    
    # Analytics Repository Implementation
    async def get_employee_summary(
        self,
        employee_id: str,
        start_date: date,
        end_date: date
    ) -> AttendanceSummaryDTO:
        """Get attendance summary for an employee."""
        try:
            attendances = await self.get_by_employee(employee_id, start_date, end_date)
            
            total_days = len(attendances)
            present_days = sum(1 for a in attendances if getattr(a, 'status', '') == 'present')
            absent_days = sum(1 for a in attendances if getattr(a, 'status', '') == 'absent')
            late_days = sum(1 for a in attendances if getattr(a, 'status', '') == 'late')
            half_days = sum(1 for a in attendances if getattr(a, 'status', '') == 'half_day')
            
            total_working_hours = sum(
                getattr(a, 'working_hours', 0) if hasattr(a, 'working_hours') else 0 
                for a in attendances
            )
            
            return AttendanceSummaryDTO(
                employee_id=employee_id,
                start_date=start_date,
                end_date=end_date,
                total_days=total_days,
                present_days=present_days,
                absent_days=absent_days,
                late_days=late_days,
                half_days=half_days,
                total_working_hours=total_working_hours,
                attendance_percentage=(present_days / max(total_days, 1)) * 100
            )
            
        except Exception as e:
            logger.error(f"Error getting employee summary: {e}")
            return AttendanceSummaryDTO(
                employee_id=employee_id,
                start_date=start_date,
                end_date=end_date,
                total_days=0,
                present_days=0,
                absent_days=0,
                late_days=0,
                half_days=0,
                total_working_hours=0,
                attendance_percentage=0
            )
    
    async def get_multiple_employee_summaries(
        self,
        employee_ids: List[str],
        start_date: date,
        end_date: date
    ) -> List[AttendanceSummaryDTO]:
        """Get attendance summaries for multiple employees."""
        try:
            summaries = []
            
            for employee_id in employee_ids:
                summary = await self.get_employee_summary(employee_id, start_date, end_date)
                summaries.append(summary)
            
            return summaries
            
        except Exception as e:
            logger.error(f"Error getting multiple employee summaries: {e}")
            return []
    
    async def get_daily_statistics(self, date: date) -> AttendanceStatisticsDTO:
        """
        Get daily attendance statistics.
        
        Replaces: get_todays_attendance_stats()
        """
        try:
            attendances = await self.get_by_date(date)
            
            total_employees = len(attendances)
            present_count = sum(1 for a in attendances if getattr(a, 'checkin_time', None) is not None)
            checked_out_count = sum(1 for a in attendances if getattr(a, 'checkout_time', None) is not None)
            absent_count = sum(1 for a in attendances if getattr(a, 'status', '') == 'absent')
            late_count = sum(1 for a in attendances if getattr(a, 'status', '') == 'late')
            
            return AttendanceStatisticsDTO(
                date=date,
                total_employees=total_employees,
                present_count=present_count,
                absent_count=absent_count,
                late_count=late_count,
                checked_out_count=checked_out_count,
                pending_check_out=present_count - checked_out_count,
                attendance_percentage=(present_count / max(total_employees, 1)) * 100
            )
            
        except Exception as e:
            logger.error(f"Error getting daily statistics: {e}")
            return AttendanceStatisticsDTO(
                date=date,
                total_employees=0,
                present_count=0,
                absent_count=0,
                late_count=0,
                checked_out_count=0,
                pending_check_out=0,
                attendance_percentage=0
            )
    
    async def get_period_statistics(
        self,
        start_date: date,
        end_date: date,
        employee_ids: Optional[List[str]] = None
    ) -> AttendanceStatisticsDTO:
        """Get attendance statistics for a period."""
        try:
            attendances = await self.get_by_date_range(start_date, end_date, employee_ids)
            
            total_records = len(attendances)
            present_count = sum(1 for a in attendances if getattr(a, 'status', '') == 'present')
            absent_count = sum(1 for a in attendances if getattr(a, 'status', '') == 'absent')
            late_count = sum(1 for a in attendances if getattr(a, 'status', '') == 'late')
            
            # Calculate unique employees
            unique_employees = len(set(getattr(a, 'employee_id', '') for a in attendances))
            
            return AttendanceStatisticsDTO(
                start_date=start_date,
                end_date=end_date,
                total_employees=unique_employees,
                total_records=total_records,
                present_count=present_count,
                absent_count=absent_count,
                late_count=late_count,
                attendance_percentage=(present_count / max(total_records, 1)) * 100
            )
            
        except Exception as e:
            logger.error(f"Error getting period statistics: {e}")
            return AttendanceStatisticsDTO(
                start_date=start_date,
                end_date=end_date,
                total_employees=0,
                total_records=0,
                present_count=0,
                absent_count=0,
                late_count=0,
                attendance_percentage=0
            )
    
    # Team-based methods (replacing manager-based functions)
    async def get_team_attendance_by_date(self, manager_id: str, attendance_date: date, hostname: str) -> List[Attendance]:
        """
        Get team attendance for a specific date.
        
        Replaces: get_team_attendance_by_date()
        """
        try:
            # This would require integration with user repository to get team members
            # For now, return empty list as it needs user repository integration
            logger.warning("Team attendance requires user repository integration")
            return []
            
        except Exception as e:
            logger.error(f"Error getting team attendance by date: {e}")
            return []
    
    async def get_team_attendance_by_month(self, manager_id: str, month: int, year: int, hostname: str) -> List[Attendance]:
        """
        Get team attendance for a month.
        
        Replaces: get_team_attendance_by_month()
        """
        try:
            # This would require integration with user repository to get team members
            # For now, return empty list as it needs user repository integration
            logger.warning("Team attendance requires user repository integration")
            return []
            
        except Exception as e:
            logger.error(f"Error getting team attendance by month: {e}")
            return []
    
    async def get_team_attendance_by_year(self, manager_id: str, year: int, hostname: str) -> List[Attendance]:
        """
        Get team attendance for a year.
        
        Replaces: get_team_attendance_by_year()
        """
        try:
            # This would require integration with user repository to get team members
            # For now, return empty list as it needs user repository integration
            logger.warning("Team attendance requires user repository integration")
            return []
            
        except Exception as e:
            logger.error(f"Error getting team attendance by year: {e}")
            return []
    
    # Legacy compatibility methods
    async def create_attendance_legacy(self, employee_id: str, hostname: str, check_in: bool = True) -> str:
        """
        Legacy compatibility for create_attendance() function.
        
        Args:
            employee_id: Employee ID
            hostname: Organisation hostname
            check_in: Whether this is a check-in (True) or check-out (False)
            
        Returns:
            Attendance ID
        """
        try:
            now = datetime.now()
            attendance_id = str(uuid.uuid4())
            
            # Create simple attendance object
            attendance_data = {
                "attendance_id": attendance_id,
                "employee_id": employee_id,
                "date": now,
                "checkin_time": now if check_in else None,
                "checkout_time": None if check_in else now,
                "status": "present" if check_in else "present",
                "created_at": now,
                "updated_at": now
            }
            
            # Save using new method
            document_id = await self._insert_document(attendance_data, hostname)
            
            logger.info(f"Created attendance (legacy): {attendance_id}")
            return attendance_id
            
        except Exception as e:
            logger.error(f"Error creating attendance (legacy): {e}")
            raise
    
    async def get_employee_attendance_by_month_legacy(self, employee_id: str, month: int, year: int, hostname: str) -> List[Dict[str, Any]]:
        """
        Legacy compatibility for get_employee_attendance_by_month() function.
        
        Returns raw documents for backward compatibility.
        """
        try:
            start_date = date(year, month, 1)
            if month == 12:
                end_date = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(year, month + 1, 1) - timedelta(days=1)
            
            attendances = await self.get_by_employee(employee_id, start_date, end_date)
            
            # Convert to legacy format
            legacy_attendances = []
            for attendance in attendances:
                if hasattr(attendance, 'dict'):
                    legacy_attendances.append(attendance.dict())
                else:
                    legacy_attendances.append({
                        "attendance_id": getattr(attendance, 'attendance_id', ''),
                        "employee_id": getattr(attendance, 'employee_id', employee_id),
                        "date": getattr(attendance, 'date', None),
                        "checkin_time": getattr(attendance, 'checkin_time', None),
                        "checkout_time": getattr(attendance, 'checkout_time', None),
                        "status": getattr(attendance, 'status', 'absent')
                    })
            
            return legacy_attendances
            
        except Exception as e:
            logger.error(f"Error getting employee attendance by month (legacy): {e}")
            return []
    
    async def get_todays_attendance_stats_legacy(self, hostname: str) -> Dict[str, int]:
        """
        Legacy compatibility for get_todays_attendance_stats() function.
        
        Returns:
            Statistics dictionary
        """
        try:
            today = datetime.now().date()
            stats = await self.get_daily_statistics(today)
            
            return {
                "total_users": getattr(stats, 'total_employees', 0),
                "checked_in": getattr(stats, 'present_count', 0),
                "checked_out": getattr(stats, 'checked_out_count', 0),
                "pending_check_in": getattr(stats, 'total_employees', 0) - getattr(stats, 'present_count', 0),
                "pending_check_out": getattr(stats, 'pending_check_out', 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting today's attendance stats (legacy): {e}")
            return {
                "total_users": 0,
                "checked_in": 0,
                "checked_out": 0,
                "pending_check_in": 0,
                "pending_check_out": 0
            }
    
    # Placeholder implementations for remaining interface methods
    async def get_department_attendance(
        self,
        date: date,
        department_ids: Optional[List[str]] = None
    ) -> List[DepartmentAttendanceDTO]:
        """Get department-wise attendance for a date."""
        # Placeholder - requires department integration
        return []
    
    async def get_attendance_trends(
        self,
        start_date: date,
        end_date: date,
        employee_ids: Optional[List[str]] = None
    ) -> List[AttendanceTrendDTO]:
        """Get attendance trends over a period."""
        # Placeholder - requires trend analysis implementation
        return []
    
    async def get_late_arrivals(
        self,
        start_date: date,
        end_date: date,
        employee_ids: Optional[List[str]] = None
    ) -> List[Attendance]:
        """Get late arrival records."""
        try:
            attendances = await self.get_by_date_range(start_date, end_date, employee_ids)
            return [a for a in attendances if getattr(a, 'status', '') == 'late']
        except Exception as e:
            logger.error(f"Error getting late arrivals: {e}")
            return []
    
    async def get_overtime_records(
        self,
        start_date: date,
        end_date: date,
        employee_ids: Optional[List[str]] = None,
        min_overtime_hours: Optional[Decimal] = None
    ) -> List[Attendance]:
        """Get overtime records."""
        # Placeholder - requires overtime calculation
        return []
    
    async def get_absent_employees(
        self,
        date: date,
        department_ids: Optional[List[str]] = None
    ) -> List[str]:
        """Get absent employees for a date."""
        try:
            attendances = await self.get_by_date(date)
            return [getattr(a, 'employee_id', '') for a in attendances if getattr(a, 'status', '') == 'absent']
        except Exception as e:
            logger.error(f"Error getting absent employees: {e}")
            return []
    
    async def get_working_hours_distribution(
        self,
        start_date: date,
        end_date: date,
        employee_ids: Optional[List[str]] = None
    ) -> Dict[str, int]:
        """Get working hours distribution."""
        # Placeholder - requires working hours analysis
        return {}
    
    async def get_attendance_percentage_by_employee(
        self,
        start_date: date,
        end_date: date,
        employee_ids: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """Get attendance percentage by employee."""
        try:
            if employee_ids:
                percentages = {}
                for employee_id in employee_ids:
                    summary = await self.get_employee_summary(employee_id, start_date, end_date)
                    percentages[employee_id] = getattr(summary, 'attendance_percentage', 0.0)
                return percentages
            return {}
        except Exception as e:
            logger.error(f"Error getting attendance percentages: {e}")
            return {}
    
    async def get_monthly_attendance_summary(
        self,
        year: int,
        month: int,
        employee_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get monthly attendance summary."""
        try:
            start_date = date(year, month, 1)
            if month == 12:
                end_date = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(year, month + 1, 1) - timedelta(days=1)
            
            stats = await self.get_period_statistics(start_date, end_date, employee_ids)
            
            return {
                "year": year,
                "month": month,
                "total_employees": getattr(stats, 'total_employees', 0),
                "total_records": getattr(stats, 'total_records', 0),
                "present_count": getattr(stats, 'present_count', 0),
                "absent_count": getattr(stats, 'absent_count', 0),
                "late_count": getattr(stats, 'late_count', 0),
                "attendance_percentage": getattr(stats, 'attendance_percentage', 0.0)
            }
        except Exception as e:
            logger.error(f"Error getting monthly summary: {e}")
            return {}
    
    # Reports Repository placeholder implementations
    async def generate_daily_report(
        self,
        date: date,
        employee_ids: Optional[List[str]] = None,
        department_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate daily attendance report."""
        # Placeholder - requires report generation implementation
        return {}
    
    async def generate_weekly_report(
        self,
        start_date: date,
        employee_ids: Optional[List[str]] = None,
        department_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate weekly attendance report."""
        # Placeholder - requires report generation implementation
        return {}
    
    async def generate_monthly_report(
        self,
        year: int,
        month: int,
        employee_ids: Optional[List[str]] = None,
        department_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate monthly attendance report."""
        # Placeholder - requires report generation implementation
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
        """Generate custom attendance report."""
        # Placeholder - requires report generation implementation
        return {}
    
    async def export_to_csv(
        self,
        attendances: List[Attendance],
        include_summary: bool = False
    ) -> str:
        """Export attendance records to CSV."""
        # Placeholder - requires CSV export implementation
        return ""
    
    async def export_to_excel(
        self,
        attendances: List[Attendance],
        include_summary: bool = False,
        include_charts: bool = False
    ) -> bytes:
        """Export attendance records to Excel."""
        # Placeholder - requires Excel export implementation
        return b""
    
    # Bulk Operations Repository placeholder implementations
    async def bulk_import(
        self,
        attendance_data: List[Dict[str, Any]],
        import_mode: str = "create"
    ) -> Dict[str, Any]:
        """Bulk import attendance records."""
        # Placeholder - requires bulk import implementation
        return {}
    
    async def bulk_update_status(
        self,
        attendance_ids: List[str],
        new_status: str,
        updated_by: str,
        reason: Optional[str] = None
    ) -> int:
        """Bulk update attendance status."""
        # Placeholder - requires bulk update implementation
        return 0
    
    async def bulk_regularize(
        self,
        attendance_ids: List[str],
        reason: str,
        regularized_by: str
    ) -> int:
        """Bulk regularize attendance records."""
        # Placeholder - requires bulk regularization implementation
        return 0
    
    async def bulk_delete(
        self,
        attendance_ids: List[str],
        deleted_by: str,
        reason: str
    ) -> int:
        """Bulk delete attendance records."""
        # Placeholder - requires bulk delete implementation
        return 0
    
    async def auto_mark_absent(
        self,
        date: date,
        employee_ids: Optional[List[str]] = None,
        exclude_on_leave: bool = True,
        exclude_holidays: bool = True
    ) -> int:
        """Auto mark employees as absent."""
        # Placeholder - requires auto marking implementation
        return 0
    
    async def auto_mark_holidays(
        self,
        date: date,
        employee_ids: Optional[List[str]] = None
    ) -> int:
        """Auto mark holidays."""
        # Placeholder - requires holiday marking implementation
        return 0
    
    # ==================== FACTORY METHODS IMPLEMENTATION ====================
    # These methods are required by the repository interfaces but are not used
    # in the current dependency injection architecture. They return self since
    # this repository implements all attendance repository interfaces.
    
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
    
    def create_composite_repository(self) -> AttendanceRepository:
        """Create composite repository instance."""
        return self 