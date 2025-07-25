import React, { ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';
import { getToken } from '../../shared/utils/auth';
import { UserRole, TokenData } from '../../shared/types';

function getTokenData(): TokenData | null {
  const token = getToken();
  if (!token) return null;

  try {
    return jwtDecode<TokenData>(token);
  } catch (e) {
    // Remove console.error for production
    return null;
  }
}

interface ProtectedRouteProps {
  children: ReactNode;
  allowedRoles?: UserRole[];
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, allowedRoles }) => {
  const tokenData = getTokenData();

  if (!tokenData) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && tokenData.role && !allowedRoles.includes(tokenData.role)) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute; 