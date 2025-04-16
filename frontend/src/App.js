import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './Components/Auth/Login';
import Home from './pages/Home';
import UsersList from './Components/User/UsersList';
import ProtectedRoute from './Components/Common/ProtectedRoute';
import SalaryComponents from './Components/Salary/SalaryComponents';
import DeclareSalary from './Components/Salary/DeclareSalary';
import LWPManagement from './features/lwp/components/LWPManagement';
import ProjectAttributes from './features/project-attributes/components/ProjectAttributes';
import ReimbursementTypes from './Components/Reimbursements/ReimbursementTypes';
import MyReimbursements from './Components/Reimbursements/MyReimbursements';
import ReimbursementAssignmentList from './Components/Reimbursements/ReimbursementAssignmentList';

//import { isAuthenticated } from './utils/auth';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="declareSalary" element={<DeclareSalary />} />
        <Route path="/home" element={<Home />} />


        <Route path="/" element={
          <ProtectedRoute allowedRoles={['user', 'lead', 'hr', 'admin', 'superadmin']}>
            <Login />
          </ProtectedRoute>
        } />
        <Route path="/users" element={
          <ProtectedRoute allowedRoles={['manager', 'admin', 'superadmin']}>
            <UsersList />
          </ProtectedRoute>
        } />

        <Route path="/salary-components" element={
          <ProtectedRoute allowedRoles={['admin', 'superadmin', 'hr']}>
            <SalaryComponents />
          </ProtectedRoute>
        } />
        <Route path="/lwp" element={
          <ProtectedRoute allowedRoles={['admin', 'superadmin', 'hr']}>
            <LWPManagement />
          </ProtectedRoute>
        } />
        <Route path="/attributes" element={
          <ProtectedRoute allowedRoles={['superadmin']}>
            <ProjectAttributes />
          </ProtectedRoute>
        } />
        <Route path="/reimbursement-types" element={
          <ProtectedRoute allowedRoles={['superadmin']}>
            <ReimbursementTypes />
          </ProtectedRoute>
        } />
        <Route path="/reimbursements-assignment" element={
          <ProtectedRoute allowedRoles={['admin', 'superadmin', 'hr']}>
            <ReimbursementAssignmentList />
          </ProtectedRoute>
        } />
        <Route path="/my-reimbursements" element={
          <ProtectedRoute allowedRoles={['superadmin', 'user']}>
            <MyReimbursements />
          </ProtectedRoute>
        } />
      </Routes>
    </Router>
  );
}

export default App;
