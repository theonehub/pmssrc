import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  CircularProgress
} from '@mui/material';
import { formatCurrency } from '../utils/taxationUtils';
import { TaxationData } from '../../../types';

interface SummarySectionProps {
  taxationData: TaxationData;
  calculatedTax: number | null;
  submitting: boolean;
  handleCalculateTax: () => void;
}

/**
 * Summary Section Component for reviewing and submitting tax declaration
 */
const SummarySection: React.FC<SummarySectionProps> = ({
  taxationData,
  calculatedTax,
  submitting,
  handleCalculateTax
}) => {
  // Get city name for display
  const getCityName = (): string => {
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

      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
          gap: 3,
          width: '100%'
        }}
      >
        {/* Left Column */}
        <Box>
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6" color="primary" gutterBottom>
                Salary Income
              </Typography>
              <Box
                sx={{
                  display: 'grid',
                  gridTemplateColumns: '2fr 1fr',
                  gap: 1,
                  alignItems: 'center'
                }}
              >
                <Typography>Basic Salary:</Typography>
                <Typography align="right">{formatCurrency(taxationData.salary.basic)}</Typography>
                
                <Typography>Dearness Allowance (DA):</Typography>
                <Typography align="right">{formatCurrency(taxationData.salary.dearness_allowance)}</Typography>
                
                <Typography>HRA ({getCityName()}):</Typography>
                <Typography align="right">{formatCurrency(taxationData.salary.hra)}</Typography>
                
                <Typography>Special Allowance:</Typography>
                <Typography align="right">{formatCurrency(taxationData.salary.special_allowance)}</Typography>
                
                <Typography>Bonus:</Typography>
                <Typography align="right">{formatCurrency(taxationData.salary.bonus)}</Typography>
              </Box>
            </CardContent>
          </Card>

          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6" color="primary" gutterBottom>
                Other Income
              </Typography>
              <Box
                sx={{
                  display: 'grid',
                  gridTemplateColumns: '2fr 1fr',
                  gap: 1,
                  alignItems: 'center'
                }}
              >
                <Typography>Interest (All Sources):</Typography>
                <Typography align="right">
                  {formatCurrency(
                    taxationData.other_sources.interest_savings + 
                    taxationData.other_sources.interest_fd + 
                    taxationData.other_sources.interest_rd +
                    taxationData.other_sources.other_interest
                  )}
                </Typography>
                
                <Typography>Dividend Income:</Typography>
                <Typography align="right">{formatCurrency(taxationData.other_sources.dividend_income)}</Typography>
                
                <Typography>Gifts:</Typography>
                <Typography align="right">{formatCurrency(taxationData.other_sources.gifts)}</Typography>
                
                <Typography>Business & Professional Income:</Typography>
                <Typography align="right">{formatCurrency(taxationData.other_sources.business_professional_income)}</Typography>
                
                <Typography>Other Income:</Typography>
                <Typography align="right">{formatCurrency(taxationData.other_sources.other_income)}</Typography>
                
                <Typography>Leave Encashment Income:</Typography>
                <Typography align="right">
                  {formatCurrency(
                    taxationData.leave_encashment?.leave_encashment_income_received || 0
                  )}
                </Typography>
                
                <Typography>Short Term Capital Gains:</Typography>
                <Typography align="right">
                  {formatCurrency(
                    taxationData.capital_gains.stcg_111a + 
                    taxationData.capital_gains.stcg_any_other_asset +
                    taxationData.capital_gains.stcg_debt_mutual_fund
                  )}
                </Typography>
                
                <Typography>Long Term Capital Gains:</Typography>
                <Typography align="right">
                  {formatCurrency(
                    taxationData.capital_gains.ltcg_112a + 
                    taxationData.capital_gains.ltcg_any_other_asset +
                    taxationData.capital_gains.ltcg_debt_mutual_fund
                  )}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Box>

        {/* Right Column */}
        <Box>
          {taxationData.regime === 'old' && (
            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h6" color="primary" gutterBottom>
                  Deductions
                </Typography>
                <Box
                  sx={{
                    display: 'grid',
                    gridTemplateColumns: '2fr 1fr',
                    gap: 1,
                    alignItems: 'center'
                  }}
                >
                  <Typography>Section 80C (Total):</Typography>
                  <Typography align="right">{formatCurrency(
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
                  )}</Typography>
                  
                  <Typography>Section 80CCC/CCD (NPS):</Typography>
                  <Typography align="right">{formatCurrency(
                    taxationData.deductions.section_80ccc_ppic +
                    taxationData.deductions.section_80ccd_1_nps +
                    taxationData.deductions.section_80ccd_1b_additional +
                    taxationData.deductions.section_80ccd_2_enps
                  )}</Typography>
                  
                  <Typography>Section 80D (Health):</Typography>
                  <Typography align="right">{formatCurrency(
                    taxationData.deductions.section_80d_hisf +
                    taxationData.deductions.section_80d_phcs +
                    taxationData.deductions.section_80d_hi_parent
                  )}</Typography>
                  
                  <Typography>Section 24B (Home Loan):</Typography>
                  <Typography align="right">{formatCurrency((taxationData.deductions as any).section_24b || 0)}</Typography>
                  
                  <Typography>Other Deductions:</Typography>
                  <Typography align="right">
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
                  </Typography>
                </Box>
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
        </Box>
      </Box>
    </Box>
  );
};

export default SummarySection; 