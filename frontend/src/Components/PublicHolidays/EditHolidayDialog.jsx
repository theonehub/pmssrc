import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box
} from '@mui/material';

const EditHolidayDialog = ({ open, onClose, onSubmit, holiday }) => {
  const [formData, setFormData] = useState({
    name: '',
    date: '',
    description: ''
  });

  useEffect(() => {
    if (holiday) {
      setFormData({
        name: holiday.name,
        date: new Date(holiday.date).toISOString().split('T')[0],
        description: holiday.description || ''
      });
    }
  }, [holiday]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(holiday.holiday_id, formData);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Edit Holiday</DialogTitle>
      <DialogContent>
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
          <TextField
            fullWidth
            label="Holiday Name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
            margin="normal"
          />
          <TextField
            fullWidth
            label="Date"
            name="date"
            type="date"
            value={formData.date}
            onChange={handleChange}
            required
            margin="normal"
            InputLabelProps={{
              shrink: true,
            }}
          />
          <TextField
            fullWidth
            label="Description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            margin="normal"
            multiline
            rows={3}
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit} variant="contained" color="primary">
          Save Changes
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default EditHolidayDialog; 