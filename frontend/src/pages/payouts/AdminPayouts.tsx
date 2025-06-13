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
  Receipt as ReceiptIcon,
  Visibility as VisibilityIcon
} from '@mui/icons-material';
import payoutService from '../../shared/services/payoutService';
import PageLayout from '../../layout/PageLayout';
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

interface Payout {
  id: string;
  pay_period_start: string;
  pay_period_end: string;
  total_employees: number;
  total_amount: number;
  status: string;
  payout_date: string;
  employees?: Array<{
    id: string;
    name: string;
    department: string;
    gross_salary: number;
    total_deductions: number;
    net_salary: number;
  }>;
}

const AdminPayouts: React.FC = () => {
  const [error] = useState<string | null>(null);
  const [selectedMonth, setSelectedMonth] = useState<number | null>(null);
  const [selectedYear, setSelectedYear] = useState<number>(payoutService.getCurrentFinancialYear());
  const [selectedPayout, setSelectedPayout] = useState<Payout | null>(null);
  const [payoutDialogOpen, setPayoutDialogOpen] = useState<boolean>(false);

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

  const handleMonthChange = (event: SelectChangeEvent<string>): void => {
    setSelectedMonth(event.target.value ? parseInt(event.target.value) : null);
  };

  const handleYearChange = (event: SelectChangeEvent<string>): void => {
    setSelectedYear(Number(event.target.value));
  };

  const handleViewPayout = (payout: Payout): void => {
    setSelectedPayout(payout);
    setPayoutDialogOpen(true);
  };

  const handleClosePayoutDialog = (): void => {
    setPayoutDialogOpen(false);
    setSelectedPayout(null);
  };

  if (isLoading) {
    return (
      <PageLayout title="Admin Payouts">
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      </PageLayout>
    );
  }

  if (error) {
    return (
      <PageLayout title="Admin Payouts">
        <Alert severity="error" sx={{ m: 3 }}>
          {error}
        </Alert>
      </PageLayout>
    );
  }

  return (
    <PageLayout title="Admin Payouts">
      <Box sx={{ p: 3 }}>
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

        <Card>
          <CardContent>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Period</TableCell>
                    <TableCell>Total Employees</TableCell>
                    <TableCell>Total Amount</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
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
              <ReceiptIcon color="primary" />
              <Typography variant="h6">
                Payout Details for {selectedPayout && payoutService.formatDateRange(
                  selectedPayout.pay_period_start,
                  selectedPayout.pay_period_end
                )}
              </Typography>
            </Box>
          </DialogTitle>
          <DialogContent>
            {selectedPayout && (
              <Box sx={{ p: 2 }}>
                {/* Summary */}
                <Box sx={{ mb: 4 }}>
                  <Typography variant="h6" gutterBottom>
                    Summary
                  </Typography>
                  <Box display="flex" gap={2}>
                    <Box>
                      <Typography variant="body2">
                        <strong>Total Employees:</strong> {selectedPayout.total_employees}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Total Amount:</strong> {payoutService.formatCurrency(selectedPayout.total_amount)}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="body2">
                        <strong>Status:</strong> {selectedPayout.status}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Payout Date:</strong> {payoutService.formatDate(selectedPayout.payout_date)}
                      </Typography>
                    </Box>
                  </Box>
                </Box>

                {/* Employee Details */}
                {selectedPayout.employees && selectedPayout.employees.length > 0 && (
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      Employee Details
                    </Typography>
                    <TableContainer>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell>Employee</TableCell>
                            <TableCell>Department</TableCell>
                            <TableCell>Gross Salary</TableCell>
                            <TableCell>Deductions</TableCell>
                            <TableCell>Net Salary</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {selectedPayout.employees.map((employee) => (
                            <TableRow key={employee.id}>
                              <TableCell>{employee.name}</TableCell>
                              <TableCell>{employee.department}</TableCell>
                              <TableCell>{payoutService.formatCurrency(employee.gross_salary)}</TableCell>
                              <TableCell>{payoutService.formatCurrency(employee.total_deductions)}</TableCell>
                              <TableCell>{payoutService.formatCurrency(employee.net_salary)}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Box>
                )}
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClosePayoutDialog}>Close</Button>
          </DialogActions>
        </Dialog>
      </Box>
    </PageLayout>
  );
};

export default AdminPayouts; 