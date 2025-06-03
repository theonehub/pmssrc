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
  CircularProgress,
  AlertColor
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

// Define interfaces
interface PublicHoliday {
  holiday_id: string | number;
  name: string;
  date: string;
  description?: string;
  created_by?: string;
  created_at?: string;
  updated_at?: string;
}

interface HolidayFormData {
  name: string;
  date: string;
  description?: string;
}

interface AlertState {
  open: boolean;
  message: string;
  severity: AlertColor;
}

interface FormattedDate {
  formatted: string;
  isUpcoming: boolean;
}

const PublicHolidays: React.FC = () => {
  // State management with proper typing
  const [holidays, setHolidays] = useState<PublicHoliday[]>([]);
  const [filteredHolidays, setFilteredHolidays] = useState<PublicHoliday[]>([]);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [openAddDialog, setOpenAddDialog] = useState<boolean>(false);
  const [openImportDialog, setOpenImportDialog] = useState<boolean>(false);
  const [openEditDialog, setOpenEditDialog] = useState<boolean>(false);
  const [selectedHoliday, setSelectedHoliday] = useState<PublicHoliday | null>(null);
  const [alert, setAlert] = useState<AlertState>({ 
    open: false, 
    message: '', 
    severity: 'success' 
  });
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | number | null>(null);

  // Memoized fetch function
  const fetchHolidays = useCallback(async (showRefreshLoader = false): Promise<void> => {
    if (showRefreshLoader) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    try {
      const response = await api.get('/api/v2/public-holidays');
      setHolidays(response.data || []);
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error fetching holidays:', error);
      }
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
  const showAlert = (message: string, severity: AlertColor = 'success'): void => {
    setAlert({ open: true, message, severity });
  };

  const handleCloseAlert = (): void => {
    setAlert(prev => ({ ...prev, open: false }));
  };

  // Event handlers
  const handleAddHoliday = async (holidayData: HolidayFormData): Promise<void> => {
    try {
      await api.post('/api/v2/public-holidays/', holidayData);
      fetchHolidays();
      setOpenAddDialog(false);
      showAlert('Holiday added successfully!', 'success');
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error adding holiday:', error);
      }
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to add holiday';
      showAlert(errorMessage, 'error');
      throw error;
    }
  };

  const handleEditHoliday = async (holidayId: string | number, holidayData: HolidayFormData): Promise<void> => {
    try {
      await api.put(`/api/v2/public-holidays/${holidayId}`, holidayData);
      fetchHolidays();
      setOpenEditDialog(false);
      setSelectedHoliday(null);
      showAlert('Holiday updated successfully!', 'success');
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error updating holiday:', error);
      }
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to update holiday';
      showAlert(errorMessage, 'error');
      throw error;
    }
  };

  const handleDeleteClick = (holidayId: string | number): void => {
    setDeleteConfirmId(holidayId);
  };

  const handleDeleteConfirm = async (): Promise<void> => {
    if (!deleteConfirmId) return;

    try {
      await api.delete(`/api/v2/public-holidays/${deleteConfirmId}`);
      fetchHolidays();
      showAlert('Holiday deleted successfully!', 'success');
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error deleting holiday:', error);
      }
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to delete holiday';
      showAlert(errorMessage, 'error');
    } finally {
      setDeleteConfirmId(null);
    }
  };

  const handleDeleteCancel = (): void => {
    setDeleteConfirmId(null);
  };

  const handleImportHolidays = async (file: File): Promise<void> => {
    try {
      await api.upload('/api/v2/public-holidays/import/with-file', file);
      fetchHolidays();
      setOpenImportDialog(false);
      showAlert('Holidays imported successfully!', 'success');
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error importing holidays:', error);
      }
      showAlert('Failed to import holidays. Please check your file format.', 'error');
      throw error;
    }
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setSearchTerm(event.target.value);
  };

  const handleRefresh = (): void => {
    fetchHolidays(true);
  };

  const handleEditClick = (holiday: PublicHoliday): void => {
    setSelectedHoliday(holiday);
    setOpenEditDialog(true);
  };

  // Render helpers
  const renderTableSkeleton = (): React.ReactElement[] => (
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

  const renderEmptyState = (): React.ReactElement => (
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

  const formatDate = (dateString: string): FormattedDate => {
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
    <PageLayout title="Public Holidays">
      <Box sx={{ p: 3 }}>
        {/* Header */}
        <Card elevation={1} sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ 
              display: 'grid', 
              gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' }, 
              gap: 2, 
              alignItems: 'center' 
            }}>
              <Box>
                <Typography variant="h4" color="primary" gutterBottom>
                  Public Holidays
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Manage public holidays and special dates
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', gap: 1, justifyContent: { xs: 'flex-start', sm: 'flex-end' }, flexWrap: 'wrap' }}>
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
            </Box>
          </CardContent>
        </Card>

        {/* Search */}
        <Paper elevation={1} sx={{ p: 2, mb: 3 }}>
          <Box sx={{ 
            display: 'grid', 
            gridTemplateColumns: { xs: '1fr', md: '2fr 1fr' }, 
            gap: 2, 
            alignItems: 'center' 
          }}>
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
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="body2" color="text.secondary">
                {loading ? 'Loading...' : `${filteredHolidays.length} holiday${filteredHolidays.length !== 1 ? 's' : ''}`}
              </Typography>
              {refreshing && <CircularProgress size={16} />}
            </Box>
          </Box>
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