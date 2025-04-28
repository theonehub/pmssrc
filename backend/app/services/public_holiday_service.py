from datetime import datetime
import logging
from fastapi import HTTPException
from models.public_holiday import PublicHoliday
from database.public_holiday_database import (
    create_holiday,
    get_all_holidays,
    get_holiday_by_month,
    update_holiday,
    import_holidays,
    get_holiday_by_date_str
)

logger = logging.getLogger(__name__)

async def is_public_holiday(date: datetime, hostname: str):
    """
    Checks if a given date is a public holiday.
    """
    date_str = date.strftime("%Y-%m-%d")
    holiday = await get_holiday_by_date_str(date_str, hostname)
    return holiday is not None

async def get_all_holidays(hostname: str):
    """
    Returns all holidays from holiday_collection for the company.
    """
    holidays = await get_all_holidays(hostname)
    logger.info("Fetched all holidays, count: %d", len(holidays))
    return holidays

async def create_holiday(holiday: PublicHoliday, emp_id: str, hostname: str):
    """
    Creates a new holiday in the holiday_collection.
    """
    logger.info(f"Creating holiday: {holiday}")
    try:
        holiday_id = await create_holiday(holiday, emp_id, hostname)
        logger.info(f"Holiday created successfully, id: {holiday_id}")
        return holiday_id
    except Exception as e:
        logger.error(f"Error creating holiday: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def get_holiday_by_month(month: int, year: int, hostname: str):
    """
    Returns holidays for a specific month and year.
    """
    holidays = await get_holiday_by_month(month, year, hostname)
    logger.info(f"Fetched holidays for {month}/{year}, count: {len(holidays)}")
    return holidays

async def update_holiday(holiday_id: str, holiday: PublicHoliday, emp_id: str, hostname: str):
    """
    Updates an existing holiday in the holiday_collection.
    """
    logger.info(f"Updating holiday {holiday_id}: {holiday}")
    try:
        updated = await update_holiday(holiday_id, holiday, emp_id, hostname)
        if not updated:
            logger.warning(f"Holiday {holiday_id} not found")
            return False
        logger.info(f"Holiday {holiday_id} updated successfully")
        return True
    except Exception as e:
        logger.error(f"Error updating holiday: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def import_holidays_from_file(holiday_data_list: list, emp_id: str, hostname: str):
    """
    Imports multiple holidays from a list of dictionaries.
    """
    logger.info(f"Importing {len(holiday_data_list)} holidays")
    try:
        inserted_count = await import_holidays(holiday_data_list, emp_id, hostname)
        logger.info(f"Successfully imported {inserted_count} holidays")
        return inserted_count
    except Exception as e:
        logger.error(f"Error importing holidays: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 