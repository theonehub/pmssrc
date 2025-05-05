import React, { useEffect, useState } from 'react';
import {
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Checkbox,
  FormControlLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  Container,
  CircularProgress,
  Box,
  IconButton,
  Typography
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import api from '../../utils/apiUtils';
import PageLayout from '../../layout/PageLayout';

function CompanyLeaves() {
  const [leaves, setLeaves] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    count: 0,
    is_active: true,
  });
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const fetchLeaves = async () => {
    try {
      const res = await api.get('/company-leaves');
      setLeaves(res.data);
    } catch (err) {
      console.error('Error fetching company leaves', err);
      setError('Failed to load company leaves.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLeaves();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      if (editingId) {
        await api.put(`/company-leaves/${editingId}`, formData);
      } else {
        await api.post('/company-leaves', formData);
      }
      setShowModal(false);
      setFormData({ name: '', count: 0, is_active: true });
      setEditingId(null);
      fetchLeaves();
    } catch (err) {
      console.error('Error saving company leave', err);
      setError('Failed to save company leave.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEdit = (leave) => {
    setFormData({ ...leave });
    setEditingId(leave.company_leave_id);
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this company leave?')) {
      try {
        await api.delete(`/company-leaves/${id}`);
        fetchLeaves();
      } catch (err) {
        console.error('Error deleting company leave', err);
        setError('Failed to delete company leave.');
      }
    }
  };

  return (
    <PageLayout>
      <Container maxWidth="lg">
        <Box sx={{ mt: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h4">Company Leaves</Typography>
          <Button variant="contained" color="primary" onClick={() => setShowModal(true)}>Add New Leave</Button>
        </Box>

        {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 5 }}>
            <CircularProgress color="primary" />
          </Box>
        ) : (
          <TableContainer component={Paper} sx={{ mt: 2 }}>
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
                  <TableCell>Name</TableCell>
                  <TableCell>Count</TableCell>
                  <TableCell>Active</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {leaves.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={4} align="center">
                      No leave defined.
                    </TableCell>
                  </TableRow>
                ) : (
                  leaves.map((leave) => (
                    <TableRow key={leave.company_leave_id}>
                      <TableCell>{leave.name}</TableCell>
                      <TableCell>{leave.count}</TableCell>
                      <TableCell>{leave.is_active ? 'Yes' : 'No'}</TableCell>
                      <TableCell>
                        <IconButton 
                          color="primary" 
                          onClick={() => {
                            handleEdit(leave)
                          }}
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton 
                          color="error" 
                          onClick={() => handleDelete(leave.company_leave_id)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        <Dialog open={showModal} onClose={() => { setShowModal(false); setFormData({ name: '', count: 0, is_active: true }); setEditingId(null); }}>
          <DialogTitle>{editingId ? 'Edit' : 'Add'} Company Leave</DialogTitle>
          <DialogContent>
            <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
              <TextField
                required
                fullWidth
                label="Leave Name"
                placeholder="e.g. Casual Leave, Sick Leave"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                sx={{ mb: 2 }}
              />
              <TextField
                required
                fullWidth
                type="number"
                label="Leave Count"
                placeholder="Number of days allowed"
                value={formData.count}
                onChange={(e) => setFormData({ ...formData, count: parseInt(e.target.value) })}
                sx={{ mb: 2 }}
              />
              <FormControlLabel
                control={<Checkbox checked={formData.is_active} onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })} />}
                label="Active"
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => { setShowModal(false); setFormData({ name: '', count: 0, is_active: true }); setEditingId(null); }}>Cancel</Button>
            <Button onClick={handleSubmit} type="submit" variant="contained" color="primary" disabled={isSubmitting}>{editingId ? 'Update' : 'Save'}</Button>
          </DialogActions>
        </Dialog>
      </Container>
    </PageLayout>
  );
}

export default CompanyLeaves; 