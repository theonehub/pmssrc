# Project Code Index

## Project Overview
This repository contains a Payroll Management System (PMS) with three main components:
- **Backend**: Server-side API and business logic built with FastAPI and MongoDB
- **Frontend**: Web client interface built with React.js and Material-UI
- **PMSMobile**: Mobile application built with React Native

The system manages various aspects of employee management including user management, attendance, leave management, salary components, reimbursements, and more.

## Tech Stack

### Backend
- **Framework**: FastAPI
- **Database**: MongoDB (pymongo)
- **Authentication**: JWT (python-jose, PyJWT)
- **Password Hashing**: passlib with bcrypt
- **File Handling**: openpyxl

### Frontend
- **Framework**: React.js
- **UI Libraries**: Material-UI (MUI) v7.0.2, React Bootstrap (inconsistently used)
- **State Management**: React Hooks (useState, useEffect)
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Date Handling**: date-fns v4.1.0

### Mobile
- **Framework**: React Native
- **Type Safety**: TypeScript
- **State Management**: React Context

## Directory Structure

### Backend
```
backend/
├── app/         # Main application code
│   ├── auth/       # Authentication components
│   ├── database/   # Database connection and setup
│   ├── models/     # Data models
│   ├── routes/     # API endpoints
│   ├── services/   # Business logic services
│   ├── tests/      # Test cases
│   ├── uploads/    # File uploads directory
│   ├── utils/      # Utility functions
│   ├── main.py     # Application entry point
│   └── config.py   # Configuration settings
├── env/         # Environment configuration
└── requirements.txt # Python dependencies
```

### Frontend
```
frontend/
├── node_modules/ # Node.js dependencies
├── public/       # Static assets
├── src/          # Source code
│   ├── Components/  # Reusable UI components
│   │   ├── Attendence/     # Attendance tracking components
│   │   ├── Auth/           # Authentication components
│   │   ├── Common/         # Shared components
│   │   ├── CompanyLeaves/  # Company leave management
│   │   ├── Leaves/         # Employee leave management
│   │   ├── Organisation/   # Organization management
│   │   ├── PublicHolidays/ # Public holiday components
│   │   ├── Reimbursements/ # Reimbursement management
│   │   ├── Salary/         # Salary management
│   │   └── User/           # User management
│   ├── features/    # Feature-specific code
│   ├── hooks/       # Custom React hooks
│   ├── layout/      # Layout components
│   ├── models/      # Data models
│   ├── pages/       # Page components
│   ├── services/    # API services
│   ├── utils/       # Utility functions
│   ├── App.jsx      # Main application component
│   ├── theme.js     # Design theme configuration
│   └── index.js     # Application entry point
├── package.json  # Project configuration
└── README.md     # Documentation
```

### PMSMobile
```
PMSMobile/
├── android/      # Android-specific code
├── ios/          # iOS-specific code
├── src/          # Source code
│   ├── context/     # React context providers
│   ├── navigation/  # Navigation configuration
│   ├── screens/     # Screen components
│   ├── services/    # API services
│   ├── types/       # TypeScript type definitions
│   ├── utils/       # Utility functions
│   └── theme.ts     # Design theme configuration
├── __tests__/    # Test files
├── node_modules/ # Node.js dependencies
├── App.tsx       # Main application component
└── package.json  # Project configuration
```

### Documentation
- `project_documentation.md` - Overall project documentation and technical stack
- `functionalities.md` - Detailed feature specifications
- `ui_standardization.md` - UI/UX guidelines and standards

## Key Features and Components

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

## Implementation Details

### Backend Components
- **API Routes**: RESTful API endpoints for client communication
- **Database Models**: MongoDB document structure definitions
- **Authentication**: JWT-based user authentication and authorization
- **Services**: Business logic implementation for various modules
- **Utilities**: Helper functions for common operations

### Frontend Components
- **Pages**: Main application views for different modules
- **Components**: Reusable UI elements organized by feature
- **Services**: API communication layer for backend interaction
- **State Management**: React hooks for local and global state
- **Routing**: Navigation between different application sections
- **Styling**: Material-UI based theming and components

### Mobile Components
- **Screens**: Mobile application views
- **Navigation**: Screen transition and routing
- **Services**: API communication layer
- **Context**: State management with React Context
- **TypeScript Types**: Type definitions for type safety

## Setup and Installation

Refer to project-specific README files for setup instructions:
- Frontend: `frontend/README.md`
- Mobile: `PMSMobile/README.md` 