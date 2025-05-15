/**
 * Utility functions for taxation-related operations
 */

/**
 * Get current financial year in format YYYY-YYYY
 * @returns {string} Current financial year in format YYYY-YYYY
 */
export const getCurrentFinancialYear = () => {
  const today = new Date();
  const currentMonth = today.getMonth();
  const currentYear = today.getFullYear();
  
  // In India, financial year starts from April (month index 3)
  // If current month is January to March, FY is previous year to current year
  // If current month is April to December, FY is current year to next year
  if (currentMonth < 3) { // January to March
    return `${currentYear-1}-${currentYear}`;
  } else { // April to December
    return `${currentYear}-${currentYear+1}`;
  }
};

/**
 * Format number to Indian number format with commas
 * @param {number} num - Number to format
 * @returns {string} Formatted string with Indian number format
 */
export const formatIndianNumber = (num) => {
  if (num === '' || isNaN(num)) return '';
  
  // Convert to number
  const numValue = typeof num === 'string' ? parseFloat(num.replace(/,/g, '')) : num;
  
  // Format to Indian number format
  return numValue.toLocaleString('en-IN');
};

/**
 * Parse string with Indian number format to float
 * @param {string} str - String with Indian number format
 * @returns {number} Parsed float value
 */
export const parseIndianNumber = (str) => {
  if (!str) return 0;
  if (typeof str === 'number') return str;
  
  // Remove all commas
  return parseFloat(str.replace(/,/g, '')) || 0;
};

/**
 * Format currency in Indian Rupee format
 * @param {number} amount - Amount to format
 * @returns {string} Formatted string with Indian Rupee currency
 */
export const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(amount);
};

/**
 * Default state for the taxation form
 * @param {string} empId - Employee ID
 * @returns {Object} Default state object
 */
export const getDefaultTaxationState = (empId) => ({
  emp_id: empId,
  emp_age: 0,
  regime: 'old',
  tax_year: getCurrentFinancialYear(),
  is_govt_employee: false,
  salary: {
    basic: 0,
    dearness_allowance: 0,
    hra: 0,
    hra_city: 'Others',
    hra_percentage: 0.4,
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
    hills_high_altd_allowance: 0,
    border_remote_allowance: 0,
    transport_employee_allowance: 0,
    children_education_allowance: 0,
    hostel_allowance: 0,
    transport_allowance: 0,
    underground_mines_allowance: 0,
    perquisites: {
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
      loan_interest_rate_company: 0.0,
      loan_interest_rate_sbi: 0,
      loan_month_count: 0,
      loan_start_date: '',
      loan_end_date: '',
      
      // Lunch/Refreshment
      lunch_amount_paid_by_employer: 0,
      lunch_amount_paid_by_employee: 0,
      
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
      club_expenses_amount_paid_for_offical_purpose: 0
    }
  },
  other_sources: {
    interest_savings: 0,
    interest_fd: 0,
    interest_rd: 0,
    dividend_income: 0,
    gifts: 0,
    other_interest: 0,
    business_professional_income: 0,
    other_income: 0
  },
  house_property: {
    property_address: '',
    occupancy_status: 'Self-Occupied',
    rent_income: 0,
    property_tax: 0,
    interest_on_home_loan: 0
  },
  capital_gains: {
    stcg_111a: 0,
    stcg_any_other_asset: 0,
    stcg_debt_mutual_fund: 0,
    ltcg_112a: 0,
    ltcg_any_other_asset: 0,
    ltcg_debt_mutual_fund: 0
  },
  leave_encashment: {
    leave_encashment_income_received: 0,
    service_years: 0,
    leave_balance: 0
  },
  deductions: {
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
    section_80eeb: 0,
    section_80e_interest: 0,
    relation_80e: '',
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
    section_24b: 0
  }
}); 