import logging
from datetime import datetime
from bson import ObjectId
from models.public_holiday import PublicHoliday
from database import public_holidays_collection
from typing import List

logger = logging.getLogger(__name__)

def get_all_holidays() -> List[PublicHoliday]:
    """
    Retrieves all active public holidays from the database.
    """
    holidays = []
    cursor = public_holidays_collection.find({"is_active": True})
    for doc in cursor:
        doc["id"] = str(doc["_id"])
        holidays.append(PublicHoliday(**doc))
    return holidays


def get_holiday_by_month(month: int, year: int) -> List[PublicHoliday]:
    """
    Retrieves all active public holidays for a specific month and year.
    """
    holidays = []
    logger.info(f"Getting holidays for month: {month} and year: {year}")
    cursor = public_holidays_collection.find({"month": month, "year": year})  
    for doc in cursor:
        doc["id"] = str(doc["_id"])
        holidays.append(PublicHoliday(**doc))
    return holidays

def create_holiday(holiday: PublicHoliday, user_emp_id: str):
    """
    Creates a new public holiday in the database.
    """
    logger.info(f"Creating public holiday: {holiday}")
    
    holiday_dict = holiday.dict(exclude={"id"})
    holiday_dict["day"] = holiday.date.day
    holiday_dict["month"] = holiday.date.month
    holiday_dict["year"] = holiday.date.year
    holiday_dict["created_at"] = datetime.now()
    holiday_dict["created_by"] = user_emp_id
    
    result = public_holidays_collection.insert_one(holiday_dict)
    
    return str(result.inserted_id)

def update_holiday(holiday_id: str, holiday: PublicHoliday, user_emp_id: str) -> bool:
    """
    Updates an existing public holiday.
    Returns True if a document was updated, False otherwise.
    """
    holiday_dict = holiday.dict(exclude={"id"})
    holiday_dict["created_by"] = user_emp_id
    
    result = public_holidays_collection.update_one(
        {"_id": ObjectId(holiday_id)},
        {"$set": holiday_dict}
    )
    
    return result.matched_count > 0

def import_holidays_from_file(holiday_data_list: List[dict], user_emp_id: str) -> int:
    """
    Imports multiple holidays from processed data.
    Returns the number of successfully imported holidays.
    """
    inserted_count = 0
    for holiday_data in holiday_data_list:
        holiday_dict = {
            "name": holiday_data['name'],
            "date": datetime.strptime(holiday_data['date'], '%Y-%m-%d') if isinstance(holiday_data['date'], str) else holiday_data['date'],
            "description": holiday_data.get('description', ''),
            "created_by": user_emp_id,
            "created_at": datetime.now(),
            "is_active": True,
            "holiday_id": holiday_data.get('holiday_id', f"HOL-{datetime.now().timestamp()}")
        }
        
        public_holidays_collection.insert_one(holiday_dict)
        inserted_count += 1
    
    return inserted_count 