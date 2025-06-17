import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  SelectChangeEvent
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import payoutService from '../../shared/services/payoutService';
import { usePayrollsQuery } from '../../shared/hooks/usePayrolls';

interface YearOption {
  value: number;
  label: string;
}

interface MonthOption {
  value: number;
  label: string;
}

interface SalaryBreakdownItem {
  label: string;
  amount: number;
}

const MySalaryDetails: React.FC = () => {
  const theme = useTheme();
  const [selectedYear, setSelectedYear] = useState<number>(payoutService.getCurrentFinancialYear());
  const [selectedMonth, setSelectedMonth] = useState<number | null>(null);

  const { data: payoutsData, isLoading } = usePayrollsQuery({
    year: selectedYear,
    month: selectedMonth
  });

  const payouts = payoutsData?.payouts || [];
  const latestPayout = payouts[0]; // Get the most recent payout

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

  const getSalaryBreakdown = (): SalaryBreakdownItem[] => {
    // Since the payout from usePayrollsQuery doesn't have detailed breakdown,
    // we'll show basic information available
    if (!latestPayout) return [];
    
    return [
      { label: 'Total Amount', amount: latestPayout.total_amount },
      { label: 'Employees', amount: latestPayout.total_employees }
    ];
  };

  const getDeductionsBreakdown = (): SalaryBreakdownItem[] => {
    // Basic deductions information
    return [
      { label: 'Processing Fee', amount: 0 }, // Placeholder
      { label: 'Other Charges', amount: 0 } // Placeholder
    ];
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

  if (!latestPayout) {
    return (
      <Box>
        <Alert severity="info" sx={{ m: 3 }}>
          No salary details found for the selected period.
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
        </Box>

        {/* Salary Breakdown */}
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3, mb: 3 }}>
          {/* Salary Breakdown */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Salary Breakdown
              </Typography>
              {getSalaryBreakdown().map((item) => (
                <Box key={item.label} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">{item.label}</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {typeof item.amount === 'number' ? payoutService.formatCurrency(item.amount) : item.amount}
                  </Typography>
                </Box>
              ))}
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
                <Typography variant="subtitle1">Total Amount</Typography>
                <Typography variant="subtitle1" fontWeight="bold">
                  {payoutService.formatCurrency(latestPayout.total_amount)}
                </Typography>
              </Box>
            </CardContent>
          </Card>

          {/* Deductions */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Deductions
              </Typography>
              {getDeductionsBreakdown().map((item) => (
                <Box key={item.label} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">{item.label}</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {payoutService.formatCurrency(item.amount)}
                  </Typography>
                </Box>
              ))}
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
                <Typography variant="subtitle1">Total Deductions</Typography>
                <Typography variant="subtitle1" fontWeight="bold">
                  {payoutService.formatCurrency(0)}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Box>

        {/* Net Salary */}
        <Card sx={{ bgcolor: theme.palette.primary.light }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="h6">Net Salary</Typography>
              <Typography variant="h4" fontWeight="bold" color="primary.dark">
                {payoutService.formatCurrency(latestPayout.total_amount)}
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Box>
  );
};

export default MySalaryDetails; 