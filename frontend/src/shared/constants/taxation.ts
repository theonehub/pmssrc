// =============================================================================
// TAXATION CONSTANTS
// Static data for tax calculations, regimes, rates, and limits
// =============================================================================

import { TaxRegime } from '../types/api';

// =============================================================================
// TAX YEAR CONSTANTS
// =============================================================================

export const CURRENT_TAX_YEAR = '2024-25';
export const CURRENT_ASSESSMENT_YEAR = '2025-26';

export const AVAILABLE_TAX_YEARS = [
  '2024-25', '2023-24', '2022-23', '2021-22', '2020-21'
];

// =============================================================================
// TAX REGIME INFORMATION
// =============================================================================

export const TAX_REGIME_INFO = {
  old: {
    name: 'Old Tax Regime',
    description: 'Traditional tax regime with deductions and exemptions',
    deductions_available: true,
    exemptions_available: true,
    standard_deduction: 50000,
    rebate_limit: 500000,
    rebate_amount: 12500,
  },
  new: {
    name: 'New Tax Regime',
    description: 'Simplified tax regime with lower rates',
    deductions_available: false,
    exemptions_limited: true,
    standard_deduction: 50000,
    rebate_limit: 700000,
    rebate_amount: 25000,
  }
} as const;

// =============================================================================
// TAX SLABS (2024-25)
// =============================================================================

export const TAX_SLABS_2024_25 = {
  old: [
    { min: 0, max: 250000, rate: 0 },
    { min: 250001, max: 500000, rate: 5 },
    { min: 500001, max: 1000000, rate: 20 },
    { min: 1000001, max: Infinity, rate: 30 }
  ],
  new: [
    { min: 0, max: 300000, rate: 0 },
    { min: 300001, max: 600000, rate: 5 },
    { min: 600001, max: 900000, rate: 10 },
    { min: 900001, max: 1200000, rate: 15 },
    { min: 1200001, max: 1500000, rate: 20 },
    { min: 1500001, max: Infinity, rate: 30 }
  ]
} as const;

// =============================================================================
// SURCHARGE RATES
// =============================================================================

export const SURCHARGE_RATES = {
  individuals: [
    { min: 0, max: 5000000, rate: 0 },
    { min: 5000001, max: 10000000, rate: 10 },
    { min: 10000001, max: 20000000, rate: 15 },
    { min: 20000001, max: 50000000, rate: 25 },
    { min: 50000001, max: Infinity, rate: 37 }
  ]
} as const;

// =============================================================================
// EDUCATION CESS
// =============================================================================

export const EDUCATION_CESS_RATE = 4; // 4% on tax + surcharge

// =============================================================================
// DEDUCTION LIMITS (2024-25)
// =============================================================================

export const DEDUCTION_LIMITS = {
  section_80c: {
    limit: 150000,
    description: 'PPF, ELSS, Life Insurance, etc.',
    applicable_regime: ['old'] as TaxRegime[]
  },
  section_80ccc: {
    limit: 150000,
    description: 'Pension fund contributions',
    applicable_regime: ['old'] as TaxRegime[]
  },
  section_80ccd_1: {
    limit: 150000,
    description: 'NPS contribution (employee)',
    applicable_regime: ['old'] as TaxRegime[]
  },
  section_80ccd_1b: {
    limit: 50000,
    description: 'Additional NPS contribution',
    applicable_regime: ['old', 'new'] as TaxRegime[]
  },
  section_80ccd_2: {
    limit: 'No limit',
    description: 'NPS contribution (employer)',
    applicable_regime: ['old', 'new'] as TaxRegime[]
  },
  section_80d_self: {
    limit: 25000,
    description: 'Health insurance (self & family)',
    applicable_regime: ['old'] as TaxRegime[]
  },
  section_80d_parents: {
    limit: 25000,
    description: 'Health insurance (parents)',
    applicable_regime: ['old'] as TaxRegime[]
  },
  section_80d_senior_citizen: {
    limit: 50000,
    description: 'Health insurance (senior citizen)',
    applicable_regime: ['old'] as TaxRegime[]
  },
  section_80e: {
    limit: 'No limit',
    description: 'Education loan interest',
    applicable_regime: ['old'] as TaxRegime[]
  },
  section_80g: {
    limit: 'Varies',
    description: 'Donations to charity',
    applicable_regime: ['old'] as TaxRegime[]
  },
  section_80tta: {
    limit: 10000,
    description: 'Savings account interest',
    applicable_regime: ['old'] as TaxRegime[]
  },
  section_80ttb: {
    limit: 50000,
    description: 'Deposit interest (senior citizen)',
    applicable_regime: ['old'] as TaxRegime[]
  }
} as const;

// =============================================================================
// EXEMPTION LIMITS
// =============================================================================

export const EXEMPTION_LIMITS = {
  hra: {
    description: 'House Rent Allowance',
    calculation: 'Minimum of: Actual HRA, 50%/40% of basic, Rent - 10% of basic',
    applicable_regime: ['old'] as TaxRegime[]
  },
  lta: {
    limit: 'No monetary limit',
    description: 'Leave Travel Allowance',
    applicable_regime: ['old'] as TaxRegime[]
  },
  medical_allowance: {
    limit: 15000,
    description: 'Medical allowance',
    applicable_regime: ['old'] as TaxRegime[]
  },
  conveyance_allowance: {
    limit: 1600,
    description: 'Conveyance allowance',
    applicable_regime: ['old'] as TaxRegime[]
  },
  uniform_allowance: {
    limit: 'Actual amount',
    description: 'Uniform allowance',
    applicable_regime: ['old'] as TaxRegime[]
  }
} as const;

// =============================================================================
// PERQUISITES VALUATION RULES
// =============================================================================

export const PERQUISITES_RULES = {
  accommodation: {
    owned_by_employer: '15% of salary',
    rented_by_employer: 'Actual rent or 15% of salary, whichever is lower',
    hotel_accommodation: 'Actual amount',
    applicable_regime: ['old', 'new'] as TaxRegime[]
  },
  car_benefit: {
    engine_1600cc_below: 1800,
    engine_above_1600cc: 2400,
    per_month: true,
    applicable_regime: ['old'] as TaxRegime[]
  },
  driver_salary: {
    valuation: 'Actual salary paid',
    applicable_regime: ['old'] as TaxRegime[]
  },
  telephone: {
    mobile_limit: 1000,
    landline_limit: 500,
    per_month: true,
    applicable_regime: ['old'] as TaxRegime[]
  }
} as const;

// =============================================================================
// CAPITAL GAINS RATES
// =============================================================================

export const CAPITAL_GAINS_RATES = {
  short_term: {
    equity: 15,
    property: 'Normal rates',
    other_assets: 'Normal rates'
  },
  long_term: {
    equity: 10,
    property_with_indexation: 20,
    property_without_indexation: 12.5,
    other_assets: 20
  }
} as const;

// =============================================================================
// HOUSE PROPERTY CONSTANTS
// =============================================================================

export const HOUSE_PROPERTY_CONSTANTS = {
  standard_deduction_rate: 30, // 30% of net annual value
  self_occupied_exemption: 200000, // Interest on loan for self-occupied
  let_out_no_limit: true, // No limit for let-out property
  municipal_tax_deduction: 'Actual amount paid'
} as const;

// =============================================================================
// AGE-BASED EXEMPTIONS
// =============================================================================

export const AGE_BASED_EXEMPTIONS = {
  below_60: {
    basic_exemption: 250000
  },
  senior_citizen: {
    age_range: '60-80',
    basic_exemption: 300000,
    additional_benefits: ['Higher 80D limit', '80TTB available']
  },
  super_senior_citizen: {
    age_range: '80+',
    basic_exemption: 500000,
    additional_benefits: ['Higher 80D limit', '80TTB available', 'No TDS on interest up to 50,000']
  }
} as const;

// =============================================================================
// TDS RATES
// =============================================================================

export const TDS_RATES = {
  salary: 'As per tax slabs',
  interest_banks: 10,
  interest_company_deposits: 10,
  dividend: 10,
  rent: 10,
  professional_fees: 10,
  commission_brokerage: 5
} as const;

// =============================================================================
// FORM FIELD CONFIGURATIONS
// =============================================================================

export const FORM_FIELD_CONFIGS = {
  currency: {
    prefix: '₹',
    thousands_separator: ',',
    decimal_places: 0,
    max_value: 99999999999
  },
  percentage: {
    suffix: '%',
    min_value: 0,
    max_value: 100,
    decimal_places: 2
  },
  date: {
    format: 'DD/MM/YYYY',
    min_year: 1950,
    max_year: new Date().getFullYear() + 10
  }
} as const;

// =============================================================================
// VALIDATION RULES
// =============================================================================

export const VALIDATION_RULES = {
  required_fields: {
    basic_info: ['tax_year', 'regime_type', 'age'],
    salary_income: ['basic_salary'],
    deductions: []
  },
  field_limits: {
    age: { min: 18, max: 100 },
    basic_salary: { min: 0, max: 99999999 },
    deduction_80c: { min: 0, max: 150000 }
  },
  conditional_validations: {
    hra_exemption: 'Required if HRA > 0',
    house_property: 'Required if property income > 0',
    capital_gains: 'Required if gains > 0'
  }
} as const;

// =============================================================================
// UI DISPLAY CONSTANTS
// =============================================================================

export const UI_CONSTANTS = {
  colors: {
    tax_liability: '#dc2626', // red-600
    savings: '#16a34a', // green-600
    income: '#2563eb', // blue-600
    deductions: '#7c3aed', // violet-600
    neutral: '#6b7280' // gray-500
  },
  chart_colors: [
    '#3b82f6', '#ef4444', '#10b981', '#f59e0b',
    '#8b5cf6', '#06b6d4', '#84cc16', '#f97316'
  ],
  animation_duration: 300,
  debounce_delay: 500
} as const;

// =============================================================================
// ERROR MESSAGES
// =============================================================================

export const ERROR_MESSAGES = {
  network: 'Network error. Please check your connection.',
  validation: 'Please check the highlighted fields.',
  calculation: 'Error calculating tax. Please try again.',
  api_timeout: 'Request timeout. Please try again.',
  unauthorized: 'Session expired. Please login again.',
  not_found: 'Record not found.',
  server_error: 'Server error. Please try again later.'
} as const;

// =============================================================================
// SUCCESS MESSAGES
// =============================================================================

export const SUCCESS_MESSAGES = {
  calculation_complete: 'Tax calculation completed successfully!',
  record_saved: 'Taxation record saved successfully!',
  record_updated: 'Taxation record updated successfully!',
  record_deleted: 'Taxation record deleted successfully!',
  export_complete: 'Export completed successfully!'
} as const;

// =============================================================================
// MOBILE BREAKPOINTS
// =============================================================================

export const MOBILE_BREAKPOINTS = {
  phone: 640,
  tablet: 768,
  desktop: 1024,
  large_desktop: 1280
} as const;

// =============================================================================
// CACHE SETTINGS
// =============================================================================

export const CACHE_SETTINGS = {
  tax_years: { duration: 24 * 60 * 60 * 1000 }, // 24 hours
  regime_comparison: { duration: 12 * 60 * 60 * 1000 }, // 12 hours
  calculation_results: { duration: 30 * 60 * 1000 }, // 30 minutes
  user_records: { duration: 5 * 60 * 1000 } // 5 minutes
} as const;

// =============================================================================
// INCOME TYPES
// =============================================================================

export const INCOME_TYPES = [
  {
    value: 'salary' as const,
    label: 'Salary Income',
    description: 'Income from employment, pension, etc.'
  },
  {
    value: 'business' as const,
    label: 'Business Income',
    description: 'Income from business or profession'
  },
  {
    value: 'capital_gains' as const,
    label: 'Capital Gains',
    description: 'Gains from sale of assets'
  },
  {
    value: 'rental' as const,
    label: 'House Property',
    description: 'Income from rental property'
  },
  {
    value: 'other_sources' as const,
    label: 'Other Sources',
    description: 'Interest, dividends, lottery, etc.'
  }
] as const; 