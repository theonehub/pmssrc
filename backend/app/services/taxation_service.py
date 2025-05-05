from models.taxation import SalaryComponents, IncomeFromOtherSources, CapitalGains, DeductionComponents, Taxation, Perquisites
from database.taxation_database import get_taxation_by_emp_id, save_taxation
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

def compute_regular_tax(income: float, regime: str = 'old') -> float:
    logger.info(f"COMPUTE_REGULAR_TAX - Starting regular tax computation with income: {income} and regime: {regime}")
    
    if regime == 'new':
        slabs = [
            (0, 300000, 0.0),
            (300001, 600000, 0.05),
            (600001, 900000, 0.10),
            (900001, 1200000, 0.15),
            (1200001, 1500000, 0.20),
            (1500001, float('inf'), 0.30)
        ]
        logger.debug(f"COMPUTE_REGULAR_TAX - Using new regime tax slabs: {slabs}")
    else:
        slabs = [
            (0, 250000, 0.0),
            (250001, 500000, 0.05),
            (500001, 1000000, 0.20),
            (1000001, float('inf'), 0.30)
        ]
        logger.debug(f"COMPUTE_REGULAR_TAX - Using old regime tax slabs: {slabs}")

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
            logger.debug(f"COMPUTE_REGULAR_TAX - Slab {lower}-{upper} at rate {rate*100}%: Taxable amount {taxable}, Tax on slab: {slab_tax}")
    
    logger.info(f"COMPUTE_REGULAR_TAX - Total regular tax calculated: {tax}")
    logger.debug(f"COMPUTE_REGULAR_TAX - Full breakdown by slabs: {json.dumps(slab_breakdown, indent=2)}")
    
    return tax

def compute_capital_gains_tax(cap_gains: CapitalGains, regime: str = 'old') -> float:
    logger.info(f"COMPUTE_CAPITAL_GAINS_TAX - Starting capital gains tax computation with regime: {regime}")
    logger.debug(f"COMPUTE_CAPITAL_GAINS_TAX - Capital gains input: STCG 111A: {cap_gains.stcg_111a}, "
                f"STCG Other: {cap_gains.stcg_any_other_asset}, STCG Debt MF: {cap_gains.stcg_debt_mutual_fund}, "
                f"LTCG 112A: {cap_gains.ltcg_112a}, LTCG Other: {cap_gains.ltcg_any_other_asset}, "
                f"LTCG Debt MF: {cap_gains.ltcg_debt_mutual_fund}")
    
    # Short-term capital gains on equity (Section 111A) - 15% flat rate
    stcg_111a_tax = cap_gains.stcg_111a * 0.15
    logger.debug(f"COMPUTE_CAPITAL_GAINS_TAX - STCG 111A Tax (15% flat rate): {stcg_111a_tax}")
    
    # Long-term capital gains on equity (Section 112A) - 10% flat rate above Rs. 1 lakh
    ltcg_112a_exemption = min(100000, cap_gains.ltcg_112a)
    ltcg_112a_taxable = max(0, cap_gains.ltcg_112a - ltcg_112a_exemption)
    ltcg_112a_tax = ltcg_112a_taxable * 0.10
    logger.debug(f"COMPUTE_CAPITAL_GAINS_TAX - LTCG 112A: Total: {cap_gains.ltcg_112a}, Exemption: {ltcg_112a_exemption}, "
                f"Taxable: {ltcg_112a_taxable}, Tax (10%): {ltcg_112a_tax}")
    
    # Other LTCG taxed at 20%
    ltcg_other = cap_gains.ltcg_any_other_asset + cap_gains.ltcg_debt_mutual_fund
    ltcg_other_tax = ltcg_other * 0.20
    logger.debug(f"COMPUTE_CAPITAL_GAINS_TAX - Other LTCG: Total: {ltcg_other}, Tax (20%): {ltcg_other_tax}")
    
    # Other STCG taxed at slab rates - this will be calculated separately with compute_regular_tax
    logger.debug(f"COMPUTE_CAPITAL_GAINS_TAX - STCG to be taxed at slab rates: {cap_gains.stcg_any_other_asset + cap_gains.stcg_debt_mutual_fund}")
    
    total_cg_tax = stcg_111a_tax + ltcg_112a_tax + ltcg_other_tax
    logger.info(f"COMPUTE_CAPITAL_GAINS_TAX - Total capital gains tax (excluding slab rate items): {total_cg_tax}")
    
    return total_cg_tax

def apply_87a_rebate(tax: float, income: float, regime: str) -> float:
    logger.info(f"APPLY_87A_REBATE - Applying section 87A rebate with tax: {tax}, income: {income}, regime: {regime}")
    
    original_tax = tax
    if regime == 'old' and income <= 500000:
        rebate_amount = min(12500, tax)
        tax = max(0, tax - rebate_amount)
        logger.debug(f"APPLY_87A_REBATE - Old Regime: Income <= 500000, Rebate: {rebate_amount}")
    elif regime == 'new' and income <= 700000:
        rebate_amount = min(25000, tax)
        tax = max(0, tax - rebate_amount)
        logger.debug(f"APPLY_87A_REBATE - New Regime: Income <= 700000, Rebate: {rebate_amount}")
    else:
        logger.debug(f"APPLY_87A_REBATE - No rebate applicable: Income or regime not eligible")
        rebate_amount = 0
    
    logger.info(f"APPLY_87A_REBATE - Tax before rebate: {original_tax}, Rebate applied: {rebate_amount}, Tax after rebate: {tax}")
    return tax

def compute_surcharge(base_tax: float, net_income: float, cap_gain_tax: float, dividend_tax: float) -> float:
    logger.info(f"COMPUTE_SURCHARGE - Computing surcharge with base tax: {base_tax}, net income: {net_income}, "
               f"capital gain tax: {cap_gain_tax}, dividend tax: {dividend_tax}")
    
    surcharge_rate = 0
    threshold = 0
    
    if net_income > 50000000:
        surcharge_rate = 0.37
        threshold = 50000000
        logger.debug(f"COMPUTE_SURCHARGE - Income > 5cr, rate: 37%")
    elif net_income > 20000000:
        surcharge_rate = 0.25
        threshold = 20000000
        logger.debug(f"COMPUTE_SURCHARGE - Income > 2cr, rate: 25%")
    elif net_income > 10000000:
        surcharge_rate = 0.15
        threshold = 10000000
        logger.debug(f"COMPUTE_SURCHARGE - Income > 1cr, rate: 15%")
    elif net_income > 5000000:
        surcharge_rate = 0.10
        threshold = 5000000
        logger.debug(f"COMPUTE_SURCHARGE - Income > 50L, rate: 10%")
    else:
        logger.debug(f"COMPUTE_SURCHARGE - Income <= 50L, no surcharge applicable")

    # Regular surcharge calculation
    tax_on_regular_income = base_tax - cap_gain_tax - dividend_tax
    reg_surcharge = tax_on_regular_income * surcharge_rate
    logger.debug(f"COMPUTE_SURCHARGE - Regular income tax: {tax_on_regular_income}, Surcharge on regular income: {reg_surcharge}")

    # Capped surcharge for capital gains and dividend (max 15%)
    capped_rate = min(surcharge_rate, 0.15)
    special_income_tax = cap_gain_tax + dividend_tax
    capped_surcharge = special_income_tax * capped_rate
    logger.debug(f"COMPUTE_SURCHARGE - Special income tax: {special_income_tax}, Capped rate: {capped_rate}, Capped surcharge: {capped_surcharge}")

    total_surcharge = reg_surcharge + capped_surcharge
    logger.info(f"COMPUTE_SURCHARGE - Total surcharge: {total_surcharge} (Regular: {reg_surcharge} + Capped: {capped_surcharge})")
    
    return total_surcharge

def apply_marginal_relief(tax: float, net_income: float, threshold: float) -> float:
    logger.info(f"APPLY_MARGINAL_RELIEF - Applying marginal relief with tax: {tax}, net income: {net_income}, threshold: {threshold}")
    
    excess_income = net_income - threshold
    logger.debug(f"APPLY_MARGINAL_RELIEF - Excess income above threshold: {excess_income}")
    
    # Calculate tax with marginal relief
    relief_amount = max(0, tax - (threshold + excess_income))
    logger.debug(f"APPLY_MARGINAL_RELIEF - Relief amount calculated: {relief_amount}")
    
    tax_after_relief = min(tax, tax - relief_amount)
    logger.info(f"APPLY_MARGINAL_RELIEF - Tax before relief: {tax}, Relief applied: {relief_amount}, Tax after relief: {tax_after_relief}")
    
    return tax_after_relief

def calculate_total_tax(emp_id: str, hostname: str) -> float:
    logger.info(f"CALCULATE_TOTAL_TAX - Starting tax calculation for employee ID: {emp_id}, hostname: {hostname}")
    
    # Get the taxation data for the employee from the database
    try:
        logger.debug(f"CALCULATE_TOTAL_TAX - Fetching taxation data from database")
        taxation_data = get_taxation_by_emp_id(emp_id, hostname)
        # Convert to Taxation object
        taxation = Taxation.from_dict(taxation_data)
        logger.debug(f"CALCULATE_TOTAL_TAX - Successfully retrieved taxation data: ID={taxation.emp_id}, Age={taxation.emp_age}, Regime={taxation.regime}")
    except Exception as e:
        # If taxation data doesn't exist or can't be retrieved, return 0
        logger.error(f"CALCULATE_TOTAL_TAX - Error retrieving taxation data: {str(e)}")
        return 0
    
    # Check if salary and perquisites exist to prevent attribute errors
    try:
        # Get components for calculation
        salary = taxation.salary
        other_sources = taxation.other_sources
        cap_gains = taxation.capital_gains
        deductions = taxation.deductions
        regime = taxation.regime
        age = taxation.emp_age
        is_govt_employee = getattr(taxation, 'is_govt_employee', False)
        
        logger.debug(f"CALCULATE_TOTAL_TAX - Tax calculation parameters - Regime: {regime}, Age: {age}, Govt Employee: {is_govt_employee}")
        
        # Calculate the total taxable income
        logger.debug(f"CALCULATE_TOTAL_TAX - Calculating salary income with components - Basic: {salary.basic}, DA: {salary.dearness_allowance}, "
                    f"HRA: {salary.hra}, Special: {salary.special_allowance}, Bonus: {salary.bonus}")
        
        salary_income = salary.total(regime)
        gross_income = salary_income
        logger.info(f"CALCULATE_TOTAL_TAX - Total salary income: {salary_income}")
        
        # Calculate other income sources
        logger.debug(f"CALCULATE_TOTAL_TAX - Calculating other sources income - Savings Interest: {other_sources.interest_savings}, "
                    f"FD Interest: {other_sources.interest_fd}, RD Interest: {other_sources.interest_rd}, Dividend: {other_sources.dividend_income}, "
                    f"Gifts: {other_sources.gifts}, Other Interest: {other_sources.other_interest}, Other Income: {other_sources.other_income}")
        
        other_income = other_sources.total_taxable_income_per_slab(regime, age)
        gross_income += other_income
        logger.info(f"CALCULATE_TOTAL_TAX - Other sources taxable income: {other_income}")
        
        # Calculate short-term capital gains taxed at special rates
        stcg_special_rate = cap_gains.total_stcg_special_rate()
        logger.debug(f"CALCULATE_TOTAL_TAX - STCG at special rates: {stcg_special_rate}")
        
        # Calculate short-term capital gains taxed at slab rates
        stcg_slab_rate = cap_gains.total_stcg_slab_rate()
        gross_income += stcg_slab_rate
        logger.debug(f"CALCULATE_TOTAL_TAX - STCG at slab rates: {stcg_slab_rate}")
        
        # Calculate long-term capital gains taxed at special rates
        ltcg_special_rate = cap_gains.total_ltcg_special_rate()
        logger.debug(f"CALCULATE_TOTAL_TAX - LTCG at special rates: {ltcg_special_rate}")
        
        logger.info(f"CALCULATE_TOTAL_TAX - Gross income before deductions: {gross_income}")
        
        # Calculate the total deductions
        total_deductions = 0
        if regime == 'old':
            # For old regime, calculate all deductions
            logger.debug(f"CALCULATE_TOTAL_TAX - Calculating deductions for old regime")
            
            # Handle EV purchase date if available
            ev_purchase_date = None
            if hasattr(deductions, 'ev_purchase_date') and deductions.ev_purchase_date:
                try:
                    ev_purchase_date = datetime.datetime.strptime(deductions.ev_purchase_date, '%Y-%m-%d').date()
                    logger.debug(f"CALCULATE_TOTAL_TAX - EV purchase date: {ev_purchase_date}")
                except Exception as e:
                    logger.warning(f"CALCULATE_TOTAL_TAX - Error parsing EV purchase date: {str(e)}")
                    ev_purchase_date = None
            
            # Log Section 80C deductions details
            section_80c_total = sum([
                deductions.section_80c_lic, deductions.section_80c_epf,
                deductions.section_80c_ssp, deductions.section_80c_nsc,
                deductions.section_80c_ulip, deductions.section_80c_tsmf,
                deductions.section_80c_tffte2c, deductions.section_80c_paphl,
                deductions.section_80c_sdpphp, deductions.section_80c_tsfdsb,
                deductions.section_80c_scss, deductions.section_80c_others
            ])
            logger.debug(f"CALCULATE_TOTAL_TAX - Section 80C components - LIC: {deductions.section_80c_lic}, EPF: {deductions.section_80c_epf}, "
                        f"SSP: {deductions.section_80c_ssp}, NSC: {deductions.section_80c_nsc}, ULIP: {deductions.section_80c_ulip}, "
                        f"TSMF: {deductions.section_80c_tsmf}, Tuition: {deductions.section_80c_tffte2c}, Loan Principal: {deductions.section_80c_paphl}, "
                        f"Stamp Duty: {deductions.section_80c_sdpphp}, FD: {deductions.section_80c_tsfdsb}, SCSS: {deductions.section_80c_scss}, "
                        f"Others: {deductions.section_80c_others}, Total: {section_80c_total}")
            
            # Log Section 80D deductions details
            section_80d_total = deductions.section_80d_hisf + deductions.section_80d_phcs + deductions.section_80d_hi_parent
            logger.debug(f"CALCULATE_TOTAL_TAX - Section 80D components - Self/Family: {deductions.section_80d_hisf}, "
                        f"Preventive: {deductions.section_80d_phcs}, Parents: {deductions.section_80d_hi_parent}, Total: {section_80d_total}")
            
            # Calculate all deductions
            total_deductions = deductions.total_deduction(
                regime=regime,
                is_govt_employee=is_govt_employee,
                gross_income=gross_income,
                age=age,
                ev_purchase_date=ev_purchase_date or datetime.datetime.now().date()
            )
            logger.info(f"CALCULATE_TOTAL_TAX - Total deductions: {total_deductions}")
        else:
            logger.info(f"CALCULATE_TOTAL_TAX - New regime selected - no deductions applicable")
        
        net_income = max(0, gross_income - total_deductions)
        logger.info(f"CALCULATE_TOTAL_TAX - Net taxable income: {net_income}")
        
        # Calculate tax on regular income (excluding capital gains and dividend)
        regular_income = net_income - stcg_slab_rate
        logger.debug(f"CALCULATE_TOTAL_TAX - Regular income (excluding STCG at slab rates): {regular_income}")
        
        tax_on_regular = compute_regular_tax(regular_income, regime)
        logger.info(f"CALCULATE_TOTAL_TAX - Tax on regular income: {tax_on_regular}")
        
        # Calculate tax on STCG at special rates (15% for section 111A)
        tax_on_stcg_special = stcg_special_rate * 0.15
        logger.info(f"CALCULATE_TOTAL_TAX - Tax on STCG at special rate (15%): {tax_on_stcg_special}")
        
        # Calculate tax on STCG at slab rates
        tax_on_stcg_slab = compute_regular_tax(stcg_slab_rate, regime)
        logger.info(f"CALCULATE_TOTAL_TAX - Tax on STCG at slab rates: {tax_on_stcg_slab}")
        
        # Calculate tax on LTCG at special rates
        tax_on_ltcg_112a = 0
        if ltcg_special_rate > 100000:  # Exemption of first 1 lakh for LTCG under section 112A
            tax_on_ltcg_112a = (ltcg_special_rate - 100000) * 0.10
            logger.info(f"CALCULATE_TOTAL_TAX - Tax on LTCG at special rate (10% above 1L): {tax_on_ltcg_112a}")
        else:
            logger.info(f"CALCULATE_TOTAL_TAX - LTCG below 1L exemption limit, no tax")
        
        # Total base tax
        base_tax = tax_on_regular + tax_on_stcg_special + tax_on_stcg_slab + tax_on_ltcg_112a
        logger.info(f"CALCULATE_TOTAL_TAX - Base tax (before rebate/surcharge/cess): {base_tax}")
        
        # Apply rebate under section 87A
        tax_after_rebate = apply_87a_rebate(base_tax, net_income, regime)
        logger.info(f"CALCULATE_TOTAL_TAX - Tax after Section 87A rebate: {tax_after_rebate}")
        
        # Calculate surcharge
        surcharge = compute_surcharge(tax_after_rebate, net_income, 
                                    tax_on_stcg_special + tax_on_ltcg_112a, 
                                    0)  # Assuming no dividend tax for simplicity
        logger.info(f"CALCULATE_TOTAL_TAX - Surcharge on tax: {surcharge}")
        
        # Apply marginal relief if applicable
        total_tax = tax_after_rebate + surcharge
        if net_income > 5000000:
            logger.debug(f"CALCULATE_TOTAL_TAX - Income > 50L, applying marginal relief")
            total_tax = apply_marginal_relief(total_tax, net_income, 5000000)
            logger.info(f"CALCULATE_TOTAL_TAX - Tax after marginal relief: {total_tax}")
        else:
            logger.debug(f"CALCULATE_TOTAL_TAX - Income <= 50L, no marginal relief applicable")
        
        # Add Health and Education Cess (4%)
        cess = total_tax * 0.04
        logger.info(f"CALCULATE_TOTAL_TAX - Health and Education Cess (4%): {cess}")
        
        final_tax = total_tax + cess
        logger.info(f"CALCULATE_TOTAL_TAX - Final tax amount: {final_tax}")
        
        # Prepare tax breakup
        tax_breakup = {
            "base_tax": round(base_tax),
            "tax_after_rebate": round(tax_after_rebate),
            "surcharge": round(surcharge),
            "cess": round(cess),
            "total_tax": round(final_tax),
            "details": {
                "regular_income": round(regular_income),
                "stcg_flat_rate": round(tax_on_stcg_special),
                "stcg_slab_rate": round(tax_on_stcg_slab),
                "ltcg_112a": round(tax_on_ltcg_112a),
                "gross_income": round(gross_income),
                "total_deductions": round(total_deductions),
                "net_income": round(net_income)
            }
        }
        logger.debug(f"CALCULATE_TOTAL_TAX - Tax breakdown: {json.dumps(tax_breakup, indent=2)}")
        
        # Update tax breakup in taxation object
        taxation.tax_breakup = tax_breakup
        taxation.total_tax = round(final_tax)
        taxation.tax_payable = round(final_tax)
        taxation.tax_due = max(0, taxation.tax_payable - (taxation.tax_paid or 0))
        taxation.tax_refundable = max(0, (taxation.tax_paid or 0) - taxation.tax_payable)
        taxation.tax_pending = taxation.tax_due
        
        logger.debug(f"CALCULATE_TOTAL_TAX - Updated taxation object: Tax payable: {taxation.tax_payable}, "
                    f"Tax paid: {taxation.tax_paid}, Tax due: {taxation.tax_due}, "
                    f"Tax refundable: {taxation.tax_refundable}, Tax pending: {taxation.tax_pending}")
        
        # Save updated taxation details
        try:
            logger.debug(f"CALCULATE_TOTAL_TAX - Saving updated taxation details to database")
            save_taxation(taxation, hostname)
            logger.info(f"CALCULATE_TOTAL_TAX - Successfully saved taxation details")
        except Exception as e:
            logger.error(f"CALCULATE_TOTAL_TAX - Error saving taxation details: {str(e)}")
        
        # Return rounded value
        logger.info(f"CALCULATE_TOTAL_TAX - Completed tax calculation for {emp_id}, Final Tax: {round(final_tax)}")
        return round(final_tax)
    except AttributeError as e:
        logger.error(f"CALCULATE_TOTAL_TAX - Error in tax calculation, attribute error: {str(e)}")
        # Return 0 or existing tax value if available
        return getattr(taxation, 'total_tax', 0)
    except Exception as e:
        logger.error(f"CALCULATE_TOTAL_TAX - Unexpected error in tax calculation: {str(e)}")
        return getattr(taxation, 'total_tax', 0)

def calculate_and_save_tax(emp_id: str, hostname: str, tax_year: str = None, regime: str = None,
                         salary: SalaryComponents = None, other_sources: IncomeFromOtherSources = None,
                         capital_gains: CapitalGains = None, deductions: DeductionComponents = None) -> Taxation:
    """
    Calculate the tax and save to the database
    """
    logger.info(f"CALCULATE_AND_SAVE_TAX - Starting tax calculation and saving for employee ID: {emp_id}")
    logger.debug(f"CALCULATE_AND_SAVE_TAX - Parameters - tax_year: {tax_year}, regime: {regime}, "
                f"salary provided: {salary is not None}, other_sources provided: {other_sources is not None}, "
                f"capital_gains provided: {capital_gains is not None}, deductions provided: {deductions is not None}")
    
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
        
        logger.debug(f"CALCULATE_AND_SAVE_TAX - Auto-determined tax year: {tax_year}")
    
    # Try to fetch existing taxation data
    try:
        logger.debug(f"CALCULATE_AND_SAVE_TAX - Trying to fetch existing taxation data for employee: {emp_id}")
        taxation_data = get_taxation_by_emp_id(emp_id, hostname)
        # Convert to Taxation object
        taxation = Taxation.from_dict(taxation_data)
        logger.info(f"CALCULATE_AND_SAVE_TAX - Found existing taxation data for employee: {emp_id}, tax year: {taxation.tax_year}, regime: {taxation.regime}")
        
        # Update with provided values
        if regime:
            logger.debug(f"CALCULATE_AND_SAVE_TAX - Updating regime from {taxation.regime} to {regime}")
            taxation.regime = regime
        if tax_year:
            logger.debug(f"CALCULATE_AND_SAVE_TAX - Updating tax year from {taxation.tax_year} to {tax_year}")
            taxation.tax_year = tax_year
        if salary:
            logger.debug(f"CALCULATE_AND_SAVE_TAX - Updating salary information")
            taxation.salary = salary
        if other_sources:
            logger.debug(f"CALCULATE_AND_SAVE_TAX - Updating other sources information")
            taxation.other_sources = other_sources
        if capital_gains:
            logger.debug(f"CALCULATE_AND_SAVE_TAX - Updating capital gains information")
            taxation.capital_gains = capital_gains
        if deductions:
            logger.debug(f"CALCULATE_AND_SAVE_TAX - Updating deductions information")
            taxation.deductions = deductions
    except Exception as e:
        logger.info(f"CALCULATE_AND_SAVE_TAX - No existing taxation data found for {emp_id}, creating new taxation object. Error: {str(e)}")
        
        # Get user age
        emp_age = 0
        try:
            logger.debug(f"CALCULATE_AND_SAVE_TAX - Fetching user data to determine age")
            user_data = get_user_by_emp_id(emp_id, hostname)
            if user_data and 'dob' in user_data and user_data['dob']:
                dob = datetime.datetime.strptime(user_data.get('dob', ''), '%Y-%m-%d')
                today = datetime.datetime.now()
                age_delta = relativedelta(today, dob)
                emp_age = age_delta.years
                logger.debug(f"CALCULATE_AND_SAVE_TAX - Calculated age for user: {emp_age} years")
            else:
                logger.warning(f"CALCULATE_AND_SAVE_TAX - No DOB found for user, defaulting age to 0")
        except Exception as e:
            logger.error(f"CALCULATE_AND_SAVE_TAX - Could not calculate age for {emp_id}: {str(e)}")
            
        # Create new taxation object if not found
        logger.info(f"CALCULATE_AND_SAVE_TAX - Creating new taxation object with emp_id: {emp_id}, age: {emp_age}, regime: {regime or 'old'}, tax_year: {tax_year}")
        taxation = Taxation(
            emp_id=emp_id,
            emp_age=emp_age,
            regime=regime or 'old',
            salary=salary or SalaryComponents(),
            other_sources=other_sources or IncomeFromOtherSources(),
            capital_gains=capital_gains or CapitalGains(),
            deductions=deductions or DeductionComponents(),
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
        
    # Calculate the total tax
    logger.info(f"CALCULATE_AND_SAVE_TAX - Calculating tax with calculated/provided data")
    
    # Save the taxation data
    try:
        logger.debug(f"CALCULATE_AND_SAVE_TAX - Saving taxation data to database")
        save_taxation(taxation, hostname)
        logger.debug(f"CALCULATE_AND_SAVE_TAX - Successfully saved taxation data")
    except Exception as e:
        logger.error(f"CALCULATE_AND_SAVE_TAX - Error saving taxation data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving taxation data: {str(e)}")
    
    # Calculate the tax
    try:
        logger.info(f"CALCULATE_AND_SAVE_TAX - Calculating total tax")
        total_tax = calculate_total_tax(emp_id, hostname)
        logger.info(f"CALCULATE_AND_SAVE_TAX - Tax calculation completed successfully, total tax: {total_tax}")
    except Exception as e:
        logger.error(f"CALCULATE_AND_SAVE_TAX - Error calculating tax: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error calculating tax: {str(e)}")
    
    # Retrieve the updated taxation data
    try:
        logger.debug(f"CALCULATE_AND_SAVE_TAX - Retrieving updated taxation data with calculated tax")
        updated_taxation_data = get_taxation_by_emp_id(emp_id, hostname)
        updated_taxation = Taxation.from_dict(updated_taxation_data)
        logger.info(f"CALCULATE_AND_SAVE_TAX - Successfully retrieved updated taxation data with tax: {updated_taxation.total_tax}")
        return updated_taxation
    except Exception as e:
        logger.error(f"CALCULATE_AND_SAVE_TAX - Error retrieving updated taxation data: {str(e)}")
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
        logger.info(f"Retrieved existing taxation data for {emp_id}")
        return taxation_data
    except HTTPException as e:
        if e.status_code == 404:
            logger.info(f"Taxation data not found for {emp_id}, creating defaults")
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
            special_allowance=0,
            bonus=0,
            perquisites=default_perquisites
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
            other_income=0
        )
        
        default_capital_gains = CapitalGains(
            stcg_111a=0,
            stcg_any_other_asset=0,
            stcg_debt_mutual_fund=0,
            ltcg_112a=0,
            ltcg_any_other_asset=0,
            ltcg_debt_mutual_fund=0
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
            capital_gains=default_capital_gains,
            deductions=default_deductions,
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
        saved_taxation = save_taxation(default_taxation, hostname)
        logger.info(f"Created default taxation data for {emp_id}")
        
        return saved_taxation
    except Exception as e:
        logger.error(f"Error creating default taxation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating default taxation: {str(e)}")
