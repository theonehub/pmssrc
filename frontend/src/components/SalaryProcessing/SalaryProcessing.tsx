import React, { useState, useEffect, useCallback } from 'react';
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
  Tooltip,
  Menu,
  ListItemIcon,
  ListItemText,
  TextField,
  Divider
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Calculate as CalculateIcon,
  Visibility as VisibilityIcon,
  MoreVert as MoreVertIcon,
  CheckCircle as ApproveIcon,
  Cancel as RejectIcon,
  Payment as PaymentIcon,
  Replay as RecomputeIcon
} from '@mui/icons-material';
import { 
  salaryProcessingApi,
  MonthlySalaryResponse as MonthlySalary,
  MonthlySalarySummaryResponse as SalarySummary,
  MonthlySalaryBulkComputeResponse as BulkComputeResult
} from '../../shared/api/salaryProcessingApi';

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

  // Status transition states
  const [statusChangeDialogOpen, setStatusChangeDialogOpen] = useState(false);
  const [statusChangeTarget, setStatusChangeTarget] = useState<{
    salary: MonthlySalary;
    newStatus: string;
    actionLabel: string;
  } | null>(null);
  const [statusChangeNotes, setStatusChangeNotes] = useState('');
  const [statusChanging, setStatusChanging] = useState(false);
  const [actionMenuAnchor, setActionMenuAnchor] = useState<null | HTMLElement>(null);
  const [actionMenuSalary, setActionMenuSalary] = useState<MonthlySalary | null>(null);

  // Payment states
  const [paymentDialogOpen, setPaymentDialogOpen] = useState(false);
  const [paymentTarget, setPaymentTarget] = useState<{
    salary: MonthlySalary;
    paymentType: 'salary' | 'tds' | 'both';
    actionLabel: string;
  } | null>(null);
  const [paymentReference, setPaymentReference] = useState('');
  const [paymentNotes, setPaymentNotes] = useState('');
  const [processingPayment, setProcessingPayment] = useState(false);

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
    salary_paid: { color: 'warning', label: 'Salary Paid' },
    tds_paid: { color: 'warning', label: 'TDS Paid' },
    paid: { color: 'success', label: 'Fully Paid' },
    rejected: { color: 'error', label: 'Rejected' }
  };

  // Status transition configuration
  const getAvailableActions = (status: string) => {
    switch (status) {
      case 'not_computed':
        return [
          { action: 'compute', label: 'Compute Salary', icon: <CalculateIcon />, targetStatus: 'computed' }
        ];
      case 'computed':
        return [
          { action: 'approve', label: 'Approve', icon: <ApproveIcon />, targetStatus: 'approved' },
          { action: 'reject', label: 'Reject', icon: <RejectIcon />, targetStatus: 'rejected' },
          { action: 'recompute', label: 'Recompute', icon: <RecomputeIcon />, targetStatus: 'computed' }
        ];
      case 'approved':
        return [
          { action: 'pay_salary', label: 'Pay Salary', icon: <PaymentIcon />, paymentType: 'salary' },
          { action: 'pay_tds', label: 'Pay TDS', icon: <PaymentIcon />, paymentType: 'tds' },
          { action: 'pay_both', label: 'Pay Both', icon: <PaymentIcon />, paymentType: 'both' },
          { action: 'reject', label: 'Reject', icon: <RejectIcon />, targetStatus: 'rejected' }
        ];
      case 'salary_paid':
        return [
          { action: 'pay_tds', label: 'Pay TDS', icon: <PaymentIcon />, paymentType: 'tds' },
          { action: 'reject', label: 'Reject', icon: <RejectIcon />, targetStatus: 'rejected' }
        ];
      case 'tds_paid':
        return [
          { action: 'pay_salary', label: 'Pay Salary', icon: <PaymentIcon />, paymentType: 'salary' },
          { action: 'reject', label: 'Reject', icon: <RejectIcon />, targetStatus: 'rejected' }
        ];
      case 'rejected':
        return [
          { action: 'recompute', label: 'Recompute', icon: <RecomputeIcon />, targetStatus: 'computed' }
        ];
      case 'paid':
        return []; // No actions available for fully paid status
      default:
        return [];
    }
  };

  // Fetch data
  const fetchSalaries = useCallback(async () => {
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
  }, [selectedMonth, selectedYear]);

  const fetchSummary = useCallback(async () => {
    try {
      const summaryData = await salaryProcessingApi.getMonthlySalarySummary(
        selectedMonth,
        selectedYear
      );
      setSummary(summaryData);
    } catch (err: any) {
      console.error('Failed to fetch summary:', err);
    }
  }, [selectedMonth, selectedYear]);

  // Effects
  useEffect(() => {
    fetchSalaries();
    fetchSummary();
  }, [fetchSalaries, fetchSummary]);

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

  // Status transition handlers
  const handleActionMenuOpen = (event: React.MouseEvent<HTMLElement>, salary: MonthlySalary) => {
    setActionMenuAnchor(event.currentTarget);
    setActionMenuSalary(salary);
  };

  const handleActionMenuClose = () => {
    setActionMenuAnchor(null);
    setActionMenuSalary(null);
  };

  const handleStatusChangeClick = (salary: MonthlySalary, action: any) => {
    if (action.action === 'compute' || action.action === 'recompute') {
      // Handle direct computation
      handleIndividualCompute(salary);
    } else if (action.action.startsWith('pay_')) {
      // Handle payment actions
      handlePaymentAction(salary, action);
    } else {
      // Handle status change with confirmation
      setStatusChangeTarget({
        salary,
        newStatus: action.targetStatus,
        actionLabel: action.label
      });
      setStatusChangeNotes('');
      setStatusChangeDialogOpen(true);
    }
    handleActionMenuClose();
  };

  const handleIndividualCompute = async (salary: MonthlySalary) => {
    setStatusChanging(true);
    setError(null);
    
    try {
      await salaryProcessingApi.computeMonthlySalary({
        employee_id: salary.employee_id,
        month: salary.month,
        year: salary.year,
        tax_year: salary.tax_year,
        force_recompute: true
      });
      
      setSuccess(`Salary computed successfully for ${salary.employee_name}`);
      
      // Refresh data
      await fetchSalaries();
      await fetchSummary();
      
    } catch (err: any) {
      setError(err.message || 'Failed to compute salary');
    } finally {
      setStatusChanging(false);
    }
  };

  const handleStatusChangeConfirm = async () => {
    if (!statusChangeTarget) return;
    
    setStatusChanging(true);
    setError(null);
    
    try {
      const updateRequest: any = {
        employee_id: statusChangeTarget.salary.employee_id,
        month: statusChangeTarget.salary.month,
        year: statusChangeTarget.salary.year,
        status: statusChangeTarget.newStatus
      };
      
      if (statusChangeNotes) {
        updateRequest.notes = statusChangeNotes;
      }
      
      await salaryProcessingApi.updateMonthlySalaryStatus(updateRequest);
      
      setSuccess(`${statusChangeTarget.actionLabel} successful for ${statusChangeTarget.salary.employee_name}`);
      
      // Refresh data
      await fetchSalaries();
      await fetchSummary();
      
      // Close dialog
      setStatusChangeDialogOpen(false);
      setStatusChangeTarget(null);
      setStatusChangeNotes('');
      
    } catch (err: any) {
      setError(err.message || `Failed to ${statusChangeTarget.actionLabel.toLowerCase()}`);
    } finally {
      setStatusChanging(false);
    }
  };

  const handleStatusChangeCancel = () => {
    setStatusChangeDialogOpen(false);
    setStatusChangeTarget(null);
    setStatusChangeNotes('');
  };

  const handlePaymentAction = (salary: MonthlySalary, action: any) => {
    setPaymentTarget({
      salary,
      paymentType: action.paymentType,
      actionLabel: action.label
    });
    setPaymentReference('');
    setPaymentNotes('');
    setPaymentDialogOpen(true);
  };

  const handlePaymentConfirm = async () => {
    if (!paymentTarget) return;

    setProcessingPayment(true);
    setError(null);

    try {
      const paymentRequest: any = {
        employee_id: paymentTarget.salary.employee_id,
        month: paymentTarget.salary.month,
        year: paymentTarget.salary.year,
        payment_type: paymentTarget.paymentType
      };
      
      if (paymentReference) {
        paymentRequest.payment_reference = paymentReference;
      }
      
      if (paymentNotes) {
        paymentRequest.payment_notes = paymentNotes;
      }
      
      await salaryProcessingApi.markSalaryPayment(paymentRequest);

      setSuccess(`Successfully marked ${paymentTarget.actionLabel.toLowerCase()} for ${paymentTarget.salary.employee_name}`);
      setPaymentDialogOpen(false);
      setPaymentTarget(null);
      setPaymentReference('');
      setPaymentNotes('');
      
      // Refresh data
      await fetchSalaries();
      await fetchSummary();
    } catch (err: any) {
      setError(err.message || `Failed to ${paymentTarget.actionLabel.toLowerCase()}`);
    } finally {
      setProcessingPayment(false);
    }
  };

  const handlePaymentCancel = () => {
    setPaymentDialogOpen(false);
    setPaymentTarget(null);
    setPaymentReference('');
    setPaymentNotes('');
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

      {/* Salary Lifecycle Workflow */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Salary Processing Workflow
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap', mt: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip label="Not Computed" color="default" size="small" variant="outlined" />
              <Typography variant="body2">→</Typography>
            </Box>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip label="Computed" color="info" size="small" variant="outlined" />
              <Typography variant="body2">→</Typography>
            </Box>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip label="Approved" color="success" size="small" variant="outlined" />
              <Typography variant="body2">→</Typography>
            </Box>
            
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 0.5 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Chip label="Salary Paid" color="warning" size="small" variant="outlined" />
                <Typography variant="caption">or</Typography>
                <Chip label="TDS Paid" color="warning" size="small" variant="outlined" />
              </Box>
              <Typography variant="body2">↓</Typography>
              <Chip label="Fully Paid" color="success" size="small" variant="outlined" />
            </Box>
            
            <Box sx={{ ml: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="body2" color="text.secondary">or</Typography>
              <Chip label="Rejected" color="error" size="small" variant="outlined" />
            </Box>
          </Box>
          
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            Use the actions menu (⋮) next to each salary record to move it through the workflow stages.
            Rejected salaries can be recomputed and re-entered into the workflow.
          </Typography>
        </CardContent>
      </Card>

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
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
                          <Tooltip title="View Details">
                            <IconButton
                              size="small"
                              onClick={() => handleViewSalaryDetails(salary)}
                            >
                              <VisibilityIcon />
                            </IconButton>
                          </Tooltip>
                          
                          {getAvailableActions(salary.status).length > 0 && (
                            <Tooltip title="Actions">
                              <IconButton
                                size="small"
                                onClick={(e) => handleActionMenuOpen(e, salary)}
                                disabled={statusChanging}
                              >
                                <MoreVertIcon />
                              </IconButton>
                            </Tooltip>
                          )}
                        </Box>
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

      {/* Action Menu */}
      <Menu
        anchorEl={actionMenuAnchor}
        open={Boolean(actionMenuAnchor)}
        onClose={handleActionMenuClose}
        PaperProps={{
          elevation: 3,
          sx: { minWidth: 180 }
        }}
      >
        {actionMenuSalary && getAvailableActions(actionMenuSalary.status).map((action) => (
          <MenuItem
            key={action.action}
            onClick={() => handleStatusChangeClick(actionMenuSalary, action)}
            disabled={statusChanging}
          >
            <ListItemIcon>
              {action.icon}
            </ListItemIcon>
            <ListItemText>
              {action.label}
            </ListItemText>
          </MenuItem>
        ))}
      </Menu>

      {/* Status Change Confirmation Dialog */}
      <Dialog
        open={statusChangeDialogOpen}
        onClose={handleStatusChangeCancel}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Confirm {statusChangeTarget?.actionLabel}
        </DialogTitle>
        <DialogContent>
          {statusChangeTarget && (
            <Box>
              <Typography gutterBottom>
                Are you sure you want to {statusChangeTarget.actionLabel.toLowerCase()} the salary for{' '}
                <strong>{statusChangeTarget.salary.employee_name}</strong>?
              </Typography>
              
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Period: {monthOptions.find(m => m.value === statusChangeTarget.salary.month)?.label} {statusChangeTarget.salary.year}
              </Typography>
              
              <Divider sx={{ my: 2 }} />
              
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Notes (Optional)"
                value={statusChangeNotes}
                onChange={(e) => setStatusChangeNotes(e.target.value)}
                placeholder="Add any notes or comments..."
                variant="outlined"
                sx={{ mt: 2 }}
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={handleStatusChangeCancel}
            disabled={statusChanging}
            color="inherit"
          >
            Cancel
          </Button>
          <Button 
            onClick={handleStatusChangeConfirm}
            disabled={statusChanging}
            variant="contained"
            startIcon={statusChanging ? <CircularProgress size={16} /> : null}
          >
            {statusChanging ? 'Processing...' : `Confirm ${statusChangeTarget?.actionLabel}`}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Payment Confirmation Dialog */}
      <Dialog
        open={paymentDialogOpen}
        onClose={handlePaymentCancel}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Confirm {paymentTarget?.actionLabel}
        </DialogTitle>
        <DialogContent>
          {paymentTarget && (
            <Box>
              <Typography gutterBottom>
                Are you sure you want to mark {paymentTarget.paymentType === 'both' ? 'both salary and TDS' : paymentTarget.paymentType.toUpperCase()} as paid for{' '}
                <strong>{paymentTarget.salary.employee_name}</strong>?
              </Typography>
              
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Period: {monthOptions.find(m => m.value === paymentTarget.salary.month)?.label} {paymentTarget.salary.year}
              </Typography>
              
              <Divider sx={{ my: 2 }} />
              
              <TextField
                fullWidth
                label="Payment Reference (Optional)"
                value={paymentReference}
                onChange={(e) => setPaymentReference(e.target.value)}
                placeholder="Transaction ID, Check number, etc."
                variant="outlined"
                sx={{ mb: 2 }}
              />
              
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Payment Notes (Optional)"
                value={paymentNotes}
                onChange={(e) => setPaymentNotes(e.target.value)}
                placeholder="Add any payment-related notes..."
                variant="outlined"
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
                     <Button 
             onClick={handlePaymentCancel}
             disabled={processingPayment}
             color="inherit"
            >
              Cancel
            </Button>
            <Button 
              onClick={handlePaymentConfirm}
              disabled={processingPayment}
              variant="contained"
              startIcon={processingPayment ? <CircularProgress size={16} /> : null}
            >
              {processingPayment ? 'Processing...' : `Confirm ${paymentTarget?.actionLabel}`}
          </Button>
        </DialogActions>
      </Dialog>

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