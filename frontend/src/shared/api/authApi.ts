import { BaseAPI } from './baseApi';
import { STORAGE_KEYS } from '../utils/constants';

// Platform-agnostic storage manager
class StorageManager {
  static getItem(key: string): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(key);
    }
    // TODO: Add React Native AsyncStorage support
    return null;
  }

  static setItem(key: string, value: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem(key, value);
    }
    // TODO: Add React Native AsyncStorage support
  }

  static removeItem(key: string): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(key);
    }
    // TODO: Add React Native AsyncStorage support
  }
}

// Type definitions
interface LoginCredentials {
  email: string;
  password: string;
  remember_me?: boolean;
}

interface AuthResponse {
  access_token: string;
  user_info: User;
  permissions: string[];
  refresh_token?: string;
}

interface User {
  employee_id: string;
  name: string;
  email: string;
  role: string;
  department?: string;
  position?: string;
  permissions?: string[];
}

interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

interface PasswordResetRequest {
  email: string;
}

interface PasswordResetConfirm {
  token: string;
  new_password: string;
}

/**
 * Enhanced Authentication API using BaseAPI pattern
 * Supports both Web and Mobile platforms
 */
class AuthAPI {
  private static instance: AuthAPI;
  private baseApi: BaseAPI;

  private constructor() {
    this.baseApi = BaseAPI.getInstance();
  }

  public static getInstance(): AuthAPI {
    if (!AuthAPI.instance) {
      AuthAPI.instance = new AuthAPI();
    }
    return AuthAPI.instance;
  }

  /**
   * Login user with credentials
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await this.baseApi.post<AuthResponse>('/v2/auth/login', credentials);

      if (!response.access_token) {
        throw new Error('Invalid login response');
      }

      // Store authentication data
      this.storeAuthData(response);

      return response;
    } catch (error: any) {
      console.error('Login error:', error);
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  }

  /**
   * Logout current user
   */
  async logout(logoutAllDevices: boolean = false): Promise<void> {
    try {
      await this.baseApi.post('/v2/auth/logout', { 
        logout_all_devices: logoutAllDevices 
      });
    } catch (error) {
      console.error('Logout API error:', error);
      // Continue with local cleanup even if API call fails
    } finally {
      this.clearAuthData();
    }
  }

  /**
   * Get current user profile
   */
  async getCurrentUserProfile(): Promise<User> {
    try {
      const response = await this.baseApi.get<User>('/v2/auth/me');
      
      // Update stored user info
      if (response) {
        StorageManager.setItem('user_info', JSON.stringify(response));
      }
      
      return response;
    } catch (error: any) {
      console.error('Error fetching user profile:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch user profile');
    }
  }

  /**
   * Change password
   */
  async changePassword(passwordData: ChangePasswordRequest): Promise<{ message: string }> {
    try {
      const response = await this.baseApi.post<{ message: string }>(
        '/v2/auth/change-password',
        passwordData
      );
      return response;
    } catch (error: any) {
      console.error('Change password error:', error);
      throw new Error(error.response?.data?.detail || 'Failed to change password');
    }
  }

  /**
   * Request password reset
   */
  async requestPasswordReset(resetData: PasswordResetRequest): Promise<{ message: string }> {
    try {
      const response = await this.baseApi.post<{ message: string }>(
        '/v2/auth/password-reset',
        resetData
      );
      return response;
    } catch (error: any) {
      console.error('Password reset request error:', error);
      throw new Error(error.response?.data?.detail || 'Failed to request password reset');
    }
  }

  /**
   * Confirm password reset
   */
  async confirmPasswordReset(resetData: PasswordResetConfirm): Promise<{ message: string }> {
    try {
      const response = await this.baseApi.post<{ message: string }>(
        '/v2/auth/password-reset/confirm',
        resetData
      );
      return response;
    } catch (error: any) {
      console.error('Change password error:', error);
      throw new Error(error.response?.data?.detail || 'Failed to reset password');
    }
  }

  /**
   * Refresh authentication token
   */
  async refreshToken(): Promise<AuthResponse> {
    try {
      const refreshToken = StorageManager.getItem('refresh_token');
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await this.baseApi.post<AuthResponse>('/v2/auth/refresh', {
        refresh_token: refreshToken
      });

      // Update stored authentication data
      this.storeAuthData(response);

      return response;
    } catch (error: any) {
      console.error('Token refresh error:', error);
      // Clear auth data on refresh failure
      this.clearAuthData();
      throw new Error(error.response?.data?.detail || 'Failed to refresh token');
    }
  }

  /**
   * Validate current token
   */
  async validateToken(): Promise<boolean> {
    try {
      await this.baseApi.get('/v2/auth/validate');
      return true;
    } catch (error) {
      console.error('Token validation error:', error);
      return false;
    }
  }

  /**
   * Get session information
   */
  async getSessionInfo(): Promise<any> {
    try {
      const response = await this.baseApi.get('/v2/auth/session');
      return response;
    } catch (error: any) {
      console.error('Session info error:', error);
      throw new Error(error.response?.data?.detail || 'Failed to get session info');
    }
  }

  // Utility methods for authentication state management

  /**
   * Store authentication data securely
   */
  private storeAuthData(authResponse: AuthResponse): void {
    const { access_token, user_info, permissions, refresh_token } = authResponse;

    StorageManager.setItem(STORAGE_KEYS.TOKEN, access_token);
    
    if (refresh_token) {
      StorageManager.setItem('refresh_token', refresh_token);
    }

    if (user_info) {
      const userForStorage = {
        employee_id: user_info.employee_id,
        name: user_info.name,
        email: user_info.email,
        role: user_info.role,
        department: user_info.department,
        position: user_info.position,
        permissions: permissions
      };
      StorageManager.setItem('user_info', JSON.stringify(userForStorage));
    }

    if (permissions) {
      StorageManager.setItem('user_permissions', JSON.stringify(permissions));
    }
  }

  /**
   * Clear all authentication data
   */
  private clearAuthData(): void {
    StorageManager.removeItem(STORAGE_KEYS.TOKEN);
    StorageManager.removeItem('refresh_token');
    StorageManager.removeItem('user_info');
    StorageManager.removeItem('user_permissions');
    StorageManager.removeItem(STORAGE_KEYS.USER_PREFERENCES);
  }

  /**
   * Get current user from storage
   */
  getCurrentUser(): User | null {
    try {
      const userData = StorageManager.getItem('user_info');
      return userData ? JSON.parse(userData) : null;
    } catch (error) {
      console.error('Error getting current user:', error);
      return null;
    }
  }

  /**
   * Get user permissions from storage
   */
  getUserPermissions(): string[] {
    try {
      const permissions = StorageManager.getItem('user_permissions');
      return permissions ? JSON.parse(permissions) : [];
    } catch (error) {
      console.error('Error getting user permissions:', error);
      return [];
    }
  }

  /**
   * Check if user has specific permission
   */
  hasPermission(permission: string): boolean {
    const permissions = this.getUserPermissions();
    return permissions.includes(permission);
  }

  /**
   * Check if user has any of the specified roles
   */
  hasRole(roles: string[]): boolean {
    const user = this.getCurrentUser();
    return user ? roles.includes(user.role) : false;
  }

  /**
   * Check if user is currently authenticated
   */
  isAuthenticated(): boolean {
    try {
      const token = StorageManager.getItem(STORAGE_KEYS.TOKEN);
      return !!token;
    } catch (error) {
      console.error('Error checking authentication:', error);
      return false;
    }
  }

  /**
   * Get authentication token
   */
  getToken(): string | null {
    return StorageManager.getItem(STORAGE_KEYS.TOKEN);
  }
}

// Export singleton instance
export const authApi = AuthAPI.getInstance();
export default authApi;

// Export types for use in components
export type {
  LoginCredentials,
  AuthResponse,
  User,
  ChangePasswordRequest,
  PasswordResetRequest,
  PasswordResetConfirm
}; 