import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Alert
} from '@mui/material';
import { Info, TrendingUp, Business, Work } from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

import { Card, CurrencyInput, TextInput, Button } from '../ui';
import { useTaxCalculation } from '../../../shared/hooks/useTaxCalculation';
import { INCOME_TYPES } from '../../../shared/constants/taxation';

// =============================================================================
// LOCAL TYPES AND INTERFACES
// =============================================================================

export type FormIncomeType = 'salary' | 'business' | 'capital_gains' | 'other_sources' | 'rental';

export interface IncomeSourceDTO {
  id?: string;
  income_type: FormIncomeType;
  annual_amount: number;
  description: string;
  
  // Optional type-specific fields
  employer_name?: string;
  pf_contribution?: number;
  professional_tax?: number;
  business_nature?: string;
  turnover?: number;
  asset_type?: string;
  holding_period?: number;
  cost_of_acquisition?: number;
  property_address?: string;
  municipal_tax?: number;
  maintenance_charges?: number;
  
  // Metadata
  created_at?: string;
  updated_at?: string;
}

// =============================================================================
// VALIDATION SCHEMA
// =============================================================================

const incomeSourceSchema = z.object({
  income_type: z.enum(['salary', 'business', 'capital_gains', 'other_sources', 'rental']),
  annual_amount: z.number().min(0, 'Amount must be positive'),
  description: z.string().min(1, 'Description is required'),
  
  // Salary specific
  employer_name: z.string().optional(),
  pf_contribution: z.number().min(0).optional(),
  professional_tax: z.number().min(0).optional(),
  
  // Business specific
  business_nature: z.string().optional(),
  turnover: z.number().min(0).optional(),
  
  // Capital gains specific
  asset_type: z.string().optional(),
  holding_period: z.number().min(0).optional(),
  cost_of_acquisition: z.number().min(0).optional(),
  
  // Rental specific
  property_address: z.string().optional(),
  municipal_tax: z.number().min(0).optional(),
  maintenance_charges: z.number().min(0).optional(),
});

type IncomeSourceFormData = z.infer<typeof incomeSourceSchema>;

// =============================================================================
// COMPONENT INTERFACES
// =============================================================================

export interface IncomeSourceFormProps {
  initialData?: Partial<IncomeSourceDTO>;
  onSubmit: (data: IncomeSourceDTO) => void;
  onCancel?: () => void;
  loading?: boolean;
  mode?: 'create' | 'edit';
}

// =============================================================================
// INCOME SOURCE FORM COMPONENT
// =============================================================================

export const IncomeSourceForm: React.FC<IncomeSourceFormProps> = ({
  initialData,
  onSubmit,
  onCancel,
  loading = false,
  mode = 'create'
}) => {
  const [selectedIncomeType, setSelectedIncomeType] = useState<FormIncomeType>('salary');
  const [estimatedTax, setEstimatedTax] = useState<number>(0);
  
  const { getQuickTaxEstimate } = useTaxCalculation();

  const {
    control,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isValid }
  } = useForm<IncomeSourceFormData>({
    resolver: zodResolver(incomeSourceSchema),
    defaultValues: {
      income_type: 'salary',
      annual_amount: 0,
      description: '',
      ...initialData
    }
  });

  const watchedAmount = watch('annual_amount');
  const watchedIncomeType = watch('income_type');

  // Update selected income type when form value changes
  useEffect(() => {
    setSelectedIncomeType(watchedIncomeType);
  }, [watchedIncomeType]);

  // Calculate estimated tax impact
  useEffect(() => {
    if (watchedAmount > 0 && getQuickTaxEstimate) {
      try {
        const estimate = getQuickTaxEstimate(watchedAmount, 'new');
        setEstimatedTax(estimate);
      } catch (error) {
        console.warn('Tax calculation failed:', error);
        setEstimatedTax(0);
      }
    } else {
      setEstimatedTax(0);
    }
  }, [watchedAmount, getQuickTaxEstimate]);

  // =============================================================================
  // FORM HANDLERS
  // =============================================================================

  const handleFormSubmit = (data: IncomeSourceFormData) => {
    // Clean up undefined values for strict typing
    const cleanedData: any = { ...data };
    Object.keys(cleanedData).forEach(key => {
      if (cleanedData[key] === undefined) {
        delete cleanedData[key];
      }
    });

    const baseData = {
      ...cleanedData,
      created_at: initialData?.created_at || new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    const submissionData: IncomeSourceDTO = initialData?.id 
      ? { ...baseData, id: initialData.id }
      : baseData;

    onSubmit(submissionData);
  };

  const handleIncomeTypeChange = (newType: FormIncomeType) => {
    setValue('income_type', newType);
    setSelectedIncomeType(newType);
    
    // Clear type-specific fields when changing type
    setValue('employer_name', '');
    setValue('business_nature', '');
    setValue('asset_type', '');
    setValue('property_address', '');
  };

  // =============================================================================
  // RENDER HELPERS
  // =============================================================================

  const getIncomeTypeIcon = (type: FormIncomeType) => {
    switch (type) {
      case 'salary': return Work;
      case 'business': return Business;
      case 'capital_gains': return TrendingUp;
      case 'rental': return Business;
      default: return Info;
    }
  };

  const getAmountSuggestions = (type: FormIncomeType): number[] => {
    switch (type) {
      case 'salary':
        return [300000, 500000, 800000, 1000000, 1500000, 2000000];
      case 'business':
        return [500000, 1000000, 2000000, 5000000, 10000000];
      case 'capital_gains':
        return [50000, 100000, 500000, 1000000, 2000000];
      case 'rental':
        return [100000, 200000, 500000, 1000000];
      default:
        return [100000, 500000, 1000000];
    }
  };

  const renderIncomeTypeSelector = () => (
    <Card title="Income Type" variant="outlined">
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr 1fr', sm: '1fr 1fr 1fr', md: 'repeat(4, 1fr)' }, gap: 2 }}>
        {INCOME_TYPES.map((type) => {
          const isSelected = selectedIncomeType === type.value;
          const Icon = getIncomeTypeIcon(type.value as FormIncomeType);
          
          return (
            <Box key={type.value}>
              <Card
                variant={isSelected ? 'info' : 'outlined'}
                onClick={() => handleIncomeTypeChange(type.value as FormIncomeType)}
                sx={{ 
                  cursor: 'pointer',
                  height: '100%',
                  transition: 'all 0.2s ease'
                }}
              >
                <Box sx={{ textAlign: 'center', p: 1 }}>
                  <Icon sx={{ fontSize: 40, mb: 1, color: isSelected ? 'primary.main' : 'text.secondary' }} />
                  <Typography variant="subtitle2" fontWeight="bold">
                    {type.label}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {type.description}
                  </Typography>
                </Box>
              </Card>
            </Box>
          );
        })}
      </Box>
    </Card>
  );

  const renderBasicDetails = () => (
    <Card title="Basic Information" variant="outlined">
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
        <Box>
          <Controller
            name="description"
            control={control}
            render={({ field }) => (
              <TextInput
                {...field}
                label="Description"
                placeholder="e.g., Salary from ABC Company"
                error={!!errors.description}
                helperText={errors.description?.message || ''}
                fullWidth
              />
            )}
          />
        </Box>
        
        <Box>
          <Controller
            name="annual_amount"
            control={control}
            render={({ field }) => (
              <CurrencyInput
                {...field}
                label="Annual Amount"
                onValueChange={field.onChange}
                error={!!errors.annual_amount}
                helperText={errors.annual_amount?.message || ''}
                suggestions={getAmountSuggestions(selectedIncomeType)}
                fullWidth
              />
            )}
          />
        </Box>
        
        <Box sx={{ 
          p: 2, 
          bgcolor: 'primary.light',
          borderRadius: 1,
          display: 'flex',
          alignItems: 'center',
          gap: 1
        }}>
          <TrendingUp color="primary" />
          <Box>
            <Typography variant="caption" color="primary.dark">
              Estimated Tax Impact
            </Typography>
            <Typography variant="h6" color="primary.dark" fontWeight="bold">
              ₹{estimatedTax.toLocaleString('en-IN')}
            </Typography>
          </Box>
        </Box>
      </Box>
    </Card>
  );

  const renderTypeSpecificFields = () => {
    switch (selectedIncomeType) {
      case 'salary':
        return renderSalaryFields();
      case 'business':
        return renderBusinessFields();
      case 'capital_gains':
        return renderCapitalGainsFields();
      case 'rental':
        return renderRentalFields();
      default:
        return null;
    }
  };

  const renderSalaryFields = () => (
    <Card title="Salary Details" variant="outlined">
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
        <Box>
          <Controller
            name="employer_name"
            control={control}
            render={({ field }) => (
              <TextInput
                {...field}
                label="Employer Name"
                placeholder="Company Name"
                fullWidth
              />
            )}
          />
        </Box>
        
        <Box>
          <Controller
            name="pf_contribution"
            control={control}
            render={({ field }) => (
              <CurrencyInput
                {...field}
                label="PF Contribution (Annual)"
                onValueChange={field.onChange}
                helperText="Employee + Employer contribution"
                fullWidth
              />
            )}
          />
        </Box>
        
        <Box>
          <Controller
            name="professional_tax"
            control={control}
            render={({ field }) => (
              <CurrencyInput
                {...field}
                label="Professional Tax (Annual)"
                onValueChange={field.onChange}
                max={2500}
                helperText="Maximum ₹2,500 per year"
                fullWidth
              />
            )}
          />
        </Box>
      </Box>
    </Card>
  );

  const renderBusinessFields = () => (
    <Card title="Business Details" variant="outlined">
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
        <Box>
          <Controller
            name="business_nature"
            control={control}
            render={({ field }) => (
              <TextInput
                {...field}
                label="Nature of Business"
                placeholder="e.g., Consulting, Trading, Manufacturing"
                fullWidth
              />
            )}
          />
        </Box>
        
        <Box>
          <Controller
            name="turnover"
            control={control}
            render={({ field }) => (
              <CurrencyInput
                {...field}
                label="Annual Turnover"
                onValueChange={field.onChange}
                helperText="Total business income for the year"
                fullWidth
              />
            )}
          />
        </Box>
      </Box>
    </Card>
  );

  const renderCapitalGainsFields = () => (
    <Card title="Capital Gains Details" variant="outlined">
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
        <Box>
          <Controller
            name="asset_type"
            control={control}
            render={({ field }) => (
              <TextInput
                {...field}
                label="Asset Type"
                placeholder="e.g., Equity Shares, Property, Mutual Funds"
                fullWidth
              />
            )}
          />
        </Box>
        
        <Box>
          <Controller
            name="holding_period"
            control={control}
            render={({ field }) => (
              <CurrencyInput
                {...field}
                label="Holding Period (Months)"
                onValueChange={field.onChange}
                helperText="Period asset was held"
                fullWidth
              />
            )}
          />
        </Box>
        
        <Box>
          <Controller
            name="cost_of_acquisition"
            control={control}
            render={({ field }) => (
              <CurrencyInput
                {...field}
                label="Cost of Acquisition"
                onValueChange={field.onChange}
                helperText="Original purchase price"
                fullWidth
              />
            )}
          />
        </Box>
      </Box>
    </Card>
  );

  const renderRentalFields = () => (
    <Card title="Rental Property Details" variant="outlined">
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
        <Box>
          <Controller
            name="property_address"
            control={control}
            render={({ field }) => (
              <TextInput
                {...field}
                label="Property Address"
                placeholder="Complete property address"
                multiline
                rows={2}
                fullWidth
              />
            )}
          />
        </Box>
        
        <Box>
          <Controller
            name="municipal_tax"
            control={control}
            render={({ field }) => (
              <CurrencyInput
                {...field}
                label="Municipal Tax (Annual)"
                onValueChange={field.onChange}
                helperText="Property tax paid to municipal authority"
                fullWidth
              />
            )}
          />
        </Box>
        
        <Box>
          <Controller
            name="maintenance_charges"
            control={control}
            render={({ field }) => (
              <CurrencyInput
                {...field}
                label="Maintenance Charges (Annual)"
                onValueChange={field.onChange}
                helperText="Annual maintenance and repair expenses"
                fullWidth
              />
            )}
          />
        </Box>
      </Box>
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
        loadingText={mode === 'create' ? 'Adding...' : 'Updating...'}
      >
        {mode === 'create' ? 'Add Income Source' : 'Update Income Source'}
      </Button>
    </Box>
  );

  // =============================================================================
  // RENDER MAIN COMPONENT
  // =============================================================================

  return (
    <Box component="form" onSubmit={handleSubmit(handleFormSubmit)}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          {mode === 'create' ? 'Add Income Source' : 'Edit Income Source'}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Provide details about your income source for accurate tax calculation
        </Typography>
      </Box>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {renderIncomeTypeSelector()}
        {renderBasicDetails()}
        {renderTypeSpecificFields()}
        
        {watchedAmount > 0 && (
          <Alert severity="info" icon={<Info />}>
            <Typography variant="body2">
              This income will be subject to tax calculation based on your selected regime. 
              The estimated impact shown is for reference only.
            </Typography>
          </Alert>
        )}
        
        {renderActions()}
      </Box>
    </Box>
  );
};

export default IncomeSourceForm; 