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
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Checkbox,
  FormControlLabel,
  Grid,
  SelectChangeEvent,
  Avatar
} from '@mui/material';
import { 
  People as PeopleIcon, 
  MonetizationOn as MonetizationOnIcon, 
  Receipt as ReceiptIcon,
  PlayArrow as PlayArrowIcon,
  CheckCircle as CheckCircleIcon,
  Refresh as RefreshIcon,
  Calculate as CalculateIcon,
  Warning as WarningIcon
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';
import { usePayrollsQuery } from '../../shared/hooks/usePayrolls';
import monthlyPayoutService, { 
  MonthlyPayoutResponse, 
  BulkPayoutRequest,
  PayoutSearchFilters,
  PayoutSummary
} from '../../shared/services/monthlyPayoutService';

// Type definitions
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
  base_salary: number;
}

interface EmployeeLWPDetails {
  [employeeId: string]: {
    lwp_days: number;
    total_working_days: number;
    advance_deduction: number;
    loan_deduction: number;
    other_deductions: number;
  };
}

/**
 * MonthlyProcessing Component - Process monthly payouts with LWP integration
 */
const MonthlyProcessing: React.FC = () => {
  const theme = useTheme();
  const [selectedYear, setSelectedYear] = useState<number>(monthlyPayoutService.getCurrentFinancialYear());
  const [selectedMonth, setSelectedMonth] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [bulkComputing, setBulkComputing] = useState<boolean>(false);
  const [bulkApproving, setBulkApproving] = useState<boolean>(false);
  const [bulkProcessingPayouts, setBulkProcessingPayouts] = useState<boolean>(false);
  
  // Data states
  const [monthlyPayouts, setMonthlyPayouts] = useState<MonthlyPayoutResponse[]>([]);
  const [summary, setSummary] = useState<PayoutSummary | null>(null);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [selectedEmployees, setSelectedEmployees] = useState<string[]>([]);
  const [employeeLWPDetails, setEmployeeLWPDetails] = useState<EmployeeLWPDetails>({});
  
  // Dialog states
  const [bulkComputeDialogOpen, setBulkComputeDialogOpen] = useState<boolean>(false);
  const [lwpDialogOpen, setLwpDialogOpen] = useState<boolean>(false);
  const [currentEmployee, setCurrentEmployee] = useState<Employee | null>(null);

  const { isLoading } = usePayrollsQuery({
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

  // Fetch monthly payouts and summary
  const fetchData = async () => {
    if (!selectedMonth) return;
    
    try {
      setError(null);
      
      // Fetch monthly payouts
      const filters: PayoutSearchFilters = {
        year: selectedYear,
        month: selectedMonth,
        page: 1,
        size: 1000
      };
      
      const [payoutsResponse, summaryResponse] = await Promise.all([
        monthlyPayoutService.searchPayouts(filters),
        monthlyPayoutService.getPayoutSummary(selectedMonth, selectedYear).catch(() => null)
      ]);
      
      setMonthlyPayouts(payoutsResponse.payouts);
      setSummary(summaryResponse);
      
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to fetch payout data. Please try again.');
    }
  };

  // Fetch employees for bulk computation
  const fetchEmployees = async () => {
    try {
      // Mock employee data - in real implementation, this would come from user service
      const mockEmployees: Employee[] = [
        { employee_id: 'EMP001', name: 'John Doe', department: 'Engineering', designation: 'Software Engineer', base_salary: 50000 },
        { employee_id: 'EMP002', name: 'Jane Smith', department: 'HR', designation: 'HR Manager', base_salary: 60000 },
        { employee_id: 'EMP003', name: 'Mike Johnson', department: 'Finance', designation: 'Accountant', base_salary: 45000 },
        { employee_id: 'EMP004', name: 'Sarah Wilson', department: 'Engineering', designation: 'Senior Developer', base_salary: 70000 },
        { employee_id: 'EMP005', name: 'David Brown', department: 'Marketing', designation: 'Marketing Manager', base_salary: 55000 }
      ];
      
      setEmployees(mockEmployees);
      
      // Initialize LWP details for all employees
      const initialLWPDetails: EmployeeLWPDetails = {};
      mockEmployees.forEach(emp => {
        initialLWPDetails[emp.employee_id] = {
          lwp_days: 0,
          total_working_days: 30,
          advance_deduction: 0,
          loan_deduction: 0,
          other_deductions: 0
        };
      });
      setEmployeeLWPDetails(initialLWPDetails);
      
    } catch (err) {
      console.error('Error fetching employees:', err);
      setError('Failed to fetch employee data.');
    }
  };

  useEffect(() => {
    fetchData();
  }, [selectedYear, selectedMonth]);

  useEffect(() => {
    fetchEmployees();
  }, []);

  const handleYearChange = (event: SelectChangeEvent<string>): void => {
    setSelectedYear(Number(event.target.value));
  };

  const handleMonthChange = (event: SelectChangeEvent<string>): void => {
    setSelectedMonth(event.target.value ? parseInt(event.target.value) : null);
  };

  const handleBulkCompute = async (): Promise<void> => {
    if (!selectedMonth || selectedEmployees.length === 0) {
      setError('Please select a month and at least one employee');
      return;
    }

    setBulkComputing(true);
    setError(null);

    try {
      const bulkRequest: BulkPayoutRequest = {
        month: selectedMonth,
        year: selectedYear,
        employee_ids: selectedEmployees,
        employee_lwp_details: Object.fromEntries(
          selectedEmployees.map(empId => [empId, employeeLWPDetails[empId]]).filter(([_, details]) => details)
        ),
        auto_approve: false
      };

      const result = await monthlyPayoutService.computeBulkPayouts(bulkRequest);
      
      setSuccess(`Successfully computed ${result.summary.successful_count} payouts. ${result.summary.failed_count} failed.`);
      setBulkComputeDialogOpen(false);
      await fetchData(); // Refresh data
      
    } catch (err) {
      console.error('Error computing bulk payouts:', err);
      setError('Failed to compute payouts. Please try again.');
    } finally {
      setBulkComputing(false);
    }
  };

  const handleBulkApprove = async (): Promise<void> => {
    if (!selectedMonth) return;
    
    setBulkApproving(true);
    setError(null);
    
    try {
      const calculatedPayouts = monthlyPayouts.filter(p => p.status === 'calculated');
      const employeeIds = calculatedPayouts.map(p => p.employee_id);
      
      if (employeeIds.length === 0) {
        setError('No calculated payouts found to approve');
        return;
      }
      
      const result = await monthlyPayoutService.bulkApprove(selectedMonth, selectedYear, employeeIds);
      setSuccess(`Successfully approved ${result.successful.length} payouts`);
      await fetchData(); // Refresh data
      
    } catch (err) {
      console.error('Error bulk approving:', err);
      setError('Failed to approve payouts. Please try again.');
    } finally {
      setBulkApproving(false);
    }
  };

  const handleBulkProcess = async (): Promise<void> => {
    if (!selectedMonth) return;
    
    setBulkProcessingPayouts(true);
    setError(null);
    
    try {
      const approvedPayouts = monthlyPayouts.filter(p => p.status === 'approved');
      const employeeIds = approvedPayouts.map(p => p.employee_id);
      
      if (employeeIds.length === 0) {
        setError('No approved payouts found to process');
        return;
      }
      
      const result = await monthlyPayoutService.bulkProcess(selectedMonth, selectedYear, employeeIds);
      setSuccess(`Successfully processed ${result.successful.length} payouts`);
      await fetchData(); // Refresh data
      
    } catch (err) {
      console.error('Error bulk processing:', err);
      setError('Failed to process payouts. Please try again.');
    } finally {
      setBulkProcessingPayouts(false);
    }
  };

  const handleEmployeeSelection = (employeeId: string, checked: boolean) => {
    if (checked) {
      setSelectedEmployees(prev => [...prev, employeeId]);
    } else {
      setSelectedEmployees(prev => prev.filter(id => id !== employeeId));
    }
  };

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedEmployees(employees.map(emp => emp.employee_id));
    } else {
      setSelectedEmployees([]);
    }
  };

  const handleLWPDetailsChange = (employeeId: string, field: keyof EmployeeLWPDetails[string], value: number) => {
    setEmployeeLWPDetails(prev => ({
      ...prev,
      [employeeId]: {
        lwp_days: 0,
        total_working_days: 30,
        advance_deduction: 0,
        loan_deduction: 0,
        other_deductions: 0,
        ...prev[employeeId],
        [field]: value
      }
    }));
  };

  const openLWPDialog = (employee: Employee) => {
    setCurrentEmployee(employee);
    setLwpDialogOpen(true);
  };

  if (isLoading) {
    return (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
    );
  }

  return (
      <Box>
        {/* Messages */}
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
              value={selectedMonth?.toString() || ''}
              label="Month"
              onChange={handleMonthChange}
            >
              <MenuItem value="">Select Month</MenuItem>
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
            onClick={fetchData}
            disabled={!selectedMonth}
          >
            Refresh
          </Button>
        </Box>

        {/* Action Buttons */}
        <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
          <Button
            variant="contained"
            startIcon={<CalculateIcon />}
            onClick={() => setBulkComputeDialogOpen(true)}
            disabled={!selectedMonth}
          >
            Bulk Compute Payouts
          </Button>
          
          <Button
            variant="outlined"
            startIcon={bulkApproving ? <CircularProgress size={20} /> : <CheckCircleIcon />}
            onClick={handleBulkApprove}
            disabled={bulkApproving || !selectedMonth || monthlyPayouts.filter(p => p.status === 'calculated').length === 0}
          >
            {bulkApproving ? 'Approving...' : 'Bulk Approve'}
          </Button>
          
          <Button
            variant="outlined"
            startIcon={bulkProcessingPayouts ? <CircularProgress size={20} /> : <PlayArrowIcon />}
            onClick={handleBulkProcess}
            disabled={bulkProcessingPayouts || !selectedMonth || monthlyPayouts.filter(p => p.status === 'approved').length === 0}
          >
            {bulkProcessingPayouts ? 'Processing...' : 'Bulk Process'}
          </Button>
        </Box>

        {/* Summary Cards */}
        {summary && (
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Avatar sx={{ bgcolor: theme.palette.primary.main, mr: 2 }}>
                      <PeopleIcon />
                    </Avatar>
                    <Typography variant="h6">Total Employees</Typography>
                  </Box>
                  <Typography variant="h3" color="primary.main" fontWeight="bold">
                    {summary.total_employees}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    For {monthlyPayoutService.getMonthName(selectedMonth || 1)} {selectedYear}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Avatar sx={{ bgcolor: theme.palette.success.main, mr: 2 }}>
                      <MonetizationOnIcon />
                    </Avatar>
                    <Typography variant="h6">Total Amount</Typography>
                  </Box>
                  <Typography variant="h3" color="success.main" fontWeight="bold">
                    {monthlyPayoutService.formatCurrency(summary.total_gross_amount)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Gross payout amount
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Avatar sx={{ bgcolor: theme.palette.info.main, mr: 2 }}>
                      <ReceiptIcon />
                    </Avatar>
                    <Typography variant="h6">Net Amount</Typography>
                  </Box>
                  <Typography variant="h3" color="info.main" fontWeight="bold">
                    {monthlyPayoutService.formatCurrency(summary.total_net_amount)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Net payout amount
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Avatar sx={{ bgcolor: theme.palette.warning.main, mr: 2 }}>
                      <WarningIcon />
                    </Avatar>
                    <Typography variant="h6">LWP Deduction</Typography>
                  </Box>
                  <Typography variant="h3" color="warning.main" fontWeight="bold">
                    {monthlyPayoutService.formatCurrency(summary.total_lwp_deduction)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total LWP deductions
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {/* Payouts Table */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Monthly Payouts Status
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Employee</TableCell>
                    <TableCell>Department</TableCell>
                    <TableCell>Gross Salary</TableCell>
                    <TableCell>LWP Days</TableCell>
                    <TableCell>Net Salary</TableCell>
                    <TableCell>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {monthlyPayouts.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} align="center">
                        No payouts found for the selected period
                      </TableCell>
                    </TableRow>
                  ) : (
                    monthlyPayouts.map((payout) => (
                      <TableRow key={payout.id}>
                        <TableCell>
                          <Box>
                            <Typography variant="body2" fontWeight="medium">
                              {payout.employee_name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {payout.employee_id}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>Engineering</TableCell> {/* Mock department */}
                        <TableCell>
                          {monthlyPayoutService.formatCurrency(payout.adjusted_monthly_gross)}
                        </TableCell>
                        <TableCell>
                          {payout.lwp_days > 0 ? (
                            <Chip 
                              label={`${payout.lwp_days} days`} 
                              size="small" 
                              color="warning" 
                            />
                          ) : (
                            <Chip label="0 days" size="small" color="success" />
                          )}
                        </TableCell>
                        <TableCell>
                          {monthlyPayoutService.formatCurrency(payout.monthly_net_salary)}
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={monthlyPayoutService.getStatusLabel(payout.status)}
                            color={monthlyPayoutService.getStatusColor(payout.status)}
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>

        {/* Bulk Compute Dialog */}
        <Dialog
          open={bulkComputeDialogOpen}
          onClose={() => setBulkComputeDialogOpen(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>Bulk Compute Monthly Payouts</DialogTitle>
          <DialogContent>
            <Box sx={{ mb: 3 }}>
              <Typography variant="body1" gutterBottom>
                Select employees and configure LWP details for bulk payout computation.
              </Typography>
              
              <FormControlLabel
                control={
                  <Checkbox
                    checked={selectedEmployees.length === employees.length}
                    indeterminate={selectedEmployees.length > 0 && selectedEmployees.length < employees.length}
                    onChange={(e) => handleSelectAll(e.target.checked)}
                  />
                }
                label="Select All Employees"
                sx={{ mb: 2 }}
              />
            </Box>

            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell padding="checkbox"></TableCell>
                    <TableCell>Employee</TableCell>
                    <TableCell>Department</TableCell>
                    <TableCell>Base Salary</TableCell>
                    <TableCell>LWP Details</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {employees.map((employee) => (
                    <TableRow key={employee.employee_id}>
                      <TableCell padding="checkbox">
                        <Checkbox
                          checked={selectedEmployees.includes(employee.employee_id)}
                          onChange={(e) => handleEmployeeSelection(employee.employee_id, e.target.checked)}
                        />
                      </TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="body2" fontWeight="medium">
                            {employee.name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {employee.employee_id}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>{employee.department}</TableCell>
                      <TableCell>{monthlyPayoutService.formatCurrency(employee.base_salary)}</TableCell>
                      <TableCell>
                        <Button
                          size="small"
                          variant="outlined"
                          onClick={() => openLWPDialog(employee)}
                        >
                          Configure LWP
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setBulkComputeDialogOpen(false)}>Cancel</Button>
            <Button
              variant="contained"
              onClick={handleBulkCompute}
              disabled={bulkComputing || selectedEmployees.length === 0}
              startIcon={bulkComputing ? <CircularProgress size={20} /> : <CalculateIcon />}
            >
              {bulkComputing ? 'Computing...' : 'Compute Payouts'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* LWP Details Dialog */}
        <Dialog
          open={lwpDialogOpen}
          onClose={() => setLwpDialogOpen(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>
            Configure LWP Details - {currentEmployee?.name}
          </DialogTitle>
          <DialogContent>
            {currentEmployee && (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
                <TextField
                  label="LWP Days"
                  type="number"
                  value={employeeLWPDetails[currentEmployee.employee_id]?.lwp_days || 0}
                  onChange={(e) => handleLWPDetailsChange(
                    currentEmployee.employee_id, 
                    'lwp_days', 
                    parseInt(e.target.value) || 0
                  )}
                  inputProps={{ min: 0, max: 31 }}
                />
                
                <TextField
                  label="Total Working Days"
                  type="number"
                  value={employeeLWPDetails[currentEmployee.employee_id]?.total_working_days || 30}
                  onChange={(e) => handleLWPDetailsChange(
                    currentEmployee.employee_id, 
                    'total_working_days', 
                    parseInt(e.target.value) || 30
                  )}
                  inputProps={{ min: 1, max: 31 }}
                />
                
                <TextField
                  label="Advance Deduction"
                  type="number"
                  value={employeeLWPDetails[currentEmployee.employee_id]?.advance_deduction || 0}
                  onChange={(e) => handleLWPDetailsChange(
                    currentEmployee.employee_id, 
                    'advance_deduction', 
                    parseFloat(e.target.value) || 0
                  )}
                  inputProps={{ min: 0 }}
                />
                
                <TextField
                  label="Loan Deduction"
                  type="number"
                  value={employeeLWPDetails[currentEmployee.employee_id]?.loan_deduction || 0}
                  onChange={(e) => handleLWPDetailsChange(
                    currentEmployee.employee_id, 
                    'loan_deduction', 
                    parseFloat(e.target.value) || 0
                  )}
                  inputProps={{ min: 0 }}
                />
                
                <TextField
                  label="Other Deductions"
                  type="number"
                  value={employeeLWPDetails[currentEmployee.employee_id]?.other_deductions || 0}
                  onChange={(e) => handleLWPDetailsChange(
                    currentEmployee.employee_id, 
                    'other_deductions', 
                    parseFloat(e.target.value) || 0
                  )}
                  inputProps={{ min: 0 }}
                />
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setLwpDialogOpen(false)}>Close</Button>
          </DialogActions>
        </Dialog>
      </Box>
  );
};

export default MonthlyProcessing; 