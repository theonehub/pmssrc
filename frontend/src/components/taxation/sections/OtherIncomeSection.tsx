import React from 'react';
import {
  Box,
  TextField,
  Typography,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent
} from '@mui/material';
import { TaxationData } from '../../../shared/types';
import { formatIndianNumber } from '../utils/taxationUtils';
import FormSectionHeader from '../components/FormSectionHeader';

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

  const handleSelectChange = (section: string, field: string, event: SelectChangeEvent<string>): void => {
    const newStatus = event.target.value;
    handleInputChange(section, field, newStatus);
  };

  const handleTextFieldChange = (section: string, field: string, event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>): void => {
    handleInputChange(section, field, event.target.value);
  };

  const handleTextFieldFocus = (section: string, field: string, event: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement>): void => {
    handleFocus(section, field, event.target.value);
  };
  
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
          {/* Other Income - Use actual property from TaxationData */}
          <TextField
            fullWidth
            label="Other Income"
            type="text"
            value={formatIndianNumber(taxationData.other_income?.other_miscellaneous_income || 0)}
            onChange={(e) => handleTextFieldChange('other_income', 'other_miscellaneous_income', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('other_income', 'other_miscellaneous_income', e)}
          />
          
          {/* House Property Income - Use actual property from TaxationData */}
          <TextField
            fullWidth
            label="House Property Income"
            type="text"
            value={formatIndianNumber(taxationData.house_property_income?.net_income || 0)}
            onChange={(e) => handleTextFieldChange('house_property_income', 'net_income', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('house_property_income', 'net_income', e)}
          />
          
          {/* Capital Gains - Use actual property from TaxationData */}
          <TextField
            fullWidth
            label="Capital Gains"
            type="text"
            value={formatIndianNumber((taxationData.capital_gains_income?.stcg_111a_equity_stt || 0) + (taxationData.capital_gains_income?.ltcg_112a_equity_stt || 0))}
            onChange={(e) => handleTextFieldChange('capital_gains_income', 'stcg_111a_equity_stt', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('capital_gains_income', 'stcg_111a_equity_stt', e)}
          />
          
          {/* Interest Income - placeholder since not in TaxationData */}
          <TextField
            fullWidth
            label="Interest from Savings Account"
            type="text"
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('other_sources', 'interest_savings', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('other_sources', 'interest_savings', e)}
          />
          
          {/* Post Office Interest */}
          <TextField
            fullWidth
            label="Post Office Interest"
            type="text"
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('other_sources', 'post_office_interest', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('other_sources', 'post_office_interest', e)}
          />
          
          {/* Dividend Income - placeholder since not in TaxationData */}
          <TextField
            fullWidth
            label="Dividend Income"
            type="text"
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('other_sources', 'dividend_income', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('other_sources', 'dividend_income', e)}
          />
          
          {/* Gifts - placeholder since not in TaxationData */}
          <TextField
            fullWidth
            label="Gifts (Cash/Kind)"
            type="text"
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('other_sources', 'gifts', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('other_sources', 'gifts', e)}
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
          {/* Business Professional Income - placeholder */}
          <TextField
            fullWidth
            label="Business Professional Income"
            type="text"
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('other_sources', 'business_professional_income', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('other_sources', 'business_professional_income', e)}
          />
        </Box>
      </Paper>

      <FormSectionHeader title="Capital Gains" />
      <Paper variant="outlined" sx={{ p: 3 }}>
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: 3,
            width: '100%'
          }}
        >
          {/* Short Term Capital Gains - 111A (Equity with STT) */}
          <TextField
            fullWidth
            label="STCG 111A (Equity with STT)"
            type="text"
            value={formatIndianNumber(taxationData.capital_gains_income?.stcg_111a_equity_stt || 0)}
            onChange={(e) => handleTextFieldChange('capital_gains_income', 'stcg_111a_equity_stt', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('capital_gains_income', 'stcg_111a_equity_stt', e)}
            helperText="Taxed at 20%"
          />
          
          {/* Short Term Capital Gains - Other Assets */}
          <TextField
            fullWidth
            label="STCG Other Assets"
            type="text"
            value={formatIndianNumber(taxationData.capital_gains_income?.stcg_other_assets || 0)}
            onChange={(e) => handleTextFieldChange('capital_gains_income', 'stcg_other_assets', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('capital_gains_income', 'stcg_other_assets', e)}
            helperText="Taxed at slab rates"
          />
          
          {/* Short Term Capital Gains - Debt Mutual Funds */}
          <TextField
            fullWidth
            label="STCG Debt Mutual Funds"
            type="text"
            value={formatIndianNumber(taxationData.capital_gains_income?.stcg_debt_mf || 0)}
            onChange={(e) => handleTextFieldChange('capital_gains_income', 'stcg_debt_mf', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('capital_gains_income', 'stcg_debt_mf', e)}
            helperText="Taxed at slab rates"
          />
          
          {/* Long Term Capital Gains - 112A (Equity with STT) */}
          <TextField
            fullWidth
            label="LTCG 112A (Equity with STT)"
            type="text"
            value={formatIndianNumber(taxationData.capital_gains_income?.ltcg_112a_equity_stt || 0)}
            onChange={(e) => handleTextFieldChange('capital_gains_income', 'ltcg_112a_equity_stt', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('capital_gains_income', 'ltcg_112a_equity_stt', e)}
            helperText="12.5% tax with ₹1.25L exemption"
          />
          
          {/* Long Term Capital Gains - Other Assets */}
          <TextField
            fullWidth
            label="LTCG Other Assets"
            type="text"
            value={formatIndianNumber(taxationData.capital_gains_income?.ltcg_other_assets || 0)}
            onChange={(e) => handleTextFieldChange('capital_gains_income', 'ltcg_other_assets', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('capital_gains_income', 'ltcg_other_assets', e)}
            helperText="Taxed at 12.5%"
          />
          
          {/* Long Term Capital Gains - Debt Mutual Funds */}
          <TextField
            fullWidth
            label="LTCG Debt Mutual Funds"
            type="text"
            value={formatIndianNumber(taxationData.capital_gains_income?.ltcg_debt_mf || 0)}
            onChange={(e) => handleTextFieldChange('capital_gains_income', 'ltcg_debt_mf', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('capital_gains_income', 'ltcg_debt_mf', e)}
            helperText="Taxed at 12.5%"
          />
        </Box>
      </Paper>

      <FormSectionHeader title="House Property" />
      <Paper variant="outlined" sx={{ p: 3 }}>
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: 3,
            width: '100%'
          }}
        >
          {/* Property Address - Multi-line text box */}
          <TextField
            fullWidth
            label="Property Address"
            multiline
            rows={3}
            value={taxationData.other_income?.house_property_income?.address || ''}
            onChange={(e) => handleTextFieldChange('other_income.house_property_income', 'address', e)}
            onFocus={(e) => handleTextFieldFocus('other_income.house_property_income', 'address', e)}
          />
          
          {/* Property Type */}
          <FormControl fullWidth>
            <InputLabel>Property Type</InputLabel>
            <Select
              value={taxationData.other_income?.house_property_income?.property_type || 'Self-Occupied'}
              label="Property Type"
              onChange={(e) => handleSelectChange('other_income.house_property_income', 'property_type', e)}
            >
              <MenuItem value="Self-Occupied">Self-Occupied</MenuItem>
              <MenuItem value="Let-Out">Let-Out</MenuItem>
            </Select>
          </FormControl>
          
          {/* Annual Rent Received */}
          <TextField
            fullWidth
            label="Annual Rent Received"
            type="text"
            value={formatIndianNumber(taxationData.other_income?.house_property_income?.annual_rent_received || 0)}
            onChange={(e) => handleTextFieldChange('other_income.house_property_income', 'annual_rent_received', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('other_income.house_property_income', 'annual_rent_received', e)}
          />
          
          {/* Municipal Taxes Paid - CORRECTED field mapping */}
          <TextField
            fullWidth
            label="Municipal Taxes Paid"
            type="text"
            value={formatIndianNumber(taxationData.other_income?.house_property_income?.municipal_taxes_paid || 0)}
            onChange={(e) => handleTextFieldChange('other_income.house_property_income', 'municipal_taxes_paid', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('other_income.house_property_income', 'municipal_taxes_paid', e)}
          />
          
          {/* Home Loan Interest - CORRECTED field mapping */}
          <TextField
            fullWidth
            label="Home Loan Interest"
            type="text"
            value={formatIndianNumber(taxationData.other_income?.house_property_income?.home_loan_interest || 0)}
            onChange={(e) => handleTextFieldChange('other_income.house_property_income', 'home_loan_interest', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('other_income.house_property_income', 'home_loan_interest', e)}
          />
          
          {/* Pre-construction Interest - ADDED missing field */}
          <TextField
            fullWidth
            label="Pre-construction Interest"
            type="text"
            value={formatIndianNumber(taxationData.other_income?.house_property_income?.pre_construction_interest || 0)}
            onChange={(e) => handleTextFieldChange('other_income.house_property_income', 'pre_construction_interest', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('other_income.house_property_income', 'pre_construction_interest', e)}
          />
        </Box>
      </Paper>
    </Box>
  );
};

export default OtherIncomeSection; 