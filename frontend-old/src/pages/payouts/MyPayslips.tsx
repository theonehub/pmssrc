import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
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
  List,
  ListItem,
  ListItemText,
  SelectChangeEvent,
  Avatar,
  Chip
} from '@mui/material';
import {
  Download as DownloadIcon,
  Visibility as VisibilityIcon,
  Close as CloseIcon,
  Receipt as ReceiptIcon,
  MonetizationOn as MonetizationOnIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';
import payoutService from '../../services/payoutService';
import PageLayout from '../../layout/PageLayout';

// Type definitions
interface Payout {
  id: string;
  basic_salary: number;
  da: number;
  hra: number;
  special_allowance: number;
  bonus: number;
  transport_allowance: number;
  medical_allowance: number;
  other_allowances: number;
  reimbursements: number;
  epf_employee: number;
  esi_employee: number;
  professional_tax: number;
  tds: number;
  advance_deduction: number;
  loan_deduction: number;
  other_deductions: number;
  gross_salary: number;
  total_deductions: number;
  net_salary: number;
  pay_period_start: string;
  pay_period_end: string;
  payout_date: string;
  status: string;
}

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
  const theme = useTheme();
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [payouts, setPayouts] = useState<Payout[]>([]);
  const [selectedYear, setSelectedYear] = useState<number>(payoutService.getCurrentFinancialYear());
  const [selectedMonth, setSelectedMonth] = useState<number | null>(null);
  const [selectedPayout, setSelectedPayout] = useState<Payout | null>(null);
  const [payslipData, setPayslipData] = useState<PayslipData | null>(null);
  const [payslipDialogOpen, setPayslipDialogOpen] = useState<boolean>(false);
  const [downloadLoading, setDownloadLoading] = useState<string | null>(null);

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

  const loadPayouts = useCallback(async (): Promise<void> => {
    setLoading(true);
    setError(null);
    
    try {
      const payoutsData: Payout[] = await payoutService.getMyPayouts(
        selectedYear as any, 
        selectedMonth as any
      );
      setPayouts(payoutsData);
    } catch (err) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error loading payouts:', err);
      }
      setError('Failed to load payslips. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [selectedYear, selectedMonth]);

  useEffect(() => {
    loadPayouts();
  }, [loadPayouts]);

  const handleViewPayslip = async (payout: Payout): Promise<void> => {
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

  const renderPayslipDialog = (): React.ReactElement | null => {
    if (!selectedPayout || !payslipData) return null;

    return (
      <Dialog 
        open={payslipDialogOpen} 
        onClose={handleClosePayslipDialog}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: { minHeight: '70vh' }
        }}
      >
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">
              Payslip - {payslipData.pay_period}
            </Typography>
            <Box>
              <Tooltip title="Download Payslip">
                <IconButton 
                  onClick={() => handleDownloadPayslip(selectedPayout.id)}
                  disabled={downloadLoading === selectedPayout.id}
                >
                  {downloadLoading === selectedPayout.id ? (
                    <CircularProgress size={24} />
                  ) : (
                    <DownloadIcon />
                  )}
                </IconButton>
              </Tooltip>
              <Tooltip title="Close">
                <IconButton onClick={handleClosePayslipDialog}>
                  <CloseIcon />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
        </DialogTitle>
        
        <DialogContent dividers>
          {/* Company Header */}
          <Box textAlign="center" mb={3}>
            <Typography variant="h5" fontWeight="bold">
              {payslipData.company_name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {payslipData.company_address}
            </Typography>
            <Typography variant="h6" color="primary" mt={2}>
              SALARY SLIP
            </Typography>
          </Box>

          {/* Employee Details */}
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2, mb: 3 }}>
            <Box>
              <Typography variant="subtitle2" color="text.secondary">Employee Details</Typography>
              <Typography><strong>Name:</strong> {payslipData.employee_name}</Typography>
              <Typography><strong>Employee Code:</strong> {payslipData.employee_code || 'N/A'}</Typography>
              <Typography><strong>Department:</strong> {payslipData.department || 'N/A'}</Typography>
              <Typography><strong>Designation:</strong> {payslipData.designation || 'N/A'}</Typography>
            </Box>
            <Box>
              <Typography variant="subtitle2" color="text.secondary">Pay Details</Typography>
              <Typography><strong>Pay Period:</strong> {payslipData.pay_period}</Typography>
              <Typography><strong>Pay Date:</strong> {payslipData.payout_date}</Typography>
              <Typography><strong>Days in Month:</strong> {payslipData.days_in_month}</Typography>
              <Typography><strong>Days Worked:</strong> {payslipData.days_worked}</Typography>
            </Box>
          </Box>

          <Divider sx={{ mb: 3 }} />

          {/* Earnings and Deductions */}
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
            {/* Earnings */}
            <Box>
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
            </Box>

            {/* Deductions */}
            <Box>
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
            </Box>
          </Box>

          <Divider sx={{ my: 3 }} />

          {/* Net Pay */}
          <Box textAlign="center" p={2} bgcolor={theme.palette.primary.light} borderRadius={1}>
            <Typography variant="h5" color="primary.dark" fontWeight="bold">
              Net Pay: {payoutService.formatCurrency(payslipData.net_pay)}
            </Typography>
          </Box>

          {/* Additional Information */}
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2, mt: 2 }}>
            <Box>
              <Typography variant="subtitle2" color="text.secondary">Year to Date</Typography>
              <Typography><strong>YTD Gross:</strong> {payoutService.formatCurrency(payslipData.ytd_gross)}</Typography>
              <Typography><strong>YTD Tax Deducted:</strong> {payoutService.formatCurrency(payslipData.ytd_tax_deducted)}</Typography>
            </Box>
            <Box>
              <Typography variant="subtitle2" color="text.secondary">Tax Information</Typography>
              <Typography><strong>Tax Regime:</strong> {payslipData.tax_regime.toUpperCase()}</Typography>
              <Typography><strong>PAN:</strong> {payslipData.pan_number || 'N/A'}</Typography>
              <Typography><strong>UAN:</strong> {payslipData.uan_number || 'N/A'}</Typography>
            </Box>
          </Box>
        </DialogContent>
        
        <DialogActions>
          <Button 
            variant="contained" 
            startIcon={<DownloadIcon />}
            onClick={() => handleDownloadPayslip(selectedPayout.id)}
            disabled={downloadLoading === selectedPayout.id}
          >
            {downloadLoading === selectedPayout.id ? 'Downloading...' : 'Download'}
          </Button>
          <Button variant="outlined" onClick={handleClosePayslipDialog}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    );
  };

  const renderPayslipsList = (): React.ReactElement => {
    if (payouts.length === 0) {
      return (
        <Alert severity="info">
          No payslips available for the selected period. Payslips are only available for processed, approved, or paid payouts.
        </Alert>
      );
    }

    return (
      <TableContainer component={Paper} variant="outlined">
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Pay Period</TableCell>
              <TableCell align="center">Status</TableCell>
              <TableCell align="right">Gross Amount</TableCell>
              <TableCell align="right">Net Amount</TableCell>
              <TableCell align="center">Payout Date</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {payouts.map((payout) => (
              <TableRow key={payout.id} hover>
                <TableCell>
                  <Box display="flex" alignItems="center">
                    <ReceiptIcon sx={{ mr: 1, color: 'text.secondary' }} />
                    <Box>
                      <Typography variant="body2" fontWeight="bold">
                        {payoutService.getMonthName(new Date(payout.pay_period_start).getMonth() + 1)} {new Date(payout.pay_period_start).getFullYear()}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {payoutService.formatDate(payout.pay_period_start)} - {payoutService.formatDate(payout.pay_period_end)}
                      </Typography>
                    </Box>
                  </Box>
                </TableCell>
                <TableCell align="center">
                  <Chip 
                    label={payoutService.getStatusLabel(payout.status)}
                    color={payoutService.getStatusColor(payout.status)}
                    size="small"
                  />
                </TableCell>
                <TableCell align="right" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                  {payoutService.formatCurrency(payout.gross_salary)}
                </TableCell>
                <TableCell align="right" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                  {payoutService.formatCurrency(payout.net_salary)}
                </TableCell>
                <TableCell align="center">
                  {payoutService.formatDate(payout.payout_date)}
                </TableCell>
                <TableCell align="center">
                  <Box display="flex" justifyContent="center" gap={1}>
                    <Tooltip title="View Payslip">
                      <IconButton 
                        size="small"
                        color="primary"
                        onClick={() => handleViewPayslip(payout)}
                      >
                        <VisibilityIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Download Payslip">
                      <IconButton 
                        size="small"
                        color="secondary"
                        onClick={() => handleDownloadPayslip(payout.id)}
                        disabled={downloadLoading === payout.id}
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
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  const handleYearChange = (event: SelectChangeEvent<number>): void => {
    setSelectedYear(event.target.value as number);
  };

  const handleMonthChange = (event: SelectChangeEvent<string>): void => {
    const value = event.target.value;
    setSelectedMonth(value === '' ? null : parseInt(value, 10));
  };

  return (
    <PageLayout title="My Payslips">
      <Typography variant="h4" gutterBottom>
        My Payslips
      </Typography>
      
      {/* Summary Cards */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3, mb: 3 }}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" mb={2}>
              <Avatar sx={{ bgcolor: theme.palette.primary.main, mr: 2 }}>
                <ReceiptIcon />
              </Avatar>
              <Typography variant="h6">Total Payslips</Typography>
            </Box>
            <Typography variant="h3" color="primary.main" fontWeight="bold">
              {payouts.length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Available payslips
            </Typography>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" mb={2}>
              <Avatar sx={{ bgcolor: theme.palette.success.main, mr: 2 }}>
                <MonetizationOnIcon />
              </Avatar>
              <Typography variant="h6">Total Earnings</Typography>
            </Box>
            <Typography variant="h3" color="success.main" fontWeight="bold">
              {payoutService.formatCurrency(payouts.reduce((total, payout) => total + payout.gross_salary, 0))}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Cumulative earnings
            </Typography>
          </CardContent>
        </Card>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(3, 1fr)' }, gap: 2, alignItems: 'center' }}>
            <FormControl fullWidth>
              <InputLabel>Year</InputLabel>
              <Select
                value={selectedYear}
                label="Year"
                onChange={handleYearChange}
              >
                {yearOptions.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl fullWidth>
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
              onClick={loadPayouts}
              disabled={loading}
              fullWidth
            >
              Refresh
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Payslips List */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Available Payslips
          </Typography>
          
          {loading ? (
            <Box display="flex" justifyContent="center" p={4}>
              <CircularProgress />
            </Box>
          ) : (
            renderPayslipsList()
          )}
        </CardContent>
      </Card>

      {/* Payslip Detail Dialog */}
      {renderPayslipDialog()}
    </PageLayout>
  );
};

export default MyPayslips; 