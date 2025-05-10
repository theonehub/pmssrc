import React from 'react';
import {
  Grid,
  TextField,
  FormControlLabel,
  Checkbox,
  Tooltip
} from '@mui/material';
import FormSectionHeader from '../../components/FormSectionHeader';
import { formatIndianNumber } from '../../utils/taxationUtils';

/**
 * Medical Reimbursement Perquisites Section
 * @param {Object} props - Component props
 * @param {Object} props.taxationData - Taxation data state
 * @param {Function} props.handleNestedInputChange - Function to handle nested input change
 * @param {Function} props.handleNestedFocus - Function to handle nested focus
 * @returns {JSX.Element} Medical Reimbursement section component
 */
const MedicalReimbursementSection = ({
  taxationData,
  handleNestedInputChange,
  handleNestedFocus
}) => {
  return (
    <>
      <FormSectionHeader title="Medical Reimbursement" />
      
      <Grid container spacing={3}>
        {/* Treatment in India */}
        <Grid item xs={12} md={6}>
          <FormControlLabel
            control={
              <Checkbox
                checked={taxationData.salary.perquisites?.is_treated_in_India || false}
                onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'is_treated_in_India', e.target.checked)}
              />
            }
            label="Treatment in India"
          />
        </Grid>
        
        {/* Medical reimbursement by employer */}
        <Grid item xs={12} md={6}>
          <Tooltip title="Medical Reimbursement by Employer">
            <TextField
              fullWidth
              label="Medical Reimbursement by Employer"
              type="text"
              value={formatIndianNumber(taxationData.salary.perquisites?.medical_reimbursement_by_employer || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'medical_reimbursement_by_employer', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'medical_reimbursement_by_employer', e.target.value)}
            />
          </Tooltip>
        </Grid>
        
        {/* Traveling allowance for treatment */}
        <Grid item xs={12} md={6}>
          <Tooltip title="Traveling Allowance for Treatment">
            <TextField
              fullWidth
              label="Traveling Allowance for Treatment"
              type="text"
              value={formatIndianNumber(taxationData.salary.perquisites?.travelling_allowance_for_treatment || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'travelling_allowance_for_treatment', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'travelling_allowance_for_treatment', e.target.value)}
            />
          </Tooltip>
        </Grid>
        
        {/* RBI limit for illness */}
        <Grid item xs={12} md={6}>
          <Tooltip title="RBI Limit for Illness">
            <TextField
              fullWidth
              label="RBI Limit for Illness"
              type="text"
              value={formatIndianNumber(taxationData.salary.perquisites?.rbi_limit_for_illness || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'rbi_limit_for_illness', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'rbi_limit_for_illness', e.target.value)}
            />
          </Tooltip>
        </Grid>
      </Grid>
    </>
  );
};

export default MedicalReimbursementSection; 