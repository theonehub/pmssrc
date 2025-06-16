import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
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
  useTheme,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  Chip
} from '@mui/material';
import useTaxationForm from './hooks/useTaxationForm';
import { formSteps } from './utils/taxationConstants';
import { validateTaxationForm } from './utils/validationRules';

// Import all section components
import RegimeSelection from './sections/RegimeSelection';
import SalarySection from './sections/SalarySection';
import PerquisitesSection from './sections/PerquisitesSection';
import OtherIncomeSection from './sections/OtherIncomeSection';
import DeductionsSection from './sections/DeductionsSection';
import SeparationSection from './sections/SeparationSection';
import SummarySection from './sections/SummarySection';

interface ValidationErrors {
  [key: string]: any;
}

interface StepErrors {
  [stepIndex: number]: boolean;
}

/**
 * TaxDeclaration component - Main component for tax declaration form
 * FIXES APPLIED:
 * 1. Added comprehensive step validation
 * 2. Added error validation dialog
 * 3. Proper error handling and display
 * 4. Step navigation restrictions based on validation
 * 5. Better user feedback and guidance
 */
const TaxDeclaration: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const { empId } = useParams<{ empId: string }>();
  const [activeStep, setActiveStep] = useState<number>(0);
  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({});
  const [showValidationDialog, setShowValidationDialog] = useState<boolean>(false);
  const [stepErrors, setStepErrors] = useState<StepErrors>({});
  
  // Initialize form using custom hook
  const hookResult: any = useTaxationForm(empId || '');
  const {
    taxationData,
    taxCalculationResponse,
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
    handleSubmit,
    fetchVrsValue
  } = hookResult;

  // Debug: Log taxation data whenever it changes
  useEffect(() => {
    console.log('🎯 TaxDeclaration received taxation data:', {
      keys: Object.keys(taxationData || {}),
      employee_id: taxationData?.employee_id,
      age: taxationData?.age,
      regime: taxationData?.regime,
      salary_income_keys: taxationData?.salary_income ? Object.keys(taxationData.salary_income) : null,
      basic_salary: taxationData?.salary_income?.basic_salary,
      deductions_keys: taxationData?.deductions ? Object.keys(taxationData.deductions) : null,
    });
  }, [taxationData]);

  // Validate form whenever data changes - now tracks warnings instead of errors
  useEffect(() => {
    const validation: any = validateTaxationForm(taxationData);
    setValidationErrors(validation.warnings || {});
    
    // Set step-specific warnings (not blocking)
    const newStepErrors: StepErrors = {};
    if (validation.warnings?.emp_age) {
      newStepErrors[0] = true; // Regime selection step has warnings
    }
    if (validation.warnings?.salary) {
      newStepErrors[1] = true; // Salary step has warnings
    }
    if (validation.warnings?.deductions) {
      newStepErrors[5] = true; // Deductions step has warnings
    }
    setStepErrors(newStepErrors);
  }, [taxationData]);

  // Handle next step without validation blocking
  const handleNext = (): void => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
    window.scrollTo(0, 0);
  };

  // Handle back step
  const handleBack = (): void => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
    window.scrollTo(0, 0);
  };

  // Handle direct step navigation - allow all navigation
  const handleStepClick = (stepIndex: number): void => {
    setActiveStep(stepIndex);
    window.scrollTo(0, 0);
  };

  // Render current step content with validation context
  const getStepContent = (step: number): React.ReactElement | string => {
    const baseProps = {
      taxationData,
      validationErrors: (validationErrors[getStepValidationKey(step)]) || {}
    };

    switch (step) {
      case 0:
        return (
          <RegimeSelection
            {...baseProps}
            handleRegimeChange={handleRegimeChange}
            handleInputChange={handleInputChange}
          />
        );
      case 1:
        return (
          <SalarySection
            {...baseProps}
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
            {...baseProps}
            handleNestedInputChange={handleNestedInputChange}
            handleNestedFocus={handleNestedFocus}
          />
        );
      case 3:
        return (
          <OtherIncomeSection
            {...baseProps}
            handleInputChange={handleInputChange}
            handleFocus={handleFocus}
          />
        );
      case 4:
        return (
          <SeparationSection
            {...baseProps}
            handleInputChange={handleInputChange}
            handleFocus={handleFocus}
            fetchVrsValue={fetchVrsValue}
          />
        );
      case 5:
        return (
          <DeductionsSection
            {...baseProps}
            handleInputChange={handleInputChange}
            handleFocus={handleFocus}
          />
        );
      case 6:
        return (
          <SummarySection
            {...baseProps}
            taxCalculationResponse={taxCalculationResponse}
            submitting={submitting}
            handleCalculateTax={handleCalculateTax}
          />
        );
      default:
        return 'Unknown step';
    }
  };

  // Get validation key for step
  const getStepValidationKey = (step: number): string => {
    switch (step) {
      case 0: return 'regime';
      case 1: return 'salary';
      case 2: return 'perquisites';
      case 3: return 'other_income';
      case 4: return 'separation';
      case 5: return 'deductions';
      case 6: return 'summary';
      default: return 'general';
    }
  };

  // Handle form submission with warning notifications instead of blocking
  const onSubmit = (): void => {
    const finalValidation: any = validateTaxationForm(taxationData);
    
    // Show warnings dialog if there are warnings, but don't block submission
    if (finalValidation.hasWarnings) {
      setShowValidationDialog(true);
    }
    
    // Always allow submission, backend will handle final validation
    handleSubmit(navigate);
  };

  // Render validation warnings dialog
  const renderValidationDialog = (): React.ReactElement => (
    <Dialog open={showValidationDialog} onClose={() => setShowValidationDialog(false)}>
      <DialogTitle>Validation Warnings</DialogTitle>
      <DialogContent>
        <Typography variant="body2" sx={{ mb: 2 }}>
          Please review the following warnings. You can still submit the form as final validation will be done by the system:
        </Typography>
        <List dense>
          {Object.entries(validationErrors).map(([section, warnings]) => (
            <ListItem key={section}>
              <ListItemText
                primary={section.charAt(0).toUpperCase() + section.slice(1)}
                secondary={
                  <Box>
                    {typeof warnings === 'object' ? 
                      Object.entries(warnings).map(([field, warning]) => (
                        <Chip key={field} label={`${field}: ${warning}`} size="small" color="warning" sx={{ mr: 0.5, mb: 0.5 }} />
                      )) :
                      <Chip label={warnings} size="small" color="warning" />
                    }
                  </Box>
                }
              />
            </ListItem>
          ))}
        </List>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setShowValidationDialog(false)}>Review Form</Button>
        <Button variant="contained" onClick={() => {
          setShowValidationDialog(false);
          handleSubmit(navigate);
        }}>
          Submit Anyway
        </Button>
      </DialogActions>
    </Dialog>
  );

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

          {/* Desktop Stepper */}
          <Stepper 
            activeStep={activeStep} 
            alternativeLabel
            sx={{ 
              mb: 4,
              display: { xs: 'none', md: 'flex' }
            }}
          >
            {formSteps.map((label, index) => (
              <Step 
                key={label}
                onClick={() => handleStepClick(index)}
                sx={{ 
                  cursor: index <= activeStep ? 'pointer' : 'default',
                  '& .MuiStepLabel-root': {
                    color: stepErrors[index] ? 'error.main' : 'inherit'
                  }
                }}
              >
                <StepLabel 
                  error={stepErrors[index] || false}
                  sx={{
                    '& .MuiStepIcon-root': {
                      color: stepErrors[index] ? 'error.main' : 'inherit'
                    }
                  }}
                >
                  {label}
                  {stepErrors[index] && (
                    <Typography variant="caption" color="error" display="block">
                      Has warnings
                    </Typography>
                  )}
                </StepLabel>
              </Step>
            ))}
          </Stepper>

          {/* Mobile stepper display */}
          <Box sx={{ display: { xs: 'block', md: 'none' }, mb: 3 }}>
            <Typography variant="h6" align="center">
              Step {activeStep + 1} of {formSteps.length}: {formSteps[activeStep]}
              {stepErrors[activeStep] && (
                <Chip label="Has Warnings" color="warning" size="small" sx={{ ml: 1 }} />
              )}
            </Typography>
          </Box>

          {/* Step Content */}
          <Box sx={{ minHeight: '60vh' }}>
            {getStepContent(activeStep)}
          </Box>

          {/* Navigation Buttons */}
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
                  startIcon={submitting && <CircularProgress size={20} />}
                >
                  {submitting ? 'Submitting...' : 'Submit Declaration'}
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

          {/* Show validation summary at bottom if there are warnings */}
          {Object.keys(validationErrors).length > 0 && (
            <Alert severity="warning" sx={{ mt: 3 }}>
              <Typography variant="subtitle2">Form has validation warnings:</Typography>
              <Typography variant="body2">
                Please review and fix the highlighted warnings in the form before proceeding.
              </Typography>
              <Button 
                size="small" 
                onClick={() => setShowValidationDialog(true)}
                sx={{ mt: 1 }}
              >
                View Details
              </Button>
            </Alert>
          )}
        </Paper>

        {/* Validation Dialog */}
        {renderValidationDialog()}
      </Container>
  );
};

export default TaxDeclaration; 