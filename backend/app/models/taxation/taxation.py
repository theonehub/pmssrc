"""
Main taxation model that integrates all components.

This module provides the main Taxation class that integrates all tax components
and provides functionality for calculating taxes, serializing/deserializing, etc.
"""

from dataclasses import dataclass
import datetime
import logging
from typing import Dict, Any, Optional, List

from models.taxation.income_sources import (
    IncomeFromOtherSources,
    IncomeFromHouseProperty,
    CapitalGains,
    LeaveEncashment,
    VoluntaryRetirement,
    Gratuity,
    RetrenchmentCompensation,
    Pension
)
from models.taxation.perquisites import Perquisites
from models.taxation.salary import SalaryComponents  
from models.taxation.deductions import DeductionComponents

logger = logging.getLogger(__name__)


@dataclass
class Taxation:
    """
    Main taxation class that integrates all tax components.
    
    This class provides a complete representation of a tax declaration,
    including all income sources, deductions, and calculation results.
    """
    emp_id: str
    emp_age: int
    salary: SalaryComponents
    other_sources: IncomeFromOtherSources
    house_property: IncomeFromHouseProperty
    capital_gains: CapitalGains
    leave_encashment: LeaveEncashment
    voluntary_retirement: VoluntaryRetirement
    retrenchment: RetrenchmentCompensation
    pension: Pension
    gratuity: Gratuity
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
    is_govt_employee: bool = False
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Taxation':
        """
        Create a Taxation object from a dictionary.
        
        Parameters:
        - data: Dictionary containing taxation data
        
        Returns:
        - Taxation object
        """
        # Extract nested objects
        salary_data = data.get('salary', {})
        other_sources_data = data.get('other_sources', {})
        house_property_data = data.get('house_property', {})
        capital_gains_data = data.get('capital_gains', {})
        leave_encashment_data = data.get('leave_encashment', {})
        voluntary_retirement_data = data.get('voluntary_retirement', {})
        pension_data = data.get('pension', {})
        gratuity_data = data.get('gratuity', {})
        deductions_data = data.get('deductions', {})
        retrenchment_data = data.get('RetrenchmentCompensation', {})

        # Handle perquisites in salary data
        perquisites = None
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
                other_vehicle_cost_to_employer=perquisites_data.get('other_vehicle_cost_to_employer', 0),
                other_vehicle_month_counts=perquisites_data.get('other_vehicle_month_counts', 0),
                
                # Medical Reimbursement
                is_treated_in_India=perquisites_data.get('is_treated_in_India', False),
                medical_reimbursement_by_employer=perquisites_data.get('medical_reimbursement_by_employer', 0),
                travelling_allowance_for_treatment=perquisites_data.get('travelling_allowance_for_treatment', 0),
                rbi_limit_for_illness=perquisites_data.get('rbi_limit_for_illness', 0),
                
                
                # Leave Travel Allowance
                lta_amount_claimed=perquisites_data.get('lta_amount_claimed', 0),
                lta_claimed_count=perquisites_data.get('lta_claimed_count', 0),
                travel_through=perquisites_data.get('travel_through', 'Air'),
                public_transport_travel_amount_for_same_distance=perquisites_data.get('public_transport_travel_amount_for_same_distance', 0),
                
                # Free Education
                employer_maintained_1st_child=perquisites_data.get('employer_maintained_1st_child', False),
                monthly_count_1st_child=perquisites_data.get('monthly_count_1st_child', 0),
                employer_monthly_expenses_1st_child=perquisites_data.get('employer_monthly_expenses_1st_child', 0),
                employer_maintained_2nd_child=perquisites_data.get('employer_maintained_2nd_child', False),
                monthly_count_2nd_child=perquisites_data.get('monthly_count_2nd_child', 0),
                employer_monthly_expenses_2nd_child=perquisites_data.get('employer_monthly_expenses_2nd_child', 0),

                # Gas, Electricity, Water
                gas_amount_paid_by_employer=perquisites_data.get('gas_amount_paid_by_employer', 0),
                electricity_amount_paid_by_employer=perquisites_data.get('electricity_amount_paid_by_employer', 0),
                water_amount_paid_by_employer=perquisites_data.get('water_amount_paid_by_employer', 0),
                gas_amount_paid_by_employee=perquisites_data.get('gas_amount_paid_by_employee', 0),
                electricity_amount_paid_by_employee=perquisites_data.get('electricity_amount_paid_by_employee', 0),
                water_amount_paid_by_employee=perquisites_data.get('water_amount_paid_by_employee', 0),
                is_gas_manufactured_by_employer=perquisites_data.get('is_gas_manufactured_by_employer', False),
                is_electricity_manufactured_by_employer=perquisites_data.get('is_electricity_manufactured_by_employer', False),
                is_water_manufactured_by_employer=perquisites_data.get('is_water_manufactured_by_employer', False),

                # Domestic help
                domestic_help_amount_paid_by_employer=perquisites_data.get('domestic_help_amount_paid_by_employer', 0),
                domestic_help_amount_paid_by_employee=perquisites_data.get('domestic_help_amount_paid_by_employee', 0),

                # Interest-free/concessional loan
                loan_type=perquisites_data.get('loan_type', 'Personal'),
                loan_amount=perquisites_data.get('loan_amount', 0),
                loan_interest_rate_company=perquisites_data.get('loan_interest_rate_company', 0),
                loan_interest_rate_sbi=perquisites_data.get('loan_interest_rate_sbi', 0),
                loan_month_count=perquisites_data.get('loan_month_count', 0),
                loan_start_date=perquisites_data.get('loan_start_date', ''),
                loan_end_date=perquisites_data.get('loan_end_date', ''),

                # Lunch/Refreshment
                lunch_amount_paid_by_employer=perquisites_data.get('lunch_amount_paid_by_employer', 0),
                lunch_amount_paid_by_employee=perquisites_data.get('lunch_amount_paid_by_employee', 0),

                # ESOP
                number_of_esop_shares_exercised=perquisites_data.get('number_of_esop_shares_exercised', 0),
                esop_exercise_price_per_share=perquisites_data.get('esop_exercise_price_per_share', 0),
                esop_allotment_price_per_share=perquisites_data.get('esop_allotment_price_per_share', 0),

                # Movable assets
                mau_ownership=perquisites_data.get('mau_ownership', 'Employer-Owned'),
                mau_value_to_employer=perquisites_data.get('mau_value_to_employer', 0),
                mau_value_to_employee=perquisites_data.get('mau_value_to_employee', 0),

                mat_value_to_employer=perquisites_data.get('mat_value_to_employer', 0),
                mat_value_to_employee=perquisites_data.get('mat_value_to_employee', 0),
                mat_type=perquisites_data.get('mat_type', 'Electronics'),
                mat_number_of_completed_years_of_use=perquisites_data.get('mat_number_of_completed_years_of_use', 0),

                # Monetary benefits
                monetary_amount_paid_by_employer=perquisites_data.get('monetary_amount_paid_by_employer', 0),
                expenditure_for_offical_purpose=perquisites_data.get('expenditure_for_offical_purpose', 0),
                monetary_benefits_amount_paid_by_employee=perquisites_data.get('monetary_benefits_amount_paid_by_employee', 0),

                # Gift Vouchers
                gift_vouchers_amount_paid_by_employer=perquisites_data.get('gift_vouchers_amount_paid_by_employer', 0),

                # Club Expenses
                club_expenses_amount_paid_by_employer=perquisites_data.get('club_expenses_amount_paid_by_employer', 0),
                club_expenses_amount_paid_by_employee=perquisites_data.get('club_expenses_amount_paid_by_employee', 0),
                club_expenses_amount_paid_for_offical_purpose=perquisites_data.get('club_expenses_amount_paid_for_offical_purpose', 0)
            )
        
        # Setup regime and age info
        regime = data.get('regime', 'old')
        emp_age = data.get('emp_age', 0)
        
        # Create component objects
        salary = SalaryComponents(
            basic=salary_data.get('basic', 0),
            dearness_allowance=salary_data.get('dearness_allowance', 0),
            hra=salary_data.get('hra', 0),
            actual_rent_paid=salary_data.get('actual_rent_paid', 0),
            hra_city=salary_data.get('hra_city', 'Others'),
            hra_percentage=salary_data.get('hra_percentage', 0),
            special_allowance=salary_data.get('special_allowance', 0),
            bonus=salary_data.get('bonus', 0),
            commission=salary_data.get('commission', 0),
            city_compensatory_allowance=salary_data.get('city_compensatory_allowance', 0),
            rural_allowance=salary_data.get('rural_allowance', 0),
            proctorship_allowance=salary_data.get('proctorship_allowance', 0),
            wardenship_allowance=salary_data.get('wardenship_allowance', 0),
            project_allowance=salary_data.get('project_allowance', 0),
            deputation_allowance=salary_data.get('deputation_allowance', 0),
            overtime_allowance=salary_data.get('overtime_allowance', 0),
            any_other_allowance=salary_data.get('any_other_allowance', 0),
            any_other_allowance_exemption=salary_data.get('any_other_allowance_exemption', 0),
            interim_relief=salary_data.get('interim_relief', 0),
            tiffin_allowance=salary_data.get('tiffin_allowance', 0),
            fixed_medical_allowance=salary_data.get('fixed_medical_allowance', 0),
            servant_allowance=salary_data.get('servant_allowance', 0),
            govt_employees_outside_india_allowance=salary_data.get('govt_employees_outside_india_allowance', 0),
            supreme_high_court_judges_allowance=salary_data.get('supreme_high_court_judges_allowance', 0),
            judge_compensatory_allowance=salary_data.get('judge_compensatory_allowance', 0),
            section_10_14_special_allowances=salary_data.get('section_10_14_special_allowances', 0),
            travel_on_tour_allowance=salary_data.get('travel_on_tour_allowance', 0),
            tour_daily_charge_allowance=salary_data.get('tour_daily_charge_allowance', 0),
            conveyance_in_performace_of_duties=salary_data.get('conveyance_in_performace_of_duties', 0),
            helper_in_performace_of_duties=salary_data.get('helper_in_performace_of_duties', 0),    
            academic_research=salary_data.get('academic_research', 0),
            uniform_allowance=salary_data.get('uniform_allowance', 0),
            hills_high_altd_allowance=salary_data.get('hills_high_altd_allowance', 0),
            hills_high_altd_exemption_limit=salary_data.get('hills_high_altd_exemption_limit', 0),
            border_remote_allowance= salary_data.get('border_remote_allowance', 0),
            border_remote_exemption_limit=salary_data.get('border_remote_exemption_limit', 0),
            transport_employee_allowance= salary_data.get('transport_employee_allowance', 0),
            children_education_allowance= salary_data.get('children_education_allowance', 0),
            children_education_count=salary_data.get('children_education_count', 0),
            children_education_months=salary_data.get('children_education_months', 0),
            hostel_allowance= salary_data.get('hostel_allowance', 0),
            hostel_count=salary_data.get('hostel_count', 0),
            hostel_months=salary_data.get('hostel_months', 0),
            underground_mines_allowance= salary_data.get('underground_mines_allowance', 0),
            govt_employee_entertainment_allowance= salary_data.get('govt_employee_entertainment_allowance', 0),
            underground_mines_months=salary_data.get('underground_mines_months', 0),
            transport_allowance= salary_data.get('transport_allowance', 0),
            transport_months=salary_data.get('transport_months', 0),
            
            perquisites=perquisites
        )
        
        other_sources = IncomeFromOtherSources(
            regime=regime,
            age=emp_age,
            interest_savings=other_sources_data.get('interest_savings', 0),
            interest_fd=other_sources_data.get('interest_fd', 0),
            interest_rd=other_sources_data.get('interest_rd', 0),
            dividend_income=other_sources_data.get('dividend_income', 0),
            gifts=other_sources_data.get('gifts', 0),
            other_interest=other_sources_data.get('other_interest', 0),
            business_professional_income=other_sources_data.get('business_professional_income', 0),
            other_income=other_sources_data.get('other_income', 0)
        )

        house_property = IncomeFromHouseProperty(
            property_address=house_property_data.get('property_address', ''),
            occupancy_status=house_property_data.get('occupancy_status', ''),
            rent_income=house_property_data.get('rent_income', 0),
            property_tax=house_property_data.get('property_tax', 0),
            interest_on_home_loan=house_property_data.get('interest_on_home_loan', 0),
            pre_construction_loan_interest=house_property_data.get('pre_construction_loan_interest', 0)
        )

        capital_gains = CapitalGains(
            stcg_111a=capital_gains_data.get('stcg_111a', 0),
            stcg_any_other_asset=capital_gains_data.get('stcg_any_other_asset', 0),
            stcg_debt_mutual_fund=capital_gains_data.get('stcg_debt_mutual_fund', 0),
            ltcg_112a=capital_gains_data.get('ltcg_112a', 0),
            ltcg_any_other_asset=capital_gains_data.get('ltcg_any_other_asset', 0),
            ltcg_debt_mutual_fund=capital_gains_data.get('ltcg_debt_mutual_fund', 0)
        )

        leave_encashment = LeaveEncashment(
            leave_encashment_income_received=leave_encashment_data.get('leave_encashment_income_received', 0),
            leave_encashed=leave_encashment_data.get('leave_encashed', 0),
            is_deceased=leave_encashment_data.get('is_deceased', False),
            during_employment=leave_encashment_data.get('during_employment', False)
        )
        
        voluntary_retirement = VoluntaryRetirement(
            is_vrs_requested=voluntary_retirement_data.get('is_vrs_requested', False),
            voluntary_retirement_amount=voluntary_retirement_data.get('voluntary_retirement_amount', 0)
        )

        retrenchment = RetrenchmentCompensation (
            retrenchment_amount=retrenchment_data.get('retrenchment_amount', 0),
            is_provided=retrenchment_data.get('is_provided', False)
        )

        pension = Pension(
            total_pension_income=pension_data.get('total_pension_income', 0),
            computed_pension_percentage=pension_data.get('computed_pension_percentage', 0),
            uncomputed_pension_frequency=pension_data.get('uncomputed_pension_frequency', 'monthly'),
            uncomputed_pension_amount=pension_data.get('uncomputed_pension_amount', 0)
        )

        gratuity = Gratuity(
            gratuity_income=gratuity_data.get('gratuity_income', 0)
        )
        
        # Parse date string for EV purchase date
        ev_purchase_date = None
        ev_purchase_date_str = deductions_data.get('ev_purchase_date')
        if ev_purchase_date_str:
            try:
                # Handle both string and datetime.date inputs
                if isinstance(ev_purchase_date_str, datetime.date):
                    ev_purchase_date = ev_purchase_date_str
                else:
                    ev_purchase_date = datetime.datetime.strptime(ev_purchase_date_str, '%Y-%m-%d').date()
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to parse EV purchase date: {e}")
                ev_purchase_date = None
        
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
            relation_80dd=deductions_data.get('relation_80dd', ''),
            disability_percentage=deductions_data.get('disability_percentage', ''),
            section_80dd=deductions_data.get('section_80dd', 0),
            relation_80ddb=deductions_data.get('relation_80ddb', ''),
            age_80ddb=deductions_data.get('age_80ddb', 0),
            section_80ddb=deductions_data.get('section_80ddb', 0),
            section_80eeb=deductions_data.get('section_80eeb', 0),
            relation_80e=deductions_data.get('relation_80e', ''),
            section_80e_interest=deductions_data.get('section_80e_interest', 0),
            ev_purchase_date=ev_purchase_date or datetime.date.today(),
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
            house_property=house_property,
            capital_gains=capital_gains,
            leave_encashment=leave_encashment,
            voluntary_retirement=voluntary_retirement,
            retrenchment=retrenchment,
            pension=pension,
            gratuity=gratuity,
            deductions=deductions,
            tax_year=data.get('tax_year', ''),
            filing_status=data.get('filing_status', 'draft'),
            total_tax=data.get('total_tax', 0),
            tax_breakup=data.get('tax_breakup', {}),
            tax_payable=data.get('tax_payable', 0),
            tax_paid=data.get('tax_paid', 0),
            tax_due=data.get('tax_due', 0),
            tax_refundable=data.get('tax_refundable', 0),
            tax_pending=data.get('tax_pending', 0),
            is_govt_employee=data.get('is_govt_employee', False)
        )
    
    @staticmethod
    def _parse_date(date_str):
        """Helper method to parse date strings safely"""
        if not date_str:
            return None
        try:
            return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            # Try ISO format
            try:
                return datetime.datetime.fromisoformat(date_str).date()
            except (ValueError, TypeError):
                return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert a Taxation object to a dictionary"""
        result = {
            'emp_id': self.emp_id,
            'emp_age': self.emp_age,
            'regime': self.regime,
            'total_tax': self.total_tax,
            'tax_breakup': self.tax_breakup,
            'tax_year': self.tax_year,
            'filing_status': self.filing_status,
            'tax_payable': self.tax_payable,
            'tax_paid': self.tax_paid,
            'tax_due': self.tax_due,
            'tax_refundable': self.tax_refundable,
            'tax_pending': self.tax_pending,
            'is_govt_employee': self.is_govt_employee
        }
        
        # Handle salary components
        if isinstance(self.salary, dict):
            result['salary'] = self.salary
        else:
            salary_dict = {}
            for attr in dir(self.salary):
                if not attr.startswith('_') and attr != 'to_dict' and attr != 'total' \
                    and attr != 'calculate_exemptions' and attr != 'calculate_taxable_salary' \
                        and attr != 'calculate_annual_value' and attr != 'calculate_hra_exemption' \
                            and attr != 'total_taxable_income_per_slab':
                    value = getattr(self.salary, attr)
                    # Handle perquisites specially
                    if attr == 'perquisites' and value is not None:
                        if isinstance(value, dict):
                            salary_dict['perquisites'] = value
                        else:
                            perq_dict = {}
                            for p_attr in dir(value):
                                if not p_attr.startswith('_') and p_attr != 'to_dict' and not p_attr.startswith('total_'):
                                    p_value = getattr(value, p_attr)
                                    # Handle date objects
                                    if isinstance(p_value, datetime.date):
                                        perq_dict[p_attr] = p_value.isoformat()
                                    else:
                                        perq_dict[p_attr] = p_value
                            salary_dict['perquisites'] = perq_dict
                    else:
                        salary_dict[attr] = value
            result['salary'] = salary_dict
        
        # Handle other_sources components
        if isinstance(self.other_sources, dict):
            result['other_sources'] = self.other_sources
        else:
            other_sources_dict = {}
            for attr in dir(self.other_sources):
                if not attr.startswith('_') and attr != 'to_dict' and attr != 'total' \
                    and attr != 'total_taxable_income_per_slab' and attr != 'get_section_80tt' \
                        and attr != 'calculate_exemptions' and attr != 'calculate_taxable_salary' \
                            and attr != 'calculate_annual_value' and attr != 'calculate_hra_exemption':
                    other_sources_dict[attr] = getattr(self.other_sources, attr)
            result['other_sources'] = other_sources_dict
        
        # Handle capital_gains components
        if isinstance(self.capital_gains, dict):
            result['capital_gains'] = self.capital_gains
        else:
            capital_gains_dict = {}
            for attr in dir(self.capital_gains):
                if not attr.startswith('_') and attr != 'to_dict' and attr != 'total' \
                    and attr != 'total_stcg_special_rate' and attr != 'total_stcg_slab_rate' \
                        and attr != 'total_ltcg_special_rate' and attr != 'calculate_ltcg_tax' \
                            and attr != 'calculate_stcg_tax' and attr != 'total_ltcg_slab_rate' \
                                and attr != 'calculate_ltcg_tax_per_slab' and attr != 'calculate_stcg_tax_per_slab'\
                                    and attr != 'tax_on_stcg_special_rate' and attr != 'tax_on_ltcg_special_rate':
                    capital_gains_dict[attr] = getattr(self.capital_gains, attr)
            result['capital_gains'] = capital_gains_dict

        # Handle leave_encashment components
        if isinstance(self.leave_encashment, dict):
            result['leave_encashment'] = self.leave_encashment
        else:
            leave_encashment_dict = {}
            for attr in dir(self.leave_encashment):
                if not attr.startswith('_') and attr != 'to_dict' and attr != 'total' and attr != 'total_taxable_income_per_slab':
                    leave_encashment_dict[attr] = getattr(self.leave_encashment, attr)
            result['leave_encashment'] = leave_encashment_dict
            
        # Handle voluntary_retirement components
        if isinstance(self.voluntary_retirement, dict):
            result['voluntary_retirement'] = self.voluntary_retirement
        else:
            voluntary_retirement_dict = {}
            for attr in dir(self.voluntary_retirement):
                if not attr.startswith('_') and attr != 'to_dict' and attr != 'total' and attr != 'total_taxable_income_per_slab' and attr != 'compute_vrs_value':
                    voluntary_retirement_dict[attr] = getattr(self.voluntary_retirement, attr)
            result['voluntary_retirement'] = voluntary_retirement_dict
        
        # Handle retrenchment components
        if isinstance(self.retrenchment, dict):
            result['retrenchment'] = self.retrenchment
        else:
            retrenchment_dict = {}
            for attr in dir(self.retrenchment):
                if not attr.startswith('_') and attr != 'to_dict' and attr != 'total' and attr != 'total_taxable_income_per_slab' and attr != 'compute_service_years':
                    retrenchment_dict[attr] = getattr(self.retrenchment, attr)
            result['retrenchment'] = retrenchment_dict
        
        if isinstance(self.pension, dict):
            result['pension'] = self.pension
        else:
            pension_dict = {}
            for attr in dir(self.pension):
                if not attr.startswith('_') and attr != 'to_dict' and attr != 'total' and attr != 'total_taxable_income_per_slab_computed' and attr != 'total_taxable_income_per_slab_uncomputed':
                    pension_dict[attr] = getattr(self.pension, attr)
            result['pension'] = pension_dict

        # Handle house_property components
        if isinstance(self.house_property, dict):
            result['house_property'] = self.house_property
        else:
            house_property_dict = {}
            for attr in dir(self.house_property):
                if not attr.startswith('_') and attr != 'to_dict' and attr != 'total_taxable_income_per_slab' and attr != 'calculate_exemptions' and attr != 'calculate_taxable_salary' and attr != 'calculate_annual_value':
                    value = getattr(self.house_property, attr)
                    if isinstance(value, datetime.date):
                        house_property_dict[attr] = value.isoformat()
                    else:
                        house_property_dict[attr] = value
            result['house_property'] = house_property_dict
            
        # Handle deductions components
        if isinstance(self.deductions, dict):
            result['deductions'] = self.deductions
        else:
            deductions_dict = {}
            for attr in dir(self.deductions):
                if not attr.startswith('_') and attr != 'to_dict' and attr != 'total' \
                    and attr != 'total_deduction' and not attr.startswith('total_deductions_') \
                        and attr != 'total_deduction_per_slab':
                    value = getattr(self.deductions, attr)
                    # Handle date objects
                    if isinstance(value, datetime.date):
                        deductions_dict[attr] = value.isoformat()
                    else:
                        deductions_dict[attr] = value
            result['deductions'] = deductions_dict
        
        return result
        
        
    def get_taxable_income(self) -> float:
        """Calculate the total taxable income"""
        # Calculate salary income
        salary_total = self.salary.total()
        logger.info(f"Salary income total: {salary_total}")
        
        # Calculate income from other sources
        other_sources_total = self.other_sources.total()
        logger.info(f"Other sources income total: {other_sources_total}")
        
        # Calculate house property income
        house_property_total = self.house_property.total_taxable_income_per_slab()
        logger.info(f"House property income total: {house_property_total}")
        
        # Calculate capital gains
        stcg_slab_rate = self.capital_gains.total_stcg_slab_rate()
        stcg_special_rate = self.capital_gains.total_stcg_special_rate()
        ltcg_special_rate = self.capital_gains.total_ltcg_special_rate()
        logger.info(f"Capital gains - STCG (slab rate): {stcg_slab_rate}, STCG (special rate): {stcg_special_rate}, LTCG (special rate): {ltcg_special_rate}")
        
        # Calculate leave encashment
        leave_encashment_total = self.leave_encashment.total_taxable_income_per_slab()
        logger.info(f"Leave encashment income total: {leave_encashment_total}")
        
        # Calculate voluntary retirement
        voluntary_retirement_total = 0
        if hasattr(self, 'voluntary_retirement') and self.voluntary_retirement:
            voluntary_retirement_total = self.voluntary_retirement.total_taxable_income_per_slab(
                regime=self.regime,
                age=self.emp_age,
                service_years=self.voluntary_retirement.service_years,
                last_drawn_monthly_salary=self.voluntary_retirement.last_drawn_monthly_salary
            )
            logger.info(f"Voluntary retirement income total: {voluntary_retirement_total}")
        
        # # Calculate retrenchment
        retrenchment_total = 0   #TODO: Add retrenchment income
        # if hasattr(self, 'retrenchment') and self.retrenchment:
        #     retrenchment_total = self.retrenchment.total_taxable_income_per_slab(
        #         regime=self.regime,
        #     )
        #     logger.info(f"Retrenchment income total: {retrenchment_total}")
        
        # Calculate gross income
        gross_income = salary_total + other_sources_total + house_property_total + \
            stcg_slab_rate + leave_encashment_total + voluntary_retirement_total
        logger.info(f"Gross income (excluding special rates): {gross_income}")
        
        # Calculate deductions (only for old regime)
        deductions_total = 0
        if self.regime == 'old':
            deductions_total = self.deductions.total()
            logger.info(f"Total deductions (old regime): {deductions_total}")
        else:
            logger.info("New regime selected: no deductions applicable")
            
        # Calculate final taxable income
        taxable_income = max(0, gross_income - deductions_total)
        logger.info(f"Final taxable income: {taxable_income}")
        
        return taxable_income
    
    def get_tax_summary(self) -> Dict[str, Any]:
        """Get a summary of the taxation"""
        # Calculate all income components
        salary_total = self.salary.total()
        other_sources_total = self.other_sources.total()
        house_property_total = self.house_property.total_taxable_income_per_slab()
        capital_gains_total = self.capital_gains.total_stcg_slab_rate() + self.capital_gains.total_stcg_special_rate() + self.capital_gains.total_ltcg_special_rate()
        leave_encashment_total = self.leave_encashment.total_taxable_income_per_slab()
        
        # Calculate voluntary retirement
        voluntary_retirement_total = 0
        if hasattr(self, 'voluntary_retirement') and self.voluntary_retirement:
            voluntary_retirement_total = self.voluntary_retirement.total_taxable_income_per_slab(
                regime=self.regime,
                age=self.emp_age,
                service_years=self.voluntary_retirement.service_years,
                last_drawn_monthly_salary=self.voluntary_retirement.last_drawn_monthly_salary
            )
        
        # Calculate gross income
        gross_income = salary_total + other_sources_total + house_property_total + capital_gains_total + leave_encashment_total + voluntary_retirement_total
        
        # Calculate deductions (only for old regime)
        deductions_total = self.deductions.total() if self.regime == 'old' else 0
        
        return {
            'emp_id': self.emp_id,
            'emp_age': self.emp_age,
            'tax_year': self.tax_year,
            'regime': self.regime,
            'gross_income': gross_income,
            'income_breakdown': {
                'salary': salary_total,
                'other_sources': other_sources_total,
                'house_property': house_property_total,
                'capital_gains': capital_gains_total,
                'leave_encashment': leave_encashment_total,
                'voluntary_retirement': voluntary_retirement_total,
                # 'retrenchment': retrenchment_total
            },
            'deductions': deductions_total,
            'taxable_income': self.get_taxable_income(),
            'total_tax': self.total_tax,
            'tax_paid': self.tax_paid,
            'tax_due': self.tax_due,
            'tax_refundable': self.tax_refundable,
            'filing_status': self.filing_status
        } 