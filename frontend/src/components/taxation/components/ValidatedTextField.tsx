import React, { useState, useEffect, useCallback } from 'react';
import {
  TextField,
  FormHelperText,
  InputAdornment,
  Box,
  Typography,
  TextFieldProps,
  IconButton,
  Tooltip
} from '@mui/material';
import { Calculate as CalculatorIcon } from '@mui/icons-material';
import { 
  validateAmount, 
  getValidationMessage,
  TAXATION_LIMITS 
} from '../utils/validationRules';
import { 
  formatIndianNumber, 
  parseIndianNumber,
  evaluateCalculatorExpression,
  isCalculatorExpression,
  validateCalculatorExpression
} from '../utils/taxationUtils';
import type { 
  CalculatorEvaluationResult, 
  CalculatorValidationResult 
} from '../utils/calculatorTypes';

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
  // Only log if value is a calculator expression
  if (typeof value === 'string' && value.startsWith('=')) {
    console.log('🔄 ValidatedTextField render with calculator expression:', { label, value });
  }
  
  const [touched, setTouched] = useState<boolean>(false);
  const [warning, setWarning] = useState<string>('');
  const [info, setInfo] = useState<string>('');
  const [isCalculating, setIsCalculating] = useState<boolean>(false);
  const [calculatorError, setCalculatorError] = useState<string>('');
  const [showCalculatorIcon, setShowCalculatorIcon] = useState<boolean>(false);

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
    setCalculatorError('');

    // Handle calculator expressions
    if (isCalculatorExpression(String(inputValue))) {
      const validation = validateCalculatorExpression(String(inputValue)) as CalculatorValidationResult;
      if (!validation.isValid) {
        setCalculatorError(validation.message);
        return;
      }
      
      const evaluation = evaluateCalculatorExpression(String(inputValue)) as CalculatorEvaluationResult;
      if (!evaluation.isValid) {
        setCalculatorError(evaluation.error || 'Invalid calculation');
        return;
      }
      
      // Use the calculated result for further validation
      const numValue = evaluation.result;
      setInfo(`Calculated: ${formatIndianNumber(numValue)}`);
      
      // Continue with normal validation using the calculated value
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
            // Don't override calculation info with field info
            if (!info.startsWith('Calculated:')) {
              setInfo(validationMessage.message);
            }
            break;
        }
      }

      // Field-specific validations
      performFieldSpecificValidations(numValue);
      return;
    }

    // Handle regular numeric values
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
  }, [fieldType, maxLimit, validationContext, performFieldSpecificValidations, info]);

  useEffect(() => {
    if (touched && value !== '') {
      validateField(value);
    }
  }, [value, touched, validateField]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    let inputValue = e.target.value;
    
    // Special handling for calculator expressions
    // If user types '=' at the beginning or after existing content, start fresh with '='
    if (inputValue.includes('=')) {
      const equalsIndex = inputValue.indexOf('=');
      if (equalsIndex === 0) {
        // User typed '=' at the beginning, keep as is
        // inputValue remains the same
      } else {
        // User typed '=' after existing content (like "0="), start fresh with just the '=' part
        inputValue = '=' + inputValue.substring(equalsIndex + 1);
      }
      
      setIsCalculating(true);
      setShowCalculatorIcon(true);
      console.log('🧮 Calculator mode activated in ValidatedTextField:', { label, inputValue });
      onChange(inputValue);
      return;
    }
    
    // If we were in calculator mode but user removed the '=', exit calculator mode
    if (isCalculating && !inputValue.startsWith('=')) {
      setIsCalculating(false);
      setShowCalculatorIcon(false);
      setCalculatorError('');
    }

    // Handle invalid arithmetic without '=' prefix
    if (fieldType !== 'text' && fieldType !== 'select') {
      // Check for arithmetic operators without '=' prefix
      const hasArithmetic = /[+\-*/]/.test(inputValue) && !inputValue.startsWith('=');
      if (hasArithmetic) {
        setCalculatorError('Invalid arithmetic without \'=\' prefix. Use = to start calculations (e.g., =10000*10)');
        console.log('❌ Invalid arithmetic detected in ValidatedTextField:', { label, inputValue });
        return;
      }
    }

    // For non-text fields, ensure numeric input (unless it's a calculator expression)
    if (fieldType !== 'text' && fieldType !== 'select' && !inputValue.startsWith('=')) {
      // Allow empty string, numbers, commas, and decimal points
      const numericPattern = /^[0-9,.\s]*$/;
      if (inputValue && !numericPattern.test(inputValue)) {
        return;
      }
    }

    onChange(inputValue);
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>): void => {
    setTouched(true);
    
    const inputValue = e.target.value;
    
    // Handle calculator expressions
    if (isCalculatorExpression(inputValue)) {
      const evaluation = evaluateCalculatorExpression(inputValue) as CalculatorEvaluationResult;
      if (evaluation.isValid) {
        // Replace the expression with the calculated result
        const formattedResult = formatIndianNumber(evaluation.result);
        onChange(formattedResult);
        setIsCalculating(false);
        setShowCalculatorIcon(false);
        setCalculatorError('');
        setInfo(`Calculated from: ${inputValue}`);
        
        // Validate the calculated result
        validateField(evaluation.result);
        return;
      } else {
        setCalculatorError(evaluation.error || 'Invalid calculation');
        return;
      }
    }
    
    // Format the value for display (existing logic)
    if (fieldType !== 'text' && fieldType !== 'select' && inputValue) {
      const numValue = parseIndianNumber(inputValue);
      if (!isNaN(numValue)) {
        onChange(formatIndianNumber(numValue));
      }
    }
    
    validateField(inputValue);
  };

  const handleFocusEvent = (e: React.FocusEvent<HTMLInputElement>): void => {
    setTouched(true);
    
    // Clear field if it contains just "0" or "₹0" to make it easier to type calculator expressions
    const currentValue = e.target.value;
    if (currentValue === '0' || currentValue === '₹0' || currentValue === '0.00' || currentValue === '₹0.00') {
      // Clear the field by calling onChange with empty string
      onChange('');
      // Also clear the input field directly
      e.target.value = '';
    }
    
    if (onFocus) {
      onFocus(e);
    }
  };

  // Determine the color and helper text based on validation state
  const getFieldState = (): FieldState => {
    if (calculatorError) {
      return {
        color: 'warning',
        helperTextContent: calculatorError,
        helperTextColor: 'error'
      };
    } else if (warning) {
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
        error={!!calculatorError} // Show error state for calculator errors
        InputProps={{
          startAdornment: (fieldType === 'amount' || fieldType.includes('amount')) ? (
            <InputAdornment position="start">₹</InputAdornment>
          ) : undefined,
          endAdornment: (() => {
            // Calculator icon for amount fields when in calculator mode
            if ((fieldType === 'amount' || fieldType.includes('amount')) && showCalculatorIcon) {
              return (
                <InputAdornment position="end">
                  <Tooltip title="Calculator mode active. Use = to start calculations (e.g., =10000*10)">
                    <IconButton edge="end" size="small" disabled>
                      <CalculatorIcon fontSize="small" color={isCalculating ? 'primary' : 'disabled'} />
                    </IconButton>
                  </Tooltip>
                </InputAdornment>
              );
            }
            // Percentage symbol for percentage fields
            if (fieldType === 'percentage') {
              return <InputAdornment position="end">%</InputAdornment>;
            }
            return undefined;
          })(),
        }}
        inputProps={{
          maxLength: fieldType === 'amount' ? 20 : fieldType === 'percentage' ? 5 : fieldType === 'age' ? 3 : undefined, // Increased for calculator expressions
          pattern: fieldType === 'amount' ? '[0-9,=+\\-*/()]*' : fieldType === 'percentage' ? '[0-9]*' : undefined
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

      {/* Show calculator usage hint for amount fields */}
      {(fieldType === 'amount' || fieldType.includes('amount')) && !fieldState.helperTextContent && !isCalculating && (
        <Typography 
          variant="caption" 
          sx={{ 
            color: 'text.secondary',
            display: 'block',
            mt: 0.5
          }}
        >
          Tip: Use = for calculations (e.g., =10000*10, =50000+25000)
        </Typography>
      )}
    </Box>
  );
};

export default ValidatedTextField; 