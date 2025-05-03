import React, { useState } from 'react';
import axios from '../../utils/axios';
import { useNavigate } from 'react-router-dom';
import {
  Button,
  TextField,
  Container,
  Grid,
  Card,
  CardHeader,
  CardContent,
  Alert,
  Box,
  Typography,
  IconButton,
  InputAdornment,
  Divider
} from '@mui/material';
import { Visibility, VisibilityOff, LockOutlined } from '@mui/icons-material';

const hostname = window.location.hostname;

const Login = () => {
  const [empId, setEmpId] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const formData = new URLSearchParams();
      formData.append('username', empId);
      formData.append('password', password);
      formData.append('hostname', hostname);

      const res = await axios.post('/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      localStorage.setItem('token', res.data.access_token);
      navigate('/home');
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid credentials');
    }
  };

  return (
    <Container maxWidth="sm" sx={{ 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center', 
      minHeight: '100vh' 
    }}>
      <Card sx={{ width: '100%', p: 2, boxShadow: 8, borderRadius: 3 }}>
        <CardHeader
          avatar={<LockOutlined color="primary" />}
          title={
            <Typography variant="h5" align="center" sx={{ fontWeight: 'bold' }}>
              Employee Portal Login
            </Typography>
          }
          sx={{ bgcolor: 'primary.light', color: 'white', textAlign: 'center' }}
        />
        <Divider />
        <CardContent>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          <Box component="form" onSubmit={handleSubmit} noValidate>
            <TextField
              margin="normal"
              required
              fullWidth
              id="empId"
              label="Employee ID"
              name="empId"
              autoComplete="username"
              autoFocus
              value={empId}
              onChange={(e) => setEmpId(e.target.value)}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type={showPassword ? 'text' : 'password'}
              id="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              InputProps={{
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
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              color="primary"
              sx={{ mt: 3, mb: 2, fontWeight: 'bold' }}
            >
              Login
            </Button>
            <Typography variant="body2" align="center" color="text.secondary">
              Having trouble? <a href="/support" style={{ textDecoration: 'none' }}>Contact Support</a>
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Container>
  );
};

export default Login;
