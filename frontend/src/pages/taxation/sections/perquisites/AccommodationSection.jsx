import React from 'react';
import {
  Grid,
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
  Tooltip
} from '@mui/material';
import FormSectionHeader from '../../components/FormSectionHeader';
import { formatIndianNumber } from '../../utils/taxationUtils';

/**
 * Accommodation Perquisites Section
 * @param {Object} props - Component props
 * @param {Object} props.taxationData - Taxation data state
 * @param {Function} props.handleNestedInputChange - Function to handle nested input change
 * @param {Function} props.handleNestedFocus - Function to handle nested focus
 * @returns {JSX.Element} Accommodation section component
 */
const AccommodationSection = ({
  taxationData,
  handleNestedInputChange,
  handleNestedFocus
}) => {
  return (
    <>
      <FormSectionHeader title="Accommodation" />
      
      <Grid container spacing={3}>
        {/* Accommodation Type */}
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Accommodation Type</InputLabel>
            <Select
              value={taxationData.salary.perquisites?.accommodation_provided || 'Employer-Owned'}
              label="Accommodation Type"
              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'accommodation_provided', e.target.value)}
            >
              <MenuItem value="Employer-Owned">Employer-Owned</MenuItem>
              <MenuItem value="Govt">Government</MenuItem>
              <MenuItem value="Employer-Leased">Employer-Leased</MenuItem>
              <MenuItem value="Hotel">Hotel (for 15 days or more)</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        
        {/* City Population Type */}
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>City Population</InputLabel>
            <Select
              value={taxationData.salary.perquisites?.accommodation_city_population || 'Exceeding 40 lakhs in 2011 Census'}
              label="City Population"
              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'accommodation_city_population', e.target.value)}
            >
              <MenuItem value="Exceeding 40 lakhs in 2011 Census">Exceeding 40 lakhs in 2011 Census</MenuItem>
              <MenuItem value="Between 15-40 lakhs in 2011 Census">Between 15-40 lakhs in 2011 Census</MenuItem>
              <MenuItem value="Below 15 lakhs in 2011 Census">Below 15 lakhs in 2011 Census</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        
        {/* Accommodation Rent */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Accommodation Rent"
            type="text"
            value={formatIndianNumber(taxationData.salary.perquisites?.accommodation_rent || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'accommodation_rent', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'accommodation_rent', e.target.value)}
          />
        </Grid>
        
        {/* Government License Fees */}
        {taxationData.salary.perquisites?.accommodation_provided === 'Govt' && (
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Government License Fees"
              type="text"
              value={formatIndianNumber(taxationData.salary.perquisites?.accommodation_govt_lic_fees || 0)}
              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'accommodation_govt_lic_fees', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'accommodation_govt_lic_fees', e.target.value)}
            />
          </Grid>
        )}
        <Box 
          sx={{ 
            width: '100%', 
            display: 'flex',
            justifyContent: 'left'
          }}
        >
          <Typography variant="h6" color="primary">Furniture</Typography>
        </Box>
        <Divider sx={{ my: 0, width: '100%' }} />
        {/* Furniture Owned */}
        <Grid item xs={12} md={6}>
          <Tooltip title= {
            <>
            Furniture Ownership:<br/>
            - Employer's: Taxable amount 10% of Employer's Furniture Cost difference Employee Contibution.<br/>
            - Non-Employer's: Employer\'s Furniture Cost difference Employee Contibution.<br/>
            </>
          }
          placement="top"
          arrow
          >
          <FormControlLabel
            control={
              <Checkbox
                checked={!!taxationData.salary.perquisites?.is_furniture_owned}
                onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'is_furniture_owned', e.target.checked)}
              />
            }
              label="Employer-Owned"
            />
          </Tooltip>
        </Grid>
        {/* Furniture Cost to Employer */}
        <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Employer's Cost"
                type="text"
                value={formatIndianNumber(taxationData.salary.perquisites?.furniture_cost_to_employer || 0)}
                onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'furniture_cost_to_employer', e.target.value)}
                InputProps={{ startAdornment: '₹' }}
                onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'furniture_cost_to_employer', e.target.value)}
              />
            </Grid>
            
            {/* Furniture Cost Paid by Employee */}
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Employee's Contribution"
                type="text"
                value={formatIndianNumber(taxationData.salary.perquisites?.furniture_cost_paid_by_employee || 0)}
                onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'furniture_cost_paid_by_employee', e.target.value)}
                InputProps={{ startAdornment: '₹' }}
                onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'furniture_cost_paid_by_employee', e.target.value)}
              />
            </Grid>
        
      </Grid>
    </>
  );
};

export default AccommodationSection; 