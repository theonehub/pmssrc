import { jwtDecode } from 'jwt-decode';
import { TokenData, UserRole } from '../types';
import { STORAGE_KEYS } from '../constants';

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
 * @returns User ID or null if not authenticated
 */
export const getUserId = (): string | null => {
  const token = getToken();
  if (!token) return null;

  const decoded = decodeToken(token);
  if (!decoded) return null;

  return decoded.emp_id || decoded.sub || null;
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
