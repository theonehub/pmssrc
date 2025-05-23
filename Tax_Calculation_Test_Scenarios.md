# Tax Calculation Test Scenarios - Comprehensive Testing Guide

## Overview
This document provides comprehensive test scenarios with exact expected results for testing the Indian taxation system. Each scenario includes input data, step-by-step calculations, and expected outputs.

---

## TEST SCENARIO 1: Young Professional - New Regime

### Input Data
- **Employee Details**: Age 28, New Regime, Private Employee
- **Salary**: Basic ₹6,00,000, DA ₹1,00,000, HRA ₹2,50,000, Special Allowance ₹1,50,000
- **Other Income**: Interest on Savings ₹15,000, FD Interest ₹25,000
- **Deductions**: None (New Regime)

### Step-by-Step Calculation

#### Income Calculation
```
1. Gross Salary = 600000 + 100000 + 250000 + 150000 = 1,100,000
2. Standard Deduction = MIN(75000, 1100000) = 75,000
3. Interest Income = 15000 + 25000 = 40,000 (No exemptions in new regime)
4. Net Taxable Income = 1,100,000 - 75,000 + 40,000 = 1,065,000
```

#### Tax Calculation (New Regime Slabs)
```
1. 0 - 4,00,000: 0% = 0
2. 4,00,001 - 8,00,000: 5% = (800000 - 400000) × 0.05 = 20,000
3. 8,00,001 - 10,65,000: 10% = (1065000 - 800000) × 0.10 = 26,500
4. Regular Tax = 0 + 20,000 + 26,500 = 46,500
```

#### Rebate and Final Tax
```
1. Section 87A Rebate = MIN(60000, 46500) = 46,500 (Income ≤ 12,00,000)
2. Tax After Rebate = 46,500 - 46,500 = 0
3. Final Tax = 0
```

### Expected Output
- **Gross Income**: ₹11,40,000
- **Net Taxable Income**: ₹10,65,000
- **Tax Before Rebate**: ₹46,500
- **Section 87A Rebate**: ₹46,500
- **Final Tax**: ₹0

---

## TEST SCENARIO 2: Senior Citizen - Old Regime with Deductions

### Input Data
- **Employee Details**: Age 65, Old Regime, Private Employee
- **Pension**: ₹4,50,000 per annum
- **Interest**: Savings ₹12,000, FD ₹45,000, RD ₹8,000
- **House Property**: Self-occupied, Home loan interest ₹1,80,000
- **Deductions**: 
  - Section 80C: ₹1,50,000
  - Section 80D Self: ₹35,000 (Age 65)
  - Section 80D Parents: ₹40,000 (Parent age 85)

### Step-by-Step Calculation

#### Income Calculation
```
1. Pension Income = 450,000
2. Total Interest = 12000 + 45000 + 8000 = 65,000
3. Section 80TTB Exemption = MIN(50000, 65000) = 50,000 (Age ≥ 60)
4. Taxable Interest = 65,000 - 50,000 = 15,000
5. House Property (Self-occupied):
   - Annual Value = 0
   - Interest Deduction = MIN(200000, 180000) = 180,000
   - Net HP Income = 0 - 180,000 = -180,000
6. Gross Income = 450,000 + 15,000 - 180,000 = 285,000
```

#### Deduction Calculation
```
1. Section 80C = 150,000
2. Section 80D Self = MIN(35000 + 0, 50000) = 35,000 (Age ≥ 60)
3. Section 80D Parents = MIN(40000, 50000) = 40,000 (Parent age ≥ 60)
4. Total Deductions = 150,000 + 35,000 + 40,000 = 225,000
```

#### Tax Calculation
```
1. Net Income = MAX(0, 285,000 - 225,000) = 60,000
2. Senior Citizen Exemption = 300,000
3. Since 60,000 < 300,000, Tax = 0
```

### Expected Output
- **Gross Income**: ₹2,85,000
- **Total Deductions**: ₹2,25,000
- **Net Taxable Income**: ₹60,000
- **Tax**: ₹0 (Below senior citizen exemption limit)

---

## TEST SCENARIO 3: High Income with Capital Gains

### Input Data
- **Employee Details**: Age 45, Old Regime, Private Employee
- **Salary**: Basic ₹15,00,000, DA ₹3,00,000, HRA ₹6,00,000, Bonus ₹5,00,000
- **Capital Gains**: 
  - STCG 111A: ₹2,00,000
  - LTCG 112A: ₹4,00,000
  - LTCG Other: ₹1,50,000
- **Deductions**: Section 80C ₹1,50,000, Section 80D ₹25,000

### Step-by-Step Calculation

#### Income Calculation
```
1. Gross Salary = 1500000 + 300000 + 600000 + 500000 = 2,900,000
2. HRA Exemption = MIN(600000, 1800000×0.4, MAX(0, RentPaid - 180000)) = Need rent data
3. Assuming metro city and rent ₹8,00,000:
   HRA Exemption = MIN(600000, 900000, 620000) = 600,000
4. Standard Deduction = MIN(50000, 2900000) = 50,000
5. Net Salary = 2,900,000 - 600,000 - 50,000 = 2,250,000
6. STCG at slab rate = 0
7. Gross Income = 2,250,000
```

#### Capital Gains Tax
```
1. STCG 111A Tax = 200,000 × 0.20 = 40,000
2. LTCG 112A Taxable = MAX(0, 400000 - 125000) = 275,000
3. LTCG 112A Tax = 275,000 × 0.125 = 34,375
4. LTCG Other Tax = 150,000 × 0.125 = 18,750
5. Total CG Tax = 40,000 + 34,375 + 18,750 = 93,125
```

#### Regular Tax Calculation
```
1. Net Income after deductions = 2,250,000 - 175,000 = 2,075,000
2. Tax Slabs (Regular taxpayer):
   - 0 - 250,000: 0% = 0
   - 250,001 - 500,000: 5% = 12,500
   - 500,001 - 1,000,000: 20% = 100,000
   - 1,000,001 - 2,075,000: 30% = 322,500
3. Regular Tax = 0 + 12,500 + 100,000 + 322,500 = 435,000
```

#### Surcharge Calculation
```
1. Base Tax = 435,000 + 93,125 = 528,125
2. Income > 10,00,000, so Surcharge = 15%
3. Surcharge = 528,125 × 0.15 = 79,219
4. Tax + Surcharge = 528,125 + 79,219 = 607,344
```

#### Final Tax
```
1. Health & Education Cess = 607,344 × 0.04 = 24,294
2. Final Tax = 607,344 + 24,294 = 631,638
```

### Expected Output
- **Gross Income**: ₹22,50,000
- **Capital Gains Tax**: ₹93,125
- **Regular Tax**: ₹4,35,000
- **Surcharge**: ₹79,219
- **Cess**: ₹24,294
- **Final Tax**: ₹6,31,638

---

## TEST SCENARIO 4: Government Employee with Allowances

### Input Data
- **Employee Details**: Age 35, Old Regime, Government Employee
- **Salary**: Basic ₹75,000, DA ₹25,000, HRA ₹30,000
- **Allowances**: 
  - Entertainment Allowance ₹8,000
  - Children Education Allowance ₹2,400 (2 children, 12 months)
  - Transport Allowance ₹6,000
- **Deductions**: Section 80C ₹1,20,000

### Step-by-Step Calculation

#### Allowance Exemptions
```
1. Entertainment Allowance = MIN(8000, 75000×0.2, 5000) = MIN(8000, 15000, 5000) = 5,000
2. Children Education = MIN(2400, 2×100×12) = MIN(2400, 2400) = 2,400
3. Transport Allowance = No specific exemption for govt employees = 0
```

#### Income Calculation
```
1. Gross Salary = 75000 + 25000 + 30000 + 8000 + 2400 + 6000 = 146,400
2. HRA Exemption = MIN(30000, 100000×0.4, MAX(0, RentPaid - 10000))
3. Assuming rent ₹25,000: HRA Exemption = MIN(30000, 40000, 15000) = 15,000
4. Total Exemptions = 15,000 + 5,000 + 2,400 = 22,400
5. Standard Deduction = MIN(50000, 146400) = 50,000
6. Net Salary = 146,400 - 22,400 - 50,000 = 74,000
```

#### Tax Calculation
```
1. Net Income after 80C = 74,000 - 120,000 = 0 (Cannot be negative)
2. Taxable Income = 0
3. Tax = 0
```

### Expected Output
- **Gross Salary**: ₹1,46,400
- **Total Exemptions**: ₹22,400
- **Standard Deduction**: ₹50,000
- **Net Income**: ₹74,000
- **After Deductions**: ₹0
- **Final Tax**: ₹0

---

## TEST SCENARIO 5: Leave Encashment and VRS

### Input Data
- **Employee Details**: Age 55, Old Regime, Private Employee, Service 25 years
- **Salary**: Basic ₹1,20,000, DA ₹40,000
- **Leave Encashment**: ₹8,00,000 (240 days encashed)
- **VRS**: ₹15,00,000
- **Average Monthly Salary**: ₹1,60,000

### Step-by-Step Calculation

#### Leave Encashment Exemption
```
1. Actual Received = 800,000
2. Ten Months Salary = 160,000 × 10 = 1,600,000
3. Statutory Limit = 2,500,000
4. Daily Salary = 160,000 ÷ 30 = 5,333
5. Max Leave Days = 25 × 30 = 750 days
6. Unexpired Leave Value = MIN(240, 750) × 5,333 = 240 × 5,333 = 1,280,000
7. Exemption = MIN(800000, 1600000, 2500000, 1280000) = 800,000
8. Taxable Leave Encashment = 800,000 - 800,000 = 0
```

#### VRS Calculation
```
1. Age 55, Service 25 years (both > minimum required)
2. Single Day Salary = 160,000 ÷ 30 = 5,333
3. Salary 45 Days = 5,333 × 45 = 240,000
4. Months Remaining = (60 - 55) × 12 = 60 months
5. Salary for Remaining Months = 160,000 × 60 = 9,600,000
6. Salary Against Service = 240,000 × 25 = 6,000,000
7. VRS Value = MIN(9600000, 6000000) = 6,000,000
8. VRS Exemption = MIN(1500000, 500000) = 500,000
9. Taxable VRS = 1,500,000 - 500,000 = 1,000,000
```

#### Tax Calculation
```
1. Annual Salary = (120000 + 40000) × 12 = 1,920,000
2. Standard Deduction = 50,000
3. Net Salary = 1,920,000 - 50,000 = 1,870,000
4. Total Taxable Income = 1,870,000 + 0 + 1,000,000 = 2,870,000
5. Tax Calculation (after deductions):
   - Assuming 80C ₹150,000: Net = 2,870,000 - 150,000 = 2,720,000
   - Tax = 12,500 + 100,000 + 516,000 = 628,500
```

### Expected Output
- **Salary Income**: ₹18,70,000
- **Leave Encashment (Taxable)**: ₹0
- **VRS (Taxable)**: ₹10,00,000
- **Total Taxable Income**: ₹27,20,000
- **Tax Before Surcharge**: ₹6,28,500
- **Surcharge (15%)**: ₹94,275
- **Cess**: ₹28,911
- **Final Tax**: ₹7,51,686

---

## VALIDATION CHECKLIST

### For Each Test Case, Verify:

#### Income Calculations
- [ ] All salary components correctly summed
- [ ] HRA exemption calculated with correct city rates
- [ ] Standard deduction applied based on regime
- [ ] Interest exemptions (80TTA/80TTB) applied correctly
- [ ] House property calculations (30% deduction for let-out)
- [ ] Capital gains rates: STCG 111A (20%), LTCG (12.5%)

#### Deduction Calculations
- [ ] Section 80C combined limit of ₹1,50,000
- [ ] Section 80D age-based limits applied
- [ ] Section 80DD/80U fixed deductions
- [ ] Deductions only applied in old regime

#### Tax Calculations
- [ ] Correct tax slabs based on regime and age
- [ ] Capital gains taxed at special rates
- [ ] Section 87A rebate applied correctly
- [ ] Surcharge thresholds and rates
- [ ] Marginal relief for surcharge
- [ ] 4% cess on (tax + surcharge)

#### Special Cases
- [ ] Senior citizen exemption limits
- [ ] Government employee specific exemptions
- [ ] Leave encashment exemption calculation
- [ ] VRS exemption (₹5 lakh limit)
- [ ] Gratuity exemption for non-govt employees

---

## AUTOMATION TESTING FRAMEWORK

### Test Data Structure
```json
{
  "test_case_id": "TC001",
  "description": "Young Professional - New Regime",
  "input": {
    "employee": {
      "age": 28,
      "regime": "new",
      "is_govt_employee": false
    },
    "salary": {
      "basic": 600000,
      "da": 100000,
      "hra": 250000,
      "special_allowance": 150000
    },
    "other_income": {
      "interest_savings": 15000,
      "interest_fd": 25000
    }
  },
  "expected_output": {
    "gross_income": 1140000,
    "net_taxable_income": 1065000,
    "tax_before_rebate": 46500,
    "rebate_87a": 46500,
    "final_tax": 0
  }
}
```

### Validation Rules
1. **Tolerance**: ±₹1 for rounding differences
2. **Mandatory Fields**: All income components must be ≥ 0
3. **Business Rules**: Verify all exemption limits and rates
4. **Cross-Validation**: Sum of components equals total

This comprehensive testing guide ensures thorough validation of the Indian taxation system against all major scenarios and edge cases. 