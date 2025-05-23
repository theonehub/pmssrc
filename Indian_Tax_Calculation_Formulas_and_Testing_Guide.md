# Indian Income Tax Calculation - Comprehensive Testing Guide

## Overview
This document captures all tax calculation formulas from the backend taxation system for testing purposes. All calculations are based on the Indian Income Tax Act with updates from Budget 2024-25.

---

## TAX SLABS AND RATES

### Old Regime Tax Slabs (Age-Based)

#### Regular Taxpayer (Age < 60)
| Income Range (₹) | Tax Rate | Formula |
|------------------|----------|---------|
| 0 - 2,50,000 | 0% | `IF(A1<=250000, 0, 0)` |
| 2,50,001 - 5,00,000 | 5% | `IF(AND(A1>250000, A1<=500000), (A1-250000)*0.05, 0)` |
| 5,00,001 - 10,00,000 | 20% | `IF(AND(A1>500000, A1<=1000000), (A1-500000)*0.20, 0)` |
| 10,00,001+ | 30% | `IF(A1>1000000, (A1-1000000)*0.30, 0)` |

#### Senior Citizen (Age 60-79)
| Income Range (₹) | Tax Rate | Formula |
|------------------|----------|---------|
| 0 - 3,00,000 | 0% | `IF(A1<=300000, 0, 0)` |
| 3,00,001 - 5,00,000 | 5% | `IF(AND(A1>300000, A1<=500000), (A1-300000)*0.05, 0)` |
| 5,00,001 - 10,00,000 | 20% | `IF(AND(A1>500000, A1<=1000000), (A1-500000)*0.20, 0)` |
| 10,00,001+ | 30% | `IF(A1>1000000, (A1-1000000)*0.30, 0)` |

#### Super Senior Citizen (Age 80+)
| Income Range (₹) | Tax Rate | Formula |
|------------------|----------|---------|
| 0 - 5,00,000 | 0% | `IF(A1<=500000, 0, 0)` |
| 5,00,001 - 10,00,000 | 20% | `IF(AND(A1>500000, A1<=1000000), (A1-500000)*0.20, 0)` |
| 10,00,001+ | 30% | `IF(A1>1000000, (A1-1000000)*0.30, 0)` |

### New Regime Tax Slabs (Budget 2025)
| Income Range (₹) | Tax Rate | Formula |
|------------------|----------|---------|
| 0 - 4,00,000 | 0% | `IF(A1<=400000, 0, 0)` |
| 4,00,001 - 8,00,000 | 5% | `IF(AND(A1>400000, A1<=800000), (A1-400000)*0.05, 0)` |
| 8,00,001 - 12,00,000 | 10% | `IF(AND(A1>800000, A1<=1200000), (A1-800000)*0.10, 0)` |
| 12,00,001 - 16,00,000 | 15% | `IF(AND(A1>1200000, A1<=1600000), (A1-1200000)*0.15, 0)` |
| 16,00,001 - 20,00,000 | 20% | `IF(AND(A1>1600000, A1<=2000000), (A1-1600000)*0.20, 0)` |
| 20,00,001 - 24,00,000 | 25% | `IF(AND(A1>2000000, A1<=2400000), (A1-2000000)*0.25, 0)` |
| 24,00,001+ | 30% | `IF(A1>2400000, (A1-2400000)*0.30, 0)` |

---

## INCOME CALCULATION FORMULAS

### 1. SALARY INCOME

#### Basic Salary Components (Always Taxable)
```excel
=Basic + DA + Special_Allowance + Bonus + Commission + City_Compensatory_Allowance + 
 Rural_Allowance + Proctorship_Allowance + Wardenship_Allowance + Project_Allowance + 
 Deputation_Allowance + Overtime_Allowance + Interim_Relief + Tiffin_Allowance + 
 Fixed_Medical_Allowance + Servant_Allowance + Any_Other_Allowance
```

#### HRA Exemption Calculation (Old Regime Only)
```excel
HRA_Exemption = MIN(
    Actual_HRA_Received,
    IF(HRA_City="Metro", (Basic+DA)*0.5, (Basic+DA)*0.4),
    MAX(0, Rent_Paid - (Basic+DA)*0.1)
)
```

#### Allowance Exemptions (Old Regime Only)
| Allowance | Exemption Formula |
|-----------|-------------------|
| Hills/High Altitude | `MIN(Hills_Allowance, Hills_Exemption_Limit)` |
| Border/Remote Area | `MIN(Border_Allowance, Border_Exemption_Limit)` |
| Transport Employee | `MIN(Transport_Employee_Allowance, MIN(10000, Transport_Employee_Allowance*0.7))` |
| Children Education | `MIN(Children_Education_Allowance, Children_Count*100*Months)` |
| Hostel Allowance | `MIN(Hostel_Allowance, Hostel_Count*300*Months)` |
| Transport (Disabled) | `MIN(Transport_Allowance, Transport_Months*3200)` |
| Underground Mines | `MIN(Underground_Mines_Allowance, Underground_Mines_Months*800)` |
| Entertainment (Govt) | `MIN(Entertainment_Allowance, MIN(Basic*0.2, 5000))` |

#### Net Salary Calculation
```excel
Gross_Salary = Basic_Components + Perquisites_Value
Total_Exemptions = HRA_Exemption + Allowance_Exemptions + Section10_Exemptions
Net_Salary = MAX(0, Gross_Salary - Total_Exemptions)
```

#### Standard Deduction
```excel
Standard_Deduction = IF(Regime="new", MIN(75000, Gross_Salary), MIN(50000, Gross_Salary))
Final_Salary_Income = MAX(0, Net_Salary - Standard_Deduction)
```

### 2. INCOME FROM OTHER SOURCES

#### Interest Income with 80TTA/80TTB
```excel
Total_Interest = Interest_Savings + Interest_FD + Interest_RD

// Old Regime
IF(Age>=60,
    80TTB_Exemption = MIN(50000, Total_Interest),
    80TTA_Exemption = MIN(10000, Interest_Savings)
)

// Taxable Interest
Taxable_Interest = IF(Regime="old",
    IF(Age>=60, MAX(0, Total_Interest-MIN(50000, Total_Interest)),
    MAX(0, Interest_Savings-MIN(10000, Interest_Savings)) + Interest_FD + Interest_RD),
    Total_Interest
)
```

#### Other Income (Always Taxable)
```excel
Other_Taxable_Income = Dividend_Income + Gifts + Other_Interest + Business_Professional_Income + Other_Income
Total_Other_Sources = Taxable_Interest + Other_Taxable_Income
```

### 3. HOUSE PROPERTY INCOME

#### Self-Occupied Property
```excel
Annual_Value = 0
Interest_Deduction = MIN(200000, Interest_on_Home_Loan)
Pre_Construction_Deduction = Pre_Construction_Interest / 5
Net_HP_Income = Annual_Value - Interest_Deduction - Pre_Construction_Deduction
```

#### Let-Out Property
```excel
Annual_Value = Rent_Income
Net_Annual_Value = Annual_Value - Property_Tax
Standard_Deduction = Net_Annual_Value * 0.30
Interest_Deduction = Interest_on_Home_Loan  // No limit for let-out
Pre_Construction_Deduction = Pre_Construction_Interest / 5
Net_HP_Income = Net_Annual_Value - Standard_Deduction - Interest_Deduction - Pre_Construction_Deduction
```

### 4. CAPITAL GAINS

#### Short-Term Capital Gains
```excel
// STCG 111A (Equity with STT) - 20% rate (Budget 2024)
STCG_111A_Tax = STCG_111A * 0.20

// STCG Other Assets - Taxed at slab rates
STCG_Slab_Rate = STCG_Other_Assets + STCG_Debt_MF
```

#### Long-Term Capital Gains
```excel
// LTCG 112A (Equity with STT) - 12.5% rate above Rs. 1.25L (Budget 2024)
LTCG_112A_Taxable = MAX(0, LTCG_112A - 125000)
LTCG_112A_Tax = LTCG_112A_Taxable * 0.125

// LTCG Other Assets - 12.5% rate (Budget 2024)
LTCG_Other = LTCG_Other_Assets + LTCG_Debt_MF
LTCG_Other_Tax = LTCG_Other * 0.125
```

### 5. LEAVE ENCASHMENT

#### Exemption Calculation (Old Regime, Non-Govt, at Retirement)
```excel
Actual_Received = Leave_Encashment_Amount
Ten_Months_Salary = Average_Monthly_Salary * 10
Statutory_Limit = 2500000
Daily_Salary = Average_Monthly_Salary / 30
Unexpired_Leave_Value = MIN(Leave_Encashed, Service_Years*30) * Daily_Salary

Exemption = MIN(Actual_Received, Ten_Months_Salary, Statutory_Limit, Unexpired_Leave_Value)
Taxable_Leave_Encashment = MAX(0, Actual_Received - Exemption)
```

### 6. VOLUNTARY RETIREMENT SCHEME (VRS)

#### VRS Value Calculation
```excel
IF(AND(Age>=40, Service_Years>=10),
    Single_Day_Salary = Last_Monthly_Salary / 30,
    Salary_45_Days = Single_Day_Salary * 45,
    Months_Remaining = (60 - Age) * 12,
    Salary_For_Remaining_Months = Last_Monthly_Salary * Months_Remaining,
    Salary_Against_Service = Salary_45_Days * Service_Years,
    VRS_Value = MIN(Salary_For_Remaining_Months, Salary_Against_Service),
    0
)

VRS_Exemption = MIN(VRS_Amount, 500000)
Taxable_VRS = MAX(0, VRS_Amount - VRS_Exemption)
```

### 7. PENSION INCOME

#### Computed Pension (Regular Monthly)
```excel
Computed_Pension_Amount = Total_Pension_Income * Computed_Pension_Percentage

// Non-Government Employee
IF(Is_Govt_Employee=FALSE,
    Exemption_Fraction = IF(Is_Gratuity_Received, 1/3, 1/2),
    Exemption_Limit = Total_Pension_Income * Exemption_Fraction,
    Taxable_Computed_Pension = MIN(Computed_Pension_Amount, Exemption_Limit),
    Taxable_Computed_Pension = Computed_Pension_Amount
)
```

#### Uncomputed Pension (Commutation)
```excel
Uncomputed_Pension_Annual = IF(Frequency="Monthly", Amount*12,
                               IF(Frequency="Quarterly", Amount*4, Amount))
```

### 8. GRATUITY

#### Exemption Calculation (Non-Government Employee)
```excel
Service_Years = (DOL - DOJ) / 365.25
Completed_Years = IF((Service_Years - INT(Service_Years))*365.25 > 182.625, 
                     INT(Service_Years)+1, INT(Service_Years))

Actual_Received = Gratuity_Amount
Daily_Salary = Last_Monthly_Salary / 26
Fifteen_Days_Salary = Daily_Salary * 15
Salary_Based_Exemption = Fifteen_Days_Salary * Completed_Years
Statutory_Limit = 2000000

Exemption = MIN(Actual_Received, Salary_Based_Exemption, Statutory_Limit)
Taxable_Gratuity = IF(Is_Govt_Employee, 0, MAX(0, Actual_Received - Exemption))
```

### 9. RETRENCHMENT COMPENSATION

#### Exemption Calculation
```excel
Service_Years = (DOL - DOJ) / 365.25
Completed_Years = IF((Service_Years - INT(Service_Years))*365.25 > 182.625, 
                     INT(Service_Years)+1, INT(Service_Years))

Actual_Received = Retrenchment_Amount
Daily_Salary = Last_Monthly_Salary / 30
Fifteen_Days_Salary = Daily_Salary * 15
Salary_Based_Exemption = Fifteen_Days_Salary * Completed_Years
Statutory_Limit = 500000

Exemption = MIN(Actual_Received, Salary_Based_Exemption, Statutory_Limit)
Taxable_Retrenchment = MAX(0, Actual_Received - Exemption)
```

---

## DEDUCTION CALCULATION FORMULAS (OLD REGIME ONLY)

### Section 80C Group (Combined Limit: ₹1,50,000)
```excel
Section_80C_Components = LIC + EPF + SSP + NSC + ULIP + ELSS + Tuition_Fees + Home_Loan_Principal + Stamp_Duty + Tax_Saving_FD + SCSS + Others + Section_80CCC + Section_80CCD_1

Section_80C_Deduction = MIN(Section_80C_Components, 150000)
Section_80CCD_1B_Deduction = MIN(Section_80CCD_1B_Additional, 50000)
Total_80C_Group = Section_80C_Deduction + Section_80CCD_1B_Deduction
```

### Section 80CCD(2) - Employer NPS Contribution
```excel
Max_Limit = IF(Is_Govt_Employee, (Basic+DA)*0.14, (Basic+DA)*0.10)
Section_80CCD_2_Deduction = MIN(Employer_NPS_Contribution, Max_Limit)
```

### Section 80D - Health Insurance
```excel
// Self and Family
Self_Family_Limit = IF(Age>=60, 50000, 25000)
Preventive_Checkup_Limit = MIN(Preventive_Checkup, 5000)
Section_80D_Self = MIN(Health_Insurance_Self + Preventive_Checkup_Limit, Self_Family_Limit)

// Parents
Parent_Limit = IF(Parent_Age>=60, 50000, 25000)
Section_80D_Parent = MIN(Health_Insurance_Parent, Parent_Limit)

Total_80D = Section_80D_Self + Section_80D_Parent
```

### Section 80DD - Disability (Fixed Deduction)
```excel
Section_80DD = IF(Relation_Valid AND Disability_Percentage="Between 40%-80%", 75000,
                  IF(Relation_Valid AND Disability_Percentage="More than 80%", 125000, 0))
```

### Section 80DDB - Medical Treatment
```excel
Relevant_Age = IF(Relation="Self", Taxpayer_Age, Patient_Age)
Limit = IF(Relevant_Age>=60, 100000, 40000)
Section_80DDB = MIN(Medical_Expenses, Limit)
```

### Section 80E - Education Loan Interest
```excel
Section_80E = IF(Relation_Valid, Education_Loan_Interest, 0)  // No upper limit
```

### Section 80EEB - Electric Vehicle Loan Interest
```excel
Valid_Purchase_Date = IF(AND(EV_Purchase_Date>=DATE(2019,4,1), EV_Purchase_Date<=DATE(2025,3,31)), TRUE, FALSE)
Section_80EEB = IF(Valid_Purchase_Date, MIN(EV_Loan_Interest, 150000), 0)
```

### Section 80U - Self Disability (Fixed Deduction)
```excel
Section_80U = IF(Disability_Percentage="Between 40%-80%", 75000,
                 IF(Disability_Percentage="More than 80%", 125000, 0))
```

### Section 80G - Charitable Donations
```excel
// Calculate Adjusted Gross Income for 80G
Other_Deductions = Sum_of_80C_to_80U_excluding_80G
Adjusted_Gross_Income = Salary_Income + Other_Sources_Income + STCG_Slab_Rate - Other_Deductions

// 80G Deductions
Section_80G_100_WO_QL = Donation_100_Without_Limit
Section_80G_50_WO_QL = Donation_50_Without_Limit * 0.5
Section_80G_100_QL = MIN(Donation_100_With_Limit, Adjusted_Gross_Income * 0.1)
Section_80G_50_QL = MIN(Donation_50_With_Limit * 0.5, Adjusted_Gross_Income * 0.1)

Total_80G = Section_80G_100_WO_QL + Section_80G_50_WO_QL + Section_80G_100_QL + Section_80G_50_QL
```

### Section 80GGC - Political Party Donations
```excel
Section_80GGC = Political_Party_Donations  // 100% deduction, no limit
```

---

## FINAL TAX CALCULATION

### Step 1: Calculate Gross Income
```excel
Gross_Income = Final_Salary_Income + Other_Sources_Income + House_Property_Income + 
               STCG_Slab_Rate + Leave_Encashment_Income + VRS_Income + 
               Pension_Income + Gratuity_Income + Retrenchment_Income
```

### Step 2: Calculate Total Deductions (Old Regime Only)
```excel
Total_Deductions = IF(Regime="old", 
    Total_80C_Group + Section_80CCD_2 + Total_80D + Section_80DD + 
    Section_80DDB + Section_80E + Section_80EEB + Section_80U + 
    Total_80G + Section_80GGC, 
    0)
```

### Step 3: Calculate Net Taxable Income
```excel
Net_Taxable_Income = MAX(0, Gross_Income - Total_Deductions)
```

### Step 4: Calculate Regular Tax (Based on Slabs)
Use the appropriate slab calculation from the tables above.

### Step 5: Calculate Capital Gains Tax (Special Rates)
```excel
STCG_Special_Tax = STCG_111A * 0.20
LTCG_Special_Tax = MAX(0, LTCG_112A - 125000) * 0.125 + LTCG_Other * 0.125
```

### Step 6: Calculate Base Tax
```excel
Base_Tax = Regular_Tax + STCG_Special_Tax + LTCG_Special_Tax
```

### Step 7: Apply Section 87A Rebate
```excel
Rebate_87A = IF(Regime="old" AND Net_Taxable_Income<=500000, MIN(12500, Base_Tax),
                IF(Regime="new" AND Net_Taxable_Income<=1200000, MIN(60000, Base_Tax), 0))

Tax_After_Rebate = MAX(0, Base_Tax - Rebate_87A)
```

### Step 8: Calculate Surcharge
```excel
Surcharge_Rate = IF(Net_Taxable_Income>50000000, 0.37,
                    IF(Net_Taxable_Income>20000000, 0.25,
                       IF(Net_Taxable_Income>10000000, 0.15,
                          IF(Net_Taxable_Income>5000000, 0.10, 0))))

Regular_Surcharge = Tax_After_Rebate * Surcharge_Rate

// Apply Marginal Relief
Income_Above_Threshold = MAX(0, Net_Taxable_Income - Threshold)
Relief = MAX(0, Regular_Surcharge - Income_Above_Threshold)
Surcharge = Regular_Surcharge - Relief

Tax_After_Surcharge = Tax_After_Rebate + Surcharge
```

### Step 9: Calculate Health & Education Cess
```excel
Health_Education_Cess = Tax_After_Surcharge * 0.04
Final_Tax = Tax_After_Surcharge + Health_Education_Cess
```

---

## TESTING SCENARIOS

### Test Case 1: Young Professional (New Regime)
- **Age**: 28
- **Regime**: New
- **Basic Salary**: ₹8,00,000
- **DA**: ₹1,00,000
- **HRA**: ₹3,00,000
- **Expected Tax**: ₹45,000 (after standard deduction and rebate)

### Test Case 2: Senior Citizen (Old Regime with Deductions)
- **Age**: 65
- **Regime**: Old
- **Pension**: ₹6,00,000
- **Section 80C**: ₹1,50,000
- **Section 80D**: ₹50,000
- **Expected Tax**: Lower due to senior citizen exemption and deductions

### Test Case 3: High Income with Capital Gains
- **Salary**: ₹25,00,000
- **LTCG 112A**: ₹3,00,000
- **STCG 111A**: ₹1,00,000
- **Expected**: Surcharge applicable, special rates for capital gains

### Test Case 4: Government Employee
- **Basic**: ₹50,000
- **DA**: ₹25,000
- **Entertainment Allowance**: ₹10,000
- **Expected**: Entertainment allowance exemption up to ₹5,000

---

## VALIDATION CHECKS

### Income Validation
1. **Salary Components**: All components ≥ 0
2. **HRA Calculation**: Verify metro vs non-metro rates
3. **Interest Income**: Verify 80TTA/80TTB application
4. **Capital Gains**: Verify correct rates and exemptions

### Deduction Validation
1. **Section 80C**: Combined limit of ₹1,50,000
2. **Section 80D**: Age-based limits correctly applied
3. **Section 80DD/80U**: Fixed deductions based on disability percentage
4. **Section 80G**: Qualifying limit calculations

### Tax Calculation Validation
1. **Slab Rates**: Correct application based on regime and age
2. **Rebate**: Verify income limits and rebate amounts
3. **Surcharge**: Verify thresholds and marginal relief
4. **Cess**: 4% on (tax + surcharge)

---

## EXCEL FORMULA SUMMARY

Create separate worksheets for:
1. **Input Data**: All income and deduction inputs
2. **Income Calculations**: All income source calculations
3. **Deduction Calculations**: All deduction calculations
4. **Tax Calculation**: Final tax computation
5. **Validation**: Cross-checks and validation formulas

Use named ranges for constants like tax slab limits, deduction limits, etc., to make formulas more readable and maintainable.

This comprehensive guide provides all necessary formulas to test the Indian taxation system thoroughly, ensuring compliance with current Income Tax Act provisions and recent budget updates. 