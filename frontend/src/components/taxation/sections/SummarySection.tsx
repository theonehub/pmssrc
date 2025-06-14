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
import { TaxationData } from '../../../shared/types';

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
  // Helper function to safely format currency values
  const formatSafeCurrency = (value: number | undefined): string => {
    return formatCurrency(value || 0);
  };

  // Get city name for display
  const getCityName = (): string => {
    switch (taxationData.salary?.hra_city) {
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
                <Typography align="right">{formatSafeCurrency(taxationData.salary?.basic)}</Typography>
                
                <Typography>Dearness Allowance (DA):</Typography>
                <Typography align="right">{formatSafeCurrency(taxationData.salary?.dearness_allowance)}</Typography>
                
                <Typography>HRA ({getCityName()}):</Typography>
                <Typography align="right">{formatSafeCurrency(taxationData.salary?.hra)}</Typography>
                
                <Typography>Special Allowance:</Typography>
                <Typography align="right">{formatSafeCurrency(taxationData.salary?.special_allowance)}</Typography>
                
                <Typography>Bonus:</Typography>
                <Typography align="right">{formatSafeCurrency(taxationData.salary?.bonus)}</Typography>
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
                  {formatSafeCurrency(
                    (taxationData.other_sources?.interest_savings || 0) + 
                    (taxationData.other_sources?.interest_fd || 0) + 
                    (taxationData.other_sources?.interest_rd || 0) +
                    (taxationData.other_sources?.other_interest || 0)
                  )}
                </Typography>
                
                <Typography>Dividend Income:</Typography>
                <Typography align="right">{formatSafeCurrency(taxationData.other_sources?.dividend_income)}</Typography>
                
                <Typography>Gifts:</Typography>
                <Typography align="right">{formatSafeCurrency(taxationData.other_sources?.gifts)}</Typography>
                
                <Typography>Business & Professional Income:</Typography>
                <Typography align="right">{formatSafeCurrency(taxationData.other_sources?.business_professional_income)}</Typography>
                
                <Typography>Other Income:</Typography>
                <Typography align="right">{formatSafeCurrency(taxationData.other_sources?.other_income)}</Typography>
                
                <Typography>Leave Encashment Income:</Typography>
                <Typography align="right">
                  {formatSafeCurrency(taxationData.leave_encashment?.leave_encashment_income_received)}
                </Typography>
                
                <Typography>Short Term Capital Gains:</Typography>
                <Typography align="right">
                  {formatSafeCurrency(
                    (typeof taxationData.capital_gains === 'object' ? 
                      (taxationData.capital_gains?.stcg_111a || 0) + 
                      (taxationData.capital_gains?.stcg_any_other_asset || 0) +
                      (taxationData.capital_gains?.stcg_debt_mutual_fund || 0)
                      : 0)
                  )}
                </Typography>
                
                <Typography>Long Term Capital Gains:</Typography>
                <Typography align="right">
                  {formatSafeCurrency(
                    (typeof taxationData.capital_gains === 'object' ? 
                      (taxationData.capital_gains?.ltcg_112a || 0) + 
                      (taxationData.capital_gains?.ltcg_any_other_asset || 0) +
                      (taxationData.capital_gains?.ltcg_debt_mutual_fund || 0)
                      : 0)
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
                  <Typography align="right">{formatSafeCurrency(
                    (taxationData.deductions?.section_80c_lic || 0) +
                    (taxationData.deductions?.section_80c_epf || 0) +
                    (taxationData.deductions?.section_80c_ssp || 0) +
                    (taxationData.deductions?.section_80c_nsc || 0) +
                    (taxationData.deductions?.section_80c_ulip || 0) +
                    (taxationData.deductions?.section_80c_tsmf || 0) +
                    (taxationData.deductions?.section_80c_tffte2c || 0) +
                    (taxationData.deductions?.section_80c_paphl || 0) +
                    (taxationData.deductions?.section_80c_sdpphp || 0) +
                    (taxationData.deductions?.section_80c_tsfdsb || 0) +
                    (taxationData.deductions?.section_80c_scss || 0) +
                    (taxationData.deductions?.section_80c_others || 0)
                  )}</Typography>
                  
                  <Typography>Section 80CCC/CCD (NPS):</Typography>
                  <Typography align="right">{formatSafeCurrency(
                    (taxationData.deductions?.section_80ccc_ppic || 0) +
                    (taxationData.deductions?.section_80ccd_1_nps || 0) +
                    (taxationData.deductions?.section_80ccd_1b_additional || 0) +
                    (taxationData.deductions?.section_80ccd_2_enps || 0)
                  )}</Typography>
                  
                  <Typography>Section 80D (Health):</Typography>
                  <Typography align="right">{formatSafeCurrency(
                    (taxationData.deductions?.section_80d_hisf || 0) +
                    (taxationData.deductions?.section_80d_phcs || 0) +
                    (taxationData.deductions?.section_80d_hi_parent || 0)
                  )}</Typography>
                  
                  <Typography>Section 24B (Home Loan):</Typography>
                  <Typography align="right">{formatSafeCurrency((taxationData.deductions as any)?.section_24b)}</Typography>
                  
                  <Typography>Other Deductions:</Typography>
                  <Typography align="right">
                    {formatSafeCurrency(
                      (taxationData.deductions?.section_80dd || 0) +
                      (taxationData.deductions?.section_80ddb || 0) +
                      (taxationData.deductions?.section_80e_interest || 0) +
                      (taxationData.deductions?.section_80eeb || 0) +
                      (taxationData.deductions?.section_80g_100_wo_ql || 0) +
                      (taxationData.deductions?.section_80g_50_wo_ql || 0) +
                      (taxationData.deductions?.section_80ggc || 0) +
                      (taxationData.deductions?.section_80u || 0)
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
                    Estimated Tax: {formatSafeCurrency(calculatedTax)}
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