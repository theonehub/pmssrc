"""
Monthly Salary Controller
HTTP controller for monthly salary operations
"""

import logging
from typing import Optional
from fastapi import HTTPException, status

from app.application.interfaces.services.monthly_salary_service import MonthlySalaryService
from app.application.dto.monthly_salary_dto import (
    MonthlySalaryResponseDTO,
    MonthlySalaryListResponseDTO,
    MonthlySalaryFilterDTO,
    MonthlySalaryComputeRequestDTO,
    MonthlySalaryBulkComputeRequestDTO,
    MonthlySalaryBulkComputeResponseDTO,
    MonthlySalaryStatusUpdateRequestDTO,
    MonthlySalarySummaryDTO
)
from app.auth.auth_dependencies import CurrentUser

logger = logging.getLogger(__name__)


class MonthlySalaryController:
    """Controller for monthly salary operations."""
    
    def __init__(self, monthly_salary_service: MonthlySalaryService):
        """
        Initialize controller with service.
        
        Args:
            monthly_salary_service: Monthly salary service
        """
        self.monthly_salary_service = monthly_salary_service
    
    async def get_monthly_salary(
        self,
        employee_id: str,
        month: int,
        year: int,
        current_user: CurrentUser
    ) -> Optional[MonthlySalaryResponseDTO]:
        """
        Get monthly salary for an employee.
        
        Args:
            employee_id: Employee ID
            month: Month (1-12)
            year: Year
            current_user: Current user context
            
        Returns:
            Optional[MonthlySalaryResponseDTO]: Monthly salary data
            
        Raises:
            HTTPException: For validation or processing errors
        """
        try:
            logger.info(f"Getting monthly salary for employee {employee_id}, {month}/{year}")
            
            # Validate month and year
            if month < 1 or month > 12:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Month must be between 1 and 12"
                )
            
            if year < 2020 or year > 2030:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Year must be between 2020 and 2030"
                )
            
            result = await self.monthly_salary_service.get_monthly_salary(
                employee_id=employee_id,
                month=month,
                year=year,
                current_user=current_user
            )
            
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Monthly salary not found for employee {employee_id}, {month}/{year}"
                )
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting monthly salary for {employee_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error occurred"
            )
    
    async def get_monthly_salaries_for_period(
        self,
        month: int,
        year: int,
        current_user: CurrentUser,
        status_filter: Optional[str] = None,
        department: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> MonthlySalaryListResponseDTO:
        """
        Get all monthly salaries for a period.
        
        Args:
            month: Month (1-12)
            year: Year
            current_user: Current user context
            status_filter: Optional status filter
            department: Optional department filter
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            MonthlySalaryListResponseDTO: List of monthly salaries
            
        Raises:
            HTTPException: For validation or processing errors
        """
        try:
            logger.info(f"Getting monthly salaries for period {month}/{year}")
            
            # Validate parameters
            if month < 1 or month > 12:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Month must be between 1 and 12"
                )
            
            if year < 2020 or year > 2030:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Year must be between 2020 and 2030"
                )
            
            if limit > 1000:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Limit cannot exceed 1000"
                )
            
            # Create filters
            filters = MonthlySalaryFilterDTO(
                month=month,
                year=year,
                status=status_filter,
                department=department,
                skip=skip,
                limit=limit
            )
            
            result = await self.monthly_salary_service.get_monthly_salaries_for_period(
                month=month,
                year=year,
                current_user=current_user,
                filters=filters
            )
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting monthly salaries for period {month}/{year}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error occurred"
            )
    
    async def compute_monthly_salary(
        self,
        request: MonthlySalaryComputeRequestDTO,
        current_user: CurrentUser
    ) -> MonthlySalaryResponseDTO:
        """
        Compute monthly salary for an employee.
        
        Args:
            request: Compute request data
            current_user: Current user context
            
        Returns:
            MonthlySalaryResponseDTO: Computed monthly salary
            
        Raises:
            HTTPException: For validation or processing errors
        """
        try:
            logger.info(f"Computing monthly salary for employee {request.employee_id}")
            
            # Set computed_by if not provided
            if not request.computed_by:
                request.computed_by = current_user.employee_id
            
            result = await self.monthly_salary_service.compute_monthly_salary(
                request=request,
                current_user=current_user
            )
            
            return result
            
        except ValueError as e:
            logger.warning(f"Validation error computing monthly salary: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error computing monthly salary for {request.employee_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error occurred"
            )
    
    async def bulk_compute_monthly_salaries(
        self,
        request: MonthlySalaryBulkComputeRequestDTO,
        current_user: CurrentUser
    ) -> MonthlySalaryBulkComputeResponseDTO:
        """
        Bulk compute monthly salaries.
        
        Args:
            request: Bulk compute request data
            current_user: Current user context
            
        Returns:
            MonthlySalaryBulkComputeResponseDTO: Bulk compute results
            
        Raises:
            HTTPException: For validation or processing errors
        """
        try:
            logger.info(f"Bulk computing monthly salaries for {request.month}/{request.year}")
            
            # Set computed_by if not provided
            if not request.computed_by:
                request.computed_by = current_user.employee_id
            
            result = await self.monthly_salary_service.bulk_compute_monthly_salaries(
                request=request,
                current_user=current_user
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in bulk compute for {request.month}/{request.year}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error occurred"
            )
    
    async def update_monthly_salary_status(
        self,
        request: MonthlySalaryStatusUpdateRequestDTO,
        current_user: CurrentUser
    ) -> MonthlySalaryResponseDTO:
        """
        Update monthly salary status.
        
        Args:
            request: Status update request data
            current_user: Current user context
            
        Returns:
            MonthlySalaryResponseDTO: Updated monthly salary
            
        Raises:
            HTTPException: For validation or processing errors
        """
        try:
            logger.info(f"Updating status for employee {request.employee_id}")
            
            # Set updated_by if not provided
            if not request.updated_by:
                request.updated_by = current_user.employee_id
            
            result = await self.monthly_salary_service.update_monthly_salary_status(
                request=request,
                current_user=current_user
            )
            
            return result
            
        except ValueError as e:
            logger.warning(f"Validation error updating status: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error updating status for {request.employee_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error occurred"
            )
    
    async def get_monthly_salary_summary(
        self,
        month: int,
        year: int,
        current_user: CurrentUser
    ) -> MonthlySalarySummaryDTO:
        """
        Get monthly salary summary for a period.
        
        Args:
            month: Month (1-12)
            year: Year
            current_user: Current user context
            
        Returns:
            MonthlySalarySummaryDTO: Summary data
            
        Raises:
            HTTPException: For validation or processing errors
        """
        try:
            logger.info(f"Getting summary for {month}/{year}")
            
            # Validate parameters
            if month < 1 or month > 12:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Month must be between 1 and 12"
                )
            
            if year < 2020 or year > 2030:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Year must be between 2020 and 2030"
                )
            
            result = await self.monthly_salary_service.get_monthly_salary_summary(
                month=month,
                year=year,
                current_user=current_user
            )
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting summary for {month}/{year}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error occurred"
            )
    
    async def delete_monthly_salary(
        self,
        employee_id: str,
        month: int,
        year: int,
        current_user: CurrentUser
    ) -> dict:
        """
        Delete monthly salary record.
        
        Args:
            employee_id: Employee ID
            month: Month (1-12)
            year: Year
            current_user: Current user context
            
        Returns:
            dict: Success message
            
        Raises:
            HTTPException: For validation or processing errors
        """
        try:
            logger.info(f"Deleting monthly salary for employee {employee_id}, {month}/{year}")
            
            # Validate parameters
            if month < 1 or month > 12:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Month must be between 1 and 12"
                )
            
            if year < 2020 or year > 2030:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Year must be between 2020 and 2030"
                )
            
            deleted = await self.monthly_salary_service.delete_monthly_salary(
                employee_id=employee_id,
                month=month,
                year=year,
                current_user=current_user
            )
            
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Monthly salary not found for employee {employee_id}, {month}/{year}"
                )
            
            return {"message": "Monthly salary deleted successfully"}
            
        except HTTPException:
            raise
        except ValueError as e:
            logger.warning(f"Validation error deleting monthly salary: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error deleting monthly salary for {employee_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error occurred"
            ) 