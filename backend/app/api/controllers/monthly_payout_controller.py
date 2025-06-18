"""
Monthly Payout Controller
FastAPI controller for monthly payout operations with LWP integration
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status, Depends, Query
from datetime import datetime

from app.application.use_cases.payroll.compute_monthly_payout_use_case import ComputeMonthlyPayoutUseCase
from app.application.dto.payroll_dto import (
    MonthlyPayoutRequestDTO, 
    MonthlyPayoutResponseDTO, 
    BulkPayoutRequestDTO,
    PayoutSearchFiltersDTO,
    PayoutUpdateDTO,
    PayoutSummaryDTO,
    PayoutApprovalDTO,
    PayoutProcessingDTO,
    PayslipDataDTO
)
from app.auth.auth_dependencies import get_current_user, CurrentUser

logger = logging.getLogger(__name__)


class MonthlyPayoutController:
    """Controller for monthly payout operations."""
    
    def __init__(self, compute_payout_use_case: ComputeMonthlyPayoutUseCase):
        self._compute_payout_use_case = compute_payout_use_case
    
    async def compute_employee_monthly_payout(
        self,
        request: MonthlyPayoutRequestDTO,
        current_user: CurrentUser = Depends(get_current_user)
    ) -> MonthlyPayoutResponseDTO:
        """
        Compute monthly payout for a single employee.
        
        Args:
            request: Monthly payout request
            current_user: Current authenticated user
            
        Returns:
            Monthly payout response
        """
        try:
            logger.info(f"Computing monthly payout for employee {request.employee_id} by user {current_user.user_id}")
            
            response = await self._compute_payout_use_case.compute_employee_monthly_payout(
                request, 
                current_user.hostname
            )
            
            return response
            
        except ValueError as e:
            logger.error(f"Validation error in compute monthly payout: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error computing monthly payout: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to compute monthly payout"
            )
    
    async def compute_bulk_monthly_payouts(
        self,
        request: BulkPayoutRequestDTO,
        current_user: CurrentUser = Depends(get_current_user)
    ) -> Dict[str, Any]:
        """
        Compute monthly payouts for multiple employees.
        
        Args:
            request: Bulk payout request
            current_user: Current authenticated user
            
        Returns:
            Bulk computation results
        """
        try:
            logger.info(f"Computing bulk monthly payouts for {len(request.employee_ids)} employees by user {current_user.user_id}")
            
            results = await self._compute_payout_use_case.compute_bulk_monthly_payouts(
                request,
                current_user.hostname
            )
            
            return results
            
        except ValueError as e:
            logger.error(f"Validation error in bulk compute: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error computing bulk payouts: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to compute bulk payouts"
            )
    
    async def get_employee_monthly_payout(
        self,
        employee_id: str,
        month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
        year: int = Query(..., ge=2020, le=2050, description="Year"),
        current_user: CurrentUser = Depends(get_current_user)
    ) -> MonthlyPayoutResponseDTO:
        """
        Get existing monthly payout for an employee.
        
        Args:
            employee_id: Employee ID
            month: Month
            year: Year
            current_user: Current authenticated user
            
        Returns:
            Monthly payout response
        """
        try:
            payout = await self._compute_payout_use_case.get_employee_monthly_payout(
                employee_id,
                month,
                year,
                current_user.hostname
            )
            
            if not payout:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Payout not found for employee {employee_id} for {month}/{year}"
                )
            
            return payout
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting monthly payout: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get monthly payout"
            )
    
    async def get_monthly_payouts_summary(
        self,
        month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
        year: int = Query(..., ge=2020, le=2050, description="Year"),
        current_user: CurrentUser = Depends(get_current_user)
    ) -> Dict[str, Any]:
        """
        Get summary of all monthly payouts for a given month.
        
        Args:
            month: Month
            year: Year
            current_user: Current authenticated user
            
        Returns:
            Monthly payouts summary
        """
        try:
            summary = await self._compute_payout_use_case.get_monthly_payouts_summary(
                month,
                year,
                current_user.hostname
            )
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting payouts summary: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get payouts summary"
            )
    
    async def search_monthly_payouts(
        self,
        employee_id: Optional[str] = Query(None, description="Employee ID filter"),
        month: Optional[int] = Query(None, ge=1, le=12, description="Month filter"),
        year: Optional[int] = Query(None, ge=2020, le=2050, description="Year filter"),
        status: Optional[str] = Query(None, description="Status filter"),
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(50, ge=1, le=500, description="Page size"),
        sort_by: Optional[str] = Query("calculation_date", description="Sort field"),
        sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
        current_user: CurrentUser = Depends(get_current_user)
    ) -> Dict[str, Any]:
        """
        Search monthly payouts with filters and pagination.
        
        Args:
            employee_id: Employee ID filter
            month: Month filter
            year: Year filter
            status: Status filter
            page: Page number
            page_size: Page size
            sort_by: Sort field
            sort_order: Sort order
            current_user: Current authenticated user
            
        Returns:
            Search results with pagination
        """
        try:
            filters = PayoutSearchFiltersDTO(
                employee_id=employee_id,
                month=month,
                year=year,
                status=status,
                page=page,
                page_size=page_size,
                sort_by=sort_by,
                sort_order=sort_order
            )
            
            # Note: This would need to be implemented in the use case
            # For now, return a placeholder
            return {
                "payouts": [],
                "total_count": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0
            }
            
        except Exception as e:
            logger.error(f"Error searching payouts: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to search payouts"
            )
    
    async def update_monthly_payout(
        self,
        employee_id: str,
        month: int,
        year: int,
        update_data: PayoutUpdateDTO,
        current_user: CurrentUser = Depends(get_current_user)
    ) -> MonthlyPayoutResponseDTO:
        """
        Update monthly payout details.
        
        Args:
            employee_id: Employee ID
            month: Month
            year: Year
            update_data: Update data
            current_user: Current authenticated user
            
        Returns:
            Updated payout response
        """
        try:
            # Note: This would need to be implemented in the use case
            # For now, just get the existing payout
            payout = await self._compute_payout_use_case.get_employee_monthly_payout(
                employee_id,
                month,
                year,
                current_user.hostname
            )
            
            if not payout:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Payout not found for employee {employee_id} for {month}/{year}"
                )
            
            # Update logic would go here
            return payout
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating monthly payout: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update monthly payout"
            )
    
    async def approve_monthly_payout(
        self,
        employee_id: str,
        month: int,
        year: int,
        current_user: CurrentUser = Depends(get_current_user)
    ) -> MonthlyPayoutResponseDTO:
        """
        Approve a monthly payout.
        
        Args:
            employee_id: Employee ID
            month: Month
            year: Year
            current_user: Current authenticated user
            
        Returns:
            Updated payout response
        """
        try:
            payout = await self._compute_payout_use_case.approve_monthly_payout(
                employee_id,
                month,
                year,
                current_user.hostname,
                current_user.user_id
            )
            
            return payout
            
        except ValueError as e:
            logger.error(f"Validation error in approve payout: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error approving monthly payout: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to approve monthly payout"
            )
    
    async def process_monthly_payout(
        self,
        employee_id: str,
        month: int,
        year: int,
        current_user: CurrentUser = Depends(get_current_user)
    ) -> MonthlyPayoutResponseDTO:
        """
        Process a monthly payout.
        
        Args:
            employee_id: Employee ID
            month: Month
            year: Year
            current_user: Current authenticated user
            
        Returns:
            Updated payout response
        """
        try:
            payout = await self._compute_payout_use_case.process_monthly_payout(
                employee_id,
                month,
                year,
                current_user.hostname,
                current_user.user_id
            )
            
            return payout
            
        except ValueError as e:
            logger.error(f"Validation error in process payout: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error processing monthly payout: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process monthly payout"
            )
    
    async def bulk_approve_payouts(
        self,
        request: PayoutApprovalDTO,
        current_user: CurrentUser = Depends(get_current_user)
    ) -> Dict[str, Any]:
        """
        Approve multiple payouts in bulk.
        
        Args:
            request: Bulk approval request
            current_user: Current authenticated user
            
        Returns:
            Bulk approval results
        """
        try:
            # Note: This would need to be implemented in the use case
            # For now, return a placeholder
            return {
                "successful_approvals": len(request.payout_ids),
                "failed_approvals": 0,
                "results": {payout_id: True for payout_id in request.payout_ids}
            }
            
        except Exception as e:
            logger.error(f"Error in bulk approve payouts: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to bulk approve payouts"
            )
    
    async def bulk_process_payouts(
        self,
        request: PayoutProcessingDTO,
        current_user: CurrentUser = Depends(get_current_user)
    ) -> Dict[str, Any]:
        """
        Process multiple payouts in bulk.
        
        Args:
            request: Bulk processing request
            current_user: Current authenticated user
            
        Returns:
            Bulk processing results
        """
        try:
            # Note: This would need to be implemented in the use case
            # For now, return a placeholder
            return {
                "successful_processing": len(request.payout_ids),
                "failed_processing": 0,
                "results": {payout_id: True for payout_id in request.payout_ids}
            }
            
        except Exception as e:
            logger.error(f"Error in bulk process payouts: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to bulk process payouts"
            )
    
    async def get_employee_payslip(
        self,
        employee_id: str,
        month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
        year: int = Query(..., ge=2020, le=2050, description="Year"),
        current_user: CurrentUser = Depends(get_current_user)
    ) -> PayslipDataDTO:
        """
        Get payslip data for an employee.
        
        Args:
            employee_id: Employee ID
            month: Month
            year: Year
            current_user: Current authenticated user
            
        Returns:
            Payslip data
        """
        try:
            payout = await self._compute_payout_use_case.get_employee_monthly_payout(
                employee_id,
                month,
                year,
                current_user.hostname
            )
            
            if not payout:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Payout not found for employee {employee_id} for {month}/{year}"
                )
            
            # Convert to payslip data
            payslip_data = PayslipDataDTO(
                payout_id=payout.payout_id,
                employee_id=payout.employee_id,
                employee_name=payout.employee_name,
                company_name="Your Company",  # This should come from organization data
                pay_period=f"{month:02d}/{year}",
                pay_period_start=f"01-{month:02d}-{year}",
                pay_period_end=f"30-{month:02d}-{year}",  # Simplified
                payout_date=f"30-{month:02d}-{year}",     # Simplified
                employee_details={},
                attendance={
                    "total_days_in_month": 30,
                    "working_days": 30,
                    "lwp_days": payout.lwp_days,
                    "effective_working_days": payout.effective_working_days
                },
                salary_breakdown={
                    "earnings": {
                        "basic_salary": payout.basic_salary,
                        "dearness_allowance": payout.dearness_allowance,
                        "hra": payout.hra,
                        "special_allowance": payout.special_allowance,
                        "transport_allowance": payout.transport_allowance,
                        "medical_allowance": payout.medical_allowance,
                        "bonus": payout.bonus,
                        "commission": payout.commission,
                        "other_allowances": payout.other_allowances,
                        "total_earnings": payout.adjusted_monthly_gross
                    },
                    "deductions": {
                        "epf_employee": payout.epf_employee,
                        "esi_employee": payout.esi_employee,
                        "professional_tax": payout.professional_tax,
                        "tds": payout.tds,
                        "advance_deduction": payout.advance_deduction,
                        "loan_deduction": payout.loan_deduction,
                        "other_deductions": payout.other_deductions,
                        "total_deductions": payout.total_deductions
                    },
                    "net_salary": payout.monthly_net_salary
                },
                tax_info={
                    "tax_regime": payout.tax_regime,
                    "annual_tax_liability": payout.annual_tax_liability,
                    "tax_exemptions": payout.tax_exemptions
                },
                lwp_impact={
                    "lwp_days": payout.lwp_days,
                    "lwp_factor": payout.lwp_factor,
                    "lwp_deduction_amount": payout.lwp_deduction_amount,
                    "base_monthly_gross": payout.base_monthly_gross
                },
                status=payout.status,
                notes=payout.notes
            )
            
            return payslip_data
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting payslip: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get payslip data"
            )
    
    async def get_pending_approvals(
        self,
        current_user: CurrentUser = Depends(get_current_user)
    ) -> List[MonthlyPayoutResponseDTO]:
        """
        Get payouts pending approval.
        
        Args:
            current_user: Current authenticated user
            
        Returns:
            List of payouts pending approval
        """
        try:
            # Note: This would need to be implemented in the use case
            # For now, return an empty list
            return []
            
        except Exception as e:
            logger.error(f"Error getting pending approvals: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get pending approvals"
            ) 