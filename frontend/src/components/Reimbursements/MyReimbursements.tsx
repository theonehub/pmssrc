import React, { useState } from 'react';
import { useReimbursementsQuery } from '../../shared/hooks/useReimbursements';
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
  Search as SearchIcon,
  Refresh as RefreshIcon,
  Receipt as ReceiptIcon,
  AttachMoney as MoneyIcon,
  Description as DescriptionIcon,
  CloudUpload as CloudUploadIcon
} from '@mui/icons-material';
import PageLayout from '../../layout/PageLayout';
import { ToastState } from '../../shared/types';
import { reimbursementApi, ReimbursementRequest } from '../../shared/api/reimbursementApi';

interface ReimbursementFormData {
  reimbursement_type_id: string;
  amount: string;
  description: string;
  file: File | null;
}

const MyReimbursements: React.FC = () => {
  // State management
  const [filteredRequests, setFilteredRequests] = useState<any[]>([]);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [formData, setFormData] = useState<ReimbursementFormData>({
    reimbursement_type_id: '',
    amount: '',
    description: '',
    file: null
  });
  const [toast, setToast] = useState<ToastState>({
    open: false,
    message: '',
    severity: 'success'
  });

  // Use React Query for reimbursements
  const { data: reimbursementsData, isLoading, error: reimbursementsError, refetch } = useReimbursementsQuery();
  const requests = reimbursementsData?.data?.requests || reimbursementsData?.requests || [];
  const types = reimbursementsData?.data?.types || reimbursementsData?.types || [];

  // Filter requests based on search term and status
  React.useEffect(() => {
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

  React.useEffect(() => {
    if (reimbursementsError) {
      showToast(reimbursementsError.message || 'Failed to fetch requests.', 'error');
    }
    // eslint-disable-next-line
  }, [reimbursementsError]);

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

  const getTypeName = (request: any): string => {
    return request.category_name || 'Unknown';
  };

  const getSelectedType = (): any | null => {
    return types.find((type: any) => type.type_id === formData.reimbursement_type_id) || null;
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
      const requestData: Omit<ReimbursementRequest, 'request_id' | 'created_at' | 'updated_at'> = {
        reimbursement_type_id: formData.reimbursement_type_id,
        amount: parseFloat(formData.amount),
        description: formData.description
      };

      if (formData.file) {
        await reimbursementApi.createRequestWithFile(requestData, formData.file);
      } else {
        await reimbursementApi.createRequest(requestData);
      }
      
      showToast('Reimbursement request submitted successfully!', 'success');
      handleClose();
      refetch();
    } catch (err: any) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Error submitting request:', err);
      }
      const errorMessage = err.response?.data?.detail || 'Failed to submit request.';
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

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setSearchTerm(event.target.value);
  };

  const handleStatusFilterChange = (event: SelectChangeEvent<string>): void => {
    setStatusFilter(event.target.value);
  };

  const handleRefresh = (): void => {
    setRefreshing(true);
    refetch().finally(() => setRefreshing(false));
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
                {isLoading ? (
                  renderTableSkeleton()
                ) : filteredRequests.length > 0 ? (
                  filteredRequests.map((request: any) => (
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
                            ₹{request.amount}
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
                                onClick={() => reimbursementApi.downloadReceipt(request.request_id)}
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
                            <Tooltip title="View Details">
                              <IconButton
                                size="small"
                                color="primary"
                              >
                                <ReceiptIcon fontSize="small" />
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
                    {types.map((type: any) => (
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
};

export default MyReimbursements; 