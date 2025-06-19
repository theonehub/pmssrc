"""
Get Monthly Salary Use Case
Use case for retrieving monthly salary data with fallback to taxation projections
"""

import logging
from typing import Optional, TYPE_CHECKING
from app.application.dto.monthly_salary_dto import MonthlySalaryResponseDTO
from app.application.interfaces.repositories.monthly_salary_repository import MonthlySalaryRepository
from app.application.interfaces.repositories.user_repository import UserRepository
from app.application.interfaces.repositories.taxation_repository import TaxationRepository
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.services.taxation.tax_calculation_service import TaxCalculationService

if TYPE_CHECKING:
    from app.auth.auth_dependencies import CurrentUser

logger = logging.getLogger(__name__)


class GetMonthlySalaryUseCase:
    """Use case for getting monthly salary with fallback logic."""
    
    def __init__(
        self,
        monthly_salary_repository: MonthlySalaryRepository,
        user_repository: UserRepository,
        taxation_repository: TaxationRepository,
        tax_calculation_service: TaxCalculationService
    ):
        """
        Initialize use case with dependencies.
        
        Args:
            monthly_salary_repository: Monthly salary repository
            user_repository: User repository
            taxation_repository: Taxation repository
            tax_calculation_service: Tax calculation service
        """
        self.monthly_salary_repository = monthly_salary_repository
        self.user_repository = user_repository
        self.taxation_repository = taxation_repository
        self.tax_calculation_service = tax_calculation_service
    
    async def execute(
        self,
        employee_id: str,
        month: int,
        year: int,
        current_user: "CurrentUser"
    ) -> Optional[MonthlySalaryResponseDTO]:
        """
        Execute the use case to get monthly salary.
        
        Implementation follows the specified data flow sequence:
        1. Fetch employee details from user_service_impl
        2. Get monthly salary info from "monthly_salary" MongoDB collection
        3. If no monthly salary data exists, fallback to taxation_records
        4. Return pre-calculated monthly_salary as PayoutMonthlyProjection with "not yet computed" status
        
        Args:
            employee_id: Employee ID
            month: Month (1-12)
            year: Year
            current_user: Current user for organization context
            
        Returns:
            Optional[MonthlySalaryResponseDTO]: Monthly salary data or None
        """
        try:
            employee_id_obj = EmployeeId(employee_id)
            hostname = current_user.hostname
            
            logger.info(f"Getting monthly salary for employee {employee_id}, month {month}/{year}")
            
            # Step 1: Get employee details from user repository
            user = await self.user_repository.get_by_id(employee_id_obj, hostname)
            if not user:
                logger.warning(f"Employee not found: {employee_id}")
                return None
            
            # Step 2: Try to get monthly salary from monthly_salary collection
            monthly_salary = await self.monthly_salary_repository.get_by_employee_month_year(
                employee_id_obj, month, year, hostname
            )
            
            if monthly_salary:
                logger.info(f"Found existing monthly salary for {employee_id}")
                return self._convert_entity_to_dto(monthly_salary, user)
            
            # Step 3: Fallback to taxation records if no monthly salary exists
            logger.info(f"No monthly salary found, falling back to taxation projection for {employee_id}")
            
            # Determine tax year from month/year
            tax_year = self._get_tax_year(month, year)
            
            # Get taxation record
            taxation_record = await self.taxation_repository.get_by_employee_and_tax_year(
                employee_id_obj, tax_year, hostname
            )
            
            if not taxation_record:
                logger.warning(f"No taxation record found for employee {employee_id}, tax year {tax_year}")
                return None
            
            # Step 4: Create monthly projection from taxation record
            try:
                # Calculate tax if not already calculated
                if not taxation_record.calculation_result:
                    calculation_result = await self.tax_calculation_service.calculate_comprehensive_tax(taxation_record)
                    taxation_record.update_calculation_result(calculation_result)
                else:
                    calculation_result = taxation_record.calculation_result
                
                # Create monthly payout projection
                monthly_projection = self.tax_calculation_service._create_monthly_payout_from_taxation_record(
                    taxation_record, calculation_result
                )
                
                # Create MonthlySalary entity from projection with "not yet computed" status
                from app.domain.entities.monthly_salary import MonthlySalary
                projected_monthly_salary = MonthlySalary.from_taxation_projection(
                    employee_id=employee_id_obj,
                    month=month,
                    year=year,
                    tax_year=tax_year,
                    organization_id=current_user.organization_id,
                    monthly_projection=monthly_projection,
                    created_by=current_user.employee_id
                )
                
                logger.info(f"Created monthly salary projection for {employee_id}")
                return self._convert_entity_to_dto(projected_monthly_salary, user)
                
            except Exception as e:
                logger.error(f"Error creating monthly projection for {employee_id}: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Error in GetMonthlySalaryUseCase for {employee_id}: {e}")
            raise
    
    def _convert_entity_to_dto(self, monthly_salary, user) -> MonthlySalaryResponseDTO:
        """Convert monthly salary entity to DTO with employee details."""
        return MonthlySalaryResponseDTO(
            employee_id=str(monthly_salary.employee_id),
            month=monthly_salary.month,
            year=monthly_salary.year,
            tax_year=monthly_salary.tax_year,
            
            # Employee info
            employee_name=user.name,
            employee_email=user.email,
            department=user.department,
            designation=user.designation,
            
            # Salary components
            basic_salary=monthly_salary.basic_salary.to_float(),
            da=monthly_salary.da.to_float(),
            hra=monthly_salary.hra.to_float(),
            special_allowance=monthly_salary.special_allowance.to_float(),
            transport_allowance=monthly_salary.transport_allowance.to_float(),
            medical_allowance=monthly_salary.medical_allowance.to_float(),
            bonus=monthly_salary.bonus.to_float(),
            commission=monthly_salary.commission.to_float(),
            other_allowances=monthly_salary.other_allowances.to_float(),
            
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
    
    def _get_tax_year(self, month: int, year: int) -> str:
        """
        Determine tax year from month and year.
        Indian tax year runs from April to March.
        
        Args:
            month: Month (1-12)
            year: Year
            
        Returns:
            str: Tax year in format 'YYYY-YY'
        """
        if month >= 4:  # April onwards
            return f"{year}-{str(year + 1)[2:]}"
        else:  # January to March
            return f"{year - 1}-{str(year)[2:]}" 