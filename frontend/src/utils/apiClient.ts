import axios, {
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
  AxiosError,
  InternalAxiosRequestConfig,
} from 'axios';
import { API_CONFIG, STORAGE_KEYS, ERROR_MESSAGES } from '../constants';
import { ApiResponse } from '../types';

/**
 * Create axios instance with default configuration
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor to add authentication token
 */
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
    try {
      const token = localStorage.getItem(STORAGE_KEYS.TOKEN);
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error in request interceptor:', error);
      }
      throw error;
    }
  },
  (error: AxiosError) => {
    if (process.env.NODE_ENV === 'development') {
      // eslint-disable-next-line no-console
      console.error('Request interceptor error:', error);
    }
    return Promise.reject(error);
  }
);

/**
 * Response interceptor to handle common errors and responses
 */
apiClient.interceptors.response.use(
  (response: AxiosResponse): AxiosResponse => {
    return response;
  },
  async (error: AxiosError) => {
    if (process.env.NODE_ENV === 'development') {
      // eslint-disable-next-line no-console
      console.error('API Error:', error.response?.data || error.message);
    }

    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem(STORAGE_KEYS.TOKEN);
      localStorage.removeItem('user_info'); // Keep for backward compatibility
      
      // Redirect to login page
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    } else if (error.response?.status === 403) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Access forbidden:', error.response?.data);
      }
    } else if (error.response && error.response.status >= 500) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Server error:', error.response.data);
      }
    } else if (error.code === 'ECONNABORTED') {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Request timeout');
      }
    } else if (!error.response) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Network error');
      }
    }

    return Promise.reject(error);
  }
);

/**
 * Generic API request wrapper with type safety
 * @param config - Axios request configuration
 * @returns Promise with typed response
 */
export const apiRequest = async <T = any>(
  config: AxiosRequestConfig
): Promise<ApiResponse<T>> => {
  try {
    const response = await apiClient(config);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ApiResponse>;

      // Return structured error response
      const errorResponse: ApiResponse<T> = {
        success: false,
        error:
          axiosError.response?.data?.error ||
          axiosError.message ||
          ERROR_MESSAGES.NETWORK_ERROR,
      };

      if (axiosError.response?.data?.message) {
        errorResponse.message = axiosError.response.data.message;
      }

      if (axiosError.response?.data?.errors) {
        errorResponse.errors = axiosError.response.data.errors;
      }

      return errorResponse;
    }

    // Handle non-axios errors
    return {
      success: false,
      error:
        error instanceof Error ? error.message : ERROR_MESSAGES.SERVER_ERROR,
    };
  }
};

/**
 * GET request helper
 * @param url - Request URL
 * @param config - Additional axios configuration
 * @returns Promise with typed response
 */
export const get = <T = any>(
  url: string,
  config?: AxiosRequestConfig
): Promise<ApiResponse<T>> => {
  return apiRequest<T>({ ...config, method: 'GET', url });
};

/**
 * POST request helper
 * @param url - Request URL
 * @param data - Request payload
 * @param config - Additional axios configuration
 * @returns Promise with typed response
 */
export const post = <T = any>(
  url: string,
  data?: any,
  config?: AxiosRequestConfig
): Promise<ApiResponse<T>> => {
  return apiRequest<T>({ ...config, method: 'POST', url, data });
};

/**
 * PUT request helper
 * @param url - Request URL
 * @param data - Request payload
 * @param config - Additional axios configuration
 * @returns Promise with typed response
 */
export const put = <T = any>(
  url: string,
  data?: any,
  config?: AxiosRequestConfig
): Promise<ApiResponse<T>> => {
  return apiRequest<T>({ ...config, method: 'PUT', url, data });
};

/**
 * DELETE request helper
 * @param url - Request URL
 * @param config - Additional axios configuration
 * @returns Promise with typed response
 */
export const del = <T = any>(
  url: string,
  config?: AxiosRequestConfig
): Promise<ApiResponse<T>> => {
  return apiRequest<T>({ ...config, method: 'DELETE', url });
};

/**
 * PATCH request helper
 * @param url - Request URL
 * @param data - Request payload
 * @param config - Additional axios configuration
 * @returns Promise with typed response
 */
export const patch = <T = any>(
  url: string,
  data?: any,
  config?: AxiosRequestConfig
): Promise<ApiResponse<T>> => {
  return apiRequest<T>({ ...config, method: 'PATCH', url, data });
};

export default apiClient;
