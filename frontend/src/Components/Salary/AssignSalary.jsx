import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { getToken } from '../../utils/auth';
import { Modal, Button, Table, Form, Alert, TableContainer, TableHead, TableBody, TableRow, TableCell, Box, TextField } from 'react-bootstrap';

const AssignSalary = ({ show, onClose, userId }) => {
  const [components, setComponents] = useState([]);
  const [assignedComponents, setAssignedComponents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const fetchComponents = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await axios.get('http://localhost:8000/salary-components', {
        headers: { Authorization: `Bearer ${getToken()}` },
      });
      setComponents(res.data);
    } catch (err) {
      setError('Failed to fetch salary components.');
    } finally {
      setLoading(false);
    }
  };

  const handleComponentChange = (componentId, field, value) => {
    setAssignedComponents((prev) => {
      const compIndex = prev.findIndex((comp) => comp.component_id === componentId);
      if (compIndex === -1) {
        return [...prev, { component_id: componentId, [field]: value }];
      } else {
        const newComponents = [...prev];
        newComponents[compIndex][field] = value;
        return newComponents;
      }
    });
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      await axios.post(
        `http://localhost:8000/employee-salary/assign/${userId}`,
        assignedComponents,
        {
          headers: { Authorization: `Bearer ${getToken()}` },
        }
      );
      setSuccess('Salary components assigned successfully!');
    } catch (err) {
      setError('Failed to assign salary components.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (show) fetchComponents();
  }, [show]);

  return (
    <Modal show={show} onHide={onClose} centered size="lg" scrollable>
      <Modal.Header closeButton>
        <Modal.Title>Assign Salary Components</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {error && <Alert variant="danger">{error}</Alert>}
        {success && <Alert variant="success">{success}</Alert>}
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
                <TableCell>Amount</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={4} align="center">Loading...</TableCell>
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
                    <TableCell>
                      <Box
                        component="span"
                        sx={{
                          display: 'inline-block',
                          padding: '4px 8px',
                          borderRadius: '4px',
                          backgroundColor: component.type === 'earning' ? 'success.main' : 'error.main',
                          color: 'white',
                          fontSize: '0.75rem',
                          fontWeight: 'bold'
                        }}
                      >
                        {component.type.charAt(0).toUpperCase() + component.type.slice(1)}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <TextField
                        type="number"
                        value={component.amount}
                        onChange={(e) => handleAmountChange(component.id, e.target.value)}
                        size="small"
                        fullWidth
                      />
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="contained"
                        color="error"
                        size="small"
                        onClick={() => handleRemove(component.id)}
                      >
                        Remove
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={4} align="center">No components added yet</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onClose}>
          Close
        </Button>
        <Button variant="primary" onClick={handleSubmit} disabled={loading}>
          {loading ? 'Saving...' : 'Save'}
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default AssignSalary;