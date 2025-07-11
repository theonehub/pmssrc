import React, { useState, ReactNode } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Divider,
  Paper,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Card,
  CardContent,
  Snackbar,
  Alert,
  AlertColor,
  SelectChangeEvent
} from '@mui/material';
import {
  Person as PersonIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  Badge as BadgeIcon,
  CalendarToday as CalendarIcon,
  Business as BusinessIcon,
  LocationOn as LocationIcon,
  Numbers as NumbersIcon,
  Security as SecurityIcon,
  ArrowBack as ArrowBackIcon,
  AccountBalance as AccountBalanceIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import dataService from '../../shared/services/dataService';

// Define interfaces
interface UserFormData {
  employee_id: string;
  name: string;
  email: string;
  gender: string;
  date_of_birth: string;
  date_of_joining: string;
  mobile: string;
  manager_id: string;
  password: string;
  role: string;
  pan_number: string;
  uan_number: string;
  aadhar_number: string;
  department: string;
  designation: string;
  location: string;
  esi_number: string;
  
  // Bank Details
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

interface FormSectionProps {
  title: string;
  children: ReactNode;
}

const EmptyUser: UserFormData = {
  employee_id: '',
  name: '',
  email: '',
  gender: '',
  date_of_birth: '',
  date_of_joining: '',
  mobile: '',
  manager_id: '',
  password: '',
  role: '',
  pan_number: '',
  uan_number: '',
  aadhar_number: '',
  department: '',
  designation: '',
  location: '',
  esi_number: '',
  
  // Bank Details
  bank_account_number: '',
  bank_name: '',
  ifsc_code: '',
  account_holder_name: '',
  branch_name: '',
  account_type: ''
};

const FormSection: React.FC<FormSectionProps> = ({ title, children }) => (
  <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
    <Typography variant="h6" color="primary" gutterBottom>
      {title}
    </Typography>
    <Divider sx={{ mb: 3 }} />
    <Box sx={{ 
      display: 'grid', 
      gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)' }, 
      gap: 3 
    }}>
      {children}
    </Box>
  </Paper>
);

const AddNewUser: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<UserFormData>(EmptyUser);
  const [files, setFiles] = useState<FileState>({
    panFile: null,
    aadharFile: null,
    photo: null
  });
  const [errors, setErrors] = useState<ErrorState>({});
  const [fileErrors, setFileErrors] = useState<ErrorState>({});
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [toast, setToast] = useState<ToastState>({
    open: false,
    message: '',
    severity: 'success'
  });

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
      showToast(error, 'error');
      return;
    }

    setFiles(prev => ({ ...prev, [fileType]: file }));
    setFileErrors(prev => ({ ...prev, [fileType]: '' }));
    showToast(`${file.name} uploaded successfully`, 'success');
  };

  const handleFileRemove = (fileType: keyof FileState): void => {
    setFiles(prev => ({ ...prev, [fileType]: null }));
    setFileErrors(prev => ({ ...prev, [fileType]: '' }));
  };

  const validateField = (name: keyof UserFormData, value: string): string => {
    const strValue = typeof value === 'string' ? value.trim() : String(value ?? '').trim();

    switch (name) {
      case 'employee_id':
        return !strValue ? 'Employee ID is required' : '';
      case 'name':
        return !strValue ? 'Full name is required' : '';
      case 'email':
        if (!strValue) return 'Email is required';
        if (!/^\S+@\S+\.\S+$/.test(value)) {
          return 'Invalid email format';
        }
        return '';
      case 'gender':
        return !strValue ? 'Gender is required' : '';
      case 'date_of_birth':
        return value ? '' : 'Date of birth is required';
      case 'date_of_joining':
        return value ? '' : 'Date of joining is required';
      case 'mobile':
        if (!strValue) return 'Mobile number is required';
        if (!/^\d{10}$/.test(value.replace(/\D/g, ''))) {
          return 'Mobile must be 10 digits';
        }
        return '';
      case 'password':
        if (!strValue) return 'Password is required';
        if (value.length < 6) {
          return 'Password must be at least 6 characters';
        }
        return '';
      case 'role':
        return !strValue ? 'Role is required' : '';
      case 'pan_number':
        if (value && !/^[A-Z]{5}[0-9]{4}[A-Z]{1}$/.test(value)) {
          return 'Invalid PAN format (e.g., ABCDE1234F)';
        }
        return '';
      case 'aadhar_number':
        if (value && !/^\d{12}$/.test(value.replace(/\D/g, ''))) {
          return 'Aadhar must be 12 digits';
        }
        return '';
      case 'uan_number':
        if (value && !/^\d{12}$/.test(value.replace(/\D/g, ''))) {
          return 'UAN must be 12 digits';
        }
        return '';
      case 'esi_number':
        if (value && !/^\d{10}$/.test(value.replace(/\D/g, ''))) {
          return 'ESI number must be 10 digits';
        }
        return '';
      case 'bank_account_number':
        if (value && (value.length < 9 || value.length > 18)) {
          return 'Account number must be between 9 and 18 characters';
        }
        return '';
      case 'ifsc_code':
        if (value && !/^[A-Z]{4}0[A-Z0-9]{6}$/.test(value.toUpperCase())) {
          return 'Invalid IFSC code format (e.g., SBIN0001234)';
        }
        return '';
      case 'account_holder_name':
        if (value && !/^[A-Za-z\s.-]+$/.test(value)) {
          return 'Account holder name can only contain letters, spaces, dots, and hyphens';
        }
        return '';
      default:
        return '';
    }
  };

  const validate = (): boolean => {
    const newErrors: ErrorState = {};
    
    // Validate all fields
    Object.keys(formData).forEach(field => {
      const error = validateField(field as keyof UserFormData, formData[field as keyof UserFormData]);
      if (error) {
        newErrors[field] = error;
      }
    });

    // Check for file errors (only if files are uploaded)
    const hasFileErrors = Object.values(fileErrors).some(error => error !== null && error !== undefined && error !== '');
    if (hasFileErrors) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.log('File errors found:', fileErrors);
      }
      showToast('Please fix file upload errors before submitting', 'error');
      return false;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    const { name, value } = e.target;
    
    // Real-time validation
    const error = validateField(name as keyof UserFormData, value);
    setErrors(prev => ({
      ...prev,
      [name]: error
    }));
    
    // Update form data
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSelectChange = (e: SelectChangeEvent<string>): void => {
    const { name, value } = e.target;
    
    // Real-time validation
    const error = validateField(name as keyof UserFormData, value);
    setErrors(prev => ({
      ...prev,
      [name]: error
    }));
    
    // Update form data
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    
    if (!validate()) {
      showToast('Please fix the errors before submitting', 'error');
      return;
    }

    setIsSubmitting(true);
    try {
      const hasFiles = files.panFile || files.aadharFile || files.photo;
      
      if (hasFiles) {
        // Only include non-null files in the payload
        const filePayload: { panFile?: File; aadharFile?: File; photo?: File } = {};
        if (files.panFile) filePayload.panFile = files.panFile;
        if (files.aadharFile) filePayload.aadharFile = files.aadharFile;
        if (files.photo) filePayload.photo = files.photo;
        await dataService.createUserWithFiles(formData, filePayload);
      } else {
        await dataService.createUser(formData);
      }
      
      showToast('User created successfully!', 'success');
      setTimeout(() => {
        navigate('/users');
      }, 1500);
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error creating user:', error);
      }
      let errorMessage = 'Failed to create user';
      
      if (error.response?.data?.detail) {
        // Handle different types of error responses
        const detail = error.response.data.detail;
        if (typeof detail === 'string') {
          errorMessage = detail;
        } else if (Array.isArray(detail)) {
          // Handle validation errors array
          errorMessage = detail.map((err: any) => err.msg || err.message || 'Validation error').join(', ');
        } else if (typeof detail === 'object' && detail.msg) {
          // Handle single validation error object
          errorMessage = detail.msg;
        } else {
          errorMessage = 'Validation failed';
        }
      } else if (error.response?.data?.message) {
        // Handle specific error messages
        errorMessage = error.response.data.message;
      } else if (error.response?.status === 422) {
        // Handle 422 validation errors
        if (error.response.data?.detail?.includes('employee strength') || 
            error.response.data?.detail?.includes('capacity') ||
            error.response.data?.detail?.includes('employee limit')) {
          errorMessage = 'Cannot create user: Organisation has reached its employee capacity limit. Please contact your administrator.';
        } else {
          errorMessage = 'Validation failed. Please check your input and try again.';
        }
      } else if (error.response?.status === 400) {
        // Handle 400 bad request errors
        if (error.response.data?.detail?.includes('employee strength') || 
            error.response.data?.detail?.includes('capacity') ||
            error.response.data?.detail?.includes('employee limit')) {
          errorMessage = 'Cannot create user: Organisation has reached its employee capacity limit. Please contact your administrator.';
        } else {
          errorMessage = 'Invalid request. Please check your input and try again.';
        }
      }
      
      showToast(errorMessage, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const showToast = (message: string, severity: AlertColor = 'success'): void => {
    setToast({ open: true, message, severity });
  };

  const handleCloseToast = (): void => {
    setToast(prev => ({ ...prev, open: false }));
  };

  return (
    <Box>
      {/* Header */}
      <Card elevation={1} sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Button
              startIcon={<ArrowBackIcon />}
              onClick={() => navigate('/users')}
              variant="outlined"
              size="small"
            >
              Back
            </Button>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Fill in the user details to create a new account
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>

      <Box component="form" onSubmit={handleSubmit} sx={{ maxWidth: 900, mx: 'auto' }}>
        {/* Basic Information Section */}
        <FormSection title="Basic Information">
          <TextField
            fullWidth
            label="Employee ID"
            name="employee_id"
            value={formData.employee_id}
            onChange={handleChange}
            error={!!errors.employee_id}
            helperText={errors.employee_id}
            required
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
            name="name"
            value={formData.name}
            onChange={handleChange}
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
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
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

          <FormControl fullWidth required error={!!errors.gender}>
            <InputLabel>Gender</InputLabel>
            <Select 
              name="gender" 
              label="Gender"
              value={formData.gender}
              onChange={handleSelectChange}
            >
              <MenuItem value="male">Male</MenuItem>
              <MenuItem value="female">Female</MenuItem>
            </Select>
            {errors.gender && (
              <Typography variant="caption" color="error" sx={{ mt: 0.5, ml: 2 }}>
                {typeof errors.gender === 'string' ? errors.gender : 'Invalid selection'}
              </Typography>
            )}
          </FormControl>

          <TextField
            fullWidth
            label="Date of Birth"
            name="date_of_birth"
            type="date"
            value={formData.date_of_birth}
            onChange={handleChange}
            error={!!errors.date_of_birth}
            helperText={errors.date_of_birth}
            required
            InputLabelProps={{ shrink: true }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <CalendarIcon color="action" />
                </InputAdornment>
              ),
            }}
          />

          <TextField
            fullWidth
            label="Date of Joining"
            name="date_of_joining"
            type="date"
            value={formData.date_of_joining}
            onChange={handleChange}
            error={!!errors.date_of_joining}
            helperText={errors.date_of_joining}
            required
            InputLabelProps={{ shrink: true }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <CalendarIcon color="action" />
                </InputAdornment>
              ),
            }}
          />

          <TextField
            fullWidth
            label="Mobile Number"
            name="mobile"
            value={formData.mobile}
            onChange={handleChange}
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

          <TextField
            fullWidth
            label="Password"
            name="password"
            type="password"
            value={formData.password}
            onChange={handleChange}
            error={!!errors.password}
            helperText={errors.password}
            required
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SecurityIcon color="action" />
                </InputAdornment>
              ),
            }}
          />
        </FormSection>

        {/* Work Information Section */}
        <FormSection title="Work Information">
          <FormControl fullWidth required error={!!errors.role}>
            <InputLabel>Role</InputLabel>
            <Select 
              name="role" 
              label="Role"
              value={formData.role}
              onChange={handleSelectChange}
            >
              <MenuItem value="user">User</MenuItem>
              <MenuItem value="manager">Manager</MenuItem>
            </Select>
            {errors.role && (
              <Typography variant="caption" color="error" sx={{ mt: 0.5, ml: 2 }}>
                {typeof errors.role === 'string' ? errors.role : 'Invalid selection'}
              </Typography>
            )}
          </FormControl>

          <TextField
            fullWidth
            label="Manager ID"
            name="manager_id"
            value={formData.manager_id}
            onChange={handleChange}
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
            label="Department"
            name="department"
            value={formData.department}
            onChange={handleChange}
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
            name="designation"
            value={formData.designation}
            onChange={handleChange}
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
            label="Location"
            name="location"
            value={formData.location}
            onChange={handleChange}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <LocationIcon color="action" />
                </InputAdornment>
              ),
            }}
          />
        </FormSection>

        {/* Document Information Section */}
        <FormSection title="Document Information">
          <TextField
            fullWidth
            label="PAN Number"
            name="pan_number"
            value={formData.pan_number}
            onChange={handleChange}
            error={!!errors.pan_number}
            helperText={errors.pan_number}
            placeholder="ABCDE1234F"
            inputProps={{ style: { textTransform: 'uppercase' } }}
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
            name="aadhar_number"
            value={formData.aadhar_number}
            onChange={handleChange}
            error={!!errors.aadhar_number}
            helperText={errors.aadhar_number}
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
            label="UAN Number"
            name="uan_number"
            value={formData.uan_number}
            onChange={handleChange}
            error={!!errors.uan_number}
            helperText={errors.uan_number}
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
            name="esi_number"
            value={formData.esi_number}
            onChange={handleChange}
            error={!!errors.esi_number}
            helperText={errors.esi_number}
            placeholder="1234567890"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <NumbersIcon color="action" />
                </InputAdornment>
              ),
            }}
          />
        </FormSection>

        {/* Bank Details Section */}
        <FormSection title="Bank Details (Optional)">
          <TextField
            fullWidth
            label="Bank Account Number"
            name="bank_account_number"
            value={formData.bank_account_number}
            onChange={handleChange}
            error={!!errors.bank_account_number}
            helperText={errors.bank_account_number}
            placeholder="Enter account number"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <AccountBalanceIcon color="action" />
                </InputAdornment>
              ),
            }}
          />

          <TextField
            fullWidth
            label="Bank Name"
            name="bank_name"
            value={formData.bank_name}
            onChange={handleChange}
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
            label="IFSC Code"
            name="ifsc_code"
            value={formData.ifsc_code}
            onChange={handleChange}
            error={!!errors.ifsc_code}
            helperText={errors.ifsc_code}
            placeholder="SBIN0001234"
            inputProps={{ style: { textTransform: 'uppercase' } }}
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
            label="Account Holder Name"
            name="account_holder_name"
            value={formData.account_holder_name}
            onChange={handleChange}
            error={!!errors.account_holder_name}
            helperText={errors.account_holder_name}
            placeholder="As per bank records"
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
            label="Branch Name"
            name="branch_name"
            value={formData.branch_name}
            onChange={handleChange}
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
              name="account_type" 
              label="Account Type"
              value={formData.account_type}
              onChange={handleSelectChange}
            >
              <MenuItem value="">Select Account Type</MenuItem>
              <MenuItem value="savings">Savings</MenuItem>
              <MenuItem value="current">Current</MenuItem>
              <MenuItem value="salary">Salary</MenuItem>
            </Select>
          </FormControl>
        </FormSection>

        {/* File Uploads Section */}
        <FormSection title="📎 Document Uploads - COMPLETELY OPTIONAL">
          <Box sx={{ gridColumn: '1 / -1' }}>
            <Alert severity="success" sx={{ mb: 3 }}>
              <Typography variant="body2">
                <strong>✅ No file uploads required!</strong> You can create the user account with just the basic information above. 
                Document uploads are completely optional and can be added anytime later.
              </Typography>
            </Alert>
          </Box>
          
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
                  id="pan-file-input"
                />
                <label htmlFor="pan-file-input">
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
                  id="aadhar-file-input"
                />
                <label htmlFor="aadhar-file-input">
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
                  id="photo-file-input"
                />
                <label htmlFor="photo-file-input">
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
        </FormSection>

        {/* Submit Button */}
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
          <Button 
            onClick={() => navigate('/users')}
            size="large"
            sx={{ minWidth: 120 }}
          >
            Cancel
          </Button>
          <Button 
            type="submit" 
            variant="contained" 
            size="large"
            disabled={isSubmitting}
            sx={{ minWidth: 120 }}
          >
            {isSubmitting ? 'Creating...' : 'Create User'}
          </Button>
        </Box>
      </Box>

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

export default AddNewUser; 