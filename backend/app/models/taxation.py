from dataclasses import dataclass
from datetime import date
from typing import Optional, Dict, Any, List

section_80g_100_wo_ql_heads = [
    "National Defence Fund set up by Central Government",
    "Prime Minister national relief fund",
    "Approved university",
    "Any other eligible donations for 100% deduction"
]

section_80g_50_wo_ql_heads = ["Prime Minister's Drought Relief Fund"]

section_80g_100_ql_heads = [
    "Donations to government or any approved local authority to promote family planning",
    "Any other fund that satisfies the conditions"
]

section_80g_50_ql_heads = [
    "Donations to government or any approved local authority to except to promote family planning",
    "Any Corporation for promoting interest of minority community",
    "For repair or renovation of any notified temple, mosque, gurudwara, church or other places of worship",
    "Any other fund that satisfies the conditions"
]

@dataclass
class IncomeFromOtherSources:
    regime: str = 'new'
    age: int = 0
    interest_savings: float = 0
    interest_fd: float = 0
    interest_rd: float = 0
    dividend_income: float = 0
    gifts: float = 0
    other_interest: float = 0
    other_income: float = 0

    def get_section_80tt(self, age: int, regime: str = 'new'):
        if regime == 'old':
            if age >= 60:
                return "80TTB"
            else:
                return "80TTC"
        else:
            return "Not Applicable"

    def total_taxable_income_per_slab(self, regime: str = 'new', age: int = 0):
        deduction = 10000
        if regime == 'new':
            return 0
        
        elif regime == 'old':
            if age >= 60:
                deduction = 50000

        return sum([
            self.interest_savings,
            self.interest_fd,
            self.interest_rd,
            self.dividend_income,
            self.gifts,
            self.other_interest,
            self.other_income
        ]) - deduction

    def total(self) -> float:
        """Calculate total income from other sources"""
        return sum([
            self.interest_savings,
            self.interest_fd,
            self.interest_rd,
            self.dividend_income,
            self.gifts,
            self.other_interest,
            self.other_income
        ])

@dataclass
class IncomeFromHouseProperty:
    occupancy_status: str = ''  #LetOut, SelfOccupied, PerConstruction
    rent_income: float = 0
    property_tax: float = 0
    standard_deduction: float = 0
    interest_on_home_loan: float = 0

    def total_taxable_income_per_slab(self, regime: str = 'new'):
        self.standard_deduction = self.rent_income * 0.3
        if regime == 'New':
            if self.occupancy_status == 'LetOut':
                interest = self.interest_on_home_loan
            else:
                interest = 0
        elif self.occupancy_status == 'PerConstruction':
            interest = self.interest_on_home_loan * 0.2
        else:
            interest = self.interest_on_home_loan

        return self.rent_income - self.property_tax - self.standard_deduction - interest
        
    
@dataclass
class CapitalGains:
    stcg_111a: float = 0    # Short Term Capital Gain from listed equity shares 
                            # and equity oriented mutual funds which are charged to STT
                            # (taxed at 20%)
    stcg_any_other_asset: float = 0     # Short Term Capital Gain from other assets 
                                        # (taxed at slab rates)
    stcg_debt_mutual_fund: float = 0    # Short Term Capital Gain from debt mutual funds 
                                        # (taxed at slab rates)
    
    ltcg_112a: float = 0    # Long Term Capital Gain from listed equity shares 
                            # and equity oriented mutual funds which are charged to STT 
                            # (12.5% above 1.25L)
    ltcg_any_other_asset: float = 0     # Long Term Capital Gain from other assets 
                                        # (taxed at 12.5%)
    ltcg_debt_mutual_fund: float = 0    # Long Term Capital Gain from debt mutual funds 
                                        # (taxed at 12.5%)
        
    def total_stcg_special_rate(self):
        """Total short-term capital gains charged at special rates"""
        return self.stcg_111a
    
    def total_stcg_slab_rate(self):
        """Total short-term capital gains taxed at slab rates"""
        return self.stcg_any_other_asset + self.stcg_debt_mutual_fund
    
    def total_ltcg_special_rate(self):
        """Total long-term capital gains charged at special rates"""
        return self.ltcg_112a + self.ltcg_any_other_asset + self.ltcg_debt_mutual_fund
    
    def total(self) -> float:
        """Calculate total capital gains"""
        return (
            self.total_stcg_special_rate() +
            self.total_stcg_slab_rate() +
            self.total_ltcg_special_rate()
        )

@dataclass
class BusinessProfessionalIncome:
    business_income: float = 0
    professional_income: float = 0
    
    def total_taxable_income_per_slab(self):
        return self.business_income + self.professional_income

@dataclass
class Perquisites:
    """
    Represents all perquisites as per Indian Income Tax Act.
    Each perquisite has its own exemption/taxability logic.
    """

    # Accommodation perquisites
    accommodation_provided: str = 'Employer-Owned'  # Employer-Owned, Govt, Employer-Leased, Hotel provided for 15 days or above
    accommodation_govt_lic_fees: float = 0
    accommodation_city_population: str = 'Exceeding 40 lakhs in 2011 Census'
    accommodation_rent: float = 0
    is_furniture_owned: bool = False
    furniture_actual_cost: float = 0
    furniture_cost_to_employer: float = 0
    furniture_cost_paid_by_employee: float = 0

    # Car perquisites
    is_car_rating_higher: bool = False  # True if engine capacity > 1.6L
    is_car_employer_owned: bool = False
    is_expenses_reimbursed: bool = False
    is_driver_provided: bool = False
    car_use: str = 'Personal'  # Personal, Business, Mixed
    car_cost_to_employer: float = 0
    month_counts: int = 0
    other_vehicle_cost: float = 0
    other_vehicle_months: int = 0

    # Medical Reimbursement
    is_treated_in_India: bool = False
    medical_reimbursement_by_employer: float = 0
    # Leave Travel Allowance
    lta_amount_claimed: float = 0
    lta_claimed_count: int = 0
    travel_through: str = 'Air'
    public_transport_travel_amount_for_same_distance: float = 0
    lta_claim_start_date: str = ''
    lta_claim_end_date: str = ''
    # Free Education
    free_education_actual_expenses: float = 0
    free_education_is_institute_by_employer: bool = False
    free_education_similar_institute_cost: float = 0
    # Gas, Electricity, Water
    gas_amount_paid_by_employer: float = 0
    electricity_amount_paid_by_employer: float = 0
    water_amount_paid_by_employer: float = 0
    gas_amount_paid_by_employee: float = 0
    electricity_amount_paid_by_employee: float = 0
    water_amount_paid_by_employee: float = 0
    # Domestic help
    domestic_help_amount_paid_by_employer: float = 0
    domestic_help_amount_paid_by_employee: float = 0
    # Interest-free/concessional loan
    loan_type: str = ''
    loan_amount: float = 0
    loan_interest_rate_company: float = 0
    loan_interest_rate_sbi: float = 0
    monthly_interest_amount_sbi: float = 0
    monthly_interest_amount_company: float = 0
    # Lunch/Refreshment
    lunch_amount_paid_by_employer: float = 0
    lunch_amount_paid_by_employee: float = 0
    # ESOP
    number_of_esop_shares_awarded: float = 0
    esop_exercise_price_per_share: float = 0
    esop_allotment_price_per_share: float = 0
    grant_date: Optional[date] = None
    vesting_date: Optional[date] = None
    exercise_date: Optional[date] = None
    vesting_period: int = 0
    exercise_period: int = 0
    exercise_price_per_share: float = 0
    # Transfer of movable assets
    movable_asset_type: str = 'Electronics'
    movable_asset_value_to_employer: float = 0
    movable_asset_value_to_employee: float = 0
    number_of_completed_years_of_use: int = 0
    # Monetary benefits
    monetary_amount_paid_by_employer: float = 0
    expenditure_for_offical_purpose: float = 0
    monetary_benefits_amount_paid_by_employee: float = 0
    # Gift Vouchers (new field for partial exemption)
    gift_vouchers_amount_paid_by_employer: float = 0
    # Club Expenses
    club_expenses_amount_paid_by_employer: float = 0
    club_expenses_amount_paid_by_employee: float = 0
    club_expenses_amount_paid_for_offical_purpose: float = 0

    def total_accommodation_value(self, gross_salary: float, regime: str = 'new') -> float:
        """Calculate taxable value of accommodation perquisite."""
        if regime == 'new':
            return 0
        
        if self.accommodation_provided == 'Govt':
                return self.accommodation_govt_lic_fees - self.accommodation_rent
        elif self.accommodation_provided == 'Employer-Owned':
            if self.is_furniture_owned:
                furniture_value = self.furniture_cost_to_employer * 0.1
            else:
                furniture_value = self.furniture_cost_to_employer - \
                                    self.furniture_cost_paid_by_employee

            if self.accommodation_city_population == 'Exceeding 40 lakhs in 2011 Census':
                return (gross_salary * 0.1) + furniture_value
            elif self.accommodation_city_population == 'Between 15 lakhs and 40 lakhs in 2011 Census':
                return (gross_salary * 0.075) + furniture_value
            elif self.accommodation_city_population == 'Below 15 lakhs in 2011 Census':
                return gross_salary * 0.05
        elif self.accommodation_provided == 'Employer-Leased':
            furniture_value = min(self.furniture_actual_cost * 0.10, 
                                  self.furniture_cost_to_employer)
            return ((min(self.accommodation_rent, (gross_salary * 0.10))) + furniture_value)
        elif self.accommodation_provided == 'Hotel provided for 15 days or above':
            return min(self.accommodation_rent, (gross_salary * 0.24))
        else:
            return 0

    def total_car_value(self, gross_salary: float, regime: str = 'new') -> float:
        """Calculate taxable value of car perquisite."""
        if regime == 'new':
            return 0
        
        if self.is_car_employer_owned:
            if self.car_use == 'Personal':
                return (self.car_cost_to_employer * self.month_counts) + \
                        (self.other_vehicle_cost - 900) * self.other_vehicle_months
            elif self.car_use == 'Business':
                return ((self.other_vehicle_cost - 900) * self.other_vehicle_months)
        
        if self.is_expenses_reimbursed:
            value = 1800 if self.is_car_rating_higher else 2400
            if self.is_driver_provided:
                value += 900
            return (value * self.month_counts) + ((self.other_vehicle_cost - 900) 
                                                  * self.other_vehicle_months)
        else:
            value = 600 if self.is_car_rating_higher else 900
            if self.is_driver_provided:
                value += 900
            return ((value * self.month_counts) + ((self.other_vehicle_cost - 900) 
                                                  * self.other_vehicle_months))
    
    def total_medical_reimbursement(self, regime: str = 'new') -> float:
        """Taxable value of medical reimbursement (exempt up to 15,000 if treated in India)."""
        if regime == 'new':
            return 0
        else:
            if self.is_treated_in_India:
                return min(self.medical_reimbursement_by_employer, 15000)
            else:
                return self.medical_reimbursement_by_employer

    def total_lta_value(self, regime: str = 'new') -> float:
        """Taxable value of Leave Travel Allowance (LTA)."""
        if regime == 'new':
            return 0
        else:
            # LTA exemption is limited to 2 journeys in a block of 4 years
            if self.lta_claimed_count <= 2:
                return max(0, self.lta_amount_claimed - self.public_transport_travel_amount_for_same_distance)
            else:
                return 0

    def total_free_education_value(self, regime: str = 'new') -> float:
        """Taxable value of free education perquisite."""
        if regime == 'new':
            return 0
        else:
            monthly_exemption = 1000  # Rs. 1,000 per month
            annual_exemption = monthly_exemption * 12  # Rs. 12,000 per year
            
            if self.free_education_is_institute_by_employer:
                # If education is provided in employer's institute
                taxable_value = max(0, self.free_education_similar_institute_cost - annual_exemption)
            else:
                # If employer pays for education elsewhere
                taxable_value = max(0, self.free_education_actual_expenses - annual_exemption)
            
            return taxable_value

    def total_gas_electricity_water_value(self, regime: str = 'new') -> float:
        """Taxable value of gas, electricity, and water perquisite."""
        if regime == 'new':
            return 0
        else:
            paid_by_employer_sum = self.gas_amount_paid_by_employer + self.electricity_amount_paid_by_employer + self.water_amount_paid_by_employer
            paid_by_employee_sum = self.gas_amount_paid_by_employee + self.electricity_amount_paid_by_employee + self.water_amount_paid_by_employee
            return max(0, paid_by_employer_sum - paid_by_employee_sum)
        

    def total_domestic_help_value(self, regime: str = 'new') -> float:
        """Taxable value of domestic help perquisite."""
        if regime == 'new':
            return 0
        else:
            return max(0, self.domestic_help_amount_paid_by_employer - self.domestic_help_amount_paid_by_employee)

    def total_interest_amount(self, regime: str = 'new') -> float:
        """Taxable value of interest-free/concessional loan perquisite."""
        if regime == 'new':
            return 0
        else:
            return max(0, self.monthly_interest_amount_sbi - self.monthly_interest_amount_company) * 12
    
    def allocation_gain(self, regime: str = 'new') -> float:
        """Taxable value of ESOP allocation gain."""
        if regime == 'new':
            return 0
        else:
            return max(0, (self.esop_allotment_price_per_share - self.esop_exercise_price_per_share) * self.number_of_esop_shares_awarded)
    
    def total_movable_asset_value(self, regime: str = 'new') -> float:
        """Taxable value of transfer of movable assets perquisite."""
        if regime == 'new':
            return 0
        else:
            if self.movable_asset_type == 'Electronics':
                asset_current_value = (self.movable_asset_value_to_employer * 0.5) * (self.number_of_completed_years_of_use)
                return max(0, (self.movable_asset_value_to_employer - asset_current_value) - self.movable_asset_value_to_employee)
            elif self.movable_asset_type == 'Motor Vehicle':
                asset_current_value = (self.movable_asset_value_to_employer * 0.2) * (self.number_of_completed_years_of_use)
                return max(0, (self.movable_asset_value_to_employer - asset_current_value) - self.movable_asset_value_to_employee)
            else:
                asset_current_value = self.movable_asset_value_to_employer 
                asset_current_value = (self.movable_asset_value_to_employer * 0.1) * (self.number_of_completed_years_of_use)
                return max(0, (self.movable_asset_value_to_employer - asset_current_value) - self.movable_asset_value_to_employee)

    def total_monetary_benefits_value(self, regime: str = 'new') -> float:
        """Taxable value of monetary benefits perquisite."""
        if regime == 'new':
            return 0
        else:
            return max(0, self.monetary_amount_paid_by_employer - 
                       self.expenditure_for_offical_purpose - 
                       self.monetary_benefits_amount_paid_by_employee)
        
    def total_gift_vouchers_value(self, regime: str = 'new') -> float:
        """Taxable value of gift vouchers (exempt up to Rs. 5,000)."""
        if regime == 'new':
            return 0
        else:
            # Only the amount above 5,000 is taxable
            return max(0, self.gift_vouchers_amount_paid_by_employer - 5000)
            
    def total_club_expenses_value(self, regime: str = 'new') -> float:
        """Taxable value of club expenses perquisite."""
        if regime == 'new':
            return 0
        else:
            return max(0, self.club_expenses_amount_paid_by_employer - 
                       self.club_expenses_amount_paid_by_employee - 
                       self.club_expenses_amount_paid_for_offical_purpose)

    def total(self, regime: str = 'new') -> float:
        """
        Calculate total taxable value of all perquisites for the given regime.
        Includes all perquisite types as per Indian tax rules.
        """
        if regime == 'new':
            return 0
        total_value = 0.0
        # Add all perquisite calculations
        total_value += self.total_accommodation_value(gross_salary=0, regime=regime)  # gross_salary to be passed if available
        total_value += self.total_car_value(gross_salary=0, regime=regime)
        total_value += self.total_medical_reimbursement(regime)
        total_value += self.total_lta_value(regime)
        total_value += self.total_free_education_value(regime)
        total_value += self.total_gas_electricity_water_value(regime)
        total_value += self.total_domestic_help_value(regime)
        total_value += self.total_interest_amount(regime)
        total_value += self.total_lunch_value(regime)
        total_value += self.allocation_gain(regime)
        total_value += self.total_movable_asset_value(regime)
        total_value += self.total_monetary_benefits_value(regime)
        total_value += self.total_gift_vouchers_value(regime)
        total_value += self.total_club_expenses_value(regime)
        return total_value

@dataclass
class SalaryComponents:
    """
    Represents all salary components as per Indian Income Tax Act.
    Includes all allowances and perquisites.
    """
    basic: float = 0
    dearness_allowance: float = 0
    hra: float = 0
    special_allowance: float = 0
    bonus: float = 0
    commission: float = 0
    city_compensatory_allowance: float = 0
    rural_allowance: float = 0
    proctorship_allowance: float = 0
    wardenship_allowance: float = 0
    project_allowance: float = 0
    deputation_allowance: float = 0
    overtime_allowance: float = 0
    interim_relief: float = 0
    tiffin_allowance: float = 0
    fixed_medical_allowance: float = 0
    servant_allowance: float = 0
    allowances_to_government_employees_outside_india: float = 0
    allowance_to_high_court_supreme_court_judges: float = 0
    compensatory_allowance_received_by_a_judge: float = 0
    special_allowances_exempt_under_section_10_14: float = 0
    allowance_granted_to_meet_cost_of_travel_on_tour: float = 0
    allowance_granted_to_meet_cost_of_daily_charges_incurred_on_tour: float = 0
    allowance_granted_to_meet_expenditure_incurred_on_conveyance_in_performace_of_duties: float = 0
    allowance_granted_to_meet_expenditure_incurred_on_helper_in_performace_of_duties: float = 0
    allowance_granted_for_encouraging_the_academic_research_training_pursuits_in_educational_research_institutions: float = 0
    allowance_granted_for_expenditure_incurred_on_purchase_or_maintenance_of_uniform_for_wear_during_performace_of_duties: float = 0
    perquisites: Optional[Perquisites] = None

    def total(self, regime: str = 'new') -> float:
        """
        Calculate total taxable salary including all components and perquisites.
        """
        base_total = (
            self.basic + self.dearness_allowance + self.hra + self.special_allowance +
            self.bonus + self.commission + self.city_compensatory_allowance + self.rural_allowance +
            self.proctorship_allowance + self.wardenship_allowance + self.project_allowance +
            self.deputation_allowance + self.overtime_allowance + self.interim_relief +
            self.tiffin_allowance + self.fixed_medical_allowance + self.servant_allowance +
            self.allowances_to_government_employees_outside_india + self.allowance_to_high_court_supreme_court_judges +
            self.compensatory_allowance_received_by_a_judge + self.special_allowances_exempt_under_section_10_14 +
            self.allowance_granted_to_meet_cost_of_travel_on_tour + self.allowance_granted_to_meet_cost_of_daily_charges_incurred_on_tour +
            self.allowance_granted_to_meet_expenditure_incurred_on_conveyance_in_performace_of_duties +
            self.allowance_granted_to_meet_expenditure_incurred_on_helper_in_performace_of_duties +
            self.allowance_granted_for_encouraging_the_academic_research_training_pursuits_in_educational_research_institutions +
            self.allowance_granted_for_expenditure_incurred_on_purchase_or_maintenance_of_uniform_for_wear_during_performace_of_duties
        )
        if self.perquisites:
            base_total += self.perquisites.total(regime)
        return base_total

@dataclass
class DeductionComponents:
    regime: str = 'new'
    age: int = 0
    #section 80C
    section_80c_lic: float = 0  #Life Insurance Premium
    section_80c_epf: float = 0  #Employee Provident Fund
    section_80c_ssp: float = 0  #Sukanya Samridhi Account
    section_80c_nsc: float = 0  #National Savings Certificate
    section_80c_ulip: float = 0  #Unit Linked Insurance Plan
    section_80c_tsmf: float = 0  #Tax Saving Mutual Fund
    section_80c_tffte2c: float = 0  #Tuition Fees for full time education of upto 2 kids
    section_80c_paphl: float = 0  #Principal amount paid for housing loan installments
    section_80c_sdpphp: float = 0  #Stamp duty paid for purchase of residental property
    section_80c_tsfdsb: float = 0  #Tax saving fixed deposit in a scheduled bank
    section_80c_scss: float = 0  #Senior citizen savings scheme
    section_80c_others: float = 0  #Others  Max all above 1,50,000

    #section 80CCC
    section_80ccc_ppic: float = 0  #Pension Payment under section  Max 1,50,000

    #section 80CCD
    section_80ccd_1_nps: float = 0  #self-employed or employee contribution to NPS
    section_80ccd_1b_additional: float = 0  #additional contribution to NPS by self-employed 
                                            #or employee Max 50,000

    # Max deduction 1,50,000 for all the above elements


    def total_deductions_80c_80ccd_80ccd_1_1b(self, regime: str = 'new'):
        if regime == 'new':
            return 0
        else:
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
            return section_80c_total
            
    section_80ccd_2_enps: float = 0  #contribution to NPS by employer 
                                     #14% of salary(govt employees) 
                                     # 10% of salary(private employees)

    def total_deductions_80ccd_2(self, regime: str = 'new', gross_income: float = 0, is_govt_employee: bool = False):
        if regime == 'new':
            return 0
        else:
            if is_govt_employee:
                max_cap = gross_income * 0.14
            else:
                max_cap = gross_income * 0.10
            return min(self.section_80ccd_2_enps, max_cap)
            

    #section 80D Health Insurance Premium
    section_80d_hisf: float = 0     #Health Insurance Premium for self and family
                                    #Max 25,000 if age is above 60 otherwise 50,000
    section_80d_phcs: float = 0     #Preventive health checkups max 5000 per year
                                    #its included in 25k or 50k limit

    def total_deductions_80d_self_family(self, regime: str = 'new', age: int = 0):
        if regime == 'new':
            return 0
        else:
            if age >= 60:
                return min(self.section_80d_hisf + min(self.section_80d_phcs, 5000), 50000)
            else:
                return min(self.section_80d_hisf + min(self.section_80d_phcs, 5000), 25000)

    #section 80D Health Insurance Premium for parents
    section_80d_hi_parent: float = 0  #Health Insurance Premium for parents
                                    #Max 25,000 if age is above 60 otherwise 50,000
    
    def total_deductions_80d_parent(self, regime: str = 'new', age: int = 0):
        if regime == 'new':
            return 0
        else:
            if age >= 60:
                return min(self.section_80d_hi_parent, 50000)
            else:
                return min(self.section_80d_hi_parent, 25000)

    #section 80DD Disability Deduction 
    relation_80dd: str = '' #Spouse, Child, Parents, Sibling
    disability_percentage: str = '' #Between 40%-80% - 75k, More than 80% - 125k
    section_80dd: float = 0

    def total_deductions_80dd(self, regime: str = 'new'):
        if regime == 'new':
            return 0
        else:
            if self.relation_80dd in ['Spouse', 'Child', 'Parents', 'Sibling']:
                if self.disability_percentage == 'Between 40%-80%':
                    return min(self.section_80dd, 75000)
                else:
                    return min(self.section_80dd, 125000)
            else:
                return 0

    #section 80DDB Specific Diseases
    relation_80ddb: str = '' #Spouse, Child, Parents, Sibling
    age_80ddb: int = 0
    section_80ddb: float = 0 #if age < 60 - 40k else 100K

    def total_deductions_80ddb(self, regime: str = 'new', age: int = 0):
        if regime == 'new':
            return 0
        else:
            if self.relation_80ddb in ['Spouse', 'Child', 'Parents', 'Sibling']:
                if age < 60:
                    return min(self.section_80ddb, 40000)
                else:
                    return min(self.section_80ddb, 100000)
            else:
                return 0

    #section 80EEB interest on loan for EV vehicle purchased between 01.04.2019 & 31.03.2023
    section_80eeb: float = 0    #Max 150K
    ev_purchase_date: date = date.today()

    def total_deductions_80eeb(self, regime: str = 'new', ev_purchase_date: date = date.today()):
        if regime == 'new':
            return 0
        else:
            if ev_purchase_date >= date(2019, 4, 1) and ev_purchase_date <= date(2023, 3, 31):
                return min(self.section_80eeb, 150000)
            else:
                return 0

    #section 80G Donations to charitable institutions
    section_80g_100_wo_ql: float = 0    #Donations entitled to 100% deduction without qualifying limit 
    section_80g_100_head: str = ''

    def total_deductions_80g_100_wo_ql(self, regime: str = 'new'):
        if regime == 'new':
            return 0
        elif self.section_80g_100_head in section_80g_100_wo_ql_heads:
            return self.section_80g_100_wo_ql
        else:
            return 0

    section_80g_50_wo_ql: float = 0    #Donations entitled to 50% deduction without qualifying limit 
    section_80g_50_head: str = ''

    def total_deductions_80g_50_wo_ql(self, regime: str = 'new'):
        if regime == 'new':
            return 0
        elif self.section_80g_50_head in section_80g_50_wo_ql_heads:
            return (self.section_80g_50_wo_ql * 0.5)
        else:
            return 0

    section_80g_100_ql: float = 0   #Donations entitled to 100% deduction with 
                                    #qualifying limit of 10% of adjusted gross total income  
    section_80g_100_ql_head: str = ''

    def total_deductions_80g_100_ql(self, regime: str = 'new', gross_total_income: float = 0):
        if regime == 'new':
            return 0
        elif self.section_80g_100_ql_head in section_80g_100_ql_heads:
            return min(self.section_80g_100_ql, (gross_total_income * 0.1))
        else:
            return 0

    section_80g_50_ql: float = 0    #Donations entitled to 50% deduction with qualifying limit of 10% of adjusted gross total income  
    section_80g_50_ql_head: str = ''

    def total_deductions_80g_50_ql(self, regime: str = 'new', gross_total_income: float = 0):
        if regime == 'new':
            return 0
        elif self.section_80g_50_ql_head in section_80g_50_ql_heads:
            return min(self.section_80g_50_ql, (gross_total_income * 0.1))
        else:
            return 0


    #section 80GGC Interest on savings account
    section_80ggc: float = 0        #Deduction on Political parties contribution (No Deductions for payments made in Cash)

    def total_deductions_80ggc(self, regime: str = 'new'):
        if regime == 'new':
            return 0
        else:
            return self.section_80ggc

    #section 80U
    section_80u: float = 0
    disability_percentage_80u: str = '' #Between 40%-80% - 75k, More than 80% - 125k

    def total_deductions_80u(self, regime: str = 'new'):
        if regime == 'new':
            return 0
        else:
            if self.disability_percentage_80u == 'Between 40%-80%':
                return min(self.section_80u, 75000)
            else:
                return min(self.section_80u, 125000)
            

    def total_deduction(self, regime: str = 'new', 
                        is_govt_employee: bool = False,         
                        gross_income: float = 0, age: int = 0,             
                        ev_purchase_date: date = date.today()):
        return (self.total_deductions_80c_80ccd_80ccd_1_1b(regime) +
                self.total_deductions_80ccd_2(regime, gross_income, is_govt_employee) +
                self.total_deductions_80d_self_family(regime, age) +
                self.total_deductions_80d_parent(regime, age) +
                self.total_deductions_80dd(regime) +
                self.total_deductions_80ddb(regime, age) +
                self.total_deductions_80eeb(regime, ev_purchase_date) +
                self.total_deductions_80g_100_wo_ql(regime) +
                self.total_deductions_80g_50_wo_ql(regime) +
                self.total_deductions_80g_100_ql(regime, gross_income) +
                self.total_deductions_80g_50_ql(regime, gross_income) +
                self.total_deductions_80ggc(regime) +
                self.total_deductions_80u(regime))

    def total(self, regime: str = 'new', is_govt_employee: bool = False, gross_income: float = 0, age: int = 0, ev_purchase_date: date = date.today()) -> float:
        """Alias for total_deduction to maintain compatibility."""
        return self.total_deduction(regime, is_govt_employee, gross_income, age, ev_purchase_date)



@dataclass
class Taxation:
    emp_id: str
    emp_age: int
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
    is_govt_employee: bool
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Taxation':
        """Create a Taxation object from a dictionary"""
        # Extract nested objects
        salary_data = data.get('salary', {})
        other_sources_data = data.get('other_sources', {})
        capital_gains_data = data.get('capital_gains', {})
        deductions_data = data.get('deductions', {})
        
        # Handle perquisites in salary data
        if 'perquisites' in salary_data and salary_data['perquisites']:
            perquisites_data = salary_data['perquisites']
            perquisites = Perquisites(
                
                # Accommodation perquisites
                accommodation_provided=perquisites_data.get('accommodation_provided', 'Employer-Owned'),
                accommodation_govt_lic_fees=perquisites_data.get('accommodation_govt_lic_fees', 0),
                accommodation_city_population=perquisites_data.get('accommodation_city_population', 'Exceeding 40 lakhs in 2011 Census'),
                accommodation_rent=perquisites_data.get('accommodation_rent', 0),
                is_furniture_owned=perquisites_data.get('is_furniture_owned', False),
                furniture_actual_cost=perquisites_data.get('furniture_actual_cost', 0),
                furniture_cost_to_employer=perquisites_data.get('furniture_cost_to_employer', 0),
                furniture_cost_paid_by_employee=perquisites_data.get('furniture_cost_paid_by_employee', 0),
                
                # Car perquisites
                is_car_rating_higher=perquisites_data.get('is_car_rating_higher', False),
                is_car_employer_owned=perquisites_data.get('is_car_employer_owned', False),
                is_expenses_reimbursed=perquisites_data.get('is_expenses_reimbursed', False),
                is_driver_provided=perquisites_data.get('is_driver_provided', False),
                car_use=perquisites_data.get('car_use', 'Personal'),
                car_cost_to_employer=perquisites_data.get('car_cost_to_employer', 0),
                month_counts=perquisites_data.get('month_counts', 0),
                other_vehicle_cost=perquisites_data.get('other_vehicle_cost', 0),
                other_vehicle_months=perquisites_data.get('other_vehicle_months', 0),
                
                # Medical Reimbursement
                is_treated_in_India=perquisites_data.get('is_treated_in_India', False),
                medical_reimbursement_by_employer=perquisites_data.get('medical_reimbursement_by_employer', 0),
                
                # Leave Travel Allowance
                lta_amount_claimed=perquisites_data.get('lta_amount_claimed', 0),
                lta_claimed_count=perquisites_data.get('lta_claimed_count', 0),
                travel_through=perquisites_data.get('travel_through', 'Air'),
                public_transport_travel_amount_for_same_distance=perquisites_data.get('public_transport_travel_amount_for_same_distance', 0),
                lta_claim_start_date=perquisites_data.get('lta_claim_start_date', ''),
                lta_claim_end_date=perquisites_data.get('lta_claim_end_date', ''),
                
                # Free Education
                free_education_actual_expenses=perquisites_data.get('free_education_actual_expenses', 0),
                free_education_is_institute_by_employer=perquisites_data.get('free_education_is_institute_by_employer', False),
                free_education_similar_institute_cost=perquisites_data.get('free_education_similar_institute_cost', 0)
            )
        else:
            perquisites = Perquisites()
        
        # Create component objects
        salary = SalaryComponents(
            basic=salary_data.get('basic', 0),
            dearness_allowance=salary_data.get('dearness_allowance', 0),
            hra=salary_data.get('hra', 0),
            special_allowance=salary_data.get('special_allowance', 0),
            bonus=salary_data.get('bonus', 0),
            perquisites=perquisites
        )
        
        # Setup regime and age info
        regime = data.get('regime', 'old')
        emp_age = data.get('emp_age', 0)
        
        other_sources = IncomeFromOtherSources(
            regime=regime,
            age=emp_age,
            interest_savings=other_sources_data.get('interest_savings', 0),
            interest_fd=other_sources_data.get('interest_fd', 0),
            interest_rd=other_sources_data.get('interest_rd', 0),
            dividend_income=other_sources_data.get('dividend_income', 0),
            gifts=other_sources_data.get('gifts', 0),
            other_interest=other_sources_data.get('other_interest', 0),
            other_income=other_sources_data.get('other_income', 0)
        )
        
        capital_gains = CapitalGains(
            stcg_111a=capital_gains_data.get('stcg_111a', 0),
            stcg_any_other_asset=capital_gains_data.get('stcg_any_other_asset', 0),
            stcg_debt_mutual_fund=capital_gains_data.get('stcg_debt_mutual_fund', 0),
            ltcg_112a=capital_gains_data.get('ltcg_112a', 0),
            ltcg_any_other_asset=capital_gains_data.get('ltcg_any_other_asset', 0),
            ltcg_debt_mutual_fund=capital_gains_data.get('ltcg_debt_mutual_fund', 0)
        )
        
        deductions = DeductionComponents(
            regime=regime,
            age=emp_age,
            section_80c_lic=deductions_data.get('section_80c_lic', 0),
            section_80c_epf=deductions_data.get('section_80c_epf', 0),
            section_80c_ssp=deductions_data.get('section_80c_ssp', 0),
            section_80c_nsc=deductions_data.get('section_80c_nsc', 0),
            section_80c_ulip=deductions_data.get('section_80c_ulip', 0),
            section_80c_tsmf=deductions_data.get('section_80c_tsmf', 0),
            section_80c_tffte2c=deductions_data.get('section_80c_tffte2c', 0),
            section_80c_paphl=deductions_data.get('section_80c_paphl', 0),
            section_80c_sdpphp=deductions_data.get('section_80c_sdpphp', 0),
            section_80c_tsfdsb=deductions_data.get('section_80c_tsfdsb', 0),
            section_80c_scss=deductions_data.get('section_80c_scss', 0),
            section_80c_others=deductions_data.get('section_80c_others', 0),
            section_80ccc_ppic=deductions_data.get('section_80ccc_ppic', 0),
            section_80ccd_1_nps=deductions_data.get('section_80ccd_1_nps', 0),
            section_80ccd_1b_additional=deductions_data.get('section_80ccd_1b_additional', 0),
            section_80ccd_2_enps=deductions_data.get('section_80ccd_2_enps', 0),
            section_80d_hisf=deductions_data.get('section_80d_hisf', 0),
            section_80d_phcs=deductions_data.get('section_80d_phcs', 0),
            section_80d_hi_parent=deductions_data.get('section_80d_hi_parent', 0),
            section_80dd=deductions_data.get('section_80dd', 0),
            section_80ddb=deductions_data.get('section_80ddb', 0),
            section_80eeb=deductions_data.get('section_80eeb', 0),
            section_80g_100_wo_ql=deductions_data.get('section_80g_100_wo_ql', 0),
            section_80g_100_head=deductions_data.get('section_80g_100_head', ''),
            section_80g_50_wo_ql=deductions_data.get('section_80g_50_wo_ql', 0),
            section_80g_50_head=deductions_data.get('section_80g_50_head', ''),
            section_80g_100_ql=deductions_data.get('section_80g_100_ql', 0),
            section_80g_100_ql_head=deductions_data.get('section_80g_100_ql_head', ''),
            section_80g_50_ql=deductions_data.get('section_80g_50_ql', 0),
            section_80g_50_ql_head=deductions_data.get('section_80g_50_ql_head', ''),
            section_80ggc=deductions_data.get('section_80ggc', 0),
            section_80u=deductions_data.get('section_80u', 0),
            disability_percentage_80u=deductions_data.get('disability_percentage_80u', '')
        )
        
        # Create and return Taxation object
        return cls(
            emp_id=data.get('emp_id', ''),
            emp_age=emp_age,
            regime=regime,
            salary=salary,
            other_sources=other_sources,
            capital_gains=capital_gains,
            deductions=deductions,
            tax_year=data.get('tax_year', ''),
            filing_status=data.get('filing_status', 'draft'),
            total_tax=data.get('total_tax', 0),
            tax_breakup=data.get('tax_breakup', {}),
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
                    
                    # Accommodation perquisites
                    'accommodation_provided': self.salary.perquisites.accommodation_provided,
                    'accommodation_govt_lic_fees': self.salary.perquisites.accommodation_govt_lic_fees,
                    'accommodation_city_population': self.salary.perquisites.accommodation_city_population,
                    'accommodation_rent': self.salary.perquisites.accommodation_rent,
                    'is_furniture_owned': self.salary.perquisites.is_furniture_owned,
                    'furniture_actual_cost': self.salary.perquisites.furniture_actual_cost,
                    'furniture_cost_to_employer': self.salary.perquisites.furniture_cost_to_employer,
                    'furniture_cost_paid_by_employee': self.salary.perquisites.furniture_cost_paid_by_employee,
                    
                    # Car perquisites
                    'is_car_rating_higher': self.salary.perquisites.is_car_rating_higher,
                    'is_car_employer_owned': self.salary.perquisites.is_car_employer_owned,
                    'is_expenses_reimbursed': self.salary.perquisites.is_expenses_reimbursed,
                    'is_driver_provided': self.salary.perquisites.is_driver_provided,
                    'car_use': self.salary.perquisites.car_use,
                    'car_cost_to_employer': self.salary.perquisites.car_cost_to_employer,
                    'month_counts': self.salary.perquisites.month_counts,
                    'other_vehicle_cost': self.salary.perquisites.other_vehicle_cost,
                    'other_vehicle_months': self.salary.perquisites.other_vehicle_months,
                    
                    # Medical Reimbursement
                    'is_treated_in_India': self.salary.perquisites.is_treated_in_India,
                    'medical_reimbursement_by_employer': self.salary.perquisites.medical_reimbursement_by_employer,
                    
                    # Leave Travel Allowance
                    'lta_amount_claimed': self.salary.perquisites.lta_amount_claimed,
                    'lta_claimed_count': self.salary.perquisites.lta_claimed_count,
                    'travel_through': self.salary.perquisites.travel_through,
                    'public_transport_travel_amount_for_same_distance': self.salary.perquisites.public_transport_travel_amount_for_same_distance,
                    'lta_claim_start_date': self.salary.perquisites.lta_claim_start_date,
                    'lta_claim_end_date': self.salary.perquisites.lta_claim_end_date,
                    
                    # Free Education
                    'free_education_actual_expenses': self.salary.perquisites.free_education_actual_expenses,
                    'free_education_is_institute_by_employer': self.salary.perquisites.free_education_is_institute_by_employer,
                    'free_education_similar_institute_cost': self.salary.perquisites.free_education_similar_institute_cost
                }
        
        # Create the dictionary
        return {
            'emp_id': self.emp_id,
            'emp_age': self.emp_age,
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
                'gifts': self.other_sources.gifts,
                'other_interest': self.other_sources.other_interest,
                'other_income': self.other_sources.other_income,
                'regime': self.other_sources.regime,
                'age': self.other_sources.age
            },
            'capital_gains': {
                'stcg_111a': self.capital_gains.stcg_111a,
                'stcg_any_other_asset': self.capital_gains.stcg_any_other_asset,
                'stcg_debt_mutual_fund': self.capital_gains.stcg_debt_mutual_fund,
                'ltcg_112a': self.capital_gains.ltcg_112a,
                'ltcg_any_other_asset': self.capital_gains.ltcg_any_other_asset,
                'ltcg_debt_mutual_fund': self.capital_gains.ltcg_debt_mutual_fund
            },
            'deductions': {
                'section_80c_lic': self.deductions.section_80c_lic,
                'section_80c_epf': self.deductions.section_80c_epf,
                'section_80c_ssp': self.deductions.section_80c_ssp,
                'section_80c_nsc': self.deductions.section_80c_nsc,
                'section_80c_ulip': self.deductions.section_80c_ulip,
                'section_80c_tsmf': self.deductions.section_80c_tsmf,
                'section_80c_tffte2c': self.deductions.section_80c_tffte2c,
                'section_80c_paphl': self.deductions.section_80c_paphl,
                'section_80c_sdpphp': self.deductions.section_80c_sdpphp,
                'section_80c_tsfdsb': self.deductions.section_80c_tsfdsb,
                'section_80c_scss': self.deductions.section_80c_scss,
                'section_80c_others': self.deductions.section_80c_others,
                'section_80ccc_ppic': self.deductions.section_80ccc_ppic,
                'section_80ccd_1_nps': self.deductions.section_80ccd_1_nps,
                'section_80ccd_1b_additional': self.deductions.section_80ccd_1b_additional,
                'section_80ccd_2_enps': self.deductions.section_80ccd_2_enps,
                'section_80d_hisf': self.deductions.section_80d_hisf,
                'section_80d_phcs': self.deductions.section_80d_phcs,
                'section_80d_hi_parent': self.deductions.section_80d_hi_parent,
                'section_80dd': self.deductions.section_80dd,
                'section_80ddb': self.deductions.section_80ddb,
                'section_80g_100_wo_ql': self.deductions.section_80g_100_wo_ql,
                'section_80g_100_head': self.deductions.section_80g_100_head,
                'section_80g_50_wo_ql': self.deductions.section_80g_50_wo_ql,
                'section_80g_50_head': self.deductions.section_80g_50_head,
                'section_80g_100_ql': self.deductions.section_80g_100_ql,
                'section_80g_100_ql_head': self.deductions.section_80g_100_ql_head,
                'section_80g_50_ql': self.deductions.section_80g_50_ql,
                'section_80g_50_ql_head': self.deductions.section_80g_50_ql_head,
                'section_80ggc': self.deductions.section_80ggc,
                'section_80u': self.deductions.section_80u,
                'disability_percentage_80u': self.deductions.disability_percentage_80u,
                'regime': self.deductions.regime,
                'age': self.deductions.age
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
            'emp_age': self.emp_age,
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
        