import React, { useEffect, useState } from "react";
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
import { useAuth } from "../../../hooks/useAuth";
import axios from "axios";

const ProjectAttributes = () => {
  const { token, user } = useAuth();
  const [attributes, setAttributes] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ key: "", value: "", default_value: "", description: "" });
  const [editKey, setEditKey] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const isSuperAdmin = user?.role === "superadmin";

  useEffect(() => {
    if (isSuperAdmin) fetchAttributes();
  }, [isSuperAdmin]);

  const fetchAttributes = async () => {
    try {
      const res = await axios.get("http://localhost:8000/attributes", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setAttributes(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    try {
      if (!form.key || !form.value || !form.default_value) {
        setError("Key, Value and Default Value are required.");
        return;
      }

      if (editKey) {
        await axios.put(`http://localhost:8000/attributes/${editKey}`, form, {
          headers: { Authorization: `Bearer ${token}` },
        });
      } else {
        await axios.post("http://localhost:8000/attributes", form, {
          headers: { Authorization: `Bearer ${token}` },
        });
      }

      setForm({ key: "", value: "", default_value: "", description: "" });
      setShowModal(false);
      setEditKey(null);
      fetchAttributes();
    } catch (err) {
      console.error(err);
      setError("Error saving attribute.");
    }
  };

  const handleEdit = (attr) => {
    setForm(attr);
    setEditKey(attr.key);
    setShowModal(true);
  };

  const handleDelete = async (key) => {
    if (!window.confirm("Are you sure you want to delete this attribute?")) return;
    try {
      await axios.delete(`http://localhost:8000/attributes/${key}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      fetchAttributes();
    } catch (err) {
      console.error(err);
    }
  };

  if (!isSuperAdmin) {
    return (
      <PageLayout>
        <Container maxWidth="lg" sx={{ mt: 4 }}>
          <Alert severity="error">Access Denied</Alert>
        </Container>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4">Project Attributes</Typography>
          <Button variant="contained" color="primary" onClick={() => setShowModal(true)}>
            + Add Attribute
          </Button>
        </Box>

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
                <TableCell>Attribute Name</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={4} align="center">
                    <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                      <CircularProgress />
                    </Box>
                  </TableCell>
                </TableRow>
              ) : attributes.length > 0 ? (
                attributes.map((attribute) => (
                  <TableRow 
                    key={attribute.id}
                    sx={{ 
                      '&:hover': { 
                        backgroundColor: 'action.hover',
                        cursor: 'pointer'
                      }
                    }}
                  >
                    <TableCell>{attribute.name}</TableCell>
                    <TableCell>{attribute.description}</TableCell>
                    <TableCell>
                      <Box
                        component="span"
                        sx={{
                          display: 'inline-block',
                          padding: '4px 8px',
                          borderRadius: '4px',
                          backgroundColor: attribute.is_active ? 'success.main' : 'error.main',
                          color: 'white',
                          fontSize: '0.75rem',
                          fontWeight: 'bold'
                        }}
                      >
                        {attribute.is_active ? 'Active' : 'Inactive'}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
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
                  <TableCell colSpan={4} align="center">No project attributes found</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Container>

      {/* Add/Edit Dialog */}
      <Dialog open={showModal} onClose={() => setShowModal(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editKey ? "Edit Attribute" : "Add Attribute"}</DialogTitle>
        <DialogContent>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              label="Key"
              value={form.key}
              disabled={!!editKey}
              onChange={(e) => setForm({ ...form, key: e.target.value })}
              fullWidth
            />
            <TextField
              label="Value"
              value={form.value}
              onChange={(e) => setForm({ ...form, value: e.target.value })}
              fullWidth
            />
            <TextField
              label="Default Value"
              value={form.default_value}
              onChange={(e) => setForm({ ...form, default_value: e.target.value })}
              fullWidth
            />
            <TextField
              label="Description (optional)"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              multiline
              rows={2}
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowModal(false)}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" color="primary">
            {editKey ? "Update" : "Save"}
          </Button>
        </DialogActions>
      </Dialog>
    </PageLayout>
  );
};

export default ProjectAttributes;