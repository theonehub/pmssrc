import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Grid
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import { formatCurrency } from './utils/taxationUtils';
import { ArrowBack, Download } from '@mui/icons-material';

interface MonthlyProjectionData {
  employee_id: string;
  month: number;
  year: number;
  basic_salary: number;
  da: number;
  hra: number;
  special_allowance: number;
  transport_allowance: number;
  medical_allowance: number;
  bonus: number;
  commission: number;
  other_allowances: number;
  epf_employee: number;
  esi_employee: number;
  professional_tax: number;
  advance_deduction: number;
  loan_deduction: number;
  other_deductions: number;
  gross_salary: number;
  net_salary: number;
  total_deductions: number;
  tds: number;
  annual_gross_salary: number;
  annual_tax_liability: number;
  tax_regime: string;
  effective_working_days: number;
  lwp_days: number;
  status: string;
  notes: string;
  remarks: string;
}

/**
 * Monthly Projections Component
 * Displays detailed monthly salary breakdown and projections based on tax calculation
 */
const MonthlyProjections: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  
  // Get data from navigation state
  const { monthlyPayroll } = location.state || {};
  
  // If no data is available, redirect back
  if (!monthlyPayroll) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h6" color="error" gutterBottom>
          No projection data available
        </Typography>
        <Button 
          variant="contained" 
          onClick={() => navigate('/taxation/declaration')}
          startIcon={<ArrowBack />}
        >
          Back to Tax Declaration
        </Button>
      </Box>
    );
  }

  const data: MonthlyProjectionData = monthlyPayroll;

  // Helper function to get month name
  const getMonthName = (month: number): string => {
    const months = [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ];
    return months[month - 1] || 'Unknown';
  };

  // Helper function to get status color
  const getStatusColor = (status: string): string => {
    switch (status.toLowerCase()) {
      case 'approved': return 'success';
      case 'pending': return 'warning';
      case 'rejected': return 'error';
      default: return 'default';
    }
  };

  // Salary components data
  const salaryComponents = [
    { label: 'Basic Salary', value: data.basic_salary, type: 'earning' },
    { label: 'Dearness Allowance (DA)', value: data.da, type: 'earning' },
    { label: 'HRA', value: data.hra, type: 'earning' },
    { label: 'Special Allowance', value: data.special_allowance, type: 'earning' },
    { label: 'Transport Allowance', value: data.transport_allowance, type: 'earning' },
    { label: 'Medical Allowance', value: data.medical_allowance, type: 'earning' },
    { label: 'Bonus', value: data.bonus, type: 'earning' },
    { label: 'Commission', value: data.commission, type: 'earning' },
    { label: 'Other Allowances', value: data.other_allowances, type: 'earning' }
  ];

  // Deduction components data
  const deductionComponents = [
    { label: 'EPF (Employee)', value: data.epf_employee, type: 'deduction' },
    { label: 'ESI (Employee)', value: data.esi_employee, type: 'deduction' },
    { label: 'Professional Tax', value: data.professional_tax, type: 'deduction' },
    { label: 'TDS', value: data.tds, type: 'deduction' },
    { label: 'Advance Deduction', value: data.advance_deduction, type: 'deduction' },
    { label: 'Loan Deduction', value: data.loan_deduction, type: 'deduction' },
    { label: 'Other Deductions', value: data.other_deductions, type: 'deduction' }
  ];

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Monthly Salary Projection
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            {getMonthName(data.month)} {data.year} - Employee ID: {data.employee_id}
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            onClick={() => navigate(-1)}
            startIcon={<ArrowBack />}
          >
            Back
          </Button>
          <Button
            variant="contained"
            startIcon={<Download />}
            onClick={() => window.print()}
          >
            Download
          </Button>
        </Box>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: '#e3f2fd' }}>
            <CardContent>
              <Typography variant="h6" color="primary">Gross Salary</Typography>
              <Typography variant="h4">{formatCurrency(data.gross_salary)}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: '#ffebee' }}>
            <CardContent>
              <Typography variant="h6" color="error">Total Deductions</Typography>
              <Typography variant="h4">{formatCurrency(data.total_deductions)}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: '#e8f5e8' }}>
            <CardContent>
              <Typography variant="h6" color="success.main">Net Salary</Typography>
              <Typography variant="h4">{formatCurrency(data.net_salary)}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: '#fff3e0' }}>
            <CardContent>
              <Typography variant="h6" color="text.secondary">TDS</Typography>
              <Typography variant="h4">{formatCurrency(data.tds)}</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Details Section */}
      <Grid container spacing={3}>
        {/* Left Column - Earnings */}
        <Grid item xs={12} md={6}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" color="primary" gutterBottom>
                Earnings Breakdown
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell><strong>Component</strong></TableCell>
                      <TableCell align="right"><strong>Amount</strong></TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {salaryComponents
                      .filter(component => component.value > 0)
                      .map((component, index) => (
                        <TableRow key={index}>
                          <TableCell>{component.label}</TableCell>
                          <TableCell align="right">
                            {formatCurrency(component.value)}
                          </TableCell>
                        </TableRow>
                      ))}
                    <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                      <TableCell><strong>Total Earnings</strong></TableCell>
                      <TableCell align="right">
                        <strong>{formatCurrency(data.gross_salary)}</strong>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Right Column - Deductions */}
        <Grid item xs={12} md={6}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" color="error" gutterBottom>
                Deductions Breakdown
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell><strong>Component</strong></TableCell>
                      <TableCell align="right"><strong>Amount</strong></TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {deductionComponents
                      .filter(component => component.value > 0)
                      .map((component, index) => (
                        <TableRow key={index}>
                          <TableCell>{component.label}</TableCell>
                          <TableCell align="right">
                            {formatCurrency(component.value)}
                          </TableCell>
                        </TableRow>
                      ))}
                    <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                      <TableCell><strong>Total Deductions</strong></TableCell>
                      <TableCell align="right">
                        <strong>{formatCurrency(data.total_deductions)}</strong>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Annual Projections */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" color="primary" gutterBottom>
            Annual Projections
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center', p: 2, bgcolor: '#f8f9fa', borderRadius: 1 }}>
                <Typography variant="body2" color="text.secondary">Annual Gross Salary</Typography>
                <Typography variant="h5">{formatCurrency(data.annual_gross_salary)}</Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center', p: 2, bgcolor: '#f8f9fa', borderRadius: 1 }}>
                <Typography variant="body2" color="text.secondary">Annual Tax Liability</Typography>
                <Typography variant="h5">{formatCurrency(data.annual_tax_liability)}</Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center', p: 2, bgcolor: '#f8f9fa', borderRadius: 1 }}>
                <Typography variant="body2" color="text.secondary">Tax Regime</Typography>
                <Typography variant="h5">{data.tax_regime.toUpperCase()}</Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center', p: 2, bgcolor: '#f8f9fa', borderRadius: 1 }}>
                <Typography variant="body2" color="text.secondary">Effective Tax Rate</Typography>
                <Typography variant="h5">
                  {((data.annual_tax_liability / data.annual_gross_salary) * 100).toFixed(1)}%
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Additional Information */}
      <Card>
        <CardContent>
          <Typography variant="h6" color="primary" gutterBottom>
            Additional Information
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">Working Days</Typography>
              <Typography variant="h6">{data.effective_working_days}</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">LWP Days</Typography>
              <Typography variant="h6">{data.lwp_days}</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">Status</Typography>
              <Chip 
                label={data.status.charAt(0).toUpperCase() + data.status.slice(1)} 
                color={getStatusColor(data.status) as any}
                size="small"
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">Net Salary %</Typography>
              <Typography variant="h6">
                {((data.net_salary / data.gross_salary) * 100).toFixed(1)}%
              </Typography>
            </Grid>
          </Grid>
          
          {data.notes && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" color="text.secondary">Notes:</Typography>
              <Typography variant="body2">{data.notes}</Typography>
            </Box>
          )}
          
          {data.remarks && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" color="text.secondary">Remarks:</Typography>
              <Typography variant="body2">{data.remarks}</Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default MonthlyProjections; 