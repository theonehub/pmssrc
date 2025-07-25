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
from app.domain.entities.taxation.monthly_salary_status import TDSStatus, PayoutStatus, PfStatus
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
    tax_year: TaxYear
    tax_regime: TaxRegime
    tax_amount: Money
    net_salary: Money
    one_time_arrear: Money = field(default_factory=Money.zero)
    one_time_bonus: Money = field(default_factory=Money.zero)
    tds_status: TDSStatus = field(default_factory=lambda: TDSStatus(paid=False, month=0, total_tax_liability=Money.zero()))
    lwp: LWPDetails = field(default_factory=lambda: LWPDetails(month=0))
    payout_status: PayoutStatus = field(default_factory=PayoutStatus)
    pf_status: PfStatus = field(default_factory=PfStatus)
    

    def __post_init__(self):
        if self.salary is None:
            raise ValueError("Salary cannot be None")
        if self.payout_status is None:
            self.payout_status = PayoutStatus(status='computed')
        if self.tds_status is None:
            self.tds_status = TDSStatus(paid=False, month=self.month, total_tax_liability=Money.zero())
        if self.lwp is None:
            self.lwp = LWPDetails(month=self.month)
        if self.pf_status is None:
            self.pf_status = PfStatus()
        
    def compute_net_pay(self) -> Money:
        """
        Compute the net pay for the month.
        """
        self.net_salary = self.salary.calculate_gross_salary()
        