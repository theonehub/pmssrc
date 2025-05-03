# Payroll Management System Documentation

## Project Overview
This is a Payroll Management System with a React frontend and FastAPI backend. The system manages various aspects of employee management including user management, attendance, leave management, salary components, reimbursements, and more.

## Tech Stack

### Frontend
- **Framework**: React.js
- **UI Libraries**: 
  - Material-UI (MUI) v7.0.2
  - React Bootstrap (inconsistently used in some components)
- **State Management**: React Hooks (useState, useEffect)
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Date Handling**: date-fns v4.1.0
- **Authentication**: JWT (jwt-decode)
- **Other Libraries**: react-toastify, xlsx

### Backend
- **Framework**: FastAPI
- **Database**: MongoDB (pymongo)
- **Authentication**: JWT (python-jose, PyJWT)
- **Password Hashing**: passlib with bcrypt
- **File Handling**: openpyxl

## Project Structure

### Frontend Structure
```
frontend/
├── src/
│   ├── Components/
│   │   ├── Attendence/
│   │   ├── Auth/
│   │   ├── Common/
│   │   ├── CompanyLeaves/
│   │   ├── Leaves/
│   │   ├── Organisation/
│   │   ├── PublicHolidays/
│   │   ├── Reimbursements/
│   │   ├── Salary/
│   │   └── User/
│   ├── features/
│   ├── hooks/
│   ├── layout/
│   ├── models/
│   ├── pages/
│   ├── services/
│   └── utils/
│   ├── App.jsx
│   ├── theme.js
│   └── index.js
```

### Backend Structure
```
backend/
├── app/
│   ├── auth/
│   ├── database/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── tests/
│   ├── uploads/
│   ├── utils/
│   ├── main.py
│   └── config.py
```

## Functionality

### 1. Authentication and Authorization
- Login system with JWT token authentication
- Role-based access control (user, manager, admin, superadmin, hr)
- Protected routes requiring specific roles

### 2. User Management
- User listing/viewing for admins and managers
- User creation and management

### 3. Attendance Management
- Tracking employee attendance
- Attendance reports and management

### 4. Leave Management
- Employee leave requests
- Leave approval workflow
- Leave balance tracking
- Company-wide leave management
- Public holiday management

### 5. Salary Management
- Salary components configuration
- Salary declaration
- Salary computation
- LWP (Leave Without Pay) Management

### 6. Reimbursement System
- Reimbursement request submission
- Reimbursement type management
- Reimbursement approval workflow

### 7. Organization Management
- Multi-organization support
- Organization listing and management

## Material-UI Implementation Analysis

The project uses Material-UI as its primary UI framework, but there are inconsistencies:

### Components Using Material-UI
- Main application theme is defined in `frontend/src/theme.js` using MUI's `createTheme`
- Most components appear to be using MUI components

### Components NOT Using Material-UI
- The Login component (`frontend/src/Components/Auth/Login.jsx`) uses React Bootstrap instead of Material-UI
- There might be other components using Bootstrap or React Bootstrap that should be migrated to Material-UI for consistency

## Recommendations for UI Consistency

1. **Migrate React Bootstrap Components to Material-UI**:
   - Replace React Bootstrap in the Login component with equivalent MUI components
   - Check for other components using React Bootstrap and convert them

2. **Standardize Design System**:
   - Ensure all components follow the defined theme in theme.js
   - Use MUI's built-in theme provider consistently

3. **Remove Unnecessary Dependencies**:
   - Consider removing Bootstrap and React Bootstrap dependencies after migration
   - Keep the codebase clean by removing unused imports

4. **Create Common Components**:
   - Develop reusable MUI-based components for common UI elements
   - Ensure consistent styling and behavior across the application

## Conclusion
The Payroll Management System is a comprehensive solution for HR and payroll management with a rich set of features. While the application primarily uses Material-UI, there are inconsistencies with some components using React Bootstrap. Standardizing all components to use Material-UI would improve maintainability and visual consistency across the application. 