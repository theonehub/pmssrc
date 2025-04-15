import React from 'react';
import { Navigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';
import { getToken } from '../../utils/auth'; // Updated path

function getTokenData() {
  const token = getToken(); // Use getToken function
  if (!token) return null;

  try {
    return jwtDecode(token);
  } catch (e) {
    console.error("Invalid token");
    return null;
  }
}

const ProtectedRoute = ({ children, allowedRoles }) => {
  const tokenData = getTokenData();

  if (!tokenData) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(tokenData.role)) {
    return <Navigate to="/" replace />;
  }

  return children;
};

export default ProtectedRoute;