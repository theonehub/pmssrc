import { apiClient } from '@pmssrc/api-client';
import { TaxCalculationRequest, TaxCalculationResponse, TaxRegime } from '@pmssrc/shared-types';
import { NetworkService } from '../../../shared/utils/NetworkService';

export interface TaxCalculationData {
  basicSalary: number;
  allowances: number;
  deductions: number;
  regime: TaxRegime;
  financialYear: string;
  additionalIncome?: number;
  investments?: number;
}

export interface TaxBreakdown {
  grossSalary: number;
  totalDeductions: number;
  taxableIncome: number;
  taxAmount: number;
  effectiveTaxRate: number;
  monthlyTax: number;
  takeHomeSalary: number;
}

export interface TaxRegimeComparison {
  oldRegime: TaxBreakdown;
  newRegime: TaxBreakdown;
  recommendedRegime: TaxRegime;
  savings: number;
}

export class TaxationService {
  /**
   * Calculate tax for given salary and regime
   */
  static async calculateTax(data: TaxCalculationData): Promise<TaxCalculationResponse> {
    return NetworkService.withInternetCheck(() =>
      apiClient.calculateTax({
        basicSalary: data.basicSalary,
        allowances: data.allowances,
        deductions: data.deductions,
        regime: data.regime,
        financialYear: data.financialYear,
        additionalIncome: data.additionalIncome || 0,
        investments: data.investments || 0,
      })
    );
  }

  /**
   * Compare old vs new tax regime
   */
  static async compareTaxRegimes(data: Omit<TaxCalculationData, 'regime'>): Promise<TaxRegimeComparison> {
    const [oldRegimeResult, newRegimeResult] = await Promise.all([
      this.calculateTax({ ...data, regime: 'old' }),
      this.calculateTax({ ...data, regime: 'new' }),
    ]);

    const oldRegime = this.createTaxBreakdown(oldRegimeResult);
    const newRegime = this.createTaxBreakdown(newRegimeResult);
    
    const savings = oldRegime.taxAmount - newRegime.taxAmount;
    const recommendedRegime = savings > 0 ? 'new' : 'old';

    return {
      oldRegime,
      newRegime,
      recommendedRegime,
      savings: Math.abs(savings),
    };
  }

  /**
   * Get tax slabs for a given regime
   */
  static getTaxSlabs(regime: TaxRegime, financialYear: string = '2024-25'): Array<{
    minIncome: number;
    maxIncome: number;
    rate: number;
    description: string;
  }> {
    if (regime === 'old') {
      return [
        { minIncome: 0, maxIncome: 250000, rate: 0, description: 'No Tax' },
        { minIncome: 250001, maxIncome: 500000, rate: 5, description: '5%' },
        { minIncome: 500001, maxIncome: 1000000, rate: 20, description: '20%' },
        { minIncome: 1000001, maxIncome: Infinity, rate: 30, description: '30%' },
      ];
    } else {
      return [
        { minIncome: 0, maxIncome: 300000, rate: 0, description: 'No Tax' },
        { minIncome: 300001, maxIncome: 600000, rate: 5, description: '5%' },
        { minIncome: 600001, maxIncome: 900000, rate: 10, description: '10%' },
        { minIncome: 900001, maxIncome: 1200000, rate: 15, description: '15%' },
        { minIncome: 1200001, maxIncome: 1500000, rate: 20, description: '20%' },
        { minIncome: 1500001, maxIncome: Infinity, rate: 30, description: '30%' },
      ];
    }
  }

  /**
   * Get standard deductions for old regime
   */
  static getStandardDeductions(): Array<{
    category: string;
    maxAmount: number;
    description: string;
  }> {
    return [
      { category: '80C', maxAmount: 150000, description: 'ELSS, PPF, EPF, Life Insurance' },
      { category: '80D', maxAmount: 25000, description: 'Health Insurance Premium' },
      { category: '80TTA', maxAmount: 10000, description: 'Interest on Savings Account' },
      { category: '80G', maxAmount: 10000, description: 'Charitable Donations' },
      { category: 'HRA', maxAmount: 0, description: 'House Rent Allowance' },
      { category: 'LTA', maxAmount: 0, description: 'Leave Travel Allowance' },
    ];
  }

  /**
   * Calculate tax manually for given income and regime
   */
  static calculateTaxManually(income: number, regime: TaxRegime): number {
    const slabs = this.getTaxSlabs(regime);
    let tax = 0;
    let remainingIncome = income;

    for (const slab of slabs) {
      if (remainingIncome <= 0) break;
      
      const slabIncome = Math.min(
        remainingIncome,
        slab.maxIncome === Infinity ? remainingIncome : slab.maxIncome - slab.minIncome + 1
      );
      
      tax += (slabIncome * slab.rate) / 100;
      remainingIncome -= slabIncome;
    }

    return tax;
  }

  /**
   * Create tax breakdown from API response
   */
  private static createTaxBreakdown(response: TaxCalculationResponse): TaxBreakdown {
    const grossSalary = response.basicSalary + response.allowances;
    const totalDeductions = response.deductions;
    const taxableIncome = grossSalary - totalDeductions;
    const taxAmount = response.taxAmount;
    const effectiveTaxRate = (taxAmount / grossSalary) * 100;
    const monthlyTax = taxAmount / 12;
    const takeHomeSalary = grossSalary - taxAmount;

    return {
      grossSalary,
      totalDeductions,
      taxableIncome,
      taxAmount,
      effectiveTaxRate,
      monthlyTax,
      takeHomeSalary,
    };
  }

  /**
   * Format currency
   */
  static formatCurrency(amount: number): string {
    return `₹${amount.toLocaleString('en-IN')}`;
  }

  /**
   * Format percentage
   */
  static formatPercentage(value: number): string {
    return `${value.toFixed(2)}%`;
  }

  /**
   * Get financial year options
   */
  static getFinancialYears(): string[] {
    const currentYear = new Date().getFullYear();
    return [
      `${currentYear}-${(currentYear + 1).toString().slice(-2)}`,
      `${currentYear - 1}-${currentYear.toString().slice(-2)}`,
      `${currentYear - 2}-${(currentYear - 1).toString().slice(-2)}`,
    ];
  }

  /**
   * Validate tax calculation data
   */
  static validateTaxData(data: TaxCalculationData): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];
    
    if (!data.basicSalary || data.basicSalary <= 0) {
      errors.push('Basic salary must be greater than 0');
    }
    
    if (data.allowances < 0) {
      errors.push('Allowances cannot be negative');
    }
    
    if (data.deductions < 0) {
      errors.push('Deductions cannot be negative');
    }
    
    if (!data.regime) {
      errors.push('Tax regime is required');
    }
    
    if (!data.financialYear) {
      errors.push('Financial year is required');
    }
    
    if (data.additionalIncome && data.additionalIncome < 0) {
      errors.push('Additional income cannot be negative');
    }
    
    if (data.investments && data.investments < 0) {
      errors.push('Investments cannot be negative');
    }
    
    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  /**
   * Get regime display name
   */
  static getRegimeDisplayName(regime: TaxRegime): string {
    return regime === 'old' ? 'Old Regime' : 'New Regime';
  }

  /**
   * Get regime description
   */
  static getRegimeDescription(regime: TaxRegime): string {
    if (regime === 'old') {
      return 'Traditional tax regime with deductions and exemptions';
    } else {
      return 'Simplified tax regime with lower rates but no deductions';
    }
  }
} 