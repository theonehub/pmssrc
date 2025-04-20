import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { getToken } from '../../utils/auth';
import PageLayout from '../../layout/PageLayout'; // Adjust path if needed
import { TableContainer, Table, TableHead, TableBody, TableRow, TableCell, Box, Button, Paper } from '@mui/material';

function DeclareSalary() {
  const [components, setComponents] = useState([]);
  const [declarations, setDeclarations] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [alert, setAlert] = useState({ type: '', message: '', show: false });
  const [loading, setLoading] = useState(true);
  const [salaries, setSalaries] = useState([]);

  const showAlert = (type, message) => {
    setAlert({ type, message, show: true });
    setTimeout(() => setAlert({ type: '', message: '', show: false }), 3000);
  };

  const fetchComponents = async () => {
    try {
      const res = await axios.get('http://localhost:8000/employee/salary-components', {
        headers: { Authorization: `Bearer ${getToken()}` },
      });

      const fetchedComponents = res.data;
      setComponents(fetchedComponents);

      const prefill = {};
      fetchedComponents.forEach((comp) => {
        if (comp.declared_amount) {
          prefill[comp.component_id] = comp.declared_amount;
        }
      });
      setDeclarations(prefill);
    } catch (err) {
      console.error('Error fetching components', err);
      showAlert('danger', 'Failed to fetch salary components');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchComponents();
  }, []);

  const handleChange = (componentId, value) => {
    setDeclarations((prev) => ({
      ...prev,
      [componentId]: value,
    }));
  };

  const handleSubmit = async (component) => {
    const declaredAmount = parseFloat(declarations[component.component_id]);
    const { min_amount, max_amount, is_editable } = component;

    if (!is_editable) {
      showAlert('warning', 'You are not allowed to declare for this component');
      return;
    }

    if (isNaN(declaredAmount) || declaredAmount < min_amount || declaredAmount > max_amount) {
      showAlert('danger', `Amount must be between ₹${min_amount} and ₹${max_amount}`);
      return;
    }

    try {
      setSubmitting(true);
      await axios.post(
        'http://localhost:8000/employee/declare',
        {
          component_id: component.component_id,
          declared_amount: declaredAmount,
        },
        {
          headers: { Authorization: `Bearer ${getToken()}` },
        }
      );
      showAlert('success', 'Declaration submitted successfully!');
    } catch (err) {
      console.error('Error submitting declaration', err);
      showAlert('danger', 'Failed to submit declaration');
    } finally {
      setSubmitting(false);
    }
  };

  const fetchSalaries = async () => {
    try {
      const res = await axios.get('http://localhost:8000/employee/salaries', {
        headers: { Authorization: `Bearer ${getToken()}` },
      });

      const fetchedSalaries = res.data;
      setSalaries(fetchedSalaries);
    } catch (err) {
      console.error('Error fetching salaries', err);
      showAlert('danger', 'Failed to fetch salaries');
    }
  };

  useEffect(() => {
    fetchSalaries();
  }, []);

  const handleEdit = (salary) => {
    // Implement edit functionality
  };

  const handleDelete = (salary) => {
    // Implement delete functionality
  };

  return (
    <PageLayout>
      <div className="container mt-4">
        <h3 className="mb-3">🧾 Declare Your Salary Components</h3>

        {alert.show && (
          <div className={`alert alert-${alert.type} alert-dismissible fade show`} role="alert">
            {alert.message}
            <button type="button" className="btn-close" onClick={() => setAlert({ ...alert, show: false })}></button>
          </div>
        )}

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
                <TableCell>Employee</TableCell>
                <TableCell>Basic Salary</TableCell>
                <TableCell>Allowances</TableCell>
                <TableCell>Deductions</TableCell>
                <TableCell>Net Salary</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">Loading...</TableCell>
                </TableRow>
              ) : salaries.length > 0 ? (
                salaries.map((salary) => (
                  <TableRow 
                    key={salary.id}
                    sx={{ 
                      '&:hover': { 
                        backgroundColor: 'action.hover',
                        cursor: 'pointer'
                      }
                    }}
                  >
                    <TableCell>{salary.employee_name}</TableCell>
                    <TableCell>{salary.basic_salary}</TableCell>
                    <TableCell>{salary.allowances}</TableCell>
                    <TableCell>{salary.deductions}</TableCell>
                    <TableCell>{salary.net_salary}</TableCell>
                    <TableCell>
                      <Box
                        component="span"
                        sx={{
                          display: 'inline-block',
                          padding: '4px 8px',
                          borderRadius: '4px',
                          backgroundColor: salary.is_active ? 'success.main' : 'error.main',
                          color: 'white',
                          fontSize: '0.75rem',
                          fontWeight: 'bold'
                        }}
                      >
                        {salary.is_active ? 'Active' : 'Inactive'}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Button
                          variant="contained"
                          color="primary"
                          size="small"
                          onClick={() => handleEdit(salary)}
                        >
                          Edit
                        </Button>
                        <Button
                          variant="contained"
                          color="error"
                          size="small"
                          onClick={() => handleDelete(salary)}
                        >
                          Delete
                        </Button>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={7} align="center">No salary declarations found</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </div>
    </PageLayout>
  );
}

export default DeclareSalary;