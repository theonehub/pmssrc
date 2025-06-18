import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Tooltip,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  SelectChangeEvent,
  Grid
} from '@mui/material';
import {
  Download as DownloadIcon,
  Email as EmailIcon,
  Visibility as VisibilityIcon,
  GetApp as GetAppIcon,
  Send as SendIcon,
  Refresh as RefreshIcon,
  Analytics as AnalyticsIcon
} from '@mui/icons-material';
import monthlyPayoutService, { 
  MonthlyPayoutResponse, 
  PayoutSearchFilters, 
  LWPAnalytics,
  PayoutSummary
} from '../../shared/services/monthlyPayoutService';
import { usePayrollsQuery } from '../../shared/hooks/usePayrolls';

interface YearOption {
  value: number;
  label: string;
}

interface MonthOption {
  value: number;
  label: string;
}

interface Employee {
  employee_id: string;
  name: string;
  department: string;
  designation: string;
  email: string;
  hasPayslip: boolean;
  payout?: MonthlyPayoutResponse;
}

interface BulkResults {
  success: number;
  failed: number;
  errors: string[];
}

const PayoutReports: React.FC = () => {
  const [selectedYear, setSelectedYear] = useState<number>(monthlyPayoutService.getCurrentFinancialYear());
  const [selectedMonth, setSelectedMonth] = useState<number | null>(null);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [summary, setSummary] = useState<PayoutSummary | null>(null);
  const [lwpAnalytics, setLwpAnalytics] = useState<LWPAnalytics | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [emailLoading, setEmailLoading] = useState<string | null>(null);
  const [bulkLoading, setBulkLoading] = useState<boolean>(false);
  const [bulkResults, setBulkResults] = useState<BulkResults | null>(null);
  const [bulkDialogOpen, setBulkDialogOpen] = useState<boolean>(false);
  const [analyticsDialogOpen, setAnalyticsDialogOpen] = useState<boolean>(false);

  usePayrollsQuery({
    year: selectedYear,
    month: selectedMonth
  });

  // Generate year options for the last 5 years
  const yearOptions: YearOption[] = Array.from({ length: 5 }, (_, i) => {
    const year = monthlyPayoutService.getCurrentFinancialYear() - i;
    return {
      value: year,
      label: monthlyPayoutService.getFinancialYearLabel(year)
    };
  });

  // Month options
  const monthOptions: MonthOption[] = Array.from({ length: 12 }, (_, i) => ({
    value: i + 1,
    label: monthlyPayoutService.getMonthName(i + 1)
  }));

  const fetchEmployeeData = async (): Promise<void> => {
    if (!selectedYear) return;

    try {
      setLoading(true);
      setError(null);
      
      // Fetch monthly payouts
      const filters: PayoutSearchFilters = {
        year: selectedYear,
        ...(selectedMonth && { month: selectedMonth }),
        page: 1,
        size: 1000
      };
      
      const [payoutsResponse, summaryResponse, lwpAnalyticsResponse] = await Promise.all([
        monthlyPayoutService.searchPayouts(filters),
        selectedMonth ? monthlyPayoutService.getPayoutSummary(selectedMonth, selectedYear).catch(() => null) : Promise.resolve(null),
        selectedMonth ? monthlyPayoutService.getLWPAnalytics(selectedMonth, selectedYear).catch(() => null) : Promise.resolve(null)
      ]);
      
      setSummary(summaryResponse);
      setLwpAnalytics(lwpAnalyticsResponse);
      
      // Transform monthly payouts to employee format for backward compatibility
      const employeeData: Employee[] = payoutsResponse.payouts.map(payout => ({
        employee_id: payout.employee_id,
        name: payout.employee_name,
        department: 'Engineering', // Mock department - would come from employee service
        designation: 'Employee', // Mock designation
        email: `${payout.employee_id.toLowerCase()}@company.com`, // Mock email
        hasPayslip: ['processed', 'paid'].includes(payout.status),
        payout: payout
      }));
      
      setEmployees(employeeData);
      
    } catch (err) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Error fetching employee data:', err);
      }
      setError('Failed to fetch employee data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEmployeeData();
  }, [selectedYear, selectedMonth]);

  const handleEmailPayslip = async (employee: Employee): Promise<void> => {
    if (!employee.payout) return;
    
    try {
      setEmailLoading(employee.employee_id);
      // Mock email functionality - would integrate with actual email service
      await new Promise(resolve => setTimeout(resolve, 2000));
      setSuccess(`Payslip emailed to ${employee.name}`);
    } catch (err) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Error emailing payslip:', err);
      }
      setError('Failed to email payslip. Please try again.');
    } finally {
      setEmailLoading(null);
    }
  };

  const handleDownloadPayslip = async (employee: Employee): Promise<void> => {
    if (!employee.payout) return;
    
    try {
      await monthlyPayoutService.downloadPayslip(
        employee.employee_id, 
        employee.payout.month, 
        employee.payout.year
      );
    } catch (err) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Error downloading payslip:', err);
      }
      setError('Failed to download payslip. Please try again.');
    }
  };

  const handleBulkGenerate = async (): Promise<void> => {
    try {
      setBulkLoading(true);
      const eligibleEmployees = employees.filter(emp => emp.hasPayslip);
      
      // Mock bulk generation - would integrate with actual payslip generation service
      await new Promise(resolve => setTimeout(resolve, 3000));
      const results: BulkResults = {
        success: eligibleEmployees.length,
        failed: 0,
        errors: []
      };
      
      setBulkResults(results);
      setBulkDialogOpen(true);
      setSuccess(`Successfully generated ${results.success} payslips`);
    } catch (err) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Error in bulk generation:', err);
      }
      setError('Failed to generate payslips. Please try again.');
    } finally {
      setBulkLoading(false);
    }
  };

  const handleBulkEmail = async (): Promise<void> => {
    try {
      setBulkLoading(true);
      const eligibleEmployees = employees.filter(emp => emp.hasPayslip);
      
      // Mock bulk email - would integrate with actual email service
      await new Promise(resolve => setTimeout(resolve, 3000));
      const results: BulkResults = {
        success: eligibleEmployees.length,
        failed: 0,
        errors: []
      };
      
      setBulkResults(results);
      setBulkDialogOpen(true);
      setSuccess(`Successfully emailed ${results.success} payslips`);
    } catch (err) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Error in bulk email:', err);
      }
      setError('Failed to email payslips. Please try again.');
    } finally {
      setBulkLoading(false);
    }
  };

  const handleYearChange = (event: SelectChangeEvent<string>): void => {
    setSelectedYear(Number(event.target.value));
  };

  const handleMonthChange = (event: SelectChangeEvent<string>): void => {
    setSelectedMonth(event.target.value ? parseInt(event.target.value) : null);
  };

  const handleCloseBulkDialog = (): void => {
    setBulkDialogOpen(false);
    setBulkResults(null);
  };

  const clearMessages = (): void => {
    setError(null);
    setSuccess(null);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Filters */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <FormControl size="small">
          <InputLabel>Financial Year</InputLabel>
          <Select
            value={selectedYear.toString()}
            label="Financial Year"
            onChange={handleYearChange}
          >
            {yearOptions.map((option) => (
              <MenuItem key={option.value} value={option.value.toString()}>
                {option.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControl size="small">
          <InputLabel>Month</InputLabel>
          <Select
            value={selectedMonth ? selectedMonth.toString() : ''}
            label="Month"
            onChange={handleMonthChange}
          >
            <MenuItem value="">All Months</MenuItem>
            {monthOptions.map((option) => (
              <MenuItem key={option.value} value={option.value.toString()}>
                {option.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={fetchEmployeeData}
          disabled={loading}
        >
          Refresh
        </Button>

        {selectedMonth && (
          <Button
            variant="outlined"
            startIcon={<AnalyticsIcon />}
            onClick={() => setAnalyticsDialogOpen(true)}
          >
            View Analytics
          </Button>
        )}
      </Box>

      {/* Messages */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={clearMessages}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={clearMessages}>
          {success}
        </Alert>
      )}

      {/* Summary Cards */}
      {summary && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" color="primary">
                  {summary.total_employees}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Employees
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" color="success.main">
                  {monthlyPayoutService.formatCurrency(summary.total_gross_amount)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Gross Amount
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" color="info.main">
                  {monthlyPayoutService.formatCurrency(summary.total_net_amount)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Net Amount
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" color="warning.main">
                  {monthlyPayoutService.formatCurrency(summary.total_lwp_deduction)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total LWP Deduction
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Bulk Actions */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <Button
          variant="contained"
          startIcon={<GetAppIcon />}
          onClick={handleBulkGenerate}
          disabled={bulkLoading || employees.length === 0}
        >
          {bulkLoading ? 'Generating...' : 'Bulk Generate Payslips'}
        </Button>
        <Button
          variant="outlined"
          startIcon={<SendIcon />}
          onClick={handleBulkEmail}
          disabled={bulkLoading || employees.length === 0}
        >
          {bulkLoading ? 'Sending...' : 'Bulk Email Payslips'}
        </Button>
      </Box>

      {/* Employee Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Employee Payouts
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Employee ID</TableCell>
                  <TableCell>Name</TableCell>
                  <TableCell>Department</TableCell>
                  <TableCell>Gross Salary</TableCell>
                  <TableCell>LWP Days</TableCell>
                  <TableCell>Net Salary</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {employees.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} align="center">
                      No employee data found for the selected period
                    </TableCell>
                  </TableRow>
                ) : (
                  employees.map((employee) => (
                    <TableRow key={employee.employee_id}>
                      <TableCell>{employee.employee_id}</TableCell>
                      <TableCell>{employee.name}</TableCell>
                      <TableCell>{employee.department}</TableCell>
                      <TableCell>
                        {employee.payout ? 
                          monthlyPayoutService.formatCurrency(employee.payout.adjusted_monthly_gross) : 
                          'N/A'
                        }
                      </TableCell>
                      <TableCell>
                        {employee.payout ? (
                          employee.payout.lwp_days > 0 ? (
                            <Chip 
                              label={`${employee.payout.lwp_days} days`} 
                              size="small" 
                              color="warning" 
                            />
                          ) : (
                            <Chip label="0 days" size="small" color="success" />
                          )
                        ) : (
                          'N/A'
                        )}
                      </TableCell>
                      <TableCell>
                        {employee.payout ? 
                          monthlyPayoutService.formatCurrency(employee.payout.monthly_net_salary) : 
                          'N/A'
                        }
                      </TableCell>
                      <TableCell>
                        {employee.payout ? (
                          <Chip
                            label={monthlyPayoutService.getStatusLabel(employee.payout.status)}
                            color={monthlyPayoutService.getStatusColor(employee.payout.status)}
                            size="small"
                          />
                        ) : (
                          <Chip label="No Payout" color="error" size="small" />
                        )}
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          {employee.hasPayslip && employee.payout && (
                            <>
                              <Tooltip title="View Payslip">
                                <IconButton size="small">
                                  <VisibilityIcon />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="Download Payslip">
                                <IconButton 
                                  size="small"
                                  onClick={() => handleDownloadPayslip(employee)}
                                >
                                  <DownloadIcon />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="Email Payslip">
                                <IconButton
                                  size="small"
                                  onClick={() => handleEmailPayslip(employee)}
                                  disabled={!!emailLoading}
                                >
                                  {emailLoading === employee.employee_id ? (
                                    <CircularProgress size={16} />
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
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Bulk Results Dialog */}
      <Dialog open={bulkDialogOpen} onClose={handleCloseBulkDialog}>
        <DialogTitle>Bulk Operation Results</DialogTitle>
        <DialogContent>
          {bulkResults && (
            <Box>
              <Typography variant="body1" gutterBottom>
                <strong>Successful:</strong> {bulkResults.success}
              </Typography>
              <Typography variant="body1" gutterBottom>
                <strong>Failed:</strong> {bulkResults.failed}
              </Typography>
              {bulkResults.errors.length > 0 && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" color="error" gutterBottom>
                    Errors:
                  </Typography>
                  {bulkResults.errors.map((error, index) => (
                    <Typography key={index} variant="body2" color="error">
                      • {error}
                    </Typography>
                  ))}
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseBulkDialog}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Analytics Dialog */}
      <Dialog 
        open={analyticsDialogOpen} 
        onClose={() => setAnalyticsDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>LWP Analytics - {selectedMonth && monthlyPayoutService.getMonthName(selectedMonth)} {selectedYear}</DialogTitle>
        <DialogContent>
          {lwpAnalytics ? (
            <Box>
              <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid item xs={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" color="warning.main">
                        {lwpAnalytics.total_employees_with_lwp}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Employees with LWP
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" color="error.main">
                        {lwpAnalytics.total_lwp_days}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total LWP Days
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" color="warning.main">
                        {monthlyPayoutService.formatCurrency(lwpAnalytics.total_lwp_deduction)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total LWP Deduction
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" color="info.main">
                        {lwpAnalytics.average_lwp_days.toFixed(1)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Average LWP Days
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              {/* Department-wise LWP */}
              <Typography variant="h6" gutterBottom>Department-wise LWP Breakdown</Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Department</TableCell>
                      <TableCell>Employees</TableCell>
                      <TableCell>Total LWP Days</TableCell>
                      <TableCell>Total Deduction</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {Object.entries(lwpAnalytics.department_wise_lwp).map(([dept, data]) => (
                      <TableRow key={dept}>
                        <TableCell>{dept}</TableCell>
                        <TableCell>{data.employee_count}</TableCell>
                        <TableCell>{data.total_lwp_days}</TableCell>
                        <TableCell>{monthlyPayoutService.formatCurrency(data.total_deduction)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          ) : (
            <Typography>No LWP analytics available for the selected period.</Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAnalyticsDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PayoutReports; 