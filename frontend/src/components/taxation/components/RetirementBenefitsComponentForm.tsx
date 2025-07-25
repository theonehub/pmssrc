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
  StepContent,
  FormControlLabel,
  Checkbox
} from '@mui/material';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { ArrowBack as ArrowBackIcon, Save as SaveIcon } from '@mui/icons-material';
import { getUserRole } from '../../../shared/utils/auth';
import taxationApi from '../../../shared/api/taxationApi';
import { CURRENT_TAX_YEAR } from '../../../shared/constants/taxation';
import { UserRole } from '../../../shared/types';

interface RetirementBenefitsComponentData {
  // Legacy fields for backward compatibility
  vrs_amount: number;
  pension_amount: number;
  commuted_pension_amount: number;
  other_retirement_benefits: number;
  
  // Detailed Leave Encashment fields
  leave_encashment_amount: number;
  average_monthly_salary: number;
  leave_days_encashed: number;
  is_deceased: boolean;
  during_employment: boolean;
  
  // Detailed Gratuity fields
  gratuity_amount: number;
  gratuity_monthly_salary: number;
  gratuity_service_years: number;
  
  // Detailed Pension fields
  pension_regular_pension: number;
  pension_commuted_pension: number;
  pension_total_pension: number;
  pension_gratuity_received: boolean;
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

interface CheckboxField extends BaseField {
  type: 'checkbox';
}

type FormField = NumberField | CheckboxField;

// Add type for monthly salary row
interface MonthlySalaryRow {
  month: string;
  amount: number;
}

// Helper to get rolling months ending with previous month, with year suffix
function getRollingMonthsWithYear(): { label: string, month: string, year: number }[] {
  const allMonths = [
    'April', 'May', 'June', 'July', 'August', 'September',
    'October', 'November', 'December', 'January', 'February', 'March'
  ];
  // Get current date
  const now = new Date();
  const jsMonth = now.getMonth(); // 0=Jan, ..., 11=Dec
  const jsYear = now.getFullYear();
  // Fiscal year starts in April
  // April=3, so fiscalMonth = (jsMonth+9)%12
  const fiscalMonth = (jsMonth + 9) % 12;
  let lastIdx = fiscalMonth - 1;
  if (lastIdx < 0) lastIdx = 11;
  // Determine the fiscal year for each month
  // Fiscal year: April to March (e.g., 2024-25: April 2024 to March 2025)
  // If current month is April 2025, last completed is March 2025, so March-25
  // If current month is May 2025, last completed is April 2025, so April-25, March-25, ...
  // Start from lastIdx, go back 11 months
  const months: { label: string, month: string, year: number }[] = [];
  let year = jsYear;
  // If lastIdx >= 9 (Jan, Feb, Mar), year = jsYear; else year = jsYear - 1 for those months
  // But we need to roll back 11 months, so we need to adjust year as we go
  // We'll start from the last completed month and go backwards
  let idx = lastIdx;
  for (let i = 0; i < 12; i++) {
    let m = allMonths[idx];
    // For months Jan, Feb, Mar (idx 9,10,11), year is jsYear+1 if fiscal year has rolled over
    let displayYear = year;
    if (idx >= 9) {
      // Jan, Feb, Mar belong to next calendar year in fiscal
      displayYear = year + 1;
    }
    // Label: e.g., March-25, April-24
    const shortYear = String(displayYear).slice(-2);
    months.unshift({ label: `${m ?? ''}-${shortYear}`, month: m ?? '', year: displayYear });
    idx--;
    if (idx < 0) {
      idx = 11;
      year--;
    }
  }
  return months;
}

const MONTHS_ORDER_WITH_YEAR = getRollingMonthsWithYear();
const initialMonthlySalaryPaid: MonthlySalaryRow[] = MONTHS_ORDER_WITH_YEAR.map(m => ({ month: m.label, amount: 0 }));

// Initial data structure
const initialRetirementBenefitsData: RetirementBenefitsComponentData = {
  // Legacy fields for backward compatibility
  vrs_amount: 0,
  pension_amount: 0,
  commuted_pension_amount: 0,
  other_retirement_benefits: 0,
  
  // Detailed Leave Encashment fields
  leave_encashment_amount: 0,
  average_monthly_salary: 0,
  leave_days_encashed: 0,
  is_deceased: false,
  during_employment: false,
  
  // Detailed Gratuity fields
  gratuity_amount: 0,
  gratuity_monthly_salary: 0,
  gratuity_service_years: 0,
  
  // Detailed Pension fields
  pension_regular_pension: 0,
  pension_commuted_pension: 0,
  pension_total_pension: 0,
  pension_gratuity_received: false
};

// Function to flatten nested backend response to flat frontend structure
const flattenRetirementBenefitsData = (nestedData: any): RetirementBenefitsComponentData => {
  console.log('Flattening retirement benefits data:', nestedData);
  const flattened: RetirementBenefitsComponentData = { ...initialRetirementBenefitsData };
  
  try {
    if (nestedData) {
      // Legacy fields
      flattened.gratuity_amount = nestedData.gratuity_amount || 0;
      flattened.leave_encashment_amount = nestedData.leave_encashment_amount || 0;
      flattened.vrs_amount = nestedData.vrs_amount || 0;
      flattened.pension_amount = nestedData.pension_amount || 0;
      flattened.commuted_pension_amount = nestedData.commuted_pension_amount || 0;
      flattened.other_retirement_benefits = nestedData.other_retirement_benefits || 0;
      
      // Detailed Leave Encashment fields
      if (nestedData.leave_encashment) {
        console.log('Processing detailed leave encashment:', nestedData.leave_encashment);
        flattened.leave_encashment_amount = nestedData.leave_encashment.leave_encashment_amount || 0;
        flattened.average_monthly_salary = nestedData.leave_encashment.average_monthly_salary || 0;
        flattened.leave_days_encashed = nestedData.leave_encashment.leave_days_encashed || 0;
        flattened.is_deceased = nestedData.leave_encashment.is_deceased || false;
        flattened.during_employment = nestedData.leave_encashment.during_employment || false;
      }
      
      // Detailed Gratuity fields
      if (nestedData.gratuity) {
        console.log('Processing detailed gratuity:', nestedData.gratuity);
        flattened.gratuity_amount = nestedData.gratuity.gratuity_amount || 0;
        flattened.gratuity_monthly_salary = nestedData.gratuity.monthly_salary || 0;
        flattened.gratuity_service_years = nestedData.gratuity.service_years || 0;
      }
      
      // Detailed Pension fields
      if (nestedData.pension) {
        console.log('Processing detailed pension:', nestedData.pension);
        flattened.pension_regular_pension = nestedData.pension.regular_pension || 0;
        flattened.pension_commuted_pension = nestedData.pension.commuted_pension || 0;
        flattened.pension_total_pension = nestedData.pension.total_pension || 0;
        flattened.pension_gratuity_received = nestedData.pension.gratuity_received || false;
      }
    }
    // Populate monthlySalaryPaid if present
    if (nestedData && Array.isArray(nestedData.monthly_salary_paid)) {
      // This state is managed by the component, so we don't set it here directly.
      // The component will manage its own state and update it.
    } else {
      // This state is managed by the component, so we don't set it here directly.
      // The component will manage its own state and update it.
    }
  } catch (error) {
    console.error('Error flattening retirement benefits data:', error);
  }
  
  return flattened;
};

const steps: { label: string; description: string; fields?: FormField[]; isMonthlySalaryPaidStep?: boolean }[] = [
  {
    label: 'Gratuity',
    description: 'Detailed gratuity information',
    fields: [
      { name: 'gratuity_amount', label: 'Gratuity Amount', type: 'number', helperText: 'Total gratuity amount received' } as NumberField,
      { name: 'gratuity_monthly_salary', label: 'Monthly Salary', type: 'number', helperText: 'Monthly salary for calculation' } as NumberField,
      { name: 'gratuity_service_years', label: 'Years of Service', type: 'number', helperText: 'Number of years of service' } as NumberField
    ]
  },
  {
    label: 'Leave Encashment',
    description: 'Detailed leave encashment information',
    fields: [
      { name: 'leave_encashment_amount', label: 'Leave Encashment Amount', type: 'number', helperText: 'Total leave encashment amount received' } as NumberField,
      { name: 'average_monthly_salary', label: 'Average Monthly Salary', type: 'number', helperText: 'Average monthly salary for calculation' } as NumberField,
      { name: 'leave_days_encashed', label: 'Leave Days Encashed', type: 'number', helperText: 'Number of leave days encashed' } as NumberField,
      { name: 'is_deceased', label: 'Employee is Deceased', type: 'checkbox', helperText: 'Check if employee is deceased (fully exempt)' } as CheckboxField,
      { name: 'during_employment', label: 'During Employment', type: 'checkbox', helperText: 'Check if encashment was during employment' } as CheckboxField
    ]
  },
  // Insert Monthly Salary Paid step here
  {
    label: 'Monthly Salary Paid',
    description: 'Enter the gross salary paid for each month (April to March)',
    isMonthlySalaryPaidStep: true
  },
  {
    label: 'VRS',
    description: 'Voluntary retirement benefits',
    fields: [
      { name: 'vrs_amount', label: 'VRS Amount', type: 'number', helperText: 'Voluntary retirement benefits' } as NumberField
    ]
  },
  {
    label: 'Pension',
    description: 'Detailed pension information',
    fields: [
      { name: 'pension_regular_pension', label: 'Regular Pension', type: 'number', helperText: 'Regular monthly pension income' } as NumberField,
      { name: 'pension_commuted_pension', label: 'Commuted Pension', type: 'number', helperText: 'Lump sum commuted pension amount' } as NumberField,
      { name: 'pension_total_pension', label: 'Total Pension', type: 'number', helperText: 'Total pension amount (regular + commuted)' } as NumberField,
      { name: 'pension_gratuity_received', label: 'Gratuity Received', type: 'checkbox', helperText: 'Check if gratuity was also received (affects commuted pension exemption)' } as CheckboxField
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
  const [monthlySalaryPaid, setMonthlySalaryPaid] = useState<MonthlySalaryRow[]>(initialMonthlySalaryPaid);
  
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

  const handleInputChange = (field: keyof RetirementBenefitsComponentData, value: number | boolean): void => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Add handler for monthly salary table
  const handleMonthlySalaryChange = (idx: number, value: number) => {
    setMonthlySalaryPaid(prev => prev.map((row, i) => i === idx ? { ...row, amount: value } : row));
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
        retirement_benefits: {
          ...formData,
          monthly_salary_paid: monthlySalaryPaid.map(row => row.amount),
        },
        notes: `Retirement benefits component ${isNewRevision ? 'created' : 'updated'} on ${new Date().toISOString()}`
      };
      
      const response = await taxationApi.updateRetirementBenefitsComponent(request);
      console.log('Save response:', response);
      
      showToast('Retirement benefits data saved successfully', 'success');
      
      // Navigate back to component management
      setTimeout(() => {
        navigate('/taxation/component-management');
      }, 1500);
      
    } catch (error: any) {
      const backendMessage = error?.response?.data?.detail;
      setError(backendMessage || 'Failed to save retirement benefits data. Please try again.');
      showToast(backendMessage || 'Failed to save retirement benefits data', 'error');
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
    // Calculate total from numeric fields only
    return formData.gratuity_amount + 
           formData.leave_encashment_amount + 
           formData.vrs_amount + 
           formData.pension_regular_pension + 
           formData.pension_commuted_pension + 
           formData.other_retirement_benefits;
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
                  {step.isMonthlySalaryPaidStep ? (
                    <Grid container spacing={2}>
                      {monthlySalaryPaid.map((row, idx) => (
                        <Grid item xs={12} sm={6} md={4} key={row.month}>
                          <TextField
                            fullWidth
                            label={row.month}
                            type="number"
                            value={row.amount}
                            onChange={e => handleMonthlySalaryChange(idx, parseFloat(e.target.value) || 0)}
                            inputProps={{ min: 0 }}
                            InputProps={{ startAdornment: '₹' }}
                            helperText={`Salary paid in ${row.month}`}
                          />
                        </Grid>
                      ))}
                    </Grid>
                  ) : (
                    <Grid container spacing={3}>
                      {step.fields && step.fields.map((field) => (
                        <Grid item xs={12} md={6} key={field.name}>
                          {field.type === 'checkbox' ? (
                            <FormControlLabel
                              control={
                                <Checkbox
                                  checked={formData[field.name as keyof RetirementBenefitsComponentData] as boolean}
                                  onChange={(e) => handleInputChange(
                                    field.name as keyof RetirementBenefitsComponentData,
                                    e.target.checked
                                  )}
                                />
                              }
                              label={field.label}
                            />
                          ) : (
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
                          )}
                        </Grid>
                      ))}
                    </Grid>
                  )}
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