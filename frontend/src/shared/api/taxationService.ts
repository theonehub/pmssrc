import { AxiosResponse } from 'axios';
import axiosInstance from '../utils/axios';
import {
  TaxationData,
  TaxRegime,
  FilingStatus,
  LeaveEncashment,
  HouseProperty,
  Pension,
  SalaryIncomeDTO,
  OtherIncomeDTO,
  TaxDeductionsDTO,
  CapitalGainsIncomeDTO,
} from '../types';

// Set up axios instance with auth token
const apiClient = () => {
  return axiosInstance;
};

// Get all taxation records with optional filters
export const getAllTaxation = async (
  taxYear: string | null = null,
  filingStatus: FilingStatus | null = null
): Promise<TaxationData[]> => {
  try {
    const url = '/api/v2/taxation/records';
    const params: Record<string, string> = {};

    if (taxYear) params.financial_year = taxYear;
    if (filingStatus) params.filing_status = filingStatus;

    const response: AxiosResponse<any> = await apiClient().get(url, {
      params,
    });
    // The backend returns { records: [...] }, so we need to extract the records array
    return response.data.records || [];
  } catch (error) {
    if (process.env.NODE_ENV === 'development') {
      // eslint-disable-next-line no-console
      console.error('Error fetching taxation data:', error);
    }
    throw error;
  }
};

// Get taxation data for a specific employee
export const getTaxationByEmpId = async (
  empId: string
): Promise<TaxationData> => {
  try {
    const response: AxiosResponse<TaxationData> = await apiClient().get(
      `/api/v2/taxation/records/employee/${empId}`
    );
    return response.data;
  } catch (error) {
    if (process.env.NODE_ENV === 'development') {
      // eslint-disable-next-line no-console
      console.error('Error fetching taxation data by employee_id:', error);
    }
    throw error;
  }
};

// Helper function to ensure numeric values
const ensureNumeric = (value: any): number => {
  if (value === null || value === undefined || value === '') return 0;
  const num = typeof value === 'string' ? parseFloat(value) : Number(value);
  return isNaN(num) ? 0 : num;
};

// Calculate comprehensive tax for an employee
export const calculateTax = async (
  empId: string,
  taxYear: string | null = null,
  regime: TaxRegime | null = null,
  taxationData?: TaxationData
): Promise<any> => {
  try {
    // If no taxation data provided, try to fetch existing record first
    let inputData: TaxationData;
    
    if (taxationData) {
      inputData = taxationData;
    } else {
      try {
        // Try to get existing taxation record for the employee
        inputData = await getTaxationByEmpId(empId);
      } catch (error) {
        // If no existing record, create minimal input with default values
        inputData = {
          employee_id: empId,
          tax_year: taxYear || '2024-25',
          regime: regime || 'new',
          age: 30, // Default age - should be provided by caller
          salary_income: createDefaultSalaryComponents(),
          other_income: createDefaultOtherSources(),
          capital_gains_income: createDefaultCapitalGains(),
          house_property_income: {
            annual_rent: 0,
            municipal_tax: 0,
            standard_deduction: 0,
            interest_on_loan: 0,
            net_income: 0
          },
          deductions: createDefaultDeductions(),
          retirement_benefits: {
            leave_encashment: {
              leave_encashment_income_received: 0,
              leave_encashment_exemption: 0,
              leave_encashment_taxable: 0
            }
          },
          perquisites: {
            other_perquisites: {
              total_perquisites: 0
            }
          }
        };
      }
    }

    // Override tax year and regime if provided
    if (taxYear) inputData.tax_year = taxYear;
    if (regime) inputData.regime = regime;
    
    // Validate required fields
    if (!inputData.tax_year) {
      throw new Error('Tax year is required for tax calculation');
    }
    if (!inputData.regime) {
      throw new Error('Tax regime is required for tax calculation');
    }
    if (!inputData.age || inputData.age < 18) {
      inputData.age = 30; // Set default age if not provided or invalid
    }

    // Transform frontend data to backend ComprehensiveTaxInputDTO format
    const comprehensiveInput = {
      tax_year: inputData.tax_year,
      regime_type: inputData.regime,
      age: inputData.age || 30, // Ensure age is provided
      
      // Salary income - transform to backend format
      salary_income: {
        basic_salary: ensureNumeric(inputData.salary_income.basic_salary),
        dearness_allowance: ensureNumeric(inputData.salary_income.dearness_allowance),
        hra_received: ensureNumeric(inputData.salary_income.hra_received),
        hra_city_type: inputData.salary_income.hra_city_type || 'non_metro',
        actual_rent_paid: ensureNumeric(inputData.salary_income.actual_rent_paid),
        bonus: ensureNumeric(inputData.salary_income.bonus),
        commission: ensureNumeric(inputData.salary_income.commission),
        special_allowance: ensureNumeric(inputData.salary_income.special_allowance),
        conveyance_allowance: ensureNumeric(inputData.salary_income.conveyance_allowance),
        medical_allowance: ensureNumeric(inputData.salary_income.medical_allowance),
        other_allowances: ensureNumeric(inputData.salary_income.other_allowances),
        
        // Additional detailed allowances
        city_compensatory_allowance: ensureNumeric(inputData.salary_income.city_compensatory_allowance),
        rural_allowance: ensureNumeric(inputData.salary_income.rural_allowance),
        proctorship_allowance: ensureNumeric(inputData.salary_income.proctorship_allowance),
        wardenship_allowance: ensureNumeric(inputData.salary_income.wardenship_allowance),
        project_allowance: ensureNumeric(inputData.salary_income.project_allowance),
        deputation_allowance: ensureNumeric(inputData.salary_income.deputation_allowance),
        interim_relief: ensureNumeric(inputData.salary_income.interim_relief),
        tiffin_allowance: ensureNumeric(inputData.salary_income.tiffin_allowance),
        overtime_allowance: ensureNumeric(inputData.salary_income.overtime_allowance),
        servant_allowance: ensureNumeric(inputData.salary_income.servant_allowance),
        hills_high_altd_allowance: ensureNumeric(inputData.salary_income.hills_high_altd_allowance),
        hills_high_altd_exemption_limit: ensureNumeric(inputData.salary_income.hills_high_altd_exemption_limit),
        border_remote_allowance: ensureNumeric(inputData.salary_income.border_remote_allowance),
        border_remote_exemption_limit: ensureNumeric(inputData.salary_income.border_remote_exemption_limit),
        transport_employee_allowance: ensureNumeric(inputData.salary_income.transport_employee_allowance),
        children_education_allowance: ensureNumeric(inputData.salary_income.children_education_allowance),
        children_education_count: ensureNumeric(inputData.salary_income.children_education_count),
        children_education_months: ensureNumeric(inputData.salary_income.children_education_months),
        hostel_allowance: ensureNumeric(inputData.salary_income.hostel_allowance),
        hostel_count: ensureNumeric(inputData.salary_income.hostel_count),
        hostel_months: ensureNumeric(inputData.salary_income.hostel_months),
        transport_months: ensureNumeric(inputData.salary_income.transport_months),
        underground_mines_allowance: ensureNumeric(inputData.salary_income.underground_mines_allowance),
        underground_mines_months: ensureNumeric(inputData.salary_income.underground_mines_months),
        govt_employee_entertainment_allowance: ensureNumeric(inputData.salary_income.govt_employee_entertainment_allowance),
        govt_employees_outside_india_allowance: ensureNumeric(inputData.salary_income.govt_employees_outside_india_allowance),
        supreme_high_court_judges_allowance: ensureNumeric(inputData.salary_income.supreme_high_court_judges_allowance),
        judge_compensatory_allowance: ensureNumeric(inputData.salary_income.judge_compensatory_allowance),
        section_10_14_special_allowances: ensureNumeric(inputData.salary_income.section_10_14_special_allowances),
        travel_on_tour_allowance: ensureNumeric(inputData.salary_income.travel_on_tour_allowance),
        tour_daily_charge_allowance: ensureNumeric(inputData.salary_income.tour_daily_charge_allowance),
        conveyance_in_performace_of_duties: ensureNumeric(inputData.salary_income.conveyance_in_performace_of_duties),
        helper_in_performace_of_duties: ensureNumeric(inputData.salary_income.helper_in_performace_of_duties),
        academic_research: ensureNumeric(inputData.salary_income.academic_research),
        uniform_allowance: ensureNumeric(inputData.salary_income.uniform_allowance),
        any_other_allowance_exemption: ensureNumeric(inputData.salary_income.any_other_allowance_exemption)
      },
      
      // Other income sources
      other_income: inputData.other_income ? {
        interest_income: {
          savings_account_interest: ensureNumeric(inputData.other_income.interest_income?.savings_account_interest),
          fixed_deposit_interest: ensureNumeric(inputData.other_income.interest_income?.fixed_deposit_interest),
          recurring_deposit_interest: ensureNumeric(inputData.other_income.interest_income?.recurring_deposit_interest),
          post_office_interest: ensureNumeric(inputData.other_income.interest_income?.post_office_interest),
          age: inputData.age
        },
        dividend_income: ensureNumeric(inputData.other_income.dividend_income),
        gifts_received: ensureNumeric(inputData.other_income.gifts_received),
        business_professional_income: ensureNumeric(inputData.other_income.business_professional_income),
        other_miscellaneous_income: ensureNumeric(inputData.other_income.other_miscellaneous_income)
      } : null,
      
      // Capital gains income
      capital_gains_income: inputData.capital_gains_income ? {
        stcg_111a_equity_stt: inputData.capital_gains_income.stcg_111a_equity_stt || 0,
        stcg_other_assets: inputData.capital_gains_income.stcg_other_assets || 0,
        stcg_debt_mf: inputData.capital_gains_income.stcg_debt_mf || 0,
        ltcg_112a_equity_stt: inputData.capital_gains_income.ltcg_112a_equity_stt || 0,
        ltcg_other_assets: inputData.capital_gains_income.ltcg_other_assets || 0,
        ltcg_debt_mf: inputData.capital_gains_income.ltcg_debt_mf || 0
      } : null,
      
      // House property income
      house_property_income: inputData.house_property_income ? {
        property_type: 'Self-Occupied',
        annual_rent_received: inputData.house_property_income.annual_rent || 0,
        municipal_taxes_paid: inputData.house_property_income.municipal_tax || 0,
        home_loan_interest: inputData.house_property_income.interest_on_loan || 0,
        pre_construction_interest: inputData.house_property_income.pre_construction_loan_interest || 0,

        
      } : null,
      
      // Retirement benefits
      retirement_benefits: inputData.retirement_benefits ? {
        leave_encashment: inputData.retirement_benefits.leave_encashment ? {
          leave_encashment_amount: inputData.retirement_benefits.leave_encashment.leave_encashment_income_received || 0,
          average_monthly_salary: 0,
          leave_days_encashed: 0,
          is_govt_employee: inputData.is_govt_employee || false,
          during_employment: inputData.retirement_benefits.leave_encashment.during_employment || false
        } : null,
        gratuity: inputData.retirement_benefits.gratuity ? {
          gratuity_amount: inputData.retirement_benefits.gratuity.gratuity_received || 0,
          monthly_salary: 0,
          service_years: 0,
          is_govt_employee: inputData.is_govt_employee || false
        } : null,
        vrs: inputData.retirement_benefits.vrs ? {
          vrs_amount: inputData.retirement_benefits.vrs.compensation_received || 0,
          monthly_salary: 0,
          age: inputData.age,
          service_years: 0
        } : null,
        pension: inputData.retirement_benefits.pension ? {
          regular_pension: inputData.retirement_benefits.pension.pension_received || 0,
          commuted_pension: inputData.retirement_benefits.pension.commuted_pension || 0,
          total_pension: inputData.retirement_benefits.pension.uncommuted_pension || 0,
          is_govt_employee: inputData.is_govt_employee || false,
          gratuity_received: false
        } : null
      } : null,
      
      // Tax deductions
      deductions: inputData.deductions ? {
        section_80c: {
          life_insurance_premium: inputData.deductions.section_80c?.life_insurance_premium || 0,
          epf_contribution: inputData.deductions.section_80c?.epf_contribution || 0,
          ppf_contribution: 0,
          nsc_investment: inputData.deductions.section_80c?.nsc_investment || 0,
          tax_saving_fd: inputData.deductions.section_80c?.tax_saver_fixed_deposit_5_years_bank || 0,
          elss_investment: inputData.deductions.section_80c?.tax_saver_mutual_fund || 0,
          home_loan_principal: inputData.deductions.section_80c?.principal_amount_paid_home_loan || 0,
          tuition_fees: inputData.deductions.section_80c?.tuition_fees_for_two_children || 0,
          ulip_premium: inputData.deductions.section_80c?.ulip_investment || 0,
          sukanya_samriddhi: inputData.deductions.section_80c?.sukanya_deposit_plan_for_girl_child || 0,
          stamp_duty_property: 0,
          senior_citizen_savings: inputData.deductions.section_80c?.senior_citizen_savings_scheme || 0,
          other_80c_investments: inputData.deductions.section_80c?.others || 0
        },
        section_80d: {
          self_family_premium: inputData.deductions.section_80d?.self_family_premium || 0,
          parent_premium: inputData.deductions.section_80d?.parent_premium || 0,
          preventive_health_checkup: inputData.deductions.section_80d?.preventive_health_checkup_self || 0,
          employee_age: inputData.age,
          parent_age: 60
        },
        section_80g: {
          pm_relief_fund: 0,
          national_defence_fund: 0,
          other_100_percent_wo_limit: inputData.deductions.section_80g?.donation_100_percent_without_limit || 0,
          other_50_percent_wo_limit: inputData.deductions.section_80g?.donation_50_percent_without_limit || 0,
          other_100_percent_w_limit: inputData.deductions.section_80g?.donation_100_percent_with_limit || 0,
          other_50_percent_w_limit: inputData.deductions.section_80g?.donation_50_percent_with_limit || 0
        },
        section_80e: {
          education_loan_interest: inputData.deductions.section_80e?.education_loan_interest || 0,
          relation: 'Self'
        },
        section_80tta_ttb: {
          savings_interest: inputData.other_income?.interest_income?.savings_account_interest || 0,
          fd_interest: inputData.other_income?.interest_income?.fixed_deposit_interest || 0,
          rd_interest: inputData.other_income?.interest_income?.recurring_deposit_interest || 0,
          post_office_interest: inputData.other_income?.interest_income?.post_office_interest || 0,
          age: inputData.age
        }
      } : null
    };

    // Debug: Log the input data being sent
    console.log('Sending comprehensive tax calculation request:', JSON.stringify(comprehensiveInput, null, 2));
    
    // Call the backend comprehensive tax calculation endpoint
    //const response = await apiClient().post('/api/v2/taxation/calculate-comprehensive', comprehensiveInput);
    const response = await apiClient().post(`/api/v2/taxation/records/employee/${empId}/calculate-comprehensive`, comprehensiveInput);
    
    // Transform backend response to expected frontend format
    const backendResult = response.data;
    
    return {
      // Map tax_liability from backend response
      tax_liability: backendResult.tax_liability,
      total_tax_liability: backendResult.total_tax_liability || backendResult.tax_liability,
      taxable_income: backendResult.taxable_income,
      total_income: backendResult.total_income,
      effective_tax_rate: backendResult.effective_tax_rate,
      regime_used: backendResult.regime_used,
      gross_income: backendResult.gross_income,
      total_exemptions: backendResult.total_exemptions,
      total_deductions: backendResult.total_deductions,
      tax_before_rebate: backendResult.tax_before_rebate,
      rebate_87a: backendResult.rebate_87a,
      tax_after_rebate: backendResult.tax_after_rebate,
      surcharge: backendResult.surcharge,
      cess: backendResult.cess,
      
      // Include tax_breakdown from backend
      tax_breakdown: backendResult.tax_breakdown,
      
      // Enhanced details
      employment_periods: backendResult.employment_periods,
      total_employment_days: backendResult.total_employment_days,
      is_mid_year_scenario: backendResult.is_mid_year_scenario,
      period_wise_income: backendResult.period_wise_income,
      surcharge_breakdown: backendResult.surcharge_breakdown,
      full_year_projection: backendResult.full_year_projection,
      mid_year_impact: backendResult.mid_year_impact,
      optimization_suggestions: backendResult.optimization_suggestions,
      taxpayer_age: backendResult.taxpayer_age,
      calculation_breakdown: backendResult.calculation_breakdown,
      regime_comparison: backendResult.regime_comparison,
      
      // Monthly payroll projection
      monthly_payroll: backendResult.monthly_payroll,
      
      message: 'Tax calculation completed successfully'
    };
    
  } catch (error) {
    if (process.env.NODE_ENV === 'development') {
      // eslint-disable-next-line no-console
      console.error('Error calculating comprehensive tax:', error);
    }
    
    // Re-throw with more context
    if (error instanceof Error) {
      throw new Error(`Tax calculation failed: ${error.message}`);
    }
    throw error;
  }
};

// Create default salary components
export const createDefaultSalaryComponents = (): SalaryIncomeDTO => ({
  basic_salary: 0,
  dearness_allowance: 0,
  hra_received: 0,
  hra_city_type: 'non_metro',
  actual_rent_paid: 0,
  bonus: 0,
  commission: 0,
  special_allowance: 0,
  conveyance_allowance: 0,
  medical_allowance: 0,
  other_allowances: 0,
  city_compensatory_allowance: 0,
  rural_allowance: 0,
  proctorship_allowance: 0,
  wardenship_allowance: 0,
  project_allowance: 0,
  deputation_allowance: 0,
  overtime_allowance: 0,
  interim_relief: 0,
  tiffin_allowance: 0,
  servant_allowance: 0,
  hills_high_altd_allowance: 0,
  hills_high_altd_exemption_limit: 0,
  border_remote_allowance: 0,
  border_remote_exemption_limit: 0,
  transport_employee_allowance: 0,
  children_education_allowance: 0,
  children_education_count: 0,
  children_education_months: 0,
  hostel_allowance: 0,
  hostel_count: 0,
  hostel_months: 0,
  transport_months: 0,
  underground_mines_allowance: 0,
  underground_mines_months: 0,
  govt_employee_entertainment_allowance: 0,
  govt_employees_outside_india_allowance: 0,
  supreme_high_court_judges_allowance: 0,
  judge_compensatory_allowance: 0,
  section_10_14_special_allowances: 0,
  any_other_allowance_exemption: 0,
  travel_on_tour_allowance: 0,
  tour_daily_charge_allowance: 0,
  conveyance_in_performace_of_duties: 0,
  helper_in_performace_of_duties: 0,
  academic_research: 0,
  uniform_allowance: 0,
});

// Create default other sources
export const createDefaultOtherSources = (): OtherIncomeDTO => ({
  interest_income: {
    savings_account_interest: 0,
    fixed_deposit_interest: 0,
    recurring_deposit_interest: 0,
    post_office_interest: 0,
  },
  dividend_income: 0,
  gifts_received: 0,
  business_professional_income: 0,
  other_miscellaneous_income: 0,
});

// Create default capital gains
export const createDefaultCapitalGains = (): CapitalGainsIncomeDTO => ({
  stcg_111a_equity_stt: 0,
  stcg_other_assets: 0,
  stcg_debt_mf: 0,
  ltcg_112a_equity_stt: 0,
  ltcg_other_assets: 0,
  ltcg_debt_mf: 0,
});

// Create default leave encashment
export const createDefaultLeaveEncashment = (): LeaveEncashment => ({
  leave_encashment_income_received: 0,
  leave_encashment_exemption: 0,
  leave_encashment_taxable: 0,
  leave_encashed: 0,
  is_deceased: false,
  during_employment: false,
});

// Create default house property
export const createDefaultHouseProperty = (): HouseProperty => ({
  property_type: 'Self-Occupied',
  annual_rent: 0,
  municipal_tax: 0,
  standard_deduction: 0,
  interest_on_loan: 0,
  net_income: 0,
  property_address: '',
  occupancy_status: '',
  rent_income: 0,
  property_tax: 0,
  interest_on_home_loan: 0,
  pre_construction_loan_interest: 0,
});

// Create default pension
export const createDefaultPension = (): Pension => ({
  pension_received: 0,
  commuted_pension: 0,
  uncommuted_pension: 0,
  total_pension_income: 0,
  computed_pension_percentage: 0,
  uncomputed_pension_frequency: '',
  uncomputed_pension_amount: 0,
});

// Create default deductions
export const createDefaultDeductions = (): TaxDeductionsDTO => ({
  section_80c: {
    life_insurance_premium: 0,
    epf_contribution: 0,
    ssp_contribution: 0,
    nsc_investment: 0,
    ulip_investment: 0,
    tax_saver_mutual_fund: 0,
    tuition_fees_for_two_children: 0,
    principal_amount_paid_home_loan: 0,
    sukanya_deposit_plan_for_girl_child: 0,
    tax_saver_fixed_deposit_5_years_bank: 0,
    senior_citizen_savings_scheme: 0,
    others: 0,
  },
  section_80ccc: {
    pension_plan_insurance_company: 0,
  },
  section_80ccd: {
    nps_contribution_10_percent: 0,
    additional_nps_50k: 0,
    employer_nps_contribution: 0,
  },
  section_80d: {
    self_family_premium: 0,
    preventive_health_checkup_self: 0,
    parent_premium: 0,
  },
  section_80dd: {
    amount: 0,
    relation: '',
    disability_percentage: '',
  },
  section_80ddb: {
    amount: 0,
    relation: '',
  },
  section_80e: {
    education_loan_interest: 0,
  },
  section_80eeb: {
    amount: 0,
  },
  section_80g: {
    donation_100_percent_without_limit: 0,
    donation_50_percent_without_limit: 0,
    donation_100_percent_with_limit: 0,
    donation_50_percent_with_limit: 0,
  },
  section_80ggc: {
    amount: 0,
  },
  section_80u: {
    amount: 0,
    disability_percentage: '',
  },
});

// Transform flat perquisites structure to nested DTO structure
const transformPerquisitesToDTO = (perquisites: any, salaryData?: any) => {
  if (!perquisites) return null;
  
  return {
    // Accommodation perquisite
    accommodation: {
      accommodation_type: perquisites.accommodation_provided || 'Employer-Owned',
      city_population: perquisites.accommodation_city_population === 'Exceeding 40 lakhs in 2011 Census' 
        ? 'Above 40 lakhs' 
        : perquisites.accommodation_city_population === 'Between 15-40 lakhs in 2011 Census'
        ? 'Between 15-40 lakhs'
        : 'Below 15 lakhs',
      license_fees: perquisites.accommodation_govt_lic_fees || 0,
      employee_rent_payment: perquisites.accommodation_rent || 0,
      basic_salary: salaryData?.basic_salary || 0,
      dearness_allowance: salaryData?.dearness_allowance || 0,
      rent_paid_by_employer: 0,
      hotel_charges: 0,
      stay_days: 0,
      furniture_cost: perquisites.furniture_actual_cost || 0,
      furniture_employee_payment: 0,
      is_furniture_owned_by_employer: perquisites.is_furniture_owned || false
    },
    
    // Car perquisite
    car: {
      car_use_type: perquisites.car_use || 'Personal',
      engine_capacity_cc: 1600, // Default value
      months_used: perquisites.month_counts || 0,
      car_cost_to_employer: perquisites.car_cost_to_employer || 0,
      other_vehicle_cost: perquisites.other_vehicle_cost_to_employer || 0,
      has_expense_reimbursement: false,
      driver_provided: false
    },
    
    // Medical reimbursement
    medical_reimbursement: {
      medical_reimbursement_amount: perquisites.medical_reimbursement_by_employer || 0,
      is_overseas_treatment: !perquisites.is_treated_in_India
    },
    
    // LTA perquisite
    lta: {
      lta_amount_claimed: perquisites.lta_amount_claimed || 0,
      lta_claimed_count: perquisites.lta_claimed_count || 0,
      public_transport_cost: perquisites.public_transport_travel_amount_for_same_distance || 0
    },
    
    // Interest free loan
    interest_free_loan: {
      loan_amount: perquisites.loan_amount || 0,
      outstanding_amount: perquisites.loan_amount || 0,
      company_interest_rate: perquisites.loan_interest_rate_company || 0,
      sbi_interest_rate: perquisites.loan_interest_rate_sbi || 0,
      loan_months: perquisites.loan_month_count || 0
    },
    
    // ESOP perquisite
    esop: {
      shares_exercised: perquisites.number_of_esop_shares_exercised || 0,
      exercise_price: perquisites.esop_exercise_price_per_share || 0,
      allotment_price: perquisites.esop_allotment_price_per_share || 0
    },
    
    // Utilities perquisite
    utilities: {
      gas_paid_by_employer: perquisites.gas_amount_paid_by_employer || 0,
      electricity_paid_by_employer: perquisites.electricity_amount_paid_by_employer || 0,
      water_paid_by_employer: perquisites.water_amount_paid_by_employer || 0,
      gas_paid_by_employee: perquisites.gas_amount_paid_by_employee || 0,
      electricity_paid_by_employee: perquisites.electricity_amount_paid_by_employee || 0,
      water_paid_by_employee: perquisites.water_amount_paid_by_employee || 0,
      is_gas_manufactured_by_employer: perquisites.is_gas_manufactured_by_employer || false,
      is_electricity_manufactured_by_employer: perquisites.is_electricity_manufactured_by_employer || false,
      is_water_manufactured_by_employer: perquisites.is_water_manufactured_by_employer || false
    },
    
    // Free education
    free_education: {
      monthly_expenses_child1: perquisites.employer_monthly_expenses_1st_child || 0,
      monthly_expenses_child2: perquisites.employer_monthly_expenses_2nd_child || 0,
      months_child1: perquisites.monthly_count_1st_child || 0,
      months_child2: perquisites.monthly_count_2nd_child || 0,
      employer_maintained_1st_child: perquisites.employer_maintained_1st_child || false,
      employer_maintained_2nd_child: perquisites.employer_maintained_2nd_child || false
    },
    
    // Movable asset usage
    movable_asset_usage: {
      asset_type: perquisites.mat_type || 'Electronics',
      asset_value: perquisites.mau_value_to_employer || 0,
      employee_payment: perquisites.mau_value_to_employee || 0,
      is_employer_owned: perquisites.mau_ownership === 'Employer-Owned'
    },
    
    // Movable asset transfer
    movable_asset_transfer: {
      asset_type: perquisites.mat_type || 'Electronics',
      asset_cost: perquisites.mat_value_to_employer || 0,
      years_of_use: perquisites.mat_number_of_completed_years_of_use || 0,
      employee_payment: perquisites.mat_value_to_employee || 0
    },
    
    // Lunch refreshment
    lunch_refreshment: {
      employer_cost: perquisites.lunch_amount_paid_by_employer || 0,
      employee_payment: perquisites.lunch_amount_paid_by_employee || 0,
      meal_days_per_year: 250 // Default working days
    },
    
    // Gift voucher
    gift_voucher: {
      gift_voucher_amount: perquisites.gift_vouchers_amount_paid_by_employer || 0
    },
    
    // Monetary benefits
    monetary_benefits: {
      monetary_amount_paid_by_employer: perquisites.monetary_amount_paid_by_employer || 0,
      expenditure_for_official_purpose: perquisites.expenditure_for_offical_purpose || 0,
      amount_paid_by_employee: perquisites.monetary_benefits_amount_paid_by_employee || 0
    },
    
    // Club expenses
    club_expenses: {
      club_expenses_paid_by_employer: perquisites.club_expenses_amount_paid_by_employer || 0,
      club_expenses_paid_by_employee: perquisites.club_expenses_amount_paid_by_employee || 0,
      club_expenses_for_official_purpose: perquisites.club_expenses_amount_paid_for_offical_purpose || 0
    },
    
    // Domestic help
    domestic_help: {
      domestic_help_paid_by_employer: perquisites.domestic_help_amount_paid_by_employer || 0,
      domestic_help_paid_by_employee: perquisites.domestic_help_amount_paid_by_employee || 0
    }
  };
};

// Submit or update taxation data
export const saveTaxationData = async (taxationData: TaxationData): Promise<any> => {
  try {
    // Transform the data to match backend DTO structure
    const transformedData = {
      tax_year: taxationData.tax_year,
      regime_type: taxationData.regime,
      age: taxationData.age,
      is_govt_employee: taxationData.is_govt_employee,
      employee_id: taxationData.employee_id,
      
      // Salary income
      salary_income: taxationData.salary_income,
      
      // Periodic salary income
      periodic_salary_income: null,
      
      // Transform perquisites to nested structure
      perquisites: transformPerquisitesToDTO(taxationData.perquisites, taxationData.salary_income),
      
      // House property income
      house_property_income: taxationData.house_property_income,
      
      // Capital gains income
      capital_gains_income: taxationData.capital_gains_income,
      
      // Retirement benefits
      retirement_benefits: taxationData.retirement_benefits,
      
      // Other income
      other_income: taxationData.other_income,
      
      // Tax deductions
      deductions: taxationData.deductions
    };

    console.log('Sending taxation data:', transformedData);
    
    const response = await apiClient().post('/api/v2/taxation/records', transformedData);
    return response.data;
  } catch (error) {
    console.error('Error saving taxation data:', error);
    throw error;
  }
};

// Update tax payment
export const updateTaxPayment = async (
  empId: string,
  amountPaid: number
): Promise<any> => {
  try {
    // Note: This endpoint doesn't exist in backend, using mock for now
    // TODO: Implement proper tax payment update endpoint in backend
    
    // Use parameters to avoid TypeScript warnings
    console.log(`Updating tax payment for employee ${empId}, amount: ${amountPaid}`);
    
    const mockData = { success: true, message: 'Payment updated successfully' };
    return mockData;
  } catch (error) {
    if (process.env.NODE_ENV === 'development') {
      // eslint-disable-next-line no-console
      console.error('Error updating tax payment:', error);
    }
    throw error;
  }
};

// Update filing status
export const updateFilingStatus = async (
  empId: string,
  status: FilingStatus
): Promise<any> => {
  try {
    // Note: This endpoint doesn't exist in backend, using mock for now
    // TODO: Implement proper filing status update endpoint in backend
    
    // Use parameters to avoid TypeScript warnings
    console.log(`Updating filing status for employee ${empId}, status: ${status}`);
    
    const mockData = { success: true, message: 'Filing status updated successfully' };
    return mockData;
  } catch (error) {
    if (process.env.NODE_ENV === 'development') {
      // eslint-disable-next-line no-console
      console.error('Error updating filing status:', error);
    }
    throw error;
  }
};

// Compute VRS value for an employee
export const computeVrsValue = async (
  empId: string,
  vrsData: any
): Promise<any> => {
  try {
    // Note: This endpoint doesn't exist in backend, using mock for now
    // TODO: Implement proper VRS computation endpoint in backend
    
    // Use parameters to avoid TypeScript warnings
    console.log(`Computing VRS value for employee ${empId}, data:`, vrsData);
    
    const mockData = { vrs_value: 500000, message: 'VRS value computed successfully' };
    return mockData;
  } catch (error) {
    if (process.env.NODE_ENV === 'development') {
      // eslint-disable-next-line no-console
      console.error('Error computing VRS value:', error);
    }
    throw error;
  }
};

// Get current user's taxation data
export const getMyTaxation = async (): Promise<TaxationData> => {
  try {
    // Note: This endpoint doesn't exist in backend, using records endpoint with current user
    // TODO: Implement proper my-taxation endpoint in backend or use current user's employee ID
    const response: AxiosResponse<TaxationData> =
      await apiClient().get(`/api/v2/taxation/records/employee/current`);
    return response.data;
  } catch (error) {
    if (process.env.NODE_ENV === 'development') {
      // eslint-disable-next-line no-console
      console.error('Error fetching my taxation data:', error);
    }
    throw error;
  }
};

export const deleteTaxation = async (empId: string): Promise<void> => {
  try {
    await apiClient().delete(`/taxation/employee/${empId}`);
  } catch (error) {
    if (process.env.NODE_ENV === 'development') {
      // eslint-disable-next-line no-console
      console.error('Error deleting taxation data:', error);
    }
    throw error;
  }
};
