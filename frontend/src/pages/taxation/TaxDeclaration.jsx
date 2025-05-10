import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import PageLayout from '../../layout/PageLayout';
import {
  Box,
  Container,
  Stepper,
  Step,
  StepLabel,
  Button,
  Typography,
  CircularProgress,
  Paper,
  Alert,
  useTheme
} from '@mui/material';
import useTaxationForm from './hooks/useTaxationForm';
import { formSteps } from './utils/taxationConstants';

// Import all section components
import RegimeSelection from './sections/RegimeSelection';
import SalarySection from './sections/SalarySection';
import PerquisitesSection from './sections/PerquisitesSection';
import OtherIncomeSection from './sections/OtherIncomeSection';
import DeductionsSection from './sections/DeductionsSection';
import SummarySection from './sections/SummarySection';

/**
 * TaxDeclaration component - Main component for tax declaration form
 * @returns {JSX.Element} Tax declaration form
 */
const TaxDeclaration = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const { empId } = useParams();
  const [activeStep, setActiveStep] = useState(0);
  
  // Initialize form using custom hook
  const {
    taxationData,
    calculatedTax,
    loading,
    submitting,
    error,
    success,
    cityForHRA,
    autoComputeHRA,
    setAutoComputeHRA,
    handleInputChange,
    handleNestedInputChange,
    handleRegimeChange,
    handleFocus,
    handleNestedFocus,
    computeHRA,
    handleCityChange,
    handleHRAChange,
    handleCalculateTax,
    handleSubmit
  } = useTaxationForm(empId);

  // Handle next step
  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
    window.scrollTo(0, 0);
  };

  // Handle back step
  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
    window.scrollTo(0, 0);
  };

  // Render current step content
  const getStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <RegimeSelection
            taxationData={taxationData}
            handleRegimeChange={handleRegimeChange}
          />
        );
      case 1:
        return (
          <SalarySection
            taxationData={taxationData}
            handleInputChange={handleInputChange}
            handleFocus={handleFocus}
            cityForHRA={cityForHRA}
            handleCityChange={handleCityChange}
            autoComputeHRA={autoComputeHRA}
            setAutoComputeHRA={setAutoComputeHRA}
            handleHRAChange={handleHRAChange}
            computeHRA={computeHRA}
          />
        );
      case 2:
        return (
          <PerquisitesSection
            taxationData={taxationData}
            handleNestedInputChange={handleNestedInputChange}
            handleNestedFocus={handleNestedFocus}
          />
        );
      case 3:
        return (
          <OtherIncomeSection
            taxationData={taxationData}
            handleInputChange={handleInputChange}
            handleFocus={handleFocus}
          />
        );
      case 4:
        return (
          <DeductionsSection
            taxationData={taxationData}
            handleInputChange={handleInputChange}
            handleFocus={handleFocus}
          />
        );
      case 5:
        return (
          <SummarySection
            taxationData={taxationData}
            calculatedTax={calculatedTax}
            submitting={submitting}
            handleCalculateTax={handleCalculateTax}
          />
        );
      default:
        return 'Unknown step';
    }
  };

  // Handle form submission
  const onSubmit = () => {
    handleSubmit(navigate);
  };

  // If loading, show loading spinner
  if (loading) {
    return (
      <Box 
        sx={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '80vh' 
        }}
      >
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <PageLayout title="Tax Declaration">
    <Container maxWidth="lg" sx={{ mb: 8 }}>
      <Paper 
        elevation={0} 
        sx={{ 
          p: { xs: 2, md: 3 }, 
          border: `1px solid ${theme.palette.divider}`,
          borderRadius: 2,
          mt: 3
        }}
      >
        <Typography variant="h4" align="center" gutterBottom>
          Income Tax Declaration
        </Typography>
        <Typography variant="subtitle1" align="center" paragraph>
          Financial Year: {taxationData.tax_year}
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 3 }}>
            {success}
          </Alert>
        )}

        <Stepper 
          activeStep={activeStep} 
          alternativeLabel
          sx={{ 
            mb: 4,
            display: { xs: 'none', md: 'flex' }
          }}
        >
          {formSteps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {/* Mobile stepper display */}
        <Box sx={{ display: { xs: 'block', md: 'none' }, mb: 3 }}>
          <Typography variant="h6" align="center">
            Step {activeStep + 1}: {formSteps[activeStep]}
          </Typography>
        </Box>

        {getStepContent(activeStep)}

        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
          <Button
            variant="outlined"
            disabled={activeStep === 0}
            onClick={handleBack}
          >
            Back
          </Button>

          <Box>
            {activeStep === formSteps.length - 1 ? (
              <Button
                variant="contained"
                color="primary"
                onClick={onSubmit}
                disabled={submitting}
              >
                {submitting ? (
                  <CircularProgress size={24} />
                ) : (
                  'Submit Declaration'
                )}
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
      </Paper>
    </Container>
    </PageLayout>
  );
};

export default TaxDeclaration; 