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
  Tooltip,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Snackbar
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
  CardGiftcard as CardGiftcardIcon,
  MoreVert as MoreVertIcon,
  FileDownload as FileDownloadIcon
} from '@mui/icons-material';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { getUserRole } from '../../shared/utils/auth';
import taxationApi from '../../shared/api/taxationApi';
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
  error?: string; // Added error property
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
  
  // Action menu state
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedComponent, setSelectedComponent] = useState<string | null>(null);
  const [exportLoading, setExportLoading] = useState<boolean>(false);
  const [exportMessage, setExportMessage] = useState<{ 
    show: boolean; 
    message: string; 
    severity: 'success' | 'error' | 'info' | 'warning';
  }>({ show: false, message: '', severity: 'success' });
  
  const taxYear = searchParams.get('year') || CURRENT_TAX_YEAR;
  const isAdmin = userRole === 'admin' || userRole === 'superadmin';

  // Helper to compute assessment year from tax year
  const getAssessmentYear = (taxYear: string): string => {
    const [start, end] = taxYear.split('-');
    if (!start || !end) return '';
    const startYear = parseInt(start, 10);
    // If end is 2 digits, add to century
    const fullEndYear = end.length === 2 ? (startYear + 1).toString().slice(0, 2) + end : end;
    return `${startYear + 1}-${(parseInt(fullEndYear, 10) + 1).toString().slice(-2)}`;
  };

  // 1. loadSalaryComponent
  const loadSalaryComponent = useCallback(async (): Promise<ComponentSummary> => {
    try {
      const response = await taxationApi.getComponent(empId!, taxYear, 'salary');
      const data = response?.component_data || response;
      
      const totalSalary = (data.basic_salary || 0) + 
                          (data.dearness_allowance || 0) + 
                          (data.hra_provided || 0) + 
                          (data.special_allowance || 0) + 
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
    } catch (error: any) {
      const backendMessage = error?.response?.data?.detail;
      return {
        id: 'salary',
        name: 'Salary Income',
        icon: <AccountBalanceIcon />,
        color: 'primary',
        hasData: false,
        totalValue: 0,
        details: {},
        error: backendMessage || 'Failed to fetch salary data.'
      };
    }
  }, [empId, taxYear]);

  // 2. loadDeductionsComponent
  const loadDeductionsComponent = useCallback(async (): Promise<ComponentSummary> => {
    try {
      const response = await taxationApi.getComponent(empId!, taxYear, 'deductions');
      const data = response?.component_data || response;
      
      const section80c = data.section_80c || {};
      const section80d = data.section_80d || {};
      
      // Fields to ignore when calculating total deductions
      const ignoredFields = [
        'limit',
        'remaining_limit',
        'total_invested',
        'limit_80ccd_1b',
        'parent_age',
        'self_family_limit',
        'parent_limit',
        'preventive_limit',
        'exemption_limit'
      ];
      
      // Filter out ignored fields and calculate total for section 80C
      const section80cTotal = Object.entries(section80c)
        .filter(([key]) => !ignoredFields.includes(key))
        .reduce((sum: number, [, val]) => sum + (Number(val) || 0), 0);
      
      // Filter out ignored fields and calculate total for section 80D
      const section80dTotal = Object.entries(section80d)
        .filter(([key]) => !ignoredFields.includes(key))
        .reduce((sum: number, [, val]) => sum + (Number(val) || 0), 0);
      
      const totalDeductions = section80cTotal + section80dTotal;
      
      return {
        id: 'deductions',
        name: 'Deductions',
        icon: <ReceiptIcon />,
        color: 'info',
        hasData: totalDeductions > 0,
        totalValue: totalDeductions,
        details: data
      };
    } catch (error: any) {
      const backendMessage = error?.response?.data?.detail;
      return {
        id: 'deductions',
        name: 'Deductions',
        icon: <ReceiptIcon />,
        color: 'info',
        hasData: false,
        totalValue: 0,
        details: {},
        error: backendMessage || 'Failed to fetch deductions data.'
      };
    }
  }, [empId, taxYear]);

  // 3. loadHousePropertyComponent
  const loadHousePropertyComponent = useCallback(async (): Promise<ComponentSummary> => {
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
    } catch (error: any) {
      const backendMessage = error?.response?.data?.detail;
      return {
        id: 'house_property_income',
        name: 'House Property',
        icon: <HomeIcon />,
        color: 'warning',
        hasData: false,
        totalValue: 0,
        details: {},
        error: backendMessage || 'Failed to fetch house property data.'
      };
    }
  }, [empId, taxYear]);

  // 4. loadCapitalGainsComponent
  const loadCapitalGainsComponent = useCallback(async (): Promise<ComponentSummary> => {
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
    } catch (error: any) {
      const backendMessage = error?.response?.data?.detail;
      return {
        id: 'capital_gains',
        name: 'Capital Gains',
        icon: <TrendingUpIcon />,
        color: 'success',
        hasData: false,
        totalValue: 0,
        details: {},
        error: backendMessage || 'Failed to fetch capital gains data.'
      };
    }
  }, [empId, taxYear]);

  // 5. loadOtherIncomeComponent
  const loadOtherIncomeComponent = useCallback(async (): Promise<ComponentSummary> => {
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
    } catch (error: any) {
      const backendMessage = error?.response?.data?.detail;
      return {
        id: 'other_income',
        name: 'Other Income',
        icon: <BusinessIcon />,
        color: 'secondary',
        hasData: false,
        totalValue: 0,
        details: {},
        error: backendMessage || 'Failed to fetch other income data.'
      };
    }
  }, [empId, taxYear]);

  // 6. loadPerquisitesComponent
  const loadPerquisitesComponent = useCallback(async (): Promise<ComponentSummary> => {
    try {
      const response = await taxationApi.getComponent(empId!, taxYear, 'perquisites');
      const data = response?.component_data || response;
      
      // Calculate accommodation perquisite
      let accommodationValue = 0;
      if (data.accommodation) {
        const acc = data.accommodation;
        if (acc.accommodation_type === 'Government') {
          accommodationValue = Math.max(0, (acc.employee_rent_payment || 0) - (acc.license_fees || 0));
        } else if (acc.accommodation_type === 'Employer-Owned') {
          let rate = 0.05; // 5% for below 15 lakhs
          if (acc.city_population === 'Above 40 lakhs') {
            rate = 0.10; // 10%
          } else if (acc.city_population === 'Between 15-40 lakhs') {
            rate = 0.075; // 7.5%
          }
          accommodationValue = (acc.license_fees || 0) * rate;
        } else if (acc.accommodation_type === 'Employer-Leased') {
          accommodationValue = Math.max(0, (acc.rent_paid_by_employer || 0) - (acc.employee_rent_payment || 0));
        } else if (acc.accommodation_type === 'Hotel') {
          accommodationValue = (acc.hotel_charges || 0) * (acc.stay_days || 0);
        }
        
        // Add furniture perquisite if owned by employer
        if (acc.is_furniture_owned_by_employer) {
          accommodationValue += Math.max(0, (acc.furniture_cost || 0) - (acc.furniture_employee_payment || 0));
        }
      }
      
      // Calculate car perquisite
      let carValue = 0;
      if (data.car) {
        const car = data.car;
        if (car.car_use_type === 'Personal') {
          // Personal use: 10% of car cost + driver cost
          carValue = ((car.car_cost_to_employer || 0) * 0.10) + (car.driver_cost || 0);
        } else if (car.car_use_type === 'Official') {
          // Official use: No perquisite
          carValue = 0;
        } else if (car.car_use_type === 'Mixed') {
          // Mixed use: 5% of car cost + driver cost
          carValue = ((car.car_cost_to_employer || 0) * 0.05) + (car.driver_cost || 0);
        }
        
        // Add other vehicle cost
        carValue += (car.other_vehicle_cost || 0);
      }
      
      // Calculate LTA perquisite
      const ltaValue = data.lta?.lta_amount_claimed || 0;
      
      // Calculate interest-free loan perquisite
      let loanValue = 0;
      if (data.interest_free_loan) {
        const loan = data.interest_free_loan;
        const outstandingAmount = loan.outstanding_amount || loan.loan_amount || 0;
        const sbiRate = loan.sbi_interest_rate || 6.5;
        const companyRate = loan.company_interest_rate || 0;
        loanValue = Math.max(0, (outstandingAmount * (sbiRate - companyRate) / 100));
      }
      
      // Calculate ESOP perquisite
      let esopValue = 0;
      if (data.esop) {
        const esop = data.esop;
        const sharesExercised = esop.shares_exercised || 0;
        const exercisePrice = esop.exercise_price || 0;
        const allotmentPrice = esop.allotment_price || 0;
        esopValue = sharesExercised * Math.max(0, allotmentPrice - exercisePrice);
      }
      
      // Calculate free education perquisite
      let educationValue = 0;
      if (data.free_education) {
        const edu = data.free_education;
        if (edu.employer_maintained_1st_child) {
          educationValue += (edu.monthly_expenses_child1 || 0) * (edu.months_child1 || 12);
        }
        if (edu.employer_maintained_2nd_child) {
          educationValue += (edu.monthly_expenses_child2 || 0) * (edu.months_child2 || 12);
        }
      }
      
      // Calculate utilities perquisite
      let utilitiesValue = 0;
      if (data.utilities) {
        const util = data.utilities;
        utilitiesValue = Math.max(0, 
          ((util.gas_paid_by_employer || 0) + (util.electricity_paid_by_employer || 0) + (util.water_paid_by_employer || 0)) -
          ((util.gas_paid_by_employee || 0) + (util.electricity_paid_by_employee || 0) + (util.water_paid_by_employee || 0))
        );
      }
      
      // Calculate lunch refreshment perquisite
      let lunchValue = 0;
      if (data.lunch_refreshment) {
        const lunch = data.lunch_refreshment;
        lunchValue = Math.max(0, (lunch.employer_cost || 0) - (lunch.employee_payment || 0));
      }
      
      // Calculate domestic help perquisite
      let domesticHelpValue = 0;
      if (data.domestic_help) {
        const domestic = data.domestic_help;
        domesticHelpValue = Math.max(0, (domestic.domestic_help_paid_by_employer || 0) - (domestic.domestic_help_paid_by_employee || 0));
      }
      
      const totalPerquisites = accommodationValue + carValue + ltaValue + loanValue + esopValue + 
                               educationValue + utilitiesValue + lunchValue + domesticHelpValue;
      
      // Debug logging
      console.log('ComponentsOverview - Perquisites calculation:', {
        accommodationValue,
        carValue,
        ltaValue,
        loanValue,
        esopValue,
        educationValue,
        utilitiesValue,
        lunchValue,
        domesticHelpValue,
        totalPerquisites
      });
      
      return {
        id: 'perquisites',
        name: 'Perquisites',
        icon: <CardGiftcardIcon />,
        color: 'error',
        hasData: totalPerquisites > 0,
        totalValue: totalPerquisites,
        details: data
      };
    } catch (error: any) {
      const backendMessage = error?.response?.data?.detail;
      return {
        id: 'perquisites',
        name: 'Perquisites',
        icon: <CardGiftcardIcon />,
        color: 'error',
        hasData: false,
        totalValue: 0,
        details: {},
        error: backendMessage || 'Failed to fetch perquisites data.'
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
      const backendMessage = error?.response?.data?.detail;
      setError(backendMessage || 'Failed to load components data. Please try again.');
      console.error('Error loading components:', error);
    } finally {
      setLoading(false);
    }
  }, [loadSalaryComponent, loadDeductionsComponent, loadHousePropertyComponent, loadCapitalGainsComponent, loadOtherIncomeComponent, loadPerquisitesComponent]);

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
            commission: salaryComponent.details.commission || 0,
            other_allowances: (salaryComponent.details.dearness_allowance || 0) + 
                             (salaryComponent.details.city_compensatory_allowance || 0),
            overtime: 0,
            gratuity: 0,
            leave_encashment: 0,
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
  }, [components, empId, taxYear]);

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
    setAnchorEl(null);
    setSelectedComponent(null);
    
    let path = `/taxation/component/${componentId}/${empId}?year=${taxYear}`;
    
    if (componentId === 'salary') {
      path = `/taxation/component/salary/${empId}?year=${taxYear}&mode=update`;
    }
    
    navigate(path);
  };

  const handleExportSalaryPackage = async () => {
    if (!empId) return;
    
    setExportLoading(true);
    try {
      const blob = await taxationApi.exportSalaryPackageToExcel(empId, taxYear);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `salary_package_${empId}_${taxYear || 'current'}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      setExportMessage({
        show: true,
        message: 'Salary package exported successfully!',
        severity: 'success'
      });
    } catch (error: any) {
      const backendMessage = error?.response?.data?.detail;
      console.error('Error exporting salary package:', error);
      setExportMessage({
        show: true,
        message: backendMessage || 'Failed to export salary package',
        severity: 'error'
      });
    } finally {
      setExportLoading(false);
      setAnchorEl(null);
    }
  };

  const handleExportSalaryPackageSingle = async () => {
    if (!empId) return;
    
    setExportLoading(true);
    try {
      const blob = await taxationApi.exportSalaryPackageSingleSheet(empId, taxYear);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `salary_package_single_${empId}_${taxYear || 'current'}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      setExportMessage({
        show: true,
        message: 'Salary package (single sheet) exported successfully!',
        severity: 'success'
      });
    } catch (error: any) {
      const backendMessage = error?.response?.data?.detail;
      console.error('Error exporting salary package (single sheet):', error);
      setExportMessage({
        show: true,
        message: backendMessage || 'Failed to export salary package (single sheet)',
        severity: 'error'
      });
    } finally {
      setExportLoading(false);
      setAnchorEl(null);
    }
  };

  const handleCloseSnackbar = (): void => {
    setExportMessage({ ...exportMessage, show: false });
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
              <Tooltip title="Actions">
                <IconButton 
                  size="small" 
                  onClick={(event) => {
                    event.stopPropagation();
                    setAnchorEl(event.currentTarget);
                    setSelectedComponent(component.id);
                  }}
                >
                  <MoreVertIcon fontSize="small" />
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
              Employee ID: {empId} | Tax Year: {taxYear} | Assessment Year: {getAssessmentYear(taxYear)}
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

      {/* Action Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={() => setAnchorEl(null)}
      >
        <MenuItem onClick={() => handleEditComponent(selectedComponent!)}>
          <ListItemIcon>
            <EditIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Edit</ListItemText>
        </MenuItem>
        <MenuItem 
          onClick={handleExportSalaryPackage}
          disabled={exportLoading}
        >
          <ListItemIcon>
            <FileDownloadIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>
            {exportLoading ? 'Exporting...' : 'Download Excel'}
          </ListItemText>
        </MenuItem>
        <MenuItem 
          onClick={handleExportSalaryPackageSingle}
          disabled={exportLoading}
        >
          <ListItemIcon>
            <FileDownloadIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>
            {exportLoading ? 'Exporting...' : 'Download Single Sheet Excel'}
          </ListItemText>
        </MenuItem>
      </Menu>

      {/* Success/Error Messages */}
      <Snackbar
        open={exportMessage.show}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={exportMessage.severity}
          sx={{ width: '100%' }}
        >
          {exportMessage.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default ComponentsOverview; 