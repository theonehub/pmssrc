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
  CircularProgress,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  Description as DescriptionIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';

// Define interfaces
interface ImportHolidaysDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (file: File) => Promise<void>;
}

const ImportHolidaysDialog: React.FC<ImportHolidaysDialogProps> = ({ 
  open, 
  onClose, 
  onSubmit 
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string>('');
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [dragActive, setDragActive] = useState<boolean>(false);

  const handleFileChange = (selectedFile: File | null): void => {
    if (selectedFile) {
      // Validate file type
      const allowedTypes = [
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel',
        '.xlsx',
        '.xls'
      ];
      
      const isValidType = allowedTypes.some(type => 
        selectedFile.type === type || selectedFile.name.toLowerCase().endsWith(type)
      );
      
      if (!isValidType) {
        setError('Please select an Excel file (.xlsx or .xls)');
        setFile(null);
        return;
      }
      
      // Validate file size (max 10MB)
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError('File size should not exceed 10MB');
        setFile(null);
        return;
      }
      
      setError('');
      setFile(selectedFile);
    }
  };

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    const selectedFile = event.target.files?.[0] || null;
    handleFileChange(selectedFile);
  };

  const handleDrag = (e: React.DragEvent<HTMLDivElement>): void => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>): void => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleSubmit = async (): Promise<void> => {
    if (!file) return;
    
    setIsUploading(true);
    try {
      await onSubmit(file);
      handleClose();
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Import failed:', error);
      }
    } finally {
      setIsUploading(false);
    }
  };

  const handleClose = (): void => {
    if (!isUploading) {
      setFile(null);
      setError('');
      setDragActive(false);
      onClose();
    }
  };

  return (
    <Dialog 
      open={open} 
      onClose={handleClose} 
      maxWidth="md" 
      fullWidth
      PaperProps={{
        sx: { minHeight: '500px' }
      }}
    >
      <DialogTitle sx={{ pb: 1 }}>
        <Typography variant="h5" component="div" color="primary">
          Import Public Holidays
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Upload an Excel file to import multiple holidays at once
        </Typography>
      </DialogTitle>
      
      <DialogContent sx={{ pt: 2 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {/* File Upload Area */}
          <Box>
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}
            
            <Box
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 2,
                p: 4,
                border: '2px dashed',
                borderColor: dragActive ? 'primary.main' : file ? 'success.main' : 'divider',
                borderRadius: 2,
                backgroundColor: dragActive ? 'action.hover' : file ? 'success.light' : 'background.paper',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                '&:hover': {
                  borderColor: 'primary.main',
                  backgroundColor: 'action.hover'
                }
              }}
            >
              {file ? (
                <>
                  <CheckCircleIcon sx={{ fontSize: 48, color: 'success.main' }} />
                  <Typography variant="h6" color="success.main">
                    File Selected
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <DescriptionIcon color="action" />
                    <Typography variant="body2">
                      {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
                    </Typography>
                  </Box>
                </>
              ) : (
                <>
                  <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main' }} />
                  <Typography variant="h6">
                    {dragActive ? 'Drop file here' : 'Upload Excel File'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" textAlign="center">
                    Drag and drop your Excel file here, or click to select
                  </Typography>
                </>
              )}
              
              <input
                type="file"
                accept=".xlsx,.xls"
                onChange={handleInputChange}
                style={{ display: 'none' }}
                id="file-upload-input"
              />
              <label htmlFor="file-upload-input">
                <Button
                  variant={file ? "outlined" : "contained"}
                  component="span"
                  startIcon={file ? <DescriptionIcon /> : <CloudUploadIcon />}
                  disabled={isUploading}
                >
                  {file ? 'Change File' : 'Select File'}
                </Button>
              </label>
            </Box>
          </Box>

          <Box>
            <Divider sx={{ my: 2 }}>
              <Typography variant="body2" color="text.secondary">
                File Requirements
              </Typography>
            </Divider>
          </Box>

          {/* Requirements */}
          <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 3 }}>
            <Box sx={{ flex: 1 }}>
              <Typography variant="subtitle2" gutterBottom>
                Required Columns:
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon fontSize="small" color="success" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="name" 
                    secondary="Holiday name (e.g., Independence Day)"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon fontSize="small" color="success" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="date" 
                    secondary="Date in YYYY-MM-DD format"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon fontSize="small" color="success" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="description" 
                    secondary="Optional description"
                  />
                </ListItem>
              </List>
            </Box>

            <Box sx={{ flex: 1 }}>
              <Typography variant="subtitle2" gutterBottom>
                File Specifications:
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <DescriptionIcon fontSize="small" color="info" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Format" 
                    secondary="Excel (.xlsx or .xls)"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <DescriptionIcon fontSize="small" color="info" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Size" 
                    secondary="Maximum 10MB"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <DescriptionIcon fontSize="small" color="info" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Headers" 
                    secondary="First row should contain column names"
                  />
                </ListItem>
              </List>
            </Box>
          </Box>
        </Box>
      </DialogContent>
      
      <DialogActions sx={{ px: 3, pb: 3, gap: 2 }}>
        <Button 
          onClick={handleClose}
          size="large"
          disabled={isUploading}
        >
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          size="large"
          disabled={!file || !!error || isUploading}
          startIcon={isUploading ? <CircularProgress size={20} /> : <CloudUploadIcon />}
          sx={{ minWidth: 120 }}
        >
          {isUploading ? 'Importing...' : 'Import Holidays'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ImportHolidaysDialog; 