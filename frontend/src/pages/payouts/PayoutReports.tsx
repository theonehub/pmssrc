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
  Divider,
  IconButton,
  Tooltip,
  Avatar,
  Chip,
  InputAdornment,
  TablePagination,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  SelectChangeEvent
} from '@mui/material';
import {
  Search as SearchIcon,
  Download as DownloadIcon,
  Email as EmailIcon,
  Visibility as VisibilityIcon,
  Receipt as ReceiptIcon,
  Person as PersonIcon,
  Assessment as AssessmentIcon,
  Send as SendIcon,
  GetApp as GetAppIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';
import payoutService from '../../services/payoutService';
import dataService from '../../services/dataService';
import PageLayout from '../../layout/PageLayout';

// Type definitions
interface Payout {
  id: string;
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
  pay_period_start: string;
  pay_period_end: string;
  payout_date: string;
  status: string;
}

interface Employee {
  emp_id: string;
  name: string;
  email: string;
  department: string;
  designation: string;
  role: string;
  doj: string;
  payout?: Payout | undefined;
  hasPayslip: boolean;
}

interface PayslipData {
  company_name: string;
  company_address: string;
  employee_name: string;
  employee_code: string;
  department: string;
  designation: string;
  pay_period: string;
  payout_date: string;
  days_in_month: number;
  days_worked: number;
  earnings: Record<string, number>;
  deductions: Record<string, number>;
  total_earnings: number;
  total_deductions: number;
  net_pay: number;
  ytd_gross: number;
  ytd_tax_deducted: number;
  tax_regime: string;
  pan_number: string;
  uan_number: string;
}

interface BulkResult {
  employee_id: string;
  employee_name: string;
  success: boolean;
  error?: string;
}

interface BulkResults {
  total: number;
  successful: number;
  failed: number;
  results: BulkResult[];
}

interface YearOption {
  value: number;
  label: string;
}

interface MonthOption {
  value: number;
  label: string;
}

interface UsersResponse {
  users: Employee[];
  total: number;
}

const PayoutReports: React.FC = () => {
  const theme = useTheme();
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState<number>(0);
  
  // Employee payslips data
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [filteredEmployees, setFilteredEmployees] = useState<Employee[]>([]);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedYear, setSelectedYear] = useState<number>(new Date().getFullYear());
  const [selectedMonth, setSelectedMonth] = useState<number>(new Date().getMonth() + 1);
  
  // Bulk operations
  const [bulkLoading, setBulkLoading] = useState<boolean>(false);
  const [bulkResults, setBulkResults] = useState<BulkResults | null>(null);
  const [bulkDialogOpen, setBulkDialogOpen] = useState<boolean>(false);
  
  // Payslip viewing
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);
  const [payslipData, setPayslipData] = useState<PayslipData | null>(null);
  const [payslipDialogOpen, setPayslipDialogOpen] = useState<boolean>(false);
  const [downloadLoading, setDownloadLoading] = useState<string | null>(null);
  const [emailLoading, setEmailLoading] = useState<string | null>(null);
  
  // Pagination
  const [page, setPage] = useState<number>(0);
  const [rowsPerPage, setRowsPerPage] = useState<number>(10);

  // Generate year options
  const yearOptions: YearOption[] = Array.from({ length: 5 }, (_, i) => {
    const year = new Date().getFullYear() - i;
    return { value: year, label: year.toString() };
  });

  // Month options
  const monthOptions: MonthOption[] = Array.from({ length: 12 }, (_, i) => ({
    value: i + 1,
    label: new Date(0, i).toLocaleString('default', { month: 'long' })
  }));

  const loadEmployeesWithPayouts = useCallback(async (): Promise<void> => {
    setLoading(true);
    setError(null);
    
    try {
      // Get all users
      const usersResponse: UsersResponse = await dataService.getUsers(0, 1000);
      const allUsers = usersResponse.users || [];
      
      // Get monthly payouts
      const payouts: Payout[] = await payoutService.getMonthlyPayouts(selectedYear, selectedMonth);
      
      // Combine user data with payout data
      const employeesWithPayouts: Employee[] = allUsers.map(user => {
        const userPayouts = payouts.filter(payout => payout.employee_id === user.emp_id);
        const latestPayout = userPayouts.length > 0 ? userPayouts[0] : undefined;
        
        return {
          ...user,
          payout: latestPayout,
          hasPayslip: latestPayout ? ['processed', 'approved', 'paid'].includes(latestPayout.status) : false
        };
      });
      
      setEmployees(employeesWithPayouts);
    } catch (err) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error loading employees with payouts:', err);
      }
      setError('Failed to load employee payouts. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [selectedYear, selectedMonth]);

  const filterEmployees = useCallback((): void => {
    if (!searchTerm) {
      setFilteredEmployees(employees);
      return;
    }

    const filtered = employees.filter(employee =>
      employee.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      employee.emp_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      employee.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      employee.department?.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredEmployees(filtered);
  }, [searchTerm, employees]);

  useEffect(() => {
    loadEmployeesWithPayouts();
  }, [loadEmployeesWithPayouts]);

  useEffect(() => {
    filterEmployees();
  }, [filterEmployees]);

  const handleViewPayslip = async (employee: Employee): Promise<void> => {
    if (!employee.payout) {
      setError('No payout found for this employee');
      return;
    }

    try {
      setSelectedEmployee(employee);
      setPayslipDialogOpen(true);
      
      // Load payslip data
      const data: PayslipData = await payoutService.getPayslipData(employee.payout.id);
      setPayslipData(data);
      
    } catch (err) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error loading payslip data:', err);
      }
      setError('Failed to load payslip details. Please try again.');
      setPayslipDialogOpen(false);
    }
  };

  const handleDownloadPayslip = async (employee: Employee): Promise<void> => {
    if (!employee.payout) {
      setError('No payout found for this employee');
      return;
    }

    try {
      setDownloadLoading(employee.emp_id);
      await payoutService.downloadPayslip(employee.payout.id);
      setSuccess(`Payslip downloaded for ${employee.name}`);
    } catch (err) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error downloading payslip:', err);
      }
      setError('Failed to download payslip. Please try again.');
    } finally {
      setDownloadLoading(null);
    }
  };

  const handleEmailPayslip = async (employee: Employee): Promise<void> => {
    if (!employee.payout) {
      setError('No payout found for this employee');
      return;
    }

    try {
      setEmailLoading(employee.emp_id);
      await payoutService.emailPayslip(employee.payout.id);
      setSuccess(`Payslip emailed to ${employee.name}`);
    } catch (err) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error emailing payslip:', err);
      }
      setError('Failed to email payslip. Please try again.');
    } finally {
      setEmailLoading(null);
    }
  };

  const handleBulkGenerate = async (): Promise<void> => {
    setBulkLoading(true);
    try {
      const eligibleEmployees = employees.filter(emp => emp.hasPayslip);
      const results: BulkResults = await payoutService.bulkGeneratePayslips(
        eligibleEmployees.map(emp => emp.payout!.id)
      );
      setBulkResults(results);
      setBulkDialogOpen(true);
      setSuccess(`Bulk generation completed: ${results.successful}/${results.total} successful`);
    } catch (err) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error in bulk generation:', err);
      }
      setError('Failed to generate payslips in bulk. Please try again.');
    } finally {
      setBulkLoading(false);
    }
  };

  const handleBulkEmail = async (): Promise<void> => {
    setBulkLoading(true);
    try {
      const eligibleEmployees = employees.filter(emp => emp.hasPayslip);
      const results: BulkResults = await payoutService.bulkEmailPayslips(
        eligibleEmployees.map(emp => emp.payout!.id)
      );
      setBulkResults(results);
      setBulkDialogOpen(true);
      setSuccess(`Bulk email completed: ${results.successful}/${results.total} successful`);
    } catch (err) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error in bulk email:', err);
      }
      setError('Failed to email payslips in bulk. Please try again.');
    } finally {
      setBulkLoading(false);
    }
  };

  const handleClosePayslipDialog = (): void => {
    setPayslipDialogOpen(false);
    setSelectedEmployee(null);
    setPayslipData(null);
  };

  const handleCloseBulkDialog = (): void => {
    setBulkDialogOpen(false);
    setBulkResults(null);
  };

  const handleChangePage = (_event: unknown, newPage: number): void => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number): void => {
    setTabValue(newValue);
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setSearchTerm(event.target.value);
  };

  const handleYearChange = (event: SelectChangeEvent<number>): void => {
    setSelectedYear(event.target.value as number);
  };

  const handleMonthChange = (event: SelectChangeEvent<number>): void => {
    setSelectedMonth(event.target.value as number);
  };

  const getInitials = (name?: string): string => {
    if (!name) return 'U';
    return name.split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getStatusColor = (status?: string): 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' => {
    switch (status?.toLowerCase()) {
      case 'paid': return 'success';
      case 'approved': return 'info';
      case 'processed': return 'primary';
      case 'pending': return 'warning';
      case 'rejected': return 'error';
      default: return 'default';
    }
  };

  const renderPayslipDialog = (): React.ReactElement | null => {
    if (!selectedEmployee || !payslipData) return null;

    return (
      <Dialog 
        open={payslipDialogOpen} 
        onClose={handleClosePayslipDialog}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: { minHeight: '70vh' }
        }}
      >
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">
              Payslip - {payslipData.pay_period}
            </Typography>
            <IconButton onClick={handleClosePayslipDialog}>
              <ReceiptIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        
        <DialogContent dividers>
          {/* Company Header */}
          <Box textAlign="center" mb={3}>
            <Typography variant="h5" fontWeight="bold">
              {payslipData.company_name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {payslipData.company_address}
            </Typography>
            <Typography variant="h6" color="primary" mt={2}>
              SALARY SLIP
            </Typography>
          </Box>

          {/* Employee Details */}
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2, mb: 3 }}>
            <Box>
              <Typography variant="subtitle2" color="text.secondary">Employee Details</Typography>
              <Typography><strong>Name:</strong> {payslipData.employee_name}</Typography>
              <Typography><strong>Employee Code:</strong> {payslipData.employee_code || 'N/A'}</Typography>
              <Typography><strong>Department:</strong> {payslipData.department || 'N/A'}</Typography>
              <Typography><strong>Designation:</strong> {payslipData.designation || 'N/A'}</Typography>
            </Box>
            <Box>
              <Typography variant="subtitle2" color="text.secondary">Pay Details</Typography>
              <Typography><strong>Pay Period:</strong> {payslipData.pay_period}</Typography>
              <Typography><strong>Pay Date:</strong> {payslipData.payout_date}</Typography>
              <Typography><strong>Days in Month:</strong> {payslipData.days_in_month}</Typography>
              <Typography><strong>Days Worked:</strong> {payslipData.days_worked}</Typography>
            </Box>
          </Box>

          <Divider sx={{ mb: 3 }} />

          {/* Earnings and Deductions */}
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
            {/* Earnings */}
            <Box>
              <Typography variant="h6" color="success.main" gutterBottom>
                Earnings
              </Typography>
              <List dense>
                {Object.entries(payslipData.earnings).map(([key, value]) => (
                  <ListItem key={key} sx={{ px: 0, py: 0.5 }}>
                    <ListItemText 
                      primary={key}
                      secondary={payoutService.formatCurrency(value)}
                      primaryTypographyProps={{ variant: 'body2' }}
                      secondaryTypographyProps={{ 
                        variant: 'body2', 
                        fontWeight: 'bold',
                        color: 'success.main'
                      }}
                    />
                  </ListItem>
                ))}
                <Divider sx={{ my: 1 }} />
                <ListItem sx={{ px: 0, bgcolor: theme.palette.success.light, borderRadius: 1 }}>
                  <ListItemText 
                    primary="Total Earnings"
                    secondary={payoutService.formatCurrency(payslipData.total_earnings)}
                    primaryTypographyProps={{ fontWeight: 'bold' }}
                    secondaryTypographyProps={{ 
                      variant: 'h6', 
                      fontWeight: 'bold',
                      color: 'success.dark'
                    }}
                  />
                </ListItem>
              </List>
            </Box>

            {/* Deductions */}
            <Box>
              <Typography variant="h6" color="error.main" gutterBottom>
                Deductions
              </Typography>
              <List dense>
                {Object.entries(payslipData.deductions).map(([key, value]) => (
                  <ListItem key={key} sx={{ px: 0, py: 0.5 }}>
                    <ListItemText 
                      primary={key}
                      secondary={payoutService.formatCurrency(value)}
                      primaryTypographyProps={{ variant: 'body2' }}
                      secondaryTypographyProps={{ 
                        variant: 'body2', 
                        fontWeight: 'bold',
                        color: 'error.main'
                      }}
                    />
                  </ListItem>
                ))}
                <Divider sx={{ my: 1 }} />
                <ListItem sx={{ px: 0, bgcolor: theme.palette.error.light, borderRadius: 1 }}>
                  <ListItemText 
                    primary="Total Deductions"
                    secondary={payoutService.formatCurrency(payslipData.total_deductions)}
                    primaryTypographyProps={{ fontWeight: 'bold' }}
                    secondaryTypographyProps={{ 
                      variant: 'h6', 
                      fontWeight: 'bold',
                      color: 'error.dark'
                    }}
                  />
                </ListItem>
              </List>
            </Box>
          </Box>

          <Divider sx={{ my: 3 }} />

          {/* Net Pay */}
          <Box textAlign="center" p={2} bgcolor={theme.palette.primary.light} borderRadius={1}>
            <Typography variant="h5" color="primary.dark" fontWeight="bold">
              Net Pay: {payoutService.formatCurrency(payslipData.net_pay)}
            </Typography>
          </Box>
        </DialogContent>
        
        <DialogActions>
          <Button 
            variant="contained" 
            startIcon={<DownloadIcon />}
            onClick={() => selectedEmployee && handleDownloadPayslip(selectedEmployee)}
            disabled={downloadLoading === selectedEmployee?.emp_id}
          >
            Download
          </Button>
          <Button 
            variant="outlined" 
            startIcon={<EmailIcon />}
            onClick={() => selectedEmployee && handleEmailPayslip(selectedEmployee)}
            disabled={emailLoading === selectedEmployee?.emp_id}
          >
            Email
          </Button>
          <Button variant="outlined" onClick={handleClosePayslipDialog}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    );
  };

  const renderBulkResultsDialog = (): React.ReactElement | null => {
    if (!bulkResults) return null;

    return (
      <Dialog 
        open={bulkDialogOpen} 
        onClose={handleCloseBulkDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">
              Bulk Operation Results
            </Typography>
            <IconButton onClick={handleCloseBulkDialog}>
              <ReceiptIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        
        <DialogContent dividers>
          {/* Summary */}
          <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 3, mb: 3 }}>
            <Box textAlign="center" p={2} bgcolor={theme.palette.info.light} borderRadius={1}>
              <Typography variant="h4" color="info.dark" fontWeight="bold">
                {bulkResults.total}
              </Typography>
              <Typography variant="body2" color="info.dark">
                Total
              </Typography>
            </Box>
            <Box textAlign="center" p={2} bgcolor={theme.palette.success.light} borderRadius={1}>
              <Typography variant="h4" color="success.dark" fontWeight="bold">
                {bulkResults.successful}
              </Typography>
              <Typography variant="body2" color="success.dark">
                Successful
              </Typography>
            </Box>
            <Box textAlign="center" p={2} bgcolor={theme.palette.error.light} borderRadius={1}>
              <Typography variant="h4" color="error.dark" fontWeight="bold">
                {bulkResults.failed}
              </Typography>
              <Typography variant="body2" color="error.dark">
                Failed
              </Typography>
            </Box>
          </Box>

          {/* Detailed Results */}
          <Typography variant="h6" gutterBottom>Detailed Results</Typography>
          <List>
            {bulkResults.results.map((result, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  {result.success ? (
                    <CheckCircleIcon color="success" />
                  ) : (
                    <ErrorIcon color="error" />
                  )}
                </ListItemIcon>
                <ListItemText
                  primary={result.employee_name}
                  secondary={result.success ? 'Success' : result.error}
                />
              </ListItem>
            ))}
          </List>
        </DialogContent>
        
        <DialogActions>
          <Button variant="outlined" onClick={handleCloseBulkDialog}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    );
  };

  const renderEmployeePayslipsTab = (): React.ReactElement => {
    const startIndex = page * rowsPerPage;
    const displayedEmployees = filteredEmployees.slice(startIndex, startIndex + rowsPerPage);

    return (
      <Box>
        {/* Filters */}
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
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={loadEmployeesWithPayouts}
                disabled={loading}
              >
                Refresh
              </Button>
            </Box>
          </CardContent>
        </Card>

        {/* Employee Table */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Employee Payslips ({filteredEmployees.length} employees)
            </Typography>
            
            {loading ? (
              <Box display="flex" justifyContent="center" p={4}>
                <CircularProgress />
              </Box>
            ) : displayedEmployees.length === 0 ? (
              <Box textAlign="center" p={4}>
                <PersonIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  No employees found
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {searchTerm ? `No employees match "${searchTerm}"` : 'No employees available for the selected period'}
                </Typography>
              </Box>
            ) : (
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
                        <TableCell align="center">Payout Status</TableCell>
                        <TableCell align="right">Net Salary</TableCell>
                        <TableCell align="center">Payslip</TableCell>
                        <TableCell align="center">Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {displayedEmployees.map((employee) => (
                        <TableRow key={employee.emp_id} hover>
                          <TableCell>
                            <Box display="flex" alignItems="center">
                              <Avatar sx={{ bgcolor: theme.palette.primary.main, mr: 2, width: 40, height: 40 }}>
                                {getInitials(employee.name)}
                              </Avatar>
                              <Box>
                                <Typography variant="subtitle2" fontWeight="bold">
                                  {employee.name}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                  {employee.emp_id}
                                </Typography>
                                {employee.designation && (
                                  <Typography variant="caption" color="text.secondary">
                                    {employee.designation}
                                  </Typography>
                                )}
                              </Box>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {employee.department || 'N/A'}
                            </Typography>
                          </TableCell>
                          <TableCell align="center">
                            {employee.payout ? (
                              <Chip 
                                label={employee.payout.status}
                                color={getStatusColor(employee.payout.status)}
                                size="small"
                              />
                            ) : (
                              <Chip label="No Payout" color="default" size="small" />
                            )}
                          </TableCell>
                          <TableCell align="right">
                            <Typography variant="body2" fontWeight="bold">
                              {employee.payout ? payoutService.formatCurrency(employee.payout.net_salary) : 'N/A'}
                            </Typography>
                          </TableCell>
                          <TableCell align="center">
                            {employee.hasPayslip ? (
                              <CheckCircleIcon color="success" />
                            ) : (
                              <ErrorIcon color="error" />
                            )}
                          </TableCell>
                          <TableCell align="center">
                            <Box display="flex" justifyContent="center" gap={1}>
                              {employee.hasPayslip && (
                                <>
                                  <Tooltip title="View Payslip">
                                    <IconButton 
                                      size="small"
                                      color="primary"
                                      onClick={() => handleViewPayslip(employee)}
                                    >
                                      <VisibilityIcon />
                                    </IconButton>
                                  </Tooltip>
                                  <Tooltip title="Download Payslip">
                                    <IconButton 
                                      size="small"
                                      color="secondary"
                                      onClick={() => handleDownloadPayslip(employee)}
                                      disabled={downloadLoading === employee.emp_id}
                                    >
                                      {downloadLoading === employee.emp_id ? (
                                        <CircularProgress size={20} />
                                      ) : (
                                        <DownloadIcon />
                                      )}
                                    </IconButton>
                                  </Tooltip>
                                  <Tooltip title="Email Payslip">
                                    <IconButton 
                                      size="small"
                                      color="info"
                                      onClick={() => handleEmailPayslip(employee)}
                                      disabled={emailLoading === employee.emp_id}
                                    >
                                      {emailLoading === employee.emp_id ? (
                                        <CircularProgress size={20} />
                                      ) : (
                                        <EmailIcon />
                                      )}
                                    </IconButton>
                                  </Tooltip>
                                </>
                              )}
                            </Box>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>

                <TablePagination
                  component="div"
                  count={filteredEmployees.length}
                  page={page}
                  onPageChange={handleChangePage}
                  rowsPerPage={rowsPerPage}
                  onRowsPerPageChange={handleChangeRowsPerPage}
                  rowsPerPageOptions={[5, 10, 25, 50]}
                />
              </>
            )}
          </CardContent>
        </Card>
      </Box>
    );
  };

  const renderBulkOperationsTab = (): React.ReactElement => {
    const eligibleEmployees = employees.filter(emp => emp.hasPayslip);
    const totalEmployees = employees.length;

    return (
      <Box>
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(3, 1fr)' }, gap: 3 }}>
          {/* Summary Cards */}
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <PersonIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">Total Employees</Typography>
              </Box>
              <Typography variant="h3" color="primary.main" fontWeight="bold">
                {totalEmployees}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                For {monthOptions.find(m => m.value === selectedMonth)?.label} {selectedYear}
              </Typography>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <CheckCircleIcon sx={{ mr: 1, color: 'success.main' }} />
                <Typography variant="h6">Eligible for Payslips</Typography>
              </Box>
              <Typography variant="h3" color="success.main" fontWeight="bold">
                {eligibleEmployees.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Processed/Approved/Paid payouts
              </Typography>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <WarningIcon sx={{ mr: 1, color: 'warning.main' }} />
                <Typography variant="h6">Not Eligible</Typography>
              </Box>
              <Typography variant="h3" color="warning.main" fontWeight="bold">
                {totalEmployees - eligibleEmployees.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                No payout or pending status
              </Typography>
            </CardContent>
          </Card>

          {/* Bulk Operations */}
          <Box sx={{ gridColumn: '1 / -1' }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Bulk Operations
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Perform bulk operations on all eligible employee payslips for the selected period.
                </Typography>

                <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2 }}>
                  <Box>
                    <Button
                      fullWidth
                      variant="contained"
                      size="large"
                      startIcon={bulkLoading ? <CircularProgress size={20} /> : <GetAppIcon />}
                      onClick={handleBulkGenerate}
                      disabled={bulkLoading || eligibleEmployees.length === 0}
                      sx={{ py: 2 }}
                    >
                      {bulkLoading ? 'Generating...' : `Generate All Payslips (${eligibleEmployees.length})`}
                    </Button>
                    <Typography variant="caption" color="text.secondary" display="block" mt={1}>
                      Generate PDF payslips for all eligible employees
                    </Typography>
                  </Box>

                  <Box>
                    <Button
                      fullWidth
                      variant="outlined"
                      size="large"
                      startIcon={bulkLoading ? <CircularProgress size={20} /> : <SendIcon />}
                      onClick={handleBulkEmail}
                      disabled={bulkLoading || eligibleEmployees.length === 0}
                      sx={{ py: 2 }}
                    >
                      {bulkLoading ? 'Emailing...' : `Email All Payslips (${eligibleEmployees.length})`}
                    </Button>
                    <Typography variant="caption" color="text.secondary" display="block" mt={1}>
                      Email payslips to all eligible employees
                    </Typography>
                  </Box>
                </Box>

                {eligibleEmployees.length === 0 && (
                  <Alert severity="info" sx={{ mt: 2 }}>
                    No employees are eligible for payslip operations. Ensure payouts are processed, approved, or paid.
                  </Alert>
                )}
              </CardContent>
            </Card>
          </Box>
        </Box>
      </Box>
    );
  };

  return (
    <PageLayout title="Payout Reports">
      <Typography variant="h4" gutterBottom>
        Payout Reports & Payslips
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Manage employee payslips, download reports, and perform bulk operations.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab 
            label="Employee Payslips" 
            icon={<ReceiptIcon />} 
            iconPosition="start"
          />
          <Tab 
            label="Bulk Operations" 
            icon={<AssessmentIcon />} 
            iconPosition="start"
          />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {tabValue === 0 && renderEmployeePayslipsTab()}
      {tabValue === 1 && renderBulkOperationsTab()}

      {/* Dialogs */}
      {renderPayslipDialog()}
      {renderBulkResultsDialog()}
    </PageLayout>
  );
};

export default PayoutReports; 