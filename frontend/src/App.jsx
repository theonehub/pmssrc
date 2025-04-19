import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './Components/Auth/Login';
import Home from './pages/Home';
import UsersList from './Components/User/UsersList';
import AttendanceUserList from './Components/Attendence/AttendenceUserList';
import ProtectedRoute from './Components/Common/ProtectedRoute';
import SalaryComponents from './Components/Salary/SalaryComponents';
import DeclareSalary from './Components/Salary/DeclareSalary';
import LWPManagement from './features/lwp/components/LWPManagement';
import ProjectAttributes from './features/project-attributes/components/ProjectAttributes';
import ReimbursementTypes from './Components/Reimbursements/ReimbursementTypes';
import MyReimbursements from './Components/Reimbursements/MyReimbursements';
import ReimbursementAssignmentList from './Components/Reimbursements/ReimbursementAssignmentList';
import PublicHolidays from './Components/PublicHolidays/PublicHolidays';

//import { isAuthenticated } from './utils/auth';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/login" element={<Login />} />
        <Route path="declareSalary" element={<DeclareSalary />} />
        <Route path="/home" element={<Home />} />
       
        <Route path="/users" element={
          <ProtectedRoute allowedRoles={['manager', 'admin', 'superadmin']}>
            <UsersList />
          </ProtectedRoute>
        } />

        <Route path="/attendance" element={
          <ProtectedRoute allowedRoles={['manager', 'admin', 'superadmin']}>
            <AttendanceUserList />
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
        <Route path="/public-holidays" element={
          <ProtectedRoute allowedRoles={['admin', 'superadmin']}>
            <PublicHolidays />
          </ProtectedRoute>
        } />
      </Routes>
    </Router>
  );
}

export default App;
