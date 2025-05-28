import React from 'react';
import {
  TextField,
  Tooltip,
  Box
} from '@mui/material';
import FormSectionHeader from '../../components/FormSectionHeader';
import { formatIndianNumber } from '../../utils/taxationUtils';
import { TaxationData } from '../../../../types';

interface ESOPStockOptionsSectionProps {
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
 * ESOP & Stock Options Perquisites Section
 */
const ESOPStockOptionsSection: React.FC<ESOPStockOptionsSectionProps> = ({
  taxationData,
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
        {/* Number of Options */}
        <Tooltip 
          title="ESOPs and Stocks Exercised within current financial year."
          placement="top"
          arrow
        >
          <TextField
            fullWidth
            label="Number of Shares Exercised"
            type="number"
            value={taxationData.salary.perquisites?.number_of_esop_shares_exercised || 0}
            onChange={(e) => handleTextFieldChange('number_of_esop_shares_exercised', e)}
            onFocus={(e) => handleTextFieldFocus('number_of_esop_shares_exercised', e)}
          />
        </Tooltip>
        
        {/* Allotment Price */}
        <TextField
          fullWidth
          label="Allotment Price (per share)"
          type="text"
          value={formatIndianNumber(taxationData.salary.perquisites?.esop_allotment_price_per_share || 0)}
          onChange={(e) => handleTextFieldChange('esop_allotment_price_per_share', e)}
          InputProps={{ startAdornment: '₹' }}
          onFocus={(e) => handleTextFieldFocus('esop_allotment_price_per_share', e)}
        />
        
        {/* Exercise Price */}
        <TextField
          fullWidth
          label="Exercise Price (per share)"
          type="text"
          value={formatIndianNumber(taxationData.salary.perquisites?.esop_exercise_price_per_share || 0)}
          onChange={(e) => handleTextFieldChange('esop_exercise_price_per_share', e)}
          InputProps={{ startAdornment: '₹' }}
          onFocus={(e) => handleTextFieldFocus('esop_exercise_price_per_share', e)}
        />
      </Box>
    </>
  );
};

export default ESOPStockOptionsSection; 