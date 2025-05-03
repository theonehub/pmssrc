import React from 'react';
import PropTypes from 'prop-types';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box
} from '@mui/material';

/**
 * Reusable form dialog component with Material-UI styling
 * 
 * @param {Object} props - Component props
 * @param {boolean} props.open - Whether the dialog is open
 * @param {function} props.onClose - Function to handle dialog close
 * @param {string} props.title - Dialog title
 * @param {React.ReactNode} props.children - Dialog content (form fields)
 * @param {string} props.submitLabel - Label for the submit button
 * @param {string} props.cancelLabel - Label for the cancel button
 * @param {function} props.onSubmit - Function to handle form submission
 * @param {boolean} props.isSubmitting - Whether the form is submitting
 * @param {Object} props.dialogProps - Additional props for the Dialog component
 */
const FormDialog = ({
  open,
  onClose,
  title,
  children,
  submitLabel = 'Submit',
  cancelLabel = 'Cancel',
  onSubmit,
  isSubmitting = false,
  dialogProps = {}
}) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(e);
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      {...dialogProps}
    >
      <DialogTitle>{title}</DialogTitle>
      <form onSubmit={handleSubmit}>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {children}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={onClose} 
            disabled={isSubmitting}
          >
            {cancelLabel}
          </Button>
          <Button 
            type="submit" 
            variant="contained" 
            disabled={isSubmitting}
          >
            {submitLabel}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

FormDialog.propTypes = {
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  title: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
  submitLabel: PropTypes.string,
  cancelLabel: PropTypes.string,
  onSubmit: PropTypes.func.isRequired,
  isSubmitting: PropTypes.bool,
  dialogProps: PropTypes.object
};

export default FormDialog; 