import React, { useState, useEffect } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
  Button,
  Alert,
  Grid,
  CircularProgress,
  Tooltip,
  Divider,
  Link
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Download as DownloadIcon,
  Visibility as VisibilityIcon
} from '@mui/icons-material';
import axios from '../../utils/axios';
import PageLayout from '../../layout/PageLayout';

function ReimbursementApprovals() {
  const [pendingRequests, setPendingRequests] = useState([]);
  const [approvedRequests, setApprovedRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [comment, setComment] = useState('');
  const [action, setAction] = useState('');
  const [viewFileUrl, setViewFileUrl] = useState('');
  const [fileDialogOpen, setFileDialogOpen] = useState(false);

  useEffect(() => {
    fetchRequests();
  }, []);

  const fetchRequests = () => {
    setLoading(true);
    Promise.all([
      axios.get('/reimbursements/pending'),
      axios.get('/reimbursements/approved')
    ])
      .then(([pendingRes, approvedRes]) => {
        setPendingRequests(pendingRes.data || []);
        setApprovedRequests(approvedRes.data || []);
      })
      .catch(err => {
        console.error('Error fetching reimbursement requests:', err);
        setError('Failed to load reimbursement requests.');
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const handleAction = (request, actionType) => {
    setSelectedRequest(request);
    setAction(actionType);
    setComment('');
    setDialogOpen(true);
  };

  const handleConfirm = () => {
    axios.put(`/reimbursements/${selectedRequest.id}/status`, {
      status: action.toUpperCase(),
      comments: comment
    })
      .then(() => {
        setDialogOpen(false);
        fetchRequests();
      })
      .catch(err => {
        console.error('Error updating reimbursement status:', err);
        setError(err.response?.data?.detail || 'Failed to update reimbursement status.');
      });
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'approved':
        return 'success.main';
      case 'pending':
        return 'warning.main';
      case 'rejected':
        return 'error.main';
      default:
        return 'grey.500';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const handleViewFile = (fileUrl) => {
    if (!fileUrl) return;
    
    // If file URL is relative, convert to absolute
    const fullUrl = fileUrl.startsWith('http') 
      ? fileUrl 
      : `${window.location.origin}${fileUrl}`;
      
    setViewFileUrl(fullUrl);
    setFileDialogOpen(true);
  };

  const handleDownloadFile = (fileUrl, fileName = 'reimbursement-file') => {
    if (!fileUrl) return;
    
    // If file URL is relative, convert to absolute
    const fullUrl = fileUrl.startsWith('http') 
      ? fileUrl 
      : `${window.location.origin}${fileUrl}`;
    
    // Create an anchor element and set its properties
    const a = document.createElement('a');
    a.href = fullUrl;
    a.download = fileName; // Set the file name for download
    a.style.display = 'none';
    
    // Append to the body and trigger the download
    document.body.appendChild(a);
    a.click();
    
    // Clean up
    document.body.removeChild(a);
  };

  const renderRequestsTable = (requests, showActions = false) => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow sx={{
            '& .MuiTableCell-head': {
              backgroundColor: 'primary.main',
              color: 'white',
              fontWeight: 'bold',
              fontSize: '0.875rem',
              padding: '12px 16px'
            }
          }}>
            <TableCell>Employee ID</TableCell>
            <TableCell>Employee Name</TableCell>
            <TableCell>Type</TableCell>
            <TableCell>Amount</TableCell>
            <TableCell>Date</TableCell>
            <TableCell>Description</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>File</TableCell>
            {showActions && <TableCell>Actions</TableCell>}
          </TableRow>
        </TableHead>
        <TableBody>
          {loading ? (
            <TableRow>
              <TableCell colSpan={showActions ? 9 : 8} align="center">
                <CircularProgress color="primary" />
              </TableCell>
            </TableRow>
          ) : requests.length > 0 ? (
            requests.map((req) => (
              <TableRow
                key={req.id}
                sx={{
                  '&:hover': {
                    backgroundColor: 'action.hover',
                    cursor: 'pointer'
                  }
                }}
              >
                <TableCell>{req.emp_id}</TableCell>
                <TableCell>{req.employee_name}</TableCell>
                <TableCell>{req.type_name}</TableCell>
                <TableCell>₹{parseFloat(req.amount).toLocaleString('en-IN')}</TableCell>
                <TableCell>{formatDate(req.created_at)}</TableCell>
                <TableCell>{req.note}</TableCell>
                <TableCell>
                  <Box
                    component="span"
                    sx={{
                      display: 'inline-block',
                      padding: '4px 8px',
                      borderRadius: '4px',
                      backgroundColor: getStatusColor(req.status),
                      color: 'white',
                      fontSize: '0.75rem',
                      fontWeight: 'bold'
                    }}
                  >
                    {req.status}
                  </Box>
                </TableCell>
                <TableCell>
                  {req.file_url ? (
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Tooltip title="View File"
                        placement="top"
                        arrow
                        >
                        <IconButton
                          color="primary"
                          size="small"
                          onClick={() => handleViewFile(req.file_url)}
                        >
                          <VisibilityIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Download File"
                        placement="top"
                        arrow
                        >
                        <IconButton
                          color="primary"
                          size="small"
                          onClick={() => handleDownloadFile(req.file_url)}
                        >
                          <DownloadIcon />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      No file
                    </Typography>
                  )}
                </TableCell>
                {showActions && (
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Tooltip title="Approve Request"
                        placement="top"
                        arrow
                        >
                        <IconButton
                          color="success"
                          size="small"
                          onClick={() => handleAction(req, 'approved')}
                        >
                          <CheckCircleIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Reject Request"
                        placement="top"
                        arrow
                        >
                        <IconButton
                          color="error"
                          size="small"
                          onClick={() => handleAction(req, 'rejected')}
                        >
                          <CancelIcon />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                )}
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={showActions ? 9 : 8} align="center">No requests found</TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );

  return (
    <PageLayout>
      <Box sx={{ mt: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4">Reimbursement Approvals</Typography>
        </Box>

        {error && <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>{error}</Alert>}

        <Typography variant="h5" sx={{ mb: 2 }}>Pending Requests</Typography>
        {renderRequestsTable(pendingRequests, true)}

        <Divider sx={{ my: 4 }} />
        
        <Typography variant="h5" sx={{ mb: 2 }}>Approved Requests</Typography>
        {renderRequestsTable(approvedRequests)}

        <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
          <DialogTitle>
            {action === 'approved' ? 'Approve Reimbursement' : 'Reject Reimbursement'}
          </DialogTitle>
          <DialogContent>
            <Box sx={{ mt: 2, minWidth: 400 }}>
              <Typography variant="body1" sx={{ mb: 2 }}>
                {action === 'approved' 
                  ? 'Are you sure you want to approve this reimbursement request?' 
                  : 'Are you sure you want to reject this reimbursement request?'}
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Comments"
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                sx={{ mb: 2 }}
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
            <Button 
              variant="contained" 
              color={action === 'approved' ? 'success' : 'error'}
              onClick={handleConfirm}
            >
              {action === 'approved' ? 'Approve' : 'Reject'}
            </Button>
          </DialogActions>
        </Dialog>

        <Dialog 
          open={fileDialogOpen} 
          onClose={() => setFileDialogOpen(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>View File</DialogTitle>
          <DialogContent>
            <Box sx={{ height: '70vh', width: '100%', overflow: 'auto' }}>
              {viewFileUrl && viewFileUrl.match(/\.(jpeg|jpg|png|gif)$/i) ? (
                <img 
                  src={viewFileUrl} 
                  alt="Reimbursement file" 
                  style={{ maxWidth: '100%', display: 'block', margin: '0 auto' }}
                />
              ) : viewFileUrl && viewFileUrl.match(/\.(pdf)$/i) ? (
                <iframe 
                  src={viewFileUrl} 
                  title="PDF Viewer" 
                  width="100%" 
                  height="100%" 
                  style={{ border: 'none' }}
                />
              ) : (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body1">
                    This file type cannot be previewed. Please download it to view.
                  </Typography>
                  <Button 
                    variant="contained" 
                    startIcon={<DownloadIcon />} 
                    sx={{ mt: 2 }}
                    onClick={() => handleDownloadFile(viewFileUrl)}
                  >
                    Download File
                  </Button>
                </Box>
              )}
            </Box>
          </DialogContent>
          <DialogActions>
            <Button 
              variant="outlined" 
              onClick={() => setFileDialogOpen(false)}
            >
              Close
            </Button>
            <Button 
              variant="contained" 
              startIcon={<DownloadIcon />}
              onClick={() => handleDownloadFile(viewFileUrl)}
            >
              Download
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </PageLayout>
  );
}

export default ReimbursementApprovals; 