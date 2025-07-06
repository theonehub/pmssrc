// =============================================================================
// TAXATION CONSTANTS
// Static data for tax calculations, regimes, rates, and limits
// =============================================================================

// =============================================================================
// TAX YEAR CONSTANTS
// =============================================================================

export const CURRENT_TAX_YEAR = '2025-26';

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