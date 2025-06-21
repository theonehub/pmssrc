import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Avatar,
  Chip,
  Divider,
  Button,
  IconButton,
  Tooltip,
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
  PhotoCamera as PhotoCameraIcon
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
  pan_document_path?: string;
  aadhar_document_path?: string;
  photo_path?: string;
  created_at?: string;
  updated_at?: string;
  is_active?: boolean;
  status?: string;
}

interface ToastState {
  open: boolean;
  message: string;
  severity: 'success' | 'error' | 'warning' | 'info';
}

type ChipColor = 'error' | 'warning' | 'info' | 'success' | 'default';

const UserDetail: React.FC = () => {
  const { empId } = useParams<{ empId: string }>();
  const navigate = useNavigate();
  
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
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

  const formatDate = (dateString?: string): string => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  const getInitials = (name?: string): string => {
    if (!name) return 'U';
    return name.split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getRoleBadgeColor = (role?: string): ChipColor => {
    switch (role?.toLowerCase()) {
      case 'admin': return 'error';
      case 'manager': return 'warning';
      case 'hr': return 'info';
      case 'employee': return 'success';
      default: return 'default';
    }
  };

  const handleViewFile = (filePath?: string, documentType?: string): void => {
    if (!filePath) return;
    
    try {
      // Create a full URL for the file
      const fileUrl = `http://localhost:8010/files/${filePath}`;
      
      // Open file in a new tab
      window.open(fileUrl, '_blank', 'noopener,noreferrer');
      showToast(`Opening ${documentType}...`, 'info');
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error opening file:', error);
      }
      showToast(`Failed to open ${documentType}`, 'error');
    }
  };

  const handleDownloadFile = async (filePath?: string): Promise<void> => {
    if (!filePath || !user) return;
    
    try {
      // Note: File download functionality might need to be implemented in the backend
      // For now, we'll show a message that this feature is coming soon
      showToast('File download feature will be implemented soon', 'info');
      
      // TODO: Implement file download through dataService
      // const fileBlob = await dataService.downloadFile(filePath);
      // Create and trigger download...
      
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error downloading file:', error);
      }
      showToast('Failed to download file. Please try again.', 'error');
    }
  };

  const showToast = (message: string, severity: ToastState['severity'] = 'success'): void => {
    setToast({ open: true, message, severity });
  };

  const handleCloseToast = (): void => {
    setToast(prev => ({ ...prev, open: false }));
  };

  if (loading) {
    return (
      <Box>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <Skeleton variant="circular" width={80} height={80} sx={{ mr: 2 }} />
              <Box>
                <Skeleton variant="text" width={200} height={32} />
                <Skeleton variant="text" width={100} height={24} />
              </Box>
            </Box>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {Array.from({ length: 8 }).map((_, index) => (
                <Skeleton key={index} variant="text" width="100%" height={60} />
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
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 2 }}>
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
                  Employee ID: {user.employee_id}
                </Typography>
              </Box>
            </Box>
            <Tooltip title="Edit User">
              <Button
                variant="contained"
                startIcon={<EditIcon />}
                onClick={() => navigate(`/users/emp/${user.employee_id}/edit`)}
              >
                Edit
              </Button>
            </Tooltip>
          </Box>
        </CardContent>
      </Card>

      <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 3 }}>
        {/* Personal Information */}
        <Box sx={{ flex: 1 }}>
          <Card elevation={1}>
            <CardContent>
              <Typography variant="h6" color="primary" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <PersonIcon />
                Personal Information
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <EmailIcon color="action" fontSize="small" />
                    <Typography variant="body2" color="text.secondary">
                      Email
                    </Typography>
                  </Box>
                  <Typography variant="body1" fontWeight="medium">
                    {user.email}
                  </Typography>
                </Box>
                
                <Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <PhoneIcon color="action" fontSize="small" />
                    <Typography variant="body2" color="text.secondary">
                      Mobile
                    </Typography>
                  </Box>
                  <Typography variant="body1" fontWeight="medium">
                    {user.mobile || 'N/A'}
                  </Typography>
                </Box>
                
                <Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <PersonIcon color="action" fontSize="small" />
                    <Typography variant="body2" color="text.secondary">
                      Gender
                    </Typography>
                  </Box>
                  <Typography variant="body1" fontWeight="medium">
                    {user.gender || 'N/A'}
                  </Typography>
                </Box>
                
                <Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <CalendarIcon color="action" fontSize="small" />
                    <Typography variant="body2" color="text.secondary">
                      Date of Birth
                    </Typography>
                  </Box>
                  <Typography variant="body1" fontWeight="medium">
                    {formatDate(user.date_of_birth)}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Box>

        {/* Work Information */}
        <Box sx={{ flex: 1 }}>
          <Card elevation={1}>
            <CardContent>
              <Typography variant="h6" color="primary" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <BusinessIcon />
                Work Information
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <CalendarIcon color="action" fontSize="small" />
                    <Typography variant="body2" color="text.secondary">
                      Date of Joining
                    </Typography>
                  </Box>
                  <Typography variant="body1" fontWeight="medium">
                    {formatDate(user.date_of_joining)}
                  </Typography>
                </Box>
                
                <Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <BusinessIcon color="action" fontSize="small" />
                    <Typography variant="body2" color="text.secondary">
                      Department
                    </Typography>
                  </Box>
                  <Typography variant="body1" fontWeight="medium">
                    {user.department || 'N/A'}
                  </Typography>
                </Box>
                
                <Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <BadgeIcon color="action" fontSize="small" />
                    <Typography variant="body2" color="text.secondary">
                      Manager ID
                    </Typography>
                  </Box>
                  <Typography variant="body1" fontWeight="medium">
                    {user.manager_id || 'N/A'}
                  </Typography>
                </Box>
                
                <Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <LocationIcon color="action" fontSize="small" />
                    <Typography variant="body2" color="text.secondary">
                      Location
                    </Typography>
                  </Box>
                  <Typography variant="body1" fontWeight="medium">
                    {user.location || 'N/A'}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Box>
      </Box>

      {/* Additional Information */}
      {(user.pan_number || user.aadhar_number || user.uan_number || user.esi_number) && (
        <Box sx={{ mt: 3 }}>
          <Card elevation={1}>
            <CardContent>
              <Typography variant="h6" color="primary" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <BadgeIcon />
                Additional Information
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 3 }}>
                {user.pan_number && (
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      PAN Number
                    </Typography>
                    <Typography variant="body1" fontWeight="medium">
                      {user.pan_number}
                    </Typography>
                  </Box>
                )}
                
                {user.aadhar_number && (
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Aadhar Number
                    </Typography>
                    <Typography variant="body1" fontWeight="medium">
                      {user.aadhar_number}
                    </Typography>
                  </Box>
                )}
                
                {user.uan_number && (
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      UAN Number
                    </Typography>
                    <Typography variant="body1" fontWeight="medium">
                      {user.uan_number}
                    </Typography>
                  </Box>
                )}
                
                {user.esi_number && (
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      ESI Number
                    </Typography>
                    <Typography variant="body1" fontWeight="medium">
                      {user.esi_number}
                    </Typography>
                  </Box>
                )}
              </Box>
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Uploaded Documents */}
      {(user.pan_document_path || user.aadhar_document_path || user.photo_path) && (
        <Box sx={{ mt: 3 }}>
          <Card elevation={1}>
            <CardContent>
              <Typography variant="h6" color="primary" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <DescriptionIcon />
                Uploaded Documents
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              <Box sx={{ display: 'flex', flexDirection: { xs: 'column', lg: 'row' }, gap: 3 }}>
                {user.pan_document_path && (
                  <Box sx={{ flex: 1 }}>
                    <Card variant="outlined" sx={{ p: 2, height: '100%' }}>
                      <Box sx={{ textAlign: 'center' }}>
                        <DescriptionIcon 
                          sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} 
                        />
                        <Typography variant="subtitle2" gutterBottom>
                          PAN Card Document
                        </Typography>
                        <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 2 }}>
                          {user.pan_document_path.split('/').pop()}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center' }}>
                          <Tooltip title="View Document">
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={() => handleViewFile(user.pan_document_path, 'PAN Card')}
                            >
                              <VisibilityIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Download Document">
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={() => handleDownloadFile(user.pan_document_path)}
                            >
                              <DownloadIcon />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </Box>
                    </Card>
                  </Box>
                )}

                {user.aadhar_document_path && (
                  <Box sx={{ flex: 1 }}>
                    <Card variant="outlined" sx={{ p: 2, height: '100%' }}>
                      <Box sx={{ textAlign: 'center' }}>
                        <DescriptionIcon 
                          sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} 
                        />
                        <Typography variant="subtitle2" gutterBottom>
                          Aadhar Card Document
                        </Typography>
                        <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 2 }}>
                          {user.aadhar_document_path.split('/').pop()}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center' }}>
                          <Tooltip title="View Document">
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={() => handleViewFile(user.aadhar_document_path, 'Aadhar Card')}
                            >
                              <VisibilityIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Download Document">
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={() => handleDownloadFile(user.aadhar_document_path)}
                            >
                              <DownloadIcon />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </Box>
                    </Card>
                  </Box>
                )}

                {user.photo_path && (
                  <Box sx={{ flex: 1 }}>
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
                              onClick={() => handleDownloadFile(user.photo_path)}
                            >
                              <DownloadIcon />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </Box>
                    </Card>
                  </Box>
                )}
              </Box>
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Toast Notifications */}
      <Snackbar 
        open={toast.open}
        autoHideDuration={6000}
        onClose={handleCloseToast}
        message={toast.message}
      />
    </Box>
  );
};

export default UserDetail; 