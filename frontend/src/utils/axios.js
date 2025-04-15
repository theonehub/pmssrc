// src/utils/axios.js
import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: '/', // change this to your actual backend URL
});

// Optionally, add an interceptor to attach token
axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default axiosInstance;
