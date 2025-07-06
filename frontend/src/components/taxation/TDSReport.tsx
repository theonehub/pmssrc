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
  TrendingUp as TrendingUpIcon,
  People as PeopleIcon,
  FileDownload as FileDownloadIcon,
  TableChart as TableChartIcon,
  GridOn as GridOnIcon,
  AccountBalance as AccountBalanceIcon,
  Assessment as AssessmentIcon,
  Description as DescriptionIcon
} from '@mui/icons-material';

/**
 * TDS Report Component - Display TDS information for tax reporting
 */
const TDSReport: React.FC = () => {
  const [salaries, setSalaries] = useState<MonthlySalaryResponse[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  const [month, setMonth] = useState<number>(new Date().getMonth() + 1);
  const [year, setYear] = useState<number>(new Date().getFullYear());
  const [taxYear, setTaxYear] = useState<string>('');
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

  // TDS specific states
  const [tdsSummary, setTdsSummary] = useState<any>(null);

  // 1. Add quarter selector state
  const [selectedQuarter, setSelectedQuarter] = useState<number>(Math.ceil((month) / 3));

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
        year,
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
  }, [month, year, statusFilter, departmentFilter, page, rowsPerPage]);

  const fetchSummary = useCallback(async () => {
    try {
      setSummaryLoading(true);
      
      const response = await salaryProcessingApi.getMonthlySalarySummary(month, year);
      setSummary(response);
      
    } catch (err) {
      console.error('Error fetching summary:', err);
      setSummary(null);
    } finally {
      setSummaryLoading(false);
    }
  }, [month, year]);

  // Calculate TDS summary
  const calculateTDSSummary = useCallback(() => {
    if (!salaries.length) return null;

    const tdsData = salaries.filter(salary => salary.tds > 0);
    
    const summary = {
      totalEmployees: salaries.length,
      employeesWithTDS: tdsData.length,
      totalTDS: tdsData.reduce((sum, salary) => sum + salary.tds, 0),
      averageTDS: tdsData.length > 0 ? tdsData.reduce((sum, salary) => sum + salary.tds, 0) / tdsData.length : 0,
      totalGrossSalary: salaries.reduce((sum, salary) => sum + salary.gross_salary, 0),
      totalNetSalary: salaries.reduce((sum, salary) => sum + salary.net_salary, 0),
      tdsByDepartment: {} as Record<string, number>,
      tdsByTaxRegime: {} as Record<string, number>,
      monthlyTDS: {} as Record<string, number>
    };

    // Calculate TDS by department
    tdsData.forEach(salary => {
      const dept = salary.department || 'Unknown';
      summary.tdsByDepartment[dept] = (summary.tdsByDepartment[dept] || 0) + salary.tds;
    });

    // Calculate TDS by tax regime
    tdsData.forEach(salary => {
      const regime = salary.tax_regime || 'Unknown';
      summary.tdsByTaxRegime[regime] = (summary.tdsByTaxRegime[regime] || 0) + salary.tds;
    });

    // Calculate monthly TDS
    tdsData.forEach(salary => {
      const monthKey = `${salary.month}/${salary.year}`;
      summary.monthlyTDS[monthKey] = (summary.monthlyTDS[monthKey] || 0) + salary.tds;
    });

    return summary;
  }, [salaries]);

  useEffect(() => {
    fetchSalaries();
    fetchSummary();
  }, [month, year, statusFilter, departmentFilter, page, rowsPerPage, fetchSalaries, fetchSummary]);

  // Calculate TDS summary when salaries change
  useEffect(() => {
    const summary = calculateTDSSummary();
    setTdsSummary(summary);
  }, [salaries, calculateTDSSummary]);

  // Set tax year based on selected year
  useEffect(() => {
    setTaxYear(`${year}-${year + 1}`);
  }, [year]);

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
  const exportTDSToCSV = async () => {
    try {
      setExportLoading(true);
      handleExportClose();
      
      const filters: { status?: string; department?: string } = {};
      if (statusFilter) filters.status = statusFilter;
      if (departmentFilter) filters.department = departmentFilter;
      
      const blob = await exportApi.exportTDSReport('csv', month, year, undefined, filters);
      
      exportApi.downloadFile(blob, `tds_report_${month}_${year}.csv`);
      
    } catch (err) {
      console.error('Error exporting TDS to CSV:', err);
      alert('Failed to export TDS to CSV. Please try again.');
    } finally {
      setExportLoading(false);
    }
  };

  const exportTDSToExcel = async () => {
    try {
      setExportLoading(true);
      handleExportClose();
      
      const filters: { status?: string; department?: string } = {};
      if (statusFilter) filters.status = statusFilter;
      if (departmentFilter) filters.department = departmentFilter;
      
      const blob = await exportApi.exportTDSReport('excel', month, year, undefined, filters);
      
      exportApi.downloadFile(blob, `tds_report_${month}_${year}.xlsx`);
      
    } catch (err) {
      console.error('Error exporting TDS to Excel:', err);
      alert('Failed to export TDS to Excel. Please try again.');
    } finally {
      setExportLoading(false);
    }
  };

  const exportTDSForm16Format = async () => {
    try {
      setExportLoading(true);
      handleExportClose();
      
      const filters: { status?: string; department?: string } = {};
      if (statusFilter) filters.status = statusFilter;
      if (departmentFilter) filters.department = departmentFilter;
      
      const blob = await exportApi.exportTDSReport('form_16', month, year, undefined, filters);
      
      exportApi.downloadFile(blob, `form_16_${year}.csv`);
      
    } catch (err) {
      console.error('Error exporting Form 16:', err);
      alert('Failed to export Form 16. Please try again.');
    } finally {
      setExportLoading(false);
    }
  };

  const exportForm24Q = async () => {
    try {
      setExportLoading(true);
      handleExportClose();
      
      const blob = await exportApi.exportForm24Q(selectedQuarter, year, 'csv');
      
      exportApi.downloadFile(blob, `form_24q_q${selectedQuarter}_${year}.csv`);
      
    } catch (err) {
      console.error('Error exporting Form 24Q:', err);
      alert('Failed to export Form 24Q. Please try again.');
    } finally {
      setExportLoading(false);
    }
  };

  const exportFVUForm24Q = async () => {
    try {
      setExportLoading(true);
      handleExportClose();
      
      const blob = await exportApi.exportForm24Q(selectedQuarter, year, 'fvu');
      
      exportApi.downloadFile(blob, `form24q_q${selectedQuarter}_${year}_FVU.txt`);
      
    } catch (err) {
      console.error('Error exporting FVU Form 24Q:', err);
      alert('Failed to export FVU Form 24Q. Please try again.');
    } finally {
      setExportLoading(false);
    }
  };

  const renderTDSSummaryCards = () => (
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
                  Employees with TDS
                </Typography>
                <Typography variant="h4">
                  {tdsSummary ? tdsSummary.employeesWithTDS : 0}
                </Typography>
              </Box>
              <AccountBalanceIcon color="primary" sx={{ fontSize: 40 }} />
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
                  Total TDS Amount
                </Typography>
                <Typography variant="h4">
                  {tdsSummary ? formatCurrency(tdsSummary.totalTDS) : formatCurrency(0)}
                </Typography>
              </Box>
              <TrendingUpIcon color="primary" sx={{ fontSize: 40 }} />
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
                  Average TDS per Employee
                </Typography>
                <Typography variant="h4">
                  {tdsSummary ? formatCurrency(tdsSummary.averageTDS) : formatCurrency(0)}
                </Typography>
              </Box>
              <AssessmentIcon color="primary" sx={{ fontSize: 40 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderTDSBreakdown = () => (
    <Grid container spacing={3} sx={{ mb: 3 }}>
      {/* TDS by Department */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              TDS by Department
            </Typography>
            <Divider sx={{ mb: 2 }} />
            {tdsSummary && Object.keys(tdsSummary.tdsByDepartment).length > 0 ? (
              Object.entries(tdsSummary.tdsByDepartment).map(([dept, amount]) => (
                <Box key={dept} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">{dept}</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {formatCurrency(amount as number)}
                  </Typography>
                </Box>
              ))
            ) : (
              <Typography variant="body2" color="textSecondary">
                No TDS data available
              </Typography>
            )}
          </CardContent>
        </Card>
      </Grid>

      {/* TDS by Tax Regime */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              TDS by Tax Regime
            </Typography>
            <Divider sx={{ mb: 2 }} />
            {tdsSummary && Object.keys(tdsSummary.tdsByTaxRegime).length > 0 ? (
              Object.entries(tdsSummary.tdsByTaxRegime).map(([regime, amount]) => (
                <Box key={regime} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">{regime.toUpperCase()}</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {formatCurrency(amount as number)}
                  </Typography>
                </Box>
              ))
            ) : (
              <Typography variant="body2" color="textSecondary">
                No TDS data available
              </Typography>
            )}
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
            <InputLabel>Quarter</InputLabel>
            <Select
              value={selectedQuarter}
              label="Quarter"
              onChange={(e) => setSelectedQuarter(Number(e.target.value))}
            >
              <MenuItem value={1}>Q1 (Apr-Jun)</MenuItem>
              <MenuItem value={2}>Q2 (Jul-Sep)</MenuItem>
              <MenuItem value={3}>Q3 (Oct-Dec)</MenuItem>
              <MenuItem value={4}>Q4 (Jan-Mar)</MenuItem>
            </Select>
          </FormControl>
        </Grid>
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
            <InputLabel>Year</InputLabel>
            <Select
              value={year}
              label="Year"
              onChange={(e) => setYear(e.target.value as number)}
            >
              {Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - 2 + i).map((year) => (
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

  const renderTDSDetailsDialog = () => (
    <Dialog
      open={detailDialogOpen}
      onClose={() => setDetailDialogOpen(false)}
      maxWidth="md"
      fullWidth
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <AssessmentIcon color="primary" />
          <Typography variant="h6">
            TDS Details - {selectedSalary?.employee_name || selectedSalary?.employee_id}
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
                  <Typography variant="body2" color="textSecondary">Tax Regime</Typography>
                  <Typography variant="body1">{selectedSalary.tax_regime}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Tax Year</Typography>
                  <Typography variant="body1">{selectedSalary.tax_year}</Typography>
                </Grid>
              </Grid>
            </Grid>

            {/* TDS Information */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                TDS Information
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Monthly TDS</Typography>
                  <Typography variant="body1" color="error" fontWeight="bold">
                    {formatCurrency(selectedSalary.tds)}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Annual Tax Liability</Typography>
                  <Typography variant="body1" fontWeight="bold">
                    {formatCurrency(selectedSalary.annual_tax_liability)}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Gross Salary</Typography>
                  <Typography variant="body1">{formatCurrency(selectedSalary.gross_salary)}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Net Salary</Typography>
                  <Typography variant="body1">{formatCurrency(selectedSalary.net_salary)}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Annual Gross Salary</Typography>
                  <Typography variant="body1">{formatCurrency(selectedSalary.annual_gross_salary)}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">TDS Payment Reference</Typography>
                  <Typography variant="body1" fontFamily="monospace">
                    TDS_{selectedSalary.employee_id}_{selectedSalary.month}_{selectedSalary.year}
                  </Typography>
                </Grid>
              </Grid>
            </Grid>

            {/* Salary Breakdown */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Salary Breakdown
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
          TDS Report
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
        Tax Deducted at Source (TDS) reporting and analysis for {taxYear}
      </Typography>

      {/* TDS Summary Cards */}
      {renderTDSSummaryCards()}

      {/* TDS Breakdown */}
      {renderTDSBreakdown()}

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
        <MenuItem onClick={exportTDSToCSV} disabled={exportLoading}>
          <ListItemIcon>
            <TableChartIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Export TDS to CSV</ListItemText>
        </MenuItem>
        <MenuItem onClick={exportTDSToExcel} disabled={exportLoading}>
          <ListItemIcon>
            <GridOnIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Export TDS to Excel</ListItemText>
        </MenuItem>
        <MenuItem onClick={exportTDSForm16Format} disabled={exportLoading}>
          <ListItemIcon>
            <DescriptionIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Export Form 16 Format</ListItemText>
        </MenuItem>
        <MenuItem onClick={exportForm24Q} disabled={exportLoading}>
          <ListItemIcon>
            <DescriptionIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Export Form 24Q</ListItemText>
        </MenuItem>
        <MenuItem onClick={exportFVUForm24Q} disabled={exportLoading}>
          <ListItemIcon>
            <DescriptionIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Export FVU (Form 24Q)</ListItemText>
        </MenuItem>
      </Menu>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* TDS Table */}
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Employee</TableCell>
                <TableCell>Department</TableCell>
                <TableCell>Tax Regime</TableCell>
                <TableCell>Gross Salary</TableCell>
                <TableCell>Net Salary</TableCell>
                <TableCell>TDS Amount</TableCell>
                <TableCell>Annual Tax Liability</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={9} align="center" sx={{ py: 4 }}>
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : filteredSalaries.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={9} align="center" sx={{ py: 4 }}>
                    <Typography variant="body1" color="textSecondary">
                      {searchTerm ? 'No TDS records found matching your search' : 'No TDS records found for the selected period'}
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                filteredSalaries
                  .filter(salary => salary.tds > 0) // Only show employees with TDS
                  .map((salary) => (
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
                      <TableCell>
                        <Chip
                          label={salary.tax_regime.toUpperCase()}
                          color="primary"
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{formatCurrency(salary.gross_salary)}</TableCell>
                      <TableCell>{formatCurrency(salary.net_salary)}</TableCell>
                      <TableCell>
                        <Typography variant="body1" color="error" fontWeight="bold">
                          {formatCurrency(salary.tds)}
                        </Typography>
                      </TableCell>
                      <TableCell>{formatCurrency(salary.annual_tax_liability)}</TableCell>
                      <TableCell>
                        <Chip
                          label={salary.status}
                          color={getStatusColor(salary.status) as any}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Tooltip title="View TDS Details">
                          <IconButton
                            size="small"
                            onClick={() => handleViewDetails(salary)}
                            color="primary"
                          >
                            <VisibilityIcon />
                          </IconButton>
                        </Tooltip>
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

      {/* TDS Details Dialog */}
      {renderTDSDetailsDialog()}
    </Box>
  );
};

export default TDSReport; 