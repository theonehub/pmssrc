"""
Get Monthly Salaries for Period Use Case
Use case for retrieving all monthly salaries for a specific month/year
"""

import logging
from typing import Optional, List, TYPE_CHECKING
from app.application.dto.monthly_salary_dto import (
    MonthlySalaryListResponseDTO, 
    MonthlySalaryResponseDTO,
    MonthlySalaryFilterDTO
)
from app.application.interfaces.repositories.monthly_salary_repository import MonthlySalaryRepository
from app.application.interfaces.repositories.user_repository import UserRepository
from app.domain.value_objects.employee_id import EmployeeId

if TYPE_CHECKING:
    from app.auth.auth_dependencies import CurrentUser

logger = logging.getLogger(__name__)


class GetMonthlySalariesForPeriodUseCase:
    """Use case for getting all monthly salaries for a period."""
    
    def __init__(
        self,
        monthly_salary_repository: MonthlySalaryRepository,
        user_repository: UserRepository
    ):
        """
        Initialize use case with dependencies.
        
        Args:
            monthly_salary_repository: Monthly salary repository
            user_repository: User repository for employee details
        """
        self.monthly_salary_repository = monthly_salary_repository
        self.user_repository = user_repository
    
    async def execute(
        self,
        month: int,
        year: int,
        current_user: "CurrentUser",
        filters: Optional[MonthlySalaryFilterDTO] = None
    ) -> MonthlySalaryListResponseDTO:
        """
        Execute the use case to get monthly salaries for a period.
        
        Args:
            month: Month (1-12)
            year: Year
            current_user: Current user for organization context
            filters: Optional filters for the query
            
        Returns:
            MonthlySalaryListResponseDTO: List of monthly salaries
        """
        try:
            hostname = current_user.hostname
            
            logger.info(f"Getting monthly salaries for period {month}/{year}")
            
            # Get monthly salaries from repository
            monthly_salaries = await self.monthly_salary_repository.get_by_month_year(
                month, year, hostname, filters
            )
            
            # Get total count for pagination
            total_count = await self.monthly_salary_repository.count_by_filters(
                filters or MonthlySalaryFilterDTO(month=month, year=year),
                hostname
            )
            
            # Convert entities to DTOs with employee details
            salary_dtos = []
            for monthly_salary in monthly_salaries:
                try:
                    # Get employee details
                    user = await self.user_repository.get_by_id(
                        monthly_salary.employee_id, hostname
                    )
                    
                    # Convert to DTO
                    dto = self._convert_entity_to_dto(monthly_salary, user)
                    salary_dtos.append(dto)
                    
                except Exception as e:
                    logger.error(f"Error converting monthly salary for {monthly_salary.employee_id}: {e}")
                    # Continue with other records
                    continue
            
            # Prepare pagination info
            skip = filters.skip if filters else 0
            limit = filters.limit if filters else 50
            has_more = (skip + len(salary_dtos)) < total_count
            
            logger.info(f"Found {len(salary_dtos)} monthly salaries for period {month}/{year}")
            
            return MonthlySalaryListResponseDTO(
                items=salary_dtos,
                total=total_count,
                skip=skip,
                limit=limit,
                has_more=has_more
            )
            
        except Exception as e:
            logger.error(f"Error in GetMonthlySalariesForPeriodUseCase for {month}/{year}: {e}")
            raise
    
    def _convert_entity_to_dto(self, monthly_salary, user) -> MonthlySalaryResponseDTO:
        """Convert monthly salary entity to DTO with employee details."""
        return MonthlySalaryResponseDTO(
            employee_id=str(monthly_salary.employee_id),
            month=monthly_salary.month,
            year=monthly_salary.year,
            tax_year=monthly_salary.tax_year,
            
            # Employee info
            employee_name=user.name if user else "Unknown",
            employee_email=user.email if user else None,
            department=user.department if user else None,
            designation=user.designation if user else None,
            
            # Salary components
            basic_salary=monthly_salary.basic_salary.to_float(),
            da=monthly_salary.da.to_float(),
            hra=monthly_salary.hra.to_float(),
            special_allowance=monthly_salary.special_allowance.to_float(),
            bonus=monthly_salary.bonus.to_float(),
            commission=monthly_salary.commission.to_float(),
            
            # Deductions
            epf_employee=monthly_salary.epf_employee.to_float(),
            esi_employee=monthly_salary.esi_employee.to_float(),
            professional_tax=monthly_salary.professional_tax.to_float(),
            tds=monthly_salary.tds.to_float(),
            advance_deduction=monthly_salary.advance_deduction.to_float(),
            loan_deduction=monthly_salary.loan_deduction.to_float(),
            other_deductions=monthly_salary.other_deductions.to_float(),
            
            # Calculated totals
            gross_salary=monthly_salary.gross_salary.to_float(),
            total_deductions=monthly_salary.total_deductions.to_float(),
            net_salary=monthly_salary.net_salary.to_float(),
            
            # Annual projections
            annual_gross_salary=monthly_salary.annual_gross_salary.to_float(),
            annual_tax_liability=monthly_salary.annual_tax_liability.to_float(),
            
            # Tax details
            tax_regime=monthly_salary.tax_regime,
            tax_exemptions=monthly_salary.tax_exemptions.to_float(),
            standard_deduction=monthly_salary.standard_deduction.to_float(),
            
            # Working days
            total_days_in_month=monthly_salary.total_days_in_month,
            working_days_in_period=monthly_salary.working_days_in_period,
            lwp_days=monthly_salary.lwp_days,
            effective_working_days=monthly_salary.effective_working_days,
            
            # Processing details
            status=monthly_salary.status.value,
            computation_date=monthly_salary.computation_date,
            notes=monthly_salary.notes,
            remarks=monthly_salary.remarks,
            
            # Audit fields
            created_at=monthly_salary.created_at,
            updated_at=monthly_salary.updated_at,
            created_by=monthly_salary.created_by,
            updated_by=monthly_salary.updated_by
        ) 