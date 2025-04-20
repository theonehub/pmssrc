import React, { useEffect, useState } from 'react';
import { Button, Container, Table, CircularProgress, Alert, TableContainer, TableHead, TableBody, TableRow, TableCell, Box, TextField, Typography } from '@mui/material';
import axios from 'axios';
import { getToken } from '../../../utils/auth';
import PageLayout from '../../../layout/PageLayout';
import * as XLSX from 'xlsx';
import { Paper } from '@mui/material';

const LWPManagement = () => {
  const [lwpRecords, setLwpRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState({ message: '', type: '' });
  const [isUpdatingBulk, setIsUpdatingBulk] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [updateStatus, setUpdateStatus] = useState({ message: '', type: '' });

  useEffect(() => {
    fetchLWPRecords();
  }, []);

  const fetchLWPRecords = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get('http://localhost:8000/lwp', {
        headers: { Authorization: `Bearer ${getToken()}` },
      });
      setLwpRecords(response.data);
    } catch (err) {
      setError('Failed to fetch LWP records.');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateLWP = async (id, presentDays) => {
    setUpdateStatus({ message: '', type: '' });
    try {
      await axios.put(`http://localhost:8000/lwp/${id}`, { present_days: presentDays }, {
        headers: { Authorization: `Bearer ${getToken()}` },
      });
      setUpdateStatus({ message: 'LWP updated successfully.', type: 'success' });
      fetchLWPRecords();
    } catch (err) {
      setUpdateStatus({ message: 'Failed to update LWP.', type: 'danger' });
    }
  };

  const handleBulkUpdate = async () => {
    setIsUpdatingBulk(true);
    setUpdateStatus({ message: '', type: '' });
    try {
      await axios.post('http://localhost:8000/lwp/update-bulk', lwpRecords, {
        headers: { Authorization: `Bearer ${getToken()}` },
      });
      setUpdateStatus({ message: 'Bulk LWP updated successfully.', type: 'success' });
      fetchLWPRecords();
    } catch (err) {
      setUpdateStatus({ message: 'Failed to bulk update LWP.', type: 'danger' });
    } finally {
      setIsUpdatingBulk(false);
    }
  };

  const handleImport = async () => {
    if (!file) {
      setUploadStatus({ message: 'Please select a file.', type: 'danger' });
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/lwp/import', formData, {
        headers: { Authorization: `Bearer ${getToken()}`, 'Content-Type': 'multipart/form-data' },
      });
      setUploadStatus({ message: response.data.msg || 'LWP data imported successfully.', type: 'success' });
      fetchLWPRecords();
    } catch (err) {
      setUploadStatus({ message: 'Failed to import LWP data.', type: 'danger' });
    }
  };

  const handleExport = async () => {
    setIsExporting(true);
    try {
      const response = await axios.get('http://localhost:8000/lwp/export', {
        headers: { Authorization: `Bearer ${getToken()}` },
        responseType: 'blob',
      });
      const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `LWP_Export_${new Date().toISOString()}.xlsx`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Error exporting data:', err);
    } finally {
      setIsExporting(false);
    }
  };

  const getStatusColor = (status) => {
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

  return (
    <PageLayout>
      <Container>
        <h3 className="mt-4 mb-4">LWP Management</h3>
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
                  <TableCell colSpan={6} align="center">Loading...</TableCell>
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
                    <TableCell>{lwp.employee_name}</TableCell>
                    <TableCell>{new Date(lwp.start_date).toLocaleDateString()}</TableCell>
                    <TableCell>{new Date(lwp.end_date).toLocaleDateString()}</TableCell>
                    <TableCell>{lwp.days}</TableCell>
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
                          fontWeight: 'bold'
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
                          onClick={() => {
                            // Implement delete functionality
                          }}
                        >
                          Delete
                        </Button>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={6} align="center">No LWP records found</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        {updateStatus.message && (
          <Alert variant={updateStatus.type}>{updateStatus.message}</Alert>
        )}
        {/* Bulk Update Button */}
        <Button className="mt-3" variant="warning" onClick={handleBulkUpdate} disabled={isUpdatingBulk}>
          {isUpdatingBulk ? (
            <>
              <CircularProgress color="primary" />
              Updating...
            </>
          ) : (
            'Update Bulk'
          )}
        </Button>
        {/* Import/Export Section */}
        <h4 className="mt-5">Import/Export LWP Data</h4>
        {/* Export Button */}
        <Button className="mb-3" variant="outline-success" onClick={handleExport} disabled={isExporting}>
          {isExporting ? (
            <>
              <CircularProgress color="primary" />
              Exporting...
            </>
          ) : (
            'Export'
          )}
        </Button>
        {/* Import Section */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="body1">Import LWP Data</Typography>
          <TextField
            type="file"
            inputProps={{ accept: ".xlsx, .xls" }}
            onChange={(e) => setFile(e.target.files[0])}
            fullWidth
          />
        </Box>
        <Button onClick={handleImport}>Import</Button>
        {uploadStatus.message && (
          <Alert variant={uploadStatus.type} className="mt-3">{uploadStatus.message}</Alert>
        )}
      </Container>
    </PageLayout>
  );
};

export default LWPManagement;