import React from 'react';
import {
  Grid,
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
  Typography
} from '@mui/material';
import FormSectionHeader from '../../components/FormSectionHeader';
import { formatIndianNumber } from '../../utils/taxationUtils';

/**
 * Car & Transport Perquisites Section
 * @param {Object} props - Component props
 * @param {Object} props.taxationData - Taxation data state
 * @param {Function} props.handleNestedInputChange - Function to handle nested input change
 * @param {Function} props.handleNestedFocus - Function to handle nested focus
 * @returns {JSX.Element} Car & Transport section component
 */
const CarTransportSection = ({
  taxationData,
  handleNestedInputChange,
  handleNestedFocus
}) => {
  return (
    <>
      <FormSectionHeader title="Car & Transport" />
      <Grid container spacing={3}>
        {/* Car rating */}
        <Grid item xs={12} md={6}>
          <FormControlLabel
            control={
              <Checkbox
                checked={taxationData.salary.perquisites?.is_car_rating_higher || false}
                onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'is_car_rating_higher', e.target.checked)}
              />
            }
            label="Car with engine capacity exceeding 1.6L"
          />
        </Grid>
        
        {/* Car ownership */}
        <Grid item xs={12} md={6}>
          <FormControlLabel
            control={
              <Checkbox
                checked={taxationData.salary.perquisites?.is_car_employer_owned || false}
                onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'is_car_employer_owned', e.target.checked)}
              />
            }
            label="Employer-Owned"
          />
        </Grid>
        
        {/* Driver provided */}
        <Grid item xs={12} md={6}>
          <FormControlLabel
            control={
              <Checkbox
                checked={taxationData.salary.perquisites?.is_driver_provided || false}
                onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'is_driver_provided', e.target.checked)}
              />
            }
            label="Driver provided by employer"
          />
        </Grid>
        
        {/* Expenses reimbursed */}
        <Grid item xs={12} md={6}>
          <FormControlLabel
            control={
              <Checkbox
                checked={taxationData.salary.perquisites?.is_expenses_reimbursed || false}
                onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'is_expenses_reimbursed', e.target.checked)}
              />
            }
            label="Employer-Reimburse Expenses"
          />
        </Grid>
        <Box 
          sx={{ 
            width: '100%', 
            display: 'flex',
            justifyContent: 'left'
          }}
        >
        </Box>
        {/* Car usage type */}
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Car Usage</InputLabel>
            <Select
              value={taxationData.salary.perquisites?.car_use || 'Personal'}
              label="Car Usage"
              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'car_use', e.target.value)}
            >
              <MenuItem value="Personal">Personal Only</MenuItem>
              <MenuItem value="Official">Official Only</MenuItem>
              <MenuItem value="Mixed">Personal & Official</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        
        {/* Car cost to employer */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Car Cost to Employer"
            type="text"
            value={formatIndianNumber(taxationData.salary.perquisites?.car_cost_to_employer || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'car_cost_to_employer', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'car_cost_to_employer', e.target.value)}
          />
        </Grid>
        
        {/* Month count for car usage */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Months of Car Usage"
            type="number"
            inputProps={{ min: 0, max: 12 }}
            value={taxationData.salary.perquisites?.month_counts || 0}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'month_counts', e.target.value)}
            onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'month_counts', e.target.value)}
          />
        </Grid>
        <Box 
          sx={{ 
            width: '100%', 
            display: 'flex',
            justifyContent: 'left'
          }}
        >
          <Typography variant="h6" color="primary">Other Vehicle</Typography>
        </Box>
        <Divider sx={{ my: 0, width: '100%' }} />
        {/* Other vehicle cost to employer */}
        <Grid item xs={12} md={6}>
          <Tooltip 
            title="Vehicle other than car"
            placement="top"
          >
          <TextField
            fullWidth
            label="Other Vehicle Cost to Employer"
            type="text"
            value={formatIndianNumber(taxationData.salary.perquisites?.other_vehicle_cost_to_employer || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'other_vehicle_cost_to_employer', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'other_vehicle_cost_to_employer', e.target.value)}
          />
          </Tooltip>
        </Grid>
        
        {/* Month count for other vehicle */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Months of Other Vehicle Usage"
            type="number"
            inputProps={{ min: 0, max: 12 }}
            value={taxationData.salary.perquisites?.other_vehicle_month_counts || 0}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'other_vehicle_month_counts', e.target.value)}
            onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'other_vehicle_month_counts', e.target.value)}
          />
        </Grid>
      </Grid>
    </>
  );
};

export default CarTransportSection; 