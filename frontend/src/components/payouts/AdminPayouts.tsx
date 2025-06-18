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
  SelectChangeEvent,
  Grid
} from '@mui/material';
import {
  Download as DownloadIcon,
  Visibility as VisibilityIcon,
  CheckCircle as CheckCircleIcon,
  PlayArrow as PlayArrowIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import monthlyPayoutService, { MonthlyPayoutResponse, PayoutSearchFilters } from '../../shared/services/monthlyPayoutService';
import { usePayrollsQuery } from '../../shared/hooks/usePayrolls';

// Type definitions
interface YearOption {
  value: number;
  label: string;
}

interface MonthOption {
  value: number;
  label: string;
}

const AdminPayouts: React.FC = () => {
  const [error, setError] = useState<string | null>(null);
  const [selectedMonth, setSelectedMonth] = useState<number | null>(null);
  const [selectedYear, setSelectedYear] = useState<number>(monthlyPayoutService.getCurrentFinancialYear());
  const [selectedPayout, setSelectedPayout] = useState<MonthlyPayoutResponse | null>(null);
  const [payoutDialogOpen, setPayoutDialogOpen] = useState<boolean>(false);
  const [monthlyPayouts, setMonthlyPayouts] = useState<MonthlyPayoutResponse[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [approving, setApproving] = useState<string | null>(null);
  const [processing, setProcessing] = useState<string | null>(null);

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

  // Fetch monthly payouts
  const fetchMonthlyPayouts = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const filters: PayoutSearchFilters = {
        year: selectedYear,
        ...(selectedMonth && { month: selectedMonth }),
        page: 1,
        size: 100
      };
      
      const response = await monthlyPayoutService.searchPayouts(filters);
      setMonthlyPayouts(response.payouts);
    } catch (err) {
      console.error('Error fetching monthly payouts:', err);
      setError('Failed to fetch monthly payouts. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Fetch data when filters change
  useEffect(() => {
    fetchMonthlyPayouts();
  }, [selectedYear, selectedMonth]);

  // Month options
  const monthOptions: MonthOption[] = Array.from({ length: 12 }, (_, i) => ({
    value: i + 1,
    label: monthlyPayoutService.getMonthName(i + 1)
  }));

  const handleMonthChange = (event: SelectChangeEvent<string>): void => {
    setSelectedMonth(event.target.value ? parseInt(event.target.value) : null);
  };

  const handleYearChange = (event: SelectChangeEvent<string>): void => {
    setSelectedYear(Number(event.target.value));
  };

  const handleViewPayout = (payout: MonthlyPayoutResponse): void => {
    setSelectedPayout(payout);
    setPayoutDialogOpen(true);
  };

  const handleClosePayoutDialog = (): void => {
    setPayoutDialogOpen(false);
    setSelectedPayout(null);
  };

  const handleApprovePayout = async (payout: MonthlyPayoutResponse): Promise<void> => {
    try {
      setApproving(payout.id);
      await monthlyPayoutService.approvePayout(payout.employee_id, payout.month, payout.year);
      await fetchMonthlyPayouts(); // Refresh data
    } catch (err) {
      console.error('Error approving payout:', err);
      setError('Failed to approve payout. Please try again.');
    } finally {
      setApproving(null);
    }
  };

  const handleProcessPayout = async (payout: MonthlyPayoutResponse): Promise<void> => {
    try {
      setProcessing(payout.id);
      await monthlyPayoutService.processPayout(payout.employee_id, payout.month, payout.year);
      await fetchMonthlyPayouts(); // Refresh data
    } catch (err) {
      console.error('Error processing payout:', err);
      setError('Failed to process payout. Please try again.');
    } finally {
      setProcessing(null);
    }
  };

  const handleDownloadPayslip = async (payout: MonthlyPayoutResponse): Promise<void> => {
    try {
      await monthlyPayoutService.downloadPayslip(payout.employee_id, payout.month, payout.year);
    } catch (err) {
      console.error('Error downloading payslip:', err);
      setError('Failed to download payslip. Please try again.');
    }
  };

  if (loading || isLoading) {
    return (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
    );
  }

  if (error) {
    return (
        <Alert severity="error" sx={{ m: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
    );
  }

  // Calculate summary statistics
  const summary = {
    totalEmployees: monthlyPayouts.length,
    totalGrossAmount: monthlyPayouts.reduce((sum, p) => sum + p.adjusted_monthly_gross, 0),
    totalNetAmount: monthlyPayouts.reduce((sum, p) => sum + p.monthly_net_salary, 0),
    totalLWPDeduction: monthlyPayouts.reduce((sum, p) => sum + p.lwp_deduction_amount, 0),
    statusCounts: monthlyPayouts.reduce((acc, p) => {
      acc[p.status] = (acc[p.status] || 0) + 1;
      return acc;
    }, {} as Record<string, number>)
  };

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
              value={selectedMonth?.toString() || ''}
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
            onClick={fetchMonthlyPayouts}
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>

        {/* Summary Cards */}
        {monthlyPayouts.length > 0 && (
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" color="primary">
                  {summary.totalEmployees}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Employees
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" color="success.main">
                  {monthlyPayoutService.formatCurrency(summary.totalGrossAmount)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Gross Amount
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" color="info.main">
                  {monthlyPayoutService.formatCurrency(summary.totalNetAmount)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Net Amount
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" color="warning.main">
                  {monthlyPayoutService.formatCurrency(summary.totalLWPDeduction)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total LWP Deduction
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        )}

        {/* Monthly Payouts Table */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Monthly Payouts
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Employee</TableCell>
                    <TableCell>Month/Year</TableCell>
                    <TableCell>Gross Salary</TableCell>
                    <TableCell>LWP Days</TableCell>
                    <TableCell>LWP Deduction</TableCell>
                    <TableCell>Net Salary</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {monthlyPayouts.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={8} align="center">
                        No monthly payouts found for the selected period
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
                        <TableCell>
                          {monthlyPayoutService.getMonthName(payout.month)} {payout.year}
                        </TableCell>
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
                          {monthlyPayoutService.formatCurrency(payout.lwp_deduction_amount)}
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
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <Tooltip title="View Details">
                              <IconButton
                                size="small"
                                onClick={() => handleViewPayout(payout)}
                              >
                                <VisibilityIcon />
                              </IconButton>
                            </Tooltip>
                            
                            {payout.status === 'calculated' && (
                              <Tooltip title="Approve">
                                <IconButton
                                  size="small"
                                  onClick={() => handleApprovePayout(payout)}
                                  disabled={!!approving}
                                >
                                  {approving === payout.id ? (
                                    <CircularProgress size={16} />
                                  ) : (
                                    <CheckCircleIcon />
                                  )}
                                </IconButton>
                              </Tooltip>
                            )}
                            
                            {payout.status === 'approved' && (
                              <Tooltip title="Process">
                                <IconButton
                                  size="small"
                                  onClick={() => handleProcessPayout(payout)}
                                  disabled={!!processing}
                                >
                                  {processing === payout.id ? (
                                    <CircularProgress size={16} />
                                  ) : (
                                    <PlayArrowIcon />
                                  )}
                                </IconButton>
                              </Tooltip>
                            )}
                            
                            {['processed', 'paid'].includes(payout.status) && (
                              <Tooltip title="Download Payslip">
                                <IconButton
                                  size="small"
                                  onClick={() => handleDownloadPayslip(payout)}
                                >
                                  <DownloadIcon />
                                </IconButton>
                              </Tooltip>
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

        {/* Payout Details Dialog */}
        <Dialog
          open={payoutDialogOpen}
          onClose={handleClosePayoutDialog}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>
            <Box display="flex" alignItems="center" gap={1}>
              <DownloadIcon color="primary" />
              <Typography variant="h6">
                Payout Details - {selectedPayout?.employee_name}
              </Typography>
            </Box>
          </DialogTitle>
          <DialogContent>
            {selectedPayout && (
              <Box sx={{ p: 2 }}>
                {/* Basic Info */}
                <Grid container spacing={2} sx={{ mb: 3 }}>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      <strong>Employee ID:</strong> {selectedPayout.employee_id}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      <strong>Period:</strong> {monthlyPayoutService.getMonthName(selectedPayout.month)} {selectedPayout.year}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      <strong>Status:</strong> 
                      <Chip
                        label={monthlyPayoutService.getStatusLabel(selectedPayout.status)}
                        color={monthlyPayoutService.getStatusColor(selectedPayout.status)}
                        size="small"
                        sx={{ ml: 1 }}
                      />
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      <strong>Calculation Date:</strong> {monthlyPayoutService.formatDate(selectedPayout.calculation_date)}
                    </Typography>
                  </Grid>
                </Grid>

                {/* LWP Details */}
                <Typography variant="h6" gutterBottom>LWP Details</Typography>
                <Grid container spacing={2} sx={{ mb: 3 }}>
                  <Grid item xs={4}>
                    <Typography variant="body2">
                      <strong>LWP Days:</strong> {selectedPayout.lwp_days}
                    </Typography>
                  </Grid>
                  <Grid item xs={4}>
                    <Typography variant="body2">
                      <strong>LWP Factor:</strong> {selectedPayout.lwp_factor}
                    </Typography>
                  </Grid>
                  <Grid item xs={4}>
                    <Typography variant="body2">
                      <strong>LWP Deduction:</strong> {monthlyPayoutService.formatCurrency(selectedPayout.lwp_deduction_amount)}
                    </Typography>
                  </Grid>
                </Grid>

                {/* Salary Breakdown */}
                <Typography variant="h6" gutterBottom>Salary Breakdown</Typography>
                <Grid container spacing={2} sx={{ mb: 3 }}>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      <strong>Base Gross:</strong> {monthlyPayoutService.formatCurrency(selectedPayout.base_monthly_gross)}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      <strong>Adjusted Gross:</strong> {monthlyPayoutService.formatCurrency(selectedPayout.adjusted_monthly_gross)}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      <strong>Total Deductions:</strong> {monthlyPayoutService.formatCurrency(selectedPayout.total_monthly_deductions)}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="primary">
                      <strong>Net Salary:</strong> {monthlyPayoutService.formatCurrency(selectedPayout.monthly_net_salary)}
                    </Typography>
                  </Grid>
                </Grid>

                {/* Deductions Breakdown */}
                <Typography variant="h6" gutterBottom>Deductions Breakdown</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={4}>
                    <Typography variant="body2">
                      <strong>EPF:</strong> {monthlyPayoutService.formatCurrency(selectedPayout.epf_employee_amount)}
                    </Typography>
                  </Grid>
                  <Grid item xs={4}>
                    <Typography variant="body2">
                      <strong>ESI:</strong> {monthlyPayoutService.formatCurrency(selectedPayout.esi_employee_amount)}
                    </Typography>
                  </Grid>
                  <Grid item xs={4}>
                    <Typography variant="body2">
                      <strong>Professional Tax:</strong> {monthlyPayoutService.formatCurrency(selectedPayout.professional_tax_amount)}
                    </Typography>
                  </Grid>
                  <Grid item xs={4}>
                    <Typography variant="body2">
                      <strong>TDS:</strong> {monthlyPayoutService.formatCurrency(selectedPayout.monthly_tds_amount)}
                    </Typography>
                  </Grid>
                  <Grid item xs={4}>
                    <Typography variant="body2">
                      <strong>Advance:</strong> {monthlyPayoutService.formatCurrency(selectedPayout.advance_deduction)}
                    </Typography>
                  </Grid>
                  <Grid item xs={4}>
                    <Typography variant="body2">
                      <strong>Other:</strong> {monthlyPayoutService.formatCurrency(selectedPayout.other_deductions)}
                    </Typography>
                  </Grid>
                </Grid>
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClosePayoutDialog}>Close</Button>
            {selectedPayout && ['processed', 'paid'].includes(selectedPayout.status) && (
              <Button
                variant="contained"
                startIcon={<DownloadIcon />}
                onClick={() => selectedPayout && handleDownloadPayslip(selectedPayout)}
              >
                Download Payslip
              </Button>
            )}
          </DialogActions>
        </Dialog>
      </Box>
  );
};

export default AdminPayouts; 