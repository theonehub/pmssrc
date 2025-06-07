import React, { useEffect, useState, useCallback } from 'react';
import reimbursementService, { ReimbursementSummary, ReimbursementType, CreateReimbursementRequest } from '../../services/reimbursementService';
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
import { ToastState } from '../../types';

interface ReimbursementFormData {
  reimbursement_type_id: string;
  amount: string;
  description: string;
  file: File | null;
}

const MyReimbursements: React.FC = () => {
  // State management
  const [requests, setRequests] = useState<ReimbursementSummary[]>([]);
  const [filteredRequests, setFilteredRequests] = useState<ReimbursementSummary[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [showEditModal, setShowEditModal] = useState<boolean>(false);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [formData, setFormData] = useState<ReimbursementFormData>({
    reimbursement_type_id: '',
    amount: '',
    description: '',
    file: null
  });
  const [types, setTypes] = useState<ReimbursementType[]>([]);
  const [editingRequest, setEditingRequest] = useState<ReimbursementSummary | null>(null);
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
        reimbursementService.getMyReimbursements(),
        reimbursementService.getReimbursementTypes()
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
        request.amount?.toString().includes(searchTerm) ||
        request.status?.toLowerCase().includes(searchLower) ||
        request.category_name?.toLowerCase().includes(searchLower)
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

  const getTypeName = (request: ReimbursementSummary): string => {
    return request.category_name || 'Unknown';
  };

  const getSelectedType = (): ReimbursementType | null => {
    return types.find(type => type.type_id === formData.reimbursement_type_id) || null;
  };

  const isReceiptRequired = (): boolean => {
    const selectedType = getSelectedType();
    return selectedType?.is_receipt_required || false;
  };

  // Event handlers
  const handleSubmit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();
    
    // Validate receipt requirement
    if (isReceiptRequired() && !formData.file) {
      showToast('Receipt is required for this reimbursement type. Please upload a receipt.', 'error');
      return;
    }
    
    try {
      const requestData: CreateReimbursementRequest = {
        employee_id: 'current_user', // This should come from auth context
        reimbursement_type_id: formData.reimbursement_type_id,
        amount: parseFloat(formData.amount),
        description: formData.description
      };

      if (formData.file) {
        await reimbursementService.createReimbursementRequestWithFile(requestData, formData.file);
      } else {
        await reimbursementService.createReimbursementRequest(requestData);
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
        // Note: File upload during edit is not supported by the backend
        showToast('File upload during edit is not supported. Please create a new request with the file.', 'warning');
        return;
      }
      
      await reimbursementService.updateReimbursementRequest(editingRequest.request_id, {
        amount: parseFloat(formData.amount),
        description: formData.description
      });
      
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
    const file = e.target.files?.[0];
    if (file) {
      // Validate file size (5MB)
      if (file.size > 5 * 1024 * 1024) {
        showToast('File size must be less than 5MB', 'error');
        return;
      }
      
      // Validate file type
      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf'];
      if (!allowedTypes.includes(file.type)) {
        showToast('Only JPG, PNG and PDF files are allowed', 'error');
        return;
      }
      
      setFormData(prev => ({ ...prev, file }));
    }
  };

  const handleClose = (): void => {
    setShowModal(false);
    setFormData({
      reimbursement_type_id: '',
      amount: '',
      description: '',
      file: null
    });
  };

  const handleEditClose = (): void => {
    setShowEditModal(false);
    setEditingRequest(null);
    setFormData({
      reimbursement_type_id: '',
      amount: '',
      description: '',
      file: null
    });
  };

  const handleEdit = (request: ReimbursementSummary): void => {
    setEditingRequest(request);
    // For summary, we don't have reimbursement_type.type_id, so we'll need to find it
    const matchingType = types.find(type => type.category_name === request.category_name);
    setFormData({
      reimbursement_type_id: matchingType?.type_id || '',
      amount: request.amount.toString(),
      description: '', // Summary doesn't have description, so we'll leave it empty
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
      await reimbursementService.deleteReimbursementRequest(deleteConfirmId);
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

  const renderTableSkeleton = (): React.ReactElement[] => (
    Array.from({ length: 5 }, (_, index) => (
      <TableRow key={index}>
        {Array.from({ length: 7 }, (_, cellIndex) => (
          <TableCell key={cellIndex}>
            <Skeleton variant="text" width="100%" height={20} />
          </TableCell>
        ))}
      </TableRow>
    ))
  );

  const renderEmptyState = (): React.ReactElement => (
    <TableRow>
      <TableCell colSpan={7} align="center" sx={{ py: 8 }}>
        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center', 
          gap: 2,
          color: 'text.secondary'
        }}>
          <ReceiptIcon sx={{ fontSize: 64, opacity: 0.3 }} />
          <Typography variant="h6" color="text.secondary">
            {searchTerm || statusFilter !== 'all' 
              ? 'No requests match your filters' 
              : 'No reimbursement requests found'
            }
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {searchTerm || statusFilter !== 'all' 
              ? 'Try adjusting your search criteria'
              : 'Click the "+" button to create your first request'
            }
          </Typography>
        </Box>
      </TableCell>
    </TableRow>
  );

  const canEdit = (status?: string): boolean => {
    return status?.toLowerCase() === 'draft' || status?.toLowerCase() === 'submitted';
  };

  const canDelete = (status?: string): boolean => {
    return status?.toLowerCase() === 'draft';
  };

  return (
    <PageLayout title="My Reimbursements">
      <Box sx={{ p: 3 }}>
        {/* Header with Actions */}
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          mb: 3 
        }}>
          <Typography variant="h4" component="h1" fontWeight="bold">
            My Reimbursements
          </Typography>
          
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
            <Tooltip title="New Request" placement="top">
              <IconButton 
                onClick={() => setShowModal(true)}
                color="primary"
                sx={{ 
                  bgcolor: 'primary.main',
                  color: 'white',
                  '&:hover': { bgcolor: 'primary.dark' }
                }}
              >
                <AddIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {/* Filters */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ 
              display: 'flex', 
              gap: 2, 
              flexWrap: 'wrap',
              alignItems: 'center'
            }}>
              <TextField
                size="small"
                placeholder="Search requests..."
                value={searchTerm}
                onChange={handleSearchChange}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon color="action" />
                    </InputAdornment>
                  ),
                }}
                sx={{ minWidth: 250 }}
              />
              
              <FormControl size="small" sx={{ minWidth: 150 }}>
                <InputLabel>Status</InputLabel>
                <Select
                  value={statusFilter}
                  label="Status"
                  onChange={handleStatusFilterChange}
                >
                  <MenuItem value="all">All Status</MenuItem>
                  <MenuItem value="draft">Draft</MenuItem>
                  <MenuItem value="submitted">Submitted</MenuItem>
                  <MenuItem value="approved">Approved</MenuItem>
                  <MenuItem value="rejected">Rejected</MenuItem>
                </Select>
              </FormControl>

              {refreshing && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CircularProgress size={16} />
                  <Typography variant="body2" color="text.secondary">
                    Refreshing...
                  </Typography>
                </Box>
              )}
            </Box>
          </CardContent>
        </Card>

        {/* Requests Table */}
        <Paper sx={{ borderRadius: 2, overflow: 'hidden' }}>
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
                  <TableCell>Type</TableCell>
                  <TableCell>Amount</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Date</TableCell>
                  <TableCell>Attachment</TableCell>
                  <TableCell align="center">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  renderTableSkeleton()
                ) : filteredRequests.length > 0 ? (
                  filteredRequests.map((request) => (
                    <Fade in key={request.request_id} timeout={300}>
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
                              {getTypeName(request)}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium" color="success.main">
                            {(request.amount)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" color="text.secondary">
                            {request.description || 'No description'}
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
                            {request.created_at ? new Date(request.created_at).toLocaleDateString() : 'N/A'}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          {request.receipt_file_name ? (
                            <Tooltip title={`View Receipt: ${request.receipt_file_name}`}>
                              <Chip
                                label={request.receipt_file_name}
                                size="small"
                                color="success"
                                variant="outlined"
                                icon={<DescriptionIcon fontSize="small" />}
                                onClick={() => reimbursementService.downloadReceipt(request.request_id)}
                                sx={{ 
                                  cursor: 'pointer',
                                  '&:hover': {
                                    backgroundColor: 'success.light',
                                    color: 'white'
                                  }
                                }}
                              />
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
                                  onClick={() => handleDeleteClick(request.request_id)}
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
                      <MenuItem key={type.type_id} value={type.type_id}>
                        {type.category_name}
                        {type.is_receipt_required && (
                          <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                            (Receipt Required)
                          </Typography>
                        )}
                      </MenuItem>
                    ))}
                  </Select>
                  {formData.reimbursement_type_id && isReceiptRequired() && (
                    <Typography variant="caption" color="warning.main" sx={{ mt: 0.5 }}>
                      ⚠️ Receipt is required for this reimbursement type
                    </Typography>
                  )}
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
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Add details about your reimbursement request..."
                />
                {isReceiptRequired() && (
                  <Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Button
                        variant="outlined"
                        component="label"
                        startIcon={<CloudUploadIcon />}
                        sx={{ minWidth: 150 }}
                      >
                        Upload Receipt
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
                      Receipt is required for this reimbursement type. Supported formats: JPG, PNG, PDF (Max 5MB)
                    </Typography>
                  </Box>
                )}
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
              disabled={
                !formData.reimbursement_type_id || 
                !formData.amount || 
                (isReceiptRequired() && !formData.file)
              }
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
                      <MenuItem key={type.type_id} value={type.type_id}>
                        {type.category_name}
                        {type.is_receipt_required && (
                          <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                            (Receipt Required)
                          </Typography>
                        )}
                      </MenuItem>
                    ))}
                  </Select>
                  {formData.reimbursement_type_id && isReceiptRequired() && (
                    <Typography variant="caption" color="warning.main" sx={{ mt: 0.5 }}>
                      ⚠️ Receipt is required for this reimbursement type
                    </Typography>
                  )}
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
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Add details about your reimbursement request..."
                />
                {isReceiptRequired() && (
                  <Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Button
                        variant="outlined"
                        component="label"
                        startIcon={<CloudUploadIcon />}
                        sx={{ minWidth: 150 }}
                      >
                        Upload New Receipt
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
                      Note: File upload during edit is not supported. Please create a new request to upload receipts.
                    </Typography>
                  </Box>
                )}
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
            variant="filled"
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