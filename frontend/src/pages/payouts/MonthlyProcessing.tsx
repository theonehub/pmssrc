import React, { useState } from 'react';
import { 
  Box, 
  CircularProgress, 
  Typography, 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem, 
  Button, 
  Alert,
  Avatar, 
  Card, 
  CardContent, 
  Chip, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  SelectChangeEvent
} from '@mui/material';
import { 
  People as PeopleIcon, 
  MonetizationOn as MonetizationOnIcon, 
  Receipt as ReceiptIcon,
  PlayArrow as PlayArrowIcon
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';
import { usePayrollsQuery } from '../../shared/hooks/usePayrolls';
import payoutService from '../../shared/services/payoutService';
import PageLayout from '../../layout/PageLayout';

// Type definitions
interface YearOption {
  value: number;
  label: string;
}

interface MonthOption {
  value: number;
  label: string;
}

/**
 * MonthlyProcessing Component - Process monthly payouts
 */
const MonthlyProcessing: React.FC = () => {
  const theme = useTheme();
  const [selectedYear, setSelectedYear] = useState<number>(payoutService.getCurrentFinancialYear());
  const [selectedMonth, setSelectedMonth] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [processing, setProcessing] = useState<boolean>(false);

  const { data: payoutsData, isLoading, refetch } = usePayrollsQuery({
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

  const handleYearChange = (event: SelectChangeEvent<string>): void => {
    setSelectedYear(Number(event.target.value));
  };

  const handleMonthChange = (event: SelectChangeEvent<string>): void => {
    setSelectedMonth(event.target.value ? parseInt(event.target.value) : null);
  };

  const handleProcessPayouts = async (): Promise<void> => {
    if (!selectedMonth) {
      setError('Please select a month to process payouts');
      return;
    }

    setProcessing(true);
    setError(null);

    try {
      await payoutService.processMonthlyPayouts(selectedYear, selectedMonth);
      if (refetch) {
        await refetch();
      }
    } catch (err) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error processing payouts:', err);
      }
      setError('Failed to process payouts. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  if (isLoading) {
    return (
      <PageLayout title="Monthly Processing">
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      </PageLayout>
    );
  }

  return (
    <PageLayout title="Monthly Processing">
      <Box sx={{ p: 3 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

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
            variant="contained"
            startIcon={processing ? <CircularProgress size={20} /> : <PlayArrowIcon />}
            onClick={handleProcessPayouts}
            disabled={processing || !selectedMonth}
          >
            {processing ? 'Processing...' : 'Process Payouts'}
          </Button>
        </Box>

        {/* Summary Cards */}
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(3, 1fr)' }, gap: 3, mb: 3 }}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Avatar sx={{ bgcolor: theme.palette.primary.main, mr: 2 }}>
                  <PeopleIcon />
                </Avatar>
                <Typography variant="h6">Total Employees</Typography>
              </Box>
              <Typography variant="h3" color="primary.main" fontWeight="bold">
                {payouts.reduce((total, payout) => total + payout.total_employees, 0)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                For selected period
              </Typography>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Avatar sx={{ bgcolor: theme.palette.success.main, mr: 2 }}>
                  <MonetizationOnIcon />
                </Avatar>
                <Typography variant="h6">Total Amount</Typography>
              </Box>
              <Typography variant="h3" color="success.main" fontWeight="bold">
                {payoutService.formatCurrency(payouts.reduce((total, payout) => total + payout.total_amount, 0))}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Gross payout amount
              </Typography>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Avatar sx={{ bgcolor: theme.palette.info.main, mr: 2 }}>
                  <ReceiptIcon />
                </Avatar>
                <Typography variant="h6">Status</Typography>
              </Box>
              <Typography variant="h3" color="info.main" fontWeight="bold">
                {payouts && payouts.length > 0 ? payouts[0]?.status || 'Pending' : 'Pending'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Current processing status
              </Typography>
            </CardContent>
          </Card>
        </Box>

        {/* Payouts Table */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Processed Payouts
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Period</TableCell>
                    <TableCell>Total Employees</TableCell>
                    <TableCell>Total Amount</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Date</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {payouts.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} align="center">
                        No payouts found for the selected period
                      </TableCell>
                    </TableRow>
                  ) : (
                    payouts.map((payout) => (
                      <TableRow key={payout.id}>
                        <TableCell>
                          {payoutService.formatDateRange(payout.pay_period_start, payout.pay_period_end)}
                        </TableCell>
                        <TableCell>{payout.total_employees}</TableCell>
                        <TableCell>{payoutService.formatCurrency(payout.total_amount)}</TableCell>
                        <TableCell>
                          <Chip
                            label={payout.status}
                            color={payout.status === 'paid' ? 'success' : 'default'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{payoutService.formatDate(payout.payout_date)}</TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </Box>
    </PageLayout>
  );
};

export default MonthlyProcessing; 