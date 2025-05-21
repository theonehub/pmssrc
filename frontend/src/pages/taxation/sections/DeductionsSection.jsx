import React from 'react';
import {
  Box,
  Typography,
  Grid,
  TextField,
  Paper,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Tooltip
} from '@mui/material';
import { formatIndianNumber } from '../utils/taxationUtils';
import FormSectionHeader from '../components/FormSectionHeader';
import {
  section80G100WoQlHeads,
  section80G50WoQlHeads,
  section80G100QlHeads,
  section80G50QlHeads,
  disabilityPercentageOptions,
  relationOptions
} from '../utils/taxationConstants';

/**
 * Deductions Section Component
 * @param {Object} props - Component props
 * @param {Object} props.taxationData - Taxation data state
 * @param {Function} props.handleInputChange - Function to handle input change
 * @param {Function} props.handleFocus - Function to handle focus
 * @returns {JSX.Element} Deductions section component
 */
const DeductionsSection = ({
  taxationData,
  handleInputChange,
  handleFocus
}) => {
  // Only show alert for old regime
  const showDeductionsAlert = taxationData.regime === 'new';
  
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
        
        <Grid container spacing={3}>
          {/* LIC Premium */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="LIC Premium"
              type="text"
              value={formatIndianNumber(taxationData.deductions.section_80c_lic)}
              onChange={(e) => handleInputChange('deductions', 'section_80c_lic', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('deductions', 'section_80c_lic', e.target.value)}
            />
          </Grid>
          
          {/* EPF */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="EPF Contribution"
              type="text"
              value={formatIndianNumber(taxationData.deductions.section_80c_epf)}
              onChange={(e) => handleInputChange('deductions', 'section_80c_epf', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('deductions', 'section_80c_epf', e.target.value)}
            />
          </Grid>
          
          {/* PPF */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="PPF"
              type="text"
              value={formatIndianNumber(taxationData.deductions.section_80c_ssp)}
              onChange={(e) => handleInputChange('deductions', 'section_80c_ssp', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('deductions', 'section_80c_ssp', e.target.value)}
            />
          </Grid>
          
          {/* NSC */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="NSC"
              type="text"
              value={formatIndianNumber(taxationData.deductions.section_80c_nsc)}
              onChange={(e) => handleInputChange('deductions', 'section_80c_nsc', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('deductions', 'section_80c_nsc', e.target.value)}
            />
          </Grid>
          
          {/* ULIP */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="ULIP"
              type="text"
              value={formatIndianNumber(taxationData.deductions.section_80c_ulip)}
              onChange={(e) => handleInputChange('deductions', 'section_80c_ulip', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('deductions', 'section_80c_ulip', e.target.value)}
            />
          </Grid>
          
          {/* Tax Saving Mutual Funds */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Tax Saving Mutual Funds (ELSS)"
              type="text"
              value={formatIndianNumber(taxationData.deductions.section_80c_tsmf)}
              onChange={(e) => handleInputChange('deductions', 'section_80c_tsmf', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('deductions', 'section_80c_tsmf', e.target.value)}
            />
          </Grid>
          
          {/* Tuition Fees */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Tuition Fees (for Children)"
              type="text"
              value={formatIndianNumber(taxationData.deductions.section_80c_tffte2c)}
              onChange={(e) => handleInputChange('deductions', 'section_80c_tffte2c', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('deductions', 'section_80c_tffte2c', e.target.value)}
            />
          </Grid>
          
          {/* Housing Loan Principal Repayment */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Housing Loan Principal Repayment"
              type="text"
              value={formatIndianNumber(taxationData.deductions.section_80c_paphl)}
              onChange={(e) => handleInputChange('deductions', 'section_80c_paphl', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('deductions', 'section_80c_paphl', e.target.value)}
            />
          </Grid>
          
          {/* Sukanya Samriddhi */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Sukanya Samriddhi"
              type="text"
              value={formatIndianNumber(taxationData.deductions.section_80c_sdpphp)}
              onChange={(e) => handleInputChange('deductions', 'section_80c_sdpphp', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('deductions', 'section_80c_sdpphp', e.target.value)}
            />
          </Grid>
          
          {/* Bank FD */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Tax Saving Bank FD (5 years)"
              type="text"
              value={formatIndianNumber(taxationData.deductions.section_80c_tsfdsb)}
              onChange={(e) => handleInputChange('deductions', 'section_80c_tsfdsb', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('deductions', 'section_80c_tsfdsb', e.target.value)}
            />
          </Grid>
          
          {/* Senior Citizens Savings Scheme */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Senior Citizens Savings Scheme"
              type="text"
              value={formatIndianNumber(taxationData.deductions.section_80c_scss)}
              onChange={(e) => handleInputChange('deductions', 'section_80c_scss', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('deductions', 'section_80c_scss', e.target.value)}
            />
          </Grid>
          
          {/* Others */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Others"
              type="text"
              value={formatIndianNumber(taxationData.deductions.section_80c_others)}
              onChange={(e) => handleInputChange('deductions', 'section_80c_others', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('deductions', 'section_80c_others', e.target.value)}
            />
          </Grid>
        </Grid>
      </Paper>
      
      <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
        <FormSectionHeader title="National Pension System (NPS)" withDivider={false} />
        
        <Grid container spacing={3}>
          {/* Pension Plans (Sec 80CCC) */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Pension Plans (Sec 80CCC)"
              type="text"
              value={formatIndianNumber(taxationData.deductions.section_80ccc_ppic)}
              onChange={(e) => handleInputChange('deductions', 'section_80ccc_ppic', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('deductions', 'section_80ccc_ppic', e.target.value)}
            />
          </Grid>
          
          {/* NPS Contribution (Sec 80CCD(1)) */}
          <Grid item xs={12} md={6}>
            <Tooltip title="NPS contribution (Sec 80CCD(1))"
            placement="top"
            arrow
            >
              <TextField
                fullWidth
                label="NPS Contribution (Sec 80CCD(1))"
                type="text"
                value={formatIndianNumber(taxationData.deductions.section_80ccd_1_nps)}
                onChange={(e) => handleInputChange('deductions', 'section_80ccd_1_nps', e.target.value)}
                InputProps={{ startAdornment: '₹' }}
                onFocus={(e) => handleFocus('deductions', 'section_80ccd_1_nps', e.target.value)}
              />
            </Tooltip>
          </Grid>
          
          {/* Additional NPS (Sec 80CCD(1B)) */}
          <Grid item xs={12} md={6}>
            <Tooltip title="Additional NPS (Sec 80CCD(1B)) Max ₹50,000"
            placement="top"
            arrow
            >
              <TextField
                fullWidth
                label="Additional NPS (Sec 80CCD(1B)) Max ₹50,000"
                type="text"
                value={formatIndianNumber(taxationData.deductions.section_80ccd_1b_additional)}
                onChange={(e) => handleInputChange('deductions', 'section_80ccd_1b_additional', e.target.value)}
                InputProps={{ startAdornment: '₹' }}
                onFocus={(e) => handleFocus('deductions', 'section_80ccd_1b_additional', e.target.value)}
              />
            </Tooltip>
          </Grid>
          
          {/* Employer NPS (Sec 80CCD(2)) */}
          <Grid item xs={12} md={6}>
            <Tooltip title="Employer NPS Contribution (Sec 80CCD(2))"
            placement="top"
            arrow
            >
              <TextField
                fullWidth
                label="Employer NPS Contribution (Sec 80CCD(2))"
                type="text"
                value={formatIndianNumber(taxationData.deductions.section_80ccd_2_enps)}
                onChange={(e) => handleInputChange('deductions', 'section_80ccd_2_enps', e.target.value)}
                InputProps={{ startAdornment: '₹' }}
                onFocus={(e) => handleFocus('deductions', 'section_80ccd_2_enps', e.target.value)}
              />
            </Tooltip>
          </Grid>
        </Grid>
      </Paper>
      
      <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
        <FormSectionHeader title="Health Insurance (Sec 80D)" withDivider={false} />
        
        <Grid container spacing={3}>
          {/* Health Insurance Self & Family */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Health Insurance - Self & Family"
              type="text"
              value={formatIndianNumber(taxationData.deductions.section_80d_hisf)}
              onChange={(e) => handleInputChange('deductions', 'section_80d_hisf', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('deductions', 'section_80d_hisf', e.target.value)}
            />
          </Grid>
          
          {/* Preventive Health Checkup */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Preventive Health Checkup"
              type="text"
              value={formatIndianNumber(taxationData.deductions.section_80d_phcs)}
              onChange={(e) => handleInputChange('deductions', 'section_80d_phcs', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('deductions', 'section_80d_phcs', e.target.value)}
            />
          </Grid>
          
          {/* Health Insurance for Parents */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Health Insurance - Parents"
              type="text"
              value={formatIndianNumber(taxationData.deductions.section_80d_hi_parent)}
              onChange={(e) => handleInputChange('deductions', 'section_80d_hi_parent', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('deductions', 'section_80d_hi_parent', e.target.value)}
            />
          </Grid>
        </Grid>
      </Paper>
      
      <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
        <FormSectionHeader title="Other Deductions" withDivider={false} />
        
        <Grid container spacing={3}>
          {/* Section 80DD - Disability */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Section 80DD - Disability"
              type="text"
              value={formatIndianNumber(taxationData.deductions.section_80dd)}
              onChange={(e) => handleInputChange('deductions', 'section_80dd', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('deductions', 'section_80dd', e.target.value)}
            />
          </Grid>
          
          {/* Relation for 80DD */}
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <Tooltip title="Relation with differently abled person">
                <InputLabel>Relation</InputLabel>
                <Select
                  value={taxationData.deductions.relation_80dd || 'Parents'}
                  label="Relation for 80DD"
                  onChange={(e) => handleInputChange('deductions', 'relation_80dd', e.target.value)}
                >
                  {relationOptions.map((relation) => (
                    <MenuItem key={relation} value={relation}>{relation}</MenuItem>
                  ))}
                </Select>
              </Tooltip>
            </FormControl>
          </Grid>
          
          {/* Disability Percentage */}
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Disability Percentage</InputLabel>
              <Select
                value={taxationData.deductions.disability_percentage || 'Between 40%-80%'}
                label="Disability Percentage"
                onChange={(e) => handleInputChange('deductions', 'disability_percentage', e.target.value)}
              >
                {disabilityPercentageOptions.map((option) => (
                  <MenuItem key={option} value={option}>{option}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Box 
            sx={{ 
              width: '100%', 
              display: 'flex',
              justifyContent: 'left'
            }}
          >
          </Box>
          
          {/* Section 80DDB - Medical Treatment */}
          <Grid item xs={12} md={6}>
            <Tooltip title="Medical Treatment"
            placement="top"
            arrow
            >
              <TextField
                fullWidth
                label="Section 80DDB - Medical Treatment"
                type="text"
                value={formatIndianNumber(taxationData.deductions.section_80ddb)}
                onChange={(e) => handleInputChange('deductions', 'section_80ddb', e.target.value)}
                InputProps={{ startAdornment: '₹' }}
                onFocus={(e) => handleFocus('deductions', 'section_80ddb', e.target.value)}
              />
            </Tooltip>
          </Grid>
          
          {/* Relation for 80DDB */}
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <Tooltip title="Relation with treated person"
              placement="top"
              arrow
              >
                <InputLabel>Relation</InputLabel>
                <Select
                  value={taxationData.deductions.relation_80ddb || 'Parents'}
                  label="Relation for 80DDB"
                  onChange={(e) => handleInputChange('deductions', 'relation_80ddb', e.target.value)}
                >
                  {relationOptions.map((relation) => (
                    <MenuItem key={relation} value={relation}>{relation}</MenuItem>
                  ))}
                </Select>
              </Tooltip>
            </FormControl>
          </Grid>
          
          {/* Age for 80DDB */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Age for 80DDB"
              type="number"
              value={taxationData.deductions.age_80ddb || 0}
              onChange={(e) => handleInputChange('deductions', 'age_80ddb', e.target.value)}
              onFocus={(e) => handleFocus('deductions', 'age_80ddb', e.target.value)}
            />
          </Grid>
          
          <Box 
            sx={{ 
              width: '100%', 
              display: 'flex',
              justifyContent: 'left'
            }}
          >
          </Box>
          
          {/* Section 80U - Self Disability */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Section 80U - Self Disability"
              type="text"
              value={formatIndianNumber(taxationData.deductions.section_80u)}
              onChange={(e) => handleInputChange('deductions', 'section_80u', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('deductions', 'section_80u', e.target.value)}
            />
          </Grid>
          
          {/* Disability Percentage for 80U */}
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Disability Percentage (80U)</InputLabel>
              <Select
                value={taxationData.deductions.disability_percentage_80u || 'Between 40%-80%'}
                label="Disability Percentage (80U)"
                onChange={(e) => handleInputChange('deductions', 'disability_percentage_80u', e.target.value)}
              >
                {disabilityPercentageOptions.map((option) => (
                  <MenuItem key={option} value={option}>{option}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Box 
            sx={{ 
              width: '100%', 
              display: 'flex',
              justifyContent: 'left'
            }}
          >
          </Box>
          {/* Section 80E - Educational Loan */}
          <Grid item xs={12} md={6}>
            <Tooltip title="Higher Education, allowed for Initial Year + 7 immediately suceeding years"
            placement="top"
            arrow
            >
              <TextField
                fullWidth
                label="Section 80E - Educational Loan"
                type="text"
                value={formatIndianNumber(taxationData.deductions.section_80e_interest)}
                onChange={(e) => handleInputChange('deductions', 'section_80e_interest', e.target.value)}
                InputProps={{ startAdornment: '₹' }}
                onFocus={(e) => handleFocus('deductions', 'section_80e_interest', e.target.value)}
              />
            </Tooltip>
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Relationship (80E)</InputLabel>
              <Select
                value={taxationData.deductions.relation_80e || ''}
                label="Relationship (80E)"
                onChange={(e) => handleInputChange('deductions', 'relation_80e', e.target.value)}
              >
                <MenuItem value="Self">Self</MenuItem>
                <MenuItem value="Spouse">Spouse</MenuItem>
                <MenuItem value="Child">Child</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          {/* Section 80EEB - Electric Vehicle Loan */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Section 80EEB - Electric Vehicle Loan Interest"
              type="text"
              value={formatIndianNumber(taxationData.deductions.section_80eeb)}
              onChange={(e) => handleInputChange('deductions', 'section_80eeb', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('deductions', 'section_80eeb', e.target.value)}
            />
          </Grid>
          {/* Loan Start Date */}
          <Grid item xs={12} md={6}>
            <Tooltip title="Date of Purchase should be between 1st Apirl 2019 and 31st March 2023"
            placement="top"
            arrow
            >
              <TextField
                fullWidth
                label="Date of Purchase"
                type="date"
                value={taxationData.deductions.ev_purchase_date || ''}
                onChange={(e) => handleInputChange('deductions', 'ev_purchase_date', e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Tooltip>
          </Grid>
        </Grid>
      </Paper>
      
      <Paper variant="outlined" sx={{ p: 3 }}>
        <FormSectionHeader title="Donations (Section 80G)" withDivider={false} />
        
        <Grid container spacing={3}>
          {/* 100% without qualifying limit */}
            <Box 
            sx={{ 
              width: '100%', 
              display: 'flex',
              justifyContent: 'left'
            }}
          >
            <Typography variant="h6" color="primary">100% Deduction without Qualifying Limit</Typography>
          </Box>
          <Divider sx={{ my: 0, width: '100%' }} />
          
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="100% Deduction - Amount"
              type="text"
              value={formatIndianNumber(taxationData.deductions.section_80g_100_wo_ql)}
              onChange={(e) => handleInputChange('deductions', 'section_80g_100_wo_ql', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('deductions', 'section_80g_100_wo_ql', e.target.value)}
            />
          </Grid>
          
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Donation Head</InputLabel>
              <Select
                value={taxationData.deductions.section_80g_100_head || 'National Defence Fund set up by Central Government'}
                label="Donation Head"
                onChange={(e) => handleInputChange('deductions', 'section_80g_100_head', e.target.value)}
              >
                {section80G100WoQlHeads.map((head) => (
                  <MenuItem key={head} value={head}>{head}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Box 
            sx={{ 
              width: '100%', 
              display: 'flex',
              justifyContent: 'left'
            }}
          >
            <Typography variant="h6" color="primary">50% Deduction without Qualifying Limit</Typography>
          </Box>
          <Divider sx={{ my: 0, width: '100%' }} />
          
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="50% Deduction - Amount"
              type="text"
              value={formatIndianNumber(taxationData.deductions.section_80g_50_wo_ql)}
              onChange={(e) => handleInputChange('deductions', 'section_80g_50_wo_ql', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('deductions', 'section_80g_50_wo_ql', e.target.value)}
            />
          </Grid>
          
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Donation Head</InputLabel>
              <Select
                value={taxationData.deductions.section_80g_50_head || 'Prime Minister\'s Drought Relief Fund'}
                label="Donation Head"
                onChange={(e) => handleInputChange('deductions', 'section_80g_50_head', e.target.value)}
              >
                {section80G50WoQlHeads.map((head) => (
                  <MenuItem key={head} value={head}>{head}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Box 
            sx={{ 
              width: '100%', 
              display: 'flex',
              justifyContent: 'left'
            }}
          >
            <Typography variant="h6" color="primary">100% Deduction with Qualifying Limit</Typography>
          </Box>
          <Divider sx={{ my: 0, width: '100%' }} />
          
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="100% Deduction (with limit) - Amount"
              type="text"
              value={formatIndianNumber(taxationData.deductions.section_80g_100_ql)}
              onChange={(e) => handleInputChange('deductions', 'section_80g_100_ql', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('deductions', 'section_80g_100_ql', e.target.value)}
            />
          </Grid>
          
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Donation Head</InputLabel>
              <Select
                value={taxationData.deductions.section_80g_100_ql_head || 'Donations to government or any approved local authority to promote family planning'}
                label="Donation Head"
                onChange={(e) => handleInputChange('deductions', 'section_80g_100_ql_head', e.target.value)}
              >
                {section80G100QlHeads.map((head) => (
                  <MenuItem key={head} value={head}>{head}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Box 
            sx={{ 
              width: '100%', 
              display: 'flex',
              justifyContent: 'left'
            }}
          >
            <Typography variant="h6" color="primary">50% Deduction with Qualifying Limit</Typography>
          </Box>
          <Divider sx={{ my: 0, width: '100%' }} />
          
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="50% Deduction (with limit) - Amount"
              type="text"
              value={formatIndianNumber(taxationData.deductions.section_80g_50_ql)}
              onChange={(e) => handleInputChange('deductions', 'section_80g_50_ql', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('deductions', 'section_80g_50_ql', e.target.value)}
            />
          </Grid>
          
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Donation Head</InputLabel>
              <Select
                value={taxationData.deductions.section_80g_50_ql_head || 'Donations to government or any approved local authority to except to promote family planning'}
                label="Donation Head"
                onChange={(e) => handleInputChange('deductions', 'section_80g_50_ql_head', e.target.value)}
              >
                {section80G50QlHeads.map((head) => (
                  <MenuItem key={head} value={head}>{head}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Box 
            sx={{ 
              width: '100%', 
              display: 'flex',
              justifyContent: 'left'
            }}
          >
            <Typography variant="h6" color="primary">100% Deduction to Political Donations</Typography>
          </Box>
          <Divider sx={{ my: 0, width: '100%' }} />
          
          {/* Section 80GGC - Political Donations */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Section 80GGC - Political Donations"
              type="text"
              value={formatIndianNumber(taxationData.deductions.section_80ggc)}
              onChange={(e) => handleInputChange('deductions', 'section_80ggc', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('deductions', 'section_80ggc', e.target.value)}
            />
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default DeductionsSection; 