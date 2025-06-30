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
from app.auth.auth_dependencies import CurrentUser
from app.application.interfaces.repositories.salary_package_repository import SalaryPackageRepository


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
        salary_package_repository: SalaryPackageRepository
    ):
        self._user_query_service = user_query_service
        self._salary_package_repository = salary_package_repository
    
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
        tax_year: str,
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
            joining_date=user_summary.date_of_joining,  # Now available in UserSummaryDTO
            current_salary=None  # UserSummaryDTO doesn't have salary info
        )
        
        # Try to get tax record information
        try:
            # Get the tax record for the specific year
            tax_record = await self._salary_package_repository.get_salary_package(
                user_summary.employee_id, 
                tax_year, 
                organization_id
            )
            
            
            if tax_record:
                employee_dto.has_tax_record = True
                employee_dto.tax_year = str(tax_record.tax_year)  # Convert TaxYear value object to string
                employee_dto.filing_status = getattr(tax_record, 'filing_status', None)
                employee_dto.regime = str(tax_record.regime) if hasattr(tax_record, 'regime') and tax_record.regime else None  # Convert TaxRegime value object to string
                employee_dto.last_updated = tax_record.updated_at.isoformat() if hasattr(tax_record, 'updated_at') and tax_record.updated_at else None
                
                # Extract total tax liability from calculation result
                total_tax = None
                
                if hasattr(tax_record, 'calculation_result') and tax_record.calculation_result:
                    calc_result = tax_record.calculation_result
                    
                    # Handle TaxCalculationResult object
                    if hasattr(calc_result, 'tax_liability'):
                        if hasattr(calc_result.tax_liability, 'to_float'):
                            total_tax = calc_result.tax_liability.to_float()
                        else:
                            total_tax = float(calc_result.tax_liability)
                    elif hasattr(calc_result, 'total_tax_liability'):
                        if hasattr(calc_result.total_tax_liability, 'to_float'):
                            total_tax = calc_result.total_tax_liability.to_float()
                        else:
                            total_tax = float(calc_result.total_tax_liability)
                    
                    # Fallback: Handle as dictionary (in case deserialization didn't work)
                    elif isinstance(calc_result, dict):
                        total_tax = calc_result.get('tax_liability') or calc_result.get('total_tax_liability')
                        
                        # Try tax_breakdown if direct fields not available
                        if not total_tax and 'tax_breakdown' in calc_result:
                            breakdown = calc_result['tax_breakdown']
                            if isinstance(breakdown, dict):
                                if 'tax_calculation' in breakdown:
                                    total_tax = breakdown['tax_calculation'].get('total_tax_liability')
                                elif 'total_tax_liability' in breakdown:
                                    total_tax = breakdown['total_tax_liability']
                
                # Set the total tax if found
                if total_tax is not None:
                    employee_dto.total_tax = float(total_tax)
            
        except Exception:
            # If tax record not found or error occurs, leave defaults
            pass
        
        return employee_dto 