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
  StepContent,
  FormControlLabel,
  Checkbox
} from '@mui/material';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { ArrowBack as ArrowBackIcon, Save as SaveIcon } from '@mui/icons-material';
import { getUserRole } from '../../../shared/utils/auth';
import { taxationApi } from '../../../shared/api/taxationApi';
import { CURRENT_TAX_YEAR } from '../../../shared/constants/taxation';

interface PerquisitesComponentData {
  // Accommodation
  accommodation_type: string;
  city_population: string;
  license_fees: number;
  employee_rent_payment: number;
  rent_paid_by_employer: number;
  hotel_charges: number;
  stay_days: number;
  furniture_cost: number;
  furniture_employee_payment: number;
  is_furniture_owned_by_employer: boolean;

  // Car
  car_use_type: string;
  engine_capacity_cc: number;
  months_used: number;
  car_cost_to_employer: number;
  other_vehicle_cost: number;
  has_expense_reimbursement: boolean;
  driver_provided: boolean;

  // Medical
  medical_reimbursement_amount: number;
  is_overseas_treatment: boolean;

  // LTA
  lta_amount_claimed: number;
  lta_claimed_count: number;
  public_transport_cost: number;

  // ESOP
  esop_exercise_value: number;
  esop_fair_market_value: number;
  esop_shares_exercised: number;

  // Free Education
  free_education_amount: number;
  is_children_education: boolean;

  // Utilities
  gas_electricity_water_amount: number;

  // Interest Free Loan
  loan_amount: number;
  interest_rate_charged: number;
  sbi_rate: number;

  // Movable Assets
  movable_asset_value: number;
  asset_usage_months: number;

  // Other Perquisites
  lunch_refreshment_amount: number;
  domestic_help_amount: number;
  other_perquisites_amount: number;
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

interface SelectField extends BaseField {
  type: 'select';
  options: { value: string; label: string; }[];
}

interface CheckboxField extends BaseField {
  type: 'checkbox';
}

type FormField = NumberField | SelectField | CheckboxField;

interface StepConfig {
  label: string;
  fields: FormField[];
}

const isSelectField = (field: FormField): field is SelectField => {
  return field.type === 'select';
};

const isCheckboxField = (field: FormField): field is CheckboxField => {
  return field.type === 'checkbox';
};

const initialPerquisitesData: PerquisitesComponentData = {
  // Accommodation
  accommodation_type: 'Employer-Owned',
  city_population: 'Below 15 lakhs',
  license_fees: 0,
  employee_rent_payment: 0,
  rent_paid_by_employer: 0,
  hotel_charges: 0,
  stay_days: 0,
  furniture_cost: 0,
  furniture_employee_payment: 0,
  is_furniture_owned_by_employer: false,

  // Car
  car_use_type: 'Personal',
  engine_capacity_cc: 1600,
  months_used: 12,
  car_cost_to_employer: 0,
  other_vehicle_cost: 0,
  has_expense_reimbursement: false,
  driver_provided: false,

  // Medical
  medical_reimbursement_amount: 0,
  is_overseas_treatment: false,

  // LTA
  lta_amount_claimed: 0,
  lta_claimed_count: 0,
  public_transport_cost: 0,

  // ESOP
  esop_exercise_value: 0,
  esop_fair_market_value: 0,
  esop_shares_exercised: 0,

  // Free Education
  free_education_amount: 0,
  is_children_education: true,

  // Utilities
  gas_electricity_water_amount: 0,

  // Interest Free Loan
  loan_amount: 0,
  interest_rate_charged: 0,
  sbi_rate: 6.5,

  // Movable Assets
  movable_asset_value: 0,
  asset_usage_months: 12,

  // Other Perquisites
  lunch_refreshment_amount: 0,
  domestic_help_amount: 0,
  other_perquisites_amount: 0
};

// Function to flatten nested backend response to flat frontend structure
const flattenPerquisitesData = (nestedData: any): PerquisitesComponentData => {
  console.log('Flattening perquisites data:', nestedData);
  const flattened: PerquisitesComponentData = { ...initialPerquisitesData };
  
  try {
    // Accommodation
    if (nestedData.accommodation) {
      console.log('Processing accommodation:', nestedData.accommodation);
      flattened.accommodation_type = nestedData.accommodation.accommodation_type || 'Employer-Owned';
      flattened.city_population = nestedData.accommodation.city_population || 'Below 15 lakhs';
      flattened.license_fees = nestedData.accommodation.license_fees || 0;
      flattened.employee_rent_payment = nestedData.accommodation.employee_rent_payment || 0;
      flattened.rent_paid_by_employer = nestedData.accommodation.rent_paid_by_employer || 0;
      flattened.hotel_charges = nestedData.accommodation.hotel_charges || 0;
      flattened.stay_days = nestedData.accommodation.stay_days || 0;
      flattened.furniture_cost = nestedData.accommodation.furniture_cost || 0;
      flattened.furniture_employee_payment = nestedData.accommodation.furniture_employee_payment || 0;
      flattened.is_furniture_owned_by_employer = nestedData.accommodation.is_furniture_owned_by_employer || false;
    }
    
    // Car
    if (nestedData.car) {
      console.log('Processing car:', nestedData.car);
      flattened.car_use_type = nestedData.car.car_use_type || 'Personal';
      flattened.engine_capacity_cc = nestedData.car.engine_capacity_cc || 1600;
      flattened.months_used = nestedData.car.months_used || 12;
      flattened.car_cost_to_employer = nestedData.car.car_cost_to_employer || 0;
      flattened.other_vehicle_cost = nestedData.car.other_vehicle_cost || 0;
      flattened.has_expense_reimbursement = nestedData.car.has_expense_reimbursement || false;
      flattened.driver_provided = nestedData.car.driver_provided || false;
    }
    
    // Medical Reimbursement
    if (nestedData.medical_reimbursement) {
      console.log('Processing medical reimbursement:', nestedData.medical_reimbursement);
      flattened.medical_reimbursement_amount = nestedData.medical_reimbursement.medical_reimbursement_amount || 0;
      flattened.is_overseas_treatment = nestedData.medical_reimbursement.is_overseas_treatment || false;
    }
    
    // LTA
    if (nestedData.lta) {
      console.log('Processing LTA:', nestedData.lta);
      flattened.lta_amount_claimed = nestedData.lta.lta_amount_claimed || 0;
      flattened.lta_claimed_count = nestedData.lta.lta_claimed_count || 0;
      flattened.public_transport_cost = nestedData.lta.public_transport_cost || 0;
    }
    
    // ESOP
    if (nestedData.esop) {
      console.log('Processing ESOP:', nestedData.esop);
      flattened.esop_exercise_value = nestedData.esop.exercise_price || 0;
      flattened.esop_fair_market_value = nestedData.esop.allotment_price || 0;
      flattened.esop_shares_exercised = nestedData.esop.shares_exercised || 0;
    }
    
    // Free Education
    if (nestedData.free_education) {
      console.log('Processing free education:', nestedData.free_education);
      flattened.free_education_amount = (nestedData.free_education.monthly_expenses_child1 || 0) + (nestedData.free_education.monthly_expenses_child2 || 0);
      flattened.is_children_education = true;
    }
    
    // Utilities
    if (nestedData.utilities) {
      console.log('Processing utilities:', nestedData.utilities);
      flattened.gas_electricity_water_amount = (nestedData.utilities.gas_paid_by_employer || 0) + 
                                              (nestedData.utilities.electricity_paid_by_employer || 0) + 
                                              (nestedData.utilities.water_paid_by_employer || 0);
    }
    
    // Interest Free Loan
    if (nestedData.interest_free_loan) {
      console.log('Processing interest free loan:', nestedData.interest_free_loan);
      flattened.loan_amount = nestedData.interest_free_loan.loan_amount || 0;
      flattened.interest_rate_charged = nestedData.interest_free_loan.company_interest_rate || 0;
      flattened.sbi_rate = nestedData.interest_free_loan.sbi_interest_rate || 6.5;
    }
    
    // Movable Assets
    if (nestedData.movable_asset_usage) {
      console.log('Processing movable assets:', nestedData.movable_asset_usage);
      flattened.movable_asset_value = nestedData.movable_asset_usage.asset_value || 0;
      flattened.asset_usage_months = nestedData.movable_asset_usage.usage_months || 12;
    }
    
    // Lunch Refreshment
    if (nestedData.lunch_refreshment) {
      console.log('Processing lunch refreshment:', nestedData.lunch_refreshment);
      flattened.lunch_refreshment_amount = nestedData.lunch_refreshment.employer_cost || 0;
    }
    
    // Domestic Help
    if (nestedData.domestic_help) {
      console.log('Processing domestic help:', nestedData.domestic_help);
      flattened.domestic_help_amount = nestedData.domestic_help.domestic_help_paid_by_employer || 0;
    }
    
    // Other Perquisites
    if (nestedData.other_perquisites) {
      console.log('Processing other perquisites:', nestedData.other_perquisites);
      flattened.other_perquisites_amount = nestedData.other_perquisites || 0;
    }
    
    console.log('Flattened perquisites data:', flattened);
    return flattened;
    
  } catch (error) {
    console.error('Error flattening perquisites data:', error);
    return initialPerquisitesData;
  }
};

const PerquisitesComponentForm: React.FC = () => {
  const { empId } = useParams<{ empId: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const userRole = getUserRole();
  
  const [loading, setLoading] = useState<boolean>(false);
  const [saving, setSaving] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<ToastState>({ show: false, message: '', severity: 'success' });
  const [perquisitesData, setPerquisitesData] = useState<PerquisitesComponentData>(initialPerquisitesData);
  const [activeStep, setActiveStep] = useState<number>(0);
  
  const taxYear = searchParams.get('year') || CURRENT_TAX_YEAR;
  const mode = searchParams.get('mode') || 'update';
  const isAdmin = userRole === 'admin' || userRole === 'superadmin';
  const isNewRevision = mode === 'new';

  // Redirect non-admin users
  useEffect(() => {
    if (!isAdmin) {
      navigate('/taxation');
    }
  }, [isAdmin, navigate]);

  const loadPerquisitesData = useCallback(async (): Promise<void> => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await taxationApi.getComponent(empId!, taxYear, 'perquisites');
      
      if (response && response.component_data) {
        console.log('Backend response component_data:', response.component_data);
        const flattenedData = flattenPerquisitesData(response.component_data);
        console.log('Flattened data:', flattenedData);
        setPerquisitesData(flattenedData);
        showToast('Perquisites data loaded successfully', 'success');
      } else if (response) {
        console.log('Backend response:', response);
        const flattenedData = flattenPerquisitesData(response);
        console.log('Flattened data:', flattenedData);
        setPerquisitesData(flattenedData);
        showToast('Perquisites data loaded successfully', 'success');
      }
    } catch (error: any) {
      if (error.response?.status === 404) {
        showToast('No existing perquisites data found. Creating new record.', 'info');
      } else {
        setError('Failed to load perquisites data. Please try again.');
        showToast('Failed to load perquisites data', 'error');
      }
    } finally {
      setLoading(false);
    }
  }, [empId, taxYear]);

  useEffect(() => {
    if (empId && !isNewRevision) {
      loadPerquisitesData();
    } else if (isNewRevision) {
      showToast('Creating new perquisites revision. Enter the updated perquisites data.', 'info');
    }
  }, [empId, taxYear, isNewRevision, loadPerquisitesData]);

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

  const handleInputChange = (field: keyof PerquisitesComponentData, value: number | string | boolean): void => {
    setPerquisitesData(prev => ({
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
        perquisites: perquisitesData,
        force_new_revision: isNewRevision,
        notes: isNewRevision 
          ? 'New perquisites revision created via individual component management'
          : 'Updated via individual component management'
      };

      await taxationApi.updatePerquisitesComponent(requestData);
      
      showToast(
        isNewRevision 
          ? 'New perquisites revision created successfully' 
          : 'Perquisites component updated successfully', 
        'success'
      );
      
      setTimeout(() => {
        navigate('/taxation/component-management');
      }, 1500);
      
    } catch (error: any) {
      setError('Failed to save perquisites data. Please try again.');
      showToast('Failed to save perquisites data', 'error');
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

  const calculateTotalPerquisites = (): number => {
    // Calculate total perquisites value based on type
    let total = 0;
    total += perquisitesData.medical_reimbursement_amount;
    total += perquisitesData.lta_amount_claimed;
    total += perquisitesData.esop_exercise_value;
    total += perquisitesData.free_education_amount;
    total += perquisitesData.gas_electricity_water_amount;
    total += perquisitesData.movable_asset_value;
    total += perquisitesData.lunch_refreshment_amount;
    total += perquisitesData.domestic_help_amount;
    total += perquisitesData.other_perquisites_amount;
    return total;
  };

  const steps: StepConfig[] = [
    {
      label: 'Accommodation',
      fields: [
        { name: 'accommodation_type', label: 'Accommodation Type', type: 'select', options: [
          { value: 'Employer-Owned', label: 'Employer-Owned' },
          { value: 'Government', label: 'Government' },
          { value: 'Employer-Leased', label: 'Employer-Leased' },
          { value: 'Hotel', label: 'Hotel' }
        ]} as SelectField,
        { name: 'city_population', label: 'City Population', type: 'select', options: [
          { value: 'Above 40 lakhs', label: 'Above 40 lakhs' },
          { value: 'Between 15-40 lakhs', label: 'Between 15-40 lakhs' },
          { value: 'Below 15 lakhs', label: 'Below 15 lakhs' }
        ]} as SelectField,
        { name: 'license_fees', label: 'License Fees (Government)', type: 'number' } as NumberField,
        { name: 'employee_rent_payment', label: 'Employee Rent Payment', type: 'number' } as NumberField,
        { name: 'rent_paid_by_employer', label: 'Rent Paid by Employer', type: 'number' } as NumberField,
        { name: 'furniture_cost', label: 'Furniture Cost', type: 'number' } as NumberField,
        { name: 'is_furniture_owned_by_employer', label: 'Furniture Owned by Employer', type: 'checkbox' } as CheckboxField
      ]
    },
    {
      label: 'Car & Transport',
      fields: [
        { name: 'car_use_type', label: 'Car Usage Type', type: 'select', options: [
          { value: 'Personal', label: 'Personal Only' },
          { value: 'Official', label: 'Official Only' },
          { value: 'Mixed', label: 'Personal & Official' }
        ]} as SelectField,
        { name: 'engine_capacity_cc', label: 'Engine Capacity (CC)', type: 'number' } as NumberField,
        { name: 'months_used', label: 'Months Used', type: 'number' } as NumberField,
        { name: 'car_cost_to_employer', label: 'Car Cost to Employer', type: 'number' } as NumberField,
        { name: 'other_vehicle_cost', label: 'Other Vehicle Cost', type: 'number' } as NumberField,
        { name: 'has_expense_reimbursement', label: 'Expense Reimbursement', type: 'checkbox' } as CheckboxField,
        { name: 'driver_provided', label: 'Driver Provided', type: 'checkbox' } as CheckboxField
      ]
    },
    {
      label: 'Medical & LTA',
      fields: [
        { name: 'medical_reimbursement_amount', label: 'Medical Reimbursement Amount', type: 'number' } as NumberField,
        { name: 'is_overseas_treatment', label: 'Overseas Treatment', type: 'checkbox' } as CheckboxField,
        { name: 'lta_amount_claimed', label: 'LTA Amount Claimed', type: 'number' } as NumberField,
        { name: 'lta_claimed_count', label: 'LTA Claims Count', type: 'number' } as NumberField,
        { name: 'public_transport_cost', label: 'Public Transport Cost (for same distance)', type: 'number' } as NumberField
      ]
    },
    {
      label: 'ESOP & Education',
      fields: [
        { name: 'esop_exercise_value', label: 'ESOP Exercise Value', type: 'number' } as NumberField,
        { name: 'esop_fair_market_value', label: 'ESOP Fair Market Value', type: 'number' } as NumberField,
        { name: 'esop_shares_exercised', label: 'ESOP Shares Exercised', type: 'number' } as NumberField,
        { name: 'free_education_amount', label: 'Free Education Amount', type: 'number' } as NumberField,
        { name: 'is_children_education', label: 'Children Education', type: 'checkbox' } as CheckboxField
      ]
    },
    {
      label: 'Other Benefits',
      fields: [
        { name: 'gas_electricity_water_amount', label: 'Gas/Electricity/Water Amount', type: 'number' } as NumberField,
        { name: 'loan_amount', label: 'Interest-free Loan Amount', type: 'number' } as NumberField,
        { name: 'interest_rate_charged', label: 'Interest Rate Charged (%)', type: 'number' } as NumberField,
        { name: 'sbi_rate', label: 'SBI Rate (%)', type: 'number' } as NumberField,
        { name: 'movable_asset_value', label: 'Movable Assets Value', type: 'number' } as NumberField,
        { name: 'lunch_refreshment_amount', label: 'Lunch/Refreshment Amount', type: 'number' } as NumberField,
        { name: 'domestic_help_amount', label: 'Domestic Help Amount', type: 'number' } as NumberField,
        { name: 'other_perquisites_amount', label: 'Other Perquisites Amount', type: 'number' } as NumberField
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
                {isNewRevision ? 'New Perquisites Revision' : 'Update Perquisites Components'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {isNewRevision 
                  ? `Create new perquisites revision for Employee ID: ${empId} | Tax Year: ${taxYear}`
                  : `Update existing perquisites components for Employee ID: ${empId} | Tax Year: ${taxYear}`
                }
              </Typography>
              {isNewRevision && (
                <Typography variant="caption" color="primary" sx={{ display: 'block', mt: 1 }}>
                  ℹ️ This will create a new perquisites entry. The previous perquisites structure will be preserved.
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
            Perquisites Summary
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">Medical Reimbursement</Typography>
              <Typography variant="h6">₹{perquisitesData.medical_reimbursement_amount.toLocaleString('en-IN')}</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">LTA Claimed</Typography>
              <Typography variant="h6">₹{perquisitesData.lta_amount_claimed.toLocaleString('en-IN')}</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">ESOP Value</Typography>
              <Typography variant="h6">₹{perquisitesData.esop_exercise_value.toLocaleString('en-IN')}</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">Total Perquisites</Typography>
              <Typography variant="h6" color="primary">₹{calculateTotalPerquisites().toLocaleString('en-IN')}</Typography>
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
                              value={perquisitesData[field.name as keyof PerquisitesComponentData] as string}
                              label={field.label}
                              onChange={(e: SelectChangeEvent) => 
                                handleInputChange(field.name as keyof PerquisitesComponentData, e.target.value)
                              }
                            >
                              {field.options.map((option) => (
                                <MenuItem key={option.value} value={option.value}>
                                  {option.label}
                                </MenuItem>
                              ))}
                            </Select>
                          </FormControl>
                        ) : isCheckboxField(field) ? (
                          <FormControlLabel
                            control={
                              <Checkbox
                                checked={perquisitesData[field.name as keyof PerquisitesComponentData] as boolean}
                                onChange={(e) => 
                                  handleInputChange(field.name as keyof PerquisitesComponentData, e.target.checked)
                                }
                              />
                            }
                            label={field.label}
                          />
                        ) : (
                          <TextField
                            fullWidth
                            label={field.label}
                            type="number"
                            value={perquisitesData[field.name as keyof PerquisitesComponentData] as number}
                            onChange={(e) => {
                              handleInputChange(field.name as keyof PerquisitesComponentData, parseFloat(e.target.value) || 0);
                            }}
                            InputProps={{
                              startAdornment: field.name.includes('rate') || field.name.includes('percent') 
                                ? <Typography variant="body2" sx={{ mr: 1 }}>%</Typography>
                                : <Typography variant="body2" sx={{ mr: 1 }}>₹</Typography>
                            }}
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

export default PerquisitesComponentForm; 