import { post, get } from '../utils/apiClient';
import { setToken, removeToken, getToken } from '../utils/auth';
import { STORAGE_KEYS } from '../constants';
import { LoginCredentials, AuthResponse, User } from '../types';

/**
 * Authentication service for handling login, logout, and user data
 */
class AuthService {
  /**
   * Login user with credentials
   * @param credentials - User login credentials
   * @returns Promise with authentication response
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await post<AuthResponse>('/auth/login', credentials);

      if (!response.success || !response.data) {
        throw new Error(response.error || 'Login failed');
      }

      const { access_token, user } = response.data;

      // Store token and user data
      setToken(access_token);
      if (user) {
        localStorage.setItem('user_info', JSON.stringify(user));
      }

      return response.data;
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
      // Optional: Call logout endpoint to invalidate token on server
      // await post('/auth/logout');

      // Remove token and user data from storage
      removeToken();
      localStorage.removeItem('user_info');
      localStorage.removeItem(STORAGE_KEYS.USER_PREFERENCES);
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Logout error:', error);
      }
      // Still remove local data even if server call fails
      removeToken();
      localStorage.removeItem('user_info');
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
      const response = await get<User>('/auth/me');

      if (response.success && response.data) {
        localStorage.setItem('user_info', JSON.stringify(response.data));
        return response.data;
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
      const response = await post<{ message: string }>(
        '/auth/change-password',
        {
          current_password: currentPassword,
          new_password: newPassword,
        }
      );

      return response.success;
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
      const response = await post<{ message: string }>(
        '/auth/forgot-password',
        {
          email,
        }
      );

      return response.success;
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
      const response = await post<{ message: string }>('/auth/reset-password', {
        token,
        new_password: newPassword,
      });

      return response.success;
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error resetting password:', error);
      }
      throw error;
    }
  }
}

// Export singleton instance
const authService = new AuthService();
export default authService;
