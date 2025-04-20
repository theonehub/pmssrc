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
  Typography
} from '@mui/material';
import axios from 'axios';
import { getToken } from '../../utils/auth';
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
  const [error, setError] = useState('');

  const fetchLeaves = async () => {
    try {
      const res = await axios.get('http://localhost:8000/company-leaves', {
        headers: { Authorization: `Bearer ${getToken()}` },
      });
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
    try {
      if (editingId) {
        await axios.put(`http://localhost:8000/company-leaves/${editingId}`, formData, {
          headers: { Authorization: `Bearer ${getToken()}` },
        });
      } else {
        await axios.post('http://localhost:8000/company-leaves', formData, {
          headers: { Authorization: `Bearer ${getToken()}` },
        });
      }
      setShowModal(false);
      setFormData({ name: '', count: 0, is_active: true });
      setEditingId(null);
      fetchLeaves();
    } catch (err) {
      console.error('Error saving company leave', err);
      setError('Failed to save company leave.');
    }
  };

  const handleEdit = (leave) => {
    setFormData({ ...leave });
    setEditingId(leave.id);
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this company leave?')) {
      try {
        await axios.delete(`http://localhost:8000/company-leaves/${id}`, {
          headers: { Authorization: `Bearer ${getToken()}` },
        });
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
                {leaves.map((leave) => (
                  <TableRow key={leave.id}>
                    <TableCell>{leave.name}</TableCell>
                    <TableCell>{leave.count}</TableCell>
                    <TableCell>{leave.is_active ? 'Yes' : 'No'}</TableCell>
                    <TableCell>
                      <Button size="small" variant="contained" color="info" sx={{ mr: 1 }} onClick={() => handleEdit(leave)}>Edit</Button>
                      <Button size="small" variant="contained" color="error" onClick={() => handleDelete(leave.id)}>Delete</Button>
                    </TableCell>
                  </TableRow>
                ))}
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
            <Button type="submit" variant="contained" color="primary">{editingId ? 'Update' : 'Save'}</Button>
          </DialogActions>
        </Dialog>
      </Container>
    </PageLayout>
  );
}

export default CompanyLeaves; 