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
  People as PeopleIcon,
  FileDownload as FileDownloadIcon,
  TableChart as TableChartIcon,
  GridOn as GridOnIcon,
  AccountBalance as AccountBalanceIcon,
  Assessment as AssessmentIcon,
  Description as DescriptionIcon,
  Savings as SavingsIcon
} from '@mui/icons-material';
import { getCurrentTaxYear, getAvailableTaxYears, taxYearStringToStartYear } from '../../shared/utils/formatting';

/**
 * PF Report Component - Display Provident Fund information for reporting
 */
const PFReport: React.FC = () => {
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

  // PF specific states
  const [pfSummary, setPfSummary] = useState<any>(null);

  // Quarter selector state
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
        taxYear,
        params
      );
      
      setSalaries(response.items);
      setTotalCount(response.total);
      
    } catch (error: any) {
      const backendMessage = error?.response?.data?.detail;
      setError(backendMessage || 'Failed to fetch PF report.');
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
      
    } catch (error: any) {
      const backendMessage = error?.response?.data?.detail;
      setError(backendMessage || 'Failed to fetch summary. Please try again.');
      setSummary(null);
    } finally {
      setSummaryLoading(false);
    }
  }, [month, taxYear]);

  // Calculate PF summary
  const calculatePFSummary = useCallback(() => {
    if (!salaries.length) return null;

    const pfData = salaries.filter(salary => salary.epf_employee > 0);
    
    const summary = {
      totalEmployees: salaries.length,
      employeesWithPF: pfData.length,
      totalEmployeePF: pfData.reduce((sum, salary) => sum + salary.epf_employee, 0),
      totalEmployerPF: pfData.reduce((sum, salary) => sum + (salary.epf_employee || 0), 0), // Assuming employer PF equals employee PF
      totalPFContribution: pfData.reduce((sum, salary) => sum + salary.epf_employee * 2, 0), // Employee + Employer
      averageEmployeePF: pfData.length > 0 ? pfData.reduce((sum, salary) => sum + salary.epf_employee, 0) / pfData.length : 0,
      averageEmployerPF: pfData.length > 0 ? pfData.reduce((sum, salary) => sum + (salary.epf_employee || 0), 0) / pfData.length : 0,
      totalGrossSalary: salaries.reduce((sum, salary) => sum + salary.gross_salary, 0),
      totalNetSalary: salaries.reduce((sum, salary) => sum + salary.net_salary, 0),
      pfByDepartment: {} as Record<string, { employee: number; employer: number; total: number }>,
      pfByTaxRegime: {} as Record<string, { employee: number; employer: number; total: number }>,
      monthlyPF: {} as Record<string, { employee: number; employer: number; total: number }>
    };

    // Calculate PF by department
    pfData.forEach(salary => {
      const dept = salary.department || 'Unknown';
      const employerPF = salary.epf_employee || 0; // Assuming employer PF equals employee PF
      const totalPF = salary.epf_employee + employerPF;
      
      if (!summary.pfByDepartment[dept]) {
        summary.pfByDepartment[dept] = { employee: 0, employer: 0, total: 0 };
      }
      const deptData = summary.pfByDepartment[dept];
      if (deptData) {
        deptData.employee += salary.epf_employee;
        deptData.employer += employerPF;
        deptData.total += totalPF;
      }
    });

    // Calculate PF by tax regime
    pfData.forEach(salary => {
      const regime = salary.tax_regime || 'Unknown';
      const employerPF = salary.epf_employee || 0;
      const totalPF = salary.epf_employee + employerPF;
      
      if (!summary.pfByTaxRegime[regime]) {
        summary.pfByTaxRegime[regime] = { employee: 0, employer: 0, total: 0 };
      }
      const regimeData = summary.pfByTaxRegime[regime];
      if (regimeData) {
        regimeData.employee += salary.epf_employee;
        regimeData.employer += employerPF;
        regimeData.total += totalPF;
      }
    });

    // Calculate monthly PF
    pfData.forEach(salary => {
      const monthKey = `${salary.month}/${salary.year}`;
      const employerPF = salary.epf_employee || 0;
      const totalPF = salary.epf_employee + employerPF;
      
      if (!summary.monthlyPF[monthKey]) {
        summary.monthlyPF[monthKey] = { employee: 0, employer: 0, total: 0 };
      }
      const monthData = summary.monthlyPF[monthKey];
      if (monthData) {
        monthData.employee += salary.epf_employee;
        monthData.employer += employerPF;
        monthData.total += totalPF;
      }
    });

    return summary;
  }, [salaries]);

  useEffect(() => {
    fetchSalaries();
    fetchSummary();
  }, [month, taxYear, statusFilter, departmentFilter, page, rowsPerPage, fetchSalaries, fetchSummary]);

  // Calculate PF summary when salaries change
  useEffect(() => {
    const summary = calculatePFSummary();
    setPfSummary(summary);
  }, [salaries, calculatePFSummary]);

  // Set tax year based on selected year
  useEffect(() => {
    setTaxYear(`${new Date().getFullYear()}-${new Date().getFullYear() + 1}`);
  }, []);

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
  const exportPFToCSV = async () => {
    try {
      setExportLoading(true);
      handleExportClose();
      
      const filters: { status?: string; department?: string } = {};
      if (statusFilter) filters.status = statusFilter;
      if (departmentFilter) filters.department = departmentFilter;
      
      const blob = await exportApi.exportPFReport('csv', month, taxYearStringToStartYear(taxYear), undefined, filters);
      
      exportApi.downloadFile(blob, `pf_report_${month}_${taxYear}.csv`);
      
    } catch (error: any) {
      const backendMessage = error?.response?.data?.detail;
      setError(backendMessage || 'Failed to export PF to CSV. Please try again.');
    } finally {
      setExportLoading(false);
    }
  };

  const exportPFToExcel = async () => {
    try {
      setExportLoading(true);
      handleExportClose();
      
      const filters: { status?: string; department?: string } = {};
      if (statusFilter) filters.status = statusFilter;
      if (departmentFilter) filters.department = departmentFilter;
      
      const blob = await exportApi.exportPFReport('excel', month, taxYearStringToStartYear(taxYear), undefined, filters);
      
      exportApi.downloadFile(blob, `pf_report_${month}_${taxYear}.xlsx`);
      
    } catch (error: any) {
      const backendMessage = error?.response?.data?.detail;
      setError(backendMessage || 'Failed to export PF to Excel. Please try again.');
    } finally {
      setExportLoading(false);
    }
  };

  const exportPFChallan = async () => {
    try {
      setExportLoading(true);
      handleExportClose();
      
      const filters: { status?: string; department?: string } = {};
      if (statusFilter) filters.status = statusFilter;
      if (departmentFilter) filters.department = departmentFilter;
      
      const blob = await exportApi.exportPFReport('challan', month, taxYearStringToStartYear(taxYear), undefined, filters);
      
      exportApi.downloadFile(blob, `pf_challan_${month}_${taxYear}.pdf`);
      
    } catch (error: any) {
      const backendMessage = error?.response?.data?.detail;
      setError(backendMessage || 'Failed to export PF Challan. Please try again.');
    } finally {
      setExportLoading(false);
    }
  };

  const exportPFReturn = async () => {
    try {
      setExportLoading(true);
      handleExportClose();
      
      const filters: { status?: string; department?: string } = {};
      if (statusFilter) filters.status = statusFilter;
      if (departmentFilter) filters.department = departmentFilter;
      
      const blob = await exportApi.exportPFReport('return', month, taxYearStringToStartYear(taxYear), undefined, filters);
      
      exportApi.downloadFile(blob, `pf_return_${month}_${taxYear}.pdf`);
      
    } catch (error: any) {
      const backendMessage = error?.response?.data?.detail;
      setError(backendMessage || 'Failed to export PF Return. Please try again.');
    } finally {
      setExportLoading(false);
    }
  };

  const renderPFSummaryCards = () => (
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
                  Employees with PF
                </Typography>
                <Typography variant="h4">
                  {pfSummary ? pfSummary.employeesWithPF : 0}
                </Typography>
              </Box>
              <SavingsIcon color="primary" sx={{ fontSize: 40 }} />
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
                  Total PF Contribution
                </Typography>
                <Typography variant="h4">
                  {pfSummary ? formatCurrency(pfSummary.totalPFContribution) : formatCurrency(0)}
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
                  Average PF per Employee
                </Typography>
                <Typography variant="h4">
                  {pfSummary ? formatCurrency(pfSummary.averageEmployeePF) : formatCurrency(0)}
                </Typography>
              </Box>
              <AssessmentIcon color="primary" sx={{ fontSize: 40 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderPFBreakdown = () => (
    <Grid container spacing={3} sx={{ mb: 3 }}>
      {/* PF by Department */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              PF by Department
            </Typography>
            <Divider sx={{ mb: 2 }} />
            {pfSummary && Object.keys(pfSummary.pfByDepartment).length > 0 ? (
              Object.entries(pfSummary.pfByDepartment).map(([dept, data]) => (
                <Box key={dept} sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" fontWeight="bold">{dept}</Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', ml: 2 }}>
                    <Typography variant="body2">Employee PF:</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {formatCurrency((data as any).employee)}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', ml: 2 }}>
                    <Typography variant="body2">Employer PF:</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {formatCurrency((data as any).employer)}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', ml: 2 }}>
                    <Typography variant="body2" color="primary" fontWeight="bold">Total:</Typography>
                    <Typography variant="body2" color="primary" fontWeight="bold">
                      {formatCurrency((data as any).total)}
                    </Typography>
                  </Box>
                </Box>
              ))
            ) : (
              <Typography variant="body2" color="textSecondary">
                No PF data available
              </Typography>
            )}
          </CardContent>
        </Card>
      </Grid>

      {/* PF by Tax Regime */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              PF by Tax Regime
            </Typography>
            <Divider sx={{ mb: 2 }} />
            {pfSummary && Object.keys(pfSummary.pfByTaxRegime).length > 0 ? (
              Object.entries(pfSummary.pfByTaxRegime).map(([regime, data]) => (
                <Box key={regime} sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" fontWeight="bold">{regime.toUpperCase()}</Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', ml: 2 }}>
                    <Typography variant="body2">Employee PF:</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {formatCurrency((data as any).employee)}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', ml: 2 }}>
                    <Typography variant="body2">Employer PF:</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {formatCurrency((data as any).employer)}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', ml: 2 }}>
                    <Typography variant="body2" color="primary" fontWeight="bold">Total:</Typography>
                    <Typography variant="body2" color="primary" fontWeight="bold">
                      {formatCurrency((data as any).total)}
                    </Typography>
                  </Box>
                </Box>
              ))
            ) : (
              <Typography variant="body2" color="textSecondary">
                No PF data available
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
              value={taxYear}
              label="Year"
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

  const renderPFDetailsDialog = () => (
    <Dialog
      open={detailDialogOpen}
      onClose={() => setDetailDialogOpen(false)}
      maxWidth="md"
      fullWidth
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <SavingsIcon color="primary" />
          <Typography variant="h6">
            PF Details - {selectedSalary?.employee_name || selectedSalary?.employee_id}
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

            {/* PF Information */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Provident Fund Information
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Employee PF</Typography>
                  <Typography variant="body1" color="primary" fontWeight="bold">
                    {formatCurrency(selectedSalary.epf_employee)}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Employer PF</Typography>
                  <Typography variant="body1" color="primary" fontWeight="bold">
                    {formatCurrency(selectedSalary.epf_employee || 0)}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Total PF Contribution</Typography>
                  <Typography variant="body1" color="primary" fontWeight="bold">
                    {formatCurrency(selectedSalary.epf_employee * 2)}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">PF Rate</Typography>
                  <Typography variant="body1">12% (Employee) + 12% (Employer)</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">PF UAN</Typography>
                  <Typography variant="body1" fontFamily="monospace">
                    {selectedSalary.employee_id.replace(/\D/g, '').padStart(12, '0')}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">PF Payment Reference</Typography>
                  <Typography variant="body1" fontFamily="monospace">
                    PF_{selectedSalary.employee_id}_{selectedSalary.month}_{selectedSalary.year}
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
                  <Typography variant="body2" color="textSecondary">Gross Salary</Typography>
                  <Typography variant="body1">{formatCurrency(selectedSalary.gross_salary)}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Net Salary</Typography>
                  <Typography variant="body1">{formatCurrency(selectedSalary.net_salary)}</Typography>
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
          PF Report
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
        Provident Fund (PF) reporting and analysis for {taxYear}
      </Typography>

      {/* PF Summary Cards */}
      {renderPFSummaryCards()}

      {/* PF Breakdown */}
      {renderPFBreakdown()}

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
        <MenuItem onClick={exportPFToCSV} disabled={exportLoading}>
          <ListItemIcon>
            <TableChartIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Export PF to CSV</ListItemText>
        </MenuItem>
        <MenuItem onClick={exportPFToExcel} disabled={exportLoading}>
          <ListItemIcon>
            <GridOnIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Export PF to Excel</ListItemText>
        </MenuItem>
        <MenuItem onClick={exportPFChallan} disabled={exportLoading}>
          <ListItemIcon>
            <DescriptionIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Export PF Challan</ListItemText>
        </MenuItem>
        <MenuItem onClick={exportPFReturn} disabled={exportLoading}>
          <ListItemIcon>
            <DescriptionIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Export PF Return</ListItemText>
        </MenuItem>
      </Menu>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* PF Table */}
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Employee</TableCell>
                <TableCell>Department</TableCell>
                <TableCell>Tax Regime</TableCell>
                <TableCell>Basic + DA</TableCell>
                <TableCell>Employee PF</TableCell>
                <TableCell>Employer PF</TableCell>
                <TableCell>Total PF</TableCell>
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
              ) : filteredSalaries.filter(salary => salary.epf_employee > 0).length === 0 ? (
                <TableRow>
                  <TableCell colSpan={9} align="center" sx={{ py: 4 }}>
                    <Typography variant="body1" color="textSecondary">
                      {searchTerm ? 'No PF records found matching your search' : 'No PF records found for the selected period'}
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                filteredSalaries
                  .filter(salary => salary.epf_employee > 0) // Only show employees with PF
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
                      <TableCell>{formatCurrency(salary.basic_salary + salary.da)}</TableCell>
                      <TableCell>
                        <Typography variant="body1" color="primary" fontWeight="bold">
                          {formatCurrency(salary.epf_employee)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body1" color="primary" fontWeight="bold">
                          {formatCurrency(salary.epf_employee || 0)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body1" color="primary" fontWeight="bold">
                          {formatCurrency(salary.epf_employee * 2)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={salary.pf_status?.status || ''}
                          color={getStatusColor(salary.pf_status?.status || '') as any}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Tooltip title="View PF Details">
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

      {/* PF Details Dialog */}
      {renderPFDetailsDialog()}
    </Box>
  );
};

export default PFReport; 