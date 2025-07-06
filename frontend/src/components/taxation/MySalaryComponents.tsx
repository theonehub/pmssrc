import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Paper,
  Card,
  CardContent,
  Grid,
  CircularProgress,
  Alert,
  Button,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Tooltip,
  Snackbar,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  FormControlLabel,
  Checkbox
} from '@mui/material';
import {
  AccountBalance as AccountBalanceIcon,
  Receipt as ReceiptIcon,
  Home as HomeIcon,
  TrendingUp as TrendingUpIcon,
  Business as BusinessIcon,
  CardGiftcard as CardGiftcardIcon,
  ExpandMore as ExpandMoreIcon,
  FileDownload as FileDownloadIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
  Info as InfoIcon,
  Edit as EditIcon,
  Save as SaveIcon
} from '@mui/icons-material';
import { useAuth } from '../../shared/hooks/useAuth';
import taxationApi from '../../shared/api/taxationApi';

interface ComponentSummary {
  id: string;
  name: string;
  icon: React.ReactElement;
  color: string;
  hasData: boolean;
  totalValue: number;
  details: Record<string, any>;
  description: string;
}

interface ToastState {
  show: boolean;
  message: string;
  severity: 'success' | 'error' | 'warning' | 'info';
}

interface DeductionsData {
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

  // Section 80D
  self_family_premium: number;
  parent_premium: number;
  preventive_health_checkup: number;

  // Section 80E
  education_loan_interest: number;

  // Section 80TTA
  savings_account_interest: number;
}

interface HousePropertyData {
  property_type: string;
  address: string;
  annual_rent_received: number;
  municipal_taxes_paid: number;
  home_loan_interest: number;
  pre_construction_interest: number;
}

interface CapitalGainsData {
  stcg_111a_equity_stt: number;
  stcg_other_assets: number;
  stcg_debt_mf: number;
  ltcg_112a_equity_stt: number;
  ltcg_other_assets: number;
  ltcg_debt_mf: number;
}

interface InterestIncomeData {
  savings_interest: number;
  fd_interest: number;
  rd_interest: number;
  post_office_interest: number;
}

interface OtherIncomeData {
  interest_income: InterestIncomeData;
  dividend_income: number;
  gifts_received: number;
  business_professional_income: number;
  other_miscellaneous_income: number;
}

interface DeductionsDialogProps {
  open: boolean;
  onClose: () => void;
  onSave: (data: DeductionsData) => Promise<void>;
  initialData: DeductionsData;
  loading: boolean;
}

interface HousePropertyDialogProps {
  open: boolean;
  onClose: () => void;
  onSave: (data: HousePropertyData) => Promise<void>;
  initialData: HousePropertyData;
  loading: boolean;
}

interface CapitalGainsDialogProps {
  open: boolean;
  onClose: () => void;
  onSave: (data: CapitalGainsData) => Promise<void>;
  initialData: CapitalGainsData;
  loading: boolean;
}

interface OtherIncomeDialogProps {
  open: boolean;
  onClose: () => void;
  onSave: (data: OtherIncomeData) => Promise<void>;
  initialData: OtherIncomeData;
  loading: boolean;
}

interface PerquisitesData {
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
  driver_cost: number;
  has_expense_reimbursement: boolean;
  driver_provided: boolean;

  // LTA
  lta_allocated_yearly: number;
  lta_amount_claimed: number;
  lta_claimed_count: number;
  public_transport_cost: number;
  travel_mode: string;
  is_monthly_paid: boolean;

  // ESOP
  esop_exercise_value: number;
  esop_fair_market_value: number;
  esop_shares_exercised: number;

  // Free Education
  monthly_expenses_child1: number;
  monthly_expenses_child2: number;
  months_child1: number;
  months_child2: number;
  employer_maintained_1st_child: boolean;
  employer_maintained_2nd_child: boolean;

  // Utilities
  gas_paid_by_employer: number;
  electricity_paid_by_employer: number;
  water_paid_by_employer: number;
  gas_paid_by_employee: number;
  electricity_paid_by_employee: number;
  water_paid_by_employee: number;
  is_gas_manufactured_by_employer: boolean;
  is_electricity_manufactured_by_employer: boolean;
  is_water_manufactured_by_employer: boolean;

  // Interest Free Loan
  loan_amount: number;
  emi_amount: number;
  company_interest_rate: number;
  sbi_interest_rate: number;
  loan_type: string;
  loan_start_date: string;

  // Movable Asset Usage
  movable_asset_type: string;
  movable_asset_usage_value: number;
  movable_asset_hire_cost: number;
  movable_asset_employee_payment: number;
  movable_asset_is_employer_owned: boolean;
  
  // Movable Asset Transfer
  movable_asset_transfer_type: string;
  movable_asset_transfer_cost: number;
  movable_asset_years_of_use: number;
  movable_asset_transfer_employee_payment: number;

  // Lunch Refreshment
  lunch_employer_cost: number;
  lunch_employee_payment: number;
  lunch_meal_days_per_year: number;
  
  // Domestic Help
  domestic_help_paid_by_employer: number;
  domestic_help_paid_by_employee: number;
  
  // Other Perquisites
  other_perquisites_amount: number;
  
  // Monetary Benefits
  monetary_benefit_type: string;
  monetary_benefit_amount: number;
  monetary_benefit_employee_payment: number;
  
  // Club Expenses
  club_expense_type: string;
  club_expense_amount: number;
  club_expense_employee_payment: number;
  
  // Other Benefits
  other_benefit_type: string;
  other_benefit_amount: number;
  other_benefit_employee_payment: number;
}

interface PerquisitesDialogProps {
  open: boolean;
  onClose: () => void;
  onSave: (data: PerquisitesData) => Promise<void>;
  initialData: PerquisitesData;
  loading: boolean;
}

// Helper function to get current tax year
const getCurrentTaxYear = (): string => {
  const currentDate = new Date();
  const currentYear = currentDate.getFullYear();
  const currentMonth = currentDate.getMonth() + 1;
  
  // Tax year starts from April 1st
  if (currentMonth >= 4) {
    return `${currentYear}-${(currentYear + 1).toString().slice(-2)}`;
  } else {
    return `${currentYear - 1}-${currentYear.toString().slice(-2)}`;
  }
};

// Helper function to generate available tax years (current + last 3 years)
const getAvailableTaxYears = (): string[] => {
  const currentTaxYear = getCurrentTaxYear();
  const yearParts = currentTaxYear.split('-');
  const currentStartYear = parseInt(yearParts[0] || '2024');
  const years: string[] = [];
  
  for (let i = 0; i <= 3; i++) {
    const startYear = currentStartYear - i;
    const endYear = startYear + 1;
    years.push(`${startYear}-${endYear.toString().slice(-2)}`);
  }
  
  return years;
};

// Initial deductions data
const initialDeductionsData: DeductionsData = {
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
  self_family_premium: 0,
  parent_premium: 0,
  preventive_health_checkup: 0,
  education_loan_interest: 0,
  savings_account_interest: 0
};

// Initial house property data
const initialHousePropertyData: HousePropertyData = {
  property_type: 'Self-Occupied',
  address: '',
  annual_rent_received: 0,
  municipal_taxes_paid: 0,
  home_loan_interest: 0,
  pre_construction_interest: 0
};

// Initial capital gains data
const initialCapitalGainsData: CapitalGainsData = {
  stcg_111a_equity_stt: 0,
  stcg_other_assets: 0,
  stcg_debt_mf: 0,
  ltcg_112a_equity_stt: 0,
  ltcg_other_assets: 0,
  ltcg_debt_mf: 0
};

// Initial other income data
const initialOtherIncomeData: OtherIncomeData = {
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

// Initial perquisites data
const initialPerquisitesData: PerquisitesData = {
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
  driver_cost: 0,
  has_expense_reimbursement: false,
  driver_provided: false,

  // LTA
  lta_allocated_yearly: 0,
  lta_amount_claimed: 0,
  lta_claimed_count: 0,
  public_transport_cost: 0,
  travel_mode: 'Air',
  is_monthly_paid: false,

  // ESOP
  esop_exercise_value: 0,
  esop_fair_market_value: 0,
  esop_shares_exercised: 0,

  // Free Education
  monthly_expenses_child1: 0,
  monthly_expenses_child2: 0,
  months_child1: 12,
  months_child2: 12,
  employer_maintained_1st_child: false,
  employer_maintained_2nd_child: false,

  // Utilities
  gas_paid_by_employer: 0,
  electricity_paid_by_employer: 0,
  water_paid_by_employer: 0,
  gas_paid_by_employee: 0,
  electricity_paid_by_employee: 0,
  water_paid_by_employee: 0,
  is_gas_manufactured_by_employer: false,
  is_electricity_manufactured_by_employer: false,
  is_water_manufactured_by_employer: false,

  // Interest Free Loan
  loan_amount: 0,
  emi_amount: 0,
  company_interest_rate: 0,
  sbi_interest_rate: 6.5,
  loan_type: 'Personal',
  loan_start_date: '',

  // Movable Asset Usage
  movable_asset_type: '',
  movable_asset_usage_value: 0,
  movable_asset_hire_cost: 0,
  movable_asset_employee_payment: 0,
  movable_asset_is_employer_owned: false,
  
  // Movable Asset Transfer
  movable_asset_transfer_type: '',
  movable_asset_transfer_cost: 0,
  movable_asset_years_of_use: 0,
  movable_asset_transfer_employee_payment: 0,

  // Lunch Refreshment
  lunch_employer_cost: 0,
  lunch_employee_payment: 0,
  lunch_meal_days_per_year: 250,
  
  // Domestic Help
  domestic_help_paid_by_employer: 0,
  domestic_help_paid_by_employee: 0,
  
  // Other Perquisites
  other_perquisites_amount: 0,
  
  // Monetary Benefits
  monetary_benefit_type: '',
  monetary_benefit_amount: 0,
  monetary_benefit_employee_payment: 0,
  
  // Club Expenses
  club_expense_type: '',
  club_expense_amount: 0,
  club_expense_employee_payment: 0,
  
  // Other Benefits
  other_benefit_type: '',
  other_benefit_amount: 0,
  other_benefit_employee_payment: 0
};

// Deductions Update Dialog Component
const DeductionsDialog: React.FC<DeductionsDialogProps> = ({
  open,
  onClose,
  onSave,
  initialData,
  loading
}) => {
  const [deductionsData, setDeductionsData] = useState<DeductionsData>(initialData);
  const [activeStep, setActiveStep] = useState<number>(0);

  // Reset form when dialog opens/closes
  useEffect(() => {
    if (open) {
      setDeductionsData(initialData);
      setActiveStep(0);
    }
  }, [open, initialData]);

  const handleInputChange = (field: keyof DeductionsData, value: number): void => {
    setDeductionsData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = async (): Promise<void> => {
    await onSave(deductionsData);
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

  const steps = [
    {
      label: 'Section 80C Investments',
      description: 'Tax-saving investments under Section 80C (Max: ₹1,50,000)',
      fields: [
        { name: 'life_insurance_premium', label: 'Life Insurance Premium' },
        { name: 'epf_contribution', label: 'EPF Contribution' },
        { name: 'ppf_contribution', label: 'PPF Contribution' },
        { name: 'nsc_investment', label: 'NSC Investment' },
        { name: 'tax_saving_fd', label: 'Tax Saving FD' },
        { name: 'elss_investment', label: 'ELSS Investment' },
        { name: 'home_loan_principal', label: 'Home Loan Principal' },
        { name: 'tuition_fees', label: 'Tuition Fees' },
        { name: 'ulip_premium', label: 'ULIP Premium' },
        { name: 'sukanya_samriddhi', label: 'Sukanya Samriddhi' },
        { name: 'stamp_duty_property', label: 'Stamp Duty on Property' },
        { name: 'senior_citizen_savings', label: 'Senior Citizen Savings' },
        { name: 'other_80c_investments', label: 'Other 80C Investments' }
      ]
    },
    {
      label: 'Section 80D Health Insurance',
      description: 'Health insurance premiums and medical expenses (Max: ₹75,000)',
      fields: [
        { name: 'self_family_premium', label: 'Self & Family Health Insurance' },
        { name: 'parent_premium', label: 'Parents Health Insurance' },
        { name: 'preventive_health_checkup', label: 'Preventive Health Checkup' }
      ]
    },
    {
      label: 'Other Deductions',
      description: 'Education loan interest and other deductions',
      fields: [
        { name: 'education_loan_interest', label: 'Education Loan Interest (80E)' },
        { name: 'savings_account_interest', label: 'Savings Account Interest (80TTA)' }
      ]
    }
  ];

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <ReceiptIcon color="primary" />
          <Typography variant="h6">
            Update Deductions
          </Typography>
        </Box>
      </DialogTitle>
      <DialogContent>
        {/* Summary Card */}
        <Card variant="outlined" sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Deductions Summary
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={4}>
                <Typography variant="body2" color="text.secondary">Section 80C Total</Typography>
                <Typography variant="h6">₹{calculate80CTotal().toLocaleString('en-IN')}</Typography>
                <Typography variant="caption" color={calculate80CTotal() > 150000 ? 'error' : 'textSecondary'}>
                  Limit: ₹1,50,000
                </Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="body2" color="text.secondary">Section 80D Total</Typography>
                <Typography variant="h6">₹{calculate80DTotal().toLocaleString('en-IN')}</Typography>
                <Typography variant="caption" color={calculate80DTotal() > 75000 ? 'error' : 'textSecondary'}>
                  Limit: ₹75,000
                </Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="body2" color="text.secondary">Education Loan Interest</Typography>
                <Typography variant="h6">₹{deductionsData.education_loan_interest.toLocaleString('en-IN')}</Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Stepper Form */}
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
                <Grid container spacing={2} sx={{ mt: 1 }}>
                  {step.fields.map((field) => (
                    <Grid item xs={12} sm={6} key={field.name}>
                      <TextField
                        fullWidth
                        label={field.label}
                        type="number"
                        value={deductionsData[field.name as keyof DeductionsData]}
                        onChange={(e) => handleInputChange(
                          field.name as keyof DeductionsData, 
                          parseFloat(e.target.value) || 0
                        )}
                        InputProps={{
                          startAdornment: <Typography variant="caption" sx={{ mr: 1 }}>₹</Typography>,
                        }}
                        size="small"
                      />
                    </Grid>
                  ))}
                </Grid>
                <Box sx={{ mt: 2 }}>
                  <Button
                    variant="contained"
                    onClick={handleNext}
                    disabled={index === steps.length - 1}
                  >
                    {index === steps.length - 1 ? 'Finish' : 'Continue'}
                  </Button>
                  <Button
                    disabled={index === 0}
                    onClick={handleBack}
                    sx={{ ml: 1 }}
                  >
                    Back
                  </Button>
                </Box>
              </StepContent>
            </Step>
          ))}
        </Stepper>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button 
          onClick={handleSave} 
          variant="contained" 
          disabled={loading}
          startIcon={loading ? <CircularProgress size={16} /> : <SaveIcon />}
        >
          {loading ? 'Saving...' : 'Save Deductions'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

// House Property Update Dialog Component
const HousePropertyDialog: React.FC<HousePropertyDialogProps> = ({
  open,
  onClose,
  onSave,
  initialData,
  loading
}) => {
  const [housePropertyData, setHousePropertyData] = useState<HousePropertyData>(initialData);
  const [activeStep, setActiveStep] = useState<number>(0);

  // Reset form when dialog opens/closes
  useEffect(() => {
    if (open) {
      setHousePropertyData(initialData);
      setActiveStep(0);
    }
  }, [open, initialData]);

  const handleInputChange = (field: keyof HousePropertyData, value: number | string): void => {
    setHousePropertyData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = async (): Promise<void> => {
    await onSave(housePropertyData);
  };

  const handleNext = (): void => {
    setActiveStep(prev => prev + 1);
  };

  const handleBack = (): void => {
    setActiveStep(prev => prev - 1);
  };

  const calculateNetIncome = (): number => {
    const annualRent = housePropertyData.annual_rent_received || 0;
    const municipalTaxes = housePropertyData.municipal_taxes_paid || 0;
    const homeLoanInterest = housePropertyData.home_loan_interest || 0;
    const preConstructionInterest = housePropertyData.pre_construction_interest || 0;
    
    if (housePropertyData.property_type === 'Self-Occupied') {
      return -(homeLoanInterest + preConstructionInterest);
    } else {
      const netAnnualValue = annualRent - municipalTaxes;
      const standardDeduction = netAnnualValue * 0.3; // 30% standard deduction
      const totalDeductions = standardDeduction + homeLoanInterest + preConstructionInterest;
      return netAnnualValue - totalDeductions;
    }
  };

  const calculateTotalDeductions = (): number => {
    const municipalTaxes = housePropertyData.municipal_taxes_paid || 0;
    const homeLoanInterest = housePropertyData.home_loan_interest || 0;
    const preConstructionInterest = housePropertyData.pre_construction_interest || 0;
    
    if (housePropertyData.property_type === 'Let-Out') {
      const annualRent = housePropertyData.annual_rent_received || 0;
      const netAnnualValue = annualRent - municipalTaxes;
      const standardDeduction = netAnnualValue * 0.3; // 30% standard deduction
      return standardDeduction + homeLoanInterest + preConstructionInterest;
    } else {
      return homeLoanInterest + preConstructionInterest;
    }
  };

  const steps = [
    {
      label: 'Property Details',
      description: 'Basic property information and type',
      fields: [
        { name: 'property_type', label: 'Property Type', type: 'select', options: [
          { value: 'Self-Occupied', label: 'Self-Occupied' },
          { value: 'Let-Out', label: 'Let-Out' }
        ]} as any,
        { name: 'address', label: 'Property Address', type: 'text' } as any
      ]
    },
    {
      label: 'Income & Expenses',
      description: 'Rental income and property expenses',
      fields: [
        { name: 'annual_rent_received', label: 'Annual Rent Received', type: 'number' } as any,
        { name: 'municipal_taxes_paid', label: 'Municipal Taxes Paid', type: 'number' } as any
      ]
    },
    {
      label: 'Loan Interest',
      description: 'Home loan interest deductions',
      fields: [
        { name: 'home_loan_interest', label: 'Home Loan Interest', type: 'number' } as any,
        { name: 'pre_construction_interest', label: 'Pre-construction Interest', type: 'number' } as any
      ]
    }
  ];

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <HomeIcon color="primary" />
          <Typography variant="h6">
            Update House Property
          </Typography>
        </Box>
      </DialogTitle>
      <DialogContent>
        {/* Summary Card */}
        <Card variant="outlined" sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              House Property Summary
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Property Type</Typography>
                <Typography variant="h6">{housePropertyData.property_type}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Annual Rent</Typography>
                <Typography variant="h6">₹{housePropertyData.annual_rent_received.toLocaleString('en-IN')}</Typography>
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
                <Grid container spacing={2} sx={{ mt: 1 }}>
                  {step.fields.map((field) => (
                    <Grid item xs={12} sm={6} key={field.name}>
                      {field.type === 'select' ? (
                        <FormControl fullWidth size="small">
                          <InputLabel>{field.label}</InputLabel>
                          <Select
                            value={housePropertyData[field.name as keyof HousePropertyData] as string}
                            label={field.label}
                            onChange={(e: SelectChangeEvent) => 
                              handleInputChange(field.name as keyof HousePropertyData, e.target.value)
                            }
                          >
                            {field.options?.map((option: { value: string; label: string }) => (
                              <MenuItem key={option.value} value={option.value}>
                                {option.label}
                              </MenuItem>
                            ))}
                          </Select>
                        </FormControl>
                      ) : field.type === 'text' ? (
                        <TextField
                          fullWidth
                          label={field.label}
                          type="text"
                          value={housePropertyData[field.name as keyof HousePropertyData]}
                          onChange={(e) => {
                            handleInputChange(field.name as keyof HousePropertyData, e.target.value);
                          }}
                          multiline={field.name === 'address'}
                          rows={field.name === 'address' ? 3 : 1}
                          size="small"
                        />
                      ) : (
                        <TextField
                          fullWidth
                          label={field.label}
                          type="number"
                          value={housePropertyData[field.name as keyof HousePropertyData]}
                          onChange={(e) => {
                            const value = parseFloat(e.target.value) || 0;
                            handleInputChange(field.name as keyof HousePropertyData, value);
                          }}
                          InputProps={{
                            startAdornment: <Typography variant="caption" sx={{ mr: 1 }}>₹</Typography>,
                          }}
                          size="small"
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
                  >
                    {index === steps.length - 1 ? 'Finish' : 'Continue'}
                  </Button>
                  <Button
                    disabled={index === 0}
                    onClick={handleBack}
                    sx={{ ml: 1 }}
                  >
                    Back
                  </Button>
                </Box>
              </StepContent>
            </Step>
          ))}
        </Stepper>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button 
          onClick={handleSave} 
          variant="contained" 
          disabled={loading}
          startIcon={loading ? <CircularProgress size={16} /> : <SaveIcon />}
        >
          {loading ? 'Saving...' : 'Save House Property'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

// Capital Gains Update Dialog Component
const CapitalGainsDialog: React.FC<CapitalGainsDialogProps> = ({
  open,
  onClose,
  onSave,
  initialData,
  loading
}) => {
  const [capitalGainsData, setCapitalGainsData] = useState<CapitalGainsData>(initialData);
  const [activeStep, setActiveStep] = useState<number>(0);

  // Reset form when dialog opens/closes
  useEffect(() => {
    if (open) {
      setCapitalGainsData(initialData);
      setActiveStep(0);
    }
  }, [open, initialData]);

  const handleInputChange = (field: keyof CapitalGainsData, value: number): void => {
    setCapitalGainsData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = async (): Promise<void> => {
    await onSave(capitalGainsData);
  };

  const handleNext = (): void => {
    setActiveStep(prev => prev + 1);
  };

  const handleBack = (): void => {
    setActiveStep(prev => prev - 1);
  };

  const calculateTotalSTCG = (): number => {
    return capitalGainsData.stcg_111a_equity_stt + 
           capitalGainsData.stcg_other_assets + 
           capitalGainsData.stcg_debt_mf;
  };

  const calculateTotalLTCG = (): number => {
    return capitalGainsData.ltcg_112a_equity_stt + 
           capitalGainsData.ltcg_other_assets + 
           capitalGainsData.ltcg_debt_mf;
  };

  const calculateTotalCapitalGains = (): number => {
    return calculateTotalSTCG() + calculateTotalLTCG();
  };

  const steps = [
    {
      label: 'Short Term Capital Gains',
      description: 'Gains from assets held for less than 12 months',
      fields: [
        { name: 'stcg_111a_equity_stt', label: 'STCG 111A (Equity with STT)', helperText: 'Taxed at 15%' },
        { name: 'stcg_other_assets', label: 'STCG Other Assets', helperText: 'Taxed at slab rates' },
        { name: 'stcg_debt_mf', label: 'STCG Debt Mutual Funds', helperText: 'Taxed at slab rates' }
      ]
    },
    {
      label: 'Long Term Capital Gains',
      description: 'Gains from assets held for more than 12 months',
      fields: [
        { name: 'ltcg_112a_equity_stt', label: 'LTCG 112A (Equity with STT)', helperText: '10% tax with ₹1.25L exemption' },
        { name: 'ltcg_other_assets', label: 'LTCG Other Assets', helperText: 'Taxed at 20% with indexation' },
        { name: 'ltcg_debt_mf', label: 'LTCG Debt Mutual Funds', helperText: 'Taxed at 20% with indexation' }
      ]
    }
  ];

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <TrendingUpIcon color="primary" />
          <Typography variant="h6">
            Update Capital Gains
          </Typography>
        </Box>
      </DialogTitle>
      <DialogContent>
        {/* Summary Card */}
        <Card variant="outlined" sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Capital Gains Summary
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={4}>
                <Typography variant="body2" color="text.secondary">Short Term Capital Gains</Typography>
                <Typography variant="h6">₹{calculateTotalSTCG().toLocaleString('en-IN')}</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="body2" color="text.secondary">Long Term Capital Gains</Typography>
                <Typography variant="h6">₹{calculateTotalLTCG().toLocaleString('en-IN')}</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="body2" color="text.secondary">Total Capital Gains</Typography>
                <Typography variant="h6" color="primary">₹{calculateTotalCapitalGains().toLocaleString('en-IN')}</Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Stepper Form */}
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
                <Grid container spacing={2} sx={{ mt: 1 }}>
                  {step.fields.map((field) => (
                    <Grid item xs={12} sm={6} key={field.name}>
                      <TextField
                        fullWidth
                        label={field.label}
                        type="number"
                        value={capitalGainsData[field.name as keyof CapitalGainsData]}
                        onChange={(e) => {
                          const value = parseFloat(e.target.value) || 0;
                          handleInputChange(field.name as keyof CapitalGainsData, value);
                        }}
                        InputProps={{
                          startAdornment: <Typography variant="caption" sx={{ mr: 1 }}>₹</Typography>,
                        }}
                        size="small"
                        helperText={field.helperText}
                      />
                    </Grid>
                  ))}
                </Grid>
                <Box sx={{ mt: 2 }}>
                  <Button
                    variant="contained"
                    onClick={handleNext}
                    disabled={index === steps.length - 1}
                  >
                    {index === steps.length - 1 ? 'Finish' : 'Continue'}
                  </Button>
                  <Button
                    disabled={index === 0}
                    onClick={handleBack}
                    sx={{ ml: 1 }}
                  >
                    Back
                  </Button>
                </Box>
              </StepContent>
            </Step>
          ))}
        </Stepper>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button 
          onClick={handleSave} 
          variant="contained" 
          disabled={loading}
          startIcon={loading ? <CircularProgress size={16} /> : <SaveIcon />}
        >
          {loading ? 'Saving...' : 'Save Capital Gains'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

// Other Income Update Dialog Component
const OtherIncomeDialog: React.FC<OtherIncomeDialogProps> = ({
  open,
  onClose,
  onSave,
  initialData,
  loading
}) => {
  const [otherIncomeData, setOtherIncomeData] = useState<OtherIncomeData>(initialData);
  const [activeStep, setActiveStep] = useState<number>(0);

  // Reset form when dialog opens/closes
  useEffect(() => {
    if (open) {
      setOtherIncomeData(initialData);
      setActiveStep(0);
    }
  }, [open, initialData]);

  const handleInputChange = (field: keyof OtherIncomeData, value: number, subfield?: keyof InterestIncomeData): void => {
    setOtherIncomeData(prev => {
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
    await onSave(otherIncomeData);
  };

  const handleNext = (): void => {
    setActiveStep(prev => prev + 1);
  };

  const handleBack = (): void => {
    setActiveStep(prev => prev - 1);
  };

  const calculateTotalInterestIncome = (): number => {
    return otherIncomeData.interest_income.savings_interest +
           otherIncomeData.interest_income.fd_interest +
           otherIncomeData.interest_income.rd_interest +
           otherIncomeData.interest_income.post_office_interest;
  };

  const calculateTotalOtherIncome = (): number => {
    return calculateTotalInterestIncome() +
           otherIncomeData.dividend_income +
           otherIncomeData.gifts_received +
           otherIncomeData.business_professional_income +
           otherIncomeData.other_miscellaneous_income;
  };

  const steps = [
    {
      label: 'Interest Income',
      description: 'Income from savings accounts, FDs, and other deposits',
      fields: [
        { name: 'savings_interest', label: 'Savings Account Interest' },
        { name: 'fd_interest', label: 'Fixed Deposit Interest' },
        { name: 'rd_interest', label: 'Recurring Deposit Interest' },
        { name: 'post_office_interest', label: 'Post Office Interest' }
      ]
    },
    {
      label: 'Dividend & Gifts',
      description: 'Dividend income and gifts received',
      fields: [
        { name: 'dividend_income', label: 'Dividend Income' },
        { name: 'gifts_received', label: 'Gifts Received' }
      ]
    },
    {
      label: 'Business & Other Income',
      description: 'Business/professional income and miscellaneous income',
      fields: [
        { name: 'business_professional_income', label: 'Business/Professional Income' },
        { name: 'other_miscellaneous_income', label: 'Other Miscellaneous Income' }
      ]
    }
  ];

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <BusinessIcon color="primary" />
          <Typography variant="h6">
            Update Other Income
          </Typography>
        </Box>
      </DialogTitle>
      <DialogContent>
        {/* Summary Card */}
        <Card variant="outlined" sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Other Income Summary
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={4}>
                <Typography variant="body2" color="text.secondary">Interest Income</Typography>
                <Typography variant="h6">₹{calculateTotalInterestIncome().toLocaleString('en-IN')}</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="body2" color="text.secondary">Dividend Income</Typography>
                <Typography variant="h6">₹{otherIncomeData.dividend_income.toLocaleString('en-IN')}</Typography>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Typography variant="body2" color="text.secondary">Total Other Income</Typography>
                <Typography variant="h6" color="primary">₹{calculateTotalOtherIncome().toLocaleString('en-IN')}</Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Stepper Form */}
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
                <Grid container spacing={2} sx={{ mt: 1 }}>
                  {step.fields.map((field) => (
                    <Grid item xs={12} sm={6} key={field.name}>
                      <TextField
                        fullWidth
                        label={field.label}
                        type="number"
                        value={
                          step.label === 'Interest Income' 
                            ? otherIncomeData.interest_income[field.name as keyof InterestIncomeData]
                            : otherIncomeData[field.name as keyof OtherIncomeData]
                        }
                        onChange={(e) => {
                          const value = parseFloat(e.target.value) || 0;
                          if (step.label === 'Interest Income') {
                            handleInputChange('interest_income', value, field.name as keyof InterestIncomeData);
                          } else {
                            handleInputChange(field.name as keyof OtherIncomeData, value);
                          }
                        }}
                        InputProps={{
                          startAdornment: <Typography variant="caption" sx={{ mr: 1 }}>₹</Typography>,
                        }}
                        size="small"
                      />
                    </Grid>
                  ))}
                </Grid>
                <Box sx={{ mt: 2 }}>
                  <Button
                    variant="contained"
                    onClick={handleNext}
                    disabled={index === steps.length - 1}
                  >
                    {index === steps.length - 1 ? 'Finish' : 'Continue'}
                  </Button>
                  <Button
                    disabled={index === 0}
                    onClick={handleBack}
                    sx={{ ml: 1 }}
                  >
                    Back
                  </Button>
                </Box>
              </StepContent>
            </Step>
          ))}
        </Stepper>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button 
          onClick={handleSave} 
          variant="contained" 
          disabled={loading}
          startIcon={loading ? <CircularProgress size={16} /> : <SaveIcon />}
        >
          {loading ? 'Saving...' : 'Save Other Income'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

// Helper functions for field type checking
const isSelectField = (field: any): field is { type: 'select'; options: { value: string; label: string; }[]; readonly?: boolean } => {
  return field.type === 'select';
};

const isCheckboxField = (field: any): field is { type: 'checkbox'; readonly?: boolean } => {
  return field.type === 'checkbox';
};

const isDateField = (field: any): field is { type: 'date'; readonly?: boolean } => {
  return field.type === 'date';
};

const isNumberField = (field: any): field is { type: 'number'; readonly?: boolean } => {
  return field.type === 'number';
};

// Perquisites Update Dialog Component
const PerquisitesDialog: React.FC<PerquisitesDialogProps> = ({
  open,
  onClose,
  onSave,
  initialData,
  loading
}) => {
  const [perquisitesData, setPerquisitesData] = useState<PerquisitesData>(initialData);
  const [activeStep, setActiveStep] = useState<number>(0);

  // Reset form when dialog opens/closes
  useEffect(() => {
    if (open) {
      setPerquisitesData(initialData);
      setActiveStep(0);
    }
  }, [open, initialData]);

  const handleInputChange = (field: keyof PerquisitesData, value: number | string | boolean): void => {
    setPerquisitesData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = async (): Promise<void> => {
    await onSave(perquisitesData);
  };

  const handleNext = (): void => {
    setActiveStep(prev => prev + 1);
  };

  const handleBack = (): void => {
    setActiveStep(prev => prev - 1);
  };

  const calculateAccommodationTotal = (): number => {
    let accommodationValue = 0;
    if (perquisitesData.accommodation_type === 'Government') {
      accommodationValue = Math.max(0, perquisitesData.employee_rent_payment - perquisitesData.license_fees);
    } else if (perquisitesData.accommodation_type === 'Employer-Owned') {
      let rate = 0.05; // 5% for below 15 lakhs
      if (perquisitesData.city_population === 'Above 40 lakhs') {
        rate = 0.10; // 10%
      } else if (perquisitesData.city_population === 'Between 15-40 lakhs') {
        rate = 0.075; // 7.5%
      }
      accommodationValue = perquisitesData.license_fees * rate;
    } else if (perquisitesData.accommodation_type === 'Employer-Leased') {
      accommodationValue = Math.max(0, perquisitesData.rent_paid_by_employer - perquisitesData.employee_rent_payment);
    } else if (perquisitesData.accommodation_type === 'Hotel') {
      accommodationValue = perquisitesData.hotel_charges * perquisitesData.stay_days;
    }
    
    // Add furniture perquisite if owned by employer
    if (perquisitesData.is_furniture_owned_by_employer) {
      accommodationValue += Math.max(0, perquisitesData.furniture_cost - perquisitesData.furniture_employee_payment);
    }
    
    return accommodationValue;
  };

  const calculateCarTransportTotal = (): number => {
    let carValue = 0;
    
    // Calculate car perquisite based on usage type
    if (perquisitesData.car_use_type === 'Personal') {
      // Personal use: 10% of car cost + driver cost
      carValue = (perquisitesData.car_cost_to_employer * 0.10) + perquisitesData.driver_cost;
    } else if (perquisitesData.car_use_type === 'Official') {
      // Official use: No perquisite
      carValue = 0;
    } else if (perquisitesData.car_use_type === 'Mixed') {
      // Mixed use: 5% of car cost + driver cost
      carValue = (perquisitesData.car_cost_to_employer * 0.05) + perquisitesData.driver_cost;
    }
    
    // Add other vehicle cost
    carValue += perquisitesData.other_vehicle_cost;
    
    return carValue;
  };

  const calculateTotalPerquisites = (): number => {
    let total = 0;
    
    // Calculate accommodation total
    total += calculateAccommodationTotal();
    
    // Calculate car and transport total
    total += calculateCarTransportTotal();
    
    total += perquisitesData.lta_amount_claimed;
    total += perquisitesData.esop_exercise_value;
    
    // Calculate free education total
    const freeEducationTotal = (perquisitesData.monthly_expenses_child1 * perquisitesData.months_child1 * (perquisitesData.employer_maintained_1st_child ? 1 : 0)) +
                              (perquisitesData.monthly_expenses_child2 * perquisitesData.months_child2 * (perquisitesData.employer_maintained_2nd_child ? 1 : 0));
    total += freeEducationTotal;
    
    // Calculate utilities total
    const utilitiesTotal = (perquisitesData.gas_paid_by_employer + 
                           perquisitesData.electricity_paid_by_employer + 
                           perquisitesData.water_paid_by_employer) -
                          (perquisitesData.gas_paid_by_employee + 
                           perquisitesData.electricity_paid_by_employee + 
                           perquisitesData.water_paid_by_employee);
    total += Math.max(0, utilitiesTotal);
    
    // Calculate movable asset usage total
    const movableAssetUsageTotal = perquisitesData.movable_asset_is_employer_owned 
      ? Math.max(0, (perquisitesData.movable_asset_usage_value * 0.1) - perquisitesData.movable_asset_employee_payment)
      : Math.max(0, perquisitesData.movable_asset_hire_cost - perquisitesData.movable_asset_employee_payment);
    total += movableAssetUsageTotal;
    
    // Calculate movable asset transfer total
    const depreciationRate = perquisitesData.movable_asset_transfer_type === 'Electronics' ? 0.5 
      : perquisitesData.movable_asset_transfer_type === 'Motor Vehicle' ? 0.2 : 0.1;
    const annualDepreciation = perquisitesData.movable_asset_transfer_cost * depreciationRate;
    const totalDepreciation = annualDepreciation * perquisitesData.movable_asset_years_of_use;
    const depreciatedValue = Math.max(0, perquisitesData.movable_asset_transfer_cost - totalDepreciation);
    const movableAssetTransferTotal = Math.max(0, depreciatedValue - perquisitesData.movable_asset_transfer_employee_payment);
    total += movableAssetTransferTotal;
    
    // Calculate lunch refreshment total
    const lunchRefreshmentTotal = Math.max(0, perquisitesData.lunch_employer_cost - perquisitesData.lunch_employee_payment);
    total += lunchRefreshmentTotal;
    
    // Calculate domestic help total
    const domesticHelpTotal = Math.max(0, perquisitesData.domestic_help_paid_by_employer - perquisitesData.domestic_help_paid_by_employee);
    total += domesticHelpTotal;
    
    // Calculate monetary benefits total
    const monetaryBenefitsTotal = Math.max(0, perquisitesData.monetary_benefit_amount - perquisitesData.monetary_benefit_employee_payment);
    total += monetaryBenefitsTotal;
    
    // Calculate club expenses total
    const clubExpensesTotal = Math.max(0, perquisitesData.club_expense_amount - perquisitesData.club_expense_employee_payment);
    total += clubExpensesTotal;
    
    total += perquisitesData.other_perquisites_amount;
    return total;
  };

  const steps = [
    // {
    //   label: 'Accommodation (Admin Only)',
    //   fields: [
    //     { name: 'accommodation_type', label: 'Accommodation Type', type: 'select', readonly: true, options: [
    //       { value: 'Employer-Owned', label: 'Employer-Owned' },
    //       { value: 'Government', label: 'Government' },
    //       { value: 'Employer-Leased', label: 'Employer-Leased' },
    //       { value: 'Hotel', label: 'Hotel' }
    //     ]},
    //     { name: 'city_population', label: 'City Population', type: 'select', readonly: true, options: [
    //       { value: 'Above 40 lakhs', label: 'Above 40 lakhs' },
    //       { value: 'Between 15-40 lakhs', label: 'Between 15-40 lakhs' },
    //       { value: 'Below 15 lakhs', label: 'Below 15 lakhs' }
    //     ]},
    //     { name: 'license_fees', label: 'License Fees (Government)', type: 'number', readonly: true },
    //     { name: 'employee_rent_payment', label: 'Employee Rent Payment', type: 'number', readonly: true },
    //     { name: 'rent_paid_by_employer', label: 'Rent Paid by Employer', type: 'number', readonly: true },
    //     { name: 'hotel_charges', label: 'Hotel Charges', type: 'number', readonly: true },
    //     { name: 'stay_days', label: 'Stay Days', type: 'number', readonly: true },
    //     { name: 'furniture_cost', label: 'Furniture Cost', type: 'number', readonly: true },
    //     { name: 'furniture_employee_payment', label: 'Furniture Employee Payment', type: 'number', readonly: true },
    //     { name: 'is_furniture_owned_by_employer', label: 'Furniture Owned by Employer', type: 'checkbox', readonly: true }
    //   ]
    // },
    // {
    //   label: 'Car & Transport',
    //   fields: [
    //     { name: 'car_use_type', label: 'Car Usage Type', type: 'select', readonly: true, options: [
    //       { value: 'Personal', label: 'Personal Only' },
    //       { value: 'Official', label: 'Official Only' },
    //       { value: 'Mixed', label: 'Personal & Official' }
    //     ]},
    //     { name: 'engine_capacity_cc', label: 'Engine Capacity (CC)', type: 'number', readonly: true },
    //     { name: 'months_used', label: 'Months Used', type: 'number', readonly: true },
    //     { name: 'months_used_other_vehicle', label: 'Months Used Other Vehicle', type: 'number', readonly: true },
    //     { name: 'car_cost_to_employer', label: 'Car Cost to Employer', type: 'number', readonly: true },
    //     { name: 'other_vehicle_cost', label: 'Other Vehicle Cost', type: 'number', readonly: true },
    //     { name: 'driver_cost', label: 'Driver Cost', type: 'number', readonly: true },
    //     { name: 'has_expense_reimbursement', label: 'Expense Reimbursement', type: 'checkbox', readonly: true },
    //     { name: 'driver_provided', label: 'Driver Provided', type: 'checkbox', readonly: true }
    //   ]
    // },
    {
      label: 'LTA',
      fields: [
        { name: 'travel_mode', label: 'Travel Mode', type: 'select', options: [
          { value: 'Air', label: 'Air' },
          { value: 'Railways', label: 'Railways' },
          { value: 'Bus', label: 'Bus' },
          { value: 'Other', label: 'Other' }
        ]},
        { name: 'lta_allocated_yearly', label: 'LTA Allocated Yearly', type: 'number', readonly: true },
        { name: 'lta_amount_claimed', label: 'LTA Amount Claimed', type: 'number' },
        { name: 'lta_claimed_count', label: 'LTA Claims Count', type: 'number' },
        { name: 'public_transport_cost', label: 'Public Transport Cost (for same distance)', type: 'number' },
        { name: 'is_monthly_paid', label: 'LTA Paid Monthly', type: 'checkbox', readonly: true }
      ]
    },
    // {
    //   label: 'Interest Free/Concessional Loan',
    //   fields: [
    //     { name: 'loan_amount', label: 'Interest-free Loan Amount', type: 'number', readonly: true },
    //     { name: 'emi_amount', label: 'EMI Amount', type: 'number', readonly: true },
    //     { name: 'company_interest_rate', label: 'Interest Rate Charged (%)', type: 'number', readonly: true },
    //     { name: 'sbi_interest_rate', label: 'SBI Rate (%)', type: 'number', readonly: true },
    //     { name: 'loan_type', label: 'Loan Type', type: 'select', readonly: true, options: [
    //       { value: 'Personal', label: 'Personal' },
    //       { value: 'Medical', label: 'Medical' },
    //       { value: 'Education', label: 'Education' },
    //       { value: 'Housing', label: 'Housing' },
    //       { value: 'Vehicle', label: 'Vehicle' },
    //       { value: 'Other', label: 'Other' }
    //     ]},
    //     { name: 'loan_start_date', label: 'Loan Start Date', type: 'date', readonly: true }
    //   ]
    // },
    {
      label: 'Education',
      fields: [
        { name: 'monthly_expenses_child1', label: 'Monthly Expenses - 1st Child', type: 'number' },
        { name: 'monthly_expenses_child2', label: 'Monthly Expenses - 2nd Child', type: 'number' },
        { name: 'months_child1', label: 'Months - 1st Child', type: 'number' },
        { name: 'months_child2', label: 'Months - 2nd Child', type: 'number' },
        { name: 'employer_maintained_1st_child', label: 'Institution Maintained by Employer - 1st Child', type: 'checkbox' },
        { name: 'employer_maintained_2nd_child', label: 'Institution Maintained by Employer - 2nd Child', type: 'checkbox' }
      ]
    },
    // {
    //   label: 'Utilities (Admin Only)',
    //   fields: [
    //     { name: 'gas_paid_by_employer', label: 'Gas Incurred by Employer', type: 'number', readonly: true },
    //     { name: 'electricity_paid_by_employer', label: 'Electricity Incurred by Employer', type: 'number', readonly: true },
    //     { name: 'water_paid_by_employer', label: 'Water Incurred by Employer', type: 'number', readonly: true },
    //     { name: 'gas_paid_by_employee', label: 'Gas Paid by Employee', type: 'number', readonly: true },
    //     { name: 'electricity_paid_by_employee', label: 'Electricity Paid by Employee', type: 'number', readonly: true },
    //     { name: 'water_paid_by_employee', label: 'Water Paid by Employee', type: 'number', readonly: true },
    //     { name: 'is_gas_manufactured_by_employer', label: 'Gas Manufactured by Employer', type: 'checkbox', readonly: true },
    //     { name: 'is_electricity_manufactured_by_employer', label: 'Electricity Manufactured by Employer', type: 'checkbox', readonly: true },
    //     { name: 'is_water_manufactured_by_employer', label: 'Water Manufactured by Employer', type: 'checkbox', readonly: true }
    //   ]
    // },
    {
      label: 'ESOP',
      fields: [
        { name: 'esop_exercise_value', label: 'ESOP Exercise Value', type: 'number' },
        { name: 'esop_fair_market_value', label: 'ESOP Fair Market Value', type: 'number' },
        { name: 'esop_shares_exercised', label: 'ESOP Shares Exercised', type: 'number' }
      ]
    },
    // {
    //   label: 'Meals Provided (Admin Only)',
    //   fields: [
    //     { name: 'lunch_employer_cost', label: 'Cost Paid by Employer', type: 'number', readonly: true },
    //     { name: 'lunch_employee_payment', label: 'Payment by Employee', type: 'number', readonly: true },
    //     { name: 'lunch_meal_days_per_year', label: 'Meal Days per Year', type: 'number', readonly: true }
    //   ]
    // },
    {
      label: 'Domestic Help',
      fields: [
        { name: 'domestic_help_paid_by_employer', label: 'Cost Paid by Employer', type: 'number' },
        { name: 'domestic_help_paid_by_employee', label: 'Payment by Employee', type: 'number' }
      ]
    },
    // {
    //   label: 'Movable Asset Usage (Admin Only)',
    //   fields: [
    //     { name: 'movable_asset_type', label: 'Asset Type', type: 'select', readonly: true, options: [
    //       { value: 'Electronics', label: 'Electronics' },
    //       { value: 'Motor Vehicle', label: 'Motor Vehicle' },
    //       { value: 'Others', label: 'Others' }
    //     ]},
    //     { name: 'movable_asset_usage_value', label: 'Asset Value', type: 'number', readonly: true },
    //     { name: 'movable_asset_hire_cost', label: 'Hire Cost', type: 'number', readonly: true },
    //     { name: 'movable_asset_employee_payment', label: 'Payment by Employee', type: 'number', readonly: true },
    //     { name: 'movable_asset_is_employer_owned', label: 'Asset Owned by Employer', type: 'checkbox', readonly: true }
    //   ]
    // },
    // {
    //   label: 'Movable Asset Transfer (Admin Only)',
    //   fields: [
    //     { name: 'movable_asset_transfer_type', label: 'Asset Type', type: 'select', readonly: true, options: [
    //       { value: 'Electronics', label: 'Electronics' },
    //       { value: 'Motor Vehicle', label: 'Motor Vehicle' },
    //       { value: 'Others', label: 'Others' }
    //     ]},
    //     { name: 'movable_asset_transfer_cost', label: 'Original Asset Cost', type: 'number', readonly: true },
    //     { name: 'movable_asset_years_of_use', label: 'Years of Use', type: 'number', readonly: true },
    //     { name: 'movable_asset_transfer_employee_payment', label: 'Payment by Employee', type: 'number', readonly: true }
    //   ]
    // },
    // {
    //   label: 'Monetary Benefits (Admin Only)',
    //   fields: [
    //     { name: 'monetary_benefit_type', label: 'Benefit Type', type: 'select', readonly: true, options: [
    //       { value: 'Cash Gift', label: 'Cash Gift' },
    //       { value: 'Voucher', label: 'Voucher' },
    //       { value: 'Others', label: 'Others' }
    //     ]},
    //     { name: 'monetary_benefit_amount', label: 'Benefit Amount', type: 'number', readonly: true },
    //     { name: 'monetary_benefit_employee_payment', label: 'Payment by Employee', type: 'number', readonly: true }
    //   ]
    // },
    // {
    //   label: 'Club Expenses (Admin Only)',
    //   fields: [
    //     { name: 'club_expense_type', label: 'Expense Type', type: 'select', readonly: true, options: [
    //       { value: 'Membership Fee', label: 'Membership Fee' },
    //       { value: 'Annual Fee', label: 'Annual Fee' },
    //       { value: 'Others', label: 'Others' }
    //     ]},
    //     { name: 'club_expense_amount', label: 'Expense Amount', type: 'number', readonly: true },
    //     { name: 'club_expense_employee_payment', label: 'Payment by Employee', type: 'number', readonly: true }
    //   ]
    // },
    // {
    //   label: 'Other Benefits (Admin Only)',
    //   fields: [
    //     { name: 'other_benefit_type', label: 'Benefit Type', type: 'select', readonly: true, options: [
    //       { value: 'Education', label: 'Education' },
    //       { value: 'Medical', label: 'Medical' },
    //       { value: 'Transport', label: 'Transport' },
    //       { value: 'Others', label: 'Others' }
    //     ]},
    //     { name: 'other_benefit_amount', label: 'Benefit Amount', type: 'number', readonly: true },
    //     { name: 'other_benefit_employee_payment', label: 'Payment by Employee', type: 'number', readonly: true }
    //   ]
    // }
  ];

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <CardGiftcardIcon color="primary" />
          <Typography variant="h6">
            Update Perquisites
          </Typography>
        </Box>
      </DialogTitle>
      <DialogContent>
        {/* Summary Card */}
        <Card variant="outlined" sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Perquisites Summary
            </Typography>
            
            {/* Accommodation Section */}
            <Typography variant="subtitle1" color="primary" sx={{ mt: 2, mb: 1, fontWeight: 'bold' }}>
              Accommodation
            </Typography>
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Accommodation Type</Typography>
                <Typography variant="h6">{perquisitesData.accommodation_type}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">City Population</Typography>
                <Typography variant="h6">{perquisitesData.city_population}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">License Fees</Typography>
                <Typography variant="h6">₹{perquisitesData.license_fees.toLocaleString('en-IN')}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Employee Rent Payment</Typography>
                <Typography variant="h6">₹{perquisitesData.employee_rent_payment.toLocaleString('en-IN')}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Rent Paid by Employer</Typography>
                <Typography variant="h6">₹{perquisitesData.rent_paid_by_employer.toLocaleString('en-IN')}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Hotel Charges</Typography>
                <Typography variant="h6">₹{perquisitesData.hotel_charges.toLocaleString('en-IN')}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Stay Days</Typography>
                <Typography variant="h6">{perquisitesData.stay_days}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Furniture Cost</Typography>
                <Typography variant="h6">₹{perquisitesData.furniture_cost.toLocaleString('en-IN')}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Accommodation Total</Typography>
                <Typography variant="h6" color="primary">₹{calculateAccommodationTotal().toLocaleString('en-IN')}</Typography>
              </Grid>
            </Grid>

            {/* Car & Transport Section */}
            <Typography variant="subtitle1" color="primary" sx={{ mt: 2, mb: 1, fontWeight: 'bold' }}>
              Car & Transport
            </Typography>
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Car Usage Type</Typography>
                <Typography variant="h6">{perquisitesData.car_use_type}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Engine Capacity</Typography>
                <Typography variant="h6">{perquisitesData.engine_capacity_cc} CC</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Months Used</Typography>
                <Typography variant="h6">{perquisitesData.months_used}</Typography>
            </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Car Cost to Employer</Typography>
                <Typography variant="h6">₹{perquisitesData.car_cost_to_employer.toLocaleString('en-IN')}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Driver Cost</Typography>
                <Typography variant="h6">₹{perquisitesData.driver_cost.toLocaleString('en-IN')}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Driver Provided</Typography>
                <Typography variant="h6">{perquisitesData.driver_provided ? 'Yes' : 'No'}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Car & Transport Total</Typography>
                <Typography variant="h6" color="primary">₹{calculateCarTransportTotal().toLocaleString('en-IN')}</Typography>
              </Grid>
            </Grid>

            {/* LTA Section */}
            <Typography variant="subtitle1" color="primary" sx={{ mt: 2, mb: 1, fontWeight: 'bold' }}>
              Leave Travel Allowance (LTA)
            </Typography>
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">LTA Allocated Yearly</Typography>
                <Typography variant="h6">₹{perquisitesData.lta_allocated_yearly.toLocaleString('en-IN')}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">LTA Amount Claimed</Typography>
                <Typography variant="h6">₹{perquisitesData.lta_amount_claimed.toLocaleString('en-IN')}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">LTA Paid Monthly</Typography>
                <Typography variant="h6">{perquisitesData.is_monthly_paid ? 'Yes' : 'No'}</Typography>
              </Grid>
            </Grid>

            {/* Other Perquisites Section */}
            <Typography variant="subtitle1" color="primary" sx={{ mt: 2, mb: 1, fontWeight: 'bold' }}>
              Other Perquisites
            </Typography>
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">ESOP Exercise Value</Typography>
                <Typography variant="h6">₹{perquisitesData.esop_exercise_value.toLocaleString('en-IN')}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Other Perquisites</Typography>
                <Typography variant="h6">₹{perquisitesData.other_perquisites_amount.toLocaleString('en-IN')}</Typography>
              </Grid>
            </Grid>

            {/* Interest Free/Concessional Loan Section */}
            <Typography variant="subtitle1" color="primary" sx={{ mt: 2, mb: 1, fontWeight: 'bold' }}>
              Interest Free/Concessional Loan
            </Typography>
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Loan Amount</Typography>
                <Typography variant="h6">₹{perquisitesData.loan_amount.toLocaleString('en-IN')}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">EMI Amount</Typography>
                <Typography variant="h6">₹{perquisitesData.emi_amount.toLocaleString('en-IN')}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Company Interest Rate</Typography>
                <Typography variant="h6">{perquisitesData.company_interest_rate}%</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">SBI Interest Rate</Typography>
                <Typography variant="h6">{perquisitesData.sbi_interest_rate}%</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Loan Type</Typography>
                <Typography variant="h6">{perquisitesData.loan_type}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Loan Start Date</Typography>
                <Typography variant="h6">{perquisitesData.loan_start_date}</Typography>
              </Grid>
            </Grid>

            {/* Utilities Section */}
            <Typography variant="subtitle1" color="primary" sx={{ mt: 2, mb: 1, fontWeight: 'bold' }}>
              Utilities (Admin Only)
            </Typography>
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Gas Paid by Employer</Typography>
                <Typography variant="h6">₹{perquisitesData.gas_paid_by_employer.toLocaleString('en-IN')}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Electricity Paid by Employer</Typography>
                <Typography variant="h6">₹{perquisitesData.electricity_paid_by_employer.toLocaleString('en-IN')}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Water Paid by Employer</Typography>
                <Typography variant="h6">₹{perquisitesData.water_paid_by_employer.toLocaleString('en-IN')}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Gas Paid by Employee</Typography>
                <Typography variant="h6">₹{perquisitesData.gas_paid_by_employee.toLocaleString('en-IN')}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Electricity Paid by Employee</Typography>
                <Typography variant="h6">₹{perquisitesData.electricity_paid_by_employee.toLocaleString('en-IN')}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Water Paid by Employee</Typography>
                <Typography variant="h6">₹{perquisitesData.water_paid_by_employee.toLocaleString('en-IN')}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Gas Manufactured by Employer</Typography>
                <Typography variant="h6">{perquisitesData.is_gas_manufactured_by_employer ? 'Yes' : 'No'}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Electricity Manufactured by Employer</Typography>
                <Typography variant="h6">{perquisitesData.is_electricity_manufactured_by_employer ? 'Yes' : 'No'}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Water Manufactured by Employer</Typography>
                <Typography variant="h6">{perquisitesData.is_water_manufactured_by_employer ? 'Yes' : 'No'}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Utilities Total</Typography>
                <Typography variant="h6" color="primary">₹{((perquisitesData.gas_paid_by_employer + 
                                 perquisitesData.electricity_paid_by_employer + 
                                 perquisitesData.water_paid_by_employer) -
                                (perquisitesData.gas_paid_by_employee + 
                                 perquisitesData.electricity_paid_by_employee + 
                                 perquisitesData.water_paid_by_employee)).toLocaleString('en-IN')}</Typography>
              </Grid>
            </Grid>

            {/* Meals Provided Section */}
            <Typography variant="subtitle1" color="primary" sx={{ mt: 2, mb: 1, fontWeight: 'bold' }}>
              Meals Provided (Admin Only)
            </Typography>
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Cost Paid by Employer</Typography>
                <Typography variant="h6">₹{perquisitesData.lunch_employer_cost.toLocaleString('en-IN')}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Payment by Employee</Typography>
                <Typography variant="h6">₹{perquisitesData.lunch_employee_payment.toLocaleString('en-IN')}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Meal Days per Year</Typography>
                <Typography variant="h6">{perquisitesData.lunch_meal_days_per_year}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Meals Total</Typography>
                <Typography variant="h6" color="primary">₹{Math.max(0, perquisitesData.lunch_employer_cost - perquisitesData.lunch_employee_payment).toLocaleString('en-IN')}</Typography>
              </Grid>
            </Grid>

            {/* Movable Asset Usage Section */}
            <Typography variant="subtitle1" color="primary" sx={{ mt: 2, mb: 1, fontWeight: 'bold' }}>
              Movable Asset Usage (Admin Only)
            </Typography>
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Asset Type</Typography>
                <Typography variant="h6">{perquisitesData.movable_asset_type || 'Not specified'}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Asset Value</Typography>
                <Typography variant="h6">₹{perquisitesData.movable_asset_usage_value.toLocaleString('en-IN')}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Hire Cost</Typography>
                <Typography variant="h6">₹{perquisitesData.movable_asset_hire_cost.toLocaleString('en-IN')}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Asset Usage Total</Typography>
                <Typography variant="h6" color="primary">₹{Math.max(0, perquisitesData.movable_asset_hire_cost - perquisitesData.movable_asset_employee_payment).toLocaleString('en-IN')}</Typography>
              </Grid>
            </Grid>

            {/* Movable Asset Transfer Section */}
            <Typography variant="subtitle1" color="primary" sx={{ mt: 2, mb: 1, fontWeight: 'bold' }}>
              Movable Asset Transfer (Admin Only)
            </Typography>
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Asset Type</Typography>
                <Typography variant="h6">{perquisitesData.movable_asset_transfer_type || 'Not specified'}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Original Cost</Typography>
                <Typography variant="h6">₹{perquisitesData.movable_asset_transfer_cost.toLocaleString('en-IN')}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Years of Use</Typography>
                <Typography variant="h6">{perquisitesData.movable_asset_years_of_use}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Asset Transfer Total</Typography>
                <Typography variant="h6" color="primary">₹{Math.max(0, perquisitesData.movable_asset_transfer_cost - perquisitesData.movable_asset_transfer_employee_payment).toLocaleString('en-IN')}</Typography>
              </Grid>
            </Grid>

            {/* Monetary Benefits Section */}
            <Typography variant="subtitle1" color="primary" sx={{ mt: 2, mb: 1, fontWeight: 'bold' }}>
              Monetary Benefits (Admin Only)
            </Typography>
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Benefit Type</Typography>
                <Typography variant="h6">{perquisitesData.monetary_benefit_type || 'Not specified'}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Benefit Amount</Typography>
                <Typography variant="h6">₹{perquisitesData.monetary_benefit_amount.toLocaleString('en-IN')}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Payment by Employee</Typography>
                <Typography variant="h6">₹{perquisitesData.monetary_benefit_employee_payment.toLocaleString('en-IN')}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Monetary Benefits Total</Typography>
                <Typography variant="h6" color="primary">₹{Math.max(0, perquisitesData.monetary_benefit_amount - perquisitesData.monetary_benefit_employee_payment).toLocaleString('en-IN')}</Typography>
              </Grid>
            </Grid>

            {/* Club Expenses Section */}
            <Typography variant="subtitle1" color="primary" sx={{ mt: 2, mb: 1, fontWeight: 'bold' }}>
              Club Expenses (Admin Only)
            </Typography>
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Expense Type</Typography>
                <Typography variant="h6">{perquisitesData.club_expense_type || 'Not specified'}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Expense Amount</Typography>
                <Typography variant="h6">₹{perquisitesData.club_expense_amount.toLocaleString('en-IN')}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Payment by Employee</Typography>
                <Typography variant="h6">₹{perquisitesData.club_expense_employee_payment.toLocaleString('en-IN')}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Club Expenses Total</Typography>
                <Typography variant="h6" color="primary">₹{Math.max(0, perquisitesData.club_expense_amount - perquisitesData.club_expense_employee_payment).toLocaleString('en-IN')}</Typography>
              </Grid>
            </Grid>

            {/* Other Benefits Section */}
            <Typography variant="subtitle1" color="primary" sx={{ mt: 2, mb: 1, fontWeight: 'bold' }}>
              Other Benefits (Admin Only)
            </Typography>
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Benefit Type</Typography>
                <Typography variant="h6">{perquisitesData.other_benefit_type || 'Not specified'}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Benefit Amount</Typography>
                <Typography variant="h6">₹{perquisitesData.other_benefit_amount.toLocaleString('en-IN')}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Payment by Employee</Typography>
                <Typography variant="h6">₹{perquisitesData.other_benefit_employee_payment.toLocaleString('en-IN')}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Other Benefits Total</Typography>
                <Typography variant="h6" color="primary">₹{Math.max(0, perquisitesData.other_benefit_amount - perquisitesData.other_benefit_employee_payment).toLocaleString('en-IN')}</Typography>
              </Grid>
            </Grid>

            {/* Total Perquisites */}
            <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
              <Typography variant="h6" color="primary" sx={{ fontWeight: 'bold' }}>
                Total Perquisites: ₹{calculateTotalPerquisites().toLocaleString('en-IN')}
              </Typography>
            </Box>
          </CardContent>
        </Card>

        {/* Stepper Form */}
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
                        <FormControl fullWidth size="small">
                          <InputLabel>{field.label}</InputLabel>
                          <Select
                            value={perquisitesData[field.name as keyof PerquisitesData] as string}
                            label={field.label}
                            onChange={(e: SelectChangeEvent) => 
                              handleInputChange(field.name as keyof PerquisitesData, e.target.value)
                            }
                            disabled={Boolean(field.readonly)}
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
                              checked={perquisitesData[field.name as keyof PerquisitesData] as boolean}
                              onChange={(e) => 
                                handleInputChange(field.name as keyof PerquisitesData, e.target.checked)
                              }
                              disabled={Boolean(field.readonly)}
                            />
                          }
                          label={field.label}
                        />
                      ) : isDateField(field) ? (
                        <TextField
                          fullWidth
                          label={field.label}
                          type="date"
                          value={perquisitesData[field.name as keyof PerquisitesData] as string}
                          onChange={(e) => {
                            handleInputChange(field.name as keyof PerquisitesData, e.target.value);
                          }}
                          InputLabelProps={{ shrink: true }}
                          size="small"
                          disabled={Boolean(field.readonly)}
                        />
                      ) : isNumberField(field) ? (
                        <TextField
                          fullWidth
                          label={field.label}
                          type="number"
                          value={perquisitesData[field.name as keyof PerquisitesData] as number}
                          onChange={(e) => {
                            const value = parseFloat(e.target.value) || 0;
                            handleInputChange(field.name as keyof PerquisitesData, value);
                          }}
                          InputProps={{
                            startAdornment: field.name.includes('rate') || field.name.includes('percent') 
                              ? <Typography variant="body2" sx={{ mr: 1 }}>%</Typography>
                              : <Typography variant="body2" sx={{ mr: 1 }}>₹</Typography>
                          }}
                          size="small"
                          disabled={Boolean(field.readonly)}
                        />
                      ) : (
                        <TextField
                          fullWidth
                          label={field.label}
                          type="number"
                          value={perquisitesData[field.name as keyof PerquisitesData] as number}
                          onChange={(e) => {
                            const value = parseFloat(e.target.value) || 0;
                            handleInputChange(field.name as keyof PerquisitesData, value);
                          }}
                          InputProps={{
                            startAdornment: field.name.includes('rate') || field.name.includes('percent') 
                              ? <Typography variant="body2" sx={{ mr: 1 }}>%</Typography>
                              : <Typography variant="body2" sx={{ mr: 1 }}>₹</Typography>
                          }}
                          size="small"
                          disabled={Boolean(field.readonly)}
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
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button 
          onClick={handleSave} 
          variant="contained" 
          disabled={loading}
          startIcon={loading ? <CircularProgress size={16} /> : <SaveIcon />}
        >
          {loading ? 'Saving...' : 'Save Perquisites'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

const MySalaryComponents: React.FC = () => {
  const { user } = useAuth();
  
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [components, setComponents] = useState<ComponentSummary[]>([]);
  const [computedTax, setComputedTax] = useState<number>(0);
  const [taxLoading, setTaxLoading] = useState<boolean>(false);
  const [taxError, setTaxError] = useState<string | null>(null);
  const [selectedTaxYear, setSelectedTaxYear] = useState<string>(getCurrentTaxYear());
  const [toast, setToast] = useState<ToastState>({ show: false, message: '', severity: 'success' });
  const [exportLoading, setExportLoading] = useState<boolean>(false);
  
  // Deductions dialog state
  const [deductionsDialogOpen, setDeductionsDialogOpen] = useState<boolean>(false);
  const [deductionsLoading, setDeductionsLoading] = useState<boolean>(false);
  const [deductionsData, setDeductionsData] = useState<DeductionsData>(initialDeductionsData);
  
  // House property dialog state
  const [housePropertyDialogOpen, setHousePropertyDialogOpen] = useState<boolean>(false);
  const [housePropertyLoading, setHousePropertyLoading] = useState<boolean>(false);
  const [housePropertyData, setHousePropertyData] = useState<HousePropertyData>(initialHousePropertyData);
  
  // Capital gains dialog state
  const [capitalGainsDialogOpen, setCapitalGainsDialogOpen] = useState<boolean>(false);
  const [capitalGainsLoading, setCapitalGainsLoading] = useState<boolean>(false);
  const [capitalGainsData, setCapitalGainsData] = useState<CapitalGainsData>(initialCapitalGainsData);
  
  // Other income dialog state
  const [otherIncomeDialogOpen, setOtherIncomeDialogOpen] = useState<boolean>(false);
  const [otherIncomeLoading, setOtherIncomeLoading] = useState<boolean>(false);
  const [otherIncomeData, setOtherIncomeData] = useState<OtherIncomeData>(initialOtherIncomeData);
  
  // Perquisites dialog state
  const [perquisitesDialogOpen, setPerquisitesDialogOpen] = useState<boolean>(false);
  const [perquisitesLoading, setPerquisitesLoading] = useState<boolean>(false);
  const [perquisitesData, setPerquisitesData] = useState<PerquisitesData>(initialPerquisitesData);

  const isCurrentYear = selectedTaxYear === getCurrentTaxYear();
  const availableTaxYears = getAvailableTaxYears();
  const employeeId = user?.employee_id;

  // 1. loadSalaryComponent
  const loadSalaryComponent = useCallback(async (): Promise<ComponentSummary | null> => {
    try {
      const response = await taxationApi.getComponent(employeeId!, selectedTaxYear, 'salary');
      const data = response?.component_data || response;
      
      const totalSalary = (data.basic_salary || 0) + 
                          (data.dearness_allowance || 0) + 
                          (data.hra_provided || 0) + 
                          (data.special_allowance || 0) + 
                          (data.bonus || 0) + 
                          (data.commission || 0);
      
      return {
        id: 'salary',
        name: 'Salary Income',
        icon: <AccountBalanceIcon />,
        color: 'primary',
        hasData: totalSalary > 0,
        totalValue: totalSalary,
        details: data,
        description: 'Basic salary, allowances, and other earnings'
      };
    } catch (error) {
      return {
        id: 'salary',
        name: 'Salary Income',
        icon: <AccountBalanceIcon />,
        color: 'primary',
        hasData: false,
        totalValue: 0,
        details: {},
        description: 'Basic salary, allowances, and other earnings'
      };
    }
  }, [employeeId, selectedTaxYear]);

  // 2. loadDeductionsComponent
  const loadDeductionsComponent = useCallback(async (): Promise<ComponentSummary | null> => {
    try {
      const response = await taxationApi.getComponent(employeeId!, selectedTaxYear, 'deductions');
      const data = response?.component_data || response;
      
      const section80c = data.section_80c || {};
      const section80d = data.section_80d || {};
      
      const totalDeductions = Object.values(section80c).reduce((sum: number, val: any) => sum + (Number(val) || 0), 0) +
                             Object.values(section80d).reduce((sum: number, val: any) => sum + (Number(val) || 0), 0);
      
      return {
        id: 'deductions',
        name: 'Deductions',
        icon: <ReceiptIcon />,
        color: 'info',
        hasData: totalDeductions > 0,
        totalValue: totalDeductions,
        details: data,
        description: 'Section 80C, 80D, and other tax-saving investments'
      };
    } catch (error) {
      return {
        id: 'deductions',
        name: 'Deductions',
        icon: <ReceiptIcon />,
        color: 'info',
        hasData: false,
        totalValue: 0,
        details: {},
        description: 'Section 80C, 80D, and other tax-saving investments'
      };
    }
  }, [employeeId, selectedTaxYear]);

  // 3. loadHousePropertyComponent
  const loadHousePropertyComponent = useCallback(async (): Promise<ComponentSummary | null> => {
    try {
      const response = await taxationApi.getComponent(employeeId!, selectedTaxYear, 'house_property_income');
      const data = response?.component_data || response;
      
      const totalValue = (data.annual_rent_received || 0);
      
      return {
        id: 'house_property_income',
        name: 'House Property',
        icon: <HomeIcon />,
        color: 'warning',
        hasData: totalValue > 0,
        totalValue: totalValue,
        details: data,
        description: 'Rental income, home loan interest, and municipal taxes'
      };
    } catch (error) {
      return {
        id: 'house_property_income',
        name: 'House Property',
        icon: <HomeIcon />,
        color: 'warning',
        hasData: false,
        totalValue: 0,
        details: {},
        description: 'Rental income, home loan interest, and municipal taxes'
      };
    }
  }, [employeeId, selectedTaxYear]);

  // 4. loadCapitalGainsComponent
  const loadCapitalGainsComponent = useCallback(async (): Promise<ComponentSummary | null> => {
    try {
      const response = await taxationApi.getComponent(employeeId!, selectedTaxYear, 'capital_gains');
      const data = response?.component_data || response;
      
      const totalCapitalGains = (data.stcg_111a_equity_stt || 0) + 
                               (data.ltcg_112a_equity_stt || 0);
      
      return {
        id: 'capital_gains',
        name: 'Capital Gains',
        icon: <TrendingUpIcon />,
        color: 'success',
        hasData: totalCapitalGains > 0,
        totalValue: totalCapitalGains,
        details: data,
        description: 'Short-term and long-term capital gains from investments'
      };
    } catch (error) {
      return {
        id: 'capital_gains',
        name: 'Capital Gains',
        icon: <TrendingUpIcon />,
        color: 'success',
        hasData: false,
        totalValue: 0,
        details: {},
        description: 'Short-term and long-term capital gains from investments'
      };
    }
  }, [employeeId, selectedTaxYear]);

  // 5. loadOtherIncomeComponent
  const loadOtherIncomeComponent = useCallback(async (): Promise<ComponentSummary | null> => {
    try {
      const response = await taxationApi.getComponent(employeeId!, selectedTaxYear, 'other_income');
      const data = response?.component_data || response;
      
      const totalOtherIncome = (data.dividend_income || 0) + 
                              (data.gifts_received || 0);
      
      return {
        id: 'other_income',
        name: 'Other Income',
        icon: <BusinessIcon />,
        color: 'secondary',
        hasData: totalOtherIncome > 0,
        totalValue: totalOtherIncome,
        details: data,
        description: 'Interest income, dividends, gifts, and business income'
      };
    } catch (error) {
      return {
        id: 'other_income',
        name: 'Other Income',
        icon: <BusinessIcon />,
        color: 'secondary',
        hasData: false,
        totalValue: 0,
        details: {},
        description: 'Interest income, dividends, gifts, and business income'
      };
    }
  }, [employeeId, selectedTaxYear]);

  // 6. loadPerquisitesComponent
  const loadPerquisitesComponent = useCallback(async (): Promise<ComponentSummary | null> => {
    try {
      const response = await taxationApi.getComponent(employeeId!, selectedTaxYear, 'perquisites');
      const data = response?.component_data || response;
      
      // Calculate accommodation perquisite
      let accommodationValue = 0;
      if (data.accommodation) {
        const acc = data.accommodation;
        if (acc.accommodation_type === 'Government') {
          accommodationValue = Math.max(0, (acc.employee_rent_payment || 0) - (acc.license_fees || 0));
        } else if (acc.accommodation_type === 'Employer-Owned') {
          let rate = 0.05; // 5% for below 15 lakhs
          if (acc.city_population === 'Above 40 lakhs') {
            rate = 0.10; // 10%
          } else if (acc.city_population === 'Between 15-40 lakhs') {
            rate = 0.075; // 7.5%
          }
          accommodationValue = (acc.license_fees || 0) * rate;
        } else if (acc.accommodation_type === 'Employer-Leased') {
          accommodationValue = Math.max(0, (acc.rent_paid_by_employer || 0) - (acc.employee_rent_payment || 0));
        } else if (acc.accommodation_type === 'Hotel') {
          accommodationValue = (acc.hotel_charges || 0) * (acc.stay_days || 0);
        }
        
        // Add furniture perquisite if owned by employer
        if (acc.is_furniture_owned_by_employer) {
          accommodationValue += Math.max(0, (acc.furniture_cost || 0) - (acc.furniture_employee_payment || 0));
        }
      }
      
      // Calculate car perquisite
      let carValue = 0;
      if (data.car) {
        const car = data.car;
        if (car.car_use_type === 'Personal') {
          // Personal use: 10% of car cost + driver cost
          carValue = ((car.car_cost_to_employer || 0) * 0.10) + (car.driver_cost || 0);
        } else if (car.car_use_type === 'Official') {
          // Official use: No perquisite
          carValue = 0;
        } else if (car.car_use_type === 'Mixed') {
          // Mixed use: 5% of car cost + driver cost
          carValue = ((car.car_cost_to_employer || 0) * 0.05) + (car.driver_cost || 0);
        }
        
        // Add other vehicle cost
        carValue += (car.other_vehicle_cost || 0);
      }
      
      // Calculate LTA perquisite
      const ltaValue = data.lta?.lta_amount_claimed || 0;
      
      // Calculate interest-free loan perquisite
      let loanValue = 0;
      if (data.interest_free_loan) {
        const loan = data.interest_free_loan;
        const outstandingAmount = loan.outstanding_amount || loan.loan_amount || 0;
        const sbiRate = loan.sbi_interest_rate || 6.5;
        const companyRate = loan.company_interest_rate || 0;
        loanValue = Math.max(0, (outstandingAmount * (sbiRate - companyRate) / 100));
      }
      
      // Calculate ESOP perquisite
      let esopValue = 0;
      if (data.esop) {
        const esop = data.esop;
        const sharesExercised = esop.shares_exercised || 0;
        const exercisePrice = esop.exercise_price || 0;
        const allotmentPrice = esop.allotment_price || 0;
        esopValue = sharesExercised * Math.max(0, allotmentPrice - exercisePrice);
      }
      
      // Calculate free education perquisite
      let educationValue = 0;
      if (data.free_education) {
        const edu = data.free_education;
        if (edu.employer_maintained_1st_child) {
          educationValue += (edu.monthly_expenses_child1 || 0) * (edu.months_child1 || 12);
        }
        if (edu.employer_maintained_2nd_child) {
          educationValue += (edu.monthly_expenses_child2 || 0) * (edu.months_child2 || 12);
        }
      }
      
      // Calculate utilities perquisite
      let utilitiesValue = 0;
      if (data.utilities) {
        const util = data.utilities;
        utilitiesValue = Math.max(0, 
          ((util.gas_paid_by_employer || 0) + (util.electricity_paid_by_employer || 0) + (util.water_paid_by_employer || 0)) -
          ((util.gas_paid_by_employee || 0) + (util.electricity_paid_by_employee || 0) + (util.water_paid_by_employee || 0))
        );
      }
      
      // Calculate lunch refreshment perquisite
      let lunchValue = 0;
      if (data.lunch_refreshment) {
        const lunch = data.lunch_refreshment;
        lunchValue = Math.max(0, (lunch.employer_cost || 0) - (lunch.employee_payment || 0));
      }
      
      // Calculate domestic help perquisite
      let domesticHelpValue = 0;
      if (data.domestic_help) {
        const domestic = data.domestic_help;
        domesticHelpValue = Math.max(0, (domestic.domestic_help_paid_by_employer || 0) - (domestic.domestic_help_paid_by_employee || 0));
      }
      
      const totalPerquisites = accommodationValue + carValue + ltaValue + loanValue + esopValue + 
                               educationValue + utilitiesValue + lunchValue + domesticHelpValue;
      
      // Debug logging
      console.log('Perquisites calculation:', {
        accommodationValue,
        carValue,
        ltaValue,
        loanValue,
        esopValue,
        educationValue,
        utilitiesValue,
        lunchValue,
        domesticHelpValue,
        totalPerquisites
      });
      
      return {
        id: 'perquisites',
        name: 'Perquisites',
        icon: <CardGiftcardIcon />,
        color: 'error',
        hasData: totalPerquisites > 0,
        totalValue: totalPerquisites,
        details: data,
        description: 'Accommodation, car, medical, LTA, ESOP, and other benefits'
      };
    } catch (error) {
      return {
        id: 'perquisites',
        name: 'Perquisites',
        icon: <CardGiftcardIcon />,
        color: 'error',
        hasData: false,
        totalValue: 0,
        details: {},
        description: 'Accommodation, car, medical, LTA, ESOP, and other benefits'
      };
    }
  }, [employeeId, selectedTaxYear]);

  // 7. loadComponentsData
  const loadComponentsData = useCallback(async (): Promise<void> => {
    try {
      setLoading(true);
      setError(null);
      
      const componentPromises = [
        loadSalaryComponent(),
        loadDeductionsComponent(),
        loadHousePropertyComponent(),
        loadCapitalGainsComponent(),
        loadOtherIncomeComponent(),
        loadPerquisitesComponent()
      ];
      
      const results = await Promise.allSettled(componentPromises);
      const loadedComponents: ComponentSummary[] = [];
      
      results.forEach((result) => {
        if (result.status === 'fulfilled' && result.value) {
          loadedComponents.push(result.value);
        }
      });
      
      setComponents(loadedComponents);
      
    } catch (error: any) {
      setError('Failed to load salary components. Please try again.');
      console.error('Error loading components:', error);
    } finally {
      setLoading(false);
    }
  }, [loadSalaryComponent, loadDeductionsComponent, loadHousePropertyComponent, loadCapitalGainsComponent, loadOtherIncomeComponent, loadPerquisitesComponent]);

  // 8. calculateComputedTax
  const calculateComputedTax = useCallback(async (): Promise<void> => {
    try {
      setTaxLoading(true);
      setTaxError(null);
      
      const salaryComponent = components.find(c => c.id === 'salary');
      
      if (!salaryComponent || !salaryComponent.hasData) {
        setComputedTax(0);
        setTaxLoading(false);
        return;
      }
      
      const monthlyTaxResult = await taxationApi.computeMonthlyTax(employeeId!);
      const monthlyTax = monthlyTaxResult.monthly_tax_liability || 0;
      setComputedTax(monthlyTax);
      
    } catch (error: any) {
      console.error('Error calculating monthly tax:', error);
      setTaxError('Failed to calculate tax. Please try again.');
      setComputedTax(0);
    } finally {
      setTaxLoading(false);
    }
  }, [components, employeeId]);

  // Load deductions data for dialog
  const loadDeductionsDataForDialog = useCallback(async (): Promise<void> => {
    try {
      const response = await taxationApi.getComponent(employeeId!, selectedTaxYear, 'deductions');
      const data = response?.component_data || response;
      
      // Extract deductions data from the response
      const section80c = data.section_80c || {};
      const section80d = data.section_80d || {};
      
      const deductionsData: DeductionsData = {
        life_insurance_premium: section80c.life_insurance_premium || 0,
        epf_contribution: section80c.epf_contribution || 0,
        ppf_contribution: section80c.ppf_contribution || 0,
        nsc_investment: section80c.nsc_investment || 0,
        tax_saving_fd: section80c.tax_saving_fd || 0,
        elss_investment: section80c.elss_investment || 0,
        home_loan_principal: section80c.home_loan_principal || 0,
        tuition_fees: section80c.tuition_fees || 0,
        ulip_premium: section80c.ulip_premium || 0,
        sukanya_samriddhi: section80c.sukanya_samriddhi || 0,
        stamp_duty_property: section80c.stamp_duty_property || 0,
        senior_citizen_savings: section80c.senior_citizen_savings || 0,
        other_80c_investments: section80c.other_80c_investments || 0,
        self_family_premium: section80d.self_family_premium || 0,
        parent_premium: section80d.parent_premium || 0,
        preventive_health_checkup: section80d.preventive_health_checkup || 0,
        education_loan_interest: data.education_loan_interest || 0,
        savings_account_interest: data.savings_account_interest || 0
      };
      
      setDeductionsData(deductionsData);
    } catch (error) {
      console.error('Error loading deductions data:', error);
      setDeductionsData(initialDeductionsData);
    }
  }, [employeeId, selectedTaxYear]);

  // Handle deductions save
  const handleDeductionsSave = async (data: DeductionsData): Promise<void> => {
    try {
      setDeductionsLoading(true);
      
      // Prepare the data in the format expected by the API
      const requestData = {
        employee_id: employeeId!,
        tax_year: selectedTaxYear,
        deductions: {
          section_80c: {
            life_insurance_premium: data.life_insurance_premium,
            epf_contribution: data.epf_contribution,
            ppf_contribution: data.ppf_contribution,
            nsc_investment: data.nsc_investment,
            tax_saving_fd: data.tax_saving_fd,
            elss_investment: data.elss_investment,
            home_loan_principal: data.home_loan_principal,
            tuition_fees: data.tuition_fees,
            ulip_premium: data.ulip_premium,
            sukanya_samriddhi: data.sukanya_samriddhi,
            stamp_duty_property: data.stamp_duty_property,
            senior_citizen_savings: data.senior_citizen_savings,
            other_80c_investments: data.other_80c_investments
          },
          section_80d: {
            self_family_premium: data.self_family_premium,
            parent_premium: data.parent_premium,
            preventive_health_checkup: data.preventive_health_checkup
          },
          education_loan_interest: data.education_loan_interest,
          savings_account_interest: data.savings_account_interest
        },
        notes: 'Updated via My Salary Components page'
      };

      await taxationApi.updateDeductionsComponent(requestData);
      
      showToast('Deductions updated successfully!', 'success');
      setDeductionsDialogOpen(false);
      
      // Refresh the components data to show updated values
      await loadComponentsData();
      
    } catch (error: any) {
      console.error('Error saving deductions:', error);
      showToast('Failed to update deductions. Please try again.', 'error');
    } finally {
      setDeductionsLoading(false);
    }
  };

  // Handle open deductions dialog
  const handleOpenDeductionsDialog = async (): Promise<void> => {
    await loadDeductionsDataForDialog();
    setDeductionsDialogOpen(true);
  };

  // Handle close deductions dialog
  const handleCloseDeductionsDialog = (): void => {
    setDeductionsDialogOpen(false);
  };

  // Load house property data for dialog
  const loadHousePropertyDataForDialog = useCallback(async (): Promise<void> => {
    try {
      const response = await taxationApi.getComponent(employeeId!, selectedTaxYear, 'house_property_income');
      const data = response?.component_data || response;
      
      const housePropertyData: HousePropertyData = {
        property_type: data.property_type || 'Self-Occupied',
        address: data.address || '',
        annual_rent_received: data.annual_rent_received || 0,
        municipal_taxes_paid: data.municipal_taxes_paid || 0,
        home_loan_interest: data.home_loan_interest || 0,
        pre_construction_interest: data.pre_construction_interest || 0
      };
      
      setHousePropertyData(housePropertyData);
    } catch (error) {
      console.error('Error loading house property data:', error);
      setHousePropertyData(initialHousePropertyData);
    }
  }, [employeeId, selectedTaxYear]);

  // Handle house property save
  const handleHousePropertySave = async (data: HousePropertyData): Promise<void> => {
    try {
      setHousePropertyLoading(true);
      
      // Prepare the data in the format expected by the API
      const requestData = {
        employee_id: employeeId!,
        tax_year: selectedTaxYear,
        house_property_income: {
          property_type: data.property_type,
          address: data.address,
          annual_rent_received: data.annual_rent_received,
          municipal_taxes_paid: data.municipal_taxes_paid,
          home_loan_interest: data.home_loan_interest,
          pre_construction_interest: data.pre_construction_interest
        },
        notes: 'Updated via My Salary Components page'
      };

      await taxationApi.updateHousePropertyComponent(requestData);
      
      showToast('House property updated successfully!', 'success');
      setHousePropertyDialogOpen(false);
      
      // Refresh the components data to show updated values
      await loadComponentsData();
      
    } catch (error: any) {
      console.error('Error saving house property:', error);
      showToast('Failed to update house property. Please try again.', 'error');
    } finally {
      setHousePropertyLoading(false);
    }
  };

  // Handle open house property dialog
  const handleOpenHousePropertyDialog = async (): Promise<void> => {
    await loadHousePropertyDataForDialog();
    setHousePropertyDialogOpen(true);
  };

  // Handle close house property dialog
  const handleCloseHousePropertyDialog = (): void => {
    setHousePropertyDialogOpen(false);
  };

  // Load capital gains data for dialog
  const loadCapitalGainsDataForDialog = useCallback(async (): Promise<void> => {
    try {
      const response = await taxationApi.getComponent(employeeId!, selectedTaxYear, 'capital_gains_income');
      const data = response?.component_data || response;
      
      const capitalGainsData: CapitalGainsData = {
        stcg_111a_equity_stt: data.stcg_111a_equity_stt || 0,
        stcg_other_assets: data.stcg_other_assets || 0,
        stcg_debt_mf: data.stcg_debt_mf || 0,
        ltcg_112a_equity_stt: data.ltcg_112a_equity_stt || 0,
        ltcg_other_assets: data.ltcg_other_assets || 0,
        ltcg_debt_mf: data.ltcg_debt_mf || 0
      };
      
      setCapitalGainsData(capitalGainsData);
    } catch (error) {
      console.error('Error loading capital gains data:', error);
      setCapitalGainsData(initialCapitalGainsData);
    }
  }, [employeeId, selectedTaxYear]);

  // Handle capital gains save
  const handleCapitalGainsSave = async (data: CapitalGainsData): Promise<void> => {
    try {
      setCapitalGainsLoading(true);
      
      // Prepare the data in the format expected by the API
      const requestData = {
        employee_id: employeeId!,
        tax_year: selectedTaxYear,
        capital_gains_income: data,
        notes: 'Updated via My Salary Components page'
      };

      await taxationApi.updateCapitalGainsComponent(requestData);
      
      showToast('Capital gains updated successfully!', 'success');
      setCapitalGainsDialogOpen(false);
      
      // Refresh the components data to show updated values
      await loadComponentsData();
      
    } catch (error: any) {
      console.error('Error saving capital gains:', error);
      showToast('Failed to update capital gains. Please try again.', 'error');
    } finally {
      setCapitalGainsLoading(false);
    }
  };

  // Handle open capital gains dialog
  const handleOpenCapitalGainsDialog = async (): Promise<void> => {
    await loadCapitalGainsDataForDialog();
    setCapitalGainsDialogOpen(true);
  };

  // Handle close capital gains dialog
  const handleCloseCapitalGainsDialog = (): void => {
    setCapitalGainsDialogOpen(false);
  };

  // Load other income data for dialog
  const loadOtherIncomeDataForDialog = useCallback(async (): Promise<void> => {
    try {
      const response = await taxationApi.getComponent(employeeId!, selectedTaxYear, 'other_income');
      const data = response?.component_data || response;
      
      const otherIncomeData: OtherIncomeData = {
        interest_income: {
          savings_interest: data.interest_income?.savings_interest || 0,
          fd_interest: data.interest_income?.fd_interest || 0,
          rd_interest: data.interest_income?.rd_interest || 0,
          post_office_interest: data.interest_income?.post_office_interest || 0
        },
        dividend_income: data.dividend_income || 0,
        gifts_received: data.gifts_received || 0,
        business_professional_income: data.business_professional_income || 0,
        other_miscellaneous_income: data.other_miscellaneous_income || 0
      };
      
      setOtherIncomeData(otherIncomeData);
    } catch (error) {
      console.error('Error loading other income data:', error);
      setOtherIncomeData(initialOtherIncomeData);
    }
  }, [employeeId, selectedTaxYear]);

  // Handle other income save
  const handleOtherIncomeSave = async (data: OtherIncomeData): Promise<void> => {
    try {
      setOtherIncomeLoading(true);
      
      // Prepare the data in the format expected by the API
      const requestData = {
        employee_id: employeeId!,
        tax_year: selectedTaxYear,
        other_income: data,
        notes: 'Updated via My Salary Components page'
      };

      await taxationApi.updateOtherIncomeComponent(requestData);
      
      showToast('Other income updated successfully!', 'success');
      setOtherIncomeDialogOpen(false);
      
      // Refresh the components data to show updated values
      await loadComponentsData();
      
    } catch (error: any) {
      console.error('Error saving other income:', error);
      showToast('Failed to update other income. Please try again.', 'error');
    } finally {
      setOtherIncomeLoading(false);
    }
  };

  // Handle open other income dialog
  const handleOpenOtherIncomeDialog = async (): Promise<void> => {
    await loadOtherIncomeDataForDialog();
    setOtherIncomeDialogOpen(true);
  };

  // Handle close other income dialog
  const handleCloseOtherIncomeDialog = (): void => {
    setOtherIncomeDialogOpen(false);
  };

  // Load perquisites data for dialog
  const loadPerquisitesDataForDialog = useCallback(async (): Promise<void> => {
    try {
      const response = await taxationApi.getComponent(employeeId!, selectedTaxYear, 'perquisites');
      const data = response?.component_data || response;
      
      const perquisitesData: PerquisitesData = {
        // Accommodation
        accommodation_type: data.accommodation?.accommodation_type || 'Employer-Owned',
        city_population: data.accommodation?.city_population || 'Below 15 lakhs',
        license_fees: data.accommodation?.license_fees || 0,
        employee_rent_payment: data.accommodation?.employee_rent_payment || 0,
        rent_paid_by_employer: data.accommodation?.rent_paid_by_employer || 0,
        hotel_charges: data.accommodation?.hotel_charges || 0,
        stay_days: data.accommodation?.stay_days || 0,
        furniture_cost: data.accommodation?.furniture_cost || 0,
        furniture_employee_payment: data.accommodation?.furniture_employee_payment || 0,
        is_furniture_owned_by_employer: data.accommodation?.is_furniture_owned_by_employer || false,

        // Car
        car_use_type: data.car?.car_use_type || 'Personal',
        engine_capacity_cc: data.car?.engine_capacity_cc || 1600,
        months_used: data.car?.months_used || 12,
        months_used_other_vehicle: data.car?.months_used_other_vehicle || 12,
        car_cost_to_employer: data.car?.car_cost_to_employer || 0,
        other_vehicle_cost: data.car?.other_vehicle_cost || 0,
        driver_cost: data.car?.driver_cost || 0,
        has_expense_reimbursement: data.car?.has_expense_reimbursement || false,
        driver_provided: data.car?.driver_provided || false,

        // LTA
        lta_allocated_yearly: data.lta?.lta_allocated_yearly || 0,
        lta_amount_claimed: data.lta?.lta_amount_claimed || 0,
        lta_claimed_count: data.lta?.lta_claimed_count || 0,
        public_transport_cost: data.lta?.public_transport_cost || 0,
        travel_mode: data.lta?.travel_mode || 'Air',
        is_monthly_paid: data.lta?.is_monthly_paid || false,

        // ESOP
        esop_exercise_value: data.esop?.exercise_price || 0,
        esop_fair_market_value: data.esop?.allotment_price || 0,
        esop_shares_exercised: data.esop?.shares_exercised || 0,

        // Free Education
        monthly_expenses_child1: data.free_education?.monthly_expenses_child1 || 0,
        monthly_expenses_child2: data.free_education?.monthly_expenses_child2 || 0,
        months_child1: data.free_education?.months_child1 || 12,
        months_child2: data.free_education?.months_child2 || 12,
        employer_maintained_1st_child: data.free_education?.employer_maintained_1st_child || false,
        employer_maintained_2nd_child: data.free_education?.employer_maintained_2nd_child || false,

        // Utilities
        gas_paid_by_employer: data.utilities?.gas_paid_by_employer || 0,
        electricity_paid_by_employer: data.utilities?.electricity_paid_by_employer || 0,
        water_paid_by_employer: data.utilities?.water_paid_by_employer || 0,
        gas_paid_by_employee: data.utilities?.gas_paid_by_employee || 0,
        electricity_paid_by_employee: data.utilities?.electricity_paid_by_employee || 0,
        water_paid_by_employee: data.utilities?.water_paid_by_employee || 0,
        is_gas_manufactured_by_employer: data.utilities?.is_gas_manufactured_by_employer || false,
        is_electricity_manufactured_by_employer: data.utilities?.is_electricity_manufactured_by_employer || false,
        is_water_manufactured_by_employer: data.utilities?.is_water_manufactured_by_employer || false,

        // Interest Free Loan
        loan_amount: data.interest_free_loan?.loan_amount || 0,
        emi_amount: data.interest_free_loan?.emi_amount || 0,
        company_interest_rate: data.interest_free_loan?.company_interest_rate || 0,
        sbi_interest_rate: data.interest_free_loan?.sbi_interest_rate || 6.5,
        loan_type: data.interest_free_loan?.loan_type || 'Personal',
        loan_start_date: data.interest_free_loan?.loan_start_date || '',

        // Movable Asset Usage
        movable_asset_type: data.movable_asset_usage?.movable_asset_type || '',
        movable_asset_usage_value: data.movable_asset_usage?.movable_asset_usage_value || 0,
        movable_asset_hire_cost: data.movable_asset_usage?.movable_asset_hire_cost || 0,
        movable_asset_employee_payment: data.movable_asset_usage?.movable_asset_employee_payment || 0,
        movable_asset_is_employer_owned: data.movable_asset_usage?.movable_asset_is_employer_owned || false,
        
        // Movable Asset Transfer
        movable_asset_transfer_type: data.movable_asset_transfer?.movable_asset_transfer_type || '',
        movable_asset_transfer_cost: data.movable_asset_transfer?.movable_asset_transfer_cost || 0,
        movable_asset_years_of_use: data.movable_asset_transfer?.movable_asset_years_of_use || 0,
        movable_asset_transfer_employee_payment: data.movable_asset_transfer?.movable_asset_transfer_employee_payment || 0,

        // Lunch Refreshment
        lunch_employer_cost: data.lunch_refreshment?.employer_cost || 0,
        lunch_employee_payment: data.lunch_refreshment?.employee_payment || 0,
        lunch_meal_days_per_year: data.lunch_refreshment?.meal_days_per_year || 250,
        
        // Domestic Help
        domestic_help_paid_by_employer: data.domestic_help?.domestic_help_paid_by_employer || 0,
        domestic_help_paid_by_employee: data.domestic_help?.domestic_help_paid_by_employee || 0,
        
        // Other Perquisites
        other_perquisites_amount: data.other_perquisites_amount || 0,
        
        // Monetary Benefits
        monetary_benefit_type: data.monetary_benefits?.monetary_benefit_type || '',
        monetary_benefit_amount: data.monetary_benefits?.monetary_benefit_amount || 0,
        monetary_benefit_employee_payment: data.monetary_benefits?.monetary_benefit_employee_payment || 0,
        
        // Club Expenses
        club_expense_type: data.club_expenses?.club_expense_type || '',
        club_expense_amount: data.club_expenses?.club_expense_amount || 0,
        club_expense_employee_payment: data.club_expenses?.club_expense_employee_payment || 0,
        
        // Other Benefits
        other_benefit_type: data.other_benefits?.other_benefit_type || '',
        other_benefit_amount: data.other_benefits?.other_benefit_amount || 0,
        other_benefit_employee_payment: data.other_benefits?.other_benefit_employee_payment || 0
      };
      
      setPerquisitesData(perquisitesData);
    } catch (error) {
      console.error('Error loading perquisites data:', error);
      setPerquisitesData(initialPerquisitesData);
    }
  }, [employeeId, selectedTaxYear]);

  // Handle perquisites save
  const handlePerquisitesSave = async (data: PerquisitesData): Promise<void> => {
    try {
      setPerquisitesLoading(true);
      
      // Prepare the data in the format expected by the API
      const requestData = {
        employee_id: employeeId!,
        tax_year: selectedTaxYear,
        perquisites: data,
        notes: 'Updated via My Salary Components page'
      };

      await taxationApi.updatePerquisitesComponent(requestData);
      
      showToast('Perquisites updated successfully!', 'success');
      setPerquisitesDialogOpen(false);
      
      // Refresh the components data to show updated values
      await loadComponentsData();
      
    } catch (error: any) {
      console.error('Error saving perquisites:', error);
      showToast('Failed to update perquisites. Please try again.', 'error');
    } finally {
      setPerquisitesLoading(false);
    }
  };

  // Handle open perquisites dialog
  const handleOpenPerquisitesDialog = async (): Promise<void> => {
    await loadPerquisitesDataForDialog();
    setPerquisitesDialogOpen(true);
  };

  // Handle close perquisites dialog
  const handleClosePerquisitesDialog = (): void => {
    setPerquisitesDialogOpen(false);
  };

  useEffect(() => {
    if (employeeId) {
      loadComponentsData();
    }
  }, [employeeId, selectedTaxYear, loadComponentsData]);

  // Calculate tax whenever components change
  useEffect(() => {
    if (components.length > 0 && employeeId) {
      calculateComputedTax();
    }
  }, [components, employeeId, calculateComputedTax]);

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  const handleTaxYearChange = (event: SelectChangeEvent<string>): void => {
    const newTaxYear = event.target.value;
    setSelectedTaxYear(newTaxYear);
  };

  const handleRefresh = async (): Promise<void> => {
    try {
      await loadComponentsData();
      showToast('Salary components refreshed successfully', 'success');
    } catch (error) {
      console.error('Error refreshing components:', error);
      showToast('Failed to refresh salary components', 'error');
    }
  };

  const handleExportSalaryPackage = async () => {
    if (!employeeId) return;
    
    setExportLoading(true);
    try {
      const blob = await taxationApi.exportSalaryPackageToExcel(employeeId, selectedTaxYear);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `my_salary_package_${selectedTaxYear}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      showToast('Salary package exported successfully!', 'success');
    } catch (error) {
      console.error('Error exporting salary package:', error);
      showToast('Failed to export salary package', 'error');
    } finally {
      setExportLoading(false);
    }
  };

  const showToast = (message: string, severity: ToastState['severity'] = 'success'): void => {
    setToast({ show: true, message, severity });
  };

  const closeToast = (): void => {
    setToast(prev => ({ ...prev, show: false }));
  };

  const formatValue = (key: string, value: any): React.ReactElement | string => {
    if (value === null || value === undefined) {
      return 'N/A';
    }
    
    if (typeof value === 'number') {
      const countFields = [
        'count', 'quantity', 'number', 'total_records', 'records_count', 
        'children_count', 'hostel_count', 'months', 'days', 'years',
        'percentage', 'rate', 'age', 'experience', 'tenure'
      ];
      
      const isCountField = countFields.some(countField => 
        key.toLowerCase().includes(countField) || 
        key.toLowerCase().endsWith('_count') ||
        key.toLowerCase().endsWith('_number') ||
        key.toLowerCase().includes('count_') ||
        (key.toLowerCase().includes('total_') && !key.toLowerCase().includes('amount') && !key.toLowerCase().includes('salary') && !key.toLowerCase().includes('income'))
      );
      
      if (isCountField) {
        return value.toString();
      }
      
      return formatCurrency(value);
    }
    
    if (typeof value === 'boolean') {
      return value ? 'Yes' : 'No';
    }
    
    if (Array.isArray(value)) {
      if (value.length === 0) {
        return 'No records';
      }
      
      return (
        <Box>
          {value.map((item, index) => (
            <Box key={index} sx={{ mb: 1, p: 1, bgcolor: 'grey.50', borderRadius: 1 }}>
              {typeof item === 'object' ? (
                <Box>
                  {Object.entries(item).map(([k, v]) => (
                    <Typography key={k} variant="caption" display="block">
                      <strong>{k.replace(/_/g, ' ')}:</strong> {
                        formatValue(k, v)
                      }
                    </Typography>
                  ))}
                </Box>
              ) : (
                <Typography variant="body2">{String(item)}</Typography>
              )}
            </Box>
          ))}
        </Box>
      );
    }
    
    if (typeof value === 'object') {
      return (
        <Box>
          {Object.entries(value).map(([k, v]) => (
            <Typography key={k} variant="caption" display="block">
              <strong>{k.replace(/_/g, ' ')}:</strong> {
                formatValue(k, v)
              }
            </Typography>
          ))}
        </Box>
      );
    }
    
    return String(value);
  };

  const renderComponentCard = (component: ComponentSummary): React.ReactElement => (
    <Grid item xs={12} sm={6} md={4} key={component.id}>
      <Card 
        variant="outlined"
        sx={{ 
          height: '100%',
          borderColor: component.hasData ? `${component.color}.main` : 'grey.300',
          transition: 'all 0.3s ease',
          '&:hover': {
            boxShadow: component.hasData ? 3 : 1,
            transform: component.hasData ? 'translateY(-2px)' : 'none'
          }
        }}
      >
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Box sx={{ color: `${component.color}.main` }}>
              {component.icon}
            </Box>
            <Typography variant="h6" sx={{ flexGrow: 1 }}>
              {component.name}
            </Typography>
            {component.hasData ? (
              <CheckCircleIcon color="success" fontSize="small" />
            ) : (
              <InfoIcon color="action" fontSize="small" />
            )}
            {/* Add edit button for deductions */}
            {component.id === 'deductions' && (
              <Tooltip title="Edit Deductions">
                <IconButton
                  size="small"
                  color="primary"
                  onClick={handleOpenDeductionsDialog}
                  sx={{ ml: 1 }}
                >
                  <EditIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
            {/* Add edit button for house property */}
            {component.id === 'house_property_income' && (
              <Tooltip title="Edit House Property">
                <IconButton
                  size="small"
                  color="primary"
                  onClick={handleOpenHousePropertyDialog}
                  sx={{ ml: 1 }}
                >
                  <EditIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
            {/* Add edit button for capital gains */}
            {component.id === 'capital_gains' && (
              <Tooltip title="Edit Capital Gains">
                <IconButton
                  size="small"
                  color="primary"
                  onClick={handleOpenCapitalGainsDialog}
                  sx={{ ml: 1 }}
                >
                  <EditIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
            {/* Add edit button for other income */}
            {component.id === 'other_income' && (
              <Tooltip title="Edit Other Income">
                <IconButton
                  size="small"
                  color="primary"
                  onClick={handleOpenOtherIncomeDialog}
                  sx={{ ml: 1 }}
                >
                  <EditIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
            {/* Add edit button for perquisites */}
            {component.id === 'perquisites' && (
              <Tooltip title="Edit Perquisites">
                <IconButton
                  size="small"
                  color="primary"
                  onClick={handleOpenPerquisitesDialog}
                  sx={{ ml: 1 }}
                >
                  <EditIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
          </Box>
          
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {component.description}
          </Typography>
          
          <Box sx={{ textAlign: 'center', py: 2 }}>
            <Typography variant="h4" color={component.hasData ? `${component.color}.main` : 'text.secondary'}>
              {formatCurrency(component.totalValue)}
            </Typography>
            <Chip
              label={component.hasData ? 'Data Available' : 'No Data'}
              color={component.hasData ? 'success' : 'default'}
              size="small"
              variant="outlined"
              sx={{ mt: 1 }}
            />
          </Box>
        </CardContent>
      </Card>
    </Grid>
  );

  const renderComponentDetails = (component: ComponentSummary): React.ReactElement => (
    <Accordion key={component.id}>
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
          <Box sx={{ color: `${component.color}.main` }}>
            {component.icon}
          </Box>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            {component.name}
          </Typography>
          <Typography variant="h6" color={`${component.color}.main`}>
            {formatCurrency(component.totalValue)}
          </Typography>
        </Box>
      </AccordionSummary>
      <AccordionDetails>
        {component.hasData ? (
          <TableContainer>
            <Table size="small">
              <TableBody>
                {Object.entries(component.details).map(([key, value]) => (
                  <TableRow key={key}>
                    <TableCell sx={{ fontWeight: 'medium', verticalAlign: 'top' }}>
                      {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </TableCell>
                    <TableCell align="right" sx={{ verticalAlign: 'top' }}>
                      {formatValue(key, value)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        ) : (
          <Box sx={{ textAlign: 'center', py: 3 }}>
            <InfoIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
            <Typography variant="body1" color="text.secondary">
              No data available for {component.name} in {selectedTaxYear}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Contact HR or your manager to update this information.
            </Typography>
          </Box>
        )}
      </AccordionDetails>
    </Accordion>
  );

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '70vh' }}>
        <CircularProgress size={40} />
      </Box>
    );
  }

  const totalValue = components.reduce((sum, comp) => sum + comp.totalValue, 0);
  const componentsWithData = components.filter(comp => comp.hasData).length;

  return (
    <Box>
      {/* Header */}
      <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              My Salary Components
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Employee ID: {employeeId} | Tax Year: {selectedTaxYear}
              {!isCurrentYear && (
                <Chip 
                  label="Previous Year" 
                  color="warning" 
                  size="small" 
                  sx={{ ml: 1 }} 
                />
              )}
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            <FormControl size="small" sx={{ minWidth: 140 }}>
              <InputLabel>Tax Year</InputLabel>
              <Select
                value={selectedTaxYear}
                label="Tax Year"
                onChange={handleTaxYearChange}
              >
                {availableTaxYears.map((year) => (
                  <MenuItem key={year} value={year}>
                    {year}
                    {year === getCurrentTaxYear() && ' (Current)'}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <Tooltip title="Refresh">
              <IconButton 
                onClick={handleRefresh}
                disabled={loading}
                color="primary"
              >
                <RefreshIcon />
              </IconButton>
            </Tooltip>
            <Button 
              variant="outlined" 
              startIcon={<FileDownloadIcon />}
              onClick={handleExportSalaryPackage}
              disabled={exportLoading}
            >
              {exportLoading ? 'Exporting...' : 'Export Excel'}
            </Button>
          </Box>
        </Box>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h6" color="text.secondary">
                Total Value
              </Typography>
              <Typography variant="h4" color="primary">
                {formatCurrency(totalValue)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h6" color="text.secondary">
                Components with Data
              </Typography>
              <Typography variant="h4" color="success.main">
                {componentsWithData} / {components.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h6" color="text.secondary">
                Monthly Tax
              </Typography>
              {taxLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 60 }}>
                  <CircularProgress size={30} />
                </Box>
              ) : taxError ? (
                <Tooltip title={taxError}>
                  <Typography variant="h4" color="error">
                    Error
                  </Typography>
                </Tooltip>
              ) : (
                <Typography variant="h4" color="warning.main">
                  {formatCurrency(computedTax)}
                </Typography>
              )}
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                Estimated monthly tax liability
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h6" color="text.secondary">
                Tax Year Status
              </Typography>
              <Chip
                label={isCurrentYear ? 'Current Year' : 'Previous Year'}
                color={isCurrentYear ? 'success' : 'warning'}
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Component Cards */}
      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        Salary Component Summary
      </Typography>
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {components.map(renderComponentCard)}
      </Grid>

      {/* Detailed View */}
      <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
        Detailed Component Values
      </Typography>
      <Box>
        {components.map(renderComponentDetails)}
      </Box>

      {/* Success/Error Messages */}
      <Snackbar
        open={toast.show}
        autoHideDuration={6000}
        onClose={closeToast}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={closeToast} 
          severity={toast.severity}
          sx={{ width: '100%' }}
        >
          {toast.message}
        </Alert>
      </Snackbar>

      {/* Deductions Update Dialog */}
      <DeductionsDialog
        open={deductionsDialogOpen}
        onClose={handleCloseDeductionsDialog}
        onSave={handleDeductionsSave}
        initialData={deductionsData}
        loading={deductionsLoading}
      />

      {/* House Property Update Dialog */}
      <HousePropertyDialog
        open={housePropertyDialogOpen}
        onClose={handleCloseHousePropertyDialog}
        onSave={handleHousePropertySave}
        initialData={housePropertyData}
        loading={housePropertyLoading}
      />

      {/* Capital Gains Update Dialog */}
      <CapitalGainsDialog
        open={capitalGainsDialogOpen}
        onClose={handleCloseCapitalGainsDialog}
        onSave={handleCapitalGainsSave}
        initialData={capitalGainsData}
        loading={capitalGainsLoading}
      />

      {/* Other Income Update Dialog */}
      <OtherIncomeDialog
        open={otherIncomeDialogOpen}
        onClose={handleCloseOtherIncomeDialog}
        onSave={handleOtherIncomeSave}
        initialData={otherIncomeData}
        loading={otherIncomeLoading}
      />

      {/* Perquisites Update Dialog */}
      <PerquisitesDialog
        open={perquisitesDialogOpen}
        onClose={handleClosePerquisitesDialog}
        onSave={handlePerquisitesSave}
        initialData={perquisitesData}
        loading={perquisitesLoading}
      />
    </Box>
  );
};

export default MySalaryComponents; 