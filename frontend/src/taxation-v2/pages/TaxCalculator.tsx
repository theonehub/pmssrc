import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Stepper,
  Step,
  StepLabel,
  Alert,
  Chip,
  useMediaQuery,
  useTheme
} from '@mui/material';
import {
  Calculate,
  AccountBalance,
  Receipt,
  ArrowBack,
  ArrowForward,
  Save
} from '@mui/icons-material';

import { Card, Button, Modal } from '../components/ui';
import { IncomeSourceForm } from '../components/forms/IncomeSourceForm';
import { DeductionsForm } from '../components/forms/DeductionsForm';
import { useTaxCalculation } from '../../shared/hooks/useTaxCalculation';
import { TaxRegime } from '../../shared/types/api';
import { formatCurrency, formatPercentage } from '../../shared/utils/formatting';

// =============================================================================
// CALCULATOR STEPS
// =============================================================================

const calculatorSteps = [
  {
    label: 'Income Sources',
    description: 'Add your income from various sources',
    icon: AccountBalance,
  },
  {
    label: 'Deductions',
    description: 'Claim available tax deductions',
    icon: Receipt,
  },
  {
    label: 'Calculate & Compare',
    description: 'View tax calculation and regime comparison',
    icon: Calculate,
  },
];

// =============================================================================
// TAX CALCULATOR COMPONENT
// =============================================================================

export const TaxCalculator: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  // State management
  const [activeStep, setActiveStep] = useState(0);
  const [showIncomeModal, setShowIncomeModal] = useState(false);
  const [editingIncome, setEditingIncome] = useState<any>(null);
  const [selectedRegime, setSelectedRegime] = useState<TaxRegime>('new');
  const [incomeSources, setIncomeSources] = useState<any[]>([]);
  const [deductions, setDeductions] = useState<any>({});

  // Hooks
  const { getQuickTaxEstimate } = useTaxCalculation();

  // =============================================================================
  // STEP HANDLERS
  // =============================================================================

  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  // =============================================================================
  // INCOME HANDLERS
  // =============================================================================

  const addIncomeSource = (incomeData: any) => {
    const newIncome = { ...incomeData, id: Date.now().toString() };
    setIncomeSources(prev => [...prev, newIncome]);
  };

  const updateIncomeSource = (id: string, incomeData: any) => {
    setIncomeSources(prev => 
      prev.map(income => income.id === id ? { ...incomeData, id } : income)
    );
  };

  const handleAddIncome = () => {
    setEditingIncome(null);
    setShowIncomeModal(true);
  };

  const handleEditIncome = (income: any) => {
    setEditingIncome(income);
    setShowIncomeModal(true);
  };

  const handleIncomeSubmit = (incomeData: any) => {
    if (editingIncome) {
      updateIncomeSource(editingIncome.id, incomeData);
    } else {
      addIncomeSource(incomeData);
    }
    setShowIncomeModal(false);
    setEditingIncome(null);
  };

  // =============================================================================
  // CALCULATION HANDLERS
  // =============================================================================

  const getTotalIncome = () => {
    return incomeSources.reduce((sum, source) => sum + source.annual_amount, 0);
  };

  const getEstimatedTax = () => {
    const totalIncome = getTotalIncome();
    if (totalIncome === 0) return 0;
    
    const estimate = getQuickTaxEstimate(totalIncome, selectedRegime);
    return estimate;
  };

  // =============================================================================
  // RENDER HELPERS
  // =============================================================================

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return renderIncomeStep();
      case 1:
        return renderDeductionsStep();
      case 2:
        return renderCalculationStep();
      default:
        return null;
    }
  };

  const renderIncomeStep = () => (
    <Card title="Income Sources" variant="outlined">
      <Box sx={{ mb: 3 }}>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Add all your income sources for accurate tax calculation
        </Typography>
        
        {incomeSources.length === 0 ? (
          <Alert severity="info" sx={{ mb: 2 }}>
            No income sources added yet. Click "Add Income Source" to get started.
          </Alert>
        ) : (
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2, mb: 2 }}>
            {incomeSources.map((income, index) => (
              <Card
                key={index}
                variant="outlined"
                onClick={() => handleEditIncome(income)}
                sx={{ cursor: 'pointer' }}
              >
                <Box sx={{ p: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    {income.description}
                  </Typography>
                  <Typography variant="h6" color="primary">
                    {formatCurrency(income.annual_amount)}
                  </Typography>
                  <Chip
                    label={income.income_type.replace('_', ' ').toUpperCase()}
                    size="small"
                    variant="outlined"
                    sx={{ mt: 1 }}
                  />
                </Box>
              </Card>
            ))}
          </Box>
        )}
        
        <Button
          variant="outlined"
          onClick={handleAddIncome}
          startIcon={<AccountBalance />}
          fullWidth={isMobile}
        >
          Add Income Source
        </Button>
      </Box>
      
      {incomeSources.length > 0 && (
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
          <Typography variant="h6">
            Total Income: {formatCurrency(getTotalIncome())}
          </Typography>
          <Button onClick={handleNext} variant="contained" endIcon={<ArrowForward />}>
            Continue to Deductions
          </Button>
        </Box>
      )}
    </Card>
  );

  const renderDeductionsStep = () => (
    <Card title="Tax Deductions" variant="outlined">
      <Box sx={{ mb: 3 }}>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Choose your tax regime and claim available deductions
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
          <Button
            variant={selectedRegime === 'old' ? 'contained' : 'outlined'}
            onClick={() => setSelectedRegime('old')}
          >
            Old Regime (With Deductions)
          </Button>
          <Button
            variant={selectedRegime === 'new' ? 'contained' : 'outlined'}
            onClick={() => setSelectedRegime('new')}
          >
            New Regime (Lower Rates)
          </Button>
        </Box>
        
        <DeductionsForm
          initialData={deductions}
          onSubmit={setDeductions}
          taxRegime={selectedRegime}
          totalIncome={getTotalIncome()}
        />
      </Box>
      
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
        <Button onClick={handleBack} variant="outlined" startIcon={<ArrowBack />}>
          Back to Income
        </Button>
        <Button onClick={handleNext} variant="contained" endIcon={<ArrowForward />}>
          Calculate Tax
        </Button>
      </Box>
    </Card>
  );

  const renderCalculationStep = () => {
    const totalIncome = getTotalIncome();
    const estimatedTax = getEstimatedTax();
    const netIncome = totalIncome - estimatedTax;
    const effectiveRate = totalIncome > 0 ? (estimatedTax / totalIncome) * 100 : 0;

    return (
      <Box>
        <Card title="Tax Calculation Results" variant="outlined" sx={{ mb: 3 }}>
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr 1fr' }, gap: 3 }}>
            <Card variant="info">
              <Box sx={{ textAlign: 'center', p: 2 }}>
                <Typography variant="h4" fontWeight="bold" color="primary">
                  {formatCurrency(estimatedTax)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Estimated Tax Liability
                </Typography>
              </Box>
            </Card>
            
            <Card variant="success">
              <Box sx={{ textAlign: 'center', p: 2 }}>
                <Typography variant="h4" fontWeight="bold" color="success.main">
                  {formatCurrency(netIncome)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Net Income (After Tax)
                </Typography>
              </Box>
            </Card>
            
            <Card variant="outlined">
              <Box sx={{ textAlign: 'center', p: 2 }}>
                <Typography variant="h4" fontWeight="bold">
                  {formatPercentage(effectiveRate)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Effective Tax Rate
                </Typography>
              </Box>
            </Card>
          </Box>
          
          <Alert severity="info" sx={{ mt: 3 }}>
            This is a quick estimate based on {selectedRegime} tax regime. 
            For detailed calculation, please use our comprehensive calculator.
          </Alert>
        </Card>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
          <Button onClick={handleBack} variant="outlined" startIcon={<ArrowBack />}>
            Back to Deductions
          </Button>
          <Button variant="contained" startIcon={<Save />}>
            Save Calculation
          </Button>
        </Box>
      </Box>
    );
  };

  // =============================================================================
  // RENDER MAIN COMPONENT
  // =============================================================================

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          Tax Calculator 2024-25
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Calculate your income tax with our comprehensive calculator
        </Typography>
      </Box>

      {/* Progress Stepper */}
      <Card sx={{ mb: 4 }}>
        <Stepper activeStep={activeStep} orientation={isMobile ? 'vertical' : 'horizontal'}>
          {calculatorSteps.map((step, index) => (
            <Step key={step.label} completed={activeStep > index}>
              <StepLabel>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <step.icon />
                  <Box>
                    <Typography variant="subtitle2">{step.label}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {step.description}
                    </Typography>
                  </Box>
                </Box>
              </StepLabel>
            </Step>
          ))}
        </Stepper>
      </Card>

      {/* Step Content */}
      {renderStepContent(activeStep)}

      {/* Income Source Modal */}
      <Modal
        open={showIncomeModal}
        onClose={() => setShowIncomeModal(false)}
        title={editingIncome ? 'Edit Income Source' : 'Add Income Source'}
        size="large"
      >
        <IncomeSourceForm
          initialData={editingIncome}
          onSubmit={handleIncomeSubmit}
          onCancel={() => setShowIncomeModal(false)}
          mode={editingIncome ? 'edit' : 'create'}
        />
      </Modal>
    </Container>
  );
};

export default TaxCalculator; 