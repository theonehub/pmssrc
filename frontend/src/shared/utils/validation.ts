// =============================================================================
// VALIDATION UTILITIES
// Comprehensive validation functions for taxation forms and calculations
// =============================================================================

import { VALIDATION_RULES, DEDUCTION_LIMITS } from '../constants/taxation';
import { TaxRegime } from '../types/api';

// =============================================================================
// VALIDATION RESULT TYPES
// =============================================================================

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  fieldErrors: Record<string, string>;
}

export interface FieldValidationResult {
  isValid: boolean;
  error?: string | undefined;
  warning?: string | undefined;
}

// =============================================================================
// BASIC FIELD VALIDATORS
// =============================================================================

/**
 * Validate required field
 */
export const validateRequired = (value: any, fieldName?: string): FieldValidationResult => {
  const isEmpty = value === null || value === undefined || value === '' || 
                  (Array.isArray(value) && value.length === 0);
  
  if (isEmpty) {
    return {
      isValid: false,
      error: `${fieldName || 'This field'} is required`
    };
  }
  
  return {
    isValid: true
  };
};

/**
 * Validate numeric value within range
 */
export const validateNumber = (
  value: number | string,
  min?: number,
  max?: number,
  fieldName?: string
): FieldValidationResult => {
  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  
  if (isNaN(numValue)) {
    return {
      isValid: false,
      error: `${fieldName || 'Value'} must be a valid number`
    };
  }
  
  if (min !== undefined && numValue < min) {
    return {
      isValid: false,
      error: `${fieldName || 'Value'} must be at least ${min}`
    };
  }
  
  if (max !== undefined && numValue > max) {
    return {
      isValid: false,
      error: `${fieldName || 'Value'} must not exceed ${max}`
    };
  }
  
  return { isValid: true };
};

/**
 * Validate currency amount
 */
export const validateCurrency = (
  value: number | string,
  fieldName?: string,
  required: boolean = false
): FieldValidationResult => {
  if (!required && (value === null || value === undefined || value === '')) {
    return { isValid: true };
  }
  
  if (required) {
    const requiredResult = validateRequired(value, fieldName);
    if (!requiredResult.isValid) return requiredResult;
  }
  
  return validateNumber(value, 0, 99999999999, fieldName);
};

/**
 * Validate age
 */
export const validateAge = (age: number | string): FieldValidationResult => {
  const result = validateNumber(age, VALIDATION_RULES.field_limits.age.min, 
                               VALIDATION_RULES.field_limits.age.max, 'Age');
  
  if (!result.isValid) return result;
  
  const numAge = typeof age === 'string' ? parseInt(age) : age;
  
  // Add warnings for specific age ranges
  if (numAge >= 60 && numAge < 80) {
    return {
      isValid: true,
      warning: 'Senior citizen benefits available (higher deduction limits)'
    };
  }
  
  if (numAge >= 80) {
    return {
      isValid: true,
      warning: 'Super senior citizen benefits available (higher exemption limit)'
    };
  }
  
  return { isValid: true };
};

// =============================================================================
// TAXATION-SPECIFIC VALIDATORS
// =============================================================================

/**
 * Validate deduction limits based on tax regime
 */
export const validateDeduction = (
  section: string,
  amount: number,
  regime: TaxRegime
): FieldValidationResult => {
  const deductionInfo = DEDUCTION_LIMITS[section as keyof typeof DEDUCTION_LIMITS];
  
  if (!deductionInfo) {
    return {
      isValid: false,
      error: `Unknown deduction section: ${section}`
    };
  }
  
  // Check if deduction is applicable for the regime
  if (!deductionInfo.applicable_regime.includes(regime)) {
    return {
      isValid: false,
      error: `${section} is not applicable for ${regime} tax regime`
    };
  }
  
  // Check limits for specific sections
  if (typeof deductionInfo.limit === 'number' && amount > deductionInfo.limit) {
    return {
      isValid: false,
      error: `${section} limit is ₹${deductionInfo.limit.toLocaleString()}`
    };
  }
  
  return { isValid: true };
};

/**
 * Validate basic information section
 */
export const validateBasicInfo = (data: {
  tax_year?: string;
  regime_type?: TaxRegime;
  age?: number;
  residential_status?: string;
}): ValidationResult => {
  const errors: string[] = [];
  const warnings: string[] = [];
  const fieldErrors: Record<string, string> = {};
  
  // Required fields
  if (!data.tax_year) {
    errors.push('Tax year is required');
    fieldErrors.tax_year = 'Tax year is required';
  }
  
  if (!data.regime_type) {
    errors.push('Tax regime is required');
    fieldErrors.regime_type = 'Tax regime is required';
  }
  
  if (!data.age) {
    errors.push('Age is required');
    fieldErrors.age = 'Age is required';
  } else {
    const ageValidation = validateAge(data.age);
    if (!ageValidation.isValid) {
      errors.push(ageValidation.error!);
      fieldErrors.age = ageValidation.error!;
    } else if (ageValidation.warning) {
      warnings.push(ageValidation.warning);
    }
  }
  
  return {
    isValid: errors.length === 0,
    errors,
    warnings,
    fieldErrors
  };
};

// =============================================================================
// EXPORT ALL VALIDATORS
// =============================================================================

export const validators = {
  required: validateRequired,
  number: validateNumber,
  currency: validateCurrency,
  age: validateAge,
  deduction: validateDeduction,
  basicInfo: validateBasicInfo
}; 