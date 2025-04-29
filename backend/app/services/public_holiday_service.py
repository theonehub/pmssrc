from datetime import datetime
import logging
from fastapi import HTTPException
import uuid
from models.public_holiday import PublicHoliday
from database.public_holiday_database import (
    create_holiday as create_holiday_db,
    get_all_holidays as get_all_holidays_db,
    get_holiday_by_month as get_holiday_by_month_db,
    update_holiday as update_holiday_db,
    import_holidays as import_holidays_db,
    get_holiday_by_date_str as get_holiday_by_date_str_db,
    delete_holiday as delete_holiday_db
)

logger = logging.getLogger(__name__)

def is_public_holiday(date: datetime, hostname: str):
    """
    Checks if a given date is a public holiday.
    """
    date_str = date.strftime("%Y-%m-%d")
    holiday = get_holiday_by_date_str_db(date_str, hostname)
    return holiday is not None

def get_all_holidays(hostname: str):
    """
    Returns all holidays from holiday_collection for the company.
    """
    holidays = get_all_holidays_db(hostname)
    logger.info("Fetched all holidays, count: %d", len(holidays))
    return holidays

def create_holiday(holiday: PublicHoliday, emp_id: str, hostname: str):
    """
    Creates a new holiday in the holiday_collection.
    """
    logger.info(f"Creating holiday: {holiday}")
    try:
        if holiday.holiday_id is None:
            holiday.holiday_id = str(uuid.uuid4())
        holiday_id = create_holiday_db(holiday, emp_id, hostname)
        logger.info(f"Holiday created successfully, id: {holiday_id}")
        return holiday_id
    except Exception as e:
        logger.error(f"Error creating holiday: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def get_holiday_by_month(month: int, year: int, hostname: str):
    """
    Returns holidays for a specific month and year.
    """
    holidays = get_holiday_by_month_db(month, year, hostname)
    logger.info(f"Fetched holidays for {month}/{year}, count: {len(holidays)}")
    return holidays

def update_holiday(holiday_id: str, holiday: PublicHoliday, emp_id: str, hostname: str):
    """
    Updates an existing holiday in the holiday_collection.
    """
    logger.info(f"Updating holiday {holiday_id}: {holiday}")
    try:
        updated = update_holiday_db(holiday_id, holiday, emp_id, hostname)
        if not updated:
            logger.warning(f"Holiday {holiday_id} not found")
            return False
        logger.info(f"Holiday {holiday_id} updated successfully")
        return True
    except Exception as e:
        logger.error(f"Error updating holiday: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def import_holidays_from_file(holiday_data_list: list, emp_id: str, hostname: str):
    """
    Imports multiple holidays from a list of dictionaries.
    """
    logger.info(f"Importing {len(holiday_data_list)} holidays")
    try:
        inserted_count = import_holidays_db(holiday_data_list, emp_id, hostname)
        logger.info(f"Successfully imported {inserted_count} holidays")
        return inserted_count
    except Exception as e:
        logger.error(f"Error importing holidays: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def delete_holiday(holiday_id: str, hostname: str):
    """
    Deletes a public holiday by setting is_active to False.
    """
    logger.info(f"Deleting holiday {holiday_id}")
    try:
        deleted = delete_holiday_db(holiday_id, hostname)
        if not deleted:
            logger.warning(f"Holiday {holiday_id} not found")
            return False
        logger.info(f"Holiday {holiday_id} deleted successfully")
        return True
    except Exception as e:
        logger.error(f"Error deleting holiday: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 