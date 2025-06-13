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
import { getUserRole } from '../../shared/utils/auth';
import PageLayout from '../../layout/PageLayout';
import { TaxationData, UserRole, FilingStatus } from '../../shared/types';

interface EmployeeRecord extends TaxationData {
  user_name?: string;
  total_tax: number;
}

/**
 * EmployeeSelection Component - Admin interface for selecting employees to manage tax declarations
 */
const EmployeeSelection: React.FC = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [employees, setEmployees] = useState<EmployeeRecord[]>([]);
  const [filteredEmployees, setFilteredEmployees] = useState<EmployeeRecord[]>([]);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const userRole: UserRole | null = getUserRole();

  // Redirect non-admin users to their own declaration page
  useEffect(() => {
    if (userRole !== 'admin' && userRole !== 'superadmin') {
      navigate('/api/v2/taxation/declaration');
    }
  }, [userRole, navigate]);

  // Fetch employees data
  useEffect(() => {
    const fetchEmployees = async (): Promise<void> => {
      try {
        setLoading(true);
        // Mock implementation since getAllTaxation is not available
        const mockEmployeeData: EmployeeRecord[] = [
          {
            employee_id: 'EMP001',
            user_name: 'John Doe',
            tax_year: '2023-24',
            regime: 'new',
            total_tax: 50000,
            filing_status: 'filed',
            basic_salary: 600000,
            hra: 240000,
            da: 0,
            medical_allowance: 15000,
            transport_allowance: 12000,
            other_allowances: 10000,
            bonus: 50000,
            pf_employee: 21600,
            esi_employee: 0,
            professional_tax: 2400,
            tds: 48000,
            other_income: 0,
            house_property_income: 0,
            capital_gains: 0,
            section_80c: 150000,
            section_80d: 25000,
            section_80g: 0,
            section_80e: 0,
            section_80tta: 0,
            perquisites: {
              accommodation_type: 'none',
              accommodation_value: 0,
              car_provided: false,
              car_cc: 0,
              car_owned_by: 'employee',
              car_used_for_business: 0,
              car_value: 0,
              driver_salary: 0,
              fuel_provided: false,
              fuel_value: 0,
              gas_electricity_water: 0,
              medical_reimbursement: 0,
              lta_claimed: 0,
              lta_exempt: 0,
              education_provided: false,
              education_value: 0,
              loan_amount: 0,
              loan_interest_rate: 0,
              loan_interest_benefit: 0,
              movable_assets_value: 0,
              esop_value: 0,
              esop_exercise_price: 0,
              esop_market_price: 0,
              other_perquisites: 0,
              total_perquisites: 0
            },
            separation_benefits: 0,
            gross_total_income: 927000,
            total_deductions: 175000,
            taxable_income: 752000,
            tax_before_relief: 50000,
            tax_relief: 0,
            tax_payable: 50000,
            advance_tax_paid: 0,
            tds_deducted: 48000,
            self_assessment_tax: 2000
          },
          {
            employee_id: 'EMP002',
            user_name: 'Jane Smith',
            tax_year: '2023-24',
            regime: 'old',
            total_tax: 75000,
            filing_status: 'pending',
            basic_salary: 800000,
            hra: 320000,
            da: 0,
            medical_allowance: 15000,
            transport_allowance: 12000,
            other_allowances: 15000,
            bonus: 80000,
            pf_employee: 21600,
            esi_employee: 0,
            professional_tax: 2400,
            tds: 72000,
            other_income: 0,
            house_property_income: 0,
            capital_gains: 0,
            section_80c: 150000,
            section_80d: 25000,
            section_80g: 0,
            section_80e: 0,
            section_80tta: 0,
            perquisites: {
              accommodation_type: 'none',
              accommodation_value: 0,
              car_provided: false,
              car_cc: 0,
              car_owned_by: 'employee',
              car_used_for_business: 0,
              car_value: 0,
              driver_salary: 0,
              fuel_provided: false,
              fuel_value: 0,
              gas_electricity_water: 0,
              medical_reimbursement: 0,
              lta_claimed: 0,
              lta_exempt: 0,
              education_provided: false,
              education_value: 0,
              loan_amount: 0,
              loan_interest_rate: 0,
              loan_interest_benefit: 0,
              movable_assets_value: 0,
              esop_value: 0,
              esop_exercise_price: 0,
              esop_market_price: 0,
              other_perquisites: 0,
              total_perquisites: 0
            },
            separation_benefits: 0,
            gross_total_income: 1242000,
            total_deductions: 175000,
            taxable_income: 1067000,
            tax_before_relief: 75000,
            tax_relief: 0,
            tax_payable: 75000,
            advance_tax_paid: 0,
            tds_deducted: 72000,
            self_assessment_tax: 3000
          }
        ];
        setEmployees(mockEmployeeData);
        setFilteredEmployees(mockEmployeeData);
      } catch (error) {
        if (process.env.NODE_ENV === 'development') {
          // eslint-disable-next-line no-console
          console.error('Error fetching employees:', error);
        }
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
        emp.employee_id.toLowerCase().includes(searchTermLower) || 
        (emp.user_name && emp.user_name.toLowerCase().includes(searchTermLower))
      );
      setFilteredEmployees(filtered);
    }
  }, [searchTerm, employees]);

  // Handle view or edit actions
  const handleViewDeclaration = (empId: string): void => {
    navigate(`/api/v2/taxation/employee/${empId}`);
  };

  const handleEditDeclaration = (empId: string): void => {
    navigate(`/api/v2/taxation/declaration/${empId}`);
  };

  // Format currency
  const formatCurrency = (amount: number | undefined): string => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount || 0);
  };

  // Helper function to get color for filing status
  const getStatusColor = (status: FilingStatus | undefined): string => {
    switch (status?.toLowerCase()) {
      case 'draft': return '#e0e0e0';
      case 'filed': return '#bbdefb';
      case 'approved': return '#c8e6c9';
      case 'rejected': return '#ffcdd2';
      case 'pending': return '#fff9c4';
      default: return '#e0e0e0';
    }
  };

  // Handle search input change
  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setSearchTerm(event.target.value);
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
            onClick={() => navigate('/api/v2/taxation')}
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
          onChange={handleSearchChange}
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
                  <TableRow key={employee.employee_id}>
                    <TableCell>{employee.employee_id}</TableCell>
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
                        {employee.filing_status?.charAt(0)?.toUpperCase() + employee.filing_status?.slice(1) || 'N/A'}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Button 
                          variant="outlined" 
                          size="small" 
                          onClick={() => handleViewDeclaration(employee.employee_id)}
                        >
                          View
                        </Button>
                        <Button 
                          variant="contained" 
                          size="small" 
                          onClick={() => handleEditDeclaration(employee.employee_id)}
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
            onClick={() => navigate('/api/v2/taxation/declaration')}
          >
            Create New Declaration
          </Button>
        </Box>
      </Box>
    </PageLayout>
  );
};

export default EmployeeSelection; 