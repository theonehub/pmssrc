import logging
from datetime import datetime
from models.public_holiday import PublicHoliday
from database.database_connector import connect_to_database

logger = logging.getLogger(__name__)

def get_holiday_collection(company_id: str):
    db = connect_to_database(company_id)
    return db["public_holidays"]


async def get_all_holidays(hostname: str):
    """
    Retrieves all active public holidays from the database.
    """
    collection = await get_holiday_collection(hostname)
    holidays = []
    cursor = collection.find({"is_active": True})
    async for doc in cursor:
        holidays.append(PublicHoliday(**doc))
    return holidays

async def create_holiday(holiday: PublicHoliday, emp_id: str, hostname: str):
    """
    Creates a new public holiday in the database.
    """
    collection = await get_holiday_collection(hostname)
    
    holiday_dict = holiday.dict(exclude={"id"})
    holiday_dict["holiday_id"] = holiday.holiday_id
    holiday_dict["day"] = holiday.date.day
    holiday_dict["month"] = holiday.date.month
    holiday_dict["year"] = holiday.date.year
    holiday_dict["created_at"] = datetime.now()
    holiday_dict["created_by"] = emp_id
    
    result = await collection.insert_one(holiday_dict)
    return holiday_dict["holiday_id"]

async def get_holiday_by_month(month: int, year: int, hostname: str):
    """
    Retrieves all active public holidays for a specific month and year.
    """
    collection = await get_holiday_collection(hostname)
    holidays = []
    cursor = collection.find({"month": month, "year": year, "is_active": True})
    async for doc in cursor:
        holidays.append(PublicHoliday(**doc))
    return holidays

async def get_holiday_by_date_str(date_str: str, hostname: str):
    """
    Retrieves a public holiday by date.
    """
    collection = await get_holiday_collection(hostname)
    holiday = await collection.find_one({"date": date_str})
    return PublicHoliday(**holiday) if holiday else None

async def update_holiday(holiday_id: str, holiday: PublicHoliday, emp_id: str, hostname: str):
    """
    Updates an existing public holiday.
    Returns True if a document was updated, False otherwise.
    """
    collection = await get_holiday_collection(hostname)
    
    holiday_dict = holiday.dict(exclude={"id"})
    holiday_dict["created_by"] = emp_id
    
    result = await collection.update_one(
        {"holiday_id": holiday_id},
        {"$set": holiday_dict}
    )
    
    return result.matched_count > 0

async def import_holidays(holiday_data_list: list, emp_id: str, hostname: str):
    """
    Imports multiple holidays from processed data.
    Returns the number of successfully imported holidays.
    """
    collection = await get_holiday_collection(hostname)
    inserted_count = 0
    
    for holiday_data in holiday_data_list:
        holiday_dict = {
            "name": holiday_data['name'],
            "date": datetime.strptime(holiday_data['date'], '%Y-%m-%d') if isinstance(holiday_data['date'], str) else holiday_data['date'],
            "description": holiday_data.get('description', ''),
            "created_by": emp_id,
            "created_at": datetime.now(),
            "is_active": True,
            "holiday_id": holiday_data.get('holiday_id', f"HOL-{datetime.now().timestamp()}")
        }
        
        await collection.insert_one(holiday_dict)
        inserted_count += 1
    
    return inserted_count 