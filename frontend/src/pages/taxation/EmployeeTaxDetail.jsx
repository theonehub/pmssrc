import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Grid,
  Card,
  CardContent,
  Divider,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  MenuItem,
  Select,
  FormControl,
  InputLabel
} from '@mui/material';
import { useNavigate, useParams } from 'react-router-dom';
import { getTaxationByEmpId, updateTaxPayment, updateFilingStatus } from '../../services/taxationService';
import { getUserRole } from '../../utils/auth';
import PageLayout from '../../layout/PageLayout';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';

const EmployeeTaxDetail = () => {
  const { empId } = useParams();
  const navigate = useNavigate();
  const userRole = getUserRole();
  const isAdmin = userRole === 'admin' || userRole === 'superadmin';

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [taxationData, setTaxationData] = useState(null);
  
  // Payment dialog
  const [paymentDialogOpen, setPaymentDialogOpen] = useState(false);
  const [paymentAmount, setPaymentAmount] = useState(0);
  
  // Filing status dialog
  const [statusDialogOpen, setStatusDialogOpen] = useState(false);
  const [selectedStatus, setSelectedStatus] = useState('');

  const filingStatuses = [
    { value: "draft", label: "Draft" },
    { value: "filed", label: "Filed" },
    { value: "approved", label: "Approved" },
    { value: "rejected", label: "Rejected" },
    { value: "pending", label: "Pending" }
  ];

  useEffect(() => {
    fetchTaxationData();
  }, [empId]);

  const fetchTaxationData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getTaxationByEmpId(empId);
      setTaxationData(response);
    } catch (err) {
      console.error('Error fetching taxation data:', err);
      setError('Failed to load taxation data. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Get total value of perquisites
  const calculatePerquisitesTotal = (perquisites) => {
    if (!perquisites) return 0;
    
    // Since the perquisites is an object containing various perquisite values,
    // we need to determine its total value
    return Object.values(perquisites)
      .filter(value => typeof value === 'number')
      .reduce((sum, value) => sum + value, 0);
  };

  // Format currency
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount || 0);
  };

  // Handle opening payment dialog
  const handleOpenPaymentDialog = () => {
    setPaymentAmount(0);
    setPaymentDialogOpen(true);
  };

  // Handle payment submission
  const handlePaymentSubmit = async () => {
    try {
      setLoading(true);
      await updateTaxPayment(empId, paymentAmount);
      setPaymentDialogOpen(false);
      setSuccess('Payment recorded successfully');
      fetchTaxationData();
    } catch (err) {
      console.error('Error updating payment:', err);
      setError('Failed to record payment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Handle opening status dialog
  const handleOpenStatusDialog = () => {
    setSelectedStatus(taxationData?.filing_status || '');
    setStatusDialogOpen(true);
  };

  // Handle status update submission
  const handleStatusSubmit = async () => {
    try {
      setLoading(true);
      await updateFilingStatus(empId, selectedStatus);
      setStatusDialogOpen(false);
      setSuccess('Filing status updated successfully');
      fetchTaxationData();
    } catch (err) {
      console.error('Error updating filing status:', err);
      setError('Failed to update filing status. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Handle navigating to edit page
  const handleEditDeclaration = () => {
    navigate(`/taxation/declaration/${empId}`);
  };

  // Helper function to get color for filing status
  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'draft': return '#e0e0e0';
      case 'filed': return '#bbdefb';
      case 'approved': return '#c8e6c9';
      case 'rejected': return '#ffcdd2';
      case 'pending': return '#fff9c4';
      default: return '#e0e0e0';
    }
  };

  if (loading) {
    return (
      <PageLayout title="Employee Tax Details">
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '70vh' }}>
          <CircularProgress />
        </Box>
      </PageLayout>
    );
  }

  if (error) {
    return (
      <PageLayout title="Employee Tax Details">
        <Box sx={{ p: 3 }}>
          <Alert severity="error">{error}</Alert>
          <Box sx={{ mt: 2 }}>
            <Button variant="outlined" onClick={() => navigate('/taxation')}>
              Back to Dashboard
            </Button>
          </Box>
        </Box>
      </PageLayout>
    );
  }

  return (
    <PageLayout title="Employee Tax Details">
      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            Employee Tax Details
          </Typography>
          <Box>
            <Button 
              variant="outlined" 
              color="primary" 
              onClick={() => navigate('/taxation')}
              sx={{ mr: 1 }}
            >
              Back to Dashboard
            </Button>
            
            {isAdmin && (
              <Button 
                variant="contained" 
                color="primary" 
                onClick={handleEditDeclaration}
              >
                Edit Declaration
              </Button>
            )}
          </Box>
        </Box>

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

        {taxationData && (
          <Grid container spacing={3}>
            {/* Employee & Tax Info */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3, mb: 3 }}>
                <Typography variant="h5" gutterBottom>Employee Information</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="subtitle1">Employee ID:</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body1">{taxationData.emp_id}</Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="subtitle1">Tax Year:</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body1">{taxationData.tax_year}</Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="subtitle1">Tax Regime:</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body1">
                      {taxationData.regime === 'old' ? 'Old Regime' : 'New Regime'}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6}>
                    <Typography variant="subtitle1">Filing Status:</Typography>
                  </Grid>
                  <Grid item xs={6}>
                                      <Box sx={{ 
                    display: 'inline-block', 
                    bgcolor: getStatusColor(taxationData.filing_status), 
                    px: 1, 
                    py: 0.5, 
                    borderRadius: 1 
                  }}>
                    {(taxationData.filing_status?.charAt(0)?.toUpperCase() + taxationData.filing_status?.slice(1)) || 'N/A'}
                  </Box>
                  </Grid>
                </Grid>
              </Paper>

              <Paper sx={{ p: 3, mb: 3 }}>
                <Typography variant="h5" gutterBottom>Tax Summary</Typography>
                <Box sx={{ height: 300, mt: 2, mb: 4 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={[
                        { name: 'Total Tax', amount: taxationData.total_tax || 0, color: '#1976d2' },
                        { name: 'Tax Paid', amount: taxationData.tax_paid || 0, color: '#2e7d32' },
                        { name: 'Tax Due', amount: taxationData.tax_due || 0, color: '#d32f2f' },
                        { name: 'Tax Refundable', amount: taxationData.tax_refundable || 0, color: '#0288d1' },
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
                          { name: 'Total Tax', amount: taxationData.total_tax || 0, color: '#1976d2' },
                          { name: 'Tax Paid', amount: taxationData.tax_paid || 0, color: '#2e7d32' },
                          { name: 'Tax Due', amount: taxationData.tax_due || 0, color: '#d32f2f' },
                          { name: 'Tax Refundable', amount: taxationData.tax_refundable || 0, color: '#0288d1' },
                        ].map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </Box>
                
                <Divider sx={{ my: 2 }} />
                {isAdmin && (
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
                    <Button 
                      variant="outlined" 
                      color="primary"
                      onClick={handleOpenPaymentDialog}
                    >
                      Record Payment
                    </Button>
                    <Button 
                      variant="outlined" 
                      color="secondary"
                      onClick={handleOpenStatusDialog}
                    >
                      Update Status
                    </Button>
                  </Box>
                )}
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
                        <TableCell align="right">{formatCurrency(taxationData.salary?.basic)}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>HRA</TableCell>
                        <TableCell align="right">{formatCurrency(taxationData.salary?.hra)}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Special Allowance</TableCell>
                        <TableCell align="right">{formatCurrency(taxationData.salary?.special_allowance)}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Bonus</TableCell>
                        <TableCell align="right">{formatCurrency(taxationData.salary?.bonus)}</TableCell>
                      </TableRow>
                      {taxationData.salary?.perquisites && (
                        <TableRow>
                          <TableCell>Perquisites</TableCell>
                          <TableCell align="right">
                            {formatCurrency(calculatePerquisitesTotal(taxationData.salary.perquisites))}
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
                            (taxationData.other_sources?.interest_savings || 0) +
                            (taxationData.other_sources?.interest_fd || 0) +
                            (taxationData.other_sources?.interest_rd || 0)
                          )}
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Dividend Income</TableCell>
                        <TableCell align="right">{formatCurrency(taxationData.other_sources?.dividend_income)}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Rental Income</TableCell>
                        <TableCell align="right">{formatCurrency(taxationData.other_sources?.rental_income)}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Capital Gains</TableCell>
                        <TableCell align="right">
                          {formatCurrency(
                            (taxationData.capital_gains?.stcg_111a || 0) +
                            (taxationData.capital_gains?.ltcg_112a || 0)
                          )}
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Other Miscellaneous</TableCell>
                        <TableCell align="right">{formatCurrency(taxationData.other_sources?.other_misc)}</TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
                
                {taxationData.regime === 'old' && (
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
                          {/* Section 80C group */}
                          <TableRow><TableCell colSpan={2}><b>Section 80C (Total up to 1,50,000)</b></TableCell></TableRow>
                          <TableRow><TableCell>LIC Premium</TableCell><TableCell align="right">{formatCurrency(taxationData.deductions?.section_80c_lic)}</TableCell></TableRow>
                          <TableRow><TableCell>EPF</TableCell><TableCell align="right">{formatCurrency(taxationData.deductions?.section_80c_epf)}</TableCell></TableRow>
                          <TableRow><TableCell>Sukanya Samridhi</TableCell><TableCell align="right">{formatCurrency(taxationData.deductions?.section_80c_ssp)}</TableCell></TableRow>
                          <TableRow><TableCell>NSC</TableCell><TableCell align="right">{formatCurrency(taxationData.deductions?.section_80c_nsc)}</TableCell></TableRow>
                          <TableRow><TableCell>ULIP</TableCell><TableCell align="right">{formatCurrency(taxationData.deductions?.section_80c_ulip)}</TableCell></TableRow>
                          <TableRow><TableCell>Tax Saving MF</TableCell><TableCell align="right">{formatCurrency(taxationData.deductions?.section_80c_tsmf)}</TableCell></TableRow>
                          <TableRow><TableCell>Tuition Fees</TableCell><TableCell align="right">{formatCurrency(taxationData.deductions?.section_80c_tffte2c)}</TableCell></TableRow>
                          <TableRow><TableCell>Principal on Home Loan</TableCell><TableCell align="right">{formatCurrency(taxationData.deductions?.section_80c_paphl)}</TableCell></TableRow>
                          <TableRow><TableCell>Stamp Duty</TableCell><TableCell align="right">{formatCurrency(taxationData.deductions?.section_80c_sdpphp)}</TableCell></TableRow>
                          <TableRow><TableCell>Tax Saving FD</TableCell><TableCell align="right">{formatCurrency(taxationData.deductions?.section_80c_tsfdsb)}</TableCell></TableRow>
                          <TableRow><TableCell>SCSS</TableCell><TableCell align="right">{formatCurrency(taxationData.deductions?.section_80c_scss)}</TableCell></TableRow>
                          <TableRow><TableCell>Others (80C)</TableCell><TableCell align="right">{formatCurrency(taxationData.deductions?.section_80c_others)}</TableCell></TableRow>
                          <TableRow><TableCell>80CCC Pension</TableCell><TableCell align="right">{formatCurrency(taxationData.deductions?.section_80ccc_ppic)}</TableCell></TableRow>
                          <TableRow><TableCell>80CCD(1) NPS</TableCell><TableCell align="right">{formatCurrency(taxationData.deductions?.section_80ccd_1_nps)}</TableCell></TableRow>
                          <TableRow><TableCell>80CCD(1B) NPS Additional</TableCell><TableCell align="right">{formatCurrency(taxationData.deductions?.section_80ccd_1b_additional)}</TableCell></TableRow>
                          <TableRow><TableCell>80CCD(2) Employer NPS</TableCell><TableCell align="right">{formatCurrency(taxationData.deductions?.section_80ccd_2_enps)}</TableCell></TableRow>
                          {/* Section 80D */}
                          <TableRow><TableCell colSpan={2}><b>Section 80D</b></TableCell></TableRow>
                          <TableRow><TableCell>Health Insurance (Self/Family)</TableCell><TableCell align="right">{formatCurrency(taxationData.deductions?.section_80d_hisf)}</TableCell></TableRow>
                          <TableRow><TableCell>Preventive Health Checkup</TableCell><TableCell align="right">{formatCurrency(taxationData.deductions?.section_80d_phcs)}</TableCell></TableRow>
                          <TableRow><TableCell>Health Insurance (Parents)</TableCell><TableCell align="right">{formatCurrency(taxationData.deductions?.section_80d_hi_parent)}</TableCell></TableRow>
                          {/* Section 80DD/80DDB/80E/80EEB/80G/80GGC/80U */}
                          <TableRow><TableCell colSpan={2}><b>Other Deductions</b></TableCell></TableRow>
                          <TableRow><TableCell>80DD (Disability Dependent)</TableCell><TableCell align="right">{formatCurrency(taxationData.deductions?.section_80dd)}</TableCell></TableRow>
                          <TableRow><TableCell>80DDB (Specified Diseases)</TableCell><TableCell align="right">{formatCurrency(taxationData.deductions?.section_80ddb)}</TableCell></TableRow>
                          <TableRow><TableCell>80E (Education Loan Interest)</TableCell><TableCell align="right">{formatCurrency(taxationData.deductions?.section_80e_interest)}</TableCell></TableRow>
                          <TableRow><TableCell>80EEB (EV Loan Interest)</TableCell><TableCell align="right">{formatCurrency(taxationData.deductions?.section_80eeb)}</TableCell></TableRow>
                          {/* Section 80G Donations */}
                          <TableRow><TableCell colSpan={2}><b>Section 80G (Donations)</b></TableCell></TableRow>
                          <TableRow><TableCell>100% WO QL</TableCell><TableCell align="right">{formatCurrency(taxationData.deductions?.section_80g_100_wo_ql)}</TableCell></TableRow>
                          <TableRow><TableCell>50% WO QL</TableCell><TableCell align="right">{formatCurrency(taxationData.deductions?.section_80g_50_wo_ql)}</TableCell></TableRow>
                          <TableRow><TableCell>100% QL</TableCell><TableCell align="right">{formatCurrency(taxationData.deductions?.section_80g_100_ql)}</TableCell></TableRow>
                          <TableRow><TableCell>50% QL</TableCell><TableCell align="right">{formatCurrency(taxationData.deductions?.section_80g_50_ql)}</TableCell></TableRow>
                          <TableRow><TableCell>80GGC (Political Party)</TableCell><TableCell align="right">{formatCurrency(taxationData.deductions?.section_80ggc)}</TableCell></TableRow>
                          {/* Section 80U */}
                          <TableRow><TableCell colSpan={2}><b>Section 80U (Disability)</b></TableCell></TableRow>
                          <TableRow><TableCell>80U</TableCell><TableCell align="right">{formatCurrency(taxationData.deductions?.section_80u)}</TableCell></TableRow>
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </>
                )}
              </Paper>
            </Grid>

            {/* Tax Breakup */}
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
                        <TableCell align="right">{formatCurrency(taxationData.tax_breakup?.base_tax)}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Tax after Rebate</TableCell>
                        <TableCell align="right">{formatCurrency(taxationData.tax_breakup?.tax_after_rebate)}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Surcharge</TableCell>
                        <TableCell align="right">{formatCurrency(taxationData.tax_breakup?.surcharge)}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Cess</TableCell>
                        <TableCell align="right">{formatCurrency(taxationData.tax_breakup?.cess)}</TableCell>
                      </TableRow>
                      <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                        <TableCell><Typography variant="subtitle1">Total Tax</Typography></TableCell>
                        <TableCell align="right">
                          <Typography variant="subtitle1">{formatCurrency(taxationData.total_tax)}</Typography>
                        </TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </Paper>
            </Grid>
          </Grid>
        )}

        {/* Payment Dialog */}
        <Dialog open={paymentDialogOpen} onClose={() => setPaymentDialogOpen(false)}>
          <DialogTitle>Record Tax Payment</DialogTitle>
          <DialogContent>
            <DialogContentText>
              Enter the tax amount paid by the employee.
            </DialogContentText>
            <TextField
              autoFocus
              margin="dense"
              label="Payment Amount"
              type="number"
              fullWidth
              value={paymentAmount}
              onChange={(e) => setPaymentAmount(parseFloat(e.target.value) || 0)}
              InputProps={{ startAdornment: '₹' }}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setPaymentDialogOpen(false)}>Cancel</Button>
            <Button 
              onClick={handlePaymentSubmit} 
              variant="contained" 
              color="primary"
              disabled={!paymentAmount || paymentAmount <= 0}
            >
              Record Payment
            </Button>
          </DialogActions>
        </Dialog>

        {/* Status Dialog */}
        <Dialog open={statusDialogOpen} onClose={() => setStatusDialogOpen(false)}>
          <DialogTitle>Update Filing Status</DialogTitle>
          <DialogContent>
            <DialogContentText>
              Update the filing status for this tax declaration.
            </DialogContentText>
            <FormControl fullWidth sx={{ mt: 2 }}>
              <InputLabel id="filing-status-label">Filing Status</InputLabel>
              <Select
                labelId="filing-status-label"
                value={selectedStatus}
                label="Filing Status"
                onChange={(e) => setSelectedStatus(e.target.value)}
              >
                {filingStatuses.map(status => (
                  <MenuItem key={status.value} value={status.value}>{status.label}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setStatusDialogOpen(false)}>Cancel</Button>
            <Button 
              onClick={handleStatusSubmit} 
              variant="contained" 
              color="primary"
              disabled={!selectedStatus}
            >
              Update Status
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </PageLayout>
  );
};

export default EmployeeTaxDetail; 