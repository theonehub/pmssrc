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
import taxationApi from '../../../shared/api/taxationApi';
import { CURRENT_TAX_YEAR } from '../../../shared/constants/taxation';
import { UserRole } from '../../../shared/types';

interface CapitalGainsComponentData {
  stcg_111a_equity_stt: number;
  stcg_other_assets: number;
  stcg_debt_mf: number;
  ltcg_112a_equity_stt: number;
  ltcg_other_assets: number;
  ltcg_debt_mf: number;
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
const initialCapitalGainsData: CapitalGainsComponentData = {
  stcg_111a_equity_stt: 0,
  stcg_other_assets: 0,
  stcg_debt_mf: 0,
  ltcg_112a_equity_stt: 0,
  ltcg_other_assets: 0,
  ltcg_debt_mf: 0
};

// Function to flatten nested backend response to flat frontend structure
const flattenCapitalGainsData = (nestedData: any): CapitalGainsComponentData => {
  console.log('Flattening capital gains data:', nestedData);
  const flattened: CapitalGainsComponentData = { ...initialCapitalGainsData };
  
  try {
    if (nestedData) {
      flattened.stcg_111a_equity_stt = nestedData.stcg_111a_equity_stt || 0;
      flattened.stcg_other_assets = nestedData.stcg_other_assets || 0;
      flattened.stcg_debt_mf = nestedData.stcg_debt_mf || 0;
      flattened.ltcg_112a_equity_stt = nestedData.ltcg_112a_equity_stt || 0;
      flattened.ltcg_other_assets = nestedData.ltcg_other_assets || 0;
      flattened.ltcg_debt_mf = nestedData.ltcg_debt_mf || 0;
    }
  } catch (error) {
    console.error('Error flattening capital gains data:', error);
  }
  
  return flattened;
};

const steps = [
  {
    label: 'Short Term Capital Gains',
    description: 'Gains from assets held for less than 12 months',
    fields: [
      { name: 'stcg_111a_equity_stt', label: 'STCG 111A (Equity with STT)', type: 'number', helperText: 'Taxed at 15%' } as NumberField,
      { name: 'stcg_other_assets', label: 'STCG Other Assets', type: 'number', helperText: 'Taxed at slab rates' } as NumberField,
      { name: 'stcg_debt_mf', label: 'STCG Debt Mutual Funds', type: 'number', helperText: 'Taxed at slab rates' } as NumberField
    ]
  },
  {
    label: 'Long Term Capital Gains',
    description: 'Gains from assets held for more than 12 months',
    fields: [
      { name: 'ltcg_112a_equity_stt', label: 'LTCG 112A (Equity with STT)', type: 'number', helperText: '10% tax with ₹1.25L exemption' } as NumberField,
      { name: 'ltcg_other_assets', label: 'LTCG Other Assets', type: 'number', helperText: 'Taxed at 20% with indexation' } as NumberField,
      { name: 'ltcg_debt_mf', label: 'LTCG Debt Mutual Funds', type: 'number', helperText: 'Taxed at 20% with indexation' } as NumberField
    ]
  }
];

const CapitalGainsComponentForm: React.FC = () => {
  const { empId } = useParams<{ empId: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState<CapitalGainsComponentData>(initialCapitalGainsData);
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
  const loadCapitalGainsData = useCallback(async (): Promise<void> => {
    if (!empId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      console.log(`Loading capital gains data for employee ${empId} for tax year ${taxYear}`);
      const response = await taxationApi.getComponent(empId, taxYear, 'capital_gains_income');
      console.log('Capital gains API response:', response);
      
      const componentData = response?.component_data || response;
      console.log('Component data:', componentData);
      
      if (componentData) {
        const flattenedData = flattenCapitalGainsData(componentData);
        console.log('Flattened capital gains data:', flattenedData);
        setFormData(flattenedData);
        showToast('Capital gains data loaded successfully', 'success');
      } else {
        console.log('No existing capital gains data found, using defaults');
        setFormData(initialCapitalGainsData);
        showToast('No existing capital gains data found', 'info');
      }
    } catch (error) {
      console.error('Error loading capital gains data:', error);
      setError('Failed to load capital gains data. Please try again.');
      showToast('Failed to load capital gains data', 'error');
    } finally {
      setLoading(false);
    }
  }, [empId, taxYear]);

  // Load data on component mount
  useEffect(() => {
    loadCapitalGainsData();
  }, [loadCapitalGainsData]);

  const handleInputChange = (field: keyof CapitalGainsComponentData, value: number): void => {
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
      console.log('Saving capital gains data:', formData);
      
      const request = {
        employee_id: empId,
        tax_year: taxYear,
        capital_gains_income: formData,
        notes: `Capital gains component ${isNewRevision ? 'created' : 'updated'} on ${new Date().toISOString()}`
      };
      
      const response = await taxationApi.updateCapitalGainsComponent(request);
      console.log('Save response:', response);
      
      showToast('Capital gains data saved successfully', 'success');
      
      // Navigate back to component management
      setTimeout(() => {
        navigate('/taxation/component-management');
      }, 1500);
      
    } catch (error) {
      console.error('Error saving capital gains data:', error);
      setError('Failed to save capital gains data. Please try again.');
      showToast('Failed to save capital gains data', 'error');
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

  const calculateTotalSTCG = (): number => {
    return formData.stcg_111a_equity_stt + formData.stcg_other_assets + formData.stcg_debt_mf;
  };

  const calculateTotalLTCG = (): number => {
    return formData.ltcg_112a_equity_stt + formData.ltcg_other_assets + formData.ltcg_debt_mf;
  };

  const calculateTotalCapitalGains = (): number => {
    return calculateTotalSTCG() + calculateTotalLTCG();
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
          Capital Gains Component Management
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

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="primary">
                Total STCG
              </Typography>
              <Typography variant="h4">
                ₹{calculateTotalSTCG().toLocaleString('en-IN')}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="secondary">
                Total LTCG
              </Typography>
              <Typography variant="h4">
                ₹{calculateTotalLTCG().toLocaleString('en-IN')}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="success.main">
                Total Capital Gains
              </Typography>
              <Typography variant="h4">
                ₹{calculateTotalCapitalGains().toLocaleString('en-IN')}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

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
                          value={formData[field.name as keyof CapitalGainsComponentData]}
                          onChange={(e) => handleInputChange(
                            field.name as keyof CapitalGainsComponentData,
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
          {saving ? 'Saving...' : 'Save Capital Gains Data'}
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

export default CapitalGainsComponentForm; 