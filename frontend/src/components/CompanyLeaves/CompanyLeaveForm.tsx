import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  MenuItem,
  FormControlLabel,
  Checkbox,
  Divider,
  Alert
} from '@mui/material';
import { CompanyLeave } from '../../models/companyLeave';

interface CompanyLeaveFormProps {
  companyLeave?: CompanyLeave | undefined;
  onSubmit: (data: Partial<CompanyLeave>) => Promise<void>;
  onCancel?: () => void;
}

const CompanyLeaveForm: React.FC<CompanyLeaveFormProps> = ({
  companyLeave,
  onSubmit,
  onCancel
}) => {
  // Form state
  const [leaveName, setLeaveName] = useState(companyLeave?.leave_name || '');
  const [accrualType, setAccrualType] = useState(companyLeave?.accrual_type || 'annually');
  const [annualAllocation, setAnnualAllocation] = useState(companyLeave?.annual_allocation?.toString() || '0');
  const [description, setDescription] = useState(companyLeave?.description || '');
  const [encashable, setEncashable] = useState(companyLeave?.encashable || false);
  const [isActive, setIsActive] = useState(companyLeave?.is_active !== undefined ? companyLeave.is_active : true);
  
  // Error states
  const [leaveNameError, setLeaveNameError] = useState('');
  const [annualAllocationError, setAnnualAllocationError] = useState('');
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState('');

  // Accrual type options
  const accrualTypeOptions = [
    { value: 'monthly', label: 'Monthly' },
    { value: 'quarterly', label: 'Quarterly' },
    { value: 'annually', label: 'Annually' },
    { value: 'immediate', label: 'Immediate' },
    { value: 'none', label: 'None' }
  ];

  // Validation functions
  const validateRequired = (value: string, fieldName: string): string => {
    return !value.trim() ? `${fieldName} is required` : '';
  };

  const validateAnnualAllocation = (value: string): string => {
    if (!value.trim()) return 'Annual allocation is required';
    const num = parseInt(value);
    if (isNaN(num) || num < 0) return 'Annual allocation must be a positive number';
    if (num > 365) return 'Annual allocation cannot exceed 365 days';
    return '';
  };

  // Real-time validation handlers


  const handleLeaveNameChange = (value: string) => {
    setLeaveName(value);
    setLeaveNameError(validateRequired(value, 'Leave name'));
  };

  const handleAnnualAllocationChange = (value: string) => {
    setAnnualAllocation(value);
    setAnnualAllocationError(validateAnnualAllocation(value));
  };

  // Form validation
  const validateForm = (): boolean => {
    let isValid = true;
    
    const nameErr = validateRequired(leaveName, 'Leave name');
    const allocationErr = validateAnnualAllocation(annualAllocation);

    setLeaveNameError(nameErr);
    setAnnualAllocationError(allocationErr);

    if (nameErr || allocationErr) {
      isValid = false;
    }

    return isValid;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError('');
    
    if (!validateForm()) {
      setSubmitError('Please fix the errors above before submitting.');
      return;
    }
    
    setIsSubmitting(true);
    try {
      const formData = {
        leave_name: leaveName,
        accrual_type: accrualType,
        annual_allocation: parseInt(annualAllocation),
        description: description || null,
        encashable,
        is_active: isActive
      };
      
      await onSubmit(formData);
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Submit error:', error);
      }
      setSubmitError(error.message || 'An error occurred while saving. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Paper sx={{ p: 3, maxWidth: 800, mx: 'auto' }}>
      <Typography variant="h5" gutterBottom>
        {companyLeave?.company_leave_id ? 'Edit Company Leave Policy' : 'Create Company Leave Policy'}
      </Typography>

      {submitError && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {submitError}
        </Alert>
      )}
      
      <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        
        {/* Leave Type Information */}
        <Box>
          <Typography variant="h6" color="primary" gutterBottom>
            Leave Type Information
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2 }}>
            <TextField
              fullWidth
              label="Leave Name"
              value={leaveName}
              onChange={(e) => handleLeaveNameChange(e.target.value)}
              error={!!leaveNameError}
              helperText={leaveNameError}
              required
              placeholder="e.g., Annual Leave, Sick Leave"
            />
          </Box>
          
          <TextField
            fullWidth
            label="Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            multiline
            rows={3}
            placeholder="Brief description of the leave policy..."
            sx={{ mt: 2 }}
          />
        </Box>

        {/* Allocation & Accrual Information */}
        <Box>
          <Typography variant="h6" color="primary" gutterBottom>
            Allocation & Accrual
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2 }}>
            <TextField
              fullWidth
              label="Annual Allocation"
              type="number"
              value={annualAllocation}
              onChange={(e) => handleAnnualAllocationChange(e.target.value)}
              error={!!annualAllocationError}
              helperText={annualAllocationError}
              required
              inputProps={{ min: 0, max: 365 }}
              placeholder="Number of days per year"
            />
            
            <TextField
              select
              fullWidth
              label="Accrual Type"
              value={accrualType}
              onChange={(e) => setAccrualType(e.target.value)}
            >
              {accrualTypeOptions.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
          </Box>
        </Box>

        {/* Policy Settings */}
        <Box>
          <Typography variant="h6" color="primary" gutterBottom>
            Policy Settings
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={encashable}
                  onChange={(e) => setEncashable(e.target.checked)}
                  color="primary"
                />
              }
              label="Leave can be encashed"
            />
            {companyLeave?.company_leave_id && (
              <FormControlLabel
                control={
                  <Checkbox
                    checked={isActive}
                    onChange={(e) => setIsActive(e.target.checked)}
                    color="primary"
                  />
                }
                label="Policy is active"
              />
            )}
          </Box>
        </Box>

        {/* Submit Buttons */}
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2, pt: 2 }}>
          {onCancel && (
            <Button
              variant="outlined"
              onClick={onCancel}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
          )}
          <Button
            type="submit"
            variant="contained"
            size="large"
            disabled={isSubmitting}
            sx={{ minWidth: 150 }}
          >
            {isSubmitting ? 'Saving...' : (companyLeave?.company_leave_id ? 'Update' : 'Create')} Leave Policy
          </Button>
        </Box>
      </Box>
    </Paper>
  );
};

export default CompanyLeaveForm; 