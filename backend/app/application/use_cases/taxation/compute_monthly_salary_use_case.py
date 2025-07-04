import logging
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime

from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.tax_year import TaxYear
from app.domain.entities.taxation.monthly_salary import MonthlySalary
from app.application.interfaces.repositories.salary_package_repository import SalaryPackageRepository
from app.application.interfaces.repositories.monthly_salary_repository import MonthlySalaryRepository
from app.application.interfaces.repositories.user_repository import UserQueryRepository
from app.domain.value_objects.money import Money
from app.domain.value_objects.tax_regime import TaxRegime
from app.domain.entities.taxation.lwp_details import LWPDetails
from app.domain.entities.taxation.salary_income import SalaryIncome
from app.domain.entities.taxation.perquisites import Perquisites
from app.domain.entities.taxation.deductions import TaxDeductions
from app.domain.entities.taxation.retirement_benefits import RetirementBenefits

logger = logging.getLogger(__name__)

class ComputeMonthlySalaryUseCase:
    """Use case for computing monthly salary."""
    
    def __init__(
        self,
        monthly_salary_repository: MonthlySalaryRepository,
        salary_package_repository: SalaryPackageRepository,
        user_query_repository: UserQueryRepository
    ):
        self._monthly_salary_repository = monthly_salary_repository
        self._salary_package_repository = salary_package_repository
        self._user_query_repository = user_query_repository
    
    async def execute(
        self,
        employee_id: str,
        month: int,
        year: int,
        tax_year: str,
        force_recompute: bool = False,
        computed_by: Optional[str] = None,
        organisation_id: str = None
    ) -> MonthlySalary:
        """Compute monthly salary for an employee."""
        try:
            employee_id_vo = EmployeeId(employee_id)
            
            # Check if salary already exists and force_recompute is False
            if not force_recompute:
                existing_salary = await self._monthly_salary_repository.get_by_employee_and_period(
                    employee_id_vo, month, year, organisation_id
                )
                if existing_salary and existing_salary.status in ["computed", "approved"]:
                    logger.info(f"Salary already computed for employee {employee_id} for {month}/{year}")
                    return existing_salary
            
            # Get the latest salary package record
            salary_package = await self._salary_package_repository.get_latest_by_employee(
                employee_id_vo, organisation_id
            )
            
            if not salary_package:
                raise ValueError(f"No salary package found for employee {employee_id}")
            
            # Get employee details
            user = await self._user_query_repository.get_by_employee_id(employee_id_vo, organisation_id)
            if not user:
                raise ValueError(f"Employee {employee_id} not found")
            
            # Extract the latest salary income
            if not salary_package.salary_incomes:
                raise ValueError(f"No salary income found in salary package for employee {employee_id}")
            
            latest_salary_income = salary_package.salary_incomes[-1]
            
            # Extract tax amount from monthly tax liability
            tax_amount = Money.zero()
            if salary_package.tax_calculation_result and salary_package.tax_calculation_result.monthly_tax_liability:
                tax_amount = salary_package.tax_calculation_result.monthly_tax_liability
            
            # Create MonthlySalary entity
            monthly_salary = MonthlySalary(
                employee_id=employee_id_vo,
                month=month,
                year=year,
                salary=latest_salary_income,
                perquisites=salary_package.perquisites or Perquisites(),
                deductions=salary_package.deductions or TaxDeductions(),
                retirement=salary_package.retirement_benefits or RetirementBenefits(),
                lwp=LWPDetails(),  # TODO: Implement LWP computation
                tax_year=TaxYear(tax_year),
                tax_regime=salary_package.tax_regime or TaxRegime.NEW,
                tax_amount=tax_amount,
                net_salary=Money.zero(),
                
                # Additional components from salary income
                transport_allowance=latest_salary_income.conveyance_allowance,
                medical_allowance=latest_salary_income.medical_allowance,
                other_allowances=Money.zero(),  # TODO: Calculate from other allowances
                
                # Deductions from salary income
                epf_employee=latest_salary_income.employee_pf,
                esi_employee=latest_salary_income.employee_esic,
                professional_tax=latest_salary_income.professional_tax,
                advance_deduction=Money.zero(),  # TODO: Get from advance records
                loan_deduction=self._calculate_loan_deduction(salary_package.perquisites, month, year),
                other_deductions=Money.zero(),  # TODO: Calculate other deductions
                
                # Loan details
                loan_principal_amount=self._get_loan_principal_amount(salary_package.perquisites, month, year),
                loan_interest_amount=self._get_loan_interest_amount(salary_package.perquisites, month, year),
                loan_outstanding_amount=self._get_loan_outstanding_amount(salary_package.perquisites, month, year),
                loan_type=self._get_loan_type(salary_package.perquisites),
                
                # Annual projections
                annual_gross_salary=latest_salary_income.calculate_gross_salary().multiply(12),
                annual_tax_liability=tax_amount.multiply(12),
                
                # Tax details
                tax_exemptions=Money.zero(),  # TODO: Calculate from tax calculation
                standard_deduction=Money(Decimal('50000')),  # Standard deduction
                
                # Working days (default values for now)
                total_days_in_month=30,
                working_days_in_period=30,
                lwp_days=0,  # TODO: Calculate from attendance
                effective_working_days=30,
                
                # Status
                status="not_computed",
                
                # Metadata
                created_by=computed_by,
                updated_by=computed_by
            )
            
            # Compute net pay
            monthly_salary.compute_net_pay()
            
            # Save to repository
            saved_salary = await self._monthly_salary_repository.save(monthly_salary, organisation_id)
            
            logger.info(f"Successfully computed monthly salary for employee {employee_id} for {month}/{year}")
            return saved_salary
            
        except Exception as e:
            logger.error(f"Error computing monthly salary for employee {employee_id}: {e}")
            raise
    
    async def bulk_compute(
        self,
        month: int,
        year: int,
        tax_year: str,
        employee_ids: Optional[List[str]] = None,
        force_recompute: bool = False,
        computed_by: Optional[str] = None,
        organisation_id: str = None
    ) -> Dict[str, Any]:
        """Bulk compute monthly salaries for multiple employees."""
        try:
            # Get all employees if not specified
            if not employee_ids:
                # TODO: Get all active employees from user repository
                employee_ids = []
            
            successful = 0
            failed = 0
            skipped = 0
            errors = []
            computed_salaries = []
            
            for employee_id in employee_ids:
                try:
                    # Check if salary already exists and force_recompute is False
                    if not force_recompute:
                        employee_id_vo = EmployeeId(employee_id)
                        existing_salary = await self._monthly_salary_repository.get_by_employee_and_period(
                            employee_id_vo, month, year, organisation_id
                        )
                        if existing_salary and existing_salary.status in ["computed", "approved"]:
                            skipped += 1
                            continue
                    
                    # Compute salary
                    salary = await self.execute(
                        employee_id, month, year, tax_year, force_recompute, computed_by, organisation_id
                    )
                    computed_salaries.append(salary)
                    successful += 1
                    
                except Exception as e:
                    failed += 1
                    errors.append({
                        "employee_id": employee_id,
                        "error": str(e)
                    })
                    logger.error(f"Failed to compute salary for employee {employee_id}: {e}")
            
            # Bulk save successful computations
            if computed_salaries:
                await self._monthly_salary_repository.bulk_save(computed_salaries, organisation_id)
            
            return {
                "total_requested": len(employee_ids),
                "successful": successful,
                "failed": failed,
                "skipped": skipped,
                "errors": errors,
                "computation_summary": {
                    "month": month,
                    "year": year,
                    "tax_year": tax_year,
                    "computed_at": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in bulk compute: {e}")
            raise
    
    async def get_monthly_salaries_for_period(
        self,
        month: int,
        year: int,
        organisation_id: str,
        status: Optional[str] = None,
        department: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get monthly salaries for a period with pagination."""
        try:
            salaries = await self._monthly_salary_repository.get_by_period(
                month, year, organisation_id, status, department, skip, limit
            )
            
            # Get total count for pagination
            total_salaries = await self._monthly_salary_repository.get_by_period(
                month, year, organisation_id, status, department, 0, 10000  # Large limit to get all
            )
            
            return {
                "items": salaries,
                "total": len(total_salaries),
                "skip": skip,
                "limit": limit,
                "has_more": (skip + limit) < len(total_salaries)
            }
            
        except Exception as e:
            logger.error(f"Error getting monthly salaries for period: {e}")
            raise
    
    async def get_monthly_salary_summary(
        self,
        month: int,
        year: int,
        organisation_id: str
    ) -> Dict[str, Any]:
        """Get summary statistics for a period."""
        try:
            summary = await self._monthly_salary_repository.get_summary_by_period(
                month, year, organisation_id
            )
            
            # Transform repository response to match controller expectations
            status_breakdown = summary.get("status_breakdown", {})
            total_records = summary.get("total_records", 0)
            
            # Calculate pending count (total - computed - approved - paid - rejected)
            computed_count = status_breakdown.get("computed", 0)
            approved_count = status_breakdown.get("approved", 0)
            paid_count = status_breakdown.get("paid", 0)
            rejected_count = status_breakdown.get("rejected", 0)
            pending_count = total_records - computed_count - approved_count - paid_count - rejected_count
            
            # Calculate completion rate
            computation_completion_rate = (computed_count / total_records * 100) if total_records > 0 else 0
            
            return {
                "month": month,
                "year": year,
                "total_employees": total_records,
                "computed_count": computed_count,
                "pending_count": max(0, pending_count),  # Ensure non-negative
                "approved_count": approved_count,
                "paid_count": paid_count,
                "total_gross_payroll": summary.get("total_gross_salary", 0.0),
                "total_net_payroll": summary.get("total_net_salary", 0.0),
                "total_deductions": summary.get("total_deductions", 0.0),
                "total_tds": summary.get("total_tax_amount", 0.0),
                "computation_completion_rate": round(computation_completion_rate, 2),
                "last_computed_at": None,  # TODO: Get from actual data
                "next_processing_date": None  # TODO: Calculate based on business logic
            }
            
        except Exception as e:
            logger.error(f"Error getting monthly salary summary: {e}")
            raise
    
    async def update_monthly_salary_status(
        self,
        employee_id: str,
        month: int,
        year: int,
        status: str,
        notes: Optional[str] = None,
        updated_by: Optional[str] = None,
        organisation_id: str = None
    ) -> Optional[MonthlySalary]:
        """Update the status of a monthly salary record."""
        try:
            employee_id_vo = EmployeeId(employee_id)
            
            # Validate status
            valid_statuses = ["not_computed", "computed", "approved", "salary_paid", "tds_paid", "paid", "rejected"]
            if status not in valid_statuses:
                raise ValueError(f"Invalid status: {status}. Valid statuses: {valid_statuses}")
            
            updated_salary = await self._monthly_salary_repository.update_status(
                employee_id_vo, month, year, status, notes, updated_by, organisation_id
            )
            
            if updated_salary:
                logger.info(f"Updated status to {status} for employee {employee_id} for {month}/{year}")
            
            return updated_salary
            
        except Exception as e:
            logger.error(f"Error updating monthly salary status: {e}")
            raise
    
    async def mark_salary_payment(
        self,
        employee_id: str,
        month: int,
        year: int,
        payment_type: str,
        payment_reference: Optional[str] = None,
        payment_notes: Optional[str] = None,
        paid_by: Optional[str] = None,
        organisation_id: str = None
    ) -> Optional[MonthlySalary]:
        """Mark payment for a monthly salary record."""
        try:
            employee_id_vo = EmployeeId(employee_id)
            
            # Validate payment type
            valid_payment_types = ["salary", "tds", "both"]
            if payment_type not in valid_payment_types:
                raise ValueError(f"Invalid payment type: {payment_type}. Valid types: {valid_payment_types}")
            
            updated_salary = await self._monthly_salary_repository.mark_payment(
                employee_id_vo, month, year, payment_type, payment_reference, payment_notes, paid_by, organisation_id
            )
            
            if updated_salary:
                logger.info(f"Marked {payment_type} payment for employee {employee_id} for {month}/{year}")
            
            return updated_salary
            
        except Exception as e:
            logger.error(f"Error marking salary payment: {e}")
            raise
    
    async def delete_monthly_salary(
        self,
        employee_id: str,
        month: int,
        year: int,
        organisation_id: str
    ) -> bool:
        """Delete a monthly salary record."""
        try:
            employee_id_vo = EmployeeId(employee_id)
            
            deleted = await self._monthly_salary_repository.delete(
                employee_id_vo, month, year, organisation_id
            )
            
            if deleted:
                logger.info(f"Deleted monthly salary for employee {employee_id} for {month}/{year}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Error deleting monthly salary: {e}")
            raise
    
    def _calculate_loan_deduction(self, perquisites: Optional[Perquisites], month: int, year: int) -> Money:
        """
        Calculate loan deduction for the given month based on perquisites.
        
        Args:
            perquisites: Perquisites entity containing loan information
            month: Current month (1-12)
            year: Current year
            
        Returns:
            Money: Monthly loan deduction amount
        """
        try:
            if not perquisites or not perquisites.interest_free_loan:
                return Money.zero()
            
            loan = perquisites.interest_free_loan
            
            # If no EMI amount is set, return zero
            if loan.emi_amount.is_zero():
                return Money.zero()
            
            # Check if loan is still active for this month
            loan_start_date = loan.loan_start_date
            if loan_start_date:
                # Calculate months since loan start
                from datetime import date
                current_date = date(year, month, 1)
                months_since_start = (current_date.year - loan_start_date.year) * 12 + (current_date.month - loan_start_date.month)
                
                # If loan hasn't started yet, return zero
                if months_since_start < 0:
                    return Money.zero()
                
                # Calculate remaining loan amount
                monthly_payment_schedule, _ = loan.calculate_monthly_payment_schedule(loan.company_interest_rate)
                
                # Find the payment for the current month
                if months_since_start < len(monthly_payment_schedule):
                    current_payment = monthly_payment_schedule[months_since_start]
                    # Return the EMI amount (principal + interest)
                    return current_payment.principal_amount.add(current_payment.interest_amount)
                else:
                    # Loan is fully paid
                    return Money.zero()
            else:
                # If no start date, assume loan is active and return EMI
                return loan.emi_amount
            
        except Exception as e:
            logger.error(f"Error calculating loan deduction: {e}")
            return Money.zero()
    
    def _get_loan_principal_amount(self, perquisites: Optional[Perquisites], month: int, year: int) -> Money:
        """Get loan principal amount for the given month."""
        try:
            if not perquisites or not perquisites.interest_free_loan:
                return Money.zero()
            
            loan = perquisites.interest_free_loan
            if loan.emi_amount.is_zero():
                return Money.zero()
            
            loan_start_date = loan.loan_start_date
            if loan_start_date:
                from datetime import date
                current_date = date(year, month, 1)
                months_since_start = (current_date.year - loan_start_date.year) * 12 + (current_date.month - loan_start_date.month)
                
                if months_since_start < 0:
                    return Money.zero()
                
                monthly_payment_schedule, _ = loan.calculate_monthly_payment_schedule(loan.company_interest_rate)
                
                if months_since_start < len(monthly_payment_schedule):
                    current_payment = monthly_payment_schedule[months_since_start]
                    return current_payment.principal_amount
                else:
                    return Money.zero()
            else:
                # If no start date, assume all EMI is principal
                return loan.emi_amount
            
        except Exception as e:
            logger.error(f"Error getting loan principal amount: {e}")
            return Money.zero()
    
    def _get_loan_interest_amount(self, perquisites: Optional[Perquisites], month: int, year: int) -> Money:
        """Get loan interest amount for the given month."""
        try:
            if not perquisites or not perquisites.interest_free_loan:
                return Money.zero()
            
            loan = perquisites.interest_free_loan
            if loan.emi_amount.is_zero():
                return Money.zero()
            
            loan_start_date = loan.loan_start_date
            if loan_start_date:
                from datetime import date
                current_date = date(year, month, 1)
                months_since_start = (current_date.year - loan_start_date.year) * 12 + (current_date.month - loan_start_date.month)
                
                if months_since_start < 0:
                    return Money.zero()
                
                monthly_payment_schedule, _ = loan.calculate_monthly_payment_schedule(loan.company_interest_rate)
                
                if months_since_start < len(monthly_payment_schedule):
                    current_payment = monthly_payment_schedule[months_since_start]
                    return current_payment.interest_amount
                else:
                    return Money.zero()
            else:
                # If no start date, assume no interest
                return Money.zero()
            
        except Exception as e:
            logger.error(f"Error getting loan interest amount: {e}")
            return Money.zero()
    
    def _get_loan_outstanding_amount(self, perquisites: Optional[Perquisites], month: int, year: int) -> Money:
        """Get loan outstanding amount for the given month."""
        try:
            if not perquisites or not perquisites.interest_free_loan:
                return Money.zero()
            
            loan = perquisites.interest_free_loan
            if loan.emi_amount.is_zero():
                return Money.zero()
            
            loan_start_date = loan.loan_start_date
            if loan_start_date:
                from datetime import date
                current_date = date(year, month, 1)
                months_since_start = (current_date.year - loan_start_date.year) * 12 + (current_date.month - loan_start_date.month)
                
                if months_since_start < 0:
                    return loan.loan_amount
                
                monthly_payment_schedule, _ = loan.calculate_monthly_payment_schedule(loan.company_interest_rate)
                
                if months_since_start < len(monthly_payment_schedule):
                    return monthly_payment_schedule[months_since_start].outstanding_amount
                else:
                    return Money.zero()
            else:
                # If no start date, assume full loan amount is outstanding
                return loan.loan_amount
            
        except Exception as e:
            logger.error(f"Error getting loan outstanding amount: {e}")
            return Money.zero()
    
    def _get_loan_type(self, perquisites: Optional[Perquisites]) -> Optional[str]:
        """Get loan type."""
        try:
            if not perquisites or not perquisites.interest_free_loan:
                return None
            
            return perquisites.interest_free_loan.loan_type
            
        except Exception as e:
            logger.error(f"Error getting loan type: {e}")
            return None 