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
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText
} from '@mui/material';
import {
  Search as SearchIcon,
  Calculate as CalculateIcon,
  Person as PersonIcon,
  MonetizationOn as MonetizationOnIcon,
  Receipt as ReceiptIcon,
  Close as CloseIcon,
  ExpandMore as ExpandMoreIcon,
  AccountBalance as AccountBalanceIcon,
  TrendingUp as TrendingUpIcon,
  Download as DownloadIcon
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';
import payoutService from '../../services/payoutService';
import dataService from '../../services/dataService';
import PageLayout from '../../layout/PageLayout';

const AdminPayouts = () => {
  const theme = useTheme();
  const [loading, setLoading] = useState(false);
  const [usersLoading, setUsersLoading] = useState(true);
  const [error, setError] = useState(null);
  const [users, setUsers] = useState([]);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [calculationDialogOpen, setCalculationDialogOpen] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [calculatedPayout, setCalculatedPayout] = useState(null);
  const [calculating, setCalculating] = useState(false);

  // Pagination
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  // Generate year options for the last 3 years and next year
  const yearOptions = Array.from({ length: 4 }, (_, i) => {
    const year = new Date().getFullYear() - 1 + i;
    return { value: year, label: year.toString() };
  });

  // Month options
  const monthOptions = Array.from({ length: 12 }, (_, i) => ({
    value: i + 1,
    label: new Date(0, i).toLocaleString('default', { month: 'long' })
  }));

  useEffect(() => {
    loadUsers();
  }, []);

  useEffect(() => {
    filterUsers();
  }, [searchTerm, users]);

  const loadUsers = async () => {
    setUsersLoading(true);
    setError(null);
    
    try {
      const response = await dataService.getUsers(0, 1000); // Get a large number of users
      setUsers(response.users || []);
    } catch (err) {
      console.error('Error loading users:', err);
      setError('Failed to load users. Please try again.');
    } finally {
      setUsersLoading(false);
    }
  };

  const filterUsers = () => {
    if (!searchTerm.trim()) {
      setFilteredUsers(users);
      return;
    }

    const searchLower = searchTerm.toLowerCase();
    const filtered = users.filter(user => 
      user.emp_id?.toLowerCase().includes(searchLower) ||
      user.name?.toLowerCase().includes(searchLower) ||
      user.email?.toLowerCase().includes(searchLower) ||
      user.department?.toLowerCase().includes(searchLower) ||
      user.designation?.toLowerCase().includes(searchLower)
    );
    setFilteredUsers(filtered);
    setPage(0); // Reset to first page when filtering
  };

  const handleCalculateSalary = (employee) => {
    setSelectedEmployee(employee);
    setCalculatedPayout(null);
    setCalculationDialogOpen(true);
  };

  const calculateMonthlySalary = async () => {
    if (!selectedEmployee) return;

    setCalculating(true);
    try {
      const payoutData = await payoutService.calculateMonthlyPayout(
        selectedEmployee.emp_id,
        selectedMonth,
        selectedYear
      );
      setCalculatedPayout(payoutData);
    } catch (err) {
      console.error('Error calculating salary:', err);
      setError('Failed to calculate monthly salary. Please try again.');
    } finally {
      setCalculating(false);
    }
  };

  const handleCloseCalculationDialog = () => {
    setCalculationDialogOpen(false);
    setSelectedEmployee(null);
    setCalculatedPayout(null);
  };

  const createPayout = async () => {
    if (!calculatedPayout) return;

    try {
      setLoading(true);
      await payoutService.createPayout(calculatedPayout);
      setError(null);
      // Show success message (you might want to add a success state)
      handleCloseCalculationDialog();
    } catch (err) {
      console.error('Error creating payout:', err);
      setError('Failed to create payout. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getInitials = (name) => {
    if (!name) return 'U';
    return name.split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getRoleBadgeColor = (role) => {
    switch (role?.toLowerCase()) {
      case 'admin': return 'error';
      case 'superadmin': return 'secondary';
      case 'manager': return 'warning';
      case 'hr': return 'info';
      default: return 'primary';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  const renderCalculationDialog = () => {
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
                    {selectedEmployee.emp_id} • {selectedEmployee.designation || 'N/A'}
                  </Typography>
                </Box>
              </Box>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2"><strong>Department:</strong> {selectedEmployee.department || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2"><strong>Email:</strong> {selectedEmployee.email || 'N/A'}</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Period Selection */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>Calculation Period</Typography>
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
                <Grid container spacing={3} sx={{ mb: 3 }}>
                  <Grid item xs={4}>
                    <Box textAlign="center" p={2} bgcolor={theme.palette.success.light} borderRadius={1}>
                      <Typography variant="h5" color="success.dark" fontWeight="bold">
                        {payoutService.formatCurrency(calculatedPayout.gross_salary)}
                      </Typography>
                      <Typography variant="body2" color="success.dark">
                        Gross Salary
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={4}>
                    <Box textAlign="center" p={2} bgcolor={theme.palette.error.light} borderRadius={1}>
                      <Typography variant="h5" color="error.dark" fontWeight="bold">
                        {payoutService.formatCurrency(calculatedPayout.total_deductions)}
                      </Typography>
                      <Typography variant="body2" color="error.dark">
                        Total Deductions
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={4}>
                    <Box textAlign="center" p={2} bgcolor={theme.palette.primary.light} borderRadius={1}>
                      <Typography variant="h5" color="primary.dark" fontWeight="bold">
                        {payoutService.formatCurrency(calculatedPayout.net_salary)}
                      </Typography>
                      <Typography variant="body2" color="primary.dark">
                        Net Salary
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>

                {/* Detailed Breakdown */}
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="subtitle1" fontWeight="bold">
                      Detailed Breakdown
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Grid container spacing={3}>
                      {/* Earnings */}
                      <Grid item xs={12} md={6}>
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
                      </Grid>

                      {/* Deductions */}
                      <Grid item xs={12} md={6}>
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
                                primary="Income Tax (TDS)"
                                secondary={payoutService.formatCurrency(calculatedPayout.tds)}
                              />
                            </ListItem>
                          )}
                        </List>
                      </Grid>
                    </Grid>
                  </AccordionDetails>
                </Accordion>

                {/* Tax Information */}
                <Box mt={2} p={2} bgcolor={theme.palette.grey[100]} borderRadius={1}>
                  <Typography variant="subtitle2" gutterBottom>Tax Information</Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2">
                        <strong>Tax Regime:</strong> {calculatedPayout.tax_regime?.toUpperCase() || 'NEW'}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2">
                        <strong>Annual Tax Liability:</strong> {payoutService.formatCurrency(calculatedPayout.annual_tax_liability)}
                      </Typography>
                    </Grid>
                  </Grid>
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

  const renderUsersTable = () => {
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
                <TableRow key={user.emp_id} hover>
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
                          {user.emp_id}
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
                      label={user.role || 'Employee'}
                      color={getRoleBadgeColor(user.role)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {formatDate(user.doj)}
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
          onPageChange={(event, newPage) => setPage(newPage)}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={(event) => {
            setRowsPerPage(parseInt(event.target.value, 10));
            setPage(0);
          }}
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
      
      {/* Search and Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                placeholder="Search employees by name, ID, email, department..."
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
            <Grid item xs={12} md={6}>
              <Box display="flex" alignItems="center" gap={2}>
                <Typography variant="body2" color="text.secondary">
                  {filteredUsers.length} employee{filteredUsers.length !== 1 ? 's' : ''} found
                </Typography>
              </Box>
            </Grid>
          </Grid>
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