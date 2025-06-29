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
  Snackbar,
  Stepper,
  Step,
  StepLabel,
  StepContent
} from '@mui/material';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { ArrowBack as ArrowBackIcon, Save as SaveIcon } from '@mui/icons-material';
import { getUserRole } from '../../../shared/utils/auth';
import { taxationApi } from '../../../shared/api/taxationApi';
import { CURRENT_TAX_YEAR } from '../../../shared/constants/taxation';
import { UserRole } from '../../../shared/types';

interface InterestIncomeData {
  savings_interest: number;
  fd_interest: number;
  rd_interest: number;
  post_office_interest: number;
}

interface OtherIncomeComponentData {
  interest_income: InterestIncomeData;
  dividend_income: number;
  gifts_received: number;
  business_professional_income: number;
  other_miscellaneous_income: number;
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
  helperText?: string;
}

interface NumberField extends BaseField {
  type: 'number';
}


// Initial data structure
const initialOtherIncomeData: OtherIncomeComponentData = {
  interest_income: {
    savings_interest: 0,
    fd_interest: 0,
    rd_interest: 0,
    post_office_interest: 0
  },
  dividend_income: 0,
  gifts_received: 0,
  business_professional_income: 0,
  other_miscellaneous_income: 0
};

// Function to flatten nested backend response to flat frontend structure
const flattenOtherIncomeData = (nestedData: any): OtherIncomeComponentData => {
  const flattened: OtherIncomeComponentData = { ...initialOtherIncomeData };
  try {
    if (nestedData) {
      if (nestedData.interest_income && typeof nestedData.interest_income === 'object') {
        flattened.interest_income = {
          savings_interest: nestedData.interest_income.savings_interest || 0,
          fd_interest: nestedData.interest_income.fd_interest || 0,
          rd_interest: nestedData.interest_income.rd_interest || 0,
          post_office_interest: nestedData.interest_income.post_office_interest || 0
        };
      }
      flattened.dividend_income = nestedData.dividend_income || 0;
      flattened.gifts_received = nestedData.gifts_received || 0;
      flattened.business_professional_income = nestedData.business_professional_income || 0;
      flattened.other_miscellaneous_income = nestedData.other_miscellaneous_income || 0;
    }
  } catch (error) {
    console.error('Error flattening other income data:', error);
  }
  return flattened;
};

const steps = [
  {
    label: 'Interest & Dividend Income',
    description: 'Income from investments and savings',
    fields: [
      { name: 'interest_income', label: 'Interest Income', type: 'number', helperText: 'From savings accounts, FDs, etc.' } as NumberField,
      { name: 'dividend_income', label: 'Dividend Income', type: 'number', helperText: 'From shares, mutual funds, etc.' } as NumberField
    ]
  },
  {
    label: 'Gifts & Business Income',
    description: 'Gifts received and business/professional income',
    fields: [
      { name: 'gifts_received', label: 'Gifts Received', type: 'number', helperText: 'Monetary gifts (taxable above ₹50K)' } as NumberField,
      { name: 'business_professional_income', label: 'Business/Professional Income', type: 'number', helperText: 'Income from business or profession' } as NumberField
    ]
  },
  {
    label: 'Other Income',
    description: 'Miscellaneous income sources',
    fields: [
      { name: 'other_miscellaneous_income', label: 'Other Miscellaneous Income', type: 'number', helperText: 'Any other income not covered above' } as NumberField
    ]
  }
];

const OtherIncomeComponentForm: React.FC = () => {
  const { empId } = useParams<{ empId: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState<OtherIncomeComponentData>(initialOtherIncomeData);
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
  const loadOtherIncomeData = useCallback(async (): Promise<void> => {
    if (!empId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      console.log(`Loading other income data for employee ${empId} for tax year ${taxYear}`);
      const response = await taxationApi.getComponent(empId, taxYear, 'other_income');
      console.log('Other income API response:', response);
      
      const componentData = response?.component_data || response;
      console.log('Component data:', componentData);
      
      if (componentData) {
        const flattenedData = flattenOtherIncomeData(componentData);
        console.log('Flattened other income data:', flattenedData);
        setFormData(flattenedData);
        showToast('Other income data loaded successfully', 'success');
      } else {
        console.log('No existing other income data found, using defaults');
        setFormData(initialOtherIncomeData);
        showToast('No existing other income data found', 'info');
      }
    } catch (error) {
      console.error('Error loading other income data:', error);
      setError('Failed to load other income data. Please try again.');
      showToast('Failed to load other income data', 'error');
    } finally {
      setLoading(false);
    }
  }, [empId, taxYear]);

  // Load data on component mount
  useEffect(() => {
    loadOtherIncomeData();
  }, [loadOtherIncomeData]);

  const handleInputChange = (field: keyof OtherIncomeComponentData, value: number, subfield?: keyof InterestIncomeData): void => {
    setFormData(prev => {
      if (field === 'interest_income' && subfield) {
        return {
          ...prev,
          interest_income: {
            ...prev.interest_income,
            [subfield]: value
          }
        };
      }
      return {
        ...prev,
        [field]: value
      };
    });
  };

  const handleSave = async (): Promise<void> => {
    if (!empId) return;
    
    setSaving(true);
    setError(null);
    
    try {
      console.log('Saving other income data:', formData);
      
      const request = {
        employee_id: empId,
        tax_year: taxYear,
        other_income: formData,
        notes: `Other income component ${isNewRevision ? 'created' : 'updated'} on ${new Date().toISOString()}`
      };
      
      const response = await taxationApi.updateOtherIncomeComponent(request);
      console.log('Save response:', response);
      
      showToast('Other income data saved successfully', 'success');
      
      // Navigate back to component management
      setTimeout(() => {
        navigate('/taxation/component-management');
      }, 1500);
      
    } catch (error) {
      console.error('Error saving other income data:', error);
      setError('Failed to save other income data. Please try again.');
      showToast('Failed to save other income data', 'error');
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

  const calculateTotalOtherIncome = (): number => {
    const interestSum = Object.values(formData.interest_income).reduce((sum, v) => sum + v, 0);
    return (
      interestSum +
      formData.dividend_income +
      formData.gifts_received +
      formData.business_professional_income +
      formData.other_miscellaneous_income
    );
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
        <Button
          variant="outlined"
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/taxation/component-management')}
        >
          Back to Component Management
        </Button>
        <Typography variant="h4" component="h1">
          Other Income Component Management
        </Typography>
      </Box>

      {/* Employee Info */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" color="text.secondary">
                Employee ID
              </Typography>
              <Typography variant="h6">
                {empId}
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" color="text.secondary">
                Tax Year
              </Typography>
              <Typography variant="h6">
                {taxYear}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Summary Card */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" color="primary" gutterBottom>
            Total Other Income
          </Typography>
          <Typography variant="h4">
            ₹{calculateTotalOtherIncome().toLocaleString('en-IN')}
          </Typography>
        </CardContent>
      </Card>

      {/* Stepper Form */}
      <Paper variant="outlined" sx={{ p: 3 }}>
        <Stepper activeStep={activeStep} orientation="vertical">
          {steps.map((step, index) => (
            <Step key={step.label}>
              <StepLabel>
                <Typography variant="h6">{step.label}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {step.description}
                </Typography>
              </StepLabel>
              <StepContent>
                <Box sx={{ mt: 2 }}>
                  <Grid container spacing={3}>
                    {step.fields.map((field) => (
                      <Grid item xs={12} md={6} key={field.name}>
                        {field.name === 'interest_income' ? (
                          <Box>
                            <TextField
                              fullWidth
                              label="Savings Interest"
                              type="number"
                              value={formData.interest_income.savings_interest}
                              onChange={(e) => handleInputChange('interest_income', parseFloat(e.target.value) || 0, 'savings_interest')}
                              InputProps={{ startAdornment: '₹' }}
                              helperText="From savings accounts"
                              sx={{ mb: 2 }}
                            />
                            <TextField
                              fullWidth
                              label="FD Interest"
                              type="number"
                              value={formData.interest_income.fd_interest}
                              onChange={(e) => handleInputChange('interest_income', parseFloat(e.target.value) || 0, 'fd_interest')}
                              InputProps={{ startAdornment: '₹' }}
                              helperText="From fixed deposits"
                              sx={{ mb: 2 }}
                            />
                            <TextField
                              fullWidth
                              label="RD Interest"
                              type="number"
                              value={formData.interest_income.rd_interest}
                              onChange={(e) => handleInputChange('interest_income', parseFloat(e.target.value) || 0, 'rd_interest')}
                              InputProps={{ startAdornment: '₹' }}
                              helperText="From recurring deposits"
                              sx={{ mb: 2 }}
                            />
                            <TextField
                              fullWidth
                              label="Post Office Interest"
                              type="number"
                              value={formData.interest_income.post_office_interest}
                              onChange={(e) => handleInputChange('interest_income', parseFloat(e.target.value) || 0, 'post_office_interest')}
                              InputProps={{ startAdornment: '₹' }}
                              helperText="From post office savings"
                              sx={{ mb: 2 }}
                            />
                          </Box>
                        ) : (
                          <TextField
                            fullWidth
                            label={field.label}
                            type="number"
                            value={formData[field.name as keyof OtherIncomeComponentData] as number}
                            onChange={(e) => handleInputChange(field.name as keyof OtherIncomeComponentData, parseFloat(e.target.value) || 0)}
                            InputProps={{ startAdornment: '₹' }}
                            helperText={field.helperText}
                            sx={{ mb: 2 }}
                          />
                        )}
                      </Grid>
                    ))}
                  </Grid>
                  
                  <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
                    <Button
                      variant="outlined"
                      onClick={handleBack}
                      disabled={index === 0}
                    >
                      Back
                    </Button>
                    <Button
                      variant="contained"
                      onClick={handleNext}
                      disabled={index === steps.length - 1}
                    >
                      Next
                    </Button>
                  </Box>
                </Box>
              </StepContent>
            </Step>
          ))}
        </Stepper>
      </Paper>

      {/* Save Button */}
      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center', gap: 2 }}>
        <Button
          variant="contained"
          color="primary"
          size="large"
          startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
          onClick={handleSave}
          disabled={saving}
        >
          {saving ? 'Saving...' : 'Save Other Income Data'}
        </Button>
      </Box>

      {/* Toast Notification */}
      <Snackbar
        open={toast.show}
        autoHideDuration={6000}
        onClose={closeToast}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={closeToast} severity={toast.severity} sx={{ width: '100%' }}>
          {toast.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default OtherIncomeComponentForm;
