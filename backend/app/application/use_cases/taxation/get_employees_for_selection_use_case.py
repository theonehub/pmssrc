"""
Use case for getting employees for taxation selection.
Reuses the user service to fetch employee data and enriches it with tax information.
"""

from typing import Optional
from datetime import datetime

from app.application.dto.taxation_dto import (
    EmployeeSelectionQuery,
    EmployeeSelectionResponse,
    EmployeeSelectionDTO
)
from app.application.dto.user_dto import UserSearchFiltersDTO
from app.application.interfaces.services.user_service import UserQueryService
from app.domain.repositories.taxation_repository import TaxationRepository
from app.auth.auth_dependencies import CurrentUser


class GetEmployeesForSelectionUseCase:
    """
    Use case for retrieving employees for taxation selection.
    
    This use case:
    1. Fetches employees using the user service
    2. Enriches employee data with tax record information
    3. Formats the response for frontend consumption
    """
    
    def __init__(
        self,
        user_query_service: UserQueryService,
        taxation_repository: TaxationRepository
    ):
        self._user_query_service = user_query_service
        self._taxation_repository = taxation_repository
    
    async def execute(
        self,
        query: EmployeeSelectionQuery,
        current_user: CurrentUser
    ) -> EmployeeSelectionResponse:
        """
        Execute the use case to get employees for selection.
        
        Args:
            query: Query parameters for filtering and pagination
            current_user: Current authenticated user with organization context
            
        Returns:
            Employee selection response with enriched data
        """
        
        # Convert taxation query to user search filters
        # Calculate page number from skip/limit
        page = (query.skip // query.limit) + 1 if query.limit > 0 else 1
        
        user_filters = UserSearchFiltersDTO(
            page=page,
            page_size=query.limit,
            name=query.search,  # UserSearchFiltersDTO uses 'name' for search
            department=query.department,
            role=query.role,
            status=query.status or "active",  # Default to active employees
            is_active=query.status != "inactive" if query.status else True
        )
        
        # Get employees from user service
        user_list_response = await self._user_query_service.search_users(
            user_filters, current_user
        )
        
        employees = []
        
        # Enrich each employee with tax information
        for user_summary in user_list_response.users:
            employee_dto = await self._enrich_employee_with_tax_info(
                user_summary, query.tax_year, current_user.hostname
            )
            
            # Apply tax-specific filtering if needed
            if query.has_tax_record is not None:
                if query.has_tax_record != employee_dto.has_tax_record:
                    continue
            
            employees.append(employee_dto)
        
        # Calculate pagination info
        total = user_list_response.total_count  # Use total_count field from UserListResponseDTO
        has_more = (query.skip + query.limit) < total
        
        return EmployeeSelectionResponse(
            total=total,
            employees=employees,
            skip=query.skip,
            limit=query.limit,
            has_more=has_more
        )
    
    async def _enrich_employee_with_tax_info(
        self,
        user_summary,
        tax_year: Optional[str],
        organization_id: str
    ) -> EmployeeSelectionDTO:
        """
        Enrich employee data with tax record information.
        
        Args:
            user_summary: User summary from user service
            tax_year: Optional tax year filter
            organization_id: Organization ID for context
            
        Returns:
            Enriched employee DTO with tax information
        """
        
        # Basic employee information from user service
        employee_dto = EmployeeSelectionDTO(
            employee_id=user_summary.employee_id,
            user_name=user_summary.name,  # UserSummaryDTO has 'name' field
            email=user_summary.email,
            department=user_summary.department,
            role=user_summary.role,
            status=user_summary.status,
            joining_date=None,  # UserSummaryDTO doesn't have joining_date, will need to get from entity if needed
            current_salary=None  # UserSummaryDTO doesn't have salary info
        )
        
        # Try to get tax record information
        try:
            # Get the most recent tax record or for specific year
            if tax_year:
                # Convert tax year string (e.g., "2023-24") to financial year integer (e.g., 2023)
                financial_year = int(tax_year.split('-')[0])
                tax_record = await self._taxation_repository.get_taxation_record(
                    user_summary.employee_id, 
                    financial_year
                )
            else:
                # Get most recent records and take the latest one
                records = await self._taxation_repository.get_taxation_records(
                    user_summary.employee_id
                )
                tax_record = records[0] if records else None
            
            if tax_record:
                employee_dto.has_tax_record = True
                employee_dto.tax_year = f"{tax_record.financial_year}-{str(tax_record.financial_year + 1)[2:]}"  # Convert back to "2023-24" format
                employee_dto.filing_status = getattr(tax_record, 'filing_status', None)
                employee_dto.regime = getattr(tax_record, 'regime', None)
                employee_dto.last_updated = tax_record.updated_at.isoformat() if hasattr(tax_record, 'updated_at') and tax_record.updated_at else None
                
                # Calculate total tax if tax calculation is available
                if hasattr(tax_record, 'tax_calculation') and tax_record.tax_calculation:
                    employee_dto.total_tax = tax_record.tax_calculation.get('total_tax_liability', 0)
                elif hasattr(tax_record, 'total_tax_liability'):
                    employee_dto.total_tax = tax_record.total_tax_liability
                
        except Exception:
            # If tax record not found or error occurs, leave defaults
            pass
        
        return employee_dto 