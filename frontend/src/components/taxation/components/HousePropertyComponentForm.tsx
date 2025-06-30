import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  Snackbar,
  Stepper,
  Step,
  StepLabel,
  StepContent
} from '@mui/material';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { ArrowBack as ArrowBackIcon, Save as SaveIcon } from '@mui/icons-material';
import { getUserRole } from '../../../shared/utils/auth';
import taxationApi from '../../../shared/api/taxationApi';
import { CURRENT_TAX_YEAR } from '../../../shared/constants/taxation';
import { UserRole } from '../../../shared/types';

interface HousePropertyComponentData {
  property_type: string;
  address: string;
  annual_rent_received: number;
  municipal_taxes_paid: number;
  home_loan_interest: number;
  pre_construction_interest: number;
}

interface ToastState {
  show: boolean;
  message: string;
  severity: 'success' | 'error' | 'warning' | 'info';
}

interface BaseField {
  name: string;
  label: string;
  type: string;
}

interface NumberField extends BaseField {
  type: 'number';
}

interface TextInputField extends BaseField {
  type: 'text';
}

interface SelectField extends BaseField {
  type: 'select';
  options: { value: string; label: string; }[];
}

type FormField = NumberField | TextInputField | SelectField;

interface StepConfig {
  label: string;
  fields: FormField[];
  description?: string;
}

const isSelectField = (field: FormField): field is SelectField => {
  return field.type === 'select';
};

const isTextField = (field: FormField): field is TextInputField => {
  return field.type === 'text';
};

// Initial data structure
const initialHousePropertyData: HousePropertyComponentData = {
  property_type: 'Self-Occupied',
  address: '',
  annual_rent_received: 0,
  municipal_taxes_paid: 0,
  home_loan_interest: 0,
  pre_construction_interest: 0
};

// Function to flatten nested backend response to flat frontend structure
const flattenHousePropertyData = (nestedData: any): HousePropertyComponentData => {
  console.log('Flattening house property data:', nestedData);
  const flattened: HousePropertyComponentData = { ...initialHousePropertyData };
  
  try {
    if (nestedData) {
      flattened.property_type = nestedData.property_type || 'Self-Occupied';
      flattened.address = nestedData.address || '';
      flattened.annual_rent_received = nestedData.annual_rent_received || 0;
      flattened.municipal_taxes_paid = nestedData.municipal_taxes_paid || 0;
      flattened.home_loan_interest = nestedData.home_loan_interest || 0;
      flattened.pre_construction_interest = nestedData.pre_construction_interest || 0;
    }
  } catch (error) {
    console.error('Error flattening house property data:', error);
  }
  
  return flattened;
};

const steps: StepConfig[] = [
  {
    label: 'Property Details',
    description: 'Basic property information and type',
    fields: [
      { name: 'property_type', label: 'Property Type', type: 'select', options: [
        { value: 'Self-Occupied', label: 'Self-Occupied' },
        { value: 'Let-Out', label: 'Let-Out' }
      ]} as SelectField,
      { name: 'address', label: 'Property Address', type: 'text' } as TextInputField
    ]
  },
  {
    label: 'Income & Expenses',
    description: 'Rental income and property expenses',
    fields: [
      { name: 'annual_rent_received', label: 'Annual Rent Received', type: 'number' } as NumberField,
      { name: 'municipal_taxes_paid', label: 'Municipal Taxes Paid', type: 'number' } as NumberField
    ]
  },
  {
    label: 'Loan Interest',
    description: 'Home loan interest deductions',
    fields: [
      { name: 'home_loan_interest', label: 'Home Loan Interest', type: 'number' } as NumberField,
      { name: 'pre_construction_interest', label: 'Pre-construction Interest', type: 'number' } as NumberField
    ]
  }
];

const HousePropertyComponentForm: React.FC = () => {
  const { empId } = useParams<{ empId: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState<HousePropertyComponentData>(initialHousePropertyData);
  const [loading, setLoading] = useState<boolean>(false);
  const [saving, setSaving] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<ToastState>({ show: false, message: '', severity: 'success' });
  const [activeStep, setActiveStep] = useState<number>(0);
  
  const taxYear = searchParams.get('year') || CURRENT_TAX_YEAR;
  const mode = searchParams.get('mode') || 'update';
  const userRole: UserRole | null = getUserRole();
  const isAdmin = userRole === 'admin' || userRole === 'superadmin';
  const isNewRevision = mode === 'new';

  // Redirect non-admin users
  useEffect(() => {
    if (!isAdmin) {
      navigate('/taxation');
    }
  }, [isAdmin, navigate]);

  // Load existing data
  const loadHousePropertyData = useCallback(async (): Promise<void> => {
    if (!empId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      console.log(`Loading house property data for employee ${empId} for tax year ${taxYear}`);
      const response = await taxationApi.getComponent(empId, taxYear, 'house_property_income');
      console.log('House property API response:', response);
      
      const componentData = response?.component_data || response;
      console.log('Component data:', componentData);
      
      if (componentData) {
        const flattenedData = flattenHousePropertyData(componentData);
        console.log('Flattened house property data:', flattenedData);
        setFormData(flattenedData);
        showToast('House property data loaded successfully', 'success');
      } else {
        console.log('No existing house property data found, using defaults');
        setFormData(initialHousePropertyData);
        showToast('No existing house property data found', 'info');
      }
    } catch (error) {
      console.error('Error loading house property data:', error);
      setError('Failed to load house property data. Please try again.');
      showToast('Failed to load house property data', 'error');
    } finally {
      setLoading(false);
    }
  }, [empId, taxYear]);

  useEffect(() => {
    if (empId && !isNewRevision) {
      loadHousePropertyData();
    } else if (isNewRevision) {
      showToast('Creating new house property revision. Enter the updated house property data.', 'info');
    }
  }, [empId, taxYear, isNewRevision, loadHousePropertyData]);

  // Early return for authentication and authorization checks
  if (userRole === null) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="warning">
          Authentication required. Please log in to access this page.
        </Alert>
      </Box>
    );
  }

  if (!isAdmin) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          Admin privileges required. Current role: {userRole}
          <br />
          Only admin and superadmin users can access this page.
        </Alert>
      </Box>
    );
  }

  const handleInputChange = (field: keyof HousePropertyComponentData, value: number | string): void => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = async (): Promise<void> => {
    if (!empId) {
      showToast('Employee ID is required', 'error');
      return;
    }
    
    setSaving(true);
    setError(null);
    
    try {
      console.log('Saving house property data:', formData);
      
      const request = {
        employee_id: empId,
        tax_year: taxYear,
        house_property_income: formData,
        notes: `House property component updated for ${taxYear}`
      };
      
      const response = await taxationApi.updateHousePropertyComponent(request);
      console.log('Save response:', response);
      
      showToast('House property data saved successfully', 'success');
      
      // Reload data to get updated values
      await loadHousePropertyData();
      
    } catch (error) {
      console.error('Error saving house property data:', error);
      setError('Failed to save house property data. Please try again.');
      showToast('Failed to save house property data', 'error');
    } finally {
      setSaving(false);
    }
  };

  const showToast = (message: string, severity: ToastState['severity'] = 'success'): void => {
    setToast({ show: true, message, severity });
  };

  const closeToast = (): void => {
    setToast(prev => ({ ...prev, show: false }));
  };

  const handleNext = (): void => {
    setActiveStep(prev => prev + 1);
  };

  const handleBack = (): void => {
    setActiveStep(prev => prev - 1);
  };

  const calculateNetIncome = (): number => {
    const annualRent = formData.annual_rent_received || 0;
    const municipalTaxes = formData.municipal_taxes_paid || 0;
    const homeLoanInterest = formData.home_loan_interest || 0;
    const preConstructionInterest = formData.pre_construction_interest || 0;
    
    // For self-occupied properties, net income is typically negative (loss)
    // For let-out properties, it's rent minus deductions
    if (formData.property_type === 'Self-Occupied') {
      return -(homeLoanInterest + preConstructionInterest);
    } else {
      const netAnnualValue = annualRent - municipalTaxes;
      const standardDeduction = netAnnualValue * 0.3; // 30% standard deduction
      const totalDeductions = standardDeduction + homeLoanInterest + preConstructionInterest;
      return netAnnualValue - totalDeductions;
    }
  };

  const calculateTotalDeductions = (): number => {
    const municipalTaxes = formData.municipal_taxes_paid || 0;
    const homeLoanInterest = formData.home_loan_interest || 0;
    const preConstructionInterest = formData.pre_construction_interest || 0;
    
    if (formData.property_type === 'Let-Out') {
      const annualRent = formData.annual_rent_received || 0;
      const netAnnualValue = annualRent - municipalTaxes;
      const standardDeduction = netAnnualValue * 0.3; // 30% standard deduction
      return standardDeduction + homeLoanInterest + preConstructionInterest;
    } else {
      return homeLoanInterest + preConstructionInterest;
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '70vh' }}>
        <CircularProgress size={40} />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Card elevation={1} sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
            <Box>
              <Typography variant="h5" component="h1" gutterBottom>
                {isNewRevision ? 'New House Property Revision' : 'Update House Property Components'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {isNewRevision 
                  ? `Create new house property revision for Employee ID: ${empId} | Tax Year: ${taxYear}`
                  : `Update existing house property components for Employee ID: ${empId} | Tax Year: ${taxYear}`
                }
              </Typography>
              {isNewRevision && (
                <Typography variant="caption" color="primary" sx={{ display: 'block', mt: 1 }}>
                  ℹ️ This will create a new house property entry. The previous house property structure will be preserved.
                </Typography>
              )}
            </Box>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button 
                variant="outlined" 
                startIcon={<ArrowBackIcon />}
                onClick={() => navigate('/taxation/component-management')}
              >
                Back to Management
              </Button>
              <Button 
                variant="contained" 
                startIcon={<SaveIcon />}
                onClick={handleSave}
                disabled={saving}
              >
                {saving 
                  ? 'Saving...' 
                  : isNewRevision 
                    ? 'Create Revision' 
                    : 'Save Changes'
                }
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Summary Card */}
      <Card elevation={1} sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            House Property Summary
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">Property Type</Typography>
              <Typography variant="h6">{formData.property_type}</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">Annual Rent</Typography>
              <Typography variant="h6">₹{formData.annual_rent_received.toLocaleString('en-IN')}</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">Total Deductions</Typography>
              <Typography variant="h6">₹{calculateTotalDeductions().toLocaleString('en-IN')}</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">Net Income</Typography>
              <Typography variant="h6" color={calculateNetIncome() < 0 ? 'error.main' : 'success.main'}>
                ₹{calculateNetIncome().toLocaleString('en-IN')}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Stepper Form */}
      <Paper elevation={1}>
        <Box sx={{ p: 3 }}>
          <Stepper activeStep={activeStep} orientation="vertical">
            {steps.map((step, index) => (
              <Step key={step.label}>
                <StepLabel>
                  <Typography variant="h6">{step.label}</Typography>
                </StepLabel>
                <StepContent>
                  <Grid container spacing={2} sx={{ mt: 1 }}>
                    {step.fields.map((field) => (
                      <Grid item xs={12} sm={6} md={4} key={field.name}>
                        {isSelectField(field) ? (
                          <FormControl fullWidth>
                            <InputLabel>{field.label}</InputLabel>
                            <Select
                              value={formData[field.name as keyof HousePropertyComponentData] as string}
                              label={field.label}
                              onChange={(e: SelectChangeEvent) => 
                                handleInputChange(field.name as keyof HousePropertyComponentData, e.target.value)
                              }
                            >
                              {field.options.map((option) => (
                                <MenuItem key={option.value} value={option.value}>
                                  {option.label}
                                </MenuItem>
                              ))}
                            </Select>
                          </FormControl>
                        ) : isTextField(field) ? (
                          <TextField
                            fullWidth
                            label={field.label}
                            type="text"
                            value={formData[field.name as keyof HousePropertyComponentData]}
                            onChange={(e) => {
                              handleInputChange(field.name as keyof HousePropertyComponentData, e.target.value);
                            }}
                            multiline={field.name === 'address'}
                            rows={field.name === 'address' ? 3 : 1}
                          />
                        ) : (
                          <TextField
                            fullWidth
                            label={field.label}
                            type="number"
                            value={formData[field.name as keyof HousePropertyComponentData]}
                            onChange={(e) => {
                              const value = parseFloat(e.target.value) || 0;
                              handleInputChange(field.name as keyof HousePropertyComponentData, value);
                            }}
                            InputProps={{ startAdornment: '₹' }}
                          />
                        )}
                      </Grid>
                    ))}
                  </Grid>
                  <Box sx={{ mt: 2 }}>
                    <Button
                      variant="contained"
                      onClick={handleNext}
                      disabled={index === steps.length - 1}
                      sx={{ mr: 1 }}
                    >
                      {index === steps.length - 1 ? 'Finish' : 'Continue'}
                    </Button>
                    <Button
                      disabled={index === 0}
                      onClick={handleBack}
                    >
                      Back
                    </Button>
                  </Box>
                </StepContent>
              </Step>
            ))}
          </Stepper>
        </Box>
      </Paper>

      {/* Toast Notifications */}
      <Snackbar
        open={toast.show}
        autoHideDuration={6000}
        onClose={closeToast}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={closeToast} 
          severity={toast.severity}
          sx={{ width: '100%' }}
          variant="filled"
        >
          {toast.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default HousePropertyComponentForm; 