import React from 'react';
import {
  TextField,
  FormControlLabel,
  Box,
  Divider,
  Tooltip,
  Typography,
  Checkbox
} from '@mui/material';
import FormSectionHeader from '../../components/FormSectionHeader';
import { formatIndianNumber } from '../../utils/taxationUtils';
import { TaxationData } from '../../../../types';

interface FreeEducationSectionProps {
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
 * Free Education Perquisites Section
 */
const FreeEducationSection: React.FC<FreeEducationSectionProps> = ({
  taxationData,
  handleNestedInputChange,
  handleNestedFocus
}) => {
  const handleCheckboxChange = (field: string, event: React.ChangeEvent<HTMLInputElement>): void => {
    handleNestedInputChange('salary', 'perquisites', field, event.target.checked);
  };

  const handleTextFieldChange = (field: string, event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>): void => {
    handleNestedInputChange('salary', 'perquisites', field, event.target.value);
  };

  const handleTextFieldFocus = (field: string, event: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement>): void => {
    handleNestedFocus('salary', 'perquisites', field, event.target.value);
  };

  return (
    <>
      <FormSectionHeader title="Free Education" />
      
      {/* First Child Section */}
      <Box 
        sx={{ 
          width: '100%', 
          display: 'flex',
          justifyContent: 'left',
          mb: 2
        }}
      >
        <Typography variant="h6" color="primary">First Child</Typography>
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
        {/* First Child Education in Employer Institution */}
        <FormControlLabel
          control={
            <Checkbox
              checked={taxationData.salary.perquisites?.employer_maintained_1st_child || false}
              onChange={(e) => handleCheckboxChange('employer_maintained_1st_child', e)}
            />
          }
          label="Education in Employer Maintained Institution"
        />
        
        {/* First Child Monthly Count */}
        <TextField
          fullWidth
          label="Monthly Count"
          type="number"
          inputProps={{ min: 0, max: 12 }}
          value={taxationData.salary.perquisites?.monthly_count_1st_child || 0}
          onChange={(e) => handleTextFieldChange('monthly_count_1st_child', e)}
          onFocus={(e) => handleTextFieldFocus('monthly_count_1st_child', e)}
        />
        
        {/* First Child Monthly Expenses */}
        <Tooltip 
          title="Value/Expenses met by Employer(Monthly)"
          placement="top"
          arrow
        >
          <TextField
            fullWidth
            label="Value/Expenses met by Employer(Monthly)"
            type="text"
            value={formatIndianNumber(taxationData.salary.perquisites?.employer_monthly_expenses_1st_child || 0)}
            onChange={(e) => handleTextFieldChange('employer_monthly_expenses_1st_child', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('employer_monthly_expenses_1st_child', e)}
          />
        </Tooltip>
      </Box>
      
      {/* Second Child Section */}
      <Box 
        sx={{ 
          width: '100%', 
          display: 'flex',
          justifyContent: 'left',
          mb: 2
        }}
      >
        <Typography variant="h6" color="primary">Second Child</Typography>
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
        {/* Second Child Education in Employer Institution */}
        <FormControlLabel
          control={
            <Checkbox
              checked={taxationData.salary.perquisites?.employer_maintained_2nd_child || false}
              onChange={(e) => handleCheckboxChange('employer_maintained_2nd_child', e)}
            />
          }
          label="Education in Employer Maintained Institution"
        />
        
        {/* Second Child Monthly Count */}
        <TextField
          fullWidth
          label="Monthly Count"
          type="number"
          inputProps={{ min: 0, max: 12 }}
          value={taxationData.salary.perquisites?.monthly_count_2nd_child || 0}
          onChange={(e) => handleTextFieldChange('monthly_count_2nd_child', e)}
          onFocus={(e) => handleTextFieldFocus('monthly_count_2nd_child', e)}
        />
        
        {/* Second Child Monthly Expenses */}
        <Tooltip 
          title="Value/Expenses met by Employer(Monthly)"
          placement="top"
          arrow
        >
          <TextField
            fullWidth
            label="Value/Expenses met by Employer(Monthly)"
            type="text"
            value={formatIndianNumber(taxationData.salary.perquisites?.employer_monthly_expenses_2nd_child || 0)}
            onChange={(e) => handleTextFieldChange('employer_monthly_expenses_2nd_child', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('employer_monthly_expenses_2nd_child', e)}
          />
        </Tooltip>
      </Box>
    </>
  );
};

export default FreeEducationSection; 