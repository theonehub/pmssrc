import React, { useState } from 'react';
import axios from 'axios';
import { getToken } from '../../shared/utils/auth';
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
  Snackbar,
  Alert,
  Chip,
  TablePagination,
  InputAdornment,
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import type { Organisation } from '../../models/organisation';
import { useOrganisationsQuery } from '../../shared/hooks/useOrganisations';
import FormDialog from '../Common/UIComponents/FormDialog';

const API_BASE_URL = 'http://localhost:8000/api/v2';

interface ToastState {
  show: boolean;
  message: string;
  severity: 'success' | 'error' | 'warning' | 'info';
}

const OrganisationsList: React.FC = () => {
  const navigate = useNavigate();
  
  // State management
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [page, setPage] = useState<number>(0);
  const [rowsPerPage, setRowsPerPage] = useState<number>(10);
  const [toast, setToast] = useState<ToastState>({ 
    show: false, 
    message: '', 
    severity: 'success' 
  });
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState<boolean>(false);

  const { data, isLoading, refetch } = useOrganisationsQuery({
    skip: page * rowsPerPage,
    limit: rowsPerPage,
    search: searchTerm || undefined
  });

  const organisations = data?.data?.organisations || data?.organisations || [];
  const total = data?.data?.total || data?.total || 0;

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
    if (organisation.organisation_id) {
      navigate(`/organisations/edit/${organisation.organisation_id}`);
    }
  };

  const handleView = (organisation: Organisation): void => {
    if (organisation.organisation_id) {
      navigate(`/organisations/${organisation.organisation_id}`);
    }
  };

  const handleDeleteClick = (id: string | undefined): void => {
    if (id) {
      setDeleteConfirmId(id);
    }
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
      refetch();
    } catch (error: any) {
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
    setRefreshing(true);
    refetch().finally(() => setRefreshing(false));
  };

  // Render helpers
  const renderTableSkeleton = (): React.ReactElement[] => (
    Array(rowsPerPage).fill(null).map((_, index) => (
      <TableRow key={index}>
        <TableCell colSpan={6}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Chip label="Loading..." />
          </Box>
        </TableCell>
      </TableRow>
    ))
  );

  const renderStatusChip = (isActive: boolean): React.ReactElement => (
    <Chip
      label={isActive ? 'Active' : 'Inactive'}
      color={isActive ? 'success' : 'default'}
      size="small"
    />
  );

  const renderEmptyState = (): React.ReactElement => (
    <TableRow>
      <TableCell colSpan={6}>
        <Box sx={{ py: 3, textAlign: 'center' }}>
          <Typography variant="body1" color="textSecondary">
            No organisations found
          </Typography>
        </Box>
      </TableCell>
    </TableRow>
  );

  const formatDate = (dateString: string | undefined): string => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <Box p={3}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">Organisations</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAdd}
        >
          Add Organisation
        </Button>
      </Box>

      {/* Search and Filter */}
      <Box mb={3} display="flex" gap={2}>
        <TextField
          placeholder="Search organisations..."
          value={searchTerm}
          onChange={handleSearchChange}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
          sx={{ width: 300 }}
        />
        <Button
          startIcon={<RefreshIcon />}
          onClick={handleRefresh}
          disabled={refreshing}
        >
          Refresh
        </Button>
      </Box>

      {/* Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Employee Strength</TableCell>
              <TableCell>Created At</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {isLoading ? (
              renderTableSkeleton()
            ) : organisations.length === 0 ? (
              renderEmptyState()
            ) : (
              organisations.map((org: Organisation) => (
                <TableRow key={org.organisation_id || 'temp-key'}>
                  <TableCell>{org.name}</TableCell>
                  <TableCell>{org.organisation_type}</TableCell>
                  <TableCell>{renderStatusChip(!!org.is_active)}</TableCell>
                  <TableCell>{org.employee_strength || 0}</TableCell>
                  <TableCell>
                    {formatDate(org.created_at)}
                  </TableCell>
                  <TableCell align="right">
                    <Box display="flex" justifyContent="flex-end" gap={1}>
                      <Button
                        size="small"
                        onClick={() => handleView(org)}
                        disabled={!org.organisation_id}
                      >
                        View
                      </Button>
                      <Button
                        size="small"
                        onClick={() => handleEdit(org)}
                        disabled={!org.organisation_id}
                      >
                        Edit
                      </Button>
                      <Button
                        size="small"
                        color="error"
                        onClick={() => handleDeleteClick(org.organisation_id)}
                        disabled={!org.organisation_id}
                      >
                        Delete
                      </Button>
                    </Box>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Pagination */}
      <TablePagination
        component="div"
        count={total}
        page={page}
        onPageChange={handlePageChange}
        rowsPerPage={rowsPerPage}
        onRowsPerPageChange={handleRowsPerPageChange}
        rowsPerPageOptions={[5, 10, 25, 50]}
      />

      {/* Delete Confirmation Dialog */}
      <FormDialog
        open={!!deleteConfirmId}
        onClose={handleDeleteCancel}
        title="Confirm Delete"
        submitLabel="Delete"
        cancelLabel="Cancel"
        onSubmit={handleDeleteConfirm}
      >
        <Typography>
          Are you sure you want to delete this organisation? This action cannot be undone.
        </Typography>
      </FormDialog>

      {/* Toast */}
      <Snackbar
        open={toast.show}
        autoHideDuration={6000}
        onClose={closeToast}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={closeToast} severity={toast.severity}>
          {toast.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default OrganisationsList;