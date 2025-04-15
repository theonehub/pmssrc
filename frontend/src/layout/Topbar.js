// src/layout/Topbar.js
import React from 'react';
import { getUserRole } from '../utils/auth';

const Topbar = ({ title }) => {
  const role = getUserRole();

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-primary px-4" style={{ height: '56px' }}>
      <span className="navbar-brand fs-5">{title || '💼 Payroll Management System'}</span>
      <div className="ms-auto text-white">
        Logged in as: <strong>{role?.toUpperCase()}</strong>
      </div>
    </nav>
  );
};

export default Topbar;
