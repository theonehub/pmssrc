import React from 'react';
import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Box,
  SelectChangeEvent
} from '@mui/material';
import FormSectionHeader from '../../components/FormSectionHeader';
import { formatIndianNumber } from '../../utils/taxationUtils';
// TaxationData import removed as it's not used

interface LoanSectionProps {
  handleNestedInputChange: (
    section: string,
    subsection: string,
    field: string,
    value: string | number
  ) => void;
  handleNestedFocus: (
    section: string,
    subsection: string,
    field: string,
    value: string | number
  ) => void;
}

/**
 * Loan Perquisites Section
 */
const LoanSection: React.FC<LoanSectionProps> = ({
  handleNestedInputChange,
  handleNestedFocus
}) => {
  const handleSelectChange = (field: string, event: SelectChangeEvent<string>): void => {
    handleNestedInputChange('salary', 'perquisites', field, event.target.value);
  };

  const handleTextFieldChange = (field: string, event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>): void => {
    handleNestedInputChange('salary', 'perquisites', field, event.target.value);
  };

  const handleTextFieldFocus = (field: string, event: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement>): void => {
    handleNestedFocus('salary', 'perquisites', field, event.target.value);
  };

  return (
    <>
      <FormSectionHeader title="Interest-free/Concessional Loan" />
      
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: 3,
          width: '100%'
        }}
      >
        {/* Loan Type */}
        <FormControl fullWidth>
          <InputLabel>Loan Type</InputLabel>
          <Select
            value={'Personal'}
            label="Loan Type"
            onChange={(e) => handleSelectChange('loan_type', e)}
          >
            <MenuItem value="Personal">Personal</MenuItem>
            <MenuItem value="Housing">Housing</MenuItem>
            <MenuItem value="Vehicle">Vehicle</MenuItem>
            <MenuItem value="Education">Education</MenuItem>
            <MenuItem value="Medical">Medical</MenuItem>
            <MenuItem value="Other">Other</MenuItem>
          </Select>
        </FormControl>
        
        {/* Loan Amount */}
        <TextField
          fullWidth
          label="Loan Amount"
          type="text"
          value={formatIndianNumber(0)}
          onChange={(e) => handleTextFieldChange('loan_amount', e)}
          InputProps={{ startAdornment: '₹' }}
          onFocus={(e) => handleTextFieldFocus('loan_amount', e)}
        />
        
        {/* Loan Interest Rate (Company) */}
        <TextField
          fullWidth
          label="Interest Rate (Company)"
          type="text"
          value={formatIndianNumber(0)}
          onChange={(e) => handleTextFieldChange('loan_interest_rate_company', e)}
          InputProps={{ endAdornment: '%' }}
          onFocus={(e) => handleTextFieldFocus('loan_interest_rate_company', e)}
        />
        
        {/* Loan Interest Rate (SBI) */}
        <TextField
          fullWidth
          label="Interest Rate (SBI)"
          type="text"
          value={formatIndianNumber(0)}
          onChange={(e) => handleTextFieldChange('loan_interest_rate_sbi', e)}
          InputProps={{ endAdornment: '%' }}
          onFocus={(e) => handleTextFieldFocus('loan_interest_rate_sbi', e)}
        />
        
        {/* Loan Start Date */}
        <TextField
          fullWidth
          label="Loan Start Date"
          type="date"
          value={''}
          onChange={(e) => handleTextFieldChange('loan_start_date', e)}
          InputLabelProps={{ shrink: true }}
        />
        
        {/* Loan End Date */}
        <TextField
          fullWidth
          label="Loan End Date"
          type="date"
          value={''}
          onChange={(e) => handleTextFieldChange('loan_end_date', e)}
          InputLabelProps={{ shrink: true }}
        />
      </Box>
    </>
  );
};

export default LoanSection; 