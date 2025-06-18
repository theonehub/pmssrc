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
  Grid,
  Divider
} from '@mui/material';
import {
  Download as DownloadIcon,
  Visibility as VisibilityIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import monthlyPayoutService, { MonthlyPayoutResponse } from '../../shared/services/monthlyPayoutService';
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

const MyPayslips: React.FC = () => {
  const [selectedYear, setSelectedYear] = useState<number>(monthlyPayoutService.getCurrentFinancialYear());
  const [selectedMonth, setSelectedMonth] = useState<number | null>(null);
  const [selectedPayout, setSelectedPayout] = useState<MonthlyPayoutResponse | null>(null);
  const [payslipDialogOpen, setPayslipDialogOpen] = useState<boolean>(false);
  const [downloadLoading, setDownloadLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [monthlyPayouts, setMonthlyPayouts] = useState<MonthlyPayoutResponse[]>([]);

  // Mock current employee ID - in real app, this would come from auth context
  const currentEmployeeId = 'EMP001';

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

  // Fetch employee's monthly payouts
  const fetchMyPayouts = async (): Promise<void> => {
    try {
      setLoading(true);
      setError(null);
      
      // Get employee history
      const history = await monthlyPayoutService.getEmployeeHistory(currentEmployeeId, 24); // Last 24 months
      
      // Filter by selected year and month if specified
      let filteredPayouts = history.filter(payout => payout.year === selectedYear);
      if (selectedMonth) {
        filteredPayouts = filteredPayouts.filter(payout => payout.month === selectedMonth);
      }
      
      setMonthlyPayouts(filteredPayouts);
      
    } catch (err) {
      console.error('Error fetching employee payouts:', err);
      setError('Failed to fetch your payslips. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMyPayouts();
  }, [selectedYear, selectedMonth]);

  const handleViewPayslip = async (payout: MonthlyPayoutResponse): Promise<void> => {
    try {
      setSelectedPayout(payout);
      setPayslipDialogOpen(true);
      
    } catch (err) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Error loading payslip data:', err);
      }
      setError('Failed to load payslip details. Please try again.');
      setPayslipDialogOpen(false);
    }
  };

  const handleDownloadPayslip = async (payout: MonthlyPayoutResponse): Promise<void> => {
    try {
      setDownloadLoading(payout.id);
      await monthlyPayoutService.downloadPayslip(payout.employee_id, payout.month, payout.year);
    } catch (err) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Error downloading payslip:', err);
      }
      setError('Failed to download payslip. Please try again.');
    } finally {
      setDownloadLoading(null);
    }
  };

  const handleClosePayslipDialog = (): void => {
    setPayslipDialogOpen(false);
    setSelectedPayout(null);
  };

  const handleYearChange = (event: SelectChangeEvent<string>): void => {
    setSelectedYear(Number(event.target.value));
  };

  const handleMonthChange = (event: SelectChangeEvent<string>): void => {
    setSelectedMonth(event.target.value ? parseInt(event.target.value) : null);
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
      <Box>
        <Alert severity="error" sx={{ m: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
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
            onClick={fetchMyPayouts}
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>

        {/* Payslips Table */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              My Payslips
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Month/Year</TableCell>
                    <TableCell>Gross Salary</TableCell>
                    <TableCell>LWP Days</TableCell>
                    <TableCell>LWP Deduction</TableCell>
                    <TableCell>Total Deductions</TableCell>
                    <TableCell>Net Salary</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {monthlyPayouts.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={8} align="center">
                        No payslips found for the selected period
                      </TableCell>
                    </TableRow>
                  ) : (
                    monthlyPayouts.map((payout) => (
                      <TableRow key={payout.id}>
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
                          {monthlyPayoutService.formatCurrency(payout.total_monthly_deductions)}
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium" color="primary">
                            {monthlyPayoutService.formatCurrency(payout.monthly_net_salary)}
                          </Typography>
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
                            {['processed', 'paid'].includes(payout.status) && (
                              <>
                                <Tooltip title="View Payslip">
                                  <IconButton
                                    size="small"
                                    onClick={() => handleViewPayslip(payout)}
                                  >
                                    <VisibilityIcon />
                                  </IconButton>
                                </Tooltip>
                                <Tooltip title="Download Payslip">
                                  <IconButton
                                    size="small"
                                    onClick={() => handleDownloadPayslip(payout)}
                                    disabled={!!downloadLoading}
                                  >
                                    {downloadLoading === payout.id ? (
                                      <CircularProgress size={16} />
                                    ) : (
                                      <DownloadIcon />
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

        {/* Payslip Details Dialog */}
        <Dialog
          open={payslipDialogOpen}
          onClose={handleClosePayslipDialog}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>
            <Box display="flex" alignItems="center" gap={1}>
              <DownloadIcon color="primary" />
              <Typography variant="h6">
                Payslip - {selectedPayout && `${monthlyPayoutService.getMonthName(selectedPayout.month)} ${selectedPayout.year}`}
              </Typography>
            </Box>
          </DialogTitle>
          <DialogContent>
            {selectedPayout && (
              <Box sx={{ p: 2 }}>
                {/* Employee Info */}
                <Grid container spacing={2} sx={{ mb: 3 }}>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      <strong>Employee Name:</strong> {selectedPayout.employee_name}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      <strong>Employee ID:</strong> {selectedPayout.employee_id}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      <strong>Pay Period:</strong> {monthlyPayoutService.getMonthName(selectedPayout.month)} {selectedPayout.year}
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
                </Grid>

                <Divider sx={{ my: 2 }} />

                {/* LWP Details */}
                <Typography variant="h6" gutterBottom>Leave Without Pay (LWP) Details</Typography>
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

                <Divider sx={{ my: 2 }} />

                {/* Salary Breakdown */}
                <Typography variant="h6" gutterBottom>Salary Breakdown</Typography>
                <Grid container spacing={2} sx={{ mb: 3 }}>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      <strong>Base Monthly Gross:</strong> {monthlyPayoutService.formatCurrency(selectedPayout.base_monthly_gross)}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      <strong>Adjusted Gross (After LWP):</strong> {monthlyPayoutService.formatCurrency(selectedPayout.adjusted_monthly_gross)}
                    </Typography>
                  </Grid>
                </Grid>

                <Divider sx={{ my: 2 }} />

                {/* Deductions Breakdown */}
                <Typography variant="h6" gutterBottom>Deductions Breakdown</Typography>
                <Grid container spacing={2} sx={{ mb: 3 }}>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      <strong>EPF (Employee):</strong> {monthlyPayoutService.formatCurrency(selectedPayout.epf_employee_amount)}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      <strong>ESI (Employee):</strong> {monthlyPayoutService.formatCurrency(selectedPayout.esi_employee_amount)}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      <strong>Professional Tax:</strong> {monthlyPayoutService.formatCurrency(selectedPayout.professional_tax_amount)}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      <strong>TDS:</strong> {monthlyPayoutService.formatCurrency(selectedPayout.monthly_tds_amount)}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      <strong>Advance Deduction:</strong> {monthlyPayoutService.formatCurrency(selectedPayout.advance_deduction)}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      <strong>Loan Deduction:</strong> {monthlyPayoutService.formatCurrency(selectedPayout.loan_deduction)}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      <strong>Other Deductions:</strong> {monthlyPayoutService.formatCurrency(selectedPayout.other_deductions)}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      <strong>LWP Deduction:</strong> {monthlyPayoutService.formatCurrency(selectedPayout.lwp_deduction_amount)}
                    </Typography>
                  </Grid>
                </Grid>

                <Divider sx={{ my: 2 }} />

                {/* Summary */}
                <Typography variant="h6" gutterBottom>Summary</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={4}>
                    <Typography variant="body1">
                      <strong>Total Deductions:</strong>
                    </Typography>
                    <Typography variant="h6" color="error">
                      {monthlyPayoutService.formatCurrency(selectedPayout.total_monthly_deductions)}
                    </Typography>
                  </Grid>
                  <Grid item xs={4}>
                    <Typography variant="body1">
                      <strong>Adjusted Gross:</strong>
                    </Typography>
                    <Typography variant="h6" color="primary">
                      {monthlyPayoutService.formatCurrency(selectedPayout.adjusted_monthly_gross)}
                    </Typography>
                  </Grid>
                  <Grid item xs={4}>
                    <Typography variant="body1">
                      <strong>Net Salary:</strong>
                    </Typography>
                    <Typography variant="h6" color="success.main">
                      {monthlyPayoutService.formatCurrency(selectedPayout.monthly_net_salary)}
                    </Typography>
                  </Grid>
                </Grid>

                {/* Workflow Info */}
                {(selectedPayout.approved_date || selectedPayout.processed_date || selectedPayout.payment_date) && (
                  <>
                    <Divider sx={{ my: 2 }} />
                    <Typography variant="h6" gutterBottom>Workflow Information</Typography>
                    <Grid container spacing={2}>
                      {selectedPayout.approved_date && (
                        <Grid item xs={4}>
                          <Typography variant="body2">
                            <strong>Approved:</strong> {monthlyPayoutService.formatDate(selectedPayout.approved_date)}
                          </Typography>
                          {selectedPayout.approved_by && (
                            <Typography variant="caption" color="text.secondary">
                              by {selectedPayout.approved_by}
                            </Typography>
                          )}
                        </Grid>
                      )}
                      {selectedPayout.processed_date && (
                        <Grid item xs={4}>
                          <Typography variant="body2">
                            <strong>Processed:</strong> {monthlyPayoutService.formatDate(selectedPayout.processed_date)}
                          </Typography>
                          {selectedPayout.processed_by && (
                            <Typography variant="caption" color="text.secondary">
                              by {selectedPayout.processed_by}
                            </Typography>
                          )}
                        </Grid>
                      )}
                      {selectedPayout.payment_date && (
                        <Grid item xs={4}>
                          <Typography variant="body2">
                            <strong>Paid:</strong> {monthlyPayoutService.formatDate(selectedPayout.payment_date)}
                          </Typography>
                          {selectedPayout.payment_reference && (
                            <Typography variant="caption" color="text.secondary">
                              Ref: {selectedPayout.payment_reference}
                            </Typography>
                          )}
                        </Grid>
                      )}
                    </Grid>
                  </>
                )}

                {selectedPayout.remarks && (
                  <>
                    <Divider sx={{ my: 2 }} />
                    <Typography variant="h6" gutterBottom>Remarks</Typography>
                    <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
                      {selectedPayout.remarks}
                    </Typography>
                  </>
                )}
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClosePayslipDialog}>Close</Button>
            {selectedPayout && ['processed', 'paid'].includes(selectedPayout.status) && (
              <Button
                variant="contained"
                startIcon={<DownloadIcon />}
                onClick={() => selectedPayout && handleDownloadPayslip(selectedPayout)}
              >
                Download PDF
              </Button>
            )}
          </DialogActions>
        </Dialog>
      </Box>
  );
};

export default MyPayslips; 