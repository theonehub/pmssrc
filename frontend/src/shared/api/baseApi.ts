import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

interface ApiConfig {
  baseURL: string;
  timeout: number;
  headers: Record<string, string>;
}

interface ApiError {
  message: string;
  status?: number;
  code?: string;
  details?: any;
}

class BaseAPI {
  private axiosInstance: AxiosInstance;
  
  constructor(config: ApiConfig) {
    this.axiosInstance = axios.create(config);
    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor for auth token and platform identification
    this.axiosInstance.interceptors.request.use(
      (config) => {
        const token = this.getAuthToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        
        // Add platform identifier for mobile/web differentiation
        config.headers['X-Platform'] = this.getPlatform();
        config.headers['X-Client-Version'] = this.getClientVersion();
        
        return config;
      },
      (error) => Promise.reject(this.transformError(error))
    );

    // Response interceptor for error handling
    this.axiosInstance.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.handleAuthError();
        }
        return Promise.reject(this.transformError(error));
      }
    );
  }

  private getAuthToken(): string | null {
    try {
      // This will work differently in web vs mobile
      if (typeof window !== 'undefined') {
        // Web environment - use localStorage
        return localStorage.getItem('auth_token') || 
               localStorage.getItem('access_token') ||
               sessionStorage.getItem('auth_token');
      } else {
        // Mobile environment (React Native)
        // Will use AsyncStorage or SecureStore - to be implemented in mobile phase
        return null;
      }
    } catch (error) {
      console.warn('Error retrieving auth token:', error);
      return null;
    }
  }

  private getPlatform(): string {
    if (typeof window !== 'undefined') {
      const userAgent = window.navigator.userAgent;
      if (/Mobile|Android|iPhone|iPad/.test(userAgent)) {
        return 'mobile-web';
      }
      return 'web';
    }
    // In React Native, Platform will be available
    return 'mobile-native';
  }

  private getClientVersion(): string {
    return process.env.REACT_APP_VERSION || '1.0.0';
  }

  private handleAuthError() {
    try {
      // Clear auth tokens
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('access_token');
        sessionStorage.removeItem('auth_token');
        
        // Redirect to login for web
        const currentPath = window.location.pathname;
        if (!currentPath.includes('/login')) {
          window.location.href = `/login?redirect=${encodeURIComponent(currentPath)}`;
        }
      } else {
        // Mobile: Will be handled by navigation system
        // TODO: Implement mobile auth error handling
      }
    } catch (error) {
      console.error('Error handling auth error:', error);
    }
  }

  private transformError(error: any): ApiError {
    if (error.response) {
      // Server responded with error status
      const status = error.response.status;
      const data = error.response.data;
      
      return {
        message: data?.detail || data?.message || `HTTP ${status} Error`,
        status,
        code: data?.code || `HTTP_${status}`,
        details: data
      };
    } else if (error.request) {
      // Network error
      return {
        message: 'Network error - please check your connection',
        code: 'NETWORK_ERROR',
        details: error.request
      };
    } else {
      // Other error
      return {
        message: error.message || 'An unexpected error occurred',
        code: 'UNKNOWN_ERROR',
        details: error
      };
    }
  }

  // Core HTTP methods with error handling
  protected async request<T>(config: AxiosRequestConfig): Promise<T> {
    try {
      const response = await this.axiosInstance.request<T>(config);
      return response.data;
    } catch (error) {
      throw error; // Error is already transformed by interceptor
    }
  }

  protected async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.request<T>({ ...config, method: 'GET', url });
  }

  protected async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.request<T>({ ...config, method: 'POST', url, data });
  }

  protected async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.request<T>({ ...config, method: 'PUT', url, data });
  }

  protected async patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.request<T>({ ...config, method: 'PATCH', url, data });
  }

  protected async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.request<T>({ ...config, method: 'DELETE', url });
  }

  // Utility methods for mobile/web compatibility
  public setAuthToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
    // For mobile, this will be handled differently
  }

  public clearAuthToken(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('access_token');
      sessionStorage.removeItem('auth_token');
    }
    // For mobile, this will be handled differently
  }

  // Health check method
  public async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return this.get('/health');
  }
}

export default BaseAPI;
export type { ApiError, ApiConfig }; 