import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
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
  ListItemText
} from '@mui/material';
import {
  Download as DownloadIcon,
  Visibility as VisibilityIcon,
  Close as CloseIcon,
  Receipt as ReceiptIcon,
  Print as PrintIcon
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';
import payoutService from '../../services/payoutService';
import PageLayout from '../../layout/PageLayout';

const MyPayslips = () => {
  const theme = useTheme();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [payouts, setPayouts] = useState([]);
  const [selectedYear, setSelectedYear] = useState(payoutService.getCurrentFinancialYear());
  const [selectedMonth, setSelectedMonth] = useState(null);
  const [selectedPayout, setSelectedPayout] = useState(null);
  const [payslipData, setPayslipData] = useState(null);
  const [payslipDialogOpen, setPayslipDialogOpen] = useState(false);
  const [downloadLoading, setDownloadLoading] = useState(null);

  // Generate year options for the last 5 years
  const yearOptions = Array.from({ length: 5 }, (_, i) => {
    const year = payoutService.getCurrentFinancialYear() - i;
    return {
      value: year,
      label: payoutService.getFinancialYearLabel(year)
    };
  });

  // Month options
  const monthOptions = Array.from({ length: 12 }, (_, i) => ({
    value: i + 1,
    label: payoutService.getMonthName(i + 1)
  }));

  useEffect(() => {
    loadPayouts();
  }, [selectedYear, selectedMonth]);

  const loadPayouts = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const payoutsData = await payoutService.getMyPayouts(selectedYear, selectedMonth);
      // Filter only payouts that are processed/approved/paid (eligible for payslips)
      const eligiblePayouts = payoutsData.filter(payout => 
        ['processed', 'approved', 'paid'].includes(payout.status)
      );
      setPayouts(eligiblePayouts);
    } catch (err) {
      console.error('Error loading payouts:', err);
      setError('Failed to load payslips. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleViewPayslip = async (payout) => {
    try {
      setSelectedPayout(payout);
      setPayslipDialogOpen(true);
      
      // Load payslip data
      const data = await payoutService.getPayslipData(payout.id);
      setPayslipData(data);
      
    } catch (err) {
      console.error('Error loading payslip data:', err);
      setError('Failed to load payslip details. Please try again.');
      setPayslipDialogOpen(false);
    }
  };

  const handleDownloadPayslip = async (payoutId) => {
    try {
      setDownloadLoading(payoutId);
      await payoutService.downloadPayslip(payoutId);
    } catch (err) {
      console.error('Error downloading payslip:', err);
      setError('Failed to download payslip. Please try again.');
    } finally {
      setDownloadLoading(null);
    }
  };

  const handleClosePayslipDialog = () => {
    setPayslipDialogOpen(false);
    setSelectedPayout(null);
    setPayslipData(null);
  };

  const renderPayslipDialog = () => {
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
          <Grid container spacing={2} mb={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" color="text.secondary">Employee Details</Typography>
              <Typography><strong>Name:</strong> {payslipData.employee_name}</Typography>
              <Typography><strong>Employee Code:</strong> {payslipData.employee_code || 'N/A'}</Typography>
              <Typography><strong>Department:</strong> {payslipData.department || 'N/A'}</Typography>
              <Typography><strong>Designation:</strong> {payslipData.designation || 'N/A'}</Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" color="text.secondary">Pay Details</Typography>
              <Typography><strong>Pay Period:</strong> {payslipData.pay_period}</Typography>
              <Typography><strong>Pay Date:</strong> {payslipData.payout_date}</Typography>
              <Typography><strong>Days in Month:</strong> {payslipData.days_in_month}</Typography>
              <Typography><strong>Days Worked:</strong> {payslipData.days_worked}</Typography>
            </Grid>
          </Grid>

          <Divider sx={{ mb: 3 }} />

          {/* Earnings and Deductions */}
          <Grid container spacing={3}>
            {/* Earnings */}
            <Grid item xs={12} md={6}>
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
            </Grid>

            {/* Deductions */}
            <Grid item xs={12} md={6}>
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
            </Grid>
          </Grid>

          <Divider sx={{ my: 3 }} />

          {/* Net Pay */}
          <Box textAlign="center" p={2} bgcolor={theme.palette.primary.light} borderRadius={1}>
            <Typography variant="h5" color="primary.dark" fontWeight="bold">
              Net Pay: {payoutService.formatCurrency(payslipData.net_pay)}
            </Typography>
          </Box>

          {/* Additional Information */}
          <Grid container spacing={2} mt={2}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" color="text.secondary">Year to Date</Typography>
              <Typography><strong>YTD Gross:</strong> {payoutService.formatCurrency(payslipData.ytd_gross)}</Typography>
              <Typography><strong>YTD Tax Deducted:</strong> {payoutService.formatCurrency(payslipData.ytd_tax_deducted)}</Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" color="text.secondary">Tax Information</Typography>
              <Typography><strong>Tax Regime:</strong> {payslipData.tax_regime.toUpperCase()}</Typography>
              <Typography><strong>PAN:</strong> {payslipData.pan_number || 'N/A'}</Typography>
              <Typography><strong>UAN:</strong> {payslipData.uan_number || 'N/A'}</Typography>
            </Grid>
          </Grid>
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

  const renderPayslipsList = () => {
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

  return (
    <PageLayout title="My Payslips">
      <Typography variant="h4" gutterBottom>
        My Payslips
      </Typography>
      
      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
                <InputLabel>Financial Year</InputLabel>
                <Select
                  value={selectedYear}
                  label="Financial Year"
                  onChange={(e) => setSelectedYear(e.target.value)}
                >
                  {yearOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
                <InputLabel>Month (Optional)</InputLabel>
                <Select
                  value={selectedMonth || ''}
                  label="Month (Optional)"
                  onChange={(e) => setSelectedMonth(e.target.value || null)}
                >
                  <MenuItem value="">All Months</MenuItem>
                  {monthOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

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