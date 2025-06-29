import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Paper,
  Card,
  CardContent,
  Grid,
  CircularProgress,
  Alert,
  Button,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  ExpandMore as ExpandMoreIcon,
  AccountBalance as AccountBalanceIcon,
  Receipt as ReceiptIcon,
  Home as HomeIcon,
  TrendingUp as TrendingUpIcon,
  Business as BusinessIcon,
  Edit as EditIcon,
  CardGiftcard as CardGiftcardIcon
} from '@mui/icons-material';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { getUserRole } from '../../shared/utils/auth';
import { taxationApi } from '../../shared/api/taxationApi';
import { TaxRegime } from '../../shared/types/api';
import { CURRENT_TAX_YEAR } from '../../shared/constants/taxation';

interface ComponentSummary {
  id: string;
  name: string;
  icon: React.ReactElement;
  color: string;
  hasData: boolean;
  totalValue: number;
  details: Record<string, any>;
}

const ComponentsOverview: React.FC = () => {
  const { empId } = useParams<{ empId: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const userRole = getUserRole();
  
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [components, setComponents] = useState<ComponentSummary[]>([]);
  const [computedTax, setComputedTax] = useState<number>(0);
  const [taxLoading, setTaxLoading] = useState<boolean>(false);
  const [taxError, setTaxError] = useState<string | null>(null);
  
  const taxYear = searchParams.get('year') || CURRENT_TAX_YEAR;
  const isAdmin = userRole === 'admin' || userRole === 'superadmin';

  // 1. loadSalaryComponent
  const loadSalaryComponent = useCallback(async (): Promise<ComponentSummary | null> => {
    try {
      const response = await taxationApi.getComponent(empId!, taxYear, 'salary');
      const data = response?.component_data || response;
      
      const totalSalary = (data.basic_salary || 0) + 
                          (data.dearness_allowance || 0) + 
                          (data.hra_provided || 0) + 
                          (data.special_allowance || 0) + 
                          (data.bonus || 0) + 
                          (data.commission || 0);
      
      return {
        id: 'salary',
        name: 'Salary Income',
        icon: <AccountBalanceIcon />,
        color: 'primary',
        hasData: totalSalary > 0,
        totalValue: totalSalary,
        details: data
      };
    } catch (error) {
      return {
        id: 'salary',
        name: 'Salary Income',
        icon: <AccountBalanceIcon />,
        color: 'primary',
        hasData: false,
        totalValue: 0,
        details: {}
      };
    }
  }, [empId, taxYear]);

  // 2. loadDeductionsComponent
  const loadDeductionsComponent = useCallback(async (): Promise<ComponentSummary | null> => {
    try {
      const response = await taxationApi.getComponent(empId!, taxYear, 'deductions');
      const data = response?.component_data || response;
      
      const section80c = data.section_80c || {};
      const section80d = data.section_80d || {};
      
      const totalDeductions = Object.values(section80c).reduce((sum: number, val: any) => sum + (Number(val) || 0), 0) +
                             Object.values(section80d).reduce((sum: number, val: any) => sum + (Number(val) || 0), 0);
      
      return {
        id: 'deductions',
        name: 'Deductions',
        icon: <ReceiptIcon />,
        color: 'info',
        hasData: totalDeductions > 0,
        totalValue: totalDeductions,
        details: data
      };
    } catch (error) {
      return {
        id: 'deductions',
        name: 'Deductions',
        icon: <ReceiptIcon />,
        color: 'info',
        hasData: false,
        totalValue: 0,
        details: {}
      };
    }
  }, [empId, taxYear]);

  // 3. loadHousePropertyComponent
  const loadHousePropertyComponent = useCallback(async (): Promise<ComponentSummary | null> => {
    try {
      const response = await taxationApi.getComponent(empId!, taxYear, 'house_property_income');
      const data = response?.component_data || response;
      
      const totalValue = (data.annual_rent_received || 0);
      
      return {
        id: 'house_property_income',
        name: 'House Property',
        icon: <HomeIcon />,
        color: 'warning',
        hasData: totalValue > 0,
        totalValue: totalValue,
        details: data
      };
    } catch (error) {
      return {
        id: 'house_property_income',
        name: 'House Property',
        icon: <HomeIcon />,
        color: 'warning',
        hasData: false,
        totalValue: 0,
        details: {}
      };
    }
  }, [empId, taxYear]);

  // 4. loadCapitalGainsComponent
  const loadCapitalGainsComponent = useCallback(async (): Promise<ComponentSummary | null> => {
    try {
      const response = await taxationApi.getComponent(empId!, taxYear, 'capital_gains');
      const data = response?.component_data || response;
      
      const totalCapitalGains = (data.stcg_111a_equity_stt || 0) + 
                               (data.ltcg_112a_equity_stt || 0);
      
      return {
        id: 'capital_gains',
        name: 'Capital Gains',
        icon: <TrendingUpIcon />,
        color: 'success',
        hasData: totalCapitalGains > 0,
        totalValue: totalCapitalGains,
        details: data
      };
    } catch (error) {
      return {
        id: 'capital_gains',
        name: 'Capital Gains',
        icon: <TrendingUpIcon />,
        color: 'success',
        hasData: false,
        totalValue: 0,
        details: {}
      };
    }
  }, [empId, taxYear]);

  // 5. loadOtherIncomeComponent
  const loadOtherIncomeComponent = useCallback(async (): Promise<ComponentSummary | null> => {
    try {
      const response = await taxationApi.getComponent(empId!, taxYear, 'other_income');
      const data = response?.component_data || response;
      
      const totalOtherIncome = (data.dividend_income || 0) + 
                              (data.gifts_received || 0);
      
      return {
        id: 'other_income',
        name: 'Other Income',
        icon: <BusinessIcon />,
        color: 'secondary',
        hasData: totalOtherIncome > 0,
        totalValue: totalOtherIncome,
        details: data
      };
    } catch (error) {
      return {
        id: 'other_income',
        name: 'Other Income',
        icon: <BusinessIcon />,
        color: 'secondary',
        hasData: false,
        totalValue: 0,
        details: {}
      };
    }
  }, [empId, taxYear]);

  // 6. loadPerquisitesComponent
  const loadPerquisitesComponent = useCallback(async (): Promise<ComponentSummary | null> => {
    try {
      const response = await taxationApi.getComponent(empId!, taxYear, 'perquisites');
      const data = response?.component_data || response;
      
      // Calculate total perquisites value from various perquisite types
      const totalPerquisites = (data.accommodation_value || 0) + 
                              (data.car_value || 0) + 
                              (data.medical_reimbursement_value || 0) + 
                              (data.lta_value || 0) + 
                              (data.loan_value || 0) + 
                              (data.esop_value || 0) + 
                              (data.other_perquisites_value || 0);
      
      return {
        id: 'perquisites',
        name: 'Perquisites',
        icon: <CardGiftcardIcon />,
        color: 'error',
        hasData: totalPerquisites > 0,
        totalValue: totalPerquisites,
        details: data
      };
    } catch (error) {
      return {
        id: 'perquisites',
        name: 'Perquisites',
        icon: <CardGiftcardIcon />,
        color: 'error',
        hasData: false,
        totalValue: 0,
        details: {}
      };
    }
  }, [empId, taxYear]);

  // 7. loadComponentsData
  const loadComponentsData = useCallback(async (): Promise<void> => {
    try {
      setLoading(true);
      setError(null);
      
      const componentPromises = [
        loadSalaryComponent(),
        loadDeductionsComponent(),
        loadHousePropertyComponent(),
        loadCapitalGainsComponent(),
        loadOtherIncomeComponent(),
        loadPerquisitesComponent()
      ];
      
      const results = await Promise.allSettled(componentPromises);
      const loadedComponents: ComponentSummary[] = [];
      
      results.forEach((result) => {
        if (result.status === 'fulfilled' && result.value) {
          loadedComponents.push(result.value);
        }
      });
      
      setComponents(loadedComponents);
      
    } catch (error: any) {
      setError('Failed to load components data. Please try again.');
      console.error('Error loading components:', error);
    } finally {
      setLoading(false);
    }
  }, [empId, taxYear, loadSalaryComponent, loadDeductionsComponent, loadHousePropertyComponent, loadCapitalGainsComponent, loadOtherIncomeComponent, loadPerquisitesComponent]);

  // 8. calculateComputedTax
  const calculateComputedTax = useCallback(async (): Promise<void> => {
    try {
      setTaxLoading(true);
      setTaxError(null);
      
      // Get salary component details to check if there's data
      const salaryComponent = components.find(c => c.id === 'salary');
      
      if (!salaryComponent || !salaryComponent.hasData) {
        setComputedTax(0);
        setTaxLoading(false);
        return;
      }
      
      // Use the new monthly tax computation API based on SalaryPackageRecord
      // This will use the latest salary income data and compute monthly tax
      const monthlyTaxResult = await taxationApi.computeMonthlyTax(empId!);
      
      // Extract monthly tax from the response
      const monthlyTax = monthlyTaxResult.monthly_tax_liability || 0;
      setComputedTax(monthlyTax);
      
    } catch (error: any) {
      console.error('Error calculating monthly tax:', error);
      
      // Fallback to simplified calculation if new API fails
      try {
        console.log('Attempting fallback calculation...');
        
        // Simple fallback - use comprehensive tax calculation as before
        const salaryComponent = components.find(c => c.id === 'salary');
        const deductionsComponent = components.find(c => c.id === 'deductions');
        
        if (!salaryComponent || !salaryComponent.hasData) {
          setComputedTax(0);
          return;
        }
        
        // Simplified tax input for fallback
        const taxInput: any = {
          tax_year: taxYear,
          regime_type: 'new' as TaxRegime,
          age: 30,
          residential_status: 'resident' as const,
          salary_income: {
            basic_salary: salaryComponent.details.basic_salary || 0,
            hra: salaryComponent.details.hra_provided || 0,
            special_allowance: salaryComponent.details.special_allowance || 0,
            bonus: salaryComponent.details.bonus || 0,
            commission: salaryComponent.details.commission || 0,
            other_allowances: (salaryComponent.details.dearness_allowance || 0) + 
                             (salaryComponent.details.city_compensatory_allowance || 0),
            overtime: 0,
            arrears: 0,
            gratuity: 0,
            leave_encashment: 0,
            professional_tax: 0,
            tds_deducted: 0,
            employer_pf: 0,
            employee_pf: 0,
            employer_esic: 0,
            employee_esic: 0,
            lta: 0,
            medical_allowance: 0,
            conveyance_allowance: 0,
            food_allowance: 0,
            telephone_allowance: 0,
            uniform_allowance: salaryComponent.details.uniform_allowance || 0,
            educational_allowance: salaryComponent.details.children_education_allowance || 0
          }
        };
        
        // Include basic deductions if available
        if (deductionsComponent?.hasData) {
          taxInput.deductions = {
            section_80c: Object.values(deductionsComponent.details.section_80c || {}).reduce((sum: number, val: any) => sum + (Number(val) || 0), 0),
            section_80d_self: Object.values(deductionsComponent.details.section_80d || {}).reduce((sum: number, val: any) => sum + (Number(val) || 0), 0),
            section_80ccc: 0,
            section_80ccd_1: 0,
            section_80ccd_1b: 0,
            section_80ccd_2: 0,
            section_80d_parents: 0,
            section_80dd: 0,
            section_80ddb: 0,
            section_80e: deductionsComponent.details.education_loan_interest || 0,
            section_80ee: 0,
            section_80eea: 0,
            section_80eeb: 0,
            section_80g: 0,
            section_80gga: 0,
            section_80ggc: 0,
            section_80ia: 0,
            section_80ib: 0,
            section_80ic: 0,
            section_80id: 0,
            section_80ie: 0,
            section_80jjaa: 0,
            section_80tta: 0,
            section_80ttb: 0,
            section_80u: 0
          };
        }
        
        const taxResult = await taxationApi.calculateComprehensiveTax(taxInput);
        const annualTax = taxResult.tax_breakdown?.total_tax_liability || 0;
        const monthlyTax = annualTax / 12; // Convert annual to monthly
        setComputedTax(monthlyTax);
        
        // Clear error since fallback worked
        setTaxError(null);
        
      } catch (fallbackError: any) {
        console.error('Fallback calculation also failed:', fallbackError);
        setTaxError('Failed to calculate tax. Please try again.');
        setComputedTax(0);
      }
    } finally {
      setTaxLoading(false);
    }
  }, [components, empId]);

  useEffect(() => {
    if (empId) {
      loadComponentsData();
    }
  }, [empId, taxYear, loadComponentsData]);

  // Calculate tax whenever components change
  useEffect(() => {
    if (components.length > 0 && empId) {
      calculateComputedTax();
    }
  }, [components, empId, calculateComputedTax]);

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  const handleEditComponent = (componentId: string): void => {
    let path = `/taxation/component/${componentId}/${empId}?year=${taxYear}`;
    
    if (componentId === 'salary') {
      path = `/taxation/component/salary/${empId}?year=${taxYear}&mode=update`;
    }
    
    navigate(path);
  };

  const renderComponentCard = (component: ComponentSummary): React.ReactElement => (
    <Grid item xs={12} sm={6} md={4} key={component.id}>
      <Card 
        variant="outlined"
        sx={{ 
          height: '100%',
          borderColor: component.hasData ? `${component.color}.main` : 'grey.300'
        }}
      >
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ color: `${component.color}.main` }}>
                {component.icon}
              </Box>
              <Typography variant="h6">
                {component.name}
              </Typography>
            </Box>
            {isAdmin && (
              <Tooltip title="Edit Component">
                <IconButton 
                  size="small" 
                  onClick={() => handleEditComponent(component.id)}
                >
                  <EditIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
          </Box>
          
          <Box sx={{ textAlign: 'center', py: 2 }}>
            <Typography variant="h4" color={component.hasData ? `${component.color}.main` : 'text.secondary'}>
              {formatCurrency(component.totalValue)}
            </Typography>
            <Chip
              label={component.hasData ? 'Has Data' : 'No Data'}
              color={component.hasData ? 'success' : 'default'}
              size="small"
              variant="outlined"
              sx={{ mt: 1 }}
            />
          </Box>
        </CardContent>
      </Card>
    </Grid>
  );

  const formatValue = (key: string, value: any): React.ReactElement | string => {
    if (value === null || value === undefined) {
      return 'N/A';
    }
    
    if (typeof value === 'number') {
      // Check if this is a count/quantity field (not a monetary value)
      const countFields = [
        'count', 'quantity', 'number', 'total_records', 'records_count', 
        'children_count', 'hostel_count', 'months', 'days', 'years',
        'percentage', 'rate', 'age', 'experience', 'tenure'
      ];
      
      const isCountField = countFields.some(countField => 
        key.toLowerCase().includes(countField) || 
        key.toLowerCase().endsWith('_count') ||
        key.toLowerCase().endsWith('_number') ||
        key.toLowerCase().includes('count_') ||
        (key.toLowerCase().includes('total_') && !key.toLowerCase().includes('amount') && !key.toLowerCase().includes('salary') && !key.toLowerCase().includes('income'))
      );
      
      if (isCountField) {
        return value.toString();
      }
      
      return formatCurrency(value);
    }
    
    if (typeof value === 'boolean') {
      return value ? 'Yes' : 'No';
    }
    
    if (Array.isArray(value)) {
      if (value.length === 0) {
        return 'No records';
      }
      
      // Handle salary history or similar array data
      return (
        <Box>
          {value.map((item, index) => (
            <Box key={index} sx={{ mb: 1, p: 1, bgcolor: 'grey.50', borderRadius: 1 }}>
              {typeof item === 'object' ? (
                <Box>
                  {Object.entries(item).map(([k, v]) => (
                    <Typography key={k} variant="caption" display="block">
                      <strong>{k.replace(/_/g, ' ')}:</strong> {
                        formatValue(k, v)
                      }
                    </Typography>
                  ))}
                </Box>
              ) : (
                <Typography variant="body2">{String(item)}</Typography>
              )}
            </Box>
          ))}
        </Box>
      );
    }
    
    if (typeof value === 'object') {
      return (
        <Box>
          {Object.entries(value).map(([k, v]) => (
            <Typography key={k} variant="caption" display="block">
              <strong>{k.replace(/_/g, ' ')}:</strong> {
                formatValue(k, v)
              }
            </Typography>
          ))}
        </Box>
      );
    }
    
    return String(value);
  };

  const renderComponentDetails = (component: ComponentSummary): React.ReactElement => (
    <Accordion key={component.id}>
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
          <Box sx={{ color: `${component.color}.main` }}>
            {component.icon}
          </Box>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            {component.name}
          </Typography>
          <Typography variant="h6" color={`${component.color}.main`}>
            {formatCurrency(component.totalValue)}
          </Typography>
        </Box>
      </AccordionSummary>
      <AccordionDetails>
        <TableContainer>
          <Table size="small">
            <TableBody>
              {Object.entries(component.details).map(([key, value]) => (
                <TableRow key={key}>
                  <TableCell sx={{ fontWeight: 'medium', verticalAlign: 'top' }}>
                    {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </TableCell>
                  <TableCell align="right" sx={{ verticalAlign: 'top' }}>
                    {formatValue(key, value)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </AccordionDetails>
    </Accordion>
  );

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '70vh' }}>
        <CircularProgress size={40} />
      </Box>
    );
  }

  const totalValue = components.reduce((sum, comp) => sum + comp.totalValue, 0);
  const componentsWithData = components.filter(comp => comp.hasData).length;

  return (
    <Box>
      {/* Header */}
      <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              Components Overview
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Employee ID: {empId} | Tax Year: {taxYear}
            </Typography>
          </Box>
          <Button 
            variant="outlined" 
            startIcon={<ArrowBackIcon />}
            onClick={() => navigate('/taxation/component-management')}
          >
            Back to Management
          </Button>
        </Box>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h6" color="text.secondary">
                Total Value
              </Typography>
              <Typography variant="h4" color="primary">
                {formatCurrency(totalValue)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h6" color="text.secondary">
                Components with Data
              </Typography>
              <Typography variant="h4" color="success.main">
                {componentsWithData} / {components.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h6" color="text.secondary">
                Monthly Tax
              </Typography>
              {taxLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 60 }}>
                  <CircularProgress size={30} />
                </Box>
              ) : taxError ? (
                <Tooltip title={taxError}>
                  <Typography variant="h4" color="error">
                    Error
                  </Typography>
                </Tooltip>
              ) : (
                <Typography variant="h4" color="warning.main">
                  {formatCurrency(computedTax)}
                </Typography>
              )}
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                Monthly tax based on salary package
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Component Cards */}
      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        Component Summary
      </Typography>
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {components.map(renderComponentCard)}
      </Grid>

      {/* Detailed View */}
      <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
        Detailed Component Values
      </Typography>
      <Box>
        {components.map(renderComponentDetails)}
      </Box>
    </Box>
  );
};

export default ComponentsOverview; 