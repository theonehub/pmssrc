import React, { useEffect, useState, useCallback } from "react";
import {
  Container,
  Table,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  TableContainer,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Box,
  Paper,
  Typography,
  CircularProgress
} from "@mui/material";
import PageLayout from "../../../layout/PageLayout";
import { useAuth } from "../../../shared/hooks/useAuth";
import axios, { AxiosResponse } from "axios";

// Define interfaces
interface ProjectAttribute {
  id?: string | number;
  key: string;
  name?: string;
  value: string;
  default_value: string;
  description: string;
  is_active?: boolean;
}

interface AttributeForm {
  key: string;
  value: string;
  default_value: string;
  description: string;
}

const API_BASE_URL = 'http://localhost:8000';

const ProjectAttributes: React.FC = () => {
  const { token, user } = useAuth();
  
  // State management with proper typing
  const [attributes, setAttributes] = useState<ProjectAttribute[]>([]);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [form, setForm] = useState<AttributeForm>({ 
    key: "", 
    value: "", 
    default_value: "", 
    description: "" 
  });
  const [editKey, setEditKey] = useState<string | null>(null);
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);

  const isSuperAdmin = user?.role === "superadmin";

  const fetchAttributes = useCallback(async (): Promise<void> => {
    try {
      if (!token) {
        throw new Error('No authentication token found');
      }

      const response: AxiosResponse<ProjectAttribute[]> = await axios.get(
        `${API_BASE_URL}/attributes`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setAttributes(response.data);
    } catch (err: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error fetching attributes:', err);
      }
      setError('Failed to fetch attributes');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (isSuperAdmin) {
      fetchAttributes();
    }
  }, [isSuperAdmin, fetchAttributes]);

  const handleSubmit = async (): Promise<void> => {
    setError("");
    
    try {
      if (!form.key || !form.value || !form.default_value) {
        setError("Key, Value and Default Value are required.");
        return;
      }

      if (!token) {
        throw new Error('No authentication token found');
      }

      if (editKey) {
        await axios.put(
          `${API_BASE_URL}/attributes/${editKey}`,
          form,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );
      } else {
        await axios.post(
          `${API_BASE_URL}/attributes`,
          form,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );
      }

      setForm({ key: "", value: "", default_value: "", description: "" });
      setShowModal(false);
      setEditKey(null);
      fetchAttributes();
    } catch (err: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error saving attribute:', err);
      }
      setError("Error saving attribute.");
    }
  };

  const handleEdit = (attr: ProjectAttribute): void => {
    const formData: AttributeForm = {
      key: attr.key,
      value: attr.value,
      default_value: attr.default_value,
      description: attr.description
    };
    setForm(formData);
    setEditKey(attr.key);
    setShowModal(true);
    setError("");
  };

  const handleDelete = async (attribute: ProjectAttribute): Promise<void> => {
    if (!window.confirm("Are you sure you want to delete this attribute?")) {
      return;
    }
    
    try {
      if (!token) {
        throw new Error('No authentication token found');
      }

      await axios.delete(
        `${API_BASE_URL}/attributes/${attribute.key}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      fetchAttributes();
    } catch (err: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error deleting attribute:', err);
      }
      setError('Failed to delete attribute');
    }
  };

  const handleModalClose = (): void => {
    setShowModal(false);
    setForm({ key: "", value: "", default_value: "", description: "" });
    setEditKey(null);
    setError("");
  };

  const handleFormChange = (field: keyof AttributeForm) => (
    event: React.ChangeEvent<HTMLInputElement>
  ): void => {
    setForm(prev => ({
      ...prev,
      [field]: event.target.value
    }));
  };

  if (!isSuperAdmin) {
    return (
      <PageLayout title="Project Attributes">
        <Container maxWidth="lg" sx={{ mt: 4 }}>
          <Alert severity="error">
            Access Denied. Only Super Administrators can manage project attributes.
          </Alert>
        </Container>
      </PageLayout>
    );
  }

  return (
    <PageLayout title="Project Attributes">
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          mb: 3 
        }}>
          <Typography variant="h4" color="primary">
            Project Attributes
          </Typography>
          <Button 
            variant="contained" 
            color="primary" 
            onClick={() => setShowModal(true)}
            size="large"
          >
            + Add Attribute
          </Button>
        </Box>

        {error && !showModal && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <TableContainer component={Paper} elevation={2}>
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
                <TableCell>Attribute Key</TableCell>
                <TableCell>Value</TableCell>
                <TableCell>Default Value</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 3 }}>
                      <CircularProgress size={24} sx={{ mr: 2 }} />
                      Loading attributes...
                    </Box>
                  </TableCell>
                </TableRow>
              ) : attributes.length > 0 ? (
                attributes.map((attribute) => (
                  <TableRow 
                    key={attribute.id || attribute.key}
                    sx={{ 
                      '&:hover': { 
                        backgroundColor: 'action.hover'
                      }
                    }}
                  >
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        {attribute.key}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {attribute.value}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {attribute.default_value}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {attribute.description || 'No description'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box
                        component="span"
                        sx={{
                          display: 'inline-block',
                          padding: '4px 8px',
                          borderRadius: '4px',
                          backgroundColor: attribute.is_active !== false ? 'success.main' : 'error.main',
                          color: 'white',
                          fontSize: '0.75rem',
                          fontWeight: 'bold'
                        }}
                      >
                        {attribute.is_active !== false ? 'Active' : 'Inactive'}
                      </Box>
                    </TableCell>
                    <TableCell align="center">
                      <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center' }}>
                        <Button
                          variant="contained"
                          color="primary"
                          size="small"
                          onClick={() => handleEdit(attribute)}
                        >
                          Edit
                        </Button>
                        <Button
                          variant="contained"
                          color="error"
                          size="small"
                          onClick={() => handleDelete(attribute)}
                        >
                          Delete
                        </Button>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={6} align="center" sx={{ py: 6 }}>
                    <Typography variant="body1" color="text.secondary">
                      No project attributes found
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      Click "Add Attribute" to create your first project attribute
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Container>

      {/* Add/Edit Dialog */}
      <Dialog 
        open={showModal} 
        onClose={handleModalClose} 
        maxWidth="sm" 
        fullWidth
        disableEscapeKeyDown={false}
      >
        <DialogTitle>
          <Typography variant="h5">
            {editKey ? "Edit Attribute" : "Add New Attribute"}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {editKey 
              ? "Update the attribute details below" 
              : "Fill in the details to create a new project attribute"
            }
          </Typography>
        </DialogTitle>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              label="Key"
              value={form.key}
              disabled={!!editKey}
              onChange={handleFormChange('key')}
              fullWidth
              required
              helperText={editKey ? "Key cannot be changed when editing" : "Unique identifier for the attribute"}
            />
            <TextField
              label="Value"
              value={form.value}
              onChange={handleFormChange('value')}
              fullWidth
              required
              helperText="Current value of the attribute"
            />
            <TextField
              label="Default Value"
              value={form.default_value}
              onChange={handleFormChange('default_value')}
              fullWidth
              required
              helperText="Default value to use when attribute is not set"
            />
            <TextField
              label="Description"
              value={form.description}
              onChange={handleFormChange('description')}
              multiline
              rows={3}
              fullWidth
              placeholder="Optional description of what this attribute is used for..."
              helperText="Optional description to help understand the purpose of this attribute"
            />
          </Box>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={handleModalClose} size="large">
            Cancel
          </Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained" 
            color="primary"
            size="large"
          >
            {editKey ? "Update" : "Save"}
          </Button>
        </DialogActions>
      </Dialog>
    </PageLayout>
  );
};

export default ProjectAttributes; 