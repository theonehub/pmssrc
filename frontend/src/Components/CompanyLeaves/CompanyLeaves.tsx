import React, { useEffect, useState } from 'react';
import {
  Button,
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
  Typography,
  Dialog,
  DialogTitle,
  DialogContent
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import CloseIcon from '@mui/icons-material/Close';
import api from '../../utils/apiUtils';
import PageLayout from '../../layout/PageLayout';
import CompanyLeaveForm from './CompanyLeaveForm';
import { CompanyLeave } from '../../models/companyLeave';

const CompanyLeaves: React.FC = () => {
  const [leaves, setLeaves] = useState<CompanyLeave[]>([]);
  const [editingLeave, setEditingLeave] = useState<CompanyLeave | undefined>(undefined);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');
  const [isFormOpen, setIsFormOpen] = useState<boolean>(false);

  const fetchLeaves = async (): Promise<void> => {
    try {
      const res = await api.get('/api/v2/company-leaves');
      // Backend returns CompanyLeaveListResponseDTO with structure: { items: [...], total, page, page_size, total_pages }
      // Extract the items array from the response
      if (res.data && res.data.items && Array.isArray(res.data.items)) {
        setLeaves(res.data.items);
      } else if (Array.isArray(res.data)) {
        // Fallback: if it's already an array (for backwards compatibility)
        setLeaves(res.data);
      } else {
        // If neither, set empty array
        setLeaves([]);
      }
    } catch (err: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error fetching company leaves', err);
      }
      setError('Failed to load company leaves.');
      // Set empty array on error to ensure leaves.map works
      setLeaves([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLeaves();
  }, []);

  const handleSubmit = async (data: Partial<CompanyLeave>): Promise<void> => {
    try {
      if (editingLeave?.company_leave_id) {
        // Update existing leave
        await api.put(`/api/v2/company-leaves/${editingLeave.company_leave_id}`, data);
      } else {
        // Create new leave
        await api.post('/api/v2/company-leaves', data);
      }
      
      // Refresh the list and close form
      await fetchLeaves();
      handleCloseForm();
      setError('');
    } catch (err: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error saving company leave', err);
      }
      throw new Error(err.response?.data?.detail || 'Failed to save company leave.');
    }
  };

  const handleEdit = (leave: CompanyLeave): void => {
    setEditingLeave(leave);
    setIsFormOpen(true);
  };

  const handleDelete = async (id: string): Promise<void> => {
    if (window.confirm('Are you sure you want to delete this company leave?')) {
      try {
        await api.delete(`/api/v2/company-leaves/${id}`);
        fetchLeaves();
      } catch (err: any) {
        if (process.env.NODE_ENV === 'development') {
          // eslint-disable-next-line no-console
          console.error('Error deleting company leave', err);
        }
        setError('Failed to delete company leave.');
      }
    }
  };

  const handleAddNew = (): void => {
    setEditingLeave(undefined);
    setIsFormOpen(true);
  };

  const handleCloseForm = (): void => {
    setEditingLeave(undefined);
    setIsFormOpen(false);
  };

  return (
    <PageLayout title="Company Leave Policies">
      <Container maxWidth="xl">
        <Box sx={{ mt: 4 }}>
          <Typography variant="h4" gutterBottom>
            Company Leave Policies
          </Typography>

          {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6">
              All Leave Policies ({leaves.length})
            </Typography>
            <Button 
              variant="contained" 
              color="primary" 
              startIcon={<AddIcon />}
              onClick={handleAddNew}
            >
              Add New Leave Policy
            </Button>
          </Box>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 5 }}>
              <CircularProgress color="primary" />
            </Box>
          ) : (
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
                    <TableCell>Leave Name</TableCell>
                    <TableCell>Accrual Type</TableCell>
                    <TableCell>Annual Allocation</TableCell>
                    <TableCell>Encashable</TableCell>
                    <TableCell>During Probation</TableCell>
                    <TableCell>Active</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {leaves.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} align="center">
                        No leave policies defined.
                      </TableCell>
                    </TableRow>
                  ) : (
                    leaves.map((leave) => (
                      <TableRow key={leave.company_leave_id}>
                        <TableCell sx={{ fontWeight: 'bold' }}>
                          {leave.leave_name}
                        </TableCell>
                        <TableCell sx={{ textTransform: 'capitalize' }}>
                          {leave.accrual_type}
                        </TableCell>
                        <TableCell>{leave.annual_allocation} days</TableCell>
                        <TableCell>{leave.encashable ? 'Yes' : 'No'}</TableCell>
                        <TableCell>{leave.is_allowed_on_probation ? 'Yes' : 'No'}</TableCell>
                        <TableCell>{leave.is_active ? 'Yes' : 'No'}</TableCell>
                        <TableCell>
                          <IconButton 
                            color="primary" 
                            onClick={() => handleEdit(leave)}
                            size="small"
                            title="Edit"
                          >
                            <EditIcon />
                          </IconButton>
                          <IconButton 
                            color="error" 
                            onClick={() => handleDelete(leave.company_leave_id)}
                            size="small"
                            title="Delete"
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

          {/* Modal Dialog for Form */}
          <Dialog 
            open={isFormOpen} 
            onClose={handleCloseForm}
            maxWidth="md"
            fullWidth
          >
            <DialogTitle>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h6">
                  {editingLeave ? 'Edit Leave Policy' : 'Add New Leave Policy'}
                </Typography>
                <IconButton onClick={handleCloseForm} size="small">
                  <CloseIcon />
                </IconButton>
              </Box>
            </DialogTitle>
            <DialogContent>
              {isFormOpen && (
                <CompanyLeaveForm 
                  companyLeave={editingLeave || undefined}
                  onSubmit={handleSubmit}
                  onCancel={handleCloseForm}
                />
              )}
            </DialogContent>
          </Dialog>
        </Box>
      </Container>
    </PageLayout>
  );
};

export default CompanyLeaves; 