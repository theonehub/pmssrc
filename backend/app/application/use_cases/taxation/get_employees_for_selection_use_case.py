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
            current_user: Current authenticated user with organisation context
            
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
                user_summary, query.tax_year, current_user
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
        current_user: CurrentUser
    ) -> EmployeeSelectionDTO:
        """
        Enrich employee data with tax record information.
        
        Args:
            user_summary: User summary from user service
            tax_year: Optional tax year filter
            current_user: Current user context
            
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
            tax_record = await self._salary_package_repository.get_salary_package_record(
                user_summary.employee_id, 
                tax_year, 
                current_user.hostname
            )
            
            if tax_record:
                employee_dto.has_tax_record = True
                employee_dto.tax_year = str(tax_record.tax_year)  # Convert TaxYear value object to string
                employee_dto.filing_status = getattr(tax_record, 'filing_status', None)
                
                # Extract regime from TaxRegime value object
                if hasattr(tax_record, 'regime') and tax_record.regime:
                    if hasattr(tax_record.regime, 'regime_type'):
                        employee_dto.regime = tax_record.regime.regime_type.value
                    else:
                        employee_dto.regime = str(tax_record.regime)
                else:
                    employee_dto.regime = None
                
                employee_dto.last_updated = tax_record.updated_at.isoformat() if hasattr(tax_record, 'updated_at') and tax_record.updated_at else None
                
                # Extract total tax liability from calculation result
                if hasattr(tax_record, 'calculation_result') and tax_record.calculation_result:
                    calc_result = tax_record.calculation_result
                    
                    # Debug logging
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.debug(f"Employee {user_summary.employee_id}: Found calculation result")
                    logger.debug(f"Employee {user_summary.employee_id}: calc_result type: {type(calc_result)}")
                    logger.debug(f"Employee {user_summary.employee_id}: calc_result attributes: {dir(calc_result)}")
                    
                    # TaxCalculationResult has tax_liability property
                    if hasattr(calc_result, 'tax_liability') and calc_result.tax_liability:
                        if hasattr(calc_result.tax_liability, 'to_float'):
                            employee_dto.total_tax = calc_result.tax_liability.to_float()
                            logger.debug(f"Employee {user_summary.employee_id}: Set total_tax from tax_liability: {employee_dto.total_tax}")
                        else:
                            employee_dto.total_tax = float(calc_result.tax_liability)
                            logger.debug(f"Employee {user_summary.employee_id}: Set total_tax from tax_liability (float): {employee_dto.total_tax}")
                    
                    # Fallback to total_tax_liability property
                    elif hasattr(calc_result, 'total_tax_liability') and calc_result.total_tax_liability:
                        if hasattr(calc_result.total_tax_liability, 'to_float'):
                            employee_dto.total_tax = calc_result.total_tax_liability.to_float()
                            logger.debug(f"Employee {user_summary.employee_id}: Set total_tax from total_tax_liability: {employee_dto.total_tax}")
                        else:
                            employee_dto.total_tax = float(calc_result.total_tax_liability)
                            logger.debug(f"Employee {user_summary.employee_id}: Set total_tax from total_tax_liability (float): {employee_dto.total_tax}")
                    else:
                        logger.debug(f"Employee {user_summary.employee_id}: No tax liability found in calculation result")
                else:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.debug(f"Employee {user_summary.employee_id}: No calculation result found")
            else:
                # No tax record exists - create a default one for display purposes
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Employee {user_summary.employee_id}: No tax record found for {tax_year}, creating default display data")
                
                # Set default values for display
                employee_dto.has_tax_record = False  # No actual record exists
                employee_dto.tax_year = tax_year
                employee_dto.filing_status = 'pending'
                employee_dto.regime = 'new'  # Default to new regime
                employee_dto.total_tax = 0.0  # Default to zero tax
                employee_dto.last_updated = None
            
        except Exception as e:
            # Log the error for debugging but don't fail the entire request
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error enriching tax info for employee {user_summary.employee_id}: {str(e)}")
            
            # Set default values in case of error
            employee_dto.has_tax_record = False
            employee_dto.tax_year = tax_year
            employee_dto.filing_status = 'pending'
            employee_dto.regime = 'new'
            employee_dto.total_tax = 0.0
            employee_dto.last_updated = None
        
        return employee_dto 