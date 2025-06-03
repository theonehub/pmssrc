"""
Get Public Holidays Use Case
Business logic for retrieving public holidays
"""

import logging
from datetime import datetime, date
from typing import List, Optional, Dict, Any

from app.application.dto.public_holiday_dto import (
    PublicHolidayResponseDTO,
    PublicHolidaySummaryDTO,
    HolidayCalendarDTO,
    get_holiday_category_options,
    get_holiday_observance_options,
    get_holiday_recurrence_options
)
from app.application.interfaces.repositories.public_holiday_repository import (
    PublicHolidayQueryRepository,
    PublicHolidayAnalyticsRepository,
    PublicHolidayCalendarRepository
)
from app.domain.entities.public_holiday import PublicHoliday


logger = logging.getLogger(__name__)


class GetPublicHolidaysUseCaseError(Exception):
    """Exception raised for get public holidays use case errors"""
    pass


class GetPublicHolidaysUseCase:
    """
    Use case for retrieving public holidays.
    
    Follows SOLID principles:
    - SRP: Only handles public holiday retrieval
    - OCP: Extensible through composition
    - LSP: Can be substituted with enhanced versions
    - ISP: Focused interface for retrieval operations
    - DIP: Depends on abstractions (repositories)
    """
    
    def __init__(
        self,
        query_repository: PublicHolidayQueryRepository,
        analytics_repository: Optional[PublicHolidayAnalyticsRepository] = None,
        calendar_repository: Optional[PublicHolidayCalendarRepository] = None
    ):
        self.query_repository = query_repository
        self.analytics_repository = analytics_repository
        self.calendar_repository = calendar_repository
    
    async def get_all_holidays(self, include_inactive: bool = False) -> List[PublicHolidayResponseDTO]:
        """Get all public holidays"""
        
        logger.info(f"Retrieving all public holidays (include_inactive: {include_inactive})")
        
        try:
            holidays = await self.query_repository.get_all(include_inactive=include_inactive)
            
            response_dtos = [
                PublicHolidayResponseDTO.from_domain(holiday)
                for holiday in holidays
            ]
            
            logger.info(f"Retrieved {len(response_dtos)} public holidays")
            return response_dtos
            
        except Exception as e:
            logger.error(f"Error retrieving all public holidays: {e}")
            raise GetPublicHolidaysUseCaseError(f"Failed to retrieve holidays: {str(e)}")
    
    async def get_active_holidays(self) -> List[PublicHolidayResponseDTO]:
        """Get all active public holidays"""
        
        logger.info("Retrieving active public holidays")
        
        try:
            holidays = await self.query_repository.get_all_active()
            
            response_dtos = [
                PublicHolidayResponseDTO.from_domain(holiday)
                for holiday in holidays
            ]
            
            logger.info(f"Retrieved {len(response_dtos)} active public holidays")
            return response_dtos
            
        except Exception as e:
            logger.error(f"Error retrieving active public holidays: {e}")
            raise GetPublicHolidaysUseCaseError(f"Failed to retrieve active holidays: {str(e)}")
    
    async def get_holiday_by_id(self, holiday_id: str) -> Optional[PublicHolidayResponseDTO]:
        """Get public holiday by ID"""
        
        logger.info(f"Retrieving public holiday by ID: {holiday_id}")
        
        try:
            holiday = await self.query_repository.get_by_id(holiday_id)
            
            if not holiday:
                logger.warning(f"Public holiday not found: {holiday_id}")
                return None
            
            response_dto = PublicHolidayResponseDTO.from_domain(holiday)
            
            logger.info(f"Retrieved public holiday: {holiday.holiday_type.name}")
            return response_dto
            
        except Exception as e:
            logger.error(f"Error retrieving public holiday by ID: {e}")
            raise GetPublicHolidaysUseCaseError(f"Failed to retrieve holiday: {str(e)}")
    
    async def get_holiday_by_date(self, holiday_date: str) -> Optional[PublicHolidayResponseDTO]:
        """Get public holiday by date"""
        
        logger.info(f"Retrieving public holiday by date: {holiday_date}")
        
        try:
            # Parse date
            date_obj = datetime.fromisoformat(holiday_date).date()
            
            holiday = await self.query_repository.get_by_date(date_obj)
            
            if not holiday:
                logger.info(f"No public holiday found on date: {holiday_date}")
                return None
            
            response_dto = PublicHolidayResponseDTO.from_domain(holiday)
            
            logger.info(f"Retrieved public holiday: {holiday.holiday_type.name}")
            return response_dto
            
        except ValueError as e:
            logger.error(f"Invalid date format: {holiday_date}")
            raise GetPublicHolidaysUseCaseError(f"Invalid date format: {holiday_date}")
        
        except Exception as e:
            logger.error(f"Error retrieving public holiday by date: {e}")
            raise GetPublicHolidaysUseCaseError(f"Failed to retrieve holiday: {str(e)}")
    
    async def get_holidays_by_year(
        self, 
        year: int, 
        include_inactive: bool = False
    ) -> List[PublicHolidayResponseDTO]:
        """Get public holidays for a specific year"""
        
        logger.info(f"Retrieving public holidays for year: {year}")
        
        try:
            holidays = await self.query_repository.get_by_year(year, include_inactive=include_inactive)
            
            response_dtos = [
                PublicHolidayResponseDTO.from_domain(holiday)
                for holiday in holidays
            ]
            
            # Sort by date
            response_dtos.sort(key=lambda h: h.holiday_date)
            
            logger.info(f"Retrieved {len(response_dtos)} public holidays for {year}")
            return response_dtos
            
        except Exception as e:
            logger.error(f"Error retrieving public holidays for year {year}: {e}")
            raise GetPublicHolidaysUseCaseError(f"Failed to retrieve holidays for {year}: {str(e)}")
    
    async def get_holidays_by_month(
        self, 
        year: int, 
        month: int, 
        include_inactive: bool = False
    ) -> List[PublicHolidayResponseDTO]:
        """Get public holidays for a specific month"""
        
        logger.info(f"Retrieving public holidays for {month}/{year}")
        
        try:
            if month < 1 or month > 12:
                raise GetPublicHolidaysUseCaseError("Month must be between 1 and 12")
            
            holidays = await self.query_repository.get_by_month(year, month, include_inactive=include_inactive)
            
            response_dtos = [
                PublicHolidayResponseDTO.from_domain(holiday)
                for holiday in holidays
            ]
            
            # Sort by date
            response_dtos.sort(key=lambda h: h.holiday_date)
            
            logger.info(f"Retrieved {len(response_dtos)} public holidays for {month}/{year}")
            return response_dtos
            
        except Exception as e:
            logger.error(f"Error retrieving public holidays for {month}/{year}: {e}")
            raise GetPublicHolidaysUseCaseError(f"Failed to retrieve holidays for {month}/{year}: {str(e)}")
    
    def get_holidays_by_date_range(
        self,
        start_date: str,
        end_date: str,
        include_inactive: bool = False
    ) -> List[PublicHolidayResponseDTO]:
        """Get public holidays within a date range"""
        
        logger.info(f"Retrieving public holidays from {start_date} to {end_date}")
        
        try:
            # Parse dates
            start_date_obj = datetime.fromisoformat(start_date).date()
            end_date_obj = datetime.fromisoformat(end_date).date()
            
            if end_date_obj < start_date_obj:
                raise GetPublicHolidaysUseCaseError("End date cannot be before start date")
            
            holidays = self.query_repository.get_by_date_range(
                start_date_obj, end_date_obj, include_inactive=include_inactive
            )
            
            response_dtos = [
                PublicHolidayResponseDTO.from_domain(holiday)
                for holiday in holidays
            ]
            
            # Sort by date
            response_dtos.sort(key=lambda h: h.date_range["start_date"])
            
            logger.info(f"Retrieved {len(response_dtos)} public holidays in date range")
            return response_dtos
            
        except ValueError as e:
            logger.error(f"Invalid date format in range: {start_date} to {end_date}")
            raise GetPublicHolidaysUseCaseError(f"Invalid date format: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error retrieving public holidays by date range: {e}")
            raise GetPublicHolidaysUseCaseError(f"Failed to retrieve holidays: {str(e)}")
    
    def get_holidays_by_category(
        self,
        category: str,
        include_inactive: bool = False
    ) -> List[PublicHolidayResponseDTO]:
        """Get public holidays by category"""
        
        logger.info(f"Retrieving public holidays for category: {category}")
        
        try:
            holidays = self.query_repository.get_by_category(category, include_inactive=include_inactive)
            
            response_dtos = [
                PublicHolidayResponseDTO.from_domain(holiday)
                for holiday in holidays
            ]
            
            # Sort by date
            response_dtos.sort(key=lambda h: h.date_range["start_date"])
            
            logger.info(f"Retrieved {len(response_dtos)} public holidays for category {category}")
            return response_dtos
            
        except Exception as e:
            logger.error(f"Error retrieving public holidays by category: {e}")
            raise GetPublicHolidaysUseCaseError(f"Failed to retrieve holidays: {str(e)}")
    
    def get_upcoming_holidays(
        self,
        days_ahead: int = 30,
        include_inactive: bool = False
    ) -> List[PublicHolidaySummaryDTO]:
        """Get upcoming holidays"""
        
        logger.info(f"Retrieving upcoming holidays for next {days_ahead} days")
        
        try:
            holidays = self.query_repository.get_upcoming_holidays(
                days_ahead=days_ahead, 
                include_inactive=include_inactive
            )
            
            summary_dtos = [
                PublicHolidaySummaryDTO.from_domain(holiday)
                for holiday in holidays
            ]
            
            # Sort by date
            summary_dtos.sort(key=lambda h: h.holiday_date)
            
            logger.info(f"Retrieved {len(summary_dtos)} upcoming holidays")
            return summary_dtos
            
        except Exception as e:
            logger.error(f"Error retrieving upcoming holidays: {e}")
            raise GetPublicHolidaysUseCaseError(f"Failed to retrieve upcoming holidays: {str(e)}")
    
    def search_holidays(
        self,
        search_term: Optional[str] = None,
        category: Optional[str] = None,
        observance: Optional[str] = None,
        year: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> List[PublicHolidayResponseDTO]:
        """Search holidays with filters"""
        
        logger.info(f"Searching holidays with filters: term={search_term}, category={category}, year={year}")
        
        try:
            holidays = self.query_repository.search_holidays(
                search_term=search_term,
                category=category,
                observance=observance,
                year=year,
                is_active=is_active
            )
            
            response_dtos = [
                PublicHolidayResponseDTO.from_domain(holiday)
                for holiday in holidays
            ]
            
            # Sort by date
            response_dtos.sort(key=lambda h: h.date_range["start_date"])
            
            logger.info(f"Found {len(response_dtos)} holidays matching search criteria")
            return response_dtos
            
        except Exception as e:
            logger.error(f"Error searching holidays: {e}")
            raise GetPublicHolidaysUseCaseError(f"Failed to search holidays: {str(e)}")
    
    def get_holiday_statistics(self, year: Optional[int] = None) -> Dict[str, Any]:
        """Get holiday statistics"""
        
        if not self.analytics_repository:
            raise GetPublicHolidaysUseCaseError("Analytics repository not available")
        
        logger.info(f"Retrieving holiday statistics for year: {year or 'all'}")
        
        try:
            statistics = self.analytics_repository.get_holiday_statistics(year=year)
            
            logger.info("Retrieved holiday statistics")
            return statistics
            
        except Exception as e:
            logger.error(f"Error retrieving holiday statistics: {e}")
            raise GetPublicHolidaysUseCaseError(f"Failed to retrieve statistics: {str(e)}")
    
    def get_holiday_calendar(
        self,
        year: int,
        month: Optional[int] = None
    ) -> HolidayCalendarDTO:
        """Get holiday calendar"""
        
        if not self.calendar_repository:
            # Fallback to basic calendar using query repository
            return self._generate_basic_calendar(year, month)
        
        logger.info(f"Generating holiday calendar for {month or 'all'}/{year}")
        
        try:
            if month:
                calendar_data = self.calendar_repository.generate_monthly_calendar(year, month)
            else:
                calendar_data = self.calendar_repository.generate_yearly_calendar(year)
            
            # Convert to DTO
            calendar_dto = HolidayCalendarDTO(
                year=year,
                month=month,
                holidays=calendar_data.get("holidays", []),
                total_holidays=calendar_data.get("total_holidays", 0),
                mandatory_holidays=calendar_data.get("mandatory_holidays", 0),
                optional_holidays=calendar_data.get("optional_holidays", 0)
            )
            
            logger.info(f"Generated holiday calendar with {calendar_dto.total_holidays} holidays")
            return calendar_dto
            
        except Exception as e:
            logger.error(f"Error generating holiday calendar: {e}")
            raise GetPublicHolidaysUseCaseError(f"Failed to generate calendar: {str(e)}")
    
    def _generate_basic_calendar(self, year: int, month: Optional[int] = None) -> HolidayCalendarDTO:
        """Generate basic calendar using query repository"""
        
        try:
            if month:
                holidays = self.query_repository.get_by_month(year, month, include_inactive=False)
            else:
                holidays = self.query_repository.get_by_year(year, include_inactive=False)
            
            holiday_dicts = []
            mandatory_count = 0
            optional_count = 0
            
            for holiday in holidays:
                holiday_dict = PublicHolidayResponseDTO.from_domain(holiday).to_dict()
                holiday_dicts.append(holiday_dict)
                
                if holiday.is_mandatory():
                    mandatory_count += 1
                elif holiday.is_optional():
                    optional_count += 1
            
            return HolidayCalendarDTO(
                year=year,
                month=month,
                holidays=holiday_dicts,
                total_holidays=len(holidays),
                mandatory_holidays=mandatory_count,
                optional_holidays=optional_count
            )
            
        except Exception as e:
            logger.error(f"Error generating basic calendar: {e}")
            raise GetPublicHolidaysUseCaseError(f"Failed to generate basic calendar: {str(e)}")
    
    def get_holiday_options(self) -> Dict[str, List[Dict[str, str]]]:
        """Get holiday options for UI"""
        
        logger.info("Retrieving holiday options")
        
        try:
            options = {
                "categories": get_holiday_category_options(),
                "observances": get_holiday_observance_options(),
                "recurrences": get_holiday_recurrence_options()
            }
            
            logger.info("Retrieved holiday options")
            return options
            
        except Exception as e:
            logger.error(f"Error retrieving holiday options: {e}")
            raise GetPublicHolidaysUseCaseError(f"Failed to retrieve options: {str(e)}")
    
    async def check_holiday_on_date(self, check_date: str) -> bool:
        """Check if there's a holiday on a specific date"""
        
        logger.info(f"Checking for holiday on date: {check_date}")
        
        try:
            # Parse date
            date_obj = datetime.fromisoformat(check_date).date()
            
            exists = await self.query_repository.exists_on_date(date_obj)
            
            logger.info(f"Holiday exists on {check_date}: {exists}")
            return exists
            
        except ValueError as e:
            logger.error(f"Invalid date format: {check_date}")
            raise GetPublicHolidaysUseCaseError(f"Invalid date format: {check_date}")
        
        except Exception as e:
            logger.error(f"Error checking holiday on date: {e}")
            raise GetPublicHolidaysUseCaseError(f"Failed to check holiday: {str(e)}")
    
    def get_holiday_conflicts(self, holiday_id: str) -> List[PublicHolidayResponseDTO]:
        """Get holidays that conflict with the specified holiday"""
        
        logger.info(f"Checking for conflicts with holiday: {holiday_id}")
        
        try:
            holiday = self.query_repository.get_by_id(holiday_id)
            if not holiday:
                raise GetPublicHolidaysUseCaseError(f"Holiday not found: {holiday_id}")
            
            conflicts = self.query_repository.get_conflicts(holiday)
            
            response_dtos = [
                PublicHolidayResponseDTO.from_domain(conflict)
                for conflict in conflicts
            ]
            
            logger.info(f"Found {len(response_dtos)} conflicts")
            return response_dtos
            
        except Exception as e:
            logger.error(f"Error checking holiday conflicts: {e}")
            raise GetPublicHolidaysUseCaseError(f"Failed to check conflicts: {str(e)}") 