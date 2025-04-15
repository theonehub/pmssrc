import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './Components/Login';
import CreateUser from './Components/CreateUser';
import Home from './Components/Home';
import UsersList from './Components/UsersList';
import ProtectedRoute from './Components/ProtectedRoutes';
import UserImport from './Components/UserImport';
import SalaryComponents from './pages/SalaryComponents';
import DeclareSalary from './Components/DeclareSalary';
import LWPManagement from './Components/LWPManagement';
import ProjectAttributes from './Components/ProjectAttributes';
import ReimbursementTypes from './Components/ReimbursementTypes';
import MyReimbursements from './Components/MyReimbursements';
import ReimbursementAssignmentList from './Components/AssignReimbursement';

//import { isAuthenticated } from './utils/auth';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="declareSalary" element={<DeclareSalary />} />

        <Route path="/" element={
          <ProtectedRoute allowedRoles={['user', 'lead', 'hr', 'admin', 'superadmin']}>
            <Home />
          </ProtectedRoute>
        } />

        <Route path="/register" element={
          <ProtectedRoute allowedRoles={['admin', 'superadmin']}>
            <CreateUser />
          </ProtectedRoute>
        } />

        <Route path="/users" element={
          <ProtectedRoute allowedRoles={['hr', 'admin', 'superadmin']}>
            <UsersList />
          </ProtectedRoute>
        } />

        <Route path="/home" element={
          <ProtectedRoute allowedRoles={['hr', 'admin', 'superadmin']}>
            <Home />
          </ProtectedRoute>
        } />

        <Route path="/import-users" element={
          <ProtectedRoute allowedRoles={['admin', 'superadmin']}>
            <UserImport />
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
          <ProtectedRoute allowedRoles={['superadmin']}>
            <MyReimbursements />
          </ProtectedRoute>
        } />
      </Routes>
    </Router>
  );
}

export default App;
