import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  TextField,
  Paper,
  Tooltip,
  FormControlLabel,
  Checkbox,
  Button,
  FormControl,
  Select,
  MenuItem
} from '@mui/material';
import { formatIndianNumber } from '../utils/taxationUtils';
import FormSectionHeader from '../components/FormSectionHeader';

/**
 * Other Income Section Component
 * @param {Object} props - Component props
 * @param {Object} props.taxationData - Taxation data state
 * @param {Function} props.handleInputChange - Function to handle input change
 * @param {Function} props.handleFocus - Function to handle focus
 * @param {Function} props.fetchVrsValue - Function to fetch VRS value
 * @returns {JSX.Element} Other Income section component
 */
const SeparationSection = ({
  taxationData,
  handleInputChange,
  handleFocus,
  fetchVrsValue
}) => {
  const [loading, setLoading] = useState(false);
  
 
  // Initialize voluntary_retirement object if it doesn't exist
  if (!taxationData.voluntary_retirement) {
    taxationData.voluntary_retirement = {
      is_vrs_requested: false,
      voluntary_retirement_amount: ''
    };
  }

  // Initialize gratuity object if it doesn't exist
  if (!taxationData.gratuity) {
    taxationData.gratuity = {
      gratuity_income: ''
    };
  }

  // Initialize retrenchment_compensation object if it doesn't exist
  if (!taxationData.retrenchment_compensation) {
    taxationData.retrenchment_compensation = {
      retrenchment_amount: '',
      is_provided: false
    };
  }

  return (
    <Box sx={{ py: 2 }}>
      <Typography variant="h6" gutterBottom>
        Separation Income
      </Typography>
      
      <FormSectionHeader title="Gratuity Income" />
      
      <Paper variant="outlined" sx={{ p: 3 }}>
        <Grid container spacing={3}>
          <Box 
            sx={{ 
              width: '100%', 
              display: 'flex',
              justifyContent: 'left'
            }}
          >
            <Typography variant="h6" color="primary">Gratuity Income</Typography>
          </Box>
          
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Gratuity Income"
              type="text"
              value={formatIndianNumber(taxationData.gratuity.gratuity_income)}
              onChange={(e) => handleInputChange('gratuity', 'gratuity_income', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('gratuity', 'gratuity_income', e.target.value)}
            />
          </Grid>
        </Grid>
      </Paper>

      <FormSectionHeader title="Leave Encashment" />
      
      <Paper variant="outlined" sx={{ p: 3 }}>
        <Grid container spacing={3}>
          {/* Leave Encashment Income */}
            <Box 
            sx={{ 
              width: '100%', 
              display: 'flex',
              justifyContent: 'left'
            }}
          >
            <Typography variant="h6" color="primary">Leave Encashment Income</Typography>
          </Box>
          <Grid item xs={12} md={4}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={taxationData.leave_encashment.during_employment}
                  onChange={(e) => {
                    const newStatus = e.target.checked;
                    handleInputChange('leave_encashment', 'during_employment', newStatus);
                    if (newStatus === true) {
                      handleInputChange('leave_encashment', 'service_years', 0);
                      handleInputChange('leave_encashment', 'leave_encashed', 0);
                    }
                  }}
                />
              }
              label="During Employment"
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={taxationData.leave_encashment.is_deceased}
                  onChange={(e) => {
                    const newStatus = e.target.checked;
                    handleInputChange('leave_encashment', 'is_deceased', newStatus);
                  }}
                />
              }
              label="Deceased"
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Leave Encashment Income Received"
              type="text"
              value={formatIndianNumber(taxationData.leave_encashment.leave_encashment_income_received)}
              onChange={(e) => handleInputChange('leave_encashment', 'leave_encashment_income_received', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('leave_encashment', 'leave_encashment_income_received', e.target.value)}
            />
          </Grid>
          
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Leave Encashed"
              type="text"
              value={formatIndianNumber(taxationData.leave_encashment.leave_encashed)}
              onChange={(e) => handleInputChange('leave_encashment', 'leave_encashed', e.target.value)}
              disabled={taxationData.leave_encashment.during_employment}
              onFocus={(e) => handleFocus('leave_encashment', 'leave_encashed', e.target.value)}
            />
          </Grid>
          
        </Grid>
      </Paper>

      <FormSectionHeader title="Voluntary Retirement Scheme" />
      
      <Paper variant="outlined" sx={{ p: 3 }}>
        <Grid container spacing={3}>
          <Box 
            sx={{ 
              width: '100%', 
              display: 'flex',
              justifyContent: 'left'
            }}
          >
            <Typography variant="h6" color="primary">Voluntary Retirement Scheme (VRS)</Typography>
          </Box>
          
          <Grid item xs={12} md={4}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={taxationData.voluntary_retirement.is_vrs_requested}
                  onChange={(e) => {
                    const newStatus = e.target.checked;
                    handleInputChange('voluntary_retirement', 'is_vrs_requested', newStatus);
                    if (!newStatus) {
                      // Reset amount when unchecked
                      handleInputChange('voluntary_retirement', 'voluntary_retirement_amount', '');
                    }
                  }}
                />
              }
              label="VRS Requested"
            />
          </Grid>

          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="VRS Amount"
              type="text"
              value={formatIndianNumber(taxationData.voluntary_retirement.voluntary_retirement_amount)}
              onChange={(e) => handleInputChange('voluntary_retirement', 'voluntary_retirement_amount', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('voluntary_retirement', 'voluntary_retirement_amount', e.target.value)}
            />
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Button 
              variant="contained" 
              onClick={() => {
                fetchVrsValue();
              }}
              fullWidth
              sx={{ height: '56px' }}
            >
              {loading ? 'Computing...' : 'Compute VRS Value'}
            </Button>
          </Grid>
        </Grid>
      </Paper>

      <FormSectionHeader title="Retrenchment Compensation" />
      
      <Paper variant="outlined" sx={{ p: 3 }}>
        <Grid container spacing={3}>
          <Box 
            sx={{ 
              width: '100%', 
              display: 'flex',
              justifyContent: 'left'
            }}
          >
            <Typography variant="h6" color="primary">Retrenchment Compensation</Typography>
          </Box>
          
          <Grid item xs={12} md={4}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={taxationData.retrenchment_compensation.is_provided}
                  onChange={(e) => {
                    const newStatus = e.target.checked;
                    handleInputChange('retrenchment_compensation', 'is_provided', newStatus);
                  }}
                />
              }
              label="Retrenchment Compensation Provided"
            />
          </Grid>
          
          {taxationData.retrenchment_compensation.is_provided && (
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Retrenchment Amount"
                type="text"
                value={formatIndianNumber(taxationData.retrenchment_compensation.retrenchment_amount)}
                onChange={(e) =>
                  handleInputChange('retrenchment_compensation', 'retrenchment_amount', e.target.value)
                }
                InputProps={{ startAdornment: '₹' }}
                onFocus={(e) =>
                  handleFocus('retrenchment_compensation', 'retrenchment_amount', e.target.value)
                }
              />
            </Grid>
          )}
        </Grid>
      </Paper>
      <FormSectionHeader title="Pension Income" />
      
      <Paper variant="outlined" sx={{ p: 3 }}>
        <Grid container spacing={3}>
          <Box 
            sx={{ 
              width: '100%', 
              display: 'flex',
              justifyContent: 'left'
            }}
          >
            <Typography variant="h6" color="primary">Pension Income</Typography>
          </Box>
          
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Pension Income"
                type="text"
                value={formatIndianNumber(taxationData.pension.total_pension_income)}
                onChange={(e) =>
                  handleInputChange('pension', 'total_pension_income', e.target.value)
                }
                InputProps={{ startAdornment: '₹' }}
                onFocus={(e) =>
                  handleFocus('pension', 'total_pension_income', e.target.value)
                }
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Computed Pension Percentage"
                type="text"
                value={formatIndianNumber(taxationData.pension.computed_pension_percentage)}
                onChange={(e) =>
                  handleInputChange('pension', 'computed_pension_percentage', e.target.value)
                }
                InputProps={{ startAdornment: '%' }}
                onFocus={(e) =>
                  handleFocus('pension', 'computed_pension_percentage', e.target.value)
                }
              />
            </Grid>
            <FormControl sx={{ minWidth: 80 }}>
                <Select
                  value={taxationData.pension.uncomputed_pension_frequency}
                  onChange={(e) => {
                    handleInputChange('pension', 'uncomputed_pension_frequency', e.target.value);
                    }}
                  >
                  {['Monthly', 'Quarterly', 'Annually'].map((size) => (
                    <MenuItem key={size} value={size}>
                    {size}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Uncomputed Pension Amount"
                type="text"
                value={formatIndianNumber(taxationData.pension.uncomputed_pension_amount)}
                onChange={(e) =>
                  handleInputChange('pension', 'uncomputed_pension_amount', e.target.value)
                }
                InputProps={{ startAdornment: '₹' }}
                onFocus={(e) =>
                  handleFocus('pension', 'uncomputed_pension_amount', e.target.value)
                }
              />
            </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default SeparationSection; 