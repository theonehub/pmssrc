import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  CircularProgress,
  Divider
} from '@mui/material';
import { formatCurrency } from '../utils/taxationUtils';
import { TaxationData, ComprehensiveTaxCalculationResponse } from '../../../shared/types';

interface SummarySectionProps {
  taxationData: TaxationData;
  taxCalculationResponse: ComprehensiveTaxCalculationResponse | null;
  submitting: boolean;
  handleCalculateTax: () => void;
}

/**
 * Summary Section Component for reviewing and submitting tax declaration
 */
const SummarySection: React.FC<SummarySectionProps> = ({
  taxationData,
  taxCalculationResponse,
  submitting,
  handleCalculateTax
}) => {


  // Helper function to safely format currency values
  const formatSafeCurrency = (value: number | undefined): string => {
    return formatCurrency(value || 0);
  };

  // Helper function to safely parse and format currency from string
  const formatSafeCurrencyFromString = (value: string | undefined): string => {
    const numValue = parseFloat(value || '0');
    return formatCurrency(isNaN(numValue) ? 0 : numValue);
  };

  // Helper function to get tax liability from response (handles different API response formats)
  const getTaxLiability = (): string => {
    if (!taxCalculationResponse) return '0';
    
    // Try different possible fields for tax liability
    const possibleFields = [
      taxCalculationResponse.tax_liability?.amount,
      taxCalculationResponse.total_tax_liability?.amount,
      taxCalculationResponse.total_tax_liability,
      taxCalculationResponse.tax_breakdown?.tax_summary?.tax_liability,
      taxCalculationResponse.tax_after_rebate,
      taxCalculationResponse.tax_before_rebate
    ];
    
    for (const field of possibleFields) {
      if (field !== undefined && field !== null && field !== '' && field !== '0' && field !== 0) {
        return typeof field === 'string' ? field : field.toString();
      }
    }
    
    // Fallback: Calculate basic tax from taxable income if available
    if (taxCalculationResponse.taxable_income?.amount) {
      const taxableAmount = parseFloat(taxCalculationResponse.taxable_income.amount);
      if (taxableAmount > 0) {
        // Get regime from response or default to 'old'
        const regime = taxCalculationResponse.tax_breakdown?.tax_summary?.regime || 
                      taxCalculationResponse.regime_used || 
                      taxationData.regime || 'old';
        
        let tax = 0;
        
        if (regime === 'new') {
          // New tax regime rates (2023-24)
          if (taxableAmount > 1500000) {
            tax = 187500 + (taxableAmount - 1500000) * 0.3; // 30% above 15L
          } else if (taxableAmount > 1200000) {
            tax = 150000 + (taxableAmount - 1200000) * 0.25; // 25% between 12L-15L
          } else if (taxableAmount > 900000) {
            tax = 67500 + (taxableAmount - 900000) * 0.2; // 20% between 9L-12L
          } else if (taxableAmount > 600000) {
            tax = 30000 + (taxableAmount - 600000) * 0.15; // 15% between 6L-9L
          } else if (taxableAmount > 300000) {
            tax = 15000 + (taxableAmount - 300000) * 0.1; // 10% between 3L-6L
          } else if (taxableAmount > 250000) {
            tax = (taxableAmount - 250000) * 0.05; // 5% between 2.5L-3L
          }
        } else {
          // Old tax regime rates
          if (taxableAmount > 1000000) {
            tax = 112500 + (taxableAmount - 1000000) * 0.3; // 30% above 10L
          } else if (taxableAmount > 500000) {
            tax = 12500 + (taxableAmount - 500000) * 0.2; // 20% between 5L-10L
          } else if (taxableAmount > 250000) {
            tax = (taxableAmount - 250000) * 0.05; // 5% between 2.5L-5L
          }
        }
        
        // Add 4% cess
        tax = tax * 1.04;
        
        return Math.round(tax).toString();
      }
    }
    
    return '0';
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
                <Typography align="right">
                  {formatSafeCurrency(
                    taxCalculationResponse?.tax_breakdown?.income_breakdown?.salary_income?.basic_salary || 
                    taxationData.salary_income?.basic_salary
                  )}
                </Typography>
                
                <Typography>Dearness Allowance (DA):</Typography>
                <Typography align="right">
                  {formatSafeCurrency(
                    taxCalculationResponse?.tax_breakdown?.income_breakdown?.salary_income?.dearness_allowance || 
                    taxationData.salary_income?.dearness_allowance
                  )}
                </Typography>
                
                <Typography>HRA ({getCityName()}):</Typography>
                <Typography align="right">
                  {formatSafeCurrency(
                    taxCalculationResponse?.tax_breakdown?.income_breakdown?.salary_income?.hra_received || 
                    taxationData.salary_income?.hra_received
                  )}
                </Typography>
                
                <Typography>Special Allowance:</Typography>
                <Typography align="right">
                  {formatSafeCurrency(
                    taxCalculationResponse?.tax_breakdown?.income_breakdown?.salary_income?.special_allowance || 
                    taxationData.salary_income?.special_allowance
                  )}
                </Typography>
                
                <Typography>Conveyance Allowance:</Typography>
                <Typography align="right">
                  {formatSafeCurrency(
                    taxCalculationResponse?.tax_breakdown?.income_breakdown?.salary_income?.conveyance_allowance || 
                    taxationData.salary_income?.conveyance_allowance
                  )}
                </Typography>
                
                <Typography>Medical Allowance:</Typography>
                <Typography align="right">
                  {formatSafeCurrency(
                    taxCalculationResponse?.tax_breakdown?.income_breakdown?.salary_income?.medical_allowance || 
                    taxationData.salary_income?.medical_allowance
                  )}
                </Typography>
                
                <Typography>Bonus:</Typography>
                <Typography align="right">
                  {formatSafeCurrency(
                    taxCalculationResponse?.tax_breakdown?.income_breakdown?.salary_income?.bonus || 
                    taxationData.salary_income?.bonus
                  )}
                </Typography>
                
                <Typography>Commission:</Typography>
                <Typography align="right">
                  {formatSafeCurrency(
                    taxCalculationResponse?.tax_breakdown?.income_breakdown?.salary_income?.commission || 
                    taxationData.salary_income?.commission
                  )}
                </Typography>
                
                <Typography>Other Allowances:</Typography>
                <Typography align="right">
                  {formatSafeCurrency(
                    taxCalculationResponse?.tax_breakdown?.income_breakdown?.salary_income?.other_allowances || 
                    taxationData.salary_income?.other_allowances
                  )}
                </Typography>
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
                <Typography>Bank Interest:</Typography>
                <Typography align="right">
                  {formatSafeCurrency(
                    taxCalculationResponse?.tax_breakdown?.income_breakdown?.other_income?.bank_interest || 
                    taxationData.other_income?.interest_income?.savings_account_interest || 0
                  )}
                </Typography>
                
                <Typography>Fixed Deposit Interest:</Typography>
                <Typography align="right">
                  {formatSafeCurrency(
                    taxCalculationResponse?.tax_breakdown?.income_breakdown?.other_income?.fixed_deposit_interest || 
                    taxationData.other_income?.interest_income?.fixed_deposit_interest || 0
                  )}
                </Typography>
                
                <Typography>Other Interest:</Typography>
                <Typography align="right">
                  {formatSafeCurrency(
                    (taxCalculationResponse?.tax_breakdown?.income_breakdown?.other_income?.recurring_deposit_interest || 0) +
                    (taxCalculationResponse?.tax_breakdown?.income_breakdown?.other_income?.post_office_interest || 0) ||
                    ((taxationData.other_income?.interest_income?.recurring_deposit_interest || 0) +
                     (taxationData.other_income?.interest_income?.post_office_interest || 0))
                  )}
                </Typography>
                
                <Typography>Dividend Income:</Typography>
                <Typography align="right">
                  {formatSafeCurrency(
                    (taxCalculationResponse?.tax_breakdown?.income_breakdown?.other_income?.equity_dividend || 0) +
                    (taxCalculationResponse?.tax_breakdown?.income_breakdown?.other_income?.mutual_fund_dividend || 0) +
                    (taxCalculationResponse?.tax_breakdown?.income_breakdown?.other_income?.other_dividend || 0) ||
                    taxationData.other_income?.dividend_income || 0
                  )}
                </Typography>
                
                <Typography>Business & Professional Income:</Typography>
                <Typography align="right">
                  {formatSafeCurrency(
                    (taxCalculationResponse?.tax_breakdown?.income_breakdown?.other_income?.business_income || 0) +
                    (taxCalculationResponse?.tax_breakdown?.income_breakdown?.other_income?.professional_income || 0) ||
                    taxationData.other_income?.business_professional_income || 0
                  )}
                </Typography>
                
                <Typography>Leave Encashment Income:</Typography>
                <Typography align="right">
                  {formatSafeCurrency(
                    taxCalculationResponse?.tax_breakdown?.income_breakdown?.retirement_benefits?.leave_encashment_amount || 
                    taxationData.retirement_benefits?.leave_encashment?.leave_encashment_income_received || 0
                  )}
                </Typography>
                
                <Typography>Short Term Capital Gains:</Typography>
                <Typography align="right">
                  {formatSafeCurrency(
                    (taxCalculationResponse?.tax_breakdown?.income_breakdown?.capital_gains_income?.stcg_111a_equity_stt || 0) + 
                    (taxCalculationResponse?.tax_breakdown?.income_breakdown?.capital_gains_income?.stcg_other_assets || 0) +
                    (taxCalculationResponse?.tax_breakdown?.income_breakdown?.capital_gains_income?.stcg_debt_mf || 0) ||
                    ((taxationData.capital_gains_income?.stcg_111a_equity_stt || 0) + 
                     (taxationData.capital_gains_income?.stcg_other_assets || 0) +
                     (taxationData.capital_gains_income?.stcg_debt_mf || 0))
                  )}
                </Typography>
                
                <Typography>Long Term Capital Gains:</Typography>
                <Typography align="right">
                  {formatSafeCurrency(
                    (taxCalculationResponse?.tax_breakdown?.income_breakdown?.capital_gains_income?.ltcg_112a_equity_stt || 0) + 
                    (taxCalculationResponse?.tax_breakdown?.income_breakdown?.capital_gains_income?.ltcg_other_assets || 0) +
                    (taxCalculationResponse?.tax_breakdown?.income_breakdown?.capital_gains_income?.ltcg_debt_mf || 0) ||
                    ((taxationData.capital_gains_income?.ltcg_112a_equity_stt || 0) + 
                     (taxationData.capital_gains_income?.ltcg_other_assets || 0) +
                     (taxationData.capital_gains_income?.ltcg_debt_mf || 0))
                  )}
                </Typography>
                
                <Typography>Other Miscellaneous Income:</Typography>
                <Typography align="right">
                  {formatSafeCurrency(
                    (taxCalculationResponse?.tax_breakdown?.income_breakdown?.other_income?.lottery_winnings || 0) +
                    (taxCalculationResponse?.tax_breakdown?.income_breakdown?.other_income?.other_speculative_income || 0) ||
                    taxationData.other_income?.other_miscellaneous_income || 0
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
                  <Typography align="right">
                    {formatSafeCurrency(
                      taxCalculationResponse?.tax_breakdown?.deductions_breakdown?.section_80c ||
                      ((taxationData.deductions?.section_80c?.life_insurance_premium || 0) +
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
                       (taxationData.deductions?.section_80c?.others || 0))
                    )}
                  </Typography>
                  
                  <Typography>Section 80CCC/CCD (NPS):</Typography>
                  <Typography align="right">
                    {formatSafeCurrency(
                      (taxationData.deductions?.section_80ccc?.pension_plan_insurance_company || 0) +
                      (taxationData.deductions?.section_80ccd?.nps_contribution_10_percent || 0) +
                      (taxationData.deductions?.section_80ccd?.additional_nps_50k || 0) +
                      (taxationData.deductions?.section_80ccd?.employer_nps_contribution || 0)
                    )}
                  </Typography>
                  
                  <Typography>Section 80D (Health):</Typography>
                  <Typography align="right">
                    {formatSafeCurrency(
                      taxCalculationResponse?.tax_breakdown?.deductions_breakdown?.section_80d ||
                      ((taxationData.deductions?.section_80d?.self_family_premium || 0) +
                       (taxationData.deductions?.section_80d?.preventive_health_checkup_self || 0) +
                       (taxationData.deductions?.section_80d?.parent_premium || 0))
                    )}
                  </Typography>
                  
                  <Typography>Section 80E (Education Loan):</Typography>
                  <Typography align="right">
                    {formatSafeCurrency(
                      taxCalculationResponse?.tax_breakdown?.deductions_breakdown?.section_80e ||
                      (taxationData.deductions?.section_80e?.education_loan_interest || 0)
                    )}
                  </Typography>
                  
                  <Typography>Section 80G (Donations):</Typography>
                  <Typography align="right">
                    {formatSafeCurrency(
                      taxCalculationResponse?.tax_breakdown?.deductions_breakdown?.section_80g ||
                      ((taxationData.deductions?.section_80g?.donation_100_percent_without_limit || 0) +
                       (taxationData.deductions?.section_80g?.donation_50_percent_without_limit || 0) +
                       (taxationData.deductions?.section_80g?.donation_100_percent_with_limit || 0) +
                       (taxationData.deductions?.section_80g?.donation_50_percent_with_limit || 0))
                    )}
                  </Typography>
                  
                  <Typography>Other Deductions:</Typography>
                  <Typography align="right">
                    {formatSafeCurrency(
                      taxCalculationResponse?.tax_breakdown?.deductions_breakdown?.other_deductions ||
                      ((taxationData.deductions?.section_80dd?.amount || 0) +
                       (taxationData.deductions?.section_80ddb?.amount || 0) +
                       (taxationData.deductions?.section_80eeb?.amount || 0) +
                       (taxationData.deductions?.section_80ggc?.amount || 0) +
                       (taxationData.deductions?.section_80u?.amount || 0))
                    )}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          )}

          {/* Tax Calculation Summary */}
          <Card sx={{ mb: 2, bgcolor: '#f5f5f5' }} key={taxCalculationResponse ? 'with-response' : 'no-response'}>
            <CardContent>
              <Typography variant="h6" color="primary" gutterBottom>
                Tax Calculation Summary
              </Typography>
              
              {taxCalculationResponse ? (
                <Box>
                  <Box
                    sx={{
                      display: 'grid',
                      gridTemplateColumns: '2fr 1fr',
                      gap: 1,
                      alignItems: 'center',
                      mb: 2
                    }}
                  >
                    <Typography>Total Income:</Typography>
                    <Typography align="right" fontWeight="medium">
                      {formatSafeCurrencyFromString(taxCalculationResponse.total_income?.amount)}
                    </Typography>
                    
                    <Typography>Total Exemptions:</Typography>
                    <Typography align="right" color="success.main">
                      -{formatSafeCurrencyFromString(taxCalculationResponse.total_exemptions?.amount)}
                    </Typography>
                    
                    <Typography>Total Deductions:</Typography>
                    <Typography align="right" color="success.main">
                      -{formatSafeCurrencyFromString(taxCalculationResponse.total_deductions?.amount)}
                    </Typography>
                    
                    <Divider sx={{ gridColumn: '1 / -1', my: 1 }} />
                    
                    <Typography fontWeight="bold">Taxable Income:</Typography>
                    <Typography align="right" fontWeight="bold">
                      {formatSafeCurrencyFromString(taxCalculationResponse.taxable_income?.amount)}
                    </Typography>
                    
                    <Typography fontWeight="bold" color="error.main">Tax Liability:</Typography>
                    <Typography align="right" fontWeight="bold" color="error.main">
                      {formatSafeCurrencyFromString(getTaxLiability())}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ textAlign: 'center', mt: 2, p: 2, bgcolor: 'primary.light', borderRadius: 1 }}>
                    <Typography variant="h5" color="primary.contrastText">
                      Final Tax: {formatSafeCurrencyFromString(getTaxLiability())}
                    </Typography>
                    <Typography variant="body2" color="primary.contrastText">
                      Tax Regime: {taxCalculationResponse.tax_breakdown?.tax_summary?.regime?.toUpperCase() || 'N/A'}
                    </Typography>
                  </Box>
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

          {/* Exemptions Breakdown */}
          {taxCalculationResponse && (
            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h6" color="primary" gutterBottom>
                  Exemptions Breakdown
                </Typography>
                <Box
                  sx={{
                    display: 'grid',
                    gridTemplateColumns: '2fr 1fr',
                    gap: 1,
                    alignItems: 'center'
                  }}
                >
                  <Typography>HRA Exemption:</Typography>
                  <Typography align="right">
                    {formatSafeCurrency(taxCalculationResponse.tax_breakdown?.exemptions_breakdown?.hra_exemption || 0)}
                  </Typography>
                  
                  <Typography>Gratuity Exemption:</Typography>
                  <Typography align="right">
                    {formatSafeCurrency(taxCalculationResponse.tax_breakdown?.exemptions_breakdown?.gratuity_exemption || 0)}
                  </Typography>
                  
                  <Typography>Leave Encashment Exemption:</Typography>
                  <Typography align="right">
                    {formatSafeCurrency(taxCalculationResponse.tax_breakdown?.exemptions_breakdown?.leave_encashment_exemption || 0)}
                  </Typography>
                  
                  <Typography>Other Exemptions:</Typography>
                  <Typography align="right">
                    {formatSafeCurrency(taxCalculationResponse.tax_breakdown?.exemptions_breakdown?.other_exemptions || 0)}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default SummarySection; 