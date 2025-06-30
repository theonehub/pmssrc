// =============================================================================
// TAX CALCULATION HOOK
// Business logic hook for tax calculations with mobile-ready features
// =============================================================================

import { useCallback, useEffect, useState } from 'react';
import { useTaxationStore } from '../stores/taxationStore';
import { validators } from '../utils/validation';
import { formatCurrency } from '../utils/formatting';
import * as Types from '../types/api';

// =============================================================================
// HOOK INTERFACE
// =============================================================================

interface UseTaxCalculationReturn {
  // Calculation state
  calculation: Types.PeriodicTaxCalculationResponseDTO | null;
  isCalculating: boolean;
  calculationError: string | null;
  
  // Form state
  formData: Types.ComprehensiveTaxInputDTO;
  isFormValid: boolean;
  formErrors: Record<string, string>;
  
  // Calculation actions
  calculateTax: (input?: Types.ComprehensiveTaxInputDTO) => Promise<void>;
  updateFormSection: (section: string, data: any) => void;
  resetCalculation: () => void;
  
  // Quick calculations
  getQuickTaxEstimate: (annualSalary: number, regime?: Types.TaxRegime) => number;
  compareRegimes: (input: Types.ComprehensiveTaxInputDTO) => Promise<RegimeComparison>;
  
  // Formatting helpers
  formatTaxAmount: (amount: number) => string;
  formatEffectiveRate: (rate: number) => string;
  
  // Validation helpers
  validateCurrentForm: () => boolean;
  getValidationErrors: () => Record<string, string>;
}

interface RegimeComparison {
  oldRegime: {
    totalTax: number;
    effectiveRate: number;
  };
  newRegime: {
    totalTax: number;
    effectiveRate: number;
  };
  recommendedRegime: Types.TaxRegime;
  savings: number;
}

// =============================================================================
// MAIN HOOK
// =============================================================================

export const useTaxCalculation = (): UseTaxCalculationReturn => {
  const {
    currentCalculation,
    calculationLoading,
    calculationError,
    formData,
    calculateTax: storeCalculateTax,
    updateFormData,
    clearError
  } = useTaxationStore();
  
  const [localValidation, setLocalValidation] = useState<{
    isValid: boolean;
    errors: Record<string, string>;
  }>({
    isValid: false,
    errors: {}
  });
  
  // =============================================================================
  // VALIDATION EFFECT
  // =============================================================================
  
  useEffect(() => {
    const validateForm = () => {
      const validation = validators.basicInfo(formData);
      setLocalValidation({
        isValid: validation.isValid,
        errors: validation.fieldErrors
      });
    };
    
    validateForm();
  }, [formData]);
  
  // =============================================================================
  // CALCULATION ACTIONS
  // =============================================================================
  
  const calculateTax = useCallback(async (input?: Types.ComprehensiveTaxInputDTO) => {
    const calculationInput = input || formData;
    
    // Validate before calculation
    const validation = validators.basicInfo(calculationInput);
    if (!validation.isValid) {
      throw new Error('Please fix validation errors before calculating');
    }
    
    try {
      await storeCalculateTax(calculationInput);
    } catch (error) {
      console.error('Tax calculation failed:', error);
      throw error;
    }
  }, [formData, storeCalculateTax]);
  
  const updateFormSection = useCallback((section: string, data: any) => {
    updateFormData(section, data);
  }, [updateFormData]);
  
  const resetCalculation = useCallback(() => {
    clearError();
    // Additional reset logic can be added here
  }, [clearError]);
  
  // =============================================================================
  // QUICK CALCULATIONS
  // =============================================================================
  
  const getQuickTaxEstimate = useCallback((
    annualSalary: number, 
    regime: Types.TaxRegime = 'new'
  ): number => {
    // Simple tax estimation logic
    const standardDeduction = 50000;
    const taxableIncome = Math.max(0, annualSalary - standardDeduction);
    
    if (regime === 'new') {
      // New regime slabs (simplified)
      if (taxableIncome <= 300000) return 0;
      if (taxableIncome <= 600000) return (taxableIncome - 300000) * 0.05;
      if (taxableIncome <= 900000) return 15000 + (taxableIncome - 600000) * 0.10;
      if (taxableIncome <= 1200000) return 45000 + (taxableIncome - 900000) * 0.15;
      if (taxableIncome <= 1500000) return 90000 + (taxableIncome - 1200000) * 0.20;
      return 150000 + (taxableIncome - 1500000) * 0.30;
    } else {
      // Old regime slabs (simplified)
      if (taxableIncome <= 250000) return 0;
      if (taxableIncome <= 500000) return (taxableIncome - 250000) * 0.05;
      if (taxableIncome <= 1000000) return 12500 + (taxableIncome - 500000) * 0.20;
      return 112500 + (taxableIncome - 1000000) * 0.30;
    }
  }, []);
  
  const compareRegimes = useCallback(async (
    input: Types.ComprehensiveTaxInputDTO
  ): Promise<RegimeComparison> => {
    // For now, use quick estimates (in production, you'd call the API)
    const salaryIncome = input.salary_income?.basic_salary || 0;
    
    const oldRegimeTax = getQuickTaxEstimate(salaryIncome, 'old');
    const newRegimeTax = getQuickTaxEstimate(salaryIncome, 'new');
    
    const oldEffectiveRate = salaryIncome > 0 ? (oldRegimeTax / salaryIncome) * 100 : 0;
    const newEffectiveRate = salaryIncome > 0 ? (newRegimeTax / salaryIncome) * 100 : 0;
    
    const recommendedRegime = oldRegimeTax < newRegimeTax ? 'old' : 'new';
    const savings = Math.abs(oldRegimeTax - newRegimeTax);
    
    return {
      oldRegime: {
        totalTax: oldRegimeTax,
        effectiveRate: oldEffectiveRate
      },
      newRegime: {
        totalTax: newRegimeTax,
        effectiveRate: newEffectiveRate
      },
      recommendedRegime,
      savings
    };
  }, [getQuickTaxEstimate]);
  
  // =============================================================================
  // FORMATTING HELPERS
  // =============================================================================
  
  const formatTaxAmount = useCallback((amount: number): string => {
    return formatCurrency(amount, { showSymbol: true, compact: false });
  }, []);
  
  const formatEffectiveRate = useCallback((rate: number): string => {
    return `${rate.toFixed(2)}%`;
  }, []);
  
  // =============================================================================
  // VALIDATION HELPERS
  // =============================================================================
  
  const validateCurrentForm = useCallback((): boolean => {
    const validation = validators.basicInfo(formData);
    setLocalValidation({
      isValid: validation.isValid,
      errors: validation.fieldErrors
    });
    return validation.isValid;
  }, [formData]);
  
  const getValidationErrors = useCallback((): Record<string, string> => {
    return localValidation.errors;
  }, [localValidation.errors]);
  
  // =============================================================================
  // RETURN HOOK INTERFACE
  // =============================================================================
  
  return {
    // Calculation state
    calculation: currentCalculation,
    isCalculating: calculationLoading.isLoading,
    calculationError: calculationError.hasError ? calculationError.message || null : null,
    
    // Form state
    formData,
    isFormValid: localValidation.isValid,
    formErrors: localValidation.errors,
    
    // Calculation actions
    calculateTax,
    updateFormSection,
    resetCalculation,
    
    // Quick calculations
    getQuickTaxEstimate,
    compareRegimes,
    
    // Formatting helpers
    formatTaxAmount,
    formatEffectiveRate,
    
    // Validation helpers
    validateCurrentForm,
    getValidationErrors
  };
};

// =============================================================================
// ADDITIONAL HOOKS FOR SPECIFIC USE CASES
// =============================================================================

/**
 * Hook for regime comparison functionality
 */
export const useRegimeComparison = () => {
  const { formData } = useTaxationStore();
  const { compareRegimes } = useTaxCalculation();
  
  const [comparison, setComparison] = useState<RegimeComparison | null>(null);
  const [isComparing, setIsComparing] = useState(false);
  
  const performComparison = useCallback(async () => {
    if (!formData.salary_income?.basic_salary) return;
    
    setIsComparing(true);
    try {
      const result = await compareRegimes(formData);
      setComparison(result);
    } catch (error) {
      console.error('Regime comparison failed:', error);
    } finally {
      setIsComparing(false);
    }
  }, [formData, compareRegimes]);
  
  return {
    comparison,
    isComparing,
    performComparison
  };
};

/**
 * Hook for mobile-optimized quick calculations
 */
export const useQuickCalculation = () => {
  const { getQuickTaxEstimate } = useTaxCalculation();
  const [quickResult, setQuickResult] = useState<{
    oldRegime: number;
    newRegime: number;
    recommended: Types.TaxRegime;
  } | null>(null);
  
  const calculateQuick = useCallback((salary: number) => {
    const oldTax = getQuickTaxEstimate(salary, 'old');
    const newTax = getQuickTaxEstimate(salary, 'new');
    
    setQuickResult({
      oldRegime: oldTax,
      newRegime: newTax,
      recommended: oldTax < newTax ? 'old' : 'new'
    });
  }, [getQuickTaxEstimate]);
  
  return {
    quickResult,
    calculateQuick
  };
}; 