import { jwtDecode } from 'jwt-decode';
import { TokenData, UserRole } from '../types';
import { STORAGE_KEYS } from './constants';

/**
 * Get authentication token from localStorage
 * @returns Token string or null if not found
 */
export const getToken = (): string | null => {
  return localStorage.getItem(STORAGE_KEYS.TOKEN);
};

/**
 * Alias for getToken for backward compatibility
 * @returns Token string or null if not found
 */
export const getAuthToken = getToken;

/**
 * Decode and validate JWT token
 * @param token - JWT token string
 * @returns Decoded token data or null if invalid
 */
const decodeToken = (token: string): TokenData | null => {
  try {
    return jwtDecode<TokenData>(token);
  } catch (error) {
    // Remove console.error for production - use proper logging
    return null;
  }
};

/**
 * Get user role from JWT token
 * @returns User role or null if not authenticated
 */
export const getUserRole = (): UserRole | null => {
  const token = getToken();
  if (!token) return null;

  const decoded = decodeToken(token);
  if (!decoded?.role) return null;

  return decoded.role.toLowerCase() as UserRole;
};

/**
 * Get user ID from JWT token
 * @returns User ID (employee_id) or null if not authenticated
 */
export const getUserId = (): string | null => {
  const token = getToken();
  if (!token) return null;

  const decoded = decodeToken(token);
  if (!decoded) return null;

  // Backend sets employee_id as primary identifier, fallback to sub if needed
  return decoded.employee_id || decoded.sub || null;
};

/**
 * Get username from JWT token
 * @returns Username or null if not authenticated
 */
export const getUsername = (): string | null => {
  const token = getToken();
  if (!token) return null;

  const decoded = decodeToken(token);
  if (!decoded) return null;

  return decoded.username || null;
};

/**
 * Get hostname from JWT token
 * @returns Hostname or null if not authenticated
 */
export const getHostname = (): string | null => {
  const token = getToken();
  if (!token) return null;

  const decoded = decodeToken(token);
  if (!decoded) return null;

  return decoded.hostname || null;
};

/**
 * Get user permissions from JWT token
 * @returns Array of permissions or empty array if not authenticated
 */
export const getUserPermissions = (): string[] => {
  const token = getToken();
  if (!token) return [];

  const decoded = decodeToken(token);
  if (!decoded) return [];

  return decoded.permissions || [];
};

/**
 * Check if user is currently authenticated
 * @returns True if user has valid token
 */
export const isAuthenticated = (): boolean => {
  const token = getToken();
  if (!token) return false;

  // Optionally check if token is expired
  const decoded = decodeToken(token);
  if (!decoded) return false;

  // Check if token is expired (if exp claim exists)
  if (decoded.exp) {
    const currentTime = Math.floor(Date.now() / 1000);
    return decoded.exp > currentTime;
  }

  return true;
};

/**
 * Set authentication token in localStorage
 * @param token - JWT token string
 */
export const setToken = (token: string): void => {
  localStorage.setItem(STORAGE_KEYS.TOKEN, token);
};

/**
 * Remove authentication token from localStorage
 */
export const removeToken = (): void => {
  localStorage.removeItem(STORAGE_KEYS.TOKEN);
};

/**
 * Get user data from JWT token
 * @returns User data or null if not authenticated
 */
export const getUserData = (): TokenData | null => {
  const token = getToken();
  if (!token) return null;

  return decodeToken(token);
};

/**
 * Check if user has specific role
 * @param requiredRole - Role to check against
 * @returns True if user has the required role
 */
export const hasRole = (requiredRole: UserRole): boolean => {
  const userRole = getUserRole();
  return userRole === requiredRole;
};

/**
 * Check if user has any of the specified roles
 * @param roles - Array of roles to check against
 * @returns True if user has any of the specified roles
 */
export const hasAnyRole = (roles: UserRole[]): boolean => {
  const userRole = getUserRole();
  return userRole ? roles.includes(userRole) : false;
};

/**
 * Check if user has a specific permission
 * @param permission - Permission to check
 * @returns True if user has the permission
 */
export const hasPermission = (permission: string): boolean => {
  const permissions = getUserPermissions();
  return permissions.includes(permission);
};

/**
 * Check if user has any of the specified permissions
 * @param requiredPermissions - Array of permissions to check
 * @returns True if user has any of the specified permissions
 */
export const hasAnyPermission = (requiredPermissions: string[]): boolean => {
  const permissions = getUserPermissions();
  return requiredPermissions.some(permission => permissions.includes(permission));
};

/**
 * Check if user has all of the specified permissions
 * @param requiredPermissions - Array of permissions to check
 * @returns True if user has all of the specified permissions
 */
export const hasAllPermissions = (requiredPermissions: string[]): boolean => {
  const permissions = getUserPermissions();
  return requiredPermissions.every(permission => permissions.includes(permission));
};

/**
 * Get token expiration time
 * @returns Expiration time as Date object or null if not authenticated
 */
export const getTokenExpiration = (): Date | null => {
  const token = getToken();
  if (!token) return null;

  const decoded = decodeToken(token);
  if (!decoded?.exp) return null;

  return new Date(decoded.exp * 1000);
};

/**
 * Get token issued time
 * @returns Issued time as Date object or null if not authenticated
 */
export const getTokenIssuedAt = (): Date | null => {
  const token = getToken();
  if (!token) return null;

  const decoded = decodeToken(token);
  if (!decoded?.iat) return null;

  return new Date(decoded.iat * 1000);
};

/**
 * Get time until token expires in seconds
 * @returns Seconds until expiration or null if not authenticated/no expiration
 */
export const getTimeUntilExpiration = (): number | null => {
  const expirationDate = getTokenExpiration();
  if (!expirationDate) return null;

  const currentTime = new Date().getTime();
  const expirationTime = expirationDate.getTime();
  
  return Math.max(0, Math.floor((expirationTime - currentTime) / 1000));
};

/**
 * Check if token will expire within specified minutes
 * @param minutes - Minutes to check against
 * @returns True if token will expire within the specified time
 */
export const willExpireSoon = (minutes: number = 5): boolean => {
  const timeUntilExpiration = getTimeUntilExpiration();
  if (timeUntilExpiration === null) return false;

  return timeUntilExpiration <= (minutes * 60);
};

/**
 * Get complete authentication context
 * @returns Object with all auth-related data or null if not authenticated
 */
export const getAuthContext = (): {
  isAuthenticated: boolean;
  userId: string | null;
  username: string | null;
  role: UserRole | null;
  hostname: string | null;
  permissions: string[];
  tokenExpiration: Date | null;
  tokenIssuedAt: Date | null;
  timeUntilExpiration: number | null;
  willExpireSoon: boolean;
} | null => {
  if (!isAuthenticated()) {
    return null;
  }

  return {
    isAuthenticated: true,
    userId: getUserId(),
    username: getUsername(),
    role: getUserRole(),
    hostname: getHostname(),
    permissions: getUserPermissions(),
    tokenExpiration: getTokenExpiration(),
    tokenIssuedAt: getTokenIssuedAt(),
    timeUntilExpiration: getTimeUntilExpiration(),
    willExpireSoon: willExpireSoon()
  };
};
