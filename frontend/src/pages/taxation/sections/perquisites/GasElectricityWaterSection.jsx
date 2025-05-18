import React from 'react';
import {
  Grid,
  TextField,
  FormControlLabel,
  Checkbox
} from '@mui/material';
import FormSectionHeader from '../../components/FormSectionHeader';
import { formatIndianNumber } from '../../utils/taxationUtils';

/**
 * Gas, Electricity, Water Section for Perquisites
 * @param {Object} props - Component props
 * @param {Object} props.taxationData - Taxation data state
 * @param {Function} props.handleNestedInputChange - Function to handle nested input change
 * @param {Function} props.handleNestedFocus - Function to handle nested focus
 * @returns {JSX.Element} Gas, Electricity, Water section component
 */
const GasElectricityWaterSection = ({
  taxationData,
  handleNestedInputChange,
  handleNestedFocus
}) => {
  return (
    <>
      <FormSectionHeader title="Gas, Electricity, Water" />
      
      <Grid container spacing={3}>
        {/* Gas Section */}
        <Grid item xs={12} md={6}>
          <FormControlLabel
            control={
              <Checkbox
                checked={taxationData.salary.perquisites?.is_gas_manufactured_by_employer || false}
                onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'is_gas_manufactured_by_employer', e.target.checked)}
              />
            }
            label="Gas Manufactured by Employer"
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label={taxationData.salary.perquisites?.is_gas_manufactured_by_employer ? "Gas Manufacturing Cost to Employer" : "Gas Amount Paid by Employee"}
            type="text"
            value={formatIndianNumber(taxationData.salary.perquisites?.gas_amount_paid_by_employer || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'gas_amount_paid_by_employer', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'gas_amount_paid_by_employer', e.target.value)}
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Gas Amount Paid by Employee"
            type="text"
            value={formatIndianNumber(taxationData.salary.perquisites?.gas_amount_paid_by_employee || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'gas_amount_paid_by_employee', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'gas_amount_paid_by_employee', e.target.value)}
          />
        </Grid>
        
        {/* Electricity Section */}
        <Grid item xs={12} md={6}>
          <FormControlLabel
            control={
              <Checkbox
                checked={taxationData.salary.perquisites?.is_electricity_manufactured_by_employer || false}
                onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'is_electricity_manufactured_by_employer', e.target.checked)}
              />
            }
            label="Electricity Manufactured by Employer"
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label={taxationData.salary.perquisites?.is_electricity_manufactured_by_employer ? "Electricity Manufacturing Cost to Employer" : "Electricity Amount Paid by Employee"}
            type="text"
            value={formatIndianNumber(taxationData.salary.perquisites?.electricity_amount_paid_by_employer || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'electricity_amount_paid_by_employer', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'electricity_amount_paid_by_employer', e.target.value)}
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Electricity Amount Paid by Employee"
            type="text"
            value={formatIndianNumber(taxationData.salary.perquisites?.electricity_amount_paid_by_employee || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'electricity_amount_paid_by_employee', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'electricity_amount_paid_by_employee', e.target.value)}
          />
        </Grid>
        
        {/* Water Section */}
        <Grid item xs={12} md={6}>
          <FormControlLabel
            control={
              <Checkbox
                checked={taxationData.salary.perquisites?.is_water_manufactured_by_employer || false}
                onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'is_water_manufactured_by_employer', e.target.checked)}
              />
            }
            label="Water Manufactured by Employer"
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label={taxationData.salary.perquisites?.is_water_manufactured_by_employer ? "Water Manufacturing Cost to Employer" : "Water Amount Paid by Employee"}
            type="text"
            value={formatIndianNumber(taxationData.salary.perquisites?.water_amount_paid_by_employer || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'water_amount_paid_by_employer', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'water_amount_paid_by_employer', e.target.value)}
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Water Amount Paid by Employee"
            type="text"
            value={formatIndianNumber(taxationData.salary.perquisites?.water_amount_paid_by_employee || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'water_amount_paid_by_employee', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'water_amount_paid_by_employee', e.target.value)}
          />
        </Grid>
      </Grid>
    </>
  );
};

export default GasElectricityWaterSection; 