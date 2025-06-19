# Field Mapping Matrix: Frontend TaxationData ↔ Backend CreateTaxationRecordRequest

## Overview
This document provides a comprehensive mapping between the frontend `TaxationData` interface and the backend `CreateTaxationRecordRequest` DTO, including all nested sub-classes and their field mappings.

## Main Object Mapping

| Frontend (TaxationData) | Backend (CreateTaxationRecordRequest) | Status | Notes |
|------------------------|--------------------------------------|---------|-------|
| `employee_id: string` | `employee_id: Optional[str]` | ✅ Direct | Both support employee_id |
| `tax_year: string` | `tax_year: str` | ✅ Direct | Same field name |
| `regime: TaxRegime` | `regime: str` | ✅ Direct | Same field name |
| `emp_age?: number` | `age: int` | ⚠️ Rename | Frontend: `emp_age`, Backend: `age` |
| `is_govt_employee?: boolean` | N/A | ❌ Missing | Backend doesn't have this field |
| `salary?: SalaryComponents` | `salary_income: Optional[SalaryIncomeDTO]` | ⚠️ Rename | **KEY MISMATCH** |
| `deductions?: Deductions` | `deductions: Optional[TaxDeductionsDTO]` | ⚠️ Structure | Different structure |
| `perquisites: Perquisites` | `perquisites: Optional[PerquisitesDTO]` | ⚠️ Structure | Different structure |
| `other_sources?: OtherSources` | `other_income: Optional[OtherIncomeDTO]` | ⚠️ Rename | Different field name |
| `capital_gains?: CapitalGains` | `capital_gains_income: Optional[CapitalGainsIncomeDTO]` | ⚠️ Rename | Different field name |
| `house_property?: HouseProperty` | `house_property_income: Optional[HousePropertyIncomeDTO]` | ⚠️ Rename | Different field name |
| `leave_encashment?: LeaveEncashment` | `retirement_benefits.leave_encashment` | ⚠️ Nested | Backend groups under retirement_benefits |
| `pension?: Pension` | `retirement_benefits.pension` | ⚠️ Nested | Backend groups under retirement_benefits |
| `voluntary_retirement?: VoluntaryRetirement` | `retirement_benefits.vrs` | ⚠️ Nested | Backend groups under retirement_benefits |
| `gratuity?: Gratuity` | `retirement_benefits.gratuity` | ⚠️ Nested | Backend groups under retirement_benefits |
| `retrenchment_compensation?: RetrenchmentCompensation` | `retirement_benefits.retrenchment_compensation` | ⚠️ Nested | Backend groups under retirement_benefits |

## 1. Salary Components Mapping

### Frontend: `SalaryComponents` → Backend: `SalaryIncomeDTO`

| Frontend Field | Backend Field | Status | Notes |
|---------------|---------------|---------|-------|
| `basic: number` | `basic_salary: Decimal` | ⚠️ Rename | Frontend: `basic`, Backend: `basic_salary` |
| `dearness_allowance: number` | `dearness_allowance: Decimal` | ✅ Direct | Same field name |
| `hra: number` | `hra_received: Decimal` | ⚠️ Rename | Frontend: `hra`, Backend: `hra_received` |
| `hra_percentage?: number` | N/A | ❌ Missing | Backend doesn't have this |
| `actual_rent_paid?: number` | `actual_rent_paid: Decimal` | ✅ Direct | Same field name |
| `special_allowance: number` | `special_allowance: Decimal` | ✅ Direct | Same field name |
| `bonus: number` | N/A | ❌ Missing | Backend doesn't have bonus in SalaryIncomeDTO |
| `commission?: number` | N/A | ❌ Missing | Backend doesn't have commission |
| `hra_city: string` | `hra_city_type: str` | ⚠️ Rename | Frontend: `hra_city`, Backend: `hra_city_type` |
| `transport_allowance: number` | `conveyance_allowance: Decimal` | ⚠️ Rename | Different field names |
| `fixed_medical_allowance: number` | `medical_allowance: Decimal` | ⚠️ Rename | Frontend: `fixed_medical_allowance`, Backend: `medical_allowance` |
| `lta_claimed: number` | `lta_received: Decimal` | ⚠️ Rename | Frontend: `lta_claimed`, Backend: `lta_received` |
| `any_other_allowance: number` | `other_allowances: Decimal` | ⚠️ Rename | Frontend: `any_other_allowance`, Backend: `other_allowances` |

### Missing in Backend SalaryIncomeDTO:
- `city_compensatory_allowance`
- `rural_allowance`
- `proctorship_allowance`
- `wardenship_allowance`
- `project_allowance`
- `deputation_allowance`
- `interim_relief`
- `tiffin_allowance`
- `overtime_allowance`
- `servant_allowance`
- `hills_high_altd_allowance`
- `border_remote_allowance`
- `transport_employee_allowance`
- `children_education_allowance`
- `hostel_allowance`
- `underground_mines_allowance`
- `govt_employee_entertainment_allowance`
- `govt_employees_outside_india_allowance`
- `supreme_high_court_judges_allowance`
- `judge_compensatory_allowance`
- `section_10_14_special_allowances`
- `travel_on_tour_allowance`
- `tour_daily_charge_allowance`
- `conveyance_in_performace_of_duties`
- `helper_in_performace_of_duties`
- `academic_research`
- `uniform_allowance`
- `any_other_allowance_exemption`

## 2. Deductions Mapping

### Frontend: `Deductions` → Backend: `TaxDeductionsDTO`

The backend has a completely different structure with nested DTOs:

| Frontend Field | Backend Field | Status | Notes |
|---------------|---------------|---------|-------|
| `section_80c_lic: number` | `section_80c.life_insurance_premium` | ⚠️ Nested | Backend groups under section_80c |
| `section_80c_epf: number` | `section_80c.epf_contribution` | ⚠️ Nested | Backend groups under section_80c |
| `section_80c_ssp: number` | `section_80c.sukanya_samriddhi` | ⚠️ Nested | Backend groups under section_80c |
| `section_80c_nsc: number` | `section_80c.nsc_investment` | ⚠️ Nested | Backend groups under section_80c |
| `section_80c_ulip: number` | `section_80c.ulip_premium` | ⚠️ Nested | Backend groups under section_80c |
| `section_80c_tsmf: number` | `section_80c.tax_saving_fd` | ⚠️ Nested | Backend groups under section_80c |
| `section_80c_tffte2c: number` | `section_80c.tuition_fees` | ⚠️ Nested | Backend groups under section_80c |
| `section_80c_paphl: number` | `section_80c.home_loan_principal` | ⚠️ Nested | Backend groups under section_80c |
| `section_80c_sdpphp: number` | `section_80c.ppf_contribution` | ⚠️ Nested | Backend groups under section_80c |
| `section_80c_tsfdsb: number` | `section_80c.elss_investment` | ⚠️ Nested | Backend groups under section_80c |
| `section_80c_scss: number` | `section_80c.senior_citizen_savings` | ⚠️ Nested | Backend groups under section_80c |
| `section_80c_others: number` | `section_80c.other_80c_investments` | ⚠️ Nested | Backend groups under section_80c |
| `section_80d_hisf: number` | `section_80d.self_family_premium` | ⚠️ Nested | Backend groups under section_80d |
| `section_80d_phcs: number` | `section_80d.preventive_health_checkup` | ⚠️ Nested | Backend groups under section_80d |
| `section_80d_hi_parent: number` | `section_80d.parent_premium` | ⚠️ Nested | Backend groups under section_80d |
| `section_80e_interest: number` | `section_80e.education_loan_interest` | ⚠️ Nested | Backend groups under section_80e |

### Backend has extensive Section 80G breakdown not in Frontend:
- `section_80g.pm_relief_fund`
- `section_80g.national_defence_fund`
- `section_80g.national_foundation_communal_harmony`
- And 20+ more specific donation categories

## 3. Perquisites Mapping

### Frontend: `Perquisites` → Backend: `PerquisitesDTO`

| Frontend Field | Backend Field | Status | Notes |
|---------------|---------------|---------|-------|
| `accommodation_type?: string` | `accommodation.accommodation_type` | ⚠️ Nested | Backend has detailed accommodation DTO |
| `accommodation_value?: number` | `accommodation.rent_paid_by_employer` | ⚠️ Nested | Different structure |
| `car_provided: boolean` | `car.car_use_type` | ⚠️ Different | Backend uses enum, frontend boolean |
| `car_cc: number` | `car.engine_capacity_cc` | ⚠️ Nested | Backend groups under car |
| `car_value: number` | `car.car_cost_to_employer` | ⚠️ Nested | Backend groups under car |
| `medical_reimbursement: number` | `medical_reimbursement.medical_reimbursement_amount` | ⚠️ Nested | Backend has detailed medical DTO |
| `lta_claimed: number` | `lta.lta_amount_claimed` | ⚠️ Nested | Backend groups under lta |
| `loan_amount: number` | `interest_free_loan.loan_amount` | ⚠️ Nested | Backend groups under interest_free_loan |
| `esop_value: number` | `esop.shares_exercised` | ⚠️ Different | Different calculation approach |

## 4. Other Income Sources Mapping

### Frontend: `OtherSources` → Backend: `OtherIncomeDTO`

| Frontend Field | Backend Field | Status | Notes |
|---------------|---------------|---------|-------|
| `interest_savings: number` | `interest_income.savings_account_interest` | ⚠️ Nested | Backend groups under interest_income |
| `interest_fd: number` | `interest_income.fixed_deposit_interest` | ⚠️ Nested | Backend groups under interest_income |
| `interest_rd: number` | `interest_income.recurring_deposit_interest` | ⚠️ Nested | Backend groups under interest_income |
| `other_interest: number` | `interest_income.other_bank_interest` | ⚠️ Nested | Backend groups under interest_income |
| `dividend_income: number` | `dividend_income: Decimal` | ✅ Direct | Same field name |
| `gifts: number` | `gifts_received: Decimal` | ⚠️ Rename | Frontend: `gifts`, Backend: `gifts_received` |
| `business_professional_income: number` | `business_professional_income: Decimal` | ✅ Direct | Same field name |
| `other_income: number` | `other_miscellaneous_income: Decimal` | ⚠️ Rename | Different field names |

## 5. Capital Gains Mapping

### Frontend: `CapitalGains` → Backend: `CapitalGainsIncomeDTO`

| Frontend Field | Backend Field | Status | Notes |
|---------------|---------------|---------|-------|
| `stcg_111a: number` | `stcg_111a_equity_stt: Decimal` | ⚠️ Rename | Backend more descriptive |
| `stcg_any_other_asset: number` | `stcg_other_assets: Decimal` | ⚠️ Rename | Different field names |
| `stcg_debt_mutual_fund: number` | N/A | ❌ Missing | Backend doesn't have this specific field |
| `ltcg_112a: number` | `ltcg_112a_equity_stt: Decimal` | ⚠️ Rename | Backend more descriptive |
| `ltcg_any_other_asset: number` | `ltcg_other_assets: Decimal` | ⚠️ Rename | Different field names |
| `ltcg_debt_mutual_fund: number` | `ltcg_debt_mf: Decimal` | ⚠️ Rename | Different field names |

## 6. House Property Mapping

### Frontend: `HouseProperty` → Backend: `HousePropertyIncomeDTO`

| Frontend Field | Backend Field | Status | Notes |
|---------------|---------------|---------|-------|
| `annual_rent: number` | `annual_rent_received: Decimal` | ⚠️ Rename | Backend more descriptive |
| `municipal_tax: number` | `municipal_taxes_paid: Decimal` | ⚠️ Rename | Backend more descriptive |
| `standard_deduction: number` | N/A | ❌ Missing | Backend calculates automatically |
| `interest_on_loan: number` | `home_loan_interest: Decimal` | ⚠️ Rename | Different field names |
| `net_income: number` | N/A | ❌ Missing | Backend calculates automatically |
| `property_address?: string` | N/A | ❌ Missing | Backend doesn't store address |
| `occupancy_status?: string` | `property_type: str` | ⚠️ Rename | Different field names |

## 7. Retirement Benefits Mapping

The frontend has separate interfaces while backend groups them under `RetirementBenefitsDTO`:

### Leave Encashment
| Frontend Field | Backend Field | Status | Notes |
|---------------|---------------|---------|-------|
| `leave_encashment_income_received: number` | `leave_encashment.leave_encashment_amount` | ⚠️ Rename | Different field names |
| `leave_encashment_exemption: number` | N/A | ❌ Missing | Backend calculates automatically |
| `leave_encashment_taxable: number` | N/A | ❌ Missing | Backend calculates automatically |

### Pension
| Frontend Field | Backend Field | Status | Notes |
|---------------|---------------|---------|-------|
| `pension_received: number` | `pension.regular_pension` | ⚠️ Rename | Different field names |
| `commuted_pension: number` | `pension.commuted_pension` | ✅ Direct | Same field name |
| `uncommuted_pension: number` | N/A | ❌ Missing | Backend calculates from regular_pension |

### Gratuity
| Frontend Field | Backend Field | Status | Notes |
|---------------|---------------|---------|-------|
| `gratuity_received: number` | `gratuity.gratuity_amount` | ⚠️ Rename | Different field names |
| `exemption_limit: number` | N/A | ❌ Missing | Backend calculates automatically |
| `taxable_amount: number` | N/A | ❌ Missing | Backend calculates automatically |

## Summary of Key Issues

### 🔴 Critical Mismatches
1. **Main Field Name**: `salary` vs `salary_income`
2. **Age Field**: `emp_age` vs `age`
3. **Deductions Structure**: Flat structure vs nested DTOs
4. **Perquisites Structure**: Flat structure vs nested DTOs
5. **Retirement Benefits**: Separate fields vs grouped DTO

### 🟡 Field Name Differences
- `basic` → `basic_salary`
- `hra` → `hra_received`
- `hra_city` → `hra_city_type`
- `transport_allowance` → `conveyance_allowance`
- `other_sources` → `other_income`
- `capital_gains` → `capital_gains_income`
- `house_property` → `house_property_income`

### 🟢 Missing Backend Fields
Many detailed allowances in frontend `SalaryComponents` are not present in backend `SalaryIncomeDTO`

### 📋 Recommendations
1. Create field mapping functions for data transformation
2. Consider backend DTO expansion to match frontend granularity
3. Implement validation for field name mismatches
4. Create adapter layer for structure differences
5. Document all calculated vs input fields 