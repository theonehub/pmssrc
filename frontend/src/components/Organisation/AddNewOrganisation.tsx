import React, { useState, useEffect, ReactNode } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Divider,
  Paper,
  Card,
  CardContent,
  Snackbar,
  Alert,
  AlertColor,
  MenuItem,
  FormControlLabel,
  Checkbox
} from '@mui/material';
import {
  Business as BusinessIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  Language as LanguageIcon,
  LocationOn as LocationIcon,
  Description as DescriptionIcon,
  Numbers as NumbersIcon,
  ArrowBack as ArrowBackIcon
} from '@mui/icons-material';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import { getToken } from '../../shared/utils/auth';
import PageLayout from '../../layout/PageLayout';
import { useOrganisationsQuery } from '../../shared/hooks/useOrganisations';

const API_BASE_URL = 'http://localhost:8000/api/v2';

interface ToastState {
  open: boolean;
  message: string;
  severity: AlertColor;
}

interface FormSectionProps {
  title: string;
  children: ReactNode;
}

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

const AddNewOrganisation: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const isEditing = !!id;

  // Individual state variables for better form control
  const [name, setName] = useState('');
  const [hostname, setHostname] = useState('');
  const [description, setDescription] = useState('');
  const [organisationType, setOrganisationType] = useState('private_limited');
  const [status, setStatus] = useState('active');
  const [employeeStrength, setEmployeeStrength] = useState('10');
  const [isActive, setIsActive] = useState(true);

  // Contact info
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [website, setWebsite] = useState('');

  // Address info
  const [address, setAddress] = useState('');
  const [city, setCity] = useState('');
  const [state, setState] = useState('');
  const [country, setCountry] = useState('');
  const [pinCode, setPinCode] = useState('');

  // Tax info
  const [panNumber, setPanNumber] = useState('');
  const [gstNumber, setGstNumber] = useState('');
  const [tanNumber, setTanNumber] = useState('');

  // Error states
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [toast, setToast] = useState<ToastState>({
    open: false,
    message: '',
    severity: 'success'
  });

  const { data: organisationData } = useOrganisationsQuery(
    isEditing ? { id } : undefined
  );

  // Load organisation data for editing
  useEffect(() => {
    if (isEditing && organisationData?.data?.organisations?.[0]) {
      const org = organisationData.data.organisations[0];
      
      // Populate form fields - handle both nested and flat structures
      setName(org.name || '');
      setHostname(org.hostname || '');
      setDescription(org.description || '');
      setOrganisationType(org.organisation_type || 'private_limited');
      setStatus(org.status || 'active');
      setEmployeeStrength(org.employee_strength?.toString() || '10');
      setIsActive(org.is_active !== undefined ? org.is_active : true);
      
      // Contact info - check both nested and flat structure
      setEmail(org.contact_info?.email || org.email || '');
      setPhone(org.contact_info?.phone || org.phone || '');
      setWebsite(org.contact_info?.website || org.website || '');
      
      // Address info - check both nested and flat structure
      setAddress(org.address?.street_address || org.street_address || '');
      setCity(org.address?.city || org.city || '');
      setState(org.address?.state || org.state || '');
      setCountry(org.address?.country || org.country || '');
      setPinCode(org.address?.pin_code || org.pin_code || '');
      
      // Tax info - check both nested and flat structure
      setPanNumber(org.tax_info?.pan_number || org.pan_number || '');
      setGstNumber(org.tax_info?.gst_number || org.gst_number || '');
      setTanNumber(org.tax_info?.tan_number || org.tan_number || '');
    }
  }, [isEditing, organisationData]);

  const validateField = (fieldName: string, value: string): string => {
    switch (fieldName) {
      case 'name':
        return !value.trim() ? 'Organisation name is required' : '';
      case 'hostname':
        return !value.trim() ? 'Hostname is required' : '';
      case 'employeeStrength':
        const num = parseInt(value);
        if (!value.trim()) return 'Employee strength is required';
        if (isNaN(num) || num <= 0) return 'Employee strength must be a positive number';
        return '';
      case 'email':
        if (!value.trim()) return '';
        return !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) ? 'Invalid email format' : '';
      case 'phone':
        if (!value.trim()) return '';
        return !/^[0-9+\-\s()]*$/.test(value) ? 'Invalid phone number format' : '';
      case 'website':
        if (!value.trim()) return '';
        return !/^https?:\/\/.+/.test(value) ? 'Website must start with http:// or https://' : '';
      case 'address':
        return !value.trim() ? 'Address is required' : '';
      case 'city':
        return !value.trim() ? 'City is required' : '';
      case 'country':
        return !value.trim() ? 'Country is required' : '';
      case 'pinCode':
        if (!value.trim()) return '';
        return !/^\d{6}$/.test(value) ? 'Pin code must be 6 digits' : '';
      case 'panNumber':
        if (!value.trim()) return 'PAN number is required';
        return !/^[A-Z]{5}[0-9]{4}[A-Z]{1}$/.test(value) ? 'Invalid PAN format (e.g., ABCDE1234F)' : '';
      case 'gstNumber':
        if (!value.trim()) return '';
        return !/^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/.test(value) ? 'Invalid GST format (e.g., 22AAAAA0000A1Z5)' : '';
      case 'tanNumber':
        if (!value.trim()) return '';
        return !/^[A-Z]{4}[0-9]{5}[A-Z]{1}$/.test(value) ? 'Invalid TAN format (e.g., ABCD12345E)' : '';
      default:
        return '';
    }
  };

  const handleFieldChange = (fieldName: string, value: string, setField: (value: string) => void) => {
    // Convert to uppercase for tax numbers
    if (['panNumber', 'gstNumber', 'tanNumber'].includes(fieldName)) {
      value = value.toUpperCase();
    }
    
    setField(value);
    
    // Real-time validation
    const error = validateField(fieldName, value);
    setErrors(prev => ({
      ...prev,
      [fieldName]: error
    }));
  };

  const validate = (): boolean => {
    const newErrors: { [key: string]: string } = {};
    
    // Validate all fields
    const fieldsToValidate = [
      { name: 'name', value: name },
      { name: 'hostname', value: hostname },
      { name: 'employeeStrength', value: employeeStrength },
      { name: 'email', value: email },
      { name: 'phone', value: phone },
      { name: 'website', value: website },
      { name: 'address', value: address },
      { name: 'city', value: city },
      { name: 'country', value: country },
      { name: 'pinCode', value: pinCode },
      { name: 'panNumber', value: panNumber },
      { name: 'gstNumber', value: gstNumber },
      { name: 'tanNumber', value: tanNumber }
    ];

    fieldsToValidate.forEach(field => {
      const error = validateField(field.name, field.value);
      if (error) {
        newErrors[field.name] = error;
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    
    if (!validate()) {
      showToast('Please fix the errors before submitting', 'error');
      return;
    }

    setIsSubmitting(true);
    try {
      const token = getToken();
      if (!token) {
        throw new Error('Authentication required. Please login again.');
      }

      // Construct the organisation object in the flattened format expected by backend
      const organisationData = {
        // Basic Information (required)
        name,
        organisation_type: organisationType,
        
        // Contact Information (flattened - required)
        email,
        phone,
        
        // Address Information (flattened - required)
        street_address: address,
        city,
        state,
        country,
        pin_code: pinCode,
        
        // Tax Information (flattened - required)
        pan_number: panNumber,
        
        // Optional fields
        description: description || '',
        status: status || 'active',
        employee_strength: parseInt(employeeStrength) || 10,
        hostname: hostname || '',
        website: website || '',
        gst_number: gstNumber || '',
        tan_number: tanNumber || '',
        
        // Additional optional fields that backend might expect
        fax: '',
        landmark: '',
        cin_number: ''
      };

      // Only include organisation_id for updates
      if (isEditing && id) {
        (organisationData as any).organisation_id = id;
      }

      const url = isEditing 
        ? `${API_BASE_URL}/organisations/${id}/`
        : `${API_BASE_URL}/organisations/`;
      const method = isEditing ? 'put' : 'post';
      
      console.log(`Making ${method.toUpperCase()} request to:`, url);
      console.log('Request data:', organisationData);

      const response = await axios[method](url, organisationData, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
      });
      
      console.log('Success response:', response.data);
      
      const successMessage = isEditing 
        ? 'Organisation updated successfully!'
        : 'Organisation created successfully!';
      
      showToast(successMessage, 'success');
      
      setTimeout(() => {
        navigate('/organisations');
      }, 1500);
      
    } catch (error: any) {
      console.error('Error saving organisation:', error);
      console.error('Error response:', error.response?.data);
      console.error('Error status:', error.response?.status);
      
      let errorMessage = isEditing ? 'Failed to update organisation' : 'Failed to create organisation';
      
      // Handle different error cases
      if (error.response?.status === 500) {
        // Backend internal server error - likely the CurrentUser vs dict issue
        errorMessage = `Backend error detected. There appears to be a type mismatch in the organisation API route. ` +
          `The route function expects CurrentUser but the implementation expects dict. ` +
          `This is a backend configuration issue that needs to be fixed by the development team.`;
      } else if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (typeof detail === 'string') {
          errorMessage = detail;
        } else if (Array.isArray(detail)) {
          errorMessage = detail.map((err: any) => err.msg || err.message || 'Validation error').join(', ');
        } else if (typeof detail === 'object' && detail.message) {
          errorMessage = detail.message;
        }
      } else if (error.response?.status === 422) {
        errorMessage = 'Validation error: Please check all required fields are filled correctly.';
      } else if (error.response?.status === 401) {
        errorMessage = 'Authentication failed. Please login again.';
      } else if (error.response?.status === 403) {
        errorMessage = 'Access denied. You may not have permission to create organisations.';
      }
      
      showToast(errorMessage, 'error');
      
      // If it's a 500 error, also show a developer-friendly message in console
      if (error.response?.status === 500) {
        console.error('='.repeat(80));
        console.error('BACKEND ISSUE DETECTED:');
        console.error('File: backend/app/api/routes/organisation_routes_v2.py');
        console.error('Issue: Type mismatch in _create_organisation_impl function');
        console.error('Line 44: current_user.employee_id - expects CurrentUser object');
        console.error('Line 37: current_user: dict - function signature expects dict');
        console.error('Fix: Change line 37 to: current_user: CurrentUser');
        console.error('Or change route to pass current_user.__dict__ instead');
        console.error('='.repeat(80));
      }
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
    <PageLayout title={isEditing ? "Edit Organisation" : "Add New Organisation"}>
      <Box sx={{ p: 3 }}>
        {/* Header */}
        <Card elevation={1} sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ 
              display: 'grid', 
              gridTemplateColumns: { xs: '1fr', sm: '1fr' }, 
              gap: 2, 
              alignItems: 'center' 
            }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Button
                  startIcon={<ArrowBackIcon />}
                  onClick={() => navigate('/organisations')}
                  variant="outlined"
                  size="small"
                >
                  Back
                </Button>
                <Box>
                  <Typography variant="h4" color="primary" gutterBottom>
                    {isEditing ? 'Edit Organisation' : 'Add New Organisation'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {isEditing 
                      ? 'Update the organisation details below'
                      : 'Fill in the organisation details to create a new organisation'
                    }
                  </Typography>
                </Box>
              </Box>
            </Box>
          </CardContent>
        </Card>

        <Box component="form" onSubmit={handleSubmit} sx={{ maxWidth: 900, mx: 'auto' }}>
          {/* Basic Information Section */}
          <FormSection title="Basic Information">
            <TextField
              fullWidth
              label="Organisation Name"
              value={name}
              onChange={(e) => handleFieldChange('name', e.target.value, setName)}
              error={!!errors.name}
              helperText={errors.name}
              required
              InputProps={{
                startAdornment: <BusinessIcon color="action" sx={{ mr: 1 }} />,
              }}
            />

            <TextField
              fullWidth
              label="Hostname"
              value={hostname}
              onChange={(e) => handleFieldChange('hostname', e.target.value, setHostname)}
              error={!!errors.hostname}
              helperText={errors.hostname}
              required
              placeholder="e.g., company.com"
              InputProps={{
                startAdornment: <LanguageIcon color="action" sx={{ mr: 1 }} />,
              }}
            />

            <TextField
              select
              fullWidth
              label="Organisation Type"
              value={organisationType}
              onChange={(e) => setOrganisationType(e.target.value)}
            >
              <MenuItem value="private_limited">Private Limited</MenuItem>
              <MenuItem value="public_limited">Public Limited</MenuItem>
              <MenuItem value="partnership">Partnership</MenuItem>
              <MenuItem value="sole_proprietorship">Sole Proprietorship</MenuItem>
              <MenuItem value="llp">Limited Liability Partnership</MenuItem>
            </TextField>

            <TextField
              select
              fullWidth
              label="Status"
              value={status}
              onChange={(e) => setStatus(e.target.value)}
            >
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="inactive">Inactive</MenuItem>
              <MenuItem value="suspended">Suspended</MenuItem>
              <MenuItem value="deleted">Deleted</MenuItem>
            </TextField>

            <TextField
              fullWidth
              label="Employee Strength"
              type="number"
              value={employeeStrength}
              onChange={(e) => handleFieldChange('employeeStrength', e.target.value, setEmployeeStrength)}
              error={!!errors.employeeStrength}
              helperText={errors.employeeStrength}
              required
              inputProps={{ min: 1 }}
              InputProps={{
                startAdornment: <NumbersIcon color="action" sx={{ mr: 1 }} />,
              }}
            />

            <Box sx={{ gridColumn: '1 / -1' }}>
              <TextField
                fullWidth
                label="Description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                multiline
                rows={3}
                placeholder="Brief description of the organisation..."
                InputProps={{
                  startAdornment: <DescriptionIcon color="action" sx={{ mr: 1, alignSelf: 'flex-start', mt: 1 }} />,
                }}
              />
            </Box>

            <Box sx={{ gridColumn: '1 / -1' }}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={isActive}
                    onChange={(e) => setIsActive(e.target.checked)}
                    color="primary"
                  />
                }
                label="Organisation is active"
              />
            </Box>
          </FormSection>

          {/* Contact Information Section */}
          <FormSection title="Contact Information">
            <TextField
              fullWidth
              label="Email"
              type="email"
              value={email}
              onChange={(e) => handleFieldChange('email', e.target.value, setEmail)}
              error={!!errors.email}
              helperText={errors.email}
              InputProps={{
                startAdornment: <EmailIcon color="action" sx={{ mr: 1 }} />,
              }}
            />

            <TextField
              fullWidth
              label="Phone"
              value={phone}
              onChange={(e) => handleFieldChange('phone', e.target.value, setPhone)}
              error={!!errors.phone}
              helperText={errors.phone}
              InputProps={{
                startAdornment: <PhoneIcon color="action" sx={{ mr: 1 }} />,
              }}
            />

            <Box sx={{ gridColumn: '1 / -1' }}>
              <TextField
                fullWidth
                label="Website"
                value={website}
                onChange={(e) => handleFieldChange('website', e.target.value, setWebsite)}
                error={!!errors.website}
                helperText={errors.website}
                placeholder="https://www.example.com"
                InputProps={{
                  startAdornment: <LanguageIcon color="action" sx={{ mr: 1 }} />,
                }}
              />
            </Box>
          </FormSection>

          {/* Address Information Section */}
          <FormSection title="Address Information">
            <Box sx={{ gridColumn: '1 / -1' }}>
              <TextField
                fullWidth
                label="Address"
                value={address}
                onChange={(e) => handleFieldChange('address', e.target.value, setAddress)}
                error={!!errors.address}
                helperText={errors.address}
                multiline
                rows={2}
                required
                InputProps={{
                  startAdornment: <LocationIcon color="action" sx={{ mr: 1, alignSelf: 'flex-start', mt: 1 }} />,
                }}
              />
            </Box>

            <TextField
              fullWidth
              label="City"
              value={city}
              onChange={(e) => handleFieldChange('city', e.target.value, setCity)}
              error={!!errors.city}
              helperText={errors.city}
              required
            />

            <TextField
              fullWidth
              label="State/Province"
              value={state}
              onChange={(e) => setState(e.target.value)}
            />

            <TextField
              fullWidth
              label="Country"
              value={country}
              onChange={(e) => handleFieldChange('country', e.target.value, setCountry)}
              error={!!errors.country}
              helperText={errors.country}
              required
            />

            <TextField
              fullWidth
              label="Pin Code"
              value={pinCode}
              onChange={(e) => handleFieldChange('pinCode', e.target.value, setPinCode)}
              error={!!errors.pinCode}
              helperText={errors.pinCode}
              placeholder="123456"
            />
          </FormSection>

          {/* Tax Information Section */}
          <FormSection title="Tax & Legal Information">
            <TextField
              fullWidth
              label="PAN Number"
              value={panNumber}
              onChange={(e) => handleFieldChange('panNumber', e.target.value, setPanNumber)}
              error={!!errors.panNumber}
              helperText={errors.panNumber}
              placeholder="ABCDE1234F"
              required
              inputProps={{ style: { textTransform: 'uppercase' } }}
              InputProps={{
                startAdornment: <NumbersIcon color="action" sx={{ mr: 1 }} />,
              }}
            />

            <TextField
              fullWidth
              label="GST Number"
              value={gstNumber}
              onChange={(e) => handleFieldChange('gstNumber', e.target.value, setGstNumber)}
              error={!!errors.gstNumber}
              helperText={errors.gstNumber}
              placeholder="22AAAAA0000A1Z5"
              inputProps={{ style: { textTransform: 'uppercase' } }}
              InputProps={{
                startAdornment: <NumbersIcon color="action" sx={{ mr: 1 }} />,
              }}
            />

            <TextField
              fullWidth
              label="TAN Number"
              value={tanNumber}
              onChange={(e) => handleFieldChange('tanNumber', e.target.value, setTanNumber)}
              error={!!errors.tanNumber}
              helperText={errors.tanNumber}
              placeholder="ABCD12345E"
              inputProps={{ style: { textTransform: 'uppercase' } }}
              InputProps={{
                startAdornment: <NumbersIcon color="action" sx={{ mr: 1 }} />,
              }}
            />
          </FormSection>

          {/* Submit Button */}
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
            <Button 
              onClick={() => navigate('/organisations')}
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
              {isSubmitting 
                ? (isEditing ? 'Updating...' : 'Creating...') 
                : (isEditing ? 'Update Organisation' : 'Create Organisation')
              }
            </Button>
          </Box>

          {/* Developer Help Section - Only show in development */}
          {/* {process.env.NODE_ENV === 'development' && (
            <Paper 
              elevation={1} 
              sx={{ 
                p: 3, 
                mt: 3, 
                backgroundColor: '#f8f9fa',
                border: '1px solid #e9ecef'
              }}
            >
              <Typography variant="h6" color="primary" gutterBottom>
                🔧 Developer Information
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                If you encounter a <strong>500 Internal Server Error</strong> when creating organisations, 
                this is due to a backend type mismatch issue:
              </Typography>
              <Box sx={{ backgroundColor: '#f1f3f4', p: 2, borderRadius: 1, fontFamily: 'monospace', fontSize: '0.875rem' }}>
                <Typography variant="body2" sx={{ fontFamily: 'inherit' }}>
                  <strong>File:</strong> backend/app/api/routes/organisation_routes_v2.py<br/>
                  <strong>Issue:</strong> Line 37 expects <code>current_user.employee_id - expects CurrentUser object</code> but receives <code>CurrentUser</code> object<br/>
                  <strong>Fix:</strong> Change line 37 to <code>current_user: CurrentUser</code>
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                This form is ready and will work once the backend type annotation is corrected.
              </Typography>
            </Paper>
          )} */}
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
    </PageLayout>
  );
};

export default AddNewOrganisation; 