import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import ErrorBoundary from './components/Common/ErrorBoundary';
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
import IndividualComponentManagement from './components/taxation/IndividualComponentManagement';
import ProcessedSalaries from './components/taxation/ProcessedSalaries';
import SalaryProcessing from './components/taxation/SalaryProcessing';

// Individual Component Forms
import SalaryComponentForm from './components/taxation/components/SalaryComponentForm';
import PerquisitesComponentForm from './components/taxation/components/PerquisitesComponentForm';
import DeductionsComponentForm from './components/taxation/components/DeductionsComponentForm';
import HousePropertyComponentForm from './components/taxation/components/HousePropertyComponentForm';
import CapitalGainsComponentForm from './components/taxation/components/CapitalGainsComponentForm';
import RetirementBenefitsComponentForm from './components/taxation/components/RetirementBenefitsComponentForm';
import OtherIncomeComponentForm from './components/taxation/components/OtherIncomeComponentForm';
import ComponentsOverview from './components/taxation/ComponentsOverview';

// Reporting Pages
import ReportingDashboard from './components/Reporting/ReportingDashboard';

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
            path="/taxation/component-management"
            element={withLayout(<IndividualComponentManagement />, 'Individual Component Management', ['admin', 'superadmin'])}
          />
          <Route
            path="/taxation/processed-salaries"
            element={withLayout(<ProcessedSalaries />, 'Processed Salaries', ['admin', 'superadmin'])}
          />
          <Route
            path="/taxation/salary-processing"
            element={withLayout(<SalaryProcessing />, 'Salary Processing Management', ['admin', 'superadmin'])}
          />
          <Route
            path="/taxation/components-overview/:empId"
            element={withLayout(<ComponentsOverview />, 'Components Overview', ['admin', 'superadmin'])}
          />
          
          {/* Individual Component Routes */}
          <Route
            path="/taxation/component/salary/:empId"
            element={withLayout(<SalaryComponentForm />, 'Salary Component Management', ['admin', 'superadmin'])}
          />
          <Route
            path="/taxation/component/salary/new/:empId"
            element={withLayout(<SalaryComponentForm />, 'New Salary Revision', ['admin', 'superadmin'])}
          />
          <Route
            path="/taxation/component/perquisites/:empId"
            element={withLayout(<PerquisitesComponentForm />, 'Perquisites Component Management', ['admin', 'superadmin'])}
          />
          <Route
            path="/taxation/component/perquisites/new/:empId"
            element={withLayout(<PerquisitesComponentForm />, 'New Perquisites Revision', ['admin', 'superadmin'])}
          />
          <Route
            path="/taxation/component/deductions/:empId"
            element={withLayout(<DeductionsComponentForm />, 'Deductions Component Management', ['admin', 'superadmin'])}
          />
          <Route
            path="/taxation/component/deductions/new/:empId"
            element={withLayout(<DeductionsComponentForm />, 'New Deductions Revision', ['admin', 'superadmin'])}
          />
          <Route
            path="/taxation/component/house-property/:empId"
            element={withLayout(<HousePropertyComponentForm />, 'House Property Component Management', ['admin', 'superadmin'])}
          />
          <Route
            path="/taxation/component/capital-gains/:empId"
            element={withLayout(<CapitalGainsComponentForm />, 'Capital Gains Component Management', ['admin', 'superadmin'])}
          />
          <Route
            path="/taxation/component/capital-gains/new/:empId"
            element={withLayout(<CapitalGainsComponentForm />, 'New Capital Gains Revision', ['admin', 'superadmin'])}
          />
          <Route
            path="/taxation/component/retirement-benefits/:empId"
            element={withLayout(<RetirementBenefitsComponentForm />, 'Retirement Benefits Component Management', ['admin', 'superadmin'])}
          />
          <Route
            path="/taxation/component/other-income/:empId"
            element={withLayout(<OtherIncomeComponentForm />, 'Other Income Component Management', ['admin', 'superadmin'])}
          />
          <Route
            path="/taxation/component/retirement-benefits/new/:empId"
            element={withLayout(<RetirementBenefitsComponentForm />, 'New Retirement Benefits Revision', ['admin', 'superadmin'])}
          />
          <Route
            path="/taxation/component/other-income/new/:empId"
            element={withLayout(<OtherIncomeComponentForm />, 'New Other Income Revision', ['admin', 'superadmin'])}
          />

          {/* Reporting Routes */}
          <Route
            path="/reporting"
            element={withLayout(<ReportingDashboard />, 'Reporting & Analytics', ['manager', 'admin', 'superadmin'])}
          />
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
      <AppContent />
    </ErrorBoundary>
  );
};

export default App; 