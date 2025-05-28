import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
  Typography,
  InputAdornment
} from '@mui/material';
import {
  Event as EventIcon,
  Description as DescriptionIcon
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

// Define interfaces
interface HolidayFormData {
  name: string;
  date: Date | null;
  description: string;
}

interface FormErrors {
  name?: string;
  date?: string;
  description?: string;
}

interface Holiday {
  holiday_id: string | number;
  name: string;
  date: string;
  description?: string;
}

interface HolidayUpdateData {
  name: string;
  date: string;
  description: string;
}

interface EditHolidayDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (holidayId: string | number, data: HolidayUpdateData) => Promise<void>;
  holiday: Holiday | null;
}

const EditHolidayDialog: React.FC<EditHolidayDialogProps> = ({ 
  open, 
  onClose, 
  onSubmit, 
  holiday 
}) => {
  const [formData, setFormData] = useState<HolidayFormData>({
    name: '',
    date: new Date(),
    description: ''
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  useEffect(() => {
    if (holiday) {
      setFormData({
        name: holiday.name || '',
        date: holiday.date ? new Date(holiday.date) : new Date(),
        description: holiday.description || ''
      });
      setErrors({});
    }
  }, [holiday]);

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};
    
    if (!formData.name.trim()) {
      newErrors.name = 'Holiday name is required';
    }
    
    if (!formData.date) {
      newErrors.date = 'Date is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (field: keyof HolidayFormData, value: string | Date | null): void => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const handleSubmit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();
    if (!validateForm() || !holiday) return;
    
    setIsSubmitting(true);
    try {
      const formattedData: HolidayUpdateData = {
        name: formData.name.trim(),
        date: formData.date instanceof Date ? formData.date.toISOString() : formData.date || '',
        description: formData.description.trim() || ''
      };
      
      await onSubmit(holiday.holiday_id, formattedData);
      handleClose();
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error updating holiday:', error);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = (): void => {
    setErrors({});
    setIsSubmitting(false);
    onClose();
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
          Edit Holiday
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Update the holiday information
        </Typography>
      </DialogTitle>
      
      <DialogContent sx={{ pt: 2 }}>
        <Box component="form" onSubmit={handleSubmit}>
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
            
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="Holiday Date"
                value={formData.date}
                onChange={(date) => handleChange('date', date)}
                slotProps={{
                  textField: {
                    fullWidth: true,
                    required: true,
                    error: !!errors.date,
                    helperText: errors.date,
                  }
                }}
              />
            </LocalizationProvider>
            
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
          disabled={!formData.name.trim() || !formData.date || isSubmitting}
          sx={{ minWidth: 120 }}
        >
          {isSubmitting ? 'Saving...' : 'Save Changes'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default EditHolidayDialog; 