import React from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  CircularProgress
} from '@mui/material';
import { formatCurrency } from '../utils/taxationUtils';

/**
 * Summary Section Component for reviewing and submitting tax declaration
 * @param {Object} props - Component props
 * @param {Object} props.taxationData - Taxation data state
 * @param {number|null} props.calculatedTax - Calculated tax amount
 * @param {boolean} props.submitting - Submitting flag
 * @param {Function} props.handleCalculateTax - Function to handle tax calculation
 * @returns {JSX.Element} Summary section component
 */
const SummarySection = ({
  taxationData,
  calculatedTax,
  submitting,
  handleCalculateTax
}) => {
  // Get city name for display
  const getCityName = () => {
    switch (taxationData.salary.hra_city) {
      case 'Metro':
        return 'Metro (Delhi, Mumbai, Kolkata, Chennai)';
      case 'Non-Metro':
        return 'Non-Metro (Tier 1 cities)';
      default:
        return 'Others (Tier 2 & 3 cities)';
    }
  };

  return (
    <Box sx={{ py: 2 }}>
      <Typography variant="h6" gutterBottom>
        Review Tax Declaration
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Please review your tax declaration details before submitting. You can go back to any section to make changes.
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6" color="primary" gutterBottom>
                Salary Income
              </Typography>
              <Grid container spacing={1}>
                <Grid item xs={8}><Typography>Basic Salary:</Typography></Grid>
                <Grid item xs={4}><Typography align="right">{formatCurrency(taxationData.salary.basic)}</Typography></Grid>
                
                <Grid item xs={8}><Typography>Dearness Allowance (DA):</Typography></Grid>
                <Grid item xs={4}><Typography align="right">{formatCurrency(taxationData.salary.dearness_allowance)}</Typography></Grid>
                
                <Grid item xs={8}><Typography>HRA ({getCityName()}):</Typography></Grid>
                <Grid item xs={4}><Typography align="right">{formatCurrency(taxationData.salary.hra)}</Typography></Grid>
                
                <Grid item xs={8}><Typography>Special Allowance:</Typography></Grid>
                <Grid item xs={4}><Typography align="right">{formatCurrency(taxationData.salary.special_allowance)}</Typography></Grid>
                
                <Grid item xs={8}><Typography>Bonus:</Typography></Grid>
                <Grid item xs={4}><Typography align="right">{formatCurrency(taxationData.salary.bonus)}</Typography></Grid>
              </Grid>
            </CardContent>
          </Card>

          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6" color="primary" gutterBottom>
                Other Income
              </Typography>
              <Grid container spacing={1}>
                <Grid item xs={8}><Typography>Interest (All Sources):</Typography></Grid>
                <Grid item xs={4}><Typography align="right">
                  {formatCurrency(
                    taxationData.other_sources.interest_savings + 
                    taxationData.other_sources.interest_fd + 
                    taxationData.other_sources.interest_rd +
                    taxationData.other_sources.other_interest
                  )}
                </Typography></Grid>
                
                <Grid item xs={8}><Typography>Dividend Income:</Typography></Grid>
                <Grid item xs={4}><Typography align="right">{formatCurrency(taxationData.other_sources.dividend_income)}</Typography></Grid>
                
                <Grid item xs={8}><Typography>Gifts:</Typography></Grid>
                <Grid item xs={4}><Typography align="right">{formatCurrency(taxationData.other_sources.gifts)}</Typography></Grid>
                
                <Grid item xs={8}><Typography>Business & Professional Income:</Typography></Grid>
                <Grid item xs={4}><Typography align="right">{formatCurrency(taxationData.other_sources.business_professional_income)}</Typography></Grid>
                
                <Grid item xs={8}><Typography>Other Income:</Typography></Grid>
                <Grid item xs={4}><Typography align="right">{formatCurrency(taxationData.other_sources.other_income)}</Typography></Grid>
                
                <Grid item xs={8}><Typography>Leave Encashment Income:</Typography></Grid>
                <Grid item xs={4}><Typography align="right">
                  {formatCurrency(
                    taxationData.leave_encashment.leave_encashment_income_received
                  )}
                </Typography></Grid>
                
                <Grid item xs={8}><Typography>Short Term Capital Gains:</Typography></Grid>
                <Grid item xs={4}><Typography align="right">
                  {formatCurrency(
                    taxationData.capital_gains.stcg_111a + 
                    taxationData.capital_gains.stcg_any_other_asset +
                    taxationData.capital_gains.stcg_debt_mutual_fund
                  )}
                </Typography></Grid>
                
                <Grid item xs={8}><Typography>Long Term Capital Gains:</Typography></Grid>
                <Grid item xs={4}><Typography align="right">
                  {formatCurrency(
                    taxationData.capital_gains.ltcg_112a + 
                    taxationData.capital_gains.ltcg_any_other_asset +
                    taxationData.capital_gains.ltcg_debt_mutual_fund
                  )}
                </Typography></Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          {taxationData.regime === 'old' && (
            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h6" color="primary" gutterBottom>
                  Deductions
                </Typography>
                <Grid container spacing={1}>
                  <Grid item xs={8}><Typography>Section 80C (Total):</Typography></Grid>
                  <Grid item xs={4}><Typography align="right">{formatCurrency(
                    taxationData.deductions.section_80c_lic +
                    taxationData.deductions.section_80c_epf +
                    taxationData.deductions.section_80c_ssp +
                    taxationData.deductions.section_80c_nsc +
                    taxationData.deductions.section_80c_ulip +
                    taxationData.deductions.section_80c_tsmf +
                    taxationData.deductions.section_80c_tffte2c +
                    taxationData.deductions.section_80c_paphl +
                    taxationData.deductions.section_80c_sdpphp +
                    taxationData.deductions.section_80c_tsfdsb +
                    taxationData.deductions.section_80c_scss +
                    taxationData.deductions.section_80c_others
                  )}</Typography></Grid>
                  
                  <Grid item xs={8}><Typography>Section 80CCC/CCD (NPS):</Typography></Grid>
                  <Grid item xs={4}><Typography align="right">{formatCurrency(
                    taxationData.deductions.section_80ccc_ppic +
                    taxationData.deductions.section_80ccd_1_nps +
                    taxationData.deductions.section_80ccd_1b_additional +
                    taxationData.deductions.section_80ccd_2_enps
                  )}</Typography></Grid>
                  
                  <Grid item xs={8}><Typography>Section 80D (Health):</Typography></Grid>
                  <Grid item xs={4}><Typography align="right">{formatCurrency(
                    taxationData.deductions.section_80d_hisf +
                    taxationData.deductions.section_80d_phcs +
                    taxationData.deductions.section_80d_hi_parent
                  )}</Typography></Grid>
                  
                  <Grid item xs={8}><Typography>Section 24B (Home Loan):</Typography></Grid>
                  <Grid item xs={4}><Typography align="right">{formatCurrency(taxationData.deductions.section_24b)}</Typography></Grid>
                  
                  <Grid item xs={8}><Typography>Other Deductions:</Typography></Grid>
                  <Grid item xs={4}><Typography align="right">
                    {formatCurrency(
                      taxationData.deductions.section_80dd +
                      taxationData.deductions.section_80ddb +
                      taxationData.deductions.section_80e_interest +
                      taxationData.deductions.section_80eeb +
                      taxationData.deductions.section_80g_100_wo_ql +
                      taxationData.deductions.section_80g_50_wo_ql +
                      taxationData.deductions.section_80ggc +
                      taxationData.deductions.section_80u
                    )}
                  </Typography></Grid>
                </Grid>
              </CardContent>
            </Card>
          )}

          <Card sx={{ mb: 2, bgcolor: '#f5f5f5' }}>
            <CardContent>
              <Typography variant="h6" color="primary" gutterBottom>
                Tax Calculation
              </Typography>
              
              {calculatedTax !== null ? (
                <Box>
                  <Typography variant="h5" align="center" sx={{ my: 2 }}>
                    Estimated Tax: {formatCurrency(calculatedTax)}
                  </Typography>
                </Box>
              ) : (
                <Box sx={{ textAlign: 'center', my: 2 }}>
                  <Button 
                    variant="contained" 
                    color="secondary"
                    onClick={handleCalculateTax}
                    disabled={submitting}
                  >
                    {submitting ? <CircularProgress size={24} /> : 'Calculate Tax'}
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default SummarySection; 