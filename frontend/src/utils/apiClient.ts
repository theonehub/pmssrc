import axios, {
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
  AxiosError,
  InternalAxiosRequestConfig,
} from 'axios';
import { API_CONFIG, STORAGE_KEYS } from '../constants';

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
 * GET request helper
 * @param url - Request URL
 * @param config - Additional axios configuration
 * @returns Promise with typed response (raw backend response)
 */
export const get = async <T = any>(
  url: string,
  config?: AxiosRequestConfig
): Promise<T> => {
  const response = await apiClient.get<T>(url, config);
  return response.data;
};

/**
 * POST request helper
 * @param url - Request URL
 * @param data - Request payload
 * @param config - Additional axios configuration
 * @returns Promise with typed response (raw backend response)
 */
export const post = async <T = any>(
  url: string,
  data?: any,
  config?: AxiosRequestConfig
): Promise<T> => {
  const response = await apiClient.post<T>(url, data, config);
  return response.data;
};

/**
 * PUT request helper
 * @param url - Request URL
 * @param data - Request payload
 * @param config - Additional axios configuration
 * @returns Promise with typed response (raw backend response)
 */
export const put = async <T = any>(
  url: string,
  data?: any,
  config?: AxiosRequestConfig
): Promise<T> => {
  const response = await apiClient.put<T>(url, data, config);
  return response.data;
};

/**
 * DELETE request helper
 * @param url - Request URL
 * @param config - Additional axios configuration
 * @returns Promise with typed response (raw backend response)
 */
export const del = async <T = any>(
  url: string,
  config?: AxiosRequestConfig
): Promise<T> => {
  const response = await apiClient.delete<T>(url, config);
  return response.data;
};

/**
 * PATCH request helper
 * @param url - Request URL
 * @param data - Request payload
 * @param config - Additional axios configuration
 * @returns Promise with typed response (raw backend response)
 */
export const patch = async <T = any>(
  url: string,
  data?: any,
  config?: AxiosRequestConfig
): Promise<T> => {
  const response = await apiClient.patch<T>(url, data, config);
  return response.data;
};

export default apiClient;
