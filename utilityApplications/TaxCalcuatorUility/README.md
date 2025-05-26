# Excel Tax Calculator

This is a comprehensive Excel-based Income Tax Calculator for Indian taxpayers, generated from the detailed structure specification.

## Files Created

1. **Tax_Calculator.xlsx** - The main Excel file with all worksheets and formulas
2. **create_tax_calculator.py** - Python script used to generate the Excel file
3. **requirements.txt** - Python dependencies needed to run the generator script

## Excel File Structure

The Excel file contains 5 worksheets:

### 1. INPUT_DATA
- **Basic Information**: Employee details, age, tax regime selection, employment dates
- **Salary Components**: Basic salary, HRA, allowances, bonuses, etc.
- **Other Income Sources**: Interest income, dividends, business income
- **House Property**: Property details, rent income, loan interest
- **Capital Gains**: STCG and LTCG from various sources
- **Leave Encashment & Others**: VRS, pension, gratuity details

### 2. DEDUCTIONS
- **Section 80C**: LIC, EPF, PPF, ELSS, home loan principal, etc.
- **Section 80CCD**: NPS contributions and employer contributions
- **Section 80D**: Health insurance premiums for self, family, and parents
- **Other Deductions**: 80DD, 80DDB, 80E, 80U, 80G sections

### 3. CALCULATIONS
- **Salary Income**: HRA exemptions, standard deduction calculations
- **Other Sources**: Interest exemptions, taxable interest
- **House Property**: Annual value, standard deduction, interest deduction
- **Capital Gains**: Tax calculations for different types of gains
- **Income Summary**: Gross income, total deductions, net taxable income

### 4. TAX_CALCULATION
- **Tax Slabs**: Age-based and regime-based tax calculations
- **Final Tax**: Rebate under 87A, surcharge, health & education cess
- **Result**: Final tax liability

### 5. VALIDATION
- **Input Validations**: Checks for valid age, positive values, required fields
- **Cross-checks**: Regime application, deduction limits, exemption verifications

## How to Use

1. **Open the Excel file**: Tax_Calculator.xlsx
2. **Start with INPUT_DATA sheet**:
   - Fill in basic information (Employee ID, Age, Tax Regime)
   - Enter salary components
   - Add other income sources if applicable
   - Fill house property details if you own property
   - Enter capital gains if any
   - Add leave encashment or other income details

3. **Move to DEDUCTIONS sheet**:
   - Enter investments under Section 80C
   - Add NPS contributions under Section 80CCD
   - Fill health insurance details under Section 80D
   - Enter other applicable deductions

4. **Check CALCULATIONS sheet**:
   - Review computed salary income after exemptions
   - Verify other income calculations
   - Check house property income computation
   - Review capital gains calculations
   - See total taxable income

5. **Review TAX_CALCULATION sheet**:
   - See age and regime-based tax computation
   - Check final tax after rebates and cess

6. **Validate using VALIDATION sheet**:
   - Ensure all inputs are valid
   - Check for any limit exceedances
   - Verify calculation cross-checks

## Key Features

- **Dual Regime Support**: Supports both old and new tax regimes
- **Age-based Calculations**: Different exemptions for regular, senior, and super senior citizens
- **Comprehensive Deductions**: All major deduction sections covered
- **Capital Gains**: STCG and LTCG calculations with proper tax rates
- **Data Validation**: Dropdown menus for critical fields
- **Color Coding**: 
  - Blue headers for sections
  - Light blue for input cells
  - Yellow for formula cells
- **Auto-calculations**: All formulas are pre-built and linked across sheets
- **Validation Checks**: Built-in checks for common errors

## Important Notes

1. **Tax Regime**: Choose "old" or "new" regime in INPUT_DATA sheet. This affects deduction applicability.
2. **Age Categories**: 
   - Regular: Below 60 years
   - Senior: 60-79 years
   - Super Senior: 80+ years
3. **HRA City**: Select appropriate city for HRA exemption calculation
4. **Property Status**: Choose "Self-Occupied" or "Let-Out" for house property
5. **Government Employee**: Select TRUE/FALSE as it affects NPS deduction limits

## Regenerating the Excel File

If you need to modify the structure or formulas:

1. Install Python and required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the generator script:
   ```bash
   python create_tax_calculator.py
   ```

This will create a new Tax_Calculator.xlsx file with the updated structure.

## Tax Year

The calculator is designed for **FY 2024-25 (AY 2025-26)** tax rates and limits. Update the limits in the Python script if needed for future years. 