import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Alert,
  LinearProgress
} from '@mui/material';
import {
  Savings,
  HealthAndSafety,
  AccountBalance,
  Info
} from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

import { Card, CurrencyInput, Button } from '../ui';
import { DeductionsDTO, TaxRegime } from '../../../shared/types/api';
import { DEDUCTION_LIMITS } from '../../../shared/constants/taxation';

// =============================================================================
// VALIDATION SCHEMA
// =============================================================================

const deductionsSchema = z.object({
  // Section 80C
  ppf: z.number().min(0).max(150000),
  epf: z.number().min(0).max(150000),
  elss: z.number().min(0).max(150000),
  life_insurance: z.number().min(0).max(150000),
  home_loan_principal: z.number().min(0).max(150000),
  nsc: z.number().min(0).max(150000),
  tax_saver_fd: z.number().min(0).max(150000),
  tuition_fees: z.number().min(0).max(150000),
  
  // Section 80D
  health_insurance_self: z.number().min(0).max(25000),
  health_insurance_parents: z.number().min(0).max(50000),
  preventive_health_checkup: z.number().min(0).max(5000),
  
  // Other Deductions
  section_80E: z.number().min(0), // Education loan interest
  section_80G: z.number().min(0), // Donations
  section_80TTA: z.number().min(0).max(10000), // Savings account interest
  section_80TTB: z.number().min(0).max(50000), // Senior citizen savings interest
  
  // Additional
  nps_80CCD1B: z.number().min(0).max(50000),
  nps_80CCD2: z.number().min(0),
  
  tax_regime: z.enum(['old', 'new']),
});

type DeductionsFormData = z.infer<typeof deductionsSchema>;

// Extended DTO for form handling
interface FormDeductionsDTO extends DeductionsDTO {
  id?: string;
  section_80C_total?: number;
  section_80D_total?: number;
  total_deductions?: number;
  created_at?: string;
  updated_at?: string;
}

// =============================================================================
// COMPONENT INTERFACES
// =============================================================================

export interface DeductionsFormProps {
  initialData?: Partial<FormDeductionsDTO>;
  onSubmit: (data: FormDeductionsDTO) => void;
  onCancel?: () => void;
  loading?: boolean;
  taxRegime?: TaxRegime;
  totalIncome?: number;
}

// =============================================================================
// DEDUCTIONS FORM COMPONENT
// =============================================================================

export const DeductionsForm: React.FC<DeductionsFormProps> = ({
  initialData,
  onSubmit,
  onCancel,
  loading = false,
  taxRegime = 'old',
  totalIncome = 0
}) => {
  const [section80CTotal, setSection80CTotal] = useState(0);
  const [section80DTotal, setSection80DTotal] = useState(0);
  const [totalDeductions, setTotalDeductions] = useState(0);
  
  const {
    control,
    handleSubmit,
    watch,
    formState: { isValid }
  } = useForm<DeductionsFormData>({
    resolver: zodResolver(deductionsSchema),
    defaultValues: {
      tax_regime: taxRegime,
      ppf: 0,
      epf: 0,
      elss: 0,
      life_insurance: 0,
      home_loan_principal: 0,
      nsc: 0,
      tax_saver_fd: 0,
      tuition_fees: 0,
      health_insurance_self: 0,
      health_insurance_parents: 0,
      preventive_health_checkup: 0,
      section_80E: 0,
      section_80G: 0,
      section_80TTA: 0,
      section_80TTB: 0,
      nps_80CCD1B: 0,
      nps_80CCD2: 0,
      ...initialData
    }
  });

  // Watch all form fields for calculations
  const watchedValues = watch();

  // Calculate totals
  useEffect(() => {
    const section80C = Math.min(
      (watchedValues.ppf || 0) +
      (watchedValues.epf || 0) +
      (watchedValues.elss || 0) +
      (watchedValues.life_insurance || 0) +
      (watchedValues.home_loan_principal || 0) +
      (watchedValues.nsc || 0) +
      (watchedValues.tax_saver_fd || 0) +
      (watchedValues.tuition_fees || 0),
      DEDUCTION_LIMITS.section_80c.limit
    );

    const section80D = Math.min(
      (watchedValues.health_insurance_self || 0) +
      (watchedValues.health_insurance_parents || 0) +
      (watchedValues.preventive_health_checkup || 0),
      (DEDUCTION_LIMITS.section_80d_self.limit + DEDUCTION_LIMITS.section_80d_parents.limit)
    );

    setSection80CTotal(section80C);
    setSection80DTotal(section80D);
    
    const total = section80C + section80D + 
      (watchedValues.section_80E || 0) +
      (watchedValues.section_80G || 0) +
      (watchedValues.section_80TTA || 0) +
      (watchedValues.section_80TTB || 0) +
      (watchedValues.nps_80CCD1B || 0) +
      (watchedValues.nps_80CCD2 || 0);
      
    setTotalDeductions(total);
  }, [watchedValues]);

  // =============================================================================
  // FORM HANDLERS
  // =============================================================================

  const handleFormSubmit = (data: DeductionsFormData) => {
    const submissionData: FormDeductionsDTO = {
      // API DTO fields mapped from form data
      section_80c: section80CTotal,
      section_80ccc: 0, // Not used in this form
      section_80ccd_1: (data.nps_80CCD1B || 0),
      section_80ccd_1b: 0, // Not used in this form
      section_80ccd_2: (data.nps_80CCD2 || 0),
      section_80d_self: (data.health_insurance_self || 0),
      section_80d_parents: (data.health_insurance_parents || 0),
      section_80dd: 0, // Not used in this form
      section_80ddb: 0, // Not used in this form
      section_80e: (data.section_80E || 0),
      section_80ee: 0, // Not used in this form
      section_80eea: 0, // Not used in this form
      section_80eeb: 0, // Not used in this form
      section_80g: (data.section_80G || 0),
      section_80gga: 0, // Not used in this form
      section_80ggc: 0, // Not used in this form
      section_80ia: 0, // Not used in this form
      section_80ib: 0, // Not used in this form
      section_80ic: 0, // Not used in this form
      section_80id: 0, // Not used in this form
      section_80ie: 0, // Not used in this form
      section_80jjaa: 0, // Not used in this form
      section_80tta: (data.section_80TTA || 0),
      section_80ttb: (data.section_80TTB || 0),
      section_80u: 0, // Not used in this form
      
      // Form-specific fields
      ...(initialData?.id && { id: initialData.id }),
      section_80C_total: section80CTotal,
      section_80D_total: section80DTotal,
      total_deductions: totalDeductions,
      created_at: initialData?.created_at || new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    onSubmit(submissionData);
  };

  // =============================================================================
  // RENDER HELPERS
  // =============================================================================

  const renderProgressBar = (current: number, limit: number, label: string) => (
    <Box sx={{ mb: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
        <Typography variant="body2" color="text.secondary">
          {label}
        </Typography>
        <Typography variant="body2" fontWeight="bold">
          ₹{current.toLocaleString()} / ₹{limit.toLocaleString()}
        </Typography>
      </Box>
      <LinearProgress
        variant="determinate"
        value={(current / limit) * 100}
        sx={{
          height: 8,
          borderRadius: 4,
          backgroundColor: 'grey.200',
          '& .MuiLinearProgress-bar': {
            backgroundColor: current >= limit ? 'success.main' : 'primary.main',
          },
        }}
      />
      {current >= limit && (
        <Typography variant="caption" color="success.main" sx={{ mt: 0.5 }}>
          Maximum limit reached
        </Typography>
      )}
    </Box>
  );

  const renderSection80C = () => (
    <Card title="Section 80C Deductions" variant="outlined">
      <Box sx={{ mb: 3 }}>
        {renderProgressBar(section80CTotal, DEDUCTION_LIMITS.section_80c.limit, 'Section 80C Progress')}
      </Box>
      
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
        <Box>
          <Controller
            name="ppf"
            control={control}
            render={({ field }) => (
              <CurrencyInput
                {...field}
                label="Public Provident Fund (PPF)"
                onValueChange={field.onChange}
                max={150000}
                helperText="15-year lock-in period"
                fullWidth
              />
            )}
          />
        </Box>
        
        <Box>
          <Controller
            name="epf"
            control={control}
            render={({ field }) => (
              <CurrencyInput
                {...field}
                label="Employee Provident Fund (EPF)"
                onValueChange={field.onChange}
                max={150000}
                helperText="Employee contribution only"
                fullWidth
              />
            )}
          />
        </Box>
        
        <Box>
          <Controller
            name="elss"
            control={control}
            render={({ field }) => (
              <CurrencyInput
                {...field}
                label="Equity Linked Savings Scheme (ELSS)"
                onValueChange={field.onChange}
                max={150000}
                helperText="3-year lock-in period"
                fullWidth
              />
            )}
          />
        </Box>
        
        <Box>
          <Controller
            name="life_insurance"
            control={control}
            render={({ field }) => (
              <CurrencyInput
                {...field}
                label="Life Insurance Premium"
                onValueChange={field.onChange}
                max={150000}
                helperText="Premium paid for life insurance"
                fullWidth
              />
            )}
          />
        </Box>
        
        <Box>
          <Controller
            name="home_loan_principal"
            control={control}
            render={({ field }) => (
              <CurrencyInput
                {...field}
                label="Home Loan Principal Repayment"
                onValueChange={field.onChange}
                max={150000}
                helperText="Principal amount only"
                fullWidth
              />
            )}
          />
        </Box>
        
        <Box>
          <Controller
            name="nsc"
            control={control}
            render={({ field }) => (
              <CurrencyInput
                {...field}
                label="National Savings Certificate (NSC)"
                onValueChange={field.onChange}
                max={150000}
                helperText="5-year term deposit"
                fullWidth
              />
            )}
          />
        </Box>
        
        <Box>
          <Controller
            name="tax_saver_fd"
            control={control}
            render={({ field }) => (
              <CurrencyInput
                {...field}
                label="Tax Saver Fixed Deposit"
                onValueChange={field.onChange}
                max={150000}
                helperText="5-year lock-in FD"
                fullWidth
              />
            )}
          />
        </Box>
        
        <Box>
          <Controller
            name="tuition_fees"
            control={control}
            render={({ field }) => (
              <CurrencyInput
                {...field}
                label="Tuition Fees"
                onValueChange={field.onChange}
                max={150000}
                helperText="Children's education fees"
                fullWidth
              />
            )}
          />
        </Box>
      </Box>
    </Card>
  );

  const renderSection80D = () => (
    <Card title="Section 80D - Health Insurance" variant="outlined">
      <Box sx={{ mb: 3 }}>
        {renderProgressBar(section80DTotal, (DEDUCTION_LIMITS.section_80d_self.limit + DEDUCTION_LIMITS.section_80d_parents.limit), 'Section 80D Progress')}
      </Box>
      
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
        <Box>
          <Controller
            name="health_insurance_self"
            control={control}
            render={({ field }) => (
              <CurrencyInput
                {...field}
                label="Health Insurance (Self & Family)"
                onValueChange={field.onChange}
                max={DEDUCTION_LIMITS.section_80d_self.limit}
                helperText={`Maximum ₹${DEDUCTION_LIMITS.section_80d_self.limit.toLocaleString()}`}
                fullWidth
              />
            )}
          />
        </Box>
        
        <Box>
          <Controller
            name="health_insurance_parents"
            control={control}
            render={({ field }) => (
              <CurrencyInput
                {...field}
                label="Health Insurance (Parents)"
                onValueChange={field.onChange}
                max={DEDUCTION_LIMITS.section_80d_parents.limit}
                helperText={`Maximum ₹${DEDUCTION_LIMITS.section_80d_parents.limit.toLocaleString()}`}
                fullWidth
              />
            )}
          />
        </Box>
        
        <Box>
          <Controller
            name="preventive_health_checkup"
            control={control}
            render={({ field }) => (
              <CurrencyInput
                {...field}
                label="Preventive Health Check-up"
                onValueChange={field.onChange}
                max={5000}
                helperText="Maximum ₹5,000 (part of 80D limit)"
                fullWidth
              />
            )}
          />
        </Box>
      </Box>
    </Card>
  );

  const renderOtherDeductions = () => (
    <Card title="Other Deductions" variant="outlined">
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
        <Box>
          <Controller
            name="section_80E"
            control={control}
            render={({ field }) => (
              <CurrencyInput
                {...field}
                label="Education Loan Interest (80E)"
                onValueChange={field.onChange}
                helperText="No upper limit"
                fullWidth
              />
            )}
          />
        </Box>
        
        <Box>
          <Controller
            name="section_80G"
            control={control}
            render={({ field }) => (
              <CurrencyInput
                {...field}
                label="Donations (80G)"
                onValueChange={field.onChange}
                helperText="To approved charitable institutions"
                fullWidth
              />
            )}
          />
        </Box>
        
        <Box>
          <Controller
            name="section_80TTA"
            control={control}
            render={({ field }) => (
              <CurrencyInput
                {...field}
                label="Savings Account Interest (80TTA)"
                onValueChange={field.onChange}
                max={DEDUCTION_LIMITS.section_80tta.limit}
                helperText={`Maximum ₹${DEDUCTION_LIMITS.section_80tta.limit.toLocaleString()}`}
                fullWidth
              />
            )}
          />
        </Box>
        
        <Box>
          <Controller
            name="section_80TTB"
            control={control}
            render={({ field }) => (
              <CurrencyInput
                {...field}
                label="Senior Citizen Interest (80TTB)"
                onValueChange={field.onChange}
                max={DEDUCTION_LIMITS.section_80ttb.limit}
                helperText={`For age 60+, Maximum ₹${DEDUCTION_LIMITS.section_80ttb.limit.toLocaleString()}`}
                fullWidth
              />
            )}
          />
        </Box>
      </Box>
    </Card>
  );

  const renderNPSDeductions = () => (
    <Card title="National Pension Scheme (NPS)" variant="outlined">
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
        <Box>
          <Controller
            name="nps_80CCD1B"
            control={control}
            render={({ field }) => (
              <CurrencyInput
                {...field}
                label="NPS Additional (80CCD1B)"
                onValueChange={field.onChange}
                max={DEDUCTION_LIMITS.section_80ccd_1b.limit}
                helperText={`Additional deduction, Maximum ₹${DEDUCTION_LIMITS.section_80ccd_1b.limit.toLocaleString()}`}
                fullWidth
              />
            )}
          />
        </Box>
        
        <Box>
          <Controller
            name="nps_80CCD2"
            control={control}
            render={({ field }) => (
              <CurrencyInput
                {...field}
                label="Employer NPS Contribution (80CCD2)"
                onValueChange={field.onChange}
                helperText="10% of basic salary limit"
                fullWidth
              />
            )}
          />
        </Box>
      </Box>
    </Card>
  );

  const renderSummary = () => (
    <Card title="Deductions Summary" variant="success">
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr 1fr' }, gap: 3 }}>
        <Box>
          <Box sx={{ textAlign: 'center', p: 2 }}>
            <Savings sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
            <Typography variant="h6" fontWeight="bold">
              ₹{section80CTotal.toLocaleString()}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Section 80C
            </Typography>
          </Box>
        </Box>
        
        <Box>
          <Box sx={{ textAlign: 'center', p: 2 }}>
            <HealthAndSafety sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
            <Typography variant="h6" fontWeight="bold">
              ₹{section80DTotal.toLocaleString()}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Section 80D
            </Typography>
          </Box>
        </Box>
        
        <Box>
          <Box sx={{ textAlign: 'center', p: 2 }}>
            <AccountBalance sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
            <Typography variant="h6" fontWeight="bold">
              ₹{totalDeductions.toLocaleString()}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Total Deductions
            </Typography>
          </Box>
        </Box>
      </Box>
      
      {totalIncome > 0 && (
        <Alert severity="success" sx={{ mt: 2 }}>
          <Typography variant="body2">
            Tax saving potential: ₹{Math.min(totalDeductions * 0.3, totalIncome * 0.3).toLocaleString()} 
            (assuming 30% tax bracket)
          </Typography>
        </Alert>
      )}
    </Card>
  );

  const renderActions = () => (
    <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 3 }}>
      {onCancel && (
        <Button variant="outlined" onClick={onCancel}>
          Cancel
        </Button>
      )}
      <Button
        type="submit"
        loading={loading}
        disabled={!isValid}
        loadingText="Saving..."
      >
        Save Deductions
      </Button>
    </Box>
  );

  // =============================================================================
  // RENDER MAIN COMPONENT
  // =============================================================================

  if (taxRegime === 'new') {
    return (
      <Card variant="warning">
        <Box sx={{ textAlign: 'center', p: 3 }}>
          <Info sx={{ fontSize: 60, color: 'warning.main', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            New Tax Regime Selected
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Most deductions are not available under the new tax regime. 
            You get lower tax rates instead of deductions.
          </Typography>
        </Box>
      </Card>
    );
  }

  return (
    <Box component="form" onSubmit={handleSubmit(handleFormSubmit)}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          Tax Deductions (Old Regime)
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Claim available deductions to reduce your taxable income
        </Typography>
      </Box>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {renderSummary()}
        {renderSection80C()}
        {renderSection80D()}
        {renderOtherDeductions()}
        {renderNPSDeductions()}
        {renderActions()}
      </Box>
    </Box>
  );
};

export default DeductionsForm; 