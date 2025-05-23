import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Paper,
  Card,
  CardContent,
  Grid,
  Avatar,
  Chip,
  Divider,
  Button,
  IconButton,
  Tooltip,
  CircularProgress,
  Alert,
  Skeleton,
  Snackbar
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Edit as EditIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  Person as PersonIcon,
  Business as BusinessIcon,
  CalendarToday as CalendarIcon,
  Badge as BadgeIcon,
  LocationOn as LocationIcon,
  Download as DownloadIcon,
  Visibility as VisibilityIcon,
  Description as DescriptionIcon,
  PhotoCamera as PhotoCameraIcon,
  CloudDownload as CloudDownloadIcon
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../utils/apiUtils';
import PageLayout from '../../layout/PageLayout';

const UserDetail = () => {
  const { empId } = useParams();
  const navigate = useNavigate();
  
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
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
      setUser(response.data);
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

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  const getInitials = (name) => {
    if (!name) return 'U';
    return name.split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getRoleBadgeColor = (role) => {
    switch (role?.toLowerCase()) {
      case 'admin': return 'error';
      case 'manager': return 'warning';
      case 'hr': return 'info';
      case 'employee': return 'success';
      default: return 'default';
    }
  };

  const handleViewFile = (filePath, documentType) => {
    if (!filePath) return;
    
    try {
      // Create a full URL for the file
      const fileUrl = `http://localhost:8000/files/${filePath}`;
      
      // Open file in a new tab
      window.open(fileUrl, '_blank', 'noopener,noreferrer');
      showToast(`Opening ${documentType}...`, 'info');
    } catch (error) {
      console.error('Error opening file:', error);
      showToast(`Failed to open ${documentType}`, 'error');
    }
  };

  const handleDownloadFile = async (filePath, fileName) => {
    if (!filePath) return;
    
    try {
      // Get the file content as blob
      const response = await api.get(`/files/${filePath}`, {}, { 
        responseType: 'blob' 
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      // Extract file extension from the original path
      const fileExtension = filePath.split('.').pop();
      link.setAttribute('download', `${fileName}_${user.emp_id}.${fileExtension}`);
      
      // Trigger download
      document.body.appendChild(link);
      link.click();
      
      // Cleanup
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading file:', error);
      showToast('Failed to download file. Please try again.', 'error');
    }
  };

  const showToast = (message, severity = 'success') => {
    setToast({ open: true, message, severity });
  };

  const handleCloseToast = () => {
    setToast(prev => ({ ...prev, open: false }));
  };

  if (loading) {
    return (
      <PageLayout>
        <Box sx={{ p: 3 }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <Skeleton variant="circular" width={80} height={80} sx={{ mr: 2 }} />
                <Box>
                  <Skeleton variant="text" width={200} height={32} />
                  <Skeleton variant="text" width={100} height={24} />
                </Box>
              </Box>
              <Grid container spacing={3}>
                {Array.from({ length: 8 }).map((_, index) => (
                  <Grid item xs={12} md={6} key={index}>
                    <Skeleton variant="text" width="100%" height={60} />
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
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <IconButton 
                  onClick={() => navigate('/users')}
                  color="primary"
                >
                  <ArrowBackIcon />
                </IconButton>
                <Avatar 
                  sx={{ 
                    width: 80, 
                    height: 80, 
                    fontSize: '1.5rem',
                    bgcolor: 'primary.main'
                  }}
                >
                  {getInitials(user.name)}
                </Avatar>
                <Box>
                  <Typography variant="h4" color="primary" gutterBottom>
                    {user.name}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Chip
                      label={user.role}
                      color={getRoleBadgeColor(user.role)}
                      variant="outlined"
                    />
                    {user.designation && (
                      <Typography variant="body2" color="text.secondary">
                        • {user.designation}
                      </Typography>
                    )}
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    Employee ID: {user.emp_id}
                  </Typography>
                </Box>
              </Box>
              <Tooltip title="Edit User">
                <Button
                  variant="contained"
                  startIcon={<EditIcon />}
                  onClick={() => navigate(`/users/emp/${user.emp_id}/edit`)}
                >
                  Edit
                </Button>
              </Tooltip>
            </Box>
          </CardContent>
        </Card>

        <Grid container spacing={3}>
          {/* Personal Information */}
          <Grid item xs={12} md={6}>
            <Card elevation={1}>
              <CardContent>
                <Typography variant="h6" color="primary" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <PersonIcon />
                  Personal Information
                </Typography>
                <Divider sx={{ mb: 2 }} />
                
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <EmailIcon color="action" fontSize="small" />
                      <Typography variant="body2" color="text.secondary">
                        Email
                      </Typography>
                    </Box>
                    <Typography variant="body1" fontWeight="medium">
                      {user.email}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={12}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <PhoneIcon color="action" fontSize="small" />
                      <Typography variant="body2" color="text.secondary">
                        Mobile
                      </Typography>
                    </Box>
                    <Typography variant="body1" fontWeight="medium">
                      {user.mobile || 'N/A'}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={12}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <PersonIcon color="action" fontSize="small" />
                      <Typography variant="body2" color="text.secondary">
                        Gender
                      </Typography>
                    </Box>
                    <Typography variant="body1" fontWeight="medium">
                      {user.gender || 'N/A'}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={12}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <CalendarIcon color="action" fontSize="small" />
                      <Typography variant="body2" color="text.secondary">
                        Date of Birth
                      </Typography>
                    </Box>
                    <Typography variant="body1" fontWeight="medium">
                      {formatDate(user.dob)}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Work Information */}
          <Grid item xs={12} md={6}>
            <Card elevation={1}>
              <CardContent>
                <Typography variant="h6" color="primary" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <BusinessIcon />
                  Work Information
                </Typography>
                <Divider sx={{ mb: 2 }} />
                
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <CalendarIcon color="action" fontSize="small" />
                      <Typography variant="body2" color="text.secondary">
                        Date of Joining
                      </Typography>
                    </Box>
                    <Typography variant="body1" fontWeight="medium">
                      {formatDate(user.doj)}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={12}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <BusinessIcon color="action" fontSize="small" />
                      <Typography variant="body2" color="text.secondary">
                        Department
                      </Typography>
                    </Box>
                    <Typography variant="body1" fontWeight="medium">
                      {user.department || 'N/A'}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={12}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <BadgeIcon color="action" fontSize="small" />
                      <Typography variant="body2" color="text.secondary">
                        Manager ID
                      </Typography>
                    </Box>
                    <Typography variant="body1" fontWeight="medium">
                      {user.manager_id || 'N/A'}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={12}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <LocationIcon color="action" fontSize="small" />
                      <Typography variant="body2" color="text.secondary">
                        Location
                      </Typography>
                    </Box>
                    <Typography variant="body1" fontWeight="medium">
                      {user.location || 'N/A'}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Additional Information */}
          {(user.pan_number || user.aadhar_number || user.uan_number || user.esi_number) && (
            <Grid item xs={12}>
              <Card elevation={1}>
                <CardContent>
                  <Typography variant="h6" color="primary" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <BadgeIcon />
                    Additional Information
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                  
                  <Grid container spacing={3}>
                    {user.pan_number && (
                      <Grid item xs={12} md={6}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          PAN Number
                        </Typography>
                        <Typography variant="body1" fontWeight="medium">
                          {user.pan_number}
                        </Typography>
                      </Grid>
                    )}
                    
                    {user.aadhar_number && (
                      <Grid item xs={12} md={6}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          Aadhar Number
                        </Typography>
                        <Typography variant="body1" fontWeight="medium">
                          {user.aadhar_number}
                        </Typography>
                      </Grid>
                    )}
                    
                    {user.uan_number && (
                      <Grid item xs={12} md={6}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          UAN Number
                        </Typography>
                        <Typography variant="body1" fontWeight="medium">
                          {user.uan_number}
                        </Typography>
                      </Grid>
                    )}
                    
                    {user.esi_number && (
                      <Grid item xs={12} md={6}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          ESI Number
                        </Typography>
                        <Typography variant="body1" fontWeight="medium">
                          {user.esi_number}
                        </Typography>
                      </Grid>
                    )}
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* Uploaded Documents */}
          {(user.pan_file_path || user.aadhar_file_path || user.photo_path) && (
            <Grid item xs={12}>
              <Card elevation={1}>
                <CardContent>
                  <Typography variant="h6" color="primary" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <DescriptionIcon />
                    Uploaded Documents
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                  
                  <Grid container spacing={3}>
                    {user.pan_file_path && (
                      <Grid item xs={12} md={4}>
                        <Card variant="outlined" sx={{ p: 2, height: '100%' }}>
                          <Box sx={{ textAlign: 'center' }}>
                            <DescriptionIcon 
                              sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} 
                            />
                            <Typography variant="subtitle2" gutterBottom>
                              PAN Card Document
                            </Typography>
                            <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 2 }}>
                              {user.pan_file_path.split('/').pop()}
                            </Typography>
                            <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center' }}>
                              <Tooltip title="View Document">
                                <IconButton
                                  size="small"
                                  color="primary"
                                  onClick={() => handleViewFile(user.pan_file_path, 'PAN Card')}
                                >
                                  <VisibilityIcon />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="Download Document">
                                <IconButton
                                  size="small"
                                  color="primary"
                                  onClick={() => handleDownloadFile(user.pan_file_path, 'PAN_Card')}
                                >
                                  <DownloadIcon />
                                </IconButton>
                              </Tooltip>
                            </Box>
                          </Box>
                        </Card>
                      </Grid>
                    )}

                    {user.aadhar_file_path && (
                      <Grid item xs={12} md={4}>
                        <Card variant="outlined" sx={{ p: 2, height: '100%' }}>
                          <Box sx={{ textAlign: 'center' }}>
                            <DescriptionIcon 
                              sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} 
                            />
                            <Typography variant="subtitle2" gutterBottom>
                              Aadhar Card Document
                            </Typography>
                            <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 2 }}>
                              {user.aadhar_file_path.split('/').pop()}
                            </Typography>
                            <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center' }}>
                              <Tooltip title="View Document">
                                <IconButton
                                  size="small"
                                  color="primary"
                                  onClick={() => handleViewFile(user.aadhar_file_path, 'Aadhar Card')}
                                >
                                  <VisibilityIcon />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="Download Document">
                                <IconButton
                                  size="small"
                                  color="primary"
                                  onClick={() => handleDownloadFile(user.aadhar_file_path, 'Aadhar_Card')}
                                >
                                  <DownloadIcon />
                                </IconButton>
                              </Tooltip>
                            </Box>
                          </Box>
                        </Card>
                      </Grid>
                    )}

                    {user.photo_path && (
                      <Grid item xs={12} md={4}>
                        <Card variant="outlined" sx={{ p: 2, height: '100%' }}>
                          <Box sx={{ textAlign: 'center' }}>
                            <PhotoCameraIcon 
                              sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} 
                            />
                            <Typography variant="subtitle2" gutterBottom>
                              Profile Photo
                            </Typography>
                            <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 2 }}>
                              {user.photo_path.split('/').pop()}
                            </Typography>
                            <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center' }}>
                              <Tooltip title="View Photo">
                                <IconButton
                                  size="small"
                                  color="primary"
                                  onClick={() => handleViewFile(user.photo_path, 'Profile Photo')}
                                >
                                  <VisibilityIcon />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="Download Photo">
                                <IconButton
                                  size="small"
                                  color="primary"
                                  onClick={() => handleDownloadFile(user.photo_path, 'Profile_Photo')}
                                >
                                  <DownloadIcon />
                                </IconButton>
                              </Tooltip>
                            </Box>
                          </Box>
                        </Card>
                      </Grid>
                    )}
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>

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

export default UserDetail; 