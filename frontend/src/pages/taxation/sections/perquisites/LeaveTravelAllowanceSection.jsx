import React from 'react';
import {
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Tooltip
} from '@mui/material';
import FormSectionHeader from '../../components/FormSectionHeader';
import { formatIndianNumber } from '../../utils/taxationUtils';

/**
 * Leave Travel Allowance Perquisites Section
 * @param {Object} props - Component props
 * @param {Object} props.taxationData - Taxation data state
 * @param {Function} props.handleNestedInputChange - Function to handle nested input change
 * @param {Function} props.handleNestedFocus - Function to handle nested focus
 * @returns {JSX.Element} Leave Travel Allowance section component
 */
const LeaveTravelAllowanceSection = ({
  taxationData,
  handleNestedInputChange,
  handleNestedFocus
}) => {
  return (
    <>
      <FormSectionHeader title="Leave Travel Allowance" />
      
      <Grid container spacing={3}>
        {/* Travel mode */}
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Travel Via</InputLabel>
            <Select
              value={taxationData.salary.perquisites?.travel_through || 'Public Transport'}
              label="Travel Via"
              onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'travel_through', e.target.value)}
            >
              <MenuItem value="Air">Air</MenuItem>
              <MenuItem value="Rail">Rail</MenuItem>
              <MenuItem value="Bus">Bus</MenuItem>
              <MenuItem value="Public Transport">Public Transport</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        {/* LTA amount claimed */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="LTA Amount Claimed"
            type="text"
            value={formatIndianNumber(taxationData.salary.perquisites?.lta_amount_claimed || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'lta_amount_claimed', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'lta_amount_claimed', e.target.value)}
          />
        </Grid>
                
        {/* Public transport amount for same distance */}
        <Grid item xs={12} md={6}>
          <Tooltip
            title={
              <>
                Mode:Air, Economy Class Fair.<br />
                Mode:Railways, 1st Class AC Fair.<br />
                Mode:Public Transport Fair equivalent to 1st Class Railways Fair.<br />
                Mode:Bus, 1st Class Deluxe Bus Fair.
              </>
              }
              placement="top"
              arrow
            >
          <TextField
            fullWidth
            label="Public Transport Amount for Same Distance"
            type="text"
            value={formatIndianNumber(taxationData.salary.perquisites?.public_transport_travel_amount_for_same_distance || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'public_transport_travel_amount_for_same_distance', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'public_transport_travel_amount_for_same_distance', e.target.value)}
          />
          </Tooltip>
        </Grid>
        <Box 
          sx={{ 
            width: '100%', 
            display: 'flex',
            justifyContent: 'left'
          }}
        >
        </Box>
       
        {/* LTA claim start date */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="LTA Claim Start Date"
            type="date"
            value={taxationData.salary.perquisites?.lta_claim_start_date || ''}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'lta_claim_start_date', e.target.value)}
            InputLabelProps={{ shrink: true }}
          />
        </Grid>
        
        {/* LTA claim end date */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="LTA Claim End Date"
            type="date"
            value={taxationData.salary.perquisites?.lta_claim_end_date || ''}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'lta_claim_end_date', e.target.value)}
            InputLabelProps={{ shrink: true }}
          />
        </Grid>
         {/* LTA claimed count */}
         <Grid item xs={12} md={6}>
          <Tooltip title="Max 2 claims per current block of 4 Years"
          placement="top"
          arrow
          >
          <TextField
            fullWidth
            label="Number of LTA Claims"
            type="number"
            inputProps={{ min: 0, max: 2 }}
            value={taxationData.salary.perquisites?.lta_claimed_count || 0}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'lta_claimed_count', e.target.value)}
            onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'lta_claimed_count', e.target.value)}
            sx={{ width: { xs: '100%', sm: '250px', md: '200px' } }}
          />
          </Tooltip>
        </Grid>
        
      </Grid>
    </>
  );
};

export default LeaveTravelAllowanceSection; 