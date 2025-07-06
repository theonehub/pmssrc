import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Alert,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  IconButton,
  Tooltip,
  Snackbar,
  Grid,
  TablePagination
} from '@mui/material';
import {
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  Receipt as ReceiptIcon,
  CalendarMonth as CalendarMonthIcon,
  AccountBalance as AccountBalanceIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon
} from '@mui/icons-material';
import { useAuth } from '../../shared/hooks/useAuth';
import { salaryProcessingApi, MonthlySalaryResponse } from '../../shared/api/salaryProcessingApi';

interface ToastState {
  show: boolean;
  message: string;
  severity: 'success' | 'error' | 'warning' | 'info';
}

const MySalary: React.FC = () => {
  const { user } = useAuth();
  
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [salaryHistory, setSalaryHistory] = useState<MonthlySalaryResponse[]>([]);
  const [toast, setToast] = useState<ToastState>({ show: false, message: '', severity: 'success' });
  const [downloadLoading, setDownloadLoading] = useState<string | null>(null);
  
  // Pagination state
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  
  // Filter state
  const [selectedYear, setSelectedYear] = useState<number>(new Date().getFullYear());
  const [selectedMonth, setSelectedMonth] = useState<string>('all');
  
  const employeeId = user?.employee_id;

  // Load salary history
  const loadSalaryHistory = useCallback(async () => {
    if (!employeeId) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const response = await salaryProcessingApi.getEmployeeSalaryHistory(employeeId, 200, 0);
      setSalaryHistory(response);
      
    } catch (err) {
      console.error('Error loading salary history:', err);
      setError('Failed to load salary history. Please try again.');
      setSalaryHistory([]);
    } finally {
      setLoading(false);
    }
  }, [employeeId]);

  // Filter salary history based on selected year and month
  const filteredSalaryHistory = salaryHistory.filter(salary => {
    const yearMatch = salary.year === selectedYear;
    const monthMatch = selectedMonth === 'all' || salary.month === parseInt(selectedMonth);
    return yearMatch && monthMatch;
  });

  // Paginated data
  const paginatedData = filteredSalaryHistory.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  // Handle pagination
  const handleChangePage = (_: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  // Handle filters
  const handleYearChange = (event: SelectChangeEvent<number>) => {
    setSelectedYear(event.target.value as number);
    setPage(0);
  };

  const handleMonthChange = (event: SelectChangeEvent<string>) => {
    setSelectedMonth(event.target.value);
    setPage(0);
  };

  // Download payslip
  const handleDownloadPayslip = async (salary: MonthlySalaryResponse) => {
    try {
      setDownloadLoading(salary.employee_id);
      
      const blob = await salaryProcessingApi.downloadPayslip(
        salary.employee_id,
        salary.month,
        salary.year
      );
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `payslip_${salary.employee_id}_${salary.month}_${salary.year}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      showToast(`Payslip downloaded for ${getMonthName(salary.month)} ${salary.year}`, 'success');
      
    } catch (err) {
      console.error('Error downloading payslip:', err);
      showToast('Failed to download payslip. Please try again.', 'error');
    } finally {
      setDownloadLoading(null);
    }
  };

  // Helper functions
  const showToast = (message: string, severity: ToastState['severity'] = 'success'): void => {
    setToast({ show: true, message, severity });
  };

  const closeToast = (): void => {
    setToast(prev => ({ ...prev, show: false }));
  };

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  const getMonthName = (month: number): string => {
    const months = [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ];
    return months[month - 1] || '';
  };

  const getStatusColor = (status: string): 'success' | 'warning' | 'error' | 'default' => {
    switch (status.toLowerCase()) {
      case 'computed':
      case 'approved':
      case 'paid':
        return 'success';
      case 'pending':
        return 'warning';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  // Get available years from salary history
  const availableYears = Array.from(new Set(salaryHistory.map(s => s.year))).sort((a, b) => b - a);

  // Load data on component mount
  useEffect(() => {
    loadSalaryHistory();
  }, [loadSalaryHistory]);

  // Calculate summary statistics
  const totalGrossSalary = filteredSalaryHistory.reduce((sum, salary) => sum + salary.gross_salary, 0);
  const totalNetSalary = filteredSalaryHistory.reduce((sum, salary) => sum + salary.net_salary, 0);
  const totalTDS = filteredSalaryHistory.reduce((sum, salary) => sum + salary.tds, 0);

  if (!employeeId) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          Employee ID not found. Please contact your administrator.
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <ReceiptIcon color="primary" sx={{ fontSize: 32 }} />
            <Typography variant="h4" component="h1">
              My Salary History
            </Typography>
          </Box>
          <Typography variant="body1" color="text.secondary">
            View and download your monthly salary slips and payment history
          </Typography>
        </CardContent>
      </Card>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <AccountBalanceIcon color="primary" />
                <Box>
                  <Typography variant="h6" color="primary">
                    {formatCurrency(totalGrossSalary)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Gross Salary
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <TrendingUpIcon color="success" />
                <Box>
                  <Typography variant="h6" color="success.main">
                    {formatCurrency(totalNetSalary)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Net Salary
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <TrendingDownIcon color="error" />
                <Box>
                  <Typography variant="h6" color="error.main">
                    {formatCurrency(totalTDS)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total TDS Deducted
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Year</InputLabel>
              <Select
                value={selectedYear}
                label="Year"
                onChange={handleYearChange}
              >
                {availableYears.map((year) => (
                  <MenuItem key={year} value={year}>
                    {year}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Month</InputLabel>
              <Select
                value={selectedMonth}
                label="Month"
                onChange={handleMonthChange}
              >
                <MenuItem value="all">All Months</MenuItem>
                {Array.from({ length: 12 }, (_, i) => i + 1).map((month) => (
                  <MenuItem key={month} value={month.toString()}>
                    {getMonthName(month)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <Tooltip title="Refresh">
              <IconButton 
                onClick={loadSalaryHistory}
                disabled={loading}
                color="primary"
              >
                <RefreshIcon />
              </IconButton>
            </Tooltip>

            <Typography variant="body2" color="text.secondary" sx={{ ml: 'auto' }}>
              Showing {filteredSalaryHistory.length} records
            </Typography>
          </Box>
        </CardContent>
      </Card>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Salary History Table */}
      <Card>
        <CardContent>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : filteredSalaryHistory.length === 0 ? (
            <Box sx={{ textAlign: 'center', p: 4 }}>
              <CalendarMonthIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No salary records found
              </Typography>
              <Typography variant="body2" color="text.secondary">
                No salary records available for the selected period.
              </Typography>
            </Box>
          ) : (
            <>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Month/Year</TableCell>
                      <TableCell>Basic Salary</TableCell>
                      <TableCell>Gross Salary</TableCell>
                      <TableCell>Net Salary</TableCell>
                      <TableCell>TDS</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {paginatedData.map((salary) => (
                      <TableRow key={`${salary.employee_id}-${salary.month}-${salary.year}`}>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {getMonthName(salary.month)} {salary.year}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Tax Year: {salary.tax_year}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          {formatCurrency(salary.basic_salary)}
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {formatCurrency(salary.gross_salary)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium" color="success.main">
                            {formatCurrency(salary.net_salary)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" color="error.main">
                            {formatCurrency(salary.tds)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={salary.status}
                            color={getStatusColor(salary.status)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Tooltip title="Download Payslip">
                            <IconButton
                              onClick={() => handleDownloadPayslip(salary)}
                              disabled={downloadLoading === salary.employee_id}
                              color="primary"
                              size="small"
                            >
                              {downloadLoading === salary.employee_id ? (
                                <CircularProgress size={20} />
                              ) : (
                                <DownloadIcon />
                              )}
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>

              {/* Pagination */}
              <TablePagination
                component="div"
                count={filteredSalaryHistory.length}
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

      {/* Toast Notification */}
      <Snackbar
        open={toast.show}
        autoHideDuration={6000}
        onClose={closeToast}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={closeToast} severity={toast.severity} sx={{ width: '100%' }}>
          {toast.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default MySalary; 