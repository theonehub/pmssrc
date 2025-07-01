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
import taxationApi from '../../../shared/api/taxationApi';
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
  months_used_other_vehicle: number;
  car_cost_to_employer: number;
  other_vehicle_cost: number;
  has_expense_reimbursement: boolean;
  driver_provided: boolean;

  // LTA
  lta_amount_claimed: number;
  lta_claimed_count: number;
  public_transport_cost: number;
  travel_mode: string;

  // ESOP
  esop_exercise_value: number;
  esop_fair_market_value: number;
  esop_shares_exercised: number;

  // Free Education - Individual components
  monthly_expenses_child1: number;
  monthly_expenses_child2: number;
  months_child1: number;
  months_child2: number;
  employer_maintained_1st_child: boolean;
  employer_maintained_2nd_child: boolean;
  
  // Legacy free education fields for backward compatibility
  free_education_amount: number;
  is_children_education: boolean;

  // Utilities - Individual components
  gas_paid_by_employer: number;
  electricity_paid_by_employer: number;
  water_paid_by_employer: number;
  gas_paid_by_employee: number;
  electricity_paid_by_employee: number;
  water_paid_by_employee: number;
  is_gas_manufactured_by_employer: boolean;
  is_electricity_manufactured_by_employer: boolean;
  is_water_manufactured_by_employer: boolean;
  
  // Legacy utilities field for backward compatibility
  gas_electricity_water_amount: number;

  // Interest Free Loan
  loan_amount: number;
  emi_amount: number;
  company_interest_rate: number;
  sbi_interest_rate: number;
  loan_type: string;
  loan_start_date: string;

  // Movable Asset Usage - Individual components
  movable_asset_type: string;
  movable_asset_usage_value: number;
  movable_asset_hire_cost: number;
  movable_asset_employee_payment: number;
  movable_asset_is_employer_owned: boolean;
  
  // Movable Asset Transfer - Individual components
  movable_asset_transfer_type: string;
  movable_asset_transfer_cost: number;
  movable_asset_years_of_use: number;
  movable_asset_transfer_employee_payment: number;
  
  // Legacy movable assets fields for backward compatibility
  movable_asset_value: number;
  asset_usage_months: number;

  // Lunch Refreshment - Individual components
  lunch_employer_cost: number;
  lunch_employee_payment: number;
  lunch_meal_days_per_year: number;
  
  // Legacy lunch refreshment field for backward compatibility
  lunch_refreshment_amount: number;
  
  // Domestic Help - Individual components
  domestic_help_paid_by_employer: number;
  domestic_help_paid_by_employee: number;
  
  // Other Perquisites
  other_perquisites_amount: number;
  
  // Monetary Benefits - Individual components
  monetary_amount_paid_by_employer: number;
  expenditure_for_official_purpose: number;
  amount_paid_by_employee: number;
  
  // Club Expenses - Individual components
  club_expenses_paid_by_employer: number;
  club_expenses_paid_by_employee: number;
  club_expenses_for_official_purpose: number;
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

interface DateField extends BaseField {
  type: 'date';
}

type FormField = NumberField | SelectField | CheckboxField | DateField;

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

const isDateField = (field: FormField): field is DateField => {
  return field.type === 'date';
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
  months_used_other_vehicle: 12,
  car_cost_to_employer: 0,
  other_vehicle_cost: 0,
  has_expense_reimbursement: false,
  driver_provided: false,


  // LTA
  lta_amount_claimed: 0,
  lta_claimed_count: 0,
  public_transport_cost: 0,
  travel_mode: 'Air',

  // ESOP
  esop_exercise_value: 0,
  esop_fair_market_value: 0,
  esop_shares_exercised: 0,

  // Free Education - Individual components
  monthly_expenses_child1: 0,
  monthly_expenses_child2: 0,
  months_child1: 12,
  months_child2: 12,
  employer_maintained_1st_child: false,
  employer_maintained_2nd_child: false,
  
  // Legacy free education fields for backward compatibility
  free_education_amount: 0,
  is_children_education: true,

  // Utilities - Individual components
  gas_paid_by_employer: 0,
  electricity_paid_by_employer: 0,
  water_paid_by_employer: 0,
  gas_paid_by_employee: 0,
  electricity_paid_by_employee: 0,
  water_paid_by_employee: 0,
  is_gas_manufactured_by_employer: false,
  is_electricity_manufactured_by_employer: false,
  is_water_manufactured_by_employer: false,
  
  // Legacy utilities field for backward compatibility
  gas_electricity_water_amount: 0,

  // Interest Free Loan
  loan_amount: 0,
  emi_amount: 0,
  company_interest_rate: 0,
  sbi_interest_rate: 6.5,
  loan_type: 'Personal',
  loan_start_date: '',

  // Movable Asset Usage - Individual components
  movable_asset_type: '',
  movable_asset_usage_value: 0,
  movable_asset_hire_cost: 0,
  movable_asset_employee_payment: 0,
  movable_asset_is_employer_owned: false,
  
  // Movable Asset Transfer - Individual components
  movable_asset_transfer_type: '',
  movable_asset_transfer_cost: 0,
  movable_asset_years_of_use: 0,
  movable_asset_transfer_employee_payment: 0,
  
  // Legacy movable assets fields for backward compatibility
  movable_asset_value: 0,
  asset_usage_months: 12,

  // Lunch Refreshment - Individual components
  lunch_employer_cost: 0,
  lunch_employee_payment: 0,
  lunch_meal_days_per_year: 250,
  
  // Legacy lunch refreshment field for backward compatibility
  lunch_refreshment_amount: 0,
  
  // Domestic Help - Individual components
  domestic_help_paid_by_employer: 0,
  domestic_help_paid_by_employee: 0,
  
  // Other Perquisites
  other_perquisites_amount: 0,
  
  // Monetary Benefits - Individual components
  monetary_amount_paid_by_employer: 0,
  expenditure_for_official_purpose: 0,
  amount_paid_by_employee: 0,
  
  // Club Expenses - Individual components
  club_expenses_paid_by_employer: 0,
  club_expenses_paid_by_employee: 0,
  club_expenses_for_official_purpose: 0
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
      flattened.months_used_other_vehicle = nestedData.car.months_used_other_vehicle || 12;
      flattened.car_cost_to_employer = nestedData.car.car_cost_to_employer || 0;
      flattened.other_vehicle_cost = nestedData.car.other_vehicle_cost || 0;
      flattened.has_expense_reimbursement = nestedData.car.has_expense_reimbursement || false;
      flattened.driver_provided = nestedData.car.driver_provided || false;
    }
    
    // LTA
    if (nestedData.lta) {
      console.log('Processing LTA:', nestedData.lta);
      flattened.lta_amount_claimed = nestedData.lta.lta_amount_claimed || 0;
      flattened.lta_claimed_count = nestedData.lta.lta_claimed_count || 0;
      flattened.public_transport_cost = nestedData.lta.public_transport_cost || 0;
      flattened.travel_mode = nestedData.lta.travel_mode || 'Air';
    }
    
    // ESOP
    if (nestedData.esop) {
      console.log('Processing ESOP:', nestedData.esop);
      flattened.esop_exercise_value = nestedData.esop.exercise_price || 0;
      flattened.esop_fair_market_value = nestedData.esop.allotment_price || 0;
      flattened.esop_shares_exercised = nestedData.esop.shares_exercised || 0;
    }
    
    // Free Education - Individual components
    if (nestedData.free_education) {
      console.log('Processing free education:', nestedData.free_education);
      flattened.monthly_expenses_child1 = nestedData.free_education.monthly_expenses_child1 || 0;
      flattened.monthly_expenses_child2 = nestedData.free_education.monthly_expenses_child2 || 0;
      flattened.months_child1 = nestedData.free_education.months_child1 || 12;
      flattened.months_child2 = nestedData.free_education.months_child2 || 12;
      flattened.employer_maintained_1st_child = nestedData.free_education.employer_maintained_1st_child || false;
      flattened.employer_maintained_2nd_child = nestedData.free_education.employer_maintained_2nd_child || false;
      
    }
    
    // Utilities - Individual components
    if (nestedData.utilities) {
      console.log('Processing utilities:', nestedData.utilities);
      flattened.gas_paid_by_employer = nestedData.utilities.gas_paid_by_employer || 0;
      flattened.electricity_paid_by_employer = nestedData.utilities.electricity_paid_by_employer || 0;
      flattened.water_paid_by_employer = nestedData.utilities.water_paid_by_employer || 0;
      flattened.gas_paid_by_employee = nestedData.utilities.gas_paid_by_employee || 0;
      flattened.electricity_paid_by_employee = nestedData.utilities.electricity_paid_by_employee || 0;
      flattened.water_paid_by_employee = nestedData.utilities.water_paid_by_employee || 0;
      flattened.is_gas_manufactured_by_employer = nestedData.utilities.is_gas_manufactured_by_employer || false;
      flattened.is_electricity_manufactured_by_employer = nestedData.utilities.is_electricity_manufactured_by_employer || false;
      flattened.is_water_manufactured_by_employer = nestedData.utilities.is_water_manufactured_by_employer || false;
      
      // Calculate legacy field for backward compatibility
      flattened.gas_electricity_water_amount = (flattened.gas_paid_by_employer || 0) + 
                                              (flattened.electricity_paid_by_employer || 0) + 
                                              (flattened.water_paid_by_employer || 0);
    }
    
    // Interest Free Loan
    if (nestedData.interest_free_loan) {
      console.log('Processing interest free loan:', nestedData.interest_free_loan);
      flattened.loan_amount = nestedData.interest_free_loan.loan_amount || 0;
      flattened.emi_amount = nestedData.interest_free_loan.emi_amount || 0;
      flattened.company_interest_rate = nestedData.interest_free_loan.company_interest_rate || 0;
      flattened.sbi_interest_rate = nestedData.interest_free_loan.sbi_interest_rate || 6.5;
      flattened.loan_type = nestedData.interest_free_loan.loan_type || 'Personal';
      flattened.loan_start_date = nestedData.interest_free_loan.loan_start_date || '';
    }
    
    // Movable Asset Usage - Individual components
    if (nestedData.movable_asset_usage) {
      console.log('Processing movable asset usage:', nestedData.movable_asset_usage);
      flattened.movable_asset_type = nestedData.movable_asset_usage.asset_type || 'Electronics';
      flattened.movable_asset_usage_value = nestedData.movable_asset_usage.asset_value || 0;
      flattened.movable_asset_hire_cost = nestedData.movable_asset_usage.hire_cost || 0;
      flattened.movable_asset_employee_payment = nestedData.movable_asset_usage.employee_payment || 0;
      flattened.movable_asset_is_employer_owned = nestedData.movable_asset_usage.is_employer_owned || true;
      
      // Set legacy field for backward compatibility
      flattened.movable_asset_value = flattened.movable_asset_usage_value;
    }
    
    // Movable Asset Transfer - Individual components
    if (nestedData.movable_asset_transfer) {
      console.log('Processing movable asset transfer:', nestedData.movable_asset_transfer);
      flattened.movable_asset_transfer_type = nestedData.movable_asset_transfer.asset_type || 'Electronics';
      flattened.movable_asset_transfer_cost = nestedData.movable_asset_transfer.asset_cost || 0;
      flattened.movable_asset_years_of_use = nestedData.movable_asset_transfer.years_of_use || 1;
      flattened.movable_asset_transfer_employee_payment = nestedData.movable_asset_transfer.employee_payment || 0;
    }
    
    // Lunch Refreshment - Individual components
    if (nestedData.lunch_refreshment) {
      console.log('Processing lunch refreshment:', nestedData.lunch_refreshment);
      flattened.lunch_employer_cost = nestedData.lunch_refreshment.employer_cost || 0;
      flattened.lunch_employee_payment = nestedData.lunch_refreshment.employee_payment || 0;
      flattened.lunch_meal_days_per_year = nestedData.lunch_refreshment.meal_days_per_year || 250;
      
      // Set legacy field for backward compatibility
      flattened.lunch_refreshment_amount = flattened.lunch_employer_cost;
    }
    
    // Domestic Help
    if (nestedData.domestic_help) {
      console.log('Processing domestic help:', nestedData.domestic_help);
      flattened.domestic_help_paid_by_employer = nestedData.domestic_help.domestic_help_paid_by_employer || 0;
      flattened.domestic_help_paid_by_employee = nestedData.domestic_help.domestic_help_paid_by_employee || 0;
    }
    
    // Other Perquisites
    if (nestedData.other_perquisites) {
      console.log('Processing other perquisites:', nestedData.other_perquisites);
      flattened.other_perquisites_amount = nestedData.other_perquisites || 0;
    }
    
    // Monetary Benefits - Individual components
    if (nestedData.monetary_benefits) {
      console.log('Processing monetary benefits:', nestedData.monetary_benefits);
      flattened.monetary_amount_paid_by_employer = nestedData.monetary_benefits.monetary_amount_paid_by_employer || 0;
      flattened.expenditure_for_official_purpose = nestedData.monetary_benefits.expenditure_for_official_purpose || 0;
      flattened.amount_paid_by_employee = nestedData.monetary_benefits.amount_paid_by_employee || 0;
    }
    
    // Club Expenses - Individual components
    if (nestedData.club_expenses) {
      console.log('Processing club expenses:', nestedData.club_expenses);
      flattened.club_expenses_paid_by_employer = nestedData.club_expenses.club_expenses_paid_by_employer || 0;
      flattened.club_expenses_paid_by_employee = nestedData.club_expenses.club_expenses_paid_by_employee || 0;
      flattened.club_expenses_for_official_purpose = nestedData.club_expenses.club_expenses_for_official_purpose || 0;
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
    total += perquisitesData.lta_amount_claimed;
    total += perquisitesData.esop_exercise_value;
    
    // Calculate free education total from individual components
    const freeEducationTotal = (perquisitesData.monthly_expenses_child1 * perquisitesData.months_child1 * (perquisitesData.employer_maintained_1st_child ? 1 : 0)) +
                              (perquisitesData.monthly_expenses_child2 * perquisitesData.months_child2 * (perquisitesData.employer_maintained_2nd_child ? 1 : 0));
    total += freeEducationTotal;
    
    // Calculate utilities total from individual components
    const utilitiesTotal = (perquisitesData.gas_paid_by_employer + 
                           perquisitesData.electricity_paid_by_employer + 
                           perquisitesData.water_paid_by_employer) -
                          (perquisitesData.gas_paid_by_employee + 
                           perquisitesData.electricity_paid_by_employee + 
                           perquisitesData.water_paid_by_employee);
    total += Math.max(0, utilitiesTotal);
    
    // Calculate movable asset usage total from individual components
    const movableAssetUsageTotal = perquisitesData.movable_asset_is_employer_owned 
      ? Math.max(0, (perquisitesData.movable_asset_usage_value * 0.1) - perquisitesData.movable_asset_employee_payment) // 10% of asset value
      : Math.max(0, perquisitesData.movable_asset_hire_cost - perquisitesData.movable_asset_employee_payment); // Full hire cost
    total += movableAssetUsageTotal;
    
    // Calculate movable asset transfer total from individual components
    const depreciationRate = perquisitesData.movable_asset_transfer_type === 'Electronics' ? 0.5 
      : perquisitesData.movable_asset_transfer_type === 'Motor Vehicle' ? 0.2 : 0.1;
    const annualDepreciation = perquisitesData.movable_asset_transfer_cost * depreciationRate;
    const totalDepreciation = annualDepreciation * perquisitesData.movable_asset_years_of_use;
    const depreciatedValue = Math.max(0, perquisitesData.movable_asset_transfer_cost - totalDepreciation);
    const movableAssetTransferTotal = Math.max(0, depreciatedValue - perquisitesData.movable_asset_transfer_employee_payment);
    total += movableAssetTransferTotal;
    
    // Calculate lunch refreshment total from individual components
    const lunchRefreshmentTotal = Math.max(0, perquisitesData.lunch_employer_cost - perquisitesData.lunch_employee_payment);
    total += lunchRefreshmentTotal;
    
    // Calculate domestic help total from individual components
    const domesticHelpTotal = Math.max(0, perquisitesData.domestic_help_paid_by_employer - perquisitesData.domestic_help_paid_by_employee);
    total += domesticHelpTotal;
    
    // Calculate monetary benefits total from individual components
    const monetaryBenefitsTotal = Math.max(0, perquisitesData.monetary_amount_paid_by_employer - perquisitesData.expenditure_for_official_purpose - perquisitesData.amount_paid_by_employee);
    total += monetaryBenefitsTotal;
    
    // Calculate club expenses total from individual components
    const clubExpensesTotal = Math.max(0, perquisitesData.club_expenses_paid_by_employer - perquisitesData.club_expenses_paid_by_employee - perquisitesData.club_expenses_for_official_purpose);
    total += clubExpensesTotal;
    
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
        { name: 'months_used_other_vehicle', label: 'Months Used Other Vehicle', type: 'number' } as NumberField,
        { name: 'car_cost_to_employer', label: 'Car Cost to Employer', type: 'number' } as NumberField,
        { name: 'other_vehicle_cost', label: 'Other Vehicle Cost', type: 'number' } as NumberField,
        { name: 'has_expense_reimbursement', label: 'Expense Reimbursement', type: 'checkbox' } as CheckboxField,
        { name: 'driver_provided', label: 'Driver Provided', type: 'checkbox' } as CheckboxField
      ]
    },
    {
      label: 'LTA',
      fields: [
        { name: 'travel_mode', label: 'Travel Mode', type: 'select', options: [
          { value: 'Air', label: 'Air' },
          { value: 'Railways', label: 'Railways' },
          { value: 'Bus', label: 'Bus' },
          { value: 'Other', label: 'Other' }
        ]} as SelectField,
        { name: 'lta_amount_claimed', label: 'LTA Amount Claimed', type: 'number' } as NumberField,
        { name: 'lta_claimed_count', label: 'LTA Claims Count', type: 'number' } as NumberField,
        { name: 'public_transport_cost', label: 'Public Transport Cost (for same distance)', type: 'number' } as NumberField
      ]
    },
    {
      label: 'Interest Free/Concessional Loan',
      fields: [
        { name: 'loan_amount', label: 'Interest-free Loan Amount', type: 'number' } as NumberField,
        { name: 'emi_amount', label: 'EMI Amount', type: 'number' } as NumberField,
        { name: 'company_interest_rate', label: 'Interest Rate Charged (%)', type: 'number' } as NumberField,
        { name: 'sbi_interest_rate', label: 'SBI Rate (%)', type: 'number' } as NumberField,
        { name: 'loan_type', label: 'Loan Type', type: 'select', options: [
          { value: 'Personal', label: 'Personal' },
          { value: 'Medical', label: 'Medical' },
          { value: 'Education', label: 'Education' },
          { value: 'Housing', label: 'Housing' },
          { value: 'Vehicle', label: 'Vehicle' },
          { value: 'Other', label: 'Other' }
        ]} as SelectField,
        { name: 'loan_start_date', label: 'Loan Start Date', type: 'date' } as DateField
      ]
    },
    {
      label: 'Education',
      fields: [
        { name: 'monthly_expenses_child1', label: 'Monthly Expenses - 1st Child', type: 'number' } as NumberField,
        { name: 'monthly_expenses_child2', label: 'Monthly Expenses - 2nd Child', type: 'number' } as NumberField,
        { name: 'months_child1', label: 'Months - 1st Child', type: 'number' } as NumberField,
        { name: 'months_child2', label: 'Months - 2nd Child', type: 'number' } as NumberField,
        { name: 'employer_maintained_1st_child', label: 'Institution Maintained by Employer', type: 'checkbox' } as CheckboxField,
        { name: 'employer_maintained_2nd_child', label: 'Institution Maintained by Employer', type: 'checkbox' } as CheckboxField
      ]
    },
    {
      label: 'Utilities',
      fields: [
        { name: 'gas_paid_by_employer', label: 'Gas Incurred by Employer', type: 'number' } as NumberField,
        { name: 'electricity_paid_by_employer', label: 'Electricity Incurred by Employer', type: 'number' } as NumberField,
        { name: 'water_paid_by_employer', label: 'Water Incurred by Employer', type: 'number' } as NumberField,
        { name: 'gas_paid_by_employee', label: 'Gas Paid by Employee', type: 'number' } as NumberField,
        { name: 'electricity_paid_by_employee', label: 'Electricity Paid by Employee', type: 'number' } as NumberField,
        { name: 'water_paid_by_employee', label: 'Water Paid by Employee', type: 'number' } as NumberField,
        { name: 'is_gas_manufactured_by_employer', label: 'Gas Manufactured by Employer', type: 'checkbox' } as CheckboxField,
        { name: 'is_electricity_manufactured_by_employer', label: 'Electricity Manufactured by Employer', type: 'checkbox' } as CheckboxField,
        { name: 'is_water_manufactured_by_employer', label: 'Water Manufactured by Employer', type: 'checkbox' } as CheckboxField
      ]
    },
    {
      label: 'ESOP',
      fields: [
        { name: 'esop_exercise_value', label: 'ESOP Exercise Value', type: 'number' } as NumberField,
        { name: 'esop_fair_market_value', label: 'ESOP Fair Market Value', type: 'number' } as NumberField,
        { name: 'esop_shares_exercised', label: 'ESOP Shares Exercised', type: 'number' } as NumberField
      ]
    },
    {
      label: 'Meals Provided',
      fields: [
        { name: 'lunch_employer_cost', label: 'Cost Paid by Employer', type: 'number' } as NumberField,
        { name: 'lunch_employee_payment', label: 'Payment by Employee', type: 'number' } as NumberField,
        { name: 'lunch_meal_days_per_year', label: 'Meal Days per Year', type: 'number' } as NumberField
      ]
    },
    {
      label: 'Domestic Help',
      fields: [
        { name: 'domestic_help_paid_by_employer', label: 'Cost Paid by Employer', type: 'number' } as NumberField,
        { name: 'domestic_help_paid_by_employee', label: 'Payment by Employee', type: 'number' } as NumberField
      ]
    },
    {
      label: 'Movable Asset Usage',
      fields: [
        { name: 'movable_asset_type', label: 'Asset Type', type: 'select', options: [
          { value: 'Electronics', label: 'Electronics' },
          { value: 'Motor Vehicle', label: 'Motor Vehicle' },
          { value: 'Others', label: 'Others' }
        ]} as SelectField,
        { name: 'movable_asset_usage_value', label: 'Asset Value', type: 'number' } as NumberField,
        { name: 'movable_asset_hire_cost', label: 'Hire Cost', type: 'number' } as NumberField,
        { name: 'movable_asset_employee_payment', label: 'Payment by Employee', type: 'number' } as NumberField,
        { name: 'movable_asset_is_employer_owned', label: 'Asset Owned by Employer', type: 'checkbox' } as CheckboxField
      ]
    },
    {
      label: 'Movable Asset Transfer',
      fields: [
        { name: 'movable_asset_transfer_type', label: 'Asset Type', type: 'select', options: [
          { value: 'Electronics', label: 'Electronics' },
          { value: 'Motor Vehicle', label: 'Motor Vehicle' },
          { value: 'Others', label: 'Others' }
        ]} as SelectField,
        { name: 'movable_asset_transfer_cost', label: 'Original Asset Cost', type: 'number' } as NumberField,
        { name: 'movable_asset_years_of_use', label: 'Years of Use', type: 'number' } as NumberField,
        { name: 'movable_asset_transfer_employee_payment', label: 'Payment by Employee', type: 'number' } as NumberField
      ]
    },
    {
      label: 'Monetary Benefits',
      fields: [
        { name: 'monetary_amount_paid_by_employer', label: 'Amount Paid by Employer', type: 'number' } as NumberField,
        { name: 'expenditure_for_official_purpose', label: 'Expenditure for Official Purpose', type: 'number' } as NumberField,
        { name: 'amount_paid_by_employee', label: 'Amount Paid by Employee', type: 'number' } as NumberField
      ]
    },
    {
      label: 'Club Expenses',
      fields: [
        { name: 'club_expenses_paid_by_employer', label: 'Club Expenses Paid by Employer', type: 'number' } as NumberField,
        { name: 'club_expenses_paid_by_employee', label: 'Club Expenses Paid by Employee', type: 'number' } as NumberField,
        { name: 'club_expenses_for_official_purpose', label: 'Club Expenses for Official Purpose', type: 'number' } as NumberField
      ]
    },
    {
      label: 'Other Benefits',
      fields: [
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
              <Typography variant="body2" color="text.secondary">LTA Claimed</Typography>
              <Typography variant="h6">₹{perquisitesData.lta_amount_claimed.toLocaleString('en-IN')}</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">ESOP Value</Typography>
              <Typography variant="h6">₹{perquisitesData.esop_exercise_value.toLocaleString('en-IN')}</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">Free Education Total</Typography>
              <Typography variant="h6">₹{((perquisitesData.monthly_expenses_child1 * perquisitesData.months_child1 * (perquisitesData.employer_maintained_1st_child ? 1 : 0)) +
                                 (perquisitesData.monthly_expenses_child2 * perquisitesData.months_child2 * (perquisitesData.employer_maintained_2nd_child ? 1 : 0))).toLocaleString('en-IN')}</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">Utilities Total</Typography>
              <Typography variant="h6">₹{((perquisitesData.gas_paid_by_employer + 
                                 perquisitesData.electricity_paid_by_employer + 
                                 perquisitesData.water_paid_by_employer) -
                                (perquisitesData.gas_paid_by_employee + 
                                 perquisitesData.electricity_paid_by_employee + 
                                 perquisitesData.water_paid_by_employee)).toLocaleString('en-IN')}</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">Meals Total</Typography>
              <Typography variant="h6">₹{Math.max(0, perquisitesData.lunch_employer_cost - perquisitesData.lunch_employee_payment).toLocaleString('en-IN')}</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">Domestic Help Total</Typography>
              <Typography variant="h6">₹{Math.max(0, perquisitesData.domestic_help_paid_by_employer - perquisitesData.domestic_help_paid_by_employee).toLocaleString('en-IN')}</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">Monetary Benefits Total</Typography>
              <Typography variant="h6">₹{Math.max(0, perquisitesData.monetary_amount_paid_by_employer - perquisitesData.expenditure_for_official_purpose - perquisitesData.amount_paid_by_employee).toLocaleString('en-IN')}</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">Club Expenses Total</Typography>
              <Typography variant="h6">₹{Math.max(0, perquisitesData.club_expenses_paid_by_employer - perquisitesData.club_expenses_paid_by_employee - perquisitesData.club_expenses_for_official_purpose).toLocaleString('en-IN')}</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">Movable Asset Usage</Typography>
              <Typography variant="h6">₹{(perquisitesData.movable_asset_is_employer_owned 
                ? Math.max(0, (perquisitesData.movable_asset_usage_value * 0.1) - perquisitesData.movable_asset_employee_payment)
                : Math.max(0, perquisitesData.movable_asset_hire_cost - perquisitesData.movable_asset_employee_payment)).toLocaleString('en-IN')}</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">Movable Asset Transfer</Typography>
              <Typography variant="h6">₹{(() => {
                const depreciationRate = perquisitesData.movable_asset_transfer_type === 'Electronics' ? 0.5 
                  : perquisitesData.movable_asset_transfer_type === 'Motor Vehicle' ? 0.2 : 0.1;
                const annualDepreciation = perquisitesData.movable_asset_transfer_cost * depreciationRate;
                const totalDepreciation = annualDepreciation * perquisitesData.movable_asset_years_of_use;
                const depreciatedValue = Math.max(0, perquisitesData.movable_asset_transfer_cost - totalDepreciation);
                return Math.max(0, depreciatedValue - perquisitesData.movable_asset_transfer_employee_payment);
              })().toLocaleString('en-IN')}</Typography>
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
                        ) : isDateField(field) ? (
                          <TextField
                            fullWidth
                            label={field.label}
                            type="date"
                            value={perquisitesData[field.name as keyof PerquisitesComponentData] as string}
                            onChange={(e) => {
                              handleInputChange(field.name as keyof PerquisitesComponentData, e.target.value);
                            }}
                            InputLabelProps={{ shrink: true }}
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