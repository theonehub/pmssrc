import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Button,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Snackbar,
  Alert,
  IconButton,
  Card,
  CardContent,
  Grid,
  TextField,
  InputAdornment,
  Skeleton,
  Tooltip,
  Fade,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Chip,
  CircularProgress
} from '@mui/material';
import {
  Add as AddIcon,
  UploadFile as UploadFileIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
  Event as EventIcon,
  CalendarToday as CalendarIcon
} from '@mui/icons-material';
import AddHolidayDialog from './AddHolidayDialog';
import ImportHolidaysDialog from './ImportHolidaysDialog';
import EditHolidayDialog from './EditHolidayDialog';
import PageLayout from '../../layout/PageLayout';
import api from '../../utils/apiUtils';

const PublicHolidays = () => {
  // State management
  const [holidays, setHolidays] = useState([]);
  const [filteredHolidays, setFilteredHolidays] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [openAddDialog, setOpenAddDialog] = useState(false);
  const [openImportDialog, setOpenImportDialog] = useState(false);
  const [openEditDialog, setOpenEditDialog] = useState(false);
  const [selectedHoliday, setSelectedHoliday] = useState(null);
  const [alert, setAlert] = useState({ 
    open: false, 
    message: '', 
    severity: 'success' 
  });
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [deleteConfirmId, setDeleteConfirmId] = useState(null);

  // Memoized fetch function
  const fetchHolidays = useCallback(async (showRefreshLoader = false) => {
    if (showRefreshLoader) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    try {
      const response = await api.get('/public-holidays');
      setHolidays(response.data || []);
    } catch (error) {
      console.error('Error fetching holidays:', error);
      showAlert('Failed to fetch holidays. Please try again.', 'error');
      setHolidays([]);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  // Filter holidays based on search term
  useEffect(() => {
    if (!searchTerm.trim()) {
      setFilteredHolidays(holidays);
    } else {
      const filtered = holidays.filter(holiday =>
        holiday.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        holiday.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        new Date(holiday.date).toLocaleDateString().includes(searchTerm)
      );
      setFilteredHolidays(filtered);
    }
  }, [holidays, searchTerm]);

  useEffect(() => {
    fetchHolidays();
  }, [fetchHolidays]);

  // Helper functions
  const showAlert = (message, severity = 'success') => {
    setAlert({ open: true, message, severity });
  };

  const handleCloseAlert = () => {
    setAlert(prev => ({ ...prev, open: false }));
  };

  // Event handlers
  const handleAddHoliday = async (holidayData) => {
    try {
      await api.post('/public-holidays/', holidayData);
      fetchHolidays();
      setOpenAddDialog(false);
      showAlert('Holiday added successfully!', 'success');
    } catch (error) {
      console.error('Error adding holiday:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to add holiday';
      showAlert(errorMessage, 'error');
      throw error;
    }
  };

  const handleEditHoliday = async (holidayId, holidayData) => {
    try {
      await api.put(`/public-holidays/${holidayId}`, holidayData);
      fetchHolidays();
      setOpenEditDialog(false);
      setSelectedHoliday(null);
      showAlert('Holiday updated successfully!', 'success');
    } catch (error) {
      console.error('Error updating holiday:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to update holiday';
      showAlert(errorMessage, 'error');
      throw error;
    }
  };

  const handleDeleteClick = (holidayId) => {
    setDeleteConfirmId(holidayId);
  };

  const handleDeleteConfirm = async () => {
    if (!deleteConfirmId) return;

    try {
      await api.delete(`/public-holidays/${deleteConfirmId}`);
      fetchHolidays();
      showAlert('Holiday deleted successfully!', 'success');
    } catch (error) {
      console.error('Error deleting holiday:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to delete holiday';
      showAlert(errorMessage, 'error');
    } finally {
      setDeleteConfirmId(null);
    }
  };

  const handleDeleteCancel = () => {
    setDeleteConfirmId(null);
  };

  const handleImportHolidays = async (file) => {
    try {
      await api.upload('/public-holidays/import/with-file', file);
      fetchHolidays();
      setOpenImportDialog(false);
      showAlert('Holidays imported successfully!', 'success');
    } catch (error) {
      console.error('Error importing holidays:', error);
      showAlert('Failed to import holidays. Please check your file format.', 'error');
      throw error;
    }
  };

  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
  };

  const handleRefresh = () => {
    fetchHolidays(true);
  };

  const handleEditClick = (holiday) => {
    setSelectedHoliday(holiday);
    setOpenEditDialog(true);
  };

  // Render helpers
  const renderTableSkeleton = () => (
    Array.from({ length: 5 }).map((_, index) => (
      <TableRow key={index}>
        <TableCell><Skeleton /></TableCell>
        <TableCell><Skeleton /></TableCell>
        <TableCell><Skeleton /></TableCell>
        <TableCell><Skeleton /></TableCell>
        <TableCell><Skeleton width={120} /></TableCell>
      </TableRow>
    ))
  );

  const renderEmptyState = () => (
    <TableRow>
      <TableCell colSpan={5} align="center" sx={{ py: 6 }}>
        <Box sx={{ textAlign: 'center' }}>
          <CalendarIcon 
            sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} 
          />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            {searchTerm ? 'No holidays found' : 'No holidays yet'}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {searchTerm 
              ? `No holidays match "${searchTerm}"`
              : 'Get started by adding your first holiday'
            }
          </Typography>
          {!searchTerm && (
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setOpenAddDialog(true)}
            >
              Add Holiday
            </Button>
          )}
        </Box>
      </TableCell>
    </TableRow>
  );

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const today = new Date();
    const isUpcoming = date > today;
    
    return {
      formatted: date.toLocaleDateString('en-GB', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
      }),
      isUpcoming
    };
  };

  return (
    <PageLayout>
      <Box sx={{ p: 3 }}>
        {/* Header */}
        <Card elevation={1} sx={{ mb: 3 }}>
          <CardContent>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={6}>
                <Typography variant="h4" color="primary" gutterBottom>
                  Public Holidays
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Manage public holidays and special dates
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end', flexWrap: 'wrap' }}>
                  <Tooltip title="Refresh">
                    <IconButton 
                      onClick={handleRefresh}
                      disabled={refreshing}
                      color="primary"
                    >
                      <RefreshIcon />
                    </IconButton>
                  </Tooltip>
                  <Button
                    variant="outlined"
                    startIcon={<UploadFileIcon />}
                    onClick={() => setOpenImportDialog(true)}
                    size="large"
                  >
                    Import
                  </Button>
                  <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={() => setOpenAddDialog(true)}
                    size="large"
                  >
                    Add Holiday
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Search */}
        <Paper elevation={1} sx={{ p: 2, mb: 3 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={8}>
              <TextField
                fullWidth
                label="Search holidays"
                variant="outlined"
                value={searchTerm}
                onChange={handleSearchChange}
                placeholder="Search by name, description, or date..."
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon color="action" />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  {loading ? 'Loading...' : `${filteredHolidays.length} holiday${filteredHolidays.length !== 1 ? 's' : ''}`}
                </Typography>
                {refreshing && <CircularProgress size={16} />}
              </Box>
            </Grid>
          </Grid>
        </Paper>

        {/* Table */}
        <Paper elevation={1}>
          <TableContainer>
            <Table stickyHeader>
              <TableHead>
                <TableRow sx={{ 
                  '& .MuiTableCell-head': { 
                    backgroundColor: 'primary.main',
                    color: 'white',
                    fontWeight: 'bold',
                    fontSize: '0.875rem'
                  }
                }}>
                  <TableCell>Holiday Name</TableCell>
                  <TableCell>Date</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell>Created By</TableCell>
                  <TableCell align="center">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  renderTableSkeleton()
                ) : filteredHolidays.length > 0 ? (
                  filteredHolidays.map((holiday) => {
                    const { formatted: formattedDate, isUpcoming } = formatDate(holiday.date);
                    return (
                      <Fade in key={holiday.holiday_id} timeout={300}>
                        <TableRow 
                          hover
                          sx={{ 
                            '&:hover': { 
                              backgroundColor: 'action.hover' 
                            }
                          }}
                        >
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <EventIcon color="action" sx={{ fontSize: 20 }} />
                              <Typography variant="subtitle2" fontWeight="medium">
                                {holiday.name}
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Typography variant="body2">
                                {formattedDate}
                              </Typography>
                              {isUpcoming && (
                                <Chip 
                                  label="Upcoming" 
                                  size="small" 
                                  color="primary" 
                                  variant="outlined" 
                                />
                              )}
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" color="text.secondary">
                              {holiday.description || 'No description'}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {holiday.created_by || 'System'}
                            </Typography>
                          </TableCell>
                          <TableCell align="center">
                            <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center' }}>
                              <Tooltip title="Edit">
                                <IconButton
                                  size="small"
                                  color="primary"
                                  onClick={() => handleEditClick(holiday)}
                                >
                                  <EditIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="Delete">
                                <IconButton
                                  size="small"
                                  color="error"
                                  onClick={() => handleDeleteClick(holiday.holiday_id)}
                                >
                                  <DeleteIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            </Box>
                          </TableCell>
                        </TableRow>
                      </Fade>
                    );
                  })
                ) : (
                  renderEmptyState()
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>

        {/* Dialogs */}
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
          onClose={() => {
            setOpenEditDialog(false);
            setSelectedHoliday(null);
          }}
          onSubmit={handleEditHoliday}
          holiday={selectedHoliday}
        />

        {/* Delete Confirmation Dialog */}
        <Dialog
          open={!!deleteConfirmId}
          onClose={handleDeleteCancel}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle color="error.main">
            Confirm Deletion
          </DialogTitle>
          <DialogContent>
            <Typography>
              Are you sure you want to delete this holiday? This action cannot be undone.
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleDeleteCancel}>
              Cancel
            </Button>
            <Button 
              onClick={handleDeleteConfirm} 
              color="error" 
              variant="contained"
              autoFocus
            >
              Delete
            </Button>
          </DialogActions>
        </Dialog>

        {/* Toast Notifications */}
        <Snackbar 
          open={alert.open} 
          autoHideDuration={6000} 
          onClose={handleCloseAlert}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <Alert 
            onClose={handleCloseAlert} 
            severity={alert.severity}
            sx={{ width: '100%' }}
            variant="filled"
          >
            {alert.message}
          </Alert>
        </Snackbar>
      </Box>
    </PageLayout>
  );
};

export default PublicHolidays; 