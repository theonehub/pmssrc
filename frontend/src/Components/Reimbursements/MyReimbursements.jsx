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
  Grid,
  InputAdornment,
  Skeleton,
  Fade,
  Chip,
  Snackbar,
  FormControl,
  InputLabel,
  Avatar
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Upload as UploadIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
  Receipt as ReceiptIcon,
  AttachMoney as MoneyIcon,
  Description as DescriptionIcon,
  CloudUpload as CloudUploadIcon
} from '@mui/icons-material';
import PageLayout from '../../layout/PageLayout';

function MyReimbursements() {
  // State management
  const [requests, setRequests] = useState([]);
  const [filteredRequests, setFilteredRequests] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [formData, setFormData] = useState({
    reimbursement_type_id: '',
    amount: '',
    note: '',
    file: null
  });
  const [types, setTypes] = useState([]);
  const [error, setError] = useState(null);
  const [editingRequest, setEditingRequest] = useState(null);
  const [deleteConfirmId, setDeleteConfirmId] = useState(null);
  const [toast, setToast] = useState({
    open: false,
    message: '',
    severity: 'success'
  });

  // Memoized fetch function
  const fetchData = useCallback(async (showRefreshLoader = false) => {
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
    } catch (err) {
      console.error('Error fetching requests:', err);
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
  const showToast = (message, severity = 'success') => {
    setToast({ open: true, message, severity });
  };

  const handleCloseToast = () => {
    setToast(prev => ({ ...prev, open: false }));
  };

  const getStatusColor = (status) => {
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

  const getTypeName = (typeId) => {
    const type = types.find(t => t.id === typeId);
    return type?.name || 'Unknown';
  };

  const formatAmount = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  // Event handlers
  const handleSubmit = async (e) => {
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
    } catch (err) {
      console.error('Error submitting request:', err);
      const errorMessage = err.response?.data?.detail || 'Failed to submit request.';
      showToast(errorMessage, 'error');
    }
  };

  const handleEditSubmit = async (e) => {
    e.preventDefault();
    
    try {
      if (formData.file) {
        await api.upload(
          `/reimbursements/${editingRequest.id}/with-file`,
          formData.file,
          {
            reimbursement_type_id: formData.reimbursement_type_id,
            amount: formData.amount,
            note: formData.note
          },
          'put'
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
    } catch (err) {
      console.error('Error updating request:', err);
      const errorMessage = err.response?.data?.detail || 'Failed to update request.';
      showToast(errorMessage, 'error');
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        showToast('File size should not exceed 5MB', 'error');
        return;
      }
      const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf'];
      if (!allowedTypes.includes(file.type)) {
        showToast('Only JPEG, PNG and PDF files are allowed', 'error');
        return;
      }
      setFormData({ ...formData, file: file });
    }
  };

  const handleClose = () => {
    setShowModal(false);
    setFormData({
      reimbursement_type_id: '',
      amount: '',
      note: '',
      file: null
    });
    setError(null);
  };

  const handleEditClose = () => {
    setShowEditModal(false);
    setEditingRequest(null);
    setFormData({
      reimbursement_type_id: '',
      amount: '',
      note: '',
      file: null
    });
    setError(null);
  };

  const handleEdit = (request) => {
    setEditingRequest(request);
    setFormData({
      reimbursement_type_id: request.reimbursement_type_id,
      amount: request.amount,
      note: request.note,
      file: null
    });
    setShowEditModal(true);
  };

  const handleDeleteClick = (requestId) => {
    setDeleteConfirmId(requestId);
  };

  const handleDeleteConfirm = async () => {
    if (!deleteConfirmId) return;

    try {
      await api.delete(`/reimbursements/${deleteConfirmId}`);
      showToast('Reimbursement request deleted successfully!', 'success');
      fetchData();
    } catch (err) {
      console.error('Error deleting request:', err);
      const errorMessage = err.response?.data?.detail || 'Failed to delete request.';
      showToast(errorMessage, 'error');
    } finally {
      setDeleteConfirmId(null);
    }
  };

  const handleDeleteCancel = () => {
    setDeleteConfirmId(null);
  };

  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
  };

  const handleStatusFilterChange = (event) => {
    setStatusFilter(event.target.value);
  };

  const handleRefresh = () => {
    fetchData(true);
  };

  // Render helpers
  const renderTableSkeleton = () => (
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

  const renderEmptyState = () => (
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

  const canEdit = (status) => {
    return status?.toLowerCase() === 'pending';
  };

  const canDelete = (status) => {
    return status?.toLowerCase() === 'pending';
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
                  My Reimbursements
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Submit and track your reimbursement requests
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
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
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Search and Filters */}
        <Paper elevation={1} sx={{ p: 2, mb: 3 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
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
            </Grid>
            <Grid item xs={12} md={3}>
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
            </Grid>
            <Grid item xs={12} md={3}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  {loading ? 'Loading...' : `${filteredRequests.length} request${filteredRequests.length !== 1 ? 's' : ''}`}
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
                            {!canEdit(request.status) && !canDelete(request.status) && (
                              <Typography variant="caption" color="text.secondary">
                                No actions
                              </Typography>
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
              <Grid container spacing={3} sx={{ mt: 1 }}>
                <Grid item xs={12}>
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
                </Grid>
                <Grid item xs={12}>
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
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Note/Description"
                    multiline
                    rows={3}
                    value={formData.note}
                    onChange={(e) => setFormData({ ...formData, note: e.target.value })}
                    placeholder="Add details about your reimbursement request..."
                  />
                </Grid>
                <Grid item xs={12}>
                  <Box sx={{ 
                    border: '2px dashed',
                    borderColor: 'divider',
                    borderRadius: 1,
                    p: 2,
                    textAlign: 'center',
                    '&:hover': {
                      borderColor: 'primary.main',
                      bgcolor: 'action.hover'
                    }
                  }}>
                    <input
                      type="file"
                      accept=".pdf,.jpg,.jpeg,.png"
                      onChange={handleFileChange}
                      style={{ display: 'none' }}
                      id="file-upload"
                    />
                    <label htmlFor="file-upload">
                      <Box sx={{ cursor: 'pointer' }}>
                        <CloudUploadIcon sx={{ fontSize: 40, color: 'text.secondary', mb: 1 }} />
                        <Typography variant="body2" color="text.secondary">
                          Click to upload receipt/bill (PDF, JPG, PNG - Max 5MB)
                        </Typography>
                        {formData.file && (
                          <Typography variant="body2" color="primary" sx={{ mt: 1 }}>
                            Selected: {formData.file.name}
                          </Typography>
                        )}
                      </Box>
                    </label>
                  </Box>
                </Grid>
                <Grid item xs={12}>
                  <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                    <Button onClick={handleClose} size="large">
                      Cancel
                    </Button>
                    <Button type="submit" variant="contained" size="large">
                      Submit Request
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </form>
          </DialogContent>
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
              <Grid container spacing={3} sx={{ mt: 1 }}>
                <Grid item xs={12}>
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
                </Grid>
                <Grid item xs={12}>
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
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Note/Description"
                    multiline
                    rows={3}
                    value={formData.note}
                    onChange={(e) => setFormData({ ...formData, note: e.target.value })}
                    placeholder="Add details about your reimbursement request..."
                  />
                </Grid>
                <Grid item xs={12}>
                  <Box sx={{ 
                    border: '2px dashed',
                    borderColor: 'divider',
                    borderRadius: 1,
                    p: 2,
                    textAlign: 'center',
                    '&:hover': {
                      borderColor: 'primary.main',
                      bgcolor: 'action.hover'
                    }
                  }}>
                    <input
                      type="file"
                      accept=".pdf,.jpg,.jpeg,.png"
                      onChange={handleFileChange}
                      style={{ display: 'none' }}
                      id="edit-file-upload"
                    />
                    <label htmlFor="edit-file-upload">
                      <Box sx={{ cursor: 'pointer' }}>
                        <CloudUploadIcon sx={{ fontSize: 40, color: 'text.secondary', mb: 1 }} />
                        <Typography variant="body2" color="text.secondary">
                          Click to upload new receipt/bill (PDF, JPG, PNG - Max 5MB)
                        </Typography>
                        {formData.file && (
                          <Typography variant="body2" color="primary" sx={{ mt: 1 }}>
                            Selected: {formData.file.name}
                          </Typography>
                        )}
                      </Box>
                    </label>
                  </Box>
                </Grid>
                <Grid item xs={12}>
                  <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                    <Button onClick={handleEditClose} size="large">
                      Cancel
                    </Button>
                    <Button type="submit" variant="contained" size="large">
                      Update Request
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </form>
          </DialogContent>
        </Dialog>

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
              Are you sure you want to delete this reimbursement request? This action cannot be undone.
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
    </PageLayout>
  );
}

export default MyReimbursements;