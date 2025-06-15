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
    switch (taxationData.salary_income?.hra_city_type) {
      case 'metro':
        return 'Metro (Delhi, Mumbai, Kolkata, Chennai)';
      case 'non_metro':
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
                <Typography align="right">{formatSafeCurrency(taxationData.salary_income?.basic_salary)}</Typography>
                
                <Typography>Dearness Allowance (DA):</Typography>
                <Typography align="right">{formatSafeCurrency(taxationData.salary_income?.dearness_allowance)}</Typography>
                
                <Typography>HRA ({getCityName()}):</Typography>
                <Typography align="right">{formatSafeCurrency(taxationData.salary_income?.hra_received)}</Typography>
                
                <Typography>Special Allowance:</Typography>
                <Typography align="right">{formatSafeCurrency(taxationData.salary_income?.special_allowance)}</Typography>
                
                <Typography>Bonus:</Typography>
                <Typography align="right">{formatSafeCurrency(taxationData.salary_income?.other_allowances)}</Typography>
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
                    (taxationData.other_income?.interest_income?.savings_account_interest || 0) + 
                    (taxationData.other_income?.interest_income?.fixed_deposit_interest || 0) + 
                    (taxationData.other_income?.interest_income?.recurring_deposit_interest || 0) +
                    (taxationData.other_income?.interest_income?.other_interest || 0)
                  )}
                </Typography>
                
                <Typography>Dividend Income:</Typography>
                <Typography align="right">{formatSafeCurrency(taxationData.other_income?.dividend_income)}</Typography>
                
                <Typography>Gifts:</Typography>
                <Typography align="right">{formatSafeCurrency(taxationData.other_income?.gifts_received)}</Typography>
                
                <Typography>Business & Professional Income:</Typography>
                <Typography align="right">{formatSafeCurrency(taxationData.other_income?.business_professional_income)}</Typography>
                
                <Typography>Other Income:</Typography>
                <Typography align="right">{formatSafeCurrency(taxationData.other_income?.other_miscellaneous_income)}</Typography>
                
                <Typography>Leave Encashment Income:</Typography>
                <Typography align="right">
                  {formatSafeCurrency(taxationData.retirement_benefits?.leave_encashment?.leave_encashment_income_received)}
                </Typography>
                
                <Typography>Short Term Capital Gains:</Typography>
                <Typography align="right">
                  {formatSafeCurrency(
                    (taxationData.capital_gains_income?.stcg_111a_equity_stt || 0) + 
                    (taxationData.capital_gains_income?.stcg_other_assets || 0) +
                    (taxationData.capital_gains_income?.stcg_debt_mutual_fund || 0)
                  )}
                </Typography>
                
                <Typography>Long Term Capital Gains:</Typography>
                <Typography align="right">
                  {formatSafeCurrency(
                    (taxationData.capital_gains_income?.ltcg_112a_equity_stt || 0) + 
                    (taxationData.capital_gains_income?.ltcg_other_assets || 0) +
                    (taxationData.capital_gains_income?.ltcg_debt_mf || 0)
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
                    (taxationData.deductions?.section_80c?.life_insurance_premium || 0) +
                    (taxationData.deductions?.section_80c?.epf_contribution || 0) +
                    (taxationData.deductions?.section_80c?.ssp_contribution || 0) +
                    (taxationData.deductions?.section_80c?.nsc_investment || 0) +
                    (taxationData.deductions?.section_80c?.ulip_investment || 0) +
                    (taxationData.deductions?.section_80c?.tax_saver_mutual_fund || 0) +
                    (taxationData.deductions?.section_80c?.tuition_fees_for_two_children || 0) +
                    (taxationData.deductions?.section_80c?.principal_amount_paid_home_loan || 0) +
                    (taxationData.deductions?.section_80c?.sukanya_deposit_plan_for_girl_child || 0) +
                    (taxationData.deductions?.section_80c?.tax_saver_fixed_deposit_5_years_bank || 0) +
                    (taxationData.deductions?.section_80c?.senior_citizen_savings_scheme || 0) +
                    (taxationData.deductions?.section_80c?.others || 0)
                  )}</Typography>
                  
                  <Typography>Section 80CCC/CCD (NPS):</Typography>
                  <Typography align="right">{formatSafeCurrency(
                    (taxationData.deductions?.section_80ccc?.pension_plan_insurance_company || 0) +
                    (taxationData.deductions?.section_80ccd?.nps_contribution_10_percent || 0) +
                    (taxationData.deductions?.section_80ccd?.additional_nps_50k || 0) +
                    (taxationData.deductions?.section_80ccd?.employer_nps_contribution || 0)
                  )}</Typography>
                  
                  <Typography>Section 80D (Health):</Typography>
                  <Typography align="right">{formatSafeCurrency(
                    (taxationData.deductions?.section_80d?.self_family_premium || 0) +
                    (taxationData.deductions?.section_80d?.preventive_health_checkup_self || 0) +
                    (taxationData.deductions?.section_80d?.parent_premium || 0)
                  )}</Typography>
                  
                  <Typography>Section 24B (Home Loan):</Typography>
                  <Typography align="right">{formatSafeCurrency((taxationData.deductions as any)?.section_24b)}</Typography>
                  
                  <Typography>Other Deductions:</Typography>
                  <Typography align="right">
                    {formatSafeCurrency(
                      (taxationData.deductions?.section_80dd?.amount || 0) +
                      (taxationData.deductions?.section_80ddb?.amount || 0) +
                      (taxationData.deductions?.section_80e?.education_loan_interest || 0) +
                      (taxationData.deductions?.section_80eeb?.amount || 0) +
                      (taxationData.deductions?.section_80g?.donation_100_percent_without_limit || 0) +
                      (taxationData.deductions?.section_80g?.donation_50_percent_without_limit || 0) +
                      (taxationData.deductions?.section_80g?.donation_100_percent_with_limit || 0) +
                      (taxationData.deductions?.section_80g?.donation_50_percent_with_limit || 0) +
                      (taxationData.deductions?.section_80ggc?.amount || 0) +
                      (taxationData.deductions?.section_80u?.amount || 0)
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