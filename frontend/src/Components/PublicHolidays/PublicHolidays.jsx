import React, { useState, useEffect } from 'react';
import { Box, Button, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Snackbar, Alert } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import AddHolidayDialog from './AddHolidayDialog';
import ImportHolidaysDialog from './ImportHolidaysDialog';
import PageLayout from '../../layout/PageLayout';
import axiosInstance from '../../utils/axios';

const PublicHolidays = () => {
  const [holidays, setHolidays] = useState([]);
  const [openAddDialog, setOpenAddDialog] = useState(false);
  const [openImportDialog, setOpenImportDialog] = useState(false);
  const [alert, setAlert] = useState({ open: false, message: '', severity: 'success' });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHolidays();
  }, []);

  const fetchHolidays = async () => {
    console.log("Fetching holidays");
    try {
      const response = await axiosInstance.get('/public-holidays');
      setHolidays(response.data);
    } catch (error) {
      console.error('Error fetching holidays:', error);
      setAlert({
        open: true,
        message: 'Failed to fetch holidays. Please try again.',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleAddHoliday = async (holidayData) => {
    try {
      console.log("Adding holiday:", holidayData);
      await axiosInstance.post('/public-holidays/', holidayData);
      fetchHolidays();
      setOpenAddDialog(false);
      setAlert({
        open: true,
        message: 'Holiday added successfully!',
        severity: 'success'
      });
    } catch (error) {
      console.error('Error adding holiday:', error);
      console.error('Error response:', error.response?.data);
      setAlert({
        open: true,
        message: `Failed to add holiday: ${error.response?.data?.detail || error.message}`,
        severity: 'error'
      });
    }
  };

  const handleImportHolidays = async (file) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      await axiosInstance.post('/public-holidays/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      fetchHolidays();
      setOpenImportDialog(false);
      setAlert({
        open: true,
        message: 'Holidays imported successfully!',
        severity: 'success'
      });
    } catch (error) {
      console.error('Error importing holidays:', error);
      setAlert({
        open: true,
        message: 'Failed to import holidays. Please check your file format.',
        severity: 'error'
      });
    }
  };

  const handleCloseAlert = () => {
    setAlert({ ...alert, open: false });
  };

  return (
    <PageLayout title="Public Holidays">
      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h4">Public Holidays</Typography>
          <Box>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setOpenAddDialog(true)}
              sx={{ mr: 2 }}
            >
              Add Holiday
            </Button>
            <Button
              variant="outlined"
              startIcon={<UploadFileIcon />}
              onClick={() => setOpenImportDialog(true)}
            >
              Import Holidays
            </Button>
          </Box>
        </Box>

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
                <TableCell>Name</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Created By</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={4} align="center">Loading...</TableCell>
                </TableRow>
              ) : holidays.length > 0 ? (
                holidays.map((holiday) => (
                  <TableRow 
                    key={holiday.id}
                    sx={{ 
                      '&:hover': { 
                        backgroundColor: 'action.hover',
                        cursor: 'pointer'
                      }
                    }}
                  >
                    <TableCell>{holiday.name}</TableCell>
                    <TableCell>{new Date(holiday.date).toLocaleDateString()}</TableCell>
                    <TableCell>{holiday.description}</TableCell>
                    <TableCell>{holiday.created_by}</TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={4} align="center">No holidays found</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>

        <AddHolidayDialog
          open={openAddDialog}
          onClose={() => setOpenAddDialog(false)}
          onSubmit={handleAddHoliday}
        />

        <ImportHolidaysDialog
          open={openImportDialog}
          onClose={() => setOpenImportDialog(false)}
          onSubmit={handleImportHolidays}
        />

        <Snackbar 
          open={alert.open} 
          autoHideDuration={6000} 
          onClose={handleCloseAlert}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert 
            onClose={handleCloseAlert} 
            severity={alert.severity}
            sx={{ width: '100%' }}
          >
            {alert.message}
          </Alert>
        </Snackbar>
      </Box>
    </PageLayout>
  );
};

export default PublicHolidays; 