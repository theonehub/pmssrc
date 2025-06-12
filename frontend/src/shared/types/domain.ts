// =============================================================================
// FRONTEND DOMAIN TYPES
// Business logic types for UI components and state management
// =============================================================================

import { TaxRegime, FilingStatus } from './api';

// =============================================================================
// FORM STATE TYPES
// =============================================================================

export interface FormFieldState {
  value: any;
  error?: string;
  touched: boolean;
  dirty: boolean;
}

export interface FormSectionState {
  [fieldName: string]: FormFieldState;
}

export interface TaxCalculatorFormState {
  basicInfo: FormSectionState;
  salaryIncome: FormSectionState;
  perquisites: FormSectionState;
  houseProperty: FormSectionState;
  capitalGains: FormSectionState;
  otherIncome: FormSectionState;
  deductions: FormSectionState;
  isValid: boolean;
  isDirty: boolean;
  currentStep: number;
  totalSteps: number;
}

// =============================================================================
// UI STATE TYPES
// =============================================================================

export interface LoadingState {
  isLoading: boolean;
  operation?: string;
  progress?: number;
}

export interface ErrorState {
  hasError: boolean;
  message?: string;
  code?: string;
  timestamp?: string;
}

export interface NotificationState {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
  action?: {
    label: string;
    handler: () => void;
  };
}

export interface PaginationState {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

// =============================================================================
// NAVIGATION AND ROUTING TYPES
// =============================================================================

export interface NavMenuItem {
  id: string;
  label: string;
  path?: string;
  icon?: string;
  children?: NavMenuItem[];
  badge?: string | number;
  disabled?: boolean;
  roles?: string[];
}

export interface BreadcrumbItem {
  label: string;
  path?: string;
  active?: boolean;
}

// =============================================================================
// CALCULATION WORKFLOW TYPES
// =============================================================================

export interface CalculationStep {
  id: string;
  title: string;
  description: string;
  component: string;
  isCompleted: boolean;
  isActive: boolean;
  isOptional: boolean;
  validationRules?: ValidationRule[];
}

export interface ValidationRule {
  field: string;
  type: 'required' | 'min' | 'max' | 'pattern' | 'custom';
  value?: any;
  message: string;
  validator?: (value: any) => boolean;
}

export interface CalculationContext {
  currentStep: number;
  steps: CalculationStep[];
  formData: any;
  validationErrors: Record<string, string[]>;
  canProceed: boolean;
  canGoBack: boolean;
}

// =============================================================================
// CHART AND VISUALIZATION TYPES
// =============================================================================

export interface ChartDataPoint {
  label: string;
  value: number;
  color?: string;
  tooltip?: string;
}

export interface TaxBreakdownChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor: string[];
    borderColor?: string[];
  }[];
}

export interface MonthlyProjectionChartData {
  months: string[];
  income: number[];
  tax: number[];
  netIncome: number[];
}

export interface RegimeComparisonChartData {
  categories: string[];
  oldRegime: number[];
  newRegime: number[];
}

// =============================================================================
// USER PREFERENCES AND SETTINGS
// =============================================================================

export interface UserPreferences {
  defaultTaxRegime: TaxRegime;
  defaultTaxYear: string;
  currency: 'INR' | 'USD';
  numberFormat: 'indian' | 'international';
  theme: 'light' | 'dark' | 'auto';
  language: 'en' | 'hi';
  autoSave: boolean;
  emailNotifications: boolean;
  reminderSettings: ReminderSettings;
}

export interface ReminderSettings {
  taxDeadlines: boolean;
  formSubmissions: boolean;
  documentUploads: boolean;
  calculationUpdates: boolean;
}

// =============================================================================
// CALCULATION TEMPLATES AND PRESETS
// =============================================================================

export interface CalculationTemplate {
  id: string;
  name: string;
  description: string;
  category: 'salary' | 'business' | 'investment' | 'retirement';
  prefilledData: Partial<any>; // Will be typed more specifically later
  tags: string[];
  isPublic: boolean;
  createdBy: string;
  createdAt: string;
  usageCount: number;
}

export interface QuickCalculationPreset {
  id: string;
  name: string;
  icon: string;
  description: string;
  targetAudience: string;
  estimatedTime: string; // e.g., "5 minutes"
  requiredFields: string[];
  optionalFields: string[];
}

// =============================================================================
// SEARCH AND FILTER TYPES
// =============================================================================

export interface SearchFilters {
  taxYear?: string;
  regime?: TaxRegime;
  status?: FilingStatus;
  dateRange?: {
    start: string;
    end: string;
  };
  amountRange?: {
    min: number;
    max: number;
  };
  tags?: string[];
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface SearchResult<T> {
  items: T[];
  totalCount: number;
  facets: SearchFacet[];
  suggestions: string[];
}

export interface SearchFacet {
  field: string;
  values: Array<{
    value: string;
    count: number;
    selected: boolean;
  }>;
}

// =============================================================================
// IMPORT/EXPORT TYPES
// =============================================================================

export interface ImportOptions {
  source: 'csv' | 'excel' | 'pdf' | 'form16' | 'bank_statement';
  mapping: Record<string, string>;
  validation: boolean;
  mergeStrategy: 'replace' | 'merge' | 'append';
}

export interface ExportOptions {
  format: 'pdf' | 'excel' | 'csv' | 'json';
  sections: string[];
  includeCharts: boolean;
  includeCalculations: boolean;
  template?: string;
}

export interface ImportResult {
  success: boolean;
  recordsProcessed: number;
  recordsImported: number;
  errors: Array<{
    row: number;
    field: string;
    message: string;
  }>;
  warnings: string[];
}

// =============================================================================
// MOBILE-SPECIFIC TYPES
// =============================================================================

export interface TouchGestureConfig {
  swipeThreshold: number;
  longPressDelay: number;
  doubleTapDelay: number;
}

export interface MobileViewport {
  width: number;
  height: number;
  orientation: 'portrait' | 'landscape';
  isTablet: boolean;
  isPhone: boolean;
}

export interface OfflineCapability {
  isOffline: boolean;
  hasLocalData: boolean;
  syncStatus: 'synced' | 'pending' | 'error';
  lastSyncTime?: string;
}

// =============================================================================
// COLLABORATION TYPES
// =============================================================================

export interface ShareableCalculation {
  id: string;
  shareToken: string;
  permissions: 'view' | 'edit' | 'comment';
  expiresAt?: string;
  accessCount: number;
  maxAccess?: number;
}

export interface CollaborationComment {
  id: string;
  userId: string;
  userName: string;
  message: string;
  timestamp: string;
  field?: string;
  resolved: boolean;
}

// =============================================================================
// PERFORMANCE MONITORING TYPES
// =============================================================================

export interface PerformanceMetrics {
  loadTime: number;
  calculationTime: number;
  renderTime: number;
  memoryUsage: number;
  networkLatency: number;
}

export interface UserAnalytics {
  sessionId: string;
  userId?: string;
  pageViews: string[];
  actions: Array<{
    type: string;
    timestamp: string;
    metadata?: any;
  }>;
  errors: Array<{
    message: string;
    timestamp: string;
    stack?: string;
  }>;
}

// =============================================================================
// ACCESSIBILITY TYPES
// =============================================================================

export interface AccessibilitySettings {
  highContrast: boolean;
  largeText: boolean;
  reduceMotion: boolean;
  screenReader: boolean;
  keyboardNavigation: boolean;
}

export interface KeyboardShortcut {
  key: string;
  modifiers: ('ctrl' | 'alt' | 'shift' | 'meta')[];
  action: string;
  description: string;
  enabled: boolean;
}

// =============================================================================
// HELP AND DOCUMENTATION TYPES
// =============================================================================

export interface HelpArticle {
  id: string;
  title: string;
  content: string;
  category: string;
  tags: string[];
  views: number;
  rating: number;
  lastUpdated: string;
}

export interface FAQ {
  id: string;
  question: string;
  answer: string;
  category: string;
  helpful: number;
  notHelpful: number;
}

export interface TutorialStep {
  id: string;
  title: string;
  description: string;
  selector: string;
  position: 'top' | 'bottom' | 'left' | 'right';
  highlight: boolean;
  action?: 'click' | 'type' | 'wait';
}

// =============================================================================
// UTILITIES AND HELPERS
// =============================================================================

export interface AsyncOperation<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  lastFetched?: string;
}

export interface CacheEntry<T> {
  data: T;
  timestamp: string;
  expiresAt: string;
  key: string;
}

export interface RetryConfig {
  attempts: number;
  delay: number;
  backoff: boolean;
  condition?: (error: any) => boolean;
} 