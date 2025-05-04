import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Grid,
  TextField,
  FormControl,
  FormControlLabel,
  RadioGroup,
  Radio,
  Divider,
  Stepper,
  Step,
  StepLabel,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  FormHelperText,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Select,
  MenuItem,
  InputLabel,
  Switch
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { useNavigate, useParams } from 'react-router-dom';
import { getTaxationByEmpId, saveTaxationData, calculateTax } from '../../services/taxationService';
import { getUserId } from '../../utils/auth';
import PageLayout from '../../layout/PageLayout';


const TaxDeclaration = () => {
  const { empId: paramEmpId } = useParams();
  const navigate = useNavigate();
  const currentUserId = getUserId();
  const empId = paramEmpId || currentUserId;

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [activeStep, setActiveStep] = useState(0);
  const [cityForHRA, setCityForHRA] = useState('Others');
  const [autoComputeHRA, setAutoComputeHRA] = useState(true);
  
  // Get current financial year in format YYYY-YYYY
  const getCurrentFinancialYear = () => {
    const today = new Date();
    const currentMonth = today.getMonth();
    const currentYear = today.getFullYear();
    
    // In India, financial year starts from April (month index 3)
    // If current month is January to March, FY is previous year to current year
    // If current month is April to December, FY is current year to next year
    if (currentMonth < 3) { // January to March
      return `${currentYear-1}-${currentYear}`;
    } else { // April to December
      return `${currentYear}-${currentYear+1}`;
    }
  };
  
  const [taxationData, setTaxationData] = useState({
    emp_id: empId,
    emp_age: 0,
    regime: 'old',
    tax_year: getCurrentFinancialYear(),
    is_govt_employee: false,
    salary: {
      basic: 0,
      dearness_allowance: 0,
      hra: 0,
      special_allowance: 0,
      bonus: 0,
      perquisites: {
        // Legacy perquisites
        company_car: 0,
        rent_free_accommodation: 0,
        concessional_loan: 0,
        gift_vouchers: 0,
        
        // Accommodation perquisites
        accommodation_provided: 'Employer-Owned', 
        accommodation_govt_lic_fees: 0,
        accommodation_city_population: 'Exceeding 40 lakhs in 2011 Census',
        accommodation_rent: 0,
        is_furniture_owned: false,
        furniture_actual_cost: 0,
        furniture_cost_to_employer: 0,
        furniture_cost_paid_by_employee: 0,
        
        // Car perquisites
        is_car_rating_higher: false,
        is_car_employer_owned: false,
        is_expenses_reimbursed: false, 
        is_driver_provided: false,
        car_use: 'Personal',
        car_cost_to_employer: 0,
        month_counts: 0,
        other_vehicle_cost: 0,
        other_vehicle_months: 0,
        
        // Medical Reimbursement
        is_treated_in_India: false,
        medical_reimbursement_by_employer: 0,
        
        // Leave Travel Allowance
        lta_amount_claimed: 0,
        lta_claimed_count: 0,
        travel_through: 'Air',
        public_transport_travel_amount_for_same_distance: 0,
        lta_claim_start_date: '',
        lta_claim_end_date: '',
        
        // Free Education
        free_education_actual_expenses: 0,
        free_education_is_institute_by_employer: false,
        free_education_similar_institute_cost: 0,
        
        // Gas, Electricity, Water
        gas_amount_paid_by_employer: 0,
        electricity_amount_paid_by_employer: 0,
        water_amount_paid_by_employer: 0,
        gas_amount_paid_by_employee: 0,
        electricity_amount_paid_by_employee: 0,
        water_amount_paid_by_employee: 0,
        
        // Domestic help
        domestic_help_amount_paid_by_employer: 0,
        domestic_help_amount_paid_by_employee: 0,
        
        // Interest-free/concessional loan
        loan_type: '',
        loan_amount: 0,
        loan_interest_rate_company: 0,
        loan_interest_rate_sbi: 0,
        monthly_interest_amount_sbi: 0,
        monthly_interest_amount_company: 0,
        
        // Lunch/Refreshment
        lunch_amount_paid_by_employer: 0,
        lunch_amount_paid_by_employee: 0
      }
    },
    other_sources: {
      interest_savings: 0,
      interest_fd: 0,
      interest_rd: 0,
      dividend_income: 0,
      gifts: 0,
      other_interest: 0,
      other_income: 0
    },
    capital_gains: {
      stcg_111a: 0,
      stcg_any_other_asset: 0,
      stcg_debt_mutual_fund: 0,
      ltcg_112a: 0,
      ltcg_any_other_asset: 0,
      ltcg_debt_mutual_fund: 0
    },
    deductions: {
      section_80c_lic: 0,
      section_80c_epf: 0,
      section_80c_ssp: 0,
      section_80c_nsc: 0,
      section_80c_ulip: 0,
      section_80c_tsmf: 0,
      section_80c_tffte2c: 0,
      section_80c_paphl: 0,
      section_80c_sdpphp: 0,
      section_80c_tsfdsb: 0,
      section_80c_scss: 0,
      section_80c_others: 0,
      section_80ccc_ppic: 0,
      section_80ccd_1_nps: 0,
      section_80ccd_1b_additional: 0,
      section_80ccd_2_enps: 0,
      section_80d_hisf: 0,
      section_80d_phcs: 0,
      section_80d_hi_parent: 0,
      section_80dd: 0,
      relation_80dd: '',
      disability_percentage: '',
      section_80ddb: 0,
      relation_80ddb: '',
      age_80ddb: 0,
      section_80eeb: 0,
      ev_purchase_date: null,
      section_80g: 0,
      section_80g_100_wo_ql: 0,
      section_80g_100_head: '',
      section_80g_50_wo_ql: 0,
      section_80g_50_head: '',
      section_80g_100_ql: 0,
      section_80g_100_ql_head: '',
      section_80g_50_ql: 0,
      section_80g_50_ql_head: '',
      section_80ggc: 0,
      section_80u: 0,
      disability_percentage_80u: ''
    }
  });
  const [calculatedTax, setCalculatedTax] = useState(null);

  // Steps for the stepper
  const steps = ['Salary Income', 'Other Income', 'Deductions', 'Review & Submit'];

  // List of cities for HRA computation
  const cities = [
    { value: 'Delhi', label: 'Delhi', rate: 0.5 },
    { value: 'Mumbai', label: 'Mumbai', rate: 0.5 },
    { value: 'Kolkata', label: 'Kolkata', rate: 0.5 },
    { value: 'Chennai', label: 'Chennai', rate: 0.5 },
    { value: 'Others', label: 'Others', rate: 0.4 }
  ];

  useEffect(() => {
    fetchTaxationData();
  }, [empId]);

  const fetchTaxationData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      try {
        const response = await getTaxationByEmpId(empId);
        setTaxationData({
          ...taxationData,
          ...response,
          emp_id: empId
        });
      } catch (err) {
        // If no existing data, continue with default values
        console.log('No existing taxation data, using defaults');
      }
    } catch (err) {
      console.error('Error fetching taxation data:', err);
      setError('Failed to load taxation data. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  // Format number with Indian system commas (1,23,456)
  const formatIndianNumber = (num) => {
    if (num === null || num === undefined || num === '') return '';
    
    const numStr = num.toString();
    let result = '';
    
    // Handle decimal part if it exists
    const parts = numStr.split('.');
    const integerPart = parts[0];
    const decimalPart = parts.length > 1 ? '.' + parts[1] : '';
    
    // Format the integer part with commas
    let lastThree = integerPart.length > 3 ? integerPart.substring(integerPart.length - 3) : integerPart;
    let remaining = integerPart.length > 3 ? integerPart.substring(0, integerPart.length - 3) : '';
    
    if (remaining !== '') {
      // Place commas after every 2 digits from right to left
      const regex = /\d{1,2}(?=(\d{2})+$)/g;
      result = remaining.replace(regex, '$&,') + ',' + lastThree;
    } else {
      result = lastThree;
    }
    
    return result + decimalPart;
  };
  
  // Parse comma-separated Indian number format back to numeric value
  const parseIndianNumber = (str) => {
    if (!str) return 0;
    return parseFloat(str.replace(/,/g, ''));
  };

  // Modified version of handleInputChange to work with formatted numbers
  const handleInputChange = (section, field, value) => {
    // Parse the value to remove commas if it's a string with commas
    let parsedValue = typeof value === 'string' ? parseIndianNumber(value) : value;
    parsedValue = parseFloat(parsedValue) || 0;
    
    setTaxationData((prevData) => ({
      ...prevData,
      [section]: {
        ...prevData[section],
        [field]: parsedValue
      }
    }));
  };

  // Modified version of handleNestedInputChange to work with formatted numbers
  const handleNestedInputChange = (section, nestedSection, field, value) => {
    // Parse the value to remove commas if it's a string with commas
    let parsedValue = typeof value === 'string' ? parseIndianNumber(value) : value;
    parsedValue = parseFloat(parsedValue) || 0;
    
    setTaxationData((prevData) => ({
      ...prevData,
      [section]: {
        ...prevData[section],
        [nestedSection]: {
          ...prevData[section][nestedSection],
          [field]: parsedValue
        }
      }
    }));
  };

  const handleRegimeChange = (event) => {
    setTaxationData((prevData) => ({
      ...prevData,
      regime: event.target.value
    }));
  };

  const handleCalculateTax = async () => {
    try {
      setSubmitting(true);
      setError(null);
      
      // First save the taxation data
      await saveTaxationData(taxationData);
      
      // Then calculate the tax
      const result = await calculateTax(empId, taxationData.tax_year, taxationData.regime);
      setCalculatedTax(result.total_tax);
      
      setSuccess('Tax calculated successfully!');
    } catch (err) {
      console.error('Error calculating tax:', err);
      setError('Failed to calculate tax. Please try again later.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSubmit = async () => {
    try {
      setSubmitting(true);
      setError(null);
      
      const dataToSubmit = {
        ...taxationData,
        filing_status: 'filed'
      };
      
      // Save the data with filed status
      await saveTaxationData(dataToSubmit);
      
      setSuccess('Tax declaration submitted successfully!');
      
      // Redirect after a short delay
      setTimeout(() => {
        navigate('/taxation');
      }, 2000);
    } catch (err) {
      console.error('Error submitting tax declaration:', err);
      setError('Failed to submit tax declaration. Please try again later.');
    } finally {
      setSubmitting(false);
    }
  };

  // Format currency
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  // Compute HRA based on city and salary components
  const computeHRA = () => {
    const basic = taxationData.salary.basic || 0;
    const da = taxationData.salary.dearness_allowance || 0;
    const baseAmount = basic + da;
    
    const selectedCity = cities.find(city => city.value === cityForHRA);
    const rate = selectedCity ? selectedCity.rate : 0.4;
    
    return Math.round(baseAmount * rate);
  };

  // Update HRA when basic salary, DA, or city changes
  useEffect(() => {
    if (autoComputeHRA) {
      const calculatedHRA = computeHRA();
      handleInputChange('salary', 'hra', calculatedHRA);
    }
  }, [taxationData.salary.basic, taxationData.salary.dearness_allowance, cityForHRA]);

  // Automatically update Section 80TTA based on savings account interest
  useEffect(() => {
    // Section 80TTA has a max limit of 10,000
    const savingsInterest = taxationData.other_sources?.interest_savings || 0;
    const section80TTAValue = Math.min(savingsInterest, 10000);
    
    // Only update if in old regime since deductions aren't allowed in new regime
    if (taxationData.regime === 'old') {
      handleInputChange('deductions', 'section_80tta', section80TTAValue);
    }
  }, [taxationData.other_sources?.interest_savings, taxationData.regime]);

  // Handle city change
  const handleCityChange = (event) => {
    setCityForHRA(event.target.value);
  };

  // Handle HRA manual edit
  const handleHRAChange = (e) => {
    setAutoComputeHRA(false);
    handleInputChange('salary', 'hra', e.target.value);
  };

  // Handle clearing zero values on focus
  const handleFocus = (section, field, value) => {
    if (value === 0) {
      setTaxationData((prevData) => ({
        ...prevData,
        [section]: {
          ...prevData[section],
          [field]: ''
        }
      }));
    }
  };

  // Handle clearing zero values in nested fields on focus
  const handleNestedFocus = (section, nestedSection, field, value) => {
    if (value === 0) {
      setTaxationData((prevData) => ({
        ...prevData,
        [section]: {
          ...prevData[section],
          [nestedSection]: {
            ...prevData[section][nestedSection],
            [field]: ''
          }
        }
      }));
    }
  };

  if (loading) {
    return (
      <PageLayout title="Tax Declaration">
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '70vh' }}>
          <CircularProgress />
        </Box>
      </PageLayout>
    );
  }

  return (
    <PageLayout title="Tax Declaration">
      <Box sx={{ p: 3 }}>
        <Paper elevation={3} sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h4" component="h1">
              {paramEmpId ? `Tax Declaration for ${paramEmpId}` : 'My Tax Declaration'}
            </Typography>
            <Button 
              variant="outlined" 
              color="primary" 
              onClick={() => navigate('/taxation')}
            >
              Back to Dashboard
            </Button>
          </Box>

          <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

          <Box sx={{ mt: 4 }}>
            {/* Tax Regime Selection */}
            <Box sx={{ mb: 4 }}>
              <Typography variant="h6" gutterBottom>Tax Regime</Typography>
              <FormControl component="fieldset">
                <RadioGroup
                  row
                  name="regime"
                  value={taxationData.regime}
                  onChange={handleRegimeChange}
                >
                  <FormControlLabel value="old" control={<Radio />} label="Old Regime (with deductions)" />
                  <FormControlLabel value="new" control={<Radio />} label="New Regime (lower rates)" />
                </RadioGroup>
                <FormHelperText>
                  {taxationData.regime === 'new' 
                    ? 'New regime has lower tax rates but no tax deductions allowed.'
                    : 'Old regime allows tax deductions but has higher tax rates.'}
                </FormHelperText>
              </FormControl>
            </Box>

            {/* Step 1: Salary Income */}
            {activeStep === 0 && (
              <Grid container spacing={3}>
                <Grid item xs={12}>
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="h6" gutterBottom>Salary Components</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Grid container spacing={3}>
                      <Grid item xs={12} md={6}>
                        <TextField
                          fullWidth
                          label="Basic Salary"
                          type="text"
                          value={formatIndianNumber(taxationData.salary.basic)}
                          onChange={(e) => handleInputChange('salary', 'basic', e.target.value)}
                          InputProps={{ startAdornment: '₹' }}
                          onFocus={(e) => handleFocus('salary', 'basic', e.target.value)}
                        />
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <TextField
                          fullWidth
                          label="Dearness Allowance (DA)"
                          type="text"
                          value={formatIndianNumber(taxationData.salary.dearness_allowance)}
                          onChange={(e) => handleInputChange('salary', 'dearness_allowance', e.target.value)}
                          InputProps={{ startAdornment: '₹' }}
                          onFocus={(e) => handleFocus('salary', 'dearness_allowance', e.target.value)}
                        />
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <FormControl fullWidth>
                          <InputLabel id="city-select-label">City (for HRA Computation)</InputLabel>
                          <Select
                            labelId="city-select-label"
                            id="city-select"
                            value={cityForHRA}
                            label="City (for HRA Computation)"
                            onChange={handleCityChange}
                          >
                            {cities.map((city) => (
                              <MenuItem key={city.value} value={city.value}>
                                {city.label} ({(city.rate * 100)}% of Basic+DA)
                              </MenuItem>
                            ))}
                          </Select>
                          <FormHelperText>
                            Metro cities: 50% of Basic+DA, Others: 40%
                          </FormHelperText>
                        </FormControl>
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <TextField
                          fullWidth
                          label="HRA"
                          type="text"
                          value={formatIndianNumber(taxationData.salary.hra)}
                          onChange={handleHRAChange}
                          InputProps={{ 
                            startAdornment: '₹',
                          }}
                          helperText={autoComputeHRA ? "Auto-computed based on city and Basic+DA" : "Manually edited"}
                          onFocus={(e) => handleFocus('salary', 'hra', e.target.value)}
                        />
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <TextField
                          fullWidth
                          label="Special Allowance"
                          type="text"
                          value={formatIndianNumber(taxationData.salary.special_allowance)}
                          onChange={(e) => handleInputChange('salary', 'special_allowance', e.target.value)}
                          InputProps={{ startAdornment: '₹' }}
                          onFocus={(e) => handleFocus('salary', 'special_allowance', e.target.value)}
                        />
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <TextField
                          fullWidth
                          label="Bonus"
                          type="text"
                          value={formatIndianNumber(taxationData.salary.bonus)}
                          onChange={(e) => handleInputChange('salary', 'bonus', e.target.value)}
                          InputProps={{ startAdornment: '₹' }}
                          onFocus={(e) => handleFocus('salary', 'bonus', e.target.value)}
                        />
                      </Grid>
                    </Grid>
                  </AccordionDetails>
                </Accordion>
                </Grid>

                <Grid item xs={12}>
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography>Perquisites & Benefits</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      {/* Legacy Perquisites - For Backward Compatibility */}
                      <Box sx={{ mb: 4 }}>
                        <Typography variant="subtitle1" gutterBottom>Legacy Perquisites</Typography>
                        <Grid container spacing={3}>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Company Car"
                              type="text"
                              value={formatIndianNumber(taxationData.salary.perquisites.company_car)}
                              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'company_car', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'company_car', e.target.value)}
                            />
                          </Grid>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Rent Free Accommodation"
                              type="text"
                              value={formatIndianNumber(taxationData.salary.perquisites.rent_free_accommodation)}
                              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'rent_free_accommodation', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'rent_free_accommodation', e.target.value)}
                            />
                          </Grid>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Concessional Loan"
                              type="text"
                              value={formatIndianNumber(taxationData.salary.perquisites.concessional_loan)}
                              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'concessional_loan', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'concessional_loan', e.target.value)}
                            />
                          </Grid>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Gift Vouchers"
                              type="text"
                              value={formatIndianNumber(taxationData.salary.perquisites.gift_vouchers)}
                              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'gift_vouchers', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'gift_vouchers', e.target.value)}
                            />
                          </Grid>
                        </Grid>
                      </Box>
                      
                      {/* Accommodation Perquisites */}
                      <Box sx={{ mb: 4 }}>
                        <Typography variant="subtitle1" gutterBottom>Accommodation Perquisites</Typography>
                        <Grid container spacing={3}>
                          <Grid item xs={12} md={6}>
                            <FormControl fullWidth>
                              <InputLabel>Accommodation Type</InputLabel>
                              <Select
                                value={taxationData.salary.perquisites.accommodation_provided}
                                onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'accommodation_provided', e.target.value)}
                                label="Accommodation Type"
                              >
                                <MenuItem value="Employer-Owned">Employer-Owned</MenuItem>
                                <MenuItem value="Govt">Government</MenuItem>
                                <MenuItem value="Employer-Leased">Employer-Leased</MenuItem>
                                <MenuItem value="Hotel provided for 15 days or above">Hotel (15+ days)</MenuItem>
                              </Select>
                            </FormControl>
                          </Grid>
                          
                          <Grid item xs={12} md={6}>
                            <FormControl fullWidth>
                              <InputLabel>City Population</InputLabel>
                              <Select
                                value={taxationData.salary.perquisites.accommodation_city_population}
                                onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'accommodation_city_population', e.target.value)}
                                label="City Population"
                                disabled={taxationData.salary.perquisites.accommodation_provided !== 'Employer-Owned'}
                              >
                                <MenuItem value="Exceeding 40 lakhs in 2011 Census">Exceeding 40 lakhs</MenuItem>
                                <MenuItem value="Between 15 lakhs and 40 lakhs in 2011 Census">Between 15-40 lakhs</MenuItem>
                                <MenuItem value="Below 15 lakhs in 2011 Census">Below 15 lakhs</MenuItem>
                              </Select>
                            </FormControl>
                          </Grid>
                          
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Accommodation Rent"
                              type="text"
                              value={formatIndianNumber(taxationData.salary.perquisites.accommodation_rent)}
                              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'accommodation_rent', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'accommodation_rent', e.target.value)}
                            />
                          </Grid>
                          
                          {taxationData.salary.perquisites.accommodation_provided === 'Govt' && (
                            <Grid item xs={12} md={6}>
                              <TextField
                                fullWidth
                                label="Government License Fees"
                                type="text"
                                value={formatIndianNumber(taxationData.salary.perquisites.accommodation_govt_lic_fees)}
                                onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'accommodation_govt_lic_fees', e.target.value)}
                                InputProps={{ startAdornment: '₹' }}
                                onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'accommodation_govt_lic_fees', e.target.value)}
                              />
                            </Grid>
                          )}
                          
                          <Grid item xs={12}>
                            <FormControlLabel
                              control={
                                <Switch
                                  checked={taxationData.salary.perquisites.is_furniture_owned}
                                  onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'is_furniture_owned', e.target.checked)}
                                  color="primary"
                                />
                              }
                              label="Furniture Owned by Employer"
                            />
                          </Grid>
                          
                          {taxationData.salary.perquisites.is_furniture_owned && (
                            <>
                              <Grid item xs={12} md={6}>
                                <TextField
                                  fullWidth
                                  label="Furniture Actual Cost"
                                  type="text"
                                  value={formatIndianNumber(taxationData.salary.perquisites.furniture_actual_cost)}
                                  onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'furniture_actual_cost', e.target.value)}
                                  InputProps={{ startAdornment: '₹' }}
                                  onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'furniture_actual_cost', e.target.value)}
                                />
                              </Grid>
                              <Grid item xs={12} md={6}>
                                <TextField
                                  fullWidth
                                  label="Furniture Cost to Employer"
                                  type="text"
                                  value={formatIndianNumber(taxationData.salary.perquisites.furniture_cost_to_employer)}
                                  onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'furniture_cost_to_employer', e.target.value)}
                                  InputProps={{ startAdornment: '₹' }}
                                  onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'furniture_cost_to_employer', e.target.value)}
                                />
                              </Grid>
                              <Grid item xs={12} md={6}>
                                <TextField
                                  fullWidth
                                  label="Furniture Cost Paid by Employee"
                                  type="text"
                                  value={formatIndianNumber(taxationData.salary.perquisites.furniture_cost_paid_by_employee)}
                                  onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'furniture_cost_paid_by_employee', e.target.value)}
                                  InputProps={{ startAdornment: '₹' }}
                                  onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'furniture_cost_paid_by_employee', e.target.value)}
                                />
                              </Grid>
                            </>
                          )}
                        </Grid>
                      </Box>
                      
                      {/* Car Perquisites */}
                      <Box>
                        <Typography variant="subtitle1" gutterBottom>Car Perquisites</Typography>
                        <Grid container spacing={3}>
                          <Grid item xs={12} md={6}>
                            <FormControlLabel
                              control={
                                <Switch
                                  checked={taxationData.salary.perquisites.is_car_employer_owned}
                                  onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'is_car_employer_owned', e.target.checked)}
                                  color="primary"
                                />
                              }
                              label="Car Owned by Employer"
                            />
                          </Grid>
                          
                          <Grid item xs={12} md={6}>
                            <FormControlLabel
                              control={
                                <Switch
                                  checked={taxationData.salary.perquisites.is_car_rating_higher}
                                  onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'is_car_rating_higher', e.target.checked)}
                                  color="primary"
                                />
                              }
                              label="Engine Capacity > 1.6L"
                            />
                          </Grid>
                          
                          <Grid item xs={12} md={6}>
                            <FormControlLabel
                              control={
                                <Switch
                                  checked={taxationData.salary.perquisites.is_expenses_reimbursed}
                                  onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'is_expenses_reimbursed', e.target.checked)}
                                  color="primary"
                                />
                              }
                              label="Expenses Reimbursed by Employer"
                            />
                          </Grid>
                          
                          <Grid item xs={12} md={6}>
                            <FormControlLabel
                              control={
                                <Switch
                                  checked={taxationData.salary.perquisites.is_driver_provided}
                                  onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'is_driver_provided', e.target.checked)}
                                  color="primary"
                                />
                              }
                              label="Driver Provided by Employer"
                            />
                          </Grid>
                          
                          <Grid item xs={12} md={6}>
                            <FormControl fullWidth>
                              <InputLabel>Car Use</InputLabel>
                              <Select
                                value={taxationData.salary.perquisites.car_use}
                                onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'car_use', e.target.value)}
                                label="Car Use"
                              >
                                <MenuItem value="Personal">Personal Use</MenuItem>
                                <MenuItem value="Business">Business Use</MenuItem>
                                <MenuItem value="Mixed">Mixed Use</MenuItem>
                              </Select>
                            </FormControl>
                          </Grid>
                          
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Car Cost to Employer"
                              type="text"
                              value={formatIndianNumber(taxationData.salary.perquisites.car_cost_to_employer)}
                              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'car_cost_to_employer', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'car_cost_to_employer', e.target.value)}
                            />
                          </Grid>
                          
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Number of Months"
                              type="number"
                              value={taxationData.salary.perquisites.month_counts}
                              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'month_counts', e.target.value)}
                              inputProps={{ min: 0, max: 12 }}
                            />
                          </Grid>
                          
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Other Vehicle Cost"
                              type="text"
                              value={formatIndianNumber(taxationData.salary.perquisites.other_vehicle_cost)}
                              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'other_vehicle_cost', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'other_vehicle_cost', e.target.value)}
                            />
                          </Grid>
                          
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Other Vehicle Months"
                              type="number"
                              value={taxationData.salary.perquisites.other_vehicle_months}
                              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'other_vehicle_months', e.target.value)}
                              inputProps={{ min: 0, max: 12 }}
                            />
                          </Grid>
                        </Grid>
                      </Box>
                      
                      {/* Medical Reimbursement */}
                      <Box sx={{ mt: 4 }}>
                        <Typography variant="subtitle1" gutterBottom>Medical Reimbursement</Typography>
                        <Grid container spacing={3}>
                          <Grid item xs={12} md={6}>
                            <FormControlLabel
                              control={
                                <Switch
                                  checked={taxationData.salary.perquisites.is_treated_in_India}
                                  onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'is_treated_in_India', e.target.checked)}
                                  color="primary"
                                />
                              }
                              label="Medical Treatment in India"
                            />
                            <FormHelperText>
                              {taxationData.regime === 'old' ? 
                                "Eligible for up to ₹15,000 tax exemption if treated in India" : 
                                "Not applicable in new tax regime"}
                            </FormHelperText>
                          </Grid>
                          
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Medical Reimbursement Amount"
                              type="text"
                              value={formatIndianNumber(taxationData.salary.perquisites.medical_reimbursement_by_employer)}
                              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'medical_reimbursement_by_employer', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'medical_reimbursement_by_employer', e.target.value)}
                              disabled={taxationData.regime === 'new'}
                              helperText={taxationData.regime === 'old' && taxationData.salary.perquisites.is_treated_in_India ? 
                                "Tax exemption up to ₹15,000" : "No exemption"}
                            />
                          </Grid>
                        </Grid>
                      </Box>
                      
                      {/* Leave Travel Allowance */}
                      <Box sx={{ mt: 4 }}>
                        <Typography variant="subtitle1" gutterBottom>Leave Travel Allowance (LTA)</Typography>
                        <Grid container spacing={3}>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="LTA Amount"
                              type="text"
                              value={formatIndianNumber(taxationData.salary.perquisites.lta_amount_claimed)}
                              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'lta_amount_claimed', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'lta_amount_claimed', e.target.value)}
                              disabled={taxationData.regime === 'new'}
                              helperText={taxationData.regime === 'old' ? 
                                "Exemption for 2 journeys in a block of 4 years" : 
                                "Not applicable in new tax regime"}
                            />
                          </Grid>
                          
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Number of Journeys Claimed"
                              type="number"
                              value={taxationData.salary.perquisites.lta_claimed_count}
                              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'lta_claimed_count', e.target.value)}
                              inputProps={{ min: 0, max: 4 }}
                              disabled={taxationData.regime === 'new'}
                              helperText="Max 2 journeys are exempt in a block of 4 years"
                            />
                          </Grid>
                          
                          <Grid item xs={12} md={6}>
                            <FormControl fullWidth disabled={taxationData.regime === 'new'}>
                              <InputLabel>Travel Mode</InputLabel>
                              <Select
                                value={taxationData.salary.perquisites.travel_through}
                                onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'travel_through', e.target.value)}
                                label="Travel Mode"
                              >
                                <MenuItem value="Air">Air</MenuItem>
                                <MenuItem value="Train">Train</MenuItem>
                                <MenuItem value="Bus">Bus</MenuItem>
                                <MenuItem value="Other">Other</MenuItem>
                              </Select>
                              <FormHelperText>
                                LTA exemption is limited to cheapest public transport fare for the same distance
                              </FormHelperText>
                            </FormControl>
                          </Grid>
                          
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Cheapest Public Transport Fare"
                              type="text"
                              value={formatIndianNumber(taxationData.salary.perquisites.public_transport_travel_amount_for_same_distance)}
                              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'public_transport_travel_amount_for_same_distance', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'public_transport_travel_amount_for_same_distance', e.target.value)}
                              disabled={taxationData.regime === 'new'}
                              helperText="Fare by the cheapest public transport for the same distance"
                            />
                          </Grid>
                          
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Journey Start Date"
                              type="date"
                              value={taxationData.salary.perquisites.lta_claim_start_date}
                              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'lta_claim_start_date', e.target.value)}
                              disabled={taxationData.regime === 'new'}
                              InputLabelProps={{ shrink: true }}
                            />
                          </Grid>
                          
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Journey End Date"
                              type="date"
                              value={taxationData.salary.perquisites.lta_claim_end_date}
                              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'lta_claim_end_date', e.target.value)}
                              disabled={taxationData.regime === 'new'}
                              InputLabelProps={{ shrink: true }}
                            />
                          </Grid>
                        </Grid>
                      </Box>
                      
                      {/* Free Education */}
                      <Box sx={{ mt: 4 }}>
                        <Typography variant="subtitle1" gutterBottom>Free Education</Typography>
                        <Grid container spacing={3}>
                          <Grid item xs={12} md={6}>
                            <FormControlLabel
                              control={
                                <Switch
                                  checked={taxationData.salary.perquisites.free_education_is_institute_by_employer}
                                  onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'free_education_is_institute_by_employer', e.target.checked)}
                                  color="primary"
                                />
                              }
                              label="Education Provided in Employer's Institute"
                            />
                            <FormHelperText>
                              {taxationData.regime === 'old' ? 
                                "Cost of education in similar institute is considered" : 
                                "Not applicable in new tax regime"}
                            </FormHelperText>
                          </Grid>
                          
                          {taxationData.salary.perquisites.free_education_is_institute_by_employer ? (
                            <Grid item xs={12} md={6}>
                              <TextField
                                fullWidth
                                label="Cost in Similar Institute"
                                type="text"
                                value={formatIndianNumber(taxationData.salary.perquisites.free_education_similar_institute_cost)}
                                onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'free_education_similar_institute_cost', e.target.value)}
                                InputProps={{ startAdornment: '₹' }}
                                onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'free_education_similar_institute_cost', e.target.value)}
                                disabled={taxationData.regime === 'new'}
                                helperText="Rs. 1,000 per month (Rs. 12,000 annually) exempt"
                              />
                            </Grid>
                          ) : (
                            <Grid item xs={12} md={6}>
                              <TextField
                                fullWidth
                                label="Education Expenses Paid by Employer"
                                type="text"
                                value={formatIndianNumber(taxationData.salary.perquisites.free_education_actual_expenses)}
                                onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'free_education_actual_expenses', e.target.value)}
                                InputProps={{ startAdornment: '₹' }}
                                onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'free_education_actual_expenses', e.target.value)}
                                disabled={taxationData.regime === 'new'}
                                helperText="Rs. 1,000 per month (Rs. 12,000 annually) exempt"
                              />
                            </Grid>
                          )}
                          
                          <Grid item xs={12}>
                            <Alert severity="info" sx={{ mt: 1 }}>
                              <Typography variant="body2">
                                Free education is exempt up to Rs. 1,000 per month (Rs. 12,000 annually). 
                                Any amount above this is taxable as a perquisite.
                              </Typography>
                            </Alert>
                          </Grid>
                        </Grid>
                      </Box>
                      
                      {/* Gas, Electricity, Water */}
                      <Box sx={{ mt: 4 }}>
                        <Typography variant="subtitle1" gutterBottom>Gas, Electricity & Water</Typography>
                        <Grid container spacing={3}>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Gas - Paid by Employer"
                              type="text"
                              value={formatIndianNumber(taxationData.salary.perquisites.gas_amount_paid_by_employer)}
                              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'gas_amount_paid_by_employer', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'gas_amount_paid_by_employer', e.target.value)}
                              disabled={taxationData.regime === 'new'}
                            />
                          </Grid>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Gas - Paid by Employee"
                              type="text"
                              value={formatIndianNumber(taxationData.salary.perquisites.gas_amount_paid_by_employee)}
                              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'gas_amount_paid_by_employee', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'gas_amount_paid_by_employee', e.target.value)}
                              disabled={taxationData.regime === 'new'}
                            />
                          </Grid>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Electricity - Paid by Employer"
                              type="text"
                              value={formatIndianNumber(taxationData.salary.perquisites.electricity_amount_paid_by_employer)}
                              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'electricity_amount_paid_by_employer', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'electricity_amount_paid_by_employer', e.target.value)}
                              disabled={taxationData.regime === 'new'}
                            />
                          </Grid>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Electricity - Paid by Employee"
                              type="text"
                              value={formatIndianNumber(taxationData.salary.perquisites.electricity_amount_paid_by_employee)}
                              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'electricity_amount_paid_by_employee', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'electricity_amount_paid_by_employee', e.target.value)}
                              disabled={taxationData.regime === 'new'}
                            />
                          </Grid>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Water - Paid by Employer"
                              type="text"
                              value={formatIndianNumber(taxationData.salary.perquisites.water_amount_paid_by_employer)}
                              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'water_amount_paid_by_employer', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'water_amount_paid_by_employer', e.target.value)}
                              disabled={taxationData.regime === 'new'}
                            />
                          </Grid>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Water - Paid by Employee"
                              type="text"
                              value={formatIndianNumber(taxationData.salary.perquisites.water_amount_paid_by_employee)}
                              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'water_amount_paid_by_employee', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'water_amount_paid_by_employee', e.target.value)}
                              disabled={taxationData.regime === 'new'}
                            />
                          </Grid>
                          <Grid item xs={12}>
                            <Alert severity="info" sx={{ mt: 1 }}>
                              <Typography variant="body2">
                                The taxable value is the amount paid by the employer minus any amount recovered from the employee.
                              </Typography>
                            </Alert>
                          </Grid>
                        </Grid>
                      </Box>
                      
                      {/* Domestic Help */}
                      <Box sx={{ mt: 4 }}>
                        <Typography variant="subtitle1" gutterBottom>Domestic Help</Typography>
                        <Grid container spacing={3}>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Domestic Help - Paid by Employer"
                              type="text"
                              value={formatIndianNumber(taxationData.salary.perquisites.domestic_help_amount_paid_by_employer)}
                              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'domestic_help_amount_paid_by_employer', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'domestic_help_amount_paid_by_employer', e.target.value)}
                              disabled={taxationData.regime === 'new'}
                            />
                          </Grid>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Domestic Help - Paid by Employee"
                              type="text"
                              value={formatIndianNumber(taxationData.salary.perquisites.domestic_help_amount_paid_by_employee)}
                              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'domestic_help_amount_paid_by_employee', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'domestic_help_amount_paid_by_employee', e.target.value)}
                              disabled={taxationData.regime === 'new'}
                            />
                          </Grid>
                          <Grid item xs={12}>
                            <Alert severity="info" sx={{ mt: 1 }}>
                              <Typography variant="body2">
                                The taxable value is the amount paid by the employer minus any amount recovered from the employee.
                              </Typography>
                            </Alert>
                          </Grid>
                        </Grid>
                      </Box>
                      
                      {/* Interest-free/concessional loan */}
                      <Box sx={{ mt: 4 }}>
                        <Typography variant="subtitle1" gutterBottom>Interest-free/Concessional Loan</Typography>
                        <Grid container spacing={3}>
                          <Grid item xs={12} md={6}>
                            <FormControl fullWidth disabled={taxationData.regime === 'new'}>
                              <InputLabel>Loan Type</InputLabel>
                              <Select
                                value={taxationData.salary.perquisites.loan_type}
                                onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'loan_type', e.target.value)}
                                label="Loan Type"
                              >
                                <MenuItem value="">Select Loan Type</MenuItem>
                                <MenuItem value="Car Loan">Car Loan</MenuItem>
                                <MenuItem value="House Loan">House Loan</MenuItem>
                                <MenuItem value="Personal Loan">Personal Loan</MenuItem>
                                <MenuItem value="Other">Other</MenuItem>
                              </Select>
                            </FormControl>
                          </Grid>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Loan Amount"
                              type="text"
                              value={formatIndianNumber(taxationData.salary.perquisites.loan_amount)}
                              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'loan_amount', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'loan_amount', e.target.value)}
                              disabled={taxationData.regime === 'new'}
                            />
                          </Grid>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Interest Rate Charged by Company (%)"
                              type="number"
                              value={taxationData.salary.perquisites.loan_interest_rate_company}
                              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'loan_interest_rate_company', e.target.value)}
                              InputProps={{ endAdornment: '%' }}
                              disabled={taxationData.regime === 'new'}
                            />
                          </Grid>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="SBI Interest Rate (%)"
                              type="number"
                              value={taxationData.salary.perquisites.loan_interest_rate_sbi}
                              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'loan_interest_rate_sbi', e.target.value)}
                              InputProps={{ endAdornment: '%' }}
                              disabled={taxationData.regime === 'new'}
                            />
                          </Grid>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Monthly Interest - SBI Rate"
                              type="text"
                              value={formatIndianNumber(taxationData.salary.perquisites.monthly_interest_amount_sbi)}
                              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'monthly_interest_amount_sbi', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'monthly_interest_amount_sbi', e.target.value)}
                              disabled={taxationData.regime === 'new'}
                            />
                          </Grid>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Monthly Interest - Company Rate"
                              type="text"
                              value={formatIndianNumber(taxationData.salary.perquisites.monthly_interest_amount_company)}
                              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'monthly_interest_amount_company', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'monthly_interest_amount_company', e.target.value)}
                              disabled={taxationData.regime === 'new'}
                            />
                          </Grid>
                          <Grid item xs={12}>
                            <Alert severity="info" sx={{ mt: 1 }}>
                              <Typography variant="body2">
                                The taxable value is the difference between the interest calculated at the SBI rate and the interest actually charged by the company, annualized.
                              </Typography>
                            </Alert>
                          </Grid>
                        </Grid>
                      </Box>
                      
                      {/* Lunch/Refreshment */}
                      <Box sx={{ mt: 4 }}>
                        <Typography variant="subtitle1" gutterBottom>Lunch/Refreshment</Typography>
                        <Grid container spacing={3}>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Lunch - Paid by Employer"
                              type="text"
                              value={formatIndianNumber(taxationData.salary.perquisites.lunch_amount_paid_by_employer)}
                              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'lunch_amount_paid_by_employer', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'lunch_amount_paid_by_employer', e.target.value)}
                              disabled={taxationData.regime === 'new'}
                            />
                          </Grid>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Lunch - Paid by Employee"
                              type="text"
                              value={formatIndianNumber(taxationData.salary.perquisites.lunch_amount_paid_by_employee)}
                              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'lunch_amount_paid_by_employee', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'lunch_amount_paid_by_employee', e.target.value)}
                              disabled={taxationData.regime === 'new'}
                            />
                          </Grid>
                          <Grid item xs={12}>
                            <Alert severity="info" sx={{ mt: 1 }}>
                              <Typography variant="body2">
                                Rs. 50 per month (Rs. 600 annually) is exempt. The taxable value is the amount paid by the employer minus any amount recovered from the employee, minus the exemption.
                              </Typography>
                            </Alert>
                          </Grid>
                        </Grid>
                      </Box>
                    </AccordionDetails>
                  </Accordion>
                </Grid>
              </Grid>
            )}

            {/* Step 2: Other Income */}
            {activeStep === 1 && (
              <Grid container spacing={3}>
                  <Grid item xs={12}>
                    <Accordion>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography variant="h6" gutterBottom>Income from Other Sources</Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Grid container spacing={3}>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Interest from Savings Account"
                              type="text"
                              value={formatIndianNumber(taxationData.other_sources.interest_savings)}
                              onChange={(e) => handleInputChange('other_sources', 'interest_savings', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleFocus('other_sources', 'interest_savings', e.target.value)}
                            />
                          </Grid>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Interest from Fixed Deposits"
                              type="text"
                              value={formatIndianNumber(taxationData.other_sources.interest_fd)}
                              onChange={(e) => handleInputChange('other_sources', 'interest_fd', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleFocus('other_sources', 'interest_fd', e.target.value)}
                            />
                          </Grid>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Interest from Recurring Deposits"
                              type="text"
                              value={formatIndianNumber(taxationData.other_sources.interest_rd)}
                              onChange={(e) => handleInputChange('other_sources', 'interest_rd', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleFocus('other_sources', 'interest_rd', e.target.value)}
                            />
                          </Grid>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Dividend Income"
                              type="text"
                              value={formatIndianNumber(taxationData.other_sources.dividend_income)}
                              onChange={(e) => handleInputChange('other_sources', 'dividend_income', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleFocus('other_sources', 'dividend_income', e.target.value)}
                            />
                          </Grid>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Gifts (Cash/Property)"
                              type="text"
                              value={formatIndianNumber(taxationData.other_sources.gifts)}
                              onChange={(e) => handleInputChange('other_sources', 'gifts', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleFocus('other_sources', 'gifts', e.target.value)}
                            />
                          </Grid>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Other Interest Income"
                              type="text"
                              value={formatIndianNumber(taxationData.other_sources.other_interest)}
                              onChange={(e) => handleInputChange('other_sources', 'other_interest', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleFocus('other_sources', 'other_interest', e.target.value)}
                            />
                          </Grid>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Other Income"
                              type="text"
                              value={formatIndianNumber(taxationData.other_sources.other_income)}
                              onChange={(e) => handleInputChange('other_sources', 'other_income', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleFocus('other_sources', 'other_income', e.target.value)}
                            />
                          </Grid>
                        </Grid>
                      </AccordionDetails>
                    </Accordion>
                  </Grid>

                  <Grid item xs={12}>
                    <Accordion>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography variant="h6" gutterBottom>Capital Gains</Typography>
                      </AccordionSummary>             
                      <AccordionDetails>
                        <Box sx={{ width: '100%' }}>
                          {/* STCG Section Header */}
                          <Box 
                            sx={{ 
                              width: '100%', 
                              p: 2, 
                              mb: 3, 
                              borderRadius: 1,
                              display: 'flex',
                              justifyContent: 'left'
                            }}
                          >
                            <Typography variant="h6" color="primary">Short-Term Capital Gains (STCG)</Typography>
                          </Box>
                          
                          {/* STCG Form Fields */}
                          <Grid container spacing={3} sx={{ mb: 4 }}>
                            <Grid item xs={12} md={4}>
                              <TextField
                                fullWidth
                                label="STCG on Equity Shares/Mutual Funds (Section 111A)"
                                type="text"
                                value={formatIndianNumber(taxationData.capital_gains.stcg_111a)}
                                onChange={(e) => handleInputChange('capital_gains', 'stcg_111a', e.target.value)}
                                InputProps={{ startAdornment: '₹' }}
                                helperText="15% flat rate on STT paid equity"
                                onFocus={(e) => handleFocus('capital_gains', 'stcg_111a', e.target.value)}
                              />
                            </Grid>
                            <Grid item xs={12} md={4}>
                              <TextField
                                fullWidth
                                label="STCG on Debt Mutual Funds"
                                type="text"
                                value={formatIndianNumber(taxationData.capital_gains.stcg_debt_mutual_fund)}
                                onChange={(e) => handleInputChange('capital_gains', 'stcg_debt_mutual_fund', e.target.value)}
                                InputProps={{ startAdornment: '₹' }}
                                helperText="Taxed at income tax slab rates"
                                onFocus={(e) => handleFocus('capital_gains', 'stcg_debt_mutual_fund', e.target.value)}
                              />
                            </Grid>
                            <Grid item xs={12} md={4}>
                              <TextField
                                fullWidth
                                label="STCG on Other Assets"
                                type="text"
                                value={formatIndianNumber(taxationData.capital_gains.stcg_any_other_asset)}
                                onChange={(e) => handleInputChange('capital_gains', 'stcg_any_other_asset', e.target.value)}
                                InputProps={{ startAdornment: '₹' }}
                                helperText="Taxed at income tax slab rates"
                                onFocus={(e) => handleFocus('capital_gains', 'stcg_any_other_asset', e.target.value)}
                              />
                            </Grid>
                          </Grid>
                          
                          <Divider sx={{ my: 4 }} />
                          
                          {/* LTCG Section Header */}
                         <Box 
                            sx={{ 
                              width: '100%', 
                              p: 2, 
                              mb: 3, 
                              borderRadius: 1,
                              display: 'flex',
                              justifyContent: 'left'
                            }}
                          >
                            <Typography variant="h6" color="primary">Long-Term Capital Gains (LTCG)</Typography>
                          </Box>
                          
                          {/* LTCG Form Fields */}
                          <Grid container spacing={3}>
                            <Grid item xs={12} md={4}>
                              <TextField
                                fullWidth
                                label="LTCG on Equity Shares/Mutual Funds (Section 112A)"
                                type="text"
                                value={formatIndianNumber(taxationData.capital_gains.ltcg_112a)}
                                onChange={(e) => handleInputChange('capital_gains', 'ltcg_112a', e.target.value)}
                                InputProps={{ startAdornment: '₹' }}
                                helperText="10% flat rate above ₹1 lakh on STT paid equity"
                                onFocus={(e) => handleFocus('capital_gains', 'ltcg_112a', e.target.value)}
                              />
                            </Grid>
                            <Grid item xs={12} md={4}>
                              <TextField
                                fullWidth
                                label="LTCG on Debt Mutual Funds"
                                type="text"
                                value={formatIndianNumber(taxationData.capital_gains.ltcg_debt_mutual_fund)}
                                onChange={(e) => handleInputChange('capital_gains', 'ltcg_debt_mutual_fund', e.target.value)}
                                InputProps={{ startAdornment: '₹' }}
                                helperText="20% flat rate with indexation benefit"
                                onFocus={(e) => handleFocus('capital_gains', 'ltcg_debt_mutual_fund', e.target.value)}
                              />
                            </Grid>
                            <Grid item xs={12} md={4}>
                              <TextField
                                fullWidth
                                label="LTCG on Other Assets"
                                type="text"
                                value={formatIndianNumber(taxationData.capital_gains.ltcg_any_other_asset)}
                                onChange={(e) => handleInputChange('capital_gains', 'ltcg_any_other_asset', e.target.value)}
                                InputProps={{ startAdornment: '₹' }}
                                helperText="20% flat rate with indexation benefit"
                                onFocus={(e) => handleFocus('capital_gains', 'ltcg_any_other_asset', e.target.value)}
                              />
                            </Grid>
                          </Grid>
                        </Box>
                      </AccordionDetails>
                    </Accordion>
                  </Grid>
              </Grid>
            )}

            {/* Step 3: Deductions (disabled in new regime) */}
            {activeStep === 2 && (
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography variant="h6" gutterBottom>Tax Deductions</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Grid container spacing={3}>
                        <Grid item xs={12}>
                          {taxationData.regime === 'new' && (
                            <Alert severity="info" sx={{ mb: 2 }}>
                              Tax deductions are not applicable in the New Tax Regime. You can switch to the Old Regime
                              to avail these deductions.
                            </Alert>
                          )}
                        </Grid>
                        
                        {/* Section 80C Deductions */}
                        <Grid item xs={12}>
                          <Accordion disabled={taxationData.regime === 'new'}>
                            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                              <Typography>Section 80C - Investments & Payments (Max ₹1,50,000)</Typography>
                            </AccordionSummary>
                            <AccordionDetails>
                              <Grid container spacing={2}>
                                <Grid item xs={12} md={6}>
                                  <TextField
                                    fullWidth
                                    label="Life Insurance Premium"
                                    type="text"
                                    value={formatIndianNumber(taxationData.deductions.section_80c_lic)}
                                    onChange={(e) => handleInputChange('deductions', 'section_80c_lic', e.target.value)}
                                    InputProps={{ startAdornment: '₹' }}
                                    disabled={taxationData.regime === 'new'}
                                    onFocus={(e) => handleFocus('deductions', 'section_80c_lic', e.target.value)}
                                  />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                  <TextField
                                    fullWidth
                                    label="Employee Provident Fund (EPF)"
                                    type="text"
                                    value={formatIndianNumber(taxationData.deductions.section_80c_epf)}
                                    onChange={(e) => handleInputChange('deductions', 'section_80c_epf', e.target.value)}
                                    InputProps={{ startAdornment: '₹' }}
                                    disabled={taxationData.regime === 'new'}
                                    onFocus={(e) => handleFocus('deductions', 'section_80c_epf', e.target.value)}
                                  />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                  <TextField
                                    fullWidth
                                    label="Sukanya Samriddhi Account"
                                    type="text"
                                    value={formatIndianNumber(taxationData.deductions.section_80c_ssp)}
                                    onChange={(e) => handleInputChange('deductions', 'section_80c_ssp', e.target.value)}
                                    InputProps={{ startAdornment: '₹' }}
                                    disabled={taxationData.regime === 'new'}
                                    onFocus={(e) => handleFocus('deductions', 'section_80c_ssp', e.target.value)}
                                  />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                  <TextField
                                    fullWidth
                                    label="National Savings Certificate (NSC)"
                                    type="text"
                                    value={formatIndianNumber(taxationData.deductions.section_80c_nsc)}
                                    onChange={(e) => handleInputChange('deductions', 'section_80c_nsc', e.target.value)}
                                    InputProps={{ startAdornment: '₹' }}
                                    disabled={taxationData.regime === 'new'}
                                    onFocus={(e) => handleFocus('deductions', 'section_80c_nsc', e.target.value)}
                                  />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                  <TextField
                                    fullWidth
                                    label="Unit Linked Insurance Plan (ULIP)"
                                    type="text"
                                    value={formatIndianNumber(taxationData.deductions.section_80c_ulip)}
                                    onChange={(e) => handleInputChange('deductions', 'section_80c_ulip', e.target.value)}
                                    InputProps={{ startAdornment: '₹' }}
                                    disabled={taxationData.regime === 'new'}
                                    onFocus={(e) => handleFocus('deductions', 'section_80c_ulip', e.target.value)}
                                  />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                  <TextField
                                    fullWidth
                                    label="Tax Saving Mutual Funds (ELSS)"
                                    type="text"
                                    value={formatIndianNumber(taxationData.deductions.section_80c_tsmf)}
                                    onChange={(e) => handleInputChange('deductions', 'section_80c_tsmf', e.target.value)}
                                    InputProps={{ startAdornment: '₹' }}
                                    disabled={taxationData.regime === 'new'}
                                    onFocus={(e) => handleFocus('deductions', 'section_80c_tsmf', e.target.value)}
                                  />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                  <TextField
                                    fullWidth
                                    label="Tuition Fees (for up to 2 children)"
                                    type="text"
                                    value={formatIndianNumber(taxationData.deductions.section_80c_tffte2c)}
                                    onChange={(e) => handleInputChange('deductions', 'section_80c_tffte2c', e.target.value)}
                                    InputProps={{ startAdornment: '₹' }}
                                    disabled={taxationData.regime === 'new'}
                                    onFocus={(e) => handleFocus('deductions', 'section_80c_tffte2c', e.target.value)}
                                  />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                  <TextField
                                    fullWidth
                                    label="Principal Repayment on Housing Loan"
                                    type="text"
                                    value={formatIndianNumber(taxationData.deductions.section_80c_paphl)}
                                    onChange={(e) => handleInputChange('deductions', 'section_80c_paphl', e.target.value)}
                                    InputProps={{ startAdornment: '₹' }}
                                    disabled={taxationData.regime === 'new'}
                                    onFocus={(e) => handleFocus('deductions', 'section_80c_paphl', e.target.value)}
                                  />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                  <TextField
                                    fullWidth
                                    label="Stamp Duty on Property Purchase"
                                    type="text"
                                    value={formatIndianNumber(taxationData.deductions.section_80c_sdpphp)}
                                    onChange={(e) => handleInputChange('deductions', 'section_80c_sdpphp', e.target.value)}
                                    InputProps={{ startAdornment: '₹' }}
                                    disabled={taxationData.regime === 'new'}
                                    onFocus={(e) => handleFocus('deductions', 'section_80c_sdpphp', e.target.value)}
                                  />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                  <TextField
                                    fullWidth
                                    label="Tax Saving Fixed Deposit (5 year lock-in)"
                                    type="text"
                                    value={formatIndianNumber(taxationData.deductions.section_80c_tsfdsb)}
                                    onChange={(e) => handleInputChange('deductions', 'section_80c_tsfdsb', e.target.value)}
                                    InputProps={{ startAdornment: '₹' }}
                                    disabled={taxationData.regime === 'new'}
                                    onFocus={(e) => handleFocus('deductions', 'section_80c_tsfdsb', e.target.value)}
                                  />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                  <TextField
                                    fullWidth
                                    label="Senior Citizens Savings Scheme"
                                    type="text"
                                    value={formatIndianNumber(taxationData.deductions.section_80c_scss)}
                                    onChange={(e) => handleInputChange('deductions', 'section_80c_scss', e.target.value)}
                                    InputProps={{ startAdornment: '₹' }}
                                    disabled={taxationData.regime === 'new'}
                                    onFocus={(e) => handleFocus('deductions', 'section_80c_scss', e.target.value)}
                                  />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                  <TextField
                                    fullWidth
                                    label="Other 80C Investments"
                                    type="text"
                                    value={formatIndianNumber(taxationData.deductions.section_80c_others)}
                                    onChange={(e) => handleInputChange('deductions', 'section_80c_others', e.target.value)}
                                    InputProps={{ startAdornment: '₹' }}
                                    disabled={taxationData.regime === 'new'}
                                    onFocus={(e) => handleFocus('deductions', 'section_80c_others', e.target.value)}
                                  />
                                </Grid>
                              </Grid>
                            </AccordionDetails>
                          </Accordion>
                        </Grid>
                        
                        {/* Section 80CCC/CCD Deductions */}
                        <Grid item xs={12}>
                          <Accordion>
                            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                              <Typography>Section 80CCC/CCD - Pension & NPS</Typography>
                            </AccordionSummary>
                            <AccordionDetails>
                              <Grid container spacing={2}>
                                <Grid item xs={12} md={6}>
                                  <TextField
                                    fullWidth
                                    label="Section 80CCC - Pension Plan"
                                    type="text"
                                    value={formatIndianNumber(taxationData.deductions.section_80ccc_ppic)}
                                    onChange={(e) => handleInputChange('deductions', 'section_80ccc_ppic', e.target.value)}
                                    InputProps={{ startAdornment: '₹' }}
                                    disabled={taxationData.regime === 'new'}
                                    helperText="Part of overall 80C limit of ₹1,50,000"
                                    onFocus={(e) => handleFocus('deductions', 'section_80ccc_ppic', e.target.value)}
                                  />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                  <TextField
                                    fullWidth
                                    label="Section 80CCD(1) - NPS Contribution"
                                    type="text"
                                    value={formatIndianNumber(taxationData.deductions.section_80ccd_1_nps)}
                                    onChange={(e) => handleInputChange('deductions', 'section_80ccd_1_nps', e.target.value)}
                                    InputProps={{ startAdornment: '₹' }}
                                    disabled={taxationData.regime === 'new'}
                                    helperText="Part of overall 80C limit of ₹1,50,000"
                                    onFocus={(e) => handleFocus('deductions', 'section_80ccd_1_nps', e.target.value)}
                                  />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                  <TextField
                                    fullWidth
                                    label="Section 80CCD(1B) - Additional NPS"
                                    type="text"
                                    value={formatIndianNumber(taxationData.deductions.section_80ccd_1b_additional)}
                                    onChange={(e) => handleInputChange('deductions', 'section_80ccd_1b_additional', e.target.value)}
                                    InputProps={{ startAdornment: '₹' }}
                                    disabled={taxationData.regime === 'new'}
                                    helperText="Additional deduction up to ₹50,000"
                                    onFocus={(e) => handleFocus('deductions', 'section_80ccd_1b_additional', e.target.value)}
                                  />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                  <TextField
                                    fullWidth
                                    label="Section 80CCD(2) - Employer NPS Contribution"
                                    type="text"
                                    value={formatIndianNumber(taxationData.deductions.section_80ccd_2_enps)}
                                    onChange={(e) => handleInputChange('deductions', 'section_80ccd_2_enps', e.target.value)}
                                    InputProps={{ startAdornment: '₹' }}
                                    disabled={taxationData.regime === 'new'}
                                    helperText="10% of salary (private) or 14% of salary (govt)"
                                    onFocus={(e) => handleFocus('deductions', 'section_80ccd_2_enps', e.target.value)}
                                  />
                                </Grid>
                              </Grid>
                            </AccordionDetails>
                          </Accordion>
                        </Grid>
                        
                        {/* Section 80D Deductions */}
                        <Grid item xs={12}>
                          <Accordion>
                            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                              <Typography>Section 80D - Health Insurance & Medical</Typography>
                            </AccordionSummary>
                            <AccordionDetails>
                              <Grid container spacing={2}>
                                <Grid item xs={12} md={6}>
                                  <TextField
                                    fullWidth
                                    label="Health Insurance Premium - Self & Family"
                                    type="text"
                                    value={formatIndianNumber(taxationData.deductions.section_80d_hisf)}
                                    onChange={(e) => handleInputChange('deductions', 'section_80d_hisf', e.target.value)}
                                    InputProps={{ startAdornment: '₹' }}
                                    disabled={taxationData.regime === 'new'}
                                    helperText="Max ₹25,000 (₹50,000 for senior citizens)"
                                    onFocus={(e) => handleFocus('deductions', 'section_80d_hisf', e.target.value)}
                                  />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                  <TextField
                                    fullWidth
                                    label="Preventive Health Checkup"
                                    type="text"
                                    value={formatIndianNumber(taxationData.deductions.section_80d_phcs)}
                                    onChange={(e) => handleInputChange('deductions', 'section_80d_phcs', e.target.value)}
                                    InputProps={{ startAdornment: '₹' }}
                                    disabled={taxationData.regime === 'new'}
                                    helperText="Max ₹5,000 (included in overall 80D limit)"
                                    onFocus={(e) => handleFocus('deductions', 'section_80d_phcs', e.target.value)}
                                  />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                  <TextField
                                    fullWidth
                                    label="Health Insurance Premium - Parents"
                                    type="text"
                                    value={formatIndianNumber(taxationData.deductions.section_80d_hi_parent)}
                                    onChange={(e) => handleInputChange('deductions', 'section_80d_hi_parent', e.target.value)}
                                    InputProps={{ startAdornment: '₹' }}
                                    disabled={taxationData.regime === 'new'}
                                    helperText="Max ₹25,000 (₹50,000 if parents are senior citizens)"
                                    onFocus={(e) => handleFocus('deductions', 'section_80d_hi_parent', e.target.value)}
                                  />
                                </Grid>
                              </Grid>
                            </AccordionDetails>
                          </Accordion>
                        </Grid>
                        
                        {/* Other Major Deductions */}
                        <Grid item xs={12}>
                          <Accordion>
                            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                              <Typography>Other Major Deductions</Typography>
                            </AccordionSummary>
                            <AccordionDetails>
                              <Grid container spacing={2}>
                                <Grid item xs={12} md={6}>
                                  <TextField
                                    fullWidth
                                    label="Section 24B - Home Loan Interest"
                                    type="text"
                                    value={formatIndianNumber(taxationData.deductions.section_24b)}
                                    onChange={(e) => handleInputChange('deductions', 'section_24b', e.target.value)}
                                    InputProps={{ startAdornment: '₹' }}
                                    disabled={taxationData.regime === 'new'}
                                    helperText="Max ₹2,00,000 for self-occupied property"
                                    onFocus={(e) => handleFocus('deductions', 'section_24b', e.target.value)}
                                  />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                  <TextField
                                    fullWidth
                                    label="Section 80DD - Disability Dependant"
                                    type="text"
                                    value={formatIndianNumber(taxationData.deductions.section_80dd)}
                                    onChange={(e) => handleInputChange('deductions', 'section_80dd', e.target.value)}
                                    InputProps={{ startAdornment: '₹' }}
                                    disabled={taxationData.regime === 'new'}
                                    helperText="₹75,000 or ₹1,25,000 based on % of disability"
                                    onFocus={(e) => handleFocus('deductions', 'section_80dd', e.target.value)}
                                  />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                  <FormControl fullWidth disabled={taxationData.regime === 'new'}>
                                    <InputLabel>Relationship (80DD)</InputLabel>
                                    <Select
                                      value={taxationData.deductions.relation_80dd || ''}
                                      onChange={(e) => handleInputChange('deductions', 'relation_80dd', e.target.value)}
                                      label="Relationship (80DD)"
                                    >
                                      <MenuItem value="">Select Relationship</MenuItem>
                                      <MenuItem value="Spouse">Spouse</MenuItem>
                                      <MenuItem value="Child">Child</MenuItem>
                                      <MenuItem value="Parents">Parents</MenuItem>
                                      <MenuItem value="Sibling">Sibling</MenuItem>
                                    </Select>
                                    <FormHelperText>Dependent with disability</FormHelperText>
                                  </FormControl>
                                </Grid>
                                <Grid item xs={12} md={6}>
                                  <FormControl fullWidth disabled={taxationData.regime === 'new'}>
                                    <InputLabel>Disability Percentage (80DD)</InputLabel>
                                    <Select
                                      value={taxationData.deductions.disability_percentage || ''}
                                      onChange={(e) => handleInputChange('deductions', 'disability_percentage', e.target.value)}
                                      label="Disability Percentage (80DD)"
                                    >
                                      <MenuItem value="">Select Percentage</MenuItem>
                                      <MenuItem value="Between 40%-80%">Between 40%-80% (₹75,000)</MenuItem>
                                      <MenuItem value="More than 80%">More than 80% (₹1,25,000)</MenuItem>
                                    </Select>
                                  </FormControl>
                                </Grid>
                                <Grid item xs={12} md={6}>
                                  <TextField
                                    fullWidth
                                    label="Section 80DDB - Medical Treatment"
                                    type="text"
                                    value={formatIndianNumber(taxationData.deductions.section_80ddb)}
                                    onChange={(e) => handleInputChange('deductions', 'section_80ddb', e.target.value)}
                                    InputProps={{ startAdornment: '₹' }}
                                    disabled={taxationData.regime === 'new'}
                                    helperText="Max ₹40,000 (₹1,00,000 for senior citizens)"
                                    onFocus={(e) => handleFocus('deductions', 'section_80ddb', e.target.value)}
                                  />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                  <FormControl fullWidth disabled={taxationData.regime === 'new'}>
                                    <InputLabel>Relationship (80DDB)</InputLabel>
                                    <Select
                                      value={taxationData.deductions.relation_80ddb || ''}
                                      onChange={(e) => handleInputChange('deductions', 'relation_80ddb', e.target.value)}
                                      label="Relationship (80DDB)"
                                    >
                                      <MenuItem value="">Select Relationship</MenuItem>
                                      <MenuItem value="Spouse">Spouse</MenuItem>
                                      <MenuItem value="Child">Child</MenuItem>
                                      <MenuItem value="Parents">Parents</MenuItem>
                                      <MenuItem value="Sibling">Sibling</MenuItem>
                                    </Select>
                                    <FormHelperText>Person receiving medical treatment</FormHelperText>
                                  </FormControl>
                                </Grid>
                                <Grid item xs={12} md={6}>
                                  <TextField
                                    fullWidth
                                    label="Age of Person (80DDB)"
                                    type="number"
                                    value={taxationData.deductions.age_80ddb || ''}
                                    onChange={(e) => handleInputChange('deductions', 'age_80ddb', parseInt(e.target.value) || 0)}
                                    disabled={taxationData.regime === 'new'}
                                    helperText="Different limits apply for senior citizens (60+ years)"
                                  />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                  <TextField
                                    fullWidth
                                    label="Section 80U - Self Disability"
                                    type="text"
                                    value={formatIndianNumber(taxationData.deductions.section_80u)}
                                    onChange={(e) => handleInputChange('deductions', 'section_80u', e.target.value)}
                                    InputProps={{ startAdornment: '₹' }}
                                    disabled={taxationData.regime === 'new'}
                                    helperText="₹75,000 or ₹1,25,000 based on % of disability"
                                    onFocus={(e) => handleFocus('deductions', 'section_80u', e.target.value)}
                                  />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                  <FormControl fullWidth disabled={taxationData.regime === 'new'}>
                                    <InputLabel>Disability Percentage (80U)</InputLabel>
                                    <Select
                                      value={taxationData.deductions.disability_percentage_80u || ''}
                                      onChange={(e) => handleInputChange('deductions', 'disability_percentage_80u', e.target.value)}
                                      label="Disability Percentage (80U)"
                                    >
                                      <MenuItem value="">Select Percentage</MenuItem>
                                      <MenuItem value="Between 40%-80%">Between 40%-80% (₹75,000)</MenuItem>
                                      <MenuItem value="More than 80%">More than 80% (₹1,25,000)</MenuItem>
                                    </Select>
                                    <FormHelperText>For self disability</FormHelperText>
                                  </FormControl>
                                </Grid>
                                
                                <Grid item xs={12} md={6}>
                                  <TextField
                                    fullWidth
                                    label="Section 80EEB - Electric Vehicle Loan Interest"
                                    type="text"
                                    value={formatIndianNumber(taxationData.deductions.section_80eeb)}
                                    onChange={(e) => handleInputChange('deductions', 'section_80eeb', e.target.value)}
                                    InputProps={{ startAdornment: '₹' }}
                                    disabled={taxationData.regime === 'new'}
                                    helperText="Max ₹1,50,000"
                                    onFocus={(e) => handleFocus('deductions', 'section_80eeb', e.target.value)}
                                  />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                  <TextField
                                    fullWidth
                                    label="EV Purchase Date"
                                    type="date"
                                    value={taxationData.deductions.ev_purchase_date || ''}
                                    onChange={(e) => handleInputChange('deductions', 'ev_purchase_date', e.target.value)}
                                    disabled={taxationData.regime === 'new'}
                                    helperText="Date of purchase must be between 01/04/2019 and 31/03/2023"
                                    InputLabelProps={{ shrink: true }}
                                  />
                                </Grid>
                              </Grid>
                            </AccordionDetails>
                          </Accordion>
                        </Grid>
                        
                        {/* Donation Deductions */}
                        <Grid item xs={12}>
                          <Accordion disabled={taxationData.regime === 'new'}>
                            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                              <Typography>Section 80G - Donations</Typography>
                            </AccordionSummary>
                            <AccordionDetails>
                              <Grid container spacing={2}>
                                <Grid item xs={12} md={6}>
                                  <TextField
                                    fullWidth
                                    label="Section 80G - General Donations"
                                    type="text"
                                    value={formatIndianNumber(taxationData.deductions.section_80g)}
                                    onChange={(e) => handleInputChange('deductions', 'section_80g', e.target.value)}
                                    InputProps={{ startAdornment: '₹' }}
                                    disabled={taxationData.regime === 'new'}
                                    onFocus={(e) => handleFocus('deductions', 'section_80g', e.target.value)}
                                  />
                                </Grid>
                                
                                {/* 100% Deduction Without Qualifying Limit */}
                                <Grid item xs={12} md={6}>
                                  <TextField
                                    fullWidth
                                    label="100% Deduction Without Qualifying Limit"
                                    type="text"
                                    value={formatIndianNumber(taxationData.deductions.section_80g_100_wo_ql)}
                                    onChange={(e) => handleInputChange('deductions', 'section_80g_100_wo_ql', e.target.value)}
                                    InputProps={{ startAdornment: '₹' }}
                                    disabled={taxationData.regime === 'new'}
                                    helperText="PM Relief Fund, National Defense Fund, etc."
                                    onFocus={(e) => handleFocus('deductions', 'section_80g_100_wo_ql', e.target.value)}
                                  />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                  <FormControl fullWidth disabled={taxationData.regime === 'new'}>
                                    <InputLabel>100% Deduction Category</InputLabel>
                                    <Select
                                      value={taxationData.deductions.section_80g_100_head || ''}
                                      onChange={(e) => handleInputChange('deductions', 'section_80g_100_head', e.target.value)}
                                      label="100% Deduction Category"
                                    >
                                      <MenuItem value="">Select Category</MenuItem>
                                      <MenuItem value="National Defence Fund set up by Central Government">National Defence Fund</MenuItem>
                                      <MenuItem value="Prime Minister national relief fund">PM National Relief Fund</MenuItem>
                                      <MenuItem value="Approved university">Approved University</MenuItem>
                                      <MenuItem value="Any other eligible donations for 100% deduction">Other eligible donations</MenuItem>
                                    </Select>
                                    <FormHelperText>Select the donation category</FormHelperText>
                                  </FormControl>
                                </Grid>
                                
                                {/* 50% Deduction Without Qualifying Limit */}
                                <Grid item xs={12} md={6}>
                                  <TextField
                                    fullWidth
                                    label="50% Deduction Without Qualifying Limit"
                                    type="text"
                                    value={formatIndianNumber(taxationData.deductions.section_80g_50_wo_ql)}
                                    onChange={(e) => handleInputChange('deductions', 'section_80g_50_wo_ql', e.target.value)}
                                    InputProps={{ startAdornment: '₹' }}
                                    disabled={taxationData.regime === 'new'}
                                    helperText="PM Drought Relief Fund, etc."
                                    onFocus={(e) => handleFocus('deductions', 'section_80g_50_wo_ql', e.target.value)}
                                  />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                  <FormControl fullWidth disabled={taxationData.regime === 'new'}>
                                    <InputLabel>50% Deduction Category</InputLabel>
                                    <Select
                                      value={taxationData.deductions.section_80g_50_head || ''}
                                      onChange={(e) => handleInputChange('deductions', 'section_80g_50_head', e.target.value)}
                                      label="50% Deduction Category"
                                    >
                                      <MenuItem value="">Select Category</MenuItem>
                                      <MenuItem value="Prime Minister's Drought Relief Fund">PM Drought Relief Fund</MenuItem>
                                    </Select>
                                    <FormHelperText>Select the donation category</FormHelperText>
                                  </FormControl>
                                </Grid>
                                
                                {/* 100% Deduction With Qualifying Limit */}
                                <Grid item xs={12} md={6}>
                                  <TextField
                                    fullWidth
                                    label="100% Deduction With Qualifying Limit (10% of Income)"
                                    type="text"
                                    value={formatIndianNumber(taxationData.deductions.section_80g_100_ql)}
                                    onChange={(e) => handleInputChange('deductions', 'section_80g_100_ql', e.target.value)}
                                    InputProps={{ startAdornment: '₹' }}
                                    disabled={taxationData.regime === 'new'}
                                    helperText="Limited to 10% of adjusted gross total income"
                                    onFocus={(e) => handleFocus('deductions', 'section_80g_100_ql', e.target.value)}
                                  />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                  <FormControl fullWidth disabled={taxationData.regime === 'new'}>
                                    <InputLabel>100% Deduction Category (With Limit)</InputLabel>
                                    <Select
                                      value={taxationData.deductions.section_80g_100_ql_head || ''}
                                      onChange={(e) => handleInputChange('deductions', 'section_80g_100_ql_head', e.target.value)}
                                      label="100% Deduction Category (With Limit)"
                                    >
                                      <MenuItem value="">Select Category</MenuItem>
                                      <MenuItem value="Donations to government or any approved local authority to promote family planning">Govt/Local Authority (Family Planning)</MenuItem>
                                      <MenuItem value="Any other fund that satisfies the conditions">Other eligible funds</MenuItem>
                                    </Select>
                                    <FormHelperText>Select the donation category</FormHelperText>
                                  </FormControl>
                                </Grid>
                                
                                {/* 50% Deduction With Qualifying Limit */}
                                <Grid item xs={12} md={6}>
                                  <TextField
                                    fullWidth
                                    label="50% Deduction With Qualifying Limit (10% of Income)"
                                    type="text"
                                    value={formatIndianNumber(taxationData.deductions.section_80g_50_ql)}
                                    onChange={(e) => handleInputChange('deductions', 'section_80g_50_ql', e.target.value)}
                                    InputProps={{ startAdornment: '₹' }}
                                    disabled={taxationData.regime === 'new'}
                                    helperText="Limited to 10% of adjusted gross total income"
                                    onFocus={(e) => handleFocus('deductions', 'section_80g_50_ql', e.target.value)}
                                  />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                  <FormControl fullWidth disabled={taxationData.regime === 'new'}>
                                    <InputLabel>50% Deduction Category (With Limit)</InputLabel>
                                    <Select
                                      value={taxationData.deductions.section_80g_50_ql_head || ''}
                                      onChange={(e) => handleInputChange('deductions', 'section_80g_50_ql_head', e.target.value)}
                                      label="50% Deduction Category (With Limit)"
                                    >
                                      <MenuItem value="">Select Category</MenuItem>
                                      <MenuItem value="Donations to government or any approved local authority to except to promote family planning">Govt/Local Authority (Except Family Planning)</MenuItem>
                                      <MenuItem value="Any Corporation for promoting interest of minority community">Corporation for minority community</MenuItem>
                                      <MenuItem value="For repair or renovation of any notified temple, mosque, gurudwara, church or other places of worship">Religious place renovation</MenuItem>
                                      <MenuItem value="Any other fund that satisfies the conditions">Other eligible funds</MenuItem>
                                    </Select>
                                    <FormHelperText>Select the donation category</FormHelperText>
                                  </FormControl>
                                </Grid>
                                
                                <Grid item xs={12} md={6}>
                                  <TextField
                                    fullWidth
                                    label="Section 80GGC - Political Donations"
                                    type="text"
                                    value={formatIndianNumber(taxationData.deductions.section_80ggc)}
                                    onChange={(e) => handleInputChange('deductions', 'section_80ggc', e.target.value)}
                                    InputProps={{ startAdornment: '₹' }}
                                    disabled={taxationData.regime === 'new'}
                                    helperText="100% deduction for donations to political parties"
                                    onFocus={(e) => handleFocus('deductions', 'section_80ggc', e.target.value)}
                                  />
                                </Grid>
                              </Grid>
                            </AccordionDetails>
                          </Accordion>
                        </Grid>
                      </Grid>
                    </AccordionDetails>
                  </Accordion>
                </Grid>
              </Grid>
            )}

            {/* Step 4: Review & Submit */}
            {activeStep === 3 && (
              <Box>
                <Typography variant="h6" gutterBottom>Review Your Tax Declaration</Typography>
                
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Card sx={{ mb: 2 }}>
                      <CardContent>
                        <Typography variant="h6" color="primary" gutterBottom>
                          Tax Regime
                        </Typography>
                        <Typography variant="body1">
                          {taxationData.regime === 'old' ? 'Old Regime (with deductions)' : 'New Regime (lower rates)'}
                        </Typography>
                      </CardContent>
                    </Card>

                    <Card sx={{ mb: 2 }}>
                      <CardContent>
                        <Typography variant="h6" color="primary" gutterBottom>
                          Salary Income
                        </Typography>
                        <Grid container spacing={1}>
                          <Grid item xs={8}><Typography>Basic Salary:</Typography></Grid>
                          <Grid item xs={4}><Typography align="right">{formatCurrency(taxationData.salary.basic)}</Typography></Grid>
                          
                          <Grid item xs={8}><Typography>Dearness Allowance (DA):</Typography></Grid>
                          <Grid item xs={4}><Typography align="right">{formatCurrency(taxationData.salary.dearness_allowance)}</Typography></Grid>
                          
                          <Grid item xs={8}><Typography>HRA ({cityForHRA}):</Typography></Grid>
                          <Grid item xs={4}><Typography align="right">{formatCurrency(taxationData.salary.hra)}</Typography></Grid>
                          
                          <Grid item xs={8}><Typography>Special Allowance:</Typography></Grid>
                          <Grid item xs={4}><Typography align="right">{formatCurrency(taxationData.salary.special_allowance)}</Typography></Grid>
                          
                          <Grid item xs={8}><Typography>Bonus:</Typography></Grid>
                          <Grid item xs={4}><Typography align="right">{formatCurrency(taxationData.salary.bonus)}</Typography></Grid>
                        </Grid>
                      </CardContent>
                    </Card>

                    <Card sx={{ mb: 2 }}>
                      <CardContent>
                        <Typography variant="h6" color="primary" gutterBottom>
                          Other Income
                        </Typography>
                        <Grid container spacing={1}>
                          <Grid item xs={8}><Typography>Interest (All Sources):</Typography></Grid>
                          <Grid item xs={4}><Typography align="right">
                            {formatCurrency(
                              taxationData.other_sources.interest_savings + 
                              taxationData.other_sources.interest_fd + 
                              taxationData.other_sources.interest_rd +
                              taxationData.other_sources.other_interest
                            )}
                          </Typography></Grid>
                          
                          <Grid item xs={8}><Typography>Dividend Income:</Typography></Grid>
                          <Grid item xs={4}><Typography align="right">{formatCurrency(taxationData.other_sources.dividend_income)}</Typography></Grid>
                          
                          <Grid item xs={8}><Typography>Gifts:</Typography></Grid>
                          <Grid item xs={4}><Typography align="right">{formatCurrency(taxationData.other_sources.gifts)}</Typography></Grid>
                          
                          <Grid item xs={8}><Typography>Other Income:</Typography></Grid>
                          <Grid item xs={4}><Typography align="right">{formatCurrency(taxationData.other_sources.other_income)}</Typography></Grid>
                          
                          <Grid item xs={8}><Typography>Short Term Capital Gains:</Typography></Grid>
                          <Grid item xs={4}><Typography align="right">
                            {formatCurrency(
                              taxationData.capital_gains.stcg_111a + 
                              taxationData.capital_gains.stcg_any_other_asset +
                              taxationData.capital_gains.stcg_debt_mutual_fund
                            )}
                          </Typography></Grid>
                          
                          <Grid item xs={8}><Typography>Long Term Capital Gains:</Typography></Grid>
                          <Grid item xs={4}><Typography align="right">
                            {formatCurrency(
                              taxationData.capital_gains.ltcg_112a + 
                              taxationData.capital_gains.ltcg_any_other_asset +
                              taxationData.capital_gains.ltcg_debt_mutual_fund
                            )}
                          </Typography></Grid>
                        </Grid>
                      </CardContent>
                    </Card>
                  </Grid>

                  <Grid item xs={12} md={6}>
                    {taxationData.regime === 'old' && (
                      <Card sx={{ mb: 2 }}>
                        <CardContent>
                          <Typography variant="h6" color="primary" gutterBottom>
                            Deductions
                          </Typography>
                          <Grid container spacing={1}>
                            <Grid item xs={8}><Typography>Section 80C (Total):</Typography></Grid>
                            <Grid item xs={4}><Typography align="right">{formatCurrency(
                              taxationData.deductions.section_80c_lic +
                              taxationData.deductions.section_80c_epf +
                              taxationData.deductions.section_80c_ssp +
                              taxationData.deductions.section_80c_nsc +
                              taxationData.deductions.section_80c_ulip +
                              taxationData.deductions.section_80c_tsmf +
                              taxationData.deductions.section_80c_tffte2c +
                              taxationData.deductions.section_80c_paphl +
                              taxationData.deductions.section_80c_sdpphp +
                              taxationData.deductions.section_80c_tsfdsb +
                              taxationData.deductions.section_80c_scss +
                              taxationData.deductions.section_80c_others
                            )}</Typography></Grid>
                            
                            <Grid item xs={8}><Typography>Section 80CCC/CCD (NPS):</Typography></Grid>
                            <Grid item xs={4}><Typography align="right">{formatCurrency(
                              taxationData.deductions.section_80ccc_ppic +
                              taxationData.deductions.section_80ccd_1_nps +
                              taxationData.deductions.section_80ccd_1b_additional +
                              taxationData.deductions.section_80ccd_2_enps
                            )}</Typography></Grid>
                            
                            <Grid item xs={8}><Typography>Section 80D (Health):</Typography></Grid>
                            <Grid item xs={4}><Typography align="right">{formatCurrency(
                              taxationData.deductions.section_80d_hisf +
                              taxationData.deductions.section_80d_phcs +
                              taxationData.deductions.section_80d_hi_parent
                            )}</Typography></Grid>
                            
                            <Grid item xs={8}><Typography>Section 24B (Home Loan):</Typography></Grid>
                            <Grid item xs={4}><Typography align="right">{formatCurrency(taxationData.deductions.section_24b)}</Typography></Grid>
                            
                            <Grid item xs={8}><Typography>Other Deductions:</Typography></Grid>
                            <Grid item xs={4}><Typography align="right">
                              {formatCurrency(
                                taxationData.deductions.section_80dd +
                                taxationData.deductions.section_80ddb +
                                taxationData.deductions.section_80eeb +
                                taxationData.deductions.section_80g +
                                taxationData.deductions.section_80g_100_wo_ql +
                                taxationData.deductions.section_80g_50_wo_ql +
                                taxationData.deductions.section_80ggc +
                                taxationData.deductions.section_80u
                              )}
                            </Typography></Grid>
                          </Grid>
                        </CardContent>
                      </Card>
                    )}

                    <Card sx={{ mb: 2, bgcolor: '#f5f5f5' }}>
                      <CardContent>
                        <Typography variant="h6" color="primary" gutterBottom>
                          Tax Calculation
                        </Typography>
                        
                        {calculatedTax !== null ? (
                          <Box>
                            <Typography variant="h5" align="center" sx={{ my: 2 }}>
                              Estimated Tax: {formatCurrency(calculatedTax)}
                            </Typography>
                          </Box>
                        ) : (
                          <Box sx={{ textAlign: 'center', my: 2 }}>
                            <Button 
                              variant="contained" 
                              color="secondary"
                              onClick={handleCalculateTax}
                              disabled={submitting}
                            >
                              {submitting ? <CircularProgress size={24} /> : 'Calculate Tax'}
                            </Button>
                          </Box>
                        )}
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              </Box>
            )}

            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
              <Button
                variant="outlined"
                onClick={handleBack}
                disabled={activeStep === 0}
              >
                Back
              </Button>
              
              <Box>
                {activeStep === steps.length - 1 ? (
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleSubmit}
                    disabled={submitting || calculatedTax === null}
                  >
                    {submitting ? <CircularProgress size={24} /> : 'Submit Declaration'}
                  </Button>
                ) : (
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleNext}
                  >
                    Next
                  </Button>
                )}
              </Box>
            </Box>
          </Box>
        </Paper>
      </Box>
    </PageLayout>
  );
};

export default TaxDeclaration; 