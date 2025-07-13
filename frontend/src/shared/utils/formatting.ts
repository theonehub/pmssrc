// =============================================================================
// FORMATTING UTILITIES
// Functions for formatting currency, numbers, dates, and display values
// =============================================================================

import { FORM_FIELD_CONFIGS } from '../constants/taxation';

// =============================================================================
// CURRENCY FORMATTING
// =============================================================================

/**
 * Format currency in Indian format with commas
 */
export const formatCurrency = (
  amount: number | string | null | undefined,
  options: {
    showSymbol?: boolean;
    compact?: boolean;
    decimalPlaces?: number;
    showZero?: boolean;
  } = {}
): string => {
  const {
    showSymbol = true,
    compact = false,
    decimalPlaces = 0,
    showZero = true
  } = options;

  if (amount === null || amount === undefined) return '';
  
  const numAmount = typeof amount === 'string' ? parseFloat(amount) : amount;
  
  if (isNaN(numAmount)) return '';
  if (numAmount === 0 && !showZero) return '';

  // For compact format (mobile-friendly)
  if (compact && Math.abs(numAmount) >= 100000) {
    if (Math.abs(numAmount) >= 10000000) { // 1 crore
      const crores = numAmount / 10000000;
      return `${showSymbol ? '₹' : ''}${crores.toFixed(1)}Cr`;
    } else if (Math.abs(numAmount) >= 100000) { // 1 lakh
      const lakhs = numAmount / 100000;
      return `${showSymbol ? '₹' : ''}${lakhs.toFixed(1)}L`;
    }
  }

  // Indian number formatting with commas
  const formatted = new Intl.NumberFormat('en-IN', {
    minimumFractionDigits: decimalPlaces,
    maximumFractionDigits: decimalPlaces
  }).format(numAmount);

  return showSymbol ? `₹${formatted}` : formatted;
};

/**
 * Format currency for input fields (without symbols, with proper separators)
 */
export const formatCurrencyInput = (value: string): string => {
  // Remove all non-numeric characters except decimal point
  const cleaned = value.replace(/[^\d.]/g, '');
  
  // Handle multiple decimal points
  const parts = cleaned.split('.');
  if (parts.length > 2) {
    return parts[0] + '.' + parts.slice(1).join('');
  }
  
  // Add commas for thousands separator
  if (parts[0]) {
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  }
  
  return parts.join('.');
};

/**
 * Parse currency input back to number
 */
export const parseCurrencyInput = (value: string): number => {
  const cleaned = value.replace(/[^\d.]/g, '');
  const parsed = parseFloat(cleaned);
  return isNaN(parsed) ? 0 : parsed;
};

// =============================================================================
// PERCENTAGE FORMATTING
// =============================================================================

/**
 * Format percentage with proper decimal places
 */
export const formatPercentage = (
  value: number | string | null | undefined,
  decimalPlaces: number = 2
): string => {
  if (value === null || value === undefined) return '';
  
  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  
  if (isNaN(numValue)) return '';
  
  return `${numValue.toFixed(decimalPlaces)}%`;
};

/**
 * Format tax rate for display
 */
export const formatTaxRate = (rate: number): string => {
  if (rate === 0) return 'Nil';
  return `${rate}%`;
};

// =============================================================================
// DATE FORMATTING
// =============================================================================

/**
 * Format date in Indian format (DD/MM/YYYY)
 */
export const formatDate = (
  date: Date | string | null | undefined,
  format: 'short' | 'long' | 'indian' = 'indian'
): string => {
  if (!date) return '';
  
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  if (isNaN(dateObj.getTime())) return '';
  
  switch (format) {
    case 'short':
      return dateObj.toLocaleDateString('en-IN', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
      });
    case 'long':
      return dateObj.toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
      });
    case 'indian':
    default:
      return dateObj.toLocaleDateString('en-IN', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      });
  }
};

/**
 * Format relative time (e.g., "2 hours ago")
 */
export const formatRelativeTime = (date: Date | string): string => {
  if (!date) return '';
  
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diffMs = now.getTime() - dateObj.getTime();
  
  const diffMinutes = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  
  if (diffMinutes < 1) return 'Just now';
  if (diffMinutes < 60) return `${diffMinutes}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  
  return formatDate(dateObj, 'short');
};

// =============================================================================
// NUMBER FORMATTING
// =============================================================================

/**
 * Format large numbers with appropriate units
 */
export const formatLargeNumber = (
  value: number,
  compact: boolean = false
): string => {
  if (Math.abs(value) >= 10000000) { // 1 crore
    return compact 
      ? `${(value / 10000000).toFixed(1)}Cr`
      : `${(value / 10000000).toFixed(2)} Crore`;
  } else if (Math.abs(value) >= 100000) { // 1 lakh
    return compact 
      ? `${(value / 100000).toFixed(1)}L`
      : `${(value / 100000).toFixed(2)} Lakh`;
  } else if (Math.abs(value) >= 1000) { // 1 thousand
    return compact 
      ? `${(value / 1000).toFixed(1)}K`
      : `${(value / 1000).toFixed(2)} Thousand`;
  }
  
  return value.toLocaleString('en-IN');
};

/**
 * Format file size
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// =============================================================================
// TEXT FORMATTING
// =============================================================================

/**
 * Capitalize first letter of each word
 */
export const titleCase = (str: string): string => {
  return str.replace(/\w\S*/g, (txt) => 
    txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
  );
};

/**
 * Convert camelCase to readable text
 */
export const camelToTitle = (str: string): string => {
  return str
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, (s) => s.toUpperCase())
    .trim();
};

/**
 * Truncate text with ellipsis
 */
export const truncateText = (
  text: string,
  maxLength: number,
  addEllipsis: boolean = true
): string => {
  if (text.length <= maxLength) return text;
  
  const truncated = text.substring(0, maxLength);
  return addEllipsis ? `${truncated}...` : truncated;
};

// =============================================================================
// TAX-SPECIFIC FORMATTING
// =============================================================================

/**
 * Format tax year display (e.g., "2024-25" -> "FY 2024-25")
 */
export const formatTaxYear = (taxYear: string, includeAY: boolean = false): string => {
  if (!taxYear) return '';
  
  const fy = `FY ${taxYear}`;
  
  if (includeAY) {
    const parts = taxYear.split('-');
    if (parts.length !== 2) return fy;
    
    const [startYear, endYear] = parts;
    if (!startYear || !endYear) return fy;
    
    const ayStartYear = parseInt(startYear) + 1;
    const ayEndYear = parseInt(`20${endYear}`) + 1;
    const ay = `AY ${ayStartYear}-${ayEndYear.toString().slice(-2)}`;
    return `${fy} (${ay})`;
  }
  
  return fy;
};

/**
 * Format regime name for display
 */
export const formatRegimeName = (regime: string): string => {
  switch (regime.toLowerCase()) {
    case 'old':
      return 'Old Tax Regime';
    case 'new':
      return 'New Tax Regime';
    default:
      return titleCase(regime);
  }
};

/**
 * Format deduction section name
 */
export const formatDeductionSection = (section: string): string => {
  return section.replace(/section_/i, 'Section ').toUpperCase();
};

/**
 * Format income source name
 */
export const formatIncomeSource = (source: string): string => {
  const sourceMap: Record<string, string> = {
    'salary_income': 'Salary Income',
    'house_property_income': 'House Property Income',
    'capital_gains': 'Capital Gains',
    'other_income': 'Other Income',
    'business_income': 'Business Income'
  };
  
  return sourceMap[source] || titleCase(source.replace(/_/g, ' '));
};

// =============================================================================
// TAX YEAR HELPERS
// =============================================================================

/**
 * Get the current tax year as a string (e.g., '2024-25')
 */
export const getCurrentTaxYear = (): string => {
  const currentDate = new Date();
  const currentYear = currentDate.getFullYear();
  const currentMonth = currentDate.getMonth() + 1;
  // Indian tax year starts in April
  if (currentMonth >= 4) {
    return `${currentYear}-${(currentYear + 1).toString().slice(-2)}`;
  } else {
    return `${currentYear - 1}-${currentYear.toString().slice(-2)}`;
  }
};

/**
 * Get an array of available tax years (current + last 4 years)
 */
export const getAvailableTaxYears = (): string[] => {
  const currentTaxYear = getCurrentTaxYear();
  const yearParts = currentTaxYear.split('-');
  const currentStartYear = parseInt(yearParts[0] || '2024');
  const years: string[] = [];
  for (let i = 0; i < 5; i++) {
    const startYear = currentStartYear - i;
    const endYear = startYear + 1;
    years.push(`${startYear}-${endYear.toString().slice(-2)}`);
  }
  return years;
};

/**
 * Convert a tax year string (e.g., '2024-25') to the start year as a number (e.g., 2024)
 */
export const taxYearStringToStartYear = (taxYear: string | undefined): number => {
  if (!taxYear || typeof taxYear !== 'string') return 0;
  const parts = taxYear.split('-');
  if (!parts[0]) return 0;
  return parseInt(parts[0], 10);
};

// =============================================================================
// MOBILE-SPECIFIC FORMATTING
// =============================================================================

/**
 * Format for mobile display (shorter labels, compact numbers)
 */
export const formatForMobile = {
  currency: (amount: number) => formatCurrency(amount, { compact: true }),
  
  label: (text: string, maxLength: number = 20) => 
    truncateText(text, maxLength),
  
  tableHeader: (text: string) => 
    truncateText(text, 10).replace(/\s+/g, '\n'),
  
  percentage: (value: number) => 
    value < 0.01 ? '<0.01%' : `${value.toFixed(1)}%`,
  
  date: (date: Date | string) => 
    formatDate(date, 'short')
};

// =============================================================================
// VALIDATION HELPERS
// =============================================================================

/**
 * Check if a value is a valid currency amount
 */
export const isValidCurrency = (value: string | number): boolean => {
  const numValue = typeof value === 'string' ? parseCurrencyInput(value) : value;
  return !isNaN(numValue) && numValue >= 0 && numValue <= FORM_FIELD_CONFIGS.currency.max_value;
};

/**
 * Check if a value is a valid percentage
 */
export const isValidPercentage = (value: string | number): boolean => {
  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  return !isNaN(numValue) && numValue >= 0 && numValue <= 100;
};

// =============================================================================
// EXPORT UTILITIES
// =============================================================================

export const formatters = {
  currency: formatCurrency,
  currencyInput: formatCurrencyInput,
  percentage: formatPercentage,
  date: formatDate,
  relativeTime: formatRelativeTime,
  largeNumber: formatLargeNumber,
  fileSize: formatFileSize,
  taxYear: formatTaxYear,
  regimeName: formatRegimeName,
  mobile: formatForMobile
};

export const parsers = {
  currency: parseCurrencyInput
};

export const validators = {
  currency: isValidCurrency,
  percentage: isValidPercentage
}; 