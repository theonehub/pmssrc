import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  LinearProgress
} from '@mui/material';
import {
  ExpandMore,
  Psychology,
  AccountBalance,
  Lightbulb,
  Calculate,
  Star
} from '@mui/icons-material';

import { Card, Button } from '../ui';
import { formatCurrency, formatPercentage } from '../../../shared/utils/formatting';
import { useTaxationStore } from '../../../shared/stores/taxationStore';

// =============================================================================
// INTERFACES & TYPES
// =============================================================================

interface OptimizationScenario {
  id: string;
  name: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  effort: 'easy' | 'moderate' | 'complex';
  taxSaving: number;
  currentValue: number;
  optimizedValue: number;
  category: 'deductions' | 'investments' | 'timing' | 'structure';
  priority: number;
}

interface InvestmentRecommendation {
  id: string;
  instrument: string;
  category: string;
  investmentAmount: number;
  taxBenefit: number;
  expectedReturns: number;
  riskLevel: 'low' | 'medium' | 'high';
  lockInPeriod: string;
  section: string;
  description: string;
}

interface ScenarioAnalysis {
  scenario: string;
  grossIncome: number;
  totalTax: number;
  netIncome: number;
  effectiveRate: number;
  savingsVsBase: number;
}

interface TaxOptimizationEngineProps {
  onApplyRecommendation?: (recommendation: OptimizationScenario) => void;
  onInvestmentSelect?: (investment: InvestmentRecommendation) => void;
}

// =============================================================================
// OPTIMIZATION ALGORITHMS
// =============================================================================

class TaxOptimizationAlgorithms {
  static analyzeCurrentTaxStructure(income: number, deductions: any, regime: string) {
    const inefficiencies: OptimizationScenario[] = [];
    let priority = 1;

    // Section 80C Analysis
    if (deductions.section_80c < 150000) {
      const potentialSaving = Math.min(150000 - deductions.section_80c, income * 0.1);
      const taxSaving = potentialSaving * (regime === 'old' ? 0.3 : 0.2);
      
      inefficiencies.push({
        id: '80c-optimization',
        name: 'Maximize Section 80C Deductions',
        description: `You can save up to ${formatCurrency(taxSaving)} by maximizing your Section 80C investments`,
        impact: taxSaving > 30000 ? 'high' : taxSaving > 15000 ? 'medium' : 'low',
        effort: 'easy',
        taxSaving,
        currentValue: deductions.section_80c,
        optimizedValue: Math.min(150000, deductions.section_80c + potentialSaving),
        category: 'deductions',
        priority: priority++
      });
    }

    // Section 80D Analysis
    if (deductions.section_80d < 25000) {
      const potentialSaving = 25000 - deductions.section_80d;
      const taxSaving = potentialSaving * (regime === 'old' ? 0.3 : 0.2);
      
      inefficiencies.push({
        id: '80d-optimization',
        name: 'Health Insurance Tax Benefits',
        description: `Invest in health insurance to save ${formatCurrency(taxSaving)} annually`,
        impact: 'medium',
        effort: 'easy',
        taxSaving,
        currentValue: deductions.section_80d,
        optimizedValue: 25000,
        category: 'deductions',
        priority: priority++
      });
    }

    // NPS Analysis
    if (income > 500000) {
      const npsInvestment = Math.min(50000, income * 0.1);
      const taxSaving = npsInvestment * (regime === 'old' ? 0.3 : 0.2);
      
      inefficiencies.push({
        id: 'nps-optimization',
        name: 'National Pension System (80CCD1B)',
        description: `Additional ${formatCurrency(taxSaving)} tax saving through NPS investment`,
        impact: 'high',
        effort: 'moderate',
        taxSaving,
        currentValue: 0,
        optimizedValue: npsInvestment,
        category: 'investments',
        priority: priority++
      });
    }

    // Tax Regime Analysis
    const oldRegimeTax = this.calculateOldRegimeTax(income, deductions);
    const newRegimeTax = this.calculateNewRegimeTax(income);
    
    if (regime === 'old' && newRegimeTax < oldRegimeTax) {
      inefficiencies.push({
        id: 'regime-switch',
        name: 'Consider New Tax Regime',
        description: `Switching to new tax regime could save ${formatCurrency(oldRegimeTax - newRegimeTax)}`,
        impact: 'high',
        effort: 'easy',
        taxSaving: oldRegimeTax - newRegimeTax,
        currentValue: oldRegimeTax,
        optimizedValue: newRegimeTax,
        category: 'structure',
        priority: priority++
      });
    }

    return inefficiencies.sort((a, b) => b.taxSaving - a.taxSaving);
  }

  static generateInvestmentRecommendations(income: number, currentDeductions: any): InvestmentRecommendation[] {
    const recommendations: InvestmentRecommendation[] = [];
    const remainingLimit = 150000 - currentDeductions.section_80c;

    if (remainingLimit > 0) {
      // ELSS Funds
      if (remainingLimit >= 50000) {
        recommendations.push({
          id: 'elss-recommendation',
          instrument: 'ELSS Mutual Funds',
          category: 'Equity',
          investmentAmount: Math.min(50000, remainingLimit),
          taxBenefit: Math.min(50000, remainingLimit) * 0.3,
          expectedReturns: 12,
          riskLevel: 'medium',
          lockInPeriod: '3 years',
          section: '80C',
          description: 'Tax-saving equity funds with growth potential'
        });
      }

      // PPF
      recommendations.push({
        id: 'ppf-recommendation',
        instrument: 'Public Provident Fund',
        category: 'Debt',
        investmentAmount: Math.min(150000, remainingLimit),
        taxBenefit: Math.min(150000, remainingLimit) * 0.3,
        expectedReturns: 7.1,
        riskLevel: 'low',
        lockInPeriod: '15 years',
        section: '80C',
        description: 'Government-backed long-term savings with tax benefits'
      });

      // ULIP
      if (remainingLimit >= 25000) {
        recommendations.push({
          id: 'ulip-recommendation',
          instrument: 'Unit Linked Insurance Plan',
          category: 'Insurance + Investment',
          investmentAmount: Math.min(25000, remainingLimit),
          taxBenefit: Math.min(25000, remainingLimit) * 0.3,
          expectedReturns: 8,
          riskLevel: 'medium',
          lockInPeriod: '5 years',
          section: '80C',
          description: 'Insurance with investment component'
        });
      }
    }

    // NPS Recommendation
    if (income > 500000) {
      recommendations.push({
        id: 'nps-80ccd1b',
        instrument: 'National Pension System',
        category: 'Retirement',
        investmentAmount: 50000,
        taxBenefit: 50000 * 0.3,
        expectedReturns: 9,
        riskLevel: 'medium',
        lockInPeriod: 'Till retirement',
        section: '80CCD(1B)',
        description: 'Additional tax benefit over 80C limit'
      });
    }

    return recommendations.sort((a, b) => b.taxBenefit - a.taxBenefit);
  }

  static calculateScenarioAnalysis(baseIncome: number): ScenarioAnalysis[] {
    const scenarios = [
      { name: 'Current', income: baseIncome },
      { name: 'With Raise (+20%)', income: baseIncome * 1.2 },
      { name: 'With Bonus (+10%)', income: baseIncome * 1.1 },
      { name: 'Optimized Deductions', income: baseIncome, optimizedDeductions: true }
    ];

    return scenarios.map(scenario => {
      const grossIncome = scenario.income;
      const deductions = scenario.optimizedDeductions ? 200000 : 50000;
      const taxableIncome = Math.max(0, grossIncome - deductions - 50000); // Standard deduction
      
      // Simplified tax calculation for new regime
      let totalTax = 0;
      if (taxableIncome > 300000) totalTax += (Math.min(taxableIncome, 600000) - 300000) * 0.05;
      if (taxableIncome > 600000) totalTax += (Math.min(taxableIncome, 900000) - 600000) * 0.10;
      if (taxableIncome > 900000) totalTax += (Math.min(taxableIncome, 1200000) - 900000) * 0.15;
      if (taxableIncome > 1200000) totalTax += (Math.min(taxableIncome, 1500000) - 1200000) * 0.20;
      if (taxableIncome > 1500000) totalTax += (taxableIncome - 1500000) * 0.30;

      // Add cess
      totalTax *= 1.04;

      const netIncome = grossIncome - totalTax;
      const effectiveRate = (totalTax / grossIncome) * 100;
      const baseTax = this.calculateBaseTax(baseIncome);
      const savingsVsBase = baseTax - totalTax;

      return {
        scenario: scenario.name,
        grossIncome,
        totalTax,
        netIncome,
        effectiveRate,
        savingsVsBase
      };
    });
  }

  private static calculateOldRegimeTax(income: number, deductions: any): number {
    const taxableIncome = Math.max(0, income - deductions.total - 50000);
    let tax = 0;
    
    if (taxableIncome > 250000) tax += (Math.min(taxableIncome, 500000) - 250000) * 0.05;
    if (taxableIncome > 500000) tax += (Math.min(taxableIncome, 1000000) - 500000) * 0.20;
    if (taxableIncome > 1000000) tax += (taxableIncome - 1000000) * 0.30;
    
    return tax * 1.04; // Add cess
  }

  private static calculateNewRegimeTax(income: number): number {
    const taxableIncome = Math.max(0, income - 50000);
    let tax = 0;
    
    if (taxableIncome > 300000) tax += (Math.min(taxableIncome, 600000) - 300000) * 0.05;
    if (taxableIncome > 600000) tax += (Math.min(taxableIncome, 900000) - 600000) * 0.10;
    if (taxableIncome > 900000) tax += (Math.min(taxableIncome, 1200000) - 900000) * 0.15;
    if (taxableIncome > 1200000) tax += (Math.min(taxableIncome, 1500000) - 1200000) * 0.20;
    if (taxableIncome > 1500000) tax += (taxableIncome - 1500000) * 0.30;
    
    return tax * 1.04; // Add cess
  }

  private static calculateBaseTax(income: number): number {
    return this.calculateNewRegimeTax(income);
  }
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export const TaxOptimizationEngine: React.FC<TaxOptimizationEngineProps> = ({
  onApplyRecommendation,
  onInvestmentSelect
}) => {
  const [analysisStep, setAnalysisStep] = useState(0);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [optimizations, setOptimizations] = useState<OptimizationScenario[]>([]);
  const [investmentRecommendations, setInvestmentRecommendations] = useState<InvestmentRecommendation[]>([]);
  const [scenarioAnalysis, setScenarioAnalysis] = useState<ScenarioAnalysis[]>([]);
  const [selectedRiskLevel, setSelectedRiskLevel] = useState<'low' | 'medium' | 'high'>('medium');

  // Hooks
  const { formData } = useTaxationStore();

  // =============================================================================
  // CALCULATIONS
  // =============================================================================

  const totalIncome = useMemo(() => {
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

  const currentDeductions = useMemo(() => {
    return formData.deductions || {
      section_80c: 0,
      section_80d: 0,
      section_80ccd_1b: 0
    };
  }, [formData.deductions]);

  // =============================================================================
  // EFFECTS
  // =============================================================================

  useEffect(() => {
    if (totalIncome > 0) {
      runOptimizationAnalysis();
    }
  }, [totalIncome]);

  // =============================================================================
  // ANALYSIS FUNCTIONS
  // =============================================================================

  const runOptimizationAnalysis = async () => {
    setIsAnalyzing(true);
    setAnalysisStep(0);

    // Step 1: Analyze current structure
    setAnalysisStep(1);
    await new Promise(resolve => setTimeout(resolve, 800));
    
    const optimizationResults = TaxOptimizationAlgorithms.analyzeCurrentTaxStructure(
      totalIncome, 
      currentDeductions, 
      'new'
    );
    setOptimizations(optimizationResults);

    // Step 2: Generate investment recommendations
    setAnalysisStep(2);
    await new Promise(resolve => setTimeout(resolve, 600));
    
    const investments = TaxOptimizationAlgorithms.generateInvestmentRecommendations(
      totalIncome,
      currentDeductions
    );
    setInvestmentRecommendations(investments);

    // Step 3: Run scenario analysis
    setAnalysisStep(3);
    await new Promise(resolve => setTimeout(resolve, 700));
    
    const scenarios = TaxOptimizationAlgorithms.calculateScenarioAnalysis(totalIncome);
    setScenarioAnalysis(scenarios);

    setAnalysisStep(4);
    setIsAnalyzing(false);
  };

  // =============================================================================
  // RENDER HELPERS
  // =============================================================================

  const renderAnalysisProgress = () => {
    if (!isAnalyzing && analysisStep === 0) return null;

    const steps = [
      'Initializing analysis...',
      'Analyzing current tax structure...',
      'Generating investment recommendations...',
      'Running scenario analysis...',
      'Analysis complete!'
    ];

    return (
      <Card variant="info" sx={{ mb: 3 }}>
        <Box sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Psychology sx={{ color: 'info.main' }} />
            <Typography variant="h6">AI Tax Optimization Analysis</Typography>
          </Box>
          
          <Typography variant="body2" sx={{ mb: 2 }}>
            {steps[analysisStep]}
          </Typography>
          
          <LinearProgress 
            variant="determinate" 
            value={(analysisStep / 4) * 100}
            sx={{ height: 8, borderRadius: 4 }}
          />
        </Box>
      </Card>
    );
  };

  const renderOptimizationRecommendations = () => {
    if (optimizations.length === 0) return null;

    const totalPotentialSavings = optimizations.reduce((sum, opt) => sum + opt.taxSaving, 0);

    return (
      <Card title="🎯 Tax Optimization Opportunities" variant="outlined" sx={{ mb: 3 }}>
        <Alert severity="success" sx={{ mb: 2 }}>
          <Typography variant="body2">
            <strong>Potential Annual Savings: {formatCurrency(totalPotentialSavings)}</strong>
          </Typography>
        </Alert>

        {optimizations.map((optimization, index) => (
          <Accordion key={optimization.id} defaultExpanded={index === 0}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                <Box sx={{ flex: 1 }}>
                  <Typography variant="subtitle1" fontWeight="bold">
                    {optimization.name}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                    <Chip 
                      label={`Save ${formatCurrency(optimization.taxSaving)}`} 
                      color="success" 
                      size="small" 
                    />
                    <Chip 
                      label={optimization.impact} 
                      color={optimization.impact === 'high' ? 'error' : optimization.impact === 'medium' ? 'warning' : 'info'}
                      size="small" 
                    />
                    <Chip 
                      label={optimization.effort} 
                      variant="outlined" 
                      size="small" 
                    />
                  </Box>
                </Box>
                <Star sx={{ color: optimization.impact === 'high' ? 'gold' : 'gray' }} />
              </Box>
            </AccordionSummary>
            
            <AccordionDetails>
              <Typography variant="body2" paragraph>
                {optimization.description}
              </Typography>
              
              <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, mb: 2 }}>
                <Box>
                  <Typography variant="caption" color="text.secondary">Current</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {formatCurrency(optimization.currentValue)}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="caption" color="text.secondary">Optimized</Typography>
                  <Typography variant="body2" fontWeight="bold" color="success.main">
                    {formatCurrency(optimization.optimizedValue)}
                  </Typography>
                </Box>
              </Box>
              
              <Button
                variant="contained"
                size="small"
                startIcon={<Lightbulb />}
                onClick={() => onApplyRecommendation?.(optimization)}
              >
                Apply Recommendation
              </Button>
            </AccordionDetails>
          </Accordion>
        ))}
      </Card>
    );
  };

  const renderInvestmentRecommendations = () => {
    if (investmentRecommendations.length === 0) return null;

    const filteredRecommendations = investmentRecommendations.filter(
      rec => selectedRiskLevel === 'medium' || rec.riskLevel === selectedRiskLevel
    );

    return (
      <Card title="💰 Smart Investment Recommendations" variant="outlined" sx={{ mb: 3 }}>
        <Box sx={{ mb: 2 }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Risk Level</InputLabel>
            <Select
              value={selectedRiskLevel}
              label="Risk Level"
              onChange={(e) => setSelectedRiskLevel(e.target.value as any)}
            >
              <MenuItem value="low">Low Risk</MenuItem>
              <MenuItem value="medium">Moderate Risk</MenuItem>
              <MenuItem value="high">High Risk</MenuItem>
            </Select>
          </FormControl>
        </Box>

        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
          {filteredRecommendations.map((investment) => (
            <Box key={investment.id} sx={{ flex: '1 1 400px', minWidth: '350px' }}>
              <Card variant="outlined">
                <Box sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    {investment.instrument}
                  </Typography>
                  
                  <Box sx={{ mb: 2 }}>
                    <Chip label={investment.section} color="primary" size="small" sx={{ mr: 1 }} />
                    <Chip label={investment.riskLevel} 
                          color={investment.riskLevel === 'low' ? 'success' : investment.riskLevel === 'high' ? 'error' : 'warning'}
                          size="small" />
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {investment.description}
                  </Typography>
                  
                  <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1, mb: 2 }}>
                    <Box>
                      <Typography variant="caption">Investment</Typography>
                      <Typography variant="body2" fontWeight="bold">
                        {formatCurrency(investment.investmentAmount)}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption">Tax Benefit</Typography>
                      <Typography variant="body2" fontWeight="bold" color="success.main">
                        {formatCurrency(investment.taxBenefit)}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption">Expected Returns</Typography>
                      <Typography variant="body2">{investment.expectedReturns}% p.a.</Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption">Lock-in Period</Typography>
                      <Typography variant="body2">{investment.lockInPeriod}</Typography>
                    </Box>
                  </Box>
                  
                  <Button
                    variant="outlined"
                    fullWidth
                    startIcon={<AccountBalance />}
                    onClick={() => onInvestmentSelect?.(investment)}
                  >
                    Select Investment
                  </Button>
                </Box>
              </Card>
            </Box>
          ))}
        </Box>
      </Card>
    );
  };

  const renderScenarioAnalysis = () => {
    if (scenarioAnalysis.length === 0) return null;

    return (
      <Card title="📊 Scenario Analysis" variant="outlined">
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
          {scenarioAnalysis.map((scenario, index) => (
            <Box key={index} sx={{ flex: '1 1 200px', minWidth: '180px' }}>
              <Card variant={scenario.savingsVsBase > 0 ? 'success' : 'outlined'}>
                <Box sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                    {scenario.scenario}
                  </Typography>
                  
                  <Typography variant="h6" color="primary">
                    {formatCurrency(scenario.netIncome)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Net Income
                  </Typography>
                  
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="body2">
                      Tax: {formatCurrency(scenario.totalTax)}
                    </Typography>
                    <Typography variant="body2">
                      Rate: {formatPercentage(scenario.effectiveRate)}
                    </Typography>
                    
                    {scenario.savingsVsBase !== 0 && (
                      <Typography 
                        variant="body2" 
                        color={scenario.savingsVsBase > 0 ? 'success.main' : 'error.main'}
                        fontWeight="bold"
                      >
                        {scenario.savingsVsBase > 0 ? '+' : ''}{formatCurrency(scenario.savingsVsBase)}
                      </Typography>
                    )}
                  </Box>
                </Box>
              </Card>
            </Box>
          ))}
        </Box>
      </Card>
    );
  };

  // =============================================================================
  // MAIN RENDER
  // =============================================================================

  if (totalIncome === 0) {
    return (
      <Card variant="info">
        <Box sx={{ textAlign: 'center', p: 4 }}>
          <Psychology sx={{ fontSize: 60, color: 'info.main', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            Add Income Sources
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Add your income sources to start the AI-powered tax optimization analysis
          </Typography>
        </Box>
      </Card>
    );
  }

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          <Psychology sx={{ mr: 2, verticalAlign: 'middle' }} />
          AI Tax Optimization Engine
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Advanced analytics and personalized recommendations to minimize your tax liability
        </Typography>
      </Box>

      {renderAnalysisProgress()}
      {renderOptimizationRecommendations()}
      {renderInvestmentRecommendations()}
      {renderScenarioAnalysis()}

      {!isAnalyzing && analysisStep > 0 && (
        <Box sx={{ textAlign: 'center', mt: 4 }}>
          <Button
            variant="outlined"
            startIcon={<Calculate />}
            onClick={runOptimizationAnalysis}
          >
            Rerun Analysis
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default TaxOptimizationEngine; 