import React from 'react';
import {
  TextField,
  FormControlLabel,
  Checkbox,
  Box
} from '@mui/material';
import FormSectionHeader from '../../components/FormSectionHeader';
import { formatIndianNumber } from '../../utils/taxationUtils';
// TaxationData import removed as it's not used

interface GasElectricityWaterSectionProps {
  handleNestedInputChange: (
    section: string,
    subsection: string,
    field: string,
    value: string | number | boolean
  ) => void;
  handleNestedFocus: (
    section: string,
    subsection: string,
    field: string,
    value: string | number
  ) => void;
}

/**
 * Gas, Electricity, Water Section for Perquisites
 */
const GasElectricityWaterSection: React.FC<GasElectricityWaterSectionProps> = ({
  handleNestedInputChange,
  handleNestedFocus
}) => {
  const handleCheckboxChange = (field: string, event: React.ChangeEvent<HTMLInputElement>): void => {
    handleNestedInputChange('salary', 'perquisites', field, event.target.checked);
  };

  const handleTextFieldChange = (field: string, event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>): void => {
    handleNestedInputChange('salary', 'perquisites', field, event.target.value);
  };

  const handleTextFieldFocus = (field: string, event: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement>): void => {
    handleNestedFocus('salary', 'perquisites', field, event.target.value);
  };

  return (
    <>
      <FormSectionHeader title="Gas, Electricity, Water" />
      
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: 3,
          width: '100%'
        }}
      >
        {/* Gas Section */}
        <FormControlLabel
          control={
            <Checkbox
              checked={false}
              onChange={(e) => handleCheckboxChange('is_gas_manufactured_by_employer', e)}
            />
          }
          label="Gas Manufactured by Employer"
        />
        
        <TextField
          fullWidth
          label="Gas Manufacturing Cost to Employer"
          type="text"
          value={formatIndianNumber(0)}
          onChange={(e) => handleTextFieldChange('gas_amount_paid_by_employer', e)}
          InputProps={{ startAdornment: '₹' }}
          onFocus={(e) => handleTextFieldFocus('gas_amount_paid_by_employer', e)}
        />
        
        <TextField
          fullWidth
          label="Gas Amount Paid by Employee"
          type="text"
          value={formatIndianNumber(0)}
          onChange={(e) => handleTextFieldChange('gas_amount_paid_by_employee', e)}
          InputProps={{ startAdornment: '₹' }}
          onFocus={(e) => handleTextFieldFocus('gas_amount_paid_by_employee', e)}
        />
        
        {/* Electricity Section */}
        <FormControlLabel
          control={
            <Checkbox
              checked={false}
              onChange={(e) => handleCheckboxChange('is_electricity_manufactured_by_employer', e)}
            />
          }
          label="Electricity Manufactured by Employer"
        />
        
        <TextField
          fullWidth
          label="Electricity Manufacturing Cost to Employer"
          type="text"
          value={formatIndianNumber(0)}
          onChange={(e) => handleTextFieldChange('electricity_amount_paid_by_employer', e)}
          InputProps={{ startAdornment: '₹' }}
          onFocus={(e) => handleTextFieldFocus('electricity_amount_paid_by_employer', e)}
        />
        
        <TextField
          fullWidth
          label="Electricity Amount Paid by Employee"
          type="text"
          value={formatIndianNumber(0)}
          onChange={(e) => handleTextFieldChange('electricity_amount_paid_by_employee', e)}
          InputProps={{ startAdornment: '₹' }}
          onFocus={(e) => handleTextFieldFocus('electricity_amount_paid_by_employee', e)}
        />
        
        {/* Water Section */}
        <FormControlLabel
          control={
            <Checkbox
              checked={false}
              onChange={(e) => handleCheckboxChange('is_water_manufactured_by_employer', e)}
            />
          }
          label="Water Manufactured by Employer"
        />
        
        <TextField
          fullWidth
          label="Water Manufacturing Cost to Employer"
          type="text"
          value={formatIndianNumber(0)}
          onChange={(e) => handleTextFieldChange('water_amount_paid_by_employer', e)}
          InputProps={{ startAdornment: '₹' }}
          onFocus={(e) => handleTextFieldFocus('water_amount_paid_by_employer', e)}
        />
        
        <TextField
          fullWidth
          label="Water Amount Paid by Employee"
          type="text"
          value={formatIndianNumber(0)}
          onChange={(e) => handleTextFieldChange('water_amount_paid_by_employee', e)}
          InputProps={{ startAdornment: '₹' }}
          onFocus={(e) => handleTextFieldFocus('water_amount_paid_by_employee', e)}
        />
      </Box>
    </>
  );
};

export default GasElectricityWaterSection; 