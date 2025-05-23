import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Grid,
  FormControlLabel,
  Checkbox,
  Typography,
  Divider,
  Paper,
  InputAdornment
} from '@mui/material';
import {
  Business as BusinessIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  Web as WebIcon,
  LocationOn as LocationIcon,
  Numbers as NumbersIcon
} from '@mui/icons-material';
import { EmptyOrganisation } from '../../models/organisation';

function OrganisationForm({ organisation = EmptyOrganisation, onSubmit }) {
  const [formData, setFormData] = useState(organisation);
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    setFormData(organisation);
    setErrors({});
  }, [organisation]);

  const validateField = (name, value) => {
    const strValue = typeof value === 'string' ? value.trim() : String(value ?? '').trim();

    switch (name) {
      case 'name':
        return !strValue ? 'Organisation name is required' : '';
      case 'address':
        return !strValue ? 'Address is required' : '';
      case 'city':
        return !strValue ? 'City is required' : '';
      case 'country':
        return !strValue ? 'Country is required' : '';
      case 'hostname':
        return !strValue ? 'Hostname is required' : '';
      case 'employee_strength':
        if (!strValue) return 'Employee strength is required';
        if (!/^\d+$/.test(value) || parseInt(value) <= 0) {
          return 'Employee strength must be a positive number';
        }
        return '';
      case 'pan_number':
        if (!strValue) return 'PAN number is required';
        if (!/^[A-Z]{5}[0-9]{4}[A-Z]{1}$/.test(value)) {
          return 'Invalid PAN format (e.g., ABCDE1234F)';
        }
        return '';
      case 'gst_number':
        if (!strValue) return 'GST number is required';
        if (!/^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/.test(value)) {
          return 'Invalid GST format';
        }
        return '';
      case 'tan_number':
        if (!strValue) return 'TAN number is required';
        if (!/^[A-Z]{4}[0-9]{5}[A-Z]{1}$/.test(value)) {
          return 'Invalid TAN format (e.g., ABCD12345E)';
        }
        return '';
      case 'email':
        if (value && !/^\S+@\S+\.\S+$/.test(value)) {
          return 'Invalid email format';
        }
        return '';
      case 'phone':
        if (value && !/^[0-9+\-\s()]*$/.test(value)) {
          return 'Invalid phone number format';
        }
        return '';
      case 'website':
        if (value && !/^https?:\/\/.+/.test(value)) {
          return 'Website must start with http:// or https://';
        }
        return '';
      case 'pin_code':
        if (value && !/^\d{6}$/.test(value)) {
          return 'Pin code must be 6 digits';
        }
        return '';
      default:
        return '';
    }
  };

  const validate = () => {
    const newErrors = {};
    const requiredFields = [
      'name', 'address', 'city', 'country', 'hostname', 
      'employee_strength', 'pan_number', 'gst_number', 'tan_number'
    ];
    
    // Validate all fields
    Object.keys(formData).forEach(field => {
      const error = validateField(field, formData[field]);
      if (error) {
        newErrors[field] = error;
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    
    // Real-time validation
    const error = validateField(name, value);
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

  const handleCheckboxChange = (e) => {
    const { name, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: checked
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validate()) {
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(formData);
    } catch (error) {
      console.error('Form submission error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const FormSection = ({ title, children }) => (
    <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" color="primary" gutterBottom>
        {title}
      </Typography>
      <Divider sx={{ mb: 3 }} />
      <Grid container spacing={3}>
        {children}
      </Grid>
    </Paper>
  );

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ maxWidth: 900, mx: 'auto' }}>
      {/* Basic Information Section */}
      <FormSection title="Basic Information">
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Organisation Name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            error={!!errors.name}
            helperText={errors.name}
            required
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
            label="Hostname"
            name="hostname"
            value={formData.hostname}
            onChange={handleChange}
            error={!!errors.hostname}
            helperText={errors.hostname}
            required
            placeholder="e.g., company.com"
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Email"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            error={!!errors.email}
            helperText={errors.email}
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
            label="Contact Number"
            name="phone"
            value={formData.phone}
            onChange={handleChange}
            error={!!errors.phone}
            helperText={errors.phone}
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
          <TextField
            fullWidth
            label="Website"
            name="website"
            value={formData.website}
            onChange={handleChange}
            error={!!errors.website}
            helperText={errors.website}
            placeholder="https://www.example.com"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <WebIcon color="action" />
                </InputAdornment>
              ),
            }}
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Employee Strength"
            name="employee_strength"
            value={formData.employee_strength}
            onChange={handleChange}
            error={!!errors.employee_strength}
            helperText={errors.employee_strength}
            required
            type="number"
            inputProps={{ min: 1 }}
          />
        </Grid>

        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            multiline
            rows={3}
            placeholder="Brief description of the organisation..."
          />
        </Grid>
      </FormSection>

      {/* Address Information Section */}
      <FormSection title="Address Information">
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Address"
            name="address"
            value={formData.address}
            onChange={handleChange}
            error={!!errors.address}
            helperText={errors.address}
            required
            multiline
            rows={2}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <LocationIcon color="action" />
                </InputAdornment>
              ),
            }}
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="City"
            name="city"
            value={formData.city}
            onChange={handleChange}
            error={!!errors.city}
            helperText={errors.city}
            required
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="State/Province"
            name="state"
            value={formData.state}
            onChange={handleChange}
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Pin Code"
            name="pin_code"
            value={formData.pin_code}
            onChange={handleChange}
            error={!!errors.pin_code}
            helperText={errors.pin_code}
            placeholder="123456"
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Country"
            name="country"
            value={formData.country}
            onChange={handleChange}
            error={!!errors.country}
            helperText={errors.country}
            required
          />
        </Grid>
      </FormSection>

      {/* Tax Information Section */}
      <FormSection title="Tax & Legal Information">
        <Grid item xs={12} md={4}>
          <TextField
            fullWidth
            label="PAN Number"
            name="pan_number"
            value={formData.pan_number}
            onChange={handleChange}
            error={!!errors.pan_number}
            helperText={errors.pan_number}
            required
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
        </Grid>

        <Grid item xs={12} md={4}>
          <TextField
            fullWidth
            label="GST Number"
            name="gst_number"
            value={formData.gst_number}
            onChange={handleChange}
            error={!!errors.gst_number}
            helperText={errors.gst_number}
            required
            placeholder="22AAAAA0000A1Z5"
            inputProps={{ style: { textTransform: 'uppercase' } }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <NumbersIcon color="action" />
                </InputAdornment>
              ),
            }}
          />
        </Grid>

        <Grid item xs={12} md={4}>
          <TextField
            fullWidth
            label="TAN Number"
            name="tan_number"
            value={formData.tan_number}
            onChange={handleChange}
            error={!!errors.tan_number}
            helperText={errors.tan_number}
            required
            placeholder="ABCD12345E"
            inputProps={{ style: { textTransform: 'uppercase' } }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <NumbersIcon color="action" />
                </InputAdornment>
              ),
            }}
          />
        </Grid>
      </FormSection>

      {/* Status Section */}
      <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" color="primary" gutterBottom>
          Status
        </Typography>
        <Divider sx={{ mb: 3 }} />
        <FormControlLabel
          control={
            <Checkbox
              name="is_active"
              checked={formData.is_active}
              onChange={handleCheckboxChange}
              color="primary"
            />
          }
          label="Organisation is active"
        />
      </Paper>

      {/* Submit Button */}
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
        <Button 
          type="submit" 
          variant="contained" 
          size="large"
          disabled={isSubmitting}
          sx={{ minWidth: 120 }}
        >
          {isSubmitting ? 'Saving...' : (formData.organisation_id ? 'Update' : 'Create')} Organisation
        </Button>
      </Box>
    </Box>
  );
}

export default OrganisationForm; 