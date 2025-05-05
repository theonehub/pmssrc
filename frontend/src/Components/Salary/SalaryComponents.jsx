import React, { useState, useEffect } from 'react';
import { FaEdit, FaTrash, FaPlus } from 'react-icons/fa';
import PageLayout from '../../layout/PageLayout';
import api from '../../utils/apiUtils';
import { 
  Paper, 
  Button, 
  Container, 
  Table, 
  CircularProgress, 
  Alert, 
  TableContainer, 
  TableHead, 
  TableBody, 
  TableRow, 
  TableCell, 
  Box, 
  TextField, 
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Snackbar,
  FormControlLabel,
  Checkbox,
  IconButton,
  Tooltip
} from '@mui/material';
import { Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import Pagination from '@mui/material/Pagination';

function SalaryComponents() {
  const [components, setComponents] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ name: '', type: 'earning', description: '' });
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [toast, setToast] = useState({ show: false, message: '', severity: 'success' });

  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 5;

  // Fetch components from API
  const fetchComponents = async () => {
    setLoading(true);
    try {
      const res = await api.get('/salary-components');
      setComponents(res.data);
    } catch (error) {
      console.error('Error fetching components:', error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchComponents();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const componentData = {
        sc_id: editingId || formData.sc_id,
        name: formData.name,
        type: formData.type,
        key: formData.name.toLowerCase().replace(/\s+/g, ''),
        max_value: formData.max_value || 0,
        declared_value: formData.declared_value || 0,
        actual_value: formData.actual_value || 0,
        is_active: formData.is_active,
        is_visible: formData.is_visible,
        is_mandatory: formData.is_mandatory,
        declaration_required: formData.declaration_required,
        description: formData.description
      };

      if (editingId) {
        await api.put(`/salary-components/${editingId}`, componentData);
        setToast({ show: true, message: 'Component updated successfully.', severity: 'success' });
      } else {
        await api.post('/salary-components', componentData);
        setToast({ show: true, message: 'Component added successfully.', severity: 'success' });
      }
      fetchComponents();
      handleCloseForm();
    } catch (error) {
      console.error('Error saving component:', error);
      setToast({ show: true, message: 'Error saving component.', severity: 'error' });
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this component?')) return;

    try {
      await api.delete(`/salary-components/${id}`);
      setToast({ show: true, message: 'Component deleted.', severity: 'info' });
      fetchComponents();
    } catch (err) {
      console.error('Error deleting component:', err);
      setToast({ show: true, message: 'Error deleting component.', severity: 'error' });
    }
  };

  const handleEdit = (comp) => {
    setFormData({ sc_id: comp.sc_id, name: comp.name, type: comp.type, is_active: comp.is_active, is_visible: comp.is_visible, is_mandatory: comp.is_mandatory, declaration_required: comp.declaration_required, description: comp.description });
    setEditingId(comp.sc_id);
    setShowForm(true);
  };

  const handleCloseForm = () => {
    setShowForm(false);
    setFormData({ name: '', type: 'earning', is_active: true, is_visible: true, is_mandatory: true, declaration_required: true, description: '' });
    setEditingId(null);
  };

  const filteredComponents = components.filter((comp) =>
    comp.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    comp.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
    comp.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalPages = Math.ceil(filteredComponents.length / pageSize);
  const paginatedComponents = filteredComponents.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

  return (
    <PageLayout>
      <Container sx={{ mt: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4">Salary Components</Typography>
          <Button variant="contained" startIcon={<FaPlus />} onClick={() => setShowForm(true)}>
            Add Component
          </Button>
        </Box>

        <TextField
          fullWidth
          variant="outlined"
          placeholder="Search by name or type"
          size="small"
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            setCurrentPage(1);
          }}
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
                <TableCell>Component Name</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Is Active</TableCell>
                <TableCell>Is Visible</TableCell>
                <TableCell>Is Mandatory</TableCell>
                <TableCell>Employee Declaration Required</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={5} align="center">Loading...</TableCell>
                </TableRow>
              ) : components.length > 0 ? (
                components.map((component) => (
                  <TableRow 
                    key={component.id}
                    sx={{ 
                      '&:hover': { 
                        backgroundColor: 'action.hover',
                        cursor: 'pointer'
                      }
                    }}
                  >
                    <TableCell>{component.name}</TableCell>
                    <TableCell>{component.type.charAt(0).toUpperCase() + component.type.slice(1)}</TableCell>
                    <TableCell>{component.is_active ? 'Yes' : 'No'}</TableCell>
                    <TableCell>{component.is_visible ? 'Yes' : 'No'}</TableCell>
                    <TableCell>{component.is_mandatory ? 'Yes' : 'No'}</TableCell>
                    <TableCell>{component.declaration_required ? 'Yes' : 'No'}</TableCell>
                    <TableCell>{component.description}</TableCell>
                    
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Tooltip title="Edit Component">
                          <IconButton
                            color="primary"
                            size="small"
                            onClick={() => handleEdit(component)}
                          >
                            <EditIcon />
                          </IconButton> 
                        </Tooltip>
                        <Tooltip title="Delete Component">
                          <IconButton
                            color="error"
                            size="small"
                            onClick={() => handleDelete(component.sc_id)}
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
                  <TableCell colSpan={5} align="center">No salary components found</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Pagination Controls */}
        {totalPages > 1 && (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
            <Pagination 
              count={totalPages} 
              page={currentPage} 
              onChange={(event, value) => setCurrentPage(value)}
              color="primary"
            />
          </Box>
        )}

        {/* Add/Edit Dialog Form */}
        <Dialog 
          open={showForm} 
          onClose={handleCloseForm}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>{editingId ? 'Edit' : 'Add'} Salary Component</DialogTitle>
          <form onSubmit={handleSubmit}>
            <DialogContent>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <TextField
                  label="Name"
                  fullWidth
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />

                <FormControl fullWidth>
                  <InputLabel>Type</InputLabel>
                  <Select
                    value={formData.type}
                    label="Type"
                    onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                  >
                    <MenuItem value="earning">Earning</MenuItem>
                    <MenuItem value="deduction">Deduction</MenuItem>
                  </Select>
                </FormControl>
                <TextField
                  label="Description" 
                  fullWidth
                  multiline
                  rows={2}
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
                <FormControlLabel
                  control={<Checkbox checked={formData.is_active} onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })} />}
                  label="Is Active"
                />
                <FormControlLabel
                  control={<Checkbox checked={formData.is_mandatory} onChange={(e) => setFormData({ ...formData, is_mandatory: e.target.checked })} />}
                  label="Is Mandatory"
                />
                <FormControlLabel
                  control={<Checkbox checked={formData.is_visible} onChange={(e) => setFormData({ ...formData, is_visible: e.target.checked })} />}
                  label="Is Visible"
                />
                <FormControlLabel
                  control={<Checkbox checked={formData.declaration_required} onChange={(e) => setFormData({ ...formData, declaration_required: e.target.checked })} />}
                  label="Employee Declaration Required"
                />
              </Box>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleCloseForm}>Cancel</Button>
              <Button type="submit" variant="contained">
                {editingId ? 'Update' : 'Add'}
              </Button>
            </DialogActions>
          </form>
        </Dialog>

        {/* Snackbar for notifications */}
        <Snackbar
          open={toast.show}
          autoHideDuration={3000}
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
      </Container>
    </PageLayout>
  );
}

export default SalaryComponents;
