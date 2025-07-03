# Payroll Management System - Comprehensive API Documentation

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Backend APIs](#backend-apis)
4. [Frontend Components](#frontend-components)
5. [Shared Utilities](#shared-utilities)
6. [Tax Calculator Utility](#tax-calculator-utility)
7. [Data Models](#data-models)
8. [Usage Examples](#usage-examples)
9. [Development Setup](#development-setup)

## Project Overview

This is a comprehensive payroll management system built with a modern tech stack consisting of:

- **Backend**: FastAPI (Python) with MongoDB
- **Frontend**: React (TypeScript) with Material-UI
- **Architecture**: Clean Architecture with SOLID principles
- **Authentication**: JWT-based authentication with refresh tokens
- **Features**: User management, attendance tracking, leave management, reimbursements, taxation, reporting

## Architecture

### Technology Stack

**Backend:**
- FastAPI 0.115.12
- MongoDB with Motor (async driver)
- Pydantic for data validation
- JWT authentication
- Clean architecture implementation

**Frontend:**
- React 18.2.0 with TypeScript
- Material-UI (@mui/material 6.1.9)
- React Query (@tanstack/react-query) for data fetching
- Zustand for state management
- React Router for navigation
- Axios for HTTP requests

## Backend APIs

### Authentication APIs (`/api/v2/auth`)

#### `POST /api/v2/auth/login`
User authentication endpoint.

**Request Body:**
```typescript
interface LoginRequestDTO {
  username: string;
  password: string;
  hostname: string;
  remember_me?: boolean;
}
```

**Response:**
```typescript
interface LoginResponseDTO {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
  permissions: string[];
}
```

**Example:**
```javascript
const response = await post('/api/v2/auth/login', {
  username: 'john.doe',
  password: 'securepassword',
  hostname: 'company.com'
});
```

#### `POST /api/v2/auth/refresh`
Refresh access token using refresh token.

**Request Body:**
```typescript
interface RefreshTokenRequestDTO {
  refresh_token: string;
}
```

#### `POST /api/v2/auth/logout`
Logout user and invalidate tokens.

#### `POST /api/v2/auth/change-password`
Change user password.

**Request Body:**
```typescript
interface PasswordChangeRequestDTO {
  old_password: string;
  new_password: string;
  confirm_password: string;
}
```

#### `GET /api/v2/auth/me`
Get current user profile information.

#### `GET /api/v2/auth/whoami`
Quick endpoint to check current authenticated user.

### User Management APIs (`/api/v2/users`)

#### `GET /api/v2/users`
Retrieve all users with optional filtering and pagination.

**Query Parameters:**
- `role` (optional): Filter by user role
- `department` (optional): Filter by department
- `status` (optional): Filter by status
- `search` (optional): Search term
- `skip` (optional): Number of records to skip
- `limit` (optional): Number of records to return

**Response:**
```typescript
interface UserListResponse {
  data: User[];
  total: number;
  page: number;
  limit: number;
}
```

#### `POST /api/v2/users`
Create a new user.

**Request Body:**
```typescript
interface CreateUserRequest {
  email: string;
  name: string;
  role: UserRole;
  employee_id?: string;
  department?: string;
  designation?: string;
  mobile?: string;
  gender?: string;
  date_of_joining?: string;
  date_of_birth?: string;
  address?: string;
  phone?: string;
}
```

#### `GET /api/v2/users/{user_id}`
Get user details by ID.

#### `PUT /api/v2/users/{user_id}`
Update user information.

#### `DELETE /api/v2/users/{user_id}`
Delete a user.

### Attendance APIs (`/api/v2/attendance`)

#### `POST /api/v2/attendance/checkin`
Record employee check-in.

**Example:**
```javascript
await post('/api/v2/attendance/checkin');
```

#### `POST /api/v2/attendance/checkout`
Record employee check-out.

#### `GET /api/v2/attendance/records`
Get attendance records with filtering.

**Query Parameters:**
- `employee_id` (optional): Filter by employee
- `start_date` (optional): Start date filter
- `end_date` (optional): End date filter

### Leave Management APIs (`/api/v2/leaves`)

#### `GET /api/v2/leaves`
Get leave requests with filtering.

#### `POST /api/v2/leaves`
Submit a new leave request.

**Request Body:**
```typescript
interface LeaveRequest {
  leave_type: string;
  start_date: string;
  end_date: string;
  reason: string;
  days?: number;
}
```

#### `PUT /api/v2/leaves/{leave_id}/approve`
Approve a leave request.

#### `PUT /api/v2/leaves/{leave_id}/reject`
Reject a leave request.

### Reimbursement APIs (`/api/v2/reimbursements`)

#### `GET /api/v2/reimbursements`
Get reimbursement requests.

#### `POST /api/v2/reimbursements`
Submit a new reimbursement request.

**Request Body:**
```typescript
interface ReimbursementRequest {
  type: string;
  amount: number;
  description: string;
  receipt_file?: File;
}
```

#### `PUT /api/v2/reimbursements/{reimbursement_id}/approve`
Approve a reimbursement request.

### Taxation APIs (`/api/v2/taxation`)

#### `GET /api/v2/taxation/declaration/{employee_id}`
Get employee tax declaration.

#### `POST /api/v2/taxation/declaration`
Submit or update tax declaration.

#### `GET /api/v2/taxation/calculate`
Calculate tax based on provided data.

**Query Parameters:**
- `regime`: Tax regime ('old' or 'new')
- `employee_id`: Employee ID

### Reporting APIs (`/api/v2/reporting`)

#### `GET /api/v2/reporting/dashboard/analytics/statistics`
Get dashboard statistics.

**Response:**
```typescript
interface DashboardStats {
  total_users: number;
  checkin_count: number;
  checkout_count: number;
  pending_reimbursements: number;
  pending_reimbursements_amount: number;
  approved_reimbursements: number;
  approved_reimbursements_amount: number;
}
```

## Frontend Components

### Core Components

#### `App.tsx`
Main application component with routing configuration.

**Features:**
- Route protection based on user roles
- Error boundary wrapping
- Global calculator component

#### `Home.tsx`
Dashboard component displaying key metrics and attendance actions.

**Props:** None

**Features:**
- Dashboard statistics display
- Check-in/check-out functionality
- Real-time data fetching

**Usage:**
```typescript
import Home from './pages/Home';

<Route path="/home" element={<Home />} />
```

### Authentication Components

#### `Login.tsx`
User authentication form component.

**Features:**
- Credential validation
- Remember me functionality
- Error handling
- Automatic redirection after login

**Usage:**
```typescript
import Login from './components/Auth/Login';

<Route path="/login" element={<Login />} />
```

### User Management Components

#### `UsersList.tsx`
User listing component with search and filtering.

**Features:**
- Sortable columns
- Search functionality
- Role-based filtering
- Pagination
- Bulk actions

**Usage:**
```typescript
import UsersList from './components/User/UsersList';

<UsersList />
```

#### `UserDetail.tsx`
Display detailed user information.

**Props:**
```typescript
interface UserDetailProps {
  userId: string;
}
```

#### `UserEdit.tsx`
User editing form component.

**Props:**
```typescript
interface UserEditProps {
  userId: string;
  onSave?: (user: User) => void;
  onCancel?: () => void;
}
```

#### `AddNewUser.tsx`
Form component for creating new users.

**Features:**
- Form validation
- File upload for documents
- Role selection
- Department assignment

### Attendance Components

#### `AttendanceUserList.tsx`
List view of employee attendance records.

**Features:**
- Date range filtering
- Employee filtering
- Export functionality
- LWP (Leave Without Pay) integration

#### `AttendanceCalendar.tsx`
Calendar view of attendance data.

**Props:**
```typescript
interface AttendanceCalendarProps {
  employeeId?: string;
  month?: number;
  year?: number;
  onDateSelect?: (date: Date) => void;
}
```

### Leave Management Components

#### `LeaveManagement.tsx`
Employee leave request and management interface.

**Features:**
- Leave request submission
- Leave balance display
- History of leave requests
- Calendar integration

#### `AllLeaves.tsx`
Admin view of all leave requests.

**Features:**
- Approval/rejection workflow
- Filtering by status, employee, date range
- Bulk operations

### Taxation Components

#### `TaxationDashboard.tsx`
Main taxation overview and navigation.

**Features:**
- Tax summary display
- Regime comparison
- Navigation to detailed forms

#### `TaxDeclaration.tsx`
Comprehensive tax declaration form.

**Props:**
```typescript
interface TaxDeclarationProps {
  employeeId?: string;
  isReadOnly?: boolean;
}
```

**Features:**
- Multi-section form (salary, deductions, other income)
- Real-time tax calculation
- Regime comparison
- Form validation

#### `SalaryComponentForm.tsx`
Detailed salary component management.

**Features:**
- Comprehensive salary component inputs
- HRA calculation
- Allowance management
- Perquisites handling

#### `DeductionsComponentForm.tsx`
Tax deductions form (80C, 80D, etc.).

**Features:**
- Section-wise deduction inputs
- Automatic limit validation
- Investment tracking

### Reimbursement Components

#### `MyReimbursements.tsx`
Employee view of their reimbursement requests.

**Features:**
- Request submission
- Status tracking
- Receipt upload
- History view

#### `ReimbursementApprovals.tsx`
Manager/Admin view for approving reimbursements.

**Features:**
- Approval workflow
- Receipt viewing
- Bulk operations
- Status filtering

### Common/Shared Components

#### `Calculator.tsx`
Built-in calculator component.

**Props:**
```typescript
interface CalculatorProps {
  open: boolean;
  onClose: () => void;
  onResult?: (result: number) => void;
}
```

**Features:**
- Basic arithmetic operations
- Memory functions
- Expression validation

#### `ErrorBoundary.tsx`
Error boundary component for graceful error handling.

**Props:**
```typescript
interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ComponentType<any>;
}
```

#### `ProtectedRoute.tsx`
Route protection based on user roles.

**Props:**
```typescript
interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: UserRole[];
}
```

#### `LoadingSpinner.tsx`
Reusable loading indicator component.

**Props:**
```typescript
interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  color?: 'primary' | 'secondary';
  text?: string;
}
```

### Layout Components

#### `PageLayout.tsx`
Main layout wrapper for pages.

**Props:**
```typescript
interface PageLayoutProps {
  title: string;
  children: React.ReactNode;
  actions?: React.ReactNode;
}
```

#### `Sidebar.tsx`
Navigation sidebar component.

**Features:**
- Role-based menu items
- Collapsible sections
- Active route highlighting

## Shared Utilities

### API Utilities

#### `BaseAPI` Class
Centralized HTTP client with authentication and error handling.

**Methods:**
```typescript
class BaseAPI {
  get<T>(url: string, config?: AxiosRequestConfig): Promise<T>
  post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T>
  put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T>
  delete<T>(url: string, config?: AxiosRequestConfig): Promise<T>
  patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T>
  upload<T>(url: string, formData: FormData, onUploadProgress?: Function): Promise<T>
  download(url: string, config?: AxiosRequestConfig): Promise<Blob>
}
```

**Usage:**
```typescript
import { get, post } from '../shared/api/baseApi';

// GET request
const users = await get<User[]>('/api/v2/users');

// POST request
const newUser = await post<User>('/api/v2/users', userData);
```

### Custom Hooks

#### `useUsers`
Hook for user data management.

```typescript
export const useUsers = () => {
  const usersQuery = useQuery(['users'], () => get('/api/v2/users'));
  const createMutation = useMutation((userData: CreateUserRequest) => 
    post('/api/v2/users', userData)
  );
  
  return {
    users: usersQuery.data,
    isLoading: usersQuery.isLoading,
    createUser: createMutation.mutate,
    isCreating: createMutation.isLoading
  };
};
```

#### `useTaxCalculation`
Hook for tax calculations.

```typescript
export const useTaxCalculation = () => {
  const calculateTax = useCallback((data: TaxationData) => {
    // Tax calculation logic
  }, []);
  
  const regimeComparison = useCallback((data: TaxationData) => {
    // Compare old vs new regime
  }, []);
  
  return { calculateTax, regimeComparison };
};
```

#### `useAttendance`
Hook for attendance data management.

```typescript
export const useAttendanceQuery = (filters: AttendanceFilters = {}) => {
  return useQuery(
    ['attendance', filters],
    () => get('/api/v2/attendance/records', { params: filters })
  );
};
```

### State Management (Zustand)

#### `useTaxationStore`
Global state for taxation data.

```typescript
interface TaxationState {
  currentDeclaration: TaxationData | null;
  regime: TaxRegime;
  calculationResults: TaxBreakup | null;
}

interface TaxationActions {
  setDeclaration: (data: TaxationData) => void;
  setRegime: (regime: TaxRegime) => void;
  calculateTax: () => void;
}

export const useTaxationStore = create<TaxationState & TaxationActions>((set, get) => ({
  // State implementation
}));
```

#### `useCalculatorStore`
Global state for calculator component.

```typescript
interface CalculatorState {
  isCalculatorOpen: boolean;
  openCalculator: () => void;
  closeCalculator: () => void;
}
```

### Utility Functions

#### Constants
Centralized application constants.

```typescript
export const API_CONFIG = {
  BASE_URL: 'http://localhost:8000',
  TIMEOUT: 30000
};

export const USER_ROLES = {
  ADMIN: 'admin',
  HR: 'hr',
  EMPLOYEE: 'employee',
  MANAGER: 'manager',
  SUPERADMIN: 'superadmin'
};

export const ROUTES = {
  HOME: '/home',
  USERS: '/users',
  TAXATION: '/taxation',
  ATTENDANCE: '/attendance'
};
```

## Tax Calculator Utility

### Standalone Excel Tax Calculator

The `utilityApplications/TaxCalcuatorUility` contains a standalone Excel-based tax calculator.

#### Files:
- `Tax_Calculator.xlsx` - Main Excel workbook
- `create_tax_calculator.py` - Python script to generate the Excel file
- `requirements.txt` - Python dependencies

#### Features:
- **Dual Regime Support**: Old and new tax regimes
- **Age-based Calculations**: Different exemptions for various age groups
- **Comprehensive Deductions**: All major tax deduction sections
- **Capital Gains**: STCG and LTCG calculations
- **Data Validation**: Built-in input validation
- **Auto-calculations**: Pre-built formulas across worksheets

#### Worksheets:
1. **INPUT_DATA**: Basic information and income sources
2. **DEDUCTIONS**: All tax deduction sections (80C, 80D, etc.)
3. **CALCULATIONS**: Income computations and exemptions
4. **TAX_CALCULATION**: Final tax calculations
5. **VALIDATION**: Input validation and cross-checks

#### Usage:
1. Open `Tax_Calculator.xlsx`
2. Fill INPUT_DATA sheet with employee details
3. Enter deductions in DEDUCTIONS sheet
4. Review calculations in CALCULATIONS sheet
5. Check final tax in TAX_CALCULATION sheet
6. Validate inputs using VALIDATION sheet

#### Regenerating the Calculator:
```bash
cd utilityApplications/TaxCalcuatorUility
pip install -r requirements.txt
python create_tax_calculator.py
```

## Data Models

### Core Interfaces

#### `User`
```typescript
interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  employee_id?: string;
  department?: string;
  designation?: string;
  mobile?: string;
  gender?: string;
  date_of_joining?: string;
  date_of_birth?: string;
  address?: string;
  phone?: string;
  status?: string;
  created_at?: string;
  updated_at?: string;
}

type UserRole = 'admin' | 'hr' | 'employee' | 'manager' | 'superadmin' | 'user';
```

#### `TaxationData`
```typescript
interface TaxationData {
  employee_id: string;
  tax_year: string;
  regime: TaxRegime;
  filing_status: FilingStatus;
  salary: SalaryComponents;
  other_sources: OtherSources;
  house_property: HouseProperty;
  capital_gains: CapitalGains;
  deductions: Deductions;
  leave_encashment: LeaveEncashment;
  pension: Pension;
  gratuity: Gratuity;
}

type TaxRegime = 'old' | 'new';
type FilingStatus = 'not_filed' | 'filed' | 'processed' | 'verified' | 'draft' | 'submitted' | 'approved' | 'rejected' | 'pending';
```

#### `SalaryComponents`
```typescript
interface SalaryComponents {
  basic: number;
  dearness_allowance: number;
  hra: number;
  special_allowance: number;
  bonus: number;
  transport_allowance: number;
  medical_allowance: number;
  // ... other allowances
  perquisites: Perquisites;
}
```

#### `Deductions`
```typescript
interface Deductions {
  section_80c: {
    life_insurance_premium: number;
    epf_contribution: number;
    ppf_contribution: number;
    nsc_investment: number;
    elss_investment: number;
    home_loan_principal: number;
    // ... other 80C investments
  };
  section_80d: {
    self_family_premium: number;
    parent_premium: number;
    preventive_health_checkup: number;
    employee_age: number;
    parent_age: number;
  };
  // ... other deduction sections
}
```

#### `AttendanceData`
```typescript
interface AttendanceData {
  employee_id: string;
  date: string;
  check_in: string;
  check_out: string;
  hours_worked: number;
  status: 'present' | 'absent' | 'late' | 'half_day';
}
```

#### `LeaveRequest`
```typescript
interface LeaveRequest {
  id?: string;
  employee_id: string;
  leave_type: string;
  start_date: string;
  end_date: string;
  days: number;
  reason: string;
  status: 'pending' | 'approved' | 'rejected';
  applied_date: string;
  approved_by?: string;
  approved_date?: string;
  comments?: string;
}
```

#### `ReimbursementData`
```typescript
interface ReimbursementData {
  id: string;
  employee_id: string;
  type: string;
  amount: number;
  description: string;
  status: 'pending' | 'approved' | 'rejected';
  submitted_date: string;
  receipt_url?: string;
}
```

## Usage Examples

### Authentication Flow

```typescript
// Login
const handleLogin = async (credentials: LoginCredentials) => {
  try {
    const response = await post<AuthResponse>('/api/v2/auth/login', credentials);
    localStorage.setItem('token', response.access_token);
    localStorage.setItem('user_info', JSON.stringify(response.user));
    navigate('/home');
  } catch (error) {
    console.error('Login failed:', error);
  }
};

// Protected route usage
<ProtectedRoute allowedRoles={['admin', 'manager']}>
  <UsersList />
</ProtectedRoute>
```

### User Management

```typescript
// Fetch users with filtering
const { users, isLoading } = useUsersQuery({
  role: 'employee',
  department: 'Engineering',
  limit: 20
});

// Create new user
const createUser = async (userData: CreateUserRequest) => {
  try {
    const newUser = await post<User>('/api/v2/users', userData);
    console.log('User created:', newUser);
  } catch (error) {
    console.error('Failed to create user:', error);
  }
};
```

### Tax Calculation

```typescript
// Using taxation store
const { setDeclaration, calculateTax, regime, setRegime } = useTaxationStore();

// Calculate tax for different regimes
const { regimeComparison } = useTaxCalculation();

const handleCalculation = (taxData: TaxationData) => {
  setDeclaration(taxData);
  const comparison = regimeComparison(taxData);
  console.log('Tax comparison:', comparison);
};

// Switch regime
const handleRegimeChange = (newRegime: TaxRegime) => {
  setRegime(newRegime);
  calculateTax();
};
```

### Attendance Tracking

```typescript
// Check-in
const handleCheckIn = async () => {
  try {
    await post('/api/v2/attendance/checkin');
    showToast('Check-in successful!', 'success');
  } catch (error) {
    showToast('Check-in failed', 'error');
  }
};

// Fetch attendance records
const { data: attendanceRecords } = useAttendanceQuery({
  employee_id: 'EMP001',
  start_date: '2024-01-01',
  end_date: '2024-01-31'
});
```

### File Upload

```typescript
// Upload reimbursement receipt
const handleReceiptUpload = async (file: File, reimbursementId: string) => {
  const formData = new FormData();
  formData.append('receipt', file);
  
  try {
    await upload(`/api/v2/reimbursements/${reimbursementId}/receipt`, formData);
    showToast('Receipt uploaded successfully!', 'success');
  } catch (error) {
    showToast('Upload failed', 'error');
  }
};
```

### Error Handling

```typescript
// Global error boundary usage
<ErrorBoundary fallback={<ErrorFallback />}>
  <App />
</ErrorBoundary>

// API error handling
const handleApiCall = async () => {
  try {
    const result = await get('/api/v2/some-endpoint');
    return result;
  } catch (error) {
    if (error.status === 401) {
      // Handle unauthorized
      redirectToLogin();
    } else if (error.status >= 500) {
      // Handle server error
      showToast('Server error occurred', 'error');
    } else {
      // Handle other errors
      showToast(error.message, 'error');
    }
  }
};
```

## Development Setup

### Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="mongodb://localhost:27017/payroll"
export SECRET_KEY="your-secret-key"

# Run the server
python -m app.main
# or
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install

# Set environment variables
REACT_APP_API_URL=http://localhost:8000

# Run the development server
npm start
```

### Tax Calculator Utility

```bash
cd utilityApplications/TaxCalcuatorUility
pip install -r requirements.txt
python create_tax_calculator.py
```

## API Rate Limits and Best Practices

### Authentication
- Access tokens expire in 1 hour
- Refresh tokens expire in 7 days
- Use refresh tokens to get new access tokens
- Implement token refresh logic in your API client

### Error Handling
- All API responses follow consistent error format
- Use HTTP status codes appropriately
- Implement retry logic for transient failures
- Log errors for debugging

### Performance
- Use pagination for large data sets
- Implement client-side caching
- Optimize database queries
- Use lazy loading for components

### Security
- Validate all inputs on both client and server
- Use HTTPS in production
- Implement proper CORS policies
- Store sensitive data securely

## Contributing

1. Follow the existing code structure and naming conventions
2. Add appropriate TypeScript types for new features
3. Include unit tests for new functionality
4. Update documentation when adding new APIs or components
5. Follow the clean architecture principles established in the codebase

## Support

For technical support or questions about the API, please refer to:
- Backend API documentation: Check FastAPI docs at `/docs` endpoint
- Frontend component documentation: See individual component files
- Tax calculator documentation: Check `utilityApplications/TaxCalcuatorUility/README.md`