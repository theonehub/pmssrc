import React, { useEffect, useState, useCallback } from 'react';
import api from '../../utils/apiUtils';
import {
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
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
  FormControl,
  InputLabel,
  Avatar,
  SelectChangeEvent
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
  Receipt as ReceiptIcon,
  AttachMoney as MoneyIcon,
  Description as DescriptionIcon,
  CloudUpload as CloudUploadIcon
} from '@mui/icons-material';
import PageLayout from '../../layout/PageLayout';
import { 
  MyReimbursementRequest, 
  ReimbursementType, 
  ReimbursementFormData, 
  ToastState
} from '../../types';

const MyReimbursements: React.FC = () => {
  // State management
  const [requests, setRequests] = useState<MyReimbursementRequest[]>([]);
  const [filteredRequests, setFilteredRequests] = useState<MyReimbursementRequest[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [showEditModal, setShowEditModal] = useState<boolean>(false);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [formData, setFormData] = useState<ReimbursementFormData>({
    reimbursement_type_id: '',
    amount: '',
    note: '',
    file: null
  });
  const [types, setTypes] = useState<ReimbursementType[]>([]);
  const [editingRequest, setEditingRequest] = useState<MyReimbursementRequest | null>(null);
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);
  const [toast, setToast] = useState<ToastState>({
    open: false,
    message: '',
    severity: 'success'
  });

  // Memoized fetch function
  const fetchData = useCallback(async (showRefreshLoader: boolean = false): Promise<void> => {
    if (showRefreshLoader) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    try {
      const [reqRes, typesRes] = await Promise.all([
        api.get('/reimbursements/my-requests'),
        api.get('/reimbursement-types/')
      ]);
      setRequests(reqRes.data || []);
      setTypes(typesRes.data || []);
    } catch (err: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error fetching requests:', err);
      }
      const errorMessage = err.response?.data?.detail || 'Failed to fetch requests.';
      showToast(errorMessage, 'error');
      setRequests([]);
      setTypes([]);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  // Filter requests based on search term and status
  useEffect(() => {
    let filtered = [...requests];

    // Apply search filter
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      filtered = filtered.filter(request =>
        request.note?.toLowerCase().includes(searchLower) ||
        request.amount?.toString().includes(searchTerm) ||
        request.status?.toLowerCase().includes(searchLower) ||
        types.find(type => type.id === request.reimbursement_type_id)?.name?.toLowerCase().includes(searchLower)
      );
    }

    // Apply status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(request => request.status?.toLowerCase() === statusFilter);
    }

    setFilteredRequests(filtered);
  }, [requests, searchTerm, statusFilter, types]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Helper functions
  const showToast = (message: string, severity: ToastState['severity'] = 'success'): void => {
    setToast({ open: true, message, severity });
  };

  const handleCloseToast = (): void => {
    setToast(prev => ({ ...prev, open: false }));
  };

  const getStatusColor = (status?: string): 'success' | 'warning' | 'error' | 'default' => {
    switch (status?.toLowerCase()) {
      case 'approved':
        return 'success';
      case 'pending':
        return 'warning';
      case 'rejected':
        return 'error';
      default:
        return 'default';
    }
  };

  const getTypeName = (typeId: string): string => {
    const type = types.find(t => t.id === typeId);
    return type?.name || 'Unknown';
  };

  const formatAmount = (amount: number): string => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount);
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  // Event handlers
  const handleSubmit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();
    
    try {
      if (formData.file) {
        await api.upload(
          '/reimbursements/with-file',
          formData.file,
          {
            reimbursement_type_id: formData.reimbursement_type_id,
            amount: formData.amount,
            note: formData.note
          }
        );
      } else {
        await api.post('/reimbursements', {
          reimbursement_type_id: formData.reimbursement_type_id,
          amount: parseFloat(formData.amount),
          note: formData.note
        });
      }
      
      showToast('Reimbursement request submitted successfully!', 'success');
      handleClose();
      fetchData();
    } catch (err: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error submitting request:', err);
      }
      const errorMessage = err.response?.data?.detail || 'Failed to submit request.';
      showToast(errorMessage, 'error');
    }
  };

  const handleEditSubmit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();
    
    if (!editingRequest) return;

    try {
      if (formData.file) {
        await api.upload(
          `/reimbursements/${editingRequest.id}/with-file`,
          formData.file,
          {
            reimbursement_type_id: formData.reimbursement_type_id,
            amount: formData.amount,
            note: formData.note
          }
        );
      } else {
        await api.put(`/reimbursements/${editingRequest.id}`, {
          reimbursement_type_id: formData.reimbursement_type_id,
          amount: parseFloat(formData.amount),
          note: formData.note
        });
      }
      
      showToast('Reimbursement request updated successfully!', 'success');
      handleEditClose();
      fetchData();
    } catch (err: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error updating request:', err);
      }
      const errorMessage = err.response?.data?.detail || 'Failed to update request.';
      showToast(errorMessage, 'error');
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    const file = e.target.files?.[0] || null;
    
    if (file) {
      // Check file size (5MB limit)
      const maxSize = 5 * 1024 * 1024; // 5MB in bytes
      if (file.size > maxSize) {
        showToast('File size must be less than 5MB', 'error');
        return;
      }
      
      // Check file type
      const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf'];
      if (!allowedTypes.includes(file.type)) {
        showToast('Only JPEG, PNG, and PDF files are allowed', 'error');
        return;
      }
    }
    
    setFormData({ ...formData, file });
  };

  const handleClose = (): void => {
    setShowModal(false);
    setFormData({
      reimbursement_type_id: '',
      amount: '',
      note: '',
      file: null
    });
  };

  const handleEditClose = (): void => {
    setShowEditModal(false);
    setEditingRequest(null);
    setFormData({
      reimbursement_type_id: '',
      amount: '',
      note: '',
      file: null
    });
  };

  const handleEdit = (request: MyReimbursementRequest): void => {
    setEditingRequest(request);
    setFormData({
      reimbursement_type_id: request.reimbursement_type_id,
      amount: request.amount.toString(),
      note: request.note || '',
      file: null
    });
    setShowEditModal(true);
  };

  const handleDeleteClick = (requestId: string): void => {
    setDeleteConfirmId(requestId);
  };

  const handleDeleteConfirm = async (): Promise<void> => {
    if (!deleteConfirmId) return;

    try {
      await api.delete(`/reimbursements/${deleteConfirmId}`);
      showToast('Reimbursement request deleted successfully!', 'success');
      setDeleteConfirmId(null);
      fetchData();
    } catch (err: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error deleting request:', err);
      }
      const errorMessage = err.response?.data?.detail || 'Failed to delete request.';
      showToast(errorMessage, 'error');
    }
  };

  const handleDeleteCancel = (): void => {
    setDeleteConfirmId(null);
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setSearchTerm(event.target.value);
  };

  const handleStatusFilterChange = (event: SelectChangeEvent<string>): void => {
    setStatusFilter(event.target.value);
  };

  const handleRefresh = (): void => {
    fetchData(true);
  };

  // Render helpers
  const renderTableSkeleton = (): React.ReactElement[] => (
    Array.from({ length: 5 }).map((_, index) => (
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

  const renderEmptyState = (): React.ReactElement => (
    <TableRow>
      <TableCell colSpan={7} align="center" sx={{ py: 6 }}>
        <Box sx={{ textAlign: 'center' }}>
          <ReceiptIcon 
            sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} 
          />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            {searchTerm || statusFilter !== 'all' ? 'No requests found' : 'No reimbursement requests yet'}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {searchTerm || statusFilter !== 'all'
              ? 'Try adjusting your search or filter criteria'
              : 'Get started by submitting your first reimbursement request'
            }
          </Typography>
          {!searchTerm && statusFilter === 'all' && (
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setShowModal(true)}
            >
              Submit Request
            </Button>
          )}
        </Box>
      </TableCell>
    </TableRow>
  );

  const canEdit = (status?: string): boolean => {
    return status?.toLowerCase() === 'pending';
  };

  const canDelete = (status?: string): boolean => {
    return status?.toLowerCase() === 'pending';
  };

  return (
    <PageLayout title="My Reimbursements">
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
                  My Reimbursements
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Submit and track your reimbursement requests
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
                  onClick={() => setShowModal(true)}
                  size="large"
                >
                  Submit Request
                </Button>
              </Box>
            </Box>
          </CardContent>
        </Card>

        {/* Search and Filters */}
        <Paper elevation={1} sx={{ p: 2, mb: 3 }}>
          <Box sx={{ 
            display: 'grid', 
            gridTemplateColumns: { xs: '1fr', md: '1fr 200px 200px' }, 
            gap: 2, 
            alignItems: 'center' 
          }}>
            <TextField
              fullWidth
              label="Search requests"
              variant="outlined"
              value={searchTerm}
              onChange={handleSearchChange}
              placeholder="Search by note, amount, or type..."
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon color="action" />
                  </InputAdornment>
                ),
              }}
            />
            <FormControl fullWidth>
              <InputLabel>Status Filter</InputLabel>
              <Select
                value={statusFilter}
                label="Status Filter"
                onChange={handleStatusFilterChange}
              >
                <MenuItem value="all">All Status</MenuItem>
                <MenuItem value="pending">Pending</MenuItem>
                <MenuItem value="approved">Approved</MenuItem>
                <MenuItem value="rejected">Rejected</MenuItem>
              </Select>
            </FormControl>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="body2" color="text.secondary">
                {loading ? 'Loading...' : `${filteredRequests.length} request${filteredRequests.length !== 1 ? 's' : ''}`}
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
                  <TableCell>Type</TableCell>
                  <TableCell>Amount</TableCell>
                  <TableCell>Note</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Submitted Date</TableCell>
                  <TableCell>Attachment</TableCell>
                  <TableCell align="center">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  renderTableSkeleton()
                ) : filteredRequests.length > 0 ? (
                  filteredRequests.map((request) => (
                    <Fade in key={request.id} timeout={300}>
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
                            <Avatar 
                              sx={{ 
                                width: 32, 
                                height: 32, 
                                bgcolor: 'primary.main',
                                fontSize: '0.75rem'
                              }}
                            >
                              <ReceiptIcon fontSize="small" />
                            </Avatar>
                            <Typography variant="subtitle2" fontWeight="medium">
                              {getTypeName(request.reimbursement_type_id)}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium" color="success.main">
                            {formatAmount(request.amount)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" color="text.secondary">
                            {request.note || 'No description'}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={request.status}
                            color={getStatusColor(request.status)}
                            size="small"
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {formatDate(request.created_at)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          {request.file_path ? (
                            <Tooltip title="View Attachment">
                              <IconButton
                                size="small"
                                color="primary"
                                onClick={() => window.open(request.file_path, '_blank')}
                              >
                                <DescriptionIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          ) : (
                            <Typography variant="caption" color="text.secondary">
                              No file
                            </Typography>
                          )}
                        </TableCell>
                        <TableCell align="center">
                          <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center' }}>
                            {canEdit(request.status) && (
                              <Tooltip title="Edit Request">
                                <IconButton
                                  size="small"
                                  color="primary"
                                  onClick={() => handleEdit(request)}
                                >
                                  <EditIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            )}
                            {canDelete(request.status) && (
                              <Tooltip title="Delete Request">
                                <IconButton
                                  size="small"
                                  color="error"
                                  onClick={() => handleDeleteClick(request.id)}
                                >
                                  <DeleteIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            )}
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

        {/* Submit Request Dialog */}
        <Dialog open={showModal} onClose={handleClose} maxWidth="sm" fullWidth>
          <DialogTitle>
            <Typography variant="h5" component="div">
              Submit Reimbursement Request
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Fill in the details for your reimbursement request
            </Typography>
          </DialogTitle>
          <DialogContent>
            <form onSubmit={handleSubmit}>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, mt: 1 }}>
                <FormControl fullWidth required>
                  <InputLabel>Reimbursement Type</InputLabel>
                  <Select
                    value={formData.reimbursement_type_id}
                    label="Reimbursement Type"
                    onChange={(e) => setFormData({ ...formData, reimbursement_type_id: e.target.value })}
                  >
                    {types.map((type) => (
                      <MenuItem key={type.id} value={type.id}>
                        {type.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
                <TextField
                  fullWidth
                  label="Amount"
                  type="number"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                  required
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <MoneyIcon color="action" />
                      </InputAdornment>
                    ),
                  }}
                />
                <TextField
                  fullWidth
                  label="Note/Description"
                  multiline
                  rows={3}
                  value={formData.note}
                  onChange={(e) => setFormData({ ...formData, note: e.target.value })}
                  placeholder="Add details about your reimbursement request..."
                />
                <Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Button
                      variant="outlined"
                      component="label"
                      startIcon={<CloudUploadIcon />}
                      sx={{ minWidth: 150 }}
                    >
                      Upload File
                      <input
                        type="file"
                        hidden
                        accept=".jpg,.jpeg,.png,.pdf"
                        onChange={handleFileChange}
                      />
                    </Button>
                    {formData.file && (
                      <Typography variant="body2" color="text.secondary">
                        {formData.file.name}
                      </Typography>
                    )}
                  </Box>
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                    Supported formats: JPG, PNG, PDF (Max 5MB)
                  </Typography>
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
              disabled={!formData.reimbursement_type_id || !formData.amount}
            >
              Submit Request
            </Button>
          </DialogActions>
        </Dialog>

        {/* Edit Request Dialog */}
        <Dialog open={showEditModal} onClose={handleEditClose} maxWidth="sm" fullWidth>
          <DialogTitle>
            <Typography variant="h5" component="div">
              Edit Reimbursement Request
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Update your reimbursement request details
            </Typography>
          </DialogTitle>
          <DialogContent>
            <form onSubmit={handleEditSubmit}>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, mt: 1 }}>
                <FormControl fullWidth required>
                  <InputLabel>Reimbursement Type</InputLabel>
                  <Select
                    value={formData.reimbursement_type_id}
                    label="Reimbursement Type"
                    onChange={(e) => setFormData({ ...formData, reimbursement_type_id: e.target.value })}
                  >
                    {types.map((type) => (
                      <MenuItem key={type.id} value={type.id}>
                        {type.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
                <TextField
                  fullWidth
                  label="Amount"
                  type="number"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                  required
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <MoneyIcon color="action" />
                      </InputAdornment>
                    ),
                  }}
                />
                <TextField
                  fullWidth
                  label="Note/Description"
                  multiline
                  rows={3}
                  value={formData.note}
                  onChange={(e) => setFormData({ ...formData, note: e.target.value })}
                  placeholder="Add details about your reimbursement request..."
                />
                <Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Button
                      variant="outlined"
                      component="label"
                      startIcon={<CloudUploadIcon />}
                      sx={{ minWidth: 150 }}
                    >
                      Upload New File
                      <input
                        type="file"
                        hidden
                        accept=".jpg,.jpeg,.png,.pdf"
                        onChange={handleFileChange}
                      />
                    </Button>
                    {formData.file && (
                      <Typography variant="body2" color="text.secondary">
                        {formData.file.name}
                      </Typography>
                    )}
                  </Box>
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                    Supported formats: JPG, PNG, PDF (Max 5MB)
                  </Typography>
                </Box>
              </Box>
            </form>
          </DialogContent>
          <DialogActions sx={{ p: 3 }}>
            <Button onClick={handleEditClose} color="inherit">
              Cancel
            </Button>
            <Button 
              onClick={handleEditSubmit} 
              variant="contained"
              disabled={!formData.reimbursement_type_id || !formData.amount}
            >
              Update Request
            </Button>
          </DialogActions>
        </Dialog>

        {/* Delete Confirmation Dialog */}
        <Dialog open={!!deleteConfirmId} onClose={handleDeleteCancel}>
          <DialogTitle>Confirm Delete</DialogTitle>
          <DialogContent>
            <Typography>
              Are you sure you want to delete this reimbursement request? This action cannot be undone.
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleDeleteCancel} color="inherit">
              Cancel
            </Button>
            <Button onClick={handleDeleteConfirm} color="error" variant="contained">
              Delete
            </Button>
          </DialogActions>
        </Dialog>

        {/* Toast Notification */}
        <Snackbar
          open={toast.open}
          autoHideDuration={6000}
          onClose={handleCloseToast}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert 
            onClose={handleCloseToast} 
            severity={toast.severity}
            sx={{ width: '100%' }}
          >
            {toast.message}
          </Alert>
        </Snackbar>
      </Box>
    </PageLayout>
  );
};

export default MyReimbursements; 