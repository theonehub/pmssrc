# Frontend Development Guidelines

## Table of Contents
1. [Project Structure](#project-structure)
2. [Coding Standards](#coding-standards)
3. [Component Guidelines](#component-guidelines)
4. [State Management](#state-management)
5. [Styling Guidelines](#styling-guidelines)
6. [Testing Guidelines](#testing-guidelines)
7. [Performance Guidelines](#performance-guidelines)
8. [Security Guidelines](#security-guidelines)

## Project Structure

```
src/
├── Components/           # Reusable UI components
│   ├── Common/          # Shared components (ErrorBoundary, LoadingSpinner, etc.)
│   ├── Auth/            # Authentication components
│   ├── User/            # User management components
│   └── ...              # Feature-specific components
├── pages/               # Page-level components
├── hooks/               # Custom React hooks
├── context/             # React context providers
├── services/            # API service functions
├── utils/               # Utility functions
├── constants/           # Application constants
├── layout/              # Layout components
└── features/            # Feature-specific modules
```

## Coding Standards

### General Rules
- Use **functional components** with hooks instead of class components
- Follow **ES6+** syntax and features
- Use **TypeScript** for type safety (when migrating)
- Implement **proper error handling** with try-catch blocks
- Use **meaningful variable and function names**
- Add **JSDoc comments** for complex functions

### File Naming Conventions
- **Components**: PascalCase (e.g., `UserProfile.jsx`)
- **Hooks**: camelCase starting with 'use' (e.g., `useAuth.js`)
- **Utilities**: camelCase (e.g., `validation.js`)
- **Constants**: camelCase (e.g., `apiConstants.js`)

### Import Organization
```javascript
// 1. React and external libraries
import React, { useState, useEffect } from 'react';
import { Button, TextField } from '@mui/material';

// 2. Internal utilities and services
import { validateEmail } from '../utils/validation';
import { userService } from '../services/userService';

// 3. Components
import LoadingSpinner from '../Components/Common/LoadingSpinner';

// 4. Constants and types
import { USER_ROLES } from '../constants';
```

## Component Guidelines

### Component Structure
```javascript
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

/**
 * Component description
 * @param {Object} props - Component props
 * @param {string} props.title - Title to display
 * @param {Function} props.onSubmit - Submit handler
 */
const MyComponent = ({ title, onSubmit }) => {
  // 1. State declarations
  const [loading, setLoading] = useState(false);
  
  // 2. Effect hooks
  useEffect(() => {
    // Effect logic
  }, []);
  
  // 3. Event handlers
  const handleSubmit = (data) => {
    setLoading(true);
    onSubmit(data);
    setLoading(false);
  };
  
  // 4. Render helpers (if needed)
  const renderContent = () => {
    // Complex render logic
  };
  
  // 5. Main render
  return (
    <div>
      {/* Component JSX */}
    </div>
  );
};

// PropTypes validation
MyComponent.propTypes = {
  title: PropTypes.string.isRequired,
  onSubmit: PropTypes.func.isRequired,
};

export default MyComponent;
```

### Component Best Practices
- **Single Responsibility**: Each component should have one clear purpose
- **Prop Validation**: Always use PropTypes for prop validation
- **Default Props**: Provide default values for optional props
- **Error Boundaries**: Wrap components that might fail
- **Loading States**: Show loading indicators for async operations
- **Accessibility**: Include proper ARIA labels and keyboard navigation

## State Management

### Local State
- Use `useState` for component-level state
- Use `useReducer` for complex state logic
- Keep state as close to where it's used as possible

### Global State
- Use React Context for app-wide state (auth, theme, etc.)
- Consider state management libraries for complex applications
- Avoid prop drilling by using context appropriately

### State Best Practices
```javascript
// ✅ Good: Descriptive state names
const [isLoading, setIsLoading] = useState(false);
const [userProfile, setUserProfile] = useState(null);

// ❌ Bad: Generic state names
const [loading, setLoading] = useState(false);
const [data, setData] = useState(null);

// ✅ Good: Functional updates for state that depends on previous state
setCount(prevCount => prevCount + 1);

// ❌ Bad: Direct state updates
setCount(count + 1);
```

## Styling Guidelines

### Material-UI Best Practices
- Use the `sx` prop for component-specific styles
- Create custom themes for consistent styling
- Use Material-UI components instead of custom HTML elements
- Follow Material Design principles

```javascript
// ✅ Good: Using sx prop
<Button 
  sx={{ 
    mt: 2, 
    backgroundColor: 'primary.main',
    '&:hover': { backgroundColor: 'primary.dark' }
  }}
>
  Submit
</Button>

// ✅ Good: Using theme values
const theme = useTheme();
<Box sx={{ color: theme.palette.primary.main }}>
```

### Responsive Design
- Use Material-UI breakpoints for responsive design
- Test on multiple screen sizes
- Use flexible layouts with Grid and Flexbox

## Testing Guidelines

### Unit Testing
- Test component behavior, not implementation details
- Use React Testing Library for component testing
- Mock external dependencies
- Test error states and edge cases

### Test Structure
```javascript
describe('UserProfile Component', () => {
  it('should render user information correctly', () => {
    // Test implementation
  });
  
  it('should handle loading state', () => {
    // Test implementation
  });
  
  it('should handle error state', () => {
    // Test implementation
  });
});
```

## Performance Guidelines

### Optimization Techniques
- Use `React.memo` for expensive components
- Implement `useMemo` and `useCallback` for expensive calculations
- Lazy load components with `React.lazy`
- Optimize bundle size with code splitting

```javascript
// ✅ Good: Memoized component
const ExpensiveComponent = React.memo(({ data }) => {
  return <div>{/* Expensive rendering */}</div>;
});

// ✅ Good: Memoized calculation
const expensiveValue = useMemo(() => {
  return heavyCalculation(data);
}, [data]);

// ✅ Good: Memoized callback
const handleClick = useCallback(() => {
  onItemClick(item.id);
}, [item.id, onItemClick]);
```

### Bundle Optimization
- Use dynamic imports for code splitting
- Optimize images and assets
- Remove unused dependencies
- Use production builds for deployment

## Security Guidelines

### Data Handling
- Validate all user inputs
- Sanitize data before displaying
- Use HTTPS for all API calls
- Store sensitive data securely

### Authentication
- Implement proper token management
- Use secure storage for tokens
- Handle token expiration gracefully
- Implement proper logout functionality

```javascript
// ✅ Good: Secure token storage
const token = localStorage.getItem('token');
if (token && !isTokenExpired(token)) {
  // Use token
}

// ✅ Good: Input validation
const isValidEmail = (email) => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
};
```

## Code Quality Tools

### ESLint Configuration
- Use the provided `.eslintrc.js` configuration
- Run ESLint before committing code
- Fix all linting errors and warnings

### Prettier Configuration
- Use the provided `.prettierrc` configuration
- Format code before committing
- Set up editor integration for automatic formatting

### Git Hooks
- Set up pre-commit hooks for linting and formatting
- Run tests before pushing code
- Use conventional commit messages

## Development Workflow

### Before Starting Development
1. Pull latest changes from main branch
2. Create a feature branch
3. Install dependencies: `npm install`
4. Start development server: `npm start`

### During Development
1. Write tests for new features
2. Follow coding standards and guidelines
3. Use meaningful commit messages
4. Test on multiple browsers and devices

### Before Submitting PR
1. Run linting: `npm run lint`
2. Run tests: `npm test`
3. Build project: `npm run build`
4. Test the build locally
5. Update documentation if needed

## Common Patterns

### Error Handling
```javascript
const [error, setError] = useState(null);
const [loading, setLoading] = useState(false);

const fetchData = async () => {
  try {
    setLoading(true);
    setError(null);
    const data = await apiCall();
    setData(data);
  } catch (err) {
    setError(err.message);
  } finally {
    setLoading(false);
  }
};
```

### Form Handling
```javascript
const [formData, setFormData] = useState(initialState);
const [errors, setErrors] = useState({});

const handleChange = (field, value) => {
  setFormData(prev => ({ ...prev, [field]: value }));
  // Clear error when user starts typing
  if (errors[field]) {
    setErrors(prev => ({ ...prev, [field]: '' }));
  }
};

const handleSubmit = async (e) => {
  e.preventDefault();
  const validationResult = validateForm(formData);
  if (!validationResult.isValid) {
    setErrors(validationResult.errors);
    return;
  }
  // Submit form
};
```

## Resources

- [React Documentation](https://reactjs.org/docs)
- [Material-UI Documentation](https://mui.com/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [ESLint Rules](https://eslint.org/docs/rules/)
- [Prettier Configuration](https://prettier.io/docs/en/configuration.html) 