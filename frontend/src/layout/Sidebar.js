import React from 'react';
import { useNavigate } from 'react-router-dom';
import { getUserRole } from '../utils/auth';

const Sidebar = () => {
  const role = getUserRole();
  const navigate = useNavigate();

  return (
    <div
      className="bg-dark text-white p-3"
      style={{
        width: '300px',
        minHeight: 'calc(100vh - 56px)',
        overflowY: 'auto',
      }}
    >
      <h5 className="mb-4 text-center">📋 Menu</h5>
      <div className="list-group">
        {(role === 'admin' || role === 'superadmin') && (
          <button
            className="list-group-item list-group-item-action list-group-item-success py-3"
            onClick={() => navigate('/register')}
          >
            <i className="bi bi-person-plus me-2"></i> Create/Register User
          </button>
        )}

        {(role === 'superadmin' || role === 'admin' || role === 'hr') && (
          <button
            className="list-group-item list-group-item-action list-group-item-secondary py-3"
            onClick={() => navigate('/users')}
          >
            <i className="bi bi-people me-2"></i> View All Users
          </button>
        )}

        {(role === 'superadmin' || role === 'admin' || role === 'hr') && (
          <button
            className="list-group-item list-group-item-action list-group-item-info py-3"
            onClick={() => navigate('/salary-components')}
          >
            <i className="bi bi-wallet2 me-2"></i> Salary Components
          </button>
        )}

        {(role === 'user' || role === 'superadmin' || role === 'admin') && (
          <button
            className="list-group-item list-group-item-action list-group-item-warning py-3"
            onClick={() => navigate('/declareSalary')}
          >
            <i className="bi bi-pencil-square me-2"></i> Declare Salary
          </button>
        )}

        {(role === 'superadmin' || role === 'admin') && (
          <button
            className="list-group-item list-group-item-action list-group-item-primary py-3"
            onClick={() => navigate('/lwp')}
          >
            <i className="bi bi-calendar-x me-2"></i> LWP Management
          </button>
        )}

        {role === 'superadmin' && (
          <button
            className="list-group-item list-group-item-action list-group-item-dark py-3"
            onClick={() => navigate('/reimbursement-types')}
          >
            <i className="bi bi-person-plus me-2"></i> Reimbursements-Types
          </button>
        )}

        {(role === 'admin' || role === 'superadmin') && (
          <button
            className="list-group-item list-group-item-action list-group-item-info py-3"
            onClick={() => navigate('/reimbursements-assignment')}
          >
            <i className="bi bi-receipt me-2"></i> Reimbursements-Assignments
          </button>
        )}

        {(role === 'user' || role === 'superadmin') && (
          <button
            className="list-group-item list-group-item-action list-group-item-info py-3"
            onClick={() => navigate('/my-reimbursements')}
          >
            <i className="bi bi-receipt me-2"></i> Reimbursements-Submit
          </button>
        )}

        {role === 'superadmin' && (
          <button
            className="list-group-item list-group-item-action list-group-item-dark py-3"
            onClick={() => navigate('/attributes')}
          >
            <i className="bi bi-gear-fill me-2"></i> Project Attributes
          </button>
        )}

        <button
          className="list-group-item list-group-item-action list-group-item-danger py-3"
          onClick={() => {
            localStorage.removeItem('token');
            navigate('/login');
          }}
        >
          <i className="bi bi-box-arrow-right me-2"></i> Logout
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
