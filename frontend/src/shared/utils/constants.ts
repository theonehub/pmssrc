// API Configuration
export const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8010',
  TIMEOUT: 30000,
} as const;

// User Roles
export const USER_ROLES = {
  SUPERADMIN: 'superadmin',
  ADMIN: 'admin',
  MANAGER: 'manager',
  HR: 'hr',
  USER: 'user',
} as const;

// Route Paths (Web and Mobile compatible)
export const ROUTES = {
  LOGIN: '/login',
  HOME: '/home',
  USERS: '/users',
  ATTENDANCE: '/attendance',
  LEAVES: '/leaves',
  REIMBURSEMENTS: '/reimbursements',
  TAXATION: '/taxation',
  PAYOUTS: '/payouts',
  ORGANISATIONS: '/organisations',
  // Mobile-specific routes (future)
  MOBILE_HOME: '/mobile/home',
  MOBILE_PROFILE: '/mobile/profile',
} as const;

// File Upload Configuration
export const FILE_CONFIG = {
  MAX_SIZE: {
    PHOTO: 2 * 1024 * 1024, // 2MB
    DOCUMENT: 5 * 1024 * 1024, // 5MB
  },
  ALLOWED_TYPES: {
    PHOTO: ['image/jpeg', 'image/png'] as const,
    DOCUMENT: ['image/jpeg', 'image/png', 'application/pdf'] as const,
  },
} as const;

// Status Types
export const STATUS_TYPES = {
  PENDING: 'pending',
  APPROVED: 'approved',
  REJECTED: 'rejected',
  ACTIVE: 'active',
  INACTIVE: 'inactive',
} as const;

// Leave Types
export const LEAVE_TYPES = {
  CASUAL: 'casual_leave',
  SICK: 'sick_leave',
  EARNED: 'earned_leave',
  MATERNITY: 'maternity_leave',
  PATERNITY: 'paternity_leave',
} as const;

// Theme Colors
export const THEME_COLORS = {
  PRIMARY: '#1976d2',
  SECONDARY: '#9c27b0',
  SUCCESS: '#2e7d32',
  ERROR: '#d32f2f',
  WARNING: '#ed6c02',
  INFO: '#0288d1',
} as const;

// Validation Rules
export const VALIDATION_RULES = {
  EMAIL_REGEX: /^\S+@\S+\.\S+$/,
  MOBILE_REGEX: /^\d{10}$/,
  PAN_REGEX: /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/,
  AADHAR_REGEX: /^\d{12}$/,
  UAN_REGEX: /^\d{12}$/,
  ESI_REGEX: /^\d{10}$/,
  MIN_PASSWORD_LENGTH: 6,
} as const;

// Date Formats
export const DATE_FORMATS = {
  DISPLAY: 'DD/MM/YYYY',
  API: 'YYYY-MM-DD',
  DATETIME: 'DD/MM/YYYY HH:mm',
} as const;

// Pagination
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 10,
  PAGE_SIZE_OPTIONS: [10, 25, 50, 100] as const,
} as const;

// Local Storage Keys
export const STORAGE_KEYS = {
  TOKEN: 'token',
  USER_PREFERENCES: 'userPreferences',
  SIDEBAR_WIDTH: 'sidebarWidth',
  SIDEBAR_OPEN: 'sidebarOpen',
} as const;

// Error Messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  UNAUTHORIZED: 'You are not authorized to perform this action.',
  FORBIDDEN: 'Access denied.',
  NOT_FOUND: 'Resource not found.',
  SERVER_ERROR: 'Internal server error. Please try again later.',
  VALIDATION_ERROR: 'Please check your input and try again.',
} as const;

// Success Messages
export const SUCCESS_MESSAGES = {
  SAVE_SUCCESS: 'Data saved successfully.',
  UPDATE_SUCCESS: 'Data updated successfully.',
  DELETE_SUCCESS: 'Data deleted successfully.',
  UPLOAD_SUCCESS: 'File uploaded successfully.',
} as const;

// Type exports for better type safety
export type UserRole = (typeof USER_ROLES)[keyof typeof USER_ROLES];
export type StatusType = (typeof STATUS_TYPES)[keyof typeof STATUS_TYPES];
export type LeaveType = (typeof LEAVE_TYPES)[keyof typeof LEAVE_TYPES];
export type RouteKey = keyof typeof ROUTES;
