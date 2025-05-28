import React from 'react';
import {
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
  Divider,
  Tooltip,
  SelectChangeEvent
} from '@mui/material';
import FormSectionHeader from '../../components/FormSectionHeader';
import { formatIndianNumber } from '../../utils/taxationUtils';
import { TaxationData } from '../../../../types';

interface MovableAssetsSectionProps {
  taxationData: TaxationData;
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
 * Movable Assets Perquisites Section
 */
const MovableAssetsSection: React.FC<MovableAssetsSectionProps> = ({
  taxationData,
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
      <FormSectionHeader title="Movable Assets Other then Computer(Usage)" />
      
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: 3,
          width: '100%'
        }}
      >
        {/* Asset Type */}
        <FormControl fullWidth>
          <InputLabel>Asset Ownership</InputLabel>
          <Select
            value={taxationData.salary.perquisites?.mau_ownership || 'Employer-Owned'}
            label="Asset Ownership"
            onChange={(e) => handleSelectChange('movable_asset_ownership', e)}
          >
            <MenuItem value="Employer-Owned">Employer-Owned</MenuItem>
            <MenuItem value="Employer-Hired">Employer-Hired</MenuItem>
          </Select>
        </FormControl>
        
        {/* Asset Value to Employer */}
        <TextField
          fullWidth
          label="Asset Value to Employer"
          type="text"
          value={formatIndianNumber(taxationData.salary.perquisites?.mau_value_to_employer || 0)}
          onChange={(e) => handleTextFieldChange('mau_value_to_employer', e)}
          InputProps={{ startAdornment: '₹' }}
          onFocus={(e) => handleTextFieldFocus('mau_value_to_employer', e)}
        />
        
        {/* Asset Value to Employee */}
        <TextField
          fullWidth
          label="Amount Paid by Employee"
          type="text"
          value={formatIndianNumber(taxationData.salary.perquisites?.mau_value_to_employee || 0)}
          onChange={(e) => handleTextFieldChange('mau_value_to_employee', e)}
          InputProps={{ startAdornment: '₹' }}
          onFocus={(e) => handleTextFieldFocus('mau_value_to_employee', e)}
        />
      </Box>

      <Box 
        sx={{ 
          width: '100%', 
          display: 'flex',
          justifyContent: 'left',
          mt: 3,
          mb: 2
        }}
      >
        <Typography variant="h6" color="primary">Movable Assets(Transfer)</Typography>
      </Box>
      <Divider sx={{ my: 0, width: '100%' }} />
      
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: 3,
          width: '100%',
          mt: 2
        }}
      >
        <FormControl fullWidth>
          <InputLabel>Asset Type</InputLabel>
          <Tooltip 
            title="Electronic items do not include household appliances (like Washing machine, microwave)"
            placement="top"
          >
            <Select
              value={taxationData.salary.perquisites?.mat_type || 'Electronics'}
              label="Asset Type"
              onChange={(e) => handleSelectChange('mat_type', e)}
            >
              <MenuItem value="Electronics">Electronics</MenuItem>
              <MenuItem value="Motor Vehicle">Motor Vehicle</MenuItem>
              <MenuItem value="Other">Other</MenuItem>
            </Select>
          </Tooltip>
        </FormControl>

        {/* Asset Value to Employer */}
        <TextField
          fullWidth
          label="Asset Value to Employer"
          type="text"
          value={formatIndianNumber(taxationData.salary.perquisites?.mat_value_to_employer || 0)}
          onChange={(e) => handleTextFieldChange('mat_value_to_employer', e)}
          InputProps={{ startAdornment: '₹' }}
          onFocus={(e) => handleTextFieldFocus('mat_value_to_employer', e)}
        />
        
        {/* Asset Value to Employee */}
        <TextField
          fullWidth
          label="Amount Paid by Employee"
          type="text"
          value={formatIndianNumber(taxationData.salary.perquisites?.mat_value_to_employee || 0)}
          onChange={(e) => handleTextFieldChange('mat_value_to_employee', e)}
          InputProps={{ startAdornment: '₹' }}
          onFocus={(e) => handleTextFieldFocus('mat_value_to_employee', e)}
        />

        {/* Years of Use */}
        <TextField
          fullWidth
          label="Number of Completed Years of Use"
          type="number"
          inputProps={{ min: 0 }}
          value={taxationData.salary.perquisites?.mat_number_of_completed_years_of_use || 0}
          onChange={(e) => handleTextFieldChange('mat_number_of_completed_years_of_use', e)}
          onFocus={(e) => handleTextFieldFocus('mat_number_of_completed_years_of_use', e)}
        />
      </Box>
    </>
  );
};

export default MovableAssetsSection; 