import React, { useEffect, useState } from 'react';
import {
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControlLabel,
  Switch,
  Table,
  TableContainer,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Box,
  Typography,
  IconButton,
  Tooltip,
  Paper,
  Container,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import axios from 'axios';
import { getToken } from '../../utils/auth';
import PageLayout from '../../layout/PageLayout';

function ReimbursementTypes() {
  const [types, setTypes] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    reimbursement_type_name: '',
    max_limit: 0,
    description: '',
    is_active: true,
  });
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchTypes = async () => {
    try {
      const res = await axios.get('http://localhost:8000/reimbursement-types', {
        headers: { Authorization: `Bearer ${getToken()}` },
      });
      setTypes(res.data);
    } catch (err) {
      console.error('Error fetching reimbursement types', err);
      setError('Failed to load reimbursement types.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTypes();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        await axios.put(`http://localhost:8000/reimbursement-types/${editingId}`, formData, {
          headers: { Authorization: `Bearer ${getToken()}` },
        });
      } else {
        await axios.post('http://localhost:8000/reimbursement-types', formData, {
          headers: { Authorization: `Bearer ${getToken()}` },
        });
      }
      setShowModal(false);
      setFormData({ reimbursement_type_name: '', max_limit: 0, description: '', is_active: true });
      setEditingId(null);
      fetchTypes();
    } catch (err) {
      console.error('Error saving reimbursement type', err);
      setError('Failed to save reimbursement type.');
    }
  };

  const handleEdit = (type) => {
    setFormData({ ...type });
    setEditingId(type.id);
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this reimbursement type?')) {
      try {
        await axios.delete(`http://localhost:8000/reimbursement-types/${id}`, {
          headers: { Authorization: `Bearer ${getToken()}` },
        });
        fetchTypes();
      } catch (err) {
        console.error('Error deleting reimbursement type', err);
        setError('Failed to delete reimbursement type.');
      }
    }
  };

  return (
    <PageLayout>
      <Container>
        <Box sx={{ mt: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4">Reimbursement Types</Typography>
          <Tooltip title="Add New Type"
            placement="top"
            arrow
            >
            <IconButton color="primary" onClick={() => setShowModal(true)}>
              <AddIcon />
            </IconButton>
          </Tooltip>
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
                <TableCell>Type Name</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Max Amount</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={5} align="center">Loading...</TableCell>
                </TableRow>
              ) : types.length > 0 ? (
                types.map((type) => (
                  <TableRow 
                    key={type.id}
                    sx={{ 
                      '&:hover': { 
                        backgroundColor: 'action.hover',
                        cursor: 'pointer'
                      }
                    }}
                  >
                    <TableCell>{type.reimbursement_type_name}</TableCell>
                    <TableCell>{type.description}</TableCell>
                    <TableCell>₹{type.max_limit.toLocaleString('en-IN')}</TableCell>
                    <TableCell>
                      <Box
                        component="span"
                        sx={{
                          display: 'inline-block',
                          padding: '4px 8px',
                          borderRadius: '4px',
                          backgroundColor: type.is_active ? 'success.main' : 'error.main',
                          color: 'white',
                          fontSize: '0.75rem',
                          fontWeight: 'bold'
                        }}
                      >
                        {type.is_active ? 'Active' : 'Inactive'}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Tooltip title="Edit Type"
                          placement="top"
                          arrow
                          >
                          <IconButton
                            color="primary"
                            size="small"
                            onClick={() => handleEdit(type)}
                          >
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete Type"
                          placement="top"
                          arrow
                          >
                          <IconButton
                            color="error"
                            size="small"
                            onClick={() => handleDelete(type.id)}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={5} align="center">No reimbursement types found</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>

        <Dialog 
          open={showModal} 
          onClose={() => { 
            setShowModal(false); 
            setFormData({ reimbursement_type_name: '', max_limit: 0, description: '', is_active: true }); 
            setEditingId(null); 
          }}
        >
          <DialogTitle>
            {editingId ? 'Edit' : 'Add'} Reimbursement Type
          </DialogTitle>
          <DialogContent>
            <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
              <TextField
                fullWidth
                required
                label="Name"
                value={formData.reimbursement_type_name}
                onChange={(e) => setFormData({ ...formData, reimbursement_type_name: e.target.value })}
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                required
                type="number"
                label="Max Limit"
                value={formData.max_limit}
                onChange={(e) => setFormData({ ...formData, max_limit: e.target.value })}
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                sx={{ mb: 2 }}
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  />
                }
                label="Active"
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => { 
              setShowModal(false); 
              setFormData({ reimbursement_type_name: '', max_limit: 0, description: '', is_active: true }); 
              setEditingId(null); 
            }}>
              Cancel
            </Button>
            <Button type="submit" variant="contained" color="primary" onClick={handleSubmit}>
              {editingId ? 'Update' : 'Save'}
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </PageLayout>
  );
}

export default ReimbursementTypes;