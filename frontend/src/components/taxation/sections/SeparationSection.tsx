import React from 'react';
import {
  Box,
  Typography,
  TextField,
  Paper,
  FormControlLabel,
  Checkbox,
  Button,
  FormControl,
  Select,
  MenuItem,
  SelectChangeEvent
} from '@mui/material';
import { formatIndianNumber } from '../utils/taxationUtils';
import FormSectionHeader from '../components/FormSectionHeader';
import { TaxationData } from '../../../shared/types';

interface SeparationSectionProps {
  taxationData: TaxationData;
  handleInputChange: (section: string, field: string, value: string | number | boolean) => void;
  handleFocus: (section: string, field: string, value: string | number) => void;
  fetchVrsValue: () => void;
}

/**
 * Separation Section Component for employee separation income
 */
const SeparationSection: React.FC<SeparationSectionProps> = ({
  taxationData,
  handleInputChange,
  handleFocus,
  fetchVrsValue
}) => {
  // Helper function to safely format values
  const formatSafeValue = (value: number | undefined): string => {
    return formatIndianNumber(value || 0);
  };

  // Type-safe event handlers
  const handleTextFieldChange = (section: string, field: string, event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>): void => {
    handleInputChange(section, field, event.target.value);
  };

  const handleCheckboxChange = (section: string, field: string, event: React.ChangeEvent<HTMLInputElement>): void => {
    handleInputChange(section, field, event.target.checked);
  };

  const handleSelectChange = (section: string, field: string, event: SelectChangeEvent<string>): void => {
    handleInputChange(section, field, event.target.value);
  };

  const handleTextFieldFocus = (section: string, field: string, event: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement>): void => {
    handleFocus(section, field, event.target.value);
  };

  // Safe access to nested objects with defaults
  const gratuity = taxationData.gratuity || { gratuity_income: 0 };
  const leaveEncashment = taxationData.leave_encashment || { 
    leave_encashment_income_received: 0, 
    leave_encashed: 0, 
    during_employment: false, 
    is_deceased: false 
  };
  const voluntaryRetirement = taxationData.voluntary_retirement || { 
    is_vrs_requested: false, 
    voluntary_retirement_amount: 0 
  };
  const retrenchmentCompensation = taxationData.retrenchment_compensation || { 
    is_provided: false, 
    retrenchment_amount: 0 
  };
  const pension = taxationData.pension || { 
    total_pension_income: 0, 
    computed_pension_percentage: 0, 
    uncomputed_pension_amount: 0 
  };

  return (
    <Box sx={{ py: 2 }}>
      <Typography variant="h6" gutterBottom>
        Separation Income
      </Typography>
      
      <FormSectionHeader title="Gratuity Income" />
      
      <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
        <Box sx={{ mb: 2 }}>
          <Typography variant="h6" color="primary">Gratuity Income</Typography>
        </Box>
        
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: 3,
            width: '100%'
          }}
        >
          <TextField
            fullWidth
            label="Gratuity Income"
            type="text"
            value={formatSafeValue(gratuity.gratuity_income)}
            onChange={(e) => handleTextFieldChange('gratuity', 'gratuity_income', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('gratuity', 'gratuity_income', e)}
          />
        </Box>
      </Paper>

      <FormSectionHeader title="Leave Encashment" />
      
      <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
        <Box sx={{ mb: 2 }}>
          <Typography variant="h6" color="primary">Leave Encashment Income</Typography>
        </Box>

        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: 3,
            width: '100%'
          }}
        >
          <FormControlLabel
            control={
              <Checkbox
                checked={Boolean(leaveEncashment.during_employment)}
                onChange={(e) => {
                  const newStatus = e.target.checked;
                  handleCheckboxChange('leave_encashment', 'during_employment', e);
                  if (newStatus === true) {
                    handleInputChange('leave_encashment', 'leave_encashed', 0);
                  }
                }}
              />
            }
            label="During Employment"
          />

          <FormControlLabel
            control={
              <Checkbox
                checked={Boolean(leaveEncashment.is_deceased)}
                onChange={(e) => handleCheckboxChange('leave_encashment', 'is_deceased', e)}
              />
            }
            label="Deceased"
          />

          <TextField
            fullWidth
            label="Leave Encashment Income Received"
            type="text"
            value={formatSafeValue(leaveEncashment.leave_encashment_income_received)}
            onChange={(e) => handleTextFieldChange('leave_encashment', 'leave_encashment_income_received', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('leave_encashment', 'leave_encashment_income_received', e)}
          />
          
          <TextField
            fullWidth
            label="Leave Encashed"
            type="text"
            value={formatSafeValue(leaveEncashment.leave_encashed)}
            onChange={(e) => handleTextFieldChange('leave_encashment', 'leave_encashed', e)}
            disabled={Boolean(leaveEncashment.during_employment)}
            onFocus={(e) => handleTextFieldFocus('leave_encashment', 'leave_encashed', e)}
          />
        </Box>
      </Paper>

      <FormSectionHeader title="Voluntary Retirement Scheme" />
      
      <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
        <Box sx={{ mb: 2 }}>
          <Typography variant="h6" color="primary">Voluntary Retirement Scheme (VRS)</Typography>
        </Box>
        
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: 3,
            width: '100%'
          }}
        >
          <FormControlLabel
            control={
              <Checkbox
                checked={Boolean(voluntaryRetirement.is_vrs_requested)}
                onChange={(e) => {
                  const newStatus = e.target.checked;
                  handleCheckboxChange('voluntary_retirement', 'is_vrs_requested', e);
                  if (!newStatus) {
                    // Reset amount when unchecked
                    handleInputChange('voluntary_retirement', 'voluntary_retirement_amount', 0);
                  }
                }}
              />
            }
            label="VRS Requested"
          />

          <TextField
            fullWidth
            label="VRS Amount"
            type="text"
            value={formatSafeValue(voluntaryRetirement.voluntary_retirement_amount)}
            onChange={(e) => handleTextFieldChange('voluntary_retirement', 'voluntary_retirement_amount', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('voluntary_retirement', 'voluntary_retirement_amount', e)}
          />
          
          <Button 
            variant="contained" 
            onClick={fetchVrsValue}
            fullWidth
            sx={{ height: '56px' }}
          >
            Compute VRS Value
          </Button>
        </Box>
      </Paper>

      <FormSectionHeader title="Retrenchment Compensation" />
      
      <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
        <Box sx={{ mb: 2 }}>
          <Typography variant="h6" color="primary">Retrenchment Compensation</Typography>
        </Box>
        
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: 3,
            width: '100%'
          }}
        >
          <FormControlLabel
            control={
              <Checkbox
                checked={Boolean(retrenchmentCompensation.is_provided)}
                onChange={(e) => handleCheckboxChange('retrenchment_compensation', 'is_provided', e)}
              />
            }
            label="Retrenchment Compensation Provided"
          />
          
          {retrenchmentCompensation.is_provided && (
            <TextField
              fullWidth
              label="Retrenchment Amount"
              type="text"
              value={formatSafeValue(retrenchmentCompensation.retrenchment_amount)}
              onChange={(e) => handleTextFieldChange('retrenchment_compensation', 'retrenchment_amount', e)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleTextFieldFocus('retrenchment_compensation', 'retrenchment_amount', e)}
            />
          )}
        </Box>
      </Paper>

      <FormSectionHeader title="Pension Income" />
      
      <Paper variant="outlined" sx={{ p: 3 }}>
        <Box sx={{ mb: 2 }}>
          <Typography variant="h6" color="primary">Pension Income</Typography>
        </Box>
        
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: 3,
            width: '100%'
          }}
        >
          <TextField
            fullWidth
            label="Pension Income"
            type="text"
            value={formatSafeValue(pension.total_pension_income)}
            onChange={(e) => handleTextFieldChange('pension', 'total_pension_income', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('pension', 'total_pension_income', e)}
          />

          <TextField
            fullWidth
            label="Computed Pension Percentage"
            type="text"
            value={formatSafeValue(pension.computed_pension_percentage)}
            onChange={(e) => handleTextFieldChange('pension', 'computed_pension_percentage', e)}
            InputProps={{ endAdornment: '%' }}
            onFocus={(e) => handleTextFieldFocus('pension', 'computed_pension_percentage', e)}
          />

          <FormControl fullWidth>
            <Select
              value={(pension as any).uncomputed_pension_frequency || 'Monthly'}
              onChange={(e) => handleSelectChange('pension', 'uncomputed_pension_frequency', e)}
              displayEmpty
            >
              {['Monthly', 'Quarterly', 'Annually'].map((frequency) => (
                <MenuItem key={frequency} value={frequency}>
                  {frequency}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            fullWidth
            label="Uncomputed Pension Amount"
            type="text"
            value={formatSafeValue(pension.uncomputed_pension_amount)}
            onChange={(e) => handleTextFieldChange('pension', 'uncomputed_pension_amount', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('pension', 'uncomputed_pension_amount', e)}
          />
        </Box>
      </Paper>
    </Box>
  );
};

export default SeparationSection; 