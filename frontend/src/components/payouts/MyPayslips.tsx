import React, { useState } from 'react';
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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip,
  Chip,
  SelectChangeEvent
} from '@mui/material';
import {
  Download as DownloadIcon,
  Visibility as VisibilityIcon,
  Receipt as ReceiptIcon
} from '@mui/icons-material';
import payoutService from '../../shared/services/payoutService';
import { usePayrollsQuery, Payout as PayrollPayout } from '../../shared/hooks/usePayrolls';

// Type definitions
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

interface YearOption {
  value: number;
  label: string;
}

interface MonthOption {
  value: number;
  label: string;
}

const MyPayslips: React.FC = () => {
  const [selectedYear, setSelectedYear] = useState<number>(payoutService.getCurrentFinancialYear());
  const [selectedMonth, setSelectedMonth] = useState<number | null>(null);
  const [selectedPayout, setSelectedPayout] = useState<PayrollPayout | null>(null);
  const [payslipData, setPayslipData] = useState<PayslipData | null>(null);
  const [payslipDialogOpen, setPayslipDialogOpen] = useState<boolean>(false);
  const [downloadLoading, setDownloadLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const { data: payoutsData, isLoading } = usePayrollsQuery({
    year: selectedYear,
    month: selectedMonth
  });

  const payouts = payoutsData?.payouts || [];

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

  const handleViewPayslip = async (payout: PayrollPayout): Promise<void> => {
    try {
      setSelectedPayout(payout);
      setPayslipDialogOpen(true);
      
      // Load payslip data
      const data: PayslipData = await payoutService.getPayslipData(payout.id);
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

  const handleDownloadPayslip = async (payoutId: string): Promise<void> => {
    try {
      setDownloadLoading(payoutId);
      await payoutService.downloadPayslip(payoutId);
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

  const handleClosePayslipDialog = (): void => {
    setPayslipDialogOpen(false);
    setSelectedPayout(null);
    setPayslipData(null);
  };

  const handleYearChange = (event: SelectChangeEvent<string>): void => {
    setSelectedYear(Number(event.target.value));
  };

  const handleMonthChange = (event: SelectChangeEvent<string>): void => {
    setSelectedMonth(event.target.value ? parseInt(event.target.value) : null);
  };

  if (isLoading) {
    return (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
    );
  }

  if (error) {
    return (
      <Box>
        <Alert severity="error" sx={{ m: 3 }}>
          {error}
        </Alert>
      </Box>
    );
  }

  return (
      <Box>
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
        </Box>

        <Card>
          <CardContent>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Period</TableCell>
                    <TableCell>Total Amount</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {payouts.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={4} align="center">
                        No payslips found for the selected period
                      </TableCell>
                    </TableRow>
                  ) : (
                    payouts.map((payout) => (
                      <TableRow key={payout.id}>
                        <TableCell>
                          {payoutService.formatDateRange(payout.pay_period_start, payout.pay_period_end)}
                        </TableCell>
                        <TableCell>{payoutService.formatCurrency(payout.total_amount)}</TableCell>
                        <TableCell>
                          <Chip
                            label={payout.status}
                            color={payout.status === 'paid' ? 'success' : 'default'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 1 }}>
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
                                onClick={() => handleDownloadPayslip(payout.id)}
                                disabled={!!downloadLoading}
                              >
                                {downloadLoading === payout.id ? (
                                  <CircularProgress size={20} />
                                ) : (
                                  <DownloadIcon />
                                )}
                              </IconButton>
                            </Tooltip>
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

        {/* Payslip Dialog */}
        <Dialog
          open={payslipDialogOpen}
          onClose={handleClosePayslipDialog}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="h6">Payslip Details</Typography>
              <IconButton onClick={handleClosePayslipDialog}>
                <ReceiptIcon />
              </IconButton>
            </Box>
          </DialogTitle>
          <DialogContent>
            {payslipData ? (
              <Box>
                {/* Company Information */}
                <Box sx={{ mb: 3, textAlign: 'center' }}>
                  <Typography variant="h5" gutterBottom>
                    {payslipData.company_name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {payslipData.company_address}
                  </Typography>
                </Box>

                {/* Employee Information */}
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Employee Information
                  </Typography>
                  <Box display="flex" gap={2}>
                    <Box flex={1}>
                      <Typography variant="body2">
                        <strong>Name:</strong> {payslipData.employee_name}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Employee Code:</strong> {payslipData.employee_code}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Department:</strong> {payslipData.department}
                      </Typography>
                    </Box>
                    <Box flex={1}>
                      <Typography variant="body2">
                        <strong>Designation:</strong> {payslipData.designation}
                      </Typography>
                      <Typography variant="body2">
                        <strong>PAN:</strong> {payslipData.pan_number}
                      </Typography>
                      <Typography variant="body2">
                        <strong>UAN:</strong> {payslipData.uan_number}
                      </Typography>
                    </Box>
                  </Box>
                </Box>

                {/* Pay Period Information */}
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Pay Period Information
                  </Typography>
                  <Box display="flex" gap={2}>
                    <Box flex={1}>
                      <Typography variant="body2">
                        <strong>Pay Period:</strong> {payslipData.pay_period}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Payout Date:</strong> {payslipData.payout_date}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Days in Month:</strong> {payslipData.days_in_month}
                      </Typography>
                    </Box>
                    <Box flex={1}>
                      <Typography variant="body2">
                        <strong>Days Worked:</strong> {payslipData.days_worked}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Tax Regime:</strong> {payslipData.tax_regime}
                      </Typography>
                    </Box>
                  </Box>
                </Box>

                {/* Earnings and Deductions */}
                <Box sx={{ mb: 4 }}>
                  <Box display="flex" gap={2}>
                    <Box flex={1}>
                      <Typography variant="h6" gutterBottom>
                        Earnings
                      </Typography>
                      <TableContainer>
                        <Table size="small">
                          <TableBody>
                            {Object.entries(payslipData.earnings).map(([key, value]) => (
                              <TableRow key={key}>
                                <TableCell>{key.replace(/_/g, ' ').toUpperCase()}</TableCell>
                                <TableCell align="right">
                                  {payoutService.formatCurrency(value)}
                                </TableCell>
                              </TableRow>
                            ))}
                            <TableRow>
                              <TableCell><strong>Total Earnings</strong></TableCell>
                              <TableCell align="right">
                                <strong>{payoutService.formatCurrency(payslipData.total_earnings)}</strong>
                              </TableCell>
                            </TableRow>
                          </TableBody>
                        </Table>
                      </TableContainer>
                    </Box>
                    <Box flex={1}>
                      <Typography variant="h6" gutterBottom>
                        Deductions
                      </Typography>
                      <TableContainer>
                        <Table size="small">
                          <TableBody>
                            {Object.entries(payslipData.deductions).map(([key, value]) => (
                              <TableRow key={key}>
                                <TableCell>{key.replace(/_/g, ' ').toUpperCase()}</TableCell>
                                <TableCell align="right">
                                  {payoutService.formatCurrency(value)}
                                </TableCell>
                              </TableRow>
                            ))}
                            <TableRow>
                              <TableCell><strong>Total Deductions</strong></TableCell>
                              <TableCell align="right">
                                <strong>{payoutService.formatCurrency(payslipData.total_deductions)}</strong>
                              </TableCell>
                            </TableRow>
                          </TableBody>
                        </Table>
                      </TableContainer>
                    </Box>
                  </Box>
                </Box>

                {/* Net Pay */}
                <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'primary.light', borderRadius: 1 }}>
                  <Typography variant="h5">
                    Net Pay: {payoutService.formatCurrency(payslipData.net_pay)}
                  </Typography>
                </Box>
              </Box>
            ) : (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                <CircularProgress />
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClosePayslipDialog}>Close</Button>
            {selectedPayout && (
              <Button
                variant="contained"
                onClick={() => handleDownloadPayslip(selectedPayout.id)}
                disabled={!!downloadLoading}
              >
                {downloadLoading === selectedPayout.id ? 'Downloading...' : 'Download PDF'}
              </Button>
            )}
          </DialogActions>
        </Dialog>
      </Box>
  );
};

export default MyPayslips; 