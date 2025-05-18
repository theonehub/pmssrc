import React from 'react';
import {
  Grid,
  TextField,
  FormControlLabel,
  Box,
  Divider,
  Tooltip,
  Typography,
  Checkbox
} from '@mui/material';
import FormSectionHeader from '../../components/FormSectionHeader';
import { formatIndianNumber } from '../../utils/taxationUtils';

/**
 * Free Education Perquisites Section
 * @param {Object} props - Component props
 * @param {Object} props.taxationData - Taxation data state
 * @param {Function} props.handleNestedInputChange - Function to handle nested input change
 * @param {Function} props.handleNestedFocus - Function to handle nested focus
 * @returns {JSX.Element} Free Education section component
 */
const FreeEducationSection = ({
  taxationData,
  handleNestedInputChange,
  handleNestedFocus
}) => {
  return (
    <>
      <Box 
          sx={{ 
            width: '100%', 
            display: 'flex',
            justifyContent: 'left'
          }}
        >
          <Typography variant="h6" color="primary">First Child</Typography>
        </Box>
        <Divider sx={{ my: 0, width: '100%' }} />
      <Grid container spacing={3}>
        {/* First Child */}
        <Grid item xs={12} md={6}>
          <FormControlLabel
            control={
              <Checkbox
                checked={taxationData.salary.perquisites?.employer_maintained_1st_child || false}
                onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'employer_maintained_1st_child', e.target.checked)}
              />
            }
            label="Education in Employer Maintained Institution"
          />
        </Grid>
        <Box 
          sx={{ 
            width: '100%', 
            display: 'flex',
            justifyContent: 'left'
          }}
        >
        </Box>
        {/* First Child Monthly Count */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Monthly Count"
            type="number"
            inputProps={{ min: 0, max: 12 }}
            value={taxationData.salary.perquisites?.monthly_count_1st_child || 0}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'monthly_count_1st_child', e.target.value)}
            onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'monthly_count_1st_child', e.target.value)}
            sx={{ width: { xs: '100%', sm: '250px', md: '200px' } }}
          />
        </Grid>
        
        {/* First Child Monthly Expenses */}
        <Grid item xs={12} md={6}>
          <Tooltip title="Value/Expenses met by Employer(Monthly)"
          placement="top"
          arrow
          >
          <TextField
            fullWidth
            label="Value/Expenses met by Employer(Monthly)"
            type="text"
            value={formatIndianNumber(taxationData.salary.perquisites?.employer_monthly_expenses_1st_child || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'employer_monthly_expenses_1st_child', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'employer_monthly_expenses_1st_child', e.target.value)}
          />
          </Tooltip>
        </Grid>
        <Box 
          sx={{ 
            width: '100%', 
            display: 'flex',
            justifyContent: 'left'
          }}
        >
          <Typography variant="h6" color="primary">Second Child</Typography>
        </Box>
        <Divider sx={{ my: 0, width: '100%' }} />
        
        {/* Second Child */}
        <Grid item xs={12} md={6}>
          <FormControlLabel
            control={
              <Checkbox
                checked={taxationData.salary.perquisites?.employer_maintained_2nd_child || false}
                onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'employer_maintained_2nd_child', e.target.checked)}
              />
            }
            label="Education in Employer Maintained Institution"
          />
        </Grid>
        <Box 
          sx={{ 
            width: '100%', 
            display: 'flex',
            justifyContent: 'left'
          }}
        >
        </Box>
        {/* Second Child Monthly Count */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Monthly Count"
            type="number"
            inputProps={{ min: 0, max: 12 }}
            value={taxationData.salary.perquisites?.monthly_count_2nd_child || 0}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'monthly_count_2nd_child', e.target.value)}
            onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'monthly_count_2nd_child', e.target.value)}
            sx={{ width: { xs: '100%', sm: '250px', md: '200px' } }}
          />
        </Grid>
        
        {/* Second Child Monthly Expenses */}
        <Grid item xs={12} md={6}>
          <Tooltip title="Value/Expenses met by Employer(Monthly)"
          placement="top"
          arrow
          >
          <TextField
            fullWidth
            label="Value/Expenses met by Employer(Monthly)"
            type="text"
            value={formatIndianNumber(taxationData.salary.perquisites?.employer_monthly_expenses_2nd_child || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'employer_monthly_expenses_2nd_child', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'employer_monthly_expenses_2nd_child', e.target.value)}
          />
          </Tooltip>
        </Grid>
      </Grid>
    </>
  );
};

export default FreeEducationSection; 