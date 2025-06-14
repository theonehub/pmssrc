import React, { useState, useEffect, useCallback } from 'react';
import {
  TextField,
  FormHelperText,
  InputAdornment,
  Box,
  Typography,
  TextFieldProps
} from '@mui/material';
import { 
  validateAmount, 
  getValidationMessage,
  TAXATION_LIMITS 
} from '../utils/validationRules';
import { formatIndianNumber, parseIndianNumber } from '../utils/taxationUtils';

type FieldType = 
  | 'amount' 
  | 'age' 
  | 'section_80c_component' 
  | 'hra' 
  | 'lta_claimed_count' 
  | 'children_count' 
  | 'months' 
  | 'percentage' 
  | 'interest_rate' 
  | 'loan_amount' 
  | 'text' 
  | 'select'
  | string; // Allow other field types that include 'amount'

interface ValidationContext {
  currentTotal?: number;
  currentValue?: number;
  basic?: number;
  da?: number;
  rentPaid?: number;
  city?: string;
  [key: string]: any;
}

interface FieldState {
  color: 'primary' | 'warning';
  helperTextContent: string;
  helperTextColor: string;
}

interface ValidatedTextFieldProps extends Omit<TextFieldProps, 'onChange' | 'onFocus' | 'color'> {
  label: string;
  value: string | number;
  onChange: (value: string) => void;
  onFocus?: (event: React.FocusEvent<HTMLInputElement>) => void;
  fieldType?: FieldType;
  maxLimit?: number;
  validationContext?: ValidationContext;
  required?: boolean;
  disabled?: boolean;
  helperText?: string;
  sx?: object;
}

/**
 * ValidatedTextField - A text field component with built-in validation for Indian taxation
 */
const ValidatedTextField: React.FC<ValidatedTextFieldProps> = ({
  label,
  value,
  onChange,
  onFocus,
  fieldType = 'amount',
  maxLimit = TAXATION_LIMITS.MAX_SALARY_COMPONENT,
  validationContext = {},
  required = false,
  disabled = false,
  helperText = '',
  sx = {},
  ...props
}) => {
  const [touched, setTouched] = useState<boolean>(false);
  const [warning, setWarning] = useState<string>('');
  const [info, setInfo] = useState<string>('');

  const performFieldSpecificValidations = useCallback((numValue: number): void => {
    switch (fieldType) {
      case 'age':
        if (numValue < TAXATION_LIMITS.MIN_AGE || numValue > TAXATION_LIMITS.MAX_AGE) {
          setWarning(`Age is outside typical range (${TAXATION_LIMITS.MIN_AGE}-${TAXATION_LIMITS.MAX_AGE}). Please verify if correct.`);
        } else if (numValue >= TAXATION_LIMITS.SENIOR_CITIZEN_AGE) {
          setInfo(`Senior citizen benefits applicable (Age ${numValue})`);
        }
        break;

      case 'section_80c_component':
        if (validationContext.currentTotal && numValue > 0) {
          const newTotal = (validationContext.currentTotal - (validationContext.currentValue || 0)) + numValue;
          if (newTotal > TAXATION_LIMITS.SECTION_80C_LIMIT) {
            setWarning(`This exceeds Section 80C limit by ₹${(newTotal - TAXATION_LIMITS.SECTION_80C_LIMIT).toLocaleString('en-IN')}. Excess amount will not be considered for deduction.`);
          } else {
            const remaining = TAXATION_LIMITS.SECTION_80C_LIMIT - newTotal;
            if (remaining > 0) {
              setInfo(`Remaining Section 80C limit: ₹${remaining.toLocaleString('en-IN')}`);
            }
          }
        }
        break;

      case 'hra':
        if (validationContext.basic && validationContext.rentPaid && numValue > 0) {
          const basic = validationContext.basic || 0;
          const da = validationContext.da || 0;
          const rentPaid = validationContext.rentPaid || 0;
          const cityCategory = ['Delhi', 'Mumbai', 'Kolkata', 'Chennai'].includes(validationContext.city || '') ? 'metro' : 'non-metro';
          
          const salary = basic + da;
          const cityRate = cityCategory === 'metro' ? TAXATION_LIMITS.HRA_METRO_RATE : TAXATION_LIMITS.HRA_NON_METRO_RATE;
          const maxHRAByCity = salary * cityRate;
          const maxHRAByRent = Math.max(0, rentPaid - (salary * TAXATION_LIMITS.HRA_RENT_EXCESS_PERCENT));
          const maxExemption = Math.min(numValue, maxHRAByCity, maxHRAByRent);
          
          if (maxExemption < numValue) {
            setInfo(`HRA exemption: ₹${maxExemption.toLocaleString('en-IN')}, Taxable: ₹${(numValue - maxExemption).toLocaleString('en-IN')}`);
          } else {
            setInfo(`Fully exempt HRA: ₹${maxExemption.toLocaleString('en-IN')}`);
          }
        }
        break;

      case 'lta_claimed_count':
        if (numValue > TAXATION_LIMITS.LTA_MAX_JOURNEYS) {
          setWarning(`LTA claimed ${numValue} times exceeds limit of ${TAXATION_LIMITS.LTA_MAX_JOURNEYS} times in ${TAXATION_LIMITS.LTA_BLOCK_YEARS} years. Excess claims may not be exempt.`);
        }
        break;

      case 'children_count':
        if (numValue > TAXATION_LIMITS.MAX_CHILDREN_FOR_EDUCATION) {
          setWarning(`Children count exceeds limit of ${TAXATION_LIMITS.MAX_CHILDREN_FOR_EDUCATION} for education allowance. Excess may not be exempt.`);
        }
        break;

      case 'months':
        if (numValue > 12) {
          setWarning('Months exceeds 12. Please verify the period.');
        }
        break;

      case 'percentage':
        if (numValue > 100) {
          setWarning('Percentage exceeds 100%. Please verify if correct.');
        }
        break;

      case 'interest_rate':
        if (numValue > 50) {
          setWarning('Interest rate seems unusually high. Please verify.');
        }
        break;

      case 'loan_amount':
        if (fieldType === 'loan_amount' && numValue <= TAXATION_LIMITS.LOAN_EXEMPTION_LIMIT) {
          setInfo('Loan amount is exempt from perquisite tax');
        } else if (numValue > TAXATION_LIMITS.LOAN_EXEMPTION_LIMIT) {
          setInfo('Loan amount exceeds exemption limit, perquisite value will be calculated');
        }
        break;
    }
  }, [fieldType, validationContext]);

  const validateField = useCallback((inputValue: string | number): void => {
    setWarning('');
    setInfo('');

    const numValue = parseIndianNumber(String(inputValue));

    // Basic amount validation - now shows warnings instead of errors
    const basicValidation = validateAmount(numValue, maxLimit);
    if (basicValidation.warning) {
      setWarning(basicValidation.warning);
      return;
    }

    // Field-specific validation messages
    const validationMessage = getValidationMessage(fieldType, numValue, validationContext);
    if (validationMessage) {
      switch (validationMessage.type) {
        case 'warning':
          setWarning(validationMessage.message);
          break;
        case 'info':
          setInfo(validationMessage.message);
          break;
      }
    }

    // Field-specific validations - now show warnings instead of blocking
    performFieldSpecificValidations(numValue);
  }, [fieldType, maxLimit, validationContext, performFieldSpecificValidations]);

  useEffect(() => {
    if (touched && value !== '') {
      validateField(value);
    }
  }, [value, touched, validateField]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    let inputValue = e.target.value;

    // For numeric fields, sanitize input
    if (fieldType !== 'text' && fieldType !== 'select') {
      // Remove invalid characters but keep decimal point and commas
      inputValue = inputValue.replace(/[^0-9.,]/g, '');
      
      // Prevent multiple decimal points
      const decimalCount = (inputValue.match(/\./g) || []).length;
      if (decimalCount > 1) {
        return;
      }
    }

    onChange(inputValue);
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>): void => {
    setTouched(true);
    
    // Format the value for display
    if (fieldType !== 'text' && fieldType !== 'select' && e.target.value) {
      const numValue = parseIndianNumber(e.target.value);
      if (!isNaN(numValue)) {
        onChange(formatIndianNumber(numValue));
      }
    }
    
    validateField(e.target.value);
  };

  const handleFocusEvent = (e: React.FocusEvent<HTMLInputElement>): void => {
    // Clear formatting on focus for easier editing
    if (fieldType !== 'text' && fieldType !== 'select' && value) {
      const numValue = parseIndianNumber(String(value));
      if (numValue === 0) {
        onChange('');
      } else {
        onChange(numValue.toString());
      }
    }
    
    if (onFocus) {
      onFocus(e);
    }
  };

  // Determine the color and helper text based on validation state
  const getFieldState = (): FieldState => {
    if (warning) {
      return {
        color: 'warning',
        helperTextContent: warning,
        helperTextColor: 'warning'
      };
    } else if (info) {
      return {
        color: 'primary',
        helperTextContent: info,
        helperTextColor: 'info'
      };
    } else if (helperText) {
      return {
        color: 'primary',
        helperTextContent: helperText,
        helperTextColor: 'text.secondary'
      };
    }
    return {
      color: 'primary',
      helperTextContent: '',
      helperTextColor: 'text.secondary'
    };
  };

  const fieldState = getFieldState();

  return (
    <Box sx={sx}>
      <TextField
        fullWidth
        label={label}
        value={value || ''}
        onChange={handleChange}
        onBlur={handleBlur}
        onFocus={handleFocusEvent}
        color={fieldState.color}
        required={required}
        disabled={disabled}
        error={false} // Never show error state, only warnings
        InputProps={{
          startAdornment: (fieldType === 'amount' || fieldType.includes('amount')) ? (
            <InputAdornment position="start">₹</InputAdornment>
          ) : (fieldType === 'percentage') ? (
            <InputAdornment position="end">%</InputAdornment>
          ) : undefined,
        }}
        inputProps={{
          maxLength: fieldType === 'amount' ? 12 : fieldType === 'percentage' ? 5 : fieldType === 'age' ? 3 : undefined,
          pattern: fieldType === 'amount' ? '[0-9,]*' : fieldType === 'percentage' ? '[0-9]*' : undefined
        }}
        {...props}
      />
      
      {fieldState.helperTextContent && (
        <FormHelperText 
          sx={{ 
            color: fieldState.helperTextColor,
            mt: 0.5,
            fontSize: '0.75rem'
          }}
        >
          {fieldState.helperTextContent}
        </FormHelperText>
      )}
      
      {/* Show max limit for amount fields */}
      {(fieldType === 'amount' || fieldType.includes('amount')) && maxLimit !== TAXATION_LIMITS.MAX_SALARY_COMPONENT && (
        <Typography 
          variant="caption" 
          sx={{ 
            color: 'text.secondary',
            display: 'block',
            mt: 0.5
          }}
        >
          Maximum allowed: ₹{maxLimit.toLocaleString('en-IN')}
        </Typography>
      )}
    </Box>
  );
};

export default ValidatedTextField; 