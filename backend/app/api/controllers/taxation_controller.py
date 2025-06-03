"""
Taxation API Controller
Handles HTTP requests for taxation operations
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import HTTPException, status

from app.application.dto.taxation_dto import (
    TaxationCreateRequestDTO,
    TaxationUpdateRequestDTO,
    TaxationResponseDTO,
    TaxSearchFiltersDTO,
    TaxCalculationRequestDTO,
    TaxProjectionDTO,
    TaxComparisonDTO,
    TaxStatisticsDTO,
    TaxationValidationError,
    TaxationNotFoundError,
    TaxationBusinessRuleError,
    TaxationCalculationError
)
from app.application.use_cases.taxation.calculate_tax_use_case import CalculateTaxUseCase
from app.application.use_cases.taxation.create_taxation_use_case import (
    CreateTaxationUseCase,
    BulkCreateTaxationUseCase
)
from app.application.interfaces.repositories.taxation_repository import (
    TaxationQueryRepository,
    TaxationCommandRepository,
    TaxationAnalyticsRepository
)


logger = logging.getLogger(__name__)


class TaxationController:
    """
    Controller for taxation API operations.
    
    Follows SOLID principles:
    - SRP: Only handles HTTP request/response for taxation
    - OCP: Can be extended with new endpoints
    - LSP: Can be substituted with enhanced versions
    - ISP: Focused interface for taxation operations
    - DIP: Depends on use case abstractions
    """
    
    def __init__(
        self,
        calculate_tax_use_case: CalculateTaxUseCase,
        create_taxation_use_case: CreateTaxationUseCase,
        bulk_create_use_case: BulkCreateTaxationUseCase,
        query_repository: TaxationQueryRepository,
        command_repository: TaxationCommandRepository,
        analytics_repository: TaxationAnalyticsRepository
    ):
        self.calculate_tax_use_case = calculate_tax_use_case
        self.create_taxation_use_case = create_taxation_use_case
        self.bulk_create_use_case = bulk_create_use_case
        self.query_repository = query_repository
        self.command_repository = command_repository
        self.analytics_repository = analytics_repository
    
    async def create_taxation(
        self,
        request: TaxationCreateRequestDTO,
        hostname: str,
        current_user: str
    ) -> TaxationResponseDTO:
        """
        Create a new taxation record.
        
        Args:
            request: Taxation creation request
            hostname: Organisation hostname
            current_user: Current authenticated user
            
        Returns:
            Created taxation response
            
        Raises:
            HTTPException: If creation fails
        """
        try:
            logger.info(f"Creating taxation record for employee: {request.employee_id}")
            
            # Set created_by if not provided
            if not request.created_by:
                request.created_by = current_user
            
            taxation = await self.create_taxation_use_case.execute(request, hostname)
            
            logger.info(f"Taxation record created successfully: {taxation.taxation_id}")
            return taxation
            
        except TaxationValidationError as e:
            logger.warning(f"Validation error creating taxation: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Validation error: {str(e)}"
            )
        except TaxationBusinessRuleError as e:
            logger.warning(f"Business rule error creating taxation: {e}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Business rule violation: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error creating taxation: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create taxation record"
            )
    
    async def bulk_create_taxation(
        self,
        employee_ids: List[str],
        tax_year: str,
        hostname: str,
        current_user: str
    ) -> Dict[str, Any]:
        """
        Create taxation records for multiple employees.
        
        Args:
            employee_ids: List of employee identifiers
            tax_year: Tax year
            hostname: Organisation hostname
            current_user: Current authenticated user
            
        Returns:
            Bulk creation results
        """
        try:
            logger.info(f"Bulk creating taxation records for {len(employee_ids)} employees")
            
            results = await self.bulk_create_use_case.execute(
                employee_ids, tax_year, hostname, current_user
            )
            
            logger.info(f"Bulk taxation creation completed: {results['total']} records processed")
            return results
            
        except Exception as e:
            logger.error(f"Error in bulk taxation creation: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create taxation records in bulk"
            )
    
    async def calculate_tax(
        self,
        request: TaxCalculationRequestDTO,
        hostname: str,
        current_user: str
    ) -> TaxationResponseDTO:
        """
        Calculate tax for an employee.
        
        Args:
            request: Tax calculation request
            hostname: Organisation hostname
            current_user: Current authenticated user
            
        Returns:
            Updated taxation response with calculated tax
        """
        try:
            logger.info(f"Calculating tax for employee: {request.employee_id}")
            
            # Set calculated_by if not provided
            if not request.calculated_by:
                request.calculated_by = current_user
            
            taxation = await self.calculate_tax_use_case.execute(request, hostname)
            
            logger.info(f"Tax calculation completed for {request.employee_id}")
            return taxation
            
        except TaxationNotFoundError as e:
            logger.warning(f"Taxation record not found: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Taxation record not found: {str(e)}"
            )
        except TaxationCalculationError as e:
            logger.warning(f"Tax calculation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tax calculation failed: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error calculating tax: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to calculate tax"
            )
    
    async def calculate_comprehensive_tax(
        self,
        employee_id: str,
        hostname: str,
        current_user: str
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive tax with projections and adjustments.
        
        Args:
            employee_id: Employee identifier
            hostname: Organisation hostname
            current_user: Current authenticated user
            
        Returns:
            Comprehensive tax calculation results
        """
        try:
            logger.info(f"Calculating comprehensive tax for employee: {employee_id}")
            
            results = await self.calculate_tax_use_case.calculate_with_projections(
                employee_id, hostname, current_user
            )
            
            logger.info(f"Comprehensive tax calculation completed for {employee_id}")
            return results
            
        except TaxationNotFoundError as e:
            logger.warning(f"Taxation record not found: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Taxation record not found: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error in comprehensive tax calculation: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to calculate comprehensive tax"
            )
    
    async def get_taxation_by_employee(
        self,
        employee_id: str,
        tax_year: str,
        hostname: str
    ) -> TaxationResponseDTO:
        """
        Get taxation record by employee and tax year.
        
        Args:
            employee_id: Employee identifier
            tax_year: Tax year
            hostname: Organisation hostname
            
        Returns:
            Taxation response
        """
        try:
            taxation = await self.query_repository.get_taxation_by_employee(
                employee_id, tax_year, hostname
            )
            
            if not taxation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Taxation record not found for employee {employee_id} in year {tax_year}"
                )
            
            return taxation
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting taxation record: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve taxation record"
            )
    
    async def get_current_taxation(
        self,
        employee_id: str,
        hostname: str
    ) -> TaxationResponseDTO:
        """
        Get current year taxation record for an employee.
        
        Args:
            employee_id: Employee identifier
            hostname: Organisation hostname
            
        Returns:
            Current taxation response
        """
        try:
            taxation = await self.query_repository.get_current_taxation(
                employee_id, hostname
            )
            
            if not taxation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Current taxation record not found for employee {employee_id}"
                )
            
            return taxation
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting current taxation: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve current taxation record"
            )
    
    async def search_taxation_records(
        self,
        filters: TaxSearchFiltersDTO,
        hostname: str
    ) -> List[TaxationResponseDTO]:
        """
        Search taxation records with filters.
        
        Args:
            filters: Search filters
            hostname: Organisation hostname
            
        Returns:
            List of matching taxation records
        """
        try:
            logger.info("Searching taxation records with filters")
            
            results = await self.query_repository.search_taxation_records(
                filters, hostname
            )
            
            logger.info(f"Found {len(results)} taxation records")
            return results
            
        except Exception as e:
            logger.error(f"Error searching taxation records: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to search taxation records"
            )
    
    async def get_employee_tax_history(
        self,
        employee_id: str,
        hostname: str
    ) -> List[TaxationResponseDTO]:
        """
        Get tax history for an employee across all years.
        
        Args:
            employee_id: Employee identifier
            hostname: Organisation hostname
            
        Returns:
            List of taxation records for the employee
        """
        try:
            history = await self.query_repository.get_employee_tax_history(
                employee_id, hostname
            )
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting tax history: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve tax history"
            )
    
    async def update_taxation(
        self,
        employee_id: str,
        request: TaxationUpdateRequestDTO,
        hostname: str,
        current_user: str
    ) -> TaxationResponseDTO:
        """
        Update an existing taxation record.
        
        Args:
            employee_id: Employee identifier
            request: Taxation update request
            hostname: Organisation hostname
            current_user: Current authenticated user
            
        Returns:
            Updated taxation response
        """
        try:
            logger.info(f"Updating taxation record for employee: {employee_id}")
            
            # Set updated_by if not provided
            if not request.updated_by:
                request.updated_by = current_user
            
            taxation = await self.command_repository.update_taxation(
                employee_id, request, hostname
            )
            
            logger.info(f"Taxation record updated successfully: {employee_id}")
            return taxation
            
        except Exception as e:
            logger.error(f"Error updating taxation record: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update taxation record"
            )
    
    async def delete_taxation(
        self,
        employee_id: str,
        tax_year: str,
        hostname: str,
        current_user: str
    ) -> Dict[str, Any]:
        """
        Delete a taxation record.
        
        Args:
            employee_id: Employee identifier
            tax_year: Tax year
            hostname: Organisation hostname
            current_user: Current authenticated user
            
        Returns:
            Deletion status
        """
        try:
            logger.info(f"Deleting taxation record for employee: {employee_id}, year: {tax_year}")
            
            success = await self.command_repository.delete_taxation(
                employee_id, tax_year, hostname
            )
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Taxation record not found or could not be deleted"
                )
            
            logger.info(f"Taxation record deleted successfully: {employee_id}")
            return {"message": "Taxation record deleted successfully", "deleted": True}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting taxation record: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete taxation record"
            )
    
    async def get_tax_statistics(
        self,
        tax_year: str,
        hostname: str,
        department: Optional[str] = None
    ) -> TaxStatisticsDTO:
        """
        Get tax statistics for a tax year.
        
        Args:
            tax_year: Tax year
            hostname: Organisation hostname
            department: Optional department filter
            
        Returns:
            Tax statistics
        """
        try:
            logger.info(f"Getting tax statistics for year: {tax_year}")
            
            statistics = await self.analytics_repository.get_tax_statistics(
                tax_year, hostname, department
            )
            
            return statistics
            
        except Exception as e:
            logger.error(f"Error getting tax statistics: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve tax statistics"
            )
    
    async def get_regime_adoption_stats(
        self,
        tax_year: str,
        hostname: str
    ) -> Dict[str, Any]:
        """
        Get tax regime adoption statistics.
        
        Args:
            tax_year: Tax year
            hostname: Organisation hostname
            
        Returns:
            Regime adoption statistics
        """
        try:
            stats = await self.analytics_repository.get_regime_adoption_stats(
                tax_year, hostname
            )
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting regime adoption stats: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve regime adoption statistics"
            )
    
    async def get_top_taxpayers(
        self,
        tax_year: str,
        hostname: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get top taxpayers for a tax year.
        
        Args:
            tax_year: Tax year
            hostname: Organisation hostname
            limit: Number of top taxpayers to return
            
        Returns:
            List of top taxpayers
        """
        try:
            top_taxpayers = await self.analytics_repository.get_top_taxpayers(
                tax_year, hostname, limit
            )
            
            return top_taxpayers
            
        except Exception as e:
            logger.error(f"Error getting top taxpayers: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve top taxpayers"
            )
    
    async def get_department_tax_summary(
        self,
        tax_year: str,
        hostname: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get department-wise tax summary.
        
        Args:
            tax_year: Tax year
            hostname: Organisation hostname
            
        Returns:
            Department-wise tax summary
        """
        try:
            summary = await self.analytics_repository.get_department_tax_summary(
                tax_year, hostname
            )
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting department tax summary: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve department tax summary"
            )
    
    async def update_filing_status(
        self,
        employee_id: str,
        tax_year: str,
        filing_status: str,
        hostname: str,
        current_user: str
    ) -> Dict[str, Any]:
        """
        Update taxation filing status.
        
        Args:
            employee_id: Employee identifier
            tax_year: Tax year
            filing_status: New filing status
            hostname: Organisation hostname
            current_user: Current authenticated user
            
        Returns:
            Update status
        """
        try:
            logger.info(f"Updating filing status for employee: {employee_id}")
            
            success = await self.command_repository.update_filing_status(
                employee_id, tax_year, filing_status, hostname, current_user
            )
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Taxation record not found or could not be updated"
                )
            
            return {
                "message": "Filing status updated successfully",
                "employee_id": employee_id,
                "filing_status": filing_status
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating filing status: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update filing status"
            ) 