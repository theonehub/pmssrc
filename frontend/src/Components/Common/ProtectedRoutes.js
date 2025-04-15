import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { isAuthenticated, getUserRole } from '../utils/auth'; // Adjust the path as necessary
import Navbar from './Navbar';
import Sidebar from '../../layout/Sidebar';
import Topbar from '../../layout/Topbar';
import './ProtectedRoutes.css'; // Optional CSS file

const ProtectedRoute = ({ children, allowedRoles = [] }) => {
  const location = useLocation();
  const isAuth = isAuthenticated();
  const userRole = getUserRole();

  if (!isAuth) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (allowedRoles.length && !allowedRoles.includes(userRole)) {
    return <Navigate to="/home" replace />;
  }

  return (
    <div className="protected-layout">
      <Sidebar />
      <div className="main-content">
        <Topbar />
        <div className="content-area">{children}</div>
      </div>
    </div>
  );
};

export default ProtectedRoute;