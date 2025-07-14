from dataclasses import dataclass, field
from app.domain.value_objects.money import Money
from app.domain.value_objects.tax_year import TaxYear
from app.domain.value_objects.tax_regime import TaxRegime
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.entities.taxation.salary_income import SalaryIncome
from app.domain.entities.taxation.perquisites import MonthlyPerquisitesPayouts
from app.domain.entities.taxation.deductions import TaxDeductions
from app.domain.entities.taxation.retirement_benefits import RetirementBenefits
from app.domain.entities.taxation.lwp_details import LWPDetails
from typing import Optional
from datetime import date

@dataclass
class MonthlySalary:
    employee_id: EmployeeId
    month: int
    year: int
    salary: SalaryIncome
    perquisites_payouts: MonthlyPerquisitesPayouts
    deductions: TaxDeductions
    retirement: RetirementBenefits
    lwp: LWPDetails
    tax_year: TaxYear
    tax_regime: TaxRegime
    tax_amount: Money
    net_salary: Money
    status: str = 'computed'
    comments: Optional[str] = None
    transaction_id: Optional[str] = None
    transfer_date: Optional[date] = None
    

    def __post_init__(self):
        if self.salary is None:
            raise ValueError("Salary cannot be None")
        
    def compute_net_pay(self) -> Money:
        """
        Compute the net pay for the month.
        """
        self.net_salary = self.salary.calculate_gross_salary()
        