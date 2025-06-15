import React from 'react';
import {
  Tooltip,
  TextField,
  Box,
  Typography,
  Divider
} from '@mui/material';
import FormSectionHeader from '../../components/FormSectionHeader';
import { formatIndianNumber } from '../../utils/taxationUtils';
import { TaxationData } from '../../../../shared/types';

interface OtherPerquisitesSectionProps {
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
 * Other Perquisites Section
 */
const OtherPerquisitesSection: React.FC<OtherPerquisitesSectionProps> = ({
  taxationData,
  handleNestedInputChange,
  handleNestedFocus
}) => {
  const handleTextFieldChange = (field: string, event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>): void => {
    handleNestedInputChange('perquisites', 'other_perquisites', field, event.target.value);
  };

  const handleTextFieldFocus = (field: string, event: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement>): void => {
    handleNestedFocus('perquisites', 'other_perquisites', field, event.target.value);
  };

  return (
    <>
      <FormSectionHeader title="Other Perquisites" />
      
      {/* Domestic Help Section */}
      <Box 
        sx={{ 
          width: '100%', 
          display: 'flex',
          justifyContent: 'left',
          mb: 2
        }}
      >
        <Typography variant="h6" color="primary">Domestic Help</Typography>
      </Box>
      <Divider sx={{ my: 0, width: '100%', mb: 3 }} />
      
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: 3,
          width: '100%',
          mb: 4
        }}
      >
        <Tooltip 
          title="Amount paid by employer"
          placement="top"
          arrow
        >
          <TextField
            fullWidth
            label="Domestic Help Amount Paid by Employer"
            type="text"
            value={formatIndianNumber(taxationData.perquisites?.other_perquisites?.domestic_help_amount_paid_by_employer || 0)}
            onChange={(e) => handleTextFieldChange('domestic_help_amount_paid_by_employer', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('domestic_help_amount_paid_by_employer', e)}
          />
        </Tooltip>
        
        <Tooltip 
          title="Amount recovered from employee"
          placement="top"
          arrow
        >
          <TextField
            fullWidth
            label="Domestic Help Amount Paid by Employee"
            type="text"
            value={formatIndianNumber(taxationData.perquisites?.other_perquisites?.domestic_help_amount_paid_by_employee || 0)}
            onChange={(e) => handleTextFieldChange('domestic_help_amount_paid_by_employee', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('domestic_help_amount_paid_by_employee', e)}
          />
        </Tooltip>
      </Box>
      
      {/* Lunch/Refreshment Section */}
      <Box 
        sx={{ 
          width: '100%', 
          display: 'flex',
          justifyContent: 'left',
          mb: 2
        }}
      >
        <Typography variant="h6" color="primary">Lunch/Refreshment</Typography>
      </Box>
      <Divider sx={{ my: 0, width: '100%', mb: 3 }} />
      
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: 3,
          width: '100%',
          mb: 4
        }}
      >
        <Tooltip 
          title="Amount paid by employer"
          placement="top"
          arrow
        >
          <TextField
            fullWidth
            label="Amount Paid by Employer"
            type="text"
            value={formatIndianNumber(taxationData.perquisites?.other_perquisites?.lunch_amount_paid_by_employer || 0)}
            onChange={(e) => handleTextFieldChange('lunch_amount_paid_by_employer', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('lunch_amount_paid_by_employer', e)}
          />
        </Tooltip>
        
        <Tooltip 
          title="Amount recovered from employee"
          placement="top"
          arrow
        >
          <TextField
            fullWidth
            label="Amount recovered from employee"
            type="text"
            value={formatIndianNumber(taxationData.perquisites?.other_perquisites?.lunch_amount_paid_by_employee || 0)}
            onChange={(e) => handleTextFieldChange('lunch_amount_paid_by_employee', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('lunch_amount_paid_by_employee', e)}
          />
        </Tooltip>
      </Box>
      
      {/* Monetary Benefits Section */}
      <Box 
        sx={{ 
          width: '100%', 
          display: 'flex',
          justifyContent: 'left',
          mb: 2
        }}
      >
        <Typography variant="h6" color="primary">Monetary Benefits</Typography>
      </Box>
      <Divider sx={{ my: 0, width: '100%', mb: 3 }} />
      
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: 3,
          width: '100%',
          mb: 4
        }}
      >
        <Tooltip 
          title="Amount paid by employer for monetary benefits"
          placement="top"
          arrow
        >
          <TextField
            fullWidth
            label="Amount Paid by Employer"
            type="text"
            value={formatIndianNumber(taxationData.perquisites?.other_perquisites?.monetary_amount_paid_by_employer || 0)}
            onChange={(e) => handleTextFieldChange('monetary_amount_paid_by_employer', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('monetary_amount_paid_by_employer', e)}
          />
        </Tooltip>
        
        <Tooltip 
          title="Official purpose Usage"
          placement="top"
          arrow
        >
          <TextField
            fullWidth
            label="Official Purpose Usage"
            type="text"
            value={formatIndianNumber(taxationData.perquisites?.other_perquisites?.expenditure_for_offical_purpose || 0)}
            onChange={(e) => handleTextFieldChange('expenditure_for_offical_purpose', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('expenditure_for_offical_purpose', e)}
          />
        </Tooltip>
        
        <Tooltip 
          title="Amount recovered by employee"
          placement="top"
          arrow
        >
          <TextField
            fullWidth
            label="Amount recovered by employee"
            type="text"
            value={formatIndianNumber(taxationData.perquisites?.other_perquisites?.monetary_benefits_amount_paid_by_employee || 0)}
            onChange={(e) => handleTextFieldChange('monetary_benefits_amount_paid_by_employee', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('monetary_benefits_amount_paid_by_employee', e)}
          />
        </Tooltip>
      </Box>
      
      {/* Gift Vouchers Section */}
      <Box 
        sx={{ 
          width: '100%', 
          display: 'flex',
          justifyContent: 'left',
          mb: 2
        }}
      >
        <Typography variant="h6" color="primary">Gift Vouchers</Typography>
      </Box>
      <Divider sx={{ my: 0, width: '100%', mb: 3 }} />
      
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: 3,
          width: '100%',
          mb: 4
        }}
      >
        <Tooltip 
          title="Amount paid by employer"
          placement="top"
          arrow
        >
          <TextField
            fullWidth
            label="Amount Paid by Employer"
            type="text"
            value={formatIndianNumber(taxationData.perquisites?.other_perquisites?.gift_vouchers_amount_paid_by_employer || 0)}
            onChange={(e) => handleTextFieldChange('gift_vouchers_amount_paid_by_employer', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('gift_vouchers_amount_paid_by_employer', e)}
          />
        </Tooltip>
      </Box>
      
      {/* Club Expenses Section */}
      <Box 
        sx={{ 
          width: '100%', 
          display: 'flex',
          justifyContent: 'left',
          mb: 2
        }}
      >
        <Typography variant="h6" color="primary">Club Expenses</Typography>
      </Box>
      <Divider sx={{ my: 0, width: '100%', mb: 3 }} />
      
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: 3,
          width: '100%',
          mb: 4
        }}
      >
        <Tooltip 
          title="Amount paid by employer"
          placement="top"
          arrow
        >
          <TextField
            fullWidth
            label="Amount Paid by Employer"
            type="text"
            value={formatIndianNumber(taxationData.perquisites?.other_perquisites?.club_expenses_amount_paid_by_employer || 0)}
            onChange={(e) => handleTextFieldChange('club_expenses_amount_paid_by_employer', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('club_expenses_amount_paid_by_employer', e)}
          />
        </Tooltip>
        
        <Tooltip 
          title="Amount recovered from employee"
          placement="top"
          arrow
        >
          <TextField
            fullWidth
            label="Amount recovered from employee"
            type="text"
            value={formatIndianNumber(taxationData.perquisites?.other_perquisites?.club_expenses_amount_paid_by_employee || 0)}
            onChange={(e) => handleTextFieldChange('club_expenses_amount_paid_by_employee', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('club_expenses_amount_paid_by_employee', e)}
          />
        </Tooltip>
        
        <Tooltip 
          title="Official purpose usage"
          placement="top"
          arrow
        >
          <TextField
            fullWidth
            label="Official purpose usage"
            type="text"
            value={formatIndianNumber(taxationData.perquisites?.other_perquisites?.club_expenses_amount_paid_for_offical_purpose || 0)}
            onChange={(e) => handleTextFieldChange('club_expenses_amount_paid_for_offical_purpose', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('club_expenses_amount_paid_for_offical_purpose', e)}
          />
        </Tooltip>
      </Box>
    </>
  );
};

export default OtherPerquisitesSection; 