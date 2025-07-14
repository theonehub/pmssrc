import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  TextField,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Tooltip,
  IconButton,
  Chip,
  TablePagination,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  Divider,
  Menu,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import { salaryProcessingApi, MonthlySalaryResponse } from '../../shared/api/salaryProcessingApi';
import { exportApi } from '../../shared/api/exportApi';
import {
  Search as SearchIcon,
  Refresh as RefreshIcon,
  Visibility as VisibilityIcon,
  AttachMoney as AttachMoneyIcon,
  Receipt as ReceiptIcon,
  Delete as DeleteIcon,
  TrendingUp as TrendingUpIcon,
  People as PeopleIcon,
  FileDownload as FileDownloadIcon,
  TableChart as TableChartIcon,
  GridOn as GridOnIcon
} from '@mui/icons-material';
import { getCurrentTaxYear, getAvailableTaxYears, taxYearStringToStartYear } from '../../shared/utils/formatting';

/**
 * ProcessedSalaries Component - Display all processed salary records
 */
const ProcessedSalaries: React.FC = () => {
  const [salaries, setSalaries] = useState<MonthlySalaryResponse[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  const [month, setMonth] = useState<number>(new Date().getMonth() + 1);
  const [taxYear, setTaxYear] = useState<string>(getCurrentTaxYear());
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [departmentFilter, setDepartmentFilter] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState<string>('');
  
  const [page, setPage] = useState<number>(0);
  const [rowsPerPage, setRowsPerPage] = useState<number>(10);
  const [totalCount, setTotalCount] = useState<number>(0);
  
  const [selectedSalary, setSelectedSalary] = useState<MonthlySalaryResponse | null>(null);
  const [detailDialogOpen, setDetailDialogOpen] = useState<boolean>(false);
  
  const [summary, setSummary] = useState<any>(null);
  const [summaryLoading, setSummaryLoading] = useState<boolean>(true);

  // Export functionality states
  const [exportAnchorEl, setExportAnchorEl] = useState<null | HTMLElement>(null);
  const [exportLoading, setExportLoading] = useState<boolean>(false);

  const [statusDialogOpen, setStatusDialogOpen] = useState(false);
  const [statusDialogSalary, setStatusDialogSalary] = useState<MonthlySalaryResponse | null>(null);
  const [nextStatus, setNextStatus] = useState<string>('');
  const [statusComments, setStatusComments] = useState('');
  const [transactionId, setTransactionId] = useState('');
  const [transferDate, setTransferDate] = useState<string>('');
  const [statusUpdateLoading, setStatusUpdateLoading] = useState(false);
  const [statusUpdateError, setStatusUpdateError] = useState<string | null>(null);

  // Placeholder for role check (replace with real auth logic)
  const isAdminUser = true; // TODO: Replace with actual role check

  // Status transition logic
  const getNextStatusOptions = (current: string) => {
    switch (current.toLowerCase()) {
      case 'computed':
        return [
          { value: 'approved', label: 'Approved' },
          { value: 'rejected', label: 'Rejected' }
        ];
      case 'approved':
        return [
          { value: 'transfer_initiated', label: 'Transfer Initiated' }
        ];
      case 'transfer_initiated':
        return [
          { value: 'transferred', label: 'Transferred' }
        ];
      default:
        return [];
    }
  };

  const handleStatusChipClick = (salary: MonthlySalaryResponse) => {
    if (!isAdminUser) return;
    setStatusDialogSalary(salary);
    setNextStatus('');
    setStatusComments('');
    setTransactionId('');
    setTransferDate('');
    setStatusUpdateError(null);
    setStatusDialogOpen(true);
  };

  const handleStatusDialogClose = () => {
    setStatusDialogOpen(false);
    setStatusDialogSalary(null);
    setNextStatus('');
    setStatusComments('');
    setTransactionId('');
    setTransferDate('');
    setStatusUpdateError(null);
  };

  const handleStatusUpdate = async () => {
    if (!statusDialogSalary || !nextStatus) return;
    if (!statusComments.trim()) {
      setStatusUpdateError('Comments are required.');
      return;
    }
    if (nextStatus === 'transferred') {
      if (!transactionId.trim()) {
        setStatusUpdateError('Transaction ID is required for Transferred status.');
        return;
      }
      if (!transferDate) {
        setStatusUpdateError('Transfer date is required for Transferred status.');
        return;
      }
    }
    setStatusUpdateLoading(true);
    setStatusUpdateError(null);
    try {
      await salaryProcessingApi.updateMonthlySalaryStatus({
        employee_id: statusDialogSalary.employee_id,
        month: statusDialogSalary.month,
        year: statusDialogSalary.year,
        tax_year: taxYear, // Add this line to include tax_year in the payload
        status: nextStatus,
        comments: statusComments,
        transaction_id: nextStatus === 'transferred' ? transactionId : undefined,
        transfer_date: nextStatus === 'transferred' && transferDate ? transferDate : undefined
      });
      setStatusDialogOpen(false);
      fetchSalaries();
      fetchSummary();
    } catch (err: any) {
      setStatusUpdateError('Failed to update status. Please try again.');
    } finally {
      setStatusUpdateLoading(false);
    }
  };

  const fetchSalaries = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params: any = {
        skip: page * rowsPerPage,
        limit: rowsPerPage
      };
      
      if (statusFilter) params.status = statusFilter;
      if (departmentFilter) params.department = departmentFilter;
      
      const response = await salaryProcessingApi.getMonthlySalariesForPeriod(
        month,
        taxYear,
        params
      );
      
      setSalaries(response.items);
      setTotalCount(response.total);
      
    } catch (err) {
      console.error('Error fetching salaries:', err);
      setError('Failed to fetch salary data. Please try again.');
      setSalaries([]);
      setTotalCount(0);
    } finally {
      setLoading(false);
    }
  }, [month, taxYear, statusFilter, departmentFilter, page, rowsPerPage]);

  const fetchSummary = useCallback(async () => {
    try {
      setSummaryLoading(true);
      
      const response = await salaryProcessingApi.getMonthlySalarySummary(month, taxYear);
      setSummary(response);
      
    } catch (err) {
      console.error('Error fetching summary:', err);
      setSummary(null);
    } finally {
      setSummaryLoading(false);
    }
  }, [month, taxYear]);

  useEffect(() => {
    fetchSalaries();
    fetchSummary();
  }, [month, taxYear, statusFilter, departmentFilter, page, rowsPerPage, fetchSalaries, fetchSummary]);

  const handleChangePage = (_: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
  };

  const filteredSalaries = salaries.filter(salary =>
    salary.employee_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    salary.employee_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    salary.employee_email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    salary.department?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleViewDetails = (salary: MonthlySalaryResponse) => {
    setSelectedSalary(salary);
    setDetailDialogOpen(true);
  };

  const handleDeleteSalary = async (salary: MonthlySalaryResponse) => {
    if (window.confirm(`Are you sure you want to delete the salary record for ${salary.employee_name || salary.employee_id}?`)) {
      try {
        await salaryProcessingApi.deleteMonthlySalary(
          salary.employee_id,
          salary.month,
          taxYear // Pass as string, not number
        );
        
        fetchSalaries();
        fetchSummary();
        
        alert('Salary record deleted successfully');
      } catch (err) {
        console.error('Error deleting salary:', err);
        alert('Failed to delete salary record');
      }
    }
  };

  const handleRefresh = () => {
    fetchSalaries();
    fetchSummary();
  };

  // Export functionality
  const handleExportClick = (event: React.MouseEvent<HTMLElement>) => {
    setExportAnchorEl(event.currentTarget);
  };

  const handleExportClose = () => {
    setExportAnchorEl(null);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'computed':
        return 'success';
      case 'pending':
        return 'warning';
      case 'approved':
        return 'info';
      case 'paid':
        return 'success';
      default:
        return 'default';
    }
  };

  // Export functions
  const exportToCSV = async () => {
    try {
      setExportLoading(true);
      handleExportClose();
      
      const filters: { status?: string; department?: string } = {};
      if (statusFilter) filters.status = statusFilter;
      if (departmentFilter) filters.department = departmentFilter;
      
      const blob = await exportApi.exportProcessedSalaries('csv', month, taxYearStringToStartYear(taxYear), filters);
      
      exportApi.downloadFile(blob, `processed_salaries_${month}_${taxYear}.csv`);
      
    } catch (err) {
      console.error('Error exporting to CSV:', err);
      alert('Failed to export to CSV. Please try again.');
    } finally {
      setExportLoading(false);
    }
  };

  const exportToExcel = async () => {
    try {
      setExportLoading(true);
      handleExportClose();
      
      const filters: { status?: string; department?: string } = {};
      if (statusFilter) filters.status = statusFilter;
      if (departmentFilter) filters.department = departmentFilter;
      
      const blob = await exportApi.exportProcessedSalaries('excel', month, taxYearStringToStartYear(taxYear), filters);
      
      exportApi.downloadFile(blob, `processed_salaries_${month}_${taxYear}.xlsx`);
      
    } catch (err) {
      console.error('Error exporting to Excel:', err);
      alert('Failed to export to Excel. Please try again.');
    } finally {
      setExportLoading(false);
    }
  };

  const exportBankTransferFormat = async () => {
    try {
      setExportLoading(true);
      handleExportClose();
      
      const filters: { status?: string; department?: string } = {};
      if (statusFilter) filters.status = statusFilter;
      if (departmentFilter) filters.department = departmentFilter;
      
      const blob = await exportApi.exportProcessedSalaries('bank_transfer', month, taxYearStringToStartYear(taxYear), filters);
      
      exportApi.downloadFile(blob, `bank_transfer_${month}_${taxYear}.csv`);
      
    } catch (err) {
      console.error('Error exporting bank transfer format:', err);
      alert('Failed to export bank transfer data. Please try again.');
    } finally {
      setExportLoading(false);
    }
  };

  const renderSummaryCards = () => (
    <Grid container spacing={3} sx={{ mb: 3 }}>
      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <Typography color="textSecondary" gutterBottom variant="body2">
                  Total Employees
                </Typography>
                <Typography variant="h4">
                  {summaryLoading ? <CircularProgress size={20} /> : (summary?.total_employees || 0)}
                </Typography>
              </Box>
              <PeopleIcon color="primary" sx={{ fontSize: 40 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
      
      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <Typography color="textSecondary" gutterBottom variant="body2">
                  Total Gross Payroll
                </Typography>
                <Typography variant="h4">
                  {summaryLoading ? <CircularProgress size={20} /> : formatCurrency(summary?.total_gross_payroll || 0)}
                </Typography>
              </Box>
              <AttachMoneyIcon color="primary" sx={{ fontSize: 40 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
      
      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <Typography color="textSecondary" gutterBottom variant="body2">
                  Total Net Payroll
                </Typography>
                <Typography variant="h4">
                  {summaryLoading ? <CircularProgress size={20} /> : formatCurrency(summary?.total_net_payroll || 0)}
                </Typography>
              </Box>
              <ReceiptIcon color="primary" sx={{ fontSize: 40 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
      
      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <Typography color="textSecondary" gutterBottom variant="body2">
                  Total TDS
                </Typography>
                <Typography variant="h4">
                  {summaryLoading ? <CircularProgress size={20} /> : formatCurrency(summary?.total_tds || 0)}
                </Typography>
              </Box>
              <TrendingUpIcon color="primary" sx={{ fontSize: 40 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderFilters = () => (
    <Paper sx={{ p: 2, mb: 3 }}>
      <Grid container spacing={2} alignItems="center">
        <Grid item xs={12} sm={6} md={2}>
          <FormControl fullWidth size="small">
            <InputLabel>Month</InputLabel>
            <Select
              value={month}
              label="Month"
              onChange={(e) => setMonth(e.target.value as number)}
            >
              {Array.from({ length: 12 }, (_, i) => ({
                value: i + 1,
                label: new Date(0, i).toLocaleString('en-US', { month: 'long' })
              })).map((month) => (
                <MenuItem key={month.value} value={month.value}>
                  {month.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} sm={6} md={2}>
          <FormControl fullWidth size="small">
            <InputLabel>Tax Year</InputLabel>
            <Select
              value={taxYear}
              label="Tax Year"
              onChange={(e) => setTaxYear(e.target.value as string)}
            >
              {getAvailableTaxYears().map((year) => (
                <MenuItem key={year} value={year}>
                  {year}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} sm={6} md={2}>
          <FormControl fullWidth size="small">
            <InputLabel>Status</InputLabel>
            <Select
              value={statusFilter}
              label="Status"
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="computed">Computed</MenuItem>
              <MenuItem value="pending">Pending</MenuItem>
              <MenuItem value="approved">Approved</MenuItem>
              <MenuItem value="paid">Paid</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} sm={6} md={2}>
          <TextField
            fullWidth
            size="small"
            label="Department"
            value={departmentFilter}
            onChange={(e) => setDepartmentFilter(e.target.value)}
            placeholder="Filter by department"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={2}>
          <TextField
            fullWidth
            size="small"
            label="Search"
            value={searchTerm}
            onChange={handleSearch}
            placeholder="Search employees..."
            InputProps={{
              startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
            }}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={2}>
          <Button
            variant="contained"
            startIcon={exportLoading ? <CircularProgress size={16} /> : <FileDownloadIcon />}
            onClick={handleExportClick}
            disabled={exportLoading || filteredSalaries.length === 0}
            fullWidth
            sx={{ minWidth: 100 }}
          >
            Export
          </Button>
        </Grid>
      </Grid>
    </Paper>
  );

  const renderSalaryDetailsDialog = () => (
    <Dialog
      open={detailDialogOpen}
      onClose={() => setDetailDialogOpen(false)}
      maxWidth="md"
      fullWidth
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <ReceiptIcon color="primary" />
          <Typography variant="h6">
            Salary Details - {selectedSalary?.employee_name || selectedSalary?.employee_id}
          </Typography>
        </Box>
      </DialogTitle>
      <DialogContent>
        {selectedSalary && (
          <Grid container spacing={3}>
            {/* Employee Information */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Employee Information
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Employee ID</Typography>
                  <Typography variant="body1">{selectedSalary.employee_id}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Name</Typography>
                  <Typography variant="body1">{selectedSalary.employee_name || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Email</Typography>
                  <Typography variant="body1">{selectedSalary.employee_email || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Department</Typography>
                  <Typography variant="body1">{selectedSalary.department || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Designation</Typography>
                  <Typography variant="body1">{selectedSalary.designation || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Tax Regime</Typography>
                  <Typography variant="body1">{selectedSalary.tax_regime}</Typography>
                </Grid>
              </Grid>
            </Grid>

            {/* Salary Components */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Salary Components
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Basic Salary</Typography>
                  <Typography variant="body1">{formatCurrency(selectedSalary.basic_salary)}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Dearness Allowance</Typography>
                  <Typography variant="body1">{formatCurrency(selectedSalary.da)}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">HRA</Typography>
                  <Typography variant="body1">{formatCurrency(selectedSalary.hra)}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Special Allowance</Typography>
                  <Typography variant="body1">{formatCurrency(selectedSalary.special_allowance)}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Bonus</Typography>
                  <Typography variant="body1">{formatCurrency(selectedSalary.bonus)}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Commission</Typography>
                  <Typography variant="body1">{formatCurrency(selectedSalary.commission)}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Arrears</Typography>
                  <Typography variant="body1">{formatCurrency(selectedSalary.arrears || 0)}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Gross Salary</Typography>
                  <Typography variant="body1" fontWeight="bold">{formatCurrency(selectedSalary.gross_salary)}</Typography>
                </Grid>
              </Grid>
            </Grid>

            {/* Deductions */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Deductions
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">EPF Employee</Typography>
                  <Typography variant="body1">{formatCurrency(selectedSalary.epf_employee)}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">ESI Employee</Typography>
                  <Typography variant="body1">{formatCurrency(selectedSalary.esi_employee)}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Professional Tax</Typography>
                  <Typography variant="body1">{formatCurrency(selectedSalary.professional_tax)}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">TDS</Typography>
                  <Typography variant="body1">{formatCurrency(selectedSalary.tds)}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Total Deductions</Typography>
                  <Typography variant="body1" fontWeight="bold">{formatCurrency(selectedSalary.total_deductions)}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Net Salary</Typography>
                  <Typography variant="body1" fontWeight="bold" color="primary">
                    {formatCurrency(selectedSalary.net_salary)}
                  </Typography>
                </Grid>
              </Grid>
            </Grid>

            {/* Working Days */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Working Days
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Total Days in Month</Typography>
                  <Typography variant="body1">{selectedSalary.total_days_in_month}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Working Days</Typography>
                  <Typography variant="body1">{selectedSalary.working_days_in_period}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">LWP Days</Typography>
                  <Typography variant="body1">{selectedSalary.lwp_days}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Effective Working Days</Typography>
                  <Typography variant="body1">{selectedSalary.effective_working_days}</Typography>
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setDetailDialogOpen(false)}>Close</Button>
      </DialogActions>
    </Dialog>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4" gutterBottom>
          Processed Salaries
        </Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={handleRefresh}
          sx={{ minWidth: 100 }}
        >
          Refresh
        </Button>
      </Box>
      <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
        View and manage all processed monthly salary records
      </Typography>

      {/* Summary Cards */}
      {renderSummaryCards()}

      {/* Filters */}
      {renderFilters()}

      {/* Export Menu */}
      <Menu
        anchorEl={exportAnchorEl}
        open={Boolean(exportAnchorEl)}
        onClose={handleExportClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        <MenuItem onClick={exportToCSV} disabled={exportLoading}>
          <ListItemIcon>
            <TableChartIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Export to CSV (Complete Data)</ListItemText>
        </MenuItem>
        <MenuItem onClick={exportToExcel} disabled={exportLoading}>
          <ListItemIcon>
            <GridOnIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Export to Excel (Complete Data)</ListItemText>
        </MenuItem>
        <MenuItem onClick={exportBankTransferFormat} disabled={exportLoading}>
          <ListItemIcon>
            <AttachMoneyIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Export Bank Transfer Format</ListItemText>
        </MenuItem>
      </Menu>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Salaries Table */}
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Employee</TableCell>
                <TableCell>Department</TableCell>
                <TableCell>Basic Salary</TableCell>
                <TableCell>Gross Salary</TableCell>
                <TableCell>Net Salary</TableCell>
                <TableCell>TDS</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : filteredSalaries.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                    <Typography variant="body1" color="textSecondary">
                      {searchTerm ? 'No salaries found matching your search' : 'No salary records found for the selected period'}
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                filteredSalaries.map((salary) => (
                  <TableRow key={`${salary.employee_id}-${salary.month}-${salary.year}`}>
                    <TableCell>
                      <Box>
                        <Typography variant="body1" fontWeight="medium">
                          {salary.employee_name || salary.employee_id}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          {salary.employee_email}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>{salary.department || 'N/A'}</TableCell>
                    <TableCell>{formatCurrency(salary.basic_salary)}</TableCell>
                    <TableCell>{formatCurrency(salary.gross_salary)}</TableCell>
                    <TableCell>{formatCurrency(salary.net_salary)}</TableCell>
                    <TableCell>{formatCurrency(salary.tds)}</TableCell>
                    <TableCell>
                      <Chip
                        label={salary.status}
                        color={getStatusColor(salary.status) as any}
                        size="small"
                        onClick={isAdminUser ? () => handleStatusChipClick(salary) : undefined}
                        style={{ cursor: isAdminUser ? 'pointer' : 'default' }}
                      />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Tooltip title="View Details">
                          <IconButton
                            size="small"
                            onClick={() => handleViewDetails(salary)}
                            color="primary"
                          >
                            <VisibilityIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete">
                          <IconButton
                            size="small"
                            onClick={() => handleDeleteSalary(salary)}
                            color="error"
                          >
                            <DeleteIcon />
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
        
        {/* Pagination */}
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50]}
          component="div"
          count={totalCount}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>

      {/* Salary Details Dialog */}
      {renderSalaryDetailsDialog()}

      {statusDialogOpen && statusDialogSalary && (
        <Dialog open={statusDialogOpen} onClose={handleStatusDialogClose} maxWidth="xs" fullWidth>
          <DialogTitle>Status Transition</DialogTitle>
          <DialogContent>
            <Typography gutterBottom>Current Status: <b>{statusDialogSalary.status}</b></Typography>
            <FormControl fullWidth sx={{ mt: 2 }}>
              <InputLabel>Next Status</InputLabel>
              <Select
                value={nextStatus}
                label="Next Status"
                onChange={e => setNextStatus(e.target.value)}
              >
                {getNextStatusOptions(statusDialogSalary.status).map(opt => (
                  <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="Comments"
              value={statusComments}
              onChange={e => setStatusComments(e.target.value)}
              fullWidth
              required
              multiline
              minRows={2}
              sx={{ mt: 2 }}
            />
            {nextStatus === 'transferred' && (
              <>
                <TextField
                  label="Transaction ID"
                  value={transactionId}
                  onChange={e => setTransactionId(e.target.value)}
                  fullWidth
                  required
                  sx={{ mt: 2 }}
                />
                <TextField
                  label="Transfer Date"
                  type="date"
                  value={transferDate}
                  onChange={e => setTransferDate(e.target.value)}
                  fullWidth
                  required
                  sx={{ mt: 2 }}
                  InputLabelProps={{ shrink: true }}
                />
              </>
            )}
            {statusUpdateError && <Alert severity="error" sx={{ mt: 2 }}>{statusUpdateError}</Alert>}
          </DialogContent>
          <DialogActions>
            <Button onClick={handleStatusDialogClose} disabled={statusUpdateLoading}>Cancel</Button>
            <Button onClick={handleStatusUpdate} variant="contained" disabled={statusUpdateLoading || !nextStatus}>
              {statusUpdateLoading ? <CircularProgress size={20} /> : 'Update Status'}
            </Button>
          </DialogActions>
        </Dialog>
      )}
    </Box>
  );
};

export default ProcessedSalaries; 