"""
Import Public Holidays Use Case
Business logic for importing public holidays from files
"""

import logging
import io
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import pandas as pd

from app.application.dto.public_holiday_dto import (
    PublicHolidayImportResultDTO,
    CreatePublicHolidayRequestDTO
)
from app.application.interfaces.repositories.public_holiday_repository import (
    PublicHolidayCommandRepository,
    PublicHolidayQueryRepository
)
from app.application.interfaces.services.event_publisher import EventPublisher
from app.application.interfaces.services.notification_service import NotificationService
from app.domain.entities.public_holiday import PublicHoliday
from app.domain.value_objects.public_holiday_id import PublicHolidayId


logger = logging.getLogger(__name__)


class ImportPublicHolidaysUseCaseError(Exception):
    """Exception raised for import public holidays use case errors"""
    pass


class ImportPublicHolidaysUseCase:
    """
    Use case for importing public holidays from files.
    """
    
    def __init__(
        self,
        command_repository: PublicHolidayCommandRepository,
        query_repository: PublicHolidayQueryRepository,
        event_publisher: EventPublisher,
        notification_service: Optional[NotificationService] = None
    ):
        self.command_repository = command_repository
        self.query_repository = query_repository
        self.event_publisher = event_publisher
        self.notification_service = notification_service
    
    async def execute(
        self, 
        file_data: bytes, 
        filename: str, 
        imported_by: str,
        hostname: str
    ) -> PublicHolidayImportResultDTO:
        """Execute the import public holidays use case."""
        
        logger.info(f"Importing public holidays from file: {filename}")
        
        try:
            # Parse the file
            holidays_data = self._parse_file(file_data, filename)
            
            # Validate parsed data
            validation_errors = self._validate_parsed_data(holidays_data)
            
            if validation_errors:
                return PublicHolidayImportResultDTO(
                    total_processed=len(holidays_data),
                    successful_imports=[],
                    failed_imports=len(holidays_data),
                    errors=validation_errors,
                    warnings=[]
                )
            
            # Import holidays
            successful_imports = []
            failed_imports = []
            import_errors = []
            
            for holiday_data in holidays_data:
                try:
                    # Create holiday entity
                    holiday = PublicHoliday.create(
                        id=PublicHolidayId.generate(),
                        name=holiday_data['name'],
                        date=holiday_data['date'],
                        description=holiday_data.get('description'),
                        is_active=holiday_data.get('is_active', True),
                        created_by=imported_by
                    )
                    
                    # Save to repository
                    saved_holiday = await self.command_repository.save(holiday, hostname)
                    
                    # Store the saved holiday data for response
                    successful_imports.append({
                        'name': saved_holiday.name,
                        'date': saved_holiday.date,
                        'description': saved_holiday.description,
                        'is_active': saved_holiday.is_active
                    })
                    
                except Exception as e:
                    logger.warning(f"Failed to import holiday {holiday_data.get('name', 'Unknown')}: {e}")
                    failed_imports.append(holiday_data)
                    import_errors.append(f"Row {holidays_data.index(holiday_data) + 2}: {str(e)}")
            
            # Publish event
            if successful_imports:
                await self.event_publisher.publish_event(
                    "public_holidays_imported",
                    {
                        "imported_by": imported_by,
                        "filename": filename,
                        "successful_count": len(successful_imports),
                        "failed_count": len(failed_imports)
                    }
                )
            
            return PublicHolidayImportResultDTO(
                total_processed=len(holidays_data),
                successful_imports=successful_imports,
                failed_imports=len(failed_imports),
                errors=import_errors,
                warnings=[]
            )
            
        except Exception as e:
            logger.error(f"Error importing public holidays from {filename}: {e}")
            raise ImportPublicHolidaysUseCaseError(f"Import failed: {str(e)}")
    
    def _parse_file(self, file_data: bytes, filename: str) -> List[Dict[str, Any]]:
        """Parse Excel file and extract holiday data."""
        try:
            # Read Excel file
            if filename.lower().endswith('.csv'):
                df = pd.read_csv(io.BytesIO(file_data))
            else:
                df = pd.read_excel(io.BytesIO(file_data))
            
            # Validate required columns
            required_columns = ['name', 'date']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ImportPublicHolidaysUseCaseError(f"Missing required columns: {missing_columns}")
            
            # Convert DataFrame to list of dictionaries
            holidays_data = []
            for index, row in df.iterrows():
                try:
                    # Parse date with DD-MM-YYYY format
                    date_str = str(row['date']).strip()
                    parsed_date = self._parse_date(date_str)
                    
                    holiday_data = {
                        'name': str(row['name']).strip(),
                        'date': parsed_date,
                        'description': str(row.get('description', '')).strip() if pd.notna(row.get('description')) else None,
                        'is_active': bool(row.get('is_active', True)) if pd.notna(row.get('is_active')) else True
                    }
                    
                    holidays_data.append(holiday_data)
                    
                except Exception as e:
                    logger.warning(f"Error parsing row {index + 2}: {e}")
                    continue
            
            return holidays_data
            
        except Exception as e:
            logger.error(f"Error parsing file {filename}: {e}")
            raise ImportPublicHolidaysUseCaseError(f"File parsing failed: {str(e)}")
    
    def _parse_date(self, date_str: str) -> date:
        """Parse date string in DD-MM-YYYY format."""
        try:
            # Handle datetime objects from Excel
            if isinstance(date_str, str):
                # Remove time component if present
                if ' ' in date_str:
                    date_str = date_str.split(' ')[0]
                
                # Try DD-MM-YYYY format first
                return datetime.strptime(date_str, "%d-%m-%Y").date()
            elif hasattr(date_str, 'date'):  # Handle datetime objects
                return date_str.date()
            elif hasattr(date_str, 'strftime'):  # Handle date objects
                return date_str
            else:
                # Convert to string and try parsing
                date_str = str(date_str)
                if ' ' in date_str:
                    date_str = date_str.split(' ')[0]
                
                # Try DD-MM-YYYY format first
                return datetime.strptime(date_str, "%d-%m-%Y").date()
        except ValueError:
            try:
                # Try DD/MM/YYYY format
                if isinstance(date_str, str):
                    if ' ' in date_str:
                        date_str = date_str.split(' ')[0]
                    return datetime.strptime(date_str, "%d/%m/%Y").date()
                else:
                    date_str = str(date_str)
                    if ' ' in date_str:
                        date_str = date_str.split(' ')[0]
                    return datetime.strptime(date_str, "%d/%m/%Y").date()
            except ValueError:
                try:
                    # Try YYYY-MM-DD format as fallback
                    if isinstance(date_str, str):
                        if ' ' in date_str:
                            date_str = date_str.split(' ')[0]
                        return datetime.strptime(date_str, "%Y-%m-%d").date()
                    else:
                        date_str = str(date_str)
                        if ' ' in date_str:
                            date_str = date_str.split(' ')[0]
                        return datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError:
                    try:
                        # Try YYYY/MM/DD format as fallback
                        if isinstance(date_str, str):
                            if ' ' in date_str:
                                date_str = date_str.split(' ')[0]
                            return datetime.strptime(date_str, "%Y/%m/%d").date()
                        else:
                            date_str = str(date_str)
                            if ' ' in date_str:
                                date_str = date_str.split(' ')[0]
                            return datetime.strptime(date_str, "%Y/%m/%d").date()
                    except ValueError:
                        raise ImportPublicHolidaysUseCaseError(f"Invalid date format: {date_str}. Expected DD-MM-YYYY format.")
    
    def _validate_parsed_data(self, holidays_data: List[Dict[str, Any]]) -> List[str]:
        """Validate parsed holiday data."""
        errors = []
        
        for index, holiday_data in enumerate(holidays_data):
            row_num = index + 2  # +2 because Excel rows are 1-indexed and we skip header
            
            # Validate name
            if not holiday_data['name'] or not holiday_data['name'].strip():
                errors.append(f"Row {row_num}: Holiday name is required")
            
            # Validate date
            if not holiday_data['date']:
                errors.append(f"Row {row_num}: Valid date is required")
        
        return errors 