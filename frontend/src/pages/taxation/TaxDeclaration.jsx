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
  InputLabel
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
    regime: 'old',
    tax_year: getCurrentFinancialYear(),
    salary: {
      basic: 0,
      dearness_allowance: 0,
      hra: 0,
      special_allowance: 0,
      bonus: 0,
      perquisites: {
        company_car: 0,
        rent_free_accommodation: 0,
        concessional_loan: 0,
        gift_vouchers: 0
      }
    },
    other_sources: {
      interest_savings: 0,
      interest_fd: 0,
      interest_rd: 0,
      dividend_income: 0,
      rental_income: 0,
      other_misc: 0
    },
    capital_gains: {
      stcg_111a: 0,
      ltcg_112a: 0
    },
    deductions: {
      section_80c: 0,
      section_80d: 0,
      section_24b: 0,
      section_80e: 0,
      section_80g: 0,
      section_80tta: 0
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
                              label="Rental Income"
                              type="text"
                              value={formatIndianNumber(taxationData.other_sources.rental_income)}
                              onChange={(e) => handleInputChange('other_sources', 'rental_income', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleFocus('other_sources', 'rental_income', e.target.value)}
                            />
                          </Grid>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Other Miscellaneous Income"
                              type="text"
                              value={formatIndianNumber(taxationData.other_sources.other_misc)}
                              onChange={(e) => handleInputChange('other_sources', 'other_misc', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleFocus('other_sources', 'other_misc', e.target.value)}
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
                        <Grid container spacing={3}>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Short Term Capital Gains (Section 111A)"
                              type="text"
                              value={formatIndianNumber(taxationData.capital_gains.stcg_111a)}
                              onChange={(e) => handleInputChange('capital_gains', 'stcg_111a', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleFocus('capital_gains', 'stcg_111a', e.target.value)}
                            />
                          </Grid>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Long Term Capital Gains (Section 112A)"
                              type="text"
                              value={formatIndianNumber(taxationData.capital_gains.ltcg_112a)}
                              onChange={(e) => handleInputChange('capital_gains', 'ltcg_112a', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              onFocus={(e) => handleFocus('capital_gains', 'ltcg_112a', e.target.value)}
                            />
                          </Grid>
                        </Grid>
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
                        <Grid container spacing={3}>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Section 80C (PPF, ELSS, etc.)"
                              type="text"
                              value={formatIndianNumber(taxationData.deductions.section_80c)}
                              onChange={(e) => handleInputChange('deductions', 'section_80c', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              disabled={taxationData.regime === 'new'}
                              helperText="Max deduction: ₹1,50,000"
                              onFocus={(e) => handleFocus('deductions', 'section_80c', e.target.value)}
                            />
                          </Grid>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Section 80D (Health Insurance)"
                              type="text"
                              value={formatIndianNumber(taxationData.deductions.section_80d)}
                              onChange={(e) => handleInputChange('deductions', 'section_80d', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              disabled={taxationData.regime === 'new'}
                              helperText="Max deduction: ₹25,000 (₹50,000 for senior citizens)"
                              onFocus={(e) => handleFocus('deductions', 'section_80d', e.target.value)}
                            />
                          </Grid>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Section 24B (Home Loan Interest)"
                              type="text"
                              value={formatIndianNumber(taxationData.deductions.section_24b)}
                              onChange={(e) => handleInputChange('deductions', 'section_24b', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              disabled={taxationData.regime === 'new'}
                              helperText="Max deduction: ₹2,00,000"
                              onFocus={(e) => handleFocus('deductions', 'section_24b', e.target.value)}
                            />
                          </Grid>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Section 80E (Education Loan Interest)"
                              type="text"
                              value={formatIndianNumber(taxationData.deductions.section_80e)}
                              onChange={(e) => handleInputChange('deductions', 'section_80e', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              disabled={taxationData.regime === 'new'}
                              helperText="No upper limit"
                              onFocus={(e) => handleFocus('deductions', 'section_80e', e.target.value)}
                            />
                          </Grid>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Section 80G (Donations)"
                              type="text"
                              value={formatIndianNumber(taxationData.deductions.section_80g)}
                              onChange={(e) => handleInputChange('deductions', 'section_80g', e.target.value)}
                              InputProps={{ startAdornment: '₹' }}
                              disabled={taxationData.regime === 'new'}
                              onFocus={(e) => handleFocus('deductions', 'section_80g', e.target.value)}
                            />
                          </Grid>
                          <Grid item xs={12} md={6}>
                            <TextField
                              fullWidth
                              label="Section 80TTA (Savings Account Interest)"
                              type="text"
                              value={formatIndianNumber(taxationData.deductions.section_80tta)}
                              InputProps={{ startAdornment: '₹' }}
                              disabled={true}
                              helperText="Auto-filled from savings interest (Max: ₹10,000)"
                              onFocus={(e) => handleFocus('deductions', 'section_80tta', e.target.value)}
                            />
                          </Grid>
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
                              taxationData.other_sources.interest_rd
                            )}
                          </Typography></Grid>
                          
                          <Grid item xs={8}><Typography>Dividend Income:</Typography></Grid>
                          <Grid item xs={4}><Typography align="right">{formatCurrency(taxationData.other_sources.dividend_income)}</Typography></Grid>
                          
                          <Grid item xs={8}><Typography>Rental Income:</Typography></Grid>
                          <Grid item xs={4}><Typography align="right">{formatCurrency(taxationData.other_sources.rental_income)}</Typography></Grid>
                          
                          <Grid item xs={8}><Typography>Capital Gains:</Typography></Grid>
                          <Grid item xs={4}><Typography align="right">
                            {formatCurrency(
                              taxationData.capital_gains.stcg_111a + 
                              taxationData.capital_gains.ltcg_112a
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
                            <Grid item xs={8}><Typography>Section 80C:</Typography></Grid>
                            <Grid item xs={4}><Typography align="right">{formatCurrency(taxationData.deductions.section_80c)}</Typography></Grid>
                            
                            <Grid item xs={8}><Typography>Section 80D:</Typography></Grid>
                            <Grid item xs={4}><Typography align="right">{formatCurrency(taxationData.deductions.section_80d)}</Typography></Grid>
                            
                            <Grid item xs={8}><Typography>Section 24B:</Typography></Grid>
                            <Grid item xs={4}><Typography align="right">{formatCurrency(taxationData.deductions.section_24b)}</Typography></Grid>
                            
                            <Grid item xs={8}><Typography>Other Deductions:</Typography></Grid>
                            <Grid item xs={4}><Typography align="right">
                              {formatCurrency(
                                taxationData.deductions.section_80e + 
                                taxationData.deductions.section_80g + 
                                taxationData.deductions.section_80tta
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