import React, { useState, useCallback, useEffect } from 'react';
import {
  TextField,
  TextFieldProps,
  InputAdornment,
  FormHelperText,
  Box,
  Chip
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { formatCurrencyInput, parseCurrencyInput } from '../../../shared/utils/formatting';
import { validators } from '../../../shared/utils/validation';

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const StyledTextField = styled(TextField)(({ theme }) => ({
  '& .MuiOutlinedInput-root': {
    borderRadius: 8,
    
    // Mobile-friendly sizing
    '@media (max-width: 768px)': {
      fontSize: '16px', // Prevents zoom on iOS
      minHeight: '48px',
    },
    
    '&.Mui-focused': {
      '& .MuiOutlinedInput-notchedOutline': {
        borderColor: theme.palette.primary.main,
        borderWidth: 2,
      },
    },
    
    '&.Mui-error': {
      '& .MuiOutlinedInput-notchedOutline': {
        borderColor: theme.palette.error.main,
      },
    },
    
    '&.success': {
      '& .MuiOutlinedInput-notchedOutline': {
        borderColor: theme.palette.success.main,
      },
    },
  },
  
  '& .MuiInputLabel-root': {
    fontSize: '1rem',
    
    '@media (max-width: 768px)': {
      fontSize: '1rem',
    },
  },
}));

const SuggestionChip = styled(Chip)(({ theme }) => ({
  margin: theme.spacing(0.5),
  fontSize: '0.75rem',
  height: 24,
  
  '&:hover': {
    backgroundColor: theme.palette.primary.light,
    color: theme.palette.primary.contrastText,
  },
}));

// =============================================================================
// COMPONENT INTERFACES
// =============================================================================

interface BaseInputProps extends Omit<TextFieldProps, 'variant' | 'type'> {
  variant?: 'outlined' | 'filled' | 'standard';
  validationState?: 'default' | 'error' | 'success' | 'warning';
  helperText?: string;
  maxLength?: number;
  showCharCount?: boolean;
  mobile?: boolean;
}

interface CurrencyInputProps extends BaseInputProps {
  type: 'currency';
  onValueChange?: (value: number) => void;
  max?: number;
  min?: number;
  suggestions?: number[];
}

interface NumberInputProps extends BaseInputProps {
  type: 'number';
  onValueChange?: (value: number) => void;
  max?: number;
  min?: number;
  step?: number;
  decimalPlaces?: number;
}

interface TextInputProps extends BaseInputProps {
  type?: 'text' | 'email' | 'tel' | 'url' | 'password';
  onValueChange?: (value: string) => void;
  suggestions?: string[];
  autoComplete?: string;
}

interface PercentageInputProps extends BaseInputProps {
  type: 'percentage';
  onValueChange?: (value: number) => void;
  max?: number;
  min?: number;
}

export type InputProps = CurrencyInputProps | NumberInputProps | TextInputProps | PercentageInputProps;

// =============================================================================
// MAIN INPUT COMPONENT
// =============================================================================

export const Input: React.FC<InputProps> = (props) => {
  const {
    type = 'text',
    value: externalValue,
    onChange,
    onValueChange,
    validationState = 'default',
    helperText,
    maxLength,
    showCharCount = false,
    mobile = false,
    error,
    ...textFieldProps
  } = props;

  const [internalValue, setInternalValue] = useState<string>('');
  const [validationError, setValidationError] = useState<string>('');
  const [showSuggestions, setShowSuggestions] = useState(false);

  // Initialize internal value
  useEffect(() => {
    if (externalValue !== undefined) {
      if (type === 'currency') {
        setInternalValue(typeof externalValue === 'number' ? externalValue.toString() : String(externalValue));
      } else {
        setInternalValue(String(externalValue || ''));
      }
    }
  }, [externalValue, type]);

  // =============================================================================
  // VALIDATION
  // =============================================================================

  const validateInput = useCallback((val: string) => {
    if (!val) {
      setValidationError('');
      return;
    }

    switch (type) {
      case 'currency':
        const currencyResult = validators.currency(val);
        if (!currencyResult.isValid) {
          setValidationError(currencyResult.message || 'Invalid currency amount');
        } else {
          setValidationError('');
        }
        break;
      
      case 'number':
      case 'percentage':
        const numValue = parseFloat(val);
        if (isNaN(numValue)) {
          setValidationError('Please enter a valid number');
        } else {
          const min = (props as NumberInputProps | PercentageInputProps).min;
          const max = (props as NumberInputProps | PercentageInputProps).max;
          
          if (min !== undefined && numValue < min) {
            setValidationError(`Value must be at least ${min}`);
          } else if (max !== undefined && numValue > max) {
            setValidationError(`Value must not exceed ${max}`);
          } else {
            setValidationError('');
          }
        }
        break;
      
      case 'email':
        const emailResult = validators.required()(val); // We can expand this with email validation
        if (!emailResult.isValid) {
          setValidationError(emailResult.message || 'Invalid email address');
        } else {
          setValidationError('');
        }
        break;
      
      default:
        setValidationError('');
    }
  }, [type, props]);

  // =============================================================================
  // CHANGE HANDLERS
  // =============================================================================

  const handleChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    let newValue = event.target.value;

    // Apply maxLength
    if (maxLength && newValue.length > maxLength) {
      newValue = newValue.slice(0, maxLength);
    }

    // Format based on type
    if (type === 'currency') {
      newValue = formatCurrencyInput(newValue);
    } else if (type === 'percentage') {
      // Remove % symbol if entered
      newValue = newValue.replace('%', '');
    }

    setInternalValue(newValue);
    validateInput(newValue);

    // Call external handlers
    if (onChange) {
      const syntheticEvent = {
        ...event,
        target: { ...event.target, value: newValue }
      };
      onChange(syntheticEvent);
    }

    if (onValueChange) {
      if (type === 'currency') {
        const numericValue = parseCurrencyInput(newValue);
        (onValueChange as (value: number) => void)(numericValue);
      } else if (type === 'number' || type === 'percentage') {
        const numericValue = parseFloat(newValue) || 0;
        (onValueChange as (value: number) => void)(numericValue);
      } else {
        (onValueChange as (value: string) => void)(newValue);
      }
    }
  }, [maxLength, type, onChange, onValueChange, validateInput]);

  // =============================================================================
  // SUGGESTION HANDLERS
  // =============================================================================

  const handleSuggestionClick = useCallback((suggestion: string | number) => {
    const suggestionValue = String(suggestion);
    setInternalValue(suggestionValue);
    setShowSuggestions(false);
    
    if (onValueChange) {
      if (type === 'currency' || type === 'number' || type === 'percentage') {
        (onValueChange as (value: number) => void)(Number(suggestion));
      } else {
        (onValueChange as (value: string) => void)(suggestionValue);
      }
    }
  }, [onValueChange, type]);

  // =============================================================================
  // RENDER HELPERS
  // =============================================================================

  const getInputAdornments = () => {
    const startAdornment = type === 'currency' ? (
      <InputAdornment position="start">₹</InputAdornment>
    ) : undefined;

    const endAdornment = type === 'percentage' ? (
      <InputAdornment position="end">%</InputAdornment>
    ) : undefined;

    return { startAdornment, endAdornment };
  };

  const renderSuggestions = () => {
    const suggestions = (props as CurrencyInputProps | TextInputProps).suggestions;
    
    if (!suggestions || !showSuggestions) return null;

    return (
      <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
        {suggestions.map((suggestion, index) => (
          <SuggestionChip
            key={index}
            label={type === 'currency' ? `₹${suggestion.toLocaleString()}` : suggestion}
            onClick={() => handleSuggestionClick(suggestion)}
            size="small"
            variant="outlined"
          />
        ))}
      </Box>
    );
  };

  const renderHelperText = () => {
    const errorText = error || validationError;
    const helpText = errorText || helperText;
    const charCount = showCharCount && maxLength ? `${internalValue.length}/${maxLength}` : '';
    
    if (!helpText && !charCount) return null;

    return (
      <FormHelperText error={!!errorText}>
        {helpText}
        {charCount && (
          <Box component="span" sx={{ float: 'right' }}>
            {charCount}
          </Box>
        )}
      </FormHelperText>
    );
  };

  // =============================================================================
  // COMPONENT PROPS
  // =============================================================================

  const { startAdornment, endAdornment } = getInputAdornments();
  const isError = !!error || !!validationError || validationState === 'error';
  const isSuccess = validationState === 'success' && !isError;

  return (
    <Box>
      <StyledTextField
        {...textFieldProps}
        value={internalValue}
        onChange={handleChange}
        onFocus={() => setShowSuggestions(true)}
        onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
        error={isError}
        className={isSuccess ? 'success' : ''}
        variant="outlined"
        fullWidth
        InputProps={{
          startAdornment,
          endAdornment,
          inputMode: type === 'currency' || type === 'number' || type === 'percentage' ? 'numeric' : 'text',
          ...textFieldProps.InputProps,
        }}
        inputProps={{
          maxLength,
          style: { fontSize: mobile ? '16px' : '14px' },
          ...textFieldProps.inputProps,
        }}
      />
      {renderHelperText()}
      {renderSuggestions()}
    </Box>
  );
};

// =============================================================================
// SPECIALIZED INPUT COMPONENTS
// =============================================================================

export const CurrencyInput: React.FC<Omit<CurrencyInputProps, 'type'>> = (props) => (
  <Input type="currency" {...props} />
);

export const NumberInput: React.FC<Omit<NumberInputProps, 'type'>> = (props) => (
  <Input type="number" {...props} />
);

export const PercentageInput: React.FC<Omit<PercentageInputProps, 'type'>> = (props) => (
  <Input type="percentage" {...props} />
);

export const TextInput: React.FC<Omit<TextInputProps, 'type'>> = (props) => (
  <Input type="text" {...props} />
);

export default Input; 