import React, { useState, useEffect, useMemo } from 'react';
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
  Checkbox,
  FormControlLabel,
  Divider,
  List,
  ListItem
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { 
  Search as SearchIcon,
  Refresh as RefreshIcon,
  Person as PersonIcon,
  Visibility as VisibilityIcon,
  ArrowBack as ArrowBackIcon,
  Settings as SettingsIcon,
  AccountBalance as AccountBalanceIcon,
  AddCircle as AddCircleIcon,
  Receipt as ReceiptIcon,
  Home as HomeIcon,
  TrendingUp as TrendingUpIcon,
  Work as WorkIcon,
  CarRental as CarRentalIcon,
  Business as BusinessIcon,
  Calculate as CalculateIcon,
  Functions as FunctionsIcon,
  AttachMoney as AttachMoneyIcon,
  PlaylistAddCheck as PlaylistAddCheckIcon,
  Group as GroupIcon,
  AccountBalanceWallet as AccountBalanceWalletIcon
} from '@mui/icons-material';
import { getUserRole } from '../../shared/utils/auth';
import { UserRole } from '../../shared/types';
import { EmployeeSelectionDTO, EmployeeSelectionQuery, FilingStatus } from '../../shared/types/api';
import { useEmployeeSelection, useRefreshEmployeeSelection } from '../../shared/hooks/useEmployeeSelection';
import taxationApi from '../../shared/api/taxationApi';
import { salaryProcessingApi } from '../../shared/api/salaryProcessingApi';

interface EmployeeRecord extends EmployeeSelectionDTO {
  // Additional fields if needed
}

interface ToastState {
  show: boolean;
  message: string;
  severity: 'success' | 'error' | 'warning' | 'info';
}

interface ComponentOption {
  id: string;
  name: string;
  description: string;
  icon: React.ReactElement;
  color: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info';
  path: string;
}

interface MonthlySalaryComputeDialogProps {
  open: boolean;
  onClose: () => void;
  employee: EmployeeRecord | null;
  taxYear: string;
  onCompute: (request: {
    employee_id: string;
    month: number;
    year: number;
    tax_year: string;
    arrears?: number | undefined;
    bonus?: number | undefined;
    use_declared_values: boolean;
  }) => Promise<void>;
}

interface BulkSalaryProcessingDialogProps {
  open: boolean;
  onClose: () => void;
  employees: EmployeeRecord[];
  taxYear: string;
  onBulkCompute: (requests: {
    employee_id: string;
    month: number;
    year: number;
    tax_year: string;
    arrears?: number | undefined;
    bonus?: number | undefined;
    use_declared_values: boolean;
  }[]) => Promise<void>;
}

interface LoanProcessingDialogProps {
  open: boolean;
  onClose: () => void;
  employee: EmployeeRecord | null;
  taxYear: string;
  onProcessLoan: (employeeId: string, taxYear: string) => Promise<any>;
}

interface EmployeeProcessingConfig {
  employee_id: string;
  selected: boolean;
  arrears: number;
  bonus: number;
  use_declared_values: boolean;
}

// Helper function to get current tax year
const getCurrentTaxYear = (): string => {
  const currentDate = new Date();
  const currentYear = currentDate.getFullYear();
  const currentMonth = currentDate.getMonth() + 1; // getMonth() returns 0-11
  
  // Tax year starts from April 1st
  if (currentMonth >= 4) {
    return `${currentYear}-${(currentYear + 1).toString().slice(-2)}`;
  } else {
    return `${currentYear - 1}-${currentYear.toString().slice(-2)}`;
  }
};

// Helper function to generate available tax years (current + last 5 years)
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

// Component options for individual management
const getComponentOptions = (): ComponentOption[] => [
  {
    id: 'salary-update',
    name: 'Update Current Salary',
    description: 'Modify existing salary components and allowances',
    icon: <AccountBalanceIcon />,
    color: 'primary',
    path: '/taxation/component/salary'
  },
  {
    id: 'salary-new',
    name: 'Add New Salary Revision',
    description: 'Define new salary structure with increments',
    icon: <AddCircleIcon />,
    color: 'success',
    path: '/taxation/component/salary/new'
  },
  {
    id: 'perquisites',
    name: 'Perquisites',
    description: 'Accommodation, car, medical, LTA, ESOP benefits',
    icon: <CarRentalIcon />,
    color: 'secondary',
    path: '/taxation/component/perquisites'
  },
  {
    id: 'deductions',
    name: 'Deductions',
    description: 'Section 80C, 80D, 80G, 80E, 80TTA investments',
    icon: <ReceiptIcon />,
    color: 'info',
    path: '/taxation/component/deductions'
  },
  {
    id: 'house-property',
    name: 'House Property',
    description: 'Rental income, home loan interest, municipal taxes',
    icon: <HomeIcon />,
    color: 'warning',
    path: '/taxation/component/house-property'
  },
  {
    id: 'capital-gains',
    name: 'Capital Gains',
    description: 'STCG, LTCG on equity, debt, real estate',
    icon: <TrendingUpIcon />,
    color: 'info',
    path: '/taxation/component/capital-gains'
  },
  {
    id: 'retirement-benefits',
    name: 'Retirement Benefits',
    description: 'Gratuity, leave encashment, VRS, pension',
    icon: <WorkIcon />,
    color: 'primary',
    path: '/taxation/component/retirement-benefits'
  },
  {
    id: 'other-income',
    name: 'Other Income',
    description: 'Interest income, dividends, gifts, business income',
    icon: <BusinessIcon />,
    color: 'secondary',
    path: '/taxation/component/other-income'
  },
  {
    id: 'monthly-payroll',
    name: 'Monthly Payroll',
    description: 'Monthly salary projections with LWP calculations',
    icon: <CalculateIcon />,
    color: 'success',
    path: '/taxation/component/monthly-payroll'
  },
  {
    id: 'regime',
    name: 'Tax Regime',
    description: 'Old vs New regime selection and age',
    icon: <SettingsIcon />,
    color: 'warning',
    path: '/taxation/component/regime'
  }
];

const MonthlySalaryComputeDialog: React.FC<MonthlySalaryComputeDialogProps> = ({
  open,
  onClose,
  employee,
  taxYear,
  onCompute
}) => {
  const [month, setMonth] = useState<number>(new Date().getMonth() + 1);
  const [year, setYear] = useState<number>(new Date().getFullYear());
  const [arrears, setArrears] = useState<number>(0);
  const [bonus, setBonus] = useState<number>(0);
  const [useDeclaredValues, setUseDeclaredValues] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const months = [
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

  const years = Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - 2 + i);

  const handleCompute = async () => {
    if (!employee) return;

    try {
      setLoading(true);
      setError(null);

      const request: {
        employee_id: string;
        month: number;
        year: number;
        tax_year: string;
        arrears?: number | undefined;
        bonus?: number | undefined;
        use_declared_values: boolean;
      } = {
        employee_id: employee.employee_id,
        month,
        year,
        tax_year: taxYear,
        use_declared_values: useDeclaredValues
      };
      
      if (arrears > 0) {
        request.arrears = arrears;
      }
      if (bonus > 0) {
        request.bonus = bonus;
      }
      
      await onCompute(request);

      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to compute monthly salary');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      onClose();
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <AttachMoneyIcon color="primary" />
          <Typography variant="h6">
            Compute Monthly Salary
          </Typography>
        </Box>
      </DialogTitle>
      <DialogContent>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Compute monthly salary for {employee?.user_name || employee?.employee_id} for {taxYear}
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={6}>
            <FormControl fullWidth>
              <InputLabel>Month</InputLabel>
              <Select
                value={month}
                label="Month"
                onChange={(e) => setMonth(e.target.value as number)}
              >
                {months.map((m) => (
                  <MenuItem key={m.value} value={m.value}>
                    {m.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={6}>
            <FormControl fullWidth>
              <InputLabel>Year</InputLabel>
              <Select
                value={year}
                label="Year"
                onChange={(e) => setYear(e.target.value as number)}
              >
                {years.map((y) => (
                  <MenuItem key={y} value={y}>
                    {y}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Arrears (if any)"
              type="number"
              value={arrears}
              onChange={(e) => setArrears(parseFloat(e.target.value) || 0)}
              InputProps={{
                startAdornment: <InputAdornment position="start">₹</InputAdornment>,
              }}
              helperText="Enter any arrears amount for this month"
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Bonus (if any)"
              type="number"
              value={bonus}
              onChange={(e) => setBonus(parseFloat(e.target.value) || 0)}
              InputProps={{
                startAdornment: <InputAdornment position="start">₹</InputAdornment>,
              }}
              helperText="Enter any bonus amount for this month"
            />
          </Grid>
          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>Computation Mode</InputLabel>
              <Select
                value={useDeclaredValues ? 'declared' : 'actual'}
                label="Computation Mode"
                onChange={(e) => setUseDeclaredValues(e.target.value === 'declared')}
              >
                <MenuItem value="declared">Use Declared Values</MenuItem>
                <MenuItem value="actual">Use Actual Proof Submission</MenuItem>
              </Select>
            </FormControl>
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
              {useDeclaredValues 
                ? 'Compute based on declared salary components and allowances'
                : 'Compute based on actual proof submissions and verified documents'
              }
            </Typography>
          </Grid>
        </Grid>

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={loading}>
          Cancel
        </Button>
        <Button 
          onClick={handleCompute} 
          variant="contained" 
          disabled={loading}
          startIcon={loading ? <CircularProgress size={16} /> : <CalculateIcon />}
        >
          {loading ? 'Computing...' : 'Compute Salary'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

const BulkSalaryProcessingDialog: React.FC<BulkSalaryProcessingDialogProps> = ({
  open,
  onClose,
  employees,
  taxYear,
  onBulkCompute
}) => {
  const [employeeConfigs, setEmployeeConfigs] = useState<Map<string, EmployeeProcessingConfig>>(new Map());
  const [month, setMonth] = useState<number>(new Date().getMonth() + 1);
  const [year, setYear] = useState<number>(new Date().getFullYear());
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [selectAll, setSelectAll] = useState<boolean>(false);

  const months = [
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

  const years = Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - 2 + i);

  // Initialize employee configurations when dialog opens
  useEffect(() => {
    if (open) {
      const configs = new Map<string, EmployeeProcessingConfig>();
      employees.forEach(emp => {
        configs.set(emp.employee_id, {
          employee_id: emp.employee_id,
          selected: false,
          arrears: 0,
          bonus: 0,
          use_declared_values: true
        });
      });
      setEmployeeConfigs(configs);
      setSelectAll(false);
      setError(null);
    }
  }, [open, employees]);

  // Handle select all toggle
  const handleSelectAll = (checked: boolean) => {
    setSelectAll(checked);
    const newConfigs = new Map(employeeConfigs);
    employees.forEach(emp => {
      const config = newConfigs.get(emp.employee_id);
      if (config) {
        config.selected = checked;
        newConfigs.set(emp.employee_id, config);
      }
    });
    setEmployeeConfigs(newConfigs);
  };

  // Handle individual employee selection
  const handleEmployeeSelect = (employeeId: string, checked: boolean) => {
    const newConfigs = new Map(employeeConfigs);
    const config = newConfigs.get(employeeId);
    if (config) {
      config.selected = checked;
      newConfigs.set(employeeId, config);
      setEmployeeConfigs(newConfigs);
      
      // Update select all state
      const selectedCount = Array.from(newConfigs.values()).filter(c => c.selected).length;
      setSelectAll(selectedCount === employees.length);
    }
  };

  // Handle arrears change for specific employee
  const handleArrearsChange = (employeeId: string, value: number) => {
    const newConfigs = new Map(employeeConfigs);
    const config = newConfigs.get(employeeId);
    if (config) {
      config.arrears = value;
      newConfigs.set(employeeId, config);
      setEmployeeConfigs(newConfigs);
    }
  };

  // Handle bonus change for specific employee
  const handleBonusChange = (employeeId: string, value: number) => {
    const newConfigs = new Map(employeeConfigs);
    const config = newConfigs.get(employeeId);
    if (config) {
      config.bonus = value;
      newConfigs.set(employeeId, config);
      setEmployeeConfigs(newConfigs);
    }
  };

  // Handle computation mode change for specific employee
  const handleComputationModeChange = (employeeId: string, useDeclaredValues: boolean) => {
    const newConfigs = new Map(employeeConfigs);
    const config = newConfigs.get(employeeId);
    if (config) {
      config.use_declared_values = useDeclaredValues;
      newConfigs.set(employeeId, config);
      setEmployeeConfigs(newConfigs);
    }
  };

  const handleBulkCompute = async () => {
    const selectedConfigs = Array.from(employeeConfigs.values()).filter(config => config.selected);
    
    if (selectedConfigs.length === 0) {
      setError('Please select at least one employee');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const requests = selectedConfigs.map(config => {
        const req: {
          employee_id: string;
          month: number;
          year: number;
          tax_year: string;
          arrears?: number | undefined;
          bonus?: number | undefined;
          use_declared_values: boolean;
        } = {
          employee_id: config.employee_id,
          month,
          year,
          tax_year: taxYear,
          use_declared_values: config.use_declared_values,
        };
        if (config.arrears > 0) {
          req.arrears = config.arrears;
        }
        if (config.bonus > 0) {
          req.bonus = config.bonus;
        }
        return req;
      });

      await onBulkCompute(requests);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process bulk salary computation');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      onClose();
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <GroupIcon color="primary" />
          <Typography variant="h6">
            Bulk Salary Processing
          </Typography>
        </Box>
      </DialogTitle>
      <DialogContent>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Process monthly salary for multiple employees for {taxYear}
        </Typography>

        {/* Global Settings */}
        <Card variant="outlined" sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="subtitle1" fontWeight="medium" gutterBottom>
              Processing Period
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={6}>
                <FormControl fullWidth>
                  <InputLabel>Month</InputLabel>
                  <Select
                    value={month}
                    label="Month"
                    onChange={(e) => setMonth(e.target.value as number)}
                  >
                    {months.map((m) => (
                      <MenuItem key={m.value} value={m.value}>
                        {m.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={6}>
                <FormControl fullWidth>
                  <InputLabel>Year</InputLabel>
                  <Select
                    value={year}
                    label="Year"
                    onChange={(e) => setYear(e.target.value as number)}
                  >
                    {years.map((y) => (
                      <MenuItem key={y} value={y}>
                        {y}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Employee Selection with Individual Settings */}
        <Card variant="outlined">
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="subtitle1" fontWeight="medium">
                Employee Configuration ({Array.from(employeeConfigs.values()).filter(c => c.selected).length} of {employees.length})
              </Typography>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={selectAll}
                    onChange={(e) => handleSelectAll(e.target.checked)}
                    indeterminate={Array.from(employeeConfigs.values()).filter(c => c.selected).length > 0 && Array.from(employeeConfigs.values()).filter(c => c.selected).length < employees.length}
                  />
                }
                label="Select All"
              />
            </Box>
            
            <Divider sx={{ mb: 2 }} />
            
            <List sx={{ maxHeight: 400, overflow: 'auto' }}>
              {employees.map((employee) => {
                const config = employeeConfigs.get(employee.employee_id);
                if (!config) return null;
                
                return (
                  <ListItem key={employee.employee_id} sx={{ flexDirection: 'column', alignItems: 'stretch', py: 2 }}>
                    {/* Employee Header */}
                    <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', mb: 2 }}>
                      <Checkbox
                        checked={config.selected}
                        onChange={(e) => handleEmployeeSelect(employee.employee_id, e.target.checked)}
                      />
                      <Box sx={{ flexGrow: 1, ml: 1 }}>
                        <Typography variant="subtitle2" fontWeight="medium">
                          {employee.user_name || employee.employee_id}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {employee.employee_id} • {employee.department || 'N/A'}
                        </Typography>
                      </Box>
                      <Chip
                        label={employee.filing_status || 'pending'}
                        size="small"
                        color={employee.filing_status === 'filed' ? 'success' : 'default'}
                        variant="outlined"
                      />
                    </Box>
                    
                    {/* Employee Configuration */}
                    {config.selected && (
                      <Box sx={{ ml: 4, mt: 1 }}>
                        <Grid container spacing={2}>
                          <Grid item xs={12} sm={6}>
                            <TextField
                              fullWidth
                              size="small"
                              label="Arrears (₹)"
                              type="number"
                              value={config.arrears}
                              onChange={(e) => handleArrearsChange(employee.employee_id, parseFloat(e.target.value) || 0)}
                              InputProps={{
                                startAdornment: <InputAdornment position="start">₹</InputAdornment>,
                              }}
                              helperText="Enter arrears amount if any"
                            />
                          </Grid>
                          <Grid item xs={12} sm={6}>
                            <TextField
                              fullWidth
                              size="small"
                              label="Bonus (₹)"
                              type="number"
                              value={config.bonus}
                              onChange={(e) => handleBonusChange(employee.employee_id, parseFloat(e.target.value) || 0)}
                              InputProps={{
                                startAdornment: <InputAdornment position="start">₹</InputAdornment>,
                              }}
                              helperText="Enter bonus amount if any"
                            />
                          </Grid>
                          <Grid item xs={12} sm={6}>
                            <FormControl fullWidth size="small">
                              <InputLabel>Computation Mode</InputLabel>
                              <Select
                                value={config.use_declared_values ? 'declared' : 'actual'}
                                label="Computation Mode"
                                onChange={(e) => handleComputationModeChange(employee.employee_id, e.target.value === 'declared')}
                              >
                                <MenuItem value="declared">Use Declared Values</MenuItem>
                                <MenuItem value="actual">Use Actual Proof Submission</MenuItem>
                              </Select>
                            </FormControl>
                            <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                              {config.use_declared_values 
                                ? 'Based on declared components'
                                : 'Based on actual proof submissions'
                              }
                            </Typography>
                          </Grid>
                        </Grid>
                      </Box>
                    )}
                  </ListItem>
                );
              })}
            </List>
          </CardContent>
        </Card>

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={loading}>
          Cancel
        </Button>
        <Button 
          onClick={handleBulkCompute} 
          variant="contained" 
          disabled={loading || Array.from(employeeConfigs.values()).filter(c => c.selected).length === 0}
          startIcon={loading ? <CircularProgress size={16} /> : <PlaylistAddCheckIcon />}
        >
          {loading ? 'Processing...' : `Process ${Array.from(employeeConfigs.values()).filter(c => c.selected).length} Employee${Array.from(employeeConfigs.values()).filter(c => c.selected).length !== 1 ? 's' : ''}`}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

const LoanProcessingDialog: React.FC<LoanProcessingDialogProps> = ({
  open,
  onClose,
  employee,
  taxYear,
  onProcessLoan
}) => {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [loanData, setLoanData] = useState<any>(null);

  const handleProcessLoan = async () => {
    if (!employee) return;

    try {
      setLoading(true);
      setError(null);
      setLoanData(null);

      const result = await onProcessLoan(employee.employee_id, taxYear);
      setLoanData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process loan schedule');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      onClose();
      setLoanData(null);
      setError(null);
    }
  };

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <AccountBalanceWalletIcon color="primary" />
          <Typography variant="h6">
            Process Loan Schedule
          </Typography>
        </Box>
      </DialogTitle>
      <DialogContent>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Process loan schedule for {employee?.user_name || employee?.employee_id} for {taxYear}
        </Typography>

        {!loanData && !loading && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <AccountBalanceWalletIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              Loan Schedule Processing
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Click the button below to process the loan schedule and view detailed breakdown
            </Typography>
            <Button
              variant="contained"
              onClick={handleProcessLoan}
              startIcon={<AccountBalanceWalletIcon />}
              size="large"
            >
              Process Loan Schedule
            </Button>
          </Box>
        )}

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 4 }}>
            <CircularProgress size={40} />
            <Typography variant="body1" sx={{ ml: 2 }}>
              Processing loan schedule...
            </Typography>
          </Box>
        )}

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}

        {loanData && (
          <Box>
            {/* Employee Information */}
            <Card variant="outlined" sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Employee Information
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Employee ID</Typography>
                    <Typography variant="body1">{loanData.employee_info?.employee_id}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Tax Year</Typography>
                    <Typography variant="body1">{loanData.employee_info?.tax_year}</Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">Loan Status</Typography>
                    <Chip
                      label={loanData.employee_info?.has_loan ? 'Has Loan' : 'No Loan'}
                      color={loanData.employee_info?.has_loan ? 'success' : 'default'}
                      variant="outlined"
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            {loanData.loan_info ? (
              <>
                {/* Loan Details */}
                <Card variant="outlined" sx={{ mb: 3 }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Loan Details
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={6} sm={3}>
                        <Typography variant="body2" color="text.secondary">Loan Amount</Typography>
                        <Typography variant="body1" fontWeight="medium">
                          {formatCurrency(loanData.loan_info.loan_amount)}
                        </Typography>
                      </Grid>
                      <Grid item xs={6} sm={3}>
                        <Typography variant="body2" color="text.secondary">EMI Amount</Typography>
                        <Typography variant="body1" fontWeight="medium">
                          {formatCurrency(loanData.loan_info.emi_amount)}
                        </Typography>
                      </Grid>
                      <Grid item xs={6} sm={3}>
                        <Typography variant="body2" color="text.secondary">Outstanding Amount</Typography>
                        <Typography variant="body1" fontWeight="medium">
                          {formatCurrency(loanData.loan_info.outstanding_amount)}
                        </Typography>
                      </Grid>
                      <Grid item xs={6} sm={3}>
                        <Typography variant="body2" color="text.secondary">Loan Type</Typography>
                        <Typography variant="body1" fontWeight="medium">
                          {loanData.loan_info.loan_type}
                        </Typography>
                      </Grid>
                      <Grid item xs={6} sm={3}>
                        <Typography variant="body2" color="text.secondary">Company Interest Rate</Typography>
                        <Typography variant="body1" fontWeight="medium">
                          {loanData.loan_info.company_interest_rate}%
                        </Typography>
                      </Grid>
                      <Grid item xs={6} sm={3}>
                        <Typography variant="body2" color="text.secondary">SBI Interest Rate</Typography>
                        <Typography variant="body1" fontWeight="medium">
                          {loanData.loan_info.sbi_interest_rate}%
                        </Typography>
                      </Grid>
                      <Grid item xs={6} sm={3}>
                        <Typography variant="body2" color="text.secondary">Interest Saved</Typography>
                        <Typography variant="body1" fontWeight="medium" color="success.main">
                          {formatCurrency(loanData.loan_info.interest_saved)}
                        </Typography>
                      </Grid>
                      <Grid item xs={6} sm={3}>
                        <Typography variant="body2" color="text.secondary">Taxable Benefit</Typography>
                        <Typography variant="body1" fontWeight="medium" color="warning.main">
                          {formatCurrency(loanData.loan_info.taxable_benefit)}
                        </Typography>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>

                {/* Summary Statistics */}
                {loanData.loan_info.summary && (
                  <Card variant="outlined" sx={{ mb: 3 }}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Summary Statistics
                      </Typography>
                      <Grid container spacing={2}>
                        <Grid item xs={6} sm={3}>
                          <Typography variant="body2" color="text.secondary">Total Months</Typography>
                          <Typography variant="body1" fontWeight="medium">
                            {loanData.loan_info.summary.total_months}
                          </Typography>
                        </Grid>
                        <Grid item xs={6} sm={3}>
                          <Typography variant="body2" color="text.secondary">Total Principal Paid</Typography>
                          <Typography variant="body1" fontWeight="medium">
                            {formatCurrency(loanData.loan_info.summary.total_principal_paid)}
                          </Typography>
                        </Grid>
                        <Grid item xs={6} sm={3}>
                          <Typography variant="body2" color="text.secondary">Total Interest Paid</Typography>
                          <Typography variant="body1" fontWeight="medium">
                            {formatCurrency(loanData.loan_info.summary.total_interest_paid)}
                          </Typography>
                        </Grid>
                        <Grid item xs={6} sm={3}>
                          <Typography variant="body2" color="text.secondary">Total Payments Made</Typography>
                          <Typography variant="body1" fontWeight="medium">
                            {formatCurrency(loanData.loan_info.summary.total_payments_made)}
                          </Typography>
                        </Grid>
                        <Grid item xs={6} sm={3}>
                          <Typography variant="body2" color="text.secondary">Remaining Principal</Typography>
                          <Typography variant="body1" fontWeight="medium">
                            {formatCurrency(loanData.loan_info.summary.remaining_principal)}
                          </Typography>
                        </Grid>
                        <Grid item xs={6} sm={3}>
                          <Typography variant="body2" color="text.secondary">Average Monthly Payment</Typography>
                          <Typography variant="body1" fontWeight="medium">
                            {formatCurrency(loanData.loan_info.summary.average_monthly_payment)}
                          </Typography>
                        </Grid>
                      </Grid>
                    </CardContent>
                  </Card>
                )}

                {/* Monthly Payment Schedules */}
                <Grid container spacing={3}>
                  {/* Company Schedule */}
                  <Grid item xs={12} md={6}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Company Rate Schedule ({loanData.loan_info.company_interest_rate}%)
                        </Typography>
                        <TableContainer>
                          <Table size="small">
                            <TableHead>
                              <TableRow>
                                <TableCell>Month</TableCell>
                                <TableCell align="right">Outstanding</TableCell>
                                <TableCell align="right">Principal</TableCell>
                                <TableCell align="right">Interest</TableCell>
                                <TableCell align="right">EMI</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {loanData.loan_info.company_schedule?.map((item: any) => (
                                <TableRow key={item.month}>
                                  <TableCell>{item.month}</TableCell>
                                  <TableCell align="right">{formatCurrency(item.outstanding_amount)}</TableCell>
                                  <TableCell align="right">{formatCurrency(item.principal_amount)}</TableCell>
                                  <TableCell align="right">{formatCurrency(item.interest_amount)}</TableCell>
                                  <TableCell align="right">{formatCurrency(item.emi_deducted)}</TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </CardContent>
                    </Card>
                  </Grid>

                  {/* SBI Schedule */}
                  <Grid item xs={12} md={6}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          SBI Rate Schedule ({loanData.loan_info.sbi_interest_rate}%)
                        </Typography>
                        <TableContainer>
                          <Table size="small">
                            <TableHead>
                              <TableRow>
                                <TableCell>Month</TableCell>
                                <TableCell align="right">Outstanding</TableCell>
                                <TableCell align="right">Principal</TableCell>
                                <TableCell align="right">Interest</TableCell>
                                <TableCell align="right">EMI</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {loanData.loan_info.sbi_schedule?.map((item: any) => (
                                <TableRow key={item.month}>
                                  <TableCell>{item.month}</TableCell>
                                  <TableCell align="right">{formatCurrency(item.outstanding_amount)}</TableCell>
                                  <TableCell align="right">{formatCurrency(item.principal_amount)}</TableCell>
                                  <TableCell align="right">{formatCurrency(item.interest_amount)}</TableCell>
                                  <TableCell align="right">{formatCurrency(item.emi_deducted)}</TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              </>
            ) : (
              <Alert severity="info" sx={{ mt: 2 }}>
                No loan information found for this employee in the selected tax year.
              </Alert>
            )}
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={loading}>
          Close
        </Button>
        {!loanData && (
          <Button 
            onClick={handleProcessLoan} 
            variant="contained" 
            disabled={loading}
            startIcon={loading ? <CircularProgress size={16} /> : <AccountBalanceWalletIcon />}
          >
            {loading ? 'Processing...' : 'Process Loan Schedule'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

/**
 * IndividualComponentManagement Component - Admin interface for managing individual taxation components
 */
const IndividualComponentManagement: React.FC = () => {
  const [filteredEmployees, setFilteredEmployees] = useState<EmployeeRecord[]>([]);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedTaxYear, setSelectedTaxYear] = useState<string>(getCurrentTaxYear());
  const [page, setPage] = useState<number>(0);
  const [rowsPerPage, setRowsPerPage] = useState<number>(10);
  const [toast, setToast] = useState<ToastState>({ 
    show: false, 
    message: '', 
    severity: 'success' 
  });
  const [componentDialogOpen, setComponentDialogOpen] = useState<boolean>(false);
  const [selectedEmployee, setSelectedEmployee] = useState<EmployeeRecord | null>(null);
  const [monthlySalaryDialogOpen, setMonthlySalaryDialogOpen] = useState<boolean>(false);
  const [monthlySalaryEmployee, setMonthlySalaryEmployee] = useState<EmployeeRecord | null>(null);
  const [bulkProcessingDialogOpen, setBulkProcessingDialogOpen] = useState<boolean>(false);
  const [loanProcessingDialogOpen, setLoanProcessingDialogOpen] = useState<boolean>(false);
  const [loanProcessingEmployee, setLoanProcessingEmployee] = useState<EmployeeRecord | null>(null);
  
  const navigate = useNavigate();
  const userRole: UserRole | null = getUserRole();
  
  // Check if selected year is current year
  const isCurrentYear = selectedTaxYear === getCurrentTaxYear();
  const availableTaxYears = getAvailableTaxYears();
  const componentOptions = getComponentOptions();
  
  // React Query hooks
  const query: EmployeeSelectionQuery = {
    skip: 0,
    limit: 100, // Get all employees for now
    tax_year: selectedTaxYear
  };
  
  const { 
    data: employeeResponse, 
    isLoading: loading, 
    error: queryError, 
    refetch 
  } = useEmployeeSelection(query);
  
  const refreshEmployeeSelection = useRefreshEmployeeSelection();
  
  // Transform API response to local format
  const employees: EmployeeRecord[] = useMemo(() => {
    const transformedEmployees = employeeResponse?.employees?.map(emp => ({
      ...emp,
      // Ensure all required fields are present with defaults
      user_name: emp.user_name || 'Unknown',
      email: emp.email || '',
      department: emp.department || 'N/A',
      role: emp.role || 'N/A',
      
      status: emp.status || 'active',
      joining_date: emp.joining_date || '',
      current_salary: emp.current_salary || 0,
      has_tax_record: emp.has_tax_record || false,
      tax_year: emp.tax_year || selectedTaxYear,
      filing_status: (emp.filing_status as FilingStatus) || 'pending',
      total_tax: emp.total_tax || 0,
      regime: emp.regime || 'new',
      last_updated: emp.last_updated || ''
    })) || [];
    
    return transformedEmployees;
  }, [employeeResponse?.employees, selectedTaxYear]);
  
  // Convert React Query error to string
  const error = queryError ? 'Failed to load employees data. Please try again later.' : null;

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

  // Show success toast when data loads successfully
  useEffect(() => {
    if (employeeResponse?.employees && !loading) {
      showToast(`Loaded ${employeeResponse.employees.length} employees for ${selectedTaxYear}`, 'success');
    }
  }, [employeeResponse, loading, selectedTaxYear]);

  // Show error toast when there's an error
  useEffect(() => {
    if (queryError) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Error fetching employees:', queryError);
      }
      showToast('Failed to load employees data. Please try again later.', 'error');
    }
  }, [queryError]);

  // Handle search with API integration
  useEffect(() => {
    if (searchTerm.trim() === '') {
      setFilteredEmployees(employees);
    } else {
      const searchTermLower = searchTerm.toLowerCase();
      const filtered = employees.filter(emp => 
        emp.employee_id.toLowerCase().includes(searchTermLower) || 
        (emp.user_name && emp.user_name.toLowerCase().includes(searchTermLower)) ||
        (emp.email && emp.email.toLowerCase().includes(searchTermLower)) ||
        (emp.department && emp.department.toLowerCase().includes(searchTermLower))
      );
      setFilteredEmployees(filtered);
    }
    setPage(0); // Reset to first page when searching
  }, [searchTerm, employees]);

  // Event handlers
  const handleViewComponents = (empId: string): void => {
    navigate(`/taxation/components-overview/${empId}?year=${selectedTaxYear}`);
  };

  const handleManageComponents = (employee: EmployeeRecord): void => {
    setSelectedEmployee(employee);
    setComponentDialogOpen(true);
  };

  const handleComputeTax = async (employee: EmployeeRecord): Promise<void> => {
    try {
      showToast('Computing tax...', 'info');
      
      // Call the monthly tax computation API
      await taxationApi.computeMonthlyTax(employee.employee_id);
      
      showToast(`Tax computed successfully for ${employee.user_name || employee.employee_id}`, 'success');
      
      // Refresh the employee data to show updated tax values
      await handleRefresh();
      
    } catch (error) {
      console.error('Error computing tax:', error);
      showToast(`Failed to compute tax for ${employee.user_name || employee.employee_id}`, 'error');
    }
  };

  const handleComponentSelect = (componentId: string): void => {
    if (selectedEmployee) {
      const component = componentOptions.find(c => c.id === componentId);
      if (component) {
        let finalPath = `${component.path}/${selectedEmployee.employee_id}?year=${selectedTaxYear}`;
        
        // Add mode parameter for salary income options
        if (componentId === 'salary-update') {
          finalPath += '&mode=update';
        } else if (componentId === 'salary-new') {
          finalPath += '&mode=new';
        }
        
        navigate(finalPath);
      }
    }
    setComponentDialogOpen(false);
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

  const handlePageChange = (_event: unknown, newPage: number): void => {
    setPage(newPage);
  };

  const handleRowsPerPageChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleRefresh = async (): Promise<void> => {
    try {
      await refetch();
      refreshEmployeeSelection(query);
      showToast(`Employee data refreshed for ${selectedTaxYear}`, 'success');
    } catch (error) {
      console.error('Error refreshing employees:', error);
      showToast('Failed to refresh employee data', 'error');
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
  const renderStatusChip = (status: FilingStatus | undefined): React.ReactElement => {
    const getStatusProps = (status: FilingStatus | undefined) => {
      switch (status?.toLowerCase()) {
        case 'filed': return { color: 'success' as const, label: 'Filed' };
        case 'approved': return { color: 'success' as const, label: 'Approved' };
        case 'pending': return { color: 'warning' as const, label: 'Pending' };
        case 'draft': return { color: 'default' as const, label: 'Draft' };
        case 'rejected': return { color: 'error' as const, label: 'Rejected' };
        default: return { color: 'default' as const, label: 'N/A' };
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

  // Helper function to render tax regime chip
  const renderTaxRegimeChip = (regime: string | undefined): React.ReactElement => {
    const normalizedRegime = regime?.toLowerCase() || 'new';
    const isOldRegime = normalizedRegime === 'old';
    
    return (
      <Chip
        label={isOldRegime ? 'Old Regime' : 'New Regime'}
        color={isOldRegime ? 'secondary' : 'primary'}
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
        <TableCell><Skeleton width={120} /></TableCell>
      </TableRow>
    ))
  );

  // Render empty state
  const renderEmptyState = (): React.ReactElement => (
    <TableRow>
      <TableCell colSpan={7} align="center" sx={{ py: 6 }}>
        <Box sx={{ textAlign: 'center' }}>
          <PersonIcon 
            sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} 
          />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            {searchTerm ? 'No employees found' : `No employees for ${selectedTaxYear}`}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {searchTerm 
              ? `No employees match "${searchTerm}" for ${selectedTaxYear}`
              : `No employee tax records available for ${selectedTaxYear}`
            }
          </Typography>
        </Box>
      </TableCell>
    </TableRow>
  );

  // Get paginated data
  const paginatedEmployees = filteredEmployees.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  const handleComputeMonthlySalary = async (request: {
    employee_id: string;
    month: number;
    year: number;
    tax_year: string;
    arrears?: number | undefined;
    bonus?: number | undefined;
    use_declared_values: boolean;
  }): Promise<void> => {
    try {
      showToast('Computing monthly salary...', 'info');
      
      // Call the monthly salary computation API
      await salaryProcessingApi.computeMonthlySalary({
        employee_id: request.employee_id,
        month: request.month,
        year: request.year,
        tax_year: request.tax_year,
        force_recompute: true,
        computed_by: 'admin'
      });
      
      showToast(`Monthly salary computed successfully for ${request.employee_id}`, 'success');
      
      // Refresh the employee data to show updated values
      await handleRefresh();
      
    } catch (error) {
      console.error('Error computing monthly salary:', error);
      showToast(`Failed to compute monthly salary for ${request.employee_id}`, 'error');
      throw error;
    }
  };

  const handleOpenMonthlySalaryDialog = (employee: EmployeeRecord): void => {
    setMonthlySalaryEmployee(employee);
    setMonthlySalaryDialogOpen(true);
  };

  const handleCloseMonthlySalaryDialog = (): void => {
    setMonthlySalaryDialogOpen(false);
    setMonthlySalaryEmployee(null);
  };

  const handleBulkSalaryProcessing = async (requests: {
    employee_id: string;
    month: number;
    year: number;
    tax_year: string;
    arrears?: number | undefined;
    bonus?: number | undefined;
    use_declared_values: boolean;
  }[]): Promise<void> => {
    try {
      showToast(`Processing salary for ${requests.length} employees...`, 'info');
      
      // Process each employee sequentially to avoid overwhelming the server
      for (let i = 0; i < requests.length; i++) {
        const request = requests[i];
        if (!request) continue; // Skip if request is undefined
        
        try {
          await salaryProcessingApi.computeMonthlySalary({
            employee_id: request.employee_id,
            month: request.month,
            year: request.year,
            tax_year: request.tax_year,
            force_recompute: true,
            computed_by: 'admin'
          });
          
          // Show progress for every 5 employees or at the end
          if ((i + 1) % 5 === 0 || i === requests.length - 1) {
            showToast(`Processed ${i + 1} of ${requests.length} employees`, 'info');
          }
        } catch (error) {
          console.error(`Error processing employee ${request.employee_id}:`, error);
          // Continue with other employees even if one fails
        }
      }
      
      showToast(`Successfully processed salary for ${requests.length} employees`, 'success');
      
      // Refresh the employee data to show updated values
      await handleRefresh();
      
    } catch (error) {
      console.error('Error in bulk salary processing:', error);
      showToast(`Failed to process bulk salary for some employees`, 'error');
      throw error;
    }
  };

  const handleOpenBulkProcessingDialog = (): void => {
    setBulkProcessingDialogOpen(true);
  };

  const handleCloseBulkProcessingDialog = (): void => {
    setBulkProcessingDialogOpen(false);
  };

  const handleProcessLoan = async (employeeId: string, taxYear: string): Promise<any> => {
    try {
      showToast('Processing loan schedule...', 'info');
      
      // Call the loan processing API
      const result = await taxationApi.processLoanSchedule(employeeId, taxYear);
      
      showToast(`Loan schedule processed successfully for ${employeeId}`, 'success');
      
      return result;
      
    } catch (error) {
      console.error('Error processing loan schedule:', error);
      showToast(`Failed to process loan schedule for ${employeeId}`, 'error');
      throw error;
    }
  };

  const handleOpenLoanProcessingDialog = (employee: EmployeeRecord): void => {
    setLoanProcessingEmployee(employee);
    setLoanProcessingDialogOpen(true);
  };

  const handleCloseLoanProcessingDialog = (): void => {
    setLoanProcessingDialogOpen(false);
    setLoanProcessingEmployee(null);
  };

  if (loading) {
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
                Individual Component Management
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Manage individual taxation components for employees - {selectedTaxYear}
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
                variant="contained" 
                color="success"
                startIcon={<PlaylistAddCheckIcon />}
                onClick={handleOpenBulkProcessingDialog}
                disabled={loading || employees.length === 0}
              >
                BULK PROCESS
              </Button>
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
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
          <TextField
            sx={{ minWidth: 300, flexGrow: 1, maxWidth: 500 }}
            label="Search employees"
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
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="body2" color="text.secondary">
              {filteredEmployees.length} employee{filteredEmployees.length !== 1 ? 's' : ''} for {selectedTaxYear}
            </Typography>
            {loading && <CircularProgress size={16} />}
          </Box>
        </Box>
      </Paper>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

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
                <TableCell>Employee ID</TableCell>
                <TableCell>Employee Name</TableCell>
                <TableCell>Tax Year</TableCell>
                <TableCell>Tax Regime</TableCell>
                <TableCell align="right">Total Tax</TableCell>
                <TableCell align="center">Filing Status</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                renderTableSkeleton()
              ) : paginatedEmployees.length > 0 ? (
                paginatedEmployees.map((employee) => (
                  <Fade in key={employee.employee_id} timeout={300}>
                    <TableRow 
                      hover
                      sx={{ 
                        '&:hover': { 
                          backgroundColor: 'action.hover' 
                        }
                      }}
                    >
                      <TableCell>
                        <Typography variant="subtitle2" fontWeight="medium">
                          {employee.employee_id}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="body2" fontWeight="medium">
                            {employee.user_name || 'Unknown'}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {employee.tax_year || 'N/A'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        {renderTaxRegimeChip(employee.regime)}
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" fontWeight="medium">
                          {formatCurrency(employee.total_tax)}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        {renderStatusChip(employee.filing_status as FilingStatus)}
                      </TableCell>
                      <TableCell align="center">
                        <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center' }}>
                          <Tooltip title="View Components">
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={() => handleViewComponents(employee.employee_id)}
                            >
                              <VisibilityIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Manage Components">
                            <IconButton
                              size="small"
                              color="secondary"
                              onClick={() => handleManageComponents(employee)}
                            >
                              <SettingsIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Compute Tax">
                            <IconButton
                              size="small"
                              color="success"
                              onClick={() => handleComputeTax(employee)}
                            >
                              <FunctionsIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Compute Monthly Salary">
                            <IconButton
                              size="small"
                              color="info"
                              onClick={() => handleOpenMonthlySalaryDialog(employee)}
                            >
                              <AttachMoneyIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Process Loan">
                            <IconButton
                              size="small"
                              color="warning"
                              onClick={() => handleOpenLoanProcessingDialog(employee)}
                            >
                              <AccountBalanceWalletIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
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
        {filteredEmployees.length > 0 && (
          <TablePagination
            component="div"
            count={filteredEmployees.length}
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

      {/* Component Selection Dialog */}
      <Dialog 
        open={componentDialogOpen} 
        onClose={() => setComponentDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <SettingsIcon color="primary" />
            <Typography variant="h6">
              Manage Components for {selectedEmployee?.user_name || selectedEmployee?.employee_id}
            </Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Select a component to manage for {selectedEmployee?.employee_id} for {selectedTaxYear}
          </Typography>
          <Grid container spacing={2}>
            {componentOptions.map((component) => (
              <Grid item xs={12} sm={6} md={4} key={component.id}>
                <Card 
                  variant="outlined" 
                  sx={{ 
                    cursor: 'pointer',
                    '&:hover': { 
                      borderColor: `${component.color}.main`,
                      backgroundColor: `${component.color}.50`
                    }
                  }}
                  onClick={() => handleComponentSelect(component.id)}
                >
                  <CardContent sx={{ textAlign: 'center', py: 2 }}>
                    <Box sx={{ color: `${component.color}.main`, mb: 1 }}>
                      {component.icon}
                    </Box>
                    <Typography variant="subtitle2" fontWeight="medium" gutterBottom>
                      {component.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {component.description}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setComponentDialogOpen(false)}>
            Cancel
          </Button>
        </DialogActions>
      </Dialog>

      {/* Monthly Salary Compute Dialog */}
      <MonthlySalaryComputeDialog
        open={monthlySalaryDialogOpen}
        onClose={handleCloseMonthlySalaryDialog}
        employee={monthlySalaryEmployee}
        taxYear={selectedTaxYear}
        onCompute={handleComputeMonthlySalary}
      />

      {/* Bulk Salary Processing Dialog */}
      <BulkSalaryProcessingDialog
        open={bulkProcessingDialogOpen}
        onClose={handleCloseBulkProcessingDialog}
        employees={employees}
        taxYear={selectedTaxYear}
        onBulkCompute={handleBulkSalaryProcessing}
      />

      {/* Loan Processing Dialog */}
      <LoanProcessingDialog
        open={loanProcessingDialogOpen}
        onClose={handleCloseLoanProcessingDialog}
        employee={loanProcessingEmployee}
        taxYear={selectedTaxYear}
        onProcessLoan={handleProcessLoan}
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

export default IndividualComponentManagement; 