import React, { useState, useEffect, useCallback } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Button, 
  Card, 
  CardContent, 
  Tab, 
  Tabs,
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  CircularProgress,
  Alert,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  SelectChangeEvent
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { getAllTaxation, getMyTaxation } from '../../services/taxationService';
import { getUserRole, getUserId } from '../../utils/auth';
import PageLayout from '../../layout/PageLayout';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import { 
  TaxationDashboardData, 
  FilingStatusOption, 
  UserRole, 
  Perquisites,
  ExtendedTaxBreakup 
} from '../../types';

interface ChartDataItem {
  name: string;
  amount: number;
  color: string;
}

const TaxationDashboard: React.FC = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState<number>(0);
  const [taxationData, setTaxationData] = useState<TaxationDashboardData[]>([]);
  
  // Get current financial year in format YYYY-YYYY
  const getCurrentFinancialYear = (): string => {
    const today = new Date();
    const currentMonth = today.getMonth();
    const currentYear = today.getFullYear();
    
    // In India, financial year starts from April (month index 3)
    // If current month is January to March, FY is previous year to current year
    // If current month is April to December, FY is current year to next year
    if (currentMonth < 3) { // January to March
      return `${currentYear-1}-${currentYear}`;
    } else { // April to December
      return `${currentYear}-${currentYear+1}`;
    }
  };

  const [taxYear, setTaxYear] = useState<string>(getCurrentFinancialYear());
  const [filingStatus, setFilingStatus] = useState<string>("draft");
  const navigate = useNavigate();
  const userRole = getUserRole() as UserRole;
  const userId = getUserId();
  const isAdmin = userRole === 'admin' || userRole === 'superadmin';

  // Generate recent financial years dynamically
  const generateTaxYears = (): string[] => {
    const currentFY = getCurrentFinancialYear();
    const years = [currentFY];
    
    // Add 3 previous financial years
    const [startYearStr] = currentFY.split('-');
    if (startYearStr) {
      const startYear = parseInt(startYearStr);
      
      for (let i = 1; i <= 3; i++) {
        years.push(`${startYear-i}-${startYear-i+1}`);
      }
    }
    
    return years;
  };

  // Tax years array
  const taxYears = generateTaxYears();

  // Filing statuses
  const filingStatuses: FilingStatusOption[] = [
    { value: "draft", label: "Draft" },
    { value: "filed", label: "Filed" },
    { value: "approved", label: "Approved" },
    { value: "rejected", label: "Rejected" },
    { value: "pending", label: "Pending" }
  ];

  const fetchTaxationData = useCallback(async (): Promise<void> => {
    try {
      setLoading(true);
      setError(null);
      
      if (isAdmin) {
        // Admin users see all taxation data
        const response = await getAllTaxation(taxYear || null, filingStatus as any || null);
        setTaxationData((response as any).records || []);
      } else {
        // Regular users see only their data
        try {
          const response = await getMyTaxation();
          // Convert to array format for consistency with admin view
          setTaxationData(response ? [response as any] : []);
        } catch (err: any) {
          if (err.response && err.response.status === 404) {
            // If no taxation record exists for this user
            setTaxationData([]);
          } else {
            throw err;
          }
        }
      }
    } catch (err: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error fetching taxation data:', err);
      }
      setError('Failed to load taxation data. Please try again later.');
    } finally {
      setLoading(false);
    }
  }, [taxYear, filingStatus, isAdmin]);

  useEffect(() => {
    fetchTaxationData();
  }, [fetchTaxationData]);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number): void => {
    setTabValue(newValue);
  };

  const handleYearChange = (event: SelectChangeEvent<string>): void => {
    setTaxYear(event.target.value);
  };

  const handleStatusChange = (event: SelectChangeEvent<string>): void => {
    setFilingStatus(event.target.value);
  };

  const handleViewDetails = (empId: string): void => {
    navigate(`/api/v2/taxation/employee/${empId}`);
  };

  const handleNewDeclaration = (): void => {
    navigate('/api/v2/taxation/declaration');
  };

  const handleMyTaxDetail = (): void => {
    // Navigate to the current user's tax details
    navigate(`/api/v2/taxation/employee/${userId}`);
  };

  // Get total value of perquisites
  const calculatePerquisitesTotal = (perquisites?: Perquisites): number => {
    if (!perquisites) return 0;
    
    // Since the perquisites is an object containing various perquisite values,
    // we need to determine its total value
    return Object.values(perquisites)
      .filter(value => typeof value === 'number')
      .reduce((sum, value) => sum + value, 0);
  };

  // Format currency
  const formatCurrency = (amount?: number): string => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount || 0);
  };

  const renderTaxationTable = (): React.ReactElement => {
    if (loading) {
      return (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      );
    }

    if (error) {
      return <Alert severity="error">{error}</Alert>;
    }

    if (taxationData.length === 0) {
      return <Alert severity="info">No taxation records found with the selected filters.</Alert>;
    }

    return (
      <TableContainer component={Paper} sx={{ mt: 2 }}>
        <Table sx={{ minWidth: 650 }} aria-label="taxation table">
          <TableHead>
            <TableRow sx={{ backgroundColor: 'primary.light' }}>
              <TableCell><Typography variant="subtitle2">Employee ID</Typography></TableCell>
              <TableCell><Typography variant="subtitle2">Tax Year</Typography></TableCell>
              <TableCell><Typography variant="subtitle2">Tax Regime</Typography></TableCell>
              <TableCell><Typography variant="subtitle2">Total Tax</Typography></TableCell>
              <TableCell><Typography variant="subtitle2">Tax Paid</Typography></TableCell>
              <TableCell><Typography variant="subtitle2">Tax Due</Typography></TableCell>
              <TableCell><Typography variant="subtitle2">Filing Status</Typography></TableCell>
              <TableCell><Typography variant="subtitle2">Actions</Typography></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {taxationData.map((row) => (
              <TableRow key={row.employee_id + row.tax_year}>
                <TableCell>{row.employee_id}</TableCell>
                <TableCell>{row.tax_year}</TableCell>
                <TableCell>{row.regime === 'old' ? 'Old Regime' : 'New Regime'}</TableCell>
                <TableCell>{formatCurrency(row.total_tax)}</TableCell>
                <TableCell>{formatCurrency(row.tax_paid)}</TableCell>
                <TableCell>{formatCurrency(row.tax_due)}</TableCell>
                <TableCell>
                  <Box sx={{ 
                    display: 'inline-block', 
                    bgcolor: getStatusColor(row.filing_status), 
                    px: 1, 
                    py: 0.5, 
                    borderRadius: 1 
                  }}>
                    {row.filing_status?.charAt(0)?.toUpperCase() + row.filing_status?.slice(1) || 'N/A'}
                  </Box>
                </TableCell>
                <TableCell>
                  <Button 
                    variant="outlined" 
                    size="small" 
                    onClick={() => handleViewDetails(row.employee_id)}
                  >
                    View Details
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  // Helper function to get color for filing status
  const getStatusColor = (status: string): string => {
    switch (status.toLowerCase()) {
      case 'draft': return '#e0e0e0';
      case 'filed': return '#bbdefb';
      case 'approved': return '#c8e6c9';
      case 'rejected': return '#ffcdd2';
      case 'pending': return '#fff9c4';
      default: return '#e0e0e0';
    }
  };

  // Summary cards for admin dashboard
  const renderSummaryCards = (): React.ReactElement => {
    // Calculate summary metrics
    const totalTaxAmount = taxationData.reduce((sum, item) => sum + (item.total_tax || 0), 0);
    const totalTaxPaid = taxationData.reduce((sum, item) => sum + (item.tax_paid || 0), 0);
    const totalTaxDue = taxationData.reduce((sum, item) => sum + (item.tax_due || 0), 0);
    const filedCount = taxationData.filter(item => item.filing_status === 'filed').length;
    
    return (
      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, 
        gap: 3, 
        mb: 3 
      }}>
        <Card sx={{ bgcolor: '#bbdefb' }}>
          <CardContent>
            <Typography variant="h6" component="div">Total Tax</Typography>
            <Typography variant="h4">{formatCurrency(totalTaxAmount)}</Typography>
          </CardContent>
        </Card>
        <Card sx={{ bgcolor: '#c8e6c9' }}>
          <CardContent>
            <Typography variant="h6" component="div">Tax Paid</Typography>
            <Typography variant="h4">{formatCurrency(totalTaxPaid)}</Typography>
          </CardContent>
        </Card>
        <Card sx={{ bgcolor: '#ffcdd2' }}>
          <CardContent>
            <Typography variant="h6" component="div">Tax Due</Typography>
            <Typography variant="h4">{formatCurrency(totalTaxDue)}</Typography>
          </CardContent>
        </Card>
        <Card sx={{ bgcolor: '#fff9c4' }}>
          <CardContent>
            <Typography variant="h6" component="div">Filed Returns</Typography>
            <Typography variant="h4">{filedCount}</Typography>
          </CardContent>
        </Card>
      </Box>
    );
  };

  // User summary card for regular users
  const renderUserSummaryCard = (): React.ReactElement => {
    if (taxationData.length === 0) {
      return (
        <Alert severity="info" sx={{ mb: 3 }}>
          No tax declarations found. Please create a new tax declaration.
        </Alert>
      );
    }
    
    const userData = taxationData[0]; // Since regular users will only have one record
    if (!userData) {
      return (
        <Alert severity="info" sx={{ mb: 3 }}>
          No tax declarations found. Please create a new tax declaration.
        </Alert>
      );
    }
    
    const extendedTaxBreakup = userData.tax_breakup as ExtendedTaxBreakup;
    
    const chartData: ChartDataItem[] = [
      { name: 'Total Tax', amount: userData.total_tax || 0, color: '#1976d2' },
      { name: 'Tax Paid', amount: userData.tax_paid || 0, color: '#2e7d32' },
      { name: 'Tax Due', amount: userData.tax_due || 0, color: '#d32f2f' },
      { name: 'Tax Refundable', amount: userData.tax_refundable || 0, color: '#0288d1' },
    ];
    
    return (
      <Box>
        {/* Employee Information Card */}
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)' }, 
          gap: 3, 
          mb: 3 
        }}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h5" gutterBottom>Employee Information</Typography>
            <Box sx={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(2, 1fr)', 
              gap: 2 
            }}>
              <Typography variant="subtitle1">Employee ID:</Typography>
              <Typography variant="body1">{userData.employee_id}</Typography>
              
              <Typography variant="subtitle1">Tax Year:</Typography>
              <Typography variant="body1">{userData.tax_year}</Typography>
              
              <Typography variant="subtitle1">Tax Regime:</Typography>
              <Typography variant="body1">
                {userData.regime === 'old' ? 'Old Regime' : 'New Regime'}
              </Typography>
              
              <Typography variant="subtitle1">Filing Status:</Typography>
              <Box sx={{ 
                display: 'inline-block', 
                bgcolor: getStatusColor(userData.filing_status), 
                px: 1, 
                py: 0.5, 
                borderRadius: 1 
              }}>
                {(userData.filing_status?.charAt(0)?.toUpperCase() + userData.filing_status?.slice(1)) || 'N/A'}
              </Box>
            </Box>
          </Paper>

          {/* Tax Summary Card with Bar Chart */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h5" gutterBottom>Tax Summary</Typography>
            <Box sx={{ height: 300, mt: 2, mb: 4 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={chartData}
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis 
                    tickFormatter={(value: number) => 
                      new Intl.NumberFormat('en-IN', {
                        style: 'currency',
                        currency: 'INR',
                        notation: 'compact',
                        maximumFractionDigits: 1
                      }).format(value)
                    } 
                  />
                  <Tooltip 
                    formatter={(value: number) => 
                      new Intl.NumberFormat('en-IN', {
                        style: 'currency',
                        currency: 'INR',
                        maximumFractionDigits: 0
                      }).format(value)
                    }
                  />
                  <Legend />
                  <Bar dataKey="amount" name="Amount" fill="#8884d8" radius={[4, 4, 0, 0]}>
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </Box>
            
            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
              <Button
                variant="outlined"
                color="primary"
                onClick={handleMyTaxDetail}
              >
                View Full Details
              </Button>
            </Box>
          </Paper>
        </Box>
          
        {/* Income & Deduction Details */}
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)' }, 
          gap: 3, 
          mb: 3 
        }}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h5" gutterBottom>Income Details</Typography>
            
            <Typography variant="h6" color="primary" sx={{ mt: 2 }}>Salary Components</Typography>
            <TableContainer component={Paper} variant="outlined" sx={{ mb: 3 }}>
              <Table size="small">
                <TableHead>
                  <TableRow sx={{ backgroundColor: 'primary.light' }}>
                    <TableCell>Component</TableCell>
                    <TableCell align="right">Amount</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  <TableRow>
                    <TableCell>Basic Salary</TableCell>
                    <TableCell align="right">{formatCurrency(userData.salary?.basic)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>HRA</TableCell>
                    <TableCell align="right">{formatCurrency(userData.salary?.hra)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Special Allowance</TableCell>
                    <TableCell align="right">{formatCurrency(userData.salary?.special_allowance)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Bonus</TableCell>
                    <TableCell align="right">{formatCurrency(userData.salary?.bonus)}</TableCell>
                  </TableRow>
                  {userData.salary?.perquisites && (
                    <TableRow>
                      <TableCell>Perquisites</TableCell>
                      <TableCell align="right">
                        {formatCurrency(calculatePerquisitesTotal(userData.salary.perquisites))}
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
            
            <Typography variant="h6" color="primary">Other Income</Typography>
            <TableContainer component={Paper} variant="outlined" sx={{ mb: 3 }}>
              <Table size="small">
                <TableHead>
                  <TableRow sx={{ backgroundColor: 'primary.light' }}>
                    <TableCell>Source</TableCell>
                    <TableCell align="right">Amount</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  <TableRow>
                    <TableCell>Interest from Savings</TableCell>
                    <TableCell align="right">{formatCurrency(userData.other_sources?.interest_savings || 0)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Interest from Fixed Deposits</TableCell>
                    <TableCell align="right">{formatCurrency(userData.other_sources?.interest_fd || 0)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Interest from Recurring Deposits</TableCell>
                    <TableCell align="right">{formatCurrency(userData.other_sources?.interest_rd || 0)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Dividend Income</TableCell>
                    <TableCell align="right">{formatCurrency(userData.other_sources?.dividend_income || 0)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Gift Income</TableCell>
                    <TableCell align="right">{formatCurrency(userData.other_sources?.gifts || 0)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Other Interest</TableCell>
                    <TableCell align="right">{formatCurrency(userData.other_sources?.other_interest || 0)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Business & Professional Income</TableCell>
                    <TableCell align="right">{formatCurrency(userData.other_sources?.business_professional_income || 0)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Other Income</TableCell>
                    <TableCell align="right">{formatCurrency(userData.other_sources?.other_income || 0)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Capital Gains (Short Term)</TableCell>
                    <TableCell align="right">
                      {formatCurrency(
                        (userData.capital_gains?.stcg_111a || 0) +
                        (userData.capital_gains?.stcg_any_other_asset || 0) +
                        (userData.capital_gains?.stcg_debt_mutual_fund || 0)
                      )}
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Capital Gains (Long Term)</TableCell>
                    <TableCell align="right">
                      {formatCurrency(
                        (userData.capital_gains?.ltcg_112a || 0) +
                        (userData.capital_gains?.ltcg_any_other_asset || 0) +
                        (userData.capital_gains?.ltcg_debt_mutual_fund || 0)
                      )}
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>

          {userData.regime === 'old' && (
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" color="primary">Deductions</Typography>
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow sx={{ backgroundColor: 'primary.light' }}>
                      <TableCell>Section</TableCell>
                      <TableCell align="right">Amount</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    <TableRow>
                      <TableCell>Section 80C (Life Insurance)</TableCell>
                      <TableCell align="right">{formatCurrency(userData.deductions?.section_80c_lic || 0)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Section 80C (EPF)</TableCell>
                      <TableCell align="right">{formatCurrency(userData.deductions?.section_80c_epf || 0)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Section 80C (Other Investments)</TableCell>
                      <TableCell align="right">{formatCurrency(
                        (userData.deductions?.section_80c_ssp || 0) +
                        (userData.deductions?.section_80c_nsc || 0) +
                        (userData.deductions?.section_80c_ulip || 0) +
                        (userData.deductions?.section_80c_tsmf || 0) +
                        (userData.deductions?.section_80c_tffte2c || 0) +
                        (userData.deductions?.section_80c_paphl || 0) +
                        (userData.deductions?.section_80c_sdpphp || 0) +
                        (userData.deductions?.section_80c_tsfdsb || 0) +
                        (userData.deductions?.section_80c_scss || 0) +
                        (userData.deductions?.section_80c_others || 0)
                      )}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Section 80CCC/CCD (Pension)</TableCell>
                      <TableCell align="right">{formatCurrency(
                        (userData.deductions?.section_80ccc_ppic || 0) +
                        (userData.deductions?.section_80ccd_1_nps || 0) +
                        (userData.deductions?.section_80ccd_1b_additional || 0) +
                        (userData.deductions?.section_80ccd_2_enps || 0)
                      )}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Section 80D (Health Insurance)</TableCell>
                      <TableCell align="right">{formatCurrency(
                        (userData.deductions?.section_80d_hisf || 0) +
                        (userData.deductions?.section_80d_phcs || 0) +
                        (userData.deductions?.section_80d_hi_parent || 0)
                      )}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Section 80DD/DDB (Disability/Disease)</TableCell>
                      <TableCell align="right">{formatCurrency(
                        (userData.deductions?.section_80dd || 0) +
                        (userData.deductions?.section_80ddb || 0)
                      )}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Section 80E (Educational Loan)</TableCell>
                      <TableCell align="right">{formatCurrency(userData.deductions?.section_80e_interest || 0)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Section 80EEB (EV Loan)</TableCell>
                      <TableCell align="right">{formatCurrency(userData.deductions?.section_80eeb || 0)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Section 80G (Donations)</TableCell>
                      <TableCell align="right">{formatCurrency(
                        (userData.deductions?.section_80g_100_wo_ql || 0) +
                        (userData.deductions?.section_80g_50_wo_ql || 0) +
                        (userData.deductions?.section_80g_100_ql || 0) +
                        (userData.deductions?.section_80g_50_ql || 0)
                      )}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Section 80GGC (Political Contributions)</TableCell>
                      <TableCell align="right">{formatCurrency(userData.deductions?.section_80ggc || 0)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Section 80U (Self Disability)</TableCell>
                      <TableCell align="right">{formatCurrency(userData.deductions?.section_80u || 0)}</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          )}
        </Box>
          
        {/* Tax Breakup Section */}
        <Paper sx={{ p: 3 }}>
          <Typography variant="h5" gutterBottom>Tax Calculation Breakup</Typography>
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow sx={{ backgroundColor: 'primary.light' }}>
                  <TableCell>Component</TableCell>
                  <TableCell align="right">Amount</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {extendedTaxBreakup?.details && (
                  <>
                    <TableRow>
                      <TableCell>Regular Income Tax</TableCell>
                      <TableCell align="right">{formatCurrency(extendedTaxBreakup.details.regular_income)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>STCG - Equity (15%)</TableCell>
                      <TableCell align="right">{formatCurrency(extendedTaxBreakup.details.stcg_flat_rate)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>STCG - Other (Slab Rate)</TableCell>
                      <TableCell align="right">{formatCurrency(extendedTaxBreakup.details.stcg_slab_rate)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>LTCG - Equity (10%)</TableCell>
                      <TableCell align="right">{formatCurrency(extendedTaxBreakup.details.ltcg_112a)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>LTCG - Other (20%)</TableCell>
                      <TableCell align="right">{formatCurrency(extendedTaxBreakup.details.ltcg_other)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Dividend Income</TableCell>
                      <TableCell align="right">{formatCurrency(extendedTaxBreakup.details.dividend_income)}</TableCell>
                    </TableRow>
                  </>
                )}
                <TableRow>
                  <TableCell>Base Tax</TableCell>
                  <TableCell align="right">{formatCurrency(extendedTaxBreakup?.base_tax)}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Tax after Rebate</TableCell>
                  <TableCell align="right">{formatCurrency(extendedTaxBreakup?.tax_after_rebate)}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Surcharge</TableCell>
                  <TableCell align="right">{formatCurrency(extendedTaxBreakup?.surcharge)}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Cess</TableCell>
                  <TableCell align="right">{formatCurrency(extendedTaxBreakup?.cess)}</TableCell>
                </TableRow>
                <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                  <TableCell><Typography variant="subtitle1">Total Tax</Typography></TableCell>
                  <TableCell align="right">
                    <Typography variant="subtitle1">{formatCurrency(userData.total_tax)}</Typography>
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      </Box>
    );
  };

  return (
    <PageLayout title="Taxation Dashboard">
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            {isAdmin ? "Taxation Dashboard" : "My Tax Dashboard"}
          </Typography>
          
          <Button 
            variant="contained" 
            color="primary" 
            onClick={handleNewDeclaration}
          >
            {isAdmin ? "New Tax Declaration" : "Edit Tax Declaration"}
          </Button>
        </Box>

        {isAdmin && (
          <Box sx={{ mb: 3 }}>
            <Tabs 
              value={tabValue} 
              onChange={handleTabChange}
              indicatorColor="primary"
              textColor="primary"
              variant="fullWidth"
            >
              <Tab label="Overview" />
              <Tab label="All Declarations" />
              {userRole === 'superadmin' && <Tab label="Administration" />}
            </Tabs>
          </Box>
        )}

        {/* Filters - Only show for admin users */}
        {isAdmin && (
          <Paper sx={{ p: 2, mb: 3 }}>
            <Box sx={{ 
              display: 'grid', 
              gridTemplateColumns: { xs: '1fr', sm: 'repeat(3, 1fr)' }, 
              gap: 2, 
              alignItems: 'center' 
            }}>
              <FormControl fullWidth variant="outlined" size="medium" sx={{ minHeight: 56 }}>
                <InputLabel id="tax-year-label">Tax Year</InputLabel>
                <Select
                  labelId="tax-year-label"
                  value={taxYear}
                  onChange={handleYearChange}
                  label="Tax Year"
                  sx={{ height: 56 }}
                >
                  <MenuItem value="">All Years</MenuItem>
                  {taxYears.map(year => (
                    <MenuItem key={year} value={year}>{year}</MenuItem>
                  ))}
                </Select>
              </FormControl>
              <FormControl fullWidth variant="outlined" size="medium" sx={{ minHeight: 56 }}>
                <InputLabel id="filing-status-label">Filing Status</InputLabel>
                <Select
                  labelId="filing-status-label"
                  value={filingStatus}
                  onChange={handleStatusChange}
                  label="Filing Status"
                  sx={{ height: 56 }}
                >
                  <MenuItem value="">All Statuses</MenuItem>
                  {filingStatuses.map(status => (
                    <MenuItem key={status.value} value={status.value}>{status.label}</MenuItem>
                  ))}
                </Select>
              </FormControl>
              <Button 
                variant="outlined" 
                color="primary" 
                fullWidth
                onClick={fetchTaxationData}
                sx={{ height: 56 }}
              >
                Refresh Data
              </Button>
            </Box>
          </Paper>
        )}

        {/* Admin dashboard overview */}
        {isAdmin && tabValue === 0 && renderSummaryCards()}
        
        {/* User dashboard summary */}
        {!isAdmin && renderUserSummaryCard()}
        
        {/* All declarations tab */}
        {(isAdmin && tabValue === 1) || (isAdmin && tabValue === 0 && !renderSummaryCards()) ? (
          renderTaxationTable()
        ) : null}
        
        {/* Non-admin view - show table if not showing user summary */}
        {!isAdmin && !taxationData.length && renderTaxationTable()}
        
        {/* Admin tab for superadmin */}
        {isAdmin && userRole === 'superadmin' && tabValue === 2 && (
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Administration</Typography>
            <Box sx={{ mt: 2 }}>
              <Button 
                variant="contained" 
                color="primary" 
                onClick={() => navigate('/api/v2/taxation/employee-selection')} 
                sx={{ mr: 2 }}
              >
                Manage Employee Declarations
              </Button>
            </Box>
          </Paper>
        )}
      </Box>
    </PageLayout>
  );
};

export default TaxationDashboard; 