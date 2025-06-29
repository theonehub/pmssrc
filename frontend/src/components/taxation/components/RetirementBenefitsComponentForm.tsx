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

interface RetirementBenefitsComponentData {
  gratuity_amount: number;
  leave_encashment_amount: number;
  vrs_amount: number;
  pension_amount: number;
  commuted_pension_amount: number;
  other_retirement_benefits: number;
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
const initialRetirementBenefitsData: RetirementBenefitsComponentData = {
  gratuity_amount: 0,
  leave_encashment_amount: 0,
  vrs_amount: 0,
  pension_amount: 0,
  commuted_pension_amount: 0,
  other_retirement_benefits: 0
};

// Function to flatten nested backend response to flat frontend structure
const flattenRetirementBenefitsData = (nestedData: any): RetirementBenefitsComponentData => {
  console.log('Flattening retirement benefits data:', nestedData);
  const flattened: RetirementBenefitsComponentData = { ...initialRetirementBenefitsData };
  
  try {
    if (nestedData) {
      flattened.gratuity_amount = nestedData.gratuity_amount || 0;
      flattened.leave_encashment_amount = nestedData.leave_encashment_amount || 0;
      flattened.vrs_amount = nestedData.vrs_amount || 0;
      flattened.pension_amount = nestedData.pension_amount || 0;
      flattened.commuted_pension_amount = nestedData.commuted_pension_amount || 0;
      flattened.other_retirement_benefits = nestedData.other_retirement_benefits || 0;
    }
  } catch (error) {
    console.error('Error flattening retirement benefits data:', error);
  }
  
  return flattened;
};

const steps = [
  {
    label: 'Gratuity & Leave Encashment',
    description: 'Retirement benefits from employment',
    fields: [
      { name: 'gratuity_amount', label: 'Gratuity Amount', type: 'number', helperText: 'Tax exempt up to ₹20L' } as NumberField,
      { name: 'leave_encashment_amount', label: 'Leave Encashment Amount', type: 'number', helperText: 'Tax exempt up to ₹3L' } as NumberField
    ]
  },
  {
    label: 'VRS & Pension',
    description: 'Voluntary retirement and pension benefits',
    fields: [
      { name: 'vrs_amount', label: 'VRS Amount', type: 'number', helperText: 'Voluntary retirement benefits' } as NumberField,
      { name: 'pension_amount', label: 'Pension Amount', type: 'number', helperText: 'Regular pension income' } as NumberField,
      { name: 'commuted_pension_amount', label: 'Commuted Pension Amount', type: 'number', helperText: 'Lump sum pension payment' } as NumberField
    ]
  },
  {
    label: 'Other Benefits',
    description: 'Additional retirement benefits',
    fields: [
      { name: 'other_retirement_benefits', label: 'Other Retirement Benefits', type: 'number', helperText: 'Any other retirement benefits' } as NumberField
    ]
  }
];

const RetirementBenefitsComponentForm: React.FC = () => {
  const { empId } = useParams<{ empId: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState<RetirementBenefitsComponentData>(initialRetirementBenefitsData);
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
  const loadRetirementBenefitsData = useCallback(async (): Promise<void> => {
    if (!empId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      console.log(`Loading retirement benefits data for employee ${empId} for tax year ${taxYear}`);
      const response = await taxationApi.getComponent(empId, taxYear, 'retirement_benefits');
      console.log('Retirement benefits API response:', response);
      
      const componentData = response?.component_data || response;
      console.log('Component data:', componentData);
      
      if (componentData) {
        const flattenedData = flattenRetirementBenefitsData(componentData);
        console.log('Flattened retirement benefits data:', flattenedData);
        setFormData(flattenedData);
        showToast('Retirement benefits data loaded successfully', 'success');
      } else {
        console.log('No existing retirement benefits data found, using defaults');
        setFormData(initialRetirementBenefitsData);
        showToast('No existing retirement benefits data found', 'info');
      }
    } catch (error) {
      console.error('Error loading retirement benefits data:', error);
      setError('Failed to load retirement benefits data. Please try again.');
      showToast('Failed to load retirement benefits data', 'error');
    } finally {
      setLoading(false);
    }
  }, [empId, taxYear]);

  // Load data on component mount
  useEffect(() => {
    loadRetirementBenefitsData();
  }, [loadRetirementBenefitsData]);

  const handleInputChange = (field: keyof RetirementBenefitsComponentData, value: number): void => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = async (): Promise<void> => {
    if (!empId) return;
    
    setSaving(true);
    setError(null);
    
    try {
      console.log('Saving retirement benefits data:', formData);
      
      const request = {
        employee_id: empId,
        tax_year: taxYear,
        retirement_benefits: formData,
        notes: `Retirement benefits component ${isNewRevision ? 'created' : 'updated'} on ${new Date().toISOString()}`
      };
      
      const response = await taxationApi.updateRetirementBenefitsComponent(request);
      console.log('Save response:', response);
      
      showToast('Retirement benefits data saved successfully', 'success');
      
      // Navigate back to component management
      setTimeout(() => {
        navigate('/taxation/component-management');
      }, 1500);
      
    } catch (error) {
      console.error('Error saving retirement benefits data:', error);
      setError('Failed to save retirement benefits data. Please try again.');
      showToast('Failed to save retirement benefits data', 'error');
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

  const calculateTotalRetirementBenefits = (): number => {
    return Object.values(formData).reduce((sum, value) => sum + value, 0);
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
          Retirement Benefits Component Management
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
            Total Retirement Benefits
          </Typography>
          <Typography variant="h4">
            ₹{calculateTotalRetirementBenefits().toLocaleString('en-IN')}
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
                        <TextField
                          fullWidth
                          label={field.label}
                          type="number"
                          value={formData[field.name as keyof RetirementBenefitsComponentData]}
                          onChange={(e) => handleInputChange(
                            field.name as keyof RetirementBenefitsComponentData,
                            parseFloat(e.target.value) || 0
                          )}
                          InputProps={{ startAdornment: '₹' }}
                          helperText={field.helperText}
                          sx={{ mb: 2 }}
                        />
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
          {saving ? 'Saving...' : 'Save Retirement Benefits Data'}
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

export default RetirementBenefitsComponentForm; 