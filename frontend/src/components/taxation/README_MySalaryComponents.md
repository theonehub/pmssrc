# My Salary Components - User-Facing Salary View

## Overview
The `MySalaryComponents` component provides employees with a comprehensive view of their salary components and tax information. This is a user-facing page that allows employees to view their own salary details without requiring admin privileges.

## Features

### 1. Salary Component Overview
- **Salary Income**: Basic salary, allowances, and other earnings
- **Deductions**: Section 80C, 80D, and other tax-saving investments
- **House Property**: Rental income, home loan interest, and municipal taxes
- **Capital Gains**: Short-term and long-term capital gains from investments
- **Other Income**: Interest income, dividends, gifts, and business income
- **Perquisites**: Accommodation, car, medical, LTA, ESOP, and other benefits

### 2. Interactive Features
- **Tax Year Selection**: View data for current and previous tax years
- **Real-time Tax Calculation**: Monthly tax liability estimation
- **Export Functionality**: Download salary package as Excel file
- **Refresh Data**: Update component data from the server
- **Responsive Design**: Works on desktop and mobile devices

### 3. Visual Components
- **Summary Cards**: Total value, components with data, monthly tax, tax year status
- **Component Cards**: Visual representation of each salary component
- **Detailed View**: Expandable accordions with detailed breakdown
- **Status Indicators**: Visual indicators for data availability

## Access Control
- **Available to**: All authenticated users (user, manager, admin, superadmin)
- **Route**: `/my-salary`
- **Navigation**: Available in the sidebar under "Income Tax" section

## Technical Implementation

### Key Dependencies
- `@mui/material`: UI components
- `@mui/icons-material`: Icons
- `react-router-dom`: Navigation
- `taxationApi`: Backend API integration
- `useAuth`: Authentication context

### API Integration
The component integrates with the following API endpoints:
- `taxationApi.getComponent()`: Fetch individual component data
- `taxationApi.computeMonthlyTax()`: Calculate monthly tax liability
- `taxationApi.exportSalaryPackageToExcel()`: Export salary data

### State Management
- **Loading States**: Separate loading states for components and tax calculation
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Toast Notifications**: Success/error feedback for user actions

### Data Flow
1. Component loads user data from authentication context
2. Fetches salary components for selected tax year
3. Calculates monthly tax liability
4. Renders component cards and detailed breakdown
5. Provides export and refresh functionality

## Usage

### For Employees
1. Navigate to "My Salary Components" from the sidebar
2. Select desired tax year from the dropdown
3. View summary cards for quick overview
4. Click on component cards to see detailed breakdown
5. Use export function to download salary package
6. Refresh data when needed

### For Administrators
- Admins can access this page to view their own salary components
- The page provides the same functionality as regular users
- Useful for testing and verification purposes

## Future Enhancements
- **Comparison View**: Compare salary components across different years
- **Tax Optimization Suggestions**: AI-powered tax saving recommendations
- **Document Upload**: Allow users to upload supporting documents
- **Notifications**: Alert users when salary components are updated
- **Mobile App**: Native mobile application for salary viewing

## Security Considerations
- User can only view their own salary data
- Employee ID is extracted from authentication context
- No sensitive data is exposed to unauthorized users
- All API calls are authenticated and authorized

## Troubleshooting

### Common Issues
1. **No Data Available**: Contact HR to update salary components
2. **Tax Calculation Errors**: Verify salary data completeness
3. **Export Failures**: Check network connectivity and try again
4. **Loading Issues**: Refresh the page or contact support

### Error Messages
- "Failed to load salary components": Network or server issue
- "Failed to calculate tax": Incomplete salary data
- "Failed to export salary package": Export service unavailable

## Related Components
- `ComponentsOverview`: Admin view for managing employee components
- `IndividualComponentManagement`: Admin interface for component management
- `SalaryComponentForm`: Form for updating salary components 