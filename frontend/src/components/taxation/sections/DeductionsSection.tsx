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
            value={formatIndianNumber(taxationData.deductions?.section_80c?.life_insurance_premium || 0)}
            onChange={(e) => handleTextFieldChange('deductions.section_80c.life_insurance_premium', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('deductions.section_80c.life_insurance_premium', e)}
          />
          
          {/* EPF */}
          <TextField
            fullWidth
            label="EPF Contribution"
            type="text"
            value={formatIndianNumber(taxationData.deductions?.section_80c?.epf_contribution || 0)}
            onChange={(e) => handleTextFieldChange('deductions.section_80c.epf_contribution', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('deductions.section_80c.epf_contribution', e)}
          />
          
          {/* PPF */}
          <TextField
            fullWidth
            label="PPF"
            type="text"
            value={formatIndianNumber(taxationData.deductions?.section_80c?.ppf_contribution || 0)}
            onChange={(e) => handleTextFieldChange('deductions.section_80c.ppf_contribution', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('deductions.section_80c.ppf_contribution', e)}
          />
          
          {/* NSC */}
          <TextField
            fullWidth
            label="NSC"
            type="text"
            value={formatIndianNumber(taxationData.deductions?.section_80c?.nsc_investment || 0)}
            onChange={(e) => handleTextFieldChange('deductions.section_80c.nsc_investment', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('deductions.section_80c.nsc_investment', e)}
          />
          
          {/* ULIP */}
          <TextField
            fullWidth
            label="ULIP"
            type="text"
            value={formatIndianNumber(taxationData.deductions?.section_80c?.ulip_premium || 0)}
            onChange={(e) => handleTextFieldChange('deductions.section_80c.ulip_premium', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('deductions.section_80c.ulip_premium', e)}
          />
          
          {/* Tax Saving Mutual Funds */}
          <TextField
            fullWidth
            label="Tax Saving Mutual Funds (ELSS)"
            type="text"
            value={formatIndianNumber(taxationData.deductions?.section_80c?.elss_investment || 0)}
            onChange={(e) => handleTextFieldChange('deductions.section_80c.elss_investment', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('deductions.section_80c.elss_investment', e)}
          />
          
          {/* Tuition Fees */}
          <TextField
            fullWidth
            label="Tuition Fees (for Children)"
            type="text"
            value={formatIndianNumber(taxationData.deductions?.section_80c?.tuition_fees || 0)}
            onChange={(e) => handleTextFieldChange('deductions.section_80c.tuition_fees', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('deductions.section_80c.tuition_fees', e)}
          />
          
          {/* Housing Loan Principal Repayment */}
          <TextField
            fullWidth
            label="Housing Loan Principal Repayment"
            type="text"
            value={formatIndianNumber(taxationData.deductions?.section_80c?.home_loan_principal || 0)}
            onChange={(e) => handleTextFieldChange('deductions.section_80c.home_loan_principal', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('deductions.section_80c.home_loan_principal', e)}
          />
          
          {/* Sukanya Samriddhi */}
          <TextField
            fullWidth
            label="Sukanya Samriddhi"
            type="text"
            value={formatIndianNumber(taxationData.deductions?.section_80c?.sukanya_samriddhi || 0)}
            onChange={(e) => handleTextFieldChange('deductions.section_80c.sukanya_samriddhi', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('deductions.section_80c.sukanya_samriddhi', e)}
          />
          
          {/* Bank FD */}
          <TextField
            fullWidth
            label="Tax Saving Bank FD (5 years)"
            type="text"
            value={formatIndianNumber(taxationData.deductions?.section_80c?.tax_saving_fd || 0)}
            onChange={(e) => handleTextFieldChange('deductions.section_80c.tax_saving_fd', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('deductions.section_80c.tax_saving_fd', e)}
          />
          
          {/* Senior Citizens Savings Scheme */}
          <TextField
            fullWidth
            label="Senior Citizens Savings Scheme"
            type="text"
            value={formatIndianNumber(taxationData.deductions?.section_80c?.senior_citizen_savings || 0)}
            onChange={(e) => handleTextFieldChange('deductions.section_80c.senior_citizen_savings', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('deductions.section_80c.senior_citizen_savings', e)}
          />
          
          {/* Others */}
          <TextField
            fullWidth
            label="Others"
            type="text"
            value={formatIndianNumber(taxationData.deductions?.section_80c?.other_80c_investments || 0)}
            onChange={(e) => handleTextFieldChange('deductions.section_80c.other_80c_investments', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('deductions.section_80c.other_80c_investments', e)}
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
            value={formatIndianNumber(taxationData.deductions?.section_80ccc?.pension_fund_contribution || 0)}
            onChange={(e) => handleTextFieldChange('deductions.section_80ccc.pension_fund_contribution', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('deductions.section_80ccc.pension_fund_contribution', e)}
          />
          
          {/* NPS Contribution (Sec 80CCD(1)) */}
          <Tooltip title="NPS contribution (Sec 80CCD(1))" placement="top" arrow>
            <TextField
              fullWidth
              label="NPS Contribution (Sec 80CCD(1))"
              type="text"
              value={formatIndianNumber(taxationData.deductions?.section_80ccd?.employee_nps_contribution || 0)}
              onChange={(e) => handleTextFieldChange('deductions.section_80ccd.employee_nps_contribution', e)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleTextFieldFocus('deductions.section_80ccd.employee_nps_contribution', e)}
            />
          </Tooltip>
          
          {/* Additional NPS (Sec 80CCD(1B)) */}
          <Tooltip title="Additional NPS (Sec 80CCD(1B)) Max ₹50,000" placement="top" arrow>
            <TextField
              fullWidth
              label="Additional NPS (Sec 80CCD(1B)) Max ₹50,000"
              type="text"
              value={formatIndianNumber(taxationData.deductions?.section_80ccd?.additional_nps_contribution || 0)}
              onChange={(e) => handleTextFieldChange('deductions.section_80ccd.additional_nps_contribution', e)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleTextFieldFocus('deductions.section_80ccd.additional_nps_contribution', e)}
            />
          </Tooltip>
          
          {/* Employer NPS (Sec 80CCD(2)) */}
          <Tooltip title="Employer NPS Contribution (Sec 80CCD(2))" placement="top" arrow>
            <TextField
              fullWidth
              label="Employer NPS Contribution (Sec 80CCD(2))"
              type="text"
              value={formatIndianNumber(taxationData.deductions?.section_80ccd?.employer_nps_contribution || 0)}
              onChange={(e) => handleTextFieldChange('deductions.section_80ccd.employer_nps_contribution', e)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleTextFieldFocus('deductions.section_80ccd.employer_nps_contribution', e)}
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
            value={formatIndianNumber(taxationData.deductions?.section_80d?.self_family_premium || 0)}
            onChange={(e) => handleTextFieldChange('deductions.section_80d.self_family_premium', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('deductions.section_80d.self_family_premium', e)}
          />
          
          {/* Preventive Health Checkup */}
          <TextField
            fullWidth
            label="Preventive Health Checkup"
            type="text"
            value={formatIndianNumber(taxationData.deductions?.section_80d?.preventive_health_checkup || 0)}
            onChange={(e) => handleTextFieldChange('deductions.section_80d.preventive_health_checkup', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('deductions.section_80d.preventive_health_checkup', e)}
          />
          
          {/* Health Insurance for Parents */}
          <TextField
            fullWidth
            label="Health Insurance - Parents"
            type="text"
            value={formatIndianNumber(taxationData.deductions?.section_80d?.parent_premium || 0)}
            onChange={(e) => handleTextFieldChange('deductions.section_80d.parent_premium', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('deductions.section_80d.parent_premium', e)}
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
            value={formatIndianNumber(taxationData.deductions?.section_80dd?.relation ? 75000 : 0)}
            onChange={(e) => handleTextFieldChange('deductions.section_80dd.relation', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('deductions.section_80dd.relation', e)}
          />
          
          {/* Relation for 80DD */}
          <FormControl fullWidth>
            <Tooltip title="Relation with differently abled person">
              <Box>
                <InputLabel>Relation</InputLabel>
                <Select
                  value={taxationData.deductions?.section_80dd?.relation || 'Parents'}
                  label="Relation for 80DD"
                  onChange={(e) => handleSelectChange('deductions.section_80dd.relation', e)}
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
              value={taxationData.deductions?.section_80dd?.disability_percentage || 'Between 40%-80%'}
              label="Disability Percentage"
              onChange={(e) => handleSelectChange('deductions.section_80dd.disability_percentage', e)}
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
              value={formatIndianNumber(taxationData.deductions?.section_80ddb?.medical_expenses || 0)}
              onChange={(e) => handleTextFieldChange('deductions.section_80ddb.medical_expenses', e)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleTextFieldFocus('deductions.section_80ddb.medical_expenses', e)}
            />
          </Tooltip>
          
          {/* Relation for 80DDB */}
          <FormControl fullWidth>
            <Tooltip title="Relation with treated person" placement="top" arrow>
              <Box>
                <InputLabel>Relation</InputLabel>
                <Select
                  value={taxationData.deductions?.section_80ddb?.relation || 'Parents'}
                  label="Relation for 80DDB"
                  onChange={(e) => handleSelectChange('deductions.section_80ddb.relation', e)}
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
            value={taxationData.deductions?.section_80ddb?.dependent_age || 0}
            onChange={(e) => handleTextFieldChange('deductions.section_80ddb.dependent_age', e)}
            onFocus={(e) => handleTextFieldFocus('deductions.section_80ddb.dependent_age', e)}
          />
          
          {/* Section 80U - Self Disability */}
          <TextField
            fullWidth
            label="Section 80U - Self Disability"
            type="text"
            value={formatIndianNumber(taxationData.deductions?.section_80u?.disability_percentage ? 75000 : 0)}
            onChange={(e) => handleTextFieldChange('deductions.section_80u.disability_percentage', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('deductions.section_80u.disability_percentage', e)}
          />
          
          {/* Disability Percentage for 80U */}
          <FormControl fullWidth>
            <InputLabel>Disability Percentage (80U)</InputLabel>
            <Select
              value={taxationData.deductions?.section_80u?.disability_percentage || 'Between 40%-80%'}
              label="Disability Percentage (80U)"
              onChange={(e) => handleSelectChange('deductions.section_80u.disability_percentage', e)}
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
              value={formatIndianNumber(taxationData.deductions?.section_80e?.education_loan_interest || 0)}
              onChange={(e) => handleTextFieldChange('deductions.section_80e.education_loan_interest', e)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleTextFieldFocus('deductions.section_80e.education_loan_interest', e)}
            />
          </Tooltip>

          <FormControl fullWidth>
            <InputLabel>Relationship (80E)</InputLabel>
            <Select
              value={taxationData.deductions?.section_80e?.relation || ''}
              label="Relationship (80E)"
              onChange={(e) => handleSelectChange('deductions.section_80e.relation', e)}
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
            value={formatIndianNumber(taxationData.deductions?.section_80eeb?.ev_loan_interest || 0)}
            onChange={(e) => handleTextFieldChange('deductions.section_80eeb.ev_loan_interest', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('deductions.section_80eeb.ev_loan_interest', e)}
          />

          {/* EV Purchase Date */}
          <Tooltip title="Date of Purchase should be between 1st Apirl 2019 and 31st March 2023" placement="top" arrow>
            <TextField
              fullWidth
              label="Date of Purchase"
              type="date"
              value={taxationData.deductions?.section_80eeb?.ev_purchase_date || ''}
              onChange={(e) => handleTextFieldChange('deductions.section_80eeb.ev_purchase_date', e)}
              InputLabelProps={{ shrink: true }}
            />
          </Tooltip>
        </Box>
      </Paper>
      
      <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
        <FormSectionHeader title="HRA Exemption" withDivider={false} />
        
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: 3,
            width: '100%'
          }}
        >
          {/* Actual Rent Paid */}
          <TextField
            fullWidth
            label="Actual Rent Paid"
            type="text"
            value={formatIndianNumber(taxationData.deductions?.hra_exemption?.actual_rent_paid || 0)}
            onChange={(e) => handleTextFieldChange('deductions.hra_exemption.actual_rent_paid', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('deductions.hra_exemption.actual_rent_paid', e)}
            helperText="Enter the actual rent amount you pay annually"
          />
          
          {/* HRA City Type */}
          <FormControl fullWidth>
            <InputLabel>City Type for HRA Calculation</InputLabel>
            <Select
              value={taxationData.deductions?.hra_exemption?.hra_city_type || 'non_metro'}
              label="City Type for HRA Calculation"
              onChange={(e) => handleSelectChange('deductions.hra_exemption.hra_city_type', e)}
            >
              <MenuItem value="metro">Metro City (50% exemption)</MenuItem>
              <MenuItem value="non_metro">Non-Metro City (40% exemption)</MenuItem>
            </Select>
          </FormControl>
        </Box>
        
        <Alert severity="info" sx={{ mt: 2 }}>
          <Typography variant="body2">
            <strong>HRA Exemption Calculation:</strong> The exemption is the minimum of:
            <br />• Actual HRA received from employer
            <br />• {taxationData.deductions?.hra_exemption?.hra_city_type === 'metro' ? '50%' : '40%'} of (Basic Salary + Dearness Allowance)
            <br />• Actual rent paid minus 10% of (Basic Salary + Dearness Allowance)
          </Typography>
        </Alert>
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
            label="PM Relief Fund"
            type="text"
            value={formatIndianNumber(taxationData.deductions?.section_80g?.pm_relief_fund || 0)}
            onChange={(e) => handleTextFieldChange('deductions.section_80g.pm_relief_fund', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('deductions.section_80g.pm_relief_fund', e)}
          />
          
          <TextField
            fullWidth
            label="National Defence Fund"
            type="text"
            value={formatIndianNumber(taxationData.deductions?.section_80g?.national_defence_fund || 0)}
            onChange={(e) => handleTextFieldChange('deductions.section_80g.national_defence_fund', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('deductions.section_80g.national_defence_fund', e)}
          />
          
          <TextField
            fullWidth
            label="CM Relief Fund"
            type="text"
            value={formatIndianNumber(taxationData.deductions?.section_80g?.cm_relief_fund || 0)}
            onChange={(e) => handleTextFieldChange('deductions.section_80g.cm_relief_fund', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('deductions.section_80g.cm_relief_fund', e)}
          />
          
          {/* 50% without qualifying limit section */}
          <Box sx={{ gridColumn: '1 / -1' }}>
            <Typography variant="h6" color="primary">50% Deduction without Qualifying Limit</Typography>
            <Divider sx={{ my: 2 }} />
          </Box>
          
          <TextField
            fullWidth
            label="JN Memorial Fund"
            type="text"
            value={formatIndianNumber(taxationData.deductions?.section_80g?.jn_memorial_fund || 0)}
            onChange={(e) => handleTextFieldChange('deductions.section_80g.jn_memorial_fund', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('deductions.section_80g.jn_memorial_fund', e)}
          />
          
          <TextField
            fullWidth
            label="PM Drought Relief Fund"
            type="text"
            value={formatIndianNumber(taxationData.deductions?.section_80g?.pm_drought_relief || 0)}
            onChange={(e) => handleTextFieldChange('deductions.section_80g.pm_drought_relief', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('deductions.section_80g.pm_drought_relief', e)}
          />
          
          {/* 100% with qualifying limit section */}
          <Box sx={{ gridColumn: '1 / -1' }}>
            <Typography variant="h6" color="primary">100% Deduction with Qualifying Limit</Typography>
            <Divider sx={{ my: 2 }} />
          </Box>
          
          <TextField
            fullWidth
            label="Family Planning Donation"
            type="text"
            value={formatIndianNumber(taxationData.deductions?.section_80g?.family_planning_donation || 0)}
            onChange={(e) => handleTextFieldChange('deductions.section_80g.family_planning_donation', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('deductions.section_80g.family_planning_donation', e)}
          />
          
          <TextField
            fullWidth
            label="Indian Olympic Association"
            type="text"
            value={formatIndianNumber(taxationData.deductions?.section_80g?.indian_olympic_association || 0)}
            onChange={(e) => handleTextFieldChange('deductions.section_80g.indian_olympic_association', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('deductions.section_80g.indian_olympic_association', e)}
          />
          
          {/* 50% with qualifying limit section */}
          <Box sx={{ gridColumn: '1 / -1' }}>
            <Typography variant="h6" color="primary">50% Deduction with Qualifying Limit</Typography>
            <Divider sx={{ my: 2 }} />
          </Box>
          
          <TextField
            fullWidth
            label="Government Charitable Donations"
            type="text"
            value={formatIndianNumber(taxationData.deductions?.section_80g?.govt_charitable_donations || 0)}
            onChange={(e) => handleTextFieldChange('deductions.section_80g.govt_charitable_donations', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('deductions.section_80g.govt_charitable_donations', e)}
          />
          
          <TextField
            fullWidth
            label="Other Charitable Donations"
            type="text"
            value={formatIndianNumber(taxationData.deductions?.section_80g?.other_charitable_donations || 0)}
            onChange={(e) => handleTextFieldChange('deductions.section_80g.other_charitable_donations', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('deductions.section_80g.other_charitable_donations', e)}
          />
          
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
            value={formatIndianNumber(taxationData.deductions?.section_80ggc?.political_party_contribution || 0)}
            onChange={(e) => handleTextFieldChange('deductions.section_80ggc.political_party_contribution', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('deductions.section_80ggc.political_party_contribution', e)}
          />
        </Box>
      </Paper>
    </Box>
  );
};

export default DeductionsSection; 