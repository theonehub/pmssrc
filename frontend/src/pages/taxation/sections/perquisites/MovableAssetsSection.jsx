import React from 'react';
import {
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
  Divider,
  Tooltip
} from '@mui/material';
import FormSectionHeader from '../../components/FormSectionHeader';
import { formatIndianNumber } from '../../utils/taxationUtils';

/**
 * Movable Assets Perquisites Section
 * @param {Object} props - Component props
 * @param {Object} props.taxationData - Taxation data state
 * @param {Function} props.handleNestedInputChange - Function to handle nested input change
 * @param {Function} props.handleNestedFocus - Function to handle nested focus
 * @returns {JSX.Element} Movable Assets section component
 */
const MovableAssetsSection = ({
  taxationData,
  handleNestedInputChange,
  handleNestedFocus
}) => {
  return (
    <>
      <FormSectionHeader title="Movable Assets Other then Computer(Usage)" />
      
      <Grid container spacing={3}>
        {/* Asset Type */}
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Asset Ownership</InputLabel>
            <Select
              value={taxationData.salary.perquisites?.mau_ownership || 'Employer-Owned'}
              label="Asset Ownership"
              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'movable_asset_ownership', e.target.value)}
            >
              <MenuItem value="Employer-Owned">Employer-Owned</MenuItem>
              <MenuItem value="Employer-Hired">Employer-Hired</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        
        {/* Asset Value to Employer */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Asset Value to Employer"
            type="text"
            value={formatIndianNumber(taxationData.salary.perquisites?.mau_value_to_employer || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'mau_value_to_employer', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'mau_value_to_employer', e.target.value)}
          />
        </Grid>
        
        {/* Asset Value to Employee */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Asset Value to Employee"
            type="text"
            value={formatIndianNumber(taxationData.salary.perquisites?.mau_value_to_employee || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'mau_value_to_employee', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'mau_value_to_employee', e.target.value)}
          />
        </Grid>

        <Box 
          sx={{ 
            width: '100%', 
            display: 'flex',
            justifyContent: 'left'
          }}
        >
          <Typography variant="h6" color="primary">Movable Assets(Transfer)</Typography>
        </Box>
        <Divider sx={{ my: 0, width: '100%' }} />
        
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Asset Type</InputLabel>
            <Tooltip title="Electronic items do not include household appliances (like Washing machine, microwave)">
            <Select
              value={taxationData.salary.perquisites?.mat_type || 'Electronics'}
              label="Asset Type"
              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'mat_type', e.target.value)}
            >
              <MenuItem value="Electronics">Electronics</MenuItem>
              <MenuItem value="Motor Vehicle">Motor Vehicle</MenuItem>
                <MenuItem value="Other">Other</MenuItem>
              </Select>
            </Tooltip>
          </FormControl>
        </Grid>

        {/* Asset Value to Employer */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Asset Value to Employer"
            type="text"
            value={formatIndianNumber(taxationData.salary.perquisites?.mat_value_to_employer || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'mat_value_to_employer', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'mat_value_to_employer', e.target.value)}
          />
        </Grid>
        
        {/* Asset Value to Employee */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Asset Value to Employee"
            type="text"
            value={formatIndianNumber(taxationData.salary.perquisites?.mat_value_to_employee || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'mat_value_to_employee', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'mat_value_to_employee', e.target.value)}
          />
        </Grid>

        {/* Years of Use */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Number of Completed Years of Use"
            type="number"
            inputProps={{ min: 0 }}
            value={taxationData.salary.perquisites?.number_of_completed_years_of_use || 0}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'mat_number_of_completed_years_of_use', e.target.value)}
            onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'mat_number_of_completed_years_of_use', e.target.value)}
          />
        </Grid>
      </Grid>
    </>
  );
};

export default MovableAssetsSection; 