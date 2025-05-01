import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Grid,
  FormControlLabel,
  Checkbox,
  Typography
} from '@mui/material';
import { EmptyOrganisation } from '../../models/organisation';

function OrganisationForm({ organisation = EmptyOrganisation, onSubmit }) {
  const [formData, setFormData] = useState(organisation);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    setFormData(organisation);
  }, [organisation]);

  const validate = () => {
    const newErrors = {};
    if (!formData.name.trim()) newErrors.name = 'Name is required';
    if (!formData.address.trim()) newErrors.address = 'Address is required';
    if (!formData.city.trim()) newErrors.city = 'City is required';
    if (!formData.country.trim()) newErrors.country = 'Country is required';
    
    if (formData.email && !/^\S+@\S+\.\S+$/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }

    if (formData.phone && !/^[0-9+\-\s()]*$/.test(formData.phone)) {
      newErrors.phone = 'Invalid phone number format';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleCheckboxChange = (e) => {
    const { name, checked } = e.target;
    setFormData({
      ...formData,
      [name]: checked
    });
  };

  const handleSubmit = (e) => {
    console.log('Form submit triggered');
    e.preventDefault();
    if (validate()) {
      console.log('Form validated, calling onSubmit with:', formData);
      onSubmit(formData);
    } else {
      console.log('Form validation failed');
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
      <Grid container spacing={2}>
        <Grid columns={{ xs: 12 }}>
          <Typography variant="h6" gutterBottom>
            Basic Information
          </Typography>
        </Grid>
        
        <Grid columns={{ xs: 12, sm: 6 }}>
          <TextField
            fullWidth
            label="Name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            error={!!errors.name}
            helperText={errors.name}
            required
          />
        </Grid>
        
        <Grid columns={{ xs: 12, sm: 6 }}>
          <TextField
            fullWidth
            label="Email"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            error={!!errors.email}
            helperText={errors.email}
          />
        </Grid>
        
        <Grid columns={{ xs: 12, sm: 6 }}>
          <TextField
            fullWidth
            label="Contact Number"
            name="phone"
            value={formData.phone}
            onChange={handleChange}
            error={!!errors.phone}
            helperText={errors.phone}
          />
        </Grid>
        
        <Grid columns={{ xs: 12, sm: 6 }}>
          <TextField
            fullWidth
            label="Website"
            name="website"
            value={formData.website}
            onChange={handleChange}
          />
        </Grid>
        
        <Grid columns={{ xs: 12 }}>
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
          />
        </Grid>
        
        <Grid columns={{ xs: 12, sm: 6 }}>
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
        
        <Grid columns={{ xs: 12, sm: 6 }}>
          <TextField
            fullWidth
            label="State/Province"
            name="state"
            value={formData.state}
            onChange={handleChange}
          />
        </Grid>
        
        <Grid columns={{ xs: 12, sm: 6 }}>
          <TextField
            fullWidth
            label="Pin Code"
            name="pin_code"
            value={formData.pin_code}
            onChange={handleChange}
          />
        </Grid>
        
        <Grid columns={{ xs: 12, sm: 6 }}>
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

        <Grid columns={{ xs: 12, sm: 6 }}>
          <TextField
            fullWidth
            label="Hostname"
            name="hostname"
            value={formData.hostname}
            onChange={handleChange}
            error={!!errors.hostname}
            helperText={errors.hostname}
            required
          />
        </Grid>

        <Grid columns={{ xs: 12, sm: 6 }}>
          <TextField
            fullWidth
            label="Employee Strength"
            name="employee_strength"
            value={formData.employee_strength}
            onChange={handleChange}
            error={!!errors.employee_strength}
            helperText={errors.employee_strength}
            required
          />
        </Grid>

        <Grid columns={{ xs: 12, sm: 6 }}>
          <TextField
            fullWidth
            label="Pan Number"
            name="pan_number"
            value={formData.pan_number}
            onChange={handleChange}
            error={!!errors.pan_number}
            helperText={errors.pan_number}
            required
          />
        </Grid> 

        <Grid columns={{ xs: 12, sm: 6 }}>
          <TextField
            fullWidth
            label="GST Number"
            name="gst_number"
            value={formData.gst_number}
            onChange={handleChange}
            error={!!errors.gst_number}
            helperText={errors.gst_number}
            required
          />
        </Grid>

        <Grid columns={{ xs: 12, sm: 6 }}>
          <TextField
            fullWidth
            label="TAN Number"
            name="tan_number"
            value={formData.tan_number}
            onChange={handleChange}
            error={!!errors.tan_number}
            helperText={errors.tan_number}
            required
          />
        </Grid>

        <Grid columns={{ xs: 12 }}>
          <TextField
            fullWidth
            label="Description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            multiline
            rows={3}
          />
        </Grid>
        
        <Grid columns={{ xs: 12 }}>
          <FormControlLabel
            control={
              <Checkbox
                name="is_active"
                checked={formData.is_active}
                onChange={handleCheckboxChange}
              />
            }
            label="Active"
          />
        </Grid>
        
        <Grid columns={{ xs: 12 }} sx={{ mt: 2 }}>
          <Button 
            type="submit" 
            variant="contained" 
            fullWidth
          >
            {formData.organisation_id ? 'Update' : 'Create'} Organisation
          </Button>
        </Grid>
      </Grid>
    </Box>
  );
}

export default OrganisationForm; 