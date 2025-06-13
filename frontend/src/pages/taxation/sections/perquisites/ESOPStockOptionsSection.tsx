import React from 'react';
import {
  TextField,
  Box
} from '@mui/material';
import FormSectionHeader from '../../components/FormSectionHeader';
import { formatIndianNumber } from '../../utils/taxationUtils';
// TaxationData import removed as it's not used

interface ESOPStockOptionsSectionProps {
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
 * ESOP & Stock Options Perquisites Section
 */
const ESOPStockOptionsSection: React.FC<ESOPStockOptionsSectionProps> = ({
  handleNestedInputChange,
  handleNestedFocus
}) => {
  const handleTextFieldChange = (field: string, event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>): void => {
    handleNestedInputChange('salary', 'perquisites', field, event.target.value);
  };

  const handleTextFieldFocus = (field: string, event: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement>): void => {
    handleNestedFocus('salary', 'perquisites', field, event.target.value);
  };

  return (
    <>
      <FormSectionHeader title="ESOP & Stock Options" />
      
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: 3,
          width: '100%'
        }}
      >
        {/* Number of shares */}
        <TextField
          fullWidth
          label="Number of Shares"
          type="number"
          value={0}
          onChange={(e) => handleTextFieldChange('esop_number_of_shares', e)}
          onFocus={(e) => handleTextFieldFocus('esop_number_of_shares', e)}
        />
        
        {/* Allotment price per share */}
        <TextField
          fullWidth
          label="Allotment Price per Share"
          type="text"
          value={formatIndianNumber(0)}
          onChange={(e) => handleTextFieldChange('esop_allotment_price_per_share', e)}
          InputProps={{ startAdornment: '₹' }}
          onFocus={(e) => handleTextFieldFocus('esop_allotment_price_per_share', e)}
        />
        
        {/* Exercise price per share */}
        <TextField
          fullWidth
          label="Exercise Price per Share"
          type="text"
          value={formatIndianNumber(0)}
          onChange={(e) => handleTextFieldChange('esop_exercise_price_per_share', e)}
          InputProps={{ startAdornment: '₹' }}
          onFocus={(e) => handleTextFieldFocus('esop_exercise_price_per_share', e)}
        />
      </Box>
    </>
  );
};

export default ESOPStockOptionsSection; 