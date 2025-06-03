import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { getToken } from '../../utils/auth';
import PageLayout from '../../layout/PageLayout';
import { useNavigate } from 'react-router-dom';
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
  TextField,
  CircularProgress,
  Snackbar,
  Alert,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Chip,
  TablePagination,
  InputAdornment,
  Card,
  CardContent,
  Skeleton,
  Tooltip,
  IconButton,
  Fade
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
  Business as BusinessIcon
} from '@mui/icons-material';
import type { Organisation } from '../../models/organisation';

const API_BASE_URL = 'http://localhost:8000/api/v2';

// Define interfaces
interface OrganisationsResponse {
  organisations: Organisation[];
  total: number;
}

interface ToastState {
  show: boolean;
  message: string;
  severity: 'success' | 'error' | 'warning' | 'info';
}

const OrganisationsList: React.FC = () => {
  const navigate = useNavigate();
  
  // State management
  const [organisations, setOrganisations] = useState<Organisation[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [page, setPage] = useState<number>(0);
  const [rowsPerPage, setRowsPerPage] = useState<number>(10);
  const [total, setTotal] = useState<number>(0);
  const [toast, setToast] = useState<ToastState>({ 
    show: false, 
    message: '', 
    severity: 'success' 
  });
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState<boolean>(false);

  // Memoized fetch function
  const fetchOrganisations = useCallback(async (showRefreshLoader = false): Promise<void> => {
    if (showRefreshLoader) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    try {
      const token = getToken();
      if (!token) {
        throw new Error('No authentication token found');
      }

      const response = await axios.get<OrganisationsResponse>(
        `${API_BASE_URL}/organisations/`,
        {
          params: {
            skip: page * rowsPerPage,
            limit: rowsPerPage,
            search: searchTerm || undefined
          },
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      setOrganisations(response.data.organisations || []);
      setTotal(response.data.total || 0);
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error fetching organisations:', error);
      }
      const errorMessage = error.response?.data?.detail || 
                          error.message || 
                          'Failed to load organisations';
      
      showToast(errorMessage, 'error');
      
      // Reset data on error
      setOrganisations([]);
      setTotal(0);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [page, rowsPerPage, searchTerm]);

  // Effects
  useEffect(() => {
    fetchOrganisations();
  }, [fetchOrganisations]);

  // Helper functions
  const showToast = (message: string, severity: ToastState['severity'] = 'success'): void => {
    setToast({ show: true, message, severity });
  };

  const closeToast = (): void => {
    setToast(prev => ({ ...prev, show: false }));
  };

  // Event handlers
  const handleAdd = (): void => {
    navigate('/organisations/add');
  };

  const handleEdit = (organisation: Organisation): void => {
    navigate(`/organisations/edit/${organisation.organisation_id}`);
  };

  const handleDeleteClick = (id: string): void => {
    setDeleteConfirmId(id);
  };

  const handleDeleteConfirm = async (): Promise<void> => {
    if (!deleteConfirmId) return;

    try {
      const token = getToken();
      if (!token) {
        throw new Error('No authentication token found');
      }

      await axios.delete(
        `${API_BASE_URL}/organisations/${deleteConfirmId}/`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      
      showToast('Organisation deleted successfully', 'success');
      fetchOrganisations();
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error deleting organisation:', error);
      }
      const errorMessage = error.response?.data?.detail || 
                          error.message || 
                          'Failed to delete organisation';
      showToast(errorMessage, 'error');
    } finally {
      setDeleteConfirmId(null);
    }
  };

  const handleDeleteCancel = (): void => {
    setDeleteConfirmId(null);
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setSearchTerm(event.target.value);
    setPage(0); // Reset to first page when searching
  };

  const handlePageChange = (_event: unknown, newPage: number): void => {
    setPage(newPage);
  };

  const handleRowsPerPageChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleRefresh = (): void => {
    fetchOrganisations(true);
  };

  // Render helpers
  const renderTableSkeleton = (): React.ReactElement[] => (
    Array.from({ length: rowsPerPage }).map((_, index) => (
      <TableRow key={index}>
        <TableCell><Skeleton /></TableCell>
        <TableCell><Skeleton /></TableCell>
        <TableCell><Skeleton /></TableCell>
        <TableCell><Skeleton /></TableCell>
        <TableCell><Skeleton /></TableCell>
        <TableCell><Skeleton /></TableCell>
        <TableCell><Skeleton width={120} /></TableCell>
      </TableRow>
    ))
  );

  const renderStatusChip = (isActive: boolean): React.ReactElement => (
    <Chip
      label={isActive ? 'Active' : 'Inactive'}
      color={isActive ? 'success' : 'default'}
      size="small"
      variant="outlined"
    />
  );

  const renderEmptyState = (): React.ReactElement => (
    <TableRow>
      <TableCell colSpan={7} align="center" sx={{ py: 6 }}>
        <Box sx={{ textAlign: 'center' }}>
          <BusinessIcon 
            sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} 
          />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            {searchTerm ? 'No organisations found' : 'No organisations yet'}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {searchTerm 
              ? `No organisations match "${searchTerm}"`
              : 'Get started by adding your first organisation'
            }
          </Typography>
          {!searchTerm && (
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleAdd}
            >
              Add Organisation
            </Button>
          )}
        </Box>
      </TableCell>
    </TableRow>
  );

  return (
    <PageLayout title="Organisations">
      <Box sx={{ p: 3 }}>
        {/* Header */}
        <Card elevation={1} sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' }, gap: 2, alignItems: 'center' }}>
              <Box>
                <Typography variant="h4" color="primary" gutterBottom>
                  Organisations
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Manage your organisations and their details
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', gap: 1, justifyContent: { xs: 'flex-start', sm: 'flex-end' } }}>
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
                  variant="contained" 
                  startIcon={<AddIcon />} 
                  onClick={handleAdd}
                  size="large"
                >
                  Add Organisation
                </Button>
              </Box>
            </Box>
          </CardContent>
        </Card>

        {/* Search and Filters */}
        <Paper elevation={1} sx={{ p: 2, mb: 3 }}>
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '2fr 1fr' }, gap: 2, alignItems: 'center' }}>
            <TextField
              fullWidth
              label="Search organisations"
              variant="outlined"
              value={searchTerm}
              onChange={handleSearchChange}
              placeholder="Search by name, city, or country..."
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
                {loading ? 'Loading...' : `${total} organisation${total !== 1 ? 's' : ''}`}
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
                  <TableCell>Organisation Name</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Phone</TableCell>
                  <TableCell>City</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="center">Employee Strength</TableCell>
                  <TableCell align="center">Used Strength</TableCell>
                  <TableCell align="center">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  renderTableSkeleton()
                ) : organisations.length > 0 ? (
                  organisations.map((org) => (
                    <Fade in key={org.organisation_id} timeout={300}>
                      <TableRow 
                        hover
                        sx={{ 
                          '&:hover': { 
                            backgroundColor: 'action.hover' 
                          }
                        }}
                      >
                        <TableCell>
                          <Box>
                            <Typography variant="subtitle2" fontWeight="medium">
                              {org.name}
                            </Typography>
                            {org.city && (
                              <Typography variant="caption" color="text.secondary">
                                {org.city}
                              </Typography>
                            )}
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {org.email || 'N/A'}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {org.phone || 'N/A'}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {org.city || 'N/A'}
                          </Typography>
                        </TableCell>
                        <TableCell>{renderStatusChip(org.is_active)}</TableCell>
                        <TableCell align="center">
                          <Typography variant="body2" fontWeight="medium">
                            {org.employee_strength || 'N/A'}
                          </Typography>
                        </TableCell>
                        <TableCell align="center">
                          <Typography variant="body2">
                            {org.used_employee_strength || 0}
                          </Typography>
                        </TableCell>
                        <TableCell align="center">
                          <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center' }}>
                            <Tooltip title="Edit">
                              <IconButton
                                size="small"
                                color="primary"
                                onClick={() => handleEdit(org)}
                              >
                                <EditIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Delete">
                              <IconButton
                                size="small"
                                color="error"
                                onClick={() => handleDeleteClick(org.organisation_id!)}
                              >
                                <DeleteIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        </TableCell>
                      </TableRow>
                    </Fade>
                  ))
                ) : (
                  renderEmptyState()
                )}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Pagination */}
          {total > 0 && (
            <TablePagination
              component="div"
              count={total}
              page={page}
              onPageChange={handlePageChange}
              rowsPerPage={rowsPerPage}
              onRowsPerPageChange={handleRowsPerPageChange}
              rowsPerPageOptions={[5, 10, 25, 50]}
              showFirstButton
              showLastButton
            />
          )}
        </Paper>

        {/* Toast Notifications */}
        <Snackbar
          open={toast.show}
          autoHideDuration={6000}
          onClose={closeToast}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <Alert 
            onClose={closeToast} 
            severity={toast.severity}
            sx={{ width: '100%' }}
            variant="filled"
          >
            {toast.message}
          </Alert>
        </Snackbar>

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
              Are you sure you want to delete this organisation? This action cannot be undone.
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
      </Box>
    </PageLayout>
  );
};

export default OrganisationsList; 