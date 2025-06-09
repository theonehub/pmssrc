import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
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
  InputLabel,
  SelectChangeEvent,
  Divider
} from '@mui/material';
import { useNavigate, useParams } from 'react-router-dom';
import { getTaxationByEmpId, updateTaxPayment, updateFilingStatus } from '../../services/taxationService';
import { getUserRole } from '../../utils/auth';
import PageLayout from '../../layout/PageLayout';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';

// Local interface for taxation data
interface LocalTaxationData {
  employee_id: string;
  employee_name?: string;
  pan_number?: string;
  tax_regime?: string;
  assessment_year?: string;
  filing_status?: string;
  total_tax: number;
  tax_paid?: number;
  tax_due?: number;
  tax_refundable?: number;
  taxable_income?: number;
  tax_before_rebate?: number;
  tax_after_rebate?: number;
  surcharge?: number;
  cess?: number;
  tax_liability?: number;
  other_income?: {
    interest_income?: number;
    dividend_income?: number;
    other_income?: number;
  };
  salary?: {
    basic_salary?: number;
    hra?: number;
    special_allowance?: number;
    bonus?: number;
    perquisites?: Record<string, number>;
  };
  capital_gains?: {
    stcg_111a?: number;
    ltcg_112a?: number;
  };
  deductions?: {
    section_80c?: {
      lic_premium?: number;
      epf?: number;
      ppf?: number;
      nsc?: number;
      elss?: number;
      others?: number;
    };
    section_80d?: {
      health_insurance?: number;
    };
    section_80e?: {
      education_loan_interest?: number;
    };
    section_80g?: {
      donations?: number;
    };
  };
}

// Type definitions
interface ChartData {
  name: string;
  amount: number;
  color: string;
}

interface FilingStatusOption {
  value: string;
  label: string;
}

const filingStatusOptions: FilingStatusOption[] = [
  { value: "draft", label: "Draft" },
  { value: "filed", label: "Filed" },
  { value: "approved", label: "Approved" },
  { value: "rejected", label: "Rejected" },
  { value: "pending", label: "Pending" }
];

const EmployeeTaxDetail: React.FC = () => {
  const { empId } = useParams<{ empId: string }>();
  const navigate = useNavigate();
  const userRole = getUserRole();
  const isAdmin = userRole === 'admin' || userRole === 'superadmin';

  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [taxationData, setTaxationData] = useState<LocalTaxationData | null>(null);
  
  // Payment dialog
  const [paymentDialogOpen, setPaymentDialogOpen] = useState<boolean>(false);
  const [paymentAmount, setPaymentAmount] = useState<number>(0);
  
  // Filing status dialog
  const [statusDialogOpen, setStatusDialogOpen] = useState<boolean>(false);
  const [selectedStatus, setSelectedStatus] = useState<string>('');

  const fetchTaxationData = useCallback(async (): Promise<void> => {
    if (!empId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await getTaxationByEmpId(empId);
      // Convert the response to our local interface
      const extendedData: LocalTaxationData = {
        employee_id: response.employee_id,
        employee_name: (response as any).employee_name || 'N/A',
        pan_number: (response as any).pan_number || '',
        tax_regime: (response as any).tax_regime || response.regime,
        assessment_year: (response as any).assessment_year || response.tax_year,
        filing_status: response.filing_status,
        total_tax: (response as any).tax_liability || (response as any).total_tax || 0,
        tax_paid: response.tax_paid || 0,
        tax_due: response.tax_due || 0,
        tax_refundable: response.tax_refundable || 0,
        taxable_income: (response as any).taxable_income || 0,
        tax_before_rebate: (response as any).tax_before_rebate || 0,
        tax_after_rebate: (response as any).tax_after_rebate || 0,
        surcharge: (response as any).surcharge || 0,
        cess: (response as any).cess || 0,
        other_income: (response as any).other_income || {},
        salary: {
          basic_salary: response.salary?.basic || 0,
          hra: response.salary?.hra || 0,
          special_allowance: response.salary?.special_allowance || 0,
          bonus: response.salary?.bonus || 0,
          perquisites: (response.salary?.perquisites as any) || {}
        },
        capital_gains: response.capital_gains || {},
        deductions: (response as any).deductions || {}
      };
      setTaxationData(extendedData);
    } catch (err) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error fetching taxation data:', err);
      }
      setError('Failed to load taxation data. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [empId]);

  useEffect(() => {
    if (empId) {
      fetchTaxationData();
    }
  }, [empId, fetchTaxationData]);

  // Format currency
  const formatCurrency = (amount?: number): string => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount || 0);
  };

  // Handle opening payment dialog
  const handleOpenPaymentDialog = (): void => {
    setPaymentAmount(0);
    setPaymentDialogOpen(true);
  };

  // Handle payment submission
  const handlePaymentSubmit = async (): Promise<void> => {
    if (!empId) return;
    
    try {
      setLoading(true);
      await updateTaxPayment(empId, paymentAmount);
      setPaymentDialogOpen(false);
      setSuccess('Payment recorded successfully');
      fetchTaxationData();
    } catch (err) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error updating payment:', err);
      }
      setError('Failed to record payment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Handle opening status dialog
  const handleOpenStatusDialog = (): void => {
    setSelectedStatus(taxationData?.filing_status || '');
    setStatusDialogOpen(true);
  };

  // Handle status update submission
  const handleStatusSubmit = async (): Promise<void> => {
    if (!empId) return;
    
    try {
      setLoading(true);
      await updateFilingStatus(empId, selectedStatus as any);
      setStatusDialogOpen(false);
      setSuccess('Filing status updated successfully');
      fetchTaxationData();
    } catch (err) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error updating filing status:', err);
      }
      setError('Failed to update filing status. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Handle navigating to edit page
  const handleEditDeclaration = (): void => {
    navigate(`/api/v2/taxation/declaration/${empId}`);
  };

  const handlePaymentAmountChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setPaymentAmount(parseFloat(event.target.value) || 0);
  };

  const handleStatusChange = (event: SelectChangeEvent<string>): void => {
    setSelectedStatus(event.target.value);
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
            <Button variant="outlined" onClick={() => navigate('/api/v2/taxation')}>
              Back to Dashboard
            </Button>
          </Box>
        </Box>
      </PageLayout>
    );
  }

  const chartData: ChartData[] = [
    { name: 'Total Tax', amount: taxationData?.total_tax || 0, color: '#1976d2' },
    { name: 'Tax Paid', amount: taxationData?.tax_paid || 0, color: '#2e7d32' },
    { name: 'Tax Due', amount: taxationData?.tax_due || 0, color: '#d32f2f' },
    { name: 'Tax Refundable', amount: taxationData?.tax_refundable || 0, color: '#0288d1' },
  ];

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
              onClick={() => navigate('/api/v2/taxation')}
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
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3, mb: 3 }}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Employee Information
              </Typography>
              <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Employee ID
                  </Typography>
                  <Typography variant="body1" fontWeight="bold">
                    {taxationData.employee_id}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Name
                  </Typography>
                  <Typography variant="body1" fontWeight="bold">
                    {taxationData.employee_name}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    PAN Number
                  </Typography>
                  <Typography variant="body1" fontWeight="bold">
                    {taxationData.pan_number || 'Not provided'}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Tax Regime
                  </Typography>
                  <Typography variant="body1" fontWeight="bold">
                    {taxationData.tax_regime}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Filing Status
                  </Typography>
                  <Typography variant="body1" fontWeight="bold">
                    {taxationData.filing_status}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Assessment Year
                  </Typography>
                  <Typography variant="body1" fontWeight="bold">
                    {taxationData.assessment_year}
                  </Typography>
                </Box>
              </Box>
            </Paper>

            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Tax Summary
              </Typography>
              <Box sx={{ height: 300, mt: 2, mb: 4 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={chartData}
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
                        }).format(value as number)
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
          </Box>
        )}

        {/* Income & Deduction Details */}
        <Box sx={{ mb: 3 }}>
          <Paper sx={{ p: 3 }}>
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
                    <TableCell align="right">{formatCurrency(taxationData?.salary?.basic_salary)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>HRA</TableCell>
                    <TableCell align="right">{formatCurrency(taxationData?.salary?.hra)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Special Allowance</TableCell>
                    <TableCell align="right">{formatCurrency(taxationData?.salary?.special_allowance)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Bonus</TableCell>
                    <TableCell align="right">{formatCurrency(taxationData?.salary?.bonus)}</TableCell>
                  </TableRow>
                  {taxationData?.salary?.perquisites && (
                    <TableRow>
                      <TableCell>Perquisites</TableCell>
                      <TableCell align="right">
                        {formatCurrency(Object.values(taxationData?.salary?.perquisites || {}).reduce((sum, val) => sum + val, 0))}
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
                        (taxationData?.other_income?.interest_income || 0)
                      )}
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Dividend Income</TableCell>
                    <TableCell align="right">{formatCurrency(taxationData?.other_income?.dividend_income)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Capital Gains</TableCell>
                    <TableCell align="right">
                      {formatCurrency(
                        (taxationData?.capital_gains?.stcg_111a || 0) +
                        (taxationData?.capital_gains?.ltcg_112a || 0)
                      )}
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Other Income</TableCell>
                    <TableCell align="right">{formatCurrency(taxationData?.other_income?.other_income)}</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
            
            {taxationData?.tax_regime === 'old' && (
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
                      <TableRow><TableCell>LIC Premium</TableCell><TableCell align="right">{formatCurrency(taxationData?.deductions?.section_80c?.lic_premium)}</TableCell></TableRow>
                      <TableRow><TableCell>EPF</TableCell><TableCell align="right">{formatCurrency(taxationData?.deductions?.section_80c?.epf)}</TableCell></TableRow>
                      <TableRow><TableCell>PPF</TableCell><TableCell align="right">{formatCurrency(taxationData?.deductions?.section_80c?.ppf)}</TableCell></TableRow>
                      <TableRow><TableCell>NSC</TableCell><TableCell align="right">{formatCurrency(taxationData?.deductions?.section_80c?.nsc)}</TableCell></TableRow>
                      <TableRow><TableCell>ELSS</TableCell><TableCell align="right">{formatCurrency(taxationData?.deductions?.section_80c?.elss)}</TableCell></TableRow>
                      <TableRow><TableCell>Others</TableCell><TableCell align="right">{formatCurrency(taxationData?.deductions?.section_80c?.others)}</TableCell></TableRow>
                      
                      {/* Other sections */}
                      <TableRow><TableCell colSpan={2}><b>Other Deductions</b></TableCell></TableRow>
                      <TableRow><TableCell>80D - Health Insurance</TableCell><TableCell align="right">{formatCurrency(taxationData?.deductions?.section_80d?.health_insurance)}</TableCell></TableRow>
                      <TableRow><TableCell>80E - Education Loan Interest</TableCell><TableCell align="right">{formatCurrency(taxationData?.deductions?.section_80e?.education_loan_interest)}</TableCell></TableRow>
                      <TableRow><TableCell>80G - Donations</TableCell><TableCell align="right">{formatCurrency(taxationData?.deductions?.section_80g?.donations)}</TableCell></TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </>
            )}
          </Paper>
        </Box>

        {/* Tax Breakup */}
        <Box sx={{ mb: 3 }}>
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
                    <TableCell>Taxable Income</TableCell>
                    <TableCell align="right">{formatCurrency(taxationData?.taxable_income)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Tax Before Rebate</TableCell>
                    <TableCell align="right">{formatCurrency(taxationData?.tax_before_rebate)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Tax After Rebate</TableCell>
                    <TableCell align="right">{formatCurrency(taxationData?.tax_after_rebate)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Surcharge</TableCell>
                    <TableCell align="right">{formatCurrency(taxationData?.surcharge)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Health & Education Cess</TableCell>
                    <TableCell align="right">{formatCurrency(taxationData?.cess)}</TableCell>
                  </TableRow>
                  <TableRow sx={{ backgroundColor: 'primary.light' }}>
                    <TableCell><strong>Total Tax Liability</strong></TableCell>
                    <TableCell align="right">
                      <Typography variant="subtitle1">{formatCurrency(taxationData?.total_tax)}</Typography>
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Box>

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
              onChange={handlePaymentAmountChange}
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
                onChange={handleStatusChange}
              >
                {filingStatusOptions.map((status) => (
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