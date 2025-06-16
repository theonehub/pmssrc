"""
Tax Deductions Entity
Domain entity for handling various tax deduction sections
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import date
from enum import Enum

from app.domain.value_objects.money import Money
from app.domain.value_objects.tax_regime import TaxRegime, TaxRegimeType


class DisabilityPercentage(Enum):
    """Disability percentage categories for tax deductions."""
    MODERATE = "Between 40%-80%"
    SEVERE = "80%+"
    SEVERE_DETAILED = "More than 80%"


class RelationType(Enum):
    """Relationship types for dependent deductions."""
    SELF = "Self"
    SPOUSE = "Spouse"
    CHILD = "Child"
    PARENTS = "Parents"
    SIBLING = "Sibling"


@dataclass
class DeductionSection80C:
    """Section 80C deductions with validation and limits."""
    
    life_insurance_premium: Money = Money.zero()
    epf_contribution: Money = Money.zero()
    ppf_contribution: Money = Money.zero()
    nsc_investment: Money = Money.zero()
    tax_saving_fd: Money = Money.zero()
    elss_investment: Money = Money.zero()
    home_loan_principal: Money = Money.zero()
    tuition_fees: Money = Money.zero()
    ulip_premium: Money = Money.zero()
    sukanya_samriddhi: Money = Money.zero()
    stamp_duty_property: Money = Money.zero()
    senior_citizen_savings: Money = Money.zero()
    other_80c_investments: Money = Money.zero()
    
    def calculate_total_investment(self) -> Money:
        """Calculate total Section 80C investments."""
        return (self.life_insurance_premium
                .add(self.epf_contribution)
                .add(self.ppf_contribution)
                .add(self.nsc_investment)
                .add(self.tax_saving_fd)
                .add(self.elss_investment)
                .add(self.home_loan_principal)
                .add(self.tuition_fees)
                .add(self.ulip_premium)
                .add(self.sukanya_samriddhi)
                .add(self.stamp_duty_property)
                .add(self.senior_citizen_savings)
                .add(self.other_80c_investments))
    
    def calculate_eligible_deduction(self, regime: TaxRegime) -> Money:
        """
        Calculate eligible 80C deduction.
        
        Args:
            regime: Tax regime
            
        Returns:
            Money: Eligible deduction amount
        """
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        total_investment = self.calculate_total_investment()
        
        # Maximum limit is ₹1.5 lakh
        max_limit = Money.from_int(150000)
        return total_investment.min(max_limit)
    
    def get_investment_breakdown(self) -> Dict[str, float]:
        """Get breakdown of investments."""
        return {
            "life_insurance_premium": self.life_insurance_premium.to_float(),
            "epf_contribution": self.epf_contribution.to_float(),
            "ppf_contribution": self.ppf_contribution.to_float(),
            "nsc_investment": self.nsc_investment.to_float(),
            "tax_saving_fd": self.tax_saving_fd.to_float(),
            "elss_investment": self.elss_investment.to_float(),
            "home_loan_principal": self.home_loan_principal.to_float(),
            "tuition_fees": self.tuition_fees.to_float(),
            "ulip_premium": self.ulip_premium.to_float(),
            "sukanya_samriddhi": self.sukanya_samriddhi.to_float(),
            "stamp_duty_property": self.stamp_duty_property.to_float(),
            "senior_citizen_savings": self.senior_citizen_savings.to_float(),
            "other_investments": self.other_80c_investments.to_float(),
            "total_invested": self.calculate_total_investment().to_float()
        }
    
    def get_remaining_limit(self) -> Money:
        """Get remaining investment limit for 80C."""
        max_limit = Money.from_int(150000)
        invested = self.calculate_total_investment()
        
        if invested.is_greater_than(max_limit):
            return Money.zero()
        
        return max_limit.subtract(invested)


@dataclass
class DeductionSection80CCC:
    """Section 80CCC - Pension Fund contributions."""
    
    pension_fund_contribution: Money = Money.zero()
    
    def calculate_eligible_deduction(self, regime: TaxRegime) -> Money:
        """Calculate Section 80CCC deduction (combined with 80C limit)."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        # This is part of the combined 80C + 80CCC + 80CCD(1) limit of ₹1.5 lakh
        return self.pension_fund_contribution


@dataclass
class DeductionSection80CCD:
    """Section 80CCD - NPS contributions."""
    
    # 80CCD(1) - Employee NPS contribution (part of 80C limit)
    employee_nps_contribution: Money = Money.zero()
    
    # 80CCD(1B) - Additional NPS contribution (separate ₹50,000 limit)
    additional_nps_contribution: Money = Money.zero()
    
    # 80CCD(2) - Employer NPS contribution
    employer_nps_contribution: Money = Money.zero()

    # basic_salary: Money = Money.zero()
    # dearness_allowance: Money = Money.zero()
    # is_government_employee: bool = False
    
    def calculate_80ccd_1_deduction(self) -> Money:
        """Calculate 80CCD(1) deduction (part of 80C limit)."""
        
        return self.employee_nps_contribution
    
    def calculate_80ccd_1b_deduction(self) -> Money:
        """Calculate 80CCD(1B) deduction (additional ₹50,000)."""
        
        max_limit = Money.from_int(50000)
        return self.additional_nps_contribution.min(max_limit)
    
    #TODO: Need to if its basic_plus_da or gross salary
    def calculate_80ccd_2_deduction(self, basic_plus_da: Money, is_government_employee: bool) -> Money:
        """Calculate 80CCD(2) deduction (employer contribution)."""
        
        if is_government_employee:
            max_cap = basic_plus_da.percentage(14)  # 14% for government
        else:
            max_cap = basic_plus_da.percentage(10)  # 10% for private
        
        return self.employer_nps_contribution.min(max_cap)
    
    def calculate_eligible_deduction(self, regime: TaxRegime, basic_plus_da: Money, is_government_employee: bool) -> Money:
        """Calculate eligible 80CCD deduction."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        return self.calculate_80ccd_1_deduction().add(self.calculate_80ccd_1b_deduction()).add(self.calculate_80ccd_2_deduction(basic_plus_da, is_government_employee))


@dataclass  
class DeductionSection80D:
    """Health insurance deductions under Section 80D."""
    
    self_family_premium: Money = Money.zero()
    parent_premium: Money = Money.zero()
    preventive_health_checkup: Money = Money.zero()  #For self and family only, not for parent
    parent_age: int = 55

    
    #TODO: Check age of employee is valid if insurance is taken for family person
    def calculate_self_family_limit(self) -> Money:
        """Calculate limit for self and family premium."""
        if self.employee_age >= 60:
            return Money.from_int(50000)  # ₹50,000 for senior citizens
        else:
            return Money.from_int(25000)  # ₹25,000 for others
    
    def calculate_parent_limit(self) -> Money:
        """Calculate limit for parent premium."""
        if self.parent_age >= 60:
            return Money.from_int(50000)  # ₹50,000 for senior citizen parents
        else:
            return Money.from_int(25000)  # ₹25,000 for others
    
    def calculate_eligible_deduction(self, regime: TaxRegime, employee_age: int) -> Money:
        """
        Calculate eligible 80D deduction.
        
        Args:
            regime: Tax regime
            
        Returns:
            Money: Eligible deduction amount
        """
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        # Self and family deduction
        self_family_limit = self.calculate_self_family_limit(employee_age)
        self_family_deduction = self.self_family_premium.min(self_family_limit)
        
        # Parent deduction
        parent_limit = self.calculate_parent_limit()
        parent_deduction = self.parent_premium.min(parent_limit)
        
        # Preventive health checkup (max ₹5,000 and within above limits)
        preventive_limit = Money.from_int(5000)
        preventive_deduction = self.preventive_health_checkup.min(preventive_limit)
        
        # Total deduction (preventive is additional)
        total_deduction = self_family_deduction.add(parent_deduction).add(preventive_deduction)
        
        return total_deduction
    
    def get_deduction_breakdown(self, regime: TaxRegime) -> Dict[str, Any]:
        """Get detailed breakdown of 80D deductions."""
        return {
            "self_family": {
                "premium_paid": self.self_family_premium.to_float(),
                "limit": self.calculate_self_family_limit().to_float(),
                "eligible_deduction": self.self_family_premium.min(self.calculate_self_family_limit()).to_float()
            },
            "parent": {
                "premium_paid": self.parent_premium.to_float(),
                "limit": self.calculate_parent_limit().to_float(),
                "eligible_deduction": self.parent_premium.min(self.calculate_parent_limit()).to_float()
            },
            "preventive_checkup": {
                "amount_paid": self.preventive_health_checkup.to_float(),
                "limit": 5000.0,
                "eligible_deduction": self.preventive_health_checkup.min(Money.from_int(5000)).to_float()
            },
            "total_eligible": self.calculate_eligible_deduction(regime).to_float()
        }


@dataclass
class DeductionSection80DD:
    """Section 80DD - Disability (Dependent)."""
    
    relation: RelationType
    disability_percentage: DisabilityPercentage

    #TODO: Need to prompt user to fill form Medical Certificate, Form 10-IA, Self-Declaration Certificate and Receipts of Insurance Premium Paid
    def calculate_eligible_deduction(self, regime: TaxRegime) -> Money:
        """Calculate Section 80DD deduction."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        if self.relation not in [RelationType.SPOUSE, RelationType.CHILD, 
                                RelationType.PARENTS, RelationType.SIBLING]:
            return Money.zero()
        
        if self.disability_percentage == DisabilityPercentage.MODERATE:
            return Money.from_int(75000)
        elif self.disability_percentage in [DisabilityPercentage.SEVERE, DisabilityPercentage.SEVERE_DETAILED]:
            return Money.from_int(125000)
        
        return Money.zero()


@dataclass
class DeductionSection80DDB:
    """Section 80DDB - Medical Treatment (Specified Diseases)."""
    
    dependent_age: int
    medical_expenses: Money = Money.zero()
    relation: RelationType = RelationType.SELF
    
    def calculate_eligible_deduction(self, regime: TaxRegime) -> Money:
        """Calculate Section 80DDB deduction."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        if self.relation not in [RelationType.SELF, RelationType.SPOUSE, RelationType.CHILD,
                                RelationType.PARENTS, RelationType.SIBLING]:
            return Money.zero()
        
        relevant_age = self.age if self.relation == RelationType.SELF else self.dependent_age
        
        if relevant_age < 60:
            max_limit = Money.from_int(40000)
        else:
            max_limit = Money.from_int(100000)
        
        return self.medical_expenses.min(max_limit)


@dataclass
class DeductionSection80E:
    """Section 80E - Education Loan Interest."""
    
    education_loan_interest: Money = Money.zero()
    relation: RelationType = RelationType.SELF
    
    def calculate_eligible_deduction(self, regime: TaxRegime) -> Money:
        """Calculate Section 80E deduction (no upper limit)."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        if self.relation not in [RelationType.SELF, RelationType.SPOUSE, RelationType.CHILD]:
            return Money.zero()
        
        return self.education_loan_interest


@dataclass
class DeductionSection80EEB:
    """Section 80EEB - Electric Vehicle Loan Interest."""
    
    ev_loan_interest: Money = Money.zero()
    ev_purchase_date: Optional[date] = None
    
    def calculate_eligible_deduction(self, regime: TaxRegime) -> Money:
        """Calculate Section 80EEB deduction."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        if self.ev_purchase_date is None:
            return Money.zero()
        
        # Check if purchase date is within eligible period
        if (self.ev_purchase_date >= date(2019, 4, 1) and 
            self.ev_purchase_date <= date(2025, 3, 31)):
            max_limit = Money.from_int(150000)
            return self.ev_loan_interest.min(max_limit)
        
        return Money.zero()


@dataclass
class DeductionSection80G:
    """Section 80G - Charitable Donations with specific donation heads."""
    
    # 100% deduction without qualifying limit - Specific heads
    pm_relief_fund: Money = Money.zero()
    national_defence_fund: Money = Money.zero()
    national_foundation_communal_harmony: Money = Money.zero()
    zila_saksharta_samiti: Money = Money.zero()
    national_illness_assistance_fund: Money = Money.zero()
    national_blood_transfusion_council: Money = Money.zero()
    national_trust_autism_fund: Money = Money.zero()
    national_sports_fund: Money = Money.zero()
    national_cultural_fund: Money = Money.zero()
    technology_development_fund: Money = Money.zero()
    national_children_fund: Money = Money.zero()
    cm_relief_fund: Money = Money.zero()
    army_naval_air_force_funds: Money = Money.zero()
    swachh_bharat_kosh: Money = Money.zero()
    clean_ganga_fund: Money = Money.zero()
    drug_abuse_control_fund: Money = Money.zero()
    other_100_percent_wo_limit: Money = Money.zero()
    
    # 50% deduction without qualifying limit - Specific heads
    jn_memorial_fund: Money = Money.zero()
    pm_drought_relief: Money = Money.zero()
    indira_gandhi_memorial_trust: Money = Money.zero()
    rajiv_gandhi_foundation: Money = Money.zero()
    other_50_percent_wo_limit: Money = Money.zero()
    
    # 100% deduction with qualifying limit (10% of income) - Specific heads
    family_planning_donation: Money = Money.zero()
    indian_olympic_association: Money = Money.zero()
    other_100_percent_w_limit: Money = Money.zero()
    
    # 50% deduction with qualifying limit (10% of income) - Specific heads
    govt_charitable_donations: Money = Money.zero()
    housing_authorities_donations: Money = Money.zero()
    religious_renovation_donations: Money = Money.zero()
    other_charitable_donations: Money = Money.zero()
    other_50_percent_w_limit: Money = Money.zero()
    
    def calculate_category_1_deduction(self) -> Money:
        """Calculate 100% deduction without qualifying limit."""
        return (self.pm_relief_fund
                .add(self.national_defence_fund)
                .add(self.national_foundation_communal_harmony)
                .add(self.zila_saksharta_samiti)
                .add(self.national_illness_assistance_fund)
                .add(self.national_blood_transfusion_council)
                .add(self.national_trust_autism_fund)
                .add(self.national_sports_fund)
                .add(self.national_cultural_fund)
                .add(self.technology_development_fund)
                .add(self.national_children_fund)
                .add(self.cm_relief_fund)
                .add(self.army_naval_air_force_funds)
                .add(self.swachh_bharat_kosh)
                .add(self.clean_ganga_fund)
                .add(self.drug_abuse_control_fund)
                .add(self.other_100_percent_wo_limit))
    
    def calculate_category_2_deduction(self) -> Money:
        """Calculate 50% deduction without qualifying limit."""
        total_donations = (self.jn_memorial_fund
                          .add(self.pm_drought_relief)
                          .add(self.indira_gandhi_memorial_trust)
                          .add(self.rajiv_gandhi_foundation)
                          .add(self.other_50_percent_wo_limit))
        return total_donations.percentage(50)
    
    def calculate_category_3_deduction(self, gross_income: Money) -> Money:
        """Calculate 100% deduction with qualifying limit."""
        total_donations = (self.family_planning_donation
                          .add(self.indian_olympic_association)
                          .add(self.other_100_percent_w_limit))
        qualifying_limit = gross_income.percentage(10)
        return total_donations.min(qualifying_limit)
    
    def calculate_category_4_deduction(self, gross_income: Money) -> Money:
        """Calculate 50% deduction with qualifying limit."""
        total_donations = (self.govt_charitable_donations
                          .add(self.housing_authorities_donations)
                          .add(self.religious_renovation_donations)
                          .add(self.other_charitable_donations)
                          .add(self.other_50_percent_w_limit))
        deduction_50_percent = total_donations.percentage(50)
        qualifying_limit = gross_income.percentage(10)
        return deduction_50_percent.min(qualifying_limit)
    
    def calculate_eligible_deduction(self, regime: TaxRegime, gross_income: Money) -> Money:
        """Calculate total Section 80G deduction."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        category_1 = self.calculate_category_1_deduction()
        category_2 = self.calculate_category_2_deduction()
        category_3 = self.calculate_category_3_deduction(gross_income)
        category_4 = self.calculate_category_4_deduction(gross_income)
        
        return category_1.add(category_2).add(category_3).add(category_4)
    
    def get_donation_breakdown(self, regime: TaxRegime) -> Dict[str, Any]:
        """Get detailed breakdown of 80G donations."""
        if regime.regime_type == TaxRegimeType.NEW:
            return {
                "regime": "New",
                "message": "No charitable donation deductions allowed in new regime",
                "total_deduction": 0.0
            }
        
        qualifying_limit = self.gross_income.percentage(10)
        
        return {
            "regime": "Old",
            "qualifying_limit": qualifying_limit.to_float(),
            "category_1_100_percent_no_limit": {
                "donations": {
                    "pm_relief_fund": self.pm_relief_fund.to_float(),
                    "national_defence_fund": self.national_defence_fund.to_float(),
                    "national_foundation_communal_harmony": self.national_foundation_communal_harmony.to_float(),
                    "cm_relief_fund": self.cm_relief_fund.to_float(),
                    "swachh_bharat_kosh": self.swachh_bharat_kosh.to_float(),
                    "clean_ganga_fund": self.clean_ganga_fund.to_float(),
                    "other_eligible_funds": self.other_100_percent_wo_limit.to_float()
                },
                "total_donated": self.calculate_category_1_deduction().to_float(),
                "eligible_deduction": self.calculate_category_1_deduction().to_float()
            },
            "category_2_50_percent_no_limit": {
                "donations": {
                    "jn_memorial_fund": self.jn_memorial_fund.to_float(),
                    "pm_drought_relief": self.pm_drought_relief.to_float(),
                    "indira_gandhi_memorial_trust": self.indira_gandhi_memorial_trust.to_float(),
                    "rajiv_gandhi_foundation": self.rajiv_gandhi_foundation.to_float(),
                    "other_eligible_funds": self.other_50_percent_wo_limit.to_float()
                },
                "total_donated": (self.jn_memorial_fund.add(self.pm_drought_relief)
                                 .add(self.indira_gandhi_memorial_trust)
                                 .add(self.rajiv_gandhi_foundation)
                                 .add(self.other_50_percent_wo_limit)).to_float(),
                "eligible_deduction": self.calculate_category_2_deduction().to_float()
            },
            "category_3_100_percent_with_limit": {
                "donations": {
                    "family_planning_donation": self.family_planning_donation.to_float(),
                    "indian_olympic_association": self.indian_olympic_association.to_float(),
                    "other_eligible_donations": self.other_100_percent_w_limit.to_float()
                },
                "total_donated": (self.family_planning_donation
                                 .add(self.indian_olympic_association)
                                 .add(self.other_100_percent_w_limit)).to_float(),
                "eligible_deduction": self.calculate_category_3_deduction().to_float()
            },
            "category_4_50_percent_with_limit": {
                "donations": {
                    "govt_charitable_donations": self.govt_charitable_donations.to_float(),
                    "housing_authorities": self.housing_authorities_donations.to_float(),
                    "religious_renovation": self.religious_renovation_donations.to_float(),
                    "other_charitable": self.other_charitable_donations.to_float(),
                    "other_eligible": self.other_50_percent_w_limit.to_float()
                },
                "total_donated": (self.govt_charitable_donations
                                 .add(self.housing_authorities_donations)
                                 .add(self.religious_renovation_donations)
                                 .add(self.other_charitable_donations)
                                 .add(self.other_50_percent_w_limit)).to_float(),
                "eligible_deduction": self.calculate_category_4_deduction().to_float()
            },
            "summary": {
                "total_donations": self.calculate_total_donations().to_float(),
                "total_eligible_deduction": self.calculate_eligible_deduction(regime).to_float(),
                "tax_saving_potential": self.calculate_eligible_deduction(regime).percentage(30).to_float()
            }
        }
    
    def calculate_total_donations(self) -> Money:
        """Calculate total donations made across all categories."""
        return (self.calculate_category_1_deduction()
                .add(self.jn_memorial_fund)
                .add(self.pm_drought_relief)
                .add(self.indira_gandhi_memorial_trust)
                .add(self.rajiv_gandhi_foundation)
                .add(self.other_50_percent_wo_limit)
                .add(self.family_planning_donation)
                .add(self.indian_olympic_association)
                .add(self.other_100_percent_w_limit)
                .add(self.govt_charitable_donations)
                .add(self.housing_authorities_donations)
                .add(self.religious_renovation_donations)
                .add(self.other_charitable_donations)
                .add(self.other_50_percent_w_limit))
    
    


@dataclass
class DeductionSection80GGC:
    """Section 80GGC - Political Party Contributions."""
    
    political_party_contribution: Money = Money.zero()
    
    def calculate_eligible_deduction(self, regime: TaxRegime) -> Money:
        """Calculate Section 80GGC deduction (no upper limit)."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        # No upper limit, but no cash payments allowed (validation should be at input level)
        return self.political_party_contribution


@dataclass
class DeductionSection80U:
    """Section 80U - Self Disability."""
    
    disability_percentage: DisabilityPercentage
    
    def calculate_eligible_deduction(self, regime: TaxRegime) -> Money:
        """Calculate Section 80U deduction."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        if self.disability_percentage == DisabilityPercentage.MODERATE:
            return Money.from_int(75000)
        elif self.disability_percentage in [DisabilityPercentage.SEVERE, DisabilityPercentage.SEVERE_DETAILED]:
            return Money.from_int(125000)
        
        return Money.zero()


@dataclass
class DeductionSection80TTA_TTB:
    """Section 80TTA/80TTB - Interest Income Exemptions."""
    
    savings_interest: Money = Money.zero()
    fd_interest: Money = Money.zero()
    rd_interest: Money = Money.zero()
    other_bank_interest: Money = Money.zero()
    age: int = 25
    
    def calculate_eligible_exemption(self, regime: TaxRegime) -> Money:
        """Calculate Section 80TTA/80TTB exemption."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        if self.age >= 60:
            # Section 80TTB - All bank interest up to Rs. 50,000
            total_interest = (self.savings_interest
                            .add(self.fd_interest)
                            .add(self.rd_interest)
                            .add(self.other_bank_interest))
            max_limit = Money.from_int(50000)
            return total_interest.min(max_limit)
        else:
            # Section 80TTA - Only savings interest up to Rs. 10,000
            max_limit = Money.from_int(10000)
            return self.savings_interest.min(max_limit)
    
    def get_exemption_breakdown(self, regime: TaxRegime) -> Dict[str, Any]:
        """Get breakdown of interest exemption."""
        if self.age >= 60:
            section = "80TTB"
            eligible_interest = (self.savings_interest
                               .add(self.fd_interest)
                               .add(self.rd_interest)
                               .add(self.other_bank_interest))
            limit = 50000
        else:
            section = "80TTA"
            eligible_interest = self.savings_interest
            limit = 10000
        
        return {
            "applicable_section": section,
            "savings_interest": self.savings_interest.to_float(),
            "fd_interest": self.fd_interest.to_float(),
            "rd_interest": self.rd_interest.to_float(),
            "other_bank_interest": self.other_bank_interest.to_float(),
            "total_interest": eligible_interest.to_float(),
            "exemption_limit": limit,
            "eligible_exemption": self.calculate_eligible_exemption(regime).to_float()
        }


@dataclass
class OtherDeductions:
    """Other miscellaneous deductions."""
    
    education_loan_interest: Money = Money.zero()
    charitable_donations: Money = Money.zero()
    savings_interest: Money = Money.zero()
    nps_contribution: Money = Money.zero()
    other_deductions: Money = Money.zero()
    
    def calculate_total(self) -> Money:
        """Calculate total other deductions."""
        return (self.education_loan_interest
                .add(self.charitable_donations)
                .add(self.savings_interest)
                .add(self.nps_contribution)
                .add(self.other_deductions))
    
    def get_breakdown(self) -> Dict[str, float]:
        """Get breakdown of other deductions."""
        return {
            "education_loan_interest": self.education_loan_interest.to_float(),
            "charitable_donations": self.charitable_donations.to_float(),
            "savings_interest": self.savings_interest.to_float(),
            "nps_contribution": self.nps_contribution.to_float(),
            "other_deductions": self.other_deductions.to_float(),
            "total": self.calculate_total().to_float()
        }


@dataclass
class TaxDeductions:
    """Complete tax deductions entity with all sections."""
    
    # Main deduction sections
    section_80c: Optional[DeductionSection80C] = None
    section_80ccc: Optional[DeductionSection80CCC] = None
    section_80ccd: Optional[DeductionSection80CCD] = None
    section_80d: Optional[DeductionSection80D] = None
    section_80dd: Optional[DeductionSection80DD] = None
    section_80ddb: Optional[DeductionSection80DDB] = None
    section_80e: Optional[DeductionSection80E] = None
    section_80eeb: Optional[DeductionSection80EEB] = None
    section_80g: Optional[DeductionSection80G] = None
    section_80ggc: Optional[DeductionSection80GGC] = None
    section_80u: Optional[DeductionSection80U] = None
    section_80tta_ttb: Optional[DeductionSection80TTA_TTB] = None
    other_deductions: Optional[OtherDeductions] = None
    
    def __post_init__(self):
        """Initialize default sections if not provided."""
        if self.section_80c is None:
            self.section_80c = DeductionSection80C()
        if self.section_80ccc is None:
            self.section_80ccc = DeductionSection80CCC()
        if self.section_80ccd is None:
            self.section_80ccd = DeductionSection80CCD()
        if self.section_80d is None:
            self.section_80d = DeductionSection80D()
        if self.other_deductions is None:
            self.other_deductions = OtherDeductions()
    
    # Backward compatibility properties for legacy code
    
    # Section 80C backward compatibility
    @property
    def life_insurance_premium(self) -> Money:
        return self.section_80c.life_insurance_premium if self.section_80c else Money.zero()
    
    @life_insurance_premium.setter
    def life_insurance_premium(self, value: Money):
        if self.section_80c is None:
            self.section_80c = DeductionSection80C()
        self.section_80c.life_insurance_premium = value
    
    @property
    def elss_investments(self) -> Money:
        return self.section_80c.elss_investment if self.section_80c else Money.zero()
    
    @elss_investments.setter
    def elss_investments(self, value: Money):
        if self.section_80c is None:
            self.section_80c = DeductionSection80C()
        self.section_80c.elss_investment = value
    
    @property
    def public_provident_fund(self) -> Money:
        return self.section_80c.ppf_contribution if self.section_80c else Money.zero()
    
    @public_provident_fund.setter
    def public_provident_fund(self, value: Money):
        if self.section_80c is None:
            self.section_80c = DeductionSection80C()
        self.section_80c.ppf_contribution = value
    
    @property
    def employee_provident_fund(self) -> Money:
        return self.section_80c.epf_contribution if self.section_80c else Money.zero()
    
    @employee_provident_fund.setter
    def employee_provident_fund(self, value: Money):
        if self.section_80c is None:
            self.section_80c = DeductionSection80C()
        self.section_80c.epf_contribution = value
    
    @property
    def sukanya_samriddhi(self) -> Money:
        return self.section_80c.sukanya_samriddhi if self.section_80c else Money.zero()
    
    @sukanya_samriddhi.setter
    def sukanya_samriddhi(self, value: Money):
        if self.section_80c is None:
            self.section_80c = DeductionSection80C()
        self.section_80c.sukanya_samriddhi = value
    
    @property
    def national_savings_certificate(self) -> Money:
        return self.section_80c.nsc_investment if self.section_80c else Money.zero()
    
    @national_savings_certificate.setter
    def national_savings_certificate(self, value: Money):
        if self.section_80c is None:
            self.section_80c = DeductionSection80C()
        self.section_80c.nsc_investment = value
    
    @property
    def tax_saving_fixed_deposits(self) -> Money:
        return self.section_80c.tax_saving_fd if self.section_80c else Money.zero()
    
    @tax_saving_fixed_deposits.setter
    def tax_saving_fixed_deposits(self, value: Money):
        if self.section_80c is None:
            self.section_80c = DeductionSection80C()
        self.section_80c.tax_saving_fd = value
    
    @property
    def principal_repayment_home_loan(self) -> Money:
        return self.section_80c.home_loan_principal if self.section_80c else Money.zero()
    
    @principal_repayment_home_loan.setter
    def principal_repayment_home_loan(self, value: Money):
        if self.section_80c is None:
            self.section_80c = DeductionSection80C()
        self.section_80c.home_loan_principal = value
    
    @property
    def tuition_fees(self) -> Money:
        return self.section_80c.tuition_fees if self.section_80c else Money.zero()
    
    @tuition_fees.setter
    def tuition_fees(self, value: Money):
        if self.section_80c is None:
            self.section_80c = DeductionSection80C()
        self.section_80c.tuition_fees = value
    
    @property
    def other_80c_deductions(self) -> Money:
        return self.section_80c.other_80c_investments if self.section_80c else Money.zero()
    
    @other_80c_deductions.setter
    def other_80c_deductions(self, value: Money):
        if self.section_80c is None:
            self.section_80c = DeductionSection80C()
        self.section_80c.other_80c_investments = value
    
    # Section 80D backward compatibility
    @property
    def health_insurance_self(self) -> Money:
        return self.section_80d.self_family_premium if self.section_80d else Money.zero()
    
    @health_insurance_self.setter
    def health_insurance_self(self, value: Money):
        if self.section_80d is None:
            self.section_80d = DeductionSection80D()
        self.section_80d.self_family_premium = value
    
    @property
    def health_insurance_parents(self) -> Money:
        return self.section_80d.parent_premium if self.section_80d else Money.zero()
    
    @health_insurance_parents.setter
    def health_insurance_parents(self, value: Money):
        if self.section_80d is None:
            self.section_80d = DeductionSection80D()
        self.section_80d.parent_premium = value
    
    @property
    def preventive_health_checkup(self) -> Money:
        return self.section_80d.preventive_health_checkup if self.section_80d else Money.zero()
    
    @preventive_health_checkup.setter
    def preventive_health_checkup(self, value: Money):
        if self.section_80d is None:
            self.section_80d = DeductionSection80D()
        self.section_80d.preventive_health_checkup = value
    
    # Section 80E backward compatibility
    @property
    def education_loan_interest(self) -> Money:
        return self.section_80e.education_loan_interest if self.section_80e else Money.zero()
    
    @education_loan_interest.setter
    def education_loan_interest(self, value: Money):
        if self.section_80e is None:
            self.section_80e = DeductionSection80E()
        self.section_80e.education_loan_interest = value
    
    # Section 80G backward compatibility
    @property
    def donations_80g(self) -> Money:
        if self.section_80g:
            return (self.section_80g.pm_relief_fund
                   .add(self.section_80g.national_defence_fund)
                   .add(self.section_80g.cm_relief_fund)
                   .add(self.section_80g.govt_charitable_donations)
                   .add(self.section_80g.other_charitable_donations))
        return Money.zero()
    
    @donations_80g.setter
    def donations_80g(self, value: Money):
        if self.section_80g is None:
            self.section_80g = DeductionSection80G()
        self.section_80g.other_charitable_donations = value
    
    # Section 80TTA/TTB backward compatibility
    @property
    def savings_account_interest(self) -> Money:
        return self.section_80tta_ttb.savings_interest if self.section_80tta_ttb else Money.zero()
    
    @savings_account_interest.setter
    def savings_account_interest(self, value: Money):
        if self.section_80tta_ttb is None:
            self.section_80tta_ttb = DeductionSection80TTA_TTB()
        self.section_80tta_ttb.savings_interest = value
    
    @property
    def senior_citizen_interest(self) -> Money:
        if self.section_80tta_ttb:
            return (self.section_80tta_ttb.fd_interest
                   .add(self.section_80tta_ttb.rd_interest)
                   .add(self.section_80tta_ttb.other_bank_interest))
        return Money.zero()
    
    @senior_citizen_interest.setter
    def senior_citizen_interest(self, value: Money):
        if self.section_80tta_ttb is None:
            self.section_80tta_ttb = DeductionSection80TTA_TTB()
        self.section_80tta_ttb.other_bank_interest = value
    
    # Section 80U/80DD backward compatibility
    @property
    def disability_deduction(self) -> Money:
        if self.section_80u:
            return Money.from_int(75000) if self.section_80u.disability_percentage == DisabilityPercentage.MODERATE else Money.from_int(125000)
        return Money.zero()
    
    @property
    def disability_deduction_amount(self) -> Money:
        return self.disability_deduction
    
    # Section 80DDB backward compatibility
    @property
    def medical_treatment_deduction(self) -> Money:
        return self.section_80ddb.medical_expenses if self.section_80ddb else Money.zero()
    
    # Additional legacy properties for regime comparison service (using different names to avoid conflicts)
    def get_section_80c_total(self) -> Money:
        return self.section_80c.calculate_total_investment() if self.section_80c else Money.zero()
    
    def get_section_80d_total(self) -> Money:
        if self.section_80d:
            return (self.section_80d.self_family_premium
                   .add(self.section_80d.parent_premium)
                   .add(self.section_80d.preventive_health_checkup))
        return Money.zero()
    
    def get_section_80e_total(self) -> Money:
        return self.education_loan_interest
    
    def get_section_80g_total(self) -> Money:
        return self.donations_80g
    
    @property
    def standard_deduction(self) -> Money:
        return Money.from_int(50000)  # Standard deduction amount
    
    @property
    def hra_exemption(self) -> Money:
        return Money.zero()  # This should be calculated based on salary
    
    @property
    def lta_exemption(self) -> Money:
        return Money.zero()  # This should be calculated based on salary
    
    # Additional legacy properties found in the search
    @property
    def scientific_research_donation(self) -> Money:
        return Money.zero()
    
    @property
    def political_donation(self) -> Money:
        return self.section_80ggc.political_party_contribution if self.section_80ggc else Money.zero()
    
    @property
    def infrastructure_deduction(self) -> Money:
        return Money.zero()
    
    @property
    def industrial_undertaking_deduction(self) -> Money:
        return Money.zero()
    
    @property
    def special_category_state_deduction(self) -> Money:
        return Money.zero()
    
    @property
    def hotel_deduction(self) -> Money:
        return Money.zero()
    
    @property
    def north_eastern_state_deduction(self) -> Money:
        return Money.zero()
    
    @property
    def employment_deduction(self) -> Money:
        return Money.zero()
    
    @property
    def employment_generation_deduction(self) -> Money:
        return Money.zero()
    
    @property
    def offshore_banking_deduction(self) -> Money:
        return Money.zero()
    
    @property
    def co_operative_society_deduction(self) -> Money:
        return Money.zero()
    
    @property
    def royalty_deduction(self) -> Money:
        return Money.zero()
    
    @property
    def patent_deduction(self) -> Money:
        return Money.zero()
    
    @property
    def interest_on_savings_deduction(self) -> Money:
        return self.savings_account_interest
    
    def calculate_combined_80c_80ccc_80ccd1_deduction(self, regime: TaxRegime) -> Money:
        """Calculate combined 80C + 80CCC + 80CCD(1) deduction with ₹1.5L limit."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        total_investment = Money.zero()
        
        # Add 80C investments
        if self.section_80c:
            total_investment = total_investment.add(self.section_80c.calculate_total_investment())
        
        # Add 80CCC pension fund
        if self.section_80ccc:
            total_investment = total_investment.add(self.section_80ccc.pension_fund_contribution)
        
        # Add 80CCD(1) employee NPS
        if self.section_80ccd:
            total_investment = total_investment.add(self.section_80ccd.employee_nps_contribution)
        
        # Apply combined limit of ₹1.5 lakh
        max_limit = Money.from_int(150000)
        return total_investment.min(max_limit)
    
    def calculate_adjusted_gross_income_for_80g(self, gross_total_income: Money, regime: TaxRegime) -> Money:
        """
        Calculate adjusted gross income for 80G qualifying limit calculation.
        
        For Section 80G purposes, the qualifying limit is based on:
        Gross Total Income minus all deductions except 80G itself.
        
        Args:
            gross_total_income: Total income before any deductions
            regime: Tax regime
            
        Returns:
            Money: Adjusted gross income for 80G calculation
        """
        if regime.regime_type == TaxRegimeType.NEW:
            return gross_total_income
        
        # Calculate all deductions except 80G
        other_deductions = Money.zero()
        
        # Combined 80C + 80CCC + 80CCD(1) deduction
        other_deductions = other_deductions.add(self.calculate_combined_80c_80ccc_80ccd1_deduction(regime))
        
        # Other individual deductions
        if self.section_80ccd:
            other_deductions = other_deductions.add(self.section_80ccd.calculate_80ccd_1b_deduction(regime))
            other_deductions = other_deductions.add(self.section_80ccd.calculate_80ccd_2_deduction(regime))
        
        if self.section_80d:
            other_deductions = other_deductions.add(self.section_80d.calculate_eligible_deduction(regime))
        
        if self.section_80dd:
            other_deductions = other_deductions.add(self.section_80dd.calculate_eligible_deduction(regime))
        
        if self.section_80ddb:
            other_deductions = other_deductions.add(self.section_80ddb.calculate_eligible_deduction(regime))
        
        if self.section_80e:
            other_deductions = other_deductions.add(self.section_80e.calculate_eligible_deduction(regime))
        
        if self.section_80eeb:
            other_deductions = other_deductions.add(self.section_80eeb.calculate_eligible_deduction(regime))
        
        if self.section_80ggc:
            other_deductions = other_deductions.add(self.section_80ggc.calculate_eligible_deduction(regime))
        
        if self.section_80u:
            other_deductions = other_deductions.add(self.section_80u.calculate_eligible_deduction(regime))
        
        # Adjusted gross income = Gross income - other deductions (excluding 80G)
        adjusted_income = gross_total_income.subtract(other_deductions)
        return adjusted_income.max(Money.zero())  # Ensure it's not negative

    def calculate_total_deductions_with_80g_adjustment(self, gross_total_income: Money, regime: TaxRegime) -> Money:
        """
        Calculate total deductions with proper 80G adjustment.
        
        This method ensures that 80G qualifying limit is calculated correctly
        based on income after other deductions.
        
        Args:
            gross_total_income: Total income before any deductions
            regime: Tax regime
            
        Returns:
            Money: Total deductions including properly calculated 80G
        """
        if regime.regime_type == TaxRegimeType.NEW:
            # Only employer NPS contribution allowed in new regime
            if self.section_80ccd:
                return self.section_80ccd.calculate_80ccd_2_deduction(regime)
            return Money.zero()
        
        # Calculate 80G with adjusted gross income
        if self.section_80g:
            adjusted_income = self.calculate_adjusted_gross_income_for_80g(gross_total_income, regime)
        
        # Now calculate total deductions normally
        return self.calculate_total_deductions(regime, adjusted_income)
    
    def calculate_total_deductions(self, regime: TaxRegime) -> Money:
        """
        Calculate total eligible deductions across all sections.
        
        Args:
            regime: Tax regime
            
        Returns:
            Money: Total deductions
        """
        if regime.regime_type == TaxRegimeType.NEW:
            # Only employer NPS contribution allowed in new regime
            if self.section_80ccd:
                return self.section_80ccd.calculate_80ccd_2_deduction(regime)
            return Money.zero()
        
        total = Money.zero()
        
        # Combined 80C + 80CCC + 80CCD(1) limit
        total = total.add(self.calculate_combined_80c_80ccc_80ccd1_deduction(regime))
        
        # 80CCD(1B) - Additional NPS (separate ₹50,000 limit)
        if self.section_80ccd:
            total = total.add(self.section_80ccd.calculate_80ccd_1b_deduction(regime))
        
        # 80CCD(2) - Employer NPS contribution
        if self.section_80ccd:
            total = total.add(self.section_80ccd.calculate_80ccd_2_deduction(regime))
        
        # 80D - Health Insurance
        if self.section_80d:
            total = total.add(self.section_80d.calculate_eligible_deduction(regime))
        
        # 80DD - Disability (Dependent)
        if self.section_80dd:
            total = total.add(self.section_80dd.calculate_eligible_deduction(regime))
        
        # 80DDB - Medical Treatment
        if self.section_80ddb:
            total = total.add(self.section_80ddb.calculate_eligible_deduction(regime))
        
        # 80E - Education Loan Interest
        if self.section_80e:
            total = total.add(self.section_80e.calculate_eligible_deduction(regime))
        
        # 80EEB - Electric Vehicle Loan Interest
        if self.section_80eeb:
            total = total.add(self.section_80eeb.calculate_eligible_deduction(regime))
        
        # 80G - Charitable Donations
        if self.section_80g:
            total = total.add(self.section_80g.calculate_eligible_deduction(regime))
        
        # 80GGC - Political Party Contributions
        if self.section_80ggc:
            total = total.add(self.section_80ggc.calculate_eligible_deduction(regime))
        
        # 80U - Self Disability
        if self.section_80u:
            total = total.add(self.section_80u.calculate_eligible_deduction(regime))
        
        # Other deductions (for backward compatibility)
        if self.other_deductions:
            total = total.add(self.other_deductions.calculate_total())
        
        return total
    
    def calculate_interest_exemptions(self, regime: TaxRegime) -> Money:
        """Calculate interest income exemptions (80TTA/80TTB)."""
        if self.section_80tta_ttb:
            return self.section_80tta_ttb.calculate_eligible_exemption(regime)
        return Money.zero()
    
    def get_comprehensive_breakdown(self, regime: TaxRegime) -> Dict[str, Any]:
        """
        Get comprehensive breakdown of all deductions and exemptions.
        
        Args:
            regime: Tax regime
            
        Returns:
            Dict: Complete breakdown
        """
        breakdown = {
            "regime": regime.regime_type.value,
            "deductions_applicable": regime.allows_deductions()
        }
        
        if regime.allows_deductions():
            # Combined 80C + 80CCC + 80CCD(1)
            combined_section = {
                "limit": 150000,
                "total_invested": 0,
                "eligible_deduction": self.calculate_combined_80c_80ccc_80ccd1_deduction(regime).to_float()
            }
            
            if self.section_80c:
                combined_section["section_80c"] = self.section_80c.get_investment_breakdown()
            if self.section_80ccc:
                combined_section["section_80ccc"] = self.section_80ccc.pension_fund_contribution.to_float()
            if self.section_80ccd:
                combined_section["section_80ccd_1"] = self.section_80ccd.employee_nps_contribution.to_float()
            
            breakdown["combined_80c_80ccc_80ccd1"] = combined_section
            
            # Individual sections
            if self.section_80ccd:
                breakdown["section_80ccd"] = {
                    "80ccd_1b": self.section_80ccd.calculate_80ccd_1b_deduction(regime).to_float(),
                    "80ccd_2": self.section_80ccd.calculate_80ccd_2_deduction(regime).to_float()
                }
            
            if self.section_80d:
                breakdown["section_80d"] = self.section_80d.get_deduction_breakdown(regime)
            
            if self.section_80dd:
                breakdown["section_80dd"] = self.section_80dd.calculate_eligible_deduction(regime).to_float()
            
            if self.section_80ddb:
                breakdown["section_80ddb"] = self.section_80ddb.calculate_eligible_deduction(regime).to_float()
            
            if self.section_80e:
                breakdown["section_80e"] = self.section_80e.calculate_eligible_deduction(regime).to_float()
            
            if self.section_80eeb:
                breakdown["section_80eeb"] = self.section_80eeb.calculate_eligible_deduction(regime).to_float()
            
            if self.section_80g:
                breakdown["section_80g"] = self.section_80g.calculate_eligible_deduction(regime).to_float()
            
            if self.section_80ggc:
                breakdown["section_80ggc"] = self.section_80ggc.calculate_eligible_deduction(regime).to_float()
            
            if self.section_80u:
                breakdown["section_80u"] = self.section_80u.calculate_eligible_deduction(regime).to_float()
            
            # Interest exemptions
            if self.section_80tta_ttb:
                breakdown["interest_exemptions"] = self.section_80tta_ttb.get_exemption_breakdown(regime)
            
            # Other deductions (for backward compatibility)
            if self.other_deductions:
                breakdown["other_deductions"] = self.other_deductions.get_breakdown()
            
            breakdown["total_deductions"] = self.calculate_total_deductions(regime).to_float()
            breakdown["total_interest_exemptions"] = self.calculate_interest_exemptions(regime).to_float()
        else:
            # New regime - only employer NPS allowed
            breakdown["new_regime_deductions"] = {
                "employer_nps_80ccd2": self.section_80ccd.calculate_80ccd_2_deduction(regime).to_float() if self.section_80ccd else 0,
                "total": self.calculate_total_deductions(regime).to_float()
            }
        
        return breakdown
    
    def get_deduction_breakdown(self, regime: TaxRegime) -> Dict[str, Any]:
        """Legacy method for backward compatibility."""
        return self.get_comprehensive_breakdown(regime)