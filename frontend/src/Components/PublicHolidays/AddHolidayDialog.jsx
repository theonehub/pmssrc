import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

const AddHolidayDialog = ({ open, onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    holiday_id: '',
    name: '',
    date: new Date(),
    description: '',
  });

  const handleSubmit = () => {
    console.log("Submitting form data:", formData);
    
    // Create a formatted data object for the backend
    const formattedData = {
      name: formData.name,
      date: formData.date instanceof Date ? formData.date.toISOString() : formData.date,
      description: formData.description || '',
      is_active: true
    };
    
    console.log("Sending formatted data:", formattedData);
    onSubmit(formattedData);
    setFormData({
      name: '',
      date: new Date(),
      description: '',
    });
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Add Public Holiday</DialogTitle>
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
          <TextField
            label="Holiday Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            fullWidth
            required
          />
          <LocalizationProvider dateAdapter={AdapterDateFns}>
            <DatePicker
              label="Date"
              value={formData.date}
              onChange={(date) => setFormData({ ...formData, date })}
              slotProps={{ textField: { fullWidth: true, required: true } }}
            />
          </LocalizationProvider>
          <TextField
            label="Description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            fullWidth
            multiline
            rows={3}
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit} variant="contained" disabled={!formData.name}>
          Add
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AddHolidayDialog; 