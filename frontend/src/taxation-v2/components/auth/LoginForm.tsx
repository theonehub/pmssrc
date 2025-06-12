import React, { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  FormControlLabel,
  Checkbox,
  Link,
  Alert,
  IconButton,
  InputAdornment,
  Divider,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Email,
  Lock,
  Google,
  Apple,
  Facebook
} from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

import { Card, Button } from '../ui';
import { useAuth } from './AuthProvider';

// =============================================================================
// VALIDATION SCHEMA
// =============================================================================

const loginSchema = z.object({
  email: z.string()
    .min(1, 'Email is required')
    .email('Invalid email address'),
  password: z.string()
    .min(6, 'Password must be at least 6 characters'),
  rememberMe: z.boolean().optional()
});

type LoginFormData = z.infer<typeof loginSchema>;

// =============================================================================
// INTERFACES
// =============================================================================

interface LoginFormProps {
  onSwitchToRegister: () => void;
  onForgotPassword: () => void;
  onSuccess?: () => void;
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export const LoginForm: React.FC<LoginFormProps> = ({
  onSwitchToRegister,
  onForgotPassword,
  onSuccess
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  
  const { signIn, error } = useAuth();

  // =============================================================================
  // FORM SETUP
  // =============================================================================

  const {
    control,
    handleSubmit,
    formState: { errors },
    setError
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
      rememberMe: false
    }
  });

  // =============================================================================
  // EVENT HANDLERS
  // =============================================================================

  const onSubmit = async (data: LoginFormData) => {
    try {
      setIsLoading(true);
      await signIn(data.email, data.password);
      onSuccess?.();
    } catch (error: any) {
      console.error('Login error:', error);
      
      // Handle specific Firebase auth errors
      switch (error.code) {
        case 'auth/user-not-found':
          setError('email', { message: 'No account found with this email' });
          break;
        case 'auth/wrong-password':
          setError('password', { message: 'Incorrect password' });
          break;
        case 'auth/invalid-email':
          setError('email', { message: 'Invalid email address' });
          break;
        case 'auth/user-disabled':
          setError('email', { message: 'This account has been disabled' });
          break;
        case 'auth/too-many-requests':
          setError('password', { message: 'Too many failed attempts. Please try again later.' });
          break;
        default:
          // Generic error handling is done by AuthProvider
          break;
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSocialLogin = async (provider: 'google' | 'apple' | 'facebook') => {
    // Placeholder for social login implementation
    console.log(`Social login with ${provider}`);
    // TODO: Implement social login
  };

  // =============================================================================
  // RENDER
  // =============================================================================

  return (
    <Card sx={{ maxWidth: 400, mx: 'auto', p: 4 }}>
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          Welcome Back
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Sign in to access your tax dashboard
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <form onSubmit={handleSubmit(onSubmit)}>
        <Box sx={{ mb: 3 }}>
          <Controller
            name="email"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                fullWidth
                label="Email Address"
                type="email"
                error={!!errors.email}
                helperText={errors.email?.message}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Email color="action" />
                    </InputAdornment>
                  ),
                }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    fontSize: isMobile ? 16 : 14, // Prevent zoom on mobile
                  }
                }}
              />
            )}
          />
        </Box>

        <Box sx={{ mb: 3 }}>
          <Controller
            name="password"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                fullWidth
                label="Password"
                type={showPassword ? 'text' : 'password'}
                error={!!errors.password}
                helperText={errors.password?.message}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Lock color="action" />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowPassword(!showPassword)}
                        edge="end"
                        aria-label="toggle password visibility"
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    fontSize: isMobile ? 16 : 14, // Prevent zoom on mobile
                  }
                }}
              />
            )}
          />
        </Box>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Controller
            name="rememberMe"
            control={control}
            render={({ field }) => (
              <FormControlLabel
                control={<Checkbox {...field} checked={field.value || false} />}
                label="Remember me"
              />
            )}
          />
          
          <Link
            component="button"
            variant="body2"
            onClick={(e) => {
              e.preventDefault();
              onForgotPassword();
            }}
            sx={{ textDecoration: 'none' }}
          >
            Forgot password?
          </Link>
        </Box>

        <Button
          type="submit"
          variant="contained"
          fullWidth
          size="large"
          loading={isLoading}
          sx={{ mb: 3, py: 1.5 }}
        >
          Sign In
        </Button>

        <Divider sx={{ my: 3 }}>
          <Typography variant="body2" color="text.secondary">
            Or continue with
          </Typography>
        </Divider>

        <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
          <Button
            variant="outlined"
            fullWidth
            startIcon={<Google />}
            onClick={() => handleSocialLogin('google')}
            sx={{ py: 1.5 }}
          >
            Google
          </Button>
          
          {!isMobile && (
            <>
              <Button
                variant="outlined"
                fullWidth
                startIcon={<Apple />}
                onClick={() => handleSocialLogin('apple')}
                sx={{ py: 1.5 }}
              >
                Apple
              </Button>
              
              <Button
                variant="outlined"
                fullWidth
                startIcon={<Facebook />}
                onClick={() => handleSocialLogin('facebook')}
                sx={{ py: 1.5 }}
              >
                Facebook
              </Button>
            </>
          )}
        </Box>

        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            Don't have an account?{' '}
            <Link
              component="button"
              variant="body2"
              onClick={(e) => {
                e.preventDefault();
                onSwitchToRegister();
              }}
              sx={{ fontWeight: 'bold', textDecoration: 'none' }}
            >
              Sign up
            </Link>
          </Typography>
        </Box>
      </form>
    </Card>
  );
};

export default LoginForm; 