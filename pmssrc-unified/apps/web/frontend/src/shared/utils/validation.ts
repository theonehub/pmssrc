import { VALIDATION_RULES } from './constants';
import { ValidationResult, FileUploadOptions } from '../types';

/**
 * Validation utility functions
 */

/**
 * Validate email format
 * @param email - Email to validate
 * @returns True if valid
 */
export const isValidEmail = (email: string): boolean => {
  if (!email) return false;
  return VALIDATION_RULES.EMAIL_REGEX.test(email);
};

/**
 * Validate mobile number format (10 digits)
 * @param mobile - Mobile number to validate
 * @returns True if valid
 */
export const isValidMobile = (mobile: string): boolean => {
  if (!mobile) return false;
  const cleanMobile = mobile.replace(/\D/g, '');
  return VALIDATION_RULES.MOBILE_REGEX.test(cleanMobile);
};

/**
 * Validate PAN number format
 * @param pan - PAN number to validate
 * @returns True if valid
 */
export const isValidPAN = (pan: string): boolean => {
  if (!pan) return false;
  return VALIDATION_RULES.PAN_REGEX.test(pan.toUpperCase());
};

/**
 * Validate Aadhar number format
 * @param aadhar - Aadhar number to validate
 * @returns True if valid
 */
export const isValidAadhar = (aadhar: string): boolean => {
  if (!aadhar) return false;
  const cleanAadhar = aadhar.replace(/\D/g, '');
  return VALIDATION_RULES.AADHAR_REGEX.test(cleanAadhar);
};

/**
 * Validate UAN number format
 * @param uan - UAN number to validate
 * @returns True if valid
 */
export const isValidUAN = (uan: string): boolean => {
  if (!uan) return false;
  const cleanUAN = uan.replace(/\D/g, '');
  return VALIDATION_RULES.UAN_REGEX.test(cleanUAN);
};

/**
 * Validate ESI number format
 * @param esi - ESI number to validate
 * @returns True if valid
 */
export const isValidESI = (esi: string): boolean => {
  if (!esi) return false;
  const cleanESI = esi.replace(/\D/g, '');
  return VALIDATION_RULES.ESI_REGEX.test(cleanESI);
};

/**
 * Validate password strength
 * @param password - Password to validate
 * @returns Validation result with isValid and message
 */
export const validatePassword = (password: string): ValidationResult => {
  if (!password) {
    return { isValid: false, message: 'Password is required', errors: ['Password is required'] };
  }

  if (password.length < VALIDATION_RULES.MIN_PASSWORD_LENGTH) {
    return {
      isValid: false,
      message: `Password must be at least ${VALIDATION_RULES.MIN_PASSWORD_LENGTH} characters long`,
      errors: [`Password must be at least ${VALIDATION_RULES.MIN_PASSWORD_LENGTH} characters long`],
    };
  }

  return { isValid: true, message: '', errors: [] };
};

/**
 * Validate required field
 * @param value - Value to validate
 * @param fieldName - Name of the field for error message
 * @returns Validation result
 */
export const validateRequired = (
  value: unknown,
  fieldName = 'Field'
): ValidationResult => {
  const stringValue =
    typeof value === 'string' ? value.trim() : String(value || '').trim();

  if (!stringValue) {
    return { isValid: false, message: `${fieldName} is required`, errors: [`${fieldName} is required`] };
  }

  return { isValid: true, message: '', errors: [] };
};

/**
 * Validate file upload
 * @param file - File to validate
 * @param options - Validation options
 * @returns Validation result
 */
export const validateFile = (
  file: File | null,
  options: FileUploadOptions = {
    maxSize: 5 * 1024 * 1024, // 5MB default
    allowedTypes: ['image/jpeg', 'image/png', 'application/pdf'],
    multiple: false
  },
  required = false,
): ValidationResult => {
  if (!file) {
    if (required) {
      return { isValid: false, message: 'File is required', errors: ['File is required'] };
    }
    return { isValid: true, message: '', errors: [] };
  }

  // Check file size
  if (file.size > options.maxSize) {
    const maxSizeMB = Math.round(options.maxSize / (1024 * 1024));
    return {
      isValid: false,
      message: `File size must be less than ${maxSizeMB}MB`,
      errors: [`File size must be less than ${maxSizeMB}MB`],
    };
  }

  // Check file type
  if (options.allowedTypes && !options.allowedTypes.includes(file.type)) {
    const allowedTypesStr = options.allowedTypes.join(', ');
    return {
      isValid: false,
      message: `Invalid file type. Allowed: ${allowedTypesStr}`,
      errors: [`Invalid file type. Allowed: ${allowedTypesStr}`],
    };
  }

  return { isValid: true, message: '', errors: [] };
};

/**
 * Validate date range
 * @param startDate - Start date
 * @param endDate - End date
 * @returns Validation result
 */
export const validateDateRange = (
  startDate: Date | string,
  endDate: Date | string
): ValidationResult => {
  if (!startDate || !endDate) {
    return { isValid: false, message: 'Both start and end dates are required', errors: ['Both start and end dates are required'] };
  }

  const start = new Date(startDate);
  const end = new Date(endDate);

  if (start > end) {
    return { isValid: false, message: 'Start date cannot be after end date', errors: ['Start date cannot be after end date'] };
  }

  return { isValid: true, message: '', errors: [] };
};

interface NumericValidationOptions {
  min?: number;
  max?: number;
  allowDecimals?: boolean;
}

/**
 * Validate numeric value
 * @param value - Value to validate
 * @param options - Validation options
 * @returns Validation result
 */
export const validateNumeric = (
  value: unknown,
  options: NumericValidationOptions = {}
): ValidationResult => {
  const { min, max, allowDecimals = true } = options;

  if (value === '' || value === null || value === undefined) {
    return { isValid: true, message: '', errors: [] }; // Allow empty values
  }

  const numValue = Number(value);

  if (isNaN(numValue)) {
    return { isValid: false, message: 'Must be a valid number', errors: ['Must be a valid number'] };
  }

  if (!allowDecimals && !Number.isInteger(numValue)) {
    return { isValid: false, message: 'Must be a whole number', errors: ['Must be a whole number'] };
  }

  if (min !== undefined && numValue < min) {
    return { isValid: false, message: `Must be at least ${min}`, errors: [`Must be at least ${min}`] };
  }

  if (max !== undefined && numValue > max) {
    return { isValid: false, message: `Must be at most ${max}`, errors: [`Must be at most ${max}`] };
  }

  return { isValid: true, message: '', errors: [] };
};

interface ValidationRule {
  validator: (value: unknown) => ValidationResult;
  required?: boolean;
}

interface ValidationRules {
  [key: string]: ValidationRule;
}

/**
 * Validate form data against rules
 * @param data - Form data to validate
 * @param rules - Validation rules
 * @returns Object with errors for each field
 */
export const validateForm = (
  data: Record<string, unknown>,
  rules: ValidationRules
): Record<string, string> => {
  const errors: Record<string, string> = {};

  Object.keys(rules).forEach(field => {
    const rule = rules[field];
    const value = data[field];

    // Check required fields
    if (rule?.required) {
      const requiredResult = validateRequired(value, field);
      if (!requiredResult.isValid) {
        errors[field] = requiredResult.message || `${field} is required`;
        return;
      }
    }

    // Skip validation if field is empty and not required
    if (
      !rule?.required &&
      (value === '' || value === null || value === undefined)
    ) {
      return;
    }

    // Run field-specific validation
    if (rule?.validator) {
      const result = rule.validator(value);
      if (!result.isValid) {
        errors[field] = result.message || `${field} is invalid`;
      }
    }
  });

  return errors;
};

// Higher-order validation functions for common use cases

/**
 * Email validation function
 * @returns Validation function for email
 */
export const email =
  () =>
  (value: unknown): ValidationResult => {
    if (typeof value !== 'string') {
      return { isValid: false, message: 'Email must be a string', errors: ['Email must be a string'] };
    }
    return isValidEmail(value)
      ? { isValid: true, message: '', errors: [] }
      : { isValid: false, message: 'Invalid email format', errors: ['Invalid email format'] };
  };

/**
 * Mobile validation function
 * @returns Validation function for mobile
 */
export const mobile =
  () =>
  (value: unknown): ValidationResult => {
    if (typeof value !== 'string') {
      return { isValid: false, message: 'Mobile number must be a string', errors: ['Mobile number must be a string'] };
    }
    return isValidMobile(value)
      ? { isValid: true, message: '', errors: [] }
      : { isValid: false, message: 'Invalid mobile number format', errors: ['Invalid mobile number format'] };
  };

/**
 * Numeric validation function
 * @param options - Validation options
 * @returns Validation function for numeric values
 */
export const numeric =
  (options: NumericValidationOptions = {}) =>
  (value: unknown): ValidationResult => {
    return validateNumeric(value, options);
  };

// Export validators object for backward compatibility
export const validators = {
  required: (fieldName = 'Field') => (value: unknown): ValidationResult => 
    validateRequired(value, fieldName),
  
  email: () => (value: unknown): ValidationResult => {
    if (!value) return { isValid: true, message: '', errors: [] };
    const stringValue = String(value);
    return isValidEmail(stringValue) 
      ? { isValid: true, message: '', errors: [] }
      : { isValid: false, message: 'Please enter a valid email address', errors: ['Please enter a valid email address'] };
  },
  
  mobile: () => (value: unknown): ValidationResult => {
    if (!value) return { isValid: true, message: '', errors: [] };
    const stringValue = String(value);
    return isValidMobile(stringValue)
      ? { isValid: true, message: '', errors: [] }
      : { isValid: false, message: 'Please enter a valid mobile number', errors: ['Please enter a valid mobile number'] };
  },
  
  currency: (value: unknown): ValidationResult => {
    if (!value) return { isValid: true, message: '', errors: [] };
    const numValue = typeof value === 'number' ? value : parseFloat(String(value));
    return !isNaN(numValue) && numValue >= 0
      ? { isValid: true, message: '', errors: [] }
      : { isValid: false, message: 'Please enter a valid currency amount', errors: ['Please enter a valid currency amount'] };
  },
  
  numeric: (options: NumericValidationOptions = {}) => (value: unknown): ValidationResult => 
    validateNumeric(value, options),
  
  basicInfo: (data: any): { isValid: boolean; fieldErrors: Record<string, string> } => {
    const errors: Record<string, string> = {};
    
    // Basic validation for common fields
    if (data.employee_id && typeof data.employee_id === 'string' && data.employee_id.trim() === '') {
      errors.employee_id = 'Employee ID is required';
    }
    
    if (data.tax_year && typeof data.tax_year === 'string' && data.tax_year.trim() === '') {
      errors.tax_year = 'Tax year is required';
    }
    
    if (data.regime && !['old', 'new'].includes(data.regime)) {
      errors.regime = 'Please select a valid tax regime';
    }
    
    // Validate salary income if present
    if (data.salary_income) {
      const salaryIncome = data.salary_income;
      if (salaryIncome.basic_salary !== undefined && (isNaN(Number(salaryIncome.basic_salary)) || Number(salaryIncome.basic_salary) < 0)) {
        errors['salary_income.basic_salary'] = 'Basic salary must be a valid positive number';
      }
    }
    
    return {
      isValid: Object.keys(errors).length === 0,
      fieldErrors: errors
    };
  },
};

export const validateFormData = (
  data: Record<string, any>,
  rules: Record<string, ValidationRule[]>
): ValidationResult => {
  const errors: Record<string, string> = {};
  let isValid = true;

  for (const [field, fieldRules] of Object.entries(rules)) {
    const value = data[field];

    for (const rule of fieldRules) {
      if (rule.required) {
        const requiredResult = validateRequired(value, field);
        if (!requiredResult.isValid) {
          errors[field] = requiredResult.message || `${field} is required`;
          isValid = false;
          break;
        }
      }

      if (value !== undefined && value !== null && value !== '') {
        const result = rule.validator(value);
        if (!result.isValid) {
          errors[field] = result.message || `${field} is invalid`;
          isValid = false;
          break;
        }
      }
    }
  }

  return {
    isValid,
    errors: Object.values(errors),
    message: isValid ? 'Validation passed' : 'Validation failed'
  };
};
