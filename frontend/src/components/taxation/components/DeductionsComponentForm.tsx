import React, { useState, useEffect } from 'react';
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
import { taxationApi } from '../../../shared/api/taxationApi';

interface DeductionsComponentData {
  // HRA Exemption
  actual_rent_paid: number;
  hra_city_type: string;

  // Section 80C
  life_insurance_premium: number;
  epf_contribution: number;
  ppf_contribution: number;
  nsc_investment: number;
  tax_saving_fd: number;
  elss_investment: number;
  home_loan_principal: number;
  tuition_fees: number;
  ulip_premium: number;
  sukanya_samriddhi: number;
  stamp_duty_property: number;
  senior_citizen_savings: number;
  other_80c_investments: number;

  // Section 80CCC
  pension_plan_insurance_company: number;

  // Section 80CCD
  nps_contribution_10_percent: number;
  additional_nps_50k: number;
  employer_nps_contribution: number;

  // Section 80D
  self_family_premium: number;
  parent_premium: number;
  preventive_health_checkup: number;

  // Section 80DD
  disability_amount: number;
  disability_relation: string;
  disability_percentage: string;

  // Section 80DDB
  medical_expenses: number;
  medical_relation: string;

  // Section 80E
  education_loan_interest: number;

  // Section 80EEB
  ev_loan_interest: number;

  // Section 80G
  donation_100_percent_without_limit: number;
  donation_50_percent_without_limit: number;
  donation_100_percent_with_limit: number;
  donation_50_percent_with_limit: number;

  // Section 80GGC
  political_party_contribution: number;

  // Section 80U
  self_disability_amount: number;
  self_disability_percentage: string;

  // Section 80TTA/TTB
  savings_account_interest: number;
  deposit_interest_senior: number;
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
  maxValue?: number;
}

interface NumberField extends BaseField {
  type: 'number';
}

interface SelectField extends BaseField {
  type: 'select';
  options: { value: string; label: string; }[];
}

type FormField = NumberField | SelectField;

interface StepConfig {
  label: string;
  fields: FormField[];
  maxLimit?: number;
  description?: string;
}

const isSelectField = (field: FormField): field is SelectField => {
  return field.type === 'select';
};

const initialDeductionsData: DeductionsComponentData = {
  // HRA Exemption
  actual_rent_paid: 0,
  hra_city_type: 'non_metro',

  // Section 80C
  life_insurance_premium: 0,
  epf_contribution: 0,
  ppf_contribution: 0,
  nsc_investment: 0,
  tax_saving_fd: 0,
  elss_investment: 0,
  home_loan_principal: 0,
  tuition_fees: 0,
  ulip_premium: 0,
  sukanya_samriddhi: 0,
  stamp_duty_property: 0,
  senior_citizen_savings: 0,
  other_80c_investments: 0,

  // Section 80CCC
  pension_plan_insurance_company: 0,

  // Section 80CCD
  nps_contribution_10_percent: 0,
  additional_nps_50k: 0,
  employer_nps_contribution: 0,

  // Section 80D
  self_family_premium: 0,
  parent_premium: 0,
  preventive_health_checkup: 0,

  // Section 80DD
  disability_amount: 0,
  disability_relation: 'Parents',
  disability_percentage: '40-79%',

  // Section 80DDB
  medical_expenses: 0,
  medical_relation: 'Self',

  // Section 80E
  education_loan_interest: 0,

  // Section 80EEB
  ev_loan_interest: 0,

  // Section 80G
  donation_100_percent_without_limit: 0,
  donation_50_percent_without_limit: 0,
  donation_100_percent_with_limit: 0,
  donation_50_percent_with_limit: 0,

  // Section 80GGC
  political_party_contribution: 0,

  // Section 80U
  self_disability_amount: 0,
  self_disability_percentage: '40-79%',

  // Section 80TTA/TTB
  savings_account_interest: 0,
  deposit_interest_senior: 0
};

const DeductionsComponentForm: React.FC = () => {
  const { empId } = useParams<{ empId: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const userRole = getUserRole();
  
  const [loading, setLoading] = useState<boolean>(false);
  const [saving, setSaving] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<ToastState>({ show: false, message: '', severity: 'success' });
  const [deductionsData, setDeductionsData] = useState<DeductionsComponentData>(initialDeductionsData);
  const [activeStep, setActiveStep] = useState<number>(0);
  
  const taxYear = searchParams.get('year') || '2024-25';
  const mode = searchParams.get('mode') || 'update';
  const isAdmin = userRole === 'admin' || userRole === 'superadmin';
  const isNewRevision = mode === 'new';

  // Redirect non-admin users
  useEffect(() => {
    if (!isAdmin) {
      navigate('/taxation');
    }
  }, [isAdmin, navigate]);

  // Load existing deductions data
  useEffect(() => {
    if (empId && !isNewRevision) {
      loadDeductionsData();
    } else if (isNewRevision) {
      showToast('Creating new deductions revision. Enter the updated deductions data.', 'info');
    }
  }, [empId, taxYear, isNewRevision]);

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

  const loadDeductionsData = async (): Promise<void> => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await taxationApi.getComponent(empId!, taxYear, 'deductions');
      
      if (response && response.component_data) {
        setDeductionsData({ ...initialDeductionsData, ...response.component_data } as DeductionsComponentData);
        showToast('Deductions data loaded successfully', 'success');
      } else if (response) {
        setDeductionsData({ ...initialDeductionsData, ...response } as DeductionsComponentData);
        showToast('Deductions data loaded successfully', 'success');
      }
    } catch (error: any) {
      if (error.response?.status === 404) {
        showToast('No existing deductions data found. Creating new record.', 'info');
      } else {
        setError('Failed to load deductions data. Please try again.');
        showToast('Failed to load deductions data', 'error');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: keyof DeductionsComponentData, value: number | string): void => {
    setDeductionsData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = async (): Promise<void> => {
    try {
      setSaving(true);
      setError(null);

      const requestData = {
        employee_id: empId!,
        tax_year: taxYear,
        deductions: deductionsData,
        force_new_revision: isNewRevision,
        notes: isNewRevision 
          ? 'New deductions revision created via individual component management'
          : 'Updated via individual component management'
      };

      await taxationApi.updateDeductionsComponent(requestData);
      
      showToast(
        isNewRevision 
          ? 'New deductions revision created successfully' 
          : 'Deductions component updated successfully', 
        'success'
      );
      
      setTimeout(() => {
        navigate('/taxation/component-management');
      }, 1500);
      
    } catch (error: any) {
      setError('Failed to save deductions data. Please try again.');
      showToast('Failed to save deductions data', 'error');
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

  const calculate80CTotal = (): number => {
    return deductionsData.life_insurance_premium +
           deductionsData.epf_contribution +
           deductionsData.ppf_contribution +
           deductionsData.nsc_investment +
           deductionsData.tax_saving_fd +
           deductionsData.elss_investment +
           deductionsData.home_loan_principal +
           deductionsData.tuition_fees +
           deductionsData.ulip_premium +
           deductionsData.sukanya_samriddhi +
           deductionsData.stamp_duty_property +
           deductionsData.senior_citizen_savings +
           deductionsData.other_80c_investments;
  };

  const calculate80DTotal = (): number => {
    return deductionsData.self_family_premium +
           deductionsData.parent_premium +
           deductionsData.preventive_health_checkup;
  };

  const calculateTotalDeductions = (): number => {
    return Math.min(calculate80CTotal(), 150000) +
           Math.min(calculate80DTotal(), 75000) +
           deductionsData.education_loan_interest +
           deductionsData.ev_loan_interest +
           deductionsData.political_party_contribution +
           deductionsData.savings_account_interest;
  };

  const steps: StepConfig[] = [
    {
      label: 'HRA Exemption',
      description: 'House Rent Allowance exemption details',
      fields: [
        { name: 'actual_rent_paid', label: 'Actual Rent Paid', type: 'number' } as NumberField,
        { name: 'hra_city_type', label: 'City Type', type: 'select', options: [
          { value: 'metro', label: 'Metro City (50% exemption)' },
          { value: 'non_metro', label: 'Non-Metro City (40% exemption)' }
        ]} as SelectField
      ]
    },
    {
      label: 'Section 80C',
      description: 'Investments and savings under Section 80C (Max: ₹1,50,000)',
      maxLimit: 150000,
      fields: [
        { name: 'life_insurance_premium', label: 'Life Insurance Premium', type: 'number' } as NumberField,
        { name: 'epf_contribution', label: 'EPF Contribution', type: 'number' } as NumberField,
        { name: 'ppf_contribution', label: 'PPF Contribution', type: 'number' } as NumberField,
        { name: 'nsc_investment', label: 'NSC Investment', type: 'number' } as NumberField,
        { name: 'tax_saving_fd', label: 'Tax Saving FD', type: 'number' } as NumberField,
        { name: 'elss_investment', label: 'ELSS Investment', type: 'number' } as NumberField,
        { name: 'home_loan_principal', label: 'Home Loan Principal', type: 'number' } as NumberField,
        { name: 'tuition_fees', label: 'Tuition Fees', type: 'number' } as NumberField,
        { name: 'ulip_premium', label: 'ULIP Premium', type: 'number' } as NumberField,
        { name: 'sukanya_samriddhi', label: 'Sukanya Samriddhi', type: 'number' } as NumberField,
        { name: 'stamp_duty_property', label: 'Stamp Duty on Property', type: 'number' } as NumberField,
        { name: 'senior_citizen_savings', label: 'Senior Citizen Savings', type: 'number' } as NumberField,
        { name: 'other_80c_investments', label: 'Other 80C Investments', type: 'number' } as NumberField
      ]
    },
    {
      label: 'Section 80D & Health',
      description: 'Health insurance and medical expenses (Max: ₹75,000)',
      maxLimit: 75000,
      fields: [
        { name: 'self_family_premium', label: 'Self & Family Health Insurance Premium', type: 'number' } as NumberField,
        { name: 'parent_premium', label: 'Parents Health Insurance Premium', type: 'number' } as NumberField,
        { name: 'preventive_health_checkup', label: 'Preventive Health Checkup', type: 'number' } as NumberField
      ]
    },
    {
      label: 'Section 80DD & 80DDB',
      description: 'Disability and medical treatment expenses',
      fields: [
        { name: 'disability_relation', label: 'Disability Relation', type: 'select', options: [
          { value: 'Self', label: 'Self' },
          { value: 'Parents', label: 'Parents' },
          { value: 'Spouse', label: 'Spouse' },
          { value: 'Children', label: 'Children' }
        ]} as SelectField,
        { name: 'disability_percentage', label: 'Disability Percentage', type: 'select', options: [
          { value: '40-79%', label: '40-79% (₹75,000)' },
          { value: '80%+', label: '80%+ (₹1,25,000)' }
        ]} as SelectField,
        { name: 'medical_expenses', label: 'Medical Expenses (80DDB)', type: 'number' } as NumberField,
        { name: 'medical_relation', label: 'Medical Relation', type: 'select', options: [
          { value: 'Self', label: 'Self' },
          { value: 'Parents', label: 'Parents' },
          { value: 'Spouse', label: 'Spouse' },
          { value: 'Children', label: 'Children' }
        ]} as SelectField
      ]
    },
    {
      label: 'Other Deductions',
      description: 'Education loan, donations, and other deductions',
      fields: [
        { name: 'education_loan_interest', label: 'Education Loan Interest (80E)', type: 'number' } as NumberField,
        { name: 'ev_loan_interest', label: 'Electric Vehicle Loan Interest (80EEB)', type: 'number', maxValue: 150000 } as NumberField,
        { name: 'donation_100_percent_without_limit', label: 'Donations 100% w/o Limit (80G)', type: 'number' } as NumberField,
        { name: 'donation_50_percent_without_limit', label: 'Donations 50% w/o Limit (80G)', type: 'number' } as NumberField,
        { name: 'donation_100_percent_with_limit', label: 'Donations 100% w/ Limit (80G)', type: 'number' } as NumberField,
        { name: 'donation_50_percent_with_limit', label: 'Donations 50% w/ Limit (80G)', type: 'number' } as NumberField,
        { name: 'political_party_contribution', label: 'Political Party Contribution (80GGC)', type: 'number' } as NumberField,
        { name: 'savings_account_interest', label: 'Savings Account Interest (80TTA)', type: 'number', maxValue: 10000 } as NumberField,
        { name: 'deposit_interest_senior', label: 'Deposit Interest - Senior Citizen (80TTB)', type: 'number', maxValue: 50000 } as NumberField
      ]
    }
  ];

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
                {isNewRevision ? 'New Deductions Revision' : 'Update Deductions Components'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {isNewRevision 
                  ? `Create new deductions revision for Employee ID: ${empId} | Tax Year: ${taxYear}`
                  : `Update existing deductions components for Employee ID: ${empId} | Tax Year: ${taxYear}`
                }
              </Typography>
              {isNewRevision && (
                <Typography variant="caption" color="primary" sx={{ display: 'block', mt: 1 }}>
                  ℹ️ This will create a new deductions entry. The previous deductions structure will be preserved.
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
            Deductions Summary
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">Section 80C Total</Typography>
              <Typography variant="h6">₹{calculate80CTotal().toLocaleString('en-IN')}</Typography>
              <Typography variant="caption" color={calculate80CTotal() > 150000 ? 'error' : 'textSecondary'}>
                Limit: ₹1,50,000
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">Section 80D Total</Typography>
              <Typography variant="h6">₹{calculate80DTotal().toLocaleString('en-IN')}</Typography>
              <Typography variant="caption" color={calculate80DTotal() > 75000 ? 'error' : 'textSecondary'}>
                Limit: ₹75,000
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">Education Loan Interest</Typography>
              <Typography variant="h6">₹{deductionsData.education_loan_interest.toLocaleString('en-IN')}</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">Total Deductions</Typography>
              <Typography variant="h6" color="primary">₹{calculateTotalDeductions().toLocaleString('en-IN')}</Typography>
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
                  {step.description && (
                    <Typography variant="body2" color="text.secondary">
                      {step.description}
                    </Typography>
                  )}
                </StepLabel>
                <StepContent>
                  <Grid container spacing={2} sx={{ mt: 1 }}>
                    {step.fields.map((field) => (
                      <Grid item xs={12} sm={6} md={4} key={field.name}>
                        {isSelectField(field) ? (
                          <FormControl fullWidth>
                            <InputLabel>{field.label}</InputLabel>
                            <Select
                              value={deductionsData[field.name as keyof DeductionsComponentData] as string}
                              label={field.label}
                              onChange={(e: SelectChangeEvent) => 
                                handleInputChange(field.name as keyof DeductionsComponentData, e.target.value)
                              }
                            >
                              {field.options.map((option) => (
                                <MenuItem key={option.value} value={option.value}>
                                  {option.label}
                                </MenuItem>
                              ))}
                            </Select>
                          </FormControl>
                        ) : (
                          <TextField
                            fullWidth
                            label={field.label}
                            type="number"
                            value={deductionsData[field.name as keyof DeductionsComponentData] as number}
                            onChange={(e) => {
                              const value = parseFloat(e.target.value) || 0;
                              handleInputChange(field.name as keyof DeductionsComponentData, value);
                            }}
                            InputProps={{
                              startAdornment: <Typography variant="body2" sx={{ mr: 1 }}>₹</Typography>
                            }}
                            helperText={
                              field.maxValue 
                                ? `Max limit: ₹${field.maxValue.toLocaleString('en-IN')}`
                                : undefined
                            }
                            {...(field.maxValue && (deductionsData[field.name as keyof DeductionsComponentData] as number) > field.maxValue && { error: true })}
                          />
                        )}
                      </Grid>
                    ))}
                  </Grid>
                  
                  {/* Section-specific totals */}
                  {step.maxLimit && (
                    <Alert 
                      severity={
                        (index === 1 && calculate80CTotal() > step.maxLimit) ||
                        (index === 2 && calculate80DTotal() > step.maxLimit)
                          ? 'warning' 
                          : 'info'
                      } 
                      sx={{ mt: 2 }}
                    >
                      <Typography variant="body2">
                        Current total: ₹{
                          index === 1 
                            ? calculate80CTotal().toLocaleString('en-IN')
                            : index === 2
                            ? calculate80DTotal().toLocaleString('en-IN')
                            : '0'
                        } | Maximum allowed: ₹{step.maxLimit.toLocaleString('en-IN')}
                      </Typography>
                    </Alert>
                  )}
                  
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

export default DeductionsComponentForm; 