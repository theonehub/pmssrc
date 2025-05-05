import axios from './axios';

/**
 * Make a standardized API request
 * 
 * @param {Object} options - Request options
 * @param {string} options.method - HTTP method (get, post, put, delete)
 * @param {string} options.url - API endpoint URL
 * @param {Object} [options.data] - Request payload for POST/PUT requests
 * @param {File} [options.file] - Primary file to upload (if any)
 * @param {string} [options.fileField] - Name of the primary file field
 * @param {Object} [options.formData] - Additional form data fields
 * @param {Object} [options.files] - Additional files to upload {fieldName: File}
 * @param {Object} [options.params] - URL query parameters
 * @param {Object} [options.headers] - Additional headers
 * @param {Object} [options.config] - Additional axios config options
 * @returns {Promise} - Axios promise
 */
export const apiRequest = async (options) => {
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
      formDataObj.append(key, value);
    });
    
    // Return the request with multipart/form-data
    return axios({
      method,
      url,
      data: formDataObj,
      params,
      headers: {
        'Content-Type': 'multipart/form-data',
        ...headers
      },
      ...config
    });
  } else {
    // Regular JSON request
    return axios({
      method,
      url,
      data,
      params,
      headers: {
        'Content-Type': 'application/json',
        ...headers
      },
      ...config
    });
  }
};

/**
 * Make a GET request
 */
export const apiGet = (url, params, config = {}) => {
  return apiRequest({ method: 'get', url, params, ...config });
};

/**
 * Make a POST request
 */
export const apiPost = (url, data, config = {}) => {
  return apiRequest({ method: 'post', url, data, ...config });
};

/**
 * Make a PUT request
 */
export const apiPut = (url, data, config = {}) => {
  return apiRequest({ method: 'put', url, data, ...config });
};

/**
 * Make a DELETE request
 */
export const apiDelete = (url, params, config = {}) => {
  return apiRequest({ method: 'delete', url, params, ...config });
};

/**
 * Upload a file with form data
 */
export const apiUpload = (url, file, formData = {}, method = 'post', fileField = 'file') => {
  return apiRequest({
    method,
    url,
    file,
    fileField,
    formData
  });
};

/**
 * Upload multiple files with form data
 */
export const apiUploadMultiple = (url, files = {}, formData = {}, method = 'post') => {
  return apiRequest({
    method,
    url,
    files,
    formData
  });
};

export default {
  request: apiRequest,
  get: apiGet,
  post: apiPost,
  put: apiPut,
  delete: apiDelete,
  upload: apiUpload,
  uploadMultiple: apiUploadMultiple
}; 