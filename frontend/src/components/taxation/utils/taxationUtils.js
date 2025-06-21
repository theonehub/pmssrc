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
  employee_id: empId,
  age: 0,
  regime: 'old',
  tax_year: getCurrentFinancialYear(),
  is_govt_employee: false,
  salary_income: {
    basic_salary: 0,
    dearness_allowance: 0,
    hra_received: 0,
    actual_rent_paid: 0,
    hra_city_type: 'non_metro',
    special_allowance: 0,
    conveyance_allowance: 0,
    medical_allowance: 0,
    other_allowances: 0,
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
    servant_allowance: 0,
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
  },
  other_income: {
    interest_income: {
      savings_account_interest: 0,
      fixed_deposit_interest: 0,
      recurring_deposit_interest: 0,
      post_office_interest: 0,
    },
    dividend_income: 0,
    gifts_received: 0,
    business_professional_income: 0,
    other_miscellaneous_income: 0
  },
  house_property_income: {
    property_type: 'Self-Occupied',
    annual_rent: 0,
    municipal_tax: 0,
    standard_deduction: 0,
    interest_on_loan: 0,
    net_income: 0,
    property_address: '',
    occupancy_status: 'Self-Occupied',
    pre_construction_loan_interest: 0
  },
  capital_gains_income: {
    stcg_111a_equity_stt: 0,
    stcg_other_assets: 0,
    stcg_debt_mf: 0,
    ltcg_112a_equity_stt: 0,
    ltcg_other_assets: 0,
    ltcg_debt_mf: 0
  },
  retirement_benefits: {
    leave_encashment: {
      leave_encashment_income_received: 0,
      leave_encashment_exemption: 0,
      leave_encashment_taxable: 0,
      is_deceased: false,
      during_employment: false
    },
    pension: {
      pension_received: 0,
      commuted_pension: 0,
      uncommuted_pension: 0,
      computed_pension_percentage: 0,
      uncomputed_pension_frequency: 'Monthly',
      uncomputed_pension_amount: 0
    },
    vrs: {
      compensation_received: 0,
      exemption_limit: 0,
      taxable_amount: 0,
      is_vrs_requested: false,
    },
    gratuity: {
      gratuity_received: 0,
      exemption_limit: 0,
      taxable_amount: 0,
    },
    retrenchment_compensation: {
      compensation_received: 0,
      exemption_limit: 0,
      taxable_amount: 0,
      is_provided: false,
    },
  },
  deductions: {
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
  },
  perquisites: {
    accommodation: {
      accommodation_type: 'none',
      accommodation_value: 0,
      accommodation_govt_lic_fees: 0,
      accommodation_city_population: '',
      accommodation_rent: 0,
      is_furniture_owned: false,
      furniture_actual_cost: 0,
    },
    car_transport: {
      car_provided: false,
      car_cc: 0,
      car_owned_by: 'company',
      car_used_for_business: 0,
      car_value: 0,
      driver_salary: 0,
      fuel_provided: false,
      fuel_value: 0,
    },
    gas_electricity_water: {
      amount: 0,
    },
    medical_reimbursement: {
      amount: 0,
    },
    leave_travel_allowance: {
      lta_claimed: 0,
      lta_exempt: 0,
    },
    free_education: {
      education_provided: false,
      education_value: 0,
    },
    loans: {
      loan_amount: 0,
      loan_interest_rate: 0,
      loan_interest_benefit: 0,
    },
    movable_assets: {
      movable_assets_value: 0,
      mau_ownership: '',
      mau_value_to_employer: 0,
      mau_value_to_employee: 0,
      mat_type: '',
      mat_value_to_employer: 0,
      mat_value_to_employee: 0,
      mat_number_of_completed_years_of_use: 0,
    },
    esop_stock_options: {
      esop_value: 0,
      esop_exercise_price: 0,
      esop_market_price: 0,
    },
    other_perquisites: {
      domestic_help_amount_paid_by_employer: 0,
      domestic_help_amount_paid_by_employee: 0,
      gardener_amount_paid_by_employer: 0,
      sweeper_amount_paid_by_employer: 0,
      personal_attendant_amount_paid_by_employer: 0,
      security_amount_paid_by_employer: 0,
      watchman_amount_paid_by_employer: 0,
      credit_card_amount_paid_by_employer: 0,
      club_expenses_amount_paid_by_employer: 0,
      club_expenses_amount_paid_by_employee: 0,
      use_of_movable_assets_amount_paid_by_employer: 0,
      transfer_of_movable_assets_amount_paid_by_employer: 0,
      interest_free_loan_amount_paid_by_employer: 0,
      club_expenses_amount_paid_for_offical_purpose: 0,
      lunch_amount_paid_by_employer: 0,
      lunch_amount_paid_by_employee: 0,
      monetary_amount_paid_by_employer: 0,
      expenditure_for_offical_purpose: 0,
      monetary_benefits_amount_paid_by_employee: 0,
      gift_vouchers_amount_paid_by_employer: 0,
      total_perquisites: 0,
    },
  }
});

/**
 * Safe calculator function for evaluating basic arithmetic expressions
 * @param {string} expression - The expression to evaluate (should start with '=')
 * @returns {{isValid: boolean, result: number, error: string|null}} - Evaluation result
 */
export const evaluateCalculatorExpression = (expression) => {
  try {
    // Remove the '=' at the beginning
    const cleanExpression = expression.substring(1).trim();
    
    // Validate that the expression only contains allowed characters
    const allowedPattern = /^[0-9+\-*/.() ]+$/;
    if (!allowedPattern.test(cleanExpression)) {
      return {
        isValid: false,
        result: 0,
        error: 'Invalid characters in expression. Only numbers and +, -, *, /, %, () are allowed.'
      };
    }
    
    // Replace % with /100 for percentage calculations
    const processedExpression = cleanExpression.replace(/(\d+(?:\.\d+)?)\s*%/g, '($1/100)');
    
    // Prevent dangerous operations by checking for function calls or assignments
    const dangerousPatterns = [
      /[a-zA-Z]/,  // No letters (function names)
      /=/,         // No assignments
      /;/,         // No semicolons
      /__/,        // No double underscores
      /\[|\]/,     // No array access
      /\{|\}/      // No object access
    ];
    
    for (const pattern of dangerousPatterns) {
      if (pattern.test(processedExpression)) {
        return {
          isValid: false,
          result: 0,
          error: 'Invalid expression format.'
        };
      }
    }
    
    // Evaluate the expression using Function constructor (safer than eval)
    // eslint-disable-next-line no-new-func
    const result = new Function('return ' + processedExpression)();
    
    // Check if result is a valid number
    if (typeof result !== 'number' || isNaN(result) || !isFinite(result)) {
      return {
        isValid: false,
        result: 0,
        error: 'Expression resulted in invalid number.'
      };
    }
    
    // Round to 2 decimal places to avoid floating point precision issues
    const roundedResult = Math.round(result * 100) / 100;
    
    return {
      isValid: true,
      result: roundedResult,
      error: null
    };
    
  } catch (error) {
    return {
      isValid: false,
      result: 0,
      error: 'Invalid mathematical expression.'
    };
  }
};

/**
 * Check if a value is a calculator expression (starts with '=')
 * @param {string} value - The value to check
 * @returns {boolean} - True if it's a calculator expression
 */
export const isCalculatorExpression = (value) => {
  return typeof value === 'string' && value.trim().startsWith('=');
};

/**
 * Validate calculator expression format
 * @param {string} expression - The expression to validate
 * @returns {{isValid: boolean, message: string}} - Validation result
 */
export const validateCalculatorExpression = (expression) => {
  if (!expression || !expression.startsWith('=')) {
    return { isValid: false, message: 'Calculator expressions must start with =' };
  }
  
  const cleanExpression = expression.substring(1).trim();
  
  if (cleanExpression.length === 0) {
    return { isValid: false, message: 'Empty expression after =' };
  }
  
  // Check for basic format issues
  if (cleanExpression.includes('**')) {
    return { isValid: false, message: 'Use * for multiplication, not **' };
  }
  
  if (cleanExpression.includes('//')) {
    return { isValid: false, message: 'Use / for division, not //' };
  }
  
  // Check for unmatched parentheses
  let openParens = 0;
  for (const char of cleanExpression) {
    if (char === '(') openParens++;
    if (char === ')') openParens--;
    if (openParens < 0) {
      return { isValid: false, message: 'Unmatched closing parenthesis' };
    }
  }
  
  if (openParens > 0) {
    return { isValid: false, message: 'Unmatched opening parenthesis' };
  }
  
  return { isValid: true, message: '' };
}; 