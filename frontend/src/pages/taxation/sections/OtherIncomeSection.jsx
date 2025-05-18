import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  TextField,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tooltip,
  FormControlLabel,
  Checkbox,
  Button
} from '@mui/material';
import { formatIndianNumber } from '../utils/taxationUtils';
import FormSectionHeader from '../components/FormSectionHeader';
import { occupancyStatuses } from '../utils/taxationConstants';

/**
 * Other Income Section Component
 * @param {Object} props - Component props
 * @param {Object} props.taxationData - Taxation data state
 * @param {Function} props.handleInputChange - Function to handle input change
 * @param {Function} props.handleFocus - Function to handle focus
 * @param {Function} props.fetchVrsValue - Function to fetch VRS value
 * @returns {JSX.Element} Other Income section component
 */
const OtherIncomeSection = ({
  taxationData,
  handleInputChange,
  handleFocus,
  fetchVrsValue
}) => {
  const [loading, setLoading] = useState(false);
  
  // Ensure all required objects exist in taxationData
  if (!taxationData.other_sources) {
    taxationData.other_sources = {
      interest_savings: '',
      interest_fd: '',
      interest_rd: '',
      other_interest: '',
      business_professional_income: '',
      dividend_income: '',
      gifts: '',
      other_income: ''
    };
  }
  
  if (!taxationData.capital_gains) {
    taxationData.capital_gains = {
      stcg_111a: '',
      stcg_debt_mutual_fund: '',
      stcg_any_other_asset: '',
      ltcg_112a: '',
      ltcg_debt_mutual_fund: '',
      ltcg_any_other_asset: ''
    };
  }

  if (!taxationData.leave_encashment) {
    taxationData.leave_encashment = {
      leave_encashment_income_received: '',
      service_years: '',
      leave_encashed: '',
      is_deceased: false,
      average_monthly_salary: '',
      during_employment: false
    };
  }
  
  if (!taxationData.house_property) {
    taxationData.house_property = {
      property_address: '',
      occupancy_status: 'Self-Occupied',
      rent_income: '',
      property_tax: '',
      interest_on_home_loan: '',
      pre_construction_loan_interest: ''
    };
  }
  
  // Initialize voluntary_retirement object if it doesn't exist
  if (!taxationData.voluntary_retirement) {
    taxationData.voluntary_retirement = {
      is_vrs_requested: false,
      voluntary_retirement_amount: '',
      max_exemption_limit: 500000
    };
  }

  useEffect(() => {
    console.log('occupancyStatuses:', occupancyStatuses);
    console.log('Current occupancy status:', taxationData.house_property.occupancy_status);
  }, [taxationData.house_property.occupancy_status]);
  
  return (
    <Box sx={{ py: 2 }}>
      <Typography variant="h6" gutterBottom>
        Income from Other Sources
      </Typography>
      
      <Paper variant="outlined" sx={{ p: 3 }}>
        <Grid container spacing={3}>
          {/* Interest from Savings Account */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Interest from Savings Account"
              type="text"
              value={formatIndianNumber(taxationData.other_sources.interest_savings)}
              onChange={(e) => handleInputChange('other_sources', 'interest_savings', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('other_sources', 'interest_savings', e.target.value)}
            />
          </Grid>
          
          {/* Interest from Fixed Deposits */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Interest from Fixed Deposits"
              type="text"
              value={formatIndianNumber(taxationData.other_sources.interest_fd)}
              onChange={(e) => handleInputChange('other_sources', 'interest_fd', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('other_sources', 'interest_fd', e.target.value)}
            />
          </Grid>
          
          {/* Interest from Recurring Deposits */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Interest from Recurring Deposits"
              type="text"
              value={formatIndianNumber(taxationData.other_sources.interest_rd)}
              onChange={(e) => handleInputChange('other_sources', 'interest_rd', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('other_sources', 'interest_rd', e.target.value)}
            />
          </Grid>
          
          {/* Other Interest */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Other Interest"
              type="text"
              value={formatIndianNumber(taxationData.other_sources.other_interest)}
              onChange={(e) => handleInputChange('other_sources', 'other_interest', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('other_sources', 'other_interest', e.target.value)}
            />
          </Grid>
          
          {/* Dividend Income */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Dividend Income"
              type="text"
              value={formatIndianNumber(taxationData.other_sources.dividend_income)}
              onChange={(e) => handleInputChange('other_sources', 'dividend_income', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('other_sources', 'dividend_income', e.target.value)}
            />
          </Grid>
          
          {/* Gifts */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Gifts (Cash/Kind)"
              type="text"
              value={formatIndianNumber(taxationData.other_sources.gifts)}
              onChange={(e) => handleInputChange('other_sources', 'gifts', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('other_sources', 'gifts', e.target.value)}
            />
          </Grid>
          
          {/* Other Income */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Other Income"
              type="text"
              value={formatIndianNumber(taxationData.other_sources.other_income)}
              onChange={(e) => handleInputChange('other_sources', 'other_income', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('other_sources', 'other_income', e.target.value)}
            />
          </Grid>
        </Grid>
      </Paper>

      <FormSectionHeader title="Business Professional Income" />
      <Paper variant="outlined" sx={{ p: 3 }}>
        <Grid container spacing={3}>
          <Box 
            sx={{ 
              width: '100%', 
              display: 'flex',
              justifyContent: 'left'
            }}
          >
            <Typography variant="h6" color="primary">Business Professional Income</Typography>
          </Box>
          {/* Business Professional Income */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Business Professional Income"
              type="text"
              value={formatIndianNumber(taxationData.other_sources.business_professional_income)}
              onChange={(e) => handleInputChange('other_sources', 'business_professional_income', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('other_sources', 'business_professional_income', e.target.value)}
            />
          </Grid>
        </Grid>
      </Paper>
      
      <FormSectionHeader title="Capital Gains" />
      
      <Paper variant="outlined" sx={{ p: 3 }}>
        <Grid container spacing={3}>
          {/* Short Term Capital Gains */}
            <Box 
            sx={{ 
              width: '100%', 
              display: 'flex',
              justifyContent: 'left'
            }}
          >
            <Typography variant="h6" color="primary">Short Term Capital Gains</Typography>
          </Box>
          
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="STCG on Equity (Section 111A)"
              type="text"
              value={formatIndianNumber(taxationData.capital_gains.stcg_111a)}
              onChange={(e) => handleInputChange('capital_gains', 'stcg_111a', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('capital_gains', 'stcg_111a', e.target.value)}
            />
          </Grid>
          
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="STCG on Debt Mutual Fund"
              type="text"
              value={formatIndianNumber(taxationData.capital_gains.stcg_debt_mutual_fund)}
              onChange={(e) => handleInputChange('capital_gains', 'stcg_debt_mutual_fund', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('capital_gains', 'stcg_debt_mutual_fund', e.target.value)}
            />
          </Grid>
          
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="STCG on Other Assets"
              type="text"
              value={formatIndianNumber(taxationData.capital_gains.stcg_any_other_asset)}
              onChange={(e) => handleInputChange('capital_gains', 'stcg_any_other_asset', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('capital_gains', 'stcg_any_other_asset', e.target.value)}
            />
          </Grid>
          
          <Box 
            sx={{ 
              width: '100%', 
              display: 'flex',
              justifyContent: 'left'
            }}
          >
            <Typography variant="h6" color="primary">Long Term Capital Gains</Typography>
          </Box>

          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="LTCG on Equity (Section 112A)"
              type="text"
              value={formatIndianNumber(taxationData.capital_gains.ltcg_112a)}
              onChange={(e) => handleInputChange('capital_gains', 'ltcg_112a', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('capital_gains', 'ltcg_112a', e.target.value)}
            />
          </Grid>
          
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="LTCG on Debt Mutual Fund"
              type="text"
              value={formatIndianNumber(taxationData.capital_gains.ltcg_debt_mutual_fund)}
              onChange={(e) => handleInputChange('capital_gains', 'ltcg_debt_mutual_fund', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('capital_gains', 'ltcg_debt_mutual_fund', e.target.value)}
            />
          </Grid>
          
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="LTCG on Other Assets"
              type="text"
              value={formatIndianNumber(taxationData.capital_gains.ltcg_any_other_asset)}
              onChange={(e) => handleInputChange('capital_gains', 'ltcg_any_other_asset', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('capital_gains', 'ltcg_any_other_asset', e.target.value)}
            />
          </Grid>
        </Grid>
      </Paper>

      <FormSectionHeader title="House Property Income" />
      
      <Paper variant="outlined" sx={{ p: 3 }}>
        <Grid container spacing={3}>
          {/* House Property Income */}
            <Box 
            sx={{ 
              width: '100%', 
              display: 'flex',
              justifyContent: 'left'
            }}
          >
            <Typography variant="h6" color="primary">Income from House Property</Typography>
          </Box>
        
          <Grid item xs={12} md={6}>
            <Tooltip title="Occupancy Status" placement="top-start">
              <FormControl fullWidth>
                <InputLabel>Occupancy Status</InputLabel>
                  <Select
                    value={taxationData.house_property.occupancy_status || 'Self-Occupied'}
                    label="Occupancy Status"
                    onChange={(e) => {
                      const newStatus = e.target.value;
                      handleInputChange('house_property', 'occupancy_status', newStatus);
                      
                      // Reset rent_income and property_tax to 0 when status is Self-Occupied
                      if (newStatus === 'Self-Occupied') {
                        handleInputChange('house_property', 'rent_income', 0);
                        handleInputChange('house_property', 'property_tax', 0);
                      }
                    }}
                    onFocus={(e) => handleFocus('house_property', 'occupancy_status', e.target.value)}
                  >
                  {occupancyStatuses.map((status) => (
                    <MenuItem key={status} value={status}>
                      {status}
                    </MenuItem>
                  ))}
                  </Select>
              </FormControl>
            </Tooltip>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Rent Income"
              type="text"
              value={formatIndianNumber(taxationData.house_property.rent_income)}
              onChange={(e) => handleInputChange('house_property', 'rent_income', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              disabled={taxationData.house_property.occupancy_status === 'Self-Occupied'}
              onFocus={(e) => handleFocus('house_property', 'rent_income', e.target.value)}
            />
          </Grid>
          
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Property Tax"
              type="text"
              value={formatIndianNumber(taxationData.house_property.property_tax)}
              onChange={(e) => handleInputChange('house_property', 'property_tax', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              disabled={taxationData.house_property.occupancy_status === 'Self-Occupied'}
              onFocus={(e) => handleFocus('house_property', 'property_tax', e.target.value)}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Interest on Home Loan"
              type="text"
              value={formatIndianNumber(taxationData.house_property.interest_on_home_loan)}
              onChange={(e) => handleInputChange('house_property', 'interest_on_home_loan', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('house_property', 'interest_on_home_loan', e.target.value)}
            />
          </Grid>
          <Grid item xs={12} md={4}>
          <Tooltip
            title={
              <>
                Applicable only if construction is completed within 5 years of purchase.<br />
                Input value sum of interest paid in last 5 years.<br />
              </>
              }
              placement="top"
              arrow
            >
              <TextField
                fullWidth
                label="Pre-Construction Loan Interest"
                type="text"
                value={formatIndianNumber(taxationData.house_property.pre_construction_loan_interest)}
                onChange={(e) => handleInputChange('house_property', 'pre_construction_loan_interest', e.target.value)}
                InputProps={{ startAdornment: '₹' }}
                onFocus={(e) => handleFocus('house_property', 'pre_construction_loan_interest', e.target.value)}
              />
            </Tooltip>
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Property Address"
              type="text"
              multiline
              rows={4}
              value={taxationData.house_property.property_address || ''}
              onChange={(e) => handleInputChange('house_property', 'property_address', e.target.value)}
              onFocus={(e) => handleFocus('house_property', 'property_address', e.target.value)}
              placeholder="Enter complete property address"
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
              label="Average Monthly Salary"
              type="text"
              value={formatIndianNumber(taxationData.leave_encashment.average_monthly_salary)}
              onChange={(e) => handleInputChange('leave_encashment', 'average_monthly_salary', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('leave_encashment', 'average_monthly_salary', e.target.value)}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Service Years"
              type="text"
              value={formatIndianNumber(taxationData.leave_encashment.service_years)}
              onChange={(e) => handleInputChange('leave_encashment', 'service_years', e.target.value)}
              disabled={taxationData.leave_encashment.during_employment}
              onFocus={(e) => handleFocus('leave_encashment', 'service_years', e.target.value)}
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
    </Box>
  );
};

export default OtherIncomeSection; 