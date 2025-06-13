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
  SelectChangeEvent,
  AlertColor
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
  Receipt as ReceiptIcon,
  Description as DescriptionIcon,
  CloudUpload as CloudUploadIcon,
  Visibility as VisibilityIcon,
  Edit as EditIcon
} from '@mui/icons-material';
import { reimbursementApi, ReimbursementRequest } from '../../shared/api/reimbursementApi';

// Define interfaces
interface ReimbursementFormData {
  reimbursement_type_id: string;
  amount: string;
  description: string;
  file: File | null;
}

interface ToastState {
  open: boolean;
  message: string;
  severity: AlertColor;
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
    setToast((prev: ToastState) => ({ ...prev, open: false }));
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
    <Box>
      {/* Header with Actions */}
      <Card elevation={1} sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Manage your reimbursement requests
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
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
                NEW REQUEST
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
            <TextField
              size="small"
              placeholder="Search requests..."
              value={searchTerm}
              onChange={handleSearchChange}
              sx={{ minWidth: 300, flexGrow: 1, maxWidth: 500 }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon color="action" />
                  </InputAdornment>
                ),
              }}
            />
            
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
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
                              onClick={() => {/* Add view details logic */}}
                            >
                              <VisibilityIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          {request.status === 'draft' && (
                            <Tooltip title="Edit">
                              <IconButton
                                size="small"
                                color="primary"
                                onClick={() => {/* Add edit logic */}}
                              >
                                <EditIcon fontSize="small" />
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

      {/* New Request Modal */}
      <Dialog 
        open={showModal} 
        onClose={handleClose}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          New Reimbursement Request
        </DialogTitle>
        <form onSubmit={handleSubmit}>
          <DialogContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, mt: 1 }}>
              <FormControl fullWidth required>
                <InputLabel>Reimbursement Type</InputLabel>
                <Select
                  value={formData.reimbursement_type_id}
                  label="Reimbursement Type"
                  onChange={(e) => setFormData(prev => ({ ...prev, reimbursement_type_id: e.target.value }))}
                >
                  {types.map((type: any) => (
                    <MenuItem key={type.type_id} value={type.type_id}>
                      {type.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <TextField
                fullWidth
                required
                label="Amount"
                type="number"
                value={formData.amount}
                onChange={(e) => setFormData(prev => ({ ...prev, amount: e.target.value }))}
                InputProps={{
                  startAdornment: <InputAdornment position="start">₹</InputAdornment>,
                }}
              />

              <TextField
                fullWidth
                multiline
                rows={3}
                label="Description"
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Describe your reimbursement request..."
              />

              {isReceiptRequired() && (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Receipt Upload {isReceiptRequired() && <span style={{ color: 'red' }}>*</span>}
                  </Typography>
                  <input
                    type="file"
                    accept="image/*,.pdf"
                    onChange={handleFileChange}
                    style={{ display: 'none' }}
                    id="receipt-upload"
                  />
                  <label htmlFor="receipt-upload">
                    <Button
                      variant="outlined"
                      component="span"
                      fullWidth
                      startIcon={<CloudUploadIcon />}
                      sx={{ py: 2 }}
                    >
                      {formData.file ? formData.file.name : 'Choose Receipt File'}
                    </Button>
                  </label>
                  {isReceiptRequired() && (
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                      Receipt is required for this reimbursement type
                    </Typography>
                  )}
                </Box>
              )}
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClose}>
              Cancel
            </Button>
            <Button 
              type="submit" 
              variant="contained"
              disabled={!formData.reimbursement_type_id || !formData.amount || (isReceiptRequired() && !formData.file)}
            >
              Submit Request
            </Button>
          </DialogActions>
        </form>
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

export default MyReimbursements; 