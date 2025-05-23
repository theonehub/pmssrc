import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000'; // Updated to match your backend

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    try {
      const token = localStorage.getItem('token'); // Changed from AsyncStorage to localStorage
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    } catch (error) {
      return Promise.reject(error);
    }
  },
  (error) => Promise.reject(error)
);

// Add response interceptor to handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('token'); // Changed from AsyncStorage to localStorage
      localStorage.removeItem('user_info');
      // Redirect to login
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient; 