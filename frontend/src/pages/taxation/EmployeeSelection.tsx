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
  InputAdornment,
  Card,
  CardContent,
  Skeleton,
  Tooltip,
  IconButton,
  Fade,
  Snackbar,
  Chip,
  TablePagination
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { 
  Search as SearchIcon,
  Refresh as RefreshIcon,
  Person as PersonIcon,
  Add as AddIcon,
  Visibility as VisibilityIcon,
  Edit as EditIcon,
  ArrowBack as ArrowBackIcon
} from '@mui/icons-material';
import { getUserRole } from '../../shared/utils/auth';
import PageLayout from '../../layout/PageLayout';
import { TaxationData, UserRole, FilingStatus } from '../../shared/types';

interface EmployeeRecord extends TaxationData {
  user_name?: string;
  total_tax: number;
}

interface ToastState {
  show: boolean;
  message: string;
  severity: 'success' | 'error' | 'warning' | 'info';
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
  const [page, setPage] = useState<number>(0);
  const [rowsPerPage, setRowsPerPage] = useState<number>(10);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [toast, setToast] = useState<ToastState>({ 
    show: false, 
    message: '', 
    severity: 'success' 
  });
  
  const navigate = useNavigate();
  const userRole: UserRole | null = getUserRole();

  // Helper functions
  const showToast = (message: string, severity: ToastState['severity'] = 'success'): void => {
    setToast({ show: true, message, severity });
  };

  const closeToast = (): void => {
    setToast(prev => ({ ...prev, show: false }));
  };

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
        setError(null);
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
          },
          {
            employee_id: 'EMP003',
            user_name: 'Mike Johnson',
            tax_year: '2023-24',
            regime: 'new',
            total_tax: 25000,
            filing_status: 'draft',
            basic_salary: 450000,
            hra: 180000,
            da: 0,
            medical_allowance: 15000,
            transport_allowance: 12000,
            other_allowances: 8000,
            bonus: 30000,
            pf_employee: 21600,
            esi_employee: 0,
            professional_tax: 2400,
            tds: 24000,
            other_income: 0,
            house_property_income: 0,
            capital_gains: 0,
            section_80c: 100000,
            section_80d: 15000,
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
            gross_total_income: 695000,
            total_deductions: 115000,
            taxable_income: 580000,
            tax_before_relief: 25000,
            tax_relief: 0,
            tax_payable: 25000,
            advance_tax_paid: 0,
            tds_deducted: 24000,
            self_assessment_tax: 1000
          }
        ];
        setEmployees(mockEmployeeData);
        setFilteredEmployees(mockEmployeeData);
        showToast('Employee data loaded successfully', 'success');
      } catch (error) {
        if (process.env.NODE_ENV === 'development') {
          // eslint-disable-next-line no-console
          console.error('Error fetching employees:', error);
        }
        const errorMessage = 'Failed to load employees data. Please try again later.';
        setError(errorMessage);
        showToast(errorMessage, 'error');
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
    setPage(0); // Reset to first page when searching
  }, [searchTerm, employees]);

  // Event handlers
  const handleViewDeclaration = (empId: string): void => {
    navigate(`/api/v2/taxation/employee/${empId}`);
  };

  const handleEditDeclaration = (empId: string): void => {
    navigate(`/api/v2/taxation/declaration/${empId}`);
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setSearchTerm(event.target.value);
  };

  const handlePageChange = (_event: unknown, newPage: number): void => {
    setPage(newPage);
  };

  const handleRowsPerPageChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleRefresh = (): void => {
    setRefreshing(true);
    // Simulate refresh
    setTimeout(() => {
      setRefreshing(false);
      showToast('Data refreshed successfully', 'success');
    }, 1000);
  };

  // Format currency
  const formatCurrency = (amount: number | undefined): string => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount || 0);
  };

  // Helper function to get status chip
  const renderStatusChip = (status: FilingStatus | undefined): React.ReactElement => {
    const getStatusProps = (status: FilingStatus | undefined) => {
      switch (status?.toLowerCase()) {
        case 'filed': return { color: 'success' as const, label: 'Filed' };
        case 'approved': return { color: 'success' as const, label: 'Approved' };
        case 'pending': return { color: 'warning' as const, label: 'Pending' };
        case 'draft': return { color: 'default' as const, label: 'Draft' };
        case 'rejected': return { color: 'error' as const, label: 'Rejected' };
        default: return { color: 'default' as const, label: 'N/A' };
      }
    };

    const { color, label } = getStatusProps(status);
    return (
      <Chip
        label={label}
        color={color}
        size="small"
        variant="outlined"
      />
    );
  };

  // Render table skeleton
  const renderTableSkeleton = (): React.ReactElement[] => (
    Array.from({ length: rowsPerPage }).map((_, index) => (
      <TableRow key={index}>
        <TableCell><Skeleton /></TableCell>
        <TableCell><Skeleton /></TableCell>
        <TableCell><Skeleton /></TableCell>
        <TableCell><Skeleton /></TableCell>
        <TableCell><Skeleton /></TableCell>
        <TableCell><Skeleton /></TableCell>
        <TableCell><Skeleton width={120} /></TableCell>
      </TableRow>
    ))
  );

  // Render empty state
  const renderEmptyState = (): React.ReactElement => (
    <TableRow>
      <TableCell colSpan={7} align="center" sx={{ py: 6 }}>
        <Box sx={{ textAlign: 'center' }}>
          <PersonIcon 
            sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} 
          />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            {searchTerm ? 'No employees found' : 'No employees yet'}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {searchTerm 
              ? `No employees match "${searchTerm}"`
              : 'No employee tax records available'
            }
          </Typography>
          {!searchTerm && (
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => navigate('/api/v2/taxation/declaration')}
            >
              Create New Declaration
            </Button>
          )}
        </Box>
      </TableCell>
    </TableRow>
  );

  // Get paginated data
  const paginatedEmployees = filteredEmployees.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  if (loading) {
    return (
      <PageLayout title="Employee Selection">
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '70vh' }}>
          <CircularProgress size={40} />
        </Box>
      </PageLayout>
    );
  }

  return (
    <PageLayout title="Employee Selection">
      <Box>
        {/* Header Card */}
        <Card elevation={1} sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
              <Box>
                <Typography variant="h5" component="h1" gutterBottom>
                  Employee Tax Declaration Management
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Select employees to view or manage their tax declarations
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                <Tooltip title="Refresh">
                  <IconButton 
                    onClick={handleRefresh}
                    disabled={refreshing}
                    color="primary"
                  >
                    <RefreshIcon />
                  </IconButton>
                </Tooltip>
                <Button 
                  variant="outlined" 
                  startIcon={<ArrowBackIcon />}
                  onClick={() => navigate('/api/v2/taxation')}
                >
                  BACK TO DASHBOARD
                </Button>
                <Button 
                  variant="contained" 
                  startIcon={<AddIcon />} 
                  onClick={() => navigate('/api/v2/taxation/declaration')}
                >
                  NEW DECLARATION
                </Button>
              </Box>
            </Box>
          </CardContent>
        </Card>

        {/* Search and Filters */}
        <Paper elevation={1} sx={{ p: 2, mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
            <TextField
              sx={{ minWidth: 300, flexGrow: 1, maxWidth: 500 }}
              label="Search employees"
              variant="outlined"
              size="small"
              value={searchTerm}
              onChange={handleSearchChange}
              placeholder="Search by Employee ID or Name..."
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon color="action" />
                  </InputAdornment>
                ),
              }}
            />
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="body2" color="text.secondary">
                {filteredEmployees.length} employee{filteredEmployees.length !== 1 ? 's' : ''}
              </Typography>
              {refreshing && <CircularProgress size={16} />}
            </Box>
          </Box>
        </Paper>

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Table */}
        <Paper elevation={1}>
          <TableContainer>
            <Table stickyHeader>
              <TableHead>
                <TableRow sx={{ 
                  '& .MuiTableCell-head': { 
                    backgroundColor: 'primary.main',
                    color: 'white',
                    fontWeight: 'bold',
                    fontSize: '0.875rem'
                  }
                }}>
                  <TableCell>Employee ID</TableCell>
                  <TableCell>Employee Name</TableCell>
                  <TableCell>Tax Year</TableCell>
                  <TableCell>Tax Regime</TableCell>
                  <TableCell align="right">Total Tax</TableCell>
                  <TableCell align="center">Filing Status</TableCell>
                  <TableCell align="center">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  renderTableSkeleton()
                ) : paginatedEmployees.length > 0 ? (
                  paginatedEmployees.map((employee) => (
                    <Fade in key={employee.employee_id} timeout={300}>
                      <TableRow 
                        hover
                        sx={{ 
                          '&:hover': { 
                            backgroundColor: 'action.hover' 
                          }
                        }}
                      >
                        <TableCell>
                          <Typography variant="subtitle2" fontWeight="medium">
                            {employee.employee_id}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Box>
                            <Typography variant="body2" fontWeight="medium">
                              {employee.user_name || 'Unknown'}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {employee.tax_year || 'N/A'}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={employee.regime === 'old' ? 'Old Regime' : 'New Regime'}
                            color={employee.regime === 'old' ? 'secondary' : 'primary'}
                            size="small"
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" fontWeight="medium">
                            {formatCurrency(employee.total_tax)}
                          </Typography>
                        </TableCell>
                        <TableCell align="center">
                          {renderStatusChip(employee.filing_status)}
                        </TableCell>
                        <TableCell align="center">
                          <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center' }}>
                            <Tooltip title="View Declaration">
                              <IconButton
                                size="small"
                                color="primary"
                                onClick={() => handleViewDeclaration(employee.employee_id)}
                              >
                                <VisibilityIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Edit Declaration">
                              <IconButton
                                size="small"
                                color="secondary"
                                onClick={() => handleEditDeclaration(employee.employee_id)}
                              >
                                <EditIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        </TableCell>
                      </TableRow>
                    </Fade>
                  ))
                ) : (
                  renderEmptyState()
                )}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Pagination */}
          {filteredEmployees.length > 0 && (
            <TablePagination
              component="div"
              count={filteredEmployees.length}
              page={page}
              onPageChange={handlePageChange}
              rowsPerPage={rowsPerPage}
              onRowsPerPageChange={handleRowsPerPageChange}
              rowsPerPageOptions={[5, 10, 25, 50]}
              showFirstButton
              showLastButton
            />
          )}
        </Paper>

        {/* Toast Notifications */}
        <Snackbar
          open={toast.show}
          autoHideDuration={6000}
          onClose={closeToast}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <Alert 
            onClose={closeToast} 
            severity={toast.severity}
            sx={{ width: '100%' }}
            variant="filled"
          >
            {toast.message}
          </Alert>
        </Snackbar>
      </Box>
    </PageLayout>
  );
};

export default EmployeeSelection; 