import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
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
  Divider,
  Avatar,
  List,
  ListItem,
  ListItemText,
  SelectChangeEvent,
  Button
} from '@mui/material';
import {
  AccountBalance as AccountBalanceIcon,
  TrendingUp as TrendingUpIcon,
  Receipt as ReceiptIcon,
  MonetizationOn as MonetizationOnIcon,
  AccountBalanceWallet as WalletIcon,
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

interface PayoutHistory {
  annual_gross: number;
  annual_net: number;
  annual_tax_deducted: number;
}

interface YearOption {
  value: number;
  label: string;
}

interface MonthOption {
  value: number;
  label: string;
}

interface EarningItem {
  label: string;
  value: number;
}

const MySalaryDetails: React.FC = () => {
  const theme = useTheme();
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [payouts, setPayouts] = useState<Payout[]>([]);
  const [selectedYear, setSelectedYear] = useState<number>(payoutService.getCurrentFinancialYear());
  const [selectedMonth, setSelectedMonth] = useState<number | null>(null);
  const [payoutHistory, setPayoutHistory] = useState<PayoutHistory | null>(null);
  const [latestPayout, setLatestPayout] = useState<Payout | null>(null);

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

  const loadData = useCallback(async (): Promise<void> => {
    setLoading(true);
    setError(null);
    
    try {
      // Load payouts for selected year/month
      const payoutsData: Payout[] = await payoutService.getMyPayouts(
        selectedYear as any, 
        selectedMonth as any
      );
      setPayouts(payoutsData);

      // Get latest payout for current salary display
      if (payoutsData.length > 0) {
        const latest = payoutsData.reduce((prev, current) => 
          new Date(prev.payout_date) > new Date(current.payout_date) ? prev : current
        );
        setLatestPayout(latest);
      }

      // Load annual history if no specific month is selected
      if (!selectedMonth) {
        const historyData: PayoutHistory = await payoutService.getMyPayoutHistory(selectedYear as any);
        setPayoutHistory(historyData);
      }

    } catch (err) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error loading salary data:', err);
      }
      setError('Failed to load salary details. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [selectedYear, selectedMonth]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const renderSalaryBreakdown = (): React.ReactElement | null => {
    if (!latestPayout) return null;

    const earnings: EarningItem[] = [
      { label: 'Basic Salary', value: latestPayout.basic_salary },
      { label: 'Dearness Allowance', value: latestPayout.da },
      { label: 'House Rent Allowance', value: latestPayout.hra },
      { label: 'Special Allowance', value: latestPayout.special_allowance },
      { label: 'Bonus', value: latestPayout.bonus },
      { label: 'Transport Allowance', value: latestPayout.transport_allowance },
      { label: 'Medical Allowance', value: latestPayout.medical_allowance },
      { label: 'Other Allowances', value: latestPayout.other_allowances },
      { label: 'Reimbursements', value: latestPayout.reimbursements }
    ].filter(item => item.value > 0);

    const deductions: EarningItem[] = [
      { label: 'Employee PF', value: latestPayout.epf_employee },
      { label: 'Employee ESI', value: latestPayout.esi_employee },
      { label: 'Professional Tax', value: latestPayout.professional_tax },
      { label: 'Income Tax (TDS)', value: latestPayout.tds },
      { label: 'Advance Deduction', value: latestPayout.advance_deduction },
      { label: 'Loan Deduction', value: latestPayout.loan_deduction },
      { label: 'Other Deductions', value: latestPayout.other_deductions }
    ].filter(item => item.value > 0);

    return (
      <>
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
          {/* Earnings */}
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Avatar sx={{ bgcolor: theme.palette.success.main, mr: 2 }}>
                  <MonetizationOnIcon />
                </Avatar>
                <Typography variant="h6" color="success.main">
                  Earnings
                </Typography>
              </Box>
              <List dense>
                {earnings.map((item, index) => (
                  <ListItem key={index} sx={{ px: 0 }}>
                    <ListItemText 
                      primary={item.label}
                      secondary={payoutService.formatCurrency(item.value)}
                      secondaryTypographyProps={{
                        variant: 'h6',
                        color: 'success.main',
                        fontWeight: 'bold'
                      }}
                    />
                  </ListItem>
                ))}
                <Divider sx={{ my: 1 }} />
                <ListItem sx={{ px: 0, bgcolor: theme.palette.success.light, borderRadius: 1 }}>
                  <ListItemText 
                    primary="Total Earnings"
                    secondary={payoutService.formatCurrency(latestPayout.gross_salary)}
                    primaryTypographyProps={{ fontWeight: 'bold' }}
                    secondaryTypographyProps={{
                      variant: 'h5',
                      color: 'success.dark',
                      fontWeight: 'bold'
                    }}
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>

          {/* Deductions */}
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Avatar sx={{ bgcolor: theme.palette.error.main, mr: 2 }}>
                  <ReceiptIcon />
                </Avatar>
                <Typography variant="h6" color="error.main">
                  Deductions
                </Typography>
              </Box>
              <List dense>
                {deductions.map((item, index) => (
                  <ListItem key={index} sx={{ px: 0 }}>
                    <ListItemText 
                      primary={item.label}
                      secondary={payoutService.formatCurrency(item.value)}
                      secondaryTypographyProps={{
                        variant: 'h6',
                        color: 'error.main',
                        fontWeight: 'bold'
                      }}
                    />
                  </ListItem>
                ))}
                <Divider sx={{ my: 1 }} />
                <ListItem sx={{ px: 0, bgcolor: theme.palette.error.light, borderRadius: 1 }}>
                  <ListItemText 
                    primary="Total Deductions"
                    secondary={payoutService.formatCurrency(latestPayout.total_deductions)}
                    primaryTypographyProps={{ fontWeight: 'bold' }}
                    secondaryTypographyProps={{
                      variant: 'h5',
                      color: 'error.dark',
                      fontWeight: 'bold'
                    }}
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Box>

        {/* Net Salary */}
        <Box sx={{ mt: 3 }}>
          <Card sx={{ bgcolor: theme.palette.primary.light }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box display="flex" alignItems="center">
                  <Avatar sx={{ bgcolor: theme.palette.primary.main, mr: 2, width: 56, height: 56 }}>
                    <WalletIcon sx={{ fontSize: 32 }} />
                  </Avatar>
                  <Box>
                    <Typography variant="h4" color="primary.dark" fontWeight="bold">
                      {payoutService.formatCurrency(latestPayout.net_salary)}
                    </Typography>
                    <Typography variant="subtitle1" color="primary.dark">
                      Net Monthly Salary
                    </Typography>
                  </Box>
                </Box>
                <Box textAlign="right">
                  <Typography variant="body2" color="primary.dark">
                    Pay Period: {payoutService.formatDate(latestPayout.pay_period_start)} - {payoutService.formatDate(latestPayout.pay_period_end)}
                  </Typography>
                  <Chip 
                    label={payoutService.getStatusLabel(latestPayout.status)}
                    color={payoutService.getStatusColor(latestPayout.status)}
                    size="small"
                    sx={{ mt: 1 }}
                  />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Box>
      </>
    );
  };

  const renderAnnualSummary = (): React.ReactElement | null => {
    if (!payoutHistory) return null;

    return (
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(3, 1fr)' }, gap: 3, mb: 3 }}>
        <Card>
          <CardContent>
            <Box textAlign="center" p={2}>
              <Avatar sx={{ bgcolor: theme.palette.info.main, mx: 'auto', mb: 1 }}>
                <TrendingUpIcon />
              </Avatar>
              <Typography variant="h5" color="info.main" fontWeight="bold">
                {payoutService.formatCurrency(payoutHistory.annual_gross)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Annual Gross
              </Typography>
            </Box>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Box textAlign="center" p={2}>
              <Avatar sx={{ bgcolor: theme.palette.success.main, mx: 'auto', mb: 1 }}>
                <AccountBalanceIcon />
              </Avatar>
              <Typography variant="h5" color="success.main" fontWeight="bold">
                {payoutService.formatCurrency(payoutHistory.annual_net)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Annual Net
              </Typography>
            </Box>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Box textAlign="center" p={2}>
              <Avatar sx={{ bgcolor: theme.palette.warning.main, mx: 'auto', mb: 1 }}>
                <ReceiptIcon />
              </Avatar>
              <Typography variant="h5" color="warning.main" fontWeight="bold">
                {payoutService.formatCurrency(payoutHistory.annual_tax_deducted)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Tax Deducted
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Box>
    );
  };

  const renderPayoutHistory = (): React.ReactElement => {
    if (payouts.length === 0) {
      return (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Payout History
            </Typography>
            <Alert severity="info">
              No payouts found for the selected period.
            </Alert>
          </CardContent>
        </Card>
      );
    }

    return (
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Payout History
          </Typography>
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Pay Period</TableCell>
                  <TableCell align="right">Gross Amount</TableCell>
                  <TableCell align="right">Deductions</TableCell>
                  <TableCell align="right">Net Amount</TableCell>
                  <TableCell align="center">Status</TableCell>
                  <TableCell align="center">Payout Date</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {payouts.map((payout) => (
                  <TableRow key={payout.id} hover>
                    <TableCell>
                      {payoutService.formatDate(payout.pay_period_start)} - {payoutService.formatDate(payout.pay_period_end)}
                    </TableCell>
                    <TableCell align="right" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                      {payoutService.formatCurrency(payout.gross_salary)}
                    </TableCell>
                    <TableCell align="right" sx={{ fontWeight: 'bold', color: 'error.main' }}>
                      {payoutService.formatCurrency(payout.total_deductions)}
                    </TableCell>
                    <TableCell align="right" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                      {payoutService.formatCurrency(payout.net_salary)}
                    </TableCell>
                    <TableCell align="center">
                      <Chip 
                        label={payoutService.getStatusLabel(payout.status)}
                        color={payoutService.getStatusColor(payout.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="center">
                      {payoutService.formatDate(payout.payout_date)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
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
    <PageLayout title="My Salary Details">
      <Typography variant="h4" gutterBottom>
        My Salary Details
      </Typography>
      
      {/* Filters */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(3, 1fr)' }, gap: 2, mb: 3 }}>
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
          onClick={loadData}
          disabled={loading}
          fullWidth
        >
          Refresh
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {loading ? (
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          {/* Current Salary Breakdown */}
          {latestPayout && (
            <>
              <Typography variant="h5" gutterBottom>
                Current Salary Breakdown
              </Typography>
              {renderSalaryBreakdown()}
            </>
          )}

          {/* Annual Summary */}
          {!selectedMonth && renderAnnualSummary()}

          {/* Payout History Table */}
          {renderPayoutHistory()}
        </>
      )}
    </PageLayout>
  );
};

export default MySalaryDetails; 