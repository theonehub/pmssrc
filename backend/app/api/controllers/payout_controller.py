"""
SOLID-Compliant Payout Controller
Handles HTTP requests for payout operations
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import date, datetime

from app.application.dto.payroll_dto import (
    PayoutCalculationRequestDTO, PayoutCreateRequestDTO, PayoutUpdateRequestDTO,
    BulkPayoutRequestDTO, PayoutSearchFiltersDTO, PayslipGenerationRequestDTO,
    PayoutResponseDTO, PayoutSummaryResponseDTO, PayoutHistoryResponseDTO,
    BulkPayoutResponseDTO, PayslipResponseDTO, PayrollErrorResponseDTO
)
from app.infrastructure.services.payroll_migration_service import (
    calculate_monthly_payout_service,
    create_payout_service,
    get_employee_payouts_service,
    get_payout_by_id_service,
    update_payout_service,
    update_payout_status_service,
    bulk_process_monthly_payouts_service,
    get_monthly_payouts_service,
    get_monthly_payout_summary_service,
    generate_payslip_data_service,
    get_employee_payout_history_service
)

logger = logging.getLogger(__name__)


class PayoutController:
    """
    SOLID-compliant controller for payout operations.
    
    Responsibilities:
    - Handle HTTP request/response mapping
    - Validate input data
    - Coordinate with business services
    - Return standardized responses
    """
    
    def __init__(self):
        """Initialize payout controller."""
        pass
    
    async def health_check(self) -> Dict[str, str]:
        """Health check endpoint for payout service."""
        return {
            "service": "payout_service", 
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        }
    
    async def calculate_payout(
        self, 
        request: PayoutCalculationRequestDTO,
        hostname: str
    ) -> PayoutResponseDTO:
        """
        Calculate monthly payout for an employee.
        
        Args:
            request: Payout calculation request
            hostname: Organization hostname
            
        Returns:
            Calculated payout response
        """
        try:
            logger.info(f"Calculating payout for employee {request.employee_id}")
            
            # Call the service layer
            payout_data = calculate_monthly_payout_service(
                employee_id=request.employee_id,
                month=request.month,
                year=request.year,
                hostname=hostname,
                override_salary=request.override_salary
            )
            
            # Convert to response DTO
            return PayoutResponseDTO(**payout_data.dict())
            
        except Exception as e:
            logger.error(f"Error calculating payout: {e}")
            raise
    
    async def create_payout(
        self,
        request: PayoutCreateRequestDTO,
        hostname: str
    ) -> PayoutResponseDTO:
        """
        Create a new payout record.
        
        Args:
            request: Payout creation request
            hostname: Organization hostname
            
        Returns:
            Created payout response
        """
        try:
            logger.info(f"Creating payout for employee {request.employee_id}")
            
            # Convert request to domain model
            from app.domain.entities.payout import PayoutCreate
            payout_create = PayoutCreate(**request.dict())
            
            # Call the service layer
            payout_data = create_payout_service(payout_create, hostname)
            
            # Convert to response DTO
            return PayoutResponseDTO(**payout_data.dict())
            
        except Exception as e:
            logger.error(f"Error creating payout: {e}")
            raise
    
    async def get_employee_payouts(
        self,
        employee_id: str,
        hostname: str,
        year: Optional[int] = None,
        month: Optional[int] = None
    ) -> List[PayoutResponseDTO]:
        """
        Get payouts for a specific employee.
        
        Args:
            employee_id: Employee ID
            hostname: Organization hostname
            year: Filter by year (optional)
            month: Filter by month (optional)
            
        Returns:
            List of employee payouts
        """
        try:
            logger.info(f"Getting payouts for employee {employee_id}")
            
            # Call the service layer
            payouts = get_employee_payouts_service(employee_id, hostname, year, month)
            
            # Convert to response DTOs
            return [PayoutResponseDTO(**payout.dict()) for payout in payouts]
            
        except Exception as e:
            logger.error(f"Error getting employee payouts: {e}")
            raise
    
    async def get_payout_by_id(
        self,
        payout_id: str,
        hostname: str
    ) -> PayoutResponseDTO:
        """
        Get payout by ID.
        
        Args:
            payout_id: Payout ID
            hostname: Organization hostname
            
        Returns:
            Payout response
        """
        try:
            logger.info(f"Getting payout {payout_id}")
            
            # Call the service layer
            payout = get_payout_by_id_service(payout_id, hostname)
            
            # Convert to response DTO
            return PayoutResponseDTO(**payout.dict())
            
        except Exception as e:
            logger.error(f"Error getting payout by ID: {e}")
            raise
    
    async def update_payout(
        self,
        payout_id: str,
        request: PayoutUpdateRequestDTO,
        hostname: str
    ) -> PayoutResponseDTO:
        """
        Update a payout record.
        
        Args:
            payout_id: Payout ID to update
            request: Update request data
            hostname: Organization hostname
            
        Returns:
            Updated payout response
        """
        try:
            logger.info(f"Updating payout {payout_id}")
            
            # Convert request to domain model
            from app.domain.entities.payout import PayoutUpdate
            payout_update = PayoutUpdate(**request.dict())
            
            # Call the service layer
            payout_data = update_payout_service(payout_id, payout_update, hostname)
            
            # Convert to response DTO
            return PayoutResponseDTO(**payout_data.dict())
            
        except Exception as e:
            logger.error(f"Error updating payout: {e}")
            raise
    
    async def update_payout_status(
        self,
        payout_id: str,
        status: str,
        updated_by: str,
        hostname: str
    ) -> Dict[str, Any]:
        """
        Update payout status.
        
        Args:
            payout_id: Payout ID
            status: New status
            updated_by: User making the update
            hostname: Organization hostname
            
        Returns:
            Status update response
        """
        try:
            logger.info(f"Updating payout {payout_id} status to {status}")
            
            # Call the service layer
            from app.domain.entities.payout import PayoutStatus
            payout_status = PayoutStatus(status)
            
            result = update_payout_status_service(payout_id, payout_status, updated_by, hostname)
            
            return {"message": "Payout status updated successfully", "result": result}
            
        except Exception as e:
            logger.error(f"Error updating payout status: {e}")
            raise
    
    async def bulk_process_payouts(
        self,
        request: BulkPayoutRequestDTO,
        hostname: str
    ) -> BulkPayoutResponseDTO:
        """
        Process payouts for multiple employees.
        
        Args:
            request: Bulk payout request
            hostname: Organization hostname
            
        Returns:
            Bulk processing response
        """
        try:
            logger.info(f"Processing bulk payouts for {len(request.employee_ids)} employees")
            
            # Convert request to domain model
            from app.domain.entities.payout import BulkPayoutRequest
            bulk_request = BulkPayoutRequest(**request.dict())
            
            # Call the service layer
            result = bulk_process_monthly_payouts_service(bulk_request, hostname)
            
            # Convert to response DTO
            return BulkPayoutResponseDTO(**result.dict())
            
        except Exception as e:
            logger.error(f"Error processing bulk payouts: {e}")
            raise
    
    async def get_monthly_payouts(
        self,
        month: int,
        year: int,
        hostname: str,
        status: Optional[str] = None
    ) -> List[PayoutResponseDTO]:
        """
        Get all payouts for a specific month.
        
        Args:
            month: Month
            year: Year
            hostname: Organization hostname
            status: Filter by status (optional)
            
        Returns:
            List of monthly payouts
        """
        try:
            logger.info(f"Getting monthly payouts for {month}/{year}")
            
            # Call the service layer
            from app.domain.entities.payout import PayoutStatus
            status_enum = PayoutStatus(status) if status else None
            
            payouts = get_monthly_payouts_service(month, year, hostname, status_enum)
            
            # Convert to response DTOs
            return [PayoutResponseDTO(**payout.dict()) for payout in payouts]
            
        except Exception as e:
            logger.error(f"Error getting monthly payouts: {e}")
            raise
    
    async def get_monthly_payout_summary(
        self,
        month: int,
        year: int,
        hostname: str
    ) -> PayoutSummaryResponseDTO:
        """
        Get payout summary for a month.
        
        Args:
            month: Month
            year: Year
            hostname: Organization hostname
            
        Returns:
            Monthly payout summary
        """
        try:
            logger.info(f"Getting payout summary for {month}/{year}")
            
            # Call the service layer
            summary = get_monthly_payout_summary_service(month, year, hostname)
            
            # Convert to response DTO
            return PayoutSummaryResponseDTO(**summary.dict())
            
        except Exception as e:
            logger.error(f"Error getting payout summary: {e}")
            raise
    
    async def generate_payslip(
        self,
        request: PayslipGenerationRequestDTO,
        hostname: str
    ) -> PayslipResponseDTO:
        """
        Generate payslip for a payout.
        
        Args:
            request: Payslip generation request
            hostname: Organization hostname
            
        Returns:
            Generated payslip response
        """
        try:
            logger.info(f"Generating payslip for payout {request.payout_id}")
            
            # Call the service layer
            payslip_data = generate_payslip_data_service(request.payout_id, hostname)
            
            # Convert to response DTO
            return PayslipResponseDTO(**payslip_data.dict())
            
        except Exception as e:
            logger.error(f"Error generating payslip: {e}")
            raise
    
    async def get_employee_payout_history(
        self,
        employee_id: str,
        year: int,
        hostname: str
    ) -> PayoutHistoryResponseDTO:
        """
        Get payout history for an employee.
        
        Args:
            employee_id: Employee ID
            year: Year
            hostname: Organization hostname
            
        Returns:
            Employee payout history
        """
        try:
            logger.info(f"Getting payout history for employee {employee_id}")
            
            # Call the service layer
            history = get_employee_payout_history_service(employee_id, year, hostname)
            
            # Convert to response DTO
            return PayoutHistoryResponseDTO(**history.dict())
            
        except Exception as e:
            logger.error(f"Error getting payout history: {e}")
            raise
