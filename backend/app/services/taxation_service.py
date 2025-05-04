from models.taxation import SalaryComponents, IncomeFromOtherSources, CapitalGains, DeductionComponents, Taxation, Perquisites
from database.taxation_database import get_taxation_by_emp_id, save_taxation
from services.organisation_service import is_govt_organisation
import datetime
import uuid

def compute_regular_tax(income: float, regime: str = 'old') -> float:
    if regime == 'new':
        slabs = [
            (0, 300000, 0.0),
            (300001, 600000, 0.05),
            (600001, 900000, 0.10),
            (900001, 1200000, 0.15),
            (1200001, 1500000, 0.20),
            (1500001, float('inf'), 0.30)
        ]
    else:
        slabs = [
            (0, 250000, 0.0),
            (250001, 500000, 0.05),
            (500001, 1000000, 0.20),
            (1000001, float('inf'), 0.30)
        ]

    tax = 0
    for lower, upper, rate in slabs:
        if income > lower:
            taxable = min(upper, income) - lower
            tax += taxable * rate
    return tax

def compute_capital_gains_tax(cap_gains: CapitalGains, regime: str = 'old') -> float:
    # Short-term capital gains on equity (Section 111A) - 15% flat rate
    stcg_111a_tax = cap_gains.stcg_111a * 0.15
    
    # Long-term capital gains on equity (Section 112A) - 10% flat rate above Rs. 1 lakh
    ltcg_112a_exemption = min(100000, cap_gains.ltcg_112a)
    ltcg_112a_taxable = max(0, cap_gains.ltcg_112a - ltcg_112a_exemption)
    ltcg_112a_tax = ltcg_112a_taxable * 0.10
    
    # Other LTCG taxed at 20%
    ltcg_other_tax = (cap_gains.ltcg_any_other_asset + cap_gains.ltcg_debt_mutual_fund) * 0.20
    
    # Other STCG taxed at slab rates - this will be calculated separately with compute_regular_tax
    
    return stcg_111a_tax + ltcg_112a_tax + ltcg_other_tax

def apply_87a_rebate(tax: float, income: float, regime: str) -> float:
    if regime == 'old' and income <= 500000:
        return max(0, tax - 12500)
    elif regime == 'new' and income <= 700000:
        return max(0, tax - 25000)
    return tax

def compute_surcharge(base_tax: float, net_income: float, cap_gain_tax: float, dividend_tax: float) -> float:
    surcharge_rate = 0
    threshold = 0
    if net_income > 50000000:
        surcharge_rate = 0.37
        threshold = 50000000
    elif net_income > 20000000:
        surcharge_rate = 0.25
        threshold = 20000000
    elif net_income > 10000000:
        surcharge_rate = 0.15
        threshold = 10000000
    elif net_income > 5000000:
        surcharge_rate = 0.10
        threshold = 5000000

    reg_surcharge = (base_tax - cap_gain_tax - dividend_tax) * surcharge_rate
    capped_surcharge = (cap_gain_tax + dividend_tax) * min(surcharge_rate, 0.15)
    return reg_surcharge + capped_surcharge

def apply_marginal_relief(tax: float, net_income: float, threshold: float) -> float:
    excess_income = net_income - threshold
    return min(tax, tax - (tax - (threshold + excess_income)))

def calculate_total_tax(emp_id: str, hostname: str) -> float:
    # Get the taxation data for the employee from the database
    try:
        taxation_data = get_taxation_by_emp_id(emp_id, hostname)
        # Convert to Taxation object
        taxation = Taxation.from_dict(taxation_data)
    except Exception as e:
        # If taxation data doesn't exist or can't be retrieved, return 0
        print(f"Error retrieving taxation data: {str(e)}")
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
        
        # Calculate the total taxable income
        salary_income = salary.total(regime)
        gross_income = salary_income
        
        # Calculate other income sources
        other_income = other_sources.total_taxable_income_per_slab(regime, age)
        gross_income += other_income
        
        # Calculate short-term capital gains taxed at special rates
        stcg_special_rate = cap_gains.total_stcg_special_rate()
        
        # Calculate short-term capital gains taxed at slab rates
        stcg_slab_rate = cap_gains.total_stcg_slab_rate()
        gross_income += stcg_slab_rate
        
        # Calculate long-term capital gains taxed at special rates
        ltcg_special_rate = cap_gains.total_ltcg_special_rate()
        
        # Calculate the total deductions
        total_deductions = 0
        if regime == 'old':
            # For old regime, calculate all deductions
            ev_purchase_date = None
            if hasattr(deductions, 'ev_purchase_date') and deductions.ev_purchase_date:
                try:
                    ev_purchase_date = datetime.datetime.strptime(deductions.ev_purchase_date, '%Y-%m-%d').date()
                except:
                    ev_purchase_date = None
            
            total_deductions = deductions.total_deduction(
                regime=regime,
                is_govt_employee=is_govt_employee,
                gross_income=gross_income,
                age=age,
                date_of_purchase=ev_purchase_date or datetime.datetime.now().date()
            )
        
        net_income = max(0, gross_income - total_deductions)
        
        # Calculate tax on regular income (excluding capital gains and dividend)
        regular_income = net_income - stcg_slab_rate
        tax_on_regular = compute_regular_tax(regular_income, regime)
        
        # Calculate tax on STCG at special rates (15% for section 111A)
        tax_on_stcg_special = stcg_special_rate * 0.15
        
        # Calculate tax on STCG at slab rates
        tax_on_stcg_slab = compute_regular_tax(stcg_slab_rate, regime)
        
        # Calculate tax on LTCG at special rates
        tax_on_ltcg_112a = 0
        if ltcg_special_rate > 100000:  # Exemption of first 1 lakh for LTCG under section 112A
            tax_on_ltcg_112a = (ltcg_special_rate - 100000) * 0.10
        
        # Total base tax
        base_tax = tax_on_regular + tax_on_stcg_special + tax_on_stcg_slab + tax_on_ltcg_112a
        
        # Apply rebate under section 87A
        tax_after_rebate = apply_87a_rebate(base_tax, net_income, regime)
        
        # Calculate surcharge
        surcharge = compute_surcharge(tax_after_rebate, net_income, 
                                    tax_on_stcg_special + tax_on_ltcg_112a, 
                                    0)  # Assuming no dividend tax for simplicity
        
        # Apply marginal relief if applicable
        total_tax = tax_after_rebate + surcharge
        if net_income > 5000000:
            total_tax = apply_marginal_relief(total_tax, net_income, 5000000)
        
        # Add Health and Education Cess (4%)
        cess = total_tax * 0.04
        final_tax = total_tax + cess
        
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
        
        # Update tax breakup in taxation object
        taxation.tax_breakup = tax_breakup
        taxation.total_tax = round(final_tax)
        taxation.tax_payable = round(final_tax)
        taxation.tax_due = max(0, taxation.tax_payable - (taxation.tax_paid or 0))
        taxation.tax_refundable = max(0, (taxation.tax_paid or 0) - taxation.tax_payable)
        taxation.tax_pending = taxation.tax_due
        
        # Save updated taxation details
        try:
            save_taxation(taxation, hostname)
        except Exception as e:
            print(f"Error saving taxation details: {str(e)}")
        
        # Return rounded value
        return round(final_tax)
    except AttributeError as e:
        print(f"Error in tax calculation, attribute error: {str(e)}")
        # Return 0 or existing tax value if available
        return getattr(taxation, 'total_tax', 0)
    except Exception as e:
        print(f"Unexpected error in tax calculation: {str(e)}")
        return getattr(taxation, 'total_tax', 0)

def calculate_and_save_tax(emp_id: str, hostname: str, tax_year: str = None, regime: str = None,
                         salary: SalaryComponents = None, other_sources: IncomeFromOtherSources = None,
                         capital_gains: CapitalGains = None, deductions: DeductionComponents = None) -> Taxation:
    """
    Calculate the tax and save to the database
    """
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
    
    # Try to fetch existing taxation data
    try:
        taxation_data = get_taxation_by_emp_id(emp_id, hostname)
        # Convert to Taxation object
        taxation = Taxation.from_dict(taxation_data)
        
        # Update with provided values
        if regime:
            taxation.regime = regime
        if tax_year:
            taxation.tax_year = tax_year
        if salary:
            taxation.salary = salary
        if other_sources:
            taxation.other_sources = other_sources
        if capital_gains:
            taxation.capital_gains = capital_gains
        if deductions:
            taxation.deductions = deductions
    except:
        # Create new taxation object if not found
        taxation = Taxation(
            emp_id=emp_id,
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
            is_govt_employee=is_govt_organisation(hostname)
        )
    
    # Save the taxation record first to ensure it exists
    save_taxation(taxation, hostname)
    
    # Calculate tax
    try:
        total_tax = calculate_total_tax(emp_id, hostname)
        
        # Update taxation object with new tax calculation
        try:
            updated_taxation_data = get_taxation_by_emp_id(emp_id, hostname)
            updated_taxation = Taxation.from_dict(updated_taxation_data)
            return updated_taxation
        except:
            # If for some reason we can't fetch the updated taxation, return the original
            taxation.total_tax = total_tax
            return taxation
    except Exception as e:
        # If tax calculation fails, still return the saved taxation data
        print(f"Error calculating tax: {str(e)}")
        return taxation
