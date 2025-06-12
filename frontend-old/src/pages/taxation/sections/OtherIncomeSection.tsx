import React, { useEffect } from 'react';
import {
  Box,
  Typography,
  TextField,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tooltip,
  SelectChangeEvent
} from '@mui/material';
import { formatIndianNumber } from '../utils/taxationUtils';
import FormSectionHeader from '../components/FormSectionHeader';
import { occupancyStatuses } from '../utils/taxationConstants';
import { TaxationData } from '../../../types';

interface OtherIncomeSectionProps {
  taxationData: TaxationData;
  handleInputChange: (
    section: string,
    field: string,
    value: string | number
  ) => void;
  handleFocus: (
    section: string,
    field: string,
    value: string | number
  ) => void;
}

/**
 * Other Income Section Component
 */
const OtherIncomeSection: React.FC<OtherIncomeSectionProps> = ({
  taxationData,
  handleInputChange,
  handleFocus
}) => {
  // Ensure all required objects exist in taxationData
  if (!taxationData.other_sources) {
    taxationData.other_sources = {
      interest_savings: 0,
      interest_fd: 0,
      interest_rd: 0,
      other_interest: 0,
      business_professional_income: 0,
      dividend_income: 0,
      gifts: 0,
      other_income: 0
    };
  }
  
  if (!taxationData.capital_gains) {
    taxationData.capital_gains = {
      stcg_111a: 0,
      stcg_debt_mutual_fund: 0,
      stcg_any_other_asset: 0,
      ltcg_112a: 0,
      ltcg_debt_mutual_fund: 0,
      ltcg_any_other_asset: 0
    };
  }

  if (!taxationData.leave_encashment) {
    taxationData.leave_encashment = {
      leave_encashment_income_received: 0,
      leave_encashed: 0,
      is_deceased: false,
      during_employment: false
    };
  }
  
  if (!taxationData.house_property) {
    taxationData.house_property = {
      property_address: '',
      occupancy_status: 'Self-Occupied',
      rent_income: 0,
      property_tax: 0,
      interest_on_home_loan: 0,
      pre_construction_loan_interest: 0
    };
  }

  const handleSelectChange = (section: string, field: string, event: SelectChangeEvent<string>): void => {
    const newStatus = event.target.value;
    handleInputChange(section, field, newStatus);
    
    // Reset rent_income and property_tax to 0 when status is Self-Occupied
    if (section === 'house_property' && field === 'occupancy_status' && newStatus === 'Self-Occupied') {
      handleInputChange('house_property', 'rent_income', 0);
      handleInputChange('house_property', 'property_tax', 0);
    }
  };

  const handleTextFieldChange = (section: string, field: string, event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>): void => {
    handleInputChange(section, field, event.target.value);
  };

  const handleTextFieldFocus = (section: string, field: string, event: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement>): void => {
    handleFocus(section, field, event.target.value);
  };

  useEffect(() => {
    // Log statements removed for production
  }, [taxationData.house_property.occupancy_status]);
  
  return (
    <Box sx={{ py: 2 }}>
      <Typography variant="h6" gutterBottom>
        Income from Other Sources
      </Typography>
      
      <Paper variant="outlined" sx={{ p: 3 }}>
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: 3,
            width: '100%'
          }}
        >
          {/* Interest from Savings Account */}
          <TextField
            fullWidth
            label="Interest from Savings Account"
            type="text"
            value={formatIndianNumber(taxationData.other_sources.interest_savings)}
            onChange={(e) => handleTextFieldChange('other_sources', 'interest_savings', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('other_sources', 'interest_savings', e)}
          />
          
          {/* Interest from Fixed Deposits */}
          <TextField
            fullWidth
            label="Interest from Fixed Deposits"
            type="text"
            value={formatIndianNumber(taxationData.other_sources.interest_fd)}
            onChange={(e) => handleTextFieldChange('other_sources', 'interest_fd', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('other_sources', 'interest_fd', e)}
          />
          
          {/* Interest from Recurring Deposits */}
          <TextField
            fullWidth
            label="Interest from Recurring Deposits"
            type="text"
            value={formatIndianNumber(taxationData.other_sources.interest_rd)}
            onChange={(e) => handleTextFieldChange('other_sources', 'interest_rd', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('other_sources', 'interest_rd', e)}
          />
          
          {/* Other Interest */}
          <TextField
            fullWidth
            label="Other Interest"
            type="text"
            value={formatIndianNumber(taxationData.other_sources.other_interest)}
            onChange={(e) => handleTextFieldChange('other_sources', 'other_interest', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('other_sources', 'other_interest', e)}
          />
          
          {/* Dividend Income */}
          <TextField
            fullWidth
            label="Dividend Income"
            type="text"
            value={formatIndianNumber(taxationData.other_sources.dividend_income)}
            onChange={(e) => handleTextFieldChange('other_sources', 'dividend_income', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('other_sources', 'dividend_income', e)}
          />
          
          {/* Gifts */}
          <TextField
            fullWidth
            label="Gifts (Cash/Kind)"
            type="text"
            value={formatIndianNumber(taxationData.other_sources.gifts)}
            onChange={(e) => handleTextFieldChange('other_sources', 'gifts', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('other_sources', 'gifts', e)}
          />
          
          {/* Other Income */}
          <TextField
            fullWidth
            label="Other Income"
            type="text"
            value={formatIndianNumber(taxationData.other_sources.other_income)}
            onChange={(e) => handleTextFieldChange('other_sources', 'other_income', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('other_sources', 'other_income', e)}
          />
        </Box>
      </Paper>

      <FormSectionHeader title="Business Professional Income" />
      <Paper variant="outlined" sx={{ p: 3 }}>
        <Box 
          sx={{ 
            width: '100%', 
            display: 'flex',
            justifyContent: 'left',
            mb: 2
          }}
        >
          <Typography variant="h6" color="primary">Business Professional Income</Typography>
        </Box>
        
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: 3,
            width: '100%'
          }}
        >
          {/* Business Professional Income */}
          <TextField
            fullWidth
            label="Business Professional Income"
            type="text"
            value={formatIndianNumber(taxationData.other_sources.business_professional_income)}
            onChange={(e) => handleTextFieldChange('other_sources', 'business_professional_income', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('other_sources', 'business_professional_income', e)}
          />
        </Box>
      </Paper>
      
      <FormSectionHeader title="Capital Gains" />
      
      <Paper variant="outlined" sx={{ p: 3 }}>
        {/* Short Term Capital Gains */}
        <Box 
          sx={{ 
            width: '100%', 
            display: 'flex',
            justifyContent: 'left',
            mb: 2
          }}
        >
          <Typography variant="h6" color="primary">Short Term Capital Gains</Typography>
        </Box>
        
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: 3,
            width: '100%',
            mb: 4
          }}
        >
          <TextField
            fullWidth
            label="STCG on Equity (Section 111A)"
            type="text"
            value={formatIndianNumber(taxationData.capital_gains.stcg_111a)}
            onChange={(e) => handleTextFieldChange('capital_gains', 'stcg_111a', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('capital_gains', 'stcg_111a', e)}
          />
          
          <TextField
            fullWidth
            label="STCG on Debt Mutual Fund"
            type="text"
            value={formatIndianNumber(taxationData.capital_gains.stcg_debt_mutual_fund)}
            onChange={(e) => handleTextFieldChange('capital_gains', 'stcg_debt_mutual_fund', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('capital_gains', 'stcg_debt_mutual_fund', e)}
          />
          
          <TextField
            fullWidth
            label="STCG on Other Assets"
            type="text"
            value={formatIndianNumber(taxationData.capital_gains.stcg_any_other_asset)}
            onChange={(e) => handleTextFieldChange('capital_gains', 'stcg_any_other_asset', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('capital_gains', 'stcg_any_other_asset', e)}
          />
        </Box>
        
        {/* Long Term Capital Gains */}
        <Box 
          sx={{ 
            width: '100%', 
            display: 'flex',
            justifyContent: 'left',
            mb: 2
          }}
        >
          <Typography variant="h6" color="primary">Long Term Capital Gains</Typography>
        </Box>

        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: 3,
            width: '100%'
          }}
        >
          <TextField
            fullWidth
            label="LTCG on Equity (Section 112A)"
            type="text"
            value={formatIndianNumber(taxationData.capital_gains.ltcg_112a)}
            onChange={(e) => handleTextFieldChange('capital_gains', 'ltcg_112a', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('capital_gains', 'ltcg_112a', e)}
          />
          
          <TextField
            fullWidth
            label="LTCG on Debt Mutual Fund"
            type="text"
            value={formatIndianNumber(taxationData.capital_gains.ltcg_debt_mutual_fund)}
            onChange={(e) => handleTextFieldChange('capital_gains', 'ltcg_debt_mutual_fund', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('capital_gains', 'ltcg_debt_mutual_fund', e)}
          />
          
          <TextField
            fullWidth
            label="LTCG on Other Assets"
            type="text"
            value={formatIndianNumber(taxationData.capital_gains.ltcg_any_other_asset)}
            onChange={(e) => handleTextFieldChange('capital_gains', 'ltcg_any_other_asset', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('capital_gains', 'ltcg_any_other_asset', e)}
          />
        </Box>
      </Paper>

      <FormSectionHeader title="House Property Income" />
      
      <Paper variant="outlined" sx={{ p: 3 }}>
        {/* House Property Income */}
        <Box 
          sx={{ 
            width: '100%', 
            display: 'flex',
            justifyContent: 'left',
            mb: 2
          }}
        >
          <Typography variant="h6" color="primary">Income from House Property</Typography>
        </Box>
        
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: 3,
            width: '100%'
          }}
        >
          <Tooltip title="Occupancy Status" placement="top-start" arrow>
            <FormControl fullWidth>
              <InputLabel>Occupancy Status</InputLabel>
              <Select
                value={taxationData.house_property.occupancy_status || 'Self-Occupied'}
                label="Occupancy Status"
                onChange={(e) => handleSelectChange('house_property', 'occupancy_status', e)}
                onFocus={(e) => handleTextFieldFocus('house_property', 'occupancy_status', e)}
              >
                {occupancyStatuses.map((status) => (
                  <MenuItem key={status} value={status}>
                    {status}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Tooltip>
          
          <TextField
            fullWidth
            label="Rent Income"
            type="text"
            value={formatIndianNumber(taxationData.house_property.rent_income)}
            onChange={(e) => handleTextFieldChange('house_property', 'rent_income', e)}
            InputProps={{ startAdornment: '₹' }}
            disabled={taxationData.house_property.occupancy_status === 'Self-Occupied'}
            onFocus={(e) => handleTextFieldFocus('house_property', 'rent_income', e)}
          />
          
          <TextField
            fullWidth
            label="Property Tax"
            type="text"
            value={formatIndianNumber(taxationData.house_property.property_tax)}
            onChange={(e) => handleTextFieldChange('house_property', 'property_tax', e)}
            InputProps={{ startAdornment: '₹' }}
            disabled={taxationData.house_property.occupancy_status === 'Self-Occupied'}
            onFocus={(e) => handleTextFieldFocus('house_property', 'property_tax', e)}
          />
          
          <TextField
            fullWidth
            label="Interest on Home Loan"
            type="text"
            value={formatIndianNumber(taxationData.house_property.interest_on_home_loan)}
            onChange={(e) => handleTextFieldChange('house_property', 'interest_on_home_loan', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('house_property', 'interest_on_home_loan', e)}
          />
          
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
              onChange={(e) => handleTextFieldChange('house_property', 'pre_construction_loan_interest', e)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleTextFieldFocus('house_property', 'pre_construction_loan_interest', e)}
            />
          </Tooltip>
          
          <TextField
            fullWidth
            label="Property Address"
            type="text"
            multiline
            rows={4}
            value={taxationData.house_property.property_address || ''}
            onChange={(e) => handleTextFieldChange('house_property', 'property_address', e)}
            onFocus={(e) => handleTextFieldFocus('house_property', 'property_address', e)}
            placeholder="Enter complete property address"
          />
        </Box>
      </Paper>
    </Box>
  );
};

export default OtherIncomeSection; 