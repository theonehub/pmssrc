import axios, { AxiosRequestConfig, AxiosResponse } from 'axios';

// Type definitions for API utilities
interface ApiRequestOptions {
  method: 'get' | 'post' | 'put' | 'delete' | 'patch';
  url: string;
  data?: any;
  file?: File;
  fileField?: string;
  formData?: Record<string, any>;
  files?: Record<string, File>;
  params?: Record<string, any>;
  headers?: Record<string, string>;
  responseType?: 'json' | 'blob' | 'text' | 'stream';
}

/**
 * Make a standardized API request
 * @param options - Request options
 * @returns Promise with axios response
 */
export const apiRequest = async (
  options: ApiRequestOptions
): Promise<AxiosResponse> => {
  const {
    method,
    url,
    data,
    file,
    fileField = 'file',
    formData = {},
    files = {},
    params,
    headers = {},
    responseType = 'json',
    ...config
  } = options;

  // Choose correct content type and prepare data
  if (file || Object.keys(files).length > 0) {
    // Handle file uploads using FormData
    const formDataObj = new FormData();

    // Add the primary file if provided
    if (file) {
      formDataObj.append(fileField, file);
    }

    // Add additional files if provided
    Object.entries(files).forEach(([key, fileObj]) => {
      if (fileObj) {
        formDataObj.append(key, fileObj);
      }
    });

    // Add other form fields
    Object.entries(formData).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        formDataObj.append(key, String(value));
      }
    });

    // Return the request with multipart/form-data
    return axios({
      method,
      url,
      data: formDataObj,
      params,
      headers: {
        'Content-Type': 'multipart/form-data',
        ...headers,
      },
      responseType,
      ...config,
    } as AxiosRequestConfig);
  } else {
    // Regular JSON request
    return axios({
      method,
      url,
      data,
      params,
      headers: {
        'Content-Type': 'application/json',
        ...headers,
      },
      responseType,
      ...config,
    } as AxiosRequestConfig);
  }
};

/**
 * Make a GET request
 * @param url - API endpoint URL
 * @param params - URL query parameters
 * @param config - Additional axios config
 * @returns Promise with axios response
 */
export const apiGet = (
  url: string,
  params?: Record<string, any>,
  config: Partial<ApiRequestOptions> = {}
): Promise<AxiosResponse> => {
  return apiRequest({ method: 'get', url, params: params || {}, ...config });
};

/**
 * Make a POST request
 * @param url - API endpoint URL
 * @param data - Request payload
 * @param config - Additional axios config
 * @returns Promise with axios response
 */
export const apiPost = (
  url: string,
  data?: any,
  config: Partial<ApiRequestOptions> = {}
): Promise<AxiosResponse> => {
  return apiRequest({ method: 'post', url, data, ...config });
};

/**
 * Make a PUT request
 * @param url - API endpoint URL
 * @param data - Request payload
 * @param config - Additional axios config
 * @returns Promise with axios response
 */
export const apiPut = (
  url: string,
  data?: any,
  config: Partial<ApiRequestOptions> = {}
): Promise<AxiosResponse> => {
  return apiRequest({ method: 'put', url, data, ...config });
};

/**
 * Make a DELETE request
 * @param url - API endpoint URL
 * @param params - URL query parameters
 * @param config - Additional axios config
 * @returns Promise with axios response
 */
export const apiDelete = (
  url: string,
  params?: Record<string, any>,
  config: Partial<ApiRequestOptions> = {}
): Promise<AxiosResponse> => {
  return apiRequest({ method: 'delete', url, params: params || {}, ...config });
};

/**
 * Upload a file with form data
 * @param url - API endpoint URL
 * @param file - File to upload
 * @param formData - Additional form data fields
 * @param method - HTTP method (default: 'post')
 * @param fileField - Name of the file field (default: 'file')
 * @returns Promise with axios response
 */
export const apiUpload = (
  url: string,
  file: File,
  formData: Record<string, any> = {},
  method: 'post' | 'put' = 'post',
  fileField: string = 'file'
): Promise<AxiosResponse> => {
  return apiRequest({
    method,
    url,
    file,
    fileField,
    formData,
  });
};

/**
 * Upload multiple files with form data
 * @param url - API endpoint URL
 * @param files - Files to upload {fieldName: File}
 * @param formData - Additional form data fields
 * @param method - HTTP method (default: 'post')
 * @returns Promise with axios response
 */
export const apiUploadMultiple = (
  url: string,
  files: Record<string, File> = {},
  formData: Record<string, any> = {},
  method: 'post' | 'put' = 'post'
): Promise<AxiosResponse> => {
  return apiRequest({
    method,
    url,
    files,
    formData,
  });
};

// Default export for backward compatibility
const api = {
  request: apiRequest,
  get: apiGet,
  post: apiPost,
  put: apiPut,
  delete: apiDelete,
  upload: apiUpload,
  uploadMultiple: apiUploadMultiple,
};

export default api;
