import React from 'react';
import {
  Grid,
  TextField,
  Tooltip
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
      
        {/* Number of Options */}
        <Grid item xs={12} md={6}>
          <Tooltip title="ESOPs and Stocks Exercised within current financial year."
          placement="top"
          arrow
          >
            <TextField
              fullWidth
              label="Number of Shares Exercised"
              type="number"
              value={taxationData.salary.perquisites?.number_of_esop_shares_exercised || 0}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'number_of_esop_shares_exercised', e.target.value)}
            onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'number_of_esop_shares_exercised', e.target.value)}
            />
          </Tooltip>
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
    </>
  );
};

export default ESOPStockOptionsSection; 