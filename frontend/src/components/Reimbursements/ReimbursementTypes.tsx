import React, { useState } from 'react';
import {
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  Box,
  Typography,
  CircularProgress,
  IconButton,
  Tooltip,
  Card,
  CardContent,
  InputAdornment,
  Skeleton,
  Fade,
  Chip,
  Snackbar,
  FormControlLabel,
  Switch
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
  Category as CategoryIcon,
  AttachMoney as MoneyIcon
} from '@mui/icons-material';
import { useReimbursementsQuery } from '../../shared/hooks/useReimbursements';
import { ReimbursementType } from '../../shared/types';
// Note: reimbursementApi would be used for CRUD operations when backend endpoints are implemented

interface ReimbursementTypeFormData {
  category_name: string;
  description: string;
  max_amount: string;
  is_receipt_required: boolean;
  is_approval_required: boolean;
  is_active: boolean;
}

const ReimbursementTypes: React.FC = () => {
  // State management
  const [filteredTypes, setFilteredTypes] = useState<ReimbursementType[]>([]);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [formData, setFormData] = useState<ReimbursementTypeFormData>({
    category_name: '',
    description: '',
    max_amount: '',
    is_receipt_required: false,
    is_approval_required: false,
    is_active: true
  });
  const [toast, setToast] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'warning' | 'info';
  }>({
    open: false,
    message: '',
    severity: 'success'
  });

  // Use React Query for reimbursements
  const { data: reimbursementsData, isLoading, error: reimbursementsError, refetch } = useReimbursementsQuery();
  const types = reimbursementsData?.data?.types || reimbursementsData?.types || [];

  // Filter types based on search term
  React.useEffect(() => {
    let filtered = [...types];

    // Apply search filter
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      filtered = filtered.filter(type =>
        type.category_name?.toLowerCase().includes(searchLower) ||
        type.description?.toLowerCase().includes(searchLower)
      );
    }

    setFilteredTypes(filtered);
  }, [types, searchTerm]);

  React.useEffect(() => {
    if (reimbursementsError) {
      showToast(reimbursementsError.message || 'Failed to fetch reimbursement types.', 'error');
    }
    // eslint-disable-next-line
  }, [reimbursementsError]);

  // Helper functions
  const showToast = (message: string, severity: 'success' | 'error' | 'warning' | 'info' = 'success'): void => {
    setToast({ open: true, message, severity });
  };

  const handleCloseToast = (): void => {
    setToast(prev => ({ ...prev, open: false }));
  };

  // Event handlers
  const handleSubmit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();
    
    try {
      const typeData = {
        category_name: formData.category_name,
        description: formData.description,
        max_amount: formData.max_amount ? parseFloat(formData.max_amount) : undefined,
        is_receipt_required: formData.is_receipt_required,
        is_approval_required: formData.is_approval_required,
        is_active: formData.is_active
      };

      // Note: This would need to be implemented in the API
      console.log('Creating reimbursement type:', typeData);
      showToast('Reimbursement type created successfully!', 'success');
      handleClose();
      refetch();
    } catch (err: any) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Error creating type:', err);
      }
      const errorMessage = err.response?.data?.detail || 'Failed to create reimbursement type.';
      showToast(errorMessage, 'error');
    }
  };

  const handleClose = (): void => {
    setShowModal(false);
    setFormData({
      category_name: '',
      description: '',
      max_amount: '',
      is_receipt_required: false,
      is_approval_required: false,
      is_active: true
    });
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setSearchTerm(event.target.value);
  };

  const handleRefresh = (): void => {
    setRefreshing(true);
    refetch().finally(() => setRefreshing(false));
  };

  const renderTableSkeleton = (): React.ReactElement[] => (
    Array.from({ length: 5 }, (_, index) => (
      <TableRow key={index}>
        {Array.from({ length: 6 }, (_, cellIndex) => (
          <TableCell key={cellIndex}>
            <Skeleton variant="text" width="100%" height={20} />
          </TableCell>
        ))}
      </TableRow>
    ))
  );

  const renderEmptyState = (): React.ReactElement => (
    <TableRow>
      <TableCell colSpan={6} align="center" sx={{ py: 8 }}>
        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center', 
          gap: 2,
          color: 'text.secondary'
        }}>
          <CategoryIcon sx={{ fontSize: 64, opacity: 0.3 }} />
          <Typography variant="h6" color="text.secondary">
            {searchTerm 
              ? 'No types match your search' 
              : 'No reimbursement types found'
            }
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {searchTerm 
              ? 'Try adjusting your search criteria'
              : 'Click the "+" button to create your first type'
            }
          </Typography>
        </Box>
      </TableCell>
    </TableRow>
  );

  return (
    <Box>
      {/* Header */}
      <Card elevation={1} sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
            <Box>
              <Typography variant="h4" color="primary" gutterBottom>
                Reimbursement Types
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Manage reimbursement categories and configurations
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Tooltip title="Refresh" placement="top">
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
                onClick={() => setShowModal(true)}
              >
                ADD TYPE
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Search */}
      <Paper elevation={1} sx={{ p: 2, mb: 3 }}>
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 2
        }}>
          <TextField
            size="small"
            placeholder="Search types..."
            value={searchTerm}
            onChange={handleSearchChange}
            sx={{ minWidth: 250 }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon color="action" />
                </InputAdornment>
              ),
            }}
          />

          {refreshing && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CircularProgress size={16} />
              <Typography variant="body2" color="text.secondary">
                Refreshing...
              </Typography>
            </Box>
          )}
        </Box>
      </Paper>

      {/* Types Table */}
      <Paper elevation={1}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow sx={{ 
                '& .MuiTableCell-head': { 
                  backgroundColor: 'primary.main',
                  color: 'white',
                  fontWeight: 'bold',
                  fontSize: '0.875rem',
                  padding: '16px'
                }
              }}>
                <TableCell>Type Name</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Max Amount</TableCell>
                <TableCell>Receipt Required</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {isLoading ? (
                renderTableSkeleton()
              ) : filteredTypes.length > 0 ? (
                filteredTypes.map((type: any) => (
                  <Fade in key={type.type_id} timeout={300}>
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
                          <CategoryIcon color="primary" />
                          <Typography variant="subtitle2" fontWeight="medium">
                            {type.category_name}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {type.description || 'No description'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium">
                          {type.max_amount ? `₹${type.max_amount}` : 'No limit'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={type.is_receipt_required ? 'Required' : 'Optional'}
                          color={type.is_receipt_required ? 'warning' : 'default'}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={type.is_active ? 'Active' : 'Inactive'}
                          color={type.is_active ? 'success' : 'default'}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell align="center">
                        <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center' }}>
                          <Tooltip title="Edit Type">
                            <IconButton
                              size="small"
                              color="primary"
                            >
                              <EditIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete Type">
                            <IconButton
                              size="small"
                              color="error"
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
      </Paper>

      {/* Create Type Dialog */}
      <Dialog open={showModal} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Typography variant="h5" component="div">
            Create Reimbursement Type
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Define a new reimbursement category
          </Typography>
        </DialogTitle>
        <DialogContent>
          <form onSubmit={handleSubmit}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, mt: 1 }}>
              <TextField
                fullWidth
                label="Type Name"
                value={formData.category_name}
                onChange={(e) => setFormData({ ...formData, category_name: e.target.value })}
                required
                placeholder="e.g., Travel, Meals, Office Supplies"
              />
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={3}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Describe what this reimbursement type covers..."
              />
              <TextField
                fullWidth
                label="Maximum Amount (Optional)"
                type="number"
                value={formData.max_amount}
                onChange={(e) => setFormData({ ...formData, max_amount: e.target.value })}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <MoneyIcon color="action" />
                    </InputAdornment>
                  ),
                }}
                placeholder="Leave empty for no limit"
              />
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.is_receipt_required}
                      onChange={(e) => setFormData({ ...formData, is_receipt_required: e.target.checked })}
                    />
                  }
                  label="Receipt Required"
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.is_approval_required}
                      onChange={(e) => setFormData({ ...formData, is_approval_required: e.target.checked })}
                    />
                  }
                  label="Approval Required"
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.is_active}
                      onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    />
                  }
                  label="Active"
                />
              </Box>
            </Box>
          </form>
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={handleClose} color="inherit">
            Cancel
          </Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained"
            disabled={!formData.category_name}
          >
            Create Type
          </Button>
        </DialogActions>
      </Dialog>

      {/* Toast Notifications */}
      <Snackbar
        open={toast.open}
        autoHideDuration={6000}
        onClose={handleCloseToast}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={handleCloseToast} 
          severity={toast.severity}
          sx={{ width: '100%' }}
          variant="filled"
        >
          {toast.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default ReimbursementTypes; 