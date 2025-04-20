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
  CircularProgress
} from '@mui/material';
import PageLayout from '../../layout/PageLayout';

function MyReimbursements () {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({ type_id: '', amount: '', note: '', file: null });
  const [types, setTypes] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [reqRes, typesRes] = await Promise.all([
        axios.get('/reimbursements/assigned'),
        axios.get('/reimbursement-types')
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
    Object.keys(formData).forEach(key => data.append(key, formData[key]));
    try {
      await axios.post('/reimbursements', data, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setShowModal(false);
      fetchData();
    } catch (err) {
      setError('Failed to submit request.');
    }
  };

  const handleFileChange = (e) => {
    setFormData({ ...formData, file: e.target.files[0] });
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

  return (
    <PageLayout>
      <Box sx={{ mt: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4">My Reimbursements</Typography>
          <Button variant="contained" color="primary" onClick={() => setShowModal(true)}>+</Button>
        </Box>

        {error && <Alert severity="error">{error}</Alert>}

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
                    <TableCell>{req.amount}</TableCell>
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
                          <Button
                            variant="contained"
                            color="primary"
                            size="small"
                          >
                            Edit
                          </Button>
                          <Button
                            variant="contained"
                            color="error"
                            size="small"
                          >
                            Delete
                          </Button>
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

        <Dialog open={showModal} onClose={() => setShowModal(false)}>
          <DialogTitle>Submit Reimbursement Request</DialogTitle>
          <DialogContent>
            <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
              <Select
                fullWidth
                value={formData.type_id}
                onChange={(e) => setFormData({ ...formData, type_id: e.target.value })}
                displayEmpty
                required
                sx={{ mb: 2 }}
              >
                <MenuItem value="" disabled>Select Type</MenuItem>
                {types.map((type) => <MenuItem key={type.id} value={type.id}>{type.name}</MenuItem>)}
              </Select>
              <TextField
                fullWidth
                type="number"
                label="Amount"
                placeholder="Amount"
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
                placeholder="Note"
                value={formData.note}
                onChange={(e) => setFormData({ ...formData, note: e.target.value })}
                sx={{ mb: 2 }}
                required
              />
              <TextField
                fullWidth
                type="file"
                onChange={handleFileChange}
                sx={{ mb: 2 }}
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowModal(false)}>Cancel</Button>
            <Button type="submit" variant="contained" color="primary">Submit</Button>
          </DialogActions>
        </Dialog>
      </Box>
    </PageLayout>
  );
};

export default MyReimbursements;