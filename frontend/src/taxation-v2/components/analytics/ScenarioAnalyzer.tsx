import React, { useState, useMemo } from 'react';
import {
  Box,
  Typography,
  Grid,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import {
  Analytics
} from '@mui/icons-material';

import { Card } from '../ui';
import { formatCurrency, formatPercentage } from '../../../shared/utils/formatting';
import { useTaxationStore } from '../../../shared/stores/taxationStore';

// =============================================================================
// INTERFACES & TYPES
// =============================================================================

interface ScenarioParameters {
  baseIncome: number;
  incomeGrowth: number;
  bonusAmount: number;
  section80c: number;
  section80d: number;
  npsContribution: number;
  elssInvestment: number;
  ppfContribution: number;
  regime: 'old' | 'new';
  ageGroup: '25-35' | '35-45' | '45-60' | '60+';
}

interface ScenarioResult {
  id: string;
  name: string;
  grossIncome: number;
  totalDeductions: number;
  taxableIncome: number;
  incomeTax: number;
  surcharge: number;
  cess: number;
  totalTax: number;
  netIncome: number;
  effectiveRate: number;
  savingsVsBase: number;
  color: string;
}

interface InvestmentImpact {
  investment: string;
  amount: number;
  taxSaving: number;
  effectiveReturn: number;
  postTaxReturn: number;
  recommendation: 'high' | 'medium' | 'low';
}

// =============================================================================
// TAX CALCULATION ENGINE
// =============================================================================

class AdvancedTaxCalculator {
  static calculateTax(scenario: ScenarioParameters): ScenarioResult {
    const { baseIncome, incomeGrowth, bonusAmount, section80c, section80d, npsContribution, regime } = scenario;
    
    const grossIncome = baseIncome * (1 + incomeGrowth / 100) + bonusAmount;
    const totalDeductions = regime === 'old' ? (section80c + section80d + npsContribution) : 0;
    const taxableIncome = Math.max(0, grossIncome - totalDeductions - 50000); // Standard deduction
    
    let incomeTax = 0;
    let surcharge = 0;
    
    if (regime === 'old') {
      // Old regime tax slabs
      if (taxableIncome > 250000) incomeTax += (Math.min(taxableIncome, 500000) - 250000) * 0.05;
      if (taxableIncome > 500000) incomeTax += (Math.min(taxableIncome, 1000000) - 500000) * 0.20;
      if (taxableIncome > 1000000) incomeTax += (taxableIncome - 1000000) * 0.30;
      
      // Surcharge for old regime
      if (grossIncome > 5000000) surcharge = incomeTax * 0.10;
      else if (grossIncome > 1000000) surcharge = incomeTax * 0.10;
    } else {
      // New regime tax slabs
      if (taxableIncome > 300000) incomeTax += (Math.min(taxableIncome, 600000) - 300000) * 0.05;
      if (taxableIncome > 600000) incomeTax += (Math.min(taxableIncome, 900000) - 600000) * 0.10;
      if (taxableIncome > 900000) incomeTax += (Math.min(taxableIncome, 1200000) - 900000) * 0.15;
      if (taxableIncome > 1200000) incomeTax += (Math.min(taxableIncome, 1500000) - 1200000) * 0.20;
      if (taxableIncome > 1500000) incomeTax += (taxableIncome - 1500000) * 0.30;
      
      // Surcharge for new regime
      if (grossIncome > 5000000) surcharge = incomeTax * 0.25;
      else if (grossIncome > 2000000) surcharge = incomeTax * 0.15;
      else if (grossIncome > 1000000) surcharge = incomeTax * 0.10;
    }
    
    const cess = (incomeTax + surcharge) * 0.04;
    const totalTax = incomeTax + surcharge + cess;
    const netIncome = grossIncome - totalTax;
    const effectiveRate = (totalTax / grossIncome) * 100;
    
    return {
      id: '',
      name: '',
      grossIncome,
      totalDeductions,
      taxableIncome,
      incomeTax,
      surcharge,
      cess,
      totalTax,
      netIncome,
      effectiveRate,
      savingsVsBase: 0,
      color: ''
    };
  }
  
  static analyzeInvestmentImpact(investments: any[]): InvestmentImpact[] {
    return investments.map(investment => {
      const taxSaving = investment.amount * 0.3; // Assuming 30% tax rate
      const postTaxReturn = (investment.returns / 100) * investment.amount + taxSaving;
      const effectiveReturnRate = (postTaxReturn / investment.amount) * 100;
      
      let recommendation: 'high' | 'medium' | 'low' = 'medium';
      if (effectiveReturnRate > 15) recommendation = 'high';
      else if (effectiveReturnRate < 8) recommendation = 'low';
      
      return {
        investment: investment.name,
        amount: investment.amount,
        taxSaving,
        effectiveReturn: effectiveReturnRate,
        postTaxReturn,
        recommendation
      };
    });
  }
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export const ScenarioAnalyzer: React.FC = () => {
  
  const [scenario, setScenario] = useState<ScenarioParameters>({
    baseIncome: 1200000,
    incomeGrowth: 10,
    bonusAmount: 100000,
    section80c: 150000,
    section80d: 25000,
    npsContribution: 50000,
    elssInvestment: 50000,
    ppfContribution: 100000,
    regime: 'new',
    ageGroup: '25-35'
  });
  
  const [selectedMetric, setSelectedMetric] = useState<'netIncome' | 'totalTax' | 'effectiveRate'>('netIncome');

  // Hooks
  const { formData } = useTaxationStore();

  // =============================================================================
  // CALCULATIONS
  // =============================================================================

  const currentIncome = useMemo(() => {
    const salaryIncome = formData.salary_income;
    if (!salaryIncome) return 0;
    
    return (
      (salaryIncome.basic_salary || 0) +
      (salaryIncome.hra || 0) +
      (salaryIncome.special_allowance || 0) +
      (salaryIncome.other_allowances || 0) +
      (salaryIncome.bonus || 0) +
      (salaryIncome.commission || 0) +
      (salaryIncome.overtime || 0)
    );
  }, [formData.salary_income]);

  const scenarios = useMemo(() => {
    const baseScenario = { ...scenario, baseIncome: currentIncome || scenario.baseIncome };
    
    const results: ScenarioResult[] = [
      {
        ...AdvancedTaxCalculator.calculateTax(baseScenario),
        id: 'current',
        name: 'Current Scenario',
        color: '#2196F3'
      },
      {
        ...AdvancedTaxCalculator.calculateTax({ ...baseScenario, regime: 'old' }),
        id: 'old-regime',
        name: 'Old Tax Regime',
        color: '#FF9800'
      },
      {
        ...AdvancedTaxCalculator.calculateTax({ 
          ...baseScenario, 
          incomeGrowth: scenario.incomeGrowth + 10 
        }),
        id: 'income-growth',
        name: `+${scenario.incomeGrowth + 10}% Income Growth`,
        color: '#4CAF50'
      },
      {
        ...AdvancedTaxCalculator.calculateTax({ 
          ...baseScenario, 
          section80c: 0,
          section80d: 0,
          npsContribution: 0 
        }),
        id: 'no-deductions',
        name: 'No Tax Deductions',
        color: '#F44336'
      },
      {
        ...AdvancedTaxCalculator.calculateTax({ 
          ...baseScenario, 
          section80c: 150000,
          section80d: 25000,
          npsContribution: 50000
        }),
        id: 'optimized',
        name: 'Optimized Deductions',
        color: '#9C27B0'
      }
    ];

    // Calculate savings vs base
    const baseResult = results[0];
    if (!baseResult) return results;
    
    return results.map(result => ({
      ...result,
      savingsVsBase: baseResult.totalTax - result.totalTax
    }));
  }, [scenario, currentIncome]);

  const investmentImpactAnalysis = useMemo(() => {
    const investments = [
      { name: 'ELSS Mutual Funds', amount: scenario.elssInvestment, returns: 12 },
      { name: 'PPF', amount: scenario.ppfContribution, returns: 7.1 },
      { name: 'NPS', amount: scenario.npsContribution, returns: 9 },
      { name: 'Health Insurance', amount: scenario.section80d, returns: 0 }, // Pure tax saving
    ];
    
    return AdvancedTaxCalculator.analyzeInvestmentImpact(investments);
  }, [scenario]);

  // =============================================================================
  // EVENT HANDLERS
  // =============================================================================

  const handleParameterChange = (parameter: keyof ScenarioParameters, value: any) => {
    setScenario(prev => ({ ...prev, [parameter]: value }));
  };

  // =============================================================================
  // RENDER HELPERS
  // =============================================================================

  const renderParameterControls = () => (
    <Card title="📊 Scenario Parameters" variant="outlined" sx={{ mb: 3 }}>
      <Grid container spacing={3}>
        {/* Income Parameters */}
        {/* @ts-ignore */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Typography variant="subtitle1" gutterBottom fontWeight="bold">
            Income Parameters
          </Typography>
          
          <Box sx={{ mb: 3 }}>
            <Typography variant="body2" gutterBottom>
              Base Income: {formatCurrency(scenario.baseIncome)}
            </Typography>
            <Slider
              value={scenario.baseIncome}
              onChange={(_, value) => handleParameterChange('baseIncome', value)}
              min={300000}
              max={5000000}
              step={50000}
              valueLabelDisplay="auto"
              valueLabelFormat={(value) => formatCurrency(value, { compact: true })}
            />
          </Box>
          
          <Box sx={{ mb: 3 }}>
            <Typography variant="body2" gutterBottom>
              Income Growth: {scenario.incomeGrowth}%
            </Typography>
            <Slider
              value={scenario.incomeGrowth}
              onChange={(_, value) => handleParameterChange('incomeGrowth', value)}
              min={0}
              max={50}
              step={5}
              valueLabelDisplay="auto"
              valueLabelFormat={(value) => `${value}%`}
            />
          </Box>
          
          <Box sx={{ mb: 3 }}>
            <Typography variant="body2" gutterBottom>
              Bonus Amount: {formatCurrency(scenario.bonusAmount)}
            </Typography>
            <Slider
              value={scenario.bonusAmount}
              onChange={(_, value) => handleParameterChange('bonusAmount', value)}
              min={0}
              max={500000}
              step={10000}
              valueLabelDisplay="auto"
              valueLabelFormat={(value) => formatCurrency(value, { compact: true })}
            />
          </Box>
        </Grid>

        {/* Tax & Investment Parameters */}
        {/* @ts-ignore */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Typography variant="subtitle1" gutterBottom fontWeight="bold">
            Tax & Investment Parameters
          </Typography>
          
          <Box sx={{ mb: 3 }}>
            <FormControl fullWidth size="small">
              <InputLabel>Tax Regime</InputLabel>
              <Select
                value={scenario.regime}
                label="Tax Regime"
                onChange={(e) => handleParameterChange('regime', e.target.value)}
              >
                <MenuItem value="new">New Tax Regime</MenuItem>
                <MenuItem value="old">Old Tax Regime</MenuItem>
              </Select>
            </FormControl>
          </Box>
          
          <Box sx={{ mb: 3 }}>
            <Typography variant="body2" gutterBottom>
              Section 80C: {formatCurrency(scenario.section80c)}
            </Typography>
            <Slider
              value={scenario.section80c}
              onChange={(_, value) => handleParameterChange('section80c', value)}
              min={0}
              max={150000}
              step={10000}
              valueLabelDisplay="auto"
              valueLabelFormat={(value) => formatCurrency(value, { compact: true })}
              disabled={scenario.regime === 'new'}
            />
          </Box>
          
          <Box sx={{ mb: 3 }}>
            <Typography variant="body2" gutterBottom>
              Section 80D: {formatCurrency(scenario.section80d)}
            </Typography>
            <Slider
              value={scenario.section80d}
              onChange={(_, value) => handleParameterChange('section80d', value)}
              min={0}
              max={75000}
              step={5000}
              valueLabelDisplay="auto"
              valueLabelFormat={(value) => formatCurrency(value, { compact: true })}
              disabled={scenario.regime === 'new'}
            />
          </Box>
          
          <Box sx={{ mb: 3 }}>
            <Typography variant="body2" gutterBottom>
              NPS Contribution: {formatCurrency(scenario.npsContribution)}
            </Typography>
            <Slider
              value={scenario.npsContribution}
              onChange={(_, value) => handleParameterChange('npsContribution', value)}
              min={0}
              max={50000}
              step={5000}
              valueLabelDisplay="auto"
              valueLabelFormat={(value) => formatCurrency(value, { compact: true })}
              disabled={scenario.regime === 'new'}
            />
          </Box>
        </Grid>
      </Grid>
    </Card>
  );

  const renderScenarioComparison = () => (
    <Card title="📈 Scenario Comparison" variant="outlined" sx={{ mb: 3 }}>
      <Box sx={{ mb: 2 }}>
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>Compare By</InputLabel>
          <Select
            value={selectedMetric}
            label="Compare By"
            onChange={(e) => setSelectedMetric(e.target.value as any)}
          >
            <MenuItem value="netIncome">Net Income</MenuItem>
            <MenuItem value="totalTax">Total Tax</MenuItem>
            <MenuItem value="effectiveRate">Effective Rate</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
        {scenarios.map((result) => (
          <Box key={result.id} sx={{ flex: '1 1 300px', minWidth: '250px' }}>
            <Card 
              variant={result.savingsVsBase > 0 ? 'success' : result.savingsVsBase < 0 ? 'error' : 'outlined'}
              sx={{ height: '100%' }}
            >
              <Box sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                  {result.name}
                </Typography>
                
                <Typography variant="h6" sx={{ color: result.color, mb: 1 }}>
                  {selectedMetric === 'netIncome' && formatCurrency(result.netIncome)}
                  {selectedMetric === 'totalTax' && formatCurrency(result.totalTax)}
                  {selectedMetric === 'effectiveRate' && formatPercentage(result.effectiveRate)}
                </Typography>
                
                <Typography variant="caption" color="text.secondary">
                  {selectedMetric === 'netIncome' && 'After Tax'}
                  {selectedMetric === 'totalTax' && 'Tax Liability'}
                  {selectedMetric === 'effectiveRate' && 'Tax Rate'}
                </Typography>
                
                {result.savingsVsBase !== 0 && (
                  <Typography 
                    variant="body2" 
                    color={result.savingsVsBase > 0 ? 'success.main' : 'error.main'}
                    fontWeight="bold"
                    sx={{ mt: 1 }}
                  >
                    {result.savingsVsBase > 0 ? 'Save ' : 'Pay '}
                    {formatCurrency(Math.abs(result.savingsVsBase))}
                  </Typography>
                )}
              </Box>
            </Card>
          </Box>
        ))}
      </Box>
    </Card>
  );

  const renderInvestmentImpact = () => (
    <Card title="💰 Investment Impact Analysis" variant="outlined">
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
        {investmentImpactAnalysis.map((analysis, index) => (
          <Box key={index} sx={{ flex: '1 1 250px', minWidth: '200px' }}>
            <Card 
              variant={
                analysis.recommendation === 'high' ? 'success' : 
                analysis.recommendation === 'low' ? 'error' : 'outlined'
              }
            >
              <Box sx={{ p: 2 }}>
                <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                  {analysis.investment}
                </Typography>
                
                <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1 }}>
                  <Box>
                    <Typography variant="caption">Investment</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {formatCurrency(analysis.amount)}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="caption">Tax Saving</Typography>
                    <Typography variant="body2" fontWeight="bold" color="success.main">
                      {formatCurrency(analysis.taxSaving)}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="caption">Effective Return</Typography>
                    <Typography variant="body2">
                      {formatPercentage(analysis.effectiveReturn)}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="caption">Recommendation</Typography>
                    <Typography 
                      variant="body2" 
                      color={
                        analysis.recommendation === 'high' ? 'success.main' : 
                        analysis.recommendation === 'low' ? 'error.main' : 'warning.main'
                      }
                      fontWeight="bold"
                    >
                      {analysis.recommendation.toUpperCase()}
                    </Typography>
                  </Box>
                </Box>
              </Box>
            </Card>
          </Box>
        ))}
      </Box>
    </Card>
  );

  // =============================================================================
  // MAIN RENDER
  // =============================================================================

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          <Analytics sx={{ mr: 2, verticalAlign: 'middle' }} />
          Scenario Analyzer
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Analyze different financial scenarios and their tax implications
        </Typography>
      </Box>

      {renderParameterControls()}
      {renderScenarioComparison()}
      {renderInvestmentImpact()}
    </Box>
  );
};

export default ScenarioAnalyzer; 