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
  Alert
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import PageLayout from '../../layout/PageLayout';
import reimbursementService, { ReimbursementType } from '../../services/reimbursementService';

interface FormData {
  category_name: string;
  max_limit: number | string;
  description: string;
  is_active: boolean;
  is_receipt_required: boolean;
  is_approval_required: boolean;
}

const ReimbursementTypes: React.FC = () => {
  const [types, setTypes] = useState<ReimbursementType[]>([]);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [formData, setFormData] = useState<FormData>({
    category_name: '',
    max_limit: 0,
    description: '',
    is_active: true,
    is_approval_required: true,
    is_receipt_required: true,
  });
  const [editingId, setEditingId] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');

  const fetchTypes = async (): Promise<void> => {
    try {
      const res = await reimbursementService.getReimbursementTypes();
      setTypes(res.data);
    } catch (err: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error fetching reimbursement types', err);
      }
      setError('Failed to load reimbursement types.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTypes();
  }, []);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    try {
      const submitData = {
        ...formData,
        max_limit: Number(formData.max_limit),
      };

      if (editingId) {
        await reimbursementService.updateReimbursementType(editingId, {
          category_name: submitData.category_name,
          description: submitData.description,
          max_limit: submitData.max_limit
        });
      } else {
        await reimbursementService.createReimbursementType({
          category_name: submitData.category_name,
          description: submitData.description,
          max_limit: submitData.max_limit,
          is_receipt_required: submitData.is_receipt_required,
          is_approval_required: submitData.is_approval_required
        });
      }
      handleCloseModal();
      fetchTypes();
    } catch (err: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error saving reimbursement type', err);
      }
      setError('Failed to save reimbursement type.');
    }
  };

  const handleEdit = (type: ReimbursementType): void => {
    setFormData({ 
      category_name: type.category_name,
      description: type.description || '',
      max_limit: type.max_limit || 0,
      is_active: type.is_active,
      is_receipt_required: type.is_receipt_required,
      is_approval_required: type.is_approval_required
    });
    setEditingId(type.type_id);
    setShowModal(true);
  };

  const handleDelete = async (id: string): Promise<void> => {
    if (window.confirm('Are you sure you want to delete this reimbursement type?')) {
      try {
        await reimbursementService.deleteReimbursementType(id);
        fetchTypes();
      } catch (err: any) {
        if (process.env.NODE_ENV === 'development') {
          // eslint-disable-next-line no-console
          console.error('Error deleting reimbursement type', err);
        }
        setError('Failed to delete reimbursement type.');
      }
    }
  };

  const handleCloseModal = (): void => {
    setShowModal(false);
    setFormData({ 
      category_name: '', 
      max_limit: 0, 
      description: '', 
      is_active: true,
      is_receipt_required: true,
      is_approval_required: true
    });
    setEditingId(null);
  };

  const handleInputChange = (field: keyof FormData, value: string | number | boolean): void => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <PageLayout title="Reimbursement Types">
      <Container>
        <Box sx={{ mt: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4">Reimbursement Types</Typography>
          <Tooltip title="Add New Type" placement="top" arrow>
            <IconButton color="primary" onClick={() => setShowModal(true)}>
              <AddIcon />
            </IconButton>
          </Tooltip>
        </Box>

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

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
                <TableCell>Approval Required</TableCell>
                <TableCell>Receipt Required</TableCell>
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
                    key={type.type_id}
                    sx={{ 
                      '&:hover': { 
                        backgroundColor: 'action.hover',
                        cursor: 'pointer'
                      }
                    }}
                  >
                    <TableCell>{type.category_name}</TableCell>
                    <TableCell>{type.description}</TableCell>
                    <TableCell>{type.max_limit ? `₹${type.max_limit.toLocaleString('en-IN')}` : 'No Limit'}</TableCell>
                    <TableCell>
                      <Box
                        component="span"
                        sx={{
                          display: 'inline-block',
                          padding: '4px 8px',
                          borderRadius: '4px',
                          backgroundColor: type.is_approval_required ? 'success.main' : 'error.main',
                          color: 'white',
                          fontSize: '0.75rem',
                          fontWeight: 'bold'
                        }}
                      >
                        {type.is_approval_required ? 'Yes' : 'No'}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box
                        component="span"
                        sx={{
                          display: 'inline-block',
                          padding: '4px 8px',
                          borderRadius: '4px',
                          backgroundColor: type.is_receipt_required ? 'success.main' : 'error.main',
                          color: 'white',
                          fontSize: '0.75rem',
                          fontWeight: 'bold'
                        }}
                      >
                        {type.is_receipt_required ? 'Yes' : 'No'}
                      </Box>
                    </TableCell>
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
                        <Tooltip title="Edit Type" placement="top" arrow>
                          <IconButton
                            color="primary"
                            size="small"
                            onClick={() => handleEdit(type)}
                          >
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete Type" placement="top" arrow>
                          <IconButton
                            color="error"
                            size="small"
                            onClick={() => handleDelete(type.type_id)}
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

        {/* Add/Edit Dialog */}
        <Dialog 
          open={showModal} 
          onClose={handleCloseModal}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>
            {editingId ? 'Edit' : 'Add'} Reimbursement Type
          </DialogTitle>
          <form onSubmit={handleSubmit}>
            <DialogContent>
              <Box sx={{ mt: 2 }}>
                <TextField
                  fullWidth
                  required
                  label="Name"
                  value={formData.category_name}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => 
                    handleInputChange('category_name', e.target.value)
                  }
                  sx={{ mb: 2 }}
                />
                <TextField
                  fullWidth
                  required
                  type="number"
                  label="Max Limit"
                  value={formData.max_limit}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => 
                    handleInputChange('max_limit', e.target.value)
                  }
                  sx={{ mb: 2 }}
                  inputProps={{ min: 0, step: 0.01 }}
                />
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Description"
                  value={formData.description}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => 
                    handleInputChange('description', e.target.value)
                  }
                  sx={{ mb: 2 }}
                />
                <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={formData.is_active}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => 
                          handleInputChange('is_active', e.target.checked)
                        }
                      />
                    }
                    label="Active"
                  />
                  <FormControlLabel
                    control={
                      <Switch
                        checked={formData.is_approval_required}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => 
                          handleInputChange('is_approval_required', e.target.checked)
                        }
                      />
                    }
                    label="Approval Required"
                  />
                  <FormControlLabel
                    control={
                      <Switch
                        checked={formData.is_receipt_required}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => 
                          handleInputChange('is_receipt_required', e.target.checked)
                        }
                      />
                    }
                    label="Receipt Required"
                  />
                </Box>
              </Box>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleCloseModal}>
                Cancel
              </Button>
              <Button type="submit" variant="contained" color="primary">
                {editingId ? 'Update' : 'Save'}
              </Button>
            </DialogActions>
          </form>
        </Dialog>
      </Container>
    </PageLayout>
  );
};

export default ReimbursementTypes; 