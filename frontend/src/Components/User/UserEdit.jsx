import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Paper,
  Card,
  CardContent,
  Grid,
  TextField,
  Button,
  IconButton,
  Tooltip,
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
  Chip
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Save as SaveIcon,
  Person as PersonIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  Business as BusinessIcon,
  CalendarToday as CalendarIcon,
  Badge as BadgeIcon,
  LocationOn as LocationIcon,
  Numbers as NumbersIcon,
  CloudUpload as CloudUploadIcon,
  Delete as DeleteIcon,
  PhotoCamera as PhotoCameraIcon,
  Description as DescriptionIcon
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../utils/apiUtils';
import PageLayout from '../../layout/PageLayout';

const FileUploadButton = ({ 
  label, 
  file, 
  onFileSelect, 
  onFileRemove, 
  accept, 
  required = false,
  icon 
}) => {
  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      onFileSelect(selectedFile);
    }
  };

  return (
    <Box>
      <Typography variant="subtitle2" gutterBottom>
        {label} {required && <span style={{ color: 'red' }}>*</span>}
      </Typography>
      <Box
        sx={{
          border: '2px dashed',
          borderColor: file ? 'success.main' : 'grey.300',
          borderRadius: 2,
          p: 2,
          textAlign: 'center',
          bgcolor: file ? 'success.50' : 'grey.50',
          cursor: 'pointer',
          '&:hover': {
            borderColor: 'primary.main',
            bgcolor: 'grey.100'
          }
        }}
      >
        {file ? (
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
              {icon}
              <Typography variant="body2" sx={{ ml: 1 }}>
                {file.name}
              </Typography>
            </Box>
            <Chip
              label={`${(file.size / 1024 / 1024).toFixed(2)} MB`}
              size="small"
              color="success"
              sx={{ mb: 1 }}
            />
            <Box>
              <IconButton
                size="small"
                color="error"
                onClick={(e) => {
                  e.stopPropagation();
                  onFileRemove();
                }}
              >
                <DeleteIcon />
              </IconButton>
            </Box>
          </Box>
        ) : (
          <Box>
            {icon}
            <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
              Click to upload {label.toLowerCase()}
            </Typography>
            <Typography variant="caption" color="textSecondary">
              {accept === 'image/*' ? 'PNG, JPG up to 2MB' : 'PNG, JPG, PDF up to 5MB'}
            </Typography>
          </Box>
        )}
        <input
          type="file"
          accept={accept}
          onChange={handleFileChange}
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            opacity: 0,
            cursor: 'pointer'
          }}
        />
      </Box>
    </Box>
  );
};

const UserEdit = () => {
  const { empId } = useParams();
  const navigate = useNavigate();
  
  const [user, setUser] = useState(null);
  const [formData, setFormData] = useState({});
  const [files, setFiles] = useState({
    panFile: null,
    aadharFile: null,
    photo: null
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [errors, setErrors] = useState({});
  const [fileErrors, setFileErrors] = useState({});
  const [toast, setToast] = useState({
    open: false,
    message: '',
    severity: 'success'
  });

  const fetchUser = useCallback(async () => {
    if (!empId) return;

    setLoading(true);
    try {
      const response = await api.get(`/users/emp/${empId}`);
      const userData = response.data;
      setUser(userData);
      setFormData({
        emp_id: userData.emp_id || '',
        name: userData.name || '',
        email: userData.email || '',
        gender: userData.gender || '',
        dob: userData.dob ? userData.dob.split('T')[0] : '',
        doj: userData.doj ? userData.doj.split('T')[0] : '',
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
        password: ''  // Empty password for updates
      });
    } catch (error) {
      console.error('Error fetching user:', error);
      setError(error.response?.data?.detail || 'Failed to fetch user details');
    } finally {
      setLoading(false);
    }
  }, [empId]);

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  const validateFile = (file, type) => {
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

  const handleFileSelect = (fileType, file) => {
    const error = validateFile(file, fileType === 'photo' ? 'photo' : 'document');
    
    if (error) {
      setFileErrors(prev => ({ ...prev, [fileType]: error }));
      return;
    }

    setFiles(prev => ({ ...prev, [fileType]: file }));
    setFileErrors(prev => ({ ...prev, [fileType]: null }));
  };

  const handleFileRemove = (fileType) => {
    setFiles(prev => ({ ...prev, [fileType]: null }));
    setFileErrors(prev => ({ ...prev, [fileType]: null }));
  };

  const validateForm = () => {
    const newErrors = {};
    
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
    const hasFileErrors = Object.values(fileErrors).some(error => error !== null);
    if (hasFileErrors) {
      showToast('Please fix file upload errors before submitting', 'error');
      return false;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      showToast('Please fix the errors before submitting', 'error');
      return;
    }
    
    setSaving(true);
    try {
      const hasFiles = files.panFile || files.aadharFile || files.photo;
      
      if (hasFiles) {
        // Use the with-files endpoint with PUT method
        await api.uploadMultiple(`/users/emp/${empId}/with-files`, {
          pan_file: files.panFile,
          aadhar_file: files.aadharFile,
          photo: files.photo
        }, {
          user_data: JSON.stringify(formData)
        }, 'put');
      } else {
        // Use the regular endpoint
        await api.put(`/users/emp/${empId}`, formData);
      }
      
      showToast('User updated successfully!', 'success');
      setTimeout(() => {
        navigate(`/users/emp/${empId}`);
      }, 1500);
    } catch (error) {
      console.error('Error updating user:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to update user';
      showToast(errorMessage, 'error');
    } finally {
      setSaving(false);
    }
  };

  const showToast = (message, severity = 'success') => {
    setToast({ open: true, message, severity });
  };

  const handleCloseToast = () => {
    setToast(prev => ({ ...prev, open: false }));
  };

  const getInitials = (name) => {
    if (!name) return 'U';
    return name.split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  if (loading) {
    return (
      <PageLayout>
        <Box sx={{ p: 3 }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <Skeleton variant="circular" width={60} height={60} sx={{ mr: 2 }} />
                <Box>
                  <Skeleton variant="text" width={200} height={32} />
                  <Skeleton variant="text" width={100} height={24} />
                </Box>
              </Box>
              <Grid container spacing={3}>
                {Array.from({ length: 12 }).map((_, index) => (
                  <Grid item xs={12} md={6} key={index}>
                    <Skeleton variant="text" width="100%" height={56} />
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Box>
      </PageLayout>
    );
  }

  if (error) {
    return (
      <PageLayout>
        <Box sx={{ p: 3 }}>
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
      </PageLayout>
    );
  }

  if (!user) {
    return (
      <PageLayout>
        <Box sx={{ p: 3 }}>
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
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <Box sx={{ p: 3 }}>
        {/* Header */}
        <Card elevation={1} sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
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
                    Employee ID: {user.emp_id}
                  </Typography>
                </Box>
              </Box>
            </Box>
          </CardContent>
        </Card>

        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            {/* Basic Information */}
            <Grid item xs={12}>
              <Card elevation={1}>
                <CardContent>
                  <Typography variant="h6" color="primary" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <PersonIcon />
                    Basic Information
                  </Typography>
                  <Divider sx={{ mb: 3 }} />
                  
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Employee ID"
                        value={formData.emp_id}
                        onChange={(e) => handleChange('emp_id', e.target.value)}
                        disabled
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <BadgeIcon color="action" />
                            </InputAdornment>
                          ),
                        }}
                      />
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
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
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
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
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
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
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                      <FormControl fullWidth>
                        <InputLabel>Gender</InputLabel>
                        <Select
                          value={formData.gender}
                          label="Gender"
                          onChange={(e) => handleChange('gender', e.target.value)}
                        >
                          <MenuItem value="Male">Male</MenuItem>
                          <MenuItem value="Female">Female</MenuItem>
                          <MenuItem value="Other">Other</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Date of Birth"
                        type="date"
                        value={formData.dob}
                        onChange={(e) => handleChange('dob', e.target.value)}
                        InputLabelProps={{ shrink: true }}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <CalendarIcon color="action" />
                            </InputAdornment>
                          ),
                        }}
                      />
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            {/* Work Information */}
            <Grid item xs={12}>
              <Card elevation={1}>
                <CardContent>
                  <Typography variant="h6" color="primary" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <BusinessIcon />
                    Work Information
                  </Typography>
                  <Divider sx={{ mb: 3 }} />
                  
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Date of Joining"
                        type="date"
                        value={formData.doj}
                        onChange={(e) => handleChange('doj', e.target.value)}
                        InputLabelProps={{ shrink: true }}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <CalendarIcon color="action" />
                            </InputAdornment>
                          ),
                        }}
                      />
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                      <FormControl fullWidth>
                        <InputLabel>Role</InputLabel>
                        <Select
                          value={formData.role}
                          label="Role"
                          onChange={(e) => handleChange('role', e.target.value)}
                        >
                          <MenuItem value="employee">Employee</MenuItem>
                          <MenuItem value="manager">Manager</MenuItem>
                          <MenuItem value="hr">HR</MenuItem>
                          <MenuItem value="admin">Admin</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
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
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
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
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
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
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
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
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            {/* Additional Information */}
            <Grid item xs={12}>
              <Card elevation={1}>
                <CardContent>
                  <Typography variant="h6" color="primary" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <NumbersIcon />
                    Additional Information
                  </Typography>
                  <Divider sx={{ mb: 3 }} />
                  
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
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
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
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
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
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
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
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
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            {/* Document Uploads */}
            <Grid item xs={12}>
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
                  
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={4}>
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
                                if (e.target.files[0]) {
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
                    </Grid>

                    <Grid item xs={12} md={4}>
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
                                if (e.target.files[0]) {
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
                    </Grid>

                    <Grid item xs={12} md={4}>
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
                                if (e.target.files[0]) {
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
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            {/* Action Buttons */}
            <Grid item xs={12}>
              <Card elevation={1}>
                <CardContent>
                  <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                    <Button 
                      onClick={() => navigate(`/users/${empId}`)}
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
            </Grid>
          </Grid>
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
    </PageLayout>
  );
};

export default UserEdit; 