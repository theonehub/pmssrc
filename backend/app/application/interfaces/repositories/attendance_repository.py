"""
Attendance Repository Interfaces
Defines contracts for attendance data access following Interface Segregation Principle
"""

from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from decimal import Decimal

from domain.entities.attendance import Attendance
from application.dto.attendance_dto import (
    AttendanceSearchFiltersDTO,
    AttendanceSummaryDTO,
    AttendanceStatisticsDTO,
    DepartmentAttendanceDTO,
    AttendanceTrendDTO
)


class AttendanceCommandRepository(ABC):
    """
    Repository interface for attendance write operations.
    
    Follows Interface Segregation Principle by focusing only on command operations.
    """
    
    @abstractmethod
    async def save(self, attendance: Attendance) -> Attendance:
        """Save attendance record"""
        pass
    
    @abstractmethod
    async def save_batch(self, attendances: List[Attendance]) -> List[Attendance]:
        """Save multiple attendance records in batch"""
        pass
    
    @abstractmethod
    async def delete(self, attendance_id: str) -> bool:
        """Delete attendance record by ID"""
        pass
    
    @abstractmethod
    async def delete_by_employee_and_date(self, employee_id: str, attendance_date: date) -> bool:
        """Delete attendance record by employee and date"""
        pass


class AttendanceQueryRepository(ABC):
    """
    Repository interface for attendance read operations.
    
    Follows Interface Segregation Principle by focusing only on query operations.
    """
    
    @abstractmethod
    async def get_by_id(self, attendance_id: str) -> Optional[Attendance]:
        """Get attendance record by ID"""
        pass
    
    @abstractmethod
    async def get_by_employee_and_date(self, employee_id: str, attendance_date: date) -> Optional[Attendance]:
        """Get attendance record by employee ID and date"""
        pass
    
    @abstractmethod
    async def get_by_employee(
        self,
        employee_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Attendance]:
        """Get attendance records by employee ID with optional date range"""
        pass
    
    @abstractmethod
    async def get_by_date(
        self,
        attendance_date: date,
        employee_ids: Optional[List[str]] = None
    ) -> List[Attendance]:
        """Get attendance records by date with optional employee filter"""
        pass
    
    @abstractmethod
    async def get_by_date_range(
        self,
        start_date: date,
        end_date: date,
        employee_ids: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Attendance]:
        """Get attendance records by date range with optional employee filter"""
        pass
    
    @abstractmethod
    async def search(self, filters: AttendanceSearchFiltersDTO) -> List[Attendance]:
        """Search attendance records with filters"""
        pass
    
    @abstractmethod
    async def count_by_filters(self, filters: AttendanceSearchFiltersDTO) -> int:
        """Count attendance records matching filters"""
        pass
    
    @abstractmethod
    async def get_pending_check_outs(self, date: Optional[date] = None) -> List[Attendance]:
        """Get attendance records with check-in but no check-out"""
        pass
    
    @abstractmethod
    async def get_regularization_requests(
        self,
        employee_ids: Optional[List[str]] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Attendance]:
        """Get attendance records that need regularization"""
        pass
    
    @abstractmethod
    async def exists_by_employee_and_date(self, employee_id: str, attendance_date: date) -> bool:
        """Check if attendance record exists for employee and date"""
        pass


class AttendanceAnalyticsRepository(ABC):
    """
    Repository interface for attendance analytics and reporting operations.
    
    Follows Interface Segregation Principle by focusing only on analytics operations.
    """
    
    @abstractmethod
    async def get_employee_summary(
        self,
        employee_id: str,
        start_date: date,
        end_date: date
    ) -> AttendanceSummaryDTO:
        """Get attendance summary for an employee"""
        pass
    
    @abstractmethod
    async def get_multiple_employee_summaries(
        self,
        employee_ids: List[str],
        start_date: date,
        end_date: date
    ) -> List[AttendanceSummaryDTO]:
        """Get attendance summaries for multiple employees"""
        pass
    
    @abstractmethod
    async def get_daily_statistics(self, date: date) -> AttendanceStatisticsDTO:
        """Get daily attendance statistics"""
        pass
    
    @abstractmethod
    async def get_period_statistics(
        self,
        start_date: date,
        end_date: date,
        employee_ids: Optional[List[str]] = None
    ) -> AttendanceStatisticsDTO:
        """Get attendance statistics for a period"""
        pass
    
    @abstractmethod
    async def get_department_attendance(
        self,
        date: date,
        department_ids: Optional[List[str]] = None
    ) -> List[DepartmentAttendanceDTO]:
        """Get department-wise attendance for a date"""
        pass
    
    @abstractmethod
    async def get_attendance_trends(
        self,
        start_date: date,
        end_date: date,
        employee_ids: Optional[List[str]] = None
    ) -> List[AttendanceTrendDTO]:
        """Get attendance trends over a period"""
        pass
    
    @abstractmethod
    async def get_late_arrivals(
        self,
        start_date: date,
        end_date: date,
        employee_ids: Optional[List[str]] = None
    ) -> List[Attendance]:
        """Get late arrival records"""
        pass
    
    @abstractmethod
    async def get_overtime_records(
        self,
        start_date: date,
        end_date: date,
        employee_ids: Optional[List[str]] = None,
        min_overtime_hours: Optional[Decimal] = None
    ) -> List[Attendance]:
        """Get overtime records"""
        pass
    
    @abstractmethod
    async def get_absent_employees(
        self,
        date: date,
        department_ids: Optional[List[str]] = None
    ) -> List[str]:
        """Get list of absent employee IDs for a date"""
        pass
    
    @abstractmethod
    async def get_working_hours_distribution(
        self,
        start_date: date,
        end_date: date,
        employee_ids: Optional[List[str]] = None
    ) -> Dict[str, int]:
        """Get distribution of working hours (e.g., {0-4: 10, 4-8: 50, 8+: 40})"""
        pass
    
    @abstractmethod
    async def get_attendance_percentage_by_employee(
        self,
        start_date: date,
        end_date: date,
        employee_ids: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """Get attendance percentage by employee"""
        pass
    
    @abstractmethod
    async def get_monthly_attendance_summary(
        self,
        year: int,
        month: int,
        employee_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get monthly attendance summary"""
        pass


class AttendanceReportsRepository(ABC):
    """
    Repository interface for attendance reporting operations.
    
    Follows Interface Segregation Principle by focusing only on reporting operations.
    """
    
    @abstractmethod
    async def generate_daily_report(
        self,
        date: date,
        employee_ids: Optional[List[str]] = None,
        department_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate daily attendance report"""
        pass
    
    @abstractmethod
    async def generate_weekly_report(
        self,
        start_date: date,
        employee_ids: Optional[List[str]] = None,
        department_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate weekly attendance report"""
        pass
    
    @abstractmethod
    async def generate_monthly_report(
        self,
        year: int,
        month: int,
        employee_ids: Optional[List[str]] = None,
        department_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate monthly attendance report"""
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    async def export_to_csv(
        self,
        attendances: List[Attendance],
        include_summary: bool = False
    ) -> str:
        """Export attendance records to CSV format"""
        pass
    
    @abstractmethod
    async def export_to_excel(
        self,
        attendances: List[Attendance],
        include_summary: bool = False,
        include_charts: bool = False
    ) -> bytes:
        """Export attendance records to Excel format"""
        pass


class AttendanceBulkOperationsRepository(ABC):
    """
    Repository interface for attendance bulk operations.
    
    Follows Interface Segregation Principle by focusing only on bulk operations.
    """
    
    @abstractmethod
    async def bulk_import(
        self,
        attendance_data: List[Dict[str, Any]],
        import_mode: str = "create"  # create, update, upsert
    ) -> Dict[str, Any]:
        """Bulk import attendance records"""
        pass
    
    @abstractmethod
    async def bulk_update_status(
        self,
        attendance_ids: List[str],
        new_status: str,
        updated_by: str,
        reason: Optional[str] = None
    ) -> int:
        """Bulk update attendance status"""
        pass
    
    @abstractmethod
    async def bulk_regularize(
        self,
        attendance_ids: List[str],
        reason: str,
        regularized_by: str
    ) -> int:
        """Bulk regularize attendance records"""
        pass
    
    @abstractmethod
    async def bulk_delete(
        self,
        attendance_ids: List[str],
        deleted_by: str,
        reason: str
    ) -> int:
        """Bulk delete attendance records"""
        pass
    
    @abstractmethod
    async def auto_mark_absent(
        self,
        date: date,
        employee_ids: Optional[List[str]] = None,
        exclude_on_leave: bool = True,
        exclude_holidays: bool = True
    ) -> int:
        """Auto-mark employees as absent for a date"""
        pass
    
    @abstractmethod
    async def auto_mark_holidays(
        self,
        date: date,
        employee_ids: Optional[List[str]] = None
    ) -> int:
        """Auto-mark employees as on holiday for a date"""
        pass


# Composite repository interface for convenience
class AttendanceRepository(
    AttendanceCommandRepository,
    AttendanceQueryRepository,
    AttendanceAnalyticsRepository,
    AttendanceReportsRepository,
    AttendanceBulkOperationsRepository
):
    """
    Composite repository interface that combines all attendance repository interfaces.
    
    This can be used when a single implementation needs to provide all functionality,
    but individual interfaces should be preferred for dependency injection to follow ISP.
    """
    pass


# Repository factory interface
class AttendanceRepositoryFactory(ABC):
    """
    Factory interface for creating attendance repository instances.
    
    Allows for different implementations (MongoDB, PostgreSQL, etc.)
    """
    
    @abstractmethod
    def create_command_repository(self) -> AttendanceCommandRepository:
        """Create command repository instance"""
        pass
    
    @abstractmethod
    def create_query_repository(self) -> AttendanceQueryRepository:
        """Create query repository instance"""
        pass
    
    @abstractmethod
    def create_analytics_repository(self) -> AttendanceAnalyticsRepository:
        """Create analytics repository instance"""
        pass
    
    @abstractmethod
    def create_reports_repository(self) -> AttendanceReportsRepository:
        """Create reports repository instance"""
        pass
    
    @abstractmethod
    def create_bulk_operations_repository(self) -> AttendanceBulkOperationsRepository:
        """Create bulk operations repository instance"""
        pass
    
    @abstractmethod
    def create_composite_repository(self) -> AttendanceRepository:
        """Create composite repository instance"""
        pass 