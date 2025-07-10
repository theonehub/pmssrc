import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  IconButton,
  CircularProgress,
  Alert,
  Skeleton,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  InputAdornment,
  Divider,
  Avatar,
  Snackbar,
  SelectChangeEvent,
  AlertColor
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Save as SaveIcon,
  Person as PersonIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  Business as BusinessIcon,
  Badge as BadgeIcon,
  LocationOn as LocationIcon,
  Numbers as NumbersIcon,
  CloudUpload as CloudUploadIcon,
  DateRange as DateRangeIcon
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import dataService from '../../shared/services/dataService';

// Define interfaces
interface User {
  employee_id: string;
  name: string;
  email: string;
  date_of_birth?: string;
  date_of_joining?: string;
  gender?: string;
  mobile?: string;
  department?: string;
  designation?: string;
  role?: string;
  manager_id?: string;
  location?: string;
  address?: string;
  emergency_contact?: string;
  blood_group?: string;
  pan_number?: string;
  aadhar_number?: string;
  uan_number?: string;
  esi_number?: string;
  created_at?: string;
  updated_at?: string;
  is_active?: boolean;
  status?: string;
  bank_account_number?: string;
  bank_name?: string;
  ifsc_code?: string;
  account_holder_name?: string;
  branch_name?: string;
  account_type?: string;
}

interface UserFormData {
  employee_id: string;
  name: string;
  email: string;
  gender: string;
  date_of_birth: string;
  date_of_joining: string;
  mobile: string;
  manager_id: string;
  role: string;
  pan_number: string;
  uan_number: string;
  aadhar_number: string;
  department: string;
  designation: string;
  location: string;
  esi_number: string;
  password: string;
  // Banking details
  bank_account_number: string;
  bank_name: string;
  ifsc_code: string;
  account_holder_name: string;
  branch_name: string;
  account_type: string;
}

interface FileState {
  panFile: File | null;
  aadharFile: File | null;
  photo: File | null;
}

interface ErrorState {
  [key: string]: string;
}

interface ToastState {
  open: boolean;
  message: string;
  severity: AlertColor;
}

const UserEdit: React.FC = () => {
  const { empId } = useParams<{ empId: string }>();
  const navigate = useNavigate();
  
  const [user, setUser] = useState<User | null>(null);
  const [formData, setFormData] = useState<UserFormData>({
    employee_id: '',
    name: '',
    email: '',
    gender: '',
    date_of_birth: '',
    date_of_joining: '',
    mobile: '',
    manager_id: '',
    role: '',
    pan_number: '',
    uan_number: '',
    aadhar_number: '',
    department: '',
    designation: '',
    location: '',
    esi_number: '',
    password: '',
    // Banking details
    bank_account_number: '',
    bank_name: '',
    ifsc_code: '',
    account_holder_name: '',
    branch_name: '',
    account_type: ''
  });
  const [files, setFiles] = useState<FileState>({
    panFile: null,
    aadharFile: null,
    photo: null
  });
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [errors, setErrors] = useState<ErrorState>({});
  const [fileErrors, setFileErrors] = useState<ErrorState>({});
  const [toast, setToast] = useState<ToastState>({
    open: false,
    message: '',
    severity: 'success'
  });

  const fetchUser = useCallback(async (): Promise<void> => {
    if (!empId) return;

    setLoading(true);
    try {
      // Try to get user by ID first, then fall back to legacy endpoint if needed
      let userData: User | null = null;
      try {
        userData = await dataService.getUserById(empId);
      } catch (error: any) {
        // If the direct lookup fails, try the legacy endpoint
        if (error.response?.status === 404) {
          userData = await dataService.getUserByEmpIdLegacy(empId);
        } else {
          throw error;
        }
      }
      
      if (userData) {
        setUser(userData);
        
        // Helper function to format dates for input[type="date"]
        const formatDateForInput = (dateString?: string): string => {
          if (!dateString) return '';
          
          try {
            // Handle different date formats
            let date: Date;
            
            if (dateString.includes('T')) {
              // ISO format with time: "2023-12-25T00:00:00Z"
              date = new Date(dateString);
            } else if (dateString.includes('-')) {
              // Already in YYYY-MM-DD format: "2023-12-25"
              if (dateString.length === 10) {
                return dateString;
              }
              date = new Date(dateString);
            } else {
              // Other formats, let Date constructor handle it
              date = new Date(dateString);
            }
            
            // Check if date is valid
            if (isNaN(date.getTime())) {
              if (process.env.NODE_ENV === 'development') {
                console.warn('Invalid date:', dateString);
              }
              return '';
            }
            
            // Format to YYYY-MM-DD for input[type="date"]
            const isoString = date.toISOString();
            const parts = isoString.split('T');
            return parts.length > 0 && parts[0] ? parts[0] : '';
          } catch (error) {
            if (process.env.NODE_ENV === 'development') {
              console.warn('Error formatting date:', dateString, error);
            }
            return '';
          }
        };
        
        const newFormData = {
          employee_id: userData.employee_id || '',
          name: userData.name || '',
          email: userData.email || '',
          gender: userData.gender || '',
          date_of_birth: formatDateForInput(userData.date_of_birth),
          date_of_joining: formatDateForInput(userData.date_of_joining),
          mobile: userData.mobile || '',
          manager_id: userData.manager_id || '',
          role: userData.role || '',
          pan_number: userData.pan_number || '',
          uan_number: userData.uan_number || '',
          aadhar_number: userData.aadhar_number || '',
          department: userData.department || '',
          designation: userData.designation || '',
          location: userData.location || '',
          esi_number: userData.esi_number || '',
          password: '',  // Empty password for updates
          // Banking details
          bank_account_number: userData.bank_account_number || '',
          bank_name: userData.bank_name || '',
          ifsc_code: userData.ifsc_code || '',
          account_holder_name: userData.account_holder_name || '',
          branch_name: userData.branch_name || '',
          account_type: userData.account_type || ''
        };
        
        setFormData(newFormData);
      } else {
        throw new Error('User not found');
      }
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error fetching user:', error);
      }
      setError(error.response?.data?.detail || error.message || 'Failed to fetch user details');
    } finally {
      setLoading(false);
    }
  }, [empId]);

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  const validateFile = (file: File, type: 'photo' | 'document'): string | null => {
    const maxSizes = {
      photo: 2 * 1024 * 1024, // 2MB
      document: 5 * 1024 * 1024 // 5MB
    };

    const allowedTypes = {
      photo: ['image/jpeg', 'image/png'],
      document: ['image/jpeg', 'image/png', 'application/pdf']
    };

    const fileType = type === 'photo' ? 'photo' : 'document';
    const maxSize = maxSizes[fileType];
    const allowed = allowedTypes[fileType];

    if (file.size > maxSize) {
      return `File size must be less than ${maxSize / 1024 / 1024}MB`;
    }

    if (!allowed.includes(file.type)) {
      return `Invalid file type. Allowed: ${fileType === 'photo' ? 'JPG, PNG' : 'JPG, PNG, PDF'}`;
    }

    return null;
  };

  const handleFileSelect = (fileType: keyof FileState, file: File): void => {
    const error = validateFile(file, fileType === 'photo' ? 'photo' : 'document');
    
    if (error) {
      setFileErrors(prev => ({ ...prev, [fileType]: error }));
      return;
    }

    setFiles(prev => ({ ...prev, [fileType]: file }));
    setFileErrors(prev => ({ ...prev, [fileType]: '' }));
  };

  const handleFileRemove = (fileType: keyof FileState): void => {
    setFiles(prev => ({ ...prev, [fileType]: null }));
    setFileErrors(prev => ({ ...prev, [fileType]: '' }));
  };

  const validateForm = (): boolean => {
    const newErrors: ErrorState = {};
    
    if (!formData.name?.trim()) {
      newErrors.name = 'Name is required';
    }
    
    if (!formData.email?.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }
    
    if (!formData.mobile?.trim()) {
      newErrors.mobile = 'Mobile is required';
    } else if (!/^\d{10}$/.test(formData.mobile.replace(/\D/g, ''))) {
      newErrors.mobile = 'Mobile must be 10 digits';
    }
    
    // Note: Password is not required for updates - backend will use existing password if not provided
    
    // Check for file errors (only if files are uploaded)
    const hasFileErrors = Object.values(fileErrors).some(error => error !== null && error !== undefined && error !== '');
    if (hasFileErrors) {
      showToast('Please fix file upload errors before submitting', 'error');
      return false;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (field: keyof UserFormData, value: string): void => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const handleSelectChange = (e: SelectChangeEvent<string>, field: keyof UserFormData): void => {
    handleChange(field, e.target.value);
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    
    if (!validateForm()) {
      showToast('Please fix the errors before submitting', 'error');
      return;
    }
    
    setSaving(true);
    try {
      const hasFiles = files.panFile || files.aadharFile || files.photo;
      
      if (hasFiles) {
        // For file uploads, we might need to implement a separate endpoint
        // For now, let's use the regular update and handle files separately
        showToast('File upload during edit will be implemented soon. User data updated.', 'info');
        await dataService.updateUserLegacy(empId!, formData);
      } else {
        // Use the regular endpoint
        await dataService.updateUserLegacy(empId!, formData);
      }
      
      showToast('User updated successfully!', 'success');
      setTimeout(() => {
        navigate(`/users/emp/${empId}`);
      }, 1500);
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error updating user:', error);
      }
      const errorMessage = error.response?.data?.detail || 'Failed to update user';
      showToast(errorMessage, 'error');
    } finally {
      setSaving(false);
    }
  };

  const showToast = (message: string, severity: AlertColor = 'success'): void => {
    setToast({ open: true, message, severity });
  };

  const handleCloseToast = (): void => {
    setToast(prev => ({ ...prev, open: false }));
  };

  const getInitials = (name: string): string => {
    if (!name) return 'U';
    return name.split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  if (loading) {
    return (
      <Box>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <Skeleton variant="circular" width={60} height={60} sx={{ mr: 2 }} />
              <Box>
                <Skeleton variant="text" width={200} height={32} />
                <Skeleton variant="text" width={100} height={24} />
              </Box>
            </Box>
            <Box sx={{ 
              display: 'grid', 
              gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, 
              gap: 3 
            }}>
              {Array.from({ length: 12 }).map((_, index) => (
                <Skeleton key={index} variant="text" width="100%" height={56} />
              ))}
            </Box>
          </CardContent>
        </Card>
      </Box>
    );
  }

  if (error) {
    return (
      <Box>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
        <Button
          variant="contained"
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/users')}
        >
          Back to Users
        </Button>
      </Box>
    );
  }

  if (!user) {
    return (
      <Box>
        <Alert severity="warning" sx={{ mb: 3 }}>
          User not found
        </Alert>
        <Button
          variant="contained"
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/users')}
        >
          Back to Users
        </Button>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Card elevation={1} sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <IconButton 
                onClick={() => navigate(`/users/emp/${empId}`)}
                color="primary"
              >
                <ArrowBackIcon />
              </IconButton>
              <Avatar 
                sx={{ 
                  width: 60, 
                  height: 60, 
                  fontSize: '1.25rem',
                  bgcolor: 'primary.main'
                }}
              >
                {getInitials(formData.name)}
              </Avatar>
              <Box>
                <Typography variant="h4" color="primary" gutterBottom>
                  Edit User: {user.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Employee ID: {user.employee_id}
                </Typography>
              </Box>
            </Box>
          </Box>
        </CardContent>
      </Card>

      <form onSubmit={handleSubmit}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {/* Basic Information */}
          <Card elevation={1}>
            <CardContent>
              <Typography variant="h6" color="primary" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <PersonIcon />
                Basic Information
              </Typography>
              <Divider sx={{ mb: 3 }} />
              
              <Box sx={{ 
                display: 'grid', 
                gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, 
                gap: 3 
              }}>
                <TextField
                  fullWidth
                  label="Employee ID"
                  value={formData.employee_id}
                  onChange={(e) => handleChange('employee_id', e.target.value)}
                  disabled
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <BadgeIcon color="action" />
                      </InputAdornment>
                    ),
                  }}
                />
                
                <TextField
                  fullWidth
                  label="Full Name"
                  value={formData.name}
                  onChange={(e) => handleChange('name', e.target.value)}
                  error={!!errors.name}
                  helperText={errors.name}
                  required
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <PersonIcon color="action" />
                      </InputAdornment>
                    ),
                  }}
                />
                
                <TextField
                  fullWidth
                  label="Email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleChange('email', e.target.value)}
                  error={!!errors.email}
                  helperText={errors.email}
                  required
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <EmailIcon color="action" />
                      </InputAdornment>
                    ),
                  }}
                />
                
                <TextField
                  fullWidth
                  label="Mobile"
                  value={formData.mobile}
                  onChange={(e) => handleChange('mobile', e.target.value)}
                  error={!!errors.mobile}
                  helperText={errors.mobile}
                  required
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <PhoneIcon color="action" />
                      </InputAdornment>
                    ),
                  }}
                />
                
                <FormControl fullWidth>
                  <InputLabel>Gender</InputLabel>
                  <Select
                    value={formData.gender}
                    label="Gender"
                    onChange={(e) => handleSelectChange(e, 'gender')}
                  >
                    <MenuItem value="male">Male</MenuItem>
                    <MenuItem value="female">Female</MenuItem>
                    <MenuItem value="other">Other</MenuItem>
                    <MenuItem value="prefer_not_to_say">Prefer not to say</MenuItem>
                  </Select>
                </FormControl>
                
                <TextField
                  fullWidth
                  label="Date of Birth"
                  type="date"
                  value={formData.date_of_birth}
                  onChange={(e) => handleChange('date_of_birth', e.target.value)}
                  InputLabelProps={{ shrink: true }}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <DateRangeIcon color="action" />
                      </InputAdornment>
                    )
                  }}
                />
              </Box>
            </CardContent>
          </Card>

          {/* Work Information */}
          <Card elevation={1}>
            <CardContent>
              <Typography variant="h6" color="primary" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <BusinessIcon />
                Work Information
              </Typography>
              <Divider sx={{ mb: 3 }} />
              
              <Box sx={{ 
                display: 'grid', 
                gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, 
                gap: 3 
              }}>
                <TextField
                  fullWidth
                  label="Date of Joining"
                  type="date"
                  value={formData.date_of_joining}
                  onChange={(e) => handleChange('date_of_joining', e.target.value)}
                  InputLabelProps={{ shrink: true }}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <DateRangeIcon color="action" />
                      </InputAdornment>
                    )
                  }}
                />
                
                <FormControl fullWidth>
                  <InputLabel>Role</InputLabel>
                  <Select
                    value={formData.role}
                    label="Role"
                    onChange={(e) => handleSelectChange(e, 'role')}
                  >
                    <MenuItem value="employee">Employee</MenuItem>
                    <MenuItem value="manager">Manager</MenuItem>
                  </Select>
                </FormControl>
                
                <TextField
                  fullWidth
                  label="Department"
                  value={formData.department}
                  onChange={(e) => handleChange('department', e.target.value)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <BusinessIcon color="action" />
                      </InputAdornment>
                    ),
                  }}
                />
                
                <TextField
                  fullWidth
                  label="Designation"
                  value={formData.designation}
                  onChange={(e) => handleChange('designation', e.target.value)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <BadgeIcon color="action" />
                      </InputAdornment>
                    ),
                  }}
                />
                
                <TextField
                  fullWidth
                  label="Manager ID"
                  value={formData.manager_id}
                  onChange={(e) => handleChange('manager_id', e.target.value)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <PersonIcon color="action" />
                      </InputAdornment>
                    ),
                  }}
                />
                
                <TextField
                  fullWidth
                  label="Location"
                  value={formData.location}
                  onChange={(e) => handleChange('location', e.target.value)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <LocationIcon color="action" />
                      </InputAdornment>
                    ),
                  }}
                />
              </Box>
            </CardContent>
          </Card>

          {/* Additional Information */}
          <Card elevation={1}>
            <CardContent>
              <Typography variant="h6" color="primary" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <NumbersIcon />
                Additional Information
              </Typography>
              <Divider sx={{ mb: 3 }} />
              
              <Box sx={{ 
                display: 'grid', 
                gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, 
                gap: 3 
              }}>
                <TextField
                  fullWidth
                  label="PAN Number"
                  value={formData.pan_number}
                  onChange={(e) => handleChange('pan_number', e.target.value)}
                  placeholder="ABCDE1234F"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <NumbersIcon color="action" />
                      </InputAdornment>
                    ),
                  }}
                />
                
                <TextField
                  fullWidth
                  label="Aadhar Number"
                  value={formData.aadhar_number}
                  onChange={(e) => handleChange('aadhar_number', e.target.value)}
                  placeholder="1234 5678 9012"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <NumbersIcon color="action" />
                      </InputAdornment>
                    ),
                  }}
                />
                
                <TextField
                  fullWidth
                  label="UAN Number"
                  value={formData.uan_number}
                  onChange={(e) => handleChange('uan_number', e.target.value)}
                  placeholder="123456789012"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <NumbersIcon color="action" />
                      </InputAdornment>
                    ),
                  }}
                />
                
                <TextField
                  fullWidth
                  label="ESI Number"
                  value={formData.esi_number}
                  onChange={(e) => handleChange('esi_number', e.target.value)}
                  placeholder="1234567890"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <NumbersIcon color="action" />
                      </InputAdornment>
                    ),
                  }}
                />
              </Box>
            </CardContent>
          </Card>

          {/* Banking Details */}
          <Card elevation={1}>
            <CardContent>
              <Typography variant="h6" color="primary" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <BusinessIcon />
                Banking Details
              </Typography>
              <Divider sx={{ mb: 3 }} />
              
              <Box sx={{ 
                display: 'grid', 
                gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, 
                gap: 3 
              }}>
                <TextField
                  fullWidth
                  label="Bank Name"
                  value={formData.bank_name}
                  onChange={(e) => handleChange('bank_name', e.target.value)}
                  placeholder="e.g., State Bank of India"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <BusinessIcon color="action" />
                      </InputAdornment>
                    ),
                  }}
                />
                
                <TextField
                  fullWidth
                  label="Account Holder Name"
                  value={formData.account_holder_name}
                  onChange={(e) => handleChange('account_holder_name', e.target.value)}
                  placeholder="Account holder's full name"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <PersonIcon color="action" />
                      </InputAdornment>
                    ),
                  }}
                />
                
                <TextField
                  fullWidth
                  label="Account Number"
                  value={formData.bank_account_number}
                  onChange={(e) => handleChange('bank_account_number', e.target.value)}
                  placeholder="1234567890"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <NumbersIcon color="action" />
                      </InputAdornment>
                    ),
                  }}
                />
                
                <TextField
                  fullWidth
                  label="IFSC Code"
                  value={formData.ifsc_code}
                  onChange={(e) => handleChange('ifsc_code', e.target.value)}
                  placeholder="SBIN0001234"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <NumbersIcon color="action" />
                      </InputAdornment>
                    ),
                  }}
                />
                
                <TextField
                  fullWidth
                  label="Branch Name"
                  value={formData.branch_name}
                  onChange={(e) => handleChange('branch_name', e.target.value)}
                  placeholder="e.g., Main Branch"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <LocationIcon color="action" />
                      </InputAdornment>
                    ),
                  }}
                />
                
                <FormControl fullWidth>
                  <InputLabel>Account Type</InputLabel>
                  <Select
                    value={formData.account_type}
                    label="Account Type"
                    onChange={(e) => handleSelectChange(e, 'account_type')}
                  >
                    <MenuItem value="savings">Savings Account</MenuItem>
                    <MenuItem value="current">Current Account</MenuItem>
                    <MenuItem value="salary">Salary Account</MenuItem>
                    <MenuItem value="fixed_deposit">Fixed Deposit</MenuItem>
                    <MenuItem value="recurring_deposit">Recurring Deposit</MenuItem>
                  </Select>
                </FormControl>
              </Box>
            </CardContent>
          </Card>

          {/* Document Uploads */}
          <Card elevation={1}>
            <CardContent>
              <Typography variant="h6" color="primary" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CloudUploadIcon />
                📎 Document Uploads - COMPLETELY OPTIONAL
              </Typography>
              <Divider sx={{ mb: 3 }} />
              
              <Alert severity="success" sx={{ mb: 3 }}>
                <Typography variant="body2">
                  <strong>✅ No file uploads required!</strong> You can update the user information without uploading any documents. 
                  Document uploads are completely optional.
                </Typography>
              </Alert>
              
              <Box sx={{ 
                display: 'grid', 
                gridTemplateColumns: { xs: '1fr', md: '1fr 1fr 1fr' }, 
                gap: 3 
              }}>
                <Box sx={{ border: '1px dashed #ccc', borderRadius: 2, p: 2, textAlign: 'center', bgcolor: '#f9f9f9' }}>
                  <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                    📄 PAN Card Document (Optional)
                  </Typography>
                  {files.panFile ? (
                    <Box>
                      <Typography variant="body2" color="success.main">
                        {files.panFile.name}
                      </Typography>
                      <Button 
                        size="small" 
                        color="error" 
                        onClick={() => handleFileRemove('panFile')}
                        sx={{ mt: 1 }}
                      >
                        Remove
                      </Button>
                    </Box>
                  ) : (
                    <Box>
                      <input
                        type="file"
                        accept="image/*,.pdf"
                        onChange={(e) => {
                          if (e.target.files?.[0]) {
                            handleFileSelect('panFile', e.target.files[0]);
                          }
                        }}
                        style={{ display: 'none' }}
                        id="pan-file-input-edit"
                      />
                      <label htmlFor="pan-file-input-edit">
                        <Button variant="outlined" component="span" size="small">
                          Choose File (Optional)
                        </Button>
                      </label>
                      <Typography variant="caption" display="block" color="textSecondary" sx={{ mt: 1 }}>
                        PNG, JPG, PDF up to 5MB
                      </Typography>
                    </Box>
                  )}
                  {fileErrors.panFile && (
                    <Alert severity="error" sx={{ mt: 1 }} variant="outlined">
                      {fileErrors.panFile}
                    </Alert>
                  )}
                </Box>

                <Box sx={{ border: '1px dashed #ccc', borderRadius: 2, p: 2, textAlign: 'center', bgcolor: '#f9f9f9' }}>
                  <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                    📄 Aadhar Card Document (Optional)
                  </Typography>
                  {files.aadharFile ? (
                    <Box>
                      <Typography variant="body2" color="success.main">
                        {files.aadharFile.name}
                      </Typography>
                      <Button 
                        size="small" 
                        color="error" 
                        onClick={() => handleFileRemove('aadharFile')}
                        sx={{ mt: 1 }}
                      >
                        Remove
                      </Button>
                    </Box>
                  ) : (
                    <Box>
                      <input
                        type="file"
                        accept="image/*,.pdf"
                        onChange={(e) => {
                          if (e.target.files?.[0]) {
                            handleFileSelect('aadharFile', e.target.files[0]);
                          }
                        }}
                        style={{ display: 'none' }}
                        id="aadhar-file-input-edit"
                      />
                      <label htmlFor="aadhar-file-input-edit">
                        <Button variant="outlined" component="span" size="small">
                          Choose File (Optional)
                        </Button>
                      </label>
                      <Typography variant="caption" display="block" color="textSecondary" sx={{ mt: 1 }}>
                        PNG, JPG, PDF up to 5MB
                      </Typography>
                    </Box>
                  )}
                  {fileErrors.aadharFile && (
                    <Alert severity="error" sx={{ mt: 1 }} variant="outlined">
                      {fileErrors.aadharFile}
                    </Alert>
                  )}
                </Box>

                <Box sx={{ border: '1px dashed #ccc', borderRadius: 2, p: 2, textAlign: 'center', bgcolor: '#f9f9f9' }}>
                  <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                    📷 Profile Photo (Optional)
                  </Typography>
                  {files.photo ? (
                    <Box>
                      <Typography variant="body2" color="success.main">
                        {files.photo.name}
                      </Typography>
                      <Button 
                        size="small" 
                        color="error" 
                        onClick={() => handleFileRemove('photo')}
                        sx={{ mt: 1 }}
                      >
                        Remove
                      </Button>
                    </Box>
                  ) : (
                    <Box>
                      <input
                        type="file"
                        accept="image/*"
                        onChange={(e) => {
                          if (e.target.files?.[0]) {
                            handleFileSelect('photo', e.target.files[0]);
                          }
                        }}
                        style={{ display: 'none' }}
                        id="photo-file-input-edit"
                      />
                      <label htmlFor="photo-file-input-edit">
                        <Button variant="outlined" component="span" size="small">
                          Choose File (Optional)
                        </Button>
                      </label>
                      <Typography variant="caption" display="block" color="textSecondary" sx={{ mt: 1 }}>
                        PNG, JPG up to 2MB
                      </Typography>
                    </Box>
                  )}
                  {fileErrors.photo && (
                    <Alert severity="error" sx={{ mt: 1 }} variant="outlined">
                      {fileErrors.photo}
                    </Alert>
                  )}
                </Box>
              </Box>
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <Card elevation={1}>
            <CardContent>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button 
                  onClick={() => navigate(`/users/emp/${empId}`)}
                  size="large"
                  disabled={saving}
                >
                  Cancel
                </Button>
                <Button 
                  type="submit" 
                  variant="contained"
                  size="large"
                  disabled={saving}
                  startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
                  sx={{ minWidth: 120 }}
                >
                  {saving ? 'Saving...' : 'Save Changes'}
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Box>
      </form>

      {/* Toast Notifications */}
      <Snackbar 
        open={toast.open} 
        autoHideDuration={6000} 
        onClose={handleCloseToast}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={handleCloseToast} 
          severity={toast.severity}
          sx={{ width: '100%' }}
          variant="filled"
        >
          {toast.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default UserEdit; 