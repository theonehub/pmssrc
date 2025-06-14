import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Typography,
  InputAdornment,
  Box
} from '@mui/material';
import {
  Event as EventIcon,
  Description as DescriptionIcon
} from '@mui/icons-material';


// Define interfaces
interface HolidayFormData {
  name: string;
  holiday_date: string;
  description: string;
}

interface FormErrors {
  name?: string;
  holiday_date?: string;
  description?: string;
}

interface HolidaySubmitData {
  name: string;
  holiday_date: string;
  description: string;
  is_active: boolean;
}

interface AddHolidayDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: HolidaySubmitData) => Promise<void>;
}

const AddHolidayDialog: React.FC<AddHolidayDialogProps> = ({ open, onClose, onSubmit }) => {
  const [formData, setFormData] = useState<HolidayFormData>({
    name: '',
    holiday_date: '',
    description: '',
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};
    
    if (!formData.name.trim()) {
      newErrors.name = 'Holiday name is required';
    }
    
    if (!formData.holiday_date) {
      newErrors.holiday_date = 'Date is required';
    } else {
      const todayParts = new Date().toISOString().split('T');
      const today: string = todayParts[0] || '';
      if (formData.holiday_date < today) {
        newErrors.holiday_date = 'Date cannot be in the past';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (): Promise<void> => {
    if (!validateForm()) return;
    
    setIsSubmitting(true);
    try {
      const formattedData: HolidaySubmitData = {
        name: formData.name.trim(),
        holiday_date: formData.holiday_date,
        description: formData.description.trim() || '',
        is_active: true
      };
      
      await onSubmit(formattedData);
      handleClose();
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error submitting holiday:', error);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = (): void => {
    setFormData({
      name: '',
      holiday_date: '',
      description: '',
    });
    setErrors({});
    setIsSubmitting(false);
    onClose();
  };

  const handleChange = (field: keyof HolidayFormData, value: string): void => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  return (
    <Dialog 
      open={open} 
      onClose={handleClose} 
      maxWidth="sm" 
      fullWidth
      PaperProps={{
        sx: { minHeight: '400px' }
      }}
    >
      <DialogTitle sx={{ pb: 1 }}>
        <Typography variant="h5" component="div" color="primary">
          Add Public Holiday
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Create a new public holiday for the calendar
        </Typography>
      </DialogTitle>
      
      <DialogContent sx={{ pt: 2 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          <TextField
            fullWidth
            label="Holiday Name"
            value={formData.name}
            onChange={(e) => handleChange('name', e.target.value)}
            error={!!errors.name}
            helperText={errors.name}
            required
            placeholder="e.g., Independence Day, Christmas"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <EventIcon color="action" />
                </InputAdornment>
              ),
            }}
          />
          
          <TextField
            fullWidth
            label="Holiday Date"
            type="date"
            value={formData.holiday_date}
            onChange={(e) => handleChange('holiday_date', e.target.value)}
            error={!!errors.holiday_date}
            helperText={errors.holiday_date}
            required
            InputLabelProps={{ shrink: true }}
            inputProps={{
              min: new Date().toISOString().split('T')[0] // Today's date as minimum
            }}
          />
          
          <TextField
            fullWidth
            label="Description"
            value={formData.description}
            onChange={(e) => handleChange('description', e.target.value)}
            multiline
            rows={3}
            placeholder="Add details about this holiday (optional)"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start" sx={{ alignSelf: 'flex-start', mt: 1 }}>
                  <DescriptionIcon color="action" />
                </InputAdornment>
              ),
            }}
          />
        </Box>
      </DialogContent>
      
      <DialogActions sx={{ px: 3, pb: 3, gap: 2 }}>
        <Button 
          onClick={handleClose}
          size="large"
          disabled={isSubmitting}
        >
          Cancel
        </Button>
        <Button 
          onClick={handleSubmit} 
          variant="contained" 
          size="large"
          disabled={!formData.name.trim() || !formData.holiday_date || isSubmitting}
          sx={{ minWidth: 120 }}
        >
          {isSubmitting ? 'Adding...' : 'Add Holiday'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AddHolidayDialog; 