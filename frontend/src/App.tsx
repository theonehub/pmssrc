import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import ErrorBoundary from './Components/Common/ErrorBoundary';
import Login from './Components/Auth/Login';
import Home from './pages/Home';
import UsersList from './Components/User/UsersList';
import UserDetail from './Components/User/UserDetail';
import UserEdit from './Components/User/UserEdit';
import AddNewUser from './Components/User/AddNewUser';
import AttendanceUserList from './Components/Attendance/AttendanceUserList';
import ProtectedRoute from './Components/Common/ProtectedRoute';
import LWPManagement from './features/lwp/components/LWPManagement';
import ProjectAttributes from './features/project-attributes/components/ProjectAttributes';
import ReimbursementTypes from './Components/Reimbursements/ReimbursementTypes';
import MyReimbursements from './Components/Reimbursements/MyReimbursements';
import ReimbursementApprovals from './Components/Reimbursements/ReimbursementApprovals';
import PublicHolidays from './Components/PublicHolidays/PublicHolidays';
import LeaveManagement from './Components/Leaves/LeaveManagement';
import AllLeaves from './Components/Leaves/AllLeaves';
import CompanyLeaves from './Components/CompanyLeaves/CompanyLeaves';
import OrganisationsList from './Components/Organisation/OrganisationsList';
import { CalculatorProvider, useCalculator } from './context/CalculatorContext';
import Calculator from './Components/Common/Calculator';

// Taxation Pages
import TaxationDashboard from './pages/taxation/TaxationDashboard';
import TaxDeclaration from './pages/taxation/TaxDeclaration';
import EmployeeTaxDetail from './pages/taxation/EmployeeTaxDetail';
import EmployeeSelection from './pages/taxation/EmployeeSelection';

// Payout Pages
import MySalaryDetails from './pages/payouts/MySalaryDetails';
import MyPayslips from './pages/payouts/MyPayslips';
import AdminPayouts from './pages/payouts/AdminPayouts';
import PayoutReports from './pages/payouts/PayoutReports';
import MonthlyProcessing from './pages/payouts/MonthlyProcessing';

const AppContent: React.FC = () => {
  const { isCalculatorOpen, closeCalculator } = useCalculator();

  return (
    <>
      <Router>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/login" element={<Login />} />
          <Route path="/home" element={<Home />} />
          
          <Route path="/users" element={
            <ProtectedRoute allowedRoles={['manager', 'admin', 'superadmin']}>
              <UsersList />
            </ProtectedRoute>
          } />

          <Route path="/users/emp/:empId" element={
            <ProtectedRoute allowedRoles={['manager', 'admin', 'superadmin']}>
              <UserDetail />
            </ProtectedRoute>
          } />

          <Route path="/users/emp/:empId/edit" element={
            <ProtectedRoute allowedRoles={['manager', 'admin', 'superadmin']}>
              <UserEdit />
            </ProtectedRoute>
          } />

          <Route path="/users/add" element={
            <ProtectedRoute allowedRoles={['manager', 'admin', 'superadmin']}>
              <AddNewUser />
            </ProtectedRoute>
          } />

          <Route path="/attendance" element={
            <ProtectedRoute allowedRoles={['manager', 'admin', 'superadmin']}>
              <AttendanceUserList />
            </ProtectedRoute>
          } />
          <Route path="/company-leaves" element={
            <ProtectedRoute allowedRoles={['superadmin', 'admin']}>
              <CompanyLeaves />
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
          <Route path="/my-reimbursements" element={
            <ProtectedRoute allowedRoles={['superadmin', 'user']}>
              <MyReimbursements />
            </ProtectedRoute>
          } />
          <Route path="/reimbursement-approvals" element={
            <ProtectedRoute allowedRoles={['manager', 'admin', 'superadmin']}>
              <ReimbursementApprovals />
            </ProtectedRoute>
          } />
          <Route path="/public-holidays" element={
            <ProtectedRoute allowedRoles={['admin', 'superadmin']}>
              <PublicHolidays />
            </ProtectedRoute>
          } />
          <Route path="/leaves" element={
            <ProtectedRoute allowedRoles={['user', 'manager', 'admin', 'superadmin']}>
              <LeaveManagement />
            </ProtectedRoute>
          } />
          <Route path="/all-leaves" element={
            <ProtectedRoute allowedRoles={['manager', 'superadmin']}>
              <AllLeaves />
            </ProtectedRoute>
          } />
          <Route path="/organisations" element={
            <ProtectedRoute allowedRoles={['superadmin']}>
              <OrganisationsList />
            </ProtectedRoute>
          } />

          {/* Taxation Routes */}
          <Route path="/taxation" element={
            <ProtectedRoute allowedRoles={['user', 'manager', 'admin', 'superadmin']}>
              <TaxationDashboard />
            </ProtectedRoute>
          } />
          <Route path="/taxation/declaration" element={
            <ProtectedRoute allowedRoles={['user', 'manager', 'admin', 'superadmin']}>
              <TaxDeclaration />
            </ProtectedRoute>
          } />
          <Route path="/taxation/declaration/:empId" element={
            <ProtectedRoute allowedRoles={['admin', 'superadmin']}>
              <TaxDeclaration />
            </ProtectedRoute>
          } />
          <Route path="/taxation/employee/:empId" element={
            <ProtectedRoute allowedRoles={['user', 'manager', 'admin', 'superadmin']}>
              <EmployeeTaxDetail />
            </ProtectedRoute>
          } />
          <Route path="/taxation/employee-selection" element={
            <ProtectedRoute allowedRoles={['admin', 'superadmin']}>
              <EmployeeSelection />
            </ProtectedRoute>
          } />

          {/* Payout Routes */}
          <Route path="/payouts/my-salary" element={
            <ProtectedRoute allowedRoles={['user', 'manager', 'admin', 'superadmin']}>
              <MySalaryDetails />
            </ProtectedRoute>
          } />
          <Route path="/payouts/my-payslips" element={
            <ProtectedRoute allowedRoles={['user', 'manager', 'admin', 'superadmin']}>
              <MyPayslips />
            </ProtectedRoute>
          } />
          <Route path="/payouts/admin" element={
            <ProtectedRoute allowedRoles={['admin', 'superadmin']}>
              <AdminPayouts />
            </ProtectedRoute>
          } />
          <Route path="/payouts/monthly" element={
            <ProtectedRoute allowedRoles={['admin', 'superadmin']}>
              <MonthlyProcessing />
            </ProtectedRoute>
          } />
          <Route path="/payouts/reports" element={
            <ProtectedRoute allowedRoles={['manager', 'admin', 'superadmin']}>
              <PayoutReports />
            </ProtectedRoute>
          } />
        </Routes>
      </Router>
      
      {/* Global Calculator Component */}
      <Calculator open={isCalculatorOpen} onClose={closeCalculator} />
    </>
  );
};

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <CalculatorProvider>
        <AppContent />
      </CalculatorProvider>
    </ErrorBoundary>
  );
};

export default App; 