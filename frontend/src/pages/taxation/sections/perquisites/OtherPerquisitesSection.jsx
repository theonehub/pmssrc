import React from 'react';
import {
  Grid,
  Tooltip,
  TextField
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
        {/* Domestic Help */}
        <Grid item xs={12} md={6}>
          <Tooltip title="Amount paid by employer for domestic help">
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
          <Tooltip title="Amount paid by employee for domestic help">
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
        
        {/* Lunch/Refreshment */}
        <Grid item xs={12} md={6}>
          <Tooltip title="Amount paid by employer for lunch">
            <TextField
              fullWidth
              label="Lunch Amount Paid by Employer"
              type="text"
              value={formatIndianNumber(taxationData.salary.perquisites?.lunch_amount_paid_by_employer || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'lunch_amount_paid_by_employer', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'lunch_amount_paid_by_employer', e.target.value)}
            />
          </Tooltip>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Tooltip title="Amount paid by employee for lunch">
            <TextField
              fullWidth
              label="Lunch Amount Paid by Employee"
              type="text"
              value={formatIndianNumber(taxationData.salary.perquisites?.lunch_amount_paid_by_employee || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'lunch_amount_paid_by_employee', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'lunch_amount_paid_by_employee', e.target.value)}
            />
          </Tooltip>
        </Grid>
        
        {/* Monetary Benefits */}
        <Grid item xs={12} md={6}>
          <Tooltip title="Amount paid by employer for monetary benefits">
            <TextField
              fullWidth
              label="Monetary Amount Paid by Employer"
              type="text"
              value={formatIndianNumber(taxationData.salary.perquisites?.monetary_amount_paid_by_employer || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'monetary_amount_paid_by_employer', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'monetary_amount_paid_by_employer', e.target.value)}
            />
          </Tooltip>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Tooltip title="Expenditure for official purpose">
            <TextField
              fullWidth
              label="Expenditure for Official Purpose"
              type="text"
              value={formatIndianNumber(taxationData.salary.perquisites?.expenditure_for_offical_purpose || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'expenditure_for_offical_purpose', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'expenditure_for_offical_purpose', e.target.value)}
            />
          </Tooltip>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Tooltip title="Monetary benefits amount paid by employee">
            <TextField
              fullWidth
              label="Monetary Benefits Amount Paid by Employee"
              type="text"
              value={formatIndianNumber(taxationData.salary.perquisites?.monetary_benefits_amount_paid_by_employee || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'monetary_benefits_amount_paid_by_employee', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'monetary_benefits_amount_paid_by_employee', e.target.value)}
            />
          </Tooltip>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Tooltip title="Gift vouchers amount paid by employer">
            <TextField
              fullWidth
              label="Gift Vouchers Amount Paid by Employer"
              type="text"
              value={formatIndianNumber(taxationData.salary.perquisites?.gift_vouchers_amount_paid_by_employer || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'gift_vouchers_amount_paid_by_employer', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'gift_vouchers_amount_paid_by_employer', e.target.value)}
            />
          </Tooltip>
        </Grid>
        
        {/* Club Expenses */}
        <Grid item xs={12} md={6}>
          <Tooltip title="Club expenses amount paid by employer">
            <TextField
              fullWidth
              label="Club Expenses Amount Paid by Employer"
              type="text"
              value={formatIndianNumber(taxationData.salary.perquisites?.club_expenses_amount_paid_by_employer || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'club_expenses_amount_paid_by_employer', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'club_expenses_amount_paid_by_employer', e.target.value)}
            />
          </Tooltip>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Tooltip title="Club expenses amount paid by employee">
            <TextField
              fullWidth
              label="Club Expenses Amount Paid by Employee"
              type="text"
              value={formatIndianNumber(taxationData.salary.perquisites?.club_expenses_amount_paid_by_employee || 0)}
            onChange={(e) => handleNestedInputChange('salary', 'perquisites', 'club_expenses_amount_paid_by_employee', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleNestedFocus('salary', 'perquisites', 'club_expenses_amount_paid_by_employee', e.target.value)}
            />
          </Tooltip>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Tooltip title="Club expenses amount paid for official purpose">
            <TextField
              fullWidth
              label="Club Expenses Amount Paid for Official Purpose"
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