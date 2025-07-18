import React, { useState, useEffect } from 'react';
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
  CircularProgress,
  Box,
  IconButton,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  Card,
  CardContent,
  Snackbar,
  AlertColor
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import CloseIcon from '@mui/icons-material/Close';
import CompanyLeaveForm from './CompanyLeaveForm';
import {
  useCompanyLeavesQuery,
  useCreateCompanyLeaveMutation,
  useUpdateCompanyLeaveMutation,
  useDeleteCompanyLeaveMutation,
  CompanyLeave,
  CompanyLeaveFormData,
  CompanyLeaveFilters
} from '../../shared/hooks/useCompanyLeaves';

// Define interfaces for local state
interface AlertState {
  open: boolean;
  message: string;
  severity: AlertColor;
}

const CompanyLeaves: React.FC = () => {
  // Local state for UI
  const [editingLeave, setEditingLeave] = useState<CompanyLeave | undefined>(undefined);
  const [isFormOpen, setIsFormOpen] = useState<boolean>(false);
  const [alert, setAlert] = useState<AlertState>({ 
    open: false, 
    message: '', 
    severity: 'success' 
  });
  const [filters] = useState<CompanyLeaveFilters>({});

  // React Query hooks
  const { 
    data, 
    isLoading, 
    error: queryError, 
    isFetching 
  } = useCompanyLeavesQuery(filters);

  const createMutation = useCreateCompanyLeaveMutation();
  const updateMutation = useUpdateCompanyLeaveMutation();
  const deleteMutation = useDeleteCompanyLeaveMutation();

  // Derived state
  const leaves = data?.data?.items || data?.items || [];

  // Helper functions
  const showAlert = (message: string, severity: AlertColor = 'success'): void => {
    setAlert({ open: true, message, severity });
  };

  const handleCloseAlert = (): void => {
    setAlert(prev => ({ ...prev, open: false }));
  };

  // Handle React Query error
  useEffect(() => {
    if (queryError) {
      showAlert('Failed to load company leaves. Please try again.', 'error');
    }
  }, [queryError]);

  // Event handlers
  const handleSubmit = async (data: Partial<CompanyLeave>): Promise<void> => {
    try {
      const formData: CompanyLeaveFormData = {
        leave_type: data.leave_type || '',
        leave_name: data.leave_name || '',
        accrual_type: data.accrual_type || '',
        annual_allocation: data.annual_allocation || 0,
        computed_monthly_allocation: data.computed_monthly_allocation || 0,
        description: data.description || null,
        encashable: data.encashable || false,
        is_active: data.is_active !== undefined ? data.is_active : true,
      };

      if (editingLeave?.company_leave_id) {
        // Update existing leave
        await updateMutation.mutateAsync({ 
          id: editingLeave.company_leave_id, 
          data: formData 
        });
        showAlert('Company leave updated successfully!', 'success');
      } else {
        // Create new leave
        await createMutation.mutateAsync(formData);
        showAlert('Company leave created successfully!', 'success');
      }
      
      handleCloseForm();
    } catch (error: any) {
      const backendMessage = error?.response?.data?.detail;
      showAlert(backendMessage || 'Failed to save company leave', 'error');
      throw error;
    }
  };

  const handleEdit = (leave: CompanyLeave): void => {
    setEditingLeave(leave);
    setIsFormOpen(true);
  };

  const handleDelete = async (id: string): Promise<void> => {
    if (window.confirm('Are you sure you want to delete this company leave?')) {
      try {
        await deleteMutation.mutateAsync(id);
        showAlert('Company leave deleted successfully!', 'success');
      } catch (error: any) {
        const backendMessage = error?.response?.data?.detail;
        showAlert(backendMessage || 'Failed to delete company leave', 'error');
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
    <Box>
      {/* Header */}
      <Card elevation={1} sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
            <Box>
              <Typography variant="h4" color="primary" gutterBottom>
                Company Leave Policies
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Manage company leave policies and configurations
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {isFetching && <CircularProgress size={20} />}
              <Button 
                variant="contained" 
                color="primary" 
                startIcon={<AddIcon />}
                onClick={handleAddNew}
                disabled={createMutation.isPending}
              >
                ADD LEAVE POLICY
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Main Content */}
      <Paper elevation={1}>
        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 5 }}>
            <CircularProgress color="primary" />
          </Box>
        ) : (
          <TableContainer>
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
                  <TableCell>Active</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {leaves.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} align="center" sx={{ py: 6 }}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h6" color="text.secondary" gutterBottom>
                          No leave policies yet
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                          Get started by adding your first leave policy
                        </Typography>
                        <Button
                          variant="contained"
                          startIcon={<AddIcon />}
                          onClick={handleAddNew}
                        >
                          Add Leave Policy
                        </Button>
                      </Box>
                    </TableCell>
                  </TableRow>
                ) : (
                  leaves.map((leave: CompanyLeave) => (
                    <TableRow 
                      key={leave.company_leave_id}
                      hover
                      sx={{ 
                        '&:hover': { 
                          backgroundColor: 'action.hover' 
                        }
                      }}
                    >
                      <TableCell sx={{ fontWeight: 'bold' }}>
                        {leave.leave_name}
                      </TableCell>
                      <TableCell sx={{ textTransform: 'capitalize' }}>
                        {leave.accrual_type}
                      </TableCell>
                      <TableCell>{leave.annual_allocation} days</TableCell>
                      <TableCell>{leave.encashable ? 'Yes' : 'No'}</TableCell>
                      <TableCell>{leave.is_active ? 'Yes' : 'No'}</TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 0.5 }}>
                          <IconButton 
                            color="primary" 
                            onClick={() => handleEdit(leave)}
                            size="small"
                            title="Edit"
                            disabled={updateMutation.isPending}
                          >
                            <EditIcon />
                          </IconButton>
                          <IconButton 
                            color="error" 
                            onClick={() => handleDelete(leave.company_leave_id)}
                            size="small"
                            title="Delete"
                            disabled={deleteMutation.isPending}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>

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

      {/* Toast Notifications */}
      <Snackbar 
        open={alert.open} 
        autoHideDuration={6000} 
        onClose={handleCloseAlert}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={handleCloseAlert} 
          severity={alert.severity}
          sx={{ width: '100%' }}
          variant="filled"
        >
          {alert.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default CompanyLeaves; 