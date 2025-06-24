import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import ErrorBoundary from './components/Common/ErrorBoundary';
import { forceReinitializePlugins } from './utils/pluginInitializer';
import Login from './components/Auth/Login';
import Home from './pages/Home';
import UsersList from './components/User/UsersList';
import UserDetail from './components/User/UserDetail';
import UserEdit from './components/User/UserEdit';
import AddNewUser from './components/User/AddNewUser';
import AttendanceUserList from './components/Attendance/AttendanceUserList';
import ProtectedRoute from './components/Common/ProtectedRoute';
import LWPManagement from './features/lwp/components/LWPManagement';
import ProjectAttributes from './features/project-attributes/components/ProjectAttributes';
import ReimbursementTypes from './components/Reimbursements/ReimbursementTypes';
import MyReimbursements from './components/Reimbursements/MyReimbursements';
import ReimbursementApprovals from './components/Reimbursements/ReimbursementApprovals';
import PublicHolidays from './components/PublicHolidays/PublicHolidays';
import LeaveManagement from './components/Leaves/LeaveManagement';
import AllLeaves from './components/Leaves/AllLeaves';
import CompanyLeaves from './components/CompanyLeaves/CompanyLeaves';
import OrganisationsList from './components/Organisation/OrganisationsList';
import AddNewOrganisation from './components/Organisation/AddNewOrganisation';
import { useCalculatorStore } from './shared/stores/calculatorStore';
import Calculator from './components/Common/Calculator';
import PageLayout from './layout/PageLayout';
import { UserRole } from './shared/types';

// Taxation Pages
import TaxationDashboard from './components/taxation/TaxationDashboard';
import TaxDeclaration from './components/taxation/TaxDeclaration';
import EmployeeTaxDetail from './components/taxation/EmployeeTaxDetail';
import EmployeeSelection from './components/taxation/EmployeeSelection';
import MonthlyProjections from './components/taxation/MonthlyProjections';

// Salary Processing Pages
import SalaryProcessing from './components/SalaryProcessing/SalaryProcessing';

// Reporting Pages
import ReportingDashboard from './components/Reporting/ReportingDashboard';

// Plugin Pages
import PluginDemo from './components/Plugins/PluginDemo';
import PluginManager from './components/Plugins/PluginManager';

// Salary Components Pages
import SalaryComponentsList from './components/SalaryComponents/SalaryComponentsList';
import CreateSalaryComponent from './components/SalaryComponents/CreateSalaryComponent';
import EditSalaryComponent from './components/SalaryComponents/EditSalaryComponent';
import FormulaBuilder from './components/SalaryComponents/FormulaBuilder';
import EmployeeMapping from './components/SalaryComponents/EmployeeMapping';
import AssignComponents from './components/SalaryComponents/AssignComponents';

const AppContent: React.FC = () => {
  const { isCalculatorOpen, closeCalculator } = useCalculatorStore();

  const withLayout = (
    component: React.ReactElement,
    title: string,
    allowedRoles: UserRole[] = []
  ) => (
    <ProtectedRoute allowedRoles={allowedRoles}>
      <PageLayout title={title}>{component}</PageLayout>
    </ProtectedRoute>
  );

  return (
    <>
      <Router>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/login" element={<Login />} />
          <Route path="/home" element={<Home />} />
          
          <Route
            path="/users"
            element={withLayout(<UsersList />, 'Users', ['manager', 'admin', 'superadmin'])}
          />

          <Route
            path="/users/emp/:empId"
            element={withLayout(<UserDetail />, 'User Detail', ['manager', 'admin', 'superadmin'])}
          />

          <Route
            path="/users/emp/:empId/edit"
            element={withLayout(<UserEdit />, 'Edit User', ['manager', 'admin', 'superadmin'])}
          />

          <Route
            path="/users/add"
            element={withLayout(<AddNewUser />, 'Add User', ['manager', 'admin', 'superadmin'])}
          />

          <Route
            path="/attendance"
            element={withLayout(<AttendanceUserList />, 'Attendance', ['manager', 'admin', 'superadmin'])}
          />
          <Route
            path="/company-leaves"
            element={withLayout(<CompanyLeaves />, 'Company Leaves', ['superadmin', 'admin'])}
          />

          <Route
            path="/lwp"
            element={withLayout(<LWPManagement />, 'LWP Management', ['admin', 'superadmin', 'hr'])}
          />
          <Route
            path="/attributes"
            element={withLayout(<ProjectAttributes />, 'Project Attributes', ['superadmin'])}
          />
          <Route
            path="/reimbursement-types"
            element={withLayout(<ReimbursementTypes />, 'Reimbursement Types', ['superadmin'])}
          />
          <Route
            path="/my-reimbursements"
            element={withLayout(<MyReimbursements />, 'My Reimbursements', ['superadmin', 'user'])}
          />
          <Route
            path="/reimbursement-approvals"
            element={withLayout(<ReimbursementApprovals />, 'Reimbursement Approvals', ['manager', 'admin', 'superadmin'])}
          />
          <Route
            path="/public-holidays"
            element={withLayout(<PublicHolidays />, 'Public Holidays', ['admin', 'superadmin'])}
          />
          <Route
            path="/leaves"
            element={withLayout(<LeaveManagement />, 'Leave Management', ['user', 'manager', 'admin', 'superadmin'])}
          />
          <Route
            path="/all-leaves"
            element={withLayout(<AllLeaves />, 'All Leaves', ['manager', 'superadmin'])}
          />
          <Route
            path="/organisations"
            element={withLayout(<OrganisationsList />, 'Organisations', ['superadmin'])}
          />

          <Route
            path="/organisations/add"
            element={withLayout(<AddNewOrganisation />, 'Add Organisation', ['superadmin'])}
          />

          <Route
            path="/organisations/edit/:id"
            element={withLayout(<AddNewOrganisation />, 'Edit Organisation', ['superadmin'])}
          />

          {/* Taxation Routes */}
          <Route
            path="/taxation"
            element={withLayout(<TaxationDashboard />, 'Taxation Dashboard', ['user', 'manager', 'admin', 'superadmin'])}
          />
          <Route
            path="/taxation/declaration"
            element={withLayout(<TaxDeclaration />, 'Tax Declaration', ['user', 'manager', 'admin', 'superadmin'])}
          />
          <Route
            path="/taxation/declaration/:empId"
            element={withLayout(<TaxDeclaration />, 'Tax Declaration', ['admin', 'superadmin'])}
          />
          <Route
            path="/taxation/employee/:empId"
            element={withLayout(<EmployeeTaxDetail />, 'Employee Tax Detail', ['user', 'manager', 'admin', 'superadmin'])}
          />
          <Route
            path="/taxation/employee-selection"
            element={withLayout(<EmployeeSelection />, 'Employee Selection', ['admin', 'superadmin'])}
          />
          <Route
            path="/taxation/monthly-projections"
            element={withLayout(<MonthlyProjections />, 'Monthly Projections', ['user', 'manager', 'admin', 'superadmin'])}
          />
          <Route
            path="/taxation/salary-processing"
            element={withLayout(<SalaryProcessing />, 'Salary Processing', ['admin', 'superadmin'])}
          />

          {/* Reporting Routes */}
          <Route
            path="/reporting"
            element={withLayout(<ReportingDashboard />, 'Reporting & Analytics', ['manager', 'admin', 'superadmin'])}
          />

          {/* Plugin Routes */}
          <Route
            path="/plugin-demo"
            element={withLayout(<PluginDemo />, 'Plugin System Demo', ['admin', 'superadmin'])}
          />
          <Route
            path="/plugin-manager"
            element={withLayout(<PluginManager />, 'Plugin Manager', ['admin', 'superadmin'])}
          />

          {/* Salary Components Routes */}
          <Route
            path="/salary-components"
            element={withLayout(<SalaryComponentsList />, 'Salary Components', ['admin', 'superadmin', 'hr'])}
          />
          <Route
            path="/salary-components/create"
            element={withLayout(<CreateSalaryComponent />, 'Create Salary Component', ['admin', 'superadmin'])}
          />
          <Route
            path="/salary-components/edit/:componentId"
            element={withLayout(<EditSalaryComponent />, 'Edit Salary Component', ['admin', 'superadmin'])}
          />
          <Route
            path="/salary-components/assign"
            element={withLayout(<AssignComponents />, 'Assign Components', ['superadmin'])}
          />
          <Route
            path="/salary-components/formula-builder"
            element={withLayout(<FormulaBuilder />, 'Formula Builder', ['admin', 'superadmin'])}
          />
          <Route
            path="/salary-components/employee-mapping"
            element={withLayout(<EmployeeMapping />, 'Employee Mapping', ['admin', 'superadmin', 'hr'])}
          />
        </Routes>
      </Router>
      
      {/* Global Calculator Component */}
      <Calculator open={isCalculatorOpen} onClose={closeCalculator} />
    </>
  );
};

const App: React.FC = () => {
  useEffect(() => {
    // Force reinitialize plugins on app startup to ensure updated menu items
    forceReinitializePlugins();
  }, []);

  return (
    <ErrorBoundary>
      <AppContent />
    </ErrorBoundary>
  );
};

export default App; 