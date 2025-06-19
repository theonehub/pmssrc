import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
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
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Calculate as CalculateIcon,
  Visibility as VisibilityIcon
} from '@mui/icons-material';
import { salaryProcessingApi } from '../../shared/api/salaryProcessingApi';

interface MonthlySalary {
  employee_id: string;
  employee_name: string | null;
  employee_email: string | null;
  department: string | null;
  designation: string | null;
  month: number;
  year: number;
  tax_year: string;
  gross_salary: number;
  net_salary: number;
  total_deductions: number;
  tds: number;
  status: string;
  computation_date: string | null;
  created_at: string;
  updated_at: string;
}

interface SalarySummary {
  month: number;
  year: number;
  tax_year: string;
  total_employees: number;
  computed_count: number;
  pending_count: number;
  approved_count: number;
  paid_count: number;
  total_gross_payroll: number;
  total_net_payroll: number;
  total_deductions: number;
  total_tds: number;
  computation_completion_rate: number;
}

interface BulkComputeResult {
  total_requested: number;
  successful: number;
  failed: number;
  skipped: number;
  errors: Array<{ employee_id: string; error: string }>;
  computation_summary: any;
}

const SalaryProcessing: React.FC = () => {
  // State management
  const [selectedMonth, setSelectedMonth] = useState<number>(new Date().getMonth() + 1);
  const [selectedYear] = useState<number>(new Date().getFullYear());
  const [currentFinancialYear] = useState<string>(() => {
    const now = new Date();
    const currentYear = now.getFullYear();
    const currentMonth = now.getMonth() + 1;
    
    if (currentMonth >= 4) {
      return `${currentYear}-${String(currentYear + 1).slice(2)}`;
    } else {
      return `${currentYear - 1}-${String(currentYear).slice(2)}`;
    }
  });

  const [salaries, setSalaries] = useState<MonthlySalary[]>([]);
  const [summary, setSummary] = useState<SalarySummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [bulkComputing, setBulkComputing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Dialog states
  const [bulkComputeDialogOpen, setBulkComputeDialogOpen] = useState(false);
  const [bulkComputeResult, setBulkComputeResult] = useState<BulkComputeResult | null>(null);
  const [selectedSalary, setSelectedSalary] = useState<MonthlySalary | null>(null);
  const [salaryDetailDialogOpen, setSalaryDetailDialogOpen] = useState(false);

  // Month options
  const monthOptions = [
    { value: 1, label: 'January' },
    { value: 2, label: 'February' },
    { value: 3, label: 'March' },
    { value: 4, label: 'April' },
    { value: 5, label: 'May' },
    { value: 6, label: 'June' },
    { value: 7, label: 'July' },
    { value: 8, label: 'August' },
    { value: 9, label: 'September' },
    { value: 10, label: 'October' },
    { value: 11, label: 'November' },
    { value: 12, label: 'December' }
  ];

  // Status configuration
  const statusConfig = {
    not_computed: { color: 'default', label: 'Not Computed' },
    pending: { color: 'warning', label: 'Pending' },
    computed: { color: 'info', label: 'Computed' },
    approved: { color: 'success', label: 'Approved' },
    paid: { color: 'success', label: 'Paid' },
    rejected: { color: 'error', label: 'Rejected' }
  };

  // Fetch data
  const fetchSalaries = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await salaryProcessingApi.getMonthlySalariesForPeriod(
        selectedMonth,
        selectedYear
      );
      setSalaries(response.items);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch salary data');
    } finally {
      setLoading(false);
    }
  };

  const fetchSummary = async () => {
    try {
      const summaryData = await salaryProcessingApi.getMonthlySalarySummary(
        selectedMonth,
        selectedYear
      );
      setSummary(summaryData);
    } catch (err: any) {
      console.error('Failed to fetch summary:', err);
    }
  };

  // Effects
  useEffect(() => {
    fetchSalaries();
    fetchSummary();
  }, [selectedMonth, selectedYear]);

  // Handlers
  const handleMonthChange = (event: any) => {
    setSelectedMonth(event.target.value);
  };

  const handleRefresh = () => {
    fetchSalaries();
    fetchSummary();
  };

  const handleBulkCompute = async () => {
    setBulkComputing(true);
    setError(null);
    
    try {
      const result = await salaryProcessingApi.bulkComputeMonthlySalaries({
        month: selectedMonth,
        year: selectedYear,
        tax_year: currentFinancialYear,
        force_recompute: false
      });
      
      setBulkComputeResult(result);
      setBulkComputeDialogOpen(true);
      
      // Refresh data after bulk compute
      await fetchSalaries();
      await fetchSummary();
      
      setSuccess(`Bulk computation completed: ${result.successful} successful, ${result.failed} failed, ${result.skipped} skipped`);
    } catch (err: any) {
      setError(err.message || 'Failed to compute salaries');
    } finally {
      setBulkComputing(false);
    }
  };

  const handleViewSalaryDetails = (salary: MonthlySalary) => {
    setSelectedSalary(salary);
    setSalaryDetailDialogOpen(true);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const getStatusChip = (status: string) => {
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.not_computed;
    return (
      <Chip
        label={config.label}
        color={config.color as any}
        size="small"
        variant="outlined"
      />
    );
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header Section */}
      <Typography variant="h4" component="h1" gutterBottom>
        Salary Processing
      </Typography>
      
      <Typography variant="subtitle1" color="text.secondary" gutterBottom>
        Current Financial Year: {currentFinancialYear}
      </Typography>

      {/* Controls Section */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} sm={4}>
              <FormControl fullWidth>
                <InputLabel>Select Month</InputLabel>
                <Select
                  value={selectedMonth}
                  label="Select Month"
                  onChange={handleMonthChange}
                >
                  {monthOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={8}>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button
                  variant="outlined"
                  startIcon={<RefreshIcon />}
                  onClick={handleRefresh}
                  disabled={loading}
                >
                  Refresh
                </Button>
                
                <Button
                  variant="contained"
                  startIcon={bulkComputing ? <CircularProgress size={20} /> : <CalculateIcon />}
                  onClick={handleBulkCompute}
                  disabled={bulkComputing || loading}
                  color="primary"
                >
                  {bulkComputing ? 'Computing...' : 'Bulk Compute Salaries'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Summary Section */}
      {summary && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Summary for {monthOptions.find(m => m.value === selectedMonth)?.label} {selectedYear}
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={6} sm={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="primary">
                    {summary.total_employees}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Employees
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={6} sm={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="success.main">
                    {summary.computed_count}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Computed
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={6} sm={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="info.main">
                    {formatCurrency(summary.total_gross_payroll)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Gross
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={6} sm={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="success.main">
                    {summary.computation_completion_rate.toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Completion Rate
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Alerts */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {/* Salary Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Monthly Salary Records
          </Typography>
          
          {loading ? (
            <Box display="flex" justifyContent="center" p={3}>
              <CircularProgress />
            </Box>
          ) : (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Employee</TableCell>
                    <TableCell>Department</TableCell>
                    <TableCell align="right">Gross Salary</TableCell>
                    <TableCell align="right">Net Salary</TableCell>
                    <TableCell align="right">TDS</TableCell>
                    <TableCell align="center">Status</TableCell>
                    <TableCell align="center">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {salaries.map((salary) => (
                    <TableRow key={`${salary.employee_id}-${salary.month}-${salary.year}`}>
                      <TableCell>
                        <Box>
                          <Typography variant="body2" fontWeight="medium">
                            {salary.employee_name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {salary.employee_id}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>{salary.department || 'N/A'}</TableCell>
                      <TableCell align="right">
                        {formatCurrency(salary.gross_salary)}
                      </TableCell>
                      <TableCell align="right">
                        {formatCurrency(salary.net_salary)}
                      </TableCell>
                      <TableCell align="right">
                        {formatCurrency(salary.tds)}
                      </TableCell>
                      <TableCell align="center">
                        {getStatusChip(salary.status)}
                      </TableCell>
                      <TableCell align="center">
                        <Tooltip title="View Details">
                          <IconButton
                            size="small"
                            onClick={() => handleViewSalaryDetails(salary)}
                          >
                            <VisibilityIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                  {salaries.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={7} align="center">
                        <Typography color="text.secondary">
                          No salary records found for the selected period
                        </Typography>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* Bulk Compute Result Dialog */}
      <Dialog
        open={bulkComputeDialogOpen}
        onClose={() => setBulkComputeDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Bulk Computation Results</DialogTitle>
        <DialogContent>
          {bulkComputeResult && (
            <Box>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="primary">
                      {bulkComputeResult.total_requested}
                    </Typography>
                    <Typography variant="caption">Total</Typography>
                  </Box>
                </Grid>
                <Grid item xs={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="success.main">
                      {bulkComputeResult.successful}
                    </Typography>
                    <Typography variant="caption">Successful</Typography>
                  </Box>
                </Grid>
                <Grid item xs={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="error.main">
                      {bulkComputeResult.failed}
                    </Typography>
                    <Typography variant="caption">Failed</Typography>
                  </Box>
                </Grid>
                <Grid item xs={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="warning.main">
                      {bulkComputeResult.skipped}
                    </Typography>
                    <Typography variant="caption">Skipped</Typography>
                  </Box>
                </Grid>
              </Grid>

              {bulkComputeResult.errors.length > 0 && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Errors:
                  </Typography>
                  {bulkComputeResult.errors.map((error, index) => (
                    <Alert key={index} severity="error" sx={{ mb: 1 }}>
                      <strong>{error.employee_id}:</strong> {error.error}
                    </Alert>
                  ))}
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBulkComputeDialogOpen(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Salary Detail Dialog */}
      <Dialog
        open={salaryDetailDialogOpen}
        onClose={() => setSalaryDetailDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Salary Details - {selectedSalary?.employee_name}
        </DialogTitle>
        <DialogContent>
          {selectedSalary && (
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography variant="h6" gutterBottom>Employee Information</Typography>
                <Typography><strong>ID:</strong> {selectedSalary.employee_id}</Typography>
                <Typography><strong>Name:</strong> {selectedSalary.employee_name}</Typography>
                <Typography><strong>Department:</strong> {selectedSalary.department}</Typography>
                <Typography><strong>Designation:</strong> {selectedSalary.designation}</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="h6" gutterBottom>Salary Information</Typography>
                <Typography><strong>Period:</strong> {monthOptions.find(m => m.value === selectedSalary.month)?.label} {selectedSalary.year}</Typography>
                <Typography><strong>Tax Year:</strong> {selectedSalary.tax_year}</Typography>
                <Typography><strong>Status:</strong> {getStatusChip(selectedSalary.status)}</Typography>
                <Typography><strong>Gross:</strong> {formatCurrency(selectedSalary.gross_salary)}</Typography>
                <Typography><strong>Net:</strong> {formatCurrency(selectedSalary.net_salary)}</Typography>
                <Typography><strong>Deductions:</strong> {formatCurrency(selectedSalary.total_deductions)}</Typography>
                <Typography><strong>TDS:</strong> {formatCurrency(selectedSalary.tds)}</Typography>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSalaryDetailDialogOpen(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SalaryProcessing; 