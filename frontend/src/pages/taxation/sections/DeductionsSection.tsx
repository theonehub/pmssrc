import React from 'react';
import {
  Box,
  Typography,
  TextField,
  Paper,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Tooltip,
  SelectChangeEvent
} from '@mui/material';
import { formatIndianNumber } from '../utils/taxationUtils';
import FormSectionHeader from '../components/FormSectionHeader';
import {
  disabilityPercentageOptions,
  relationOptions
} from '../utils/taxationConstants';
import { TaxationData } from '../../../shared/types';

interface DeductionsSectionProps {
  taxationData: TaxationData;
  handleInputChange: (section: string, field: string, value: string | number | boolean) => void;
  handleFocus: (section: string, field: string, value: string | number) => void;
}

/**
 * Deductions Section Component for tax declaration
 */
const DeductionsSection: React.FC<DeductionsSectionProps> = ({
  taxationData,
  handleInputChange,
  handleFocus
}) => {
  // Only show alert for new regime (deductions not available)
  const showDeductionsAlert = taxationData.regime === 'new';
  
  // Type-safe event handlers
  const handleTextFieldChange = (field: string, event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>): void => {
    handleInputChange('deductions', field, event.target.value);
  };

  const handleSelectChange = (field: string, event: SelectChangeEvent<string>): void => {
    handleInputChange('deductions', field, event.target.value);
  };

  const handleTextFieldFocus = (field: string, event: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement>): void => {
    const numericValue = parseFloat(event.target.value.replace(/,/g, '')) || 0;
    handleFocus('deductions', field, numericValue);
  };
  
  return (
    <Box sx={{ py: 2 }}>
      <Typography variant="h6" gutterBottom>
        Deductions
      </Typography>
      
      {showDeductionsAlert && (
        <Alert severity="info" sx={{ mb: 3 }}>
          Most deductions are not available under the new tax regime. However, you can still fill this section if you want to compare tax liability between old and new regimes.
        </Alert>
      )}
      
      <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
        <FormSectionHeader title="Section 80C (Max ₹1,50,000)" withDivider={false} />
        
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: 3,
            width: '100%'
          }}
        >
          {/* LIC Premium */}
          <TextField
            fullWidth
            label="LIC Premium"
            type="text"
            value={formatIndianNumber(taxationData.section_80c || 0)}
            onChange={(e) => handleTextFieldChange('section_80c', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('section_80c', e)}
          />
          
          {/* EPF */}
          <TextField
            fullWidth
            label="EPF Contribution"
            type="text"
            value={formatIndianNumber(taxationData.pf_employee || 0)}
            onChange={(e) => handleTextFieldChange('pf_employee', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('pf_employee', e)}
          />
          
          {/* PPF */}
          <TextField
            fullWidth
            label="PPF"
            type="text"
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('section_80c_ssp', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('section_80c_ssp', e)}
          />
          
          {/* NSC */}
          <TextField
            fullWidth
            label="NSC"
            type="text"
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('section_80c_nsc', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('section_80c_nsc', e)}
          />
          
          {/* ULIP */}
          <TextField
            fullWidth
            label="ULIP"
            type="text"
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('section_80c_ulip', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('section_80c_ulip', e)}
          />
          
          {/* Tax Saving Mutual Funds */}
          <TextField
            fullWidth
            label="Tax Saving Mutual Funds (ELSS)"
            type="text"
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('section_80c_tsmf', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('section_80c_tsmf', e)}
          />
          
          {/* Tuition Fees */}
          <TextField
            fullWidth
            label="Tuition Fees (for Children)"
            type="text"
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('section_80c_tffte2c', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('section_80c_tffte2c', e)}
          />
          
          {/* Housing Loan Principal Repayment */}
          <TextField
            fullWidth
            label="Housing Loan Principal Repayment"
            type="text"
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('section_80c_paphl', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('section_80c_paphl', e)}
          />
          
          {/* Sukanya Samriddhi */}
          <TextField
            fullWidth
            label="Sukanya Samriddhi"
            type="text"
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('section_80c_sdpphp', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('section_80c_sdpphp', e)}
          />
          
          {/* Bank FD */}
          <TextField
            fullWidth
            label="Tax Saving Bank FD (5 years)"
            type="text"
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('section_80c_tsfdsb', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('section_80c_tsfdsb', e)}
          />
          
          {/* Senior Citizens Savings Scheme */}
          <TextField
            fullWidth
            label="Senior Citizens Savings Scheme"
            type="text"
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('section_80c_scss', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('section_80c_scss', e)}
          />
          
          {/* Others */}
          <TextField
            fullWidth
            label="Others"
            type="text"
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('section_80c_others', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('section_80c_others', e)}
          />
        </Box>
      </Paper>
      
      <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
        <FormSectionHeader title="National Pension System (NPS)" withDivider={false} />
        
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: 3,
            width: '100%'
          }}
        >
          {/* Pension Plans (Sec 80CCC) */}
          <TextField
            fullWidth
            label="Pension Plans (Sec 80CCC)"
            type="text"
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('section_80ccc_ppic', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('section_80ccc_ppic', e)}
          />
          
          {/* NPS Contribution (Sec 80CCD(1)) */}
          <Tooltip title="NPS contribution (Sec 80CCD(1))" placement="top" arrow>
            <TextField
              fullWidth
              label="NPS Contribution (Sec 80CCD(1))"
              type="text"
              value={formatIndianNumber(0)}
              onChange={(e) => handleTextFieldChange('section_80ccd_1_nps', e)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleTextFieldFocus('section_80ccd_1_nps', e)}
            />
          </Tooltip>
          
          {/* Additional NPS (Sec 80CCD(1B)) */}
          <Tooltip title="Additional NPS (Sec 80CCD(1B)) Max ₹50,000" placement="top" arrow>
            <TextField
              fullWidth
              label="Additional NPS (Sec 80CCD(1B)) Max ₹50,000"
              type="text"
              value={formatIndianNumber(0)}
              onChange={(e) => handleTextFieldChange('section_80ccd_1b_additional', e)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleTextFieldFocus('section_80ccd_1b_additional', e)}
            />
          </Tooltip>
          
          {/* Employer NPS (Sec 80CCD(2)) */}
          <Tooltip title="Employer NPS Contribution (Sec 80CCD(2))" placement="top" arrow>
            <TextField
              fullWidth
              label="Employer NPS Contribution (Sec 80CCD(2))"
              type="text"
              value={formatIndianNumber(0)}
              onChange={(e) => handleTextFieldChange('section_80ccd_2_enps', e)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleTextFieldFocus('section_80ccd_2_enps', e)}
            />
          </Tooltip>
        </Box>
      </Paper>
      
      <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
        <FormSectionHeader title="Health Insurance (Sec 80D)" withDivider={false} />
        
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: 3,
            width: '100%'
          }}
        >
          {/* Health Insurance Self & Family */}
          <TextField
            fullWidth
            label="Health Insurance - Self & Family"
            type="text"
            value={formatIndianNumber(taxationData.section_80d || 0)}
            onChange={(e) => handleTextFieldChange('section_80d', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('section_80d', e)}
          />
          
          {/* Preventive Health Checkup */}
          <TextField
            fullWidth
            label="Preventive Health Checkup"
            type="text"
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('section_80d_checkup', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('section_80d_checkup', e)}
          />
          
          {/* Health Insurance for Parents */}
          <TextField
            fullWidth
            label="Health Insurance - Parents"
            type="text"
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('section_80d_parents', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('section_80d_parents', e)}
          />
        </Box>
      </Paper>
      
      <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
        <FormSectionHeader title="Other Deductions" withDivider={false} />
        
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: 3,
            width: '100%'
          }}
        >
          {/* Section 80DD - Disability */}
          <TextField
            fullWidth
            label="Section 80DD - Disability"
            type="text"
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('section_80dd', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('section_80dd', e)}
          />
          
          {/* Relation for 80DD */}
          <FormControl fullWidth>
            <Tooltip title="Relation with differently abled person">
              <Box>
                <InputLabel>Relation</InputLabel>
                <Select
                  value={'Parents'}
                  label="Relation for 80DD"
                  onChange={(e) => handleSelectChange('relation_80dd', e)}
                >
                  {relationOptions.map((relation) => (
                    <MenuItem key={relation} value={relation}>{relation}</MenuItem>
                  ))}
                </Select>
              </Box>
            </Tooltip>
          </FormControl>
          
          {/* Disability Percentage */}
          <FormControl fullWidth>
            <InputLabel>Disability Percentage</InputLabel>
            <Select
              value={'Between 40%-80%'}
              label="Disability Percentage"
              onChange={(e) => handleSelectChange('disability_percentage', e)}
            >
              {disabilityPercentageOptions.map((option) => (
                <MenuItem key={option} value={option}>{option}</MenuItem>
              ))}
            </Select>
          </FormControl>
          
          {/* Section 80DDB - Medical Treatment */}
          <Tooltip title="Medical Treatment" placement="top" arrow>
            <TextField
              fullWidth
              label="Section 80DDB - Medical Treatment"
              type="text"
              value={formatIndianNumber(0)}
              onChange={(e) => handleTextFieldChange('section_80ddb', e)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleTextFieldFocus('section_80ddb', e)}
            />
          </Tooltip>
          
          {/* Relation for 80DDB */}
          <FormControl fullWidth>
            <Tooltip title="Relation with treated person" placement="top" arrow>
              <Box>
                <InputLabel>Relation</InputLabel>
                <Select
                  value={'Parents'}
                  label="Relation for 80DDB"
                  onChange={(e) => handleSelectChange('relation_80ddb', e)}
                >
                  {relationOptions.map((relation) => (
                    <MenuItem key={relation} value={relation}>{relation}</MenuItem>
                  ))}
                </Select>
              </Box>
            </Tooltip>
          </FormControl>
          
          {/* Age for 80DDB */}
          <TextField
            fullWidth
            label="Age for 80DDB"
            type="number"
            value={0}
            onChange={(e) => handleTextFieldChange('age_80ddb', e)}
            onFocus={(e) => handleTextFieldFocus('age_80ddb', e)}
          />
          
          {/* Section 80U - Self Disability */}
          <TextField
            fullWidth
            label="Section 80U - Self Disability"
            type="text"
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('section_80u', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('section_80u', e)}
          />
          
          {/* Disability Percentage for 80U */}
          <FormControl fullWidth>
            <InputLabel>Disability Percentage (80U)</InputLabel>
            <Select
              value={'Between 40%-80%'}
              label="Disability Percentage (80U)"
              onChange={(e) => handleSelectChange('disability_percentage_80u', e)}
            >
              {disabilityPercentageOptions.map((option) => (
                <MenuItem key={option} value={option}>{option}</MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Section 80E - Educational Loan */}
          <Tooltip title="Higher Education, allowed for Initial Year + 7 immediately suceeding years" placement="top" arrow>
            <TextField
              fullWidth
              label="Section 80E - Educational Loan"
              type="text"
              value={formatIndianNumber(taxationData.section_80e || 0)}
              onChange={(e) => handleTextFieldChange('section_80e', e)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleTextFieldFocus('section_80e', e)}
            />
          </Tooltip>

          <FormControl fullWidth>
            <InputLabel>Relationship (80E)</InputLabel>
            <Select
              value={''}
              label="Relationship (80E)"
              onChange={(e) => handleSelectChange('relation_80e', e)}
            >
              <MenuItem value="Self">Self</MenuItem>
              <MenuItem value="Spouse">Spouse</MenuItem>
              <MenuItem value="Child">Child</MenuItem>
            </Select>
          </FormControl>
          
          {/* Section 80EEB - Electric Vehicle Loan */}
          <TextField
            fullWidth
            label="Section 80EEB - Electric Vehicle Loan Interest"
            type="text"
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('section_80eeb', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('section_80eeb', e)}
          />

          {/* EV Purchase Date */}
          <Tooltip title="Date of Purchase should be between 1st Apirl 2019 and 31st March 2023" placement="top" arrow>
            <TextField
              fullWidth
              label="Date of Purchase"
              type="date"
              value={''}
              onChange={(e) => handleTextFieldChange('ev_purchase_date', e)}
              InputLabelProps={{ shrink: true }}
            />
          </Tooltip>
        </Box>
      </Paper>
      
      <Paper variant="outlined" sx={{ p: 3 }}>
        <FormSectionHeader title="Donations (Section 80G)" withDivider={false} />
        
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: 3,
            width: '100%'
          }}
        >
          {/* 100% without qualifying limit section */}
          <Box sx={{ gridColumn: '1 / -1' }}>
            <Typography variant="h6" color="primary">100% Deduction without Qualifying Limit</Typography>
            <Divider sx={{ my: 2 }} />
          </Box>
          
          <TextField
            fullWidth
            label="100% Deduction - Amount"
            type="text"
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('section_80g_100_wo_ql', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('section_80g_100_wo_ql', e)}
          />
          
          <FormControl fullWidth>
            <InputLabel>Donation Head</InputLabel>
            <Select
              value={'National Defence Fund set up by Central Government'}
              label="Donation Head"
              onChange={(e) => handleSelectChange('section_80g_100_head', e)}
            >
              <MenuItem value="National Defence Fund set up by Central Government">National Defence Fund set up by Central Government</MenuItem>
              <MenuItem value="Prime Minister's National Relief Fund">Prime Minister's National Relief Fund</MenuItem>
              <MenuItem value="Any other fund set up by Central Government for charitable purposes">Any other fund set up by Central Government for charitable purposes</MenuItem>
            </Select>
          </FormControl>
          
          {/* 50% without qualifying limit section */}
          <Box sx={{ gridColumn: '1 / -1' }}>
            <Typography variant="h6" color="primary">50% Deduction without Qualifying Limit</Typography>
            <Divider sx={{ my: 2 }} />
          </Box>
          
          <TextField
            fullWidth
            label="50% Deduction - Amount"
            type="text"
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('section_80g_50_wo_ql', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('section_80g_50_wo_ql', e)}
          />
          
          <FormControl fullWidth>
            <InputLabel>Donation Head</InputLabel>
            <Select
              value={'Prime Minister\'s Drought Relief Fund'}
              label="Donation Head"
              onChange={(e) => handleSelectChange('section_80g_50_head', e)}
            >
              <MenuItem value="Prime Minister's Drought Relief Fund">Prime Minister's Drought Relief Fund</MenuItem>
              <MenuItem value="National Foundation for Communal Harmony">National Foundation for Communal Harmony</MenuItem>
              <MenuItem value="Any other fund approved by Central Government">Any other fund approved by Central Government</MenuItem>
            </Select>
          </FormControl>
          
          {/* 100% with qualifying limit section */}
          <Box sx={{ gridColumn: '1 / -1' }}>
            <Typography variant="h6" color="primary">100% Deduction with Qualifying Limit</Typography>
            <Divider sx={{ my: 2 }} />
          </Box>
          
          <TextField
            fullWidth
            label="100% Deduction (with limit) - Amount"
            type="text"
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('section_80g_100_ql', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('section_80g_100_ql', e)}
          />
          
          <FormControl fullWidth>
            <InputLabel>Donation Head</InputLabel>
            <Select
              value={'Donations to government or any approved local authority to promote family planning'}
              label="Donation Head"
              onChange={(e) => handleSelectChange('section_80g_100_ql_head', e)}
            >
              <MenuItem value="Donations to government or any approved local authority to promote family planning">Donations to government or any approved local authority to promote family planning</MenuItem>
              <MenuItem value="Any other approved institution for family planning">Any other approved institution for family planning</MenuItem>
            </Select>
          </FormControl>
          
          {/* 50% with qualifying limit section */}
          <Box sx={{ gridColumn: '1 / -1' }}>
            <Typography variant="h6" color="primary">50% Deduction with Qualifying Limit</Typography>
            <Divider sx={{ my: 2 }} />
          </Box>
          
          <TextField
            fullWidth
            label="50% Deduction (with limit) - Amount"
            type="text"
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('section_80g_50_ql', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('section_80g_50_ql', e)}
          />
          
          <FormControl fullWidth>
            <InputLabel>Donation Head</InputLabel>
            <Select
              value={'Donations to government or any approved local authority to except to promote family planning'}
              label="Donation Head"
              onChange={(e) => handleSelectChange('section_80g_50_ql_head', e)}
            >
              <MenuItem value="Donations to government or any approved local authority to except to promote family planning">Donations to government or any approved local authority to except to promote family planning</MenuItem>
              <MenuItem value="Any other approved charitable institution">Any other approved charitable institution</MenuItem>
            </Select>
          </FormControl>
          
          {/* Political donations section */}
          <Box sx={{ gridColumn: '1 / -1' }}>
            <Typography variant="h6" color="primary">100% Deduction to Political Donations</Typography>
            <Divider sx={{ my: 2 }} />
          </Box>
          
          {/* Section 80GGC - Political Donations */}
          <TextField
            fullWidth
            label="Section 80GGC - Political Donations"
            type="text"
            value={formatIndianNumber(0)}
            onChange={(e) => handleTextFieldChange('section_80ggc', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('section_80ggc', e)}
          />
        </Box>
      </Paper>
    </Box>
  );
};

export default DeductionsSection; 