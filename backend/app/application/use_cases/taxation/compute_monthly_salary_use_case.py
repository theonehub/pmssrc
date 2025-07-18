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
from app.domain.entities.taxation.monthly_salary import MonthlySalary
from app.domain.entities.taxation.taxation_record import TDSStatus
from app.domain.entities.taxation.salary_income import SalaryIncome
from app.domain.entities.taxation.perquisites import MonthlyPerquisitesPayouts
from app.domain.entities.taxation.deductions import TaxDeductions
from app.domain.entities.taxation.retirement_benefits import RetirementBenefits
from app.domain.entities.taxation.lwp_details import LWPDetails
from app.domain.value_objects.tax_regime import TaxRegime
from app.domain.services.taxation.tax_calculation_service import TaxCalculationService
from app.auth.auth_dependencies import CurrentUser
from app.domain.entities.taxation.monthly_salary_status import PayoutStatus


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
        current_user: CurrentUser
    ) -> MonthlySalaryResponseDTO:
        """
        Execute monthly salary computation for an employee.
        
        Args:
            request: Monthly salary computation request
            current_user: Current authenticated user with organisation context
            
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
            user = await self.user_repository.get_by_id(employee_id, current_user.hostname)
            
            if not user:
                raise ValueError(f"Employee {request.employee_id} not found")
            
            # 2. Get salary package record
            tax_year = TaxYear.from_string(request.tax_year)
            salary_package_record = await self.salary_package_repository.get_salary_package_record(
                request.employee_id, str(tax_year), current_user.hostname
            )
            
            if not salary_package_record:
                raise ValueError(
                    f"Salary package record not found for employee {request.employee_id} "
                    f"in tax year {request.tax_year}"
                )

            # 4. Get current salary income (latest one)
            current_salary_income = salary_package_record.get_latest_salary_income()
            if not current_salary_income:
                raise ValueError(f"No salary income found for employee {request.employee_id}")
            
            # 5. Create monthly salary components
            monthly_salary = await self._create_monthly_salary(
                current_salary_income, salary_package_record, request, current_user
            )
            
            #6 Insert or replace monthly_salary for the same month and year
            existing_index = next(
                (i for i, record in enumerate(salary_package_record.monthly_salary_records)
                 if record.month == monthly_salary.month and record.year == monthly_salary.year),
                None
            )
            if existing_index is not None:
                salary_package_record.monthly_salary_records[existing_index] = monthly_salary
            else:
                salary_package_record.monthly_salary_records.append(monthly_salary)
            await self.salary_package_repository.save(salary_package_record, current_user.hostname)
            
            # 7. Calculate monthly tax
            monthly_tax = await self._calculate_monthly_tax(
                salary_package_record, request, current_user
            )
            
            # 8. Compute net salary
            monthly_salary.compute_net_pay()
            monthly_salary.tax_amount = monthly_tax
            monthly_salary.tds_status.total_tax_liability = monthly_tax
            await self.salary_package_repository.save(salary_package_record, current_user.hostname)
            
            # 9. Build response DTO
            response = self._build_response_dto(
                monthly_salary, user, request, current_user
            )

            logger.info(f"Successfully computed monthly salary for employee {request.employee_id}")
            logger.info(f"Gross: ₹{response.gross_salary:,.2f}, Net: ₹{response.net_salary:,.2f}")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to compute monthly salary for employee {request.employee_id}: {str(e)}")
            raise
    
    async def _create_monthly_salary(
        self, 
        salary_income: SalaryIncome, 
        salary_package_record, 
        request: MonthlySalaryComputeRequestDTO,
        current_user: CurrentUser
    ) -> MonthlySalary:
        """
        Create monthly salary components from annual salary income.
        
        Args:
            salary_income: Annual salary income
            salary_package_record: Employee's salary package record
            request: Computation request
            current_user: Current authenticated user with organisation context
            
        Returns:
            Dict containing monthly salary components
        """

        monthly_lwp = await self._calculate_lwp_days(request.employee_id, request.month, salary_package_record.tax_year.get_start_date().year, current_user)
        one_time_bonus = Money.from_float(request.one_time_bonus) if request.one_time_bonus else Money.zero()
        one_time_arrear = Money.from_float(request.one_time_arrear) if request.one_time_arrear else Money.zero()

        # Create monthly salary income
        monthly_salary_income = SalaryIncome(
            basic_salary=salary_income.basic_salary,
            dearness_allowance=salary_income.dearness_allowance,
            hra_provided=salary_income.hra_provided,
            special_allowance=salary_income.special_allowance,
            commission=salary_income.commission,
            epf_employee=salary_income.epf_employee,
            vps_employee=salary_income.vps_employee,    

            epf_employer=salary_income.epf_employer,

            eps_employee=salary_income.eps_employee,
            eps_employer=salary_income.eps_employer,

            esi_contribution=salary_income.esi_contribution,

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
        
        # 7. Create MonthlySalary entity
        monthly_salary = MonthlySalary(
            employee_id=request.employee_id,
            month=request.month,
            year=salary_package_record.tax_year.get_start_date().year, # Use the start year of the tax year
            salary=monthly_salary_income,
            perquisites_payouts=monthly_perquisites_payouts,
            deductions=monthly_deductions,
            retirement=monthly_retirement,
            lwp=monthly_lwp,
            one_time_arrear=one_time_arrear,
            one_time_bonus=one_time_bonus,
            tds_status=TDSStatus(status='unpaid', total_tax_liability=Money.zero()),
            payout_status=PayoutStatus(status='computed'),
            tax_year=salary_package_record.tax_year,
            tax_regime=salary_package_record.regime,
            tax_amount=Money.zero(),
            net_salary=Money.zero()  # Will be computed below
        )
        return monthly_salary
    
    async def _calculate_lwp_days(
        self,
        employee_id: str,
        month: int,
        year: int,
        current_user: CurrentUser
    ) -> LWPDetails:
        """
        Calculate Leave Without Pay (LWP) days for the specified month.
        
        Args:
            employee_id: Employee identifier
            month: Month (1-12)
            year: Year
            current_user: Current authenticated user with organisation context
            
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
                employee_id, month, year, current_user
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
        current_user: CurrentUser
    ) -> Money:
        """
        Calculate monthly tax liability.
        
        Args:
            salary_package_record: Employee's salary package record
            request: Computation request
            current_user: CurrentUser
            
        Returns:
            Money: Monthly tax amount
        """
        try:
            # Use existing tax calculation service
            tax_result = await self.tax_calculation_service.compute_monthly_tax(
                request.employee_id, current_user, computing_month=request.month
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
        current_user: CurrentUser
    ) -> MonthlySalaryResponseDTO:
        """
        Build response DTO from MonthlySalary entity.
        
        Args:
            monthly_salary: Computed monthly salary entity
            user: User entity
            request: Original request
            current_user: Current authenticated user with organisation context
            
        Returns:
            MonthlySalaryResponseDTO: Response DTO
        """
  
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
        
        # Calculate professional tax
        professional_tax = self._calculate_monthly_professional_tax(monthly_salary.salary.basic_salary + monthly_salary.salary.dearness_allowance)

        total_deductions = (monthly_salary.salary.eps_employee + monthly_salary.salary.esi_contribution + tds + loan_emi)
        net_salary = self._safe_subtract(monthly_salary.salary.basic_salary + monthly_salary.salary.dearness_allowance, total_deductions)
        
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
            
            # Salary components (from salary structure)
            basic_salary=monthly_salary.salary.basic_salary.to_float(),
            da=monthly_salary.salary.dearness_allowance.to_float(),
            hra=monthly_salary.salary.hra_provided.to_float(),
            eps_employee=monthly_salary.salary.eps_employee.to_float(),  # Employee Pension Scheme (part of EPF, 8.33% of basic+DA)
            eps_employer=monthly_salary.salary.eps_employer.to_float(),
            esi_contribution=monthly_salary.salary.esi_contribution.to_float(),
            vps_employee=monthly_salary.salary.vps_employee.to_float(),  # Voluntary PF (over and above statutory EPF)
            special_allowance=monthly_salary.salary.special_allowance.to_float(),
            transport_allowance=0.0,  # Not in current model
            medical_allowance=0.0,  # Not in current model
            commission=monthly_salary.salary.commission.to_float(),
            other_allowances=0.0,  # Would need to sum specific allowances

            # One time bonuses and arrears
            one_time_arrear=monthly_salary.one_time_arrear.to_float() if hasattr(monthly_salary, 'one_time_arrear') else 0.0,
            one_time_bonus=monthly_salary.one_time_bonus.to_float() if hasattr(monthly_salary, 'one_time_bonus') else 0.0,
            
            # Deductions (statutory, calculated)
            epf_employee=monthly_salary.salary.eps_employee.to_float(),  # Employee Provident Fund (12% of basic+DA, includes EPS+VPF)
            esi_employee=monthly_salary.salary.esi_contribution.to_float(),
            tds=tds.to_float(),
            advance_deduction=0.0,
            loan_deduction=loan_emi.to_float(),
            other_deductions=0.0,
            
            # Calculated totals
            gross_salary=monthly_salary.salary.basic_salary.to_float() + monthly_salary.salary.dearness_allowance.to_float(),
            total_deductions=total_deductions.to_float(),
            net_salary=net_salary.to_float(),
            
            # Annual projections (from salary package)
            annual_gross_salary=monthly_salary.salary.basic_salary.multiply(12).to_float() + monthly_salary.salary.dearness_allowance.multiply(12).to_float(),
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
                "gross_salary": monthly_salary.salary.basic_salary.to_float() + monthly_salary.salary.dearness_allowance.to_float(),
                "total_deductions": total_deductions.to_float(),
                "net_salary": net_salary.to_float(),
                "monthly_tax": tds.to_float(),
                "lwp_days": working_days_info['lwp_days'],
                "lwp_factor": monthly_salary.lwp.get_lwp_factor()
            },
            professional_tax=professional_tax.to_float()
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
    