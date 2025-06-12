import { VALIDATION_RULES } from '../constants';
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
    return { isValid: false, message: 'Password is required' };
  }

  if (password.length < VALIDATION_RULES.MIN_PASSWORD_LENGTH) {
    return {
      isValid: false,
      message: `Password must be at least ${VALIDATION_RULES.MIN_PASSWORD_LENGTH} characters long`,
    };
  }

  return { isValid: true, message: '' };
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
    return { isValid: false, message: `${fieldName} is required` };
  }

  return { isValid: true, message: '' };
};

/**
 * Validate file upload
 * @param file - File to validate
 * @param options - Validation options
 * @returns Validation result
 */
export const validateFile = (
  file: File | null,
  options: FileUploadOptions = {}
): ValidationResult => {
  const {
    maxSize = 5 * 1024 * 1024, // 5MB default
    allowedTypes = ['image/jpeg', 'image/png', 'application/pdf'],
    required = false,
  } = options;

  if (!file) {
    if (required) {
      return { isValid: false, message: 'File is required' };
    }
    return { isValid: true, message: '' };
  }

  if (file.size > maxSize) {
    const maxSizeMB = (maxSize / 1024 / 1024).toFixed(1);
    return {
      isValid: false,
      message: `File size must be less than ${maxSizeMB}MB`,
    };
  }

  if (!allowedTypes.includes(file.type)) {
    const allowedTypesStr = allowedTypes
      .map(type => type.split('/')[1]?.toUpperCase())
      .join(', ');
    return {
      isValid: false,
      message: `Invalid file type. Allowed: ${allowedTypesStr}`,
    };
  }

  return { isValid: true, message: '' };
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
    return { isValid: false, message: 'Both start and end dates are required' };
  }

  const start = new Date(startDate);
  const end = new Date(endDate);

  if (start > end) {
    return { isValid: false, message: 'Start date cannot be after end date' };
  }

  return { isValid: true, message: '' };
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
    return { isValid: true, message: '' }; // Allow empty values
  }

  const numValue = Number(value);

  if (isNaN(numValue)) {
    return { isValid: false, message: 'Must be a valid number' };
  }

  if (!allowDecimals && !Number.isInteger(numValue)) {
    return { isValid: false, message: 'Must be a whole number' };
  }

  if (min !== undefined && numValue < min) {
    return { isValid: false, message: `Must be at least ${min}` };
  }

  if (max !== undefined && numValue > max) {
    return { isValid: false, message: `Must be at most ${max}` };
  }

  return { isValid: true, message: '' };
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
        errors[field] = requiredResult.message;
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
        errors[field] = result.message;
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
      return { isValid: false, message: 'Email must be a string' };
    }
    return isValidEmail(value)
      ? { isValid: true, message: '' }
      : { isValid: false, message: 'Invalid email format' };
  };

/**
 * Mobile validation function
 * @returns Validation function for mobile
 */
export const mobile =
  () =>
  (value: unknown): ValidationResult => {
    if (typeof value !== 'string') {
      return { isValid: false, message: 'Mobile number must be a string' };
    }
    return isValidMobile(value)
      ? { isValid: true, message: '' }
      : { isValid: false, message: 'Invalid mobile number format' };
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
