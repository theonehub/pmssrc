import React from 'react';
import {
  Grid,
  TextField
} from '@mui/material';
import FormSectionHeader from '../../components/FormSectionHeader';
import { formatIndianNumber } from '../../utils/taxationUtils';

/**
 * ESOP & Stock Options Perquisites Section
 * @param {Object} props - Component props
 * @param {Object} props.taxationData - Taxation data state
 * @param {Function} props.handleNestedInputChange - Function to handle nested input change
 * @param {Function} props.handleNestedFocus - Function to handle nested focus
 * @returns {JSX.Element} ESOP & Stock Options section component
 */
const ESOPStockOptionsSection = ({
  taxationData,
  handleNestedInputChange,
  handleNestedFocus
}) => {
  return (
    <>
      <FormSectionHeader title="ESOP & Stock Options" />
      
      <Grid container spacing={3}>
        {/* Grant Date */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Grant Date"
            type="date"
            value={taxationData.salary.perquisites?.grant_date || ''}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'grant_date', e.target.value)}
            InputLabelProps={{ shrink: true }}
          />
        </Grid>
        
        {/* Vesting Date */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Vesting Date"
            type="date"
            value={taxationData.salary.perquisites?.vesting_date || ''}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'vesting_date', e.target.value)}
            InputLabelProps={{ shrink: true }}
          />
        </Grid>
        
        {/* Exercise Date */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Exercise Date"
            type="date"
            value={taxationData.salary.perquisites?.exercise_date || ''}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'exercise_date', e.target.value)}
            InputLabelProps={{ shrink: true }}
          />
        </Grid>
        
        {/* Number of Options */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Number of Shares Awarded"
            type="number"
            value={taxationData.salary.perquisites?.number_of_esop_shares_awarded || 0}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'number_of_esop_shares_awarded', e.target.value)}
            onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'number_of_esop_shares_awarded', e.target.value)}
          />
        </Grid>
        
        {/* FMV on Exercise Date */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Allotment Price (per share)"
            type="text"
            value={formatIndianNumber(taxationData.salary.perquisites?.esop_allotment_price_per_share || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'esop_allotment_price_per_share', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'esop_allotment_price_per_share', e.target.value)}
          />
        </Grid>
        
        {/* Exercise Price */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Exercise Price (per share)"
            type="text"
            value={formatIndianNumber(taxationData.salary.perquisites?.esop_exercise_price_per_share || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'esop_exercise_price_per_share', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'esop_exercise_price_per_share', e.target.value)}
          />
        </Grid>
      </Grid>
    </>
  );
};

export default ESOPStockOptionsSection; 