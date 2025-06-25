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
  StepContent,
  FormControlLabel,
  Switch
} from '@mui/material';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { ArrowBack as ArrowBackIcon, Save as SaveIcon } from '@mui/icons-material';
import { getUserRole } from '../../../shared/utils/auth';
import { taxationApi } from '../../../shared/api/taxationApi';

interface SalaryComponentData {
  basic_salary: number;
  dearness_allowance: number;
  hra_provided: number;
  hra_city_type: string;

  special_allowance: number;
  bonus: number;
  commission: number;
  // Additional allowances
  city_compensatory_allowance: number;
  rural_allowance: number;
  proctorship_allowance: number;
  wardenship_allowance: number;
  project_allowance: number;
  deputation_allowance: number;
  interim_relief: number;
  tiffin_allowance: number;
  overtime_allowance: number;
  servant_allowance: number;
  hills_high_altd_allowance: number;
  border_remote_allowance: number;
  transport_employee_allowance: number;
  children_education_allowance: number;
  hostel_allowance: number;
  underground_mines_allowance: number;
  govt_employee_entertainment_allowance: number;
  supreme_high_court_judges_allowance: number;
  judge_compensatory_allowance: number;
  section_10_14_special_allowances: number;
  travel_on_tour_allowance: number;
  tour_daily_charge_allowance: number;
  conveyance_in_performace_of_duties: number;
  helper_in_performace_of_duties: number;
  academic_research: number;
  uniform_allowance: number;
  any_other_allowance_exemption: number;
}

interface ToastState {
  show: boolean;
  message: string;
  severity: 'success' | 'error' | 'warning' | 'info';
}

// Define proper field interfaces
interface BaseField {
  name: string;
  label: string;
  type: string;
}

interface NumberField extends BaseField {
  type: 'number';
  autoCalculate?: boolean;
}

interface SelectField extends BaseField {
  type: 'select';
  options: { value: string; label: string; }[];
}

type FormField = NumberField | SelectField;

interface StepConfig {
  label: string;
  fields: FormField[];
}

// Type guards
const isSelectField = (field: FormField): field is SelectField => {
  return field.type === 'select';
};

const isNumberFieldWithAutoCalculate = (field: FormField): field is NumberField & { autoCalculate: true } => {
  return field.type === 'number' && 'autoCalculate' in field && field.autoCalculate === true;
};

const initialSalaryData: SalaryComponentData = {
  basic_salary: 0,
  dearness_allowance: 0,
  hra_provided: 0,
  hra_city_type: 'non_metro',
  
  special_allowance: 0,
  bonus: 0,
  commission: 0,
  city_compensatory_allowance: 0,
  rural_allowance: 0,
  proctorship_allowance: 0,
  wardenship_allowance: 0,
  project_allowance: 0,
  deputation_allowance: 0,
  interim_relief: 0,
  tiffin_allowance: 0,
  overtime_allowance: 0,
  servant_allowance: 0,
  hills_high_altd_allowance: 0,
  border_remote_allowance: 0,
  transport_employee_allowance: 0,
  children_education_allowance: 0,
  hostel_allowance: 0,
  underground_mines_allowance: 0,
  govt_employee_entertainment_allowance: 0,
  supreme_high_court_judges_allowance: 0,
  judge_compensatory_allowance: 0,
  section_10_14_special_allowances: 0,
  travel_on_tour_allowance: 0,
  tour_daily_charge_allowance: 0,
  conveyance_in_performace_of_duties: 0,
  helper_in_performace_of_duties: 0,
  academic_research: 0,
  uniform_allowance: 0,
  any_other_allowance_exemption: 0
};

const SalaryComponentForm: React.FC = () => {
  const { empId } = useParams<{ empId: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const userRole = getUserRole();
  
  const [loading, setLoading] = useState<boolean>(false);
  const [saving, setSaving] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<ToastState>({ show: false, message: '', severity: 'success' });
  const [salaryData, setSalaryData] = useState<SalaryComponentData>(initialSalaryData);
  const [activeStep, setActiveStep] = useState<number>(0);
  const [autoComputeHRA, setAutoComputeHRA] = useState<boolean>(false);
  
  const taxYear = searchParams.get('year') || '2024-25';
  const mode = searchParams.get('mode') || 'update'; // 'update' or 'new'
  const isAdmin = userRole === 'admin' || userRole === 'superadmin';
  const isNewRevision = mode === 'new';

  // Redirect non-admin users
  useEffect(() => {
    if (!isAdmin) {
      navigate('/taxation');
    }
  }, [isAdmin, navigate]);

  // Load existing salary data (only for update mode)
  useEffect(() => {
    if (empId && !isNewRevision) {
      loadSalaryData();
    } else if (isNewRevision) {
      // For new revision, show info message
      showToast('Creating new salary revision. Enter the updated salary components.', 'info');
    }
  }, [empId, taxYear, isNewRevision]);

  // Auto-calculate HRA when basic salary or DA changes
  useEffect(() => {
    if (autoComputeHRA) {
      const calculatedHRA = computeHRA();
      setSalaryData(prev => ({
        ...prev,
        hra_provided: calculatedHRA
      }));
    }
  }, [salaryData.basic_salary, salaryData.dearness_allowance, autoComputeHRA]);

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

  const loadSalaryData = async (): Promise<void> => {
    try {
      setLoading(true);
      setError(null);
      
      // Try to get existing salary component data
      const response = await taxationApi.getComponent(empId!, taxYear, 'salary');
      
      if (response && response.component_data) {
        // Extract the actual salary data from component_data
        setSalaryData({ ...initialSalaryData, ...response.component_data } as SalaryComponentData);
        showToast('Salary data loaded successfully', 'success');
      } else if (response) {
        // Fallback: if component_data doesn't exist, try using response directly
        setSalaryData({ ...initialSalaryData, ...response } as SalaryComponentData);
        showToast('Salary data loaded successfully', 'success');
      }
    } catch (error: any) {
      if (error.response?.status === 404) {
        // No existing data, use defaults
        showToast('No existing salary data found. Creating new record.', 'info');
      } else {
        setError('Failed to load salary data. Please try again.');
        showToast('Failed to load salary data', 'error');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: keyof SalaryComponentData, value: number): void => {
    setSalaryData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSelectChange = (field: keyof SalaryComponentData, value: string): void => {
    setSalaryData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Compute HRA based on basic salary and DA formula: (Basic+DA) * 0.5
  const computeHRA = (): number => {
    const basic = salaryData.basic_salary || 0;
    const da = salaryData.dearness_allowance || 0;
    const baseAmount = basic + da;
    const defaultRate = 0.5;
    return Math.round(baseAmount * defaultRate);
  };

  const handleSave = async (): Promise<void> => {
    try {
      setSaving(true);
      setError(null);

      const requestData = {
        employee_id: empId!,
        tax_year: taxYear,
        salary_income: salaryData,
        force_new_revision: isNewRevision, // Add flag to indicate new revision
        notes: isNewRevision 
          ? 'New salary revision created via individual component management'
          : 'Updated via individual component management'
      };

      await taxationApi.updateSalaryComponent(requestData);
      
      showToast(
        isNewRevision 
          ? 'New salary revision created successfully' 
          : 'Salary component updated successfully', 
        'success'
      );
      
      // Navigate back to component management
      setTimeout(() => {
        navigate('/taxation/component-management');
      }, 1500);
      
    } catch (error: any) {
      setError('Failed to save salary data. Please try again.');
      showToast('Failed to save salary data', 'error');
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

  const calculateTotalSalary = (): number => {
    // Calculate total salary by adding basic salary + total allowances
    return salaryData.basic_salary + calculateTotalAllowances();
  };

  const calculateTotalAllowances = (): number => {
    // Calculate allowances by explicitly including only allowance fields
    // This is more precise than excluding fields
    const allowanceFields = [
      'dearness_allowance',
              'hra_provided', 
      'special_allowance',
      'bonus',
      'commission',
      'city_compensatory_allowance',
      'rural_allowance',
      'proctorship_allowance',
      'wardenship_allowance',
      'project_allowance',
      'deputation_allowance',
      'interim_relief',
      'tiffin_allowance',
      'overtime_allowance',
      'servant_allowance',
      'hills_high_altd_allowance',
      'border_remote_allowance',
      'transport_employee_allowance',
      'children_education_allowance',
      'hostel_allowance',
      'underground_mines_allowance',
      'govt_employee_entertainment_allowance',
      'supreme_high_court_judges_allowance',
      'judge_compensatory_allowance',
      'section_10_14_special_allowances',
      'travel_on_tour_allowance',
      'tour_daily_charge_allowance',
      'conveyance_in_performace_of_duties',
      'helper_in_performace_of_duties',
      'academic_research',
      'uniform_allowance',
      'any_other_allowance_exemption'
    ];
    
    return allowanceFields.reduce((sum, field) => {
      const value = salaryData[field as keyof SalaryComponentData];
      return sum + (typeof value === 'number' ? value : 0);
    }, 0);
  };

  const steps: StepConfig[] = [
    {
      label: 'Basic Salary Components',
      fields: [
        { name: 'basic_salary', label: 'Basic Salary', type: 'number' } as NumberField,
        { name: 'dearness_allowance', label: 'Dearness Allowance', type: 'number' } as NumberField,
        { name: 'special_allowance', label: 'Special Allowance', type: 'number' } as NumberField,
        { name: 'bonus', label: 'Bonus', type: 'number' } as NumberField,
        { name: 'commission', label: 'Commission', type: 'number' } as NumberField
      ]
    },
    {
      label: 'HRA Components',
      fields: [
        { name: 'hra_provided', label: 'HRA Provided', type: 'number', autoCalculate: true } as NumberField,
        { name: 'hra_city_type', label: 'HRA City Type', type: 'select', options: [
          { value: 'metro', label: 'Metro City' },
          { value: 'non_metro', label: 'Non-Metro City' }
        ]} as SelectField
      ]
    },
    {
      label: 'Additional Allowances',
      fields: [
        { name: 'city_compensatory_allowance', label: 'City Compensatory Allowance', type: 'number' } as NumberField,
        { name: 'rural_allowance', label: 'Rural Allowance', type: 'number' } as NumberField,
        { name: 'project_allowance', label: 'Project Allowance', type: 'number' } as NumberField,
        { name: 'deputation_allowance', label: 'Deputation Allowance', type: 'number' } as NumberField,
        { name: 'overtime_allowance', label: 'Overtime Allowance', type: 'number' } as NumberField,
        { name: 'children_education_allowance', label: 'Children Education Allowance', type: 'number' } as NumberField,
        { name: 'hostel_allowance', label: 'Hostel Allowance', type: 'number' } as NumberField,
        { name: 'uniform_allowance', label: 'Uniform Allowance', type: 'number' } as NumberField
      ]
    },
    {
      label: 'Special Allowances',
      fields: [
        { name: 'proctorship_allowance', label: 'Proctorship Allowance', type: 'number' } as NumberField,
        { name: 'wardenship_allowance', label: 'Wardenship Allowance', type: 'number' } as NumberField,
        { name: 'interim_relief', label: 'Interim Relief', type: 'number' } as NumberField,
        { name: 'tiffin_allowance', label: 'Tiffin Allowance', type: 'number' } as NumberField,
        { name: 'servant_allowance', label: 'Servant Allowance', type: 'number' } as NumberField,
        { name: 'hills_high_altd_allowance', label: 'Hills/High Altitude Allowance', type: 'number' } as NumberField,
        { name: 'border_remote_allowance', label: 'Border/Remote Allowance', type: 'number' } as NumberField,
        { name: 'transport_employee_allowance', label: 'Transport Employee Allowance', type: 'number' } as NumberField
      ]
    },
    {
      label: 'Other Components',
      fields: [
        { name: 'underground_mines_allowance', label: 'Underground Mines Allowance', type: 'number' } as NumberField,
        { name: 'govt_employee_entertainment_allowance', label: 'Govt Employee Entertainment Allowance', type: 'number' } as NumberField,
        { name: 'supreme_high_court_judges_allowance', label: 'Supreme/High Court Judges Allowance', type: 'number' } as NumberField,
        { name: 'judge_compensatory_allowance', label: 'Judge Compensatory Allowance', type: 'number' } as NumberField,
        { name: 'section_10_14_special_allowances', label: 'Section 10(14) Special Allowances', type: 'number' } as NumberField,
        { name: 'travel_on_tour_allowance', label: 'Travel on Tour Allowance', type: 'number' } as NumberField,
        { name: 'tour_daily_charge_allowance', label: 'Tour Daily Charge Allowance', type: 'number' } as NumberField,
        { name: 'conveyance_in_performace_of_duties', label: 'Conveyance in Performance of Duties', type: 'number' } as NumberField,
        { name: 'helper_in_performace_of_duties', label: 'Helper in Performance of Duties', type: 'number' } as NumberField,
        { name: 'academic_research', label: 'Academic Research', type: 'number' } as NumberField,
        { name: 'any_other_allowance_exemption', label: 'Any Other Allowance/Exemption', type: 'number' } as NumberField
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
                {isNewRevision ? 'New Salary Revision' : 'Update Salary Components'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {isNewRevision 
                  ? `Create new salary revision for Employee ID: ${empId} | Tax Year: ${taxYear}`
                  : `Update existing salary components for Employee ID: ${empId} | Tax Year: ${taxYear}`
                }
              </Typography>
              {isNewRevision && (
                <Typography variant="caption" color="primary" sx={{ display: 'block', mt: 1 }}>
                  ℹ️ This will create a new salary entry. The previous salary structure will be preserved.
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
            Salary Summary
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">Basic Salary</Typography>
              <Typography variant="h6">₹{salaryData.basic_salary.toLocaleString('en-IN')}</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">Total Allowances</Typography>
              <Typography variant="h6">₹{calculateTotalAllowances().toLocaleString('en-IN')}</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">HRA Received</Typography>
              <Typography variant="h6">₹{salaryData.hra_provided.toLocaleString('en-IN')}</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">Total Salary</Typography>
              <Typography variant="h6" color="primary">₹{calculateTotalSalary().toLocaleString('en-IN')}</Typography>
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
                              value={salaryData[field.name as keyof SalaryComponentData] as string}
                              label={field.label}
                              onChange={(e: SelectChangeEvent) => 
                                handleSelectChange(field.name as keyof SalaryComponentData, e.target.value)
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
                          <Box>
                            <TextField
                              fullWidth
                              label={field.label}
                              type="number"
                              value={salaryData[field.name as keyof SalaryComponentData] as number}
                              onChange={(e) => {
                                if (isNumberFieldWithAutoCalculate(field) && field.name === 'hra_provided') {
                                  setAutoComputeHRA(false);
                                }
                                handleInputChange(field.name as keyof SalaryComponentData, parseFloat(e.target.value) || 0);
                              }}
                              InputProps={{
                                startAdornment: <Typography variant="body2" sx={{ mr: 1 }}>₹</Typography>
                              }}
                              helperText={
                                isNumberFieldWithAutoCalculate(field) && field.name === 'hra_provided' 
                                  ? autoComputeHRA 
                                    ? "Auto-calculated as (Basic + DA) × 50%" 
                                    : "Enter HRA amount or enable auto-calculation"
                                  : undefined
                              }
                            />
                            {isNumberFieldWithAutoCalculate(field) && field.name === 'hra_provided' && (
                              <FormControlLabel
                                control={
                                  <Switch
                                    checked={autoComputeHRA}
                                    onChange={(e) => setAutoComputeHRA(e.target.checked)}
                                  />
                                }
                                label="Auto-calculate HRA"
                              />
                            )}
                          </Box>
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

export default SalaryComponentForm; 