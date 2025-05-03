import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  TextField,
  CircularProgress,
  Alert,
  InputAdornment
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { Search as SearchIcon } from '@mui/icons-material';
import { getAllTaxation } from '../../services/taxationService';
import { getUserRole } from '../../utils/auth';
import PageLayout from '../../layout/PageLayout';

const EmployeeSelection = () => {
  const [loading, setLoading] = useState(true);
  const [employees, setEmployees] = useState([]);
  const [filteredEmployees, setFilteredEmployees] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const userRole = getUserRole();

  // Redirect non-admin users to their own declaration page
  useEffect(() => {
    if (userRole !== 'admin' && userRole !== 'superadmin') {
      navigate('/taxation/declaration');
    }
  }, [userRole, navigate]);

  // Fetch employees data
  useEffect(() => {
    const fetchEmployees = async () => {
      try {
        setLoading(true);
        const response = await getAllTaxation();
        setEmployees(response.records);
        setFilteredEmployees(response.records);
      } catch (err) {
        console.error('Error fetching employees:', err);
        setError('Failed to load employees data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchEmployees();
  }, []);

  // Handle search
  useEffect(() => {
    if (searchTerm.trim() === '') {
      setFilteredEmployees(employees);
    } else {
      const searchTermLower = searchTerm.toLowerCase();
      const filtered = employees.filter(emp => 
        emp.emp_id.toLowerCase().includes(searchTermLower) || 
        (emp.user_name && emp.user_name.toLowerCase().includes(searchTermLower))
      );
      setFilteredEmployees(filtered);
    }
  }, [searchTerm, employees]);

  // Handle view or edit actions
  const handleViewDeclaration = (empId) => {
    navigate(`/taxation/employee/${empId}`);
  };

  const handleEditDeclaration = (empId) => {
    navigate(`/taxation/declaration/${empId}`);
  };

  // Format currency
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount || 0);
  };

  // Helper function to get color for filing status
  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'draft': return '#e0e0e0';
      case 'filed': return '#bbdefb';
      case 'approved': return '#c8e6c9';
      case 'rejected': return '#ffcdd2';
      case 'pending': return '#fff9c4';
      default: return '#e0e0e0';
    }
  };

  if (loading) {
    return (
      <PageLayout title="Employee Selection">
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '70vh' }}>
          <CircularProgress />
        </Box>
      </PageLayout>
    );
  }

  return (
    <PageLayout title="Employee Selection">
      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            Select Employee for Tax Declaration
          </Typography>
          <Button 
            variant="outlined" 
            color="primary" 
            onClick={() => navigate('/taxation')}
          >
            Back to Dashboard
          </Button>
        </Box>

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        <TextField
          fullWidth
          variant="outlined"
          placeholder="Search by Employee ID or Name"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          sx={{ mb: 3 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow sx={{ backgroundColor: 'primary.light' }}>
                <TableCell><Typography variant="subtitle2">Employee ID</Typography></TableCell>
                <TableCell><Typography variant="subtitle2">Employee Name</Typography></TableCell>
                <TableCell><Typography variant="subtitle2">Latest Tax Year</Typography></TableCell>
                <TableCell><Typography variant="subtitle2">Tax Regime</Typography></TableCell>
                <TableCell><Typography variant="subtitle2">Total Tax</Typography></TableCell>
                <TableCell><Typography variant="subtitle2">Filing Status</Typography></TableCell>
                <TableCell><Typography variant="subtitle2">Actions</Typography></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredEmployees.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">No employees found</TableCell>
                </TableRow>
              ) : (
                filteredEmployees.map((employee) => (
                  <TableRow key={employee.emp_id}>
                    <TableCell>{employee.emp_id}</TableCell>
                    <TableCell>{employee.user_name || 'Unknown'}</TableCell>
                    <TableCell>{employee.tax_year || 'N/A'}</TableCell>
                    <TableCell>
                      {employee.regime === 'old' ? 'Old Regime' : 'New Regime'}
                    </TableCell>
                    <TableCell>{formatCurrency(employee.total_tax)}</TableCell>
                    <TableCell>
                      <Box sx={{ 
                        display: 'inline-block', 
                        bgcolor: getStatusColor(employee.filing_status), 
                        px: 1, 
                        py: 0.5, 
                        borderRadius: 1 
                      }}>
                        {employee.filing_status.charAt(0).toUpperCase() + employee.filing_status.slice(1)}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Button 
                          variant="outlined" 
                          size="small" 
                          onClick={() => handleViewDeclaration(employee.emp_id)}
                        >
                          View
                        </Button>
                        <Button 
                          variant="contained" 
                          size="small" 
                          onClick={() => handleEditDeclaration(employee.emp_id)}
                          color="primary"
                        >
                          Edit
                        </Button>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>

        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center' }}>
          <Button 
            variant="contained" 
            color="primary" 
            onClick={() => navigate('/taxation/declaration')}
          >
            Create New Declaration
          </Button>
        </Box>
      </Box>
    </PageLayout>
  );
};

export default EmployeeSelection; 