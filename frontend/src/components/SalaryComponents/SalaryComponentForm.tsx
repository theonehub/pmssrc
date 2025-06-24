import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  MenuItem,
  FormControlLabel,
  Switch,
  Divider,
  Alert,
  Grid,
  Card,
  CardContent,
  Chip,
} from '@mui/material';
import { useNavigate, useParams } from 'react-router-dom';
import { 
  useSalaryComponents, 
  useSalaryComponent, 
  useFormulaValidation 
} from '../../shared/hooks/useSalaryComponents';
import { 
  CreateSalaryComponentRequest, 
  UpdateSalaryComponentRequest
} from '../../shared/api/salaryComponentApi';

interface SalaryComponentFormProps {
  mode: 'create' | 'edit';
}

const SalaryComponentForm: React.FC<SalaryComponentFormProps> = ({ mode }) => {
  const navigate = useNavigate();
  const { componentId } = useParams<{ componentId: string }>();
  
  // Get existing component data for edit mode
  const { component, isLoading: isLoadingComponent } = useSalaryComponent(
    mode === 'edit' && componentId ? componentId : ''
  );
  
  const { createComponent, updateComponent, isCreating, isUpdating } = useSalaryComponents();
  const { validateFormula, isValidating } = useFormulaValidation();

  // Form state
  const [code, setCode] = useState('');
  const [name, setName] = useState('');
  const [componentType, setComponentType] = useState<'EARNING' | 'DEDUCTION' | 'REIMBURSEMENT'>('EARNING');
  const [valueType, setValueType] = useState<'FIXED' | 'FORMULA' | 'VARIABLE'>('FIXED');
  const [isTaxable, setIsTaxable] = useState(true);
  const [formula, setFormula] = useState('');
  const [description, setDescription] = useState('');
  const [isActive, setIsActive] = useState(true);

  // Error states
  const [codeError, setCodeError] = useState('');
  const [nameError, setNameError] = useState('');
  const [formulaError, setFormulaError] = useState('');
  const [submitError, setSubmitError] = useState('');
  const [formulaValidation, setFormulaValidation] = useState<any>(null);

  // Component type options
  const componentTypeOptions = [
    { value: 'EARNING', label: 'Earning' },
    { value: 'DEDUCTION', label: 'Deduction' },
    { value: 'REIMBURSEMENT', label: 'Reimbursement' },
  ];

  // Value type options
  const valueTypeOptions = [
    { value: 'FIXED', label: 'Fixed Amount' },
    { value: 'FORMULA', label: 'Formula Based' },
    { value: 'VARIABLE', label: 'Variable' },
  ];

  // Load existing data for edit mode
  useEffect(() => {
    if (mode === 'edit' && component) {
      setCode(component.code || '');
      setName(component.name);
      setComponentType(component.component_type);
      setValueType(component.value_type);
      setIsTaxable(component.is_taxable);
      setFormula(component.formula || '');
      setDescription(component.description || '');
      setIsActive(component.is_active);
    }
  }, [mode, component]);

  // Validation functions
  const validateRequired = (value: string, fieldName: string): string => {
    return !value.trim() ? `${fieldName} is required` : '';
  };

  const validateCode = (value: string): string => {
    if (!value.trim()) return 'Component code is required';
    if (!/^[A-Z0-9_]+$/.test(value)) {
      return 'Code must contain only uppercase letters, numbers, and underscores';
    }
    return '';
  };

  const handleCodeChange = (value: string) => {
    const uppercaseValue = value.toUpperCase();
    setCode(uppercaseValue);
    setCodeError(validateCode(uppercaseValue));
  };

  const handleNameChange = (value: string) => {
    setName(value);
    setNameError(validateRequired(value, 'Component name'));
  };

  const handleFormulaChange = async (value: string) => {
    setFormula(value);
    setFormulaError('');
    setFormulaValidation(null);

    if (valueType === 'FORMULA' && value.trim()) {
      try {
        const validation = await validateFormula({
          formula: value,
          component_type: componentType,
        });
        setFormulaValidation(validation);
        if (!validation.is_valid) {
          setFormulaError(validation.errors?.join(', ') || 'Invalid formula');
        }
      } catch (error: any) {
        setFormulaError(error.message || 'Failed to validate formula');
      }
    }
  };

  // Form validation
  const validateForm = (): boolean => {
    let isValid = true;
    
    const codeErr = validateCode(code);
    setCodeError(codeErr);
    
    const nameErr = validateRequired(name, 'Component name');
    setNameError(nameErr);

    if (codeErr || nameErr) {
      isValid = false;
    }

    if (valueType === 'FORMULA') {
      const formulaErr = validateRequired(formula, 'Formula');
      setFormulaError(formulaErr);
      
      if (formulaErr || (formulaValidation && !formulaValidation.is_valid)) {
        isValid = false;
      }
    }

    return isValid;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError('');
    
    if (!validateForm()) {
      setSubmitError('Please fix the errors above before submitting.');
      return;
    }
    
    try {
      const formData: CreateSalaryComponentRequest | UpdateSalaryComponentRequest = {
        code,
        name,
        component_type: componentType,
        value_type: valueType,
        is_taxable: isTaxable,
        is_active: isActive,
        ...(description && { description }),
        ...(valueType === 'FORMULA' && formula && { formula }),
      };
      
      if (mode === 'create') {
        await createComponent(formData as CreateSalaryComponentRequest);
      } else if (componentId) {
        await updateComponent(componentId, formData as UpdateSalaryComponentRequest);
      }
      
      navigate('/salary-components');
    } catch (error: any) {
      setSubmitError(error.message || 'An error occurred while saving. Please try again.');
    }
  };

  const isLoading = mode === 'edit' ? isLoadingComponent : false;
  const isSubmitting = isCreating || isUpdating;

  if (isLoading) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography>Loading component...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, maxWidth: 800, mx: 'auto' }}>
      {/* Header */}
      <Typography variant="h4" gutterBottom>
        {mode === 'create' ? 'Create Salary Component' : 'Edit Salary Component'}
      </Typography>

      {submitError && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {submitError}
        </Alert>
      )}
      
      <Paper sx={{ p: 3 }}>
        <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          
          {/* Basic Information */}
          <Box>
            <Typography variant="h6" color="primary" gutterBottom>
              Basic Information
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Component Code"
                  value={code}
                  onChange={(e) => handleCodeChange(e.target.value)}
                  error={!!codeError}
                  helperText={codeError || "Unique identifier (e.g., BASIC_SALARY, HRA)"}
                  required
                  placeholder="e.g., BASIC_SALARY, HRA"
                  disabled={mode === 'edit'}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Component Name"
                  value={name}
                  onChange={(e) => handleNameChange(e.target.value)}
                  error={!!nameError}
                  helperText={nameError}
                  required
                  placeholder="e.g., Basic Salary, HRA, etc."
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <TextField
                  select
                  fullWidth
                  label="Component Type"
                  value={componentType}
                  onChange={(e) => setComponentType(e.target.value as any)}
                  required
                >
                  {componentTypeOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <TextField
                  select
                  fullWidth
                  label="Value Type"
                  value={valueType}
                  onChange={(e) => setValueType(e.target.value as any)}
                  required
                >
                  {valueTypeOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={isTaxable}
                        onChange={(e) => setIsTaxable(e.target.checked)}
                      />
                    }
                    label="Taxable Component"
                  />
                  <FormControlLabel
                    control={
                      <Switch
                        checked={isActive}
                        onChange={(e) => setIsActive(e.target.checked)}
                      />
                    }
                    label="Active Component"
                  />
                </Box>
              </Grid>
            </Grid>
            
            <TextField
              fullWidth
              label="Description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              multiline
              rows={3}
              placeholder="Brief description of the salary component..."
              sx={{ mt: 2 }}
            />
          </Box>

          {/* Calculation Method */}
          <Box>
            <Typography variant="h6" color="primary" gutterBottom>
              Calculation Method
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            {valueType === 'FORMULA' && (
              <Box sx={{ mt: 2 }}>
                <TextField
                  fullWidth
                  label="Formula"
                  value={formula}
                  onChange={(e) => handleFormulaChange(e.target.value)}
                  error={!!formulaError}
                  helperText={formulaError || "e.g., basic_salary * 0.1, basic_salary + da"}
                  required={valueType === 'FORMULA'}
                  multiline
                  rows={3}
                  placeholder="Enter calculation formula..."
                />
                
                {isValidating && (
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="body2" color="info.main">
                      Validating formula...
                    </Typography>
                  </Box>
                )}
                
                {formulaValidation && (
                  <Card sx={{ mt: 2 }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <Typography variant="subtitle2">Formula Validation:</Typography>
                        <Chip
                          label={formulaValidation.is_valid ? 'Valid' : 'Invalid'}
                          color={formulaValidation.is_valid ? 'success' : 'error'}
                          size="small"
                        />
                      </Box>
                      
                      {formulaValidation.parsed_formula && (
                        <Typography variant="body2" sx={{ mb: 1 }}>
                          <strong>Parsed:</strong> {formulaValidation.parsed_formula}
                        </Typography>
                      )}
                      
                      {formulaValidation.errors && formulaValidation.errors.length > 0 && (
                        <Box sx={{ mb: 1 }}>
                          <Typography variant="body2" color="error">
                            <strong>Errors:</strong>
                          </Typography>
                          <ul style={{ margin: 0, paddingLeft: 16 }}>
                            {formulaValidation.errors.map((error: string, index: number) => (
                              <li key={index}>
                                <Typography variant="body2" color="error">
                                  {error}
                                </Typography>
                              </li>
                            ))}
                          </ul>
                        </Box>
                      )}
                      
                      {formulaValidation.warnings && formulaValidation.warnings.length > 0 && (
                        <Box>
                          <Typography variant="body2" color="warning.main">
                            <strong>Warnings:</strong>
                          </Typography>
                          <ul style={{ margin: 0, paddingLeft: 16 }}>
                            {formulaValidation.warnings.map((warning: string, index: number) => (
                              <li key={index}>
                                <Typography variant="body2" color="warning.main">
                                  {warning}
                                </Typography>
                              </li>
                            ))}
                          </ul>
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                )}
              </Box>
            )}
            
            {valueType !== 'FORMULA' && (
              <Alert severity="info" sx={{ mt: 2 }}>
                This component will use {valueType === 'FIXED' ? 'fixed amounts' : 'variable amounts'} that can be set individually for each employee.
              </Alert>
            )}
          </Box>

          {/* Action Buttons */}
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 3 }}>
            <Button
              variant="outlined"
              onClick={() => navigate('/salary-components')}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="contained"
              disabled={isSubmitting}
            >
              {isSubmitting 
                ? (mode === 'create' ? 'Creating...' : 'Updating...')
                : (mode === 'create' ? 'Create Component' : 'Update Component')
              }
            </Button>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

export default SalaryComponentForm; 