import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Button, 
  Grid, 
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
  Divider
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { getAllTaxation, getTaxationByEmpId, getMyTaxation } from '../../services/taxationService';
import { getUserRole, getUserId } from '../../utils/auth';
import PageLayout from '../../layout/PageLayout';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';

const TaxationDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  const [taxationData, setTaxationData] = useState([]);
  
  // Get current financial year in format YYYY-YYYY
  const getCurrentFinancialYear = () => {
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

  const [taxYear, setTaxYear] = useState(getCurrentFinancialYear());
  const [filingStatus, setFilingStatus] = useState("draft");
  const navigate = useNavigate();
  const userRole = getUserRole();
  const userId = getUserId();
  const isAdmin = userRole === 'admin' || userRole === 'superadmin';

  // Generate recent financial years dynamically
  const generateTaxYears = () => {
    const currentFY = getCurrentFinancialYear();
    const years = [currentFY];
    
    // Add 3 previous financial years
    const [startYearStr] = currentFY.split('-');
    const startYear = parseInt(startYearStr);
    
    for (let i = 1; i <= 3; i++) {
      years.push(`${startYear-i}-${startYear-i+1}`);
    }
    
    return years;
  };

  // Tax years array
  const taxYears = generateTaxYears();

  // Filing statuses
  const filingStatuses = [
    { value: "draft", label: "Draft" },
    { value: "filed", label: "Filed" },
    { value: "approved", label: "Approved" },
    { value: "rejected", label: "Rejected" },
    { value: "pending", label: "Pending" }
  ];

  useEffect(() => {
    fetchTaxationData();
  }, [taxYear, filingStatus]);

  const fetchTaxationData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      if (isAdmin) {
        // Admin users see all taxation data
        const response = await getAllTaxation(taxYear || null, filingStatus || null);
        setTaxationData(response.records || []);
      } else {
        // Regular users see only their data
        try {
          const response = await getMyTaxation();
          // Convert to array format for consistency with admin view
          setTaxationData(response ? [response] : []);
        } catch (err) {
          if (err.response && err.response.status === 404) {
            // If no taxation record exists for this user
            setTaxationData([]);
          } else {
            throw err;
          }
        }
      }
    } catch (err) {
      console.error('Error fetching taxation data:', err);
      setError('Failed to load taxation data. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleYearChange = (event) => {
    setTaxYear(event.target.value);
  };

  const handleStatusChange = (event) => {
    setFilingStatus(event.target.value);
  };

  const handleViewDetails = (empId) => {
    navigate(`/taxation/employee/${empId}`);
  };

  const handleNewDeclaration = () => {
    navigate('/taxation/declaration');
  };

  const handleMyTaxDetail = () => {
    // Navigate to the current user's tax details
    navigate(`/taxation/employee/${userId}`);
  };

  // Format currency
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  const renderTaxationTable = () => {
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
              <TableRow key={row.emp_id + row.tax_year}>
                <TableCell>{row.emp_id}</TableCell>
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
                    {row.filing_status.charAt(0).toUpperCase() + row.filing_status.slice(1)}
                  </Box>
                </TableCell>
                <TableCell>
                  <Button 
                    variant="outlined" 
                    size="small" 
                    onClick={() => handleViewDetails(row.emp_id)}
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
  const getStatusColor = (status) => {
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
  const renderSummaryCards = () => {
    // Calculate summary metrics
    const totalTaxAmount = taxationData.reduce((sum, item) => sum + (item.total_tax || 0), 0);
    const totalTaxPaid = taxationData.reduce((sum, item) => sum + (item.tax_paid || 0), 0);
    const totalTaxDue = taxationData.reduce((sum, item) => sum + (item.tax_due || 0), 0);
    const filedCount = taxationData.filter(item => item.filing_status === 'filed').length;
    
    return (
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: '#bbdefb' }}>
            <CardContent>
              <Typography variant="h6" component="div">Total Tax</Typography>
              <Typography variant="h4">{formatCurrency(totalTaxAmount)}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: '#c8e6c9' }}>
            <CardContent>
              <Typography variant="h6" component="div">Tax Paid</Typography>
              <Typography variant="h4">{formatCurrency(totalTaxPaid)}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: '#ffcdd2' }}>
            <CardContent>
              <Typography variant="h6" component="div">Tax Due</Typography>
              <Typography variant="h4">{formatCurrency(totalTaxDue)}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: '#fff9c4' }}>
            <CardContent>
              <Typography variant="h6" component="div">Filed Returns</Typography>
              <Typography variant="h4">{filedCount}</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  // User summary card for regular users
  const renderUserSummaryCard = () => {
    if (taxationData.length === 0) {
      return (
        <Alert severity="info" sx={{ mb: 3 }}>
          No tax declarations found. Please create a new tax declaration.
        </Alert>
      );
    }
    
    const userData = taxationData[0]; // Since regular users will only have one record
    
    return (
      <Box>
        {/* Employee Information Card */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h5" gutterBottom>Employee Information</Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="subtitle1">Employee ID:</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body1">{userData.emp_id}</Typography>
                </Grid>
                
                <Grid item xs={6}>
                  <Typography variant="subtitle1">Tax Year:</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body1">{userData.tax_year}</Typography>
                </Grid>
                
                <Grid item xs={6}>
                  <Typography variant="subtitle1">Tax Regime:</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body1">
                    {userData.regime === 'old' ? 'Old Regime' : 'New Regime'}
                  </Typography>
                </Grid>
                
                <Grid item xs={6}>
                  <Typography variant="subtitle1">Filing Status:</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Box sx={{ 
                    display: 'inline-block', 
                    bgcolor: getStatusColor(userData.filing_status), 
                    px: 1, 
                    py: 0.5, 
                    borderRadius: 1 
                  }}>
                    {(userData.filing_status?.charAt(0)?.toUpperCase() + userData.filing_status?.slice(1)) || 'N/A'}
                  </Box>
                </Grid>
              </Grid>
            </Paper>

            {/* Tax Summary Card with Bar Chart */}
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h5" gutterBottom>Tax Summary</Typography>
              <Box sx={{ height: 300, mt: 2, mb: 4 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={[
                      { name: 'Total Tax', amount: userData.total_tax || 0, color: '#1976d2' },
                      { name: 'Tax Paid', amount: userData.tax_paid || 0, color: '#2e7d32' },
                      { name: 'Tax Due', amount: userData.tax_due || 0, color: '#d32f2f' },
                      { name: 'Tax Refundable', amount: userData.tax_refundable || 0, color: '#0288d1' },
                    ]}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis 
                      tickFormatter={(value) => 
                        new Intl.NumberFormat('en-IN', {
                          style: 'currency',
                          currency: 'INR',
                          notation: 'compact',
                          maximumFractionDigits: 1
                        }).format(value)
                      } 
                    />
                    <Tooltip 
                      formatter={(value) => 
                        new Intl.NumberFormat('en-IN', {
                          style: 'currency',
                          currency: 'INR',
                          maximumFractionDigits: 0
                        }).format(value)
                      }
                    />
                    <Legend />
                    <Bar dataKey="amount" name="Amount" fill="#8884d8" radius={[4, 4, 0, 0]}>
                      {[
                        { name: 'Total Tax', amount: userData.total_tax || 0, color: '#1976d2' },
                        { name: 'Tax Paid', amount: userData.tax_paid || 0, color: '#2e7d32' },
                        { name: 'Tax Due', amount: userData.tax_due || 0, color: '#d32f2f' },
                        { name: 'Tax Refundable', amount: userData.tax_refundable || 0, color: '#0288d1' },
                      ].map((entry, index) => (
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
          </Grid>
          
          {/* Income & Deduction Details */}
          <Grid item xs={12} md={6}>
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
                          {formatCurrency(
                            (userData.salary?.perquisites?.company_car || 0) +
                            (userData.salary?.perquisites?.rent_free_accommodation || 0) +
                            (userData.salary?.perquisites?.concessional_loan || 0) +
                            (userData.salary?.perquisites?.gift_vouchers || 0)
                          )}
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
                      <TableCell>Interest Income</TableCell>
                      <TableCell align="right">
                        {formatCurrency(
                          (userData.other_sources?.interest_savings || 0) +
                          (userData.other_sources?.interest_fd || 0) +
                          (userData.other_sources?.interest_rd || 0)
                        )}
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Dividend Income</TableCell>
                      <TableCell align="right">{formatCurrency(userData.other_sources?.dividend_income)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Rental Income</TableCell>
                      <TableCell align="right">{formatCurrency(userData.other_sources?.rental_income)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Capital Gains</TableCell>
                      <TableCell align="right">
                        {formatCurrency(
                          (userData.capital_gains?.stcg_111a || 0) +
                          (userData.capital_gains?.ltcg_112a || 0)
                        )}
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Other Miscellaneous</TableCell>
                      <TableCell align="right">{formatCurrency(userData.other_sources?.other_misc)}</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
              
              {userData.regime === 'old' && (
                <>
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
                          <TableCell>Section 80C</TableCell>
                          <TableCell align="right">{formatCurrency(userData.deductions?.section_80c)}</TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell>Section 80D</TableCell>
                          <TableCell align="right">{formatCurrency(userData.deductions?.section_80d)}</TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell>Section 24B</TableCell>
                          <TableCell align="right">{formatCurrency(userData.deductions?.section_24b)}</TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell>Section 80E</TableCell>
                          <TableCell align="right">{formatCurrency(userData.deductions?.section_80e)}</TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell>Section 80G</TableCell>
                          <TableCell align="right">{formatCurrency(userData.deductions?.section_80g)}</TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell>Section 80TTA</TableCell>
                          <TableCell align="right">{formatCurrency(userData.deductions?.section_80tta)}</TableCell>
                        </TableRow>
                      </TableBody>
                    </Table>
                  </TableContainer>
                </>
              )}
            </Paper>
          </Grid>
          
          {/* Tax Breakup Section */}
          <Grid item xs={12}>
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
                    <TableRow>
                      <TableCell>Base Tax</TableCell>
                      <TableCell align="right">{formatCurrency(userData.tax_breakup?.base_tax)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Tax after Rebate</TableCell>
                      <TableCell align="right">{formatCurrency(userData.tax_breakup?.tax_after_rebate)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Surcharge</TableCell>
                      <TableCell align="right">{formatCurrency(userData.tax_breakup?.surcharge)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Cess</TableCell>
                      <TableCell align="right">{formatCurrency(userData.tax_breakup?.cess)}</TableCell>
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
          </Grid>
        </Grid>
      </Box>
    );
  };

  return (
    <PageLayout title="Taxation Dashboard">
      <Box sx={{ p: 3 }}>
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
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={4}>
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
              </Grid>
              <Grid item xs={12} sm={4}>
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
              </Grid>
              <Grid item xs={12} sm={4}>
                <Button 
                  variant="outlined" 
                  color="primary" 
                  fullWidth
                  onClick={fetchTaxationData}
                  sx={{ height: 56 }}
                >
                  Refresh Data
                </Button>
              </Grid>
            </Grid>
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
                onClick={() => navigate('/taxation/employee-selection')} 
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