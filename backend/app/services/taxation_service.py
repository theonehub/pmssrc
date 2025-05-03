from models.taxation import SalaryComponents, IncomeFromOtherSources, CapitalGains, DeductionComponents, Taxation, Perquisites
from database.taxation_database import get_taxation_by_emp_id, save_taxation
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

def compute_capital_gains_tax(cap_gains: CapitalGains) -> float:
    stcg_tax = cap_gains.stcg_111a * 0.15
    ltcg_taxable = max(0, cap_gains.ltcg_112a - 100000)
    ltcg_tax = ltcg_taxable * 0.10
    return stcg_tax + ltcg_tax

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
        
        # Calculate the tax
        salary_income = salary.total()
        other_income = other_sources.total()
        capital_gains_income = cap_gains.total()
        gross_total_income = salary_income + other_income + capital_gains_income
        deduction_total = 0 if regime == 'new' else deductions.total()
        net_income = max(0, gross_total_income - deduction_total)

        regular_income = max(0, net_income - cap_gains.total() - other_sources.dividend_income)

        tax_on_regular = compute_regular_tax(regular_income, regime)
        tax_on_cg = compute_capital_gains_tax(cap_gains)
        tax_on_dividends = compute_regular_tax(other_sources.dividend_income, regime)

        base_tax = tax_on_regular + tax_on_cg + tax_on_dividends
        tax_after_rebate = apply_87a_rebate(base_tax, net_income, regime)

        surcharge = compute_surcharge(tax_after_rebate, net_income, tax_on_cg, tax_on_dividends)
        total_tax = tax_after_rebate + surcharge

        if net_income > 5000000:
            total_tax = apply_marginal_relief(total_tax, net_income, 5000000)
        
        cess = total_tax * 0.04  # 4% Health and Education Cess
        final_tax = total_tax + cess
        
        # Prepare tax breakup
        tax_breakup = {
            "base_tax": round(base_tax),
            "tax_after_rebate": round(tax_after_rebate),
            "surcharge": round(surcharge),
            "cess": round(cess),
            "total_tax": round(final_tax)
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
            tax_pending=0
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
