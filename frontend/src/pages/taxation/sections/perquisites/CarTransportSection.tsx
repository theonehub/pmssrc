import React from 'react';
import {
  TextField,
  FormControlLabel,
  Checkbox,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Divider,
  Tooltip,
  Typography,
  SelectChangeEvent
} from '@mui/material';
import FormSectionHeader from '../../components/FormSectionHeader';
import { formatIndianNumber } from '../../utils/taxationUtils';
import { TaxationData } from '../../../../shared/types';

interface CarTransportSectionProps {
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
 * Car & Transport Perquisites Section
 */
const CarTransportSection: React.FC<CarTransportSectionProps> = ({
  handleNestedInputChange,
  handleNestedFocus
}) => {
  const handleCheckboxChange = (field: string, event: React.ChangeEvent<HTMLInputElement>): void => {
    handleNestedInputChange('salary', 'perquisites', field, event.target.checked);
  };

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
      <FormSectionHeader title="Car & Transport" />
      
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: 3,
          width: '100%',
          mb: 3
        }}
      >
        {/* Car rating */}
        <FormControlLabel
          control={
            <Checkbox
              checked={false}
              onChange={(e) => handleCheckboxChange('is_car_rating_higher', e)}
            />
          }
          label="Car with engine capacity exceeding 1.6L"
        />
        
        {/* Car ownership */}
        <FormControlLabel
          control={
            <Checkbox
              checked={false}
              onChange={(e) => handleCheckboxChange('is_car_employer_owned', e)}
            />
          }
          label="Employer-Owned"
        />
        
        {/* Driver provided */}
        <FormControlLabel
          control={
            <Checkbox
              checked={false}
              onChange={(e) => handleCheckboxChange('is_driver_provided', e)}
            />
          }
          label="Driver provided by employer"
        />
        
        {/* Expenses reimbursed */}
        <FormControlLabel
          control={
            <Checkbox
              checked={false}
              onChange={(e) => handleCheckboxChange('is_expenses_reimbursed', e)}
            />
          }
          label="Employer-Reimburse Expenses"
        />
        
        {/* Car usage type */}
        <FormControl fullWidth>
          <InputLabel>Car Usage</InputLabel>
          <Select
            value={'Personal'}
            label="Car Usage"
            onChange={(e) => handleSelectChange('car_use', e)}
          >
            <MenuItem value="Personal">Personal Only</MenuItem>
            <MenuItem value="Official">Official Only</MenuItem>
            <MenuItem value="Mixed">Personal & Official</MenuItem>
          </Select>
        </FormControl>
        
        {/* Car cost to employer */}
        <TextField
          fullWidth
          label="Car Cost to Employer"
          type="text"
          value={formatIndianNumber(0)}
          onChange={(e) => handleTextFieldChange('car_cost_to_employer', e)}
          InputProps={{ startAdornment: '₹' }}
          onFocus={(e) => handleTextFieldFocus('car_cost_to_employer', e)}
        />
        
        {/* Month count for car usage */}
        <TextField
          fullWidth
          label="Months of Car Usage"
          type="number"
          inputProps={{ min: 0, max: 12 }}
          value={0}
          onChange={(e) => handleTextFieldChange('month_counts', e)}
          onFocus={(e) => handleTextFieldFocus('month_counts', e)}
        />
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
        <Typography variant="h6" color="primary">Other Vehicle</Typography>
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
        {/* Other vehicle cost to employer */}
        <Tooltip 
          title="Vehicle other than car"
          placement="top"
        >
          <TextField
            fullWidth
            label="Other Vehicle Cost to Employer"
            type="text"
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('other_vehicle_cost_to_employer', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('other_vehicle_cost_to_employer', e)}
          />
        </Tooltip>
        
        {/* Month count for other vehicle */}
        <TextField
          fullWidth
          label="Months of Other Vehicle Usage"
          type="number"
          inputProps={{ min: 0, max: 12 }}
          value={0}
          onChange={(e) => handleTextFieldChange('other_vehicle_month_counts', e)}
          onFocus={(e) => handleTextFieldFocus('other_vehicle_month_counts', e)}
        />
      </Box>
    </>
  );
};

export default CarTransportSection; 