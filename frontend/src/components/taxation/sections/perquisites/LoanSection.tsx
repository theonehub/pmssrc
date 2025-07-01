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
import DatePicker from 'react-datepicker';
import "react-datepicker/dist/react-datepicker.css";
import FormSectionHeader from '../../components/FormSectionHeader';
import { formatIndianNumber } from '../../utils/taxationUtils';

// Add custom styles for the date picker
const datePickerStyles = `
  .date-picker-wrapper .react-datepicker-wrapper {
    width: 100%;
  }
  .date-picker-wrapper .react-datepicker__input-container input {
    width: 100%;
    padding: 16.5px 14px;
    border: 1px solid rgba(0, 0, 0, 0.23);
    border-radius: 4px;
    font-size: 16px;
    background-color: transparent;
    transition: border-color 0.2s;
  }
  .date-picker-wrapper .react-datepicker__input-container input:focus {
    outline: none;
    border-color: #1976d2;
    border-width: 2px;
  }
  .date-picker-wrapper .react-datepicker__input-container input:hover {
    border-color: rgba(0, 0, 0, 0.87);
  }
`;
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

  const handleDateChange = (field: string, date: Date | null): void => {
    const dateString = date ? date.toISOString().split('T')[0] : '';
    handleNestedInputChange('salary', 'perquisites', field, dateString || '');
  };

  return (
    <>
      <style>{datePickerStyles}</style>
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
        
        {/* EMI Amount */}
        <TextField
          fullWidth
          label="EMI Amount"
          type="text"
          value={formatIndianNumber(0)}
          onChange={(e) => handleTextFieldChange('emi_amount', e)}
          InputProps={{ startAdornment: '₹' }}
          onFocus={(e) => handleTextFieldFocus('emi_amount', e)}
        />

        {/* Loan Start Date */}
        <Box sx={{ display: 'flex', flexDirection: 'column' }}>
          <label style={{ marginBottom: '8px', fontSize: '14px', color: 'rgba(0, 0, 0, 0.6)' }}>
            Loan Start Date
          </label>
          <div style={{ width: '100%' }}>
            <DatePicker
              selected={null}
              onChange={(date) => handleDateChange('loan_start_date', date)}
              placeholderText="Select loan start date"
              dateFormat="dd/MM/yyyy"
              className="form-control"
              wrapperClassName="date-picker-wrapper"
            />
          </div>
        </Box>
      </Box>
    </>
  );
};

export default LoanSection; 