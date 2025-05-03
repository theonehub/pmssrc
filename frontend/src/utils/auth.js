// src/utils/auth.js
import { jwtDecode } from 'jwt-decode';

export const getToken = () => {
  return localStorage.getItem('token');
};

// Alias for getToken for backward compatibility
export const getAuthToken = getToken;

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

export const getUserId = () => {
  const token = getToken();
  if (!token) return null;
  try {
    const decoded = jwtDecode(token);
    return decoded.emp_id || decoded.sub; // Assuming JWT contains emp_id or sub (subject) claim
  } catch (error) {
    console.error("Invalid token:", error);
    return null;
  }
};

export const isAuthenticated = () => {
  return !!getToken();
};