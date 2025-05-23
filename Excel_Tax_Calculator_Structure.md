# Excel Tax Calculator - Worksheet Structure and Formulas

## Worksheet 1: INPUT_DATA

### Basic Information (A1:B20)
| Cell | Field | Value/Formula |
|------|-------|---------------|
| A1 | Employee ID | Text Input |
| A2 | Age | Numeric Input |
| A3 | Tax Regime | Dropdown: "old", "new" |
| A4 | Is Government Employee | Dropdown: TRUE, FALSE |
| A5 | Tax Year | Text Input (e.g., "2024-25") |
| A6 | Date of Joining | Date Input |
| A7 | Date of Leaving | Date Input |
| A8 | Service Years | `=DATEDIF(B6,B7,"Y")` |

### Salary Components (A10:B40)
| Cell | Component | Input Type |
|------|-----------|------------|
| B10 | Basic Salary | Numeric |
| B11 | Dearness Allowance | Numeric |
| B12 | HRA | Numeric |
| B13 | Actual Rent Paid | Numeric |
| B14 | HRA City | Dropdown: "Delhi", "Mumbai", "Kolkata", "Chennai", "Others" |
| B15 | Special Allowance | Numeric |
| B16 | Bonus | Numeric |
| B17 | Commission | Numeric |
| B18 | Transport Allowance | Numeric |
| B19 | Children Education Allowance | Numeric |
| B20 | Children Count | Numeric |
| B21 | Education Months | Numeric |
| B22 | Entertainment Allowance | Numeric |
| B23 | Medical Allowance | Numeric |
| B24 | Any Other Allowance | Numeric |

### Other Income Sources (A45:B60)
| Cell | Income Source | Input Type |
|------|---------------|------------|
| B45 | Interest on Savings | Numeric |
| B46 | Interest on FD | Numeric |
| B47 | Interest on RD | Numeric |
| B48 | Dividend Income | Numeric |
| B49 | Gift Income | Numeric |
| B50 | Other Interest | Numeric |
| B51 | Business Income | Numeric |
| B52 | Other Income | Numeric |

### House Property (A65:B75)
| Cell | Property Detail | Input Type |
|------|-----------------|------------|
| B65 | Property Status | Dropdown: "Self-Occupied", "Let-Out" |
| B66 | Rent Income | Numeric |
| B67 | Property Tax | Numeric |
| B68 | Home Loan Interest | Numeric |
| B69 | Pre-Construction Interest | Numeric |

### Capital Gains (A80:B90)
| Cell | Capital Gain | Input Type |
|------|--------------|------------|
| B80 | STCG 111A | Numeric |
| B81 | STCG Other Assets | Numeric |
| B82 | STCG Debt MF | Numeric |
| B83 | LTCG 112A | Numeric |
| B84 | LTCG Other Assets | Numeric |
| B85 | LTCG Debt MF | Numeric |

### Leave Encashment & Others (A95:B110)
| Cell | Component | Input Type |
|------|-----------|------------|
| B95 | Leave Encashment Amount | Numeric |
| B96 | Leave Days Encashed | Numeric |
| B97 | VRS Amount | Numeric |
| B98 | Pension Income | Numeric |
| B99 | Gratuity Amount | Numeric |
| B100 | Retrenchment Compensation | Numeric |
| B101 | Average Monthly Salary | Numeric |

---

## Worksheet 2: DEDUCTIONS

### Section 80C Components (A1:B20)
| Cell | Deduction | Input Type |
|------|-----------|------------|
| B1 | LIC Premium | Numeric |
| B2 | EPF Contribution | Numeric |
| B3 | PPF Investment | Numeric |
| B4 | NSC Investment | Numeric |
| B5 | ELSS Investment | Numeric |
| B6 | Home Loan Principal | Numeric |
| B7 | Tuition Fees | Numeric |
| B8 | Others 80C | Numeric |
| B9 | **Total 80C** | `=SUM(B1:B8)` |
| B10 | **80C Deduction** | `=MIN(B9,150000)` |

### Section 80CCD (A25:B35)
| Cell | NPS Deduction | Formula |
|------|---------------|---------|
| B25 | NPS Self Contribution | Numeric Input |
| B26 | NPS Additional 1B | Numeric Input |
| B27 | NPS Employer Contribution | Numeric Input |
| B28 | **80CCD(1) Included in 80C** | Already in B10 |
| B29 | **80CCD(1B) Additional** | `=MIN(B26,50000)` |
| B30 | **80CCD(2) Employer** | `=MIN(B27,IF(INPUT_DATA.B4,(INPUT_DATA.B10+INPUT_DATA.B11)*0.14,(INPUT_DATA.B10+INPUT_DATA.B11)*0.10))` |

### Section 80D Health Insurance (A40:B50)
| Cell | Health Insurance | Formula |
|------|------------------|---------|
| B40 | Self & Family Premium | Numeric Input |
| B41 | Preventive Checkup | Numeric Input |
| B42 | Parent Premium | Numeric Input |
| B43 | Parent Age | Numeric Input |
| B44 | **80D Self & Family** | `=MIN(B40+MIN(B41,5000),IF(INPUT_DATA.B2>=60,50000,25000))` |
| B45 | **80D Parents** | `=MIN(B42,IF(B43>=60,50000,25000))` |
| B46 | **Total 80D** | `=B44+B45` |

### Other Deductions (A55:B80)
| Cell | Deduction Section | Formula |
|------|-------------------|---------|
| B55 | 80DD Relation | Dropdown Input |
| B56 | 80DD Disability % | Dropdown: "Between 40%-80%", "More than 80%" |
| B57 | **80DD Deduction** | `=IF(AND(B55<>"",B56<>""),IF(B56="Between 40%-80%",75000,125000),0)` |
| B60 | 80DDB Medical Expenses | Numeric Input |
| B61 | 80DDB Patient Age | Numeric Input |
| B62 | **80DDB Deduction** | `=MIN(B60,IF(B61>=60,100000,40000))` |
| B65 | 80E Education Loan Interest | Numeric Input |
| B66 | **80E Deduction** | `=B65` |
| B70 | 80U Self Disability % | Dropdown: "Between 40%-80%", "More than 80%" |
| B71 | **80U Deduction** | `=IF(B70="Between 40%-80%",75000,IF(B70="More than 80%",125000,0))` |
| B75 | 80G Donations | Numeric Input |
| B76 | **80G Deduction** | `=B75` (Simplified) |

---

## Worksheet 3: CALCULATIONS

### Income Calculations (A1:C50)

#### Salary Income (A1:C20)
| Cell | Description | Formula |
|------|-------------|---------|
| C1 | **Basic Components** | `=SUM(INPUT_DATA.B10:B24)` |
| C2 | **HRA Exemption** | `=IF(INPUT_DATA.B3="old",MIN(INPUT_DATA.B12,IF(INPUT_DATA.B14="Metro",(INPUT_DATA.B10+INPUT_DATA.B11)*0.5,(INPUT_DATA.B10+INPUT_DATA.B11)*0.4),MAX(0,INPUT_DATA.B13-(INPUT_DATA.B10+INPUT_DATA.B11)*0.1)),0)` |
| C3 | **Other Exemptions** | Detailed calculation needed |
| C4 | **Standard Deduction** | `=IF(INPUT_DATA.B3="new",MIN(75000,C1),MIN(50000,C1))` |
| C5 | **Net Salary Income** | `=MAX(0,C1-C2-C3-C4)` |

#### Other Sources Income (A25:C35)
| Cell | Description | Formula |
|------|-------------|---------|
| C25 | **Total Interest** | `=SUM(INPUT_DATA.B45:B47)` |
| C26 | **Interest Exemption** | `=IF(INPUT_DATA.B3="old",IF(INPUT_DATA.B2>=60,MIN(50000,C25),MIN(10000,INPUT_DATA.B45)),0)` |
| C27 | **Taxable Interest** | `=MAX(0,C25-C26)` |
| C28 | **Other Income** | `=SUM(INPUT_DATA.B48:B52)` |
| C29 | **Total Other Sources** | `=C27+C28` |

#### House Property Income (A40:C50)
| Cell | Description | Formula |
|------|-------------|---------|
| C40 | **Annual Value** | `=IF(INPUT_DATA.B65="Self-Occupied",0,INPUT_DATA.B66)` |
| C41 | **Property Tax** | `=INPUT_DATA.B67` |
| C42 | **Net Annual Value** | `=MAX(0,C40-C41)` |
| C43 | **Standard Deduction** | `=IF(INPUT_DATA.B65="Let-Out",C42*0.3,0)` |
| C44 | **Interest Deduction** | `=IF(INPUT_DATA.B65="Self-Occupied",MIN(200000,INPUT_DATA.B68),INPUT_DATA.B68)` |
| C45 | **Pre-Construction** | `=INPUT_DATA.B69/5` |
| C46 | **Net HP Income** | `=C42-C43-C44-C45` |

#### Capital Gains (A55:C70)
| Cell | Description | Formula |
|------|-------------|---------|
| C55 | **STCG Slab Rate** | `=INPUT_DATA.B81+INPUT_DATA.B82` |
| C56 | **STCG Special Tax** | `=INPUT_DATA.B80*0.20` |
| C57 | **LTCG 112A Taxable** | `=MAX(0,INPUT_DATA.B83-125000)` |
| C58 | **LTCG 112A Tax** | `=C57*0.125` |
| C59 | **LTCG Other Tax** | `=(INPUT_DATA.B84+INPUT_DATA.B85)*0.125` |

### Total Income Summary (A75:C85)
| Cell | Description | Formula |
|------|-------------|---------|
| C75 | **Gross Income** | `=C5+C29+C46+C55` |
| C76 | **Total Deductions** | `=IF(INPUT_DATA.B3="old",SUM(DEDUCTIONS.B10,DEDUCTIONS.B29,DEDUCTIONS.B30,DEDUCTIONS.B46,DEDUCTIONS.B57,DEDUCTIONS.B62,DEDUCTIONS.B66,DEDUCTIONS.B71,DEDUCTIONS.B76),0)` |
| C77 | **Net Taxable Income** | `=MAX(0,C75-C76)` |

---

## Worksheet 4: TAX_CALCULATION

### Tax Slab Calculation (A1:C20)
| Cell | Description | Formula |
|------|-------------|---------|
| C1 | **Age Category** | `=IF(INPUT_DATA.B2>=80,"Super Senior",IF(INPUT_DATA.B2>=60,"Senior","Regular"))` |
| C2 | **Regime** | `=INPUT_DATA.B3` |
| C5 | **Tax Slab 1** | Complex nested IF formula for slabs |
| C6 | **Tax Slab 2** | Complex nested IF formula for slabs |
| C7 | **Tax Slab 3** | Complex nested IF formula for slabs |
| C8 | **Tax Slab 4** | Complex nested IF formula for slabs |
| C9 | **Tax Slab 5** | Complex nested IF formula for slabs |
| C10 | **Regular Tax** | `=SUM(C5:C9)` |

### Final Tax Calculation (A25:C40)
| Cell | Description | Formula |
|------|-------------|---------|
| C25 | **Base Tax** | `=C10+CALCULATIONS.C56+CALCULATIONS.C58+CALCULATIONS.C59` |
| C26 | **87A Rebate** | `=IF(AND(INPUT_DATA.B3="old",CALCULATIONS.C77<=500000),MIN(12500,C25),IF(AND(INPUT_DATA.B3="new",CALCULATIONS.C77<=1200000),MIN(60000,C25),0))` |
| C27 | **Tax After Rebate** | `=MAX(0,C25-C26)` |
| C28 | **Surcharge Rate** | `=IF(CALCULATIONS.C77>50000000,0.37,IF(CALCULATIONS.C77>20000000,0.25,IF(CALCULATIONS.C77>10000000,0.15,IF(CALCULATIONS.C77>5000000,0.10,0))))` |
| C29 | **Surcharge** | `=C27*C28` |
| C30 | **Tax + Surcharge** | `=C27+C29` |
| C31 | **Health & Education Cess** | `=C30*0.04` |
| C32 | **FINAL TAX** | `=C30+C31` |

---

## Worksheet 5: VALIDATION

### Input Validations (A1:C20)
| Cell | Check | Formula |
|------|-------|---------|
| C1 | Age Valid | `=IF(AND(INPUT_DATA.B2>=18,INPUT_DATA.B2<=100),"✓","✗")` |
| C2 | Salary Components ≥ 0 | `=IF(COUNTIF(INPUT_DATA.B10:B24,"<0")=0,"✓","✗")` |
| C3 | HRA City Valid | `=IF(INPUT_DATA.B14<>"","✓","✗")` |
| C4 | 80C Limit Check | `=IF(DEDUCTIONS.B9<=150000,"✓","Exceeds Limit")` |
| C5 | 80D Age-based Check | `=IF(DEDUCTIONS.B44<=IF(INPUT_DATA.B2>=60,50000,25000),"✓","Exceeds Limit")` |

### Calculation Cross-checks (A25:C35)
| Cell | Check | Formula |
|------|-------|---------|
| C25 | Tax Regime Applied | `=INPUT_DATA.B3` |
| C26 | Deductions Applied | `=IF(INPUT_DATA.B3="old","Yes","No")` |
| C27 | Age-based Exemption | `=IF(INPUT_DATA.B2>=60,"Applied","Not Applied")` |
| C28 | Capital Gains Rate | `="STCG: 20%, LTCG: 12.5%"` |

---

## Implementation Instructions

1. **Create 5 worksheets** with the names above
2. **Set up data validation** for dropdown fields
3. **Apply conditional formatting** for validation cells
4. **Use named ranges** for constants:
   - `Tax_Slabs_Old_Regular`: For regular taxpayer slabs
   - `Tax_Slabs_Old_Senior`: For senior citizen slabs
   - `Tax_Slabs_New`: For new regime slabs
   - `Deduction_Limits`: For various deduction limits

5. **Protection**: Protect calculation cells and allow input only in designated cells

6. **Testing**: Use the test cases provided in the main document

This structure provides a complete Excel-based tax calculator that mirrors the backend calculations exactly. 