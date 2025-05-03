from dataclasses import dataclass
from typing import Optional, Dict, Any, List

@dataclass
class IncomeFromOtherSources:
    interest_savings: float = 0
    interest_fd: float = 0
    interest_rd: float = 0
    dividend_income: float = 0
    rental_income: float = 0
    other_misc: float = 0

    def total(self):
        return sum([
            self.interest_savings,
            self.interest_fd,
            self.interest_rd,
            self.dividend_income,
            self.rental_income,
            self.other_misc
        ])

@dataclass
class CapitalGains:
    stcg_111a: float = 0
    ltcg_112a: float = 0

    def total(self):
        return self.stcg_111a + self.ltcg_112a

@dataclass
class Perquisites:
    company_car: float = 0
    rent_free_accommodation: float = 0
    concessional_loan: float = 0
    gift_vouchers: float = 0

    def total(self):
        return sum([
            self.company_car,
            self.rent_free_accommodation,
            self.concessional_loan,
            self.gift_vouchers
        ])

@dataclass
class SalaryComponents:
    basic: float = 0
    dearness_allowance: float = 0
    hra: float = 0
    special_allowance: float = 0
    bonus: float = 0
    perquisites: Optional[Perquisites] = None

    def total(self):
        base_total = self.basic + self.dearness_allowance + self.hra + self.special_allowance + self.bonus
        if self.perquisites:
            base_total += self.perquisites.total()
        return base_total

@dataclass
class DeductionComponents:
    section_80c: float = 0
    section_80d: float = 0
    section_24b: float = 0
    section_80e: float = 0
    section_80g: float = 0
    section_80tta: float = 0

    def total(self):
        return (
            min(self.section_80c, 150000) +
            min(self.section_80d, 25000) +
            min(self.section_24b, 200000) +
            self.section_80e +
            self.section_80g +
            min(self.section_80tta, 10000)
        )


@dataclass
class Taxation:
    emp_id: str
    salary: SalaryComponents
    other_sources: IncomeFromOtherSources
    capital_gains: CapitalGains
    deductions: DeductionComponents
    regime: str
    total_tax: float
    tax_breakup: dict
    tax_year: str
    filing_status: str
    tax_payable: float
    tax_paid: float
    tax_due: float
    tax_refundable: float
    tax_pending: float
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Taxation':
        """Convert a dictionary to a Taxation object"""
        salary_data = data.get('salary', {})
        other_sources_data = data.get('other_sources', {})
        capital_gains_data = data.get('capital_gains', {})
        deductions_data = data.get('deductions', {})
        
        # Create Perquisites object if it exists in salary data
        perquisites = None
        if 'perquisites' in salary_data and salary_data['perquisites']:
            # Make sure we have all required fields for Perquisites
            perq_data = salary_data['perquisites']
            if isinstance(perq_data, dict):
                perquisites = Perquisites(
                    company_car=perq_data.get('company_car', 0),
                    rent_free_accommodation=perq_data.get('rent_free_accommodation', 0),
                    concessional_loan=perq_data.get('concessional_loan', 0),
                    gift_vouchers=perq_data.get('gift_vouchers', 0)
                )
            else:
                # Already a Perquisites object
                perquisites = perq_data
        
        # Create SalaryComponents
        salary = SalaryComponents(
            basic=salary_data.get('basic', 0),
            dearness_allowance=salary_data.get('dearness_allowance', 0),
            hra=salary_data.get('hra', 0),
            special_allowance=salary_data.get('special_allowance', 0),
            bonus=salary_data.get('bonus', 0),
            perquisites=perquisites
        )
        
        # Create IncomeFromOtherSources
        other_sources = IncomeFromOtherSources(
            interest_savings=other_sources_data.get('interest_savings', 0),
            interest_fd=other_sources_data.get('interest_fd', 0),
            interest_rd=other_sources_data.get('interest_rd', 0),
            dividend_income=other_sources_data.get('dividend_income', 0),
            rental_income=other_sources_data.get('rental_income', 0),
            other_misc=other_sources_data.get('other_misc', 0)
        )
        
        # Create CapitalGains
        capital_gains = CapitalGains(
            stcg_111a=capital_gains_data.get('stcg_111a', 0),
            ltcg_112a=capital_gains_data.get('ltcg_112a', 0)
        )
        
        # Create DeductionComponents
        deductions = DeductionComponents(
            section_80c=deductions_data.get('section_80c', 0),
            section_80d=deductions_data.get('section_80d', 0),
            section_24b=deductions_data.get('section_24b', 0),
            section_80e=deductions_data.get('section_80e', 0),
            section_80g=deductions_data.get('section_80g', 0),
            section_80tta=deductions_data.get('section_80tta', 0)
        )
        
        # Create Taxation object
        return cls(
            emp_id=data.get('emp_id', ''),
            salary=salary,
            other_sources=other_sources,
            capital_gains=capital_gains,
            deductions=deductions,
            regime=data.get('regime', 'old'),
            total_tax=data.get('total_tax', 0),
            tax_breakup=data.get('tax_breakup', {}),
            tax_year=data.get('tax_year', ''),
            filing_status=data.get('filing_status', 'draft'),
            tax_payable=data.get('tax_payable', 0),
            tax_paid=data.get('tax_paid', 0),
            tax_due=data.get('tax_due', 0),
            tax_refundable=data.get('tax_refundable', 0),
            tax_pending=data.get('tax_pending', 0)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert a Taxation object to a dictionary"""
        # Convert perquisites to dict if present
        perquisites_dict = None
        if self.salary.perquisites:
            # Check if perquisites is already a dictionary
            if isinstance(self.salary.perquisites, dict):
                perquisites_dict = self.salary.perquisites
            else:
                # It's a Perquisites object
                perquisites_dict = {
                    'company_car': self.salary.perquisites.company_car,
                    'rent_free_accommodation': self.salary.perquisites.rent_free_accommodation,
                    'concessional_loan': self.salary.perquisites.concessional_loan,
                    'gift_vouchers': self.salary.perquisites.gift_vouchers
                }
        
        # Create the dictionary
        return {
            'emp_id': self.emp_id,
            'salary': {
                'basic': self.salary.basic,
                'dearness_allowance': self.salary.dearness_allowance,
                'hra': self.salary.hra,
                'special_allowance': self.salary.special_allowance,
                'bonus': self.salary.bonus,
                'perquisites': perquisites_dict
            },
            'other_sources': {
                'interest_savings': self.other_sources.interest_savings,
                'interest_fd': self.other_sources.interest_fd,
                'interest_rd': self.other_sources.interest_rd,
                'dividend_income': self.other_sources.dividend_income,
                'rental_income': self.other_sources.rental_income,
                'other_misc': self.other_sources.other_misc
            },
            'capital_gains': {
                'stcg_111a': self.capital_gains.stcg_111a,
                'ltcg_112a': self.capital_gains.ltcg_112a
            },
            'deductions': {
                'section_80c': self.deductions.section_80c,
                'section_80d': self.deductions.section_80d,
                'section_24b': self.deductions.section_24b,
                'section_80e': self.deductions.section_80e,
                'section_80g': self.deductions.section_80g,
                'section_80tta': self.deductions.section_80tta
            },
            'regime': self.regime,
            'total_tax': self.total_tax,
            'tax_breakup': self.tax_breakup,
            'tax_year': self.tax_year,
            'filing_status': self.filing_status,
            'tax_payable': self.tax_payable,
            'tax_paid': self.tax_paid,
            'tax_due': self.tax_due,
            'tax_refundable': self.tax_refundable,
            'tax_pending': self.tax_pending
        }
        
    def get_taxable_income(self) -> float:
        """Calculate the total taxable income"""
        gross_income = self.salary.total() + self.other_sources.total() + self.capital_gains.total()
        deductions_total = 0 if self.regime == 'new' else self.deductions.total()
        return max(0, gross_income - deductions_total)
    
    def get_tax_summary(self) -> Dict[str, Any]:
        """Get a summary of the taxation"""
        return {
            'emp_id': self.emp_id,
            'tax_year': self.tax_year,
            'regime': self.regime,
            'gross_income': self.salary.total() + self.other_sources.total() + self.capital_gains.total(),
            'deductions': self.deductions.total() if self.regime == 'old' else 0,
            'taxable_income': self.get_taxable_income(),
            'total_tax': self.total_tax,
            'tax_paid': self.tax_paid,
            'tax_due': self.tax_due,
            'tax_refundable': self.tax_refundable,
            'filing_status': self.filing_status
        }
        