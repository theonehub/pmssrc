import { AxiosInstance, AxiosResponse } from 'axios';
import axiosInstance from '../utils/axios';
import {
  TaxationData,
  TaxRegime,
  FilingStatus,
  SalaryComponents,
  Perquisites,
  OtherSources,
  CapitalGains,
  LeaveEncashment,
  HouseProperty,
  Pension,
  Deductions,
} from '../types';

// Set up axios instance with auth token
const apiClient = (): AxiosInstance => {
  return axiosInstance;
};

// Get all taxation records with optional filters
export const getAllTaxation = async (
  taxYear: string | null = null,
  filingStatus: FilingStatus | null = null
): Promise<TaxationData[]> => {
  try {
    const url = '/api/v2/taxation/all-taxation';
    const params: Record<string, string> = {};

    if (taxYear) params.tax_year = taxYear;
    if (filingStatus) params.filing_status = filingStatus;

    const response: AxiosResponse<TaxationData[]> = await apiClient().get(url, {
      params,
    });
    return response.data;
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
      `/api/v2/taxation/taxation/${empId}`
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

// Calculate tax for an employee
export const calculateTax = async (
  empId: string,
  taxYear: string | null = null,
  regime: TaxRegime | null = null
): Promise<any> => {
  try {
    const response: AxiosResponse<any> = await apiClient().post(
      '/api/v2/taxation/calculate',
      {
        employee_id: empId,
        tax_year: taxYear,
        regime,
      }
    );
    return response.data;
  } catch (error) {
    if (process.env.NODE_ENV === 'development') {
      // eslint-disable-next-line no-console
      console.error('Error calculating tax:', error);
    }
    throw error;
  }
};

// Create default perquisites object
const createDefaultPerquisites = (): Perquisites => ({
  // Accommodation perquisites
  accommodation_provided: 'Employer-Owned',
  accommodation_govt_lic_fees: 0,
  accommodation_city_population: 'Exceeding 40 lakhs in 2011 Census',
  accommodation_rent: 0,
  is_furniture_owned: false,
  furniture_actual_cost: 0,
  furniture_cost_to_employer: 0,
  furniture_cost_paid_by_employee: 0,

  // Car perquisites
  is_car_rating_higher: false,
  is_car_employer_owned: false,
  is_expenses_reimbursed: false,
  is_driver_provided: false,
  car_use: 'Personal',
  car_cost_to_employer: 0,
  month_counts: 0,
  other_vehicle_cost_to_employer: 0,
  other_vehicle_month_counts: 0,

  // Medical Reimbursement
  is_treated_in_India: false,
  medical_reimbursement_by_employer: 0,
  travelling_allowance_for_treatment: 0,
  rbi_limit_for_illness: 0,

  // Leave Travel Allowance
  lta_amount_claimed: 0,
  lta_claimed_count: 0,
  travel_through: 'Air',
  public_transport_travel_amount_for_same_distance: 0,
  lta_claim_start_date: '',
  lta_claim_end_date: '',

  // Free Education
  employer_maintained_1st_child: false,
  monthly_count_1st_child: 0,
  employer_monthly_expenses_1st_child: 0,
  employer_maintained_2nd_child: false,
  monthly_count_2nd_child: 0,
  employer_monthly_expenses_2nd_child: 0,

  // Gas, Electricity, Water
  is_gas_manufactured_by_employer: false,
  gas_amount_paid_by_employer: 0,
  gas_amount_paid_by_employee: 0,
  is_electricity_manufactured_by_employer: false,
  electricity_amount_paid_by_employer: 0,
  electricity_amount_paid_by_employee: 0,
  is_water_manufactured_by_employer: false,
  water_amount_paid_by_employer: 0,
  water_amount_paid_by_employee: 0,

  // Domestic help
  domestic_help_amount_paid_by_employer: 0,
  domestic_help_amount_paid_by_employee: 0,

  // Interest-free/concessional loan
  loan_type: 'Personal',
  loan_amount: 0,
  loan_interest_rate_company: 0,
  loan_interest_rate_sbi: 0,
  loan_month_count: 0,
  loan_start_date: '',
  loan_end_date: '',

  // Lunch/Refreshment
  lunch_amount_paid_by_employer: 0,
  lunch_amount_paid_by_employee: 0,

  // ESOP & Stock Options fields
  number_of_esop_shares_exercised: 0,
  esop_exercise_price_per_share: 0,
  esop_allotment_price_per_share: 0,
  grant_date: null,
  vesting_date: null,
  exercise_date: null,
  vesting_period: 0,
  exercise_period: 0,
  exercise_price_per_share: 0,

  // Movable Asset
  mau_ownership: 'Employer-Owned',
  mau_value_to_employer: 0,
  mau_value_to_employee: 0,
  mat_type: 'Electronics',
  mat_value_to_employer: 0,
  mat_value_to_employee: 0,
  mat_number_of_completed_years_of_use: 0,

  // Monetary Benefits
  monetary_amount_paid_by_employer: 0,
  expenditure_for_offical_purpose: 0,
  monetary_benefits_amount_paid_by_employee: 0,
  gift_vouchers_amount_paid_by_employer: 0,

  // Club Expenses
  club_expenses_amount_paid_by_employer: 0,
  club_expenses_amount_paid_by_employee: 0,
  club_expenses_amount_paid_for_offical_purpose: 0,
});

// Create default salary components
const createDefaultSalaryComponents = (): SalaryComponents => ({
  basic: 0,
  dearness_allowance: 0,
  hra_city: 'Others',
  hra_percentage: 0.4,
  hra: 0,
  actual_rent_paid: 0,
  special_allowance: 0,
  bonus: 0,
  commission: 0,
  city_compensatory_allowance: 0,
  rural_allowance: 0,
  proctorship_allowance: 0,
  wardenship_allowance: 0,
  project_allowance: 0,
  deputation_allowance: 0,
  overtime_allowance: 0,
  interim_relief: 0,
  tiffin_allowance: 0,
  fixed_medical_allowance: 0,
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
  transport_allowance: 0,
  transport_months: 0,
  underground_mines_allowance: 0,
  underground_mines_months: 0,
  govt_employee_entertainment_allowance: 0,
  govt_employees_outside_india_allowance: 0,
  supreme_high_court_judges_allowance: 0,
  judge_compensatory_allowance: 0,
  section_10_14_special_allowances: 0,
  any_other_allowance: 0,
  any_other_allowance_exemption: 0,
  travel_on_tour_allowance: 0,
  tour_daily_charge_allowance: 0,
  conveyance_in_performace_of_duties: 0,
  helper_in_performace_of_duties: 0,
  academic_research: 0,
  uniform_allowance: 0,
  perquisites: createDefaultPerquisites(),
});

// Create default other sources
const createDefaultOtherSources = (): OtherSources => ({
  interest_savings: 0,
  interest_fd: 0,
  interest_rd: 0,
  dividend_income: 0,
  gifts: 0,
  other_interest: 0,
  business_professional_income: 0,
  other_income: 0,
});

// Create default capital gains
const createDefaultCapitalGains = (): CapitalGains => ({
  stcg_111a: 0,
  stcg_any_other_asset: 0,
  stcg_debt_mutual_fund: 0,
  ltcg_112a: 0,
  ltcg_any_other_asset: 0,
  ltcg_debt_mutual_fund: 0,
});

// Create default leave encashment
const createDefaultLeaveEncashment = (): LeaveEncashment => ({
  leave_encashment_income_received: 0,
  leave_encashed: 0,
  is_deceased: false,
  during_employment: false,
});

// Create default house property
const createDefaultHouseProperty = (): HouseProperty => ({
  property_address: '',
  occupancy_status: 'Self-Occupied',
  rent_income: 0,
  property_tax: 0,
  interest_on_home_loan: 0,
  pre_construction_loan_interest: 0,
});

// Create default pension
const createDefaultPension = (): Pension => ({
  total_pension_income: 0,
  computed_pension_percentage: 0,
  uncomputed_pension_frequency: 'Monthly',
  uncomputed_pension_amount: 0,
});

// Create default deductions
const createDefaultDeductions = (): Deductions => ({
  section_80c_lic: 0,
  section_80c_epf: 0,
  section_80c_ssp: 0,
  section_80c_nsc: 0,
  section_80c_ulip: 0,
  section_80c_tsmf: 0,
  section_80c_tffte2c: 0,
  section_80c_paphl: 0,
  section_80c_sdpphp: 0,
  section_80c_tsfdsb: 0,
  section_80c_scss: 0,
  section_80c_others: 0,
  section_80ccc_ppic: 0,
  section_80ccd_1_nps: 0,
  section_80ccd_1b_additional: 0,
  section_80ccd_2_enps: 0,
  section_80d_hisf: 0,
  section_80d_phcs: 0,
  section_80d_hi_parent: 0,
  section_80dd: 0,
  relation_80dd: '',
  disability_percentage: '',
  section_80ddb: 0,
  relation_80ddb: '',
  age_80ddb: 0,
  section_80e_interest: 0,
  relation_80e: '',
  section_80eeb: 0,
  ev_purchase_date: null,
  section_80g_100_wo_ql: 0,
  section_80g_100_head: '',
  section_80g_50_wo_ql: 0,
  section_80g_50_head: '',
  section_80g_100_ql: 0,
  section_80g_100_ql_head: '',
  section_80g_50_ql: 0,
  section_80g_50_ql_head: '',
  section_80ggc: 0,
  section_80u: 0,
  disability_percentage_80u: '',
});

// Submit or update taxation data
export const saveTaxationData = async (
  taxationData: Partial<TaxationData>
): Promise<TaxationData> => {
  try {
    // Add filing_status if not present
    if (!taxationData.filing_status) {
      taxationData.filing_status = 'draft';
    }

    // Add default values for other required fields if not present
    if (!taxationData.tax_breakup) {
      taxationData.tax_breakup = {
        gross_total_income: 0,
        total_deductions: 0,
        taxable_income: 0,
        tax_before_relief: 0,
        tax_relief: 0,
        tax_payable: 0,
      };
    }

    // Make sure salary components exist
    if (!taxationData.salary) {
      taxationData.salary = createDefaultSalaryComponents();
    } else if (!taxationData.salary.perquisites) {
      taxationData.salary.perquisites = createDefaultPerquisites();
    }

    // Initialize other_sources if missing
    if (!taxationData.other_sources) {
      taxationData.other_sources = createDefaultOtherSources();
    }

    // Initialize capital_gains if missing
    if (!taxationData.capital_gains) {
      taxationData.capital_gains = createDefaultCapitalGains();
    }

    if (!taxationData.leave_encashment) {
      taxationData.leave_encashment = createDefaultLeaveEncashment();
    }

    if (!taxationData.house_property) {
      taxationData.house_property = createDefaultHouseProperty();
    }

    if (!taxationData.pension) {
      taxationData.pension = createDefaultPension();
    }

    // Initialize deductions if missing
    if (!taxationData.deductions) {
      taxationData.deductions = createDefaultDeductions();
    }

    // Initialize government employment status if missing
    if (taxationData.is_govt_employee === undefined) {
      taxationData.is_govt_employee = false;
    }

    // Initialize payment fields if not present
    if (taxationData.tax_payable === undefined) taxationData.tax_payable = 0;
    if (taxationData.tax_paid === undefined) taxationData.tax_paid = 0;
    if (taxationData.tax_due === undefined) taxationData.tax_due = 0;
    if (taxationData.tax_refundable === undefined)
      taxationData.tax_refundable = 0;
    if (taxationData.tax_pending === undefined) taxationData.tax_pending = 0;

    // Updated to use v2 API endpoint
    const response: AxiosResponse<TaxationData> = await apiClient().post(
      '/api/v2/taxation/save-taxation-data',
      taxationData
    );
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Update tax payment
export const updateTaxPayment = async (
  empId: string,
  amountPaid: number
): Promise<any> => {
  try {
    // Updated to use v2 API endpoint
    const response: AxiosResponse<any> = await apiClient().post(
      '/api/v2/taxation/update-tax-payment',
      {
        employee_id: empId,
        amount_paid: amountPaid,
      }
    );
    return response.data;
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
    const response: AxiosResponse<any> = await apiClient().post(
      '/update-filing-status',
      {
        employee_id: empId,
        status,
      }
    );
    return response.data;
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
    // Updated to use v2 API endpoint
    const response: AxiosResponse<any> = await apiClient().post(
      `/api/v2/taxation/compute-vrs-value/${empId}`,
      vrsData
    );
    return response.data;
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
    // Updated to use v2 API endpoint
    const response: AxiosResponse<TaxationData> =
      await apiClient().get(`/api/v2/taxation/my-taxation`);
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
