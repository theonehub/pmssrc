import React from 'react';
import {
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField
} from '@mui/material';
import FormSectionHeader from '../../components/FormSectionHeader';
import { formatIndianNumber } from '../../utils/taxationUtils';

/**
 * Loan Perquisites Section
 * @param {Object} props - Component props
 * @param {Object} props.taxationData - Taxation data state
 * @param {Function} props.handleNestedInputChange - Function to handle nested input change
 * @param {Function} props.handleNestedFocus - Function to handle nested focus
 * @returns {JSX.Element} Loan section component
 */
const LoanSection = ({
  taxationData,
  handleNestedInputChange,
  handleNestedFocus
}) => {
  return (
    <>
      <FormSectionHeader title="Interest-free/Concessional Loan" />
      
      <Grid container spacing={3}>
        {/* Loan Type */}
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Loan Type</InputLabel>
            <Select
              value={taxationData.salary.perquisites?.loan_type || 'Personal'}
              label="Loan Type"
              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'loan_type', e.target.value)}
            >
              <MenuItem value="Personal">Personal</MenuItem>
              <MenuItem value="Housing">Housing</MenuItem>
              <MenuItem value="Vehicle">Vehicle</MenuItem>
              <MenuItem value="Education">Education</MenuItem>
              <MenuItem value="Medical">Medical</MenuItem>
              <MenuItem value="Other">Other</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        
        {/* Loan Amount */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Loan Amount"
            type="text"
            value={formatIndianNumber(taxationData.salary.perquisites?.loan_amount || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'loan_amount', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'loan_amount', e.target.value)}
          />
        </Grid>
        
        {/* Loan Interest Rate (Company) */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Interest Rate (Company)"
            type="text"
            value={formatIndianNumber(taxationData.salary.perquisites?.loan_interest_rate_company || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'loan_interest_rate_company', e.target.value)}
            InputProps={{ endAdornment: '%' }}
            onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'loan_interest_rate_company', e.target.value)}
          />
        </Grid>
        
        {/* Loan Interest Rate (SBI) */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Interest Rate (SBI)"
            type="text"
            value={formatIndianNumber(taxationData.salary.perquisites?.loan_interest_rate_sbi || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'loan_interest_rate_sbi', e.target.value)}
            InputProps={{ endAdornment: '%' }}
            onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'loan_interest_rate_sbi', e.target.value)}
          />
        </Grid>
        
        {/* Loan Start Date */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Loan Start Date"
            type="date"
            value={taxationData.salary.perquisites?.loan_start_date || ''}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'loan_start_date', e.target.value)}
            InputLabelProps={{ shrink: true }}
          />
        </Grid>
        
        {/* Loan End Date */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Loan End Date"
            type="date"
            value={taxationData.salary.perquisites?.loan_end_date || ''}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'loan_end_date', e.target.value)}
            InputLabelProps={{ shrink: true }}
          />
        </Grid>
        
        {/* Loan Duration (months)
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Loan Duration (months)"
            type="number"
            value={taxationData.salary.perquisites?.loan_month_count || 0}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'loan_month_count', e.target.value)}
            onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'loan_month_count', e.target.value)}
          />
        </Grid> */}
      </Grid>
    </>
  );
};

export default LoanSection; 