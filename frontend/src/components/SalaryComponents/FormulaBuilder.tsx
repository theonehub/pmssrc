import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  Card,
  CardContent,
  Chip,
  Alert,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  MenuItem,
} from '@mui/material';
import {
  Functions as FunctionsIcon,
  PlayArrow as TestIcon,
  Code as CodeIcon,
} from '@mui/icons-material';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { 
  useFormulaValidation, 
  useSalaryComponent, 
  useCalculationTest,
  useSalaryComponents 
} from '../../shared/hooks/useSalaryComponents';

// Common formula examples
const FORMULA_EXAMPLES = [
  {
    name: 'HRA (House Rent Allowance)',
    formula: 'basic_salary * 0.4',
    description: '40% of basic salary',
  },
  {
    name: 'Dearness Allowance',
    formula: 'basic_salary * 0.12',
    description: '12% of basic salary',
  },
  {
    name: 'Transport Allowance',
    formula: 'min(1600, actual_transport_cost)',
    description: 'Minimum of 1600 or actual transport cost',
  },
  {
    name: 'Professional Tax',
    formula: 'if(gross_salary > 10000, 200, if(gross_salary > 8500, 150, 0))',
    description: 'Conditional professional tax based on gross salary',
  },
  {
    name: 'EPF Contribution',
    formula: 'min(basic_salary * 0.12, 1800)',
    description: '12% of basic salary, capped at 1800',
  },
];

const AVAILABLE_VARIABLES = [
  'basic_salary',
  'da',
  'hra',
  'special_allowance',
  'gross_salary',
  'transport_allowance',
  'medical_allowance',
  'other_allowances',
  'years_of_service',
  'designation_level',
];

const FormulaBuilder: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const componentId = searchParams.get('component');
  
  const { component } = useSalaryComponent(componentId || '');
  const { validateFormula, isValidating } = useFormulaValidation();
  const { testCalculation, isCalculating } = useCalculationTest();
  const { updateComponent } = useSalaryComponents();

  // Formula state
  const [formula, setFormula] = useState('');
  const [componentType, setComponentType] = useState<'EARNING' | 'DEDUCTION' | 'REIMBURSEMENT'>('EARNING');
  const [testEmployeeId, setTestEmployeeId] = useState('');
  
  // Results state
  const [validationResult, setValidationResult] = useState<any>(null);
  const [testResult, setTestResult] = useState<any>(null);
  const [error, setError] = useState('');

  // Load existing component data
  useEffect(() => {
    if (component) {
      setFormula(component.formula || '');
      setComponentType(component.component_type);
    }
  }, [component]);

  const handleFormulaChange = (value: string) => {
    setFormula(value);
    setValidationResult(null);
    setError('');
  };

  const handleValidateFormula = async () => {
    if (!formula.trim()) {
      setError('Please enter a formula to validate');
      return;
    }

    try {
      const result = await validateFormula({
        formula,
        component_type: componentType,
      });
      setValidationResult(result);
      setError('');
    } catch (error: any) {
      setError(error.message || 'Failed to validate formula');
    }
  };

  const handleTestCalculation = async () => {
    if (!componentId || !testEmployeeId) {
      setError('Please select an employee and ensure component is saved');
      return;
    }

    try {
      const result = await testCalculation(testEmployeeId, componentId);
      setTestResult(result);
      setError('');
    } catch (error: any) {
      setError(error.message || 'Failed to test calculation');
    }
  };

  const handleSaveFormula = async () => {
    if (!componentId || !validationResult?.is_valid) {
      setError('Please validate the formula first');
      return;
    }

    try {
      await updateComponent(componentId, { formula });
      navigate('/salary-components');
    } catch (error: any) {
      setError(error.message || 'Failed to save formula');
    }
  };

  const insertVariable = (variable: string) => {
    const textarea = document.querySelector('textarea[name="formula"]') as HTMLTextAreaElement;
    if (textarea) {
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const newFormula = formula.substring(0, start) + variable + formula.substring(end);
      setFormula(newFormula);
      
      // Reset cursor position
      setTimeout(() => {
        textarea.setSelectionRange(start + variable.length, start + variable.length);
        textarea.focus();
      }, 0);
    }
  };

  const insertExample = (exampleFormula: string) => {
    setFormula(exampleFormula);
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <FunctionsIcon sx={{ mr: 2, fontSize: 32 }} color="primary" />
        <Typography variant="h4">
          Formula Builder
          {component && (
            <Typography variant="subtitle1" color="text.secondary">
              for {component.name}
            </Typography>
          )}
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Formula Editor */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Formula Editor
            </Typography>
            
            <TextField
              select
              fullWidth
              label="Component Type"
              value={componentType}
              onChange={(e) => setComponentType(e.target.value as any)}
              sx={{ mb: 2 }}
            >
              <MenuItem value="EARNING">Earning</MenuItem>
              <MenuItem value="DEDUCTION">Deduction</MenuItem>
              <MenuItem value="REIMBURSEMENT">Reimbursement</MenuItem>
            </TextField>

            <TextField
              fullWidth
              name="formula"
              label="Formula"
              value={formula}
              onChange={(e) => handleFormulaChange(e.target.value)}
              multiline
              rows={6}
              placeholder="Enter your formula here... e.g., basic_salary * 0.1"
              sx={{ mb: 2 }}
            />

            <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
              <Button
                variant="outlined"
                onClick={handleValidateFormula}
                disabled={isValidating}
                startIcon={<CodeIcon />}
              >
                {isValidating ? 'Validating...' : 'Validate Formula'}
              </Button>
              
              {componentId && (
                <Button
                  variant="outlined"
                  onClick={handleTestCalculation}
                  disabled={isCalculating || !testEmployeeId}
                  startIcon={<TestIcon />}
                >
                  {isCalculating ? 'Testing...' : 'Test Calculation'}
                </Button>
              )}
              
              {validationResult?.is_valid && componentId && (
                <Button
                  variant="contained"
                  onClick={handleSaveFormula}
                >
                  Save Formula
                </Button>
              )}
            </Box>

            {/* Test Employee Selection */}
            {componentId && (
              <TextField
                fullWidth
                label="Test Employee ID"
                value={testEmployeeId}
                onChange={(e) => setTestEmployeeId(e.target.value)}
                placeholder="Enter employee ID to test calculation"
                sx={{ mb: 2 }}
              />
            )}

            {/* Validation Results */}
            {validationResult && (
              <Card sx={{ mb: 3 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    <Typography variant="h6">Validation Result:</Typography>
                    <Chip
                      label={validationResult.is_valid ? 'Valid' : 'Invalid'}
                      color={validationResult.is_valid ? 'success' : 'error'}
                    />
                  </Box>
                  
                  {validationResult.parsed_formula && (
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      <strong>Parsed Formula:</strong> {validationResult.parsed_formula}
                    </Typography>
                  )}
                  
                  {validationResult.errors && validationResult.errors.length > 0 && (
                    <Alert severity="error" sx={{ mb: 1 }}>
                      <strong>Errors:</strong>
                      <ul style={{ margin: 0, paddingLeft: 16 }}>
                        {validationResult.errors.map((error: string, index: number) => (
                          <li key={index}>{error}</li>
                        ))}
                      </ul>
                    </Alert>
                  )}
                  
                  {validationResult.warnings && validationResult.warnings.length > 0 && (
                    <Alert severity="warning">
                      <strong>Warnings:</strong>
                      <ul style={{ margin: 0, paddingLeft: 16 }}>
                        {validationResult.warnings.map((warning: string, index: number) => (
                          <li key={index}>{warning}</li>
                        ))}
                      </ul>
                    </Alert>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Test Results */}
            {testResult && (
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Test Calculation Result
                  </Typography>
                  <Typography variant="h4" color="primary" gutterBottom>
                    ₹{testResult.calculated_amount.toLocaleString()}
                  </Typography>
                  {testResult.details && (
                    <pre style={{ backgroundColor: '#f5f5f5', padding: 8, borderRadius: 4, fontSize: 12 }}>
                      {JSON.stringify(testResult.details, null, 2)}
                    </pre>
                  )}
                </CardContent>
              </Card>
            )}
          </Paper>
        </Grid>

        {/* Sidebar with Variables and Examples */}
        <Grid item xs={12} md={4}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            {/* Available Variables */}
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Available Variables
              </Typography>
              <List dense>
                {AVAILABLE_VARIABLES.map((variable) => (
                  <ListItem key={variable} disablePadding>
                    <ListItemButton onClick={() => insertVariable(variable)}>
                      <ListItemText 
                        primary={variable}
                        primaryTypographyProps={{ variant: 'body2', fontFamily: 'monospace' }}
                      />
                    </ListItemButton>
                  </ListItem>
                ))}
              </List>
            </Paper>

            {/* Formula Examples */}
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Formula Examples
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                {FORMULA_EXAMPLES.map((example, index) => (
                  <Card key={index} variant="outlined">
                    <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                      <Typography variant="subtitle2" gutterBottom>
                        {example.name}
                      </Typography>
                      <Typography 
                        variant="body2" 
                        sx={{ fontFamily: 'monospace', mb: 1, backgroundColor: '#f5f5f5', p: 1, borderRadius: 1 }}
                      >
                        {example.formula}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {example.description}
                      </Typography>
                      <Button
                        size="small"
                        onClick={() => insertExample(example.formula)}
                        sx={{ mt: 1 }}
                      >
                        Use This
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </Box>
            </Paper>

            {/* Formula Syntax Help */}
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Syntax Help
              </Typography>
              <Typography variant="body2" component="div">
                <strong>Operators:</strong>
                <ul style={{ margin: '4px 0', paddingLeft: 16 }}>
                  <li>+, -, *, / (basic math)</li>
                  <li>min(a, b) - minimum value</li>
                  <li>max(a, b) - maximum value</li>
                  <li>if(condition, true_value, false_value)</li>
                  <li>&gt;, &lt;, &gt;=, &lt;=, == (comparisons)</li>
                </ul>
                
                <strong>Examples:</strong>
                <ul style={{ margin: '4px 0', paddingLeft: 16 }}>
                  <li>basic_salary * 0.4</li>
                  <li>min(1600, transport_allowance)</li>
                  <li>if(years_of_service &gt; 5, basic_salary * 0.1, 0)</li>
                </ul>
              </Typography>
            </Paper>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

export default FormulaBuilder; 