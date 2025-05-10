import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  FormHelperText
} from '@mui/material';

/**
 * Component for selecting tax regime
 * @param {Object} props - Component props
 * @param {Object} props.taxationData - Taxation data state
 * @param {Function} props.handleRegimeChange - Function to handle regime change
 * @returns {JSX.Element} Regime selection component
 */
const RegimeSelection = ({ taxationData, handleRegimeChange }) => {
  return (
    <Box sx={{ py: 2 }}>
      <Typography variant="h6" gutterBottom>
        Select Tax Regime
      </Typography>
      <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
        <FormControl component="fieldset">
          <RadioGroup
            aria-label="tax-regime"
            name="tax-regime"
            value={taxationData.regime}
            onChange={handleRegimeChange}
          >
            <FormControlLabel 
              value="old" 
              control={<Radio />} 
              label="Old Regime (with deductions & exemptions)" 
            />
            <FormHelperText sx={{ ml: 4, mb: 2 }}>
              The old tax regime allows various deductions and exemptions like Section 80C, 80D, HRA, etc. 
              This might be beneficial if you have eligible investments and expenses.
            </FormHelperText>
            
            <FormControlLabel 
              value="new" 
              control={<Radio />} 
              label="New Regime (lower tax rates, no deductions)" 
            />
            <FormHelperText sx={{ ml: 4 }}>
              The new tax regime offers lower tax rates but doesn't allow most deductions and exemptions. 
              This might be beneficial if you don't have many eligible investments or expenses.
            </FormHelperText>
          </RadioGroup>
        </FormControl>
      </Paper>
      
      <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
        Note: You can calculate your tax under both regimes before making your final decision.
      </Typography>
    </Box>
  );
};

export default RegimeSelection; 