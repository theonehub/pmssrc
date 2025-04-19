import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Alert,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

const ImportHolidaysDialog = ({ open, onClose, onSubmit }) => {
  const [file, setFile] = useState(null);
  const [error, setError] = useState('');

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    
    if (selectedFile) {
      if (!selectedFile.name.endsWith('.xlsx')) {
        setError('Please select an Excel (.xlsx) file');
        setFile(null);
      } else {
        setError('');
        setFile(selectedFile);
      }
    }
  };

  const handleSubmit = () => {
    if (file) {
      onSubmit(file);
      setFile(null);
    }
  };

  const handleClose = () => {
    setFile(null);
    setError('');
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>Import Public Holidays</DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 2,
            mt: 2,
            p: 3,
            border: '2px dashed #ccc',
            borderRadius: 1,
          }}
        >
          <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main' }} />
          <Typography variant="h6">Upload Excel File</Typography>
          <Typography variant="body2" color="text.secondary">
            The Excel file should have columns: name, date (YYYY-MM-DD), description
          </Typography>
          <Button
            variant="contained"
            component="label"
            sx={{ mt: 2 }}
          >
            Select File
            <input
              type="file"
              hidden
              accept=".xlsx"
              onChange={handleFileChange}
            />
          </Button>
          {file && (
            <Typography variant="body2">
              Selected file: {file.name}
            </Typography>
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={!file || error}
        >
          Import
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ImportHolidaysDialog; 