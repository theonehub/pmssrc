import React, { useState, useEffect } from 'react';
import { Box, Button, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Snackbar, Alert, IconButton } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddHolidayDialog from './AddHolidayDialog';
import ImportHolidaysDialog from './ImportHolidaysDialog';
import EditHolidayDialog from './EditHolidayDialog';
import PageLayout from '../../layout/PageLayout';
import api from '../../utils/apiUtils';

const PublicHolidays = () => {
  const [holidays, setHolidays] = useState([]);
  const [openAddDialog, setOpenAddDialog] = useState(false);
  const [openImportDialog, setOpenImportDialog] = useState(false);
  const [openEditDialog, setOpenEditDialog] = useState(false);
  const [selectedHoliday, setSelectedHoliday] = useState(null);
  const [alert, setAlert] = useState({ open: false, message: '', severity: 'success' });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHolidays();
  }, []);

  const fetchHolidays = async () => {
    console.log("Fetching holidays");
    try {
      const response = await api.get('/public-holidays');
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
      await api.post('/public-holidays/', holidayData);
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

  const handleEditHoliday = async (holidayId, holidayData) => {
    try {
      await api.put(`/public-holidays/${holidayId}`, holidayData);
      fetchHolidays();
      setOpenEditDialog(false);
      setAlert({
        open: true,
        message: 'Holiday updated successfully!',
        severity: 'success'
      });
    } catch (error) {
      console.error('Error updating holiday:', error);
      setAlert({
        open: true,
        message: `Failed to update holiday: ${error.response?.data?.detail || error.message}`,
        severity: 'error'
      });
    }
  };

  const handleDeleteHoliday = async (holidayId) => {
    if (window.confirm('Are you sure you want to delete this holiday?')) {
      try {
        await api.delete(`/public-holidays/${holidayId}`);
        fetchHolidays();
        setAlert({
          open: true,
          message: 'Holiday deleted successfully!',
          severity: 'success'
        });
      } catch (error) {
        console.error('Error deleting holiday:', error);
        setAlert({
          open: true,
          message: `Failed to delete holiday: ${error.response?.data?.detail || error.message}`,
          severity: 'error'
        });
      }
    }
  };

  const handleImportHolidays = async (file) => {
    try {
      await api.upload('/public-holidays/import/with-file', file);
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
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={5} align="center">Loading...</TableCell>
                </TableRow>
              ) : holidays.length > 0 ? (
                holidays.map((holiday) => (
                  <TableRow 
                    key={holiday.holiday_id}
                    sx={{ 
                      '&:hover': { 
                        backgroundColor: 'action.hover',
                      }
                    }}
                  >
                    <TableCell>{holiday.name}</TableCell>
                    <TableCell>{new Date(holiday.date).toLocaleDateString()}</TableCell>
                    <TableCell>{holiday.description}</TableCell>
                    <TableCell>{holiday.created_by}</TableCell>
                    <TableCell>
                      <IconButton 
                        color="primary" 
                        onClick={() => {
                          setSelectedHoliday(holiday);
                          setOpenEditDialog(true);
                        }}
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton 
                        color="error" 
                        onClick={() => handleDeleteHoliday(holiday.holiday_id)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={5} align="center">No holidays found</TableCell>
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

        <EditHolidayDialog
          open={openEditDialog}
          onClose={() => setOpenEditDialog(false)}
          onSubmit={handleEditHoliday}
          holiday={selectedHoliday}
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