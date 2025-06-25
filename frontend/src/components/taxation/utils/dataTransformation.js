import { getDefaultTaxationState } from './taxationUtils';

/**
 * Transform comprehensive taxation record from backend to frontend form format
 * @param {Object} comprehensiveRecord - Comprehensive taxation record from backend
 * @param {string} empId - Employee ID
 * @returns {Object} Transformed data for frontend form
 */
export const transformComprehensiveRecordToFormData = (comprehensiveRecord, empId) => {
  if (!comprehensiveRecord) {
    return getDefaultTaxationState(empId);
  }

  // Helper function to convert Decimal strings to numbers
  const toNumber = (value) => {
    if (value === null || value === undefined) return 0;
    if (typeof value === 'string') return parseFloat(value) || 0;
    if (typeof value === 'number') return value;
    return 0;
  };

  // Helper function to safely extract nested object values
  const safeExtract = (obj, defaultValue = {}) => {
    return obj && typeof obj === 'object' ? obj : defaultValue;
  };

  // Helper function to transform nested objects with number conversion
  const transformNestedObject = (sourceObj, defaultFields = {}) => {
    const source = safeExtract(sourceObj, defaultFields);
    const result = {};
    
    // First, set all default fields
    Object.keys(defaultFields).forEach(key => {
      result[key] = defaultFields[key];
    });
    
    // Then, override with actual values from source
    Object.keys(source).forEach(key => {
      if (typeof defaultFields[key] === 'number') {
        result[key] = toNumber(source[key]);
      } else if (typeof defaultFields[key] === 'string') {
        result[key] = source[key] || defaultFields[key];
      } else {
        result[key] = source[key] !== undefined ? source[key] : defaultFields[key];
      }
    });
    
    return result;
  };

  try {
    // Transform the comprehensive record to form format
    const transformedData = {
      employee_id: comprehensiveRecord.employee_id || empId,
      age: toNumber(comprehensiveRecord.age),
      emp_age: toNumber(comprehensiveRecord.age), // Frontend uses emp_age
      regime: comprehensiveRecord.regime_type || 'old',
      tax_year: comprehensiveRecord.tax_year || getDefaultTaxationState(empId).tax_year,
      is_govt_employee: Boolean(comprehensiveRecord.is_govt_employee),

      // Transform salary income with all allowances
      salary_income: transformNestedObject(comprehensiveRecord.salary_income, {
        basic_salary: 0,
        dearness_allowance: 0,
        hra_provided: 0,
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
      }),

      // Transform perquisites (keep as is for now, as it's complex nested structure)
      perquisites: safeExtract(comprehensiveRecord.perquisites, {
        accommodation: null,
        car: null,
        medical_reimbursement: null,
        lta: null,
        interest_free_loan: null,
        esop: null,
        utilities: null,
        free_education: null,
        lunch_refreshment: null,
        domestic_help: null,
        movable_asset_usage: null,
        movable_asset_transfer: null,
        gift_voucher: null,
        monetary_benefits: null,
        club_expenses: null
      }),

      // Transform house property income
      house_property_income: transformNestedObject(comprehensiveRecord.house_property_income, {
        property_type: 'Self-Occupied',
        annual_rent_received: 0,
        municipal_taxes_paid: 0,
        home_loan_interest: 0,
        pre_construction_interest: 0,
  
        
      }),

      // Transform capital gains
      capital_gains_income: transformNestedObject(comprehensiveRecord.capital_gains_income, {
        stcg_111a_equity_stt: 0,
        stcg_other_assets: 0,
        ltcg_112a_equity_stt: 0,
        ltcg_other_assets: 0,
        ltcg_debt_mf: 0,
      }),

      // Transform retirement benefits (keep as is for complex nested structure)
      retirement_benefits: safeExtract(comprehensiveRecord.retirement_benefits),

      // Transform other income
      other_income: {
        interest_income: safeExtract(comprehensiveRecord.other_income?.interest_income),
        dividend_income: toNumber(comprehensiveRecord.other_income?.dividend_income),
        gifts_received: toNumber(comprehensiveRecord.other_income?.gifts_received),
        business_professional_income: toNumber(comprehensiveRecord.other_income?.business_professional_income),
        other_miscellaneous_income: toNumber(comprehensiveRecord.other_income?.other_miscellaneous_income),
      },

      // Transform deductions with proper nested structure
      deductions: {
        hra_exemption: transformNestedObject(comprehensiveRecord.deductions?.hra_exemption, {
          actual_rent_paid: 0,
          hra_city_type: 'non_metro',
        }),
        section_80c: transformNestedObject(comprehensiveRecord.deductions?.section_80c, {
          life_insurance_premium: 0,
          epf_contribution: 0,
          ppf_contribution: 0,
          nsc_investment: 0,
          tax_saving_fd: 0,
          elss_investment: 0,
          home_loan_principal: 0,
          tuition_fees: 0,
          ulip_premium: 0,
          sukanya_samriddhi: 0,
          stamp_duty_property: 0,
          senior_citizen_savings: 0,
          other_80c_investments: 0,
        }),
        section_80d: transformNestedObject(comprehensiveRecord.deductions?.section_80d, {
          self_family_premium: 0,
          parent_premium: 0,
          preventive_health_checkup: 0,
          employee_age: 30,
          parent_age: 60,
        }),
        section_80g: safeExtract(comprehensiveRecord.deductions?.section_80g, {}),
        section_80e: {
          education_loan_interest: toNumber(comprehensiveRecord.deductions?.section_80e?.education_loan_interest),
          relation: comprehensiveRecord.deductions?.section_80e?.relation || 'Self',
        },
        section_80tta_ttb: transformNestedObject(comprehensiveRecord.deductions?.section_80tta_ttb, {
          savings_interest: 0,
          fd_interest: 0,
          rd_interest: 0,
          post_office_interest: 0,
          age: 25,
        }),
        other_deductions: transformNestedObject(comprehensiveRecord.deductions?.other_deductions, {
          education_loan_interest: 0,
          charitable_donations: 0,
          savings_interest: 0,
          nps_contribution: 0,
          other_deductions: 0,
        }),
      },

      // Add any other fields that might be needed
      multiple_house_properties: safeExtract(comprehensiveRecord.multiple_house_properties),
      monthly_payroll: safeExtract(comprehensiveRecord.monthly_payroll),
      periodic_salary_income: safeExtract(comprehensiveRecord.periodic_salary_income),
    };

    if (process.env.NODE_ENV === 'development') {
      // eslint-disable-next-line no-console
      console.log('🔄 Transformed comprehensive record:', {
        original_keys: Object.keys(comprehensiveRecord),
        transformed_keys: Object.keys(transformedData),
        salary_basic: transformedData.salary_income?.basic_salary,
        deductions_80c: Object.keys(transformedData.deductions?.section_80c || {}),
      });
    }

    return transformedData;
  } catch (error) {
    if (process.env.NODE_ENV === 'development') {
      // eslint-disable-next-line no-console
      console.error('❌ Error transforming comprehensive record:', error);
    }
    // Fallback to default state if transformation fails
    return getDefaultTaxationState(empId);
  }
}; 