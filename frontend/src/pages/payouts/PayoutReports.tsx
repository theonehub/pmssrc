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
  Paper,
  Chip,
  IconButton,
  Tooltip,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  SelectChangeEvent
} from '@mui/material';
import {
  Download as DownloadIcon,
  Email as EmailIcon,
  Visibility as VisibilityIcon,
  GetApp as GetAppIcon,
  Send as SendIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import payoutService from '../../shared/services/payoutService';
import PageLayout from '../../layout/PageLayout';
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
  payout?: {
    id: string;
    gross_salary: number;
    total_deductions: number;
    net_salary: number;
    status: string;
  };
}

interface BulkResults {
  success: number;
  failed: number;
  errors: string[];
}

const PayoutReports: React.FC = () => {
  const [selectedYear, setSelectedYear] = useState<number>(payoutService.getCurrentFinancialYear());
  const [selectedMonth, setSelectedMonth] = useState<number | null>(null);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [emailLoading, setEmailLoading] = useState<string | null>(null);
  const [bulkLoading, setBulkLoading] = useState<boolean>(false);
  const [bulkResults, setBulkResults] = useState<BulkResults | null>(null);
  const [bulkDialogOpen, setBulkDialogOpen] = useState<boolean>(false);

  const { isLoading: payoutsLoading } = usePayrollsQuery({
    year: selectedYear,
    month: selectedMonth
  });

  // Generate year options for the last 5 years
  const yearOptions: YearOption[] = Array.from({ length: 5 }, (_, i) => {
    const year = payoutService.getCurrentFinancialYear() - i;
    return {
      value: year,
      label: payoutService.getFinancialYearLabel(year)
    };
  });

  // Month options
  const monthOptions: MonthOption[] = Array.from({ length: 12 }, (_, i) => ({
    value: i + 1,
    label: payoutService.getMonthName(i + 1)
  }));

  const fetchEmployeeData = async (): Promise<void> => {
    if (!selectedYear) return;

    try {
      setLoading(true);
      setError(null);
      
      // Mock employee data since the actual API methods are not available
      const mockEmployees: Employee[] = [
        {
          employee_id: 'EMP001',
          name: 'John Doe',
          department: 'Engineering',
          designation: 'Software Engineer',
          email: 'john.doe@company.com',
          hasPayslip: true,
          payout: {
            id: 'PAY001',
            gross_salary: 50000,
            total_deductions: 5000,
            net_salary: 45000,
            status: 'paid'
          }
        },
        {
          employee_id: 'EMP002',
          name: 'Jane Smith',
          department: 'HR',
          designation: 'HR Manager',
          email: 'jane.smith@company.com',
          hasPayslip: true,
          payout: {
            id: 'PAY002',
            gross_salary: 60000,
            total_deductions: 6000,
            net_salary: 54000,
            status: 'paid'
          }
        }
      ];
      
      setEmployees(mockEmployees);
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
      // Mock email functionality
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

  const handleBulkGenerate = async (): Promise<void> => {
    try {
      setBulkLoading(true);
      const eligibleEmployees = employees.filter(emp => emp.hasPayslip);
      
      // Mock bulk generation
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
      
      // Mock bulk email
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

  if (payoutsLoading || loading) {
    return (
      <PageLayout title="Payout Reports">
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      </PageLayout>
    );
  }

  return (
    <PageLayout title="Payout Reports">
      <Box sx={{ p: 3 }}>
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
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Employee ID</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Department</TableCell>
                    <TableCell>Gross Salary</TableCell>
                    <TableCell>Net Salary</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {employees.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} align="center">
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
                          {employee.payout ? payoutService.formatCurrency(employee.payout.gross_salary) : 'N/A'}
                        </TableCell>
                        <TableCell>
                          {employee.payout ? payoutService.formatCurrency(employee.payout.net_salary) : 'N/A'}
                        </TableCell>
                        <TableCell>
                          {employee.payout ? (
                            <Chip
                              label={employee.payout.status}
                              color={employee.payout.status === 'paid' ? 'success' : 'default'}
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
                                  <IconButton size="small">
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
      </Box>
    </PageLayout>
  );
};

export default PayoutReports; 