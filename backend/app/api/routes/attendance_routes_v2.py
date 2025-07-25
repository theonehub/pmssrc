"""
SOLID-Compliant Attendance Routes
Clean API layer following SOLID principles
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.utils.logger import get_logger

logger = get_logger(__name__)


from app.api.controllers.attendance_controller import AttendanceController
from app.application.dto.attendance_dto import (
    AttendanceCheckInRequestDTO,
    AttendanceCheckOutRequestDTO,
    AttendanceSearchFiltersDTO,
    AttendanceResponseDTO,
    AttendanceStatisticsDTO,
    AttendanceValidationError,
    AttendanceBusinessRuleError,
    AttendanceNotFoundError
)
from app.auth.auth import role_checker
from app.auth.auth_dependencies import CurrentUser, get_current_user

# Create router
router = APIRouter(prefix="/v2/attendance", tags=["Attendance V2 (SOLID)"])


def get_attendance_controller() -> AttendanceController:
    """Dependency injection for attendance controller"""
    try:
        logger.info("Getting attendance controller from container")
        from app.config.dependency_container import get_dependency_container
        logger.info("Getting dependency container")
        container = get_dependency_container()
        logger.info("Getting attendance controller from container")
        return container.get_attendance_controller()
    except Exception as e:
        logger.warning(f"Could not get attendance controller from container: {e}")
        # Fallback to direct instantiation
        return AttendanceController()


# ==================== ATTENDANCE ENDPOINTS ====================

def convert_date_format(date_str):
    """Convert DD-MM-YYYY to YYYY-MM-DD"""
    return datetime.strptime(date_str, "%d-%m-%Y").strftime("%Y-%m-%d")


@router.post("/bulk/checkin/checkout/{employee_id}/start/{start_date}/{start_time}/end/{end_date}/{end_time}",
             response_model=List[AttendanceResponseDTO])
async def checkin_bulk(
    employee_id: str = Path(..., description="Employee ID"),
    start_date: str = Path(..., description="Start date"),
    end_date: str = Path(..., description="End date"),
    start_time: str = Path(..., description="Start time"),
    end_time: str = Path(..., description="End time"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: AttendanceController = Depends(get_attendance_controller)
):
    """Record employee check-in"""
    from datetime import datetime, timedelta
    try:
        logger.info(f"Check-in request for employee: {current_user.employee_id}")
        # Convert to YYYY-MM-DD string, then to datetime object
        start_date_str = convert_date_format(start_date)  # 'YYYY-MM-DD'
        end_date_str = convert_date_format(end_date)
        start_date_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date_dt = datetime.strptime(end_date_str, "%Y-%m-%d")

        # Accept both HH:MM and HH:MM:SS
        def parse_time(t):
            try:
                return datetime.strptime(t, "%H:%M:%S").strftime("%H:%M:%S")
            except ValueError:
                return datetime.strptime(t, "%H:%M").strftime("%H:%M:%S")

        start_time_fmt = parse_time(start_time)
        end_time_fmt = parse_time(end_time)

        responses = []
        current_date = start_date_dt
        while current_date <= end_date_dt:
            date_str = current_date.strftime("%Y-%m-%d")
            check_in_dt = f"{date_str}T{start_time_fmt}"
            check_out_dt = f"{date_str}T{end_time_fmt}"

            request_in = AttendanceCheckInRequestDTO(
                employee_id=employee_id,
                timestamp=date_str,
                check_in_time=check_in_dt
            )
            print(request_in)
            await controller.checkin(request_in, current_user)

            request_out = AttendanceCheckOutRequestDTO(
                employee_id=employee_id,
                timestamp=date_str,
                check_out_time=check_out_dt
            )
            response_out = await controller.checkout(request_out, current_user)
            responses.append(response_out)

            current_date += timedelta(days=1)
        
        return responses
    except Exception as e:
        logger.error(f"Unexpected error during check-in: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/checkin", response_model=AttendanceResponseDTO)
async def checkin(
    current_user: CurrentUser = Depends(get_current_user),
    controller: AttendanceController = Depends(get_attendance_controller)
):
    """Record employee check-in"""
    try:
        logger.info(f"Check-in request for employee: {current_user.employee_id}")
        
        request = AttendanceCheckInRequestDTO(
            employee_id=current_user.employee_id,
            timestamp=datetime.now()
        )
        
        response = await controller.checkin(request, current_user)
        
        return response
        
    except AttendanceValidationError as e:
        logger.warning(f"Validation error during check-in: {e}")
        raise HTTPException(status_code=400, detail={"error": "validation_error", "message": str(e)})
    
    except AttendanceBusinessRuleError as e:
        logger.warning(f"Business rule error during check-in: {e}")
        raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
    
    except Exception as e:
        logger.error(f"Unexpected error during check-in: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/checkout", response_model=AttendanceResponseDTO)
async def checkout(
    current_user: CurrentUser = Depends(get_current_user),
    controller: AttendanceController = Depends(get_attendance_controller)
):
    """Record employee check-out"""
    try:
        logger.info(f"Check-out request for employee: {current_user.employee_id}")
        
        request = AttendanceCheckOutRequestDTO(
            employee_id=current_user.employee_id,
            timestamp=datetime.now()
        )
        
        response = await controller.checkout(request, current_user)
        
        return response
        
    except AttendanceValidationError as e:
        logger.warning(f"Validation error during check-out: {e}")
        raise HTTPException(status_code=400, detail={"error": "validation_error", "message": str(e)})
    
    except AttendanceBusinessRuleError as e:
        logger.warning(f"Business rule error during check-out: {e}")
        raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
    
    except Exception as e:
        logger.error(f"Unexpected error during check-out: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/employee/{employee_id}/month/{month}/year/{year}", response_model=List[AttendanceResponseDTO])
async def get_employee_attendance_by_month(
    employee_id: str = Path(..., description="Employee ID"),
    month: int = Path(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Path(..., ge=2000, le=3000, description="Year"),
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(role_checker(["admin", "superadmin", "manager"])),
    controller: AttendanceController = Depends(get_attendance_controller)
):
    """Get employee attendance records for a specific month"""
    try:
        logger.info(f"Getting attendance for employee {employee_id} for {month}/{year}")
        
        filters = AttendanceSearchFiltersDTO(
            employee_id=employee_id,
            month=month,
            year=year
        )
        
        response = await controller.get_employee_attendance_by_month(filters, current_user)
        
        return response
        
    except AttendanceNotFoundError as e:
        logger.warning(f"Attendance not found: {e}")
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": str(e)})
    
    except Exception as e:
        logger.error(f"Error getting employee attendance: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/employee/{employee_id}/year/{year}", response_model=List[AttendanceResponseDTO])
async def get_employee_attendance_by_year(
    employee_id: str = Path(..., description="Employee ID"),
    year: int = Path(..., ge=2000, le=3000, description="Year"),
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(role_checker(["admin", "superadmin", "manager"])),
    controller: AttendanceController = Depends(get_attendance_controller)
):
    """Get employee attendance records for a specific year"""
    try:
        logger.info(f"Getting attendance for employee {employee_id} for year {year}")
        
        filters = AttendanceSearchFiltersDTO(
            employee_id=employee_id,
            year=year
        )
        
        response = await controller.get_employee_attendance_by_year(filters, current_user)
        
        return response
        
    except AttendanceNotFoundError as e:
        logger.warning(f"Attendance not found: {e}")
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": str(e)})
    
    except Exception as e:
        logger.error(f"Error getting employee attendance: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/team/date/{date}/month/{month}/year/{year}", response_model=List[AttendanceResponseDTO])
async def get_team_attendance_by_date(
    date: int = Path(..., ge=1, le=31, description="Date (1-31)"),
    month: int = Path(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Path(..., ge=2000, le=3000, description="Year"),
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(role_checker(["admin", "superadmin", "manager"])),
    controller: AttendanceController = Depends(get_attendance_controller)
):
    """Get team attendance records for a specific date"""
    try:
        logger.info(f"Getting team attendance for {date}/{month}/{year}")
        
        filters = AttendanceSearchFiltersDTO(
            manager_id=current_user.employee_id,
            date=date,
            month=month,
            year=year
        )
        
        response = await controller.get_team_attendance_by_date(filters, current_user)
        
        return response
        
    except AttendanceNotFoundError as e:
        logger.warning(f"Team attendance not found: {e}")
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": str(e)})
    
    except Exception as e:
        logger.error(f"Error getting team attendance: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/team/month/{month}/year/{year}", response_model=List[AttendanceResponseDTO])
async def get_team_attendance_by_month(
    month: int = Path(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Path(..., ge=2000, le=3000, description="Year"),
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(role_checker(["admin", "superadmin", "manager"])),
    controller: AttendanceController = Depends(get_attendance_controller)
):
    """Get team attendance records for a specific month"""
    try:
        logger.info(f"Getting team attendance for {month}/{year}")
        
        filters = AttendanceSearchFiltersDTO(
            manager_id=current_user.employee_id,
            month=month,
            year=year
        )
        
        response = await controller.get_team_attendance_by_month(filters, current_user)
        
        return response
        
    except AttendanceNotFoundError as e:
        logger.warning(f"Team attendance not found: {e}")
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": str(e)})
    
    except Exception as e:
        logger.error(f"Error getting team attendance: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stats/today", response_model=AttendanceStatisticsDTO)
async def get_todays_attendance_stats(
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(role_checker(["admin", "superadmin", "manager"])),
    controller: AttendanceController = Depends(get_attendance_controller)
):
    """Get today's attendance statistics"""
    try:
        logger.info("Getting today's attendance statistics")
        
        response = await controller.get_todays_attendance_stats(current_user)
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting attendance statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/my/month/{month}/year/{year}", response_model=List[AttendanceResponseDTO])
async def get_my_attendance_by_month(
    month: int = Path(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Path(..., ge=2000, le=3000, description="Year"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: AttendanceController = Depends(get_attendance_controller)
):
    """Get my attendance records for a specific month"""
    try:
        logger.info(f"Getting my attendance for {month}/{year}")
        
        filters = AttendanceSearchFiltersDTO(
            employee_id=current_user.employee_id,
            month=month,
            year=year
        )
        
        response = await controller.get_employee_attendance_by_month(filters, current_user)
        
        return response
        
    except AttendanceNotFoundError as e:
        logger.warning(f"My attendance not found: {e}")
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": str(e)})
    
    except Exception as e:
        logger.error(f"Error getting my attendance: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/my/year/{year}", response_model=List[AttendanceResponseDTO])
async def get_my_attendance_by_year(
    year: int = Path(..., ge=2000, le=3000, description="Year"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: AttendanceController = Depends(get_attendance_controller)
):
    """Get my attendance records for a specific year"""
    try:
        logger.info(f"Getting my attendance for year {year}")
        
        filters = AttendanceSearchFiltersDTO(
            employee_id=current_user.employee_id,
            year=year
        )
        
        response = await controller.get_employee_attendance_by_year(filters, current_user)
        
        return response
        
    except AttendanceNotFoundError as e:
        logger.warning(f"My attendance not found: {e}")
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": str(e)})
    
    except Exception as e:
        logger.error(f"Error getting my attendance: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/user/{employee_id}/{month}/{year}", response_model=List[Dict[str, Any]])
async def get_user_attendance_by_month_legacy(
    employee_id: str = Path(..., description="Employee ID"),
    month: int = Path(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Path(..., ge=2000, le=3000, description="Year"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: AttendanceController = Depends(get_attendance_controller)
):
    """
    Get user attendance records for a specific month (Legacy endpoint for frontend compatibility).
    
    This endpoint provides backward compatibility for the frontend while maintaining
    the same business logic as the V2 API.
    """
    try:
        logger.info(f"Getting attendance for employee {employee_id} for {month}/{year} (legacy endpoint)")
        
        filters = AttendanceSearchFiltersDTO(
            employee_id=employee_id,
            month=month,
            year=year
        )
        
        # Use the existing V2 controller method
        v2_response = await controller.get_employee_attendance_by_month(filters, current_user)
        
        # Transform to legacy format
        from app.application.dto.attendance_dto import LegacyAttendanceRecordDTO
        legacy_response = []
        for attendance in v2_response:
            legacy_record = LegacyAttendanceRecordDTO.from_attendance_response(attendance)
            legacy_response.append({
                "checkin_time": legacy_record.checkin_time,
                "checkout_time": legacy_record.checkout_time
            })
        
        return legacy_response
        
    except AttendanceNotFoundError as e:
        logger.warning(f"Attendance not found: {e}")
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": str(e)})
    
    except Exception as e:
        logger.error(f"Error getting employee attendance: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") 