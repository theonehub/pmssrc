import React from 'react';
import {
  TextField,
  FormControlLabel,
  Checkbox,
  Tooltip,
  Box
} from '@mui/material';
import FormSectionHeader from '../../components/FormSectionHeader';
import { formatIndianNumber } from '../../utils/taxationUtils';
import { TaxationData } from '../../../../types';

interface MedicalReimbursementSectionProps {
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
 * Medical Reimbursement Perquisites Section
 */
const MedicalReimbursementSection: React.FC<MedicalReimbursementSectionProps> = ({
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
      <FormSectionHeader title="Medical Reimbursement" />
      
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: 3,
          width: '100%'
        }}
      >
        {/* Treatment in India */}
        <FormControlLabel
          control={
            <Checkbox
              checked={taxationData.salary.perquisites?.is_treated_in_India || false}
              onChange={(e) => handleCheckboxChange('is_treated_in_India', e)}
            />
          }
          label="Treatment in India"
        />
        
        {/* Medical reimbursement by employer */}
        <Tooltip 
          title="Medical Reimbursement by Employer"
          placement="top"
          arrow
        >
          <TextField
            fullWidth
            label="Medical Reimbursement by Employer"
            type="text"
            value={formatIndianNumber(taxationData.salary.perquisites?.medical_reimbursement_by_employer || 0)}
            onChange={(e) => handleTextFieldChange('medical_reimbursement_by_employer', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('medical_reimbursement_by_employer', e)}
          />
        </Tooltip>
        
        {/* Traveling allowance for treatment */}
        <Tooltip 
          title="Traveling Allowance for Treatment"
          placement="top"
          arrow
        >
          <TextField
            fullWidth
            label="Traveling Allowance for Treatment"
            type="text"
            value={formatIndianNumber(taxationData.salary.perquisites?.travelling_allowance_for_treatment || 0)}
            onChange={(e) => handleTextFieldChange('travelling_allowance_for_treatment', e)}
            InputProps={{ startAdornment: '₹' }}
            disabled={taxationData.salary.perquisites?.is_treated_in_India}
            onFocus={(e) => handleTextFieldFocus('travelling_allowance_for_treatment', e)}
          />
        </Tooltip>
        
        {/* RBI limit for illness */}
        <Tooltip 
          title="RBI Limit for Illness"
          placement="top"
          arrow
        >
          <TextField
            fullWidth
            label="RBI Limit for Illness"
            type="text"
            value={formatIndianNumber(taxationData.salary.perquisites?.rbi_limit_for_illness || 0)}
            onChange={(e) => handleTextFieldChange('rbi_limit_for_illness', e)}
            InputProps={{ startAdornment: '₹' }}
            disabled={taxationData.salary.perquisites?.is_treated_in_India}
            onFocus={(e) => handleTextFieldFocus('rbi_limit_for_illness', e)}
          />
        </Tooltip>
      </Box>
    </>
  );
};

export default MedicalReimbursementSection; 