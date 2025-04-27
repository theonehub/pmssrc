from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, logger
from typing import List
from models.public_holiday import PublicHoliday
from models.user_model import UserInfo
from auth.auth import get_current_user, extract_hostname, role_checker, extract_emp_id
import io
import logging
import services.public_holiday_service as holiday_service
import pandas as pd

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/public-holidays",
    tags=["Public Holidays"]
)

@router.get("/", response_model=List[PublicHoliday])
async def get_public_holidays(hostname: str = Depends(extract_hostname)):
    """
    Get all active public holidays for the company.
    """
    return holiday_service.get_all_holidays(hostname)

@router.post("/")
async def create_public_holiday(
    holiday: PublicHoliday, 
    current_emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["admin", "superadmin"]))
):
    """
    Create a new public holiday.
    Only admins and superadmins can create holidays.
    """
    logger.info(f"Creating public holiday: {holiday}")
    holiday_id = holiday_service.create_holiday(holiday, current_emp_id, hostname)
    return {"message": "Public holiday created successfully", "id": holiday_id}

@router.get("/month/{month}/{year}")
async def get_holiday_by_month(
    month: int, 
    year: int, 
    hostname: str = Depends(extract_hostname)
):
    return holiday_service.get_holiday_by_month(month, year, hostname)    

@router.put("/{holiday_id}")
async def update_public_holiday(
    holiday_id: str, 
    holiday: PublicHoliday, 
    current_emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["admin", "superadmin"]))
):
    """
    Update an existing public holiday.
    Only admins and superadmins can update holidays.
    """
    updated = holiday_service.update_holiday(holiday_id, holiday, current_emp_id, hostname)
    
    if not updated:
        raise HTTPException(status_code=404, detail="Holiday not found")
    
    return {"message": "Public holiday updated successfully"}

@router.post("/import")
async def import_holidays(
    file: UploadFile = File(...), 
    current_emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["admin", "superadmin"]))
):
    """
    Import multiple holidays from an Excel file.
    Only admins and superadmins can import holidays.
    """
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Only Excel files are allowed")
    
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # Convert DataFrame to list of dictionaries
        holiday_data_list = df.to_dict('records')
        
        inserted_count = holiday_service.import_holidays_from_file(
            holiday_data_list, 
            current_emp_id,
            hostname
        )
        
        return {"message": f"Successfully imported {inserted_count} holidays"}
    except Exception as e:
        logger.error(f"Error importing holidays: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e)) 