# Indian Taxation Components and Computations Guide

## Overview
This document provides a comprehensive overview of all taxation components and their computations as per the Indian Income Tax Act, based on the implementation in the taxation models system. This guide is designed to help AI systems understand and recreate these computations accurately.

## Tax Regimes
The system supports two tax regimes:
1. **Old Regime**: Allows various deductions and exemptions
2. **New Regime**: Higher exemption limits but fewer deductions allowed

---

## 1. SALARY COMPONENTS

### 1.1 Core Salary Components
- **Basic Pay**: Fundamental salary component (Taxable)
- **Dearness Allowance (DA)**: Cost of living adjustment (Taxable)
- **House Rent Allowance (HRA)**: Housing expense allowance (Partially exempt)
- **Special Allowance**: Additional allowance (Taxable)
- **Bonus**: Performance-based payment (Taxable)
- **Commission**: Sales/performance commission (Taxable)

### 1.2 Other Allowances (Fully Taxable)
- **City Compensatory Allowance**: Urban area compensation
- **Rural Allowance**: Rural posting compensation
- **Proctorship Allowance**: Academic supervision allowance
- **Wardenship Allowance**: Hostel management allowance
- **Project Allowance**: Project-specific allowance
- **Deputation Allowance**: Temporary assignment allowance
- **Overtime Allowance**: Extra hours compensation
- **Interim Relief**: Temporary financial relief
- **Tiffin Allowance**: Meal allowance
- **Fixed Medical Allowance**: Medical expense allowance
- **Servant Allowance**: Domestic help allowance
- **Any Other Allowance**: Miscellaneous allowances

### 1.3 Exempted Allowances (Section 10)
- **Government Employees Outside India Allowance**: Fully exempt
- **Supreme/High Court Judges Allowance**: Fully exempt
- **Judge Compensatory Allowance**: Fully exempt
- **Section 10(14) Special Allowances**: Fully exempt
- **Travel on Tour Allowance**: Fully exempt
- **Tour Daily Charge Allowance**: Fully exempt
- **Conveyance in Performance of Duties**: Fully exempt
- **Helper in Performance of Duties**: Fully exempt
- **Academic Research Allowance**: Fully exempt
- **Uniform Allowance**: Fully exempt

### 1.4 Special Allowances with Limits
1. **Hills/High Altitude Allowance**
   - Range: Rs. 300 - Rs. 7,000 per month
   - Exemption: Up to specified limit per employee
   - Calculation: `min(allowance_received, exemption_limit)`

2. **Border/Remote Area Allowance**
   - Range: Rs. 200 - Rs. 3,000 per month
   - Exemption: Up to specified limit per employee
   - Calculation: `min(allowance_received, exemption_limit)`

3. **Transport Employee Allowance**
   - Exemption: Lesser of Rs. 10,000 or 70% of allowance
   - Calculation: `min(allowance, min(10000, 0.7 * allowance))`

4. **Children Education Allowance**
   - Exemption: Rs. 100 per month per child (max 2 children)
   - Calculation: `min(allowance, children_count * 100 * months)`

5. **Hostel Allowance**
   - Exemption: Rs. 300 per month per child (max 2 children)
   - Calculation: `min(allowance, children_count * 300 * months)`

6. **Transport Allowance (Disabled)**
   - Exemption: Rs. 3,200 per month (for disabled individuals)
   - Calculation: `min(allowance, months * 3200)`

7. **Underground Mines Allowance**
   - Exemption: Rs. 800 per month
   - Calculation: `min(allowance, months * 800)`

8. **Government Employee Entertainment Allowance**
   - Exemption: Minimum of (Allowance, 20% of Basic, Rs. 5,000)
   - Calculation: `min(allowance, basic * 0.2, 5000)`
   - Only applicable to government employees

### 1.5 HRA Exemption Calculation
HRA exemption is the minimum of:
1. Actual HRA received
2. 50% of salary (metro cities) or 40% (non-metro)
3. Rent paid minus 10% of salary

**Formula**: 
```
basic_plus_da = basic + dearness_allowance
if city in ['Delhi', 'Mumbai', 'Kolkata', 'Chennai']:
    percent_of_salary = 0.5 * basic_plus_da
else:
    percent_of_salary = 0.4 * basic_plus_da

rent_minus_salary = max(0, actual_rent_paid - (0.1 * basic_plus_da))
hra_exemption = min(hra_received, percent_of_salary, rent_minus_salary)
```

---

## 2. PERQUISITES

### 2.1 Accommodation Perquisites
**Types**: Employer-Owned, Government, Employer-Leased, Hotel (15+ days)

**Calculations**:
- **Government**: `max(0, license_fees - employee_rent_payment) + furniture_value`
- **Employer-Owned**: 
  - Cities >40 lakhs: `(basic + da) * 0.10 + furniture_value`
  - Cities 15-40 lakhs: `(basic + da) * 0.075 + furniture_value`
  - Cities <15 lakhs: `(basic + da) * 0.05 + furniture_value`
- **Employer-Leased**: `min(rent_paid_by_employer, (basic + da) * 0.10) + furniture_value`
- **Hotel**: `min(hotel_charges, (basic + da) * 0.24)`

**Furniture Value**: 
- If employer-owned: `(furniture_cost * 0.1) - employee_payment`
- If hired/leased: `furniture_cost - employee_payment`

### 2.2 Car Perquisites
**Car Use Types**: Personal, Business, Mixed

**Engine Capacity Impact**:
- Higher capacity (>1.6L): Higher perquisite rates
- Lower capacity (≤1.6L): Lower perquisite rates

**Calculations**:
- **Personal Use**: `(car_cost_to_employer * months) + (other_vehicle_cost * months)`
- **Business Use**: `0` (not taxable)
- **Mixed Use**:
  - With expense reimbursement: 
    - >1.6L: `Rs. 2,400 per month`
    - ≤1.6L: `Rs. 1,800 per month`
  - Without expense reimbursement:
    - >1.6L: `Rs. 900 per month`
    - ≤1.6L: `Rs. 600 per month`
  - Driver provided: Additional `Rs. 900 per month`

### 2.3 Medical Reimbursement
**Treatment in India**: 
- Exemption: Rs. 15,000
- Taxable: `max(0, reimbursement - 15000)`

**Overseas Treatment**: 
- Travel allowance taxable if gross salary > Rs. 2,00,000
- Medical expenses beyond RBI limit taxable
- Calculation: `travel_value + max(0, medical_expenses - rbi_limit)`

### 2.4 Leave Travel Allowance (LTA)
**Exemption Rules**:
- Limited to 2 journeys in 4-year block
- Exemption limited to economy class airfare/AC first class railway fare

**Calculation**:
```
if lta_claimed_count > 2:
    return lta_amount_claimed  # Fully taxable
else:
    eligible_exemption = public_transport_cost_for_same_distance
    return max(0, lta_amount_claimed - eligible_exemption)
```

### 2.5 Interest-Free/Concessional Loans
**Exemptions**:
- Medical loans: Fully exempt
- Loans ≤ Rs. 20,000: Fully exempt

**Taxable Benefit Calculation**: 
```
interest_rate_diff = sbi_rate - company_rate
if interest_rate_diff <= 0:
    return 0

principal = outstanding_amount if outstanding_amount > 0 else loan_amount
annual_benefit = principal * (interest_rate_diff / 100)

if loan_months < 12:
    return annual_benefit * (loan_months / 12)
return annual_benefit
```

### 2.6 Employee Stock Options (ESOP)
**Allocation Gain Formula**: 
```
allocation_gain = max(0, (exercise_price - allotment_price) * shares_exercised)
```

### 2.7 Gas, Electricity, Water
**Calculation**: 
```
employer_total = gas_paid_by_employer + electricity_paid_by_employer + water_paid_by_employer
employee_total = gas_paid_by_employee + electricity_paid_by_employee + water_paid_by_employee
taxable_value = max(0, employer_total - employee_total)
```

### 2.8 Free Education
**Exemption**: Rs. 1,000 per month per child (max 2 children)
**Calculation**:
```
child1_taxable = max(0, monthly_expenses_child1 - 1000) * months_child1
child2_taxable = max(0, monthly_expenses_child2 - 1000) * months_child2
total_taxable = child1_taxable + child2_taxable
```

### 2.9 Movable Assets Usage
**Calculation**:
- **Employer-Owned**: `max(0, (asset_value * 0.1) - employee_payment)`
- **Employer-Hired**: `max(0, hire_cost - employee_payment)`

### 2.10 Movable Assets Transfer
**Depreciation Rates**:
- Electronics: 50% per year
- Motor Vehicle: 20% per year
- Others: 10% per year

**Calculation**:
```
if asset_type == 'Electronics':
    depreciation_rate = 0.5
elif asset_type == 'Motor Vehicle':
    depreciation_rate = 0.2
else:
    depreciation_rate = 0.1

depreciated_value = (asset_cost * depreciation_rate) * years_of_use
taxable_value = max(0, (asset_cost - depreciated_value) - employee_payment)
```

### 2.11 Lunch/Refreshment
**Exemption**: Rs. 50 per meal
**Calculation**: 
```
annual_exemption = 50 * meal_days_per_year
taxable_value = max(0, employer_cost - employee_payment - annual_exemption)
```

### 2.12 Gift Vouchers
**Exemption**: Rs. 5,000 per annum
**Calculation**: 
```
if gift_voucher_amount <= 5000:
    return 0
else:
    return gift_voucher_amount - 5000
```

---

## 3. INCOME FROM OTHER SOURCES

### 3.1 Interest Income Types
1. **Savings Account Interest**
2. **Fixed Deposit Interest**
3. **Recurring Deposit Interest**
4. **Other Interest Income**

### 3.2 Section 80TTA/80TTB Exemptions
**Section 80TTA (Age < 60)**:
- Only savings account interest eligible
- Exemption: Up to Rs. 10,000
- Calculation: 
```
exempt_savings = min(10000, savings_interest)
taxable_interest = max(0, savings_interest - exempt_savings) + fd_interest + rd_interest
```

**Section 80TTB (Age ≥ 60)**:
- All bank interest (savings, FD, RD) eligible
- Exemption: Up to Rs. 50,000
- Calculation:
```
total_interest = savings_interest + fd_interest + rd_interest
exempt_interest = min(50000, total_interest)
taxable_interest = max(0, total_interest - exempt_interest)
```

### 3.3 Other Income Sources (Fully Taxable)
- **Dividend Income**
- **Gifts Received**
- **Business/Professional Income**
- **Other Income**

---

## 4. INCOME FROM HOUSE PROPERTY

### 4.1 Property Types and Annual Value
1. **Self-Occupied**: Annual value = 0
2. **Let-Out**: Annual value = Rent received
3. **Deemed Let-Out**: Based on fair rental value

### 4.2 Self-Occupied Property Calculation
```
annual_value = 0
interest_deduction = min(200000, home_loan_interest)
pre_construction_deduction = pre_construction_interest / 5
net_income = annual_value - interest_deduction - pre_construction_deduction
```

### 4.3 Let-Out Property Calculation
```
annual_value = rent_received
net_annual_value = annual_value - municipal_taxes
standard_deduction = net_annual_value * 0.30
interest_deduction = home_loan_interest  # No upper limit
pre_construction_deduction = pre_construction_interest / 5
net_income = net_annual_value - standard_deduction - interest_deduction - pre_construction_deduction
```

---

## 5. CAPITAL GAINS

### 5.1 Short-Term Capital Gains (STCG)
1. **STCG 111A (Equity with STT)**
   - Rate: 20% (Budget 2024)
   - Tax calculation: `stcg_111a * 0.20`

2. **STCG from Other Assets**
   - Rate: Slab rates
   - Included in regular income computation

### 5.2 Long-Term Capital Gains (LTCG)
1. **LTCG 112A (Equity with STT)**
   - Rate: 12.5% (Budget 2024)
   - Exemption: Rs. 1,25,000 (Budget 2024)
   - Calculation: `max(0, ltcg_112a - 125000) * 0.125`

2. **LTCG from Other Assets**
   - Rate: 12.5% (Budget 2024)
   - Calculation: `(ltcg_other_assets + ltcg_debt_mf) * 0.125`

---

## 6. RETIREMENT BENEFITS

### 6.1 Leave Encashment
**During Employment**: Fully taxable

**On Retirement/Termination (Non-Government)**:
Exemption is minimum of:
1. Actual amount received
2. 10 months' average salary
3. Rs. 25,00,000
4. Unexpired leave value

**Calculation**:
```
if is_govt_employee or is_deceased:
    return 0

if during_employment:
    return leave_encashment_amount

actual_received = leave_encashment_amount
ten_months_salary = average_monthly_salary * 10
statutory_limit = 2500000
unexpired_leave_value = leave_encashed * (average_monthly_salary / 30)

exemption = min(actual_received, ten_months_salary, statutory_limit, unexpired_leave_value)
taxable_amount = max(0, actual_received - exemption)
```

### 6.2 Voluntary Retirement Scheme (VRS)
**Eligibility**: Age ≥ 40 and Service ≥ 10 years
**Exemption**: Rs. 5,00,000

**VRS Value Calculation**: 
```
if age < 40 or service_years < 10:
    return 0

single_day_salary = monthly_salary / 30
salary_45_days = single_day_salary * 45
months_remaining = (60 - age) * 12
salary_for_remaining_months = monthly_salary * months_remaining
salary_for_service = salary_45_days * service_years
vrs_value = min(salary_for_remaining_months, salary_for_service)

taxable_amount = max(0, vrs_amount - 500000)
```

### 6.3 Gratuity
**Government Employees**: Fully exempt

**Non-Government Employees** - Exemption is minimum of:
1. Actual amount received
2. 15 days' salary for each year of service
3. Rs. 20,00,000

**Calculation**:
```
if is_govt_employee:
    return 0

actual_received = gratuity_amount
daily_salary = monthly_salary / 26
salary_based_exemption = (daily_salary * 15) * service_years
statutory_limit = 2000000

exemption = min(actual_received, salary_based_exemption, statutory_limit)
taxable_amount = max(0, actual_received - exemption)
```

### 6.4 Pension
**Regular Pension**: Fully taxable

**Commuted Pension**:
```
if is_govt_employee:
    return 0  # Fully exempt for government employees

exemption_fraction = 1/3 if gratuity_received else 1/2
exemption_limit = total_pension * exemption_fraction
taxable_pension = min(commuted_pension, exemption_limit)
```

### 6.5 Retrenchment Compensation
Exemption is minimum of:
1. Actual amount received
2. Rs. 5,00,000
3. 15 days' pay for each completed year of service

**Calculation**:
```
actual_received = retrenchment_amount
statutory_limit = 500000
daily_salary = monthly_salary / 30
completed_years = int(service_years)
remaining_days = (service_years - completed_years) * 365.25
if remaining_days > 182.625:  # More than 6 months
    completed_years += 1
salary_based_exemption = (daily_salary * 15) * completed_years

exemption = min(actual_received, salary_based_exemption, statutory_limit)
taxable_amount = max(0, actual_received - exemption)
```

---

## 7. DEDUCTIONS (OLD REGIME ONLY)

### 7.1 Section 80C, 80CCC, 80CCD(1) - Combined Limit Rs. 1,50,000

**Section 80C Components**:
- Life Insurance Premium
- Employee Provident Fund
- Sukanya Samridhi Account
- National Savings Certificate
- Unit Linked Insurance Plan
- Tax Saving Mutual Fund
- Tuition fees (max 2 children)
- Housing loan principal
- Stamp duty on property purchase
- Tax saving fixed deposits
- Senior Citizen Savings Scheme
- Others

**Calculation**:
```
section_80c_total = sum([
    lic_premium, epf, sukanya, nsc, ulip, tax_saving_mf,
    tuition_fees, housing_principal, stamp_duty, tax_saving_fd,
    scss, others, pension_premium_80ccc, nps_80ccd_1
])
capped_80c = min(section_80c_total, 150000)
```

### 7.2 Section 80CCD(1B) - Additional Rs. 50,000
```
additional_nps_deduction = min(nps_additional_contribution, 50000)
```

### 7.3 Section 80CCD(2) - Employer NPS Contribution
```
if is_govt_employee:
    max_cap = (basic + da) * 0.14  # 14% for government
else:
    max_cap = (basic + da) * 0.10  # 10% for private
    
deduction = min(employer_nps_contribution, max_cap)
```

### 7.4 Section 80D - Health Insurance

**Self and Family**:
```
if age >= 60:
    max_cap = 50000
else:
    max_cap = 25000

total = min((health_insurance + min(preventive_checkup, 5000)), max_cap)
```

**Parents**:
```
if parent_age >= 60:
    max_cap = 50000
else:
    max_cap = 25000

deduction = min(parent_health_insurance, max_cap)
```

### 7.5 Section 80DD - Disability (Dependent)
**Fixed Deductions** (not based on actual expenditure):
```
if relation in ['Spouse', 'Child', 'Parents', 'Sibling']:
    if disability_percentage == 'Between 40%-80%':
        return 75000
    elif disability_percentage in ['More than 80%', '80%+']:
        return 125000
return 0
```

### 7.6 Section 80DDB - Medical Treatment (Specified Diseases)
```
if relation in ['Self', 'Spouse', 'Child', 'Parents', 'Sibling']:
    relevant_age = age if relation == 'Self' else dependent_age
    if relevant_age < 60:
        return min(medical_expenses, 40000)
    else:
        return min(medical_expenses, 100000)
return 0
```

### 7.7 Section 80E - Education Loan Interest
```
if relation in ['Self', 'Spouse', 'Child']:
    return education_loan_interest  # No upper limit
return 0
```

### 7.8 Section 80EEB - Electric Vehicle Loan Interest
```
if ev_purchase_date >= date(2019, 4, 1) and ev_purchase_date <= date(2025, 3, 31):
    return min(ev_loan_interest, 150000)
return 0
```

### 7.9 Section 80G - Charitable Donations

**Four Categories**:

1. **100% deduction without qualifying limit**:
```
if donation_head in section_80g_100_wo_ql_heads:
    return donation_amount
```

2. **50% deduction without qualifying limit**:
```
if donation_head in section_80g_50_wo_ql_heads:
    return donation_amount * 0.5
```

3. **100% deduction with qualifying limit (10% of income)**:
```
if donation_head in section_80g_100_ql_heads:
    return min(donation_amount, gross_income * 0.1)
```

4. **50% deduction with qualifying limit (10% of income)**:
```
if donation_head in section_80g_50_ql_heads:
    return min(donation_amount * 0.5, gross_income * 0.1)
```

### 7.10 Section 80GGC - Political Party Contributions
```
# No upper limit, but no cash payments allowed
return political_party_contribution
```

### 7.11 Section 80U - Self Disability
**Fixed Deductions** (not based on actual expenditure):
```
if disability_percentage == 'Between 40%-80%':
    return 75000
elif disability_percentage in ['More than 80%', '80%+']:
    return 125000
return 0
```

---

## 8. TAX COMPUTATION FLOW

### Step 1: Calculate Gross Total Income
```
# 1. Salary Income
salary_income = total_salary_components - exemptions + perquisites_value

# 2. Income from Other Sources  
other_sources_income = total_other_income - section_80tta_80ttb_exemptions

# 3. Income from House Property
house_property_income = annual_value - deductions

# 4. Capital Gains
capital_gains_slab = stcg_other_assets + stcg_debt_mf
capital_gains_special = stcg_111a + ltcg_112a + ltcg_other_assets

# 5. Retirement Benefits
retirement_income = leave_encashment + gratuity + pension + vrs + retrenchment - exemptions

gross_total_income = salary_income + other_sources_income + house_property_income + capital_gains_slab + retirement_income
```

### Step 2: Calculate Total Income (Old Regime)
```
total_deductions = (
    section_80c_80ccc_80ccd_1 + section_80ccd_1b + section_80ccd_2 +
    section_80d_self + section_80d_parent + section_80dd + section_80ddb +
    section_80e + section_80eeb + section_80g + section_80ggc + section_80u
)

total_income = gross_total_income - total_deductions
```

### Step 3: Calculate Tax
```
# STCG and LTCG at special rates (taxed separately)
stcg_tax = stcg_111a * 0.20
ltcg_tax = max(0, ltcg_112a - 125000) * 0.125 + ltcg_other * 0.125

# Income at slab rates
slab_income = total_income  # After deductions
slab_tax = calculate_income_tax_slab(slab_income)

total_tax = slab_tax + stcg_tax + ltcg_tax
```

### Step 4: Add Cess and Surcharge
```
# Health and Education Cess: 4%
cess = total_tax * 0.04

# Surcharge based on income levels
if total_income > certain_threshold:
    surcharge = total_tax * surcharge_rate
else:
    surcharge = 0

final_tax = total_tax + cess + surcharge
```

---

## 9. DONATION CATEGORIES (Section 80G)

### 100% Deduction (No Qualifying Limit)
- National Defence Fund set up by Central Government
- Prime Minister national relief fund
- National Foundation for Communal Harmony
- An approved university/educational institution of National eminence
- Zila Saksharta Samiti constituted in any district
- Fund set up by a state government for medical relief to the poor
- National Illness Assistance Fund
- National Blood Transfusion Council or any State Blood Transfusion Council
- National Trust for Welfare of Persons with Autism, Cerebral Palsy, Mental Retardation, and Multiple Disabilities
- National Sports Fund, National Cultural Fund
- Fund for Technology Development and Application
- National Children Fund
- Chief Minister Relief Fund or Lieutenant Governor Relief Fund
- Army/Naval/Air Force Central Welfare Funds
- Swachh Bharat Kosh, Clean Ganga Fund
- National Fund for Control of Drug Abuse

### 50% Deduction (No Qualifying Limit)
- Jawaharlal Nehru Memorial Fund
- Prime Minister's Drought Relief Fund
- Indira Gandhi Memorial Trust
- Rajiv Gandhi Foundation

### 100% Deduction (With Qualifying Limit - 10% of Income)
- Donations to Government for promoting family planning
- Donation by company to Indian Olympic Association for sports development

### 50% Deduction (With Qualifying Limit - 10% of Income)
- Donations to other funds satisfying Section 80G(5) conditions
- Donations to Government for charitable purposes (other than family planning)
- Donations to housing authorities
- Donations for repair/renovation of religious places of historic importance

---

## 10. REGIME-SPECIFIC RULES

### Old Regime
- All deductions under Sections 80C to 80U allowed
- All salary exemptions applicable
- HRA exemption available
- Perquisites taxable as per detailed rules
- Section 80TTA/80TTB interest exemptions available

### New Regime  
- No deductions allowed (except specific ones like NPS employer contribution)
- Limited exemptions available
- Higher standard deduction
- Perquisites generally not taxable
- No interest income exemptions

---

## 11. KEY COMPUTATIONAL FORMULAS

### Age-Based Calculations
```python
def get_applicable_limit(age, below_60_limit, above_60_limit):
    return above_60_limit if age >= 60 else below_60_limit

# Health Insurance (80D)
health_limit = get_applicable_limit(age, 25000, 50000)

# Interest Exemption
if age >= 60:
    # Section 80TTB - All bank interest up to Rs. 50,000
    interest_exemption = min(50000, total_bank_interest)
else:
    # Section 80TTA - Only savings interest up to Rs. 10,000  
    interest_exemption = min(10000, savings_interest)
```

### Service-Based Calculations
```python
def calculate_service_years(date_of_joining, date_of_leaving):
    service_days = (date_of_leaving - date_of_joining).days
    return service_days / 365.25

def calculate_gratuity_exemption(gratuity_amount, monthly_salary, service_years):
    actual_received = gratuity_amount
    daily_salary = monthly_salary / 26
    salary_based_exemption = (daily_salary * 15) * service_years
    statutory_limit = 2000000
    return min(actual_received, salary_based_exemption, statutory_limit)
```

### Minimum/Maximum Logic
```python
def calculate_exemption(*amounts):
    return min(amounts)

def calculate_taxable_amount(total_received, exemption):
    return max(0, total_received - exemption)
```

---

This comprehensive guide provides all the necessary information for AI systems to understand and recreate the Indian taxation computations accurately. Each section includes specific formulas, limits, conditions, and calculation methods as implemented in the taxation models system.
