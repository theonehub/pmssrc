import React, { useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  TextField,
  Paper,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tooltip
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
 * @returns {JSX.Element} Other Income section component
 */
const OtherIncomeSection = ({
  taxationData,
  handleInputChange,
  handleFocus
}) => {
  // Ensure all required objects exist in taxationData
  if (!taxationData.other_sources) {
    taxationData.other_sources = {
      interest_savings: '',
      interest_fd: '',
      interest_rd: '',
      other_interest: '',
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
  
  if (!taxationData.house_property) {
    taxationData.house_property = {
      property_address: '',
      occupancy_status: 'Self-occupied',
      rent_income: '',
      property_tax: '',
      interest_home_loan: ''
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
          <FormControl fullWidth>
            <InputLabel>Occupancy Status</InputLabel>
            <Tooltip title="Occupancy Status">
              <Select
                value={taxationData.house_property.occupancy_status || 'Self-occupied'}
                label="Occupancy Status"
                onChange={(e) => handleInputChange('house_property', 'occupancy_status', e.target.value)}
              >
              {occupancyStatuses.map((status) => (
                <MenuItem key={status} value={status}>
                  {status}
                </MenuItem>
              ))}
              </Select>
            </Tooltip>
          </FormControl>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Rent Income"
              type="text"
              value={formatIndianNumber(taxationData.house_property.rent_income)}
              onChange={(e) => handleInputChange('house_property', 'rent_income', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
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
              onFocus={(e) => handleFocus('house_property', 'property_tax', e.target.value)}
            />
          </Grid>
          
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Interest on Home Loan"
              type="text"
              value={formatIndianNumber(taxationData.house_property.interest_home_loan)}
              onChange={(e) => handleInputChange('house_property', 'interest_home_loan', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('house_property', 'interest_home_loan', e.target.value)}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Property Address"
              type="text"
              multiline
              rows={4}
              value={formatIndianNumber(taxationData.house_property.property_address)}
              onChange={(e) => handleInputChange('house_property', 'property_address', e.target.value)}
              onFocus={(e) => handleFocus('house_property', 'property_address', e.target.value)}
            />
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default OtherIncomeSection; 