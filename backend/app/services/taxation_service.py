from models.taxation import (
    SalaryComponents, 
    IncomeFromOtherSources, 
    IncomeFromHouseProperty, 
    CapitalGains, 
    DeductionComponents, 
    Taxation, 
    Perquisites, 
    LeaveEncashment, 
    VoluntaryRetirement, 
    RetrenchmentCompensation,
    Pension,
    Gratuity
)
from database.taxation_database import get_taxation_by_emp_id, get_taxation_collection, save_taxation, _ensure_serializable
from services.organisation_service import is_govt_organisation
from database.user_database import get_user_by_emp_id
import datetime
import uuid
import logging
from fastapi import HTTPException
from dateutil.relativedelta import relativedelta
import json

# Configure detailed logging
logger = logging.getLogger(__name__)

def compute_regular_tax(income: float, regime: str = 'old', age: int = 0) -> float:
    """
    Compute regular income tax based on income tax slabs.
    
    Args:
        income: Taxable income amount
        regime: Tax regime ('old' or 'new')
        age: Age of taxpayer for senior citizen benefits
        
    Returns:
        Total tax amount
    """
    logger.info(f"compute_regular_tax - Starting regular tax computation with income: {income}, regime: {regime}, age: {age}")
    
    if regime == 'new':
        # New regime tax slabs (Budget 2025 rates)
        slabs = [
            (0, 400000, 0.0),           # Up to Rs. 4 lakh - Nil
            (400001, 800000, 0.05),     # Rs. 4-8 lakh - 5%
            (800001, 1200000, 0.10),    # Rs. 8-12 lakh - 10%
            (1200001, 1600000, 0.15),   # Rs. 12-16 lakh - 15%
            (1600001, 2000000, 0.20),   # Rs. 16-20 lakh - 20%
            (2000001, 2400000, 0.25),   # Rs. 20-24 lakh - 25%
            (2400001, float('inf'), 0.30) # Above Rs. 24 lakh - 30%
        ]
        logger.info(f"compute_regular_tax - Using new regime tax slabs (Budget 2025): {slabs}")
    else:
        # Old regime tax slabs with age-based exemptions
        if age >= 80:  # Super Senior Citizens
            basic_exemption = 500000  # Rs. 5 lakh exemption
        elif age >= 60:  # Senior Citizens
            basic_exemption = 300000  # Rs. 3 lakh exemption
        else:
            basic_exemption = 250000  # Rs. 2.5 lakh exemption
            
        slabs = [
            (0, basic_exemption, 0.0),
            (basic_exemption, 500000, 0.05) if basic_exemption < 500000 else None,
            (500000, 1000000, 0.20),
            (1000000, float('inf'), 0.30)
        ]
        # Remove None entries for senior citizens
        slabs = [slab for slab in slabs if slab is not None]
        logger.info(f"compute_regular_tax - Using old regime tax slabs with basic exemption {basic_exemption}: {slabs}")

    tax = 0
    slab_breakdown = []
    
    for lower, upper, rate in slabs:
        if income > lower:
            taxable = min(upper, income) - lower
            slab_tax = taxable * rate
            tax += slab_tax
            slab_breakdown.append({
                "slab": f"{lower}-{upper}",
                "rate": f"{rate*100}%",
                "taxable_amount": round(taxable, 2),
                "tax_on_slab": round(slab_tax, 2)
            })
            logger.info(f"compute_regular_tax - Slab {lower}-{upper} at rate {rate*100}%: Taxable amount {taxable}, Tax on slab: {slab_tax}")
    
    logger.info(f"compute_regular_tax - Total regular tax calculated: {tax}")
    logger.info(f"compute_regular_tax - Full breakdown by slabs: {json.dumps(slab_breakdown, indent=2)}")
    
    return tax

def compute_capital_gains_tax(cap_gains: CapitalGains, regime: str = 'old') -> float:
    """
    Compute capital gains tax with updated rates as per Budget 2024.
    
    Args:
        cap_gains: CapitalGains object containing all capital gains data
        regime: Tax regime ('old' or 'new')
        
    Returns:
        Total capital gains tax (excluding items taxed at slab rates)
    """
    logger.info(f"compute_capital_gains_tax - Starting capital gains tax computation with regime: {regime}")
    logger.info(f"compute_capital_gains_tax - Capital gains input: STCG 111A: {cap_gains.stcg_111a}, "
                f"STCG Other: {cap_gains.stcg_any_other_asset}, STCG Debt MF: {cap_gains.stcg_debt_mutual_fund}, "
                f"LTCG 112A: {cap_gains.ltcg_112a}, LTCG Other: {cap_gains.ltcg_any_other_asset}, "
                f"LTCG Debt MF: {cap_gains.ltcg_debt_mutual_fund}")
    
    # UPDATED: Short-term capital gains on equity (Section 111A) - 20% flat rate (Budget 2024)
    stcg_111a_tax = cap_gains.stcg_111a * 0.20
    logger.info(f"compute_capital_gains_tax - STCG 111A Tax (20% flat rate - Budget 2024): {stcg_111a_tax}")
    
    # UPDATED: Long-term capital gains on equity (Section 112A) - 12.5% flat rate above Rs. 1.25 lakh (Budget 2024)
    ltcg_112a_exemption = min(125000, cap_gains.ltcg_112a)  # Updated exemption limit
    ltcg_112a_taxable = max(0, cap_gains.ltcg_112a - ltcg_112a_exemption)
    ltcg_112a_tax = ltcg_112a_taxable * 0.125  # Updated rate to 12.5%
    logger.info(f"compute_capital_gains_tax - LTCG 112A: Total: {cap_gains.ltcg_112a}, Exemption: {ltcg_112a_exemption}, "
                f"Taxable: {ltcg_112a_taxable}, Tax (12.5% - Budget 2024): {ltcg_112a_tax}")
    
    # UPDATED: Other LTCG taxed at 12.5% (Budget 2024)
    ltcg_other = cap_gains.ltcg_any_other_asset + cap_gains.ltcg_debt_mutual_fund
    ltcg_other_tax = ltcg_other * 0.125  # Updated rate to 12.5%
    logger.info(f"compute_capital_gains_tax - Other LTCG: Total: {ltcg_other}, Tax (12.5% - Budget 2024): {ltcg_other_tax}")
    
    # Other STCG taxed at slab rates - this will be calculated separately with compute_regular_tax
    logger.info(f"compute_capital_gains_tax - STCG to be taxed at slab rates: {cap_gains.stcg_any_other_asset + cap_gains.stcg_debt_mutual_fund}")
    
    total_cg_tax = stcg_111a_tax + ltcg_112a_tax + ltcg_other_tax
    logger.info(f"compute_capital_gains_tax - Total capital gains tax (excluding slab rate items): {total_cg_tax}")
    
    return total_cg_tax

def apply_87a_rebate(tax: float, income: float, regime: str) -> float:
    """
    Apply section 87A rebate with updated limits as per Budget 2025.
    
    Args:
        tax: Tax amount before rebate
        income: Total taxable income
        regime: Tax regime ('old' or 'new')
        
    Returns:
        Tax amount after applying rebate
    """
    logger.info(f"apply_87a_rebate - Applying section 87A rebate with tax: {tax}, income: {income}, regime: {regime}")
    
    original_tax = tax
    if regime == 'old' and income <= 500000:
        rebate_amount = min(12500, tax)
        tax = max(0, tax - rebate_amount)
        logger.info(f"apply_87a_rebate - Old Regime: Income <= 500000, Rebate: {rebate_amount}")
    elif regime == 'new' and income <= 1200000:  # UPDATED: New limit for 12 lakh income (Budget 2025)
        rebate_amount = min(60000, tax)  # UPDATED: Increased rebate to Rs. 60,000 (Budget 2025)
        tax = max(0, tax - rebate_amount)
        logger.info(f"apply_87a_rebate - New Regime: Income <= 1200000, Rebate: {rebate_amount} (Budget 2025)")
    else:
        logger.info(f"apply_87a_rebate - No rebate applicable: Income or regime not eligible")
        rebate_amount = 0
    
    logger.info(f"apply_87a_rebate - Tax before rebate: {original_tax}, Rebate applied: {rebate_amount}, Tax after rebate: {tax}")
    return tax

def apply_standard_deduction(gross_salary: float, regime: str) -> float:
    """
    Apply standard deduction for salaried individuals.
    
    Args:
        gross_salary: Gross salary income
        regime: Tax regime ('old' or 'new')
        
    Returns:
        Standard deduction amount
    """
    if gross_salary <= 0:
        return 0
        
    if regime == 'new':
        standard_deduction = min(75000, gross_salary)  # Rs. 75,000 for new regime
        logger.info(f"apply_standard_deduction - New regime standard deduction: {standard_deduction}")
    else:
        standard_deduction = min(50000, gross_salary)  # Rs. 50,000 for old regime
        logger.info(f"apply_standard_deduction - Old regime standard deduction: {standard_deduction}")
        
    return standard_deduction

def compute_surcharge(base_tax: float, net_income: float) -> dict: #return total_tax,total_surcharge
    logger.info(f"compute_surcharge - Computing surcharge with base tax: {base_tax}, net income: {net_income}")
    
    surcharge_rate = 0
    threshold = 0
    
    if net_income > 50000000:  #5cr
        surcharge_rate = 0.37
        threshold = 50000000  #5cr
        logger.info(f"compute_surcharge - Income > 5cr, rate: 37%")
    elif net_income > 20000000:
        surcharge_rate = 0.25
        threshold = 20000000
        logger.info(f"compute_surcharge - Income > 2cr, rate: 25%")
    elif net_income > 10000000:  #1cr
        surcharge_rate = 0.15
        threshold = 10000000
        logger.info(f"compute_surcharge - Income > 1cr, rate: 15%")
    elif net_income > 5000000:  #50L
        surcharge_rate = 0.10
        threshold = 5000000  #50L
        logger.info(f"compute_surcharge - Income > 50L, rate: 10%")
    else:
        logger.info(f"compute_surcharge - Income <= 50L, no surcharge applicable")

    # Regular surcharge calculation
    reg_surcharge = base_tax * surcharge_rate
    logger.info(f"compute_surcharge - Regular income tax: {base_tax}, Surcharge on regular income: {reg_surcharge}")
    income_above_threshold = max(0, net_income - threshold)
    logger.info(f"compute_surcharge - Income above threshold: {income_above_threshold}")    

    # Apply marginal relief if applicable
    relief_amount = max(0, reg_surcharge - income_above_threshold)
    logger.info(f"compute_surcharge - Relief amount: {relief_amount}")
    
    surcharge = reg_surcharge - relief_amount
    logger.info(f"compute_surcharge - Surcharge: {surcharge}")
    total_tax = base_tax + surcharge
    logger.info(f"compute_surcharge - Total tax: {total_tax}")
    return {"total_tax":total_tax, "surcharge":surcharge}


def calculate_total_tax(emp_id: str, hostname: str) -> float:
    """
    Calculate total tax liability for an employee with comprehensive income sources and deductions.
    
    FIXES APPLIED:
    1. Added all missing income sources (house property, leave encashment, pension, gratuity, etc.)
    2. Fixed deduction calculation method calls
    3. Added standard deduction for salaried income
    4. Updated capital gains calculations with latest rates
    5. Added age-based tax slab calculations
    6. Proper integration of all income heads
    
    Args:
        emp_id: Employee ID
        hostname: Organization hostname
        
    Returns:
        Total tax amount
    """
    logger.info(f"calculate_total_tax() - Starting comprehensive tax calculation for employee ID: {emp_id}, hostname: {hostname}")
    
    # Get the taxation data for the employee from the database
    try:
        logger.info(f"calculate_total_tax() - Fetching taxation data from database")
        taxation_data = get_taxation_by_emp_id(emp_id, hostname)
        # Convert to Taxation object
        taxation = Taxation.from_dict(taxation_data)
        logger.info(f"calculate_total_tax() - Successfully retrieved taxation data: ID={taxation.emp_id}, "
                    f"Age={taxation.emp_age}, Regime={taxation.regime}")
    except Exception as e:
        # If taxation data doesn't exist or can't be retrieved, return 0
        logger.error(f"calculate_total_tax() - Error retrieving taxation data: {str(e)}")
        return 0
    
    # Check if salary and perquisites exist to prevent attribute errors
    try:
        # Get components for calculation
        salary = taxation.salary
        other_sources = taxation.other_sources
        house_property = taxation.house_property  # FIXED: Added missing house property
        cap_gains = taxation.capital_gains
        leave_encashment = taxation.leave_encashment  # FIXED: Added missing leave encashment
        voluntary_retirement = taxation.voluntary_retirement  # FIXED: Added missing VRS
        pension = taxation.pension  # FIXED: Added missing pension
        gratuity = taxation.gratuity  # FIXED: Added missing gratuity
        retrenchment = taxation.retrenchment  # FIXED: Added missing retrenchment
        deductions = taxation.deductions
        regime = taxation.regime
        age = taxation.emp_age
        is_govt_employee = taxation.is_govt_employee
        
        logger.info(f"calculate_total_tax() - Tax calculation parameters - Regime: {regime}, Age: {age}, Govt Employee: {is_govt_employee}")
        
        # ========== INCOME CALCULATION ==========
        
        # 1. SALARY INCOME with Standard Deduction, LWP Adjustment, and Salary Change Projection
        # First try to get salary projection considering mid-year changes
        salary_projection = None
        try:
            from services.salary_history_service import calculate_annual_salary_projection
            salary_projection = calculate_annual_salary_projection(emp_id, taxation.tax_year, hostname)
            logger.info(f"calculate_total_tax() - Salary projection found: {salary_projection.salary_changes_count} changes")
        except Exception as e:
            logger.warning(f"calculate_total_tax() - Could not calculate salary projection: {str(e)}")
        
        # Then try to get LWP-adjusted salary from actual payout records
        lwp_adjusted_salary = calculate_lwp_adjusted_annual_salary(emp_id, hostname, taxation.tax_year)
        
        # Determine which salary calculation method to use (priority order):
        # 1. LWP-adjusted salary (actual payouts) - most accurate
        # 2. Salary projection (considering mid-year changes) - second most accurate
        # 3. Static taxation data (fallback) - least accurate
        
        if lwp_adjusted_salary:
            # Use actual earned salary considering LWP (highest priority)
            gross_salary_income = lwp_adjusted_salary["actual_annual_gross"]
            logger.info(f"calculate_total_tax() - Using LWP-adjusted salary: {gross_salary_income} "
                       f"(LWP days: {lwp_adjusted_salary['total_lwp_days']}, "
                       f"Adjustment ratio: {lwp_adjusted_salary['lwp_adjustment_ratio']:.4f})")
            
            # Update tax breakup with LWP details
            salary_calculation_details = {
                "method_used": "lwp_adjusted",
                "lwp_adjustment_applied": True,
                "theoretical_annual_salary": salary.total_taxable_income_per_slab(regime),
                "actual_annual_salary": gross_salary_income,
                "total_lwp_days": lwp_adjusted_salary["total_lwp_days"],
                "lwp_adjustment_ratio": lwp_adjusted_salary["lwp_adjustment_ratio"],
                "lwp_salary_reduction": salary.total_taxable_income_per_slab(regime) - gross_salary_income,
                "salary_changes_count": salary_projection.salary_changes_count if salary_projection else 0
            }
        elif salary_projection and salary_projection.salary_changes_count > 0:
            # Use salary projection considering mid-year changes (second priority)
            gross_salary_income = salary_projection.projected_annual_gross
            logger.info(f"calculate_total_tax() - Using salary projection: {gross_salary_income} "
                       f"(Salary changes: {salary_projection.salary_changes_count}, "
                       f"Last change: {salary_projection.last_change_date})")
            
            salary_calculation_details = {
                "method_used": "salary_projection",
                "lwp_adjustment_applied": False,
                "theoretical_annual_salary": salary.total_taxable_income_per_slab(regime),
                "projected_annual_salary": gross_salary_income,
                "salary_changes_count": salary_projection.salary_changes_count,
                "last_change_date": str(salary_projection.last_change_date),
                "projection_calculation_date": str(salary_projection.calculation_date),
                "total_lwp_days": 0,
                "lwp_adjustment_ratio": 1.0,
                "salary_projection_difference": gross_salary_income - salary.total_taxable_income_per_slab(regime)
            }
        else:
            # Fallback to theoretical salary from taxation data (lowest priority)
            gross_salary_income = salary.total_taxable_income_per_slab(regime)
            logger.info(f"calculate_total_tax() - Using theoretical salary (no payout records or salary changes): {gross_salary_income}")
            
            salary_calculation_details = {
                "method_used": "static_taxation_data",
                "lwp_adjustment_applied": False,
                "theoretical_annual_salary": gross_salary_income,
                "actual_annual_salary": gross_salary_income,
                "total_lwp_days": 0,
                "lwp_adjustment_ratio": 1.0,
                "lwp_salary_reduction": 0,
                "salary_changes_count": 0
            }
        
        standard_deduction = apply_standard_deduction(gross_salary_income, regime)  # FIXED: Added standard deduction
        salary_income = max(0, gross_salary_income - standard_deduction)
        logger.info(f"calculate_total_tax() - Gross salary income: {gross_salary_income}, Standard deduction: {standard_deduction}, Net salary income: {salary_income}")
        
        # 2. INCOME FROM OTHER SOURCES (with proper 80TTA/80TTB treatment)
        other_income = other_sources.total_taxable_income_per_slab(regime, age)
        logger.info(f"calculate_total_tax() - Other sources taxable income: {other_income}")
        
        # 3. HOUSE PROPERTY INCOME (FIXED: Was completely missing)
        house_property_income = house_property.total_taxable_income_per_slab(regime)
        logger.info(f"calculate_total_tax() - House property income: {house_property_income}")
        
        # 4. LEAVE ENCASHMENT INCOME (FIXED: Was missing)
        # Need to get service years and average salary for exemption calculation
        try:
            user_data = get_user_by_emp_id(emp_id, hostname)
            if user_data and 'doj' in user_data and user_data['doj']:
                doj = datetime.datetime.strptime(user_data.get('doj', ''), '%Y-%m-%d')
                today = datetime.datetime.now()
                service_years = relativedelta(today, doj).years
                # Use basic + DA as average monthly salary for leave encashment calculation
                average_monthly_salary = (salary.basic + salary.dearness_allowance) / 12 if (salary.basic + salary.dearness_allowance) > 0 else 100000
            else:
                service_years = 0
                average_monthly_salary = 100000
        except Exception as e:
            logger.warning(f"calculate_total_tax() - Could not calculate service years: {str(e)}")
            service_years = 0
            average_monthly_salary = 100000
            
        leave_encashment_income = leave_encashment.total_taxable_income_per_slab(
            regime=regime, 
            is_govt_employee=is_govt_employee, 
            service_years=service_years, 
            average_monthly_salary=average_monthly_salary
        )
        logger.info(f"calculate_total_tax() - Leave encashment taxable income: {leave_encashment_income}")
        
        # 5. VOLUNTARY RETIREMENT INCOME (FIXED: Was missing)
        vrs_income = 0
        if hasattr(voluntary_retirement, 'total_taxable_income_per_slab'):
            vrs_income = voluntary_retirement.total_taxable_income_per_slab(
                regime=regime, 
                age=age, 
                service_years=service_years, 
                last_drawn_monthly_salary=average_monthly_salary
            )
        logger.info(f"calculate_total_tax() - VRS taxable income: {vrs_income}")
        
        # 6. PENSION INCOME (FIXED: Was missing)
        pension_income = 0
        if hasattr(pension, 'total_taxable_income_per_slab_computed'):
            pension_income += pension.total_taxable_income_per_slab_computed(
                regime=regime, 
                is_govt_employee=is_govt_employee, 
                is_gratuity_received=gratuity.gratuity_income > 0
            )
        if hasattr(pension, 'total_taxable_income_per_slab_uncomputed'):
            pension_income += pension.total_taxable_income_per_slab_uncomputed(regime=regime)
        logger.info(f"calculate_total_tax() - Pension taxable income: {pension_income}")
        
        # 7. GRATUITY INCOME (FIXED: Was missing)
        gratuity_income = 0
        if hasattr(gratuity, 'total_taxable_income_per_slab'):
            try:
                doj_date = datetime.datetime.strptime(user_data.get('doj', ''), '%Y-%m-%d') if user_data and 'doj' in user_data else None
                dol_date = datetime.datetime.now()  # Assuming current date as date of leaving for calculation
                gratuity_income = gratuity.total_taxable_income_per_slab(
                    regime=regime,
                    doj=doj_date,
                    dol=dol_date,
                    last_drawn_monthly_salary=average_monthly_salary,
                    is_govt_employee=is_govt_employee
                )
            except Exception as e:
                logger.warning(f"calculate_total_tax() - Error calculating gratuity: {str(e)}")
                gratuity_income = 0
        logger.info(f"calculate_total_tax() - Gratuity taxable income: {gratuity_income}")
        
        # 8. RETRENCHMENT COMPENSATION (FIXED: Was missing)
        retrenchment_income = 0
        if hasattr(retrenchment, 'total_taxable_income_per_slab') and retrenchment.is_provided:
            try:
                doj_date = datetime.datetime.strptime(user_data.get('doj', ''), '%Y-%m-%d') if user_data and 'doj' in user_data else None
                dol_date = datetime.datetime.now()
                retrenchment_income = retrenchment.total_taxable_income_per_slab(
                    regime=regime,
                    doj=doj_date,
                    dol=dol_date,
                    last_drawn_monthly_salary=average_monthly_salary
                )
            except Exception as e:
                logger.warning(f"calculate_total_tax() - Error calculating retrenchment: {str(e)}")
                retrenchment_income = 0
        logger.info(f"calculate_total_tax() - Retrenchment taxable income: {retrenchment_income}")
        
        # 9. CAPITAL GAINS (Short-term gains taxed at slab rates)
        stcg_slab_rate = cap_gains.total_stcg_slab_rate()
        logger.info(f"calculate_total_tax() - STCG at slab rates: {stcg_slab_rate}")
        
        # Calculate GROSS INCOME (all sources combined)
        gross_income = (salary_income + other_income + house_property_income + 
                       leave_encashment_income + vrs_income + pension_income + 
                       gratuity_income + retrenchment_income + stcg_slab_rate)
        logger.info(f"calculate_total_tax() - Total gross income before deductions: {gross_income}")
        
        # ========== DEDUCTION CALCULATION ==========
        
        # FIXED: Corrected method call with proper parameters
        total_deductions = 0
        if regime == 'old':  # Deductions only apply in old regime
            total_deductions = deductions.total_deduction_per_slab(
                salary=salary, 
                income_from_other_sources=other_sources, 
                regime=regime, 
                is_govt_employee=is_govt_employee, 
                age=age, 
                parent_age=age  # Assuming same age for parent age if not provided
            )
            logger.info(f"calculate_total_tax() - Total deductions (old regime): {total_deductions}")
        else:
            logger.info(f"calculate_total_tax() - No deductions applicable (new regime)")
        
        # Calculate NET TAXABLE INCOME
        net_income = max(0, gross_income - total_deductions)
        logger.info(f"calculate_total_tax() - Net taxable income {gross_income} - {total_deductions}: {net_income}")
        
        # ========== TAX CALCULATION ==========
        
        # 1. Tax on regular income (FIXED: Added age parameter for senior citizen slabs)
        tax_on_regular = compute_regular_tax(net_income, regime, age)
        logger.info(f"calculate_total_tax() - Tax on regular income: {tax_on_regular}")
        
        # 2. Tax on STCG at special rates (FIXED: Updated rates)
        tax_on_stcg_special = cap_gains.tax_on_stcg_special_rate()
        logger.info(f"calculate_total_tax() - Tax on STCG at special rate (20%): {tax_on_stcg_special}")

        # 3. Tax on LTCG at special rates (FIXED: Updated rates)
        tax_on_ltcg_special = cap_gains.tax_on_ltcg_special_rate()
        logger.info(f"calculate_total_tax() - Tax on LTCG at special rate (12.5%): {tax_on_ltcg_special}")

        # Total base tax
        base_tax = tax_on_regular + tax_on_stcg_special + tax_on_ltcg_special
        logger.info(f"calculate_total_tax() - Base tax (before rebate/surcharge/cess): {base_tax}")
        
        # Apply rebate under section 87A (FIXED: Updated rebate limits)
        tax_after_rebate = apply_87a_rebate(base_tax, net_income, regime)
        logger.info(f"calculate_total_tax() - Tax after Section 87A rebate: {tax_after_rebate}")
        
        # Calculate surcharge
        surcharge_result = compute_surcharge(tax_after_rebate, net_income)
        total_tax = surcharge_result["total_tax"]
        surcharge = surcharge_result["surcharge"]
        logger.info(f"calculate_total_tax() - Surcharge on tax: {surcharge}")
        
        # Add Health and Education Cess (4%)
        cess = total_tax * 0.04
        logger.info(f"calculate_total_tax() - Health and Education Cess (4%): {cess}")
        
        final_tax = total_tax + cess
        logger.info(f"calculate_total_tax() - Final tax amount: {final_tax}")
        
        # Prepare comprehensive tax breakup
        tax_breakup = {
            "base_tax": round(base_tax),
            "tax_after_rebate": round(tax_after_rebate),
            "surcharge": round(surcharge),
            "cess": round(cess),
            "total_tax": round(final_tax),
            "details": {
                "gross_salary_income": round(gross_salary_income),
                "standard_deduction": round(standard_deduction),
                "net_salary_income": round(salary_income),
                "other_sources_income": round(other_income),
                "house_property_income": round(house_property_income),
                "leave_encashment_income": round(leave_encashment_income),
                "vrs_income": round(vrs_income),
                "pension_income": round(pension_income),
                "gratuity_income": round(gratuity_income),
                "retrenchment_income": round(retrenchment_income),
                "stcg_slab_rate": round(stcg_slab_rate),
                "stcg_special_rate_tax": round(tax_on_stcg_special),
                "ltcg_special_rate_tax": round(tax_on_ltcg_special),
                "gross_income": round(gross_income),
                "total_deductions": round(total_deductions),
                "net_income": round(net_income),
                "regime": regime,
                "age": age,
                "is_govt_employee": is_govt_employee
            },
            "lwp_adjustment": {
                "applied": lwp_details["lwp_adjustment_applied"],
                "theoretical_annual_salary": round(lwp_details["theoretical_annual_salary"]),
                "actual_annual_salary": round(lwp_details["actual_annual_salary"]),
                "total_lwp_days": lwp_details["total_lwp_days"],
                "lwp_adjustment_ratio": round(lwp_details["lwp_adjustment_ratio"], 4),
                "salary_reduction_due_to_lwp": round(lwp_details["lwp_salary_reduction"]),
                "tax_savings_due_to_lwp": round((lwp_details["lwp_salary_reduction"] * (tax_on_regular / max(net_income, 1))) if lwp_details["lwp_salary_reduction"] > 0 else 0)
            }
        }
        logger.info(f"calculate_total_tax() - Comprehensive tax breakdown: {json.dumps(tax_breakup, indent=2)}")
        
        # Update tax breakup in taxation object
        taxation.tax_breakup = tax_breakup
        taxation.total_tax = round(final_tax)
        taxation.tax_payable = round(final_tax)
        taxation.tax_due = max(0, taxation.tax_payable - (taxation.tax_paid or 0))
        taxation.tax_refundable = max(0, (taxation.tax_paid or 0) - taxation.tax_payable)
        taxation.tax_pending = taxation.tax_due
        
        logger.info(f"calculate_total_tax() - Updated taxation object: Tax payable: {taxation.tax_payable}, "
                    f"Tax paid: {taxation.tax_paid}, Tax due: {taxation.tax_due}, "
                    f"Tax refundable: {taxation.tax_refundable}, Tax pending: {taxation.tax_pending}")
        
        # Save updated taxation details
        try:
            logger.info(f"calculate_total_tax() - Saving updated taxation details to database")
            
            # Convert to dictionary and ensure all fields are properly serialized
            taxation_dict = _ensure_serializable(taxation.to_dict())
            
            # Add update timestamp
            taxation_dict["updated_at"] = datetime.datetime.now()
            
            # Use the save_taxation function to handle database operations
            save_taxation(taxation_dict, hostname)
            
            logger.info(f"calculate_total_tax() - Successfully saved taxation details")
        except Exception as e:
            logger.error(f"calculate_total_tax() - Error saving taxation details: {str(e)}")
        
        # Return rounded value
        logger.info(f"calculate_total_tax() - Completed comprehensive tax calculation for {emp_id}, Final Tax: {round(final_tax)}")
        return round(final_tax)
        
    except AttributeError as e:
        logger.error(f"calculate_total_tax() - Error in tax calculation, attribute error: {str(e)}")
        # Return 0 or existing tax value if available
        return getattr(taxation, 'total_tax', 0)
    except Exception as e:
        logger.error(f"calculate_total_tax() - Unexpected error in tax calculation: {str(e)}")
        return getattr(taxation, 'total_tax', 0)

def calculate_and_save_tax(emp_id: str, hostname: str, emp_age: int = None, is_govt_employee: bool = False, 
                            tax_year: str = None, regime: str = None,
                            salary: SalaryComponents = None, other_sources: IncomeFromOtherSources = None,
                            capital_gains: CapitalGains = None, deductions: DeductionComponents = None,
                            leave_encashment: LeaveEncashment = None, voluntary_retirement: VoluntaryRetirement = None,
                            retrenchment: RetrenchmentCompensation = None, pension: Pension = None,
                            gratuity: Gratuity = None, house_property: IncomeFromHouseProperty = None) -> Taxation:
    """
    Calculate the tax and save to the database
    """
    logger.info(f"calculate_and_save_tax - Starting tax calculation and saving for employee ID: {emp_id}")
    logger.info(f"calculate_and_save_tax - Parameters - emp_age: {emp_age}, is_govt_employee: {is_govt_employee}, regime: {regime}, "
                f"salary provided: {salary is not None}, other_sources provided: {other_sources is not None}, "
                f"capital_gains provided: {capital_gains is not None}, deductions provided: {deductions is not None}, "
                f"leave_encashment provided: {leave_encashment is not None}, "
                f"voluntary_retirement provided: {voluntary_retirement is not None}")
    
    # Get current tax year if not provided
    if not tax_year:
        current_date = datetime.datetime.now()
        current_month = current_date.month
        current_year = current_date.year
        
        # In India, financial year starts from April (month index 4)
        # If current month is January to March, FY is previous year to current year
        # If current month is April to December, FY is current year to next year
        if current_month < 4:  # January to March
            tax_year = f"{current_year-1}-{current_year}"
        else:  # April to December
            tax_year = f"{current_year}-{current_year+1}"
        
        logger.info(f"calculate_and_save_tax - Auto-determined tax year: {tax_year}")
    
    if emp_age == 0:
        # Get user age
        try:
            logger.info(f"calculate_and_save_tax - Fetching user data to determine age")
            user_data = get_user_by_emp_id(emp_id, hostname)
            if user_data and 'dob' in user_data and user_data['dob']:
                dob = datetime.datetime.strptime(user_data.get('dob', ''), '%Y-%m-%d')
                today = datetime.datetime.now()
                age_delta = relativedelta(today, dob)
                emp_age = age_delta.years
                logger.info(f"calculate_and_save_tax - Calculated age for user: {emp_age} years")
            else:   
                logger.warning(f"calculate_and_save_tax - No DOB found for user, defaulting age to 0")
        except Exception as e:
            logger.error(f"calculate_and_save_tax - Could not calculate age for {emp_id}: {str(e)}")
            
    # Try to fetch existing taxation data
    try:
        logger.info(f"calculate_and_save_tax - Trying to fetch existing taxation data for employee: {emp_id}")
        taxation_data = get_taxation_by_emp_id(emp_id, hostname)
        # Convert to Taxation object
        taxation = Taxation.from_dict(taxation_data)
        logger.info(f"calculate_and_save_tax - Found existing taxation data for employee: {emp_id},"
                    f" age: {taxation.emp_age}, tax year: {taxation.tax_year}, regime: {taxation.regime}")
        
        # Update with provided values
        if regime:
            logger.info(f"calculate_and_save_tax - Updating regime from {taxation.regime} to {regime}")
            taxation.regime = regime
        if tax_year:
            logger.info(f"calculate_and_save_tax - Updating tax year from {taxation.tax_year} to {tax_year}")
            taxation.tax_year = tax_year
        if salary:
            logger.info(f"calculate_and_save_tax - Updating salary information")
            taxation.salary = salary
        if other_sources:
            logger.info(f"calculate_and_save_tax - Updating other sources information")
            taxation.other_sources = other_sources
        if house_property:
            logger.info(f"calculate_and_save_tax - Updating house property information")
            taxation.house_property = house_property
        if capital_gains:
            logger.info(f"calculate_and_save_tax - Updating capital gains information")
            taxation.capital_gains = capital_gains
        if deductions:
            logger.info(f"calculate_and_save_tax - Updating deductions information")
            taxation.deductions = deductions
        if leave_encashment:
            logger.info(f"calculate_and_save_tax - Updating leave encashment information")
            taxation.leave_encashment = leave_encashment
        if voluntary_retirement:
            logger.info(f"calculate_and_save_tax - Updating voluntary retirement information")
            taxation.voluntary_retirement = voluntary_retirement
        if retrenchment:
            logger.info(f"calculate_and_save_tax - Updating retrenchment information")
            taxation.retrenchment = retrenchment
        if pension:
            logger.info(f"calculate_and_save_tax - Updating pension information")
            taxation.pension = pension
        if gratuity:
            logger.info(f"calculate_and_save_tax - Updating gratuity information")
            taxation.gratuity = gratuity
    except Exception as e:
        logger.info(f"calculate_and_save_tax - No existing taxation data found for {emp_id}, creating new taxation object. Error: {str(e)}")
        
        
        # Create new taxation object if not found
        logger.info(f"calculate_and_save_tax - Creating new taxation object with emp_id: {emp_id}, age: {emp_age}, regime: {regime or 'old'}, tax_year: {tax_year}")
        taxation = Taxation(
            emp_id=emp_id,
            emp_age=emp_age,
            regime=regime or 'old',
            salary=salary or SalaryComponents(),
            other_sources=other_sources or IncomeFromOtherSources(),
            house_property=house_property or IncomeFromHouseProperty(),
            capital_gains=capital_gains or CapitalGains(),
            leave_encashment=leave_encashment or LeaveEncashment(),
            voluntary_retirement=voluntary_retirement or VoluntaryRetirement(),
            retrenchment=retrenchment or RetrenchmentCompensation(),    
            deductions=deductions or DeductionComponents(),
            pension=pension or Pension(),
            gratuity=gratuity or Gratuity(),
            tax_year=tax_year,
            filing_status='draft',
            total_tax=0,
            tax_breakup={},
            tax_payable=0,
            tax_paid=0,
            tax_due=0,
            tax_refundable=0,
            tax_pending=0,
            is_govt_employee=False
        )
        
    # Save the taxation data
    try:
        logger.info(f"calculate_and_save_tax - Saving taxation data to database")
        
        # Get dictionary representation and ensure serializable
        taxation_dict = _ensure_serializable(taxation.to_dict())
        
        # Add update timestamp
        taxation_dict["updated_at"] = datetime.datetime.now()
        
        # Use database function to save
        save_taxation(taxation_dict, hostname)
        logger.info(f"calculate_and_save_tax - Successfully saved taxation data")
    except Exception as e:
        logger.error(f"calculate_and_save_tax - Error saving taxation data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving taxation data: {str(e)}")
    
    # Calculate the tax
    try:
        logger.info(f"calculate_and_save_tax - Calculating total tax")
        total_tax = calculate_total_tax(emp_id, hostname)
        logger.info(f"calculate_and_save_tax - Tax calculation completed successfully, total tax: {total_tax}")
    except Exception as e:
        logger.error(f"calculate_and_save_tax - Error calculating tax: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error calculating tax: {str(e)}")
    
    # Retrieve the updated taxation data
    try:
        logger.info(f"calculate_and_save_tax - Retrieving updated taxation data with calculated tax")
        updated_taxation_data = get_taxation_by_emp_id(emp_id, hostname)
        updated_taxation = Taxation.from_dict(updated_taxation_data)
        logger.info(f"calculate_and_save_tax - Successfully retrieved updated taxation data with tax: {updated_taxation.total_tax}")
        return updated_taxation
    except Exception as e:
        logger.error(f"calculate_and_save_tax - Error retrieving updated taxation data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving updated taxation data: {str(e)}")

def get_or_create_taxation_by_emp_id(emp_id: str, hostname: str) -> dict:
    """
    Retrieves taxation data for an employee, or creates it with default values if it doesn't exist.
    
    Parameters:
    - emp_id: Employee ID
    - hostname: Organization hostname
    
    Returns:
    - Dictionary containing taxation data
    """
    try:
        # Try to fetch existing taxation data
        taxation_data = get_taxation_by_emp_id(emp_id, hostname)
        logger.info(f"get_or_create_taxation_by_emp_id - Retrieved existing taxation data for {emp_id}")
        return taxation_data
    except HTTPException as e:
        if e.status_code == 404:
            logger.info(f"get_or_create_taxation_by_emp_id - Taxation data not found for {emp_id}, creating defaults")
            # Taxation not found, create default
            return create_default_taxation(emp_id, hostname)
        else:
            # Re-raise other exceptions
            logger.error(f"Error fetching taxation data: {str(e)}")
            raise

def create_default_taxation(emp_id: str, hostname: str) -> dict:
    """
    Creates default taxation data for a user.
    
    Parameters:
    - emp_id: Employee ID
    - hostname: Organization hostname
    
    Returns:
    - Dictionary containing new taxation data
    """
    try:
        # Get user data to extract age
        user_data = get_user_by_emp_id(emp_id, hostname)
        if not user_data:
            logger.error(f"User {emp_id} not found")
            raise HTTPException(status_code=404, detail=f"User {emp_id} not found")
        
        # Calculate age from date of birth
        emp_age = 0
        try:
            dob = datetime.datetime.strptime(user_data.get('dob', ''), '%Y-%m-%d')
            logger.info(f"Calculated age for {emp_id}: {dob}")
            today = datetime.datetime.now()
            age_delta = relativedelta(today, dob)
            emp_age = age_delta.years
            logger.info(f"Calculated age for {emp_id}: {emp_age} years")
        except (ValueError, AttributeError) as e:
            logger.warning(f"Could not calculate age for {emp_id}: {str(e)}")
        
        # Check if organization is governmental
        is_govt_emp = False
        try:
            is_govt_emp = is_govt_organisation(hostname)
            logger.info(f"Detected government employee status for {emp_id}: {is_govt_emp}")
        except Exception as e:
            logger.warning(f"Could not determine government employee status: {str(e)}")
        
        # Get current financial year
        current_date = datetime.datetime.now()
        current_month = current_date.month
        current_year = current_date.year
        
        if current_month < 4:  # January to March
            tax_year = f"{current_year-1}-{current_year}"
        else:  # April to December
            tax_year = f"{current_year}-{current_year+1}"
        
        # Create default taxation object
        default_perquisites = Perquisites()
        
        default_salary = SalaryComponents(
            basic=0,
            dearness_allowance=0,
            hra=0,
            actual_rent_paid=0,
            hra_city='Others',
            hra_percentage=0.4,
            special_allowance=0,
            bonus=0,
            perquisites=default_perquisites,
            hills_high_altd_allowance=0,
            hills_high_altd_exemption_limit=0,
            border_remote_allowance=0,
            border_remote_exemption_limit=0,
            transport_employee_allowance=0,
            children_education_allowance=0,
            children_education_count=0,
            children_education_months=0,
            hostel_allowance=0,
            hostel_count=0,
            hostel_months=0,
            transport_allowance=0,
            transport_months=0,
            underground_mines_allowance=0,
            underground_mines_months=0,
            govt_employee_entertainment_allowance=0
        )
        
        default_other_sources = IncomeFromOtherSources(
            regime='old',
            age=emp_age,
            interest_savings=0,
            interest_fd=0,
            interest_rd=0,
            dividend_income=0,
            gifts=0,
            other_interest=0,
            business_professional_income=0,
            other_income=0
        )

        default_house_property = IncomeFromHouseProperty(
            property_address='',
            occupancy_status='Self-Occupied',
            rent_income=0,
            property_tax=0,
            interest_on_home_loan=0,
            pre_construction_loan_interest=0
        )
        
        default_capital_gains = CapitalGains(
            stcg_111a=0,
            stcg_any_other_asset=0,
            stcg_debt_mutual_fund=0,
            ltcg_112a=0,
            ltcg_any_other_asset=0,
            ltcg_debt_mutual_fund=0
        )

        default_leave_encashment = LeaveEncashment(
            leave_encashment_income_received=0,
            leave_encashed=0,
            is_deceased=False,
            during_employment=False
        )
        
        default_voluntary_retirement = VoluntaryRetirement(
            is_vrs_requested=False,
            voluntary_retirement_amount=0
        )

        default_retrenchment = RetrenchmentCompensation(
            retrenchment_amount=0,
            is_provided=False
        )
        
        default_pension = Pension(
            total_pension_income=0,
            computed_pension_percentage=0,
            uncomputed_pension_frequency='Monthly',
            uncomputed_pension_amount=0
        )

        default_gratuity = Gratuity(
            gratuity_income=0
        )
        
        default_deductions = DeductionComponents(
            regime='old',
            age=emp_age,
            section_80c_lic=0,
            section_80c_epf=0,
            section_80c_ssp=0,
            section_80c_nsc=0,
            section_80c_ulip=0,
            section_80c_tsmf=0,
            section_80c_tffte2c=0,
            section_80c_paphl=0,
            section_80c_sdpphp=0,
            section_80c_tsfdsb=0,
            section_80c_scss=0,
            section_80c_others=0,
            section_80ccc_ppic=0,
            section_80ccd_1_nps=0,
            section_80ccd_1b_additional=0,
            section_80ccd_2_enps=0,
            section_80d_hisf=0,
            section_80d_phcs=0,
            section_80d_hi_parent=0,
            section_80dd=0,
            relation_80dd='',
            disability_percentage='',
            section_80ddb=0,
            relation_80ddb='',
            age_80ddb=0,
            section_80e_interest=0,
            relation_80e='',
            section_80eeb=0,
            section_80g_100_wo_ql=0,
            section_80g_100_head='',
            section_80g_50_wo_ql=0,
            section_80g_50_head='',
            section_80g_100_ql=0,
            section_80g_100_ql_head='',
            section_80g_50_ql=0,
            section_80g_50_ql_head='',
            section_80ggc=0,
            section_80u=0,
            disability_percentage_80u=''
        )
        
        default_taxation = Taxation(
            emp_id=emp_id,
            emp_age=emp_age,
            salary=default_salary,
            other_sources=default_other_sources,
            house_property=default_house_property,
            capital_gains=default_capital_gains,
            leave_encashment=default_leave_encashment,
            voluntary_retirement=default_voluntary_retirement,
            retrenchment=default_retrenchment,
            deductions=default_deductions,
            pension=default_pension,
            gratuity=default_gratuity,
            regime='old',
            total_tax=0,
            tax_breakup={},
            tax_year=tax_year,
            filing_status='draft',
            tax_payable=0,
            tax_paid=0,
            tax_due=0,
            tax_refundable=0,
            tax_pending=0,
            is_govt_employee=is_govt_emp
        )
        
        # Save the default taxation data
        default_dict = _ensure_serializable(default_taxation.to_dict())
        saved_taxation = save_taxation(default_dict, hostname)
        logger.info(f"Created default taxation data for {emp_id}")
        
        return saved_taxation
    except Exception as e:
        logger.error(f"Error creating default taxation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating default taxation: {str(e)}")

def compute_vrs_from_user_data(emp_id: str, hostname: str) -> float:
    """
    Compute the VRS value for a user based on their profile data.
    
    Parameters:
    - emp_id: Employee ID
    - hostname: Organization hostname
    
    Returns:
    - Computed VRS value
    """
    try:
        # Get user data to calculate age and service years
        user_data = get_user_by_emp_id(emp_id, hostname)
        if not user_data:
            logger.error(f"User {emp_id} not found")
            raise HTTPException(status_code=404, detail=f"User {emp_id} not found")
        
        # Default monthly salary
        last_drawn_monthly_salary = 100000
        
        # Calculate age from date of birth
        try:
            dob = datetime.datetime.strptime(user_data.get('dob', ''), '%Y-%m-%d')
            today = datetime.datetime.now()
            age_delta = relativedelta(today, dob)
            age = age_delta.years
            logger.info(f"Calculated age for {emp_id}: {age} years")
        except (ValueError, AttributeError) as e:
            logger.error(f"Could not calculate age for {emp_id}: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Invalid date of birth for user {emp_id}")
        
        # Calculate service years from date of joining
        try:
            doj = datetime.datetime.strptime(user_data.get('doj', ''), '%Y-%m-%d')
            service_delta = relativedelta(today, doj)
            service_years = service_delta.years
            logger.info(f"Calculated service years for {emp_id}: {service_years} years")
        except (ValueError, AttributeError) as e:
            logger.error(f"Could not calculate service years for {emp_id}: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Invalid date of joining for user {emp_id}")
        
        # Create a VoluntaryRetirement instance and compute VRS value
        vrs = VoluntaryRetirement()
        vrs_value = vrs.compute_vrs_value(
            age=age,
            service_years=service_years,
            last_drawn_monthly_salary=last_drawn_monthly_salary
        )
        
        logger.info(f"Computed VRS value for {emp_id}: {vrs_value}")
        return vrs_value
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error computing VRS value from user data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error computing VRS value: {str(e)}")

def calculate_lwp_adjusted_annual_salary(emp_id: str, hostname: str, tax_year: str = None) -> dict:
    """
    Calculate actual annual salary considering LWP deductions from payout records.
    
    Args:
        emp_id: Employee ID
        hostname: Organization hostname
        tax_year: Tax year in format "YYYY-YYYY" (e.g., "2024-2025")
        
    Returns:
        Dictionary with actual annual salary components and LWP adjustment details
    """
    logger.info(f"calculate_lwp_adjusted_annual_salary - Starting LWP-adjusted salary calculation for {emp_id}")
    
    try:
        # Import here to avoid circular imports
        from database.payout_database import PayoutDatabase
        
        # Determine tax year if not provided
        if not tax_year:
            current_date = datetime.datetime.now()
            current_month = current_date.month
            current_year = current_date.year
            
            if current_month < 4:  # January to March
                tax_year = f"{current_year-1}-{current_year}"
                year_to_query = current_year
            else:  # April to December
                tax_year = f"{current_year}-{current_year+1}"
                year_to_query = current_year
        else:
            # Extract year from tax_year format "YYYY-YYYY"
            year_to_query = int(tax_year.split('-')[0])
        
        logger.info(f"calculate_lwp_adjusted_annual_salary - Using tax year: {tax_year}, querying year: {year_to_query}")
        
        # Get payout database
        payout_db = PayoutDatabase(hostname)
        
        # Get all payouts for the employee for the tax year
        payouts = payout_db.get_employee_payouts(emp_id, year=year_to_query)
        logger.info(f"calculate_lwp_adjusted_annual_salary - Found {len(payouts)} payout records for {emp_id}")
        
        if not payouts:
            logger.warning(f"calculate_lwp_adjusted_annual_salary - No payout records found for {emp_id}, returning None")
            return None
        
        # Calculate actual annual amounts from payouts
        actual_annual_basic = sum(payout.basic_salary for payout in payouts)
        actual_annual_da = sum(payout.da for payout in payouts)
        actual_annual_hra = sum(payout.hra for payout in payouts)
        actual_annual_special_allowance = sum(payout.special_allowance for payout in payouts)
        actual_annual_bonus = sum(payout.bonus for payout in payouts)
        
        # Calculate total working days and LWP days
        total_working_days = sum(getattr(payout, 'working_days_in_period', 0) for payout in payouts)
        total_lwp_days = sum(getattr(payout, 'lwp_days', 0) for payout in payouts)
        total_effective_working_days = sum(getattr(payout, 'effective_working_days', 0) for payout in payouts)
        
        # Calculate total days in the year (for months with payouts)
        total_days_in_year = sum(getattr(payout, 'total_days_in_month', 0) for payout in payouts)
        
        # Calculate LWP adjustment ratio
        lwp_adjustment_ratio = total_effective_working_days / total_working_days if total_working_days > 0 else 1.0
        
        actual_annual_gross = (actual_annual_basic + actual_annual_da + actual_annual_hra + 
                              actual_annual_special_allowance + actual_annual_bonus)
        
        result = {
            "actual_annual_basic": actual_annual_basic,
            "actual_annual_da": actual_annual_da,
            "actual_annual_hra": actual_annual_hra,
            "actual_annual_special_allowance": actual_annual_special_allowance,
            "actual_annual_bonus": actual_annual_bonus,
            "actual_annual_gross": actual_annual_gross,
            "total_working_days": total_working_days,
            "total_lwp_days": total_lwp_days,
            "total_effective_working_days": total_effective_working_days,
            "total_days_in_year": total_days_in_year,
            "lwp_adjustment_ratio": lwp_adjustment_ratio,
            "months_with_payouts": len(payouts),
            "tax_year": tax_year
        }
        
        logger.info(f"calculate_lwp_adjusted_annual_salary - LWP-adjusted salary calculated: "
                   f"Gross: {actual_annual_gross}, LWP days: {total_lwp_days}, "
                   f"Adjustment ratio: {lwp_adjustment_ratio:.4f}")
        
        return result
        
    except Exception as e:
        logger.error(f"calculate_lwp_adjusted_annual_salary - Error calculating LWP-adjusted salary: {str(e)}")
        return None
