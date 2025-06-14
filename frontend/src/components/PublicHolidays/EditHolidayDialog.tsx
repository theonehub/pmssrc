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

interface Holiday {
  id: string;
  name: string;
  holiday_date: string;
  description?: string;
}

interface HolidayUpdateData {
  name: string;
  holiday_date: string;
  description: string;
}

interface EditHolidayDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (holidayId: string, data: HolidayUpdateData) => Promise<void>;
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
    holiday_date: '',
    description: ''
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  useEffect(() => {
    if (holiday) {
      setFormData({
        name: holiday.name || '',
        holiday_date: holiday.holiday_date || '',
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
    
    if (!formData.holiday_date) {
      newErrors.holiday_date = 'Date is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (field: keyof HolidayFormData, value: string): void => {
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
        holiday_date: formData.holiday_date,
        description: formData.description.trim() || ''
      };
      
      await onSubmit(holiday.id, formattedData);
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
          {isSubmitting ? 'Saving...' : 'Save Changes'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default EditHolidayDialog; 