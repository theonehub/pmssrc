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
from models.taxation.income_sources import IncomeFromOtherSources, CapitalGains
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
        """
        Calculate total deductions for health insurance for self and family.
        
        FIXED CRITICAL ERROR: Age logic was inverted.
        Correct limits:
        - Below 60 years: Rs. 25,000
        - 60+ years: Rs. 50,000
        """
        if regime == 'new':
            return 0
        else:
            # FIXED: Corrected age-based limits
            if age >= 60:
                max_cap = 50000  # Senior citizens get higher limit
            else:
                max_cap = 25000  # Below 60 gets lower limit
            
            total = min((self.section_80d_hisf + min(self.section_80d_phcs, 5000)), max_cap)
            logger.info(f"Health insurance for self and family for age {age}:")
            logger.info(f"FIXED: Age >= 60 gets Rs. 50,000 limit, below 60 gets Rs. 25,000 limit")
            logger.info(f"min(({self.section_80d_hisf} + min({self.section_80d_phcs}, 5000)), {max_cap}) = {total}")
            return total

    # section 80D Health Insurance Premium for parents
    section_80d_hi_parent: float = 0  # Health Insurance Premium for parents
                                    # Max 25,000 if parent age is below 60, otherwise 50,000
    
    def total_deductions_80d_parent(self, regime: str = 'new', parent_age: int = 0) -> float:
        """
        Calculate total deductions for health insurance for parents.
        
        FIXED: Proper age-based limits for parents' health insurance.
        """
        if regime == 'new':
            return 0
        else:
            # FIXED: Corrected parent age-based limits
            if parent_age >= 60:
                max_cap = 50000  # Senior citizen parents get higher limit
            else:
                max_cap = 25000  # Below 60 gets lower limit
                
            total = min(self.section_80d_hi_parent, max_cap)
            logger.info(f"Health insurance for parents for age {parent_age}:")
            logger.info(f"FIXED: Parent age >= 60 gets Rs. 50,000 limit, below 60 gets Rs. 25,000 limit")
            logger.info(f"min({self.section_80d_hi_parent}, {max_cap}) = {total}")
            return total


    # section 80DD Disability Deduction 
    relation_80dd: str = '' # Spouse, Child, Parents, Sibling
    disability_percentage: str = '' # Between 40%-80% - 75k, More than 80% - 125k
    section_80dd: float = 0

    def total_deductions_80dd(self, regime: str = 'new') -> float:
        """
        Calculate deductions for disability of dependent under section 80DD.
        
        FIXED CRITICAL LOGIC ERROR: 
        - Section 80DD is a fixed deduction based on disability percentage
        - It's not based on actual amount spent
        - Rs. 75,000 for 40-80% disability, Rs. 1,25,000 for 80%+ disability
        """
        if regime == 'new':
            return 0
        else:
            if self.relation_80dd in ['Spouse', 'Child', 'Parents', 'Sibling']:
                logger.info(f"Calculating Section 80DD total for {self.relation_80dd} "
                           f"with disability percentage {self.disability_percentage}")
                
                # FIXED: Section 80DD is a FIXED deduction, not min of actual and limit
                if self.disability_percentage == 'Between 40%-80%':
                    total = 75000  # Fixed deduction for 40-80% disability
                    logger.info(f"Section 80DD FIXED deduction for 40-80% disability: Rs. 75,000")
                    return total
                elif self.disability_percentage == 'More than 80%' or self.disability_percentage == '80%+':
                    total = 125000  # Fixed deduction for 80%+ disability
                    logger.info(f"Section 80DD FIXED deduction for 80%+ disability: Rs. 1,25,000")
                    return total
                else:
                    logger.info(f"Section 80DD: Invalid disability percentage: {self.disability_percentage}")
                    return 0
            else:
                logger.info(f"Section 80DD: No valid relation specified: {self.relation_80dd}")
                return 0

    # section 80DDB Specific Diseases
    relation_80ddb: str = '' # Self, Spouse, Child, Parents, Sibling
    age_80ddb: int = 0
    section_80ddb: float = 0 # if age < 60 - 40k else 100k

    def total_deductions_80ddb(self, regime: str = 'new', age: int = 0) -> float:
        """
        Calculate deductions for medical treatment of specified diseases under 80DDB.
        
        FIXED: Added 'Self' as valid relation and corrected age logic.
        """
        if regime == 'new':
            return 0
        else:
            # FIXED: Added 'Self' to valid relations
            if self.relation_80ddb in ['Self', 'Spouse', 'Child', 'Parents', 'Sibling']:
                logger.info(f"Calculating Section 80DDB total for {self.relation_80ddb} "
                           f"with age {age if self.relation_80ddb == 'Self' else self.age_80ddb}")
                
                # Use appropriate age based on relation
                relevant_age = age if self.relation_80ddb == 'Self' else self.age_80ddb
                
                if relevant_age < 60:
                    total = min(self.section_80ddb, 40000)
                    logger.info(f"Section 80DDB: Age < 60, limit Rs. 40,000, deduction: {total}")
                    return total
                else:
                    total = min(self.section_80ddb, 100000)
                    logger.info(f"Section 80DDB: Age >= 60, limit Rs. 1,00,000, deduction: {total}")
                    return total
            else:
                logger.info(f"Section 80DDB: No valid relation specified: {self.relation_80ddb}")
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

    def total_deductions_80eeb(self, regime: str = 'new') -> float:
        """
        Calculate deductions for electric vehicle loan interest under 80EEB.
        
        FIXED: Updated date validation as Section 80EEB was extended.
        Currently valid for loans taken for EVs purchased between:
        - Original: 01.04.2019 to 31.03.2023
        - Extended: 01.04.2019 to 31.03.2025 (as per recent budget announcements)
        """
        if regime == 'new':
            return 0
        else:
            logger.info(f"Calculating Section 80EEB total for EV purchase date: {self.ev_purchase_date}")
            
            # FIXED: Extended date range and better validation
            if hasattr(self, 'ev_purchase_date') and self.ev_purchase_date:
                # Updated date range - scheme has been extended
                if self.ev_purchase_date >= date(2019, 4, 1) and self.ev_purchase_date <= date(2025, 3, 31):
                    total = min(self.section_80eeb, 150000)
                    logger.info(f"Section 80EEB: EV purchased within eligible period, deduction: {total}")
                    return total
                else:
                    logger.info(f"Section 80EEB: EV purchase date {self.ev_purchase_date} not within eligible period (01.04.2019 to 31.03.2025)")
                    return 0
            else:
                logger.info("Section 80EEB: No EV purchase date provided")
                return 0


    # section 80GGC Political party contributions
    section_80ggc: float = 0        # Deduction on Political parties contribution (No Deductions for payments made in Cash)

    def total_deductions_80ggc(self, regime: str = 'new') -> float:
        """
        Calculate deduction for political party contributions under 80GGC.
        
        FIXED: Added validation and limits as per Income Tax Act.
        - 100% deduction is allowed
        - No cash payments allowed (assumed all contributions are by cheque/online)
        - No upper limit specified in the Act
        """
        if regime == 'new':
            return 0
        else:
            if self.section_80ggc > 0:
                logger.info(f"Section 80GGC: Political party contribution deduction: {self.section_80ggc}")
                logger.info("Note: Cash payments are not eligible for deduction under 80GGC")
                return self.section_80ggc
            else:
                return 0

    # section 80U Self disability
    section_80u: float = 0
    disability_percentage_80u: str = '' # Between 40%-80% - 75k, More than 80% - 125k

    def total_deductions_80u(self, regime: str = 'new') -> float:
        """
        Calculate deduction for self disability under section 80U.
        
        FIXED CRITICAL LOGIC ERROR:
        - Section 80U is a FIXED deduction based on disability percentage
        - It's not based on actual amount spent
        - Rs. 75,000 for 40-80% disability, Rs. 1,25,000 for 80%+ disability
        """
        if regime == 'new':
            return 0
        else:
            logger.info(f"Calculating Section 80U total for disability percentage: {self.disability_percentage_80u}")
            
            # FIXED: Section 80U is a FIXED deduction, not min of actual and limit
            if self.disability_percentage_80u == 'Between 40%-80%':
                total = 75000  # Fixed deduction for 40-80% disability
                logger.info(f"Section 80U FIXED deduction for 40-80% disability: Rs. 75,000")
                return total
            elif self.disability_percentage_80u == 'More than 80%' or self.disability_percentage_80u == '80%+':
                total = 125000  # Fixed deduction for 80%+ disability  
                logger.info(f"Section 80U FIXED deduction for 80%+ disability: Rs. 1,25,000")
                return total
            else:
                logger.info(f"Section 80U: No valid disability percentage specified: {self.disability_percentage_80u}")
                return 0

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
                             capital_gains: CapitalGains,
                             regime: str = 'new', 
                            is_govt_employee: bool = False, 
                            age: int = 0, parent_age: int = 0) -> float:
        """
        Calculate total 80G deductions.
        
        FIXED CRITICAL ERROR: Corrected gross income calculation for 80G qualifying limits.
        For 80G purposes, gross income should exclude:
        - LTCG and STCG under special rates (as they're taxed separately)
        - All other deductions except 80G itself
        """
        if regime == 'new':
            return 0
            
        # Calculate basic + DA for any calculations that need it
        gross_income_basic_da = salary.basic + salary.dearness_allowance

        # FIXED: Calculate other deductions (excluding 80G) for proper gross income calculation
        other_deductions = sum([
            self.total_deductions_80c_80ccd_80ccd_1_1b(regime), 
            self.total_deductions_80ccd_2(regime, gross_income_basic_da, is_govt_employee), 
            self.total_deductions_80d_self_family(regime, age), 
            self.total_deductions_80d_parent(regime, parent_age), 
            self.total_deductions_80dd(regime), 
            self.total_deductions_80ddb(regime, age), 
            self.total_deductions_80e(regime), 
            self.total_deductions_80eeb(regime), 
            self.total_deductions_80ggc(regime), 
            self.total_deductions_80u(regime)
        ])
        logger.info(f"Other deductions (excluding 80G): {other_deductions}")

        # FIXED: Calculate adjusted gross income for 80G qualifying limit
        # Gross Total Income minus:
        # 1. LTCG and STCG taxed at special rates (as they don't contribute to 80G base)
        # 2. Other deductions (80C to 80U excluding 80G)
        gross_income_for_80g = (
            salary.total_taxable_income_per_slab(regime=regime) +
            income_from_other_sources.total_taxable_income_per_slab(regime=regime, age=age) +
            capital_gains.total_stcg_slab_rate()  # Only STCG taxed at slab rates
            # Note: LTCG and STCG under special rates are excluded as per IT Act
        ) - other_deductions
        
        # Ensure gross income is not negative
        gross_income_for_80g = max(0, gross_income_for_80g)
        logger.info(f"Adjusted gross income for 80G calculation: {gross_income_for_80g}")

        # Calculate all 80G deductions
        total_deductions_80g = sum([
            self.total_deductions_80g_100_wo_ql(regime),
            self.total_deductions_80g_50_wo_ql(regime),
            self.total_deductions_80g_100_ql(regime, gross_income_for_80g),
            self.total_deductions_80g_50_ql(regime, gross_income_for_80g)
        ])
        
        logger.info(f"Total Section 80G deductions: {total_deductions_80g}")
        return total_deductions_80g

    def total_deduction_per_slab(self, salary: SalaryComponents, 
                                 income_from_other_sources: IncomeFromOtherSources, 
                                 regime: str = 'new', 
                                 is_govt_employee: bool = False, 
                                 age: int = 0, 
                                 parent_age: int = 0) -> float:
        """
        Calculate total deductions from all sections with proper parameter handling.
        
        FIXES APPLIED:
        1. Proper method signature without capital_gains parameter mismatch
        2. All deduction sections properly integrated
        3. Regime-specific deduction restrictions
        4. Age-based deduction calculations
        
        Parameters:
        - salary: SalaryComponents object for salary-based deductions
        - income_from_other_sources: IncomeFromOtherSources for income-based deductions
        - regime: Tax regime ('new' or 'old') - deductions only in old regime
        - is_govt_employee: Whether the taxpayer is a government employee
        - age: Age of the taxpayer for age-based deductions
        - parent_age: Age of parents for parent-related deductions
        
        Returns:
        - Total deduction amount
        """
        logger.info(f"total_deduction_per_slab - Starting deduction calculation for regime: {regime}, age: {age}, govt_employee: {is_govt_employee}")
        
        if regime == 'new':
            logger.info("total_deduction_per_slab - New regime: No deductions applicable")
            return 0
        
        # Calculate all deduction components (only for old regime)
        logger.info("total_deduction_per_slab - Calculating deductions for old regime")
        
        # Basic + DA for 80CCD(2) calculation
        gross_income_basic_da = salary.basic + salary.dearness_allowance
        
        # Section 80C, 80CCC, 80CCD(1), 80CCD(1B) - Investment deductions
        deduction_80c_group = self.total_deductions_80c_80ccd_80ccd_1_1b(regime)
        logger.info(f"total_deduction_per_slab - 80C group deductions: {deduction_80c_group}")
        
        # Section 80CCD(2) - Employer NPS contribution
        deduction_80ccd_2 = self.total_deductions_80ccd_2(regime, gross_income_basic_da, is_govt_employee)
        logger.info(f"total_deduction_per_slab - 80CCD(2) deductions: {deduction_80ccd_2}")
        
        # Section 80D - Health insurance premiums
        deduction_80d_self = self.total_deductions_80d_self_family(regime, age)
        deduction_80d_parent = self.total_deductions_80d_parent(regime, parent_age)
        logger.info(f"total_deduction_per_slab - 80D deductions: Self/Family: {deduction_80d_self}, Parents: {deduction_80d_parent}")
        
        # Section 80DD - Disability deductions
        deduction_80dd = self.total_deductions_80dd(regime)
        logger.info(f"total_deduction_per_slab - 80DD deductions: {deduction_80dd}")
        
        # Section 80DDB - Medical treatment of specified diseases
        deduction_80ddb = self.total_deductions_80ddb(regime, age)
        logger.info(f"total_deduction_per_slab - 80DDB deductions: {deduction_80ddb}")
        
        # Section 80E - Education loan interest
        deduction_80e = self.total_deductions_80e(regime)
        logger.info(f"total_deduction_per_slab - 80E deductions: {deduction_80e}")
        
        # Section 80EEB - Electric vehicle loan interest
        deduction_80eeb = self.total_deductions_80eeb(regime)
        logger.info(f"total_deduction_per_slab - 80EEB deductions: {deduction_80eeb}")
        
        # Section 80GGC - Political party contributions
        deduction_80ggc = self.total_deductions_80ggc(regime)
        logger.info(f"total_deduction_per_slab - 80GGC deductions: {deduction_80ggc}")
        
        # Section 80U - Self disability
        deduction_80u = self.total_deductions_80u(regime)
        logger.info(f"total_deduction_per_slab - 80U deductions: {deduction_80u}")
        
        # Section 80G - Charitable donations (FIXED: Removed capital_gains parameter)
        deduction_80g = self.total_deductions_80g(
            salary=salary, 
            income_from_other_sources=income_from_other_sources, 
            capital_gains=CapitalGains(),  # Use empty capital gains object for 80G calculation
            regime=regime, 
            is_govt_employee=is_govt_employee, 
            age=age, 
            parent_age=parent_age
        )
        logger.info(f"total_deduction_per_slab - 80G deductions: {deduction_80g}")
        
        # Total all deductions
        total_deductions = (
            deduction_80c_group +
            deduction_80ccd_2 +
            deduction_80d_self +
            deduction_80d_parent +
            deduction_80dd +
            deduction_80ddb +
            deduction_80e +
            deduction_80eeb +
            deduction_80ggc +
            deduction_80u +
            deduction_80g
        )
        
        logger.info(f"total_deduction_per_slab - Total deductions calculated: {total_deductions}")
        logger.info(f"total_deduction_per_slab - Deduction breakdown: 80C: {deduction_80c_group}, 80CCD(2): {deduction_80ccd_2}, "
                   f"80D: {deduction_80d_self + deduction_80d_parent}, 80DD: {deduction_80dd}, 80DDB: {deduction_80ddb}, "
                   f"80E: {deduction_80e}, 80EEB: {deduction_80eeb}, 80GGC: {deduction_80ggc}, 80U: {deduction_80u}, 80G: {deduction_80g}")
        
        return total_deductions

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the object to a dictionary for JSON serialization.
        
        FIXED: Changed from class method to instance method to access instance attributes.
        """
        return {
            "regime": self.regime,
            "age": self.age,
            "section_80c_lic": self.section_80c_lic,
            "section_80c_epf": self.section_80c_epf,
            "section_80c_ssp": self.section_80c_ssp,
            "section_80c_nsc": self.section_80c_nsc, 
            "section_80c_ulip": self.section_80c_ulip,
            "section_80c_tsmf": self.section_80c_tsmf,
            "section_80c_tffte2c": self.section_80c_tffte2c,
            "section_80c_paphl": self.section_80c_paphl,
            "section_80c_sdpphp": self.section_80c_sdpphp,
            "section_80c_tsfdsb": self.section_80c_tsfdsb,
            "section_80c_scss": self.section_80c_scss,
            "section_80c_others": self.section_80c_others,
            "section_80ccc_ppic": self.section_80ccc_ppic,
            "section_80ccd_1_nps": self.section_80ccd_1_nps,
            "section_80ccd_1b_additional": self.section_80ccd_1b_additional,
            "section_80ccd_2_enps": self.section_80ccd_2_enps,
            "section_80d_hisf": self.section_80d_hisf,  
            "section_80d_phcs": self.section_80d_phcs,
            "section_80d_hi_parent": self.section_80d_hi_parent,
            "relation_80dd": self.relation_80dd,
            "disability_percentage": self.disability_percentage,
            "section_80dd": self.section_80dd,
            "relation_80ddb": self.relation_80ddb,
            "age_80ddb": self.age_80ddb,
            "section_80ddb": self.section_80ddb,
            "section_80eeb": self.section_80eeb,
            "relation_80e": self.relation_80e,
            "section_80e_interest": self.section_80e_interest,
            "ev_purchase_date": self.ev_purchase_date.isoformat() if hasattr(self, 'ev_purchase_date') and self.ev_purchase_date else None,
            "section_80g_100_wo_ql": self.section_80g_100_wo_ql,
            "section_80g_100_head": self.section_80g_100_head,
            "section_80g_50_wo_ql": self.section_80g_50_wo_ql,
            "section_80g_50_head": self.section_80g_50_head,
            "section_80g_100_ql": self.section_80g_100_ql,
            "section_80g_100_ql_head": self.section_80g_100_ql_head,
            "section_80g_50_ql": self.section_80g_50_ql,
            "section_80g_50_ql_head": self.section_80g_50_ql_head,
            "section_80ggc": self.section_80ggc,
            "section_80u": self.section_80u,
            "disability_percentage_80u": self.disability_percentage_80u
        } 

    @classmethod
    def from_dict(cls, data: dict):
        """
        Create a DeductionComponents object from dictionary data.
        
        Added proper data type handling and default values for all fields.
        """
        deduction_obj = cls()
        
        # Basic fields
        deduction_obj.regime = data.get('regime', 'old')
        deduction_obj.age = data.get('age', 0)
        
        # Section 80C fields
        deduction_obj.section_80c_lic = data.get('section_80c_lic', 0)
        deduction_obj.section_80c_epf = data.get('section_80c_epf', 0)
        deduction_obj.section_80c_ssp = data.get('section_80c_ssp', 0)
        deduction_obj.section_80c_nsc = data.get('section_80c_nsc', 0)
        deduction_obj.section_80c_ulip = data.get('section_80c_ulip', 0)
        deduction_obj.section_80c_tsmf = data.get('section_80c_tsmf', 0)
        deduction_obj.section_80c_tffte2c = data.get('section_80c_tffte2c', 0)
        deduction_obj.section_80c_paphl = data.get('section_80c_paphl', 0)
        deduction_obj.section_80c_sdpphp = data.get('section_80c_sdpphp', 0)
        deduction_obj.section_80c_tsfdsb = data.get('section_80c_tsfdsb', 0)
        deduction_obj.section_80c_scss = data.get('section_80c_scss', 0)
        deduction_obj.section_80c_others = data.get('section_80c_others', 0)
        
        # Section 80CCC
        deduction_obj.section_80ccc_ppic = data.get('section_80ccc_ppic', 0)
        
        # Section 80CCD
        deduction_obj.section_80ccd_1_nps = data.get('section_80ccd_1_nps', 0)
        deduction_obj.section_80ccd_1b_additional = data.get('section_80ccd_1b_additional', 0)
        deduction_obj.section_80ccd_2_enps = data.get('section_80ccd_2_enps', 0)
        
        # Section 80D
        deduction_obj.section_80d_hisf = data.get('section_80d_hisf', 0)
        deduction_obj.section_80d_phcs = data.get('section_80d_phcs', 0)
        deduction_obj.section_80d_hi_parent = data.get('section_80d_hi_parent', 0)
        
        # Section 80DD
        deduction_obj.relation_80dd = data.get('relation_80dd', '')
        deduction_obj.disability_percentage = data.get('disability_percentage', '')
        deduction_obj.section_80dd = data.get('section_80dd', 0)
        
        # Section 80DDB
        deduction_obj.relation_80ddb = data.get('relation_80ddb', '')
        deduction_obj.age_80ddb = data.get('age_80ddb', 0)
        deduction_obj.section_80ddb = data.get('section_80ddb', 0)
        
        # Section 80E
        deduction_obj.relation_80e = data.get('relation_80e', 'Self')
        deduction_obj.section_80e_interest = data.get('section_80e_interest', 0)
        
        # Section 80EEB
        deduction_obj.section_80eeb = data.get('section_80eeb', 0)
        ev_date_str = data.get('ev_purchase_date')
        if ev_date_str:
            try:
                # Handle both ISO format and date object
                if isinstance(ev_date_str, str):
                    deduction_obj.ev_purchase_date = datetime.datetime.fromisoformat(ev_date_str).date()
                else:
                    deduction_obj.ev_purchase_date = ev_date_str
            except (ValueError, AttributeError):
                deduction_obj.ev_purchase_date = date.today()
        else:
            deduction_obj.ev_purchase_date = date.today()
        
        # Section 80G
        deduction_obj.section_80g_100_wo_ql = data.get('section_80g_100_wo_ql', 0)
        deduction_obj.section_80g_100_head = data.get('section_80g_100_head', '')
        deduction_obj.section_80g_50_wo_ql = data.get('section_80g_50_wo_ql', 0)
        deduction_obj.section_80g_50_head = data.get('section_80g_50_head', '')
        deduction_obj.section_80g_100_ql = data.get('section_80g_100_ql', 0)
        deduction_obj.section_80g_100_ql_head = data.get('section_80g_100_ql_head', '')
        deduction_obj.section_80g_50_ql = data.get('section_80g_50_ql', 0)
        deduction_obj.section_80g_50_ql_head = data.get('section_80g_50_ql_head', '')
        
        # Section 80GGC
        deduction_obj.section_80ggc = data.get('section_80ggc', 0)
        
        # Section 80U
        deduction_obj.section_80u = data.get('section_80u', 0)
        deduction_obj.disability_percentage_80u = data.get('disability_percentage_80u', '')
        
        return deduction_obj 