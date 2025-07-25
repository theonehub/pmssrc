"""
Public Holiday Repository Interfaces
Abstract interfaces for public holiday data access
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime, date

from app.domain.entities.public_holiday import PublicHoliday


class PublicHolidayCommandRepository(ABC):
    """
    Interface for public holiday write operations.
    
    Follows SOLID principles:
    - SRP: Only handles write operations
    - OCP: Can be extended with new implementations
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for commands only
    - DIP: Depends on abstractions, not concretions
    """
    
    @abstractmethod
    def save(self, holiday: PublicHoliday) -> bool:
        """Save a new public holiday"""
        pass
    
    @abstractmethod
    def update(self, holiday: PublicHoliday) -> bool:
        """Update an existing public holiday"""
        pass
    
    @abstractmethod
    def delete(self, holiday_id: str) -> bool:
        """Delete a public holiday (soft delete)"""
        pass
    
    @abstractmethod
    def save_batch(self, holidays: List[PublicHoliday]) -> Dict[str, bool]:
        """Save multiple holidays in batch"""
        pass


class PublicHolidayQueryRepository(ABC):
    """
    Interface for public holiday read operations.
    
    Follows SOLID principles:
    - SRP: Only handles read operations
    - OCP: Can be extended with new query methods
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for queries only
    - DIP: Depends on abstractions, not concretions
    """
    
    @abstractmethod
    def get_by_id(self, holiday_id: str) -> Optional[PublicHoliday]:
        """Get public holiday by ID"""
        pass
    
    @abstractmethod
    def get_by_date(self, holiday_date: date) -> Optional[PublicHoliday]:
        """Get public holiday by specific date"""
        pass
    
    @abstractmethod
    def get_all_active(self) -> List[PublicHoliday]:
        """Get all active public holidays"""
        pass
    
    @abstractmethod
    def get_all(self, include_inactive: bool = False) -> List[PublicHoliday]:
        """Get all public holidays"""
        pass
    
    @abstractmethod
    def get_by_year(self, year: int, include_inactive: bool = False) -> List[PublicHoliday]:
        """Get public holidays for a specific year"""
        pass
    
    @abstractmethod
    def get_by_month(self, year: int, month: int, include_inactive: bool = False) -> List[PublicHoliday]:
        """Get public holidays for a specific month"""
        pass
    
    @abstractmethod
    def get_by_date_range(
        self, 
        start_date: date, 
        end_date: date, 
        include_inactive: bool = False
    ) -> List[PublicHoliday]:
        """Get public holidays within a date range"""
        pass
    
    @abstractmethod
    def get_by_category(
        self, 
        category: str, 
        include_inactive: bool = False
    ) -> List[PublicHoliday]:
        """Get public holidays by category"""
        pass
    
    @abstractmethod
    def get_upcoming_holidays(
        self, 
        days_ahead: int = 30,
        include_inactive: bool = False
    ) -> List[PublicHoliday]:
        """Get upcoming holidays within specified days"""
        pass
    
    @abstractmethod
    def search_holidays(
        self,
        search_term: Optional[str] = None,
        category: Optional[str] = None,
        observance: Optional[str] = None,
        year: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> List[PublicHoliday]:
        """Search holidays with multiple filters"""
        pass
    
    @abstractmethod
    def exists_on_date(self, holiday_date: date) -> bool:
        """Check if any active holiday exists on a specific date"""
        pass
    
    @abstractmethod
    def get_conflicts(self, holiday: PublicHoliday) -> List[PublicHoliday]:
        """Get holidays that conflict with the given holiday"""
        pass
    
    @abstractmethod
    def count_active(self) -> int:
        """Count active public holidays"""
        pass
    
    @abstractmethod
    def count_by_category(self, category: str) -> int:
        """Count holidays by category"""
        pass


class PublicHolidayAnalyticsRepository(ABC):
    """
    Interface for public holiday analytics and reporting operations.
    
    Follows SOLID principles:
    - SRP: Only handles analytics operations
    - OCP: Can be extended with new analytics methods
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for analytics only
    - DIP: Depends on abstractions, not concretions
    """
    
    @abstractmethod
    def get_holiday_statistics(
        self,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get comprehensive holiday statistics"""
        pass
    
    @abstractmethod
    def get_category_distribution(
        self,
        year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get distribution of holidays by category"""
        pass
    
    @abstractmethod
    def get_monthly_distribution(
        self,
        year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get distribution of holidays by month"""
        pass
    
    @abstractmethod
    def get_observance_analysis(
        self,
        year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get analysis of holiday observance types"""
        pass
    
    @abstractmethod
    def get_holiday_trends(
        self,
        years: int = 5
    ) -> List[Dict[str, Any]]:
        """Get holiday trends over multiple years"""
        pass
    
    @abstractmethod
    def get_weekend_analysis(
        self,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get analysis of holidays falling on weekends"""
        pass
    
    @abstractmethod
    def get_long_weekend_opportunities(
        self,
        year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get potential long weekend opportunities"""
        pass
    
    @abstractmethod
    def get_holiday_calendar_summary(
        self,
        year: int,
        month: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get calendar summary for a specific period"""
        pass
    
    @abstractmethod
    def get_compliance_report(self) -> Dict[str, Any]:
        """Get holiday compliance and policy adherence report"""
        pass
    
    @abstractmethod
    def get_usage_metrics(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get holiday usage and access metrics"""
        pass


class PublicHolidayCalendarRepository(ABC):
    """
    Interface for holiday calendar operations.
    
    Follows SOLID principles:
    - SRP: Only handles calendar operations
    - OCP: Can be extended with new calendar methods
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for calendar operations
    - DIP: Depends on abstractions, not concretions
    """
    
    @abstractmethod
    def generate_yearly_calendar(
        self,
        year: int,
        include_weekends: bool = True,
        include_optional: bool = True
    ) -> Dict[str, Any]:
        """Generate complete yearly holiday calendar"""
        pass
    
    @abstractmethod
    def generate_monthly_calendar(
        self,
        year: int,
        month: int,
        include_weekends: bool = True,
        include_optional: bool = True
    ) -> Dict[str, Any]:
        """Generate monthly holiday calendar"""
        pass
    
    @abstractmethod
    def get_working_days_count(
        self,
        start_date: date,
        end_date: date,
        exclude_weekends: bool = True
    ) -> int:
        """Get count of working days excluding holidays"""
        pass
    
    @abstractmethod
    def get_next_working_day(
        self,
        from_date: date,
        exclude_weekends: bool = True
    ) -> date:
        """Get next working day after given date"""
        pass
    
    @abstractmethod
    def get_previous_working_day(
        self,
        from_date: date,
        exclude_weekends: bool = True
    ) -> date:
        """Get previous working day before given date"""
        pass
    
    @abstractmethod
    def is_working_day(
        self,
        check_date: date,
        exclude_weekends: bool = True
    ) -> bool:
        """Check if a date is a working day"""
        pass
    
    @abstractmethod
    def get_holiday_bridges(
        self,
        year: int
    ) -> List[Dict[str, Any]]:
        """Get potential holiday bridge opportunities"""
        pass


class PublicHolidayRepository(ABC):
    """
    Unified Public Holiday Repository Interface following User Module Architecture Guide.
    
    Combines essential CRUD operations with organisation context support.
    Follows SOLID principles with clean architecture patterns.
    """
    
    @abstractmethod
    async def save(self, holiday: PublicHoliday, hostname: str) -> PublicHoliday:
        """Save public holiday to organisation-specific database."""
        pass
    
    @abstractmethod
    async def get_by_id(self, holiday_id: 'PublicHolidayId', hostname: str) -> Optional[PublicHoliday]:
        """Get public holiday by ID from organisation-specific database."""
        pass
    
    @abstractmethod
    async def find_with_filters(
        self, 
        filters: 'PublicHolidaySearchFiltersDTO', 
        hostname: str
    ) -> tuple[List[PublicHoliday], int]:
        """Find public holidays with filters from organisation-specific database."""
        pass
    
    @abstractmethod
    async def find_by_date_range(
        self, 
        start_date: date, 
        end_date: date, 
        hostname: str
    ) -> List[PublicHoliday]:
        """Find public holidays within date range from organisation-specific database."""
        pass
    
    @abstractmethod
    async def find_by_date(self, holiday_date: date, hostname: str) -> List[PublicHoliday]:
        """Find public holidays on specific date from organisation-specific database."""
        pass
    
    @abstractmethod
    async def find_by_name_and_date(self, name: str, holiday_date: date, hostname: str) -> List[PublicHoliday]:
        """Find public holidays by name and date from organisation-specific database."""
        pass
    
    @abstractmethod
    async def delete(self, holiday_id: 'PublicHolidayId', hostname: str) -> bool:
        """Delete public holiday from organisation-specific database."""
        pass


# Legacy interface for backward compatibility
class LegacyPublicHolidayRepository(
    PublicHolidayCommandRepository,
    PublicHolidayQueryRepository,
    PublicHolidayAnalyticsRepository,
    PublicHolidayCalendarRepository
):
    """
    Legacy Public Holiday Repository Interface.
    
    Combines all specialized repository interfaces to provide a unified
    interface for public holiday operations.
    
    Follows SOLID principles:
    - SRP: Provides a unified interface
    - OCP: Can be extended through inheritance
    - LSP: All implementations must be substitutable
    - ISP: Composed of focused, segregated interfaces
    - DIP: Depends on abstractions, not concretions
    """
    pass 