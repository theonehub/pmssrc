# Frontend Architecture Documentation

## 1. Technology Stack
- **Framework**: React 18.2.0
- **Language**: TypeScript
- **UI Library**: Material-UI (MUI) v7.0.2
- **Routing**: React Router v6.30.0
- **State Management**: React Context API
- **HTTP Client**: Axios v1.8.4
- **Date Handling**: date-fns v4.1.0
- **Charts**: Recharts v2.15.3
- **Form Handling**: Custom implementation with MUI components
- **Notifications**: react-toastify v11.0.5

## 2. Project Structure
```
frontend/
├── src/
│   ├── Components/         # Reusable UI components
│   ├── context/           # React Context providers
│   ├── features/          # Feature-specific components
│   ├── hooks/            # Custom React hooks
│   ├── layout/           # Layout components
│   ├── models/           # Data models
│   ├── pages/            # Page components
│   ├── services/         # API services
│   ├── types/            # TypeScript type definitions
│   ├── utils/            # Utility functions
│   ├── constants/        # Constants and configurations
│   ├── App.tsx           # Main application component
│   └── theme.js          # MUI theme configuration
```

## 3. Theme Configuration
The application uses a custom MUI theme with the following key configurations:

### Color Palette
```javascript
palette: {
  primary: {
    main: '#1976d2',
    light: '#42a5f5',
    dark: '#1565c0',
    contrastText: '#ffffff',
  },
  secondary: {
    main: '#9c27b0',
    light: '#ba68c8',
    dark: '#7b1fa2',
    contrastText: '#ffffff',
  },
  // ... other colors
}
```

### Typography
```javascript
typography: {
  fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  h1: { fontSize: '2.5rem', fontWeight: 500 },
  h2: { fontSize: '2rem', fontWeight: 500 },
  // ... other typography styles
}
```

### Component Customization
```javascript
components: {
  MuiButton: {
    styleOverrides: {
      root: {
        textTransform: 'none',
        borderRadius: 8,
      },
    },
  },
  MuiCard: {
    styleOverrides: {
      root: {
        borderRadius: 8,
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      },
    },
  },
}
```

## 4. Layout System

### PageLayout Component
- Responsive layout with collapsible sidebar
- Topbar with title and menu toggle
- Main content area with proper spacing
- Mobile-friendly design with drawer navigation
- Resizable sidebar (desktop only)

### Sidebar Features
- Collapsible categories
- Role-based menu items
- Persistent state (localStorage)
- Mobile drawer support
- Smooth transitions

### Navigation Structure
```typescript
interface MenuCategory {
  id: string;
  title: string;
  icon: React.ReactElement;
  items: MenuItem[];
}

interface MenuItem {
  title: string;
  icon: React.ReactElement;
  path?: string;
  action?: string;
  roles: UserRole[];
}
```

## 5. Common Components

### DataTable
- Sortable columns
- Pagination
- Search functionality
- Custom cell rendering
- Row selection
- Responsive design

### FormDialog
- Reusable modal dialog
- Form handling
- Validation support
- Loading states
- Error handling

### StatusBadge
- Color-coded status indicators
- Customizable styles
- Multiple status types

### SearchInput
- Debounced search
- Clear functionality
- Loading state
- Custom styling

## 6. Authentication & Authorization

### Protected Routes
```typescript
interface ProtectedRouteProps {
  allowedRoles: UserRole[];
  children: React.ReactNode;
}
```

### Role-Based Access
- User roles: 'user', 'manager', 'admin', 'superadmin'
- Role-based menu visibility
- Route protection
- API access control

## 7. Error Handling

### ErrorBoundary
- Global error catching
- Fallback UI
- Error reporting
- Development mode details

### API Error Handling
- Axios interceptors
- Toast notifications
- Error state management
- Retry mechanisms

## 8. State Management

### Context Providers
- Calculator context
- Authentication context
- Theme context
- User context

### Custom Hooks
- API data fetching
- Form handling
- Authentication
- Theme switching

## 9. API Integration

### Service Structure
```typescript
interface ApiService {
  baseURL: string;
  headers: Record<string, string>;
  get: (url: string) => Promise<any>;
  post: (url: string, data: any) => Promise<any>;
  // ... other methods
}
```

### Authentication
- JWT token management
- Token refresh
- Axios interceptors
- Error handling

## 10. Responsive Design

### Breakpoints
```javascript
{
  xs: 0,
  sm: 600,
  md: 960,
  lg: 1280,
  xl: 1920
}
```

### Mobile Considerations
- Drawer navigation
- Responsive tables
- Touch-friendly inputs
- Adaptive layouts

## 11. Performance Optimizations

### Code Splitting
- Route-based splitting
- Component lazy loading
- Dynamic imports

### Caching
- API response caching
- Local storage usage
- Session management

## 12. Development Tools

### Scripts
```json
{
  "start": "react-scripts start",
  "build": "react-scripts build",
  "test": "react-scripts test",
  "lint": "eslint src --ext .js,.jsx,.ts,.tsx",
  "format": "prettier --write src/**/*.{js,jsx,ts,tsx,json,css,md}"
}
```

### Code Quality
- ESLint configuration
- Prettier formatting
- TypeScript strict mode
- Testing setup

## 13. Key Features

### Leave Management
- Leave application
- Leave approval workflow
- Leave balance tracking
- Public holidays management
- Company leaves configuration

### Attendance
- Attendance tracking
- LWP (Loss of Pay) management
- Attendance reports
- Team attendance view

### Payouts & Salary
- Salary details view
- Payslip generation
- Salary calculator
- Monthly processing
- Payout reports

### Taxation
- Tax dashboard
- Tax declaration
- Employee tax details
- Tax calculations

### Reimbursements
- Reimbursement types
- Reimbursement requests
- Approval workflow
- Reimbursement tracking

### Organization Management
- Organization setup
- Team management
- User management
- Role management

## 14. Best Practices

### Code Organization
- Feature-based structure
- Component reusability
- Clear separation of concerns
- Consistent naming conventions

### State Management
- Context for global state
- Local state for component-specific data
- Proper state initialization
- State update patterns

### Error Handling
- Comprehensive error boundaries
- User-friendly error messages
- Error logging
- Recovery mechanisms

### Performance
- Memoization where needed
- Proper dependency arrays
- Lazy loading
- Code splitting

### Security
- JWT token management
- Role-based access control
- Input validation
- XSS prevention

## 15. Testing Strategy

### Unit Testing
- Component testing
- Hook testing
- Utility function testing
- Service testing

### Integration Testing
- API integration tests
- User flow testing
- State management testing

### E2E Testing
- Critical user journeys
- Cross-browser testing
- Performance testing

## 16. Deployment

### Build Process
- Production build optimization
- Environment configuration
- Asset optimization
- Source map generation

### CI/CD
- Automated testing
- Build verification
- Deployment automation
- Environment management

## 17. Monitoring and Maintenance

### Error Tracking
- Error boundary implementation
- Error logging
- Performance monitoring
- User feedback collection

### Performance Monitoring
- Load time tracking
- Resource usage monitoring
- API performance tracking
- User experience metrics

### Maintenance
- Regular dependency updates
- Code quality checks
- Performance optimization
- Security patches 