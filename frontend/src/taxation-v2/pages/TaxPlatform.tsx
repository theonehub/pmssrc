import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Tabs,
  Tab,
  Grid,
  Card as MuiCard,
  CardContent,
  Avatar,
  Chip,
  IconButton,
  useTheme,
  useMediaQuery,
  Alert,
  LinearProgress
} from '@mui/material';
import {
  Psychology,
  Analytics,
  AccountBalance,
  Sync,
  Security,
  TrendingUp,
  Lightbulb,
  CloudSync
} from '@mui/icons-material';

import { Card, Button } from '../components/ui';
import { TaxOptimizationEngine, ScenarioAnalyzer } from '../components/analytics';
import { apiIntegrationService } from '../services/apiIntegration';
import { formatCurrency } from '../../shared/utils/formatting';

// =============================================================================
// INTERFACES
// =============================================================================

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

interface PlatformStats {
  totalSavings: number;
  optimizationScore: number;
  accountsConnected: number;
  lastSyncTime: string;
}

interface TaxAlert {
  id: string;
  type: 'opportunity' | 'deadline' | 'update' | 'warning';
  title: string;
  description: string;
  action?: string;
  date: string;
}

// =============================================================================
// TAB PANEL COMPONENT
// =============================================================================

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index, ...other }) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`platform-tabpanel-${index}`}
      aria-labelledby={`platform-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ py: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
};

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export const TaxPlatform: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const [activeTab, setActiveTab] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [platformStats, setPlatformStats] = useState<PlatformStats>({
    totalSavings: 125000,
    optimizationScore: 87,
    accountsConnected: 3,
    lastSyncTime: new Date().toISOString()
  });
  
  const [taxAlerts] = useState<TaxAlert[]>([
    {
      id: '1',
      type: 'opportunity',
      title: 'Maximize Section 80C',
      description: 'You can save ₹45,000 more by investing in tax-saving instruments',
      action: 'Optimize Now',
      date: new Date().toISOString()
    },
    {
      id: '2',
      type: 'deadline',
      title: 'Tax Filing Deadline',
      description: 'ITR filing deadline is in 15 days',
      action: 'File Now',
      date: new Date(Date.now() + 15 * 24 * 60 * 60 * 1000).toISOString()
    },
    {
      id: '3',
      type: 'update',
      title: 'New Tax Rules',
      description: 'Standard deduction increased to ₹75,000 for FY 2024-25',
      date: new Date().toISOString()
    }
  ]);

  const [connectedAccounts, setConnectedAccounts] = useState<any[]>([]);

  // =============================================================================
  // EFFECTS
  // =============================================================================

  useEffect(() => {
    loadConnectedAccounts();
  }, []);

  // =============================================================================
  // FUNCTIONS
  // =============================================================================

  const loadConnectedAccounts = async () => {
    try {
      // Load mock data for demo
      const bankData = apiIntegrationService.generateMockBankData();
      const investmentData = apiIntegrationService.generateMockInvestmentData();
      
      setConnectedAccounts([
        ...bankData.accounts.map(acc => ({ ...acc, type: 'bank' })),
        ...investmentData.accounts.map(acc => ({ ...acc, type: 'investment' }))
      ]);
    } catch (error) {
      console.error('Failed to load connected accounts:', error);
    }
  };

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleSyncData = async () => {
    setIsLoading(true);
    try {
      // Simulate data sync
      await new Promise(resolve => setTimeout(resolve, 2000));
      setPlatformStats(prev => ({
        ...prev,
        lastSyncTime: new Date().toISOString()
      }));
    } catch (error) {
      console.error('Sync failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleOptimizationApply = (recommendation: any) => {
    console.log('Applying optimization:', recommendation);
    // Update platform stats
    setPlatformStats(prev => ({
      ...prev,
      totalSavings: prev.totalSavings + recommendation.taxSaving,
      optimizationScore: Math.min(100, prev.optimizationScore + 5)
    }));
  };

  // =============================================================================
  // RENDER COMPONENTS
  // =============================================================================

  const renderPlatformOverview = () => (
    <Box>
      {/* Platform Stats */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card variant="gradient">
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <Typography variant="h4" fontWeight="bold" color="white">
                {formatCurrency(platformStats.totalSavings)}
              </Typography>
              <Typography variant="body2" color="rgba(255,255,255,0.8)">
                Total Tax Savings
              </Typography>
            </Box>
          </Card>
        </Grid>
        
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card variant="outlined">
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <Typography variant="h4" fontWeight="bold" color="success.main">
                {platformStats.optimizationScore}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Optimization Score
              </Typography>
            </Box>
          </Card>
        </Grid>
        
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card variant="outlined">
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <Typography variant="h4" fontWeight="bold" color="primary.main">
                {platformStats.accountsConnected}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Connected Accounts
              </Typography>
            </Box>
          </Card>
        </Grid>
        
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card variant="outlined">
            <Box sx={{ p: 3, textAlign: 'center', position: 'relative' }}>
              <IconButton 
                size="small" 
                onClick={handleSyncData}
                disabled={isLoading}
                sx={{ position: 'absolute', top: 8, right: 8 }}
              >
                <Sync sx={{ fontSize: 20 }} />
              </IconButton>
              
              <Typography variant="h6" fontWeight="bold" color="info.main">
                {isLoading ? 'Syncing...' : 'Up to Date'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Last sync: {new Date(platformStats.lastSyncTime).toLocaleTimeString()}
              </Typography>
              
              {isLoading && <LinearProgress sx={{ mt: 1 }} />}
            </Box>
          </Card>
        </Grid>
      </Grid>

      {/* Tax Alerts */}
      <Card title="🔔 Tax Alerts & Opportunities" variant="outlined" sx={{ mb: 4 }}>
        {taxAlerts.map((alert) => (
          <Alert 
            key={alert.id}
            severity={
              alert.type === 'opportunity' ? 'success' : 
              alert.type === 'deadline' ? 'warning' : 
              alert.type === 'update' ? 'info' : 'error'
            }
            action={
              alert.action && (
                <Button size="small" variant="contained">
                  {alert.action}
                </Button>
              )
            }
            sx={{ mb: 1 }}
          >
            <Typography variant="subtitle2" fontWeight="bold">
              {alert.title}
            </Typography>
            <Typography variant="body2">
              {alert.description}
            </Typography>
          </Alert>
        ))}
      </Card>

      {/* Connected Accounts */}
      <Card title="🔗 Connected Accounts" variant="outlined">
        <Grid container spacing={2}>
          {connectedAccounts.map((account, index) => (
            <Grid size={{ xs: 12, sm: 6, md: 4 }} key={index}>
              <MuiCard variant="outlined">
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <Avatar sx={{ bgcolor: account.type === 'bank' ? 'primary.main' : 'secondary.main' }}>
                      <AccountBalance />
                    </Avatar>
                    <Box>
                      <Typography variant="subtitle2" fontWeight="bold">
                        {account.bankName || account.provider}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {account.accountNumber || account.accountType}
                      </Typography>
                    </Box>
                  </Box>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2">
                      {account.type === 'bank' ? 'Balance' : 'Value'}
                    </Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {formatCurrency(account.balance || account.currentValue)}
                    </Typography>
                  </Box>
                  
                  {account.type === 'investment' && (
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
                      <Typography variant="body2">Gains</Typography>
                      <Chip 
                        label={`+${account.gainsPercentage}%`}
                        color="success" 
                        size="small" 
                      />
                    </Box>
                  )}
                </CardContent>
              </MuiCard>
            </Grid>
          ))}
          
          <Grid size={{ xs: 12, sm: 6, md: 4 }}>
            <MuiCard 
              variant="outlined" 
              sx={{ 
                border: '2px dashed',
                borderColor: 'grey.300',
                cursor: 'pointer',
                '&:hover': { borderColor: 'primary.main' }
              }}
            >
              <CardContent sx={{ textAlign: 'center', py: 4 }}>
                <Avatar sx={{ bgcolor: 'grey.100', mx: 'auto', mb: 2 }}>
                  <Sync />
                </Avatar>
                <Typography variant="subtitle2" color="text.secondary">
                  Connect New Account
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Bank, Investment, or Crypto
                </Typography>
              </CardContent>
            </MuiCard>
          </Grid>
        </Grid>
      </Card>
    </Box>
  );

  const renderIntegrationsTab = () => (
    <Box>
      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Card title="🏦 Banking Integration" variant="outlined" sx={{ height: '100%' }}>
            <Box sx={{ p: 2 }}>
              <Typography variant="body2" paragraph>
                Connect your bank accounts to automatically import income and expense data.
                Supports major Indian banks with secure Open Banking APIs.
              </Typography>
              
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>Supported Banks:</Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {['HDFC Bank', 'ICICI Bank', 'SBI', 'Axis Bank', 'Kotak Mahindra'].map(bank => (
                    <Chip key={bank} label={bank} size="small" />
                  ))}
                </Box>
              </Box>
              
              <Button 
                variant="contained" 
                startIcon={<AccountBalance />}
                fullWidth
              >
                Connect Bank Account
              </Button>
            </Box>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 6 }}>
          <Card title="📈 Investment Integration" variant="outlined" sx={{ height: '100%' }}>
            <Box sx={{ p: 2 }}>
              <Typography variant="body2" paragraph>
                Link your investment accounts to track capital gains, dividends, and optimize
                your tax-saving investments automatically.
              </Typography>
              
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>Supported Platforms:</Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {['Zerodha', 'Groww', 'Angel One', 'Upstox', 'Paytm Money'].map(platform => (
                    <Chip key={platform} label={platform} size="small" />
                  ))}
                </Box>
              </Box>
              
              <Button 
                variant="contained" 
                startIcon={<TrendingUp />}
                fullWidth
              >
                Connect Investment Account
              </Button>
            </Box>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 6 }}>
          <Card title="🏛️ Government APIs" variant="outlined" sx={{ height: '100%' }}>
            <Box sx={{ p: 2 }}>
              <Typography variant="body2" paragraph>
                Real-time updates on tax rules, slabs, and regulations directly from
                government sources. PAN validation and compliance checks.
              </Typography>
              
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>Features:</Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {['Tax Rule Updates', 'PAN Validation', 'ITR Status', 'TDS Certificates'].map(feature => (
                    <Chip key={feature} label={feature} size="small" color="info" />
                  ))}
                </Box>
              </Box>
              
              <Button 
                variant="contained" 
                startIcon={<Security />}
                fullWidth
              >
                Enable Government APIs
              </Button>
            </Box>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 6 }}>
          <Card title="📊 Export & Accounting" variant="outlined" sx={{ height: '100%' }}>
            <Box sx={{ p: 2 }}>
              <Typography variant="body2" paragraph>
                Export your tax data to popular accounting software or generate
                professional reports for filing and record-keeping.
              </Typography>
              
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>Export Options:</Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {['Tally', 'Zoho Books', 'QuickBooks', 'Excel', 'PDF Reports'].map(option => (
                    <Chip key={option} label={option} size="small" color="secondary" />
                  ))}
                </Box>
              </Box>
              
              <Button 
                variant="contained" 
                startIcon={<CloudSync />}
                fullWidth
              >
                Export Tax Data
              </Button>
            </Box>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );

  // =============================================================================
  // MAIN RENDER
  // =============================================================================

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" gutterBottom fontWeight="bold">
          <Psychology sx={{ mr: 2, verticalAlign: 'middle' }} />
          AI Tax Platform
        </Typography>
        <Typography variant="h6" color="text.secondary">
          Advanced analytics, optimization, and integrations for smart tax management
        </Typography>
      </Box>

      {/* Navigation Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs 
          value={activeTab} 
          onChange={handleTabChange}
          variant={isMobile ? "scrollable" : "fullWidth"}
          scrollButtons="auto"
        >
          <Tab 
            icon={<Analytics />} 
            label="Platform Overview" 
            id="platform-tab-0"
            aria-controls="platform-tabpanel-0"
          />
          <Tab 
            icon={<Lightbulb />} 
            label="AI Optimization" 
            id="platform-tab-1"
            aria-controls="platform-tabpanel-1"
          />
          <Tab 
            icon={<Analytics />} 
            label="Scenario Analysis" 
            id="platform-tab-2"
            aria-controls="platform-tabpanel-2"
          />
          <Tab 
            icon={<CloudSync />} 
            label="Integrations" 
            id="platform-tab-3"
            aria-controls="platform-tabpanel-3"
          />
        </Tabs>
      </Box>

      {/* Tab Panels */}
      <TabPanel value={activeTab} index={0}>
        {renderPlatformOverview()}
      </TabPanel>

      <TabPanel value={activeTab} index={1}>
        <TaxOptimizationEngine 
          onApplyRecommendation={handleOptimizationApply}
          onInvestmentSelect={(investment) => console.log('Selected investment:', investment)}
        />
      </TabPanel>

      <TabPanel value={activeTab} index={2}>
        <ScenarioAnalyzer />
      </TabPanel>

      <TabPanel value={activeTab} index={3}>
        {renderIntegrationsTab()}
      </TabPanel>
    </Box>
  );
};

export default TaxPlatform; 