// Barrel file: shared/api/index.ts
// Expose all domain-specific API singletons through one import path.

import axios from 'axios';
import { BaseAPI } from './baseApi';
import { API_CONFIG } from '../utils/constants';

export interface ApiResponse<T = any> {
  data: T;
  status: number;
  message?: string;
}

export interface ApiError {
  message: string;
  code?: string;
  details?: any;
}

export const apiClient = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request interceptor for authentication
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Handle token refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refreshToken');
        const response = await axios.post('/api/auth/refresh', { refreshToken });
        const { token } = response.data;

        localStorage.setItem('token', token);
        originalRequest.headers.Authorization = `Bearer ${token}`;

        return apiClient(originalRequest);
      } catch (refreshError) {
        // Handle refresh token failure
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Export base API for backward compatibility
export const baseApi = BaseAPI.getInstance();

export { default as AuthAPI } from './authApi';
export { default as UserAPI } from './userApi';
export { default as LeavesAPI } from './leavesApi';
export { default as OrganizationAPI } from './organizationApi';
export { default as TaxationAPI } from './taxationApi';
export { default as ReimbursementService } from './reimbursementService';

// Note: Some services are in JS for now; they'll be converted to TS in later tasks. 