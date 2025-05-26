import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
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
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  Search as SearchIcon,
  Download as DownloadIcon,
  Email as EmailIcon,
  Visibility as VisibilityIcon,
  Receipt as ReceiptIcon,
  Person as PersonIcon,
  Assessment as AssessmentIcon,
  MonetizationOn as MonetizationOnIcon,
  Send as SendIcon,
  GetApp as GetAppIcon,
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';
import payoutService from '../../services/payoutService';
import dataService from '../../services/dataService';
import PageLayout from '../../layout/PageLayout';

const PayoutReports = () => {
  const theme = useTheme();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  
  // Employee payslips data
  const [employees, setEmployees] = useState([]);
  const [filteredEmployees, setFilteredEmployees] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);
  
  // Bulk operations
  const [bulkLoading, setBulkLoading] = useState(false);
  const [bulkResults, setBulkResults] = useState(null);
  const [bulkDialogOpen, setBulkDialogOpen] = useState(false);
  
  // Payslip viewing
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [payslipData, setPayslipData] = useState(null);
  const [payslipDialogOpen, setPayslipDialogOpen] = useState(false);
  const [downloadLoading, setDownloadLoading] = useState(null);
  const [emailLoading, setEmailLoading] = useState(null);
  
  // Pagination
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  // Generate year options
  const yearOptions = Array.from({ length: 5 }, (_, i) => {
    const year = new Date().getFullYear() - i;
    return { value: year, label: year.toString() };
  });

  // Month options
  const monthOptions = Array.from({ length: 12 }, (_, i) => ({
    value: i + 1,
    label: new Date(0, i).toLocaleString('default', { month: 'long' })
  }));

  useEffect(() => {
    loadEmployeesWithPayouts();
  }, [selectedYear, selectedMonth]);

  useEffect(() => {
    filterEmployees();
  }, [searchTerm, employees]);

  const loadEmployeesWithPayouts = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Get all users
      const usersResponse = await dataService.getUsers(0, 1000);
      const allUsers = usersResponse.users || [];
      
      // Get monthly payouts
      const payouts = await payoutService.getMonthlyPayouts(selectedYear, selectedMonth);
      
      // Combine user data with payout data
      const employeesWithPayouts = allUsers.map(user => {
        const userPayouts = payouts.filter(payout => payout.employee_id === user.emp_id);
        const latestPayout = userPayouts.length > 0 ? userPayouts[0] : null;
        
        return {
          ...user,
          payout: latestPayout,
          hasPayslip: latestPayout && ['processed', 'approved', 'paid'].includes(latestPayout.status)
        };
      });
      
      setEmployees(employeesWithPayouts);
    } catch (err) {
      console.error('Error loading employees with payouts:', err);
      setError('Failed to load employee payouts. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const filterEmployees = () => {
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
  };

  const handleViewPayslip = async (employee) => {
    if (!employee.payout) {
      setError('No payout found for this employee');
      return;
    }

    try {
      setSelectedEmployee(employee);
      setPayslipDialogOpen(true);
      
      // Load payslip data
      const data = await payoutService.getPayslipData(employee.payout.id);
      setPayslipData(data);
      
    } catch (err) {
      console.error('Error loading payslip data:', err);
      setError('Failed to load payslip details. Please try again.');
      setPayslipDialogOpen(false);
    }
  };

  const handleDownloadPayslip = async (employee) => {
    if (!employee.payout) {
      setError('No payout found for this employee');
      return;
    }

    try {
      setDownloadLoading(employee.emp_id);
      await payoutService.downloadPayslip(employee.payout.id);
      setSuccess(`Payslip downloaded for ${employee.name}`);
    } catch (err) {
      console.error('Error downloading payslip:', err);
      setError('Failed to download payslip. Please try again.');
    } finally {
      setDownloadLoading(null);
    }
  };

  const handleEmailPayslip = async (employee) => {
    if (!employee.payout) {
      setError('No payout found for this employee');
      return;
    }

    try {
      setEmailLoading(employee.emp_id);
      await payoutService.emailPayslip(employee.payout.id);
      setSuccess(`Payslip emailed to ${employee.name} at ${employee.email}`);
    } catch (err) {
      console.error('Error emailing payslip:', err);
      setError('Failed to email payslip. Please try again.');
    } finally {
      setEmailLoading(null);
    }
  };

  const handleBulkGenerate = async () => {
    setBulkLoading(true);
    setError(null);
    
    try {
      const result = await payoutService.bulkGeneratePayslips(selectedMonth, selectedYear);
      setBulkResults(result);
      setBulkDialogOpen(true);
      setSuccess(`Bulk payslip generation completed: ${result.results.successful_generations} successful, ${result.results.failed_generations} failed`);
    } catch (err) {
      console.error('Error in bulk payslip generation:', err);
      setError('Failed to generate payslips in bulk. Please try again.');
    } finally {
      setBulkLoading(false);
    }
  };

  const handleBulkEmail = async () => {
    setBulkLoading(true);
    setError(null);
    
    try {
      const result = await payoutService.bulkEmailPayslips(selectedMonth, selectedYear);
      setBulkResults(result);
      setBulkDialogOpen(true);
      setSuccess(`Bulk payslip email initiated for ${selectedMonth}/${selectedYear}`);
    } catch (err) {
      console.error('Error in bulk payslip email:', err);
      setError('Failed to email payslips in bulk. Please try again.');
    } finally {
      setBulkLoading(false);
    }
  };

  const handleClosePayslipDialog = () => {
    setPayslipDialogOpen(false);
    setSelectedEmployee(null);
    setPayslipData(null);
  };

  const handleCloseBulkDialog = () => {
    setBulkDialogOpen(false);
    setBulkResults(null);
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const renderPayslipDialog = () => {
    if (!selectedEmployee || !payslipData) return null;

    return (
      <Dialog open={payslipDialogOpen} onClose={handleClosePayslipDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Typography variant="h6">
              Payslip - {selectedEmployee.name}
            </Typography>
            <IconButton onClick={handleClosePayslipDialog}>
              <ExpandMoreIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        
        <DialogContent>
          {/* Employee Information */}
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>Employee Information</Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography><strong>Name:</strong> {payslipData.employee_name}</Typography>
                  <Typography><strong>Employee Code:</strong> {payslipData.employee_code || 'N/A'}</Typography>
                  <Typography><strong>Department:</strong> {payslipData.department || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography><strong>Pay Period:</strong> {payslipData.pay_period}</Typography>
                  <Typography><strong>Pay Date:</strong> {payslipData.payout_date}</Typography>
                  <Typography><strong>LWP Days:</strong> {payslipData.lwp_days}</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Earnings and Deductions */}
          <Grid container spacing={3}>
            {/* Earnings */}
            <Grid item xs={12} md={6}>
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
            </Grid>

            {/* Deductions */}
            <Grid item xs={12} md={6}>
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
            </Grid>
          </Grid>

          {/* Net Pay */}
          <Card sx={{ mt: 2, bgcolor: theme.palette.primary.light }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="center">
                <Box textAlign="center">
                  <Typography variant="h4" color="primary.dark" fontWeight="bold">
                    {payoutService.formatCurrency(payslipData.net_pay)}
                  </Typography>
                  <Typography variant="subtitle1" color="primary.dark">
                    Net Pay
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>

          {/* YTD Information */}
          <Grid container spacing={2} mt={2}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" color="text.secondary">Year to Date</Typography>
              <Typography><strong>YTD Gross:</strong> {payoutService.formatCurrency(payslipData.ytd_gross)}</Typography>
              <Typography><strong>YTD Tax Deducted:</strong> {payoutService.formatCurrency(payslipData.ytd_tax_deducted)}</Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" color="text.secondary">Tax Information</Typography>
              <Typography><strong>Tax Regime:</strong> {payslipData.tax_regime.toUpperCase()}</Typography>
              <Typography><strong>PAN:</strong> {payslipData.pan_number || 'N/A'}</Typography>
              <Typography><strong>UAN:</strong> {payslipData.uan_number || 'N/A'}</Typography>
            </Grid>
          </Grid>
        </DialogContent>
        
        <DialogActions>
          <Button 
            variant="contained" 
            startIcon={<DownloadIcon />}
            onClick={() => handleDownloadPayslip(selectedEmployee)}
            disabled={downloadLoading === selectedEmployee.emp_id}
          >
            {downloadLoading === selectedEmployee.emp_id ? 'Downloading...' : 'Download PDF'}
          </Button>
          <Button 
            variant="outlined" 
            startIcon={<EmailIcon />}
            onClick={() => handleEmailPayslip(selectedEmployee)}
            disabled={emailLoading === selectedEmployee.emp_id}
          >
            {emailLoading === selectedEmployee.emp_id ? 'Sending...' : 'Email'}
          </Button>
          <Button variant="text" onClick={handleClosePayslipDialog}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    );
  };

  const renderBulkResultsDialog = () => {
    if (!bulkResults) return null;

    return (
      <Dialog open={bulkDialogOpen} onClose={handleCloseBulkDialog} maxWidth="md" fullWidth>
        <DialogTitle>Bulk Operation Results</DialogTitle>
        <DialogContent>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={4}>
              <Box textAlign="center" p={2}>
                <Avatar sx={{ bgcolor: theme.palette.info.main, mx: 'auto', mb: 1 }}>
                  <AssessmentIcon />
                </Avatar>
                <Typography variant="h5" color="info.main" fontWeight="bold">
                  {bulkResults.results?.total_payouts || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Payouts
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Box textAlign="center" p={2}>
                <Avatar sx={{ bgcolor: theme.palette.success.main, mx: 'auto', mb: 1 }}>
                  <CheckCircleIcon />
                </Avatar>
                <Typography variant="h5" color="success.main" fontWeight="bold">
                  {bulkResults.results?.successful_generations || bulkResults.results?.successful_emails || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Successful
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Box textAlign="center" p={2}>
                <Avatar sx={{ bgcolor: theme.palette.error.main, mx: 'auto', mb: 1 }}>
                  <ErrorIcon />
                </Avatar>
                <Typography variant="h5" color="error.main" fontWeight="bold">
                  {bulkResults.results?.failed_generations || bulkResults.results?.failed_emails || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Failed
                </Typography>
              </Box>
            </Grid>
          </Grid>

          {/* Error Details */}
          {bulkResults.results?.errors && bulkResults.results.errors.length > 0 && (
            <Accordion sx={{ mt: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle1" color="error">
                  Error Details ({bulkResults.results.errors.length})
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <List dense>
                  {bulkResults.results.errors.map((error, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <ErrorIcon color="error" />
                      </ListItemIcon>
                      <ListItemText 
                        primary={`Employee: ${error.employee_id}`}
                        secondary={error.error}
                      />
                    </ListItem>
                  ))}
                </List>
              </AccordionDetails>
            </Accordion>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseBulkDialog}>Close</Button>
        </DialogActions>
      </Dialog>
    );
  };

  const renderEmployeePayslipsTab = () => {
    const paginatedEmployees = filteredEmployees.slice(
      page * rowsPerPage,
      page * rowsPerPage + rowsPerPage
    );

    return (
      <Box>
        {/* Search and Filters */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={6} md={4}>
                <TextField
                  fullWidth
                  placeholder="Search employees..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <SearchIcon />
                      </InputAdornment>
                    ),
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={3} md={2}>
                <FormControl fullWidth>
                  <InputLabel>Month</InputLabel>
                  <Select
                    value={selectedMonth}
                    label="Month"
                    onChange={(e) => setSelectedMonth(e.target.value)}
                  >
                    {monthOptions.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={3} md={2}>
                <FormControl fullWidth>
                  <InputLabel>Year</InputLabel>
                  <Select
                    value={selectedYear}
                    label="Year"
                    onChange={(e) => setSelectedYear(e.target.value)}
                  >
                    {yearOptions.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Employee Payslips Table */}
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">
                Employee Payslips - {monthOptions.find(m => m.value === selectedMonth)?.label} {selectedYear}
              </Typography>
              <Box display="flex" gap={2}>
                <Chip 
                  label={`${filteredEmployees.filter(emp => emp.hasPayslip).length} Payslips Available`}
                  color="success"
                  size="small"
                />
                <Chip 
                  label={`${filteredEmployees.filter(emp => emp.payout && !emp.hasPayslip).length} Pending`}
                  color="warning"
                  size="small"
                />
                <Chip 
                  label={`${filteredEmployees.filter(emp => !emp.payout).length} No Payout`}
                  color="default"
                  size="small"
                />
                {filteredEmployees.filter(emp => emp.payout && emp.payout.status === 'pending').length > 0 && (
                  <Button
                    variant="outlined"
                    size="small"
                    color="warning"
                    onClick={() => window.location.href = '/payouts'}
                  >
                    Process {filteredEmployees.filter(emp => emp.payout && emp.payout.status === 'pending').length} Pending Payouts
                  </Button>
                )}
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<RefreshIcon />}
                  onClick={loadEmployeesWithPayouts}
                  disabled={loading}
                >
                  Refresh
                </Button>
              </Box>
            </Box>
            
            {loading ? (
              <Box display="flex" justifyContent="center" p={4}>
                <CircularProgress />
              </Box>
            ) : (
              <>
                <TableContainer component={Paper} variant="outlined">
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Employee</TableCell>
                        <TableCell>Department</TableCell>
                        <TableCell align="center">Payslip Status</TableCell>
                        <TableCell align="right">Gross Amount</TableCell>
                        <TableCell align="right">Net Amount</TableCell>
                        <TableCell align="center">Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {paginatedEmployees.map((employee) => (
                        <TableRow key={employee.emp_id} hover>
                          <TableCell>
                            <Box display="flex" alignItems="center">
                              <Avatar sx={{ mr: 2, bgcolor: theme.palette.primary.main }}>
                                <PersonIcon />
                              </Avatar>
                              <Box>
                                <Typography variant="body2" fontWeight="bold">
                                  {employee.name}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                  {employee.emp_id} • {employee.email}
                                </Typography>
                              </Box>
                            </Box>
                          </TableCell>
                          <TableCell>{employee.department || 'N/A'}</TableCell>
                          <TableCell align="center">
                            {employee.hasPayslip ? (
                              <Chip 
                                label="Available"
                                color="success"
                                size="small"
                                icon={<CheckCircleIcon />}
                              />
                            ) : employee.payout ? (
                              <Chip 
                                label={payoutService.getStatusLabel(employee.payout.status)}
                                color={payoutService.getStatusColor(employee.payout.status)}
                                size="small"
                              />
                            ) : (
                              <Chip 
                                label="No Payout"
                                color="default"
                                size="small"
                                icon={<WarningIcon />}
                              />
                            )}
                          </TableCell>
                          <TableCell align="right">
                            {employee.payout ? (
                              <Typography variant="body2" fontWeight="bold" color="success.main">
                                {payoutService.formatCurrency(employee.payout.gross_salary)}
                              </Typography>
                            ) : (
                              <Typography variant="body2" color="text.secondary">-</Typography>
                            )}
                          </TableCell>
                          <TableCell align="right">
                            {employee.payout ? (
                              <Typography variant="body2" fontWeight="bold" color="primary.main">
                                {payoutService.formatCurrency(employee.payout.net_salary)}
                              </Typography>
                            ) : (
                              <Typography variant="body2" color="text.secondary">-</Typography>
                            )}
                          </TableCell>
                          <TableCell align="center">
                            <Box display="flex" justifyContent="center" gap={1}>
                              <Tooltip title={
                                employee.hasPayslip 
                                  ? "View Payslip" 
                                  : employee.payout 
                                    ? `Payslip not available - Payout status: ${payoutService.getStatusLabel(employee.payout.status)}`
                                    : "No payout found for this month"
                              }>
                                <IconButton 
                                  size="small"
                                  color="primary"
                                  onClick={() => handleViewPayslip(employee)}
                                  disabled={!employee.hasPayslip}
                                >
                                  <VisibilityIcon />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title={
                                employee.hasPayslip 
                                  ? "Download Payslip" 
                                  : employee.payout 
                                    ? `Payslip not available - Payout status: ${payoutService.getStatusLabel(employee.payout.status)}`
                                    : "No payout found for this month"
                              }>
                                <IconButton 
                                  size="small"
                                  color="secondary"
                                  onClick={() => handleDownloadPayslip(employee)}
                                  disabled={!employee.hasPayslip || downloadLoading === employee.emp_id}
                                >
                                  {downloadLoading === employee.emp_id ? (
                                    <CircularProgress size={20} />
                                  ) : (
                                    <DownloadIcon />
                                  )}
                                </IconButton>
                              </Tooltip>
                              <Tooltip title={
                                !employee.email 
                                  ? "No email address available"
                                  : employee.hasPayslip 
                                    ? "Email Payslip" 
                                    : employee.payout 
                                      ? `Payslip not available - Payout status: ${payoutService.getStatusLabel(employee.payout.status)}`
                                      : "No payout found for this month"
                              }>
                                <IconButton 
                                  size="small"
                                  color="info"
                                  onClick={() => handleEmailPayslip(employee)}
                                  disabled={!employee.hasPayslip || !employee.email || emailLoading === employee.emp_id}
                                >
                                  {emailLoading === employee.emp_id ? (
                                    <CircularProgress size={20} />
                                  ) : (
                                    <EmailIcon />
                                  )}
                                </IconButton>
                              </Tooltip>
                            </Box>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>

                <TablePagination
                  rowsPerPageOptions={[5, 10, 25, 50]}
                  component="div"
                  count={filteredEmployees.length}
                  rowsPerPage={rowsPerPage}
                  page={page}
                  onPageChange={handleChangePage}
                  onRowsPerPageChange={handleChangeRowsPerPage}
                />
              </>
            )}
          </CardContent>
        </Card>
      </Box>
    );
  };

  const renderBulkOperationsTab = () => {
    return (
      <Box>
        <Grid container spacing={3}>
          {/* Bulk Generate Payslips */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <Avatar sx={{ bgcolor: theme.palette.primary.main, mr: 2 }}>
                    <GetAppIcon />
                  </Avatar>
                  <Typography variant="h6">
                    Bulk Generate Payslips
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Generate PDF payslips for all employees with processed payouts for the selected month.
                </Typography>
                <Box mt={2}>
                  <Button
                    variant="contained"
                    startIcon={bulkLoading ? <CircularProgress size={20} /> : <GetAppIcon />}
                    onClick={handleBulkGenerate}
                    disabled={bulkLoading}
                    fullWidth
                  >
                    {bulkLoading ? 'Generating...' : 'Generate All Payslips'}
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Bulk Email Payslips */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <Avatar sx={{ bgcolor: theme.palette.info.main, mr: 2 }}>
                    <SendIcon />
                  </Avatar>
                  <Typography variant="h6">
                    Bulk Email Payslips
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Email payslips to all employees with processed payouts for the selected month.
                </Typography>
                <Box mt={2}>
                  <Button
                    variant="contained"
                    color="info"
                    startIcon={bulkLoading ? <CircularProgress size={20} /> : <SendIcon />}
                    onClick={handleBulkEmail}
                    disabled={bulkLoading}
                    fullWidth
                  >
                    {bulkLoading ? 'Sending...' : 'Email All Payslips'}
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Period Selection */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Operation Period
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <FormControl fullWidth>
                      <InputLabel>Month</InputLabel>
                      <Select
                        value={selectedMonth}
                        label="Month"
                        onChange={(e) => setSelectedMonth(e.target.value)}
                      >
                        {monthOptions.map((option) => (
                          <MenuItem key={option.value} value={option.value}>
                            {option.label}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={6}>
                    <FormControl fullWidth>
                      <InputLabel>Year</InputLabel>
                      <Select
                        value={selectedYear}
                        label="Year"
                        onChange={(e) => setSelectedYear(e.target.value)}
                      >
                        {yearOptions.map((option) => (
                          <MenuItem key={option.value} value={option.value}>
                            {option.label}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    );
  };

  return (
    <PageLayout title="Payout Reports">
      <Typography variant="h4" gutterBottom>
        Payout Reports & Payslips
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

      {/* Information Alert */}
      {!loading && filteredEmployees.length > 0 && filteredEmployees.filter(emp => emp.hasPayslip).length === 0 && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="body2">
            <strong>Payslips not available:</strong> To view and download payslips, payouts must be in "Processed", "Approved", or "Paid" status. 
            {filteredEmployees.filter(emp => emp.payout && emp.payout.status === 'pending').length > 0 && (
              <span> There are {filteredEmployees.filter(emp => emp.payout && emp.payout.status === 'pending').length} pending payouts that need to be processed first.</span>
            )}
            {filteredEmployees.filter(emp => !emp.payout).length > 0 && (
              <span> {filteredEmployees.filter(emp => !emp.payout).length} employees don't have payouts for this period.</span>
            )}
          </Typography>
        </Alert>
      )}

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
          <Tab label="Employee Payslips" icon={<ReceiptIcon />} />
          <Tab label="Bulk Operations" icon={<AssessmentIcon />} />
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