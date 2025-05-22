"""
Deduction components model for taxation calculations.

Represents all deduction components as per Indian Income Tax Act.
"""

import logging
from dataclasses import dataclass
from datetime import date
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

from models.taxation.salary import SalaryComponents
from models.taxation.income_sources import IncomeFromOtherSources
from models.taxation.constants import (
    section_80g_100_wo_ql_heads,
    section_80g_50_wo_ql_heads,
    section_80g_100_ql_heads,
    section_80g_50_ql_heads
)


@dataclass
class DeductionComponents:
    """
    Represents all deduction components as per Indian Income Tax Act.
    Includes deductions under various sections like 80C, 80D, etc.
    """
    regime: str = 'new'
    age: int = 0
    
    # section 80C
    section_80c_lic: float = 0           # Life Insurance Premium
    section_80c_epf: float = 0           # Employee Provident Fund
    section_80c_ssp: float = 0           # Sukanya Samridhi Account
    section_80c_nsc: float = 0           # National Savings Certificate
    section_80c_ulip: float = 0          # Unit Linked Insurance Plan
    section_80c_tsmf: float = 0          # Tax Saving Mutual Fund
    section_80c_tffte2c: float = 0       # Tuition Fees for full time education of upto 2 kids
    section_80c_paphl: float = 0         # Principal amount paid for housing loan installments
    section_80c_sdpphp: float = 0        # Stamp duty paid for purchase of residental property
    section_80c_tsfdsb: float = 0        # Tax saving fixed deposit in a scheduled bank
    section_80c_scss: float = 0          # Senior citizen savings scheme
    section_80c_others: float = 0        # Others  Max all above 1,50,000

    # section 80CCC
    section_80ccc_ppic: float = 0        # Pension Plan of LIC or other Insurance Company  Max 1,50,000

    # section 80CCD
    section_80ccd_1_nps: float = 0       # self-employed or employee contribution to NPS
    section_80ccd_1b_additional: float = 0  # additional contribution to NPS by self-employed 
                                           # or employee Max 50,000

    # Max deduction 1,50,000 for all the above elements
    def total_deductions_80c_80ccd_80ccd_1_1b(self, regime: str = 'new') -> float:
        """
        Calculate total deductions under 80C, 80CCC, 80CCD(1), 80CCD(1B)
        Max limit of 1,50,000 applies to 80C, 80CCC, 80CCD(1) combined
        Additional 50,000 for 80CCD(1B)
        """
        if regime == 'new':
            return 0
        else:
            logger.info(f"Section 80C components: Life Insurance Premium :{self.section_80c_lic}")
            logger.info(f"Employee Provident Fund :{self.section_80c_epf}")
            logger.info(f"Sukanya Samridhi Account :{self.section_80c_ssp}")
            logger.info(f"National Savings Certificate :{self.section_80c_nsc}")
            logger.info(f"Unit Linked Insurance Plan :{self.section_80c_ulip}")
            logger.info(f"Tax Saving Mutual Fund :{self.section_80c_tsmf}")
            logger.info(f"Tuition Fees for full time education of upto 2 kids :{self.section_80c_tffte2c}")
            logger.info(f"Principal amount paid for housing loan installments :{self.section_80c_paphl}")
            logger.info(f"Stamp duty paid for purchase of residental property :{self.section_80c_sdpphp}")
            logger.info(f"Tax saving fixed deposit in a scheduled bank :{self.section_80c_tsfdsb}")
            logger.info(f"Senior citizen savings scheme :{self.section_80c_scss}")
            logger.info(f"Others :{self.section_80c_others}")
            logger.info(f"Pension Payment under section 80CCC :{self.section_80ccc_ppic}")
            logger.info(f"NPS :{self.section_80ccd_1_nps}")
            logger.info(f"Additional contribution to NPS by self-employed or employee(50K) :{self.section_80ccd_1b_additional}")
            
            # Calculate Section 80C total (capped at 150,000)
            section_80c_total = (min(sum([
                self.section_80c_lic,
                self.section_80c_epf,
                self.section_80c_ssp,
                self.section_80c_nsc,
                self.section_80c_ulip,
                self.section_80c_tsmf,
                self.section_80c_tffte2c,
                self.section_80c_paphl,
                self.section_80c_sdpphp,
                self.section_80c_tsfdsb,
                self.section_80c_scss,
                self.section_80c_others,
                self.section_80ccc_ppic,
                self.section_80ccd_1_nps]), 150000) +
                min(self.section_80ccd_1b_additional, 50000))
            logger.info(f"Section 80C total: {section_80c_total}")
            return section_80c_total
            
    section_80ccd_2_enps: float = 0  # contribution to NPS by employer 
                                     # 14% of salary(govt employees) 
                                     # 10% of salary(private employees)
    #Gross income is Basic + DA only
    #TODO: Not including in deductions for now.
    def total_deductions_80ccd_2(self, regime: str = 'new', gross_income_basic_da: float = 0, is_govt_employee: bool = False) -> float:
        """
        Calculate total deductions under 80CCD(2) - Employer's contribution to NPS
        Limit is 14% of salary for government employees, 10% for private
        """
        if regime == 'new':
            return 0
        else:
            if is_govt_employee:
                logger.info(f"Calculating Section 80CCD(2) total for government employee {gross_income_basic_da} * 14% = {gross_income_basic_da * 0.14}")
                max_cap = gross_income_basic_da * 0.14
            else:
                logger.info(f"Calculating Section 80CCD(2) total for private employee {gross_income_basic_da} * 10% = {gross_income_basic_da * 0.10}")
                max_cap = gross_income_basic_da * 0.10
            logger.info(f"Section 80CCD(2) Employer's contribution to NPS: {self.section_80ccd_2_enps}")
            logger.info(f"Deduction: {min(self.section_80ccd_2_enps, max_cap)}")
            return min(self.section_80ccd_2_enps, max_cap)
            
    # section 80D Health Insurance Premium Self and Family
    section_80d_hisf: float = 0     # Health Insurance Premium for self and family
                                    # Max 25,000 if age is above 60 otherwise 50,000
    section_80d_phcs: float = 0     # Preventive health checkups max 5000 per year
                                    # its included in 25k or 50k limit

    def total_deductions_80d_self_family(self, regime: str = 'new', age: int = 0) -> float:
        """Calculate total deductions for health insurance for self and family."""
        if regime == 'new':
            return 0
        else:
            if age >= 60:
                max_cap = 50000
                
            else:
                max_cap = 25000
            
        total = min((self.section_80d_hisf + min(self.section_80d_phcs, 5000)), max_cap)
        logger.info(f"Health insurance for self and family for age {age}:")
        logger.info(f"min(({self.section_80d_hisf} + min({self.section_80d_phcs}, 5000)), {max_cap}) = {total}")
        return total

    # section 80D Health Insurance Premium for parents
    section_80d_hi_parent: float = 0  # Health Insurance Premium for parents
                                    # Max 25,000 if age is above 60 otherwise 50,000
    
    def total_deductions_80d_parent(self, regime: str = 'new', parent_age: int = 0) -> float:
        """Calculate total deductions for health insurance for parents."""
        if regime == 'new':
            return 0
        else:
            if parent_age >= 60:
                max_cap = 50000
            else:
                max_cap = 25000
            total = min(self.section_80d_hi_parent, max_cap)
            logger.info(f"Health insurance for parents for age {parent_age}:")
            logger.info(f"min({self.section_80d_hi_parent}, {max_cap}) = {total}")
            return total


    # section 80DD Disability Deduction 
    relation_80dd: str = '' # Spouse, Child, Parents, Sibling
    disability_percentage: str = '' # Between 40%-80% - 75k, More than 80% - 125k
    section_80dd: float = 0

    def total_deductions_80dd(self, regime: str = 'new') -> float:
        """Calculate deductions for disability of dependent under section 80DD."""
        if regime == 'new':
            return 0
        else:
            if self.relation_80dd in ['Spouse', 'Child', 'Parents', 'Sibling']:
                logger.info(f"Calculating Section 80DD total for {self.relation_80dd} \
                            with disability percentage {self.disability_percentage}")
                if self.disability_percentage == 'Between 40%-80%':
                    total = min(self.section_80dd, 75000)
                    logger.info(f"Section 80DD min ({self.relation_80dd}, 75000) = {total}")
                    return total
                else:
                    total = min(self.section_80dd, 125000)
                    logger.info(f"Section 80DD min ({self.relation_80dd}, 125000) = {total}")
                    return total
            else:
                return 0

    # section 80DDB Specific Diseases
    relation_80ddb: str = '' # Spouse, Child, Parents, Sibling
    age_80ddb: int = 0
    section_80ddb: float = 0 # if age < 60 - 40k else 1L

    def total_deductions_80ddb(self, regime: str = 'new', age: int = 0) -> float:
        """Calculate deductions for medical treatment of specified diseases under 80DDB."""
        if regime == 'new':
            return 0
        else:
            if self.relation_80ddb in ['Spouse', 'Child', 'Parents', 'Sibling']:
                logger.info(f"Calculating Section 80DDB total for {self.relation_80ddb} \
                            with age {age}")
                if age < 60:
                    total = min(self.section_80ddb, 40000)
                    logger.info(f"Section 80DDB min ({self.section_80ddb}, 40000) = {total}")
                    return total
                else:
                    total = min(self.section_80ddb, 100000)
                    logger.info(f"Section 80DDB min ({self.section_80ddb}, 100000) = {total}")
                    return total
            else:
                return 0
            
    # section 80E Education Loan Interest
    relation_80e: str = 'Self' # Self, Spouse, Child                                  
    section_80e_interest: float = 0 # No limit

    def total_deductions_80e(self, regime: str = 'new') -> float:
        """Calculate deductions for Education Loan Interest under 80E."""   
        if regime == 'new':
            return 0
        else:
            if self.relation_80e in ['Self', 'Spouse', 'Child']:
                logger.info(f"Section 80E {self.section_80e_interest}")
                return self.section_80e_interest
            else:
                return 0
            
    # section 80EEB interest on loan for EV vehicle purchased between 01.04.2019 & 31.03.2023
    section_80eeb: float = 0    # Max 150K
    ev_purchase_date: date = date.today()

    def total_deductions_80eeb(self, regime: str = 'new', ev_purchase_date: date = date.today()) -> float:
        """Calculate deductions for electric vehicle loan interest under 80EEB."""
        if regime == 'new':
            return 0
        else:
            logger.info(f"Calculating Section 80EEB total for {ev_purchase_date}")
            if ev_purchase_date >= date(2019, 4, 1) and ev_purchase_date <= date(2023, 3, 31):
                total = min(self.section_80eeb, 150000)
                logger.info(f"Section 80EEB min ({self.section_80eeb}, 150000) = {total}")
                return total
            else:
                return 0


    # section 80GGC Political party contributions
    section_80ggc: float = 0        # Deduction on Political parties contribution (No Deductions for payments made in Cash)

    def total_deductions_80ggc(self, regime: str = 'new') -> float:
        """Calculate deduction for political party contributions under 80GGC."""
        if regime == 'new':
            return 0
        else:
            return self.section_80ggc

    # section 80U Self disability
    section_80u: float = 0
    disability_percentage_80u: str = '' # Between 40%-80% - 75k, More than 80% - 125k

    def total_deductions_80u(self, regime: str = 'new') -> float:
        """Calculate deduction for self disability under section 80U."""
        if regime == 'new':
            return 0
        else:
            logger.info(f"Calculating Section 80U total for {self.disability_percentage_80u}")
            if self.disability_percentage_80u == 'Between 40%-80%':
                logger.info(f"Section 80U min ({self.section_80u}, 75000) = {min(self.section_80u, 75000)}")
                return min(self.section_80u, 75000)
            else:
                logger.info(f"Section 80U min ({self.section_80u}, 125000) = {min(self.section_80u, 125000)}")
                return min(self.section_80u, 125000)

    # section 80G Donations to charitable institutions
    section_80g_100_wo_ql: float = 0    # Donations entitled to 100% deduction without qualifying limit 
    section_80g_100_head: str = ''

    def total_deductions_80g_100_wo_ql(self, regime: str = 'new') -> float:
        """Calculate 100% deduction for donations without qualifying limit under 80G."""
        if regime == 'new':
            return 0
        
        elif self.section_80g_100_head in section_80g_100_wo_ql_heads:
            logger.info(f"Section 80G 100% deduction for donations without qualifying limit:")
            logger.info(f"Section 80G {self.section_80g_100_head}")
            logger.info(f"{self.section_80g_100_wo_ql}")
            return self.section_80g_100_wo_ql
        else:
            return 0

    section_80g_50_wo_ql: float = 0    # Donations entitled to 50% deduction without qualifying limit 
    section_80g_50_head: str = ''

    def total_deductions_80g_50_wo_ql(self, regime: str = 'new') -> float:
        """Calculate 50% deduction for donations without qualifying limit under 80G."""
        if regime == 'new':
            return 0
        elif self.section_80g_50_head in section_80g_50_wo_ql_heads:
            logger.info(f"Section 80G 50% deduction for donations without qualifying limit:")
            logger.info(f"Section 80G {self.section_80g_50_head}")
            logger.info(f"{self.section_80g_50_wo_ql} * 0.5 = {self.section_80g_50_wo_ql * 0.5}")
            return (self.section_80g_50_wo_ql * 0.5)
        else:
            return 0

    section_80g_100_ql: float = 0   # Donations entitled to 100% deduction with 
                                    # qualifying limit of 10% of adjusted gross total income  
    section_80g_100_ql_head: str = ''

    #TODO: Compute gross_income excluding 80G deductions(pic on whatsapp)
    def total_deductions_80g_100_ql(self, regime: str = 'new', gross_income: float = 0) -> float:
        """Calculate 100% deduction for donations with qualifying limit under 80G."""
        if regime == 'new':
            return 0
        elif self.section_80g_100_ql_head in section_80g_100_ql_heads:
            logger.info(f"Section 80G 100% deduction for donations with qualifying limit:")
            logger.info(f"Section 80G {self.section_80g_100_ql_head}")
            logger.info(f"min({self.section_80g_100_ql}, ({gross_income} * 0.1)) = {min(self.section_80g_100_ql, (gross_income * 0.1))}")
            return min(self.section_80g_100_ql, (gross_income * 0.1))
        else:
            return 0

    section_80g_50_ql: float = 0    # Donations entitled to 50% deduction with qualifying limit of 10% of adjusted gross total income  
    section_80g_50_ql_head: str = ''

    def total_deductions_80g_50_ql(self, regime: str = 'new', gross_income: float = 0) -> float:
        """Calculate 50% deduction for donations with qualifying limit under 80G."""
        if regime == 'new':
            return 0
        elif self.section_80g_50_ql_head in section_80g_50_ql_heads:
            logger.info(f"Section 80G 50% deduction for donations with qualifying limit:")
            logger.info(f"Section 80G {self.section_80g_50_ql_head}")
            logger.info(f"{self.section_80g_50_ql} * 0.5 = {self.section_80g_50_ql * 0.5}")
            logger.info(f"{gross_income} * 0.1 = {gross_income * 0.1}")
            return min((self.section_80g_50_ql * 0.5), (gross_income * 0.1))
        else:
            return 0

    def total_deductions_80g(self, salary: SalaryComponents, 
                             income_from_other_sources: IncomeFromOtherSources, 
                             regime: str = 'new', 
                            is_govt_employee: bool = False, 
                            age: int = 0, parent_age: int = 0, 
                            ev_purchase_date: date = date.today()) -> float:
        """Calculate total 80G deductions."""
        gross_income_basic_da = salary.basic + salary.dearness_allowance

        ##Compute deductions
        deduction = sum([self.total_deductions_80c_80ccd_80ccd_1_1b(regime), 
                    self.total_deductions_80ccd_2(regime, gross_income_basic_da, is_govt_employee), 
                    self.total_deductions_80d_self_family(regime, age), 
                    self.total_deductions_80d_parent(regime, parent_age), 
                    self.total_deductions_80dd(regime), 
                    self.total_deductions_80ddb(regime, age), 
                    self.total_deductions_80e(regime), 
                    self.total_deductions_80eeb(regime, ev_purchase_date), 
                    self.total_deductions_80ggc(regime), 
                    self.total_deductions_80u(regime)])
        logger.info(f"Deduction computed for 80G(80c to 80u): {deduction}")
        
        ### compute income
        #Gross Total Income
        #– Exempt income (e.g., agricultural income)
        #– Long-term capital gains (LTCG)
        #– Short-term capital gains under Section 111A (STT-paid equity gains)
        #– Deductions under Sections 80C to 80U (excluding 80G)
        #– Income on which income tax is not payable (like shares from an AOP)
        gross_income = sum([
            salary.total_taxable_income_per_slab(gross_salary=(salary.basic+salary.dearness_allowance), regime=regime),
            income_from_other_sources.total_taxable_income_per_slab(regime=regime)
        ])
        logger.info(f"Gross income: {gross_income}")

        ##Compute 80G
        total_deductions_80g = sum([
            self.total_deductions_80g_100_wo_ql(regime),
            self.total_deductions_80g_50_wo_ql(regime),
            self.total_deductions_80g_100_ql(regime, gross_income),
            self.total_deductions_80g_50_ql(regime, gross_income)
        ])
        return total_deductions_80g

    def total_deduction_per_slab(self, salary: SalaryComponents, 
                                 income_from_other_sources: IncomeFromOtherSources, 
                                 regime: str = 'new', 
                                 is_govt_employee: bool = False, 
                                 age: int = 0, 
                                 parent_age: int = 0,
                                 ev_purchase_date: date = date.today()) -> float:
        """
        Calculate total deductions from all sections.
        
        Parameters:
        - regime: Tax regime ('new' or 'old')
        - is_govt_employee: Whether the taxpayer is a government employee
        - gross_income: Gross total income for percentage-based caps
        - age: Age of the taxpayer for age-based deductions
        - ev_purchase_date: Purchase date of electric vehicle for 80EEB deduction
        
        Returns:
        - Total deduction amount
        """
        return (self.total_deductions_80c_80ccd_80ccd_1_1b(regime) +
                self.total_deductions_80d_self_family(regime, age) +
                self.total_deductions_80d_parent(regime, age) +
                self.total_deductions_80dd(regime) +
                self.total_deductions_80ddb(regime, age) +
                self.total_deductions_80eeb(regime, ev_purchase_date) +
                self.total_deductions_80ggc(regime) +
                self.total_deductions_80u(regime) +
                self.total_deductions_80g(salary, income_from_other_sources, regime, is_govt_employee, age, parent_age, ev_purchase_date))

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert the object to a dictionary for JSON serialization."""
        return {
            "regime": cls.regime,
            "age": cls.age,
            "section_80c_lic": cls.section_80c_lic,
            "section_80c_epf": cls.section_80c_epf,
            "section_80c_ssp": cls.section_80c_ssp,
            "section_80c_nsc": cls.section_80c_nsc, 
            "section_80c_ulip": cls.section_80c_ulip,
            "section_80c_tsmf": cls.section_80c_tsmf,
            "section_80c_tffte2c": cls.section_80c_tffte2c,
            "section_80c_paphl": cls.section_80c_paphl,
            "section_80c_sdpphp": cls.section_80c_sdpphp,
            "section_80c_tsfdsb": cls.section_80c_tsfdsb,
            "section_80c_scss": cls.section_80c_scss,
            "section_80c_others": cls.section_80c_others,
            "section_80ccc_ppic": cls.section_80ccc_ppic,
            "section_80ccd_1_nps": cls.section_80ccd_1_nps,
            "section_80ccd_1b_additional": cls.section_80ccd_1b_additional,
            "section_80ccd_2_enps": cls.section_80ccd_2_enps,
            "section_80d_hisf": cls.section_80d_hisf,  
            "section_80d_phcs": cls.section_80d_phcs,
            "section_80d_hi_parent": cls.section_80d_hi_parent,
            "relation_80dd": cls.relation_80dd,
            "disability_percentage": cls.disability_percentage,
            "section_80dd": cls.section_80dd,
            "relation_80ddb": cls.relation_80ddb,
            "age_80ddb": cls.age_80ddb,
            "section_80ddb": cls.section_80ddb,
            "section_80eeb": cls.section_80eeb,
            "relation_80e": cls.relation_80e,
            "section_80e_interest": cls.section_80e_interest,
            "ev_purchase_date": cls.ev_purchase_date.isoformat() if hasattr(cls, 'ev_purchase_date') and cls.ev_purchase_date else None,
            "section_80g_100_wo_ql": cls.section_80g_100_wo_ql,
            "section_80g_100_head": cls.section_80g_100_head,
            "section_80g_50_wo_ql": cls.section_80g_50_wo_ql,
            "section_80g_50_head": cls.section_80g_50_head,
            "section_80g_100_ql": cls.section_80g_100_ql,
            "section_80g_100_ql_head": cls.section_80g_100_ql_head,
            "section_80g_50_ql": cls.section_80g_50_ql,
            "section_80g_50_ql_head": cls.section_80g_50_ql_head,
            "section_80ggc": cls.section_80ggc,
            "section_80u": cls.section_80u,
            "disability_percentage_80u": cls.disability_percentage_80u
        } 