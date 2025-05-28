# TypeScript Conversion Example

## Before: JavaScript Component (Login.jsx)

```jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { TextField, Button, Paper, Typography } from '@mui/material';
import { authService } from '../../services/authService';

const Login = () => {
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await authService.login(credentials);
      localStorage.setItem('token', response.access_token);
      navigate('/home');
    } catch (err) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setCredentials({
      ...credentials,
      [e.target.name]: e.target.value
    });
  };

  return (
    <Paper sx={{ p: 4, maxWidth: 400, mx: 'auto', mt: 8 }}>
      <Typography variant="h4" gutterBottom>
        Login
      </Typography>
      
      <form onSubmit={handleSubmit}>
        <TextField
          name="username"
          label="Username"
          value={credentials.username}
          onChange={handleChange}
          fullWidth
          margin="normal"
          required
        />
        
        <TextField
          name="password"
          label="Password"
          type="password"
          value={credentials.password}
          onChange={handleChange}
          fullWidth
          margin="normal"
          required
        />
        
        {error && (
          <Typography color="error" sx={{ mt: 2 }}>
            {error}
          </Typography>
        )}
        
        <Button
          type="submit"
          variant="contained"
          fullWidth
          disabled={loading}
          sx={{ mt: 3 }}
        >
          {loading ? 'Logging in...' : 'Login'}
        </Button>
      </form>
    </Paper>
  );
};

export default Login;
```

## After: TypeScript Component (Login.tsx)

```tsx
import React, { useState, FormEvent, ChangeEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { TextField, Button, Paper, Typography } from '@mui/material';
import { authService } from '../../services/authService';
import { LoginCredentials, AuthResponse } from '../../types';

interface LoginState {
  credentials: LoginCredentials;
  loading: boolean;
  error: string;
}

const Login: React.FC = () => {
  const [state, setState] = useState<LoginState>({
    credentials: {
      username: '',
      password: ''
    },
    loading: false,
    error: ''
  });
  
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    setState(prev => ({ ...prev, loading: true, error: '' }));

    try {
      const response: AuthResponse = await authService.login(state.credentials);
      localStorage.setItem('token', response.access_token);
      navigate('/home');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Login failed';
      setState(prev => ({ ...prev, error: errorMessage }));
    } finally {
      setState(prev => ({ ...prev, loading: false }));
    }
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>): void => {
    const { name, value } = e.target;
    setState(prev => ({
      ...prev,
      credentials: {
        ...prev.credentials,
        [name]: value
      }
    }));
  };

  return (
    <Paper sx={{ p: 4, maxWidth: 400, mx: 'auto', mt: 8 }}>
      <Typography variant="h4" gutterBottom>
        Login
      </Typography>
      
      <form onSubmit={handleSubmit}>
        <TextField
          name="username"
          label="Username"
          value={state.credentials.username}
          onChange={handleChange}
          fullWidth
          margin="normal"
          required
          autoComplete="username"
        />
        
        <TextField
          name="password"
          label="Password"
          type="password"
          value={state.credentials.password}
          onChange={handleChange}
          fullWidth
          margin="normal"
          required
          autoComplete="current-password"
        />
        
        {state.error && (
          <Typography color="error" sx={{ mt: 2 }}>
            {state.error}
          </Typography>
        )}
        
        <Button
          type="submit"
          variant="contained"
          fullWidth
          disabled={state.loading}
          sx={{ mt: 3 }}
        >
          {state.loading ? 'Logging in...' : 'Login'}
        </Button>
      </form>
    </Paper>
  );
};

export default Login;
```

## Key Changes Made

### 1. **File Extension**
- Changed from `.jsx` to `.tsx`

### 2. **Type Imports**
```tsx
import { LoginCredentials, AuthResponse } from '../../types';
```

### 3. **Component Type Annotation**
```tsx
const Login: React.FC = () => {
```

### 4. **State Type Definition**
```tsx
interface LoginState {
  credentials: LoginCredentials;
  loading: boolean;
  error: string;
}

const [state, setState] = useState<LoginState>({
  // initial state
});
```

### 5. **Event Handler Types**
```tsx
const handleSubmit = async (e: FormEvent<HTMLFormElement>): Promise<void> => {
  // implementation
};

const handleChange = (e: ChangeEvent<HTMLInputElement>): void => {
  // implementation
};
```

### 6. **API Response Types**
```tsx
const response: AuthResponse = await authService.login(state.credentials);
```

### 7. **Error Handling**
```tsx
const errorMessage = err instanceof Error ? err.message : 'Login failed';
```

### 8. **Accessibility Improvements**
```tsx
<TextField
  autoComplete="username"  // Added for better UX
  // ...
/>
```

## Benefits of TypeScript Conversion

### ✅ **Type Safety**
- Catch errors at compile time
- IntelliSense and autocomplete
- Refactoring confidence

### ✅ **Better Documentation**
- Self-documenting code
- Clear API contracts
- Easier onboarding

### ✅ **Improved Maintainability**
- Easier to understand data flow
- Reduced runtime errors
- Better IDE support

## Conversion Checklist

- [ ] Change file extension from `.jsx` to `.tsx`
- [ ] Add React.FC type annotation
- [ ] Define interfaces for component props and state
- [ ] Type all event handlers
- [ ] Type API responses and function returns
- [ ] Add proper error handling with type guards
- [ ] Import and use shared types from `types/index.ts`
- [ ] Remove any `console.log` statements
- [ ] Add accessibility attributes where needed
- [ ] Test the component thoroughly

## Next Components to Convert

1. **High Priority** (Core functionality)
   - `Components/Auth/Login.jsx` ✅ (Example above)
   - `Components/Common/ProtectedRoute.jsx`
   - `hooks/useAuth.js`
   - `services/authService.js`

2. **Medium Priority** (Frequently used)
   - `Components/User/UsersList.jsx`
   - `Components/Attendance/AttendanceUserList.jsx`
   - `layout/Sidebar.jsx`
   - `pages/Home.jsx`

3. **Low Priority** (Less critical)
   - Form components
   - Utility components
   - Test files

Start with utility functions and hooks, then move to components, as they're easier to convert and provide immediate benefits. 