import React from 'react';
import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  FormControlLabel,
  Checkbox,
  Box,
  Typography,
  Divider,
  Tooltip,
  SelectChangeEvent
} from '@mui/material';
import FormSectionHeader from '../../components/FormSectionHeader';
import { formatIndianNumber } from '../../utils/taxationUtils';
import { TaxationData } from '../../../../types';

interface AccommodationSectionProps {
  taxationData: TaxationData;
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
 * Accommodation Perquisites Section
 */
const AccommodationSection: React.FC<AccommodationSectionProps> = ({
  taxationData,
  handleNestedInputChange,
  handleNestedFocus
}) => {
  const handleSelectChange = (field: string, event: SelectChangeEvent<string>): void => {
    handleNestedInputChange('salary', 'perquisites', field, event.target.value);
  };

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
      <FormSectionHeader title="Accommodation" />
      
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: 3,
          width: '100%',
          mb: 3
        }}
      >
        {/* Accommodation Type */}
        <FormControl fullWidth>
          <InputLabel>Accommodation Type</InputLabel>
          <Select
            value={taxationData.salary.perquisites?.accommodation_provided || 'Employer-Owned'}
            label="Accommodation Type"
            onChange={(e) => handleSelectChange('accommodation_provided', e)}
          >
            <MenuItem value="Employer-Owned">Employer-Owned</MenuItem>
            <MenuItem value="Govt">Government</MenuItem>
            <MenuItem value="Employer-Leased">Employer-Leased</MenuItem>
            <MenuItem value="Hotel">Hotel (for 15 days or more)</MenuItem>
          </Select>
        </FormControl>
        
        {/* City Population Type */}
        <FormControl fullWidth>
          <InputLabel>City Population</InputLabel>
          <Select
            value={taxationData.salary.perquisites?.accommodation_city_population || 'Exceeding 40 lakhs in 2011 Census'}
            label="City Population"
            onChange={(e) => handleSelectChange('accommodation_city_population', e)}
          >
            <MenuItem value="Exceeding 40 lakhs in 2011 Census">Exceeding 40 lakhs in 2011 Census</MenuItem>
            <MenuItem value="Between 15-40 lakhs in 2011 Census">Between 15-40 lakhs in 2011 Census</MenuItem>
            <MenuItem value="Below 15 lakhs in 2011 Census">Below 15 lakhs in 2011 Census</MenuItem>
          </Select>
        </FormControl>
        
        {/* Accommodation Rent */}
        <TextField
          fullWidth
          label="Accommodation Rent"
          type="text"
          value={formatIndianNumber(taxationData.salary.perquisites?.accommodation_rent || 0)}
          onChange={(e) => handleTextFieldChange('accommodation_rent', e)}
          InputProps={{ startAdornment: '₹' }}
          onFocus={(e) => handleTextFieldFocus('accommodation_rent', e)}
        />
        
        {/* Government License Fees */}
        {taxationData.salary.perquisites?.accommodation_provided === 'Govt' && (
          <TextField
            fullWidth
            label="Government License Fees"
            type="text"
            value={formatIndianNumber(taxationData.salary.perquisites?.accommodation_govt_lic_fees || 0)}
            onChange={(e) => handleTextFieldChange('accommodation_govt_lic_fees', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('accommodation_govt_lic_fees', e)}
          />
        )}
      </Box>
      
      <Box 
        sx={{ 
          width: '100%', 
          display: 'flex',
          justifyContent: 'left',
          mt: 2,
          mb: 2
        }}
      >
        <Typography variant="h6" color="primary">Furniture</Typography>
      </Box>
      <Divider sx={{ my: 0, width: '100%', mb: 3 }} />
      
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: 3,
          width: '100%'
        }}
      >
        {/* Furniture Owned */}
        <Tooltip 
          title={
            <>
              Furniture Ownership:<br/>
              - Employer's: Taxable amount 10% of Employer's Furniture Cost difference Employee Contribution.<br/>
              - Non-Employer's: Employer's Furniture Cost difference Employee Contribution.<br/>
            </>
          }
          placement="top"
          arrow
        >
          <FormControlLabel
            control={
              <Checkbox
                checked={!!taxationData.salary.perquisites?.is_furniture_owned}
                onChange={(e) => handleCheckboxChange('is_furniture_owned', e)}
              />
            }
            label="Employer-Owned"
          />
        </Tooltip>
        
        {/* Furniture Cost to Employer */}
        <TextField
          fullWidth
          label="Employer's Cost"
          type="text"
          value={formatIndianNumber(taxationData.salary.perquisites?.furniture_cost_to_employer || 0)}
          onChange={(e) => handleTextFieldChange('furniture_cost_to_employer', e)}
          InputProps={{ startAdornment: '₹' }}
          onFocus={(e) => handleTextFieldFocus('furniture_cost_to_employer', e)}
        />
        
        {/* Furniture Cost Paid by Employee */}
        <TextField
          fullWidth
          label="Employee's Contribution"
          type="text"
          value={formatIndianNumber(taxationData.salary.perquisites?.furniture_cost_paid_by_employee || 0)}
          onChange={(e) => handleTextFieldChange('furniture_cost_paid_by_employee', e)}
          InputProps={{ startAdornment: '₹' }}
          onFocus={(e) => handleTextFieldFocus('furniture_cost_paid_by_employee', e)}
        />
      </Box>
    </>
  );
};

export default AccommodationSection; 