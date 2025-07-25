import React, { useState, useEffect } from 'react';
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
  InputAdornment,
  Card,
  CardContent,
  Skeleton,
  Tooltip,
  IconButton,
  Fade,
  Snackbar,
  Chip,
  TablePagination,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { 
  Search as SearchIcon,
  Refresh as RefreshIcon,
  Visibility as VisibilityIcon,
  ArrowBack as ArrowBackIcon,
  AttachMoney as AttachMoneyIcon,
  Receipt as ReceiptIcon,
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Pending as PendingIcon,
  Download as DownloadIcon,
  Work as WorkIcon,
  Calculate as CalculateIcon,
  AccountBalance as AccountBalanceIcon
} from '@mui/icons-material';
import { getUserRole } from '../../shared/utils/auth';
import { UserRole } from '../../shared/types';

interface ProcessedSalaryRecord {
  id: string;
  employee_id: string;
  employee_name: string;
  department: string;
  month: number;
  year: number;
  tax_year: string;
  basic_salary: number;
  total_earnings: number;
  total_deductions: number;
  net_salary: number;
  one_time_arrear: number;
  one_time_bonus: number;
  computation_mode: 'declared' | 'actual';
  processing_status: 'completed' | 'failed' | 'pending';
  processed_at: string;
  processed_by: string;
  remarks?: string;
  lwp_days?: number;
  lwp_amount?: number;
  gross_salary?: number;
  taxable_salary?: number;
  allowances?: {
    hra?: number;
    da?: number;
    ta?: number;
    other_allowances?: number;
  };
  deductions?: {
    pf?: number;
    tds?: number;
    other_deductions?: number;
  };
}

interface ToastState {
  show: boolean;
  message: string;
  severity: 'success' | 'error' | 'warning' | 'info';
}

// Helper function to get current tax year
const getCurrentTaxYear = (): string => {
  const currentDate = new Date();
  const currentYear = currentDate.getFullYear();
  const currentMonth = currentDate.getMonth() + 1;
  
  if (currentMonth >= 4) {
    return `${currentYear}-${(currentYear + 1).toString().slice(-2)}`;
  } else {
    return `${currentYear - 1}-${currentYear.toString().slice(-2)}`;
  }
};

// Helper function to generate available tax years
const getAvailableTaxYears = (): string[] => {
  const currentTaxYear = getCurrentTaxYear();
  const yearParts = currentTaxYear.split('-');
  const currentStartYear = parseInt(yearParts[0] || '2024');
  const years: string[] = [];
  
  for (let i = 0; i <= 5; i++) {
    const startYear = currentStartYear - i;
    const endYear = startYear + 1;
    years.push(`${startYear}-${endYear.toString().slice(-2)}`);
  }
  
  return years;
};

// Mock data for demonstration - replace with actual API call
const getMockProcessedSalaries = (): ProcessedSalaryRecord[] => {
  return Array.from({ length: 50 }, (_, index) => {
    const month = Math.floor(Math.random() * 12) + 1;
    const year = 2024;
    const basicSalary = 50000 + Math.random() * 100000;
    const totalEarnings = basicSalary * (1 + Math.random() * 0.5);
    const totalDeductions = totalEarnings * (0.1 + Math.random() * 0.2);
    const netSalary = totalEarnings - totalDeductions;
    const oneTimeArrear = Math.random() > 0.7 ? Math.random() * 20000 : 0;
    const oneTimeBonus = Math.random() > 0.7 ? Math.random() * 20000 : 0;
    
    return {
      id: `salary_${index + 1}`,
      employee_id: `EMP${String(index + 1).padStart(3, '0')}`,
      employee_name: `Employee ${index + 1}`,
      department: ['IT', 'HR', 'Finance', 'Marketing', 'Operations', 'Sales', 'Engineering'][Math.floor(Math.random() * 7)] || 'N/A',
      month,
      year,
      tax_year: '2024-25',
      basic_salary: Math.round(basicSalary),
      total_earnings: Math.round(totalEarnings),
      total_deductions: Math.round(totalDeductions),
      net_salary: Math.round(netSalary),
      one_time_arrear: Math.round(oneTimeArrear),
      one_time_bonus: Math.round(oneTimeBonus),
      computation_mode: Math.random() > 0.5 ? 'declared' : 'actual',
      processing_status: ['completed', 'failed', 'pending'][Math.floor(Math.random() * 3)] as 'completed' | 'failed' | 'pending',
      processed_at: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
      processed_by: 'admin',
      ...(Math.random() > 0.8 && { remarks: 'Some processing remarks' }),
      ...(Math.random() > 0.7 && { lwp_days: Math.floor(Math.random() * 5) }),
      ...(Math.random() > 0.7 && { lwp_amount: Math.random() * 5000 }),
      gross_salary: Math.round(totalEarnings + oneTimeArrear + oneTimeBonus),
      taxable_salary: Math.round(totalEarnings - totalDeductions),
      allowances: {
        hra: Math.round(basicSalary * 0.4),
        da: Math.round(basicSalary * 0.1),
        ta: Math.round(basicSalary * 0.05),
        other_allowances: Math.round(basicSalary * 0.15)
      },
      deductions: {
        pf: Math.round(basicSalary * 0.12),
        tds: Math.round(totalEarnings * 0.1),
        other_deductions: Math.round(totalEarnings * 0.05)
      }
    };
  });
};

interface SalaryDetailDialogProps {
  open: boolean;
  onClose: () => void;
  salaryRecord: ProcessedSalaryRecord | null;
}

const SalaryDetailDialog: React.FC<SalaryDetailDialogProps> = ({
  open,
  onClose,
  salaryRecord
}) => {
  if (!salaryRecord) return null;

  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const formatCurrency = (amount: number | undefined): string => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount || 0);
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'failed': return 'error';
      case 'pending': return 'warning';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircleIcon color="success" />;
      case 'failed': return <ErrorIcon color="error" />;
      case 'pending': return <PendingIcon color="warning" />;
      default: return <PendingIcon />;
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <ReceiptIcon color="primary" />
          <Typography variant="h6">
            Salary Details - {salaryRecord.employee_name}
          </Typography>
        </Box>
      </DialogTitle>
      <DialogContent>
        <Grid container spacing={3}>
          {/* Employee Information */}
          <Grid item xs={12}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Employee Information
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Employee ID</Typography>
                    <Typography variant="body1" fontWeight="medium">{salaryRecord.employee_id}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Department</Typography>
                    <Typography variant="body1" fontWeight="medium">{salaryRecord.department}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Processing Period</Typography>
                    <Typography variant="body1" fontWeight="medium">
                      {months[salaryRecord.month - 1]} {salaryRecord.year}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Tax Year</Typography>
                    <Typography variant="body1" fontWeight="medium">{salaryRecord.tax_year}</Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Salary Breakdown */}
          <Grid item xs={12}>
            <Accordion defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <AttachMoneyIcon color="primary" />
                  <Typography variant="h6">Salary Breakdown</Typography>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2" color="text.secondary">Basic Salary</Typography>
                    <Typography variant="h6" color="primary">{formatCurrency(salaryRecord.basic_salary)}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2" color="text.secondary">Total Earnings</Typography>
                    <Typography variant="h6" color="success.main">{formatCurrency(salaryRecord.total_earnings)}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2" color="text.secondary">Total Deductions</Typography>
                    <Typography variant="h6" color="error.main">{formatCurrency(salaryRecord.total_deductions)}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2" color="text.secondary">Net Salary</Typography>
                    <Typography variant="h6" fontWeight="bold">{formatCurrency(salaryRecord.net_salary)}</Typography>
                  </Grid>
                  {salaryRecord.one_time_arrear > 0 && (
                    <Grid item xs={12} sm={6}>
                      <Typography variant="subtitle2" color="text.secondary">Arrears</Typography>
                      <Typography variant="h6" color="warning.main">{formatCurrency(salaryRecord.one_time_arrear)}</Typography>
                    </Grid>
                  )}
                  {salaryRecord.one_time_bonus > 0 && (
                    <Grid item xs={12} sm={6}>
                      <Typography variant="subtitle2" color="text.secondary">Bonus</Typography>
                      <Typography variant="h6" color="warning.main">{formatCurrency(salaryRecord.one_time_bonus)}</Typography>
                    </Grid>
                  )}
                  {salaryRecord.lwp_days && salaryRecord.lwp_days > 0 && (
                    <Grid item xs={12} sm={6}>
                      <Typography variant="subtitle2" color="text.secondary">LWP Days</Typography>
                      <Typography variant="h6" color="error.main">{salaryRecord.lwp_days} days</Typography>
                    </Grid>
                  )}
                  {salaryRecord.lwp_amount && salaryRecord.lwp_amount > 0 && (
                    <Grid item xs={12} sm={6}>
                      <Typography variant="subtitle2" color="text.secondary">LWP Amount</Typography>
                      <Typography variant="h6" color="error.main">{formatCurrency(salaryRecord.lwp_amount)}</Typography>
                    </Grid>
                  )}
                </Grid>
              </AccordionDetails>
            </Accordion>
          </Grid>

          {/* Allowances Breakdown */}
          {salaryRecord.allowances && (
            <Grid item xs={12}>
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <AccountBalanceIcon color="primary" />
                    <Typography variant="h6">Allowances Breakdown</Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="subtitle2" color="text.secondary">HRA</Typography>
                      <Typography variant="h6" color="success.main">{formatCurrency(salaryRecord.allowances.hra)}</Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="subtitle2" color="text.secondary">Dearness Allowance</Typography>
                      <Typography variant="h6" color="success.main">{formatCurrency(salaryRecord.allowances.da)}</Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="subtitle2" color="text.secondary">Transport Allowance</Typography>
                      <Typography variant="h6" color="success.main">{formatCurrency(salaryRecord.allowances.ta)}</Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="subtitle2" color="text.secondary">Other Allowances</Typography>
                      <Typography variant="h6" color="success.main">{formatCurrency(salaryRecord.allowances.other_allowances)}</Typography>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            </Grid>
          )}

          {/* Deductions Breakdown */}
          {salaryRecord.deductions && (
            <Grid item xs={12}>
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <WorkIcon color="primary" />
                    <Typography variant="h6">Deductions Breakdown</Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="subtitle2" color="text.secondary">Provident Fund</Typography>
                      <Typography variant="h6" color="error.main">{formatCurrency(salaryRecord.deductions.pf)}</Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="subtitle2" color="text.secondary">TDS</Typography>
                      <Typography variant="h6" color="error.main">{formatCurrency(salaryRecord.deductions.tds)}</Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="subtitle2" color="text.secondary">Other Deductions</Typography>
                      <Typography variant="h6" color="error.main">{formatCurrency(salaryRecord.deductions.other_deductions)}</Typography>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            </Grid>
          )}

          {/* Processing Information */}
          <Grid item xs={12}>
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CalculateIcon color="primary" />
                  <Typography variant="h6">Processing Information</Typography>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2" color="text.secondary">Computation Mode</Typography>
                    <Chip 
                      label={salaryRecord.computation_mode === 'declared' ? 'Declared Values' : 'Actual Proof'} 
                      color={salaryRecord.computation_mode === 'declared' ? 'primary' : 'secondary'}
                      size="small"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2" color="text.secondary">Processing Status</Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {getStatusIcon(salaryRecord.processing_status)}
                      <Chip 
                        label={salaryRecord.processing_status} 
                        color={getStatusColor(salaryRecord.processing_status) as any}
                        size="small"
                      />
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2" color="text.secondary">Processed At</Typography>
                    <Typography variant="body2">{formatDate(salaryRecord.processed_at)}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2" color="text.secondary">Processed By</Typography>
                    <Typography variant="body2">{salaryRecord.processed_by}</Typography>
                  </Grid>
                  {salaryRecord.remarks && (
                    <Grid item xs={12}>
                      <Typography variant="subtitle2" color="text.secondary">Remarks</Typography>
                      <Typography variant="body2">{salaryRecord.remarks}</Typography>
                    </Grid>
                  )}
                </Grid>
              </AccordionDetails>
            </Accordion>
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
        <Button 
          variant="contained" 
          startIcon={<DownloadIcon />}
          onClick={() => {
            // TODO: Implement download functionality
            console.log('Download salary details');
          }}
        >
          Download
        </Button>
      </DialogActions>
    </Dialog>
  );
};

/**
 * SalaryProcessing Component - Comprehensive salary processing management
 */
const SalaryProcessing: React.FC = () => {
  const [filteredSalaries, setFilteredSalaries] = useState<ProcessedSalaryRecord[]>([]);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedTaxYear, setSelectedTaxYear] = useState<string>(getCurrentTaxYear());
  const [selectedMonth, setSelectedMonth] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [selectedDepartment, setSelectedDepartment] = useState<string>('all');
  const [page, setPage] = useState<number>(0);
  const [rowsPerPage, setRowsPerPage] = useState<number>(10);
  const [toast, setToast] = useState<ToastState>({ 
    show: false, 
    message: '', 
    severity: 'success' 
  });
  const [detailDialogOpen, setDetailDialogOpen] = useState<boolean>(false);
  const [selectedSalaryRecord, setSelectedSalaryRecord] = useState<ProcessedSalaryRecord | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  
  const navigate = useNavigate();
  const userRole: UserRole | null = getUserRole();
  
  // Check if selected year is current year
  const isCurrentYear = selectedTaxYear === getCurrentTaxYear();
  const availableTaxYears = getAvailableTaxYears();
  
  // Mock data - replace with actual API call
  const [salaryRecords, setSalaryRecords] = useState<ProcessedSalaryRecord[]>([]);
  
  // Load salary records
  useEffect(() => {
    const loadSalaryRecords = async () => {
      setLoading(true);
      try {
        // TODO: Replace with actual API call
        // const response = await salaryProcessingApi.getProcessedSalaries({
        //   tax_year: selectedTaxYear,
        //   month: selectedMonth !== 'all' ? parseInt(selectedMonth) : undefined
        // });
        // setSalaryRecords(response.data);
        
        // Mock data for now
        await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API delay
        const mockData = getMockProcessedSalaries();
        setSalaryRecords(mockData);
        showToast(`Loaded ${mockData.length} salary records for ${selectedTaxYear}`, 'success');
      } catch (error: any) {
        let backendMessage: string | undefined;
        if (error && typeof error === 'object' && 'response' in error) {
          backendMessage = (error as any).response?.data?.detail;
        }
        showToast(backendMessage || 'Failed to load salary records', 'error');
      } finally {
        setLoading(false);
      }
    };

    loadSalaryRecords();
  }, [selectedTaxYear, selectedMonth]);

  // Helper functions
  const showToast = (message: string, severity: ToastState['severity'] = 'success'): void => {
    setToast({ show: true, message, severity });
  };

  const closeToast = (): void => {
    setToast(prev => ({ ...prev, show: false }));
  };

  // Redirect non-admin users
  useEffect(() => {
    if (userRole !== 'admin' && userRole !== 'superadmin') {
      navigate(`/taxation`);
    }
  }, [userRole, navigate]);

  // Handle search and filtering
  useEffect(() => {
    let filtered = salaryRecords;

    // Filter by search term
    if (searchTerm.trim() !== '') {
      const searchTermLower = searchTerm.toLowerCase();
      filtered = filtered.filter(record => 
        record.employee_id.toLowerCase().includes(searchTermLower) || 
        record.employee_name.toLowerCase().includes(searchTermLower) ||
        record.department.toLowerCase().includes(searchTermLower)
      );
    }

    // Filter by status
    if (selectedStatus !== 'all') {
      filtered = filtered.filter(record => record.processing_status === selectedStatus);
    }

    // Filter by department
    if (selectedDepartment !== 'all') {
      filtered = filtered.filter(record => record.department === selectedDepartment);
    }

    setFilteredSalaries(filtered);
    setPage(0); // Reset to first page when filtering
  }, [searchTerm, selectedStatus, selectedDepartment, salaryRecords]);

  // Event handlers
  const handleViewDetails = (record: ProcessedSalaryRecord): void => {
    setSelectedSalaryRecord(record);
    setDetailDialogOpen(true);
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setSearchTerm(event.target.value);
  };

  const handleTaxYearChange = (event: SelectChangeEvent<string>): void => {
    const newTaxYear = event.target.value;
    setSelectedTaxYear(newTaxYear);
    setSearchTerm(''); // Clear search when changing year
    setPage(0); // Reset pagination
  };

  const handleMonthChange = (event: SelectChangeEvent<string>): void => {
    setSelectedMonth(event.target.value);
    setPage(0);
  };

  const handleStatusChange = (event: SelectChangeEvent<string>): void => {
    setSelectedStatus(event.target.value);
    setPage(0);
  };

  const handleDepartmentChange = (event: SelectChangeEvent<string>): void => {
    setSelectedDepartment(event.target.value);
    setPage(0);
  };

  const handlePageChange = (_event: unknown, newPage: number): void => {
    setPage(newPage);
  };

  const handleRowsPerPageChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleRefresh = async (): Promise<void> => {
    try {
      setLoading(true);
      // TODO: Replace with actual API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      const mockData = getMockProcessedSalaries();
      setSalaryRecords(mockData);
      showToast(`Salary records refreshed for ${selectedTaxYear}`, 'success');
    } catch (error: any) {
      let backendMessage: string | undefined;
      if (error && typeof error === 'object' && 'response' in error) {
        backendMessage = (error as any).response?.data?.detail;
      }
      showToast(backendMessage || 'Failed to refresh salary records', 'error');
    } finally {
      setLoading(false);
    }
  };

  // Format currency
  const formatCurrency = (amount: number | undefined): string => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount || 0);
  };

  // Helper function to get status chip
  const renderStatusChip = (status: string): React.ReactElement => {
    const getStatusProps = (status: string) => {
      switch (status) {
        case 'completed': return { color: 'success' as const, label: 'Completed' };
        case 'failed': return { color: 'error' as const, label: 'Failed' };
        case 'pending': return { color: 'warning' as const, label: 'Pending' };
        default: return { color: 'default' as const, label: 'Unknown' };
      }
    };

    const { color, label } = getStatusProps(status);
    return (
      <Chip
        label={label}
        color={color}
        size="small"
        variant="outlined"
      />
    );
  };

  // Helper function to get computation mode chip
  const renderComputationModeChip = (mode: string): React.ReactElement => {
    const isDeclared = mode === 'declared';
    return (
      <Chip
        label={isDeclared ? 'Declared' : 'Actual'}
        color={isDeclared ? 'primary' : 'secondary'}
        size="small"
        variant="outlined"
      />
    );
  };

  // Render table skeleton
  const renderTableSkeleton = (): React.ReactElement[] => (
    Array.from({ length: rowsPerPage }).map((_, index) => (
      <TableRow key={index}>
        <TableCell><Skeleton /></TableCell>
        <TableCell><Skeleton /></TableCell>
        <TableCell><Skeleton /></TableCell>
        <TableCell><Skeleton /></TableCell>
        <TableCell><Skeleton /></TableCell>
        <TableCell><Skeleton /></TableCell>
        <TableCell><Skeleton /></TableCell>
        <TableCell><Skeleton /></TableCell>
        <TableCell><Skeleton width={120} /></TableCell>
      </TableRow>
    ))
  );

  // Render empty state
  const renderEmptyState = (): React.ReactElement => (
    <TableRow>
      <TableCell colSpan={9} align="center" sx={{ py: 6 }}>
        <Box sx={{ textAlign: 'center' }}>
          <ReceiptIcon 
            sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} 
          />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            {searchTerm ? 'No salary records found' : `No salary records for ${selectedTaxYear}`}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {searchTerm 
              ? `No salary records match "${searchTerm}" for ${selectedTaxYear}`
              : `No processed salary records available for ${selectedTaxYear}`
            }
          </Typography>
        </Box>
      </TableCell>
    </TableRow>
  );

  // Get paginated data
  const paginatedSalaries = filteredSalaries.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  const months = [
    { value: 'all', label: 'All Months' },
    { value: '1', label: 'January' },
    { value: '2', label: 'February' },
    { value: '3', label: 'March' },
    { value: '4', label: 'April' },
    { value: '5', label: 'May' },
    { value: '6', label: 'June' },
    { value: '7', label: 'July' },
    { value: '8', label: 'August' },
    { value: '9', label: 'September' },
    { value: '10', label: 'October' },
    { value: '11', label: 'November' },
    { value: '12', label: 'December' }
  ];

  const statusOptions = [
    { value: 'all', label: 'All Status' },
    { value: 'completed', label: 'Completed' },
    { value: 'failed', label: 'Failed' },
    { value: 'pending', label: 'Pending' }
  ];

  const departmentOptions = [
    { value: 'all', label: 'All Departments' },
    { value: 'IT', label: 'IT' },
    { value: 'HR', label: 'HR' },
    { value: 'Finance', label: 'Finance' },
    { value: 'Marketing', label: 'Marketing' },
    { value: 'Operations', label: 'Operations' },
    { value: 'Sales', label: 'Sales' },
    { value: 'Engineering', label: 'Engineering' }
  ];

  if (loading && salaryRecords.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '70vh' }}>
        <CircularProgress size={40} />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header Card */}
      <Card elevation={1} sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
            <Box>
              <Typography variant="h5" component="h1" gutterBottom>
                Salary Processing Management
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Comprehensive salary processing and management system - {selectedTaxYear}
                {!isCurrentYear && (
                  <Chip 
                    label="Previous Year - Read Only" 
                    color="warning" 
                    size="small" 
                    sx={{ ml: 1 }} 
                  />
                )}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
              <FormControl size="small" sx={{ minWidth: 140 }}>
                <InputLabel>Tax Year</InputLabel>
                <Select
                  value={selectedTaxYear}
                  label="Tax Year"
                  onChange={handleTaxYearChange}
                >
                  {availableTaxYears.map((year) => (
                    <MenuItem key={year} value={year}>
                      {year}
                      {year === getCurrentTaxYear() && ' (Current)'}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <Tooltip title="Refresh">
                <IconButton 
                  onClick={handleRefresh}
                  disabled={loading}
                  color="primary"
                >
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
              <Button 
                variant="outlined" 
                startIcon={<ArrowBackIcon />}
                onClick={() => navigate('/taxation')}
              >
                BACK TO DASHBOARD
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Search and Filters */}
      <Paper elevation={1} sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={3}>
            <TextField
              fullWidth
              label="Search records"
              variant="outlined"
              size="small"
              value={searchTerm}
              onChange={handleSearchChange}
              placeholder="Search by Employee ID or Name..."
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon color="action" />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} sm={2}>
            <FormControl fullWidth size="small">
              <InputLabel>Month</InputLabel>
              <Select
                value={selectedMonth}
                label="Month"
                onChange={handleMonthChange}
              >
                {months.map((month) => (
                  <MenuItem key={month.value} value={month.value}>
                    {month.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={2}>
            <FormControl fullWidth size="small">
              <InputLabel>Status</InputLabel>
              <Select
                value={selectedStatus}
                label="Status"
                onChange={handleStatusChange}
              >
                {statusOptions.map((status) => (
                  <MenuItem key={status.value} value={status.value}>
                    {status.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={2}>
            <FormControl fullWidth size="small">
              <InputLabel>Department</InputLabel>
              <Select
                value={selectedDepartment}
                label="Department"
                onChange={handleDepartmentChange}
              >
                {departmentOptions.map((dept) => (
                  <MenuItem key={dept.value} value={dept.value}>
                    {dept.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={3}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="body2" color="text.secondary">
                {filteredSalaries.length} record{filteredSalaries.length !== 1 ? 's' : ''} for {selectedTaxYear}
              </Typography>
              {loading && <CircularProgress size={16} />}
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Table */}
      <Paper elevation={1}>
        <TableContainer>
          <Table stickyHeader>
            <TableHead>
              <TableRow sx={{ 
                '& .MuiTableCell-head': { 
                  backgroundColor: 'primary.main',
                  color: 'white',
                  fontWeight: 'bold',
                  fontSize: '0.875rem'
                }
              }}>
                <TableCell>Employee</TableCell>
                <TableCell>Department</TableCell>
                <TableCell>Period</TableCell>
                <TableCell>Basic Salary</TableCell>
                <TableCell>Net Salary</TableCell>
                <TableCell>Arrears</TableCell>
                <TableCell>Mode</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                renderTableSkeleton()
              ) : paginatedSalaries.length > 0 ? (
                paginatedSalaries.map((record) => (
                  <Fade in key={record.id} timeout={300}>
                    <TableRow 
                      hover
                      sx={{ 
                        '&:hover': { 
                          backgroundColor: 'action.hover' 
                        }
                      }}
                    >
                      <TableCell>
                        <Box>
                          <Typography variant="subtitle2" fontWeight="medium">
                            {record.employee_name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {record.employee_id}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={record.department} 
                          size="small" 
                          variant="outlined"
                          color="default"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {new Date(record.year, record.month - 1).toLocaleDateString('en-IN', { 
                            month: 'short', 
                            year: 'numeric' 
                          })}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium">
                          {formatCurrency(record.basic_salary)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium" color="success.main">
                          {formatCurrency(record.net_salary)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        {record.one_time_arrear > 0 ? (
                          <Typography variant="body2" color="warning.main" fontWeight="medium">
                            {formatCurrency(record.one_time_arrear)}
                          </Typography>
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            -
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        {renderComputationModeChip(record.computation_mode)}
                      </TableCell>
                      <TableCell>
                        {renderStatusChip(record.processing_status)}
                      </TableCell>
                      <TableCell align="center">
                        <Tooltip title="View Details">
                          <IconButton
                            size="small"
                            color="primary"
                            onClick={() => handleViewDetails(record)}
                          >
                            <VisibilityIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  </Fade>
                ))
              ) : (
                renderEmptyState()
              )}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Pagination */}
        {filteredSalaries.length > 0 && (
          <TablePagination
            component="div"
            count={filteredSalaries.length}
            page={page}
            onPageChange={handlePageChange}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={handleRowsPerPageChange}
            rowsPerPageOptions={[5, 10, 25, 50]}
            showFirstButton
            showLastButton
          />
        )}
      </Paper>

      {/* Salary Detail Dialog */}
      <SalaryDetailDialog
        open={detailDialogOpen}
        onClose={() => setDetailDialogOpen(false)}
        salaryRecord={selectedSalaryRecord}
      />

      {/* Toast Notifications */}
      <Snackbar
        open={toast.show}
        autoHideDuration={6000}
        onClose={closeToast}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={closeToast} 
          severity={toast.severity}
          sx={{ width: '100%' }}
          variant="filled"
        >
          {toast.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default SalaryProcessing; 