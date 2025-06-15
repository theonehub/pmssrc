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
          {/* Short Term Capital Gains */}
          <TextField
            fullWidth
            label="Short Term Capital Gains (111A)"
            type="text"
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('capital_gains', 'stcg_111a', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('capital_gains', 'stcg_111a', e)}
          />
          
          {/* Long Term Capital Gains */}
          <TextField
            fullWidth
            label="Long Term Capital Gains (112A)"
            type="text"
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('capital_gains', 'ltcg_112a', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('capital_gains', 'ltcg_112a', e)}
          />
        </Box>
      </Paper>

      <FormSectionHeader title="Leave Encashment" />
      <Paper variant="outlined" sx={{ p: 3 }}>
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: 3,
            width: '100%'
          }}
        >
          {/* Leave Encashment Income */}
          <TextField
            fullWidth
            label="Leave Encashment Income"
            type="text"
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('leave_encashment', 'income_received', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('leave_encashment', 'income_received', e)}
          />
          
          {/* Leave Days Encashed */}
          <TextField
            fullWidth
            label="Leave Days Encashed"
            type="number"
            value={0}
            onChange={(e) => handleTextFieldChange('leave_encashment', 'leave_encashed', e)}
            onFocus={(e) => handleTextFieldFocus('leave_encashment', 'leave_encashed', e)}
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
          {/* Property Address */}
          <TextField
            fullWidth
            label="Property Address"
            type="text"
            value={''}
            onChange={(e) => handleTextFieldChange('house_property', 'property_address', e)}
            onFocus={(e) => handleTextFieldFocus('house_property', 'property_address', e)}
          />
          
          {/* Occupancy Status */}
          <FormControl fullWidth>
            <InputLabel>Occupancy Status</InputLabel>
            <Select
              value={'Self-Occupied'}
              label="Occupancy Status"
              onChange={(e) => handleSelectChange('house_property', 'occupancy_status', e)}
            >
              <MenuItem value="Self-Occupied">Self-Occupied</MenuItem>
              <MenuItem value="Let Out">Let Out</MenuItem>
              <MenuItem value="Deemed Let Out">Deemed Let Out</MenuItem>
            </Select>
          </FormControl>
          
          {/* Rent Income */}
          <TextField
            fullWidth
            label="Rent Income"
            type="text"
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('house_property', 'rent_income', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('house_property', 'rent_income', e)}
          />
          
          {/* Property Tax */}
          <TextField
            fullWidth
            label="Property Tax"
            type="text"
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('house_property', 'property_tax', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('house_property', 'property_tax', e)}
          />
          
          {/* Interest on Home Loan */}
          <TextField
            fullWidth
            label="Interest on Home Loan"
            type="text"
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('house_property', 'interest_on_home_loan', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('house_property', 'interest_on_home_loan', e)}
          />
        </Box>
      </Paper>
    </Box>
  );
};

export default OtherIncomeSection; 