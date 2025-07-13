from typing import Dict, Any, Optional
from datetime import datetime, date
from decimal import Decimal
import logging

from app.application.dto.taxation_dto import MonthlySalaryComputeRequestDTO, MonthlySalaryResponseDTO
from app.application.interfaces.repositories.salary_package_repository import SalaryPackageRepository
from app.application.interfaces.repositories.user_repository import UserQueryRepository
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.tax_year import TaxYear
from app.domain.value_objects.money import Money
from app.domain.entities.monthly_salary import MonthlySalary
from app.domain.entities.taxation.taxation_record import TDSStatus
from app.domain.entities.taxation.salary_income import SalaryIncome
from app.domain.entities.taxation.perquisites import MonthlyPerquisitesPayouts
from app.domain.entities.taxation.deductions import TaxDeductions
from app.domain.entities.taxation.retirement_benefits import RetirementBenefits
from app.domain.entities.taxation.lwp_details import LWPDetails
from app.domain.value_objects.tax_regime import TaxRegime
from app.domain.services.taxation.tax_calculation_service import TaxCalculationService

logger = logging.getLogger(__name__)

class ComputeMonthlySalaryUseCase:
    """
    Use case for computing monthly salary for an employee.
    
    This use case:
    1. Retrieves the employee's salary package record
    2. Creates a MonthlySalary entity with current month's data
    3. Computes monthly salary components including deductions
    4. Calculates tax liability for the month
    5. Saves the computed monthly salary to the database
    6. Returns the computed monthly salary details
    """
    
    def __init__(
        self,
        salary_package_repository: SalaryPackageRepository,
        user_repository: UserQueryRepository,
        tax_calculation_service: TaxCalculationService
    ):
        self.salary_package_repository = salary_package_repository
        self.user_repository = user_repository
        self.tax_calculation_service = tax_calculation_service
    
    async def execute(
        self, 
        request: MonthlySalaryComputeRequestDTO,
        organization_id: str
    ) -> MonthlySalaryResponseDTO:
        """
        Execute monthly salary computation for an employee.
        
        Args:
            request: Monthly salary computation request
            organization_id: Organization ID for multi-tenancy
            
        Returns:
            MonthlySalaryResponseDTO: Computed monthly salary details
            
        Raises:
            ValueError: If employee or salary package not found
            RuntimeError: If computation fails
        """
        logger.debug(f"Starting monthly salary computation for employee {request.employee_id}")
        logger.debug(f"Month: {request.month}, Tax Year: {request.tax_year}")
        
        try:
            # 1. Get employee details
            employee_id = EmployeeId(request.employee_id)
            user = await self.user_repository.get_by_id(employee_id, organization_id)
            
            if not user:
                raise ValueError(f"Employee {request.employee_id} not found")
            
            # 2. Get salary package record
            tax_year = TaxYear.from_string(request.tax_year)
            salary_package_record = await self.salary_package_repository.get_salary_package_record(
                request.employee_id, str(tax_year), organization_id
            )
            
            if not salary_package_record:
                raise ValueError(
                    f"Salary package record not found for employee {request.employee_id} "
                    f"in tax year {request.tax_year}"
                )
            financial_year_month = self._convert_to_financial_year_month(request.month, tax_year)
            
            # 3. Update arrears if provided
            if request.arrears is not None and request.arrears > 0:
                arrears_amount = Money.from_float(request.arrears)
                salary_package_record.set_arrears_for_month(financial_year_month, arrears_amount)
                logger.info(f"Updated arrears for month {financial_year_month}: ₹{request.arrears:,.2f}")

                
            if request.bonus is not None and request.bonus > 0:
                bonus_amount = Money.from_float(request.bonus)
                salary_package_record.set_bonus_for_month(financial_year_month, bonus_amount)
                logger.info(f"Updated bonus for month {financial_year_month}: ₹{request.bonus:,.2f}")

                
            # Save the updated salary package record
            await self.salary_package_repository.save(salary_package_record, organization_id)
            
            # 4. Get current salary income (latest one)
            current_salary_income = salary_package_record.get_latest_salary_income()
            if not current_salary_income:
                raise ValueError(f"No salary income found for employee {request.employee_id}")
            
            # 5. Create monthly salary components
            monthly_salary_components = await self._create_monthly_salary_components(
                current_salary_income, salary_package_record, request, organization_id
            )
            
            # 6. Calculate monthly tax
            monthly_tax = await self._calculate_monthly_tax(
                salary_package_record, request, organization_id
            )

            

            # 7. Create MonthlySalary entity
            monthly_salary = MonthlySalary(
                employee_id=employee_id,
                month=request.month,
                year=tax_year.get_start_date().year, # Use the start year of the tax year
                salary=monthly_salary_components['salary'],
                perquisites_payouts=monthly_salary_components['perquisites_payouts'],
                deductions=monthly_salary_components['deductions'],
                retirement=monthly_salary_components['retirement'],
                lwp=monthly_salary_components['lwp'],
                tax_year=tax_year,
                tax_regime=salary_package_record.regime,
                tax_amount=monthly_tax,
                net_salary=Money.zero()  # Will be computed below
            )


            
            # 8. Compute net salary
            monthly_salary.compute_net_pay()
            
            # 9. Build response DTO
            response = self._build_response_dto(
                monthly_salary, user, request, organization_id
            )

            salary_package_record.monthly_salary_records.append(monthly_salary)
            await self.salary_package_repository.save(salary_package_record, organization_id)
            
            
            logger.info(f"Successfully computed monthly salary for employee {request.employee_id}")
            logger.info(f"Gross: ₹{response.gross_salary:,.2f}, Net: ₹{response.net_salary:,.2f}")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to compute monthly salary for employee {request.employee_id}: {str(e)}")
            raise
    
    async def _create_monthly_salary_components(
        self, 
        salary_income: SalaryIncome, 
        salary_package_record, 
        request: MonthlySalaryComputeRequestDTO,
        organization_id: str
    ) -> Dict[str, Any]:
        """
        Create monthly salary components from annual salary income.
        
        Args:
            salary_income: Annual salary income
            salary_package_record: Employee's salary package record
            request: Computation request
            organization_id: Organization ID for multi-tenancy
            
        Returns:
            Dict containing monthly salary components
        """
        # Use monthly components directly (salary_income already contains monthly values)
        monthly_basic = salary_income.basic_salary
        monthly_da = salary_income.dearness_allowance
        monthly_hra = salary_income.hra_provided
        monthly_special = salary_income.special_allowance
        monthly_bonus = salary_income.bonus
        monthly_commission = salary_income.commission
        
        # Get arrears and bonus from salary package record for the specific month
        financial_year_month = self._convert_to_financial_year_month(request.month, salary_package_record.tax_year)
        monthly_arrears = salary_package_record.get_arrears_per_month(financial_year_month)
        monthly_bonus = salary_package_record.get_bonus_per_month(financial_year_month)
        
        # Create monthly salary income
        monthly_salary_income = SalaryIncome(
            basic_salary=monthly_basic,
            dearness_allowance=monthly_da,
            hra_provided=monthly_hra,
            special_allowance=monthly_special,
            bonus=monthly_bonus,
            commission=monthly_commission,
            arrears=monthly_arrears,
            specific_allowances=salary_income.specific_allowances,  # Salary_income and its components are monthly
            effective_from=datetime(salary_package_record.tax_year.get_start_date().year, request.month, 1),
            effective_till=datetime(salary_package_record.tax_year.get_start_date().year, request.month, 1)
        )
        
        # Create other components (simplified for monthly)
        perq_components = salary_package_record.perquisites.get_perquisites_components()
        perq_total = sum([c.value for c in perq_components], start=Money.zero())
        monthly_perquisites_payouts = MonthlyPerquisitesPayouts(components=perq_components, total=perq_total)
        monthly_deductions = TaxDeductions()  # Will be calculated
        monthly_retirement = RetirementBenefits()  # Empty for now
        
        # Calculate LWP details for the month
        monthly_lwp = await self._calculate_lwp_days(request.employee_id, request.month, salary_package_record.tax_year.get_start_date().year, organization_id)
        
        return {
            'salary': monthly_salary_income,
            'perquisites_payouts': monthly_perquisites_payouts,
            'deductions': monthly_deductions,
            'retirement': monthly_retirement,
            'lwp': monthly_lwp
        }
    
    async def _calculate_lwp_days(
        self,
        employee_id: str,
        month: int,
        year: int,
        organization_id: str
    ) -> LWPDetails:
        """
        Calculate Leave Without Pay (LWP) days for the specified month.
        
        Args:
            employee_id: Employee identifier
            month: Month (1-12)
            year: Year
            organization_id: Organization identifier
            
        Returns:
            LWPDetails: LWP details for the month
        """
        try:
            logger.info(f"Calculating LWP for employee {employee_id} in {month}/{year}")
            
            # Get LWP calculation service from dependency container
            from app.config.dependency_container import get_dependency_container
            container = get_dependency_container()
            lwp_service = container.get_lwp_calculation_service()
            
            if not lwp_service:
                logger.warning("LWP calculation service not available, using default LWP details")
                return LWPDetails(
                    lwp_days=0,
                    total_working_days=26,  # Default working days
                    month=month,
                    year=year
                )
            
            # Calculate LWP using standardized service
            lwp_result = await lwp_service.calculate_lwp_for_month(
                employee_id, month, year, organization_id
            )
            
            # Create LWPDetails entity
            lwp_details = LWPDetails(
                lwp_days=lwp_result.lwp_days,
                total_working_days=lwp_result.working_days,
                month=month,
                year=year
            )
            
            logger.info(f"LWP calculation completed: {lwp_result.lwp_days} LWP days out of {lwp_result.working_days} working days")
            return lwp_details
            
        except Exception as e:
            logger.error(f"Error calculating LWP for employee {employee_id}: {e}")
            # Return default LWP details on error
            return LWPDetails(
                lwp_days=0,
                total_working_days=26,  # Default working days
                month=month,
                year=year
            )
    
    async def _calculate_monthly_tax(
        self, 
        salary_package_record, 
        request: MonthlySalaryComputeRequestDTO,
        organization_id: str
    ) -> Money:
        """
        Calculate monthly tax liability.
        
        Args:
            salary_package_record: Employee's salary package record
            request: Computation request
            organization_id: Organization ID
            
        Returns:
            Money: Monthly tax amount
        """
        try:
            # Use existing tax calculation service
            tax_result = await self.tax_calculation_service.compute_monthly_tax(
                request.employee_id, organization_id
            )
            
            # Extract monthly tax from result
            monthly_tax_amount = tax_result.get('monthly_tax_liability', 0.0)
            return Money.from_float(monthly_tax_amount)
            
        except Exception as e:
            logger.warning(f"Failed to calculate monthly tax: {str(e)}")
            # Return zero tax if calculation fails
            return Money.zero()
    
    def _build_response_dto(
        self, 
        monthly_salary: MonthlySalary, 
        user, 
        request: MonthlySalaryComputeRequestDTO,
        organization_id: str
    ) -> MonthlySalaryResponseDTO:
        """
        Build response DTO from MonthlySalary entity.
        
        Args:
            monthly_salary: Computed monthly salary entity
            user: User entity
            request: Original request
            organization_id: Organization ID
            
        Returns:
            MonthlySalaryResponseDTO: Response DTO
        """
        # Calculate deductions
        gross_salary = monthly_salary.salary.calculate_gross_salary()
        
        # Calculate statutory deductions (simplified)
        epf_employee = self._calculate_monthly_epf(gross_salary)
        esi_employee = self._calculate_monthly_esi(gross_salary)
        professional_tax = self._calculate_monthly_professional_tax(gross_salary)
        
        # Use monthly tax from entity
        tds = monthly_salary.tax_amount
        
        # Get loan EMI amount from perquisites
        loan_emi_amount = monthly_salary.perquisites_payouts.total if monthly_salary.perquisites_payouts else Money.zero()
        # Extract loan EMI specifically from components
        loan_emi = Money.zero()
        if monthly_salary.perquisites_payouts and monthly_salary.perquisites_payouts.components:
            for component in monthly_salary.perquisites_payouts.components:
                if component.key == "loan":
                    loan_emi = component.value
                    break
        
        total_deductions = epf_employee.add(esi_employee).add(professional_tax).add(tds).add(loan_emi)
        net_salary = self._safe_subtract(gross_salary, total_deductions)
        
        # Get working days info from LWP details
        working_days_info = self._get_working_days_info_from_lwp(monthly_salary.lwp)
        
        return MonthlySalaryResponseDTO(
            employee_id=request.employee_id,
            month=request.month,
            year=monthly_salary.year, # Use the year from the MonthlySalary entity
            tax_year=request.tax_year,
            
            # Employee details
            employee_name=user.name if user else None,
            employee_email=user.email if user else None,
            department=user.department if user else None,
            designation=user.designation if user else None,
            
            # Salary components
            basic_salary=monthly_salary.salary.basic_salary.to_float(),
            da=monthly_salary.salary.dearness_allowance.to_float(),
            hra=monthly_salary.salary.hra_provided.to_float(),
            pf_employee_contribution=monthly_salary.salary.pf_employee_contribution.to_float(),
            pf_employer_contribution=monthly_salary.salary.pf_employer_contribution.to_float(),
            esi_contribution=monthly_salary.salary.esi_contribution.to_float(),
            pf_voluntary_contribution=monthly_salary.salary.pf_voluntary_contribution.to_float(),
            pf_total_contribution=monthly_salary.salary.pf_total_contribution.to_float(),
            special_allowance=monthly_salary.salary.special_allowance.to_float(),
            transport_allowance=0.0,  # Not in current model
            medical_allowance=0.0,  # Not in current model
            bonus=monthly_salary.salary.bonus.to_float(),
            commission=monthly_salary.salary.commission.to_float(),
            other_allowances=0.0,  # Would need to sum specific allowances
            arrears=monthly_salary.salary.arrears.to_float(),
            
            # Deductions
            epf_employee=epf_employee.to_float(),
            esi_employee=esi_employee.to_float(),
            professional_tax=professional_tax.to_float(),
            tds=tds.to_float(),
            advance_deduction=0.0,
            loan_deduction=loan_emi.to_float(),
            other_deductions=0.0,
            
            # Calculated totals
            gross_salary=gross_salary.to_float(),
            total_deductions=total_deductions.to_float(),
            net_salary=net_salary.to_float(),
            
            # Annual projections (from salary package)
            annual_gross_salary=gross_salary.multiply(12).to_float(),
            annual_tax_liability=tds.multiply(12).to_float(),
            
            # Tax details
            tax_regime=monthly_salary.tax_regime.regime_type.value,
            tax_exemptions=0.0,  # Would need to calculate
            standard_deduction=0.0,  # Would need to calculate
            
            # Working days from LWP details
            total_days_in_month=working_days_info['total_days'],
            working_days_in_period=working_days_info['working_days'],
            lwp_days=working_days_info['lwp_days'],
            effective_working_days=working_days_info['effective_days'],
            
            # Status and metadata
            status="computed",
            computation_date=datetime.utcnow().isoformat(),
            notes=f"Computed using {'declared' if request.use_declared_values else 'actual'} values",
            remarks=None,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            created_by=request.computed_by,
            updated_by=request.computed_by,
            
            # Computation details
            use_declared_values=request.use_declared_values,
            computation_mode="declared" if request.use_declared_values else "actual",
            computation_summary={
                "gross_salary": gross_salary.to_float(),
                "total_deductions": total_deductions.to_float(),
                "net_salary": net_salary.to_float(),
                "monthly_tax": tds.to_float(),
                "lwp_days": working_days_info['lwp_days'],
                "lwp_factor": monthly_salary.lwp.get_lwp_factor()
            }
        )
    
    def _get_working_days_info_from_lwp(self, lwp_details: LWPDetails) -> Dict[str, int]:
        """
        Get working days information from LWP details.
        
        Args:
            lwp_details: LWP details entity
            
        Returns:
            Dict containing working days information
        """
        import calendar
        
        # Get total days in month
        total_days = calendar.monthrange(lwp_details.year, lwp_details.month)[1]
        
        # Use LWP details for working days
        working_days = lwp_details.total_working_days
        lwp_days = lwp_details.lwp_days
        effective_days = lwp_details.get_paid_days()
        
        return {
            'total_days': total_days,
            'working_days': working_days,
            'lwp_days': lwp_days,
            'effective_days': effective_days
        }
    
    def _calculate_monthly_epf(self, gross_salary: Money) -> Money:
        """Calculate monthly EPF contribution (12% of basic + DA)."""
        # Simplified calculation - in reality would need basic + DA
        return gross_salary.multiply(Decimal('0.12'))
    
    def _calculate_monthly_esi(self, gross_salary: Money) -> Money:
        """Calculate monthly ESI contribution (0.75% of gross)."""
        return gross_salary.multiply(Decimal('0.0075'))
    
    def _calculate_monthly_professional_tax(self, gross_salary: Money) -> Money:
        """Calculate monthly professional tax based on slabs."""
        # Simplified - would need proper slab calculation
        gross_amount = gross_salary.to_float()
        if gross_amount <= 10000:
            return Money.zero()
        elif gross_amount <= 15000:
            return Money.from_float(150.0)
        else:
            return Money.from_float(200.0)
    
    def _get_working_days_info(self, month: int, year: int) -> Dict[str, int]:
        """Get working days information for the month."""
        # Simplified calculation
        import calendar
        
        # Get total days in month
        total_days = calendar.monthrange(year, month)[1]
        
        # Assume 26 working days per month (excluding Sundays)
        working_days = 26
        lwp_days = 0  # Would need to get from attendance system
        effective_days = working_days - lwp_days
        
        return {
            'total_days': total_days,
            'working_days': working_days,
            'lwp_days': lwp_days,
            'effective_days': effective_days
        }

    def _safe_subtract(self, a: Money, b: Money) -> Money:
        """Safely subtract two Money objects and handle negative results gracefully."""
        try:
            return a.subtract(b)
        except ValueError as e:
            if "Cannot subtract to negative amount" in str(e):
                # If subtraction would result in negative, return zero
                return Money.zero()
            else:
                # Re-raise other errors
                raise
    
    def _convert_to_financial_year_month(self, calendar_month: int, tax_year: TaxYear) -> int:
        """
        Convert calendar month/year to financial year month (1-12).
        
        Args:
            calendar_month: Calendar month (1-12)
            tax_year: Tax year object
            
        Returns:
            int: Financial year month (1-12, where 1=April, 12=March)
        """
        # Get financial year start date
        fy_start_date = tax_year.get_start_date()
        fy_start_year = fy_start_date.year
        fy_start_month = fy_start_date.month
        
        # Calculate the difference in months
        month_diff = (fy_start_year - fy_start_year) * 12 + (calendar_month - fy_start_month)
        
        # Convert to financial year month (1-12)
        financial_year_month = month_diff + 1
        
        # Ensure it's within valid range
        if not 1 <= financial_year_month <= 12:
            raise ValueError(f"Invalid financial year month: {financial_year_month}")
        
        return financial_year_month
    