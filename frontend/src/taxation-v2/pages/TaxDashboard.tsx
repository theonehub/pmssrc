import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Typography,
  Tabs,
  Tab,
  useTheme,
  useMediaQuery,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  TrendingUp,
  Calculate,
  Receipt,
  FileDownload,
  Assessment,
  CompareArrows,
  Timeline
} from '@mui/icons-material';

import { Card, Button } from '../components/ui';
import { TaxBreakdownChart } from '../components/charts/TaxBreakdownChart';
import { TaxTrendsChart } from '../components/charts/TaxTrendsChart';
import { useTaxCalculation } from '../../shared/hooks/useTaxCalculation';
import { formatCurrency, formatPercentage } from '../../shared/utils/formatting';

// =============================================================================
// INTERFACES
// =============================================================================

interface DashboardOverview {
  currentYear: {
    grossIncome: number;
    totalTax: number;
    netIncome: number;
    effectiveRate: number;
    totalDeductions: number;
  };
  previousYear: {
    grossIncome: number;
    totalTax: number;
    netIncome: number;
  };
  projections: {
    estimatedTax: number;
    potentialSavings: number;
  };
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

// =============================================================================
// TAB PANEL COMPONENT
// =============================================================================

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
  return (
    <Box
      role="tabpanel"
      hidden={value !== index}
      id={`dashboard-tabpanel-${index}`}
      aria-labelledby={`dashboard-tab-${index}`}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </Box>
  );
};

// =============================================================================
// TAX DASHBOARD COMPONENT
// =============================================================================

export const TaxDashboard: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [activeTab, setActiveTab] = useState(0);
  const [dashboardData, setDashboardData] = useState<DashboardOverview | null>(null);

  // Hooks
  const { getQuickTaxEstimate } = useTaxCalculation();
  
  // Local state for missing properties
  const [incomeSources] = useState<any[]>([]);

  // Mock data for demonstration
  const mockTaxBreakdownData = {
    income_tax: 150000,
    surcharge: 15000,
    cess: 6000,
    total_deductions: 150000,
    net_income: 800000,
    gross_income: 1200000
  };

  const mockTrendsData = [
    { year: '2020', gross_income: 1000000, total_tax: 120000, net_income: 730000, effective_rate: 12, deductions: 150000 },
    { year: '2021', gross_income: 1100000, total_tax: 140000, net_income: 810000, effective_rate: 12.7, deductions: 150000 },
    { year: '2022', gross_income: 1150000, total_tax: 145000, net_income: 855000, effective_rate: 12.6, deductions: 150000 },
    { year: '2023', gross_income: 1200000, total_tax: 171000, net_income: 879000, effective_rate: 14.25, deductions: 150000 },
    { year: '2024', gross_income: 1300000, total_tax: 180000, net_income: 970000, effective_rate: 13.8, deductions: 150000 }
  ];

  // =============================================================================
  // EFFECTS
  // =============================================================================

  useEffect(() => {
    // Calculate dashboard overview data
    const totalIncome = incomeSources.reduce((sum, source) => sum + source.annual_amount, 0);
    
    if (totalIncome > 0) {
      const estimate = getQuickTaxEstimate(totalIncome, 'new');

      setDashboardData({
        currentYear: {
          grossIncome: totalIncome,
          totalTax: estimate,
          netIncome: totalIncome - estimate,
          effectiveRate: (estimate / totalIncome) * 100,
          totalDeductions: 150000 // Mock data
        },
        previousYear: {
          grossIncome: totalIncome * 0.9,
          totalTax: estimate * 0.85,
          netIncome: (totalIncome * 0.9) - (estimate * 0.85)
        },
        projections: {
          estimatedTax: estimate,
          potentialSavings: 50000 // Mock data
        }
      });
    }
  }, [incomeSources, getQuickTaxEstimate]);

  // =============================================================================
  // EVENT HANDLERS
  // =============================================================================

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleExportData = () => {
    // Export functionality
    console.log('Exporting tax data...');
  };

  const handleNewCalculation = () => {
    // Navigate to calculator
    console.log('Starting new calculation...');
  };

  const handleCompareRegimes = () => {
    // Compare tax regimes
    console.log('Comparing tax regimes...');
  };

  // =============================================================================
  // RENDER HELPERS
  // =============================================================================

  const renderOverviewCards = () => {
    if (!dashboardData) {
      return (
        <Grid container spacing={3}>
          {[1, 2, 3, 4].map((i) => (
            <Grid size={{ xs: 12, sm: 6, md: 3 }} key={i}>
              <Card loading />
            </Grid>
          ))}
        </Grid>
      );
    }

    const { currentYear, previousYear } = dashboardData;
    const incomeGrowth = ((currentYear.grossIncome - previousYear.grossIncome) / previousYear.grossIncome) * 100;
    const taxGrowth = ((currentYear.totalTax - previousYear.totalTax) / previousYear.totalTax) * 100;

    return (
      <Grid container spacing={3}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card variant="info">
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <TrendingUp sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
              <Typography variant="h4" fontWeight="bold">
                {formatCurrency(currentYear.grossIncome)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Gross Income
              </Typography>
              <Typography variant="caption" color={incomeGrowth >= 0 ? 'success.main' : 'error.main'}>
                {formatPercentage(incomeGrowth)} vs last year
              </Typography>
            </Box>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card variant="error">
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <Receipt sx={{ fontSize: 40, color: 'error.main', mb: 1 }} />
              <Typography variant="h4" fontWeight="bold">
                {formatCurrency(currentYear.totalTax)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Tax
              </Typography>
              <Typography variant="caption" color={taxGrowth <= incomeGrowth ? 'success.main' : 'warning.main'}>
                {formatPercentage(taxGrowth)} vs last year
              </Typography>
            </Box>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card variant="success">
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <TrendingUp sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
              <Typography variant="h4" fontWeight="bold">
                {formatCurrency(currentYear.netIncome)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Net Income
              </Typography>
              <Typography variant="caption" color="success.main">
                After tax income
              </Typography>
            </Box>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card variant="outlined">
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <Assessment sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
              <Typography variant="h4" fontWeight="bold">
                {formatPercentage(currentYear.effectiveRate)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Effective Tax Rate
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Current year rate
              </Typography>
            </Box>
          </Card>
        </Grid>
      </Grid>
    );
  };

  const renderQuickActions = () => (
    <Card title="Quick Actions" variant="outlined">
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Button
            variant="contained"
            fullWidth
            startIcon={<Calculate />}
            onClick={handleNewCalculation}
          >
            New Calculation
          </Button>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Button
            variant="outlined"
            fullWidth
            startIcon={<CompareArrows />}
            onClick={handleCompareRegimes}
          >
            Compare Regimes
          </Button>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Button
            variant="outlined"
            fullWidth
            startIcon={<FileDownload />}
            onClick={handleExportData}
          >
            Export Data
          </Button>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Button
            variant="outlined"
            fullWidth
            startIcon={<Assessment />}
          >
            View Reports
          </Button>
        </Grid>
      </Grid>
    </Card>
  );

  const renderRecentActivity = () => (
    <Card title="Recent Activity" variant="outlined">
      <Box sx={{ p: 2 }}>
        {incomeSources.length === 0 ? (
          <Typography variant="body2" color="text.secondary" textAlign="center">
            No recent calculations. Start by adding income sources.
          </Typography>
        ) : (
          incomeSources.slice(0, 3).map((source, index) => (
            <Box 
              key={index}
              sx={{ 
                display: 'flex', 
                justifyContent: 'space-between',
                alignItems: 'center',
                py: 1,
                borderBottom: index < 2 ? '1px solid #f0f0f0' : 'none'
              }}
            >
              <Box>
                <Typography variant="body2" fontWeight="bold">
                  {source.description}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {source.income_type.replace('_', ' ').toUpperCase()}
                </Typography>
              </Box>
              <Typography variant="body2" color="primary">
                {formatCurrency(source.annual_amount)}
              </Typography>
            </Box>
          ))
        )}
      </Box>
    </Card>
  );

  const renderSpeedDial = () => {
    if (!isMobile) return null;

    const actions = [
      { icon: <Calculate />, name: 'Calculate Tax', onClick: handleNewCalculation },
      { icon: <CompareArrows />, name: 'Compare Regimes', onClick: handleCompareRegimes },
      { icon: <FileDownload />, name: 'Export Data', onClick: handleExportData },
    ];

    return (
      <SpeedDial
        ariaLabel="Dashboard Actions"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        icon={<SpeedDialIcon />}
      >
        {actions.map((action) => (
          <SpeedDialAction
            key={action.name}
            icon={action.icon}
            tooltipTitle={action.name}
            onClick={action.onClick}
          />
        ))}
      </SpeedDial>
    );
  };

  // =============================================================================
  // MAIN RENDER
  // =============================================================================

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          <DashboardIcon sx={{ mr: 2, verticalAlign: 'middle' }} />
          Tax Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Overview of your tax calculations and financial insights
        </Typography>
      </Box>

      {/* Overview Cards */}
      {renderOverviewCards()}

      {/* Quick Actions */}
      <Box sx={{ mt: 4 }}>
        {renderQuickActions()}
      </Box>

      {/* Tabs */}
      <Box sx={{ mt: 4 }}>
        <Tabs 
          value={activeTab} 
          onChange={handleTabChange}
          variant={isMobile ? 'scrollable' : 'standard'}
          scrollButtons="auto"
        >
          <Tab label="Breakdown Analysis" icon={<Assessment />} />
          <Tab label="Historical Trends" icon={<Timeline />} />
          <Tab label="Recent Activity" icon={<Receipt />} />
        </Tabs>

        <TabPanel value={activeTab} index={0}>
          <TaxBreakdownChart data={mockTaxBreakdownData} />
        </TabPanel>

        <TabPanel value={activeTab} index={1}>
          <TaxTrendsChart data={mockTrendsData} />
        </TabPanel>

        <TabPanel value={activeTab} index={2}>
          <Grid container spacing={3}>
            <Grid size={{ xs: 12, md: 8 }}>
              {renderRecentActivity()}
            </Grid>
            <Grid size={{ xs: 12, md: 4 }}>
              <Card title="Tax Optimization Tips" variant="info">
                <Box sx={{ p: 2 }}>
                  <Typography variant="body2" paragraph>
                    💡 Consider maximizing your Section 80C deductions to save up to ₹46,800 in taxes.
                  </Typography>
                  <Typography variant="body2" paragraph>
                    🏥 Health insurance premiums under Section 80D can provide additional savings.
                  </Typography>
                  <Typography variant="body2">
                    📊 Compare old vs new tax regime to optimize your tax liability.
                  </Typography>
                </Box>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>
      </Box>

      {/* Mobile Speed Dial */}
      {renderSpeedDial()}
    </Container>
  );
};

export default TaxDashboard; 