import axios, {
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
  AxiosError,
  InternalAxiosRequestConfig,
} from 'axios';

// Platform detection for mobile compatibility
const isWeb = typeof window !== 'undefined';

// Extend the InternalAxiosRequestConfig to include metadata
interface ExtendedAxiosRequestConfig extends InternalAxiosRequestConfig {
  metadata?: {
    requestId: string;
    startTime: number;
  };
}

// Enhanced Storage abstraction for cross-platform compatibility
class StorageManager {
  static getItem(key: string): string | null {
    if (isWeb) {
      return localStorage.getItem(key);
    }
    // TODO: Add React Native AsyncStorage support
    // import AsyncStorage from '@react-native-async-storage/async-storage';
    // return AsyncStorage.getItem(key);
    return null;
  }

  static setItem(key: string, value: string): void {
    if (isWeb) {
      localStorage.setItem(key, value);
    }
    // TODO: Add React Native AsyncStorage support
    // import AsyncStorage from '@react-native-async-storage/async-storage';
    // AsyncStorage.setItem(key, value);
  }

  static removeItem(key: string): void {
    if (isWeb) {
      localStorage.removeItem(key);
    }
    // TODO: Add React Native AsyncStorage support
    // import AsyncStorage from '@react-native-async-storage/async-storage';
    // AsyncStorage.removeItem(key);
  }

  static clear(): void {
    if (isWeb) {
      localStorage.clear();
    }
    // TODO: Add React Native AsyncStorage support
    // import AsyncStorage from '@react-native-async-storage/async-storage';
    // AsyncStorage.clear();
  }
}

// API Configuration
const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
} as const;

// Storage Keys
const STORAGE_KEYS = {
  TOKEN: 'token',
  REFRESH_TOKEN: 'refresh_token',
  USER_INFO: 'user_info',
  USER_PREFERENCES: 'userPreferences',
} as const;

// Error types
export interface APIError {
  message: string;
  status?: number;
  code?: string;
  details?: any;
}

// Request retry configuration
interface RetryConfig {
  attempts: number;
  delay: number;
  condition?: (error: AxiosError) => boolean;
}

export interface BaseApiConfig {
  baseURL?: string;
  headers?: Record<string, string>;
  timeout?: number;
}

/**
 * Enhanced BaseAPI class for cross-platform compatibility
 * Supports both Web (React) and Mobile (React Native)
 * Features: Authentication, Error Handling, Retry Logic, Platform Detection
 */
export class BaseAPI {
  private static instance: BaseAPI;
  private axiosInstance: AxiosInstance;
  private isRefreshing = false;
  private failedQueue: Array<{
    resolve: (value: any) => void;
    reject: (error: any) => void;
  }> = [];

  private constructor() {
    this.axiosInstance = axios.create({
      baseURL: API_CONFIG.BASE_URL,
      timeout: API_CONFIG.TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
        'X-Platform': isWeb ? 'web' : 'mobile',
        'X-Client-Version': process.env.REACT_APP_VERSION || '1.0.0',
      },
    });

    this.setupInterceptors();
  }

  public static getInstance(): BaseAPI {
    if (!BaseAPI.instance) {
      BaseAPI.instance = new BaseAPI();
    }
    return BaseAPI.instance;
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.axiosInstance.interceptors.request.use(
      (config: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
        try {
          const token = StorageManager.getItem(STORAGE_KEYS.TOKEN);
          if (token && config.headers) {
            config.headers.Authorization = `Bearer ${token}`;
          }

          // Add request ID for tracking
          const extendedConfig = config as ExtendedAxiosRequestConfig;
          extendedConfig.metadata = {
            requestId: this.generateRequestId(),
            startTime: Date.now(),
          };

          if (process.env.NODE_ENV === 'development') {
            console.log(`🚀 API Request [${extendedConfig.metadata.requestId}]:`, {
              method: config.method?.toUpperCase(),
              url: config.url,
              data: config.data,
            });
          }

          return config;
        } catch (error) {
          if (process.env.NODE_ENV === 'development') {
            console.error('Error in request interceptor:', error);
          }
          throw error;
        }
      },
      (error: AxiosError) => {
        if (process.env.NODE_ENV === 'development') {
          console.error('Request interceptor error:', error);
        }
        return Promise.reject(error);
      }
    );

    // Response interceptor with token refresh logic
    this.axiosInstance.interceptors.response.use(
      (response: AxiosResponse): AxiosResponse => {
        if (process.env.NODE_ENV === 'development') {
          const extendedConfig = response.config as ExtendedAxiosRequestConfig;
          const requestId = extendedConfig.metadata?.requestId;
          const duration = Date.now() - (extendedConfig.metadata?.startTime || 0);
          console.log(`✅ API Response [${requestId}]:`, {
            status: response.status,
            duration: `${duration}ms`,
            data: response.data,
          });
        }
        return response;
      },
      async (error: AxiosError) => {
        const originalRequest = error.config as ExtendedAxiosRequestConfig & { _retry?: boolean };

        if (process.env.NODE_ENV === 'development') {
          const requestId = originalRequest?.metadata?.requestId;
          console.error(`❌ API Error [${requestId}]:`, {
            status: error.response?.status,
            message: error.message,
            data: error.response?.data,
          });
        }

        // Handle 401 errors with token refresh
        if (error.response?.status === 401 && !originalRequest._retry) {
          if (this.isRefreshing) {
            // If already refreshing, queue the request
            return new Promise((resolve, reject) => {
              this.failedQueue.push({ resolve, reject });
            }).then((token) => {
              if (originalRequest.headers) {
                originalRequest.headers.Authorization = `Bearer ${token}`;
              }
              return this.axiosInstance(originalRequest);
            }).catch((err) => {
              return Promise.reject(err);
            });
          }

          originalRequest._retry = true;
          this.isRefreshing = true;

          try {
            const refreshToken = StorageManager.getItem(STORAGE_KEYS.REFRESH_TOKEN);
            if (refreshToken) {
              const newToken = await this.refreshAuthToken(refreshToken);
              this.processQueue(null, newToken);
              
              if (originalRequest.headers) {
                originalRequest.headers.Authorization = `Bearer ${newToken}`;
              }
              return this.axiosInstance(originalRequest);
            }
          } catch (refreshError) {
            this.processQueue(refreshError, null);
            this.handleAuthFailure();
          } finally {
            this.isRefreshing = false;
          }
        }

        // Handle other error types
        this.handleApiError(error);
        return Promise.reject(this.formatError(error));
      }
    );
  }

  private async refreshAuthToken(refreshToken: string): Promise<string> {
    try {
      const response = await axios.post(`${API_CONFIG.BASE_URL}/api/v2/auth/refresh`, {
        refresh_token: refreshToken,
      });
      
      const { access_token, refresh_token: newRefreshToken } = response.data;
      
      StorageManager.setItem(STORAGE_KEYS.TOKEN, access_token);
      if (newRefreshToken) {
        StorageManager.setItem(STORAGE_KEYS.REFRESH_TOKEN, newRefreshToken);
      }
      
      return access_token;
    } catch (error) {
      throw error;
    }
  }

  private processQueue(error: any, token: string | null) {
    this.failedQueue.forEach(({ resolve, reject }) => {
      if (error) {
        reject(error);
      } else {
        resolve(token);
      }
    });
    
    this.failedQueue = [];
  }

  private handleAuthFailure(): void {
    // Clear all auth data
    StorageManager.removeItem(STORAGE_KEYS.TOKEN);
    StorageManager.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
    StorageManager.removeItem(STORAGE_KEYS.USER_INFO);
    
    // Platform-specific navigation
    if (isWeb && window.location.pathname !== '/login') {
      window.location.href = '/login';
    }
    // TODO: Add React Native navigation logic
    // NavigationService.navigate('Login');
  }

  private handleApiError(error: AxiosError): void {
    if (error.response?.status === 403) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Access forbidden:', error.response?.data);
      }
    } else if (error.response && error.response.status >= 500) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Server error:', error.response.data);
      }
    } else if (error.code === 'ECONNABORTED') {
      if (process.env.NODE_ENV === 'development') {
        console.error('Request timeout');
      }
    } else if (!error.response) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Network error');
      }
    }
  }

  private formatError(error: AxiosError): APIError {
    const apiError: APIError = {
      message: (error.response?.data as any)?.detail || error.message || 'An unexpected error occurred',
      details: error.response?.data,
    };

    // Only add optional properties if they have values
    if (error.response?.status) {
      apiError.status = error.response.status;
    }
    
    if (error.code) {
      apiError.code = error.code;
    }

    return apiError;
  }

  private generateRequestId(): string {
    return Math.random().toString(36).substr(2, 9);
  }

  /**
   * Request with retry logic
   */
  private async requestWithRetry<T>(
    config: AxiosRequestConfig,
    retryConfig: RetryConfig = {
      attempts: API_CONFIG.RETRY_ATTEMPTS,
      delay: API_CONFIG.RETRY_DELAY,
    }
  ): Promise<T> {
    let lastError: AxiosError | undefined;

    for (let attempt = 1; attempt <= retryConfig.attempts; attempt++) {
      try {
        const response = await this.axiosInstance.request<T>(config);
        return response.data;
      } catch (error) {
        lastError = error as AxiosError;

        // Don't retry on certain conditions
        if (
          lastError.response?.status === 401 ||
          lastError.response?.status === 403 ||
          lastError.response?.status === 404 ||
          (retryConfig.condition && !retryConfig.condition(lastError))
        ) {
          throw lastError;
        }

        if (attempt < retryConfig.attempts) {
          await this.delay(retryConfig.delay * attempt);
          if (process.env.NODE_ENV === 'development') {
            console.log(`🔄 Retrying request (attempt ${attempt + 1}/${retryConfig.attempts})`);
          }
        }
      }
    }

    throw lastError || new Error('Request failed after all retry attempts');
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * GET request helper
   */
  public async get<T = any>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<T> {
    return this.requestWithRetry<T>({ ...config, method: 'GET', url });
  }

  /**
   * POST request helper
   */
  public async post<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response = await this.axiosInstance.post<T>(url, data, config);
    return response.data;
  }

  /**
   * PUT request helper
   */
  public async put<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response = await this.axiosInstance.put<T>(url, data, config);
    return response.data;
  }

  /**
   * DELETE request helper
   */
  public async delete<T = any>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response = await this.axiosInstance.delete<T>(url, config);
    return response.data;
  }

  /**
   * PATCH request helper
   */
  public async patch<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response = await this.axiosInstance.patch<T>(url, data, config);
    return response.data;
  }

  /**
   * Upload file helper
   */
  public async upload<T = any>(
    url: string,
    formData: FormData,
    onUploadProgress?: (progressEvent: any) => void
  ): Promise<T> {
    const config: AxiosRequestConfig = {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    };
    
    if (onUploadProgress) {
      config.onUploadProgress = onUploadProgress;
    }
    
    const response = await this.axiosInstance.post<T>(url, formData, config);
    return response.data;
  }

  /**
   * Download file helper
   */
  public async download(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<Blob> {
    const response = await this.axiosInstance.get(url, {
      ...config,
      responseType: 'blob',
    });
    return response.data;
  }

  /**
   * Get current authentication status
   */
  public isAuthenticated(): boolean {
    return !!StorageManager.getItem(STORAGE_KEYS.TOKEN);
  }

  /**
   * Get current user info from storage
   */
  public getCurrentUser(): any {
    try {
      const userInfo = StorageManager.getItem(STORAGE_KEYS.USER_INFO);
      return userInfo ? JSON.parse(userInfo) : null;
    } catch (error) {
      console.error('Error parsing user info:', error);
      return null;
    }
  }

  /**
   * Clear all authentication data
   */
  public clearAuth(): void {
    StorageManager.removeItem(STORAGE_KEYS.TOKEN);
    StorageManager.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
    StorageManager.removeItem(STORAGE_KEYS.USER_INFO);
    
    // Clear authorization header
    delete this.axiosInstance.defaults.headers.common['Authorization'];
  }

  public getBaseURL(): string {
    return API_CONFIG.BASE_URL;
  }
}

// Create singleton instance
export const apiClient = BaseAPI.getInstance();

// Export individual methods for backward compatibility
export const get = <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> =>
  apiClient.get<T>(url, config);

export const post = <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> =>
  apiClient.post<T>(url, data, config);

export const put = <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> =>
  apiClient.put<T>(url, data, config);

export const del = <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> =>
  apiClient.delete<T>(url, config);

export const patch = <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> =>
  apiClient.patch<T>(url, data, config);

export const upload = <T = any>(url: string, formData: FormData, onUploadProgress?: (progressEvent: any) => void): Promise<T> =>
  apiClient.upload<T>(url, formData, onUploadProgress);

export const download = (url: string, config?: AxiosRequestConfig): Promise<Blob> =>
  apiClient.download(url, config);

export default apiClient; 