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
  const gratuity = taxationData.retirement_benefits?.gratuity || { gratuity_received: 0, exemption_limit: 0, taxable_amount: 0 };
  const leaveEncashment = taxationData.retirement_benefits?.leave_encashment || { 
    leave_encashment_income_received: 0, 
    leave_encashment_exemption: 0,
    leave_encashment_taxable: 0,
    during_employment: false, 
    is_deceased: false 
  };
  const voluntaryRetirement = taxationData.retirement_benefits?.vrs || { 
    is_vrs_requested: false, 
    compensation_received: 0,
    exemption_limit: 0,
    taxable_amount: 0
  };
  const retrenchmentCompensation = taxationData.retirement_benefits?.retrenchment_compensation || { 
    is_provided: false, 
    compensation_received: 0,
    exemption_limit: 0,
    taxable_amount: 0
  };
  const pension = taxationData.retirement_benefits?.pension || { 
    pension_received: 0, 
    commuted_pension: 0, 
    uncommuted_pension: 0,
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
            value={formatSafeValue(gratuity.gratuity_received)}
            onChange={(e) => handleTextFieldChange('gratuity', 'gratuity_received', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('gratuity', 'gratuity_received', e)}
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
                    handleInputChange('leave_encashment', 'leave_encashment_exemption', 0);
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
            label="Leave Encashment Exemption"
            type="text"
            value={formatSafeValue(leaveEncashment.leave_encashment_exemption)}
            onChange={(e) => handleTextFieldChange('leave_encashment', 'leave_encashment_exemption', e)}
            disabled={Boolean(leaveEncashment.during_employment)}
            onFocus={(e) => handleTextFieldFocus('leave_encashment', 'leave_encashment_exemption', e)}
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
                  handleCheckboxChange('vrs', 'is_vrs_requested', e);
                  if (!newStatus) {
                    // Reset amount when unchecked
                    handleInputChange('vrs', 'compensation_received', 0);
                  }
                }}
              />
            }
            label="VRS Requested"
          />

          <TextField
            fullWidth
            label="VRS Compensation Received"
            type="text"
            value={formatSafeValue(voluntaryRetirement.compensation_received)}
            onChange={(e) => handleTextFieldChange('vrs', 'compensation_received', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('vrs', 'compensation_received', e)}
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
              label="Retrenchment Compensation Received"
              type="text"
              value={formatSafeValue(retrenchmentCompensation.compensation_received)}
              onChange={(e) => handleTextFieldChange('retrenchment_compensation', 'compensation_received', e)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleTextFieldFocus('retrenchment_compensation', 'compensation_received', e)}
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
            value={formatSafeValue(pension.pension_received)}
            onChange={(e) => handleTextFieldChange('pension', 'pension_received', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('pension', 'pension_received', e)}
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
              value={(pension as any).uncommuted_pension_frequency || 'Monthly'}
              onChange={(e) => handleSelectChange('pension', 'uncommuted_pension_frequency', e)}
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
            label="Uncommuted Pension Amount"
            type="text"
            value={formatSafeValue(pension.uncommuted_pension)}
            onChange={(e) => handleTextFieldChange('pension', 'uncommuted_pension', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('pension', 'uncommuted_pension', e)}
          />
        </Box>
      </Paper>
    </Box>
  );
};

export default SeparationSection; 