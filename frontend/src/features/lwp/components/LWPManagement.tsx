import React, { useEffect, useState } from 'react';
import { 
  Button, 
  Container, 
  Table, 
  CircularProgress, 
  Alert, 
  TableContainer, 
  TableHead, 
  TableBody, 
  TableRow, 
  TableCell, 
  Box, 
  TextField, 
  Typography,
  Paper,
  AlertColor
} from '@mui/material';
import axios, { AxiosResponse } from 'axios';
import { getToken } from '../../../shared/utils/auth';

// Define interfaces
interface LWPRecord {
  id: string | number;
  employee_name: string;
  start_date: string;
  end_date: string;
  days: number;
  status: 'approved' | 'pending' | 'rejected' | string;
  present_days?: number;
}

interface StatusMessage {
  message: string;
  type: 'success' | 'danger' | 'error' | '';
}

interface ImportResponse {
  msg?: string;
}

const API_BASE_URL = 'http://localhost:8000';

const LWPManagement: React.FC = () => {
  // State management with proper typing
  const [lwpRecords, setLwpRecords] = useState<LWPRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<StatusMessage>({ message: '', type: '' });
  const [isUpdatingBulk, setIsUpdatingBulk] = useState<boolean>(false);
  const [isExporting, setIsExporting] = useState<boolean>(false);
  const [updateStatus, setUpdateStatus] = useState<StatusMessage>({ message: '', type: '' });

  useEffect(() => {
    fetchLWPRecords();
  }, []);

  const fetchLWPRecords = async (): Promise<void> => {
    setLoading(true);
    setError(null);
    try {
      const token = getToken();
      if (!token) {
        throw new Error('No authentication token found');
      }

      const response: AxiosResponse<LWPRecord[]> = await axios.get(
        `${API_BASE_URL}/lwp`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setLwpRecords(response.data);
    } catch (err: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error fetching LWP records:', err);
      }
      setError('Failed to fetch LWP records.');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateLWP = async (id: string | number, presentDays?: number): Promise<void> => {
    setUpdateStatus({ message: '', type: '' });
    try {
      const token = getToken();
      if (!token) {
        throw new Error('No authentication token found');
      }

      await axios.put(
        `${API_BASE_URL}/lwp/${id}`,
        { present_days: presentDays },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setUpdateStatus({ message: 'LWP updated successfully.', type: 'success' });
      fetchLWPRecords();
    } catch (err: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error updating LWP:', err);
      }
      setUpdateStatus({ message: 'Failed to update LWP.', type: 'danger' });
    }
  };

  const handleBulkUpdate = async (): Promise<void> => {
    setIsUpdatingBulk(true);
    setUpdateStatus({ message: '', type: '' });
    try {
      const token = getToken();
      if (!token) {
        throw new Error('No authentication token found');
      }

      await axios.post(
        `${API_BASE_URL}/lwp/update-bulk`,
        lwpRecords,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setUpdateStatus({ message: 'Bulk LWP updated successfully.', type: 'success' });
      fetchLWPRecords();
    } catch (err: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error bulk updating LWP:', err);
      }
      setUpdateStatus({ message: 'Failed to bulk update LWP.', type: 'danger' });
    } finally {
      setIsUpdatingBulk(false);
    }
  };

  const handleImport = async (): Promise<void> => {
    if (!file) {
      setUploadStatus({ message: 'Please select a file.', type: 'danger' });
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const token = getToken();
      if (!token) {
        throw new Error('No authentication token found');
      }

      const response: AxiosResponse<ImportResponse> = await axios.post(
        `${API_BASE_URL}/lwp/import`,
        formData,
        {
          headers: { 
            Authorization: `Bearer ${token}`, 
            'Content-Type': 'multipart/form-data' 
          },
        }
      );
      setUploadStatus({ 
        message: response.data.msg || 'LWP data imported successfully.', 
        type: 'success' 
      });
      fetchLWPRecords();
    } catch (err: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error importing LWP data:', err);
      }
      setUploadStatus({ message: 'Failed to import LWP data.', type: 'danger' });
    }
  };

  const handleExport = async (): Promise<void> => {
    setIsExporting(true);
    try {
      const token = getToken();
      if (!token) {
        throw new Error('No authentication token found');
      }

      const response: AxiosResponse<Blob> = await axios.get(
        `${API_BASE_URL}/lwp/export`,
        {
          headers: { Authorization: `Bearer ${token}` },
          responseType: 'blob',
        }
      );
      
      const blob = new Blob([response.data], { 
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `LWP_Export_${new Date().toISOString()}.xlsx`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error exporting data:', err);
      }
    } finally {
      setIsExporting(false);
    }
  };

  const getStatusColor = (status?: string): string => {
    switch (status?.toLowerCase()) {
      case 'approved':
        return 'success.main';
      case 'pending':
        return 'warning.main';
      case 'rejected':
        return 'error.main';
      default:
        return 'grey.500';
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    const selectedFile = event.target.files?.[0] || null;
    setFile(selectedFile);
  };

  const getAlertSeverity = (type: string): AlertColor => {
    switch (type) {
      case 'success':
        return 'success';
      case 'danger':
      case 'error':
        return 'error';
      default:
        return 'info';
    }
  };

  const handleDeleteLWP = (id: string | number): void => {
    // TODO: Implement delete functionality
    if (process.env.NODE_ENV === 'development') {
      // eslint-disable-next-line no-console
      console.log('Delete LWP with ID:', id);
    }
  };

  return (
    <Box>
      <Container>
        <Typography variant="h4" sx={{ mt: 4, mb: 4 }}>
          LWP Management
        </Typography>
        
        {/* Error Display */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Existing LWP Records */}
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow sx={{ 
                '& .MuiTableCell-head': { 
                  backgroundColor: 'primary.main',
                  color: 'white',
                  fontWeight: 'bold',
                  fontSize: '0.875rem',
                  padding: '12px 16px'
                }
              }}>
                <TableCell>Employee</TableCell>
                <TableCell>Start Date</TableCell>
                <TableCell>End Date</TableCell>
                <TableCell>Days</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 3 }}>
                      <CircularProgress size={24} sx={{ mr: 2 }} />
                      Loading...
                    </Box>
                  </TableCell>
                </TableRow>
              ) : lwpRecords.length > 0 ? (
                lwpRecords.map((lwp) => (
                  <TableRow 
                    key={lwp.id}
                    sx={{ 
                      '&:hover': { 
                        backgroundColor: 'action.hover',
                        cursor: 'pointer'
                      }
                    }}
                  >
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        {lwp.employee_name}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      {new Date(lwp.start_date).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      {new Date(lwp.end_date).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        {lwp.days}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box
                        component="span"
                        sx={{
                          display: 'inline-block',
                          padding: '4px 8px',
                          borderRadius: '4px',
                          backgroundColor: getStatusColor(lwp.status),
                          color: 'white',
                          fontSize: '0.75rem',
                          fontWeight: 'bold',
                          textTransform: 'capitalize'
                        }}
                      >
                        {lwp.status}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Button
                          variant="contained"
                          color="primary"
                          size="small"
                          onClick={() => handleUpdateLWP(lwp.id, lwp.present_days)}
                        >
                          Edit
                        </Button>
                        <Button
                          variant="contained"
                          color="error"
                          size="small"
                          onClick={() => handleDeleteLWP(lwp.id)}
                        >
                          Delete
                        </Button>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={6} align="center" sx={{ py: 6 }}>
                    <Typography variant="body1" color="text.secondary">
                      No LWP records found
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Update Status */}
        {updateStatus.message && (
          <Alert severity={getAlertSeverity(updateStatus.type)} sx={{ mt: 2 }}>
            {updateStatus.message}
          </Alert>
        )}

        {/* Bulk Update Button */}
        <Button 
          sx={{ mt: 3 }} 
          variant="contained" 
          color="warning" 
          onClick={handleBulkUpdate} 
          disabled={isUpdatingBulk || lwpRecords.length === 0}
        >
          {isUpdatingBulk ? (
            <>
              <CircularProgress color="inherit" size={20} sx={{ mr: 1 }} />
              Updating...
            </>
          ) : (
            'Update Bulk'
          )}
        </Button>

        {/* Import/Export Section */}
        <Typography variant="h5" sx={{ mt: 5, mb: 2 }}>
          Import/Export LWP Data
        </Typography>

        {/* Export Button */}
        <Button 
          sx={{ mb: 3 }}
          variant="outlined" 
          color="success" 
          onClick={handleExport} 
          disabled={isExporting}
        >
          {isExporting ? (
            <>
              <CircularProgress color="inherit" size={20} sx={{ mr: 1 }} />
              Exporting...
            </>
          ) : (
            'Export'
          )}
        </Button>

        {/* Import Section */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="body1" sx={{ mb: 1 }}>
            Import LWP Data
          </Typography>
          <TextField
            type="file"
            inputProps={{ accept: ".xlsx, .xls" }}
            onChange={handleFileChange}
            fullWidth
            helperText="Select an Excel file (.xlsx or .xls) to import LWP data"
          />
        </Box>
        
        <Button 
          variant="contained" 
          onClick={handleImport}
          disabled={!file}
        >
          Import
        </Button>

        {/* Upload Status */}
        {uploadStatus.message && (
          <Alert severity={getAlertSeverity(uploadStatus.type)} sx={{ mt: 3 }}>
            {uploadStatus.message}
          </Alert>
        )}
      </Container>
    </Box>
  );
};

export default LWPManagement; 