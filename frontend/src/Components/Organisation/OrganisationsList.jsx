import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { getToken } from '../../utils/auth';
import PageLayout from '../../layout/PageLayout';
import {
  Box,
  Button,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  CircularProgress,
  Snackbar,
  Alert,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import { EmptyOrganisation } from '../../models/organisation';
import OrganisationForm from './OrganisationForm';

function OrganisationsList() {
  const [organisations, setOrganisations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(0);
  const [limit, setLimit] = useState(10);
  const [total, setTotal] = useState(0);
  const [showForm, setShowForm] = useState(false);
  const [currentOrganisation, setCurrentOrganisation] = useState(EmptyOrganisation);
  const [toast, setToast] = useState({ show: false, message: '', severity: 'success' });

  // Fetch organisations from API
  const fetchOrganisations = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`http://localhost:8000/organisations?skip=${page * limit}&limit=${limit}`, {
        headers: { Authorization: `Bearer ${getToken()}` },
      });
      setOrganisations(res.data.organisations);
      setTotal(res.data.total);
    } catch (error) {
      console.error('Error fetching organisations:', error);
      setToast({
        show: true,
        message: 'Failed to load organisations. ' + (error.response?.data?.detail || error.message),
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrganisations();
  }, [page, limit]);

  const handleEdit = (organisation) => {
    setCurrentOrganisation(organisation);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this organisation?')) return;

    try {
      await axios.delete(`http://localhost:8000/organisation/${id}`, {
        headers: { Authorization: `Bearer ${getToken()}` },
      });
      
      setToast({
        show: true,
        message: 'Organisation deleted successfully',
        severity: 'success'
      });
      
      fetchOrganisations();
    } catch (error) {
      console.error('Error deleting organisation:', error);
      setToast({
        show: true,
        message: 'Failed to delete organisation: ' + (error.response?.data?.detail || error.message),
        severity: 'error'
      });
    }
  };

  const handleAdd = () => {
    setCurrentOrganisation(EmptyOrganisation);
    setShowForm(true);
  };

  const handleFormClose = () => {
    setShowForm(false);
    setCurrentOrganisation(EmptyOrganisation);
  };

  const handleFormSubmit = async (formData) => {
    try {
      if (formData.id) {
        // Update existing organisation
        await axios.put(`http://localhost:8000/organisation/${formData.id}`, formData, {
          headers: { Authorization: `Bearer ${getToken()}` },
        });
        setToast({
          show: true,
          message: 'Organisation updated successfully',
          severity: 'success'
        });
      } else {
        // Create new organisation
        await axios.post('http://localhost:8000/organisation', formData, {
          headers: { Authorization: `Bearer ${getToken()}` },
        });
        setToast({
          show: true,
          message: 'Organisation created successfully',
          severity: 'success'
        });
      }
      
      handleFormClose();
      fetchOrganisations();
    } catch (error) {
      console.error('Error saving organisation:', error);
      setToast({
        show: true,
        message: 'Failed to save organisation: ' + (error.response?.data?.detail || error.message),
        severity: 'error'
      });
    }
  };

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
    // Reset to first page when searching
    setPage(0);
  };

  // Filter organisations based on search term
  const filteredOrganisations = organisations.filter(
    (org) => org.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
             org.city.toLowerCase().includes(searchTerm.toLowerCase()) ||
             org.country.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <PageLayout>
      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4">Organisations</Typography>
          <Button 
            variant="contained" 
            startIcon={<AddIcon />} 
            onClick={handleAdd}
          >
            Add Organisation
          </Button>
        </Box>

        <TextField
          fullWidth
          label="Search by name, city, or country"
          variant="outlined"
          value={searchTerm}
          onChange={handleSearch}
          sx={{ mb: 3 }}
        />

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
                <TableCell>Name</TableCell>
                <TableCell>City</TableCell>
                <TableCell>Country</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    <CircularProgress size={24} />
                  </TableCell>
                </TableRow>
              ) : filteredOrganisations.length > 0 ? (
                filteredOrganisations.map((org) => (
                  <TableRow key={org.id}>
                    <TableCell>{org.name}</TableCell>
                    <TableCell>{org.city}</TableCell>
                    <TableCell>{org.country}</TableCell>
                    <TableCell>{org.is_active ? 'Active' : 'Inactive'}</TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Button
                          size="small"
                          variant="contained"
                          color="primary"
                          startIcon={<EditIcon />}
                          onClick={() => handleEdit(org)}
                        >
                          Edit
                        </Button>
                        <Button
                          size="small"
                          variant="contained"
                          color="error"
                          startIcon={<DeleteIcon />}
                          onClick={() => handleDelete(org.id)}
                        >
                          Delete
                        </Button>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    No organisations found
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Pagination controls - simplified, you might want to add actual pagination UI */}
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
          <Button 
            disabled={page === 0} 
            onClick={() => setPage(page - 1)}
          >
            Previous
          </Button>
          <Box sx={{ mx: 2, display: 'flex', alignItems: 'center' }}>
            Page {page + 1} of {Math.ceil(total / limit)}
          </Box>
          <Button 
            disabled={page >= Math.ceil(total / limit) - 1} 
            onClick={() => setPage(page + 1)}
          >
            Next
          </Button>
        </Box>

        {/* Feedback Toast */}
        <Snackbar
          open={toast.show}
          autoHideDuration={6000}
          onClose={() => setToast({ ...toast, show: false })}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <Alert 
            onClose={() => setToast({ ...toast, show: false })} 
            severity={toast.severity}
            sx={{ width: '100%' }}
          >
            {toast.message}
          </Alert>
        </Snackbar>

        {/* Organisation Form Dialog */}
        <Dialog
          open={showForm}
          onClose={handleFormClose}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>
            {currentOrganisation.id ? 'Edit Organisation' : 'Add Organisation'}
          </DialogTitle>
          <DialogContent>
            <OrganisationForm 
              organisation={currentOrganisation} 
              onSubmit={handleFormSubmit} 
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={handleFormClose}>Cancel</Button>
          </DialogActions>
        </Dialog>
      </Box>
    </PageLayout>
  );
}

export default OrganisationsList; 