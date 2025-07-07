import { post, get } from './baseApi';
import { setToken, removeToken, getToken } from '../utils/auth';
import { STORAGE_KEYS } from '../utils/constants';
import { LoginCredentials, AuthResponse, User } from '../types';

/**
 * Authentication service for handling login, logout, and user data
 * Updated to use v2 API endpoints
 */
class AuthService {
  /**
   * Login user with credentials
   * @param credentials - User login credentials
   * @returns Promise with authentication response
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      // Updated to use v2 API endpoint
      const response = await post<AuthResponse>('/api/v2/auth/login', credentials);

      // Accept direct backend response (not wrapped in { success, data })
      if (!response.access_token) {
        throw new Error('Login failed');
      }

      const { access_token, user_info, permissions } = response;

      // Store token and user data (updated format)
      setToken(access_token);
      if (user_info) {
        // Store user info in the expected format for compatibility
        const userForStorage = {
          employee_id: user_info.employee_id,
          name: user_info.name,
          email: user_info.email,
          role: user_info.role,
          department: user_info.department,
          position: user_info.position,
          permissions: permissions
        };
        localStorage.setItem('user_info', JSON.stringify(userForStorage));
        localStorage.setItem('user_permissions', JSON.stringify(permissions));
      }

      return response;
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Login error:', error);
      }
      // Re-throw the error to be handled by the calling component
      throw error;
    }
  }

  /**
   * Logout current user
   * @returns Promise that resolves when logout is complete
   */
  async logout(): Promise<void> {
    try {
      // Call v2 logout endpoint to invalidate token on server
      await post('/api/v2/auth/logout', { logout_all_devices: false });

      // Remove token and user data from storage
      removeToken();
      localStorage.removeItem('user_info');
      localStorage.removeItem('user_permissions');
      localStorage.removeItem(STORAGE_KEYS.USER_PREFERENCES);
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Logout error:', error);
      }
      // Still remove local data even if server call fails
      removeToken();
      localStorage.removeItem('user_info');
      localStorage.removeItem('user_permissions');
      localStorage.removeItem(STORAGE_KEYS.USER_PREFERENCES);
    }
  }

  /**
   * Get current user data from storage
   * @returns User data or null if not found
   */
  getCurrentUser(): User | null {
    try {
      const userData = localStorage.getItem('user_info');
      return userData ? JSON.parse(userData) : null;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error getting current user:', error);
      }
      return null;
    }
  }

  /**
   * Get user permissions from storage
   * @returns Array of permissions or empty array if not found
   */
  getUserPermissions(): string[] {
    try {
      const permissions = localStorage.getItem('user_permissions');
      return permissions ? JSON.parse(permissions) : [];
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error getting user permissions:', error);
      }
      return [];
    }
  }

  /**
   * Check if user has specific permission
   * @param permission - Permission to check
   * @returns True if user has the permission
   */
  hasPermission(permission: string): boolean {
    const permissions = this.getUserPermissions();
    return permissions.includes(permission);
  }

  /**
   * Check if user is currently authenticated
   * @returns True if user has valid token
   */
  isAuthenticated(): boolean {
    try {
      const token = getToken();
      return !!token;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error checking authentication:', error);
      }
      return false;
    }
  }

  /**
   * Refresh user data from server
   * @returns Promise with updated user data
   */
  async refreshUserData(): Promise<User | null> {
    try {
      // Get user data from user endpoint which includes profile picture
      const response = await get<any>('/api/v2/users/me');

      if (response) {
        // Map the response to include profile_picture field
        const userData: User = {
          id: response.employee_id || '',
          email: response.email || '',
          name: response.name || '',
          role: response.role || 'user',
          employee_id: response.employee_id || '',
          department: response.department || '',
          designation: response.designation || '',
          mobile: response.mobile || '',
          gender: response.gender || '',
          date_of_joining: response.date_of_joining || '',
          date_of_birth: response.date_of_birth || '',
          address: response.address || '',
          phone: response.phone || '',
          status: response.status || '',
          created_at: response.created_at || '',
          updated_at: response.updated_at || '',
          position: response.position || '',
          profile_picture: response.photo_path || '', // Map photo_path to profile_picture
        };
        
        localStorage.setItem('user_info', JSON.stringify(userData));
        return userData;
      }

      return null;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error refreshing user data:', error);
      }
      return null;
    }
  }

  /**
   * Change user password
   * @param currentPassword - Current password
   * @param newPassword - New password
   * @returns Promise with success status
   */
  async changePassword(
    currentPassword: string,
    newPassword: string
  ): Promise<boolean> {
    try {
      // Updated to use v2 API endpoint
      const response = await post<{ message: string }>(
        '/api/v2/auth/change-password',
        {
          current_password: currentPassword,
          new_password: newPassword,
          confirm_password: newPassword,
        }
      );

      return !!response.message;
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error changing password:', error);
      }
      throw error;
    }
  }

  /**
   * Request password reset
   * @param email - User email
   * @returns Promise with success status
   */
  async requestPasswordReset(email: string): Promise<boolean> {
    try {
      // Updated to use v2 API endpoint
      const response = await post<{ message: string }>(
        '/api/v2/auth/reset-password',
        {
          email,
        }
      );

      return !!response.message;
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error requesting password reset:', error);
      }
      throw error;
    }
  }

  /**
   * Reset password with token
   * @param token - Reset token
   * @param newPassword - New password
   * @returns Promise with success status
   */
  async resetPassword(token: string, newPassword: string): Promise<boolean> {
    try {
      // Updated to use v2 API endpoint
      const response = await post<{ message: string }>('/api/v2/auth/reset-password/confirm', {
        reset_token: token,
        new_password: newPassword,
      });

      return !!response.message;
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error resetting password:', error);
      }
      throw error;
    }
  }

  /**
   * Validate current token
   * @returns Promise with validation status
   */
  async validateToken(): Promise<boolean> {
    try {
      const token = getToken();
      if (!token) return false;

      // Use v2 API endpoint for token validation
      const response = await post<{ is_valid: boolean }>('/api/v2/auth/validate');
      
      return response.is_valid === true;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error validating token:', error);
      }
      return false;
    }
  }

  /**
   * Get session information
   * @returns Promise with session data
   */
  async getSessionInfo(): Promise<any> {
    try {
      // Use v2 API endpoint for session info
      const response = await get<any>('/api/v2/auth/session');
      
      return response || null;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error getting session info:', error);
      }
      return null;
    }
  }

  /**
   * Refresh access token
   * @param refreshToken - Refresh token
   * @returns Promise with new token data
   */
  async refreshToken(refreshToken: string): Promise<any> {
    try {
      // Use v2 API endpoint for token refresh
      const response = await post<any>('/api/v2/auth/refresh', {
        refresh_token: refreshToken
      });
      
      if (response?.access_token) {
        setToken(response.access_token);
      }
      
      return response;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error refreshing token:', error);
      }
      throw error;
    }
  }
}

// Export singleton instance
const authService = new AuthService();
export default authService;
