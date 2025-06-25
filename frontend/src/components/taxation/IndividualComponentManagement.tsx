import React, { useState, useEffect, useMemo } from 'react';
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
  TablePagination,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { 
  Search as SearchIcon,
  Refresh as RefreshIcon,
  Person as PersonIcon,
  Visibility as VisibilityIcon,
  ArrowBack as ArrowBackIcon,
  Settings as SettingsIcon,
  AccountBalance as AccountBalanceIcon,
  AddCircle as AddCircleIcon,
  Receipt as ReceiptIcon,
  Home as HomeIcon,
  TrendingUp as TrendingUpIcon,
  Work as WorkIcon,
  CarRental as CarRentalIcon,
  Business as BusinessIcon,
  Calculate as CalculateIcon
} from '@mui/icons-material';
import { getUserRole } from '../../shared/utils/auth';
import { UserRole } from '../../shared/types';
import { EmployeeSelectionDTO, EmployeeSelectionQuery, FilingStatus } from '../../shared/types/api';
import { useEmployeeSelection, useRefreshEmployeeSelection } from '../../shared/hooks/useEmployeeSelection';

interface EmployeeRecord extends EmployeeSelectionDTO {
  // Additional fields if needed
}

interface ToastState {
  show: boolean;
  message: string;
  severity: 'success' | 'error' | 'warning' | 'info';
}

interface ComponentOption {
  id: string;
  name: string;
  description: string;
  icon: React.ReactElement;
  color: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info';
  path: string;
}

// Helper function to get current tax year
const getCurrentTaxYear = (): string => {
  const currentDate = new Date();
  const currentYear = currentDate.getFullYear();
  const currentMonth = currentDate.getMonth() + 1; // getMonth() returns 0-11
  
  // Tax year starts from April 1st
  if (currentMonth >= 4) {
    return `${currentYear}-${(currentYear + 1).toString().slice(-2)}`;
  } else {
    return `${currentYear - 1}-${currentYear.toString().slice(-2)}`;
  }
};

// Helper function to generate available tax years (current + last 5 years)
const getAvailableTaxYears = (): string[] => {
  const currentTaxYear = getCurrentTaxYear();
  const yearParts = currentTaxYear.split('-');
  const currentStartYear = parseInt(yearParts[0] || '2024');
  const years: string[] = [];
  
  for (let i = 0; i <= 5; i++) {
    const startYear = currentStartYear - i;
    const endYear = startYear + 1;
    years.push(`${startYear}-${endYear.toString().slice(-2)}`);
  }
  
  return years;
};

// Component options for individual management
const getComponentOptions = (): ComponentOption[] => [
  {
    id: 'salary-update',
    name: 'Update Current Salary',
    description: 'Modify existing salary components and allowances',
    icon: <AccountBalanceIcon />,
    color: 'primary',
    path: '/taxation/component/salary'
  },
  {
    id: 'salary-new',
    name: 'Add New Salary Revision',
    description: 'Define new salary structure with increments',
    icon: <AddCircleIcon />,
    color: 'success',
    path: '/taxation/component/salary/new'
  },
  {
    id: 'perquisites',
    name: 'Perquisites',
    description: 'Accommodation, car, medical, LTA, ESOP benefits',
    icon: <CarRentalIcon />,
    color: 'secondary',
    path: '/taxation/component/perquisites'
  },
  {
    id: 'deductions',
    name: 'Deductions',
    description: 'Section 80C, 80D, 80G, 80E, 80TTA investments',
    icon: <ReceiptIcon />,
    color: 'info',
    path: '/taxation/component/deductions'
  },
  {
    id: 'house-property',
    name: 'House Property',
    description: 'Rental income, home loan interest, municipal taxes',
    icon: <HomeIcon />,
    color: 'warning',
    path: '/taxation/component/house-property'
  },
  {
    id: 'capital-gains',
    name: 'Capital Gains',
    description: 'STCG, LTCG on equity, debt, real estate',
    icon: <TrendingUpIcon />,
    color: 'info',
    path: '/taxation/component/capital-gains'
  },
  {
    id: 'retirement-benefits',
    name: 'Retirement Benefits',
    description: 'Gratuity, leave encashment, VRS, pension',
    icon: <WorkIcon />,
    color: 'primary',
    path: '/taxation/component/retirement-benefits'
  },
  {
    id: 'other-income',
    name: 'Other Income',
    description: 'Interest income, dividends, gifts, business income',
    icon: <BusinessIcon />,
    color: 'secondary',
    path: '/taxation/component/other-income'
  },
  {
    id: 'monthly-payroll',
    name: 'Monthly Payroll',
    description: 'Monthly salary projections with LWP calculations',
    icon: <CalculateIcon />,
    color: 'success',
    path: '/taxation/component/monthly-payroll'
  },
  {
    id: 'regime',
    name: 'Tax Regime',
    description: 'Old vs New regime selection and age',
    icon: <SettingsIcon />,
    color: 'warning',
    path: '/taxation/component/regime'
  }
];

/**
 * IndividualComponentManagement Component - Admin interface for managing individual taxation components
 */
const IndividualComponentManagement: React.FC = () => {
  const [filteredEmployees, setFilteredEmployees] = useState<EmployeeRecord[]>([]);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedTaxYear, setSelectedTaxYear] = useState<string>(getCurrentTaxYear());
  const [page, setPage] = useState<number>(0);
  const [rowsPerPage, setRowsPerPage] = useState<number>(10);
  const [toast, setToast] = useState<ToastState>({ 
    show: false, 
    message: '', 
    severity: 'success' 
  });
  const [componentDialogOpen, setComponentDialogOpen] = useState<boolean>(false);
  const [selectedEmployee, setSelectedEmployee] = useState<EmployeeRecord | null>(null);
  
  const navigate = useNavigate();
  const userRole: UserRole | null = getUserRole();
  
  // Check if selected year is current year
  const isCurrentYear = selectedTaxYear === getCurrentTaxYear();
  const availableTaxYears = getAvailableTaxYears();
  const componentOptions = getComponentOptions();
  
  // React Query hooks
  const query: EmployeeSelectionQuery = {
    skip: 0,
    limit: 100, // Get all employees for now
    tax_year: selectedTaxYear
  };
  
  const { 
    data: employeeResponse, 
    isLoading: loading, 
    error: queryError, 
    refetch 
  } = useEmployeeSelection(query);
  
  const refreshEmployeeSelection = useRefreshEmployeeSelection();
  
  // Transform API response to local format
  const employees: EmployeeRecord[] = useMemo(() => {
    const transformedEmployees = employeeResponse?.employees?.map(emp => ({
      ...emp,
      // Ensure all required fields are present with defaults
      user_name: emp.user_name || 'Unknown',
      email: emp.email || '',
      department: emp.department || 'N/A',
      role: emp.role || 'N/A',
      
      status: emp.status || 'active',
      joining_date: emp.joining_date || '',
      current_salary: emp.current_salary || 0,
      has_tax_record: emp.has_tax_record || false,
      tax_year: emp.tax_year || selectedTaxYear,
      filing_status: (emp.filing_status as FilingStatus) || 'pending',
      total_tax: emp.total_tax || 0,
      regime: emp.regime || 'new',
      last_updated: emp.last_updated || ''
    })) || [];
    
    return transformedEmployees;
  }, [employeeResponse?.employees, selectedTaxYear]);
  
  // Convert React Query error to string
  const error = queryError ? 'Failed to load employees data. Please try again later.' : null;

  // Helper functions
  const showToast = (message: string, severity: ToastState['severity'] = 'success'): void => {
    setToast({ show: true, message, severity });
  };

  const closeToast = (): void => {
    setToast(prev => ({ ...prev, show: false }));
  };

  // Redirect non-admin users
  useEffect(() => {
    if (userRole !== 'admin' && userRole !== 'superadmin') {
      navigate(`/taxation`);
    }
  }, [userRole, navigate]);

  // Show success toast when data loads successfully
  useEffect(() => {
    if (employeeResponse?.employees && !loading) {
      showToast(`Loaded ${employeeResponse.employees.length} employees for ${selectedTaxYear}`, 'success');
    }
  }, [employeeResponse, loading, selectedTaxYear]);

  // Show error toast when there's an error
  useEffect(() => {
    if (queryError) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Error fetching employees:', queryError);
      }
      showToast('Failed to load employees data. Please try again later.', 'error');
    }
  }, [queryError]);

  // Handle search with API integration
  useEffect(() => {
    if (searchTerm.trim() === '') {
      setFilteredEmployees(employees);
    } else {
      const searchTermLower = searchTerm.toLowerCase();
      const filtered = employees.filter(emp => 
        emp.employee_id.toLowerCase().includes(searchTermLower) || 
        (emp.user_name && emp.user_name.toLowerCase().includes(searchTermLower)) ||
        (emp.email && emp.email.toLowerCase().includes(searchTermLower)) ||
        (emp.department && emp.department.toLowerCase().includes(searchTermLower))
      );
      setFilteredEmployees(filtered);
    }
    setPage(0); // Reset to first page when searching
  }, [searchTerm, employees]);

  // Event handlers
  const handleViewComponents = (empId: string): void => {
    navigate(`/taxation/components-overview/${empId}?year=${selectedTaxYear}`);
  };

  const handleManageComponents = (employee: EmployeeRecord): void => {
    setSelectedEmployee(employee);
    setComponentDialogOpen(true);
  };

  const handleComponentSelect = (componentId: string): void => {
    if (selectedEmployee) {
      const component = componentOptions.find(c => c.id === componentId);
      if (component) {
        let finalPath = `${component.path}/${selectedEmployee.employee_id}?year=${selectedTaxYear}`;
        
        // Add mode parameter for salary income options
        if (componentId === 'salary-update') {
          finalPath += '&mode=update';
        } else if (componentId === 'salary-new') {
          finalPath += '&mode=new';
        }
        
        navigate(finalPath);
      }
    }
    setComponentDialogOpen(false);
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setSearchTerm(event.target.value);
  };

  const handleTaxYearChange = (event: SelectChangeEvent<string>): void => {
    const newTaxYear = event.target.value;
    setSelectedTaxYear(newTaxYear);
    setSearchTerm(''); // Clear search when changing year
    setPage(0); // Reset pagination
  };

  const handlePageChange = (_event: unknown, newPage: number): void => {
    setPage(newPage);
  };

  const handleRowsPerPageChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleRefresh = async (): Promise<void> => {
    try {
      await refetch();
      refreshEmployeeSelection(query);
      showToast(`Employee data refreshed for ${selectedTaxYear}`, 'success');
    } catch (error) {
      console.error('Error refreshing employees:', error);
      showToast('Failed to refresh employee data', 'error');
    }
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

  // Helper function to render tax regime chip
  const renderTaxRegimeChip = (regime: string | undefined): React.ReactElement => {
    const normalizedRegime = regime?.toLowerCase() || 'new';
    const isOldRegime = normalizedRegime === 'old';
    
    return (
      <Chip
        label={isOldRegime ? 'Old Regime' : 'New Regime'}
        color={isOldRegime ? 'secondary' : 'primary'}
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
            {searchTerm ? 'No employees found' : `No employees for ${selectedTaxYear}`}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {searchTerm 
              ? `No employees match "${searchTerm}" for ${selectedTaxYear}`
              : `No employee tax records available for ${selectedTaxYear}`
            }
          </Typography>
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
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '70vh' }}>
        <CircularProgress size={40} />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header Card */}
      <Card elevation={1} sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
            <Box>
              <Typography variant="h5" component="h1" gutterBottom>
                Individual Component Management
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Manage individual taxation components for employees - {selectedTaxYear}
                {!isCurrentYear && (
                  <Chip 
                    label="Previous Year - Read Only" 
                    color="warning" 
                    size="small" 
                    sx={{ ml: 1 }} 
                  />
                )}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
              <FormControl size="small" sx={{ minWidth: 140 }}>
                <InputLabel>Tax Year</InputLabel>
                <Select
                  value={selectedTaxYear}
                  label="Tax Year"
                  onChange={handleTaxYearChange}
                >
                  {availableTaxYears.map((year) => (
                    <MenuItem key={year} value={year}>
                      {year}
                      {year === getCurrentTaxYear() && ' (Current)'}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <Tooltip title="Refresh">
                <IconButton 
                  onClick={handleRefresh}
                  disabled={loading}
                  color="primary"
                >
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
              <Button 
                variant="outlined" 
                startIcon={<ArrowBackIcon />}
                onClick={() => navigate('/taxation')}
              >
                BACK TO DASHBOARD
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
              {filteredEmployees.length} employee{filteredEmployees.length !== 1 ? 's' : ''} for {selectedTaxYear}
            </Typography>
            {loading && <CircularProgress size={16} />}
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
                        {renderTaxRegimeChip(employee.regime)}
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" fontWeight="medium">
                          {formatCurrency(employee.total_tax)}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        {renderStatusChip(employee.filing_status as FilingStatus)}
                      </TableCell>
                      <TableCell align="center">
                        <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center' }}>
                          <Tooltip title="View Components">
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={() => handleViewComponents(employee.employee_id)}
                            >
                              <VisibilityIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Manage Components">
                            <IconButton
                              size="small"
                              color="secondary"
                              onClick={() => handleManageComponents(employee)}
                            >
                              <SettingsIcon fontSize="small" />
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

      {/* Component Selection Dialog */}
      <Dialog 
        open={componentDialogOpen} 
        onClose={() => setComponentDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <SettingsIcon color="primary" />
            <Typography variant="h6">
              Manage Components for {selectedEmployee?.user_name || selectedEmployee?.employee_id}
            </Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Select a component to manage for {selectedEmployee?.employee_id} for {selectedTaxYear}
          </Typography>
          <Grid container spacing={2}>
            {componentOptions.map((component) => (
              <Grid item xs={12} sm={6} md={4} key={component.id}>
                <Card 
                  variant="outlined" 
                  sx={{ 
                    cursor: 'pointer',
                    '&:hover': { 
                      borderColor: `${component.color}.main`,
                      backgroundColor: `${component.color}.50`
                    }
                  }}
                  onClick={() => handleComponentSelect(component.id)}
                >
                  <CardContent sx={{ textAlign: 'center', py: 2 }}>
                    <Box sx={{ color: `${component.color}.main`, mb: 1 }}>
                      {component.icon}
                    </Box>
                    <Typography variant="subtitle2" fontWeight="medium" gutterBottom>
                      {component.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {component.description}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setComponentDialogOpen(false)}>
            Cancel
          </Button>
        </DialogActions>
      </Dialog>

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
  );
};

export default IndividualComponentManagement; 