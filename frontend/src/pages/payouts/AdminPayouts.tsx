import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Alert,
  CircularProgress,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip,
  Avatar,
  Chip,
  InputAdornment,
  TablePagination,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  SelectChangeEvent
} from '@mui/material';
import {
  Search as SearchIcon,
  Calculate as CalculateIcon,
  Person as PersonIcon,
  MonetizationOn as MonetizationOnIcon,
  Close as CloseIcon,
  ExpandMore as ExpandMoreIcon
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';
import payoutService from '../../services/payoutService';
import dataService from '../../services/dataService';
import PageLayout from '../../layout/PageLayout';

// Type definitions
interface User {
  employee_id: string;
  name: string;
  email: string;
  department: string;
  designation: string;
  role: string;
  date_of_joining: string;
}

interface UsersResponse {
  users: User[];
  total: number;
}

interface CalculatedPayout {
  employee_id: string;
  basic_salary: number;
  da: number;
  hra: number;
  special_allowance: number;
  bonus: number;
  transport_allowance: number;
  medical_allowance: number;
  other_allowances: number;
  reimbursements: number;
  epf_employee: number;
  esi_employee: number;
  professional_tax: number;
  tds: number;
  advance_deduction: number;
  loan_deduction: number;
  other_deductions: number;
  gross_salary: number;
  total_deductions: number;
  net_salary: number;
  tax_regime: string;
  annual_tax_liability: number;
  pay_period_start: string;
  pay_period_end: string;
}

interface YearOption {
  value: number;
  label: string;
}

interface MonthOption {
  value: number;
  label: string;
}

type ChipColor = 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning';

const AdminPayouts: React.FC = () => {
  const theme = useTheme();
  const [loading, setLoading] = useState<boolean>(false);
  const [usersLoading, setUsersLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [filteredUsers, setFilteredUsers] = useState<User[]>([]);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedMonth, setSelectedMonth] = useState<number>(new Date().getMonth() + 1);
  const [selectedYear, setSelectedYear] = useState<number>(new Date().getFullYear());
  const [calculationDialogOpen, setCalculationDialogOpen] = useState<boolean>(false);
  const [selectedEmployee, setSelectedEmployee] = useState<User | null>(null);
  const [calculatedPayout, setCalculatedPayout] = useState<CalculatedPayout | null>(null);
  const [calculating, setCalculating] = useState<boolean>(false);

  // Pagination
  const [page, setPage] = useState<number>(0);
  const [rowsPerPage, setRowsPerPage] = useState<number>(10);

  // State for calculated payouts
  const [calculatedPayouts] = useState<CalculatedPayout[]>([]);
  const [totalPayoutAmount] = useState<number>(0);

  // Generate year options for the last 3 years and next year
  const yearOptions: YearOption[] = Array.from({ length: 4 }, (_, i) => {
    const year = new Date().getFullYear() - 1 + i;
    return { value: year, label: year.toString() };
  });

  // Month options
  const monthOptions: MonthOption[] = Array.from({ length: 12 }, (_, i) => ({
    value: i + 1,
    label: new Date(0, i).toLocaleString('default', { month: 'long' })
  }));

  useEffect(() => {
    loadUsers();
  }, []);

  const filterUsers = useCallback((): void => {
    if (!searchTerm.trim()) {
      setFilteredUsers(users);
      return;
    }

    const searchLower = searchTerm.toLowerCase();
    const filtered = users.filter(user => 
      user.employee_id?.toLowerCase().includes(searchLower) ||
      user.name?.toLowerCase().includes(searchLower) ||
      user.email?.toLowerCase().includes(searchLower) ||
      user.department?.toLowerCase().includes(searchLower) ||
      user.designation?.toLowerCase().includes(searchLower)
    );
    setFilteredUsers(filtered);
    setPage(0); // Reset to first page when filtering
  }, [searchTerm, users]);

  useEffect(() => {
    filterUsers();
  }, [filterUsers]);

  const loadUsers = async (): Promise<void> => {
    setUsersLoading(true);
    setError(null);
    
    try {
      const response: UsersResponse = await dataService.getUsers(0, 1000); // Get a large number of users
      setUsers(response.users || []);
    } catch (err) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error loading users:', err);
      }
      setError('Failed to load users. Please try again.');
    } finally {
      setUsersLoading(false);
    }
  };

  const handleCalculateSalary = (employee: User): void => {
    setSelectedEmployee(employee);
    setCalculatedPayout(null);
    setCalculationDialogOpen(true);
  };

  const calculateMonthlySalary = async (): Promise<void> => {
    if (!selectedEmployee) return;

    setCalculating(true);
    try {
      const payoutData: CalculatedPayout = await payoutService.calculateMonthlyPayout(
        selectedEmployee.employee_id,
        selectedMonth,
        selectedYear
      );
      setCalculatedPayout(payoutData);
    } catch (err) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error calculating salary:', err);
      }
      setError('Failed to calculate monthly salary. Please try again.');
    } finally {
      setCalculating(false);
    }
  };

  const handleCloseCalculationDialog = (): void => {
    setCalculationDialogOpen(false);
    setSelectedEmployee(null);
    setCalculatedPayout(null);
  };

  const createPayout = async (): Promise<void> => {
    if (!calculatedPayout) return;

    try {
      setLoading(true);
      await payoutService.createPayout(calculatedPayout);
      setError(null);
      // Show success message (you might want to add a success state)
      handleCloseCalculationDialog();
    } catch (err) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error creating payout:', err);
      }
      setError('Failed to create payout. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getInitials = (name?: string): string => {
    if (!name) return 'U';
    return name.split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getRoleBadgeColor = (role?: string): ChipColor => {
    switch (role?.toLowerCase()) {
      case 'admin': return 'error';
      case 'superadmin': return 'secondary';
      case 'manager': return 'warning';
      case 'hr': return 'info';
      default: return 'primary';
    }
  };

  const formatDate = (dateString?: string): string => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setSearchTerm(event.target.value);
  };

  const handleMonthChange = (event: SelectChangeEvent<number>): void => {
    setSelectedMonth(event.target.value as number);
  };

  const handleYearChange = (event: SelectChangeEvent<number>): void => {
    setSelectedYear(event.target.value as number);
  };

  const handlePageChange = (_event: unknown, newPage: number): void => {
    setPage(newPage);
  };

  const handleRowsPerPageChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleCalculatePayouts = async (): Promise<void> => {
    setCalculating(true);
    setError(null);
    
    try {
      // For now, we'll just show a message that bulk calculation is not implemented
      setError('Bulk payout calculation feature is not yet implemented. Please calculate individual payouts.');
    } catch (err) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error calculating payouts:', err);
      }
      setError('Failed to calculate payouts. Please try again.');
    } finally {
      setCalculating(false);
    }
  };

  const renderCalculationDialog = (): React.ReactElement | null => {
    if (!selectedEmployee) return null;

    return (
      <Dialog 
        open={calculationDialogOpen} 
        onClose={handleCloseCalculationDialog}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: { minHeight: '60vh' }
        }}
      >
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">
              Calculate Monthly Salary - {selectedEmployee.name}
            </Typography>
            <IconButton onClick={handleCloseCalculationDialog}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        
        <DialogContent dividers>
          {/* Employee Info */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Avatar sx={{ bgcolor: theme.palette.primary.main, mr: 2 }}>
                  {getInitials(selectedEmployee.name)}
                </Avatar>
                <Box>
                  <Typography variant="h6">{selectedEmployee.name}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {selectedEmployee.employee_id} • {selectedEmployee.designation || 'N/A'}
                  </Typography>
                </Box>
              </Box>
              <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
                <Box>
                  <Typography variant="body2"><strong>Department:</strong> {selectedEmployee.department || 'N/A'}</Typography>
                </Box>
                <Box>
                  <Typography variant="body2"><strong>Email:</strong> {selectedEmployee.email || 'N/A'}</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>

          {/* Period Selection */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>Calculation Period</Typography>
              <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
                <FormControl fullWidth>
                  <InputLabel>Month</InputLabel>
                  <Select
                    value={selectedMonth}
                    label="Month"
                    onChange={handleMonthChange}
                  >
                    {monthOptions.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
                <FormControl fullWidth>
                  <InputLabel>Year</InputLabel>
                  <Select
                    value={selectedYear}
                    label="Year"
                    onChange={handleYearChange}
                  >
                    {yearOptions.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Box>
              <Box mt={2}>
                <Button
                  variant="contained"
                  startIcon={calculating ? <CircularProgress size={20} /> : <CalculateIcon />}
                  onClick={calculateMonthlySalary}
                  disabled={calculating}
                  fullWidth
                >
                  {calculating ? 'Calculating...' : 'Calculate Monthly Salary'}
                </Button>
              </Box>
            </CardContent>
          </Card>

          {/* Calculation Results */}
          {calculatedPayout && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Calculation Results</Typography>
                
                {/* Summary */}
                <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 3, mb: 3 }}>
                  <Box textAlign="center" p={2} bgcolor={theme.palette.success.light} borderRadius={1}>
                    <Typography variant="h5" color="success.dark" fontWeight="bold">
                      {payoutService.formatCurrency(calculatedPayout.gross_salary)}
                    </Typography>
                    <Typography variant="body2" color="success.dark">
                      Gross Salary
                    </Typography>
                  </Box>
                  <Box textAlign="center" p={2} bgcolor={theme.palette.error.light} borderRadius={1}>
                    <Typography variant="h5" color="error.dark" fontWeight="bold">
                      {payoutService.formatCurrency(calculatedPayout.total_deductions)}
                    </Typography>
                    <Typography variant="body2" color="error.dark">
                      Total Deductions
                    </Typography>
                  </Box>
                  <Box textAlign="center" p={2} bgcolor={theme.palette.primary.light} borderRadius={1}>
                    <Typography variant="h5" color="primary.dark" fontWeight="bold">
                      {payoutService.formatCurrency(calculatedPayout.net_salary)}
                    </Typography>
                    <Typography variant="body2" color="primary.dark">
                      Net Salary
                    </Typography>
                  </Box>
                </Box>

                {/* Detailed Breakdown */}
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="subtitle1" fontWeight="bold">
                      Detailed Breakdown
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
                      {/* Earnings */}
                      <Box>
                        <Typography variant="h6" color="success.main" gutterBottom>
                          Earnings
                        </Typography>
                        <List dense>
                          {calculatedPayout.basic_salary > 0 && (
                            <ListItem sx={{ px: 0 }}>
                              <ListItemText 
                                primary="Basic Salary"
                                secondary={payoutService.formatCurrency(calculatedPayout.basic_salary)}
                              />
                            </ListItem>
                          )}
                          {calculatedPayout.da > 0 && (
                            <ListItem sx={{ px: 0 }}>
                              <ListItemText 
                                primary="Dearness Allowance"
                                secondary={payoutService.formatCurrency(calculatedPayout.da)}
                              />
                            </ListItem>
                          )}
                          {calculatedPayout.hra > 0 && (
                            <ListItem sx={{ px: 0 }}>
                              <ListItemText 
                                primary="House Rent Allowance"
                                secondary={payoutService.formatCurrency(calculatedPayout.hra)}
                              />
                            </ListItem>
                          )}
                          {calculatedPayout.special_allowance > 0 && (
                            <ListItem sx={{ px: 0 }}>
                              <ListItemText 
                                primary="Special Allowance"
                                secondary={payoutService.formatCurrency(calculatedPayout.special_allowance)}
                              />
                            </ListItem>
                          )}
                          {calculatedPayout.bonus > 0 && (
                            <ListItem sx={{ px: 0 }}>
                              <ListItemText 
                                primary="Bonus"
                                secondary={payoutService.formatCurrency(calculatedPayout.bonus)}
                              />
                            </ListItem>
                          )}
                        </List>
                      </Box>

                      {/* Deductions */}
                      <Box>
                        <Typography variant="h6" color="error.main" gutterBottom>
                          Deductions
                        </Typography>
                        <List dense>
                          {calculatedPayout.epf_employee > 0 && (
                            <ListItem sx={{ px: 0 }}>
                              <ListItemText 
                                primary="Employee PF"
                                secondary={payoutService.formatCurrency(calculatedPayout.epf_employee)}
                              />
                            </ListItem>
                          )}
                          {calculatedPayout.esi_employee > 0 && (
                            <ListItem sx={{ px: 0 }}>
                              <ListItemText 
                                primary="Employee ESI"
                                secondary={payoutService.formatCurrency(calculatedPayout.esi_employee)}
                              />
                            </ListItem>
                          )}
                          {calculatedPayout.professional_tax > 0 && (
                            <ListItem sx={{ px: 0 }}>
                              <ListItemText 
                                primary="Professional Tax"
                                secondary={payoutService.formatCurrency(calculatedPayout.professional_tax)}
                              />
                            </ListItem>
                          )}
                          {calculatedPayout.tds > 0 && (
                            <ListItem sx={{ px: 0 }}>
                              <ListItemText 
                                primary="TDS"
                                secondary={payoutService.formatCurrency(calculatedPayout.tds)}
                              />
                            </ListItem>
                          )}
                        </List>
                      </Box>
                    </Box>
                  </AccordionDetails>
                </Accordion>

                {/* Tax Information */}
                <Box mt={2} p={2} bgcolor={theme.palette.grey[100]} borderRadius={1}>
                  <Typography variant="subtitle2" gutterBottom>Tax Information</Typography>
                  <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
                    <Box>
                      <Typography variant="body2">
                        <strong>Tax Regime:</strong> {calculatedPayout.tax_regime?.toUpperCase() || 'NEW'}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="body2">
                        <strong>Annual Tax Liability:</strong> {payoutService.formatCurrency(calculatedPayout.annual_tax_liability)}
                      </Typography>
                    </Box>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          )}
        </DialogContent>
        
        <DialogActions>
          {calculatedPayout && (
            <Button 
              variant="contained" 
              color="primary"
              startIcon={loading ? <CircularProgress size={20} /> : <MonetizationOnIcon />}
              onClick={createPayout}
              disabled={loading}
            >
              {loading ? 'Creating...' : 'Create Payout'}
            </Button>
          )}
          <Button variant="outlined" onClick={handleCloseCalculationDialog}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    );
  };

  const renderUsersTable = (): React.ReactElement => {
    const startIndex = page * rowsPerPage;
    const displayedUsers = filteredUsers.slice(startIndex, startIndex + rowsPerPage);

    if (usersLoading) {
      return (
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      );
    }

    if (displayedUsers.length === 0) {
      return (
        <Box textAlign="center" p={4}>
          <PersonIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            {searchTerm ? 'No users found' : 'No users available'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {searchTerm ? `No users match "${searchTerm}"` : 'Add users to calculate payouts'}
          </Typography>
        </Box>
      );
    }

    return (
      <>
        <TableContainer component={Paper} variant="outlined">
          <Table>
            <TableHead>
              <TableRow sx={{ 
                '& .MuiTableCell-head': { 
                  backgroundColor: 'primary.main',
                  color: 'white',
                  fontWeight: 'bold'
                }
              }}>
                <TableCell>Employee</TableCell>
                <TableCell>Department</TableCell>
                <TableCell>Role</TableCell>
                <TableCell>Joining Date</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {displayedUsers.map((user) => (
                <TableRow key={user.employee_id} hover>
                  <TableCell>
                    <Box display="flex" alignItems="center">
                      <Avatar sx={{ bgcolor: theme.palette.primary.main, mr: 2, width: 40, height: 40 }}>
                        {getInitials(user.name)}
                      </Avatar>
                      <Box>
                        <Typography variant="subtitle2" fontWeight="bold">
                          {user.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {user.employee_id}
                        </Typography>
                        {user.designation && (
                          <Typography variant="caption" color="text.secondary">
                            {user.designation}
                          </Typography>
                        )}
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {user.department || 'N/A'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={user.role || 'User'}
                      color={getRoleBadgeColor(user.role)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {formatDate(user.date_of_joining)}
                    </Typography>
                  </TableCell>
                  <TableCell align="center">
                    <Tooltip title="Calculate Monthly Salary">
                      <Button
                        variant="contained"
                        size="small"
                        startIcon={<CalculateIcon />}
                        onClick={() => handleCalculateSalary(user)}
                        sx={{ minWidth: 140 }}
                      >
                        Calculate
                      </Button>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        <TablePagination
          component="div"
          count={filteredUsers.length}
          page={page}
          onPageChange={handlePageChange}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={handleRowsPerPageChange}
          rowsPerPageOptions={[5, 10, 25, 50]}
        />
      </>
    );
  };

  return (
    <PageLayout title="Admin Payouts">
      <Typography variant="h4" gutterBottom>
        Employee Salary Calculator
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Calculate monthly salary for any employee and create payouts.
      </Typography>
      
      {/* Summary Cards */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(3, 1fr)' }, gap: 3, mb: 3 }}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" mb={2}>
              <PersonIcon sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6">Total Employees</Typography>
            </Box>
            <Typography variant="h3" color="primary.main" fontWeight="bold">
              {users.length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Active employees
            </Typography>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" mb={2}>
              <CalculateIcon sx={{ mr: 1, color: 'success.main' }} />
              <Typography variant="h6">Calculated Payouts</Typography>
            </Box>
            <Typography variant="h3" color="success.main" fontWeight="bold">
              {calculatedPayouts.length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              For {monthOptions.find(m => m.value === selectedMonth)?.label} {selectedYear}
            </Typography>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" mb={2}>
              <MonetizationOnIcon sx={{ mr: 1, color: 'warning.main' }} />
              <Typography variant="h6">Total Payout</Typography>
            </Box>
            <Typography variant="h3" color="warning.main" fontWeight="bold">
              {payoutService.formatCurrency(totalPayoutAmount)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Net amount to be paid
            </Typography>
          </CardContent>
        </Card>
      </Box>

      {/* Filters and Actions */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(4, 1fr)' }, gap: 2, alignItems: 'center' }}>
            <TextField
              fullWidth
              placeholder="Search employees..."
              value={searchTerm}
              onChange={handleSearchChange}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
            <FormControl fullWidth>
              <InputLabel>Year</InputLabel>
              <Select
                value={selectedYear}
                label="Year"
                onChange={handleYearChange}
              >
                {yearOptions.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl fullWidth>
              <InputLabel>Month</InputLabel>
              <Select
                value={selectedMonth}
                label="Month"
                onChange={handleMonthChange}
              >
                {monthOptions.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <Button
              fullWidth
              variant="contained"
              startIcon={calculating ? <CircularProgress size={20} /> : <CalculateIcon />}
              onClick={handleCalculatePayouts}
              disabled={calculating}
            >
              {calculating ? 'Calculating...' : 'Calculate Payouts'}
            </Button>
          </Box>
        </CardContent>
      </Card>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Users List */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Employee List
          </Typography>
          {renderUsersTable()}
        </CardContent>
      </Card>

      {/* Calculation Dialog */}
      {renderCalculationDialog()}
    </PageLayout>
  );
};

export default AdminPayouts; 