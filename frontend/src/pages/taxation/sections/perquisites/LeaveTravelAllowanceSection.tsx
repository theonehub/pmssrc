import React from 'react';
import {
  Box,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tooltip,
  SelectChangeEvent
} from '@mui/material';
import FormSectionHeader from '../../components/FormSectionHeader';
import { formatIndianNumber } from '../../utils/taxationUtils';
// TaxationData import removed as it's not used

interface LeaveTravelAllowanceSectionProps {
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
 * Leave Travel Allowance Perquisites Section
 */
const LeaveTravelAllowanceSection: React.FC<LeaveTravelAllowanceSectionProps> = ({
  handleNestedInputChange,
  handleNestedFocus
}) => {
  const handleSelectChange = (field: string, event: SelectChangeEvent<string>): void => {
    handleNestedInputChange('salary', 'perquisites', field, event.target.value);
  };

  const handleTextFieldChange = (field: string, event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>): void => {
    handleNestedInputChange('salary', 'perquisites', field, event.target.value);
  };

  const handleTextFieldFocus = (field: string, event: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement>): void => {
    handleNestedFocus('salary', 'perquisites', field, event.target.value);
  };

  return (
    <>
      <FormSectionHeader title="Leave Travel Allowance" />
      
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: 3,
          width: '100%'
        }}
      >
        {/* Travel mode */}
        <FormControl fullWidth>
          <InputLabel>Travel Via</InputLabel>
          <Select
            value={'Public Transport'}
            label="Travel Via"
            onChange={(e) => handleSelectChange('travel_through', e)}
          >
            <MenuItem value="Air">Air</MenuItem>
            <MenuItem value="Rail">Rail</MenuItem>
            <MenuItem value="Bus">Bus</MenuItem>
            <MenuItem value="Public Transport">Public Transport</MenuItem>
          </Select>
        </FormControl>

        {/* LTA amount claimed */}
        <TextField
          fullWidth
          label="LTA Amount Claimed"
          type="text"
          value={formatIndianNumber(0)}
          onChange={(e) => handleTextFieldChange('lta_amount_claimed', e)}
          InputProps={{ startAdornment: '₹' }}
          onFocus={(e) => handleTextFieldFocus('lta_amount_claimed', e)}
        />
                
        {/* Public transport amount for same distance */}
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
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('public_transport_travel_amount_for_same_distance', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('public_transport_travel_amount_for_same_distance', e)}
          />
        </Tooltip>
       
        {/* LTA claim start date */}
        <TextField
          fullWidth
          label="LTA Claim Start Date"
          type="date"
          value={''}
          onChange={(e) => handleTextFieldChange('lta_claim_start_date', e)}
          InputLabelProps={{ shrink: true }}
        />
        
        {/* LTA claim end date */}
        <TextField
          fullWidth
          label="LTA Claim End Date"
          type="date"
          value={''}
          onChange={(e) => handleTextFieldChange('lta_claim_end_date', e)}
          InputLabelProps={{ shrink: true }}
        />
        
        {/* LTA claimed count */}
        <Tooltip 
          title="Max 2 claims per current block of 4 Years"
          placement="top"
          arrow
        >
          <TextField
            fullWidth
            label="Number of LTA Claims"
            type="number"
            inputProps={{ min: 0, max: 2 }}
            value={0}
            onChange={(e) => handleTextFieldChange('lta_claimed_count', e)}
            onFocus={(e) => handleTextFieldFocus('lta_claimed_count', e)}
          />
        </Tooltip>
      </Box>
    </>
  );
};

export default LeaveTravelAllowanceSection; 