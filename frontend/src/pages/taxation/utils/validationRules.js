/**
 * Validation rules for Indian taxation system
 * All limits and validations as per Indian Income Tax Act
 */

// Income Tax limits and constants for FY 2024-25
export const TAXATION_LIMITS = {
  // Basic limits
  MAX_SALARY_COMPONENT: 99999999, // 9.99 Crores
  MAX_AGE: 100,
  MIN_AGE: 18,
  
  // Section 80C limits
  SECTION_80C_LIMIT: 150000, // Rs. 1.5 lakh
  
  // Section 80D limits (Health Insurance)
  SECTION_80D_SELF_FAMILY_BELOW_60: 25000, // Rs. 25,000
  SECTION_80D_SELF_FAMILY_60_PLUS: 50000, // Rs. 50,000
  SECTION_80D_PARENTS_BELOW_60: 25000, // Rs. 25,000
  SECTION_80D_PARENTS_60_PLUS: 50000, // Rs. 50,000
  SECTION_80D_TOTAL_LIMIT: 100000, // Rs. 1 lakh (total for all)
  
  // Section 80DD limits (Disabled Dependent)
  SECTION_80DD_NORMAL: 75000, // Rs. 75,000
  SECTION_80DD_SEVERE: 125000, // Rs. 1.25 lakh
  
  // Section 80DDB limits (Medical Treatment)
  SECTION_80DDB_NORMAL: 40000, // Rs. 40,000
  SECTION_80DDB_SENIOR_CITIZEN: 100000, // Rs. 1 lakh
  
  // Section 80E limits (Education Loan Interest)
  SECTION_80E_NO_LIMIT: true, // No upper limit
  
  // Section 80EEB limits (Electric Vehicle Loan Interest)
  SECTION_80EEB_LIMIT: 150000, // Rs. 1.5 lakh
  
  // Section 80G limits (Donations)
  SECTION_80G_100_NO_QUALIFYING_LIMIT: 999999999, // No limit
  SECTION_80G_50_NO_QUALIFYING_LIMIT: 999999999, // No limit
  
  // Section 80GGC limits (Political Party Donations)
  SECTION_80GGC_NO_LIMIT: true, // No upper limit
  
  // Section 80U limits (Self Disability)
  SECTION_80U_NORMAL: 75000, // Rs. 75,000
  SECTION_80U_SEVERE: 125000, // Rs. 1.25 lakh
  
  // Section 80CCD limits (NPS)
  SECTION_80CCD_1_LIMIT_PERCENT: 0.1, // 10% of salary
  SECTION_80CCD_1B_ADDITIONAL: 50000, // Rs. 50,000 additional
  SECTION_80CCD_2_EMPLOYER_LIMIT_PERCENT: 0.14, // 14% of salary
  
  // HRA calculation limits
  HRA_METRO_RATE: 0.5, // 50% for metro cities
  HRA_NON_METRO_RATE: 0.4, // 40% for non-metro cities
  HRA_RENT_EXCESS_PERCENT: 0.1, // 10% of Basic + DA
  
  // Allowance exemption limits
  MEDICAL_REIMBURSEMENT_EXEMPTION: 15000, // Rs. 15,000
  LTA_BLOCK_YEARS: 4, // 4 years
  LTA_MAX_JOURNEYS: 2, // 2 journeys in block
  GIFT_VOUCHER_EXEMPTION: 5000, // Rs. 5,000
  
  // Children allowances
  CHILDREN_EDUCATION_ALLOWANCE_PER_CHILD: 100, // Rs. 100 per month per child
  MAX_CHILDREN_FOR_EDUCATION: 2, // Maximum 2 children
  HOSTEL_ALLOWANCE_PER_CHILD: 300, // Rs. 300 per month per child
  
  // Transport allowances
  TRANSPORT_EMPLOYEE_ALLOWANCE_LIMIT: 10000, // Rs. 10,000 or 70% whichever is less
  TRANSPORT_ALLOWANCE_DISABLED: 3200, // Rs. 3,200 per month for disabled
  UNDERGROUND_MINES_ALLOWANCE: 800, // Rs. 800 per month
  
  // Capital gains limits
  LTCG_EXEMPTION_LIMIT: 125000, // Rs. 1.25 lakh (Budget 2024)
  STCG_111A_RATE: 0.20, // 20% (Budget 2024)
  LTCG_112A_RATE: 0.125, // 12.5% (Budget 2024)
  
  // Interest-free loan limits
  LOAN_EXEMPTION_LIMIT: 20000, // Rs. 20,000
  
  // Perquisites limits
  CAR_PERQ_HIGHER_CAPACITY_WITH_EXPENSE: 2400, // Rs. 2,400 pm
  CAR_PERQ_LOWER_CAPACITY_WITH_EXPENSE: 1800, // Rs. 1,800 pm
  CAR_PERQ_HIGHER_CAPACITY_WITHOUT_EXPENSE: 900, // Rs. 900 pm
  CAR_PERQ_LOWER_CAPACITY_WITHOUT_EXPENSE: 600, // Rs. 600 pm
  DRIVER_PERQ_ADDITIONAL: 900, // Rs. 900 pm for driver
  
  // Lunch/Meal allowance
  LUNCH_EXEMPTION_PER_MEAL: 50, // Rs. 50 per meal
  
  // Free education
  FREE_EDUCATION_EXEMPTION: 1000, // Rs. 1,000 per month per child
  
  // Gratuity exemption
  GRATUITY_EXEMPTION_LIMIT: 2000000, // Rs. 20 lakh
  
  // Leave encashment exemption
  LEAVE_ENCASHMENT_EXEMPTION_LIMIT: 300000, // Rs. 3 lakh
  
  // VRS exemption
  VRS_EXEMPTION_LIMIT: 500000, // Rs. 5 lakh
  
  // Standard deduction (New regime)
  STANDARD_DEDUCTION_NEW_REGIME: 75000, // Rs. 75,000 (Budget 2025)
  
  // Age categories
  SENIOR_CITIZEN_AGE: 60,
  SUPER_SENIOR_CITIZEN_AGE: 80
};

// Validation functions
export const validateAmount = (amount, maxLimit = TAXATION_LIMITS.MAX_SALARY_COMPONENT) => {
  const numAmount = parseFloat(amount) || 0;
  return {
    isValid: true, // Always allow but provide warnings
    warning: numAmount < 0 ? 'Amount cannot be negative' : 
             numAmount > maxLimit ? `Amount exceeds recommended limit of ₹${maxLimit.toLocaleString('en-IN')}` : null
  };
};

export const validateAge = (age) => {
  const numAge = parseInt(age) || 0;
  return {
    isValid: true, // Always allow but provide warnings
    warning: numAge < TAXATION_LIMITS.MIN_AGE ? `Age is below typical working age of ${TAXATION_LIMITS.MIN_AGE}` :
             numAge > TAXATION_LIMITS.MAX_AGE ? `Age exceeds typical limit of ${TAXATION_LIMITS.MAX_AGE}` : null
  };
};

export const validateSection80C = (totalAmount) => {
  return {
    isValid: true, // Always allow but provide warnings
    warning: totalAmount > TAXATION_LIMITS.SECTION_80C_LIMIT ? 
             `Total Section 80C deductions exceed statutory limit of ₹${TAXATION_LIMITS.SECTION_80C_LIMIT.toLocaleString('en-IN')}. Excess amount will not be considered for deduction.` : null,
    remainingLimit: Math.max(0, TAXATION_LIMITS.SECTION_80C_LIMIT - totalAmount),
    info: totalAmount > 0 && totalAmount <= TAXATION_LIMITS.SECTION_80C_LIMIT ? 
          `Remaining Section 80C limit: ₹${Math.max(0, TAXATION_LIMITS.SECTION_80C_LIMIT - totalAmount).toLocaleString('en-IN')}` : null
  };
};

export const validateSection80D = (amount, age, type) => {
  let limit;
  if (type === 'self_family') {
    limit = age >= TAXATION_LIMITS.SENIOR_CITIZEN_AGE ? 
            TAXATION_LIMITS.SECTION_80D_SELF_FAMILY_60_PLUS : 
            TAXATION_LIMITS.SECTION_80D_SELF_FAMILY_BELOW_60;
  } else if (type === 'parents') {
    limit = age >= TAXATION_LIMITS.SENIOR_CITIZEN_AGE ? 
            TAXATION_LIMITS.SECTION_80D_PARENTS_60_PLUS : 
            TAXATION_LIMITS.SECTION_80D_PARENTS_BELOW_60;
  }
  
  return {
    isValid: true, // Always allow but provide warnings
    warning: amount > limit ? 
             `Section 80D ${type} deduction exceeds statutory limit of ₹${limit.toLocaleString('en-IN')} for ${age >= 60 ? 'senior citizens' : 'individuals below 60'}. Excess amount will not be considered.` : null,
    limit: limit
  };
};

export const validateHRA = (hra, basic, da, rentPaid, cityCategory) => {
  const salary = basic + da;
  const cityRate = cityCategory === 'metro' ? TAXATION_LIMITS.HRA_METRO_RATE : TAXATION_LIMITS.HRA_NON_METRO_RATE;
  
  const maxHRAByCity = salary * cityRate;
  const maxHRAByRent = Math.max(0, rentPaid - (salary * TAXATION_LIMITS.HRA_RENT_EXCESS_PERCENT));
  const maxHRAExemption = Math.min(hra, maxHRAByCity, maxHRAByRent);
  
  return {
    exemption: maxHRAExemption,
    taxable: Math.max(0, rentPaid - maxHRAExemption),
    calculations: {
      actualHRA: hra,
      cityBasedLimit: maxHRAByCity,
      rentBasedLimit: maxHRAByRent
    }
  };
};

export const validateLTA = (claimedCount, amount) => {
  return {
    isValid: true, // Always allow but provide warnings
    warning: claimedCount > TAXATION_LIMITS.LTA_MAX_JOURNEYS ? 
             `LTA claimed ${claimedCount} times exceeds limit of ${TAXATION_LIMITS.LTA_MAX_JOURNEYS} times in ${TAXATION_LIMITS.LTA_BLOCK_YEARS} years. Excess claims may not be exempt.` : null
  };
};

export const validateChildrenAllowances = (childrenCount, months) => {
  let warnings = [];
  if (childrenCount > TAXATION_LIMITS.MAX_CHILDREN_FOR_EDUCATION) {
    warnings.push(`Children count exceeds limit of ${TAXATION_LIMITS.MAX_CHILDREN_FOR_EDUCATION} for education allowance`);
  }
  if (months > 12) {
    warnings.push('Months cannot exceed 12');
  }
  
  return {
    isValid: true, // Always allow but provide warnings
    warning: warnings.length > 0 ? warnings.join('. ') : null
  };
};

export const validateInterestFreeLoan = (loanAmount) => {
  return {
    isExempt: loanAmount <= TAXATION_LIMITS.LOAN_EXEMPTION_LIMIT,
    message: loanAmount <= TAXATION_LIMITS.LOAN_EXEMPTION_LIMIT ? 
             'Loan amount is exempt from perquisite tax' : 
             'Loan amount exceeds exemption limit, perquisite value will be calculated'
  };
};

// Comprehensive form validation - now returns warnings instead of blocking errors
export const validateTaxationForm = (taxationData) => {
  const warnings = {};
  
  // Validate age
  if (taxationData.emp_age) {
    const ageValidation = validateAge(taxationData.emp_age);
    if (ageValidation.warning) {
      warnings.emp_age = ageValidation.warning;
    }
  }
  
  // Validate salary components
  if (taxationData.salary) {
    const salaryWarnings = {};
    
    Object.keys(taxationData.salary).forEach(field => {
      if (typeof taxationData.salary[field] === 'number' && field !== 'hra_percentage') {
        const validation = validateAmount(taxationData.salary[field]);
        if (validation.warning) {
          salaryWarnings[field] = validation.warning;
        }
      }
    });
    
    // Validate HRA calculation
    if (taxationData.salary.hra && taxationData.salary.basic) {
      const cityCategory = ['Delhi', 'Mumbai', 'Kolkata', 'Chennai'].includes(taxationData.salary.hra_city) ? 'metro' : 'non-metro';
      const hraValidation = validateHRA(
        taxationData.salary.hra,
        taxationData.salary.basic,
        taxationData.salary.dearness_allowance || 0,
        taxationData.salary.actual_rent_paid || 0,
        cityCategory
      );
      if (hraValidation.taxable > 0) {
        salaryWarnings.hra_info = `HRA exemption: ₹${hraValidation.exemption.toLocaleString('en-IN')}, Taxable: ₹${hraValidation.taxable.toLocaleString('en-IN')}`;
      } 
    }
    
    if (Object.keys(salaryWarnings).length > 0) {
      warnings.salary = salaryWarnings;
    }
  }
  
  // Validate deductions
  if (taxationData.deductions) {
    const deductionWarnings = {};
    
    // Section 80C validation
    const section80CTotal = (taxationData.deductions.section_80c_lic || 0) +
                           (taxationData.deductions.section_80c_epf || 0) +
                           (taxationData.deductions.section_80c_ssp || 0) +
                           (taxationData.deductions.section_80c_nsc || 0) +
                           (taxationData.deductions.section_80c_ulip || 0) +
                           (taxationData.deductions.section_80c_others || 0);
    
    const section80CValidation = validateSection80C(section80CTotal);
    if (section80CValidation.warning) {
      deductionWarnings.section_80c = section80CValidation.warning;
    }
    
    // Section 80D validation
    if (taxationData.deductions.section_80d_hisf) {
      const section80DValidation = validateSection80D(
        taxationData.deductions.section_80d_hisf,
        taxationData.emp_age || 0,
        'self_family'
      );
      if (section80DValidation.warning) {
        deductionWarnings.section_80d_self = section80DValidation.warning;
      }
    }
    
    if (Object.keys(deductionWarnings).length > 0) {
      warnings.deductions = deductionWarnings;
    }
  }
  
  return {
    isValid: true, // Always allow submission, just provide warnings
    warnings: warnings,
    hasWarnings: Object.keys(warnings).length > 0
  };
};

// Input sanitization and formatting
export const sanitizeNumericInput = (value, maxLimit = TAXATION_LIMITS.MAX_SALARY_COMPONENT) => {
  if (!value) return 0;
  
  // Remove all non-numeric characters except decimal point
  const cleanValue = value.toString().replace(/[^0-9.]/g, '');
  
  // Parse to number
  const numValue = parseFloat(cleanValue) || 0;
  
  // Apply max limit
  return Math.min(numValue, maxLimit);
};

// Real-time validation messages - updated to handle warnings
export const getValidationMessage = (field, value, context = {}) => {
  const validation = validateAmount(value);
  
  if (validation.warning) {
    return {
      type: 'warning',
      message: validation.warning
    };
  }
  
  // Contextual messages for specific fields
  switch (field) {
    case 'section_80c_total':
      const section80CValidation = validateSection80C(value);
      if (section80CValidation.warning) {
        return { type: 'warning', message: section80CValidation.warning };
      }
      if (section80CValidation.info) {
        return { type: 'info', message: section80CValidation.info };
      }
      break;
      
    case 'hra':
      if (context.basic && context.rentPaid) {
        const cityCategory = ['Delhi', 'Mumbai', 'Kolkata', 'Chennai'].includes(context.city) ? 'metro' : 'non-metro';
        const hraValidation = validateHRA(value, context.basic, context.da || 0, context.rentPaid, cityCategory);
        return {
          type: 'info',
          message: `HRA exemption: ₹${hraValidation.exemption.toLocaleString('en-IN')}`
        };
      }
      break;
      
    default:
      return null;
  }
};

export default {
  TAXATION_LIMITS,
  validateAmount,
  validateAge,
  validateSection80C,
  validateSection80D,
  validateHRA,
  validateLTA,
  validateChildrenAllowances,
  validateInterestFreeLoan,
  validateTaxationForm,
  sanitizeNumericInput,
  getValidationMessage
}; 