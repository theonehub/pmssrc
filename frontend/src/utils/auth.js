// src/utils/auth.js
import { jwtDecode } from 'jwt-decode';

export const getToken = () => {
  return localStorage.getItem('token');
};

export const getUserRole = () => {
  const token = getToken();
  if (!token) return null;
  try {
    const decoded = jwtDecode(token);
    return decoded.role?.toLowerCase(); // Assuming your JWT contains a `role` claim
  } catch (error) {
    console.error("Invalid token:", error);
    return null;
  }
};

export const isAuthenticated = () => {
  return !!getToken();
};