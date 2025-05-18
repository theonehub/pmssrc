import React from 'react';
import {
  Grid,
  Tooltip,
  TextField,
  Box,
  Typography,
  Divider
} from '@mui/material';
import FormSectionHeader from '../../components/FormSectionHeader';
import { formatIndianNumber } from '../../utils/taxationUtils';

/**
 * Other Perquisites Section
 * @param {Object} props - Component props
 * @param {Object} props.taxationData - Taxation data state
 * @param {Function} props.handleNestedInputChange - Function to handle nested input change
 * @param {Function} props.handleNestedFocus - Function to handle nested focus
 * @returns {JSX.Element} Other Perquisites section component
 */
const OtherPerquisitesSection = ({
  taxationData,
  handleNestedInputChange,
  handleNestedFocus
}) => {
  return (
    <>
      <FormSectionHeader title="Other Perquisites" />
      
      <Grid container spacing={3}>
      <Box 
          sx={{ 
            width: '100%', 
            display: 'flex',
            justifyContent: 'left'
          }}
        >
          <Typography variant="h6" color="primary">Domestic Help</Typography>
        </Box>
        <Divider sx={{ my: 0, width: '100%' }} />
        
        {/* Domestic Help */}
        <Grid item xs={12} md={6}>
          <Tooltip title="Amount paid by employer">
            <TextField
              fullWidth
              label="Domestic Help Amount Paid by Employer"
              type="text"
              value={formatIndianNumber(taxationData.salary.perquisites?.domestic_help_amount_paid_by_employer || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'domestic_help_amount_paid_by_employer', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'domestic_help_amount_paid_by_employer', e.target.value)}
            />
          </Tooltip>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Tooltip title="Amount recovered from employee">
            <TextField
              fullWidth
              label="Domestic Help Amount Paid by Employee"
              type="text"
              value={formatIndianNumber(taxationData.salary.perquisites?.domestic_help_amount_paid_by_employee || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'domestic_help_amount_paid_by_employee', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'domestic_help_amount_paid_by_employee', e.target.value)}
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
          <Typography variant="h6" color="primary">Lunch/Refreshment</Typography>
        </Box>
        <Divider sx={{ my: 0, width: '100%' }} />
        
        {/* Lunch/Refreshment */}
        <Grid item xs={12} md={6}>
          <Tooltip title="Amount paid by employer">
            <TextField
              fullWidth
              label="Amount Paid by Employer"
              type="text"
              value={formatIndianNumber(taxationData.salary.perquisites?.lunch_amount_paid_by_employer || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'lunch_amount_paid_by_employer', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'lunch_amount_paid_by_employer', e.target.value)}
            />
          </Tooltip>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Tooltip title="Amount recovered from employee">
            <TextField
              fullWidth
              label="Amount recovered from employee"
              type="text"
              value={formatIndianNumber(taxationData.salary.perquisites?.lunch_amount_paid_by_employee || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'lunch_amount_paid_by_employee', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'lunch_amount_paid_by_employee', e.target.value)}
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
          <Typography variant="h6" color="primary">Monetary Benefits</Typography>
        </Box>
        <Divider sx={{ my: 0, width: '100%' }} />
        
        {/* Monetary Benefits */}
        <Grid item xs={12} md={6}>
          <Tooltip title="Amount paid by employer for monetary benefits">
            <TextField
              fullWidth
              label="Amount Paid by Employer"
              type="text"
              value={formatIndianNumber(taxationData.salary.perquisites?.monetary_amount_paid_by_employer || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'monetary_amount_paid_by_employer', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'monetary_amount_paid_by_employer', e.target.value)}
            />
          </Tooltip>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Tooltip title="Official purpose Usage">
            <TextField
              fullWidth
              label="Official Purpose Usage"
              type="text"
              value={formatIndianNumber(taxationData.salary.perquisites?.expenditure_for_offical_purpose || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'expenditure_for_offical_purpose', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'expenditure_for_offical_purpose', e.target.value)}
            />
          </Tooltip>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Tooltip title="Amount recovered by employee">
            <TextField
              fullWidth
              label="Amount recovered by employee"
              type="text"
              value={formatIndianNumber(taxationData.salary.perquisites?.monetary_benefits_amount_paid_by_employee || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'monetary_benefits_amount_paid_by_employee', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'monetary_benefits_amount_paid_by_employee', e.target.value)}
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
          <Typography variant="h6" color="primary">Gift Vouchers</Typography>
        </Box>
        <Divider sx={{ my: 0, width: '100%' }} />
        
        <Grid item xs={12} md={6}>
          <Tooltip title="Amount paid by employer">
            <TextField
              fullWidth
              label="Amount Paid by Employer"
              type="text"
              value={formatIndianNumber(taxationData.salary.perquisites?.gift_vouchers_amount_paid_by_employer || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'gift_vouchers_amount_paid_by_employer', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'gift_vouchers_amount_paid_by_employer', e.target.value)}
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
          <Typography variant="h6" color="primary">Club Expenses</Typography>
        </Box>
        <Divider sx={{ my: 0, width: '100%' }} />
        
        {/* Club Expenses */}
        <Grid item xs={12} md={6}>
          <Tooltip title="Amount paid by employer">
            <TextField
              fullWidth
              label="Amount Paid by Employer"
              type="text"
              value={formatIndianNumber(taxationData.salary.perquisites?.club_expenses_amount_paid_by_employer || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'club_expenses_amount_paid_by_employer', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'club_expenses_amount_paid_by_employer', e.target.value)}
            />
          </Tooltip>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Tooltip title="Amount recovered from employee">
            <TextField
              fullWidth
              label="Amount recovered from employee"
              type="text"
              value={formatIndianNumber(taxationData.salary.perquisites?.club_expenses_amount_paid_by_employee || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'club_expenses_amount_paid_by_employee', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'club_expenses_amount_paid_by_employee', e.target.value)}
            />
          </Tooltip>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Tooltip title="Official purpose usage">
            <TextField
              fullWidth
              label="Official purpose usage"
              type="text"
              value={formatIndianNumber(taxationData.salary.perquisites?.club_expenses_amount_paid_for_offical_purpose || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'club_expenses_amount_paid_for_offical_purpose', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'club_expenses_amount_paid_for_offical_purpose', e.target.value)}
            />
          </Tooltip>
        </Grid>
      </Grid>
    </>
  );
};

export default OtherPerquisitesSection; 