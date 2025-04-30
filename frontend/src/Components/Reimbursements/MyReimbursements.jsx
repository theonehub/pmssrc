import React, { useEffect, useState } from 'react';
import axios from '../../utils/axios';
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
  Tooltip
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Upload as UploadIcon
} from '@mui/icons-material';
import PageLayout from '../../layout/PageLayout';

function MyReimbursements () {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    reimbursement_type_id: '',
    amount: '',
    note: '',
    file: null
  });
  const [types, setTypes] = useState([]);
  const [error, setError] = useState(null);
  const [editingRequest, setEditingRequest] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [reqRes, typesRes] = await Promise.all([
        axios.get('/reimbursements/my-requests'),
        axios.get('/reimbursement-types/')
      ]);
      setRequests(reqRes.data);
      setTypes(typesRes.data);
    } catch (err) {
      setError('Failed to load data.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const data = new FormData();
    data.append('reimbursement_type_id', formData.reimbursement_type_id);
    data.append('amount', formData.amount);
    data.append('note', formData.note);
    if (formData.file) {
      data.append('file', formData.file, formData.file.name);
    }

    try {
      await axios.post('/reimbursements', data, {
        headers: { 
          'Content-Type': 'multipart/form-data'
        }
      });
      setShowModal(false);
      setFormData({
        reimbursement_type_id: '',
        amount: '',
        note: '',
        file: null
      });
      fetchData(); // Refresh the list
    } catch (err) {
      console.error('Error submitting request:', err);
      setError(err.response?.data?.detail || 'Failed to submit request.');
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file size (e.g., max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        setError('File size should not exceed 5MB');
        return;
      }
      // Validate file type
      const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf'];
      if (!allowedTypes.includes(file.type)) {
        setError('Only JPEG, PNG and PDF files are allowed');
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

  const handleDelete = async (requestId) => {
    if (window.confirm('Are you sure you want to delete this reimbursement request?')) {
      try {
        await axios.delete(`/reimbursements/${requestId}`);
        fetchData();
      } catch (err) {
        console.error('Error deleting request:', err);
        setError(err.response?.data?.detail || 'Failed to delete request.');
      }
    }
  };

  const handleEditSubmit = async (e) => {
    e.preventDefault();
    const data = new FormData();
    data.append('reimbursement_type_id', formData.reimbursement_type_id);
    data.append('amount', formData.amount);
    data.append('note', formData.note);
    if (formData.file) {
      data.append('file', formData.file, formData.file.name);
    }

    try {
      await axios.put(`/reimbursements/${editingRequest.id}`, data, {
        headers: { 
          'Content-Type': 'multipart/form-data'
        }
      });
      setShowEditModal(false);
      setEditingRequest(null);
      setFormData({
        reimbursement_type_id: '',
        amount: '',
        note: '',
        file: null
      });
      fetchData();
    } catch (err) {
      console.error('Error updating request:', err);
      setError(err.response?.data?.detail || 'Failed to update request.');
    }
  };

  return (
    <PageLayout>
      <Box sx={{ mt: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4">My Reimbursements</Typography>
          <Tooltip title="Add Reimbursement">
            <IconButton color="primary" onClick={() => setShowModal(true)}>
              <AddIcon />
            </IconButton>
          </Tooltip>
        </Box>

        {error && <Alert severity="error" onClose={() => setError(null)}>{error}</Alert>}

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
                <TableCell>Type</TableCell>
                <TableCell>Amount</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
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
                    <TableCell>{req.type_name}</TableCell>
                    <TableCell>₹{parseFloat(req.amount).toLocaleString('en-IN')}</TableCell>
                    <TableCell>{new Date(req.created_at).toLocaleDateString()}</TableCell>
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
                      {req.status === 'PENDING' && (
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Tooltip title="Edit">
                            <IconButton
                              color="primary"
                              size="small"
                              onClick={() => handleEdit(req)}
                            >
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete">
                            <IconButton
                              color="error"
                              size="small"
                              onClick={() => handleDelete(req.id)}
                            >
                              <DeleteIcon />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={6} align="center">No reimbursements found</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>

        <Dialog open={showModal} onClose={handleClose}>
          <form onSubmit={handleSubmit}>
            <DialogTitle>Submit Reimbursement Request</DialogTitle>
            <DialogContent>
              <Box sx={{ mt: 2 }}>
                <Select
                  fullWidth
                  value={formData.reimbursement_type_id}
                  onChange={(e) => setFormData({ ...formData, reimbursement_type_id: e.target.value })}
                  displayEmpty
                  required
                  sx={{ mb: 2 }}
                >
                  <MenuItem value="" disabled>Select Type</MenuItem>
                  {types.map((type) => (
                    <MenuItem key={type.reimbursement_type_id} value={type.reimbursement_type_id}>
                      {type.reimbursement_type_name}
                    </MenuItem>
                  ))}
                </Select>
                <TextField
                  fullWidth
                  type="number"
                  label="Amount"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                  sx={{ mb: 2 }}
                  required
                />
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Note"
                  value={formData.note}
                  onChange={(e) => setFormData({ ...formData, note: e.target.value })}
                  sx={{ mb: 2 }}
                  required
                />
                <TextField
                  fullWidth
                  type="file"
                  inputProps={{
                    accept: '.jpg,.jpeg,.png,.pdf'
                  }}
                  InputProps={{
                    startAdornment: (
                      <IconButton component="span">
                        <UploadIcon />
                      </IconButton>
                    ),
                  }}
                  onChange={handleFileChange}
                  sx={{ mb: 2 }}
                />
                {formData.file && (
                  <Typography variant="caption" display="block" gutterBottom>
                    Selected file: {formData.file.name}
                  </Typography>
                )}
              </Box>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleClose}>Cancel</Button>
              <Button type="submit" variant="contained" color="primary">
                Submit
              </Button>
            </DialogActions>
          </form>
        </Dialog>

        <Dialog open={showEditModal} onClose={() => { setShowEditModal(false); setEditingRequest(null); }}>
          <form onSubmit={handleEditSubmit}>
            <DialogTitle>Edit Reimbursement Request</DialogTitle>
            <DialogContent>
              <Box sx={{ mt: 2 }}>
                <Select
                  fullWidth
                  value={formData.reimbursement_type_id}
                  onChange={(e) => setFormData({ ...formData, reimbursement_type_id: e.target.value })}
                  displayEmpty
                  required
                  sx={{ mb: 2 }}
                >
                  <MenuItem value="" disabled>Select Type</MenuItem>
                  {types.map((type) => (
                    <MenuItem key={type.reimbursement_type_id} value={type.reimbursement_type_id}>
                      {type.reimbursement_type_name}
                    </MenuItem>
                  ))}
                </Select>
                <TextField
                  fullWidth
                  type="number"
                  label="Amount"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                  sx={{ mb: 2 }}
                  required
                />
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Note"
                  value={formData.note}
                  onChange={(e) => setFormData({ ...formData, note: e.target.value })}
                  sx={{ mb: 2 }}
                  required
                />
                <TextField
                  fullWidth
                  type="file"
                  inputProps={{
                    accept: '.jpg,.jpeg,.png,.pdf'
                  }}
                  InputProps={{
                    startAdornment: (
                      <IconButton component="span">
                        <UploadIcon />
                      </IconButton>
                    ),
                  }}
                  onChange={handleFileChange}
                  sx={{ mb: 2 }}
                />
                {formData.file && (
                  <Typography variant="caption" display="block" gutterBottom>
                    Selected file: {formData.file.name}
                  </Typography>
                )}
              </Box>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => { setShowEditModal(false); setEditingRequest(null); }}>Cancel</Button>
              <Button type="submit" variant="contained" color="primary">
                Update
              </Button>
            </DialogActions>
          </form>
        </Dialog>
      </Box>
    </PageLayout>
  );
};

export default MyReimbursements;