"""
Test script for taxation calculations.

This script tests all components of the taxation system to ensure they are correctly calculated.
"""

import logging
import datetime
from models.taxation.taxation import Taxation
from models.taxation.salary import SalaryComponents
from models.taxation.perquisites import Perquisites
from models.taxation.income_sources import (
    IncomeFromOtherSources,
    IncomeFromHouseProperty,
    CapitalGains,
    LeaveEncashment
)
from models.taxation.deductions import DeductionComponents

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_taxation_components():
    """Test all taxation components with sample data."""
    logger.info("Starting taxation components test")
    
    # 1. Create perquisites
    perquisites = Perquisites(
        # Accommodation
        accommodation_provided='Employer-Owned',
        accommodation_city_population='Exceeding 40 lakhs in 2011 Census',
        accommodation_rent=15000,
        is_furniture_owned=True,
        furniture_actual_cost=50000,
        furniture_cost_to_employer=5000,
        
        # Car
        is_car_employer_owned=True,
        car_use='Mixed',
        car_cost_to_employer=10000,
        month_counts=12,
        
        # Medical
        medical_reimbursement_by_employer=20000,
        
        # LTA
        lta_amount_claimed=50000,
        lta_claimed_count=1,
        travel_through='Air',
        public_transport_travel_amount_for_same_distance=40000
    )
    
    # 2. Create salary components
    salary = SalaryComponents(
        basic=1000000,
        dearness_allowance=100000,
        hra=240000,
        hra_city='Delhi',
        special_allowance=120000,
        bonus=50000,
        commission=30000,
        perquisites=perquisites
    )
    
    # 3. Create other income sources
    other_sources = IncomeFromOtherSources(
        regime='old',
        age=40,
        interest_savings=10000,
        interest_fd=30000,
        dividend_income=5000,
        business_professional_income=100000
    )
    
    # 4. Create house property income
    house_property = IncomeFromHouseProperty(
        property_address='123 Example St, Mumbai',
        occupancy_status='Let-Out',
        rent_income=240000,
        property_tax=10000,
        interest_on_home_loan=180000,
        municipal_tax_paid=24000
    )
    
    # 5. Create capital gains
    capital_gains = CapitalGains(
        stcg_111a=50000,  # Special rate (15%)
        stcg_any_other_asset=30000,  # Normal slab rate
        ltcg_112a=150000,  # Special rate (10% after 1L exemption)
        ltcg_any_other_asset=100000  # Special rate (20% with indexation)
    )
    
    # 6. Create leave encashment
    leave_encashment = LeaveEncashment(
        leave_encashment_income_received=500000,
        leave_encashed=90,
        is_deceased=False,
    )
    
    # 7. Create deductions
    ev_purchase_date = datetime.date(2020, 6, 15)
    deductions = DeductionComponents(
        regime='old',
        age=40,
        section_80c_lic=20000,
        section_80c_epf=50000,
        section_80c_tsfdsb=50000,
        section_80ccd_1_nps=50000,
        section_80d_hisf=25000,
        section_80d_hi_parent=30000,
        section_80eeb=20000,
        ev_purchase_date=ev_purchase_date
    )
    
    # 8. Create taxation object
    taxation = Taxation(
        emp_id='TEST001',
        emp_age=40,
        regime='old',
        salary=salary,
        other_sources=other_sources,
        house_property=house_property,
        capital_gains=capital_gains,
        leave_encashment=leave_encashment,
        deductions=deductions,
        tax_year='2023-2024',
        filing_status='draft',
        total_tax=0,
        tax_breakup={},
        tax_payable=0,
        tax_paid=0,
        tax_due=0,
        tax_refundable=0,
        tax_pending=0
    )
    
    # 9. Test calculations
    
    # Test salary calculation
    salary_total = salary.total('old')
    logger.info(f"Salary total: {salary_total}")
    
    # Test house property income
    house_property_income = house_property.total_taxable_income_per_slab('old')
    logger.info(f"House property income: {house_property_income}")
    
    # Test capital gains
    stcg_special = capital_gains.total_stcg_special_rate()
    stcg_slab = capital_gains.total_stcg_slab_rate()
    ltcg_special = capital_gains.total_ltcg_special_rate()
    ltcg_taxable = capital_gains.calculate_ltcg_tax()
    logger.info(f"STCG special rate: {stcg_special}")
    logger.info(f"STCG slab rate: {stcg_slab}")
    logger.info(f"LTCG special rate: {ltcg_special}")
    logger.info(f"LTCG taxable amounts: {ltcg_taxable}")
    
    # Test leave encashment
    leave_encashment_income = leave_encashment.total_taxable_income_per_slab('old')
    logger.info(f"Leave encashment income: {leave_encashment_income}")
    
    # Test deductions
    deductions_total = deductions.total('old', False, salary_total, 40, ev_purchase_date)
    logger.info(f"Total deductions: {deductions_total}")
    
    # Test taxable income calculation
    taxable_income = taxation.get_taxable_income()
    logger.info(f"Taxable income: {taxable_income}")
    
    # Test tax summary
    tax_summary = taxation.get_tax_summary()
    logger.info(f"Tax summary: {tax_summary}")
    
    return taxation

if __name__ == "__main__":
    taxation = test_taxation_components()
    logger.info("Taxation test completed successfully") 